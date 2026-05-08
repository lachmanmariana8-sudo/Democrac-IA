# DEMOCRAC.IA

## Predictive Electoral Integrity & Risk System

## PEIRS

### DOCUMENTO DE ARQUITECTURA, DIAGNÓSTICO Y ROADMAP DE IMPLEMENTACIÓN

**Versión 2.0  |  Mayo 2026**

**CONFIDENCIAL**

---

> *Este documento sucede a la versión 1.0 (Marzo 2026). Refleja el estado
> de la plataforma al cierre del 4 de mayo de 2026, tras dos meses de
> desarrollo intensivo: del diagnóstico inicial al producto en producción
> con caso de uso real (Perú 2026).*
>
> *Para el público técnico interno, ver el documento hermano
> [PEIRS_Arquitectura_Roadmap.md](PEIRS_Arquitectura_Roadmap.md), que contiene
> el script cronológico de todas las sesiones de trabajo.*

---

## 1. Estado Actual de la Plataforma

### 1.1 Producto en operación

Al cierre de la versión 2.0, DEMOCRAC.IA / PEIRS es una plataforma de
inteligencia electoral en producción, con un caso de uso activo (la
observación de las elecciones generales de Perú 2026, programadas para
el 12 de abril) y arquitectura validada para escalarse a Brasil
(4 de octubre de 2026) y Estados Unidos midterms (3 de noviembre de 2026).

La plataforma combina:

- Una base de conocimiento histórico de cobertura global (V-Dem 1789-2025,
  Freedom House 2013-2025, Perceptions of Electoral Integrity 2012-2023,
  Reporters Without Borders 2025).
- Un sistema de monitoreo en tiempo real (Hunter scheduler) que opera 24/7
  sobre fuentes RSS verificadas, con clasificación automática mediante
  Claude Sonnet 4.6 y deduplicación semántica.
- Un sistema de generación de informes (Elite Report) que produce
  documentos de observación electoral comparables en estructura y rigor a
  los de las misiones internacionales, en minutos en lugar de semanas.
- Un dashboard institucional (democracia.ar) con sala de situación
  específica para Perú 2026 y soporte trilingüe (es/en/pt).

### 1.2 Componentes operativos

| Capa | Componente | Estado |
| --- | --- | --- |
| Inteligencia | Pipeline LangGraph 4 agentes | Operativo |
| Inteligencia | Hunter scheduler 24/7 (4h configurable) | Operativo |
| Inteligencia | Constitucionalista RAG (ChromaDB, 23 instrumentos) | Operativo |
| Inteligencia | Architect Agent autónomo (Claude Opus 4.7) | Operativo |
| Producto | Elite Report 12 capítulos + 3 anexos | Operativo |
| Producto | i18n profundo trilingüe (180+ claves) | Operativo |
| Producto | Observer Protocol multi-fase (9 fases) | Operativo |
| Producto | MOE Brief con descarga | Operativo |
| Producto | Endpoint /structured (extracción dinámica) | Operativo |
| Datos | V-Dem v16 (1789-2025) | Operativo |
| Datos | Freedom House FIW (2013-2025) | Operativo |
| Datos | PEI 10.0 (2012-2023) | Operativo |
| Datos | RSF 2025 | Operativo |
| Datos | OONI integration (censura web) | Operativo |
| Datos | 14 instrumentos del derecho internacional | Operativo |
| Persistencia | SQLite triple-tier (filesystem + TEXT + PDF on-demand) | Operativo |
| Persistencia | Backup script (`scripts/backup.py --targz`) | Operativo |
| Frontend | Dashboard React multi-tab | Operativo |
| Frontend | Perú Situation Room (11 secciones) | Operativo |
| Infraestructura | Railway (backend) + Netlify (frontend) | Operativo |
| Infraestructura | CORS hardening + X-Observer-Key + rate limiting | Operativo |
| Infraestructura | Discord webhook alerts (severidad ≥ high) | Operativo |
| Calidad | 91/91 tests integrados pasando | Operativo |

### 1.3 Cierre de brechas v1.0 → v2.0

