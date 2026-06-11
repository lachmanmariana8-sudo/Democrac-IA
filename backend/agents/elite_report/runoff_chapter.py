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


def _render_items(items: List[Dict[str, Any]], limit: int = 8) -> List[str]:
    """Renderiza items de cualquiera de los ejes (incidents/signals/cases/...).

    Tolerante a esquemas distintos: hallazgos OSINT ({content_summary}),
    narrativas ({narrative_summary}) y señales del EMB ({actor, action_type,
    summary}). Cada item cierra con su fuente primaria (source_url)."""
    _KNOWN_SEV = {"critical", "high", "medium", "low", "info", "moderate"}
    lines = []
    for it in items[:limit]:
        date = it.get("date") or "—"
        # Solo mostramos severidad real; NUNCA códigos de auditoría crudos
        # (verification_level tipo VERIFIED_SECONDARY no se expone al lector).
        sev_raw = str(it.get("severity") or "").lower()
        sev = sev_raw if sev_raw in _KNOWN_SEV else ""
        summary = (it.get("content_summary") or it.get("narrative_summary")
                   or it.get("summary") or "").strip()
        actor = it.get("actor") or ""
        classification = it.get("classification") or it.get("action_type") or ""
        sources = it.get("sources") or []
        src = sources[0] if sources else ""
        url = it.get("source_url")
        if url:
            tail = " — [" + (src or "fuente") + "](" + url + ")"
        elif src:
            tail = " — " + src
        else:
            tail = ""
        bullet = "- **" + str(date) + "**"
        if sev:
            bullet += " · " + sev
        if actor:
            bullet += " · " + str(actor)
        if summary:
            bullet += " · " + summary
        if classification:
            bullet += " (" + str(classification) + ")"
        bullet += tail
        lines.append(bullet)
    return lines


def _build_first_round_section(runoff: Dict[str, Any], lang: str) -> List[str]:
    """Sección 1 — resultados consumados de la PRIMERA vuelta (12-abr).

    Fuente factual ÚNICA de los resultados de 1ª vuelta: el breakdown completo.
    Los dos primeros se marcan como finalistas que pasan al balotaje."""
    parts: List[str] = ["#### " + t(lang, "runoff_obs.first_round_header")]
    parts.append(t(lang, "runoff_obs.first_round_intro"))

    br = runoff.get("first_round_full_breakdown") or {}
    by_party = br.get("by_party") or []
    flag = t(lang, "runoff_obs.advances_flag")
    for i, c in enumerate(by_party):
        parts.append(t(lang, "runoff_obs.candidate_line").format(
            name=c.get("candidate", "—"),
            party=c.get("party_name", "—"),
            pct=c.get("pct", "—"),
            votes=_fmt_int(c.get("votes"), lang),
            flag=(flag if i < 2 else ""),
        ))

    abstention = br.get("abstention_pct")
    if abstention is not None:
        parts.append(t(lang, "runoff_obs.turnout_line").format(
            turnout=round(100 - abstention, 2),
            abstention=abstention,
            blank=br.get("blank_pct", "—"),
            null=br.get("null_pct", "—"),
        ))
    return parts


# Estado → texto legible (NUNCA mostramos "PENDIENTE_VERIFICACION" al lector).
_STATUS_TEXT = {
    "CONFIRMED": "runoff_obs.status_confirmed",
    "VERIFIED_SECONDARY": "runoff_obs.status_verified",
    "PENDIENTE_VERIFICACION": "runoff_obs.status_registered",
}


