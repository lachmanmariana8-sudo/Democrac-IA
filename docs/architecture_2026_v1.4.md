# DEMOCRAC.IA / PEIRS
## Architecture Document — Diagnostics & Implementation Roadmap
### Edición técnica interna · Marzo 2026 · v1.4

---

## 1. Visión del Sistema

**PEIRS** (Predictive Electoral Integrity & Risk System) es la infraestructura técnica de DEMOCRAC.IA. Su función central es orquestar una cadena de agentes de inteligencia artificial que procesan datos electorales verificados, evalúan el cumplimiento del derecho internacional y generan informes auditables de riesgo electoral.

El sistema opera bajo tres principios arquitecturales invariables:

1. **Trazabilidad total** — cada hallazgo tiene fuente primaria identificada, timestamp UTC y nivel de confianza declarado
2. **Fallback gracioso** — toda integración externa (LLM, OONI, RAG, alertas) tiene implementación de contingencia; el sistema no falla en silencio
3. **Mejora continua guiada** — el Expert Architect Agent audita el sistema y propone mejoras estructurales en cada ciclo

---

## 2. Topología del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                     BROWSER (localhost:5173)                      │
│              React 19 + Vite 7 + Recharts 3                      │
│   Dashboard · Análisis País · SENTINEL · Perú 2026 · Observación │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP REST  (localhost:8001)
┌──────────────────────▼──────────────────────────────────────────┐
│                   BACKEND — FastAPI + LangGraph                   │
│                                                                   │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │         PIPELINE LANGGRAPH (5 agentes secuenciales)      │   │
│   │  Ingestion → PoliticalAnalyst → LegalCompliance          │   │
│   │           → DictamenAgent → ReportGenerator              │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│   │ Agent 5      │  │  Agent 7     │  │  Expert Architect     │   │
│   │ FieldValidator│  │ AlertDispatch│  │  Agent (meta-agente) │   │
│   └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                   │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │  MÓDULOS DE SOPORTE                                       │   │
│   │  data_loaders · catalog · instruments · field_validator   │   │
│   │  fraud_hate_analysis · peru_data · mock_data · config    │   │
│   └──────────────────────────────────────────────────────────┘   │
└──────┬─────────────────────┬──────────────────────┬─────────────┘
       │                     │                      │
┌──────▼──────┐    ┌─────────▼──────┐    ┌──────────▼──────────┐
│  SQLite DB  │    │  RAG (ChromaDB)│    │  Fuentes Externas   │
│  WAL mode   │    │  60+ docs      │    │  OONI · Claude API  │
│  8 tablas   │    │  legales       │    │  Slack/Webhook/SMTP │
└─────────────┘    └────────────────┘    └─────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────┐
│  DATASETS PRIMARIOS (locales)                                    │
│  V-Dem v15 (383 MB) · FH FIW 2025 · RSF 2025 · PEI v10.0       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Stack Tecnológico

| Capa | Tecnología | Versión | Función |
|---|---|---|---|
| API Framework | FastAPI | ≥ 0.115 | Endpoints REST, validación Pydantic, CORS |
| Orquestación de agentes | LangGraph | ≥ 0.2.0 | DAG de 5 nodos, gestión de estado |
| LLM — análisis | Claude Sonnet | claude-sonnet-4-6 | Narrativas, análisis político |
| LLM — arquitectura | Claude Opus | claude-opus-4-6 | Auditoría sistémica, adaptive thinking |
| Runtime | Python | 3.14 | Backend completo |
| Base de datos | SQLite (WAL) | nativa | Persistencia transaccional |
| Vector store | ChromaDB | ≥ 0.5.0 | RAG legal (opcional) |
| Embeddings | sentence-transformers | ≥ 3.0.0 | Búsqueda semántica (opcional) |
| HTTP client | httpx | ≥ 0.27.0 | OONI API, integraciones externas |
| Procesamiento datos | pandas | ≥ 2.0.0 | Carga y normalización datasets |
| Frontend | React + Vite | 19.2 + 7.3 | Interfaz de usuario |
| Visualización | Recharts | 3.8.0 | Gráficos dinámicos |