El diagnóstico de Marzo 2026 identificó ocho brechas críticas. Estado al
4 de mayo de 2026:

| ID | Brecha (v1.0) | Estado actual (v2.0) |
| --- | --- | --- |
| P0 | Trazabilidad inexistente | **Resuelto.** Cada dato del informe tiene `source_id`, `source_url`, `recorded_at`, `confidence_level`, `legal_basis`, `agent_id`. Citas APA 7 en bibliografía. |
| P0 | 100 % de datos mock | **Resuelto.** Cuatro datasets reales integrados (V-Dem v16, FH FIW, PEI 10.0, RSF 2025). Hunter monitorea 8 fuentes RSS reales para Perú. |
| P1 | Marco legal con reglas estáticas | **Resuelto.** RAG semántico (ChromaDB + sentence-transformers all-MiniLM-L6-v2) sobre corpus de 23 instrumentos jurídico-electorales. |
| P1 | Sólo ICCPR como base normativa | **Resuelto.** 14 instrumentos: ICCPR, CADH, CDI, CEDAW, OSCE/ODIHR, UNDRIP, jurisprudencia CIDH, Constitución Perú 1993, LOE 26859, LOP 28094, Resoluciones JNE. |
| P1 | Sin diferenciación regional | **Parcialmente resuelto.** Detección automática de región y aplicación de instrumentos universales + regionales operativa para Américas. Pendiente para Europa/África/Asia (Sprint 3). |
| P2 | Datos en memoria | **Resuelto.** SQLite con persistencia triple-tier. Sobrevive a reinicios y a corrupción del filesystem del volumen. |
| P2 | Layout dashboard incompleto | **Resuelto.** Frontend en producción en democracia.ar con responsive design. |
| P3 | Sin autenticación | **Resuelto.** X-Observer-Key sobre endpoints sensibles, rate limiting por IP, budget diario configurable por país. |

### 1.4 Brechas remanentes y nuevas

| ID | Brecha actual | Prioridad | Roadmap |
| --- | --- | --- | --- |
| P1 | Marco institucional generalizado para arquitecturas no-peruanas (federal centralizado tipo Brasil, federal descentralizado tipo USA) | Alta | Sprint 3 |
| P1 | Prompts de capítulos del Elite Report en español; LLM responde en inglés/portugués pero residuos en narrativa | Alta | Sprint 4 |
| P2 | Adapter por país pluggable (eliminar `if country_code == "PER"` distribuido) | Alta | Sprint 2 |
| P3 | Detección estadística de anomalías temporales (Hunter clasifica pero no detecta cambios de tasa) | Media | Backlog |
| P3 | Mapa mundial interactivo en frontend | Media | Backlog |
| P3 | Sistema multi-rol (observador/analista/admin) | Baja | Backlog |

---

## 2. Framework de Trazabilidad — Implementado

El esquema de metadatos por dato propuesto en la versión 1.0 está hoy
implementado y operativo. Cada hallazgo del Hunter, cada cita en el Elite
Report y cada dato cuantitativo del dashboard cumple los nueve campos de
trazabilidad definidos.

### 2.1 Esquema operativo

| Campo | Implementación | Ejemplo |
| --- | --- | --- |
| `source_id` | Identificador interno único | `vdem_v16_PER_2025` |
| `source_type` | Enum: `dataset`, `rss`, `api`, `document`, `manual` | `rss` |
| `source_url` | URL exacta verificable | `https://andina.pe/agencia/...` |
| `recorded_at` | Timestamp ISO 8601 | `2026-04-15T20:14:31Z` |
| `data_hash` | SHA-256 sobre dato crudo | `a3f2b7c8d1e4...` |
| `confidence_level` | Enum: `confirmed`, `probable`, `unverified`, `mock` | `confirmed` |
| `legal_basis` | Artículo y tratado aplicable | `ICCPR Art. 25(b)` |
| `agent_id` | Agente que procesó el dato | `elite_loader` |
| `version` | Versionado para rastreo histórico | `v0.5.2` |

### 2.2 Política de publicación

> **Regla de oro (vigente):** Si un dato no puede llenar todos los campos
> del esquema, no se publica. Se marca como `pending_verification` y no
> alimenta el Risk Score ni los gráficos del informe.

