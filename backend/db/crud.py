"""
DEMOCRAC.IA / PEIRS — CRUD helpers SQLite
Operaciones de base de datos para análisis, reportes, observaciones y alertas.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from db.schema import SCHEMA_SQL, SCHEMA_VERSION

# ── Ruta de la base de datos ──────────────────────────────────────────────────
_DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "peirs.db"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Conexión ──────────────────────────────────────────────────────────────────

def get_db_path() -> Path:
    import os
    return Path(os.getenv("PEIRS_DB_PATH", str(_DEFAULT_DB_PATH)))


@contextmanager
def get_conn(db_path: Optional[Path] = None):
    """Context manager para conexiones SQLite con WAL y FK habilitados."""
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Inicialización ────────────────────────────────────────────────────────────

def init_db(db_path: Optional[Path] = None) -> None:
    """Crea las tablas si no existen. Idempotente."""
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        # Guarda la versión del schema
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _schema_meta (
                key TEXT PRIMARY KEY, value TEXT
            )
        """)
        conn.execute(
            "INSERT OR REPLACE INTO _schema_meta VALUES ('version', ?)",
            (str(SCHEMA_VERSION),)
        )
    print(f"[DB] OK: SQLite inicializado en {get_db_path()}")


# ── Analysis Runs ─────────────────────────────────────────────────────────────

def create_run(run_id: str, country_code: str, election_date: Optional[str] = None) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO analysis_runs
               (run_id, country_code, election_date, started_at, status)
               VALUES (?, ?, ?, ?, 'running')""",
            (run_id, country_code, election_date, _utcnow())
        )


def complete_run(
    run_id: str,
    risk_score: float,
    risk_level: str,
    data_confidence: str = "medium",
    error_msg: Optional[str] = None,
) -> None:
    status = "failed" if error_msg else "completed"
    with get_conn() as conn:
        conn.execute(
            """UPDATE analysis_runs
               SET completed_at=?, status=?, risk_score=?, risk_level=?,
                   data_confidence=?, error_msg=?
               WHERE run_id=?""",
            (_utcnow(), status, risk_score, risk_level, data_confidence, error_msg, run_id)
        )


def get_run(run_id: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM analysis_runs WHERE run_id=?", (run_id,)
        ).fetchone()
        return dict(row) if row else None


def list_runs(country_code: Optional[str] = None, limit: int = 50) -> List[Dict]:
    with get_conn() as conn:
        if country_code:
            rows = conn.execute(
                "SELECT * FROM analysis_runs WHERE country_code=? ORDER BY started_at DESC LIMIT ?",
                (country_code, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM analysis_runs ORDER BY started_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


# ── Reports ───────────────────────────────────────────────────────────────────

def save_report(
    run_id: str,
    country_code: str,
    report_md: str,
    report_json: Optional[Dict] = None,
    chapters: Optional[Dict] = None,
    file_path: Optional[str] = None,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO reports
               (run_id, country_code, report_md, report_json, chapters, created_at, file_path)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                country_code,
                report_md,
                json.dumps(report_json) if report_json else None,
                json.dumps(chapters) if chapters else None,
                _utcnow(),
                file_path,
            )
        )
        return cur.lastrowid


def get_report(run_id: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE run_id=? ORDER BY created_at DESC LIMIT 1",
            (run_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("report_json"):
            d["report_json"] = json.loads(d["report_json"])
        if d.get("chapters"):
            d["chapters"] = json.loads(d["chapters"])
        return d


def get_latest_report(country_code: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            """SELECT r.* FROM reports r
               JOIN analysis_runs a ON r.run_id = a.run_id
               WHERE r.country_code=? AND a.status='completed'
               ORDER BY r.created_at DESC LIMIT 1""",
            (country_code,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("report_json"):
            d["report_json"] = json.loads(d["report_json"])
        return d


# ── Observation Sessions ──────────────────────────────────────────────────────

def create_session(
    session_id: str,
    country_code: str,
    phase: str = "pre_election",
    run_id: Optional[str] = None,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO observation_sessions
               (session_id, country_code, phase, started_at, status, run_id)
               VALUES (?, ?, ?, ?, 'active', ?)""",
            (session_id, country_code, phase, _utcnow(), run_id)
        )


def close_session(session_id: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE observation_sessions SET status='closed', ended_at=? WHERE session_id=?",
            (_utcnow(), session_id)
        )


