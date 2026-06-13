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


def test_peru_adapter_runoff_observation_returns_full_dict_with_axes():
    """El adapter expone runoff_observation() = dict completo del balotaje
    (finalistas + fechas + runoff_phase_observation con los ejes canónicos)."""
    from agents.elite_report.country_adapters import get_adapter
    runoff = get_adapter("PER").runoff_observation([])
    assert isinstance(runoff, dict)
    assert runoff.get("finalists"), "debe incluir finalistas para el contexto"
    obs = runoff["runoff_phase_observation"]
    for axis in ("hate_speech_and_intimidation_incidents",
                 "osint_information_integrity_monitor",
                 "electoral_violence_incidents",
                 "media_access_monitoring", "dispute_resolution_tracker"):
        assert axis in obs


def test_runoff_chapter_no_pending_language():
    """Requisito: cuando no hay datos NO debe decir 'pendiente de verificar' ni
    mostrar el estado crudo. Los ejes vacíos se resumen en una nota de cobertura
    honesta (monitoreado-sin-incidentes vs sin-evidencia-primaria)."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter

    obs = get_adapter("PER").runoff_observation([])
    chapter = build_runoff_observation_chapter(obs, lang="es")
    assert chapter is not None
    n = chapter.narrative
    # Lenguaje prospectivo ERRADICADO.
    assert "PENDIENTE_VERIFICACION" not in n
    assert "pendiente de verificar" not in n.lower()
    assert "Eje no observado" not in n
    # Nota de cobertura presente, con la distinción honesta de los vacíos.
    assert "Cobertura de monitoreo" in n
    assert "monitoreados sin incidentes documentados" in n
    assert "sin evidencia primaria procesada" in n


def test_runoff_chapter_reflects_hunter_escalation():
    """2 fuentes primarias independientes en violencia → VERIFIED_SECONDARY,
    y el capítulo lo refleja con el conteo de hallazgos."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter

    entries = [
        {"entry_id": "v1", "category": "security", "severity": "high",
         "credibility": "high", "verified": False, "finding": "Ataque a local",
         "hunter_source": "acled", "evidence_ref": "https://acleddata.com/x",
         "timestamp": "2026-06-05T10:00:00+00:00", "location": "Cusco"},
        {"entry_id": "v2", "category": "security", "severity": "high",
         "credibility": "high", "verified": False, "finding": "Amenaza a personero",
         "hunter_source": "defensoria", "evidence_ref": "https://defensoria.gob.pe/y",
         "timestamp": "2026-06-05T11:00:00+00:00", "location": "Puno"},
    ]
    runoff = get_adapter("PER").runoff_observation(entries)
    obs = runoff["runoff_phase_observation"]
    assert obs["electoral_violence_incidents"]["audit_status"] == "VERIFIED_SECONDARY"

    chapter = build_runoff_observation_chapter(runoff, lang="es")
    # Estado mostrado en texto LEGIBLE (no el código crudo).
    assert "hallazgos verificados" in chapter.narrative
    assert "VERIFIED_SECONDARY" not in chapter.narrative
    assert "Hallazgos registrados: 2" in chapter.narrative


