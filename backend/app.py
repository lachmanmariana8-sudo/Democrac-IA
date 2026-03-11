"""
DEMOCRAC.IA (PEIRS) — Backend Core
Predictive Electoral Integrity & Risk System

Esqueleto LangGraph + FastAPI con los 4 agentes orquestados.
Los agentes usan datos mock que serán reemplazados por fuentes reales.

Requisitos:
    pip install langgraph langchain-core langchain-anthropic fastapi uvicorn pydantic

Ejecución:
    uvicorn app:app --reload --port 8000

Endpoints:
    POST /api/analyze         → Ejecuta el pipeline completo para un país
    GET  /api/countries       → Lista países disponibles
    GET  /api/report/{id}     → Obtiene el reporte generado
    GET  /api/health          → Health check
"""

from __future__ import annotations

import os
import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import TypedDict, Dict, List, Optional, Any

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_TEMPERATURE = 0.2

# Inicialización del LLM (se usa en agentes 3 y 4)
llm = ChatAnthropic(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    anthropic_api_key=ANTHROPIC_API_KEY,
) if ANTHROPIC_API_KEY else None


# ═══════════════════════════════════════════════════════════════════════════════
# 2. DEFINICIÓN DEL ESTADO GLOBAL (LangGraph State)
# ═══════════════════════════════════════════════════════════════════════════════

class ElectionRiskState(TypedDict):
    """Estado compartido que transita por todos los agentes."""
    # --- Inputs ---
    run_id: str
    country: str
    country_code: str
    election_date: str
    timestamp: str

    # --- Agente 1: Ingesta OSINT ---
    context_data: Dict[str, Any]

    # --- Agente 2: Análisis Político-Digital ---
    political_data: Dict[str, Any]

    # --- Agente 3: Cumplimiento Legal ---
    legal_analysis: Dict[str, Any]

    # --- Agente 4: Reporte VIP ---
    risk_score: float
    risk_level: str
    report_chapters: Dict[str, str]
    executive_summary: str
    final_report_markdown: str

    # --- Metadatos ---
    agent_logs: List[str]
    errors: List[str]