---

## 4. Pipeline LangGraph — 5 Agentes Secuenciales

El pipeline implementa un grafo de estado dirigido acíclico (DAG). El estado global `ElectionRiskState` (TypedDict) se pasa inmutablemente entre nodos.

### Estado global (ElectionRiskState)

```python
class ElectionRiskState(TypedDict):
    # Identificación
    run_id: str
    country: str
    country_code: str
    election_date: str
    timestamp: str

    # Datos de fuentes primarias
    context_data: Dict          # V-Dem, FH, RSF, PEI, OONI indices
    political_data: Dict        # Coaliciones, polarización, medios
    legal_analysis: Dict        # Violaciones por instrumento, severidad

    # Resultado
    risk_score: float           # 0–100
    risk_level: str             # critical / high / moderate / low
    dictamen: str               # Dictamen legal formal

    # Informe
    report_chapters: Dict       # 10 capítulos keyed por sección
    executive_summary: str
    final_report_markdown: str

    # Trazabilidad
    agent_logs: List[Dict]      # Audit trail completo
    trace_log: List[str]        # Log cronológico de operaciones
    errors: List[str]
    applicable_instruments: List[str]
```

### Nodo 1 — Ingestion Agent

**Función:** Recolección, normalización y validación de datos de fuentes primarias.

**Datos consumidos:**
- V-Dem v15 — `libdem`, `v2elembaut`, `v2elembcap`, `v2mebias`, `v2elfinref`, `v2jureview`, `v2psbars`, `v2psoppaut`
- Freedom House FIW 2025 — Political Rights, Civil Liberties
- RSF 2025 — Press Freedom Score
- PEI v10.0 — Electoral Integrity Index
- OONI API — anomalías de red (tiempo real, caché 1h)

**Output:** `context_data` con valores normalizados 0–1 para cada índice.

### Nodo 2 — Political Analyst Agent

**Función:** Análisis del contexto político, coaliciones, dinámica institucional, amenazas digitales.

**Proceso:**
1. Evalúa independencia del OGE (V-Dem `v2elembaut`, `v2elembcap`)
2. Analiza sesgo mediático y libertad de prensa (V-Dem `v2mebias` + RSF)
3. Calcula nivel de polarización y barreras para la oposición
4. Integra señales OONI para ecosistema digital
5. Genera perfil de riesgo político contextualizado

**Output:** `political_data` con scores dimensionales y factores de riesgo.

### Nodo 3 — Legal Compliance Agent

**Función:** Evaluación del cumplimiento del derecho electoral internacional mediante RAG.

**Instrumentos por región:**
- Global: ICCPR, CEDAW, ICERD, CRPD, UNDRIP, UNCAC
- Américas: + CADH, CDI
- Europa: + ECHR-P1, Documento Copenhague
- África: + ACHPR, ACDEG
- Asia-Pacífico: + Bangkok Declaration
- Mundo Árabe: + Carta Árabe

**Output:** `legal_analysis` con violaciones detectadas, artículos referenciados y nivel de confianza.

### Nodo 4 — Electoral Dictamen Agent

**Función:** Dictamen legal formal y cálculo del IRE.

**Fórmula IRE:**
```
IRE = base_score(libdem, FH, PEI)
    + violation_weight(legal_violations × 0.15)
    + emb_score(autonomía, capacidad OGE)
    + media_score(RSF, v2mebias)
    + digital_score(OONI_anomalies)
    → normalizado 0–100
```

**8 dimensiones del radar:**

