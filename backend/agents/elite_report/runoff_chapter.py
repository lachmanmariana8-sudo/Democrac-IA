"""Capítulo determinista de observación de la fase entre vueltas (9 ejes).

NO usa LLM: la narrativa se construye con strings i18n + los datos de
PERU_RUNOFF_2026 (enriquecido por modules/runoff_enrichment.py). Garantiza que
el Elite Report se genere SIEMPRE — incluso con todos los ejes vacíos —
explicando el PROCESO de cara a la segunda vuelta (finalistas, fechas,
comparativa de 1ª vuelta, base legal) y distinguiendo honestamente
"monitoreado, 0 hallazgos" de "no observado".
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.elite_report.models import EliteChapter
from agents.elite_report.i18n import t

# Posición lógica: justo después de "Jornada electoral" (cap. 5). El número real
# se reasigna en compose al renumerar; este es el default si no se renumera.
RUNOFF_CHAPTER_NUMBER = 6
RUNOFF_CHAPTER_ID = "observacion_entre_vueltas"

AXIS_ORDER: List[str] = [
    "campaign_conduct_finalist_a",
    "campaign_conduct_finalist_b",
    "hate_speech_and_intimidation_incidents",
    "media_access_monitoring",
    "emb_independence_stress_signals",
    "election_day_logistics_readiness",
    "vote_count_transparency_protocol",
    "dispute_resolution_tracker",
    "osint_information_integrity_monitor",
    "electoral_violence_incidents",
]

# Ejes alimentados por OSINT/Hunter: su estado vacío es "monitoreado, 0 hallazgos".
# El resto son institucionales: su estado vacío es "no observado, pendiente fuente".
OSINT_AXES = frozenset({
    "hate_speech_and_intimidation_incidents",
    "osint_information_integrity_monitor",
    "electoral_violence_incidents",
})

_ESCALATED = {"VERIFIED_SECONDARY", "CONFIRMED"}

_THOUSANDS_SEP = {"es": ".", "pt": ".", "en": ","}


def _fmt_int(n: Any, lang: str) -> str:
    try:
        grouped = "{:,}".format(int(n))
    except (TypeError, ValueError):
        return str(n)
    return grouped.replace(",", _THOUSANDS_SEP.get(lang, ","))


def _axis_count(axis_key: str, block: Dict[str, Any]) -> int:
    """Mismo criterio que countOf() del frontend (Dashboard.jsx)."""
    for k in ("incidents", "signals", "cases", "narratives"):
        v = block.get(k)
        if isinstance(v, list):
            return len(v)
    if axis_key == "media_access_monitoring":
        return 1 if block.get("finalist_a_minutes") is not None else 0
    if axis_key == "election_day_logistics_readiness":
        return 1 if block.get("polling_stations_total") is not None else 0
    if axis_key == "vote_count_transparency_protocol":
        return 1 if block.get("mesa_level_disaggregation_available") is not None else 0
    return 0


def _axis_items(block: Dict[str, Any]) -> List[Dict[str, Any]]:
    for k in ("incidents", "narratives", "signals", "cases"):
        v = block.get(k)
        if isinstance(v, list) and v:
            return v
    return []


def _render_items(items: List[Dict[str, Any]], limit: int = 5) -> List[str]:
    lines = []
    for it in items[:limit]:
        date = it.get("date") or "—"
        sev = it.get("severity") or "info"
        summary = (it.get("content_summary") or it.get("narrative_summary") or "").strip()
        classification = it.get("classification") or ""
        sources = it.get("sources") or []
        src = sources[0] if sources else ""
        url = it.get("source_url")
        if url:
            tail = " — [" + (src or url) + "](" + url + ")"
        elif src:
            tail = " — " + src
        else:
            tail = ""
        bullet = "- **" + str(date) + "** · " + str(sev)
        if summary:
            bullet += " · " + summary
        if classification:
            bullet += " (" + str(classification) + ")"
        bullet += tail
        lines.append(bullet)
    return lines


def _build_context_section(runoff: Dict[str, Any], lang: str) -> List[str]:
    """Párrafo introductorio: finalistas, fechas, comparativa 1ª vuelta, base legal."""
    parts: List[str] = ["### " + t(lang, "runoff_obs.context_header")]

    runoff_date = runoff.get("runoff_date") or "—"
    first_round_date = runoff.get("first_round_date") or "—"
    parts.append(t(lang, "runoff_obs.context_intro").format(
        runoff_date=runoff_date, first_round_date=first_round_date))

    finalists = runoff.get("finalists") or []
    pcts = []
    for f in finalists:
        pct = f.get("first_round_pct")
        if pct is not None:
            pcts.append(pct)
        parts.append(t(lang, "runoff_obs.finalist_line").format(
            name=f.get("candidate_name", "—"),
            party=f.get("party_name", "—"),
            pct=pct if pct is not None else "—",
            votes=_fmt_int(f.get("first_round_votes"), lang),
        ))
    if len(pcts) == 2:
        parts.append(t(lang, "runoff_obs.margin_line").format(
            margin=round(abs(pcts[0] - pcts[1]), 2)))

    br = runoff.get("first_round_full_breakdown") or {}
    abstention = br.get("abstention_pct")
    if abstention is not None:
        parts.append(t(lang, "runoff_obs.turnout_line").format(
            turnout=round(100 - abstention, 2),
            abstention=abstention,
            blank=br.get("blank_pct", "—"),
            null=br.get("null_pct", "—"),
        ))

    parts.append(t(lang, "runoff_obs.legal_basis"))
    return parts


def build_runoff_observation_narrative(runoff: Dict[str, Any], lang: str) -> str:
    """Construye el markdown del capítulo desde el dict completo del balotaje."""
    observation = runoff.get("runoff_phase_observation") or {}
    parts: List[str] = _build_context_section(runoff, lang)

    parts.append("### " + t(lang, "runoff_obs.observation_header"))
    parts.append(t(lang, "runoff_obs.intro"))

    total_findings = 0
    any_escalated = False
    body: List[str] = []
    for axis_key in AXIS_ORDER:
        block = observation.get(axis_key)
        if not isinstance(block, dict):
            continue
        status = block.get("audit_status", "PENDIENTE_VERIFICACION")
        if status in _ESCALATED:
            any_escalated = True
        count = _axis_count(axis_key, block)
        total_findings += count

        label = t(lang, "runoff_obs.axis." + axis_key, axis_key)
        body.append("#### " + label + " — `" + str(status) + "`")
        # Qué observa el eje (siempre, aunque esté vacío).
        body.append("*" + t(lang, "runoff_obs.desc." + axis_key, "") + "*")

        if count == 0:
            key = "runoff_obs.no_findings" if axis_key in OSINT_AXES else "runoff_obs.not_observed"
            body.append(t(lang, key))
        else:
            body.append(t(lang, "runoff_obs.findings_count").format(n=count))
            items = _axis_items(block)
            if items:
                body.extend(_render_items(items))

    global_status = "PARCIAL" if any_escalated else "PENDIENTE_VERIFICACION"
    parts.append("**" + t(lang, "runoff_obs.global_header").format(
        status=global_status, n=total_findings) + "**")
    parts.extend(body)
    return "\n\n".join(parts)


def build_runoff_observation_chapter(
    runoff: Optional[Dict[str, Any]], lang: str = "es"
) -> Optional[EliteChapter]:
    """Devuelve un EliteChapter determinista, o None si no hay datos de runoff.

    `runoff` es el dict COMPLETO del balotaje (PERU_RUNOFF_2026 enriquecido):
    debe contener al menos runoff_phase_observation.
    """
    if not isinstance(runoff, dict) or "runoff_phase_observation" not in runoff:
        return None
    narrative = build_runoff_observation_narrative(runoff, lang)
    return EliteChapter(
        number=RUNOFF_CHAPTER_NUMBER,
        chapter_id=RUNOFF_CHAPTER_ID,
        title="Observación de la fase entre vueltas — 9 ejes canónicos",
        narrative=narrative,
    )
