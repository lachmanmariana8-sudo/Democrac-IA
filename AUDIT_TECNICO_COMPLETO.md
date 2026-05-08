# DEMOCRAC.IA / PEIRS — Auditoría Técnica Completa

**Predictive Electoral Integrity & Risk System**
**Fecha:** 4 de mayo de 2026 | **Versión:** 0.5.2 | **Estado:** En producción

> **Versión anterior:** v1.0 del 5-abril-2026 (v0.4.0). Esta auditoría refleja
> el estado real al cierre de la sesión del 4-may-2026, después de:
> i18n profundo del Elite Report (es/en/pt), upgrade a V-Dem v16,
> Sprint 1 de tests integrados, recuperación de incidente Railway.

---

## 1. Qué es DEMOCRAC.IA

DEMOCRAC.IA es un sistema de inteligencia electoral OSINT que analiza, monitorea y predice riesgos a la integridad de procesos electorales en América Latina y el mundo. Opera mediante un enjambre de agentes de IA orquestados por LangGraph que procesan datos de fuentes internacionales verificadas, aplican marcos legales de derechos humanos, y generan reportes de riesgo accionables.

### 1.1 Misión

Democratizar el acceso a inteligencia electoral de calidad, antes reservada a organizaciones internacionales con presupuestos millonarios, poniendo herramientas de monitoreo profesional al alcance de observadores ciudadanos, medios independientes y organizaciones de la sociedad civil.

### 1.2 Valores expresados en el desarrollo

| Valor | Expresión concreta |
|---|---|
| **Transparencia** | Trazabilidad completa: cada dato del reporte incluye fuente, fecha y nivel de confianza. Código abierto en GitHub |
| **Rigurosidad** | Corpus legal de 14 instrumentos jurídico-electorales en ChromaDB con búsqueda semántica (ICCPR, CADH, CDI, CEDAW, OSCE/ODIHR, UNDRIP, jurisprudencia CIDH, Constitución Perú 1993, LOE 26859, LOP 28094, Resoluciones JNE). No inventa: cita |
| **Independencia** | Sin financiamiento partidario. Datos de fuentes académicas (V-Dem) y organismos internacionales (Freedom House, OSCE) |
| **Accesibilidad** | Dashboard web gratuito en democracia.ar. Interfaz en español. Visualizaciones intuitivas |
| **Protección de derechos** | Cada hallazgo se mapea automáticamente a los artículos de derechos humanos potencialmente vulnerados |
| **Automatización responsable** | IA como herramienta de análisis, no como tomadora de decisiones. Humano en el loop para verificación |
| **Resiliencia** | Fallbacks en cada capa: sin CSV usa mocks, sin ChromaDB usa keyword search, sin LLM genera templates |

---

## 2. Qué hace la plataforma

### 2.1 Pipeline de análisis

La plataforma opera con **dos pipelines en paralelo**:

#### A) Pipeline LangGraph (4 agentes) — análisis original

```text
┌──────────────┐    ┌───────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Agente 1    │───>│    Agente 2       │───>│    Agente 3      │───>│    Agente 4      │
│  OSINT       │    │  POLITICAL        │    │  LEGAL           │    │  REPORT          │
│  INGESTION   │    │  ANALYST          │    │  COMPLIANCE      │    │  GENERATOR       │
└──────────────┘    └───────────────────┘    └──────────────────┘    └──────────────────┘
      │                     │                        │                       │
  V-Dem v16           Partidos,             RAG Legal Corpus          Reporte 9 caps
  Freedom House       Medios,               14 instrumentos           Markdown + JSON
  RSF 2025, PEI 10    Redes digitales       ICCPR, CADH, CIDH        Trazabilidad APA 7
```

#### B) Pipeline Elite Report (6 etapas) — producto canónico

```text
EliteLoader → PhaseOrganizer → CrossReferenceBuilder → PredictiveEngine
    → ChapterComposer → Visualizer + Renderer → Persist (SQLite triple-tier)
```

Genera el **Elite Report de 12 capítulos + 3 anexos** con i18n trilingüe
(es/en/pt), 21 visualizaciones SVG server-side, motor predictivo con 6
escenarios + early-warning meter, y citas APA 7. Costo ~$0.40-0.80 por
informe con prompt caching de Anthropic.

