# DEMOCRAC.IA / PEIRS — Metodología Constructiva del Informe Elite

> **Versión: 1.0 — Fecha: 2026-05-04**
> **Propósito:** documentar el método reproducible para construir un Informe Elite de observación electoral. Aplicable a Perú 2026 (caso piloto) y replicable a cualquier país y ciclo electoral.
>
> Este documento es el **playbook canónico** del producto. Cuando se escale a Argentina 2027, Brasil 2026, Colombia 2026, etc., debe seguirse este método con ajustes mínimos parametrizados.

---

## 1. Propósito del informe Elite

El **Informe Elite** es el producto final del sistema PEIRS — un documento de observación electoral comparable en estructura y rigor a los informes de las misiones de observación internacional, pero generado en minutos en lugar de semanas.

Cada Informe Elite cumple cinco condiciones no negociables:

1. **Trazabilidad verificable** — cada hallazgo cita fuente primaria con URL pública.
2. **Sin sesgo político-partidario** — el informe no toma posición sobre quién debe ganar; solo documenta integridad del proceso.
3. **No-legitimación** — el informe no valida ni invalida resultados; emite inteligencia electoral.
4. **Estándares internacionales** — se ancla en obligaciones del derecho internacional aplicable a procesos electorales.
5. **Reproducibilidad** — cualquier observador con la documentación puede regenerar el informe y verificar las citas.

El disclosure obligatorio aparece en tres lugares de cada informe (cover, declaración preliminar, footer):

> **DEMOCRAC.IA no legitima ni valida resultados electorales.** Este informe emite inteligencia electoral con trazabilidad verificable bajo estándares internacionales de observación electoral, sin sesgo político-partidario.

---

## 2. Estructura del informe (12 capítulos + 3 anexos)

| # | Capítulo | Foco |
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
| 9 | Análisis predictivo | Escenarios probabilísticos + early warning meter |
| 10 | Conclusiones | Semáforo institucional + radar 8 dimensiones |
| 11 | Recomendaciones | Matriz priorizada (destinatario × prioridad × horizonte) |
| 12 | IA en el proceso electoral | Arquitectura técnica + brecha regulatoria |
| A | Metodología técnica | Cómo se construyó este informe |
| B | Bibliografía APA 7 | Fuentes citadas |
| C | Hallazgos completos | Listado universal del Hunter del período |

---

## 3. Pipeline de 6 etapas

