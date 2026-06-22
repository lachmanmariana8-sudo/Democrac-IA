"""Base de prueba trazable (append-only) — persistencia de capturas del Hunter.

Cada captura del Hunter se guarda apenas se registra, de modo que la evidencia
NUNCA se pierda aunque el proceso reinicie (root-cause: antes las capturas solo
vivían en `observation_store` en memoria, y un redeploy de Railway las perdía).

La base DEDUPLICADA y los conteos del informe se derivan de esta tabla con
scripts/build_evidence_base.py (un hecho = un hallazgo, con todas sus fuentes).

Idempotente: UNIQUE(entry_id) + INSERT OR IGNORE → re-ingerir la misma sesión
no duplica filas.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict

# Umbral de vuelta — espejo de PEIRSEliteReport._ROUND_THRESHOLD. Se importa
# perezosamente para evitar un ciclo de imports con el módulo del informe.
_ROUND_THRESHOLD = "2026-05-03"


def round_label(recorded_at: str | None) -> str:
    """1ª vuelta = hasta el cierre del cómputo de 1ª vuelta (recorded_at < umbral)."""
    d = (recorded_at or "")[:10]
    return "1ª vuelta" if d and d < _ROUND_THRESHOLD else "2ª vuelta"


def persist_capture(conn: sqlite3.Connection, country_code: str,
                    session_id: str | None, entry: Dict[str, Any]) -> bool:
    """Inserta una captura cruda en evidence_entries (append-only, idempotente).

    Devuelve True si insertó una fila nueva, False si ya existía (o sin entry_id).
    No lanza: la persistencia de evidencia nunca debe romper el loop del Hunter.
    """
    eid = entry.get("entry_id")
    if not eid:
        return False
    try:
        cur = conn.execute(
            """INSERT OR IGNORE INTO evidence_entries
               (entry_id, country_code, session_id, round, category, severity,
                finding, location, recorded_at, source_url, source_name,
                source_title, phase, ingested_at, raw_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                eid,
                country_code.upper(),
                session_id,
                round_label(entry.get("recorded_at")),
                entry.get("category") or "other",
                entry.get("severity") or "info",
                entry.get("finding") or "",
                entry.get("location") or None,
                entry.get("recorded_at"),
                entry.get("evidence_ref") or entry.get("url"),
                entry.get("hunter_source") or entry.get("source"),
                entry.get("hunter_title") or entry.get("title"),
                entry.get("phase"),
                datetime.now(timezone.utc).isoformat(),
                json.dumps(entry, ensure_ascii=False, sort_keys=True),
            ),
        )
        return cur.rowcount > 0
    except Exception:
        # Best-effort: nunca propagar errores de persistencia al Hunter.
        return False


def persist_captures(conn: sqlite3.Connection, country_code: str,
                     session_id: str | None, entries: list[Dict[str, Any]]) -> int:
    """Persiste un lote; devuelve cuántas filas nuevas se insertaron."""
    return sum(persist_capture(conn, country_code, session_id, e) for e in entries)


def count(conn: sqlite3.Connection, country_code: str) -> Dict[str, int]:
    """Conteo rápido por ronda (para verificación/diagnóstico)."""
    rows = conn.execute(
        "SELECT round, COUNT(*) FROM evidence_entries WHERE country_code=? GROUP BY round",
        (country_code.upper(),),
    ).fetchall()
    out = {r[0]: r[1] for r in rows}
    out["total"] = sum(out.values())
    return out