### 2.2 Agentes especializados adicionales

| Agente | Función |
|---|---|
| **Hunter Agent** | Rastreo automático OSINT: RSS (Andina, RPP, JNE, ONPE) + OONI censura internet. Clasifica hallazgos con Claude y los registra en el protocolo de observación |
| **Auditor Agent** | Validación de hallazgos de campo: deduplicación, scoring de calidad, detección de patrones de fraude |
| **Alert Dispatch Agent** | Notificaciones en tiempo real a Discord/Slack/email cuando se detectan hallazgos de severidad alta o crítica |
| **Architect Agent** | Meta-agente para mejora continua del sistema (CLI-driven) |

### 2.3 Protocolo de observación electoral

Sistema completo de observación de campo con 9 fases:

```
PREPARATORIO → PRE-CAMPAÑA → CAMPAÑA → SILENCIO ELECTORAL → JORNADA ELECTORAL
    → CONTEO/TABULACIÓN → POST-ELECTORAL → RESOLUCIÓN DE DISPUTAS → COMPLETADO
```

- 19 categorías de hallazgos (fraude, discurso de odio, seguridad, logística, censura, etc.)
- 5 niveles de severidad (info → critical)
- Autenticación por API key para observadores
- Detección automática de patrones de fraude (geográfico, temporal, sistemático)
- Mapeo automático a derechos humanos vulnerados

### 2.4 Elite Report — 12 capítulos + 3 anexos

| Cap. | Título | Contenido |
|---|---|---|
| -2 | Declaración preliminar | Síntesis ejecutiva en 1 página A4 (300-400 palabras) |
| 1 | Contexto histórico | Trayectoria democrática 10 años con datasets cuantitativos |
| 2 | Marco jurídico aplicable | Normativa internacional + nacional en jerarquía |
| 3 | Sistema electoral | Arquitectura institucional (EMB), procedimientos, tecnología |
| 4 | Fase pre-electoral | Hallazgos del Hunter en preparatoria + campaña |
| 5 | Jornada electoral | Eventos hora por hora, regiones afectadas |
| 6 | Escrutinio y cómputo | Progreso de actas, incidentes de integridad |
| 7 | Post-electoral | Red de actores, cronología judicial |
| 8 | Derechos vulnerados | Cumplimiento ICCPR/CADH/CDI por artículo |
| 9 | Análisis predictivo | 6 escenarios probabilísticos + early-warning meter |
| 10 | Conclusiones | Síntesis multidimensional 8 PEIRS |
| 11 | Recomendaciones | Corto / mediano / largo plazo + sistema internacional |
| 12 | IA y regulación | Arquitectura tecnológica, incidentes, marco regulatorio |
| Anexo A | Metodología técnica | Pipeline PEIRS, fuentes Hunter, limitaciones reconocidas |
| Anexo B | Bibliografía APA 7 | Citas con URL activa a fuente primaria |
| Anexo C | Glosario | Definiciones de categorías Hunter |

---

## 3. Stack técnico completo

### 3.1 Backend

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.11 (Railway/Nixpacks) — 3.14 dev local |
| Framework API | FastAPI | >=0.115.0 |
| Servidor ASGI | Uvicorn | >=0.30.0 |
| Orquestación IA | LangGraph | >=0.2.0 |
| LLM Framework | LangChain Core + Anthropic | >=0.3.0 / >=0.2.0 |
| Modelo LLM (clasificación + composición) | Claude Sonnet 4.6 | claude-sonnet-4-6 con prompt caching |
| Modelo LLM (Architect Agent autónomo) | Claude Opus 4.7 | claude-opus-4-7 + claude-agent-sdk |
| Validación | Pydantic | >=2.0 |
| Datos | Pandas | >=2.0.0 |
| Vector DB | ChromaDB | >=0.5.0 |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | >=3.0.0 (~90MB) |
| HTTP Client | httpx | >=0.27.0 |
| Base de datos | SQLite triple-tier (filesystem + TEXT + PDF on-demand) | Built-in + Pandas |
| i18n | Módulo propio `i18n.py` (180+ keys) + `section_titles.py` (50 entries) | es / en / pt |
| Tests | pytest | 91/91 pasando, `requirements-dev.txt` separado |

