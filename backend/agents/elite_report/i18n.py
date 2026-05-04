"""Internacionalización del Elite Report (chrome del informe).

El composer ya respeta `req.language` para la narrativa de los 12 capítulos
(via prompts). Pero TODO el "chrome" del informe (cover, footer, TOC, anexos,
labels de viz) estaba hardcoded en español. Este módulo centraliza los strings
para soportar es/en/pt.

Uso:
    from agents.elite_report.i18n import t

    t("en", "cover.findings_monitored") -> "findings monitored"
    t("es", "cover.findings_monitored") -> "hallazgos monitoreados"
    t("pt", "cover.findings_monitored") -> "registros monitorados"

Si la clave no existe en el idioma pedido, cae al español como default.
"""
from __future__ import annotations
from typing import Dict


_STRINGS: Dict[str, Dict[str, str]] = {
    # ── Cover ────────────────────────────────────────────────────────
    "cover.pretitle": {
        "es": "Misión de Observación Electoral · PEIRS",
        "en": "Electoral Observation Mission · PEIRS",
        "pt": "Missão de Observação Eleitoral · PEIRS",
    },
    "cover.elections_year": {
        "es": "Elecciones",
        "en": "Elections",
        "pt": "Eleições",
    },
    "cover.election_day": {
        "es": "Jornada del",
        "en": "Election day",
        "pt": "Jornada de",
    },
    "cover.findings_monitored": {
        "es": "hallazgos monitoreados",
        "en": "findings monitored",
        "pt": "registros monitorados",
    },
    "cover.critical": {
        "es": "críticos",
        "en": "critical",
        "pt": "críticos",
    },
    "cover.high": {
        "es": "altos",
        "en": "high",
        "pt": "altos",
    },
    "cover.days_monitoring": {
        "es": "días de monitoreo continuo",
        "en": "days of continuous monitoring",
        "pt": "dias de monitoramento contínuo",
    },
    "cover.mission": {
        "es": "Misión:",
        "en": "Mission:",
        "pt": "Missão:",
    },
    "cover.lead_observer": {
        "es": "Observadora responsable:",
        "en": "Lead observer:",
        "pt": "Observadora responsável:",
    },
    "cover.organization": {
        "es": "Organización emisora:",
        "en": "Issuing organization:",
        "pt": "Organização emissora:",
    },
    "cover.report_number": {
        "es": "N° de informe:",
        "en": "Report number:",
        "pt": "N° do relatório:",
    },
    "cover.period": {
        "es": "Período cubierto:",
        "en": "Period covered:",
        "pt": "Período coberto:",
    },
    "cover.audience": {
        "es": "Audiencia:",
        "en": "Audience:",
        "pt": "Audiência:",
    },
    "cover.language": {
        "es": "Idioma:",
        "en": "Language:",
        "pt": "Idioma:",
    },
    "cover.generated": {
        "es": "Generado:",
        "en": "Generated:",
        "pt": "Gerado:",
    },

    # ── Tipos de informe ─────────────────────────────────────────────
    "report_type.pre_electoral": {
        "es": "Informe Pre-Electoral",
        "en": "Pre-Electoral Report",
        "pt": "Relatório Pré-Eleitoral",
    },
    "report_type.jornada": {
        "es": "Informe de Jornada",
        "en": "Election Day Report",
        "pt": "Relatório do Dia da Eleição",
    },
    "report_type.preliminary": {
        "es": "Informe Preliminar",
        "en": "Preliminary Report",
        "pt": "Relatório Preliminar",
    },
    "report_type.final": {
        "es": "Informe Final",
        "en": "Final Report",
        "pt": "Relatório Final",
    },
    "report_type.ad_hoc": {
        "es": "Informe Ad-hoc",
        "en": "Ad-hoc Report",
        "pt": "Relatório Ad-hoc",
    },

    # ── Disclosure ───────────────────────────────────────────────────
    "disclosure.headline": {
        "es": "DEMOCRAC.IA no legitima ni valida resultados electorales.",
        "en": "DEMOCRAC.IA does not legitimize or validate electoral results.",
        "pt": "DEMOCRAC.IA não legitima nem valida resultados eleitorais.",
    },
    "disclosure.body": {
        "es": "Este informe emite inteligencia electoral con trazabilidad verificable bajo estándares internacionales de observación electoral, sin sesgo político-partidario. Los datos son para uso analítico de autoridades electorales, organismos multilaterales, observadores acreditados y academia. Cada hallazgo cita fuente primaria con URL pública; los bloques sin verificación independiente fueron postergados antes que publicados.",
        "en": "This report issues electoral intelligence with verifiable traceability under international standards for electoral observation, without political-partisan bias. Data is for analytical use by electoral authorities, multilateral organizations, accredited observers, and academia. Every finding cites a primary source with public URL; blocks without independent verification were postponed rather than published.",
        "pt": "Este relatório emite inteligência eleitoral com rastreabilidade verificável sob padrões internacionais de observação eleitoral, sem viés político-partidário. Os dados são para uso analítico por autoridades eleitorais, organismos multilaterais, observadores credenciados e academia. Cada registro cita fonte primária com URL pública; blocos sem verificação independente foram adiados em vez de publicados.",
    },

    # ── Footer ───────────────────────────────────────────────────────
    "footer.disclosure_short": {
        "es": "Inteligencia electoral con trazabilidad verificable bajo estándares internacionales de observación electoral.",
        "en": "Electoral intelligence with verifiable traceability under international standards for electoral observation.",
        "pt": "Inteligência eleitoral com rastreabilidade verificável sob padrões internacionais de observação eleitoral.",
    },
    "footer.pipeline_meta": {
        "es": "Pipeline 6 etapas · SVG server-side · Citas APA 7",
        "en": "6-stage pipeline · Server-side SVG · APA 7 citations",
        "pt": "Pipeline de 6 etapas · SVG server-side · Citações APA 7",
    },

    # ── TOC ──────────────────────────────────────────────────────────
    "toc.title": {
        "es": "Tabla de contenidos",
        "en": "Table of contents",
        "pt": "Índice",
    },
    "toc.cap_prefix": {
        "es": "Cap. ",
        "en": "Ch. ",
        "pt": "Cap. ",
    },
    "toc.declaration_label": {
        "es": "Declaración",
        "en": "Declaration",
        "pt": "Declaração",
    },

    # ── Anexos ───────────────────────────────────────────────────────
    "appendix.a.title": {
        "es": "Anexo A — Metodología técnica",
        "en": "Appendix A — Technical methodology",
        "pt": "Anexo A — Metodologia técnica",
    },
    "appendix.b.title": {
        "es": "Anexo B — Bibliografía (APA 7)",
        "en": "Appendix B — Bibliography (APA 7)",
        "pt": "Anexo B — Bibliografia (APA 7)",
    },
    "appendix.c.title": {
        "es": "Anexo C — Hallazgos completos",
        "en": "Appendix C — Complete findings",
        "pt": "Anexo C — Registros completos",
    },
    "appendix.a.label_short": {
        "es": "A",
        "en": "A",
        "pt": "A",
    },
    "appendix.a.title_short": {
        "es": "Metodología técnica",
        "en": "Technical methodology",
        "pt": "Metodologia técnica",
    },
    "appendix.b.title_short": {
        "es": "Bibliografía APA",
        "en": "APA Bibliography",
        "pt": "Bibliografia APA",
    },
    "appendix.c.title_short": {
        "es": "Hallazgos completos",
        "en": "Complete findings",
        "pt": "Registros completos",
    },
    "appendix.b.intro": {
        "es": "referencias ordenadas alfabéticamente.",
        "en": "references in alphabetical order.",
        "pt": "referências em ordem alfabética.",
    },
    "appendix.c.placeholder": {
        "es": "Listado completo de hallazgos del Hunter disponible en formato Markdown descargable. Incluye entry_id, fecha, severidad, categoría, finding, medio, URL y priority_score.",
        "en": "Complete list of Hunter findings available in downloadable Markdown format. Includes entry_id, date, severity, category, finding, source, URL, and priority_score.",
        "pt": "Lista completa de registros do Hunter disponível em formato Markdown para download. Inclui entry_id, data, severidade, categoria, registro, mídia, URL e priority_score.",
    },

    # ── Chapter titles (deben coincidir con CHAPTER_CATALOG) ─────────
    "chapter.declaracion_preliminar": {
        "es": "Declaración preliminar",
        "en": "Preliminary declaration",
        "pt": "Declaração preliminar",
    },
    "chapter.contexto_historico": {
        "es": "Contexto histórico",
        "en": "Historical context",
        "pt": "Contexto histórico",
    },
    "chapter.marco_juridico": {
        "es": "Marco jurídico aplicable",
        "en": "Applicable legal framework",
        "pt": "Marco jurídico aplicável",
    },
    "chapter.sistema_electoral": {
        "es": "Sistema electoral",
        "en": "Electoral system",
        "pt": "Sistema eleitoral",
    },
    "chapter.fase_pre_electoral": {
        "es": "Fase pre-electoral",
        "en": "Pre-electoral phase",
        "pt": "Fase pré-eleitoral",
    },
    "chapter.jornada_electoral": {
        "es": "Jornada electoral",
        "en": "Election day",
        "pt": "Dia da eleição",
    },
    "chapter.escrutinio_computo": {
        "es": "Escrutinio y cómputo",
        "en": "Vote counting and tabulation",
        "pt": "Apuração e totalização",
    },
    "chapter.post_electoral": {
        "es": "Post-electoral",
        "en": "Post-electoral",
        "pt": "Pós-eleitoral",
    },
    "chapter.derechos_vulnerados": {
        "es": "Derechos vulnerados",
        "en": "Rights violations",
        "pt": "Direitos violados",
    },
    "chapter.analisis_predictivo": {
        "es": "Análisis predictivo",
        "en": "Predictive analysis",
        "pt": "Análise preditiva",
    },
    "chapter.conclusiones": {
        "es": "Conclusiones",
        "en": "Conclusions",
        "pt": "Conclusões",
    },
    "chapter.recomendaciones": {
        "es": "Recomendaciones",
        "en": "Recommendations",
        "pt": "Recomendações",
    },
    "chapter.ia_regulacion": {
        "es": "Inteligencia Artificial en el proceso electoral",
        "en": "Artificial Intelligence in the electoral process",
        "pt": "Inteligência Artificial no processo eleitoral",
    },

    # ── SVG: severidades ─────────────────────────────────────────────
    "sev.critical": {"es": "Crítico", "en": "Critical", "pt": "Crítico"},
    "sev.high":     {"es": "Alto",    "en": "High",     "pt": "Alto"},
    "sev.medium":   {"es": "Medio",   "en": "Medium",   "pt": "Médio"},
    "sev.low":      {"es": "Bajo",    "en": "Low",      "pt": "Baixo"},
    "sev.info":     {"es": "Info",    "en": "Info",     "pt": "Info"},

    # ── SVG: estados generales ───────────────────────────────────────
    "viz.no_data_title": {
        "es": "Sin datos disponibles",
        "en": "No data available",
        "pt": "Sem dados disponíveis",
    },
    "viz.empty_state_short": {
        "es": "Sin datos",
        "en": "No data",
        "pt": "Sem dados",
    },
    "viz.pending": {
        "es": "Pendiente",
        "en": "Pending",
        "pt": "Pendente",
    },

    # ── Findings cited block ─────────────────────────────────────────
    "findings_cited.heading": {
        "es": "HALLAZGOS CITADOS",
        "en": "CITED FINDINGS",
        "pt": "REGISTROS CITADOS",
    },

    # ── Header de informe markdown ───────────────────────────────────
    "md.header_title": {
        "es": "PEIRS Elite Report",
        "en": "PEIRS Elite Report",
        "pt": "PEIRS Elite Report",
    },
    "md.classification_label": {
        "es": "Clasificación:",
        "en": "Classification:",
        "pt": "Classificação:",
    },
}


def t(language: str, key: str, default: str | None = None) -> str:
    """Lookup i18n. Cae a 'es' si la clave existe en español pero no en el
    idioma pedido (defensive). Si la clave no existe en absoluto, devuelve
    el default o el key mismo."""
    lang = (language or "es").lower()
    bundle = _STRINGS.get(key)
    if bundle is None:
        return default if default is not None else key
    return bundle.get(lang) or bundle.get("es") or default or key
