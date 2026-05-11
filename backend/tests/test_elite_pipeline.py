"""Tests integrados del pipeline Elite Report.

Foco: atrapar los bugs reales que llegaron a producción durante 28-abr/4-may
2026. Cada test corresponde a una clase de error que efectivamente tuvimos:

  test_vizkind_covers_dispatcher_kinds
    - bug "parliament_scenarios no en VizKind Literal" (4-may, c2fd554)

  test_findingref_has_required_attrs
    - bug "FindingRef object has no attribute timestamp/location/source_org"
      (4-may, c2fd554)

  test_predictive_engine_no_setattr_on_list
    - bug "list object has no attribute append_pattern" (4-may, f0f1bdd)

  test_attach_visualizations_runs_with_real_bundle
    - smoke E2E del Visualizer con bundle real-shape, sin LLM

  test_all_wired_kinds_render_valid_svg
    - cada kind cableado por _attach_visualizations produce SVG valido

  test_predictive_engine_returns_correct_shape
    - sin LLM, _evaluate_rules + el ensamblado producen ForecastPayload OK

Sin red, sin LLM real. Corre en CI con `pytest backend/tests/test_elite_pipeline.py`.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import get_args
from unittest import mock

import pytest

# Asegurar backend/ en path (igual que conftest.py)
_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


# ───────────────────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────────────────

def _make_finding_ref(
    entry_id: str = "f1",
    finding: str = "Hallazgo de prueba",
    category: str = "logistics",
    severity: str = "high",
):
    """Construye FindingRef con todos los atributos que el pipeline puede leer."""
    from agents.elite_report.models import FindingRef
    return FindingRef(
        entry_id=entry_id,
        finding=finding,
        category=category,
        severity=severity,
        source_name="El Comercio",
        source_url="https://elcomercio.pe/test",
        recorded_at="2026-04-12T09:30:00",
        themes=["jornada"],
        priority_score=0.8,
        phase="election_day",
        location="Lima",
    )


def _make_bundle():
    """EvidenceBundle real-shape con findings, phase_evidence, cross_refs y series."""
    from agents.elite_report.models import (
        EvidenceBundle, PhaseEvidence, CrossReference,
        HistoricalSeries, HistoricalDatapoint,
    )

    findings = [
        _make_finding_ref("f1", "Cajas sin fiscalizador", "ballot_tampering", "critical"),
        _make_finding_ref("f2", "JNE inviabilidad complementarias", "legal", "high"),
        _make_finding_ref("f3", "Allanamiento ONPE", "fraud_allegation", "high"),
        _make_finding_ref("f4", "Cobertura Andina", "logistics", "info"),
        _make_finding_ref("f5", "Disinformacion sobre padron", "disinformation", "medium"),
    ]

    phase_evidence = {
        "campaign": PhaseEvidence(
            phase_id="campaign", phase_label="Campaña electoral",
            findings=findings[:2], total_count=20,
            critical_count=1, high_count=5, medium_count=8,
        ),
        "counting_tabulation": PhaseEvidence(
            phase_id="counting_tabulation", phase_label="Escrutinio y cómputo",
            findings=findings[2:], total_count=15,
            critical_count=0, high_count=4, medium_count=6,
        ),
    }

    cross_refs = [
        CrossReference(
            finding_entry_id="f1",
            finding_snippet="Cajas sin fiscalizador",
            normative_instrument="ICCPR Art. 25",
            article_number="25",
            severity="critical",
            reasoning="Vulneracion del nucleo del sufragio autentico",
        ),
    ]

    historical_series = [
        HistoricalSeries(
            indicator="vdem_libdem",
            indicator_label="Liberal Democracy Index (V-Dem)",
            source="V-Dem Institute",
            source_citation="V-Dem Institute. (2026). v16.",
            unit="0.0–1.0",
            datapoints=[
                HistoricalDatapoint(year=2020, value=0.55, source="V-Dem v16"),
                HistoricalDatapoint(year=2025, value=0.48, source="V-Dem v16"),
            ],
            trend_direction="down",
            trend_note="Caida sostenida 2020-2025",
        ),
    ]

    return EvidenceBundle(
        country_code="PER",
        period_start="2026-03-30",
        period_end="2026-04-28",
        loaded_at=datetime.now(timezone.utc).isoformat(),
        hunter_entries=findings,
        hunter_stats={"total": 35, "critical": 1, "high": 9, "medium": 14},
        alerts_dispatched=2,
        phase_evidence=phase_evidence,
        rag_documents=[],
        historical_series=historical_series,
        cross_references=cross_refs,
        warnings=[],
    )


def _make_forecast():
    """ForecastPayload mock para tests del Visualizer."""
    from agents.elite_report.models import ForecastPayload, ForecastScenario
    return ForecastPayload(
        horizon_days=14,
        generated_at=datetime.now(timezone.utc).isoformat(),
        scenarios=[
            ForecastScenario(
                scenario_id="A",
                label="Disputa prolongada",
                probability=0.65,
                confidence_interval=(0.55, 0.75),
                indicators=["Bloomberg caos electoral", "Renuncia ONPE"],
                implications="Crisis institucional probable",
            ),
            ForecastScenario(
                scenario_id="B",
                label="Proclamacion sin disputa",
                probability=0.25,
                confidence_interval=(0.15, 0.35),
                indicators=["Escrutinio al 95%"],
                implications="Camino institucional ordenado",
            ),
        ],
        dominant_pattern="Crisis institucional aguda",
        early_warning_level="orange",
        early_warning_note="Riesgo elevado por convergencia de fallas",
    )


# ───────────────────────────────────────────────────────────────────────
# Tests
# ───────────────────────────────────────────────────────────────────────

def test_vizkind_covers_dispatcher_kinds():
    """Cada kind cableado en _ELITE_MAP debe estar declarado en VizKind Literal.
    Atrapa el bug del 4-may donde parliament_scenarios estaba en el dispatcher
    pero no en el Literal — ValidationError al construir VizSpec."""
    from agents.elite_report.models import VizKind, VizSpec
    from agents.elite_report.visualizer.renderer import _ELITE_MAP, _LEGACY_KINDS

    allowed = set(get_args(VizKind))
    dispatcher = set(_ELITE_MAP.keys()) | _LEGACY_KINDS
    missing = dispatcher - allowed
    assert not missing, (
        f"Kinds en dispatcher pero NO declarados en VizKind Literal: {sorted(missing)}. "
        f"Construir VizSpec(kind=...) tiraría ValidationError."
    )

    # Smoke: construir VizSpec para cada kind del dispatcher pasa Pydantic
    for kind in sorted(dispatcher):
        VizSpec(kind=kind, title="t", caption="c", data={})


def test_findingref_has_required_attrs():
    """FindingRef debe tener los atributos que _attach_visualizations lee.
    Atrapa los bugs donde se asumia .timestamp / .source_org / .location y no
    existian, generando AttributeError en runtime."""
    fr = _make_finding_ref()
    # Atributos que el pipeline lee (chequeados explicitamente)
    for attr in [
        "entry_id", "finding", "category", "severity",
        "source_name", "source_url",
        "recorded_at",   # NO timestamp
        "phase", "themes", "priority_score",
        "location",      # agregado el 4-may
    ]:
        assert hasattr(fr, attr), f"FindingRef sin atributo {attr!r}"


def test_predictive_engine_no_setattr_on_list():
    """PredictiveEngine no debe intentar monkey-patch atributos sobre la lista
    de scenarios. Atrapa el bug append_pattern (4-may, f0f1bdd)."""
    from agents.elite_report.predictive.engine import PredictiveEngine

    engine = PredictiveEngine(llm=None, country_code="PER")
    bundle = _make_bundle()
    candidates = engine._evaluate_rules(bundle)

    # Verificacion explicita: candidates es una list, NO debe tener
    # append_pattern/append_warning como atributos.
    assert isinstance(candidates, list)
    for forbidden in ["append_pattern", "append_warning", "append_warning_note"]:
        assert not hasattr(candidates, forbidden), (
            f"List of scenarios tiene atributo {forbidden!r} — "
            f"signo de monkey-patch ilegal."
        )


def test_predictive_engine_returns_correct_payload_shape():
    """Sin LLM, el engine debe ensamblar un ForecastPayload valido con
    dominant_pattern y early_warning_level provenientes de heuristica."""
    import asyncio
    from agents.elite_report.predictive.engine import PredictiveEngine

    engine = PredictiveEngine(llm=None, country_code="PER")
    bundle = _make_bundle()
    payload = asyncio.run(engine.forecast(bundle, horizon_days=14))

    assert payload.horizon_days == 14
    assert isinstance(payload.scenarios, list)
    assert payload.early_warning_level in ("green", "amber", "orange", "red")
    assert payload.dominant_pattern, "dominant_pattern no debe estar vacio"


def test_attach_visualizations_runs_with_real_bundle():
    """Smoke: _attach_visualizations no debe lanzar AttributeError ni Validation
    error con un bundle real-shape. Esto cubre el regression de los 3 bugs del
    4-may (timestamp/location/source_org/append_pattern)."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.composer.chapter_composer import CHAPTER_CATALOG
    from agents.elite_report.models import EliteChapter

    bundle = _make_bundle()
    forecast = _make_forecast()
    stats = {
        "total": 35, "critical": 1, "high": 9, "medium": 14,
        "by_severity": {"critical": 1, "high": 9, "medium": 14},
        "days_covered": 30,
    }

    chapters = [
        EliteChapter(
            number=meta["number"],
            chapter_id=meta["chapter_id"],
            title=meta["title"],
            narrative="placeholder",
        )
        for meta in CHAPTER_CATALOG
    ]

    # No debe lanzar
    PEIRSEliteReport._attach_visualizations(chapters, bundle, forecast, stats)

    # Verificaciones: al menos un capítulo recibió viz
    total_viz = sum(len(ch.visualizations) for ch in chapters)
    assert total_viz > 0, "Ningun capitulo recibio visualizaciones"

    # Cada VizSpec construido es valido (kind en VizKind Literal)
    for ch in chapters:
        for viz in ch.visualizations:
            assert viz.kind, f"VizSpec sin kind en cap {ch.chapter_id}"


