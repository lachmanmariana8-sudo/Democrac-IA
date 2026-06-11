"""Tests para modules/runoff_enrichment.py — merge Hunter→ejes OSINT + escalación.

Función pura: sin fixtures de DB, sin monkeypatch, sin red.
Paridad 3.11/3.14: se evitan f-strings anidados.
"""
import copy

import pytest

from modules.peru_data import PERU_RUNOFF_2026
from modules.runoff_enrichment import (
    enrich_runoff_observation,
    compute_axis_audit_status,
    HUNTER_CATEGORY_TO_AXIS,
    MIN_INDEPENDENT_PRIMARY,
    CONFIRM_INDEPENDENT_PRIMARY,
    PRIMARY_CREDIBILITY,
    AUDIT_PENDING,
    AUDIT_SECONDARY,
    AUDIT_CONFIRMED,
)

OSINT_AXES = (
    "hate_speech_and_intimidation_incidents",
    "osint_information_integrity_monitor",
    "electoral_violence_incidents",
)


def _entry(entry_id, category, **kw):
    """Construye un entry estilo observation_store con defaults razonables."""
    base = {
        "entry_id": entry_id,
        "timestamp": "2026-06-05T12:00:00+00:00",
        "category": category,
        "finding": "Hallazgo de prueba " + entry_id,
        "severity": "high",
        "verified": False,
        "credibility": "medium",
        "evidence_ref": "https://example.org/" + entry_id,
        "hunter_source": "rss",
        "source_org": "Hunter/rss",
        "location": "Lima",
    }
    base.update(kw)
    return base


def _item_key(axis):
    return "narratives" if axis == "osint_information_integrity_monitor" else "incidents"


# ── No-mutación (propiedad de seguridad clave) ────────────────────────────────

def test_no_mutation_of_input_dict():
    snapshot = copy.deepcopy(PERU_RUNOFF_2026)
    entries = [_entry("e1", "hate_speech", credibility="high", hunter_source="ojo_publico")]
    enrich_runoff_observation(PERU_RUNOFF_2026, entries)
    assert PERU_RUNOFF_2026 == snapshot, "enrich no debe mutar el dict de módulo"


def test_no_mutation_of_entries():
    entries = [_entry("e1", "security", credibility="high")]
    snapshot = copy.deepcopy(entries)
    enrich_runoff_observation(PERU_RUNOFF_2026, entries)
    assert entries == snapshot


# ── Estado vacío ──────────────────────────────────────────────────────────────

def test_empty_entries_keeps_pendiente():
    enriched = enrich_runoff_observation(PERU_RUNOFF_2026, [])
    obs = enriched["runoff_phase_observation"]
    for axis in OSINT_AXES:
        assert obs[axis]["audit_status"] == AUDIT_PENDING
        assert obs[axis][_item_key(axis)] == []


# ── Mapping categoría → eje ───────────────────────────────────────────────────

def test_category_to_axis_mapping_lands_in_one_axis():
    # Un entry por cada categoría mapeada; cada uno aterriza en su eje y solo ahí.
    for category, axis in HUNTER_CATEGORY_TO_AXIS.items():
        entries = [_entry("e1", category)]
        obs = enrich_runoff_observation(PERU_RUNOFF_2026, entries)["runoff_phase_observation"]
        assert len(obs[axis][_item_key(axis)]) == 1, "categoría " + category + " debe ir a " + axis
        # Ningún otro eje OSINT recibió el item.
        for other in OSINT_AXES:
            if other == axis:
                continue
            assert obs[other][_item_key(other)] == [], category + " no debe contaminar " + other


def test_gender_violence_routes_to_violence_axis():
    obs = enrich_runoff_observation(
        PERU_RUNOFF_2026, [_entry("e1", "gender_violence")]
    )["runoff_phase_observation"]
    assert len(obs["electoral_violence_incidents"]["incidents"]) == 1
    assert obs["hate_speech_and_intimidation_incidents"]["incidents"] == []


def test_unmapped_categories_are_ignored():
    for category in ("logistics", "legal", "media", "counting", "results",
                     "campaign_violation", "accessibility", "irregular_procedure", "other"):
        obs = enrich_runoff_observation(
            PERU_RUNOFF_2026, [_entry("e1", category)]
        )["runoff_phase_observation"]
        for axis in OSINT_AXES:
            assert obs[axis][_item_key(axis)] == [], category + " no debe poblar " + axis


# ── Trazabilidad del item fusionado ───────────────────────────────────────────

