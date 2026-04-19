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


REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports", "designed")


class ReportDesigner:
    """
    Pipeline de composición de informes (Fase A — esqueleto).

    Los 3 pasos se implementan como métodos privados. En Fase A devuelven data
    determinista; en Fases B-E se reemplazan con lógica real.
    """

    def __init__(self, llm=None, hunter_entries_loader=None, alerts_loader=None):
        """
        Args:
            llm: instancia de Claude (futuro uso en Composer)
            hunter_entries_loader: callable(cc) -> list de entries (futuro uso en Structurer)
            alerts_loader: callable(cc) -> list de alerts (futuro uso en Structurer)
        """
        self.llm = llm
        self._entries_loader = hunter_entries_loader
        self._alerts_loader = alerts_loader

    async def run(self, req: ReportRequest) -> ReportOutput:
        """Ejecuta el pipeline completo. Fase A: mocks."""
        report_id = str(uuid.uuid4())[:12]
        now = datetime.now(timezone.utc).isoformat()

        # Paso 1 — Structurer (mock)
        skeleton = self._structurer_mock(req)

        # Paso 2 — Visualizer (mock)
        skeleton = self._visualizer_mock(skeleton, req)

        # Paso 3 — Composer (mock)
        output = self._composer_mock(skeleton, req, report_id, now)

        # Persistencia simple en disco (Fase A)
        self._persist_mock(output, req)

        return output

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
        """Agrega VizSpecs mockeados según audiencia. Fase A no renderiza SVG."""
        stats = skeleton["stats"]
        for section in skeleton["sections"]:
            if section.section_id in ("cifras_clave", "infografia_unica"):
                section.viz_specs.append(VizSpec(
                    kind="infographic_top",
                    title="Cifras clave del proceso",
                    caption=f"Datos del sistema PEIRS cubriendo {stats.days_covered} días.",
                    data={
                        "kpis": [
                            {"label": "Hallazgos registrados", "value": stats.total_findings, "color": "#00d4aa"},
                            {"label": "Críticos", "value": stats.critical, "color": "#ef4444"},
                            {"label": "Altos", "value": stats.high, "color": "#f97316"},
                            {"label": "Fuentes", "value": stats.sources_count, "color": "#3b82f6"},
                        ]
                    },
                ))
            if section.section_id in ("timeline_hallazgos", "findings"):
                section.viz_specs.append(VizSpec(
                    kind="timeline",
                    title="Distribución diaria de hallazgos",
                    caption="Agregado por severidad.",
                    data={"placeholder": "Fase A — datos reales se calculan en Fase B."},
                ))
        return skeleton

    # ────────────────────────────────────────────────────────────────────
    # Paso 3: Composer (mock Fase A)
    # ────────────────────────────────────────────────────────────────────
    def _composer_mock(self, skeleton: Dict[str, Any], req: ReportRequest,
                       report_id: str, now: str) -> ReportOutput:
        """Genera narrativas mock + renderiza Markdown. Fase A."""
        sections: List[ReportSection] = skeleton["sections"]
        stats: ReportStats = skeleton["stats"]

        for section in sections:
            section.narrative = self._mock_narrative(section, req, stats)

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
                "Fase A — esqueleto funcional. Narrativas generadas con plantillas; "
                "las Fases B-E implementarán lógica real (Structurer con dedupe semántico, "
                "Visualizer con SVG/matplotlib, Composer con Claude)."
            ],
        )

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
                "Pipeline PEIRS: Hunter RSS cada 4h sobre 5 fuentes peruanas verificadas, clasificación con "
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
        """HTML liviano embebible en iframe del frontend."""
        body_sections = []
        for section in sections:
            viz_html = ""
            for v in section.viz_specs:
                if v.kind == "infographic_top" and v.data.get("kpis"):
                    kpis = v.data["kpis"]
                    viz_html += '<div class="kpis">' + "".join(
                        f'<div class="kpi" style="border-color:{k["color"]};"><div class="kpi-val" style="color:{k["color"]};">{k["value"]}</div><div class="kpi-label">{k["label"]}</div></div>'
                        for k in kpis
                    ) + "</div>"
                else:
                    viz_html += f'<div class="viz-placeholder">[{v.kind}] {v.title} — <em>{v.caption}</em></div>'

            body_sections.append(
                f'<section><h2>{section.title}</h2>'
                f'<div class="narrative">{section.narrative.replace(chr(10), "<br>").replace("**", "<strong>").replace("<strong>", "<strong>", 1)}</div>'
                f'{viz_html}'
                f'</section>'
            )

        css = """
        body { font-family: -apple-system, 'Segoe UI', sans-serif; max-width: 900px;
               margin: 2rem auto; padding: 0 1.5rem; color: #1a1a1a; line-height: 1.6; }
        h1 { color: #0a0e17; border-bottom: 2px solid #00796b; padding-bottom: 8px; }
        h2 { color: #004d40; border-bottom: 1px solid #b0bec5; padding-bottom: 4px; margin-top: 2rem; }
        .narrative { margin: 1rem 0; }
        .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 1rem 0; }
        .kpi { padding: 14px; border: 2px solid; border-radius: 8px; text-align: center; }
        .kpi-val { font-size: 28px; font-weight: 800; font-family: monospace; line-height: 1.1; }
        .kpi-label { font-size: 10px; color: #64748b; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; }
        .viz-placeholder { background: #f0f7f6; padding: 14px; border-left: 3px solid #00796b; margin: 10px 0; font-size: 13px; }
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
