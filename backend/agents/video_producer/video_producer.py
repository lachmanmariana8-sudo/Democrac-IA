"""VideoProducer — orquestador del pipeline Guionista → Storyboard → TTS → (Render).

Pipeline (Fases A+B+C):
    findings → Scriptwriter(Claude) → StoryboardBuilder → TTS por beat →
             status=storyboard_ready (con audios persistidos) → [Render MP4]

El render MP4 (frames + audios + transiciones) entra en Fase D (moviepy/ffmpeg).
"""
from __future__ import annotations

import asyncio
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agents.video_producer.models import (
    Beat,
    Storyboard,
    VideoJobRequest,
    VideoJobResult,
    VideoPreset,
)
from agents.video_producer.presets import get_preset_config
from agents.video_producer.scriptwriter import Scriptwriter
from agents.video_producer.storyboard import StoryboardBuilder


def video_audio_root() -> Path:
    """Directorio donde guardamos MP3 por beat. Mismo volumen persistente que peirs.db.

    En Railway: `/data/video_audio/...`. Local dev: `<repo>/data/video_audio/...`.
    """
    override = os.getenv("VIDEO_AUDIO_ROOT")
    if override:
        return Path(override)
    try:
        from db.crud import get_db_path
        return get_db_path().parent / "video_audio"
    except Exception:
        # Fallback: repo_root/data/video_audio
        return Path(__file__).resolve().parents[3] / "data" / "video_audio"


def video_mp4_root() -> Path:
    """Directorio donde guardamos MP4 finales compuestos (Fase D)."""
    override = os.getenv("VIDEO_MP4_ROOT")
    if override:
        return Path(override)
    try:
        from db.crud import get_db_path
        return get_db_path().parent / "video_mp4"
    except Exception:
        return Path(__file__).resolve().parents[3] / "data" / "video_mp4"


COUNTRY_NAMES = {"PER": "Perú", "ARG": "Argentina", "BOL": "Bolivia", "CHL": "Chile"}

CLAUDE_INPUT_COST_PER_MTOK = 3.0
CLAUDE_OUTPUT_COST_PER_MTOK = 15.0


