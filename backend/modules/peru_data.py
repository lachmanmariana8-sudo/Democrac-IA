"""DEMOCRAC.IA / PEIRS — Datos especificos de Peru 2026"""

PERU_ELECTORAL_SYSTEM = {
    "name": "Representación Proporcional con Cifra Repartidora (D'Hondt)",
    "law": "Ley Orgánica de Elecciones N° 26859 y modificatorias",
    "seats": 130,
    "chamber": "Unicameral — Congreso de la República",
    "term_years": 5,
    "districts": 26,
    "district_note": "26 circunscripciones (25 regiones + Lima Metropolitana). Magnitude varía de 1 (Moquegua, Tacna, Madre de Dios) a 36 (Lima).",
    "threshold": "5% de votos válidos a nivel nacional O 7 escaños en al menos un distrito (Ley 31046)",
    "threshold_note": "El umbral doble reduce fragmentación pero en la práctica han sobrevivido 8+ bancadas en cada congreso desde 2011.",
    "formula": "Cifra Repartidora (Método D'Hondt) — favorece a partidos más grandes en distritos plurinominales",
    "ballot_type": "Lista cerrada y bloqueada con voto preferencial (hasta 2 preferencias)",
    "vote_preference_note": "El voto preferencial permite al elector reordenar candidatos dentro de la lista, lo que genera competencia intrapartidaria intensa.",
    "presidential_system": "Elección directa a 2 vueltas (ballotage)",
    "ballotage_threshold": "Mayoría absoluta (50%+1) en 1ª vuelta. Si nadie alcanza: 2ª vuelta entre los dos más votados.",
    "women_quota": "30% mínimo de mujeres en listas (Ley 31030, 2021)",
    "youth_quota": "20% de jóvenes (hasta 29 años) y comunidades nativas en listas",
    "simultaneity": "Elecciones presidenciales y congresales simultáneas (misma boleta, mismo día)",
    "prohibitions": "Condenados con sentencia firme no pueden postular. Funcionarios públicos deben renunciar 6 meses antes.",
    "key_bodies": {
        "JNE": "Jurado Nacional de Elecciones — árbitro electoral máximo, resuelve impugnaciones, proclama resultados",
        "ONPE": "Oficina Nacional de Procesos Electorales — organiza la votación, escrutinio, transmisión de resultados",
        "RENIEC": "Registro Nacional de Identificación — padrón electoral, DNI, biometría",
    },
    "historical_fragmentation": "Perú ha promediado 7-8 bancadas efectivas desde 2011. Ningún partido ha obtenido mayoría absoluta (66 escaños) desde Fuerza Popular en 2016.",
    "sources": [
        {"label": "JNE — Sistema Electoral Peruano", "url": "https://www.jne.gob.pe"},
        {"label": "ONPE — Elecciones 2026", "url": "https://www.onpe.gob.pe"},
        {"label": "Ley N° 26859 — Ley Orgánica de Elecciones", "url": "https://www.leyes.congreso.gob.pe"},
        {"label": "IDEA Internacional — Electoral System Design Database", "url": "https://www.idea.int/data-tools/country-view/247/40"},
    ],
}