def test_all_wired_kinds_render_valid_svg():
    """Para cada kind que el pipeline efectivamente cabling, render_svg debe
    devolver un SVG valido (no placeholder, no exception)."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.composer.chapter_composer import CHAPTER_CATALOG
    from agents.elite_report.models import EliteChapter
    from agents.elite_report.visualizer.renderer import render_svg

    bundle = _make_bundle()
    forecast = _make_forecast()
    stats = {
        "total": 35, "critical": 1, "high": 9, "medium": 14,
        "by_severity": {"critical": 1, "high": 9, "medium": 14},
        "days_covered": 30,
    }
    chapters = [
        EliteChapter(number=m["number"], chapter_id=m["chapter_id"],
                     title=m["title"], narrative="x")
        for m in CHAPTER_CATALOG
    ]
    PEIRSEliteReport._attach_visualizations(chapters, bundle, forecast, stats)

    fails = []
    for ch in chapters:
        for viz in ch.visualizations:
            try:
                svg = render_svg(viz.kind, viz.data)
                if not svg.startswith("<svg") or "</svg>" not in svg:
                    fails.append(f"{ch.chapter_id}/{viz.kind}: SVG malformado")
                # Que no sea el placeholder de "kind no implementado"
                if "implementación en Sprint 5b" in svg:
                    fails.append(f"{ch.chapter_id}/{viz.kind}: cae a placeholder")
            except Exception as e:
                fails.append(f"{ch.chapter_id}/{viz.kind}: {type(e).__name__}: {e}")

    assert not fails, "Renders fallidos:\n  " + "\n  ".join(fails)


def test_chapter_composer_compose_chapter_handles_no_llm():
    """Cuando llm=None (caso degradado), _compose_chapter debe retornar
    EliteChapter con narrative='' y warning explicito en lugar de crashear."""
    import asyncio
    from agents.elite_report.composer.chapter_composer import (
        ChapterComposer, CHAPTER_CATALOG,
    )
    from agents.elite_report.models import EliteReportRequest, MissionMetadata

    composer = ChapterComposer(llm=None)
    req = EliteReportRequest(
        country_code="PER",
        mission_metadata=MissionMetadata(
            report_number="TEST-001",
            period_start="2026-04-01",
            period_end="2026-04-30",
            jornada_date="2026-04-12",
        ),
    )

    meta = next(m for m in CHAPTER_CATALOG if m["chapter_id"] == "contexto_historico")
    chapter = asyncio.run(composer._compose_chapter(meta, "contexto", req))

    assert chapter.chapter_id == "contexto_historico"
    assert chapter.narrative == ""
    assert any("LLM" in w for w in chapter.warnings)


def test_format_vdem_emb_returns_quantitative_block():
    """El helper _format_vdem_emb debe devolver string con valores numericos
    de los 6 indicadores del EMB para PER 2025 (post b21edf2 + a47e3f7)."""
    from agents.elite_report.composer.chapter_composer import ChapterComposer
    out = ChapterComposer._format_vdem_emb("PER", last_n=5)
    # Smoke: presencia de los 6 indicadores
    for code in ["v2elembaut", "v2elembcap", "v2elirreg",
                 "v2elintim", "v2xcl_rol", "v2jureview"]:
        assert code in out, f"Indicador {code} ausente en _format_vdem_emb output"
    # Smoke: tendencia con 5 años
    assert "Tendencia" in out, "Bloque de tendencia ausente"


def test_disclosure_present_in_cover_render():
    """El render del cover debe incluir el disclosure literal de no-legitimacion."""
    from agents.elite_report.renderer.html_renderer import _render_cover
    from agents.elite_report.models import EliteReportRequest, MissionMetadata

    req = EliteReportRequest(
        country_code="PER",
        mission_metadata=MissionMetadata(
            report_number="TEST-001",
            period_start="2026-04-01",
            period_end="2026-04-30",
            jornada_date="2026-04-12",
        ),
    )
    stats = {"total": 100, "critical": 5, "high": 20, "days_covered": 30}
    cover = _render_cover(req, stats, "Perú", "2026-05-04T00:00:00", "test-id")

    assert "no legitima ni valida" in cover, "Disclosure ausente del cover"
    assert "estándares internacionales de observación electoral" in cover, (
        "Disclosure no usa la frase neutra (debe ser 'estándares internacionales "
        "de observación electoral', sin nombrar organismos especificos)."
    )
    # NO debe nombrar organismos especificos en el cover (politica 4-may)
    for org in ["Comisión de Venecia", "OEA/DECO", "OSCE/ODIHR", "Carter Center"]:
        assert org not in cover, f"Cover nombra organismo {org!r} (no permitido)"


def test_peru_adapter_institutional_model():
    """Sprint 3 — PeruAdapter implementa institutional_model() con la
    topologia unitaria peruana correcta (JNE arbiter + ONPE/RENIEC/JEE
    subnacionales + 4 layers normativas + tabulacion centralizada)."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.country_adapters.base import (
        EMBBody, InstitutionalModel, LegalLayer
    )

    adapter = get_adapter("PER")
    model = adapter.institutional_model()

    assert isinstance(model, InstitutionalModel)
    assert model.system_type == "unitary"
    assert isinstance(model.national_emb, EMBBody)
    assert model.national_emb.name == "JNE"
    assert model.national_emb.role == "arbiter"
    assert model.transmission_chain_type == "centralized"

    # Verificar bodies subnacionales/auxiliares (ONPE, RENIEC, JEE)
    sub_names = {b.name for b in model.subnational_embs}
    assert {"ONPE", "RENIEC", "JEE"}.issubset(sub_names)

    # 4 capas normativas presentes
    layer_names = {layer.layer for layer in model.legal_layers}
    assert layer_names == {"constitutional", "federal", "subnational", "international"}

    # Constitucion presente en la layer constitucional
    constitutional_layer = next(
        layer for layer in model.legal_layers if layer.layer == "constitutional"
    )
    assert any("Constitución" in inst for inst in constitutional_layer.instruments), (
        "Constitución Política del Perú debe estar en la layer constitutional"
    )