def get_session(session_id: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM observation_sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        return dict(row) if row else None


# ── Observation Entries ───────────────────────────────────────────────────────

def save_entry(entry: Dict[str, Any]) -> None:
    """Guarda un hallazgo validado. El dict debe tener entry_id y session_id."""
    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO observation_entries (
               entry_id, session_id, country_code, category, severity,
               finding, location, observed_at, submitted_at,
               validated, quality_score, duplicate_of, validation_notes,
               has_evidence, evidence_desc, evidence_url,
               observer_id, observer_org,
               confidence, iccpr_articles, cedaw_articles
            ) VALUES (
               :entry_id, :session_id, :country_code, :category, :severity,
               :finding, :location, :observed_at, :submitted_at,
               :validated, :quality_score, :duplicate_of, :validation_notes,
               :has_evidence, :evidence_desc, :evidence_url,
               :observer_id, :observer_org,
               :confidence, :iccpr_articles, :cedaw_articles
            )""",
            {
                "entry_id": entry.get("entry_id"),
                "session_id": entry.get("session_id"),
                "country_code": entry.get("country_code"),
                "category": entry.get("category"),
                "severity": entry.get("severity", "medium"),
                "finding": entry.get("finding"),
                "location": entry.get("location"),
                "observed_at": entry.get("observed_at", _utcnow()),
                "submitted_at": entry.get("submitted_at", _utcnow()),
                "validated": 1 if entry.get("validated") else 0,
                "quality_score": entry.get("quality_score"),
                "duplicate_of": entry.get("duplicate_of"),
                "validation_notes": json.dumps(entry.get("validation_notes", [])),
                "has_evidence": 1 if entry.get("has_evidence") else 0,
                "evidence_desc": entry.get("evidence_desc"),
                "evidence_url": entry.get("evidence_url"),
                "observer_id": entry.get("observer_id"),
                "observer_org": entry.get("observer_org"),
                "confidence": entry.get("confidence", "unverified"),
                "iccpr_articles": json.dumps(entry.get("iccpr_articles", [])),
                "cedaw_articles": json.dumps(entry.get("cedaw_articles", [])),
            }
        )
        # Actualiza contador de la sesión
        conn.execute(
            "UPDATE observation_sessions SET total_entries = total_entries + 1 WHERE session_id=?",
            (entry.get("session_id"),)
        )


def get_entries(session_id: str, severity: Optional[str] = None) -> List[Dict]:
    with get_conn() as conn:
        if severity:
            rows = conn.execute(
                "SELECT * FROM observation_entries WHERE session_id=? AND severity=? ORDER BY submitted_at DESC",
                (session_id, severity)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM observation_entries WHERE session_id=? ORDER BY submitted_at DESC",
                (session_id,)
            ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            for col in ("validation_notes", "iccpr_articles", "cedaw_articles"):
                if d.get(col):
                    try:
                        d[col] = json.loads(d[col])
                    except (json.JSONDecodeError, TypeError):
                        pass
            result.append(d)
        return result


# ── Detection Patterns ────────────────────────────────────────────────────────

def save_pattern(
    session_id: str,
    pattern_type: str,
    description: str,
    districts: Optional[List[str]] = None,
    entry_count: int = 0,
    fraud_score: float = 0.0,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO detection_patterns
               (session_id, pattern_type, description, districts, entry_count, fraud_score, detected_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id, pattern_type, description,
                json.dumps(districts or []),
                entry_count, fraud_score, _utcnow()
            )
        )
        # Actualiza pattern_score de la sesión si es mayor
        conn.execute(
            "UPDATE observation_sessions SET pattern_score = MAX(COALESCE(pattern_score, 0), ?) WHERE session_id=?",
            (fraud_score, session_id)
        )


# ── Alerts ────────────────────────────────────────────────────────────────────

def save_alert(alert: Dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO alerts (
               alert_id, country_code, event_type, severity, title, description,
               entry_id, session_id, fraud_score, rights_at_risk,
               dispatched_at, channels, channels_ok, error_msg
            ) VALUES (
               :alert_id, :country_code, :event_type, :severity, :title, :description,
               :entry_id, :session_id, :fraud_score, :rights_at_risk,
               :dispatched_at, :channels, :channels_ok, :error_msg
            )""",
            {
                "alert_id": alert.get("alert_id"),
                "country_code": alert.get("country_code"),
                "event_type": alert.get("event_type"),
                "severity": alert.get("severity"),
                "title": alert.get("title"),
                "description": alert.get("description"),
                "entry_id": alert.get("entry_id"),
                "session_id": alert.get("session_id"),
                "fraud_score": alert.get("fraud_score"),
                "rights_at_risk": json.dumps(alert.get("rights_at_risk", [])),
                "dispatched_at": alert.get("dispatched_at", _utcnow()),
                "channels": json.dumps(alert.get("channels", {})),
                "channels_ok": alert.get("channels_ok", 0),
                "error_msg": alert.get("error_msg"),
            }
        )


def list_alerts(country_code: str, limit: int = 100) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM alerts WHERE country_code=? ORDER BY dispatched_at DESC LIMIT ?",
            (country_code, limit)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            for col in ("rights_at_risk", "channels"):
                if d.get(col):
                    try:
                        d[col] = json.loads(d[col])
                    except (json.JSONDecodeError, TypeError):
                        pass
            result.append(d)
        return result


# ── OONI Snapshots ────────────────────────────────────────────────────────────

def save_ooni_snapshot(
    country_code: str,
    blocked_urls: int,
    anomalies: int,
    summary: Dict,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO ooni_snapshots
               (country_code, fetched_at, blocked_urls, anomalies, summary_json)
               VALUES (?, ?, ?, ?, ?)""",
            (country_code, _utcnow(), blocked_urls, anomalies, json.dumps(summary))
        )


def get_latest_ooni(country_code: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM ooni_snapshots WHERE country_code=? ORDER BY fetched_at DESC LIMIT 1",
            (country_code,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("summary_json"):
            d["summary_json"] = json.loads(d["summary_json"])
        return d


# ── Stats / Dashboard ─────────────────────────────────────────────────────────

def get_db_stats() -> Dict:
    """Resumen rápido del estado de la base de datos."""
    with get_conn() as conn:
        stats = {}
        for table in ("analysis_runs", "reports", "observation_sessions",
                      "observation_entries", "alerts"):
            row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            stats[table] = row[0] if row else 0
        # Últimas 5 ejecuciones
        rows = conn.execute(
            "SELECT run_id, country_code, risk_level, completed_at FROM analysis_runs "
            "WHERE status='completed' ORDER BY completed_at DESC LIMIT 5"
        ).fetchall()
        stats["recent_runs"] = [dict(r) for r in rows]
        return stats
