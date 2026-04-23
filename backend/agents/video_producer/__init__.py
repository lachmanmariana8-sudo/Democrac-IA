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

# Renderer — opcional (requiere Pillow).
try:
    from agents.video_producer.renderer import (
        FrameRenderer,
        render_beat_png,
        render_beat_to_file,
    )
    RENDERER_AVAILABLE = True
except ImportError:
    RENDERER_AVAILABLE = False
    FrameRenderer = None              # type: ignore[assignment]
    render_beat_png = None            # type: ignore[assignment]
    render_beat_to_file = None        # type: ignore[assignment]

# TTS — opcional (requiere edge-tts).
try:
    from agents.video_producer.tts import (
        TTSEngine,
        SynthesisResult,
        pick_voice,
        synthesize_beat_audio,
    )
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    TTSEngine = None                  # type: ignore[assignment]
    SynthesisResult = None            # type: ignore[assignment]
    pick_voice = None                 # type: ignore[assignment]
    synthesize_beat_audio = None      # type: ignore[assignment]


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
    # renderer (Fase B1)
    "FrameRenderer",
    "render_beat_png",
    "render_beat_to_file",
    "RENDERER_AVAILABLE",
    # TTS (Fase C)
    "TTSEngine",
    "SynthesisResult",
    "pick_voice",
    "synthesize_beat_audio",
    "TTS_AVAILABLE",
]
