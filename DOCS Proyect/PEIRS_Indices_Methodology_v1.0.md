# DEMOCRAC.IA / PEIRS — Índices Cuantitativos: Metodología v1.0

**Documento técnico-académico — Ámbito de aplicación: Elite Report**
**Versión 1.0  |  Mayo 2026**
**Clasificación: Público — Citable en informes institucionales**

---

> *Este documento describe la construcción matemática de cada índice
> cuantitativo que aparece en el Elite Report de DEMOCRAC.IA / PEIRS. El
> objetivo es habilitar la cita formal de estos índices por parte de
> tribunales, organismos supranacionales, organizaciones de derechos
> civiles, instituciones académicas y socios de datos. Cada fórmula es
> reproducible y auditable contra los inputs del corpus.*

---

## 1. PEIRS Crisis Index (Cap 9 — Early Warning Meter)

### 1.1 Definición operacional

El **PEIRS Crisis Index** es un score continuo en `[0, 1]` que representa
la severidad ponderada del corpus de hallazgos del Hunter para una ventana
electoral monitoreada. Sintetiza en un único valor el balance entre
hallazgos de baja, media, alta y crítica severidad observados en el período.

### 1.2 Fórmula

```
                Σ ( SEV_W[severity] · count_by_severity[severity] )
crisis_index = ──────────────────────────────────────────────────────
                                total_findings
```

Sujeto a `crisis_index ∈ [0, 1]`.

**Pesos de severidad SEV_W:**

| Severity | Peso | Justificación |
|---|---|---|
| critical | 1.00 | Hallazgos que comprometen la integridad sistémica del proceso |
| high     | 0.55 | Hallazgos materialmente significativos pero no sistémicos |
| medium   | 0.20 | Anomalías documentadas que requieren observación continuada |
| low      | 0.05 | Incidencias menores, contextuales |
| info     | 0.00 | Información sin connotación de riesgo |

Donde `total_findings = Σ count_by_severity` (mínimo 1 para evitar
división por cero).

### 1.3 Mapeo a niveles cualitativos

El nivel cualitativo se deriva del índice cuantitativo (no se asigna
externamente):

| crisis_index | Nivel | Etiqueta APA |
|---|---|---|
| 0.00 ≤ x < 0.20 | green   | Estable |
| 0.20 ≤ x < 0.40 | amber   | Vigilancia |
| 0.40 ≤ x < 0.60 | orange  | Riesgo elevado |
| 0.60 ≤ x ≤ 1.00 | red     | Crisis |

### 1.4 Inputs y trazabilidad

- **Origen del corpus**: `bundle.hunter_entries` — entries del Hunter
  scheduler durante el período de observación, persistidas en
  SQLite (`observation_entries` table).
- **Cada entry** tiene severity asignada por Claude Sonnet 4.6 al
  clasificar el item RSS, con campos: `entry_id`, `severity`,
  `category`, `recorded_at`, `source_name`, `source_url`, `finding`,
  `confidence_level`, `agent_id`.
- **Trazabilidad** APA 7: cada finding del corpus tiene URL primaria
  verificable y timestamp. La metadata persiste cross-restart vía
  triple-tier SQLite + filesystem + TEXT columns.

### 1.5 Validación y limitaciones

**Validez interna:**

- Dependencia exclusiva del corpus monitoreado por Hunter scheduler.
- Sensible al volumen de findings — un período con pocos findings
  pero todos críticos puede arrojar índice alto sin representar
  estado sistémico (ver "Sample size" abajo).

**Limitaciones declaradas:**

- **Sample size**: índice válido solo si `total_findings ≥ 10`. Para
  total < 10 se reporta el índice junto con flag `sample_size = small`.
- **Fuentes**: PER 2026 Hunter monitorea 14 fuentes RSS (8 nacionales
  + 6 internacionales con filtro Peru-relevante). La cobertura sesgada
  a centros urbanos limeños es una limitación reconocida — la
  cobertura regional rural es indirecta.
- **Clasificación LLM**: Sonnet 4.6 asigna severity con criterios
  documentados en el system prompt del Hunter, pero la asignación
  individual no está calibrada formalmente contra rúbrica de
  observador humano (próximo Sprint).
- **Horizonte**: representa estado del período monitoreado, no
  proyección. Para proyección ver §2 (PredictiveEngine).

### 1.6 Implementación de referencia

```python
SEV_W = {"critical": 1.00, "high": 0.55, "medium": 0.20,
         "low": 0.05, "info": 0.0}

def crisis_index(findings):
    by_sev = Counter(f.severity for f in findings)
    if not by_sev:
        return 0.0, "green", "no_data"
    weighted = sum(SEV_W.get(s, 0) * c for s, c in by_sev.items())
    total = sum(by_sev.values())
    idx = max(0.0, min(1.0, weighted / total))
    if idx >= 0.60: level = "red"
    elif idx >= 0.40: level = "orange"
    elif idx >= 0.20: level = "amber"
    else: level = "green"
    sample_size = "small" if total < 10 else "ok"
    return idx, level, sample_size
```

