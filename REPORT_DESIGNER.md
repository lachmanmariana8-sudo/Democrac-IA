# ReportDesigner — Blueprint arquitectónico

**Propósito:** Sub-agente de PEIRS especializado en componer informes de observación electoral de nivel internacional a partir de los hallazgos del Hunter, los datasets estructurales y el análisis cualitativo. Reproducible, parametrizable por audiencia, integrado con el dashboard.

**Estado del blueprint:** Diseño aprobado en 2026-04-14. Documento histórico que guió la implementación.

---

## ⓘ Implementation Status (2026-05-04)

> **Este blueprint guió la implementación de dos productos relacionados:**
>
> 1. **`ReportDesigner` (sub-agente)** — implementado en
>    `backend/agents/report_designer/`. Pipeline Structurer → Visualizer
>    → Composer. 4 audiencias (technical / executive / press /
>    international). ES / EN. Dedupe semántico (category+URL+date).
>    Priorización ponderada por severidad × recencia × credibilidad.
>    **OPERATIVO** al 4-may-2026.
>
> 2. **`PEIRS Elite Report`** — sucesor canónico del ReportDesigner para
>    la audiencia institucional internacional. Implementado en
>    `backend/agents/elite_report/`. Pipeline de 6 etapas (EliteLoader →
>    PhaseOrganizer → CrossReferenceBuilder → PredictiveEngine →
>    ChapterComposer → Visualizer + Renderer). 12 capítulos + 3 anexos.
>    i18n trilingüe (es/en/pt). Costo $0.40-0.80 por informe.
>    **OPERATIVO** al 4-may-2026.
>
> **Diferencia entre ambos:** el ReportDesigner es la versión genérica
> con cuatro audiencias y dos idiomas; el Elite Report es la versión
> "premium" especializada para audiencia institucional/observadores
> internacionales con motor predictivo y i18n trilingüe.
>
> **Para el blueprint sucesor del Elite Report**, ver
> [ELITE_REPORT.md](ELITE_REPORT.md).
>
> **Para el estado actual de la plataforma**, ver
> [STATUS_REPORT.md](STATUS_REPORT.md) y
> [DOCS Proyect/PEIRS_Arquitectura_Roadmap.md](DOCS%20Proyect/PEIRS_Arquitectura_Roadmap.md).

---

## 1. Problema que resuelve

El pipeline actual del PEIRS produce:
- **Datos estructurales** (FH, V-Dem, PEI, RSF) vía `data_loaders.py`.
- **Hallazgos en vivo** (Hunter → tabla `alerts` + `observation_sessions`).
- **Análisis cualitativo** (11 capítulos generados por el pipeline LangGraph — `architect` + `auditor` + `hunter`).

Lo que NO hace bien:
- Combinar esas tres fuentes en un **documento único, narrado, auditable y visualmente superior**.
- Adaptar el mismo contenido a **distintas audiencias** (técnica, ejecutiva, prensa, internacional).
- Mantener **trazabilidad de fuente** al nivel de cada afirmación del informe.
- Generar **visualizaciones ad-hoc** (timelines, infografías, matrices de derechos).

El `ReportDesigner` cubre exactamente ese gap.

---

## 2. Arquitectura general

```
                    ┌──────────────────────────────────────┐
                    │         ReportDesigner.run()         │
                    │  (backend/agents/report_designer.py) │
                    └────────────────┬─────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
      ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
      │  Structurer   │ →  │  Visualizer   │ →  │   Composer    │
      │   (paso 1)    │     │   (paso 2)    │     │   (paso 3)    │
      └───────────────┘     └───────────────┘     └───────────────┘
              │                      │                      │
              ▼                      ▼                      ▼
   Deduplica, agrupa,        Genera specs de          Render final
   decide secciones,         gráficos (SVG/           (MD + HTML +
   ordena por tema,          Chart.js), infografías   PDF) con CSS
   asigna prioridad          de KPIs, matrices        institucional
```

### Inputs

```python
class ReportRequest(BaseModel):
    country_code: str                           # "PER"
    audience: Literal[
        "technical",       # ~20 pág, anexos completos
        "executive",       # ~2 pág, gráficos clave
        "press",           # ~1 pág, 1 infografía
        "international",   # ~15 pág, inglés, marco comparado
    ]
    period_days: int = 7                        # ventana de hallazgos a incluir
    include_live_alerts: bool = True            # tirar de /api/alerts/{cc}
    include_datasets: bool = True               # FH/V-Dem/PEI/RSF
    include_chapters: Optional[List[str]] = None  # filtrar capítulos del informe LangGraph
    language: Literal["es", "en"] = "es"
    output_formats: List[Literal["md", "html", "pdf"]] = ["md", "html"]
```

