"""Tests del VideoComposer del Video Producer v2 (Fase D).

Los tests reales con ffmpeg están marcados @ffmpeg y skippeados por default
(corrida real toma 2-10s). El resto son puramente sync + mocks.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestIsAvailable:
    def test_devuelve_booleano(self):
        from agents.video_producer.composer import is_available
        assert isinstance(is_available(), bool)

    def test_false_si_imageio_ffmpeg_ausente(self, monkeypatch):
        import agents.video_producer.composer as comp_mod
        monkeypatch.setattr(comp_mod, "_FFMPEG_OK", False)
        assert comp_mod.is_available() is False


class TestComposerInit:
    def test_lanza_sin_ffmpeg(self, monkeypatch):
        import agents.video_producer.composer as comp_mod
        monkeypatch.setattr(comp_mod, "_FFMPEG_OK", False)
        with pytest.raises(RuntimeError, match="imageio-ffmpeg"):
            comp_mod.VideoComposer()

    def test_acepta_ffmpeg_explicito(self, tmp_path):
        """Podés pasar el binario vía ctor (útil para tests que mockean subprocess)."""
        from agents.video_producer.composer import VideoComposer
        c = VideoComposer(
            audio_root=tmp_path / "a",
            video_root=tmp_path / "v",
            ffmpeg_exe="/fake/ffmpeg",
        )
        assert c.ffmpeg == "/fake/ffmpeg"
        assert c.audio_root == tmp_path / "a"
        assert c.video_root == tmp_path / "v"


class TestComposeErrores:
    def test_storyboard_vacio_lanza(self, tmp_path):
        from agents.video_producer.composer import VideoComposer, ComposerError
        from agents.video_producer.models import Storyboard, VideoPreset

        c = VideoComposer(
            audio_root=tmp_path / "a", video_root=tmp_path / "v",
            ffmpeg_exe="/fake/ffmpeg",
        )
        sb = Storyboard(preset=VideoPreset.ALERT_30S, beats=[], total_duration_s=0.0)
        with pytest.raises(ComposerError, match="sin beats"):
            c.compose(sb, job_id="test")

    def test_ffmpeg_falla_lanza_composer_error(self, tmp_path, monkeypatch):
        """Si subprocess.run devuelve rc != 0, ComposerError con stderr tail."""
        import subprocess as sp
        from agents.video_producer.composer import VideoComposer, ComposerError
        from agents.video_producer.models import Beat, Storyboard, VideoPreset

        def fake_run(*a, **kw):
            class _R:
                returncode = 1
                stdout = ""
                stderr = "fake: Invalid codec\nline2\nline3"
            return _R()
        monkeypatch.setattr(sp, "run", fake_run)

        c = VideoComposer(
            audio_root=tmp_path / "a", video_root=tmp_path / "v",
            ffmpeg_exe="/fake/ffmpeg",
        )
        sb = Storyboard(
            preset=VideoPreset.ALERT_30S,
            beats=[Beat(beat_id="b0", kind="intro", duration_s=1.0, visual="solid_bg")],
            total_duration_s=1.0,
        )
        with pytest.raises(ComposerError, match="ffmpeg"):
            c.compose(sb, job_id="test_fail")


# ── Test con ffmpeg real (marker @ffmpeg, skippeado por default) ─────────────

@pytest.mark.ffmpeg
class TestRealCompose:
    """Compone un MP4 real con ffmpeg. ~2-5s de ejecución."""

    def test_compose_de_2_beats_produce_mp4_valido(self, tmp_path):
        pytest.importorskip("imageio_ffmpeg")
        pytest.importorskip("PIL")

        from agents.video_producer.composer import VideoComposer, is_available
        from agents.video_producer.models import Beat, Overlay, Storyboard, VideoPreset

        if not is_available():
            pytest.skip("ffmpeg no operativo")

        sb = Storyboard(
            preset=VideoPreset.ALERT_30S,
            width=1080, height=1920, fps=30,
            beats=[
                Beat(
                    beat_id="b00", kind="intro", duration_s=1.5,
                    visual="solid_bg",
                    overlays=[Overlay(kind="title", text="Test", position="center")],
                ),
                Beat(
                    beat_id="b01", kind="outro", duration_s=1.5,
                    visual="solid_bg",
                    overlays=[Overlay(kind="cta", text="democracia.ar", position="center")],
                ),
            ],
            total_duration_s=3.0,
        )

        # Sin audio_root con archivos → beats sin audio → ffmpeg genera silencio
        composer = VideoComposer(
            audio_root=tmp_path / "audio_empty",
            video_root=tmp_path / "video",
        )
        out = composer.compose(sb, job_id="t_real")

        assert out.exists()
        assert out.suffix == ".mp4"
        assert out.stat().st_size > 10_000, "MP4 sospechosamente chico"
        # Magic bytes: ISO Base Media — [4 bytes size]"ftyp"
        head = out.read_bytes()[:12]
        assert b"ftyp" in head, f"no parece MP4 ISO: {head!r}"