Ubicación canónica: `backend/agents/elite_report/elite_report.py`,
función `_attach_visualizations`, sección `early_warning_meter`.

---

## 2. Forecast Probabilities (Cap 9 — Escenarios Probabilísticos)

### 2.1 Definición operacional

Conjunto de hasta 6 escenarios probabilísticos sobre la dinámica
post-electoral, cada uno con probabilidad estimada y banda de
confianza al 90%.

### 2.2 Pipeline híbrido

```
PredictiveEngine.forecast(bundle) =
    rule_engine(bundle.hunter_entries, bundle.cross_references)
    + claude_refinement(rule_output, country_context)
```

**Etapa 1 — Reglas determinísticas:**

Cada uno de los 6 escenarios canónicos
(`s_dispute_prolongada`, `s_nulidad_parcial`, `s_segunda_vuelta`,
`s_crisis_institucional`, `s_reforma_legislativa`,
`s_proclamacion_sin_disputa`) se evalúa contra triggers definidos
sobre el corpus:

```
fraud_allegation_count_ge:    activador para s_dispute_prolongada
ballot_tampering_count_ge:    activador para s_nulidad_parcial
country=PER:                  contextual para s_segunda_vuelta
security_violence_count_ge:   activador para s_crisis_institucional
digital_count_ge:             activador para s_reforma_legislativa
low_disruption_complement:    activador para s_proclamacion_sin_disputa
```

Cada escenario activado parte de su `base_probability` documentada
en `backend/agents/elite_report/predictive/scenarios.py`.

**Etapa 2 — Refinement por Claude Sonnet 4.6:**

Recibe los escenarios candidatos + contexto país + corpus
sintetizado. Retorna probabilidades ajustadas y narrativa específica.

### 2.3 Validación

- **Banda de confianza** ±10pp por defecto (LLM puede ajustar si
  identifica alta varianza)
- **Suma de probabilidades** no garantizada como 1.0 — los escenarios
  no son mutuamente excluyentes (e.g. `s_segunda_vuelta` y
  `s_dispute_prolongada` pueden coocurrir)
- **Horizonte** 2-4 semanas; más allá la precisión cae

### 2.4 Limitaciones

- Los escenarios son específicos por país (PER tiene 6, otros países
  requieren extender el catálogo en `predictive/scenarios.py`)
- El refinement Claude introduce variabilidad entre corridas; la misma
  evidencia puede arrojar probabilidades ligeramente distintas (~±3pp)
  por temperatura del LLM (T=0.3)

---

## 3. Compliance Matrix Status (Cap 8 — Cumplimiento ICCPR/CADH)

### 3.1 Definición operacional

Por cada artículo del corpus normativo (ICCPR, CADH, CDI, CEDAW, etc.)
se asigna status `ok|partial|breach|unknown` basado en el conteo de
findings high/critical asociados al artículo via cross_reference.

### 3.2 Reglas de transición

```
breach   ⇐ high_findings ≥ 5
partial  ⇐ high_findings ≥ 1  OR  total_findings ≥ 3
ok       ⇐ total_findings >  0  AND  no high
unknown  ⇐ total_findings == 0
```

### 3.3 Inputs

`bundle.cross_references[]` — cada CrossReference asocia un
`finding_entry_id` con un `normative_instrument`. Construido por
CrossReferenceBuilder mediante mapeo curado de 14 categorías Hunter →
artículos normativos.

### 3.4 Limitación reconocida

El mapeo categoría → artículo es curated, no derivado del LLM. Esto
reduce flexibilidad pero aumenta reproducibilidad. Cualquier ajuste
del mapeo se versionado en `organizers/cross_reference.py`.

---

## 4. Radar PEIRS — 8 Dimensiones (Cap 10)

### 4.1 Definición operacional

Vector de 8 valores en `[0, 100]` representando la "salud" de cada
dimensión PEIRS de la integridad electoral.

### 4.2 Fórmula por dimensión

```
dim_value = max(0, min(100, round(100 - Σ_findings_in_categories sev_weight)))

donde:
  categories(suffrage)    = [voter_suppression]
  categories(legal)       = [legal, irregular_procedure]
  categories(emb)         = [logistics, fraud_allegation, counting]
  categories(media)       = [media, hate_speech, disinformation]
  categories(finance)     = [campaign_violation]
  categories(digital)     = [digital]
  categories(justice)     = [judicial]
  categories(inclusivity) = [voter_suppression, security]

sev_weight = {critical: 12, high: 6, medium: 2, low: 0.5, info: 0}
```

### 4.3 Interpretación

- **100**: dimensión sin hallazgos — estado óptimo aparente
- **50-100**: dimensión con anomalías documentadas pero no sistémicas
- **0-50**: dimensión con hallazgos críticos concentrados — vulnerabilidad

### 4.4 Limitación reconocida

