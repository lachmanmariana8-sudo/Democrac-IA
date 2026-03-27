"""
agents/pipeline.py — Pipeline LangGraph de DEMOCRAC.IA (PEIRS)

Extrae de app.py:
  - PEIRSState (TypedDict, alias de ElectionRiskState)
  - build_workflow()  — construye y compila el StateGraph
  - peirs_pipeline    — instancia compilada lista para invocar

Los nodos del grafo se importan desde agents/nodes.py.
Las variables globales (llm, VDEM_DF, etc.) son importadas
desde app.py o desde los módulos de datos si están disponibles.

MIGRADO desde app.py — función build_workflow() (línea ~4071)
"""

from __future__ import annotations

from typing import TypedDict, Dict, List, Any

from langgraph.graph import StateGraph, END


# ── Estado del pipeline (alias de ElectionRiskState en app.py) ────────────────
class PEIRSState(TypedDict):
    run_id: str
    country: str
    country_code: str
    election_date: str
    timestamp: str
    context_data: Dict[str, Any]
    political_data: Dict[str, Any]
    legal_analysis: Dict[str, Any]
    risk_score: float
    risk_level: str
    report_chapters: Dict[str, str]
    executive_summary: str
    final_report_markdown: str
    agent_logs: List[str]
    errors: List[str]
    trace_log: List[Dict]
    applicable_instruments: Dict
    dictamen: Dict
    voting_day_data: Dict


# ── Importación de nodos ───────────────────────────────────────────────────────
try:
    from agents.nodes import (
        run_ingestion,
        run_political_analyst,
        run_legal_compliance,
        run_dictamen_agent,
        run_report_generator,
    )
    _NODES_AVAILABLE = True
except ImportError:
    _NODES_AVAILABLE = False


def build_workflow() -> StateGraph:
    """
    Construye y compila el grafo LangGraph del pipeline PEIRS.

    Nodos:
      Ingestion -> PoliticalAnalyst -> LegalCompliance -> DictamenAgent -> ReportGenerator -> END

    Los nodos son wrappers definidos en agents/nodes.py que delegan
    a las funciones reales en app.py para compatibilidad durante la migración.
    """
    if not _NODES_AVAILABLE:
        # Fallback: importar directamente desde app.py si los nodos no están disponibles
        try:
            from app import (  # type: ignore
                ingestion_agent,
                political_analyst_agent,
                legal_compliance_agent,
                electoral_dictamen_agent,
                report_generator_agent,
                ElectionRiskState,
            )
            workflow = StateGraph(ElectionRiskState)
            workflow.add_node("Ingestion", ingestion_agent)
            workflow.add_node("PoliticalAnalyst", political_analyst_agent)
            workflow.add_node("LegalCompliance", legal_compliance_agent)
            workflow.add_node("DictamenAgent", electoral_dictamen_agent)
            workflow.add_node("ReportGenerator", report_generator_agent)
        except ImportError:
            raise RuntimeError(
                "No se pudo construir el workflow: "
                "ni agents/nodes.py ni app.py están disponibles."
            )
    else:
        workflow = StateGraph(PEIRSState)
        workflow.add_node("Ingestion", run_ingestion)
        workflow.add_node("PoliticalAnalyst", run_political_analyst)
        workflow.add_node("LegalCompliance", run_legal_compliance)
        workflow.add_node("DictamenAgent", run_dictamen_agent)
        workflow.add_node("ReportGenerator", run_report_generator)

    workflow.add_edge("Ingestion", "PoliticalAnalyst")
    workflow.add_edge("PoliticalAnalyst", "LegalCompliance")
    workflow.add_edge("LegalCompliance", "DictamenAgent")
    workflow.add_edge("DictamenAgent", "ReportGenerator")
    workflow.add_edge("ReportGenerator", END)

    workflow.set_entry_point("Ingestion")

    return workflow.compile()


# ── Instancia compilada del pipeline ──────────────────────────────────────────
try:
    peirs_pipeline = build_workflow()
except Exception as _e:
    print(f"[agents/pipeline] AVISO: No se pudo instanciar peirs_pipeline: {_e}")
    peirs_pipeline = None


__all__ = ["PEIRSState", "build_workflow", "peirs_pipeline"]
