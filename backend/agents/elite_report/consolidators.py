"""Consolidación de hallazgos: un hecho = un hallazgo con TODAS sus fuentes.

El Hunter capta el mismo evento varias veces (re-scrapes, varios medios), y el
pipeline no deduplicaba: cada captura entraba como un hallazgo separado, lo que
producía repetición de eventos y de fuentes en cronologías y ejes.

Este módulo agrupa hallazgos del MISMO evento (misma fecha + alta similitud de
texto, sin LLM) y fusiona sus fuentes en una sola entrada. No borra información:
preserva todas las URLs (campo `sources`) y la trazabilidad. Determinista.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Callable, Dict, List

_STOPWORDS = frozenset({
    "para", "como", "pero", "porque", "donde", "cuando", "sobre", "entre",
    "desde", "hasta", "segun", "tras", "ante", "este", "esta", "estos", "estas",
    "esa", "ese", "esos", "esas", "que", "con", "por", "una", "unos", "unas",
    "del", "las", "los", "the", "and", "for", "with",
})

_SEV_RANK = {"critical": 5, "high": 4, "medium": 3, "moderate": 3, "low": 2, "info": 1}

# Umbral de similitud (Jaccard de tokens significativos) para considerar dos
# hallazgos del mismo evento, dentro del mismo día. 0.5 tolera redacciones
# distintas del mismo hecho (medios diferentes) sin mezclar eventos distintos.
DEFAULT_THRESHOLD = 0.5


def _deaccent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _sig_tokens(text: str) -> frozenset:
    """Conjunto de tokens significativos (≥5 letras o números) sin acentos.

    Aplica un stem ligero (primeros 6 caracteres) a las palabras para tolerar
    variantes de inflexión del mismo hecho (denuncia/denunció → 'denunc')."""
    t = _deaccent((text or "").lower())
    words = re.findall(r"[a-z0-9]+", t)
    out = set()
    for w in words:
        if w in _STOPWORDS:
            continue
        if w.isdigit() and len(w) >= 2:
            out.add(w)
        elif len(w) >= 5:
            out.add(w[:6])
    return frozenset(out)


def _jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cluster_records(
    records: List[Any],
    text_of: Callable[[Any], str],
    date_of: Callable[[Any], str],
    threshold: float = DEFAULT_THRESHOLD,
) -> List[List[int]]:
    """Agrupa índices de `records` por (misma fecha[:10] + Jaccard ≥ threshold).
    Greedy y estable: respeta el orden de aparición."""
    clusters: List[Dict[str, Any]] = []
    for i, r in enumerate(records):
        d = (date_of(r) or "")[:10]
        sig = _sig_tokens(text_of(r))
        placed = False
        for c in clusters:
            if c["date"] == d and _jaccard(c["sig"], sig) >= threshold:
                c["idx"].append(i)
                placed = True
                break
        if not placed:
            clusters.append({"date": d, "sig": sig, "idx": [i]})
    return [c["idx"] for c in clusters]


def _source_entry(url: str, name: str) -> Dict[str, str]:
    return {"url": url or "", "name": (name or "fuente")}


def consolidate_findingrefs(findings: List[Any], threshold: float = DEFAULT_THRESHOLD) -> List[Any]:
    """Consolida una lista de FindingRef. Devuelve un hallazgo por evento, con
    `sources` = unión de todas las fuentes (URL única) y la fecha más temprana.
    El representante es el de mayor priority_score/severidad."""
    if not findings:
        return []
    groups = cluster_records(
        findings, text_of=lambda f: getattr(f, "finding", "") or "",
        date_of=lambda f: getattr(f, "recorded_at", "") or "", threshold=threshold)
    out = []
    for idxs in groups:
        group = [findings[i] for i in idxs]
        rep = max(group, key=lambda f: (getattr(f, "priority_score", 0) or 0,
                                        _SEV_RANK.get((getattr(f, "severity", "") or "").lower(), 0)))
        sources: List[Dict[str, str]] = []
        seen = set()
        for f in group:
            url = getattr(f, "source_url", "") or ""
            name = getattr(f, "source_name", "") or getattr(f, "source_title", "") or ""
            key = url or name
            if key and key not in seen:
                seen.add(key)
                sources.append(_source_entry(url, name))
        dates = [getattr(f, "recorded_at", "") for f in group if getattr(f, "recorded_at", "")]
        themes = sorted({th for f in group for th in (getattr(f, "themes", []) or [])})
        try:
            rep.sources = sources
            if dates:
                rep.recorded_at = min(dates)
            if themes:
                rep.themes = themes
        except (AttributeError, ValueError):
            pass
        out.append(rep)
    return out


def consolidate_items(items: List[Dict[str, Any]], threshold: float = DEFAULT_THRESHOLD) -> List[Dict[str, Any]]:
    """Consolida items de un eje (dicts). Cada evento queda UNA vez.

    Preserva `sources` (lista de identificadores de fuente, usada para el cálculo
    de audit_status — NO la pisa) y añade `source_links` (lista de {url, name})
    para el render: un hecho = una entrada con todas sus fuentes enlazadas."""
    if not items:
        return []

    def _text(it: Dict[str, Any]) -> str:
        return (it.get("content_summary") or it.get("narrative_summary")
                or it.get("summary") or it.get("finding") or "")

    groups = cluster_records(items, text_of=_text,
                             date_of=lambda it: it.get("date") or it.get("recorded_at") or "",
                             threshold=threshold)
    out = []
    for idxs in groups:
        group = [items[i] for i in idxs]
        rep = dict(max(group, key=lambda it: _SEV_RANK.get(
            (it.get("severity") or it.get("verification_level") or "").lower(), 0)))
        # Unión de `sources` (strings) — preserva semántica del audit_status.
        merged_sources: List[Any] = []
        seen_s = set()
        # Enlaces para el render (dicts {url, name}).
        links: List[Dict[str, str]] = []
        seen_u = set()
        for it in group:
            for s in (it.get("sources") or []):
                if s and s not in seen_s:
                    seen_s.add(s)
                    merged_sources.append(s)
            url = it.get("source_url") or ""
            name = (it.get("sources") or ["fuente"])[0] if it.get("sources") else "fuente"
            if url and url not in seen_u:
                seen_u.add(url)
                links.append(_source_entry(url, name))
        rep["sources"] = merged_sources
        if links:
            rep["source_links"] = links
        out.append(rep)
    return out
