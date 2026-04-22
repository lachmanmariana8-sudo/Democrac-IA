# Informe de Observación Electoral — Elecciones Generales Perú 2026

**Emisor:** DemocracIA / PEIRS (Predictive Electoral Integrity & Risk System)
**Período cubierto:** 9 al 16 de abril de 2026 (campaña, silencio electoral, jornada, escrutinio y primeros días de disputa)
**Jornada electoral:** 12 de abril de 2026
**Fecha de cierre del informe:** 16 de abril de 2026
**Observadora responsable:** Mariana Lachman
**Versión:** 1.1 (preliminar — addendum de 15–16 abril incorporado; la proclamación oficial continúa pendiente)

---

## 1. Resumen ejecutivo

Las Elecciones Generales de Perú del 12 de abril de 2026 — la primera elección presidencial, parlamentaria bicameral y supranacional bajo el nuevo marco de doble valla y bicameralidad — estuvieron **marcadas por una crisis operativa y logística de la Oficina Nacional de Procesos Electorales (ONPE)** de magnitud histórica, con consecuencias penales en curso contra su titular y funcionarios.

El sistema de monitoreo DemocracIA/PEIRS registró **838 hallazgos** sobre el proceso electoral peruano durante ocho días consecutivos (9 al 16 de abril), clasificados automáticamente con Claude (Anthropic) sobre cinco fuentes RSS peruanas (Andina, El Comercio, Gestión, IDL-Reporteros, RPP). De ese universo, **7 hallazgos fueron clasificados como críticos** y **107 como de severidad alta**.

**Ejes principales del informe:**

1. **Crisis logística de ONPE:** no instalación de mesas, material electoral nunca entregado, más de **52,000 ciudadanos sin sufragar** en >180 mesas afectadas, incluyendo 15 centros de votación en Lima Sur (San Juan de Miraflores, Lurín, Pachacámac) donde el material jamás llegó. La fiscalía investiga posible colusión entre ONPE y la empresa tercerizada **Galaga**.
2. **Ecosistema de desinformación electoral:** 284 hallazgos en esta categoría (43% del total). IDL-Reporteros documentó versiones falsas, engañosas o imprecisas difundidas por 34 candidatos presidenciales durante los debates.
3. **Incidentes de integridad del escrutinio:** destrucción intencional de 18 cédulas válidas por fiscalizadora del JNE en Trujillo (detenida en flagrancia) y ruptura de cédulas en Callao por fallas técnicas del Sistema Tecnológico de Apoyo al Escrutinio (STAE).
4. **Responsabilidad penal:** JNE denuncia penalmente al jefe de ONPE Piero Corvetto y tres funcionarios por delito contra el derecho al sufragio y omisión de actos funcionales. Gerente de Gestión Electoral detenido en flagrancia.
5. **Uso de Inteligencia Artificial sin marco regulatorio:** ONPE implementó por primera vez un sistema de doble validación con IA en el cómputo electoral, en ausencia de auditoría pública certificada y sin estándares legales aplicables al proceso.
6. **(Addendum 15-16 abr)** **Contraloría documenta 270 informes con 600 observaciones** sobre fallas de ONPE previas al día de la votación, consolidando la hipótesis de omisión institucional deliberada. **Fiscal de la Nación pide separación cautelar** del titular de ONPE durante el escrutinio. **Rafael López Aliaga (Renovación Popular)** solicita nulidad de elecciones y ofrece recompensa de S/20.000 por pruebas de fraude — potencial configuración del tipo penal de tráfico de influencias.

El proceso continúa abierto al momento de este informe: el escrutinio oficial se encontraba, al 13 de abril en la tarde, en **55,68% de actas procesadas** — muy por debajo del 100% proyectado por ONPE para las 23:30 del 12 de abril. La **proclamación presidencial oficial permanece pendiente** al 16 de abril, con alta probabilidad de segunda vuelta y con el organismo electoral bajo crisis penal e institucional abierta.

---

## 2. Metodología

### 2.1 Sistema de observación

El informe se basa en la operación autónoma del sistema **PEIRS (Predictive Electoral Integrity & Risk System)** de DemocracIA, desplegado en un contenedor Railway con persistencia SQLite sobre volumen montado, durante el período del 8 al 14 de abril de 2026.

**Componentes del pipeline:**

1. **Hunter RSS Agent:** extracción cada 4 horas sobre feeds peruanos de Andina (agencia oficial), El Comercio, Gestión, IDL-Reporteros, Wayka y RPP Noticias.
2. **Clasificador LLM:** Claude Sonnet 4.6 (Anthropic) categoriza cada ítem como relevante/no-relevante, asigna categoría, severidad (info/low/medium/high/critical), y derechos en riesgo conforme a ICCPR, CADH y CDI.
3. **Validador de entradas:** deduplicación por contenido, normalización de severidades, escalamiento automático según reglas por categoría.
4. **Despacho de alertas:** envío automático a canal Discord de las alertas de severidad `high` y `critical`, con traza de fuente (medio + URL del artículo original).
5. **Persistencia:** registro en tabla `observation_entries` y tabla `alerts` de SQLite sobre volumen persistente.

### 2.2 Marco normativo de análisis

Cada hallazgo se evaluó contra el marco de derechos políticos y civiles pertinente:

