# DEMOCRAC.IA — DOCUMENTO DE ARQUITECTURA, DIAGNÓSTICO Y ROADMAP DE IMPLEMENTACIÓN

## Plataforma de Inteligencia Electoral con IA

*Version: 0.5.1 — Fecha: 2026-05-04*
*Clasificacion: Uso interno — Fundadora y equipo tecnico*

> **Nota de versionado:** Esta version refleja la arquitectura real al 4-may-2026.
> Las fases v0.5.0 (SENTINEL), v0.6.0 (persistencia) y v0.8.0 (PDF + API auth)
> del roadmap original ya estan operativas. Se sumaron tres modulos no
> previstos: Hunter scheduler, Constitucionalista RAG, Architect Agent autonomo,
> Elite Report 12-capitulos y ReportDesigner sub-agente.
>
> **Metodología constructiva del informe Elite:** consultar
> [DOCS Proyect/INFORME_METODOLOGIA.md](INFORME_METODOLOGIA.md) — playbook
> reproducible para Perú 2026 y replicable a cualquier país y ciclo electoral.
> Incluye análisis del Architect Agent con 3 sprints recomendados antes de
> escalar a un segundo país.

---

## VISION

Democrac.IA sera la **plataforma de referencia global** para inteligencia electoral basada en IA.
Combina una base de conocimiento historico de 50 anos (PEIRS) con monitoreo en tiempo real
(SENTINEL), produciendo informes de calidad equivalente a los de la OEA, OSCE/ODIHR y el
Centro Carter -- pero automatizados, escalables y disponibles en minutos, no en semanas.

**No legitimamos elecciones. Emitimos inteligencia electoral con trazabilidad verificable.**

---

## ARQUITECTURA ACTUAL

```
+======================================================================+
|                        DEMOCRAC.IA v0.4.5                            |
+========================+=============================================+
|   PEIRS                |   SENTINEL                                  |
|   Knowledge Base       |   Real-Time Intelligence                    |
|                        |                                             |
|  - V-Dem v15 (27.913   |  - Calendario electoral global (stub)       |
|    registros, 1789-    |  - /api/sentinel/alerts (operativo)         |
|    2024)               |  - OSINT feeds (pendiente)                  |
|  - Freedom House       |  - Social Media Monitor (pendiente)         |
|    FIW 2013-2025       |  - WebSocket (pendiente)                    |
|  - PEI 10.0 (586       |  - Predictor ML (pendiente)                 |
|    elecciones,         |                                             |
|    2012-2023)          |                                             |
|  - RSF 2025 (180       |                                             |
|    paises)             |                                             |
+========================+=============================================+
|         MOTOR DE ANALISIS -- LangGraph + Claude Sonnet               |
|                                                                      |
|   Agente OSINT -> Agente Politico -> Agente Legal -> Agente Informe  |
|   + Agente MOE Brief (operativo) + Agente Mejora Continua (pendiente)|
+======================================================================+
|                      CAPA DE SALIDA                                  |
|                                                                      |
|   Dashboard React   |  Informe VIP 9 caps  |  MOE Brief descargable |
|   Peru Sala Sit.    |  Trazabilidad        |  API REST              |
|   Sentinel (stub)   |  Markdown export     |  PDF (pendiente)       |
+======================================================================+
```

---

## ESTADO ACTUAL (v0.5.0 -- 2026-04-27)

### Componentes Operativos en Produccion

