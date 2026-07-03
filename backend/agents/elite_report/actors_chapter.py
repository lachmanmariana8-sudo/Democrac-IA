"""Capítulo determinista de Actores político-electorales y situación procesal.

NO usa LLM: se arma con PERU_POLITICAL_FORCES (perfiles, antecedentes y riesgo
ICCPR con fuente primaria). Trae al informe la data de actores que hasta ahora
sólo vivía en la solapa /api/peru/actors (huérfana). Es factual y trazable: cada
situación procesal/judicial cita su fuente (resolución JNE, expediente PJ,
carpeta fiscal), sin especular ni imputar responsabilidad penal.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.elite_report.models import EliteChapter
from agents.elite_report.i18n import t

# Posición lógica: tras "Sistema electoral" (cap. 3), antes de la fase
# pre-electoral. El número real se reasigna al renumerar en compose.
ACTORS_CHAPTER_NUMBER = 4
ACTORS_CHAPTER_ID = "actores_situacion_procesal"

# Marcadores de una situación procesal/judicial documentada en el perfil.
_JUDICIAL_KW = (
    "deten", "conden", "inhabilit", "investigaci", "lavado", "fiscal",
    "sentenc", "proceso penal", "carpeta fiscal", "denuncia", "prisión",
    "prision", "expediente",
)

_SEAT = "current_seats"


# Líderes que NO son una persona física con antecedente propio (colectivos,
# coaliciones, independientes): se excluyen de la sección procesal individual.
_NON_INDIVIDUAL = ("n/a", "directiva", "colectiv", "coalici", "varios")


def _has_judicial(force: Dict[str, Any]) -> bool:
    leader = (force.get("leader") or "").lower().strip()
    if not leader or any(tok in leader for tok in _NON_INDIVIDUAL):
        return False
    blob = " ".join(str(force.get(k, "")) for k in
                    ("background", "risk_notes", "iccpr_risk")).lower()
    return any(k in blob for k in _JUDICIAL_KW)


def _iccpr_article(force: Dict[str, Any]) -> str:
    risk = force.get("iccpr_risk") or ""
    return risk.split("—")[0].strip() if risk else "—"


def _iccpr_citation(force: Dict[str, Any]) -> str:
    """Cita de la fuente primaria del riesgo ICCPR (fuente · fecha, con URL)."""
    src = (force.get("iccpr_source") or "").strip()
    date = (force.get("iccpr_date") or "").strip()
    url = (force.get("iccpr_url") or "").strip()
    label = src
    if date:
        label = f"{label} · {date}" if label else date
    if not label:
        return ""
    return f"[{label}]({url})" if url else f"({label})"


def build_actors_narrative(forces: List[Dict[str, Any]], lang: str) -> str:
    parts: List[str] = [t(lang, "actors.intro")]

    # ── Tabla resumen de todas las fuerzas ──────────────────────────────
    cols = [t(lang, "actors.col.force"), t(lang, "actors.col.leader"),
            t(lang, "actors.col.ideology"), t(lang, "actors.col.seats"),
            t(lang, "actors.col.risk"), t(lang, "actors.col.iccpr")]
    rows = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    risk_lbl = {"high": t(lang, "actors.risk.high"),
                "medium": t(lang, "actors.risk.medium"),
                "low": t(lang, "actors.risk.low")}
    for f in forces:
        seats = f.get(_SEAT)
        rows.append("| {n} ({a}) | {ldr} | {ideo} | {s} | {r} | {art} |".format(
            n=f.get("name", "—"), a=f.get("abbr", ""), ldr=f.get("leader", "—"),
            ideo=f.get("ideology", "—"), s=(str(seats) if seats is not None else "—"),
            r=risk_lbl.get((f.get("risk_profile") or "").lower(), "—"),
            art=_iccpr_article(f)))
    parts.append("\n".join(rows))

    # ── Situación procesal de los actores con antecedentes judiciales ────
    judicial = [f for f in forces if _has_judicial(f)]
    if judicial:
        parts.append("### " + t(lang, "actors.judicial_header"))
        parts.append(t(lang, "actors.judicial_intro"))
        for f in judicial:
            parts.append("#### {leader} — {name} ({abbr})".format(
                leader=f.get("leader", "—"), name=f.get("name", "—"),
                abbr=f.get("abbr", "")))
            if f.get("background"):
                parts.append(str(f["background"]))
            if f.get("iccpr_risk"):
                line = ("**" + t(lang, "actors.iccpr_label") + ":** "
                        + str(f["iccpr_risk"]))
                cite = _iccpr_citation(f)
                if cite:
                    line += " " + cite
                parts.append(line)

    parts.append("*" + t(lang, "actors.note") + "*")
    return "\n\n".join(parts)


def build_actors_chapter(
    forces: Optional[List[Dict[str, Any]]], lang: str = "es"
) -> Optional[EliteChapter]:
    """EliteChapter determinista de actores, o None si no hay fuerzas cargadas."""
    if not forces:
        return None
    return EliteChapter(
        number=ACTORS_CHAPTER_NUMBER,
        chapter_id=ACTORS_CHAPTER_ID,
        title=t(lang, "actors.title"),
        narrative=build_actors_narrative(forces, lang),
    )