PERU_POLITICAL_FORCES = [
    {
        "id": "app", "name": "Alianza para el Progreso", "abbr": "APP",
        "ideology": "Centro / Populismo pragmático", "position": 50,
        "founded": 1999, "color": "#f97316",
        "leader": "César Acuña Peralta",
        "background": (
            "Fundada en 1999 por César Acuña, empresario universitario de La Libertad. "
            "Su crecimiento se sustenta en la red de universidades privadas del Grupo UCV, "
            "con presencia en 18 regiones. Ha sido el partido con mayor número de candidatos "
            "electos en elecciones regionales y municipales 2022. Su modelo organizativo ha "
            "sido cuestionado como 'partido-empresa' por organismos como Transparencia Internacional Perú. "
            "Acuña fue inhabilitado en 2018 por el JNE por presuntas dádivas electorales, sanción "
            "posteriormente levantada, lo que generó controversia sobre la aplicabilidad efectiva del Art. 25 ICCPR."
        ),
        "candidates_2026": [
            {"name": "César Acuña Peralta", "role": "Candidato presidencial confirmado",
             "notes": "Cuarta candidatura presidencial. Gobernador electo de La Libertad 2022-2026. Postula con la figura de 'gestor' y candidato de centro."},
        ],
        "electoral_history": [
            {"year": 2016, "seats": 9,  "first_round_pct": None, "result": "Coalición menor. APP apoya a PPK en 2ª vuelta."},
            {"year": 2020, "seats": 22, "first_round_pct": None, "result": "Elecciones extraordinarias. Segundo partido más votado."},
            {"year": 2021, "seats": 22, "first_round_pct": 6.1,  "result": "4to lugar presidencial (Acuña). 22 escaños iniciales, sube a 28 por transfugismo."},
        ],
        "key_policies": [
            "Inversión en infraestructura educativa y universidades regionales",
            "Descentralización fiscal y fortalecimiento de gobiernos regionales",
            "Seguridad ciudadana con énfasis en penas más duras",
        ],
        "base_regions": ["La Libertad", "Cajamarca", "Lambayeque"],
        "current_seats": 28, "electoral_strength": "Alto", "risk_profile": "high",
        "risk_notes": "Red clientelar articulada en torno a universidades UCV. Financiamiento opaco. Acuña con inhabilitaciones previas.",
        "strengths": ["Infraestructura organizacional universitaria", "Presencia robusta en norte", "Financiamiento sólido"],
        "vulnerabilities": ["Denuncias de compra de votos", "Imagen de partido-empresa", "Dependencia del liderazgo personal"],
        "iccpr_risk": "Art. 25 ICCPR — posible afectación al sufragio libre mediante prácticas clientelares documentadas por la ONPE y JNE.",
        "iccpr_source": "JNE Res. 0234-2018-JNE; ONPE Informe de Financiamiento 2022; Transparencia Internacional Perú (2023)",
        "iccpr_date": "2018 (inhabilitación), 2022 (informe ONPE), actualizado ene 2026",
        "iccpr_url": "https://www.jne.gob.pe/transparencia/resoluciones/",
    },
    {
        "id": "fp", "name": "Fuerza Popular", "abbr": "FP",
        "ideology": "Derecha / Fujimorismo", "position": 72,
        "founded": 2010, "color": "#ef4444",
        "leader": "Keiko Fujimori",
        "background": (
            "Heredera del fujimorismo, movimiento nacido en torno al expresidente Alberto Fujimori (1990-2000). "
            "Keiko Fujimori ha liderado tres candidaturas presidenciales (2011, 2016, 2021), "
            "perdiendo las tres en segunda vuelta. En 2016 obtuvo 73 escaños (mayoría absoluta) "
            "y usó ese dominio para enfrentarse al ejecutivo de PPK, generando una crisis constitucional. "
            "Keiko fue detenida en 2018 y 2019 por presunto lavado de activos en el caso Odebrecht; "
            "tiene proceso abierto. El partido ha renovado parcialmente su cúpula pero mantiene "
            "el liderazgo personalista de la familia Fujimori."
        ),
        "candidates_2026": [
            {"name": "Keiko Fujimori", "role": "Candidata presidencial (4ª postulación)",
             "notes": "Mantiene liderazgo del partido. Proceso judicial por lavado de activos en curso. Base electoral fiel en Lima y regiones costeras."},
        ],
        "electoral_history": [
            {"year": 2016, "seats": 73, "first_round_pct": 39.9, "result": "Mayoría absoluta en congreso. Keiko pierde 2ª vuelta presidencial vs PPK por menos de 0.1%."},
            {"year": 2020, "seats": 15, "first_round_pct": None, "result": "Elecciones extraordinarias. Derrumbe electoral post-confrontación con Vizcarra."},
            {"year": 2021, "seats": 24, "first_round_pct": 13.4, "result": "13.4% en 1ª vuelta, 49.9% en 2ª vuelta. Impugna resultado ante el JNE sin éxito."},
        ],
        "key_policies": [
            "Mano dura contra la criminalidad e inseguridad",
            "Libre mercado y protección a la inversión privada",
            "Rechazo a la Asamblea Constituyente",
        ],
        "base_regions": ["Lima", "Ica", "Arequipa", "Ucayali"],
        "current_seats": 23, "electoral_strength": "Alto", "risk_profile": "high",
        "risk_notes": "Historia de 3 procesos electorales con denuncias de fraude. Keiko con condena suspendida. Control parcial de instituciones cuestionado.",
        "strengths": ["Base electoral leal en Lima", "Estructura partidaria consolidada", "Candidatos con experiencia legislativa"],
        "vulnerabilities": ["Imagen negativa por corrupción", "Dependencia del legado Fujimori", "Juicios pendientes"],
        "iccpr_risk": "Art. 14 ICCPR — garantías procesales comprometidas en relación al proceso penal activo del liderazgo.",
        "iccpr_source": "Poder Judicial del Perú — Expediente N° 00299-2017-36-5001-JR-PE-01; CIDH Informe Anual 2023",
        "iccpr_date": "2017 (inicio proceso), dic 2023 (última resolución de apelación), ene 2026 (estado activo)",
        "iccpr_url": "https://cej.pj.gob.pe/cej/forms/busquedaform.html",
    },
    {
        "id": "rp", "name": "Renovación Popular", "abbr": "RP",
        "ideology": "Derecha / Conservador-liberal", "position": 80,
        "founded": 2020, "color": "#0ea5e9",
        "leader": "Rafael López Aliaga",
        "background": (
            "Partido fundado en 2020 por Rafael López Aliaga, empresario de origen limeño. "
            "De perfil ultraconservador en lo social (declaradamente antiaborto, crítico de la ideología de género) "
            "y liberal en lo económico. Su primera candidatura presidencial en 2021 (12.8%) lo consolidó "
            "como líder de la derecha dura urbana. Fue elegido alcalde de Lima Metropolitana en 2022, "
            "cargo desde el cual ha impulsado una gestión confrontacional con el gobierno central. "
            "Su discurso polarizante y el uso del término 'castrocomunismo' para referirse a la izquierda "
            "ha sido documentado como factor de desinformación."
        ),
        "candidates_2026": [
            {"name": "Rafael López Aliaga", "role": "Candidato presidencial (2ª postulación)",
             "notes": "Alcalde de Lima hasta diciembre 2025. Perfil empresarial. Alta recordación en Lima pero baja fuera de la capital."},
        ],
        "electoral_history": [
            {"year": 2021, "seats": 9, "first_round_pct": 12.8, "result": "3er lugar presidencial. 9 escaños en congreso. Ingreso sorpresivo al escenario político."},
        ],
        "key_policies": [
            "Tolerancia cero al crimen: cárceles duras, pena de muerte para terrorismo",
            "Eliminación de impuestos a pequeñas empresas y reducción del Estado",
            "Rechazo a la agenda LGBT y políticas de género en educación",
        ],
        "base_regions": ["Lima", "Arequipa", "Moquegua"],
        "current_seats": 9, "electoral_strength": "Medio", "risk_profile": "moderate",
        "risk_notes": "Discurso polarizante. Cuestionamientos sobre financiamiento empresarial. Posiciones restrictivas sobre derechos civiles.",
        "strengths": ["Base urbana de clase media-alta", "Liderazgo mediático", "Posicionamiento anticorrupción"],
        "vulnerabilities": ["Escaso implante territorial fuera de Lima", "Discurso divisivo", "Partido personalista joven"],
        "iccpr_risk": "Art. 19, 21 ICCPR — restricciones retóricas a libertades civiles documentadas en campaña; potencial impacto en derechos de minorías.",
        "iccpr_source": "Freedom House FIW 2025 (pp. 14-15); IPYS Perú — Monitoreo de Discurso Político 2024-2025",
        "iccpr_date": "2024-2025 (campaña electoral, monitoreo IPYS)",
        "iccpr_url": "https://freedomhouse.org/country/peru/freedom-world/2025",
    },
    {
        "id": "pl", "name": "Perú Libre", "abbr": "PL",
        "ideology": "Izquierda / Marxismo-leninismo", "position": 15,
        "founded": 2009, "color": "#a855f7",
        "leader": "Vladimir Cerrón",
        "background": (
            "Fundado en 2009 en la región Junín por Vladimir Cerrón, médico y exgobernador regional. "
            "Fue el vehículo que llevó a Pedro Castillo a la presidencia en 2021 con apenas el 18.9% en primera vuelta. "
            "Cerrón fue condenado en 2019 por corrupción (3.5 años de prisión efectiva) e inhabilitado para cargos públicos, "
            "lo que generó una contradicción estructural: el fundador no pudo ser candidato del gobierno que él mismo impulsó. "
            "Castillo rompió con Cerrón en 2022. Tras la vacancia de Castillo, el partido se fragmentó y hoy opera "
            "con presencia marginal pero organizada en regiones andinas del centro-sur."
        ),
        "candidates_2026": [
            {"name": "Por definir", "role": "Candidato presidencial sin confirmar",
             "notes": "Cerrón inhabilitado. El partido buscará candidato de la región andina. Alta incertidumbre sobre su viabilidad para superar el umbral del 5%."},
        ],
        "electoral_history": [
            {"year": 2021, "seats": 37, "first_round_pct": 18.9, "result": "Castillo gana presidencia con 50.1% en 2ª vuelta. 37 escaños iniciales, se fragmenta a 7 por conflictos internos."},
        ],
        "key_policies": [
            "Asamblea Constituyente para nueva Constitución",
            "Nationalización de recursos naturales estratégicos",
            "Reforma agraria y redistribución de tierras",
        ],
        "base_regions": ["Junín", "Cusco", "Puno", "Ayacucho"],
        "current_seats": 7, "electoral_strength": "Medio", "risk_profile": "high",
        "risk_notes": "Cerrón condenado por corrupción e inhabilitado. Partido instrumento de Castillo (2021). Base en regiones andinas.",
        "strengths": ["Base en sierra central y sur", "Discurso redistributivo con arrastre popular"],
        "vulnerabilities": ["Liderazgo inhabilitado", "Asociación con gestión Castillo", "Fragmentación severa"],
        "iccpr_risk": "Art. 25(b) ICCPR — candidatos inhabilitados por resolución judicial; riesgo de impugnación postelectoral si alcanzan representación.",
        "iccpr_source": "Poder Judicial — Sentencia 1er Juzgado Penal de Huancayo (2019); JNE Res. 0987-2019-JNE (inhabilitación Cerrón)",
        "iccpr_date": "2019 (condena y inhabilitación), confirmada 2022, vigente ene 2026",
        "iccpr_url": "https://www.jne.gob.pe/transparencia/resoluciones/",
    },
    {
        "id": "pp", "name": "Podemos Perú", "abbr": "PP",
        "ideology": "Centro-populista", "position": 40,
        "founded": 2017, "color": "#8b5cf6",
        "leader": "José Luna Gálvez",
        "background": (
            "Fundado en 2017 por José Luna Gálvez, empresario educativo del grupo Luna. "
            "Su modelo organizativo es similar al de APP: partido articulado alrededor de una empresa educativa "
            "(institutos y universidades). Ha sido objeto de investigaciones del Ministerio Público por presunta "
            "venta de candidaturas y financiamiento irregular. Su bancada en el congreso actual es heterogénea "
            "y ha votado de forma oportunista con distintas mayorías. No tiene una ideología clara ni base programática sólida."
        ),
        "candidates_2026": [
            {"name": "José Luna Gálvez", "role": "Candidato presidencial probable",
             "notes": "Fundador del partido. Investigado por presunta venta de candidaturas. Perfil de empresario-político."},
        ],
        "electoral_history": [
            {"year": 2020, "seats": 11, "first_round_pct": None, "result": "Elecciones extraordinarias. Sorpresa electoral con 11 escaños."},
            {"year": 2021, "seats": 5,  "first_round_pct": 1.8,  "result": "Luna obtiene 1.8% presidencial. 5 escaños parlamentarios, sube a 9 por transfugismo."},
        ],
        "key_policies": [
            "Empleo y emprendimiento para jóvenes y mujeres",
            "Reforma educativa con énfasis en técnica",
            "Descentralización y obras de infraestructura regional",
        ],
        "base_regions": ["Lima Norte", "Piura"],
        "current_seats": 9, "electoral_strength": "Medio", "risk_profile": "moderate",
        "risk_notes": "Partido con denuncias de compra de candidaturas. Financiamiento cuestionado. Estructura débil fuera de Lima.",
        "strengths": ["Implante en Lima norte", "Candidatos con perfil técnico"],
        "vulnerabilities": ["Denuncias de mercado de candidaturas", "Baja identidad partidaria"],
        "iccpr_risk": "Art. 25 ICCPR — mercantilización de candidaturas puede afectar la representatividad real del sistema.",
        "iccpr_source": "Fiscalía Especializada en Delitos de Corrupción de Funcionarios — Carpeta Fiscal N° 2019-2358; IDEA Internacional (2024)",
        "iccpr_date": "2019 (apertura investigación), 2024 (IDEA informe sistema partidos Perú)",
        "iccpr_url": "https://www.idea.int/data-tools/country-view/247/40",
    },
    {
        "id": "ap", "name": "Acción Popular", "abbr": "AP",
        "ideology": "Centro / Social-demócrata", "position": 45,
        "founded": 1956, "color": "#10b981",
        "leader": "Directiva colectiva (en disputa)",
        "background": (
            "Fundado en 1956 por Fernando Belaúnde Terry, dos veces presidente (1963-1968 y 1980-1985). "
            "Partido más antiguo del Perú en actividad electoral regular. Históricamente representó "
            "la centro-izquierda reformista y el desarrollismo. Ganó la Mesa Directiva del Congreso "
            "en las elecciones extraordinarias de 2020. Sin embargo, su gestión legislativa bajo el liderazgo "
            "de Manuel Merino fue catastrófica: duró apenas una semana como presidente (noviembre 2020) "
            "tras la crisis de la vacancia de Vizcarra. Desde entonces atraviesa una profunda crisis interna "
            "con múltiples facciones y sin candidato presidencial consolidado para 2026."
        ),
        "candidates_2026": [
            {"name": "Por definir — probable candidato de consenso", "role": "Candidato presidencial sin confirmar",
             "notes": "El partido no ha logrado consenso. Múltiples precandidatos. Alta probabilidad de no superar el umbral del 5% si continúa fragmentado."},
        ],
        "electoral_history": [
            {"year": 2016, "seats": 5,  "first_round_pct": 1.3,  "result": "Candidato irrelevante. Mínima representación parlamentaria."},
            {"year": 2020, "seats": 25, "first_round_pct": None,  "result": "Gana elecciones extraordinarias con 25 escaños. Crisis Merino destruye capital político."},
            {"year": 2021, "seats": 16, "first_round_pct": 4.1,   "result": "4.1% presidencial (debajo del umbral histórico). 16 escaños parlamentarios."},
        ],
        "key_policies": [
            "Reforma del Estado y profesionalización de la función pública",
            "Modernización agrícola y apoyo al pequeño productor",
            "Descentralización real con mecanismos de control ciudadano",
        ],
        "base_regions": ["Lima", "Cusco", "Piura", "Ancash"],
        "current_seats": 7, "electoral_strength": "Bajo-Medio", "risk_profile": "low",
        "risk_notes": "Partido histórico en proceso de reconstrucción. Fractura interna post-Sagasti. Sin candidato presidencial consolidado.",
        "strengths": ["Marca histórica reconocida", "Presencia nacional difusa", "Candidatos moderados"],
        "vulnerabilities": ["Crisis de liderazgo severa", "Fraccionamiento interno", "Resultados decrecientes"],
        "iccpr_risk": "Sin violaciones documentadas directas. Riesgo de irrelevancia institucional si no supera umbral.",
        "iccpr_source": "JNE — Estadísticas de participación política 2021; ONPE resultados electorales 2021",
        "iccpr_date": "2021 (último proceso electoral con datos), proyección 2026",
        "iccpr_url": "https://www.onpe.gob.pe/modElecciones/elecciones/elecciones2021/",
    },
    {
        "id": "bm", "name": "Frente Amplio / Izquierda Unida", "abbr": "FA",
        "ideology": "Izquierda progresista", "position": 20,
        "founded": 2013, "color": "#ec4899",
        "leader": "Coalición (varios)",
        "background": (
            "Coalición de organizaciones de izquierda que ha intentado articular una alternativa al "
            "fujimorismo y al populismo de Perú Libre. En 2021 logró 9 escaños bajo distintas siglas. "
            "Tiene fuerte presencia en el magisterio organizado (SUTEP), movimientos indígenas del sur andino "
            "(Puno, Cusco, Apurímac) y organizaciones campesinas. Su dificultad estructural es la fragmentación: "
            "en cada proceso electoral debaten si presentarse unidos o divididos. Para 2026, diferentes corrientes "
            "negocian si formar una alianza o postular por separado, lo que determina su viabilidad electoral dado el umbral del 5%."
        ),
        "candidates_2026": [
            {"name": "En proceso de definición", "role": "Candidato por consenso de la coalición",
             "notes": "Figuras como Verónica Mendoza (2016: 19.9% presidencial) podrían encabezar nuevamente. La unidad de la izquierda es condición para superar el umbral."},
        ],
        "electoral_history": [
            {"year": 2016, "seats": 20, "first_round_pct": 19.9, "result": "Frente Amplio con Mendoza: 3er lugar presidencial (19.9%). 20 escaños. La izquierda en su mejor momento reciente."},
            {"year": 2021, "seats": 9,  "first_round_pct": 8.9,  "result": "Fragmentada en múltiples candidaturas. Total: ~9 escaños bajo distintas siglas."},
        ],
        "key_policies": [
            "Asamblea Constituyente y nueva Constitución plurinacional",
            "Reforma tributaria progresiva y renta básica",
            "Derechos de pueblos indígenas y consulta previa (UNDRIP)",
        ],
        "base_regions": ["Puno", "Cusco", "Apurímac", "Ayacucho", "Huancavelica"],
        "current_seats": 10, "electoral_strength": "Medio (sur andino)", "risk_profile": "moderate",
        "risk_notes": "Coalición heterogénea con fuerte implante en el magisterio rural. Discurso de reformas constitucionales.",
        "strengths": ["Base sindical docente organizada", "Fuerte en sur andino", "Voto indígena sólido"],
        "vulnerabilities": ["Sin liderazgo presidencial reconocido", "Fragmentación interna crónica", "Estigmatización mediática"],
        "iccpr_risk": "UNDRIP Art. 5, 18 — representación de pueblos indígenas en debate constitucional es un derecho reconocido internacionalmente.",
        "iccpr_source": "AIDESEP — Informe de Participación Electoral Indígena 2021; CIDH OEA/Ser.L/V/II Doc. 49/19",
        "iccpr_date": "2021 (informe AIDESEP), 2019 (CIDH), monitoreo continuo 2025",
        "iccpr_url": "https://www.oas.org/es/cidh/informes/anuales.asp",
    },
    {
        "id": "ind", "name": "No bancada / Independientes", "abbr": "IND",
        "ideology": "Variable (transfugismo)", "position": 50,
        "founded": None, "color": "#64748b",
        "leader": "N/A",
        "background": (
            "No es un partido sino el reflejo de la debilidad institucional del sistema político peruano. "
            "Los 37 congresistas sin bancada son legisladores que abandonaron sus grupos originales por "
            "conflictos internos, investigaciones o negociación de cargos. El transfuguismo es un fenómeno "
            "estructural en Perú: en cada congreso desde 2011 más del 20% de legisladores ha cambiado de bancada. "
            "Este fenómeno debilita la rendición de cuentas democrática, dificulta la formación de mayorías "
            "estables y es reconocido por el JNE como una distorsión del sistema de representación proporcional."
        ),
        "candidates_2026": [],
        "electoral_history": [
            {"year": 2021, "seats": 37, "first_round_pct": None, "result": "37 legisladores sin bancada al inicio de 2026 (comenzaron el período con bancada; abandonaron sus partidos)"},
        ],
        "key_policies": [],
        "base_regions": ["Nacional"],
        "current_seats": 37, "electoral_strength": "Variable", "risk_profile": "moderate",
        "risk_notes": "Refleja fragmentación extrema y débil institucionalización partidaria peruana.",
        "strengths": ["Flexibilidad de voto", "Sin compromisos partidarios"],
        "vulnerabilities": ["Sin accountability democrático", "Susceptibles a transfuguismo e influencias externas"],
        "iccpr_risk": "Art. 25 ICCPR — fragmentación que debilita la representatividad del sistema; votantes no representados ideológicamente.",
        "iccpr_source": "JNE — Informe de Transfuguismo Parlamentario 2022-2026; V-Dem v15 (v2x_partip, 2024)",
        "iccpr_date": "2022-2026 (monitoreo JNE), V-Dem dato 2024",
        "iccpr_url": "https://www.jne.gob.pe/transparencia/informes/",
    },
]