| Componente | Estado | Notas |
| --- | --- | --- |
| **Pipeline LangGraph 4 agentes** | Operativo | OSINT > Politico > Legal > Informe |
| **Hunter scheduler 24/7** | Operativo | Intervalo configurable (default 4h), persistente en volumen Railway con auto-recovery. 1.685 entries reales clasificadas para Peru 2026 al 27-abr |
| **Constitucionalista RAG** | Operativo | ChromaDB + sentence-transformers all-MiniLM-L6-v2. Corpus de 23 instrumentos juridico-electorales |
| **Architect Agent autonomo** | Operativo | claude-agent-sdk con Claude Opus 4.7. Acceso al codebase para refactor iterativo bajo regla de trazabilidad estricta |
| **Elite Report 12 capitulos** | Operativo | Claude Sonnet 4 con prompt caching, 4 audiencias (institutional/executive/press/international), motor predictivo con 6 escenarios + early-warning meter, 21 visualizaciones SVG server-side, citas APA 7. Costo ~$0.40-0.80 por informe |
| **ReportDesigner sub-agente** | Operativo | Pipeline Structurer > Visualizer > Composer. 4 audiencias, ES/EN, dedupe semantico (category+URL+date), priorizacion ponderada |
| **Observer Protocol** | Operativo | Sesiones multi-fase con 9 fases electorales (preparatoria > pre-campaña > campaña > silencio > jornada > escrutinio > post-electoral > resolucion de disputas > completada) |
| **MOE Brief** | Operativo | /api/moe/brief/{code} + descarga markdown |
| V-Dem v15 integrado | Operativo | 27.913 observaciones pais-año, 1789-2024 |
| Freedom House FIW integrado | Operativo | 2.723 filas, ediciones 2013-2025 |
| PEI 10.0 integrado | Operativo | 586 elecciones, 2012-2023 |
| RSF 2025 integrado | Operativo | 180 paises, index libertad de prensa |
| Marco legal | Operativo | 14 instrumentos en taxonomia propia: ICCPR, CADH, CDI, CEDAW, OSCE/ODIHR, UNDRIP, jurisprudencia CIDH, Constitucion Peru 1993, LOE 26859, LOP 28094, Resoluciones JNE |
| **8 fuentes RSS Peru** | Operativo | Andina, RPP, El Comercio, Gestion, IDL-Reporteros, Wayka, JNE, ONPE — mapeadas a fases electorales |
| **OONI integration** | Operativo | Censura de internet (date-only since/until tras fix 22-abr) |
| **Discord webhook alerts** | Operativo | Severidad >= high dispara notificacion |
| **SQLite persistencia** | Operativo | reports + sessions + entries + reportes elite. Sobrevive reinicios. |
| **Hardening produccion** | Operativo | Auth X-Observer-Key, rate-limit por IP, budget diario por pais (cap configurable), fallbacks gracias |
| **PDF export Elite** | Operativo | xhtml2pdf con CSS @page A4 + @media print. Firma con run_id + timestamp |
| **Markdown export** | Operativo | MOE Brief + informe completo |
| Dashboard React multi-tab | Operativo | Overview / Detalle / Sentinel / Peru Situation Room / Metodologia |
| Peru Situation Room | Operativo | 11 tabs: Alertas / Calendario / Datos / Series V-Dem / Actores / Parlamento / MOE Brief / Jornada / Evaluacion / Metodologia / Informe Elite + Consulta constitucional |
| Catalogo paises | Operativo | 38 paises (Americas, Europa Este, Africa, Asia) |
| /api/country/{code} | Operativo | Datos por pais con cache 24h |
| /api/peru/actors | Operativo | 8 fuerzas politicas 2026 con perfiles ICCPR |
| /api/peru/scenarios | Operativo | 4 escenarios parlamentarios + datos regionales |
| Trazabilidad APA 7 | Operativo | Cada dato con source/url/date/confidence_level. Bloques sin URL primaria son postergados antes que publicarse (politica del Architect Agent) |
| **Deploy Railway + Netlify** | Operativo | Auto-deploy con git push, healthcheck /api/health (timeout 300s), volumen persistente. Frontend en democracia.ar |

### Componentes Pendientes

| Componente | Estado | Prioridad |
|---|---|---|
| WebSocket alertas en vivo | No existe (Discord webhook lo cubre parcialmente) | Baja |
| Mapa mundial interactivo | No existe | Media |
| Multi-idioma (FR para Africa) | Solo ES + EN | Baja |
| Detección estadística de anomalías ML | Hunter clasifica pero no detecta anomalias temporales | Media |
| API publica externa con tiers | Solo X-Observer-Key interna | Baja |
| Sistema de usuarios (observador/analista/admin) | No existe | Baja |

---

## DATASETS INTEGRADOS

| Dataset | Archivo local | Registros | Cobertura | Uso |
|---|---|---|---|---|
| V-Dem v15 | V-Dem-CY-Full+Others-v15.csv (384MB) | 27.913 | 1789-2024 | EMB, irregularidades, lib. civil, media, digital |
| Freedom House FIW | All_data_FIW_2013-2025 - Index.csv | 2.723 | 2013-2025 | Score democracia, libertades civiles/politicas |
| PEI 10.0 | PEI/PEI_10 Election External.csv | 586 | 2012-2023 | Integridad EMBs, financiamiento, medios, registro |
| RSF 2025 | RSF/2025 - 2025.csv | 180 | 2025 | Libertad de prensa por pais |

