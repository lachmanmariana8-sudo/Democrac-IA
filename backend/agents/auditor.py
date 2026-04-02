"""
DEMOCRAC.IA / PEIRS — Agente Auditor Mínimo
============================================
Audita la calidad e integridad de los hallazgos de campo en tiempo real.
Detecta anomalías estadísticas que indican posible inundación de entradas falsas,
inconsistencias de severidad, y silencios sospechosos durante períodos de alta actividad.

Versión mínima pre-elección — foco en dimensión 1: Auditoría de hallazgos de campo.
Activado event-driven desde los endpoints de observación y scheduled cada 30 minutos.

Uso:
    from agents.auditor import AuditAgent
    agent = AuditAgent()
    result = agent.audit_session(session, country_code="PER")
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import statistics


# ── Constantes de thresholds ──────────────────────────────────────────────────

# Más de N entradas en los últimos M minutos → posible inundación
FLOOD_ENTRIES_THRESHOLD  = 10   # entradas
FLOOD_WINDOW_MINUTES     = 15   # ventana de tiempo

# Si >X% de entradas son del mismo observer_id → concentración sospechosa
SINGLE_OBSERVER_RATIO    = 0.7

# Si >X% tienen categoria fraud_allegation sin evidencia → calidad baja
UNVERIFIED_FRAUD_RATIO   = 0.6

# Severidad crítica sin evidencia adjunta
CRITICAL_NO_EVIDENCE_LIMIT = 3  # máximo tolerable

# Si el gap entre entradas supera esto durante elección activa → silencio sospechoso
SILENCE_GAP_MINUTES      = 90


class AuditFinding:
    """Un hallazgo individual del auditor."""
    def __init__(self, code: str, level: str, message: str, detail: Any = None):
        self.code    = code     # identificador del tipo de anomalía
        self.level   = level    # "warning" | "alert" | "critical"
        self.message = message
        self.detail  = detail
        self.ts      = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        return {
            "code": self.code, "level": self.level,
            "message": self.message, "detail": self.detail,
            "detected_at": self.ts,
        }


class AuditResult:
    def __init__(self, session_id: str, country_code: str):
        self.session_id   = session_id
        self.country_code = country_code
        self.findings: List[AuditFinding] = []
        self.audit_score  = 1.0   # 1.0 = integridad máxima, 0.0 = anomalía grave
        self.audited_at   = datetime.now(timezone.utc).isoformat()
        self.entries_analyzed = 0

    def add(self, finding: AuditFinding) -> None:
        self.findings.append(finding)
        # Penalizar score según nivel
        penalties = {"warning": 0.05, "alert": 0.15, "critical": 0.35}
        self.audit_score = max(0.0, self.audit_score - penalties.get(finding.level, 0))

    @property
    def has_critical(self) -> bool:
        return any(f.level == "critical" for f in self.findings)

    @property
    def summary(self) -> str:
        if not self.findings:
            return "OK — Sin anomalías detectadas."
        levels = {"critical": 0, "alert": 0, "warning": 0}
        for f in self.findings:
            levels[f.level] = levels.get(f.level, 0) + 1
        parts = [f"{v} {k}" for k, v in levels.items() if v]
        return f"Anomalías detectadas: {', '.join(parts)}. Score de integridad: {self.audit_score:.2f}/1.00"

    def to_dict(self) -> Dict:
        return {
            "session_id":      self.session_id,
            "country_code":    self.country_code,
            "audit_score":     round(self.audit_score, 3),
            "entries_analyzed": self.entries_analyzed,
            "findings_count":  len(self.findings),
            "has_critical":    self.has_critical,
            "summary":         self.summary,
            "findings":        [f.to_dict() for f in self.findings],
            "audited_at":      self.audited_at,
        }


class AuditAgent:
    """
    Agente Auditor mínimo — dimensión 1: auditoría de hallazgos de campo.
    Sin dependencias externas. Análisis estadístico puro sobre los entries de la sesión.
    """

    def audit_session(self, session: Dict, country_code: str = "") -> AuditResult:
        """
        Audita la sesión completa de observación.
        session: el dict de observation_store[country_code]
        """
        sid    = session.get("session_id", "unknown")
        result = AuditResult(session_id=sid, country_code=country_code)
        entries: List[Dict] = session.get("entries", [])
        result.entries_analyzed = len(entries)

        if not entries:
            return result

        now = datetime.now(timezone.utc)

        # ── Check 1: Inundación de entradas (flood detection) ─────────────────
        window_start = now - timedelta(minutes=FLOOD_WINDOW_MINUTES)
        recent = []
        for e in entries:
            ts_str = e.get("submitted_at") or e.get("timestamp") or ""
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts >= window_start:
                    recent.append(e)
            except (ValueError, AttributeError):
                pass

        if len(recent) >= FLOOD_ENTRIES_THRESHOLD:
            result.add(AuditFinding(
                code="FLOOD_DETECTED",
                level="critical",
                message=f"{len(recent)} entradas en los últimos {FLOOD_WINDOW_MINUTES} min — posible inundación coordinada.",
                detail={"entries_in_window": len(recent), "window_minutes": FLOOD_WINDOW_MINUTES},
            ))

        # ── Check 2: Concentración de un solo observador ──────────────────────
        observer_counts: Dict[str, int] = {}
        for e in entries:
            oid = e.get("observer_id") or "unknown"
            observer_counts[oid] = observer_counts.get(oid, 0) + 1

        if observer_counts:
            max_count = max(observer_counts.values())
            max_obs   = max(observer_counts, key=lambda k: observer_counts[k])
            ratio     = max_count / len(entries)
            if ratio >= SINGLE_OBSERVER_RATIO and len(entries) >= 5:
                result.add(AuditFinding(
                    code="SINGLE_OBSERVER_CONCENTRATION",
                    level="alert",
                    message=f"Observador '{max_obs}' generó {max_count}/{len(entries)} entradas ({ratio:.0%}) — concentración sospechosa.",
                    detail={"observer_id": max_obs, "count": max_count, "ratio": round(ratio, 3)},
                ))

        # ── Check 3: fraud_allegation sin evidencia ───────────────────────────
        frauds = [e for e in entries if e.get("category") == "fraud_allegation"]
        frauds_no_ev = [e for e in frauds if not e.get("has_evidence") and not e.get("verified")]
        if frauds and len(frauds_no_ev) / len(frauds) >= UNVERIFIED_FRAUD_RATIO:
            result.add(AuditFinding(
                code="FRAUD_ALLEGATIONS_UNVERIFIED",
                level="alert",
                message=f"{len(frauds_no_ev)}/{len(frauds)} alegaciones de fraude sin evidencia adjunta ni verificación.",
                detail={"unverified_count": len(frauds_no_ev), "total_fraud": len(frauds)},
            ))

        # ── Check 4: Críticos sin evidencia ──────────────────────────────────
        crit_no_ev = [
            e for e in entries
            if e.get("severity") == "critical"
            and not e.get("has_evidence")
            and not e.get("verified")
        ]
        if len(crit_no_ev) > CRITICAL_NO_EVIDENCE_LIMIT:
            result.add(AuditFinding(
                code="CRITICAL_WITHOUT_EVIDENCE",
                level="alert",
                message=f"{len(crit_no_ev)} hallazgos críticos sin evidencia — revisar antes de escalar.",
                detail={"entry_ids": [e.get("entry_id") for e in crit_no_ev[:5]]},
            ))

        # ── Check 5: Silencio sospechoso (gap temporal) ──────────────────────
        timestamps = []
        for e in entries:
            ts_str = e.get("submitted_at") or e.get("timestamp") or ""
            try:
                timestamps.append(datetime.fromisoformat(ts_str.replace("Z", "+00:00")))
            except (ValueError, AttributeError):
                pass

        if len(timestamps) >= 3:
            timestamps.sort()
            gaps = [(timestamps[i+1] - timestamps[i]).total_seconds() / 60
                    for i in range(len(timestamps) - 1)]
            max_gap = max(gaps)
            if max_gap >= SILENCE_GAP_MINUTES:
                gap_idx = gaps.index(max_gap)
                result.add(AuditFinding(
                    code="TEMPORAL_SILENCE",
                    level="warning",
                    message=f"Gap de {max_gap:.0f} min sin entradas entre {timestamps[gap_idx].strftime('%H:%M')} y {timestamps[gap_idx+1].strftime('%H:%M')} UTC.",
                    detail={"gap_minutes": round(max_gap, 1), "gap_start": timestamps[gap_idx].isoformat()},
                ))

        # ── Check 6: Distribución geográfica anómala ──────────────────────────
        locations: Dict[str, int] = {}
        for e in entries:
            loc = (e.get("location") or "").strip().split(",")[0].strip()
            if loc:
                locations[loc] = locations.get(loc, 0) + 1

        if locations and len(entries) >= 8:
            top_loc   = max(locations, key=lambda k: locations[k])
            top_count = locations[top_loc]
            geo_ratio = top_count / len(entries)
            if geo_ratio >= 0.8:
                result.add(AuditFinding(
                    code="GEOGRAPHIC_CONCENTRATION",
                    level="warning",
                    message=f"{top_count}/{len(entries)} entradas ({geo_ratio:.0%}) desde '{top_loc}' — escasa cobertura geográfica.",
                    detail={"location": top_loc, "count": top_count, "ratio": round(geo_ratio, 3)},
                ))

        # ── Check 7: Severidades inconsistentes ───────────────────────────────
        # Si hay >=5 "critical" pero 0 "high" — distribución sospechosa
        sev_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0, "info": 0}
        for e in entries:
            s = e.get("severity", "medium")
            sev_counts[s] = sev_counts.get(s, 0) + 1

        if sev_counts["critical"] >= 5 and sev_counts["high"] == 0 and len(entries) >= 8:
            result.add(AuditFinding(
                code="SEVERITY_DISTRIBUTION_ANOMALY",
                level="warning",
                message=f"{sev_counts['critical']} entradas críticas y 0 altas — distribución de severidad inusual.",
                detail={"severity_distribution": sev_counts},
            ))

        return result

    def audit_entry(self, entry: Dict, existing_entries: List[Dict], country_code: str = "") -> AuditResult:
        """Audita una entrada individual en el contexto de la sesión. Para uso event-driven."""
        mock_session = {
            "session_id": entry.get("session_id", "unknown"),
            "entries": existing_entries + [entry],
        }
        return self.audit_session(mock_session, country_code)
