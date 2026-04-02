"""
DEMOCRAC.IA — Cuestionario de Evaluación de Ciclo Electoral
===========================================================
Cuestionario estructurado para observadores de campo que permite
comparar las respuestas del observador con los scores de los datasets
(V-Dem v15, FH FIW 2025, RSF 2025, PEI v10.0) al final del ciclo.

Escala de respuesta (Likert extendida):
  5 — Cumple plenamente / Sin problemas detectados
  4 — Cumple con observaciones menores
  3 — Cumplimiento parcial / Problemas aislados
  2 — Incumplimiento significativo / Problemas sistemáticos
  1 — Incumplimiento grave / Violación abierta
  0 — Sin información (observador no pudo verificar)

Conversión a escala 0-100: score * 20 → 100=máximo, 0=mínimo.
"""

from typing import List, Optional, Dict, Any

# ─── Escala estándar ──────────────────────────────────────────────────────────
SCALE_LIKERT5 = [
    {"value": 5, "label": "5 — Cumple plenamente"},
    {"value": 4, "label": "4 — Cumple con observaciones menores"},
    {"value": 3, "label": "3 — Cumplimiento parcial"},
    {"value": 2, "label": "2 — Incumplimiento significativo"},
    {"value": 1, "label": "1 — Incumplimiento grave"},
    {"value": 0, "label": "Sin información"},
]

SCALE_YESNO = [
    {"value": 5, "label": "Sí — plenamente"},
    {"value": 3, "label": "Parcialmente"},
    {"value": 1, "label": "No"},
    {"value": 0, "label": "Sin información"},
]

SCALE_PRESENCE = [
    {"value": 5, "label": "Ausente / No detectado"},
    {"value": 3, "label": "Presente en casos aislados"},
    {"value": 1, "label": "Presente de forma sistemática"},
    {"value": 0, "label": "Sin información"},
]


