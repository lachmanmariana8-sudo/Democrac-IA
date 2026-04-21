"""
ReportDesigner — Composer con Claude (Fase C).

Reemplaza las plantillas estáticas por narrativa generada por Claude sobre
los findings priorizados del Structurer. Cada sección se genera con un
prompt específico por audiencia (technical/executive/press/international).

Ventaja sobre plantillas:
- Texto sustantivo y específico a los hallazgos reales del ciclo.
- Citas textuales de fuentes primarias (con URL).
- Adaptación automática al idioma y a la densidad informativa.

Estrategia de tokens:
- Prompt caching de Anthropic sobre el contexto común (findings + stats +
  marco normativo) — pagamos la construcción una vez, reusamos en cada sección.
- Longitud máxima por sección parametrizada por audiencia.
- Temperatura baja (0.2) para consistencia.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

from agents.report_designer.models import ReportRequest, ReportSection, FindingRef


# Rol del redactor por audiencia
ROLE_PROMPTS = {
    "technical": (
        "Sos un/a redactor/a de informes de observación electoral con formación en "
        "derecho internacional de los derechos humanos. Escribís con rigor académico, "
        "citás normativa específica (artículos, resoluciones), declarás limitaciones "
        "explícitamente. Lector objetivo: observador/a internacional o jurista."
    ),
    "executive": (
        "Sos un/a analista que redacta para decisores de alto nivel. Escribís denso "
        "y accionable. Frases cortas. Bullets con verbo al inicio. Conclusiones en "
        "negrita. Lector objetivo: jefatura de misión, embajadores, contrapartes "
        "institucionales."
    ),
    "press": (
        "Sos un/a periodista de datos. Escribís frases declarativas breves con una "
        "cita textual destacada. Sin jerga. El público lo lee en 60 segundos."
    ),
    "international": (
        "You are an electoral observation mission report writer trained in international "
        "human rights law. Write with academic rigor in English. Cite specific norms "
        "(ICCPR/ACHR/IADC articles). Compare with regional standards (OAS, EU EOM, "
        "Carter Center methodologies) when relevant."
    ),
}

# Longitud máxima por sección según audiencia (palabras)
MAX_WORDS = {
    "technical": 450,
    "executive": 120,
    "press": 80,
    "international": 350,
}

# Instrucciones específicas por section_id (la semántica de la sección)
SECTION_INSTRUCTIONS = {
    "portada": "Redactá la portada del informe. Debe incluir: nombre de la misión, país, jornada electoral, período cubierto, número de hallazgos base, audiencia. Sin conclusiones. Tono neutro institucional.",
    "resumen_ejecutivo": "Redactá el resumen ejecutivo. Debe incluir: (1) estado del proceso, (2) 2-3 cifras clave más importantes, (3) los 3 temas críticos dominantes, (4) una conclusión sobre legitimidad del proceso. Máximo 4 párrafos.",
    "declaracion_1_pagina": "Declaración preliminar de una página. Tono: observador internacional. Estructura: (a) qué observamos, (b) qué encontramos, (c) qué implica para la integridad del proceso. Citá al menos 2 hallazgos de severidad high/critical con su fuente.",
    "metodologia": "Describí la metodología PEIRS: frecuencia del Hunter RSS (4h), fuentes monitoreadas, clasificación con Claude Sonnet, dedupe semántico, priorización ponderada. Citá los instrumentos normativos aplicados (ICCPR, CADH, CDI, Constitución país).",
    "cifras_clave": "Presentá las cifras principales en bullets. Incluí: total findings, distribución por severidad, días cubiertos, fuentes activas, top 3 temas. Lenguaje directo.",
    "contexto": "Contextualizá brevemente el proceso electoral del país: sistema electoral, antecedentes de estabilidad institucional, cualquier particularidad del ciclo actual. Máximo 3 párrafos.",
    "timeline_hallazgos": "Describí la evolución temporal de los hallazgos: cuándo fueron los picos, qué los explica. Referíte a la visualización adjunta.",
    "temas_criticos": "Para cada uno de los top 5 temas detectados, escribí un bloque con: título del tema, cantidad de hallazgos, los 2-3 hallazgos más ilustrativos con cita textual breve y link a fuente. Cada bloque máximo 120 palabras.",
    "3_temas_mas_criticos": "Los 3 temas con más hallazgos high/critical. Para cada uno: nombre, cifra, 1 hallazgo representativo con su fuente. Formato numerado.",
    "derechos_vulnerados": "Marco de derechos vulnerados. Agrupá los hallazgos por instrumento normativo (ICCPR Art. 25, CADH Art. 23, CADH Art. 13, ICCPR Art. 19(2), CDI Art. 3). Cuántos hallazgos los invocan.",
    "responsabilidad_penal": "Describí las acciones penales, administrativas y de control documentadas durante el ciclo. Citá actores institucionales específicos (Fiscalía, Contraloría, JNJ, JNE) y hallazgos concretos con fuente.",
    "recomendaciones": "Recomendaciones en 3 niveles temporales: corto plazo (48-72h), mediano (1-6 meses), largo (pre-próximas elecciones). Cada recomendación debe estar anclada en un hallazgo específico del informe.",
    "recomendaciones_prioritarias": "Las 3 recomendaciones más urgentes. Cada una con el hallazgo que la motiva y el órgano responsable de implementarla.",
    "titulo": "Generá un título periodístico breve (máximo 15 palabras) que capture el tema más relevante del ciclo.",
    "bajada": "Bajada periodística (30-50 palabras) que resuma los 2-3 hallazgos más importantes con cifras y fuente.",
    "infografia_unica": "Texto compacto para una infografía: cifras esenciales separadas por punto medio o barras.",
    "3_hallazgos_mas_cita": "Los 3 hallazgos con mayor priority_score. Formato numerado. Cada uno con cita textual breve y link de fuente.",
    "anexo_fuentes": "Listado de fuentes citadas agrupadas por tipo: medios RSS, normativa nacional, instrumentos internacionales, jurisprudencia. Sin narrativa, solo enumeración.",
    # English
    "cover": "Write the report cover. Include: mission name, country, election date, period covered, number of findings, audience. Neutral institutional tone.",
    "executive_summary": "Executive summary: state of process, key figures, 3 dominant critical themes, conclusion on process integrity. Max 4 paragraphs.",
    "context_comparative": "Comparative context: place the country on international democratic indicators (Freedom House, V-Dem). Reference OAS/EU EOM methodologies applicable.",
    "findings": "Describe the findings by theme with top citations and source links.",
    "rights_framework": "Rights framework: group findings by instrument (ICCPR Art. 25, ACHR Art. 23, ACHR Art. 13, ICCPR Art. 19(2), IADC Art. 3).",
    "recommendations": "Recommendations in 3 time horizons: short (48-72h), medium (1-6 months), long (pre-next-elections). Each anchored to a specific finding.",
    "references": "Sources cited, grouped by type.",
    "methodology": "PEIRS methodology: Hunter RSS 4h frequency, monitored sources, Claude Sonnet classification, semantic dedup, weighted prioritization. Cite applied normative instruments.",
}


def _findings_context(findings: List[FindingRef], max_items: int = 15) -> str:
    """Serializa findings en texto compacto para el prompt."""
    if not findings:
        return "(Sin hallazgos específicos asignados a esta sección; usá contexto general del informe.)"
    lines = []
    for i, f in enumerate(findings[:max_items]):
        src = f.source_name or "sin-fuente"
        url = f.source_url or ""
        cat = f.category
        sev = f.severity
        text = (f.finding or "")[:250]
        date = (f.recorded_at or "")[:10]
        lines.append(f"[{i+1}] [{sev}] [{cat}] {date} | {src}: {text} | URL: {url}")
    return "\n".join(lines)


def _stats_context(stats) -> str:
    if not stats:
        return ""
    return (
        f"Total findings: {stats.total_findings} | "
        f"Critical: {stats.critical} | High: {stats.high} | Medium: {stats.medium} | "
        f"Low: {stats.low} | Info: {stats.info} | "
        f"Days covered: {stats.days_covered} | Sources: {stats.sources_count}"
    )


def _themes_context(theme_ranking: List[Dict]) -> str:
    if not theme_ranking:
        return ""
    lines = ["TEMAS CLASIFICADOS (ordenados por densidad high+critical):"]
    for i, t in enumerate(theme_ranking[:8]):
        lines.append(
            f"  {i+1}. {t['label']}: {t['total']} hallazgos ({t['high_critical']} high/critical)"
        )
    return "\n".join(lines)


async def compose_section(
    llm,
    section: ReportSection,
    req: ReportRequest,
    stats,
    theme_ranking: List[Dict],
    top_findings_overall: List[FindingRef],
    country_context: str = "",
) -> str:
    """
    Genera la narrativa de UNA sección usando Claude.
    Fallback: si llm=None o falla la llamada, retorna string vacío y el caller
    usa la plantilla Fase B como fallback.
    """
    if llm is None:
        return ""

    role = ROLE_PROMPTS.get(req.audience, ROLE_PROMPTS["technical"])
    instructions = SECTION_INSTRUCTIONS.get(section.section_id, f"Redactá la sección '{section.title}'.")
    max_words = MAX_WORDS.get(req.audience, 350)
    language_note = "Responde en español rioplatense-peruano formal." if req.language == "es" else "Respond in formal English."

    # Contexto específico de la sección
    section_findings = _findings_context(section.findings, max_items=12)
    overall_findings = _findings_context(top_findings_overall[:10], max_items=10)
    themes = _themes_context(theme_ranking)
    stats_line = _stats_context(stats)

    system_prompt = f"""{role}

