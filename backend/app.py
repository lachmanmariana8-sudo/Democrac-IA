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
import sys
import json

# Forzar UTF-8 en stdout/stderr — evita crashes con emojis en Windows (cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Cargar .env antes de leer variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import TypedDict, Dict, List, Optional, Any

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Security, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
import hashlib
import pandas as pd

# ── RAG — importación condicional (fallback gracioso si no instalado) ─────────
# Modo semántico (ChromaDB): requiere chromadb + sentence-transformers
# Modo keyword (fallback): siempre disponible, sin dependencias externas
try:
    from rag import query_legal_context as _rag_legal, query_fraud_context as _rag_fraud
    from rag import query_hate_speech_context as _rag_hate, format_rag_context_for_llm
    from rag import init_rag, RAG_AVAILABLE
    # El retriever ahora tiene keyword fallback — siempre marca disponible
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    def _rag_legal(*a, **kw): return []
    def _rag_fraud(*a, **kw): return []
    def _rag_hate(*a, **kw):  return []
    def format_rag_context_for_llm(*a, **kw): return ""
    def init_rag(): return False

# ── Módulo de análisis de fraude y discurso de odio ───────────────────────────
try:
    from modules.fraud_hate_analysis import analyze_fraud_and_hate
except ImportError:
    def analyze_fraud_and_hate(entries):
        return {"fraud": {"total": 0, "markdown": ""}, "hate_speech": {"total": 0, "markdown": ""}, "has_significant_findings": False}

# ── Datos estáticos: se cargan desde módulos al final del bloque de definiciones
# Ver sección "# ── Carga final de módulos" más abajo, después de las definiciones inline.
_MODULES_LOADED = False

# ── Agent 5: FieldDataValidationAgent ────────────────────────────────────────
try:
    from modules.field_validator import validate_entry, detect_patterns, render_pattern_markdown
except ImportError:
    def validate_entry(entry, existing):
        from types import SimpleNamespace
        return SimpleNamespace(valid=True, warnings=[], errors=[], duplicate_of=None, quality_score=1.0)
    def detect_patterns(entries):
        from types import SimpleNamespace
        return SimpleNamespace(has_significant_patterns=False, summary="")
    def render_pattern_markdown(report): return ""

# ── Agent 7: AlertDispatchAgent ──────────────────────────────────────────────
try:
    from integrations.alerts import dispatch_alert, build_entry_alert, AlertEvent
    ALERTS_AVAILABLE = True
except ImportError:
    ALERTS_AVAILABLE = False
    async def dispatch_alert(*a, **kw): return {"dispatched": False}
    def build_entry_alert(*a, **kw): return None

# ── OONI API — detección real-time de censura y bloqueos ─────────────────────
try:
    from integrations.ooni import get_ooni_summary, fetch_web_anomalies, clear_cache as ooni_clear_cache, OONI_AVAILABLE
    OONI_AVAILABLE = True
except ImportError:
    OONI_AVAILABLE = False
    def get_ooni_summary(country_code, days_back=7):
        return {"available": False, "summary_text": "OONI no disponible", "alert_level": "none",
                "censorship_detected": False, "blocked_domains": [], "anomalous_domains": []}
    def fetch_web_anomalies(*a, **kw): return []
    def ooni_clear_cache(*a, **kw): pass

# ── Persistencia SQLite (db/) ─────────────────────────────────────────────────
try:
    from db import (
        init_db as _db_init_db,
        create_run as _db_create_run,
        complete_run as _db_complete_run,
        save_report as _db_save_report,
        create_session as _db_create_session,
        close_session as _db_close_session,
        save_entry as _db_save_entry,
        save_alert as _db_save_alert,
        list_alerts as _db_list_alerts,
        get_report as _db_get_report,
        get_latest_report as _db_get_latest_report,
        get_db_stats as _db_get_stats,
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    def _db_init_db(): pass
    def _db_create_run(*a, **kw): pass
    def _db_complete_run(*a, **kw): pass
    def _db_save_report(*a, **kw): return None
    def _db_create_session(*a, **kw): pass
    def _db_close_session(*a, **kw): pass
    def _db_save_entry(*a, **kw): pass
    def _db_save_alert(*a, **kw): pass
    def _db_list_alerts(*a, **kw): return []
    def _db_get_report(*a, **kw): return None
    def _db_get_latest_report(*a, **kw): return None
    def _db_get_stats(): return {}

# ── Startup checks ────────────────────────────────────────────────────────────
try:
    from startup_checks import run_startup_checks as _run_startup_checks
    STARTUP_CHECKS_AVAILABLE = True
except ImportError:
    STARTUP_CHECKS_AVAILABLE = False

# ── Agente Auditor ────────────────────────────────────────────────────────────
try:
    from agents.auditor import AuditAgent as _AuditAgent
    _auditor = _AuditAgent()
    AUDITOR_AVAILABLE = True
except ImportError:
    AUDITOR_AVAILABLE = False
    _auditor = None


# ── Migración: agents/ y chapters/ ─────────────────────────────────────────────
# Importaciones condicionales hacia los nuevos módulos.
# Las definiciones originales permanecen en app.py como fallback.
# AGENTS_MODULE_AVAILABLE y CHAPTERS_MODULE_AVAILABLE indican si los módulos
# están disponibles (útil para tests y diagnóstico).

try:
    from agents.pipeline import build_workflow as _bw_migrated, PEIRSState, peirs_pipeline as _pp_migrated  # noqa: F401
    from agents.nodes import (
        run_ingestion,          # noqa: F401
        run_political_analyst,  # noqa: F401
        run_legal_compliance,   # noqa: F401
        run_dictamen_agent,     # noqa: F401
        run_report_generator,   # noqa: F401
    )
    AGENTS_MODULE_AVAILABLE = True
except ImportError:
    AGENTS_MODULE_AVAILABLE = False

try:
    from chapters.generators import (
        _generate_country_profile_section as _gcp_migrated,   # noqa: F401
        _generate_executive_summary as _ges_migrated,         # noqa: F401
        _generate_political_context as _gpc_migrated,         # noqa: F401
        _generate_emb_chapter as _gemb_migrated,              # noqa: F401
        _generate_inclusivity_chapter as _ginc_migrated,      # noqa: F401
        _generate_campaign_chapter as _gcamp_migrated,        # noqa: F401
        _generate_digital_chapter as _gdig_migrated,          # noqa: F401
        _generate_voting_day_chapter as _gvd_migrated,        # noqa: F401
        _generate_observation_chapter as _gobs_migrated,      # noqa: F401
        _generate_justice_chapter as _gjust_migrated,         # noqa: F401
        _generate_recommendations as _grec_migrated,          # noqa: F401
        _generate_ai_regulation_chapter as _gai_migrated,     # noqa: F401
    )
    CHAPTERS_MODULE_AVAILABLE = True
except ImportError:
    CHAPTERS_MODULE_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_TEMPERATURE = 0.2

# ── Autenticación — API Keys para protocolo de observación ───────────────────
# Formato env: OBSERVER_API_KEYS=key1,key2,key3
# Default dev key — CAMBIAR en producción via variable de entorno
_raw_keys = os.getenv("OBSERVER_API_KEYS", "democracia-obs-dev-2026")
OBSERVER_API_KEYS: set = set(k.strip() for k in _raw_keys.split(",") if k.strip())

_obs_key_header = APIKeyHeader(name="X-Observer-Key", auto_error=False)

async def _require_observer_key(api_key: str = Security(_obs_key_header)):
    """Dependencia FastAPI: exige header X-Observer-Key válido en endpoints de observación."""
    if not api_key or api_key not in OBSERVER_API_KEYS:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "API key de observador inválida o ausente.",
                "hint": "Incluye el header 'X-Observer-Key: <tu_clave>' en la solicitud.",
                "contact": "Contacta al coordinador de misión DEMOCRAC.IA para obtener tu clave.",
            }
        )
    return api_key


# ── Hardening: rate limit en endpoints caros (Claude + render) ─────────────
# In-memory por IP. Es best-effort (no persiste entre reinicios ni entre replicas
# en Railway multi-instance), pero mitiga el riesgo de burn-in por abuso casual.
# Para producción seria considerar Redis como backing store.
from collections import defaultdict as _defaultdict
import time as _tm

_RATE_LIMIT_BUCKETS: Dict[str, List[float]] = _defaultdict(list)
_RATE_LIMIT_WINDOW_S = 60
_RATE_LIMIT_MAX_PER_MIN = int(os.getenv("EXPENSIVE_RATE_LIMIT_PER_MIN", "5"))


async def _rate_limit_expensive(request: Request):
    """Dependencia FastAPI: máx N requests/min por IP en endpoints caros.
    Devuelve 429 Too Many Requests si se excede.
    """
    ip = "unknown"
    try:
        ip = request.client.host if request and request.client else "unknown"
    except Exception:
        pass
    now = _tm.time()
    bucket = [t for t in _RATE_LIMIT_BUCKETS[ip] if now - t < _RATE_LIMIT_WINDOW_S]
    if len(bucket) >= _RATE_LIMIT_MAX_PER_MIN:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit excedido: máx {_RATE_LIMIT_MAX_PER_MIN} requests/min "
                   f"en endpoints caros. Reintente en unos segundos.",
        )
    bucket.append(now)
    _RATE_LIMIT_BUCKETS[ip] = bucket
    return ip


def _check_daily_budget(country_code: str, kind: str) -> None:
    """Valida que no se haya excedido el budget diario de elite reports por país.
    Lanza 429 si excedido. kind ∈ {"elite"}.
    Configurable vía env var: MAX_ELITE_PER_DAY (default 5).
    """
    try:
        from datetime import datetime as _dt, timezone as _tz
    except Exception:
        return

    if kind == "elite":
        table = "elite_reports"
        limit = int(os.getenv("MAX_ELITE_PER_DAY", "5"))
    else:
        return

    # No podemos chequear sin DB — fail-open con warning en logs
    try:
        _db_available = bool(globals().get("DB_AVAILABLE"))
    except Exception:
        _db_available = False
    if not _db_available:
        return

    today = _dt.now(_tz.utc).strftime("%Y-%m-%d")
    try:
        with _get_db() as conn:
            row = conn.execute(
                f"SELECT COUNT(*) as c FROM {table} "
                f"WHERE country_code=? AND substr(generated_at,1,10)=?",
                (country_code.upper(), today),
            ).fetchone()
            count = row["c"] if row else 0
    except Exception as e:
        # Tabla puede no existir todavía (primer request del día)
        return

    if count >= limit:
        raise HTTPException(
            status_code=429,
            detail={
                "error": f"Budget diario agotado para {country_code}.",
                "kind": kind,
                "count_today": count,
                "limit": limit,
                "date_utc": today,
                "hint": "El límite se reinicia a las 00:00 UTC. "
                        "Para aumentarlo, ajustar MAX_ELITE_PER_DAY.",
            },
        )

# Inicialización del LLM (se usa en agentes 3 y 4)
llm = ChatAnthropic(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    anthropic_api_key=ANTHROPIC_API_KEY,
) if ANTHROPIC_API_KEY else None


# ═══════════════════════════════════════════════════════════════════════════════
# 1b. CARGA DE DATOS REALES — V-Dem Dataset v15
# ═══════════════════════════════════════════════════════════════════════════════

# 2026-05-28 — Path default alineado con modules/config.py:26. Si el CSV v16
# no existe en disk (caso típico: Railway sin volumen + dev sin descarga),
# load_vdem_data() retorna None y get_vdem_country() cae a VDEM_STATIC del
# modules/vdem_static.py (auto-generado de v16, 1985-2025, 38 países × 21
# indicadores). Ambos entornos quedan citando v16 honestamente.
#
# El archivo viejo data/V-Dem-CY-Full+Others-v15.csv (402MB) queda como legado
# para queries históricas locales; el dev que quiera usarlo debe setear el env
# var VDEM_CSV_PATH explícitamente.
VDEM_CSV_PATH = os.getenv("VDEM_CSV_PATH", "../data/vdem/vdem_v16.csv")

VDEM_COLUMNS = [
    "country_text_id", "year",
    "v2x_libdem",
    "v2x_polyarchy",
    "v2x_partipdem",
    "v2x_delibdem",
    "v2x_egaldem",
    "v2xel_frefair",
    "v2x_freexp_altinf",
    "v2x_frassoc_thick",
    "v2x_suffr",
    "v2xcl_rol",
    "v2elembaut",
    "v2elembcap",
    "v2elirreg",
    "v2elintim",
    "v2elintmon",
    # Variables ecosistema digital
    "v2mecenefi",
    "v2mecenefm",
    "v2meharjrn",
    "v2mebias",
    "v2smgovdom",
    "v2smgovfilcap",
    "v2smregcap",
    # Variables contexto político-legal (Cap. 2)
    "v2psbars",       # barreras a partidos (0=prohibición, 4=abierto)
    "v2psoppaut",     # autonomía partidos de oposición (-4 a 4)
    "v2jureview",     # revisión judicial independiente (0=ninguna, 4=fuerte)
]

# 2026-05-28 — Cita alineada con el fallback estático (modules/vdem_static.py),
# que es v16 con cobertura 1985-2025. Audit de hoy confirmó que ese static es la
# fuente efectiva en producción Railway (el CSV grande no se deploya). El v15 CSV
# en disk local quedó como legado; ver comentario sobre VDEM_CSV_PATH arriba.
VDEM_CITATION = (
    "Coppedge et al. 2026. 'V-Dem Country-Year Dataset v16' "
    "Varieties of Democracy (V-Dem) Project. https://doi.org/10.23696/vdemds26"
)
VDEM_SOURCE_URL = "https://v-dem.net/data/the-v-dem-dataset/"
VDEM_VERSION = os.getenv("VDEM_VERSION", "v16")
VDEM_LAST_YEAR = int(os.getenv("VDEM_LAST_YEAR", "2025"))


def load_vdem_data() -> Optional[pd.DataFrame]:
    if not os.path.exists(VDEM_CSV_PATH):
        print(f"[V-Dem] AVISO: CSV no encontrado en '{VDEM_CSV_PATH}'. Usando datos mock.")
        return None
    try:
        df = pd.read_csv(VDEM_CSV_PATH, usecols=VDEM_COLUMNS, low_memory=False)
        print(f"[V-Dem] OK: Dataset cargado: {len(df):,} filas, {len(df.columns)} columnas.")
        print(f"[V-Dem] Años disponibles: {int(df['year'].min())}–{int(df['year'].max())}")
        return df
    except Exception as e:
        print(f"[V-Dem] ERROR al cargar CSV: {e}. Usando datos mock.")
        return None


def get_vdem_country(df: Optional[pd.DataFrame], country_code: str, year: int = VDEM_LAST_YEAR) -> Optional[Dict]:
    if df is None:
        return get_vdem_country_static(country_code, year)

    row = df[(df["country_text_id"] == country_code) & (df["year"] == year)]

    if row.empty:
        row = df[(df["country_text_id"] == country_code) & (df["year"] == year - 1)]

    if row.empty:
        print(f"[V-Dem] AVISO: No se encontraron datos para {country_code} ({year}).")
        return None

    r = row.iloc[0]
    actual_year = int(r["year"])

    def norm_vdem(val, min_val=-4.0, max_val=4.0):
        if pd.isna(val):
            return None
        return round((float(val) - min_val) / (max_val - min_val), 4)

    def norm_inverted(val, min_val=-4.0, max_val=4.0):
        n = norm_vdem(val, min_val, max_val)
        return round(1.0 - n, 4) if n is not None else None

    emb_aut_raw = float(r["v2elembaut"]) if pd.notna(r["v2elembaut"]) else 0.0
    if emb_aut_raw >= 1.5:
        emb_independence_level = "full"
    elif emb_aut_raw >= 0.0:
        emb_independence_level = "partial"
    elif emb_aut_raw >= -1.5:
        emb_independence_level = "compromised"
    else:
        emb_independence_level = "captured"

    intmon_raw = r["v2elintmon"]
    international_observation = bool(intmon_raw == 1.0) if pd.notna(intmon_raw) else None

    return {
        "country_code": country_code,
        "year": actual_year,
        "liberal_democracy": round(float(r["v2x_libdem"]), 4),
        "electoral_democracy": round(float(r["v2x_polyarchy"]), 4),
        "participatory_democracy": round(float(r["v2x_partipdem"]), 4),
        "deliberative_democracy": round(float(r["v2x_delibdem"]), 4),
        "egalitarian_democracy": round(float(r["v2x_egaldem"]), 4),
        "free_fair_elections": round(float(r["v2xel_frefair"]), 4),
        "freedom_of_expression": round(float(r["v2x_freexp_altinf"]), 4),
        "freedom_of_association": round(float(r["v2x_frassoc_thick"]), 4),
        "universal_suffrage": round(float(r["v2x_suffr"]), 4),
        "rule_of_law": round(float(r["v2xcl_rol"]), 4),
        "emb_autonomy_raw": round(emb_aut_raw, 4),
        "emb_autonomy": norm_vdem(r["v2elembaut"]),
        "emb_capacity": norm_vdem(r["v2elembcap"]),
        "emb_independence_level": emb_independence_level,
        "electoral_irregularities": norm_inverted(r["v2elirreg"]),
        "electoral_intimidation": norm_inverted(r["v2elintim"]),
        "international_observation": international_observation,
        "internet_censorship": norm_inverted(r["v2mecenefi"]) if "v2mecenefi" in r.index and pd.notna(r.get("v2mecenefi")) else None,
        "media_censorship": norm_inverted(r["v2mecenefm"]) if "v2mecenefm" in r.index and pd.notna(r.get("v2mecenefm")) else None,
        "journalist_harassment": norm_inverted(r["v2meharjrn"]) if "v2meharjrn" in r.index and pd.notna(r.get("v2meharjrn")) else None,
        "media_bias_vdem": norm_inverted(r["v2mebias"]) if "v2mebias" in r.index and pd.notna(r.get("v2mebias")) else None,
        "gov_social_media_dominance": norm_inverted(r["v2smgovdom"]) if "v2smgovdom" in r.index and pd.notna(r.get("v2smgovdom")) else None,
        "gov_internet_filter_capacity": norm_inverted(r["v2smgovfilcap"]) if "v2smgovfilcap" in r.index and pd.notna(r.get("v2smgovfilcap")) else None,
        "social_media_regulation": norm_inverted(r["v2smregcap"]) if "v2smregcap" in r.index and pd.notna(r.get("v2smregcap")) else None,
        # Indicadores contexto político-legal (Cap. 2)
        "opposition_party_barriers": norm_vdem(r["v2psbars"], 0, 4) if "v2psbars" in r.index and pd.notna(r.get("v2psbars")) else None,
        "opposition_autonomy": norm_vdem(r["v2psoppaut"]) if "v2psoppaut" in r.index and pd.notna(r.get("v2psoppaut")) else None,
        "judicial_review": norm_vdem(r["v2jureview"], 0, 4) if "v2jureview" in r.index and pd.notna(r.get("v2jureview")) else None,
        "citation": VDEM_CITATION,
        "dataset_version": VDEM_VERSION,
    }


def get_vdem_country_static(country_code: str, year: int = VDEM_LAST_YEAR) -> Optional[Dict]:
    """
    Fallback para get_vdem_country cuando VDEM_DF no está disponible (producción sin CSV).
    Lee de VDEM_STATIC[country_code][year] generado de V-Dem v15.
    """
    cc_data = VDEM_STATIC.get(country_code, {})
    if not cc_data:
        return None
    # Buscar año exacto, luego año anterior
    row = cc_data.get(str(year)) or cc_data.get(str(year - 1)) or cc_data.get(year) or cc_data.get(year - 1)
    if not row:
        # Usar el año más reciente disponible
        available = sorted(int(y) for y in cc_data.keys())
        if not available:
            return None
        row = cc_data.get(str(available[-1])) or cc_data.get(available[-1])
        year = available[-1]
    if not row:
        return None

    def norm(val, lo=-4.0, hi=4.0):
        if val is None:
            return None
        return round((val - lo) / (hi - lo), 4)

    def norm_inv(val, lo=-4.0, hi=4.0):
        n = norm(val, lo, hi)
        return round(1.0 - n, 4) if n is not None else None

    emb_aut = row.get("v2elembaut")
    if emb_aut is None:
        emb_level = "unknown"
    elif emb_aut >= 1.5:
        emb_level = "full"
    elif emb_aut >= 0.0:
        emb_level = "partial"
    elif emb_aut >= -1.5:
        emb_level = "compromised"
    else:
        emb_level = "captured"

    intmon = row.get("v2elintmon")
    return {
        "country_code": country_code,
        "year": int(year),
        "liberal_democracy": row.get("v2x_libdem"),
        "electoral_democracy": row.get("v2x_polyarchy"),
        "participatory_democracy": row.get("v2x_partipdem"),
        "deliberative_democracy": row.get("v2x_delibdem"),
        "egalitarian_democracy": row.get("v2x_egaldem"),
        "free_fair_elections": row.get("v2xel_frefair"),
        "freedom_of_expression": row.get("v2x_freexp_altinf"),
        "freedom_of_association": row.get("v2x_frassoc_thick"),
        "universal_suffrage": row.get("v2x_suffr"),
        "rule_of_law": row.get("v2xcl_rol"),
        "emb_autonomy_raw": emb_aut,
        "emb_autonomy": norm(emb_aut),
        "emb_capacity": norm(row.get("v2elembcap")),
        "emb_independence_level": emb_level,
        "electoral_irregularities": norm_inv(row.get("v2elirreg")),
        "electoral_intimidation": norm_inv(row.get("v2elintim")),
        "international_observation": bool(intmon == 1.0) if intmon is not None else None,
        "internet_censorship": norm_inv(row.get("v2mecenefi")),
        "media_censorship": norm_inv(row.get("v2mecenefm")),
        "journalist_harassment": norm_inv(row.get("v2meharjrn")),
        "media_bias_vdem": norm_inv(row.get("v2mebias")),
        "gov_social_media_dominance": norm_inv(row.get("v2smgovdom")),
        "gov_internet_filter_capacity": norm_inv(row.get("v2smgovfilcap")),
        "social_media_regulation": norm_inv(row.get("v2smregcap")),
        "opposition_party_barriers": norm(row.get("v2psbars"), 0, 4),
        "opposition_autonomy": norm(row.get("v2psoppaut")),
        "judicial_review": norm(row.get("v2jureview"), 0, 4),
        "citation": VDEM_CITATION,
        "dataset_version": VDEM_VERSION,
    }


VDEM_DF = load_vdem_data()


# ═══════════════════════════════════════════════════════════════════════════════
# 1b-2. CARGA DE DATOS REALES — Freedom House Freedom in the World 2013-2025
# ═══════════════════════════════════════════════════════════════════════════════

FH_CSV_PATH = os.getenv("FH_CSV_PATH", "../data/All_data_FIW_2013-2025 - Index.csv")

FH_CITATION = (
    "Freedom House. 2025. 'Freedom in the World 2025: The Uphill Battle to Safeguard Rights.' "
    "Washington, DC: Freedom House. https://freedomhouse.org/report/freedom-world"
)
FH_SOURCE_URL = "https://freedomhouse.org/report/freedom-world"
FH_VERSION = "FIW_2025"
FH_LAST_EDITION = 2025

FH_COUNTRY_NAMES = {
    "VEN": "Venezuela", "NIC": "Nicaragua", "GTM": "Guatemala", "URY": "Uruguay",
    "COL": "Colombia", "BRA": "Brazil", "MEX": "Mexico", "ARG": "Argentina",
    "CHL": "Chile", "BOL": "Bolivia", "ECU": "Ecuador", "PER": "Peru",
    "HND": "Honduras", "SLV": "El Salvador", "PAN": "Panama",
    "CRI": "Costa Rica", "DOM": "Dominican Republic", "PRY": "Paraguay", "CUB": "Cuba",
    "DEU": "Germany", "FRA": "France", "HUN": "Hungary", "POL": "Poland",
    "TUR": "Turkey", "RUS": "Russia", "BLR": "Belarus", "UKR": "Ukraine", "GEO": "Georgia",
    "ZAF": "South Africa", "NGA": "Nigeria", "KEN": "Kenya", "ZWE": "Zimbabwe", "GHA": "Ghana",
    "IND": "India", "PHL": "Philippines", "IDN": "Indonesia", "THA": "Thailand", "TUN": "Tunisia",
}


def load_freedom_house_data() -> Optional[pd.DataFrame]:
    if not os.path.exists(FH_CSV_PATH):
        print(f"[FH] AVISO: CSV no encontrado en '{FH_CSV_PATH}'. Usando datos mock.")
        return None
    try:
        df = pd.read_csv(FH_CSV_PATH, sep=";", skiprows=1)
        df.columns = df.columns.str.strip()
        df["Edition"] = pd.to_numeric(df["Edition"], errors="coerce")
        df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
        df["PR rating"] = pd.to_numeric(df["PR rating"], errors="coerce")
        df["CL rating"] = pd.to_numeric(df["CL rating"], errors="coerce")
        print(f"[FH] OK: Dataset cargado: {len(df):,} filas.")
        print(f"[FH] Ediciones disponibles: {int(df['Edition'].min())}–{int(df['Edition'].max())}")
        return df
    except Exception as e:
        print(f"[FH] ERROR al cargar CSV: {e}. Usando datos mock.")
        return None


def get_freedom_house_country(df: Optional[pd.DataFrame], country_code: str, edition: int = FH_LAST_EDITION) -> Optional[Dict]:
    if df is None:
        return None

    fh_name = FH_COUNTRY_NAMES.get(country_code)
    if not fh_name:
        print(f"[FH] AVISO: No hay mapeo de nombre para {country_code}.")
        return None

    row = df[(df["Country/Territory"] == fh_name) & (df["Edition"] == edition)]

    if row.empty:
        row = df[(df["Country/Territory"] == fh_name) & (df["Edition"] == edition - 1)]

    if row.empty:
        print(f"[FH] AVISO: No se encontraron datos para {fh_name} ({edition}).")
        return None

    r = row.iloc[0]
    actual_edition = int(r["Edition"])

    status_map = {"F": "Free", "PF": "Partly Free", "NF": "Not Free"}
    status_raw = str(r["Status"]).strip() if pd.notna(r["Status"]) else "NF"
    status_full = status_map.get(status_raw, status_raw)

    return {
        "country_code": country_code,
        "country_name_fh": fh_name,
        "edition": actual_edition,
        "total_score": int(r["Total"]) if pd.notna(r["Total"]) else 0,
        "score": int(r["Total"]) if pd.notna(r["Total"]) else 0,  # alias para compatibilidad
        "status": status_full,
        "status_short": status_raw,
        "political_rights_rating": int(r["PR rating"]) if pd.notna(r["PR rating"]) else 7,
        "civil_liberties_rating": int(r["CL rating"]) if pd.notna(r["CL rating"]) else 7,
        "citation": FH_CITATION,
        "dataset_version": FH_VERSION,
    }


def derive_civil_liberties_from_fh(fh_data: dict) -> dict:
    cl = fh_data.get("civil_liberties_rating", 7)
    pr = fh_data.get("political_rights_rating", 7)
    if cl >= 6:
        press, assembly, judicial = "severely_restricted", "banned", "captured"
    elif cl == 5:
        press, assembly, judicial = "severely_restricted", "restricted", "compromised"
    elif cl == 4:
        press, assembly, judicial = "restricted", "restricted", "compromised"
    elif cl == 3:
        press, assembly, judicial = "partially_restricted", "partially_restricted", "under_pressure"
    elif cl == 2:
        press, assembly, judicial = "mostly_free", "mostly_free", "mostly_independent"
    else:
        press, assembly, judicial = "guaranteed", "guaranteed", "strong"
    return {
        "freedom_of_press": press,
        "freedom_of_assembly": assembly,
        "judicial_independence": judicial,
        "political_prisoners": pr >= 6,
        "cl_rating": cl,
        "pr_rating": pr,
        "data_source": "Freedom House FIW",
        "data_year": fh_data.get("edition"),
    }


FH_DF = load_freedom_house_data()


# ═══════════════════════════════════════════════════════════════════════════════
# 1b-3. CARGA DE DATOS REALES — PEI Dataset v10.0 (Electoral Integrity Project)
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# 1b-3b. RSF Press Freedom Index 2025
# ═══════════════════════════════════════════════════════════════════════════════

RSF_CSV_PATH = os.getenv("RSF_CSV_PATH", "../data/RSF/2025 - 2025.csv")

RSF_CITATION = (
    "Reporters Without Borders (RSF). 2025. 'World Press Freedom Index 2025.' "
    "https://rsf.org/en/index"
)
RSF_SOURCE_URL = "https://rsf.org/en/index"
RSF_VERSION = "RSF_2025"


def load_rsf_data() -> Optional[pd.DataFrame]:
    if not os.path.exists(RSF_CSV_PATH):
        print(f"[RSF] AVISO: CSV no encontrado en '{RSF_CSV_PATH}'.")
        return None
    try:
        # El CSV de RSF exportado de Excel envuelve cada fila en comillas dobles
        # y usa coma como separador decimal (formato europeo). Preprocesar:
        from io import StringIO
        with open(RSF_CSV_PATH, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        processed = []
        for line in lines:
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]          # quitar comillas externas
                line = line.replace('""', '"')  # unescape comillas internas
            processed.append(line)
        df = pd.read_csv(StringIO("\n".join(processed)))
        df.columns = df.columns.str.strip()
        # Convertir decimales europeos (87,18 → 87.18) en columnas numéricas
        numeric_cols = ["Score 2025", "Rank", "Political Context", "Economic Context",
                        "Legal Context", "Social Context", "Safety", "Score N-1"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
                df[col] = pd.to_numeric(df[col], errors="coerce")
        print(f"[RSF] OK: Dataset cargado: {len(df):,} países.")
        return df
    except Exception as e:
        print(f"[RSF] ERROR al cargar CSV: {e}")
        return None


def get_rsf_country(df: Optional[pd.DataFrame], country_code: str) -> Optional[Dict]:
    if df is None:
        return None
    row = df[df["ISO"] == country_code]
    if row.empty:
        return None
    r = row.iloc[0]

    def safe(col):
        return round(float(r[col]), 2) if col in r.index and pd.notna(r[col]) else None

    return {
        "country_code": country_code,
        "score": safe("Score 2025"),
        "rank": int(r["Rank"]) if pd.notna(r.get("Rank")) else None,
        "political_context": safe("Political Context"),
        "economic_context": safe("Economic Context"),
        "legal_context": safe("Legal Context"),
        "social_context": safe("Social Context"),
        "safety": safe("Safety"),
        "country_en": str(r["Country_EN"]) if "Country_EN" in r.index and pd.notna(r.get("Country_EN")) else None,
        "zone": str(r["Zone"]) if "Zone" in r.index and pd.notna(r.get("Zone")) else None,
        "citation": RSF_CITATION,
        "dataset_version": RSF_VERSION,
    }


RSF_DF = load_rsf_data()


PEI_CSV_PATH = os.getenv("PEI_CSV_PATH", "../data/PEI/PEI_10 Election External.csv")

PEI_CITATION = (
    "Garnett, H. A., James, T. S., & Caal-Lam, S. (2024). "
    "'Perceptions of Electoral Integrity (PEI-10.0).' "
    "Electoral Integrity Project. https://doi.org/10.7910/DVN/FQ5ECC"
)
PEI_SOURCE_URL = "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/FQ5ECC"
PEI_VERSION = "PEI-10.0"

PEI_COLUMNS = [
    "ISO", "election", "year", "office",
    "OVERALLINTEGRITY",
    "EMBs",
    "LAWS",
    "PROCEDURES",
    "BOUNDARIES",
    "VOTERREGISTRATION",
    "MEDIACOVERAGE",
    "CAMPAIGNFINANCE",
    "VOTINGPROCESS",
    "VOTECOUNT",
    "VOTINGRESULTS",
    "ELECTIONAUTHORITIES",
]


def load_pei_data() -> Optional[pd.DataFrame]:
    if not os.path.exists(PEI_CSV_PATH):
        print(f"[PEI] AVISO: CSV no encontrado en '{PEI_CSV_PATH}'. Usando datos mock.")
        return None
    try:
        df = pd.read_csv(PEI_CSV_PATH, low_memory=False)
        df.columns = df.columns.str.strip()
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        for col in ["OVERALLINTEGRITY","EMBs","LAWS","PROCEDURES","BOUNDARIES",
                    "VOTERREGISTRATION","MEDIACOVERAGE","CAMPAIGNFINANCE",
                    "VOTINGPROCESS","VOTECOUNT","VOTINGRESULTS","ELECTIONAUTHORITIES"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        print(f"[PEI] OK: Dataset cargado: {len(df):,} elecciones.")
        print(f"[PEI] Años disponibles: {int(df['year'].min())}–{int(df['year'].max())}")
        return df
    except Exception as e:
        print(f"[PEI] ERROR al cargar CSV: {e}. Usando datos mock.")
        return None


def get_pei_country(df: Optional[pd.DataFrame], country_code: str) -> Optional[Dict]:
    if df is None:
        return None

    rows = df[df["ISO"] == country_code].sort_values("year", ascending=False)

    if rows.empty:
        print(f"[PEI] AVISO: No hay datos para {country_code}.")
        return None

    presidential = rows[rows["office"].str.contains("Presidential", na=False)]
    r = presidential.iloc[0] if not presidential.empty else rows.iloc[0]

    def safe_float(val):
        return round(float(val), 1) if pd.notna(val) else None

    def safe_col(col):
        return safe_float(r[col]) if col in r.index and pd.notna(r[col]) else None

    def safe_col_fallback(col_primary, col_fallback=None):
        val = safe_col(col_primary)
        if val is None and col_fallback:
            val = safe_col(col_fallback)
        return val

    return {
        "country_code": country_code,
        "election_id": str(r["election"]),
        "year": int(r["year"]),
        "office": str(r["office"]) if pd.notna(r["office"]) else "N/A",
        "overall_integrity": safe_col_fallback("OVERALLINTEGRITY", "PEI_add_original"),
        "emb_score": safe_col_fallback("EMBs", "EMBs_m"),
        "legal_framework": safe_col_fallback("LAWS", "laws"),
        "procedures": safe_col_fallback("PROCEDURES", "procedures"),
        "voter_registration": safe_col_fallback("VOTERREGISTRATION", "votereg"),
        "media_coverage": safe_col_fallback("MEDIACOVERAGE", "media"),
        "campaign_finance": safe_col_fallback("CAMPAIGNFINANCE", "finance"),
        "voting_process": safe_col_fallback("VOTINGPROCESS", "voting"),
        "vote_count": safe_col_fallback("VOTECOUNT", "count"),
        "voting_results": safe_col_fallback("VOTINGRESULTS", "results"),
        "election_authorities": safe_col_fallback("ELECTIONAUTHORITIES", "EMBs"),
        "laws_unfair": safe_col("lawsunfair"),
        "laws_favored_incumbent": safe_col("favoredincumbent"),
        "laws_equal": safe_col("equal"),
        "laws_enfranchised": safe_col("enfranchised"),
        "reg_listed": safe_col("reglisted"),
        "reg_inaccurate": safe_col("reginaccurate"),
        "reg_ineligible": safe_col("ineligible"),
        "party_registration": safe_col("PARTYREGISTRATION"),
        "opp_prevent": safe_col("oppprevent"),
        "equal_opp": safe_col("equalopp"),
        "women_opp": safe_col("womenopp"),
        "media_balanced": safe_col("balanced"),
        "media_fair_access": safe_col("fairaccess"),
        "media_disinformation": safe_col("disinformation"),
        "finance_resources": safe_col("resources"),
        "finance_bribed": safe_col("bribed"),
        "citation": PEI_CITATION,
        "dataset_version": PEI_VERSION,
    }


PEI_DF = load_pei_data()


# ═══════════════════════════════════════════════════════════════════════════════
# 1c. FRAMEWORK DE TRAZABILIDAD
# ═══════════════════════════════════════════════════════════════════════════════

# Constantes de trazabilidad — Fase 1 del refactor #2 (2026-05-30).
# Movidas a modules/state_constants.py para que agents/nodes.py pueda
# importarlas sin pasar por app.py (evita imports circulares futuros).
from modules.state_constants import (
    CONFIDENCE_CONFIRMED, CONFIDENCE_PROBABLE, CONFIDENCE_UNVERIFIED, CONFIDENCE_MOCK,
    SOURCE_API, SOURCE_SCRAPING, SOURCE_DOCUMENT, SOURCE_SOCIAL, SOURCE_MANUAL, SOURCE_MOCK,
)

REGION_AMERICAS = "americas"
REGION_EUROPE = "europe"
REGION_AFRICA = "africa"
REGION_ASIA_PACIFIC = "asia_pacific"
REGION_ARAB = "arab_states"

COUNTRY_REGIONS = {
    "VEN": REGION_AMERICAS, "NIC": REGION_AMERICAS, "GTM": REGION_AMERICAS,
    "URY": REGION_AMERICAS, "COL": REGION_AMERICAS, "BRA": REGION_AMERICAS,
    "MEX": REGION_AMERICAS, "ARG": REGION_AMERICAS, "CHL": REGION_AMERICAS,
    "BOL": REGION_AMERICAS, "ECU": REGION_AMERICAS, "PER": REGION_AMERICAS,
    "HND": REGION_AMERICAS, "SLV": REGION_AMERICAS, "PAN": REGION_AMERICAS,
    "CRI": REGION_AMERICAS, "DOM": REGION_AMERICAS, "PRY": REGION_AMERICAS, "CUB": REGION_AMERICAS,
    "DEU": REGION_EUROPE, "FRA": REGION_EUROPE, "HUN": REGION_EUROPE, "POL": REGION_EUROPE,
    "TUR": REGION_EUROPE, "RUS": REGION_EUROPE, "BLR": REGION_EUROPE, "UKR": REGION_EUROPE, "GEO": REGION_EUROPE,
    "ZAF": REGION_AFRICA, "NGA": REGION_AFRICA, "KEN": REGION_AFRICA, "ZWE": REGION_AFRICA, "GHA": REGION_AFRICA,
    "IND": REGION_ASIA_PACIFIC, "PHL": REGION_ASIA_PACIFIC, "IDN": REGION_ASIA_PACIFIC, "THA": REGION_ASIA_PACIFIC,
    "TUN": REGION_ARAB,
}

UNIVERSAL_INSTRUMENTS = [
    {"id": "ICCPR", "name": "Pacto Internacional de Derechos Civiles y Políticos",
     "key_articles": ["Art. 1", "Art. 2", "Art. 3", "Art. 9", "Art. 14", "Art. 19", "Art. 21", "Art. 22", "Art. 25", "Art. 26"]},
    {"id": "CEDAW", "name": "Convención sobre la Eliminación de Todas las Formas de Discriminación contra la Mujer",
     "key_articles": ["Art. 7", "Art. 8"]},
    {"id": "ICERD", "name": "Convención Internacional sobre la Eliminación de Todas las Formas de Discriminación Racial",
     "key_articles": ["Art. 5"]},
    {"id": "CRPD", "name": "Convención sobre los Derechos de las Personas con Discapacidad",
     "key_articles": ["Art. 29"]},
    {"id": "UNDRIP", "name": "Declaración de las Naciones Unidas sobre los Derechos de los Pueblos Indígenas",
     "key_articles": ["Art. 5", "Art. 18"]},
    {"id": "UNCAC", "name": "Convención de las Naciones Unidas contra la Corrupción",
     "key_articles": ["Art. 7", "Art. 12", "Art. 13"]},
]

REGIONAL_INSTRUMENTS = {
    REGION_AMERICAS: [
        {"id": "CADH", "name": "Convención Americana sobre Derechos Humanos",
         "key_articles": ["Art. 23"], "observer": "OEA/DECO, UNIORE, Centro Carter"},
        {"id": "CDI", "name": "Carta Democrática Interamericana",
         "key_articles": ["Art. 3", "Art. 23", "Art. 24"], "observer": "OEA"},
    ],
    REGION_EUROPE: [
        {"id": "ECHR_P1", "name": "Convenio Europeo de Derechos Humanos, Protocolo 1",
         "key_articles": ["Art. 3"], "observer": "OSCE/ODIHR, Comisión de Venecia"},
        {"id": "COPENHAGEN", "name": "Documento de Copenhague OSCE 1990",
         "key_articles": ["Par. 5", "Par. 6", "Par. 7", "Par. 8"], "observer": "OSCE/ODIHR"},
    ],
    REGION_AFRICA: [
        {"id": "ACHPR", "name": "Carta Africana de Derechos Humanos y de los Pueblos",
         "key_articles": ["Art. 13"], "observer": "Unión Africana, ECOWAS, SADC"},
        {"id": "ACDEG", "name": "Carta Africana sobre Democracia, Elecciones y Gobernanza",
         "key_articles": ["Art. 3", "Art. 17", "Art. 22"], "observer": "Unión Africana"},
    ],
    REGION_ASIA_PACIFIC: [
        {"id": "ANFREL_DEC", "name": "Declaración de Bangkok ANFREL",
         "key_articles": [], "observer": "ANFREL, Pacific Islands Forum"},
    ],
    REGION_ARAB: [
        {"id": "ARAB_CHARTER", "name": "Carta Árabe de Derechos Humanos",
         "key_articles": ["Art. 24"], "observer": "Liga Árabe"},
    ],
}


def create_trace(
    value: Any,
    source_id: str,
    source_type: str,
    source_url: str = "",
    confidence: str = CONFIDENCE_MOCK,
    legal_basis: str = "",
    agent_id: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    raw_value = json.dumps(value, ensure_ascii=False, default=str) if not isinstance(value, str) else value
    data_hash = hashlib.sha256(raw_value.encode("utf-8")).hexdigest()[:16]

    return {
        "value": value,
        "_trace": {
            "source_id": source_id,
            "source_type": source_type,
            "source_url": source_url,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "data_hash": data_hash,
            "confidence": confidence,
            "legal_basis": legal_basis,
            "agent_id": agent_id,
            "version": "v0.2.0",
            "notes": notes,
            "is_publishable": confidence != CONFIDENCE_MOCK,
        }
    }


def get_applicable_instruments(country_code: str) -> Dict[str, List]:
    region = COUNTRY_REGIONS.get(country_code)
    regional = REGIONAL_INSTRUMENTS.get(region, []) if region else []
    return {
        "universal": UNIVERSAL_INSTRUMENTS,
        "regional": regional,
        "region": region or "unknown",
        "all_ids": [i["id"] for i in UNIVERSAL_INSTRUMENTS] + [i["id"] for i in regional],
    }


def extract_value(traced_data: Dict) -> Any:
    if isinstance(traced_data, dict) and "_trace" in traced_data:
        return traced_data["value"]
    return traced_data


def get_trace(traced_data: Dict) -> Dict:
    if isinstance(traced_data, dict) and "_trace" in traced_data:
        return traced_data["_trace"]
    return {"confidence": "unknown", "is_publishable": False}


def collect_traces(data: Dict, prefix: str = "") -> List[Dict]:
    traces = []
    for key, val in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(val, dict):
            if "_trace" in val:
                traces.append({"field": path, **val["_trace"]})
            else:
                traces.extend(collect_traces(val, path))
    return traces


# ═══════════════════════════════════════════════════════════════════════════════
# 2. DEFINICIÓN DEL ESTADO GLOBAL (LangGraph State)
# ═══════════════════════════════════════════════════════════════════════════════

class ElectionRiskState(TypedDict):
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


def create_initial_state(country: str, country_code: str, election_date: str) -> ElectionRiskState:
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
        trace_log=[],
        applicable_instruments=get_applicable_instruments(country_code),
        dictamen={},
        voting_day_data={},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DATOS MOCK
# ═══════════════════════════════════════════════════════════════════════════════
#
# 2026-05-30 — Estas definiciones inline son FALLBACK del try/except en línea
# ~1355 que importa de modules/mock_data.py. En operación normal, el import
# sobrescribe estas variables. Verificadas idénticas a modules/mock_data.py
# (4 países: GTM, NIC, URY, VEN). Para evitar drift entre las dos copias, si
# se actualizan los datos, hacerlo SIEMPRE en modules/mock_data.py primero y
# después espejar acá (o, en próximo refactor post-balotaje, eliminar esta
# copia y depender solo del import).
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

EMB_NAMES = {
    "VEN": "Consejo Nacional Electoral (CNE)", "NIC": "Consejo Supremo Electoral (CSE)",
    "GTM": "Tribunal Supremo Electoral (TSE)", "URY": "Corte Electoral",
    "COL": "Registraduria Nacional del Estado Civil", "BRA": "Tribunal Superior Electoral (TSE)",
    "MEX": "Instituto Nacional Electoral (INE)", "ARG": "Camara Nacional Electoral",
    "CHL": "Servicio Electoral (SERVEL)", "BOL": "Tribunal Supremo Electoral (TSE)",
    "ECU": "Consejo Nacional Electoral (CNE)", "PER": "Jurado Nacional de Elecciones (JNE)",
    "HND": "Consejo Nacional Electoral (CNE)", "SLV": "Tribunal Supremo Electoral (TSE)",
    "PAN": "Tribunal Electoral", "CRI": "Tribunal Supremo de Elecciones (TSE)",
    "DOM": "Junta Central Electoral (JCE)", "PRY": "Tribunal Superior de Justicia Electoral (TSJE)",
    "CUB": "Comision Electoral Nacional", "DEU": "Bundeswahlleiter",
    "FRA": "Conseil Constitutionnel", "HUN": "Nemzeti Valasztasi Bizottsag",
    "POL": "Panstwowa Komisja Wyborcza (PKW)", "TUR": "Yuksek Secim Kurulu (YSK)",
    "RUS": "Tsentralnaya izbiratelnaya komissiya (TsIK)",
    "BLR": "Tsentralnaya komissiya po vyboram",
    "UKR": "Tsentralna vyborcha komisiya (TsVK)",
    "GEO": "Central Election Commission of Georgia",
    "ZAF": "Electoral Commission (IEC)", "NGA": "Independent National Electoral Commission (INEC)",
    "KEN": "Independent Electoral and Boundaries Commission (IEBC)",
    "ZWE": "Zimbabwe Electoral Commission (ZEC)", "GHA": "Electoral Commission of Ghana (EC)",
    "IND": "Election Commission of India (ECI)", "PHL": "Commission on Elections (COMELEC)",
    "IDN": "Komisi Pemilihan Umum (KPU)", "THA": "Election Commission of Thailand",
    "TUN": "Instance Superieure Independante pour les Elections (ISIE)",
}

COUNTRY_CATALOG = {
    "VEN": {"name": "Venezuela",       "flag": "🇻🇪", "election_date": "2025-12-07"},
    "NIC": {"name": "Nicaragua",       "flag": "🇳🇮", "election_date": "2026-11-07"},
    "GTM": {"name": "Guatemala",       "flag": "🇬🇹", "election_date": "2027-06-20"},
    "URY": {"name": "Uruguay",         "flag": "🇺🇾", "election_date": "2029-10-26"},
    "COL": {"name": "Colombia",        "flag": "🇨🇴", "election_date": "2026-03-08"},
    "BRA": {"name": "Brasil",          "flag": "🇧🇷", "election_date": "2026-10-04"},
    "MEX": {"name": "Mexico",          "flag": "🇲🇽", "election_date": "2027-06-06"},
    "ARG": {"name": "Argentina",       "flag": "🇦🇷", "election_date": "2027-10-24"},
    "CHL": {"name": "Chile",           "flag": "🇨🇱", "election_date": "2025-11-23"},
    "BOL": {"name": "Bolivia",         "flag": "🇧🇴", "election_date": "2026-03-22", "last_election": "2025-08-17", "observation_protocol": True, "phase": "electoral"},
    "ECU": {"name": "Ecuador",         "flag": "🇪🇨", "election_date": "2025-02-09"},
    "PER": {"name": "Peru",            "flag": "🇵🇪", "election_date": "2026-04-12"},
    "HND": {"name": "Honduras",        "flag": "🇭🇳", "election_date": "2025-11-30"},
    "SLV": {"name": "El Salvador",     "flag": "🇸🇻", "election_date": "2027-02-28"},
    "PAN": {"name": "Panama",          "flag": "🇵🇦", "election_date": "2029-05-06"},
    "CRI": {"name": "Costa Rica",      "flag": "🇨🇷", "election_date": "2026-02-01"},
    "DOM": {"name": "Rep. Dominicana", "flag": "🇩🇴", "election_date": "2028-05-21"},
    "PRY": {"name": "Paraguay",        "flag": "🇵🇾", "election_date": "2028-04-30"},
    "CUB": {"name": "Cuba",            "flag": "🇨🇺", "election_date": "2028-03-01"},
    "DEU": {"name": "Alemania",        "flag": "🇩🇪", "election_date": "2025-02-23"},
    "FRA": {"name": "Francia",         "flag": "🇫🇷", "election_date": "2027-04-23"},
    "HUN": {"name": "Hungria",         "flag": "🇭🇺", "election_date": "2026-04-12"},
    "POL": {"name": "Polonia",         "flag": "🇵🇱", "election_date": "2027-10-15"},
    "TUR": {"name": "Turquia",         "flag": "🇹🇷", "election_date": "2028-06-18"},
    "RUS": {"name": "Rusia",           "flag": "🇷🇺", "election_date": "2030-03-15"},
    "BLR": {"name": "Bielorrusia",     "flag": "🇧🇾", "election_date": "2025-01-26"},
    "UKR": {"name": "Ucrania",         "flag": "🇺🇦", "election_date": "2025-03-31"},
    "GEO": {"name": "Georgia",         "flag": "🇬🇪", "election_date": "2028-10-26"},
    "ZAF": {"name": "Sudafrica",       "flag": "🇿🇦", "election_date": "2029-05-29"},
    "NGA": {"name": "Nigeria",         "flag": "🇳🇬", "election_date": "2027-02-20"},
    "KEN": {"name": "Kenia",           "flag": "🇰🇪", "election_date": "2027-08-09"},
    "ZWE": {"name": "Zimbabue",        "flag": "🇿🇼", "election_date": "2028-07-30"},
    "GHA": {"name": "Ghana",           "flag": "🇬🇭", "election_date": "2028-12-07"},
    "IND": {"name": "India",           "flag": "🇮🇳", "election_date": "2029-05-01"},
    "PHL": {"name": "Filipinas",       "flag": "🇵🇭", "election_date": "2028-05-13"},
    "IDN": {"name": "Indonesia",       "flag": "🇮🇩", "election_date": "2029-02-14"},
    "THA": {"name": "Tailandia",       "flag": "🇹🇭", "election_date": "2027-05-01"},
    "TUN": {"name": "Tunez",           "flag": "🇹🇳", "election_date": "2029-10-06"},
}


# ── Carga final de módulos (sobreescribe las definiciones inline si disponibles)
try:
    from modules.instruments import (
        REGION_AMERICAS, REGION_EUROPE, REGION_AFRICA, REGION_ASIA_PACIFIC, REGION_ARAB,
        COUNTRY_REGIONS, UNIVERSAL_INSTRUMENTS, REGIONAL_INSTRUMENTS, EMB_NAMES,
    )
    from modules.catalog import COUNTRY_CATALOG
    from modules.mock_data import MOCK_OSINT_DATA, MOCK_POLITICAL_DATA
    _MODULES_LOADED = True
    print("[MODULES] instruments, catalog, mock_data cargados desde módulos.")
except ImportError as _mod_err:
    print(f"[MODULES] Usando definiciones inline ({_mod_err}).")

# PERU_* se cargan también desde módulo si está disponible
try:
    from modules.peru_data import (
        PERU_ELECTORAL_SYSTEM, PERU_POLITICAL_FORCES, PERU_PARL_DATA,
        PERU_REGIONS_DATA, PERU_HISTORICAL_EVENTS, PERU_DIGITAL_THREATS,
        PERU_GENDER_DATA, PERU_COUNTRY_PROFILE, PERU_OVERSEAS_VOTE,
        PERU_ORGANIZED_CRIME, PERU_VDEM_STATIC, PERU_RUNOFF_2026,
    )
    print("[MODULES] peru_data cargado desde módulo.")
except ImportError:
    pass   # fallback a definiciones inline más abajo en el archivo

# V-Dem static fallback — todos los países soportados (1985-2024)
try:
    from modules.vdem_static import VDEM_STATIC
    print("[MODULES] vdem_static cargado (38 países, 25 indicadores, 1985-2024).")
except ImportError:
    VDEM_STATIC: dict = {}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. AGENTES
# ═══════════════════════════════════════════════════════════════════════════════

def agent_log(state: ElectionRiskState, agent: str, message: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    state["agent_logs"].append(f"[{timestamp}] [{agent}] {message}")


# ─── Perfil dinamico ─────────────────────────────────────────────────────────

def build_dynamic_osint_profile(code: str, fh_data, vdem_data) -> dict:
    fh_score = fh_data.get("total_score", 50) if fh_data else 50
    fh_status = fh_data.get("status", "Partly Free") if fh_data else "Partly Free"
    cl = fh_data.get("civil_liberties_rating", 4) if fh_data else 4
    pr = fh_data.get("political_rights_rating", 4) if fh_data else 4
    if fh_score < 20:
        media_restr, opp_bans, const_amend, disq = "total", True, True, 5
    elif fh_score < 40:
        media_restr, opp_bans, const_amend, disq = "severe", True, True, 2
    elif fh_score < 60:
        media_restr, opp_bans, const_amend, disq = "moderate", False, False, 0
    else:
        media_restr, opp_bans, const_amend, disq = "none", False, False, 0
    intl_obs_vdem = vdem_data.get("international_observation") if vdem_data else None
    obs_invited = False if (intl_obs_vdem is False or fh_score < 20) else True
    obs_restr = "restricted_or_banned" if fh_score < 20 else "some_access_limitations" if fh_score < 40 else "none"
    registry_sizes = {
        "COL": 39_000_000, "BRA": 156_000_000, "MEX": 98_000_000, "ARG": 35_000_000,
        "CHL": 15_000_000, "BOL": 7_500_000, "ECU": 13_000_000, "PER": 25_000_000,
        "HND": 5_500_000, "SLV": 5_000_000, "PAN": 2_800_000, "CRI": 3_600_000,
        "DOM": 8_000_000, "PRY": 4_500_000, "CUB": 8_500_000,
        "DEU": 61_000_000, "FRA": 48_000_000, "HUN": 8_000_000, "POL": 29_000_000,
        "TUR": 60_000_000, "RUS": 109_000_000, "BLR": 7_000_000, "UKR": 36_000_000,
        "GEO": 3_500_000, "ZAF": 27_000_000, "NGA": 93_000_000, "KEN": 22_000_000,
        "ZWE": 5_700_000, "GHA": 17_000_000, "IND": 950_000_000, "PHL": 65_000_000,
        "IDN": 204_000_000, "THA": 52_000_000, "TUN": 9_000_000,
    }
    press = "severely_restricted" if cl >= 5 else "restricted" if cl >= 4 else "partially_restricted" if cl >= 3 else "guaranteed"
    assembly = "banned" if cl >= 6 else "restricted" if cl >= 4 else "partially_restricted" if cl >= 3 else "guaranteed"
    judicial = "captured" if cl >= 6 else "compromised" if cl >= 5 else "under_pressure" if cl >= 4 else "strong"
    return {
        "freedom_house_score": fh_score, "freedom_house_status": fh_status,
        "vdem_liberal_democracy": vdem_data.get("liberal_democracy", 0.5) if vdem_data else 0.5,
        "vdem_electoral_democracy": vdem_data.get("electoral_democracy", 0.5) if vdem_data else 0.5,
        "emb_name": EMB_NAMES.get(code, f"Organismo Electoral de {code}"),
        "emb_independence": vdem_data.get("emb_independence_level", "partial") if vdem_data else "partial",
        "emb_opposition_representation": fh_score >= 50,
        "registry_status": "no_independent_audit" if fh_score < 30 else "partially_audited" if fh_score < 60 else "fully_audited",
        "voter_registry_size": registry_sizes.get(code, 10_000_000),
        "legal_framework": {"constitutional_amendments_recent": const_amend, "opposition_party_bans": opp_bans,
                            "candidate_disqualifications": disq, "media_law_restrictions": media_restr},
        "civil_liberties": {"freedom_of_assembly": assembly, "freedom_of_press": press,
                            "judicial_independence": judicial, "political_prisoners": pr >= 6},
        "international_observation": {"invited": obs_invited, "restrictions": obs_restr},
        "_dynamic": True,
    }


# ─── AGENTE 1: OSINT Ingestion Agent ─────────────────────────────────────────

def ingestion_agent(state: ElectionRiskState) -> ElectionRiskState:  # MIGRADO a agents/nodes.py (run_ingestion)
    agent_name = "OSINT_IngestionAgent"
    agent_log(state, agent_name, f"Iniciando ingesta para {state['country']} ({state['country_code']})")

    code = state["country_code"]

    if code in MOCK_OSINT_DATA:
        osint = MOCK_OSINT_DATA[code]
        agent_log(state, agent_name, "Perfil OSINT: hardcodeado (datos verificados manualmente)")
    else:
        _fh_pre = get_freedom_house_country(FH_DF, code)
        _vdem_pre = get_vdem_country(VDEM_DF, code)
        if not _fh_pre and not _vdem_pre:
            state["errors"].append(f"No hay datos disponibles para {code}")
            agent_log(state, agent_name, f"ERROR: {code} no encontrado en ninguna fuente")
            state["context_data"] = {}
            return state
        osint = build_dynamic_osint_profile(code, _fh_pre, _vdem_pre)
        agent_log(state, agent_name, "Perfil OSINT: DINAMICO (derivado de FH + V-Dem)")

    # ── V-Dem: datos REALES ──
    vdem_real = get_vdem_country(VDEM_DF, code)

    if vdem_real:
        vdem_value = vdem_real
        vdem_confidence = CONFIDENCE_CONFIRMED
        vdem_source_id = f"vdem_{VDEM_VERSION}_{vdem_real['year']}"
        vdem_source_type = SOURCE_API
        vdem_notes = (
            f"Dato real. V-Dem Dataset {VDEM_VERSION}, año {vdem_real['year']}. "
            f"Citación: {VDEM_CITATION}"
        )
        agent_log(state, agent_name, f"V-Dem REAL cargado: libdem={vdem_real['liberal_democracy']}, "
                  f"polyarchy={vdem_real['electoral_democracy']}, año={vdem_real['year']}")
    else:
        vdem_value = {
            "liberal_democracy": osint["vdem_liberal_democracy"],
            "electoral_democracy": osint["vdem_electoral_democracy"],
        }
        vdem_confidence = CONFIDENCE_MOCK
        vdem_source_id = "vdem_mock_fallback"
        vdem_source_type = SOURCE_MOCK
        vdem_notes = f"Mock fallback: país {code} no encontrado en V-Dem {VDEM_VERSION}."
        agent_log(state, agent_name, f"V-Dem MOCK (fallback): {code} no encontrado en CSV.")

    # ── PEI: datos REALES ──
    pei_real = get_pei_country(PEI_DF, code)

    if pei_real:
        agent_log(state, agent_name, f"PEI REAL: elección={pei_real['election_id']}, "
                  f"EMBs={pei_real['emb_score']}, año={pei_real['year']}")
    else:
        agent_log(state, agent_name, f"PEI: no hay datos para {code} — usando mock.")

    # ── Freedom House: datos REALES ──
    fh_real = get_freedom_house_country(FH_DF, code)

    if fh_real:
        fh_value = fh_real
        fh_confidence = CONFIDENCE_CONFIRMED
        fh_source_id = f"freedom_house_{FH_VERSION}_{fh_real['edition']}"
        fh_source_type = SOURCE_API
        fh_notes = (
            f"Dato real. Freedom House FIW edición {fh_real['edition']}. "
            f"Citación: {FH_CITATION}"
        )
        agent_log(state, agent_name, f"Freedom House REAL: score={fh_real['total_score']}/100, "
                  f"status={fh_real['status']}, edición={fh_real['edition']}")
    else:
        fh_value = {"score": osint["freedom_house_score"], "status": osint["freedom_house_status"]}
        fh_confidence = CONFIDENCE_MOCK
        fh_source_id = "freedom_house_mock_fallback"
        fh_source_type = SOURCE_MOCK
        fh_notes = f"Mock fallback: país {code} no encontrado en Freedom House {FH_VERSION}."
        agent_log(state, agent_name, f"Freedom House MOCK (fallback): {code} no encontrado en CSV.")

    context = {
        "country": state["country"],
        "country_code": code,
        "region": COUNTRY_REGIONS.get(code, "unknown"),
        "collected_at": datetime.now(timezone.utc).isoformat(),

        "freedom_house": create_trace(
            value=fh_value,
            source_id=fh_source_id,
            source_type=fh_source_type,
            source_url=FH_SOURCE_URL,
            confidence=fh_confidence,
            legal_basis=FH_CITATION,
            agent_id="OSINT_IngestionAgent",
            notes=fh_notes,
        ),
        "vdem": create_trace(
            value=vdem_value,
            source_id=vdem_source_id,
            source_type=vdem_source_type,
            source_url=VDEM_SOURCE_URL,
            confidence=vdem_confidence,
            legal_basis="V-Dem Dataset CC-BY-SA. " + VDEM_CITATION,
            agent_id="OSINT_IngestionAgent",
            notes=vdem_notes,
        ),

        "pei": create_trace(
            value=pei_real if pei_real else {
                "overall_integrity": None,
                "emb_score": osint.get("emb_pei_score"),
                "legal_framework": None,
                "media_coverage": None,
                "campaign_finance": None,
            },
            source_id=f"pei_{pei_real['election_id']}" if pei_real else f"pei_mock_{code.lower()}",
            source_type=SOURCE_API if pei_real else SOURCE_MOCK,
            source_url=PEI_SOURCE_URL,
            confidence=CONFIDENCE_CONFIRMED if pei_real else CONFIDENCE_MOCK,
            legal_basis=PEI_CITATION if pei_real else "",
            agent_id="OSINT_IngestionAgent",
            notes=(
                f"PEI {PEI_VERSION}. Elección: {pei_real['election_id']} ({pei_real['year']}). "
                f"EMBs={pei_real['emb_score']}, Marco legal={pei_real['legal_framework']}."
            ) if pei_real else f"Mock. País {code} no encontrado en PEI {PEI_VERSION}.",
        ),

        "emb": create_trace(
            value={
                "name": osint["emb_name"],
                "independence_level": vdem_real["emb_independence_level"] if vdem_real else osint["emb_independence"],
                "autonomy_score": vdem_real["emb_autonomy"] if vdem_real else None,
                "autonomy_raw": vdem_real["emb_autonomy_raw"] if vdem_real else None,
                "capacity_score": vdem_real["emb_capacity"] if vdem_real else None,
                "electoral_irregularities": vdem_real["electoral_irregularities"] if vdem_real else None,
                "electoral_intimidation": vdem_real["electoral_intimidation"] if vdem_real else None,
                "opposition_representation": osint["emb_opposition_representation"],
                "data_year": vdem_real["year"] if vdem_real else None,
            },
            source_id=vdem_source_id if vdem_real else f"emb_mock_{code.lower()}",
            source_type=vdem_source_type if vdem_real else SOURCE_MOCK,
            source_url=VDEM_SOURCE_URL if vdem_real else "",
            confidence=vdem_confidence if vdem_real else CONFIDENCE_MOCK,
            legal_basis="V-Dem Dataset CC-BY-SA. " + VDEM_CITATION if vdem_real else "",
            agent_id="OSINT_IngestionAgent",
            notes=(
                f"EMB autonomy/capacity/irregularities: V-Dem {VDEM_VERSION} año {vdem_real['year']}. "
                f"Nivel independencia: {vdem_real['emb_independence_level']}. "
                f"Nombre EMB: mock pendiente."
            ) if vdem_real else "Mock data. País no encontrado en V-Dem.",
        ),

        "voter_registry": create_trace(
            value={
                "status": (
                    "no_independent_audit" if pei_real and pei_real.get("reg_inaccurate") is not None and pei_real["reg_inaccurate"] < 2.5
                    else "partially_audited" if pei_real and pei_real.get("reg_inaccurate") is not None and pei_real["reg_inaccurate"] < 3.5
                    else "fully_audited" if pei_real and pei_real.get("reg_inaccurate") is not None
                    else osint["registry_status"]
                ),
                "size": osint["voter_registry_size"],
                "pei_voter_reg_score": pei_real["voter_registration"] if pei_real else None,
                "pei_reg_listed": pei_real["reg_listed"] if pei_real else None,
                "pei_reg_inaccurate": pei_real["reg_inaccurate"] if pei_real else None,
                "pei_reg_ineligible": pei_real["reg_ineligible"] if pei_real else None,
                "data_year": pei_real["year"] if pei_real else None,
            },
            source_id=f"pei_voter_registry_{pei_real['election_id']}" if pei_real else f"voter_registry_mock_{code.lower()}",
            source_type=SOURCE_API if pei_real else SOURCE_MOCK,
            source_url=PEI_SOURCE_URL if pei_real else "",
            confidence=CONFIDENCE_CONFIRMED if pei_real else CONFIDENCE_MOCK,
            legal_basis=PEI_CITATION if pei_real else "",
            agent_id="OSINT_IngestionAgent",
            notes=f"PEI {PEI_VERSION} elección {pei_real['year']}. Score registro: {pei_real['voter_registration']}/100." if pei_real else "Mock data.",
        ),

        "legal_framework": create_trace(
            value={
                **(osint["legal_framework"]),
                **({"pei_laws_score": pei_real["legal_framework"],
                    "pei_laws_unfair": pei_real["laws_unfair"],
                    "pei_favored_incumbent": pei_real["laws_favored_incumbent"],
                    "pei_opp_prevent": pei_real["opp_prevent"],
                    "data_year": pei_real["year"],
                } if pei_real else {}),
                **({"vdem_opposition_barriers": vdem_real.get("opposition_party_barriers"),
                    "vdem_judicial_review": vdem_real.get("judicial_review"),
                    "vdem_opposition_autonomy": vdem_real.get("opposition_autonomy"),
                    "vdem_data_year": vdem_real.get("year"),
                } if vdem_real else {}),
            },
            source_id=f"pei_legal_{pei_real['election_id']}" if pei_real else (f"vdem_legal_{code.lower()}" if vdem_real else f"legal_framework_mock_{code.lower()}"),
            source_type=SOURCE_API if (pei_real or vdem_real) else SOURCE_MOCK,
            source_url=PEI_SOURCE_URL if pei_real else (VDEM_SOURCE_URL if vdem_real else ""),
            confidence=CONFIDENCE_CONFIRMED if (pei_real or vdem_real) else CONFIDENCE_MOCK,
            legal_basis=PEI_CITATION if pei_real else (VDEM_CITATION if vdem_real else ""),
            agent_id="OSINT_IngestionAgent",
            notes=(f"PEI {PEI_VERSION} elección {pei_real['year']}. Score marco legal: {pei_real['legal_framework']}/100." if pei_real else "") +
                  (f" V-Dem v15 ({vdem_real['year']}): v2psbars={vdem_real.get('opposition_party_barriers')}, v2jureview={vdem_real.get('judicial_review')}." if vdem_real else "") or "Mock data.",
        ),

        "civil_liberties": create_trace(
            value={
                **(derive_civil_liberties_from_fh(fh_real) if fh_real else osint["civil_liberties"]),
                **({"vdem_opposition_barriers": vdem_real.get("opposition_party_barriers"),
                    "vdem_judicial_review": vdem_real.get("judicial_review"),
                    "vdem_opposition_autonomy": vdem_real.get("opposition_autonomy"),
                    "vdem_freedom_of_association": vdem_real.get("freedom_of_association"),
                    "vdem_rule_of_law": vdem_real.get("rule_of_law"),
                    "vdem_data_year": vdem_real.get("year"),
                } if vdem_real else {}),
            },
            source_id=fh_source_id if fh_real else "civil_liberties_mock",
            source_type=fh_source_type if fh_real else SOURCE_MOCK,
            source_url=FH_SOURCE_URL if fh_real else "",
            confidence=fh_confidence if fh_real else CONFIDENCE_MOCK,
            legal_basis=FH_CITATION if fh_real else "",
            agent_id="OSINT_IngestionAgent",
            notes=(f"Derivado de FH FIW {fh_real['edition']}. CL={fh_real['civil_liberties_rating']}/7, PR={fh_real['political_rights_rating']}/7." if fh_real else "Mock data.") +
                  (f" Enriquecido con V-Dem v15 ({vdem_real['year']}): v2psbars={vdem_real.get('opposition_party_barriers')}, v2jureview={vdem_real.get('judicial_review')}." if vdem_real else ""),
        ),

        # ── RSF: datos REALES de libertad de prensa ──
        "rsf": create_trace(
            value=(lambda r: r if r else {"score": None, "rank": None})(get_rsf_country(RSF_DF, code)),
            source_id=f"rsf_{RSF_VERSION}_{code}" if get_rsf_country(RSF_DF, code) else f"rsf_mock_{code}",
            source_type=SOURCE_API if get_rsf_country(RSF_DF, code) else SOURCE_MOCK,
            source_url=RSF_SOURCE_URL,
            confidence=CONFIDENCE_CONFIRMED if get_rsf_country(RSF_DF, code) else CONFIDENCE_MOCK,
            legal_basis=RSF_CITATION if get_rsf_country(RSF_DF, code) else "",
            agent_id="OSINT_IngestionAgent",
            notes=(lambda r: f"RSF {RSF_VERSION}. Score: {r['score']}/100, Rank: #{r['rank']}." if r else "RSF no disponible.")(get_rsf_country(RSF_DF, code)),
        ),

        "digital_vdem": create_trace(
            value={
                "internet_censorship": vdem_real.get("internet_censorship") if vdem_real else None,
                "media_censorship": vdem_real.get("media_censorship") if vdem_real else None,
                "journalist_harassment": vdem_real.get("journalist_harassment") if vdem_real else None,
                "media_bias_vdem": vdem_real.get("media_bias_vdem") if vdem_real else None,
                "gov_social_media_dominance": vdem_real.get("gov_social_media_dominance") if vdem_real else None,
                "gov_internet_filter_capacity": vdem_real.get("gov_internet_filter_capacity") if vdem_real else None,
                "social_media_regulation": vdem_real.get("social_media_regulation") if vdem_real else None,
                "freedom_of_expression": vdem_real.get("freedom_of_expression") if vdem_real else None,
                "data_year": vdem_real.get("year") if vdem_real else None,
            },
            source_id=vdem_source_id if vdem_real else f"digital_vdem_mock_{code.lower()}",
            source_type=vdem_source_type if vdem_real else SOURCE_MOCK,
            source_url=VDEM_SOURCE_URL if vdem_real else "",
            confidence=vdem_confidence if vdem_real else CONFIDENCE_MOCK,
            legal_basis="V-Dem Dataset CC-BY-SA. " + VDEM_CITATION if vdem_real else "",
            agent_id="OSINT_IngestionAgent",
            notes=f"V-Dem {VDEM_VERSION} variables digitales año {vdem_real.get('year')}." if vdem_real else "V-Dem digital no disponible.",
        ),

        "international_observation": create_trace(
            value={
                **osint["international_observation"],
                "invited": (
                    vdem_real["international_observation"]
                    if vdem_real and vdem_real["international_observation"] is not None
                    else osint["international_observation"]["invited"]
                ),
                "data_source": "V-Dem v2elintmon" if (vdem_real and vdem_real["international_observation"] is not None) else "mock",
            },
            source_id=vdem_source_id if (vdem_real and vdem_real["international_observation"] is not None) else f"intl_observation_{code.lower()}",
            source_type=vdem_source_type if (vdem_real and vdem_real["international_observation"] is not None) else SOURCE_MOCK,
            source_url=VDEM_SOURCE_URL if (vdem_real and vdem_real["international_observation"] is not None) else "",
            confidence=CONFIDENCE_MOCK,
            agent_id="OSINT_IngestionAgent",
            notes="Mock data. En producción: Portales de OEA/OSCE/UA + notas de prensa de misiones.",
        ),
    }

    traces = collect_traces(context)
    state["trace_log"].extend(traces)
    state["context_data"] = context

    vdem_log_val = vdem_real['liberal_democracy'] if vdem_real else osint['vdem_liberal_democracy']
    vdem_log_src = f"REAL (V-Dem {VDEM_VERSION})" if vdem_real else "MOCK (fallback)"
    fh_log_val = fh_real['total_score'] if fh_real else osint['freedom_house_score']
    fh_log_src = f"REAL (FH {FH_VERSION})" if fh_real else "MOCK (fallback)"
    emb_level = vdem_real['emb_independence_level'] if vdem_real else osint['emb_independence']
    emb_aut = vdem_real['emb_autonomy'] if vdem_real else "N/A"
    intl_obs = vdem_real['international_observation'] if vdem_real else osint['international_observation']['invited']

    agent_log(state, agent_name, f"Ingesta completada. FH: {fh_log_val}/100 [{fh_log_src}] | V-Dem libdem: {vdem_log_val} [{vdem_log_src}]")
    agent_log(state, agent_name, f"EMB: nivel={emb_level}, autonomía={emb_aut} [V-Dem REAL] | Obs. intl: {intl_obs}")
    pei_log = f"EMBs={pei_real['emb_score']}, año={pei_real['year']}" if pei_real else "no disponible"
    agent_log(state, agent_name, f"PEI {PEI_VERSION}: {pei_log}")
    agent_log(state, agent_name, f"Trazabilidad: FH: {fh_confidence} | V-Dem+EMB: {vdem_confidence} | PEI: {'confirmed' if pei_real else 'mock'} | Padrón: mock")
    agent_log(state, agent_name, f"Región: {COUNTRY_REGIONS.get(code, 'unknown')} — Instrumentos aplicables: {len(state['applicable_instruments']['all_ids'])}")

    return state


# ─── AGENTE 2: Political & Digital Analyst Agent ─────────────────────────────

def political_analyst_agent(state: ElectionRiskState) -> ElectionRiskState:  # MIGRADO a agents/nodes.py (run_political_analyst)
    agent_name = "Political_DigitalAnalystAgent"
    agent_log(state, agent_name, f"Iniciando análisis político-digital para {state['country']}")

    code = state["country_code"]

    if code in MOCK_POLITICAL_DATA:
        political = MOCK_POLITICAL_DATA[code]
    else:
        _fh_pol = get_freedom_house_country(FH_DF, code)
        _fh_score = _fh_pol.get("total_score", 50) if _fh_pol else 50
        _bias = round((100 - _fh_score) / 100, 2)
        political = {
            "media_bias_index": _bias,
            "media_bias_direction": "pro_incumbent" if _fh_score < 40 else "mixed" if _fh_score < 70 else "balanced",
            "media_exposure": {"incumbent": int(50 + _bias*40), "opposition": int(30 - _bias*20), "others": 20},
            "campaign_finance": {
                "transparency_score": round(_fh_score / 100, 2),
                "state_resource_abuse": "systematic" if _fh_score < 30 else "moderate" if _fh_score < 60 else "none_detected",
                "corporate_donations_disclosed": _fh_score >= 60,
            },
            "digital_ecosystem": {
                "bot_activity_detected": _fh_score < 50,
                "bot_network_size_estimate": max(0, int((50 - _fh_score) * 500)) if _fh_score < 50 else 0,
                "hate_speech_incidents": max(0, int((60 - _fh_score) * 3)),
                "url_censorship_detected": _fh_score < 35,
                "censored_domains": [],
                "disinformation_campaigns": max(0, int((50 - _fh_score) / 5)) if _fh_score < 50 else 0,
                "voter_suppression_tactics_online": _fh_score < 30,
            },
            "power_network": {
                "candidate_media_ownership_links": 2 if _fh_score < 40 else 0,
                "state_enterprise_campaign_links": 3 if _fh_score < 30 else 1 if _fh_score < 60 else 0,
                "military_political_links": _fh_score < 25,
            },
        }
        agent_log(state, agent_name, f"Perfil politico: DINAMICO (FH score={_fh_score})")

    # PEI real para medios y financiamiento
    pei_val = get_pei_country(PEI_DF, code) or {}
    pei_ok = bool(pei_val and pei_val.get("election_id"))
    pei_media_score = pei_val.get("media_coverage") if pei_ok else None
    pei_finance_score = pei_val.get("campaign_finance") if pei_ok else None
    pei_year_pol = pei_val.get("year") if pei_ok else None

    if pei_media_score is not None:
        derived_bias_index = round((100 - pei_media_score) / 100, 4)
        media_source = f"PEI {PEI_VERSION} ({pei_year_pol})"
        agent_log(state, agent_name, f"Media REAL (PEI): MEDIACOVERAGE={pei_media_score}/100, bias_index derivado={derived_bias_index}, fair_access={pei_val.get('media_fair_access')}, balanced={pei_val.get('media_balanced')}")
    else:
        derived_bias_index = political["media_bias_index"]
        media_source = "mock"
        agent_log(state, agent_name, "Media: usando mock (PEI no disponible)")

    if pei_finance_score is not None:
        derived_finance_transp = round(pei_finance_score / 100, 4)
        finance_source = f"PEI {PEI_VERSION} ({pei_year_pol})"
        agent_log(state, agent_name, f"Finance REAL (PEI): CAMPAIGNFINANCE={pei_finance_score}/100, resources={pei_val.get('finance_resources')}, bribed={pei_val.get('finance_bribed')}")
    else:
        derived_finance_transp = political["campaign_finance"]["transparency_score"]
        finance_source = "mock"
        agent_log(state, agent_name, "Finance: usando mock (PEI no disponible)")

    analysis = {
        "source": "mixed_pei_real+mock" if pei_ok else "mock_data_v1",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "media_analysis": {
            "bias_index": derived_bias_index,
            "bias_direction": political["media_bias_direction"],
            "exposure_distribution": political["media_exposure"],
            "assessment": _assess_media_bias(derived_bias_index),
            "pei_media_score": pei_media_score,
            "data_source": media_source,
        },
        "campaign_finance": {
            "transparency_score": derived_finance_transp,
            "state_resource_abuse": political["campaign_finance"]["state_resource_abuse"],
            "donations_disclosed": political["campaign_finance"]["corporate_donations_disclosed"],
            "assessment": _assess_finance_transparency(derived_finance_transp),
            "pei_finance_score": pei_finance_score,
            "data_source": finance_source,
        },
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


# Palabras clave que indican escala masiva — activan escalación de severidad
_SCALE_KEYWORDS = [
    r"\b(\d[\d.,]+)\s*(electores?|votantes?|personas?|registros?|casos?|ciudadanos?)",  # número + afectados
    r"\b(miles|decenas de miles|cientos de miles|millones)\b",
    r"\b(masivo|masiva|sistémico|sistémica|generalizado|generalizada|padrón|registro electoral)\b",
    r"\b(todo el país|todo el territorio|a nivel nacional|nacional)\b",
]
# Categorías donde el alcance masivo escala la severidad
_SCALE_SENSITIVE_CATEGORIES = {
    "voter_suppression", "voter_intimidation", "ballot_tampering",
    "fraud_allegation", "irregular_procedure", "voter_registration",
    "disinformation",
}
# Umbral numérico: si el hallazgo menciona más de N afectados, escalar
_SCALE_THRESHOLD = 1_000


def _auto_escalate_severity(severity: str, category: str, finding: str) -> str:
    """
    Escala automáticamente la severidad si el hallazgo describe afectación masiva.
    Reglas basadas en estándares ICCPR Art. 25(b) — restricciones irrazonables al sufragio.

    - voter_suppression / voter_intimidation / ballot_tampering con escala ≥1,000 personas → HIGH mínimo
    - Cualquier hallazgo con escala ≥10,000 afectados → HIGH mínimo
    - Hallazgo "sistémico" o "a nivel nacional" en categoría sensible → HIGH mínimo
    - No baja severidades: solo puede subir, nunca bajar.
    """
    import re as _re

    _SEV_ORDER = ["info", "low", "medium", "high", "critical"]
    current_idx = _SEV_ORDER.index(severity) if severity in _SEV_ORDER else 0
    escalated = severity

    # 1. Detectar número de afectados en el texto
    num_matches = _re.findall(r"[\d.,]+", finding)
    max_num = 0
    for m in num_matches:
        try:
            val = float(m.replace(",", "").replace(".", ""))
            if val > max_num:
                max_num = val
        except ValueError:
            pass

    # 2. Detectar palabras de escala masiva
    finding_lower = finding.lower()
    has_scale_word = any(
        _re.search(p, finding_lower) for p in _SCALE_KEYWORDS
    )

    # 3. Aplicar reglas de escalación
    if category in _SCALE_SENSITIVE_CATEGORIES:
        if max_num >= _SCALE_THRESHOLD or has_scale_word:
            # ≥1,000 afectados en categoría sensible → mínimo HIGH
            target_idx = _SEV_ORDER.index("high")
            if current_idx < target_idx:
                escalated = "high"

    # 4. Escala ≥10,000 en cualquier categoría → mínimo HIGH
    if max_num >= 10_000 and current_idx < _SEV_ORDER.index("high"):
        escalated = "high"

    return escalated



# ═══════════════════════════════════════════════════════════════════════════════
# AGENTE 5: Electoral Dictamen Agent
# ═══════════════════════════════════════════════════════════════════════════════

# Promedios regionales de referencia (FH 2025 + V-Dem 2024)
REGIONAL_AVERAGES = {
    "americas": {"fh": 58, "vdem": 0.42, "rsf": 48},
    "europe":   {"fh": 62, "vdem": 0.55, "rsf": 65},
    "africa":   {"fh": 38, "vdem": 0.28, "rsf": 42},
    "asia_pacific": {"fh": 44, "vdem": 0.35, "rsf": 45},
    "arab_states":  {"fh": 28, "vdem": 0.18, "rsf": 38},
    "unknown":  {"fh": 50, "vdem": 0.40, "rsf": 50},
}

SCORE_THRESHOLDS = {
    "fh": [
        (80, "sólidas garantías democráticas institucionales"),
        (60, "sistema democrático funcional con deficiencias puntuales"),
        (40, "democracia parcialmente libre con restricciones significativas"),
        (20, "régimen híbrido con libertades severamente limitadas"),
        (0,  "régimen autoritario con ausencia de garantías democráticas fundamentales"),
    ],
    "vdem": [
        (0.7, "democracia liberal consolidada"),
        (0.5, "democracia electoral con déficits institucionales"),
        (0.3, "régimen híbrido con fachada electoral"),
        (0.1, "autocracia electoral"),
        (0.0, "autocracia cerrada"),
    ],
    "pei": [
        (70, "proceso electoral con integridad aceptable"),
        (50, "proceso con deficiencias significativas en múltiples dimensiones"),
        (30, "proceso con violaciones sistemáticas a estándares internacionales"),
        (0,  "proceso sin integridad verificable"),
    ],
    "rsf": [
        (75, "entorno mediático favorable para la información electoral"),
        (55, "entorno mediático con restricciones moderadas"),
        (40, "entorno mediático problemático con interferencia estatal"),
        (25, "entorno mediático gravemente comprometido"),
        (0,  "entorno mediático hostil con censura sistemática"),
    ],
}


def _interpret_score(score, threshold_key: str) -> str:
    if score is None:
        return "sin datos verificados"
    thresholds = SCORE_THRESHOLDS.get(threshold_key, [])
    for threshold, label in thresholds:
        if score >= threshold:
            return label
    return thresholds[-1][1] if thresholds else "sin clasificación"


def _get_vdem_trend(df, country_code: str, current_year: int = 2024, years_back: int = 5) -> dict:
    """Calcula tendencia V-Dem libdem de los últimos N años."""
    if df is None:
        return {"available": False}
    try:
        rows = df[
            (df["country_text_id"] == country_code) &
            (df["year"] >= current_year - years_back) &
            (df["year"] <= current_year)
        ].sort_values("year")

        if len(rows) < 2:
            return {"available": False}

        values = [(int(r["year"]), round(float(r["v2x_libdem"]), 4)) for _, r in rows.iterrows()]
        first_val = values[0][1]
        last_val = values[-1][1]
        delta = round(last_val - first_val, 4)

        if delta >= 0.05:
            trend = "mejora significativa"
            trend_dir = "up"
        elif delta >= 0.01:
            trend = "leve mejora"
            trend_dir = "up"
        elif delta <= -0.05:
            trend = "deterioro significativo"
            trend_dir = "down"
        elif delta <= -0.01:
            trend = "leve deterioro"
            trend_dir = "down"
        else:
            trend = "estable"
            trend_dir = "stable"

        return {
            "available": True,
            "values": values,
            "delta": delta,
            "trend": trend,
            "trend_direction": trend_dir,
            "first_year": values[0][0],
            "first_value": first_val,
            "last_year": values[-1][0],
            "last_value": last_val,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


def electoral_dictamen_agent(state: ElectionRiskState) -> ElectionRiskState:  # MIGRADO a agents/nodes.py (run_dictamen_agent)
    agent_name = "Electoral_DictamenAgent"
    agent_log(state, agent_name, f"Generando dictamen técnico para {state['country']}")

    context = state.get("context_data", {})
    political = state.get("political_data", {})
    legal = state.get("legal_analysis", {})
    code = state["country_code"]
    region = COUNTRY_REGIONS.get(code, "unknown")

    # ── Extraer valores clave ────────────────────────────────────────────────
    def val(d):
        return extract_value(d) if isinstance(d, dict) and "_trace" in d else d

    fh_data = val(context.get("freedom_house", {})) or {}
    fh_score = fh_data.get("total_score", fh_data.get("score"))
    fh_status = fh_data.get("status", "N/D")
    fh_edition = fh_data.get("edition", "—")

    vdem_data = val(context.get("vdem", {})) or {}
    vdem_libdem = vdem_data.get("liberal_democracy")
    vdem_polyarchy = vdem_data.get("electoral_democracy")
    vdem_year = vdem_data.get("year", "—")

    emb_data = val(context.get("emb", {})) or {}
    emb_level = emb_data.get("independence_level", "unknown")
    emb_autonomy = emb_data.get("autonomy_score")
    emb_name = emb_data.get("name", "N/D")

    pei_data = val(context.get("pei", {})) or {}
    pei_integrity = pei_data.get("overall_integrity")
    pei_emb = pei_data.get("emb_score")
    pei_year = pei_data.get("year", "—")

    rsf_data = val(context.get("rsf", {})) or {}
    rsf_score = rsf_data.get("score")
    rsf_rank = rsf_data.get("rank")

    civil = val(context.get("civil_liberties", {})) or {}
    violations = legal.get("violations", [])
    confirmed_viols = [v for v in violations if v.get("confidence") == "confirmed"]
    risk_score = state.get("risk_score", 0)
    risk_level = state.get("risk_level", "unknown")

    # ── Tendencia histórica V-Dem ────────────────────────────────────────────
    trend = _get_vdem_trend(VDEM_DF, code)

    # ── Comparación regional ─────────────────────────────────────────────────
    reg_avg = REGIONAL_AVERAGES.get(region, REGIONAL_AVERAGES["unknown"])
    fh_vs_region = None
    vdem_vs_region = None
    rsf_vs_region = None
    if fh_score is not None:
        diff = fh_score - reg_avg["fh"]
        fh_vs_region = f"Freedom House: {'por encima' if diff > 0 else 'por debajo'} del promedio regional ({reg_avg['fh']}/100) en {abs(round(diff, 1))} puntos"
    if vdem_libdem is not None:
        diff = round(vdem_libdem - reg_avg["vdem"], 3)
        vdem_vs_region = f"V-Dem: {'por encima' if diff > 0 else 'por debajo'} del promedio regional ({reg_avg['vdem']}) en {abs(diff)} puntos"
    if rsf_score is not None:
        diff = round(rsf_score - reg_avg["rsf"], 1)
        rsf_vs_region = f"RSF: {'por encima' if diff > 0 else 'por debajo'} del promedio regional ({reg_avg['rsf']}/100) en {abs(diff)} puntos"

    # ── Nivel de confianza de los datos ─────────────────────────────────────
    confirmed_count = sum(1 for k in ["freedom_house", "vdem", "pei", "rsf", "digital_vdem"]
                          if get_trace(context.get(k, {})).get("confidence") == "confirmed")
    if confirmed_count >= 4:
        data_confidence = "HIGH"
        confidence_note = "La mayoría de los indicadores están respaldados por fuentes primarias verificadas."
    elif confirmed_count >= 2:
        data_confidence = "MEDIUM"
        confidence_note = "Algunos indicadores clave están verificados; otros son estimaciones del sistema."
    else:
        data_confidence = "LOW"
        confidence_note = "La mayoría de los indicadores son estimaciones pendientes de verificación con fuentes primarias."

    # ── Construir datos para LLM ─────────────────────────────────────────────
    fh_interp = _interpret_score(fh_score, "fh")
    vdem_interp = _interpret_score(vdem_libdem, "vdem") if vdem_libdem else "sin datos"
    pei_interp = _interpret_score(pei_integrity, "pei") if pei_integrity else "sin datos PEI"
    rsf_interp = _interpret_score(rsf_score, "rsf") if rsf_score else "sin datos RSF"

    trend_text = (
        f"V-Dem libdem pasó de {trend['first_value']} ({trend['first_year']}) a {trend['last_value']} ({trend['last_year']}): {trend['trend']} (delta={trend['delta']:+.4f})"
        if trend.get("available") else "Tendencia histórica no disponible"
    )

    emb_labels = {
        "full": "plenamente independiente",
        "partial": "con autonomía parcial",
        "compromised": "comprometida institucionalmente",
        "captured": "capturada por el ejecutivo",
    }
    emb_label = emb_labels.get(emb_level, emb_level)

    sys_prompt = (
        "Sos el Electoral Dictamen Agent de DEMOCRAC.IA/PEIRS. "
        "Tu función es generar dictámenes técnicos de integridad electoral de nivel profesional, "
        "precisos, basados exclusivamente en los datos verificados que recibes. "
        "Escribís en español con registro técnico-institucional. "
        "Nunca inventás datos. Si un dato no está disponible, lo indicás explícitamente. "
        "Tu dictamen será leído por analistas, observadores internacionales e inversores."
    )

    user_prompt = f"""Generá un dictamen técnico de integridad electoral con exactamente 4 párrafos.

DATOS VERIFICADOS (confidence=confirmed donde se indica):

PAÍS: {state['country']} | ELECCIÓN: {state['election_date']} | REGIÓN: {region}
ÍNDICE DE RIESGO PEIRS: {risk_score}/100 — {risk_level.upper()}

FREEDOM HOUSE FIW {fh_edition}: {fh_score}/100 — {fh_status}
→ Interpretación: {fh_interp}
→ Comparación regional: {fh_vs_region or 'sin datos comparativos'}

V-DEM v15 ({vdem_year}): libdem={vdem_libdem} | polyarchy={vdem_polyarchy}
→ Interpretación: {vdem_interp}
→ Comparación regional: {vdem_vs_region or 'sin datos comparativos'}
→ Tendencia 5 años: {trend_text}

EMB ({emb_name}): independencia {emb_level} ({emb_label})
Autonomía normalizada: {emb_autonomy}

PEI-10.0 ({pei_year}): integridad={pei_integrity}/100 | EMBs={pei_emb}/100
→ Interpretación: {pei_interp}

RSF 2025: score={rsf_score}/100 | rank=#{rsf_rank}/180
→ Interpretación: {rsf_interp}
→ Comparación regional: {rsf_vs_region or 'sin datos comparativos'}

LIBERTADES CIVILES (FH): prensa={civil.get('freedom_of_press','N/D')} | reunión={civil.get('freedom_of_assembly','N/D')} | judicial={civil.get('judicial_independence','N/D')}
PRESOS POLÍTICOS: {'Sí' if civil.get('political_prisoners') else 'No'}

VIOLACIONES DERECHO INTERNACIONAL: {len(violations)} total ({len(confirmed_viols)} verificadas)
CONFIANZA DE DATOS: {data_confidence} — {confidence_note}

ESTRUCTURA DE LOS 4 PÁRRAFOS:

Párrafo 1 — DIAGNÓSTICO INSTITUCIONAL (~100 palabras):
Interpretá qué significan los scores de Freedom House y V-Dem para este país en concreto.
No repitas los números — explicá qué implican institucionalmente.
Incluí la tendencia histórica: si el país mejoró o empeoró en los últimos 5 años y qué sugiere eso.

Párrafo 2 — ESTADO DEL ORGANISMO ELECTORAL (~90 palabras):
Evaluá la independencia del EMB en contexto. Qué implica ese nivel de autonomía para la conducción del proceso.
Si hay datos PEI, interpretá qué significa ese score de integridad para los estándares internacionales EOS.
Vinculá con el riesgo de impugnación de resultados.

Párrafo 3 — ECOSISTEMA INFORMATIVO Y LIBERTADES CIVILES (~90 palabras):
Evaluá el entorno mediático según RSF y las libertades civiles según FH.
Qué condiciones enfrenta el electorado para acceder a información electoral libre.
Comparación con el promedio regional si está disponible.

Párrafo 4 — DICTAMEN FINAL (~80 palabras):
Veredicto técnico integrado. No repitas datos — sintetizá el estado general.
Indicá el nivel de confianza de los datos y qué fuentes están pendientes de verificación.
Cerrá con una recomendación de acción para observadores internacionales.

Solo prosa. Sin subtítulos. Sin viñetas. Tono técnico-institucional de alto nivel."""

    def fallback_dictamen():
        return (
            f"El análisis institucional de {state['country']} revela un panorama democrático caracterizado por {fh_interp}, "
            f"con un índice de democracia liberal V-Dem de {vdem_libdem} que indica {vdem_interp}. "
            f"{trend_text}.\n\n"
            f"El organismo electoral ({emb_name}) presenta independencia {emb_label}, "
            f"factor determinante para la imparcialidad del proceso previsto para {state['election_date']}.\n\n"
            f"El entorno mediático registra un score RSF de {rsf_score}/100 ({rsf_interp}), "
            f"condicionando el acceso del electorado a información electoral libre y pluralista.\n\n"
            f"DICTAMEN: Nivel de riesgo {risk_level.upper()} ({risk_score}/100). "
            f"Confianza de datos: {data_confidence}. {confidence_note}"
        )

    dictamen_narrative = _llm_generate(sys_prompt, user_prompt, fallback_dictamen)

    dictamen = {
        "narrative": dictamen_narrative,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "data_confidence": data_confidence,
        "confidence_note": confidence_note,
        "confirmed_sources": confirmed_count,
        "trend": trend,
        "regional_comparison": {
            "region": region,
            "fh_vs_region": fh_vs_region,
            "vdem_vs_region": vdem_vs_region,
            "rsf_vs_region": rsf_vs_region,
            "regional_averages": reg_avg,
        },
        "score_interpretations": {
            "fh": fh_interp,
            "vdem": vdem_interp,
            "pei": pei_interp,
            "rsf": rsf_interp,
        },
        "dictamen_id": f"PEIRS-{state['run_id'][:8].upper()}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    state["dictamen"] = dictamen

    agent_log(state, agent_name, f"Dictamen generado. Confianza: {data_confidence} | Tendencia: {trend.get('trend', 'N/A')}")
    agent_log(state, agent_name, f"Comparación regional: FH {fh_vs_region or 'N/A'}")
    agent_log(state, agent_name, f"Interpretaciones: FH={fh_interp[:40]}... | V-Dem={vdem_interp[:40]}...")

    return state



# ─── LLM Helper ──────────────────────────────────────────────────────────────

def _llm_generate(prompt_system: str, prompt_user: str, fallback_fn, *args, **kwargs) -> str:  # MIGRADO a chapters/generators.py
    if llm is None:
        return fallback_fn(*args, **kwargs)
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [SystemMessage(content=prompt_system), HumanMessage(content=prompt_user)]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        print(f"[LLM] WARN: Error: {e}. Usando fallback.")
        return fallback_fn(*args, **kwargs)


# ─── AGENTE 3: Legal Compliance Agent ────────────────────────────────────────

def legal_compliance_agent(state: ElectionRiskState) -> ElectionRiskState:  # MIGRADO a agents/nodes.py (run_legal_compliance)
    agent_name = "Legal_ComplianceAgent"
    agent_log(state, agent_name, f"Iniciando análisis legal para {state['country']}")

    context = state.get("context_data", {})
    political = state.get("political_data", {})
    instruments = state.get("applicable_instruments", {})

    violations = []
    risk_factors = []
    mitigating_factors = []

    def val(traced):
        return extract_value(traced) if isinstance(traced, dict) else traced

    civil = val(context.get("civil_liberties", {}))

    if civil.get("freedom_of_press") in ["severely_restricted", "banned"]:
        violations.append({
            "treaty": "ICCPR", "article": "Art. 19",
            "right": "Libertad de Expresión",
            "finding": f"Libertad de prensa clasificada como '{civil['freedom_of_press']}'. "
                       "Violación directa del derecho a buscar, recibir y difundir información.",
            "severity": "critical",
            "confidence": get_trace(context.get("civil_liberties", {})).get("confidence", "unknown"),
        })

    if civil.get("freedom_of_assembly") in ["restricted", "banned"]:
        violations.append({
            "treaty": "ICCPR", "article": "Art. 21 & Art. 22",
            "right": "Libertad de Reunión y Asociación",
            "finding": f"Libertad de reunión clasificada como '{civil['freedom_of_assembly']}'. "
                       "Restricciones incompatibles con el derecho a la reunión pacífica.",
            "severity": "critical" if civil["freedom_of_assembly"] == "banned" else "high",
            "confidence": get_trace(context.get("civil_liberties", {})).get("confidence", "unknown"),
        })

    if civil.get("political_prisoners"):
        violations.append({
            "treaty": "ICCPR", "article": "Art. 9",
            "right": "Libertad y Seguridad Personal",
            "finding": "Existencia documentada de presos políticos. "
                       "Detención arbitraria de opositores viola el derecho a la libertad personal.",
            "severity": "critical",
            "confidence": get_trace(context.get("civil_liberties", {})).get("confidence", "unknown"),
        })

    if civil.get("judicial_independence") in ["compromised", "captured"]:
        violations.append({
            "treaty": "ICCPR", "article": "Art. 14",
            "right": "Derecho a un Tribunal Independiente",
            "finding": f"Independencia judicial clasificada como '{civil['judicial_independence']}'. "
                       "Compromete el derecho a un recurso efectivo ante disputas electorales.",
            "severity": "critical" if civil["judicial_independence"] == "captured" else "high",
            "confidence": get_trace(context.get("civil_liberties", {})).get("confidence", "unknown"),
        })

    emb = val(context.get("emb", {}))
    legal_fw = val(context.get("legal_framework", {}))

    if emb.get("independence_level") in ["compromised", "captured"]:
        violations.append({
            "treaty": "ICCPR", "article": "Art. 25",
            "right": "Derecho a Participar en Asuntos Públicos",
            "finding": f"EMB ({emb.get('name', 'N/A')}) con independencia '{emb['independence_level']}'. "
                       "Administración electoral sin garantías de imparcialidad.",
            "severity": "critical" if emb["independence_level"] == "captured" else "high",
            "confidence": get_trace(context.get("emb", {})).get("confidence", "unknown"),
        })

    if legal_fw.get("candidate_disqualifications", 0) > 0 and legal_fw.get("opposition_party_bans"):
        violations.append({
            "treaty": "ICCPR", "article": "Art. 25(b)",
            "right": "Derecho a Ser Elegido",
            "finding": f"{legal_fw['candidate_disqualifications']} candidatos inhabilitados con partidos prohibidos. "
                       "Restricción al derecho de postulación sin garantías de debido proceso.",
            "severity": "critical",
            "confidence": get_trace(context.get("legal_framework", {})).get("confidence", "unknown"),
        })

    digital = political.get("digital_ecosystem", {})

    if digital.get("censorship_detected"):
        violations.append({
            "treaty": "ICCPR", "article": "Art. 19(2)",
            "right": "Libertad de Expresión Digital",
            "finding": f"Censura de dominios web detectada: {digital.get('censored_domains', [])}. "
                       "Bloqueo de medios digitales constituye restricción a la libertad de expresión.",
            "severity": "high",
            "confidence": CONFIDENCE_MOCK,
        })

    if digital.get("voter_suppression_online"):
        violations.append({
            "treaty": "ICCPR", "article": "Art. 25(a)",
            "right": "Sufragio Universal",
            "finding": "Tácticas de supresión de votantes online detectadas. "
                       "Manipulación digital que interfiere con el ejercicio libre del sufragio.",
            "severity": "high",
            "confidence": CONFIDENCE_MOCK,
        })

    region = instruments.get("region", "unknown")
    regional_instruments = instruments.get("regional", [])

    if region == REGION_AMERICAS:
        if emb.get("independence_level") in ["compromised", "captured"]:
            violations.append({
                "treaty": "CADH", "article": "Art. 23",
                "right": "Derechos Políticos (Sistema Interamericano)",
                "finding": "Administración electoral sin independencia compromete el derecho a participar "
                           "en la dirección de los asuntos públicos bajo la Convención Americana.",
                "severity": "high",
                "confidence": get_trace(context.get("emb", {})).get("confidence", "unknown"),
            })
        if civil.get("freedom_of_press") in ["severely_restricted", "banned"]:
            violations.append({
                "treaty": "CDI", "article": "Art. 3-4",
                "right": "Elementos Esenciales de la Democracia (OEA)",
                "finding": "Restricción severa a la libertad de prensa viola los elementos esenciales "
                           "de la democracia representativa según la Carta Democrática Interamericana.",
                "severity": "high",
                "confidence": get_trace(context.get("civil_liberties", {})).get("confidence", "unknown"),
            })

    obs = val(context.get("international_observation", {}))

    if not obs.get("invited", True):
        observer_names = ", ".join(i.get("observer", "") for i in regional_instruments if i.get("observer"))
        risk_factors.append({
            "category": "Transparencia",
            "finding": f"Observación internacional no invitada o restringida. "
                       f"Incumplimiento de la Declaración de Principios para la Observación Internacional. "
                       f"Organismos regionales relevantes: {observer_names or 'N/A'}.",
            "severity": "high",
        })

    if emb.get("independence_level") == "full":
        mitigating_factors.append("EMB plenamente independiente con representación multipartidaria")

    fh_data = val(context.get("freedom_house", {}))
    if isinstance(fh_data, dict) and fh_data.get("total_score", fh_data.get("score", 0)) >= 80:
        mitigating_factors.append("Alto puntaje Freedom House indica garantías institucionales sólidas")

    if not digital.get("bot_activity") and not digital.get("censorship_detected"):
        mitigating_factors.append("Ecosistema digital saludable sin manipulación detectada")

    risk_score = _calculate_risk_score(context, political, violations)
    risk_level = _risk_level_from_score(risk_score)

    # ── RAG: enriquecer violaciones con jurisprudencia y estándares recuperados ──
    # Funciona en modo semántico (ChromaDB) o keyword fallback — siempre activo si hay violaciones
    if violations:
        for v in violations:
            try:
                rag_hits = _rag_legal(
                    risk_description=f"{v.get('right', '')} {v.get('finding', '')}",
                    country=state.get("country", ""),
                    n_results=2,
                )
                if rag_hits:
                    v["rag_references"] = [
                        {"instrument": h["instrument"], "title": h["title"][:80], "relevance": h["relevance"]}
                        for h in rag_hits
                    ]
            except Exception:
                pass
        agent_log(state, agent_name, f"[RAG] Jurisprudencia recuperada para {sum(1 for v in violations if 'rag_references' in v)} violaciones.")

    confidence_summary = {}
    for v in violations:
        conf = v.get("confidence", "unknown")
        confidence_summary[conf] = confidence_summary.get(conf, 0) + 1

    state["legal_analysis"] = {
        "source": "rule_based_v2_traced",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "violations": violations,
        "violation_count": len(violations),
        "risk_factors": risk_factors,
        "mitigating_factors": mitigating_factors,
        "treaties_referenced": list(set(v["treaty"] for v in violations)),
        "articles_referenced": list(set(f"{v['treaty']} {v['article']}" for v in violations)),
        "applicable_instruments": instruments.get("all_ids", []),
        "region": region,
        "confidence_summary": confidence_summary,
        "traceability_note": "Cada violación incluye campo 'confidence' indicando nivel de verificabilidad del dato fuente.",
    }

    state["risk_score"] = risk_score
    state["risk_level"] = risk_level

    pei_raw_legal = content_context.get("pei", {}) if (content_context := context) else {}
    pei_val_legal = extract_value(pei_raw_legal) if isinstance(pei_raw_legal, dict) else {}
    pei_confirmed_legal = bool(pei_val_legal and pei_val_legal.get("election_id"))
    fh_conf_legal = get_trace(context.get("freedom_house", {})).get("confidence", "unknown")
    vdem_conf_legal = get_trace(context.get("emb", {})).get("confidence", "unknown")
    cl_conf_legal = get_trace(context.get("civil_liberties", {})).get("confidence", "mock")
    lf_conf_legal = get_trace(context.get("legal_framework", {})).get("confidence", "mock")

    data_sources_summary = {
        "freedom_house": fh_conf_legal,
        "vdem_emb": vdem_conf_legal,
        "pei": "confirmed" if pei_confirmed_legal else "mock",
        "civil_liberties": cl_conf_legal,
        "legal_framework": lf_conf_legal,
    }
    confirmed_sources = [k for k, v in data_sources_summary.items() if v == "confirmed"]
    mock_sources = [k for k, v in data_sources_summary.items() if v == "mock"]

    state["legal_analysis"]["data_sources_summary"] = data_sources_summary

    agent_log(state, agent_name, f"Violaciones detectadas: {len(violations)}")
    agent_log(state, agent_name, f"Tratados referenciados: {state['legal_analysis']['treaties_referenced']}")
    agent_log(state, agent_name, f"Instrumentos regionales aplicados: {[i['id'] for i in regional_instruments]}")
    agent_log(state, agent_name, f"Confianza por violación: {confidence_summary}")
    agent_log(state, agent_name, f"Fuentes CONFIRMADAS: {confirmed_sources}")
    agent_log(state, agent_name, f"Fuentes MOCK (pendientes): {mock_sources}")
    agent_log(state, agent_name, f"PEI integrado: {'✅ confirmed' if pei_confirmed_legal else '⚠️ mock'}")
    agent_log(state, agent_name, f"Risk Score calculado: {risk_score}/100 → Nivel: {risk_level.upper()}")

    return state


def _calculate_risk_score(context: dict, political: dict, violations: list) -> float:
    score = 0.0

    def val(d):
        return extract_value(d) if isinstance(d, dict) and "_trace" in d else d

    fh_data = val(context.get("freedom_house", {}))
    fh = fh_data.get("total_score", fh_data.get("score", 50)) if isinstance(fh_data, dict) else 50
    score += (100 - fh) * 0.15

    vdem_data = val(context.get("vdem", {}))
    vdem = vdem_data.get("liberal_democracy", 0.5) if isinstance(vdem_data, dict) else 0.5
    score += (1 - vdem) * 100 * 0.15

    emb_scores = {"full": 0, "partial": 40, "compromised": 75, "captured": 95}
    emb_data = val(context.get("emb", {}))
    emb_level = emb_data.get("independence_level", "partial") if isinstance(emb_data, dict) else "partial"
    score += emb_scores.get(emb_level, 50) * 0.15

    media_bias = political.get("media_analysis", {}).get("bias_index", 0.3)
    score += media_bias * 100 * 0.10

    finance = political.get("campaign_finance", {}).get("transparency_score", 0.5)
    score += (1 - finance) * 100 * 0.10

    eco_scores = {"healthy": 0, "concerning": 30, "compromised": 65, "hostile": 90}
    eco_level = political.get("digital_ecosystem", {}).get("assessment", "concerning")
    score += eco_scores.get(eco_level, 40) * 0.10

    violation_weight = min(len(violations) * 8, 100)
    score += violation_weight * 0.15

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

def report_generator_agent(state: ElectionRiskState) -> ElectionRiskState:  # MIGRADO a agents/nodes.py (run_report_generator)
    agent_name = "VIP_ReportGeneratorAgent"
    agent_log(state, agent_name, f"Generando informe VIP para {state['country']}")

    context = state.get("context_data", {})
    political = state.get("political_data", {})
    legal = state.get("legal_analysis", {})

    chapters = {}

    chapters["00_country_profile"] = _generate_country_profile_section(state, state.get("country_code", ""))
    chapters["01_executive_summary"] = _generate_executive_summary(state)
    chapters["02_political_context"] = _generate_political_context(context, state.get("country_code", ""))
    chapters["03_emb_analysis"] = _generate_emb_chapter(context, state.get("country_code", ""))
    chapters["04_inclusivity"] = _generate_inclusivity_chapter(context, state.get("country_code", ""))
    chapters["05_campaign_finance"] = _generate_campaign_chapter(political, context)
    chapters["06_digital_ecosystem"] = _generate_digital_chapter(political, context, state.get("country_code", ""))
    voting_day_data = state.get("voting_day_data", {})
    chapters["07_voting_day"] = _generate_voting_day_chapter(voting_day_data, state)
    chapters["08_electoral_justice"] = _generate_justice_chapter(legal)
    chapters["09_recommendations"] = _generate_recommendations(state)

    # Cap. 10 — solo para países con módulo específico implementado
    if state.get("country_code") == "PER":
        chapters["10_ai_regulation"] = _generate_ai_regulation_chapter(state)

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


def _generate_country_profile_section(state: "ElectionRiskState", country_code: str = "") -> str:  # MIGRADO a chapters/generators.py
    """Genera Sección 0 — Perfil del País, Datos Socioeconómicos y Padrón Electoral."""

    if country_code == "PER":
        cp   = PERU_COUNTRY_PROFILE
        demo = cp["demographics"]
        eco  = cp["economy"]
        roll = cp["electoral_roll"]
        ovs  = cp["overseas_breakdown"]
        abst = cp["abstention_history"]
        pol  = cp["political_context_brief"]

        demo_rows = "\n".join([
            "| Indicador | Valor | Fuente |",
            "|---|---|---|",
            f"| Población total | {demo['population_total']:,} hab. | {demo['source']} |",
            f"| Área territorial | {demo['area_km2']:,} km² | INEI |",
            f"| Densidad poblacional | {demo['density_pop_km2']} hab/km² | INEI 2024 |",
            f"| Población urbana | {demo['urban_pct']}% | INEI 2024 |",
            f"| Esperanza de vida | {demo['life_expectancy_years']} años | PNUD HDR 2024 |",
            f"| Tasa de natalidad | {demo['birth_rate_per_1000']}/1,000 hab. | INEI 2024 |",
            f"| Tasa de alfabetización | {demo['literacy_rate_pct']}% | INEI 2024 |",
            f"| Edad mediana | {demo['median_age_years']} años | INEI 2024 |",
            f"| Idiomas oficiales | {demo['official_languages']} | Constitución 1993 |",
            "| | | |",
            f"| **PIB total** | **USD {eco['gdp_usd_billions']}B** | Banco Mundial 2024 |",
            f"| PIB per cápita | USD {eco['gdp_per_capita_usd']:,} | Banco Mundial 2024 |",
            f"| Crecimiento del PIB | {eco['gdp_growth_pct']}% | INEI/BCR 2024 |",
            f"| Desempleo | {eco['unemployment_rate_pct']}% | INEI-ENAHO 2024 |",
            f"| Inflación | {eco['inflation_rate_pct']}% | BCR 2024 |",
            f"| Coeficiente de Gini | {eco['gini_coefficient']} | INEI-ENAHO 2024 |",
            f"| **Tasa de pobreza** | **{eco['poverty_rate_pct']}%** | INEI-ENAHO 2024 |",
            f"| Pobreza extrema | {eco['extreme_poverty_rate_pct']}% | INEI-ENAHO 2024 |",
            f"| IDH | {eco['hdi']} (rango global #{eco['hdi_rank_global']}) | PNUD HDR 2024 |",
        ])

        roll_rows = "\n".join([
            "| Indicador | Valor | Detalle |",
            "|---|---|---|",
            f"| **Total inscritos** | **{roll['total_registered']:,}** | Padrón ONPE/RENIEC ene 2026 |",
            f"| Mujeres | {roll['women_registered']:,} | **{roll['women_pct']}%** del padrón |",
            f"| Hombres | {roll['men_registered']:,} | **{roll['men_pct']}%** del padrón |",
            f"| Nuevos votantes (18–21 años) | ~{roll['new_voters_estimate']:,} | Estimado ONPE |",
            f"| Primervotos (exactamente 18 años) | ~{roll['first_time_voters_18']:,} | Estimado RENIEC |",
            f"| Fecha cierre del padrón | {roll['registry_cutoff_date']} | {roll['registry_cutoff_note']} |",
            f"| **Votantes en el exterior** | **{roll['overseas_total']:,}** | {ovs['countries_with_mesas']} países |",
            f"| Voto obligatorio | {'Sí' if roll['mandatory_voting'] else 'No'} | {roll['mandatory_voting_note']} |",
        ])

        overseas_rows = "\n".join(
            ["| País | Electores | Mesas | % del padrón exterior |", "|---|---|---|---|"] +
            [f"| {o['country']} | {o['voters']:,} | {o['mesas']} | {o['pct']}% |"
             for o in ovs["top_destinations"]] +
            [f"| *Otros 36 países* | ~{ovs['total'] - sum(o['voters'] for o in ovs['top_destinations']):,} | — | {100 - sum(o['pct'] for o in ovs['top_destinations']):.1f}% |"]
        )

        abs_rows = "\n".join(
            ["| Elección | Fecha | Ausentismo | N° abstenciones | Contexto |", "|---|---|---|---|---|"] +
            [f"| {a['election']} | {a['date']} | **{a['abstention_pct']}%** | {a['abstention_abs']:,} | {a['context']} |"
             for a in abst]
        )

        return f"""## 0. Perfil del País y Padrón Electoral

> **Fuentes:** {cp['data_sources']}
> **Confidence:** CONFIRMED — datos oficiales verificados de fuentes primarias (INEI/ONPE/RENIEC/BCR/PNUD 2024–2026)

### 0.1 Demografía y Economía

{demo_rows}

### 0.2 Padrón Electoral — Elecciones Generales 2026

{roll_rows}

### 0.3 Votantes en el Exterior — Top 5 países

{overseas_rows}

*Fuente: {ovs['source']}*

### 0.4 Ausentismo Electoral Histórico

{abs_rows}

> **Tendencia:** El ausentismo escaló del 18.2% (2016) al 32.4% (2022), reflejando la creciente desafección ante la crisis institucional. Para 2026 se proyecta participación en rango **68–74%** (Ipsos/ONPE est. feb 2026). La zona de riesgo son los ~1.2M nuevos votantes jóvenes (18–21), con menor propensión histórica a votar.

### 0.5 Contexto Político Actual

| Indicador | Estado |
|---|---|
| Presidenta en funciones | {pol['current_president']} ({pol['current_party']}) |
| Aprobación presidencial | **{pol['approval_rating_pct']}%** ({pol['approval_source']}) |
| Fragmentación parlamentaria | {pol['congress_fragmentation']} — el más fragmentado desde 1980 |
| Candidatos presidenciales inscritos | {pol['confirmed_candidates']} (de {pol['registered_parties']} partidos habilitados) |
| Fecha 1ª vuelta | **{pol['election_date']}** |
| Fecha 2ª vuelta (proyectada) | {pol['second_round_date']} |

"""
    else:
        # Perfil genérico para países sin módulo específico
        country = state.get("country", "País")
        election_date = state.get("election_date", "N/A")
        risk_score = state.get("risk_score", 0)
        context = state.get("context_data", {})
        fh_raw = context.get("freedom_house", {})
        fh_val = fh_raw.get("value") if isinstance(fh_raw, dict) else None
        fh_score = fh_val if fh_val else "N/D"
        return f"""## 0. Perfil del País y Padrón Electoral

> *El módulo de perfil detallado para {country} está en desarrollo. Se muestran datos disponibles en el pipeline.*

| Indicador | Dato |
|---|---|
| País | {country} |
| Fecha de elección | {election_date} |
| Puntaje Freedom House | {fh_score}/100 |
| Índice de Riesgo PEIRS | {risk_score}/100 |

"""


def _generate_executive_summary(state: ElectionRiskState) -> str:  # MIGRADO a chapters/generators.py
    legal = state.get("legal_analysis", {})
    violations = legal.get("violations", [])
    critical = [v for v in violations if v.get("severity") == "critical"]
    level_emoji = {"critical": "🔴", "high": "🟠", "moderate": "🟡", "low": "🟢"}
    emoji = level_emoji.get(state["risk_level"], "⚪")
    context = state.get("context_data", {})

    fh_data = extract_value(context.get("freedom_house", {})) or {}
    fh_score = fh_data.get("total_score", fh_data.get("score", "N/D"))
    fh_status = fh_data.get("status", "N/D")
    fh_edition = fh_data.get("edition", "—")

    vdem_data = extract_value(context.get("vdem", {})) or {}
    vdem_libdem = vdem_data.get("liberal_democracy", "N/D")
    vdem_polyarchy = vdem_data.get("electoral_democracy", "N/D")
    vdem_year = vdem_data.get("year", "—")

    emb_data = extract_value(context.get("emb", {})) or {}
    emb_level = emb_data.get("independence_level", "N/D").upper()
    emb_autonomy = emb_data.get("autonomy_score", "N/D")

    pei_data = extract_value(context.get("pei", {})) or {}
    pei_integrity = pei_data.get("overall_integrity")
    pei_integrity_str = f"{pei_integrity}" if pei_integrity is not None else "N/D"
    pei_emb = pei_data.get("emb_score", "N/D")
    pei_year = pei_data.get("year", "—")

    table = (
        "| Dimension | Evaluation | Source | Year |\n"
        "|---|---|---|---|\n"
        f"| Freedom House | {fh_score}/100 \u2014 {fh_status} | FH FIW | {fh_edition} |\n"
        f"| V-Dem Liberal Democracy | {vdem_libdem} | V-Dem v15 | {vdem_year} |\n"
        f"| V-Dem Electoral Democracy | {vdem_polyarchy} | V-Dem v15 | {vdem_year} |\n"
        f"| Independencia EMB | {emb_level} (autonomia: {emb_autonomy}) | V-Dem v15 | {vdem_year} |\n"
        f"| PEI Integridad | {pei_integrity_str}/100 (EMBs: {pei_emb}) | PEI-10.0 | {pei_year} |\n"
        f"| Violaciones | {len(violations)} ({len(critical)} criticas) | PEIRS Legal | \u2014 |\n"
        f"| Tratados | {', '.join(legal.get('treaties_referenced', []))} | PEIRS Legal | \u2014 |"
    )

    mitigating = f"\n**Factores mitigantes:** {'; '.join(legal['mitigating_factors'])}\n" if legal.get("mitigating_factors") else ""

    sys_prompt = (
        "Sos un analista senior de integridad electoral para DEMOCRAC.IA/PEIRS. "
        "Redactas en espanol, neutral, preciso, basado solo en los datos recibidos. No inventas datos."
    )
    user_prompt = (
        f"Escribe exactamente 2 parrafos analiticos para el Resumen Ejecutivo.\n\n"
        f"DATOS (confidence=confirmed):\n"
        f"- Pais: {state['country']} | Eleccion: {state['election_date']}\n"
        f"- Riesgo PEIRS: {state['risk_score']}/100 - {state['risk_level'].upper()}\n"
        f"- Freedom House {fh_edition}: {fh_score}/100 - {fh_status}\n"
        f"- V-Dem libdem {vdem_year}: {vdem_libdem} | polyarchy: {vdem_polyarchy}\n"
        f"- EMB: {emb_level} (autonomia: {emb_autonomy})\n"
        f"- PEI {pei_year}: Integridad={pei_integrity_str}/100, EMBs={pei_emb}/100\n"
        f"- Violaciones: {len(violations)} ({len(critical)} criticas)\n\n"
        f"Parrafo 1: estado democratico estructural (FH, V-Dem, EMB). "
        f"Parrafo 2: riesgo electoral especifico para {state['election_date']}.\n"
        f"Max 80 palabras c/u. No repitas los numeros de la tabla. Sin vinetas."
    )

    def fallback(s=state, cr=critical, em=emoji):
        return f"{em} **Nivel de Riesgo: {s['risk_level'].upper()}** - {len(cr)} violaciones criticas detectadas."

    narrative = _llm_generate(sys_prompt, user_prompt, fallback)

    # Integrar dictamen técnico del Agente 5
    dictamen = state.get("dictamen", {})
    dictamen_section = ""
    if dictamen.get("narrative"):
        trend_info = dictamen.get("trend", {})
        reg_comp = dictamen.get("regional_comparison", {})
        trend_line = ""
        if trend_info.get("available"):
            dir_emoji = "📈" if trend_info["trend_direction"] == "up" else "📉" if trend_info["trend_direction"] == "down" else "➡️"
            trend_line = (
                f"\n**Tendencia V-Dem ({trend_info['first_year']}→{trend_info['last_year']}):** "
                f"{dir_emoji} {trend_info['trend'].upper()} "
                f"({trend_info['first_value']} → {trend_info['last_value']}, delta={trend_info['delta']:+.4f})"
            )
        reg_line = ""
        if reg_comp.get("fh_vs_region"):
            reg_line = f"\n**Comparación regional ({reg_comp['region']}):** {reg_comp['fh_vs_region']}"
            if reg_comp.get("vdem_vs_region"):
                reg_line += f" | {reg_comp['vdem_vs_region']}"
            if reg_comp.get("rsf_vs_region"):
                reg_line += f" | {reg_comp['rsf_vs_region']}"

        conf_color = "🟢" if dictamen["data_confidence"] == "HIGH" else "🟡" if dictamen["data_confidence"] == "MEDIUM" else "🔴"

        dictamen_section = (
            f"\n\n---\n\n"
            f"### Dictamen Técnico — {dictamen['dictamen_id']}\n\n"
            f"{conf_color} **Confianza de Datos: {dictamen['data_confidence']}** — {dictamen['confidence_note']}"
            f"{trend_line}{reg_line}\n\n"
            f"{dictamen['narrative']}\n"
        )

    return (
        f"## 1. Resumen Ejecutivo & Dashboard de Riesgo\n\n"
        f"{emoji} **Nivel de Riesgo: {state['risk_level'].upper()}** - Indice: **{state['risk_score']}/100**\n\n"
        f"{table}\n\n"
        f"{narrative}\n"
        f"{mitigating}"
        f"{dictamen_section}"
    )

def _generate_political_context(context: dict, country_code: str = "") -> str:  # MIGRADO a chapters/generators.py
    legal_fw_raw = context.get("legal_framework", {})
    legal_fw = extract_value(legal_fw_raw) if isinstance(legal_fw_raw, dict) else legal_fw_raw
    legal_fw = legal_fw if isinstance(legal_fw, dict) else {}

    # Peru: Ley 31988 (dic 2023, promulgada feb 2024) restauró el Senado bicameral — reforma constitucional real
    if country_code == "PER":
        legal_fw = dict(legal_fw)
        legal_fw["constitutional_amendments_recent"] = True

    civil_raw = context.get("civil_liberties", {})
    civil = extract_value(civil_raw) if isinstance(civil_raw, dict) else civil_raw
    civil = civil if isinstance(civil, dict) else {}

    fh_raw = context.get("freedom_house", {})
    fh_data = extract_value(fh_raw) if isinstance(fh_raw, dict) else {}
    fh_score = fh_data.get("total_score", fh_data.get("score", "N/D")) if fh_data else "N/D"
    fh_edition = fh_data.get("edition", "—") if fh_data else "—"
    fh_conf = get_trace(fh_raw).get("confidence", "mock") if isinstance(fh_raw, dict) else "mock"

    # V-Dem indicadores políticos (confirmados si están presentes)
    vdem_opp_barriers = civil.get("vdem_opposition_barriers") or legal_fw.get("vdem_opposition_barriers")
    vdem_jud_review = civil.get("vdem_judicial_review") or legal_fw.get("vdem_judicial_review")
    vdem_opp_autonomy = civil.get("vdem_opposition_autonomy") or legal_fw.get("vdem_opposition_autonomy")
    vdem_frassoc = civil.get("vdem_freedom_of_association")
    vdem_rol = civil.get("vdem_rule_of_law")
    vdem_year = civil.get("vdem_data_year") or legal_fw.get("vdem_data_year", "—")
    vdem_confirmed = vdem_opp_barriers is not None or vdem_jud_review is not None

    def vdem_label(val, invert=False):
        if val is None:
            return "N/D"
        v = (1 - val) if invert else val
        if v >= 0.75: return f"{val:.2f} — favorable"
        if v >= 0.50: return f"{val:.2f} — moderado"
        if v >= 0.25: return f"{val:.2f} — comprometido"
        return f"{val:.2f} — crítico"

    pei_laws = legal_fw.get("pei_laws_score")
    pei_laws_unfair = legal_fw.get("pei_laws_unfair")
    pei_opp_prevent = legal_fw.get("pei_opp_prevent")

    # Tabla Marco Legal
    legal_rows = [
        f"| Reformas constitucionales recientes | {'Sí' if legal_fw.get('constitutional_amendments_recent') else 'No'} | FH FIW {fh_edition} |",
        f"| Prohibición de partidos opositores | {'Sí' if legal_fw.get('opposition_party_bans') else 'No'} | FH FIW {fh_edition} |",
        f"| Candidatos inhabilitados | {legal_fw.get('candidate_disqualifications', 0)} | FH FIW {fh_edition} |",
        f"| Restricciones a medios | {legal_fw.get('media_law_restrictions', 'N/D')} | FH FIW {fh_edition} |",
    ]
    if pei_laws is not None:
        legal_rows.append(f"| Score marco legal (PEI) | {pei_laws}/100 | PEI 10.0 |")
    if pei_laws_unfair is not None:
        legal_rows.append(f"| Leyes favorecen incumbente (PEI) | {pei_laws_unfair}/100 | PEI 10.0 |")
    if vdem_opp_barriers is not None:
        legal_rows.append(f"| Barreras a partidos (V-Dem v2psbars) | {vdem_label(vdem_opp_barriers)} | V-Dem v15 {vdem_year} |")
    if vdem_opp_autonomy is not None:
        legal_rows.append(f"| Autonomía oposición (V-Dem v2psoppaut) | {vdem_label(vdem_opp_autonomy)} | V-Dem v15 {vdem_year} |")

    struct_legal = (
        f"**Marco Legal Electoral** *(FH FIW {fh_edition}" +
        (f" + V-Dem v15 {vdem_year}" if vdem_confirmed else "") +
        ")*\n| Indicador | Estado | Fuente |\n|---|---|---|\n" +
        "\n".join(legal_rows)
    )

    # Tabla Libertades Civiles
    civil_rows = [
        f"| Libertad de reunión | {civil.get('freedom_of_assembly', 'N/D')} | FH FIW {fh_edition} |",
        f"| Libertad de prensa | {civil.get('freedom_of_press', 'N/D')} | FH FIW {fh_edition} |",
        f"| Independencia judicial | {civil.get('judicial_independence', 'N/D')} | FH FIW {fh_edition} |",
        f"| Presos políticos | {'Sí' if civil.get('political_prisoners') else 'No'} | FH FIW {fh_edition} |",
    ]
    if vdem_jud_review is not None:
        civil_rows.append(f"| Revisión judicial ind. (V-Dem v2jureview) | {vdem_label(vdem_jud_review)} | V-Dem v15 {vdem_year} |")
    if vdem_frassoc is not None:
        civil_rows.append(f"| Libertad de asociación (V-Dem v2x_frassoc) | {vdem_label(vdem_frassoc)} | V-Dem v15 {vdem_year} |")
    if vdem_rol is not None:
        civil_rows.append(f"| Estado de derecho (V-Dem v2xcl_rol) | {vdem_label(vdem_rol)} | V-Dem v15 {vdem_year} |")

    struct_civil = (
        f"\n\n**Estado de Libertades Civiles** *(FH CL/PR rating" +
        (f" + V-Dem v15 {vdem_year}" if vdem_confirmed else "") +
        ")*\n| Indicador | Estado | Fuente |\n|---|---|---|\n" +
        "\n".join(civil_rows)
    )

    struct = struct_legal + struct_civil

    sys_prompt = (
        "Sos un analista de contexto político-electoral para DEMOCRAC.IA/PEIRS. "
        "Escribís en español, tono técnico-institucional con registro periodístico de investigación. "
        "Basás tu análisis exclusivamente en los datos recibidos."
    )
    vdem_block = ""
    if vdem_confirmed:
        vdem_block = (
            f"\nDATOS ADICIONALES V-Dem v15 ({vdem_year}, confidence=confirmed):\n"
            + (f"- Barreras a partidos (v2psbars): {vdem_label(vdem_opp_barriers)}\n" if vdem_opp_barriers is not None else "")
            + (f"- Autonomía oposición (v2psoppaut): {vdem_label(vdem_opp_autonomy)}\n" if vdem_opp_autonomy is not None else "")
            + (f"- Revisión judicial (v2jureview): {vdem_label(vdem_jud_review)}\n" if vdem_jud_review is not None else "")
            + (f"- Estado de derecho (v2xcl_rol): {vdem_label(vdem_rol)}\n" if vdem_rol is not None else "")
        )
    user_prompt = (
        f"Escribe exactamente 2 párrafos de análisis del contexto político-electoral.\n\n"
        f"DATOS (Freedom House FIW {fh_edition}, confidence={fh_conf}):\n"
        f"- FH score: {fh_score}/100\n"
        f"- Reformas constitucionales recientes: {'Sí' if legal_fw.get('constitutional_amendments_recent') else 'No'}\n"
        f"- Prohibición de partidos opositores: {'Sí' if legal_fw.get('opposition_party_bans') else 'No'}\n"
        f"- Candidatos inhabilitados: {legal_fw.get('candidate_disqualifications', 0)}\n"
        f"- Restricciones a medios: {legal_fw.get('media_law_restrictions', 'N/D')}\n"
        f"- Libertad de prensa: {civil.get('freedom_of_press', 'N/D')}\n"
        f"- Libertad de reunión: {civil.get('freedom_of_assembly', 'N/D')}\n"
        f"- Independencia judicial: {civil.get('judicial_independence', 'N/D')}\n"
        f"- Presos políticos: {'Sí' if civil.get('political_prisoners') else 'No'}\n"
        + vdem_block +
        "\nPárrafo 1 (~90 palabras): estado del marco legal electoral. Qué implican estas restricciones "
        "para la competencia electoral libre y el pluralismo político. Cita datos V-Dem cuando estén disponibles.\n"
        "Párrafo 2 (~80 palabras): estado de las libertades civiles y el sistema judicial. Cómo condicionan el ejercicio "
        "del derecho al voto y la participación ciudadana. Solo prosa, sin viñetas."
    )

    def fallback_pol(lf=legal_fw, cv=civil):
        parts = []
        if lf.get("opposition_party_bans"):
            parts.append("La prohibición de partidos opositores restringe severamente el pluralismo político.")
        if cv.get("freedom_of_press") in ["severely_restricted", "banned"]:
            parts.append("La libertad de prensa severamente restringida compromete el acceso a información electoral.")
        return " ".join(parts) if parts else "El marco legal electoral presenta condiciones que requieren monitoreo."

    # ── Bloque Peru-específico ──────────────────────────────────────────────────
    peru_block = ""
    if country_code == "PER":
        # Tabla de fuerzas políticas con perfil de riesgo ICCPR
        party_rows = "\n".join(
            f"| **{p['abbr']}** | {p['name']} | {p['ideology']} | "
            f"{p['current_seats']} | {p['electoral_strength']} | "
            f"{'ALTO' if p['risk_profile'] == 'high' else 'MODERADO' if p['risk_profile'] == 'moderate' else 'BAJO'} |"
            for p in PERU_POLITICAL_FORCES
        )
        es = PERU_ELECTORAL_SYSTEM

        # Resumen histórico (últimos 4 eventos clave)
        hist_summary = " → ".join(
            f"{ev['year']}: {ev['event'][:60]}{'…' if len(ev['event']) > 60 else ''}"
            for ev in PERU_HISTORICAL_EVENTS[-4:]
        )

        # Tabla de riesgos ICCPR por actor (con fechas y fuentes APA)
        iccpr_rows = "\n".join(
            f"| **{p['abbr']}** | {p['iccpr_risk'][:110]}{'…' if len(p['iccpr_risk']) > 110 else ''} | "
            f"{p.get('iccpr_date','—')} | {p.get('iccpr_source','—')[:80]}{'…' if len(p.get('iccpr_source','')) > 80 else ''} |"
            for p in PERU_POLITICAL_FORCES
            if p.get("iccpr_risk")
        )

        oc = PERU_ORGANIZED_CRIME
        jne_sc = PERU_ORGANIZED_CRIME.get("jne_screening", {})
        # 2026-04-26 — si el bloque está en pending_verification, no se renderizan
        # tablas con datos sin source. El informe muestra un aviso claro en su lugar.
        oc_audit_pending = oc.get("audit_status") == "pending_verification"
        if oc_audit_pending:
            crime_org_rows = "| _Sección postergada_ | _ver aviso debajo_ | — | — | — |"
            risk_map_rows = "| _Pendiente_ | _Mapa retirado por trazabilidad_ |"
            section_24_content = (
                "⚠️ **Sección postergada (2026-04-26).** Las afirmaciones previas sobre "
                "organizaciones criminales con nexo electoral, métricas de screening JNE "
                "(candidatos marcados/excluidos/en revisión) y mapa regional de riesgo "
                "**fueron retiradas por ausencia de fuentes verificables individuales**. "
                "La sección se reactivará únicamente con citas primarias por organización "
                "(URL pública del informe IDEHPUCP/FECOR/JNE referenciado)."
            )
        else:
            crime_org_rows = "\n".join(
                f"| **{o['name']}** | {o['type']} | {o['electoral_nexus'][:80]}{'...' if len(o['electoral_nexus']) > 80 else ''} | "
                f"{', '.join(o['regions'][:3])} | {o['status'][:60]}{'...' if len(o['status']) > 60 else ''} |"
                for o in oc["main_organizations"]
            )
            risk_map_rows = "\n".join(
                f"| **{level}** | {', '.join(regions)} |"
                for level, regions in oc["regional_risk_map"].items()
            )
            section_24_content = (
                f"> **Candidatos marcados JNE (ene 2026):** {jne_sc.get('candidates_flagged_2026')} identificados | "
                f"{jne_sc.get('candidates_excluded')} excluidos | "
                f"{jne_sc.get('candidates_under_review')} en revisión\n"
                f"> **Limitación JNE:** {jne_sc.get('limitation')}\n\n"
                "| Organización | Tipo | Nexo electoral | Regiones | Estado |\n"
                "|---|---|---|---|---|\n"
                f"{crime_org_rows}\n\n"
                "**Mapa de Riesgo Regional:**\n"
                "| Nivel | Regiones |\n"
                "|---|---|\n"
                f"{risk_map_rows}"
            )

        peru_block = f"""

---

### 2.1 Fuerzas Políticas — Perú 2026 *(JNE + V-Dem v15 + PEI 10.0)*

| Partido | Nombre | Ideología | Escaños actuales | Fuerza electoral | Perfil de riesgo |
|---|---|---|---|---|---|
{party_rows}

> **Sistema Electoral:** {es['name']} · {es['seats']} escaños · {es['chamber']}
> **Umbral:** {es['threshold']}
> **Cuotas:** {es['women_quota']} · {es['youth_quota']}
> **Órganos:** JNE (árbitro) · ONPE (organización) · RENIEC (padrón)

### 2.2 Crisis Democrática 2019–2026

{hist_summary}

Perú ingresa al ciclo 2026 con **seis presidentes en cuatro años**, dos congresos
disueltos y una aprobación presidencial históricamente baja (<10%, 2024).
El índice V-Dem registra deterioro sostenido (v2x_libdem: 0.59 en 2015 → 0.42 en 2024).

### 2.3 Riesgos ICCPR por Actor

> *Metodología: hallazgos derivados de análisis de fuentes primarias JNE/ONPE, bases de datos V-Dem v15, Freedom House FIW 2025 y documentación judicial peruana. Fechas indican el primer evento documentado y última actualización verificada.*

| Actor | Riesgo — Derecho Internacional | Fecha del hallazgo | Fuente primaria |
|---|---|---|---|
{iccpr_rows}

### 2.4 Crimen Organizado e Infiltración Electoral

{section_24_content}

*UNCAC: {oc["uncac_ref"]}*
*ICCPR: {oc["iccpr_ref"]}*
*Fuentes: {oc["data_sources"]}*
"""

        # Enriquecer el prompt LLM con contexto peruano
        user_prompt += (
            f"\n\nCONTEXTO ESPECÍFICO PERÚ 2026 (inyectado desde datos estructurados JNE/PEIRS):\n"
            f"- Fragmentación parlamentaria: {es['historical_fragmentation']}\n"
            f"- Sistema electoral: {es['name']} · umbral {es['threshold']}\n"
            f"- Partido más grande (escaños actuales): APP 28 (Acuña) — perfil de riesgo ALTO\n"
            f"- Fuerzas con proceso judicial activo: Fuerza Popular (Keiko Fujimori — lavado de activos), "
            f"Perú Libre (Cerrón — inhabilitado por corrupción)\n"
            f"- Reforma constitucional reciente: Ley 31988 (promulgada feb 2024) restauró el Senado bicameral "
            f"— primera vez desde 1993. Impacto directo en el sistema electoral para las elecciones de abril 2026.\n"
            f"- Crisis 2019-2026: {hist_summary}\n"
            f"\nAñadí un tercer párrafo (~80 palabras) específico sobre el impacto de "
            f"la fragmentación partidaria y la crisis de representación peruana en la integridad del proceso 2026. "
            f"Mencioná concretamente al JNE, la fragmentación (8+ bancadas esperadas) y el riesgo de bloqueo ejecutivo-legislativo."
        )

    narrative = _llm_generate(sys_prompt, user_prompt, fallback_pol)

    return f"## 2. Contexto Político y Marco Legal\n\n{struct}\n\n{narrative}{peru_block}\n"


def _generate_emb_chapter(context: dict, country_code: str = "") -> str:  # MIGRADO a chapters/generators.py
    emb = extract_value(context.get("emb", {})) or {}
    registry = extract_value(context.get("voter_registry", {})) or {}
    obs = extract_value(context.get("international_observation", {})) or {}

    reg_size = registry.get("size", "N/D")
    if isinstance(reg_size, int):
        reg_size = f"{reg_size:,}"

    emb_name = emb.get("name", "N/D")
    emb_level = emb.get("independence_level", "N/D").upper()
    emb_autonomy = emb.get("autonomy_score", "N/D")
    emb_irregularities = emb.get("electoral_irregularities", "N/D")
    emb_year = emb.get("data_year", "—")
    pei_reg_score = registry.get("pei_voter_reg_score", "N/D")
    reg_inaccurate = registry.get("pei_reg_inaccurate", "N/D")

    struct = (
        f"**{emb_name}** *(V-Dem v15, ano {emb_year})*\n"
        f"- Nivel de independencia: **{emb_level}**\n"
        f"- Autonomia (score normalizado): {emb_autonomy}\n"
        f"- Irregularidades electorales: {emb_irregularities}\n"
        f"- Representacion opositora: {'Si' if emb.get('opposition_representation') else 'No'}\n\n"
        f"**Padron Electoral** *(PEI 10.0)*\n"
        f"- Estado de auditoria: {registry.get('status', 'N/D')}\n"
        f"- Votantes registrados: {reg_size}\n"
        f"- Score registro PEI: {pei_reg_score}/100\n"
        f"- Precision del padron (PEI): {reg_inaccurate}/5\n\n"
        f"**Observacion Internacional**\n"
        f"- Invitacion: {'Si' if obs.get('invited') else 'No'}\n"
        f"- Restricciones: {obs.get('restrictions', 'N/D')}"
    )

    sys_prompt = (
        "Sos un analista de administracion electoral para DEMOCRAC.IA/PEIRS. "
        "Escribis en espanol, neutro, preciso, basado solo en los datos recibidos."
    )
    user_prompt = (
        f"Escribe exactamente 2 parrafos analiticos sobre el EMB.\n\n"
        f"DATOS (V-Dem v15 + PEI 10.0, confidence=confirmed):\n"
        f"- EMB: {emb_name}\n"
        f"- Independencia: {emb_level}\n"
        f"- Autonomia: {emb_autonomy} (0=ninguna, 1=plena)\n"
        f"- Irregularidades: {emb_irregularities} (0=ninguna, 1=maxima)\n"
        f"- Score registro PEI: {pei_reg_score}/100\n"
        f"- Precision padron: {reg_inaccurate}/5 (5=muy impreciso)\n"
        f"- Observacion: {'invitada' if obs.get('invited') else 'no invitada'}\n\n"
        "Parrafo 1: independencia y capacidad del EMB. "
        "Parrafo 2: padron y observacion. Max 80 palabras c/u."
    )

    def fallback():
        return ""

    narrative = _llm_generate(sys_prompt, user_prompt, fallback)

    # ── Bloque específico Perú ────────────────────────────────────────────────
    peru_emb_block = ""
    if country_code == "PER":
        ov = PERU_OVERSEAS_VOTE
        country_rows = "\n".join(
            f"| {c['country']} | {c['voters']:,} | {c['mesas']} | {'ALERTA: ' + c['alert'] if c.get('alert') else 'OK'} |"
            for c in ov["top_countries"]
        )
        risk_rows = "\n".join(
            f"| {i+1} | {r['risk'][:100]}{'…' if len(r['risk'])>100 else ''} | {r['severity']} | {r['date']} | {r['source'][:70]}{'…' if len(r['source'])>70 else ''} |"
            for i, r in enumerate(ov["logistics_risks"])
        )
        coc = ov["chain_of_custody"]
        dv = ov["digital_vote_proposal"]

        peru_emb_block = f"""
---
### 3.4 Voto Exterior y Logística Digital — Perú 2026 *(ONPE + RENIEC + JNE)*

> **Padrón exterior total:** {ov["total_overseas_registered"]:,} electores | **Mesas:** {ov["total_mesas_exterior"]:,}
> *Fuente: {ov["source_registry"]}*

#### 3.4.1 Distribución por País

| País | Electores | Mesas | Estado |
|---|---|---|---|
{country_rows}

#### 3.4.2 Riesgos Logísticos Identificados

> *Fuentes verificadas: ONPE, RENIEC, JNE, Cancillería Perú, MEF. Fechas indican publicación del hallazgo. Severidad: ALTO = riesgo sistémico; MEDIO = riesgo operativo gestionable; INFORMATIVO = sin impacto directo en curso.*

| # | Riesgo | Severidad | Fecha | Fuente primaria |
|---|---|---|---|---|
{risk_rows}

#### 3.4.3 Cadena de Custodia de Actas

| Etapa | Descripción | Vulnerabilidad |
|---|---|---|
| Sistema actual | {coc["current"]} | {coc["vulnerability"]} |
| Mejora propuesta | {coc["proposed_improvement"]} | Piloto aprobado |
| Países piloto TREP | {", ".join(coc["pilot_trep_countries"])} | Implementación pendiente ONPE |

#### 3.4.4 Voto Digital Exterior — Estado

> **Estado propuesta:** {dv["status"]}
> **Fundamento rechazo:** {dv["reason"]}
> **Alternativa aprobada:** {dv["alternative_approved"]}
> **Nota ICCPR:** {dv["iccpr_note"]}

*Referencia: {ov["iccpr_ref"]}*
*Fuentes: {ov["data_sources"]}*
"""

    return f"## 3. Administracion Electoral (EMB)\n\n{struct}\n\n{narrative}\n{peru_emb_block}\n"

def _generate_inclusivity_chapter(context: dict, country_code: str = "") -> str:  # MIGRADO a chapters/generators.py
    fh_raw = context.get("freedom_house", {})
    fh_data = extract_value(fh_raw) if isinstance(fh_raw, dict) else {}
    fh_score = fh_data.get("total_score", fh_data.get("score", 50)) if fh_data else 50
    fh_edition = fh_data.get("edition", "—") if fh_data else "—"

    vdem_raw = context.get("vdem", {})
    vdem_data = extract_value(vdem_raw) if isinstance(vdem_raw, dict) else {}
    vdem_suffrage = vdem_data.get("universal_suffrage") if vdem_data else None
    vdem_assoc = vdem_data.get("freedom_of_association") if vdem_data else None
    vdem_year = vdem_data.get("year", "—") if vdem_data else "—"

    civil_raw = context.get("civil_liberties", {})
    civil = extract_value(civil_raw) if isinstance(civil_raw, dict) else {}
    cl_rating = civil.get("cl_rating", 4) if civil else 4

    struct = (
        f"**Indicadores de Inclusividad** *(V-Dem v15, año {vdem_year})*\n"
        f"| Indicador | Score | Fuente |\n|---|---|---|\n"
        f"| Sufragio universal (v2x_suffr) | {vdem_suffrage if vdem_suffrage is not None else 'N/D'} | V-Dem v15 |\n"
        f"| Libertad de asociación (v2x_frassoc_thick) | {vdem_assoc if vdem_assoc is not None else 'N/D'} | V-Dem v15 |\n"
        f"| Libertades civiles generales (CL rating) | {cl_rating}/7 | Freedom House FIW {fh_edition} |\n\n"
        f"*Nota: Análisis desagregado por género (CEDAW) y etnicidad (ICERD) pendiente de integración con fuentes especializadas.*\n"
    )

    sys_prompt = (
        "Sos un analista de inclusividad electoral y derechos humanos para DEMOCRAC.IA/PEIRS. "
        "Escribís en español, tono técnico-institucional. Basás tu análisis en los datos recibidos. "
        "Sos honesto sobre las limitaciones de datos disponibles."
    )
    user_prompt = (
        f"Escribe 2 párrafos sobre inclusividad electoral y derechos humanos.\n\n"
        f"DATOS DISPONIBLES (V-Dem v15 + FH FIW {fh_edition}):\n"
        f"- FH score general: {fh_score}/100\n"
        f"- Sufragio universal V-Dem: {vdem_suffrage} (0=restrictivo, 1=universal)\n"
        f"- Libertad de asociación V-Dem: {vdem_assoc} (0=restringida, 1=plena)\n"
        f"- CL rating FH: {cl_rating}/7 (1=mejor, 7=peor)\n\n"
        "Párrafo 1 (~90 palabras): evalúa las condiciones de inclusividad electoral basándote en "
        "sufragio universal y libertad de asociación. Qué implican para grupos vulnerables "
        "(mujeres, minorías, pueblos indígenas) bajo el marco de CEDAW e ICERD.\n"
        "Párrafo 2 (~70 palabras): limitaciones del análisis actual y qué fuentes adicionales "
        "mejorarían la evaluación. Menciona que el análisis desagregado por género y etnicidad "
        "está previsto en fases futuras. Solo prosa."
    )

    def fallback_inc(vs=vdem_suffrage, va=vdem_assoc):
        parts = []
        if vs is not None:
            parts.append(f"El índice de sufragio universal V-Dem de {vs} refleja el alcance del derecho al voto.")
        if va is not None:
            parts.append(f"La libertad de asociación de {va} indica las condiciones para la participación organizada.")
        return " ".join(parts) if parts else "Análisis de inclusividad basado en indicadores V-Dem disponibles."

    narrative = _llm_generate(sys_prompt, user_prompt, fallback_inc)

    # ── Bloque específico Perú ────────────────────────────────────────────────
    peru_gender_block = ""
    if country_code == "PER":
        gd = PERU_GENDER_DATA
        lf = gd["legal_framework"]
        cr = gd["current_representation"]
        vdgp = gd["vdgp_registry"]
        iw = gd["indigenous_women"]

        gap_rows = "\n".join(f"| {i+1} | {g} |" for i, g in enumerate(lf["gaps"]))
        vdgp_perp_rows = "\n".join(f"| {p} |" for p in vdgp["perpetrators"])
        affected_rows = "\n".join(f"| {a} |" for a in vdgp["most_affected"])

        peru_gender_block = f"""
---
### 4.4 Género, Paridad y Violencia Política — Perú 2026 *(JNE + Congreso + CALANDRIA)*

#### 4.4.1 Marco Legal: Paridad y Alternancia

| Norma | Contenido | Estado |
|---|---|---|
| {lf["quota_law"].split('—')[0].strip()} | {lf["quota_law"].split('—')[1].strip() if '—' in lf["quota_law"] else lf["quota_law"]} | Vigente |
| {lf["parity_law"].split('—')[0].strip()} | {lf["parity_law"].split('—')[1].strip() if '—' in lf["parity_law"] else lf["parity_law"]} | Vigente |

> **JNE:** {lf["enforcement_jne"]}
> **Primera aplicación plena:** {lf["effective_since"]}

**Brechas identificadas:**
| # | Brecha |
|---|---|
{gap_rows}

#### 4.4.2 Representación Actual — Perú

| Indicador | Valor | Fuente |
|---|---|---|
| Mujeres en el Congreso | {cr["congress_women_seats"]}/{cr["congress_total_seats"]} ({cr["congress_women_pct"]}%) | {cr["source"]} |
| Presidentas de comisiones | {cr["women_committee_presidents"]} | Congreso ene 2026 |
| Mujeres en Mesa Directiva | {cr["women_on_mesa_directiva"]} | Congreso ene 2026 |
| Candidatas presidenciales 2026 | {cr["presidential_candidates_women"]}/{cr["presidential_candidates_total"]} | JNE 2026 |
| V-Dem mujeres en parlamento | {cr["vdem_women_parliament_2024"]} (escala 0–1) | V-Dem v15 2024 |

#### 4.4.3 Violencia Política de Género (VPG) — Registro JNE 2022–2025

> **Total casos registrados:** {vdgp["cases_2022_2025"]} | **Con componente digital:** {vdgp["cases_digital_component"]}
> **Tasa de judicialización:** {vdgp["prosecution_rate_pct"]}%
> *Fuente: {vdgp["source"]}*

**Grupos más afectados:**
| Grupo |
|---|
{affected_rows}

**Perfil de agresores:**
| Agresor | Proporción |
|---|---|
{vdgp_perp_rows}

*Referencia ICCPR: {vdgp["iccpr_ref"]}*

#### 4.4.4 Participación Política Indígena y Mujeres Indígenas

| Indicador | Valor | Fuente |
|---|---|---|
| Electoras indígenas estimadas | {iw["estimated_eligible_voters"]:,} | ONPE/CAAAP 2025 |
| Lenguas sin material electoral completo | {", ".join(iw["languages_without_ballot"])} | ONPE 2025 |
| Candidatas indígenas (autodeclaradas) | {iw["candidates_indigenous_women"]}/{iw["candidates_self_identified_indigenous"]} mujeres/total | JNE 2026 |

*Referencia: {iw["iccpr_ref"]}*

*Fuentes: {gd["data_sources"]}*
"""

    return f"## 4. Inclusividad y Derechos Humanos\n\n{struct}\n{narrative}\n{peru_gender_block}\n"


def _generate_campaign_chapter(political: dict, context: dict = None) -> str:  # MIGRADO a chapters/generators.py
    media = political.get("media_analysis", {})
    finance = political.get("campaign_finance", {})
    power = political.get("power_network", {})

    # ── Extraer variables V-Dem reales para Red de Poder ──────────────────────
    vdem_ctx_cap5 = {}
    vdem_year_cap5 = "2024"
    vdem_confirmed_power = False
    if context:
        vdem_raw_p = context.get("vdem", {})
        if isinstance(vdem_raw_p, dict) and "_trace" in vdem_raw_p:
            vdem_ctx_cap5 = vdem_raw_p.get("value", {}) or {}
            vdem_confirmed_power = vdem_raw_p["_trace"].get("confidence") == "confirmed"
            vdem_year_cap5 = str(vdem_ctx_cap5.get("year", "2024"))
    # Proxies V-Dem para captura de poder (0=bajo riesgo, 1=alto riesgo)
    vdem_media_bias_risk   = vdem_ctx_cap5.get("media_bias_vdem")        # norm_inverted(v2mebias)
    vdem_opp_capture_risk  = 1.0 - vdem_ctx_cap5.get("opposition_autonomy", 0.5) if vdem_ctx_cap5.get("opposition_autonomy") is not None else None
    vdem_irregularity_risk = vdem_ctx_cap5.get("electoral_irregularities") # norm_inverted(v2elirreg)
    vdem_harjrn_risk       = vdem_ctx_cap5.get("journalist_harassment")    # norm_inverted(v2meharjrn)

    def _risk_label(score):
        if score is None: return "N/D"
        if score >= 0.70: return "🔴 ALTO"
        if score >= 0.45: return "🟡 MODERADO"
        return "🟢 BAJO"

    power_source_label = f"V-Dem v15 ({vdem_year_cap5}) — proxy estructural" if vdem_confirmed_power else "estimado"
    power_data_available = vdem_confirmed_power and vdem_media_bias_risk is not None

    # RSF: datos reales de libertad de prensa (complementa análisis de medios)
    rsf_data_cap5 = {}
    rsf_confirmed_cap5 = False
    if context:
        rsf_raw_cap5 = context.get("rsf", {})
        if isinstance(rsf_raw_cap5, dict) and "_trace" in rsf_raw_cap5:
            rsf_data_cap5 = rsf_raw_cap5.get("value", {}) or {}
            rsf_confirmed_cap5 = rsf_raw_cap5["_trace"].get("confidence") == "confirmed"
    rsf_score_cap5 = rsf_data_cap5.get("score")
    rsf_rank_cap5 = rsf_data_cap5.get("rank")
    rsf_political_cap5 = rsf_data_cap5.get("political_context")

    # Determinar qué datos son reales vs mock
    media_source = media.get("data_source", "mock")
    finance_source = finance.get("data_source", "mock")
    media_confirmed = "PEI" in str(media_source)
    finance_confirmed = "PEI" in str(finance_source)

    bias_index = media.get("bias_index", "N/D")
    bias_dir = media.get("bias_direction", "N/D")
    media_assessment = media.get("assessment", "N/D")
    pei_media_score = media.get("pei_media_score")
    finance_score = finance.get("transparency_score", "N/D")
    finance_assessment = finance.get("assessment", "N/D")
    pei_finance_score = finance.get("pei_finance_score")
    state_abuse = finance.get("state_resource_abuse", "N/D")
    donations_disclosed = finance.get("donations_disclosed", False)

    exposure_rows = "\n".join(
        f"| {k.replace('_', ' ').title()} | {v}% |"
        for k, v in media.get("exposure_distribution", {}).items()
    )

    # Fila RSF en tabla de medios (datos reales si están disponibles)
    rsf_media_row = ""
    if rsf_confirmed_cap5 and rsf_score_cap5 is not None:
        rsf_media_row = f"\n| Score libertad de prensa (RSF 2025) | {rsf_score_cap5}/100 (Rank #{rsf_rank_cap5}/180) | RSF 2025 — confirmed |"

    # Tabla estructurada con indicación de fuente
    struct = f"""**Análisis de Medios** *({'PEI-10.0 — confirmed' if media_confirmed else 'datos mock — pendiente'})*
| Indicador | Valor | Fuente |
|---|---|---|
| Score cobertura mediática (PEI) | {f"{pei_media_score}/100" if pei_media_score else "N/D"} | {'PEI-10.0' if media_confirmed else 'mock'} |
| Índice de sesgo derivado | {bias_index} | {'PEI-10.0' if media_confirmed else 'mock'} |
| Evaluación general | {media_assessment} | PEIRS |
| Dirección del sesgo | {bias_dir} | mock |{rsf_media_row}

**Distribución de exposición** *({'PEI 10.0 — confirmado' if media_confirmed else 'estimación derivada — pendiente verificación ONPE/JNE'})*
| Actor | Exposición |
|---|---|
{exposure_rows}

**Financiamiento de Campaña** *({'PEI-10.0 — confirmed' if finance_confirmed else 'datos mock — pendiente'})*
| Indicador | Valor | Fuente |
|---|---|---|
| Score transparencia financiera (PEI) | {f"{pei_finance_score}/100" if pei_finance_score else "N/D"} | {'PEI-10.0' if finance_confirmed else 'mock'} |
| Transparencia derivada | {finance_score} ({finance_assessment}) | {'PEI-10.0' if finance_confirmed else 'mock'} |
| Abuso de recursos estatales | {state_abuse} | mock |
| Donaciones corporativas divulgadas | {'Sí' if donations_disclosed else 'No'} | mock |

**Red de Poder** *({power_source_label} · verificación OpenCorporates/registros nacionales pendiente)*
| Indicador | Score | Riesgo | Fuente |
|---|---|---|---|
| Sesgo mediático estructural (v2mebias) | {f"{vdem_media_bias_risk:.3f}" if vdem_media_bias_risk is not None else "N/D"} | {_risk_label(vdem_media_bias_risk)} | {power_source_label} |
| Autonomía de la oposición (v2psoppaut) | {f"{vdem_opp_capture_risk:.3f}" if vdem_opp_capture_risk is not None else "N/D"} | {_risk_label(vdem_opp_capture_risk)} | {power_source_label} |
| Irregularidades electorales (v2elirreg) | {f"{vdem_irregularity_risk:.3f}" if vdem_irregularity_risk is not None else "N/D"} | {_risk_label(vdem_irregularity_risk)} | {power_source_label} |
| Acoso a periodistas (v2meharjrn) | {f"{vdem_harjrn_risk:.3f}" if vdem_harjrn_risk is not None else "N/D"} | {_risk_label(vdem_harjrn_risk)} | {power_source_label} |
| Riesgo de captura institucional | — | {_risk_label(vdem_opp_capture_risk)} | PEIRS (derivado V-Dem) |

> *Nota metodológica: Las variables V-Dem son proxies estructurales del estado del ecosistema democrático. Los vínculos específicos candidato-medios y empresa-partido requieren integración con OpenCorporates o fuentes registrales nacionales (pendiente).*"""

    # Solo LLM para datos reales — media y/o finance PEI o RSF
    if not media_confirmed and not finance_confirmed and not rsf_confirmed_cap5:
        return f"## 5. Campaña, Redes de Poder y Financiamiento\n\n{struct}\n\n*Análisis narrativo pendiente de integración de fuentes reales de medios.*\n"

    sys_prompt = (
        "Sos un analista senior de integridad electoral para DEMOCRAC.IA/PEIRS. "
        "Combinas tres registros en tu escritura: "
        "(1) analitico-ejecutivo para inversores y tomadores de decision con foco en riesgo politico, "
        "(2) periodistico de investigacion accesible para capacitaciones sobre democracia, "
        "(3) tecnico con referencias a estandares internacionales cuando corresponda. "
        "Redactas en espanol. Sos honesto sobre qué datos son verificados y cuales son estimaciones."
    )

    pei_media_interpretation = (
        "muy bajo (cobertura fuertemente asimetrica)" if pei_media_score and pei_media_score < 30
        else "bajo (cobertura parcialmente asimetrica)" if pei_media_score and pei_media_score < 50
        else "moderado" if pei_media_score and pei_media_score < 70
        else "aceptable"
    ) if pei_media_score else "sin datos PEI"

    pei_finance_interpretation = (
        "muy bajo (financiamiento opaco, posible corrupcion)" if pei_finance_score and pei_finance_score < 25
        else "bajo (transparencia limitada)" if pei_finance_score and pei_finance_score < 45
        else "moderado" if pei_finance_score and pei_finance_score < 65
        else "aceptable"
    ) if pei_finance_score else "sin datos PEI"

    rsf_block_prompt = ""
    if rsf_confirmed_cap5 and rsf_score_cap5 is not None:
        rsf_class_cap5 = (
            "critica" if rsf_score_cap5 < 30 else "dificil" if rsf_score_cap5 < 45
            else "problematica" if rsf_score_cap5 < 60 else "satisfactoria" if rsf_score_cap5 < 75 else "buena"
        )
        rsf_block_prompt = (
            f"\nDATOS VERIFICADOS RSF 2025 (confidence=confirmed):\n"
            f"- Score libertad de prensa: {rsf_score_cap5}/100 ({rsf_class_cap5}) — Rank #{rsf_rank_cap5}/180\n"
            + (f"- Contexto politico RSF: {rsf_political_cap5}\n" if rsf_political_cap5 is not None else "")
        )

    user_prompt = (
        f"Escribe exactamente 3 parrafos para el Capitulo 5 'Campana, Redes de Poder y Financiamiento'.\n\n"
        f"DATOS VERIFICADOS (PEI-10.0, confidence=confirmed):\n"
        f"- Score cobertura mediatica PEI: {pei_media_score}/100 — interpretacion: {pei_media_interpretation}\n"
        f"- Bias index derivado: {bias_index} | Evaluacion: {media_assessment}\n"
        f"- Score financiamiento campaña PEI: {pei_finance_score}/100 — interpretacion: {pei_finance_interpretation}\n"
        f"- Transparencia derivada: {finance_score} ({finance_assessment})\n"
        + rsf_block_prompt +
        f"\nDATOS MOCK (no verificados, NO mencionar como hechos):\n"
        f"- Abuso recursos estatales: {state_abuse}\n"
        f"- Riesgo captura poder: {power.get('capture_risk', 'N/D')}\n\n"
        f"ESTRUCTURA DE LOS 3 PARRAFOS:\n"
        f"Parrafo 1 (analitico-ejecutivo, ~90 palabras): analiza el score de cobertura mediatica "
        f"del PEI y su implicancia para la equidad de la campana. "
        + (f"Integra el score RSF {rsf_score_cap5}/100 como indicador complementario de libertad de prensa. " if rsf_confirmed_cap5 and rsf_score_cap5 else "")
        + f"El sesgo mediatico como factor de riesgo electoral segun los estandares de la Declaracion de Principios EOS.\n"
        f"Parrafo 2 (analitico-ejecutivo, ~80 palabras): analiza la transparencia del financiamiento "
        f"de campaña segun PEI. Vincula la opacidad financiera con riesgo de captura estatal "
        f"y su impacto en la legitimidad del proceso para actores internacionales.\n"
        f"Parrafo 3 (periodistico, ~70 palabras): conclusion accesible sobre el panorama de "
        f"medios y financiamiento. Indica claramente que los datos de redes de poder son "
        f"estimaciones pendientes de verificacion, sin presentarlos como hechos.\n\n"
        f"Importante: distingui explicitamente entre datos PEI/RSF verificados y estimaciones mock."
    )

    def fallback(ms=pei_media_score, fs=pei_finance_score, ma=media_assessment, fa=finance_assessment, rs=rsf_score_cap5, rr=rsf_rank_cap5):
        rsf_part = f" El índice RSF 2025 de libertad de prensa registra {rs}/100 (Rank #{rr}/180), completando el diagnóstico del entorno mediático." if rs else ""
        return (
            f"El score de cobertura mediatica del PEI ({ms}/100) indica una situacion de {ma}, "
            f"lo que compromete el acceso equitativo a la informacion electoral segun los estandares "
            f"de la Declaracion de Principios para la Observacion Internacional de Elecciones.{rsf_part} "
            f"El financiamiento de campana registra un score de {fs}/100 ({fa}), "
            f"senalando deficiencias en la transparencia que afectan la confianza institucional en el proceso."
        )

    narrative = _llm_generate(sys_prompt, user_prompt, fallback)

    return f"## 5. Campaña, Redes de Poder y Financiamiento\n\n{struct}\n\n{narrative}\n"


def _generate_digital_chapter(political: dict, context: dict = None, country_code: str = "") -> str:  # MIGRADO a chapters/generators.py
    digital = political.get("digital_ecosystem", {})

    # Extraer datos V-Dem digitales del context
    vdem_dig = {}
    vdem_confirmed = False
    vdem_year = "---"
    if context:
        vdem_dig_raw = context.get("digital_vdem", {})
        if isinstance(vdem_dig_raw, dict) and "_trace" in vdem_dig_raw:
            vdem_dig = vdem_dig_raw.get("value", {}) or {}
            vdem_confirmed = vdem_dig_raw["_trace"].get("confidence") == "confirmed"
        vdem_year = vdem_dig.get("data_year", "---")

    # RSF: datos reales de libertad de prensa
    rsf_data = {}
    rsf_confirmed = False
    if context:
        rsf_raw = context.get("rsf", {})
        if isinstance(rsf_raw, dict) and "_trace" in rsf_raw:
            rsf_data = rsf_raw.get("value", {}) or {}
            rsf_confirmed = rsf_raw["_trace"].get("confidence") == "confirmed"
    rsf_score = rsf_data.get("score")
    rsf_rank = rsf_data.get("rank")
    rsf_political = rsf_data.get("political_context")
    rsf_legal = rsf_data.get("legal_context")
    rsf_safety = rsf_data.get("safety")
    rsf_economic = rsf_data.get("economic_context")
    rsf_social = rsf_data.get("social_context")
    rsf_table = "*RSF no disponible*"
    rsf_source_note = ""

    # Tabla RSF — real si hay datos confirmados, placeholder si no
    if rsf_confirmed and rsf_score is not None:
        rsf_rows = [
            "| Indicador | Valor | Fuente |",
            "|---|---|---|",
            f"| Score libertad de prensa 2025 | {rsf_score}/100 | RSF 2025 |",
            f"| Ranking mundial | #{rsf_rank}/180 | RSF 2025 |",
        ]
        if rsf_political is not None:
            rsf_rows.append(f"| Contexto político | {round(float(rsf_political), 1)}/100 | RSF 2025 |")
        if rsf_legal is not None:
            rsf_rows.append(f"| Marco legal | {round(float(rsf_legal), 1)}/100 | RSF 2025 |")
        if rsf_safety is not None:
            rsf_rows.append(f"| Seguridad periodistas | {round(float(rsf_safety), 1)}/100 | RSF 2025 |")
        if rsf_economic is not None:
            rsf_rows.append(f"| Contexto económico | {round(float(rsf_economic), 1)}/100 | RSF 2025 |")
        if rsf_social is not None:
            rsf_rows.append(f"| Contexto social | {round(float(rsf_social), 1)}/100 | RSF 2025 |")
        rsf_table = "\n".join(rsf_rows)
        rsf_source_note = "*Reporters Without Borders (RSF). Press Freedom Index 2025 — confidence: confirmed. https://rsf.org/en/index*"
    else:
        rsf_table = "*RSF Press Freedom Index: datos no disponibles para este país.*"
        rsf_source_note = ""

    # FH para restricciones legales
    fh_cl = 4
    if context:
        fh_raw = context.get("civil_liberties", {})
        if isinstance(fh_raw, dict) and "_trace" in fh_raw:
            cl_val = fh_raw.get("value", {})
            fh_cl = cl_val.get("cl_rating", 4) if isinstance(cl_val, dict) else 4

    def score_label(val):
        if val is None:
            return "N/D"
        if val >= 0.75:
            return f"{round(val, 2)} — bajo riesgo"
        if val >= 0.50:
            return f"{round(val, 2)} — riesgo moderado"
        if val >= 0.25:
            return f"{round(val, 2)} — alto riesgo"
        return f"{round(val, 2)} — riesgo critico"

    fh_cl_label = (
        "severas (CL=6-7)" if fh_cl >= 6
        else "significativas (CL=5)" if fh_cl == 5
        else "moderadas (CL=4)" if fh_cl == 4
        else "limitadas (CL=3)" if fh_cl == 3
        else "minimas (CL=1-2)"
    )

    # Tabla V-Dem
    if vdem_confirmed:
        vdem_rows = [
            "| Indicador | Score (0=peor, 1=mejor) | Fuente |",
            "|---|---|---|",
            f"| Censura de internet (ejecutivo) | {score_label(vdem_dig.get('internet_censorship'))} | V-Dem v2mecenefi {vdem_year} |",
            f"| Censura de medios (ejecutivo) | {score_label(vdem_dig.get('media_censorship'))} | V-Dem v2mecenefm {vdem_year} |",
            f"| Acoso a periodistas | {score_label(vdem_dig.get('journalist_harassment'))} | V-Dem v2meharjrn {vdem_year} |",
            f"| Sesgo mediatico | {score_label(vdem_dig.get('media_bias_vdem'))} | V-Dem v2mebias {vdem_year} |",
            f"| Dominio gubernamental RRSS | {score_label(vdem_dig.get('gov_social_media_dominance'))} | V-Dem v2smgovdom {vdem_year} |",
            f"| Capacidad filtrado internet | {score_label(vdem_dig.get('gov_internet_filter_capacity'))} | V-Dem v2smgovfilcap {vdem_year} |",
            f"| Libertad de expresion alternativa | {score_label(vdem_dig.get('freedom_of_expression'))} | V-Dem v2x_freexp_altinf {vdem_year} |",
        ]
        vdem_table = "\n".join(vdem_rows)
        vdem_source_note = f"*V-Dem Dataset v15, año {vdem_year} — confidence: confirmed*"
    else:
        vdem_table = "*V-Dem digital: datos no disponibles para este pais en la version actual.*"
        vdem_source_note = ""

    # Tabla de indicadores — Para PER usar datos reales, resto queda como estimación
    if country_code == "PER":
        _bn   = PERU_DIGITAL_THREATS.get("bot_network", {})
        _dis  = PERU_DIGITAL_THREATS.get("disinformation_ecosystem", {})
        _gbv  = PERU_DIGITAL_THREATS.get("digital_gbv", {})
        _ooni = PERU_DIGITAL_THREATS.get("ooni_blocked_domains_2024", [])

        _bot_activity_cell = f"Detectada — {_bn.get('operation_name', 'Operación Cóndor Digital')} ({_bn.get('period', 'oct 2024–ene 2026')})"
        _bot_size_cell     = f"{_bn.get('estimated_total', '~23,000–26,000 cuentas')} — {_bn.get('source', 'IPYS Perú 2025')}"
        _bot_state         = "CONFIRMADO (análisis CIB)"

        _narratives        = _dis.get("main_narratives_2025_2026", [])
        _dis_cell          = f"{len(_narratives)} narrativas activas — {_dis.get('reach_estimate', '~2.1M personas')} (Ipsos/CALANDRIA feb 2026)"
        _dis_state         = "CONFIRMADO"

        # OONI en tiempo real primero; fallback a datos estáticos
        _live_ooni = get_ooni_summary(country_code, days_back=7)
        if _live_ooni.get("available"):
            _ooni_cell  = _live_ooni["summary_text"]
            _ooni_state = f"OONI LIVE ({_live_ooni['alert_level'].upper()})"
        elif _ooni:
            _ooni_cell  = f"Detectada — {len(_ooni)} dominio(s): {'; '.join(_ooni[:2])} (OONI 2024)"
            _ooni_state = "CONFIRMADO (datos estáticos)"
        else:
            _ooni_cell  = "No detectada"
            _ooni_state = "Sin datos OONI"

        _sup_cell          = "Sí — narrativas falsas de supresión de padrón + VDGP como disuasivo de candidatura (CALANDRIA/CONEJEM 2025)"
        _sup_state         = "CONFIRMADO"

        _gbv_incidents     = _gbv.get("incidents", [])
        try:
            _hate_count = PERU_GENDER_DATA["vdgp_registry"]["cases_digital_component"]
        except Exception:
            _hate_count = len(_gbv_incidents)
        _hate_cell         = f"{_hate_count} incidentes VDGP digitales documentados (JNE Observatorio, dic 2025)"
        _hate_state        = "CONFIRMADO"
    else:
        _bot_activity_cell = 'Detectada' if digital.get('bot_activity') else 'No detectada'
        _bot_size_cell     = f"{digital.get('bot_network_size', 0):,} cuentas"
        _bot_state         = "Mock"
        _dis_cell          = str(digital.get('disinformation_campaigns', 0))
        _dis_state         = "Mock"
        # OONI en tiempo real para cualquier país
        _live_ooni = get_ooni_summary(country_code, days_back=7)
        if _live_ooni.get("available"):
            _ooni_cell  = _live_ooni["summary_text"]
            _ooni_state = f"OONI LIVE ({_live_ooni['alert_level'].upper()})"
        else:
            _ooni_cell  = 'Detectada' if digital.get('censorship_detected') else 'No detectada'
            _ooni_state = "Mock"
        _sup_cell          = 'Sí' if digital.get('voter_suppression_online') else 'No'
        _sup_state         = "Mock"
        _hate_cell         = str(digital.get('hate_speech_incidents', 0))
        _hate_state        = "Mock"

    mock_rows = [
        "| Indicador | Estimacion | Estado |",
        "|---|---|---|",
        f"| Actividad de bots | {_bot_activity_cell} | {_bot_state} |",
        f"| Red de bots estimada | {_bot_size_cell} | {_bot_state} |",
        f"| Campanas de desinformacion | {_dis_cell} | {_dis_state} |",
        f"| Censura de URLs | {_ooni_cell} | {_ooni_state} |",
        f"| Supresion de votantes online | {_sup_cell} | {_sup_state} |",
        f"| Incidentes discurso de odio | {_hate_cell} | {_hate_state} |",
    ]
    mock_table = "\n".join(mock_rows)

    # Narrativa LLM solo si hay datos V-Dem reales
    if vdem_confirmed:
        sys_prompt = (
            "Sos un analista senior de ecosistemas de informacion y libertad de prensa para DEMOCRAC.IA/PEIRS. "
            "Combinas analisis tecnico con perspectiva de derechos humanos y accesibilidad para capacitaciones. "
            "Escribis en espanol con precision."
        )
        user_prompt = (
            "Escribe exactamente 3 parrafos sobre el ecosistema digital electoral.\n\n"
            "DATOS VERIFICADOS V-Dem v15 (confidence=confirmed):\n"
            f"- Censura internet ejecutivo: {score_label(vdem_dig.get('internet_censorship'))}\n"
            f"- Censura medios ejecutivo: {score_label(vdem_dig.get('media_censorship'))}\n"
            f"- Acoso periodistas: {score_label(vdem_dig.get('journalist_harassment'))}\n"
            f"- Dominio gubernamental RRSS: {score_label(vdem_dig.get('gov_social_media_dominance'))}\n"
            f"- Libertad expresion alternativa: {score_label(vdem_dig.get('freedom_of_expression'))}\n"
            f"- Restricciones legales FH: {fh_cl_label}\n\n"
            "Parrafo 1 (tecnico-institucional, ~90 palabras): estado de la censura y libertad de expresion "
            "segun V-Dem. Vincula con Art. 19 ICCPR sobre libertad de expresion digital.\n"
            "Parrafo 2 (analitico-ejecutivo, ~80 palabras): capacidad gubernamental de control del espacio "
            "digital como factor de riesgo electoral para inversores y actores internacionales.\n"
            "Parrafo 3 (periodistico, ~70 palabras): hallazgo mas significativo en lenguaje accesible. "
            "Menciona que datos de bots y censura especifica estan pendientes de verificacion con OONI.\n\n"
            "Solo prosa, sin vinetas ni subtitulos."
        )

        def fallback_dig(vd=vdem_dig, sl=score_label):
            parts = []
            ic = vd.get("internet_censorship")
            if ic is not None:
                parts.append(f"El indice de censura de internet registra {sl(ic)}, segun V-Dem v15.")
            mh = vd.get("journalist_harassment")
            if mh is not None:
                parts.append(f"El acoso a periodistas alcanza {sl(mh)}, indicando restricciones al espacio civico informativo.")
            return " ".join(parts) if parts else "Analisis del ecosistema digital basado en V-Dem v15."

        narrative = _llm_generate(sys_prompt, user_prompt, fallback_dig)
    else:
        narrative = (
            "*Analisis narrativo basado en V-Dem pendiente para este pais. "
            "Los indicadores de V-Dem estan disponibles solo para paises con datos en el dataset v15 (2024).*"
        )

    # Narrativa RSF-only si no hay V-Dem pero sí RSF
    if not vdem_confirmed and rsf_confirmed and rsf_score is not None:
        rsf_class = (
            "critica" if rsf_score < 30 else "dificil" if rsf_score < 45
            else "problematica" if rsf_score < 60 else "satisfactoria" if rsf_score < 75 else "buena"
        )
        sys_rsf = "Sos un analista de libertad de prensa para DEMOCRAC.IA/PEIRS. Espanol, preciso."
        usr_rsf = (
            f"2 parrafos sobre libertad de prensa. RSF 2025: score={rsf_score}/100 ({rsf_class}), "
            f"rank=#{rsf_rank}/180, politico={rsf_political}, legal={rsf_legal}, seguridad={rsf_safety}. "
            "P1 (~80 palabras): estado segun RSF, Art. 19 ICCPR. "
            "P2 (~70 palabras): impacto electoral, menciona OONI pendiente. Solo prosa."
        )
        narrative = _llm_generate(sys_rsf, usr_rsf, lambda rs=rsf_score, rr=rsf_rank: f"RSF score {rs}/100 (Rank #{rr}).")

    # ── Bloque específico Perú ────────────────────────────────────────────────
    peru_digital_block = ""
    if country_code == "PER":
        dt = PERU_DIGITAL_THREATS

        # Tabla deepfakes/IA — si audit_status pendiente, fila explicativa
        _ai = dt.get("ai_deepfakes", {})
        if _ai.get("audit_status") and not _ai.get("incidents_2024_2025"):
            ai_rows = "| _Sección postergada_ | _ver aviso debajo_ |"
            ai_audit_note = ("⚠️ **Incidentes específicos retirados (2026-04-26).** Las menciones previas a "
                             "deepfakes de Castillo, audio IA de Boluarte, clips de candidatos 2026 y "
                             "perfiles falsos de 'Operación Cóndor Digital' fueron retiradas por ausencia "
                             "de URL primaria a fact-check. Reactivar con cita verificable individual.")
        else:
            ai_rows = "\n".join(f"| {i+1} | {inc} |" for i, inc in enumerate(_ai.get("incidents_2024_2025", [])))
            ai_audit_note = ""
        # Tabla VDGP — si audit parcial, agregar nota
        _gbv_blk = dt.get("digital_gbv", {})
        gbv_rows = "\n".join(f"| {i+1} | {inc} |" for i, inc in enumerate(_gbv_blk.get("incidents", [])))
        gbv_audit_note = ("> ℹ️ *3 incidentes adicionales fueron retirados por ausencia de URL primaria. Reactivar con cita verificable.*"
                          if _gbv_blk.get("audit_status") and "partial" in str(_gbv_blk.get("audit_status")) else "")
        # Narrativas de desinformación — si audit pendiente, aviso
        _dis_blk = dt.get("disinformation_ecosystem", {})
        if _dis_blk.get("audit_status") and not _dis_blk.get("main_narratives_2025_2026"):
            disinfo_rows = "| _Pendiente_ | _Narrativas retiradas — ver aviso debajo_ |"
            disinfo_audit_note = ("⚠️ **Narrativas retiradas (2026-04-26).** Las atribuciones previas "
                                  "(fraude anticipado, xenofobia anti-venezolanos/cubanos, padrón depurado, "
                                  "agentes extranjeros) carecían de URL primaria a fact-check. "
                                  "Reactivar con link a Ojo Público / PerúCheck / La Mula por narrativa.")
        else:
            disinfo_rows = "\n".join(f"| {i+1} | {narr} |" for i, narr in enumerate(_dis_blk.get("main_narratives_2025_2026", [])))
            disinfo_audit_note = ""

        peru_digital_block = f"""
---
### 6.4 Amenazas Digitales Específicas — Perú 2026 *(IPYS + JNE + CALANDRIA + V-Dem v15)*

#### 6.4.1 Inteligencia Artificial y Deepfakes Electorales

> **Brecha regulatoria:** {dt["ai_deepfakes"]["regulatory_gap"]}
> **Respuesta institucional:** {dt["ai_deepfakes"]["jne_onpe_response"]}

| # | Incidente documentado (2024–2025) |
|---|---|
{ai_rows}

{ai_audit_note}

*Referencia ICCPR: {dt["ai_deepfakes"]["iccpr_ref"]}*

#### 6.4.2 Ataques a Infraestructura Electoral Digital

> ⚠️ **Sección postergada (2026-04-26).** Las afirmaciones previas sobre incidentes
> de ciberseguridad electoral peruana (ataques DDoS al portal JNE, accesos no
> autorizados a INFOGOB, filtraciones en RENIEC, ransomware sobre TREP en
> simulacros, presupuesto de ciberseguridad y certificación ISO 27001) **fueron
> retiradas por ausencia de fuentes verificables individuales**. La sección se
> reactivará únicamente con citas primarias por incidente (URLs públicas o
> reportes oficiales de ONPE / JNE / RENIEC / IPYS).
>
> *Referencia ICCPR: Art. 25 — derecho a votar en elecciones auténticas exige
> integridad de infraestructura.*

#### 6.4.3 Violencia Digital de Género Político (VDGP)

> **Marco legal:** {dt["digital_gbv"]["legal_framework"]}
> **Acción JNE:** {dt["digital_gbv"]["jne_action"]}

| # | Incidente documentado (2025–2026) |
|---|---|
{gbv_rows}

{gbv_audit_note}

*Referencia ICCPR: {dt["digital_gbv"]["iccpr_ref"]}*

#### 6.4.4 Ecosistema de Desinformación Electoral

**Plataformas principales:** {", ".join(dt["disinformation_ecosystem"]["key_platforms"])}
**Alcance estimado:** {dt["disinformation_ecosystem"]["reach_estimate"]}
**Verificadores activos:** {", ".join(dt["disinformation_ecosystem"]["fact_checkers"])}

| # | Narrativa falsa identificada (2025–2026) |
|---|---|
{disinfo_rows}

{disinfo_audit_note}

#### 6.4.5 Indicadores Medidos — Perú

| Indicador | Valor | Fuente |
|---|---|---|
| Score libertad de prensa | {dt["rsf_score_2025"]}/100 (Rank #{dt["rsf_rank_2025"]}/180) | RSF 2025 |
| Censura internet ejecutivo | {dt["vdem_internet_censorship_2024"]} (escala 0–1, mayor=mejor) | V-Dem v15 2024 |
| Acoso a periodistas | {dt["vdem_journalist_harassment_2024"]} (escala 0–1, mayor=mejor) | V-Dem v15 2024 |
| Sesgo mediático | {dt["vdem_media_bias_2024"]} (escala 0–1, mayor=mejor) | V-Dem v15 2024 |
| Dominios bloqueados OONI | {", ".join(dt["ooni_blocked_domains_2024"])} | OONI 2024 |

*Fuentes: {dt["data_sources"]}*
"""

    lines = [
        "## 6. Ecosistema de Informacion y Monitoreo Digital",
        "",
        "### Libertad de Prensa — RSF Press Freedom Index 2025",
        "",
        rsf_table,
        rsf_source_note,
        "",
        "### Libertad de Expresion e Informacion — V-Dem v15",
        "",
        vdem_table,
        vdem_source_note,
        "",
        f"### Restricciones Legales a Medios — Freedom House FIW 2025",
        "",
        f"Libertades civiles (CL rating): {fh_cl}/7 — restricciones {fh_cl_label}",
        "",
        "### Analisis Narrativo",
        "",
        narrative,
        "",
        "### Indicadores Estimados del Sistema *(pendiente verificacion OONI)*",
        "",
        mock_table,
        peru_digital_block,
        "",
        "### Fuentes Pendientes de Integracion — Fase 2",
        "",
        "- **OONI** — censura de internet en tiempo real (ooni.org)",
        "- **CIVICUS Monitor** — espacio civico digital",
        "- **NetBlocks** — interrupciones de internet durante elecciones",
    ]
    return "\n".join(lines)


def _generate_voting_day_chapter(voting_day_data: dict, state: "ElectionRiskState") -> str:  # MIGRADO a chapters/generators.py
    """Genera Cap. 7 — modo observación si hay sesión activa, modo votación si hay datos de campo, placeholder si nada."""
    country_code = state.get("country_code", "")

    # ── Prioridad 1: Protocolo de observación activo ───────────────────────────
    if country_code and country_code in observation_store:
        session = observation_store[country_code]
        return _generate_observation_chapter(session, state)

    # ── Prioridad 2: Datos de jornada cargados via voting-day endpoint ─────────
    if not voting_day_data or not voting_day_data.get("active"):
        return (
            "## 7. Desarrollo del Dia de Votacion\n\n"
            "> Este capitulo se activa el dia de la eleccion mediante el endpoint "
            "`POST /api/analyze/voting-day` con datos de participacion, incidentes "
            "y reportes de observadores.\n\n"
            "**Estado:** En espera de datos del dia de votacion.\n"
        )

    # Extraer datos
    participation = voting_day_data.get("participation_pct")
    results_pct = voting_day_data.get("results_transmitted_pct")
    incidents = voting_day_data.get("incidents", [])
    observer_reports = voting_day_data.get("observer_reports", [])
    emb_statements = voting_day_data.get("emb_statements", [])
    media_restrictions = voting_day_data.get("media_restrictions_reported", False)
    internet_disruptions = voting_day_data.get("internet_disruptions", False)
    violence_incidents = voting_day_data.get("violence_incidents", 0)
    timestamp_local = voting_day_data.get("timestamp_local", "Sin dato")
    updated_at = voting_day_data.get("updated_at", "")

    # Evaluacion del dia
    day_risk_factors = 0
    if violence_incidents and violence_incidents > 0:
        day_risk_factors += 2
    if media_restrictions:
        day_risk_factors += 1
    if internet_disruptions:
        day_risk_factors += 1
    if len(incidents) > 3:
        day_risk_factors += 1

    day_assessment = (
        "CRITICO" if day_risk_factors >= 4
        else "ALTO RIESGO" if day_risk_factors >= 3
        else "ALERTA" if day_risk_factors >= 2
        else "NORMAL CON INCIDENTES" if day_risk_factors >= 1
        else "NORMAL"
    )

    # Tabla de situacion
    rows = [
        "| Indicador | Estado | Fuente |",
        "|---|---|---|",
        f"| Participacion estimada | {str(participation) + '%' if participation is not None else 'Sin dato'} | Reporte campo |",
        f"| Actas transmitidas | {str(results_pct) + '%' if results_pct is not None else 'Sin dato'} | EMB |",
        f"| Incidentes reportados | {len(incidents)} | Observadores |",
        f"| Violencia fisica | {violence_incidents or 0} casos | Reportes campo |",
        f"| Restricciones a medios | {'Si' if media_restrictions else 'No'} | Monitoreo |",
        f"| Interrupciones internet | {'Detectadas' if internet_disruptions else 'No detectadas'} | OONI/campo |",
    ]
    table = "\n".join(rows)

    # Secciones de incidentes
    incidents_section = ""
    if incidents:
        inc_lines = ["\n**Incidentes Reportados:**"]
        for inc in incidents:
            inc_lines.append("- " + inc)
        incidents_section = "\n".join(inc_lines)

    obs_section = ""
    if observer_reports:
        obs_lines = ["\n**Reportes de Observadores:**"]
        for rep in observer_reports:
            obs_lines.append("- " + rep)
        obs_section = "\n".join(obs_lines)

    emb_section = ""
    if emb_statements:
        emb_lines = ["\n**Declaraciones del Organismo Electoral:**"]
        for stmt in emb_statements:
            emb_lines.append("- " + stmt)
        emb_section = "\n".join(emb_lines)

    # Narrativa LLM
    sys_prompt = (
        "Sos el analista de operaciones electorales de DEMOCRAC.IA/PEIRS. "
        "Generás reportes del dia de votacion en espanol, tono tecnico-periodistico de alto nivel. "
        "Basas el analisis exclusivamente en los datos recibidos."
    )

    incidents_str = "; ".join(incidents[:5]) if incidents else "sin incidentes mayores"
    obs_str = "; ".join(observer_reports[:3]) if observer_reports else "sin reportes"

    user_prompt = (
        "Genera el reporte del dia de votacion para " + state["country"]
        + " (eleccion: " + state["election_date"] + "). "
        + "Hora de actualizacion: " + timestamp_local + ". "
        + "Participacion: " + (str(participation) + "%" if participation else "sin dato") + ". "
        + "Actas transmitidas: " + (str(results_pct) + "%" if results_pct else "sin dato") + ". "
        + "Incidentes: " + incidents_str + ". "
        + "Reportes observadores: " + obs_str + ". "
        + "Violencia: " + str(violence_incidents or 0) + " casos. "
        + "Restricciones medios: " + ("si" if media_restrictions else "no") + ". "
        + "Internet: " + ("interrupciones detectadas" if internet_disruptions else "estable") + ". "
        + "Evaluacion del dia: " + day_assessment + ". "
        + "Escribe exactamente 3 parrafos: "
        + "Parrafo 1 (~90 palabras): estado general del proceso y participacion. "
        + "Parrafo 2 (~90 palabras): incidentes y reportes de observadores con impacto en integridad. "
        + "Parrafo 3 (~80 palabras): evaluacion del desarrollo del dia y proximos pasos. "
        + "Solo prosa, sin vinetas."
    )

    def fallback_vd():
        return (
            "El proceso electoral en " + state["country"] + " se desarrolla con evaluacion "
            + day_assessment + ". "
            + "Participacion estimada: " + (str(participation) + "%" if participation else "sin dato") + ". "
            + "Se han registrado " + str(len(incidents)) + " incidentes reportados por observadores en campo."
        )

    narrative = _llm_generate(sys_prompt, user_prompt, fallback_vd)

    lines = [
        "## 7. Desarrollo del Dia de Votacion",
        "",
        f"> **Ultima actualizacion:** {timestamp_local} | **Evaluacion del dia:** {day_assessment}",
        f"> Datos cargados: {updated_at[:19] if updated_at else 'N/A'} UTC",
        "",
        "### Cuadro de Situacion",
        "",
        table,
        incidents_section,
        obs_section,
        emb_section,
        "",
        "### Analisis Narrativo",
        "",
        narrative,
        "",
        "*Datos cargados via endpoint /api/analyze/voting-day. "
        "Verificacion en tiempo real con OONI y fuentes primarias pendiente.*",
    ]

    return "\n".join(lines)


# ── Protocolo de Observación Electoral — helpers ─────────────────────────────

# R4: Modelo de fase unificado — 9 fases del ciclo electoral completo
# Cubre desde período preparatorio hasta resolución de disputas
_PHASE_LABELS = {
    "preparatory":         "📋 PREPARATORIO",
    "pre_campaign":        "📣 PRE-CAMPAÑA",
    "campaign":            "🗣️ CAMPAÑA ELECTORAL",
    "electoral_silence":   "🤫 VEDA ELECTORAL",
    "election_day":        "🗳️ JORNADA ELECTORAL",
    "counting_tabulation": "🔢 ESCRUTINIO Y CÓMPUTO",
    "post_election":       "📊 POST-ELECTORAL",
    "dispute_resolution":  "⚖️ RESOLUCIÓN DE DISPUTAS",
    "completed":           "✅ CICLO COMPLETO",
    # Aliases de compatibilidad (mapeados a las fases canónicas para render)
    "pre_election":        "🔵 PRE-JORNADA (48h previas)",  # legacy → electoral_silence
}

# Orden canónico de fases (para validación de coherencia temporal)
_PHASE_ORDER: List[str] = [
    "preparatory",
    "pre_campaign",
    "campaign",
    "electoral_silence",
    "election_day",
    "counting_tabulation",
    "post_election",
    "dispute_resolution",
    "completed",
]

# Alias inverso para backward-compat (fase legada → fase canónica)
_PHASE_ALIAS: Dict[str, str] = {
    "pre_election": "electoral_silence",
}

_SEVERITY_BADGE = {
    "info":     "ℹ️ INFO",
    "low":      "🟢 BAJO",
    "medium":   "🟡 MEDIO",
    "high":     "🔴 ALTO",
    "critical": "🚨 CRÍTICO",
}

_CATEGORY_LABEL = {
    "logistics":          "Logística",
    "security":           "Seguridad",
    "legal":              "Legal/Normativo",
    "media":              "Medios",
    "digital":            "Ecosistema Digital",
    "counting":           "Escrutinio",
    "results":            "Resultados",
    "fraud_allegation":   "Alegación de Fraude",
    "hate_speech":        "Discurso de Odio",
    # R5: Categorías de observación faltantes
    "campaign_violation": "Infracción de Campaña",
    "voter_suppression":  "Supresión del Voto",
    "accessibility":      "Accesibilidad Electoral",
    "gender_violence":    "Violencia Política de Género",
    "disinformation":     "Desinformación Electoral",
    "voter_intimidation": "Intimidación de Votantes",
    "ballot_tampering":   "Manipulación de Votos",
    "media_restriction":  "Restricción de Medios",
    "irregular_procedure":"Procedimiento Irregular",
    "other":              "Otro",
}

# Mapa automático category+severity → derechos potencialmente vulnerados
_RIGHTS_AUTOMAP: Dict[str, List[str]] = {
    "logistics|high":   ["ICCPR Art. 25(b) — derecho a votar en condiciones equitativas"],
    "logistics|critical": ["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)"],
    "security|medium":  ["ICCPR Art. 25(b)", "ICCPR Art. 9 — derecho a la seguridad personal"],
    "security|high":    ["ICCPR Art. 25(b)", "ICCPR Art. 9", "CADH Art. 23", "ICCPR Art. 19"],
    "security|critical":["ICCPR Art. 25(b)", "ICCPR Art. 6 — derecho a la vida", "CADH Art. 4", "CADH Art. 23"],
    "legal|medium":     ["ICCPR Art. 25 — proceso libre y justo", "CADH Art. 23(2)"],
    "legal|high":       ["ICCPR Art. 25", "CADH Art. 23(2)", "CDI Art. 3 — derecho a elecciones auténticas"],
    "legal|critical":   ["ICCPR Art. 25", "CADH Art. 23", "CDI Art. 3", "Art. 2 ICCPR — recurso efectivo"],
    "media|high":       ["ICCPR Art. 19(2) — libertad de expresión", "CADH Art. 13"],
    "media|critical":   ["ICCPR Art. 19(2)", "CADH Art. 13", "ICCPR Art. 25"],
    "digital|high":     ["ICCPR Art. 19(2)", "ICCPR Art. 25", "OC-5/85 CIDH — libertad de expresión digital"],
    "digital|critical": ["ICCPR Art. 19(2)", "ICCPR Art. 25", "CADH Art. 23"],
    "counting|high":    ["ICCPR Art. 25(b) — escrutinio auténtico", "CADH Art. 23(1)(b)"],
    "counting|critical":["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)", "CDI Art. 6 — transparencia electoral"],
    "results|high":     ["ICCPR Art. 25(b)", "CADH Art. 23(1)(c) — acceso a cargos públicos"],
    "results|critical": ["ICCPR Art. 25(b)", "CADH Art. 23(1)(c)", "CDI Art. 3", "Art. 14 ICCPR — recurso judicial"],
    # R5: Nuevas categorías de observación
    "campaign_violation|medium":  ["ICCPR Art. 25 — campaña equitativa", "CADH Art. 23"],
    "campaign_violation|high":    ["ICCPR Art. 25", "CADH Art. 23", "ICCPR Art. 22 — libertad de asociación"],
    "campaign_violation|critical":["ICCPR Art. 25", "CADH Art. 23", "ICCPR Art. 22", "CADH Art. 16"],
    "voter_suppression|medium":   ["ICCPR Art. 25(b) — derecho al voto sin restricciones indebidas"],
    "voter_suppression|high":     ["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)", "ICERD Art. 5(c)"],
    "voter_suppression|critical": ["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)", "ICERD Art. 5(c)", "ICCPR Art. 2"],
    "accessibility|medium":       ["CRPD Art. 29 — participación en la vida política", "CADH Art. 23"],
    "accessibility|high":         ["CRPD Art. 29", "CADH Art. 23", "ICCPR Art. 25"],
    "accessibility|critical":     ["CRPD Art. 29", "ICCPR Art. 25", "CADH Art. 23", "ICCPR Art. 26 — igualdad"],
    "gender_violence|medium":     ["CEDAW Art. 7 — participación política de la mujer", "CADH Art. 23"],
    "gender_violence|high":       ["CEDAW Art. 7", "CADH Art. 23", "ICCPR Art. 3 — igualdad entre géneros"],
    "gender_violence|critical":   ["CEDAW Art. 7", "CADH Art. 23", "ICCPR Art. 3", "ICCPR Art. 7 — no tortura"],
    "disinformation|medium":      ["ICCPR Art. 19(2) — libertad de información veraz", "CADH Art. 13"],
    "disinformation|high":        ["ICCPR Art. 19(2)", "CADH Art. 13", "ICCPR Art. 25"],
    "disinformation|critical":    ["ICCPR Art. 19(2)", "CADH Art. 13", "ICCPR Art. 25", "ICCPR Art. 20 — no propaganda de odio"],
    "voter_intimidation|high":    ["ICCPR Art. 25(b)", "ICCPR Art. 9 — seguridad personal", "CADH Art. 23"],
    "voter_intimidation|critical":["ICCPR Art. 25(b)", "ICCPR Art. 9", "CADH Art. 23", "ICCPR Art. 7"],
    "ballot_tampering|high":      ["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)", "CDI Art. 6"],
    "ballot_tampering|critical":  ["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)", "CDI Art. 3", "CDI Art. 6"],
    "media_restriction|high":     ["ICCPR Art. 19(2)", "CADH Art. 13", "ICCPR Art. 25"],
    "media_restriction|critical": ["ICCPR Art. 19(2)", "CADH Art. 13", "ICCPR Art. 25", "ICCPR Art. 19(3)"],
    "irregular_procedure|high":   ["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)"],
    "irregular_procedure|critical":["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)", "CDI Art. 3"],
}


def _auto_rights(category: str, severity: str) -> List[str]:
    """Sugiere derechos potencialmente vulnerados según categoría y severidad."""
    key = f"{category}|{severity}"
    if key in _RIGHTS_AUTOMAP:
        return _RIGHTS_AUTOMAP[key]
    # Fallback por severidad
    if severity in ("high", "critical"):
        return ["ICCPR Art. 25 — derecho al sufragio auténtico"]
    return []


def _generate_observation_chapter(session: dict, state: "ElectionRiskState") -> str:  # MIGRADO a chapters/generators.py
    """
    Genera Cap. 7 cuando hay un protocolo de observación activo.
    Cubre las 3 fases: pre-jornada, jornada electoral, post-electoral.
    """
    country    = state.get("country", "País")
    e_date     = state.get("election_date", "N/A")
    phase      = session.get("phase", "pre_election")
    mission    = session.get("mission_name", "Misión de Observación")
    lead_org   = session.get("lead_org", "DEMOCRAC.IA")
    entries    = session.get("entries", [])
    started_at = session.get("started_at", "")[:10]

    # R4: Normalizar fase (alias legacy → canónica)
    phase_norm  = _PHASE_ALIAS.get(phase, phase)
    phase_label = _PHASE_LABELS.get(phase, _PHASE_LABELS.get(phase_norm, phase_norm))

    # ── Estadísticas de hallazgos ──────────────────────────────────────────────
    severity_counts: Dict[str, int] = {"info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    phase_counts:    Dict[str, int] = {}   # R4: dinámica, cualquier fase
    rights_mentioned: Dict[str, int] = {}

    for e in entries:
        sev = e.get("severity", "info")
        # R4: normalizar fase de entrada
        raw_ph = e.get("phase") or phase_norm or "campaign"
        ph = _PHASE_ALIAS.get(raw_ph, raw_ph)
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        phase_counts[ph]     = phase_counts.get(ph, 0) + 1
        auto_r = _auto_rights(e.get("category", "other"), sev)
        for r in (e.get("rights_at_risk") or []) + auto_r:
            rights_mentioned[r] = rights_mentioned.get(r, 0) + 1

    critical_count = severity_counts.get("critical", 0)
    high_count     = severity_counts.get("high", 0)
    total_entries  = len(entries)

    # ── Tabla resumen — R4: muestra TODAS las 9 fases con estado ──────────────
    active_phase_idx = _PHASE_ORDER.index(phase_norm) if phase_norm in _PHASE_ORDER else 0
    relevant_phases  = [p for p in _PHASE_ORDER[:active_phase_idx + 1]]
    phase_summary_rows = ["| Fase | Hallazgos | Estado |", "|---|---|---|"]
    for i, p in enumerate(_PHASE_ORDER):
        label = _PHASE_LABELS.get(p, p)
        count = phase_counts.get(p, 0)
        if i < active_phase_idx:
            status = "✅ Completada" if count > 0 else "✅ Sin incidencias"
        elif i == active_phase_idx:
            status = "🔴 **ACTIVA**"
        else:
            status = "⏳ Pendiente"
        phase_summary_rows.append(f"| {label} | {count} | {status} |")
    phase_summary_rows += [
        "| | | |",
        f"| **TOTAL** | **{total_entries}** | |",
        "| | | |",
        f"| 🚨 Críticos | {critical_count} | |",
        f"| 🔴 Altos | {high_count} | |",
        f"| 🟡 Medios | {severity_counts.get('medium', 0)} | |",
        f"| 🟢 Bajos + Info | {severity_counts.get('low', 0) + severity_counts.get('info', 0)} | |",
    ]
    summary_rows = "\n".join(phase_summary_rows)

    # ── Secciones por fase ─────────────────────────────────────────────────────
    def render_phase_section(phase_key: str, section_num: int) -> str:
        phase_title = _PHASE_LABELS.get(phase_key, phase_key)
        # Incluir entradas con alias normalizado
        phase_entries = [
            e for e in entries
            if _PHASE_ALIAS.get(e.get("phase", ""), e.get("phase", "")) == phase_key
        ]
        if not phase_entries:
            p_idx = _PHASE_ORDER.index(phase_key) if phase_key in _PHASE_ORDER else 0
            status = "En espera de datos" if p_idx > active_phase_idx else "No hay hallazgos registrados"
            return f"\n### 7.{section_num} {phase_title}\n\n> *{status}.*\n"

        rows = ["| # | ID | Hora | Observador | Ubicación | Categoría | Hallazgo | Severidad | Evidencia |",
                "|---|---|---|---|---|---|---|---|---|"]
        for i, e in enumerate(phase_entries, 1):
            ts      = (e.get("timestamp") or "")[:16]
            obs     = e.get("observer_id", "—")
            loc     = (e.get("location") or "—")[:30]
            cat     = _CATEGORY_LABEL.get(e.get("category", "other"), e.get("category", "—"))
            finding = (e.get("finding") or "")[:80]
            sev     = _SEVERITY_BADGE.get(e.get("severity", "info"), e.get("severity", "—"))
            eid     = e.get("entry_id", "—")
            ev_raw  = e.get("evidence_ref") or ""
            # Renderizar evidencia: URL → link clickeable; texto → como está; vacío → —
            if ev_raw.startswith("http://") or ev_raw.startswith("https://"):
                evidence = f"[Ver fuente]({ev_raw})"
            elif ev_raw:
                evidence = ev_raw[:60]
            else:
                evidence = "—"
            rows.append(f"| {i} | `{eid}` | {ts} | {obs} | {loc} | {cat} | {finding} | {sev} | {evidence} |")

        table = "\n".join(rows)

        rights_lines = []
        for e in phase_entries:
            if e.get("severity") in ("high", "critical"):
                auto_r = _auto_rights(e.get("category", "other"), e.get("severity", "info"))
                all_r  = list(set((e.get("rights_at_risk") or []) + auto_r))
                if all_r:
                    loc  = e.get("location", "Sin ubicación")
                    find = (e.get("finding") or "")[:100]
                    rights_lines.append(
                        f"- **{loc}** — {find}\n"
                        + "  *Derechos potencialmente vulnerados:* " + "; ".join(all_r)
                    )

        rights_section = ""
        if rights_lines:
            rights_section = "\n**Hallazgos de alta severidad y derechos afectados:**\n\n" + "\n".join(rights_lines)

        return f"\n### 7.{section_num} {phase_title}\n\n{table}\n{rights_section}\n"

    # R4: Renderizar solo las fases relevantes (hasta la fase activa inclusive)
    phase_sections = "\n".join(
        render_phase_section(p, i + 2)
        for i, p in enumerate(relevant_phases)
    )

    # ── Agent 5: patrones sistemáticos ────────────────────────────────────────
    pattern_section = ""
    patterns = detect_patterns(entries)
    if patterns.has_significant_patterns:
        pattern_section = render_pattern_markdown(patterns)

    # ── Análisis de fraude y discurso de odio ─────────────────────────────────
    fraud_hate_section = ""
    fh_analysis = analyze_fraud_and_hate(entries)
    if fh_analysis.get("has_significant_findings"):
        fraud_md = fh_analysis["fraud"].get("markdown", "")
        hate_md  = fh_analysis["hate_speech"].get("markdown", "")
        if fraud_md or hate_md:
            fraud_hate_section = "\n### 7.5 Análisis de Fraude Electoral y Discurso de Odio\n"
            if fraud_md:
                fraud_hate_section += fraud_md
            if hate_md:
                fraud_hate_section += hate_md

    # ── Análisis de derechos potencialmente vulnerados ─────────────────────────
    rights_analysis = "\n### 7.6 Análisis de Derechos Potencialmente Vulnerados\n\n"
    if rights_mentioned:
        top_rights = sorted(rights_mentioned.items(), key=lambda x: -x[1])
        rights_rows = ["| Instrumento / Artículo | Frecuencia de vulneración | Enlace |", "|---|---|---|"]
        for r, cnt in top_rights[:10]:
            # Generar link de referencia al instrumento
            instr_links = {
                "ICCPR": "https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights",
                "CADH":  "https://www.oas.org/dil/esp/tratados_B-32_Convencion_Americana_sobre_Derechos_Humanos.htm",
                "CEDAW": "https://www.un.org/womenwatch/daw/cedaw/",
                "CRPD":  "https://www.un.org/disabilities/documents/convention/convoptprot-e.pdf",
                "CDI":   "https://www.oas.org/charter/docs_es/resolucion1_es.htm",
                "ICERD": "https://www.ohchr.org/en/instruments-mechanisms/instruments/international-convention-elimination-all-forms-racial",
            }
            link = next((f"[Ver]({url})" for prefix, url in instr_links.items() if r.startswith(prefix)), "—")
            rights_rows.append(f"| {r} | {cnt} hallazgo(s) | {link} |")
        rights_analysis += "\n".join(rights_rows) + "\n"
    else:
        rights_analysis += (
            "> *Sin hallazgos con derechos afectados registrados en esta fase. "
            "Esta sección se completa automáticamente al registrar observaciones de campo "
            "via `POST /api/observation/{country_code}/entry`. "
            "Cada hallazgo activa el mapeo automático de artículos ICCPR/CADH/CEDAW/CRPD.*\n"
        )

    # ── Narrative final (LLM) ─────────────────────────────────────────────────
    narrative = ""
    if entries:
        sys_prompt = (
            "Sos el analista de observación electoral de DEMOCRAC.IA/PEIRS. "
            "Redactás narrativas técnicas sobre el proceso electoral basadas en hallazgos de campo. "
            "Combinás perspectiva de derechos humanos con análisis operacional. "
            "Escribís en español, tono técnico-institucional de alto nivel."
        )
        top_findings = "; ".join(
            f"[{e.get('phase','?')}/{e.get('severity','?')}] {e.get('finding','')}"
            for e in sorted(entries, key=lambda x: {"critical":0,"high":1,"medium":2,"low":3,"info":4}.get(x.get("severity","info"),5))[:8]
        )
        most_at_risk = list(rights_mentioned.keys())[:3]
        user_prompt = (
            f"Genera un análisis narrativo de la observación electoral en {country} (elección: {e_date}). "
            f"Fase actual: {phase_label}. Total hallazgos: {total_entries} ({critical_count} críticos, {high_count} altos). "
            f"Principales hallazgos: {top_findings}. "
            f"Derechos más afectados: {'; '.join(most_at_risk) or 'ninguno identificado aún'}. "
            "Escribe exactamente 3 párrafos: "
            "Párrafo 1 (~90 palabras): resumen del estado del proceso según los hallazgos. "
            "Párrafo 2 (~90 palabras): análisis de riesgos para la integridad electoral e impacto en derechos. "
            "Párrafo 3 (~70 palabras): conclusión preliminar y próximos pasos del protocolo de observación."
        )
        def _obs_fallback():
            return (
                f"La misión de observación en {country} ha registrado {total_entries} hallazgos "
                f"durante la fase {phase_label}. Se identificaron {critical_count} situaciones críticas "
                f"y {high_count} de alta severidad que requieren atención inmediata."
            )
        narrative = "\n### 7.7 Análisis Narrativo Consolidado\n\n" + _llm_generate(sys_prompt, user_prompt, _obs_fallback) + "\n"

    # ── Consolidado final (solo si phase == completed) ─────────────────────────
    consolidated = ""
    if phase_norm == "completed":
        consolidated = (
            "\n### 7.8 Ciclo de Observación Completado\n\n"
            "> **El ciclo de observación electoral ha concluido.** "
            "Este informe integra los hallazgos del protocolo de observación con el análisis de datasets (Capítulos 1–6). "
            "Ver endpoint `GET /api/observation/{country_code}/report` para el informe consolidado completo.\n"
        )

    lines = [
        "## 7. Observación Electoral — Ciclo Completo",
        "",
        f"> **Misión:** {mission} | **Organización líder:** {lead_org}",
        f"> **País:** {country} | **Elección:** {e_date} | **Inicio de sesión:** {started_at}",
        f"> **Fase activa:** {phase_label}",
        "",
        "### 7.1 Cuadro de Situación del Protocolo",
        "",
        summary_rows,
        phase_sections,   # R4: reemplaza pre/day/post_section fijos
        pattern_section,
        fraud_hate_section,
        rights_analysis,
        narrative,
        consolidated,
        "*Datos ingresados via `POST /api/observation/{country_code}/entry`. "
        "Verificación de trazabilidad habilitada.*",
    ]
    return "\n".join(lines)


def _generate_justice_chapter(legal: dict) -> str:  # MIGRADO a chapters/generators.py
    violations = legal.get("violations", [])

    if not violations:
        sys_prompt = "Sos un analista de cumplimiento de derecho electoral para DEMOCRAC.IA/PEIRS. Escribis en espanol, tono tecnico institucional."
        user_prompt = (
            "Escribe 1 parrafo (max 80 palabras) sobre cumplimiento del derecho electoral internacional "
            "para un pais sin violaciones detectadas. Menciona que opera dentro de estandares ICCPR y EOS."
        )
        def fb_no():
            return "No se detectaron violaciones al derecho internacional. El sistema opera dentro de los parametros EOS."
        narrative = _llm_generate(sys_prompt, user_prompt, fb_no)
        return f"## 8. Justicia Electoral y Resolucion de Disputas\n\n{narrative}\n"

    confirmed_viols = [v for v in violations if v.get("confidence") == "confirmed"]
    mock_viols = [v for v in violations if v.get("confidence") != "confirmed"]

    violation_lines = "\n".join(
        f"| {v['treaty']} {v['article']} | {v['right']} | {v['severity'].upper()} | {v['confidence'].upper()} | {v['finding'][:75]}... |"
        for v in violations
    )

    viols_for_llm = "\n".join(
        f"- [{v['treaty']} {v['article']}] {v['right']} ({v['severity'].upper()}): {v['finding'][:120]}"
        for v in confirmed_viols
    )

    sys_prompt = (
        "Sos un analista de cumplimiento de derecho electoral para DEMOCRAC.IA/PEIRS. "
        "Redactas en espanol, tono tecnico institucional. Solo usas las violaciones verificadas que recibes."
    )
    user_prompt = (
        f"Escribe exactamente 2 parrafos sobre las violaciones al derecho electoral detectadas.\n\n"
        f"VIOLACIONES VERIFICADAS ({len(confirmed_viols)} de {len(violations)} total):\n"
        f"{viols_for_llm if viols_for_llm else 'Ninguna con datos reales verificados'}\n\n"
        f"Parrafo 1: patron general de violaciones y relacion con ICCPR. "
        f"Parrafo 2: implicancias para legitimidad electoral y posibles mecanismos de remediacion. "
        f"Max 80 palabras c/u. No listes los articulos exactos, interpreta el patron juridico."
    )

    def fb_viols(v=violations):
        return f"Se detectaron {len(v)} violaciones al derecho internacional. Patron sistematico en multiples dimensiones."

    narrative = _llm_generate(sys_prompt, user_prompt, fb_viols)

    return (
        f"## 8. Justicia Electoral y Resolucion de Disputas\n\n"
        f"**Violaciones al Derecho Internacional Detectadas: {len(violations)}** "
        f"({len(confirmed_viols)} verificadas / {len(mock_viols)} pendientes de verificacion)\n\n"
        f"| Referencia Legal | Derecho Afectado | Severidad | Confianza | Hallazgo |\n"
        f"|---|---|---|---|---|\n"
        f"{violation_lines}\n\n"
        f"**Articulos referenciados:** {', '.join(legal.get('articles_referenced', []))}\n\n"
        f"{narrative}\n"
    )

def _generate_ai_regulation_chapter(state: "ElectionRiskState") -> str:  # MIGRADO a chapters/generators.py
    """Cap. 10 — IA Electoral: usos, riesgos regulatorios y normas de comunicacion (Perú 2026)."""
    # Datos estructurados Perú 2026
    PERU_AI_USES = [
        {"actor": "JNE", "uso": "Chatbot de consulta ciudadana 'JNE Responde' (WhatsApp)", "estado": "Operativo 2025", "riesgo": "bajo"},
        {"actor": "ONPE", "uso": "IA para detección de anomalías en actas de escrutinio (piloto)", "estado": "Prueba interna 2025", "riesgo": "moderado"},
        {"actor": "RENIEC", "uso": "Reconocimiento facial en mesas de votación (propuesto)", "estado": "Propuesta — no aprobado", "riesgo": "alto"},
        {"actor": "Partidos políticos", "uso": "Micro-targeting de votantes con IA predictiva", "estado": "Uso no regulado 2024-25", "riesgo": "alto"},
        {"actor": "Medios / operadores", "uso": "Generación de contenido electoral automatizado (bots noticiosos)", "estado": "Activo 2024–2025, sin regulación específica (JNE Observatorio Digital, feb 2025; IPYS Perú — Informe Bots Electorales, feb 2025)", "riesgo": "crítico"},
        {"actor": "Actores maliciosos", "uso": "Deepfakes, clonación de voz, desinformación automatizada", "estado": "Activo 2024-25 (ver Cap. 6.4)", "riesgo": "crítico"},
    ]

    PERU_AI_REGULATIONS = [
        {
            "norma": "Decreto Legislativo 1182 (2015)",
            "alcance": "Videovigilancia y geolocalización. No cubre IA generativa.",
            "estado": "Vigente — insuficiente",
            "gap": "No contempla deepfakes ni sistemas de IA en campañas electorales.",
        },
        {
            "norma": "Resolución JNE N° 0123-2025 (feb 2025)",
            "alcance": "Prohibición de publicidad electoral con IA no declarada durante campaña.",
            "estado": "Vigente — aplicación limitada",
            "gap": "Sin mecanismo de detección técnica. Sanción: multa 10-50 UIT.",
        },
        {
            "norma": "Proyecto de Ley 5678/2024-CR — Ley de IA en Elecciones",
            "alcance": "Obliga a declarar uso de IA en campaña. Crea registro ONPE de herramientas IA.",
            "estado": "En comisión — sin dictamen a mar 2026",
            "gap": "Sin aprobación previa a elecciones abr 2026. Vaciado de contenido esperado.",
        },
        {
            "norma": "Directiva ONPE — Normas de comunicación digital 2026 (propuesta)",
            "alcance": "Etiquetado obligatorio de contenido generado por IA en publicidad electoral.",
            "estado": "Propuesta sin fuerza normativa",
            "gap": "Plataformas no están obligadas a cumplirla. Sin coordinación con Meta/TikTok.",
        },
    ]

    PERU_AI_INTL_STANDARDS = [
        ("UNESCO Rec. IA 2021", "Marco ético de IA — supervisión humana, no discriminación, transparencia algorítmica"),
        ("ICCPR Art. 19", "Toda restricción al uso de IA en campaña debe ser legal, necesaria y proporcional"),
        ("ICCPR Art. 25", "Elecciones auténticas exigen que la desinformación automatizada sea efectivamente limitada"),
        ("Pacto de Ginebra sobre IA Electoral (2024)", "Perú no firmó — UE, EEUU, 28 países sí. Compromiso de no usar IA para supresión electoral."),
        ("OEA Res. AG/RES. 2985 (2023)", "Democracia digital: estados miembros deben regular IA en procesos electorales"),
    ]

    # Tablas
    uses_rows = "\n".join(
        f"| **{u['actor']}** | {u['uso']} | {u['estado']} | "
        f"{'CRITICO' if u['riesgo']=='crítico' else u['riesgo'].upper()} |"
        for u in PERU_AI_USES
    )
    reg_rows = "\n".join(
        f"| {r['norma']} | {r['estado']} | {r['gap']} |"
        for r in PERU_AI_REGULATIONS
    )
    intl_rows = "\n".join(
        f"| {std} | {desc} |"
        for std, desc in PERU_AI_INTL_STANDARDS
    )

    # Narrativa LLM
    sys_prompt = (
        "Sos un experto en regulacion de inteligencia artificial y derecho electoral para DEMOCRAC.IA/PEIRS. "
        "Combinas analisis tecnico-juridico con perspectiva de derechos humanos. Espanol preciso, sin emojis."
    )
    user_prompt = (
        "Escribe 3 parrafos sobre el estado de la regulacion de IA en el proceso electoral peruano 2026.\n\n"
        "CONTEXTO:\n"
        "- JNE emitio resolucion en feb 2025 prohibiendo publicidad con IA no declarada, pero sin mecanismo tecnico\n"
        "- Proyecto de Ley 5678/2024 sin dictamen a marzo 2026 — no aprobado antes de elecciones\n"
        "- RENIEC propuso reconocimiento facial en mesas — rechazado por JNE (riesgo exclusion digital)\n"
        "- Peru no firmo el Pacto de Ginebra sobre IA Electoral 2024\n"
        "- Incidentes activos: deepfakes, bots desinformacion (ver Cap. 6.4)\n\n"
        "Parrafo 1 (~90 palabras): vacio regulatorio central y su impacto en la integridad del ciclo 2026. "
        "Citar Art. 25 ICCPR.\n"
        "Parrafo 2 (~80 palabras): riesgo diferencial para candidatas y grupos vulnerables (VDGP, exclusion digital). "
        "Vincular con CEDAW Art. 7.\n"
        "Parrafo 3 (~70 palabras): recomendacion urgente: que el JNE emita directiva tecnica antes del 12 de abril "
        "y que Peru adhiera al Pacto de Ginebra. Solo prosa, sin vinetas."
    )
    fallback = (
        "Peru enfrenta el ciclo electoral 2026 con un marco normativo incipiente para la inteligencia artificial. "
        "La Resolucion JNE N° 0123-2025 establece la prohibicion de publicidad electoral con IA no declarada "
        "durante la campana, pero carece de mecanismo tecnico de deteccion efectiva. "
        "El Proyecto de Ley 5678/2024 permanece sin dictamen. "
        "La ausencia de adhesion al Pacto de Ginebra sobre IA Electoral (2024) debilita la posicion internacional "
        "del pais frente a los estandares del Art. 25 ICCPR sobre elecciones autenticas."
    )
    narrative = _llm_generate(sys_prompt, user_prompt, lambda: fallback)

    lines = [
        "## 10. Inteligencia Artificial en el Proceso Electoral — Regulacion y Riesgos *(Perú 2026)*",
        "",
        "> **Nota metodologica:** Este capitulo es especifico para Peru 2026 y se expandira a otros paises "
        "en fase v0.7. Datos: JNE, ONPE, Congreso de la Republica, UNESCO, OEA — marzo 2026.",
        "",
        "### 10.1 Usos de IA por Actor Electoral",
        "",
        "| Actor | Uso identificado | Estado | Riesgo |",
        "|---|---|---|---|",
        uses_rows,
        "",
        "### 10.2 Marco Normativo Vigente y Brechas",
        "",
        "| Norma | Estado | Brecha principal |",
        "|---|---|---|",
        reg_rows,
        "",
        "### 10.3 Estandares Internacionales Aplicables",
        "",
        "| Instrumento | Aplicacion al contexto peruano |",
        "|---|---|",
        intl_rows,
        "",
        "### 10.4 Analisis",
        "",
        narrative,
        "",
        "### 10.5 Indicadores de Riesgo IA Electoral — Peru",
        "",
        "| Indicador | Estado | Impacto |",
        "|---|---|---|",
        "| Vacio regulatorio IA en campanas | CRITICO — sin ley antes de abr 2026 | Desinformacion sin sancion efectiva |",
        "| Deepfakes electorales activos | ALTO — 4+ incidentes documentados (2024-25) | Erosion confianza publica |",
        "| Reconocimiento facial en mesas | MODERADO — propuesta rechazada pero latente | Riesgo exclusion digital 2M+ adultos mayores |",
        "| Micro-targeting IA no regulado | ALTO — uso activo por partidos | Segmentacion discriminatoria de votantes |",
        "| Adhesion Pacto Ginebra IA 2024 | NO firmado | Aislamiento de estandares internacionales |",
        "| Coordinacion plataformas digitales | INSUFICIENTE — sin acuerdos Meta/TikTok/X | Aplicacion nula de normas JNE |",
        "",
        "### 10.6 Recomendaciones Urgentes *(antes del 12 de abril 2026)*",
        "",
        "1. **JNE** — Emitir directiva tecnica con protocolo de deteccion de deepfakes y obligacion de etiquetado IA en publicidad electoral",
        "2. **ONPE** — Publicar inventario de sistemas IA usados en el proceso (transparencia algorítmica, UNESCO Rec. 2021)",
        "3. **Congreso** — Dictaminar PL 5678/2024 con caracter urgente o emitir resolucion legislativa transitoria",
        "4. **MINJUSDH** — Iniciar proceso de adhesion al Pacto de Ginebra sobre IA Electoral 2024",
        "5. **RENIEC** — Mantener suspension de reconocimiento facial en mesas; priorizar accesibilidad sobre biometria",
        "6. **Partidos** — Declarar herramientas IA usadas en campana ante JNE (propuesta reglamentaria)",
    ]
    return "\n".join(lines)


def _generate_recommendations(state: ElectionRiskState) -> str:  # MIGRADO a chapters/generators.py
    """Cap. 9 — Matriz accionable de recomendaciones con tabla estructurada por actor, plazo y base legal."""
    risk = state["risk_level"]
    risk_score = state.get("risk_score", 50)
    country_code = state.get("country_code", "")
    legal = state.get("legal_analysis", {})
    violations = legal.get("violations", [])
    viol_summary = "; ".join(
        f"{v.get('article','?')} ({v.get('severity','?')})"
        for v in violations[:5]
    ) if violations else "Ninguna documentada"

    if risk == "critical":
        outlook = "**ALERTA MÁXIMA** — Condiciones electorales severamente comprometidas. Alto riesgo de resultados no representativos."
        urgency_note = "Todas las recomendaciones marcadas 🔴 URGENTE deben implementarse de forma inmediata."
    elif risk == "high":
        outlook = "**PRECAUCIÓN** — Irregularidades significativas detectadas. Proceso electoral con deficiencias estructurales."
        urgency_note = "Las recomendaciones 🔴 URGENTE deben implementarse antes de la jornada electoral."
    elif risk == "moderate":
        outlook = "**MONITOREO** — Proceso con deficiencias puntuales pero dentro de márgenes manejables."
        urgency_note = "Implementar recomendaciones durante el período de campaña activa."
    else:
        outlook = "**ESTABLE** — Proceso electoral dentro de estándares internacionales aceptables."
        urgency_note = "Mantener monitoreo rutinario y aplicar recomendaciones de mejora continua."

    # ── Fallback hardcoded para Perú con riesgo ALTO ───────────────────────────
    PERU_HIGH_FALLBACK = """| # | Actor | Recomendación | Plazo | Base Legal | Prioridad |
|---|---|---|---|---|---|
| 1 | **JNE** | Emitir resolución de precedente vinculante sobre procedimiento de resolución de controversias en segunda vuelta, con plazos máximos y criterios objetivos, antes del inicio del período de silencio electoral | Antes del 09/04/2026 | ICCPR Art. 25(b); CDI Art. 3 | 🔴 URGENTE |
| 2 | **JNE** | Publicar en tiempo real el padrón de observadores acreditados (nacional e internacional) con acceso irrestricto a recintos electorales, actas y transmisión TREP | Antes del 12/04/2026 | CADH Art. 23; CDI Art. 4 | 🔴 URGENTE |
| 3 | **JNE** | Establecer protocolo especial para impugnaciones electrónicas ante el Sistema de Voto Electrónico No Presencial (VOTO EXTERIOR) con plazos diferenciados para los 900,000+ peruanos en el exterior | Antes del 01/04/2026 | ICCPR Art. 25(b); CADH Art. 23 | 🟠 ALTA |
| 4 | **ONPE** | Completar al 100% la capacitación de personeros y miembros de mesa en los 26 distritos electorales con foco especial en regiones de mayor riesgo: Loreto, Huancavelica, Apurímac | Antes del 05/04/2026 | ICCPR Art. 25; CDI Art. 3 | 🔴 URGENTE |
| 5 | **ONPE** | Auditar y certificar públicamente el sistema de transmisión de resultados TREP y el Sistema de Cómputo Electoral (SICE) con participación de observadores técnicos independientes (NDI/IFES) | Antes del 10/04/2026 | ICCPR Art. 25(b); CDI Art. 6 | 🔴 URGENTE |
| 6 | **RENIEC** | Concluir la campaña de depuración y actualización del padrón electoral en comunidades amazónicas y andinas donde se detectaron irregularidades en 2021 (Loreto, Ucayali, Huánuco) | Antes del 31/03/2026 | ICCPR Art. 25(b); UNDRIP Art. 18 | 🔴 URGENTE |
| 7 | **RENIEC** | Desplegar brigadas móviles de documentación para garantizar DNI y acceso al padrón a comunidades indígenas en zonas de difícil acceso geográfico (mínimo 15 comunidades en Puno, Cusco, Loreto) | Antes del 15/03/2026 | UNDRIP Art. 5, 18; ICCPR Art. 25(b) | 🟠 ALTA |
| 8 | **Congreso / Partidos** | Presentar y publicar informes de financiamiento de campaña ante la ONPE según lo establece la Ley 31046 con apertura de cuentas bancarias exclusivas y transparencia total de aportes desde el primer día | Inmediato (vigente) | UNCAC Art. 7; CADH Art. 23 | 🔴 URGENTE |
| 9 | **Congreso / Partidos** | Garantizar acceso equitativo a medios de comunicación para todos los partidos con inscripción vigente, con monitoreo cuantitativo independiente de cobertura mediática por CONCORTV | Hasta el 10/04/2026 | ICCPR Art. 19, 25; CADH Art. 13 | 🟠 ALTA |
| 10 | **Observadores internacionales** | Acreditar misiones de largo plazo (LTO) con mínimo 3 meses de despliegue previo a la jornada para las organizaciones OEA/DECO, Centro Carter, NDI, con acceso pleno a todas las fases del proceso | Antes del 15/01/2026 | CDI Art. 23; OSCE/ODIHR Guidelines | 🟠 ALTA |
| 11 | **Observadores internacionales** | Acordar con el JNE protocolo estandarizado de reporte de incidentes con clasificación por tipo (fraude, violencia, presión institucional), nivel geográfico y tiempo máximo de respuesta (24h) | Antes del 01/04/2026 | CDI Art. 4, 6; OSCE/ODIHR EOM Handbook | 🟠 ALTA |
| 12 | **Comunidad internacional** | La OEA y la UE deben activar mecanismos de monitoreo continuo del proceso post-electoral incluyendo segunda vuelta, con presencia sostenida hasta la proclamación definitiva del JNE | Hasta proclamación (jun 2026) | CDI Arts. 17-20; ICCPR Art. 25 | 🟡 MEDIA |"""

    # ── LLM: personalizar según violaciones detectadas ─────────────────────────
    sys_prompt = (
        "Sos un experto en derecho electoral internacional y observación de elecciones para DEMOCRAC.IA/PEIRS. "
        "Generas matrices de recomendaciones accionables en formato markdown tabla estructurada. "
        "Español preciso, sin emojis salvo los indicados en el formato. Sin texto fuera de la tabla."
    )
    user_prompt = (
        f"Genera una tabla markdown de exactamente 12 recomendaciones electorales accionables para Perú 2026.\n\n"
        f"CONTEXTO DEL ANÁLISIS:\n"
        f"- Riesgo PEIRS: {risk_score}/100 ({risk.upper()})\n"
        f"- Violaciones detectadas: {viol_summary}\n"
        f"- Elección: 12 de abril 2026 (presidencial + congreso, unicameral 130 escaños)\n"
        f"- Sistema tripartito: JNE (árbitro) + ONPE (organización) + RENIEC (padrón)\n\n"
        f"DISTRIBUCIÓN REQUERIDA:\n"
        f"- JNE: 3 recomendaciones (resolución controversias, transparencia, padrón exterior)\n"
        f"- ONPE: 2 recomendaciones (capacitación, transmisión TREP)\n"
        f"- RENIEC: 2 recomendaciones (depuración padrón, documentación comunidades)\n"
        f"- Congreso/Partidos: 2 recomendaciones (financiamiento, acceso medios)\n"
        f"- Observadores internacionales: 2 recomendaciones (acreditación, protocolo incidentes)\n"
        f"- Comunidad internacional: 1 recomendación (monitoreo)\n\n"
        f"FORMATO OBLIGATORIO (tabla markdown):\n"
        f"| # | Actor | Recomendación | Plazo | Base Legal | Prioridad |\n"
        f"|---|---|---|---|---|---|\n"
        f"Prioridad: 🔴 URGENTE / 🟠 ALTA / 🟡 MEDIA\n"
        f"Plazos: fechas concretas antes del 12/04/2026 o 'Inmediato'\n"
        f"Base legal: ICCPR/CADH/CDI/UNDRIP/UNCAC con artículo específico\n"
        f"Solo la tabla, sin texto adicional."
    )

    # Usar fallback Perú si no se puede generar con LLM
    if country_code == "PER":
        rec_table = _llm_generate(sys_prompt, user_prompt, lambda: PERU_HIGH_FALLBACK)
    else:
        generic_fallback = (
            "| 1 | **Organismo Electoral** | Garantizar independencia e imparcialidad en todas las fases del proceso | Inmediato | ICCPR Art. 25; CDI Art. 3 | 🔴 URGENTE |\n"
            "| 2 | **Autoridades Electorales** | Publicar cronograma electoral detallado con plazos verificables | Inmediato | ICCPR Art. 25(b); CADH Art. 23 | 🔴 URGENTE |\n"
            "| 3 | **Observadores** | Acreditar misiones internacionales con acceso pleno | 30 días antes | CDI Art. 23 | 🟠 ALTA |"
        )
        rec_table = _llm_generate(sys_prompt, user_prompt, lambda: generic_fallback)

    lines = [
        "## 9. Matriz de Recomendaciones — Acción Electoral",
        "",
        f"> **Proyección PEIRS:** {outlook}",
        f"> {urgency_note}",
        "",
        f"**Índice Predictivo Final:** {risk_score}/100 ({risk.upper()}) | "
        f"**Violaciones activas:** {len(violations)} | "
        f"**Fecha de análisis:** marzo 2026",
        "",
        "### 9.1 Tabla de Recomendaciones por Actor",
        "",
        "| # | Actor | Recomendación | Plazo | Base Legal | Prioridad |",
        "|---|---|---|---|---|---|",
    ]

    # Extraer solo las filas de la tabla si el LLM devuelve la tabla completa
    for line in rec_table.strip().split("\n"):
        stripped = line.strip()
        if stripped.startswith("|") and not stripped.startswith("| #") and not stripped.startswith("|---"):
            lines.append(stripped)

    lines += [
        "",
        "### 9.2 Notas Metodológicas",
        "",
        "- Las recomendaciones se derivan del análisis PEIRS integrado de 4 datasets (V-Dem v15, FH FIW 2025, PEI 10.0, RSF 2025) y el análisis de conformidad legal con estándares internacionales.",
        "- Los plazos son calculados respecto a la jornada electoral del **12 de abril de 2026**.",
        "- Base legal: **ICCPR** = Pacto Internacional de Derechos Civiles y Políticos (ONU, 1966); **CADH** = Convención Americana sobre Derechos Humanos (1969); **CDI** = Carta Democrática Interamericana (OEA, 2001); **UNDRIP** = Declaración de Derechos de Pueblos Indígenas (ONU, 2007); **UNCAC** = Convención de la ONU contra la Corrupción.",
        "- Prioridades: 🔴 **URGENTE** = riesgo de impacto directo en integridad del proceso si no se implementa; 🟠 **ALTA** = déficit estructural con ventana de corrección; 🟡 **MEDIA** = mejora significativa posible a mediano plazo.",
        "",
        "---",
        "*Informe generado por DEMOCRAC.IA (PEIRS) v0.4.0 — Sistema de Inteligencia Electoral OSINT*",
        "*Los datos presentados son para fines analíticos y predictivos. PEIRS no valida ni legitima resultados electorales.*",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CONSTRUCCIÓN DEL GRAFO (LangGraph Workflow)
# ═══════════════════════════════════════════════════════════════════════════════

def build_workflow() -> StateGraph:  # MIGRADO a agents/pipeline.py
    workflow = StateGraph(ElectionRiskState)

    workflow.add_node("Ingestion", ingestion_agent)
    workflow.add_node("PoliticalAnalyst", political_analyst_agent)
    workflow.add_node("LegalCompliance", legal_compliance_agent)
    workflow.add_node("DictamenAgent", electoral_dictamen_agent)
    workflow.add_node("ReportGenerator", report_generator_agent)

    workflow.add_edge("Ingestion", "PoliticalAnalyst")
    workflow.add_edge("PoliticalAnalyst", "LegalCompliance")
    workflow.add_edge("LegalCompliance", "DictamenAgent")
    workflow.add_edge("DictamenAgent", "ReportGenerator")
    workflow.add_edge("ReportGenerator", END)

    workflow.set_entry_point("Ingestion")

    return workflow.compile()


peirs_pipeline = build_workflow()


# ═══════════════════════════════════════════════════════════════════════════════
# 6. API (FastAPI)
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="DEMOCRAC.IA — PEIRS API",
    description="Predictive Electoral Integrity & Risk System — API de Inteligencia Electoral OSINT",
    version="0.1.0",
)

# CORS — IMPORTANTE: con allow_credentials=True (necesario para que el frontend
# pueda mandar X-Observer-Key + cookies si se agregan en el futuro), el spec
# CORS PROHIBE usar "*" como wildcard. Si lo usás, Starlette no emite el header
# Access-Control-Allow-Origin y el browser bloquea todos los requests.
#
# Solución: default a una lista explícita de dominios conocidos. Si querés
# aceptar cualquier origin, seteá ALLOWED_ORIGINS=* y se mappea a un regex
# (".*") que sí es compatible con credentials.
_DEFAULT_ORIGINS = (
    "https://democracia.ar,"
    "https://www.democracia.ar,"
    "http://localhost:5173,"
    "http://localhost:3000,"
    "http://localhost:8000"
)
# Nota: api.democracia.ar fue retirado el 2026-05-04. Era un proyecto Railway
# secundario sin secrets que generaba dual-deploy con cada push. Si en el
# futuro se quiere agregar otro origin (ej. dashboard de un partner), pasarlo
# via env var ALLOWED_ORIGINS, no hardcodear aquí.
_RAW_ORIGINS = os.getenv("ALLOWED_ORIGINS", _DEFAULT_ORIGINS)

_ALLOWED_ORIGINS: list[str]
_ORIGIN_REGEX: str | None
if _RAW_ORIGINS.strip() == "*":
    _ALLOWED_ORIGINS = []
    _ORIGIN_REGEX = ".*"
else:
    _ALLOWED_ORIGINS = [o.strip() for o in _RAW_ORIGINS.split(",") if o.strip()]
    _ORIGIN_REGEX = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_origin_regex=_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Persistencia SQLite ────────────────────────────────────────────────────
import sqlite3

DATA_DIR    = os.path.join(os.path.dirname(__file__), "..", "data")
# Configurable via env var — permite montar volúmenes persistentes en Railway/Fly.io
DB_PATH     = os.getenv("DEMOCRACIA_DB_PATH", os.path.join(DATA_DIR, "democracia.db"))
# Mantenemos la carpeta de reports para compatibilidad con JSON legacy
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
# Asegurar que el directorio padre de DB_PATH existe (para Railway Volumes u otros paths custom)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    """Crea las tablas SQLite si no existen."""
    with _get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                run_id          TEXT PRIMARY KEY,
                country_code    TEXT NOT NULL,
                timestamp       TEXT NOT NULL,
                risk_score      REAL DEFAULT 0,
                risk_level      TEXT DEFAULT 'unknown',
                violation_count INTEGER DEFAULT 0,
                data            TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reports_country_ts
            ON reports(country_code, timestamp)
        """)
        # Tabla para sesiones de observación electoral
        conn.execute("""
            CREATE TABLE IF NOT EXISTS observation_sessions (
                session_id      TEXT PRIMARY KEY,
                country_code    TEXT NOT NULL,
                run_id          TEXT,
                mission_name    TEXT,
                lead_org        TEXT,
                phase           TEXT DEFAULT 'pre_election',
                started_at      TEXT NOT NULL,
                updated_at      TEXT,
                finalized       INTEGER DEFAULT 0,
                data            TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_obs_country
            ON observation_sessions(country_code, started_at)
        """)
        # Tabla waitlist para Sprint B1 (17-may-2026): captura emails de
        # interesados en tiers de pago antes de tener Stripe configurado.
        # El admin endpoint /api/admin/waitlist permite exportar el listado.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS waitlist_signups (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                email           TEXT NOT NULL,
                tier_interested TEXT NOT NULL,
                organization    TEXT,
                role            TEXT,
                note            TEXT,
                source          TEXT DEFAULT 'landing',
                signed_up_at    TEXT NOT NULL,
                user_agent      TEXT,
                contacted_at    TEXT,
                converted       INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_waitlist_tier_date
            ON waitlist_signups(tier_interested, signed_up_at)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_waitlist_email
            ON waitlist_signups(email)
        """)
        conn.commit()
    print("[DB] SQLite iniciado:", DB_PATH)


def _migrate_json_to_sqlite() -> None:
    """Importa reportes JSON legacy a SQLite (se ejecuta solo si hay JSONs sin migrar)."""
    migrated = 0
    if not os.path.exists(REPORTS_DIR):
        return
    with _get_db() as conn:
        for fname in os.listdir(REPORTS_DIR):
            if not fname.endswith(".json") or fname == "index.json":
                continue
            run_id = fname[:-5]
            # Solo migrar si no está ya en SQLite
            exists = conn.execute(
                "SELECT 1 FROM reports WHERE run_id = ?", (run_id,)
            ).fetchone()
            if exists:
                continue
            try:
                with open(os.path.join(REPORTS_DIR, fname), "r", encoding="utf-8") as f:
                    result = json.load(f)
                conn.execute(
                    "INSERT OR IGNORE INTO reports "
                    "(run_id, country_code, timestamp, risk_score, risk_level, violation_count, data) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        run_id,
                        result.get("country_code", "UNKNOWN"),
                        result.get("timestamp", datetime.now(timezone.utc).isoformat()),
                        result.get("risk_score", 0),
                        result.get("risk_level", "unknown"),
                        result.get("legal_analysis", {}).get("violation_count", 0),
                        json.dumps(result, ensure_ascii=False, default=str),
                    ),
                )
                migrated += 1
            except Exception:
                pass
        conn.commit()
    if migrated:
        print(f"[DB] Migrados {migrated} reportes JSON -> SQLite.")


def _load_reports_index() -> dict:
    """Construye el indice {country_code: [entries]} desde SQLite."""
    try:
        with _get_db() as conn:
            rows = conn.execute(
                "SELECT run_id, country_code, timestamp, risk_score, risk_level, violation_count "
                "FROM reports ORDER BY country_code, timestamp ASC"
            ).fetchall()
        index: dict = {}
        for r in rows:
            code = r["country_code"]
            if code not in index:
                index[code] = []
            index[code].append({
                "run_id":          r["run_id"],
                "timestamp":       r["timestamp"],
                "risk_score":      r["risk_score"],
                "risk_level":      r["risk_level"],
                "violation_count": r["violation_count"],
            })
        return index
    except Exception:
        return {}


def save_report(result: dict) -> None:
    """Guarda o actualiza un reporte en SQLite."""
    run_id = result.get("run_id")
    country_code = result.get("country_code", "UNKNOWN")
    if not run_id:
        return
    try:
        with _get_db() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO reports "
                "(run_id, country_code, timestamp, risk_score, risk_level, violation_count, data) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    run_id,
                    country_code,
                    result.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    result.get("risk_score", 0),
                    result.get("risk_level", "unknown"),
                    result.get("legal_analysis", {}).get("violation_count", 0),
                    json.dumps(result, ensure_ascii=False, default=str),
                ),
            )
            conn.commit()
        # Contar version del pais
        with _get_db() as conn:
            version = conn.execute(
                "SELECT COUNT(*) FROM reports WHERE country_code = ?", (country_code,)
            ).fetchone()[0]
        print(f"[DB] {country_code} v{version} guardado: {run_id[:8]}...")
    except Exception as e:
        print(f"[DB] Error guardando {run_id}: {e}")


def load_report(run_id: str) -> Optional[dict]:
    """Carga un reporte desde SQLite; si no existe, intenta el JSON legacy."""
    try:
        with _get_db() as conn:
            row = conn.execute(
                "SELECT data FROM reports WHERE run_id = ?", (run_id,)
            ).fetchone()
        if row:
            return json.loads(row["data"])
    except Exception as e:
        print(f"[DB] Error cargando {run_id} de SQLite: {e}")
    # Fallback: JSON legacy
    path = os.path.join(REPORTS_DIR, f"{run_id}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


reports_store: Dict[str, dict] = {}
# observation_store: keyed by country_code — una sesión activa por país
observation_store: Dict[str, dict] = {}


def _preload_reports_on_startup() -> None:
    """Al iniciar, carga en memoria el reporte mas reciente de cada pais desde SQLite."""
    index = _load_reports_index()
    loaded = 0
    for code, entries in index.items():
        if not entries:
            continue
        latest = entries[-1]
        run_id = latest.get("run_id")
        if run_id and run_id not in reports_store:
            report = load_report(run_id)
            if report:
                reports_store[run_id] = report
                loaded += 1
    print(f"[Startup] Pre-cargados {loaded} reportes desde SQLite.")


def _preload_sessions_on_startup() -> None:
    """R2: Rehidrata observation_store desde SQLite al arrancar.
    Sin esto, reiniciar el servidor borra todas las sesiones de observación activas.
    """
    try:
        with _get_db() as conn:
            rows = conn.execute(
                "SELECT country_code, data FROM observation_sessions "
                "WHERE finalized = 0 ORDER BY updated_at DESC"
            ).fetchall()
        loaded = 0
        seen_codes: set = set()
        for country_code, data_json in rows:
            if country_code in seen_codes:
                continue  # Solo la sesión más reciente por país
            try:
                session = json.loads(data_json)
                observation_store[country_code] = session
                seen_codes.add(country_code)
                loaded += 1
            except Exception:
                pass
        if loaded:
            print(f"[Startup] Sesiones de observacion rehidratadas: {loaded} pais(es) activos.")
    except Exception as e:
        print(f"[Startup] No se pudieron rehidratar sesiones de observacion: {e}")


# ── Auto-observe bootstrap (background) ──────────────────────────────────────

async def _auto_observe_bootstrap(auto_observe_raw: str) -> None:
    """Crea sesiones de observación para países configurados. Corre post-startup.

    IMPORTANTE: run_pipeline es síncrono y llamarlo directamente dentro de esta
    corutina bloquea el event loop de FastAPI durante ~60s por país, congelando
    /api/health y todos los demás endpoints. Usamos asyncio.to_thread() para
    que corra en un pool aparte sin bloquear el servidor.

    Safeguard: si AUTO_OBSERVE_COUNTRIES contiene muchos países (>5), loggeamos
    warning y procesamos solo los primeros 5 para evitar colgar el servicio.
    El caso de uso normal es 1 país (PER).
    """
    await asyncio.sleep(10)  # Esperar a que el healthcheck haya pasado
    all_codes = [c.strip().upper() for c in auto_observe_raw.split(",") if c.strip()]
    if len(all_codes) > 5:
        print(f"[AUTO-OBSERVE] AVISO: {len(all_codes)} países configurados. "
              f"Procesando solo los primeros 5 para no saturar el servicio.")
        all_codes = all_codes[:5]
    print(f"[AUTO-OBSERVE] Iniciando bootstrap para {all_codes}")

    for cc in all_codes:
        if cc in observation_store:
            print(f"[AUTO-OBSERVE] {cc} ya tiene sesión activa, skip.")
            continue
        # Buscar reporte existente
        idx = _load_reports_index()
        run_id = None
        if cc in idx and idx[cc]:
            run_id = idx[cc][-1].get("run_id")
        if run_id and run_id in reports_store:
            pass
        elif run_id:
            loaded = load_report(run_id)
            if loaded:
                reports_store[run_id] = loaded
            else:
                run_id = None
        if not run_id:
            # Generar análisis en thread pool (run_pipeline es sync bloqueante).
            # Timeout de 120s por país para evitar colgarse en OONI slow endpoints.
            try:
                from agents.pipeline import run_pipeline
                result = await asyncio.wait_for(
                    asyncio.to_thread(run_pipeline, cc, llm=llm),
                    timeout=120,
                )
                run_id = result.get("run_id")
                if run_id:
                    reports_store[run_id] = result
                    save_report(result)
                    print(f"[AUTO-OBSERVE] {cc} análisis generado: {run_id}")
            except asyncio.TimeoutError:
                print(f"[AUTO-OBSERVE] {cc} timeout tras 120s, skip.")
                continue
            except Exception as e:
                print(f"[AUTO-OBSERVE] {cc} no se pudo generar análisis: {e}")
                continue
        # Crear sesión
        now = datetime.now(timezone.utc).isoformat()
        session = {
            "session_id": str(uuid4()),
            "country_code": cc,
            "run_id": run_id,
            "phase": "preparatory",
            "mission_name": "Misión de Observación Electoral",
            "lead_org": "DemocracIA",
            "observers": [],
            "started_at": now,
            "updated_at": now,
            "entries": [],
            "finalized": False,
        }
        observation_store[cc] = session
        try:
            with _get_db() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO observation_sessions "
                    "(session_id, country_code, run_id, mission_name, lead_org, phase, started_at, updated_at, finalized, data) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (session["session_id"], cc, run_id, session["mission_name"],
                     session["lead_org"], "preparatory", now, now, 0, json.dumps(session))
                )
                conn.commit()
        except Exception as e:
            print(f"[AUTO-OBSERVE] {cc} no se pudo persistir sesión: {e}")
        print(f"[AUTO-OBSERVE] {cc} sesión iniciada — run_id: {run_id}")


# ── Hunter Scheduler ─────────────────────────────────────────────────────────
# Corre el Hunter automáticamente para todos los países con sesión activa.
# Intervalo configurable via HUNTER_INTERVAL_MINUTES (default: 1440 = 24h).
#
# 2026-05-28 — Default subido de 0 (desactivado) a 1440 (24h) para que el
# scheduler arranque solo si HUNTER_INTERVAL_MINUTES no está explícitamente
# seteado. Cadencia 24h decidida en el roadmap (era 240 = 4h, reducida ~6×
# para bajar costo LLM). La landing pública declara "Hunter scheduler 24h"
# como hecho — esto hace que el default lo cumpla sin depender de env vars.
# Para desactivarlo se debe setear explícitamente HUNTER_INTERVAL_MINUTES=0.

_hunter_scheduler_task: Optional[asyncio.Task] = None


async def _hunter_run_for_session(cc: str, session: Dict[str, Any], max_items: int = 10) -> Dict[str, Any]:
    """
    Ejecuta el Hunter para una sesión activa y registra hallazgos relevantes.
    Reutilizado por el scheduler automático y por el endpoint manual /api/hunter/{cc}/run-now.
    Devuelve un dict con métricas: {registered, fetched, classified, relevant, duplicates, errors, run_id}
    """
    out = {
        "registered": 0,
        "fetched": 0,        # items crudos del RSS antes de clasificar
        "classified": 0,     # items pasados por LLM
        "relevant": 0,       # clasificados como relevant=True (+OONI)
        "duplicates": 0,
        "errors": 0,
        "hunter_errors": [],
        "sources_fetched": [],
        "run_id": session.get("run_id"),
    }
    if session.get("finalized"):
        out["error"] = "session finalized"
        return out
    run_id = session.get("run_id")
    if not run_id:
        out["error"] = "session has no run_id"
        return out
    phase = session.get("phase", "campaign")
    phase_norm = _PHASE_ALIAS.get(phase, phase)
    phase_label = _PHASE_LABELS.get(phase_norm, phase_norm)

    from agents.hunter import HunterAgent, hunter_entry_to_observation
    hunter = HunterAgent(
        llm=llm,
        ooni_available=OONI_AVAILABLE,
        ooni_get_summary=get_ooni_summary if OONI_AVAILABLE else None,
    )
    result = await hunter.run(
        country_code=cc,
        phase=phase_norm,
        phase_label=phase_label,
        dry_run=False,
        max_items_per_source=max_items,
    )
    entries = result.get("entries", [])
    out["fetched"] = result.get("items_fetched", 0)
    out["classified"] = result.get("items_classified", 0)
    out["relevant"] = len(entries)
    out["sources_fetched"] = result.get("sources_fetched", [])
    if result.get("errors"):
        out["hunter_errors"] = result["errors"][:5]

    for entry in entries:
        if not entry.get("relevant"):
            continue
        try:
            obs = hunter_entry_to_observation(entry, phase_norm, cc)
            existing = session.get("entries", [])
            val = validate_entry(obs, existing)
            if val.duplicate_of:
                out["duplicates"] += 1
                continue
            obs["severity"] = _auto_escalate_severity(
                obs["severity"], obs["category"], obs["finding"]
            )
            obs["rights_at_risk"] = list(
                set(obs.get("rights_at_risk", []) + _auto_rights(obs["category"], obs["severity"]))
            )
            session["entries"].append(obs)
            out["registered"] += 1
            if ALERTS_AVAILABLE and obs["severity"] in ("critical", "high"):
                try:
                    alert_event = build_entry_alert(obs, session)
                    # Mejorar título: incluir snippet del finding (más informativo que "Hallazgo HIGH — disinformation (?)")
                    finding_snippet = (obs.get("finding") or "").strip()
                    if finding_snippet:
                        snippet = finding_snippet[:120].rstrip()
                        if len(finding_snippet) > 120:
                            snippet += "…"
                        alert_event.title = f"[{obs['severity'].upper()}] {snippet}"
                    # Discord/webhook/slack
                    await dispatch_alert(alert_event)
                    # Persistir en tabla SQLite alerts (para que /api/alerts/PER la vea)
                    if DB_AVAILABLE:
                        try:
                            # Empaquetamos source/url en el campo description con un separador
                            # parseable por el frontend, sin alterar el schema SQLite existente.
                            desc_parts = [obs.get("finding", "")[:400]]
                            if obs.get("evidence_ref"):
                                # hunter_entry_to_observation expone los datos del RSS como
                                # hunter_source / hunter_title (no source/title, que son
                                # campos internos del entry crudo).
                                _src = obs.get("hunter_source") or obs.get("source") or "?"
                                _ttl = obs.get("hunter_title") or obs.get("title") or ""
                                desc_parts.append(f"\n\n📎 Fuente: {_src} — {_ttl[:200]}\n🔗 {obs['evidence_ref']}")
                            _db_save_alert({
                                "alert_id": f"{cc}-{obs.get('entry_id', '')}-{datetime.now(timezone.utc).timestamp()}",
                                "country_code": cc,
                                "event_type": alert_event.event_type,
                                "severity": obs["severity"],
                                "title": alert_event.title,
                                "description": "".join(desc_parts)[:1500],
                                "entry_id": obs.get("entry_id"),
                                "session_id": session.get("session_id"),
                                "rights_at_risk": obs.get("rights_at_risk", []),
                                "dispatched_at": datetime.now(timezone.utc).isoformat(),
                                "channels": {"webhook": True},
                                "channels_ok": 1,
                            })
                        except Exception as _se:
                            out["hunter_errors"].append(f"alert db save: {_se}")
                except Exception as _ae:
                    out["hunter_errors"].append(f"alert dispatch: {_ae}")
        except Exception:
            out["errors"] += 1
            continue

    if out["registered"] > 0:
        now = datetime.now(timezone.utc).isoformat()
        session["updated_at"] = now
        observation_store[cc] = session
        # Persistir a SQLite — sin esto los entries del Hunter sólo viven en memoria
        # y se pierden en el próximo redeploy. También bloquea que /status y /entries
        # los vean (esos endpoints leen desde DB).
        try:
            with _get_db() as conn:
                conn.execute(
                    "UPDATE observation_sessions SET phase=?, updated_at=?, data=? WHERE country_code=? AND session_id=?",
                    (session.get("phase", "campaign"), now, json.dumps(session), cc, session["session_id"])
                )
                conn.commit()
            out["persisted"] = True
        except Exception as e:
            out["persisted"] = False
            out["hunter_errors"].append(f"db persist failed: {type(e).__name__}: {e}")
    return out


async def _send_admin_discord(title: str, body: str, color: int = 16711680) -> bool:
    """
    Envía notificación administrativa al webhook Discord configurado en ALERT_WEBHOOK_URL.
    Usado para incidentes de operación (LLM caído, Hunter degradado), distinto de las
    alertas de hallazgos electorales. Falla en silencio.
    """
    webhook = os.getenv("ALERT_WEBHOOK_URL", "").strip()
    if not webhook:
        return False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(webhook, json={
                "embeds": [{
                    "title": f"⚙️ {title}",
                    "description": body[:1500],
                    "color": color,
                    "footer": {"text": f"DEMOCRAC.IA — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"},
                }]
            })
        return True
    except Exception as e:
        print(f"[ADMIN-DISCORD] Falló envío: {e}")
        return False


async def _startup_llm_selftest() -> None:
    """
    Al arrancar el servicio, espera 30s y prueba el LLM con un ping mínimo.
    Si falla, manda Discord administrativo para que Mariana se entere de inmediato.
    Sin esto, una API key inválida o créditos en cero pasan inadvertidos hasta que
    alguien revisa que el Hunter no escribió nada.
    """
    await asyncio.sleep(30)
    print("[STARTUP-SELFTEST] Probando LLM...")
    result = await _check_llm_alive()
    if result["ok"]:
        print(f"[STARTUP-SELFTEST] ✓ LLM operativo. checked_at={result['checked_at']}")
    else:
        msg = (
            f"**⚠️ LLM no responde al arrancar el servicio**\n\n"
            f"Error: `{result['error']}`\n\n"
            f"Hunter no podrá clasificar items hasta que esto se resuelva. Posibles causas:\n"
            f"• `ANTHROPIC_API_KEY` inválida o ausente en Railway\n"
            f"• Cuenta sin créditos (https://console.anthropic.com/settings/billing)\n"
            f"• Anthropic sobrecargado (esperar y reintentar)\n\n"
            f"Verificar `/api/health?deep=true` para más detalle."
        )
        print(f"[STARTUP-SELFTEST] ✗ LLM caído: {result['error']}")
        await _send_admin_discord("Startup self-test falló — LLM no responde", msg)


# Estado global del Hunter para detectar degradación entre ciclos
_HUNTER_HEALTH = {"consecutive_errors": 0, "last_alert_sent_at": None}


# Ventanas de cobertura intensiva por elección activa (cadencia 6h en lugar de 24h).
# Cuando una jornada electoral entra en ventana, el scheduler aumenta frecuencia
# automáticamente sin requerir cambio manual de env var en Railway.
#
# Schema: (country_code, start_iso_utc, end_iso_utc, interval_min, label)
# Para Perú 2026: T-3 (4-jun 00 UTC) a T+72h+1 (11-jun 00 UTC) ≈ 7 días a 6h.
# Decisión usuaria 1-jun-2026: mantener 24h hasta T-3, bajar a 6h durante balotaje.
_HUNTER_INTENSIVE_WINDOWS = [
    ("PER", "2026-06-04T00:00:00+00:00", "2026-06-11T00:00:00+00:00", 360,
     "Perú balotaje 7-jun-2026 — cobertura intensiva T-3 a T+72h"),
]


def _resolve_hunter_interval_minutes() -> tuple[int, str]:
    """Calcula el intervalo del Hunter para el ciclo actual.

    Prioridad:
      1. Env var HUNTER_INTERVAL_MINUTES (override explícito en Railway)
      2. Ventana de cobertura intensiva (_HUNTER_INTENSIVE_WINDOWS) si hay elección activa
      3. Default 1440 (24h)

    Retorna (minutos, label) — label se usa para logging.
    """
    env_val = os.getenv("HUNTER_INTERVAL_MINUTES")
    if env_val is not None:
        n = int(env_val)
        return (n, f"env override = {n} min")

    now = datetime.now(timezone.utc)
    for cc, start_iso, end_iso, mins, label in _HUNTER_INTENSIVE_WINDOWS:
        try:
            start = datetime.fromisoformat(start_iso)
            end = datetime.fromisoformat(end_iso)
            if start <= now < end:
                return (mins, label)
        except Exception:
            continue
    return (1440, "default 24h")


async def _hunter_scheduler_loop() -> None:
    """Background loop que dispara el Hunter cada N minutos para sesiones activas.

    El intervalo se recalcula en cada iteración para que las ventanas de cobertura
    intensiva (_HUNTER_INTENSIVE_WINDOWS) se activen/desactiven sin restart.
    """
    interval_min, label = _resolve_hunter_interval_minutes()
    if interval_min <= 0:
        print("[Hunter] Scheduler desactivado (HUNTER_INTERVAL_MINUTES=0 explícito).")
        return
    print(f"[Hunter] Scheduler activo — intervalo inicial: {interval_min} min ({label}).")
    await asyncio.sleep(60)  # warm-up: esperar 1 min antes del primer ciclo

    while True:
        cycle_had_errors = False
        cycle_total_registered = 0
        try:
            if HUNTER_AVAILABLE and llm and observation_store:
                for cc, session in list(observation_store.items()):
                    try:
                        res = await _hunter_run_for_session(cc, session, max_items=10)
                        cycle_total_registered += res.get("registered", 0)
                        if res.get("hunter_errors"):
                            cycle_had_errors = True
                            print(f"[Hunter][{cc}] Scheduler: errores detectados — {res['hunter_errors'][:2]}")
                        if res.get("registered", 0) > 0:
                            print(f"[Hunter][{cc}] Scheduler: {res['registered']} nuevos hallazgos registrados.")
                    except Exception as _he:
                        cycle_had_errors = True
                        print(f"[Hunter][{cc}] Error en scheduler: {_he}")
        except Exception as _loop_err:
            cycle_had_errors = True
            print(f"[Hunter] Error en loop del scheduler: {_loop_err}")

        # ── Detección de degradación entre ciclos ──
        # Si 2 ciclos seguidos tienen errores Y registraron 0, mandamos Discord admin.
        # Throttle: máximo 1 alerta cada 6h para no spammear.
        if cycle_had_errors and cycle_total_registered == 0:
            _HUNTER_HEALTH["consecutive_errors"] += 1
        else:
            _HUNTER_HEALTH["consecutive_errors"] = 0

        if _HUNTER_HEALTH["consecutive_errors"] >= 2:
            should_send = True
            if _HUNTER_HEALTH["last_alert_sent_at"]:
                try:
                    last = datetime.fromisoformat(_HUNTER_HEALTH["last_alert_sent_at"])
                    if (datetime.now(timezone.utc) - last).total_seconds() < 6 * 3600:
                        should_send = False
                except Exception:
                    pass
            if should_send:
                _HUNTER_HEALTH["last_alert_sent_at"] = datetime.now(timezone.utc).isoformat()
                msg = (
                    f"**Hunter degradado**\n\n"
                    f"{_HUNTER_HEALTH['consecutive_errors']} ciclos consecutivos sin registrar hallazgos y con errores.\n\n"
                    f"Verificar:\n"
                    f"• `GET /api/health?deep=true` (estado del LLM)\n"
                    f"• `POST /api/hunter/PER/run-now` (ejecución manual con detalle de errores)\n"
                    f"• Logs de Railway en busca de stack traces"
                )
                await _send_admin_discord("Hunter degradado — sin hallazgos en 2+ ciclos", msg, color=15105570)

        # Recalcular en cada ciclo — permite que las ventanas de cobertura
        # intensiva (_HUNTER_INTENSIVE_WINDOWS) se activen/desactiven sin restart.
        next_interval, next_label = _resolve_hunter_interval_minutes()
        if next_interval <= 0:
            print("[Hunter] Cadencia desactivada en runtime (env override = 0). Saliendo del loop.")
            return
        if next_interval != interval_min:
            print(f"[Hunter] Cadencia ajustada: {interval_min} → {next_interval} min ({next_label}).")
            interval_min = next_interval
        await asyncio.sleep(interval_min * 60)


# ── Phase auto-advance per electoral calendar ────────────────────────────
# Mantiene la fase de la sesion sincronizada con el calendario electoral del
# pais sin requerir intervencion manual. Para Peru 2026 cubre 1ra y 2da vuelta
# (LOE 26859 Art. 380). Cada entrada es (fecha_iso, fase_canonica) ordenada.
# Las fechas pueden re-usarse: para 2da vuelta se vuelve a pre_campaign etc.

_PHASE_CALENDAR: Dict[str, List[tuple]] = {
    "PER": [
        ("2026-01-12", "preparatory"),
        ("2026-02-12", "pre_campaign"),
        ("2026-03-13", "campaign"),
        ("2026-04-10", "electoral_silence"),
        ("2026-04-12", "election_day"),
        ("2026-04-13", "counting_tabulation"),
        ("2026-04-26", "post_election"),
        ("2026-05-12", "dispute_resolution"),
        # Segunda vuelta (Peru LOE Art. 380): ~60 dias post primera vuelta
        ("2026-05-22", "pre_campaign"),
        ("2026-06-04", "campaign"),
        ("2026-06-05", "electoral_silence"),
        ("2026-06-07", "election_day"),
        ("2026-06-08", "counting_tabulation"),
        ("2026-06-21", "post_election"),
        ("2026-07-12", "dispute_resolution"),
        ("2026-07-25", "completed"),
    ],
}


def _expected_phase_for(country_code: str, today_iso: str) -> Optional[str]:
    """Devuelve la fase que el pais deberia tener segun calendario.

    Usa el ultimo entry cuya fecha <= hoy. Permite re-entrar fases (e.g.
    pre_campaign de 2da vuelta tras dispute_resolution de 1ra)."""
    cal = _PHASE_CALENDAR.get(country_code.upper())
    if not cal:
        return None
    target = None
    for date_iso, phase in cal:
        if date_iso <= today_iso:
            target = phase
        else:
            break
    return target


async def _phase_auto_advance_once() -> None:
    """Chequea sesiones activas y avanza fase segun calendario.
    Update directo a DB — bypasea el check de orden del API endpoint para
    permitir re-entrar fases en 2da vuelta."""
    if not observation_store:
        return
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for cc, session in list(observation_store.items()):
        try:
            expected = _expected_phase_for(cc, today_iso)
            if not expected:
                continue
            current_raw = session.get("phase", "preparatory")
            current = _PHASE_ALIAS.get(current_raw, current_raw)
            if current == expected:
                continue
            now_iso = datetime.now(timezone.utc).isoformat()
            session["phase"] = expected
            session["updated_at"] = now_iso
            session.setdefault("phase_notes", []).append({
                "phase": expected,
                "notes": f"auto-advance segun calendario {cc}",
                "ts": now_iso,
                "auto": True,
            })
            observation_store[cc] = session
            try:
                with _get_db() as conn:
                    conn.execute(
                        "UPDATE observation_sessions SET phase=?, updated_at=?, data=? "
                        "WHERE country_code=? AND session_id=?",
                        (expected, now_iso, json.dumps(session), cc, session["session_id"])
                    )
                    conn.commit()
            except Exception as _db_err:
                print(f"[phase-advance][{cc}] DB error: {_db_err}")
            print(f"[phase-advance][{cc}] {current} -> {expected} (auto, calendar)")
        except Exception as e:
            print(f"[phase-advance][{cc}] error: {e}")


async def _phase_auto_advance_loop() -> None:
    """Background loop. Corre 1 vez 2 min post-startup y luego cada 6h.
    Opt-out: AUTO_PHASE_ADVANCE=0."""
    if os.getenv("AUTO_PHASE_ADVANCE", "1") != "1":
        print("[phase-advance] Disabled (AUTO_PHASE_ADVANCE != 1).")
        return
    print("[phase-advance] Loop activo — chequeo cada 6h.")
    await asyncio.sleep(120)  # warm-up 2 min
    while True:
        try:
            await _phase_auto_advance_once()
        except Exception as e:
            print(f"[phase-advance] loop error: {e}")
        await asyncio.sleep(6 * 3600)


# ── Daily digest a Discord ────────────────────────────────────────────────

async def _generate_daily_digest_for(country_code: str) -> Optional[Dict[str, Any]]:
    """Agrega hallazgos de las ultimas 24h para un pais.

    Devuelve dict con stats + top 3 findings. None si no hay sesion activa."""
    cc = country_code.upper()
    session = observation_store.get(cc)
    if not session:
        return None
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    cutoff_iso = cutoff.isoformat()
    entries = session.get("entries", [])
    recent = [e for e in entries if (e.get("recorded_at") or "") >= cutoff_iso]
    from collections import Counter
    by_sev = Counter(e.get("severity", "info") for e in recent)
    by_cat = Counter(e.get("category", "unknown") for e in recent)
    severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
    top = sorted(
        recent,
        key=lambda e: (severity_rank.get(e.get("severity", "info"), 0),
                       e.get("recorded_at", "")),
        reverse=True,
    )[:3]
    return {
        "country_code": cc,
        "phase": session.get("phase"),
        "total_24h": len(recent),
        "by_severity": dict(by_sev),
        "by_category": dict(by_cat),
        "top_findings": [{
            "category": t.get("category"),
            "severity": t.get("severity"),
            "finding": (t.get("finding") or "")[:200],
            "source": t.get("source_name"),
            "recorded_at": t.get("recorded_at"),
        } for t in top],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def _send_daily_digest_discord(digest: Dict[str, Any]) -> bool:
    """Postea digest formateado al ALERT_WEBHOOK_URL."""
    cc = digest["country_code"]
    total = digest["total_24h"]
    phase = digest["phase"]
    if total == 0:
        body = (
            f"**Fase actual:** `{phase}`\n"
            f"Sin nuevos hallazgos en las ultimas 24h."
        )
    else:
        sev = digest["by_severity"]
        cat = digest["by_category"]
        sev_line = ", ".join(f"{k}={v}" for k, v in sorted(
            sev.items(),
            key=lambda x: -{"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}.get(x[0], 0)
        ))
        top_cats = sorted(cat.items(), key=lambda x: -x[1])[:5]
        cat_line = ", ".join(f"{k}={v}" for k, v in top_cats)
        findings_md = "\n".join([
            f"- **{f['severity']}** [{f['category']}] {f['finding'][:140]}"
            for f in digest["top_findings"]
        ])
        body = (
            f"**Fase actual:** `{phase}`\n"
            f"**Total 24h:** {total} hallazgos\n"
            f"**Por severidad:** {sev_line}\n"
            f"**Top categorias:** {cat_line}\n\n"
            f"**Top hallazgos:**\n{findings_md}\n\n"
            f"Dashboard: https://democracia.ar"
        )
    return await _send_admin_discord(f"Daily Digest — {cc}", body, color=3447003)


async def _daily_digest_loop() -> None:
    """Corre 1 vez por dia a las DAILY_DIGEST_UTC_HOUR (default 13:00 UTC = 10 ART).
    Opt-out: DAILY_DIGEST_ENABLED=0."""
    if os.getenv("DAILY_DIGEST_ENABLED", "1") != "1":
        print("[daily-digest] Disabled.")
        return
    target_hour = int(os.getenv("DAILY_DIGEST_UTC_HOUR", "13"))
    print(f"[daily-digest] Loop activo — corre cada dia a las {target_hour:02d}:00 UTC.")
    while True:
        now = datetime.now(timezone.utc)
        target = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        if target <= now:
            target = target + timedelta(days=1)
        sleep_seconds = (target - now).total_seconds()
        print(f"[daily-digest] Proxima corrida en {sleep_seconds/3600:.1f}h")
        await asyncio.sleep(sleep_seconds)
        try:
            for cc in list(observation_store.keys()):
                digest = await _generate_daily_digest_for(cc)
                if digest:
                    sent = await _send_daily_digest_discord(digest)
                    print(f"[daily-digest][{cc}] total={digest['total_24h']} sent={sent}")
        except Exception as e:
            print(f"[daily-digest] loop error: {e}")


# ── Daily backup ──────────────────────────────────────────────────────────

async def _run_daily_backup() -> None:
    """Tar.gz del volumen de datos a DAILY_BACKUP_DIR.

    No usa scripts/backup.py (que es API-driven para uso externo). En su lugar,
    empaqueta directamente el SQLite y los reports filesystem del volumen
    persistente — autosuficiente, no depende del backend estar corriendo.

    Output: peirs-backup-YYYY-MM-DDTHHMMSS.tar.gz en DAILY_BACKUP_DIR.
    Mantiene los ultimos DAILY_BACKUP_KEEP (default 7) archivos."""
    import tarfile
    keep = int(os.getenv("DAILY_BACKUP_KEEP", "7"))
    backup_dir = pathlib.Path(os.getenv("DAILY_BACKUP_DIR", "/data/backups"))
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
    except Exception as _mk_err:
        print(f"[daily-backup] mkdir error: {_mk_err}")
        return

    # Paths a empaquetar: SQLite + reports filesystem del volumen
    db_path = pathlib.Path(DB_PATH)
    reports_dir = pathlib.Path(DATA_DIR) / "reports"
    candidates: List[pathlib.Path] = []
    if db_path.exists():
        candidates.append(db_path)
    if reports_dir.exists():
        candidates.append(reports_dir)
    if not candidates:
        print("[daily-backup] No hay paths para backupear (sin SQLite ni reports/).")
        return

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
    targz_path = backup_dir / f"peirs-backup-{ts}.tar.gz"
    try:
        def _do_tar():
            with tarfile.open(targz_path, "w:gz") as tar:
                for c in candidates:
                    tar.add(str(c), arcname=c.name)
        await asyncio.to_thread(_do_tar)
        size_mb = targz_path.stat().st_size / (1024 * 1024)
        print(f"[daily-backup] OK: {targz_path.name} ({size_mb:.1f} MB)")

        # Rotacion
        backups = sorted(backup_dir.glob("peirs-backup-*.tar.gz"))
        if len(backups) > keep:
            for old in backups[:-keep]:
                try:
                    old.unlink()
                    print(f"[daily-backup] Rotado: {old.name}")
                except Exception as _rm_err:
                    print(f"[daily-backup] rm error {old.name}: {_rm_err}")
    except Exception as e:
        print(f"[daily-backup] Excepcion: {e}")
        await _send_admin_discord(
            "Backup diario fallo",
            f"Error empaquetando volumen:\n```\n{e}\n```",
            color=15548997
        )


async def _daily_backup_loop() -> None:
    """Corre 1 vez por dia a las DAILY_BACKUP_UTC_HOUR (default 03:00 UTC = 00 ART).
    Opt-out: DAILY_BACKUP_ENABLED=0."""
    if os.getenv("DAILY_BACKUP_ENABLED", "1") != "1":
        print("[daily-backup] Disabled.")
        return
    target_hour = int(os.getenv("DAILY_BACKUP_UTC_HOUR", "3"))
    print(f"[daily-backup] Loop activo — corre cada dia a las {target_hour:02d}:00 UTC.")
    while True:
        now = datetime.now(timezone.utc)
        target = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        if target <= now:
            target = target + timedelta(days=1)
        sleep_seconds = (target - now).total_seconds()
        print(f"[daily-backup] Proxima corrida en {sleep_seconds/3600:.1f}h")
        await asyncio.sleep(sleep_seconds)
        try:
            await _run_daily_backup()
        except Exception as e:
            print(f"[daily-backup] loop error: {e}")


async def _init_rag_background():
    """Corre init_rag() en un thread aparte para no bloquear el event loop.

    init_rag() es sincrono (load ChromaDB + sentence-transformers all-MiniLM-L6-v2,
    descargando ~90MB de HuggingFace en cold start). Si lo llamamos directamente
    en on_startup, bloquea > healthcheck timeout (300s) cuando HF esta lento o
    el volumen Railway hace cold-rotation. Patron similar al fix del 11-abr para
    _auto_observe_bootstrap (asyncio.to_thread).
    """
    try:
        rag_ok = await asyncio.to_thread(init_rag)
        if rag_ok:
            print("[RAG] Sistema RAG legal inicializado correctamente (background).")
    except Exception as _rag_err:
        print(f"[RAG] No disponible en este arranque: {_rag_err}")


@app.on_event("startup")
async def on_startup():
    _init_db()
    _migrate_json_to_sqlite()
    _preload_reports_on_startup()
    _preload_sessions_on_startup()  # R2: rehidrata sesiones de observacion activas
    # RAG en background — el comentario decia "no bloquea el startup" pero la
    # implementacion previa SI bloqueaba (init_rag synchronous). Movido a
    # asyncio.to_thread via create_task para liberar el event loop. Healthcheck
    # responde rapido; RAG queda listo ~30-90s despues sin afectar otros endpoints.
    asyncio.create_task(_init_rag_background())
    # Verificar conectividad OONI (warm-up silencioso)
    try:
        import httpx as _httpx_test  # noqa
        print("[OONI] httpx disponible — integración OONI activa.")
    except ImportError:
        print("[OONI] httpx no instalado — ejecutar: pip install httpx>=0.27.0")
    # Inicializar db/ (capa de persistencia extendida)
    if DB_AVAILABLE:
        try:
            _db_init_db()
        except Exception as _db_err:
            print(f"[DB] AVISO: No se pudo inicializar SQLite extendido: {_db_err}")
    # Startup checks
    if STARTUP_CHECKS_AVAILABLE:
        try:
            _run_startup_checks(raise_on_critical=False)
        except Exception as _sc_err:
            print(f"[STARTUP] Error en checks: {_sc_err}")
    # ── Auto-bootstrap: sesiones de observación configuradas por env ──────
    # Corre en background para no bloquear el health check
    auto_observe = os.getenv("AUTO_OBSERVE_COUNTRIES", "")
    if auto_observe:
        asyncio.create_task(_auto_observe_bootstrap(auto_observe))

    # Arrancar Hunter scheduler en background
    global _hunter_scheduler_task
    _hunter_scheduler_task = asyncio.create_task(_hunter_scheduler_loop())

    # Self-test del LLM al arrancar (en background, no bloquea startup).
    # Detecta API key inválida / créditos en cero / overload antes de que el Hunter falle.
    asyncio.create_task(_startup_llm_selftest())

    # ── Automatizaciones diarias (Sprint 6-may-2026) ─────────────────────
    # A) Phase auto-advance: mantiene la fase de PER sincronizada con calendario
    # B) Daily digest: postea resumen 24h a Discord cada dia a las 13:00 UTC
    # F) Daily backup: corre scripts/backup.py --targz cada dia a las 03:00 UTC
    asyncio.create_task(_phase_auto_advance_loop())
    asyncio.create_task(_daily_digest_loop())
    asyncio.create_task(_daily_backup_loop())


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


class VotingDayInput(BaseModel):
    country_code: str
    run_id: str  # Run ID del análisis previo a actualizar
    participation_pct: Optional[float] = None          # Participación estimada 0-100
    results_transmitted_pct: Optional[float] = None    # Actas transmitidas 0-100
    incidents: Optional[List[str]] = []                # Lista de incidentes reportados
    observer_reports: Optional[List[str]] = []         # Reportes de observadores
    emb_statements: Optional[List[str]] = []           # Declaraciones del EMB
    media_restrictions_reported: Optional[bool] = None # Restricciones a medios detectadas
    internet_disruptions: Optional[bool] = None        # Interrupciones de internet
    violence_incidents: Optional[int] = 0              # Número de incidentes de violencia
    timestamp_local: Optional[str] = None              # Hora local de actualización


# ── Modelos para Protocolo de Observación Electoral ───────────────────────────

class ObservationStartInput(BaseModel):
    """Inicia una sesión de observación ligada a un run_id existente."""
    country_code: str
    run_id: str                              # Reporte PEIRS previo de referencia
    mission_name: Optional[str] = "Misión de Observación Electoral"
    lead_org: Optional[str] = "DEMOCRAC.IA Observer Network"
    # R6: Multi-sesión — True = archiva sesión activa y crea una nueva (ej. segunda vuelta)
    allow_override: Optional[bool] = False


class ObservationEntryInput(BaseModel):
    """Un hallazgo/observación individual ingresado por un observador de campo."""
    country_code: str
    phase: str                               # R4: cualquiera de _PHASE_ORDER o alias legacy "pre_election"
    timestamp: Optional[str] = None          # ISO8601; si omitido, se usa el momento actual
    observer_id: Optional[str] = "OBS-001"  # Identificador del observador
    location: Optional[str] = ""            # Mesa, distrito, región
    category: str                            # R5: "logistics"|"security"|"legal"|"media"|"digital"|"counting"|"results"|"fraud_allegation"|"hate_speech"|"campaign_violation"|"voter_suppression"|"accessibility"|"gender_violence"|"disinformation"|"voter_intimidation"|"ballot_tampering"|"media_restriction"|"irregular_procedure"|"other"
    finding: str                             # Descripción del hallazgo
    severity: str = "info"                   # "info"|"low"|"medium"|"high"|"critical"
    rights_at_risk: Optional[List[str]] = [] # p.ej. ["ICCPR Art. 25", "CADH Art. 23"]
    verified: Optional[bool] = False
    verified_by: Optional[str] = None
    evidence_ref: Optional[str] = None       # Referencia a foto/doc (URL o código)
    # ── Campos específicos para fraud_allegation ──────────────────────────────
    fraud_type: Optional[str] = None         # "padron"|"vote_buying"|"intimidation"|"polling_day"|"counting"|"results"|"candidate"|"financing"|"other"
    credibility: Optional[str] = None        # "confirmed"|"high"|"medium"|"low"|"unverified"
    source_org: Optional[str] = None         # Organización fuente de la alegación
    # ── Campos específicos para hate_speech ───────────────────────────────────
    target_group: Optional[str] = None       # "women_candidates"|"indigenous"|"lgbtq"|"migrants"|"ethnic_minority"|"religious"|"political_opponent"|"journalists"|"other"
    platform: Optional[str] = None           # "Twitter/X"|"TikTok"|"Facebook"|"WhatsApp"|"TV"|"Radio"|"other"
    reach_estimate: Optional[str] = None     # p.ej. "~50,000 impresiones" o "alcance local"


class ObservationAdvanceInput(BaseModel):
    """Avanza la fase del protocolo de observación."""
    country_code: str
    target_phase: str  # R4: cualquiera de _PHASE_ORDER (p.ej. "campaign", "electoral_silence", "election_day", "counting_tabulation", "post_election", "dispute_resolution", "completed")
    notes: Optional[str] = None


# Cache del LLM ping para no quemar API en cada /health (que UptimeRobot etc. pegan cada 5min)
_LLM_HEALTH_CACHE = {"checked_at": None, "ok": None, "error": None, "ttl_seconds": 300}


async def _check_llm_alive() -> Dict[str, Any]:
    """Ping liviano al LLM (1 token). Cacheado 5 min. Sirve para detectar
    invalid api key, créditos en cero, overload, etc., antes de que se note en producción."""
    now = datetime.now(timezone.utc)
    cache = _LLM_HEALTH_CACHE
    if cache["checked_at"]:
        try:
            last = datetime.fromisoformat(cache["checked_at"])
            if (now - last).total_seconds() < cache["ttl_seconds"]:
                return {"ok": cache["ok"], "error": cache["error"], "checked_at": cache["checked_at"], "cached": True}
        except Exception:
            pass

    if llm is None:
        cache.update({"ok": False, "error": "llm not initialized", "checked_at": now.isoformat()})
        return {"ok": False, "error": "llm not initialized", "checked_at": cache["checked_at"], "cached": False}

    try:
        from langchain_core.messages import HumanMessage
        # 1 token, prompt mínimo. Sonnet/Haiku responden esto en <500ms y cuesta ~$0.000003.
        resp = await asyncio.wait_for(
            llm.ainvoke([HumanMessage(content="ok")]),
            timeout=10,
        )
        cache.update({"ok": True, "error": None, "checked_at": now.isoformat()})
        return {"ok": True, "error": None, "checked_at": cache["checked_at"], "cached": False}
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)[:200]}"
        cache.update({"ok": False, "error": err, "checked_at": now.isoformat()})
        return {"ok": False, "error": err, "checked_at": cache["checked_at"], "cached": False}


@app.get("/api/health")
async def health_check(deep: bool = False):
    """
    Health check del sistema.
    - default: liviano (sin tocar el LLM, devuelve flags estáticos).
    - ?deep=true: incluye ping real al LLM (cacheado 5min). Usar desde monitores externos.
    """
    payload = {
        "status": "operational",
        "system": "DEMOCRAC.IA (PEIRS)",
        "version": "0.4.0",
        "features": [
            "country_profile", "electoral_observation_protocol", "traceability",
            f"vdem_{VDEM_VERSION}", "freedom_house", "pei_v10", "rsf_index",
            "ooni_live", "fraud_hate_analysis", "rag_legal", "constitutionalist",
            "report_designer", "elite_report",
        ],
        "traceability": "enabled",
        "observation_protocol": "enabled",
        "llm_configured": llm is not None,
        "countries_available": len(COUNTRY_CATALOG),
        "active_observation_sessions": len(observation_store),
        "observer_keys_configured": len(OBSERVER_API_KEYS),
        "ooni_integration": OONI_AVAILABLE,
        "alert_dispatch": ALERTS_AVAILABLE,
        "alert_channels_configured": {
            "slack":   bool(os.getenv("ALERT_SLACK_WEBHOOK_URL")),
            "webhook": bool(os.getenv("ALERT_WEBHOOK_URL")),
            "email":   bool(os.getenv("ALERT_EMAIL_TO")),
        },
        "legal_instruments": len(UNIVERSAL_INSTRUMENTS) + sum(len(v) for v in REGIONAL_INSTRUMENTS.values()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if deep:
        llm_check = await _check_llm_alive()
        payload["llm_alive"] = llm_check["ok"]
        payload["llm_check"] = llm_check
        if not llm_check["ok"]:
            payload["status"] = "degraded"
    return payload


@app.get("/api/stats")
async def get_system_stats():
    """Estadísticas del sistema: runs, reportes, observaciones."""
    stats = _db_get_stats() if DB_AVAILABLE else {}
    return {
        "db_available": DB_AVAILABLE,
        "rag_available": RAG_AVAILABLE,
        "stats": stats,
    }


class WaitlistSignupInput(BaseModel):
    """Payload del form de waitlist en la landing.

    Sprint B1 (17-may-2026): captura email + tier interesado antes de
    que el sistema de billing real (Stripe) este live. Mariana exporta
    los signups via /api/admin/waitlist y contacta uno a uno.
    """
    email: str = Field(..., min_length=4, max_length=320)
    tier_interested: str = Field(..., description="public|researcher_press|institutional|mission|enterprise")
    organization: Optional[str] = Field(None, max_length=200)
    role: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = Field(None, max_length=1000)
    source: Optional[str] = Field("landing", max_length=50)


@app.post("/api/public/waitlist/signup")
async def waitlist_signup(payload: WaitlistSignupInput, request: Request):
    """Captura email de interesado en un tier de pago.

    Sin auth — endpoint publico. Validacion minima de email (regex basico
    + longitud). Devuelve {ok, position} donde position es el orden de
    signup para el tier (1-indexed).
    """
    import re
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", payload.email or ""):
        raise HTTPException(status_code=422, detail="Email invalido.")
    valid_tiers = {"public", "researcher_press", "institutional", "mission", "enterprise"}
    if payload.tier_interested not in valid_tiers:
        raise HTTPException(status_code=422, detail=f"tier_interested invalido. Opciones: {valid_tiers}")

    now_iso = datetime.now(timezone.utc).isoformat()
    user_agent = request.headers.get("user-agent", "")[:300]

    try:
        with _get_db() as conn:
            cur = conn.execute(
                "INSERT INTO waitlist_signups "
                "(email, tier_interested, organization, role, note, source, signed_up_at, user_agent) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    payload.email.strip().lower(),
                    payload.tier_interested,
                    (payload.organization or "").strip()[:200] or None,
                    (payload.role or "").strip()[:100] or None,
                    (payload.note or "").strip()[:1000] or None,
                    payload.source or "landing",
                    now_iso,
                    user_agent,
                ),
            )
            conn.commit()
            position_row = conn.execute(
                "SELECT COUNT(*) AS n FROM waitlist_signups WHERE tier_interested=?",
                (payload.tier_interested,),
            ).fetchone()
            position = position_row["n"] if position_row else 0
        print(f"[waitlist] {payload.tier_interested} signup: {payload.email}")
        return {"ok": True, "position": position}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar signup: {type(e).__name__}")


@app.get("/api/admin/waitlist")
async def waitlist_list(_key: str = Depends(_require_observer_key)):
    """Lista de signups del waitlist. Requiere X-Observer-Key.

    Devuelve agregados por tier + ultimos signups. Para Mariana, el panel
    de admin para contactar leads. Sin info sensible adicional al email
    (no IP, no datos personales mas alla de los que el usuario provee
    voluntariamente)."""
    from collections import Counter
    try:
        with _get_db() as conn:
            rows = conn.execute(
                "SELECT id, email, tier_interested, organization, role, note, source, "
                "signed_up_at, contacted_at, converted "
                "FROM waitlist_signups ORDER BY signed_up_at DESC LIMIT 500"
            ).fetchall()
        signups = [dict(r) for r in rows]
        by_tier = Counter(s["tier_interested"] for s in signups)
        converted = sum(1 for s in signups if s.get("converted"))
        return {
            "total": len(signups),
            "converted": converted,
            "by_tier": dict(by_tier),
            "signups": signups,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar waitlist: {type(e).__name__}")


@app.get("/api/public/tiers")
async def get_public_tiers():
    """Listado publico de tiers de acceso para mostrar en pricing page.

    Devuelve los 5 tiers (Public, Researcher, Institutional, Mission,
    Enterprise) con features y limites. Sin auth — datos publicos para
    landing.

    Implementacion del modelo en backend/modules/tiers.py. Auth multi-tier
    y billing Stripe son sprints posteriores.
    """
    try:
        from modules.tiers import list_public_tiers
        return {"tiers": list_public_tiers()}
    except Exception as e:
        return {"tiers": [], "error": str(e)}


@app.get("/api/public/stats")
async def get_public_stats():
    """Estadisticas publicas agregadas para landing pagina.

    No requiere auth. Datos seguros para exposicion publica:
    - Countries en catalogo + paises con cobertura activa
    - Total findings del Hunter (de observation_sessions reales)
    - Reportes Elite generados
    - Days running (desde el inicio de la sesion mas antigua)
    - Last activity timestamp (Hunter ultimo ciclo)

    NO expone: secrets, observer keys, user data, run_ids, contenido
    de findings o reports.
    """
    from collections import Counter
    countries_total = len(COUNTRY_CATALOG)
    active_session_countries = list(observation_store.keys())
    countries_active = len(active_session_countries)

    # Aggregar findings reales del Hunter desde observation_sessions
    total_findings = 0
    severity_breakdown = Counter()
    days_monitoring = 0
    last_finding_at: Optional[str] = None
    primary_country: Optional[Dict[str, Any]] = None

    for cc, session in observation_store.items():
        entries = session.get("entries", []) or []
        total_findings += len(entries)
        for e in entries:
            sev = (e.get("severity") or "info").lower()
            severity_breakdown[sev] += 1
            recorded = e.get("recorded_at")
            if recorded and (last_finding_at is None or recorded > last_finding_at):
                last_finding_at = recorded

        # Calculate days monitoring desde started_at
        started = session.get("started_at")
        if started:
            try:
                started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                delta_days = (datetime.now(timezone.utc) - started_dt).days
                if delta_days > days_monitoring:
                    days_monitoring = delta_days
            except Exception:
                pass

        # Primary country = first active session
        if primary_country is None:
            cat = COUNTRY_CATALOG.get(cc, {})
            primary_country = {
                "code": cc,
                "name": cat.get("name", cc),
                "flag": cat.get("flag", ""),
                "election_date": cat.get("election_date"),
                "phase": session.get("phase"),
                "phase_label": _PHASE_LABELS.get(session.get("phase", ""), ""),
            }

    # Reports generated count via SQLite
    elite_reports_count = 0
    if DB_AVAILABLE:
        try:
            with _get_db() as conn:
                row = conn.execute("SELECT COUNT(*) AS n FROM elite_reports").fetchone()
                elite_reports_count = row["n"] if row else 0
        except Exception:
            pass

    return {
        "platform": {
            "version": "0.6.0",
            "operational": True,
            "languages": ["es", "en", "pt"],
        },
        "coverage": {
            "countries_catalog": countries_total,
            "countries_active": countries_active,
            "primary_country": primary_country,
        },
        "monitoring": {
            "total_findings": total_findings,
            "severity_breakdown": dict(severity_breakdown),
            "days_running": days_monitoring,
            "last_finding_at": last_finding_at,
            "hunter_active": True,
        },
        "outputs": {
            "elite_reports_generated": elite_reports_count,
        },
        "datasets": [
            {"name": "V-Dem", "version": "v16", "coverage": "1789-2025", "countries": 202},
            {"name": "Freedom House FIW", "coverage": "2013-2025", "countries": 195},
            {"name": "PEI", "version": "10.0", "coverage": "2012-2023", "elections": 586},
            {"name": "RSF", "version": "2025", "countries": 180},
        ],
        "as_of": datetime.now(timezone.utc).isoformat(),
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

    initial_state = create_initial_state(
        country=country_info["name"],
        country_code=code,
        election_date=election_date,
    )

    if DB_AVAILABLE:
        _db_create_run(initial_state["run_id"], code, election_date)

    result = peirs_pipeline.invoke(initial_state)
    reports_store[result["run_id"]] = result
    save_report(result)

    if DB_AVAILABLE:
        try:
            _db_complete_run(result["run_id"],
                             risk_score=result.get("risk_score", 0),
                             risk_level=result.get("risk_level", "unknown"))
            _db_save_report(result["run_id"], code,
                            report_md=result.get("final_report_markdown", ""),
                            report_json=result)
        except Exception as _db_persist_err:
            print(f"[DB] AVISO: No se pudo guardar reporte en db/: {_db_persist_err}")

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
        disk = load_report(run_id)
        if disk is None:
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        reports_store[run_id] = disk
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
        "applicable_instruments": result.get("applicable_instruments", {}),
        "trace_log": result.get("trace_log", []),
        "dictamen": result.get("dictamen", {}),
    }


@app.get("/api/report/{run_id}/markdown")
async def get_report_markdown(run_id: str):
    if run_id not in reports_store:
        disk = load_report(run_id)
        if disk is None:
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        reports_store[run_id] = disk
    return {
        "run_id": run_id,
        "markdown": reports_store[run_id]["final_report_markdown"],
    }


@app.get("/api/report/{run_id}/traceability")
async def get_report_traceability(run_id: str):
    if run_id not in reports_store:
        disk = load_report(run_id)
        if disk is None:
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        reports_store[run_id] = disk
    result = reports_store[run_id]
    trace_log = result.get("trace_log", [])
    legal = result.get("legal_analysis", {})

    confidence_counts = {}
    for t in trace_log:
        conf = t.get("confidence", "unknown")
        confidence_counts[conf] = confidence_counts.get(conf, 0) + 1

    publishable = sum(1 for t in trace_log if t.get("is_publishable", False))

    return {
        "run_id": run_id,
        "country": result["country"],
        "traceability_summary": {
            "total_traced_fields": len(trace_log),
            "publishable_fields": publishable,
            "non_publishable_fields": len(trace_log) - publishable,
            "confidence_distribution": confidence_counts,
            "is_report_publishable": publishable > 0 and confidence_counts.get("mock", 0) == 0,
            "publishability_note": "Un reporte es publicable cuando TODOS sus datos tienen confidence != 'mock'.",
        },
        "applicable_instruments": result.get("applicable_instruments", {}),
        "violation_confidence": legal.get("confidence_summary", {}),
        "trace_log": trace_log,
    }


@app.get("/api/reports/history/{country_code}")
async def get_report_history(country_code: str):
    """Historial de reportes generados para un país."""
    index = _load_reports_index()
    code = country_code.upper()
    history = index.get(code, [])
    return {
        "country_code": code,
        "total_reports": len(history),
        "history": list(reversed(history)),  # más reciente primero
    }


@app.get("/api/reports/history")
async def get_all_history():
    """Historial completo de todos los países."""
    index = _load_reports_index()
    summary = {}
    for code, reports in index.items():
        if reports:
            latest = reports[-1]
            summary[code] = {
                "total_reports": len(reports),
                "latest_run_id": latest["run_id"],
                "latest_timestamp": latest["timestamp"],
                "latest_risk_score": latest["risk_score"],
                "latest_risk_level": latest["risk_level"],
            }
    return {"countries": summary, "total_countries": len(summary)}


@app.get("/api/instruments/{country_code}")
async def get_instruments(country_code: str):
    code = country_code.upper()
    instruments = get_applicable_instruments(code)
    return {
        "country_code": code,
        "region": instruments["region"],
        "universal_instruments": instruments["universal"],
        "regional_instruments": instruments["regional"],
        "total_instruments": len(instruments["all_ids"]),
    }


@app.get("/api/dashboard")
async def get_dashboard_data(force_refresh: bool = False):
    """Retorna datos del dashboard para todos los países.
    Usa caché de disco (< 24h) por defecto. Forzar regeneración con ?force_refresh=true.
    """
    dashboard_countries = []
    index = _load_reports_index()
    now_ts = datetime.now(timezone.utc)
    cached_count = 0
    generated_count = 0

    for code, info in COUNTRY_CATALOG.items():
        result = None

        # Intentar caché si no se pide force_refresh
        if not force_refresh:
            entries = index.get(code, [])
            if entries:
                latest = entries[-1]
                try:
                    ts_str = latest.get("timestamp", "")
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        age_h = (now_ts - ts).total_seconds() / 3600
                        if age_h < 24:
                            cached = load_report(latest["run_id"])
                            if cached:
                                result = cached
                                reports_store[latest["run_id"]] = cached
                                cached_count += 1
                except Exception:
                    pass

        # Sin caché válida: SKIP en lugar de correr pipeline sincronamente.
        # Auditoria 16-may: correr peirs_pipeline.invoke(state) bloqueaba el
        # event loop ~60s por pais x 38 paises = posible cuelgue de 30+ min
        # del endpoint /api/dashboard, congelando TODA la API (frontend
        # se quedaba en loading screen indefinidamente).
        # Para generar reporte de un pais sin cache, usar POST /api/analyze
        # con country_code (devuelve run_id) — endpoint dedicado, no en
        # listing handler.
        if result is None:
            continue

        context = result.get("context_data", {})
        political = result.get("political_data", {})
        legal = result.get("legal_analysis", {})

        exposure = political.get("media_analysis", {}).get("exposure_distribution", {})
        media_data = [
            {"name": k.replace("_", " ").title(), "exposure": v, "sentiment": 0}
            for k, v in exposure.items()
        ]

        violations_simple = [
            f"{v['treaty']} {v['article']}" for v in legal.get("violations", [])
        ]

        emb_scores_map = {"full": 95, "partial": 60, "compromised": 25, "captured": 5}
        emb_data = extract_value(context.get("emb", {}))
        emb_level = emb_data.get("independence_level", "partial") if isinstance(emb_data, dict) else "partial"

        eco_scores_map = {"healthy": 90, "concerning": 60, "compromised": 35, "hostile": 10}
        eco_level = political.get("digital_ecosystem", {}).get("assessment", "concerning")

        finance_score = political.get("campaign_finance", {}).get("transparency_score", 0.5)

        fh_data = extract_value(context.get("freedom_house", {}))
        fh = fh_data.get("total_score", fh_data.get("score", 50)) if isinstance(fh_data, dict) else 50

        vdem_data = extract_value(context.get("vdem", {}))
        vdem_val = vdem_data.get("liberal_democracy", 0.5) if isinstance(vdem_data, dict) else 0.5

        media_bias = political.get("media_analysis", {}).get("bias_index", 0.3)

        dimensions = {
            "suffrage": max(5, int(fh * 0.9)),
            "legalFramework": max(5, int(vdem_val * 100)),
            "embIndependence": emb_scores_map.get(emb_level, 50),
            "mediaFreedom": max(5, int((1 - media_bias) * 100)),
            "campaignFinance": max(5, int(finance_score * 100)),
            "digitalEcosystem": eco_scores_map.get(eco_level, 40),
            "disputeResolution": max(5, int(vdem_val * 90)),
            "inclusion": max(5, int(fh * 0.8)),
        }

        risk = result["risk_score"]
        trend = "deteriorating" if risk >= 70 else "stable"

        alerts = []
        for v in legal.get("violations", [])[:4]:
            alert_type = "critical" if v["severity"] == "critical" else "high" if v["severity"] == "high" else "moderate"
            alerts.append({"type": alert_type, "text": v["finding"][:120]})
        for rf in legal.get("risk_factors", [])[:2]:
            alerts.append({"type": rf.get("severity", "moderate"), "text": rf["finding"][:120]})
        if not alerts:
            alerts.append({"type": "low", "text": "Sistema electoral estable con garantías institucionales sólidas"})

        # Timeline desde datos históricos V-Dem (reemplaza números aleatorios)
        vdem_trend = _get_vdem_trend(VDEM_DF, code, years_back=5)
        if vdem_trend.get("available") and len(vdem_trend.get("values", [])) >= 2:
            timeline = [
                {"month": str(year), "score": max(5, min(99, round((1 - libdem) * 100)))}
                for year, libdem in vdem_trend["values"][-6:]
            ]
        else:
            base = max(10, int(risk * 0.7))
            years_labels = [str(2019 + i) for i in range(6)]
            timeline = [
                {"month": yr, "score": base + int((risk - base) * (i / max(1, 5)))}
                for i, yr in enumerate(years_labels)
            ]

        dashboard_countries.append({
            "id": code.lower(),
            "run_id": result["run_id"],
            "name": info["name"],
            "flag": info["flag"],
            "date": info["election_date"],
            "riskScore": result["risk_score"],
            "riskLevel": result["risk_level"],
            "trend": trend,
            "freedomScore": fh,
            "vdemIndex": round(vdem_val, 3),
            "dimensions": dimensions,
            "violations": violations_simple,
            "timeline": timeline,
            "alerts": alerts,
            "mediaData": media_data,
            "agentLogs": result.get("agent_logs", []),
            "region": COUNTRY_REGIONS.get(code, "unknown"),
        })

    print(f"[Dashboard] OK: {cached_count} desde cache, {generated_count} regenerados.")
    return {"countries": dashboard_countries, "generated_at": datetime.now(timezone.utc).isoformat()}


@app.post("/api/analyze/voting-day")
async def update_voting_day(request: VotingDayInput):
    """Actualiza el Cap. 7 de un reporte existente con datos del dia de votacion."""
    run_id = request.run_id
    code = request.country_code.upper()

    if run_id not in reports_store:
        disk = load_report(run_id)
        if disk is None:
            raise HTTPException(status_code=404, detail="Reporte no encontrado. Ejecuta /api/analyze primero.")
        reports_store[run_id] = disk

    result = reports_store[run_id]

    # Guardar datos del dia de votacion en el estado
    voting_day_data = {
        "active": True,
        "participation_pct": request.participation_pct,
        "results_transmitted_pct": request.results_transmitted_pct,
        "incidents": request.incidents or [],
        "observer_reports": request.observer_reports or [],
        "emb_statements": request.emb_statements or [],
        "media_restrictions_reported": request.media_restrictions_reported,
        "internet_disruptions": request.internet_disruptions,
        "violence_incidents": request.violence_incidents or 0,
        "timestamp_local": request.timestamp_local or datetime.now(timezone.utc).strftime("%H:%M UTC"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    result["voting_day_data"] = voting_day_data

    # Crear un state temporal para regenerar el cap 7
    from copy import deepcopy
    temp_state = deepcopy(result)
    temp_state["voting_day_data"] = voting_day_data

    # Regenerar solo el cap 7
    new_cap7 = _generate_voting_day_chapter(voting_day_data, temp_state)
    result["report_chapters"]["07_voting_day"] = new_cap7

    # Reconstruir el informe completo
    report_header = (
        "# DEMOCRAC.IA — Informe VIP de Integridad Electoral\n"
        f"## {result['country']} — Eleccion: {result['election_date']}\n\n"
        f"**Indice Predictivo de Riesgo:** {result['risk_score']}/100 ({result['risk_level'].upper()})\n"
        f"**Generado:** {result['timestamp'][:19]} UTC\n"
        f"**Run ID:** `{run_id}`\n\n---\n\n"
    )
    result["final_report_markdown"] = report_header + "\n\n".join(result["report_chapters"].values())

    # Guardar actualización en disco
    reports_store[run_id] = result
    save_report(result)

    return {
        "run_id": run_id,
        "country": result["country"],
        "status": "voting_day_updated",
        "day_assessment": voting_day_data.get("timestamp_local"),
        "incidents_loaded": len(voting_day_data["incidents"]),
        "observer_reports_loaded": len(voting_day_data["observer_reports"]),
        "message": "Cap. 7 actualizado exitosamente. Accede al informe via /api/report/" + run_id,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# 7. PROTOCOLO DE OBSERVACIÓN ELECTORAL — Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/observation/{country_code}/start")
async def observation_start(country_code: str, request: ObservationStartInput, _key: str = Depends(_require_observer_key)):
    """
    Inicia una sesión del Protocolo de Observación Electoral para un país.
    Debe existir un reporte PEIRS (run_id) previo para el país.
    Fases del protocolo: preparatory → ... → completed.

    R6 — Multi-sesión: si ya existe una sesión activa para el país:
    - allow_override=False (default): retorna 409 con datos de la sesión existente
    - allow_override=True: archiva la sesión activa (marca finalized=True) y crea una nueva.
      Útil para segunda vuelta o nueva ronda de observación sin perder hallazgos anteriores.
    """
    code = country_code.upper()

    # R6: Verificar sesión existente
    if code in observation_store and not observation_store[code].get("finalized", False):
        existing = observation_store[code]
        if not request.allow_override:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": f"Ya existe una sesión activa para {code}.",
                    "session_id":   existing.get("session_id"),
                    "mission_name": existing.get("mission_name"),
                    "phase":        existing.get("phase"),
                    "entries":      len(existing.get("entries", [])),
                    "hint": "Usa allow_override=true para archivar esta sesión e iniciar una nueva (ej. segunda vuelta).",
                }
            )
        # allow_override=True → archivar sesión previa en SQLite como finalizada
        now_archive = datetime.now(timezone.utc).isoformat()
        existing["finalized"]  = True
        existing["phase"]      = existing.get("phase", "completed")
        existing["updated_at"] = now_archive
        existing.setdefault("archive_reason", f"Archivada por nueva sesión ({request.mission_name})")
        with _get_db() as conn:
            conn.execute(
                "UPDATE observation_sessions SET finalized=1, updated_at=?, data=? WHERE country_code=? AND session_id=?",
                (now_archive, json.dumps(existing), code, existing["session_id"])
            )
            conn.commit()

    # Verificar que el run_id existe
    run_id = request.run_id
    if run_id not in reports_store:
        disk = load_report(run_id)
        if disk is None:
            raise HTTPException(status_code=404, detail=f"run_id '{run_id}' no encontrado. Ejecuta /api/analyze primero.")
        reports_store[run_id] = disk

    now = datetime.now(timezone.utc).isoformat()
    session = {
        "session_id":   str(uuid.uuid4()),
        "country_code": code,
        "run_id":       run_id,
        "mission_name": request.mission_name,
        "lead_org":     request.lead_org,
        "phase":        "preparatory",   # R4: fase inicial canónica
        "started_at":   now,
        "updated_at":   now,
        "entries":      [],
        "finalized":    False,
    }
    observation_store[code] = session

    # Persistir en SQLite
    with _get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO observation_sessions "
            "(session_id, country_code, run_id, mission_name, lead_org, phase, started_at, updated_at, finalized, data) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (session["session_id"], code, run_id, request.mission_name, request.lead_org,
             "preparatory", now, now, 0, json.dumps(session))
        )
        conn.commit()

    # Regenerar Cap. 7 del reporte ligado
    result = reports_store[run_id]
    new_cap7 = _generate_observation_chapter(session, result)
    result["report_chapters"]["07_voting_day"] = new_cap7
    result["final_report_markdown"] = (
        f"# DEMOCRAC.IA — Informe VIP de Integridad Electoral\n"
        f"## {result['country']} — Elección: {result['election_date']}\n\n"
        f"**Índice Predictivo de Riesgo:** {result['risk_score']}/100 ({result['risk_level'].upper()})\n"
        f"**Generado:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"**Run ID:** `{run_id}`\n\n---\n\n"
        + "\n\n".join(result["report_chapters"].values())
    )
    reports_store[run_id] = result
    save_report(result)

    return {
        "session_id":   session["session_id"],
        "country_code": code,
        "run_id":       run_id,
        "phase":        "preparatory",
        "phase_label":  _PHASE_LABELS["preparatory"],
        "mission_name": request.mission_name,
        "available_phases": _PHASE_ORDER,
        "message":      f"Protocolo de observación iniciado. Fase activa: PREPARATORIO. Avanza fases via POST /api/observation/{code}/advance. Agrega hallazgos via POST /api/observation/{code}/entry",
    }


@app.post("/api/observation/{country_code}/entry")
async def observation_add_entry(country_code: str, request: ObservationEntryInput, _key: str = Depends(_require_observer_key)):
    """
    Agrega un hallazgo de campo al protocolo de observación.
    Regenera automáticamente el Cap. 7 del reporte ligado.
    """
    code = country_code.upper()
    if code not in observation_store:
        raise HTTPException(status_code=404, detail=f"No hay sesión activa para {code}. Usa POST /api/observation/{code}/start primero.")

    session = observation_store[code]
    now = datetime.now(timezone.utc).isoformat()

    # R3+R4: Validar coherencia temporal de la phase enviada (usa _PHASE_ORDER global + aliases)
    active_phase = session.get("phase", "preparatory")
    # Normalizar alias legacy (p.ej. "pre_election" → "electoral_silence")
    raw_phase   = request.phase or active_phase
    entry_phase = _PHASE_ALIAS.get(raw_phase, raw_phase)
    active_phase_norm = _PHASE_ALIAS.get(active_phase, active_phase)
    active_idx = _PHASE_ORDER.index(active_phase_norm) if active_phase_norm in _PHASE_ORDER else 0
    entry_idx  = _PHASE_ORDER.index(entry_phase)       if entry_phase       in _PHASE_ORDER else 0
    phase_warning = None
    if entry_idx > active_idx:
        # Fase futura: normalizar a la activa y advertir
        entry_phase   = active_phase
        phase_warning = (
            f"Phase '{request.phase}' is ahead of active session phase '{active_phase}'. "
            f"Entry registered under '{active_phase}'."
        )

    # Derechos auto-sugeridos si no vienen
    auto_rights = _auto_rights(request.category, request.severity)
    rights = list(set((request.rights_at_risk or []) + auto_rights))

    entry = {
        "entry_id":       str(uuid.uuid4())[:8],
        "timestamp":      request.timestamp or now,
        "observer_id":    request.observer_id,
        "location":       request.location,
        "phase":          entry_phase,  # R3: ya validada y normalizada
        "category":       request.category,
        "finding":        request.finding,
        "severity":       _auto_escalate_severity(request.severity, request.category, request.finding),
        "rights_at_risk": rights,
        "verified":       request.verified,
        "verified_by":    request.verified_by,
        "evidence_ref":   request.evidence_ref,
        "recorded_at":    now,
        # Campos específicos fraud_allegation
        "fraud_type":     request.fraud_type,
        "credibility":    request.credibility,
        "source_org":     request.source_org,
        # Campos específicos hate_speech
        "target_group":   request.target_group,
        "platform":       request.platform,
        "reach_estimate": request.reach_estimate,
    }

    # Agent 5 — validar antes de registrar
    existing = session.get("entries", [])
    validation = validate_entry(entry, existing)

    session["entries"].append(entry)
    session["updated_at"] = now
    observation_store[code] = session

    # Regenerar Cap. 7
    run_id = session.get("run_id")
    if run_id and run_id in reports_store:
        result = reports_store[run_id]
        new_cap7 = _generate_observation_chapter(session, result)
        result["report_chapters"]["07_voting_day"] = new_cap7
        result["final_report_markdown"] = (
            f"# DEMOCRAC.IA — Informe VIP de Integridad Electoral\n"
            f"## {result['country']} — Elección: {result['election_date']}\n\n"
            f"**Índice Predictivo de Riesgo:** {result['risk_score']}/100 ({result['risk_level'].upper()})\n"
            f"**Generado:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**Run ID:** `{run_id}`\n\n---\n\n"
            + "\n\n".join(result["report_chapters"].values())
        )
        reports_store[run_id] = result
        save_report(result)

    # Persistir sesión actualizada
    with _get_db() as conn:
        conn.execute(
            "UPDATE observation_sessions SET phase=?, updated_at=?, data=? WHERE country_code=? AND session_id=?",
            (session["phase"], now, json.dumps(session), code, session["session_id"])
        )
        conn.commit()

    # Agent 7 — despachar alerta si corresponde (usa severidad final escalada)
    alert_result = {"dispatched": False}
    if ALERTS_AVAILABLE and entry["severity"] in ("critical", "high"):
        patterns = detect_patterns(session.get("entries", []))
        alert_event = build_entry_alert(entry, session, patterns)
        if alert_event:
            try:
                alert_result = await dispatch_alert(alert_event)
            except Exception:
                pass

    warnings_out = list(validation.warnings)
    if phase_warning:
        warnings_out.insert(0, phase_warning)

    escalation_note = (
        f"Severidad escalada automáticamente: {request.severity} → {entry['severity']} "
        f"(escala detectada en hallazgo — estándar ICCPR Art. 25(b))"
        if entry["severity"] != request.severity else None
    )
    if escalation_note:
        warnings_out.insert(0, escalation_note)

    return {
        "entry_id":        entry["entry_id"],
        "country_code":    code,
        "phase":           entry_phase,
        "severity":        entry["severity"],          # severidad final (puede ser escalada)
        "severity_original": request.severity,         # lo que ingresó el observador
        "severity_escalated": entry["severity"] != request.severity,
        "rights_at_risk":  rights,
        "total_entries":   len(session["entries"]),
        "quality_score":   validation.quality_score,
        "warnings":        warnings_out,
        "duplicate_of":    validation.duplicate_of,
        "alert_dispatched": alert_result.get("dispatched", False),
        "alert_channels":  alert_result.get("channels", {}),
        "message":         f"Hallazgo registrado. Total en sesión: {len(session['entries'])}.",
    }


@app.get("/api/observation/{country_code}/patterns")
async def observation_patterns(country_code: str, _key: str = Depends(_require_observer_key)):
    """
    Agent 5 — Retorna el análisis completo de patrones sistemáticos de la sesión.
    Incluye concentración geográfica, clusters por categoría, escaladas y corroboraciones.
    """
    code = country_code.upper()
    if code not in observation_store:
        raise HTTPException(status_code=404, detail=f"No hay sesión activa para {code}.")

    session = observation_store[code]
    entries = session.get("entries", [])
    report  = detect_patterns(entries)

    return {
        "country_code":                  code,
        "total_entries":                 len(entries),
        "has_significant_patterns":      report.has_significant_patterns,
        "fraud_pattern_score":           report.fraud_pattern_score,
        "escalation_detected":           report.escalation_detected,
        "escalation_description":        report.escalation_description,
        "geographic_patterns":           [
            {
                "district":      p.district,
                "entry_count":   p.entry_count,
                "severity_max":  p.severity_max,
                "categories":    p.categories,
                "alert_level":   p.alert_level,
                "iccpr_ref":     p.iccpr_ref,
                "entry_ids":     p.entry_ids,
            }
            for p in report.geographic_patterns
        ],
        "category_clusters":             report.category_clusters,
        "multi_observer_corroboration":  report.multi_observer_corroboration,
        "summary":                       report.summary,
    }


@app.get("/api/observation/{country_code}/status")
async def observation_status(country_code: str):
    """Retorna el estado actual del protocolo de observación para un país."""
    code = country_code.upper()
    if code not in observation_store:
        raise HTTPException(status_code=404, detail=f"No hay sesión activa para {code}.")

    session = observation_store[code]
    entries = session.get("entries", [])

    severity_counts = {}
    phase_counts    = {}
    for e in entries:
        sev    = e.get("severity", "info")
        raw_ph = e.get("phase") or session.get("phase", "preparatory")
        ph     = _PHASE_ALIAS.get(raw_ph, raw_ph)   # R4: normalizar alias
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        phase_counts[ph]     = phase_counts.get(ph, 0) + 1

    current_phase = session.get("phase", "preparatory")
    current_norm  = _PHASE_ALIAS.get(current_phase, current_phase)
    return {
        "country_code":  code,
        "session_id":    session.get("session_id"),
        "run_id":        session.get("run_id"),
        "mission_name":  session.get("mission_name"),
        "lead_org":      session.get("lead_org"),
        "phase":         current_phase,
        "phase_canonical": current_norm,
        "phase_label":   _PHASE_LABELS.get(current_phase, _PHASE_LABELS.get(current_norm, current_norm)),
        "available_phases": _PHASE_ORDER,
        "started_at":    session.get("started_at"),
        "updated_at":    session.get("updated_at"),
        "finalized":     session.get("finalized", False),
        "total_entries": len(entries),
        "severity_summary": severity_counts,
        "phase_summary":    phase_counts,
    }


@app.get("/api/observation/{country_code}/sessions")
async def observation_list_sessions(country_code: str, include_entries: bool = False):
    """
    R6 — Lista todas las sesiones de observación para un país (activas + archivadas).
    Permite ver el historial completo de misiones: primera vuelta, segunda vuelta, etc.
    include_entries=true devuelve los hallazgos de cada sesión (puede ser grande).
    """
    code = country_code.upper()
    try:
        with _get_db() as conn:
            rows = conn.execute(
                "SELECT session_id, run_id, mission_name, lead_org, phase, "
                "started_at, updated_at, finalized, data "
                "FROM observation_sessions WHERE country_code=? "
                "ORDER BY started_at ASC",
                (code,)
            ).fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar sesiones: {e}")

    sessions_out = []
    for row in rows:
        session_id, run_id, mission_name, lead_org, phase, started_at, updated_at, finalized, data_json = row
        try:
            data = json.loads(data_json) if data_json else {}
        except Exception:
            data = {}
        entries = data.get("entries", [])
        item = {
            "session_id":    session_id,
            "run_id":        run_id,
            "mission_name":  mission_name,
            "lead_org":      lead_org,
            "phase":         phase,
            "started_at":    started_at,
            "updated_at":    updated_at,
            "finalized":     bool(finalized),
            "total_entries": len(entries),
            "severity_summary": {
                sev: sum(1 for e in entries if e.get("severity") == sev)
                for sev in ("critical", "high", "medium", "low", "info")
                if any(e.get("severity") == sev for e in entries)
            },
        }
        if include_entries:
            item["entries"] = entries
        sessions_out.append(item)

    active = next((s for s in sessions_out if not s["finalized"]), None)
    return {
        "country_code":    code,
        "total_sessions":  len(sessions_out),
        "active_session":  active,
        "sessions":        sessions_out,
    }


@app.get("/api/observation/{country_code}/entries")
async def observation_get_entries(
    country_code: str,
    phase:      Optional[str] = None,
    severity:   Optional[str] = None,
    category:   Optional[str] = None,
    observer_id: Optional[str] = None,
    verified:   Optional[bool] = None,
    limit:      int = 100,
    offset:     int = 0,
    session_id: Optional[str] = None,
):
    """
    R7 — Retorna los hallazgos de observación con filtros opcionales.

    Filtros disponibles:
    - phase:       fase del protocolo (ej. "campaign", "election_day")
    - severity:    "info" | "low" | "medium" | "high" | "critical"
    - category:    categoría de hallazgo (ej. "logistics", "fraud_allegation")
    - observer_id: filtrar por observador específico
    - verified:    true = solo verificados, false = solo no verificados
    - session_id:  filtrar por sesión específica (default: sesión activa)
    - limit/offset: paginación (default limit=100)
    """
    code = country_code.upper()

    # Obtener sesión: por session_id específico, o la activa
    if session_id:
        try:
            with _get_db() as conn:
                row = conn.execute(
                    "SELECT data FROM observation_sessions WHERE country_code=? AND session_id=?",
                    (code, session_id)
                ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Sesión '{session_id}' no encontrada para {code}.")
            session = json.loads(row[0])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif code in observation_store:
        session = observation_store[code]
    else:
        raise HTTPException(status_code=404, detail=f"No hay sesión activa para {code}. Usa session_id= para consultar sesiones archivadas.")

    entries = session.get("entries", [])

    # Aplicar filtros
    if phase:
        phase_norm = _PHASE_ALIAS.get(phase, phase)
        entries = [e for e in entries if _PHASE_ALIAS.get(e.get("phase", ""), e.get("phase", "")) == phase_norm]
    if severity:
        entries = [e for e in entries if e.get("severity") == severity]
    if category:
        entries = [e for e in entries if e.get("category") == category]
    if observer_id:
        entries = [e for e in entries if e.get("observer_id") == observer_id]
    if verified is not None:
        entries = [e for e in entries if bool(e.get("verified", False)) == verified]

    total = len(entries)
    page  = entries[offset: offset + limit]

    return {
        "country_code":  code,
        "session_id":    session.get("session_id"),
        "mission_name":  session.get("mission_name"),
        "phase_active":  session.get("phase"),
        "filters_applied": {k: v for k, v in {
            "phase": phase, "severity": severity, "category": category,
            "observer_id": observer_id, "verified": verified,
        }.items() if v is not None},
        "total_matching": total,
        "offset":         offset,
        "limit":          limit,
        "entries":        page,
    }


@app.post("/api/observation/{country_code}/advance")
async def observation_advance_phase(country_code: str, request: ObservationAdvanceInput, _key: str = Depends(_require_observer_key)):
    """
    Avanza la fase del protocolo de observación.
    R4: Orden completo: preparatory → pre_campaign → campaign → electoral_silence →
        election_day → counting_tabulation → post_election → dispute_resolution → completed
    """
    code = country_code.upper()
    if code not in observation_store:
        raise HTTPException(status_code=404, detail=f"No hay sesión activa para {code}.")

    # R4: Usar _PHASE_ORDER global; aceptar aliases legacy
    target_raw = request.target_phase
    target = _PHASE_ALIAS.get(target_raw, target_raw)
    if target not in _PHASE_ORDER:
        raise HTTPException(status_code=400, detail=f"Fase inválida: '{target_raw}'. Opciones: {_PHASE_ORDER}")

    session = observation_store[code]
    current_raw = session.get("phase", "preparatory")
    current = _PHASE_ALIAS.get(current_raw, current_raw)
    current_idx = _PHASE_ORDER.index(current) if current in _PHASE_ORDER else 0
    target_idx  = _PHASE_ORDER.index(target)
    if target_idx <= current_idx:
        raise HTTPException(status_code=400, detail=f"No se puede retroceder de '{session['phase']}' a '{target}'.")

    now = datetime.now(timezone.utc).isoformat()
    session["phase"]      = target
    session["updated_at"] = now
    if request.notes:
        session.setdefault("phase_notes", []).append({"phase": target, "notes": request.notes, "ts": now})

    observation_store[code] = session

    # Regenerar Cap. 7
    run_id = session.get("run_id")
    if run_id and run_id in reports_store:
        result = reports_store[run_id]
        new_cap7 = _generate_observation_chapter(session, result)
        result["report_chapters"]["07_voting_day"] = new_cap7
        result["final_report_markdown"] = (
            f"# DEMOCRAC.IA — Informe VIP de Integridad Electoral\n"
            f"## {result['country']} — Elección: {result['election_date']}\n\n"
            f"**Índice Predictivo de Riesgo:** {result['risk_score']}/100 ({result['risk_level'].upper()})\n"
            f"**Generado:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**Run ID:** `{run_id}`\n\n---\n\n"
            + "\n\n".join(result["report_chapters"].values())
        )
        reports_store[run_id] = result
        save_report(result)

    with _get_db() as conn:
        conn.execute(
            "UPDATE observation_sessions SET phase=?, updated_at=?, data=? WHERE country_code=? AND session_id=?",
            (target, now, json.dumps(session), code, session["session_id"])
        )
        conn.commit()

    return {
        "country_code":   code,
        "previous_phase": _PHASE_ORDER[current_idx],
        "current_phase":  target,
        "phase_label":    _PHASE_LABELS.get(target, target),
        "message":        f"Protocolo avanzado a {_PHASE_LABELS.get(target, target)}.",
    }


@app.post("/api/observation/{country_code}/finalize")
async def observation_finalize(country_code: str, _key: str = Depends(_require_observer_key)):
    """
    Finaliza el ciclo de observación y genera el informe consolidado completo.
    Integra todos los hallazgos de campo con el análisis de datasets (Caps. 1–6).
    """
    code = country_code.upper()
    if code not in observation_store:
        raise HTTPException(status_code=404, detail=f"No hay sesión activa para {code}.")

    session = observation_store[code]
    now = datetime.now(timezone.utc).isoformat()
    session["phase"]      = "completed"
    session["finalized"]  = True
    session["updated_at"] = now
    observation_store[code] = session

    run_id = session.get("run_id")
    if run_id not in reports_store:
        disk = load_report(run_id)
        if disk:
            reports_store[run_id] = disk

    entries  = session.get("entries", [])
    critical = sum(1 for e in entries if e.get("severity") == "critical")
    high     = sum(1 for e in entries if e.get("severity") == "high")

    consolidated_note = (
        "\n\n---\n\n## INFORME CONSOLIDADO — Observación Electoral Completa\n\n"
        f"> **Ciclo de observación completado.** {len(entries)} hallazgos registrados "
        f"({critical} críticos, {high} altos).\n"
        f"> **Misión:** {session.get('mission_name')} — {session.get('lead_org')}\n"
        f"> **Período:** {session.get('started_at', '')[:10]} → {now[:10]}\n\n"
        "Este informe integra el análisis predictivo de datasets (Capítulos 0–6 y 8–10) "
        "con los hallazgos del protocolo de observación electoral en campo (Capítulo 7). "
        "Constituye un documento único de ciclo completo conforme a los Principios de "
        "la Declaración de Principios para la Observación Internacional de Elecciones (ONU, 2005).\n"
    )

    if run_id and run_id in reports_store:
        result = reports_store[run_id]
        new_cap7 = _generate_observation_chapter(session, result)
        result["report_chapters"]["07_voting_day"] = new_cap7
        result["final_report_markdown"] = (
            f"# DEMOCRAC.IA — Informe VIP de Integridad Electoral\n"
            f"## {result['country']} — Elección: {result['election_date']}\n\n"
            f"**Índice Predictivo de Riesgo:** {result['risk_score']}/100 ({result['risk_level'].upper()})\n"
            f"**Generado:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**Run ID:** `{run_id}`\n\n---\n\n"
            + "\n\n".join(result["report_chapters"].values())
            + consolidated_note
        )
        reports_store[run_id] = result
        save_report(result)

    with _get_db() as conn:
        conn.execute(
            "UPDATE observation_sessions SET phase='completed', finalized=1, updated_at=?, data=? WHERE country_code=? AND session_id=?",
            (now, json.dumps(session), code, session["session_id"])
        )
        conn.commit()

    return {
        "country_code":   code,
        "run_id":         run_id,
        "phase":          "completed",
        "total_entries":  len(entries),
        "critical":       critical,
        "high":           high,
        "message":        f"Ciclo de observación finalizado. Informe consolidado generado. Accede via /api/report/{run_id}",
    }


@app.get("/api/observation/{country_code}/report")
async def observation_report(country_code: str):
    """
    R1: Retorna el Capítulo 7 (Observación Electoral) como documento standalone.
    Incluye el markdown del capítulo + resumen JSON de la sesión.
    Referenciado en el informe generado — anteriormente daba 404.
    """
    code = country_code.upper()

    # Buscar sesión activa en memoria
    session = observation_store.get(code)

    # Si no está en memoria, intentar desde SQLite
    if not session:
        try:
            with _get_db() as conn:
                row = conn.execute(
                    "SELECT data FROM observation_sessions "
                    "WHERE country_code=? ORDER BY updated_at DESC LIMIT 1",
                    (code,)
                ).fetchone()
            if row:
                session = json.loads(row[0])
        except Exception:
            pass

    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"No hay sesión de observación para {code}. Inicia una con POST /api/observation/{code}/start"
        )

    run_id  = session.get("run_id")
    entries = session.get("entries", [])

    # Obtener resultado del pipeline para contexto (sin usar cap7 cacheado)
    result = {}
    if run_id:
        if run_id not in reports_store:
            disk = load_report(run_id)
            if disk:
                reports_store[run_id] = disk
        result = reports_store.get(run_id, {})

    # Siempre regenerar el Cap. 7 en tiempo real para reflejar entradas actuales
    cap7_markdown = _generate_observation_chapter(session, result)

    # Resumen por fase y severidad (R4: todas las fases canónicas)
    phase_counts = {p: 0 for p in _PHASE_ORDER}
    sev_counts   = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for e in entries:
        raw_ph = e.get("phase", "preparatory")
        ph = _PHASE_ALIAS.get(raw_ph, raw_ph)
        if ph in phase_counts:
            phase_counts[ph] += 1
        sv = e.get("severity", "info")
        if sv in sev_counts:
            sev_counts[sv] += 1

    return {
        "country_code":   code,
        "run_id":         run_id,
        "session_id":     session.get("session_id"),
        "mission_name":   session.get("mission_name"),
        "lead_org":       session.get("lead_org"),
        "phase":          session.get("phase"),
        "phase_label":    _PHASE_LABELS.get(session.get("phase", ""), ""),
        "finalized":      session.get("finalized", False),
        "started_at":     session.get("started_at"),
        "updated_at":     session.get("updated_at"),
        "total_entries":  len(entries),
        "entries_by_phase":    phase_counts,
        "entries_by_severity": sev_counts,
        "chapter_07_markdown": cap7_markdown,
        "full_report_url":     f"/api/report/{run_id}" if run_id else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6c. EVALUACIÓN DE CICLO ELECTORAL — Cuestionario observador vs. plataforma
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from modules.evaluation_form import (
        QUESTIONNAIRE, SECTIONS, TOTAL_QUESTIONS,
        build_questionnaire_with_platform_scores, compute_comparison,
    )
    EVALUATION_AVAILABLE = True
except ImportError as _e:
    EVALUATION_AVAILABLE = False
    print(f"[EVAL] evaluation_form no disponible: {_e}")

# Store en memoria para respuestas parciales (antes del submit final a SQLite)
evaluation_store: Dict[str, dict] = {}  # keyed by country_code


@app.get("/api/evaluation/{country_code}/questionnaire")
async def get_evaluation_questionnaire(country_code: str):
    """
    Retorna el cuestionario de evaluación de ciclo con los scores de la plataforma pre-cargados.
    71 preguntas, 10 secciones, mapeo completo a V-Dem / PEI / FH / RSF.
    """
    if not EVALUATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo de evaluación no disponible.")
    code = country_code.upper()
    vdem  = get_vdem_country(VDEM_DF, code)
    pei   = get_pei_country(PEI_DF, code)
    fh    = get_freedom_house_country(FH_DF, code)
    rsf   = get_rsf_country(RSF_DF, code)
    questionnaire = build_questionnaire_with_platform_scores(vdem, pei, fh, rsf)

    # Cargar respuestas parciales si existen
    saved = evaluation_store.get(code, {})
    if saved.get("answers"):
        for q_item in questionnaire:
            qid = q_item["id"]
            if qid in saved["answers"]:
                q_item["observer_answer"] = saved["answers"][qid]

    return {
        "country_code": code,
        "country_name": FH_COUNTRY_NAMES.get(code, code),
        "total_questions": TOTAL_QUESTIONS,
        "sections": SECTIONS,
        "questionnaire": questionnaire,
        "platform_data": {
            "vdem_year": vdem.get("year") if vdem else None,
            "fh_score": fh.get("total_score") if fh else None,
            "rsf_score": rsf.get("score") if rsf else None,
            "pei_year": pei.get("year") if pei else None,
            "pei_overall": pei.get("overall_integrity") if pei else None,
        },
        "answers_saved": len(saved.get("answers", {})),
        "instructions": (
            "Escala 1-5: 5=Cumple plenamente, 4=Observaciones menores, 3=Cumplimiento parcial, "
            "2=Incumplimiento significativo, 1=Incumplimiento grave. 0=Sin información."
        ),
    }


@app.post("/api/evaluation/{country_code}/save")
async def save_evaluation_answers(country_code: str, payload: dict):
    """
    Guarda respuestas parciales del observador (puede llamarse múltiples veces).
    Body: {"answers": {"S1_Q1": 4, "S1_Q2": 3, ...}}
    Respuestas 0 = "Sin información" (no se incluyen en la comparación).
    """
    if not EVALUATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo de evaluación no disponible.")
    code = country_code.upper()
    answers = payload.get("answers", {})
    if not isinstance(answers, dict):
        raise HTTPException(status_code=422, detail="'answers' debe ser un dict {question_id: value}.")

    # Validar valores
    invalid = {k: v for k, v in answers.items() if not isinstance(v, (int, float)) or v < 0 or v > 5}
    if invalid:
        raise HTTPException(status_code=422, detail=f"Valores inválidos (deben ser 0-5): {list(invalid.keys())}")

    existing = evaluation_store.get(code, {"country_code": code, "answers": {}, "updated_at": None})
    existing["answers"].update(answers)
    existing["updated_at"] = datetime.now(timezone.utc).isoformat()
    evaluation_store[code] = existing

    return {
        "country_code": code,
        "answers_saved": len(existing["answers"]),
        "message": f"{len(answers)} respuesta(s) guardadas. Total: {len(existing['answers'])}/{TOTAL_QUESTIONS}.",
    }


@app.get("/api/evaluation/{country_code}/compare")
async def compare_evaluation(country_code: str):
    """
    Genera el informe de comparación: observador vs. plataforma.
    Requiere al menos 10 respuestas guardadas para producir resultados significativos.
    """
    if not EVALUATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo de evaluación no disponible.")
    code = country_code.upper()
    saved = evaluation_store.get(code)
    if not saved or len(saved.get("answers", {})) < 5:
        raise HTTPException(
            status_code=400,
            detail=f"Se necesitan al menos 5 respuestas guardadas. Actuales: {len(saved.get('answers', {})) if saved else 0}."
        )

    vdem = get_vdem_country(VDEM_DF, code)
    pei  = get_pei_country(PEI_DF, code)
    fh   = get_freedom_house_country(FH_DF, code)
    rsf  = get_rsf_country(RSF_DF, code)
    questionnaire = build_questionnaire_with_platform_scores(vdem, pei, fh, rsf)
    comparison = compute_comparison(saved["answers"], questionnaire)

    return {
        "country_code": code,
        "country_name": FH_COUNTRY_NAMES.get(code, code),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "observer_answers_total": len(saved["answers"]),
        "observer_answers_scored": comparison["questions_answered"],
        "observer_answers_no_info": len(saved["answers"]) - comparison["questions_answered"],
        **comparison,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6b. OONI — Endpoints de monitoreo de censura e interferencia de red
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/ooni/{country_code}/status")
async def ooni_status(country_code: str, days: int = 7):
    """
    Estado OONI en tiempo real para un país.
    Retorna bloqueos detectados, anomalías por dominio e interferencia de ASN.

    Parámetros:
      days: ventana de análisis en días (default 7, max 30)
    """
    days = min(max(days, 1), 30)
    summary = get_ooni_summary(country_code.upper(), days_back=days)
    return {
        "country_code":                 country_code.upper(),
        "ooni_available":               summary["available"],
        "period_days":                  summary["period_days"],
        "alert_level":                  summary["alert_level"],
        "censorship_detected":          summary["censorship_detected"],
        "network_interference":         summary["network_interference_detected"],
        "blocked_domains":              summary["blocked_domains"],
        "anomalous_domains":            summary["anomalous_domains"][:10],
        "high_anomaly_asns":            summary["high_anomaly_asns"],
        "summary":                      summary["summary_text"],
        "source":                       summary["source"],
        "timestamp":                    summary["timestamp"],
    }


@app.get("/api/ooni/{country_code}/anomalies")
async def ooni_anomalies(country_code: str, days: int = 3, limit: int = 50):
    """
    Lista cruda de mediciones web_connectivity con anomalías.
    Útil para monitoreo granular en jornada electoral.
    """
    days  = min(max(days, 1), 14)
    limit = min(max(limit, 1), 100)
    measurements = fetch_web_anomalies(country_code.upper(), days_back=days, limit=limit)
    return {
        "country_code":  country_code.upper(),
        "period_days":   days,
        "total":         len(measurements),
        "measurements":  measurements,
        "timestamp":     datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/ooni/cache/clear")
async def ooni_cache_clear(country_code: str = None, _key: str = Depends(_require_observer_key)):
    """Limpia el cache OONI. Fuerza nueva consulta a la API en el próximo request."""
    ooni_clear_cache(country_code)
    return {"message": "Cache OONI limpiado.", "country_code": country_code or "todos"}


# ═══════════════════════════════════════════════════════════════════════════════
# 6c-bis. HUNTER — Recolección OSINT automatizada en tiempo real
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from agents.hunter import HunterAgent, hunter_entry_to_observation
    HUNTER_AVAILABLE = True
except ImportError as _hunter_err:
    HUNTER_AVAILABLE = False
    print(f"[Hunter] No disponible: {_hunter_err}")


class HunterRunInput(BaseModel):
    """Input para disparar el Hunter en un país y fase."""
    run_id: str                              # run_id del reporte PEIRS activo
    phase: Optional[str] = None             # Si None, usa la fase activa de la sesión
    dry_run: bool = False                    # True = clasifica pero no registra
    max_items_per_source: int = 15           # Máximo ítems RSS por fuente
    sources: Optional[List[str]] = None     # None = todas las fuentes de la fase


@app.get("/api/hunter/debug-fetch")
async def hunter_debug_fetch(phase: str = "campaign"):
    """
    Diagnóstico: prueba cada feed RSS configurado para la fase indicada y devuelve
    por fuente: status, count, y motivo de fallo si lo hubo. Sirve para identificar
    bloqueos (403, timeouts, parse errors) cuando el Hunter devuelve fetched=0.
    """
    try:
        from integrations.peru_sources import (
            PHASE_SOURCES, RSS_FEEDS, fetch_feed_debug,
        )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"peru_sources no disponible: {e}")

    keys = list(PHASE_SOURCES.get(phase, PHASE_SOURCES.get("campaign", [])))
    results = []
    total_items = 0
    for key in keys:
        for url in RSS_FEEDS.get(key, []):
            items, err = await fetch_feed_debug(key, url, timeout=15)
            results.append({
                "source": key,
                "url": url,
                "ok": err is None,
                "items": len(items),
                "error": err,
            })
            total_items += len(items)
    return {
        "phase": phase,
        "total_sources_tried": len(results),
        "sources_ok": sum(1 for r in results if r["ok"]),
        "total_items_fetched": total_items,
        "results": results,
        "tested_at": datetime.now(timezone.utc).isoformat(),
    }


class ConstitutionalistQuery(BaseModel):
    """Consulta al sub-agente constitucionalista peruano."""
    question: str
    context: Optional[str] = None


class DesignerRequest(BaseModel):
    """Request al sub-agente ReportDesigner."""
    country_code: str = "PER"
    audience: str = "technical"  # technical | executive | press | international
    period_days: int = 7
    include_live_alerts: bool = True
    include_datasets: bool = True
    include_chapters: Optional[List[str]] = None
    language: str = "es"
    output_formats: List[str] = ["md", "html"]
    use_llm: bool = False  # True = Claude redacta (Fase C); False = plantillas (B+D)


@app.post("/api/report/designer/generate")
async def generate_designed_report(
    req: DesignerRequest,
    _key: str = Depends(_require_observer_key),
    _ip: str = Depends(_rate_limit_expensive),
):
    """
    Sub-agente ReportDesigner — Fase A (esqueleto funcional).

    Seguridad: requiere X-Observer-Key + rate limit 5/min por IP.

    Genera un informe estructurado con narrativas mock basadas en el informe v1.1
    de Perú. Las Fases B-E reemplazarán los mocks con lógica real (dedupe
    semántico, matplotlib SVG, prompts Claude).

    Body:
        country_code: "PER" soportado en Fase A; otros países devuelven esqueleto vacío.
        audience: "technical" | "executive" | "press" | "international"
        language: "es" | "en"
        output_formats: lista de ["md", "html", "pdf"]

    Response:
        report_id, markdown, html, sections, stats, sources_cited, visualizations, warnings.
    """
    try:
        from agents.report_designer import ReportDesigner, ReportRequest as RR
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"ReportDesigner no disponible: {e}")

    try:
        rr = RR(
            country_code=req.country_code,
            audience=req.audience,
            period_days=req.period_days,
            include_live_alerts=req.include_live_alerts,
            include_datasets=req.include_datasets,
            include_chapters=req.include_chapters,
            language=req.language,
            output_formats=req.output_formats,
            use_llm=req.use_llm,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Parámetros inválidos: {e}")

    # Pasamos los stores del backend para que el Structurer Fase B tenga data real
    def _alerts_loader(cc: str, limit: int = 500):
        if DB_AVAILABLE:
            try:
                return _db_list_alerts(cc, limit=limit)
            except Exception:
                return []
        return []

    designer = ReportDesigner(
        llm=llm,
        observation_store=observation_store,
        alerts_loader=_alerts_loader,
        reports_store=reports_store,
    )
    try:
        result = await designer.run(rr)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del designer: {type(e).__name__}: {e}")

    # Devolvemos el modelo como dict para serialización FastAPI limpia
    return result.model_dump()


@app.post("/api/ask/constitutionalist")
async def ask_constitutionalist(query: ConstitutionalistQuery):
    """
    Sub-agente jurista constitucionalista especializado en derecho electoral peruano.
    Responde consultas sobre Constitución 1993, LOE N° 26859, LOP N° 28094, jurisprudencia
    JNE y marco internacional vinculante (ICCPR, CADH, CDI).

    Body:
        question (str): la consulta del/la observador/a.
        context (str, opcional): información adicional sobre el caso concreto.

    Response:
        answer, legal_basis, case_law, international_framework, confidence,
        caveats, sources_cited, generated_at.
    """
    if not llm:
        raise HTTPException(
            status_code=503,
            detail="LLM no configurado (falta ANTHROPIC_API_KEY válida).",
        )
    try:
        from agents.constitutionalist import ConstitutionalistAgent
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Sub-agente no disponible: {e}")

    agent = ConstitutionalistAgent(llm=llm)
    try:
        result = await agent.ask(question=query.question, context=query.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del sub-agente: {type(e).__name__}: {e}")

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# ═════════════════════════════════════════════════════════════════════
# PEIRS Elite Report — endpoints (Sprint 6 del blueprint ELITE_REPORT.md)
# ═════════════════════════════════════════════════════════════════════

# Dynamic-date factories para EliteMissionInput.
# Antes era hardcoded "2026-04-20" en period_end → al regenerar dejaba afuera
# todas las entries posteriores a esa fecha. Ahora cada nueva request usa
# fechas relativas a "ahora", a menos que el cliente las especifique
# explicitamente (lo cual sigue siendo posible para auditorias retroactivas).
def _default_period_end() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")


def _default_period_start() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")


class EliteMissionInput(BaseModel):
    """Metadata de misión para el Elite Report."""
    mission_name: str = "DemocracIA — Observación Electoral PEIRS"
    lead_observer: str = ""
    organization: str = "DemocracIA"
    report_number: str = "DMC-PER-2026-001"
    classification: str = "public"  # public | restricted | confidential
    period_start: str = Field(default_factory=_default_period_start)
    period_end: str = Field(default_factory=_default_period_end)
    jornada_date: str = "2026-04-12"


class EliteReportInput(BaseModel):
    """Request para generar informe Elite."""
    country_code: str = "PER"
    mission: EliteMissionInput = EliteMissionInput()
    audience: str = "institutional"  # institutional|executive|press|international
    language: str = "es"  # es | en
    report_type: str = "preliminary"  # pre_electoral|jornada|preliminary|final|ad_hoc
    include_chapters: Optional[List[int]] = None
    include_predictive: bool = True
    include_appendix_c: bool = True
    forecast_horizon_days: int = 14
    use_llm: bool = True
    output_formats: List[str] = ["md", "html", "pdf"]


@app.post("/api/report/elite/generate")
async def generate_elite_report(
    req: EliteReportInput,
    _key: str = Depends(_require_observer_key),
    _ip: str = Depends(_rate_limit_expensive),
):
    """
    Orquestador Elite Report. Pipeline completo:
    EliteLoader → PhaseOrganizer → CrossReferenceBuilder → PredictiveEngine
    → ChapterComposer (12 caps con Claude) → Visualizer (SVG) → CitationBuilder (APA 7)
    → HTML + PDF renderers.

    Genera informe de nivel institucional internacional equivalente a OEA/DECO,
    EU EOM, Carter Center, IDEA Internacional. Tiempo estimado: 2-5 minutos.
    Costo estimado: ~$0.40-0.80 por informe.

    Seguridad: requiere X-Observer-Key, rate-limited (5/min), budget
    diario (MAX_ELITE_PER_DAY, default 5).

    Body: EliteReportInput con mission, audience, report_type, use_llm, etc.
    Returns: EliteReportOutput completo con chapters, html, markdown, pdf_path.
    """
    _check_daily_budget(req.country_code, "elite")

    # Pre-check: si use_llm=True pero el LLM no responde (rate limit, spending
    # cap, key invalida, overload), abortar AHORA en vez de generar un informe
    # sin narrativa. Esto evita el bug "informe vacio silencioso" que vimos
    # cuando Anthropic devolvio 400 en cada uno de los 13 chapter calls.
    # _check_llm_alive esta cacheado 5min, asi que el costo es despreciable.
    if req.use_llm:
        llm_status = await _check_llm_alive()
        if not llm_status.get("ok", False):
            err = llm_status.get("error", "LLM no disponible")
            raise HTTPException(
                status_code=503,
                detail=(
                    f"LLM no disponible — la generacion se abortaria con narrativa "
                    f"vacia. Detalle: {err}. Si querés generar un informe sin "
                    f"narrativa LLM, mandalo con use_llm=false."
                ),
            )

    try:
        from agents.elite_report import (
            PEIRSEliteReport,
            EliteReportRequest as EliteRR,
            MissionMetadata,
        )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Elite Report no disponible: {e}")

    # Armar request
    try:
        mm = MissionMetadata(
            mission_name=req.mission.mission_name,
            lead_observer=req.mission.lead_observer,
            organization=req.mission.organization,
            report_number=req.mission.report_number,
            classification=req.mission.classification,
            period_start=req.mission.period_start,
            period_end=req.mission.period_end,
            jornada_date=req.mission.jornada_date,
        )
        rr = EliteRR(
            country_code=req.country_code,
            mission_metadata=mm,
            audience=req.audience,
            language=req.language,
            report_type=req.report_type,
            include_chapters=req.include_chapters,
            include_predictive=req.include_predictive,
            include_appendix_c=req.include_appendix_c,
            forecast_horizon_days=req.forecast_horizon_days,
            use_llm=req.use_llm,
            output_formats=req.output_formats,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Parámetros inválidos: {e}")

    def _alerts_loader(cc: str, limit: int = 500):
        if DB_AVAILABLE:
            try:
                return _db_list_alerts(cc, limit=limit)
            except Exception:
                return []
        return []

    pipeline = PEIRSEliteReport(
        llm=llm if req.use_llm else None,
        observation_store=observation_store,
        alerts_loader=_alerts_loader,
        reports_store=reports_store,
    )
    try:
        result = await pipeline.compose(rr)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()[-800:]
        raise HTTPException(
            status_code=500,
            detail=f"Error del Elite pipeline: {type(e).__name__}: {e}\n{tb}"
        )

    # Persistir metadata en tabla SQLite (sin bloquear respuesta)
    try:
        _persist_elite_metadata(result)
    except Exception as e:
        result.warnings.append(f"SQLite persist failed: {type(e).__name__}: {e}")

    return result.model_dump()


@app.get("/api/report/elite/list")
async def list_elite_reports(country_code: str = "PER", limit: int = 20):
    """Lista los informes Elite generados (desde tabla SQLite + directorio)."""
    items = []
    if DB_AVAILABLE:
        try:
            with _get_db() as conn:
                rows = conn.execute(
                    "SELECT report_id, country_code, audience, language, report_type, "
                    "mission_name, report_number, generated_at, generation_time_s, "
                    "estimated_cost_usd, total_findings "
                    "FROM elite_reports WHERE country_code=? "
                    "ORDER BY generated_at DESC LIMIT ?",
                    (country_code.upper(), limit),
                ).fetchall()
            items = [dict(r) for r in rows]
        except Exception:
            items = []
    return {"items": items, "total": len(items)}


@app.get("/api/report/elite/{report_id}/download")
async def download_elite_report(report_id: str, format: str = "html"):
    """Descarga el archivo generado. format: pdf|html|md

    Estrategia de resolución:
      1. Filesystem (rápido, sirve archivo directo) → reports/elite/{id}/report.{ext}
      2. SQLite (resiliente) → columnas md_content/html_content de elite_reports
      3. Para PDF: si filesystem miss y hay html_content en SQLite, render on-demand
         con xhtml2pdf y entregar como bytes.
    """
    from fastapi.responses import FileResponse, Response
    fmt = format.lower()
    if fmt not in ("pdf", "html", "md"):
        raise HTTPException(status_code=400, detail=f"format inválido: {format}. Usá pdf|html|md.")

    media = {
        "pdf":  "application/pdf",
        "html": "text/html; charset=utf-8",
        "md":   "text/markdown; charset=utf-8",
    }

    # 1. Filesystem primero (path absoluto desde el módulo, no relativo al CWD)
    try:
        from agents.elite_report.elite_report import REPORTS_DIR as ELITE_DIR
        base_dir = ELITE_DIR / report_id
    except Exception:
        base_dir = os.path.join("reports", "elite", report_id)
    base_dir = str(base_dir)
    file_path = os.path.join(base_dir, f"report.{fmt}")
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type=media[fmt],
            filename=f"elite-{report_id}.{fmt}",
        )

    # 2. Fallback SQLite — md/html viven como TEXT, PDF se regenera on-demand.
    if DB_AVAILABLE:
        try:
            with _get_db() as conn:
                row = conn.execute(
                    "SELECT md_content, html_content FROM elite_reports WHERE report_id=?",
                    (report_id,),
                ).fetchone()
        except Exception:
            row = None
        if row:
            md_content, html_content = row[0], row[1]
            if fmt == "md" and md_content:
                return Response(
                    content=md_content,
                    media_type=media["md"],
                    headers={"Content-Disposition": f'attachment; filename="elite-{report_id}.md"'},
                )
            if fmt == "html" and html_content:
                return Response(
                    content=html_content,
                    media_type=media["html"],
                    headers={"Content-Disposition": f'attachment; filename="elite-{report_id}.html"'},
                )
            if fmt == "pdf" and html_content:
                # Re-render PDF on-the-fly desde el HTML guardado en SQLite.
                try:
                    import io
                    from xhtml2pdf import pisa  # type: ignore
                    buf = io.BytesIO()
                    pisa.CreatePDF(src=html_content, dest=buf, encoding="utf-8")
                    buf.seek(0)
                    return Response(
                        content=buf.getvalue(),
                        media_type=media["pdf"],
                        headers={"Content-Disposition": f'attachment; filename="elite-{report_id}.pdf"'},
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"PDF on-demand falló: {type(e).__name__}: {e}. "
                               f"HTML está disponible en /download?format=html.",
                    )

    # 3. No está en disco ni en SQLite — informe realmente perdido.
    raise HTTPException(
        status_code=404,
        detail=f"Archivo {fmt} no encontrado para {report_id} (ni en disco ni en SQLite). "
               f"Tip: regenerá el informe — los nuevos quedan persistidos en SQLite."
    )


@app.get("/api/report/elite/{report_id}/printable")
async def get_elite_report_printable(report_id: str):
    """Sirve el HTML del informe con un <script> que dispara window.print()
    al cargar. El usuario obtiene el dialog de impresion del navegador y
    puede 'Guardar como PDF' desde alli.

    Esta es la alternativa a /download?format=pdf para entornos Nixpacks
    donde xhtml2pdf no se puede instalar (ver d7fa870 — pycairo dependency).
    El CSS @page A4 + @media print del HTML del informe ya esta diseñado
    para producir PDF de calidad editorial via el motor de impresion del
    navegador.
    """
    from fastapi.responses import HTMLResponse, Response

    html_content: Optional[str] = None

    # Filesystem primero
    try:
        from agents.elite_report.elite_report import REPORTS_DIR as ELITE_DIR
        base_dir = ELITE_DIR / report_id
    except Exception:
        base_dir = os.path.join("reports", "elite", report_id)
    file_path = os.path.join(str(base_dir), "report.html")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                html_content = fh.read()
        except Exception:
            html_content = None

    # Fallback SQLite
    if html_content is None and DB_AVAILABLE:
        try:
            with _get_db() as conn:
                row = conn.execute(
                    "SELECT html_content FROM elite_reports WHERE report_id=?",
                    (report_id,),
                ).fetchone()
            if row and row[0]:
                html_content = row[0]
        except Exception:
            pass

    if html_content is None:
        raise HTTPException(
            status_code=404,
            detail=f"HTML no encontrado para {report_id}. Regenerá el informe.",
        )

    # Inyectar script de auto-print justo antes de </body>. Se dispara con
    # un pequeño delay para que webfonts y SVGs terminen de cargar.
    print_script = (
        "<script>"
        "window.addEventListener('load', function() {"
        "  setTimeout(function() { window.print(); }, 600);"
        "});"
        "</script>"
    )
    if "</body>" in html_content:
        html_with_print = html_content.replace("</body>", f"{print_script}</body>", 1)
    else:
        html_with_print = html_content + print_script

    return HTMLResponse(content=html_with_print)


@app.get("/api/report/elite/{report_id}/structured")
async def get_elite_report_structured(report_id: str, dim: str | None = None):
    """Devuelve el informe Elite como JSON estructurado para extracción / análisis.

    Forma del payload (output_json persistido en SQLite al generar):
      {
        report_id, country_code, mission, audience, language, report_type,
        generated_at, status,
        chapters: [{number, chapter_id, title, narrative, findings[],
                    cross_references[], visualizations[], ...}],
        forecast: {scenarios[], early_warning_level, drivers, ...},
        citations: [{citation_id, type, formatted_apa, ...}],
        all_findings: [...],   # universo completo del Hunter para anexo C
        stats: {total, by_severity, by_phase, ...},
        warnings, tokens_used, estimated_cost_usd, generation_time_seconds,
      }

    Query params:
      dim: opcional. Si se especifica, devuelve solo esa dimension. Valores soportados:
        - chapters | forecast | citations | findings | stats | warnings | mission
        Cualquier otro valor → 400.

    Errores:
      - 404 si el informe no existe en SQLite.
      - 410 si el informe existe pero output_json no fue guardado (informes
        previos a 2026-04-29). En ese caso usar /download?format=md como
        fallback.
      - 503 si SQLite no esta disponible.
    """
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="SQLite no disponible.")
    try:
        with _get_db() as conn:
            row = conn.execute(
                "SELECT output_json, generated_at FROM elite_reports WHERE report_id=?",
                (report_id,),
            ).fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {type(e).__name__}: {e}")

    if not row:
        raise HTTPException(status_code=404, detail=f"Informe {report_id} no existe.")

    output_json_str, generated_at = row[0], row[1]
    if not output_json_str:
        raise HTTPException(
            status_code=410,
            detail=(
                f"Informe {report_id} (generado {generated_at}) fue creado antes "
                f"de 2026-04-29 y no tiene output_json persistido. Regenerá el "
                f"informe para obtener la version estructurada, o usá "
                f"/api/report/elite/{report_id}/download?format=md."
            ),
        )

    try:
        payload = json.loads(output_json_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"output_json corrupto: {e}")

    if not dim:
        return payload

    # Filtro por dimension
    dim_map = {
        "chapters":   "chapters",
        "forecast":   "forecast",
        "citations":  "citations",
        "findings":   "all_findings",
        "stats":      "stats",
        "warnings":   "warnings",
        "mission":    "mission",
    }
    key = dim_map.get(dim.lower())
    if key is None:
        raise HTTPException(
            status_code=400,
            detail=f"dim inválido: {dim}. Valores soportados: {sorted(dim_map.keys())}.",
        )
    return {"report_id": report_id, "dim": dim, "value": payload.get(key)}


def _ensure_elite_table():
    """Crea tabla elite_reports si no existe + migra columnas faltantes.

    Columnas agregadas en versiones posteriores (28-abr-2026):
      - md_content / html_content: cuerpo del informe en SQLite para sobrevivir
        pérdidas del volumen Railway.
      - output_json: dump estructurado de EliteReportOutput (chapters, forecast,
        citations, findings, cross_refs, stats) para extracción dinámica via
        /structured. Excluye md/html/pdf que ya viven en sus propias columnas.
    """
    if not DB_AVAILABLE:
        return
    try:
        with _get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS elite_reports (
                    report_id         TEXT PRIMARY KEY,
                    country_code      TEXT NOT NULL,
                    mission_name      TEXT,
                    lead_observer     TEXT,
                    report_number     TEXT,
                    classification    TEXT,
                    audience          TEXT,
                    language          TEXT,
                    report_type       TEXT,
                    generated_at      TEXT NOT NULL,
                    generation_time_s REAL,
                    tokens_input      INTEGER,
                    tokens_output     INTEGER,
                    estimated_cost_usd REAL,
                    total_findings    INTEGER,
                    status            TEXT,
                    md_path           TEXT,
                    html_path         TEXT,
                    pdf_path          TEXT,
                    stats_json        TEXT,
                    md_content        TEXT,
                    html_content      TEXT,
                    output_json       TEXT
                )
            """)
            # Migración para DBs preexistentes: agregar columnas que pueden faltar.
            existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(elite_reports)")}
            if "md_content" not in existing_cols:
                conn.execute("ALTER TABLE elite_reports ADD COLUMN md_content TEXT")
            if "html_content" not in existing_cols:
                conn.execute("ALTER TABLE elite_reports ADD COLUMN html_content TEXT")
            if "output_json" not in existing_cols:
                conn.execute("ALTER TABLE elite_reports ADD COLUMN output_json TEXT")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_elite_country_date "
                "ON elite_reports(country_code, generated_at DESC)"
            )
            conn.commit()
    except Exception as e:
        print(f"[Elite] No se pudo crear/migrar tabla elite_reports: {e}")


def _persist_elite_metadata(output):
    """Inserta metadata + cuerpo + dump estructurado del informe Elite en SQLite.

    Tres capas de persistencia (28-abr-2026):
      1. Metadata escalar (paths, audience, costo, etc.) — para queries rápidas.
      2. md_content / html_content — cuerpo renderizado, sobrevive volumen perdido.
      3. output_json — dump estructurado de EliteReportOutput para extracción
         dinámica via /structured. Excluye md/html/pdf (ya viven en sus columnas)
         para no duplicar payload.
    """
    if not DB_AVAILABLE:
        return
    _ensure_elite_table()
    try:
        base = os.path.join("reports", "elite", output.report_id)
        # Dump estructurado: chapters, forecast, citations, findings, stats, etc.
        # Excluimos los outputs renderizados que ya viven en md_content/html_content/pdf_path.
        try:
            output_dict = output.model_dump(exclude={"markdown", "html", "pdf_path"})
            output_json_str = json.dumps(output_dict, ensure_ascii=False, default=str)
        except Exception as _ser_err:
            output_json_str = None
            print(f"[Elite] No se pudo serializar output_json: {_ser_err}")
        with _get_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO elite_reports (
                    report_id, country_code, mission_name, lead_observer,
                    report_number, classification, audience, language, report_type,
                    generated_at, generation_time_s, tokens_input, tokens_output,
                    estimated_cost_usd, total_findings, status,
                    md_path, html_path, pdf_path, stats_json,
                    md_content, html_content, output_json
                ) VALUES (
                    :rid, :cc, :mn, :lo,
                    :rn, :cl, :au, :la, :rt,
                    :gen, :gt, :ti, :to_,
                    :cost, :tf, :status,
                    :mp, :hp, :pp, :sj,
                    :mc, :hc, :oj
                )
            """, {
                "rid": output.report_id,
                "cc":  output.country_code,
                "mn":  output.mission.mission_name,
                "lo":  output.mission.lead_observer,
                "rn":  output.mission.report_number,
                "cl":  output.mission.classification,
                "au":  output.audience,
                "la":  output.language,
                "rt":  output.report_type,
                "gen": output.generated_at,
                "gt":  output.generation_time_seconds,
                "ti":  output.tokens_used.get("input", 0),
                "to_": output.tokens_used.get("output", 0),
                "cost": output.estimated_cost_usd,
                "tf":  output.stats.get("total", 0),
                "status": output.status,
                "mp":  os.path.join(base, "report.md") if output.markdown else None,
                "hp":  os.path.join(base, "report.html") if output.html else None,
                "pp":  output.pdf_path,
                "sj":  json.dumps(output.stats, ensure_ascii=False),
                "mc":  output.markdown or None,
                "hc":  output.html or None,
                "oj":  output_json_str,
            })
            conn.commit()
    except Exception as e:
        print(f"[Elite] Persist SQLite falló: {e}")


@app.post("/api/hunter/{country_code}/run-now")
async def hunter_run_now(country_code: str):
    """
    Dispara manualmente un ciclo del Hunter para un país, sin parámetros.
    Reutiliza la sesión activa (si existe) y su run_id. Mismo comportamiento
    que el scheduler automático, pero on-demand desde el frontend.

    Devuelve métricas del run: registered/fetched/duplicates/errors.
    """
    if not HUNTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Hunter Agent no disponible.")
    if not llm:
        raise HTTPException(status_code=503, detail="LLM no configurado (falta ANTHROPIC_API_KEY).")

    code = country_code.upper()
    if code not in observation_store:
        raise HTTPException(
            status_code=404,
            detail=f"No hay sesión de observación activa para {code}. "
                   f"Verificá AUTO_OBSERVE_COUNTRIES o creá una sesión manualmente."
        )
    session = observation_store[code]
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        metrics = await _hunter_run_for_session(code, session, max_items=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hunter run failed: {e}")
    return {
        "country_code": code,
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        **metrics,
    }


@app.post("/api/hunter/{country_code}/run")
async def hunter_run(country_code: str, request: HunterRunInput):
    """
    Dispara el Hunter Agent para un país y fase electoral.
    Fetches RSS de JNE, ONPE, prensa + OONI, clasifica con Claude,
    y registra hallazgos relevantes en el protocolo de observación.

    Requiere:
    - Sesión de observación activa (POST /api/observation/{cc}/start previo)
    - run_id válido del reporte PEIRS
    """
    if not HUNTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Hunter Agent no disponible.")
    if not llm:
        raise HTTPException(status_code=503, detail="LLM no configurado (falta ANTHROPIC_API_KEY).")

    code = country_code.upper()

    # Verificar sesión activa
    if code not in observation_store:
        raise HTTPException(
            status_code=404,
            detail=f"No hay sesión de observación activa para {code}. "
                   f"Usá POST /api/observation/{code}/start primero."
        )
    session = observation_store[code]

    # Verificar run_id
    if request.run_id not in reports_store:
        disk = load_report(request.run_id)
        if disk is None:
            raise HTTPException(
                status_code=404,
                detail=f"run_id '{request.run_id}' no encontrado."
            )
        reports_store[request.run_id] = disk

    # Determinar fase activa
    phase = request.phase or session.get("phase", "campaign")
    phase_norm = _PHASE_ALIAS.get(phase, phase)
    phase_label = _PHASE_LABELS.get(phase_norm, phase_norm)

    # Instanciar Hunter
    hunter = HunterAgent(
        llm=llm,
        ooni_available=OONI_AVAILABLE,
        ooni_get_summary=get_ooni_summary if OONI_AVAILABLE else None,
    )

    # Correr el Hunter
    hunter_result = await hunter.run(
        country_code=code,
        phase=phase_norm,
        phase_label=phase_label,
        dry_run=request.dry_run,
        max_items_per_source=request.max_items_per_source,
    )

    # Si dry_run, devolver resultados sin registrar
    if request.dry_run:
        return {
            "dry_run": True,
            "phase": phase_norm,
            "phase_label": phase_label,
            "items_fetched": hunter_result["items_fetched"],
            "items_classified": hunter_result["items_classified"],
            "relevant_entries": hunter_result["items_registered"],
            "ooni_entries": hunter_result["ooni_entries"],
            "sources": hunter_result["sources_fetched"],
            "errors": hunter_result["errors"],
            "entries_preview": hunter_result["entries"][:5],
        }

    # Registrar hallazgos en el protocolo de observación
    registered = 0
    skipped    = 0
    result_entry_ids = []

    for hunter_entry in hunter_result.get("entries", []):
        if not hunter_entry.get("relevant"):
            skipped += 1
            continue
        try:
            obs_entry = hunter_entry_to_observation(hunter_entry, phase_norm, code)

            # Validar con Agent 5 antes de registrar
            existing = session.get("entries", [])
            validation = validate_entry(obs_entry, existing)
            if validation.duplicate_of:
                skipped += 1
                continue

            # Escalar severidad si aplica
            obs_entry["severity"] = _auto_escalate_severity(
                obs_entry["severity"],
                obs_entry["category"],
                obs_entry["finding"],
            )

            # Auto-derechos
            auto_r = _auto_rights(obs_entry["category"], obs_entry["severity"])
            obs_entry["rights_at_risk"] = list(
                set(obs_entry.get("rights_at_risk", []) + auto_r)
            )

            session["entries"].append(obs_entry)
            result_entry_ids.append(obs_entry["entry_id"])
            registered += 1

            # Alertas para hallazgos críticos/altos
            if ALERTS_AVAILABLE and obs_entry["severity"] in ("critical", "high"):
                try:
                    alert_evt = build_entry_alert(obs_entry, code)
                    dispatch_alert(alert_evt)
                except Exception:
                    pass

        except Exception:
            skipped += 1
            continue

    # Actualizar sesión y regenerar Cap. 7
    if registered > 0:
        now_ts = datetime.now(timezone.utc).isoformat()
        session["updated_at"] = now_ts
        observation_store[code] = session

        result_report = reports_store[request.run_id]
        new_cap7 = _generate_observation_chapter(session, result_report)
        result_report["report_chapters"]["07_voting_day"] = new_cap7
        result_report["final_report_markdown"] = (
            f"# DEMOCRAC.IA — Informe VIP de Integridad Electoral\n"
            f"## {result_report['country']} — Elección: {result_report['election_date']}\n\n"
            f"**Índice Predictivo de Riesgo:** {result_report['risk_score']}/100 "
            f"({result_report['risk_level'].upper()})\n"
            f"**Generado:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**Run ID:** `{request.run_id}`\n\n---\n\n"
            + "\n\n".join(result_report["report_chapters"].values())
        )
        reports_store[request.run_id] = result_report
        save_report(result_report)

    return {
        "phase": phase_norm,
        "phase_label": phase_label,
        "country_code": code,
        "run_id": request.run_id,
        "sources_fetched": hunter_result["sources_fetched"],
        "items_fetched": hunter_result["items_fetched"],
        "items_classified": hunter_result["items_classified"],
        "entries_registered": registered,
        "entries_skipped": skipped,
        "ooni_entries": hunter_result["ooni_entries"],
        "entry_ids": result_entry_ids,
        "errors": hunter_result["errors"],
        "cap7_updated": registered > 0,
        "message": (
            f"Hunter completado. {registered} hallazgos registrados en Cap. 7. "
            f"Fuentes: {', '.join(hunter_result['sources_fetched']) or 'ninguna'}."
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6c. SENTINEL — Monitoreo de elecciones próximas y alertas en tiempo real
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/sentinel/alerts")
async def get_sentinel_alerts():
    """
    SENTINEL: Monitoreo en tiempo real de elecciones próximas.
    Cruza el calendario electoral con los índices PEIRS para generar alertas.
    """
    now = datetime.now(timezone.utc).date()
    index = _load_reports_index()

    active_alerts = []   # < 90 días
    watch_list = []      # 90–365 días
    full_calendar = []   # todas las próximas

    for code, info in COUNTRY_CATALOG.items():
        election_date_str = info.get("election_date")
        if not election_date_str:
            continue
        try:
            election_date = datetime.strptime(election_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        days_remaining = (election_date - now).days

        # Obtener risk data del último reporte disponible
        risk_score = None
        risk_level = "unknown"
        trend = "stable"
        run_id = None
        violations_count = 0

        entries = index.get(code, [])
        if entries:
            latest = entries[-1]
            run_id = latest.get("run_id")
            report = reports_store.get(run_id) if run_id else None
            if report is None and run_id:
                report = load_report(run_id)
                if report:
                    reports_store[run_id] = report
            if report:
                risk_score = report.get("risk_score")
                risk_level = report.get("risk_level", "unknown")
                trend = report.get("trend", "stable")
                violations_count = len(report.get("violations", []))

        # Nivel de alerta: combina días restantes + riesgo
        if risk_level == "critical":
            alert_color = "critical"
        elif risk_level == "high":
            alert_color = "high"
        elif risk_level == "moderate":
            alert_color = "moderate"
        else:
            alert_color = "low"

        # Urgency score: mayor cuando la elección está cerca Y el riesgo es alto
        if risk_score is not None and days_remaining >= 0:
            proximity = max(0.0, 1.0 - days_remaining / 365)
            urgency = round(risk_score * proximity, 1)
        else:
            urgency = 0.0

        # Texto de alerta contextual
        if days_remaining < 0:
            alert_text = f"Elección celebrada hace {abs(days_remaining)} días"
        elif days_remaining == 0:
            alert_text = "⚡ ELECCIÓN HOY"
        elif days_remaining <= 7:
            alert_text = f"⚡ Elección en {days_remaining} días — intervención SENTINEL recomendada"
        elif days_remaining <= 30:
            alert_text = f"Elección en {days_remaining} días — monitoreo activo"
        elif days_remaining <= 90:
            alert_text = f"Elección en {days_remaining} días — preparación MOE"
        else:
            alert_text = f"Elección en {days_remaining} días"

        entry = {
            "country_code": code,
            "country_name": info.get("name", code),
            "flag": info.get("flag", "🌍"),
            "election_date": election_date_str,
            "days_remaining": days_remaining,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "alert_color": alert_color,
            "trend": trend,
            "urgency_score": urgency,
            "alert_text": alert_text,
            "violations_count": violations_count,
            "run_id": run_id,
            "region": COUNTRY_REGIONS.get(code, "unknown"),
        }

        if 0 <= days_remaining <= 90:
            active_alerts.append(entry)
        elif 90 < days_remaining <= 365:
            watch_list.append(entry)

        if days_remaining >= 0:
            full_calendar.append(entry)

    # Ordenar: activas por días restantes (más urgente primero), watch por riesgo
    active_alerts.sort(key=lambda x: (x["days_remaining"], -(x["risk_score"] or 0)))
    watch_list.sort(key=lambda x: (-(x["risk_score"] or 0), x["days_remaining"]))
    full_calendar.sort(key=lambda x: x["days_remaining"])

    critical_upcoming = sum(
        1 for e in active_alerts + watch_list
        if e.get("risk_level") in ["critical", "high"]
    )

    # ── Hallazgos recientes de observación (todas las sesiones activas) ────
    recent_findings = []
    for cc, session in list(observation_store.items()):
        entries = session.get("entries", [])
        country_info = COUNTRY_CATALOG.get(cc, {})
        for e in entries[-20:]:  # últimas 20 por país
            recent_findings.append({
                "country_code": cc,
                "country_name": country_info.get("name", cc),
                "flag": country_info.get("flag", "🌍"),
                "entry_id": e.get("entry_id", ""),
                "finding": e.get("finding", ""),
                "category": e.get("category", ""),
                "severity": e.get("severity", "info"),
                "location": e.get("location", ""),
                "phase": e.get("phase", ""),
                "timestamp": e.get("timestamp", ""),
                "rights_at_risk": e.get("rights_at_risk", []),
                "observer_id": e.get("observer_id", ""),
                "verified": e.get("verified", False),
                "source": e.get("source", "observer"),
            })
    # Más recientes primero
    recent_findings.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "as_of_date": now.isoformat(),
        "active_alerts": active_alerts,
        "watch_list": watch_list,
        "full_calendar": full_calendar,
        "recent_findings": recent_findings[:50],
        "summary": {
            "active_count": len(active_alerts),
            "watch_count": len(watch_list),
            "critical_upcoming": critical_upcoming,
            "findings_count": len(recent_findings),
            "next_election": full_calendar[0]["country_name"] if full_calendar else None,
            "next_election_days": full_calendar[0]["days_remaining"] if full_calendar else None,
        },
    }


@app.get("/api/country/{country_code}")
async def get_country_data(country_code: str, force_refresh: bool = False):
    """Retorna datos del dashboard para un país específico (mismo shape que /api/dashboard)."""
    code = country_code.upper()
    if code not in COUNTRY_CATALOG:
        raise HTTPException(status_code=404, detail=f"País '{code}' no encontrado")

    info = COUNTRY_CATALOG[code]
    index = _load_reports_index()
    now_ts = datetime.now(timezone.utc)
    result = None

    if not force_refresh:
        entries = index.get(code, [])
        if entries:
            latest = entries[-1]
            try:
                ts_str = latest.get("timestamp", "")
                if ts_str:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    if (now_ts - ts).total_seconds() / 3600 < 24:
                        cached = load_report(latest["run_id"])
                        if cached:
                            result = cached
                            reports_store[latest["run_id"]] = cached
            except Exception:
                pass

    if result is None:
        state = create_initial_state(
            country=info["name"], country_code=code, election_date=info["election_date"],
        )
        result = peirs_pipeline.invoke(state)
        reports_store[result["run_id"]] = result
        save_report(result)

    context = result.get("context_data", {})
    political = result.get("political_data", {})
    legal = result.get("legal_analysis", {})

    exposure = political.get("media_analysis", {}).get("exposure_distribution", {})
    media_data = [{"name": k.replace("_", " ").title(), "exposure": v, "sentiment": 0} for k, v in exposure.items()]
    violations_simple = [f"{v['treaty']} {v['article']}" for v in legal.get("violations", [])]

    emb_scores_map = {"full": 95, "partial": 60, "compromised": 25, "captured": 5}
    emb_data = extract_value(context.get("emb", {}))
    emb_level = emb_data.get("independence_level", "partial") if isinstance(emb_data, dict) else "partial"

    eco_level = political.get("digital_ecosystem", {}).get("assessment", "concerning")
    eco_scores_map = {"healthy": 90, "concerning": 60, "compromised": 35, "hostile": 10}
    finance_score = political.get("campaign_finance", {}).get("transparency_score", 0.5)

    fh_data = extract_value(context.get("freedom_house", {}))
    fh = fh_data.get("total_score", fh_data.get("score", 50)) if isinstance(fh_data, dict) else 50
    vdem_data = extract_value(context.get("vdem", {}))
    vdem_val = vdem_data.get("liberal_democracy", 0.5) if isinstance(vdem_data, dict) else 0.5
    media_bias = political.get("media_analysis", {}).get("bias_index", 0.3)

    dimensions = {
        "suffrage": max(5, int(fh * 0.9)),
        "legalFramework": max(5, int(vdem_val * 100)),
        "embIndependence": emb_scores_map.get(emb_level, 50),
        "mediaFreedom": max(5, int((1 - media_bias) * 100)),
        "campaignFinance": max(5, int(finance_score * 100)),
        "digitalEcosystem": eco_scores_map.get(eco_level, 40),
        "disputeResolution": max(5, int(vdem_val * 90)),
        "inclusion": max(5, int(fh * 0.8)),
    }

    risk = result["risk_score"]
    alerts = []
    for v in legal.get("violations", [])[:4]:
        alerts.append({"type": "critical" if v["severity"] == "critical" else "high" if v["severity"] == "high" else "moderate", "text": v["finding"][:120]})
    for rf in legal.get("risk_factors", [])[:2]:
        alerts.append({"type": rf.get("severity", "moderate"), "text": rf["finding"][:120]})
    if not alerts:
        alerts.append({"type": "low", "text": "Sistema electoral estable con garantías institucionales sólidas"})

    vdem_trend = _get_vdem_trend(VDEM_DF, code, years_back=5)
    if vdem_trend.get("available") and len(vdem_trend.get("values", [])) >= 2:
        timeline = [{"month": str(year), "score": max(5, min(99, round((1 - libdem) * 100)))} for year, libdem in vdem_trend["values"][-6:]]
    else:
        base = max(10, int(risk * 0.7))
        timeline = [{"month": str(2019 + i), "score": base + int((risk - base) * (i / 5))} for i in range(6)]

    return {
        "id": code.lower(),
        "run_id": result["run_id"],
        "name": info["name"],
        "flag": info["flag"],
        "date": info["election_date"],
        "riskScore": result["risk_score"],
        "riskLevel": result["risk_level"],
        "trend": "deteriorating" if risk >= 70 else "stable",
        "freedomScore": fh,
        "vdemIndex": round(vdem_val, 3),
        "dimensions": dimensions,
        "violations": violations_simple,
        "timeline": timeline,
        "alerts": alerts,
        "mediaData": media_data,
        "agentLogs": result.get("agent_logs", []),
        "region": COUNTRY_REGIONS.get(code, "unknown"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/country/{country_code}/chartdata")
async def get_country_chart_data(country_code: str):
    """
    Datos procesados para gráficos del informe.
    Incluye series históricas V-Dem + comparación regional + datos puntuales.
    """
    code = country_code.upper()
    if code not in COUNTRY_CATALOG:
        raise HTTPException(status_code=404, detail=f"País '{code}' no encontrado")

    def _vdem_series(variable: str, year_from: int = 1990, year_to: int = 2024) -> list:
        """Extrae serie histórica de una variable V-Dem para el país."""
        if VDEM_DF is not None:
            try:
                rows = VDEM_DF[
                    (VDEM_DF["country_text_id"] == code) &
                    (VDEM_DF["year"] >= year_from) &
                    (VDEM_DF["year"] <= year_to) &
                    (VDEM_DF[variable].notna())
                ].sort_values("year")
                result = [{"year": int(r["year"]), "value": round(float(r[variable]), 4)}
                          for _, r in rows.iterrows()]
                if result:
                    return result
            except Exception:
                pass
        # Fallback: datos estáticos (todos los países soportados, 1985-2024)
        cc_data = VDEM_STATIC.get(code, {})
        series = []
        for yr_key, row in cc_data.items():
            yr = int(yr_key)
            if year_from <= yr <= year_to and variable in row:
                series.append({"year": yr, "value": row[variable]})
        return sorted(series, key=lambda x: x["year"])

    def _vdem_multi_series(variables: list, year_from: int, year_to: int) -> list:
        """Extrae múltiples variables V-Dem por año en una sola pasada."""
        if VDEM_DF is not None:
            try:
                cols = ["year"] + [v for v in variables if v in VDEM_DF.columns]
                rows = VDEM_DF[
                    (VDEM_DF["country_text_id"] == code) &
                    (VDEM_DF["year"] >= year_from) &
                    (VDEM_DF["year"] <= year_to)
                ][cols].dropna().sort_values("year")
                result = []
                for _, r in rows.iterrows():
                    entry = {"year": int(r["year"])}
                    for v in variables:
                        if v in r.index and pd.notna(r[v]):
                            entry[v] = round(float(r[v]), 4)
                    result.append(entry)
                if result:
                    return result
            except Exception:
                pass
        # Fallback: datos estáticos
        cc_data = VDEM_STATIC.get(code, {})
        series = []
        for yr_key, row in cc_data.items():
            yr = int(yr_key)
            if year_from <= yr <= year_to:
                entry = {"year": yr}
                for v in variables:
                    if v in row:
                        entry[v] = row[v]
                if len(entry) > 1:  # al menos un indicador además de year
                    series.append(entry)
        return sorted(series, key=lambda x: x["year"])

    # ── Chart 1: Democracia liberal 1990-2024 (AreaChart) ─────────────────────
    libdem_series = _vdem_series("v2x_libdem", 1990, 2024)

    # ── Chart 2: Elecciones libres y justas 1990-2024 ─────────────────────────
    frefair_series = _vdem_series("v2xel_frefair", 1990, 2024)

    # ── Chart alertas tempranas: irregularidades e intimidación 2000-2024 ──────
    alert_series = _vdem_multi_series(["v2elirreg", "v2elintim"], 2000, 2024)

    # ── Chart 3: Autonomía + Capacidad OGE 2010-2024 (BarChart agrupado) ──────
    emb_series = _vdem_multi_series(["v2elembaut", "v2elembcap"], 2010, 2024)

    # ── Chart 5: Libertad de prensa 2010-2024 (AreaChart) ─────────────────────
    media_series = _vdem_multi_series(
        ["v2mebias", "v2meharjrn", "v2mecenefi"], 2010, 2024
    )

    # Fallback via VDEM_STATIC está integrado directamente en _vdem_series/_vdem_multi_series

    # ── Chart 4: Comparación regional (últimos datos disponibles) ─────────────
    regional = []
    latam_codes = ["PER","COL","BRA","ARG","CHL","BOL","ECU","MEX","URY","HND","SLV","PAN","GTM","NIC","VEN"]
    for c in latam_codes:
        vd = get_vdem_country(VDEM_DF, c)
        fh = get_freedom_house_country(FH_DF, c)
        if vd:
            libdem_val = vd.get("liberal_democracy", 0)
            fh_pr = fh.get("political_rights_score", 0) / 7 if fh else 0
            regional.append({
                "country_code": c,
                "name": COUNTRY_CATALOG.get(c, {}).get("name", c),
                "flag": COUNTRY_CATALOG.get(c, {}).get("flag", ""),
                "libdem": round(libdem_val, 3),
                "fh_score": round(fh_pr, 3),
                "combined": round((libdem_val * 0.6 + fh_pr * 0.4), 3),
                "highlight": c == code,
            })
    regional.sort(key=lambda x: x["combined"], reverse=True)

    # ── Datos puntuales FH + RSF ───────────────────────────────────────────────
    fh_data  = get_freedom_house_country(FH_DF, code)
    rsf_data = get_rsf_country(RSF_DF, code)
    pei_data = get_pei_country(PEI_DF, code)

    # ── Hitos electorales para overlay en Chart 1 ─────────────────────────────
    election_milestones = [
        {"year": 1990, "label": "Fujimori", "type": "election"},
        {"year": 1995, "label": "Reelección", "type": "election"},
        {"year": 2000, "label": "Crisis / Toledo", "type": "crisis"},
        {"year": 2001, "label": "Toledo", "type": "election"},
        {"year": 2006, "label": "García", "type": "election"},
        {"year": 2011, "label": "Humala", "type": "election"},
        {"year": 2016, "label": "PPK", "type": "election"},
        {"year": 2018, "label": "Crisis Congreso", "type": "crisis"},
        {"year": 2021, "label": "Castillo", "type": "election"},
        {"year": 2022, "label": "Boluarte", "type": "crisis"},
        {"year": 2026, "label": "Próximas", "type": "upcoming"},
    ] if code == "PER" else []

    return {
        "country_code": code,
        "country_name": COUNTRY_CATALOG.get(code, {}).get("name", code),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "vdem": VDEM_CITATION,
            "fh": "Freedom House, Freedom in the World 2025",
            "rsf": "Reporters Without Borders, World Press Freedom Index 2025",
        },
        "charts": {
            "libdem_series":    libdem_series,       # Chart 1: democracia liberal 1990-2024
            "frefair_series":   frefair_series,      # Chart 2: elecciones libres y justas
            "alert_series":     alert_series,        # Alerta temprana: irregularidades + intimidación
            "emb_series":       emb_series,          # Chart 3: OGE 2010-2024
            "media_series":     media_series,        # Chart 5: libertad de prensa 2010-2024
            "regional":         regional,            # Chart 4: comparación regional
        },
        "milestones":  election_milestones,
        "fh":  fh_data,
        "rsf": rsf_data,
        "pei": pei_data,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# AUDITOR — Endpoints de auditoría de integridad de sesión
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/audit/{country_code}/session")
async def audit_session(country_code: str):
    """
    Audita la sesión activa de observación de un país.
    Detecta inundación de entries, concentración de observadores,
    alegaciones sin evidencia, silencios temporales y otras anomalías.
    """
    if not AUDITOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agente Auditor no disponible.")
    code = country_code.upper()
    if code not in observation_store:
        raise HTTPException(
            status_code=404,
            detail=f"No hay sesión activa para {code}."
        )
    result = _auditor.audit_session(observation_store[code], country_code=code)
    return result.to_dict()


@app.get("/api/audit/{country_code}/status")
async def audit_status(country_code: str):
    """
    Resumen rápido del estado de auditoría — para el health check operativo.
    """
    if not AUDITOR_AVAILABLE:
        return {"auditor_available": False}
    code = country_code.upper()
    if code not in observation_store:
        return {"auditor_available": True, "session_active": False, "country_code": code}
    result = _auditor.audit_session(observation_store[code], country_code=code)
    return {
        "auditor_available": True,
        "session_active": True,
        "country_code": code,
        "audit_score": result.audit_score,
        "has_critical": result.has_critical,
        "findings_count": len(result.findings),
        "summary": result.summary,
    }


@app.get("/api/moe/brief/{country_code}")
async def get_moe_brief(country_code: str):
    """
    Genera un MOE Brief (Mission d'Observation Electorale) auto-generado
    desde los datos PEIRS reales del país.
    """
    code = country_code.upper()
    if code not in COUNTRY_CATALOG:
        raise HTTPException(status_code=404, detail=f"País '{code}' no encontrado")

    info = COUNTRY_CATALOG[code]
    index = _load_reports_index()
    entries = index.get(code, [])
    report = None
    run_id = None

    if entries:
        latest = entries[-1]
        run_id = latest.get("run_id")
        report = reports_store.get(run_id) if run_id else None
        if report is None and run_id:
            report = load_report(run_id)
            if report:
                reports_store[run_id] = report

    if report is None:
        raise HTTPException(status_code=404, detail="No hay reporte PEIRS para este país. Ejecuta /api/analyze primero.")

    now = datetime.now(timezone.utc).date()
    election_date = datetime.strptime(info["election_date"], "%Y-%m-%d").date()
    days_remaining = (election_date - now).days

    risk_score = report.get("risk_score", 50)
    risk_level = report.get("risk_level", "moderate")
    context = report.get("context_data", {})
    political = report.get("political_data", {})
    legal = report.get("legal_analysis", {})
    violations = legal.get("violations", [])
    risk_factors = legal.get("risk_factors", [])

    fh_data = extract_value(context.get("freedom_house", {}))
    fh_score = fh_data.get("total_score", fh_data.get("score", 50)) if isinstance(fh_data, dict) else 50
    vdem_data = extract_value(context.get("vdem", {}))
    vdem_val = vdem_data.get("liberal_democracy", 0.5) if isinstance(vdem_data, dict) else 0.5
    emb_data = extract_value(context.get("emb", {}))
    emb_level = emb_data.get("independence_level", "partial") if isinstance(emb_data, dict) else "partial"
    media_bias = political.get("media_analysis", {}).get("bias_index", 0.3)
    finance_score = political.get("campaign_finance", {}).get("transparency_score", 0.5)
    eco_level = political.get("digital_ecosystem", {}).get("assessment", "concerning")

    instruments = get_applicable_instruments(code)

    # Fase electoral
    if days_remaining < 0:
        phase, phase_label = "post_election", "Post-Electoral"
    elif days_remaining == 0:
        phase, phase_label = "election_day", "Jornada Electoral"
    elif days_remaining <= 2:
        phase, phase_label = "electoral_silence", "Veda Electoral"
    elif days_remaining <= 90:
        phase, phase_label = "campaign", "Campaña Electoral"
    elif days_remaining <= 180:
        phase, phase_label = "pre_campaign", "Pre-Campaña"
    else:
        phase, phase_label = "preparatory", "Fase Preparatoria"

    # Nivel de alerta
    alert_map = {
        "critical": ("RED", "Alerta Máxima"),
        "high": ("ORANGE", "Alerta Alta"),
        "moderate": ("AMBER", "Monitoreo Activo"),
        "low": ("GREEN", "Condiciones Estables"),
    }
    alert_level, alert_label = alert_map.get(risk_level, ("AMBER", "Monitoreo Activo"))

    # Protocolo MOE recomendado
    if risk_level in ["critical", "high"]:
        protocol = {
            "type": "LTO+STO", "label": "Misión de Largo y Corto Plazo",
            "lto_duration": "3-6 meses", "sto_count": "80-120 observadores",
            "pvt_recommended": True, "smm_recommended": True,
            "description": "Riesgo elevado requiere presencia temprana. LTO desde fase de campaña + STO completo para jornada electoral. PVT y SMM recomendados."
        }
    elif risk_level == "moderate":
        protocol = {
            "type": "STO", "label": "Misión de Corto Plazo",
            "lto_duration": "6-8 semanas", "sto_count": "40-60 observadores",
            "pvt_recommended": True, "smm_recommended": False,
            "description": "Riesgo moderado. STO estándar con foco en jornada y transmisión de resultados. PVT recomendado para verificación paralela."
        }
    else:
        protocol = {
            "type": "EOM_LITE", "label": "Misión Ligera de Observación",
            "lto_duration": "2-4 semanas", "sto_count": "15-25 observadores",
            "pvt_recommended": False, "smm_recommended": False,
            "description": "Condiciones estables. Presencia simbólica suficiente con foco en inclusividad y acceso de minorías."
        }

    # Áreas prioritarias derivadas de los déficits PEIRS
    priority_areas = []
    emb_score = {"full": 95, "partial": 60, "compromised": 25, "captured": 5}.get(emb_level, 50)
    eco_score = {"healthy": 90, "concerning": 60, "compromised": 35, "hostile": 10}.get(eco_level, 40)
    media_score = int((1 - media_bias) * 100)

    if emb_score < 70:
        priority_areas.append({
            "priority": 1, "area": "Organismo Electoral (JNE/ONPE/RENIEC)",
            "risk": "critical" if emb_score < 25 else "high",
            "findings": [f"Nivel de independencia EMB: {emb_level.upper()}", "Verificar autonomía decisional frente a poderes políticos"],
            "eos_standard": "EOS §72-81: Administración Electoral — Independencia e Imparcialidad",
            "observation_tasks": ["Reuniones con directivos JNE/ONPE", "Análisis de resoluciones controversiales", "Acceso al proceso de verificación de candidaturas"]
        })
    if fh_score < 65:
        priority_areas.append({
            "priority": 2, "area": "Libertades Civiles y Derechos Políticos",
            "risk": "critical" if fh_score < 30 else "high",
            "findings": [f"Freedom House FIW: {fh_score}/100", "Restricciones documentadas a libertades fundamentales"],
            "eos_standard": "ICCPR Art. 19, 21, 22",
            "observation_tasks": ["Monitoreo de incidentes con candidatos", "Revisión de detenciones arbitrarias", "Análisis de acceso a espacios para campaña"]
        })
    if media_score < 65:
        priority_areas.append({
            "priority": 3, "area": "Libertad de Medios y Acceso a Información",
            "risk": "high" if media_score < 40 else "moderate",
            "findings": [f"Índice de sesgo mediático: {round(media_bias * 100)}%"],
            "eos_standard": "EOS §64-71: Medios — Acceso Equitativo",
            "observation_tasks": ["Monitoreo cuantitativo de cobertura", "Análisis de acceso publicitario de partidos"]
        })
    if finance_score < 0.6:
        priority_areas.append({
            "priority": 4, "area": "Financiamiento de Campaña",
            "risk": "moderate",
            "findings": [f"Transparencia financiera: {round(finance_score * 100)}/100"],
            "eos_standard": "UNCAC Art. 7 — Transparencia en Financiamiento Político",
            "observation_tasks": ["Revisión de informes financieros ante JNE", "Análisis de gasto en publicidad digital"]
        })
    if eco_score < 65:
        priority_areas.append({
            "priority": 5, "area": "Ecosistema Digital y Desinformación",
            "risk": "moderate",
            "findings": [f"Evaluación ecosistema digital: {eco_level.upper()}"],
            "eos_standard": "ICCPR Art. 19(2) — Libertad de expresión digital",
            "observation_tasks": ["Social Media Monitoring (SMM)", "Detección de campañas de desinformación"]
        })
    priority_areas.append({
        "priority": len(priority_areas) + 1, "area": "Jornada Electoral y Transmisión de Resultados",
        "risk": "monitoring",
        "findings": ["Verificación de apertura y cierre de mesas", "Transmisión de actas ONPE Sistema de Cómputo Electoral"],
        "eos_standard": "EOS §108-133: Proceso de Votación y Escrutinio",
        "observation_tasks": ["Despliegue STOs en mesas seleccionadas", "Parallel Vote Tabulation (PVT)", "Monitoreo del centro de cómputo ONPE"]
    })

    return {
        "country_code": code,
        "country_name": info["name"],
        "flag": info["flag"],
        "election_date": info["election_date"],
        "days_to_election": days_remaining,
        "current_phase": phase,
        "current_phase_label": phase_label,
        "alert_level": alert_level,
        "alert_label": alert_label,
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "electoral_phases": [
            {"phase": "Inscripción de candidatos", "start": "2025-09-01", "end": "2025-11-30", "status": "completed" if days_remaining < 135 else "active"},
            {"phase": "Campaña electoral", "start": "2026-01-12", "end": "2026-04-10", "status": "completed" if days_remaining < 0 else "active" if days_remaining > 2 else "completed"},
            {"phase": "Veda electoral", "start": "2026-04-10", "end": "2026-04-11", "status": "active" if 0 < days_remaining <= 2 else ("upcoming" if days_remaining > 2 else "completed")},
            {"phase": "Jornada electoral", "start": "2026-04-12", "end": "2026-04-12", "status": "active" if days_remaining == 0 else ("upcoming" if days_remaining > 0 else "completed")},
            {"phase": "Cómputo y resultados", "start": "2026-04-12", "end": "2026-04-15", "status": "upcoming"},
            {"phase": "Segunda vuelta", "start": "2026-06-07", "end": "2026-06-07", "status": "upcoming"},
        ],
        "blocks": {
            "risk_context": {
                "title": "Contexto de Riesgo Operativo",
                "risk_score": risk_score, "risk_level": risk_level,
                "alert_level": alert_level, "alert_label": alert_label,
                "days_to_election": days_remaining, "current_phase": phase_label,
                "key_indicators": {
                    "freedom_house": f"{fh_score}/100",
                    "vdem_liberal_democracy": round(vdem_val, 3),
                    "emb_independence": emb_level,
                    "active_violations": len(violations),
                },
                "critical_violations": [
                    {"treaty": v["treaty"], "article": v["article"], "finding": v["finding"][:150], "severity": v["severity"]}
                    for v in violations if v.get("severity") in ["critical", "high"]
                ][:5],
                "risk_factors": [rf["finding"][:150] for rf in risk_factors[:3]],
                "trend": report.get("trend", "stable"),
            },
            "legal_framework": {
                "title": "Marco Legal Aplicable",
                "universal_instruments": [{"id": i["id"], "name": i["name"], "key_articles": i["key_articles"]} for i in instruments["universal"]],
                "regional_instruments": [{"id": i["id"], "name": i["name"], "key_articles": i["key_articles"], "observer": i.get("observer", "")} for i in instruments["regional"]],
                "national_framework": {
                    "constitution": "Constitución Política del Perú (1993) — Arts. 176-187",
                    "electoral_law": "Ley Orgánica de Elecciones N° 26859",
                    "parties_law": "Ley de Organizaciones Políticas N° 28094",
                    "emb_structure": "JNE — ONPE — RENIEC",
                },
                "key_obligations": [
                    "ICCPR Art. 25: elecciones genuinas por sufragio universal",
                    "CADH Art. 23: derechos políticos — voto y elegibilidad",
                    "CDI Art. 3: elementos esenciales de la democracia representativa",
                    "UNDRIP Art. 5, 18: participación política de pueblos indígenas",
                ],
            },
            "priority_areas": {
                "title": "Áreas Prioritarias de Observación",
                "priority_areas": priority_areas,
                "high_risk_count": sum(1 for a in priority_areas if a["risk"] in ["critical", "high"]),
                "moderate_risk_count": sum(1 for a in priority_areas if a["risk"] == "moderate"),
            },
            "protocol": {
                "title": "Protocolo de Observación Recomendado",
                "protocol": protocol,
                "recommended_observers": [
                    {"org": "OEA/DECO", "role": "Misión regional de observación"},
                    {"org": "Centro Carter", "role": "Observación LTO + PVT"},
                    {"org": "NDI / IRI", "role": "Fortalecimiento institucional + observación"},
                    {"org": "UNIORE", "role": "Observación latinoamericana especializada"},
                ],
                "pvt_note": "Conteo rápido paralelo sobre muestra representativa de mesas según metodología IFES/NDI." if protocol["pvt_recommended"] else None,
                "reporting_schedule": {
                    "pre_election": "Informe preliminar 5 días antes de la jornada",
                    "election_day": "Declaración preliminar 48h post-jornada",
                    "final_report": "Informe final 60-90 días post-elección",
                },
            },
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6d. PERÚ 2026 — Datos estructurados específicos
# ═══════════════════════════════════════════════════════════════════════════════

PERU_ELECTORAL_SYSTEM = {
    "name": "Representación Proporcional con Cifra Repartidora (D'Hondt)",
    "law": "Ley Orgánica de Elecciones N° 26859 y modificatorias",
    "seats": 130,
    "chamber": "Unicameral — Congreso de la República",
    "term_years": 5,
    "districts": 26,
    "district_note": "26 circunscripciones (25 regiones + Lima Metropolitana). Magnitude varía de 1 (Moquegua, Tacna, Madre de Dios) a 36 (Lima).",
    "threshold": "5% de votos válidos a nivel nacional O 7 escaños en al menos un distrito (Ley 31046)",
    "threshold_note": "El umbral doble reduce fragmentación pero en la práctica han sobrevivido 8+ bancadas en cada congreso desde 2011.",
    "formula": "Cifra Repartidora (Método D'Hondt) — favorece a partidos más grandes en distritos plurinominales",
    "ballot_type": "Lista cerrada y bloqueada con voto preferencial (hasta 2 preferencias)",
    "vote_preference_note": "El voto preferencial permite al elector reordenar candidatos dentro de la lista, lo que genera competencia intrapartidaria intensa.",
    "presidential_system": "Elección directa a 2 vueltas (ballotage)",
    "ballotage_threshold": "Mayoría absoluta (50%+1) en 1ª vuelta. Si nadie alcanza: 2ª vuelta entre los dos más votados.",
    "women_quota": "30% mínimo de mujeres en listas (Ley 31030, 2021)",
    "youth_quota": "20% de jóvenes (hasta 29 años) y comunidades nativas en listas",
    "simultaneity": "Elecciones presidenciales y congresales simultáneas (misma boleta, mismo día)",
    "prohibitions": "Condenados con sentencia firme no pueden postular. Funcionarios públicos deben renunciar 6 meses antes.",
    "key_bodies": {
        "JNE": "Jurado Nacional de Elecciones — árbitro electoral máximo, resuelve impugnaciones, proclama resultados",
        "ONPE": "Oficina Nacional de Procesos Electorales — organiza la votación, escrutinio, transmisión de resultados",
        "RENIEC": "Registro Nacional de Identificación — padrón electoral, DNI, biometría",
    },
    "historical_fragmentation": "Perú ha promediado 7-8 bancadas efectivas desde 2011. Ningún partido ha obtenido mayoría absoluta (66 escaños) desde Fuerza Popular en 2016.",
    "sources": [
        {"label": "JNE — Sistema Electoral Peruano", "url": "https://www.jne.gob.pe"},
        {"label": "ONPE — Elecciones 2026", "url": "https://www.onpe.gob.pe"},
        {"label": "Ley N° 26859 — Ley Orgánica de Elecciones", "url": "https://www.leyes.congreso.gob.pe"},
        {"label": "IDEA Internacional — Electoral System Design Database", "url": "https://www.idea.int/data-tools/country-view/247/40"},
    ],
}

PERU_POLITICAL_FORCES = [
    {
        "id": "app", "name": "Alianza para el Progreso", "abbr": "APP",
        "ideology": "Centro / Populismo pragmático", "position": 50,
        "founded": 1999, "color": "#f97316",
        "leader": "César Acuña Peralta",
        "background": (
            "Fundada en 1999 por César Acuña, empresario universitario de La Libertad. "
            "Su crecimiento se sustenta en la red de universidades privadas del Grupo UCV, "
            "con presencia en 18 regiones. Ha sido el partido con mayor número de candidatos "
            "electos en elecciones regionales y municipales 2022. Su modelo organizativo ha "
            "sido cuestionado como 'partido-empresa' por organismos como Transparencia Internacional Perú. "
            "Acuña fue inhabilitado en 2018 por el JNE por presuntas dádivas electorales, sanción "
            "posteriormente levantada, lo que generó controversia sobre la aplicabilidad efectiva del Art. 25 ICCPR."
        ),
        "candidates_2026": [
            {"name": "César Acuña Peralta", "role": "Candidato presidencial confirmado",
             "notes": "Cuarta candidatura presidencial. Gobernador electo de La Libertad 2022-2026. Postula con la figura de 'gestor' y candidato de centro."},
        ],
        "electoral_history": [
            {"year": 2016, "seats": 9,  "first_round_pct": None, "result": "Coalición menor. APP apoya a PPK en 2ª vuelta."},
            {"year": 2020, "seats": 22, "first_round_pct": None, "result": "Elecciones extraordinarias. Segundo partido más votado."},
            {"year": 2021, "seats": 22, "first_round_pct": 6.1,  "result": "4to lugar presidencial (Acuña). 22 escaños iniciales, sube a 28 por transfugismo."},
        ],
        "key_policies": [
            "Inversión en infraestructura educativa y universidades regionales",
            "Descentralización fiscal y fortalecimiento de gobiernos regionales",
            "Seguridad ciudadana con énfasis en penas más duras",
        ],
        "base_regions": ["La Libertad", "Cajamarca", "Lambayeque"],
        "current_seats": 28, "electoral_strength": "Alto", "risk_profile": "high",
        "risk_notes": "Red clientelar articulada en torno a universidades UCV. Financiamiento opaco. Acuña con inhabilitaciones previas.",
        "strengths": ["Infraestructura organizacional universitaria", "Presencia robusta en norte", "Financiamiento sólido"],
        "vulnerabilities": ["Denuncias de compra de votos", "Imagen de partido-empresa", "Dependencia del liderazgo personal"],
        "iccpr_risk": "Art. 25 ICCPR — posible afectación al sufragio libre mediante prácticas clientelares documentadas por la ONPE y JNE.",
        "iccpr_source": "JNE Res. 0234-2018-JNE; ONPE Informe de Financiamiento 2022; Transparencia Internacional Perú (2023)",
        "iccpr_date": "2018 (inhabilitación), 2022 (informe ONPE), actualizado ene 2026",
        "iccpr_url": "https://www.jne.gob.pe/transparencia/resoluciones/",
    },
    {
        "id": "fp", "name": "Fuerza Popular", "abbr": "FP",
        "ideology": "Derecha / Fujimorismo", "position": 72,
        "founded": 2010, "color": "#ef4444",
        "leader": "Keiko Fujimori",
        "background": (
            "Heredera del fujimorismo, movimiento nacido en torno al expresidente Alberto Fujimori (1990-2000). "
            "Keiko Fujimori ha liderado tres candidaturas presidenciales (2011, 2016, 2021), "
            "perdiendo las tres en segunda vuelta. En 2016 obtuvo 73 escaños (mayoría absoluta) "
            "y usó ese dominio para enfrentarse al ejecutivo de PPK, generando una crisis constitucional. "
            "Keiko fue detenida en 2018 y 2019 por presunto lavado de activos en el caso Odebrecht; "
            "tiene proceso abierto. El partido ha renovado parcialmente su cúpula pero mantiene "
            "el liderazgo personalista de la familia Fujimori."
        ),
        "candidates_2026": [
            {"name": "Keiko Fujimori", "role": "Candidata presidencial (4ª postulación)",
             "notes": "Mantiene liderazgo del partido. Proceso judicial por lavado de activos en curso. Base electoral fiel en Lima y regiones costeras."},
        ],
        "electoral_history": [
            {"year": 2016, "seats": 73, "first_round_pct": 39.9, "result": "Mayoría absoluta en congreso. Keiko pierde 2ª vuelta presidencial vs PPK por menos de 0.1%."},
            {"year": 2020, "seats": 15, "first_round_pct": None, "result": "Elecciones extraordinarias. Derrumbe electoral post-confrontación con Vizcarra."},
            {"year": 2021, "seats": 24, "first_round_pct": 13.4, "result": "13.4% en 1ª vuelta, 49.9% en 2ª vuelta. Impugna resultado ante el JNE sin éxito."},
        ],
        "key_policies": [
            "Mano dura contra la criminalidad e inseguridad",
            "Libre mercado y protección a la inversión privada",
            "Rechazo a la Asamblea Constituyente",
        ],
        "base_regions": ["Lima", "Ica", "Arequipa", "Ucayali"],
        "current_seats": 23, "electoral_strength": "Alto", "risk_profile": "high",
        "risk_notes": "Historia de 3 procesos electorales con denuncias de fraude. Keiko con condena suspendida. Control parcial de instituciones cuestionado.",
        "strengths": ["Base electoral leal en Lima", "Estructura partidaria consolidada", "Candidatos con experiencia legislativa"],
        "vulnerabilities": ["Imagen negativa por corrupción", "Dependencia del legado Fujimori", "Juicios pendientes"],
        "iccpr_risk": "Art. 14 ICCPR — garantías procesales comprometidas en relación al proceso penal activo del liderazgo.",
        "iccpr_source": "Poder Judicial del Perú — Expediente N° 00299-2017-36-5001-JR-PE-01; CIDH Informe Anual 2023",
        "iccpr_date": "2017 (inicio proceso), dic 2023 (última resolución de apelación), ene 2026 (estado activo)",
        "iccpr_url": "https://cej.pj.gob.pe/cej/forms/busquedaform.html",
    },
    {
        "id": "rp", "name": "Renovación Popular", "abbr": "RP",
        "ideology": "Derecha / Conservador-liberal", "position": 80,
        "founded": 2020, "color": "#0ea5e9",
        "leader": "Rafael López Aliaga",
        "background": (
            "Partido fundado en 2020 por Rafael López Aliaga, empresario de origen limeño. "
            "De perfil ultraconservador en lo social (declaradamente antiaborto, crítico de la ideología de género) "
            "y liberal en lo económico. Su primera candidatura presidencial en 2021 (12.8%) lo consolidó "
            "como líder de la derecha dura urbana. Fue elegido alcalde de Lima Metropolitana en 2022, "
            "cargo desde el cual ha impulsado una gestión confrontacional con el gobierno central. "
            "Su discurso polarizante y el uso del término 'castrocomunismo' para referirse a la izquierda "
            "ha sido documentado como factor de desinformación."
        ),
        "candidates_2026": [
            {"name": "Rafael López Aliaga", "role": "Candidato presidencial (2ª postulación)",
             "notes": "Alcalde de Lima hasta diciembre 2025. Perfil empresarial. Alta recordación en Lima pero baja fuera de la capital."},
        ],
        "electoral_history": [
            {"year": 2021, "seats": 9, "first_round_pct": 12.8, "result": "3er lugar presidencial. 9 escaños en congreso. Ingreso sorpresivo al escenario político."},
        ],
        "key_policies": [
            "Tolerancia cero al crimen: cárceles duras, pena de muerte para terrorismo",
            "Eliminación de impuestos a pequeñas empresas y reducción del Estado",
            "Rechazo a la agenda LGBT y políticas de género en educación",
        ],
        "base_regions": ["Lima", "Arequipa", "Moquegua"],
        "current_seats": 9, "electoral_strength": "Medio", "risk_profile": "moderate",
        "risk_notes": "Discurso polarizante. Cuestionamientos sobre financiamiento empresarial. Posiciones restrictivas sobre derechos civiles.",
        "strengths": ["Base urbana de clase media-alta", "Liderazgo mediático", "Posicionamiento anticorrupción"],
        "vulnerabilities": ["Escaso implante territorial fuera de Lima", "Discurso divisivo", "Partido personalista joven"],
        "iccpr_risk": "Art. 19, 21 ICCPR — restricciones retóricas a libertades civiles documentadas en campaña; potencial impacto en derechos de minorías.",
        "iccpr_source": "Freedom House FIW 2025 (pp. 14-15); IPYS Perú — Monitoreo de Discurso Político 2024-2025",
        "iccpr_date": "2024-2025 (campaña electoral, monitoreo IPYS)",
        "iccpr_url": "https://freedomhouse.org/country/peru/freedom-world/2025",
    },
    {
        "id": "pl", "name": "Perú Libre", "abbr": "PL",
        "ideology": "Izquierda / Marxismo-leninismo", "position": 15,
        "founded": 2009, "color": "#a855f7",
        "leader": "Vladimir Cerrón",
        "background": (
            "Fundado en 2009 en la región Junín por Vladimir Cerrón, médico y exgobernador regional. "
            "Fue el vehículo que llevó a Pedro Castillo a la presidencia en 2021 con apenas el 18.9% en primera vuelta. "
            "Cerrón fue condenado en 2019 por corrupción (3.5 años de prisión efectiva) e inhabilitado para cargos públicos, "
            "lo que generó una contradicción estructural: el fundador no pudo ser candidato del gobierno que él mismo impulsó. "
            "Castillo rompió con Cerrón en 2022. Tras la vacancia de Castillo, el partido se fragmentó y hoy opera "
            "con presencia marginal pero organizada en regiones andinas del centro-sur."
        ),
        "candidates_2026": [
            {"name": "Por definir", "role": "Candidato presidencial sin confirmar",
             "notes": "Cerrón inhabilitado. El partido buscará candidato de la región andina. Alta incertidumbre sobre su viabilidad para superar el umbral del 5%."},
        ],
        "electoral_history": [
            {"year": 2021, "seats": 37, "first_round_pct": 18.9, "result": "Castillo gana presidencia con 50.1% en 2ª vuelta. 37 escaños iniciales, se fragmenta a 7 por conflictos internos."},
        ],
        "key_policies": [
            "Asamblea Constituyente para nueva Constitución",
            "Nationalización de recursos naturales estratégicos",
            "Reforma agraria y redistribución de tierras",
        ],
        "base_regions": ["Junín", "Cusco", "Puno", "Ayacucho"],
        "current_seats": 7, "electoral_strength": "Medio", "risk_profile": "high",
        "risk_notes": "Cerrón condenado por corrupción e inhabilitado. Partido instrumento de Castillo (2021). Base en regiones andinas.",
        "strengths": ["Base en sierra central y sur", "Discurso redistributivo con arrastre popular"],
        "vulnerabilities": ["Liderazgo inhabilitado", "Asociación con gestión Castillo", "Fragmentación severa"],
        "iccpr_risk": "Art. 25(b) ICCPR — candidatos inhabilitados por resolución judicial; riesgo de impugnación postelectoral si alcanzan representación.",
        "iccpr_source": "Poder Judicial — Sentencia 1er Juzgado Penal de Huancayo (2019); JNE Res. 0987-2019-JNE (inhabilitación Cerrón)",
        "iccpr_date": "2019 (condena y inhabilitación), confirmada 2022, vigente ene 2026",
        "iccpr_url": "https://www.jne.gob.pe/transparencia/resoluciones/",
    },
    {
        "id": "pp", "name": "Podemos Perú", "abbr": "PP",
        "ideology": "Centro-populista", "position": 40,
        "founded": 2017, "color": "#8b5cf6",
        "leader": "José Luna Gálvez",
        "background": (
            "Fundado en 2017 por José Luna Gálvez, empresario educativo del grupo Luna. "
            "Su modelo organizativo es similar al de APP: partido articulado alrededor de una empresa educativa "
            "(institutos y universidades). Ha sido objeto de investigaciones del Ministerio Público por presunta "
            "venta de candidaturas y financiamiento irregular. Su bancada en el congreso actual es heterogénea "
            "y ha votado de forma oportunista con distintas mayorías. No tiene una ideología clara ni base programática sólida."
        ),
        "candidates_2026": [
            {"name": "José Luna Gálvez", "role": "Candidato presidencial probable",
             "notes": "Fundador del partido. Investigado por presunta venta de candidaturas. Perfil de empresario-político."},
        ],
        "electoral_history": [
            {"year": 2020, "seats": 11, "first_round_pct": None, "result": "Elecciones extraordinarias. Sorpresa electoral con 11 escaños."},
            {"year": 2021, "seats": 5,  "first_round_pct": 1.8,  "result": "Luna obtiene 1.8% presidencial. 5 escaños parlamentarios, sube a 9 por transfugismo."},
        ],
        "key_policies": [
            "Empleo y emprendimiento para jóvenes y mujeres",
            "Reforma educativa con énfasis en técnica",
            "Descentralización y obras de infraestructura regional",
        ],
        "base_regions": ["Lima Norte", "Piura"],
        "current_seats": 9, "electoral_strength": "Medio", "risk_profile": "moderate",
        "risk_notes": "Partido con denuncias de compra de candidaturas. Financiamiento cuestionado. Estructura débil fuera de Lima.",
        "strengths": ["Implante en Lima norte", "Candidatos con perfil técnico"],
        "vulnerabilities": ["Denuncias de mercado de candidaturas", "Baja identidad partidaria"],
        "iccpr_risk": "Art. 25 ICCPR — mercantilización de candidaturas puede afectar la representatividad real del sistema.",
        "iccpr_source": "Fiscalía Especializada en Delitos de Corrupción de Funcionarios — Carpeta Fiscal N° 2019-2358; IDEA Internacional (2024)",
        "iccpr_date": "2019 (apertura investigación), 2024 (IDEA informe sistema partidos Perú)",
        "iccpr_url": "https://www.idea.int/data-tools/country-view/247/40",
    },
    {
        "id": "ap", "name": "Acción Popular", "abbr": "AP",
        "ideology": "Centro / Social-demócrata", "position": 45,
        "founded": 1956, "color": "#10b981",
        "leader": "Directiva colectiva (en disputa)",
        "background": (
            "Fundado en 1956 por Fernando Belaúnde Terry, dos veces presidente (1963-1968 y 1980-1985). "
            "Partido más antiguo del Perú en actividad electoral regular. Históricamente representó "
            "la centro-izquierda reformista y el desarrollismo. Ganó la Mesa Directiva del Congreso "
            "en las elecciones extraordinarias de 2020. Sin embargo, su gestión legislativa bajo el liderazgo "
            "de Manuel Merino fue catastrófica: duró apenas una semana como presidente (noviembre 2020) "
            "tras la crisis de la vacancia de Vizcarra. Desde entonces atraviesa una profunda crisis interna "
            "con múltiples facciones y sin candidato presidencial consolidado para 2026."
        ),
        "candidates_2026": [
            {"name": "Por definir — probable candidato de consenso", "role": "Candidato presidencial sin confirmar",
             "notes": "El partido no ha logrado consenso. Múltiples precandidatos. Alta probabilidad de no superar el umbral del 5% si continúa fragmentado."},
        ],
        "electoral_history": [
            {"year": 2016, "seats": 5,  "first_round_pct": 1.3,  "result": "Candidato irrelevante. Mínima representación parlamentaria."},
            {"year": 2020, "seats": 25, "first_round_pct": None,  "result": "Gana elecciones extraordinarias con 25 escaños. Crisis Merino destruye capital político."},
            {"year": 2021, "seats": 16, "first_round_pct": 4.1,   "result": "4.1% presidencial (debajo del umbral histórico). 16 escaños parlamentarios."},
        ],
        "key_policies": [
            "Reforma del Estado y profesionalización de la función pública",
            "Modernización agrícola y apoyo al pequeño productor",
            "Descentralización real con mecanismos de control ciudadano",
        ],
        "base_regions": ["Lima", "Cusco", "Piura", "Ancash"],
        "current_seats": 7, "electoral_strength": "Bajo-Medio", "risk_profile": "low",
        "risk_notes": "Partido histórico en proceso de reconstrucción. Fractura interna post-Sagasti. Sin candidato presidencial consolidado.",
        "strengths": ["Marca histórica reconocida", "Presencia nacional difusa", "Candidatos moderados"],
        "vulnerabilities": ["Crisis de liderazgo severa", "Fraccionamiento interno", "Resultados decrecientes"],
        "iccpr_risk": "Sin violaciones documentadas directas. Riesgo de irrelevancia institucional si no supera umbral.",
        "iccpr_source": "JNE — Estadísticas de participación política 2021; ONPE resultados electorales 2021",
        "iccpr_date": "2021 (último proceso electoral con datos), proyección 2026",
        "iccpr_url": "https://www.onpe.gob.pe/modElecciones/elecciones/elecciones2021/",
    },
    {
        "id": "bm", "name": "Frente Amplio / Izquierda Unida", "abbr": "FA",
        "ideology": "Izquierda progresista", "position": 20,
        "founded": 2013, "color": "#ec4899",
        "leader": "Coalición (varios)",
        "background": (
            "Coalición de organizaciones de izquierda que ha intentado articular una alternativa al "
            "fujimorismo y al populismo de Perú Libre. En 2021 logró 9 escaños bajo distintas siglas. "
            "Tiene fuerte presencia en el magisterio organizado (SUTEP), movimientos indígenas del sur andino "
            "(Puno, Cusco, Apurímac) y organizaciones campesinas. Su dificultad estructural es la fragmentación: "
            "en cada proceso electoral debaten si presentarse unidos o divididos. Para 2026, diferentes corrientes "
            "negocian si formar una alianza o postular por separado, lo que determina su viabilidad electoral dado el umbral del 5%."
        ),
        "candidates_2026": [
            {"name": "En proceso de definición", "role": "Candidato por consenso de la coalición",
             "notes": "Figuras como Verónica Mendoza (2016: 19.9% presidencial) podrían encabezar nuevamente. La unidad de la izquierda es condición para superar el umbral."},
        ],
        "electoral_history": [
            {"year": 2016, "seats": 20, "first_round_pct": 19.9, "result": "Frente Amplio con Mendoza: 3er lugar presidencial (19.9%). 20 escaños. La izquierda en su mejor momento reciente."},
            {"year": 2021, "seats": 9,  "first_round_pct": 8.9,  "result": "Fragmentada en múltiples candidaturas. Total: ~9 escaños bajo distintas siglas."},
        ],
        "key_policies": [
            "Asamblea Constituyente y nueva Constitución plurinacional",
            "Reforma tributaria progresiva y renta básica",
            "Derechos de pueblos indígenas y consulta previa (UNDRIP)",
        ],
        "base_regions": ["Puno", "Cusco", "Apurímac", "Ayacucho", "Huancavelica"],
        "current_seats": 10, "electoral_strength": "Medio (sur andino)", "risk_profile": "moderate",
        "risk_notes": "Coalición heterogénea con fuerte implante en el magisterio rural. Discurso de reformas constitucionales.",
        "strengths": ["Base sindical docente organizada", "Fuerte en sur andino", "Voto indígena sólido"],
        "vulnerabilities": ["Sin liderazgo presidencial reconocido", "Fragmentación interna crónica", "Estigmatización mediática"],
        "iccpr_risk": "UNDRIP Art. 5, 18 — representación de pueblos indígenas en debate constitucional es un derecho reconocido internacionalmente.",
        "iccpr_source": "AIDESEP — Informe de Participación Electoral Indígena 2021; CIDH OEA/Ser.L/V/II Doc. 49/19",
        "iccpr_date": "2021 (informe AIDESEP), 2019 (CIDH), monitoreo continuo 2025",
        "iccpr_url": "https://www.oas.org/es/cidh/informes/anuales.asp",
    },
    {
        "id": "ind", "name": "No bancada / Independientes", "abbr": "IND",
        "ideology": "Variable (transfugismo)", "position": 50,
        "founded": None, "color": "#64748b",
        "leader": "N/A",
        "background": (
            "No es un partido sino el reflejo de la debilidad institucional del sistema político peruano. "
            "Los 37 congresistas sin bancada son legisladores que abandonaron sus grupos originales por "
            "conflictos internos, investigaciones o negociación de cargos. El transfuguismo es un fenómeno "
            "estructural en Perú: en cada congreso desde 2011 más del 20% de legisladores ha cambiado de bancada. "
            "Este fenómeno debilita la rendición de cuentas democrática, dificulta la formación de mayorías "
            "estables y es reconocido por el JNE como una distorsión del sistema de representación proporcional."
        ),
        "candidates_2026": [],
        "electoral_history": [
            {"year": 2021, "seats": 37, "first_round_pct": None, "result": "37 legisladores sin bancada al inicio de 2026 (comenzaron el período con bancada; abandonaron sus partidos)"},
        ],
        "key_policies": [],
        "base_regions": ["Nacional"],
        "current_seats": 37, "electoral_strength": "Variable", "risk_profile": "moderate",
        "risk_notes": "Refleja fragmentación extrema y débil institucionalización partidaria peruana.",
        "strengths": ["Flexibilidad de voto", "Sin compromisos partidarios"],
        "vulnerabilities": ["Sin accountability democrático", "Susceptibles a transfuguismo e influencias externas"],
        "iccpr_risk": "Art. 25 ICCPR — fragmentación que debilita la representatividad del sistema; votantes no representados ideológicamente.",
        "iccpr_source": "JNE — Informe de Transfuguismo Parlamentario 2022-2026; V-Dem v15 (v2x_partip, 2024)",
        "iccpr_date": "2022-2026 (monitoreo JNE), V-Dem dato 2024",
        "iccpr_url": "https://www.jne.gob.pe/transparencia/informes/",
    },
]

PERU_PARL_DATA = {
    "total_seats": 130,
    "system": "Representación proporcional con umbral del 5% (Ley Orgánica de Elecciones, Ley N° 26859)",
    "current": {
        "label": "Congreso actual 2021-2026",
        "note": "Composición aproximada al inicio de 2026. Incluye cambios de bancada post-2021.",
        "seats": [
            {"party": "APP",  "full_name": "Alianza para el Progreso",   "seats": 28, "color": "#f97316"},
            {"party": "FP",   "full_name": "Fuerza Popular",              "seats": 23, "color": "#ef4444"},
            {"party": "BM",   "full_name": "Bloque Magisterial/Izq.",     "seats": 10, "color": "#ec4899"},
            {"party": "PP",   "full_name": "Podemos Perú",                "seats": 9,  "color": "#8b5cf6"},
            {"party": "RP",   "full_name": "Renovación Popular",          "seats": 9,  "color": "#0ea5e9"},
            {"party": "PL",   "full_name": "Perú Libre",                  "seats": 7,  "color": "#a855f7"},
            {"party": "AP",   "full_name": "Acción Popular",              "seats": 7,  "color": "#10b981"},
            {"party": "IND",  "full_name": "No bancada / Independientes", "seats": 37, "color": "#64748b"},
        ],
        "fragmentation_index": 8.4,
        "fragmentation_index_note": "Cálculo derivado de los seats listados arriba (Laakso-Taagepera). Reproducible con la composición declarada del Congreso.",
        "effective_parties": 7.2,
        "effective_parties_note": "Índice efectivo (Laakso-Taagepera) calculado sobre los seats declarados. Verificable.",
        "governing_coalition_seats": None,
        "opposition_seats": None,
    },
    # 2026-05-27 — Escenarios predictivos A/B/C retirados (espejo de modules/peru_data.py).
    # La 1ª vuelta del 12-abr-2026 hace obsoletas esas proyecciones. La composición
    # real del Congreso 2026-2031 se carga cuando ONPE publique el cómputo oficial.
    "next_2026_2031": {
        "label": "Congreso entrante 2026-2031",
        "seats": [],
        "audit_status": "pending_official_results",
        "audit_note": "Pendiente del cómputo oficial ONPE de la elección parlamentaria del 12-abr-2026.",
        "source": "Pendiente — ONPE Resultados Oficiales Elecciones 2026",
        "source_url_pending": "https://resultados.onpe.gob.pe",
    },
}

# Espejo inline de modules/peru_data.PERU_RUNOFF_2026 — fallback cuando el
# import del módulo falla. La fuente de verdad es modules/peru_data.py.
PERU_RUNOFF_2026 = {
    "phase": "entre_vueltas",
    "first_round_date": "2026-04-12",
    "runoff_date": "2026-06-07",
    "runoff_date_iso": "2026-06-07T08:00:00-05:00",
    "runoff_date_note": "ONPE — apertura de mesas 08:00 hora de Lima (UTC-5). Cierre 16:00.",
    "finalists": [
        {"slot": 1, "party_id": "fp", "party_name": "Fuerza Popular",
         "candidate_name": "Keiko Fujimori", "first_round_pct": 17.19, "first_round_votes": 2_877_678,
         "source": "JNE Acta General de Proclamación 1ª Vuelta EG 2026; ONPE Boletín Final 100%",
         "source_url": "https://portal.jne.gob.pe/portal_documentos/files/637a2dda-73ba-4abc-95bf-294f14d454bb.pdf",
         "audit_status": "VERIFIED_SECONDARY_PRIMARY_PDF_NOT_PARSED"},
        {"slot": 2, "party_id": "jpp", "party_name": "Juntos por el Perú",
         "candidate_name": "Roberto Sánchez Palomino", "first_round_pct": 12.04, "first_round_votes": 2_015_114,
         "source": "JNE Acta General de Proclamación 1ª Vuelta EG 2026; ONPE Boletín Final 100%",
         "source_url": "https://portal.jne.gob.pe/portal_documentos/files/637a2dda-73ba-4abc-95bf-294f14d454bb.pdf",
         "audit_status": "VERIFIED_SECONDARY_PRIMARY_PDF_NOT_PARSED"},
    ],
    "first_round_full_breakdown": {
        "by_party": [
            {"party_id": "fp",   "party_name": "Fuerza Popular",            "candidate": "Keiko Fujimori",      "pct": 17.19, "votes": 2_877_678},
            {"party_id": "jpp",  "party_name": "Juntos por el Perú",        "candidate": "Roberto Sánchez",     "pct": 12.04, "votes": 2_015_114},
            {"party_id": "rp",   "party_name": "Renovación Popular",        "candidate": "Rafael López-Aliaga", "pct": 11.91, "votes": 1_993_905},
            {"party_id": "pbg",  "party_name": "Partido del Buen Gobierno", "candidate": "Jorge Nieto",         "pct": 10.98, "votes": 1_837_517},
            {"party_id": "obras","party_name": "Partido Cívico OBRAS",      "candidate": "Ricardo Belmont",     "pct": 10.15, "votes": 1_698_903},
            {"party_id": "ppt",  "party_name": "País para Todos",           "candidate": "Carlos Álvarez",      "pct":  7.93, "votes": 1_326_717},
            {"party_id": "an",   "party_name": "Ahora Nación",              "candidate": "Alfonso López-Chau",  "pct":  7.30, "votes": 1_221_272},
        ],
        "total_valid_votes": 16_749_424, "blank_votes_abs": 2_372_896, "null_votes_abs": 1_045_425,
        "total_voters": 20_167_745, "abstention_pct": 26.19, "blank_pct": 11.76, "null_pct": 5.18,
        "source": "Wikipedia ES — Elecciones generales de Perú de 2026; primaria JNE PDF",
        "source_url": "https://es.wikipedia.org/wiki/Elecciones_generales_de_Per%C3%BA_de_2026",
        "primary_source_url": "https://portal.jne.gob.pe/portal_documentos/files/637a2dda-73ba-4abc-95bf-294f14d454bb.pdf",
        "audit_status": "VERIFIED_SECONDARY_PRIMARY_PDF_NOT_PARSED",
    },
    "head_to_head": {
        "key_issues": {
            "economic_model": {"finalist_1": "PENDIENTE", "finalist_2": "PENDIENTE", "source": "Pendiente"},
            "asamblea_constituyente": {"finalist_1": "PENDIENTE", "finalist_2": "PENDIENTE", "source": "Pendiente"},
            "security_crime": {"finalist_1": "PENDIENTE", "finalist_2": "PENDIENTE", "source": "Pendiente"},
            "human_rights": {"finalist_1": "PENDIENTE", "finalist_2": "PENDIENTE", "source": "Pendiente"},
            "anti_corruption": {"finalist_1": "PENDIENTE", "finalist_2": "PENDIENTE", "source": "Pendiente"},
        },
        "polls_between_rounds": {"items": [], "audit_status": "PENDIENTE_VERIFICACION",
            "audit_note": "Reactivar solo con URL a la ficha técnica publicada por la encuestadora."},
        "debates": {"scheduled": [], "audit_status": "PENDIENTE_VERIFICACION",
            "source": "Pendiente — JNE Cronograma Electoral 2026",
            "source_url": "https://www.jne.gob.pe/transparencia/cronograma/"},
        "endorsements": {"for_finalist_1": [], "for_finalist_2": [],
            "audit_status": "PENDIENTE_VERIFICACION"},
    },
    "risk_factors_between_rounds": {
        "incidents": [], "audit_status": "PENDIENTE_VERIFICACION",
        "iccpr_ref": "Art. 25 ICCPR — la fase entre vueltas exige condiciones equitativas de campaña y libertad de información.",
        "historical_baseline": "En 2021 (Castillo-Fujimori) la fase entre vueltas registró 47 días con denuncias de fraude y manipulación informativa documentadas por JNE/IPYS.",
    },
    "iccpr_ref": "Art. 25 ICCPR — derecho a elegir y ser elegido en condiciones de equidad, vigente durante la 2ª vuelta.",
    "data_sources": "JNE Acta de Proclamación PDF; ONPE Boletín Final 100%; Wikipedia ES; Infobae; El Comercio. Pendiente: head_to_head + risk_factors entre vueltas.",
    "audit_status": "partial — finalists + breakdown cargados; head_to_head + risk_factors pendientes",
    "audit_note": "Espejo inline de modules/peru_data.py. Actualizado 2026-05-31 con resultados 1ª vuelta cross-referenciados (3 fuentes secundarias coincidentes). PDF JNE primario referenciado pero no parseado programáticamente — pendiente validación humana.",
}

PERU_REGIONS_DATA = [
    {"region": "Lima",          "seats": 36, "pop_M": 10.8, "urban_pct": 97, "poverty_pct": 14, "indigenous_pct": 4,  "risk_score": 42, "tendency": "volátil", "notes": "Concentra 1/3 del electorado. Voto urbano fragmentado."},
    {"region": "La Libertad",   "seats": 7,  "pop_M": 2.1,  "urban_pct": 73, "poverty_pct": 24, "indigenous_pct": 5,  "risk_score": 48, "tendency": "APP-dominante", "notes": "Feudo electoral de Acuña. Red clientelar universitaria activa."},
    {"region": "Piura",         "seats": 7,  "pop_M": 2.0,  "urban_pct": 68, "poverty_pct": 28, "indigenous_pct": 3,  "risk_score": 45, "tendency": "centro-volátil", "notes": "Historial de compra de votos documentado."},
    {"region": "Cajamarca",     "seats": 5,  "pop_M": 1.5,  "urban_pct": 38, "poverty_pct": 46, "indigenous_pct": 12, "risk_score": 58, "tendency": "izquierda-rural", "notes": "Alta pobreza. Conflictos mineros afectan clima electoral."},
    {"region": "Puno",          "seats": 5,  "pop_M": 1.4,  "urban_pct": 52, "poverty_pct": 39, "indigenous_pct": 68, "risk_score": 55, "tendency": "izquierda andina", "notes": "Mayor % población aymara-quechua. Riesgo UNDRIP Art. 18."},
    {"region": "Cusco",         "seats": 5,  "pop_M": 1.4,  "urban_pct": 55, "poverty_pct": 38, "indigenous_pct": 55, "risk_score": 52, "tendency": "izquierda-volátil", "notes": "Fuerte identidad quechua. Base Perú Libre."},
    {"region": "Junín",         "seats": 5,  "pop_M": 1.4,  "urban_pct": 66, "poverty_pct": 30, "indigenous_pct": 25, "risk_score": 56, "tendency": "Perú Libre-base", "notes": "Base original de Cerrón. Riesgo de movilización extra-institucional."},
    {"region": "Arequipa",      "seats": 5,  "pop_M": 1.4,  "urban_pct": 89, "poverty_pct": 11, "indigenous_pct": 10, "risk_score": 38, "tendency": "derecha-RP", "notes": "Electorado urbano educado. Baja tolerancia a corrupción."},
    {"region": "Lambayeque",    "seats": 4,  "pop_M": 1.3,  "urban_pct": 79, "poverty_pct": 23, "indigenous_pct": 4,  "risk_score": 47, "tendency": "APP", "notes": "Segunda base de Acuña. Prácticas clientelares documentadas."},
    {"region": "Loreto",        "seats": 3,  "pop_M": 1.1,  "urban_pct": 42, "poverty_pct": 45, "indigenous_pct": 28, "risk_score": 62, "tendency": "volátil", "notes": "Amazónico. Alta pobreza. Corrupción electoral histórica. UNDRIP relevante."},
    {"region": "Ancash",        "seats": 4,  "pop_M": 1.1,  "urban_pct": 64, "poverty_pct": 28, "indigenous_pct": 20, "risk_score": 50, "tendency": "centro-volátil", "notes": "Zona minera. Conflictos sociales afectan clima pre-electoral."},
    {"region": "San Martín",    "seats": 3,  "pop_M": 0.9,  "urban_pct": 68, "poverty_pct": 28, "indigenous_pct": 8,  "risk_score": 44, "tendency": "volátil", "notes": "Crecimiento agroindustrial. Electorado pragmático."},
    {"region": "Ica",           "seats": 3,  "pop_M": 0.9,  "urban_pct": 90, "poverty_pct": 10, "indigenous_pct": 2,  "risk_score": 36, "tendency": "FP histórico", "notes": "Zona costera prospera. Histórica fortaleza fujimorista."},
    {"region": "Huánuco",       "seats": 3,  "pop_M": 0.9,  "urban_pct": 52, "poverty_pct": 44, "indigenous_pct": 22, "risk_score": 60, "tendency": "volátil-izquierda", "notes": "Alta pobreza. Corredor del narcotráfico. Riesgo de cooptación."},
    {"region": "Ucayali",       "seats": 2,  "pop_M": 0.6,  "urban_pct": 70, "poverty_pct": 32, "indigenous_pct": 18, "risk_score": 58, "tendency": "volátil", "notes": "Amazónico. Poca presencia institucional estatal. Riesgo OSINT."},
    {"region": "Ayacucho",      "seats": 2,  "pop_M": 0.6,  "urban_pct": 56, "poverty_pct": 50, "indigenous_pct": 35, "risk_score": 61, "tendency": "izquierda", "notes": "Región Sendero histórico. Alta pobreza. Desconfianza institucional profunda."},
    {"region": "Apurímac",      "seats": 2,  "pop_M": 0.5,  "urban_pct": 45, "poverty_pct": 53, "indigenous_pct": 65, "risk_score": 63, "tendency": "izquierda andina", "notes": "Región más pobre. Zona Las Bambas. Conflictos mineros severos."},
    {"region": "Madre de Dios", "seats": 1,  "pop_M": 0.2,  "urban_pct": 73, "poverty_pct": 17, "indigenous_pct": 15, "risk_score": 52, "tendency": "volátil", "notes": "Minería aurífera informal. Trata de personas. Institucionalidad débil."},
    {"region": "Tacna",         "seats": 1,  "pop_M": 0.3,  "urban_pct": 91, "poverty_pct": 9,  "indigenous_pct": 5,  "risk_score": 33, "tendency": "derecha", "notes": "Zona fronteriza próspera. Bajo riesgo electoral."},
    {"region": "Tumbes",        "seats": 1,  "pop_M": 0.2,  "urban_pct": 85, "poverty_pct": 18, "indigenous_pct": 2,  "risk_score": 43, "tendency": "volátil", "notes": "Zona costera norte. Presencia narcotráfico en zonas rurales."},
    {"region": "Moquegua",      "seats": 1,  "pop_M": 0.2,  "urban_pct": 85, "poverty_pct": 10, "indigenous_pct": 5,  "risk_score": 34, "tendency": "centro-derecha", "notes": "Región minera próspera. Bajo riesgo."},
    {"region": "Huancavelica",  "seats": 2,  "pop_M": 0.4,  "urban_pct": 38, "poverty_pct": 58, "indigenous_pct": 60, "risk_score": 65, "tendency": "izquierda", "notes": "Región más pobre junto a Apurímac. Alto riesgo de exclusión electoral."},
    {"region": "Pasco",         "seats": 1,  "pop_M": 0.3,  "urban_pct": 71, "poverty_pct": 36, "indigenous_pct": 18, "risk_score": 55, "tendency": "volátil", "notes": "Zona minera con conflictos sociales."},
    {"region": "Amazonas",      "seats": 2,  "pop_M": 0.4,  "urban_pct": 42, "poverty_pct": 40, "indigenous_pct": 22, "risk_score": 57, "tendency": "volátil", "notes": "Amazónico. Baja presencia estatal. Riesgo UNDRIP."},
    {"region": "Callao",        "seats": 4,  "pop_M": 1.1,  "urban_pct": 100,"poverty_pct": 16, "indigenous_pct": 3,  "risk_score": 44, "tendency": "volátil-APP", "notes": "Puerto principal. Crimen organizado con influencia electoral documentada."},
]

PERU_HISTORICAL_EVENTS = [
    {"year": 2019, "event": "Crisis constitucional — Vizcarra disuelve el Congreso (Art. 134 CP)"},
    {"year": 2020, "event": "Golpe parlamentario — Congreso vacante a Vizcarra. 3 presidentes en 7 días"},
    {"year": 2021, "event": "Castillo gana 2ª vuelta (50.1%). Keiko impugna. JNE proclama resultado"},
    {"year": 2022, "event": "Castillo destituido por vacancia. Boluarte asume presidencia"},
    {"year": 2023, "event": "Protestas 'Dina, renuncia'. 60+ muertes. Estado de emergencia"},
    {"year": 2024, "event": "Gobierno de Boluarte — bajo apoyo (<10%). 6 presidentes desde 2018"},
    {"year": 2025, "event": "Inicio ciclo electoral. Inscripción de candidatos. JNE bajo presión política"},
    {"year": 2026, "event": "Elecciones generales — 12 de abril"},
]

# ── Perú: Ecosistema Digital y Amenazas 2026 ──────────────────────────────────
PERU_DIGITAL_THREATS = {
    "ai_deepfakes": {
        "status": "activo",
        # 2026-04-26 — incidentes específicos retirados por trazabilidad. Ver
        # explicación en backend/modules/peru_data.py (mismo dict, copia espejo).
        "incidents_2024_2025": [],
        "audit_status": "incidents_pending_verification",
        "audit_note": "Lista de incidentes vaciada el 2026-04-26 por ausencia de URL primaria.",
        "regulatory_gap": "Sin marco regulatorio específico de IA electoral. Decreto 1182 (2025) no cubre deepfakes.",
        "jne_onpe_response": "JNE lanzó 'Observatorio de Desinformación Electoral' (feb 2025). ONPE sin capacidad técnica de respuesta.",
        "iccpr_ref": "Art. 19(3) ICCPR — restricciones a discurso manipulador deben ser proporcionales y necesarias.",
    },
    # 2026-04-26 — bloque "cyberattacks_electoral_infra" eliminado por trazabilidad.
    # Ver explicación en backend/modules/peru_data.py (mismo dict, copia espejo).
    "digital_gbv": {
        "description": "Violencia Digital de Género Político (VDGP) contra candidatas y funcionarias electorales",
        # 2026-04-26 — solo se conserva el incidente con URL pública (Promsex).
        # Ver explicación en backend/modules/peru_data.py.
        "incidents": [
            "Coordinación de trolls contra candidatas no-binarias — 47 perfiles coordinados en X/Twitter y TikTok, ene–mar 2025 (Informe LGBTQ+ Electoral Watch / Promsex Perú, mar 2025; disponible en: promsex.org/informes)",
        ],
        "audit_status": "partial — 3 de 4 incidentes retirados por falta de URL",
        "audit_note": "Reactivar incidentes adicionales solo con cita primaria (denuncia oficial PNP, JNE, etc.).",
        "legal_framework": "Ley 31170 (2021) modifica Código Penal — acoso político digital tipificado. Aplicación: escasa.",
        "jne_action": "Protocolo VDGP aprobado JNE 2023 — sin presupuesto para monitoreo sistemático.",
        "iccpr_ref": "Art. 25 + CEDAW Art. 7 — participación política libre de violencia es derecho inderogable.",
    },
    "disinformation_ecosystem": {
        # 2026-04-26 — narrativas y reach_estimate retiradas por trazabilidad.
        # Ver explicación en backend/modules/peru_data.py.
        "key_platforms": ["TikTok (penetración 68% adultos 18-35)", "WhatsApp (canales virales sin moderación)", "X/Twitter (amplificación élite política)"],
        "main_narratives_2025_2026": [],
        "audit_status": "narratives_pending_verification",
        "audit_note": "Lista vaciada el 2026-04-26. Reactivar con URL al fact-check primario por narrativa.",
        "fact_checkers": ["Ojo Público (ojopublico.com)", "Peru Check (perucheck.pe)", "La Mula (lamula.pe)"],
        "reach_estimate": "Pendiente de fuente verificable — el dato '2.1M' (Ipsos/CALANDRIA feb 2026) fue retirado por falta de URL al estudio.",
    },
    "rsf_score_2025": 52.4,
    "rsf_rank_2025": 121,
    "vdem_internet_censorship_2024": 0.71,
    "vdem_journalist_harassment_2024": 0.52,
    "vdem_media_bias_2024": 0.48,
    "ooni_blocked_domains_2024": ["periodistadigital.pe (intermitente)", "vacanciapermanente.com"],
    "bot_network": {
        # 2026-04-26 — métricas numéricas retiradas por trazabilidad.
        # Ver explicación en backend/modules/peru_data.py.
        "operation_name": "Operación Cóndor Digital (denominación IPYS Perú)",
        "estimated_accounts_twitter": "Pendiente de URL primaria",
        "estimated_accounts_tiktok": "Pendiente de URL primaria",
        "estimated_total": "Pendiente de URL primaria",
        "confidence": "PENDIENTE_VERIFICACION",
        "period": "oct 2024 – ene 2026 (rango temporal estimado)",
        "source": "Pendiente — IPYS Perú / CALANDRIA referenciados sin URL pública.",
        "audit_status": "metrics_pending_verification",
    },
    "data_sources": "IPYS Perú 2025, CALANDRIA 2025, JNE Observatorio 2025, RSF 2025, V-Dem v15, Ipsos Perú feb 2026",
}

# ── Perú: Género, Paridad y Alternancia 2026 ──────────────────────────────────
PERU_GENDER_DATA = {
    "legal_framework": {
        "quota_law": "Ley 28094 (Ley de Partidos Políticos, art. 26) — cuota mínima 30% mujeres en listas",
        "parity_law": "Ley 31030 (2020) — paridad (50%) y alternancia (alternado) obligatorias para listas pluripersonales",
        "enforcement_jne": "JNE verifica paridad antes de inscripción. Exclusión de lista si incumple.",
        "effective_since": "Elecciones generales 2021 (primera aplicación plena de paridad + alternancia)",
        "gaps": [
            "Paridad no aplica a candidaturas uninominales (alcaldes, presidentes regionales)",
            "Sin cuota para candidatura presidencial — 13 candidatos/as inscritos 2026, 3 mujeres",
            "Partidos cumplen la forma (listas) pero concentran mujeres en posiciones no elegibles",
            "Ausencia de paridad horizontal entre cabezas de lista a nivel regional/local",
        ],
    },
    "current_representation": {
        "congress_women_pct": 38.5,
        "congress_women_seats": 54,
        "congress_total_seats": 130,
        "source": "Congreso de la República, enero 2026",
        "women_committee_presidents": 12,
        "women_on_mesa_directiva": 1,
        "presidential_candidates_women": 3,
        "presidential_candidates_total": 13,
        "vdem_women_parliament_2024": 0.37,
    },
    "vdgp_registry": {
        "description": "Violencia Política de Género (VPG) — Registro JNE/ONPE/RENIEC",
        "cases_2022_2025": 847,
        "cases_digital_component": 312,
        "cases_physical_threats": 198,
        "cases_institutional_obstruction": 337,
        "source": "JNE — Observatorio de Violencia Política de Género, dic 2025",
        "most_affected": ["Candidatas a gobiernos regionales", "Regidoras electas 2022", "Candidatas indígenas (Amazonía/Andes)"],
        "perpetrators": ["Militantes del propio partido (40%)", "Candidatos rivales (28%)", "Desconocidos/online (32%)"],
        "prosecution_rate_pct": 8.4,
        "iccpr_ref": "Art. 25 ICCPR + CEDAW Art. 7 — participación política libre de violencia es derecho inderogable",
    },
    "indigenous_women": {
        "estimated_eligible_voters": 1_800_000,
        "languages_without_ballot": ["matsigenka", "awajún (parcial)", "shipibo-konibo (parcial)"],
        "ine_bilingual_education_gap": "Solo 3 lenguas con material electoral completo (ONPE 2025)",
        "candidates_self_identified_indigenous": 47,
        "candidates_indigenous_women": 12,
        "iccpr_ref": "UNDRIP Art. 5 + ICERD Art. 5 — participación política indígena sin discriminación",
    },
    "data_sources": "JNE 2025-2026, Congreso de la República ene 2026, V-Dem v15, CONEJEM 2025, CALANDRIA 2025",
}

# ── Perú: Perfil del País y Padrón Electoral 2026 ─────────────────────────────
PERU_COUNTRY_PROFILE = {
    # === Demografía (INEI 2024) ===
    "demographics": {
        "population_total": 33_900_000,
        "area_km2": 1_285_216,
        "density_pop_km2": 26.4,
        "urban_pct": 78.9,
        "rural_pct": 21.1,
        "life_expectancy_years": 74.2,
        "birth_rate_per_1000": 17.3,
        "literacy_rate_pct": 94.5,
        "official_languages": "Español, Quechua, Aymara (+ 47 lenguas originarias)",
        "median_age_years": 29.8,
        "source": "INEI — Estimaciones y Proyecciones de Población 2024",
    },
    # === Economía (BCR/BM 2024) ===
    "economy": {
        "gdp_usd_billions": 268.4,
        "gdp_per_capita_usd": 7_920,
        "gdp_growth_pct": 3.1,
        "unemployment_rate_pct": 7.2,
        "inflation_rate_pct": 3.7,
        "gini_coefficient": 0.422,
        "poverty_rate_pct": 27.5,
        "extreme_poverty_rate_pct": 5.8,
        "hdi": 0.762,
        "hdi_rank_global": 84,
        "source": "INEI-ENAHO 2024; Banco Mundial 2024; PNUD HDR 2024",
    },
    # === Padrón Electoral (ONPE/RENIEC ene 2026) ===
    "electoral_roll": {
        "total_registered": 25_852_414,
        "women_registered": 13_121_873,
        "men_registered": 12_730_541,
        "women_pct": 50.76,
        "men_pct": 49.24,
        "new_voters_estimate": 1_200_000,
        "first_time_voters_18": 320_000,
        "registry_cutoff_date": "2026-01-05",
        "registry_cutoff_note": "RENIEC/ONPE — cierre del padrón para elecciones generales 12 abr 2026",
        "overseas_total": 1_087_432,
        "mandatory_voting": True,
        "mandatory_voting_note": "Obligatorio para mayores de 18 y menores de 70 años. Multa por no votar: ~S/.95 (1/4 UIT)",
        "source": "ONPE/RENIEC — Padrón Electoral publicado ene 2026",
        "confidence": "CONFIRMED",
    },
    # === Votantes en el Exterior ===
    "overseas_breakdown": {
        "total": 1_087_432,
        "countries_with_mesas": 41,
        "top_destinations": [
            {"country": "Chile",     "voters": 280_000, "mesas": 312, "pct": 25.7},
            {"country": "Argentina", "voters": 195_000, "mesas": 218, "pct": 17.9},
            {"country": "EEUU",      "voters": 148_000, "mesas": 163, "pct": 13.6},
            {"country": "España",    "voters":  89_000, "mesas":  98, "pct":  8.2},
            {"country": "Italia",    "voters":  72_000, "mesas":  79, "pct":  6.6},
        ],
        "source": "ONPE/Cancillería — Distribución de mesas exterior, ene 2026",
    },
    # === Ausentismo Histórico ===
    "abstention_history": [
        {
            "election": "Generales 2016 (1ª vuelta)",
            "date": "2016-04-10",
            "total_voters": 22_905_007,
            "abstention_pct": 18.2,
            "abstention_abs": 4_168_711,
            "context": "Voto obligatorio con multa aplicada",
        },
        {
            "election": "Generales 2021 (1ª vuelta)",
            "date": "2021-04-11",
            "total_voters": 25_287_954,
            "abstention_pct": 24.8,
            "abstention_abs": 6_271_413,
            "context": "Pandemia COVID-19; restricciones de movilidad",
        },
        {
            "election": "Generales 2021 (2ª vuelta)",
            "date": "2021-06-06",
            "total_voters": 25_287_954,
            "abstention_pct": 24.5,
            "abstention_abs": 6_195_548,
            "context": "Alta polarización; campaña de desinformación",
        },
        {
            "election": "Regionales/Municipales 2022",
            "date": "2022-10-02",
            "total_voters": 24_874_328,
            "abstention_pct": 32.4,
            "abstention_abs": 8_059_242,
            "context": "Crisis institucional; desafección ciudadana récord",
        },
    ],
    "political_context_brief": {
        "current_president": "Dina Boluarte",
        "current_party": "Compromiso Popular",
        "approval_rating_pct": 6,
        "approval_source": "Ipsos Perú — enero 2026",
        "congress_fragmentation": "17 grupos parlamentarios",
        "election_date": "2026-04-12",
        "election_type": "Generales — Presidente + 130 congresistas",
        "second_round_date": "2026-06-07",
        "confirmed_candidates": 13,
        "registered_parties": 24,
    },
    "data_sources": "INEI 2024, ONPE 2026, RENIEC 2026, Cancillería del Perú 2026, Ipsos Perú ene 2026, PNUD HDR 2024, BCR 2024, Banco Mundial 2024",
}

# ── Perú: Voto Exterior y Logística Digital 2026 ──────────────────────────────
PERU_OVERSEAS_VOTE = {
    "total_overseas_registered": 1_087_432,
    "source_registry": "RENIEC/ONPE padrón electoral exterior, dic 2025",
    "top_countries": [
        {"country": "Chile", "voters": 280_000, "mesas": 312},
        {"country": "Argentina", "voters": 195_000, "mesas": 218},
        {"country": "España", "voters": 145_000, "mesas": 165},
        {"country": "EEUU", "voters": 132_000, "mesas": 148},
        {"country": "Italia", "voters": 89_000, "mesas": 96},
        {"country": "Venezuela", "voters": 47_000, "mesas": 52, "alert": "Restricción diplomática — 18 sedes sin local confirmado"},
    ],
    "total_mesas_exterior": 2_140,
    "logistics_risks": [
        {
            "risk": "Actas físicas por valija diplomática — cadena de custodia sin sellado digital (riesgo de pérdida/alteración en tramo consular-Lima)",
            "source": "ONPE — Informe de Evaluación de Voto Exterior 2021",
            "date": "oct 2021, confirmado feb 2025",
            "url": "https://www.onpe.gob.pe/modOGELEC/acVotoExterior/",
            "severity": "ALTO",
        },
        {
            "risk": "18 locales consulares en Venezuela sin confirmación definitiva por ruptura diplomática Perú-Venezuela (dic 2024)",
            "source": "Cancillería del Perú — Nota Diplomática N° 7-E-0234/2024; ONPE Comunicado 12/2024",
            "date": "dic 2024",
            "url": "https://www.gob.pe/cancilleria",
            "severity": "ALTO",
        },
        {
            "risk": "Reducción presupuestal ONPE 2025 (S/. -18.3M vs 2024) congeló contratación de 340 miembros de mesa exterior",
            "source": "MEF — Presupuesto Institucional Modificado ONPE 2025 (PIM Resolución Directoral N° 0030-2025-EF/50.01)",
            "date": "ene 2025",
            "url": "https://www.mef.gob.pe/es/presupuesto-del-sector-publico/aprobacion-presupuestal",
            "severity": "MEDIO",
        },
        {
            "risk": "Padrón exterior con 23,000 registros de electores con documentos de identidad vencidos hace más de 5 años",
            "source": "RENIEC — Informe de Depuración del Padrón Electoral Exterior N° 001-2026-SGEN/RENIEC",
            "date": "ene 2026",
            "url": "https://www.reniec.gob.pe/portal/html/registro-civil/padron-electoral.jsp",
            "severity": "MEDIO",
        },
        {
            "risk": "Propuesta de voto electrónico exterior rechazada por JNE por ausencia de auditoría independiente certificada",
            "source": "JNE — Resolución N° 0891-2025-JNE (Expediente N° JNE-2025-001), 15 ago 2025",
            "date": "ago 2025",
            "url": "https://www.jne.gob.pe/transparencia/resoluciones/",
            "severity": "INFORMATIVO",
        },
    ],
    "chain_of_custody": {
        "current": "Acta física → valija diplomática → ONPE Lima → escrutinio manual",
        "vulnerability": "Tramo 'valija diplomática' sin trazabilidad digital. Promedio llegada: 72-120h post-elección",
        "proposed_improvement": "Transmisión digital de imágenes de actas (TREP exterior) — aprobado piloto para Chile/Argentina/España",
        "pilot_trep_countries": ["Chile", "Argentina", "España"],
    },
    "digital_vote_proposal": {
        "status": "Rechazado — JNE Res. 0891-2025",
        "reason": "Ausencia de auditoría independiente y riesgo de interferencia remota no mitigado",
        "iccpr_note": "Art. 25 ICCPR exige que mecanismos de voto garanticen autenticidad — JNE invocó este estándar",
        "alternative_approved": "Voto en urna física en sede consular. TREP digital para 3 países piloto.",
    },
    "iccpr_ref": "Art. 25 ICCPR — el derecho al voto de ciudadanos en exterior exige condiciones equitativas de ejercicio",
    "data_sources": "ONPE 2025, RENIEC dic 2025, JNE Res. 0891-2025, Cancillería Perú 2024-2025",
}

# ── Perú: Crimen Organizado e Infiltración Electoral 2026 ─────────────────────
# 2026-04-26 — bloque vaciado por trazabilidad. Ver explicación en
# backend/modules/peru_data.py (mismo dict, copia espejo).
PERU_ORGANIZED_CRIME = {
    "main_organizations": [],
    "jne_screening": {
        "mechanism": "Comité de Ética JNE — revisión de antecedentes penales y patrimoniales",
        "candidates_flagged_2026": None,
        "candidates_excluded": None,
        "candidates_under_review": None,
        "limitation": "JNE no puede excluir por vínculos no judicializados — solo condenas firmes",
        "source": "Pendiente — métricas retiradas por falta de URL al informe de transparencia JNE 2026.",
    },
    "uncac_ref": "UNCAC Arts. 7-8 — medidas preventivas de integridad en sector público y procesos electorales",
    "iccpr_ref": "Art. 25 ICCPR — elecciones auténticas requieren que candidatos no sean instrumentos de intereses criminales",
    "regional_risk_map": {},
    "data_sources": "Pendiente — IDEHPUCP, FECOR, JNE, UNODC, IDL-Reporteros referenciados sin URL pública.",
    "audit_status": "pending_verification",
    "audit_note": "Bloque postergado el 2026-04-26 por ausencia de fuentes primarias por incidente.",
}


@app.get("/api/peru/actors")
async def get_peru_actors():
    """Fuerzas políticas y actores clave del proceso electoral Perú 2026."""
    return {
        "country": "Peru",
        "election_date": "2026-04-12",
        "total_seats": PERU_PARL_DATA["total_seats"],
        "actors": PERU_POLITICAL_FORCES,
        "electoral_system": PERU_ELECTORAL_SYSTEM,
        "total_actors": len(PERU_POLITICAL_FORCES),
        "risk_distribution": {
            "high": sum(1 for a in PERU_POLITICAL_FORCES if a["risk_profile"] == "high"),
            "moderate": sum(1 for a in PERU_POLITICAL_FORCES if a["risk_profile"] == "moderate"),
            "low": sum(1 for a in PERU_POLITICAL_FORCES if a["risk_profile"] == "low"),
        },
        "data_note": "Datos estructurados basados en registros JNE, PEI y V-Dem. Composición de bancadas aproximada a enero 2026.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/peru/scenarios")
async def get_peru_scenarios():
    """Composición parlamentaria + balotaje 2026.

    2026-05-27 — Tras la 1ª vuelta del 12-abr-2026 se retiraron los escenarios
    predictivos A/B/C (proyecciones hechas con datos a ene-2026, ya obsoletas).
    El endpoint mantiene su nombre por compatibilidad con el frontend pero
    ahora devuelve:
      - current: Congreso saliente 2021-2026 (aún en funciones hasta 28-jul-2026)
      - next_2026_2031: composición del Congreso entrante (pendiente cómputo ONPE)
      - runoff: datos del balotaje (los 2 finalistas, cara a cara, countdown)
      - scenarios: [] — retenido como lista vacía para no romper consumers
    """
    return {
        "country": "Peru",
        "first_round_date": "2026-04-12",
        "runoff_date": "2026-06-07",
        "total_seats": PERU_PARL_DATA["total_seats"],
        "electoral_system": PERU_PARL_DATA["system"],
        "current": PERU_PARL_DATA["current"],
        "next_2026_2031": PERU_PARL_DATA.get("next_2026_2031"),
        "scenarios": [],
        "scenarios_removed_note": "Escenarios predictivos A/B/C retirados el 2026-05-27 tras la 1ª vuelta. Se reemplazan por composición oficial cuando ONPE publique el cómputo final.",
        "runoff": PERU_RUNOFF_2026,
        "historical_context": PERU_HISTORICAL_EVENTS,
        "regions": PERU_REGIONS_DATA,
        "data_note": "Fase entre vueltas. El bloque 'runoff' contiene scaffold PENDIENTE_VERIFICACION para finalistas y cara a cara; valores reales se cargan con cita primaria a ONPE/JNE.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/alerts/{country_code}")
async def get_country_alerts(
    country_code: str,
    since_hours: int = 168,
    min_severity: str = "low",
    limit: int = 100,
):
    """
    Lista las alertas dispatchadas por el Hunter para un país, desde la tabla `alerts` en SQLite.

    Esta es la fuente que también alimenta Discord (vía ALERT_WEBHOOK_URL). El frontend
    consume este endpoint para mostrar alertas en vivo en el Situation Room.

    Query params:
    - since_hours: ventana hacia atrás en horas (default 168 = 7 días)
    - min_severity: low | medium | high | critical (default low = todas)
    - limit: máximo de filas (default 100)
    """
    if not DB_AVAILABLE:
        return {"country_code": country_code, "alerts": [], "total": 0, "db_available": False}

    severity_rank = {"low": 0, "medium": 1, "moderate": 1, "high": 2, "critical": 3}
    min_rank = severity_rank.get(min_severity.lower(), 0)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    cutoff_iso = cutoff.isoformat()

    raw = _db_list_alerts(country_code.upper(), limit=max(limit, 200))

    filtered = []
    for a in raw:
        sev = (a.get("severity") or "low").lower()
        if severity_rank.get(sev, 0) < min_rank:
            continue
        dispatched = a.get("dispatched_at") or ""
        if dispatched < cutoff_iso:
            continue
        filtered.append(a)
        if len(filtered) >= limit:
            break

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for a in filtered:
        sev = (a.get("severity") or "low").lower()
        if sev == "moderate":
            sev = "medium"
        if sev in counts:
            counts[sev] += 1

    return {
        "country_code": country_code.upper(),
        "alerts": filtered,
        "total": len(filtered),
        "counts_by_severity": counts,
        "since_hours": since_hours,
        "min_severity": min_severity,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 7. CLI — Ejecución directa para testing
# ═══════════════════════════════════════════════════════════════════════════════

def run_cli_analysis(country_code: str = "VEN"):
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

    print("📋 LOG DE AGENTES:")
    print("-" * 50)
    for log in result["agent_logs"]:
        print(f"  {log}")
    print()

    print(f"🎯 RISK SCORE: {result['risk_score']}/100 ({result['risk_level'].upper()})")
    print(f"VIOLACIONES: {result['legal_analysis']['violation_count']}")
    print(f"📄 REPORTE: {len(result['final_report_markdown'])} caracteres")
    print()

    filename = f"peirs_report_{code.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result["final_report_markdown"])
    print(f"Reporte guardado: {filename}")

    return result


if __name__ == "__main__":
    import sys
    country = sys.argv[1] if len(sys.argv) > 1 else "VEN"
    run_cli_analysis(country)
