# PEIRS Agents Charter

> **Scope:** Democrac.IA / PEIRS únicamente. Voto Informado es un proyecto separado y NO se cubre acá (ver memoria `project_separation_democracia_voto`).
> **Versión:** 0.1 — 1-jun-2026
> **Objetivo:** Documentar qué hace y qué NO hace cada agente del sistema, para que la operación sea predecible cuando se sume Brasil (oct-2026) y USA (nov-2026).

---

## Cómo leer este documento

Cada agente lleva 7 campos:

| Campo | Significado |
|---|---|
| **Rol** | Una frase: qué problema resuelve. |
| **INPUT canónico** | Qué datos consume — schema o referencia. |
| **OUTPUT canónico** | Qué produce — schema o referencia. |
| **DEBE** | 3-5 acciones explícitamente esperadas. |
| **NO DEBE** | 3-5 acciones explícitamente prohibidas. |
| **Trigger** | Cómo se invoca (endpoint, scheduler, manual). |
| **Archivo principal** | Path absoluto al código fuente. |

Las **Reglas de oro transversales** (sin números mágicos, sin mock en prod, URL primaria por dato, audit_status PENDIENTE antes de inventar, no `/generate` sin OK) **aplican a todos los agentes**. No se repiten por agente.

---

## PARTE 1 — Agentes internos de PEIRS

Estos viven en `backend/`, los orquesta LangGraph (`backend/agents/pipeline.py`), y se invocan vía endpoints FastAPI. Son agentes "de producción" — no los toca el usuario directamente.

---

### A1 · OSINT Ingestion Agent

