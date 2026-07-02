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


def test_milestones_and_emb_event_grouping():
    """Bloque 4: hitos del ciclo (1ª→2ª→escrutinio). Bloque 3: las 6 señales
    del EMB se agrupan bajo el evento 'Crisis institucional de la ONPE'."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter

    runoff = get_adapter("PER").runoff_observation([])
    n = build_runoff_observation_chapter(runoff, lang="es").narrative
    # Bloque 4 — hitos cronológicos
    assert "Hitos del ciclo electoral 2026" in n
    assert "Primera vuelta" in n and "Keiko Fujimori" in n
    assert "Segunda vuelta" in n
    assert "Escrutinio finalizado" in n and "49.641" in n
    # Bloque 3 — evento EMB agrupador + sus señales debajo
    assert "Crisis institucional de la ONPE" in n
    assert "Corvetto" in n          # las 6 señales siguen presentes, agrupadas
    # El evento aparece antes que las viñetas de señales
    assert n.index("Crisis institucional de la ONPE") < n.index("Corvetto")


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
    fase entre vueltas (observación) y 2ª (cómputo final al 100% el 29-jun, SIN
    proclamación — la del JNE es el 15-jul) + STAE."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter

    runoff = get_adapter("PER").runoff_observation([])
    narrative = build_runoff_observation_chapter(runoff, lang="es").narrative

    # 1ª vuelta — resultados
    assert "Primera vuelta" in narrative
    assert "Keiko Fujimori" in narrative and "Roberto Sánchez" in narrative
    assert "17.19" in narrative
    # 2ª vuelta — cómputo FINAL al 100%, SIN ganador proclamado (proclamación 15-jul)
    assert "Segunda vuelta" in narrative
    assert "Sin ganador proclamado" in narrative
    assert "50.135" in narrative                      # % final 2ª vuelta (cómputo 100%)
    assert "49.641" in narrative                      # margen final
    assert "2026-06-29" in narrative                  # fecha de finalización del escrutinio
    assert "2026-07-15" in narrative                  # proclamación oficial del JNE pendiente
    assert "Implicancia de la demora" in narrative    # comentario sobre la demora
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


def test_build_stats_populates_by_round_and_category():
    """Bloque Q: _build_stats debe exponer by_round (split 1ª/2ª por umbral
    2026-05-01), by_category (nube temática) y consolidated_total — y el split
    por vuelta DEBE sumar el universo consolidado (coherencia con Anexo C)."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    bundle = _make_bundle()  # todos los findings son 2026-04-12 → 1ª vuelta
    bundle.hunter_entries.append(_make_finding_ref(
        "rv1", "Allanamiento ONPE en balotaje", "fraud_allegation", "high"))
    bundle.hunter_entries[-1].recorded_at = "2026-06-02T10:00:00"  # 2ª vuelta
    stats = PEIRSEliteReport._build_stats(bundle)

    assert "by_round" in stats and "by_category" in stats
    assert "consolidated_total" in stats
    r1 = stats["by_round"]["1ª vuelta"]
    r2 = stats["by_round"]["2ª vuelta"]
    assert r2["total"] >= 1  # el finding de junio cae en 2ª vuelta
    # Coherencia: split por vuelta = universo consolidado
    assert r1["total"] + r2["total"] == stats["consolidated_total"]
    # by_category ordenado desc por count, con severity_max
    cats = stats["by_category"]
    assert cats and all({"category", "count", "severity_max"} <= set(c) for c in cats)
    counts = [c["count"] for c in cats]
    assert counts == sorted(counts, reverse=True)