def test_merged_item_carries_traceability():
    entries = [_entry(
        "trace-99", "disinformation",
        severity="critical", credibility="high", verified=True,
        evidence_ref="https://dfrlab.org/x", hunter_source="dfrlab",
    )]
    obs = enrich_runoff_observation(PERU_RUNOFF_2026, entries)["runoff_phase_observation"]
    item = obs["osint_information_integrity_monitor"]["narratives"][0]
    assert item["hunter_entry_id"] == "trace-99"
    assert item["severity"] == "critical"
    assert item["credibility"] == "high"
    assert item["verified"] is True
    assert item["source_url"] == "https://dfrlab.org/x"
    assert item["sources"] == ["dfrlab"]
    assert item["verification_level"] == "OONI_PRIMARY"
    assert item["classification"] == "disinformation"


# ── Escalación de audit_status ────────────────────────────────────────────────

def test_two_independent_primaries_escalate_to_secondary():
    items = [
        {"credibility": "high", "verified": False, "sources": ["ojo_publico"]},
        {"credibility": "high", "verified": False, "sources": ["idl_reporteros"]},
    ]
    assert compute_axis_audit_status(items) == AUDIT_SECONDARY


def test_same_source_not_independent_stays_pending():
    items = [
        {"credibility": "high", "verified": False, "sources": ["rss"]},
        {"credibility": "high", "verified": False, "sources": ["rss"]},
    ]
    assert compute_axis_audit_status(items) == AUDIT_PENDING


def test_verified_flag_confirms():
    items = [{"credibility": "medium", "verified": True, "sources": ["ooni"]}]
    assert compute_axis_audit_status(items) == AUDIT_CONFIRMED


def test_three_independent_primaries_confirm():
    items = [
        {"credibility": "high", "verified": False, "sources": ["a"]},
        {"credibility": "high", "verified": False, "sources": ["b"]},
        {"credibility": "high", "verified": False, "sources": ["c"]},
    ]
    assert compute_axis_audit_status(items) == AUDIT_CONFIRMED


def test_medium_credibility_never_escalates():
    items = [{"credibility": "medium", "verified": False, "sources": ["s" + str(i)]}
             for i in range(5)]
    assert compute_axis_audit_status(items) == AUDIT_PENDING


def test_escalation_through_enrich_end_to_end():
    # 2 fuentes primarias independientes en el eje de violencia → VERIFIED_SECONDARY.
    entries = [
        _entry("v1", "security", credibility="high", hunter_source="acled"),
        _entry("v2", "security", credibility="high", hunter_source="defensoria"),
    ]
    obs = enrich_runoff_observation(PERU_RUNOFF_2026, entries)["runoff_phase_observation"]
    assert obs["electoral_violence_incidents"]["audit_status"] == AUDIT_SECONDARY


# ── Ejes institucionales intactos ─────────────────────────────────────────────

def test_institutional_axes_untouched_with_entries_present():
    entries = [_entry("e1", "hate_speech", credibility="high"),
               _entry("e2", "disinformation", credibility="high")]
    obs = enrich_runoff_observation(PERU_RUNOFF_2026, entries)["runoff_phase_observation"]
    # Hunter (OSINT) NO escala ejes institucionales aún vacíos.
    for axis in ("media_access_monitoring",
                 "election_day_logistics_readiness", "vote_count_transparency_protocol",
                 "dispute_resolution_tracker", "campaign_conduct_finalist_a",
                 "campaign_conduct_finalist_b"):
        assert obs[axis]["audit_status"] == AUDIT_PENDING
    # emb_independence_stress_signals está pre-cargado con señales documentadas
    # (crisis ONPE/JNE de 1ª vuelta, con fuentes). El Hunter no lo altera:
    # conserva su baseline VERIFIED_SECONDARY.
    assert obs["emb_independence_stress_signals"]["audit_status"] == AUDIT_SECONDARY
    assert len(obs["emb_independence_stress_signals"]["signals"]) >= 1


# ── Constantes nombradas (anti magic-number drift) ────────────────────────────

def test_named_constants_documented_values():
    assert MIN_INDEPENDENT_PRIMARY == 2
    assert CONFIRM_INDEPENDENT_PRIMARY == 3
    assert PRIMARY_CREDIBILITY == frozenset({"high"})
    assert AUDIT_PENDING == "PENDIENTE_VERIFICACION"
    assert AUDIT_SECONDARY == "VERIFIED_SECONDARY"
    assert AUDIT_CONFIRMED == "CONFIRMED"