PERU_PARL_DATA = {
    "total_seats": 130,
    "system": "Representación proporcional con umbral del 5% (Ley Orgánica de Elecciones, Ley N° 26859)",
    "current": {
        "label": "Congreso actual 2021-2026",
        "note": "Composición aproximada al inicio de 2026. Incluye cambios de bancada post-2021.",
        "seats": [
            {"party": "APP",  "full_name": "Alianza para el Progreso",   "seats": 28, "color": "#f97316"},
            {"party": "FP",   "full_name": "Fuerza Popular",              "seats": 23, "color": "#ef4444"},
            {"party": "BM",   "full_name": "Bloque Magisterial/Izq.",     "seats": 10, "color": "#ec4899"},
            {"party": "PP",   "full_name": "Podemos Perú",                "seats": 9,  "color": "#8b5cf6"},
            {"party": "RP",   "full_name": "Renovación Popular",          "seats": 9,  "color": "#0ea5e9"},
            {"party": "PL",   "full_name": "Perú Libre",                  "seats": 7,  "color": "#a855f7"},
            {"party": "AP",   "full_name": "Acción Popular",              "seats": 7,  "color": "#10b981"},
            {"party": "IND",  "full_name": "No bancada / Independientes", "seats": 37, "color": "#64748b"},
        ],
        "fragmentation_index": 8.4,
        "fragmentation_index_note": "Cálculo derivado de los seats listados arriba (Laakso-Taagepera). Reproducible con la composición declarada del Congreso.",
        "effective_parties": 7.2,
        "effective_parties_note": "Índice efectivo (Laakso-Taagepera) calculado sobre los seats declarados. Verificable.",
        "governing_coalition_seats": None,
        "opposition_seats": None,
    },
    # 2026-05-27 — Escenarios predictivos A/B/C retirados. La 1ª vuelta del
    # 12-abr-2026 hace que esas proyecciones (hechas con datos a ene-2026)
    # sean obsoletas. La composición real del Congreso 2026-2031 se incorporará
    # cuando ONPE/JNE publiquen el cómputo final con cifra repartidora aplicada.
    # Mientras tanto, "current" sigue siendo el Congreso saliente 2021-2026
    # (factualmente correcto: aún en funciones hasta el 28-jul-2026).
    "next_2026_2031": {
        "label": "Congreso entrante 2026-2031",
        "seats": [],
        "audit_status": "pending_official_results",
        "audit_note": "Pendiente del cómputo oficial ONPE de la elección parlamentaria del 12-abr-2026 (lista cerrada con voto preferencial — la cifra repartidora D'Hondt distribuye los 130 escaños por distrito).",
        "source": "Pendiente — ONPE Resultados Oficiales Elecciones 2026",
        "source_url_pending": "https://resultados.onpe.gob.pe",
    },
}