```
┌─────────────────────────────────────────────────────────────────────┐
│  EliteLoader → PhaseOrganizer → CrossReferenceBuilder →             │
│  PredictiveEngine → ChapterComposer → Visualizer →                  │
│  Renderer (HTML+MD+PDF) → Persist (SQLite + filesystem)             │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.1. EliteLoader

Carga paralela de:

- `hunter_entries`: findings clasificados del Hunter en el período (severidad, categoría, fase, fuente, URL)
- `rag_documents`: corpus normativo aplicable filtrado por país (RAG ChromaDB con sentence-transformers)
- `historical_series`: V-Dem v16 (1789-2025), Freedom House FIW, PEI 10.0, RSF Press Freedom
- `alerts_dispatched`: alertas Discord enviadas durante el período
- `vdem_emb_quant`: indicadores cuantitativos V-Dem específicos del EMB (autonomía, capacidad, irregularidades, intimidación, estado de derecho, revisión judicial)

**Cache TTL: 1 hora.** Reduce costo de regeneraciones consecutivas.

### 3.2. PhaseOrganizer

Agrupa los hallazgos en las **9 fases del ciclo electoral**:

```
preparatorio → pre-campaña → campaña → silencio electoral →
jornada electoral → escrutinio y cómputo → post-electoral →
resolución de disputas → ciclo completo
```

Cada fase recibe sus findings específicos. Esto permite que el Cap. 4 cite solo evidencia pre-electoral, el Cap. 5 solo de jornada, etc.

### 3.3. CrossReferenceBuilder

Mapea cada hallazgo a artículos normativos específicos según su categoría. Ejemplos:

- `ballot_tampering` → ICCPR Art. 25 (sufragio auténtico) + CADH Art. 23
- `voter_suppression` → ICCPR Art. 25(b) + CDI Art. 3
- `disinformation` → ICCPR Art. 19(2) + CADH Art. 13
- `gender_violence` → CEDAW Art. 7-8 + Ley 31170 (PER)

Produce `cross_references[]`: tuplas `(finding_id, article, severity, reasoning)`.

### 3.4. PredictiveEngine

Motor híbrido **reglas deterministas + LLM**:

1. Evalúa 6 escenarios canónicos (disputa prolongada, nulidad parcial, segunda vuelta, crisis institucional, reforma IA electoral, proclamación sin disputa) con triggers determinísticos.
2. Si el LLM está disponible, refina las probabilidades base con razonamiento sobre las señales agregadas y hallazgos top.
3. Devuelve `ForecastPayload` con escenarios + intervalos de confianza + `early_warning_level` (green/amber/orange/red) + `dominant_pattern`.

Costo: ~$0.05 por informe (1 llamada LLM con prompt caching).

### 3.5. ChapterComposer

Genera los **12 capítulos en paralelo** con concurrency limit 4. Cada capítulo:

1. Lee su prompt específico desde `composer/prompts/cap_NN_*.md`.
2. Lo combina con el `shared_context` (mismo para los 12 — aprovecha prompt caching de Anthropic).
3. Llama `claude-sonnet-4-20250514` con SystemMessage (shared) + HumanMessage (cap-specific).
4. Procesa la respuesta: limpia heading nivel 1, extrae word count, captura tokens usados.
5. Retorna `EliteChapter` con `narrative` + `findings_cited[]` + `cross_references[]`.

Si el LLM falla en un capítulo, retorna chapter vacío con warning. El **pre-check `/api/health?deep=true`** detecta caída del LLM antes de gastar tokens (ver `b24019f`).

### 3.6. Visualizer

Genera **21 visualizaciones SVG server-side** (pure-Python, sin matplotlib). Cada chapter recibe los kinds que le corresponden:

| Cap | Kinds wired |
|---|---|
| 1 | `timeseries_multi`, `events_timeline` |
| 2 | `matrix_normativa` |
| 3 | `flow_chart_voting`, `network_institutions` |
| 4 | `phase_timeline` |
| 5 | `hourly_timeline`, `map_regions_affected` |
| 6 | `progress_chart`, `integrity_incidents_grid` |
| 7 | `actor_network`, `judicial_timeline` |
| 8 | `heatmap_rights`, `compliance_matrix` |
| 9 | `forecast_chart`, `scenario_probability`, `early_warning_meter` |
| 10 | `semaphore_institutional`, `dimensions_radar` |
| 11 | `matrix_recommendations` |
| 12 | `system_architecture` |

Renderers en `backend/agents/elite_report/visualizer/`. Cada renderer recibe `data: dict` con shape específica documentada en docstring.

### 3.7. Renderer

Tres outputs:

- **HTML**: con `@page A4` + `@media print` para imprimirlo profesionalmente desde el navegador. Incluye CSS institucional (Fraunces + DM Sans + DM Mono).
- **MD**: para archivado y conversión a otros formatos. Generado vía `markitdown` desde el HTML.
- **PDF**: vía `/api/report/elite/{id}/printable` que sirve el HTML con `window.print()` automático. El motor del navegador genera PDF de calidad editorial.

### 3.8. Persist

Doble persistencia (`cb2ae9b`):

1. **SQLite (resiliente)**: tabla `elite_reports` con columnas `md_content` + `html_content` + `output_json` (estructura completa). Sobrevive crashes del volumen Railway.
2. **Filesystem (rápido)**: `reports/elite/{report_id}/report.{md,html,pdf}` para servir descargas directo.

Endpoint `/download` tiene **fallback 3-tier**: filesystem → SQLite TEXT → PDF on-demand desde HTML.

---

## 4. Datos de entrada

### 4.1. Datasets cuantitativos

| Dataset | Versión | Cobertura | Tamaño | Path |
|---|---|---|---|---|
| V-Dem | v16 | 1789-2025, 28.092 obs país-año, 4.618 columnas | 445 MB (CSV) | `data/vdem/vdem_v16.csv` (gitignored) |
| V-Dem static (pre-procesado) | v16 | 38 países × 21 indicadores × 1985-2025 | 618 KB | `backend/modules/vdem_static.py` (tracked) |
| Freedom House FIW | 2013-2025 | 2.723 filas, ~200 países | 0.5 MB | `data/All_data_FIW_2013-2025 - Index.csv` |
| PEI | 10.0 | 586 elecciones, 2012-2023 | ~2 MB | `data/PEI/PEI_10 Election External.csv` |
| RSF Press Freedom | 2025 | 180 países (con Score N-1 → 2 puntos) | 30 KB | `data/RSF/2025 - 2025.csv` |

**Estrategia 2-tier para V-Dem**: el CSV completo no entra en git. El static pre-procesado sí. En Railway, el loader cae automáticamente al static.

### 4.2. Corpus normativo (RAG)

ChromaDB con embeddings `sentence-transformers/all-MiniLM-L6-v2`. Documentos:

- 14 instrumentos universales/regionales: ICCPR, CADH, CDI, CEDAW, OSCE/ODIHR, UNDRIP, etc.
- Para PER: Constitución 1993, LOE 26859, LOP 28094, jurisprudencia JNE clave (incl. Res. 0891-2025-JNE sobre voto electrónico).

Ubicación: `backend/rag/corpus.py`. Para escalar a otro país: agregar instrumentos nacionales con tags `{ISO}_*`.

### 4.3. Hunter (OSINT en vivo)

Scheduler async que corre cada 24h (configurable via `HUNTER_INTERVAL_MINUTES`). Ingesta:

- 8 fuentes RSS para PER mapeadas a fases: Andina, RPP, El Comercio, Gestión, IDL-Reporteros, Wayka, JNE, ONPE
- OONI API para censura de internet
- Clasifica con `claude-sonnet-4-20250514` en **18 categorías** + 5 niveles de severidad
- Dedupe por (categoría, URL, fecha)
- Persiste en SQLite con auto-recovery sobre volumen Railway

---

## 5. Cómo escalar a otro país

**Tiempo total estimado: 6-8 horas de trabajo de research + curado** + 30-60 min de código pegamento.

### 5.1. Estructura de archivos a crear

```
backend/
├── modules/
│   └── {iso}_data.py            ← paralelo a peru_data.py
├── integrations/
│   └── {iso}_sources.py         ← paralelo a peru_sources.py (RSS feeds)
└── rag/corpus.py                ← agregar instrumentos nacionales del país
```

### 5.2. `{iso}_data.py` — qué llenar

```python
{ISO}_POLITICAL_FORCES = [
    {"abbr": "...", "name": "...", "ideology": "...",
     "current_seats": N, "electoral_strength": "...",
     "risk_profile": "high|moderate|low",
     "iccpr_risk": "...", "iccpr_source": "...", "iccpr_date": "...",
     "iccpr_url": "..."},
    # ...
]