def test_quant_panel_renders_with_methodological_captions():
    """Bloque Q: el panorama cuantitativo debe renderizar ambos viz (cuadro por
    vuelta + nube temática) con SVG válido y captions metodológicas no vacías."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.renderer.html_renderer import _render_quant_panel
    import re
    bundle = _make_bundle()
    stats = PEIRSEliteReport._build_stats(bundle)
    panel = _render_quant_panel(stats, "es")
    assert 'id="panorama-cuantitativo"' in panel
    assert panel.count("<svg") >= 2  # cuadro + nube
    caps = re.findall(r'viz-caption">([^<]+)<', panel)
    assert len(caps) >= 2 and all(c.strip() for c in caps)
    # La metodología cita el umbral de vuelta y la consolidación
    assert "consolidado" in panel.lower()


def test_adapter_exposes_vdem_emb_series():
    """P2 (framework agnóstico): la apertura ya no importa peru_data ni gatea
    en ==PER; toma la serie V-Dem del EMB vía adapter.vdem_emb_series()."""
    from agents.elite_report.country_adapters import get_adapter
    adapter = get_adapter("PER")
    assert hasattr(adapter, "vdem_emb_series")
    series = adapter.vdem_emb_series()
    assert series and isinstance(series, list)
    assert all("year" in p and "v2elembaut" in p for p in series)
    # elite_report ya no debe gatear la apertura en el literal "PER"
    import inspect
    from agents.elite_report import elite_report as er
    src = inspect.getsource(er.PEIRSEliteReport.compose)
    assert 'vdem_emb_series' in src
    assert '== "PER"' not in src


def test_hunter_gold_set_accuracy_is_recomputable():
    """P2: ACCURACY_METRICS debe coincidir con recomputar desde GOLD_SET
    (no son magic numbers) y exponer precision/recall/f1 por categoría."""
    from agents.hunter_version import (
        GOLD_SET, ACCURACY_METRICS, compute_accuracy, fingerprint)
    assert ACCURACY_METRICS == compute_accuracy(GOLD_SET)
    assert 0.0 <= ACCURACY_METRICS["category_accuracy"] <= 1.0
    assert 0.0 <= ACCURACY_METRICS["severity_accuracy"] <= 1.0
    # cada categoría del gold tiene precision/recall/f1/support
    for c, m in ACCURACY_METRICS["per_category"].items():
        assert {"precision", "recall", "f1", "support"} <= set(m)
    fp = fingerprint()
    assert fp["gold_set_size"] == len(GOLD_SET)
    assert fp["category_accuracy"] == ACCURACY_METRICS["category_accuracy"]


def test_actor_bias_report_detects_and_flags():
    """P2: el reporte de sesgo agrupa por tipo de actor, calcula severidad media
    y marca (flagged) las desviaciones marcadas respecto a la media global."""
    from agents.hunter_version import actor_bias_report

    class _E:
        def __init__(self, sev, src, fnd):
            self.severity, self.source_name, self.finding = sev, src, fnd

    # Institución estatal sistemáticamente crítica; medios siempre info → sesgo.
    entries = (
        [_E("critical", "ONPE", "x") for _ in range(4)]
        + [_E("info", "El Comercio diario", "y") for _ in range(4)]
    )
    rep = actor_bias_report(entries)
    assert rep["total_classified"] == 8
    by = rep["by_actor"]
    assert "state_institution" in by and "media" in by
    assert by["state_institution"]["mean_severity"] == 5.0
    assert by["media"]["mean_severity"] == 1.0
    # con esta separación extrema, ambos deben quedar flagged
    assert by["state_institution"]["flagged"] and by["media"]["flagged"]


def test_appendix_a_stamps_classifier_quality_and_bias():
    """P2: el bloque de versión del Anexo A debe estampar calidad del
    clasificador (gold set) y la tabla de sesgo por actor."""
    from agents.elite_report.renderer.html_renderer import _render_version_block
    from agents.hunter_version import fingerprint, actor_bias_report

    class _E:
        def __init__(self, sev, src, fnd):
            self.severity, self.source_name, self.finding = sev, src, fnd

    audit = {
        "pipeline_version": "1.0.0", "config_version": "1.0.0", "config_hash": "h",
        "classifier": {"model": "m", "prompt_sha256_16": "p"},
        "config": {"llm": {"model": "m", "temperature": 0.2},
                   "escalation": {"min_independent_primary": 2,
                                  "confirm_independent_primary": 3},
                   "consolidation": {"jaccard_threshold": 0.5}},
        "classifier_quality": fingerprint(),
        "actor_bias": actor_bias_report([_E("high", "JNE", "x")]),
    }
    html = _render_version_block(audit, "es")
    assert "Calidad del clasificador" in html
    assert "Auditoría de sesgo" in html


def test_round_threshold_reconciles_first_round():
    """El umbral de vuelta debe ser 2026-05-03: hallazgos hasta el cierre del
    cómputo de 1ª vuelta (2-may) quedan en 1ª; desde el 3-may, en 2ª. Esto
    reconcilia con el informe preliminar de 1ª vuelta (1923 capturas a 2-may)."""
    from agents.elite_report.elite_report import PEIRSEliteReport
    assert PEIRSEliteReport._ROUND_THRESHOLD == "2026-05-03"
    assert PEIRSEliteReport._round_label("2026-05-02T23:59:00") == "1ª vuelta"
    assert PEIRSEliteReport._round_label("2026-05-03T00:01:00") == "2ª vuelta"
    assert PEIRSEliteReport._round_label("2026-04-12T10:00:00") == "1ª vuelta"
    assert PEIRSEliteReport._round_label("2026-06-07T10:00:00") == "2ª vuelta"


def test_evidence_base_persist_is_append_only_idempotent():
    """La base de prueba persiste cada captura una sola vez (UNIQUE entry_id):
    re-ingerir la misma sesión NO duplica filas. Garantía anti-pérdida."""
    import sqlite3
    from modules import evidence_base as eb
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE evidence_entries (entry_id TEXT PRIMARY KEY,
        country_code TEXT NOT NULL, session_id TEXT, round TEXT, category TEXT,
        severity TEXT, finding TEXT, location TEXT, recorded_at TEXT, source_url TEXT,
        source_name TEXT, source_title TEXT, phase TEXT, ingested_at TEXT NOT NULL,
        raw_json TEXT NOT NULL)""")
    caps = [
        {"entry_id": "a1", "category": "disinformation", "severity": "high",
         "finding": "x", "recorded_at": "2026-04-12T10:00:00", "evidence_ref": "http://e/1"},
        {"entry_id": "a2", "category": "fraud_allegation", "severity": "critical",
         "finding": "y", "recorded_at": "2026-06-02T10:00:00", "evidence_ref": "http://e/2"},
    ]
    assert eb.persist_captures(conn, "PER", "s1", caps) == 2
    assert eb.persist_captures(conn, "PER", "s1", caps) == 0  # idempotente
    c = eb.count(conn, "PER")
    assert c["total"] == 2 and c["1ª vuelta"] == 1 and c["2ª vuelta"] == 1


