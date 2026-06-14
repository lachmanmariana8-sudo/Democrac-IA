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
        "es": "Monitoreo Electoral · PEIRS",
        "en": "Electoral Monitoring · PEIRS",
        "pt": "Monitoramento Eleitoral · PEIRS",
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
        "es": "Responsable del monitoreo:",
        "en": "Monitoring lead:",
        "pt": "Responsável pelo monitoramento:",
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
        "es": "Apertura",
        "en": "Opening",
        "pt": "Abertura",
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
    "appendix.c.intro": {
        "es": "{n} eventos del período monitoreado (hallazgos del Hunter consolidados por evento: un hecho = una fila con todas sus fuentes). Cada fila es rastreable hasta sus fuentes primarias (enlaces en la columna Fuente). Es el respaldo auditable del informe.",
        "en": "{n} events in the monitored period (Hunter findings consolidated per event: one fact = one row with all its sources). Each row is traceable to its primary sources (links in the Source column). This is the report's auditable backing.",
        "pt": "{n} eventos do período monitorado (achados do Hunter consolidados por evento: um fato = uma linha com todas as suas fontes). Cada linha é rastreável até suas fontes primárias (links na coluna Fonte). É o respaldo auditável do relatório.",
    },
    "appendix.c.empty": {
        "es": "No se registraron hallazgos del Hunter en el período monitoreado.",
        "en": "No Hunter findings were recorded in the monitored period.",
        "pt": "Não foram registrados achados do Hunter no período monitorado.",
    },
    "appendix.c.truncated": {
        "es": "Se muestran los primeros {shown} de {total} hallazgos. El listado completo está en el Markdown descargable.",
        "en": "Showing the first {shown} of {total} findings. The complete list is in the downloadable Markdown.",
        "pt": "Exibindo os primeiros {shown} de {total} registros. A lista completa está no Markdown para download.",
    },
    "appendix.c.col.n": {"es": "#", "en": "#", "pt": "#"},
    "appendix.c.col.phase": {"es": "Fase", "en": "Phase", "pt": "Fase"},
    "phase.pre_electoral": {"es": "Pre-electoral", "en": "Pre-election", "pt": "Pré-eleitoral"},
    "phase.election_day": {"es": "Jornada", "en": "Election day", "pt": "Dia da eleição"},
    "phase.count": {"es": "Escrutinio", "en": "Vote count", "pt": "Apuração"},
    "phase.post_electoral": {"es": "Post-electoral", "en": "Post-election", "pt": "Pós-eleitoral"},
    "phase.other": {"es": "General", "en": "General", "pt": "Geral"},
    "appendix.c.col.date": {"es": "Fecha", "en": "Date", "pt": "Data"},
    "appendix.c.col.severity": {"es": "Sev.", "en": "Sev.", "pt": "Sev."},
    "appendix.c.col.category": {"es": "Categoría", "en": "Category", "pt": "Categoria"},
    "appendix.c.col.finding": {"es": "Hallazgo", "en": "Finding", "pt": "Achado"},
    "appendix.c.col.source": {"es": "Fuente", "en": "Source", "pt": "Fonte"},

    # ── Chapter titles (deben coincidir con CHAPTER_CATALOG) ─────────
    "chapter.declaracion_preliminar": {
        "es": "Prólogo y síntesis ejecutiva",
        "en": "Prologue and executive summary",
        "pt": "Prólogo e síntese executiva",
    },
    # ── Prólogo (Quiénes somos) — texto institucional fijo ───────────────
    "prologo.title": {"es": "Quiénes somos", "en": "Who we are", "pt": "Quem somos"},
    "prologo.p1": {
        "es": "**Democrac.IA PEIRS** es una plataforma de **monitoreo electoral** con fines **analíticos y de estudio**, **apartidaria e independiente**, construida sobre una **arquitectura de agentes de inteligencia artificial**. Su propósito es **servir, informar y fortalecer a la ciudadanía** en los procesos electorales y sus dinámicas en la era de la IA, aportando inteligencia electoral verificable y trazable que amplíe la capacidad de la sociedad civil, la academia, los organismos de observación y la prensa para comprender la **integridad** de una elección más allá del resultado.",
        "en": "**Democrac.IA PEIRS** is an **electoral monitoring** platform for **analytical and study** purposes, **non-partisan and independent**, built on an **artificial-intelligence agent architecture**. Its purpose is to **serve, inform and strengthen citizens** in electoral processes and their dynamics in the AI era, providing verifiable and traceable electoral intelligence that broadens the capacity of civil society, academia, observation bodies and the press to understand the **integrity** of an election beyond its result.",
        "pt": "**Democrac.IA PEIRS** é uma plataforma de **monitoramento eleitoral** com fins **analíticos e de estudo**, **apartidária e independente**, construída sobre uma **arquitetura de agentes de inteligência artificial**. Seu propósito é **servir, informar e fortalecer a cidadania** nos processos eleitorais e suas dinâmicas na era da IA, oferecendo inteligência eleitoral verificável e rastreável que amplie a capacidade da sociedade civil, da academia, dos organismos de observação e da imprensa para compreender a **integridade** de uma eleição para além do resultado.",
    },
    "prologo.p2": {
        "es": "**Lo que no somos.** No somos una autoridad electoral ni la sustituimos: no organizamos, administramos ni certificamos comicios, y **no legitimamos, validamos ni impugnamos resultados**. No tomamos posición político-partidaria. Monitoreamos el **proceso** —no las propuestas ni las candidaturas— bajo estándares internacionales de observación electoral (Art. 25 del ICCPR, Art. 23 de la CADH, la Declaración de Principios para la Observación Internacional de Elecciones de 2005 y los marcos de OEA/UE), complementados con indicadores académicos como V-Dem.",
        "en": "**What we are not.** We are not an electoral authority, nor do we replace one: we do not organise, administer or certify elections, and we **do not legitimise, validate or challenge results**. We take no partisan political position. We monitor the **process** —not the platforms or the candidacies— under international electoral observation standards (ICCPR Art. 25, ACHR Art. 23, the 2005 Declaration of Principles for International Election Observation and the OAS/EU frameworks), complemented by academic indicators such as V-Dem.",
        "pt": "**O que não somos.** Não somos uma autoridade eleitoral nem a substituímos: não organizamos, administramos nem certificamos eleições, e **não legitimamos, validamos nem impugnamos resultados**. Não tomamos posição político-partidária. Monitoramos o **processo** —não as propostas nem as candidaturas— sob padrões internacionais de observação eleitoral (Art. 25 do ICCPR, Art. 23 da CADH, a Declaração de Princípios para a Observação Internacional de Eleições de 2005 e os marcos da OEA/UE), complementados por indicadores acadêmicos como o V-Dem.",
    },
    "prologo.p3": {
        "es": "**Qué hacemos.** PEIRS opera un pipeline de agentes de IA especializados que, de forma continua: (1) monitorea fuentes abiertas —RSS de medios, monitoreo OSINT y mediciones técnicas de conectividad (OONI)—; (2) clasifica automáticamente cada hallazgo por categoría, fase electoral y severidad; (3) cruza la evidencia contra el marco normativo internacional; y (4) consolida y documenta cada hecho con **trazabilidad a su fuente primaria**. El resultado es **inteligencia electoral auditable**: cada afirmación de este informe puede rastrearse hasta su origen (véase Anexo C) y ningún dato se afirma sin respaldo. La consolidación asegura que un hecho se reporte una sola vez, con todas sus fuentes; y el monitoreo distingue siempre lo documentado de los vacíos de cobertura, sin inferir normalidad a partir de la ausencia de datos.",
        "en": "**What we do.** PEIRS runs a pipeline of specialised AI agents that continuously: (1) monitor open sources —media RSS, OSINT monitoring and technical connectivity measurements (OONI)—; (2) automatically classify each finding by category, electoral phase and severity; (3) cross-check evidence against the international normative framework; and (4) consolidate and document each fact with **traceability to its primary source**. The result is **auditable electoral intelligence**: every statement in this report can be traced to its origin (see Appendix C) and no datum is asserted without backing. Consolidation ensures a fact is reported once, with all its sources; and monitoring always distinguishes the documented from coverage gaps, without inferring normality from the absence of data.",
        "pt": "**O que fazemos.** O PEIRS opera um pipeline de agentes de IA especializados que, de forma contínua: (1) monitora fontes abertas —RSS de mídia, monitoramento OSINT e medições técnicas de conectividade (OONI)—; (2) classifica automaticamente cada achado por categoria, fase eleitoral e severidade; (3) cruza a evidência com o marco normativo internacional; e (4) consolida e documenta cada fato com **rastreabilidade até sua fonte primária**. O resultado é **inteligência eleitoral auditável**: cada afirmação deste relatório pode ser rastreada até sua origem (ver Anexo C) e nenhum dado é afirmado sem respaldo. A consolidação garante que um fato seja relatado uma só vez, com todas as suas fontes; e o monitoramento distingue sempre o documentado das lacunas de cobertura, sem inferir normalidade a partir da ausência de dados.",
    },
    "prologo.p4": {
        "es": "**Por qué, ahora.** En una era donde la desinformación, los *deepfakes* y la opacidad algorítmica de los sistemas de cómputo redefinen los riesgos de integridad, Democrac.IA PEIRS pone capacidades de análisis antes reservadas a grandes instituciones **al servicio del interés público y del fortalecimiento democrático**.",
        "en": "**Why now.** In an era where disinformation, *deepfakes* and the algorithmic opacity of vote-counting systems redefine integrity risks, Democrac.IA PEIRS puts analytical capabilities once reserved for large institutions **at the service of the public interest and democratic strengthening**.",
        "pt": "**Por que agora.** Numa era em que a desinformação, os *deepfakes* e a opacidade algorítmica dos sistemas de apuração redefinem os riscos de integridade, a Democrac.IA PEIRS coloca capacidades de análise antes reservadas a grandes instituições **a serviço do interesse público e do fortalecimento democrático**.",
    },
    # ── Síntesis ejecutiva (armada desde datos) ──────────────────────────
    "declaration.synthesis_title": {
        "es": "Síntesis ejecutiva — monitoreo e integridad del ciclo electoral 2026",
        "en": "Executive summary — monitoring and integrity of the 2026 electoral cycle",
        "pt": "Síntese executiva — monitoramento e integridade do ciclo eleitoral 2026",
    },
    "declaration.period_corpus": {
        "es": "Democrac.IA PEIRS monitoreó el ciclo electoral peruano de 2026 a lo largo de sus dos vueltas: desde la primera vuelta del 12 de abril hasta el escrutinio de la segunda vuelta del 7 de junio. En ese período se clasificaron automáticamente **{n} hallazgos** de fuentes abiertas (RSS, OSINT propio y mediciones OONI), de los cuales **{n_alta}** se clasificaron de severidad alta o crítica, concentrados en las fases de escrutinio y de resolución de disputas (detalle trazable en el Anexo C).",
        "en": "Democrac.IA PEIRS monitored Peru's 2026 electoral cycle across its two rounds: from the first round on 12 April to the count of the second round on 7 June. In that period **{n} findings** were automatically classified from open sources (RSS, own OSINT and OONI measurements), of which **{n_alta}** were classified as high or critical severity, concentrated in the count and dispute-resolution phases (traceable detail in Appendix C).",
        "pt": "A Democrac.IA PEIRS monitorou o ciclo eleitoral peruano de 2026 ao longo de seus dois turnos: do primeiro turno de 12 de abril até a apuração do segundo turno de 7 de junho. Nesse período foram classificados automaticamente **{n} achados** de fontes abertas (RSS, OSINT próprio e medições OONI), dos quais **{n_alta}** foram classificados de severidade alta ou crítica, concentrados nas fases de apuração e de resolução de disputas (detalhe rastreável no Anexo C).",
    },
    "declaration.patterns_intro": {
        "es": "El monitoreo de ambas vueltas identifica una convergencia de factores que tensiona la legitimidad del resultado:",
        "en": "Monitoring of both rounds identifies a convergence of factors straining the legitimacy of the result:",
        "pt": "O monitoramento de ambos os turnos identifica uma convergência de fatores que tensiona a legitimidade do resultado:",
    },
    "declaration.pattern_result": {
        "es": "- **Resultado al filo, sin proclamación.** En la segunda vuelta, el escrutinio oficial de la ONPE arrojó un empate técnico: al corte del {actas} % de actas, {a} ({ap}) y {b} ({bp}) se separaban por **~{margin} votos (≈{mp} pp)**, con el liderazgo marginal alternando entre cómputos. El JNE no ha proclamado ganador (ONPE; El Comercio, 2026).",
        "en": "- **Razor-thin result, not proclaimed.** In the second round, ONPE's official count produced a technical tie: at the {actas} % tally-sheet cut, {a} ({ap}) and {b} ({bp}) were separated by **~{margin} votes (≈{mp} pp)**, with the marginal lead alternating between counts. The JNE has not proclaimed a winner (ONPE; El Comercio, 2026).",
        "pt": "- **Resultado no limite, sem proclamação.** No segundo turno, a apuração oficial da ONPE produziu um empate técnico: no corte de {actas} % das atas, {a} ({ap}) e {b} ({bp}) separavam-se por **~{margin} votos (≈{mp} pp)**, com a liderança marginal alternando entre apurações. O JNE não proclamou vencedor (ONPE; El Comercio, 2026).",
    },
    "declaration.pattern_count": {
        "es": "- **Escrutinio prolongado.** El presidente del JNE estimó que el resultado se conocería alrededor de un mes después de la votación, por las actas observadas en revisión en los JEE (JNE, 2026).",
        "en": "- **Protracted count.** The JNE president estimated the result would be known about a month after the vote, owing to observed tally sheets under JEE review (JNE, 2026).",
        "pt": "- **Apuração prolongada.** O presidente do JNE estimou que o resultado seria conhecido cerca de um mês após a votação, devido às atas observadas em revisão nos JEE (JNE, 2026).",
    },
    "declaration.pattern_emb": {
        "es": "- **Órgano electoral bajo cuestionamiento.** La primera vuelta dejó a la ONPE en crisis institucional —su titular denunciado penalmente, pedido de separación cautelar del Fiscal de la Nación y observaciones de la Contraloría—, documentada con fuentes primarias (véase Cap. 6 y Anexo C).",
        "en": "- **Electoral body under question.** The first round left ONPE in institutional crisis —its head criminally charged, a request for precautionary removal by the Attorney General and observations by the Comptroller—, documented with primary sources (see Ch. 6 and Appendix C).",
        "pt": "- **Órgão eleitoral sob questionamento.** O primeiro turno deixou a ONPE em crise institucional —seu titular denunciado penalmente, pedido de afastamento cautelar do Procurador-Geral e observações da Controladoria—, documentada com fontes primárias (ver Cap. 6 e Anexo C).",
    },
    "declaration.reading": {
        "es": "Esta convergencia —margen ínfimo, escrutinio demorado y un organismo electoral en crisis— configura un escenario de **alta contestabilidad** del resultado, que interpela el estándar del **Art. 25 del ICCPR** sobre elecciones auténticas, en su dimensión de transparencia del escrutinio y aceptación del resultado. El contexto es consistente con el deterioro de los indicadores de V-Dem sobre el órgano electoral: la autonomía cayó de {aut0} ({y0}) a {aut1} ({y1}) y la capacidad de {cap0} a {cap1} (V-Dem v16). PEIRS no afirma fraude ni anticipa el desenlace: la credibilidad del resultado dependerá de la independencia con que el EMB resuelva las impugnaciones pendientes.",
        "en": "This convergence —minimal margin, delayed count and an electoral body in crisis— configures a scenario of **high contestability** of the result, which interpellates the **ICCPR Art. 25** standard on genuine elections, in its dimension of count transparency and acceptance of the result. The context is consistent with the deterioration of V-Dem's indicators on the electoral body: autonomy fell from {aut0} ({y0}) to {aut1} ({y1}) and capacity from {cap0} to {cap1} (V-Dem v16). PEIRS asserts no fraud and anticipates no outcome: the credibility of the result will depend on the independence with which the EMB resolves the pending challenges.",
        "pt": "Esta convergência —margem ínfima, apuração atrasada e um órgão eleitoral em crise— configura um cenário de **alta contestabilidade** do resultado, que interpela o padrão do **Art. 25 do ICCPR** sobre eleições genuínas, em sua dimensão de transparência da apuração e aceitação do resultado. O contexto é consistente com a deterioração dos indicadores do V-Dem sobre o órgão eleitoral: a autonomia caiu de {aut0} ({y0}) para {aut1} ({y1}) e a capacidade de {cap0} para {cap1} (V-Dem v16). O PEIRS não afirma fraude nem antecipa o desfecho: a credibilidade do resultado dependerá da independência com que o EMB resolva as impugnações pendentes.",
    },
    "declaration.reading_no_vdem": {
        "es": "Esta convergencia —margen ínfimo, escrutinio demorado y un organismo electoral en crisis— configura un escenario de **alta contestabilidad** del resultado, que interpela el estándar del **Art. 25 del ICCPR** sobre elecciones auténticas. PEIRS no afirma fraude ni anticipa el desenlace: la credibilidad del resultado dependerá de la independencia con que el EMB resuelva las impugnaciones pendientes.",
        "en": "This convergence —minimal margin, delayed count and an electoral body in crisis— configures a scenario of **high contestability** of the result, interpellating the **ICCPR Art. 25** standard on genuine elections. PEIRS asserts no fraud and anticipates no outcome: the credibility of the result will depend on the independence with which the EMB resolves the pending challenges.",
        "pt": "Esta convergência —margem ínfima, apuração atrasada e um órgão eleitoral em crise— configura um cenário de **alta contestabilidade** do resultado, interpelando o padrão do **Art. 25 do ICCPR** sobre eleições genuínas. O PEIRS não afirma fraude nem antecipa o desfecho: a credibilidade do resultado dependerá da independência com que o EMB resolva as impugnações pendentes.",
    },
    "declaration.disclosure": {
        "es": "Democrac.IA PEIRS no legitima ni valida resultados electorales; emite inteligencia electoral con trazabilidad verificable, sin sesgo político-partidario.",
        "en": "Democrac.IA PEIRS does not legitimise or validate electoral results; it issues electoral intelligence with verifiable traceability, without political-partisan bias.",
        "pt": "A Democrac.IA PEIRS não legitima nem valida resultados eleitorais; emite inteligência eleitoral com rastreabilidade verificável, sem viés político-partidário.",
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
    "chapter.observacion_entre_vueltas": {
        "es": "Resultados electorales y monitoreo del proceso — 1ª y 2ª vuelta",
        "en": "Electoral results and process monitoring — first and second round",
        "pt": "Resultados eleitorais e monitoramento do processo — 1º e 2º turno",
    },

    # ── Capítulo: observación entre vueltas (determinista, sin LLM) ───
    "runoff_obs.intro": {
        "es": "Estado de monitoreo por eje al cierre del período. El nivel de auditoría escala objetivamente — por documento oficial o cruce de ≥2 fuentes primarias independientes (≥3 ⇒ confirmado), nunca por validación humana informal.",
        "en": "Per-axis monitoring status at period close. Audit level escalates objectively — by official document or cross-check of ≥2 independent primary sources (≥3 ⇒ confirmed), never by informal human validation.",
        "pt": "Estado de monitoramento por eixo no fechamento do período. O nível de auditoria escala objetivamente — por documento oficial ou cruzamento de ≥2 fontes primárias independentes (≥3 ⇒ confirmado), nunca por validação humana informal.",
    },
    "runoff_obs.no_findings": {
        "es": "Sin hallazgos corroborados durante la ventana de observación (eje monitoreado, 0 incidentes verificados).",
        "en": "No corroborated findings during the observation window (axis monitored, 0 verified incidents).",
        "pt": "Sem achados corroborados durante a janela de observação (eixo monitorado, 0 incidentes verificados).",
    },
    "runoff_obs.not_observed": {
        "es": "Eje no observado — pendiente ingesta de fuente primaria.",
        "en": "Axis not observed — pending primary-source ingestion.",
        "pt": "Eixo não observado — pendente de ingestão de fonte primária.",
    },
    "runoff_obs.findings_count": {
        "es": "Hallazgos registrados: {n}.",
        "en": "Findings recorded: {n}.",
        "pt": "Achados registrados: {n}.",
    },
    "runoff_obs.global_header": {
        "es": "Estado de auditoría global: {status} · Hallazgos totales: {n}",
        "en": "Global audit status: {status} · Total findings: {n}",
        "pt": "Estado de auditoria global: {status} · Achados totais: {n}",
    },
    "runoff_obs.axis.campaign_conduct_finalist_a": {
        "es": "Conducta de campaña — finalista A", "en": "Campaign conduct — finalist A", "pt": "Conduta de campanha — finalista A",
    },
    "runoff_obs.axis.campaign_conduct_finalist_b": {
        "es": "Conducta de campaña — finalista B", "en": "Campaign conduct — finalist B", "pt": "Conduta de campanha — finalista B",
    },
    "runoff_obs.axis.hate_speech_and_intimidation_incidents": {
        "es": "Discurso de odio e intimidación", "en": "Hate speech and intimidation", "pt": "Discurso de ódio e intimidação",
    },
    "runoff_obs.axis.media_access_monitoring": {
        "es": "Acceso equitativo a medios", "en": "Equitable media access", "pt": "Acesso equitativo à mídia",
    },
    "runoff_obs.axis.emb_independence_stress_signals": {
        "es": "Independencia del EMB (JNE/ONPE)", "en": "EMB independence (JNE/ONPE)", "pt": "Independência do EMB (JNE/ONPE)",
    },
    "runoff_obs.axis.election_day_logistics_readiness": {
        "es": "Logística de la jornada electoral", "en": "Election-day logistics readiness", "pt": "Logística da jornada eleitoral",
    },
    "runoff_obs.axis.vote_count_transparency_protocol": {
        "es": "Transparencia del cómputo", "en": "Vote-count transparency", "pt": "Transparência da apuração",
    },
    "runoff_obs.axis.dispute_resolution_tracker": {
        "es": "Impugnaciones (JEE/JNE)", "en": "Dispute resolution (JEE/JNE)", "pt": "Impugnações (JEE/JNE)",
    },
    "runoff_obs.axis.osint_information_integrity_monitor": {
        "es": "OSINT · integridad informativa", "en": "OSINT · information integrity", "pt": "OSINT · integridade informativa",
    },
    "runoff_obs.axis.electoral_violence_incidents": {
        "es": "Violencia política y seguridad", "en": "Political violence and security", "pt": "Violência política e segurança",
    },

    # Contexto del proceso de cara a la segunda vuelta (capítulo determinista).
    "runoff_obs.report_title": {
        "es": "Resultados electorales y monitoreo del proceso — 1ª y 2ª vuelta",
        "en": "Electoral results and process monitoring — first and second round",
        "pt": "Resultados eleitorais e monitoramento do processo — 1º e 2º turno",
    },
    "runoff_obs.first_round_header": {
        "es": "Primera vuelta — resultados oficiales (12 de abril de 2026)",
        "en": "First round — official results (12 April 2026)",
        "pt": "Primeiro turno — resultados oficiais (12 de abril de 2026)",
    },
    "runoff_obs.first_round_intro": {
        "es": "Resultados oficiales de la primera vuelta presidencial. Los dos candidatos más votados pasaron al balotaje:",
        "en": "Official results of the first presidential round. The two most-voted candidates advanced to the runoff:",
        "pt": "Resultados oficiais do primeiro turno presidencial. Os dois candidatos mais votados avançaram ao segundo turno:",
    },
    "runoff_obs.candidate_line": {
        "es": "- **{name}** ({party}) — {pct}% ({votes} votos){flag}",
        "en": "- **{name}** ({party}) — {pct}% ({votes} votes){flag}",
        "pt": "- **{name}** ({party}) — {pct}% ({votes} votos){flag}",
    },
    "runoff_obs.advances_flag": {
        "es": " — pasa al balotaje", "en": " — advances to runoff", "pt": " — avança ao segundo turno",
    },
    "runoff_obs.tbl.candidate": {"es": "Candidato", "en": "Candidate", "pt": "Candidato"},
    "runoff_obs.tbl.party": {"es": "Partido", "en": "Party", "pt": "Partido"},
    "runoff_obs.tbl.pct": {"es": "% válidos", "en": "% valid", "pt": "% válidos"},
    "runoff_obs.tbl.votes": {"es": "Votos", "en": "Votes", "pt": "Votos"},
    "runoff_obs.tbl.result": {"es": "Resultado", "en": "Result", "pt": "Resultado"},
    "runoff_obs.tbl.advances": {"es": "Pasa al balotaje", "en": "Advances", "pt": "Avança ao 2º turno"},
    "runoff_obs.tbl.pct_prov": {"es": "% válidos (prov.)", "en": "% valid (prov.)", "pt": "% válidos (prov.)"},
    "runoff_obs.tbl.votes_prov": {"es": "Votos (prov.)", "en": "Votes (prov.)", "pt": "Votos (prov.)"},
    "runoff_obs.between_header": {
        "es": "Fase entre vueltas — monitoreo del proceso (13 abr – 7 jun 2026)",
        "en": "Between rounds — process monitoring (13 Apr – 7 Jun 2026)",
        "pt": "Entre turnos — monitoramento do processo (13 abr – 7 jun 2026)",
    },
    "runoff_obs.second_round_header": {
        "es": "Segunda vuelta — resultado provisional (7 de junio de 2026)",
        "en": "Second round — provisional result (7 June 2026)",
        "pt": "Segundo turno — resultado provisório (7 de junho de 2026)",
    },
    "runoff_obs.second_round_status": {
        "es": "Escrutinio oficial de ONPE en curso al {as_of} ({actas}% de actas procesadas). Resultado **provisional**, sujeto a cambios:",
        "en": "Official ONPE count in progress as of {as_of} ({actas}% of tally sheets processed). **Provisional** result, subject to change:",
        "pt": "Apuração oficial da ONPE em curso em {as_of} ({actas}% das atas processadas). Resultado **provisório**, sujeito a alterações:",
    },
    "runoff_obs.candidate_line_prov": {
        "es": "- **{name}** ({party}) — {pct}% ({votes} votos) · provisional",
        "en": "- **{name}** ({party}) — {pct}% ({votes} votes) · provisional",
        "pt": "- **{name}** ({party}) — {pct}% ({votes} votos) · provisório",
    },
    "runoff_obs.second_round_pending": {
        "es": "**Sin ganador proclamado.** {note}",
        "en": "**No winner proclaimed.** {note}",
        "pt": "**Sem vencedor proclamado.** {note}",
    },
    "runoff_obs.stae_header": {
        "es": "Sistema tecnológico de escrutinio (STAE)",
        "en": "Vote-count technology system (STAE)",
        "pt": "Sistema tecnológico de apuração (STAE)",
    },
    "runoff_obs.context_header": {
        "es": "Contexto del balotaje", "en": "Runoff context", "pt": "Contexto do segundo turno",
    },
    "runoff_obs.context_intro": {
        "es": "El {runoff_date} se celebra la segunda vuelta presidencial entre los dos finalistas surgidos de la primera vuelta del {first_round_date}:",
        "en": "On {runoff_date} the presidential runoff is held between the two finalists from the first round of {first_round_date}:",
        "pt": "Em {runoff_date} ocorre o segundo turno presidencial entre os dois finalistas do primeiro turno de {first_round_date}:",
    },
    "runoff_obs.finalist_line": {
        "es": "- **{name}** ({party}) — {pct}% en primera vuelta ({votes} votos)",
        "en": "- **{name}** ({party}) — {pct}% in the first round ({votes} votes)",
        "pt": "- **{name}** ({party}) — {pct}% no primeiro turno ({votes} votos)",
    },
    "runoff_obs.margin_line": {
        "es": "Margen entre ambos finalistas en primera vuelta: {margin} puntos porcentuales.",
        "en": "Margin between the two finalists in the first round: {margin} percentage points.",
        "pt": "Margem entre os dois finalistas no primeiro turno: {margin} pontos percentuais.",
    },
    "runoff_obs.turnout_line": {
        "es": "Participación en primera vuelta: {turnout}% (abstención {abstention}%); votos en blanco {blank}%, nulos {null}%.",
        "en": "First-round turnout: {turnout}% (abstention {abstention}%); blank votes {blank}%, null {null}%.",
        "pt": "Comparecimento no primeiro turno: {turnout}% (abstenção {abstention}%); votos em branco {blank}%, nulos {null}%.",
    },
    "runoff_obs.legal_basis": {
        "es": "El monitoreo PEIRS se centra en el **proceso**, no en las propuestas programáticas. Base normativa: ICCPR Art. 25 — derecho a elegir y ser elegido en condiciones de equidad, vigente durante la segunda vuelta.",
        "en": "PEIRS monitoring focuses on the **process**, not policy platforms. Normative basis: ICCPR Art. 25 — the right to vote and be elected under equitable conditions, in force during the runoff.",
        "pt": "O monitoramento PEIRS concentra-se no **processo**, não nas propostas programáticas. Base normativa: ICCPR Art. 25 — direito de eleger e ser eleito em condições de equidade, vigente durante o segundo turno.",
    },
    "runoff_obs.observation_header": {
        "es": "Estado de monitoreo por eje", "en": "Per-axis monitoring status", "pt": "Estado de monitoramento por eixo",
    },
    "runoff_obs.results_macro": {
        "es": "Resultados electorales", "en": "Electoral results", "pt": "Resultados eleitorais",
    },
    "runoff_obs.observation_intro": {
        "es": "Durante la fase entre vueltas (13 abr – 7 jun 2026) el monitoreo se organizó en 9 ejes del proceso. A continuación, los ejes con hechos documentados; al cierre, la cobertura del resto.",
        "en": "During the inter-round phase (13 Apr – 7 Jun 2026) monitoring was organised across 9 process axes. Below, the axes with documented facts; at the end, the coverage of the rest.",
        "pt": "Durante a fase entre turnos (13 abr – 7 jun 2026) o monitoramento foi organizado em 9 eixos do processo. A seguir, os eixos com fatos documentados; ao final, a cobertura dos demais.",
    },
    "runoff_obs.status_confirmed": {
        "es": "hallazgos confirmados (documento oficial o ≥3 fuentes independientes)",
        "en": "confirmed findings (official document or ≥3 independent sources)",
        "pt": "achados confirmados (documento oficial ou ≥3 fontes independentes)",
    },
    "runoff_obs.status_verified": {
        "es": "hallazgos verificados (≥2 fuentes independientes)",
        "en": "verified findings (≥2 independent sources)",
        "pt": "achados verificados (≥2 fontes independentes)",
    },
    "runoff_obs.status_registered": {
        "es": "hallazgos registrados, no corroborados de forma independiente",
        "en": "findings recorded, not independently corroborated",
        "pt": "achados registrados, não corroborados de forma independente",
    },
    "runoff_obs.coverage_header": {
        "es": "Cobertura de monitoreo", "en": "Monitoring coverage", "pt": "Cobertura de monitoramento",
    },
    "runoff_obs.coverage_monitored": {
        "es": "**Ejes monitoreados sin incidentes documentados** en el período: {axes}. La ausencia de incidentes refleja que el monitoreo (OSINT propio, redes, OONI) no registró eventos verificables — no es una afirmación de normalidad institucional.",
        "en": "**Axes monitored with no documented incidents** in the period: {axes}. The absence of incidents reflects that monitoring (own OSINT, social media, OONI) recorded no verifiable events — it is not an assertion of institutional normality.",
        "pt": "**Eixos monitorados sem incidentes documentados** no período: {axes}. A ausência de incidentes reflete que o monitoramento (OSINT próprio, redes, OONI) não registrou eventos verificáveis — não é uma afirmação de normalidade institucional.",
    },
    "runoff_obs.coverage_no_source": {
        "es": "**Ejes sin evidencia primaria procesada** en el período: {axes}. Requerían acceso a fuentes administrativas o documentales (ONPE-DFP, expedientes JEE/JNE, veeduría) que no se ingirieron — vacío de cobertura, no de cumplimiento.",
        "en": "**Axes with no primary evidence processed** in the period: {axes}. They required access to administrative or documentary sources (ONPE-DFP, JEE/JNE records, monitoring) that were not ingested — a coverage gap, not a compliance one.",
        "pt": "**Eixos sem evidência primária processada** no período: {axes}. Exigiam acesso a fontes administrativas ou documentais (ONPE-DFP, processos JEE/JNE, fiscalização) que não foram ingeridas — lacuna de cobertura, não de cumprimento.",
    },
    # ── Lectura de riesgo de legitimidad (síntesis del EMB + 2021) ──────────
    "runoff_obs.risk_header": {
        "es": "Riesgo de legitimidad del resultado",
        "en": "Result legitimacy risk",
        "pt": "Risco de legitimidade do resultado",
    },
    "runoff_obs.risk_intro": {
        "es": "Más allá de quién resulte proclamado, el monitoreo PEIRS identifica una convergencia de factores que tensiona la legitimidad del resultado de la 2ª vuelta:",
        "en": "Beyond who is ultimately proclaimed, PEIRS monitoring identifies a convergence of factors straining the legitimacy of the runoff result:",
        "pt": "Para além de quem seja proclamado, o monitoramento PEIRS identifica uma convergência de fatores que tensiona a legitimidade do resultado do 2º turno:",
    },
    "runoff_obs.risk_margin": {
        "es": "**Margen mínimo.** El resultado provisional se define por ~{mp} puntos porcentuales (~{mv} votos), dentro del universo de actas aún en revisión.",
        "en": "**Razor-thin margin.** The provisional result is decided by ~{mp} percentage points (~{mv} votes), within the universe of tally sheets still under review.",
        "pt": "**Margem mínima.** O resultado provisório é definido por ~{mp} pontos percentuais (~{mv} votos), dentro do universo de atas ainda em revisão.",
    },
    "runoff_obs.risk_unproclaimed": {
        "es": "**Resultado no proclamado.** El JNE no ha proclamado ganador; persisten actas observadas en revisión en JEE.",
        "en": "**Result not proclaimed.** The JNE has not proclaimed a winner; observed tally sheets remain under JEE review.",
        "pt": "**Resultado não proclamado.** O JNE não proclamou vencedor; persistem atas observadas em revisão no JEE.",
    },
    "runoff_obs.risk_emb": {
        "es": "**Órgano electoral cuestionado.** La ONPE atravesó la 1ª vuelta con su titular denunciado penalmente y pedidos de separación cautelar ({n} señales documentadas más arriba).",
        "en": "**Electoral body under question.** ONPE went through the first round with its head criminally charged and requests for precautionary removal ({n} signals documented above).",
        "pt": "**Órgão eleitoral questionado.** A ONPE atravessou o 1º turno com seu titular denunciado penalmente e pedidos de afastamento cautelar ({n} sinais documentados acima).",
    },
    "runoff_obs.risk_stae": {
        "es": "**Cómputo sin auditoría pública.** El STAE presentó fallas en 1ª vuelta y operó sin auditoría independiente certificada.",
        "en": "**Count without public audit.** STAE failed in the first round and operated without certified independent audit.",
        "pt": "**Apuração sem auditoria pública.** O STAE apresentou falhas no 1º turno e operou sem auditoria independente certificada.",
    },
    "runoff_obs.risk_reading": {
        "es": "La concurrencia de un margen ínfimo, un resultado aún no proclamado y un organismo electoral bajo cuestionamiento penal configura un escenario de **alta contestabilidad**. En estas condiciones, la credibilidad del desenlace no depende solo de la exactitud del cómputo, sino de la **independencia percibida del EMB** al resolver las impugnaciones — una obligación de transparencia del escrutinio y de recurso efectivo (ICCPR Art. 25; CADH Arts. 23 y 25).",
        "en": "The concurrence of a minimal margin, an unproclaimed result and an electoral body under criminal scrutiny configures a scenario of **high contestability**. Under these conditions, the credibility of the outcome depends not only on the accuracy of the count but on the **perceived independence of the EMB** in resolving challenges — an obligation of scrutiny transparency and effective remedy (ICCPR Art. 25; ACHR Arts. 23 and 25).",
        "pt": "A concorrência de uma margem ínfima, um resultado não proclamado e um órgão eleitoral sob escrutínio penal configura um cenário de **alta contestabilidade**. Nessas condições, a credibilidade do desfecho depende não só da exatidão da apuração, mas da **independência percebida do EMB** ao resolver as impugnações — uma obrigação de transparência da apuração e de recurso efetivo (ICCPR Art. 25; CADH Arts. 23 e 25).",
    },
    "runoff_obs.risk_2021": {
        "es": "**Antecedente — balotaje 2021.** {winner} ({wp}) se impuso a {ru} ({rp}) por ≈{mv} votos ({mp} pp). {ru} presentó pedidos de nulidad alegando fraude que el JNE desestimó, y la proclamación tomó alrededor de seis semanas (19-jul-2021). El paralelo —margen estrecho, alegaciones de fraude y judicialización del resultado— es el patrón a monitorear en 2026.",
        "en": "**Precedent — 2021 runoff.** {winner} ({wp}) defeated {ru} ({rp}) by ≈{mv} votes ({mp} pp). {ru} filed nullity requests alleging fraud, which the JNE dismissed, and proclamation took about six weeks (19 Jul 2021). The parallel — narrow margin, fraud allegations and judicialisation of the result — is the pattern to monitor in 2026.",
        "pt": "**Precedente — 2º turno 2021.** {winner} ({wp}) venceu {ru} ({rp}) por ≈{mv} votos ({mp} pp). {ru} apresentou pedidos de nulidade alegando fraude, que o JNE rejeitou, e a proclamação levou cerca de seis semanas (19-jul-2021). O paralelo — margem estreita, alegações de fraude e judicialização do resultado — é o padrão a monitorar em 2026.",
    },
    "runoff_obs.desc.campaign_conduct_finalist_a": {
        "es": "Cumplimiento de reglas de campaña: uso de recursos del Estado, tope de gasto, propaganda fuera de plazo, franja electoral.",
        "en": "Campaign-rule compliance: use of state resources, spending caps, out-of-period propaganda, allocated airtime.",
        "pt": "Cumprimento das regras de campanha: uso de recursos do Estado, teto de gastos, propaganda fora do prazo, faixa eleitoral.",
    },
    "runoff_obs.desc.campaign_conduct_finalist_b": {
        "es": "Cumplimiento de reglas de campaña: uso de recursos del Estado, tope de gasto, propaganda fuera de plazo, franja electoral.",
        "en": "Campaign-rule compliance: use of state resources, spending caps, out-of-period propaganda, allocated airtime.",
        "pt": "Cumprimento das regras de campanha: uso de recursos do Estado, teto de gastos, propaganda fora do prazo, faixa eleitoral.",
    },
    "runoff_obs.desc.hate_speech_and_intimidation_incidents": {
        "es": "Discurso de odio, intimidación e incitación a la violencia electoral (estándar ICCPR Art. 20).",
        "en": "Hate speech, intimidation and incitement to electoral violence (ICCPR Art. 20 standard).",
        "pt": "Discurso de ódio, intimidação e incitação à violência eleitoral (padrão ICCPR Art. 20).",
    },
    "runoff_obs.desc.media_access_monitoring": {
        "es": "Acceso equitativo a medios: cobertura proporcional medida en minutos/menciones (medición cuantitativa, no contenido).",
        "en": "Equitable media access: proportional coverage measured in minutes/mentions (quantitative, not content).",
        "pt": "Acesso equitativo à mídia: cobertura proporcional medida em minutos/menções (quantitativa, não conteúdo).",
    },
    "runoff_obs.desc.emb_independence_stress_signals": {
        "es": "Señales de presión sobre la independencia del órgano electoral (JNE/ONPE/RENIEC).",
        "en": "Pressure signals on the independence of the electoral body (JNE/ONPE/RENIEC).",
        "pt": "Sinais de pressão sobre a independência do órgão eleitoral (JNE/ONPE/RENIEC).",
    },
    "runoff_obs.desc.election_day_logistics_readiness": {
        "es": "Preparación logística de la jornada: mesas, locales, accesibilidad, sorteo de miembros de mesa.",
        "en": "Election-day logistics readiness: polling stations, venues, accessibility, poll-worker selection.",
        "pt": "Preparação logística da jornada: mesas, locais, acessibilidade, sorteio de mesários.",
    },
    "runoff_obs.desc.vote_count_transparency_protocol": {
        "es": "Transparencia del cómputo: trazabilidad de actas, plazos y desagregación por mesa.",
        "en": "Vote-count transparency: tally-sheet traceability, deadlines and mesa-level disaggregation.",
        "pt": "Transparência da apuração: rastreabilidade de atas, prazos e desagregação por mesa.",
    },
    "runoff_obs.desc.dispute_resolution_tracker": {
        "es": "Impugnaciones y disputas electorales ante JEE/JNE.",
        "en": "Electoral challenges and disputes before JEE/JNE.",
        "pt": "Impugnações e disputas eleitorais perante JEE/JNE.",
    },
    "runoff_obs.desc.osint_information_integrity_monitor": {
        "es": "Integridad informativa: desinformación, deepfakes, redes inauténticas, narrativas de fraude.",
        "en": "Information integrity: disinformation, deepfakes, inauthentic networks, fraud narratives.",
        "pt": "Integridade informativa: desinformação, deepfakes, redes inautênticas, narrativas de fraude.",
    },
    "runoff_obs.desc.electoral_violence_incidents": {
        "es": "Violencia política y seguridad electoral: amenazas, ataques físicos, obstrucción de personeros.",
        "en": "Political violence and electoral security: threats, physical attacks, obstruction of poll watchers.",
        "pt": "Violência política e segurança eleitoral: ameaças, ataques físicos, obstrução de fiscais.",
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
        "es": "Eventos críticos del período monitoreado",
        "en": "Critical events of the monitored period",
        "pt": "Eventos críticos do período monitorado",
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
        "es": "Acciones e intervenciones cruzadas registradas.",
        "en": "Recorded cross-cutting actions and interventions.",
        "pt": "Ações e intervenções cruzadas registradas.",
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
    "viz.scenario_probability.caption": {
        "es": "Probabilidad estimada de cada escenario prospectivo; suman ~100%. Mayor barra = escenario más probable según el modelo.",
        "en": "Estimated probability of each prospective scenario; they sum to ~100%. Longer bar = more likely scenario per the model.",
        "pt": "Probabilidade estimada de cada cenário prospectivo; somam ~100%. Barra maior = cenário mais provável segundo o modelo.",
    },
    "viz.early_warning_meter.title": {
        "es": "Medidor de alerta temprana",
        "en": "Early warning meter",
        "pt": "Medidor de alerta antecipada",
    },
    "viz.early_warning_meter.caption": {
        "es": "Índice de crisis 0–1, ponderado por severidad de los hallazgos (crítico=1,0; alto=0,55; medio=0,20). Verde <0,20 · ámbar 0,20–0,40 · naranja 0,40–0,60 · rojo ≥0,60. Mayor = mayor riesgo.",
        "en": "Crisis index 0–1, weighted by finding severity (critical=1.0; high=0.55; medium=0.20). Green <0.20 · amber 0.20–0.40 · orange 0.40–0.60 · red ≥0.60. Higher = greater risk.",
        "pt": "Índice de crise 0–1, ponderado pela severidade dos registros (crítico=1,0; alto=0,55; médio=0,20). Verde <0,20 · âmbar 0,20–0,40 · laranja 0,40–0,60 · vermelho ≥0,60. Maior = maior risco.",
    },
    "viz.semaphore_institutional.title": {
        "es": "Evaluación institucional por órgano",
        "en": "Institutional assessment by body",
        "pt": "Avaliação institucional por órgão",
    },
    "viz.semaphore_institutional.caption": {
        "es": "Estado por órgano según la severidad máxima de hallazgos que lo mencionan. Verde = sin incidencias relevantes · ámbar = hallazgos moderados · rojo = hallazgos graves/críticos.",
        "en": "Per-body status based on the maximum severity of findings mentioning it. Green = no relevant incidents · amber = moderate findings · red = serious/critical findings.",
        "pt": "Estado por órgão conforme a severidade máxima dos registros que o mencionam. Verde = sem incidências relevantes · âmbar = registros moderados · vermelho = registros graves/críticos.",
    },
    "viz.dimensions_radar.title": {
        "es": "8 Dimensiones PEIRS",
        "en": "PEIRS 8 dimensions",
        "pt": "8 dimensões PEIRS",
    },
    "viz.dimensions_radar.caption": {
        "es": "Escala 0–100 de salud por dimensión: 100 = sin incidencias registradas en el ciclo; valores bajos = mayor concentración de hallazgos graves. Un valor cercano a 0 (p. ej. Org. electoral) señala dimensión bajo estrés, no ausencia de datos.",
        "en": "0–100 health scale per dimension: 100 = no incidents recorded in the cycle; low values = greater concentration of serious findings. A value near 0 (e.g. Electoral body) signals a dimension under stress, not missing data.",
        "pt": "Escala 0–100 de saúde por dimensão: 100 = sem incidências registradas no ciclo; valores baixos = maior concentração de registros graves. Um valor próximo de 0 (ex.: Órgão eleitoral) sinaliza dimensão sob estresse, não ausência de dados.",
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

    # ── Forecast chart badge + severity labels ──────────────────────────
    "viz.alert": {
        "es": "ALERTA",
        "en": "ALERT",
        "pt": "ALERTA",
    },
    "viz.severity.info": {
        "es": "info",
        "en": "info",
        "pt": "info",
    },
    "viz.severity.low": {
        "es": "bajo",
        "en": "low",
        "pt": "baixo",
    },
    "viz.severity.medium": {
        "es": "medio",
        "en": "medium",
        "pt": "médio",
    },
    "viz.severity.high": {
        "es": "alto",
        "en": "high",
        "pt": "alto",
    },
    "viz.severity.critical": {
        "es": "crítico",
        "en": "critical",
        "pt": "crítico",
    },

    # ── Forecast scenario short labels (forecast_chart, scenario_probability) ──
    "forecast.scenario.s_dispute_prolongada.label": {
        "es": "Disputa post-electoral prolongada",
        "en": "Prolonged post-electoral dispute",
        "pt": "Disputa pós-eleitoral prolongada",
    },
    "forecast.scenario.s_nulidad_parcial.label": {
        "es": "Nulidad parcial por el JNE",
        "en": "Partial nullity by JNE",
        "pt": "Nulidade parcial pelo JNE",
    },
    "forecast.scenario.s_segunda_vuelta.label": {
        "es": "Segunda vuelta con alta complejidad operativa",
        "en": "Runoff with high operational complexity",
        "pt": "Segundo turno com alta complexidade operacional",
    },
    "forecast.scenario.s_crisis_institucional.label": {
        "es": "Crisis institucional post-escrutinio aguda",
        "en": "Acute post-tally institutional crisis",
        "pt": "Crise institucional aguda pós-apuração",
    },
    "forecast.scenario.s_reforma_legislativa.label": {
        "es": "Reforma legislativa post-proceso sobre IA electoral",
        "en": "Post-process legislative reform on electoral AI",
        "pt": "Reforma legislativa pós-processo sobre IA eleitoral",
    },
    "forecast.scenario.s_proclamacion_sin_disputa.label": {
        "es": "Proclamación sin disputa mayor",
        "en": "Proclamation without major dispute",
        "pt": "Proclamação sem disputa relevante",
    },

    # ── Appendix A body (technical methodology) ─────────────────────────
    "appendix.a.h_pipeline": {
        "es": "Pipeline PEIRS",
        "en": "PEIRS Pipeline",
        "pt": "Pipeline PEIRS",
    },
    "appendix.a.intro": {
        "es": "Este informe fue generado con el sistema DemocracIA / PEIRS (Predictive Electoral Integrity &amp; Risk System), aplicando el pipeline de 6 etapas:",
        "en": "This report was generated with the DemocracIA / PEIRS (Predictive Electoral Integrity &amp; Risk System) system, applying the 6-stage pipeline:",
        "pt": "Este relatório foi gerado com o sistema DemocracIA / PEIRS (Predictive Electoral Integrity &amp; Risk System), aplicando o pipeline de 6 etapas:",
    },
    "appendix.a.li_eliteloader": {
        "es": "<strong>EliteLoader</strong> — carga paralela de evidencia: entries del Hunter, alertas dispatchadas, corpus constitucionalista RAG filtrado por país, y series históricas V-Dem, Freedom House, PEI, RSF. Cache TTL 1 hora.",
        "en": "<strong>EliteLoader</strong> — parallel evidence loading: Hunter entries, dispatched alerts, country-filtered constitutionalist RAG corpus, and historical series V-Dem, Freedom House, PEI, RSF. Cache TTL 1 hour.",
        "pt": "<strong>EliteLoader</strong> — carregamento paralelo de evidência: entradas do Hunter, alertas despachados, corpus constitucionalista RAG filtrado por país e séries históricas V-Dem, Freedom House, PEI, RSF. Cache TTL 1 hora.",
    },
    "appendix.a.li_phaseorganizer": {
        "es": "<strong>PhaseOrganizer</strong> — agrupa {n} hallazgos en las 9 fases del ciclo electoral según fecha y calendario electoral.",
        "en": "<strong>PhaseOrganizer</strong> — groups {n} findings into the 9 phases of the electoral cycle by date and electoral calendar.",
        "pt": "<strong>PhaseOrganizer</strong> — agrupa {n} registros nas 9 fases do ciclo eleitoral conforme data e calendário eleitoral.",
    },
    "appendix.a.li_crossref": {
        "es": "<strong>CrossReferenceBuilder</strong> — linkea hallazgos high/critical con artículos del marco normativo (Constitución, LOE, LOP, jurisprudencia, ICCPR, CADH, CDI) mediante mapeo curado de 14 categorías.",
        "en": "<strong>CrossReferenceBuilder</strong> — links high/critical findings to normative-framework articles (Constitution, electoral law, jurisprudence, ICCPR, ACHR, IADC) through a curated 14-category mapping.",
        "pt": "<strong>CrossReferenceBuilder</strong> — vincula registros high/critical a artigos do marco normativo (Constituição, lei eleitoral, jurisprudência, ICCPR, CADH, CDI) por meio de mapeamento curado de 14 categorias.",
    },
    "appendix.a.li_predictive": {
        "es": "<strong>PredictiveEngine</strong> — motor híbrido de reglas deterministas + Claude Sonnet 4.6 para estimar escenarios probabilísticos de dinámica institucional post-proceso.",
        "en": "<strong>PredictiveEngine</strong> — hybrid engine combining deterministic rules + Claude Sonnet 4.6 to estimate probabilistic scenarios of post-process institutional dynamics.",
        "pt": "<strong>PredictiveEngine</strong> — motor híbrido de regras determinísticas + Claude Sonnet 4.6 para estimar cenários probabilísticos de dinâmica institucional pós-processo.",
    },
    "appendix.a.li_composer": {
        "es": "<strong>ChapterComposer</strong> — 12 prompts especializados con prompt caching de Anthropic, concurrency limit 4. Cada capítulo se genera con contexto compartido y datos específicos.",
        "en": "<strong>ChapterComposer</strong> — 12 specialised prompts with Anthropic prompt caching, concurrency limit 4. Each chapter is generated with shared context and chapter-specific data.",
        "pt": "<strong>ChapterComposer</strong> — 12 prompts especializados com prompt caching da Anthropic, concorrência limitada a 4. Cada capítulo é gerado com contexto compartilhado e dados específicos.",
    },
    "appendix.a.li_visualizer": {
        "es": "<strong>Visualizer + Renderer</strong> — SVG server-side con paleta institucional, HTML responsive, PDF A4 con tipografía Fraunces+DM Sans+DM Mono.",
        "en": "<strong>Visualizer + Renderer</strong> — server-side SVG with institutional palette, responsive HTML, A4 PDF with Fraunces + DM Sans + DM Mono typography.",
        "pt": "<strong>Visualizer + Renderer</strong> — SVG server-side com paleta institucional, HTML responsivo, PDF A4 com tipografia Fraunces + DM Sans + DM Mono.",
    },
    "appendix.a.h_sources": {
        "es": "Fuentes Hunter",
        "en": "Hunter Sources",
        "pt": "Fontes Hunter",
    },
    "appendix.a.p_sources": {
        "es": "Monitoreo RSS cada 24 horas sobre dos capas de fuentes. Capa nacional: Andina, El Comercio, Gestión, IDL-Reporteros, RPP Noticias, Wayka, JNE, ONPE. Capa internacional (filtrada por keyword \"Peru\"): BBC News Latin America, BBC Mundo, Deutsche Welle en español, El País Internacional, The Guardian World, NYT Americas. Clasificación automática con Claude Sonnet 4.6. Dedupe semántico por (categoría, URL normalizada, fecha). Priorización ponderada: severidad × recencia (decay exp. 3 días) × credibilidad de fuente.",
        "en": "RSS monitoring every 24 hours over two source layers. National: Andina, El Comercio, Gestión, IDL-Reporteros, RPP Noticias, Wayka, JNE, ONPE. International (keyword-filtered for \"Peru\"): BBC News Latin America, BBC Mundo, Deutsche Welle in Spanish, El País Internacional, The Guardian World, NYT Americas. Automatic classification with Claude Sonnet 4.6. Semantic dedupe by (category, normalised URL, date). Weighted prioritisation: severity × recency (3-day exponential decay) × source credibility.",
        "pt": "Monitoramento RSS a cada 24 horas sobre duas camadas de fontes. Camada nacional: Andina, El Comercio, Gestión, IDL-Reporteros, RPP Noticias, Wayka, JNE, ONPE. Camada internacional (filtrada por palavra-chave \"Peru\"): BBC News Latin America, BBC Mundo, Deutsche Welle em espanhol, El País Internacional, The Guardian World, NYT Americas. Classificação automática com Claude Sonnet 4.6. Dedupe semântico por (categoria, URL normalizada, data). Priorização ponderada: severidade × recência (decaimento exp. 3 dias) × credibilidade da fonte.",
    },
    "appendix.a.h_limits": {
        "es": "Limitaciones reconocidas",
        "en": "Acknowledged limitations",
        "pt": "Limitações reconhecidas",
    },
    "appendix.a.li_lim_bias": {
        "es": "Sesgo de fuentes: los medios monitoreados son mayoritariamente limeños; la cobertura regional es indirecta.",
        "en": "Source bias: monitored media are mostly Lima-based; regional coverage is indirect.",
        "pt": "Viés de fontes: os veículos monitorados são majoritariamente limenhos; a cobertura regional é indireta.",
    },
    "appendix.a.li_lim_horizon": {
        "es": "Horizonte predictivo: las estimaciones del PredictiveEngine cubren 2-4 semanas. Más allá pierden precisión.",
        "en": "Predictive horizon: PredictiveEngine estimates cover 2-4 weeks. Beyond that, precision degrades.",
        "pt": "Horizonte preditivo: as estimativas do PredictiveEngine cobrem 2-4 semanas. Além disso, perdem precisão.",
    },
    "appendix.a.li_lim_no_replace": {
        "es": "No reemplaza observación presencial: este informe complementa, no sustituye, las misiones oficiales de observación.",
        "en": "Does not replace on-site observation: this report complements, but does not substitute, official observation missions.",
        "pt": "Não substitui observação presencial: este relatório complementa, mas não substitui, as missões oficiais de observação.",
    },

    # ── Radar 8 dimensiones PEIRS — labels (Cap 10) ────────────────────────
    "viz.dim.suffrage":    {"es": "Sufragio",          "en": "Suffrage",            "pt": "Sufrágio"},
    "viz.dim.legal":       {"es": "Marco legal",       "en": "Legal framework",     "pt": "Marco legal"},
    "viz.dim.emb":         {"es": "Org. electoral",    "en": "Electoral body",      "pt": "Org. eleitoral"},
    "viz.dim.media":       {"es": "Medios",            "en": "Media",               "pt": "Mídia"},
    "viz.dim.finance":     {"es": "Financiamiento",    "en": "Campaign finance",    "pt": "Financiamento"},
    "viz.dim.digital":     {"es": "Digital / IA",      "en": "Digital / AI",        "pt": "Digital / IA"},
    "viz.dim.justice":     {"es": "Justicia electoral", "en": "Electoral justice",  "pt": "Justiça eleitoral"},
    "viz.dim.inclusivity": {"es": "Inclusividad",      "en": "Inclusivity",         "pt": "Inclusividade"},

    # ── Semaforo institucional — notes derivadas dinamicamente (Cap 10) ────
    "semaphore.note.crisis": {
        "es": "Crisis institucional reportada",
        "en": "Institutional crisis reported",
        "pt": "Crise institucional reportada",
    },
    "semaphore.note.high": {
        "es": "Múltiples hallazgos de alta severidad",
        "en": "Multiple high-severity findings",
        "pt": "Múltiplos achados de alta severidade",
    },
    "semaphore.note.tension": {
        "es": "Tensión institucional documentada",
        "en": "Documented institutional tension",
        "pt": "Tensão institucional documentada",
    },
    "semaphore.note.stable": {
        "es": "Sin incidentes graves reportados",
        "en": "No serious incidents reported",
        "pt": "Sem incidentes graves reportados",
    },
    "semaphore.note.no_data": {
        "es": "Sin datos en el corpus monitoreado",
        "en": "No data in monitored corpus",
        "pt": "Sem dados no corpus monitorado",
    },
    "semaphore.organ.global": {
        "es": "Proceso global",
        "en": "Overall process",
        "pt": "Processo global",
    },
}


_INSTRUMENT_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Mapeo de palabras "traducibles" en nombres de instrumentos normativos.
    # Las abreviaturas/acronimos (ICCPR, CADH, CDI, CEDAW, LOE, LOP, OSCE/ODIHR)
    # se mantienen — son acronimos canonicos de derecho internacional.
    # Solo se traducen las palabras locales como "Constitución" o nombres de
    # leyes peruanas con denominacion descriptiva.
    "Constitución Política del Perú": {
        "es": "Constitución Política del Perú",
        "en": "Political Constitution of Peru",
        "pt": "Constituição Política do Peru",
    },
    "Constitución Política": {
        "es": "Constitución Política",
        "en": "Political Constitution",
        "pt": "Constituição Política",
    },
    "Constitución": {
        "es": "Constitución",
        "en": "Constitution",
        "pt": "Constituição",
    },
    "Resoluciones JNE": {
        "es": "Resoluciones JNE",
        "en": "JNE Resolutions",
        "pt": "Resoluções JNE",
    },
    "Ley Orgánica de Elecciones": {
        "es": "Ley Orgánica de Elecciones",
        "en": "Electoral Organic Law",
        "pt": "Lei Orgânica Eleitoral",
    },
    "Ley de Organizaciones Políticas": {
        "es": "Ley de Organizaciones Políticas",
        "en": "Political Organizations Law",
        "pt": "Lei de Organizações Políticas",
    },
}


def translate_instrument(name: str, language: str) -> str:
    """Traduce nombre de instrumento normativo a en/pt.

    Las abreviaturas (ICCPR, CADH, CDI, CEDAW, LOE, LOP) se mantienen
    como acronimos canonicos. Solo las palabras descriptivas localizables
    (Constitución, Resoluciones, etc.) se reemplazan.

    Reemplazo por patron mas largo primero para evitar matches parciales
    (e.g. "Constitución Política del Perú" antes que "Constitución" sola).
    """
    if not name:
        return name
    lang = (language or "es").lower()
    if lang not in ("en", "pt"):
        return name
    # Patrones ordenados por longitud descendente
    for pattern in sorted(_INSTRUMENT_TRANSLATIONS.keys(), key=len, reverse=True):
        if pattern in name:
            replacement = _INSTRUMENT_TRANSLATIONS[pattern].get(lang, pattern)
            return name.replace(pattern, replacement, 1)
    return name


def t(language: str, key: str, default: str | None = None) -> str:
    """Lookup i18n. Cae a 'es' si la clave existe en español pero no en el
    idioma pedido (defensive). Si la clave no existe en absoluto, devuelve
    el default o el key mismo."""
    lang = (language or "es").lower()
    bundle = _STRINGS.get(key)
    if bundle is None:
        return default if default is not None else key
    return bundle.get(lang) or bundle.get("es") or default or key