| Dimensión | Variable fuente |
|---|---|
| `suffrage` | Freedom House Political Rights |
| `legalFramework` | V-Dem libdem |
| `embIndependence` | V-Dem v2elembaut + v2elembcap |
| `mediaFreedom` | V-Dem v2mebias + RSF |
| `campaignFinance` | V-Dem v2elfinref |
| `digitalEcosystem` | OONI anomalías + índice digital |
| `disputeResolution` | V-Dem v2jureview |
| `inclusion` | Freedom House + CRPD |

**Niveles de riesgo:**

| IRE | Nivel |
|---|---|
| 0–29 | LOW |
| 30–49 | MODERATE |
| 50–69 | HIGH |
| 70–100 | CRITICAL |

### Nodo 5 — Report Generator Agent

**Función:** Generación de informe estructurado en 10 capítulos.

| Cap. | Sección | Contenido |
|---|---|---|
| 01 | `country_profile` | Perfil institucional, OGE, contexto demográfico |
| 02 | `executive_summary` | IRE, nivel de riesgo, hallazgos principales |
| 03 | `political_context` | Análisis político, coaliciones, polarización |
| 04 | `emb_chapter` | Evaluación del OGE |
| 05 | `inclusivity` | Participación: mujeres, pueblos indígenas, CRPD |
| 06 | `campaign_chapter` | Campaña, medios, financiamiento |
| 07 | `voting_day` | Observación de campo — 9 fases, 18 categorías |
| 08 | `justice_chapter` | Violaciones de derecho internacional |
| 09 | `recommendations` | Acciones por dimensión de riesgo |
| 10 | `ai_regulation` | Marco normativo de IA en procesos electorales |

---

## 5. Agentes Independientes

### Agent 5 — FieldDataValidationAgent

**Archivo:** `modules/field_validator.py`

| Check | Lógica |
|---|---|
| Campos obligatorios | `finding`, `severity`, `category`, `phase` |
| Longitud mínima | `finding` ≥ 20 caracteres |
| Alertas por severidad | Evidencia requerida en `critical` + `fraud_allegation` |
| Detección de duplicados | Similitud textual ≥ 0.85 + ventana temporal ≤ 5 min |
| Score de calidad | 0.0–1.0 basado en 6 dimensiones ponderadas |

```python
class PatternReport:
    geographic_patterns: List[GeographicPattern]
    category_clusters: List[CategoryCluster]
    multi_observer_corroboration: List[str]
    has_significant_patterns: bool
    fraud_pattern_score: float   # 0.0–1.0
    summary: str
```

### Agent 7 — AlertDispatchAgent

**Archivo:** `integrations/alerts.py`

| Canal | Variable env | Estado default |
|---|---|---|
| Slack | `SLACK_WEBHOOK_URL` | Deshabilitado |
| Webhook genérico | `ALERT_WEBHOOK_URL` | Deshabilitado |
| Email (SMTP) | `SMTP_*` + `ALERT_EMAIL_*` | Deshabilitado |

Activación automática ante `severity = critical/high` en observaciones de campo.

### SENTINEL

Monitor continuo de señales de riesgo en `/api/sentinel/alerts`. Agrega alertas activas con contexto de país y nivel de urgencia.

### Expert Architect Agent

**Archivo:** `agents/architect.py`
**Modelo:** `claude-opus-4-6` + adaptive thinking

```bash
cd backend
PYTHONIOENCODING=utf-8 venv/Scripts/python -m agents.architect --task audit
```

**Tareas:** `audit` · `improve` · `test` · `integrate_db` · `integrate_startup` · `custom`

---

## 6. Protocolo de Observación Electoral

### Ciclo de 9 fases

```
preparatory → pre_campaign → campaign → electoral_silence
           → election_day → counting_tabulation
           → post_election → dispute_resolution → completed
```

Alias de compatibilidad: `pre_election` → `electoral_silence`

### Endpoints del protocolo