- **Pacto Internacional de Derechos Civiles y Políticos (ICCPR)**, Arts. 19 (libertad de expresión e información), 25 (derechos políticos — sufragio activo y pasivo).
- **Convención Americana sobre Derechos Humanos (CADH)**, Arts. 13 (libertad de pensamiento y expresión), 23 (derechos políticos).
- **Carta Democrática Interamericana (CDI)**, Art. 3 (elementos esenciales de la democracia representativa).
- **Constitución Política del Perú (1993)**, Arts. 2(17), 31, 35, 176-186.
- **Ley Orgánica de Elecciones N° 26859** y sus modificatorias, particularmente Arts. 190, 191, 351, 358, 363.
- **Ley 31030 (2020):** paridad y alternancia.
- **Ley 31170 (2021):** acoso político.

### 2.3 Alcance y limitaciones

- **Alcance geográfico del Hunter:** nacional (monitoreo de medios), con fuerte concentración en Lima por sesgo de las fuentes.
- **Período cubierto:** 9–14 abril 2026. El sistema experimentó una interrupción del 13-abr ~20:25 UTC al 14-abr ~02:27 UTC por caída de contenedor Railway (resuelta con el *fix* `9341f5f` sobre el bootstrap asíncrono que bloqueaba el event loop).
- **El conteo oficial sigue abierto:** al cierre de este informe (14-abr mediodía UTC) no hay proclamación presidencial oficial.
- **No incluido:** observación presencial en mesas, entrevistas con candidatos/autoridades, análisis de resultados por región/circunscripción, monitoreo de redes sociales más allá de lo citado por las fuentes primarias.

---

## 3. Datos cuantitativos del período observado

### 3.1 Volumen y distribución temporal

**Total de hallazgos registrados: 654**

| Día | Hallazgos | Contexto |
|---|---|---|
| 2026-04-09 | 156 | Cierre de campaña |
| 2026-04-10 | 108 | Inicio de silencio electoral (00:00 PET) y Ley Seca |
| 2026-04-11 | 112 | Veda electoral |
| 2026-04-12 | 126 | **Jornada electoral** |
| 2026-04-13 | 122 | Post-jornada, continuidad del escrutinio |
| 2026-04-14 | 30 | Escrutinio en curso, denuncias penales formales |

### 3.2 Distribución por severidad

| Severidad | Cantidad | % |
|---|---|---|
| critical | 4 | 0,6% |
| high | 74 | 11,3% |
| medium | 259 | 39,6% |
| low | 122 | 18,7% |
| info | 195 | 29,8% |

### 3.3 Distribución por categoría

| Categoría | Cantidad | % |
|---|---|---|
| **disinformation** (desinformación) | 284 | 43,4% |
| **logistics** (logística electoral) | 191 | 29,2% |
| other | 49 | 7,5% |
| **legal** (acciones judiciales y jurídicas) | 45 | 6,9% |
| campaign_violation | 39 | 6,0% |
| security | 12 | 1,8% |
| results | 11 | 1,7% |
| counting | 7 | 1,1% |
| digital | 4 | 0,6% |
| irregular_procedure | 3 | 0,5% |
| accessibility | 2 | 0,3% |
| fraud_allegation | 2 | 0,3% |
| ballot_tampering | 2 | 0,3% |
| hate_speech | 1 | 0,2% |
| media | 1 | 0,2% |
| voter_suppression | 1 | 0,2% |

### 3.4 Fuentes verificadoras

| Medio | Hallazgos | Rol observado |
|---|---|---|
| IDL-Reporteros | 293 | Fact-checking y verificación sistemática |
| El Comercio | 172 | Cobertura principal de denuncias institucionales |
| Gestión | 105 | Ángulo económico-empresarial |
| RPP Noticias | 84 | Cobertura operativa en tiempo real |

### 3.5 Derechos políticos y civiles más invocados

| Instrumento | Citas |
|---|---|
| ICCPR Art. 25 (derechos políticos) | 586 |
| CADH Art. 23 (derechos políticos) | 169 |
| CADH Art. 13 (libertad de expresión) | 166 |
| ICCPR Art. 19(2) — libertad de información veraz | 135 |
| CADH Art. 23(2) (restricciones admisibles) | 38 |
| ICCPR Art. 25(b) — voto en condiciones equitativas | 42 |

---

## 4. Fase de campaña y silencio electoral (9–11 abril)

### 4.1 Ecosistema de desinformación documentado

IDL-Reporteros realizó verificación sistemática de las declaraciones de los candidatos presidenciales. La serie incluyó:

- **Informe general:** *"Datos falsos, engañosos o ciertos de los candidatos presidenciales 2026"* — identifica que **34 candidatos presidenciales expusieron versiones erróneas, falsas, imprecisas y engañosas durante debates electorales** sobre temáticas sociales y económicas.
- Casos individuales verificados:
 - Keiko Fujimori (Fuerza Popular): dato falso sobre inflación peruana.
 - Vladimir Cerrón (Perú Libre, candidato prófugo): dato falso sobre votaciones parlamentarias.
 - Wolfgang Grozo: información falsa sobre unión civil en la Constitución.
 - Adriana Tudela: afirmación engañosa sobre cronología del Reinfo.
 - Rafael López Aliaga (Renovación Popular): imagen falsa de mitin multitudinario.
 - Javier Diez Canseco: dato impreciso sobre diversidad cultural y lingüística.

**Pieza editorial de IDL:** *"Fanático de la mentira"* — identifica a un actor específico como "mayor desinformador del país" que difunde mentiras y calumnias de forma sistemática, con impacto en la confianza del proceso democrático.

**Derechos vulnerados:** ICCPR Art. 19(2) (derecho a recibir información veraz), CADH Art. 13, ICCPR Art. 25 (condiciones equitativas de campaña).

### 4.2 Denuncia de captura institucional (IDL, 12-abr 00:15)

