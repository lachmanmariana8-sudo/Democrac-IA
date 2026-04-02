"""pytest conftest — fixtures compartidas para PEIRS test suite."""
import os
import sys
from pathlib import Path

import pytest

# Asegura que backend/ está en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_db(tmp_path):
    """Base de datos SQLite temporal para tests."""
    db_path = tmp_path / "test_peirs.db"
    os.environ["PEIRS_DB_PATH"] = str(db_path)
    yield db_path
    if db_path.exists():
        db_path.unlink()
    del os.environ["PEIRS_DB_PATH"]


@pytest.fixture
def sample_entry():
    """Hallazgo de campo de ejemplo."""
    return {
        "entry_id": "test-entry-001",
        "session_id": "test-session-001",
        "country_code": "PER",
        "category": "voter_intimidation",
        "severity": "high",
        "finding": "Observadores reportan presencia de personal no autorizado en mesa de votación",
        "location": "Lima, distrito La Victoria, local 0023",
        "observed_at": "2026-04-05T09:30:00Z",
        "submitted_at": "2026-04-05T09:35:00Z",
        "confidence": "probable",
        "has_evidence": True,
        "evidence_desc": "Fotografía del incidente",
    }


@pytest.fixture
def sample_entries_batch():
    """Múltiples hallazgos para tests de patrones."""
    base = {
        "session_id": "test-session-002",
        "country_code": "PER",
        "category": "irregular_procedure",
        "severity": "high",
        "observed_at": "2026-04-05T09:00:00Z",
        "submitted_at": "2026-04-05T09:05:00Z",
        "confidence": "probable",
    }
    return [
        {**base, "entry_id": f"test-entry-{i:03d}",
         "finding": f"Procedimiento irregular en mesa {i}",
         "location": f"Lima, distrito {['San Juan', 'Miraflores', 'La Victoria'][i % 3]}"}
        for i in range(6)
    ]
