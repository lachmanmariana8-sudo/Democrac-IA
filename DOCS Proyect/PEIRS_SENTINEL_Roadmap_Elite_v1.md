# DEMOCRAC.IA — Roadmap Elite Premium
## Integración PEIRS Knowledge Base + SENTINEL Real-Time
*Versión: 1.0 — Fecha: 2026-03-22*

---

## VISIÓN

Democrac.IA será la **plataforma de referencia global** para inteligencia electoral basada en IA.
Combinará una base de conocimiento histórico de 50 años (PEIRS) con monitoreo en tiempo real
(SENTINEL), produciendo informes de calidad equivalente a los de la OEA, OSCE/ODIHR y el
Centro Carter — pero automatizados, escalables y disponibles en minutos, no en semanas.

**No legitimamos elecciones. Emitimos inteligencia electoral con trazabilidad verificable.**

---

## ARQUITECTURA ELITE — Visión General

```
╔══════════════════════════════════════════════════════════════════════╗
║                        DEMOCRAC.IA v1.0                             ║
╠══════════════════════╦═══════════════════════════════════════════════╣
║   PEIRS              ║   SENTINEL                                   ║
║   Knowledge Base     ║   Real-Time Intelligence                     ║
║                      ║                                              ║
║  • V-Dem v15         ║  • Calendario electoral global               ║
║  • Freedom House     ║  • OSINT feeds (noticias, ONG, EMBs)        ║
║  • PEI 10.0          ║  • Social Media Monitor                      ║
║  • RSF 2025          ║  • Alertas automáticas por umbral            ║
║  • V-Dem histórico   ║  • WebSocket — alertas en vivo               ║
║  • PostgreSQL        ║  • Predictor ML                              ║
╠══════════════════════╩═══════════════════════════════════════════════╣
║              MOTOR DE ANÁLISIS — LangGraph + Claude                 ║
║                                                                      ║
║   Agente OSINT → Agente Político → Agente Legal → Agente Informe    ║
║   + Agente MOE (Misiones) + Agente Mejora Continua                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                      CAPA DE SALIDA                                  ║
║                                                                      ║
║   Dashboard Elite  ·  Informe VIP PDF  ·  MOE Brief  ·  API REST    ║
║   Estadísticas     ·  Comparativas     ·  Embeddings ·  Webhooks    ║
╠══════════════════════════════════════════════════════════════════════╣
║              AGENTE DE MEJORA CONTINUA (automatizado)                ║
║   Diagnostica → Benchmarks → Propone → Genera reporte → Issues      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## ESTADO ACTUAL (v0.3.2 — baseline)

| Componente | Estado | Calidad |
|---|---|---|
| Pipeline LangGraph 4 agentes | ✅ Operativo | Producción |
| V-Dem v15 integrado | ✅ Real | Verificado |
| Freedom House FIW integrado | ✅ Real | Verificado |
| PEI 10.0 integrado | ✅ Real | Verificado |
| RSF integrado | ✅ Real | Verificado |
| Informes VIP markdown | ✅ Cap. 1,2,3,4,5,6,8,9 | Producción |
| Cap. 7 Día de Votación | ✅ Tiempo real | Producción |
| Dashboard React con tabs | ✅ Operativo | Producción |
| Persistencia en disco (JSON) | ✅ Operativo | Funcional |
| 4 países monitoreados | ✅ VEN, NIC, GTM, URY | Producción |
| SENTINEL | ❌ No existe | — |
| MOE Brief | ❌ No existe | — |
| SQLite/PostgreSQL | ❌ JSON files | — |
| API pública | ❌ No existe | — |
| PDF export | ❌ Solo HTML | — |
| Agente Mejora Continua | ❌ No existe | — |

---

## ROADMAP POR FASES

---

### FASE v0.4.0 — FUNDACIÓN DE DATOS ELITE
*Objetivo: Base sólida para escalar. Sin esto nada de lo siguiente es posible.*

#### Backend
- **SQLite → migrar a PostgreSQL**
  - Una tabla `reports` con índice por país + fecha + risk_score
  - Una tabla `countries` con metadata y configuración
  - Una tabla `elections_calendar` para SENTINEL
  - Una tabla `sentinel_alerts` para alertas en tiempo real
  - Conexión via SQLAlchemy (ya disponible en FastAPI)

- **Escalar a 38 países**
  - América Latina: Argentina, Bolivia, Brasil, Chile, Colombia, Ecuador, El Salvador, Guatemala, Haití, Honduras, México, Nicaragua, Paraguay, Perú, Rep. Dominicana, Uruguay, Venezuela
  - Europa del Este: Bielorrusia, Hungría, Moldova, Rusia, Ucrania
  - África Subsahariana: Camerún, Congo, Etiopía, Nigeria, Zimbabue
  - Asia: Bangladesh, Filipinas, Myanmar, Pakistán, Tailandia
  - Resto: Turquía, Serbia, Georgia, Armenia, Azerbaiyán

- **Endpoint `/api/stats/global`**
  - Distribución de risk levels por región
  - Ranking de países por riesgo
  - Tendencia global 2013–2025 (V-Dem histórico)
  - Países con peor deterioro en los últimos 5 años

- **Batch processing en background**
  - `/api/dashboard` no bloquea — genera países en background tasks
  - FastAPI BackgroundTasks con progress tracking
  - Cache de 24h por país (no regenerar si datos no cambiaron)

#### Frontend
- **Tab "🌎 Global" en navegación**
  - Mapa mundial con heat map de riesgo (Recharts o D3)
  - Ranking de países con filtro por región
  - Gráfico de distribución global de risk scores

- **Filtros en el dashboard**
  - Por región geográfica
  - Por nivel de riesgo (CRITICAL / HIGH / MODERATE / LOW)
  - Por tipo de elección (presidencial, legislativa, local)

#### Métricas de éxito v0.4.0
- 38 países analizados en < 5 minutos
- Datos persisten entre reinicios del backend
- Sin errores en la consola del frontend

---

### FASE v0.5.0 — SENTINEL: INTELIGENCIA EN TIEMPO REAL
*Objetivo: Que la plataforma "vea" lo que pasa ahora, no solo lo que pasó.*

#### Módulo SENTINEL — Backend

**`sentinel/calendar.py`**
- Fuente primaria: API de Wikipedia (Wikidata) para calendario electoral
- Fuente secundaria: IFES Election Guide (scraping ético)
- Detección automática de elecciones en los próximos 90 / 30 / 7 días
- Clasificación: presidencial / legislativa / referéndum / local
- Actualización diaria via cron job

**`sentinel/osint_feeds.py`**
- RSS feeds de fuentes verificadas:
  - Reportes de misiones de observación (OEA DECO, OSCE/ODIHR)
  - Comunicados de EMBs oficiales por país
  - Human Rights Watch, Amnesty International, Freedom House Alerts
  - Reuters, AP, EFE (sección política)
- Extracción de señales de riesgo por keywords:
  - "irregularidades", "intimidación", "censura", "fraude", "violencia"
  - "irregularities", "intimidation", "censorship", "fraud", "violence"
- Score de señal OSINT: 0–10 por elección activa

**`sentinel/social_monitor.py`**
- Monitoreo de hashtags electorales por país (sin API de pago)
- Fuentes: Mastodon, Reddit, foros públicos
- Detección de patrones de desinformación (keywords + frecuencia)
- Integración con OONI para detectar censura de internet

**`sentinel/alert_engine.py`**
- Umbral configurable por país: si SENTINEL score > X → alerta
- 3 niveles de alerta: WATCH / WARNING / CRITICAL
- Trigger automático: regenerar informe del país afectado
- Webhook saliente: notificación a Slack/email cuando hay CRITICAL

**Endpoints nuevos:**
```
GET  /api/sentinel/status           → Estado de monitoreo global
GET  /api/sentinel/calendar         → Elecciones próximas 90 días
GET  /api/sentinel/alerts           → Alertas activas por país
GET  /api/sentinel/country/{code}   → Señales SENTINEL de un país
POST /api/sentinel/trigger/{code}   → Forzar actualización manual
WS   /ws/sentinel                   → WebSocket para alertas en vivo
```

#### Frontend SENTINEL

**Tab "🔴 Sentinel" en navegación principal**
- Panel de alertas en tiempo real (WebSocket)
- Ticker de eventos electorales activos
- Semáforo global: cuántos países en WATCH / WARNING / CRITICAL
- Timeline de próximas elecciones (90 días)

**Indicador SENTINEL en cada CountryCard:**
- Punto rojo parpadeando si hay alerta activa
- Badge con nivel: WATCH / WARNING / CRITICAL
- Tooltip: motivo de la alerta + fuente

**Dashboard de país — nueva fila:**
- "Señales SENTINEL activas" con fuentes y timestamps
- Score SENTINEL vs Score histórico PEIRS (comparación)

#### Métricas de éxito v0.5.0
- Alertas generadas automáticamente en < 1 hora de un evento real
- WebSocket sin reconexiones manuales en 24h
- 0 falsos positivos críticos en primera semana

---

### FASE v0.6.0 — MOE: MISIONES DE OBSERVACIÓN ELECTORAL
*Objetivo: Que la plataforma sea una herramienta real para observadores internacionales.*

#### ¿Qué es un MOE Brief?
Un documento estructurado que los observadores electorales usan antes de desplegar una misión.
Incluye: contexto político, marco legal aplicable, áreas de riesgo prioritarias, metodología
recomendada, contactos institucionales, y cronograma de la misión.

Democrac.IA lo genera automáticamente en minutos, combinando:
- Análisis PEIRS del país (histórico + actual)
- Señales SENTINEL activas
- Marco legal internacional aplicable (ICCPR, CADH, CDI, etc.)
- Metodología de la misión (OSCE/ODIHR, MOE-UE, OEA-DECO)

#### Agente MOE — Backend
**`agents/moe_agent.py`** — nuevo agente LangGraph

Genera un Brief MOE con las siguientes secciones:
1. **Ficha País** — datos básicos, tipo de elección, fecha, EMB
2. **Contexto Político** — análisis histórico PEIRS
3. **Marco Legal** — tratados aplicables + artículos específicos
4. **Áreas de Riesgo Prioritarias** — top 5 con evidencia verificada
5. **Metodología Recomendada** — LTO/STO, PVT, SMM
6. **Protocolo de Día de Votación** — checklist + formulario de incidentes
7. **Cronograma** — hitos antes/durante/post elección
8. **Contactos Institucionales** — EMB, sociedad civil, medios

**Endpoints:**
```
POST /api/moe/brief/{run_id}        → Genera Brief MOE (async)
GET  /api/moe/brief/{run_id}        → Obtiene Brief generado
GET  /api/moe/brief/{run_id}/pdf    → Descarga en PDF
POST /api/moe/voting-day/{run_id}   → Registra incidentes en tiempo real
GET  /api/moe/voting-day/{run_id}   → Estado del día de votación
```

#### Frontend MOE

**Botón "Generar Brief MOE" en DetailView**
- Activo solo si riskLevel >= HIGH o SENTINEL activo
- Genera en background con spinner
- Descarga como PDF o abre en modal

**Formulario de Día de Votación (Cap. 7)**
- Input de incidentes en tiempo real
- Clasificación: intimidación / irregularidad técnica / violencia / acceso denegado
- Geolocalización de incidente
- Nivel de severidad
- Nombre del observador y credencial

#### Métricas de éxito v0.6.0
- Brief MOE generado en < 60 segundos
- PDF descargable con formato profesional (logo, colores institucionales)
- Formulario de incidentes funcional y persistente

---

### FASE v0.7.0 — AGENTE DE MEJORA CONTINUA
*Objetivo: La plataforma se mejora sola. El arquitecto experto nunca duerme.*

#### ¿Qué es el Agente de Mejora Continua?
Un agente LangGraph que corre semanalmente (cron job) y:
1. **Diagnostica** el sistema: errores en logs, endpoints lentos, datos desactualizados
2. **Benchmarks** la calidad de sus propios informes vs. versión anterior
3. **Detecta** gaps de datos (países sin datos recientes, datasets vencidos)
4. **Propone** mejoras priorizadas con justificación técnica y estimación de impacto
5. **Genera** un reporte `IMPROVEMENT_REPORT_YYYY-MM-DD.md`
6. **Crea** GitHub Issues automáticamente si prioridad = CRITICAL o HIGH

#### `agents/improvement_agent.py`

**Módulo 1 — System Health Check:**
- Tiempo de respuesta de cada endpoint (/api/dashboard, /api/report, /api/sentinel)
- Tasa de errores en últimas 24h (logs de FastAPI)
- Uso de memoria y CPU
- Integridad de datos: ¿todos los países tienen datos del año actual?

**Módulo 2 — Data Quality Monitor:**
- Verifica que V-Dem, FH, PEI, RSF tengan datos del año en curso
- Detecta países donde el análisis usa más del 30% de datos mock
- Alerta si un dataset tiene > 6 meses sin actualización
- Sugiere fuentes alternativas para gaps detectados

**Módulo 3 — Report Quality Benchmark:**
- Compara Risk Score actual vs. mes anterior por país
- Detecta inconsistencias: score subió pero violaciones bajaron
- Evalúa longitud y densidad de información por capítulo
- Puntaje de calidad 0-100 por informe

**Módulo 4 — Architecture Proposer:**
- Analiza el backlog de issues
- Prioriza por impacto × esfuerzo
- Propone el siguiente paso técnico concreto
- Genera código de ejemplo para la mejora propuesta

**Formato del reporte generado:**
```markdown
# DEMOCRAC.IA — Improvement Report
## 2026-03-29 | Score del sistema: 78/100