```
POST /api/observation/{cc}/start      # Inicia misión (requiere run_id)
POST /api/observation/{cc}/entry      # Registra hallazgo
POST /api/observation/{cc}/advance    # Avanza fase
GET  /api/observation/{cc}/status     # Estado de la misión
GET  /api/observation/{cc}/patterns   # Detección de patrones
GET  /api/observation/{cc}/report     # Capítulo 7 standalone (R1)
```

**Autenticación:** Header `X-Observer-Key`
**Clave dev:** `democracia-obs-dev-2026`

### Validaciones automáticas

- **R3 — Coherencia temporal:** entrada en fase futura se normaliza a la activa + genera `phase_warning`
- **R2 — Rehidratación startup:** `_preload_sessions_on_startup()` carga sesiones activas desde SQLite
- **Derechos autoasignados:** combinación `category × severity` → lista artículos de tratados

### Derechos autoasignados por categoría × severidad (ejemplos)

| Combinación | Derechos asignados automáticamente |
|---|---|
| `campaign_violation\|high` | ICCPR 25, CADH 23, ICCPR 22 |
| `voter_suppression\|critical` | ICCPR 25(b), CADH 23(1)(b), ICERD 5(c), ICCPR 2 |
| `gender_violence\|high` | CEDAW 7, CADH 23, ICCPR 3 |
| `disinformation\|critical` | ICCPR 19(2), CADH 13, ICCPR 25, ICCPR 20 |
| `accessibility\|high` | CRPD 29, CADH 23, ICCPR 25 |

---

## 7. Base de Datos — SQLite (WAL)

**Ubicación:** `data/peirs.db`
**Modo:** WAL — lecturas y escrituras concurrentes
**FK constraints:** habilitados via `PRAGMA foreign_keys = ON`

### Esquema — 8 tablas

```sql
analysis_runs (run_id PK, country_code, started_at, completed_at,
               status, risk_score, risk_level, error_msg)

reports (run_id PK FK→analysis_runs, country_code, election_date,
         risk_score, risk_level, chapters_json, markdown, generated_at)

observation_sessions (session_id PK, country_code, run_id FK→reports,
                      mission_name, lead_org, phase DEFAULT 'preparatory',
                      started_at, updated_at, finalized INT DEFAULT 0, data TEXT)

observation_entries (entry_id PK, session_id FK→observation_sessions,
                     country_code, phase, category, severity, finding,
                     location, timestamp, rights_at_risk, quality_score, verified)

detection_patterns (id PK AUTOINCREMENT, session_id FK,
                    country_code, generated_at, fraud_pattern_score,
                    has_significant_patterns, report_json)

alerts (id PK AUTOINCREMENT, run_id, country_code, alert_type,
        severity, message, dispatched, dispatched_at, channels_json)

ooni_snapshots (id PK AUTOINCREMENT, country_code, captured_at,
                anomaly_count, data_json)

_schema_meta (key PK, value)
```

---

## 8. RAG — Base de Conocimiento Legal

**Vector store:** ChromaDB (local)
**Embeddings:** sentence-transformers `all-MiniLM-L6-v2` (~90MB)
**Corpus:** 60+ documentos legales internacionales (`rag/corpus.py`)

**Consultas disponibles:**
```python
query_legal_context(country_code, query)
query_fraud_context(query)
query_hate_speech_context(query)
format_rag_context_for_llm(results)
```

**Estado:** dependencia opcional. En modo degradado (sin ChromaDB), análisis legal opera mediante reglas codificadas en `instruments.py`.

---

## 9. Fuentes de Datos

| Dataset | Versión | Archivo | Cobertura | Carga |
|---|---|---|---|---|
| V-Dem | v15 (2025) | `V-Dem-CY-Full+Others-v15.csv` (383 MB) | 27.913 filas, 1789–2024 | Startup, caché memoria |
| Freedom House FIW | 2025 | `All_data_FIW_2025_*.csv` | 195 países | Startup, caché |
| RSF Press Freedom | 2025 | `RSF/2025.csv` | 180 países | Startup, caché |
| PEI | v10.0 | `PEI/PEI_10_*.csv` | 586 elecciones 2012–2023 | Startup, caché |
| OONI | API tiempo real | — | 200+ países | On-demand, caché 1h |

