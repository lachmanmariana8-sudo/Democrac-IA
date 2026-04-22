"""VideoProducer — orquestador del pipeline Guionista → Director → HeyGen."""
from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agents.video_producer.models import (
    VideoJobRequest,
    VideoJobResult,
    VideoScriptRequest,
)
from agents.video_producer.scriptwriter import Scriptwriter
from agents.video_producer.director import Director
from agents.video_producer.heygen_client import HeyGenClient, HeyGenError


COUNTRY_NAMES = {"PER": "Perú", "ARG": "Argentina", "BOL": "Bolivia", "CHL": "Chile"}

# Costo aprox por 1M tokens (Claude Sonnet 4.6)
CLAUDE_INPUT_COST_PER_MTOK = 3.0
CLAUDE_OUTPUT_COST_PER_MTOK = 15.0


class VideoProducer:
    """Orquestador end-to-end: findings → guión → plan → HeyGen render."""

    def __init__(
        self,
        llm=None,
        heygen_api_key: Optional[str] = None,
        alerts_loader: Optional[Callable[[str, int], List[Dict[str, Any]]]] = None,
    ):
        self.llm = llm
        self.scriptwriter = Scriptwriter(llm=llm)
        self.director = Director(llm=llm)
        self.heygen = HeyGenClient(api_key=heygen_api_key)
        self.alerts_loader = alerts_loader

    # ── Entrada principal ───────────────────────────────────────────────
    async def produce(self, req: VideoJobRequest) -> VideoJobResult:
        t0 = time.monotonic()
        job_id = f"vid_{uuid.uuid4().hex[:10]}"
        country_name = COUNTRY_NAMES.get(req.country_code.upper(), req.country_code)

        result = VideoJobResult(
            job_id=job_id,
            country_code=req.country_code,
            status="pending",
            language=req.language,
            style=req.style,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        # 1. FINDINGS
        findings = self._load_findings(req)
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
            target_duration_s=req.target_duration_s,
        )
        result.script = script
        self._accumulate_tokens(result, estimate_script=True)

        # 3. PLAN
        result.status = "planning"
        plan = await self.director.plan(script=script, target_duration_s=req.target_duration_s)
        result.plan = plan
        self._accumulate_tokens(result, estimate_plan=True)

        # 4. HEYGEN (si no es dry_run)
        if req.dry_run:
            result.status = "completed"
            result.duration_s = round(time.monotonic() - t0, 2)
            result.warnings.append("dry_run=True — no se llamó a HeyGen.")
            return result

        if not self.heygen.is_configured():
            result.status = "failed"
            result.error = "HEYGEN_API_KEY no configurada en el entorno."
            return result

        try:
            result.status = "rendering"
            # Concatenamos la narración de todas las escenas para HeyGen (v1: single-shot)
            full_narration = "\n\n".join(s.narration for s in plan.scenes).strip() or script.full_text
            heygen_resp = self.heygen.generate_video(
                script_text=full_narration,
                avatar_id=req.avatar_id,
                voice_id=req.voice_id,
                language=req.language,
                dimension_w=req.dimension_w,
                dimension_h=req.dimension_h,
                background_hex=plan.scenes[0].background_value if plan.scenes else "#0f4f4b",
                title=req.title or f"PEIRS Video — {country_name} — {result.generated_at[:10]}",
            )
            result.heygen_video_id = heygen_resp["video_id"]
            result.heygen_status = "submitted"
            # NO bloqueamos esperando el render (30-120s). El frontend poll.
        except HeyGenError as e:
            result.status = "failed"
            result.error = f"HeyGen: {e}"
            return result
        except Exception as e:
            result.status = "failed"
            result.error = f"{type(e).__name__}: {e}"
            return result

        result.status = "rendering"
        result.duration_s = round(time.monotonic() - t0, 2)
        return result

    # ── Polling utilitario ──────────────────────────────────────────────
    def fetch_status(self, heygen_video_id: str) -> Dict[str, Any]:
        """Expuesto para el endpoint de polling."""
        return self.heygen.get_status(heygen_video_id)

    # ── Helpers ─────────────────────────────────────────────────────────
    def _load_findings(self, req: VideoJobRequest) -> List[Dict[str, Any]]:
        """Carga findings desde alerts_loader. Aplica filtros severity/período."""
        if not self.alerts_loader:
            return []
        try:
            raw = self.alerts_loader(req.country_code, 500) or []
        except Exception:
            return []

        allowed = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
        min_rank = allowed.get(req.severity_min.lower(), 4)

        # Ventana temporal
        from datetime import datetime as _dt, timedelta as _td
        cutoff = _dt.now(timezone.utc) - _td(days=max(req.period_days, 1))

        filtered = []
        for a in raw:
            sev_rank = allowed.get(str(a.get("severity", "")).lower(), 0)
            if sev_rank < min_rank:
                continue
            ts_str = a.get("recorded_at") or a.get("published_at") or a.get("created_at")
            if ts_str:
                try:
                    ts = _dt.fromisoformat(str(ts_str).replace("Z", "+00:00"))
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    if ts < cutoff:
                        continue
                except Exception:
                    pass
            filtered.append(a)

        # Ordenar por severidad desc + fecha desc
        def _key(a):
            sev = allowed.get(str(a.get("severity", "")).lower(), 0)
            ts = a.get("recorded_at") or a.get("published_at") or ""
            return (-sev, ts)
        filtered.sort(key=_key, reverse=True)  # más reciente primero dentro de severidad
        return filtered[: req.max_findings]

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
    def _accumulate_tokens(result: VideoJobResult, estimate_script: bool = False, estimate_plan: bool = False):
        """Heurística conservadora — refinar cuando capturemos tokens reales del LLM."""
        if estimate_script:
            result.tokens_used["input"] = result.tokens_used.get("input", 0) + 3500
            result.tokens_used["output"] = result.tokens_used.get("output", 0) + 700
        if estimate_plan:
            result.tokens_used["input"] = result.tokens_used.get("input", 0) + 1800
            result.tokens_used["output"] = result.tokens_used.get("output", 0) + 500
        in_tok = result.tokens_used.get("input", 0)
        out_tok = result.tokens_used.get("output", 0)
        result.estimated_cost_usd = round(
            (in_tok / 1_000_000) * CLAUDE_INPUT_COST_PER_MTOK
            + (out_tok / 1_000_000) * CLAUDE_OUTPUT_COST_PER_MTOK,
            4,
        )