def create_initial_state(country: str, country_code: str, election_date: str) -> ElectionRiskState:
    """Crea el estado inicial para un análisis."""
    return ElectionRiskState(
        run_id=str(uuid.uuid4()),
        country=country,
        country_code=country_code,
        election_date=election_date,
        timestamp=datetime.now(timezone.utc).isoformat(),
        context_data={},
        political_data={},
        legal_analysis={},
        risk_score=0.0,
        risk_level="pending",
        report_chapters={},
        executive_summary="",
        final_report_markdown="",
        agent_logs=[],
        errors=[],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DATOS MOCK (Serán reemplazados por fuentes reales)
# ═══════════════════════════════════════════════════════════════════════════════

MOCK_OSINT_DATA = {
    "VEN": {
        "freedom_house_score": 16,
        "freedom_house_status": "Not Free",
        "vdem_liberal_democracy": 0.12,
        "vdem_electoral_democracy": 0.15,
        "emb_name": "Consejo Nacional Electoral (CNE)",
        "emb_independence": "compromised",
        "emb_opposition_representation": False,
        "registry_status": "no_independent_audit",
        "voter_registry_size": 21_200_000,
        "legal_framework": {
            "constitutional_amendments_recent": True,
            "opposition_party_bans": True,
            "candidate_disqualifications": 3,
            "media_law_restrictions": "severe",
        },
        "civil_liberties": {
            "freedom_of_assembly": "restricted",
            "freedom_of_press": "severely_restricted",
            "judicial_independence": "compromised",
            "political_prisoners": True,
        },
        "international_observation": {
            "invited": False,
            "restrictions": "total_ban_on_independent_observers",
        },
    },
    "NIC": {
        "freedom_house_score": 13,
        "freedom_house_status": "Not Free",
        "vdem_liberal_democracy": 0.08,
        "vdem_electoral_democracy": 0.10,
        "emb_name": "Consejo Supremo Electoral (CSE)",
        "emb_independence": "captured",
        "emb_opposition_representation": False,
        "registry_status": "no_audit",
        "voter_registry_size": 4_500_000,
        "legal_framework": {
            "constitutional_amendments_recent": True,
            "opposition_party_bans": True,
            "candidate_disqualifications": 7,
            "media_law_restrictions": "total",
        },
        "civil_liberties": {
            "freedom_of_assembly": "banned",
            "freedom_of_press": "banned",
            "judicial_independence": "captured",
            "political_prisoners": True,
        },
        "international_observation": {
            "invited": False,
            "restrictions": "all_international_ngos_expelled",
        },
    },
    "GTM": {
        "freedom_house_score": 48,
        "freedom_house_status": "Partly Free",
        "vdem_liberal_democracy": 0.41,
        "vdem_electoral_democracy": 0.48,
        "emb_name": "Tribunal Supremo Electoral (TSE)",
        "emb_independence": "partial",
        "emb_opposition_representation": True,
        "registry_status": "partially_audited",
        "voter_registry_size": 9_300_000,
        "legal_framework": {
            "constitutional_amendments_recent": False,
            "opposition_party_bans": False,
            "candidate_disqualifications": 1,
            "media_law_restrictions": "moderate",
        },
        "civil_liberties": {
            "freedom_of_assembly": "partially_restricted",
            "freedom_of_press": "partially_restricted",
            "judicial_independence": "under_pressure",
            "political_prisoners": False,
        },
        "international_observation": {
            "invited": True,
            "restrictions": "some_access_limitations",
        },
    },
    "URY": {
        "freedom_house_score": 97,
        "freedom_house_status": "Free",
        "vdem_liberal_democracy": 0.89,
        "vdem_electoral_democracy": 0.92,
        "emb_name": "Corte Electoral",
        "emb_independence": "full",
        "emb_opposition_representation": True,
        "registry_status": "fully_audited",
        "voter_registry_size": 2_700_000,
        "legal_framework": {
            "constitutional_amendments_recent": False,
            "opposition_party_bans": False,
            "candidate_disqualifications": 0,
            "media_law_restrictions": "none",
        },
        "civil_liberties": {
            "freedom_of_assembly": "guaranteed",
            "freedom_of_press": "guaranteed",
            "judicial_independence": "strong",
            "political_prisoners": False,
        },
        "international_observation": {
            "invited": True,
            "restrictions": "none",
        },
    },
}

MOCK_POLITICAL_DATA = {
    "VEN": {
        "media_bias_index": 0.78,
        "media_bias_direction": "pro_incumbent",
        "media_exposure": {
            "incumbent": 78, "opposition_a": 12, "opposition_b": 7, "others": 3,
        },
        "campaign_finance": {
            "transparency_score": 0.15,
            "state_resource_abuse": "systematic",
            "corporate_donations_disclosed": False,
        },
        "digital_ecosystem": {
            "bot_activity_detected": True,
            "bot_network_size_estimate": 45_000,
            "hate_speech_incidents": 342,
            "url_censorship_detected": True,
            "censored_domains": ["www.example-opposition-media.com"],
            "disinformation_campaigns": 12,
            "voter_suppression_tactics_online": True,
        },
        "power_network": {
            "candidate_media_ownership_links": 3,
            "state_enterprise_campaign_links": 5,
            "military_political_links": True,
        },
    },
    "NIC": {
        "media_bias_index": 0.91,
        "media_bias_direction": "pro_incumbent",
        "media_exposure": {
            "incumbent": 91, "opposition": 4, "independent": 3, "others": 2,
        },
        "campaign_finance": {
            "transparency_score": 0.05,
            "state_resource_abuse": "total",
            "corporate_donations_disclosed": False,
        },
        "digital_ecosystem": {
            "bot_activity_detected": True,
            "bot_network_size_estimate": 28_000,
            "hate_speech_incidents": 567,
            "url_censorship_detected": True,
            "censored_domains": ["confidencial.digital", "100noticias.com.ni"],
            "disinformation_campaigns": 23,
            "voter_suppression_tactics_online": True,
        },
        "power_network": {
            "candidate_media_ownership_links": 7,
            "state_enterprise_campaign_links": 12,
            "military_political_links": True,
        },
    },
    "GTM": {
        "media_bias_index": 0.42,
        "media_bias_direction": "mixed",
        "media_exposure": {
            "party_a": 38, "party_b": 32, "party_c": 18, "others": 12,
        },
        "campaign_finance": {
            "transparency_score": 0.40,
            "state_resource_abuse": "moderate",
            "corporate_donations_disclosed": True,
        },
        "digital_ecosystem": {
            "bot_activity_detected": True,
            "bot_network_size_estimate": 8_000,
            "hate_speech_incidents": 89,
            "url_censorship_detected": False,
            "censored_domains": [],
            "disinformation_campaigns": 4,
            "voter_suppression_tactics_online": False,
        },
        "power_network": {
            "candidate_media_ownership_links": 2,
            "state_enterprise_campaign_links": 1,
            "military_political_links": False,
        },
    },
    "URY": {
        "media_bias_index": 0.15,
        "media_bias_direction": "balanced",
        "media_exposure": {
            "frente_amplio": 35, "partido_nacional": 33, "partido_colorado": 20, "others": 12,
        },
        "campaign_finance": {
            "transparency_score": 0.82,
            "state_resource_abuse": "none_detected",
            "corporate_donations_disclosed": True,
        },
        "digital_ecosystem": {
            "bot_activity_detected": False,
            "bot_network_size_estimate": 0,
            "hate_speech_incidents": 12,
            "url_censorship_detected": False,
            "censored_domains": [],
            "disinformation_campaigns": 0,
            "voter_suppression_tactics_online": False,
        },
        "power_network": {
            "candidate_media_ownership_links": 0,
            "state_enterprise_campaign_links": 0,
            "military_political_links": False,
        },
    },
}

# Catálogo de países disponibles para análisis
COUNTRY_CATALOG = {
    "VEN": {"name": "Venezuela", "flag": "🇻🇪", "election_date": "2025-12-07"},
    "NIC": {"name": "Nicaragua", "flag": "🇳🇮", "election_date": "2026-03-15"},
    "GTM": {"name": "Guatemala", "flag": "🇬🇹", "election_date": "2027-06-25"},
    "URY": {"name": "Uruguay", "flag": "🇺🇾", "election_date": "2029-10-26"},
}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. AGENTES (Nodos del Grafo LangGraph)
# ═══════════════════════════════════════════════════════════════════════════════

def agent_log(state: ElectionRiskState, agent: str, message: str) -> None:
    """Registra actividad de un agente en el log."""
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    state["agent_logs"].append(f"[{timestamp}] [{agent}] {message}")


# ─── AGENTE 1: OSINT Ingestion Agent ─────────────────────────────────────────

def ingestion_agent(state: ElectionRiskState) -> ElectionRiskState:
    """
    Agente de Ingesta y Contexto (OSINT).
    
    En producción:
        - Consulta APIs de Freedom House y V-Dem
        - Scraping con Playwright a portales de EMBs
        - Extrae marco legal, padrón y datos institucionales
        - Almacena en PostgreSQL
    
    Ahora: Usa datos mock del diccionario MOCK_OSINT_DATA.
    """
    agent_name = "OSINT_IngestionAgent"
    agent_log(state, agent_name, f"Iniciando ingesta para {state['country']} ({state['country_code']})")

    code = state["country_code"]

    if code not in MOCK_OSINT_DATA:
        state["errors"].append(f"No hay datos OSINT disponibles para {code}")
        agent_log(state, agent_name, f"ERROR: País {code} no encontrado en fuentes")
        state["context_data"] = {}
        return state

    # === AQUÍ SE CONECTARÁN LAS FUENTES REALES ===
    # TODO: freedom_house_data = await fetch_freedom_house_api(code)
    # TODO: vdem_data = await fetch_vdem_api(code)
    # TODO: emb_data = await scrape_emb_portal(code)
    # TODO: legal_data = await scrape_legal_framework(code)

    osint = MOCK_OSINT_DATA[code]

    context = {
        "source": "mock_data_v1",
        "country": state["country"],
        "country_code": code,
        "collected_at": datetime.now(timezone.utc).isoformat(),

        # Índices internacionales
        "freedom_house": {
            "score": osint["freedom_house_score"],
            "status": osint["freedom_house_status"],
        },
        "vdem": {
            "liberal_democracy": osint["vdem_liberal_democracy"],
            "electoral_democracy": osint["vdem_electoral_democracy"],
        },

        # Administración Electoral (EMB)
        "emb": {
            "name": osint["emb_name"],
            "independence_level": osint["emb_independence"],
            "opposition_representation": osint["emb_opposition_representation"],
        },

        # Padrón electoral
        "voter_registry": {
            "status": osint["registry_status"],
            "size": osint["voter_registry_size"],
        },

        # Marco legal
        "legal_framework": osint["legal_framework"],

        # Libertades civiles
        "civil_liberties": osint["civil_liberties"],

        # Observación internacional
        "international_observation": osint["international_observation"],
    }

    state["context_data"] = context
    agent_log(state, agent_name, f"Ingesta completada. Freedom House: {osint['freedom_house_score']}/100, V-Dem: {osint['vdem_liberal_democracy']}")
    agent_log(state, agent_name, f"EMB independencia: {osint['emb_independence']}, Observación internacional: {'permitida' if osint['international_observation']['invited'] else 'restringida'}")

    return state


# ─── AGENTE 2: Political & Digital Analyst Agent ─────────────────────────────

def political_analyst_agent(state: ElectionRiskState) -> ElectionRiskState:
    """
    Agente de Competitividad, Medios y Ecosistema Digital.
    
    En producción:
        - Construye grafos de poder en Neo4j
        - Monitorea redes sociales (X, Facebook, TikTok)
        - Analiza cobertura mediática y financiamiento
        - Detecta bots, desinformación y discurso de odio
    
    Ahora: Usa datos mock del diccionario MOCK_POLITICAL_DATA.
    """
    agent_name = "Political_DigitalAnalystAgent"
    agent_log(state, agent_name, f"Iniciando análisis político-digital para {state['country']}")

    code = state["country_code"]

    if code not in MOCK_POLITICAL_DATA:
        state["errors"].append(f"No hay datos políticos disponibles para {code}")
        state["political_data"] = {}
        return state

    # === AQUÍ SE CONECTARÁN LAS FUENTES REALES ===
    # TODO: neo4j_graph = await build_power_network(code)
    # TODO: social_data = await monitor_social_media(code)
    # TODO: media_data = await analyze_media_coverage(code)

    political = MOCK_POLITICAL_DATA[code]

    analysis = {
        "source": "mock_data_v1",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),

        # Sesgo mediático
        "media_analysis": {
            "bias_index": political["media_bias_index"],
            "bias_direction": political["media_bias_direction"],
            "exposure_distribution": political["media_exposure"],
            "assessment": _assess_media_bias(political["media_bias_index"]),
        },

        # Financiamiento de campaña
        "campaign_finance": {
            "transparency_score": political["campaign_finance"]["transparency_score"],
            "state_resource_abuse": political["campaign_finance"]["state_resource_abuse"],
            "donations_disclosed": political["campaign_finance"]["corporate_donations_disclosed"],
            "assessment": _assess_finance_transparency(political["campaign_finance"]["transparency_score"]),
        },

        # Ecosistema digital
        "digital_ecosystem": {
            "bot_activity": political["digital_ecosystem"]["bot_activity_detected"],
            "bot_network_size": political["digital_ecosystem"]["bot_network_size_estimate"],
            "hate_speech_incidents": political["digital_ecosystem"]["hate_speech_incidents"],
            "censorship_detected": political["digital_ecosystem"]["url_censorship_detected"],
            "censored_domains": political["digital_ecosystem"]["censored_domains"],
            "disinformation_campaigns": political["digital_ecosystem"]["disinformation_campaigns"],
            "voter_suppression_online": political["digital_ecosystem"]["voter_suppression_tactics_online"],
            "assessment": _assess_digital_ecosystem(political["digital_ecosystem"]),
        },

        # Red de poder (para Neo4j)
        "power_network": {
            "media_ownership_links": political["power_network"]["candidate_media_ownership_links"],
            "state_enterprise_links": political["power_network"]["state_enterprise_campaign_links"],
            "military_links": political["power_network"]["military_political_links"],
            "capture_risk": _assess_capture_risk(political["power_network"]),
        },
    }

    state["political_data"] = analysis

    agent_log(state, agent_name, f"Sesgo mediático: {political['media_bias_index']:.2f} ({political['media_bias_direction']})")
    agent_log(state, agent_name, f"Ecosistema digital — Bots: {'SÍ' if political['digital_ecosystem']['bot_activity_detected'] else 'NO'}, Censura: {'SÍ' if political['digital_ecosystem']['url_censorship_detected'] else 'NO'}")
    agent_log(state, agent_name, f"Red de poder — Vínculos medios: {political['power_network']['candidate_media_ownership_links']}, Empresas estatales: {political['power_network']['state_enterprise_campaign_links']}")

    return state