### Output

```python
class ReportOutput(BaseModel):
    report_id: str
    country_code: str
    audience: str
    generated_at: str
    markdown: str
    html: str
    pdf_url: Optional[str]          # ruta relativa al archivo
    sections: List[ReportSection]   # estructura parseable
    stats: ReportStats              # total hallazgos, por severidad, etc.
    sources_cited: List[SourceCitation]
    visualizations: List[VizSpec]   # gráficos embebidos
    warnings: List[str]             # qué faltó, qué se aproximó
```

---

## 3. Paso 1 — Structurer

**Responsabilidad:** transformar el raw data en una estructura semántica ordenada.

### Entrada
- Entries del Hunter (~600 en el caso Perú) desde `/api/observation/{cc}/entries`.
- Alertas high/critical desde `/api/alerts/{cc}`.
- Datasets estructurales desde el reporte más reciente (`reports_store`).
- 11 capítulos cualitativos desde `reports_store[run_id].report_chapters`.

### Proceso

**3.1 Deduplicación semántica.** El Hunter registra el mismo hecho múltiples veces en runs distintos (ejemplo: las 180 mesas afectadas en Perú aparecen en 4 entries con fraseos similares). El Structurer agrupa por:

```python
def dedupe_key(entry):
    return (
        entry["category"],
        normalize_url(entry.get("evidence_ref")),   # misma URL = mismo hecho
        entry["recorded_at"][:10],                  # mismo día
    )
```

Para entries sin URL (ej. análisis generados), se usa embedding semántico del `finding` truncado a 100 chars + categoría.

**3.2 Agrupación por tema.** El classifier LLM (Claude) vuelve a leer los hallazgos deduplicados y asigna **tema** (distinto de `category`). Los temas son más gruesos y narrativos:

```
TEMAS = [
    "crisis_logistica_emb",
    "desinformacion",
    "violencia_politica",
    "integridad_escrutinio",
    "tecnologia_electoral_ia",
    "financiamiento_campana",
    "medios_libertad_prensa",
    "genero_violencia_politica",
    "pueblos_originarios_accesibilidad",
    "resolucion_disputas",
    "captura_institucional",
]
```

Un hallazgo puede tener 1–3 temas.

**3.3 Priorización.** Ordena por `score = severity_weight * recency_weight * source_credibility`:

```
severity_weight  = {critical:10, high:7, medium:3, low:1, info:0.5}
recency_weight   = 1 + 2 * exp(-days_since / 3)         # decaimiento exponencial
source_weight    = {ooni:1.5, idl:1.4, jne:1.3, onpe:1.3,
                    elcomercio:1.0, gestion:1.0, rpp:1.0,
                    andina:0.9, wayka:0.8, (sin fuente):0.5}
```

**3.4 Decisión de secciones.** Según `audience`, usa un template de estructura:

```python
SECTION_TEMPLATES = {
    "technical": [
        "portada", "resumen_ejecutivo", "metodologia", "cifras_clave",
        "contexto", "timeline_hallazgos", "temas_criticos",
        "derechos_vulnerados", "responsabilidad_penal", "recomendaciones",
        "anexo_fuentes", "anexo_metodologia_tecnica",
    ],
    "executive": [
        "portada", "declaracion_1_pagina", "cifras_clave",
        "3_temas_mas_criticos", "recomendaciones_prioritarias",
    ],
    "press": [
        "titulo", "bajada", "infografia_unica",
        "3_hallazgos_mas_cita", "contacto",
    ],
    "international": [
        "cover", "executive_summary", "context_comparative",
        "findings", "rights_framework", "recommendations",
        "methodology", "references",
    ],
}
```

**3.5 Asignación de evidencia.** Cada sección carga sus hallazgos relevantes con metadata de trazabilidad:

```python
class SectionContent(BaseModel):
    section_id: str
    title: str
    narrative: str                    # texto cualitativo (del Composer)
    findings: List[FindingRef]        # evidencia citable
    viz_specs: List[VizSpec]          # gráficos a renderizar
    order: int
```

### Salida del Structurer

Un `ReportSkeleton` con secciones vacías de narrativa pero llenas de evidencia.

---

## 4. Paso 2 — Visualizer

**Responsabilidad:** generar especificaciones de gráficos según el contenido de cada sección.

### Tipos de visualización soportados