def test_theme_breakdown_reconciles_to_consolidated_total():
    """El desglose temático ('+N' por temática) debe sumar el universo
    consolidado: Σ counts == consolidated_total (coherencia con la nube y el
    cuadro por vuelta)."""
    import re
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.consolidators import consolidate_findingrefs
    from agents.elite_report.renderer.html_renderer import _render_theme_breakdown
    bundle = _make_bundle()
    stats = PEIRSEliteReport._build_stats(bundle)
    cons = consolidate_findingrefs(bundle.hunter_entries)
    html = _render_theme_breakdown(stats["by_category"], stats["consolidated_total"], cons, "es")
    plus = [int(x) for x in re.findall(r">\+(\d+)<", html)]
    assert sum(plus) == stats["consolidated_total"]
    # Cada temática enlaza al menos un ejemplo a su fuente (si hay findings)
    assert 'class="theme-src"' in html


def test_parliament_scenarios_removed_from_dispatcher():
    """parliament_scenarios era deuda muerta (renderer sin capítulo tras quitar
    el predictivo) → fuera del dispatcher."""
    from agents.elite_report.visualizer.renderer import _ELITE_MAP
    assert "parliament_scenarios" not in _ELITE_MAP


def test_loader_falls_back_to_durable_base(monkeypatch):
    """Con observation_store vacío, el loader debe poblarse desde la base de
    prueba durable (evidence_base/raw/*.jsonl) — el informe nunca sale vacío.
    En los tests la base está desactivada por conftest; la rehabilitamos aquí."""
    import os
    from pathlib import Path
    from agents.elite_report.loaders.hunter_loader import HunterLoader, _EVIDENCE_RAW_DIR
    if not list(Path(_EVIDENCE_RAW_DIR).glob("PER_session_*.jsonl")):
        import pytest
        pytest.skip("No hay base de prueba durable committeada para PER")
    monkeypatch.delenv("PEIRS_DISABLE_DURABLE_BASE", raising=False)
    hl = HunterLoader(observation_store={})  # store vacío
    findings, _, stats = hl.load("PER", "2026-04-08", "2026-06-22")
    assert stats["total"] > 1000, "el fallback durable debería traer el corpus completo"