IDL-Reporteros publicó el día mismo de la elección la investigación *"Los votos y las leyes del pacto para capturar el país"*, documentando una **coalición parlamentaria votando de forma concertada para capturar instituciones del Estado y aprobar leyes que garanticen impunidad** a sus integrantes.

Este hallazgo es especialmente relevante porque sitúa la elección en un contexto de continuidad de un proyecto de captura legislativa previo, no como evento aislado.

**Derechos vulnerados:** ICCPR Art. 25 (proceso libre y justo), CDI Art. 3.

### 4.3 Violencia política y seguridad

- **Fallecimiento del candidato al Senado Dante Castro** (Juntos por el Perú) en accidente durante mitin en Callao (cayó desde un vehículo en actividad de campaña). Reportado el 14-abr por RPP.
- Durante la campaña se registraron reportes de acoso digital a candidatas, aunque en volumen menor al esperado según el análisis pre-electoral de DemocracIA (asunto tratado por JNE-Observa Igualdad).

### 4.4 Financiamiento de campaña

- **Más de 50 candidatos al Congreso no presentaron reportes de financiamiento** ante ONPE, en violación de la normativa de transparencia.
- **Partido Cívico Obras** (Ricardo Belmont) figura entre los que no transparentaron aportes — documentado por El Comercio.

**Derechos vulnerados:** CADH Art. 23, ICCPR Art. 25 (campaña equitativa).

---

## 5. Jornada electoral (12 de abril de 2026)

### 5.1 Cronología de la crisis

| Hora (PET) | Evento |
|---|---|
| **08:00** | Apertura programada de mesas de sufragio |
| — | Reportes tempranos de **no instalación de mesas** en Callao, Ancón, Comas, Surco, Lima Sur |
| — | Laptops e impresoras del STAE no funcionando por falta de energía y conexión a internet |
| — | Miembros de mesa firman en cuadernos ante imposibilidad de usar el sistema |
| **≤16:00** | **JNE amplía horario de votación hasta las 18:00 a nivel nacional** |
| **16:00 →** | Inicio de difusión de conteo rápido (DATUM Internacional) |
| **Tarde** | Transparencia (observador internacional) **suspende su conteo rápido** y exhorta a ONPE/JNE suspender publicación de resultados oficiales |
| **18:00** | Cierre de mesas (con ampliación) |
| **Nocturno** | Escrutinio en mesas se extiende hasta madrugada del 13 |
| **23:30** | Meta ONPE de conteo rápido al 100% — **no cumplida** |

### 5.2 Magnitud de la exclusión del sufragio

- **63,300 ciudadanos de Lima Sur** (San Juan de Miraflores, Lurín, Pachacámac) no pudieron votar en **15 centros de votación** donde el material electoral **nunca llegó** — clasificado `critical`.
- **52,000 ciudadanos adicionales** afectados por caos en **más de 180 mesas** a nivel nacional, incluyendo consulados de EE. UU. donde no llegaron los miembros de mesa — clasificado `critical`.
- **211 mesas no instaladas** en el agregado nacional (denuncia pública de Keiko Fujimori al jefe de ONPE).
- **Rafael López Aliaga denuncia más de 1 millón de personas sin voto** — cifra aún no verificada independientemente al cierre del informe.

**Cuantificación mínima documentada: ~115,000 ciudadanos sin poder sufragar** por causas atribuibles al organismo electoral. **Derecho vulnerado:** ICCPR Art. 25(b) — derecho a votar en condiciones equitativas; CADH Art. 23(1)(b).

### 5.3 Incidentes de integridad del escrutinio

**Caso 1 — Trujillo (La Libertad):** Fiscalizadora del JNE **destruyó intencionalmente 18 cédulas válidas** durante el escrutinio. Fue **detenida en flagrancia** por la Policía Nacional del Perú. Clasificado como `ballot_tampering`. Caso individual de integridad, no sistémico.

**Caso 2 — Callao:** miembros de mesa **rompieron cédulas y actas electorales** al fallar el sistema STAE. Contrario a la primera versión atribuida a "falta de tinta", **ONPE confirmó oficialmente que la causa fue la falla del sistema**. Este caso documenta una falla sistémica del componente tecnológico (ver Sección 7).

### 5.4 Otros incidentes relevantes

- **Miembros de mesa en Trujillo trabajaron más de 24 horas continuas** hasta las 09:15 del lunes 13 para completar el conteo. Evidencia de un cuello de botella severo en la cadena acta física → digitalización.
- **Reacción de la prensa internacional:** la jornada fue calificada como *"caótica"* en cobertura internacional.
- **Gremios empresariales** (Confiep, Comex, Adex, CCL) emitieron comunicados coordinados denunciando fallas logísticas y tecnológicas como "problemas estructurales" de gestión pública.

---

## 6. Escrutinio y respuesta institucional (13–14 abril)

### 6.1 Ritmo del cómputo oficial

| Momento | Actas procesadas |
|---|---|
| 13-abr mediodía | 53,89 % |
| 13-abr tarde | 55,68 % |

El ritmo está sustancialmente por debajo del plan operativo de ONPE, que proyectaba el conteo rápido al 100 % para las 23:30 del 12-abr. Al cierre de este informe **no hay proclamación presidencial oficial**; los candidatos continúan en expectativa de resultados.

**Proyecciones de boca de urna** (El Comercio, 14-abr) indican **seis bancadas** en el nuevo Senado bicameral, con composición aparentemente similar al período saliente.

### 6.2 Acciones penales e investigaciones