def test_runoff_chapter_has_legitimacy_risk_section():
    """Eje central de riesgo: convergencia (margen + no proclamado + EMB +
    STAE) + espejo 2021, anclado en datos cargados, sin especular el desenlace."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter

    runoff = get_adapter("PER").runoff_observation([])
    n = build_runoff_observation_chapter(runoff, lang="es").narrative
    assert "Riesgo de legitimidad del resultado" in n
    assert "alta contestabilidad" in n
    # Factores de convergencia
    assert "Margen mínimo" in n and "no proclamado" in n.lower()
    assert "Órgano electoral cuestionado" in n
    # Espejo 2021 con datos + fuente
    assert "2021" in n and "Pedro Castillo" in n
    assert "44.263" in n or "44263" in n
    assert "es.wikipedia.org" in n
    # Marco normativo
    assert "ICCPR Art. 25" in n and "CADH" in n


def test_runoff_chapter_none_observation_returns_none():
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter
    assert build_runoff_observation_chapter(None, lang="es") is None
    # Un dict sin runoff_phase_observation tampoco produce capítulo.
    assert build_runoff_observation_chapter({"finalists": []}, lang="es") is None


def test_runoff_chapter_is_factual_record_both_rounds():
    """El capítulo es el registro factual de AMBAS vueltas: 1ª (resultados),
    fase entre vueltas (observación) y 2ª (provisional, sin ganador) + STAE."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter

    runoff = get_adapter("PER").runoff_observation([])
    narrative = build_runoff_observation_chapter(runoff, lang="es").narrative

    # 1ª vuelta — resultados
    assert "Primera vuelta" in narrative
    assert "Keiko Fujimori" in narrative and "Roberto Sánchez" in narrative
    assert "17.19" in narrative
    # 2ª vuelta — provisional, SIN ganador proclamado
    assert "Segunda vuelta" in narrative
    assert "provisional" in narrative.lower()
    assert "Sin ganador proclamado" in narrative
    assert "50.004" in narrative                      # % provisional 2ª vuelta (corte 98.3%)
    # STAE — corrección factual (no se afirma buen funcionamiento)
    assert "STAE" in narrative
    assert "sin fallas" not in narrative.lower()
    # Crisis EMB cargada con fuente
    assert "Corvetto" in narrative
    # base legal + nota de cobertura de los ejes vacíos
    assert "ICCPR Art. 25" in narrative
    assert "Cobertura de monitoreo" in narrative
    # Macro-secciones claras
    assert "Resultados electorales" in narrative


# ───────────────────────────────────────────────────────────────────────
# Fixes de visualización (doble título, gauge sin datos, radar EMB, leyendas)
# ───────────────────────────────────────────────────────────────────────

def test_build_stats_populates_by_severity():
    """_build_stats debe exponer by_severity para que el gauge calcule
    crisis_index ≠ 0 (antes faltaba la clave y el gauge salía en 0)."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    bundle = _make_bundle()
    stats = PEIRSEliteReport._build_stats(bundle)
    assert "by_severity" in stats
    bs = stats["by_severity"]
    assert set(bs) >= {"critical", "high", "medium", "low", "info"}
    assert bs["high"] == 9 and bs["critical"] == 1
    # El índice ponderado sería > 0 con estos hallazgos.
    sev_w = {"critical": 1.0, "high": 0.55, "medium": 0.2, "low": 0.05, "info": 0.0}
    total_w = sum(sev_w[s] * c for s, c in bs.items())
    assert total_w > 0


def test_5b_renderers_have_no_embedded_title():
    """Los renderers de Sprint 5b ya NO dibujan su título embebido (el título
    lo pone el <figcaption> del HTML). Evita el doble título reportado."""
    from agents.elite_report.visualizer.renderer import render_svg
    cases = {
        "early_warning_meter": {"level": "amber", "score": 0.3, "label": "x", "drivers": []},
        "flow_chart_voting": {"stages": []},
        "system_architecture": {"_language": "es"},
    }
    headers = ["ALERTA TEMPRANA", "CADENA DEL VOTO", "ARQUITECTURA DEL SISTEMA"]
    for kind, data in cases.items():
        svg = render_svg(kind, data)
        for h in headers:
            assert h not in svg, f"{kind} aún dibuja título embebido {h!r}"


def test_radar_emb_reflects_organ_questioning():
    """Un hallazgo que cuestiona al EMB (menciona ONPE) aunque esté clasificado
    como 'legal' debe bajar la dimensión 'Org. electoral' del radar — antes
    quedaba en 100 porque solo miraba logistics/fraud/counting."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.composer.chapter_composer import CHAPTER_CATALOG
    from agents.elite_report.models import EliteChapter

    bundle = _make_bundle()
    bundle.hunter_entries.append(_make_finding_ref(
        "emb1", "Cuestionamiento a la imparcialidad de la ONPE", "legal", "critical"))
    chapters = [EliteChapter(number=m["number"], chapter_id=m["chapter_id"],
                             title=m["title"], narrative="x")
                for m in CHAPTER_CATALOG]
    stats = {"total": 36, "critical": 2, "high": 9, "medium": 14,
             "by_severity": {"critical": 2, "high": 9, "medium": 14, "low": 0, "info": 0},
             "days_covered": 30}
    PEIRSEliteReport._attach_visualizations(chapters, bundle, _make_forecast(), stats)

    radar = None
    for ch in chapters:
        for viz in ch.visualizations:
            if viz.kind == "dimensions_radar":
                radar = viz
    assert radar is not None
    emb_dim = next(d for d in radar.data["dimensions"]
                   if "electoral" in d["label"].lower())
    assert emb_dim["value"] < 100, "el cuestionamiento al EMB debe reflejarse"