Bloques sin URL primaria son postergados antes que publicarse. Esta
política es enforced por el Architect Agent en cada sesión.

### 2.3 Citación pública (APA 7)

Cada Elite Report incluye un Anexo B (Bibliografía) con las citas
formateadas según APA 7, con enlace `[URL]` activo a la fuente primaria.
La numeración `[N]` aparece desplazada del cuerpo del item para preservar
legibilidad tipográfica.

---

## 3. Marco Legal Expandido — Implementado

El sistema cubre hoy la totalidad de los instrumentos universales propuestos
en v1.0 más los regionales aplicables a las Américas (caso de uso activo).
Los instrumentos para Europa, África y Asia-Pacífico están catalogados y
listos para activarse cuando se onboard nuevos países.

### 3.1 Instrumentos Universales (operativos)

- ICCPR — Pacto Internacional de Derechos Civiles y Políticos (Art. 19, 21, 22, 25)
- CEDAW — Convención sobre la Eliminación de toda forma de Discriminación contra la Mujer
- ICERD — Convención sobre la Eliminación de la Discriminación Racial
- CRPD — Convención sobre los Derechos de las Personas con Discapacidad
- UNDRIP — Declaración de los Derechos de los Pueblos Indígenas
- UNCAC — Convención de las Naciones Unidas contra la Corrupción

### 3.2 Instrumentos Regionales

| Región | Instrumentos | Organismos | Estado |
| --- | --- | --- | --- |
| Américas | Convención Americana sobre DDHH (Art. 23), Carta Democrática Interamericana | OEA / DECO, UNIORE, Centro Carter | Operativo |
| Europa | CEDH Protocolo 1 Art. 3, Documento de Copenhague OSCE 1990 | OSCE / ODIHR, Comisión de Venecia, Parlamento Europeo | Catalogado |
| África | Carta Africana sobre DDHP (Art. 13), Carta Africana sobre Democracia 2007 | UA, ECOWAS, SADC, IGAD | Catalogado |
| Asia-Pacífico | Declaración ANFREL Bangkok, Pacific Islands Forum Biketawa | ANFREL, Pacific Islands Forum | Catalogado |
| Mundo Árabe | Carta Árabe de DDHH (Art. 24) | Liga Árabe, Red Árabe Electoral | Catalogado |

### 3.3 Marco doméstico de Perú 2026

- Constitución Política del Perú (1993, vigente con reformas)
- Ley Orgánica de Elecciones N° 26859 (LOE)
- Ley Orgánica de Partidos Políticos N° 28094 (LOP)
- Resoluciones del Jurado Nacional de Elecciones (JNE)

### 3.4 Mecanismo de aplicación

El Legal Compliance Agent detecta automáticamente la región del país en
análisis y aplica los instrumentos universales más los regionales
correspondientes. La consulta es semántica sobre el corpus RAG vectorizado,
no rule-based.

---

## 4. Arquitectura Técnica

### 4.1 Stack tecnológico

| Capa | Tecnología | Versión |
| --- | --- | --- |
| Backend | Python + FastAPI | 3.11 (Railway) / 3.14 (dev local) + 0.115 |
| Modelo de inteligencia | Claude Sonnet 4.6 (clasificación + composición) | claude-sonnet-4-6 con prompt caching |
| Modelo autónomo | Claude Opus 4.7 (Architect Agent) | claude-opus-4-7 + claude-agent-sdk |
| Orquestación | LangGraph + LangChain | 0.2 + 0.3 |
| RAG | ChromaDB + sentence-transformers (all-MiniLM-L6-v2) | 90 MB indexado |
| Persistencia | SQLite triple-tier | filesystem + TEXT columns + PDF on-demand |
| Frontend | Vite + React + Recharts | 7.x + 18 + 2.x |
| Tipografía | Fraunces + DM Sans + DM Mono | Google Fonts |
| Generación PDF | Browser-native via `/printable` + `window.print()` | Sin dependencias C-extension |
| i18n | Módulo propio `i18n.py` (180+ claves) + `section_titles.py` (50 entradas) | es / en / pt |
| Tests | pytest | 91/91 pasando |
| Deploy backend | Railway con Nixpacks + volumen persistente + healthcheck | -- |
| Deploy frontend | Netlify auto-deploy desde main | democracia.ar |
| Autenticación | X-Observer-Key + rate limit + budget diario | -- |
| Alertas | Discord webhook | severidad ≥ high |