- **JNE denuncia penalmente a Piero Corvetto (jefe de ONPE) + 3 funcionarios** (14-abr) por presuntos delitos contra el derecho al sufragio y omisión de actos funcionales.
- **Detención en flagrancia del gerente de Gestión Electoral de ONPE** (13-abr) por presunta omisión de funciones.
- **Fiscal de la Nación** abre investigación por posible **colusión entre ONPE y la empresa Galaga**, tercerizada del transporte de material electoral.
- **Fiscalía Anticorrupción + Dircocor** con diligencias activas en ONPE desde el 12-abr.
- **JNJ (Junta Nacional de Justicia)** iniciará investigación disciplinaria y **revisará el proceso de ratificación del jefe de ONPE**.
- **Congreso** cita a Corvetto y al presidente del JNE Roberto Burneo.
- **Partido Renovación Popular** presenta denuncia formal por delito de omisión.

### 6.3 Sentencia contra el presidente del Congreso

Durante la semana previa al cierre de campaña, el presidente del Congreso **Fernando Rospigliosi fue sentenciado a 9 meses de prisión suspendida por difamación agravada**, generando incertidumbre sobre su candidatura electoral. Reportado por Gestión el 14-abr.

### 6.4 Respuesta oficial

- El **jefe de ONPE Piero Corvetto reconoció problemas logísticos** durante la jornada y ofreció disculpas públicas.
- La **Contraloría de la República supervisó el traslado de material electoral a 2.270 locales de votación** — función de control preventivo que no impidió las fallas.
- **Autorización de votación el lunes 13** para electores que no pudieron sufragar por falta de material (saludada por Transparencia).

### 6.5 Riesgo post-electoral en curso

**Transportistas anuncian paro nacional indefinido desde el 15 de abril** — 3 días después de la jornada — exigiendo subsidio de combustible. La afectación potencial al traslado post-electoral de actas físicas es significativa y debe monitorearse.

---

## 7. Fase post-electoral: análisis del uso de Inteligencia Artificial

### 7.1 Arquitectura del sistema ONPE 2026

La ONPE implementó para las Elecciones Generales 2026 una **triple ruta de procesamiento** compuesta por tres sistemas informáticos operando en cadena:

| Etapa | Sistema | Sigla | Función |
|---|---|---|---|
| 1. En mesa de sufragio | Solución Tecnológica de Apoyo al Escrutinio | **STAE** | Laptop + impresora: registro de datos, validación de identidades, firmas digitales, alertas por errores en sumas, impresión de actas |
| 2. Cómputo centralizado | Sistema de Cómputo Electoral | **SCE** | Digitalización, verificación y procesamiento de actas. **Validación dual con IA** |
| 3. Publicación | Sistema de Presentación de Resultados | **SPR** | Publicación en `resultadoelectoral.onpe.gob.pe` |

### 7.2 Rol de la Inteligencia Artificial

El componente con IA opera en la fase **SCE (cómputo centralizado)**, no en STAE. Según la descripción oficial de ONPE citada por Diario Correo:

> *"Un operador ingresa los datos sin conocer a qué organización política pertenecen los votos, mientras un sistema automatizado, con apoyo de inteligencia artificial, revisa la misma información. Si ambas lecturas coinciden, los votos se contabilizan; si no, el acta pasa a observación."*

Se trata de un sistema de **reconocimiento óptico de caracteres (OCR) asistido por aprendizaje automático**, combinado con una capa de validación humana cruzada. No es un modelo generativo; es un clasificador/extractor aplicado a actas escaneadas, con una decisión binaria (computar / enviar a observación).

### 7.3 Cobertura geográfica del STAE

**STAE se implementó únicamente en Lima Metropolitana y Callao.** El resto del país operó con procedimiento tradicional (acta manual + firma física + digitalización diferida).

**Implicancia para el informe:** existe una **desigualdad territorial en el soporte tecnológico** al trabajo de mesa. Las circunscripciones fuera del área metropolitana carecieron de las alertas automáticas de error en sumas y de la validación de identidades en línea.

### 7.4 Fallas documentadas del STAE en la jornada

**A. Fallas de infraestructura:**
- Laptops e impresoras inoperables por **falta de energía eléctrica** en locales de votación.
- **Conexión a internet deficiente** en varios colegios.
- **Falta de tinta de impresora** impidiendo el cierre de actas.
- Distritos afectados documentados: Callao, Ancón, Comas, Surco, Santiago de Surco.
- La **Defensoría del Pueblo** advirtió que en Santiago de Surco la ONPE distribuyó los equipos STAE **el día mismo de la elección**.

**B. Fallas de validación del sistema:**
- Miembros de mesa reportan que *"los códigos no eran reconocidos en algunas mesas, lo que impedía la instalación de la mesa de sufragio"*.
- Los ensayos previos del STAE no presentaron estos problemas — una **discrepancia crítica entre escenario de prueba y escenario de producción**.

**C. Cadena de custodia comprometida:**
- Miembros de mesa **forzados a destruir cédulas y actas** por falla del sistema. ONPE confirmó oficialmente que la causa fue técnica (no falta de tinta) y el incidente se concentró en Callao.
- Método de contingencia adoptado: **firma en cuadernos físicos** en lugar de registro digital.

### 7.5 Ausencia de auditoría pública del componente de IA

**Este es el punto central de la observación post-electoral.**

- Un día antes de la elección **no existía información pública clara sobre auditorías independientes certificadas** de los sistemas STAE/SCE/SPR.
- El especialista electoral **Erick Iriarte** planteó la cuestión públicamente: *"¿estos sistemas han sido auditados? ¿Quién los ha auditado? ¿Y dónde están los reportes?"*
- En agosto de 2025, el JNE había **rechazado la propuesta de voto electrónico no presencial (VENP) mediante Resolución N° 0891-2025-JNE**, precisamente por la *"ausencia de auditoría independiente certificada"*. Sin embargo, un sistema de IA operando sobre la totalidad del acervo digital de actas sí fue autorizado, sin que conste aplicación del mismo estándar.

