"""VideoProducer — orquestador del pipeline Guionista → Storyboard → (Render).

Pipeline actual (Fase A):
    findings → Scriptwriter(Claude) → StoryboardBuilder → status=storyboard_ready

El renderizado (frames + TTS + MP4) se agrega en Fases B/C/D.
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional

from agents.video_producer.models import (
    VideoJobRequest,
    VideoJobResult,
    VideoPreset,
)
from agents.video_producer.presets import get_preset_config
from agents.video_producer.scriptwriter import Scriptwriter
from agents.video_producer.storyboard import StoryboardBuilder


COUNTRY_NAMES = {"PER": "Perú", "ARG": "Argentina", "BOL": "Bolivia", "CHL": "Chile"}

CLAUDE_INPUT_COST_PER_MTOK = 3.0
CLAUDE_OUTPUT_COST_PER_MTOK = 15.0


class VideoProducer:
    """Orquestador: findings → guión → storyboard → [render]."""

    def __init__(
        self,
        llm=None,
        alerts_loader: Optional[Callable[[str, int], List[Dict[str, Any]]]] = None,
    ):
        self.llm = llm
        self.scriptwriter = Scriptwriter(llm=llm)
        self.storyboarder = StoryboardBuilder()
        self.alerts_loader = alerts_loader

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
        result.status = "storyboard_ready"

        # 4. RENDER — Fase B/C/D implementarán esto.
        if req.dry_run:
            result.duration_s = round(time.monotonic() - t0, 2)
            result.warnings.append("dry_run=True — se entrega guión + storyboard, sin render.")
            return result

        result.warnings.append(
            "Render en desarrollo (Fase B–D). Por ahora se entrega guión + storyboard para preview."
        )
        result.duration_s = round(time.monotonic() - t0, 2)
        return result

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
