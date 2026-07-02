#!/usr/bin/env python
"""Genera el informe FINAL de Perú 2026 localmente, con LLM real y el corpus
completo (base de prueba), para revisión antes de publicar.

Requisitos:
- backend/.env con una ANTHROPIC_API_KEY VÁLIDA.
- evidence_base/raw/PER_session_*.jsonl (base de prueba; ya committeada).

Uso (desde backend/):
    python -m scripts.generate_final_report

Clave: usa período COMPLETO (2026-04-08 → hoy) para incluir 1ª y 2ª vuelta.
Persiste en reports/elite/{report_id}/ (report.html, report.md, metadata.json).
"""
from __future__ import annotations

import asyncio
import glob
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")

from langchain_anthropic import ChatAnthropic                       # noqa: E402
from modules.config import LLM_MODEL                                # noqa: E402
from agents.elite_report.models import EliteReportRequest, MissionMetadata  # noqa: E402
from agents.elite_report.elite_report import PEIRSEliteReport       # noqa: E402

RAW_DIR = BACKEND.parent / "evidence_base" / "raw"
# Período COMPLETO del ciclo: incluye 1ª vuelta (abr) y 2ª vuelta (jun). Si se
# acorta el period_start, la 1ª vuelta se filtra y el informe sale incompleto.
PERIOD_START = "2026-04-08"
JORNADA = "2026-06-07"


def _load_corpus() -> list:
    rows = []
    for fp in sorted(glob.glob(str(RAW_DIR / "PER_session_*.jsonl"))):
        with open(fp, encoding="utf-8") as fh:
            rows.extend(json.loads(l) for l in fh if l.strip())
    return rows


def _period_end(rows: list) -> str:
    """period_end = fecha de la última captura del corpus. Garantiza que el
    informe cubra TODO el corpus (nada se filtra por ventana) y que el total
    consolidado del informe == manifest (coherencia perfecta)."""
    dates = [(r.get("recorded_at") or "")[:10] for r in rows]
    dates = [d for d in dates if d]
    return max(dates) if dates else "2026-06-29"


async def _run() -> None:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        sys.exit("[final] Falta ANTHROPIC_API_KEY en backend/.env")
    temp = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    llm = ChatAnthropic(model=LLM_MODEL, temperature=temp, anthropic_api_key=key)

    # Pre-check: una sola llamada barata para no gastar 13 chapters si la key falla.
    try:
        ping = llm.invoke("Responde solo: OK")
        print(f"[final] LLM OK ({LLM_MODEL}, temp {temp}) -> {str(ping.content)[:40]!r}")
    except Exception as e:
        sys.exit(f"[final] LLM no disponible ({type(e).__name__}: {str(e)[:200]}). "
                 f"Verificá la ANTHROPIC_API_KEY en backend/.env.")

    raw = _load_corpus()
    period_end = _period_end(raw)
    print(f"[final] corpus: {len(raw)} capturas | period_end={period_end}")
    session = {
        "session_id": "4053dd18", "country_code": "PER", "phase": "counting_tabulation",
        "mission_name": "DemocracIA Misión Perú 2026", "lead_org": "DemocracIA",
        "started_at": "2026-04-08T04:31:36+00:00", "updated_at": f"{period_end}T23:59:59+00:00",
        "finalized": False, "entries": raw,
    }
    rep = PEIRSEliteReport(llm=llm, observation_store={"PER": session})
    req = EliteReportRequest(
        country_code="PER", language="es", include_appendix_c=True,
        report_type="final", use_llm=True, output_formats=["md", "html"],
        mission_metadata=MissionMetadata(
            report_number="PE-2026-FINAL", period_start=PERIOD_START,
            period_end=period_end, jornada_date=JORNADA),
    )
    out = await rep.compose(req)
    st = out.stats or {}
    print(f"[final] STATUS: {out.status} | report_id: {out.report_id}")
    print(f"[final] tokens: {out.tokens_used} | cost_usd: {out.estimated_cost_usd} "
          f"| secs: {round(out.generation_time_seconds or 0, 1)}")
    empty = sum(1 for c in out.chapters if not (c.narrative or '').strip())
    print(f"[final] chapters: {len(out.chapters)} | empty narratives: {empty}")
    print(f"[final] total: {st.get('total')} | consolidated: {st.get('consolidated_total')}")
    br = st.get("by_round") or {}
    if br:
        print(f"[final] by_round: 1ª={br.get('1ª vuelta', {}).get('total')} "
              f"2ª={br.get('2ª vuelta', {}).get('total')}")
    print(f"[final] HTML: reports/elite/{out.report_id}/report.html")
    if out.warnings:
        print(f"[final] warnings ({len(out.warnings)}):")
        for w in out.warnings[:6]:
            print("   -", w[:160])


if __name__ == "__main__":
    asyncio.run(_run())
