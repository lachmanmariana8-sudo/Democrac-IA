"""
PEIRS Elite Report — Modelos Pydantic (Sprint 2).

Contratos de datos para el sub-agente de composición de informes elite.
Ver ELITE_REPORT.md sección 6 para especificación completa.

Decisiones aprobadas (2026-04-20):
- Alcance: solo PER por ahora (arquitectura genérica, contenido específico).
- Motor predictivo obligatorio en preliminary/final.
- Sin firma del jefe de misión en portada.
- Clasificación por defecto: public.
- Costo máximo: $1.00 por informe.
"""
from __future__ import annotations

from typing import List, Optional, Literal, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone


# ── Types ────────────────────────────────────────────────────────────────
Audience = Literal["institutional", "executive", "press", "international"]
Language = Literal["es", "en"]
ReportClassification = Literal["public", "restricted", "confidential"]
ReportType = Literal["pre_electoral", "jornada", "preliminary", "final", "ad_hoc"]
OutputFormat = Literal["md", "html", "pdf"]
EarlyWarningLevel = Literal["green", "amber", "orange", "red"]

# Fases del ciclo electoral (consistente con OBS_PHASES del frontend)
ElectoralPhase = Literal[
    "preparatory", "pre_campaign", "campaign", "electoral_silence",
    "election_day", "counting_tabulation", "post_election",
    "dispute_resolution", "completed",
]

# Citation types
CitationType = Literal[
    "book", "article", "web", "legal", "case_law", "dataset",
    "report", "treaty", "journalistic",
]


# ── Metadata de la misión ───────────────────────────────────────────────
class MissionMetadata(BaseModel):
    """Metadatos institucionales de la misión de observación.
    Sin firma del jefe de misión (decisión 5, 2026-04-20)."""
    mission_name: str = "DemocracIA — Observación Electoral PEIRS"
    lead_observer: str = "Mariana Lachman"
    organization: str = "DemocracIA"
    report_number: str = Field(..., description="Ej. 'DMC-PER-2026-001'")
    classification: ReportClassification = "public"
    period_start: str = Field(..., description="ISO date 'YYYY-MM-DD'")
    period_end: str = Field(..., description="ISO date 'YYYY-MM-DD'")
    jornada_date: str = Field(..., description="Fecha de la elección, ISO")

    @field_validator("period_start", "period_end", "jornada_date")
    @classmethod
    def _validate_iso_date(cls, v: str) -> str:
        try:
            datetime.strptime(v[:10], "%Y-%m-%d")
        except Exception:
            raise ValueError(f"Fecha inválida: {v}. Formato esperado: YYYY-MM-DD")
        return v


# ── Request ─────────────────────────────────────────────────────────────
class EliteReportRequest(BaseModel):
    """Parámetros para generar un informe Elite."""
    country_code: str = Field(..., description="ISO-3 code; en Sprint 2-6: 'PER'")
    mission_metadata: MissionMetadata
    audience: Audience = "institutional"
    language: Language = "es"
    report_type: ReportType = "preliminary"

    # Control fino
    include_chapters: Optional[List[int]] = Field(
        None, description="Subset de capítulos 1-12. None = todos."
    )
    include_predictive: bool = True
    include_appendix_c: bool = Field(
        True, description="Lista completa de hallazgos del Hunter en anexo C."
    )
    forecast_horizon_days: int = Field(14, ge=1, le=90)
    use_llm: bool = Field(True, description="Fase C siempre activa en Elite.")
    output_formats: List[OutputFormat] = Field(default_factory=lambda: ["md", "html", "pdf"])

    @field_validator("country_code")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.upper()


# ── Finding + evidencia ─────────────────────────────────────────────────
class FindingRef(BaseModel):
    """Referencia a un hallazgo del Hunter con trazabilidad completa.
    Reutilizado entre ReportDesigner y EliteReport."""
    entry_id: Optional[str] = None
    finding: str
    category: str
    severity: str
    source_name: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    recorded_at: Optional[str] = None
    themes: List[str] = Field(default_factory=list)
    priority_score: Optional[float] = None
    phase: Optional[str] = None
    # Agregado 2026-04-29 — location se setea por hunter_loader cuando está
    # disponible en el ObservationEntry original. Sirve para mapping a regiones
    # en map_regions_affected / integrity_incidents_grid.
    location: Optional[str] = None