### 3.2 Frontend

| Componente | Tecnología | Versión |
|---|---|---|
| Framework | React | 19.2.0 |
| Build tool | Vite | 7.3.1 |
| Visualización | Recharts | 3.8.0 |
| Tipado | TypeScript (dev) | Incluido |
| Linting | ESLint | 9.39.1 |
| Diseño | CSS-in-JS (inline styles) | Dark theme |

### 3.3 Infraestructura

| Componente | Servicio | URL |
|---|---|---|
| Backend hosting | Railway (Nixpacks + volumen persistente) | democracia-peirs-production.up.railway.app |
| Frontend hosting | Netlify | democracia-peirs.netlify.app |
| Dominio principal | democracia.ar | www.democracia.ar |
| Backup | `scripts/backup.py --targz` (snapshot single-file) | Manual / cron recomendado |
| Generación PDF | Browser-native via `/printable` + `window.print()` | Sin dependencias C-extension |
| SSL/TLS | Let's Encrypt (auto) | Renovación automática |
| CI/CD | GitHub → Railway / Netlify | Auto-deploy on push to main (secundario `api.democracia.ar` con auto-deploy DESACTIVADO) |
| Alertas | Discord webhook | Embed format con severidad/color (severidad ≥ high) |
| Repositorio | GitHub | lachmanmariana8-sudo/democracia-peirs |

### 3.4 Fuentes de datos integradas

| Fuente | Tipo | Cobertura | Variables clave |
|---|---|---|---|
| **V-Dem v16** | Dataset académico | 1789-2025 (CSV completo ~440MB) + tier estático en `vdem_static.py` (38 países × 21 indicadores × 1985-2025, 618KB en git) | 21 indicadores: tipo régimen, equidad electoral, sesgo mediático, autonomía EMB, irregularidades, ecosistema digital |
| **Freedom House FIW** | Índice anual | 210+ países, 2013-2025 | Derechos políticos (0-40), libertades civiles (0-60), estatus |
| **RSF Press Freedom** | Índice anual | 180 países, 2025 | Score libertad de prensa (0-100), tracker de periodistas asesinados |
| **PEI v10** | Dataset académico | 586 elecciones, 2012-2023 | Integridad percibida: EMBs, leyes, procedimientos, conteo, resultados |
| **OONI** | API tiempo real | Global, continuo | Anomalías web, interferencia de red por dominio y ASN (date-only since/until) |
| **Hunter RSS** | Feeds RSS cada 24h | 14 fuentes: 8 nacionales (Andina, RPP, El Comercio, Gestión, IDL-Reporteros, Wayka, JNE, ONPE) + 6 internacionales filtradas por keyword "Peru" (BBC LatAm, BBC Mundo, DW español, El País Internacional, Guardian World, NYT Americas) | Noticias clasificadas por fase electoral con Sonnet 4.6, dedupe semántico |

### 3.5 Corpus legal RAG (14 instrumentos jurídico-electorales)

Vectorizado en ChromaDB con embeddings sentence-transformers all-MiniLM-L6-v2.
Búsqueda semántica con keyword fallback. Indexado en background al startup
para no bloquear el healthcheck Railway.

| Categoría | Instrumentos |
|---|---|
| **ICCPR** | Art. 25 (derecho al voto), Art. 19 (expresión), Art. 20 (odio), Arts. 21-22 (asamblea) |
| **CADH** | Art. 23 (derechos políticos), Art. 13 (libertad de expresión) |
| **CDI** | Carta Democrática Interamericana completa |
| **CIDH Jurisprudencia** | Castañeda Gutman 2008, Yatama 2005, López Mendoza 2011 |
| **CEDAW** | Art. 7 — Participación política de mujeres |
| **OSCE/ODIHR** | Manual de observación electoral, Declaración de Principios 2005 |
| **UNDRIP** | Derechos de los pueblos indígenas en procesos electorales |
| **Marco nacional Perú** | Constitución 1993, LOE 26859, LOP 28094, Resoluciones JNE |