### 4.2 Pipeline del Elite Report

El producto canónico de la plataforma es el Elite Report — un documento
estructurado en 12 capítulos más 3 anexos, generado por un pipeline de
seis etapas:

1. **EliteLoader** — carga paralela de evidencia: entries del Hunter,
   alertas dispatchadas, corpus constitucionalista filtrado por país,
   series históricas de los cuatro datasets. Cache TTL 1 hora.
2. **PhaseOrganizer** — agrupa los hallazgos del Hunter en las nueve
   fases del ciclo electoral según fecha y calendario electoral.
3. **CrossReferenceBuilder** — vincula hallazgos de severidad
   `high`/`critical` con artículos del marco normativo mediante mapeo
   curado de 14 categorías.
4. **PredictiveEngine** — motor híbrido que combina reglas determinísticas
   sobre patrones del Hunter con análisis cualitativo de Claude Sonnet 4.6,
   produciendo seis escenarios probabilísticos con bandas de confianza y
   un nivel de alerta temprana.
5. **ChapterComposer** — 12 prompts especializados con prompt caching de
   Anthropic y concurrencia limitada a cuatro peticiones simultáneas.
   Cada capítulo se genera con contexto compartido y datos específicos.
6. **Visualizer + Renderer** — 21 visualizaciones SVG server-side con
   paleta institucional. HTML responsive con CSS @page A4 + @media print
   para impresión profesional. Triple persistencia en SQLite.

### 4.3 Disclosure obligatorio

Cada Elite Report incluye, en cover, declaración preliminar y footer, el
siguiente disclosure inmodificable:

> **DEMOCRAC.IA no legitima ni valida resultados electorales.** Este
> informe emite inteligencia electoral con trazabilidad verificable bajo
> estándares internacionales de observación electoral, sin sesgo
> político-partidario.

El texto evita deliberadamente nombrar organismos específicos (OEA, EU EOM,
Centro Carter) para preservar neutralidad institucional y no inducir
asociaciones que podrían leerse como endoso.

### 4.4 Internacionalización

La plataforma soporta tres idiomas como first-class citizens:

- **Español** — idioma de origen, prompts del LLM, Perú 2026.
- **Inglés** — para audiencia internacional, partners (V-Dem, Freedom
  House, PEI, RSF), USA 2026 midterms.
- **Portugués** — para Brasil 2026.

Cobertura del i18n al cierre v2.0:

- 180+ claves cubriendo cover, footer, TOC, captions, títulos y subtítulos
  de visualizaciones, headers SVG, status labels, gauge bands, compliance
  columns, scenarios labels, audit notes, alert badges, severity legends,
  Appendix A body completo, subchapter titles 1.1-12.6 (50 entradas).
- LANGUAGE_RULE en composer instruye al LLM a responder en el idioma
  pedido aún cuando el contexto sea en español.
- Capa `section_titles.py` traduce headers `## N.M ...` por número de
  subsección (no por texto), robusto a variaciones del LLM.

---

## 5. Caso de Uso — Perú 2026

### 5.1 Contexto

Las elecciones generales del 12 de abril de 2026 en Perú constituyen el
caso de uso piloto de la plataforma. Perú reúne las condiciones que la
hacen un escenario informativo:

- Inestabilidad institucional reciente (seis presidentes en cuatro años).
- Indicadores V-Dem y Freedom House en deterioro entre 2018-2024.
- Despliegue de un sistema electoral con componentes de IA (STAE,
  SCE) sin auditoría pública independiente.
- Marco legal robusto (LOE, LOP, Constitución) pero con tensiones
  ejecutivas y legislativas sobre el ente electoral.

### 5.2 Cobertura activa