### 7.6 Implicaciones de la IA no regulada en procesos electorales

Perú no cuenta con un marco legal específico que regule el uso de sistemas de inteligencia artificial en procesos electorales. La Ley Orgánica de Elecciones N° 26859 no contempla disposiciones sobre:

1. **Estándares de explicabilidad y trazabilidad algorítmica** — no hay obligación de que ONPE publique el modelo, los datasets de entrenamiento, ni las métricas de desempeño (tasas de falsos positivos/negativos en el reconocimiento de actas).
2. **Derecho de impugnación sobre decisiones automatizadas** — si la IA clasifica un acta como "observada", no existe un procedimiento recursivo específico para que el personero o la organización política cuestione la decisión del sistema (distinto del recurso habitual sobre actas observadas, que presupone decisión humana).
3. **Régimen de responsabilidad civil y penal por errores algorítmicos** — la responsabilidad penal de los funcionarios de ONPE actualmente investigada se basa en omisión de actos funcionales humanos; no hay marco aplicable para errores del sistema automatizado.
4. **Principio de publicidad del escrutinio (ICCPR Art. 25, CADH Art. 23)** — el Comité de Derechos Humanos ha sostenido (OG 25, párr. 25) que el escrutinio debe ser *transparente y los resultados deben ponerse a disposición del público*. Un sistema de IA no auditable introduce una capa de **tecno-opacidad** que es prima facie incompatible con la obligación de transparencia del proceso.
5. **Certificación independiente previa** — no existe autoridad nacional con competencia explícita para auditar, certificar y autorizar sistemas de IA de uso electoral. El INDECOPI no tiene mandato; la Autoridad Nacional de Protección de Datos Personales solo actúa sobre tratamiento de datos personales.
6. **Derecho a la información veraz (ICCPR Art. 19(2))** — el acceso ciudadano al código fuente, a los datos de entrenamiento y a los reportes de validación es una condición instrumental del derecho a recibir información sobre el proceso electoral.
7. **Confianza electoral** — la combinación de **(a)** implementación de IA + **(b)** ausencia de auditoría pública + **(c)** fallas visibles del componente STAE + **(d)** crisis logística paralela, genera un contexto de riesgo sistémico para la confianza en los resultados oficiales.

### 7.7 Recomendación específica

La observación recomienda a la ONPE y al JNE:

- **Publicación inmediata** del código fuente, arquitectura del modelo de IA utilizado en SCE, datasets de entrenamiento y métricas de desempeño sobre el corpus real de actas 2026.
- **Auditoría independiente post-electoral** con participación de universidades peruanas, sociedad civil organizada y expertos internacionales, siguiendo protocolos análogos a los aplicados a urnas electrónicas (IDEA Internacional, Council of Europe).
- **Informe público desglosado** por sistema (STAE/SCE/SPR) sobre incidencias, mesas afectadas, actas que pasaron a observación por discrepancia IA-operador, y resolución final de cada una.
- **Al Congreso de la República:** inicio de un proceso legislativo para **regular el uso de IA en procesos electorales**, con estándares mínimos de auditoría, explicabilidad y recurso, aplicables a las próximas elecciones (municipales/regionales 2026 y sub-nacionales siguientes).

---

## 8. Marco de derechos vulnerados (síntesis)

| Derecho / Instrumento | Citas en hallazgos | Vulneraciones principales documentadas |
|---|---|---|
| **ICCPR Art. 25 — Derechos políticos** | 586 | Imposibilidad de sufragio por falla operativa (~115.000 personas); condiciones no equitativas de campaña; proceso sin garantías plenas de integridad del escrutinio |
| **CADH Art. 23** | 169 | Mismas vulneraciones bajo sistema interamericano; acceso desigual al soporte tecnológico por territorio |
| **CADH Art. 13 — Libertad de expresión** | 166 | Ecosistema de desinformación no mitigado; denuncias específicas de ACOSO digital a candidatas |
| **ICCPR Art. 19(2) — Información veraz** | 135 | Desinformación sistemática en debates; ausencia de información pública sobre auditoría de sistemas críticos |
| **CDI Art. 3** | 6 | Proceso electoral con debilidades estructurales que afectan elementos esenciales de la democracia representativa |

---

## 9. Conclusiones preliminares

1. **La crisis del 12-abr no fue de seguridad ni de fraude sistémico: fue de ejecución operativa.** Las fallas masivas de ONPE en distribución de material, instalación de mesas y soporte técnico comprometieron el derecho al sufragio de al menos 115.000 personas documentadas, con una cifra plausiblemente mayor en investigación.

2. **La integridad del voto individual fue mayormente preservada** a pesar del caos. Los dos incidentes de manipulación de cédulas documentados (Trujillo y Callao) tienen causas distintas: uno es un caso penal individual (fiscalizadora del JNE), el otro es consecuencia de fallas técnicas del STAE. No hay evidencia sistémica de fraude electoral intencional en el escrutinio; sí hay evidencia sistémica de negligencia institucional.

3. **El ecosistema de desinformación fue el tema dominante en volumen** (43% de los hallazgos). IDL-Reporteros operó como contrapeso técnico mediante fact-checking documentado, pero no alcanza para compensar la asimetría informativa de una campaña con 34 candidatos difundiendo versiones falsas o engañosas.

