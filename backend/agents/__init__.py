"""
agents/ — Módulo de agentes y pipeline LangGraph para DEMOCRAC.IA (PEIRS)

Estado de migración:
  - agents/pipeline.py  → build_workflow(), PEIRSState (alias de ElectionRiskState), peirs_pipeline
  - agents/nodes.py     → funciones nodo del grafo LangGraph:
                           ingestion_agent, political_analyst_agent,
                           legal_compliance_agent, electoral_dictamen_agent,
                           report_generator_agent

Este paquete re-exporta los símbolos clave para que app.py pueda importarlos
con importaciones condicionales sin romper el comportamiento existente.

Nota: las funciones originales permanecen definidas en app.py durante la
fase de migración.  Solo se agregan aliases/imports condicionales para
habilitar la transición gradual.
"""

from __future__ import annotations

try:
    from agents.pipeline import build_workflow, PEIRSState, peirs_pipeline
    from agents.nodes import (
        run_ingestion,
        run_political_analyst,
        run_legal_compliance,
        run_dictamen_agent,
        run_report_generator,
    )
    AGENTS_AVAILABLE = True
except Exception:
    AGENTS_AVAILABLE = False

__all__ = [
    "build_workflow",
    "PEIRSState",
    "peirs_pipeline",
    "run_ingestion",
    "run_political_analyst",
    "run_legal_compliance",
    "run_dictamen_agent",
    "run_report_generator",
    "AGENTS_AVAILABLE",
]