---

## 4. Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        www.democracia.ar (Netlify)                         │
│  React 19.2 + Vite 7.3 + Recharts 3.8                                     │
│  6 vistas: Overview | Análisis | Sentinel | Perú 2026 | Observación | Met. │
│  31 componentes React | 16 endpoints consumidos | 5 tipos de gráficos      │
├─────────────────────────────────────────────────────────────────────────────┤
│                              HTTPS / JSON                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                Railway (Backend FastAPI — 8,100 LOC app.py)                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  API Layer — 39 endpoints                                          │    │
│  │  /api/analyze | /api/report | /api/observation | /api/hunter       │    │
│  │  /api/sentinel | /api/ooni | /api/country | /api/evaluation        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  LangGraph Pipeline — 5 agentes + 3 especializados                 │    │
│  │  Ingestion → Political → Legal → Dictamen → ReportGen              │    │
│  │  + Hunter (OSINT) + Auditor (validación) + Alerts (dispatch)       │    │
│  │  LLM: Claude Sonnet 4 (temperature=0.2)                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  SQLite DB   │  │  ChromaDB    │  │  OONI API    │  │  RSS Feeds   │   │
│  │  8 tablas    │  │  17 docs     │  │  Tiempo real │  │  4 fuentes   │   │
│  │  CRUD 18 fn  │  │  + keyword   │  │  Censura web │  │  Perú        │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Data Loaders: V-Dem v15 | Freedom House | RSF | PEI v10          │    │
│  │  38 países monitoreados | Fallback a datos mock si CSV ausente     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────┐              │
│  │  Integrations: Discord Alerts | OONI | Hunter Scheduler  │              │
│  │  AUTO_OBSERVE_COUNTRIES | HUNTER_INTERVAL_MINUTES=1440    │              │
│  └──────────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. API — 39 endpoints documentados

### Core

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/health` | Estado del sistema, versión, features activos |
| GET | `/api/stats` | Estadísticas de DB: runs, reportes, sesiones, alertas |
| GET | `/api/countries` | Lista de 38 países con fecha de elección |
| GET | `/api/dashboard` | Dashboard resumen para frontend |

### Análisis

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/analyze` | Ejecuta pipeline completo de 5 agentes para un país |
| POST | `/api/analyze/voting-day` | Análisis en tiempo real durante jornada electoral |
| GET | `/api/report/{run_id}` | Reporte completo (JSON) |
| GET | `/api/report/{run_id}/markdown` | Reporte en Markdown |
| GET | `/api/report/{run_id}/traceability` | Trazabilidad: fuentes y confianza |
| GET | `/api/reports/history/{cc}` | Historial de reportes por país |
| GET | `/api/reports/history` | Últimos 50 reportes |

### Observación electoral

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/observation/{cc}/start` | Iniciar sesión de observación (requiere API key) |
| POST | `/api/observation/{cc}/entry` | Registrar hallazgo de campo |
| POST | `/api/observation/{cc}/advance` | Avanzar fase del protocolo |
| POST | `/api/observation/{cc}/finalize` | Cerrar sesión de observación |
| GET | `/api/observation/{cc}/entries` | Listar hallazgos con filtros |
| GET | `/api/observation/{cc}/patterns` | Patrones de fraude detectados |
| GET | `/api/observation/{cc}/status` | Estado de la sesión activa |
| GET | `/api/observation/{cc}/sessions` | Historial de sesiones |
| GET | `/api/observation/{cc}/report` | Reporte de observación |

### OSINT automatizado

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/hunter/{cc}/run` | Ejecutar Hunter Agent (OSINT + clasificación LLM) |
| GET | `/api/sentinel/alerts` | Alertas electorales + hallazgos recientes |
| GET | `/api/ooni/{cc}/status` | Estado de censura internet (OONI) |
| GET | `/api/ooni/{cc}/anomalies` | Detalles de anomalías web |

