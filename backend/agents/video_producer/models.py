"""Schemas del Video Producer — pipeline data-driven (sin avatar IA).

Flujo: findings → VideoScript (guión) → Storyboard (beats + visuals) →
       Render (frames + audio TTS + MP4). Fase A entrega hasta Storyboard.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ── Presets ──────────────────────────────────────────────────────────────

class VideoPreset(str, Enum):
    ALERT_30S     = "alert_30s"         # 1 incidente crítico · 30s · 9:16
    WEEKLY_90S    = "weekly_90s"        # top findings de la semana · 90s · 9:16
    BRIEF_5MIN    = "brief_5min"        # institucional · 3-5min · 16:9
    EXPLAINER_60S = "explainer_60s"     # concepto técnico · 60s · 9:16


# ── Guionista ────────────────────────────────────────────────────────────

class VideoScriptRequest(BaseModel):
    country_code: str = "PER"
    period_days: int = 7
    severity_min: str = "high"
    max_findings: int = 5
    language: Literal["es", "en", "pt", "qu"] = "es"
    style: Literal["sober", "urgent", "explainer"] = "sober"
    target_duration_s: int = 75


class VideoScript(BaseModel):
    hook: str
    context: str
    findings_narrative: str
    closing: str
    word_count: int = 0
    estimated_duration_s: float = 0.0
    full_text: str = ""
    sources_cited: List[str] = Field(default_factory=list)
    language: str = "es"
    tone: str = "sober"


# ── Storyboard ────────────────────────────────────────────────────────────

class Overlay(BaseModel):
    """Elemento gráfico compuesto sobre el frame."""
    kind: Literal[
        "title",            # título de pantalla completa
        "lower_third",      # tercio inferior con nombre + fuente
        "stat_card",        # card con número destacado
        "quote",            # cita con comillas y atribución
        "source",           # "Fuente: IDL-Reporteros"
        "timeline_event",   # hito en timeline
        "cta",              # call-to-action final
    ] = "lower_third"
    text: str = ""
    secondary_text: str = ""                 # p.ej. fuente de una cita
    position: Literal["top", "center", "bottom", "left", "right"] = "bottom"
    start_s: float = 0.0
    duration_s: float = 4.0


class Beat(BaseModel):
    """Unidad narrativa del storyboard: narración + composición visual + overlays."""
    beat_id: str
    kind: Literal[
        "intro",        # logo + título
        "stat",         # KPIs / gráfico de dato
        "incident",     # descripción de un hallazgo
        "timeline",     # timeline animado
        "quote",        # cita destacada
        "outro",        # CTA final
    ] = "incident"
    narration: str = ""
    duration_s: float = 5.0
    visual: Literal[
        "solid_bg",
        "kpi_grid",
        "bar_chart",
        "donut_chart",
        "map_regions",
        "timeline",
        "quote_panel",
    ] = "solid_bg"
    visual_data: Dict[str, Any] = Field(default_factory=dict)
    overlays: List[Overlay] = Field(default_factory=list)
    bg_color_hex: str = "#0B1F2A"             # teal institucional oscuro
    accent_color_hex: str = "#D97706"         # naranja institucional

    # Audio (Fase C). El archivo se guarda en {audio_root}/{job_id}/beat_{idx:02d}.mp3
    # y se sirve via GET /api/video/{job_id}/audio/{beat_idx}.
    has_audio: bool = False
    audio_duration_s: Optional[float] = None
    audio_voice: Optional[str] = None


class Storyboard(BaseModel):
    preset: VideoPreset
    beats: List[Beat] = Field(default_factory=list)
    total_duration_s: float = 0.0
    width: int = 1080
    height: int = 1920                         # 9:16 por default (Reels/TikTok/Shorts)
    fps: int = 30


# ── Job ────────────────────────────────────────────────────────────────────

class VideoJobRequest(BaseModel):
    """Solicitud end-to-end: filtros + preset → guión + storyboard + render."""
    country_code: str = "PER"
    preset: VideoPreset = VideoPreset.ALERT_30S
    period_days: int = 7
    severity_min: str = "high"
    max_findings: int = 5
    language: Literal["es", "en", "pt", "qu"] = "es"
    style: Literal["sober", "urgent", "explainer"] = "sober"
    title: Optional[str] = None
    use_llm: bool = True
    dry_run: bool = False                      # si True: solo guión + storyboard, no render


class VideoJobResult(BaseModel):
    job_id: str
    country_code: str
    preset: str = "alert_30s"
    status: Literal[
        "pending", "scripting", "storyboarding",
        "storyboard_ready", "rendering", "completed", "failed",
    ] = "pending"

    script: Optional[VideoScript] = None
    storyboard: Optional[Storyboard] = None

    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_s: float = 0.0

    tokens_used: Dict[str, int] = Field(default_factory=lambda: {"input": 0, "output": 0})
    estimated_cost_usd: float = 0.0

    generated_at: str = ""
    findings_count: int = 0
    language: str = "es"
    style: str = "sober"

    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