### 🔴 Crítico (acción inmediata)
- [ISSUE] RSF dataset: sin actualización hace 8 meses
  Impacto: 37 países con datos de prensa desactualizados
  Fix propuesto: Actualizar scraper RSF + endpoint de actualización manual

### 🟠 Alto (próxima semana)
- [MEJORA] Cap. 4 (Inclusividad): 100% mock para 34 de 38 países
  Impacto: Análisis CEDAW/ICERD sin respaldo empírico
  Fix propuesto: Integrar UN Women Data Hub + UNDP Gender Equality Index

### 🟡 Medio (próximo sprint)
- [OPTIMIZACIÓN] /api/dashboard tarda 47s para 38 países
  Causa: análisis secuencial, no paralelo
  Fix propuesto: asyncio.gather() para pipeline paralelo

### Próximo paso recomendado:
Implementar asyncio.gather() en /api/dashboard para reducir tiempo de 47s a ~12s.
Estimación: 2 horas de trabajo. Ver código propuesto en /docs/improvements/parallel_dashboard.py
```

#### Endpoint y scheduler:
```
GET  /api/improvement/latest        → Último reporte de mejora
POST /api/improvement/run           → Forzar ejecución manual
GET  /api/improvement/history       → Historial de reportes
```

Cron job: cada lunes a las 06:00 UTC via APScheduler (ya disponible en FastAPI).

#### Métricas de éxito v0.7.0
- Reporte semanal generado sin intervención humana
- Al menos 3 mejoras implementadas a partir de sus sugerencias
- Score del sistema mejora de semana a semana

---

### FASE v1.0 — PLATAFORMA ELITE INTEGRADA
*Objetivo: Todo corriendo junto. Lista para usuarios externos.*

#### Integraciones adicionales v1.0

**PDF Export de calidad profesional**
- Librería: WeasyPrint (Python) o Puppeteer (Node)
- Template con: logo Democrac.IA, colores institucionales, numeración de páginas
- Incluye: carátula, índice, todos los capítulos, gráficos embebidos, bibliografía
- Firmado digitalmente con timestamp y hash de integridad

**API REST pública**
- Autenticación via API key
- Rate limiting por tier (free / professional / enterprise)
- Documentación OpenAPI auto-generada (FastAPI lo hace nativo)
- Endpoints de solo lectura para el dashboard público

**Multi-idioma**
- Español (principal)
- Inglés (para audiencia internacional)
- Francés (para África francófona)
- Sistema i18n en el frontend (react-i18next)

**Notificaciones**
- Email: alerta cuando risk level sube en un país monitoreado
- Slack webhook: alerta SENTINEL CRITICAL
- RSS feed: nuevos informes publicados

**Sistema de usuarios (básico)**
- Login simple (no OAuth, solo email + token)
- Rol "observador": puede generar MOE briefs
- Rol "analista": puede configurar alertas
- Rol "admin": acceso completo

#### Infraestructura v1.0
- Docker + docker-compose (backend + frontend + PostgreSQL)
- Nginx como reverse proxy
- GitHub Actions: tests automáticos en cada PR
- Deploy en VPS (Hetzner o DigitalOcean) — ~€10/mes
- Dominio: democracia.ai o peirs.democracia.ai

#### Dashboard Elite — Componentes finales

| Componente | Descripción |
|---|---|
| Mapa mundial interactivo | Heat map de riesgo por país, clic para detalle |
| Ticker en tiempo real | SENTINEL: eventos electorales activos |
| Panel de comparativas | Evolución histórica V-Dem por región 2013–2025 |
| Ranking dinámico | Top 10 países en deterioro democrático |
| Estadísticas globales | Distribución de risk, promedio regional, tendencias |
| Generador MOE | Brief de misión en 60 segundos |
| Biblioteca de informes | Historial por país con versionado |
| Centro de metodología | Documentación completa de cada indicador |

---

## FLUJO DE TRABAJO FIJO (OPERATIVO v1.0)

```
LUNES 06:00 UTC
└── Agente Mejora Continua → diagnóstico semanal
└── SENTINEL → actualiza calendario electoral