**Nota de reproducibilidad:** El archivo V-Dem (384MB) excede el limite de GitHub. Debe
descargarse directamente desde <https://www.v-dem.net/data/the-v-dem-dataset/>
Los demas datasets estan en el repositorio.

---

## ARQUITECTURA DE CODIGO

```
D:\DemocracIA\
|
+-- backend/
|   +-- app.py                    (archivo principal -- 4.600+ lineas)
|   |   |
|   |   +-- Seccion 1: Configuracion (LLM, API key, modelos)
|   |   +-- Seccion 2: V-Dem loader (variables seleccionadas, normalizacion)
|   |   +-- Seccion 3: FH loader (CSV parsing, score extraccion)
|   |   +-- Seccion 4: PEI loader (EMBs, integridad, financiamiento)
|   |   +-- Seccion 5: RSF loader (libertad de prensa)
|   |   +-- Seccion 6: Datos estructurados por pais
|   |   |   +-- 6a: Instrumentos legales (14 universales/regionales)
|   |   |   +-- 6b: Regiones y mapeo pais-region
|   |   |   +-- 6c: Catalogo de 38 paises (COUNTRY_CATALOG)
|   |   |   +-- 6d: Peru 2026 (PERU_POLITICAL_FORCES, PERU_ELECTORAL_SYSTEM,
|   |   |            PERU_PARL_DATA, PERU_REGIONS_DATA, PERU_HISTORICAL_EVENTS)
|   |   +-- Seccion 7: LangGraph State + Pipeline 4 agentes
|   |   |   +-- Agente 1: OSINT (carga V-Dem, FH, PEI, RSF por pais)
|   |   |   +-- Agente 2: Politico (media bias, ecosistema digital, finanzas)
|   |   |   +-- Agente 3: Legal (violaciones ICCPR/CADH, risk score)
|   |   |   +-- Agente 4: Informe (genera 9 capitulos + executive summary)
|   |   +-- Seccion 8: Generadores de capitulos
|   |   |   +-- _generate_executive_summary()
|   |   |   +-- _generate_political_context(context, country_code)  [* enriquecido PER]
|   |   |   +-- _generate_emb_chapter()
|   |   |   +-- _generate_inclusivity_chapter()
|   |   |   +-- _generate_campaign_chapter()
|   |   |   +-- _generate_digital_chapter()
|   |   |   +-- _generate_voting_day_chapter()
|   |   |   +-- _generate_justice_chapter()
|   |   |   +-- _generate_recommendations()
|   |   +-- Seccion 9: Persistencia (save_report, load_report, index JSON)
|   |   +-- Seccion 10: FastAPI endpoints
|   |   |   +-- GET  /api/health
|   |   |   +-- GET  /api/countries
|   |   |   +-- POST /api/analyze
|   |   |   +-- GET  /api/report/{run_id}
|   |   |   +-- GET  /api/report/{run_id}/markdown
|   |   |   +-- GET  /api/report/{run_id}/traceability
|   |   |   +-- GET  /api/report/{run_id}/history
|   |   |   +-- GET  /api/dashboard
|   |   |   +-- GET  /api/country/{country_code}
|   |   |   +-- GET  /api/instruments/{country_code}
|   |   |   +-- GET  /api/moe/brief/{country_code}
|   |   |   +-- POST /api/analyze/voting-day
|   |   |   +-- GET  /api/sentinel/alerts
|   |   |   +-- GET  /api/peru/actors
|   |   |   +-- GET  /api/peru/scenarios
|   |   +-- Seccion 11: Peru 2026 datos estructurados
|   |   +-- Seccion 12: CLI para testing
|   +-- venv/                     (entorno virtual Python)
|
+-- frontend/
|   +-- src/
|   |   +-- App.jsx               (archivo unico -- 5.000+ lineas)
|   |   |   |
|   |   |   +-- Componentes base: Card, SectionTitle, Gauge, CircularScore
|   |   |   +-- ChartMethodologyBtn (metodologia por grafico)
|   |   |   +-- EMBStatusPanel
|   |   |   +-- renderMarkdownWithTooltips (informe con tooltips interactivos)
|   |   |   +-- ReportViewer (Dashboard / Dictamen / Informe tabs)
|   |   |   +-- OverviewView (dashboard 38 paises con busqueda y regiones)
|   |   |   +-- DetailView (analisis por pais: gauge + radar + violaciones + informe)
|   |   |   +-- SentinelView (alertas en tiempo real -- conectado a /api/sentinel/alerts)
|   |   |   +-- PeruSituationRoom (sala de situacion especifica Peru 2026)
|   |   |   |   +-- Tab Inteligencia: metricas FH/V-Dem/PEI + radar + timeline
|   |   |   |   +-- Tab Actores: 8 fuerzas politicas con perfiles expandibles
|   |   |   |   +-- Tab Parlamento: escenarios + hemiciclo + datos regionales
|   |   |   |   +-- Tab MOE Brief: brief de mision + descarga markdown
|   |   |   |   +-- Tab Jornada: formulario dia de votacion en tiempo real
|   |   |   |   +-- Tab Informe: PEIRS completo 9 capitulos (ReportViewer)
|   |   |   +-- MethodologyView (documentacion de indicadores)
|   |   |   +-- CountrySelector (busqueda + agrupacion regional)
|   |   |   +-- App principal: navegacion Overview / Detalle / Sentinel / Peru / Metodologia
|   +-- index.html
|   +-- package.json
|   +-- vite.config.js
|
+-- data/
|   +-- V-Dem-CY-Full+Others-v15.csv     (384MB -- excluido de git)
|   +-- All_data_FIW_2013-2025 - Index.csv
|   +-- PEI/PEI_10 Election External.csv
|   +-- RSF/2025 - 2025.csv
|   +-- reports/                          (generados por pipeline -- excluidos de git)
|   |   +-- index.json                   (indice por pais)
|   |   +-- {run_id}.json                (reporte completo por ejecucion)
|
+-- DOCS Proyect/
|   +-- PEIRS_Arquitectura_Roadmap.md    (este documento)
|   +-- PEIRS_SENTINEL_Roadmap_Elite_v1.md
|   +-- PEIRS_Arquitectura_Roadmap.docx  (version Word)
|   +-- Prompt Maestro Democracia New.docx
|
+-- Project_State.mp                     (estado del proyecto, actualizado por sesion)
+-- iniciar_backend.ps1                  (levanta uvicorn con PYTHONUTF8=1)
+-- iniciar_frontend.ps1                 (levanta vite dev server)
+-- actualizar.ps1                       (git pull + dependencias)
```