```python
class VizSpec(BaseModel):
    kind: Literal[
        "timeline",          # hallazgos por día
        "bar_horizontal",    # rankings (medios, categorías, derechos)
        "donut",             # distribución por severidad
        "kpi_card",          # cifra grande con contexto
        "matrix",            # cruce categoría × severidad
        "map_mesas",         # mapa de mesas afectadas (Perú: regiones)
        "sparkline",         # tendencia pequeña inline
        "quote_block",       # cita destacada con fuente
        "infographic_top",   # infografía top cifras para portada
    ]
    data: dict              # datos específicos del chart
    title: str
    caption: str            # pie con fuente y período
    width: Optional[int]    # en mm, para PDF
    svg: Optional[str]      # SVG pre-renderizado (server-side)
```

### Renderizado server-side

Para que el PDF lleve gráficos sin depender del navegador:

- **KPI cards, quote blocks, matrix, infografía:** SVG generado a mano (templates en `report_designer/visualizations/`).
- **Bar charts, timeline, donut:** `matplotlib` → SVG embebido en el MD/HTML.
- **Mapa de mesas Perú:** SVG estático de regiones (Lima, Callao, Lima Sur, Trujillo) con overlay de intensidad según cantidad de mesas afectadas.

### Ejemplo — Timeline de hallazgos Perú

```
data = {
    "days": ["2026-04-09", "2026-04-10", "2026-04-11", "2026-04-12", "2026-04-13", "2026-04-14"],
    "series": [
        {"name": "critical", "values": [0, 0, 0, 0, 2, 2]},
        {"name": "high",     "values": [20, 10, 10, 6, 22, 6]},
        {"name": "medium",   "values": [50, 40, 45, 55, 60, 9]},
    ],
    "annotations": [
        {"day": "2026-04-12", "label": "Jornada electoral", "color": "#d32f2f"},
        {"day": "2026-04-10", "label": "Silencio electoral", "color": "#f57c00"},
    ],
}
```

Salida: SVG de ~400×180 con área apilada, anotaciones verticales, ejes y leyenda integrados.

### Ejemplo — Infografía top (portada)

```
┌──────────────────────────────────────────────┐
│  PERÚ — ELECCIONES GENERALES 12 ABR 2026     │
│                                               │
│  [ICONO]    [ICONO]    [ICONO]   [ICONO]     │
│   63.300     180+        4          74        │
│  CIUDADANOS  MESAS    CRÍTICAS   ALTAS        │
│  SIN VOTAR  AFECT.                            │
│                                               │
│  [ICONO]    [ICONO]                          │
│    293        4                               │
│   FACT-CHECK DENUNCIAS                        │
│    (IDL)    PENALES                           │
└──────────────────────────────────────────────┘
```

---

## 5. Paso 3 — Composer

**Responsabilidad:** generar el texto narrativo de cada sección + render final en MD/HTML/PDF.

### Prompts por audiencia

Hay 4 prompts base en `report_designer/prompts/`:

**5.1 `technical.md`** — tono académico, citas formales, longitud por sección 400–800 palabras, incluye metodología y caveats explícitos.

**5.2 `executive.md`** — tono ejecutivo, bullets accionables, máximo 120 palabras por sección, conclusiones en "negrita".

**5.3 `press.md`** — tono periodístico, frases cortas, una cita textual destacada, sin jerga técnica.

**5.4 `international.md`** — inglés, marco comparado (cita OEA/IDEA/OSCE), sigue estilo de EU EOM.

### Estructura de prompt de sección

Cada sección se genera con un prompt del tipo:

```
# Rol
Sos un redactor de informes de observación electoral con entrenamiento en
{audience_training}. Escribís la sección "{section_title}" del informe final.

# Contexto del país
{country_context}   # 1 párrafo generado por el Structurer

# Hallazgos relevantes (ordenados por prioridad, top 20)
{findings_json}

# Visualizaciones que van en esta sección
{viz_captions}      # pies de gráficos que el lector verá

# Instrucciones de estilo
{audience_style_rules}

# Instrucciones de citación
- Cada afirmación sustantiva debe cerrar con una referencia: [medio, fecha] o
  [instrumento legal Art.].
- Si un hallazgo tiene URL, usar markdown link.
- No inventar cifras. Si falta un dato, escribir "(cifra en verificación)".

# Longitud máxima
{max_words}

Devolvé SOLO el markdown de la sección, sin título de nivel 1.
```

### Cacheo y optimización

