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
from agents.elite_report.consolidators import consolidate_findingrefs
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
        self.observation_store = observation_store
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

        # ── 5. PREDICTIVE ENGINE — DESACTIVADO ─────────────────────────
        # El informe es RETROSPECTIVO/factual (la elección ya ocurrió). Se
        # eliminó el análisis probabilístico (proyecciones + escenarios) a
        # pedido institucional. El medidor de alerta temprana se conserva como
        # ÍNDICE DE SEVERIDAD del período observado (no es pronóstico) y se
        # renderiza en Conclusiones. forecast queda None: no hay capítulo
        # predictivo en el catálogo y _attach_visualizations no emite
        # forecast_chart ni scenario_probability.
        forecast = None

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

        # ── 6b. CAPÍTULO DETERMINISTA: observación entre vueltas ───────
        # 9 ejes canónicos con audit_status objetivo. Sin LLM: se genera
        # siempre, con lenguaje honesto de estado vacío (PER-específico).
        try:
            from agents.elite_report.country_adapters import get_adapter
            from agents.elite_report.runoff_chapter import build_runoff_observation_chapter
            _adapter = get_adapter(req.country_code)
            runoff_obs = None
            if hasattr(_adapter, "runoff_observation"):
                entries = (self.observation_store or {}).get(
                    req.country_code.upper(), {}
                ).get("entries", [])
                runoff_obs = _adapter.runoff_observation(entries)
            runoff_chapter = build_runoff_observation_chapter(
                runoff_obs, lang=req.language or "es"
            )
            if runoff_chapter is not None:
                # Insertar justo después de "Jornada electoral" (cap. 5) y
                # renumerar los capítulos positivos en orden de lista, para que
                # la observación del balotaje quede en el flujo del proceso y no
                # como anexo tras "IA y regulación".
                insert_at = len(chapters)
                for i, ch in enumerate(chapters):
                    if ch.chapter_id == "jornada_electoral":
                        insert_at = i + 1
                        break
                chapters.insert(insert_at, runoff_chapter)
                n = 0
                for ch in chapters:
                    if ch.number > 0:
                        n += 1
                        ch.number = n
        except Exception as e:
            bundle.warnings.append(
                f"Capítulo observación entre vueltas falló: {type(e).__name__}: {e}"
            )

        # ── 7. ATTACH VISUALIZATIONS A CADA CAPÍTULO ───────────────────
        self._attach_visualizations(chapters, bundle, forecast, stats,
                                     language=req.language or "es")

        # ── 8. CITATION BUILDER ────────────────────────────────────────
        cb = CitationBuilder(language=req.language or "es")
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
            # Anexo C consolidado: un hecho = una fila con todas sus fuentes.
            findings=(consolidate_findingrefs(bundle.hunter_entries)
                      if req.include_appendix_c else None),
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
            all_findings=bundle.hunter_entries[:2500] if req.include_appendix_c else [],
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
            # Mapa por severidad — consumido por el medidor de alerta temprana
            # (early_warning_data). Sin esto, crisis_index quedaba en 0.0 siempre.
            "by_severity": dict(sev),
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

        # ── Sprint 2: CountryAdapter resuelve toda la data PER-especifica ──
        # En lugar de inline data dicts, llamamos al adapter del pais. Para
        # Brasil/USA solo hace falta sumar BrazilAdapter / USAAdapter al
        # registry y todo lo de abajo funciona sin tocar este archivo.
        from agents.elite_report.country_adapters import get_adapter
        _adapter = get_adapter(bundle.country_code)

        # Matriz normativa (cap 2)
        matrix_norm_data = {"rows": _adapter.legal_framework_rows()}

        # ── Radar 8 dimensiones PEIRS (Cap 10) — auditoria 9-may-2026 (G1) ──
        # Antes: 8 valores hardcoded (55, 72, 28, 58, 50, 35, 60, 62) que NO
        # cambiaban entre informes. Riesgo credibilidad.
        # Ahora: heuristica documentada en el comentario original — valor de
        # cada dimension = max(0, 100 - sum(severity_weight de findings en
        # categorias de esa dimension)). Periodo limpio -> ~100, periodo con
        # criticos concentrados -> baja drasticamente.
        from agents.elite_report.i18n import t as _ti
        _DIM_CATS: Dict[str, List[str]] = {
            "suffrage":    ["voter_suppression"],
            "legal":       ["legal", "irregular_procedure"],
            "emb":         ["logistics", "fraud_allegation", "counting", "irregular_procedure"],
            "media":       ["media", "hate_speech", "disinformation"],
            "finance":     ["campaign_violation"],
            "digital":     ["digital"],
            "justice":     ["judicial"],
            "inclusivity": ["voter_suppression", "security"],
        }
        # La dimensión "Org. electoral" también recoge hallazgos que cuestionen
        # directamente al EMB (JNE/ONPE/RENIEC) aunque estén clasificados como
        # legal/other — así el radar es CONSISTENTE con el semáforo institucional,
        # que detecta los órganos por keyword (ver _ORGAN_KW más abajo).
        _EMB_ORGAN_KW = [
            "jne", "jurado nacional", "jurado electoral", "onpe", "oficina nacional",
            "reniec", "registro nacional", "organismo electoral", "autoridad electoral",
        ]
        _SEV_WEIGHTS = {"critical": 12, "high": 6, "medium": 2, "low": 0.5, "info": 0}

        def _dim_matches(f, dim_id: str, cats: List[str]) -> bool:
            if (f.category or "").lower() in cats:
                return True
            if dim_id == "emb":
                txt = ((f.finding or "") + " " + (f.source_name or "")).lower()
                return any(k in txt for k in _EMB_ORGAN_KW)
            return False

        _radar_dims = []
        for _dim_id, _cats in _DIM_CATS.items():
            _weighted = sum(
                _SEV_WEIGHTS.get((f.severity or "info").lower(), 0)
                for f in bundle.hunter_entries
                if _dim_matches(f, _dim_id, _cats)
            )
            _value = max(0, min(100, round(100 - _weighted)))
            _radar_dims.append({
                "label": _ti(language, f"viz.dim.{_dim_id}"),
                "value": _value,
            })
        radar_data = {"dimensions": _radar_dims}

        # ── Semaforo institucional (Cap 10) — auditoria 9-may-2026 (G2) ────
        # Antes: status hardcoded JNE=amber/ONPE=red/RENIEC=green/global=amber
        # con notes fijas. NO respondia al corpus del Hunter.
        # Ahora: cuenta findings por organo (match keyword en finding/source),
        # status derivado de la severidad maxima observada en el periodo.
        # Notes via i18n trilingue.
        from collections import Counter as _Counter
        _ORGAN_KW: Dict[str, List[str]] = {
            # NOTA: estos keywords son PER-especificos. Sprint 2 (CountryAdapter)
            # los va a abstraer a un adapter por pais.
            "JNE":    ["jne", "jurado nacional", "jurado electoral"],
            "ONPE":   ["onpe", "oficina nacional"],
            "RENIEC": ["reniec", "registro nacional"],
        }

        def _compute_organ(label: str, kws: List[str]) -> Dict[str, Any]:
            kws_lo = [k.lower() for k in kws]
            organ_findings = [
                f for f in bundle.hunter_entries
                if any(k in ((f.finding or "") + " " + (f.source_name or "")).lower()
                       for k in kws_lo)
            ]
            sev = _Counter((f.severity or "info").lower() for f in organ_findings)
            crit, high, med = sev.get("critical", 0), sev.get("high", 0), sev.get("medium", 0)
            if not organ_findings:
                status, note_key = "green", "semaphore.note.no_data"
            elif crit >= 1:
                status, note_key = "red", "semaphore.note.crisis"
            elif high >= 2:
                status, note_key = "orange", "semaphore.note.high"
            elif high >= 1 or med >= 3:
                status, note_key = "amber", "semaphore.note.tension"
            else:
                status, note_key = "green", "semaphore.note.stable"
            note = _ti(language, note_key)
            counts_suffix = f" ({crit}c/{high}h/{med}m)" if organ_findings else ""
            return {"label": label, "status": status, "note": f"{note}{counts_suffix}"}

        _organs_per = [_compute_organ(lbl, kws) for lbl, kws in _ORGAN_KW.items()]
        # Status global = peor entre los organos
        _status_rank = {"red": 4, "orange": 3, "amber": 2, "green": 1}
        _global_status = max(
            (o["status"] for o in _organs_per),
            key=lambda s: _status_rank.get(s, 0),
            default="green",
        )
        _global_organ = {
            "label": _ti(language, "semaphore.organ.global"),
            "status": _global_status,
            "note": _ti(language, {
                "red":    "semaphore.note.crisis",
                "orange": "semaphore.note.high",
                "amber":  "semaphore.note.tension",
                "green":  "semaphore.note.stable",
            }.get(_global_status, "semaphore.note.stable")),
        }
        semaphore_data = {"organs": _organs_per + [_global_organ]}

        # ── Sprint 5b — Datos derivados del bundle ──────────────────────────

        # Consolidación: un hecho = un hallazgo con todas sus fuentes (dedup de
        # capturas/medios repetidos del mismo evento). Se usa para timelines y
        # Anexo C; stats.total se mantiene sobre el corpus crudo (volumen real).
        consolidated_findings = consolidate_findingrefs(bundle.hunter_entries)

        # Etiqueta de vuelta por fecha (cronología 1ª → 2ª vuelta).
        def _round_of(date_str: str) -> str:
            d = (date_str or "")[:10]
            return "1ª vuelta" if d and d < "2026-05-01" else "2ª vuelta"

        sev_rank = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
        ranked_findings = sorted(
            consolidated_findings,
            key=lambda f: (-sev_rank.get((f.severity or "info").lower(), 0),
                           f.recorded_at or ""),
        )
        # events_timeline (cap 1): eventos críticos/altos, deduplicados y en
        # ORDEN CRONOLÓGICO (1ª → 2ª vuelta), no por severidad.
        _crit = [f for f in consolidated_findings
                 if (f.severity or "").lower() in ("critical", "high")]
        _crit_chrono = sorted(_crit, key=lambda f: f.recorded_at or "")[:12]
        events_timeline_data = {
            "events": [
                {
                    "date": (f.recorded_at or "")[:10],
                    "label": (f.finding or "")[:46],
                    "severity": (f.severity or "info").lower(),
                    "round": _round_of(f.recorded_at),
                }
                for f in _crit_chrono
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

        # progress_chart: % actas procesadas (cap 6) — auditoria 9-may-2026:
        #   Antes era MOCK con 6 puntos hardcoded (12.4%, 38.2%, ..., 95.1%).
        #   Cualquier informe mostraba siempre los mismos numeros. Riesgo
        #   credibilidad si dos informes distintos exhiben identicos %.
        #
        # Ahora: best-effort derivacion desde bundle.hunter_entries que
        # mencionen "% actas" o similar en finding text + timestamp. Si no
        # hay >= 3 puntos coherentes, progress_data.points queda vacio y la
        # viz NO se attachea al capitulo (ver attach_visualizations).
        import re as _re
        _PCT_RE = _re.compile(r"\b(\d{1,3}(?:[.,]\d+)?)\s*%")
        _progress_points = []
        for _f in bundle.hunter_entries:
            _cat = (_f.category or "").lower()
            if _cat not in ("counting", "results"):
                continue
            _text = (_f.finding or "")
            _m = _PCT_RE.search(_text)
            if not _m:
                continue
            try:
                _pct = float(_m.group(1).replace(",", "."))
            except ValueError:
                continue
            if not 0 <= _pct <= 100:
                continue
            _ts = _f.recorded_at
            if not _ts:
                continue
            _progress_points.append({"t": _ts[:16].replace("T", " "), "pct": _pct})
        # Necesitamos al menos 3 puntos coherentes para tener una curva
        # informativa. Si hay menos, el grafico se omite (no se renderiza
        # empty-state porque la viz no se agrega a chapter.visualizations).
        if len(_progress_points) >= 3:
            _progress_points.sort(key=lambda p: p["t"])
            progress_data = {
                "points": _progress_points,
                "current_pct": _progress_points[-1]["pct"],
            }
        else:
            progress_data = {"points": [], "current_pct": None}

        # integrity_incidents_grid: regiones × categorías (cap 6)
        # Sprint 2: regions y parliament data via adapter.
        _regions_data = _adapter.regions_data() or []
        _parliament_payload = _adapter.parliament_scenarios()

        # Verificar si tenemos datos de location en el bundle (campo opcional
        # en FindingRef desde 2026-04-29; antes era None para todos los findings).
        has_locations = any(
            (f.location or "").strip() for f in bundle.hunter_entries
        )

        if _regions_data and has_locations:
            top_regions_per = [r["region"] for r in _regions_data[:8]]
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
        if _regions_data and has_locations:
            for r in _regions_data[:24]:
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

        # actor_network: red de actores (cap 7) — institucional + extra-electoral
        # Sprint 2: data y labels traducidos provistos por country adapter.
        actor_network_data = _adapter.actor_network(language)

        # judicial_timeline: cronología (cap 7) — findings legal/judicial,
        # deduplicados y en ORDEN CRONOLÓGICO 1ª → 2ª vuelta (no por severidad).
        judicial_findings = sorted(
            [f for f in consolidated_findings
             if (f.category or "").lower() in
             ("legal", "fraud_allegation", "irregular_procedure", "judicial")],
            key=lambda f: f.recorded_at or "",
        )[:10]
        judicial_data = {
            "actions": [
                {
                    "date": (f.recorded_at or "")[:10],
                    "actor": (f.source_name or "—")[:24],
                    "action": (f.finding or "")[:80],
                    "severity": (f.severity or "info").lower(),
                    "round": _round_of(f.recorded_at),
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

        # early_warning_meter (cap 9) — auditoria 10-may-2026
        # ANTES: score era magic number {green:0.15, amber:0.40, orange:0.65, red:0.88}
        # asignado por nivel. NO derivado del corpus. Period con 1 critical o 100
        # critical mostraba el mismo 0.88 si caia en "red". No auditable.
        #
        # AHORA: PEIRS Crisis Index — severity-weighted average del corpus.
        # Formula auditable, citable en informes formales:
        #
        #   crisis_index = Σ(SEV_W[severity] × count_by_severity) / total_findings
        #
        #   SEV_W = {critical: 1.00, high: 0.55, medium: 0.20, low: 0.05, info: 0}
        #
        # Range [0, 1]. Mappeo a level:
        #   >= 0.60: red
        #   >= 0.40: orange
        #   >= 0.20: amber
        #   <  0.20: green
        #
        # El NIVEL del medidor (banda resaltada) se deriva del MISMO crisis_index
        # que posiciona la aguja, para que banda + aguja + número sean coherentes
        # entre sí. (Antes el forecast.early_warning_level podía pisar el nivel y
        # mostrar banda verde con aguja casi en rojo.) El nivel del forecast sigue
        # disponible para el capítulo predictivo y su propio gráfico.
        _SEV_W = {"critical": 1.00, "high": 0.55, "medium": 0.20, "low": 0.05, "info": 0.0}
        _by_sev = stats.get("by_severity", {}) or {}
        _total_w = sum(_SEV_W.get(s, 0) * c for s, c in _by_sev.items())
        _total_n = max(sum(_by_sev.values()), 1)
        crisis_index = max(0.0, min(1.0, _total_w / _total_n))

        if crisis_index >= 0.60:   level = "red"
        elif crisis_index >= 0.40: level = "orange"
        elif crisis_index >= 0.20: level = "amber"
        else:                      level = "green"

        # Drivers: top categorías
        top_drivers = [c for c, _ in all_cats.most_common(3)]

        early_warning_data = {
            "level": level,
            "score": round(crisis_index, 3),
            "label": _adapter.early_warning_label(level, language),
            "drivers": top_drivers,
        }

        # matrix_recommendations (cap 11)
        recommendations_data = _adapter.recommendations(language)

        # system_architecture (cap 12)
        architecture_data = _adapter.architecture(language)

        # network_institutions (cap 3)
        network_inst_data = _adapter.network_institutions(language)

        # flow_chart_voting (cap 3)
        flow_voting_data = _adapter.flow_voting_stages(language)

        # parliament_scenarios (cap 9) — opcional, segun adapter
        parliament_data: Optional[Dict[str, Any]] = _parliament_payload

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
                # Solo emitir progress_chart si hay puntos derivados reales (>=3)
                # del Hunter. Sin data real, omitimos la viz: no mostramos mock
                # ni un empty-state generico (ver construccion arriba).
                if progress_data["points"]:
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
            elif ch.chapter_id == "conclusiones":
                ch.visualizations.append(_vs("semaphore_institutional", semaphore_data))
                ch.visualizations.append(_vs("dimensions_radar", radar_data))
                # Medidor de alerta temprana reubicado aquí (antes vivía en el
                # capítulo predictivo, ya eliminado). Es un ÍNDICE DE SEVERIDAD
                # del período observado, NO un pronóstico.
                ch.visualizations.append(_vs("early_warning_meter", early_warning_data))
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
