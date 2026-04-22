"""PEIRS Video Producer — sub-agente de cinematografía y edición.

Genera videos cortos tipo noticia (60-90s) sobre los hallazgos del sistema:
1. Guionista (Claude) escribe un guión periodístico desde findings/alerts
2. Director (Claude) traduce el guión a plan de escenas con overlays
3. HeyGen API renderiza el video con un avatar hablante multilingüe
4. VideoProducer orquesta todo y persiste en SQLite
"""

from agents.video_producer.models import (
    VideoScriptRequest,
    VideoScript,
    SceneSpec,
    OverlaySpec,
    VideoPlan,
    VideoJobRequest,
    VideoJobResult,
)
from agents.video_producer.video_producer import VideoProducer

__all__ = [
    "VideoScriptRequest",
    "VideoScript",
    "SceneSpec",
    "OverlaySpec",
    "VideoPlan",
    "VideoJobRequest",
    "VideoJobResult",
    "VideoProducer",
]