---

## FLUJO DE DATOS -- GENERACION DE UN INFORME

```
POST /api/analyze  {country_code: "PER"}
        |
        v
create_initial_state(country="Peru", code="PER", election_date="2026-04-12")
        |
        v
[AGENTE 1 -- OSINT]
  - get_vdem_data("PER")       -> V-Dem v15, ano 2024
  - get_fh_data("PER")         -> FH FIW 2025, score 72/100
  - get_pei_data("PER")        -> PEI 10.0, eleccion 2021
  - get_rsf_data("PER")        -> RSF 2025
  - context_data = {vdem, fh, pei, rsf, emb, legal_framework, civil_liberties...}
        |
        v
[AGENTE 2 -- POLITICO]
  - Media bias index (PEI MEDIACOVERAGE -> score normalizado)
  - Digital ecosystem assessment (V-Dem smgovdom, smregcap)
  - Campaign finance score (PEI CAMPAIGNFINANCE)
  - political_data = {media_analysis, digital_ecosystem, campaign_finance}
        |
        v
[AGENTE 3 -- LEGAL]
  - get_applicable_instruments("PER") -> ICCPR, CADH, CDI, UNDRIP, etc.
  - Evalua 10 violaciones: Art. 25 ICCPR, Art. 13 CADH...
  - Calcula risk_score (FH 15% + V-Dem 15% + EMB 15% + media 10% + finanzas 10% + digital 10% + violaciones 15% + obs.intl 10%)
  - legal_analysis = {violations, risk_factors, violation_count}
  - risk_score = 29.6/100, risk_level = "moderate"
        |
        v
[AGENTE 4 -- INFORME]
  - Cap. 1: Executive Summary (datos reales FH + V-Dem + EMB + PEI)
  - Cap. 2: Contexto Politico (FH + V-Dem + PEI + [PER: fuerzas politicas, crisis, ICCPR])
  - Cap. 3: EMB (V-Dem real: JNE PARTIAL, autonomia 0.60, irregularidades 0.35)
  - Cap. 4: Inclusividad (V-Dem suffrage + association + FH CL)
  - Cap. 5: Campana y Medios (PEI media + V-Dem bias)
  - Cap. 6: Ecosistema Digital (V-Dem smgovdom + LLM narrativa)
  - Cap. 7: Dia de Votacion (activado via /api/analyze/voting-day)
  - Cap. 8: Justicia Electoral (10 violaciones ICCPR/CADH con severidad)
  - Cap. 9: Recomendaciones (outlook + impacto inversores)
  - final_report_markdown = informe completo
        |
        v
save_report(result)  ->  data/reports/{run_id}.json
                     ->  data/reports/index.json  (actualiza entrada PER)
        |
        v
Response: {run_id, risk_score: 29.6, risk_level: "moderate", violation_count: N}
```

