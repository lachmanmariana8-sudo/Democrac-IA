"""Post-procesamiento de títulos de subsecciones (## N.M ...).

Los prompts cap_NN.md fijan los títulos en español ("## 5.1 Cronología del día").
El LLM, aun con LANGUAGE_RULE=en, los copia verbatim porque vienen como
parte de la instrucción/estructura. Hasta que se traduzcan los prompts
(Sprint 4), este módulo intercepta el markdown y reemplaza la línea
`## N.M <texto>` por la versión en el idioma pedido.

El reemplazo es por número de subsección (e.g. "5.1"), no por el texto
en sí — eso lo hace robusto a variaciones tipográficas que el LLM pueda
introducir.
"""
from __future__ import annotations

import re
from typing import Dict


# {section_id: {language: title}}. Listas extraídas de cap_NN.md (es) y
# traducidas a en/pt manualmente con cuidado terminológico.
SECTION_TITLES: Dict[str, Dict[str, str]] = {
    # Cap 1 — Contexto histórico
    "1.1": {"es": "Trayectoria democrática 2015–2025",
            "en": "Democratic trajectory 2015–2025",
            "pt": "Trajetória democrática 2015–2025"},
    "1.2": {"es": "Índices complementarios",
            "en": "Complementary indices",
            "pt": "Índices complementares"},
    "1.3": {"es": "Eventos institucionales críticos del último ciclo",
            "en": "Critical institutional events of the latest cycle",
            "pt": "Eventos institucionais críticos do último ciclo"},
    # Cap 2 — Marco jurídico
    "2.1": {"es": "Marco constitucional",
            "en": "Constitutional framework",
            "pt": "Marco constitucional"},
    "2.2": {"es": "Marco legal — normativa específica",
            "en": "Legal framework — specific regulations",
            "pt": "Marco legal — normativa específica"},
    "2.3": {"es": "Jurisprudencia electoral relevante",
            "en": "Relevant electoral jurisprudence",
            "pt": "Jurisprudência eleitoral relevante"},
    "2.4": {"es": "Marco internacional aplicable",
            "en": "Applicable international framework",
            "pt": "Marco internacional aplicável"},
    # Cap 3 — Sistema electoral
    "3.1": {"es": "Arquitectura institucional",
            "en": "Institutional architecture",
            "pt": "Arquitetura institucional"},
    "3.2": {"es": "Procedimientos electorales",
            "en": "Electoral procedures",
            "pt": "Procedimentos eleitorais"},
    "3.3": {"es": "Tecnología electoral del ciclo",
            "en": "Electoral technology of the cycle",
            "pt": "Tecnologia eleitoral do ciclo"},
    "3.4": {"es": "Cadena de custodia del voto",
            "en": "Vote chain of custody",
            "pt": "Cadeia de custódia do voto"},
    # Cap 4 — Pre-electoral
    "4.1": {"es": "Panorama general de las 4 fases previas",
            "en": "Overview of the 4 preceding phases",
            "pt": "Panorama geral das 4 fases anteriores"},
    "4.2": {"es": "Ecosistema informativo y desinformación",
            "en": "Information ecosystem and disinformation",
            "pt": "Ecossistema informativo e desinformação"},
    "4.3": {"es": "Campaña electoral",
            "en": "Electoral campaign",
            "pt": "Campanha eleitoral"},
    "4.4": {"es": "Silencio electoral y observancia normativa",
            "en": "Campaign silence period and regulatory compliance",
            "pt": "Silêncio eleitoral e observância normativa"},
    # Cap 5 — Jornada electoral
    "5.1": {"es": "Cronología del día",
            "en": "Day's chronology",
            "pt": "Cronologia do dia"},
    "5.2": {"es": "Operativa de ONPE y cumplimiento logístico",
            "en": "ONPE operations and logistical compliance",
            "pt": "Operação da ONPE e cumprimento logístico"},
    "5.3": {"es": "Exclusión del sufragio documentada",
            "en": "Documented suffrage exclusion",
            "pt": "Exclusão do sufrágio documentada"},
    "5.4": {"es": "Observación y transparencia",
            "en": "Observation and transparency",
            "pt": "Observação e transparência"},
    "5.5": {"es": "Incidentes de integridad en mesa",
            "en": "Polling-station integrity incidents",
            "pt": "Incidentes de integridade em mesa"},
    # Cap 6 — Escrutinio y cómputo
    "6.1": {"es": "Escrutinio en mesa",
            "en": "Polling-station tally",
            "pt": "Apuração em mesa"},
    "6.2": {"es": "Actas observadas",
            "en": "Contested tally sheets",
            "pt": "Atas observadas"},
    "6.3": {"es": "Digitalización y transmisión",
            "en": "Digitisation and transmission",
            "pt": "Digitalização e transmissão"},
    "6.4": {"es": "Validación IA-operador (SCE)",
            "en": "AI-operator validation (SCE)",
            "pt": "Validação IA-operador (SCE)"},
    "6.5": {"es": "Ritmo del cómputo oficial",
            "en": "Pace of the official count",
            "pt": "Ritmo da apuração oficial"},
    # Cap 7 — Post-electoral
    "7.1": {"es": "Ritmo de proclamación y resultados oficiales",
            "en": "Proclamation pace and official results",
            "pt": "Ritmo de proclamação e resultados oficiais"},
    "7.2": {"es": "Acciones penales e institucionales contra autoridades",
            "en": "Criminal and institutional actions against authorities",
            "pt": "Ações penais e institucionais contra autoridades"},
    "7.3": {"es": "Narrativa de fraude y pedidos de nulidad",
            "en": "Fraud narrative and nullity petitions",
            "pt": "Narrativa de fraude e pedidos de nulidade"},
    "7.4": {"es": "Rol de actores externos al sistema electoral",
            "en": "Role of external actors to the electoral system",
            "pt": "Papel de atores externos ao sistema eleitoral"},
    "7.5": {"es": "Red de actores institucionales",
            "en": "Network of institutional actors",
            "pt": "Rede de atores institucionais"},
    # Cap 8 — Derechos vulnerados
    "8.1": {"es": "Marco de derechos vulnerados — enumeración",
            "en": "Framework of breached rights — enumeration",
            "pt": "Marco de direitos violados — enumeração"},
    "8.2": {"es": "Matriz analítica: categoría × derecho",
            "en": "Analytical matrix: category × right",
            "pt": "Matriz analítica: categoria × direito"},
    "8.3": {"es": "Cumplimiento del Estado con obligaciones internacionales",
            "en": "State compliance with international obligations",
            "pt": "Cumprimento do Estado com obrigações internacionais"},
    "8.4": {"es": "Activación potencial de mecanismos internacionales",
            "en": "Potential activation of international mechanisms",
            "pt": "Ativação potencial de mecanismos internacionais"},
    # Cap 9 — Análisis predictivo
    "9.1": {"es": "Metodología del análisis predictivo",
            "en": "Predictive-analysis methodology",
            "pt": "Metodologia da análise preditiva"},
    "9.2": {"es": "Patrón dominante identificado",
            "en": "Identified dominant pattern",
            "pt": "Padrão dominante identificado"},
    "9.3": {"es": "Escenarios probabilísticos",
            "en": "Probabilistic scenarios",
            "pt": "Cenários probabilísticos"},
    "9.4": {"es": "Nivel de alerta temprana",
            "en": "Early-warning level",
            "pt": "Nível de alerta antecipada"},
    # Cap 10 — Conclusiones
    "10.1": {"es": "Síntesis del proceso",
             "en": "Process synthesis",
             "pt": "Síntese do processo"},
    "10.2": {"es": "Evaluación por dimensiones PEIRS",
             "en": "Assessment by PEIRS dimensions",
             "pt": "Avaliação por dimensões PEIRS"},
    "10.3": {"es": "Evaluación de legitimidad del proceso",
             "en": "Process legitimacy assessment",
             "pt": "Avaliação de legitimidade do processo"},
    "10.4": {"es": "Comparación con compromisos internacionales",
             "en": "Comparison with international commitments",
             "pt": "Comparação com compromissos internacionais"},
    "10.5": {"es": "Juicio global",
             "en": "Overall judgement",
             "pt": "Julgamento global"},
    # Cap 11 — Recomendaciones
    "11.1": {"es": "Corto plazo (48 horas – 30 días)",
             "en": "Short term (48 hours – 30 days)",
             "pt": "Curto prazo (48 horas – 30 dias)"},
    "11.2": {"es": "Mediano plazo (1–6 meses)",
             "en": "Medium term (1–6 months)",
             "pt": "Médio prazo (1–6 meses)"},
    "11.3": {"es": "Largo plazo (6 meses – pre-próximas elecciones)",
             "en": "Long term (6 months – pre-next elections)",
             "pt": "Longo prazo (6 meses – pré-próximas eleições)"},
    "11.4": {"es": "Recomendaciones al sistema internacional",
             "en": "Recommendations to the international system",
             "pt": "Recomendações ao sistema internacional"},
    # Cap 12 — IA y regulación
    "12.1": {"es": "Arquitectura del sistema tecnológico desplegado",
             "en": "Architecture of the deployed technology system",
             "pt": "Arquitetura do sistema tecnológico implantado"},
    "12.2": {"es": "Incidentes documentados en el ciclo",
             "en": "Documented incidents in the cycle",
             "pt": "Incidentes documentados no ciclo"},
    "12.3": {"es": "El precedente regulatorio del VENP",
             "en": "The VENP regulatory precedent",
             "pt": "O precedente regulatório do VENP"},
    "12.4": {"es": "Marco regulatorio vigente — el vacío actual",
             "en": "Current regulatory framework — the existing gap",
             "pt": "Marco regulatório vigente — a lacuna atual"},
    "12.5": {"es": "Estándares internacionales emergentes como referencia",
             "en": "Emerging international standards as reference",
             "pt": "Padrões internacionais emergentes como referência"},
    "12.6": {"es": "Recomendación específica al Congreso",
             "en": "Specific recommendation to Congress",
             "pt": "Recomendação específica ao Congresso"},
}


_HEAD_RE = re.compile(r"^(##\s+)(\d+\.\d+)(\s+)(.*)$", re.MULTILINE)


def translate_section_titles(md: str, language: str) -> str:
    """Para cada línea ``## N.M <texto>`` del markdown, reemplaza ``<texto>``
    por la traducción correspondiente del SECTION_TITLES si existe la entrada
    para ``N.M`` y el idioma. Si la sección o el idioma no están en el dict,
    deja la línea intacta (fallback al output original del LLM).

    No-op si language=="es": los prompts ya están en español.
    """
    if not md:
        return md
    lang = (language or "es").lower()
    if lang == "es":
        return md

    def _repl(m: "re.Match[str]") -> str:
        prefix, num, sep, _orig = m.group(1), m.group(2), m.group(3), m.group(4)
        bundle = SECTION_TITLES.get(num)
        if not bundle:
            return m.group(0)
        new_title = bundle.get(lang)
        if not new_title:
            return m.group(0)
        return f"{prefix}{num}{sep}{new_title}"

    return _HEAD_RE.sub(_repl, md)