{ISO}_ELECTORAL_SYSTEM = {
    "name": "Representación proporcional con umbral X%",
    "seats": N, "chamber": "unicameral|bicameral",
    "threshold": "X%", "women_quota": "X% paridad",
    "youth_quota": "X% jóvenes",
}

{ISO}_PARL_DATA = {...}            # composición + escenarios A/B/C
{ISO}_REGIONS_DATA = [...]          # regiones con peso electoral + tendencia
{ISO}_HISTORICAL_EVENTS = [...]    # 5-10 eventos clave de la última década
{ISO}_DIGITAL_THREATS = {...}       # IA, deepfakes, desinfo, bots, etc.
{ISO}_GENDER_DATA = {...}          # paridad, VDGP, leyes
```

### 5.3. `{iso}_sources.py` — RSS feeds priorizados por fase

Mapear 6-10 medios al país, con priorización por las **9 fases electorales**. Ejemplo PER:

```python
RSS_FEEDS = {"andina": [...], "rpp": [...], "elcomercio": [...], ...}
PHASE_SOURCES = {
    "preparatory": ["andina", "elcomercio", ...],
    "campaign": ["andina", "elcomercio", "rpp", ...],
    "election_day": ["andina", "rpp", "onpe", ...],   # + OONI siempre
    # ...
}
```

### 5.4. Corpus normativo — instrumentos nacionales

En `rag/corpus.py`, agregar:

- Constitución del país (artículos sobre régimen electoral)
- Ley orgánica electoral
- Ley de partidos políticos
- Jurisprudencia clave del organismo electoral
- Instrumentos regionales aplicables si difieren (ej. para África: Carta Africana DDHH)

Tags: `{ISO}_constitutional`, `{ISO}_electoral_law`, `{ISO}_party_law`, `{ISO}_jurisprudence`.

### 5.5. Sesión Hunter activa

Endpoint:

```bash
curl -X POST https://api.../api/observation/{ISO}/start \
  -H "X-Observer-Key: ..." \
  -d '{"country_code": "{ISO}", "run_id": "<run del PEIRS clasico>",
       "mission_name": "DEMOCRACIA Misión {País} 2027", ...}'