---

## CALCULO DEL RISK SCORE

```
risk_score = sum(dimension * peso) / 100

Dimensiones y pesos:
  Freedom House score        15%   (FH FIW 2025, confirmado)
  V-Dem lib. democracy       15%   (V-Dem v15, confirmado)
  EMB independence           15%   (V-Dem v2elembaut, confirmado)
  Media freedom              10%   (PEI MEDIACOVERAGE, confirmado)
  Campaign finance           10%   (PEI CAMPAIGNFINANCE, confirmado)
  Digital ecosystem          10%   (V-Dem smgovdom + smregcap, confirmado)
  Legal violations           15%   (conteo x severidad x 10)
  International observation  10%   (V-Dem + protocolo de obs.)

Niveles:
  0-25:  LOW      (condiciones institucionales solidas)
  26-50: MODERATE (requiere monitoreo activo)
  51-75: HIGH     (condiciones para alerta de mision)
  76-100: CRITICAL (riesgo sistemico -- protocolo de emergencia)
```

---

## PAISES MONITOREADOS (38)

| Region | Paises |
|---|---|
| Americas (19) | VEN, NIC, GTM, URY, COL, BRA, MEX, ARG, CHL, BOL, ECU, PER, HND, SLV, PAN, CRI, DOM, PRY, CUB |
| Europa (8) | DEU, FRA, HUN, POL, SRB, GEO, ARM, AZE |
| Africa (5) | CMR, COD, ETH, NGA, ZWE |
| Asia/Medio Oriente (6) | BGD, PHL, MMR, PAK, THA, TUR |

**Paises con datos reales confirmados (4 fuentes):** VEN, NIC, GTM, URY
**Peru:** datos reales + seccion especifica con fuerzas politicas 2026

---

## DIAGNOSTICO DE CALIDAD POR CAPITULO

| Capitulo | Fuente | Confianza | Cobertura real |
|---|---|---|---|
| Cap. 1 Resumen Ejecutivo | FH + V-Dem + EMB + PEI | CONFIRMED | 38 paises |
| Cap. 2 Contexto Politico | FH + V-Dem + PEI + [PER: JNE/datos estructurados] | CONFIRMED | 38 paises (PER con seccion especifica) |
| Cap. 3 EMB | V-Dem v15 real | CONFIRMED | 38 paises |
| Cap. 4 Inclusividad | V-Dem suffrage + FH CL | CONFIRMED | 38 paises |
| Cap. 5 Campana y Medios | PEI MEDIACOVERAGE + V-Dem | CONFIRMED | 38 paises con PEI |
| Cap. 6 Ecosistema Digital | V-Dem smgovdom + LLM | PARTIAL | V-Dem real, narrativa mock |
| Cap. 7 Dia de Votacion | Manual via endpoint | ON-DEMAND | Activo solo el dia de eleccion |
| Cap. 8 Justicia Electoral | FH + V-Dem + 14 instrumentos | CONFIRMED | 38 paises |
| Cap. 9 Recomendaciones | LLM basado en risk score | MOCK | Pendiente datos de inversion |

---