def q(id_, section, dimension, ire_dim, text, scale, dataset_var,
       dataset_source, iccpr_ref, note=None):
    """Constructor de pregunta estandarizado."""
    return {
        "id": id_,
        "section": section,
        "dimension": dimension,
        "ire_dimension": ire_dim,
        "text": text,
        "scale": scale,
        "dataset_var": dataset_var,
        "dataset_source": dataset_source,
        "iccpr_ref": iccpr_ref,
        "note": note,
        "observer_answer": None,   # null hasta que el observador responda
        "platform_score": None,    # se completa al generar el cuestionario
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CUESTIONARIO COMPLETO — 68 preguntas, 10 secciones
# ═══════════════════════════════════════════════════════════════════════════════

QUESTIONNAIRE: List[Dict[str, Any]] = [

    # ─── SECCIÓN 1: OGE / ADMINISTRACIÓN ELECTORAL (8 preguntas) ──────────────
    # Mapea a: V-Dem v2elembaut, v2elembcap / PEI emb_score, election_authorities

    q("S1_Q1", "OGE y Administración Electoral", "Independencia del OGE", 3,
      "¿El JNE actuó con independencia del poder ejecutivo y legislativo durante el ciclo electoral observado?",
      SCALE_LIKERT5, "emb_autonomy", "V-Dem v2elembaut",
      "ICCPR Art. 25(b); CADH Art. 23",
      "Observar: ¿hubo presiones públicas, declaraciones de funcionarios, interferencia en resoluciones?"),

    q("S1_Q2", "OGE y Administración Electoral", "Independencia del OGE", 3,
      "¿La ONPE administró la logística electoral (materiales, actas, transmisión) de forma técnica y sin sesgo partidario?",
      SCALE_LIKERT5, "emb_capacity", "V-Dem v2elembcap",
      "ICCPR Art. 25(b); CDI Art. 5",
      "Incluye: entrega de materiales, capacitación de mesa, transmisión de resultados ACTA."),

    q("S1_Q3", "OGE y Administración Electoral", "Independencia del OGE", 3,
      "¿El JNE resolvió las impugnaciones y recursos electorales de forma oportuna, motivada e imparcial?",
      SCALE_LIKERT5, "election_authorities", "PEI v10.0 — ELECTIONAUTHORITIES",
      "ICCPR Art. 25(b); CADH Art. 8",
      "Tomar nota de casos de demora injustificada, resoluciones sin motivación o con efecto político evidente."),

    q("S1_Q4", "OGE y Administración Electoral", "Independencia del OGE", 3,
      "¿La composición del JNE/ONPE/RENIEC reflejó pluralismo y ausencia de captura por partido en el gobierno?",
      SCALE_LIKERT5, "emb_autonomy", "V-Dem v2elembaut",
      "ICCPR Art. 25; CDI Art. 4",
      None),

    q("S1_Q5", "OGE y Administración Electoral", "Independencia del OGE", 3,
      "¿Los organismos electorales publicaron sus decisiones con transparencia suficiente (actas, resoluciones, comunicados)?",
      SCALE_LIKERT5, "emb_capacity", "V-Dem v2elembcap",
      "ICCPR Art. 25; CDI Art. 4",
      "Verificar portal JNE, ONPE, RENIEC durante la observación."),

    q("S1_Q6", "OGE y Administración Electoral", "Independencia del OGE", 3,
      "¿El RENIEC garantizó un padrón actualizado, accesible y libre de errores materiales significativos?",
      SCALE_LIKERT5, "voter_registration", "PEI v10.0 — VOTERREGISTRATION",
      "ICCPR Art. 25(b)",
      "Considerar: depuración de fallecidos, duplicados, electores con DNI vencido."),

    q("S1_Q7", "OGE y Administración Electoral", "Independencia del OGE", 3,
      "¿Existió coordinación efectiva entre JNE, ONPE y RENIEC sin solapamientos o conflictos de competencia?",
      SCALE_LIKERT5, "emb_capacity", "V-Dem v2elembcap",
      "CDI Art. 5",
      None),

    q("S1_Q8", "OGE y Administración Electoral", "Independencia del OGE", 3,
      "¿Los partidos políticos y observadores internacionales tuvieron acceso efectivo a los procesos del OGE?",
      SCALE_LIKERT5, "emb_autonomy", "V-Dem v2elembaut + PEI",
      "ICCPR Art. 25; CADH Art. 23",
      "Incluye: acreditación de fiscales de partido, acceso a centros de cómputo, respuesta a solicitudes de información."),

    # ─── SECCIÓN 2: MARCO LEGAL ELECTORAL (7 preguntas) ──────────────────────
    # Mapea a: V-Dem v2x_polyarchy, v2xcl_rol, v2psbars / PEI legal_framework, procedures

    q("S2_Q1", "Marco Legal Electoral", "Marco Legal", 2,
      "¿El marco legal electoral (Ley Orgánica de Elecciones, Ley de Partidos Políticos) garantizó condiciones de competencia equitativa?",
      SCALE_LIKERT5, "legal_framework", "PEI v10.0 — LAWS",
      "ICCPR Art. 25; CADH Art. 23(2)",
      None),

    q("S2_Q2", "Marco Legal Electoral", "Marco Legal", 2,
      "¿Las reglas electorales favorecieron indebidamente al partido/candidato en el gobierno (legislación ad hoc, cambios tardíos)?",
      SCALE_PRESENCE, "legal_framework", "PEI v10.0 — LAWS",
      "ICCPR Art. 25; CDI Art. 3",
      "Atención a cambios de reglas a menos de 90 días de la elección."),

    q("S2_Q3", "Marco Legal Electoral", "Marco Legal", 2,
      "¿Los procedimientos de inscripción de candidatos fueron justos, claros y aplicados de forma no discriminatoria?",
      SCALE_LIKERT5, "procedures", "PEI v10.0 — PROCEDURES",
      "ICCPR Art. 25(b); CADH Art. 23(2)",
      None),

    q("S2_Q4", "Marco Legal Electoral", "Marco Legal", 2,
      "¿Existieron requisitos legales que impidieron arbitrariamente la candidatura de personas o grupos?",
      SCALE_PRESENCE, "electoral_democracy", "V-Dem v2x_polyarchy",
      "ICCPR Art. 25(b); CADH Art. 23(2)",
      "Incluir: inhabilitaciones, restricciones de domicilio, cuotas violadas."),

    q("S2_Q5", "Marco Legal Electoral", "Marco Legal", 2,
      "¿El sistema judicial ordinario y electoral garantizó el estado de derecho durante el proceso electoral?",
      SCALE_LIKERT5, "rule_of_law", "V-Dem v2xcl_rol",
      "ICCPR Art. 14; CADH Art. 8",
      None),

    q("S2_Q6", "Marco Legal Electoral", "Marco Legal", 2,
      "¿Los partidos de oposición pudieron operar con libertad de movimiento, reunión y expresión durante la campaña?",
      SCALE_LIKERT5, "opposition_autonomy", "V-Dem v2psoppaut",
      "ICCPR Art. 19, 21, 22; CADH Art. 13, 15, 16",
      None),

    q("S2_Q7", "Marco Legal Electoral", "Marco Legal", 2,
      "¿El sistema de barreras electorales (umbral de votos para partidos) fue proporcional y no discriminatorio?",
      SCALE_LIKERT5, "opposition_party_barriers", "V-Dem v2psbars",
      "ICCPR Art. 25; CADH Art. 23",
      None),

    # ─── SECCIÓN 3: PADRÓN Y REGISTRO ELECTORAL (6 preguntas) ───────────────
    # Mapea a: PEI voter_registration / V-Dem v2x_suffr

    q("S3_Q1", "Padrón y Registro Electoral", "Sufragio Universal", 1,
      "¿El padrón electoral estuvo disponible para consulta pública con suficiente anticipación a la elección?",
      SCALE_LIKERT5, "voter_registration", "PEI v10.0 — VOTERREGISTRATION",
      "ICCPR Art. 25(b)",
      "Estándar: disponible en línea y en sedes de RENIEC al menos 30 días antes."),

    q("S3_Q2", "Padrón y Registro Electoral", "Sufragio Universal", 1,
      "¿El padrón exterior fue depurado de forma efectiva (electores con documentos vencidos, fallecidos, duplicados)?",
      SCALE_LIKERT5, "voter_registration", "PEI v10.0 — VOTERREGISTRATION",
      "ICCPR Art. 25(b); ICERD Art. 5(c)",
      "Referencia: Informe de Depuración RENIEC N°001-2026 — 23,000 electores con DNI vencido."),

    q("S3_Q3", "Padrón y Registro Electoral", "Sufragio Universal", 1,
      "¿Los ciudadanos peruanos en el exterior pudieron ejercer su derecho al voto sin restricciones logísticas o documentales irrazonables?",
      SCALE_LIKERT5, "universal_suffrage", "V-Dem v2x_suffr",
      "ICCPR Art. 25(b); CADH Art. 23(1)(b)",
      None),

    q("S3_Q4", "Padrón y Registro Electoral", "Sufragio Universal", 1,
      "¿Los mecanismos de corrección del padrón (tachas, inclusiones, rectificaciones) funcionaron de forma accesible y oportuna?",
      SCALE_LIKERT5, "voter_registration", "PEI v10.0 — VOTERREGISTRATION",
      "ICCPR Art. 25(b)",
      None),

    q("S3_Q5", "Padrón y Registro Electoral", "Sufragio Universal", 1,
      "¿Hubo denuncias verificadas de electores excluidos arbitrariamente del padrón?",
      SCALE_PRESENCE, "voter_registration", "PEI v10.0 — VOTERREGISTRATION",
      "ICCPR Art. 25(b); CADH Art. 23",
      None),

    q("S3_Q6", "Padrón y Registro Electoral", "Sufragio Universal", 1,
      "¿El procedimiento de verificación de identidad en mesa fue uniforme y no discriminatorio?",
      SCALE_LIKERT5, "universal_suffrage", "V-Dem v2x_suffr",
      "ICCPR Art. 25(b); ICERD Art. 5(c)",
      None),

    # ─── SECCIÓN 4: INCLUSIVIDAD Y DERECHOS DIFERENCIALES (6 preguntas) ─────
    # Mapea a: V-Dem v2x_suffr / FH CL / CEDAW Art.7 / CRPD Art.29

    q("S4_Q1", "Inclusividad y Derechos Diferenciales", "Inclusión Electoral", 8,
      "¿Se garantizó la participación de mujeres como candidatas sin obstáculos discriminatorios específicos (paridad, acoso, financiamiento)?",
      SCALE_LIKERT5, "universal_suffrage", "V-Dem v2x_suffr + CEDAW",
      "CEDAW Art. 7; ICCPR Art. 3, 25; CADH Art. 23",
      "Perú tiene cuota de paridad 50%. Verificar listas de candidatos presentadas."),

    q("S4_Q2", "Inclusividad y Derechos Diferenciales", "Inclusión Electoral", 8,
      "¿Los centros de votación fueron accesibles para personas con discapacidad (rampas, señalización, asistencia)?",
      SCALE_LIKERT5, "universal_suffrage", "CRPD Art. 29",
      "CRPD Art. 29; ICCPR Art. 25",
      "Verificar en al menos 5 centros de votación durante la jornada."),

    q("S4_Q3", "Inclusividad y Derechos Diferenciales", "Inclusión Electoral", 8,
      "¿Las comunidades indígenas y campesinas tuvieron acceso al proceso electoral en condiciones lingüísticas y geográficas adecuadas?",
      SCALE_LIKERT5, "universal_suffrage", "V-Dem v2x_suffr + UNDRIP",
      "UNDRIP Arts. 5, 18; ICCPR Art. 25",
      "Especialmente relevante en regiones: Cusco, Puno, Loreto, Ucayali, Amazonas."),

    q("S4_Q4", "Inclusividad y Derechos Diferenciales", "Inclusión Electoral", 8,
      "¿Hubo violencia política de género: amenazas, agresiones físicas o simbólicas dirigidas específicamente a candidatas o electoras?",
      SCALE_PRESENCE, "universal_suffrage", "CEDAW Art. 7 + CADH",
      "CEDAW Art. 7; ICCPR Art. 3; CADH Art. 23",
      None),

    q("S4_Q5", "Inclusividad y Derechos Diferenciales", "Inclusión Electoral", 8,
      "¿Se respetaron los derechos de los adultos mayores como electores (acceso, asistencia, no manipulación)?",
      SCALE_LIKERT5, "universal_suffrage", "V-Dem v2x_suffr",
      "ICCPR Art. 25",
      None),

    q("S4_Q6", "Inclusividad y Derechos Diferenciales", "Inclusión Electoral", 8,
      "¿Los materiales electorales (papeletas, actas, guías) estuvieron disponibles en idiomas distintos al castellano donde correspondía?",
      SCALE_LIKERT5, "universal_suffrage", "UNDRIP Art. 18; CRPD Art. 29",
      "UNDRIP Art. 18; ICCPR Art. 25",
      "Verificar disponibilidad en quechua/aymara/amazónico según región de observación."),

    # ─── SECCIÓN 5: CAMPAÑA ELECTORAL Y FINANCIAMIENTO (8 preguntas) ─────────
    # Mapea a: PEI campaign_finance, media_coverage / V-Dem v2mebias

    q("S5_Q1", "Campaña y Financiamiento Electoral", "Financiamiento de Campaña", 5,
      "¿Los partidos políticos reportaron el financiamiento de campaña de forma transparente y completa ante el JNE?",
      SCALE_LIKERT5, "campaign_finance", "PEI v10.0 — CAMPAIGNFINANCE",
      "UNCAC Arts. 7, 12, 13; CADH Art. 23",
      None),

    q("S5_Q2", "Campaña y Financiamiento Electoral", "Financiamiento de Campaña", 5,
      "¿Hubo evidencia de uso indebido de recursos estatales (publicidad estatal, infraestructura, funcionarios) para favorecer al candidato oficialista?",
      SCALE_PRESENCE, "campaign_finance", "PEI v10.0 — CAMPAIGNFINANCE",
      "UNCAC Art. 7; ICCPR Art. 25; CDI Art. 3",
      "Incluir: inauguraciones de obras, entrega de bonos, actos de gobierno con apariencia de campaña."),

    q("S5_Q3", "Campaña y Financiamiento Electoral", "Financiamiento de Campaña", 5,
      "¿Las donaciones corporativas a campañas estuvieron debidamente registradas y dentro de los límites legales?",
      SCALE_LIKERT5, "campaign_finance", "PEI v10.0 — CAMPAIGNFINANCE",
      "UNCAC Arts. 7, 12",
      None),

    q("S5_Q4", "Campaña y Financiamiento Electoral", "Financiamiento de Campaña", 5,
      "¿Existió compra de votos, clientelismo o distribución de dádivas durante la campaña?",
      SCALE_PRESENCE, "campaign_finance", "PEI v10.0 — CAMPAIGNFINANCE",
      "ICCPR Art. 25(b); UNCAC Art. 7; CADH Art. 23",
      "Incluir: entrega de productos, dinero, servicios condicionados al voto."),

    q("S5_Q5", "Campaña y Financiamiento Electoral", "Financiamiento de Campaña", 5,
      "¿El JNE fiscalizó efectivamente el financiamiento de campaña durante el período observado?",
      SCALE_LIKERT5, "campaign_finance", "PEI v10.0 — CAMPAIGNFINANCE",
      "UNCAC Arts. 7, 13",
      None),

    q("S5_Q6", "Campaña y Financiamiento Electoral", "Medios y Campaña", 4,
      "¿Se respetó la veda electoral (silencio electoral) en las 48h previas a la votación?",
      SCALE_LIKERT5, "electoral_democracy", "V-Dem v2x_polyarchy",
      "LOE Art. 191; ICCPR Art. 25",
      "Verificar: actos de campaña encubiertos, publicidad en espacios públicos, cobertura mediática sesgada."),

    q("S5_Q7", "Campaña y Financiamiento Electoral", "Medios y Campaña", 4,
      "¿Hubo intimidación, amenazas o violencia dirigida a candidatos, activistas o sus familias durante la campaña?",
      SCALE_PRESENCE, "electoral_intimidation", "V-Dem v2elintim",
      "ICCPR Arts. 9, 25; CADH Arts. 5, 23",
      None),

    q("S5_Q8", "Campaña y Financiamiento Electoral", "Medios y Campaña", 4,
      "¿Los actos de campaña se desarrollaron en un ambiente de seguridad física adecuado para candidatos y votantes?",
      SCALE_LIKERT5, "electoral_intimidation", "V-Dem v2elintim",
      "ICCPR Arts. 9, 25",
      None),

    # ─── SECCIÓN 6: LIBERTAD DE PRENSA Y MEDIOS (7 preguntas) ────────────────
    # Mapea a: V-Dem v2mebias, v2meharjrn, v2mecenefi / RSF 2025

    q("S6_Q1", "Libertad de Prensa y Medios", "Libertad de Prensa", 4,
      "¿Los medios de comunicación nacionales dieron cobertura equitativa y proporcional a los distintos candidatos y partidos?",
      SCALE_LIKERT5, "media_bias_vdem", "V-Dem v2mebias + PEI MEDIACOVERAGE",
      "ICCPR Art. 19(2); CADH Art. 13; ICCPR Art. 25",
      "PEI 2021 Perú: MEDIACOVERAGE=40/100 — umbral de referencia histórico."),

    q("S6_Q2", "Libertad de Prensa y Medios", "Libertad de Prensa", 4,
      "¿Los periodistas que cubrieron el proceso electoral pudieron trabajar sin acoso, amenazas o restricciones?",
      SCALE_LIKERT5, "journalist_harassment", "V-Dem v2meharjrn",
      "ICCPR Art. 19; CADH Art. 13",
      "RSF Perú 2025: score 42.88/100, rank #130 — contexto de referencia."),

    q("S6_Q3", "Libertad de Prensa y Medios", "Libertad de Prensa", 4,
      "¿Existió presión del gobierno sobre medios de comunicación para influir en la cobertura electoral?",
      SCALE_PRESENCE, "media_bias_vdem", "V-Dem v2mebias",
      "ICCPR Art. 19; CADH Art. 13",
      "Incluir: presiones publicitarias, licencias, procesos judiciales instrumentalizados."),

    q("S6_Q4", "Libertad de Prensa y Medios", "Libertad de Prensa", 4,
      "¿Las redes sociales y medios digitales operaron sin restricciones o bloqueos durante el proceso electoral?",
      SCALE_LIKERT5, "internet_censorship", "V-Dem v2mecenefi + OONI",
      "ICCPR Art. 19(2); CADH Art. 13",
      "Verificar con OONI Explorer: ooni.org/es/country/PE"),

    q("S6_Q5", "Libertad de Prensa y Medios", "Libertad de Prensa", 4,
      "¿Hubo campañas de desinformación electoral masiva en medios digitales o redes sociales?",
      SCALE_PRESENCE, "internet_censorship", "V-Dem v2mecenefi + OONI",
      "ICCPR Art. 19(2), 20; CADH Art. 13",
      "Incluir: noticias falsas viralizadas sobre candidatos, el proceso o los resultados."),

    q("S6_Q6", "Libertad de Prensa y Medios", "Libertad de Prensa", 4,
      "¿Los medios estatales (TV Perú, Radio Nacional) mantuvieron imparcialidad en la cobertura electoral?",
      SCALE_LIKERT5, "media_bias_vdem", "V-Dem v2mebias",
      "ICCPR Art. 19; CADH Art. 13",
      None),

    q("S6_Q7", "Libertad de Prensa y Medios", "Libertad de Prensa", 4,
      "¿Hubo acceso plural a debates electorales televisivos para todos los candidatos con representación significativa?",
      SCALE_LIKERT5, "media_bias_vdem", "PEI MEDIACOVERAGE",
      "ICCPR Art. 19, 25; CADH Art. 13",
      None),

    # ─── SECCIÓN 7: JORNADA ELECTORAL (10 preguntas) ─────────────────────────
    # Mapea a: PEI voting_process / V-Dem v2elirreg, v2elintim

    q("S7_Q1", "Jornada Electoral", "Sufragio Universal", 1,
      "¿La apertura de los centros de votación fue oportuna (entre 07:00–08:00) y con todos los materiales disponibles?",
      SCALE_LIKERT5, "voting_process", "PEI v10.0 — VOTINGPROCESS",
      "ICCPR Art. 25(b)",
      "Estándar: ≥90% de mesas instaladas antes de las 08:00."),

    q("S7_Q2", "Jornada Electoral", "Sufragio Universal", 1,
      "¿Los miembros de mesa fueron capacitados suficientemente y cumplieron sus funciones de forma correcta?",
      SCALE_LIKERT5, "voting_process", "PEI v10.0 — VOTINGPROCESS",
      "ICCPR Art. 25(b)",
      None),

    q("S7_Q3", "Jornada Electoral", "Sufragio Universal", 1,
      "¿El voto fue secreto y se garantizó la privacidad en todos los centros observados?",
      SCALE_LIKERT5, "voting_process", "PEI v10.0 — VOTINGPROCESS",
      "ICCPR Art. 25(b)",
      "Verificar: biombos, disposición de mesas, conducta de miembros de mesa."),

    q("S7_Q4", "Jornada Electoral", "Sufragio Universal", 1,
      "¿Hubo irregularidades materiales en la jornada: boletas faltantes, actas pre-llenadas, urnas manipuladas?",
      SCALE_PRESENCE, "electoral_irregularities", "V-Dem v2elirreg",
      "ICCPR Art. 25(b); CADH Art. 23(1)(b)",
      None),

    q("S7_Q5", "Jornada Electoral", "Sufragio Universal", 1,
      "¿Los fiscales de partido y observadores nacionales/internacionales tuvieron acceso efectivo a todos los centros?",
      SCALE_LIKERT5, "voting_process", "PEI v10.0 — VOTINGPROCESS",
      "ICCPR Art. 25; CDI Art. 24",
      None),

    q("S7_Q6", "Jornada Electoral", "Sufragio Universal", 1,
      "¿Hubo presencia de personas no autorizadas dentro de los centros de votación (militares, autoridades locales, fiscalizadores informales)?",
      SCALE_PRESENCE, "electoral_intimidation", "V-Dem v2elintim",
      "ICCPR Art. 25(b); CADH Art. 23",
      None),

    q("S7_Q7", "Jornada Electoral", "Sufragio Universal", 1,
      "¿El cierre de centros de votación fue oportuno y ordenado, respetando el derecho de quienes ya estaban en fila?",
      SCALE_LIKERT5, "voting_process", "PEI v10.0 — VOTINGPROCESS",
      "ICCPR Art. 25(b)",
      None),

    q("S7_Q8", "Jornada Electoral", "Sufragio Universal", 1,
      "¿Los materiales electorales (actas, papeletas, sellos) estuvieron en condiciones adecuadas y sin signos de adulteración?",
      SCALE_LIKERT5, "voting_process", "PEI v10.0 — VOTINGPROCESS",
      "ICCPR Art. 25(b); CDI Art. 6",
      None),

    q("S7_Q9", "Jornada Electoral", "Sufragio Universal", 1,
      "¿Hubo incidentes de violencia, intimidación o perturbación del orden en los centros de votación observados?",
      SCALE_PRESENCE, "electoral_intimidation", "V-Dem v2elintim",
      "ICCPR Arts. 9, 25; CADH Art. 5",
      None),

    q("S7_Q10", "Jornada Electoral", "Sufragio Universal", 1,
      "¿La participación electoral (tasa de votación) reflejó condiciones de acceso normal al proceso?",
      SCALE_LIKERT5, "universal_suffrage", "V-Dem v2x_suffr",
      "ICCPR Art. 25(b)",
      "Comparar con participación en elecciones anteriores (2021: 74%). Desviaciones >10pp merecen análisis."),

    # ─── SECCIÓN 8: ESCRUTINIO Y TRANSMISIÓN DE RESULTADOS (6 preguntas) ─────
    # Mapea a: PEI vote_count, voting_results

    q("S8_Q1", "Escrutinio y Transmisión de Resultados", "Resolución de Disputas", 7,
      "¿El escrutinio en mesa fue realizado con presencia de fiscales de todos los partidos?",
      SCALE_LIKERT5, "vote_count", "PEI v10.0 — VOTECOUNT",
      "ICCPR Art. 25(b); CDI Art. 6",
      None),

    q("S8_Q2", "Escrutinio y Transmisión de Resultados", "Resolución de Disputas", 7,
      "¿Las actas de escrutinio fueron firmadas por los miembros de mesa y entregadas a los fiscales presentes?",
      SCALE_LIKERT5, "vote_count", "PEI v10.0 — VOTECOUNT",
      "ICCPR Art. 25(b); CADH Art. 23(1)(b)",
      None),

    q("S8_Q3", "Escrutinio y Transmisión de Resultados", "Resolución de Disputas", 7,
      "¿La transmisión de resultados (ACTA) por parte de la ONPE fue oportuna, transparente y verificable?",
      SCALE_LIKERT5, "voting_results", "PEI v10.0 — VOTINGRESULTS",
      "ICCPR Art. 25(b); CDI Art. 6",
      "PEI 2021: VOTINGRESULTS=46/100 — umbral histórico de referencia."),

    q("S8_Q4", "Escrutinio y Transmisión de Resultados", "Resolución de Disputas", 7,
      "¿Hubo discrepancias significativas entre los resultados del ACTA y las actas físicas observadas?",
      SCALE_PRESENCE, "electoral_irregularities", "V-Dem v2elirreg",
      "ICCPR Art. 25(b); CDI Art. 6",
      None),

    q("S8_Q5", "Escrutinio y Transmisión de Resultados", "Resolución de Disputas", 7,
      "¿Los resultados preliminares (ONPE al 100%) coincidieron con los resultados oficiales del JNE sin alteraciones?",
      SCALE_LIKERT5, "voting_results", "PEI v10.0 — VOTINGRESULTS",
      "ICCPR Art. 25(b); CDI Art. 6",
      None),

    q("S8_Q6", "Escrutinio y Transmisión de Resultados", "Resolución de Disputas", 7,
      "¿Los partidos y candidatos aceptaron los resultados electorales o impugnaron por vías legales establecidas?",
      SCALE_LIKERT5, "voting_results", "PEI v10.0 — VOTINGRESULTS",
      "ICCPR Art. 25(b); CADH Art. 8",
      "Distinguir: impugnación legítima vs. rechazo global sin fundamento."),

    # ─── SECCIÓN 9: JUSTICIA ELECTORAL Y POST-ELECTORAL (5 preguntas) ────────
    # Mapea a: V-Dem v2jureview / PEI voting_results

    q("S9_Q1", "Justicia Electoral", "Resolución de Disputas", 7,
      "¿El sistema de justicia electoral (JNE en segunda instancia) ofreció recursos efectivos para impugnar irregularidades?",
      SCALE_LIKERT5, "judicial_review", "V-Dem v2jureview",
      "ICCPR Art. 14; CADH Art. 8, 25",
      None),

    q("S9_Q2", "Justicia Electoral", "Resolución de Disputas", 7,
      "¿Las resoluciones del JNE sobre impugnaciones fueron motivadas, oportunas e independientes de presiones políticas?",
      SCALE_LIKERT5, "judicial_review", "V-Dem v2jureview",
      "ICCPR Art. 14; CADH Art. 8",
      None),

    q("S9_Q3", "Justicia Electoral", "Resolución de Disputas", 7,
      "¿Se garantizó el acceso equitativo a la justicia electoral para partidos y candidatos sin recursos económicos suficientes?",
      SCALE_LIKERT5, "judicial_review", "V-Dem v2jureview",
      "ICCPR Art. 14; CADH Art. 8",
      None),

    q("S9_Q4", "Justicia Electoral", "Resolución de Disputas", 7,
      "¿Hubo presiones del ejecutivo, legislativo u otros actores para influir en las resoluciones del JNE post-elección?",
      SCALE_PRESENCE, "judicial_review", "V-Dem v2jureview",
      "ICCPR Art. 14; CADH Art. 8; CDI Art. 4",
      None),

    q("S9_Q5", "Justicia Electoral", "Resolución de Disputas", 7,
      "¿El proceso de proclamación del candidato ganador se realizó en plazos razonables y con debido proceso?",
      SCALE_LIKERT5, "election_authorities", "PEI v10.0 — ELECTIONAUTHORITIES",
      "ICCPR Art. 25; CADH Art. 23",
      None),

    # ─── SECCIÓN 10: EVALUACIÓN GLOBAL — 8 DIMENSIONES IRE (8 preguntas) ─────
    # Evaluación sintética directa de cada dimensión del IRE

    q("S10_Q1", "Evaluación Global IRE", "Sufragio Universal", 1,
      "DIMENSIÓN IRE 1 — SUFRAGIO: ¿El derecho al sufragio universal fue garantizado en la práctica para el conjunto de la población electoral?",
      SCALE_LIKERT5, "universal_suffrage",
      "FH Political Rights + V-Dem v2x_suffr",
      "ICCPR Art. 25(b); CADH Art. 23(1)(b)",
      "Síntesis de tu evaluación sobre toda la Sección 3 (Padrón) + Sección 7 (Jornada)."),

    q("S10_Q2", "Evaluación Global IRE", "Marco Legal", 2,
      "DIMENSIÓN IRE 2 — MARCO LEGAL: ¿El marco legal electoral garantizó condiciones de competencia libre, justa y no discriminatoria?",
      SCALE_LIKERT5, "electoral_democracy",
      "V-Dem v2x_polyarchy + PEI LAWS",
      "ICCPR Art. 25; CADH Art. 23(2)",
      "Síntesis de tu evaluación de Sección 2 (Marco Legal)."),

    q("S10_Q3", "Evaluación Global IRE", "Independencia del OGE", 3,
      "DIMENSIÓN IRE 3 — OGE: ¿Los organismos electorales (JNE, ONPE, RENIEC) actuaron con independencia, capacidad y neutralidad suficientes?",
      SCALE_LIKERT5, "emb_autonomy",
      "V-Dem v2elembaut + v2elembcap + PEI EMBs",
      "ICCPR Art. 25; CDI Arts. 4, 5",
      "Síntesis de tu evaluación de Sección 1 (OGE)."),

    q("S10_Q4", "Evaluación Global IRE", "Libertad de Prensa", 4,
      "DIMENSIÓN IRE 4 — MEDIOS: ¿El ecosistema mediático garantizó acceso equitativo, libertad de prensa y ausencia de sesgo sistemático?",
      SCALE_LIKERT5, "media_bias_vdem",
      "V-Dem v2mebias + RSF 2025 + PEI MEDIACOVERAGE",
      "ICCPR Art. 19(2); CADH Art. 13; ICCPR Art. 25",
      "RSF Perú 2025: 42.88/100 (rank #130). PEI 2021: 40/100."),

    q("S10_Q5", "Evaluación Global IRE", "Financiamiento de Campaña", 5,
      "DIMENSIÓN IRE 5 — FINANCIAMIENTO: ¿El financiamiento de campaña fue transparente, equitativo y libre de corrupción?",
      SCALE_LIKERT5, "campaign_finance",
      "PEI CAMPAIGNFINANCE",
      "UNCAC Arts. 7, 12; ICCPR Art. 25; CDI Art. 3",
      "PEI 2021 Perú: CAMPAIGNFINANCE=50/100."),

    q("S10_Q6", "Evaluación Global IRE", "Ecosistema Digital", 6,
      "DIMENSIÓN IRE 6 — DIGITAL: ¿El ecosistema digital operó sin censura, con información veraz y sin manipulación masiva?",
      SCALE_LIKERT5, "internet_censorship",
      "V-Dem v2mecenefi + OONI API",
      "ICCPR Art. 19(2); CADH Art. 13; ICCPR Art. 25",
      "Verificar: ooni.org/es/country/PE para bloqueos web detectados."),

    q("S10_Q7", "Evaluación Global IRE", "Resolución de Disputas", 7,
      "DIMENSIÓN IRE 7 — JUSTICIA: ¿El sistema de justicia electoral ofreció recursos efectivos, independientes y accesibles?",
      SCALE_LIKERT5, "judicial_review",
      "V-Dem v2jureview + PEI VOTINGRESULTS",
      "ICCPR Art. 14; CADH Arts. 8, 25",
      "Síntesis de tu evaluación de Sección 9 (Justicia Electoral)."),

    q("S10_Q8", "Evaluación Global IRE", "Inclusión Electoral", 8,
      "DIMENSIÓN IRE 8 — INCLUSIÓN: ¿El proceso garantizó participación sin discriminación por género, etnia, discapacidad, ubicación geográfica o condición económica?",
      SCALE_LIKERT5, "universal_suffrage",
      "FH Civil Liberties + V-Dem v2x_suffr + CRPD + CEDAW",
      "ICCPR Arts. 25, 26; CEDAW Art. 7; CRPD Art. 29; ICERD Art. 5(c)",
      "Síntesis de tu evaluación de Sección 4 (Inclusividad)."),
]


# ─── Secciones del cuestionario ───────────────────────────────────────────────
SECTIONS = [
    {"id": 1, "key": "S1", "title": "OGE y Administración Electoral",     "questions": 8,  "ire_dim": 3},
    {"id": 2, "key": "S2", "title": "Marco Legal Electoral",               "questions": 7,  "ire_dim": 2},
    {"id": 3, "key": "S3", "title": "Padrón y Registro Electoral",         "questions": 6,  "ire_dim": 1},
    {"id": 4, "key": "S4", "title": "Inclusividad y Derechos Diferenciales","questions": 6, "ire_dim": 8},
    {"id": 5, "key": "S5", "title": "Campaña y Financiamiento Electoral",  "questions": 8,  "ire_dim": 5},
    {"id": 6, "key": "S6", "title": "Libertad de Prensa y Medios",         "questions": 7,  "ire_dim": 4},
    {"id": 7, "key": "S7", "title": "Jornada Electoral",                   "questions": 10, "ire_dim": 1},
    {"id": 8, "key": "S8", "title": "Escrutinio y Transmisión de Resultados","questions": 6,"ire_dim": 7},
    {"id": 9, "key": "S9", "title": "Justicia Electoral",                  "questions": 5,  "ire_dim": 7},
    {"id": 10,"key": "S10","title": "Evaluación Global — 8 Dimensiones IRE","questions": 8, "ire_dim": None},
]

TOTAL_QUESTIONS = len(QUESTIONNAIRE)  # 71 preguntas


# ─── Mapeo: variable de dataset → score normalizado de la plataforma ─────────
PLATFORM_SCORE_MAP = {
    # V-Dem (0-1 → *100)
    "emb_autonomy":             ("vdem", "emb_autonomy",             100),
    "emb_capacity":             ("vdem", "emb_capacity",             100),
    "electoral_democracy":      ("vdem", "electoral_democracy",      100),
    "rule_of_law":              ("vdem", "rule_of_law",              100),
    "universal_suffrage":       ("vdem", "universal_suffrage",       100),
    "free_fair_elections":      ("vdem", "free_fair_elections",      100),
    "freedom_of_expression":    ("vdem", "freedom_of_expression",    100),
    "electoral_irregularities": ("vdem", "electoral_irregularities", 100),
    "electoral_intimidation":   ("vdem", "electoral_intimidation",   100),
    "internet_censorship":      ("vdem", "internet_censorship",      100),
    "journalist_harassment":    ("vdem", "journalist_harassment",    100),
    "media_bias_vdem":          ("vdem", "media_bias_vdem",          100),
    "opposition_autonomy":      ("vdem", "opposition_autonomy",      100),
    "opposition_party_barriers":("vdem", "opposition_party_barriers",100),
    "judicial_review":          ("vdem", "judicial_review",          100),
    # PEI (0-100, ya está en escala 100)
    "legal_framework":          ("pei",  "legal_framework",          1),
    "procedures":               ("pei",  "procedures",               1),
    "voter_registration":       ("pei",  "voter_registration",       1),
    "media_coverage":           ("pei",  "media_coverage",           1),
    "campaign_finance":         ("pei",  "campaign_finance",         1),
    "voting_process":           ("pei",  "voting_process",           1),
    "vote_count":               ("pei",  "vote_count",               1),
    "voting_results":           ("pei",  "voting_results",           1),
    "election_authorities":     ("pei",  "election_authorities",     1),
    "emb_score":                ("pei",  "emb_score",                1),
}


def build_questionnaire_with_platform_scores(vdem_data: dict, pei_data: dict,
                                              fh_data: dict, rsf_data: dict) -> list:
    """
    Genera el cuestionario con los scores de la plataforma pre-cargados.
    vdem_data: dict de get_vdem_country()
    pei_data: dict de get_pei_country()
    fh_data: dict de get_freedom_house_country()
    rsf_data: dict de get_rsf_country()
    """
    import copy
    qs = copy.deepcopy(QUESTIONNAIRE)

    for q_item in qs:
        var = q_item["dataset_var"]
        # Buscar en PLATFORM_SCORE_MAP
        if var in PLATFORM_SCORE_MAP:
            source, key, multiplier = PLATFORM_SCORE_MAP[var]
            raw = None
            if source == "vdem" and vdem_data:
                raw = vdem_data.get(key)
            elif source == "pei" and pei_data:
                raw = pei_data.get(key)
            if raw is not None:
                try:
                    q_item["platform_score"] = round(float(raw) * multiplier, 1)
                except (TypeError, ValueError):
                    pass

        # Completar FH y RSF para preguntas específicas
        if var == "universal_suffrage" and fh_data:
            q_item["platform_fh_note"] = f"FH Political Rights: {fh_data.get('political_rights_rating', '—')}/7"
        if "rsf" in var.lower() and rsf_data:
            q_item["platform_rsf_note"] = f"RSF 2025: {rsf_data.get('score', '—')}/100 (rank #{rsf_data.get('rank', '—')})"

    return qs


def compute_comparison(answers: dict, questionnaire_with_scores: list) -> dict:
    """
    Compara respuestas del observador con scores de la plataforma.

    answers: {question_id: observer_value (0-5)}
    Returns: dict con convergencia por sección y global.
    """
    results = []
    section_results = {}

    for q_item in questionnaire_with_scores:
        qid = q_item["id"]
        obs_raw = answers.get(qid)
        plat_raw = q_item.get("platform_score")

        if obs_raw is None or obs_raw == 0:  # Sin información
            continue
        if plat_raw is None:
            continue

        # Convertir observer answer (1-5) a escala 0-100
        obs_100 = (obs_raw / 5) * 100
        plat_100 = plat_raw  # ya en 0-100

        diff = abs(obs_100 - plat_100)
        convergence = max(0, 100 - diff)

        result = {
            "id": qid,
            "section": q_item["section"],
            "ire_dimension": q_item["ire_dimension"],
            "text_short": q_item["text"][:80],
            "observer_score_raw": obs_raw,
            "observer_score_100": round(obs_100, 1),
            "platform_score_100": round(plat_100, 1),
            "difference": round(diff, 1),
            "convergence_pct": round(convergence, 1),
            "convergence_label": (
                "✅ Alta convergencia" if convergence >= 75
                else "🟡 Convergencia moderada" if convergence >= 50
                else "🔴 Divergencia significativa"
            ),
            "dataset_var": q_item["dataset_var"],
            "dataset_source": q_item["dataset_source"],
            "iccpr_ref": q_item["iccpr_ref"],
        }
        results.append(result)

        sec = q_item["section"]
        if sec not in section_results:
            section_results[sec] = {"diffs": [], "obs_scores": [], "plat_scores": []}
        section_results[sec]["diffs"].append(diff)
        section_results[sec]["obs_scores"].append(obs_100)
        section_results[sec]["plat_scores"].append(plat_100)

    # Resumen por sección
    section_summary = {}
    for sec, data in section_results.items():
        if data["diffs"]:
            avg_diff = sum(data["diffs"]) / len(data["diffs"])
            section_summary[sec] = {
                "avg_observer_score": round(sum(data["obs_scores"]) / len(data["obs_scores"]), 1),
                "avg_platform_score": round(sum(data["plat_scores"]) / len(data["plat_scores"]), 1),
                "avg_difference": round(avg_diff, 1),
                "convergence_pct": round(max(0, 100 - avg_diff), 1),
                "questions_answered": len(data["diffs"]),
            }

    # Resumen global
    all_diffs = [r["difference"] for r in results]
    global_convergence = round(max(0, 100 - sum(all_diffs) / len(all_diffs)), 1) if all_diffs else None

    return {
        "questions_answered": len(results),
        "global_convergence_pct": global_convergence,
        "global_convergence_label": (
            "✅ Alta convergencia: plataforma y observador coinciden"
            if global_convergence is not None and global_convergence >= 75
            else "🟡 Convergencia moderada: divergencias parciales"
            if global_convergence is not None and global_convergence >= 50
            else "🔴 Divergencia significativa: requiere análisis"
        ),
        "section_summary": section_summary,
        "question_results": sorted(results, key=lambda x: x["difference"], reverse=True),
        "top_divergences": [r for r in results if r["convergence_pct"] < 50][:10],
        "top_convergences": [r for r in results if r["convergence_pct"] >= 80][:10],
    }