def _assess_media_bias(index: float) -> str:
    if index >= 0.7: return "severe_asymmetry"
    if index >= 0.4: return "moderate_asymmetry"
    return "acceptable_balance"

def _assess_finance_transparency(score: float) -> str:
    if score >= 0.7: return "transparent"
    if score >= 0.4: return "partially_transparent"
    return "opaque"

def _assess_digital_ecosystem(data: dict) -> str:
    threats = sum([
        data["bot_activity_detected"],
        data["url_censorship_detected"],
        data["voter_suppression_tactics_online"],
        data["disinformation_campaigns"] > 5,
        data["hate_speech_incidents"] > 100,
    ])
    if threats >= 4: return "hostile"
    if threats >= 2: return "compromised"
    if threats >= 1: return "concerning"
    return "healthy"

def _assess_capture_risk(network: dict) -> str:
    links = network["candidate_media_ownership_links"] + network["state_enterprise_campaign_links"]
    if network["military_political_links"] or links >= 8: return "high_capture"
    if links >= 3: return "moderate_capture"
    return "low_capture"


# ─── AGENTE 3: Legal Compliance Agent (RAG) ──────────────────────────────────

def legal_compliance_agent(state: ElectionRiskState) -> ElectionRiskState:
    """
    Agente de Cumplimiento Legal y RAG.
    
    En producción:
        - Consulta semántica a Vector DB (Pinecone/Qdrant)
        - Corpus: +300 documentos del Centro Carter, ICCPR, CEDAW, ICERD
        - Vincula cada irregularidad a artículos específicos
        - Rastrea resoluciones de tribunales electorales
    
    Ahora: Usa lógica rule-based para mapear irregularidades a violaciones.
    En la siguiente fase, el LLM + RAG reemplaza estas reglas.
    """
    agent_name = "Legal_ComplianceAgent"
    agent_log(state, agent_name, f"Iniciando análisis legal para {state['country']}")

    context = state.get("context_data", {})
    political = state.get("political_data", {})

    violations = []
    risk_factors = []
    mitigating_factors = []

    # ── Análisis de libertades civiles vs ICCPR ──

    civil = context.get("civil_liberties", {})

    if civil.get("freedom_of_press") in ["severely_restricted", "banned"]:
        violations.append({
            "treaty": "ICCPR",
            "article": "Art. 19",
            "right": "Libertad de Expresión",
            "finding": f"Libertad de prensa clasificada como '{civil['freedom_of_press']}'. "
                       "Violación directa del derecho a buscar, recibir y difundir información.",
            "severity": "critical",
        })

    if civil.get("freedom_of_assembly") in ["restricted", "banned"]:
        violations.append({
            "treaty": "ICCPR",
            "article": "Art. 21 & Art. 22",
            "right": "Libertad de Reunión y Asociación",
            "finding": f"Libertad de reunión clasificada como '{civil['freedom_of_assembly']}'. "
                       "Restricciones incompatibles con el derecho a la reunión pacífica.",
            "severity": "critical" if civil["freedom_of_assembly"] == "banned" else "high",
        })

    if civil.get("political_prisoners"):
        violations.append({
            "treaty": "ICCPR",
            "article": "Art. 9",
            "right": "Libertad y Seguridad Personal",
            "finding": "Existencia documentada de presos políticos. "
                       "Detención arbitraria de opositores viola el derecho a la libertad personal.",
            "severity": "critical",
        })

    if civil.get("judicial_independence") in ["compromised", "captured"]:
        violations.append({
            "treaty": "ICCPR",
            "article": "Art. 14",
            "right": "Derecho a un Tribunal Independiente",
            "finding": f"Independencia judicial clasificada como '{civil['judicial_independence']}'. "
                       "Compromete el derecho a un recurso efectivo ante disputas electorales.",
            "severity": "critical" if civil["judicial_independence"] == "captured" else "high",
        })

    # ── Análisis de administración electoral vs ICCPR Art. 25 ──

    emb = context.get("emb", {})
    legal_fw = context.get("legal_framework", {})

    if emb.get("independence_level") in ["compromised", "captured"]:
        violations.append({
            "treaty": "ICCPR",
            "article": "Art. 25",
            "right": "Derecho a Participar en Asuntos Públicos",
            "finding": f"EMB ({emb.get('name', 'N/A')}) con independencia '{emb['independence_level']}'. "
                       "Administración electoral sin garantías de imparcialidad.",
            "severity": "critical" if emb["independence_level"] == "captured" else "high",
        })

    if legal_fw.get("candidate_disqualifications", 0) > 0 and legal_fw.get("opposition_party_bans"):
        violations.append({
            "treaty": "ICCPR",
            "article": "Art. 25(b)",
            "right": "Derecho a Ser Elegido",
            "finding": f"{legal_fw['candidate_disqualifications']} candidatos inhabilitados con partidos prohibidos. "
                       "Restricción al derecho de postulación sin garantías de debido proceso.",
            "severity": "critical",
        })

    # ── Análisis del ecosistema digital vs libertad de expresión ──

    digital = political.get("digital_ecosystem", {})

    if digital.get("censorship_detected"):
        violations.append({
            "treaty": "ICCPR",
            "article": "Art. 19(2)",
            "right": "Libertad de Expresión Digital",
            "finding": f"Censura de dominios web detectada: {digital.get('censored_domains', [])}. "
                       "Bloqueo de medios digitales constituye restricción a la libertad de expresión.",
            "severity": "high",
        })

    if digital.get("voter_suppression_online"):
        violations.append({
            "treaty": "ICCPR",
            "article": "Art. 25(a)",
            "right": "Sufragio Universal",
            "finding": "Tácticas de supresión de votantes online detectadas. "
                       "Manipulación digital que interfiere con el ejercicio libre del sufragio.",
            "severity": "high",
        })

    # ── Observación internacional ──

    obs = context.get("international_observation", {})

    if not obs.get("invited", True):
        risk_factors.append({
            "category": "Transparencia",
            "finding": "Observación internacional no invitada o restringida. "
                       "Incumplimiento de la Declaración de Principios para la Observación Internacional.",
            "severity": "high",
        })

    # ── Factores mitigantes ──

    if emb.get("independence_level") == "full":
        mitigating_factors.append("EMB plenamente independiente con representación multipartidaria")

    if context.get("freedom_house", {}).get("score", 0) >= 80:
        mitigating_factors.append("Alto puntaje Freedom House indica garantías institucionales sólidas")

    if not digital.get("bot_activity") and not digital.get("censorship_detected"):
        mitigating_factors.append("Ecosistema digital saludable sin manipulación detectada")

    # ── Cálculo del Risk Score ──

    risk_score = _calculate_risk_score(context, political, violations)
    risk_level = _risk_level_from_score(risk_score)

    state["legal_analysis"] = {
        "source": "rule_based_v1",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "violations": violations,
        "violation_count": len(violations),
        "risk_factors": risk_factors,
        "mitigating_factors": mitigating_factors,
        "treaties_referenced": list(set(v["treaty"] for v in violations)),
        "articles_referenced": list(set(f"{v['treaty']} {v['article']}" for v in violations)),
    }

    state["risk_score"] = risk_score
    state["risk_level"] = risk_level

    agent_log(state, agent_name, f"Violaciones detectadas: {len(violations)}")
    agent_log(state, agent_name, f"Tratados referenciados: {state['legal_analysis']['treaties_referenced']}")
    agent_log(state, agent_name, f"Risk Score calculado: {risk_score}/100 → Nivel: {risk_level.upper()}")

    return state