- El Composer usa **prompt caching de Anthropic** para el contexto del país + findings (que son estables durante una sesión). Se aprovecha cuando se generan múltiples variantes de audiencia sobre la misma data.
- Caching de secciones: si una sección ya fue generada en una versión anterior del informe y los findings no cambiaron (hash estable), se reusa.

### Render final

**Markdown:** unión ordenada de secciones + frontmatter YAML con metadata.

**HTML:** template en `report_designer/templates/report.html` con:
- CSS institucional (ya tenemos estilo en `build_pdf.py`, se refactoriza a `report.css`).
- SVGs inline.
- Links clickeables con `target="_blank"`.
- Table of contents auto-generado.
- Footer con generated_at + versión.

**PDF:** usa el mismo HTML procesado con `xhtml2pdf` (ya instalado) o se upgrade a `weasyprint` si hace falta mejor tipografía. Pesar los trade-offs antes de implementar.

---

## 6. Integración con el backend existente

### 6.1 Endpoint nuevo

```python
# backend/app.py

@app.post("/api/report/designer/generate")
async def generate_designed_report(req: ReportRequest):
    """
    Dispara el ReportDesigner y retorna metadata + ruta de descarga.
    El proceso corre en background (2-5 min por informe completo).
    Retorna report_id para polling.
    """
    if not HUNTER_AVAILABLE or not llm:
        raise HTTPException(503, "LLM o Hunter no disponibles")

    report_id = str(uuid.uuid4())[:12]
    asyncio.create_task(
        ReportDesigner(llm=llm).run_async(req, report_id=report_id)
    )
    return {
        "report_id": report_id,
        "status": "generating",
        "poll_url": f"/api/report/designer/status/{report_id}",
    }


@app.get("/api/report/designer/status/{report_id}")
async def report_designer_status(report_id: str):
    """Polling del estado. Retorna progreso, errores y link al archivo final."""
    ...


@app.get("/api/report/designer/{report_id}/download")
async def report_designer_download(report_id: str, format: str = "pdf"):
    """Descarga del archivo generado."""
    ...
```

### 6.2 Persistencia

Los informes generados se guardan en:
- `reports/designed/{report_id}.md`
- `reports/designed/{report_id}.html`
- `reports/designed/{report_id}.pdf`
- Fila en tabla nueva `designed_reports`:
  ```sql
  CREATE TABLE designed_reports (
      report_id    TEXT PRIMARY KEY,
      country_code TEXT NOT NULL,
      audience     TEXT NOT NULL,
      language     TEXT NOT NULL,
      run_id       TEXT,                    -- run_id del análisis base
      generated_at TEXT NOT NULL,
      stats        TEXT,                    -- JSON con métricas
      status       TEXT,                    -- generating | done | failed
      error_msg    TEXT,
      md_path      TEXT,
      html_path    TEXT,
      pdf_path     TEXT
  );
  ```

### 6.3 Frontend

**Tab nuevo** `📄 Informe preliminar` en `PeruSituationRoom`. Distinto del actual "Informe PEIRS" (que muestra los 11 capítulos tal cual). El nuevo:

- Selector de **audiencia** (4 botones tipo chip: Técnico / Ejecutivo / Prensa / Internacional).
- Selector de **período** (24h / 7d / 30d / todo el proceso).
- Selector de **idioma** (ES / EN).
- Botón **"Generar informe"** → dispara el endpoint.
- Durante la generación: barra de progreso con pasos ("Deduplicando → Clasificando temas → Redactando → Visualizando → PDF").
- Al terminar: embebe el HTML en iframe + botones de descarga PDF/MD + botón "Enviar por email".

Los informes previos se listan abajo (últimos 10) con su audiencia, fecha y tamaño.

---

## 7. Estructura de archivos a crear

```
backend/
└── agents/
    ├── report_designer/
    │   ├── __init__.py
    │   ├── designer.py                # ReportDesigner class
    │   ├── structurer.py              # Paso 1
    │   ├── visualizer.py              # Paso 2
    │   ├── composer.py                # Paso 3
    │   ├── models.py                  # ReportRequest, ReportOutput, VizSpec, etc.
    │   ├── dedupe.py                  # lógica de deduplicación
    │   ├── prompts/
    │   │   ├── technical.md
    │   │   ├── executive.md
    │   │   ├── press.md
    │   │   └── international.md
    │   ├── templates/
    │   │   ├── report.html            # template HTML base
    │   │   └── report.css             # estilos
    │   └── visualizations/
    │       ├── timeline.py            # genera SVG timeline
    │       ├── kpi_card.py            # SVG de KPI
    │       ├── donut.py               # severidad distribución
    │       ├── matrix.py              # cruce categoria × severidad
    │       ├── map_peru.py            # SVG base + overlay
    │       └── infographic.py         # infografía de portada

reports/
└── designed/
    ├── <report_id>.md
    ├── <report_id>.html
    └── <report_id>.pdf
```

