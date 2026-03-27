"""
DEMOCRAC.IA / PEIRS — db/
Capa de persistencia SQLite.

Uso:
    from db import init_db, create_run, save_report, save_entry, save_alert
    init_db()  # llamar al inicio de la app
"""
from db.crud import (
    init_db,
    get_conn,
    # Runs
    create_run,
    complete_run,
    get_run,
    list_runs,
    # Reports
    save_report,
    get_report,
    get_latest_report,
    # Observation sessions
    create_session,
    close_session,
    get_session,
    # Entries
    save_entry,
    get_entries,
    # Patterns
    save_pattern,
    # Alerts
    save_alert,
    list_alerts,
    # OONI
    save_ooni_snapshot,
    get_latest_ooni,
    # Stats
    get_db_stats,
)

__all__ = [
    "init_db", "get_conn",
    "create_run", "complete_run", "get_run", "list_runs",
    "save_report", "get_report", "get_latest_report",
    "create_session", "close_session", "get_session",
    "save_entry", "get_entries",
    "save_pattern",
    "save_alert", "list_alerts",
    "save_ooni_snapshot", "get_latest_ooni",
    "get_db_stats",
]
