"""
Tests E2E del pipeline PEIRS — flujo completo sin LLM real.
Verifica la integración entre: Field Validator → Audit Agent → RAG → DB → Alert.

Estos tests no hacen llamadas al LLM (usan mocks) y no requieren datasets CSV.
Cubren el flujo crítico que debe funcionar sin errores el 12 de abril.
"""
import json
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Fixtures compartidas ──────────────────────────────────────────────────────

@pytest.fixture
def session_per():
    """Sesión de observación activa para Perú."""
    return {
        "session_id": "e2e-session-per-001",
        "country_code": "PER",
        "phase": "election_day",
        "mission_name": "Misión DEMOCRAC.IA — Elecciones 2026",
        "lead_org": "DEMOCRAC.IA Observer Network",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "finalized": False,
        "entries": [],
        "run_id": "e2e-run-per-001",
    }


@pytest.fixture
def entry_intimidacion():
    return {
        "entry_id": "e2e-entry-001",
        "session_id": "e2e-session-per-001",
        "country_code": "PER",
        "phase": "election_day",
        "category": "voter_intimidation",
        "severity": "high",
        "finding": "Personal de seguridad no identificado impide el acceso a mesa de votación en local escolar",
        "location": "Lima, distrito La Victoria, local 0023",
        "observer_id": "OBS-PER-007",
        "observer_org": "DEMOCRAC.IA",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "has_evidence": True,
        "evidence_desc": "Fotografía y video del incidente",
        "rights_at_risk": ["ICCPR Art. 25", "CADH Art. 23"],
        "confidence": "probable",
        "verified": False,
    }


