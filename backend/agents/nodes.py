"""
agents/nodes.py — Funciones nodo del grafo LangGraph para DEMOCRAC.IA (PEIRS)

Cada función tiene la signature:  (state: PEIRSState) -> PEIRSState

Durante la migración estas funciones son wrappers que delegan en las
implementaciones de app.py, evitando duplicación de código y manteniendo
la funcionalidad intacta.

MIGRADO desde app.py — funciones agente (líneas ~1158–2241)
  - ingestion_agent         → run_ingestion
  - political_analyst_agent → run_political_analyst
  - legal_compliance_agent  → run_legal_compliance
  - electoral_dictamen_agent → run_dictamen_agent
  - report_generator_agent  → run_report_generator
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.pipeline import PEIRSState


# ─────────────────────────────────────────────────────────────────────────────
# Importación de las funciones originales desde app.py
# Se usa importación lazy para evitar importaciones circulares durante el
# arranque del servidor.
# ─────────────────────────────────────────────────────────────────────────────

def _get_app_agents():
    """Importa las funciones agente originales desde app.py."""
    try:
        from app import (  # type: ignore
            ingestion_agent,
            political_analyst_agent,
            legal_compliance_agent,
            electoral_dictamen_agent,
            report_generator_agent,
        )
        return (
            ingestion_agent,
            political_analyst_agent,
            legal_compliance_agent,
            electoral_dictamen_agent,
            report_generator_agent,
        )
    except ImportError as e:
        raise ImportError(
            f"[agents/nodes] No se pudo importar los agentes desde app.py: {e}"
        )


# ── Nodo 1: Ingestion ──────────────────────────────────────────────────────────

def run_ingestion(state: "PEIRSState") -> "PEIRSState":
    """
    Nodo LangGraph — OSINT Ingestion Agent.

    Ingesta datos de fuentes OSINT (Freedom House, V-Dem, PEI, RSF)
    y construye el contexto inicial del estado.

    Delega en `ingestion_agent` de app.py durante la migración.
    """
    ingestion_agent, _, _, _, _ = _get_app_agents()
    return ingestion_agent(state)


# ── Nodo 2: Political Analyst ──────────────────────────────────────────────────

def run_political_analyst(state: "PEIRSState") -> "PEIRSState":
    """
    Nodo LangGraph — Political & Digital Analyst Agent.

    Analiza el ecosistema político-digital: sesgo mediático,
    financiamiento de campaña, red de poder y ecosistema digital.

    Delega en `political_analyst_agent` de app.py durante la migración.
    """
    _, political_analyst_agent, _, _, _ = _get_app_agents()
    return political_analyst_agent(state)


# ── Nodo 3: Legal Compliance ───────────────────────────────────────────────────

def run_legal_compliance(state: "PEIRSState") -> "PEIRSState":
    """
    Nodo LangGraph — Legal Compliance Agent.

    Evalúa violaciones al derecho internacional (ICCPR, CADH, CDI)
    y calcula el score de riesgo electoral.

    Delega en `legal_compliance_agent` de app.py durante la migración.
    """
    _, _, legal_compliance_agent, _, _ = _get_app_agents()
    return legal_compliance_agent(state)


# ── Nodo 4: Dictamen ───────────────────────────────────────────────────────────

def run_dictamen_agent(state: "PEIRSState") -> "PEIRSState":
    """
    Nodo LangGraph — Electoral Dictamen Agent.

    Genera el dictamen técnico de integridad electoral usando LLM
    con datos verificados de Freedom House, V-Dem, PEI y RSF.

    Delega en `electoral_dictamen_agent` de app.py durante la migración.
    """
    _, _, _, electoral_dictamen_agent, _ = _get_app_agents()
    return electoral_dictamen_agent(state)


# ── Nodo 5: Report Generator ───────────────────────────────────────────────────

def run_report_generator(state: "PEIRSState") -> "PEIRSState":
    """
    Nodo LangGraph — VIP Report Generator Agent.

    Genera el informe VIP completo (10 capítulos) con datos estructurados
    y narrativas LLM para cada sección temática.

    Delega en `report_generator_agent` de app.py durante la migración.
    """
    _, _, _, _, report_generator_agent = _get_app_agents()
    return report_generator_agent(state)


__all__ = [
    "run_ingestion",
    "run_political_analyst",
    "run_legal_compliance",
    "run_dictamen_agent",
    "run_report_generator",
]
