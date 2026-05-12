# DEMOCRAC.IA — DOCUMENTO DE ARQUITECTURA, DIAGNÓSTICO Y ROADMAP DE IMPLEMENTACIÓN

## Plataforma de Inteligencia Electoral con IA

*Version: 0.6.0 — Fecha: 2026-05-12 (cierre Sprint 4)*
*Clasificacion: Uso interno — Fundadora y equipo tecnico*

> **Nota de versionado:** v0.6.0 refleja el trabajo del 4 al 12 de mayo
> 2026. Sumario de cambios vs v0.5.2:
>
> - **Sprint Hunter-International (7-may):** 8 → 14 fuentes RSS (6 intl
>   filtradas por keyword "Peru"). Cadencia bajada a 24h (`HUNTER_INTERVAL_MINUTES=1440`).
> - **Automatizaciones diarias (8-may):** phase auto-advance cada 6h,
>   daily digest a Discord 10:00 ART, daily backup volumen 00:00 ART.
> - **Auditoría 9-may de visualizaciones:** G1 Radar 8 dims, G2 Semáforo
>   institucional, G3 Progress chart — todos derivaban de mock data
>   hardcoded. Fixeados con derivación real del corpus + L1 (citation
>   builder language-aware).
> - **PEIRS Crisis Index v1.0 (10-may):** el "0.88 Crisis" era magic number
>   cosmético. Reemplazado por fórmula auditable severity-weighted documentada
>   en `PEIRS_Indices_Methodology_v1.0.md` (citable para Ágora Data y
>   tribunales).
> - **Sprint 2 — CountryAdapter (10-may):** interfaz `CountryAdapter`
>   pluggable, `PeruAdapter` consolida ~200 líneas PER-específicas que antes
>   estaban inline. Foundation para Brasil/USA.
> - **Sprint 3 — InstitutionalModel (11-may):** dataclasses abstractas para
>   tipos unitary / federal_centralized / federal_descentralized.
> - **Sprint 4 — Prompts EN traducidos (12-may):** 14 archivos cap_NN.md a
>   `prompts/en/`. Loader trilingüe con fallback a ES. Reportes en inglés
>   ahora con narrativa nativa sin Spanish bleed-through.
>
> **Documentos hermanos (consultar):**
>
> - [INFORME_METODOLOGIA.md](INFORME_METODOLOGIA.md) — playbook reproducible
>   para construir el Elite Report en Perú 2026 y replicarlo a otros países.
> - **Sección "Evolución por sesiones"** dentro de este documento — script
>   cronológico del trabajo realizado de v0.3.x a v0.5.2.

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
|                        DEMOCRAC.IA v0.5.2                            |
+========================+=============================================+
|   PEIRS                |   HUNTER + OBSERVATION                      |
|   Knowledge Base       |   Real-Time Intelligence                    |
|                        |                                             |
|  - V-Dem v16 (1789-    |  - Hunter scheduler 24/7 (4h default)       |
|    2025) — upgrade     |  - 8 fuentes RSS Peru por fase electoral    |
|    al 4-may-2026       |  - Clasificacion automatica Sonnet 4.6      |
|  - Freedom House       |  - Dedupe semantico (cat+URL+date)          |
|    FIW 2013-2025       |  - OONI integration (censura web)           |
|  - PEI 10.0 (586       |  - Discord webhook (severidad >= high)      |
|    elecciones,         |  - Observer Protocol (9 fases)              |
|    2012-2023)          |  - Sesiones rehidratadas en boot            |
|  - RSF 2025 (180       |  - vdem_static.py: tier estatico para       |
|    paises)             |    Railway sin CSV (618KB tracked)          |
+========================+=============================================+
|         MOTOR DE ANALISIS -- LangGraph + Claude (multi-modelo)       |
|                                                                      |
|   PIPELINE 4 AGENTES (analisis original):                            |
|   Agente OSINT -> Agente Politico -> Agente Legal -> Agente Informe  |
|                                                                      |
|   ELITE REPORT (12 capitulos + 3 anexos):                            |
|   EliteLoader -> PhaseOrganizer -> CrossReferenceBuilder ->          |
|   PredictiveEngine -> ChapterComposer -> Visualizer -> Renderer ->   |
|   Persist (SQLite triple-tier)                                       |
|                                                                      |
|   AUXILIARES: Constitucionalista RAG (ChromaDB + sentence-           |
|   transformers), ReportDesigner sub-agente, Architect Agent          |
|   (Opus 4.7 + claude-agent-sdk para refactor iterativo)              |
+======================================================================+
|         I18N (es/en/pt) — INFORMES MULTILENGUE COMPLETOS             |
|                                                                      |
|   180+ claves i18n.py: cover, footer, TOC, captions, viz titles      |
|   y subtitulos, headers SVG, status labels, gauge bands, compliance  |
|   columns, scenarios labels, audit notes, alert badges, severity     |
|   legends, Appendix A body, subchapter titles 1.1-12.6 (50 entries)  |
+======================================================================+
|                      CAPA DE SALIDA                                  |
|                                                                      |
|   Dashboard React multi-tab    |  Elite Report 12 caps + i18n        |
|   Peru Situation Room          |  /printable (browser PDF nativo)    |
|   Frontend en democracia.ar    |  Markdown export                    |
|                                |  HTML responsive + print A4         |
|                                |  SQLite TEXT cache (triple tier)    |
+======================================================================+
|                  PERSISTENCIA Y RECUPERACION                         |
|                                                                      |
|   SQLite con md_content + html_content TEXT — sobrevive a perdida    |
|   de archivos. Reportes y findings persisten cross-restart.          |
|   Backup script (scripts/backup.py --targz) para snapshot completo.  |
+======================================================================+
```

---

## ESTADO ACTUAL (v0.5.2 -- 2026-05-04)

### Componentes Operativos en Produccion

| Componente | Estado | Notas |
| --- | --- | --- |
| **Pipeline LangGraph 4 agentes** | Operativo | OSINT > Politico > Legal > Informe |
| **Hunter scheduler 24/7** | Operativo | Intervalo configurable (default 4h), persistente en volumen Railway con auto-recovery. Re-arranca tras reinicio sin perder cola |
| **Constitucionalista RAG** | Operativo | ChromaDB + sentence-transformers all-MiniLM-L6-v2. Corpus de 23 instrumentos juridico-electorales. `init_rag` ahora corre en `asyncio.to_thread` para no bloquear startup |
| **Architect Agent autonomo** | Operativo | claude-agent-sdk con Claude Opus 4.7. Acceso al codebase para refactor iterativo bajo regla de trazabilidad estricta |
| **Elite Report 12 capitulos + 3 anexos** | Operativo | Claude Sonnet 4 con prompt caching, 4 audiencias (institutional/executive/press/international), motor predictivo con 6 escenarios + early-warning meter, 21 visualizaciones SVG server-side, citas APA 7. **i18n profundo es/en/pt** (180+ claves). Costo ~$0.40-0.80 por informe |
| **i18n profundo Elite Report** | Operativo (4-may) | 180+ claves cubriendo: cover, footer, TOC, captions, viz titles/subtitles, headers SVG, status labels, gauge bands, compliance columns, scenarios labels, audit notes, alert badges, severity legends, Appendix A body completo, subchapter titles 1.1-12.6 (50 entries × 3 idiomas). Idiomas: es/en/pt |
| **ReportDesigner sub-agente** | Operativo | Pipeline Structurer > Visualizer > Composer. 4 audiencias, ES/EN, dedupe semantico (category+URL+date), priorizacion ponderada |
| **Observer Protocol** | Operativo | Sesiones multi-fase con 9 fases electorales (preparatoria > pre-campaña > campaña > silencio > jornada > escrutinio > post-electoral > resolucion de disputas > completada) |
| **MOE Brief** | Operativo | /api/moe/brief/{code} + descarga markdown |
| **V-Dem v16 integrado** | Operativo (4-may) | Upgrade desde v15. Cobertura 1789-2025 (vs 1789-2024). 38 paises × 21 indicadores en `vdem_static.py` (618KB tracked, fallback Railway sin CSV). CSV completo (~440MB) en `data/vdem/vdem_v16.csv` excluido de git. `VDEM_VERSION` lee de env, default `v16`. Cita academica actualizada (vdemds26) |
| Freedom House FIW integrado | Operativo | 2.723 filas, ediciones 2013-2025 |
| PEI 10.0 integrado | Operativo | 586 elecciones, 2012-2023 |
| RSF 2025 integrado | Operativo | 180 paises, index libertad de prensa |
| Marco legal | Operativo | 14 instrumentos en taxonomia propia: ICCPR, CADH, CDI, CEDAW, OSCE/ODIHR, UNDRIP, jurisprudencia CIDH, Constitucion Peru 1993, LOE 26859, LOP 28094, Resoluciones JNE |
| **8 fuentes RSS Peru** | Operativo | Andina, RPP, El Comercio, Gestion, IDL-Reporteros, Wayka, JNE, ONPE — mapeadas a fases electorales |
| **OONI integration** | Operativo | Censura de internet (date-only since/until tras fix 22-abr) |
| **Discord webhook alerts** | Operativo | Severidad >= high dispara notificacion |
| **SQLite triple-tier persistencia** | Operativo (4-may) | reports + sessions + entries + reportes elite. Tablas `elite_reports` con columnas TEXT `md_content` y `html_content` — el reporte sobrevive aunque el filesystem del volumen se corrompa. Re-render desde DB sin perder data |
| **Hardening produccion** | Operativo | Auth X-Observer-Key, rate-limit por IP, budget diario por pais (cap configurable via `MAX_ELITE_PER_DAY`, default 5), fallbacks gracias. CORS con dominios explicitos + soporte wildcard via regex |
| **PDF export Elite** | Operativo (4-may, refactor) | Removido xhtml2pdf (pycairo no compila en Nixpacks Railway). Reemplazo: endpoint `/printable` que sirve HTML estilizado para `window.print()` del browser → PDF nativo. Cero dependencias C-extension |
| **Markdown export** | Operativo | MOE Brief + informe completo. Section titles traducidos via `section_titles.py` |
| **Endpoint /structured** | Operativo (4-may) | `/api/elite-report/{run_id}/structured` extrae secciones especificas del MD del informe (titulo, sintesis, recomendaciones, anexos). Para preview rapido sin re-generar |
| Dashboard React multi-tab | Operativo | Overview / Detalle / Sentinel / Peru Situation Room / Metodologia |
| Peru Situation Room | Operativo | Tabs: Alertas / Calendario / Datos / Series V-Dem / Actores / Parlamento / MOE Brief / Jornada / Evaluacion / Metodologia / Informe Elite + Consulta constitucional |
| Catalogo paises | Operativo | 38 paises (Americas, Europa Este, Africa, Asia) |
| /api/country/{code} | Operativo | Datos por pais con cache 24h |
| /api/peru/actors | Operativo | 8 fuerzas politicas 2026 con perfiles ICCPR |
| /api/peru/scenarios | Operativo | 4 escenarios parlamentarios + datos regionales |
| Trazabilidad APA 7 | Operativo | Cada dato con source/url/date/confidence_level. Bloques sin URL primaria son postergados antes que publicarse (politica del Architect Agent) |
| **Deploy Railway + Netlify** | Operativo | Auto-deploy con git push, healthcheck /api/health (timeout 300s), volumen persistente. Frontend en democracia.ar. **Dual-deploy resuelto el 4-may** (proyecto secundario `api.democracia.ar` con auto-deploy desactivado) |
| **Sprint 1: tests integrados** | Operativo (4-may) | 9 tests nuevos en `backend/tests/test_elite_pipeline.py` cubriendo VizKind dispatch, FindingRef shape, PredictiveEngine returns, attach_visualizations, render SVG por kind, ChapterComposer no-LLM mode, `_format_vdem_emb`, disclosure presence. 91/91 tests del suite total pasando. `requirements-dev.txt` separado |
| **scripts/backup.py** | Operativo (4-may) | Backup completo de prod state (SQLite, reports filesystem, env vars no-secretas) con flag `--targz` para snapshot single-file. Ejecutar antes de operaciones de riesgo |
| **scripts/generate_vdem_static.py** | Operativo (4-may) | Regenera `backend/modules/vdem_static.py` desde el CSV completo. Para refrescar el tier estatico cuando V-Dem libere v17 o se cambien indicadores monitoreados |
| **Disclosure neutral** | Operativo (4-may) | Cover, declaracion preliminar y footer NO mencionan organismos especificos. Texto: "bajo estandares internacionales de observacion electoral, sin sesgo politico-partidario" |

### Componentes Pendientes

| Componente | Estado | Prioridad |
|---|---|---|
| Sprint 2 — CountryAdapter | Pendiente (blocking BRA/USA): extraer logica PER a adapter pluggable, eliminar `if country_code == "PER"` distribuido | Alta |
| Sprint 3 — Modelo institucional generalizado | Pendiente (6-8h): soporte federal centralizado (BRA), federal descentralizado (USA) | Alta |
| Sprint 4 — Traducir 13 prompts cap_NN.md a en/pt | Pendiente (8-10h): elimina restos de español en narrativa LLM. Mientras tanto, parche `section_titles.py` cubre los headers | Alta |
| Sprint 5 — Brasil 2026 onboarding | Pendiente (10-12h, antes 4-oct-2026) | Alta |
| Sprint 6 — USA 2026 midterms onboarding | Pendiente (12-16h, antes 3-nov-2026) | Alta |
| Frontend feature flags + preview unlock | Pendiente: tabs Brasil/USA con `?preview=DEMOCRACIA_PREVIEW_2026` | Media |
| Citation builder i18n | Meses en español, "Recuperado de" → "Retrieved from" | Media |
| Predictive scenarios narrative i18n | Implications/indicators/watch_signals en español dentro de narrativa | Media |
| WebSocket alertas en vivo | No existe (Discord webhook lo cubre parcialmente) | Baja |
| Mapa mundial interactivo | No existe | Media |
| Multi-idioma FR para Africa | Solo ES + EN + PT | Baja |
| Detección estadística de anomalías ML | Hunter clasifica pero no detecta anomalias temporales | Media |
| API publica externa con tiers | Solo X-Observer-Key interna | Baja |
| Sistema de usuarios (observador/analista/admin) | No existe | Baja |

---

## EVOLUCION POR SESIONES (SCRIPT DEL TRABAJO)

> Este es el script cronologico de todas las sesiones de trabajo desde
> el primer commit. Cada bloque corresponde a una sesion identificable
> por fecha, con los entregables especificos. Util para auditoria de
> producto, presentacion a inversores/partners, y como evidencia
> historica del crecimiento del codebase.

### Sesiones 7 al 12-may-2026 (cierre v0.6.0)

Bloque de trabajo de una semana cubriendo Sprint Hunter-International,
automatizaciones, auditoria de visualizaciones, methodology doc para
partners, y los Sprints 2-4 del roadmap multipais.

#### 7-may-2026 — Sprint Hunter-International

- `integrations/peru_sources.py`: 8 fuentes peruanas + 6 internacionales
  (BBC LatAm, BBC Mundo, DW español, El País Internacional, Guardian
  World, NYT Americas). Filtro `_filter_intl_relevant` con keywords
  "peru/perú/lima".
- `loaders/hunter_loader.py`: credibility scores 1.1-1.2 para fuentes
  intl. Commit `3ca2e22`.

#### 8-may-2026 — Cadencia 24h + automatizaciones

- `HUNTER_INTERVAL_MINUTES=1440` (era 240): reduce costo LLM ~6×.
- 3 background loops nuevos en `app.py`:
  - `_phase_auto_advance_loop()` cada 6h con calendar 1ra+2da vuelta PER
  - `_daily_digest_loop()` a las 13:00 UTC con resumen 24h a Discord
  - `_daily_backup_loop()` a las 03:00 UTC tar.gz del volumen
- Opt-out via env vars `AUTO_PHASE_ADVANCE`/`DAILY_DIGEST_ENABLED`/
  `DAILY_BACKUP_ENABLED`. Commit `a147f77`.

#### 9-may-2026 — Auditoria visualizaciones + brand

- **Brand:** logo `BrandLogo` target glyph (dos círculos + punto
  terracota) + wordmark Democrac.IA. Reemplaza "D" gradiente. Favicon
  con fondo dark. Commit `0ecc2ee`.
- **Sprint Hunter-International cobertura Peru:** sumado `Informe_Elite_PER_preliminar_2026-05-03.html` al repo para acceso rápido.
- **Auditoría 9-may** detectó 3 visualizaciones con mock hardcoded:
  - G1 Radar 8 dimensiones (55, 72, 28, ...) — fixeado con
    severity-weighted del corpus
  - G2 Semáforo institucional (JNE=amber/ONPE=red/RENIEC=green
    hardcoded) — fixeado con keyword match + status derivado
  - G3 Progress chart (6 puntos mock 21:00 12.4%, ...) — fixeado con
    regex `\b(\d{1,3}(?:[.,]\d+)?)\s*%` sobre Hunter findings
  - L1 Citation builder "Recuperado de" no traducido — fixeado APA 7
    trilingüe
  - M1-M5 PER hardcoded (matrix_normativa, actor_network, etc.) —
    diferido a Sprint 2
- Heatmap derechos × categorías: 3 fixes (match exacto, rights
  dinámicos, i18n de instrumentos). Commit `87e5e24`.
- Lead observer eliminado del cover (default "" + render condicional).
- Logo target glyph embedded en cover del informe. Disclosure neutral
  preservado. Commit `25a604e`.

#### 10-may-2026 — Crisis Index real + Sprint 2

- **Crisis Index v1.0:** fórmula `Σ(SEV_W × count) / total_findings`
  con pesos `{critical:1.00, high:0.55, medium:0.20, low:0.05, info:0}`.
  Reemplaza magic number 0.88. Commit `2793a70`.
- **`PEIRS_Indices_Methodology_v1.0.md` (NUEVO)** — documento
  técnico-académico para citas formales por Ágora Data, tribunales,
  organismos supranacionales. 8 secciones cubriendo Crisis Index,
  Forecast, Compliance Matrix, Radar, datasets de origen con DOIs.
- **Sprint 2 — CountryAdapter:** `country_adapters/{base.py, peru.py,
  __init__.py}`. Movidas ~200 líneas PER-específicas de
  `elite_report.py:_attach_visualizations`. Pluggable para BRA/USA via
  registro en `_ADAPTERS`. Commit `5d4fa16`.

#### 11-may-2026 — Sprint 3 InstitutionalModel

- **Sprint 3 — Modelo institucional generalizado:** dataclasses
  `EMBBody`, `LegalLayer`, `InstitutionalModel` cubriendo 3 tipos
  (unitary, federal_centralized, federal_descentralized).
  `PeruAdapter.institutional_model()` declara sistema unitario con
  JNE+ONPE+RENIEC+JEE + 4 capas normativas. Test integrado nuevo.
  Foundation para BrazilAdapter (TSE+TREs) y USAAdapter (50 estados
  sin EMB nacional). Commit `248cc41`.

#### 12-may-2026 — Sprint 4 prompts EN

- **Sprint 4 — Traducción de 14 prompts a EN:**
  `composer/prompts/{es,en,pt}/` estructura nueva. Loader trilingüe
  con fallback a ES. 14 archivos traducidos: `base_context.md` +
  `cap_00..cap_12.md`. PT cae a ES (pendiente Sprint 5). Cierra el
  último bolsillo de español en narrativa LLM para reportes EN.
  Commit `810e2db`.
- **Memory updates:** project memories `project_peru2026.md`
  (estado al 12-may) + `project_brazil_usa_2026.md` (nuevo,
  Sprints 5/6 con plantillas) + 4 feedback memories nuevas
  (railway_edge_sync, no_magic_numbers, no_mock_data_in_prod,
  railway_redeploy_vs_build).

### Sesion 4-may-2026 (cierre v0.5.2)

Sesion de hardening + i18n + recuperacion ante incidente. Trabajo
ordenado en 4 bloques:

#### Bloque A — Recuperacion Railway (incidente y resolucion)

- **Incidente 4-may 11:00 ART:** durante limpieza del dual-deploy, se
  ejecuto la accion de borrar el proyecto Railway equivocado. Se elimino
  por error el proyecto **primario** `democracia-peirs-production` (con
  secrets, LLM, sesiones activas, volumen con SQLite + reports) en lugar
  del secundario vacio `api.democracia.ar`.
- **Diagnostico:** TCP+TLS al edge de Railway funcionaban pero requests
  colgaban infinito. Patron tipico de container deleted con DNS aun
  apuntando al edge.
- **Resolucion (15:30 ART):** restore desde dashboard de Railway con la
  ventana de "Recently Deleted Projects". Volumen recuperado integro,
  sesion PER 2026 activa preservada, todos los reportes generados
  intactos.
- **Lecciones aplicadas:** secundario quedo con auto-deploy DESACTIVADO
  (no eliminado, por seguridad). Procedimiento documentado: cualquier
  futura limpieza requiere triple-check de URL antes de delete.
- **Tiempo de downtime:** ~4h hasta restore + ~12 min adicionales para
  primer deploy post-restore.

#### Bloque B — i18n profundo del Elite Report (es/en/pt)

Hallazgo: usuaria descargo informe Peru en EN y vio `~120 strings
hardcoded en español`. Auditoria sistematica + traduccion en 3 commits:

- **Commit `3733d67`** (i18n del chrome): cover, footer, TOC,
  declaracion preliminar, render_chapter, render_appendix_a/b/c,
  render_markdown. SVG label wrap a 2 lineas. Bibliografia con padding
  CSS corregido.
- **Commit `afc4971`** (i18n profundo): 120+ keys cubriendo viz titles
  (21), captions (21), uppercase headers de SVG (12), status labels
  (OK/Watch/Crisis), gauge bands (GREEN/AMBER/ORANGE/RED), compliance
  status (COMPLIES/PARTIAL/BREACH/N/D), compliance columns
  (ARTICLE/TOPIC/EVIDENCE/STATUS), recommendations columns. Datos
  internos de actor_network (Prosecutor's Office, Judiciary, Independent
  press), flow_voting, network_inst, recommendations_data,
  architecture_data, early_warning_data — todos traducidos por idioma
  del informe.
- **Commit `06866a4`** (Appendix A + scenario labels + alert badge): el
  cuerpo del Appendix A (Pipeline PEIRS, EliteLoader, PhaseOrganizer,
  Fuentes Hunter, Limitaciones) pasa por `t()`. Forecast scenarios
  labels traducidos via lookup `forecast.scenario.{scenario_id}.label`
  con fallback al original. Forecast badge `ALERTA` → `ALERT`. Heatmap
  legend de severidades (bajo/medio/alto/critico). Architecture caption
  con la key `viz.audit_note` que ya existia pero no se usaba.
- **Commit `563dec6`** (subchapter titles): nuevo modulo
  `agents/elite_report/section_titles.py` con dict de 50 entradas
  cubriendo 1.1-12.6 traducidas a en/pt. Funcion
  `translate_section_titles(md, lang)` aplicada en `_render_chapter` y
  `render_markdown` antes de convertir markdown a HTML. Parche puente
  hasta Sprint 4 (traducir prompts).
- **LANGUAGE_RULE reforzado** en `chapter_composer.py`: bloque explicito
  por idioma instruyendo al LLM "Respond in 100% English even though
  context blocks are in Spanish". Entrada `pt` agregada.

#### Bloque C — V-Dem v16 upgrade

- **Commit `cb2ae9b`** (precursor): SQLite TEXT columns `md_content` +
  `html_content` para sobrevivir a perdidas del filesystem del volumen.
  Reportes ahora en triple-tier (filesystem + SQLite TEXT + PDF
  on-demand).
- **Upgrade V-Dem v16:** `data/vdem/vdem_v16.csv` (~440MB, excluido de
  git). `backend/modules/vdem_static.py` regenerado: 38 paises × 21
  indicadores × 1985-2025 (618KB tracked en git). `VDEM_VERSION = "v16"`,
  `VDEM_LAST_YEAR = 2025` en `modules/config.py`. Cita academica:
  "Coppedge et al. 2026. V-Dem Country-Year Dataset v16. Project. doi:
  10.23696/vdemds26".
- **Commit `b99e022`** (fix display): `app.py:372` y `app.py:5518`
  tenian `vdem_v15` hardcoded. Migrados a leer de
  `os.getenv("VDEM_VERSION", "v16")`. El feature flag en `/api/health`
  ahora se construye con f-string del valor real.
- **Script generador** (`scripts/generate_vdem_static.py`): regenera el
  static fallback desde el CSV completo. Para futuros uplifts (v17,
  v18) o cambio de indicadores monitoreados.

#### Bloque D — Sprint 1: tests integrados + backup + UX

- **Commit `14e9023`** (Sprint 1 tests): `backend/tests/test_elite_pipeline.py`
  con 9 tests:
  1. `test_vizkind_covers_dispatcher_kinds`
  2. `test_findingref_has_required_attrs`
  3. `test_predictive_engine_no_setattr_on_list`
  4. `test_predictive_engine_returns_correct_payload_shape`
  5. `test_attach_visualizations_runs_with_real_bundle`
  6. `test_all_wired_kinds_render_valid_svg`
  7. `test_chapter_composer_compose_chapter_handles_no_llm`
  8. `test_format_vdem_emb_returns_quantitative_block`
  9. `test_disclosure_present_in_cover_render`
- **`requirements-dev.txt`** separado de prod (pytest + plugins NO
  van a Railway).
- **`scripts/backup.py`** con flag `--targz` para snapshot single-file
  de prod (SQLite + reports filesystem + env-vars no-secretas).
- **Commit `b24019f`** (UX pre-checks): pre-check del LLM antes de
  spawn del Elite Report (evita 60s de LLM call si key invalida o
  creditos cero). `period_end` dinamico calculado desde fecha de
  eleccion + 30 dias.
- **Commit `c953c67`** (`/structured` endpoint): extrae secciones
  especificas del MD del informe (titulo, sintesis, recomendaciones,
  anexos) sin re-generar. Para preview rapido y reuso.
- **Commit `0c091b9`** (CORS hardening): default a dominios explicitos.
  Soporte wildcard via regex (`ALLOWED_ORIGINS=*` se mapea a `.*`)
  para ser compatible con `allow_credentials=True`.
- **Commit `7d5b5b9`** (precursor a esta sesion pero relacionado):
  `init_rag()` movido a `asyncio.create_task(asyncio.to_thread(...))`
  para no bloquear el event loop. Healthcheck Railway responde rapido
  desde startup.
- **Commit `3422036`** (disclosure neutral): texto del cover, footer y
  declaracion no menciona organismos especificos. Reemplazo: "bajo
  estandares internacionales de observacion electoral". Wrap de leyendas
  SVG a 2 lineas via helper `_wrap_2lines()`.
- **Commit `371146e`** (metodologia): nuevo documento
  [DOCS Proyect/INFORME_METODOLOGIA.md](INFORME_METODOLOGIA.md) — 9
  secciones del playbook reproducible.
- **Commit `5de6b32` + `d6637c7`**: backup script + `backups/` ignorado
  por git.

### Sesion 27-abr-2026 (v0.5.0)

Cierre de SENTINEL/Hunter, RAG Constitucionalista, Architect Agent
autonomo, Elite Report 12-capitulos, ReportDesigner sub-agente,
hardening de produccion, migracion a SQLite. (Detalles en commits
anteriores a `cb2ae9b` y en versiones previas de este roadmap.)

### Sesiones previas (v0.3.x → v0.4.x)

Pipeline LangGraph 4 agentes original. Carga de datasets V-Dem v15,
FH FIW, PEI 10.0, RSF 2025. Catalogo de 38 paises. Integracion OONI.
8 fuentes RSS Peru. Frontend React multi-tab con Peru Situation Room.
Deploy inicial Railway + Netlify. (Ver historial git para granularidad.)

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
| Backend | Python + FastAPI | 3.11 (Railway) / 3.14 (dev local) + 0.115 | Operativo. Confirmado parity tras incidente PEP 701 nested f-strings (3.14 acepta, 3.11 no) |
| LLM analista | Claude Sonnet 4.6 (clasificacion + composicion) | claude-sonnet-4-6 + prompt caching | Operativo |
| LLM autonomo | Claude Opus 4.7 (Architect Agent) | claude-opus-4-7 + claude-agent-sdk | Operativo |
| Orquestacion agentes | LangGraph + LangChain | 0.2 + 0.3 | Operativo |
| RAG | ChromaDB + sentence-transformers | all-MiniLM-L6-v2 (90MB) | Operativo. `init_rag` en `asyncio.to_thread` para no bloquear startup |
| Base de datos | SQLite triple-tier (filesystem + TEXT columns + PDF on-demand) | -- | Operativo |
| Scheduler | Hunter loop async | intervalo 4h configurable | Operativo |
| OSINT feeds | RSS via httpx + xml stdlib | 8 fuentes Peru por fase | Operativo |
| Censura internet | OONI API | date-only since/until | Operativo |
| Alertas | Discord webhook | severidad >= high | Operativo |
| Frontend | Vite + React + Recharts | 7.x + 18 + 2.x | Operativo |
| CSS/Fonts | DM Sans, DM Mono, Fraunces | CDN | Operativo |
| PDF | Browser-native via `/printable` + `window.print()` | -- | Operativo (4-may). Removido xhtml2pdf (pycairo no compila en Nixpacks) |
| i18n | `agents/elite_report/i18n.py` (180+ keys) + `section_titles.py` (50 entries) | es/en/pt | Operativo (4-may) |
| Tests | pytest + pytest-asyncio | 91/91 pasando | `requirements-dev.txt` separado de prod |
| Deploy backend | Railway (Nixpacks) con volumen persistente + healthcheck | -- | Operativo. **Restore Recovery procedure** documentado tras incidente 4-may |
| Deploy frontend | Netlify auto-deploy con git push | democracia.ar | Operativo. `VITE_API_BASE` apunta a primario |
| Auth | X-Observer-Key + rate-limit por IP + budget diario por pais (`MAX_ELITE_PER_DAY`) | -- | Operativo |
| CORS | Dominios explicitos por default + soporte wildcard via regex (compat con `allow_credentials=True`) | -- | Operativo |
| WebSocket | -- (Discord webhook lo cubre parcialmente) | -- | No prioritario |
| CI/CD | GitHub (manual + Railway auto-deploy desde `main`) | -- | Parcial. Secundario `api.democracia.ar` con auto-deploy DESACTIVADO |
| Backup | `scripts/backup.py --targz` | -- | Operativo (4-may) |

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
| #001 | V-Dem CSV no esta en git por tamaño (~440MB) — instrucciones en README | Media | Mitigado: `vdem_static.py` (618KB) provee fallback completo en Railway |
| #002 | SENTINEL /api/sentinel/alerts devuelve datos estaticos, no OSINT real | Media | Mitigado: Hunter scheduler cubre el caso de uso real con clasificacion ML |
| #003 | Marco legal y padron electoral Cap. 2: mock para paises no-PER | Media | Abierto. Sprint 3 (modelo institucional generalizado) lo resuelve |
| #004 | Contador confianza Agente Legal no cuenta PEI correctamente | Baja | Abierto |
| #005 | Warning "Duplicate key border" en App.jsx | Baja | Abierto |
| #006 | PEI Venezuela: OVERALLINTEGRITY = N/D (datos 2018, fuera de rango) | Info | Abierto |
| #007 | reports_store en memoria — se pierde entre reinicios | Resuelto | SQLite triple-tier con `md_content`/`html_content` TEXT |
| #008 | Dashboard mostraba marcadores de capitulo | Alta | Resuelto |
| #009 | UnicodeEncodeError en prints con emojis (Windows cp1252) | Alta | Resuelto (PYTHONUTF8=1 + `sys.stdout.reconfigure`) |
| #010 | Python 3.11 vs 3.14 PEP 701 parity (nested f-strings) | Alta | Resuelto: convencion de NO usar `f"""...{f"""..."""}..."""`, precomputar variables |
| #011 | xhtml2pdf rompe build Nixpacks (pycairo C-extension) | Alta | Resuelto: `/printable` endpoint con `window.print()` |
| #012 | Volumen Railway pierde reportes en crash | Alta | Resuelto: SQLite TEXT columns como segunda capa |
| #013 | `init_rag` blocking startup — Railway healthcheck timeout | Alta | Resuelto: `asyncio.create_task(asyncio.to_thread(init_rag))` |
| #014 | CORS hardcoded incompleto, faltaba `democracia.ar` | Alta | Resuelto: default a dominios explicitos + soporte wildcard regex |
| #015 | `parliament_scenarios` no estaba en VizKind Literal | Alta | Resuelto: agregado |
| #016 | `PredictiveEngine` intentaba `setattr` sobre list | Alta | Resuelto: refactor a tuple return |
| #017 | `FindingRef` AttributeError (timestamp/location/source_org) | Alta | Resuelto: campos reales son `recorded_at`, `source_name`. `location` agregado como Optional |
| #018 | Disclosure mencionaba organismos especificos (OEA, EU EOM, Carter) | Alta | Resuelto: texto neutro "estandares internacionales" |
| #019 | Bibliografia: numeracion `[N]` mezclada con texto del item | Alta | Resuelto: padding CSS + `::before` absolute |
| #020 | Informe EN tenia ~120 strings hardcoded en español | Alta | Resuelto en 4 commits (i18n profundo + section_titles + Appendix A + scenarios) |
| #021 | `vdem_v15` hardcoded en `app.py` aunque modulo `config.py` migro a v16 | Media | Resuelto: lectura via `os.getenv` |
| #022 | Dual-deploy Railway (cada push buildea en 2 proyectos) | Media | Mitigado: secundario con auto-deploy DESACTIVADO. Pendiente delete formal con triple-check |
| #023 | Eliminacion accidental de proyecto Railway primario | Critico | Resuelto: restore desde dashboard, volumen integro |

---

## ROADMAP DE SPRINTS — POST v0.5.2

> Tras el cierre del 4-may-2026, los proximos sprints estan condicionados
> por las elecciones de Brasil (4-oct-2026) y USA midterms (3-nov-2026).
> Orden no-negociable: Sprints 2 y 3 son blockers para escalar a otro pais.

### Sprint 2 — CountryAdapter (4-6h, blocking)

Extraer logica especifica de Peru a un adapter pluggable. Eliminar el
patron `if country_code == "PER":` distribuido en backend.

- Crear interfaz `CountryAdapter` con metodos `get_actors`, `get_phases`,
  `get_legal_framework`, `get_emb_config`, `get_static_events`.
- Implementar `PeruAdapter` con la logica actual.
- Refactorizar puntos de uso a `adapter = get_adapter(country_code)`.
- Tests: cobertura de cada metodo del adapter.

### Sprint 3 — Modelo institucional generalizado (6-8h, blocking)

Soporte para arquitecturas institucionales distintas a la peruana:

- **Federal centralizado (Brasil):** TSE + TREs estaduales, sistema
  unico de tabulacion electronica.
- **Federal descentralizado (USA):** sin EMB nacional, 50 estados +
  DC con legislacion propia, voting machines heterogeneas.

Tareas:

- Modelo `InstitutionalArchitecture` con campos `level`, `embs`,
  `transmission_chain`, `audit_components`, `legal_framework_layered`.
- Refactor de `architecture_data` (cap 3) para que renderice cualquier
  topologia.
- Tests: validar modelos con datos PER, BRA, USA stub.

### Sprint 4 — Traducir 13 prompts cap_NN.md a en/pt (8-10h)

Cubre el ultimo bolsillo de español en el output del LLM:

- 13 archivos: `cap_00.md` a `cap_12.md` + `base_context.md`.
- Por archivo: traducir instrucciones, ejemplos, section IDs.
- Mantener estructura `## N.M Title` exacta para que `section_titles.py`
  siga funcionando como red de seguridad.