def _calculate_risk_score(context: dict, political: dict, violations: list) -> float:
    """Calcula el índice de riesgo 0-100 basado en múltiples dimensiones."""
    score = 0.0

    # Dimensión 1: Freedom House (invertido: menor score = más riesgo)
    fh = context.get("freedom_house", {}).get("score", 50)
    score += (100 - fh) * 0.15

    # Dimensión 2: V-Dem (invertido)
    vdem = context.get("vdem", {}).get("liberal_democracy", 0.5)
    score += (1 - vdem) * 100 * 0.15

    # Dimensión 3: Independencia EMB
    emb_scores = {"full": 0, "partial": 40, "compromised": 75, "captured": 95}
    emb_level = context.get("emb", {}).get("independence_level", "partial")
    score += emb_scores.get(emb_level, 50) * 0.15

    # Dimensión 4: Sesgo mediático
    media_bias = political.get("media_analysis", {}).get("bias_index", 0.3)
    score += media_bias * 100 * 0.10

    # Dimensión 5: Financiamiento (invertido)
    finance = political.get("campaign_finance", {}).get("transparency_score", 0.5)
    score += (1 - finance) * 100 * 0.10

    # Dimensión 6: Ecosistema digital
    eco_scores = {"healthy": 0, "concerning": 30, "compromised": 65, "hostile": 90}
    eco_level = political.get("digital_ecosystem", {}).get("assessment", "concerning")
    score += eco_scores.get(eco_level, 40) * 0.10

    # Dimensión 7: Violaciones legales
    violation_weight = min(len(violations) * 8, 100)
    score += violation_weight * 0.15

    # Dimensión 8: Observación internacional
    obs = context.get("international_observation", {})
    if not obs.get("invited", True):
        score += 90 * 0.10
    elif obs.get("restrictions", "none") != "none":
        score += 45 * 0.10

    return round(min(max(score, 0), 100), 1)