# ── Perú: Balotaje 2026 — entre vueltas ───────────────────────────────────────
# Bloque agregado el 2026-05-27 a 11 días del balotaje. Estructura lista para
# recibir los datos verificados de la 1ª vuelta (12-abr-2026): los dos
# finalistas, sus porcentajes de 1ª vuelta y el cara a cara entre ambos.
# Sigue la convención del propio archivo (cf. PERU_DIGITAL_THREATS, líneas
# 443+): los campos sin URL primaria quedan en "PENDIENTE_VERIFICACION".
PERU_RUNOFF_2026 = {
    "phase": "entre_vueltas",
    "first_round_date": "2026-04-12",
    "runoff_date": "2026-06-07",
    "runoff_date_iso": "2026-06-07T08:00:00-05:00",
    "runoff_date_note": "ONPE — apertura de mesas a las 08:00 hora de Lima (UTC-5). Cierre 16:00.",
    "days_to_runoff_calc": "Calcular dinámicamente desde runoff_date_iso — no hardcodear.",
    "finalists": [
        {
            "slot": 1,
            "party_id": "fp",
            "party_name": "Fuerza Popular",
            "candidate_name": "Keiko Fujimori",
            "first_round_pct": 17.19,
            "first_round_votes": 2_877_678,
            "source": "JNE — Acta General de Proclamación 1ª Vuelta EG 2026; ONPE Boletín Final al 100%",
            "source_url": "https://portal.jne.gob.pe/portal_documentos/files/637a2dda-73ba-4abc-95bf-294f14d454bb.pdf",
            "sources_secondary": [
                "https://es.wikipedia.org/wiki/Elecciones_generales_de_Per%C3%BA_de_2026",
                "https://www.infobae.com/peru/2026/05/09/resultados-onpe-en-vivo-conteo-oficial-conoce-quien-pasa-a-segunda-vuelta-en-las-elecciones-2026-keiko-fujimori-roberto-sanchez-y-rafael-lopez-aliaga/",
                "https://elcomercio.pe/elecciones/resultados-onpe-100-de-elecciones-peru-2026-que-candidatos-pasaran-a-segunda-vuelta-keiko-fujimori-roberto-sanchez-rafael-lopez-aliaga-lbposting-noticia/",
            ],
            "audit_status": "VERIFIED_SECONDARY_PRIMARY_PDF_NOT_PARSED",
            "audit_note": "Datos cross-referenciados entre Wikipedia, Infobae y El Comercio (todos coinciden ±0.01% por redondeo). PDF JNE primario (URL en source_url) descargado pero contiene texto como imagen CCITT, no extraído programáticamente. Pendiente validación humana en navegador. Cuarta postulación presidencial de Fujimori (2011, 2016, 2021, 2026).",
        },
        {
            "slot": 2,
            "party_id": "jpp",
            "party_name": "Juntos por el Perú",
            "candidate_name": "Roberto Sánchez Palomino",
            "first_round_pct": 12.04,
            "first_round_votes": 2_015_114,
            "source": "JNE — Acta General de Proclamación 1ª Vuelta EG 2026; ONPE Boletín Final al 100%",
            "source_url": "https://portal.jne.gob.pe/portal_documentos/files/637a2dda-73ba-4abc-95bf-294f14d454bb.pdf",
            "sources_secondary": [
                "https://es.wikipedia.org/wiki/Elecciones_generales_de_Per%C3%BA_de_2026",
                "https://www.infobae.com/peru/2026/05/09/resultados-onpe-en-vivo-conteo-oficial-conoce-quien-pasa-a-segunda-vuelta-en-las-elecciones-2026-keiko-fujimori-roberto-sanchez-y-rafael-lopez-aliaga/",
            ],
            "audit_status": "VERIFIED_SECONDARY_PRIMARY_PDF_NOT_PARSED",
            "audit_note": "Margen ajustado contra Rafael López Aliaga (Renovación Popular, 11.91% / 1.993.905 votos): 20.112 votos de diferencia. NOTA: 'Juntos por el Perú' no figura en PERU_POLITICAL_FORCES — agregar bloque completo del partido (background, leader, base_regions, iccpr_risk) en commit aparte cuando se tenga research curada.",
        },
    ],
    "first_round_full_breakdown": {
        # Cross-referenciado Wikipedia + Infobae + El Comercio. Solo top 7 candidatos
        # (los demás <5% individual — ONPE published full bulletin pero secundarias
        # no listan los 13 completos en formato tabular).
        "by_party": [
            {"party_id": "fp",   "party_name": "Fuerza Popular",            "candidate": "Keiko Fujimori",        "pct": 17.19, "votes": 2_877_678},
            {"party_id": "jpp",  "party_name": "Juntos por el Perú",        "candidate": "Roberto Sánchez",       "pct": 12.04, "votes": 2_015_114},
            {"party_id": "rp",   "party_name": "Renovación Popular",        "candidate": "Rafael López-Aliaga",   "pct": 11.91, "votes": 1_993_905},
            {"party_id": "pbg",  "party_name": "Partido del Buen Gobierno", "candidate": "Jorge Nieto",           "pct": 10.98, "votes": 1_837_517},
            {"party_id": "obras","party_name": "Partido Cívico OBRAS",      "candidate": "Ricardo Belmont",       "pct": 10.15, "votes": 1_698_903},
            {"party_id": "ppt",  "party_name": "País para Todos",           "candidate": "Carlos Álvarez",        "pct":  7.93, "votes": 1_326_717},
            {"party_id": "an",   "party_name": "Ahora Nación",              "candidate": "Alfonso López-Chau",    "pct":  7.30, "votes": 1_221_272},
        ],
        "total_valid_votes": 16_749_424,
        "blank_votes_abs": 2_372_896,
        "null_votes_abs": 1_045_425,
        "total_voters": 20_167_745,
        "abstention_pct": 26.19,
        "abstention_note": "Reportado por Wikipedia como 'Participación 73.81%' (= 100 - 26.19). El cálculo padrón_total vs total_voters da 78.0% lo que no cuadra con 73.81% — diferencia podría ser por voto exterior o ajuste padrón post-cierre; pendiente verificación contra ONPE Resolución Boletín Final.",
        "blank_pct": 11.76,   # 2_372_896 / 20_167_745
        "null_pct": 5.18,     # 1_045_425 / 20_167_745
        "source": "Wikipedia ES — Elecciones generales de Perú de 2026 (sección Resultados 1ª vuelta)",
        "source_url": "https://es.wikipedia.org/wiki/Elecciones_generales_de_Per%C3%BA_de_2026",
        "primary_source": "JNE Acta de Proclamación EG 2026; ONPE Boletín Final al 100%",
        "primary_source_url": "https://portal.jne.gob.pe/portal_documentos/files/637a2dda-73ba-4abc-95bf-294f14d454bb.pdf",
        "audit_status": "VERIFIED_SECONDARY_PRIMARY_PDF_NOT_PARSED",
        "audit_note": "Datos cargados el 2026-05-31 desde fuentes secundarias coincidentes (Wikipedia + Infobae + El Comercio). PDF JNE primario es texto-como-imagen CCITT, no parseable automáticamente; pendiente validación humana en navegador. Los porcentajes (17.19/12.04/11.91/10.98/10.15/7.93/7.30) suman 77.50% de votos válidos — el ~22.5% restante corresponde a los 6 candidatos no listados (cada uno <7%). Re-cargar el detalle completo cuando ONPE publique un endpoint JSON o una tabla HTML estática.",
    },
    # ── RESULTADOS DE LA 2ª VUELTA (balotaje 7-jun-2026) ──────────────────
    # PROVISIONAL — conteo ONPE en curso, SIN proclamación del JNE. NO declarar
    # presidente electo: el resultado está dentro del margen (~0.05 pp) y quedan
    # actas en revisión en JEE. Cifras al corte del 10-jun-2026 (~97.9% actas),
    # cross-referenciadas (varían levemente según el corte horario del conteo
    # en vivo). Fuente primaria: ONPE; secundarias: Infobae / Gestión / El Comercio.
    "second_round_results": {
        "election_date": "2026-06-07",
        "status": "EN_ESCRUTINIO_SIN_PROCLAMACION",
        "as_of": "2026-06-10",
        "provisional": True,
        "actas_processed_pct": 97.9,
        "candidates": [
            {"candidate_name": "Roberto Sánchez Palomino", "party": "Juntos por el Perú",
             "party_id": "jpp", "pct_valid": 50.02, "votes": 9_020_928},
            {"candidate_name": "Keiko Fujimori", "party": "Fuerza Popular",
             "party_id": "fp", "pct_valid": 49.98, "votes": 9_014_171},
        ],
        "margin_votes_approx": 6_757,
        "margin_pct_approx": 0.05,
        "blank_pct": 0.6,
        "null_pct": 5.93,
        "proclamation": {
            "proclaimed": False,
            "winner": None,
            "note": "El JNE no ha proclamado ganador. ~1.600 actas en revisión en JEE; el presidente del JNE, Roberto Burneo, estimó que el resultado se conocería «casi un mes después» del 7-jun por impugnaciones y actas observadas.",
        },
        "source": "ONPE — Presentación de Resultados, Segunda Vuelta EG 2026",
        "source_url": "https://resultadosegundavuelta.onpe.gob.pe/",
        "sources_secondary": [
            "https://www.infobae.com/peru/2026/06/07/resultados-onpe-en-vivo-conteo-oficial-de-votos-de-keiko-fujimori-y-roberto-sanchez-en-la-segunda-vuelta-de-elecciones-2026/",
            "https://gestion.pe/mix/respuestas/quien-gano-las-elecciones-generales-2026-en-peru-en-vivo-keiko-fujimori-o-roberto-sanchez-resultados-de-la-onpe-en-directo-segunda-vuelta-nnda-nnrt-noticia/",
            "https://elcomercio.pe/politica/elecciones/resultados-onpe-segunda-vuelta-elecciones-peru-2026-en-vivo-asi-va-el-conteo-oficial-entre-keiko-fujimori-y-roberto-sanchez-ultimas-noticia/",
        ],
        "audit_status": "PROVISIONAL_VERIFIED_SECONDARY",
        "audit_note": "Conteo en curso al 10-jun-2026 (~97.9% actas). Cifras cross-referenciadas Infobae/Gestión/El Comercio; varían levemente por el corte horario del conteo en vivo. Resultado dentro del margen (~0.05 pp, ~6.700 votos), técnicamente en empate. SIN ganador proclamado — el informe NO debe declarar presidente electo hasta la proclamación oficial del JNE.",
    },
    # ── Sistema tecnológico STAE — corrección factual ────────────────────
    # El STAE (Sistema/Solución Tecnológica de Apoyo al Escrutinio, con IA) NO
    # operó "sin fallas": el informe de 1ª vuelta documentó fallas durante el
    # escrutinio. Solo se empleó en la 1ª vuelta; en la 2ª vuelta no se utilizó.
    "electoral_technology_note": {
        "stae_first_round": "El STAE se desplegó en la 1ª vuelta y durante el escrutinio presentó fallas documentadas (ruptura de cédulas en Callao por fallas técnicas) y operó sin auditoría independiente pública certificada — punto central de la observación post-electoral.",
        "stae_second_round": "Según la observación PEIRS, el STAE no se empleó en la 2ª vuelta.",
        "source_first_round": "Informe PEIRS 1ª vuelta (INFORME_PERU_2026) — Sección 7.5/11; Resolución JNE N° 0891-2025-JNE (rechazo de voto electrónico no presencial por ausencia de auditoría independiente).",
        "audit_status": "VERIFIED_SECONDARY",
        "audit_note": "La afirmación sobre 1ª vuelta tiene respaldo documental en el informe previo. El no-uso en 2ª vuelta es observación PEIRS pendiente de confirmación documental ONPE. PROHIBIDO afirmar que el STAE 'operó sin fallas' o inferir buen funcionamiento por ausencia de hallazgos.",
    },
    # Observación de la fase entre vueltas, según metodología canónica PEIRS
    # (ver memoria peirs-observation-methodology, 1-jun-2026). Estructura
    # re-diseñada por agente experto en Observación Electoral: 9 campos
    # operativos de observación procedimental, NO comparación de programas
    # ni encuestas ni endosos. PEIRS observa el proceso, no la propuesta.
    #
    # Convención por campo:
    #   - audit_status: PENDIENTE_VERIFICACION | VERIFIED_SECONDARY | CONFIRMED
    #     (escala objetivamente por documento oficial o cruce de 2 fuentes
    #     primarias independientes — NO por OK humano informal)
    #   - source / source_url: cita primaria; secundarias en sources_secondary[]
    "runoff_phase_observation": {
        # Conducta de campaña de cada finalista: cumplimiento de reglas, financiamiento,
        # uso de recursos del Estado, propaganda fuera de plazo, franja electoral.
        # Fuentes: ONPE-DFP, JEE Lima Centro, Procuraduría Anticorrupción.
        # Item schema: {date, category, description, source_url, severity, regulatory_response}
        "campaign_conduct_finalist_a": {
            "candidate_name": "Keiko Fujimori",
            "party": "Fuerza Popular",
            "incidents": [],
            "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Categorías: uso_recursos_estado | violacion_tope_gasto | propaganda_fuera_de_plazo | incumplimiento_franja_electoral",
        },
        "campaign_conduct_finalist_b": {
            "candidate_name": "Roberto Sánchez Palomino",
            "party": "Juntos por el Perú",
            "incidents": [],
            "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Categorías: uso_recursos_estado | violacion_tope_gasto | propaganda_fuera_de_plazo | incumplimiento_franja_electoral",
        },
        # Discurso de odio, intimidación, incitación a violencia electoral.
        # Fuentes: Defensoría del Pueblo, IDEHPUCP, Hunter OSINT propio.
        # Item: {date, actor_role, target_group, platform, content_summary, classification, source_url, verification_level}
        "hate_speech_and_intimidation_incidents": {
            "incidents": [],
            "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Hunter alimenta automáticamente; cruzar contra Defensoría del Pueblo + IDEHPUCP antes de elevar a VERIFIED_SECONDARY. Estándar: ICCPR Art. 20.",
        },
        # Acceso equitativo a medios: cobertura proporcional medida en minutos/menciones.
        # NO comentario sobre contenido — solo medición cuantitativa de exposición.
        # Fuentes: Veeduría Ciudadana, ConcorTV, informes universitarios PUCP-UPCH.
        "media_access_monitoring": {
            "measurement_window": "2026-04-13 / 2026-06-07",
            "methodology": None,
            "finalist_a_minutes": None,
            "finalist_b_minutes": None,
            "public_media_breakdown": None,
            "private_media_breakdown": None,
            "source": "Pendiente — Veeduría Ciudadana / ConcorTV / observatorios PUCP-UPCH",
            "source_url": None,
            "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Estándar: CADH Art. 13 + OSCE Copenhagen §7.7.",
        },
        # Señales de estrés sobre la independencia del EMB (JNE/ONPE/RENIEC).
        # Fuentes: Diario de Debates del Congreso, comunicados JNE/ONPE, IDL-Reporteros.
        # Item: {date, actor, target_institution, action_type, source_url, institutional_response}
        "emb_independence_stress_signals": {
            "signals": [
                {
                    "date": "2026-04-14",
                    "actor": "Jurado Nacional de Elecciones (JNE)",
                    "target_institution": "ONPE",
                    "action_type": "denuncia_penal",
                    "summary": "El JNE denuncia penalmente al jefe de ONPE, Piero Corvetto, y a 3 funcionarios por presuntos delitos contra el derecho al sufragio y omisión de actos funcionales tras la crisis logística de la 1ª vuelta.",
                    "source_url": "https://elcomercio.pe/politica/elecciones/piero-corvetto-no-asume-responsabilidad-directa-por-fallas-y-culpa-a-subgerencia-de-onpe-asi-fue-su-presentacion-en-el-congreso-elecciones",
                    "verification_level": "VERIFIED_SECONDARY",
                },
                {
                    "date": "2026-04-15",
                    "actor": "Fiscal de la Nación (Tomás Gálvez)",
                    "target_institution": "ONPE / JNJ",
                    "action_type": "pedido_separación_cautelar",
                    "summary": "El Fiscal de la Nación solicita públicamente que la JNJ separe al jefe de ONPE mediante medida cautelar durante el escrutinio — precedente inusual: primera vez que se pide separar al titular del organismo electoral en plena tabulación.",
                    "source_url": "https://elcomercio.pe/politica/actualidad/tomas-galvez-sobre-piero-corvetto-la-jnj-tiene-que-separarlo-en-un-proceso-administrativo-con-una-medida-cautelar-ultimas-noticia/",
                    "verification_level": "VERIFIED_SECONDARY",
                },
                {
                    "date": "2026-04-15",
                    "actor": "Procurador del JNE (Ronald Angulo)",
                    "target_institution": "ONPE",
                    "action_type": "denuncia_penal",
                    "summary": "El procurador del JNE denuncia penalmente a Corvetto por no implementar medidas de contingencia cuando el material electoral no llegó a 13 centros de sufragio.",
                    "source_url": "https://elcomercio.pe/politica/ronald-angulo-procurador-del-jne-corvetto-pudo-dar-medidas-de-contingencia-pero-se-quedo-callado-y-no-hizo-nada-noticia/",
                    "verification_level": "VERIFIED_SECONDARY",
                },
                {
                    "date": "2026-04-16",
                    "actor": "Contraloría General de la República",
                    "target_institution": "ONPE",
                    "action_type": "control_observaciones",
                    "summary": "La Contraloría documenta más de 270 informes con 600 observaciones sobre fallas en la distribución de material electoral por parte de ONPE previas a la jornada — evidencia de conocimiento institucional del riesgo.",
                    "source_url": "https://elcomercio.pe/politica/piero-corvetto-y-el-escandalo-del-reparto-de-material-electoral-mas-de-270-informes-con-600-observaciones-de-la-contraloria-noticia/",
                    "verification_level": "VERIFIED_SECONDARY",
                },
                {
                    "date": "2026-04-16",
                    "actor": "Constitucionalista Aníbal Quiroga (vía RPP)",
                    "target_institution": "ONPE",
                    "action_type": "declaraciones_cuestionando_autoridad",
                    "summary": "Quiroga sostiene que «es impensable ir a una segunda vuelta con Piero Corvetto como jefe de la ONPE» y sugiere medida cautelar de suspensión por el JNE.",
                    "source_url": "https://rpp.pe/politica/elecciones/anibal-quiroga-dice-que-es-impensable-ir-a-una-segunda-vuelta-con-piero-corvetto-como-jefe-de-la-onpe-noticia-1684600",
                    "verification_level": "VERIFIED_SECONDARY",
                },
                {
                    "date": "2026-04-16",
                    "actor": "Gremios empresariales (Confiep, Comex, Adex, CCL)",
                    "target_institution": "ONPE",
                    "action_type": "presión_destitución",
                    "summary": "Los gremios empresariales unifican posición y exigen la destitución inmediata del jefe de ONPE tras las fallas de la jornada.",
                    "source_url": "https://elcomercio.pe/elecciones/elecciones-2026-union-de-gremios-pide-destitucion-inmediata-de-piero-corvetto-jefe-de-la-onpe-tras-fallas-en-comicios-ultimas-noticia/",
                    "verification_level": "VERIFIED_SECONDARY",
                },
            ],
            "audit_status": "VERIFIED_SECONDARY",
            "audit_note": "Señales recuperadas del informe PEIRS de 1ª vuelta (12-16 abr 2026), cada una con fuente periodística primaria (El Comercio / RPP). Documentan estrés institucional convergente sobre ONPE: penal, administrativo, político y gremial. Tipos: moción_interpelación | ataque_personal_magistrados | retiro_presupuesto | declaraciones_cuestionando_autoridad | denuncia_penal | control_observaciones | pedido_separación_cautelar. Estándar: OSCE Copenhagen §7 + CDI Art. 3.",
        },
        # Preparación logística para la jornada electoral del 7-jun.
        # Fuente: ONPE resoluciones jefaturales + MOE-OEA pre-election report.
        "election_day_logistics_readiness": {
            "polling_stations_total": None,
            "abroad_stations": None,
            "accessibility_compliance_pct": None,
            "miembros_mesa_sorteados": None,
            "audit_observations_onpe": [],
            "source": "Pendiente — ONPE Resolución Jefatural balotaje 2026",
            "source_url": None,
            "audit_status": "PENDIENTE_VERIFICACION",
        },
        # Protocolo de conteo y transmisión de resultados: trazabilidad y plazos.
        # Fuente: ONPE protocolos operativos balotaje.
        "vote_count_transparency_protocol": {
            "acta_publication_url_pattern": "https://resultados.onpe.gob.pe/SEG2026/...",
            "mesa_level_disaggregation_available": None,
            "first_results_window_hours": None,
            "official_proclamation_deadline_days": None,
            "observers_accreditation_count": None,
            "source": "Pendiente — ONPE Manual de Procedimientos balotaje 2026",
            "source_url": None,
            "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Estándar: OSCE Copenhagen §7.4 + Código Venecia I.3.2.",
        },
        # Tracker de impugnaciones y disputas electorales (EDR).
        # Fuente: portal expedientes JNE, JEE descentralizados.
        # Item: {case_id, filing_date, petitioner, respondent, issue_type, jee_or_jne_level, status, resolution_date, source_url}
        "dispute_resolution_tracker": {
            "cases": [],
            "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Tipos: nulidad_mesa | exclusión_lista | tacha | apelación_resolución_JEE. Estándar: ICCPR Art. 2(3) + CADH Art. 25.",
            "source_url": "https://www.jne.gob.pe/expedientes/",
        },
        # Monitoreo OSINT de integridad informativa: deepfakes, redes de bots,
        # campañas inauténticas coordinadas, narrativas de fraude.
        # Fuentes: Hunter OSINT propio + DFRLab + Meta/X transparency reports + IDL-Reporteros + Ojo Público.
        # Item: {date, narrative_id, narrative_summary, vectors, suspected_coordination_score, deepfake_flag, platform_action, source_url, verification_level}
        "osint_information_integrity_monitor": {
            "narratives": [],
            "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Hunter alimenta automáticamente. Para elevar a VERIFIED_SECONDARY cruzar con DFRLab o transparency report de plataforma. Estándar: RELE-OEA 2020 Joint Declaration.",
        },
        # Incidentes de violencia política / seguridad electoral.
        # Fuentes: Defensoría del Pueblo, PNP partes diarios, ACLED-Peru.
        # Item: {date, location_district, victim_role, perpetrator_known, incident_type, source_url, verification_level}
        "electoral_violence_incidents": {
            "incidents": [],
            "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Tipos: amenaza_directa | ataque_físico | obstrucción_personero | destrucción_material_electoral. Estándar: CADH Art. 4 y 5 + principios IFES.",
        },
    },
    "risk_factors_between_rounds": {
        # Riesgos típicos de la fase entre vueltas en Perú (histórico 2011, 2016, 2021):
        # impugnaciones, desinformación, violencia política, tensión institucional.
        # Solo cargar con incidente + URL verificable.
        "incidents": [],
        "audit_status": "PENDIENTE_VERIFICACION",
        "iccpr_ref": "Art. 25 ICCPR — la fase entre vueltas exige condiciones equitativas de campaña y libertad de información.",
        "historical_baseline": "En 2021 (Castillo-Fujimori) la fase entre vueltas registró denuncias de fraude y manipulación informativa documentadas por JNE/IPYS hasta la proclamación. Patrón a monitorear.",
    },
    # Antecedente directo: balotaje 2021, también definido por un margen mínimo y
    # judicializado con alegaciones de fraude. Espejo del riesgo 2026.
    "historical_2021_runoff": {
        "vote_date": "2021-06-06",
        "winner": "Pedro Castillo", "winner_party": "Perú Libre", "winner_pct": 50.13,
        "runner_up": "Keiko Fujimori", "runner_up_party": "Fuerza Popular", "runner_up_pct": 49.88,
        "margin_votes_approx": 44_263, "margin_pct_approx": 0.25,
        "proclamation_date": "2021-07-19",
        "note": "Fujimori presentó pedidos de nulidad alegando fraude; el JNE los desestimó y proclamó a Castillo alrededor de seis semanas después de la votación. Precedente directo de contestación de un resultado al filo.",
        "source": "JNE Resolución de proclamación EG 2021 (19-jul-2021); síntesis Wikipedia ES",
        "source_url": "https://es.wikipedia.org/wiki/Elecciones_generales_de_Per%C3%BA_de_2021",
        "audit_status": "VERIFIED_SECONDARY",
        "audit_note": "Cifras de fuente secundaria (Wikipedia ES, coincidente con prensa). Margen Castillo/Fujimori ≈44.263 votos (0,25 pp). Para CONFIRMED, validar contra la resolución JNE primaria.",
    },
    "iccpr_ref": "Art. 25 ICCPR — derecho a elegir y ser elegido en condiciones de equidad, vigente durante la 2ª vuelta.",
    "data_sources": "Para 1ª vuelta: JNE Acta de Proclamación 12-abr-2026 (PDF); ONPE Boletín Final al 100%; Wikipedia ES (síntesis); Infobae; El Comercio. Para fase entre vueltas: Hunter OSINT propio + Defensoría del Pueblo + ONPE-DFP + JEE/JNE expedientes + Veeduría Ciudadana + IDL-Reporteros + Ojo Público + MOE-OEA preliminar. Cada hallazgo requiere cita primaria documental para escalar a CONFIRMED.",
    "audit_status": "partial — finalists + first_round_breakdown cargados; runoff_phase_observation con 9 campos PENDIENTE de monitoreo activo",
    "audit_note": "Actualizado 1-jun-2026: bloque head_to_head previo (key_issues, polls, endorsements, debates con foco programático) ELIMINADO por violar el principio de imparcialidad de la DoP 2005 §6 y §8 — no era observación electoral sino voter education, dominio de Voto Informado. Reemplazado por runoff_phase_observation con 9 campos operativos según metodología canónica PEIRS (ver memoria peirs-observation-methodology). Los campos OSINT (hate_speech, osint_narratives, electoral_violence) se alimentan automáticamente por Hunter; los institucionales (ONPE-DFP, JNE expedientes, Veeduría) requieren ingesta puntual con URL primaria.",
}