- Validacion: generar informe EN y PT completo, comparar contra ES.

Una vez completo, `section_titles.py` se mantiene como capa defensiva.

### Sprint 5 — Brasil 2026 onboarding (10-12h, antes 4-oct-2026)

- Nuevo `BrasilAdapter` con TSE + TREs, sistema biometrico, urna
  electronica.
- Carga del calendario electoral 2026 (TSE oficial).
- 5-8 fuentes RSS verificadas (Folha, Estado, O Globo, Agencia Brasil,
  CNN Brasil, Conjur, JOTA, Poder360).
- Marco legal: Codigo Eleitoral (Lei 4.737/65), Lei das Eleicoes
  (9.504/97), Lei dos Partidos (9.096/95), Resolucoes TSE 23.610/2024.
- Tab "Brasil 2026" en frontend con preview-unlock (`?preview=...`).
- Testing: generar informe sample con datos sinteticos.

### Sprint 6 — USA 2026 midterms onboarding (12-16h, antes 3-nov-2026)

Mas complejo que Brasil por la heterogeneidad de 50 estados:

- `USAAdapter` con modelo descentralizado (Election Assistance
  Commission federal pero sin autoridad ejecutiva).
- Mapeo estado por estado de las primary methods (closed/open/jungle),
  voter ID, mail-in ballots, registration deadlines.
