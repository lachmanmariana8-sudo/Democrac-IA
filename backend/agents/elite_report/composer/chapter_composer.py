"""
ChapterComposer — orquesta la generación de los 12 capítulos del Elite Report
con Claude, usando prompt caching para eficiencia y concurrency limitada.

Pipeline:
1. Lee los prompts desde backend/agents/elite_report/composer/prompts/
2. Construye el system prompt con el base_context.md rellenado con data real
3. Para cada capítulo, arma su user prompt con datos específicos
4. Ejecuta en concurrency=4 con 2 reintentos por fallo
5. Devuelve {chapter_id: narrative} con fallback a template si falla

El system prompt base se construye UNA VEZ y se reusa en 12 llamadas
(aprovechando prompt caching de Anthropic si está disponible).

Audiencias soportadas:
- institutional: 800 words por capítulo, tono académico formal
- executive: 300 words, bullets, accionable
- press: 200 words, frases cortas, cita textual destacada
- international: inglés, marco comparado con OEA/EU EOM/Carter Center
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.elite_report.models import (
    EliteReportRequest,
    EliteChapter,
    FindingRef,
    ForecastPayload,
    HistoricalSeries,
    PhaseEvidence,
    CrossReference,
)


# Metadata de los 12 capítulos (+ declaración preliminar como cap. -2)
CHAPTER_CATALOG: List[Dict[str, Any]] = [
    {"number": -2, "chapter_id": "declaracion_preliminar",
     "title": "Declaración preliminar",
     "prompt_file": "cap_00_declaracion.md", "max_words": 400},
    {"number": 1, "chapter_id": "contexto_historico",
     "title": "Contexto histórico",
     "prompt_file": "cap_01_contexto_historico.md", "max_words": 700},
    {"number": 2, "chapter_id": "marco_juridico",
     "title": "Marco jurídico aplicable",
     "prompt_file": "cap_02_marco_juridico.md", "max_words": 800},
    {"number": 3, "chapter_id": "sistema_electoral",
     "title": "Sistema electoral",
     "prompt_file": "cap_03_sistema_electoral.md", "max_words": 800},
    {"number": 4, "chapter_id": "fase_pre_electoral",
     "title": "Fase pre-electoral",
     "prompt_file": "cap_04_fase_pre_electoral.md", "max_words": 900},
    {"number": 5, "chapter_id": "jornada_electoral",
     "title": "Jornada electoral",
     "prompt_file": "cap_05_jornada_electoral.md", "max_words": 1000},
    {"number": 6, "chapter_id": "escrutinio_computo",
     "title": "Escrutinio y cómputo",
     "prompt_file": "cap_06_escrutinio_computo.md", "max_words": 900},
    {"number": 7, "chapter_id": "post_electoral",
     "title": "Post-electoral",
     "prompt_file": "cap_07_post_electoral.md", "max_words": 1000},
    {"number": 8, "chapter_id": "derechos_vulnerados",
     "title": "Derechos vulnerados",
     "prompt_file": "cap_08_derechos_vulnerados.md", "max_words": 900},
    {"number": 9, "chapter_id": "analisis_predictivo",
     "title": "Análisis predictivo",
     "prompt_file": "cap_09_analisis_predictivo.md", "max_words": 1000},
    {"number": 10, "chapter_id": "conclusiones",
     "title": "Conclusiones",
     "prompt_file": "cap_10_conclusiones.md", "max_words": 900},
    {"number": 11, "chapter_id": "recomendaciones",
     "title": "Recomendaciones",
     "prompt_file": "cap_11_recomendaciones.md", "max_words": 900},
    {"number": 12, "chapter_id": "ia_regulacion",
     "title": "Inteligencia Artificial en el proceso electoral",
     "prompt_file": "cap_12_ia_regulacion.md", "max_words": 1000},
]


AUDIENCE_DESC = {
    "institutional": "Jefaturas de misión de observación, órganos electorales, academia jurídica. Tono académico formal. Densidad informativa alta.",
    "executive": "Decisores ejecutivos, embajadores, jefaturas institucionales. Tono accionable. Bullets preferidos. Máximo 300 palabras por capítulo.",
    "press": "Periodistas especializados. Frases cortas declarativas. Sin jerga. Cita textual destacada. Máximo 200 palabras por capítulo.",
    "international": "Observadores internacionales (OEA, EU EOM, Carter Center). English. Marco comparado con estándares internacionales. Formal academic tone.",
}

LANGUAGE_FULL = {"es": "Español (rioplatense-peruano formal)", "en": "English (formal academic)"}
LANGUAGE_RULE = {
    "es": "Respondé en español formal, registro institucional peruano.",
    "en": "Respond in formal academic English.",
}


class ChapterComposer:
    """Genera los 12 capítulos con Claude."""

    def __init__(self, llm=None, concurrency_limit: int = 4, retries: int = 2):
        self.llm = llm
        self.concurrency_limit = concurrency_limit
        self.retries = retries
        self._prompts_dir = Path(__file__).parent / "prompts"
        self._base_context_template = self._load_prompt_file("base_context.md")

    # ── Utilitarios de carga ────────────────────────────────────────────
    def _load_prompt_file(self, filename: str) -> str:
        p = self._prompts_dir / filename
        if not p.exists():
            return ""
        return p.read_text(encoding="utf-8")

    # ── Formateo del contexto compartido ────────────────────────────────
    def _build_shared_context(
        self,
        req: EliteReportRequest,
        hunter_entries: List[FindingRef],
        theme_ranking: List[Dict[str, Any]],
        phase_evidence: Dict[str, PhaseEvidence],
        rag_docs: List[Dict[str, Any]],
        historical_series: List[HistoricalSeries],
        forecast: Optional[ForecastPayload],
        stats: Dict[str, Any],
        sources_list: List[str],
        alerts_dispatched: int,
        country_name: str = "Perú",
    ) -> str:
        """Rellena base_context.md con la evidencia del bundle."""
        ctx = self._base_context_template

        # Sustituciones simples
        replacements = {
            "{country_code}": req.country_code,
            "{country_name}": country_name,
            "{mission_name}": req.mission_metadata.mission_name,
            "{lead_observer}": req.mission_metadata.lead_observer,
            "{period_start}": req.mission_metadata.period_start,
            "{period_end}": req.mission_metadata.period_end,
            "{jornada_date}": req.mission_metadata.jornada_date,
            "{report_type}": req.report_type,
            "{audience}": req.audience,
            "{audience_description}": AUDIENCE_DESC.get(req.audience, AUDIENCE_DESC["institutional"]),
            "{language_full}": LANGUAGE_FULL.get(req.language, "Español"),
            "{language_rule}": LANGUAGE_RULE.get(req.language, LANGUAGE_RULE["es"]),
            "{classification}": req.mission_metadata.classification,
            "{total_findings}": str(stats.get("total", len(hunter_entries))),
            "{sev_dist}": self._format_sev_dist(stats),
            "{days_covered}": str(stats.get("days_covered", "—")),
            "{sources_list}": ", ".join(sources_list[:8]) or "—",
            "{alerts_dispatched}": str(alerts_dispatched),
            "{theme_ranking_formatted}": self._format_themes(theme_ranking),
            "{top_findings_formatted}": self._format_top_findings(hunter_entries[:20]),
            "{phase_evidence_formatted}": self._format_phase_evidence(phase_evidence),
            "{rag_extracts_formatted}": self._format_rag(rag_docs[:10]),
            "{historical_series_formatted}": self._format_series(historical_series),
            "{vdem_emb_quant_formatted}": self._format_vdem_emb(req.country_code),
            "{forecast_formatted}": self._format_forecast(forecast),
        }
        for k, v in replacements.items():
            ctx = ctx.replace(k, v)
        return ctx

    @staticmethod
    def _format_vdem_emb(country_code: str, last_n: int = 5) -> str:
        """Indicadores V-Dem cuantitativos del EMB y estado de derecho — para que
        el cap. 3 y otros puedan citar valores específicos en lugar de descripciones
        cualitativas vacías. Lee desde VDEM_STATIC (38 paises x 1985-2025).

        Indicadores incluidos:
          - v2elembaut: autonomía órganos electorales (escala -3 a +3, mas alto = mas autonomía)
          - v2elembcap: capacidad órganos electorales (escala -3 a +3)
          - v2elirreg: irregularidades electorales (escala -3 a +3, mas BAJO = menos irregularidades)
          - v2elintim: intimidación electoral (escala -3 a +3)
          - v2xcl_rol: estado de derecho (rango 0-1)
          - v2jureview: revisión judicial (escala -3 a +3)
        """
        try:
            from modules.vdem_static import VDEM_STATIC
        except Exception:
            return "(V-Dem static no disponible)"

        country = VDEM_STATIC.get(country_code, {})
        if not country:
            return f"(V-Dem sin datos para {country_code})"

        years = sorted(country.keys(), key=int)
        if not years:
            return f"(V-Dem sin años para {country_code})"

        latest_year = years[-1]
        latest = country[latest_year]
        # Indicadores que vamos a citar en cap 3.1 y cap 3.4
        ind_meta = [
            ("v2elembaut",      "Autonomía EMB",         "−3 a +3, mayor = más autónomo"),
            ("v2elembcap",      "Capacidad EMB",         "−3 a +3, mayor = más capaz"),
            ("v2elirreg",       "Irregularidades elect.", "−3 a +3, menor = menos irregularidades"),
            ("v2elintim",       "Intimidación electoral", "−3 a +3, menor = menos intimidación"),
            ("v2xcl_rol",       "Estado de derecho",     "0 a 1, mayor = más rule of law"),
            ("v2jureview",      "Revisión judicial",     "−3 a +3, mayor = más independencia judicial"),
        ]

        lines = [f"**Valores actuales V-Dem v16 para {country_code} ({latest_year}):**\n"]
        for code, label, scale in ind_meta:
            v = latest.get(code)
            if v is None:
                lines.append(f"- {label} (`{code}`): N/D ({scale})")
            else:
                lines.append(f"- {label} (`{code}`): **{v:.3f}** ({scale})")

        # Tendencia últimos N años para los 4 EMB-críticos
        trend_codes = ["v2elembaut", "v2elembcap", "v2elirreg", "v2elintim"]
        trend_years = years[-last_n:] if len(years) >= last_n else years
        if len(trend_years) >= 2:
            lines.append(f"\n**Tendencia últimos {len(trend_years)} años:**\n")
            for code in trend_codes:
                values = []
                for y in trend_years:
                    block = country.get(y, {})
                    val = block.get(code)
                    if val is not None:
                        values.append(f"{y}={val:.2f}")
                    else:
                        values.append(f"{y}=N/D")
                lines.append(f"- `{code}`: {' → '.join(values)}")

        return "\n".join(lines)

    @staticmethod
    def _format_sev_dist(stats: Dict[str, Any]) -> str:
        parts = []
        for sev in ("critical", "high", "medium", "low", "info"):
            n = stats.get(sev, 0)
            if n:
                parts.append(f"{n} {sev}")
        return " · ".join(parts) or "—"

    @staticmethod
    def _format_themes(theme_ranking: List[Dict[str, Any]]) -> str:
        if not theme_ranking:
            return "(Sin temas clasificados disponibles.)"
        lines = []
        for i, t in enumerate(theme_ranking[:8]):
            label = t.get("label") or t.get("theme_id", "sin-etiqueta")
            total = t.get("total", 0)
            hc = t.get("high_critical", 0)
            lines.append(f"  {i+1}. **{label}**: {total} hallazgos ({hc} high/critical)")
        return "\n".join(lines)

    @staticmethod
    def _format_top_findings(findings: List[FindingRef]) -> str:
        if not findings:
            return "(Sin hallazgos priorizados.)"
        lines = []
        for i, f in enumerate(findings):
            text = (f.finding or "")[:200]
            src = f.source_name or "sin-fuente"
            url = f.source_url or ""
            date = (f.recorded_at or "")[:10]
            sev = f.severity or "info"
            cat = f.category or "other"
            lines.append(
                f"  [{i+1}] [{sev}] [{cat}] {date} | {src}: {text}"
                + (f" | URL: {url}" if url else "")
            )
        return "\n".join(lines)

    @staticmethod
    def _format_phase_evidence(phase_evidence: Dict[str, PhaseEvidence]) -> str:
        if not phase_evidence:
            return "(Sin evidencia por fase disponible.)"
        lines = []
        for phase_id, pe in phase_evidence.items():
            lines.append(
                f"  - **{pe.phase_label}** ({phase_id}): "
                f"{pe.total_count} hallazgos · "
                f"{pe.critical_count} critical · {pe.high_count} high · "
                f"temas dominantes: {', '.join(pe.dominant_themes) or '—'}"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_rag(rag_docs: List[Dict[str, Any]]) -> str:
        if not rag_docs:
            return "(Sin corpus normativo cargado.)"
        lines = []
        for d in rag_docs:
            title = d.get("title", "sin título")
            instrument = d.get("instrument", "—")
            # Primeras 400 chars del text
            text = (d.get("text") or "")[:400].replace("\n", " ")
            lines.append(f"  - [{instrument}] **{title}**: {text}…")
        return "\n".join(lines)

    @staticmethod
    def _format_series(series: List[HistoricalSeries]) -> str:
        if not series:
            return "(Sin datasets estructurales disponibles.)"
        lines = []
        for s in series:
            pts = s.datapoints
            if not pts:
                continue
            first, last = pts[0], pts[-1]
            lines.append(
                f"  - **{s.indicator_label}** ({s.source}): "
                f"{first.year}→{last.year}: {first.value}→{last.value} "
                f"[{s.trend_direction}] — {s.trend_note}"
            )
        return "\n".join(lines) or "(Series no disponibles.)"

    @staticmethod
    def _format_forecast(forecast: Optional[ForecastPayload]) -> str:
        if not forecast or not forecast.scenarios:
            return "(Motor predictivo no habilitado o sin escenarios activos.)"
        lines = [
            f"**Patrón dominante:** {forecast.dominant_pattern}",
            f"**Nivel de alerta:** {forecast.early_warning_level.upper()} — {forecast.early_warning_note}",
            "",
            "**Escenarios activos:**",
        ]
        for s in forecast.scenarios:
            ci = ""
            if s.confidence_interval:
                ci = f" (IC: {s.confidence_interval[0]*100:.0f}–{s.confidence_interval[1]*100:.0f}%)"
            lines.append(
                f"  - **{s.label}**: {s.probability*100:.0f}%{ci} | "
                f"Base normativa: {s.legal_basis or '—'} | "
                f"Implicaciones: {s.implications[:200]}"
            )
        return "\n".join(lines)

    # ── Composición de un capítulo ──────────────────────────────────────
    async def _compose_chapter(
        self,
        chapter_meta: Dict[str, Any],
        shared_context: str,
        req: EliteReportRequest,
    ) -> EliteChapter:
        """Genera la narrativa de UN capítulo con reintentos."""
        prompt_file = chapter_meta["prompt_file"]
        user_prompt = self._load_prompt_file(prompt_file)
        if not user_prompt:
            # Fallback: capítulo vacío con warning
            return EliteChapter(
                number=chapter_meta["number"],
                chapter_id=chapter_meta["chapter_id"],
                title=chapter_meta["title"],
                narrative="",
                warnings=[f"Prompt file no encontrado: {prompt_file}"],
            )

        if self.llm is None:
            return EliteChapter(
                number=chapter_meta["number"],
                chapter_id=chapter_meta["chapter_id"],
                title=chapter_meta["title"],
                narrative="",
                warnings=["LLM no configurado — capítulo generado vacío."],
            )

        # Intentar hasta self.retries+1 veces
        from langchain_core.messages import HumanMessage, SystemMessage

        last_error = None
        for attempt in range(self.retries + 1):
            try:
                response = await self.llm.ainvoke([
                    SystemMessage(content=shared_context),
                    HumanMessage(content=user_prompt),
                ])
                text = response.content.strip() if hasattr(response, "content") else str(response)

                # Limpiar heading de nivel 1 si Claude lo incluyó
                if text.startswith("# ") or text.startswith("## "):
                    # Solo eliminar si es el título esperado del capítulo
                    first_line = text.split("\n", 1)[0]
                    if any(kw in first_line.lower() for kw in chapter_meta["chapter_id"].lower().split("_")):
                        text = text.split("\n", 1)[1].strip() if "\n" in text else ""

                word_count = len(text.split())
                tokens = {}
                if hasattr(response, "response_metadata"):
                    usage = response.response_metadata.get("usage", {})
                    tokens = {
                        "input": usage.get("input_tokens", 0),
                        "output": usage.get("output_tokens", 0),
                    }

                return EliteChapter(
                    number=chapter_meta["number"],
                    chapter_id=chapter_meta["chapter_id"],
                    title=chapter_meta["title"],
                    narrative=text,
                    word_count=word_count,
                    tokens_used=tokens,
                )
            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e)[:200]}"
                if attempt < self.retries:
                    await asyncio.sleep(2 ** attempt)  # backoff exponencial
                    continue

        return EliteChapter(
            number=chapter_meta["number"],
            chapter_id=chapter_meta["chapter_id"],
            title=chapter_meta["title"],
            narrative="",
            warnings=[f"Falló tras {self.retries+1} intentos: {last_error}"],
        )

    # ── Orquestador principal ──────────────────────────────────────────
    async def compose_all(
        self,
        req: EliteReportRequest,
        hunter_entries: List[FindingRef],
        theme_ranking: List[Dict[str, Any]],
        phase_evidence: Dict[str, PhaseEvidence],
        rag_docs: List[Dict[str, Any]],
        historical_series: List[HistoricalSeries],
        forecast: Optional[ForecastPayload],
        stats: Dict[str, Any],
        sources_list: List[str],
        alerts_dispatched: int,
        cross_references: Optional[List[CrossReference]] = None,
        country_name: str = "Perú",
        filter_chapters: Optional[List[int]] = None,
    ) -> List[EliteChapter]:
        """Genera los 12 capítulos (o el subset solicitado) en paralelo."""
        # Filtrar capítulos según request
        catalog = CHAPTER_CATALOG
        if filter_chapters:
            catalog = [c for c in catalog if c["number"] in filter_chapters]

        # Armar contexto compartido UNA vez
        shared_context = self._build_shared_context(
            req=req,
            hunter_entries=hunter_entries,
            theme_ranking=theme_ranking,
            phase_evidence=phase_evidence,
            rag_docs=rag_docs,
            historical_series=historical_series,
            forecast=forecast,
            stats=stats,
            sources_list=sources_list,
            alerts_dispatched=alerts_dispatched,
            country_name=country_name,
        )

        # Generar con concurrency limit
        sem = asyncio.Semaphore(self.concurrency_limit)

        async def _gen_one(meta: Dict[str, Any]) -> EliteChapter:
            async with sem:
                return await self._compose_chapter(meta, shared_context, req)

        results = await asyncio.gather(
            *[_gen_one(c) for c in catalog],
            return_exceptions=True,
        )

        out: List[EliteChapter] = []
        for r in results:
            if isinstance(r, Exception):
                continue
            out.append(r)

        # Ordenar por number
        out.sort(key=lambda c: c.number)
        return out
