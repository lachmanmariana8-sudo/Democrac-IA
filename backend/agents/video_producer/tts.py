"""TTSEngine — síntesis de voz con edge-tts (Microsoft Edge TTS, gratuito).

Fase C del Video Producer v2. Convierte el texto de cada Beat en un MP3
y mide su duración real (desde los eventos SentenceBoundary / WordBoundary
que emite el stream de edge-tts).

DECISIÓN DE DISEÑO:
  La duración del audio dicta la duración del beat. Si el guión original
  estimaba 8s pero el TTS tarda 6.2s, usamos 6.2s — es más honesto que
  dejar 1.8s de silencio al final. Caller puede re-timear el storyboard.

FALLBACKS:
  - Sin edge-tts instalado     → synthesize devuelve (b'', 0.0) con error
  - Quechua (qu) sin voz nativa → warn + cae a voz española
  - Si Microsoft bloquea IPs   → el caller marca el beat como sin-audio

COSTO: USD 0.00 — edge-tts usa el endpoint público de Edge/Bing sin auth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

try:
    import edge_tts  # type: ignore
    _EDGE_TTS_OK = True
except ImportError:  # pragma: no cover
    _EDGE_TTS_OK = False


# ── Mapa voz por idioma × estilo ──────────────────────────────────────────────
# Seleccionadas por calidad (todas son Neural) + coherencia regional:
# - ES → Perú (voz local, pertinente para la misión)
# - EN → EE.UU. (estándar internacional broadcast)
# - PT → Brasil
# - QU → fallback a ES con aviso

VOICES: Dict[str, Dict[str, str]] = {
    "es": {
        "sober":     "es-PE-AlexNeural",        # masculino, sobrio
        "urgent":    "es-PE-AlexNeural",        # misma voz, prosodia por el texto
        "explainer": "es-PE-CamilaNeural",      # femenino, didáctico
    },
    "en": {
        "sober":     "en-US-AriaNeural",
        "urgent":    "en-US-AriaNeural",
        "explainer": "en-US-JennyNeural",
    },
    "pt": {
        "sober":     "pt-BR-AntonioNeural",
        "urgent":    "pt-BR-AntonioNeural",
        "explainer": "pt-BR-FranciscaNeural",
    },
    # 'qu' no tiene voces nativas en edge-tts — fallback al español peruano.
}


def pick_voice(language: str = "es", style: str = "sober") -> Tuple[str, Optional[str]]:
    """Devuelve (voice_id, warning). warning=None si hay voz nativa para el idioma."""
    lang = (language or "es").lower()
    st = (style or "sober").lower()
    table = VOICES.get(lang)
    if not table:
        # Quechua y otros → fallback español peruano
        fallback = VOICES["es"].get(st, VOICES["es"]["sober"])
        return (fallback, f"idioma {lang!r} sin voz nativa; fallback a {fallback}")
    return (table.get(st, table["sober"]), None)


# ── Resultado de una síntesis ─────────────────────────────────────────────────

@dataclass
class SynthesisResult:
    audio_mp3: bytes
    duration_s: float                  # duración real derivada de los boundaries
    voice: str
    warning: Optional[str] = None      # p.ej. fallback de idioma


# ── Engine ────────────────────────────────────────────────────────────────────

class TTSEngine:
    """Interfaz mínima — todo async porque edge-tts lo es."""

    def __init__(self) -> None:
        if not _EDGE_TTS_OK:
            # No tiramos aquí para permitir que el caller maneje el estado.
            pass

    @property
    def is_configured(self) -> bool:
        return _EDGE_TTS_OK

    async def synthesize(
        self,
        text: str,
        language: str = "es",
        style: str = "sober",
        voice_override: Optional[str] = None,
    ) -> SynthesisResult:
        """Devuelve MP3 + duración + voz usada. Lanza RuntimeError si edge-tts falla."""
        if not _EDGE_TTS_OK:
            raise RuntimeError("edge-tts no instalado (agregar 'edge-tts>=7.0' a requirements.txt)")

        clean = (text or "").strip()
        if not clean:
            # Sin texto no tiene sentido pedirle a TTS — devolvemos MP3 vacío.
            return SynthesisResult(audio_mp3=b"", duration_s=0.0, voice="",
                                   warning="texto vacío — sin audio generado")

        voice, warn = (voice_override, None) if voice_override else pick_voice(language, style)

        communicate = edge_tts.Communicate(clean, voice)
        audio = bytearray()
        last_end_100ns = 0

        async for chunk in communicate.stream():
            kind = chunk.get("type")
            if kind == "audio":
                audio.extend(chunk.get("data", b""))
            elif kind in ("SentenceBoundary", "WordBoundary"):
                # offset y duration vienen en unidades de 100 nanosegundos.
                end = int(chunk.get("offset", 0)) + int(chunk.get("duration", 0))
                if end > last_end_100ns:
                    last_end_100ns = end

        duration_s = last_end_100ns / 10_000_000.0
        if duration_s <= 0 and audio:
            # Fallback heurístico si el servicio no envió boundaries:
            # edge-tts default bitrate ~24 kbps → 3 KB por segundo.
            duration_s = max(1.0, len(audio) / 3000.0)

        return SynthesisResult(
            audio_mp3=bytes(audio),
            duration_s=round(duration_s, 3),
            voice=voice,
            warning=warn,
        )


# ── API de módulo ─────────────────────────────────────────────────────────────

async def synthesize_beat_audio(
    text: str,
    language: str = "es",
    style: str = "sober",
) -> SynthesisResult:
    """Shortcut imperativo para callers async."""
    return await TTSEngine().synthesize(text=text, language=language, style=style)