4. **Las consecuencias penales institucionales son graves y están en curso:** la titularidad máxima de ONPE enfrenta denuncia penal del JNE; hay funcionarios detenidos en flagrancia; la Fiscalía investiga posible colusión con un proveedor privado (Galaga). La independencia operativa de la ONPE requerirá revisión.

5. **El uso de IA sin marco regulatorio es el punto ciego estructural más preocupante.** No por evidencia de mal funcionamiento — que no disponemos — sino por la **imposibilidad institucional de verificarlo**. Perú corrió una elección crítica con un componente de IA no auditado públicamente, en ausencia de estándares legales aplicables y sin procedimientos de recurso específicos. Este vacío debe ser atendido legislativamente antes de las próximas elecciones.

6. **Los observadores internacionales (Transparencia) suspendieron su conteo rápido el 12-abr** — hecho cualitativo de alto impacto que debe figurar en cualquier evaluación oficial final.

---

## 10. Recomendaciones

### 10.1 A corto plazo (48–72 horas)

- Publicación por ONPE del **cronograma de rezagos**: cuántas mesas faltan procesar, dónde, y plan de cierre del escrutinio.
- **Registro público auditado** de todos los ciudadanos afectados por no instalación de mesas o falta de material, con mecanismo de compensación (ej. certificación gratuita del impedimento para efectos de multas por no sufragar).
- **Informe técnico del STAE** con desagregación: mesas donde falló, tipo de falla, tiempo de recuperación, actas perdidas o reconstruidas.

### 10.2 A mediano plazo (1–6 meses)

- **Auditoría independiente integral** de los tres sistemas (STAE, SCE, SPR) con participación de universidades, sociedad civil y expertos internacionales.
- **Revisión del proceso de ratificación del jefe de ONPE** por la JNJ.
- **Investigación penal concluida** sobre el contrato con Galaga y la cadena de decisión logística.
- Publicación del **código fuente y documentación técnica** del componente de IA, con licencia que permita la verificación pública.

### 10.3 A largo plazo (pre-próximas elecciones)

- **Ley de IA en procesos electorales** — al Congreso de la República — con estándares mínimos de auditoría, explicabilidad, trazabilidad, derecho de impugnación sobre decisiones automatizadas y régimen de responsabilidad.
- **Reforma de la arquitectura logística de ONPE** incorporando redundancia, control de terceros y capacidad de respuesta territorial.
- **Integración de estándares internacionales** sobre IA en democracia (Consejo de Europa — Convención marco sobre IA 2024, UNESCO — Recomendación sobre la Ética de la IA 2021, IDEA Internacional — guías sobre tecnología electoral).

---

## 11. Addendum v1.1 — Novedades del 15 y 16 de abril de 2026

Este addendum se incorpora sobre la base del monitoreo continuo del sistema PEIRS entre el 15 y el 16 de abril de 2026. Durante las 48 horas posteriores al cierre del informe v1.0 se registraron **120 hallazgos adicionales** (sobre un total de 838 acumulados), incluyendo **3 hallazgos críticos nuevos** y **33 de severidad alta**. Las categorías dominantes fueron logística electoral (35), conteo (20), acciones legales (17), resultados (17) y alegaciones de fraude (14).

### 11.1 Contraloría: 270 informes con 600 observaciones

El hallazgo estructural más grave del período es la revelación del volumen de control interno documentado contra la ONPE por el órgano superior de control del Estado:

