# PEIRS Elite Report — Blueprint arquitectónico

**Versión del blueprint:** 1.1 — APROBADO para implementación
**Estado del blueprint:** Decisiones confirmadas por Mariana Lachman el 2026-04-20. Sprint 2 autorizado.
**Fecha del blueprint:** 2026-04-20
**Autora del proyecto:** Mariana Lachman · DemocracIA
**Referencias:** `REPORT_DESIGNER.md` (blueprint predecesor, Fases A-D ya implementadas), `INFORME_PERU_2026.md` (informe v1.1 manual ya entregado).

---

## ⓘ Implementation Status (2026-05-04)

> **Este documento es el blueprint arquitectónico que guió la implementación.**
> El producto descrito aquí está **operativo en producción al cierre del
> 4-may-2026 (v0.5.2)**. El blueprint se mantiene como referencia histórica
> de las decisiones de diseño.
>
> **Estado real al 2026-05-04:**
>
> | Item | Estado |
> | --- | --- |
> | 12 capítulos + 3 anexos generándose | OPERATIVO |
> | Pipeline 6 etapas (EliteLoader → ... → Renderer) | OPERATIVO |
> | Motor predictivo con 6 escenarios + early-warning | OPERATIVO |
> | 21 visualizaciones SVG server-side | OPERATIVO |
> | Citas APA 7 con `[URL]` activas | OPERATIVO |
> | i18n trilingüe (es / en / pt) — 180+ claves | OPERATIVO (4-may) |
> | Section titles 1.1-12.6 traducidos en/pt | OPERATIVO (4-may) |
> | Persistencia SQLite triple-tier | OPERATIVO (4-may) |
> | PDF browser-native via `/printable` | OPERATIVO (reemplazó xhtml2pdf) |
> | `/structured` endpoint para extracción dinámica | OPERATIVO |
> | Disclosure neutro (sin nombres de organismos) | OPERATIVO |
> | Sprint 1 — 9 tests integrados | OPERATIVO (91/91 total) |
> | Costo real por informe | $0.40-0.80 (dentro del límite $1.00 OK) |
>
> **Pendientes respecto al blueprint:**
>
> | Item | Estado | Resolución |
> | --- | --- | --- |
> | Traducir prompts cap_NN.md a en/pt | Pendiente | Sprint 4 (8-10h). Mientras tanto, `section_titles.py` cubre los headers como red de seguridad |
> | Country adapter pluggable | Pendiente | Sprint 2 (4-6h), bloqueador para Brasil/USA |
> | Modelo institucional generalizado (federal centr./descentr.) | Pendiente | Sprint 3 (6-8h) |
> | Brasil 2026 onboarding | Pendiente | Sprint 5 (10-12h, antes 4-oct-2026) |
> | USA 2026 midterms onboarding | Pendiente | Sprint 6 (12-16h, antes 3-nov-2026) |
>
> **Documentos hermanos vivos (estado actual):**
>
> - [STATUS_REPORT.md](STATUS_REPORT.md) — diagnóstico técnico
> - [DOCS Proyect/PEIRS_Documento_Institucional_v2.0.md](DOCS%20Proyect/PEIRS_Documento_Institucional_v2.0.md) — dossier para partners
> - [DOCS Proyect/PEIRS_Arquitectura_Roadmap.md](DOCS%20Proyect/PEIRS_Arquitectura_Roadmap.md) — roadmap técnico cronológico
> - [DOCS Proyect/INFORME_METODOLOGIA.md](DOCS%20Proyect/INFORME_METODOLOGIA.md) — playbook reproducible

## Decisiones confirmadas (2026-04-20)

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | 12 capítulos correctos | ✅ OK |
| 2 | Triángulo de evidencia como principio rector | ✅ OK |
| 3 | Motor predictivo obligatorio en preliminary/final | ✅ OK |
| 4 | Clasificación por defecto `public` | ✅ OK |
| 5 | Firma del jefe de misión | ❌ NO — sin firma en portada |
| 6 | Tab "Informe PEIRS" reemplaza o coexiste | ✅ reemplaza (mantiene ReportViewer como "vista técnica" alterna) |
| 7 | Alcance Elite | 🇵🇪 **Solo Perú por ahora** (arquitectura genérica, contenido específico PER) |
| 8 | Costo máximo $1.00 | ✅ OK |

---

## Índice del blueprint

