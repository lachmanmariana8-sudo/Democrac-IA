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
        "es": "Democrac.IA PEIRS monitoreó el ciclo electoral peruano de 2026 de forma continua a lo largo de sus dos vueltas: desde la fase pre-electoral —antes de la primera vuelta del 12 de abril— pasando por la fase entre vueltas, hasta el escrutinio de la segunda vuelta del 7 de junio. En ese período se clasificaron automáticamente **{n} hallazgos** de fuentes abiertas (RSS, OSINT propio y mediciones OONI), de los cuales **{n_alta}** se clasificaron de severidad alta o crítica, concentrados en las fases de escrutinio y de resolución de disputas (detalle trazable en el Anexo C).",
        "en": "Democrac.IA PEIRS continuously monitored Peru's 2026 electoral cycle across its two rounds: from the pre-electoral phase —before the first round on 12 April— through the inter-round phase, to the count of the second round on 7 June. In that period **{n} findings** were automatically classified from open sources (RSS, own OSINT and OONI measurements), of which **{n_alta}** were classified as high or critical severity, concentrated in the count and dispute-resolution phases (traceable detail in Appendix C).",
        "pt": "A Democrac.IA PEIRS monitorou continuamente o ciclo eleitoral peruano de 2026 ao longo de seus dois turnos: desde a fase pré-eleitoral —antes do primeiro turno de 12 de abril— passando pela fase entre turnos, até a apuração do segundo turno de 7 de junho. Nesse período foram classificados automaticamente **{n} achados** de fontes abertas (RSS, OSINT próprio e medições OONI), dos quais **{n_alta}** foram classificados de severidade alta ou crítica, concentrados nas fases de apuração e de resolução de disputas (detalhe rastreável no Anexo C).",
    },
    "declaration.patterns_intro": {
        "es": "El monitoreo de ambas vueltas identifica una convergencia de factores que tensiona la legitimidad del resultado:",
        "en": "Monitoring of both rounds identifies a convergence of factors straining the legitimacy of the result:",
        "pt": "O monitoramento de ambos os turnos identifica uma convergência de fatores que tensiona a legitimidade do resultado:",
    },
    "declaration.pattern_result": {
        "es": "- **Resultado al filo, sin proclamación oficial.** En la segunda vuelta, el cómputo oficial de la ONPE se cerró al {actas} % de actas el 29-jun-2026: {a} ({ap}) superó a {b} ({bp}) por apenas **~{margin} votos (≈{mp} pp)**, uno de los balotajes más estrechos de la historia peruana reciente. El JNE aún no proclama ganador: la proclamación oficial está fijada para el 15-jul-2026 (ONPE; El Comercio, 2026).",
        "en": "- **Razor-thin result, not yet proclaimed.** In the second round, ONPE's official count closed at {actas} % of tally sheets on 29 Jun 2026: {a} ({ap}) edged {b} ({bp}) by just **~{margin} votes (≈{mp} pp)**, one of the closest runoffs in recent Peruvian history. The JNE has not yet proclaimed a winner: the official proclamation is set for 15 Jul 2026 (ONPE; El Comercio, 2026).",
        "pt": "- **Resultado no limite, sem proclamação oficial.** No segundo turno, a apuração oficial da ONPE encerrou a {actas} % das atas em 29-jun-2026: {a} ({ap}) superou {b} ({bp}) por apenas **~{margin} votos (≈{mp} pp)**, um dos segundos turnos mais estreitos da história peruana recente. O JNE ainda não proclamou vencedor: a proclamação oficial está marcada para 15-jul-2026 (ONPE; El Comercio, 2026).",
    },
    "declaration.uncertainty": {
        "es": "- **Resultado estadísticamente indeterminado.** El margen (~{margin} votos) es menor que el volumen de votos en actas pendientes (~{pending}% del total) y ~{jee} actas en revisión en JEE: el desenlace no está definido por el cómputo actual.",
        "en": "- **Statistically undetermined result.** The margin (~{margin} votes) is smaller than the volume of votes in pending tally sheets (~{pending}% of total) and ~{jee} sheets under JEE review: the outcome is not determined by the current count.",
        "pt": "- **Resultado estatisticamente indeterminado.** A margem (~{margin} votos) é menor que o volume de votos em atas pendentes (~{pending}% do total) e ~{jee} atas em revisão no JEE: o desfecho não está definido pela apuração atual.",
    },
    "declaration.pattern_count": {
        "es": "- **Escrutinio prolongado.** El cómputo final al 100 % recién se alcanzó el 29-jun-2026, 22 días después de la votación, y la proclamación oficial del JNE quedó fijada para el 15-jul — una demora atípica que refleja el margen mínimo y las actas observadas en revisión en los JEE (JNE/ONPE, 2026).",
        "en": "- **Protracted count.** The 100 % final count was only reached on 29 Jun 2026, 22 days after the vote, and the JNE's official proclamation was set for 15 Jul — an atypical delay reflecting the razor-thin margin and observed tally sheets under JEE review (JNE/ONPE, 2026).",
        "pt": "- **Apuração prolongada.** A apuração final a 100 % só foi alcançada em 29-jun-2026, 22 dias após a votação, e a proclamação oficial do JNE foi marcada para 15-jul — um atraso atípico que reflete a margem mínima e as atas observadas em revisão nos JEE (JNE/ONPE, 2026).",
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
    "runoff_obs.more_in_panel": {
        "es": "(+{n} hallazgos más en este eje — detalle en el Panorama cuantitativo y el Anexo C, sin repetir aquí.)",
        "en": "(+{n} more findings in this axis — detail in the Quantitative overview and Appendix C, not repeated here.)",
        "pt": "(+{n} registros a mais neste eixo — detalhe no Panorama quantitativo e no Anexo C, sem repetir aqui.)",
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
    "runoff_obs.tbl.pct_prov": {"es": "% válidos", "en": "% valid", "pt": "% válidos"},
    "runoff_obs.tbl.votes_prov": {"es": "Votos", "en": "Votes", "pt": "Votos"},
    "runoff_obs.between_header": {
        "es": "Fase entre vueltas — monitoreo del proceso (13 abr – 7 jun 2026)",
        "en": "Between rounds — process monitoring (13 Apr – 7 Jun 2026)",
        "pt": "Entre turnos — monitoramento do processo (13 abr – 7 jun 2026)",
    },
    "runoff_obs.second_round_header": {
        "es": "Segunda vuelta — cómputo final ONPE al 100% (jornada del 7 de junio de 2026)",
        "en": "Second round — final ONPE count at 100% (election day 7 June 2026)",
        "pt": "Segundo turno — apuração final da ONPE a 100% (jornada de 7 de junho de 2026)",
    },
    "runoff_obs.second_round_status": {
        "es": "Cómputo oficial de ONPE **finalizado al {actas}% de actas** el {as_of}. Resultado del cómputo final, **pendiente de proclamación oficial del JNE**:",
        "en": "Official ONPE count **completed at {actas}% of tally sheets** on {as_of}. Final count result, **pending official JNE proclamation**:",
        "pt": "Apuração oficial da ONPE **concluída a {actas}% das atas** em {as_of}. Resultado da apuração final, **pendente de proclamação oficial do JNE**:",
    },
    "runoff_obs.second_round_finalized": {
        "es": "**Escrutinio finalizado:** {note}",
        "en": "**Count finalized:** {note}",
        "pt": "**Apuração concluída:** {note}",
    },
    "runoff_obs.second_round_delay": {
        "es": "**Implicancia de la demora.** {note}",
        "en": "**Implication of the delay.** {note}",
        "pt": "**Implicação do atraso.** {note}",
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
    # ── Hitos del ciclo (bloque 4) ───────────────────────────────────────
    "runoff_obs.milestones_header": {
        "es": "Hitos del ciclo electoral 2026", "en": "2026 electoral cycle milestones", "pt": "Marcos do ciclo eleitoral 2026",
    },
    "runoff_obs.milestone_r1": {
        "es": "- **{date}** — Primera vuelta. Pasan al balotaje {a} ({ap}) y {b} ({bp}).",
        "en": "- **{date}** — First round. {a} ({ap}) and {b} ({bp}) advance to the runoff.",
        "pt": "- **{date}** — Primeiro turno. {a} ({ap}) e {b} ({bp}) avançam ao segundo turno.",
    },
    "runoff_obs.milestone_emb": {
        "es": "- **14–16 abr** — Crisis institucional de la ONPE: su titular denunciado penalmente y pedidos de separación cautelar (véase eje EMB y Anexo C).",
        "en": "- **14–16 Apr** — ONPE institutional crisis: its head criminally charged and requests for precautionary removal (see EMB axis and Appendix C).",
        "pt": "- **14–16 abr** — Crise institucional da ONPE: seu titular denunciado penalmente e pedidos de afastamento cautelar (ver eixo EMB e Anexo C).",
    },
    "runoff_obs.milestone_between": {
        "es": "- **13 abr – 7 jun** — Fase entre vueltas: monitoreo del proceso.",
        "en": "- **13 Apr – 7 Jun** — Inter-round phase: process monitoring.",
        "pt": "- **13 abr – 7 jun** — Fase entre turnos: monitoramento do processo.",
    },
    "runoff_obs.milestone_r2": {
        "es": "- **{date}** — Segunda vuelta (balotaje).",
        "en": "- **{date}** — Second round (runoff).",
        "pt": "- **{date}** — Segundo turno.",
    },
    "runoff_obs.milestone_count": {
        "es": "- **{as_of}** — Escrutinio finalizado al {actas} % de actas: {winner} virtual ganadora por ~{margin} votos; proclamación oficial del JNE pendiente ({procl_date}).",
        "en": "- **{as_of}** — Count completed at {actas} % of tally sheets: {winner} virtual winner by ~{margin} votes; official JNE proclamation pending ({procl_date}).",
        "pt": "- **{as_of}** — Apuração concluída a {actas} % das atas: {winner} virtual vencedora por ~{margin} votos; proclamação oficial do JNE pendente ({procl_date}).",
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
        "es": "**Margen mínimo.** El resultado se definió por apenas ~{mp} puntos porcentuales (~{mv} votos) sobre el cómputo final al 100 % — uno de los más estrechos de la historia electoral peruana reciente.",
        "en": "**Razor-thin margin.** The result was decided by just ~{mp} percentage points (~{mv} votes) on the 100 % final count — one of the closest in recent Peruvian electoral history.",
        "pt": "**Margem mínima.** O resultado foi definido por apenas ~{mp} pontos percentuais (~{mv} votos) na apuração final a 100 % — um dos mais estreitos da história eleitoral peruana recente.",
    },
    "runoff_obs.risk_unproclaimed": {
        "es": "**Resultado aún no proclamado.** El cómputo de ONPE cerró al 100 % el 29-jun-2026, pero la proclamación oficial del JNE recién está fijada para el 15-jul-2026, más de cinco semanas después de la jornada.",
        "en": "**Result not yet proclaimed.** ONPE's count closed at 100 % on 29 Jun 2026, but the JNE's official proclamation is only set for 15 Jul 2026, more than five weeks after election day.",
        "pt": "**Resultado ainda não proclamado.** A apuração da ONPE encerrou a 100 % em 29-jun-2026, mas a proclamação oficial do JNE só está marcada para 15-jul-2026, mais de cinco semanas após a jornada.",
    },
    "runoff_obs.risk_emb": {
        "es": "**Órgano electoral cuestionado.** La ONPE atravesó la 1ª vuelta con su titular denunciado penalmente y pedidos de separación cautelar ({n} señales documentadas más arriba).",
        "en": "**Electoral body under question.** ONPE went through the first round with its head criminally charged and requests for precautionary removal ({n} signals documented above).",
        "pt": "**Órgão eleitoral questionado.** A ONPE atravessou o 1º turno com seu titular denunciado penalmente e pedidos de afastamento cautelar ({n} sinais documentados acima).",
    },
    "runoff_obs.risk_uncertainty": {
        "es": "**Resultado estadísticamente indeterminado.** El volumen de votos en actas pendientes y observadas (~{pending}% + ~{jee} actas en JEE) supera el margen (~{margin} votos): el desenlace no queda definido por el cómputo actual.",
        "en": "**Statistically undetermined result.** The volume of votes in pending and observed tally sheets (~{pending}% + ~{jee} sheets at JEE) exceeds the margin (~{margin} votes): the outcome is not settled by the current count.",
        "pt": "**Resultado estatisticamente indeterminado.** O volume de votos em atas pendentes e observadas (~{pending}% + ~{jee} atas no JEE) supera a margem (~{margin} votos): o desfecho não fica definido pela apuração atual.",
    },
    "runoff_obs.risk_suffrage_prefix": {
        "es": "Afectación al sufragio activo", "en": "Impact on the active right to vote", "pt": "Afetação ao sufrágio ativo",
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
        "es": "Nivel de riesgo del período. Combina el índice de severidad del corpus monitoreado (ponderado: crítico=1,0; alto=0,55; medio=0,20) con un piso por hechos institucionales documentados (crisis del EMB, resultado indeterminado, sistema de cómputo sin auditoría). Escala: verde = estable (sin tensiones relevantes) · ámbar = tensión incipiente · naranja = tensión elevada · rojo = riesgo crítico. Mayor = mayor riesgo.",
        "en": "Period risk level. Combines the severity index of the monitored corpus (weighted: critical=1.0; high=0.55; medium=0.20) with a floor from documented institutional facts (EMB crisis, undetermined result, unaudited count system). Scale: green = stable (no relevant strain) · amber = emerging strain · orange = elevated strain · red = critical risk. Higher = greater risk.",
        "pt": "Nível de risco do período. Combina o índice de severidade do corpus monitorado (ponderado: crítico=1,0; alto=0,55; médio=0,20) com um piso por fatos institucionais documentados (crise do EMB, resultado indeterminado, sistema de apuração sem auditoria). Escala: verde = estável · âmbar = tensão incipiente · laranja = tensão elevada · vermelho = risco crítico. Maior = maior risco.",
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

    # ── Panel cuantitativo (Bloque Q) ────────────────────────────────
    "viz.findings_by_round.title": {
        "es": "Hallazgos por fase electoral y severidad",
        "en": "Findings by electoral phase and severity",
        "pt": "Registros por fase eleitoral e severidade",
    },
    "viz.findings_by_round.caption": {
        "es": "Hallazgos del ciclo desglosados por severidad y por fase electoral: 1ª vuelta (hasta el 2-may-2026, incl. jornada del 12-abr y su cómputo), entre vueltas (3-may a 6-jun) y 2ª vuelta (desde la jornada del 7-jun: balotaje, escrutinio y post-electoral). Conteo sobre el universo CONSOLIDADO (un hecho = un hallazgo, sin duplicados de medios), coherente con el Anexo C y la base de prueba. El total consolidado es menor al volumen crudo de capturas monitoreadas.",
        "en": "Cycle findings broken down by severity and electoral phase: 1st round (through 2026-05-02, incl. the 12 Apr election day and its count), between rounds (3 May–6 Jun) and 2nd round (from the 7 Jun runoff day: balloting, count and post-election). Counts use the CONSOLIDATED universe (one fact = one finding, no media duplicates), consistent with Appendix C and the evidence base. The consolidated total is lower than the raw capture volume.",
        "pt": "Registros do ciclo por severidade e fase eleitoral: 1º turno (até 02-mai-2026, incl. jornada de 12-abr e sua apuração), entre turnos (3-mai a 6-jun) e 2º turno (desde a jornada de 7-jun: 2º turno, apuração e pós-eleição). Contagem sobre o universo CONSOLIDADO, coerente com o Anexo C e a base de provas. O total consolidado é menor que o volume bruto.",
    },
    "viz.rights_bars.title": {
        "es": "Derechos e instrumentos más invocados",
        "en": "Most-invoked rights and instruments",
        "pt": "Direitos e instrumentos mais invocados",
    },
    "viz.rights_bars.caption": {
        "es": "Instrumentos normativos (ICCPR, CADH, Constitución, etc.) invocados por los hallazgos del ciclo, ordenados por cantidad de hallazgos que los referencian. Deriva de las referencias cruzadas hallazgo→norma; reemplaza el mapa de calor denso por una lectura directa.",
        "en": "Normative instruments (ICCPR, ACHR, Constitution, etc.) invoked by the cycle's findings, ranked by number of findings referencing each. Derived from finding→norm cross-references; replaces the dense heatmap with a direct read.",
        "pt": "Instrumentos normativos (PIDCP, CADH, Constituição, etc.) invocados pelos registros do ciclo, ordenados pela quantidade de registros que os referenciam. Deriva das referências cruzadas registro→norma; substitui o mapa de calor denso por uma leitura direta.",
    },
    "viz.category_cloud.title": {
        "es": "Nube de hallazgos por temática",
        "en": "Findings cloud by topic",
        "pt": "Nuvem de registros por temática",
    },
    "viz.category_cloud.caption": {
        "es": "Temáticas de TODO el ciclo electoral (1ª vuelta, entre vueltas y 2ª vuelta): el tamaño es proporcional al volumen de hallazgos consolidados; el color indica la severidad máxima observada en la temática (rojo = crítico · naranja = alto · ámbar = medio). Se muestran todas las temáticas del ciclo.",
        "en": "Topics across the WHOLE electoral cycle (1st round, between rounds and 2nd round): size is proportional to the volume of consolidated findings; color indicates the maximum severity observed in the topic (red = critical · orange = high · amber = medium). All cycle topics are shown.",
        "pt": "Temáticas do ciclo: o tamanho é proporcional ao volume de registros consolidados; a cor indica a severidade máxima observada (vermelho = crítico · laranja = alto · âmbar = médio). Top-12 temáticas por volume.",
    },
    "quant.section.title": {
        "es": "Panorama cuantitativo",
        "en": "Quantitative overview",
        "pt": "Panorama quantitativo",
    },
    "quant.section.intro": {
        "es": "Síntesis cuantitativa del ciclo monitoreado: distribución de hallazgos por vuelta y severidad, y concentración temática. Todas las cifras se calculan sobre el corpus consolidado (un hecho = un hallazgo con todas sus fuentes); ver metodología bajo cada figura y el detalle trazable en el Anexo C.",
        "en": "Quantitative synthesis of the monitored cycle: distribution of findings by round and severity, and topic concentration. All figures are computed on the consolidated corpus (one fact = one finding with all its sources); see methodology under each figure and the traceable detail in Appendix C.",
        "pt": "Síntese quantitativa do ciclo monitorado: distribuição de registros por turno e severidade, e concentração temática. Todos os números são calculados sobre o corpus consolidado (um fato = um registro com todas as fontes); ver metodologia sob cada figura e o detalhe rastreável no Anexo C.",
    },
    "quant.kpi.consolidated": {
        "es": "Hallazgos consolidados",
        "en": "Consolidated findings",
        "pt": "Registros consolidados",
    },
    "quant.kpi.round1": {"es": "1ª vuelta", "en": "1st round", "pt": "1º turno"},
    "quant.kpi.round2": {"es": "2ª vuelta", "en": "2nd round", "pt": "2º turno"},
    "quant.kpi.interround": {"es": "Entre vueltas", "en": "Between rounds", "pt": "Entre turnos"},
    "quant.kpi.topics": {"es": "Temáticas", "en": "Topics", "pt": "Temáticas"},
    "quant.tbl.severity": {"es": "Severidad", "en": "Severity", "pt": "Severidade"},
    "quant.tbl.total": {"es": "Total", "en": "Total", "pt": "Total"},

    # Desglose temático (tabla categoría → +N → ejemplos)
    "theme.title": {
        "es": "Hallazgos por temática (con ejemplos trazables)",
        "en": "Findings by topic (with traceable examples)",
        "pt": "Registros por temática (com exemplos rastreáveis)",
    },
    "theme.caption": {
        "es": "Conteo deduplicado por temática (un hecho = un hallazgo); el signo «+» indica que es un piso verificado. La suma de las temáticas = {total} hechos consolidados. Se muestran 1-2 ejemplos representativos por temática (mayor prioridad), cada uno enlazado a su fuente primaria; el universo íntegro y trazable está en el Anexo C y en la base de prueba.",
        "en": "Deduplicated count per topic (one fact = one finding); the «+» sign marks a verified floor. Topics sum to {total} consolidated facts. 1-2 representative examples per topic (highest priority) are shown, each linked to its primary source; the full traceable universe is in Appendix C and the evidence base.",
        "pt": "Contagem deduplicada por temática (um fato = um registro); o sinal «+» indica um piso verificado. A soma das temáticas = {total} fatos consolidados. Mostram-se 1-2 exemplos representativos por temática (maior prioridade), cada um com link à fonte primária; o universo íntegro está no Anexo C e na base de provas.",
    },
    # Tabla de eventos críticos (reemplaza la línea de tiempo amontonada)
    "crit.title": {
        "es": "Eventos críticos del ciclo monitoreado",
        "en": "Critical events of the monitored cycle",
        "pt": "Eventos críticos do ciclo monitorado",
    },
    "crit.caption": {
        "es": "Hallazgos de severidad crítica y alta del ciclo, ordenados por severidad y fecha (hasta 14), con el órgano implicado y enlace a la fuente primaria. Reemplaza la línea de tiempo previa, que amontonaba los eventos más tempranos y resultaba ilegible. El detalle completo está en el Anexo C y la base de prueba.",
        "en": "Critical- and high-severity findings of the cycle, ordered by severity and date (up to 14), with the body involved and a link to the primary source. Replaces the previous timeline, which clustered the earliest events and was unreadable. Full detail in Appendix C and the evidence base.",
        "pt": "Registros de severidade crítica e alta do ciclo, ordenados por severidade e data (até 14), com o órgão implicado e link à fonte primária. Substitui a linha do tempo anterior, que amontoava os eventos mais antigos. Detalhe completo no Anexo C e na base de provas.",
    },
    "crit.col.date": {"es": "Fecha", "en": "Date", "pt": "Data"},
    "crit.col.sev": {"es": "Severidad", "en": "Severity", "pt": "Severidade"},
    "crit.col.organ": {"es": "Órgano", "en": "Body", "pt": "Órgão"},
    "crit.col.event": {"es": "Evento", "en": "Event", "pt": "Evento"},
    "crit.col.source": {"es": "Fuente", "en": "Source", "pt": "Fonte"},
    "theme.col.topic": {"es": "Temática", "en": "Topic", "pt": "Temática"},
    "theme.col.count": {"es": "Hallazgos", "en": "Findings", "pt": "Registros"},
    "theme.col.sevmax": {"es": "Sev. máx.", "en": "Max sev.", "pt": "Sev. máx."},
    "theme.col.examples": {"es": "Ejemplos representativos", "en": "Representative examples", "pt": "Exemplos representativos"},
    "appendix.c.evidence_base": {
        "es": "Este anexo es una MUESTRA trazable. La base de prueba completa y verificable — {dedup} hechos consolidados a partir de {raw} capturas, cada uno con su(s) fuente(s) — está archivada y sellada por integridad (sha256):",
        "en": "This appendix is a traceable SAMPLE. The full, verifiable evidence base — {dedup} consolidated facts from {raw} captures, each with its source(s) — is archived and integrity-sealed (sha256):",
        "pt": "Este anexo é uma AMOSTRA rastreável. A base de provas completa e verificável — {dedup} fatos consolidados a partir de {raw} capturas, cada um com sua(s) fonte(s) — está arquivada e selada por integridade (sha256):",
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
    "appendix.a.li_lim_classifier": {
        "es": "Clasificación automática por IA sin validación humana sistemática: categoría y severidad pueden contener error de clasificación. Ver versión del clasificador abajo.",
        "en": "Automatic AI classification without systematic human validation: category and severity may contain classification error. See classifier version below.",
        "pt": "Classificação automática por IA sem validação humana sistemática: categoria e severidade podem conter erro. Ver versão do classificador abaixo.",
    },
    "appendix.a.li_lim_llm": {
        "es": "Los capítulos narrativos se redactan con un modelo de lenguaje y NO son deterministas entre corridas; las secciones de datos (apertura, resultados, hitos, anexos) son deterministas y reproducibles.",
        "en": "Narrative chapters are written with a language model and are NOT deterministic across runs; data sections (opening, results, milestones, appendices) are deterministic and reproducible.",
        "pt": "Os capítulos narrativos são redigidos com um modelo de linguagem e NÃO são determinísticos entre execuções; as seções de dados (abertura, resultados, marcos, anexos) são determinísticas e reproduzíveis.",
    },
    "appendix.a.h_sampling": {
        "es": "Marco muestral y cobertura", "en": "Sampling frame and coverage", "pt": "Marco amostral e cobertura",
    },
    "appendix.a.p_sampling": {
        "es": "El corpus proviene de fuentes abiertas (RSS de medios, monitoreo OSINT propio y mediciones OONI). Sobre-representa eventos de alta saliencia mediática, urbanos y en castellano; sub-representa lo rural, lo no digital y lenguas originarias. Los conteos son volúmenes del corpus, no estimaciones poblacionales.",
        "en": "The corpus comes from open sources (media RSS, own OSINT monitoring and OONI measurements). It over-represents high media-salience, urban and Spanish-language events; it under-represents rural, non-digital and Indigenous-language events. Counts are corpus volumes, not population estimates.",
        "pt": "O corpus provém de fontes abertas (RSS de mídia, monitoramento OSINT próprio e medições OONI). Sobre-representa eventos de alta saliência midiática, urbanos e em espanhol; sub-representa o rural, o não digital e línguas originárias. As contagens são volumes do corpus, não estimativas populacionais.",
    },
    "appendix.a.h_version": {
        "es": "Versión y trazabilidad del pipeline", "en": "Pipeline version and traceability", "pt": "Versão e rastreabilidade do pipeline",
    },
    "appendix.a.p_version": {
        "es": "Parámetros exactos con los que se produjo este informe (auditables por terceros):",
        "en": "Exact parameters with which this report was produced (third-party auditable):",
        "pt": "Parâmetros exatos com que este relatório foi produzido (auditáveis por terceiros):",
    },
    "appendix.a.ver.pipeline": {"es": "Versión de pipeline", "en": "Pipeline version", "pt": "Versão do pipeline"},
    "appendix.a.ver.config": {"es": "Versión de configuración", "en": "Config version", "pt": "Versão da configuração"},
    "appendix.a.ver.classifier": {"es": "Clasificador (Hunter)", "en": "Classifier (Hunter)", "pt": "Classificador (Hunter)"},
    "appendix.a.ver.llm": {"es": "Modelo de redacción", "en": "Drafting model", "pt": "Modelo de redação"},
    "appendix.a.ver.thresholds": {"es": "Umbrales", "en": "Thresholds", "pt": "Limiares"},
    "appendix.a.ver.classifier_quality": {
        "es": "Calidad del clasificador", "en": "Classifier quality", "pt": "Qualidade do classificador"},
    "appendix.a.ver.gold_set": {"es": "muestra de oro", "en": "gold set", "pt": "amostra de ouro"},
    # ── P2: Auditoría de sesgo por actor ─────────────────────────────────
    "appendix.a.h_bias": {
        "es": "Auditoría de sesgo por tipo de actor",
        "en": "Bias audit by actor type",
        "pt": "Auditoria de viés por tipo de ator",
    },
    "appendix.a.p_bias": {
        "es": "Severidad media (escala 1=info … 5=crítico) de los hallazgos según el tipo de actor involucrado. Severidad media global del corpus: {g}. Una desviación marcada respecto a la media global (⚠) señala posible sesgo de severidad por actor y exige revisión humana; no implica error, sino punto de control de imparcialidad.",
        "en": "Mean severity (scale 1=info … 5=critical) of findings by the actor type involved. Corpus global mean severity: {g}. A marked deviation from the global mean (⚠) signals possible per-actor severity bias and warrants human review; it does not imply error but an impartiality checkpoint.",
        "pt": "Severidade média (escala 1=info … 5=crítico) dos registros segundo o tipo de ator envolvido. Severidade média global do corpus: {g}. Um desvio marcado em relação à média global (⚠) sinaliza possível viés de severidade por ator e exige revisão humana.",
    },
    "appendix.a.bias.actor": {"es": "Tipo de actor", "en": "Actor type", "pt": "Tipo de ator"},
    "appendix.a.bias.count": {"es": "Hallazgos", "en": "Findings", "pt": "Registros"},
    "appendix.a.bias.mean": {"es": "Severidad media", "en": "Mean severity", "pt": "Severidade média"},
    "appendix.a.bias.delta": {"es": "Δ vs. global", "en": "Δ vs. global", "pt": "Δ vs. global"},
    # ── Dashboard ejecutivo ──────────────────────────────────────────────
    "exec.title": {"es": "Resumen ejecutivo", "en": "Executive summary", "pt": "Resumo executivo"},
    "exec.kpi.findings": {"es": "Hallazgos", "en": "Findings", "pt": "Achados"},
    "exec.kpi.consolidated": {"es": "Hechos consolidados", "en": "Consolidated facts", "pt": "Fatos consolidados"},
    "exec.kpi.captures": {"es": "Capturas monitoreadas", "en": "Monitored captures", "pt": "Capturas monitoradas"},
    "exec.kpi.critical": {"es": "Críticos", "en": "Critical", "pt": "Críticos"},
    "exec.kpi.high": {"es": "Severidad alta", "en": "High severity", "pt": "Severidade alta"},
    "exec.kpi.days": {"es": "Días monitoreados", "en": "Days monitored", "pt": "Dias monitorados"},
    "exec.kpi.risk": {"es": "Nivel de riesgo", "en": "Risk level", "pt": "Nível de risco"},
    "exec.traceability": {
        "es": "Base de prueba: {consolidated} hechos consolidados (un hecho = un hallazgo, sin repetir) a partir de {raw} capturas monitoreadas — 100% con fuente primaria, archivada y sellada por integridad (sha256). Detalle trazable en el Anexo C.",
        "en": "Evidence base: {consolidated} consolidated facts (one fact = one finding, no duplicates) from {raw} monitored captures — 100% with a primary source, archived and integrity-sealed (sha256). Traceable detail in Appendix C.",
        "pt": "Base de provas: {consolidated} fatos consolidados (um fato = um registro, sem repetir) a partir de {raw} capturas monitoradas — 100% com fonte primária, arquivada e selada por integridade (sha256). Detalhe rastreável no Anexo C.",
    },
    # ── Panel internacional ──────────────────────────────────────────────
    "intl.title": {
        "es": "Indicadores internacionales de democracia",
        "en": "International democracy indicators",
        "pt": "Indicadores internacionais de democracia",
    },
    "intl.col.indicator": {"es": "Indicador", "en": "Indicator", "pt": "Indicador"},
    "intl.col.value": {"es": "Último valor", "en": "Latest value", "pt": "Último valor"},
    "intl.col.initial": {"es": "Inicial", "en": "Initial", "pt": "Inicial"},
    "intl.col.current": {"es": "Actual", "en": "Current", "pt": "Atual"},
    "intl.col.trend": {"es": "Tendencia", "en": "Trend", "pt": "Tendência"},
    "intl.col.variation": {"es": "Variación", "en": "Change", "pt": "Variação"},
    "intl.col.unit": {"es": "Escala", "en": "Scale", "pt": "Escala"},
    "intl.col.source": {"es": "Fuente", "en": "Source", "pt": "Fonte"},
    "intl.windows_note": {
        "es": "Las ventanas temporales difieren por dataset: cada serie usa su rango disponible más reciente (p. ej. PEI hasta 2021; RSF desde 2024). La variación se calcula sobre los extremos de cada serie, no sobre un año común.",
        "en": "Time windows differ by dataset: each series uses its most recent available range (e.g. PEI through 2021; RSF from 2024). Change is computed over each series' own endpoints, not a common year.",
        "pt": "As janelas temporais diferem por dataset: cada série usa seu intervalo disponível mais recente (ex.: PEI até 2021; RSF desde 2024). A variação é calculada sobre os extremos de cada série, não sobre um ano comum.",
    },
    "intl.intro": {
        "es": "Cómo venía el proceso electoral según los principales índices internacionales: valor al inicio de la serie disponible y valor más reciente, con su tendencia.",
        "en": "How the electoral process was trending per the main international indices: value at the start of the available series and the most recent value, with its trend.",
        "pt": "Como vinha o processo eleitoral segundo os principais índices internacionais: valor no início da série disponível e valor mais recente, com sua tendência.",
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


# ── Etiquetas de categoría de hallazgo (nube temática, Bloque Q) ──────────
_CATEGORY_LABELS: dict[str, dict[str, str]] = {
    "voter_suppression":   {"es": "Restricción del voto",  "en": "Voter suppression",   "pt": "Restrição do voto"},
    "legal":               {"es": "Legal/normativo",       "en": "Legal/regulatory",    "pt": "Legal/normativo"},
    "irregular_procedure": {"es": "Procedimiento irregular","en": "Irregular procedure", "pt": "Procedimento irregular"},
    "logistics":           {"es": "Logística electoral",   "en": "Electoral logistics", "pt": "Logística eleitoral"},
    "fraud_allegation":    {"es": "Denuncia de fraude",     "en": "Fraud allegation",    "pt": "Denúncia de fraude"},
    "counting":            {"es": "Escrutinio/cómputo",     "en": "Vote counting",       "pt": "Apuração"},
    "results":             {"es": "Resultados",             "en": "Results",             "pt": "Resultados"},
    "media":               {"es": "Medios/cobertura",       "en": "Media coverage",      "pt": "Mídia/cobertura"},
    "hate_speech":         {"es": "Discurso de odio",       "en": "Hate speech",         "pt": "Discurso de ódio"},
    "disinformation":      {"es": "Desinformación",         "en": "Disinformation",      "pt": "Desinformação"},
    "campaign_violation":  {"es": "Financiamiento/campaña", "en": "Campaign finance",    "pt": "Financiamento/campanha"},
    "digital":             {"es": "Entorno digital",        "en": "Digital environment", "pt": "Ambiente digital"},
    "judicial":            {"es": "Judicial",               "en": "Judicial",            "pt": "Judicial"},
    "security":            {"es": "Seguridad/violencia",    "en": "Security/violence",   "pt": "Segurança/violência"},
    "media_restriction":   {"es": "Restricción mediática",  "en": "Media restriction",   "pt": "Restrição à mídia"},
    "ballot_tampering":    {"es": "Manipulación de cédulas/actas", "en": "Ballot tampering", "pt": "Manipulação de cédulas/atas"},
    "accessibility":       {"es": "Accesibilidad",          "en": "Accessibility",       "pt": "Acessibilidade"},
    "voter_intimidation":  {"es": "Intimidación al votante", "en": "Voter intimidation",  "pt": "Intimidação do eleitor"},
    "other":               {"es": "Otros",                  "en": "Other",               "pt": "Outros"},
}


def category_label(category: str, language: str) -> str:
    """Etiqueta legible para una categoría de hallazgo (nube temática).
    Cae al título-case del key si la categoría no está mapeada."""
    lang = (language or "es").lower()
    bundle = _CATEGORY_LABELS.get((category or "other").lower())
    if bundle:
        return bundle.get(lang) or bundle.get("es") or category
    return (category or "other").replace("_", " ").capitalize()


def t(language: str, key: str, default: str | None = None) -> str:
    """Lookup i18n. Cae a 'es' si la clave existe en español pero no en el
    idioma pedido (defensive). Si la clave no existe en absoluto, devuelve
    el default o el key mismo."""
    lang = (language or "es").lower()
    bundle = _STRINGS.get(key)
    if bundle is None:
        return default if default is not None else key
    return bundle.get(lang) or bundle.get("es") or default or key