## ROADMAP POR FASES

---

### FASE v0.5.0 -- SENTINEL: INTELIGENCIA EN TIEMPO REAL

*Objetivo: La plataforma "ve" lo que pasa ahora, no solo lo que paso.*
*Estado: /api/sentinel/alerts existe como stub -- necesita datos reales.*

#### Backend

**`sentinel/calendar.py`**

- Fuente: API Wikidata para calendario electoral global
- Deteccion automatica de elecciones en los proximos 90 / 30 / 7 dias
- Clasificacion: presidencial / legislativa / referendum / local
- Actualizacion diaria via APScheduler

**`sentinel/osint_feeds.py`**

- RSS feeds verificados: OEA DECO, OSCE/ODIHR, HRW, Amnesty, Freedom House Alerts
- Reuters, AP, EFE (seccion politica)
- Extraccion de senales de riesgo por keywords (ES + EN)
- Score OSINT: 0-10 por eleccion activa

**`sentinel/alert_engine.py`**

- Umbral configurable por pais
- 3 niveles: WATCH / WARNING / CRITICAL
- Trigger automatico: regenerar informe del pais afectado
- Webhook: Slack/email cuando hay CRITICAL

**Endpoints a completar:**

```
GET  /api/sentinel/status           -> Estado de monitoreo global
GET  /api/sentinel/calendar         -> Elecciones proximas 90 dias
GET  /api/sentinel/alerts           -> Alertas reales (actualmente stub)
GET  /api/sentinel/country/{code}   -> Senales SENTINEL de un pais
POST /api/sentinel/trigger/{code}   -> Forzar actualizacion manual
WS   /ws/sentinel                   -> WebSocket para alertas en vivo
```

#### Frontend

- Panel de alertas en tiempo real (WebSocket)
- Punto rojo parpadeando en CountryCard si hay alerta activa
- Ticker de eventos electorales activos en la barra de navegacion

#### Metricas de exito v0.5.0

- Alertas generadas automaticamente en < 1 hora de un evento real
- 0 falsos positivos criticos en primera semana

---

### FASE v0.6.0 -- PERSISTENCIA Y ESCALABILIDAD

*Objetivo: El sistema no pierde datos entre reinicios y es reproducible.*

#### Backend

**SQLite como capa de persistencia primaria**

- Una tabla `reports` con indice por pais + fecha + risk_score
- Una tabla `countries` con metadata y configuracion
- Una tabla `elections_calendar` para SENTINEL
- Conexion via SQLAlchemy (ya disponible en FastAPI)
- Migraciones con Alembic

**Batch processing paralelo**

- `/api/dashboard` con `asyncio.gather()` para analisis en paralelo
- Cache de 24h por pais (no regenerar si datos no cambiaron)
- Progress tracking con Server-Sent Events

**Endpoint `/api/stats/global`**

- Distribucion de risk levels por region
- Ranking de paises por riesgo
- Tendencia global 2013-2025 (V-Dem historico)

#### Frontend

- Tab "Global" con mapa mundial (heat map de riesgo)
- Ranking con filtro por region y nivel de riesgo

#### Metricas de exito v0.6.0

- 38 paises analizados en paralelo en < 30 segundos
- Datos persisten entre reinicios (SQLite)
- Sin errores en consola del frontend

---

### FASE v0.7.0 -- AGENTE DE MEJORA CONTINUA

*Objetivo: La plataforma se mejora sola. El arquitecto experto nunca duerme.*

**`agents/improvement_agent.py`**

Corre semanalmente (cron job APScheduler) y:

1. Diagnostica: errores en logs, endpoints lentos, datos desactualizados
2. Benchmarks: calidad de informes vs. version anterior
3. Detecta: gaps de datos (paises sin datos recientes, datasets vencidos)
4. Propone: mejoras priorizadas con justificacion tecnica e impacto estimado
5. Genera: `IMPROVEMENT_REPORT_YYYY-MM-DD.md` en /docs/improvements/
6. Crea: GitHub Issues automaticamente si prioridad = CRITICAL o HIGH

**Endpoints:**

```
GET  /api/improvement/latest        -> Ultimo reporte de mejora
POST /api/improvement/run           -> Forzar ejecucion manual
GET  /api/improvement/history       -> Historial de reportes
```

---