class VideoProducer:
    """Orquestador: findings → guión → storyboard → TTS → [render]."""

    def __init__(
        self,
        llm=None,
        alerts_loader: Optional[Callable[[str, int], List[Dict[str, Any]]]] = None,
        audio_root: Optional[Path] = None,
    ):
        self.llm = llm
        self.scriptwriter = Scriptwriter(llm=llm)
        self.storyboarder = StoryboardBuilder()
        self.alerts_loader = alerts_loader
        self.audio_root = Path(audio_root) if audio_root else video_audio_root()

    async def produce(self, req: VideoJobRequest) -> VideoJobResult:
        t0 = time.monotonic()
        job_id = f"vid_{uuid.uuid4().hex[:10]}"
        country_name = COUNTRY_NAMES.get(req.country_code.upper(), req.country_code)

        preset = req.preset if isinstance(req.preset, VideoPreset) else VideoPreset(req.preset)
        cfg = get_preset_config(preset)
        target_duration = cfg["target_duration_s"]
        # Preset manda: si define max_findings, tiene prioridad sobre lo que pidió el user
        max_findings = cfg["max_findings"] or req.max_findings

        result = VideoJobResult(
            job_id=job_id,
            country_code=req.country_code,
            preset=preset.value,
            status="pending",
            language=req.language,
            style=req.style,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        # 1. FINDINGS
        findings = self._load_findings(req, max_findings=max_findings)
        result.findings_count = len(findings)
        stats = self._compute_stats(findings, req)

        # 2. GUIÓN
        result.status = "scripting"
        script = await self.scriptwriter.compose(
            findings=findings,
            stats=stats,
            country_name=country_name,
            period_days=req.period_days,
            severity_min=req.severity_min,
            language=req.language,
            style=req.style,
            target_duration_s=target_duration,
        )
        result.script = script
        self._accumulate_tokens(result, estimate_script=True)

        # 3. STORYBOARD
        result.status = "storyboarding"
        storyboard = self.storyboarder.build(
            script=script, preset=preset, stats=stats, findings=findings,
        )
        result.storyboard = storyboard

        # 4. TTS por beat (Fase C). En dry_run: se salta para no llamar a Microsoft.
        if not req.dry_run:
            await self._synthesize_storyboard_audio(
                storyboard=storyboard,
                job_id=job_id,
                language=req.language,
                style=req.style,
                warnings=result.warnings,
            )

        result.status = "storyboard_ready"

        # 5. RENDER MP4 — Fase D (ffmpeg via imageio-ffmpeg).
        if req.dry_run:
            result.duration_s = round(time.monotonic() - t0, 2)
            result.warnings.append("dry_run=True — se entrega guión + storyboard, sin TTS ni render.")
            return result

        try:
            from agents.video_producer.composer import VideoComposer, is_available
        except ImportError as e:
            result.warnings.append(f"composer no disponible: {e}")
            result.duration_s = round(time.monotonic() - t0, 2)
            return result

        if not is_available():
            result.warnings.append(
                "imageio-ffmpeg no instalado/operativo — storyboard entregado sin MP4."
            )
            result.duration_s = round(time.monotonic() - t0, 2)
            return result

        result.status = "rendering"
        try:
            composer = VideoComposer()
            # ffmpeg es CPU-bound — a thread para no bloquear el event loop.
            mp4_path = await asyncio.to_thread(
                composer.compose, storyboard, job_id,
            )
            result.video_url = f"/api/video/{job_id}/download"
            result.duration_s = round(time.monotonic() - t0, 2)
            result.status = "completed"
        except Exception as e:
            result.warnings.append(f"render MP4 falló: {type(e).__name__}: {e}")
            result.status = "failed"
            result.error = f"{type(e).__name__}: {e}"
            result.duration_s = round(time.monotonic() - t0, 2)

        return result

    # ── TTS pipeline (Fase C) ──────────────────────────────────────────

    async def _synthesize_storyboard_audio(
        self,
        storyboard: Storyboard,
        job_id: str,
        language: str,
        style: str,
        warnings: List[str],
    ) -> None:
        """Sintetiza MP3 por cada beat con narración. Actualiza beat.duration_s
        para que el video acomode la duración real del audio (solo alarga, no
        acorta — respetamos el mínimo del storyboard).
        """
        try:
            from agents.video_producer.tts import TTSEngine
        except ImportError:
            warnings.append("edge-tts no disponible — storyboard queda sin audio.")
            return

        tts = TTSEngine()
        if not tts.is_configured:
            warnings.append("edge-tts no instalado — storyboard queda sin audio.")
            return

        job_dir = self.audio_root / job_id
        try:
            job_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            warnings.append(f"no se pudo crear {job_dir}: {e}")
            return

        async def _synth(idx: int, beat: Beat) -> None:
            text = (beat.narration or "").strip()
            if not text:
                return
            try:
                r = await tts.synthesize(text=text, language=language, style=style)
            except Exception as e:
                warnings.append(f"TTS falló en beat {idx}: {type(e).__name__}: {e}")
                return
            if not r.audio_mp3:
                return
            try:
                out = job_dir / f"beat_{idx:02d}.mp3"
                out.write_bytes(r.audio_mp3)
            except Exception as e:
                warnings.append(f"no se pudo guardar audio beat {idx}: {e}")
                return
            beat.has_audio = True
            beat.audio_duration_s = r.duration_s
            beat.audio_voice = r.voice
            if r.duration_s > beat.duration_s:
                beat.duration_s = round(r.duration_s, 3)
            if r.warning:
                warnings.append(f"beat {idx}: {r.warning}")

        # Parallel TTS — edge-tts es async y Microsoft tolera pocos calls concurrentes.
        await asyncio.gather(*(_synth(i, b) for i, b in enumerate(storyboard.beats)),
                             return_exceptions=True)

        # Re-total después de los ajustes de duración.
        storyboard.total_duration_s = round(sum(b.duration_s for b in storyboard.beats), 2)

    # ── Helpers ─────────────────────────────────────────────────────────

    def _load_findings(self, req: VideoJobRequest, max_findings: int = 5) -> List[Dict[str, Any]]:
        if not self.alerts_loader:
            return []
        try:
            raw = self.alerts_loader(req.country_code, 500) or []
        except Exception:
            return []

        ranks = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
        min_rank = ranks.get(req.severity_min.lower(), 4)

        cutoff = datetime.now(timezone.utc) - timedelta(days=max(req.period_days, 1))
        filtered: List[Dict[str, Any]] = []
        for a in raw:
            sev_rank = ranks.get(str(a.get("severity", "")).lower(), 0)
            if sev_rank < min_rank:
                continue
            ts_str = a.get("recorded_at") or a.get("published_at") or a.get("created_at")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    if ts < cutoff:
                        continue
                except Exception:
                    pass
            filtered.append(a)

        def _key(a: Dict[str, Any]):
            sev = ranks.get(str(a.get("severity", "")).lower(), 0)
            ts = a.get("recorded_at") or a.get("published_at") or ""
            return (-sev, ts)

        filtered.sort(key=_key, reverse=True)
        return filtered[: max_findings] if max_findings else filtered

    @staticmethod
    def _compute_stats(findings: List[Dict[str, Any]], req: VideoJobRequest) -> Dict[str, Any]:
        stats = {
            "total": len(findings),
            "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0,
            "days_covered": req.period_days,
        }
        for f in findings:
            s = str(f.get("severity", "info")).lower()
            if s in stats:
                stats[s] += 1
        return stats

    @staticmethod
    def _accumulate_tokens(result: VideoJobResult, estimate_script: bool = False):
        # Heurística conservadora. Refinar cuando capturemos tokens reales.
        if estimate_script:
            result.tokens_used["input"] = result.tokens_used.get("input", 0) + 3500
            result.tokens_used["output"] = result.tokens_used.get("output", 0) + 700
        in_tok = result.tokens_used.get("input", 0)
        out_tok = result.tokens_used.get("output", 0)
        result.estimated_cost_usd = round(
            (in_tok / 1_000_000) * CLAUDE_INPUT_COST_PER_MTOK
            + (out_tok / 1_000_000) * CLAUDE_OUTPUT_COST_PER_MTOK,
            4,
        )