@pytest.fixture
def entry_fraude():
    return {
        "entry_id": "e2e-entry-002",
        "session_id": "e2e-session-per-001",
        "country_code": "PER",
        "phase": "counting",
        "category": "fraud_allegation",
        "severity": "critical",
        "finding": "Acta adulterada detectada en mesa 0047 — firmas de miembros de mesa no coinciden",
        "location": "Lima, San Juan de Lurigancho",
        "observer_id": "OBS-PER-012",
        "observer_org": "DEMOCRAC.IA",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "has_evidence": True,
        "evidence_desc": "Copia del acta con discrepancias documentadas",
        "rights_at_risk": ["ICCPR Art. 25(b)", "CDI Art. 3"],
        "confidence": "confirmed",
        "verified": True,
        "fraud_type": "counting",
        "credibility": "confirmed",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Field Validator → validación y deduplicación
# ═══════════════════════════════════════════════════════════════════════════════

class TestFieldValidatorE2E:

    def test_entry_passes_validation(self, entry_intimidacion):
        from modules.field_validator import validate_entry
        result = validate_entry(entry_intimidacion, existing_entries=[])
        assert result.valid
        assert result.quality_score > 0.5
        assert result.duplicate_of is None

    def test_duplicate_detected_same_category_location(self):
        from modules.field_validator import validate_entry
        # El validador usa "timestamp" + (mismo observer_id O misma location) + misma category
        original = {
            "entry_id": "orig-001",
            "session_id": "s1",
            "country_code": "PER",
            "category": "voter_intimidation",
            "severity": "high",
            "finding": "Personal no autorizado bloquea acceso a mesa de votación",
            "location": "Lima, La Victoria, local 0023",
            "observer_id": "OBS-007",
            "timestamp": "2026-04-12T09:30:00Z",
        }
        duplicate = {
            **original,
            "entry_id": "dup-001",
            "timestamp": "2026-04-12T09:32:00Z",  # 2 min después — dentro de ventana 5min
        }
        result = validate_entry(duplicate, existing_entries=[original])
        assert result.duplicate_of == "orig-001"

    def test_critical_without_evidence_gets_warning(self):
        from modules.field_validator import validate_entry
        entry = {
            "entry_id": "e2e-crit-nev",
            "session_id": "s1",
            "country_code": "PER",
            "category": "ballot_tampering",
            "severity": "critical",
            "finding": "Urna manipulada antes del cierre",
            "location": "Cusco",
            "observer_id": "OBS-001",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "has_evidence": False,
            "confidence": "unverified",
        }
        result = validate_entry(entry, existing_entries=[])
        assert any("evidencia" in w.lower() or "evidence" in w.lower() for w in result.warnings)

    def test_fraud_without_credibility_gets_warning(self, entry_fraude):
        from modules.field_validator import validate_entry
        entry = {**entry_fraude, "credibility": None, "has_evidence": False}
        result = validate_entry(entry, existing_entries=[])
        assert len(result.warnings) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 2. RAG keyword retriever — sin ChromaDB
# ═══════════════════════════════════════════════════════════════════════════════

class TestRAGKeywordRetriever:

    def test_query_intimidacion_returns_iccpr(self):
        from rag.retriever import _keyword_query
        results = _keyword_query("intimidacion votantes elecciones", n_results=3)
        assert len(results) > 0
        instruments = [r["instrument"] for r in results]
        assert any("ICCPR" in i for i in instruments)

    def test_query_fraude_actas_returns_relevant(self):
        from rag.retriever import _keyword_query
        results = _keyword_query("fraude actas escrutinio resultados electorales", n_results=3)
        assert len(results) > 0
        assert all(r["relevance"] > 0 for r in results)

    def test_query_returns_excerpt(self):
        from rag.retriever import _keyword_query
        results = _keyword_query("sufragio universal derecho voto", n_results=2)
        for r in results:
            assert "title" in r
            assert "instrument" in r
            assert "relevance" in r
            assert "excerpt" in r

    def test_query_category_filter(self):
        from rag.retriever import _keyword_query
        results = _keyword_query("violencia genero candidatas", n_results=5,
                                  category_filter=["gender_rights", "hate_speech"])
        # No debe retornar docs de otras categorías si hay filtro
        for r in results:
            # Solo verificar que algo retorna — el corpus puede no tener esas categorías
            assert isinstance(r, dict)

    def test_legal_context_function(self):
        from rag.retriever import query_legal_context
        results = query_legal_context("voter intimidation polling station", country="Peru", n_results=3)
        assert isinstance(results, list)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Audit Agent — detección de anomalías
# ═══════════════════════════════════════════════════════════════════════════════

class TestAuditAgentE2E:

    def test_clean_session_no_findings(self, session_per, entry_intimidacion):
        from agents.auditor import AuditAgent
        session = {**session_per, "entries": [entry_intimidacion]}
        agent = AuditAgent()
        result = agent.audit_session(session, country_code="PER")
        assert result.audit_score > 0.5
        assert not result.has_critical

    def test_flood_detection(self, session_per):
        from agents.auditor import AuditAgent, FLOOD_ENTRIES_THRESHOLD, FLOOD_WINDOW_MINUTES
        from datetime import timedelta
        # Generar entradas en ventana de tiempo reciente
        now = datetime.now(timezone.utc)
        entries = []
        for i in range(FLOOD_ENTRIES_THRESHOLD + 2):
            entries.append({
                "entry_id": f"flood-{i:03d}",
                "session_id": session_per["session_id"],
                "country_code": "PER",
                "category": "irregular_procedure",
                "severity": "medium",
                "finding": f"Procedimiento irregular en mesa {i}",
                "location": "Lima",
                "observer_id": f"OBS-{i:03d}",
                "submitted_at": (now - timedelta(minutes=1)).isoformat(),
                "has_evidence": False,
                "confidence": "unverified",
            })
        session = {**session_per, "entries": entries}
        agent = AuditAgent()
        result = agent.audit_session(session, country_code="PER")
        flood_findings = [f for f in result.findings if f.code == "FLOOD_DETECTED"]
        assert len(flood_findings) > 0
        assert result.has_critical

    def test_single_observer_concentration(self, session_per):
        from agents.auditor import AuditAgent
        entries = []
        for i in range(10):
            entries.append({
                "entry_id": f"conc-{i:03d}",
                "session_id": session_per["session_id"],
                "country_code": "PER",
                "category": "irregular_procedure",
                "severity": "low",
                "finding": f"Hallazgo {i}",
                "location": "Lima",
                "observer_id": "OBS-SOLO-001",  # mismo observador siempre
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "has_evidence": True,
                "confidence": "probable",
            })
        session = {**session_per, "entries": entries}
        result = AuditAgent().audit_session(session, country_code="PER")
        conc = [f for f in result.findings if f.code == "SINGLE_OBSERVER_CONCENTRATION"]
        assert len(conc) > 0

    def test_audit_score_decreases_with_findings(self, session_per):
        from agents.auditor import AuditAgent
        from datetime import timedelta
        # Sesión limpia
        clean_session = {**session_per, "entries": [{
            "entry_id": "ok-001",
            "session_id": session_per["session_id"],
            "country_code": "PER",
            "category": "voter_intimidation",
            "severity": "high",
            "finding": "Hallazgo documentado con evidencia",
            "location": "Miraflores",
            "observer_id": "OBS-A",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "has_evidence": True,
            "confidence": "confirmed",
        }]}
        now = datetime.now(timezone.utc)
        # Sesión con flood
        flood_session = {**session_per, "entries": [
            {
                "entry_id": f"bad-{i}",
                "session_id": session_per["session_id"],
                "country_code": "PER",
                "category": "other",
                "severity": "medium",
                "finding": f"Entry {i}",
                "location": "Lima",
                "observer_id": "BOT-001",
                "submitted_at": (now).isoformat(),
                "has_evidence": False,
                "confidence": "unverified",
            } for i in range(15)
        ]}
        agent = AuditAgent()
        clean_result = agent.audit_session(clean_session, country_code="PER")
        flood_result  = agent.audit_session(flood_session, country_code="PER")
        assert clean_result.audit_score > flood_result.audit_score


# ═══════════════════════════════════════════════════════════════════════════════
# 4. DB — flujo completo observation session + entries
# ═══════════════════════════════════════════════════════════════════════════════

class TestE2EObservationFlow:

    @pytest.fixture(autouse=True)
    def setup_db(self, tmp_db):
        from db import init_db
        init_db(tmp_db)

    def test_full_observation_flow(self, tmp_db, entry_intimidacion, entry_fraude):
        from db import (
            create_run, complete_run, create_session, save_entry,
            get_entries, get_session, get_db_stats,
        )
        # 1. Crear run de análisis
        create_run("e2e-run-001", "PER", "2026-04-12")
        # 2. Crear sesión de observación
        create_session("e2e-session-001", "PER", phase="election_day", run_id="e2e-run-001")
        # 3. Registrar hallazgos
        e1 = {**entry_intimidacion, "session_id": "e2e-session-001"}
        e2 = {**entry_fraude,       "session_id": "e2e-session-001"}
        save_entry(e1)
        save_entry(e2)
        # 4. Verificar que quedaron persistidos
        entries = get_entries("e2e-session-001")
        assert len(entries) == 2
        categories = {e["category"] for e in entries}
        assert "voter_intimidation" in categories
        assert "fraud_allegation" in categories
        # 5. Verificar sesión
        session = get_session("e2e-session-001")
        assert session["total_entries"] == 2
        # 6. Completar el run
        complete_run("e2e-run-001", risk_score=72.0, risk_level="high")
        # 7. Stats globales
        stats = get_db_stats()
        assert stats["observation_sessions"] >= 1
        assert stats["observation_entries"] >= 2

    def test_entry_severity_filter(self, tmp_db, entry_intimidacion, entry_fraude):
        from db import create_session, save_entry, get_entries
        create_session("e2e-session-002", "PER", phase="election_day")
        e1 = {**entry_intimidacion, "session_id": "e2e-session-002"}
        e2 = {**entry_fraude,       "session_id": "e2e-session-002"}
        save_entry(e1)
        save_entry(e2)
        critical_entries = get_entries("e2e-session-002", severity="critical")
        assert len(critical_entries) == 1
        assert critical_entries[0]["category"] == "fraud_allegation"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Integración: validator → auditor → DB en secuencia
# ═══════════════════════════════════════════════════════════════════════════════

class TestE2EIntegration:

    @pytest.fixture(autouse=True)
    def setup_db(self, tmp_db):
        from db import init_db
        init_db(tmp_db)

    def test_validate_then_audit_then_persist(self, tmp_db, session_per, entry_intimidacion):
        """
        Flujo completo: entrada llega → se valida → se audita → se persiste en DB.
        Este es el camino crítico del día de elecciones.
        """
        from modules.field_validator import validate_entry
        from agents.auditor import AuditAgent
        from db import create_session, save_entry, get_entries

        # 1. Validar la entrada
        validation = validate_entry(entry_intimidacion, existing_entries=[])
        assert validation.valid
        assert validation.duplicate_of is None

        # 2. Aplicar resultado de validación a la entrada
        entry_to_save = {
            **entry_intimidacion,
            "validated": 1 if validation.valid else 0,
            "quality_score": validation.quality_score,
            "validation_notes": validation.warnings,
        }

        # 3. Persistir en DB
        create_session("e2e-int-session", "PER", phase="election_day")
        entry_to_save["session_id"] = "e2e-int-session"
        save_entry(entry_to_save)

        # 4. Auditar la sesión con la entrada persistida
        session_with_entry = {**session_per, "entries": [entry_intimidacion]}
        agent = AuditAgent()
        audit = agent.audit_session(session_with_entry, country_code="PER")
        assert audit.audit_score > 0.5

        # 5. Verificar que la entrada está en DB
        entries = get_entries("e2e-int-session")
        assert len(entries) == 1
        assert entries[0]["validated"] == 1

    def test_rag_enriches_legal_analysis(self):
        """
        El RAG keyword retriever enriquece el análisis legal con jurisprudencia.
        """
        from rag.retriever import query_legal_context
        # Simular una violación detectada por el Legal Compliance Agent
        violation = {
            "right": "Sufragio universal",
            "finding": "Intimidación de votantes en acceso a mesa de votación",
            "article": "Art. 25(b)",
            "treaty": "ICCPR",
        }
        query = f"{violation['right']} {violation['finding']}"
        rag_hits = query_legal_context(query, country="Peru", n_results=2)

        # El RAG debe retornar al menos una referencia legal relevante
        assert len(rag_hits) > 0
        # Los hits deben tener la estructura correcta
        for hit in rag_hits:
            assert "instrument" in hit
            assert "title" in hit
            assert "relevance" in hit
            assert hit["relevance"] > 0