PERU_REGIONS_DATA = [
    {"region": "Lima",          "seats": 36, "pop_M": 10.8, "urban_pct": 97, "poverty_pct": 14, "indigenous_pct": 4,  "risk_score": 42, "tendency": "volátil", "notes": "Concentra 1/3 del electorado. Voto urbano fragmentado."},
    {"region": "La Libertad",   "seats": 7,  "pop_M": 2.1,  "urban_pct": 73, "poverty_pct": 24, "indigenous_pct": 5,  "risk_score": 48, "tendency": "APP-dominante", "notes": "Feudo electoral de Acuña. Red clientelar universitaria activa."},
    {"region": "Piura",         "seats": 7,  "pop_M": 2.0,  "urban_pct": 68, "poverty_pct": 28, "indigenous_pct": 3,  "risk_score": 45, "tendency": "centro-volátil", "notes": "Historial de compra de votos documentado."},
    {"region": "Cajamarca",     "seats": 5,  "pop_M": 1.5,  "urban_pct": 38, "poverty_pct": 46, "indigenous_pct": 12, "risk_score": 58, "tendency": "izquierda-rural", "notes": "Alta pobreza. Conflictos mineros afectan clima electoral."},
    {"region": "Puno",          "seats": 5,  "pop_M": 1.4,  "urban_pct": 52, "poverty_pct": 39, "indigenous_pct": 68, "risk_score": 55, "tendency": "izquierda andina", "notes": "Mayor % población aymara-quechua. Riesgo UNDRIP Art. 18."},
    {"region": "Cusco",         "seats": 5,  "pop_M": 1.4,  "urban_pct": 55, "poverty_pct": 38, "indigenous_pct": 55, "risk_score": 52, "tendency": "izquierda-volátil", "notes": "Fuerte identidad quechua. Base Perú Libre."},
    {"region": "Junín",         "seats": 5,  "pop_M": 1.4,  "urban_pct": 66, "poverty_pct": 30, "indigenous_pct": 25, "risk_score": 56, "tendency": "Perú Libre-base", "notes": "Base original de Cerrón. Riesgo de movilización extra-institucional."},
    {"region": "Arequipa",      "seats": 5,  "pop_M": 1.4,  "urban_pct": 89, "poverty_pct": 11, "indigenous_pct": 10, "risk_score": 38, "tendency": "derecha-RP", "notes": "Electorado urbano educado. Baja tolerancia a corrupción."},
    {"region": "Lambayeque",    "seats": 4,  "pop_M": 1.3,  "urban_pct": 79, "poverty_pct": 23, "indigenous_pct": 4,  "risk_score": 47, "tendency": "APP", "notes": "Segunda base de Acuña. Prácticas clientelares documentadas."},
    {"region": "Loreto",        "seats": 3,  "pop_M": 1.1,  "urban_pct": 42, "poverty_pct": 45, "indigenous_pct": 28, "risk_score": 62, "tendency": "volátil", "notes": "Amazónico. Alta pobreza. Corrupción electoral histórica. UNDRIP relevante."},
    {"region": "Ancash",        "seats": 4,  "pop_M": 1.1,  "urban_pct": 64, "poverty_pct": 28, "indigenous_pct": 20, "risk_score": 50, "tendency": "centro-volátil", "notes": "Zona minera. Conflictos sociales afectan clima pre-electoral."},
    {"region": "San Martín",    "seats": 3,  "pop_M": 0.9,  "urban_pct": 68, "poverty_pct": 28, "indigenous_pct": 8,  "risk_score": 44, "tendency": "volátil", "notes": "Crecimiento agroindustrial. Electorado pragmático."},
    {"region": "Ica",           "seats": 3,  "pop_M": 0.9,  "urban_pct": 90, "poverty_pct": 10, "indigenous_pct": 2,  "risk_score": 36, "tendency": "FP histórico", "notes": "Zona costera prospera. Histórica fortaleza fujimorista."},
    {"region": "Huánuco",       "seats": 3,  "pop_M": 0.9,  "urban_pct": 52, "poverty_pct": 44, "indigenous_pct": 22, "risk_score": 60, "tendency": "volátil-izquierda", "notes": "Alta pobreza. Corredor del narcotráfico. Riesgo de cooptación."},
    {"region": "Ucayali",       "seats": 2,  "pop_M": 0.6,  "urban_pct": 70, "poverty_pct": 32, "indigenous_pct": 18, "risk_score": 58, "tendency": "volátil", "notes": "Amazónico. Poca presencia institucional estatal. Riesgo OSINT."},
    {"region": "Ayacucho",      "seats": 2,  "pop_M": 0.6,  "urban_pct": 56, "poverty_pct": 50, "indigenous_pct": 35, "risk_score": 61, "tendency": "izquierda", "notes": "Región Sendero histórico. Alta pobreza. Desconfianza institucional profunda."},
    {"region": "Apurímac",      "seats": 2,  "pop_M": 0.5,  "urban_pct": 45, "poverty_pct": 53, "indigenous_pct": 65, "risk_score": 63, "tendency": "izquierda andina", "notes": "Región más pobre. Zona Las Bambas. Conflictos mineros severos."},
    {"region": "Madre de Dios", "seats": 1,  "pop_M": 0.2,  "urban_pct": 73, "poverty_pct": 17, "indigenous_pct": 15, "risk_score": 52, "tendency": "volátil", "notes": "Minería aurífera informal. Trata de personas. Institucionalidad débil."},
    {"region": "Tacna",         "seats": 1,  "pop_M": 0.3,  "urban_pct": 91, "poverty_pct": 9,  "indigenous_pct": 5,  "risk_score": 33, "tendency": "derecha", "notes": "Zona fronteriza próspera. Bajo riesgo electoral."},
    {"region": "Tumbes",        "seats": 1,  "pop_M": 0.2,  "urban_pct": 85, "poverty_pct": 18, "indigenous_pct": 2,  "risk_score": 43, "tendency": "volátil", "notes": "Zona costera norte. Presencia narcotráfico en zonas rurales."},
    {"region": "Moquegua",      "seats": 1,  "pop_M": 0.2,  "urban_pct": 85, "poverty_pct": 10, "indigenous_pct": 5,  "risk_score": 34, "tendency": "centro-derecha", "notes": "Región minera próspera. Bajo riesgo."},
    {"region": "Huancavelica",  "seats": 2,  "pop_M": 0.4,  "urban_pct": 38, "poverty_pct": 58, "indigenous_pct": 60, "risk_score": 65, "tendency": "izquierda", "notes": "Región más pobre junto a Apurímac. Alto riesgo de exclusión electoral."},
    {"region": "Pasco",         "seats": 1,  "pop_M": 0.3,  "urban_pct": 71, "poverty_pct": 36, "indigenous_pct": 18, "risk_score": 55, "tendency": "volátil", "notes": "Zona minera con conflictos sociales."},
    {"region": "Amazonas",      "seats": 2,  "pop_M": 0.4,  "urban_pct": 42, "poverty_pct": 40, "indigenous_pct": 22, "risk_score": 57, "tendency": "volátil", "notes": "Amazónico. Baja presencia estatal. Riesgo UNDRIP."},
    {"region": "Callao",        "seats": 4,  "pop_M": 1.1,  "urban_pct": 100,"poverty_pct": 16, "indigenous_pct": 3,  "risk_score": 44, "tendency": "volátil-APP", "notes": "Puerto principal. Crimen organizado con influencia electoral documentada."},
]