def _build_observation_section(observation: Dict[str, Any], lang: str) -> List[str]:
    """Observación del proceso entre vueltas — registro RETROSPECTIVO.

    Solo desarrolla los ejes con hechos documentados. Los ejes sin datos NO se
    listan uno a uno con "pendiente"; se resumen en una nota de cobertura
    honesta (monitoreado-sin-incidentes vs sin-evidencia-primaria), preservando
    la trazabilidad del vacío sin sonar prospectivo."""
    parts: List[str] = [t(lang, "runoff_obs.observation_intro")]

    monitored_empty: List[str] = []   # OSINT vacíos
    no_source_empty: List[str] = []   # institucionales vacíos
    for axis_key in AXIS_ORDER:
        block = observation.get(axis_key)
        if not isinstance(block, dict):
            continue
        label = t(lang, "runoff_obs.axis." + axis_key, axis_key)
        count = _axis_count(axis_key, block)

        if count == 0:
            (monitored_empty if axis_key in OSINT_AXES else no_source_empty).append(label)
            continue

        # Eje con hechos documentados: se desarrolla con estado LEGIBLE.
        status = block.get("audit_status", "PENDIENTE_VERIFICACION")
        status_txt = t(lang, _STATUS_TEXT.get(status, "runoff_obs.status_registered"), "")
        parts.append("#### " + label)
        parts.append("*" + t(lang, "runoff_obs.desc." + axis_key, "") + "*")
        parts.append("**" + status_txt + "** · " +
                     t(lang, "runoff_obs.findings_count").format(n=count))
        items = _axis_items(block)
        if items:
            parts.extend(_render_items(items))

    # Nota de cobertura para los ejes sin hechos documentados.
    if monitored_empty or no_source_empty:
        parts.append("#### " + t(lang, "runoff_obs.coverage_header"))
        if monitored_empty:
            parts.append(t(lang, "runoff_obs.coverage_monitored").format(
                axes=", ".join(monitored_empty)))
        if no_source_empty:
            parts.append(t(lang, "runoff_obs.coverage_no_source").format(
                axes=", ".join(no_source_empty)))
    return parts


def _build_second_round_section(runoff: Dict[str, Any], lang: str) -> List[str]:
    """Sección 3 — resultado PROVISIONAL de la 2ª vuelta (7-jun). SIN ganador
    proclamado: refleja el escrutinio en curso, no anticipa desenlace."""
    sr = runoff.get("second_round_results")
    if not isinstance(sr, dict):
        return []
    parts: List[str] = ["#### " + t(lang, "runoff_obs.second_round_header")]
    parts.append(t(lang, "runoff_obs.second_round_status").format(
        as_of=sr.get("as_of", "—"),
        actas=sr.get("actas_processed_pct", "—"),
    ))
    for c in sr.get("candidates") or []:
        parts.append(t(lang, "runoff_obs.candidate_line_prov").format(
            name=c.get("candidate_name", "—"),
            party=c.get("party", "—"),
            pct=c.get("pct_valid", "—"),
            votes=_fmt_int(c.get("votes"), lang),
        ))
    procl = sr.get("proclamation") or {}
    if not procl.get("proclaimed"):
        parts.append(t(lang, "runoff_obs.second_round_pending").format(
            note=procl.get("note", "")))
    src_url = sr.get("source_url")
    if src_url:
        parts.append("> Fuente: [" + sr.get("source", "ONPE") + "](" + src_url + ")")
    return parts


def _build_stae_note(runoff: Dict[str, Any], lang: str) -> List[str]:
    """Nota factual sobre el STAE — corrige la falsa afirmación de buen
    funcionamiento. Solo se emite si hay dato cargado."""
    note = runoff.get("electoral_technology_note")
    if not isinstance(note, dict):
        return []
    parts: List[str] = ["#### " + t(lang, "runoff_obs.stae_header")]
    if note.get("stae_first_round"):
        parts.append(note["stae_first_round"])
    if note.get("stae_second_round"):
        parts.append(note["stae_second_round"])
    src = note.get("source_first_round")
    if src:
        parts.append("> " + src)
    return parts


def build_runoff_observation_narrative(runoff: Dict[str, Any], lang: str) -> str:
    """Markdown del capítulo factual: 1ª vuelta · entre vueltas · 2ª vuelta · STAE.

    Es la FUENTE ÚNICA de los resultados electorales en el informe (los demás
    capítulos no los repiten). Determinista: sin LLM, sin pronósticos."""
    observation = runoff.get("runoff_phase_observation") or {}
    parts: List[str] = []
    # Macro-sección A — Resultados electorales (hechos consumados).
    parts.append("### " + t(lang, "runoff_obs.results_macro"))
    parts += _build_first_round_section(runoff, lang)
    parts += _build_second_round_section(runoff, lang)
    parts += _build_stae_note(runoff, lang)
    # Macro-sección B — Observación del proceso entre vueltas.
    parts.append("### " + t(lang, "runoff_obs.between_header"))
    parts += _build_observation_section(observation, lang)
    parts.append(t(lang, "runoff_obs.legal_basis"))
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
        title=t(lang, "runoff_obs.report_title"),
        narrative=narrative,
    )