### FASE v0.8.0 -- EXPORTACION Y API PUBLICA

**PDF Export profesional**

- WeasyPrint (Python): carátula, indice, graficos embebidos, bibliografia
- Firmado con timestamp y hash de integridad
- Endpoint: `GET /api/report/{run_id}/pdf`

**API REST publica**

- Autenticacion via API key
- Rate limiting por tier (free / professional / enterprise)
- Documentacion OpenAPI auto-generada (FastAPI lo hace nativo)

---

### FASE v1.0 -- PLATAFORMA ELITE INTEGRADA

*Objetivo: Todo corriendo junto. Lista para usuarios externos.*

#### Integraciones adicionales

- Multi-idioma: ES (principal) / EN / FR (Africa francofona)
- Sistema de usuarios: observador / analista / admin
- Notificaciones: email + Slack webhook + RSS feed

#### Infraestructura

- Docker + docker-compose (backend + frontend + PostgreSQL)
- Nginx como reverse proxy
- GitHub Actions: tests automaticos en cada PR
- Deploy en VPS (Hetzner o DigitalOcean, aprox. 10 EUR/mes)
- Dominio: democracia.ai o peirs.democracia.ai

#### Dashboard Elite -- Componentes finales

| Componente | Descripcion |
|---|---|
| Mapa mundial interactivo | Heat map de riesgo por pais, clic para detalle |
| Ticker en tiempo real | SENTINEL: eventos electorales activos |
| Panel de comparativas | Evolucion historica V-Dem por region 2013-2025 |
| Ranking dinamico | Top 10 paises en deterioro democratico |
| Estadisticas globales | Distribucion de risk, promedio regional, tendencias |
| Generador MOE | Brief de mision en 60 segundos |
| Biblioteca de informes | Historial por pais con versionado |
| Centro de metodologia | Documentacion completa de cada indicador |

---

## METRICAS DE EXITO -- EVOLUCION

| Metrica | v0.3.2 (base) | v0.4.5 (hoy) | Objetivo v1.0 |
|---|---|---|---|
| Paises monitoreados | 4 | 38 | 50+ |
| Datasets integrados | 2 (V-Dem, FH) | 4 (+ PEI, RSF) | 8+ |
| Capitulos con datos reales | 4/9 | 7/9 | 9/9 |
| Informe puntual Peru 2026 | No | Si (Cap. 2 enriquecido) | Todos los paises priorizados |
| MOE Brief | No | Si (operativo) | + PDF profesional |
| Sala de Situacion Peru | No | Si (6 tabs) | Todos los paises con eleccion < 90 dias |
| SENTINEL | No | Stub operativo | Real-time con OSINT feeds |
| Persistencia entre reinicios | No (memoria) | Parcial (JSON disco) | SQLite/PostgreSQL |
| Trazabilidad de datos | No | Si (confidence level por dato) | Auditoria completa |
| Export descargable | No | Si (markdown MOE Brief) | PDF firmado digitalmente |
| Tiempo de generacion de informe | ~45s | ~30s | < 10s (cache) |
| Usuarios simultaneos soportados | 1 | 1 | 50+ |
| Uptime | Local | Local | 99.5% (VPS) |

---

## PRINCIPIOS DE CALIDAD

1. **Trazabilidad completa** -- Cada dato tiene fuente, fecha y nivel de confianza visible en el informe
2. **No legitimacion** -- PEIRS emite riesgo predictivo, nunca valida resultados electorales
3. **Evidence-based** -- Cero afirmaciones sin respaldo empirico verificable
4. **Transparencia metodologica** -- Toda metrica tiene su metodologia publica (boton en el dashboard)
5. **Mejora continua** -- El sistema es mas inteligente en cada sesion
6. **Codigo auditable** -- GitHub publico, cambios trazables, sin logica oculta

---

## STACK TECNOLOGICO

