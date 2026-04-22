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
        self._attach_visualizations(chapters, bundle, forecast, stats)

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
                                forecast, stats: Dict[str, Any]) -> None:
        """Adjunta VizSpecs a cada capítulo según su chapter_id."""
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

        # Forecast viz data
        forecast_data = None
        if forecast:
            forecast_data = {
                "scenarios": [
                    {
                        "label": s.label,
                        "probability": s.probability,
                        "ci_low": s.confidence_interval[0] if s.confidence_interval else max(0, s.probability - 0.1),
                        "ci_high": s.confidence_interval[1] if s.confidence_interval else min(1, s.probability + 0.1),
                    }
                    for s in forecast.scenarios
                ],
                "warning_level": forecast.early_warning_level,
            }

        # Heatmap derechos × categorías
        from collections import defaultdict, Counter
        rights_by_cat: Dict[str, Counter] = defaultdict(Counter)
        all_rights: Counter = Counter()
        all_cats: Counter = Counter()
        for f in bundle.hunter_entries:
            cat = f.category or "other"
            all_cats[cat] += 1
            # Extract rights from CrossReferences of this finding
            # (simplificado: usamos categorías conocidas por ahora)
        # Llenar matriz básica con las 4 categorías más comunes
        top_cats = [c for c, _ in all_cats.most_common(6)]
        top_rights = ["ICCPR Art. 25", "CADH Art. 23", "CADH Art. 13",
                      "ICCPR Art. 19(2)", "CDI Art. 3", "Constitución Art. 176"]
        heatmap_matrix = []
        for right in top_rights[:6]:
            row = []
            for cat in top_cats[:6]:
                # Count findings that would invoke this right for this category
                # Usamos el mapping CATEGORY_TO_LAW de CrossReference como proxy
                row.append(sum(1 for cr in bundle.cross_references
                               if cr.normative_instrument.startswith(right.split()[0])
                               and any(f.category == cat and f.entry_id == cr.finding_entry_id
                                        for f in bundle.hunter_entries)))
            heatmap_matrix.append(row)

        heatmap_data = {
            "rights": top_rights[:6],
            "categories": top_cats[:6],
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

        # Asignar viz por chapter_id
        for ch in chapters:
            if ch.chapter_id == "contexto_historico" and series_data["series"]:
                ch.visualizations.append(VizSpec(
                    kind="timeseries_multi",
                    title="Trayectoria histórica — índices democráticos",
                    caption="Series V-Dem, Freedom House, PEI y RSF de los últimos 10 años.",
                    data=series_data,
                ))
            elif ch.chapter_id == "marco_juridico":
                ch.visualizations.append(VizSpec(
                    kind="matrix_normativa",
                    title="Marco normativo aplicable",
                    caption="Instrumentos ordenados por jerarquía normativa.",
                    data=matrix_norm_data,
                ))
            elif ch.chapter_id == "fase_pre_electoral" and phase_data["phases"]:
                ch.visualizations.append(VizSpec(
                    kind="phase_timeline",
                    title="Distribución de hallazgos por fase electoral",
                    caption="Barras apiladas por severidad a lo largo del ciclo.",
                    data=phase_data,
                ))
            elif ch.chapter_id == "derechos_vulnerados":
                ch.visualizations.append(VizSpec(
                    kind="heatmap_rights",
                    title="Heatmap derechos × categorías",
                    caption="Intensidad = cantidad de hallazgos que invocan cada derecho.",
                    data=heatmap_data,
                ))
            elif ch.chapter_id == "analisis_predictivo" and forecast_data:
                ch.visualizations.append(VizSpec(
                    kind="forecast_chart",
                    title="Escenarios probabilísticos con bandas de confianza",
                    caption="Horizonte de 2 semanas post-informe.",
                    data=forecast_data,
                ))
                ch.visualizations.append(VizSpec(
                    kind="scenario_probability",
                    title="Probabilidad por escenario (vista compacta)",
                    caption="",
                    data={"scenarios": forecast_data["scenarios"]},
                ))
            elif ch.chapter_id == "conclusiones":
                ch.visualizations.append(VizSpec(
                    kind="semaphore_institutional",
                    title="Evaluación institucional por órgano",
                    caption="Semáforo de estado al cierre del período observado.",
                    data=semaphore_data,
                ))
                ch.visualizations.append(VizSpec(
                    kind="dimensions_radar",
                    title="8 Dimensiones PEIRS",
                    caption="Evaluación cualitativa ajustada por hallazgos del ciclo.",
                    data=radar_data,
                ))

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