- **Hunter scheduler** corriendo cada 24 horas sobre 14 fuentes RSS (8 nacionales + 6 internacionales filtradas por keyword "Peru")
  verificadas (Andina, RPP, El Comercio, Gestión, IDL-Reporteros, Wayka,
  JNE, ONPE), mapeadas a las nueve fases del ciclo electoral.
- **Sesión de observación activa** desde el inicio de la fase preparatoria,
  rehidratada automáticamente al reiniciar el sistema.
- **Alertas Discord** disparadas en eventos de severidad `high` o superior.
- **Elite Reports** generables on-demand para cualquier fase del ciclo.
- **Sala de situación** en frontend con once secciones específicas.

### 5.3 Datos peruanos integrados

- Catálogo de las 8 fuerzas políticas con elecciones 2026, perfiles ICCPR.
- Sistema electoral: arquitectura JNE / ONPE / RENIEC, procedimientos,
  tecnología, cadena de custodia.
- Escenarios parlamentarios proyectados.
- Datos regionales con riesgo electoral por circunscripción.
- Eventos institucionales críticos del último ciclo.

### 5.4 Cobertura geográfica más amplia

La plataforma incluye un catálogo global de 38 países priorizados, con
datos reales confirmados para los cuatro países pilotos (Venezuela,
Nicaragua, Guatemala, Uruguay). El resto del catálogo dispone de
infraestructura de generación pero requiere onboarding específico
(Sprints 5 y 6 cubren Brasil y USA).

| Región | Países |
| --- | --- |
| Américas (19) | VEN, NIC, GTM, URY, COL, BRA, MEX, ARG, CHL, BOL, ECU, PER, HND, SLV, PAN, CRI, DOM, PRY, CUB |
| Europa (8) | DEU, FRA, HUN, POL, SRB, GEO, ARM, AZE |
| África (5) | CMR, COD, ETH, NGA, ZWE |
| Asia / Medio Oriente (6) | BGD, PHL, MMR, PAK, THA, TUR |

---

## 6. Roadmap de Evolución

> Los próximos sprints están condicionados por el calendario electoral
> 2026: Brasil (4 de octubre) y USA midterms (3 de noviembre). Los
> Sprints 2 y 3 son blockers no negociables para escalar a un segundo país.

### Sprint 2 — CountryAdapter pluggable (4-6 horas)

Extracción de la lógica específica de Perú a un adapter pluggable.
Eliminación del patrón `if country_code == "PER"` distribuido en backend.
Interfaz `CountryAdapter` con métodos canónicos (`get_actors`, `get_phases`,
`get_legal_framework`, `get_emb_config`, `get_static_events`).

### Sprint 3 — Modelo institucional generalizado (6-8 horas)

Soporte para arquitecturas distintas a la peruana:

- **Federal centralizado (Brasil):** TSE como autoridad nacional, TREs
  estaduales, sistema único de tabulación electrónica.
- **Federal descentralizado (USA):** sin EMB nacional, 50 estados más
  Distrito de Columbia con legislación propia, voting machines
  heterogéneas, primary methods variables.

### Sprint 4 — Traducción de prompts (8-10 horas)

Traducción al inglés y portugués de los 13 archivos de prompts de
capítulos (`cap_00.md` a `cap_12.md` más `base_context.md`). Cubre el
último bolsillo de español en el output del LLM. Una vez completo, la
capa `section_titles.py` se mantiene como red de seguridad.

### Sprint 5 — Brasil 2026 onboarding (10-12 horas, antes 4-oct-2026)

Construcción del `BrasilAdapter`. Integración del calendario electoral
oficial del TSE. Cinco a ocho fuentes RSS verificadas. Marco legal: Código
Eleitoral (Lei 4.737/65), Lei das Eleições (9.504/97), Lei dos Partidos
(9.096/95), Resoluções TSE 23.610/2024. Tab "Brasil 2026" en frontend
con preview-unlock.

### Sprint 6 — USA 2026 midterms onboarding (12-16 horas, antes 3-nov-2026)

