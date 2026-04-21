"""
ReportDesigner — Modelos Pydantic.

Definen los contratos de entrada (ReportRequest) y salida (ReportOutput) del
sub-agente de composición de informes. Ver REPORT_DESIGNER.md sección 2.
"""
from __future__ import annotations

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


Audience = Literal["technical", "executive", "press", "international"]
Language = Literal["es", "en"]
OutputFormat = Literal["md", "html", "pdf"]


class ReportRequest(BaseModel):
    """Parámetros para generar un informe."""
    country_code: str = Field(..., description="Código ISO-3 del país (PER, VEN, etc.)")
    audience: Audience = "technical"
    period_days: int = Field(7, ge=1, le=365, description="Ventana de hallazgos a incluir")
    include_live_alerts: bool = True
    include_datasets: bool = True
    include_chapters: Optional[List[str]] = None
    language: Language = "es"
    output_formats: List[OutputFormat] = Field(default_factory=lambda: ["md", "html"])
    use_llm: bool = Field(False, description="Si True, usa Claude para narrativas (Fase C). Si False, usa plantillas (Fase B).")


class FindingRef(BaseModel):
    """Referencia a un hallazgo citado en el informe con trazabilidad completa."""
    entry_id: Optional[str] = None
    finding: str
    category: str
    severity: str
    source_name: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    recorded_at: Optional[str] = None


class VizSpec(BaseModel):
    """Especificación de una visualización a renderizar en el informe."""
    kind: Literal[
        "timeline", "bar_horizontal", "donut", "kpi_card", "matrix",
        "map_mesas", "sparkline", "quote_block", "infographic_top"
    ]
    title: str
    caption: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)
    width: Optional[int] = None
    svg: Optional[str] = None


class ReportSection(BaseModel):
    """Sección del informe con su narrativa, evidencia y visualizaciones."""
    section_id: str
    title: str
    narrative: str = ""
    findings: List[FindingRef] = Field(default_factory=list)
    viz_specs: List[VizSpec] = Field(default_factory=list)
    order: int = 0


class ReportStats(BaseModel):
    """Métricas cuantitativas del informe."""
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    days_covered: int = 0
    sources_count: int = 0
    generated_at: str


class SourceCitation(BaseModel):
    """Fuente citada en el informe (agregado por el Composer)."""
    kind: Literal["rss", "legal_instrument", "case_law", "dataset", "expert"] = "rss"
    label: str
    url: Optional[str] = None
    date: Optional[str] = None


class ReportOutput(BaseModel):
    """Resultado completo del ReportDesigner."""
    report_id: str
    country_code: str
    audience: Audience
    language: Language
    generated_at: str
    status: Literal["generating", "done", "failed"] = "done"
    markdown: Optional[str] = None
    html: Optional[str] = None
    pdf_path: Optional[str] = None
    sections: List[ReportSection] = Field(default_factory=list)
    stats: Optional[ReportStats] = None
    sources_cited: List[SourceCitation] = Field(default_factory=list)
    visualizations: List[VizSpec] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