def test_rights_bars_replaces_heatmap():
    """rights_bars (barras claras) reemplaza el heatmap denso en el dispatcher y
    renderiza SVG válido; el heatmap viejo ya no se adjunta."""
    from agents.elite_report.visualizer.renderer import _ELITE_MAP, render_svg
    assert "rights_bars" in _ELITE_MAP
    svg = render_svg("rights_bars", {"items": [
        {"label": "ICCPR Art. 25", "count": 40}, {"label": "CADH Art. 23", "count": 12}]})
    assert svg.startswith("<svg") and "40" in svg
    # Sin instrumentos → empty-state, no barras vacías
    assert "Sin" in render_svg("rights_bars", {"items": []})


def test_critical_events_table_links_sources():
    """La tabla de eventos críticos (reemplazo de la línea de tiempo amontonada)
    lista críticos/altos con enlace a fuente; no usa la línea de tiempo vieja."""
    from agents.elite_report.renderer.html_renderer import _render_critical_events
    from agents.elite_report.consolidators import consolidate_findingrefs
    bundle = _make_bundle()
    cons = consolidate_findingrefs(bundle.hunter_entries)
    html = _render_critical_events(cons, "es")
    assert 'crit-events' in html and '<table' in html
    assert 'href=' in html  # fuentes enlazadas


def test_evidence_note_matches_report_consolidated():
    """Coherencia numérica: el manifest de la base (que alimenta la nota del
    Anexo C) debe declarar el mismo universo consolidado que _build_stats."""
    import json
    from pathlib import Path
    from agents.elite_report.elite_report import PEIRSEliteReport
    man_path = Path(__file__).resolve().parents[2] / "evidence_base" / "manifest.json"
    raw_dir = Path(__file__).resolve().parents[2] / "evidence_base" / "raw"
    if not man_path.exists() or not list(raw_dir.glob("PER_session_*.jsonl")):
        import pytest
        pytest.skip("No hay base de prueba committeada")
    import glob
    from datetime import datetime, timezone
    from agents.elite_report.models import EvidenceBundle
    from agents.elite_report.loaders.hunter_loader import HunterLoader
    raw = []
    for fp in glob.glob(str(raw_dir / "PER_session_*.jsonl")):
        raw += [json.loads(l) for l in open(fp, encoding="utf-8") if l.strip()]
    now = datetime.now(timezone.utc)
    findings = [HunterLoader._to_finding_ref(e, now) for e in raw]
    findings.sort(key=lambda x: -(x.priority_score or 0))
    bundle = EvidenceBundle(country_code="PER", period_start="2026-04-08",
        period_end="2026-06-22", loaded_at=now.isoformat(), hunter_entries=findings,
        hunter_stats={"total": len(findings)}, alerts_dispatched=0, phase_evidence={},
        rag_documents=[], historical_series=[], cross_references=[], warnings=[])
    stats = PEIRSEliteReport._build_stats(bundle)
    man = json.loads(man_path.read_text(encoding="utf-8"))
    assert man["dedup_total"] == stats["consolidated_total"], (
        f"manifest {man['dedup_total']} != report {stats['consolidated_total']}")