Construcción del `USAAdapter`. Modelado descentralizado (Election
Assistance Commission federal sin autoridad ejecutiva). Mapeo estado por
estado de primary methods, voter ID, mail-in ballots, registration
deadlines. Marco legal en capas: 1st/14th/15th/19th/24th/26th
Amendments, VRA 1965, HAVA 2002, NVRA 1993. Categoría nueva en Hunter
para voter suppression / gerrymandering / election denial rhetoric.

### Sprints horizontales (paralelos)

- Citation builder i18n (1-2 horas).
- Predictive scenarios narrative i18n (3-4 horas).
- Frontend feature flags + preview unlock (4-6 horas).

---

## 7. Anclajes para el Diálogo Institucional con Partners

La plataforma emplea cuatro datasets propietarios de instituciones
académicas y de derechos civiles. La relación con cada partner está
construida sobre tres pilares: atribución exacta, evidencia de uso fiel,
y métricas de uso.

### 7.1 Atribución correcta (Anexo B de cada Elite Report)

| Dataset | Atribución exacta | Licencia |
| --- | --- | --- |
| V-Dem v16 | Coppedge et al. 2026. *V-Dem Country-Year Dataset v16*. Varieties of Democracy (V-Dem) Project. <https://doi.org/10.23696/vdemds26> | Académica con atribución |
| Freedom House FIW | Freedom House. 2025. *Freedom in the World 2025*. <https://freedomhouse.org/report/freedom-world/2025> | Open data |
| PEI 10.0 | Norris, Pippa et al. 2024. *Perceptions of Electoral Integrity Dataset (PEI-10.0)*. Harvard Dataverse. | Open con atribución |
| RSF 2025 | Reporters Without Borders. 2025. *World Press Freedom Index 2025*. <https://rsf.org/en/index> | CC-BY-NC |

### 7.2 Evidencia de uso fiel

- **Trazabilidad APA 7** sobre cada dato del informe, con enlace activo a
  la fuente primaria.
- **Disclosure neutral de no-legitimación** en cover, declaración
  preliminar y footer.
- **Triple-tier de persistencia** que permite auditoría post-publicación
  del estado exacto de los datos al momento de generar el informe.
- **Tests integrados** (91/91 pasando) que validan que la disclosure y la
  bibliografía aparecen correctamente.
- **Versionado del CSV de origen** en `VDEM_VERSION` (env var) para
  trazabilidad de cuando se actualizó cada dataset.

### 7.3 Métricas de uso (a calcular previo a presentaciones)

- Número de países analizados con cada dataset.
- Número de Elite Reports generados.
- Cobertura temporal efectivamente utilizada de cada dataset.
- Casos de uso públicos verificables.

---

## 8. Recomendación de Próximos Pasos

### 8.1 Prioridad inmediata (próximas 4-6 semanas)

1. **Sprints 2 y 3** (CountryAdapter + modelo institucional generalizado)
   como condición sine-qua-non para escalar a Brasil y USA.
2. **Sprint 4** (traducción de prompts) para eliminar el último residuo
   de español en outputs en inglés/portugués.
3. **Diálogo formal con dataset partners** (V-Dem, Freedom House, PEI,
   RSF). Presentación del producto, atribución correcta, casos de uso.
   Considerar partnership formal o acuerdo de uso institucional.

### 8.2 Cobertura electoral H2 2026

1. **Sprint 5 (Brasil 2026)** completado antes del 4 de octubre.
2. **Sprint 6 (USA 2026 midterms)** completado antes del 3 de noviembre.
3. Cobertura simultánea de tres países en producción (Perú, Brasil, USA)
   sin degradación de calidad de informe.

### 8.3 Sostenibilidad operativa

1. **Backup automatizado** programado (cron diario) usando
   `scripts/backup.py --targz`.
2. **Procedimiento documentado de restore Railway** (anexado en el
   roadmap técnico) para reducir tiempo de respuesta ante incidentes.
3. **Métricas de salud** del sistema visibles en panel interno: número de
   reports generados, latencia LLM, hits de cache, costos por país.

---

*DEMOCRAC.IA / PEIRS — Predictive Electoral Integrity & Risk System*
*Documento institucional v2.0 — Mayo 2026 — CONFIDENCIAL*
*Sucede a la versión 1.0 (Marzo 2026)*