CONTEXTO DEL INFORME (compartido entre todas las secciones — prompt caching):

País: {req.country_code}
Audiencia: {req.audience}
Período cubierto: últimos {req.period_days} días
Fecha del informe: {stats.generated_at[:10] if stats and stats.generated_at else ''}

ESTADÍSTICAS: {stats_line}

{themes}

HALLAZGOS PRIORITARIOS GLOBALES (referencia, con link de fuente):
{overall_findings}

CONTEXTO PAÍS:
{country_context or 'Sin contexto país adicional provisto.'}

REGLAS DE REDACCIÓN:
- NO inventes cifras, artículos o resoluciones. Solo usá las que aparecen arriba o en la
  normativa internacional de público conocimiento (ICCPR, CADH, CDI).
- Cada afirmación sustantiva debe tener una fuente citable (medio RSS con URL, o
  instrumento normativo con artículo).
- Formato markdown. Para citas de URL: [texto](url).
- Negrita con **doble asterisco** para énfasis clave.
- Listas con guiones.
- {language_note}
- Máximo {max_words} palabras.
- No incluyas el título de la sección (ya se renderiza automáticamente).
- No uses frases genéricas como "es importante notar" o "cabe señalar".
"""

    user_prompt = f"""SECCIÓN A REDACTAR: {section.title} ({section.section_id})