def test_manifest_invariants_partitions_sum_to_totals():
    """Coherencia cuantitativa: en el manifest, toda partición del universo
    reconcilia — la suma por vuelta y por temática == dedup_total, y la suma de
    capturas crudas por vuelta == raw_total. Blinda el pedido de 'perfecta
    coherencia de datos vs hallazgos documentados'."""
    import json
    from pathlib import Path
    man_path = Path(__file__).resolve().parents[2] / "evidence_base" / "manifest.json"
    if not man_path.exists():
        import pytest
        pytest.skip("No hay base de prueba committeada")
    man = json.loads(man_path.read_text(encoding="utf-8"))
    n_dedup = man["dedup_total"]
    assert sum(v["dedup"] for v in man["by_round"].values()) == n_dedup
    assert sum(c["count"] for c in man["by_category"]) == n_dedup
    assert sum(v["raw"] for v in man["by_round"].values()) == man["raw_total"]
    # Coherencia de las temáticas por vuelta con el total temático.
    assert sum(c["count"] for c in man["by_category_round1"]) == man["by_round"]["1ª vuelta"]["dedup"]
    assert sum(c["count"] for c in man["by_category_round2"]) == man["by_round"]["2ª vuelta"]["dedup"]


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


def test_documented_risk_lifts_gauge_and_radar():
    """Los gráficos analíticos reflejan la EVIDENCIA documentada (crisis EMB,
    resultado indeterminado, STAE), no solo el corpus OSINT. Sin esto, el
    medidor daba 'Estable' y el radar 'Org. electoral=100' pese a la crisis."""
    import asyncio
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.models import EliteReportRequest, MissionMetadata
    rep = PEIRSEliteReport(llm=None, observation_store={"PER": {"entries": []}})
    req = EliteReportRequest(country_code="PER", language="es", include_predictive=False,
        output_formats=["html"], mission_metadata=MissionMetadata(report_number="DR",
        period_start="2026-04-12", period_end="2026-06-13", jornada_date="2026-06-07"))
    out = asyncio.run(rep.compose(req))
    concl = next(c for c in out.chapters if c.chapter_id == "conclusiones")
    gauge = next(v for v in concl.visualizations if v.kind == "early_warning_meter")
    radar = next(v for v in concl.visualizations if v.kind == "dimensions_radar")
    # Medidor elevado por hechos documentados (no 'green'/'Estable')
    assert gauge.data["level"] in ("orange", "red")
    assert any("ONPE" in d or "indeterminado" in d for d in gauge.data.get("drivers", []))
    # Radar: "Org. electoral" baja drásticamente (no queda en 100)
    emb_val = next(d["value"] for d in radar.data["dimensions"] if "electoral" in d["label"].lower())
    assert emb_val < 50


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