**Variables V-Dem utilizadas:**

| Variable V-Dem | Descripción | Dimensión IRE |
|---|---|---|
| `v2x_libdem` | Liberal Democracy Index | legalFramework |
| `v2elembaut` | EMB Autonomy | embIndependence |
| `v2elembcap` | EMB Capacity | embIndependence |
| `v2mebias` | Media Bias | mediaFreedom |
| `v2elfinref` | Campaign Finance Regulation | campaignFinance |
| `v2jureview` | Judicial Review | disputeResolution |
| `v2psbars` | Opposition Party Barriers | legalFramework |
| `v2psoppaut` | Opposition Autonomy | political_data |

---

## 10. Superficie API Completa

### Análisis y reportes

| Endpoint | Método | Auth | Descripción |
|---|---|---|---|
| `/api/health` | GET | — | Health check operacional |
| `/api/countries` | GET | — | Catálogo 38 países |
| `/api/analyze` | POST | — | Ejecuta pipeline completo |
| `/api/report/{run_id}` | GET | — | Informe JSON completo |
| `/api/report/{run_id}/markdown` | GET | — | Informe Markdown |
| `/api/dashboard` | GET | — | KPIs todos los países activos |
| `/api/country/{code}` | GET | — | Perfil individual + dimensiones |
| `/api/stats` | GET | — | Estado del sistema |
| `/api/sentinel/alerts` | GET | — | Alertas SENTINEL activas |

### Protocolo de Observación

| Endpoint | Método | Auth | Descripción |
|---|---|---|---|
| `/api/observation/{cc}/start` | POST | Observer-Key | Inicia sesión |
| `/api/observation/{cc}/entry` | POST | Observer-Key | Registra hallazgo |
| `/api/observation/{cc}/advance` | POST | Observer-Key | Avanza fase |
| `/api/observation/{cc}/finalize` | POST | Observer-Key | Cierra ciclo |
| `/api/observation/{cc}/status` | GET | — | Estado de la misión |
| `/api/observation/{cc}/patterns` | GET | Observer-Key | Patrones sistémicos |
| `/api/observation/{cc}/report` | GET | — | Cap. 7 standalone |

---

## 11. Frontend — Componentes y Vistas

**Archivo principal:** `frontend/src/App.jsx` (~6.200 líneas)

| Vista | ID | Descripción |
|---|---|---|
| Overview | `overview` | KPIs globales, radar 8 ejes, timeline histórica |
| Análisis País | `country` | Perfil, dimensiones, alertas individuales |
| SENTINEL | `sentinel` | Alertas activas, monitoreo |
| Perú 2026 | `peru` | Vista focal con datos detallados |
| Observación | `observer` | Protocolo de campo: 9 fases, 18 categorías |

**Componentes destacados:**

| Componente | Función |
|---|---|
| `SystemHealth` | Badge DB ● RAG ● N runs (actualiza cada 60s) |
| `ObserverView` | Formulario de campo con validación live |
| `PeruSituationRoom` | Vista focal + botón "Generar Nuevo Análisis" |
| `generateHtmlReport()` | Informe HTML A4 imprimible con toolbar |

---

## 12. Configuración del Entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `ANTHROPIC_API_KEY` | Sí* | API key Anthropic |
| `OBSERVER_API_KEYS` | No | Claves observadores (default: `democracia-obs-dev-2026`) |
| `VDEM_CSV_PATH` | No | Ruta V-Dem v15 |
| `FH_CSV_PATH` | No | Ruta Freedom House FIW |
| `RSF_CSV_PATH` | No | Ruta RSF |
| `PEI_CSV_PATH` | No | Ruta PEI |
| `PEIRS_DB_PATH` | No | Ruta SQLite (default: `data/peirs.db`) |
| `SLACK_WEBHOOK_URL` | No | Alertas Slack |
| `ALERT_WEBHOOK_URL` | No | Webhook genérico |
| `SMTP_*` | No | Email alerts |