La asignación categoría → dimensión es operacional. Una misma
finding puede afectar múltiples dimensiones (ej. `voter_suppression`
afecta `suffrage` E `inclusivity`). El doble-conteo es deliberado —
ambas dimensiones son legítimamente impactadas.

---

## 5. Datasets de Origen — Atribución y Validación

### 5.1 V-Dem v16

| Atributo | Valor |
|---|---|
| Cita formal | Coppedge et al. (2026). *V-Dem Country-Year Dataset v16*. Varieties of Democracy Project. <https://doi.org/10.23696/vdemds26> |
| Cobertura | 1789–2025, 202 países |
| Indicadores usados | 21 (incluye `v2x_polyarchy`, `v2elembaut`, `v2x_suffr`, `v2mebias`, `v2smgovdom`, `v2xcl_rol`) |
| Validación | Inter-coder reliability scores publicados anualmente por V-Dem |
| Licencia | Académica con atribución |

### 5.2 Freedom House FIW

| Atributo | Valor |
|---|---|
| Cita formal | Freedom House (2025). *Freedom in the World 2025*. <https://freedomhouse.org/report/freedom-world/2025> |
| Cobertura | 195 países + 15 territorios, 2013–2025 |
| Indicadores usados | PR (Political Rights, 0–40), CL (Civil Liberties, 0–60), Status (Free/Partly Free/Not Free) |
| Validación | Methodology pública con 25 sub-indicadores |
| Licencia | Open con atribución |

### 5.3 PEI 10.0 (Perceptions of Electoral Integrity)

| Atributo | Valor |
|---|---|
| Cita formal | Norris, P., et al. (2024). *Perceptions of Electoral Integrity Dataset (PEI-10.0)*. Harvard Dataverse. |
| Cobertura | 586 elecciones, 2012–2023 |
| Indicadores usados | OVERALLINTEGRITY, MEDIACOVERAGE, CAMPAIGNFINANCE, EMB |
| Validación | Expert survey con N≥40 expertos por elección |
| Licencia | Open con atribución |

### 5.4 RSF World Press Freedom Index

| Atributo | Valor |
|---|---|
| Cita formal | Reporters Without Borders (2025). *World Press Freedom Index 2025*. <https://rsf.org/en/index> |
| Cobertura | 180 países |
| Indicadores usados | Score global (0–100), ranking |
| Validación | Methodology pública con 5 sub-indicadores |
| Licencia | CC BY-NC 4.0 |

---

## 6. Reproducibilidad

### 6.1 Inmutabilidad por commit

Toda fórmula es código auditable en GitHub. Versionado por commit:

- Crisis Index: `backend/agents/elite_report/elite_report.py`,
  función `_attach_visualizations`, sección `early_warning_meter`
- Compliance Matrix: idem, sección `compliance_matrix`
- Radar PEIRS: idem, sección `radar_data` (G1 fix)
- Forecast: `backend/agents/elite_report/predictive/engine.py`

### 6.2 Cita formal de este documento

> DEMOCRAC.IA / PEIRS. (2026, mayo). *Índices Cuantitativos: Metodología
> v1.0*. <https://github.com/lachmanmariana8-sudo/democracia-peirs/blob/main/DOCS%20Proyect/PEIRS_Indices_Methodology_v1.0.md>

### 6.3 Versionado de la metodología

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 2026-05-10 | Versión inicial. Cubre: Crisis Index, Forecast, Compliance Matrix, Radar 8 dimensiones, datasets |

Cualquier cambio a fórmulas debe incrementar versión y registrarse aquí.

---

## 7. Limitaciones generales del PEIRS

1. **No reemplaza observación presencial**: PEIRS complementa, no
   sustituye, las misiones oficiales de observación electoral.
2. **No legitima resultados**: PEIRS emite inteligencia electoral con
   trazabilidad verificable, no valida ni invalida resultados.
3. **Cobertura sesgada**: Hunter monitorea fuentes RSS digitales;
   procesos en regiones sin cobertura digital quedan parcialmente
   representados.
4. **Dependencia LLM**: clasificación de severity y refinamiento de
   forecast dependen de Claude Sonnet 4.6. Variabilidad entre corridas
   ~±3pp para forecast, severity estable.
5. **Frecuencia de actualización**: Hunter scheduler corre cada 24h
   (configurable). Cambios entre ciclos no aparecen en informes
   generados antes del siguiente ciclo.

---

## 8. Contacto institucional

Para preguntas metodológicas, validación o partnerships:

- **Repositorio público**: <https://github.com/lachmanmariana8-sudo/democracia-peirs>
- **Documento institucional**: [PEIRS_Documento_Institucional_v2.0.md](PEIRS_Documento_Institucional_v2.0.md)
- **Roadmap técnico**: [PEIRS_Arquitectura_Roadmap.md](PEIRS_Arquitectura_Roadmap.md)

---

*DEMOCRAC.IA / PEIRS — Predictive Electoral Integrity & Risk System*
*Metodología de Índices v1.0 — Mayo 2026*
