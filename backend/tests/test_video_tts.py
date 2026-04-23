"""Tests del TTSEngine del Video Producer v2 (Fase C).

Evitan llamadas reales a Microsoft edge-tts por default. Usamos asyncio.run
para no requerir pytest-asyncio como nuevo dep del proyecto.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.video_producer.tts import (  # noqa: E402
    TTSEngine,
    SynthesisResult,
    VOICES,
    pick_voice,
)


# ── pick_voice (sin I/O, 100% sync) ───────────────────────────────────────────

class TestPickVoice:
    def test_es_sober_devuelve_voz_peruana(self):
        voice, warn = pick_voice("es", "sober")
        assert voice.startswith("es-PE-"), f"esperaba voz peruana, obtuvo {voice!r}"
        assert warn is None

    def test_es_explainer_es_camila(self):
        voice, _ = pick_voice("es", "explainer")
        assert voice == "es-PE-CamilaNeural"

    def test_en_urgent_usa_aria(self):
        voice, warn = pick_voice("en", "urgent")
        assert voice == "en-US-AriaNeural"
        assert warn is None

    def test_pt_sober_usa_antonio(self):
        voice, _ = pick_voice("pt", "sober")
        assert voice == "pt-BR-AntonioNeural"

    def test_quechua_cae_a_espanol_con_warning(self):
        voice, warn = pick_voice("qu", "sober")
        assert voice.startswith("es-PE-")
        assert warn is not None
        assert "fallback" in warn.lower()

    def test_style_desconocido_cae_a_sober(self):
        voice, _ = pick_voice("es", "nonsense_style")
        assert voice == VOICES["es"]["sober"]


# ── TTSEngine (sin red) ───────────────────────────────────────────────────────

class TestTTSEngineLocal:
    def test_is_configured_es_booleano(self):
        engine = TTSEngine()
        assert isinstance(engine.is_configured, bool)

    def test_texto_vacio_no_llama_al_servicio(self):
        pytest.importorskip("edge_tts")
        engine = TTSEngine()
        r = asyncio.run(engine.synthesize("   ", language="es", style="sober"))
        assert isinstance(r, SynthesisResult)
        assert r.audio_mp3 == b""
        assert r.duration_s == 0.0
        assert r.warning and "vac" in r.warning.lower()

    def test_sin_edge_tts_lanza_runtime_error(self, monkeypatch):
        import agents.video_producer.tts as tts_mod
        monkeypatch.setattr(tts_mod, "_EDGE_TTS_OK", False)
        engine = tts_mod.TTSEngine()
        with pytest.raises(RuntimeError, match="edge-tts"):
            asyncio.run(engine.synthesize("hola", language="es"))


# ── Integración VideoProducer con TTS mockeado ───────────────────────────────

class TestVideoProducerAudio:
    def test_dry_run_no_invoca_tts(self):
        """dry_run=True salta TTS y deja beats sin audio."""
        from agents.video_producer import VideoProducer, VideoJobRequest, VideoPreset

        producer = VideoProducer(llm=None, alerts_loader=None)
        req = VideoJobRequest(
            country_code="PER",
            preset=VideoPreset.ALERT_30S,
            dry_run=True,
        )
        result = asyncio.run(producer.produce(req))
        assert result.status == "storyboard_ready"
        assert result.storyboard is not None
        assert all(not b.has_audio for b in result.storyboard.beats)
        assert any("dry_run" in w.lower() for w in result.warnings)

    def test_persiste_mp3_con_engine_mockeado(self, tmp_path, monkeypatch):
        """Path completo: un beat con narración → archivo MP3 en audio_root."""
        from agents.video_producer import VideoProducer, VideoJobRequest, VideoPreset
        from agents.video_producer.models import Storyboard
        import agents.video_producer.tts as tts_mod

        fake_audio = b"ID3\x03" + b"\x00" * 4096

        class _FakeEngine:
            @property
            def is_configured(self): return True
            async def synthesize(self, text, language="es", style="sober", voice_override=None):
                from agents.video_producer.tts import SynthesisResult
                return SynthesisResult(
                    audio_mp3=fake_audio, duration_s=3.5, voice="es-PE-AlexNeural",
                )

        monkeypatch.setattr(tts_mod, "TTSEngine", _FakeEngine)

        producer = VideoProducer(llm=None, alerts_loader=None, audio_root=tmp_path)
        req = VideoJobRequest(
            country_code="PER", preset=VideoPreset.ALERT_30S, dry_run=False,
        )
        result = asyncio.run(producer.produce(req))
        assert result.status == "storyboard_ready"
        assert result.storyboard is not None

        sb: Storyboard = result.storyboard
        audio_beats = [b for b in sb.beats if b.has_audio]
        assert len(audio_beats) >= 1, (
            "ningún beat tiene audio — revisar que los beats del preset tengan narración"
        )

        job_dir = tmp_path / result.job_id
        assert job_dir.is_dir()
        files = sorted(job_dir.glob("beat_*.mp3"))
        assert len(files) == len(audio_beats)
        for f in files:
            assert f.read_bytes() == fake_audio

        # Duración del beat ajustada al audio (solo alarga — el storyboard respeta mínimos).
        for b in audio_beats:
            assert b.audio_duration_s == 3.5
            assert b.audio_voice == "es-PE-AlexNeural"
            assert b.duration_s >= 3.5

    def test_engine_no_configurado_warnea_y_no_crashea(self, tmp_path, monkeypatch):
        """Si edge-tts no está disponible, produce() no crashea — solo agrega warning."""
        from agents.video_producer import VideoProducer, VideoJobRequest, VideoPreset
        import agents.video_producer.tts as tts_mod

        class _DeadEngine:
            @property
            def is_configured(self): return False
            async def synthesize(self, *a, **kw): raise AssertionError("should not be called")

        monkeypatch.setattr(tts_mod, "TTSEngine", _DeadEngine)

        producer = VideoProducer(llm=None, alerts_loader=None, audio_root=tmp_path)
        req = VideoJobRequest(country_code="PER", preset=VideoPreset.ALERT_30S, dry_run=False)
        result = asyncio.run(producer.produce(req))
        assert result.status == "storyboard_ready"
        assert any("edge-tts" in w.lower() for w in result.warnings)
        # Sin ningún audio generado
        assert all(not b.has_audio for b in (result.storyboard.beats if result.storyboard else []))


# ── Test opcional con red (marker @network para correr aparte) ───────────────

@pytest.mark.network
def test_sintesis_real_de_frase_corta():
    """Real round-trip a Microsoft. Correr con `pytest -m network` explícito."""
    pytest.importorskip("edge_tts")
    engine = TTSEngine()
    r = asyncio.run(engine.synthesize("Hola, esto es una prueba.", language="es", style="sober"))
    assert len(r.audio_mp3) > 5000, "MP3 sospechosamente chico"
    # MP3 puede arrancar con tag ID3 o con un sync frame 0xFFE*.
    # 0xFF + (0xE0..0xFF) son los sync words válidos de MPEG Audio Layer III.
    head = r.audio_mp3[:2]
    assert head[:3] == b"ID3" or (head[0] == 0xFF and (head[1] & 0xE0) == 0xE0), \
        f"no parece MP3, primeros bytes: {r.audio_mp3[:4]!r}"
    assert 0.8 <= r.duration_s <= 5.0, f"duración fuera de rango: {r.duration_s}s"
    assert r.voice.startswith("es-PE-")