---

## 8. Dependencias nuevas a instalar

```
matplotlib>=3.9      # gráficos server-side
jinja2>=3.1          # templates HTML
pillow>=10           # manipulación de imágenes
# ya tenemos: markdown, xhtml2pdf, anthropic, langchain
```

Agregar a `requirements.txt` + re-deploy.

---

## 9. Plan de implementación en fases

**Fase A — Esqueleto funcional (4 h)**
- Crear estructura de archivos.
- Implementar `ReportDesigner.run()` con los 3 pasos en mock (devuelven datos fijos).
- Endpoint `/api/report/designer/generate` devolviendo un informe hardcoded igual al INFORME_PERU_2026.md actual.
- Tab nuevo en dashboard con los selectores y el iframe.
- Validar que el loop completo funciona end-to-end con datos estáticos.

**Fase B — Structurer real (3 h)**
- Implementar deduplicación, agrupación por tema, priorización.
- Loader que tira de `/api/observation/{cc}/entries` + `/api/alerts/{cc}` + reports_store.
- Unit tests sobre el caso Perú (654 entries → esperamos ~80 hallazgos deduplicados).

**Fase C — Composer real (3 h)**
- Implementar los 4 prompts por audiencia.
- Llamadas a Claude con prompt caching.
- Render MD + HTML con Jinja2.
- Validar output sobre caso Perú.

**Fase D — Visualizer real (4 h)**
- Implementar los 8 tipos de viz con matplotlib/SVG.
- Timeline + infografía top + donut + matrix.
- Integración inline en el HTML.

**Fase E — PDF + polish (2 h)**
- Upgrade de xhtml2pdf a weasyprint si hace falta.
- Pie de página con numeración.
- Auto-TOC.
- Smoke test de los 4 modos de audiencia sobre Perú.

**Total estimado:** ~16 h de trabajo puro. En sesiones de 2-3 h es factible en 6-7 encuentros.

---

## 10. Criterios de éxito

El ReportDesigner estará "listo" cuando:

1. Generar el informe técnico Perú reproduce **≥95%** del contenido de `INFORME_PERU_2026.md` actual pero con mejor diseño visual.
2. Cambiar `audience` de `technical` a `executive` en un botón produce un informe **coherente de 2 páginas** en <60 segundos.
3. La versión inglés `international` pasa un test de lectura por un experto en EU EOM/OSCE sin correcciones estructurales.
4. El PDF abre sin warnings en Acrobat / Preview / Chrome.
5. Cada afirmación del informe tiene **al menos una fuente citable** con URL o instrumento legal.
6. Regenerar el mismo informe con la misma data produce **output idéntico** (determinismo con seed fija en el LLM).

---

## 11. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Costo de tokens explota en informe internacional largo | Prompt caching + generación sección por sección con contexto reducido |
| Claude inventa cifras (hallucinations) | Instrucción explícita "no inventar" + validador que chequea cada cifra contra la base de findings |
| Visualizaciones matplotlib se rompen en contenedor Railway (fuentes no instaladas) | Fallback a tablas MD + SVG inline; fonts embebidas en el template |
| PDF con caracteres especiales (ñ, acentos, emojis) falla | Test explícito con caso Perú que tiene muchos acentos; fallback sin emojis |
| El informe queda visualmente peor que competidores (OEA, EU EOM) | Referencia visual explícita en el template CSS; revisión estética en fase E |
| Falla el LLM durante generación | Checkpoints entre pasos; retry con backoff; fallback a draft sin narrativa fina |

---

## 12. Preguntas abiertas para discutir

1. **¿El informe se versiona?** Cada vez que se regenera, ¿se guarda todo o solo el último?
2. **¿Hay revisión humana antes de publicar?** ¿O el informe sale directamente al dashboard público?
3. **¿Quién firma el informe?** Si es para misión OEA, necesitamos bloque de firma en la portada.
4. **¿El ReportDesigner va a estar disponible para otros países** (Venezuela, Bolivia próximas elecciones) o es solo Perú?
5. **¿Hay un modo "draft privado"** solo visible para el observador vs. informe oficial publicado?

Estas preguntas no bloquean Fase A pero conviene resolverlas antes de Fase C (prompts).

---

**Documento cerrado. Próxima sesión: Fase A.**
