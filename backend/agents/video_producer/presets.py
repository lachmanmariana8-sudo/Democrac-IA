"""Configuración declarativa de los 4 presets de video.

Cada preset define duración objetivo, dimensiones, cantidad de hallazgos
y la secuencia de beats del storyboard.
"""
from __future__ import annotations

from typing import Any, Dict, List

from agents.video_producer.models import VideoPreset


PRESET_CONFIG: Dict[VideoPreset, Dict[str, Any]] = {
    VideoPreset.ALERT_30S: {
        "label":             "🚨 Alerta crítica",
        "description":       "1 incidente crítico + cita + fuente + CTA al dashboard.",
        "target_duration_s": 30,
        "max_findings":      1,
        "dimensions":        (1080, 1920),    # 9:16 vertical — Reels/TikTok/Shorts
        "style_default":     "urgent",
        "beat_types":        ["intro", "incident", "quote", "outro"],
        "target_platforms":  ["instagram_reels", "tiktok", "youtube_shorts"],
    },
    VideoPreset.WEEKLY_90S: {
        "label":             "📊 Resumen semanal",
        "description":       "Top hallazgos de la semana con timeline animado.",
        "target_duration_s": 90,
        "max_findings":      5,
        "dimensions":        (1080, 1920),    # 9:16 vertical
        "style_default":     "sober",
        "beat_types":        ["intro", "stat", "incident", "incident", "incident", "timeline", "outro"],
        "target_platforms":  ["instagram_reels", "instagram_feed", "youtube_shorts"],
    },
    VideoPreset.BRIEF_5MIN: {
        "label":             "📘 Brief institucional",
        "description":       "Informe para YouTube/LinkedIn con gráficos y narrativa completa.",
        "target_duration_s": 300,
        "max_findings":      8,
        "dimensions":        (1920, 1080),    # 16:9 horizontal
        "style_default":     "sober",
        "beat_types":        [
            "intro", "stat", "stat", "incident", "incident", "incident",
            "timeline", "quote", "outro",
        ],
        "target_platforms":  ["youtube", "linkedin", "web"],
    },
    VideoPreset.EXPLAINER_60S: {
        "label":             "🎓 Explainer técnico",
        "description":       "Concepto técnico (STAE, Art. 184, integridad electoral, etc.).",
        "target_duration_s": 60,
        "max_findings":      0,                # explainer no depende de findings
        "dimensions":        (1080, 1920),    # 9:16
        "style_default":     "explainer",
        "beat_types":        ["intro", "stat", "stat", "quote", "outro"],
        "target_platforms":  ["instagram_reels", "tiktok", "youtube_shorts", "educational"],
    },
}


def get_preset_config(preset: VideoPreset) -> Dict[str, Any]:
    return PRESET_CONFIG[preset]


def list_presets() -> List[Dict[str, Any]]:
    """Serializa los presets para exponerlos al frontend."""
    out = []
    for p, cfg in PRESET_CONFIG.items():
        w, h = cfg["dimensions"]
        out.append({
            "id":                p.value,
            "label":             cfg["label"],
            "description":       cfg["description"],
            "target_duration_s": cfg["target_duration_s"],
            "max_findings":      cfg["max_findings"],
            "width":             w,
            "height":            h,
            "aspect_ratio":      f"{w}:{h}",
            "style_default":     cfg["style_default"],
            "beat_count":        len(cfg["beat_types"]),
            "target_platforms":  cfg["target_platforms"],
        })
    return out