def test_p1_international_panel_and_suffrage_rights():
    """P1 #7: panel internacional consolidado desde HistoricalSeries.
    P1 #10: afectación al sufragio activo (derecho) en la sección de riesgo."""
    from agents.elite_report.renderer.html_renderer import _render_datasets_overview
    from agents.elite_report.models import HistoricalSeries, HistoricalDatapoint
    s = HistoricalSeries(
        indicator="vdem_libdem", indicator_label="V-Dem — Democracia liberal",
        source="V-Dem v16", source_citation="Coppedge et al.", unit="0-1",
        datapoints=[HistoricalDatapoint(year=2015, value=0.62, source="V-Dem"),
                    HistoricalDatapoint(year=2024, value=0.40, source="V-Dem")],
        trend_direction="down")
    html = _render_datasets_overview([s], language="es")
    assert "datasets-overview" in html
    assert "V-Dem — Democracia liberal" in html
    # Trayectoria: valor inicial (2015) → actual (2024) + tendencia
    assert "0.62" in html and "2015" in html        # inicial
    assert "0.4" in html and "2024" in html and "↓" in html   # actual + tendencia

    # Sufragio activo en la sección de riesgo
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter
    n = build_runoff_observation_chapter(get_adapter("PER").runoff_observation([]), lang="es").narrative
    assert "sufragio activo" in n.lower()
    assert "ICCPR Art. 25.b" in n
    assert "elcomercio.pe" in n                                # fuente


def test_p1_executive_dashboard_and_pro_layout():
    """P1: dashboard ejecutivo (KPIs + viz), numeración de figuras, reglas de
    impresión y badges accesibles con aria-label."""
    import asyncio
    from agents.elite_report.elite_report import PEIRSEliteReport
    from agents.elite_report.models import EliteReportRequest, MissionMetadata
    entries = [{"entry_id": "x1", "category": "security", "severity": "critical",
                "finding": "Incidente en mesa", "credibility": "high", "verified": False,
                "hunter_source": "acled", "evidence_ref": "https://a/1",
                "recorded_at": "2026-06-07", "timestamp": "2026-06-07", "phase": "election_day"}]
    rep = PEIRSEliteReport(llm=None, observation_store={"PER": {"entries": entries}})
    req = EliteReportRequest(country_code="PER", language="es", include_predictive=False,
        include_appendix_c=True, output_formats=["html"],
        mission_metadata=MissionMetadata(report_number="P1", period_start="2026-04-12",
            period_end="2026-06-13", jornada_date="2026-06-07"))
    html = asyncio.run(rep.compose(req)).html or ""
    # Dashboard ejecutivo: banda de KPIs (sin gráficos — no se duplican)
    assert 'id="executive-dashboard"' in html and "Resumen ejecutivo" in html
    assert html.count("kpi-num") >= 4
    # Los gráficos viven en Conclusiones, NO en el dashboard: el semáforo
    # aparece UNA sola vez (sin duplicación dashboard/capítulo).
    assert html.count('aria-label="Sem') <= 1
    # Cuadro de indicadores de datasets después del TOC
    assert 'id="datasets-overview"' in html
    # Layout profesional
    assert "counter-increment: figure-counter" in html
    assert "orphans" in html and "print-color-adjust" in html
    assert "counter(page)" in html                  # numeración de páginas
    # Accesibilidad de badges
    assert 'aria-label="Severidad' in html
    assert "border: 1px solid #d32f2f" in html      # contraste con borde


def test_audit_config_fingerprint_stable_and_complete():
    """P0.3: el sello de auditoría tiene versión + hash estable + clasificador."""
    from modules.audit_config import config_fingerprint, config_hash
    fp = config_fingerprint()
    assert fp["pipeline_version"] and fp["config_version"]
    assert fp["config_hash"] == config_hash()          # estable/determinista
    assert len(fp["config_hash"]) == 16
    assert fp["classifier"]["model"]                    # modelo del clasificador
    assert "escalation" in fp["config"] and "consolidation" in fp["config"]


def test_llm_guard_flags_unsupported_numbers():
    """P0.4: marca cifras ausentes del contexto; no marca las respaldadas
    ni números de artículo chicos."""
    from agents.elite_report.llm_guard import find_unsupported_numbers
    ctx = "La autonomía cayó de 2,40 (2021) a 0,96 (2024). Margen 1.303 votos."
    text = ("El índice fue 1.31 (Art. 178). Cayó a 0,96 con margen de 1303 votos. "
            "Ver subsección 10.2 y el año 1969.")
    flagged = find_unsupported_numbers(text, ctx)
    assert "1.31" in flagged                               # decimal inventado
    assert "0,96" not in flagged                           # respaldado
    assert "1303" not in flagged                           # 1.303 ≈ 1303 (normalizado)
    assert "178" not in flagged                            # número de artículo
    assert "10.2" not in flagged                           # subsección (1 decimal) — excluida
    assert "1969" not in flagged                           # año — no se marca