LUNES-VIERNES (continuo)
└── SENTINEL feeds → monitoreo cada 2 horas
└── Si alerta CRITICAL → regenerar informe país afectado automáticamente

MARTES 08:00 UTC
└── Batch PEIRS → actualizar análisis de países con elecciones en < 30 días

JUEVES
└── Agente Mejora Continua → genera IMPROVEMENT_REPORT.md
└── Crea GitHub Issues si hay críticos

VIERNES
└── Revisión manual del IMPROVEMENT_REPORT
└── Aprobación de cambios propuestos para la semana siguiente
```

---

## STACK TECNOLÓGICO ELITE

| Capa | Tecnología | Motivo |
|---|---|---|
| Backend | Python + FastAPI | Ya instalado, nativo async |
| IA / Agentes | LangGraph + Claude Sonnet | Ya integrado |
| Base de datos | PostgreSQL + SQLAlchemy | Escalable, queries complejas |
| Cache | Redis | Cache de análisis por país (24h TTL) |
| Frontend | Vite + React + Recharts | Ya instalado |
| WebSocket | FastAPI WebSockets | Alertas SENTINEL en vivo |
| PDF | WeasyPrint | Python nativo, sin deps externas |
| Scheduler | APScheduler | Cron jobs integrados en FastAPI |
| Deploy | Docker + Nginx | Reproducible, fácil de mantener |
| CI/CD | GitHub Actions | Tests automáticos en cada commit |

---

## PRINCIPIOS DE CALIDAD ELITE

1. **Trazabilidad completa** — Cada dato tiene fuente, fecha y nivel de confianza visible
2. **No legitimación** — PEIRS emite riesgo predictivo, nunca valida resultados
3. **Evidence-based** — Cero afirmaciones sin respaldo empírico verificable
4. **Transparencia metodológica** — Toda métrica tiene su metodología pública
5. **Mejora continua** — El sistema es más inteligente cada semana
6. **Código auditado** — GitHub público, cambios trazables, sin magia oculta

---

## MÉTRICAS DE ÉXITO — PLATAFORMA ELITE

| Métrica | Actual (v0.3.2) | Objetivo (v1.0) |
|---|---|---|
| Países monitoreados | 4 | 38+ |
| Tiempo de generación de informe | ~30s | < 10s (cache) |
| Capítulos con datos reales | 6/9 | 9/9 |
| Fuentes de datos integradas | 4 | 8+ |
| Informes generados en 24h | 4 | 38+ |
| Alertas en tiempo real | No | Sí (< 2h de latencia) |
| MOE Briefs generables | No | Sí (< 60s) |
| Export PDF | Solo HTML | PDF profesional |
| Usuarios simultáneos soportados | 1 | 50+ |
| Uptime | Local (0% si no hay PC encendida) | 99.5% (VPS) |

---

## PRÓXIMA SESIÓN — v0.4.0

**Tarea 1:** Migración a PostgreSQL
```
backend/database.py      → Modelos SQLAlchemy
backend/migrations/      → Alembic para versioning del schema
.env                     → DATABASE_URL=postgresql://...
```

**Tarea 2:** 38 países en COUNTRY_CATALOG
```
backend/countries.py     → Catálogo separado del app.py principal
```

**Tarea 3:** Batch processing con cache
```
backend/app.py           → /api/dashboard con asyncio.gather()
backend/cache.py         → Cache por país con TTL 24h
```

**Tarea 4:** Tab Global en el frontend
```
frontend/src/GlobalView.jsx  → Mapa + ranking + estadísticas
```

---
*Documento generado por Democrac.IA — Claude Sonnet 4.6 — 2026-03-22*
*Clasificación: Uso interno — Fundadora y equipo técnico*
