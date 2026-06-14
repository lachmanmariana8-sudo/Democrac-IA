"""Apertura determinista del informe: Prólogo ("Quiénes somos") + Síntesis
ejecutiva. Reemplaza la 'Declaración preliminar' redactada por el LLM (que
introducía cifras inventadas) por texto institucional fijo + síntesis armada
desde los datos reales. Sin LLM, sin pronósticos, todo trazable.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.elite_report.i18n import t

_THOUSANDS_SEP = {"es": ".", "pt": ".", "en": ","}
_DECIMAL_SEP = {"es": ",", "pt": ",", "en": "."}


def _fmt_int(n: Any, lang: str) -> str:
    try:
        grouped = "{:,}".format(int(n))
    except (TypeError, ValueError):
        return str(n)
    return grouped.replace(",", _THOUSANDS_SEP.get(lang, ","))


def _fmt_dec(v: Any, lang: str, places: int = 2) -> str:
    try:
        s = f"{float(v):.{places}f}"
    except (TypeError, ValueError):
        return str(v)
    return s.replace(".", _DECIMAL_SEP.get(lang, "."))


def _vdem_endpoints(series: Optional[List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    """Extrae autonomía/capacidad del EMB en el año base (2021 si existe, si no
    el más antiguo) y en el año más reciente disponible. Solo datos del dataset."""
    if not series:
        return None
    rows = [r for r in series if isinstance(r, dict) and r.get("v2elembaut") is not None]
    if not rows:
        return None
    rows.sort(key=lambda r: r.get("year", 0))
    base = next((r for r in rows if r.get("year") == 2021), rows[0])
    latest = rows[-1]
    return {
        "y0": base.get("year"), "aut0": base.get("v2elembaut"), "cap0": base.get("v2elembcap"),
        "y1": latest.get("year"), "aut1": latest.get("v2elembaut"), "cap1": latest.get("v2elembcap"),
    }


def build_declaration_narrative(
    runoff: Dict[str, Any],
    stats: Optional[Dict[str, Any]],
    vdem_emb_series: Optional[List[Dict[str, Any]]],
    lang: str = "es",
) -> Optional[str]:
    """Markdown de la apertura: Prólogo (institucional, fijo) + Síntesis
    ejecutiva (datos reales). Devuelve None si faltan datos del balotaje."""
    if not isinstance(runoff, dict) or "second_round_results" not in runoff:
        return None
    sr = runoff["second_round_results"]
    stats = stats or {}

    parts: List[str] = []

    # ── Prólogo — Quiénes somos (texto institucional fijo) ───────────────
    parts.append("### " + t(lang, "prologo.title"))
    for k in ("prologo.p1", "prologo.p2", "prologo.p3", "prologo.p4"):
        parts.append(t(lang, k))

    # ── Síntesis ejecutiva (armada desde datos) ──────────────────────────
    parts.append("### " + t(lang, "declaration.synthesis_title"))

    total = stats.get("total", 0)
    n_alta = (stats.get("critical", 0) or 0) + (stats.get("high", 0) or 0)
    parts.append(t(lang, "declaration.period_corpus").format(
        n=_fmt_int(total, lang), n_alta=_fmt_int(n_alta, lang)))

    parts.append(t(lang, "declaration.patterns_intro"))

    cands = sr.get("candidates") or []
    factors: List[str] = []
    if len(cands) >= 2:
        factors.append(t(lang, "declaration.pattern_result").format(
            actas=_fmt_dec(sr.get("actas_processed_pct"), lang, 1),
            a=cands[0].get("candidate_name", "—"), ap=cands[0].get("party", "—"),
            b=cands[1].get("candidate_name", "—"), bp=cands[1].get("party", "—"),
            margin=_fmt_int(sr.get("margin_votes_approx"), lang),
            mp=_fmt_dec(sr.get("margin_pct_approx"), lang, 3)))
    factors.append(t(lang, "declaration.pattern_count"))
    factors.append(t(lang, "declaration.pattern_emb"))
    parts.append("\n".join(factors))

    vd = _vdem_endpoints(vdem_emb_series)
    if vd:
        parts.append(t(lang, "declaration.reading").format(
            aut0=_fmt_dec(vd["aut0"], lang), y0=vd["y0"],
            aut1=_fmt_dec(vd["aut1"], lang), y1=vd["y1"],
            cap0=_fmt_dec(vd["cap0"], lang), cap1=_fmt_dec(vd["cap1"], lang)))
    else:
        parts.append(t(lang, "declaration.reading_no_vdem"))

    parts.append("*" + t(lang, "declaration.disclosure") + "*")
    return "\n\n".join(parts)