def _risk_level_from_score(score: float) -> str:
    if score >= 75: return "critical"
    if score >= 50: return "high"
    if score >= 25: return "moderate"
    return "low"


# ─── AGENTE 4: VIP Report Generator Agent ────────────────────────────────────

def report_generator_agent(state: ElectionRiskState) -> ElectionRiskState:
    """
    Agente Redactor del Informe VIP.
    
    En producción:
        - Usa Claude para generar narrativa ejecutiva
        - Exporta a LaTeX/PDF con Pandoc
        - Genera gráficos incrustados
    
    Ahora: Genera reporte Markdown estructurado.
    Si hay API key de Anthropic, usa Claude para el resumen ejecutivo.
    Si no, genera un resumen template-based.
    """
    agent_name = "VIP_ReportGeneratorAgent"
    agent_log(state, agent_name, f"Generando informe VIP para {state['country']}")

    context = state.get("context_data", {})
    political = state.get("political_data", {})
    legal = state.get("legal_analysis", {})

    # ── Generar capítulos modulares ──
    chapters = {}

    chapters["01_executive_summary"] = _generate_executive_summary(state)
    chapters["02_political_context"] = _generate_political_context(context)
    chapters["03_emb_analysis"] = _generate_emb_chapter(context)
    chapters["04_inclusivity"] = _generate_inclusivity_chapter(context)
    chapters["05_campaign_finance"] = _generate_campaign_chapter(political)
    chapters["06_digital_ecosystem"] = _generate_digital_chapter(political)
    chapters["07_voting_day"] = "## 7. Desarrollo del Día de Votación\n\n*Capítulo pendiente — se genera el día de la elección con datos de tabulación en tiempo real.*\n"
    chapters["08_electoral_justice"] = _generate_justice_chapter(legal)
    chapters["09_recommendations"] = _generate_recommendations(state)

    # ── Compilar reporte final ──
    report_header = f"""# DEMOCRAC.IA — Informe VIP de Integridad Electoral
## {state['country']} — Elección: {state['election_date']}

**Índice Predictivo de Riesgo:** {state['risk_score']}/100 ({state['risk_level'].upper()})
**Generado:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
**Run ID:** `{state['run_id']}`

---

"""

    full_report = report_header + "\n\n".join(chapters.values())

    state["report_chapters"] = chapters
    state["executive_summary"] = chapters["01_executive_summary"]
    state["final_report_markdown"] = full_report

    agent_log(state, agent_name, f"Informe generado: {len(chapters)} capítulos, {len(full_report)} caracteres")

    return state