| Capa | Tecnologia | Version | Estado |
|---|---|---|---|
| Backend | Python + FastAPI | 3.11 + 0.115 | Operativo |
| LLM analista | Claude Sonnet 4 (clasificacion + composicion) | claude-sonnet-4-20250514 | Operativo |
| LLM autonomo | Claude Opus 4.7 (Architect Agent) | claude-opus-4-7 + claude-agent-sdk | Operativo |
| Orquestacion agentes | LangGraph + LangChain | 0.2 + 0.3 | Operativo |
| RAG | ChromaDB + sentence-transformers | all-MiniLM-L6-v2 | Operativo |
| Base de datos | SQLite (persistencia primaria) | -- | Operativo |
| Scheduler | Hunter loop async + APScheduler | intervalo 4h configurable | Operativo |
| OSINT feeds | RSS via httpx + xml stdlib | 8 fuentes Peru por fase | Operativo |
| Censura internet | OONI API | date-only since/until | Operativo |
| Alertas | Discord webhook | severidad >= high | Operativo |
| Frontend | Vite + React + Recharts | 7.x + 18 + 2.x | Operativo |
| CSS/Fonts | DM Sans, DM Mono, Fraunces | CDN | Operativo |
| PDF | xhtml2pdf con CSS @page A4 + @media print | -- | Operativo |
| Deploy backend | Railway (Nixpacks) con volumen persistente + healthcheck | -- | Operativo |
| Deploy frontend | Netlify auto-deploy con git push | democracia.ar | Operativo |
| Auth | X-Observer-Key + rate-limit + budget diario por pais | -- | Operativo |
| WebSocket | -- (Discord webhook lo cubre parcialmente) | -- | No prioritario |
| CI/CD | GitHub (manual + Railway auto-deploy) | -- | Parcial |

---

## INICIO DE SESION (WORKFLOW OPERATIVO)

```powershell
# Terminal 1 -- Backend
cd D:\DemocracIA
.\iniciar_backend.ps1
# Verifica: [V-Dem] OK [FH] OK [PEI] OK -- Application startup complete.

# Terminal 2 -- Frontend
.\iniciar_frontend.ps1
# Verifica: VITE ready in Xms -- Local: http://localhost:5173/

# Primer uso (poblar cache de paises):
# GET http://localhost:8000/api/dashboard

# Regenerar informe de un pais:
# GET http://localhost:8000/api/country/PER?force_refresh=true
```

---

## ISSUES CONOCIDOS

| ID | Descripcion | Prioridad | Estado |
|---|---|---|---|
| #001 | V-Dem no esta en git -- instrucciones de descarga necesitan README | Alta | Abierto |
| #002 | SENTINEL /api/sentinel/alerts devuelve datos estaticos, no OSINT real | Alta | Abierto |
| #003 | Marco legal y padron electoral Cap. 2: mock para paises no-PER | Media | Abierto |
| #004 | Contador confianza Agente Legal no cuenta PEI correctamente | Baja | Abierto |
| #005 | Warning "Duplicate key border" en App.jsx | Baja | Abierto |
| #006 | PEI Venezuela: OVERALLINTEGRITY = N/D (datos 2018, fuera de rango) | Info | Abierto |
| #007 | reports_store en memoria -- se pierde entre reinicios (mitigado con JSON disco) | Media | Mitigado |
| #008 | Dashboard mostraba marcadores de capitulo | Alta | Resuelto |
| #009 | UnicodeEncodeError en prints con emojis (Windows cp1252) | Alta | Resuelto (PYTHONUTF8=1) |

---

## PROXIMA SESION RECOMENDADA

### Opcion A -- SENTINEL datos reales (impacto alto, visible)

Completar `/api/sentinel/alerts` con RSS feeds reales de OEA y HRW.
El frontend ya tiene la tab SENTINEL lista -- solo falta conectar datos.

### Opcion B -- SQLite persistencia (fundacion solida)

Migrar JSON a SQLite con SQLAlchemy.
Resuelve el issue #007 definitivamente y habilita queries complejas.

### Opcion C -- Continuar Peru (profundidad de contenido)

Enriquecer Cap. 5 (Campana y Medios) con datos PEI especificos de Peru.
Agregar seccion de candidatos presidenciales 2026 en /api/peru/actors.

---

*Documento actualizado por Democrac.IA -- Claude Opus 4.7 -- 2026-04-27 (v0.5.0)*
*Refleja la arquitectura real al 27-abr-2026, despues de los sprints SENTINEL/Hunter, RAG Constitucionalista, Architect Agent autonomo, Elite Report 12-capitulos, ReportDesigner, hardening de produccion y migracion a SQLite.*
*Clasificacion: Uso interno -- Fundadora y equipo tecnico*
