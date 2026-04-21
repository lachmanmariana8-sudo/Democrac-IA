"""
HunterLoader — extrae entries + alerts del backend para un país y período.

Normaliza los entries del observation_store (que tienen shape heterogéneo por
el Hunter) al FindingRef canónico del EliteReport.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from agents.elite_report.models import FindingRef


# Pesos de priorización (alineados con Structurer del ReportDesigner)
SEVERITY_WEIGHT = {
    "critical": 10, "high": 7, "medium": 3, "moderate": 3, "low": 1, "info": 0.5
}
SOURCE_CREDIBILITY = {
    "ooni": 1.5, "idl": 1.4, "jne": 1.3, "onpe": 1.3,
    "elcomercio": 1.0, "gestion": 1.0, "rpp": 1.0,
    "andina": 0.9, "wayka": 0.8, "": 0.5, None: 0.5,
}


class HunterLoader:
    """Extrae entries + alerts del backend con filtro por país y período."""

    def __init__(
        self,
        observation_store: Optional[Dict] = None,
        alerts_loader=None,
    ):
        """
        Args:
            observation_store: dict {cc: session} del backend FastAPI.
            alerts_loader: callable(cc, limit) -> list. Opcional.
        """
        self._store = observation_store
        self._alerts_loader = alerts_loader

    def load(
        self,
        country_code: str,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
    ) -> Tuple[List[FindingRef], int, Dict[str, int]]:
        """
        Retorna: (finding_refs_normalizados, alerts_count, stats_by_severity).

        Filtra por período si se proveen period_start/period_end (ISO dates).
        """
        cc = country_code.upper()
        entries: List[Dict[str, Any]] = []
        if self._store and cc in self._store:
            entries = list(self._store[cc].get("entries", []))

        # Filtro por período
        if period_start or period_end:
            entries = [
                e for e in entries
                if self._in_period(e.get("recorded_at"), period_start, period_end)
            ]

        # Normalizar a FindingRef + agregar priority_score
        now = datetime.now(timezone.utc)
        findings: List[FindingRef] = []
        for e in entries:
            f = self._to_finding_ref(e, now)
            findings.append(f)

        # Ordenar por priority_score descendente
        findings.sort(key=lambda x: -(x.priority_score or 0))

        # Stats por severidad
        sev_dist = Counter((f.severity or "info").lower() for f in findings)
        if "moderate" in sev_dist:
            sev_dist["medium"] = sev_dist.get("medium", 0) + sev_dist.pop("moderate")
        stats = dict(sev_dist)
        stats["total"] = len(findings)

        # Alerts
        alerts_count = 0
        if self._alerts_loader:
            try:
                alerts = self._alerts_loader(cc, limit=500)
                alerts_count = len(alerts)
            except Exception:
                alerts_count = 0

        return findings, alerts_count, stats

    @staticmethod
    def _in_period(recorded_at: Optional[str],
                    period_start: Optional[str],
                    period_end: Optional[str]) -> bool:
        if not recorded_at:
            return True
        rec_day = recorded_at[:10]
        if period_start and rec_day < period_start[:10]:
            return False
        if period_end and rec_day > period_end[:10]:
            return False
        return True

    @staticmethod
    def _priority_score(entry: Dict, now: datetime) -> float:
        import math
        sev = (entry.get("severity") or "low").lower()
        sw = SEVERITY_WEIGHT.get(sev, 1.0)
        try:
            dt_raw = (entry.get("recorded_at") or "").replace("Z", "+00:00")
            if not dt_raw:
                return 0.0
            dt = datetime.fromisoformat(dt_raw)
            days = max(0, (now - dt).total_seconds() / 86400.0)
        except Exception:
            days = 30
        rw = 1.0 + 2.0 * math.exp(-days / 3.0)
        src = (entry.get("hunter_source") or entry.get("source") or "").lower()
        cw = SOURCE_CREDIBILITY.get(src, SOURCE_CREDIBILITY.get(None, 0.5))
        return round(sw * rw * cw, 2)

    @classmethod
    def _to_finding_ref(cls, entry: Dict, now: datetime) -> FindingRef:
        """Normaliza un entry del Hunter a FindingRef."""
        score = cls._priority_score(entry, now)
        return FindingRef(
            entry_id=entry.get("entry_id"),
            finding=(entry.get("finding") or "")[:600],
            category=entry.get("category") or "other",
            severity=entry.get("severity") or "info",
            source_name=entry.get("hunter_source") or entry.get("source"),
            source_title=entry.get("hunter_title") or entry.get("title"),
            source_url=entry.get("evidence_ref") or entry.get("url"),
            recorded_at=entry.get("recorded_at"),
            themes=entry.get("_themes", []) or [],
            priority_score=score,
            phase=entry.get("phase"),
        )