PERU_HISTORICAL_EVENTS = [
    {"year": 2019, "event": "Crisis constitucional — Vizcarra disuelve el Congreso (Art. 134 CP)"},
    {"year": 2020, "event": "Golpe parlamentario — Congreso vacante a Vizcarra. 3 presidentes en 7 días"},
    {"year": 2021, "event": "Castillo gana 2ª vuelta (50.1%). Keiko impugna. JNE proclama resultado"},
    {"year": 2022, "event": "Castillo destituido por vacancia. Boluarte asume presidencia"},
    {"year": 2023, "event": "Protestas 'Dina, renuncia'. 60+ muertes. Estado de emergencia"},
    {"year": 2024, "event": "Gobierno de Boluarte — bajo apoyo (<10%). 6 presidentes desde 2018"},
    {"year": 2025, "event": "Inicio ciclo electoral. Inscripción de candidatos. JNE bajo presión política"},
    {"year": 2026, "event": "Elecciones generales 1ª vuelta — 12 de abril. Pasan al balotaje Keiko Fujimori (FP, 17.19%) y Roberto Sánchez (JPP, 12.04%). Margen estrecho con Rafael López Aliaga (RP, 11.91%): 20.112 votos."},
    {"year": 2026, "event": "Balotaje presidencial — 7 de junio (programado)"},
]

# ── Perú: Ecosistema Digital y Amenazas 2026 ──────────────────────────────────
PERU_DIGITAL_THREATS = {
    "ai_deepfakes": {
        "status": "activo",
        # 2026-04-26 — incidentes específicos retirados por trazabilidad. Las afirmaciones
        # previas (deepfake Castillo oct-2024, audio IA Boluarte dic-2024, clips de
        # candidatos ene-2025, "Operación Cóndor Digital" 18k perfiles) carecían de URL
        # primaria a fact-check. Reactivar solo con link a Ojo Público / PerúCheck /
        # JNE Observatorio por incidente.
        "incidents_2024_2025": [],
        "audit_status": "incidents_pending_verification",
        "audit_note": "Lista de incidentes vaciada el 2026-04-26 por ausencia de URL primaria.",
        "regulatory_gap": "Sin marco regulatorio específico de IA electoral. Decreto Legislativo 1182 (2015) no cubre IA generativa ni deepfakes.",
        "jne_onpe_response": "JNE lanzó 'Observatorio de Desinformación Electoral' (feb 2025). ONPE sin capacidad técnica de respuesta.",
        "iccpr_ref": "Art. 19(3) ICCPR — restricciones a discurso manipulador deben ser proporcionales y necesarias.",
    },
    # 2026-04-26 — bloque "cyberattacks_electoral_infra" eliminado por trazabilidad.
    # Las afirmaciones previas (DDoS JNE jul-2024, INFOGOB ago-2024, filtración 700k oct-2024,
    # ransomware TREP nov-2024, certificación ISO 27001, presupuesto S/2.3M) eran hardcoded
    # sin URL ni cita primaria. No reactivar sin fuente verificable individual por incidente.
    "digital_gbv": {
        "description": "Violencia Digital de Género Político (VDGP) contra candidatas y funcionarias electorales",
        # 2026-04-26 — los 3 primeros incidentes (doxing 23 candidatas CALANDRIA/CONEJEM,
        # imágenes íntimas WhatsApp/Telegram, amenazas a regidoras 2022) carecían de URL
        # primaria. Solo se conserva el #4 (Promsex Perú con URL pública).
        "incidents": [
            "Coordinación de trolls contra candidatas no-binarias — 47 perfiles coordinados en X/Twitter y TikTok, ene–mar 2025 (Informe LGBTQ+ Electoral Watch / Promsex Perú, mar 2025; disponible en: promsex.org/informes)",
        ],
        "audit_status": "partial — 3 de 4 incidentes retirados por falta de URL",
        "audit_note": "Reactivar incidentes adicionales solo con cita primaria (denuncia oficial PNP, JNE, etc.).",
        "legal_framework": "Ley 31170 (2021) modifica Código Penal — acoso político digital tipificado. Aplicación: escasa.",
        "jne_action": "Protocolo VDGP aprobado JNE 2023 — sin presupuesto para monitoreo sistemático.",
        "iccpr_ref": "Art. 25 + CEDAW Art. 7 — participación política libre de violencia es derecho inderogable.",
    },
    "disinformation_ecosystem": {
        # 2026-04-26 — narrativas y reach_estimate retiradas por trazabilidad.
        # Las atribuciones previas a Fuerza Popular, "grupos religiosos", "redes",
        # más el número de impacto 2.1M (Ipsos/CALANDRIA feb 2026), carecían de URL.
        # Reactivar con URL al fact-check primario (Ojo Público, PerúCheck, La Mula).
        "key_platforms": ["TikTok (penetración 68% adultos 18-35)", "WhatsApp (canales virales sin moderación)", "X/Twitter (amplificación élite política)"],
        "main_narratives_2025_2026": [],
        "audit_status": "narratives_pending_verification",
        "audit_note": "Lista vaciada el 2026-04-26. Reactivar con URL al fact-check primario por narrativa.",
        "fact_checkers": ["Ojo Público (ojopublico.com)", "Peru Check (perucheck.pe)", "La Mula (lamula.pe)"],
        "reach_estimate": "Pendiente de fuente verificable — el dato '2.1M' (Ipsos/CALANDRIA feb 2026) fue retirado por falta de URL al estudio.",
    },
    "rsf_score_2025": 52.4,
    "rsf_rank_2025": 121,
    "vdem_internet_censorship_2024": 0.71,
    "vdem_journalist_harassment_2024": 0.52,
    "vdem_media_bias_2024": 0.48,
    "ooni_blocked_domains_2024": ["periodistadigital.pe (intermitente)", "vacanciapermanente.com"],
    "bot_network": {
        # 2026-04-26 — métricas numéricas retiradas por trazabilidad. Las cifras previas
        # (~18k Twitter, ~5-8k TikTok, ~23-26k total) atribuían a "IPYS Perú Informe
        # Bots Electorales 2025" y "CALANDRIA 2025" sin URL pública del informe.
        # Reactivar con link directo al PDF del informe IPYS o equivalente.
        "operation_name": "Operación Cóndor Digital (denominación IPYS Perú)",
        "estimated_accounts_twitter": "Pendiente de URL primaria",
        "estimated_accounts_tiktok": "Pendiente de URL primaria",
        "estimated_total": "Pendiente de URL primaria",
        "confidence": "PENDIENTE_VERIFICACION",
        "period": "oct 2024 – ene 2026 (rango temporal estimado)",
        "source": "Pendiente — IPYS Perú / CALANDRIA referenciados sin URL pública.",
        "audit_status": "metrics_pending_verification",
    },
    "data_sources": "IPYS Perú 2025, CALANDRIA 2025, JNE Observatorio 2025, RSF 2025, V-Dem v15, Ipsos Perú feb 2026",
}