### País y evaluación

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/country/{cc}` | Perfil completo del país |
| GET | `/api/country/{cc}/chartdata` | Datos para gráficos |
| GET | `/api/instruments/{cc}` | Instrumentos legales aplicables |
| GET | `/api/moe/brief/{cc}` | Brief del organismo electoral |
| GET | `/api/evaluation/{cc}/questionnaire` | Cuestionario de evaluación MOE |
| POST | `/api/evaluation/{cc}/save` | Guardar respuestas de evaluación |
| GET | `/api/evaluation/{cc}/compare` | Comparar contra línea base |
| GET | `/api/peru/actors` | Actores políticos Perú 2026 |
| GET | `/api/peru/scenarios` | Escenarios electorales Perú 2026 |

---

## 6. Frontend — Dashboard interactivo

### 6.1 Vistas principales (6)

| Vista | Descripción |
|---|---|
| **Overview** | Grid de 38 países con cards de riesgo, búsqueda y filtros |
| **Análisis País** | Reporte VIP interactivo: gauges, radars, heatmaps, violaciones |
| **Sentinel** | Monitoreo en tiempo real: alertas activas, watchlist, hallazgos recientes del Hunter |
| **Perú 2026** | Situation room dedicada: countdown, actores, escenarios, encuestas, observación |
| **Observación** | Interfaz para observadores de campo: registro de hallazgos, histórico |
| **Metodología** | Documentación de cada gráfico: qué mide, cómo se calcula, fuentes, interpretación |

### 6.2 Componentes React (31)

Componentes de UI: `GlowDot`, `RiskGauge`, `RiskGaugeElite`, `Card`, `Tag`, `SectionTitle`, `AnimatedCounter`, `LoadingScreen`, `ErrorScreen`, `SystemHealth`, `Navbar`, `CountryCard`, `CircularScore`, `BarMeter`, `TooltipInfo`, `InfoIcon`, `SourceBadge`, `GlossaryCard`, `DimensionBar`, `CivilLibertiesSemaphore`

Componentes de datos: `AlertCard`, `ViolationCard`, `ViolationHeatmap`, `EMBStatusPanel`, `IntelligenceSourceRow`, `SentinelCard`, `FindingCard`

Vistas: `OverviewView`, `DetailView`, `SentinelView`, `PeruSituationRoom`, `ObserverView`, `MethodologyView`, `ReportViewer`

### 6.3 Visualizaciones (Recharts)

- **BarChart** — Distribución de exposición mediática, comparativas
- **RadarChart** — Análisis multidimensional de integridad electoral
- **LineChart** — Evolución temporal de índices de riesgo
- **AreaChart** — Tendencias con área sombreada
- **PieChart** — Distribución proporcional

### 6.4 Diseño

- **Theme:** Dark mode profesional (`#0a0e17` fondo, `#00d4aa` acento teal)
- **Tipografía:** DM Sans (texto), DM Mono (datos/código)
- **Responsive:** Grid auto-fit, flexbox
- **Severidad visual:** Rojo crítico → Naranja alto → Amarillo moderado → Teal bajo
- **Bundle:** 939KB JS, 0.91KB CSS (producción optimizada)

---

## 7. Base de datos — SQLite

### 7.1 Schema (8 tablas)

| Tabla | Propósito | Registros típicos |
|---|---|---|
| `analysis_runs` | Ejecuciones del pipeline | run_id, country, risk_score, status |
| `reports` | Reportes generados | Markdown + JSON + capítulos |
| `observation_sessions` | Sesiones de observación | Por país, fase, observadores |
| `observation_entries` | Hallazgos individuales | Categoría, severidad, ubicación, evidencia |
| `detection_patterns` | Patrones de fraude | Tipo, distritos, score, escalación |
| `alerts` | Alertas despachadas | Canales, respuesta, timestamp |
| `ooni_snapshots` | Snapshots de censura | URLs bloqueadas, anomalías |
| `_schema_meta` | Control de versión del schema | version=1 |

### 7.2 CRUD (18 funciones)

Runs: `create_run`, `complete_run`, `get_run`, `list_runs`
Reports: `save_report`, `get_report`, `get_latest_report`
Sessions: `create_session`, `close_session`, `get_session`
Entries: `save_entry`, `get_entries`
Patterns: `save_pattern`
Alerts: `save_alert`, `list_alerts`
OONI: `save_ooni_snapshot`, `get_latest_ooni`
Stats: `get_db_stats`

