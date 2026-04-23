"""StoryboardBuilder: traduce VideoScript + preset → Storyboard.

Fase A: rule-based (sin LLM). Recorre la secuencia de beat_types del preset,
asigna duración proporcional según pesos, y completa overlays/visuales desde
el script + stats + findings.

Fase B refinará con LLM si hace falta (e.g., seleccionar cuál incident va en
qué beat, generar cita destacada, etc.).
"""
from __future__ import annotations

from typing import Any, Dict, List

from agents.video_producer.models import (
    Beat,
    Overlay,
    Storyboard,
    VideoPreset,
    VideoScript,
)
from agents.video_producer.presets import get_preset_config


# Pesos para distribuir la duración total entre beats.
# intro/outro cortos, incident/timeline largos, stat/quote intermedios.
BEAT_WEIGHTS: Dict[str, float] = {
    "intro":    0.6,
    "stat":     1.0,
    "incident": 1.4,
    "timeline": 1.2,
    "quote":    1.2,
    "outro":    0.6,
}


class StoryboardBuilder:
    def build(
        self,
        script: VideoScript,
        preset: VideoPreset,
        stats: Dict[str, Any],
        findings: List[Dict[str, Any]],
    ) -> Storyboard:
        cfg = get_preset_config(preset)
        width, height = cfg["dimensions"]
        total_duration = float(cfg["target_duration_s"])
        beat_types: List[str] = cfg["beat_types"]

        total_weight = sum(BEAT_WEIGHTS.get(t, 1.0) for t in beat_types)
        unit = total_duration / total_weight if total_weight > 0 else total_duration / max(len(beat_types), 1)

        beats: List[Beat] = []
        finding_idx = 0
        for i, btype in enumerate(beat_types):
            dur = round(unit * BEAT_WEIGHTS.get(btype, 1.0), 2)
            beat = self._build_beat(
                idx=i, btype=btype, dur=dur,
                script=script, stats=stats, findings=findings,
                finding_idx=finding_idx,
            )
            if btype == "incident":
                finding_idx += 1
            beats.append(beat)

        return Storyboard(
            preset=preset,
            beats=beats,
            total_duration_s=round(sum(b.duration_s for b in beats), 2),
            width=width,
            height=height,
            fps=30,
        )

    # ── Beats individuales ─────────────────────────────────────────────

    def _build_beat(
        self,
        idx: int,
        btype: str,
        dur: float,
        script: VideoScript,
        stats: Dict[str, Any],
        findings: List[Dict[str, Any]],
        finding_idx: int = 0,
    ) -> Beat:
        beat_id = f"b{idx:02d}_{btype}"

        if btype == "intro":
            return Beat(
                beat_id=beat_id, kind="intro", duration_s=dur,
                narration=script.hook,
                visual="solid_bg",
                overlays=[
                    Overlay(kind="title", text="DemocracIA / PEIRS",
                            position="center", start_s=0.0, duration_s=dur),
                    Overlay(kind="source", text="Observación electoral · Perú 2026",
                            position="bottom", start_s=0.5, duration_s=max(dur - 0.5, 0.5)),
                ],
            )

        if btype == "stat":
            return Beat(
                beat_id=beat_id, kind="stat", duration_s=dur,
                narration=script.context,
                visual="kpi_grid",
                visual_data={
                    "kpis": [
                        {"label": "Hallazgos",  "value": stats.get("total", 0)},
                        {"label": "Críticos",   "value": stats.get("critical", 0)},
                        {"label": "Altos",      "value": stats.get("high", 0)},
                        {"label": "Días",       "value": stats.get("days_covered", 0)},
                    ],
                },
            )

        if btype == "incident":
            f = findings[finding_idx] if finding_idx < len(findings) else {}
            title = str(f.get("title") or f.get("summary") or "Hallazgo registrado")
            source = str(f.get("source") or "Fuente registrada")
            return Beat(
                beat_id=beat_id, kind="incident", duration_s=dur,
                narration=_truncate(script.findings_narrative, 600),
                visual="solid_bg",
                overlays=[
                    Overlay(kind="lower_third",
                            text=_truncate(title, 120),
                            secondary_text=_truncate(source, 80),
                            position="bottom",
                            start_s=0.5, duration_s=max(dur - 0.5, 0.5)),
                ],
            )

        if btype == "timeline":
            events = []
            for f in findings[:6]:
                ts = str(f.get("recorded_at") or f.get("published_at") or "")[:10]
                label = _truncate(str(f.get("title") or f.get("summary") or ""), 60)
                if ts or label:
                    events.append({"t": ts, "label": label})
            return Beat(
                beat_id=beat_id, kind="timeline", duration_s=dur,
                narration="",
                visual="timeline",
                visual_data={"events": events},
            )

        if btype == "quote":
            text = _truncate(script.findings_narrative, 220) or _truncate(script.context, 220)
            return Beat(
                beat_id=beat_id, kind="quote", duration_s=dur,
                narration="",
                visual="quote_panel",
                overlays=[
                    Overlay(kind="quote", text=text, position="center",
                            start_s=0.0, duration_s=dur),
                ],
            )

        # outro
        return Beat(
            beat_id=beat_id, kind="outro", duration_s=dur,
            narration=script.closing,
            visual="solid_bg",
            overlays=[
                Overlay(kind="cta", text="democracia.ar", position="center",
                        start_s=0.0, duration_s=dur),
            ],
        )


def _truncate(text: str, n: int) -> str:
    text = (text or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"
