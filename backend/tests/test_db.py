"""Tests para la capa de persistencia SQLite (db/)."""
import pytest
from db import (
    init_db, create_run, complete_run, get_run, list_runs,
    save_report, get_report, get_latest_report,
    create_session, close_session, get_session,
    save_entry, get_entries,
    save_alert, list_alerts,
    get_db_stats,
)


@pytest.fixture(autouse=True)
def setup_db(tmp_db):
    init_db(tmp_db)


class TestAnalysisRuns:
    def test_create_and_get_run(self):
        create_run("run-001", "PER", "2026-04-05")
        run = get_run("run-001")
        assert run is not None
        assert run["country_code"] == "PER"
        assert run["status"] == "running"

    def test_complete_run(self):
        create_run("run-002", "VEN")
        complete_run("run-002", risk_score=85.5, risk_level="critical")
        run = get_run("run-002")
        assert run["status"] == "completed"
        assert run["risk_score"] == 85.5
        assert run["risk_level"] == "critical"

    def test_failed_run(self):
        create_run("run-003", "NIC")
        complete_run("run-003", risk_score=0, risk_level="unknown", error_msg="API timeout")
        run = get_run("run-003")
        assert run["status"] == "failed"
        assert run["error_msg"] == "API timeout"

    def test_list_runs_by_country(self):
        create_run("run-per-1", "PER")
        create_run("run-per-2", "PER")
        create_run("run-ven-1", "VEN")
        runs = list_runs(country_code="PER")
        assert len(runs) == 2
        assert all(r["country_code"] == "PER" for r in runs)

    def test_get_nonexistent_run(self):
        assert get_run("nonexistent") is None


class TestReports:
    def test_save_and_get_report(self):
        create_run("run-rep-1", "PER")
        save_report("run-rep-1", "PER", "# Reporte Perú\n## Cap 1\nContenido...")
        report = get_report("run-rep-1")
        assert report is not None
        assert "Reporte Perú" in report["report_md"]

    def test_report_with_json(self):
        create_run("run-rep-2", "GTM")
        save_report(
            "run-rep-2", "GTM", "# Reporte\n",
            report_json={"risk_score": 60, "risk_level": "moderate"},
            chapters={"cap_01": "Executive summary..."}
        )
        report = get_report("run-rep-2")
        assert isinstance(report["report_json"], dict)
        assert report["report_json"]["risk_score"] == 60
        assert isinstance(report["chapters"], dict)

    def test_latest_report_returns_completed_only(self):
        create_run("run-rep-3", "URY")
        save_report("run-rep-3", "URY", "# Draft")
        # No completamos el run — status sigue 'running'
        report = get_latest_report("URY")
        assert report is None  # Solo retorna si run está completed
        complete_run("run-rep-3", risk_score=20.0, risk_level="low")
        report = get_latest_report("URY")
        assert report is not None


class TestObservationSessions:
    def test_create_and_close_session(self):
        create_session("sess-001", "PER", "election_day")
        session = get_session("sess-001")
        assert session["status"] == "active"
        assert session["phase"] == "election_day"
        close_session("sess-001")
        session = get_session("sess-001")
        assert session["status"] == "closed"
        assert session["ended_at"] is not None

    def test_session_entry_count_increments(self, sample_entry):
        create_session("sess-002", "PER")
        entry = {**sample_entry, "session_id": "sess-002"}
        save_entry(entry)
        session = get_session("sess-002")
        assert session["total_entries"] == 1


class TestObservationEntries:
    def test_save_and_get_entry(self, sample_entry):
        create_session(sample_entry["session_id"], "PER")
        save_entry(sample_entry)
        entries = get_entries(sample_entry["session_id"])
        assert len(entries) == 1
        assert entries[0]["category"] == "voter_intimidation"

    def test_filter_by_severity(self, sample_entries_batch):
        create_session("test-session-002", "PER")
        for entry in sample_entries_batch:
            save_entry(entry)
        high_entries = get_entries("test-session-002", severity="high")
        assert len(high_entries) == 6
        low_entries = get_entries("test-session-002", severity="low")
        assert len(low_entries) == 0

    def test_entry_deduplication_stored(self, sample_entry):
        create_session(sample_entry["session_id"], "PER")
        entry = {**sample_entry, "duplicate_of": "some-other-entry-id"}
        save_entry(entry)
        entries = get_entries(sample_entry["session_id"])
        assert entries[0]["duplicate_of"] == "some-other-entry-id"


class TestAlerts:
    def test_save_and_list_alerts(self):
        save_alert({
            "alert_id": "alert-001",
            "country_code": "PER",
            "event_type": "critical_entry",
            "severity": "critical",
            "title": "Intimidación electoral detectada",
            "channels_ok": 2,
        })
        alerts = list_alerts("PER")
        assert len(alerts) == 1
        assert alerts[0]["title"] == "Intimidación electoral detectada"

    def test_alert_deduplication(self):
        alert = {
            "alert_id": "alert-dup",
            "country_code": "NIC",
            "event_type": "fraud_pattern",
            "severity": "high",
            "title": "Patrón de fraude detectado",
        }
        save_alert(alert)
        save_alert(alert)  # INSERT OR IGNORE — no debe fallar ni duplicar
        alerts = list_alerts("NIC")
        assert len(alerts) == 1


class TestDbStats:
    def test_stats_structure(self):
        stats = get_db_stats()
        assert "analysis_runs" in stats
        assert "reports" in stats
        assert "observation_sessions" in stats
        assert "observation_entries" in stats
        assert "alerts" in stats
        assert "recent_runs" in stats
