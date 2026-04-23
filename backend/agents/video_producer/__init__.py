"""PEIRS Video Producer — sub-agente data-driven de composición audiovisual.

Genera videos cortos (30s–5min) para redes sociales + web a partir de los
hallazgos del Hunter:

    findings → Scriptwriter (Claude) → StoryboardBuilder → Render (frames + TTS + MP4)

Sin avatares IA: cada video muestra datos, citas, fuentes y gráficos —
coherente con una misión anti-desinformación.

4 presets (ver presets.py):
  - alert_30s:     9:16 · 30s  · alerta crítica
  - weekly_90s:    9:16 · 90s  · resumen semanal con timeline
  - brief_5min:   16:9  · 5min · institucional YouTube/LinkedIn
  - explainer_60s: 9:16 · 60s  · concepto técnico (STAE, Art. 184, etc.)
"""

from agents.video_producer.models import (
    Beat,
    Overlay,
    Storyboard,
    VideoJobRequest,
    VideoJobResult,
    VideoPreset,
    VideoScript,
    VideoScriptRequest,
)
from agents.video_producer.presets import (
    get_preset_config,
    list_presets,
    PRESET_CONFIG,
)
from agents.video_producer.storyboard import StoryboardBuilder
from agents.video_producer.video_producer import VideoProducer


__all__ = [
    # models
    "VideoScriptRequest",
    "VideoScript",
    "Overlay",
    "Beat",
    "Storyboard",
    "VideoPreset",
    "VideoJobRequest",
    "VideoJobResult",
    # presets
    "PRESET_CONFIG",
    "get_preset_config",
    "list_presets",
    # builders
    "StoryboardBuilder",
    "VideoProducer",
]