*Sin `ANTHROPIC_API_KEY`: modo degradado con fallback textual (funcional, no narrativo LLM).

**Variables futuras (infraestructura producción):**
```env
POSTGRES_URL=postgresql://...
NEO4J_URI=bolt://...
PINECONE_API_KEY=...
```

---

## 13. Suite de Tests

**Framework:** pytest · **65 tests · 100% pasando**

| Archivo | Dominio |
|---|---|
| `test_config_and_modules.py` | Configuración y módulos |
| `test_data_loaders.py` | V-Dem, FH, RSF, PEI loaders |
| `test_db.py` | SQLite CRUD, esquema, WAL |
| `test_field_validator.py` | Validación, duplicados, patrones, calidad |
| `conftest.py` | Fixtures (monkeypatch, paths) |

```bash
cd backend
PYTHONIOENCODING=utf-8 venv/Scripts/python -m pytest tests/ -q
# → 65 passed in ~3s
```

---

## 14. Diagnósticos del Estado Actual

### ✅ Operacional y validado

| Componente | Notas |
|---|---|
| Pipeline LangGraph (5 agentes) | Modo degradado sin API key |
| Datasets V-Dem, FH, RSF, PEI | Cargados en memoria al startup |
| OONI API (tiempo real) | httpx disponible, caché 1h |
| SQLite WAL (8 tablas) | FK constraints activos |
| Protocolo observación 9 fases | R4: fases completas |
| 18 categorías + derechos automap | R5: ICCPR/CADH/CEDAW/CRPD |
| Rehidratación de sesiones | R2: recovery automático |
| Validación coherencia temporal | R3: phase_warning |
| Endpoint `/observation/{cc}/report` | R1: Cap. 7 standalone |
| Agent 5 (FieldValidator) | quality_score, duplicados, patrones |
| Agent 7 (AlertDispatch) | Sin canales configurados → no-op |
| Expert Architect Agent | Requiere ANTHROPIC_API_KEY |
| Dashboard React (5 vistas) | SystemHealth badge activo |
| Impresión A4 HTML | CSS @media print, toolbar |
| Suite de tests (65) | 100% pasando |

### ⚠️ Funcional con limitaciones

| Componente | Limitación | Impacto |
|---|---|---|
| Generación LLM | Requiere ANTHROPIC_API_KEY | Sin key: fallback textual |
| RAG (ChromaDB) | No instalado por defecto | Análisis legal por reglas codificadas |
| Alertas | Sin canales en entorno dev | Log interno, no despacho |
| `app.py` monolítico | 6.900 líneas — migración en curso | Mantenibilidad; funcionalidad OK |
| Puerto 8000 | Ghost sockets Windows | Sistema operacional en 8001 |
| `API_BASE` hardcoded | `localhost:8001` en App.jsx | Cambio manual para producción |

### ❌ Pendiente de implementación

| Feature | Prioridad | Descripción |
|---|---|---|
| Multi-sesión por país (R6) | Alta | Segunda vuelta sin perder datos primera |
| Filtros en `/entries` (R7) | Alta | `?phase=`, `?severity=`, `?category=` |
| Gráficos V-Dem en informe Perú | Alta | Charts interactivos con datos reales |
| Migración agents → `nodes.py` | Media | Extraer 5 agentes de `app.py` |
| Migración capítulos → `generators.py` | Media | Extraer 10 funciones `_generate_*` |
| Test de integración API | Media | Endpoints observación end-to-end |
| Variables entorno en frontend | Media | `import.meta.env.VITE_API_BASE` |

---

## 15. Roadmap de Implementación