class PhaseEvidence(BaseModel):
    """Evidencia agrupada por fase electoral (para coherencia temporal)."""
    phase_id: ElectoralPhase
    phase_label: str
    findings: List[FindingRef] = Field(default_factory=list)
    total_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    dominant_themes: List[str] = Field(default_factory=list)
    period_start: Optional[str] = None
    period_end: Optional[str] = None


class CrossReference(BaseModel):
    """Link entre un hallazgo y un artículo del corpus normativo (cap. 2, 8)."""
    finding_entry_id: str
    finding_snippet: str
    normative_instrument: str
    normative_article: Optional[str] = None
    relevance: Literal["direct", "related", "contextual"] = "related"
    reasoning: str = Field(
        "", description="1-2 frases explicando por qué este hallazgo cruza esta norma."
    )


# ── Series históricas (cap. 1) ──────────────────────────────────────────
class HistoricalDatapoint(BaseModel):
    """Un punto de una serie histórica (V-Dem/FH/PEI/RSF)."""
    year: int
    value: float
    source: str
    note: Optional[str] = None


class HistoricalSeries(BaseModel):
    """Serie histórica completa de un indicador."""
    indicator: str = Field(..., description="'vdem_libdem', 'fh_total', 'pei_embs', 'rsf_score'")
    indicator_label: str
    source: str
    source_citation: str
    unit: str = Field("0-100", description="Escala del indicador")
    datapoints: List[HistoricalDatapoint]
    trend_direction: Literal["up", "down", "stable", "volatile"] = "stable"
    trend_note: str = ""


# ── Predictive ──────────────────────────────────────────────────────────
class ForecastScenario(BaseModel):
    """Un escenario predictivo."""
    scenario_id: str
    label: str
    probability: float = Field(..., ge=0.0, le=1.0)
    confidence_interval: Optional[Tuple[float, float]] = None
    indicators: List[str] = Field(default_factory=list)
    implications: str = ""
    watch_signals: List[str] = Field(default_factory=list)
    legal_basis: Optional[str] = Field(
        None, description="Artículo o norma que aplica al escenario."
    )


class ForecastPayload(BaseModel):
    """Resultado completo del PredictiveEngine."""
    horizon_days: int
    generated_at: str
    scenarios: List[ForecastScenario]
    dominant_pattern: str
    early_warning_level: EarlyWarningLevel
    early_warning_note: str
    methodology_note: str = (
        "Escenarios híbridos: reglas deterministas sobre patrones Hunter + "
        "análisis cualitativo con Claude. No son pronóstico electoral político "
        "(quién gana) — son estimación de dinámica institucional post-proceso."
    )


# ── Citas APA 7 ─────────────────────────────────────────────────────────
class CitationEntry(BaseModel):
    """Entry de bibliografía en formato APA 7."""
    citation_id: str = Field(..., description="'C-001', 'C-002', ...")
    type: CitationType
    apa_formatted: str = Field(
        ...,
        description="Cita completa APA 7, ej. 'V-Dem Institute. (2025). Varieties of Democracy...'"
    )
    short_form: str = Field(
        ...,
        description="Forma abreviada in-line, ej. '(V-Dem Institute, 2025)'"
    )
    url: Optional[str] = None
    accessed_date: Optional[str] = None
    notes: Optional[str] = None