def _generate_executive_summary(state: ElectionRiskState) -> str:
    legal = state.get("legal_analysis", {})
    violations = legal.get("violations", [])
    critical = [v for v in violations if v.get("severity") == "critical"]

    level_emoji = {"critical": "🔴", "high": "🟠", "moderate": "🟡", "low": "🟢"}
    emoji = level_emoji.get(state["risk_level"], "⚪")

    summary = f"""## 1. Resumen Ejecutivo & Dashboard de Riesgo

{emoji} **Nivel de Riesgo: {state['risk_level'].upper()}** — Índice: **{state['risk_score']}/100**

| Dimensión | Evaluación |
|---|---|
| Freedom House | {state['context_data'].get('freedom_house', {}).get('score', 'N/A')}/100 ({state['context_data'].get('freedom_house', {}).get('status', 'N/A')}) |
| V-Dem Liberal Democracy | {state['context_data'].get('vdem', {}).get('liberal_democracy', 'N/A')} |
| Independencia EMB | {state['context_data'].get('emb', {}).get('independence_level', 'N/A').upper()} |
| Violaciones detectadas | {len(violations)} ({len(critical)} críticas) |
| Tratados referenciados | {', '.join(legal.get('treaties_referenced', []))} |

**Alertas críticas:** {len(critical)} violaciones de severidad crítica al derecho internacional detectadas.
"""
    if legal.get("mitigating_factors"):
        summary += f"\n**Factores mitigantes:** {'; '.join(legal['mitigating_factors'])}\n"

    return summary


def _generate_political_context(context: dict) -> str:
    legal_fw = context.get("legal_framework", {})
    civil = context.get("civil_liberties", {})

    return f"""## 2. Contexto Político y Marco Legal

**Marco Legal Electoral:**
- Reformas constitucionales recientes: {'Sí' if legal_fw.get('constitutional_amendments_recent') else 'No'}
- Prohibición de partidos opositores: {'Sí' if legal_fw.get('opposition_party_bans') else 'No'}
- Candidatos inhabilitados: {legal_fw.get('candidate_disqualifications', 0)}
- Restricciones a medios: {legal_fw.get('media_law_restrictions', 'N/A')}

**Estado de Libertades Civiles:**
- Libertad de reunión: {civil.get('freedom_of_assembly', 'N/A')}
- Libertad de prensa: {civil.get('freedom_of_press', 'N/A')}
- Independencia judicial: {civil.get('judicial_independence', 'N/A')}
- Presos políticos: {'Sí' if civil.get('political_prisoners') else 'No'}
"""


def _generate_emb_chapter(context: dict) -> str:
    emb = context.get("emb", {})
    registry = context.get("voter_registry", {})
    obs = context.get("international_observation", {})

    return f"""## 3. Administración Electoral (EMB)

**{emb.get('name', 'N/A')}**
- Nivel de independencia: **{emb.get('independence_level', 'N/A').upper()}**
- Representación opositora: {'Sí' if emb.get('opposition_representation') else 'No'}

**Padrón Electoral:**
- Estado de auditoría: {registry.get('status', 'N/A')}
- Votantes registrados: {registry.get('size', 'N/A'):,}

**Observación Internacional:**
- Invitación: {'Sí' if obs.get('invited') else 'No'}
- Restricciones: {obs.get('restrictions', 'N/A')}
"""


def _generate_inclusivity_chapter(context: dict) -> str:
    return """## 4. Inclusividad y Derechos Humanos

*Análisis detallado de barreras hacia mujeres (CEDAW), minorías y pueblos indígenas (ICERD) será generado con datos del Agente OSINT en producción.*

**Pendiente:** Integración con indicadores de participación desagregados por género y etnicidad.
"""


def _generate_campaign_chapter(political: dict) -> str:
    media = political.get("media_analysis", {})
    finance = political.get("campaign_finance", {})
    power = political.get("power_network", {})

    exposure_lines = "\n".join(
        f"  - {k}: {v}%" for k, v in media.get("exposure_distribution", {}).items()
    )

    return f"""## 5. Campaña, Redes de Poder y Financiamiento

**Análisis de Medios:**
- Índice de sesgo: {media.get('bias_index', 'N/A')} ({media.get('assessment', 'N/A')})
- Dirección del sesgo: {media.get('bias_direction', 'N/A')}
- Distribución de exposición:
{exposure_lines}

**Financiamiento de Campaña:**
- Transparencia: {finance.get('transparency_score', 'N/A')} ({finance.get('assessment', 'N/A')})
- Abuso de recursos estatales: {finance.get('state_resource_abuse', 'N/A')}
- Donaciones corporativas divulgadas: {'Sí' if finance.get('donations_disclosed') else 'No'}

**Red de Poder (GraphOS):**
- Vínculos candidato-medios: {power.get('media_ownership_links', 0)}
- Vínculos con empresas estatales: {power.get('state_enterprise_links', 0)}
- Vínculos militares-políticos: {'Sí' if power.get('military_links') else 'No'}
- Riesgo de captura: {power.get('capture_risk', 'N/A')}
"""


def _generate_digital_chapter(political: dict) -> str:
    digital = political.get("digital_ecosystem", {})

    return f"""## 6. Ecosistema de Información y Monitoreo Digital

**Evaluación general:** {digital.get('assessment', 'N/A').upper()}

**Manipulación Coordinada:**
- Actividad de bots detectada: {'Sí' if digital.get('bot_activity') else 'No'}
- Tamaño estimado de red de bots: {digital.get('bot_network_size', 0):,}
- Campañas de desinformación: {digital.get('disinformation_campaigns', 0)}

**Censura y Supresión:**
- Censura de URLs detectada: {'Sí' if digital.get('censorship_detected') else 'No'}
- Dominios censurados: {', '.join(digital.get('censored_domains', [])) or 'Ninguno'}
- Supresión de votantes online: {'Sí' if digital.get('voter_suppression_online') else 'No'}

**Discurso de Odio:**
- Incidentes detectados: {digital.get('hate_speech_incidents', 0)}
"""