def test_gauge_level_coherent_with_score():
    """La banda (level) del medidor debe ser coherente con el score que posiciona
    la aguja — antes el forecast podía mostrar 'green' con score 0.78 (rojo)."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.composer.chapter_composer import CHAPTER_CATALOG
    from agents.elite_report.models import EliteChapter

    bundle = _make_bundle()  # 1 critical + varios high
    chapters = [EliteChapter(number=m["number"], chapter_id=m["chapter_id"],
                             title=m["title"], narrative="x")
                for m in CHAPTER_CATALOG]
    stats = PEIRSEliteReport._build_stats(bundle)
    # forecast dice green, pero el gauge debe ignorarlo y usar el score.
    forecast = _make_forecast()
    forecast.early_warning_level = "green"
    PEIRSEliteReport._attach_visualizations(chapters, bundle, forecast, stats)

    gauge = None
    for ch in chapters:
        for v in ch.visualizations:
            if v.kind == "early_warning_meter":
                gauge = v
    assert gauge is not None
    score, level = gauge.data["score"], gauge.data["level"]
    bands = [(0.60, "red"), (0.40, "orange"), (0.20, "amber"), (0.0, "green")]
    expected = next(lvl for thr, lvl in bands if score >= thr)
    assert level == expected, f"score={score} ⇒ {expected}, pero level={level}"


def test_viz_captions_resolve_with_scale_direction():
    """Las leyendas clave existen y explican la dirección de la escala."""
    from agents.elite_report.i18n import t
    radar = t("es", "viz.dimensions_radar.caption", "")
    assert "100" in radar and "0" in radar  # explica los extremos
    assert t("es", "viz.scenario_probability.caption", "") != ""
    gauge = t("es", "viz.early_warning_meter.caption", "")
    assert "rojo" in gauge.lower() or "riesgo" in gauge.lower()


def test_compose_includes_runoff_chapter_without_llm():
    """E2E sin LLM ni red: compose() debe generar el informe e incluir el
    capítulo determinista de observación entre vueltas en chapters + render."""
    import asyncio
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.models import EliteReportRequest, MissionMetadata

    report = PEIRSEliteReport(llm=None, observation_store={"PER": {"entries": []}})
    req = EliteReportRequest(
        country_code="PER",
        language="es",
        include_predictive=False,
        output_formats=["md", "html"],
        mission_metadata=MissionMetadata(
            report_number="TEST-RUNOFF-001",
            period_start="2026-06-04",
            period_end="2026-06-10",
            jornada_date="2026-06-07",
        ),
    )
    output = asyncio.run(report.compose(req))

    assert output.status == "done"
    ids = [c.chapter_id for c in output.chapters]
    assert "observacion_entre_vueltas" in ids, ids
    # Reposicionado: va inmediatamente después de "Jornada electoral".
    assert ids.index("observacion_entre_vueltas") == ids.index("jornada_electoral") + 1
    # Renumeración contigua de capítulos positivos (sin saltos ni duplicados).
    nums = [c.number for c in output.chapters if c.number > 0]
    assert nums == list(range(1, len(nums) + 1)), nums
    # Análisis probabilístico ELIMINADO: no hay capítulo predictivo ni forecast.
    assert "analisis_predictivo" not in ids
    assert output.forecast is None
    # Ninguna viz de proyección/escenarios se emite.
    kinds = [v.kind for c in output.chapters for v in c.visualizations]
    assert "forecast_chart" not in kinds and "scenario_probability" not in kinds
    # El medidor de alerta temprana se conserva, reubicado en Conclusiones.
    concl = next(c for c in output.chapters if c.chapter_id == "conclusiones")
    assert "early_warning_meter" in [v.kind for v in concl.visualizations]
    # Sin lenguaje "pendiente"; en su lugar, nota de cobertura honesta.
    html = output.html or ""
    assert "PENDIENTE_VERIFICACION" not in html
    assert "Cobertura de monitoreo" in html
    # Resultados de ambas vueltas (fuente factual única) + crisis EMB.
    assert "Keiko Fujimori" in html and "Sin ganador proclamado" in html
    assert "Corvetto" in html
    # Apéndice C con trazabilidad (tabla de hallazgos) presente en estructura.
    assert 'id="appendix-c"' in html


def test_consolidate_merges_same_event_sources():
    """Bloque 1: dos capturas del mismo evento (misma fecha, texto similar) se
    funden en UN hallazgo con AMBAS fuentes; eventos distintos no se mezclan."""
    from agents.elite_report.consolidators import consolidate_findingrefs, consolidate_items
    from agents.elite_report.models import FindingRef

    refs = [
        FindingRef(finding="La Fiscalía pidió diez años de prisión para el subgerente de ONPE",
                   category="legal", severity="high", source_name="ElComercio",
                   source_url="https://ec.pe/1", recorded_at="2026-04-15"),
        FindingRef(finding="Fiscalía solicitó diez años de prisión contra subgerente de la ONPE",
                   category="legal", severity="high", source_name="Gestion",
                   source_url="https://gestion.pe/2", recorded_at="2026-04-15"),
        FindingRef(finding="Ataque a local de votación en Cusco con heridos",
                   category="security", severity="critical", source_name="ACLED",
                   source_url="https://acled.com/3", recorded_at="2026-06-07"),
    ]
    out = consolidate_findingrefs(refs)
    assert len(out) == 2, "los 2 hallazgos del mismo evento deben fundirse en 1"
    fiscalia = next(f for f in out if "Fiscal" in f.finding)
    urls = {s["url"] for s in fiscalia.sources}
    assert urls == {"https://ec.pe/1", "https://gestion.pe/2"}

    # consolidate_items preserva `sources` (audit) y agrega `source_links`.
    items = [
        {"content_summary": "Amenaza a personero electoral en Puno", "date": "2026-06-05",
         "severity": "high", "sources": ["acled"], "source_url": "https://a/1"},
        {"content_summary": "Amenaza contra personero electoral en Puno", "date": "2026-06-05",
         "severity": "high", "sources": ["defensoria"], "source_url": "https://b/2"},
    ]
    ci = consolidate_items(items)
    assert len(ci) == 1
    assert set(ci[0]["sources"]) == {"acled", "defensoria"}        # audit intacto
    assert len(ci[0]["source_links"]) == 2                          # render: 2 enlaces


def test_timelines_chronological_with_round_and_dedup():
    """Bloque 2: las cronologías quedan deduplicadas y ordenadas por fecha
    (1ª → 2ª vuelta), con etiqueta de vuelta."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.composer.chapter_composer import CHAPTER_CATALOG
    from agents.elite_report.models import EliteChapter, FindingRef

    bundle = _make_bundle()
    # Inyectar findings judiciales: 1ª vuelta (abr) y 2ª vuelta (jun), con dup.
    bundle.hunter_entries.extend([
        FindingRef(finding="JNE denuncia penalmente al jefe de ONPE", category="legal",
                   severity="high", source_name="EC", source_url="https://e/jun",
                   recorded_at="2026-06-08"),
        FindingRef(finding="JNE denunció penalmente al jefe de la ONPE", category="legal",
                   severity="high", source_name="RPP", source_url="https://r/jun",
                   recorded_at="2026-06-08"),
        FindingRef(finding="Allanamiento a oficinas de ONPE por fallas logísticas",
                   category="judicial", severity="critical", source_name="EC",
                   source_url="https://e/abr", recorded_at="2026-04-14"),
    ])
    chapters = [EliteChapter(number=m["number"], chapter_id=m["chapter_id"],
                             title=m["title"], narrative="x") for m in CHAPTER_CATALOG]
    stats = PEIRSEliteReport._build_stats(bundle)
    PEIRSEliteReport._attach_visualizations(chapters, bundle, None, stats)
    jud = None
    for ch in chapters:
        for v in ch.visualizations:
            if v.kind == "judicial_timeline":
                jud = v
    assert jud is not None
    actions = jud.data["actions"]
    dates = [a["date"] for a in actions]
    assert dates == sorted(dates), "la cronología debe ir en orden ascendente"
    # Dedup: el evento JNE/ONPE de jun aparece una sola vez.
    jne = [a for a in actions if "ONPE" in a["action"] and a["date"] == "2026-06-08"]
    assert len(jne) == 1
    # Etiqueta de vuelta presente y correcta.
    assert any(a["round"] == "1ª vuelta" for a in actions)
    assert any(a["round"] == "2ª vuelta" for a in actions)