# ── Visualizaciones ─────────────────────────────────────────────────────
VizKind = Literal[
    # De Fase D ya existente
    "infographic_top", "timeline", "bar_horizontal", "donut", "kpi_card",
    "matrix", "map_mesas", "sparkline", "quote_block",
    # Nuevas en Elite (ELITE_REPORT.md sección 10)
    "timeseries_multi", "events_timeline", "matrix_normativa",
    "network_institutions", "flow_chart_voting", "phase_timeline",
    "hourly_timeline", "map_regions_affected", "progress_chart",
    "integrity_incidents_grid", "actor_network", "judicial_timeline",
    "heatmap_rights", "compliance_matrix", "forecast_chart",
    "scenario_probability", "early_warning_meter", "semaphore_institutional",
    "dimensions_radar", "matrix_recommendations", "system_architecture",
    # Agregado 2026-04-29 — escenarios parlamentarios proyectados (Cap 9, PER-only).
    "parliament_scenarios",
]


class VizSpec(BaseModel):
    """Especificación de una visualización."""
    kind: VizKind
    title: str
    caption: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)
    width: Optional[int] = None
    height: Optional[int] = None
    svg: Optional[str] = Field(None, description="SVG pre-renderizado")


# ── Capítulo ────────────────────────────────────────────────────────────
class EliteChapter(BaseModel):
    """Un capítulo del informe Elite."""
    number: int = Field(..., description="1-12; 0 portada; -1 TOC; -2 declaración")
    chapter_id: str = Field(..., description="'contexto', 'marco_juridico', etc.")
    title: str
    subtitle: Optional[str] = None
    narrative: str = Field(
        "", description="Markdown con citas APA (generado por Composer)"
    )
    findings: List[FindingRef] = Field(default_factory=list)
    cross_references: List[CrossReference] = Field(default_factory=list)
    visualizations: List[VizSpec] = Field(default_factory=list)
    citations_used: List[str] = Field(
        default_factory=list,
        description="citation_ids referenciados en la narrativa"
    )
    historical_series: List[HistoricalSeries] = Field(default_factory=list)
    phase_evidence: Optional[PhaseEvidence] = None
    word_count: int = 0
    warnings: List[str] = Field(default_factory=list)
    tokens_used: Dict[str, int] = Field(default_factory=dict)


# ── Output completo ─────────────────────────────────────────────────────
class EliteReportOutput(BaseModel):
    """Resultado completo del PEIRSEliteReport."""
    report_id: str
    country_code: str
    mission: MissionMetadata
    audience: Audience
    language: Language
    report_type: ReportType
    generated_at: str
    status: Literal["generating", "done", "failed"] = "done"

    # Contenido
    chapters: List[EliteChapter] = Field(default_factory=list)
    forecast: Optional[ForecastPayload] = None
    citations: List[CitationEntry] = Field(default_factory=list)
    all_findings: List[FindingRef] = Field(
        default_factory=list,
        description="Universo completo para anexo C. Prioritizado."
    )

    # Outputs renderizados
    markdown: Optional[str] = None
    html: Optional[str] = None
    pdf_path: Optional[str] = None

    # Metadata operativa
    stats: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    tokens_used: Dict[str, int] = Field(default_factory=dict)
    estimated_cost_usd: float = 0.0
    generation_time_seconds: float = 0.0


# ── Bundle de evidencia cargada ──────────────────────────────────────────
class EvidenceBundle(BaseModel):
    """Producto del EliteLoader: toda la evidencia normalizada lista para el pipeline."""
    country_code: str
    period_start: str
    period_end: str
    loaded_at: str

    # Hunter
    hunter_entries: List[FindingRef] = Field(default_factory=list)
    hunter_stats: Dict[str, int] = Field(default_factory=dict)
    alerts_dispatched: int = 0

    # Phase evidence (post PhaseOrganizer)
    phase_evidence: Dict[str, PhaseEvidence] = Field(default_factory=dict)

    # RAG
    rag_documents: List[Dict[str, Any]] = Field(default_factory=list)

    # Datasets
    historical_series: List[HistoricalSeries] = Field(default_factory=list)

    # Cross-references (post CrossReference)
    cross_references: List[CrossReference] = Field(default_factory=list)

    # Temas (del Structurer existente del ReportDesigner)
    theme_ranking: List[Dict[str, Any]] = Field(default_factory=list)

    # Warnings del pipeline de carga
    warnings: List[str] = Field(default_factory=list)