---

## 8. Testing

| Archivo | Tests | Cobertura |
|---|---|---|
| `test_config_and_modules.py` | 18 | Configuración, catálogo, instrumentos |
| `test_data_loaders.py` | 9 | V-Dem, Freedom House, RSF, PEI |
| `test_db.py` | 30 | CRUD completo, deduplicación, alertas |
| `test_field_validator.py` | 6 | Validación, patrones, calidad |
| `test_e2e_pipeline.py` | 10 | Pipeline end-to-end |
| `test_elite_pipeline.py` | 9 | Sprint 1: VizKind dispatch, FindingRef, PredictiveEngine, attach_visualizations, render SVG, ChapterComposer no-LLM, `_format_vdem_emb`, disclosure presence |
| `conftest.py` | — | Fixtures: DB temporal, mocks |
| **TOTAL** | **91 tests** | **100% passing** (~8s) |

---

## 9. Workflow de desarrollo y deploy

### 9.1 Desarrollo local

```
d:\DemocracIA> .\arrange_all.ps1
  → Backend: http://localhost:8000 (FastAPI + Swagger en /docs)
  → Frontend: http://localhost:5173 (Vite HMR)
  → Tests: C:/Python314/python.exe -m pytest backend/tests/ -v
```

### 9.2 CI/CD Pipeline

```
git push origin main
    ├──> Railway detecta cambio → rebuild backend → health check → deploy
    └──> Netlify detecta cambio → npm run build → publish dist/ → deploy
```

### 9.3 Variables de entorno en producción (Railway)

| Variable | Valor | Función |
|---|---|---|
| `ANTHROPIC_API_KEY` | sk-ant-... | LLM para análisis y clasificación |
| `OBSERVER_API_KEYS` | clave-produccion-2026 | Autenticación de observadores |
| `ALLOWED_ORIGINS` | https://www.democracia.ar,https://democracia.ar | CORS |
| `ALERT_WEBHOOK_URL` | https://discord.com/api/webhooks/... | Alertas a Discord |
| `ALERT_MIN_SEVERITY` | high | Umbral mínimo para alertas |
| `HUNTER_INTERVAL_MINUTES` | 1440 | Hunter automático cada 24h (configurable) |
| `AUTO_OBSERVE_COUNTRIES` | PER | Auto-crear sesión de observación en startup |
| `MAX_ELITE_PER_DAY` | 20 | Budget diario de Elite Reports por país |
| `VDEM_VERSION` | v16 | Versión del dataset V-Dem en uso |
| `VDEM_LAST_YEAR` | 2025 | Año más reciente cubierto por el dataset |
| `DEMOCRACIA_DB_PATH` | /data/democracia.db | Path al SQLite en volumen Railway |

### 9.4 Variables de entorno en producción (Netlify)

| Variable | Valor | Función |
|---|---|---|
| `VITE_API_BASE` | https://democracia-peirs-production.up.railway.app | URL del backend |
| `NODE_VERSION` | 20 | Versión de Node para build |

---

## 10. Estado del sitio web en producción

### 10.1 Verificación en vivo (4 mayo 2026)

| Servicio | URL | Estado |
|---|---|---|
| Frontend | <https://democracia.ar> | OPERATIVO (200 OK, Netlify) |
| Backend | <https://democracia-peirs-production.up.railway.app> | OPERATIVO (recovery exitoso 4-may) |
| Health check | `/api/health` | version 0.5.2, 38 países, 14 instrumentos legales, V-Dem v16 |
| RAG legal | ChromaDB | ACTIVO (init en background) |
| OONI | Integración | ACTIVA |
| Hunter scheduler | 14 fuentes RSS (8 PER + 6 intl) | ACTIVO cada 24h |
| Alertas Discord | Webhook | CONFIGURADO Y PROBADO |
| Sesión observación PER 2026 | Volumen SQLite | ACTIVA, restaurada tras incidente Railway |
| SSL | Let's Encrypt | Renovación automática |

### 10.2 Features activos en producción

