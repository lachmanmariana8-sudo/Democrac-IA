"""VideoComposer — ensambla MP4 desde un Storyboard (Fase D).

Pipeline por beat:
  1. Renderea PNG del beat con FrameRenderer.
  2. Usa el MP3 persistido de Fase C si existe; si no, genera silencio.
  3. ffmpeg: PNG loop + audio → mini-MP4 con duración exacta.
Luego concatena todos los mini-MP4s en final.mp4 (copy, sin re-encode).

Usa imageio-ffmpeg para tener un binario portable sin depender del sistema
ni de nixpacks. Funciona igual en Windows, Linux y macOS.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

try:
    import imageio_ffmpeg  # type: ignore
    _FFMPEG_OK = True
except ImportError:  # pragma: no cover
    _FFMPEG_OK = False

from agents.video_producer.models import Beat, Storyboard
from agents.video_producer.renderer import FrameRenderer


class ComposerError(Exception):
    """Falla durante la composición del MP4."""


class VideoComposer:
    """Compone un MP4 desde un Storyboard usando ffmpeg.

    Estado por instancia es mínimo: sólo cachea la ruta al binario ffmpeg.
    La composición en sí es puramente funcional sobre disk I/O.
    """

    def __init__(
        self,
        audio_root: Optional[Path] = None,
        video_root: Optional[Path] = None,
        ffmpeg_exe: Optional[str] = None,
    ):
        if not _FFMPEG_OK and not ffmpeg_exe:
            raise RuntimeError(
                "imageio-ffmpeg no instalado — agregar 'imageio-ffmpeg>=0.5' a requirements.txt"
            )
        self.ffmpeg = ffmpeg_exe or imageio_ffmpeg.get_ffmpeg_exe()
        # Imports tardíos de los roots para permitir tests con override
        from agents.video_producer.video_producer import (
            video_audio_root, video_mp4_root,
        )
        self.audio_root = Path(audio_root) if audio_root else video_audio_root()
        self.video_root = Path(video_root) if video_root else video_mp4_root()

    # ── Entrada pública ────────────────────────────────────────────────
    def compose(self, storyboard: Storyboard, job_id: str) -> Path:
        """Compone el MP4 final para job_id. Devuelve la ruta absoluta al archivo.

        Raises:
            ComposerError: si ffmpeg falla en cualquier paso.
        """
        if not storyboard.beats:
            raise ComposerError("storyboard sin beats — no hay nada que componer")

        out_dir = self.video_root / job_id
        out_dir.mkdir(parents=True, exist_ok=True)
        final_path = out_dir / "final.mp4"

        renderer = FrameRenderer(width=storyboard.width, height=storyboard.height)

        # Usamos tempdir para PNGs y mini-MP4s: se borran automáticamente.
        # Sólo dejamos persistido el final.mp4 en video_root.
        with tempfile.TemporaryDirectory(prefix=f"peirs_vid_{job_id}_") as tmpdir:
            tmp = Path(tmpdir)
            beat_mp4s: List[Path] = []

            for i, beat in enumerate(storyboard.beats):
                png = tmp / f"beat_{i:02d}.png"
                png.write_bytes(renderer.render_png(beat))

                audio = self._resolve_audio_path(job_id, i, beat)
                beat_mp4 = tmp / f"beat_{i:02d}.mp4"
                self._compose_beat(
                    png=png, audio=audio,
                    duration_s=float(beat.duration_s),
                    width=storyboard.width, height=storyboard.height,
                    fps=storyboard.fps, out=beat_mp4,
                )
                beat_mp4s.append(beat_mp4)

            # Concat — el concat demuxer necesita rutas relativas al cwd de ffmpeg.
            concat_txt = tmp / "concat.txt"
            concat_txt.write_text(
                "\n".join(f"file '{p.name}'" for p in beat_mp4s),
                encoding="utf-8",
            )
            self._concat(concat_txt=concat_txt, out=final_path, cwd=tmp)

        return final_path

    # ── Helpers ────────────────────────────────────────────────────────

    def _resolve_audio_path(self, job_id: str, idx: int, beat: Beat) -> Optional[Path]:
        if not beat.has_audio:
            return None
        p = self.audio_root / job_id / f"beat_{idx:02d}.mp3"
        return p if p.exists() else None

    def _compose_beat(
        self,
        *,
        png: Path,
        audio: Optional[Path],
        duration_s: float,
        width: int,
        height: int,
        fps: int,
        out: Path,
    ) -> None:
        """Arma un MP4 de duración exacta para un beat."""
        cmd: List[str] = [
            self.ffmpeg, "-y",
            "-loop", "1", "-framerate", str(fps), "-i", str(png),
        ]
        if audio:
            cmd.extend(["-i", str(audio)])
        else:
            # Silencio sintético con la misma duración que el beat
            cmd.extend([
                "-f", "lavfi", "-t", f"{duration_s:.3f}",
                "-i", "anullsrc=r=44100:cl=stereo",
            ])
        cmd.extend([
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-tune", "stillimage", "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            # Forzamos la duración exacta del beat. Si el audio es más corto,
            # queda silencio al final (no nos molesta para videos de redes).
            "-t", f"{duration_s:.3f}",
            str(out),
        ])
        self._run(cmd, stage="beat_compose")

    def _concat(self, *, concat_txt: Path, out: Path, cwd: Path) -> None:
        """Concatena mini-MP4s en el final sin re-encode (stream copy)."""
        cmd = [
            self.ffmpeg, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt.name),       # relativo al cwd
            "-c", "copy",
            str(out),
        ]
        self._run(cmd, stage="concat", cwd=cwd)

    def _run(self, cmd: List[str], *, stage: str, cwd: Optional[Path] = None) -> None:
        r = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=120,
            cwd=str(cwd) if cwd else None,
        )
        if r.returncode != 0:
            tail = (r.stderr or "").strip().splitlines()[-10:]
            raise ComposerError(f"ffmpeg {stage} failed rc={r.returncode}: {chr(10).join(tail)}")


# ── Helper de módulo ────────────────────────────────────────────────────

def compose_storyboard(storyboard: Storyboard, job_id: str) -> Path:
    """Shortcut: compone un storyboard con los defaults de VideoComposer."""
    return VideoComposer().compose(storyboard=storyboard, job_id=job_id)


def is_available() -> bool:
    """Retorna True si el composer puede ejecutarse (imageio-ffmpeg instalado)."""
    if not _FFMPEG_OK:
        return False
    try:
        # Verificar que el binario existe y responde
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        r = subprocess.run([exe, "-version"], capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False