def _generate_justice_chapter(legal: dict) -> str:
    violations = legal.get("violations", [])

    if not violations:
        return """## 8. Justicia Electoral y Resolución de Disputas

No se detectaron violaciones al derecho internacional en el proceso analizado. El sistema de justicia electoral opera dentro de los parámetros de los estándares EOS.
"""

    violation_lines = "\n".join(
        f"| {v['treaty']} {v['article']} | {v['right']} | {v['severity'].upper()} | {v['finding'][:80]}... |"
        for v in violations
    )

    return f"""## 8. Justicia Electoral y Resolución de Disputas

**Violaciones al Derecho Internacional Detectadas: {len(violations)}**

| Referencia Legal | Derecho Afectado | Severidad | Hallazgo |
|---|---|---|---|
{violation_lines}

**Artículos referenciados:** {', '.join(legal.get('articles_referenced', []))}

**Factores agravantes:** Patrón sistemático de violaciones en múltiples dimensiones.
"""


def _generate_recommendations(state: ElectionRiskState) -> str:
    risk = state["risk_level"]

    if risk == "critical":
        outlook = "**ALERTA MÁXIMA** — Condiciones electorales severamente comprometidas. Alto riesgo de resultados no representativos."
        investor_impact = "Riesgo elevado de inestabilidad post-electoral, sanciones internacionales y volatilidad macroeconómica."
    elif risk == "high":
        outlook = "**PRECAUCIÓN** — Irregularidades significativas detectadas. Proceso electoral con deficiencias estructurales."
        investor_impact = "Riesgo moderado-alto de disputas prolongadas y cambios regulatorios abruptos."
    elif risk == "moderate":
        outlook = "**MONITOREO** — Proceso con deficiencias puntuales pero dentro de márgenes manejables."
        investor_impact = "Riesgo moderado. Recomendable monitoreo continuo de indicadores clave."
    else:
        outlook = "**ESTABLE** — Proceso electoral dentro de estándares internacionales aceptables."
        investor_impact = "Bajo riesgo político. Entorno institucional favorable para operaciones."

    return f"""## 9. Matriz de Recomendaciones VIP

**Proyección:** {outlook}

**Impacto para Inversores y Analistas:** {investor_impact}

**Índice Predictivo Final:** {state['risk_score']}/100 ({state['risk_level'].upper()})

---
*Informe generado por DEMOCRAC.IA (PEIRS) v0.1.0 — Sistema de Inteligencia Electoral OSINT*
*Los datos presentados son para fines analíticos y predictivos. PEIRS no valida ni legitima resultados electorales.*
"""


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CONSTRUCCIÓN DEL GRAFO (LangGraph Workflow)
# ═══════════════════════════════════════════════════════════════════════════════

def build_workflow() -> StateGraph:
    """Construye y compila el grafo de agentes."""
    workflow = StateGraph(ElectionRiskState)

    # Añadir nodos (agentes)
    workflow.add_node("Ingestion", ingestion_agent)
    workflow.add_node("PoliticalAnalyst", political_analyst_agent)
    workflow.add_node("LegalCompliance", legal_compliance_agent)
    workflow.add_node("ReportGenerator", report_generator_agent)

    # Definir flujo secuencial
    workflow.add_edge("Ingestion", "PoliticalAnalyst")
    workflow.add_edge("PoliticalAnalyst", "LegalCompliance")
    workflow.add_edge("LegalCompliance", "ReportGenerator")
    workflow.add_edge("ReportGenerator", END)

    workflow.set_entry_point("Ingestion")

    return workflow.compile()


# Compilar la app de LangGraph
peirs_pipeline = build_workflow()


# ═══════════════════════════════════════════════════════════════════════════════
# 6. API (FastAPI)
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="DEMOCRAC.IA — PEIRS API",
    description="Predictive Electoral Integrity & Risk System — API de Inteligencia Electoral OSINT",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: restringir a dominio del dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacén de reportes en memoria (en producción: PostgreSQL)
reports_store: Dict[str, dict] = {}


class AnalyzeRequest(BaseModel):
    country_code: str
    election_date: str | None = None


class AnalyzeResponse(BaseModel):
    run_id: str
    country: str
    risk_score: float
    risk_level: str
    violation_count: int
    status: str


@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "system": "DEMOCRAC.IA (PEIRS)",
        "version": "0.1.0",
        "llm_configured": llm is not None,
        "countries_available": len(COUNTRY_CATALOG),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/countries")