```json
{
  "features": [
    "country_profile",
    "electoral_observation_protocol",
    "traceability",
    "vdem_v16",
    "freedom_house",
    "pei_v10",
    "rsf_index",
    "ooni_live",
    "fraud_hate_analysis",
    "rag_legal",
    "constitutionalist",
    "report_designer",
    "elite_report"
  ],
  "llm_configured": true,
  "active_observation_sessions": 1,
  "observer_keys_configured": 1,
  "alert_dispatch": true,
  "alert_channels_configured": { "webhook": true }
}
```

---

## 11. Logros alcanzados

### 11.1 Producto

- Sistema de inteligencia electoral funcional, en producción, accesible en <https://democracia.ar>
- Pipeline LangGraph 4 agentes + Elite Report 6-etapas generando informes de 12 capítulos + 3 anexos
- i18n trilingüe (es / en / pt) con 180+ claves cubriendo todo el chrome del informe
- Protocolo completo de observación electoral (9 fases, 19 categorías)
- Hunter Agent automático cada 24h rastreando 14 fuentes RSS (8 nacionales + 6 internacionales filtradas por keyword "Peru") con clasificación Sonnet 4.6
- Alertas en tiempo real a Discord para hallazgos ≥ high
- RAG legal con 14 instrumentos jurídico-electorales en ChromaDB
- Monitoreo OONI de censura internet en tiempo real
- SQLite triple-tier: filesystem + TEXT columns + PDF on-demand. Sobrevive a corrupción del volumen
- Architect Agent autónomo (Claude Opus 4.7 + claude-agent-sdk) para refactor iterativo

### 11.2 Técnicos

- ~15,000 LOC Python (backend: `app.py` 5400+ líneas + módulos)
- ~5,000 LOC React (single-file `App.jsx`)
- 39+ endpoints API documentados
- 91 tests automatizados, 100% passing en ~8s
- Deploy automatizado: push a GitHub → Railway primario + Netlify rebuild (secundario con auto-deploy desactivado por seguridad)
- 38 países en catálogo, 4 con datos reales confirmados (VEN, NIC, GTM, URY) + Perú con cobertura activa
- Base de datos SQLite con 8 tablas + tablas Elite Report con TEXT columns
- Fallbacks en cada capa garantizan que el sistema nunca falla completamente
- Backup script (`scripts/backup.py --targz`) para snapshot single-file de prod

### 11.3 Operativos

- Dominio propio: democracia.ar con SSL auto-renovable
- Perú 2026 como caso de estudio activo (elecciones 12 abril 2026)
- Sesión de observación auto-bootstrapped en cada deploy
- Integración Discord operativa para alertas electorales

### 11.4 Evolución del proyecto (~55 días)

| Fecha | Hito |
|---|---|
| 11 mar 2026 | PEIRS v0.2 — LangGraph + FastAPI + React dashboard + trazabilidad |
| 12 mar 2026 | Integración Freedom House, V-Dem v15 real, PEI v10 |
| 25 mar 2026 | SQLite, informe Perú enriquecido, timeline crisis democrática |
| 27 mar 2026 | Arquitectura v0.4: agents/, chapters/, db/, tests/ |
| 1 abr 2026 | Hunter Agent, protocolo multi-sesión, deploy config |
| 4-5 abr 2026 | Deploy a producción, fix port mismatch, RAG ChromaDB activo, Discord alertas |
| 14-20 abr 2026 | Elite Report 12 capítulos + 3 anexos, ReportDesigner sub-agente |
| 27 abr 2026 | v0.5.0 — Constitucionalista RAG, Architect Agent autónomo, hardening producción, migración SQLite |
| 4 may 2026 | v0.5.2 — i18n profundo (es/en/pt), V-Dem v16 upgrade, Sprint 1 tests (91/91), backup script, /printable, /structured. Recuperación incidente Railway. Disclosure neutral |

**~75 commits en ~55 días.** De prototipo a producción + i18n trilingüe + caso de uso activo.

---

## 12. Próximos pasos

### 12.1 Sprints blockers para BRA + USA (próximas 4-6 semanas)