1. [Visión y propósito](#1-visión-y-propósito)
2. [Público objetivo y casos de uso](#2-público-objetivo-y-casos-de-uso)
3. [Diferenciadores con el estado actual](#3-diferenciadores-con-el-estado-actual)
4. [Arquitectura general](#4-arquitectura-general)
5. [Estructura del informe — 12 capítulos + 3 anexos](#5-estructura-del-informe)
6. [Modelo de datos (Pydantic)](#6-modelo-de-datos)
7. [Pipeline de composición](#7-pipeline-de-composición)
8. [Sistema de citas y trazabilidad](#8-sistema-de-citas-y-trazabilidad)
9. [Motor predictivo](#9-motor-predictivo)
10. [Sistema de visualizaciones](#10-sistema-de-visualizaciones)
11. [Renderizado HTML + PDF](#11-renderizado-html--pdf)
12. [Integración con el dashboard](#12-integración-con-el-dashboard)
13. [Roadmap de implementación — 6 sprints](#13-roadmap-de-implementación)
14. [Criterios de calidad y aceptación](#14-criterios-de-calidad-y-aceptación)
15. [Referencias: informes modelo del sector](#15-referencias)

---

## 1. Visión y propósito

**PEIRS Elite Report** es el producto de máxima calidad del sistema DemocracIA:
un informe de observación electoral de **nivel institucional internacional** que
articule de manera coherente los tres tipos de evidencia disponibles
(antecedentes estructurales, observación empírica en tiempo real, marco
normativo) y los proyecte en análisis predictivo sobre el ciclo electoral en
curso.

**El objetivo declarado es un producto comparable en calidad editorial y rigor
metodológico a los informes de:**

- Misiones OEA/DECO
- EU EOM (European Union Election Observation Missions)
- Carter Center
- IDEA Internacional
- OSCE/ODIHR

Mientras que esos organismos producen informes en 30-60 días con equipos de
observadores presenciales, PEIRS Elite Report **genera el documento en minutos
con evidencia primaria verificable y trazabilidad completa**, sin reemplazar la
observación presencial sino complementándola con inteligencia basada en datos.

### Principio rector

> *Un observador internacional experto debe poder leer el informe y concluir
> "este es el tipo de trabajo que produciría una misión oficial".*

---

## 2. Público objetivo y casos de uso

### Lectores primarios

1. **Jefaturas de misión de observación electoral** — OEA, EU EOM, NDI, IRI.
2. **Autoridades electorales** — tribunal electoral, órgano administrativo.
3. **Academia jurídica** — profesores de derecho constitucional y electoral.
4. **Prensa internacional especializada** — corresponsales de Reuters, AFP, AP
   asignados a cobertura electoral.
5. **Organismos internacionales** — Relatoría Especial de la OEA para
   Libertad de Expresión, CIDH, Comité DDHH ONU.

### Casos de uso

| Caso | Uso específico |
|---|---|
| Informe pre-electoral | 15 días antes de la jornada — diagnóstico de riesgos |
| Informe de jornada | 48h post-jornada — primer análisis |
| Informe preliminar | 7-10 días post-jornada — documento público de misión |
| Informe final | 60-90 días post-proceso — cierre académico |
| Actualización por crisis | Ad-hoc cuando eventos críticos lo requieran |

### Formatos de entrega

- **PDF institucional A4** (principal) — para distribución oficial
- **HTML navegable** — para sitio web DemocracIA
- **Markdown** — para archivado, versionado, conversión
- **DOCX** (opcional futuro) — para colaboración con contrapartes

---

## 3. Diferenciadores con el estado actual

El tab "Informe PEIRS" actual tiene 11 capítulos generados por el pipeline
LangGraph (auditor + architect agents) **aislados entre sí**: cada capítulo es
texto generado independientemente, sin cruzar evidencia, sin visualizaciones
propias, sin análisis predictivo.

### Los 5 diferenciadores que convierten el informe en "Elite"

#### 3.1. Triángulo de evidencia en cada capítulo temático

Cada sección sustantiva articula tres vértices de evidencia:

```
                [Antecedente estructural]
                          /\
                         /  \
                        /    \
                       /      \
                      / CRUCE  \
                     /          \
                    /            \
                   /              \
                  /________________\
    [Observación empírica]      [Marco normativo]
     (Hunter findings)          (Constitución + LOE
                                 + jurisprudencia
                                 + RAG)
```

- **Vértice 1 — Antecedente estructural:** series históricas V-Dem, FH, PEI, RSF
  de 10+ años con interpretación de tendencia.
- **Vértice 2 — Observación empírica:** hallazgos del Hunter priorizados
  (severidad × recencia × credibilidad), con URL, medio y fecha de cada cita.
- **Vértice 3 — Marco normativo:** artículos de Constitución, LOE, LOP,
  resoluciones JNE relevantes, estándares ICCPR/CADH/CDI. Extraído del corpus
  RAG constitucionalista.

#### 3.2. Coherencia temporal explícita

El informe muestra la **evolución por fases del ciclo electoral** sin
ambigüedad. Las 9 fases ya presentes en el sistema PEIRS:

1. `preparatory` — Preparatorio
2. `pre_campaign` — Pre-campaña
3. `campaign` — Campaña electoral
4. `electoral_silence` — Veda/silencio electoral
5. `election_day` — Jornada electoral
6. `counting_tabulation` — Escrutinio y cómputo
7. `post_election` — Post-electoral
8. `dispute_resolution` — Resolución de disputas
9. `completed` — Ciclo completo

Cada capítulo temático muestra su evolución por fase con visualización
dedicada (`phase_timeline`).

#### 3.3. Análisis predictivo

El motor predictivo combina:

- **Patrones detectados** por el Hunter (ej: aceleración de fraud_allegation)
- **Antecedentes históricos** del país y de países comparables (V-Dem)
- **Marco normativo** aplicable (umbrales legales: quórum, plazos, mayorías)

Para producir **3-5 escenarios probabilísticos** con bandas de confianza:

| Escenario | Probabilidad | Indicadores | Implicaciones |
|---|---|---|---|
| Proclamación sin disputa mayor | 35% | Hunter: 10 critical, JNE res. ... | Consolidación institucional |
| Disputa prolongada post-escrutinio | 45% | Patrón de fraud_allegation, 9 entries ... | Riesgo de captura judicial |
| Nulidad parcial por el JNE | 15% | LOE Art. 184 requisitos + ... | Crisis institucional aguda |
| Segunda vuelta con impugnaciones | 55% (condicional) | ... | Complejidad operativa adicional |

#### 3.4. Citas académicas formales (APA 7)

Cada afirmación sustantiva se referencia según **APA 7th edition**:

```
El 63.300 ciudadanos de Lima Sur no pudieron sufragar por falta de material
electoral en 15 centros de votación (El Comercio, 2026, 13 de abril).
```

Con bibliografía completa en Anexo B, ordenada por autor/organización.

#### 3.5. Diseño visual institucional

- **Tipografía:** Fraunces (serif editorial) para titulares, DM Sans (sans
  institucional) para texto, DM Mono para cifras y código.
- **Paleta:** verde petróleo institucional (`#00796b`), azul profundo (`#0a0e17`),
  acentos puntuales de severidad (rojo, naranja, amarillo, verde, azul).
- **Visualizaciones:** SVG server-side con estándar estético OEA-inspired.
- **Layout A4:** márgenes 2.2/2/2.5cm, interlineado 1.45, cuerpo 10pt.
- **Paginación:** TOC con paginación automática, saltos de página por capítulo.
- **Branding sutil:** logo DemocracIA en encabezado, footer con página y fecha.

---

## 4. Arquitectura general

### 4.1. Diagrama de flujo

```
┌───────────────────────────────────────────────────────────────────┐
│                    POST /api/report/elite/generate                 │
│                    body: EliteReportRequest                        │
└────────────────────────────────┬──────────────────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────┐
│                         PEIRSEliteReport                           │
│                        (orquestador)                               │
└────────────────────────────────┬──────────────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
   ┌────────────┐        ┌────────────┐         ┌────────────┐
   │ EliteLoader│        │  RAGLoader │         │ DatasetsLdr│
   │  (Hunter   │        │ (corpus    │         │ (V-Dem,FH, │
   │   + alerts)│        │  constit.) │         │  PEI, RSF) │
   └─────┬──────┘        └─────┬──────┘         └─────┬──────┘
         └──────────────────────┴──────────────────────┘
                                │
                                ▼
                      ┌───────────────────┐
                      │  PhaseOrganizer   │
                      │  Agrupa evidencia │
                      │  por 9 fases del  │
                      │  ciclo electoral  │
                      └──────────┬────────┘
                                 │
                                 ▼
                      ┌───────────────────┐
                      │  CrossReference   │
                      │  Linkea hallazgos │
                      │  con artículos    │
                      │  LOE/Const/Jurisp │
                      └──────────┬────────┘
                                 │
                                 ▼
                      ┌───────────────────┐
                      │ PredictiveEngine  │
                      │ Genera 3-5 escen. │
                      │ probabilísticos   │
                      └──────────┬────────┘
                                 │
                                 ▼
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
   ┌────────────┐        ┌────────────┐         ┌────────────┐
   │ChapterComp-│        │ Visualizer │         │ Citations  │
   │oser (x12)  │        │ Elite SVG  │         │ Builder APA│
   │con Claude  │        │ (12 tipos) │         │            │
   └─────┬──────┘        └─────┬──────┘         └─────┬──────┘
         └──────────────────────┴──────────────────────┘
                                │
                                ▼
                      ┌───────────────────┐
                      │  EliteRenderer    │
                      │  HTML + PDF con   │
                      │  tipografía elite │
                      └──────────┬────────┘
                                 │
                                 ▼
                      ┌───────────────────┐
                      │   EliteReport     │
                      │   persistence +   │
                      │   download URLs   │
                      └───────────────────┘
```

### 4.2. Módulos (estructura de archivos)

```
backend/
└── agents/
    └── elite_report/
        ├── __init__.py
        ├── elite_report.py          # orquestador principal PEIRSEliteReport
        ├── models.py                # Pydantic schemas
        ├── loaders/
        │   ├── __init__.py
        │   ├── hunter_loader.py     # entries + alerts
        │   ├── rag_loader.py        # corpus constitucionalista
        │   └── datasets_loader.py   # V-Dem, FH, PEI, RSF
        ├── organizers/
        │   ├── __init__.py
        │   ├── phase_organizer.py   # agrupa por 9 fases
        │   └── cross_reference.py   # linkea hallazgos ↔ normativa
        ├── predictive/
        │   ├── __init__.py
        │   ├── engine.py            # PredictiveEngine
        │   └── scenarios.py         # templates de escenarios
        ├── composer/
        │   ├── __init__.py
        │   ├── chapter_composer.py  # ChapterComposer con Claude
        │   ├── prompts/
        │   │   ├── base_context.md  # contexto compartido (prompt cache)
        │   │   ├── cap_01_contexto.md
        │   │   ├── cap_02_marco_juridico.md
        │   │   ├── cap_03_sistema_electoral.md
        │   │   ├── cap_04_pre_electoral.md
        │   │   ├── cap_05_jornada.md
        │   │   ├── cap_06_escrutinio.md
        │   │   ├── cap_07_post_electoral.md
        │   │   ├── cap_08_derechos.md
        │   │   ├── cap_09_predictivo.md
        │   │   ├── cap_10_conclusiones.md
        │   │   ├── cap_11_recomendaciones.md
        │   │   └── cap_12_ia_regulacion.md
        │   └── citation_builder.py  # APA 7 formatter
        ├── visualizer/
        │   ├── __init__.py
        │   ├── renderer.py          # dispatcher
        │   ├── timeseries.py        # serie V-Dem
        │   ├── phase_timeline.py    # 9 fases × hallazgos
        │   ├── map_regions.py       # mapa mesas afectadas
        │   ├── network.py           # red de actores institucionales
        │   ├── heatmap.py           # derechos × hallazgos
        │   ├── forecast.py          # predicción con bandas
        │   ├── semaphore.py         # semáforo institucional
        │   └── matrix.py            # matriz normativa
        └── renderer/
            ├── __init__.py
            ├── html_renderer.py     # genera HTML completo
            ├── pdf_renderer.py      # weasyprint o fallback
            ├── templates/
            │   ├── elite_report.html
            │   └── elite_report.css
            └── assets/
                ├── logo_democracia.svg
                ├── fonts.css
                └── paper_texture.svg

reports/
└── elite/
    └── <report_id>/
        ├── metadata.json
        ├── report.md
        ├── report.html
        └── report.pdf
```

---

## 5. Estructura del informe

**12 capítulos + 3 anexos. Estructura fija garantizada por template.**

### 5.1. Portada (sin número)

**Contenido:**

- Escudo institucional DemocracIA + logo país
- Título: "Misión de Observación Electoral · [País] · Elecciones [Año]"
- Subtítulo: "Informe [Preliminar / De Jornada / Final]"
- Metadata: versión, período cubierto, fecha de cierre
- Línea institucional: "DemocracIA / PEIRS (Predictive Electoral Integrity and
  Risk System)"
- Firma de la jefatura de misión (texto o imagen)
- Número de registro del informe
- Clasificación de circulación (público / restringido / confidencial)

**Visualización:** bloque editorial SVG de portada.

### 5.2. Tabla de contenidos

Auto-generada. Links internos a cada capítulo. Muestra número de página en PDF.

### 5.3. Declaración preliminar (1 página)

**Contenido:**

- **2-3 párrafos de narrativa ejecutiva**
- **Infografía horizontal** con 6 KPIs clave
- **Frase de juicio global** destacada en caja lateral

**Visualizaciones:**

- `infographic_horizontal`: 6 KPIs en una fila
- `semaphore_mini`: semáforo institucional global

### 5.4. Capítulo 1 — Contexto histórico

**Objetivo:** situar la elección en su trayectoria de 10+ años.

**Contenido:**

- Timeline de eventos institucionales críticos (6 presidentes en 4 años, etc.)
- Series históricas V-Dem (Liberal Democracy Index 2015-2025)
- Freedom House 10 años con gradiente
- Cambios de régimen documentados
- Episodios de violencia política relevante

**Evidencia:** datasets + hechos históricos del corpus RAG.

**Visualizaciones:**

- `timeseries_multi`: V-Dem + FH + PEI superpuestos (líneas)
- `events_timeline`: marcadores de eventos críticos

**Citas esperadas:** V-Dem Institute (2025). *Liberal Democracy Index, V-Dem
v15*. Freedom House (2025). *Freedom in the World 2025*. IDEA Internacional
(2023). *State of Democracy in the Americas*.

### 5.5. Capítulo 2 — Marco jurídico

**Objetivo:** mapa normativo exhaustivo aplicable al proceso.

**Contenido:**

- Constitución — artículos electorales (Art. 2, 31, 35, 176-187)
- Ley Orgánica de Elecciones N° 26859 — secciones relevantes
- Ley de Organizaciones Políticas N° 28094 — paridad, financiamiento,
  democracia interna
- Jurisprudencia JNE relevante del ciclo actual
- Marco internacional — ICCPR Art. 25, CADH Art. 23, CDI Art. 3-4
- Estándares OSCE/ODIHR, OEA/DECO aplicables

**Evidencia:** 100% corpus RAG constitucionalista peruano (ya implementado).

**Visualizaciones:**

- `matrix_normativa`: matriz 3D (artículo × tema × jerarquía)

**Citas esperadas:** Constitución Política del Perú. (1993). Ley Orgánica de
Elecciones N° 26859. (1997). Res. JNE 0891-2025-JNE. (15 de agosto de 2025).

### 5.6. Capítulo 3 — Sistema electoral

**Objetivo:** descripción del diseño institucional.

**Contenido:**

- Sistema tripartito JNE / ONPE / RENIEC (Art. 177 Const.)
- Competencias por organismo
- Procedimientos electorales (campaña, jornada, escrutinio)
- Tecnología electoral implementada en el ciclo (STAE, SCE, SPR)
- Cadena de custodia del voto
- Marco regulatorio de IA en el proceso electoral (vacío actual)

**Evidencia:** corpus RAG + Hunter findings tema `tecnologia_electoral_ia`.

**Visualizaciones:**

- `network_institutions`: diagrama SVG de relaciones JNE/ONPE/RENIEC
- `flow_chart_voting`: cadena del voto desde padrón hasta proclamación

### 5.7. Capítulo 4 — Fase pre-electoral

**Objetivo:** análisis de preparatorio + pre-campaña + campaña + silencio.

**Contenido:**

- Distribución temporal de hallazgos Hunter en estas 4 fases
- Ecosistema de desinformación (fact-checks IDL-Reporteros)
- Incidentes en campaña (violencia, acoso, financiamiento irregular)
- Observancia del silencio electoral
- Restricciones a medios documentadas

**Evidencia:** Hunter findings filtrados por phase ∈ {preparatory, pre_campaign,
campaign, electoral_silence}.

**Visualizaciones:**

- `phase_timeline`: densidad de hallazgos por día en estas 4 fases
- `donut_categories`: distribución por categoría

### 5.8. Capítulo 5 — Jornada electoral

**Objetivo:** reconstrucción hora por hora de la jornada.

**Contenido:**

- Cronología de incidentes (hora × evento)
- Mesas afectadas geográficamente
- Ampliaciones de horario, intervenciones institucionales
- Tecnología electoral en operación (éxitos y fallas de STAE)
- Transparencia (observadores internacionales, suspensiones)
- Cifras de exclusión del sufragio documentadas

**Evidencia:** Hunter findings phase = `election_day` + datos oficiales ONPE.

**Visualizaciones:**

- `hourly_timeline`: eventos 08:00-18:00 del día
- `map_regions_affected`: mapa SVG con intensidad por región

### 5.9. Capítulo 6 — Escrutinio y cómputo

**Objetivo:** seguimiento del conteo oficial.

**Contenido:**

- Ritmo de actas procesadas en 24/48/72h
- Actas observadas e impugnadas
- Incidentes de integridad (Trujillo fiscalizadora, Callao STAE)
- Sistema SCE y validación IA-operador
- Transparencia del proceso (portal público, auditorías)

**Evidencia:** Hunter findings phase = `counting_tabulation` + datos SCE.

**Visualizaciones:**

- `progress_chart`: % actas procesadas en el tiempo
- `integrity_incidents_grid`: grilla de incidentes por región

### 5.10. Capítulo 7 — Post-electoral

**Objetivo:** análisis del período post-jornada.

**Contenido:**

- Proclamación o demora en proclamación
- Denuncias penales contra autoridades electorales
- Narrativas de fraude y sus patrones
- Reacción de partidos perdedores
- Rol de gremios, sociedad civil, prensa internacional
- Segunda vuelta (si aplica): perspectivas

**Evidencia:** Hunter phase = `post_election` + acciones institucionales.

**Visualizaciones:**

- `actor_network`: red de actores involucrados (JNE, ONPE, Fiscalía, partidos)
- `judicial_timeline`: cronología de acciones judiciales

### 5.11. Capítulo 8 — Derechos vulnerados

**Objetivo:** matriz de violaciones cruzada con instrumentos internacionales.

**Contenido:**

- Enumeración de derechos invocados (ICCPR 25, CADH 23, CADH 13, etc.)
- Cuantificación: cuántos hallazgos invocan cada derecho
- Análisis de cumplimiento del Estado con obligaciones ICCPR/CADH
- Recomendaciones a mecanismos internacionales (Relatorías, CIDH)

**Evidencia:** Hunter findings con `rights_at_risk` + jurisprudencia Corte IDH.

**Visualizaciones:**

- `heatmap_rights`: heatmap derechos × categoría
- `compliance_matrix`: matriz de cumplimiento por artículo

### 5.12. Capítulo 9 — Análisis predictivo

**Objetivo:** proyección de escenarios probabilísticos para próximas fases.

**Contenido:**

- 3-5 escenarios con probabilidad estimada
- Indicadores que alimentan cada escenario
- Implicaciones institucionales de cada escenario
- Umbrales de alerta temprana a monitorear
- Comparación con elecciones históricas del país y de países comparables

**Evidencia:** PredictiveEngine sobre patrones Hunter + datasets + RAG.

**Visualizaciones:**

- `forecast_chart`: proyección con bandas de confianza
- `scenario_probability`: barras horizontales con % de cada escenario

### 5.13. Capítulo 10 — Conclusiones

**Objetivo:** juicio global sobre la integridad electoral.

**Contenido:**

- Síntesis del proceso en 5-7 hallazgos
- Evaluación de legitimidad (¿el proceso fue libre, justo, auténtico?)
- Calificación por las 8 dimensiones PEIRS
- Comparación con los compromisos internacionales del país
- Semáforo institucional final

**Evidencia:** agregación de los 9 capítulos previos.

**Visualizaciones:**

- `semaphore_institutional`: semáforo con los 3 organismos + proceso global
- `dimensions_radar`: radar 8 dimensiones PEIRS

### 5.14. Capítulo 11 — Recomendaciones

**Objetivo:** matriz accionable para decisores.

**Contenido:**

- Tabla estructurada: corto/mediano/largo plazo × órgano responsable
- Cada recomendación está anclada en un hallazgo específico del informe
- Prioridad (alta/media/baja) y estado de implementación (pendiente/en curso)

**Visualizaciones:**

- `matrix_recommendations`: matriz 3×N con priority flags

### 5.15. Capítulo 12 — IA en el proceso electoral

**Objetivo:** caso de estudio específico (característico del 2026 peruano).

**Contenido:**

- Arquitectura STAE/SCE/SPR
- Ausencia de auditoría pública del componente IA
- Comparación con VENP rechazado por Res. JNE 0891-2025
- Implicaciones regulatorias (7 puntos del informe v1.1)
- Recomendación de Ley de IA electoral

**Evidencia:** sección 7 del INFORME_PERU_2026.md + corpus RAG.

**Visualizaciones:**

- `system_architecture`: diagrama STAE + SCE + SPR con flujo de datos

### 5.16. Anexos

#### Anexo A — Metodología técnica

- Pipeline PEIRS completo
- Hunter: fuentes, frecuencia, clasificación
- Estadística del Structurer (dedupe, temas, priorización)
- Parámetros del PredictiveEngine
- Limitaciones reconocidas

#### Anexo B — Bibliografía y fuentes

- **Subsección B.1:** Instrumentos internacionales (ICCPR, CADH, CDI, OSCE)
- **Subsección B.2:** Normativa nacional (Constitución, LOE, LOP, leyes)
- **Subsección B.3:** Jurisprudencia (JNE, Corte IDH, Tribunal Constitucional)
- **Subsección B.4:** Datasets (V-Dem, FH, PEI, RSF) con citas APA
- **Subsección B.5:** Fuentes periodísticas (todas las URLs citadas ordenadas
  por medio)
- **Subsección B.6:** Literatura académica (IDEA, Carter, EU EOM metodologías)

**Formato:** APA 7 estricto.

#### Anexo C — Listado de hallazgos

Tabla completa de **todos los hallazgos del Hunter** con:

- entry_id
- fecha
- severidad
- categoría
- tema canónico asignado
- finding (texto completo)
- medio + URL
- priority_score

Ordenados por priority_score descendente. Navegable desde citas del informe.

---

## 6. Modelo de datos

```python
# backend/agents/elite_report/models.py
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


Audience = Literal["institutional", "executive", "press", "international"]
Language = Literal["es", "en"]
ReportClassification = Literal["public", "restricted", "confidential"]


class MissionMetadata(BaseModel):
    """Metadatos de la misión de observación."""
    mission_name: str = "DemocracIA — Observación Electoral PEIRS"
    lead_observer: str = "Mariana Lachman"
    organization: str = "DemocracIA"
    report_number: str           # ej. "DMC-PER-2026-001"
    classification: ReportClassification = "public"
    period_start: str            # ISO date
    period_end: str              # ISO date
    jornada_date: str            # fecha de la elección
    signed_off: bool = False


class EliteReportRequest(BaseModel):
    """Request para generar informe Elite."""
    country_code: str
    mission_metadata: MissionMetadata
    audience: Audience = "institutional"
    language: Language = "es"
    report_type: Literal["pre_electoral", "jornada", "preliminary",
                          "final", "ad_hoc"] = "preliminary"
    # Control fino:
    include_chapters: Optional[List[int]] = None     # [1, 5, 9, 11] para subset
    include_predictive: bool = True
    include_appendix_c: bool = True                   # lista completa de hallazgos
    forecast_horizon_days: int = 14
    use_llm: bool = True                              # Fase C siempre en Elite
    output_formats: List[Literal["md", "html", "pdf"]] = ["md", "html", "pdf"]


class PhaseEvidence(BaseModel):
    """Evidencia agrupada por fase electoral."""
    phase_id: str
    phase_label: str
    findings: List["FindingRef"] = Field(default_factory=list)
    total_count: int = 0
    high_critical_count: int = 0
    dominant_themes: List[str] = Field(default_factory=list)


class CrossReference(BaseModel):
    """Link entre un hallazgo del Hunter y un artículo del corpus normativo."""
    finding_entry_id: str
    finding_snippet: str
    normative_instrument: str    # ej. "Constitución Perú Art. 178"
    relevance: Literal["direct", "related", "contextual"]
    reasoning: str                # 1-2 frases explicando el link


class HistoricalDatapoint(BaseModel):
    """Un punto de una serie histórica (V-Dem, FH, PEI)."""
    year: int
    value: float
    source: str                   # "V-Dem v15", "Freedom House 2025", etc.
    note: Optional[str] = None    # evento histórico asociado si aplica


class HistoricalSeries(BaseModel):
    """Serie histórica completa de un indicador."""
    indicator: str                # "vdem_libdem", "fh_total", "pei_embs"
    source: str
    datapoints: List[HistoricalDatapoint]
    trend_direction: Literal["up", "down", "stable", "volatile"]
    trend_note: str


class ForecastScenario(BaseModel):
    """Un escenario predictivo."""
    scenario_id: str
    label: str                    # "Proclamación sin disputa mayor"
    probability: float            # 0-1
    confidence_interval: Optional[tuple[float, float]] = None
    indicators: List[str]         # patrones que lo sustentan
    implications: str             # 2-3 oraciones
    watch_signals: List[str]      # indicadores a monitorear


class ForecastPayload(BaseModel):
    """Resultado completo del PredictiveEngine."""
    horizon_days: int
    generated_at: str
    scenarios: List[ForecastScenario]
    dominant_pattern: str
    early_warning_level: Literal["green", "amber", "orange", "red"]
    early_warning_note: str


class CitationEntry(BaseModel):
    """Entry de bibliografía en formato APA."""
    citation_id: str
    type: Literal["book", "article", "web", "legal", "case_law", "dataset",
                  "report", "treaty"]
    apa_formatted: str            # la cita completa en APA 7
    short_form: str               # "(El Comercio, 2026)"
    url: Optional[str] = None
    accessed_date: Optional[str] = None


class EliteChapter(BaseModel):
    """Un capítulo del informe Elite."""
    number: int                   # 1-12; 0 para portada; -1 para TOC
    title: str
    subtitle: Optional[str] = None
    narrative: str                # markdown con citas APA
    findings: List["FindingRef"] = Field(default_factory=list)
    cross_references: List[CrossReference] = Field(default_factory=list)
    visualizations: List["VizSpec"] = Field(default_factory=list)
    citations_used: List[str] = Field(default_factory=list)  # citation_ids
    historical_series: List[HistoricalSeries] = Field(default_factory=list)
    phase_evidence: Optional[PhaseEvidence] = None
    word_count: int = 0
    warnings: List[str] = Field(default_factory=list)


class EliteReportOutput(BaseModel):
    """Resultado completo del informe Elite."""
    report_id: str
    country_code: str
    mission: MissionMetadata
    audience: Audience
    language: Language
    report_type: str
    generated_at: str
    status: Literal["generating", "done", "failed"] = "done"
    # Contenido
    chapters: List[EliteChapter]
    forecast: Optional[ForecastPayload] = None
    citations: List[CitationEntry] = Field(default_factory=list)
    all_findings: List["FindingRef"] = Field(default_factory=list)  # Anexo C
    # Outputs renderizados
    markdown: Optional[str] = None
    html: Optional[str] = None
    pdf_path: Optional[str] = None
    # Metadata
    stats: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    tokens_used: Dict[str, int] = Field(default_factory=dict)
    generation_time_seconds: float = 0.0
```

Los modelos `FindingRef` y `VizSpec` reutilizan los del `ReportDesigner`
existente.

---

## 7. Pipeline de composición

### 7.1. Orquestador principal

```python
class PEIRSEliteReport:
    async def compose(self, req: EliteReportRequest) -> EliteReportOutput:
        # 0. Inicialización
        report_id = str(uuid.uuid4())[:12]
        start_time = time.time()

        # 1. Carga de datos (paralelo)
        hunter_data, rag_corpus, datasets = await asyncio.gather(
            self.hunter_loader.load(req.country_code, req.period_start, req.period_end),
            self.rag_loader.load(req.country_code),
            self.datasets_loader.load(req.country_code, years=10),
        )

        # 2. Organización por fases
        phase_evidence = self.phase_organizer.organize(hunter_data)

        # 3. Cross-referencing
        cross_refs = self.cross_reference.link_findings_to_norms(
            hunter_data, rag_corpus
        )

        # 4. Motor predictivo
        forecast = None
        if req.include_predictive:
            forecast = await self.predictive_engine.forecast(
                hunter_data, datasets, rag_corpus, horizon=req.forecast_horizon_days
            )

        # 5. Composición de capítulos (12 con concurrency 4)
        chapters = await self.chapter_composer.compose_all(
            req=req,
            hunter_data=hunter_data,
            rag_corpus=rag_corpus,
            datasets=datasets,
            phase_evidence=phase_evidence,
            cross_refs=cross_refs,
            forecast=forecast,
        )

        # 6. Citas APA
        citations = self.citation_builder.build_bibliography(
            chapters, hunter_data, datasets, rag_corpus
        )

        # 7. Renderizado
        output = EliteReportOutput(
            report_id=report_id,
            country_code=req.country_code,
            mission=req.mission_metadata,
            audience=req.audience,
            language=req.language,
            report_type=req.report_type,
            generated_at=datetime.now(timezone.utc).isoformat(),
            chapters=chapters,
            forecast=forecast,
            citations=citations,
            all_findings=hunter_data.all_prioritized_findings,
        )
        output.markdown = self.html_renderer.render_markdown(output)
        output.html = self.html_renderer.render_html(output)
        if "pdf" in req.output_formats:
            output.pdf_path = await self.pdf_renderer.render_pdf(output)

        # 8. Persistencia
        self._persist(output)
        output.generation_time_seconds = time.time() - start_time
        return output
```

### 7.2. ChapterComposer con Claude

Cada capítulo se genera con un prompt especializado. El contexto compartido
(base_context.md) se envía con **prompt caching de Anthropic**: pagás la
construcción una vez, reusás en 12 llamadas.

**Estructura del system prompt compartido** (cached):

```
Sos un/a redactor/a de informes de observación electoral de nivel
institucional internacional comparable a misiones de la OEA, EU EOM,
Carter Center, IDEA Internacional y OSCE/ODIHR.

El informe que estás redactando tiene el siguiente contexto:

PAÍS: {country_code} — {country_name}
MISIÓN: {mission_name} · Jefatura: {lead_observer}
PERÍODO: {period_start} a {period_end}
TIPO DE INFORME: {report_type}
AUDIENCIA: {audience} ({audience_description})
IDIOMA: {language}

DATOS DISPONIBLES (compartidos con todos los capítulos):

ESTADÍSTICAS:
- Total de hallazgos procesados: {total_findings}
- Distribución severidad: {sev_dist}
- Días cubiertos: {days_covered}
- Fuentes activas: {sources_list}

TEMAS DOMINANTES (por densidad high/critical):
{theme_ranking_top_8}

HALLAZGOS PRIORITARIOS GLOBALES (top 20):
{top_findings_with_urls}

CORPUS NORMATIVO (extractos del RAG constitucionalista):
{rag_extracts_top_10}

DATASETS (series históricas 2016-2025):
{vdem_series}
{fh_series}
{pei_series}
{rsf_series}

MARCO PREDICTIVO (si disponible):
{forecast_scenarios}

REGLAS DE REDACCIÓN ESTRICTAS:
- NO inventes cifras, artículos o resoluciones.
- Cada afirmación sustantiva debe cerrar con una cita en formato APA 7
  abreviado entre paréntesis: (Autor/Institución, Año) o (Medio, Año,
  Fecha).
- Para artículos de ley: "Art. N de [nombre ley]".
- Para resoluciones judiciales: número completo "Res. JNE 0891-2025-JNE".
- Links a medios como markdown: [frase contextual](URL).
- Tono académico formal pero legible. Frases medianas (15-25 palabras).
- NO usar frases cliché ("es importante notar", "cabe señalar").
- Citas textuales breves van entre "comillas" con fuente al final.
- Balanceo: si hay controversia, presentá ambas posiciones con fuentes.
- Declará limitaciones o zonas grises explícitamente.
- {language_rule}

FORMATO DE SALIDA:
Markdown. Sin título de nivel 1 (ya se renderiza automáticamente).
Subsecciones con ## si el capítulo lo requiere. Listas con guiones.
Énfasis con **negritas**. Citas textuales con > bloque.
```

**Prompts específicos por capítulo** (archivo por capítulo en `prompts/`):

Cada uno incluye:

1. Objetivo del capítulo (1 párrafo)
2. Estructura esperada (secciones mínimas)
3. Hallazgos específicos relevantes (pasados al prompt)
4. Longitud objetivo (palabras)
5. Visualizaciones que acompañan (pies de gráfico)
6. Instrucciones específicas de tono/ángulo

### 7.3. Límites y controles

| Parámetro | Valor Elite |
|---|---|
| Concurrency | 4 capítulos en paralelo |
| Timeout por capítulo | 60s |
| Max words portada | 200 |
| Max words resumen ejecutivo | 500 |
| Max words capítulo temático | 800 |
| Max words conclusiones | 600 |
| Max words recomendaciones | 500 |
| Temperatura | 0.25 |
| Top_p | 0.9 |
| Reintentos por capítulo | 2 |
| Fallback si falla | plantilla B con evidencia real |

---

## 8. Sistema de citas y trazabilidad

### 8.1. Formato de cita in-line

Durante la redacción Claude genera citas con formato:

```
(El Comercio, 2026, 13 de abril)
(V-Dem Institute, 2025)
(Res. JNE 0891-2025-JNE)
(Constitución Política del Perú, 1993, Art. 178)
(ICCPR, Art. 25)
(CIDH, Medidas cautelares, 2023)
```

### 8.2. CitationBuilder

Módulo `citation_builder.py` que:

1. Recorre las narrativas de los 12 capítulos.
2. Extrae patrones de cita (regex sobre paréntesis con autor-año).
3. Matchea cada cita con el asset correspondiente:
   - Fuentes periodísticas → FindingRef con URL
   - Instrumentos legales → corpus RAG
   - Datasets → catálogo fijo (V-Dem v15, FH 2025, etc.)
   - Jurisprudencia → corpus RAG constitucionalista
4. Genera la entrada bibliográfica APA 7 completa.
5. Asigna un `citation_id` (C-001, C-002, ...) y sustituye la cita in-line por
   superíndice `¹` clicable al Anexo B.

### 8.3. Formato APA 7 por tipo

**Artículo periodístico:**

```
El Comercio. (2026, 13 de abril). Más de 52.000 personas se quedaron sin
votar: las consecuencias para los organismos electorales. *El Comercio*.
https://elcomercio.pe/politica/...
```

**Instrumento legal:**

```
Congreso de la República del Perú. (1997). *Ley Orgánica de Elecciones N°
26859*. Diario Oficial El Peruano, 30 de septiembre de 1997.
https://leyes.congreso.gob.pe/Documentos/Leyes/26859.pdf
```

**Resolución judicial:**

```
Jurado Nacional de Elecciones. (2025, 15 de agosto). *Resolución N°
0891-2025-JNE: Rechazo de propuesta de voto electrónico no presencial
para Elecciones Generales 2026* (Expediente N° JNE-2025-001). JNE.
```

**Dataset:**

```
V-Dem Institute. (2025). *Varieties of Democracy (V-Dem) Dataset v15*.
University of Gothenburg. https://v-dem.net/data/dataset-archive/
```

**Tratado internacional:**

```
Organización de las Naciones Unidas. (1966). *Pacto Internacional de
Derechos Civiles y Políticos*. Resolución 2200A (XXI) de la Asamblea
General, 16 de diciembre de 1966.
```

### 8.4. Trazabilidad verificable

Cada cita debe permitir al lector:

1. Abrir el link si es URL.
2. Ubicar el artículo en la ley si es instrumento legal.
3. Descargar el dataset si es académico.
4. Ver el hallazgo específico en Anexo C si es Hunter finding.

---

## 9. Motor predictivo

### 9.1. Principio metodológico

El motor predictivo NO hace pronósticos sobre resultados electorales (quién
gana). Eso es predicción política de encuesta, NO observación.

**Lo que SÍ predice:**

- Probabilidad de **disputas post-electorales** extensas.
- Probabilidad de **nulidad parcial o total** según umbrales LOE.
- Probabilidad de **segunda vuelta** (si aplica).
- Probabilidad de **crisis institucional** post-escrutinio.
- Probabilidad de **activación de mecanismos internacionales** (CIDH, OEA).
- Probabilidad de **reformas legislativas** post-proceso.

### 9.2. Inputs del PredictiveEngine

- **Patrones del Hunter** (aceleración, temas dominantes por fase)
- **Series históricas** V-Dem, FH, PEI (trayectoria institucional)
- **Jurisprudencia relevante** (RAG constitucionalista)
- **Umbrales legales** (Art. 184 LOE nulidad, Art. 380 segunda vuelta, etc.)
- **Comparables regionales** (elecciones de otros países en los últimos 3
  años con patrones similares)

### 9.3. Método

**Híbrido:** reglas deterministas + prompt de Claude con role analítico.

1. **Reglas deterministas** generan candidatos de escenario basados en:
   - Si `fraud_allegation > N` entries → escenario "disputa prolongada" ON
   - Si `votos_nulos + blancos > 2/3` → escenario "nulidad art. 184" ON
   - Si `sin_voto_docts > umbral_10pct_padrón` → escenario "impugnación masiva"
     ON
   - ...

2. **Prompt Claude** recibe candidatos + toda la evidencia disponible y:
   - Asigna probabilidad a cada escenario (con justificación)
   - Genera "watch signals" para monitoreo
   - Declara nivel de alerta temprana (verde/amber/naranja/rojo)

### 9.4. Output

```python
ForecastPayload(
    horizon_days=14,
    generated_at="2026-04-20T...",
    scenarios=[
        ForecastScenario(
            scenario_id="s1",
            label="Disputa post-electoral prolongada",
            probability=0.55,
            confidence_interval=(0.40, 0.70),
            indicators=[
                "14 entries fraud_allegation en las últimas 48h",
                "Narrativa de nulidad liderada por Renovación Popular",
                "Fiscal de la Nación pide medida cautelar contra ONPE",
            ],
            implications=(
                "Alto riesgo de impugnaciones masivas ante JEE. Posible "
                "retraso de proclamación. Tensión institucional sostenida."
            ),
            watch_signals=[
                "Número de impugnaciones ante JEE a 72h de proclamación",
                "Resoluciones JNE sobre pedidos de nulidad parcial",
                "Posicionamiento de observadores internacionales",
            ],
        ),
        # ... 3-5 escenarios más
    ],
    dominant_pattern="Escalamiento institucional con patrón de fraude narrativo",
    early_warning_level="orange",
    early_warning_note=(
        "Nivel naranja: alta probabilidad de crisis institucional en las "
        "próximas 2 semanas sin alteración del resultado electoral base."
    ),
)
```

### 9.5. Visualización

Capítulo 9 contiene:

- `forecast_chart`: línea temporal con probabilidad acumulada de cada escenario
- `scenario_probability`: barras horizontales con % y bandas de confianza
- `early_warning_meter`: medidor tipo velocímetro con el nivel actual

---

## 10. Sistema de visualizaciones

### 10.1. Extensión sobre Fase D existente

El `ReportDesigner` ya tiene 4 renderers (infographic_top, timeline,
bar_horizontal, donut). Elite Report agrega 8 nuevos:

| Kind | Uso | Donde aparece |
|---|---|---|
| `timeseries_multi` | Series históricas V-Dem + FH + PEI | Cap. 1 |
| `events_timeline` | Timeline de eventos críticos con marcadores | Cap. 1 |
| `matrix_normativa` | Matriz artículo × tema × jerarquía | Cap. 2 |
| `network_institutions` | Diagrama SVG de red institucional | Cap. 3, 7 |
| `flow_chart_voting` | Cadena del voto (padrón → proclamación) | Cap. 3 |
| `phase_timeline` | 9 fases × densidad de hallazgos | Cap. 4, múltiples |
| `hourly_timeline` | Eventos hora por hora | Cap. 5 |
| `map_regions_affected` | Mapa Perú con intensidad por región | Cap. 5 |
| `progress_chart` | Línea de % actas procesadas vs tiempo | Cap. 6 |
| `integrity_incidents_grid` | Grilla 2D de incidentes | Cap. 6 |
| `actor_network` | Red de actores con aristas (acciones) | Cap. 7 |
| `judicial_timeline` | Timeline de acciones judiciales | Cap. 7 |
| `heatmap_rights` | Heatmap derechos × categoría | Cap. 8 |
| `compliance_matrix` | Matriz de cumplimiento ICCPR/CADH | Cap. 8 |
| `forecast_chart` | Forecast con bandas de confianza | Cap. 9 |
| `scenario_probability` | Barras horizontales % escenarios | Cap. 9 |
| `early_warning_meter` | Velocímetro de alerta | Cap. 9 |
| `semaphore_institutional` | Semáforo JNE+ONPE+RENIEC+proceso | Cap. 10 |
| `dimensions_radar` | Radar 8 dimensiones PEIRS | Cap. 10 |
| `matrix_recommendations` | Matriz 3×N con priority flags | Cap. 11 |
| `system_architecture` | Diagrama STAE+SCE+SPR con flujo de datos | Cap. 12 |

### 10.2. Estándar visual común

- **Paleta base:** `#00796b` (teal institucional), `#004d40` (verde oscuro),
  `#263238` (texto), `#78909c` (texto muted), `#cbd5e1` (borders).
- **Paleta severidad:** `#d32f2f critical`, `#f97316 high`, `#fbc02d medium`,
  `#388e3c low`, `#1976d2 info`.
- **Tipografía SVG:** `DM Sans` para labels, `DM Mono` para cifras.
- **Tamaños estándar:**
  - Infografías portada: 640×200
  - Timelines: 640×260
  - Matrices: 640×400
  - Mapas: 560×560
  - Networks: 640×480
  - Radars: 400×400
- **Leyendas:** siempre abajo con guiones separadores.
- **Accesibilidad:** ARIA labels, contraste mínimo 4.5:1, patrones además de
  color para daltonismo.

### 10.3. Fallback

Si una visualización falla, se renderiza un bloque informativo con los datos
en tabla. No puede haber "cuadro vacío" en el informe.

---

## 11. Renderizado HTML + PDF

### 11.1. HTML

**Template:** `elite_report.html` — Jinja2 con placeholders para cada capítulo.

**Estructura:**

```html
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <link rel="stylesheet" href="fonts.css">
  <link rel="stylesheet" href="elite_report.css">
</head>
<body>
  <article class="elite-report">
    <section class="cover">...</section>
    <nav class="toc">...</nav>
    <section class="declaration">...</section>
    <section class="chapter" id="chapter-1">...</section>
    ...
    <section class="chapter" id="chapter-12">...</section>
    <aside class="appendix" id="appendix-a">...</aside>
    <aside class="appendix" id="appendix-b">...</aside>
    <aside class="appendix" id="appendix-c">...</aside>
    <footer>
      <p>DemocracIA · PEIRS · Informe generado {date}</p>
    </footer>
  </article>
</body>
</html>
```

**CSS:** dual-mode — pantalla y print media query.

### 11.2. PDF

**Herramienta primaria:** `weasyprint` (requiere libs sistema). Si no está
disponible en Railway, **fallback a xhtml2pdf** con tipografía alternativa.

**Características del PDF:**

- A4 con márgenes 2.2cm superior / 2cm laterales / 2.5cm inferior
- Numeración automática de páginas
- Encabezado: logo + "PEIRS Elite Report · {country}" a la izquierda, número de
  capítulo a la derecha
- Pie: página × de total, fecha de generación, clasificación
- Saltos de página automáticos entre capítulos
- TOC con paginación real
- Colores institucionales preservados
- Enlaces internos clicables (citas → Anexo B)

### 11.3. Markdown

Versión plain para archivado / conversión. Mantiene estructura y citas; las
visualizaciones se documentan como bloques `[Visualización: kind — title]`.

---

## 12. Integración con el dashboard

### 12.1. Nuevo tab reemplaza "Informe PEIRS"

- Tab actual "📄 Informe PEIRS" se **renombra** a "📘 Informe Elite"
- Mantiene el `innerTab` id `informe` para no romper deep-links
- ReportViewer original queda disponible como **view alterno**
  ("Ver versión técnica PEIRS completa")

### 12.2. UI del tab

```
┌─────────────────────────────────────────────────────────┐
│  📘 Informe Elite                       [↻ Regenerar]  │
├─────────────────────────────────────────────────────────┤
│  Audiencia:   [Institucional ▼]                         │
│  Idioma:      [Español ▼]                               │
│  Tipo:        [Preliminary ▼]                           │
│  Clasificación: [● Público  ○ Restringido  ○ Conf.]     │
│                                                          │
│  [✓] Incluir análisis predictivo                        │
│  [✓] Incluir anexo C (lista completa de hallazgos)      │
│  Horizonte forecast: [14 días ▼]                        │
│                                                          │
│                [▶ Generar Informe Elite]                │
│                                                          │
│  (generación: 3-5 min · costo: ~$0.40-0.80)             │
├─────────────────────────────────────────────────────────┤
│  Estado: [██████████████████▓░░░] 85% — Cap. 10/12      │
│  Secciones: ✓ Estructura  ✓ Datasets  ✓ Hunter          │
│             ✓ RAG  ✓ Predictivo  ⏳ Redacción Claude   │
├─────────────────────────────────────────────────────────┤
│  [ÚLTIMO INFORME GENERADO]                              │
│  DMC-PER-2026-001 · 20-abr 14:23 · 47 páginas          │
│  ⬇ Descargar PDF   ⬇ Descargar HTML   ⬇ Descargar MD   │
│                                                          │
│  [VIEWER EMBEBIDO]                                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │ TOC interno                                       │   │
│  │ Capítulo 1 · Contexto histórico                  │   │
│  │ [gráfico serie V-Dem]                            │   │
│  │ Narrativa con citas APA superíndice              │   │
│  │ ...                                               │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  [HISTORIAL]                                            │
│  DMC-PER-2026-001  20-abr  institucional  es  [ver]    │
│  DMC-PER-2026-000  19-abr  executive       es  [ver]    │
└─────────────────────────────────────────────────────────┘
```

### 12.3. Endpoint

```
POST /api/report/elite/generate
  body: EliteReportRequest
  response (sync): EliteReportOutput completo

POST /api/report/elite/generate-async
  body: EliteReportRequest
  response: { report_id, status: "generating" }

GET  /api/report/elite/status/{report_id}
  response: { report_id, status, progress_pct, current_stage }

GET  /api/report/elite/{report_id}/download?format=pdf|html|md
  response: archivo directo

GET  /api/report/elite/list?country=PER&limit=20
  response: { items: [metadata], total: N }
```

### 12.4. Persistencia

Tabla nueva `elite_reports`:

```sql
CREATE TABLE elite_reports (
    report_id         TEXT PRIMARY KEY,
    country_code      TEXT NOT NULL,
    mission_name      TEXT,
    lead_observer     TEXT,
    report_number     TEXT,
    classification    TEXT,
    audience          TEXT,
    language          TEXT,
    report_type       TEXT,
    generated_at      TEXT NOT NULL,
    generation_time_s REAL,
    tokens_used_in    INTEGER,
    tokens_used_out   INTEGER,
    status            TEXT,
    page_count        INTEGER,
    md_path           TEXT,
    html_path         TEXT,
    pdf_path          TEXT,
    stats_json        TEXT
);
CREATE INDEX idx_elite_country_date ON elite_reports(country_code, generated_at DESC);
```

---

## 13. Roadmap de implementación

### Sprint 2 — DataLoader unificado (~4h)

**Objetivo:** módulos `loaders/` que traen toda la evidencia normalizada.

**Subtareas:**

1. `hunter_loader.py` — levanta entries + alerts del backend.
2. `rag_loader.py` — tira del corpus constitucionalista con filtrado por país.
3. `datasets_loader.py` — carga series V-Dem, FH, PEI, RSF desde `/data`.
4. Cache TTL 1h para evitar reconsultas.
5. Test unitario sobre PER con validación de shape.

**Entregable:** función `EliteLoader.load_all(cc, period)` que retorna un dict
normalizado con todos los vértices del triángulo de evidencia.

### Sprint 3 — Organizers + PredictiveEngine (~5h)

**Objetivo:** módulos que agrupan y proyectan la evidencia.

**Subtareas:**

1. `phase_organizer.py` — agrupa entries por las 9 fases.
2. `cross_reference.py` — matchea findings ↔ normativa por keyword + semántica
   ligera.
3. `predictive/engine.py` — motor híbrido reglas + Claude.
4. Templates de escenarios en `predictive/scenarios.py`.
5. Test sobre PER con verificación de coherencia (ej: si hay 14
   fraud_allegation, el escenario de disputa debe estar entre 0.4 y 0.7 de
   probabilidad).

**Entregable:** `ForecastPayload` válido para PER + estructura `PhaseEvidence`
por capítulo.

### Sprint 4 — ChapterComposer con Claude (~7h)

**Objetivo:** 12 capítulos redactados con calidad elite.

**Subtareas:**

1. `prompts/base_context.md` — contexto compartido completo.
2. 12 prompts específicos en `prompts/cap_NN_*.md`.
3. `chapter_composer.py` con prompt caching de Anthropic.
4. Concurrency 4, timeout 60s por capítulo, 2 reintentos.
5. `citation_builder.py` con formateador APA 7 para 7 tipos de fuente.
6. Test: generación completa de los 12 capítulos para PER, validación de
   longitud objetivo y cobertura de citas.

**Entregable:** 12 capítulos narrados con citas + bibliografía completa.

### Sprint 5 — Visualizer extendido (~6h)

**Objetivo:** 21 tipos de visualización SVG institucional.

**Subtareas:**

1. 8 renderers nuevos que no teníamos (timeseries_multi, events_timeline,
   matrix_normativa, phase_timeline, hourly_timeline, map_regions_affected,
   actor_network, heatmap_rights).
2. 8 renderers adicionales de Elite (progress_chart,
   integrity_incidents_grid, judicial_timeline, compliance_matrix,
   forecast_chart, scenario_probability, early_warning_meter,
   semaphore_institutional, dimensions_radar, matrix_recommendations,
   system_architecture, flow_chart_voting, network_institutions).
3. Estandarización de paleta + tipografía SVG.
4. Test visual: render de cada tipo con data de PER, validación manual de
   legibilidad.

**Entregable:** módulo `visualizer/` completo con 21 kinds soportados.

### Sprint 6 — Renderer PDF + Endpoints + Frontend (~5h)

**Objetivo:** producto integrado end-to-end.

**Subtareas:**

1. `html_renderer.py` con Jinja2 template completo.
2. `pdf_renderer.py` con weasyprint (con fallback xhtml2pdf).
3. Tipografía: Fraunces + DM Sans + DM Mono como fonts embebidos.
4. Endpoints sync y async (`/api/report/elite/generate*`).
5. Tabla `elite_reports` en SQLite con migration.
6. Tab frontend con selectores, progreso, viewer, historial.
7. Smoke test end-to-end: generar informe Elite institucional para PER en
   español, verificar que produce MD + HTML + PDF sin errores.

**Entregable:** tab "📘 Informe Elite" en dashboard funcional, PDF de 40-50
páginas, calidad editorial.

### Resumen horas

| Sprint | Horas | Entregable |
|---|---|---|
| 1 (este) | ~3h (hecho) | Blueprint aprobado |
| 2 | ~4h | EliteLoader |
| 3 | ~5h | Organizers + PredictiveEngine |
| 4 | ~7h | 12 capítulos narrados + citas APA |
| 5 | ~6h | 21 visualizaciones |
| 6 | ~5h | PDF + endpoints + frontend |
| **Total** | **~30h** | Producto elite completo |

Distribuible en 6-8 sesiones de 3-5h.

---

## 14. Criterios de calidad y aceptación

El informe Elite se considera **aprobado para producción** cuando cumple TODOS
los siguientes criterios:

### 14.1. Cobertura de evidencia

- [ ] 100% de los capítulos temáticos (4-9) articulan los 3 vértices del
      triángulo de evidencia.
- [ ] ≥ 80% de los hallazgos prioritarios del Hunter aparecen citados al menos
      una vez en el informe.
- [ ] ≥ 5 instrumentos normativos citados con referencia al artículo específico.
- [ ] ≥ 3 datasets internacionales con serie histórica de 5+ años visualizada.

### 14.2. Rigor de citas

- [ ] 100% de las afirmaciones sustantivas tienen cita.
- [ ] 0 citas inventadas (validado por contraste con RAG y FindingRefs).
- [ ] Formato APA 7 estricto en Anexo B.
- [ ] Links clicables a medios primarios desde in-line.
- [ ] Superíndices clicables → Anexo B.

### 14.3. Calidad redaccional

- [ ] Lectura por observador/a internacional experto/a (juez retirado, ex-jefe
      de misión OEA) → recibir calificación *"al nivel que produciría una
      misión oficial"*.
- [ ] Sin frases cliché ("es importante notar", "cabe señalar", etc.).
- [ ] Tono consistente por audiencia.
- [ ] Balanceo de posiciones cuando hay controversia.

### 14.4. Diseño visual

- [ ] Tipografía Fraunces / DM Sans / DM Mono aplicada correctamente.
- [ ] Paleta institucional consistente en todas las visualizaciones.
- [ ] PDF ≤ 50 páginas con TOC paginado.
- [ ] Sin cuadros vacíos o placeholders.
- [ ] Saltos de página entre capítulos.
- [ ] Encabezado y pie de página en cada página.

### 14.5. Reproducibilidad

- [ ] Regenerar el informe con los mismos inputs produce output idéntico
      (misma estructura, citas, visualizaciones). La narrativa Claude puede
      variar ligeramente por temperatura pero manteniendo fuentes.
- [ ] `report_id` único generado cada vez.
- [ ] Persistencia en tabla `elite_reports` con metadata completa.

### 14.6. Performance

- [ ] Generación completa < 5 minutos.
- [ ] Costo de tokens por informe < $1.00.
- [ ] Manejo de timeouts y reintentos graceful.

### 14.7. Seguridad y compliance

- [ ] Sin exposición de tokens API o credenciales.
- [ ] Sanitización de inputs (especialmente `mission_metadata.lead_observer`
      en HTML).
- [ ] Respeto a `classification` — si es `confidential`, no indexar por crawler.
- [ ] Sin retención de PII más allá de lo necesario.

---

## 15. Referencias

### Informes modelo estudiados para benchmarking

1. **OEA / DECO.** (2023). *Informe final de la Misión de Observación Electoral
   — Guatemala, Elecciones Generales 2023*. Secretaría General OEA.
2. **EU EOM.** (2022). *Final Report — Colombia Presidential and Parliamentary
   Elections 2022*. European Union External Action.
3. **The Carter Center.** (2024). *Final Report — Venezuela Presidential
   Elections 2024*. Atlanta.
4. **IDEA Internacional.** (2023). *El Estado de la Democracia en las Américas*.
   IDEA Institute for Democracy and Electoral Assistance.
5. **OSCE/ODIHR.** (2023). *Election Observation Handbook* (7th ed.). OSCE
   Office for Democratic Institutions and Human Rights.
6. **NDI.** (2022). *Guide for Election Observation Missions*. National
   Democratic Institute.

### Documentos del sistema PEIRS ya producidos

- [`REPORT_DESIGNER.md`](REPORT_DESIGNER.md) — Blueprint de la Fase A-E del
  ReportDesigner (Fases A-D implementadas).
- [`INFORME_PERU_2026.md`](INFORME_PERU_2026.md) — Informe v1.1 manual para
  Perú (baseline de contenido).
- `backend/rag/corpus.py` — 46 entries de corpus legal electoral (6
  específicos de Perú).

### Estándares normativos de referencia

- ICCPR — International Covenant on Civil and Political Rights (1966).
- CADH — Convención Americana sobre Derechos Humanos (1969).
- CDI — Carta Democrática Interamericana (2001).
- ONU — Declaración de Principios para la Observación Internacional de
  Elecciones (2005).

---

## Decisiones abiertas pendientes de aprobación

Antes de arrancar el Sprint 2, necesito confirmación de Mariana sobre:

1. **¿Los 12 capítulos son los correctos, o agregás/sacás alguno?**
2. **¿Estructura "triángulo de evidencia" te cierra?** Cualquier capítulo
   temático (4-9) va a tener: antecedente + observación + marco → análisis.
3. **¿El motor predictivo debe ser obligatorio o opt-in?** Propuesta:
   obligatorio en informes "preliminary" y "final"; opt-in en "jornada".
4. **¿Nivel de clasificación por defecto?** ("public" propuesto — razonable
   para DemocracIA).
5. **¿Firma manual del jefe de misión?** Si sí, ¿cómo se captura (PNG subido,
   texto, ambos)?
6. **¿Tab actual "Informe PEIRS" se reemplaza o coexiste?** Propuesta:
   reemplaza, con vínculo al ReportViewer original como "vista técnica PEIRS".
7. **¿Apuntamos solo a PER para Elite o hacemos genérico para 38 países?**
   Propuesta: arquitectura genérica desde el inicio, contenido específico PER
   en Sprint 4.
8. **¿Costo máximo aceptable por informe Elite?** Propuesta: $1.00. Con
   prompt caching y concurrency se alcanza ~$0.40-0.80.

Con estas 8 respuestas, cierro el blueprint y arrancamos Sprint 2.

---

**Fin del blueprint v1.0. Esperando revisión de Mariana para ajustes antes de
Sprint 2.**