async def list_countries():
    return {
        "countries": [
            {
                "code": code,
                "name": info["name"],
                "flag": info["flag"],
                "election_date": info["election_date"],
            }
            for code, info in COUNTRY_CATALOG.items()
        ]
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_election(request: AnalyzeRequest):
    code = request.country_code.upper()

    if code not in COUNTRY_CATALOG:
        raise HTTPException(
            status_code=404,
            detail=f"País '{code}' no encontrado. Disponibles: {list(COUNTRY_CATALOG.keys())}",
        )

    country_info = COUNTRY_CATALOG[code]
    election_date = request.election_date or country_info["election_date"]

    # Crear estado inicial
    initial_state = create_initial_state(
        country=country_info["name"],
        country_code=code,
        election_date=election_date,
    )

    # Ejecutar pipeline completo
    result = peirs_pipeline.invoke(initial_state)

    # Almacenar resultado
    reports_store[result["run_id"]] = result

    return AnalyzeResponse(
        run_id=result["run_id"],
        country=result["country"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        violation_count=result["legal_analysis"].get("violation_count", 0),
        status="completed",
    )


@app.get("/api/report/{run_id}")
async def get_report(run_id: str):
    if run_id not in reports_store:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    result = reports_store[run_id]

    return {
        "run_id": run_id,
        "country": result["country"],
        "country_code": result["country_code"],
        "election_date": result["election_date"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "legal_analysis": result["legal_analysis"],
        "context_data": result["context_data"],
        "political_data": result["political_data"],
        "report_chapters": result["report_chapters"],
        "executive_summary": result["executive_summary"],
        "final_report_markdown": result["final_report_markdown"],
        "agent_logs": result["agent_logs"],
        "errors": result["errors"],
        "timestamp": result["timestamp"],
    }


@app.get("/api/report/{run_id}/markdown")
async def get_report_markdown(run_id: str):
    if run_id not in reports_store:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    return {
        "run_id": run_id,
        "markdown": reports_store[run_id]["final_report_markdown"],
    }


@app.get("/api/dashboard")
async def get_dashboard_data():
    """
    Ejecuta el pipeline para todos los países y devuelve datos
    formateados para el dashboard React.
    """
    dashboard_countries = []

    for code, info in COUNTRY_CATALOG.items():
        # Ejecutar pipeline
        state = create_initial_state(
            country=info["name"],
            country_code=code,
            election_date=info["election_date"],
        )
        result = peirs_pipeline.invoke(state)
        reports_store[result["run_id"]] = result

        # Extraer datos para el dashboard
        context = result.get("context_data", {})
        political = result.get("political_data", {})
        legal = result.get("legal_analysis", {})

        # Construir media_data desde exposure_distribution
        exposure = political.get("media_analysis", {}).get("exposure_distribution", {})
        media_data = [
            {"name": k.replace("_", " ").title(), "exposure": v, "sentiment": 0}
            for k, v in exposure.items()
        ]

        # Construir violations list (strings simplificados)
        violations_simple = [
            f"{v['treaty']} {v['article']}" for v in legal.get("violations", [])
        ]

        # Construir dimensions desde los datos reales del scoring
        emb_scores = {"full": 95, "partial": 60, "compromised": 25, "captured": 5}
        emb_level = context.get("emb", {}).get("independence_level", "partial")

        eco_scores = {"healthy": 90, "concerning": 60, "compromised": 35, "hostile": 10}
        eco_level = political.get("digital_ecosystem", {}).get("assessment", "concerning")

        finance_score = political.get("campaign_finance", {}).get("transparency_score", 0.5)

        fh = context.get("freedom_house", {}).get("score", 50)
        vdem_val = context.get("vdem", {}).get("liberal_democracy", 0.5)

        media_bias = political.get("media_analysis", {}).get("bias_index", 0.3)

        dimensions = {
            "suffrage": max(5, int(fh * 0.9)),
            "legalFramework": max(5, int(vdem_val * 100)),
            "embIndependence": emb_scores.get(emb_level, 50),
            "mediaFreedom": max(5, int((1 - media_bias) * 100)),
            "campaignFinance": max(5, int(finance_score * 100)),
            "digitalEcosystem": eco_scores.get(eco_level, 40),
            "disputeResolution": max(5, int(vdem_val * 90)),
            "inclusion": max(5, int(fh * 0.8)),
        }

        # Determinar trend
        risk = result["risk_score"]
        trend = "deteriorating" if risk >= 70 else "stable" if risk >= 30 else "stable"

        # Construir alerts desde violations + risk_factors
        alerts = []
        for v in legal.get("violations", [])[:4]:
            alert_type = "critical" if v["severity"] == "critical" else "high" if v["severity"] == "high" else "moderate"
            alerts.append({"type": alert_type, "text": v["finding"][:120]})
        for rf in legal.get("risk_factors", [])[:2]:
            alerts.append({"type": rf.get("severity", "moderate"), "text": rf["finding"][:120]})

        if not alerts:
            alerts.append({"type": "low", "text": "Sistema electoral estable con garantías institucionales sólidas"})

        # Timeline simulada (en producción: datos históricos de PostgreSQL)
        import random
        months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
        base = max(10, risk - random.randint(10, 25))
        timeline = []
        for i, m in enumerate(months):
            step = base + int((risk - base) * (i / (len(months) - 1)))
            timeline.append({"month": m, "score": step})

        dashboard_countries.append({
            "id": code.lower(),
            "run_id": result["run_id"],
            "name": info["name"],
            "flag": info["flag"],
            "date": info["election_date"],
            "riskScore": result["risk_score"],
            "riskLevel": result["risk_level"],
            "trend": trend,
            "freedomScore": context.get("freedom_house", {}).get("score", 0),
            "vdemIndex": context.get("vdem", {}).get("liberal_democracy", 0),
            "dimensions": dimensions,
            "violations": violations_simple,
            "timeline": timeline,
            "alerts": alerts,
            "mediaData": media_data,
            "agentLogs": result.get("agent_logs", []),
        })

    return {"countries": dashboard_countries, "generated_at": datetime.now(timezone.utc).isoformat()}


# ═══════════════════════════════════════════════════════════════════════════════
# 7. CLI — Ejecución directa para testing
# ═══════════════════════════════════════════════════════════════════════════════

def run_cli_analysis(country_code: str = "VEN"):
    """Ejecuta un análisis desde la línea de comandos."""
    code = country_code.upper()
    if code not in COUNTRY_CATALOG:
        print(f"Error: País '{code}' no disponible. Opciones: {list(COUNTRY_CATALOG.keys())}")
        return

    info = COUNTRY_CATALOG[code]
    print(f"\n{'='*70}")
    print(f"  DEMOCRAC.IA (PEIRS) — Análisis Electoral")
    print(f"  País: {info['flag']} {info['name']} | Elección: {info['election_date']}")
    print(f"{'='*70}\n")

    state = create_initial_state(
        country=info["name"],
        country_code=code,
        election_date=info["election_date"],
    )

    result = peirs_pipeline.invoke(state)

    # Imprimir logs de agentes
    print("📋 LOG DE AGENTES:")
    print("-" * 50)
    for log in result["agent_logs"]:
        print(f"  {log}")
    print()

    # Imprimir resumen
    print(f"🎯 RISK SCORE: {result['risk_score']}/100 ({result['risk_level'].upper()})")
    print(f"⚖️  VIOLACIONES: {result['legal_analysis']['violation_count']}")
    print(f"📄 REPORTE: {len(result['final_report_markdown'])} caracteres")
    print()

    # Guardar reporte
    filename = f"peirs_report_{code.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result["final_report_markdown"])
    print(f"💾 Reporte guardado: {filename}")

    return result


if __name__ == "__main__":
    import sys
    country = sys.argv[1] if len(sys.argv) > 1 else "VEN"
    run_cli_analysis(country)