| Prioridad | Sprint | Esfuerzo | Bloquea |
|---|---|---|---|
| P0 | **Sprint 2 — CountryAdapter pluggable** | 4-6h | Onboarding Brasil, USA |
| P0 | **Sprint 3 — Modelo institucional generalizado** | 6-8h | Federal centralizado (BRA), federal descentralizado (USA) |
| P1 | **Sprint 4 — Traducir 13 prompts cap_NN.md a en/pt** | 8-10h | Eliminar últimos restos de español en narrativa LLM |

### 12.2 Cobertura electoral H2 2026

| Sprint | Calendario | Esfuerzo |
|---|---|---|
| **Sprint 5 — Brasil 2026 onboarding** | Antes 4-oct-2026 | 10-12h |
| **Sprint 6 — USA 2026 midterms onboarding** | Antes 3-nov-2026 | 12-16h |

### 12.3 Mediano plazo (paralelo, 1-3 meses)

| Tarea | Descripción |
|---|---|
| **Frontend feature flags + preview unlock** | Tabs Brasil / USA con `?preview=DEMOCRACIA_PREVIEW_2026` |
| **Citation builder i18n** | Meses en español, "Recuperado de" → "Retrieved from" |
| **Predictive scenarios narrative i18n** | Implications/indicators/watch_signals en es dentro de narrativa |
| **PostgreSQL** | Evaluar migración desde SQLite si concurrencia lo justifica |
| **Tests E2E integración Railway** | Smoke tests contra API real post-deploy |
| **Monitoring** | Dashboard Railway metrics para uptime y latencia LLM |
| **Backup automatizado** | Cron diario invocando `scripts/backup.py --targz` |

### 12.4 Largo plazo (6-12 meses)

| Tarea | Descripción |
|---|---|
| **Neo4j** | Grafo de redes de poder: partidos, financistas, medios |
| **NLP avanzado** | Análisis de sentimiento en redes sociales (Twitter/X, TikTok) |
| **Playwright scraping** | OSINT profundo: scraping de portales electorales |
| **API pública con tiers** | Abrir API para investigadores y periodistas |
| **App móvil** | PWA para observadores en campo sin conexión |
| **Multi-idioma adicional** | Francés (África francófona) |
| **Detección estadística de anomalías** | Hunter detecta cambios de tasa, no sólo clasifica |

---

## 13. Métricas del proyecto

| Métrica | Valor |
|---|---|
| Líneas de código backend | ~15,000 |
| Líneas de código frontend | ~5,000 (single-file `App.jsx`) |
| Endpoints API | 40+ (incluye `/structured`, `/printable`, `/elite-report/*`) |
| Pipelines de análisis | 2 (LangGraph 4 agentes + Elite Report 6 etapas) |
| Agentes IA | 7 (4 LangGraph + Hunter + Auditor + Architect Agent autónomo) |
| Tests | 91 (100% passing en ~8s) |
| Países monitoreados | 38 |
| Países con cobertura activa | 1 (Perú 2026) |
| Fuentes de datos | 6 (V-Dem v16, FH, RSF, PEI, OONI, Hunter RSS) |
| Instrumentos legales | 14 |
| Idiomas soportados | 3 (es / en / pt) |
| Claves i18n | 180+ |
| Categorías Hunter | 19 |
| Fases electorales | 9 |
| Capítulos Elite Report | 12 + 3 anexos |
| Visualizaciones SVG | 21 server-side |
| Escenarios predictivos | 6 con bandas de confianza |
| Commits | ~75 en ~55 días |
| Tiempo a producción + i18n trilingüe | ~55 días |

---

## 14. Información de contacto y repositorio

| Item | Valor |
|---|---|
| Repositorio | https://github.com/lachmanmariana8-sudo/democracia-peirs |
| Sitio web | https://www.democracia.ar |
| Backend API | https://democracia-peirs-production.up.railway.app |
| Swagger docs | https://democracia-peirs-production.up.railway.app/docs |
| Branch principal | main |
| Licencia | Pendiente de definir |

---

*Documento actualizado el 4 de mayo de 2026. DEMOCRAC.IA / PEIRS v0.5.2.*
*De prototipo a producción + i18n trilingüe + caso de uso activo en ~55 días.*
*Inteligencia electoral para todos.*