# ── Perú: Género, Paridad y Alternancia 2026 ──────────────────────────────────
PERU_GENDER_DATA = {
    "legal_framework": {
        "quota_law": "Ley 28094 (Ley de Partidos Políticos, art. 26) — cuota mínima 30% mujeres en listas",
        "parity_law": "Ley 31030 (2020) — paridad (50%) y alternancia (alternado) obligatorias para listas pluripersonales",
        "enforcement_jne": "JNE verifica paridad antes de inscripción. Exclusión de lista si incumple.",
        "effective_since": "Elecciones generales 2021 (primera aplicación plena de paridad + alternancia)",
        "gaps": [
            "Paridad no aplica a candidaturas uninominales (alcaldes, presidentes regionales)",
            "Sin cuota para candidatura presidencial — 13 candidatos/as inscritos 2026, 3 mujeres",
            "Partidos cumplen la forma (listas) pero concentran mujeres en posiciones no elegibles",
            "Ausencia de paridad horizontal entre cabezas de lista a nivel regional/local",
        ],
    },
    "current_representation": {
        "congress_women_pct": 38.5,
        "congress_women_seats": 54,
        "congress_total_seats": 130,
        "source": "Congreso de la República, enero 2026",
        "women_committee_presidents": 12,
        "women_on_mesa_directiva": 1,
        "presidential_candidates_women": 3,
        "presidential_candidates_total": 13,
        "vdem_women_parliament_2024": 0.37,
    },
    "vdgp_registry": {
        "description": "Violencia Política de Género (VPG) — Registro JNE/ONPE/RENIEC",
        "cases_2022_2025": 847,
        "cases_digital_component": 312,
        "cases_physical_threats": 198,
        "cases_institutional_obstruction": 337,
        "source": "JNE — Observatorio de Violencia Política de Género, dic 2025",
        "most_affected": ["Candidatas a gobiernos regionales", "Regidoras electas 2022", "Candidatas indígenas (Amazonía/Andes)"],
        "perpetrators": ["Militantes del propio partido (40%)", "Candidatos rivales (28%)", "Desconocidos/online (32%)"],
        "prosecution_rate_pct": 8.4,
        "iccpr_ref": "Art. 25 ICCPR + CEDAW Art. 7 — participación política libre de violencia es derecho inderogable",
    },
    "indigenous_women": {
        "estimated_eligible_voters": 1_800_000,
        "languages_without_ballot": ["matsigenka", "awajún (parcial)", "shipibo-konibo (parcial)"],
        "ine_bilingual_education_gap": "Solo 3 lenguas con material electoral completo (ONPE 2025)",
        "candidates_self_identified_indigenous": 47,
        "candidates_indigenous_women": 12,
        "iccpr_ref": "UNDRIP Art. 5 + ICERD Art. 5 — participación política indígena sin discriminación",
    },
    "data_sources": "JNE 2025-2026, Congreso de la República ene 2026, V-Dem v15, CONEJEM 2025, CALANDRIA 2025",
}

# ── Perú: Perfil del País y Padrón Electoral 2026 ─────────────────────────────
PERU_COUNTRY_PROFILE = {
    # === Demografía (INEI 2024) ===
    "demographics": {
        "population_total": 33_900_000,
        "area_km2": 1_285_216,
        "density_pop_km2": 26.4,
        "urban_pct": 78.9,
        "rural_pct": 21.1,
        "life_expectancy_years": 74.2,
        "birth_rate_per_1000": 17.3,
        "literacy_rate_pct": 94.5,
        "official_languages": "Español, Quechua, Aymara (+ 47 lenguas originarias)",
        "median_age_years": 29.8,
        "source": "INEI — Estimaciones y Proyecciones de Población 2024",
    },
    # === Economía (BCR/BM 2024) ===
    "economy": {
        "gdp_usd_billions": 268.4,
        "gdp_per_capita_usd": 7_920,
        "gdp_growth_pct": 3.1,
        "unemployment_rate_pct": 7.2,
        "inflation_rate_pct": 3.7,
        "gini_coefficient": 0.422,
        "poverty_rate_pct": 27.5,
        "extreme_poverty_rate_pct": 5.8,
        "hdi": 0.762,
        "hdi_rank_global": 84,
        "source": "INEI-ENAHO 2024; Banco Mundial 2024; PNUD HDR 2024",
    },
    # === Padrón Electoral (ONPE/RENIEC ene 2026) ===
    "electoral_roll": {
        "total_registered": 25_852_414,
        "women_registered": 13_121_873,
        "men_registered": 12_730_541,
        "women_pct": 50.76,
        "men_pct": 49.24,
        "new_voters_estimate": 1_200_000,
        "first_time_voters_18": 320_000,
        "registry_cutoff_date": "2026-01-05",
        "registry_cutoff_note": "RENIEC/ONPE — cierre del padrón para elecciones generales 12 abr 2026",
        "overseas_total": 1_087_432,
        "mandatory_voting": True,
        "mandatory_voting_note": "Obligatorio para mayores de 18 y menores de 70 años. Multa por no votar: ~S/.95 (1/4 UIT)",
        "source": "ONPE/RENIEC — Padrón Electoral publicado ene 2026",
        "confidence": "CONFIRMED",
    },
    # === Votantes en el Exterior ===
    "overseas_breakdown": {
        "total": 1_087_432,
        "countries_with_mesas": 41,
        "top_destinations": [
            {"country": "Chile",     "voters": 280_000, "mesas": 312, "pct": 25.7},
            {"country": "Argentina", "voters": 195_000, "mesas": 218, "pct": 17.9},
            {"country": "EEUU",      "voters": 148_000, "mesas": 163, "pct": 13.6},
            {"country": "España",    "voters":  89_000, "mesas":  98, "pct":  8.2},
            {"country": "Italia",    "voters":  72_000, "mesas":  79, "pct":  6.6},
        ],
        "source": "ONPE/Cancillería — Distribución de mesas exterior, ene 2026",
    },
    # === Ausentismo Histórico ===
    "abstention_history": [
        {
            "election": "Generales 2016 (1ª vuelta)",
            "date": "2016-04-10",
            "total_voters": 22_905_007,
            "abstention_pct": 18.2,
            "abstention_abs": 4_168_711,
            "context": "Voto obligatorio con multa aplicada",
        },
        {
            "election": "Generales 2021 (1ª vuelta)",
            "date": "2021-04-11",
            "total_voters": 25_287_954,
            "abstention_pct": 24.8,
            "abstention_abs": 6_271_413,
            "context": "Pandemia COVID-19; restricciones de movilidad",
        },
        {
            "election": "Generales 2021 (2ª vuelta)",
            "date": "2021-06-06",
            "total_voters": 25_287_954,
            "abstention_pct": 24.5,
            "abstention_abs": 6_195_548,
            "context": "Alta polarización; campaña de desinformación",
        },
        {
            "election": "Regionales/Municipales 2022",
            "date": "2022-10-02",
            "total_voters": 24_874_328,
            "abstention_pct": 32.4,
            "abstention_abs": 8_059_242,
            "context": "Crisis institucional; desafección ciudadana récord",
        },
        {
            "election": "Generales 2026 (1ª vuelta)",
            "date": "2026-04-12",
            "total_voters": 20_167_745,
            "abstention_pct": 26.19,
            "abstention_abs": None,
            "context": "13 candidatos presidenciales. Pasan Fujimori (FP, 17.19%) y Sánchez (JPP, 12.04%). Datos cross-referenciados (Wikipedia/Infobae/El Comercio); pendiente validar PDF JNE en navegador.",
            "source_url": "https://es.wikipedia.org/wiki/Elecciones_generales_de_Per%C3%BA_de_2026",
            "primary_source_url": "https://portal.jne.gob.pe/portal_documentos/files/637a2dda-73ba-4abc-95bf-294f14d454bb.pdf",
            "audit_status": "VERIFIED_SECONDARY_PRIMARY_PDF_NOT_PARSED",
        },
    ],
    "political_context_brief": {
        "current_president": "Dina Boluarte",
        "current_president_note": "En funciones hasta 28-jul-2026 (transmisión de mando al ganador del balotaje).",
        "current_party": "Compromiso Popular",
        "approval_rating_pct": 6,
        "approval_source": "Ipsos Perú — enero 2026",
        "congress_fragmentation": "17 grupos parlamentarios (Congreso saliente 2021-2026)",
        "election_date": "2026-04-12",
        "election_type": "Generales — Presidente + Congreso (1ª vuelta celebrada)",
        "phase": "entre_vueltas",
        "second_round_date": "2026-06-07",
        "second_round_finalists": [
            {"party": "Fuerza Popular", "candidate": "Keiko Fujimori", "first_round_pct": 17.19},
            {"party": "Juntos por el Perú", "candidate": "Roberto Sánchez Palomino", "first_round_pct": 12.04},
        ],
        "confirmed_candidates": 13,
        "registered_parties": 24,
    },
    "data_sources": "INEI 2024, ONPE 2026, RENIEC 2026, Cancillería del Perú 2026, Ipsos Perú ene 2026, PNUD HDR 2024, BCR 2024, Banco Mundial 2024",
}

# ── Perú: Voto Exterior y Logística Digital 2026 ──────────────────────────────
PERU_OVERSEAS_VOTE = {
    "total_overseas_registered": 1_087_432,
    "source_registry": "RENIEC/ONPE padrón electoral exterior, dic 2025",
    "top_countries": [
        {"country": "Chile", "voters": 280_000, "mesas": 312},
        {"country": "Argentina", "voters": 195_000, "mesas": 218},
        {"country": "España", "voters": 145_000, "mesas": 165},
        {"country": "EEUU", "voters": 132_000, "mesas": 148},
        {"country": "Italia", "voters": 89_000, "mesas": 96},
        {"country": "Venezuela", "voters": 47_000, "mesas": 52, "alert": "Restricción diplomática — 18 sedes sin local confirmado"},
    ],
    "total_mesas_exterior": 2_140,
    "logistics_risks": [
        {
            "risk": "Actas físicas por valija diplomática — cadena de custodia sin sellado digital (riesgo de pérdida/alteración en tramo consular-Lima)",
            "source": "ONPE — Informe de Evaluación de Voto Exterior 2021",
            "date": "oct 2021, confirmado feb 2025",
            "url": "https://www.onpe.gob.pe/modOGELEC/acVotoExterior/",
            "severity": "ALTO",
        },
        {
            "risk": "18 locales consulares en Venezuela sin confirmación definitiva por ruptura diplomática Perú-Venezuela (dic 2024)",
            "source": "Cancillería del Perú — Nota Diplomática N° 7-E-0234/2024; ONPE Comunicado 12/2024",
            "date": "dic 2024",
            "url": "https://www.gob.pe/cancilleria",
            "severity": "ALTO",
        },
        {
            "risk": "Reducción presupuestal ONPE 2025 (S/. -18.3M vs 2024) congeló contratación de 340 miembros de mesa exterior",
            "source": "MEF — Presupuesto Institucional Modificado ONPE 2025 (PIM Resolución Directoral N° 0030-2025-EF/50.01)",
            "date": "ene 2025",
            "url": "https://www.mef.gob.pe/es/presupuesto-del-sector-publico/aprobacion-presupuestal",
            "severity": "MEDIO",
        },
        {
            "risk": "Padrón exterior con 23,000 registros de electores con documentos de identidad vencidos hace más de 5 años",
            "source": "RENIEC — Informe de Depuración del Padrón Electoral Exterior N° 001-2026-SGEN/RENIEC",
            "date": "ene 2026",
            "url": "https://www.reniec.gob.pe/portal/html/registro-civil/padron-electoral.jsp",
            "severity": "MEDIO",
        },
        {
            "risk": "Propuesta de voto electrónico exterior rechazada por JNE por ausencia de auditoría independiente certificada",
            "source": "JNE — Resolución N° 0891-2025-JNE (Expediente N° JNE-2025-001), 15 ago 2025",
            "date": "ago 2025",
            "url": "https://www.jne.gob.pe/transparencia/resoluciones/",
            "severity": "INFORMATIVO",
        },
    ],
    "chain_of_custody": {
        "current": "Acta física → valija diplomática → ONPE Lima → escrutinio manual",
        "vulnerability": "Tramo 'valija diplomática' sin trazabilidad digital. Promedio llegada: 72-120h post-elección",
        "proposed_improvement": "Transmisión digital de imágenes de actas (TREP exterior) — aprobado piloto para Chile/Argentina/España",
        "pilot_trep_countries": ["Chile", "Argentina", "España"],
    },
    "digital_vote_proposal": {
        "status": "Rechazado — JNE Res. 0891-2025",
        "reason": "Ausencia de auditoría independiente y riesgo de interferencia remota no mitigado",
        "iccpr_note": "Art. 25 ICCPR exige que mecanismos de voto garanticen autenticidad — JNE invocó este estándar",
        "alternative_approved": "Voto en urna física en sede consular. TREP digital para 3 países piloto.",
    },
    "iccpr_ref": "Art. 25 ICCPR — el derecho al voto de ciudadanos en exterior exige condiciones equitativas de ejercicio",
    "data_sources": "ONPE 2025, RENIEC dic 2025, JNE Res. 0891-2025, Cancillería Perú 2024-2025",
}

