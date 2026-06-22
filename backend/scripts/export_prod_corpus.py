#!/usr/bin/env python
"""Exporta el corpus completo de observación (Hunter) desde producción (Railway)
hacia un JSONL crudo versionado — la base de prueba trazable de cada informe.

Determinista, read-only, SIN costo LLM: pagina GET /api/observation/{cc}/entries.
No llama a ningún endpoint /generate.

Uso:
    python -m scripts.export_prod_corpus --country PER
    python -m scripts.export_prod_corpus --country PER --base https://...railway.app

Salida:
    evidence_base/raw/{CC}_session_{sid8}.jsonl   (una línea por captura)
    evidence_base/raw/{CC}_export_meta.json       (sesión, totales, fecha de pull)

El crudo íntegro hace AUDITABLE la deduplicación posterior: cualquiera puede
re-correr build_evidence_base.py y reproducir los conteos del informe.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

DEFAULT_BASE = "https://democracia-peirs-production.up.railway.app"
# Raíz del repo = .../DemocracIA (scripts/ está bajo backend/)
REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "evidence_base" / "raw"


def _fetch(url: str, timeout: int = 60) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec: URL fija de prod
        return json.loads(resp.read().decode("utf-8"))


def export_corpus(country: str, base: str, page_size: int = 500) -> Path:
    cc = country.upper()
    base = base.rstrip("/")

    # 1) total + session_id de la sesión activa
    head = _fetch(f"{base}/api/observation/{cc}/entries?limit=1&offset=0")
    total = int(head.get("total_matching", 0))
    sid = head.get("session_id") or "unknown"
    if total == 0:
        print(f"[export] {cc}: 0 entradas — nada que exportar.", file=sys.stderr)
        sys.exit(1)
    print(f"[export] {cc} sesión {sid}: {total} entradas a paginar (page={page_size}).")

    # 2) paginar
    seen: set[str] = set()
    entries: list[dict] = []
    offset = 0
    while offset < total:
        page = _fetch(f"{base}/api/observation/{cc}/entries?limit={page_size}&offset={offset}")
        chunk = page.get("entries", [])
        if not chunk:
            break
        for e in chunk:
            eid = e.get("entry_id")
            # Dedup defensivo por entry_id (la paginación no debería repetir,
            # pero el store puede mutar entre páginas durante el pull).
            key = eid or f"_noid_{offset}_{len(entries)}"
            if key in seen:
                continue
            seen.add(key)
            entries.append(e)
        offset += len(chunk)
        print(f"[export]   {min(offset, total)}/{total}")

    # 3) escribir crudo (orden estable por recorded_at, entry_id)
    entries.sort(key=lambda e: ((e.get("recorded_at") or ""), (e.get("entry_id") or "")))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sid8 = (sid or "unknown")[:8]
    out = RAW_DIR / f"{cc}_session_{sid8}.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")

    meta = {
        "country_code": cc,
        "session_id": sid,
        "source_base": base,
        "total_reported": total,
        "total_written": len(entries),
        "with_source_url": sum(1 for e in entries if e.get("evidence_ref") or e.get("url")),
    }
    (RAW_DIR / f"{cc}_export_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[export] OK -> {out} ({len(entries)} filas; "
          f"{meta['with_source_url']} con URL de fuente)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Exporta corpus de observación desde prod.")
    ap.add_argument("--country", default="PER")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--page-size", type=int, default=500)
    args = ap.parse_args()
    export_corpus(args.country, args.base, args.page_size)


if __name__ == "__main__":
    main()
