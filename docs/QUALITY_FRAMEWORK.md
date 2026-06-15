# Marco de Calidad PEIRS — estándar canónico de informes

> Modelo de referencia para todos los informes de Democrac.IA PEIRS (Perú 2026 y
> los próximos países: Brasil, USA). Todo informe se autoevalúa contra los **6
> pilares**; un informe no se publica si no cumple el umbral de cada pilar.

Versión del marco: **1.0** · Origen: auditoría experta multidisciplinaria del
informe Perú 2026 (junio 2026). Implementación de referencia: `backend/agents/elite_report/`.

---

## Principios rectores

1. **Monitoreo, no observación.** PEIRS hace monitoreo automatizado de fuentes
   abiertas; complementa, no sustituye, a las misiones de observación humanas.
2. **El proceso, no el resultado.** Se observa la integridad del proceso, no las
   propuestas ni las candidaturas. Apartidario.
3. **Nada sin fuente.** Ningún dato se afirma sin trazabilidad a su fuente
   primaria. Prohibido inventar cifras, años o hechos.
4. **Ausencia ≠ normalidad.** Nunca inferir que algo "funcionó bien" a partir de
   la ausencia de hallazgos. Se distingue *documentado* de *vacío de cobertura*.
5. **Retrospectivo y honesto con la incertidumbre.** No se anticipan desenlaces;
   los resultados provisionales se marcan como tales y se cuantifica su incertidumbre.

---

## Los 6 pilares (con umbral mínimo)

### 1. Trazabilidad
- Cada hecho rastreable a su fuente primaria; **un hecho = un hallazgo con todas
  sus fuentes** (consolidación, no repetición).
- Anexo C completo con columna de fuentes y fase.
- *Implementación:* `consolidators.py`, `_render_appendix_c`, `runoff_enrichment`.

### 2. Rigor estadístico e incertidumbre
- Toda cifra con su calidad de dato; sin afirmaciones sin denominador.
- Resultados provisionales: cuantificar incertidumbre **vs margen** (si los votos
  en juego superan el margen ⇒ "estadísticamente indeterminado").
- *Implementación:* `second_round_results.uncertainty`; render en síntesis y
  sección de riesgo.

### 3. Auditabilidad de IA
- Versión de pipeline + **hash de configuración** + huella del clasificador
  (modelo + hash del prompt) estampados en cada informe (Anexo A).
- Validador anti-alucinación post-LLM (cifras del texto deben existir en el corpus).
- Config centralizada y versionada (sin *magic numbers* dispersos).
- Capítulos LLM marcados como no deterministas; secciones de datos deterministas.
- *Implementación:* `modules/audit_config.py`, `llm_guard.py`, `EliteReportOutput`
  (`pipeline_version`/`config_version`/`config_hash`/`classifier`), `_render_version_block`.
- *Pendiente (P0.5/P0.6):* archivado del contenido fuente (no solo URL) + store append-only.

### 4. Cobertura y método
- Sección de **Metodología y Limitaciones** explícita: marco muestral y sus
  sesgos, límites del clasificador, no-determinismo LLM, qué puede/no evaluar el monitoreo.
- *Implementación:* `_render_appendix_a` (h_sampling, h_limits, h_version).

### 5. Estándares internacionales
- Encuadre ICCPR Art. 25 / CADH Arts. 23–25 + jurisprudencia interamericana
  (Yatama, Castañeda) cuando aplica.
- Panel consolidado V-Dem / Freedom House / RSF / PEI; triangulación con MOEs
  (OEA / UE / Carter / IDEA).
- *Pendiente (P1):* panel internacional + ingesta de declaraciones de MOEs.

### 6. Calidad visual/editorial
- Dashboard ejecutivo de 1 página (semáforo + KPIs + radar).
- Numeración de figuras; impresión profesional (orphans/widows, page-breaks,
  numeración de páginas); accesibilidad WCAG AA (contraste + aria-label).
- *Pendiente (P1):* `_render_executive_dashboard`, contadores CSS, reglas print.

---

## Checklist de onboarding por país (Brasil, USA, …)

1. **Adapter** — implementar `CountryAdapter` (`country_adapters/base.py`): 13 métodos
   + `vdem_emb_series()` + `adapter_config()` (nombres EMB ops/árbitro/registro, fechas).
2. **Datos** — crear `modules/{cc}_data.py` espejando las estructuras de `peru_data.py`
   (`{CC}_ELECTORAL_SYSTEM`, `{CC}_RUNOFF_{año}` con `uncertainty`, `{CC}_VDEM_STATIC`,
   `{CC}_REGIONS_DATA`, fuerzas políticas).
3. **Registro** — `country_adapters/__init__.py` (`_ADAPTERS["{CC}"]`); extender `COUNTRY_NAMES`.
4. **i18n** — verificar strings genéricos; parametrizar fechas/EMB names vía adapter.
5. **Calidad** — correr la suite (`pytest tests/`) incluyendo invariantes: hash de config
   estable, anti-alucinación, incertidumbre renderizada, sin hardcodes `== "PER"`.

> Estado de agnosticismo (jun 2026): ~75% reutilizable. Refactors P2 pendientes para
> 100% (quitar `== "PER"` en `elite_report.py`, parametrizar i18n PER, `adapter_config()`).

---

## Rúbrica de calificación (autoevaluación por informe)

Cada pilar 0–10; el informe reporta su nota por pilar y global. Umbral de
publicación: ningún pilar < 6; global ≥ 7. (Perú 2026 al cierre de P0: global ~6,6,
en ascenso con P0→P2.)