INSTRUCCIONES ESPECÍFICAS:
{instructions}

HALLAZGOS ASIGNADOS ESPECÍFICAMENTE A ESTA SECCIÓN:
{section_findings}

Redactá ahora el contenido de la sección. Markdown. Máximo {max_words} palabras.
"""

    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        text = response.content.strip() if hasattr(response, "content") else str(response)
        # Limpieza: sacar encabezados duplicados si Claude los incluyó pese a la instrucción
        if text.startswith("## ") or text.startswith("# "):
            lines = text.split("\n", 1)
            text = lines[1].strip() if len(lines) > 1 else ""
        return text
    except Exception as e:
        # Fallback silencioso al caller; loggeamos el error
        print(f"[Composer] Error generando sección {section.section_id}: {type(e).__name__}: {e}")
        return ""


async def compose_all_sections(
    llm,
    sections: List[ReportSection],
    req: ReportRequest,
    stats,
    theme_ranking: List[Dict],
    top_findings_overall: List[FindingRef],
    country_context: str = "",
    concurrency_limit: int = 3,
) -> Dict[str, str]:
    """
    Genera narrativas para todas las secciones con concurrencia limitada.
    Retorna {section_id: narrative}. Las secciones que fallen devuelven "".
    """
    sem = asyncio.Semaphore(concurrency_limit)

    async def _compose_one(section: ReportSection):
        async with sem:
            narrative = await compose_section(
                llm=llm,
                section=section,
                req=req,
                stats=stats,
                theme_ranking=theme_ranking,
                top_findings_overall=top_findings_overall,
                country_context=country_context,
            )
            return section.section_id, narrative

    results = await asyncio.gather(*[_compose_one(s) for s in sections], return_exceptions=True)

    out: Dict[str, str] = {}
    for r in results:
        if isinstance(r, Exception):
            continue
        sid, narrative = r
        if narrative:
            out[sid] = narrative
    return out
