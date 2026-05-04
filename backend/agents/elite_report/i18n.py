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

    # ─────────────────────────────────────────────────────────────────
    # Visualizaciones — title + caption
    # ─────────────────────────────────────────────────────────────────
    "viz.timeseries_multi.title": {
        "es": "Trayectoria histórica — índices democráticos",
        "en": "Historical trajectory — democratic indices",
        "pt": "Trajetória histórica — índices democráticos",
    },
    "viz.timeseries_multi.caption": {
        "es": "Series V-Dem, Freedom House, PEI y RSF de los últimos 10 años.",
        "en": "V-Dem, Freedom House, PEI and RSF series for the last 10 years.",
        "pt": "Séries V-Dem, Freedom House, PEI e RSF dos últimos 10 anos.",
    },
    "viz.events_timeline.title": {
        "es": "Eventos críticos del período observado",
        "en": "Critical events of the observed period",
        "pt": "Eventos críticos do período observado",
    },
    "viz.events_timeline.caption": {
        "es": "Top hallazgos ordenados por severidad y fecha.",
        "en": "Top findings ranked by severity and date.",
        "pt": "Principais registros ordenados por severidade e data.",
    },
    "viz.matrix_normativa.title": {
        "es": "Marco normativo aplicable",
        "en": "Applicable legal framework",
        "pt": "Marco normativo aplicável",
    },
    "viz.matrix_normativa.caption": {
        "es": "Instrumentos ordenados por jerarquía normativa.",
        "en": "Instruments ordered by normative hierarchy.",
        "pt": "Instrumentos ordenados por hierarquia normativa.",
    },
    "viz.flow_chart_voting.title": {
        "es": "Cadena del voto — actores y custodia",
        "en": "Vote chain — actors and custody",
        "pt": "Cadeia do voto — atores e custódia",
    },
    "viz.flow_chart_voting.caption": {
        "es": "Padrón → Mesa → Acta → STAE/SCE → Cómputo → Proclamación.",
        "en": "Roll → Polling station → Tally sheet → STAE/SCE → Tabulation → Proclamation.",
        "pt": "Cadastro → Mesa → Ata → STAE/SCE → Apuração → Proclamação.",
    },
    "viz.network_institutions.title": {
        "es": "Red institucional electoral",
        "en": "Electoral institutional network",
        "pt": "Rede institucional eleitoral",
    },
    "viz.network_institutions.caption": {
        "es": "JNE (árbitro), ONPE (organización), RENIEC (padrón) y sus interacciones.",
        "en": "JNE (arbiter), ONPE (organization), RENIEC (electoral roll) and their interactions.",
        "pt": "JNE (árbitro), ONPE (organização), RENIEC (cadastro) e suas interações.",
    },
    "viz.phase_timeline.title": {
        "es": "Distribución de hallazgos por fase electoral",
        "en": "Distribution of findings by electoral phase",
        "pt": "Distribuição de registros por fase eleitoral",
    },
    "viz.phase_timeline.caption": {
        "es": "Barras apiladas por severidad a lo largo del ciclo.",
        "en": "Stacked bars by severity along the cycle.",
        "pt": "Barras empilhadas por severidade ao longo do ciclo.",
    },
    "viz.hourly_timeline.title": {
        "es": "Jornada — eventos por hora",
        "en": "Election day — events by hour",
        "pt": "Dia da eleição — eventos por hora",
    },
    "viz.hourly_timeline.caption": {
        "es": "Volumen y severidad máxima de hallazgos por franja horaria.",
        "en": "Volume and maximum severity of findings by time slot.",
        "pt": "Volume e severidade máxima de registros por faixa horária.",
    },
    "viz.map_regions_affected.title": {
        "es": "Regiones afectadas — intensidad por incidentes",
        "en": "Affected regions — incident intensity",
        "pt": "Regiões afetadas — intensidade por incidentes",
    },
    "viz.map_regions_affected.caption": {
        "es": "Conteo de hallazgos por región (location matching).",
        "en": "Findings count by region (location matching).",
        "pt": "Contagem de registros por região (location matching).",
    },
    "viz.progress_chart.title": {
        "es": "Progreso de actas procesadas",
        "en": "Tally sheet processing progress",
        "pt": "Progresso de atas processadas",
    },
    "viz.progress_chart.caption": {
        "es": "Curva temporal del % escrutado (estimación).",
        "en": "Temporal curve of % counted (estimate).",
        "pt": "Curva temporal do % apurado (estimativa).",
    },
    "viz.integrity_incidents_grid.title": {
        "es": "Incidentes de integridad — región × categoría",
        "en": "Integrity incidents — region × category",
        "pt": "Incidentes de integridade — região × categoria",
    },
    "viz.integrity_incidents_grid.caption": {
        "es": "Intensidad cromática proporcional al conteo.",
        "en": "Chromatic intensity proportional to the count.",
        "pt": "Intensidade cromática proporcional à contagem.",
    },
    "viz.actor_network.title": {
        "es": "Red de actores institucionales",
        "en": "Institutional actor network",
        "pt": "Rede de atores institucionais",
    },
    "viz.actor_network.caption": {
        "es": "Acciones e intervenciones cruzadas observadas.",
        "en": "Observed cross-cutting actions and interventions.",
        "pt": "Ações e intervenções cruzadas observadas.",
    },
    "viz.judicial_timeline.title": {
        "es": "Cronología judicial",
        "en": "Judicial timeline",
        "pt": "Cronologia judicial",
    },
    "viz.judicial_timeline.caption": {
        "es": "Acciones legales documentadas en el período.",
        "en": "Legal actions documented during the period.",
        "pt": "Ações legais documentadas no período.",
    },
    "viz.heatmap_rights.title": {
        "es": "Heatmap derechos × categorías",
        "en": "Rights × categories heatmap",
        "pt": "Heatmap direitos × categorias",
    },
    "viz.heatmap_rights.caption": {
        "es": "Intensidad = cantidad de hallazgos que invocan cada derecho.",
        "en": "Intensity = number of findings that invoke each right.",
        "pt": "Intensidade = número de registros que invocam cada direito.",
    },
    "viz.compliance_matrix.title": {
        "es": "Matriz de cumplimiento ICCPR / CADH",
        "en": "ICCPR / ACHR compliance matrix",
        "pt": "Matriz de cumprimento ICCPR / CADH",
    },
    "viz.compliance_matrix.caption": {
        "es": "Estado por artículo según severidad de hallazgos vinculados.",
        "en": "Status per article based on severity of linked findings.",
        "pt": "Status por artigo conforme severidade dos registros vinculados.",
    },
    "viz.forecast_chart.title": {
        "es": "Escenarios probabilísticos con bandas de confianza",
        "en": "Probabilistic scenarios with confidence bands",
        "pt": "Cenários probabilísticos com faixas de confiança",
    },
    "viz.forecast_chart.caption": {
        "es": "Horizonte de 2 semanas post-informe.",
        "en": "2-week horizon post-report.",
        "pt": "Horizonte de 2 semanas pós-relatório.",
    },
    "viz.scenario_probability.title": {
        "es": "Probabilidad por escenario (vista compacta)",
        "en": "Probability per scenario (compact view)",
        "pt": "Probabilidade por cenário (visão compacta)",
    },
    "viz.early_warning_meter.title": {
        "es": "Medidor de alerta temprana",
        "en": "Early warning meter",
        "pt": "Medidor de alerta antecipada",
    },
    "viz.early_warning_meter.caption": {
        "es": "Nivel actual de riesgo según severidad agregada y forecast.",
        "en": "Current risk level based on aggregated severity and forecast.",
        "pt": "Nível atual de risco conforme severidade agregada e forecast.",
    },
    "viz.semaphore_institutional.title": {
        "es": "Evaluación institucional por órgano",
        "en": "Institutional assessment by body",
        "pt": "Avaliação institucional por órgão",
    },
    "viz.semaphore_institutional.caption": {
        "es": "Semáforo de estado al cierre del período observado.",
        "en": "Status signal at the close of the observed period.",
        "pt": "Sinal de status ao final do período observado.",
    },
    "viz.dimensions_radar.title": {
        "es": "8 Dimensiones PEIRS",
        "en": "PEIRS 8 dimensions",
        "pt": "8 dimensões PEIRS",
    },
    "viz.dimensions_radar.caption": {
        "es": "Evaluación cualitativa ajustada por hallazgos del ciclo.",
        "en": "Qualitative assessment adjusted by cycle findings.",
        "pt": "Avaliação qualitativa ajustada pelos registros do ciclo.",
    },
    "viz.matrix_recommendations.title": {
        "es": "Matriz de recomendaciones priorizadas",
        "en": "Prioritized recommendations matrix",
        "pt": "Matriz de recomendações priorizadas",
    },
    "viz.matrix_recommendations.caption": {
        "es": "Recomendación × destinatario × prioridad × horizonte temporal.",
        "en": "Recommendation × addressee × priority × time horizon.",
        "pt": "Recomendação × destinatário × prioridade × horizonte temporal.",
    },
    "viz.system_architecture.title": {
        "es": "Arquitectura del sistema electoral con IA",
        "en": "AI-enabled electoral system architecture",
        "pt": "Arquitetura do sistema eleitoral com IA",
    },
    "viz.system_architecture.caption": {
        "es": "Capas STAE → SCE → SPR con flujo de datos. Badges indican estado de auditoría pública.",
        "en": "Layers STAE → SCE → SPR with data flow. Badges indicate public audit status.",
        "pt": "Camadas STAE → SCE → SPR com fluxo de dados. Selos indicam status de auditoria pública.",
    },

    # ─────────────────────────────────────────────────────────────────
    # Datos internos de SVG: status, niveles, headers de columnas
    # ─────────────────────────────────────────────────────────────────
    # Headers en uppercase (renderers internal text)
    "viz.header.electoral_network": {
        "es": "RED INSTITUCIONAL ELECTORAL",
        "en": "ELECTORAL INSTITUTIONAL NETWORK",
        "pt": "REDE INSTITUCIONAL ELEITORAL",
    },
    "viz.header.vote_chain": {
        "es": "CADENA DEL VOTO",
        "en": "VOTE CHAIN",
        "pt": "CADEIA DO VOTO",
    },
    "viz.header.compliance_matrix": {
        "es": "MATRIZ DE CUMPLIMIENTO ICCPR / CADH",
        "en": "ICCPR / ACHR COMPLIANCE MATRIX",
        "pt": "MATRIZ DE CUMPRIMENTO ICCPR / CADH",
    },
    "viz.header.recommendations_matrix": {
        "es": "RECOMENDACIONES — DESTINATARIO × PRIORIDAD × HORIZONTE",
        "en": "RECOMMENDATIONS — ADDRESSEE × PRIORITY × HORIZON",
        "pt": "RECOMENDAÇÕES — DESTINATÁRIO × PRIORIDADE × HORIZONTE",
    },
    "viz.header.actor_network": {
        "es": "RED DE ACTORES — ACCIONES E INTERVENCIONES",
        "en": "ACTOR NETWORK — ACTIONS AND INTERVENTIONS",
        "pt": "REDE DE ATORES — AÇÕES E INTERVENÇÕES",
    },
    "viz.header.judicial_chronology": {
        "es": "CRONOLOGÍA JUDICIAL",
        "en": "JUDICIAL TIMELINE",
        "pt": "CRONOLOGIA JUDICIAL",
    },
    "viz.header.regions_affected": {
        "es": "REGIONES AFECTADAS — INTENSIDAD POR INCIDENTES",
        "en": "AFFECTED REGIONS — INTENSITY BY INCIDENTS",
        "pt": "REGIÕES AFETADAS — INTENSIDADE POR INCIDENTES",
    },
    "viz.header.electoral_day": {
        "es": "JORNADA — EVENTOS POR HORA",
        "en": "ELECTION DAY — EVENTS BY HOUR",
        "pt": "DIA DA ELEIÇÃO — EVENTOS POR HORA",
    },
    "viz.header.tally_progress": {
        "es": "PROGRESO DE ACTAS PROCESADAS",
        "en": "TALLY SHEET PROCESSING PROGRESS",
        "pt": "PROGRESSO DE ATAS PROCESSADAS",
    },
    "viz.header.integrity_grid": {
        "es": "INCIDENTES DE INTEGRIDAD — REGIÓN × CATEGORÍA",
        "en": "INTEGRITY INCIDENTS — REGION × CATEGORY",
        "pt": "INCIDENTES DE INTEGRIDADE — REGIÃO × CATEGORIA",
    },
    "viz.header.early_warning": {
        "es": "ALERTA TEMPRANA — NIVEL DE RIESGO",
        "en": "EARLY WARNING — RISK LEVEL",
        "pt": "ALERTA ANTECIPADA — NÍVEL DE RISCO",
    },
    "viz.header.system_architecture": {
        "es": "ARQUITECTURA DEL SISTEMA ELECTORAL",
        "en": "ELECTORAL SYSTEM ARCHITECTURE",
        "pt": "ARQUITETURA DO SISTEMA ELEITORAL",
    },

    # Status labels en flow_chart_voting
    "viz.status.ok":      {"es": "OK",       "en": "OK",       "pt": "OK"},
    "viz.status.warn":    {"es": "Atención", "en": "Warning",  "pt": "Atenção"},
    "viz.status.fail":    {"es": "Falla",    "en": "Failure",  "pt": "Falha"},
    "viz.status.pending": {"es": "Pendiente","en": "Pending",  "pt": "Pendente"},

    # Early warning gauge bands
    "viz.gauge.green":  {"es": "VERDE",   "en": "GREEN",   "pt": "VERDE"},
    "viz.gauge.amber":  {"es": "ÁMBAR",   "en": "AMBER",   "pt": "ÂMBAR"},
    "viz.gauge.orange": {"es": "NARANJA", "en": "ORANGE",  "pt": "LARANJA"},
    "viz.gauge.red":    {"es": "ROJO",    "en": "RED",     "pt": "VERMELHO"},
    "viz.gauge.risk_label_prefix": {
        "es": "RIESGO ",
        "en": "RISK ",
        "pt": "RISCO ",
    },

    # Compliance matrix status labels
    "viz.compliance.ok":      {"es": "CUMPLE",   "en": "COMPLIES",   "pt": "CUMPRE"},
    "viz.compliance.partial": {"es": "PARCIAL",  "en": "PARTIAL",    "pt": "PARCIAL"},
    "viz.compliance.breach":  {"es": "INCUMPLE", "en": "BREACH",     "pt": "INFRINGE"},
    "viz.compliance.unknown": {"es": "S/D",      "en": "N/D",        "pt": "S/D"},

    # Compliance matrix column headers
    "viz.compliance.col.article":   {"es": "ARTÍCULO",  "en": "ARTICLE",   "pt": "ARTIGO"},
    "viz.compliance.col.topic":     {"es": "TEMA",      "en": "TOPIC",     "pt": "TEMA"},
    "viz.compliance.col.evidence":  {"es": "EVIDENCIA", "en": "EVIDENCE",  "pt": "EVIDÊNCIA"},
    "viz.compliance.col.status":    {"es": "ESTADO",    "en": "STATUS",    "pt": "STATUS"},
    "viz.compliance.evidence_unit": {"es": "ev.",       "en": "ev.",       "pt": "ev."},

    # Recommendations matrix column headers
    "viz.rec.col.recommendation": {"es": "RECOMENDACIÓN","en": "RECOMMENDATION","pt": "RECOMENDAÇÃO"},
    "viz.rec.col.addressee":      {"es": "DESTINATARIO", "en": "ADDRESSEE",     "pt": "DESTINATÁRIO"},
    "viz.rec.col.priority":       {"es": "PRIORIDAD",    "en": "PRIORITY",      "pt": "PRIORIDADE"},
    "viz.rec.col.horizon":        {"es": "HORIZONTE",    "en": "HORIZON",       "pt": "HORIZONTE"},

    # Other internal labels
    "viz.legend.majority": {
        "es": "— — línea = umbral mayoría simple",
        "en": "— — line = simple majority threshold",
        "pt": "— — linha = limiar de maioria simples",
    },
    "viz.timeseries.title_suffix": {
        "es": "Series históricas",
        "en": "Historical series",
        "pt": "Séries históricas",
    },
    "viz.audit_note": {
        "es": "componentes con auditoría pública. Gap estructural: SCE/STAE sin auditoría independiente.",
        "en": "components with public audit. Structural gap: SCE/STAE without independent audit.",
        "pt": "componentes com auditoria pública. Lacuna estrutural: SCE/STAE sem auditoria independente.",
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
