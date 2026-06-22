#!/usr/bin/env python
"""Construye la BASE DE PRUEBA trazable y deduplicada a partir del crudo exportado
de prod (scripts/export_prod_corpus.py).

Determinista, sin LLM. Un hecho = un hallazgo (sin repetir), con TODAS sus fuentes.
Reutiliza la misma deduplicación que el informe (cluster_records de consolidators)
para que los conteos de la base == los conteos del informe.

Uso (desde backend/):
    python -m scripts.build_evidence_base --country PER

Entrada:
    evidence_base/raw/{CC}_session_*.jsonl   (capturas crudas, 1 línea c/u)

Salida (versionada en el repo = prueba auditable):
    evidence_base/{CC}_round1.jsonl   (hechos consolidados de 1ª vuelta)
    evidence_base/{CC}_round2.jsonl   (hechos consolidados de 2ª vuelta)
    evidence_base/manifest.json       (raw_total, dedup_total, by_round,
                                       by_category con los "+N", % con URL, sha256)
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from agents.elite_report.consolidators import cluster_records
from agents.elite_report.loaders.hunter_loader import HunterLoader
from agents.elite_report.elite_report import PEIRSEliteReport

REPO_ROOT = Path(__file__).resolve().parents[2]
EB_DIR = REPO_ROOT / "evidence_base"
RAW_DIR = EB_DIR / "raw"

_SEV_RANK = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_raw(country: str) -> List[Dict[str, Any]]:
    files = sorted(glob.glob(str(RAW_DIR / f"{country}_session_*.jsonl")))
    if not files:
        raise SystemExit(f"[build] No hay crudo en {RAW_DIR} para {country}. "
                         f"Corré export_prod_corpus.py primero.")
    rows: List[Dict[str, Any]] = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            rows.extend(json.loads(l) for l in fh if l.strip())
    return rows


def _consolidate(findings: List[Any]) -> List[Dict[str, Any]]:
    """Agrupa por (fecha + similitud) y devuelve un dict-hecho por grupo con
    TODAS las fuentes y entry_ids fusionados. Mismo clustering que el informe."""
    groups = cluster_records(
        findings,
        text_of=lambda f: getattr(f, "finding", "") or "",
        date_of=lambda f: getattr(f, "recorded_at", "") or "",
    )
    facts: List[Dict[str, Any]] = []
    for idxs in groups:
        grp = [findings[i] for i in idxs]
        rep = max(grp, key=lambda f: (getattr(f, "priority_score", 0) or 0,
                                      _SEV_RANK.get((getattr(f, "severity", "") or "").lower(), 0)))
        sources, seen = [], set()
        for f in grp:
            url = getattr(f, "source_url", "") or ""
            name = getattr(f, "source_name", "") or getattr(f, "source_title", "") or "fuente"
            key = url or name
            if key and key not in seen:
                seen.add(key)
                sources.append({"url": url, "name": name})
        dates = [getattr(f, "recorded_at", "") for f in grp if getattr(f, "recorded_at", "")]
        entry_ids = sorted({getattr(f, "entry_id", None) for f in grp if getattr(f, "entry_id", None)})
        facts.append({
            "finding": getattr(rep, "finding", "") or "",
            "category": getattr(rep, "category", "other") or "other",
            "severity": (getattr(rep, "severity", "info") or "info").lower(),
            "recorded_at": min(dates) if dates else getattr(rep, "recorded_at", None),
            "round": PEIRSEliteReport._round_label(min(dates) if dates else ""),
            "priority_score": getattr(rep, "priority_score", None),
            "location": getattr(rep, "location", None) or None,
            "captures": len(grp),          # cuántas capturas crudas se fusionaron
            "entry_ids": entry_ids,        # trazabilidad: ids crudos del evento
            "sources": sources,            # TODAS las URLs/medios del hecho
        })
    # Orden estable cronológico
    facts.sort(key=lambda x: ((x.get("recorded_at") or ""), x.get("category", "")))
    return facts


def _write_jsonl(path: Path, facts: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for fct in facts:
            fh.write(json.dumps(fct, ensure_ascii=False, sort_keys=True) + "\n")


def _by_category(facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts: Counter = Counter()
    sevmax: Dict[str, str] = {}
    for f in facts:
        c = f["category"]
        counts[c] += 1
        s = f["severity"]
        if _SEV_RANK.get(s, 0) > _SEV_RANK.get(sevmax.get(c, "info"), 0):
            sevmax[c] = s
    return [{"category": c, "count": n, "severity_max": sevmax.get(c, "info")}
            for c, n in counts.most_common()]


def build(country: str, stamp: str) -> Dict[str, Any]:
    cc = country.upper()
    raw = _load_raw(cc)
    now = datetime.now(timezone.utc)
    findings = [HunterLoader._to_finding_ref(e, now) for e in raw]
    # cluster_records es greedy y SENSIBLE AL ORDEN. El loader del informe ordena
    # por priority_score desc antes de consolidar; replicamos ese orden para que
    # los clusters (y por ende los conteos) sean idénticos a los del informe.
    findings.sort(key=lambda x: -(x.priority_score or 0))

    # Coherencia EXACTA con el informe: _build_stats consolida TODO el corpus y
    # luego asigna cada hecho a su vuelta por la fecha más temprana del cluster.
    # Replicamos ese orden (consolidar→partir), no partir→consolidar, para que
    # manifest.dedup_total == report.consolidated_total y los splits coincidan.
    all_facts = _consolidate(findings)
    facts1 = [f for f in all_facts if f["round"] == "1ª vuelta"]
    facts2 = [f for f in all_facts if f["round"] == "2ª vuelta"]
    # "raw" por vuelta = capturas crudas en cada ventana (volumen monitoreado).
    r1 = [f for f in findings if PEIRSEliteReport._round_label(f.recorded_at) == "1ª vuelta"]
    r2 = [f for f in findings if PEIRSEliteReport._round_label(f.recorded_at) == "2ª vuelta"]

    EB_DIR.mkdir(parents=True, exist_ok=True)
    p1, p2 = EB_DIR / f"{cc}_round1.jsonl", EB_DIR / f"{cc}_round2.jsonl"
    _write_jsonl(p1, facts1)
    _write_jsonl(p2, facts2)

    dedup_total = len(facts1) + len(facts2)
    with_url = sum(1 for f in (facts1 + facts2) if f["sources"] and f["sources"][0]["url"])
    manifest = {
        "country_code": cc,
        "built_at": stamp,
        "raw_total": len(raw),
        "dedup_total": dedup_total,
        "by_round": {
            "1ª vuelta": {"raw": len(r1), "dedup": len(facts1)},
            "2ª vuelta": {"raw": len(r2), "dedup": len(facts2)},
        },
        "by_category": _by_category(facts1 + facts2),
        "by_category_round1": _by_category(facts1),
        "by_category_round2": _by_category(facts2),
        "facts_with_source_url": with_url,
        "pct_with_source_url": round(100 * with_url / max(dedup_total, 1), 1),
        "round_threshold": PEIRSEliteReport._ROUND_THRESHOLD,
        "files": {
            p1.name: {"facts": len(facts1), "sha256": _sha256(p1)},
            p2.name: {"facts": len(facts2), "sha256": _sha256(p2)},
        },
    }
    (EB_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description="Construye la base de prueba deduplicada.")
    ap.add_argument("--country", default="PER")
    # stamp inyectable (Date.now no disponible en algunos entornos de orquestación)
    ap.add_argument("--stamp", default=None)
    args = ap.parse_args()
    stamp = args.stamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    m = build(args.country, stamp)
    print(f"[build] raw={m['raw_total']} dedup={m['dedup_total']} "
          f"(R1 {m['by_round']['1ª vuelta']['raw']}->{m['by_round']['1ª vuelta']['dedup']}, "
          f"R2 {m['by_round']['2ª vuelta']['raw']}->{m['by_round']['2ª vuelta']['dedup']}) "
          f"url={m['pct_with_source_url']}%")
    print("[build] top temáticas:",
          ", ".join(f"{c['category']}:{c['count']}" for c in m["by_category"][:6]))


if __name__ == "__main__":
    main()
