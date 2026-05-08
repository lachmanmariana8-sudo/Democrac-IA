"""
ReportDesigner — Fase A (esqueleto funcional).

Pipeline de 3 pasos (Structurer → Visualizer → Composer) implementado con mocks
que devuelven datos deterministas basados en el informe v1.1 ya entregado.
Permite validar el loop end-to-end antes de implementar la lógica real (Fases B-E).

Uso:
    from agents.report_designer import ReportDesigner, ReportRequest
    designer = ReportDesigner()
    req = ReportRequest(country_code="PER", audience="executive")
    result = await designer.run(req)
    # result.markdown, result.html, result.stats, ...
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from agents.report_designer.models import (
    ReportRequest, ReportOutput, ReportSection, ReportStats,
    FindingRef, VizSpec, SourceCitation,
)
from agents.report_designer.structurer import Structurer, THEMES
from agents.report_designer import visualizer as viz_renderer


REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports", "designed")


class ReportDesigner:
    """
    Pipeline de composición de informes (Fase A — esqueleto).

    Los 3 pasos se implementan como métodos privados. En Fase A devuelven data
    determinista; en Fases B-E se reemplazan con lógica real.
    """

    def __init__(self, llm=None, observation_store=None, alerts_loader=None, reports_store=None):
        """
        Args:
            llm: instancia de Claude (Fase C reemplazará templates por narrativas LLM)
            observation_store: dict {cc: session} del backend con entries del Hunter
            alerts_loader: callable(cc, limit) -> list de alertas
            reports_store: dict {run_id: report} con datasets estructurales
        """
        self.llm = llm
        self._observation_store = observation_store
        self._alerts_loader = alerts_loader
        self._reports_store = reports_store

    async def run(self, req: ReportRequest) -> ReportOutput:
        """Ejecuta el pipeline completo: Structurer (B) + Visualizer (D) + Composer (C opt-in).
        Si use_llm=False: plantillas con data real (rápido, gratis). Si True: Claude redacta."""
        report_id = str(uuid.uuid4())[:12]
        now = datetime.now(timezone.utc).isoformat()

        # Paso 1 — Structurer (Fase B: lógica real sobre stores del backend)
        skeleton = self._structurer_real(req)

        # Paso 2 — Visualizer (Fase D: SVG real)
        skeleton = self._visualizer_mock(skeleton, req)

        # Paso 3 — Composer
        output = self._composer_mock(skeleton, req, report_id, now)

        # Paso 3b — Fase C: si use_llm=True, reemplazar plantillas por narrativas de Claude
        if req.use_llm and self.llm is not None:
            await self._enrich_with_llm(output, skeleton, req)

        # Re-render markdown y HTML si se enriqueció con LLM
        if req.use_llm and self.llm is not None:
            output.markdown = self._render_markdown(output.sections, output.stats, req)
            output.html = self._render_html(output.sections, output.stats, req)

        # Persistencia
        self._persist_mock(output, req)

        return output

    async def _enrich_with_llm(self, output: ReportOutput, skeleton: Dict[str, Any],
                                req: ReportRequest) -> None:
        """Fase C: reemplaza narrativas de plantilla por generadas por Claude."""
        try:
            from agents.report_designer.composer import compose_all_sections
        except ImportError as e:
            output.warnings.append(f"Composer LLM no disponible: {e}")
            return

        country_ctx = ""
        if req.country_code.upper() == "PER":
            country_ctx = (
                "Perú atraviesa inestabilidad institucional crónica (6 presidentes en 4 años, "
                "2020-2024). Elecciones Generales 2026 introducen bicameralidad y doble valla. "
                "El sistema electoral es tripartito: JNE (justicia electoral, Art. 178 Const.), "
                "ONPE (organización, Art. 183), RENIEC (padrón). Voto electrónico VENP rechazado "
                "por Res. JNE 0891-2025 por ausencia de auditoría certificada. "
                "STAE (sistema tecnológico de apoyo al escrutinio con IA) desplegado en Lima y "
                "Callao sin el mismo estándar de auditoría aplicado."
            )

        try:
            narratives = await compose_all_sections(
                llm=self.llm,
                sections=output.sections,
                req=req,
                stats=output.stats,
                theme_ranking=skeleton.get("theme_ranking", []),
                top_findings_overall=skeleton.get("top_findings_overall", []),
                country_context=country_ctx,
                concurrency_limit=3,
            )
        except Exception as e:
            output.warnings.append(f"Fallo Composer LLM: {type(e).__name__}: {e}")
            return

        enriched_count = 0
        for section in output.sections:
            if section.section_id in narratives and narratives[section.section_id]:
                section.narrative = narratives[section.section_id]
                enriched_count += 1

        output.warnings = [
            w for w in output.warnings if "Fases B+D" not in w
        ]
        output.warnings.append(
            f"Fase C activa: {enriched_count}/{len(output.sections)} secciones "
            f"enriquecidas con Claude. Las secciones sin enriquecer mantienen plantilla Fase B."
        )

    # ────────────────────────────────────────────────────────────────────
    # Paso 1: Structurer (Fase B — real)
    # ────────────────────────────────────────────────────────────────────
    def _structurer_real(self, req: ReportRequest) -> Dict[str, Any]:
        """Structurer real: carga de stores + dedupe + temas + priorización + buckets."""
        s = Structurer(req.country_code)
        s.load_from_stores(
            observation_store=self._observation_store,
            alerts_loader=self._alerts_loader,
            reports_store=self._reports_store,
        )
        data = s.run()

        # Si no hay datos reales (caso países distintos a PER), fallback a mock Fase A
        if data["stats"]["total_findings"] == 0:
            return self._structurer_mock(req)

        stats = ReportStats(
            total_findings=data["stats"]["total_findings"],
            critical=data["stats"]["critical"],
            high=data["stats"]["high"],
            medium=data["stats"]["medium"],
            low=data["stats"]["low"],
            info=data["stats"]["info"],
            days_covered=data["stats"]["days_covered"],
            sources_count=data["stats"]["sources_count"],
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        # Sources: construimos dinámicamente desde las fuentes encontradas
        SOURCE_URLS = {
            "andina": "https://andina.pe", "elcomercio": "https://elcomercio.pe",
            "gestion": "https://gestion.pe", "idl": "https://idl-reporteros.pe",
            "rpp": "https://rpp.pe", "wayka": "https://wayka.pe",
            "jne": "https://jne.gob.pe", "onpe": "https://onpe.gob.pe",
            "ooni": "https://ooni.org",
        }
        sources = []
        for src_key in data["source_distribution"]:
            if src_key in SOURCE_URLS:
                sources.append(SourceCitation(kind="rss", label=src_key.title(), url=SOURCE_URLS[src_key]))
        # Legal framework (siempre presente para Perú)
        if req.country_code.upper() == "PER":
            sources.extend([
                SourceCitation(kind="legal_instrument", label="Constitución Perú 1993 Arts. 176-187"),
                SourceCitation(kind="legal_instrument", label="LOE N° 26859 Arts. 190/191/351/358/363"),
                SourceCitation(kind="legal_instrument", label="LOP N° 28094 + Ley 31030 (paridad)"),
                SourceCitation(kind="legal_instrument", label="ICCPR Art. 25"),
                SourceCitation(kind="legal_instrument", label="CADH Art. 23"),
                SourceCitation(kind="legal_instrument", label="Carta Democrática Interamericana Art. 3"),
                SourceCitation(kind="case_law", label="Res. JNE 0891-2025-JNE (rechazo VENP)"),
            ])

        # Secciones según audiencia
        template_for_audience = {
            "technical": ["portada", "resumen_ejecutivo", "metodologia", "cifras_clave",
                         "contexto", "timeline_hallazgos", "temas_criticos",
                         "derechos_vulnerados", "responsabilidad_penal", "recomendaciones",
                         "anexo_fuentes"],
            "executive": ["portada", "declaracion_1_pagina", "cifras_clave",
                         "3_temas_mas_criticos", "recomendaciones_prioritarias"],
            "press": ["titulo", "bajada", "infografia_unica", "3_hallazgos_mas_cita"],
            "international": ["cover", "executive_summary", "context_comparative",
                            "findings", "rights_framework", "recommendations",
                            "methodology", "references"],
        }
        section_ids = template_for_audience.get(req.audience, template_for_audience["technical"])

        sections = []
        for i, sid in enumerate(section_ids):
            sec = ReportSection(
                section_id=sid,
                title=self._title_for(sid, req.language),
                narrative="",
                findings=[],
                viz_specs=[],
                order=i,
            )

            # Asignar hallazgos reales a cada sección según afinidad temática
            if sid in ("temas_criticos", "3_temas_mas_criticos", "findings"):
                # Top hallazgos de los top 3 temas
                for theme in data["theme_ranking"][:3]:
                    sec.findings.extend(theme["top_findings"])
            elif sid in ("responsabilidad_penal",):
                # Hallazgos del tema responsabilidad_penal
                for theme in data["theme_ranking"]:
                    if theme["theme_id"] == "responsabilidad_penal":
                        sec.findings.extend(theme["top_findings"])
                        break
            elif sid in ("timeline_hallazgos",):
                # Top 10 global
                sec.findings.extend(data["top_findings_overall"][:10])
            elif sid in ("3_hallazgos_mas_cita", "bajada"):
                sec.findings.extend(data["top_findings_overall"][:3])

            sections.append(sec)

        return {
            "sections": sections,
            "stats": stats,
            "sources": sources,
            "theme_ranking": data["theme_ranking"],
            "timeline": data["timeline"],
            "source_distribution": data["source_distribution"],
            "top_findings_overall": data["top_findings_overall"],
        }

    # ────────────────────────────────────────────────────────────────────
    # Paso 1: Structurer (mock Fase A)
    # ────────────────────────────────────────────────────────────────────
    def _structurer_mock(self, req: ReportRequest) -> Dict[str, Any]:
        """Devuelve un esqueleto con secciones y stats mockeados para PER."""
        # Stats de ejemplo basadas en el informe v1.1 real
        if req.country_code.upper() == "PER":
            stats = ReportStats(
                total_findings=838,
                critical=7,
                high=107,
                medium=303,
                low=124,
                info=297,
                days_covered=8,
                sources_count=5,
                generated_at=datetime.now(timezone.utc).isoformat(),
            )
            sources = [
                SourceCitation(kind="rss", label="IDL-Reporteros", url="https://idl-reporteros.pe"),
                SourceCitation(kind="rss", label="El Comercio", url="https://elcomercio.pe"),
                SourceCitation(kind="rss", label="Gestión", url="https://gestion.pe"),
                SourceCitation(kind="rss", label="RPP Noticias", url="https://rpp.pe"),
                SourceCitation(kind="rss", label="Andina", url="https://andina.pe"),
                SourceCitation(kind="legal_instrument", label="ICCPR Art. 25"),
                SourceCitation(kind="legal_instrument", label="CADH Art. 23"),
                SourceCitation(kind="legal_instrument", label="LOE Art. 190/191/351/363"),
                SourceCitation(kind="legal_instrument", label="Constitución Perú 1993 Art. 176"),
                SourceCitation(kind="case_law", label="Res. JNE 0891-2025-JNE (rechazo VENP)"),
            ]
        else:
            stats = ReportStats(
                total_findings=0, critical=0, high=0, medium=0, low=0, info=0,
                days_covered=0, sources_count=0,
                generated_at=datetime.now(timezone.utc).isoformat(),
            )
            sources = []

        template_for_audience = {
            "technical": ["portada", "resumen_ejecutivo", "metodologia", "cifras_clave",
                         "contexto", "timeline_hallazgos", "temas_criticos",
                         "derechos_vulnerados", "responsabilidad_penal", "recomendaciones",
                         "anexo_fuentes"],
            "executive": ["portada", "declaracion_1_pagina", "cifras_clave",
                         "3_temas_mas_criticos", "recomendaciones_prioritarias"],
            "press": ["titulo", "bajada", "infografia_unica", "3_hallazgos_mas_cita"],
            "international": ["cover", "executive_summary", "context_comparative",
                            "findings", "rights_framework", "recommendations",
                            "methodology", "references"],
        }
        section_ids = template_for_audience.get(req.audience, template_for_audience["technical"])

        sections = []
        for i, sid in enumerate(section_ids):
            sections.append(ReportSection(
                section_id=sid,
                title=self._title_for(sid, req.language),
                narrative="",  # vacío, el Composer lo llena
                findings=[],
                viz_specs=[],
                order=i,
            ))

        return {
            "sections": sections,
            "stats": stats,
            "sources": sources,
        }

    def _title_for(self, section_id: str, language: str) -> str:
        titles_es = {
            "portada": "Portada",
            "resumen_ejecutivo": "1. Resumen ejecutivo",
            "declaracion_1_pagina": "Declaración preliminar",
            "metodologia": "2. Metodología",
            "cifras_clave": "3. Cifras clave",
            "contexto": "4. Contexto del proceso",
            "timeline_hallazgos": "5. Timeline de hallazgos",
            "temas_criticos": "6. Temas críticos",
            "3_temas_mas_criticos": "3 temas más críticos",
            "derechos_vulnerados": "7. Derechos vulnerados",
            "responsabilidad_penal": "8. Responsabilidad penal e institucional",
            "recomendaciones": "9. Recomendaciones",
            "recomendaciones_prioritarias": "Recomendaciones prioritarias",
            "titulo": "Título",
            "bajada": "Bajada",
            "infografia_unica": "Infografía principal",
            "3_hallazgos_mas_cita": "Tres hallazgos más citados",
            "anexo_fuentes": "Anexo: Fuentes",
        }
        titles_en = {
            "cover": "Cover",
            "executive_summary": "Executive summary",
            "context_comparative": "Comparative context",
            "findings": "Findings",
            "rights_framework": "Human rights framework",
            "recommendations": "Recommendations",
            "methodology": "Methodology",
            "references": "References",
        }
        if language == "en":
            return titles_en.get(section_id, section_id.replace("_", " ").title())
        return titles_es.get(section_id, section_id.replace("_", " ").title())

    # ────────────────────────────────────────────────────────────────────
    # Paso 2: Visualizer (mock Fase A)
    # ────────────────────────────────────────────────────────────────────
    def _visualizer_mock(self, skeleton: Dict[str, Any], req: ReportRequest) -> Dict[str, Any]:
        """Agrega VizSpecs con datos reales del Structurer (Fase B). Fase D:
        reemplaza `data` con SVG renderizado por matplotlib."""
        stats = skeleton["stats"]
        timeline = skeleton.get("timeline", [])
        source_dist = skeleton.get("source_distribution", {})

        for section in skeleton["sections"]:
            if section.section_id in ("cifras_clave", "infografia_unica"):
                section.viz_specs.append(VizSpec(
                    kind="infographic_top",
                    title="Cifras clave del proceso",
                    caption=f"Datos del sistema PEIRS cubriendo {stats.days_covered} días.",
                    data={
                        "kpis": [
                            {"label": "Hallazgos registrados", "value": stats.total_findings, "color": "#00796b"},
                            {"label": "Críticos", "value": stats.critical, "color": "#d32f2f"},
                            {"label": "Altos", "value": stats.high, "color": "#f97316"},
                            {"label": "Fuentes", "value": stats.sources_count, "color": "#1976d2"},
                        ]
                    },
                ))
                # Donut de severidades
                if section.section_id == "cifras_clave":
                    section.viz_specs.append(VizSpec(
                        kind="donut",
                        title="Distribución por severidad",
                        caption="Universo total de hallazgos clasificados.",
                        data={"segments": [
                            {"label": "critical", "value": stats.critical, "color": "#d32f2f"},
                            {"label": "high", "value": stats.high, "color": "#f97316"},
                            {"label": "medium", "value": stats.medium, "color": "#fbc02d"},
                            {"label": "low", "value": stats.low, "color": "#388e3c"},
                            {"label": "info", "value": stats.info, "color": "#1976d2"},
                        ]},
                    ))
            if section.section_id in ("timeline_hallazgos", "findings"):
                section.viz_specs.append(VizSpec(
                    kind="timeline",
                    title="Distribución diaria de hallazgos por severidad",
                    caption="Los picos post-jornada indican escalamiento de la cobertura informativa y denuncias.",
                    data={"days": timeline},
                ))
                if source_dist:
                    section.viz_specs.append(VizSpec(
                        kind="bar_horizontal",
                        title="Distribución por medio verificador",
                        caption="Fuentes RSS peruanas monitoreadas.",
                        data={"bars": [{"label": k, "value": v} for k, v in sorted(source_dist.items(), key=lambda x: -x[1])]},
                    ))
        return skeleton

    # ────────────────────────────────────────────────────────────────────
    # Paso 3: Composer (mock Fase A)
    # ────────────────────────────────────────────────────────────────────
    def _composer_mock(self, skeleton: Dict[str, Any], req: ReportRequest,
                       report_id: str, now: str) -> ReportOutput:
        """Genera narrativas con plantillas que incorporan hallazgos reales del
        Structurer (Fase B). Fase C reemplaza plantillas por Claude."""
        sections: List[ReportSection] = skeleton["sections"]
        stats: ReportStats = skeleton["stats"]
        theme_ranking = skeleton.get("theme_ranking", [])
        top_findings = skeleton.get("top_findings_overall", [])

        for section in sections:
            section.narrative = self._mock_narrative_v2(section, req, stats, theme_ranking, top_findings)

        markdown = self._render_markdown(sections, stats, req)
        html = self._render_html(sections, stats, req)

        return ReportOutput(
            report_id=report_id,
            country_code=req.country_code.upper(),
            audience=req.audience,
            language=req.language,
            generated_at=now,
            status="done",
            markdown=markdown,
            html=html,
            sections=sections,
            stats=stats,
            sources_cited=skeleton["sources"],
            visualizations=[v for s in sections for v in s.viz_specs],
            warnings=[
                "Fases B+D activas: Structurer real con dedupe semántico + clasificación "
                "por 11 temas + priorización ponderada; Visualizer con SVG reales "
                "(infographic, timeline apilado, donut, bar horizontal). "
                "Fase C pendiente: narrativas generadas con plantillas; Claude reemplazará "
                "esto para producir texto sustantivo con citas verificables."
            ],
        )

    def _mock_narrative_v2(self, section: ReportSection, req: ReportRequest,
                            stats: ReportStats, theme_ranking: List[Dict],
                            top_findings: List[FindingRef]) -> str:
        """Plantillas que incorporan data REAL del Structurer (Fase B).
        Fase C reemplaza esto por prompts Claude con contexto completo."""
        country = req.country_code.upper()
        sid = section.section_id

        # Helper: formatea un FindingRef como línea markdown con link
        def _cite(f: FindingRef, max_chars: int = 200) -> str:
            finding_text = (f.finding or "")[:max_chars]
            if len(f.finding or "") > max_chars:
                finding_text += "…"
            src = f.source_name or "fuente"
            if f.source_url:
                return f"{finding_text} [_{src}_]({f.source_url})"
            return f"{finding_text} [_{src}_]"

        def _top_themes_str(n: int = 3) -> str:
            out = []
            for t in theme_ranking[:n]:
                out.append(f"**{t['label']}** ({t['total']} hallazgos, {t['high_critical']} high/critical)")
            return "; ".join(out)

        # Fallback: si no hay data real (country != PER), usamos plantillas v1
        if country != "PER" or stats.total_findings == 0:
            return self._mock_narrative(section, req, stats)

        # Cifras derivadas
        top_source = ""
        if theme_ranking:
            top_source = theme_ranking[0]["label"].lower()

        templates = {
            "portada": (
                f"**DemocracIA / PEIRS — Informe preliminar de observación electoral**\n\n"
                f"País: {country} · Fecha del informe: {stats.generated_at[:10]} · "
                f"Período: últimos {stats.days_covered} días · Audiencia: {req.audience}\n\n"
                f"Este documento resume {stats.total_findings} hallazgos monitoreados automáticamente "
                f"por el sistema PEIRS, clasificados con asistencia de IA sobre 5 fuentes RSS peruanas."
            ),
            "resumen_ejecutivo": (
                f"El sistema PEIRS registró **{stats.total_findings} hallazgos** en {stats.days_covered} "
                f"días sobre el proceso electoral peruano. De ellos, **{stats.critical} críticos** y "
                f"**{stats.high} de severidad alta**. Los temas dominantes fueron {_top_themes_str(3)}. "
                f"El proceso continúa abierto al cierre de este informe; la proclamación presidencial "
                f"oficial permanece pendiente y la disputa institucional sigue activa."
            ),
            "declaracion_1_pagina": (
                f"Las Elecciones Generales Perú 2026 están marcadas por la peor crisis operativa del "
                f"organismo electoral en la historia democrática moderna del país. Al menos 115.000 "
                f"ciudadanos documentados sin poder sufragar, cifra probablemente subestimada. "
                f"{_top_themes_str(3)}. El escrutinio continúa abierto; las responsabilidades penales "
                f"e institucionales están en curso. El proceso sigue siendo legítimo pero con graves "
                f"debilidades estructurales que requieren atención legislativa inmediata."
            ),
            "metodologia": (
                f"**Pipeline PEIRS**: Hunter RSS cada 24 horas sobre 14 fuentes (8 peruanas + 6 internacionales filtradas por keyword \"Peru\") incluyendo Andina, "
                f"El Comercio, Gestión, IDL-Reporteros, RPP Noticias). Clasificación automática "
                f"con Claude Sonnet 4.6 (Anthropic). Dedupe semántico por (categoría, URL, fecha). "
                f"Priorización ponderada: severidad × recencia (decay exp. 3 días) × credibilidad "
                f"de fuente. **Marco normativo**: ICCPR Art. 25, CADH Art. 23, CDI Art. 3, "
                f"Constitución Perú 1993 Arts. 176-187, LOE N° 26859, LOP N° 28094."
            ),
            "cifras_clave": (
                f"- **{stats.total_findings}** hallazgos monitoreados y clasificados\n"
                f"- **{stats.critical}** críticos · **{stats.high}** altos · **{stats.medium}** medios · "
                f"**{stats.low}** bajos · **{stats.info}** informativos\n"
                f"- **{stats.sources_count}** fuentes RSS verificadas\n"
                f"- **{stats.days_covered}** días de monitoreo continuo\n"
                f"- Top 3 temas: {_top_themes_str(3)}"
            ),
            "contexto": (
                f"Perú atraviesa inestabilidad institucional crónica: 6 presidentes en 4 años "
                f"(2020-2024). Las Elecciones 2026 introducen bicameralidad y doble valla. "
                f"El voto electrónico no presencial fue rechazado por Res. JNE 0891-2025 "
                f"por ausencia de auditoría independiente certificada. "
                f"El sistema tripartito JNE/ONPE/RENIEC opera bajo tensión institucional "
                f"inédita tras el 12 de abril."
            ),
            "timeline_hallazgos": (
                f"Distribución diaria de hallazgos por severidad (ver visualización adjunta). "
                f"Los picos post-jornada reflejan el escalamiento de denuncias penales y la "
                f"cobertura informativa de las fallas operativas de ONPE."
            ),
            "temas_criticos": self._render_themes_section(theme_ranking, _cite),
            "3_temas_mas_criticos": (
                "Los tres temas que concentran mayor densidad de hallazgos críticos/altos son:\n\n"
                + "\n".join([
                    f"**{i+1}. {t['label']}** — {t['high_critical']} high/critical sobre "
                    f"{t['total']} hallazgos totales. Ejemplo: "
                    f"_{(t['top_findings'][0].finding or '')[:160]}…_"
                    for i, t in enumerate(theme_ranking[:3]) if t.get("top_findings")
                ])
            ),
            "derechos_vulnerados": (
                f"Marco de derechos invocados en los hallazgos:\n\n"
                f"- **ICCPR Art. 25** — sufragio activo y pasivo en condiciones equitativas\n"
                f"- **CADH Art. 23** — derechos políticos bajo sistema interamericano\n"
                f"- **CADH Art. 13** / **ICCPR Art. 19(2)** — libertad de expresión y derecho "
                f"a información veraz\n"
                f"- **Carta Democrática Interamericana Art. 3** — elementos esenciales de la "
                f"democracia representativa (elecciones auténticas, estado de derecho, "
                f"separación de poderes)\n"
                f"- **Constitución Perú Arts. 2(17), 31, 35, 176-187** — marco interno"
            ),
            "responsabilidad_penal": self._render_penal_section(section.findings, _cite),
            "recomendaciones": (
                "**Corto plazo (48–72h)**: publicación del cronograma de rezagos del escrutinio; "
                "registro auditado de ciudadanos afectados por no instalación de mesas; informe "
                "técnico desagregado del sistema STAE.\n\n"
                "**Mediano plazo (1–6 meses)**: auditoría independiente integral de los 3 sistemas "
                "(STAE/SCE/SPR) con participación académica y de sociedad civil; revisión del "
                "proceso de ratificación del jefe de ONPE; conclusión de la investigación penal "
                "sobre el contrato con Galaga; publicación del código fuente del componente de IA.\n\n"
                "**Largo plazo (pre-próximas elecciones)**: Ley de IA en procesos electorales con "
                "estándares obligatorios de auditoría, explicabilidad y derecho de impugnación "
                "sobre decisiones automatizadas; reforma logística de ONPE con redundancia y "
                "control sobre terceros; integración con estándares internacionales."
            ),
            "recomendaciones_prioritarias": (
                "1. **Publicación inmediata** del código fuente y documentación del sistema STAE\n"
                "2. **Ley de IA electoral** al Congreso antes de la segunda vuelta\n"
                "3. **Auditoría independiente post-electoral** con universidades, sociedad civil "
                "y expertos internacionales"
            ),
            "titulo": f"Crisis operativa de ONPE marca Elecciones Perú 2026: {stats.critical + stats.high} hallazgos de severidad alta o crítica",
            "bajada": self._render_top_findings_compact(top_findings[:3], _cite),
            "infografia_unica": (
                f"**{stats.total_findings}** hallazgos · **{stats.critical}** críticos · "
                f"**{stats.high}** altos · **{stats.sources_count}** fuentes · "
                f"**{stats.days_covered}** días · Top tema: {theme_ranking[0]['label'] if theme_ranking else '—'}"
            ),
            "3_hallazgos_mas_cita": self._render_top_findings_bullets(top_findings[:3], _cite),
            "anexo_fuentes": (
                f"**Medios RSS verificados**: " +
                ", ".join(skeleton_src for skeleton_src in []) +  # placeholder
                "Andina, El Comercio, Gestión, IDL-Reporteros, RPP Noticias\n\n"
                f"**Normativa peruana**: Constitución 1993 Arts. 176-187; LOE N° 26859 Arts. 190/191/351/358/363; "
                f"LOP N° 28094; Ley 31030 (paridad); Ley 31170 (acoso político).\n\n"
                f"**Instrumentos internacionales**: ICCPR (ratificado), CADH (ratificado), "
                f"Carta Democrática Interamericana, jurisprudencia Corte IDH.\n\n"
                f"**Jurisprudencia JNE**: Res. 0234-2018 (inhabilitación por financiamiento ilícito), "
                f"Res. 0891-2025 (rechazo VENP por falta de auditoría)."
            ),
            # EN (international)
            "cover": f"DemocracIA / PEIRS — Electoral Observation Preliminary Report — {country} 2026",
            "executive_summary": (
                f"Peru's General Elections of 12-Apr-2026 were marked by the worst operational "
                f"crisis of ONPE (electoral body) in modern democratic history. PEIRS recorded "
                f"{stats.total_findings} classified findings over {stats.days_covered} days. "
                f"{stats.critical} critical and {stats.high} high-severity events. "
                f"Vote counting continues open; criminal prosecution against the ONPE chief is "
                f"underway. The AI-assisted vote processing system (STAE) was deployed without "
                f"independent certified audit."
            ),
            "context_comparative": (
                "Peru is classified 'Partly Free' by Freedom House 2025 and 'Electoral Democracy' "
                "by V-Dem v15. Chronic institutional instability (6 presidents in 4 years). "
                "The 2026 elections introduce bicameralism and a twin-threshold system. "
                "Electronic voting (VENP) was rejected by JNE Resolution 0891-2025 for lack of "
                "independent audit — the same standard was NOT applied to the STAE AI system "
                "deployed for ballot processing."
            ),
            "findings": (
                f"{stats.total_findings} automated findings recorded; {stats.critical} critical, "
                f"{stats.high} high severity. Dominant themes: "
                + ", ".join(t['label'] for t in theme_ranking[:3])
                + ". See visualizations for daily distribution."
            ),
            "rights_framework": (
                "ICCPR Art. 25 (political rights), CADH Art. 23 (inter-American political rights), "
                "CADH Art. 13 / ICCPR Art. 19(2) (freedom of expression, right to truthful "
                "information), Inter-American Democratic Charter Art. 3 (essential elements of "
                "representative democracy)."
            ),
            "recommendations": (
                "Short-term: transparency from ONPE on backlog and affected citizens. "
                "Medium-term: independent audit of STAE/SCE/SPR. "
                "Long-term: legislation on AI in electoral processes; ONPE logistical reform; "
                "alignment with international standards (Council of Europe AI Framework Convention 2024, "
                "UNESCO Recommendation on AI Ethics)."
            ),
            "references": (
                "Peruvian verified media RSS (Andina, El Comercio, Gestión, IDL-Reporteros, RPP); "
                "International: ICCPR, ACHR, IADC, IACHR jurisprudence; "
                "National: Constitution 1993 Arts. 176-187, Organic Election Law 26859, "
                "Political Organizations Law 28094."
            ),
        }
        return templates.get(sid, self._mock_narrative(section, req, stats))

    def _render_themes_section(self, theme_ranking: List[Dict], cite_fn) -> str:
        """Arma la sección temas_criticos con los top 5 temas y sus findings."""
        if not theme_ranking:
            return "Sin temas clasificados (datos insuficientes)."
        lines = []
        for i, t in enumerate(theme_ranking[:5]):
            lines.append(f"### {chr(ord('A')+i)}. {t['label']}")
            lines.append(f"*{t['total']} hallazgos registrados · {t['high_critical']} de severidad high/critical.*")
            lines.append("")
            for f in t.get("top_findings", [])[:3]:
                lines.append(f"- {cite_fn(f)}")
            lines.append("")
        return "\n".join(lines)

    def _render_penal_section(self, findings: List[FindingRef], cite_fn) -> str:
        """Arma la sección de responsabilidad penal con findings reales."""
        if not findings:
            return (
                "Las acciones penales y administrativas documentadas incluyen: denuncia penal "
                "del JNE contra el titular de ONPE; detención en flagrancia del gerente de "
                "Gestión Electoral; investigación de la Fiscalía Anticorrupción por posible "
                "colusión con el proveedor tercerizado del transporte; revisión disciplinaria "
                "de la JNJ sobre el proceso de ratificación del jefe de ONPE. "
                "(El informe completo contendrá el detalle específico al activar Fase C "
                "con narrativa asistida por LLM.)"
            )
        lines = ["Hallazgos específicos relacionados con responsabilidad penal e institucional:", ""]
        for f in findings[:8]:
            lines.append(f"- {cite_fn(f, 220)}")
        return "\n".join(lines)

    def _render_top_findings_bullets(self, findings: List[FindingRef], cite_fn) -> str:
        if not findings:
            return "Sin hallazgos prioritarios disponibles."
        return "\n\n".join(f"**{i+1}.** {cite_fn(f, 220)}" for i, f in enumerate(findings))

    def _render_top_findings_compact(self, findings: List[FindingRef], cite_fn) -> str:
        if not findings:
            return "Denuncias penales en curso contra autoridades del organismo electoral; crisis operativa documentada; cuestionamientos a la legitimidad del resultado."
        snippets = [(f.finding or "")[:80].rstrip() + "…" for f in findings[:3] if f.finding]
        return "; ".join(snippets) + "."

    def _mock_narrative(self, section: ReportSection, req: ReportRequest, stats: ReportStats) -> str:
        """Narrativas de plantilla. En Fase C se reemplazan con Claude."""
        country = req.country_code.upper()
        if country != "PER":
            return f"[{section.title}] Contenido pendiente para {country}. En Fase A sólo Perú tiene plantilla."

        templates = {
            "portada": f"**DemocracIA / PEIRS**\n\nInforme preliminar de observación electoral — {country}\n\n*Audiencia: {req.audience}*\n\n*Generado: {stats.generated_at[:10]}*",
            "resumen_ejecutivo": (
                f"El sistema PEIRS registró **{stats.total_findings} hallazgos** en {stats.days_covered} días "
                f"sobre el proceso electoral peruano 2026. De ellos, **{stats.critical} fueron clasificados como críticos** "
                f"y **{stats.high} como de severidad alta**. La crisis operativa de ONPE del 12-abr dejó al menos "
                f"115.000 ciudadanos sin sufragar, detonó denuncias penales contra su titular y abrió una disputa "
                f"institucional en curso."
            ),
            "declaracion_1_pagina": (
                "En una página: las Elecciones Generales Perú 2026 atravesaron la peor crisis operativa de ONPE "
                "de la historia democrática moderna del país. El escrutinio continúa abierto y las responsabilidades "
                "penales institucionales están en curso. El proceso sigue siendo legítimo pero con graves debilidades "
                "que requieren atención inmediata del Congreso y del sistema de justicia."
            ),
            "metodologia": (
                "Pipeline PEIRS: Hunter RSS cada 24h sobre 14 fuentes verificadas (nacionales e internacionales), clasificación con "
                "Claude Sonnet 4.6, persistencia SQLite sobre volume Railway. Marco normativo: ICCPR Art. 25, "
                "CADH Art. 23, Constitución Perú 1993 Arts. 176-187, LOE N° 26859, LOP N° 28094."
            ),
            "cifras_clave": (
                f"- **{stats.total_findings}** hallazgos clasificados\n"
                f"- **{stats.critical}** críticos · **{stats.high}** altos · **{stats.medium}** medios\n"
                f"- **{stats.sources_count}** fuentes RSS peruanas\n"
                f"- **{stats.days_covered}** días de monitoreo"
            ),
            "contexto": (
                "Perú atraviesa una inestabilidad institucional crónica: 6 presidentes en 4 años (2020-2024). "
                "Las Elecciones Generales 2026 introducen bicameralidad, doble valla y rechazo del voto electrónico "
                "no presencial (Res. JNE 0891-2025). El sistema tripartito JNE/ONPE/RENIEC opera bajo tensión "
                "institucional inédita tras el 12-abr."
            ),
            "timeline_hallazgos": "Timeline de hallazgos por día (ver visualización adjunta). Pico post-electoral el 13-abr con 24 alertas high.",
            "temas_criticos": (
                "**A. Crisis logística ONPE** (191 hallazgos, 2 críticos iniciales + 1 adicional post-13-abr). "
                "**B. IA no regulada (STAE)** — componente de IA en cómputo sin auditoría pública certificada. "
                "**C. Narrativa de fraude** — López Aliaga pide nulidad, ofrece S/20.000 recompensa (potencial tipo penal Art. 400 CP). "
                "**D. Captura institucional** — investigación IDL sobre coalición parlamentaria votando concertadamente. "
                "**E. Responsabilidad penal del titular ONPE** — denuncia JNE + Fiscalía anticorrupción."
            ),
            "3_temas_mas_criticos": (
                "1. Crisis logística ONPE (115k+ sin voto). 2. IA sin auditoría pública (STAE). "
                "3. Responsabilidad penal titular ONPE."
            ),
            "derechos_vulnerados": (
                "**ICCPR Art. 25** (586 menciones): sufragio activo y pasivo en condiciones equitativas. "
                "**CADH Art. 23** (169): derechos políticos bajo sistema interamericano. "
                "**CADH Art. 13** (166): libertad de expresión. "
                "**ICCPR Art. 19(2)** (135): información veraz."
            ),
            "responsabilidad_penal": (
                "JNE denuncia penalmente al jefe de ONPE Piero Corvetto + 3 funcionarios por presuntos delitos "
                "contra el derecho de sufragio y omisión de actos funcionales. Gerente de Gestión Electoral detenido "
                "en flagrancia. Fiscalía de la Nación pide separación cautelar. Subgerente de Producción Electoral "
                "procesado con pedido fiscal de +10 años. JNJ inicia investigación disciplinaria y revisión del proceso "
                "de ratificación."
            ),
            "recomendaciones": (
                "**Corto plazo**: publicación cronograma de rezagos; registro público auditado de ciudadanos afectados; "
                "informe técnico STAE desagregado. **Mediano**: auditoría independiente integral de los 3 sistemas "
                "(STAE/SCE/SPR); revisión proceso de ratificación jefe ONPE; conclusión investigación penal Galaga. "
                "**Largo**: Ley de IA en procesos electorales al Congreso; reforma arquitectura logística ONPE; "
                "integración con estándares internacionales (Consejo de Europa, UNESCO, IDEA)."
            ),
            "recomendaciones_prioritarias": (
                "1. Publicación código fuente y documentación STAE. "
                "2. Legislación de IA electoral antes de segunda vuelta. "
                "3. Auditoría independiente post-electoral con participación civil y académica."
            ),
            "anexo_fuentes": (
                "**Medios RSS monitoreados**: Andina, El Comercio, Gestión, IDL-Reporteros, RPP Noticias. "
                "**Normativa**: Constitución 1993 Arts. 176-187, LOE N° 26859, LOP N° 28094, Ley 31030 (paridad), "
                "Ley 31170 (acoso político). **Instrumentos internacionales**: ICCPR, CADH, CDI, jurisprudencia Corte IDH."
            ),
            "titulo": "Crisis operativa de ONPE marca elecciones Perú 2026",
            "bajada": "Al menos 115.000 ciudadanos sin voto; JNE denuncia penalmente al jefe del organismo electoral; IA en cómputo sin auditoría.",
            "infografia_unica": (
                f"{stats.total_findings} hallazgos · {stats.critical} críticos · {stats.high} altos · "
                f"{stats.sources_count} fuentes · {stats.days_covered} días"
            ),
            "3_hallazgos_mas_cita": (
                "**1.** Contraloría emitió 270 informes con 600 observaciones previas a la jornada (El Comercio, 16-abr). "
                "**2.** JNE denuncia penalmente al jefe ONPE Piero Corvetto (RPP, 14-abr). "
                "**3.** Transparencia suspendió su conteo rápido por fallas operativas (RPP, 13-abr)."
            ),
            # International (English)
            "executive_summary": (
                "Peru's General Elections of 12-Apr-2026 were marked by the worst operational crisis of ONPE "
                "(National Office for Electoral Processes) in modern democratic history. At least 115,000 citizens "
                "were unable to vote. The head of the electoral body faces criminal prosecution. The country's "
                "first deployment of AI in ballot processing (STAE system) was authorized without independent "
                "certified audit. Vote counting continues open."
            ),
            "context_comparative": (
                "Peru ranks in the 'Partly Free' tier on Freedom House (2025) and 'Electoral Democracy' on V-Dem v15. "
                "Institutional instability is chronic: 6 presidents in 4 years. The 2026 elections introduce "
                "bicameralism and a new twin-threshold system; electronic voting was rejected by JNE Resolution "
                "0891-2025 for lack of independent audit."
            ),
            "findings": f"{stats.total_findings} automated findings recorded over {stats.days_covered} days. See visualization for daily distribution.",
            "rights_framework": "ICCPR Art. 25 (586 citations), CADH Art. 23 (169), CADH Art. 13 (166), ICCPR Art. 19(2) (135). Inter-American Democratic Charter Art. 3.",
            "recommendations": "Short-term transparency from ONPE; medium-term independent audit of STAE/SCE/SPR; long-term legislation on AI in electoral processes.",
            "references": "Peruvian media RSS (verified sources); international instruments (ICCPR, ACHR, IADC); JNE jurisprudence.",
            "cover": f"DemocracIA / PEIRS — Electoral Observation Preliminary Report — {country} 2026",
        }
        return templates.get(section.section_id, f"[{section.title}] — plantilla Fase A pendiente de expandir en Composer real.")

    def _render_markdown(self, sections: List[ReportSection], stats: ReportStats,
                        req: ReportRequest) -> str:
        """Arma el Markdown unificado."""
        lines = [f"# Informe de Observación Electoral — {req.country_code.upper()}",
                 f"*Audiencia: {req.audience} · Idioma: {req.language} · Generado: {stats.generated_at[:16]}*",
                 "", "---", ""]
        for section in sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.narrative)
            lines.append("")
            for v in section.viz_specs:
                lines.append(f"> **[Visualización — {v.kind}]** {v.title}  \n> *{v.caption}*")
                lines.append("")
        lines.append("---")
        lines.append(f"*Fase A del ReportDesigner. {stats.total_findings} hallazgos base.*")
        return "\n".join(lines)

    def _render_html(self, sections: List[ReportSection], stats: ReportStats,
                    req: ReportRequest) -> str:
        """HTML liviano embebible en iframe del frontend. Fase D: SVG inline reales."""
        body_sections = []
        for section in sections:
            viz_html = ""
            for v in section.viz_specs:
                svg = viz_renderer.render(v.kind, v.data)
                if svg:
                    viz_html += (
                        f'<figure class="viz">'
                        f'<figcaption class="viz-title">{self._escape(v.title)}</figcaption>'
                        f'<div class="viz-svg">{svg}</div>'
                        f'<figcaption class="viz-caption">{self._escape(v.caption)}</figcaption>'
                        f'</figure>'
                    )
                else:
                    viz_html += (
                        f'<div class="viz-placeholder">[{v.kind}] '
                        f'{self._escape(v.title)} — <em>{self._escape(v.caption)}</em></div>'
                    )

            # Render narrative con markdown simplificado: ** → strong, - → li, \n\n → párrafos
            narrative_html = self._render_markdown_simple(section.narrative)
            # Citas de findings de la sección (si existen)
            if section.findings:
                narrative_html += '<div class="findings"><h4>Hallazgos citados:</h4><ul>'
                for f in section.findings[:8]:
                    src = f.source_name or "fuente"
                    link = f' — <a href="{self._escape(f.source_url)}" target="_blank" rel="noopener">{src}</a>' if f.source_url else f' — {src}'
                    sev_tag = f'<span class="sev sev-{f.severity}">{f.severity}</span>'
                    narrative_html += f'<li>{sev_tag}{self._escape(f.finding[:220])}{link}</li>'
                narrative_html += '</ul></div>'

            body_sections.append(
                f'<section><h2>{self._escape(section.title)}</h2>'
                f'{narrative_html}'
                f'{viz_html}'
                f'</section>'
            )

        css = """
        body { font-family: -apple-system, 'Segoe UI', sans-serif; max-width: 900px;
               margin: 2rem auto; padding: 0 1.5rem; color: #1a1a1a; line-height: 1.6;
               font-size: 14px; }
        h1 { color: #0a0e17; border-bottom: 2px solid #00796b; padding-bottom: 8px;
             font-size: 24px; }
        h2 { color: #004d40; border-bottom: 1px solid #b0bec5; padding-bottom: 4px;
             margin-top: 2.2rem; font-size: 18px; }
        h3 { color: #00695c; font-size: 15px; margin-top: 1.4rem; }
        h4 { color: #263238; font-size: 13px; margin-top: 1rem; text-transform: uppercase;
             letter-spacing: 1px; }
        .narrative { margin: 1rem 0; }
        .narrative p { margin: 0.7rem 0; }
        .narrative ul, .narrative ol { margin: 0.7rem 0; padding-left: 1.6rem; }
        .narrative strong { color: #000; font-weight: 700; }
        .narrative a { color: #00695c; }
        .narrative em { color: #37474f; }
        .viz { margin: 1.2rem 0; padding: 10px; background: #fafafa; border-radius: 8px;
               border: 1px solid #e5e7eb; }
        .viz-title { font-size: 12px; font-weight: 700; color: #00695c;
                     text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
        .viz-caption { font-size: 11px; color: #78909c; margin-top: 6px; font-style: italic; }
        .viz-svg { text-align: center; }
        .viz-svg svg { max-width: 100%; height: auto; }
        .viz-placeholder { background: #f0f7f6; padding: 14px; border-left: 3px solid #00796b;
                           margin: 10px 0; font-size: 13px; color: #78909c; }
        .findings { margin-top: 1rem; padding: 10px 14px; background: #f7fafc;
                    border-left: 3px solid #00796b; border-radius: 4px; }
        .findings ul { margin: 6px 0 0; padding-left: 1.2rem; }
        .findings li { margin: 8px 0; font-size: 12px; color: #37474f; line-height: 1.6; }
        .sev { display: inline-block; padding: 1px 6px; border-radius: 3px;
               font-family: monospace; font-size: 9px; font-weight: 700;
               text-transform: uppercase; margin-right: 6px; letter-spacing: 1px; }
        .sev-critical { background: #fef2f2; color: #d32f2f; }
        .sev-high { background: #fff7ed; color: #f97316; }
        .sev-medium, .sev-moderate { background: #fefce8; color: #b45309; }
        .sev-low { background: #f0fdf4; color: #388e3c; }
        .sev-info { background: #eff6ff; color: #1976d2; }
        """
        return (
            f'<!DOCTYPE html><html lang="{req.language}"><head><meta charset="utf-8">'
            f'<title>DemocracIA Report {req.country_code}</title><style>{css}</style></head>'
            f'<body><h1>Informe DemocracIA — {req.country_code.upper()}</h1>'
            f'<p><em>Audiencia: {req.audience} · Generado: {stats.generated_at[:16]}</em></p>'
            + "".join(body_sections)
            + f'<hr><p style="color:#78909c;font-size:11px">Fase A — Esqueleto funcional ReportDesigner. {stats.total_findings} hallazgos base.</p>'
            + '</body></html>'
        )

    @staticmethod
    def _escape(s: str) -> str:
        import html
        return html.escape(s or "")

    def _render_markdown_simple(self, md: str) -> str:
        """Conversor markdown → HTML liviano (sin libs externas). Soporta:
        - **bold** y _em_ / *em*
        - # H1, ## H2, ### H3 (solo a inicio de línea)
        - - / * listas
        - párrafos separados por línea en blanco
        - [link](url)
        """
        if not md:
            return ""
        import re
        import html as _html

        lines = md.split("\n")
        out = []
        in_list = False

        def inline(s: str) -> str:
            s = _html.escape(s)
            # Links [texto](url)
            s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                       r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
            # Bold **x**
            s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
            # Italic _x_
            s = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<em>\1</em>', s)
            return s

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_list:
                    out.append("</ul>")
                    in_list = False
                out.append("")
                continue
            if stripped.startswith("### "):
                if in_list: out.append("</ul>"); in_list = False
                out.append(f"<h3>{inline(stripped[4:])}</h3>")
            elif stripped.startswith("## "):
                if in_list: out.append("</ul>"); in_list = False
                out.append(f"<h3>{inline(stripped[3:])}</h3>")
            elif stripped.startswith("# "):
                if in_list: out.append("</ul>"); in_list = False
                out.append(f"<h3>{inline(stripped[2:])}</h3>")
            elif stripped.startswith("- ") or stripped.startswith("* "):
                if not in_list:
                    out.append("<ul>"); in_list = True
                out.append(f"<li>{inline(stripped[2:])}</li>")
            else:
                if in_list: out.append("</ul>"); in_list = False
                out.append(f"<p>{inline(stripped)}</p>")
        if in_list:
            out.append("</ul>")
        return '<div class="narrative">' + "\n".join(out) + "</div>"

    def _persist_mock(self, output: ReportOutput, req: ReportRequest) -> None:
        """Guarda MD + HTML en disco bajo reports/designed/."""
        try:
            os.makedirs(REPORTS_DIR, exist_ok=True)
            base = os.path.join(REPORTS_DIR, output.report_id)
            if "md" in req.output_formats and output.markdown:
                with open(f"{base}.md", "w", encoding="utf-8") as f:
                    f.write(output.markdown)
            if "html" in req.output_formats and output.html:
                with open(f"{base}.html", "w", encoding="utf-8") as f:
                    f.write(output.html)
        except Exception as e:
            output.warnings.append(f"Persistencia parcial falló: {e}")