### Sprint completado (al 2026-03-28)

| ID | Feature | Archivos |
|---|---|---|
| R1 | `GET /api/observation/{cc}/report` | `app.py` |
| R2 | Rehidratación sesiones SQLite→memoria | `app.py` |
| R3 | Validación coherencia temporal fase | `app.py` |
| R4 | Modelo 9 fases electorales | `app.py`, `App.jsx` |
| R5 | 18 categorías + derechos automap | `app.py`, `App.jsx` |

### Sprint siguiente (R6–R10)

| ID | Feature | Prioridad | Complejidad |
|---|---|---|---|
| R6 | Multi-sesión por país | Alta | Media |
| R7 | Filtros en `/entries` | Alta | Baja |
| R8 | Gráficos V-Dem en informe Perú HTML | Alta | Media |
| R9 | Migración agentes → `agents/nodes.py` | Media | Alta |
| R10 | Migración capítulos → `chapters/generators.py` | Media | Alta |

### Roadmap Q2–Q4 2026

| Período | Meta | Prerrequisito |
|---|---|---|
| Q2 2026 | Multi-sesión + filtros + gráficos V-Dem | R6, R7, R8 |
| Q2 2026 | 60 países en catálogo | catalog.py + datasets |
| Q3 2026 | Variables entorno frontend + modo producción | — |
| Q3 2026 | Auth OAuth2 para API institucional | — |
| Q3 2026 | PostgreSQL como alternativa a SQLite | R9, R10 |
| Q4 2026 | 80 jurisdicciones monitoreadas | Expansión datasets |
| Q4 2026 | Motor i18n — EN/PT en informes | Componente nuevo |

### Visión 2027–2028

| Año | Meta |
|---|---|
| 2027 | 120 jurisdicciones · Módulo segunda vuelta · Validación institucional |
| 2027 | Dashboard tiempo real con fuentes de prensa |
| 2028 | 193 jurisdicciones (cobertura ONU completa) |
| 2028 | Neo4j para análisis de redes de influencia |

---

## 16. Guía de Desarrollo

### Arrancar el sistema localmente

```bash
# Backend
cd d:/DemocracIA/backend
PYTHONIOENCODING=utf-8 venv/Scripts/python -m uvicorn app:app --port 8001 --host 127.0.0.1

# Frontend
cd d:/DemocracIA/frontend
npm run dev

# Tests
cd d:/DemocracIA/backend
PYTHONIOENCODING=utf-8 venv/Scripts/python -m pytest tests/ -q

# Expert Architect Agent
cd d:/DemocracIA/backend
PYTHONIOENCODING=utf-8 venv/Scripts/python -m agents.architect --task audit
```

### Agregar un nuevo país

1. `modules/catalog.py` — código ISO 3-letras, nombre, bandera, fecha elección, región
2. `modules/instruments.py` → `COUNTRY_REGIONS` + `EMB_NAMES`
3. Verificar cobertura en V-Dem y FH para el código país

### Agregar una nueva categoría de observación

1. `app.py` → `_CATEGORY_LABEL` (nombre legible)
2. `app.py` → `_RIGHTS_AUTOMAP` (derechos por severidad)
3. `frontend/src/App.jsx` → `OBS_CATEGORIES` (id + label)

### Convenciones de código

- Toda función LLM tiene fallback: `_llm_generate(sys_prompt, user_prompt, fallback_fn)`
- Toda conexión SQLite usa context manager `_get_db()`
- Nivel de confianza declarado en cada hallazgo: `confirmed / probable / unverified`
- Unicode en consola Windows: siempre `PYTHONIOENCODING=utf-8`
- Nunca usar `Stop-Process` en ghost sockets Windows — reiniciar sesión de terminal

---

*DEMOCRAC.IA / PEIRS — Documento interno de arquitectura*
*Edición 2026 v1.4 — Actualización: marzo 2026*
*© Agora Data*
