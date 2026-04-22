"""Schemas del Video Producer."""
from __future__ import annotations

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


# ── Entrada del guionista ────────────────────────────────────────────────
class VideoScriptRequest(BaseModel):
    """Filtros para seleccionar los hallazgos que alimentan el guión."""
    country_code: str = "PER"
    period_days: int = 7                       # últimos N días de findings
    severity_min: str = "high"                 # high | critical
    max_findings: int = 5                      # 3-5 es lo ideal para 60-90s
    language: Literal["es", "en", "pt", "qu"] = "es"
    style: Literal["sober", "urgent", "explainer"] = "sober"
    target_duration_s: int = 75                # 60-90s típico


# ── Salida del guionista ────────────────────────────────────────────────
class VideoScript(BaseModel):
    """Guión periodístico producido por el Guionista-Claude."""
    hook: str                                  # apertura (~10s)
    context: str                               # marco (~15s)
    findings_narrative: str                    # hallazgos citados (~30-45s)
    closing: str                               # cierre + CTA (~10s)
    word_count: int = 0
    estimated_duration_s: float = 0.0
    full_text: str = ""                        # hook + context + findings + closing concatenado
    sources_cited: List[str] = Field(default_factory=list)
    language: str = "es"
    tone: str = "sober"


# ── Plan cinematográfico ─────────────────────────────────────────────────
class OverlaySpec(BaseModel):
    """Elemento gráfico sobrepuesto a una escena."""
    kind: Literal["lower_third", "caption", "stat_card", "svg_chart", "source_url"] = "caption"
    content: str = ""                          # texto o ref al SVG
    start_s: float = 0.0
    duration_s: float = 4.0
    position: Literal["top", "bottom", "left", "right", "center"] = "bottom"


class SceneSpec(BaseModel):
    """Una escena del video: lo que dice el avatar + overlays."""
    scene_id: str
    narration: str                             # texto que lee el avatar
    duration_s: float = 8.0
    avatar_style: Literal["talking", "reading", "authoritative"] = "talking"
    background: Literal["studio", "solid", "newsroom", "brief"] = "studio"
    background_value: str = "#0f4f4b"          # hex color si background=solid
    overlays: List[OverlaySpec] = Field(default_factory=list)
    b_roll_hint: Optional[str] = None          # descripción para B-roll futuro


class VideoPlan(BaseModel):
    """Plan completo producido por el Director-Claude."""
    scenes: List[SceneSpec] = Field(default_factory=list)
    total_duration_s: float = 0.0
    intro_hint: Optional[str] = None
    outro_hint: Optional[str] = None


# ── Request de producción completa ───────────────────────────────────────
class VideoJobRequest(BaseModel):
    """Solicitud end-to-end: genera guión + plan + renderiza con HeyGen."""
    country_code: str = "PER"
    period_days: int = 7
    severity_min: str = "high"
    max_findings: int = 5
    language: Literal["es", "en", "pt", "qu"] = "es"
    style: Literal["sober", "urgent", "explainer"] = "sober"
    target_duration_s: int = 75

    # HeyGen — opcionales, usan defaults si no se pasan
    avatar_id: Optional[str] = None
    voice_id: Optional[str] = None
    dimension_w: int = 1280
    dimension_h: int = 720
    title: Optional[str] = None                # para el archivo/entrega

    # Comportamiento
    use_llm: bool = True
    dry_run: bool = False                      # no llama a HeyGen, sólo genera guión+plan


# ── Resultado de un trabajo ──────────────────────────────────────────────
class VideoJobResult(BaseModel):
    """Estado de un job de video."""
    job_id: str
    country_code: str
    status: Literal["pending", "scripting", "planning", "rendering", "completed", "failed"] = "pending"
    script: Optional[VideoScript] = None
    plan: Optional[VideoPlan] = None

    heygen_video_id: Optional[str] = None
    heygen_status: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    tokens_used: Dict[str, int] = Field(default_factory=lambda: {"input": 0, "output": 0})
    estimated_cost_usd: float = 0.0

    generated_at: str = ""
    duration_s: float = 0.0

    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    # Metadata para UI
    findings_count: int = 0
    language: str = "es"
    style: str = "sober"