def test_appendix_c_renders_traceable_findings_table():
    """El Apéndice C debe renderizar una TABLA real de hallazgos con
    trazabilidad (fecha, severidad, categoría, hallazgo, fuente con URL),
    no un placeholder. Atrapa el bug del placeholder vacío."""
    from agents.elite_report.renderer.html_renderer import _render_appendix_c
    from agents.elite_report.models import FindingRef

    findings = [
        FindingRef(entry_id="f1", finding="Ataque a local de votación en Cusco",
                   category="security", severity="critical",
                   source_name="ACLED", source_url="https://acleddata.com/x",
                   recorded_at="2026-06-07T10:00:00+00:00"),
        FindingRef(entry_id="f2", finding="Narrativa de fraude en redes",
                   category="disinformation", severity="high",
                   source_name="DFRLab", source_url="https://dfrlab.org/y",
                   recorded_at="2026-06-08T09:00:00+00:00"),
    ]
    # Un finding con MÚLTIPLES fuentes consolidadas (un hecho = N fuentes).
    findings[0].sources = [
        {"url": "https://acleddata.com/x", "name": "ACLED"},
        {"url": "https://rpp.pe/z", "name": "RPP"},
    ]
    html = _render_appendix_c(findings, language="es")
    assert "findings-table" in html               # tabla real, no placeholder
    assert "Ataque a local de votación" in html   # el hallazgo
    assert "https://acleddata.com/x" in html       # trazabilidad: URL primaria
    assert "https://rpp.pe/z" in html              # 2ª fuente del MISMO evento
    assert "https://dfrlab.org/y" in html          # fallback a source_url (1 fuente)
    assert "2026-06-07" in html                    # fecha
    assert "2 eventos" in html                     # eventos consolidados
    # Estado vacío honesto (sin findings) NO usa lenguaje de placeholder viejo.
    empty = _render_appendix_c([], language="es")
    assert "descargable" not in empty.lower() or "No se registraron" in empty
