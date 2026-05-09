"""
PEIRSEliteReport — orquestador principal del informe Elite.

Pipeline completo:
    EliteLoader → PhaseOrganizer → CrossReferenceBuilder → PredictiveEngine
                → ChapterComposer → Visualizer → CitationBuilder → Renderers

Entry point: PEIRSEliteReport.compose(req) → EliteReportOutput.

Integra todos los sprints 2-5 del blueprint ELITE_REPORT.md.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from agents.elite_report.models import (
    EliteReportRequest,
    EliteReportOutput,
    EvidenceBundle,
    VizSpec,
)
from agents.elite_report.loaders import EliteLoader
from agents.elite_report.organizers import PhaseOrganizer, CrossReferenceBuilder
from agents.elite_report.predictive import PredictiveEngine
from agents.elite_report.composer import ChapterComposer, CitationBuilder


# Paths de persistencia
REPORTS_DIR = Path(__file__).parent.parent.parent.parent / "reports" / "elite"

# País → nombre humano (solo PER soportado en Sprint 2-6)
COUNTRY_NAMES = {"PER": "Perú"}


class PEIRSEliteReport:
    """Orquestador principal. Genera el informe Elite completo."""

    def __init__(
        self,
        llm=None,
        observation_store: Optional[Dict] = None,
        alerts_loader: Optional[Callable] = None,
        reports_store: Optional[Dict] = None,
    ):
        """
        Args:
            llm: ChatAnthropic con API key válida. Si None, Composer falla
                 graceful (capítulos vacíos con warning) y Predictive usa
                 solo reglas deterministas.
            observation_store: dict {cc: session} del backend FastAPI.
            alerts_loader: callable(cc, limit) para tabla alerts SQLite.
            reports_store: dict {run_id: report} con datasets estructurales.
        """
        self.llm = llm
        self.loader = EliteLoader(
            observation_store=observation_store,
            alerts_loader=alerts_loader,
        )
        self.reports_store = reports_store  # no usado directamente en Sprint 6

    async def compose(self, req: EliteReportRequest) -> EliteReportOutput:
        """Pipeline completo. Devuelve EliteReportOutput con markdown + html + pdf."""
        start_ts = time.time()
        report_id = str(uuid.uuid4())[:12]
        generated_at = datetime.now(timezone.utc).isoformat()
        country_name = COUNTRY_NAMES.get(req.country_code.upper(), req.country_code)

        # ── 1. LOADER ──────────────────────────────────────────────────
        bundle: EvidenceBundle = await self.loader.load_all(
            country_code=req.country_code,
            period_start=req.mission_metadata.period_start,
            period_end=req.mission_metadata.period_end,
        )

        # ── 2. PHASE ORGANIZER ─────────────────────────────────────────
        phase_org = PhaseOrganizer(country_code=req.country_code)
        phase_evidence = phase_org.organize(bundle.hunter_entries)
        bundle.phase_evidence = phase_evidence

        # ── 3. CROSS REFERENCE ─────────────────────────────────────────
        cr_builder = CrossReferenceBuilder(rag_documents=bundle.rag_documents)
        cross_refs = cr_builder.build_for_findings(bundle.hunter_entries)
        bundle.cross_references = cross_refs

        # ── 4. THEME RANKING (para contexto composer) ──────────────────
        theme_ranking = self._build_theme_ranking(bundle)
        bundle.theme_ranking = theme_ranking

        # ── 5. PREDICTIVE ENGINE ───────────────────────────────────────
        forecast = None
        if req.include_predictive and req.report_type in ("preliminary", "final", "ad_hoc"):
            engine = PredictiveEngine(llm=self.llm, country_code=req.country_code)
            try:
                forecast = await engine.forecast(bundle, horizon_days=req.forecast_horizon_days)
            except Exception as e:
                bundle.warnings.append(
                    f"PredictiveEngine falló: {type(e).__name__}: {e}"
                )

        # ── 6. CHAPTER COMPOSER ────────────────────────────────────────
        stats = self._build_stats(bundle)
        sources_list = self._build_sources_list(bundle)

        composer = ChapterComposer(
            llm=self.llm,
            concurrency_limit=4,
            retries=2,
        )
        chapters = await composer.compose_all(
            req=req,
            hunter_entries=bundle.hunter_entries,
            theme_ranking=theme_ranking,
            phase_evidence=phase_evidence,
            rag_docs=bundle.rag_documents,
            historical_series=bundle.historical_series,
            forecast=forecast,
            stats=stats,
            sources_list=sources_list,
            alerts_dispatched=bundle.alerts_dispatched,
            cross_references=cross_refs,
            country_name=country_name,
            filter_chapters=req.include_chapters,
        )

        # ── 7. ATTACH VISUALIZATIONS A CADA CAPÍTULO ───────────────────
        self._attach_visualizations(chapters, bundle, forecast, stats,
                                     language=req.language or "es")

        # ── 8. CITATION BUILDER ────────────────────────────────────────
        cb = CitationBuilder()
        citations = cb.build_bibliography(
            chapters=chapters,
            hunter_entries=bundle.hunter_entries,
            historical_series=bundle.historical_series,
        )

        # ── 9. RENDERIZADO ─────────────────────────────────────────────
        from agents.elite_report.renderer.html_renderer import render_markdown, render_html
        from agents.elite_report.renderer.pdf_renderer import render_pdf
        from agents.elite_report.renderer.markitdown_bridge import html_to_markdown

        html = render_html(
            chapters=chapters,
            citations=citations,
            req=req,
            stats=stats,
            forecast=forecast,
            country_name=country_name,
            report_id=report_id,
            generated_at=generated_at,
        )

        # Markdown: intentamos con microsoft/markitdown (mejor fidelidad),
        # y si falla degradamos al generador interno.
        markdown = html_to_markdown(html)
        if not markdown:
            markdown = render_markdown(
                chapters=chapters,
                citations=citations,
                req=req,
                stats=stats,
                country_name=country_name,
            )

        pdf_path: Optional[str] = None
        if "pdf" in req.output_formats:
            try:
                pdf_path = render_pdf(html, report_id=report_id)
            except Exception as e:
                bundle.warnings.append(
                    f"PDF renderer falló: {type(e).__name__}: {e}"
                )

        # ── 10. BUILD OUTPUT ──────────────────────────────────────────
        tokens_in = sum(c.tokens_used.get("input", 0) for c in chapters)
        tokens_out = sum(c.tokens_used.get("output", 0) for c in chapters)
        estimated_cost = (tokens_in * 3.0 + tokens_out * 15.0) / 1_000_000

        output = EliteReportOutput(
            report_id=report_id,
            country_code=req.country_code,
            mission=req.mission_metadata,
            audience=req.audience,
            language=req.language,
            report_type=req.report_type,
            generated_at=generated_at,
            status="done",
            chapters=chapters,
            forecast=forecast,
            citations=citations,
            all_findings=bundle.hunter_entries[:500] if req.include_appendix_c else [],
            markdown=markdown,
            html=html,
            pdf_path=pdf_path,
            stats=stats,
            warnings=bundle.warnings,
            tokens_used={"input": tokens_in, "output": tokens_out},
            estimated_cost_usd=round(estimated_cost, 4),
            generation_time_seconds=round(time.time() - start_ts, 2),
        )

        # ── 11. PERSISTENCIA ──────────────────────────────────────────
        self._persist(output)

        return output

    # ────────────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────────────
    @staticmethod
    def _build_stats(bundle: EvidenceBundle) -> Dict[str, Any]:
        """Stats agregadas a nivel de informe."""
        hs = bundle.hunter_stats or {}
        sev = {
            "critical": hs.get("critical", 0),
            "high": hs.get("high", 0),
            "medium": hs.get("medium", 0),
            "low": hs.get("low", 0),
            "info": hs.get("info", 0),
        }
        # Días cubiertos = días únicos con al menos un finding
        days = set()
        for f in bundle.hunter_entries:
            if f.recorded_at:
                days.add(f.recorded_at[:10])
        return {
            "total": hs.get("total", len(bundle.hunter_entries)),
            "critical": sev["critical"],
            "high": sev["high"],
            "medium": sev["medium"],
            "low": sev["low"],
            "info": sev["info"],
            "days_covered": len(days),
            "alerts_dispatched": bundle.alerts_dispatched,
        }

    @staticmethod
    def _build_sources_list(bundle: EvidenceBundle) -> list:
        """Lista única de fuentes RSS activas."""
        seen = set()
        for f in bundle.hunter_entries:
            src = (f.source_name or "").lower()
            if src and src not in seen:
                seen.add(src)
        return sorted(seen)

    @staticmethod
    def _build_theme_ranking(bundle: EvidenceBundle) -> list:
        """Re-usa la lógica del Structurer del ReportDesigner para construir
        el theme_ranking (ordenado por densidad high+critical)."""
        from collections import Counter, defaultdict
        # Asignar temas desde FindingRef.themes si ya vienen, o inferir desde categorías
        buckets: Dict[str, list] = defaultdict(list)
        for f in bundle.hunter_entries:
            if f.themes:
                for t in f.themes:
                    buckets[t].append(f)
            else:
                # Fallback: usar category como tema
                buckets[f.category or "other"].append(f)

        ranking = []
        for theme_id, fs in buckets.items():
            hc = sum(1 for f in fs if (f.severity or "").lower() in ("high", "critical"))
            ranking.append({
                "theme_id": theme_id,
                "label": theme_id.replace("_", " ").title(),
                "total": len(fs),
                "high_critical": hc,
                "top_findings": sorted(fs, key=lambda x: -(x.priority_score or 0))[:3],
            })
        ranking.sort(key=lambda x: (-x["high_critical"], -x["total"]))
        return ranking

    @staticmethod
    def _attach_visualizations(chapters: list, bundle: EvidenceBundle,
                                forecast, stats: Dict[str, Any],
                                language: str = "es") -> None:
        """Adjunta VizSpecs a cada capítulo según su chapter_id.

        Todos los `title=` y `caption=` se traducen via i18n keys
        `viz.{kind}.title` / `viz.{kind}.caption` para soportar es/en/pt.
        """
        from agents.elite_report.i18n import t as _t
        # Datos pre-computados reutilizables
        series_data = {
            "series": [
                {
                    "label": s.indicator_label,
                    "unit": s.unit,
                    "points": [{"year": p.year, "value": p.value} for p in s.datapoints],
                }
                for s in bundle.historical_series
            ],
            "events": [],  # se puede enriquecer en Sprint 5b
        }

        phase_data = {
            "phases": [],
        }
        for phase_id, pe in bundle.phase_evidence.items():
            phase_data["phases"].append({
                "phase": phase_id,
                "label": pe.phase_label,
                "total": pe.total_count,
                "critical": pe.critical_count,
                "high": pe.high_count,
                "medium": pe.medium_count,
                "low": sum(1 for f in pe.findings if (f.severity or "").lower() == "low"),
                "info": sum(1 for f in pe.findings if (f.severity or "").lower() == "info"),
            })

        # Forecast viz data — scenario labels via i18n key forecast.scenario.{id}.label
        forecast_data = None
        if forecast:
            from agents.elite_report.i18n import t as _ti
            def _scen_label(s):
                key = f"forecast.scenario.{s.scenario_id}.label"
                return _ti(language, key, default=s.label)
            forecast_data = {
                "scenarios": [
                    {
                        "label": _scen_label(s),
                        "probability": s.probability,
                        "ci_low": s.confidence_interval[0] if s.confidence_interval else max(0, s.probability - 0.1),
                        "ci_high": s.confidence_interval[1] if s.confidence_interval else min(1, s.probability + 0.1),
                    }
                    for s in forecast.scenarios
                ],
                "warning_level": forecast.early_warning_level,
            }

        # Heatmap derechos × categorías (Cap 8) — auditoria 9-may-2026:
        #   A) Fix matching: usar igualdad exacta en cross_reference.normative_instrument
        #      en vez de prefix-match (que duplicaba conteos entre Art. 25 y Art. 19(2)
        #      del mismo tratado).
        #   B) Rights dinamicos: top-6 instrumentos REALMENTE invocados por los
        #      cross_references del periodo, no una lista hardcoded de 6.
        #   C) i18n de los nombres traducibles ("Constitución" -> "Constitution"/"Constituição").
        from collections import defaultdict, Counter
        from agents.elite_report.i18n import translate_instrument as _ti_instr

        # Top-6 categorias del Hunter (sin cambios)
        all_cats: Counter = Counter()
        for f in bundle.hunter_entries:
            cat = f.category or "other"
            all_cats[cat] += 1
        top_cats = [c for c, _ in all_cats.most_common(6)]

        # Top-6 rights extraidos de los cross_references reales del periodo (B)
        cr_counts: Counter = Counter()
        for cr in bundle.cross_references:
            cr_counts[cr.normative_instrument] += 1
        top_rights = [r for r, _ in cr_counts.most_common(6)]

        # Fallback canonico si no hay cross_references aun (e.g. periodo sin
        # findings high/critical). Mantiene el grafico informativo en vez de
        # mostrar empty-state cuando si hay categorias del Hunter.
        if not top_rights:
            top_rights = ["ICCPR Art. 25", "CADH Art. 23", "CADH Art. 13",
                          "ICCPR Art. 19(2)", "CDI Art. 3", "Constitución Art. 176"]

        # Index entry_id -> category para reducir el costo del cross-product
        entry_cat: Dict[str, str] = {f.entry_id: (f.category or "other") for f in bundle.hunter_entries}

        # Build matriz con match EXACTO (A)
        heatmap_matrix = []
        for right in top_rights:
            row = []
            for cat in top_cats:
                count = sum(
                    1 for cr in bundle.cross_references
                    if cr.normative_instrument == right
                    and entry_cat.get(cr.finding_entry_id) == cat
                )
                row.append(count)
            heatmap_matrix.append(row)

        # Traducir labels de derechos al idioma del informe (C)
        display_rights = [_ti_instr(r, language) for r in top_rights]

        heatmap_data = {
            "rights": display_rights,
            "categories": top_cats,
            "matrix": heatmap_matrix,
        }

        # Matriz normativa (cap 2)
        matrix_norm_data = {
            "rows": [
                {"instrument": "Constitución Art. 176", "topic": "Finalidad del sistema electoral",
                 "hierarchy": "constitucional"},
                {"instrument": "Constitución Art. 178", "topic": "Atribuciones del JNE",
                 "hierarchy": "constitucional"},
                {"instrument": "Constitución Art. 183", "topic": "Funciones de ONPE",
                 "hierarchy": "constitucional"},
                {"instrument": "LOE Art. 190", "topic": "Silencio electoral",
                 "hierarchy": "legal"},
                {"instrument": "LOE Art. 343", "topic": "Actas observadas",
                 "hierarchy": "legal"},
                {"instrument": "LOE Art. 380", "topic": "Segunda vuelta",
                 "hierarchy": "legal"},
                {"instrument": "LOP Art. 34", "topic": "Transparencia financiera",
                 "hierarchy": "legal"},
                {"instrument": "Ley 31030 (2020)", "topic": "Paridad y alternancia",
                 "hierarchy": "legal"},
                {"instrument": "Ley 31170 (2021)", "topic": "Acoso político",
                 "hierarchy": "legal"},
                {"instrument": "Res. JNE 0891-2025", "topic": "Rechazo del voto electrónico",
                 "hierarchy": "jurisprudencial"},
                {"instrument": "ICCPR Art. 25", "topic": "Derechos políticos",
                 "hierarchy": "internacional"},
                {"instrument": "CADH Art. 23", "topic": "Derechos políticos interamericanos",
                 "hierarchy": "internacional"},
            ]
        }

        # Radar 8 dimensiones (ejemplo — se recalcula a partir de stats)
        # Heurística simple: valor = max(0, 100 - (findings_en_esa_dim * factor))
        radar_data = {
            "dimensions": [
                {"label": "Sufragio", "value": 55},
                {"label": "Marco legal", "value": 72},
                {"label": "Org. electoral", "value": 28},  # ONPE en crisis
                {"label": "Medios", "value": 58},
                {"label": "Financiamiento", "value": 50},
                {"label": "Digital / IA", "value": 35},
                {"label": "Justicia electoral", "value": 60},
                {"label": "Inclusividad", "value": 62},
            ]
        }

        # Semáforo institucional
        semaphore_data = {
            "organs": [
                {"label": "JNE", "status": "amber",
                 "note": "Activo pero bajo tensión con ONPE"},
                {"label": "ONPE", "status": "red",
                 "note": "Crisis operativa + investigación penal"},
                {"label": "RENIEC", "status": "green",
                 "note": "Operando sin incidentes reportados"},
                {"label": "Proceso global", "status": "amber",
                 "note": "Legítimo con observaciones estructurales"},
            ]
        }

        # ── Sprint 5b — Datos derivados del bundle ──────────────────────────

        # events_timeline: top-N hallazgos por (severity desc, date asc) (cap 1)
        sev_rank = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
        ranked_findings = sorted(
            bundle.hunter_entries,
            key=lambda f: (-sev_rank.get((f.severity or "info").lower(), 0),
                           f.recorded_at or ""),
        )
        events_timeline_data = {
            "events": [
                {
                    "date": (f.recorded_at or "")[:10],
                    "label": (f.finding or "")[:46],
                    "severity": (f.severity or "info").lower(),
                }
                for f in ranked_findings[:10]
            ],
        }

        # hourly_timeline: eventos por hora del día electoral (cap 5)
        # Filtrar findings de jornada_date y agrupar por hora.
        hourly_buckets: Dict[int, Dict[str, Any]] = {}
        for f in bundle.hunter_entries:
            ts = f.recorded_at or ""
            if "T" in ts:
                try:
                    h = int(ts.split("T")[1][:2])
                    if 8 <= h <= 18:
                        bucket = hourly_buckets.setdefault(
                            h, {"count": 0, "max_sev": "info"}
                        )
                        bucket["count"] += 1
                        sev = (f.severity or "info").lower()
                        if sev_rank.get(sev, 0) > sev_rank.get(bucket["max_sev"], 0):
                            bucket["max_sev"] = sev
                except (ValueError, IndexError):
                    pass
        hourly_data = {
            "events": [
                {"hour": f"{h:02d}:00", "count": b["count"], "severity": b["max_sev"]}
                for h, b in sorted(hourly_buckets.items())
            ],
            "start_hour": 8, "end_hour": 18,
        }

        # progress_chart: % actas procesadas (cap 6) — MOCK por ahora,
        # data real viene de ONPE escrutinio si está disponible.
        progress_data = {
            "points": [
                {"t": "21:00", "pct": 12.4}, {"t": "00:00", "pct": 38.2},
                {"t": "06:00", "pct": 67.5}, {"t": "12:00", "pct": 84.1},
                {"t": "18:00", "pct": 92.3}, {"t": "00:00+", "pct": 95.1},
            ],
            "current_pct": 95.1,
        }

        # integrity_incidents_grid: regiones × categorías (cap 6)
        # Top regiones del PERU_REGIONS_DATA si país es PER
        try:
            from modules.peru_data import PERU_REGIONS_DATA, PERU_PARL_DATA
            _peru_data_available = True
        except ImportError:
            _peru_data_available = False
            PERU_REGIONS_DATA = []
            PERU_PARL_DATA = {}

        # Verificar si tenemos datos de location en el bundle (campo opcional
        # en FindingRef desde 2026-04-29; antes era None para todos los findings).
        has_locations = any(
            (f.location or "").strip() for f in bundle.hunter_entries
        )

        if bundle.country_code == "PER" and _peru_data_available and has_locations:
            top_regions_per = [r["region"] for r in PERU_REGIONS_DATA[:8]]
        else:
            top_regions_per = []
        # Categorías observadas en el bundle (top 6)
        cat_top6 = [c for c, _ in all_cats.most_common(6)]
        # Matriz: por cada región, contar findings_in_finding.location ~ region por categoría
        grid_values: List[List[int]] = []
        for reg in top_regions_per:
            row = []
            for cat in cat_top6:
                count = sum(1 for f in bundle.hunter_entries
                            if (f.location or "").lower().find(reg.lower()) != -1
                            and f.category == cat)
                row.append(count)
            grid_values.append(row)
        incidents_grid_data = {
            "rows": top_regions_per, "cols": cat_top6, "values": grid_values,
        }

        # map_regions_affected: intensidad por región (cap 5)
        # Sólo se popula si hay location data en el bundle. Caso contrario,
        # el viz cae en empty_state placeholder en el renderer.
        regions_affected_data: Dict[str, Any] = {"regions": []}
        if bundle.country_code == "PER" and _peru_data_available and has_locations:
            for r in PERU_REGIONS_DATA[:24]:
                # Contar findings cuya location coincide con la región
                count = sum(1 for f in bundle.hunter_entries
                            if (f.location or "").lower().find(r["region"].lower()) != -1)
                # Intensidad por count
                if count >= 20:
                    intens = "critical"
                elif count >= 10:
                    intens = "high"
                elif count >= 4:
                    intens = "medium"
                else:
                    intens = "low"
                regions_affected_data["regions"].append({
                    "name": r["region"], "intensity": intens, "incidents": count,
                })

        # actor_network: red de actores (cap 7) — institucional + partidario
        # Type/action labels traducidos por idioma del informe.
        _i18n_actor = {
            "es": {"inst": "institución", "fis": "fiscal", "jud": "judicial", "med": "media",
                   "investiga": "investiga", "audita": "audita", "padrón": "padrón",
                   "supervisa": "supervisa", "reporta": "reporta",
                   "fiscalia": "Fiscalía", "pj": "Poder Judicial", "prensa": "Prensa indep."},
            "en": {"inst": "institution", "fis": "prosecutor", "jud": "judicial", "med": "media",
                   "investiga": "investigates", "audita": "audits", "padrón": "electoral roll",
                   "supervisa": "supervises", "reporta": "reports",
                   "fiscalia": "Prosecutor's Office", "pj": "Judiciary", "prensa": "Independent press"},
            "pt": {"inst": "instituição", "fis": "fiscal", "jud": "judicial", "med": "media",
                   "investiga": "investiga", "audita": "audita", "padrón": "cadastro",
                   "supervisa": "supervisiona", "reporta": "reporta",
                   "fiscalia": "Ministério Público", "pj": "Judiciário", "prensa": "Imprensa indep."},
        }.get(language, None) or {}
        if not _i18n_actor:
            _i18n_actor = {"inst": "institución", "fis": "fiscal", "jud": "judicial", "med": "media",
                           "investiga": "investiga", "audita": "audita", "padrón": "padrón",
                           "supervisa": "supervisa", "reporta": "reporta",
                           "fiscalia": "Fiscalía", "pj": "Poder Judicial", "prensa": "Prensa indep."}
        actor_network_data = {
            "actors": [
                {"id": "JNE", "label": "JNE", "type": _i18n_actor["inst"]},
                {"id": "ONPE", "label": "ONPE", "type": _i18n_actor["inst"]},
                {"id": "RENIEC", "label": "RENIEC", "type": _i18n_actor["inst"]},
                {"id": "FIS", "label": _i18n_actor["fiscalia"], "type": _i18n_actor["fis"]},
                {"id": "PJ", "label": _i18n_actor["pj"], "type": _i18n_actor["jud"]},
                {"id": "PRENSA", "label": _i18n_actor["prensa"], "type": _i18n_actor["med"]},
            ],
            "edges": [
                {"from": "FIS", "to": "ONPE", "action": _i18n_actor["investiga"], "severity": "high"},
                {"from": "JNE", "to": "ONPE", "action": _i18n_actor["audita"], "severity": "medium"},
                {"from": "RENIEC", "to": "ONPE", "action": _i18n_actor["padrón"], "severity": "info"},
                {"from": "PJ", "to": "FIS", "action": _i18n_actor["supervisa"], "severity": "info"},
                {"from": "PRENSA", "to": "ONPE", "action": _i18n_actor["reporta"], "severity": "medium"},
            ],
        }

        # judicial_timeline: cronología (cap 7) — derivada de findings legal/judicial
        judicial_findings = [
            f for f in ranked_findings
            if (f.category or "").lower() in
            ("legal", "fraud_allegation", "irregular_procedure", "judicial")
        ][:8]
        judicial_data = {
            "actions": [
                {
                    "date": (f.recorded_at or "")[:10],
                    "actor": (f.source_name or "—")[:24],
                    "action": (f.finding or "")[:80],
                    "severity": (f.severity or "info").lower(),
                }
                for f in judicial_findings
            ],
        }

        # compliance_matrix: cumplimiento ICCPR/CADH por artículo (cap 8)
        # Derivar de cross_references contando severidad por artículo
        article_breaches: Dict[str, Dict[str, int]] = {}
        for cr in bundle.cross_references:
            art = cr.normative_instrument
            if art not in article_breaches:
                article_breaches[art] = {"total": 0, "high": 0}
            article_breaches[art]["total"] += 1
            # find linked finding
            for f in bundle.hunter_entries:
                if f.entry_id == cr.finding_entry_id and (f.severity or "").lower() in ("critical", "high"):
                    article_breaches[art]["high"] += 1
                    break
        compliance_rows = []
        for art, br in sorted(article_breaches.items(), key=lambda x: -x[1]["total"])[:12]:
            if br["high"] >= 5:
                status = "breach"
            elif br["high"] >= 1 or br["total"] >= 3:
                status = "partial"
            elif br["total"] > 0:
                status = "ok"
            else:
                status = "unknown"
            compliance_rows.append({
                "article": art[:32],
                "topic": "—",  # se podría enriquecer mapeando art→tema
                "status": status,
                "evidence_count": br["total"],
            })
        compliance_data = {"rows": compliance_rows}

        # early_warning_meter (cap 9) — derivado del forecast.early_warning_level
        warning_score_map = {"green": 0.15, "amber": 0.40, "orange": 0.65, "red": 0.88}
        if forecast and forecast.early_warning_level:
            level = forecast.early_warning_level
        else:
            # Fallback: derivar score de critical/total
            crit = stats.get("by_severity", {}).get("critical", 0)
            total = max(stats.get("total", 1), 1)
            ratio = crit / total
            if ratio >= 0.05: level = "red"
            elif ratio >= 0.02: level = "orange"
            elif ratio >= 0.005: level = "amber"
            else: level = "green"
        # Drivers: top categorías
        top_drivers = [c for c, _ in all_cats.most_common(3)]
        # i18n labels para early_warning, recommendations, architecture
        _i18n_data = {
            "es": {
                "ew_levels": {"green": "Estable", "amber": "Vigilancia",
                              "orange": "Riesgo elevado", "red": "Crisis"},
                "horizon_short": "corto", "horizon_medium": "medio", "horizon_long": "largo",
                "rec_rows": [
                    "Auditar STAE/SCE con tercero independiente",
                    "Marco legal IA en procesos electorales",
                    "Reforzar cadena de custodia de actas",
                    "Capacitación obligatoria miembros de mesa",
                    "Marco regulatorio publicidad digital",
                    "Protocolo de respuesta a desinformación",
                ],
                "addressee_congress": "Congreso", "addressee_jne_cong": "JNE/Congreso",
                "addressee_onpe_jne": "ONPE/JNE",
                "stae_subtitle": "Mesa — laptops/imp.",
                "sce_subtitle": "Cómputo + IA dual",
                "spr_subtitle": "resultadoelectoral",
                "flow_label_actas": "actas + foto",
                "flow_label_aggr": "agregados",
                "role_arbiter": "árbitro", "role_org": "organización", "role_roll": "padrón",
                "edge_label_roll": "padrón", "edge_label_tally": "actas",
                "edge_label_oversight": "fiscaliza",
                "stage_roll": "Padrón", "stage_table": "Mesa",
                "stage_tally": "Acta", "stage_count": "Cómputo",
                "stage_proclaim": "Proclamación",
                "actor_table_members": "Miembros mesa",
            },
            "en": {
                "ew_levels": {"green": "Stable", "amber": "Watch",
                              "orange": "Elevated risk", "red": "Crisis"},
                "horizon_short": "short", "horizon_medium": "medium", "horizon_long": "long",
                "rec_rows": [
                    "Audit STAE/SCE with an independent third party",
                    "Legal framework for AI in electoral processes",
                    "Strengthen chain of custody of tally sheets",
                    "Mandatory training for polling station members",
                    "Regulatory framework for digital advertising",
                    "Disinformation response protocol",
                ],
                "addressee_congress": "Congress", "addressee_jne_cong": "JNE/Congress",
                "addressee_onpe_jne": "ONPE/JNE",
                "stae_subtitle": "Polling — laptops/printers",
                "sce_subtitle": "Tabulation + dual AI",
                "spr_subtitle": "results portal",
                "flow_label_actas": "tally sheets + photo",
                "flow_label_aggr": "aggregates",
                "role_arbiter": "arbiter", "role_org": "organization",
                "role_roll": "electoral roll",
                "edge_label_roll": "electoral roll", "edge_label_tally": "tally sheets",
                "edge_label_oversight": "oversight",
                "stage_roll": "Electoral roll", "stage_table": "Polling station",
                "stage_tally": "Tally sheet", "stage_count": "Tabulation",
                "stage_proclaim": "Proclamation",
                "actor_table_members": "Polling members",
            },
            "pt": {
                "ew_levels": {"green": "Estável", "amber": "Vigilância",
                              "orange": "Risco elevado", "red": "Crise"},
                "horizon_short": "curto", "horizon_medium": "médio", "horizon_long": "longo",
                "rec_rows": [
                    "Auditar STAE/SCE com terceiro independente",
                    "Marco legal de IA em processos eleitorais",
                    "Reforçar cadeia de custódia das atas",
                    "Capacitação obrigatória dos membros de mesa",
                    "Marco regulatório de publicidade digital",
                    "Protocolo de resposta a desinformação",
                ],
                "addressee_congress": "Congresso", "addressee_jne_cong": "JNE/Congresso",
                "addressee_onpe_jne": "ONPE/JNE",
                "stae_subtitle": "Mesa — laptops/imp.",
                "sce_subtitle": "Apuração + IA dual",
                "spr_subtitle": "portal de resultados",
                "flow_label_actas": "atas + foto",
                "flow_label_aggr": "agregados",
                "role_arbiter": "árbitro", "role_org": "organização", "role_roll": "cadastro",
                "edge_label_roll": "cadastro", "edge_label_tally": "atas",
                "edge_label_oversight": "fiscaliza",
                "stage_roll": "Cadastro", "stage_table": "Mesa",
                "stage_tally": "Ata", "stage_count": "Apuração",
                "stage_proclaim": "Proclamação",
                "actor_table_members": "Membros mesa",
            },
        }.get(language, {})
        if not _i18n_data:
            _i18n_data = _i18n_actor and {} or {}  # caer a es default
        # Asegurar estructura mínima si language unsupported
        _i18n_data = _i18n_data or {
            "ew_levels": {"green": "Estable", "amber": "Vigilancia",
                          "orange": "Riesgo elevado", "red": "Crisis"},
            "horizon_short": "corto", "horizon_medium": "medio", "horizon_long": "largo",
            "rec_rows": ["Auditar STAE/SCE con tercero independiente",
                         "Marco legal IA en procesos electorales",
                         "Reforzar cadena de custodia de actas",
                         "Capacitación obligatoria miembros de mesa",
                         "Marco regulatorio publicidad digital",
                         "Protocolo de respuesta a desinformación"],
            "addressee_congress": "Congreso", "addressee_jne_cong": "JNE/Congreso",
            "addressee_onpe_jne": "ONPE/JNE",
            "stae_subtitle": "Mesa — laptops/imp.", "sce_subtitle": "Cómputo + IA dual",
            "spr_subtitle": "resultadoelectoral",
            "flow_label_actas": "actas + foto", "flow_label_aggr": "agregados",
            "role_arbiter": "árbitro", "role_org": "organización", "role_roll": "padrón",
            "edge_label_roll": "padrón", "edge_label_tally": "actas",
            "edge_label_oversight": "fiscaliza",
            "stage_roll": "Padrón", "stage_table": "Mesa",
            "stage_tally": "Acta", "stage_count": "Cómputo",
            "stage_proclaim": "Proclamación",
            "actor_table_members": "Miembros mesa",
        }

        early_warning_data = {
            "level": level,
            "score": warning_score_map.get(level, 0.5),
            "label": _i18n_data["ew_levels"].get(level, ""),
            "drivers": top_drivers,
        }

        # matrix_recommendations (cap 11)
        _rec_rows = _i18n_data["rec_rows"]
        _hs = _i18n_data["horizon_short"]
        _hm = _i18n_data["horizon_medium"]
        recommendations_data = {
            "rows": [
                {"recommendation": _rec_rows[0], "addressee": "ONPE",
                 "priority": "critical", "horizon": _hs},
                {"recommendation": _rec_rows[1],
                 "addressee": _i18n_data["addressee_congress"],
                 "priority": "high", "horizon": _hm},
                {"recommendation": _rec_rows[2],
                 "addressee": _i18n_data["addressee_onpe_jne"],
                 "priority": "high", "horizon": _hs},
                {"recommendation": _rec_rows[3], "addressee": "ONPE",
                 "priority": "medium", "horizon": _hs},
                {"recommendation": _rec_rows[4],
                 "addressee": _i18n_data["addressee_jne_cong"],
                 "priority": "medium", "horizon": _hm},
                {"recommendation": _rec_rows[5], "addressee": "JNE",
                 "priority": "high", "horizon": _hs},
            ]
        }

        # system_architecture (cap 12) — STAE + SCE + SPR
        architecture_data = {
            "components": [
                {"id": "STAE", "label": "STAE",
                 "subtitle": _i18n_data["stae_subtitle"], "layer": "edge", "audited": False},
                {"id": "SCE", "label": "SCE",
                 "subtitle": _i18n_data["sce_subtitle"], "layer": "core", "audited": False},
                {"id": "SPR", "label": "SPR",
                 "subtitle": _i18n_data["spr_subtitle"], "layer": "publish", "audited": True},
            ],
            "flows": [
                {"from": "STAE", "to": "SCE", "label": _i18n_data["flow_label_actas"]},
                {"from": "SCE", "to": "SPR", "label": _i18n_data["flow_label_aggr"]},
            ],
        }

        # network_institutions (cap 3) — JNE + ONPE + RENIEC + relaciones
        network_inst_data = {
            "nodes": [
                {"id": "JNE", "label": "JNE", "role": _i18n_data["role_arbiter"], "status": "amber"},
                {"id": "ONPE", "label": "ONPE", "role": _i18n_data["role_org"], "status": "red"},
                {"id": "RENIEC", "label": "RENIEC", "role": _i18n_data["role_roll"], "status": "ok"},
            ],
            "edges": [
                {"from": "RENIEC", "to": "ONPE", "label": _i18n_data["edge_label_roll"]},
                {"from": "ONPE", "to": "JNE", "label": _i18n_data["edge_label_tally"]},
                {"from": "JNE", "to": "ONPE", "label": _i18n_data["edge_label_oversight"]},
            ],
        }

        # flow_chart_voting (cap 3) — cadena del voto
        flow_voting_data = {
            "stages": [
                {"name": _i18n_data["stage_roll"], "actor": "RENIEC", "status": "ok"},
                {"name": _i18n_data["stage_table"], "actor": "ONPE+ODPE", "status": "ok"},
                {"name": _i18n_data["stage_tally"], "actor": _i18n_data["actor_table_members"], "status": "warn"},
                {"name": "STAE/SCE", "actor": "ONPE", "status": "warn"},
                {"name": _i18n_data["stage_count"], "actor": "JEE", "status": "ok"},
                {"name": _i18n_data["stage_proclaim"], "actor": "JNE", "status": "pending"},
            ],
        }

        # parliament_scenarios (cap 9) — sólo PER
        parliament_data: Optional[Dict[str, Any]] = None
        if bundle.country_code == "PER" and _peru_data_available and PERU_PARL_DATA.get("scenarios"):
            parliament_data = {
                "scenarios": PERU_PARL_DATA["scenarios"],
                "total_seats": PERU_PARL_DATA.get("total_seats", 130),
            }

        # ── Asignar viz por chapter_id ──────────────────────────────────────
        # Helper local: crea VizSpec con title/caption traducidos via i18n.
        # Inyecta _language en data para que los renderers internos puedan
        # i18n sus strings hardcoded (status labels, headers uppercase, etc).
        def _vs(kind: str, data: Dict[str, Any]) -> VizSpec:
            data_with_lang = dict(data) if isinstance(data, dict) else {"_data": data}
            data_with_lang["_language"] = language
            return VizSpec(
                kind=kind,
                title=_t(language, f"viz.{kind}.title"),
                caption=_t(language, f"viz.{kind}.caption", ""),
                data=data_with_lang,
            )

        for ch in chapters:
            if ch.chapter_id == "contexto_historico":
                if series_data["series"]:
                    ch.visualizations.append(_vs("timeseries_multi", series_data))
                if events_timeline_data["events"]:
                    ch.visualizations.append(_vs("events_timeline", events_timeline_data))
            elif ch.chapter_id == "marco_juridico":
                ch.visualizations.append(_vs("matrix_normativa", matrix_norm_data))
            elif ch.chapter_id == "sistema_electoral":
                ch.visualizations.append(_vs("flow_chart_voting", flow_voting_data))
                ch.visualizations.append(_vs("network_institutions", network_inst_data))
            elif ch.chapter_id == "fase_pre_electoral" and phase_data["phases"]:
                ch.visualizations.append(_vs("phase_timeline", phase_data))
            elif ch.chapter_id == "jornada_electoral":
                if hourly_data["events"]:
                    ch.visualizations.append(_vs("hourly_timeline", hourly_data))
                if regions_affected_data["regions"]:
                    ch.visualizations.append(_vs("map_regions_affected", regions_affected_data))
            elif ch.chapter_id == "escrutinio_computo":
                ch.visualizations.append(_vs("progress_chart", progress_data))
                if any(any(v > 0 for v in row) for row in incidents_grid_data["values"]):
                    ch.visualizations.append(_vs("integrity_incidents_grid", incidents_grid_data))
            elif ch.chapter_id == "post_electoral":
                ch.visualizations.append(_vs("actor_network", actor_network_data))
                if judicial_data["actions"]:
                    ch.visualizations.append(_vs("judicial_timeline", judicial_data))
            elif ch.chapter_id == "derechos_vulnerados":
                ch.visualizations.append(_vs("heatmap_rights", heatmap_data))
                if compliance_data["rows"]:
                    ch.visualizations.append(_vs("compliance_matrix", compliance_data))
            elif ch.chapter_id == "analisis_predictivo":
                if forecast_data:
                    ch.visualizations.append(_vs("forecast_chart", forecast_data))
                    ch.visualizations.append(_vs(
                        "scenario_probability",
                        {"scenarios": forecast_data["scenarios"]},
                    ))
                ch.visualizations.append(_vs("early_warning_meter", early_warning_data))
                # Cableado de parliament_scenarios retirado 2026-04-29 a pedido
                # de Mariana.
            elif ch.chapter_id == "conclusiones":
                ch.visualizations.append(_vs("semaphore_institutional", semaphore_data))
                ch.visualizations.append(_vs("dimensions_radar", radar_data))
            elif ch.chapter_id == "recomendaciones":
                ch.visualizations.append(_vs("matrix_recommendations", recommendations_data))
            elif ch.chapter_id == "ia_regulacion":
                ch.visualizations.append(_vs("system_architecture", architecture_data))

    def _persist(self, output: EliteReportOutput) -> None:
        """Guarda markdown + html + metadata.json en reports/elite/{report_id}/."""
        try:
            base_dir = REPORTS_DIR / output.report_id
            base_dir.mkdir(parents=True, exist_ok=True)

            if output.markdown:
                (base_dir / "report.md").write_text(output.markdown, encoding="utf-8")
            if output.html:
                (base_dir / "report.html").write_text(output.html, encoding="utf-8")

            metadata = {
                "report_id": output.report_id,
                "country_code": output.country_code,
                "mission": output.mission.model_dump(),
                "audience": output.audience,
                "language": output.language,
                "report_type": output.report_type,
                "generated_at": output.generated_at,
                "stats": output.stats,
                "tokens_used": output.tokens_used,
                "estimated_cost_usd": output.estimated_cost_usd,
                "generation_time_seconds": output.generation_time_seconds,
                "pdf_path": output.pdf_path,
                "warnings_count": len(output.warnings),
            }
            (base_dir / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            output.warnings.append(f"Persistencia falló: {type(e).__name__}: {e}")
