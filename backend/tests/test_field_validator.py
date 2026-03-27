"""Tests para Agent 5: FieldDataValidationAgent (modules/field_validator.py)."""
import pytest
from modules.field_validator import validate_entry, detect_patterns, render_pattern_markdown


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_entry(**kwargs):
    base = {
        "entry_id": "e-001",
        "category": "voter_intimidation",
        "severity": "high",
        "finding": "Personal no autorizado en la mesa de votación, identificado como miembro del partido gobernante",
        "location": "Lima, La Victoria, Local 0023",
        "timestamp": "2026-04-05T09:30:00Z",
        "confidence": "probable",
        "has_evidence": True,
        "credibility_source": "observer_field",
    }
    base.update(kwargs)
    return base


# ── Tests de validación individual ───────────────────────────────────────────

class TestValidateEntry:
    def test_valid_entry_passes(self):
        entry = make_entry()
        result = validate_entry(entry, [])
        assert result.valid is True
        assert result.quality_score > 0.5

    def test_short_finding_generates_warning(self):
        entry = make_entry(finding="Problema")
        result = validate_entry(entry, [])
        warnings = [w for w in result.warnings if "corto" in w.lower() or "breve" in w.lower() or "finding" in w.lower()]
        # Debe haber al menos un warning sobre el finding
        assert len(result.warnings) > 0

    def test_critical_without_evidence_generates_warning(self):
        entry = make_entry(severity="critical", has_evidence=False)
        result = validate_entry(entry, [])
        # No debe bloquear, pero sí advertir
        assert result.valid is True
        assert len(result.warnings) > 0

    def test_fraud_allegation_needs_credibility(self):
        entry = make_entry(
            category="fraud_allegation",
            severity="critical",
            has_evidence=False,
            credibility_source=None,
        )
        result = validate_entry(entry, [])
        # Fraude crítico sin evidencia ni fuente de credibilidad debe generar warnings
        assert len(result.warnings) > 0

    def test_duplicate_detection(self):
        existing_entry = make_entry(entry_id="e-original", timestamp="2026-04-05T09:30:00Z")
        duplicate = make_entry(
            entry_id="e-dup",
            finding="Personal no autorizado en la mesa de votación, identificado como miembro del partido gobernante",
            timestamp="2026-04-05T09:32:00Z",  # 2 minutos después
        )
        result = validate_entry(duplicate, [existing_entry])
        assert result.duplicate_of == "e-original"

    def test_different_findings_not_duplicate(self):
        existing = make_entry(entry_id="e-001", finding="Irregularidad en padrón electoral")
        new = make_entry(entry_id="e-002", finding="Intimidación a votantes en la cola")
        result = validate_entry(new, [existing])
        assert result.duplicate_of is None

    def test_quality_score_range(self):
        entry = make_entry()
        result = validate_entry(entry, [])
        assert 0.0 <= result.quality_score <= 1.0

    def test_missing_required_fields_invalid(self):
        entry = {"entry_id": "e-bad", "category": "other"}  # Sin finding ni severity
        result = validate_entry(entry, [])
        assert result.valid is False
        assert len(result.errors) > 0


# ── Tests de detección de patrones ───────────────────────────────────────────

class TestDetectPatterns:
    def make_entries_batch(self, n=5, location_prefix="Lima, La Victoria"):
        return [
            make_entry(
                entry_id=f"e-{i:03d}",
                category="irregular_procedure",
                severity="high",
                location=f"{location_prefix}, Local {i:04d}",
                timestamp=f"2026-04-05T0{9+i//4}:{(i*10)%60:02d}:00Z",
            )
            for i in range(n)
        ]

    def test_geographic_pattern_detected(self):
        entries = self.make_entries_batch(5, "Lima, La Victoria")
        patterns = detect_patterns(entries)
        geo_patterns = [p for p in patterns if p.pattern_type == "geographic"]
        assert len(geo_patterns) > 0

    def test_category_cluster_detected(self):
        entries = [
            make_entry(entry_id=f"e-{i}", category="voter_intimidation", severity="high",
                      location=f"Lima, distrito {i}", timestamp=f"2026-04-05T09:0{i}:00Z")
            for i in range(4)
        ]
        patterns = detect_patterns(entries)
        category_patterns = [p for p in patterns if p.pattern_type == "category_cluster"]
        assert len(category_patterns) > 0

    def test_no_patterns_with_few_entries(self):
        entries = self.make_entries_batch(1)
        patterns = detect_patterns(entries)
        # Con 1 sola entrada no debe haber patrones geográficos
        geo = [p for p in patterns if p.pattern_type == "geographic"]
        assert len(geo) == 0

    def test_fraud_score_increases_with_patterns(self):
        few = self.make_entries_batch(2)
        many = self.make_entries_batch(8)
        patterns_few = detect_patterns(few)
        patterns_many = detect_patterns(many)
        score_few = max((p.fraud_score for p in patterns_few), default=0.0)
        score_many = max((p.fraud_score for p in patterns_many), default=0.0)
        assert score_many >= score_few


# ── Tests de render markdown ──────────────────────────────────────────────────

class TestRenderPatternMarkdown:
    def test_renders_nonempty_string(self):
        entries = [
            make_entry(entry_id=f"e-{i}", severity="high",
                      location=f"Lima, La Victoria, Local {i}",
                      timestamp=f"2026-04-05T09:0{i}:00Z")
            for i in range(5)
        ]
        patterns = detect_patterns(entries)
        md = render_pattern_markdown(patterns, entries)
        assert isinstance(md, str)
        assert len(md) > 0

    def test_renders_empty_for_no_patterns(self):
        md = render_pattern_markdown([], [])
        assert isinstance(md, str)