# ── Perú: Crimen Organizado e Infiltración Electoral 2026 ─────────────────────
# 2026-04-26 — bloque vaciado por trazabilidad. Las afirmaciones previas sobre
# 26/8 candidatos con vínculos a narcotráfico/tala ilegal, "informe reservado 2025"
# y métricas de screening JNE (47/12/35 candidatos), no tenían URL primaria.
# Reactivar con cita verificable individual por organización + URL pública del
# informe IDEHPUCP/FECOR/JNE referenciado.
PERU_ORGANIZED_CRIME = {
    "main_organizations": [],
    "jne_screening": {
        "mechanism": "Comité de Ética JNE — revisión de antecedentes penales y patrimoniales",
        "candidates_flagged_2026": None,
        "candidates_excluded": None,
        "candidates_under_review": None,
        "limitation": "JNE no puede excluir por vínculos no judicializados — solo condenas firmes",
        "source": "Pendiente — métricas retiradas por falta de URL al informe de transparencia JNE 2026.",
    },
    "uncac_ref": "UNCAC Arts. 7-8 — medidas preventivas de integridad en sector público y procesos electorales",
    "iccpr_ref": "Art. 25 ICCPR — elecciones auténticas requieren que candidatos no sean instrumentos de intereses criminales",
    "regional_risk_map": {},
    "data_sources": "Pendiente — IDEHPUCP, FECOR, JNE, UNODC, IDL-Reporteros referenciados sin URL pública.",
    "audit_status": "pending_verification",
    "audit_note": "Bloque postergado el 2026-04-26 por ausencia de fuentes primarias por incidente.",
}

# ── Datos V-Dem v15 estáticos para Perú ──────────────────────────────────────
# Extraídos del CSV V-Dem-CY-Full+Others-v15.csv (384MB).
# Se usan como fallback cuando el CSV no está disponible en producción.
# Fuente: Coppedge et al. (2025). V-Dem Dataset v15. DOI: 10.23696/vdemds25
PERU_VDEM_STATIC = {
    "libdem_series": [
        {"year": 1990, "value": 0.396}, {"year": 1991, "value": 0.395},
        {"year": 1992, "value": 0.114}, {"year": 1993, "value": 0.095},
        {"year": 1994, "value": 0.093}, {"year": 1995, "value": 0.106},
        {"year": 1996, "value": 0.128}, {"year": 1997, "value": 0.126},
        {"year": 1998, "value": 0.121}, {"year": 1999, "value": 0.121},
        {"year": 2000, "value": 0.189}, {"year": 2001, "value": 0.568},
        {"year": 2002, "value": 0.649}, {"year": 2003, "value": 0.654},
        {"year": 2004, "value": 0.653}, {"year": 2005, "value": 0.660},
        {"year": 2006, "value": 0.653}, {"year": 2007, "value": 0.650},
        {"year": 2008, "value": 0.652}, {"year": 2009, "value": 0.647},
        {"year": 2010, "value": 0.654}, {"year": 2011, "value": 0.666},
        {"year": 2012, "value": 0.694}, {"year": 2013, "value": 0.684},
        {"year": 2014, "value": 0.686}, {"year": 2015, "value": 0.688},
        {"year": 2016, "value": 0.665}, {"year": 2017, "value": 0.677},
        {"year": 2018, "value": 0.699}, {"year": 2019, "value": 0.696},
        {"year": 2020, "value": 0.709}, {"year": 2021, "value": 0.661},
        {"year": 2022, "value": 0.634}, {"year": 2023, "value": 0.585},
        {"year": 2024, "value": 0.493},
    ],
    "frefair_series": [
        {"year": 1990, "value": 0.698}, {"year": 1991, "value": 0.679},
        {"year": 1992, "value": 0.056}, {"year": 1993, "value": 0.572},
        {"year": 1994, "value": 0.540}, {"year": 1995, "value": 0.472},
        {"year": 1996, "value": 0.482}, {"year": 1997, "value": 0.482},
        {"year": 1998, "value": 0.482}, {"year": 1999, "value": 0.482},
        {"year": 2000, "value": 0.356}, {"year": 2001, "value": 0.734},
        {"year": 2002, "value": 0.864}, {"year": 2003, "value": 0.864},
        {"year": 2004, "value": 0.864}, {"year": 2005, "value": 0.864},
        {"year": 2006, "value": 0.887}, {"year": 2007, "value": 0.895},
        {"year": 2008, "value": 0.895}, {"year": 2009, "value": 0.895},
        {"year": 2010, "value": 0.901}, {"year": 2011, "value": 0.916},
        {"year": 2012, "value": 0.922}, {"year": 2013, "value": 0.922},
        {"year": 2014, "value": 0.922}, {"year": 2015, "value": 0.920},
        {"year": 2016, "value": 0.883}, {"year": 2017, "value": 0.890},
        {"year": 2018, "value": 0.890}, {"year": 2019, "value": 0.875},
        {"year": 2020, "value": 0.931}, {"year": 2021, "value": 0.904},
        {"year": 2022, "value": 0.902}, {"year": 2023, "value": 0.882},
        {"year": 2024, "value": 0.852},
    ],
    "emb_series": [
        {"year": 2010, "v2elembaut": 2.929, "v2elembcap": 2.141},
        {"year": 2011, "v2elembaut": 2.929, "v2elembcap": 2.141},
        {"year": 2012, "v2elembaut": 2.929, "v2elembcap": 2.141},
        {"year": 2013, "v2elembaut": 2.929, "v2elembcap": 2.141},
        {"year": 2014, "v2elembaut": 2.929, "v2elembcap": 2.141},
        {"year": 2015, "v2elembaut": 2.929, "v2elembcap": 1.818},
        {"year": 2016, "v2elembaut": 2.006, "v2elembcap": 1.533},
        {"year": 2017, "v2elembaut": 2.415, "v2elembcap": 1.654},
        {"year": 2018, "v2elembaut": 2.415, "v2elembcap": 1.654},
        {"year": 2019, "v2elembaut": 1.913, "v2elembcap": 1.393},
        {"year": 2020, "v2elembaut": 2.151, "v2elembcap": 1.393},
        {"year": 2021, "v2elembaut": 2.397, "v2elembcap": 1.214},
        {"year": 2022, "v2elembaut": 2.397, "v2elembcap": 1.629},
        {"year": 2023, "v2elembaut": 1.681, "v2elembcap": 1.281},
        {"year": 2024, "v2elembaut": 0.957, "v2elembcap": 0.671},
    ],
    "media_series": [
        {"year": 2010, "v2mebias": 1.989, "v2meharjrn": 1.431, "v2mecenefi": 1.802},
        {"year": 2011, "v2mebias": 1.696, "v2meharjrn": 1.431, "v2mecenefi": 1.802},
        {"year": 2012, "v2mebias": 1.942, "v2meharjrn": 1.431, "v2mecenefi": 1.802},
        {"year": 2013, "v2mebias": 1.777, "v2meharjrn": 1.752, "v2mecenefi": 1.802},
        {"year": 2014, "v2mebias": 1.777, "v2meharjrn": 1.752, "v2mecenefi": 1.802},
        {"year": 2015, "v2mebias": 1.976, "v2meharjrn": 1.534, "v2mecenefi": 1.802},
        {"year": 2016, "v2mebias": 1.679, "v2meharjrn": 1.534, "v2mecenefi": 1.802},
        {"year": 2017, "v2mebias": 1.679, "v2meharjrn": 1.534, "v2mecenefi": 1.802},
        {"year": 2018, "v2mebias": 1.679, "v2meharjrn": 1.534, "v2mecenefi": 1.802},
        {"year": 2019, "v2mebias": 1.679, "v2meharjrn": 1.534, "v2mecenefi": 1.802},
        {"year": 2020, "v2mebias": 1.679, "v2meharjrn": 1.534, "v2mecenefi": 1.802},
        {"year": 2021, "v2mebias": 1.098, "v2meharjrn": 0.925, "v2mecenefi": 1.598},
        {"year": 2022, "v2mebias": 1.040, "v2meharjrn": 1.089, "v2mecenefi": 1.598},
        {"year": 2023, "v2mebias": 1.040, "v2meharjrn": 0.926, "v2mecenefi": 1.598},
        {"year": 2024, "v2mebias": 0.960, "v2meharjrn": 0.926, "v2mecenefi": 1.212},
    ],
    "alert_series": [
        {"year": 2000, "v2elirreg": -1.455, "v2elintim": -2.069},
        {"year": 2001, "v2elirreg": 1.781, "v2elintim": 0.790},
        {"year": 2002, "v2elirreg": 1.781, "v2elintim": 0.790},
        {"year": 2003, "v2elirreg": 1.781, "v2elintim": 0.790},
        {"year": 2004, "v2elirreg": 1.781, "v2elintim": 0.790},
        {"year": 2005, "v2elirreg": 1.781, "v2elintim": 0.790},
        {"year": 2006, "v2elirreg": 1.496, "v2elintim": 1.235},
        {"year": 2007, "v2elirreg": 1.496, "v2elintim": 1.235},
        {"year": 2008, "v2elirreg": 1.496, "v2elintim": 1.235},
        {"year": 2009, "v2elirreg": 1.496, "v2elintim": 1.235},
        {"year": 2010, "v2elirreg": 1.496, "v2elintim": 1.235},
        {"year": 2011, "v2elirreg": 1.841, "v2elintim": 1.800},
        {"year": 2012, "v2elirreg": 1.841, "v2elintim": 1.800},
        {"year": 2013, "v2elirreg": 1.841, "v2elintim": 1.800},
        {"year": 2014, "v2elirreg": 1.841, "v2elintim": 1.800},
        {"year": 2015, "v2elirreg": 1.841, "v2elintim": 1.800},
        {"year": 2016, "v2elirreg": 1.991, "v2elintim": 1.645},
        {"year": 2017, "v2elirreg": 1.991, "v2elintim": 1.645},
        {"year": 2018, "v2elirreg": 1.991, "v2elintim": 1.645},
        {"year": 2019, "v2elirreg": 1.991, "v2elintim": 1.645},
        {"year": 2020, "v2elirreg": 1.945, "v2elintim": 2.128},
        {"year": 2021, "v2elirreg": 1.181, "v2elintim": 2.136},
        {"year": 2022, "v2elirreg": 1.302, "v2elintim": 2.136},
        {"year": 2023, "v2elirreg": 1.302, "v2elintim": 2.136},
        {"year": 2024, "v2elirreg": 1.302, "v2elintim": 2.136},
    ],
}