```

Setear `AUTO_OBSERVE_COUNTRIES={ISO},PER` en env vars de Railway para que arranque al deploy.

### 5.6. Validación

1. Generar primer Elite Report `audience=executive&report_type=preliminary`.
2. Revisar manualmente: ¿el modelo cita los instrumentos del país? ¿Los hallazgos vienen con URL?
3. Iterar 1-2 generaciones ajustando prompts si los capítulos quedan desbalanceados.

---

## 6. Cómo escalar a otro ciclo electoral del mismo país

Más simple que cambiar país — el método ya está; solo refrescar **datos**:

### 6.1. Actualizar fechas

En `modules/{iso}_data.py`: actualizar fechas de eventos históricos, jornada electoral, lista de candidatos confirmados.

### 6.2. Corpus normativo — nuevas resoluciones

Agregar al RAG las resoluciones del organismo electoral relevantes al nuevo ciclo (ej. nueva Res. JNE para 2031).

### 6.3. Actualizar `{iso}_political_forces`

Composición parlamentaria post-elección + escenarios para el ciclo siguiente.

### 6.4. Nueva sesión Hunter

Cuando proclame el resultado del ciclo actual, **archivar** la sesión PER actual (con `POST /api/observation/PER/finalize`) y crear nueva con `allow_override: true`.

### 6.5. Mantener V-Dem actualizado

V-Dem publica nueva versión cada año en marzo. Bajarla con:

```bash
python skills/electoral-data-integration/scripts/download_datasets.py --only vdem
python scripts/generate_vdem_static.py
```

Verificar `VDEM_LAST_YEAR` en `modules/config.py`.

---

## 7. Costos y tiempos

| Etapa | Tiempo | Costo (USD) |
|---|---|---|
| Hunter ciclo (cada 24h) | ~30-60s | ~$0.10-0.20 (con fuentes intl) |
| EliteLoader | < 1s | $0 (cache) |
| PredictiveEngine | ~10s | ~$0.05 |
| ChapterComposer (12 caps) | ~2-3 min | ~$0.40-0.70 |
| Visualizer | < 5s | $0 |
| Renderer + Persist | < 5s | $0 |
| **Informe completo** | **2-4 min** | **~$0.40-0.80** |

Cap diario por país configurable: `MAX_ELITE_PER_DAY=5` (default). Auth: `X-Observer-Key` requerida en `/api/report/elite/generate`.

---

## 8. Análisis del Architect Agent — método actual y futuro

> **Nota:** este análisis está escrito por mí (Claude Opus 4.7) operando como "Architect Agent" durante la sesión 4-may-2026. No fue invocado el agente real (`backend/agents/architect.py`) por consideración de costo. Tiene el mismo contexto operativo pero podría diferir si se invocara con acceso fresh al codebase.

### 8.1. Lo que está sólido del método

- **Trazabilidad disciplinada**: la regla "cada dato con fuente, timestamp, confidence" es el activo más valioso del sistema. La auditoría de abril que postergó secciones sin URL primaria (commit `ac0c8e2`) sentó precedente operativo.
- **Persistencia resiliente**: la migración a SQLite con triple-tier fallback (`cb2ae9b`) eliminó el problema de informes huérfanos por crashes de volumen Railway.
- **Pipeline LLM-async no-bloqueante**: con `init_rag` en background (`7d5b5b9`) y pre-check del LLM (`b24019f`), el sistema arranca rápido y falla rápido cuando debe.
- **Datasets v16 con fallback static**: 38 países × 21 indicadores × 1985-2025 caben en 618 KB tracked en git, garantizando que prod tenga data aunque el CSV gigante no esté (`b21edf2`).
- **Composer con prompt caching**: el `shared_context` se construye una vez para los 12 capítulos. Reduce el costo a ~$0.40-0.80 por informe completo.

### 8.2. Riesgos y debilidades pendientes

**Severidad alta:**

1. **Single-point-of-failure: ANTHROPIC_API_KEY.** Si Anthropic baja, hibernar el sistema completo. El pre-check evita gastar tokens en vacío pero no provee continuidad. Mitigación a futuro: fallback a otro provider (OpenAI / Google) detrás de una abstracción uniforme.

2. **Hardcoded peruano en módulos**: `peru_data.py` tiene 700+ líneas de datos PER específicos. La intención de "arquitectura genérica, contenido específico" se cumple parcialmente — el código del Elite Report es genérico, pero el llamador pasa `country_code="PER"` y muchos viz tienen ramas `if country_code == "PER":`. Cuando se sume el segundo país hay refactor inevitable.

3. **Validación humana del informe ausente del flujo**: el sistema genera informe de 12 capítulos en 3 minutos. Antes de publicar a una audiencia institucional, falta una etapa de "review humana del LLM-output" obligatoria. Hoy se hace ad-hoc por Mariana.

**Severidad media:**

4. **Test coverage del pipeline Elite es bajo.** Hay tests para datasets loaders y db, pero no para el flow Composer → Visualizer → Renderer. Los bugs visibles del 4-may (AttributeError en PredictiveEngine, validation_error en VizSpec, atributos inexistentes en FindingRef) los hubiéramos atrapado con tests integrados.

5. **No hay versioning del prompt template.** Si cambiamos `cap_03.md` y degrada la calidad, no hay forma fácil de rollback selectivo de prompt sin git revert. Considerar persistir versión de prompts en `EliteReportOutput` para que cada informe sea reproducible bit-a-bit.

6. **Hunter tiene un único webhook (Discord)**. Si el webhook falla silenciosamente, las alertas críticas no llegan a nadie. Mitigación: sumar email/Slack como redundancia para severidad ≥ critical.

**Severidad baja:**

7. **Dos proyectos Railway en el repo** (`api.democracia.ar` secundario sin secrets). Confunde debugging. Borrarlo está autorizado por Mariana (4-may).

### 8.3. Recomendaciones priorizadas — próximos 3 sprints

| Sprint | Esfuerzo | Impacto | Item |
|---|---|---|---|
| **Sprint A** (2-3h) | Bajo | Alto | **Tests integrados del pipeline Elite**: smoke test que genera un informe E2E con bundle mockeado y verifica que (a) los 12 capítulos compilan, (b) los 21 viz se rinden, (c) el JSON estructurado tiene la shape esperada. Atrapa los 3 bugs del 4-may antes de que lleguen a prod. |
| **Sprint B** (4-6h) | Medio | Alto | **Refactor multi-país**: extraer `country_specific = CountryAdapter(cc)` que provee `political_forces`, `parl_data`, `regions`, etc. Eliminar `if country_code == "PER":` distribuidos. Habilita que sumar AR/BR sea ~2h en vez de ~8h. |
| **Sprint C** (6-8h) | Alto | Alto | **Versioning de prompts + replay**: persistir hash de prompts en cada `EliteReportOutput`. Endpoint `/api/report/elite/{id}/replay` que regenera con el mismo prompt aunque el repo haya cambiado. Permite auditoría completa de cualquier informe publicado. |

### 8.4. Antes de escalar a un segundo país

**Checklist mínimo:**

- [ ] Sprint A (tests integrados) cerrado
- [ ] Sprint B (refactor multi-país) cerrado
- [ ] Decisión: ¿qué país? Recomendado: **Argentina 2027** por (a) afinidad metodológica con PER, (b) ciclo legislativo en agenda, (c) acceso a fuentes RSS.
- [ ] Compilación de instrumentos jurídicos AR (Constitución, Cód. Electoral, Ley Orgánica de Partidos, jurisprudencia CNE).
- [ ] 6-10 fuentes RSS AR mapeadas a fases.
- [ ] Validación: generar primer informe AR → review manual → iterar prompts si hace falta.

---

## 9. Referencias internas

- `DOCS Proyect/PEIRS_Arquitectura_Roadmap.md` — arquitectura general v0.5.0
- `ELITE_REPORT.md` — blueprint original (sprints 1-6)
- `PROMPT_MAESTRO.md` — instrumento de evaluación de informes
- `scripts/generate_vdem_static.py` — regenerador del static V-Dem
- `scripts/backup.py` — backup completo del estado de prod
- `backend/agents/elite_report/composer/prompts/*.md` — los 13 prompts editables (12 caps + base_context)
- `backend/agents/elite_report/visualizer/renderers*.py` — 21 SVG renderers

---

*Documento creado por Claude Opus 4.7 en sesión con Mariana Lachman, 2026-05-04. Vivo: actualizar cada vez que el método cambie sustantivamente.*