- Marco legal por capa: 1st/14th/15th/19th/24th/26th Amendments, VRA
  1965, HAVA 2002, NVRA 1993.
- 6+ fuentes RSS (NYT/WaPo/AP/Reuters/Politico/Brennan Center).
- Especifico USA: monitor de voter suppression, gerrymandering, election
  denial rhetoric (categoria nueva en Hunter).
- Tab "USA 2026" con disclaimer de cobertura federal-only para midterms.

### Sprints horizontales (paralelos, no-blocking)

- Citation builder i18n (1-2h)
- Predictive scenarios narrative i18n (3-4h)
- Frontend feature flags + preview unlock (4-6h)

---

## PROCEDIMIENTOS OPERATIVOS

### Restore de proyecto Railway eliminado por error

> Procedimiento documentado tras incidente del 4-may-2026.

1. Acceder a [railway.app](https://railway.app) → Account Settings.
2. Buscar **"Recently Deleted Projects"** o **"Trash"** en sidebar.
3. Si aparece el proyecto: click → **Restore**.
4. Si no aparece (ventana de 7 dias agotada o plan sin restore):
   contactar soporte por chat dentro del dashboard con esta plantilla:
   > *"Hi — I accidentally deleted my production project today (DATE),
   > name was X. It had a persistent volume with critical data. Please
   > restore the project and the volume ASAP. Thanks."*
5. Tras restore: el deploy puede tardar 5-10 min en levantar el
   container nuevo. Volumen viene integro si Railway lo restauro
   correctamente.
6. **Verificar despues del restore:** `/api/health` debe responder 200,
   `active_observation_sessions` debe coincidir con lo previo, version
   en feature flag debe ser la esperada.

### Reset de Observer Key en browser

Si la usuaria pierde el `localStorage` (incognito, clear cache):

1. En Railway → primario → **Variables**, copiar valor de `OBSERVER_API_KEYS`.
2. Navegar a `https://democracia.ar/?key=ESA_KEY`.
3. Frontend ingiere automaticamente, guarda en localStorage, limpia URL.
4. Refresh con `Ctrl+F5` para activar la nueva key en todos los requests.

### Trigger redeploy desde main sin tocar el secundario

> Para subir codigo nuevo al primario sin disparar build en secundario.

1. Verificar en secundario (`api.democracia.ar`) → Settings → Source
   que **"Auto deploys when pushed to GitHub"** este en **DESACTIVADO**.
2. `git push origin main` → solo el primario buildea.
3. Cuando el secundario tenga que sincronizarse (rara vez), activar
   manualmente desde dashboard, esperar build, desactivar de nuevo.

### Subir el budget diario de Elite Reports

`MAX_ELITE_PER_DAY` (default 5). Para subirlo:

1. Railway → primario → **Variables** → editar/agregar
   `MAX_ELITE_PER_DAY=20` (o el valor deseado).
2. Railway redeploya automaticamente al cambiar variables.
3. Verificar en `/api/health` que el container esta operativo.
4. El proximo intento ya respeta el limite nuevo.

---

## ANCLAJES PARA DOSSIER DE PARTNERS (V-Dem, FH, PEI, RSF)

> Cuando se construya el dossier institucional para presentar a los 4
> dataset partners, los puntos clave a incluir son:

### Atribucion correcta de datasets

| Dataset | Atribucion exacta | Documento de licencia |
| --- | --- | --- |
| V-Dem v16 | "Coppedge et al. 2026. V-Dem Country-Year Dataset v16. Varieties of Democracy (V-Dem) Project. <https://doi.org/10.23696/vdemds26>" | <https://v-dem.net/data/data-version-16/> |
| Freedom House FIW | "Freedom House. 2025. Freedom in the World 2025. <https://freedomhouse.org/report/freedom-world/2025>" | Open data terms |
| PEI 10.0 | "Norris, Pippa et al. 2024. Perceptions of Electoral Integrity Dataset (PEI-10.0). Harvard Dataverse." | Open with attribution |
| RSF 2025 | "Reporters Without Borders. 2025. World Press Freedom Index 2025. <https://rsf.org/en/index>" | CC-BY-NC |

### Evidencia de uso fiel

- Trazabilidad APA 7 sobre cada dato en el informe.
- Citas en bibliografia (Anexo B) con URL al dataset original.
- Disclosure neutro de no-legitimacion en cover, declaracion preliminar
  y footer de cada informe.
- Triple-tier de persistencia para auditoria post-publicacion.

### Metricas de uso (a calcular antes de presentar)

- Numero de paises analizados con cada dataset.
- Numero de informes Elite generados.
- Cobertura temporal (V-Dem 1789-2025, FH 2013-2025, PEI 2012-2023, RSF 2025).
- Casos de uso publicos (Peru 2026 hasta el momento).

---

*Documento actualizado por Democrac.IA — Claude Opus 4.7 — 2026-05-04 (v0.5.2)*
*Refleja la arquitectura real al cierre del 4-may-2026, despues de la sesion
de hardening + i18n profundo + V-Dem v16 upgrade + recuperacion del incidente
Railway. Ver seccion "Evolucion por sesiones" para el script cronologico
completo.*
*Clasificacion: Uso interno -- Fundadora y equipo tecnico*
