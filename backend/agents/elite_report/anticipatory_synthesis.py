"""Síntesis anticipatoria determinista: qué anticipaban los índices
internacionales (V-Dem, Freedom House, PEI, RSF) y qué mostró el ciclo 2026.

Cierra el loop datos↔hallazgos SIN LLM y SIN especular: empareja la TENDENCIA
real de cada dataset (de bundle.historical_series) con el volumen real de
hallazgos consolidados en las categorías que ese índice mide (stats.by_category).
Cada cifra es auditable; no se afirma causalidad, sólo congruencia observada.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.elite_report.i18n import t, category_label

# Qué categorías de hallazgo "cubre" cada índice (para el emparejamiento).
_INDICATOR_MAP = [
    ("rsf", ("press freedom", "rsf", "prensa"),
     ["disinformation", "media_restriction", "media"]),
    ("vdem", ("liberal democracy", "v-dem", "vdem"),
     ["legal", "fraud_allegation", "counting", "results"]),
    ("fh", ("freedom house", "freedom in the world", "fiw"),
     ["voter_suppression", "voter_intimidation", "security", "hate_speech",
      "media_restriction"]),
    ("pei", ("electoral integrity", "pei", "integridad"),
     ["logistics", "counting", "results", "ballot_tampering",
      "irregular_procedure"]),
]

_TREND_WORD = {
    "down": "trend.down", "up": "trend.up",
    "stable": "trend.stable", "volatile": "trend.volatile",
}


def _match_indicator(label: str, source: str) -> Optional[str]:
    blob = f"{label} {source}".lower()
    for key, kws, _cats in _INDICATOR_MAP:
        if any(kw in blob for kw in kws):
            return key
    return None


def _cats_for(key: str) -> List[str]:
    for k, _kws, cats in _INDICATOR_MAP:
        if k == key:
            return cats
    return []


def build_anticipatory_synthesis(
    series_list: Optional[List[Any]],
    stats: Optional[Dict[str, Any]],
    lang: str = "es",
) -> str:
    """Markdown de la síntesis anticipatoria, o "" si faltan datos."""
    if not series_list or not stats:
        return ""
    by_cat = {c.get("category"): int(c.get("count", 0) or 0)
              for c in (stats.get("by_category") or [])}
    if not by_cat:
        return ""

    parts: List[str] = ["### " + t(lang, "synth.header"), t(lang, "synth.intro")]

    cols = [t(lang, "synth.col.indicator"), t(lang, "synth.col.trend"),
            t(lang, "synth.col.anticipated"), t(lang, "synth.col.evidence")]
    rows = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * 4) + "|"]

    any_row = False
    for s in series_list:
        label = getattr(s, "indicator_label", "") or ""
        source = getattr(s, "source", "") or ""
        key = _match_indicator(label, source)
        if not key:
            continue
        direction = getattr(s, "trend_direction", "stable") or "stable"
        trend_txt = t(lang, _TREND_WORD.get(direction, "trend.stable"))
        # Evidencia: categorías cubiertas con conteo > 0, ordenadas por volumen.
        cats = [(c, by_cat.get(c, 0)) for c in _cats_for(key)]
        cats = sorted([(c, n) for c, n in cats if n > 0], key=lambda x: -x[1])
        if not cats:
            continue
        evidence = " · ".join(f"{category_label(c, lang)} ({n})" for c, n in cats[:3])
        anticipated = t(lang, f"synth.anticipated.{key}")
        rows.append(f"| {label} | {trend_txt} | {anticipated} | {evidence} |")
        any_row = True

    if not any_row:
        return ""
    parts.append("\n".join(rows))
    parts.append(t(lang, "synth.closing"))
    return "\n\n".join(parts)