| Campo | Valor |
|---|---|
| **Rol** | Cargar evidencia paralela de datasets estructurales + OSINT en un `EvidenceBundle`. |
| **INPUT canónico** | `state["country_code"]`, `state["country"]`, fecha de elección. |
| **OUTPUT canónico** | `state["context_data"]` con V-Dem, FH, PEI, RSF, hunter_entries[], rag_documents[], historical_series. |
| **DEBE** | Cargar V-Dem + FH + PEI + RSF en paralelo. Marcar cada dato con `confidence_level` y `source_id`. Usar fallback static cuando el CSV no existe en disk. Logear avance con `agent_log()`. Persistir warnings de data quality en `state["warnings"]`. |
| **NO DEBE** | Inventar datos cuando el dataset falla (debe retornar mock con `confidence_level=mock`). Bloquear el event loop con descargas síncronas largas. Modificar las constantes V-Dem/FH/PEI/RSF en runtime. Hardcodear países nuevos (deben agregarse vía catalog). |
| **Trigger** | `POST /api/analyze` → primer nodo del workflow LangGraph. |
| **Archivo principal** | [backend/app.py:1446](backend/app.py#L1446) (wrapper en [backend/agents/nodes.py:57](backend/agents/nodes.py#L57)) |

---

### A2 · Political-Digital Analyst Agent

| Campo | Valor |
|---|---|
| **Rol** | Sintetizar el ecosistema político-digital del país (sesgo mediático, financiamiento, captura, salud digital). |
| **INPUT canónico** | `state["context_data"]` (output de A1). |
| **OUTPUT canónico** | `state["political_data"]` con `media_bias_assessment`, `finance_opacity_score`, `digital_ecosystem_health`, `capture_risk_by_actor`, `vdem_trajectory`, `international_pressure`. |
| **DEBE** | Mapear índices V-Dem a assessment cualitativo determinista. Calcular delta 5 años para detectar trayectoria de deterioro. Identificar riesgo de captura por actor político. Reportar `international_pressure` desde RSF + FH. |
| **NO DEBE** | Emitir juicios partidarios (`X es de izquierda mala`). Usar el LLM como reemplazo de cálculo determinista — los assessments salen de reglas sobre datos. Cambiar la trayectoria histórica (V-Dem es histórico, no actualizable acá). Inventar `capture_risk` para actores sin evidencia documentada. |
| **Trigger** | Segundo nodo del workflow LangGraph (tras A1). |
| **Archivo principal** | [backend/app.py:1727](backend/app.py#L1727) (wrapper en [backend/agents/nodes.py:72](backend/agents/nodes.py#L72)) |

---

### A3 · Legal Compliance Agent

| Campo | Valor |
|---|---|
| **Rol** | Mapear hallazgos OSINT a marco legal (universal + regional + doméstico) y calcular compliance matrix. |
| **INPUT canónico** | `state["context_data"]` (hunter_entries, region) + corpus RAG. |
| **OUTPUT canónico** | `state["legal_analysis"]` con `compliance_matrix` (ok/partial/breach/unknown por artículo), `breaches[]` con `legal_basis`, `applicable_instruments`. |
| **DEBE** | Resolver region automática (Americas/Europe/Africa/Asia/Arab) y aplicar instrumentos correspondientes. Citar artículo + número exacto (`ICCPR Art. 25(b)`). Marcar `unknown` cuando no hay evidencia, no `ok`. Usar el sub-agente Constitutionalist para queries jurídicas profundas. |
| **NO DEBE** | Inventar jurisprudencia. Mezclar instrumentos de regiones distintas sin justificación (ej: aplicar ACHPR a Perú). Categorizar como `breach` sin >=1 hallazgo `high` o >=5 `medium`. Tomar decisiones políticas (el rol es legal, no editorial). |
| **Trigger** | Tercer nodo del workflow LangGraph. |
| **Archivo principal** | [backend/app.py:2263](backend/app.py#L2263) (wrapper en [backend/agents/nodes.py:87](backend/agents/nodes.py#L87)) |

---

### A4 · Electoral Dictamen Agent

| Campo | Valor |
|---|---|
| **Rol** | Calcular `risk_score` (0-100) y `risk_level` (stable/vigilance/elevated/crisis) integrales. |
| **INPUT canónico** | A1 + A2 + A3 outputs (context_data, political_data, legal_analysis). |
| **OUTPUT canónico** | `state["risk_score"]`, `state["risk_level"]`, `state["dictamen"]` con justificación. |
| **DEBE** | Aplicar fórmula auditable del `crisis_index` (V-Dem 15% + FH 15% + EMB 15% + media 10% + finance 10% + digital 10% + violations 15% + obs 10%). Mapear `risk_level` desde rangos fijos del score. Documentar cada peso del cálculo. |
| **NO DEBE** | Cambiar los pesos sin commit explícito a `PEIRS_Indices_Methodology.md`. Emitir score basado en intuición LLM (es cálculo determinista). Suavizar resultados para hacer el reporte menos alarmante. |
| **Trigger** | Cuarto nodo del workflow LangGraph. |
| **Archivo principal** | [backend/app.py:2037](backend/app.py#L2037) (wrapper en [backend/agents/nodes.py:102](backend/agents/nodes.py#L102)) |

---

### A5 · Report Generator Agent

| Campo | Valor |
|---|---|
| **Rol** | Generar el Elite Report (12 capítulos + 3 anexos) en Markdown/HTML/PDF, en es/en/pt. |
| **INPUT canónico** | Estado completo (todos los outputs A1-A4). |
| **OUTPUT canónico** | `report_chapters[]`, `executive_summary`, `final_report_markdown`, citas APA 7, 21 visualizaciones SVG, persistencia SQLite triple. |
| **DEBE** | Componer los 12 capítulos con Claude Sonnet 4.6 + prompt caching. Pasar por `PredictiveEngine` para escenarios con bandas de confianza. Renderizar SVG server-side (no client-side). Generar disclosure neutral inmodificable en la portada. Persistir `output_json` para `/structured`. |
| **NO DEBE** | Llamar `/generate` sin OK explícito de la usuaria (regla `feedback_no_accidental_costs`). Publicar capítulos con datos `confidence_level=mock` sin warning. Cambiar el disclosure de la portada ("DEMOCRAC.IA no legitima ni valida resultados electorales"). Generar PT sin prompts PT disponibles (hoy `composer/prompts/pt/` está vacío). |
| **Trigger** | Quinto nodo del workflow LangGraph. |
| **Archivo principal** | [backend/app.py:2537](backend/app.py#L2537), [backend/agents/elite_report/](backend/agents/elite_report/) |

---

### Architect Agent (meta, background)

| Campo | Valor |
|---|---|
| **Rol** | Auditor de calidad + ejecutor autónomo de mejoras al código. Corre fuera del pipeline `/api/analyze`. |
| **INPUT canónico** | Task prompt: `audit`, `improve`, `test`, `integrate_db`. |
| **OUTPUT canónico** | Reporte estructurado de auditoría + diff de cambios + test results. |
| **DEBE** | Seguir ciclo EVALUAR → PRIORIZAR → IMPLEMENTAR → VERIFICAR → DOCUMENTAR → PROPONER. Validar con pytest antes de commit. Documentar cada cambio en commit message extenso. Respetar reglas de oro transversales. |
| **NO DEBE** | Tocar producción Railway directamente. Borrar tests pasando. Modificar V-Dem/FH/PEI/RSF data (es read-only). Commit sin que pytest pase. Generar Elite Reports (eso es A5, con autorización de costo). |
| **Trigger** | `POST /api/architect/run` o CLI `python -m backend.agents.architect --task <X>`. |
| **Archivo principal** | [backend/agents/architect.py](backend/agents/architect.py) (usa Claude Opus 4.7) |

---

### Hunter Scheduler (no es agente LLM)

| Campo | Valor |
|---|---|
| **Rol** | Background loop que dispara el `HunterAgent` cada 24h sobre sesiones activas, ingesta 14 RSS y clasifica. |
| **INPUT canónico** | `observation_store` (sesiones activas por país). |
| **OUTPUT canónico** | `hunter_entries` persistidos en SQLite + alertas Discord para severity ≥ high. |
| **DEBE** | Default 24h (`HUNTER_INTERVAL_MINUTES=1440`). Throttle a 1 alerta cada 6h cuando hay degradación. Persistir errores con context para debug. Saltarse sesiones marcadas `finalized: True`. |
| **NO DEBE** | Bloquear el event loop. Ejecutar más de 1 ciclo en paralelo por país. Mandar alerta crítica sin verificar `consecutive_errors >= 2`. Trabajar con LLM no configurado (debe fallar gracioso). |
| **Trigger** | `_hunter_scheduler_loop()` async background task lanzado en startup. Override manual: `POST /api/hunter/{cc}/run-now`. |
| **Archivo principal** | [backend/agents/hunter.py](backend/agents/hunter.py), scheduler en [backend/app.py:5314](backend/app.py#L5314) |

---

### Auditor Agent

| Campo | Valor |
|---|---|
| **Rol** | Detector de anomalías en sesiones de observación (flood, concentración, alegaciones sin evidencia, silencios). |
| **INPUT canónico** | `observation_store[country]["entries"]`. |
| **OUTPUT canónico** | `audit_score` (0-1) + findings con `level` (warning/alert/critical). |
| **DEBE** | Flagear 10+ entries en 15 min (flood). Flagear >70% entries de un solo observador (concentración). Flagear >60% allegations sin evidencia (calidad). Flagear 90+ min sin entrada durante periodo activo (silencio). |
| **NO DEBE** | Borrar entries. Modificar `level` de findings ya creados. Disparar alertas que crucen al canal público del Hunter (separación de responsabilidades). |
| **Trigger** | Tras cada `POST /api/observation/{cc}/entry`. |
| **Archivo principal** | [backend/agents/auditor.py](backend/agents/auditor.py) |

---

### Constitutionalist (sub-agente RAG)

| Campo | Valor |
|---|---|
| **Rol** | Responder consultas jurídicas profundas con RAG sobre el corpus legal electoral. Sub-agente invocado por A3. |
| **INPUT canónico** | `question` (string) + `context` opcional. |
| **OUTPUT canónico** | JSON estructurado: `answer`, `legal_basis[]`, `case_law[]`, `international_framework[]`, `confidence`, `caveats[]`. |
| **DEBE** | Citar artículos exactos (`Constitución Art. 178`, `Res. JNE 0891-2025-JNE`). Declarar vacío normativo cuando aplica (no inventar doctrina). Identificar info faltante cuando no puede dictaminar. Responder en español rioplatense-peruano formal. |
| **NO DEBE** | Emitir opinión política. Inventar resoluciones JNE o sentencias Corte IDH. Saltarse el sistema de tags PERU_TAGS para queries Perú. Mezclar instrumentos de otros países (hoy es Peru-only). |
| **Trigger** | `POST /api/ask/constitutionalist`, o invocado internamente desde A3. |
| **Archivo principal** | [backend/agents/constitutionalist.py](backend/agents/constitutionalist.py) |

---

## PARTE 2 — Agentes Claude Code (los que uso yo en tu sesión)

Estos NO viven en el backend de PEIRS. Viven en mi sesión con vos en Claude Code. Los invoco cuando necesito delegar trabajo de búsqueda, análisis o ejecución específica. Vos seguís siendo quien decide qué se commitea.

---

### Claude principal (yo, el conversacional)

| Campo | Valor |
|---|---|
| **Rol** | Interlocutor primario. Leo código, edito archivos, commit, ejecuto comandos, te muestro resultados. |
| **DEBE** | Confirmar antes de acciones destructivas o de costo (push, force-push, `/generate`, deploy). Commit por categoría con mensajes explicativos. Verificar build + lint antes de commitear refactors. Citar `file:line` cuando referencio código. |
| **NO DEBE** | Inventar datos con `audit_status: CONFIRMED`. Saltar revisión humana en outputs institucionales. Tocar memoria sin razón clara (ver reglas de auto-memory). Mezclar Democrac.IA con Voto Informado. |
| **Cuándo invocarme** | Default. Tareas que requieren juicio, edición de código, dialogue, decisiones de arquitectura. |
| **Cuándo NO** | Búsquedas amplias en código grande (delegá a Explore). Auditorías de PR (delegá a code-reviewer). |
| **Costo** | El más alto. Cada turno míe ocupa contexto principal. Mantené sesiones largas tracked vía memory. |

---

### Explore (búsqueda read-only rápida)

| Campo | Valor |
|---|---|
| **Rol** | Localizar código: archivos por patrón, símbolos por grep, "dónde está X". |
| **DEBE** | Recibir scope explícito ("quick" / "medium" / "very thorough"). Devolver paths + extractos relevantes. Cerrar rápido. |
| **NO DEBE** | Editar archivos (es read-only). Hacer code review (no es su rol). Análisis de cross-file consistency (Explore lee excerpts, no whole files). |
| **Cuándo invocarlo** | Más de 3 grep/glob seguidos, búsqueda con varias variantes de nombre, mapear estructura de un módulo desconocido. |
| **Cuándo NO** | Lookup puntual (uso Grep/Glob directo). Auditoría que necesite leer archivos enteros (uso general-purpose). |
| **Costo** | Bajo. Contexto separado del principal, no consume el mío. |

---

### Plan (arquitecto de implementación)

| Campo | Valor |
|---|---|
| **Rol** | Diseñar plan paso a paso para una task no trivial antes de codear. |
| **DEBE** | Identificar archivos críticos. Considerar tradeoffs (performance, mantenibilidad, alcance). Devolver pasos numerados con dependencias entre sí. |
| **NO DEBE** | Implementar (es read-only). Tomar la decisión final (eso queda en vos). |
| **Cuándo invocarlo** | Antes de un refactor que toque 5+ archivos o cambie arquitectura (ver instrucción CLAUDE.md sobre `/plan-eng-review` para PEIRS). |
| **Cuándo NO** | Cambios atómicos y bien acotados (hago yo directo). |
| **Costo** | Medio. Contexto separado. |

---

### code-reviewer

| Campo | Valor |
|---|---|
| **Rol** | Revisar PRs o diffs locales con perspectiva crítica independiente. |
| **DEBE** | Identificar bugs, regresiones, problemas de seguridad. Sugerir simplificaciones. Validar contra reglas de oro del proyecto. |
| **NO DEBE** | Reimplementar el PR (su rol es revisar, no escribir). Aprobar sin haber leído el diff completo. |
| **Cuándo invocarlo** | Antes de mergear refactors complejos, post-implementación de features que tocan generación de informes. |
| **Cuándo NO** | Cambios triviales (typo, rename). Trabajo en progreso temprano (no hay nada que revisar todavía). |
| **Costo** | Medio. |

---

### general-purpose

| Campo | Valor |
|---|---|
| **Rol** | Tareas multi-paso o búsquedas que requieren leer archivos enteros + ejecutar comandos. |
| **DEBE** | Recibir contexto explícito de qué busca y por qué. Devolver reporte estructurado. |
| **NO DEBE** | Hacer commits sin tu OK. Generar datos institucionales sin URL primaria. |
| **Cuándo invocarlo** | Auditorías completas (como la que hicimos del proyecto). Investigaciones cruzadas backend + frontend. |
| **Cuándo NO** | Búsqueda simple (uso Explore o Grep). |
| **Costo** | Alto. Contexto y herramientas equivalentes al mío. |

---

### claude-code-guide

| Campo | Valor |
|---|---|
| **Rol** | Responder preguntas sobre Claude Code, Agent SDK, Claude API (hooks, slash commands, MCP, settings). |
| **DEBE** | Buscar en docs oficiales antes de responder. Citar versión cuando aplica. |
| **NO DEBE** | Aconsejar sobre tu código de PEIRS (otro agente). |
| **Cuándo invocarlo** | "Cómo configuro X en Claude Code", "puede Claude hacer Y". |
| **Cuándo NO** | Cualquier cosa de PEIRS o tu código. |
| **Costo** | Bajo. |

---

### Decisiones que SIEMPRE quedan en vos (no en agente)

Esto NO es delegable:

- Autorizar costos: cualquier llamada a `/generate`, deploy a Railway, push a `main`
- Validar URL primaria de cualquier dato institucional antes de escalarlo a `CONFIRMED`
- Aprobar el contenido de cualquier outreach institucional (V-Dem, Freedom House, Google.org)
- Confirmar cambios al disclosure de portada o a la metodología de índices
- Decidir qué país se suma al catálogo y cuándo
- Decisiones editoriales / políticas / legales de fondo