def test_final_count_pending_proclamation_rendered():
    """Cómputo final al 100% (29-jun) con virtual ganadora pero SIN proclamación
    oficial (JNE el 15-jul): el capítulo y la síntesis lo reflejan sin declarar
    presidenta electa, e incluyen el comentario sobre la demora."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.runoff_chapter import build_runoff_observation_chapter
    from agents.elite_report.declaration_chapter import build_declaration_narrative
    from modules.peru_data import PERU_VDEM_STATIC
    runoff = get_adapter("PER").runoff_observation([])
    n = build_runoff_observation_chapter(runoff, lang="es").narrative
    assert "Sin ganador proclamado" in n
    assert "2026-07-15" in n                          # proclamación pendiente
    assert "Implicancia de la demora" in n            # comentario sobre la demora
    assert "no declara presidenta electa" in n.lower()  # negación explícita, no se anticipa
    syn = build_declaration_narrative(runoff, {"total": 10, "critical": 1, "high": 2},
                                      PERU_VDEM_STATIC.get("emb_series"), lang="es")
    assert "no proclama" in syn.lower() or "sin proclamación" in syn.lower()
    assert "49.641" in syn                            # margen final


def test_appendix_a_has_version_and_limits():
    """P0.2/P0.3: el Anexo A muestra marco muestral, límites y versión auditable."""
    from agents.elite_report.renderer.html_renderer import _render_appendix_a
    from agents.elite_report.models import EliteReportRequest, MissionMetadata
    from modules.audit_config import config_fingerprint
    req = EliteReportRequest(country_code="PER", language="es",
        mission_metadata=MissionMetadata(report_number="A", period_start="2026-04-12",
            period_end="2026-06-13", jornada_date="2026-06-07"))
    html = _render_appendix_a(req, {"total": 100}, language="es", audit=config_fingerprint())
    assert "muestral" in html.lower()                    # marco muestral
    assert "Versión y trazabilidad" in html              # bloque de versión
    assert "claude-sonnet" in html                       # clasificador/modelo
    assert "no son deterministas" in html.lower()        # límite LLM


def test_deterministic_declaration_prologue_and_synthesis():
    """La apertura determinista trae Prólogo (quiénes somos) + Síntesis con
    datos reales (sin invención): terminología 'monitoreo', V-Dem reales
    (2,40→0,96), sin códigos crudos, sin el valor alucinado '1.31'."""
    from agents.elite_report.country_adapters import get_adapter
    from agents.elite_report.declaration_chapter import build_declaration_narrative
    from modules.peru_data import PERU_VDEM_STATIC

    runoff = get_adapter("PER").runoff_observation([])
    stats = {"total": 1922, "critical": 30, "high": 91}
    md = build_declaration_narrative(runoff, stats, PERU_VDEM_STATIC.get("emb_series"), lang="es")
    assert md is not None
    assert "Quiénes somos" in md and "Síntesis ejecutiva" in md
    assert "monitoreó" in md and "monitoreo" in md.lower()
    assert "1.922" in md or "1922" in md            # corpus (volumen)
    assert "sin proclamación" in md.lower() or "no proclama" in md.lower()
    assert "~49.641 votos" in md                      # margen final (cómputo 100%)
    # V-Dem real, NO el inventado 1.31/2025
    assert "2,40" in md and "0,96" in md
    assert "1.31" not in md and "2025" not in md
    assert "v2elemb" not in md                        # sin códigos crudos
    # No legitima / disclosure
    assert "no legitima ni valida" in md


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