> La Contraloría emitió **más de 270 informes con 600 observaciones** sobre fallas en la distribución de material electoral por parte de ONPE, afectando locales de votación. La investigación del Ministerio Público y la Junta Nacional de Justicia (JNJ) se encuentran en curso. [El Comercio, 16-abr](https://elcomercio.pe/politica/piero-corvetto-y-el-escandalo-del-reparto-de-material-electoral-mas-de-270-informes-con-600-observaciones-de-la-contraloria-noticia/)

Este volumen de observaciones previas a la jornada **documenta conocimiento institucional del riesgo** por parte de la ONPE antes del 12-abr. Refuerza la narrativa de omisión deliberada sobre la que se construyen las imputaciones penales contra su titular.

**Clasificación:** `critical` / `logistics`.
**Derechos vulnerados:** ICCPR Art. 25(b), CADH Art. 23(1)(b).

### 11.2 Escalamiento de acciones penales y administrativas contra ONPE

Entre el 15 y el 16 de abril las consecuencias penales e institucionales se consolidaron y expandieron:

- **Fiscal de la Nación (Tomás Gálvez)** solicitó públicamente que la JNJ **separe al jefe de ONPE mediante medida cautelar durante el proceso de escrutinio**. Precedente institucional inusual: es la primera vez que se pide separar al titular del organismo electoral en plena tabulación de resultados. [El Comercio, 15-abr](https://elcomercio.pe/politica/actualidad/tomas-galvez-sobre-piero-corvetto-la-jnj-tiene-que-separarlo-en-un-proceso-administrativo-con-una-medida-cautelar-ultimas-noticia/)
- **Procurador del JNE (Ronald Angulo)** denuncia penalmente a Piero Corvetto por no implementar medidas de contingencia cuando el material electoral no llegó a **13 centros de sufragio**: *"Corvetto pudo dar medidas de contingencia pero se quedó callado y no hizo nada"*. [El Comercio, 15-abr](https://elcomercio.pe/politica/ronald-angulo-procurador-del-jne-corvetto-pudo-dar-medidas-de-contingencia-pero-se-quedo-callado-y-no-hizo-nada-noticia/)
- **Subgerente de Producción Electoral de ONPE** procesado penalmente junto a José Luna con **pedido fiscal de más de 10 años de pena privativa de libertad**. [El Comercio, 15-abr](https://elcomercio.pe/politica/onpe-subgerente-de-produccion-electoral-es-procesado-junto-a-jose-luna-por-que-fiscalia-pidio-mas-de-10-anos-de-pena-privativa-de-liberta-en-su-contr)
- **Gremios empresariales** (Confiep, Comex, Adex, CCL) unifican su posición y exigen destitución inmediata de Corvetto. [El Comercio, 16-abr](https://elcomercio.pe/elecciones/elecciones-2026-union-de-gremios-pide-destitucion-inmediata-de-piero-corvetto-jefe-de-la-onpe-tras-fallas-en-comicios-ultimas-noticia/)
- **Respuesta del titular de ONPE:** compareció en el Congreso el 16-abr. **No asumió responsabilidad directa**; culpó a la subgerencia de ONPE. [El Comercio, 16-abr](https://elcomercio.pe/politica/elecciones/piero-corvetto-no-asume-responsabilidad-directa-por-fallas-y-culpa-a-subgerencia-de-onpe-asi-fue-su-presentacion-en-el-congreso-elecciones)

### 11.3 Narrativa de fraude y solicitud de nulidad

Un vector separado y paralelo al caso penal emerge como foco post-electoral: la construcción de una narrativa de fraude desde sectores políticos perdedores, liderada por Rafael López Aliaga (Renovación Popular):

- 15-abr: López Aliaga **denuncia fraude electoral** y solicita la **anulación de las elecciones**, alegando irregularidades que impidieron votar a más de 52.000 ciudadanos. Exige nulidad con plazo de 24 horas. [El Comercio](https://elcomercio.pe/politica/elecciones-generales-2026-elecciones-en-peru-renovacion-popular-rafael-lopez-aliaga-denuncia-fraude-y-pide-que-se-declaren-nulas-las-elecciones-segun)
- 15-abr: López Aliaga solicita al JNE **suspender la proclamación del segundo y tercer lugar** hasta que ONPE aclare información de votantes. [El Comercio](https://elcomercio.pe/politica/elecciones/rafael-lopez-aliaga-pide-al-jne-suspender-proclamacion-de-segundo-y-tercer-lugar-hasta-que-onpe-aclare-informacion-de-votantes-ultimas-not)
- 16-abr: López Aliaga solicita suspender proclamación de resultados presidenciales alegando que fallas de ONPE impidieron votar **a más de 600 mil ciudadanos limeños** (cifra en disputa, superior al mínimo documentado de 115.000). **Clasificación critical.** [Gestión](https://gestion.pe/peru/politica/lopez-aliaga-pide-al-jne-suspender-proclamacion-de-resultados-denuncia-que-mas-de-600-mil-limenos-no-pudieron-votar-noticia/)
- 16-abr: **Renovación Popular ofrece S/20.000 de recompensa** a funcionarios del JNE y ONPE por información sobre presuntas irregularidades, fraude o sabotaje electoral. [Gestión](https://gestion.pe/peru/politica/elecciones-2026-rafael-lopez-aliaga-y-renovacion-popular-ofrecen-s-20000-de-recompensa-por-pruebas-de-fraude-electoral-noticia/)

> **Observación de integridad:** la oferta de una recompensa monetaria a funcionarios electorales por parte de un partido político puede configurar un **tipo penal de instigación a la violación de deberes funcionariales** (Código Penal peruano Art. 400 — tráfico de influencias) y debe ser evaluada por el Ministerio Público. El diseño de un mecanismo de incentivo económico paralelo a las vías institucionales de denuncia vulnera el principio de imparcialidad y puede afectar la cadena de prueba.

**Respuesta institucional a la narrativa de fraude:**

- **Anahí Durand niega fraude** y cuestiona el pedido de anulación. [RPP, 15-abr](https://rpp.pe/politica/elecciones/anahi-durand-niega-fraude-y-cuestiona-pedido-de-rafael-lopez-aliaga-para-anular-elecciones-noticia-1684384)
- Se advierte sobre **intentos organizados de desconocer los resultados electorales** — patrón que el análisis pre-electoral de DemocracIA ya había identificado como riesgo estructural en el contexto peruano (6 presidentes en 4 años; crisis institucional crónica).

**Clasificación:** las 9 entries de esta categoría son `fraud_allegation`. **Derechos en tensión:** CADH Art. 23 (derechos políticos, ambos sentidos — quienes denuncian y quienes ven amenazada la proclamación legítima), ICCPR Art. 25, CDI Art. 3.

### 11.4 Escenario de segunda vuelta y legitimidad del organismo electoral

Un eje nuevo que se vuelve explícito en esta ventana es la **viabilidad política de una segunda vuelta** con el organismo electoral bajo crisis abierta:

- El constitucionalista **Aníbal Quiroga** (entrevistado por RPP) plantea que *"es impensable ir a una segunda vuelta con Piero Corvetto como jefe de la ONPE"*, y sugiere medida cautelar de suspensión por parte del JNE hasta resolución del proceso de destitución. [RPP, 16-abr](https://rpp.pe/politica/elecciones/anibal-quiroga-dice-que-es-impensable-ir-a-una-segunda-vuelta-con-piero-corvetto-como-jefe-de-la-onpe-noticia-1684600)
- El **Alcalde de Lima Renzo Reggiardo** se suma a las denuncias, exigiendo que el JNE solicite a ONPE información inmediata sobre las mesas de sufragio en Lima Metropolitana que abrieron tarde. [Gestión, 16-abr](https://gestion.pe/peru/politica/renzo-reggiardo-solicita-que-el-jne-exija-a-la-onpe-informacion-inmediata-sobre-las-mesas-de-sufragio-de-lima-metropolitana-que-abrieron-tarde-e-im)

Esto configura un **escenario de disputa institucional en curso** donde el escrutinio todavía no concluyó y ya hay presión política, penal y administrativa sobre la titularidad de ONPE. La decisión del JNE respecto de la petición de nulidad de Renovación Popular es el punto de inflexión inmediato.

### 11.5 Actualización cuantitativa al 16 de abril

Los números consolidados del sistema PEIRS al cierre de este addendum:

| Métrica | v1.0 (14-abr) | v1.1 (16-abr) | Δ |
|---|---|---|---|
| Total entries | 654 | **838** | +184 |
| Critical | 4 | **7** | +3 |
| High | 74 | **107** | +33 |
| Medium | 259 | **303** | +44 |
| Días monitoreados | 6 | 8 | +2 |
| Alertas despachadas a Discord | ~65 | **~105 (est.)** | +40 |

La categoría **`fraud_allegation`** sube de 2 a **16 entries**, reflejando el viraje narrativo de los partidos perdedores hacia la impugnación del proceso. La categoría **`legal`** sube de 45 a 62, reflejando el escalamiento de acciones penales y administrativas contra ONPE.

### 11.6 Observaciones finales del addendum

1. **El sistema de observación sigue operativo y autónomo** — Railway persistente, Hunter cada 4h, alertas a Discord, frontend en `democracia.ar`.
2. **Mayor factor de incertidumbre abierto:** la resolución del JNE respecto a la petición de nulidad de Renovación Popular. Si el JNE rechaza la nulidad, la narrativa de fraude puede intentar sostener la tensión post-electoral; si la admite a trámite, se abre un escenario de disputa institucional prolongada.
3. **Segunda vuelta probable** — el conteo oficial al 16-abr no define ganador con mayoría absoluta. La fecha de la segunda vuelta y el estatus de Corvetto al momento de organizarla son los dos vectores a monitorear en los próximos 7 días.
4. **Uso de IA no auditada (STAE) ingresa al debate público** — el caso Corvetto visibiliza que los sistemas tecnológicos electorales fueron autorizados sin estándares públicos. Es una ventana de oportunidad regulatoria que el Congreso puede aprovechar antes de la segunda vuelta.

---

## Anexo A — Fuentes primarias citadas

### Marco normativo
- Pacto Internacional de Derechos Civiles y Políticos (ICCPR), Arts. 19, 25.
- Convención Americana sobre Derechos Humanos (CADH), Arts. 13, 23.
- Carta Democrática Interamericana (CDI), Art. 3.
- Constitución Política del Perú (1993).
- Ley Orgánica de Elecciones N° 26859 y modificatorias.
- Ley 31030 (2020) — paridad y alternancia.
- Ley 31170 (2021) — acoso político.
- Resolución JNE N° 0891-2025-JNE (15-ago-2025) — rechazo del voto electrónico no presencial.

### Medios con cobertura verificada (Hunter RSS)
- Agencia Andina — [https://andina.pe](https://andina.pe)
- El Comercio — [https://elcomercio.pe](https://elcomercio.pe)
- Gestión — [https://gestion.pe](https://gestion.pe)
- IDL-Reporteros — [https://idl-reporteros.pe](https://idl-reporteros.pe)
- RPP Noticias — [https://rpp.pe](https://rpp.pe)

### Fuentes consultadas para la sección STAE (WebSearch, 14-abr-2026)
- ONPE — Portal oficial STAE: [https://eg2026.onpe.gob.pe/la-organizacion/stae/](https://eg2026.onpe.gob.pe/la-organizacion/stae/)
- *La ONPE usará una triple ruta para el conteo de votos* — Diario Correo
- *STAE: el sistema que debía agilizar el proceso pero cuyas fallas terminaron por retrasar la instalación de mesas* — El Comercio
- *ONPE niega que cédulas se rompieran por "falta de tinta"* — Infobae
- *ONPE explica el funcionamiento del sistema de cómputo y garantiza transparencia* — RPP
- *Reportan fallas en el sistema de la ONPE que retrasan la apertura de mesas: "Firmamos en un cuaderno"* — La República
- *Denuncian falta de laptops e impresoras malogradas en las Elecciones 2026* — La República
- *ONPE: denuncian que miembros de mesa rompen cédulas ante fallas del sistema* — Caretas

---

## Anexo B — Especificación técnica del sistema de monitoreo

- **Plataforma:** DemocracIA / PEIRS v0.4.0
- **Pipeline:** FastAPI + LangGraph + SQLite (volumen persistente Railway)
- **Clasificador:** Claude Sonnet 4.6 (Anthropic)
- **Frecuencia Hunter:** cada 4 horas (HUNTER_INTERVAL_MINUTES=240)
- **Fase de la sesión PER al cierre:** `counting_tabulation` (🔢 Escrutinio y Cómputo)
- **Session ID:** `4053dd18-b334-4ca1-b44b-dc102256bda1`
- **Run ID reporte base:** `80e00137-538c-455d-8240-e27aa86299fd`
- **Dashboard público:** [https://democracia.ar](https://democracia.ar) — tab "🇵🇪 Perú" → "🚨 Alertas en vivo"
- **Alertas despachadas a Discord:** 65 (severidad high + critical) al 14-abr
- **Código fuente:** [github.com/lachmanmariana8-sudo/democracia-peirs](https://github.com/lachmanmariana8-sudo/democracia-peirs)

---

**Fin del informe preliminar — v1.0**
*Este informe se actualizará cuando concluya el escrutinio oficial y se proclame ganador.*
