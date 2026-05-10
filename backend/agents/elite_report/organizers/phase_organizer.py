"""
PhaseOrganizer — agrupa findings del Hunter por las 9 fases del ciclo electoral.

Las fases vienen del sistema PEIRS (OBS_PHASES en frontend/App.jsx):
preparatory, pre_campaign, campaign, electoral_silence, election_day,
counting_tabulation, post_election, dispute_resolution, completed.

Cuando un finding no tiene `phase` explícito, se infiere por fecha del
finding cruzada con el calendario electoral del país (para Perú 2026 tenemos
fechas conocidas del proceso).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Dict, List, Optional

from agents.elite_report.models import FindingRef, PhaseEvidence


# Etiquetas humanas de las fases
PHASE_LABELS = {
    "preparatory":         "📋 Preparatorio",
    "pre_campaign":        "📣 Pre-campaña",
    "campaign":            "🗣️ Campaña electoral",
    "electoral_silence":   "🤫 Silencio / veda electoral",
    "election_day":        "🗳️ Jornada electoral",
    "counting_tabulation": "🔢 Escrutinio y cómputo",
    "post_election":       "📊 Post-electoral",
    "dispute_resolution":  "⚖️ Resolución de disputas",
    "completed":           "✅ Ciclo completo",
}

# Orden canónico
PHASE_ORDER = [
    "preparatory", "pre_campaign", "campaign", "electoral_silence",
    "election_day", "counting_tabulation", "post_election",
    "dispute_resolution", "completed",
]


# Sprint 2: el calendario ahora viene del CountryAdapter del pais. Se mantiene
# PERU_2026_CALENDAR como const exportada para backward compat con tests u
# otros callers que lo importen directamente; valor identico al del adapter.
PERU_2026_CALENDAR = {
    "preparatory":         (date(2025, 10, 12), date(2026,  1, 11)),
    "pre_campaign":        (date(2026,  1, 12), date(2026,  2, 11)),
    "campaign":            (date(2026,  2, 12), date(2026,  4,  9)),
    "electoral_silence":   (date(2026,  4, 10), date(2026,  4, 11)),
    "election_day":        (date(2026,  4, 12), date(2026,  4, 12)),
    "counting_tabulation": (date(2026,  4, 13), date(2026,  4, 20)),
    "post_election":       (date(2026,  4, 21), date(2026,  5, 15)),
    "dispute_resolution":  (date(2026,  5, 16), date(2026,  6, 10)),
    "completed":           (date(2026,  6, 11), date(2027,  1,  1)),
}


class PhaseOrganizer:
    """Agrupa findings por fase electoral."""

    def __init__(self, country_code: str = "PER"):
        from agents.elite_report.country_adapters import get_adapter
        self.country_code = country_code.upper()
        self.calendar = get_adapter(self.country_code).electoral_calendar()

    def organize(self, findings: List[FindingRef]) -> Dict[str, PhaseEvidence]:
        """Retorna dict {phase_id: PhaseEvidence}. Incluye todas las fases del
        calendario aunque no tengan findings (para mostrar fases vacías en viz)."""
        buckets: Dict[str, List[FindingRef]] = defaultdict(list)

        for f in findings:
            phase = self._assign_phase(f)
            buckets[phase].append(f)

        result: Dict[str, PhaseEvidence] = {}
        for phase_id in PHASE_ORDER:
            bucket = buckets.get(phase_id, [])
            if not bucket and phase_id not in self.calendar:
                # Fase sin calendario conocido y sin findings — no la incluimos
                continue

            # Stats
            sev_counter = Counter((f.severity or "info").lower() for f in bucket)
            if "moderate" in sev_counter:
                sev_counter["medium"] += sev_counter.pop("moderate")

            # Temas dominantes (top 3)
            theme_counter: Counter = Counter()
            for f in bucket:
                for t in f.themes:
                    theme_counter[t] += 1
            dominant_themes = [t for t, _ in theme_counter.most_common(3)]

            # Rango temporal
            dates = [f.recorded_at[:10] for f in bucket if f.recorded_at]
            period_start = min(dates) if dates else None
            period_end = max(dates) if dates else None
            if not period_start and phase_id in self.calendar:
                period_start = self.calendar[phase_id][0].isoformat()
                period_end = self.calendar[phase_id][1].isoformat()

            result[phase_id] = PhaseEvidence(
                phase_id=phase_id,
                phase_label=PHASE_LABELS.get(phase_id, phase_id),
                findings=sorted(bucket, key=lambda x: -(x.priority_score or 0)),
                total_count=len(bucket),
                critical_count=sev_counter.get("critical", 0),
                high_count=sev_counter.get("high", 0),
                medium_count=sev_counter.get("medium", 0),
                dominant_themes=dominant_themes,
                period_start=period_start,
                period_end=period_end,
            )

        return result

    def _assign_phase(self, f: FindingRef) -> str:
        """Si el finding tiene phase explícito, lo usa. Si no, lo infiere por fecha."""
        if f.phase and f.phase in PHASE_ORDER:
            return f.phase

        # Inferir por fecha si hay calendario
        if not f.recorded_at or not self.calendar:
            return "preparatory"  # fallback conservador
        try:
            rec_day = datetime.strptime(f.recorded_at[:10], "%Y-%m-%d").date()
        except Exception:
            return "preparatory"

        for phase_id in PHASE_ORDER:
            if phase_id not in self.calendar:
                continue
            start, end = self.calendar[phase_id]
            if start <= rec_day <= end:
                return phase_id

        # Más allá del calendario
        if self.calendar:
            first_phase_start = min(s for s, _ in self.calendar.values())
            if rec_day < first_phase_start:
                return "preparatory"
        return "completed"

    def timeline_summary(self, phase_evidence: Dict[str, PhaseEvidence]) -> List[Dict]:
        """Genera resumen compacto para visualizaciones phase_timeline.
        Retorna [{phase, label, total, critical, high, medium, themes}]."""
        out = []
        for phase_id in PHASE_ORDER:
            pe = phase_evidence.get(phase_id)
            if not pe:
                continue
            out.append({
                "phase": phase_id,
                "label": pe.phase_label,
                "total": pe.total_count,
                "critical": pe.critical_count,
                "high": pe.high_count,
                "medium": pe.medium_count,
                "themes": pe.dominant_themes,
                "period_start": pe.period_start,
                "period_end": pe.period_end,
            })
        return out
