"""Registro CENTRAL y VERSIONADO de la configuración del pipeline PEIRS.

Único lugar de verdad para los parámetros que afectan la clasificación, la
consolidación y la escalación de evidencia. Cada informe estampa
`config_fingerprint()` (versión + hash + clasificador) para que un tercero pueda
auditar con qué parámetros exactos se produjo — pilar de auditabilidad del
Marco de Calidad PEIRS (docs/QUALITY_FRAMEWORK.md).

Los módulos del pipeline importan sus umbrales desde aquí (no los redefinen):
consolidators.py y runoff_enrichment.py. Pendiente de migrar (P2): los pesos de
hunter_loader.py y el crisis_index de elite_report.py — hoy se reflejan aquí
como valores canónicos para el sello del informe.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

from modules import config as _cfg

# Versión del pipeline (capacidades del generador) y de la configuración.
# Subir CONFIG_VERSION ante cualquier cambio de umbral/peso documentado abajo.
PIPELINE_VERSION = "1.0.0"
CONFIG_VERSION = "1.0.0"

# ── Consolidación: un hecho = un hallazgo con todas sus fuentes ──────────────
CONSOLIDATION_JACCARD_THRESHOLD = 0.5
CONSOLIDATION_STEM_LEN = 6

# ── Escalación de audit_status por fuentes primarias independientes ──────────
MIN_INDEPENDENT_PRIMARY = 2       # ≥2 ⇒ VERIFIED_SECONDARY
CONFIRM_INDEPENDENT_PRIMARY = 3   # ≥3 (o doc oficial/OONI) ⇒ CONFIRMED
PRIMARY_CREDIBILITY = ("high",)   # tier que cuenta como fuente primaria

# ── Pesos de severidad ───────────────────────────────────────────────────────
SEVERITY_WEIGHTS_PRIORITY = {"critical": 10, "high": 7, "medium": 3, "low": 1, "info": 0.5}
CRISIS_INDEX_WEIGHTS = {"critical": 1.0, "high": 0.55, "medium": 0.20, "low": 0.05, "info": 0.0}

# Snapshot serializable (base del hash de auditoría).
AUDIT_CONFIG: Dict[str, Any] = {
    "pipeline_version": PIPELINE_VERSION,
    "llm": {"model": _cfg.LLM_MODEL, "temperature": _cfg.LLM_TEMPERATURE},
    "datasets": {
        "vdem": getattr(_cfg, "VDEM_VERSION", None),
        "freedom_house": getattr(_cfg, "FH_VERSION", None),
        "rsf": getattr(_cfg, "RSF_VERSION", None),
        "pei": getattr(_cfg, "PEI_VERSION", None),
    },
    "consolidation": {
        "jaccard_threshold": CONSOLIDATION_JACCARD_THRESHOLD,
        "stem_len": CONSOLIDATION_STEM_LEN,
        "scope": "same_day",
    },
    "escalation": {
        "min_independent_primary": MIN_INDEPENDENT_PRIMARY,
        "confirm_independent_primary": CONFIRM_INDEPENDENT_PRIMARY,
        "primary_credibility": list(PRIMARY_CREDIBILITY),
    },
    "severity_weights_priority": SEVERITY_WEIGHTS_PRIORITY,
    "crisis_index_weights": CRISIS_INDEX_WEIGHTS,
}


def config_hash() -> str:
    """Hash estable (sha256[:16]) del snapshot de configuración."""
    blob = json.dumps(AUDIT_CONFIG, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def classifier_fingerprint() -> Dict[str, Optional[str]]:
    """Modelo del clasificador + hash de su system prompt (versión del prompt)."""
    prompt_hash: Optional[str] = None
    try:
        from agents.hunter import _SYSTEM_PROMPT  # import perezoso: evita costo/ciclos
        prompt_hash = hashlib.sha256(_SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:16]
    except Exception:
        prompt_hash = None
    return {"model": _cfg.LLM_MODEL, "prompt_sha256_16": prompt_hash}


def config_fingerprint() -> Dict[str, Any]:
    """Sello de auditoría que el informe estampa: versión + hash + clasificador."""
    return {
        "pipeline_version": PIPELINE_VERSION,
        "config_version": CONFIG_VERSION,
        "config_hash": config_hash(),
        "classifier": classifier_fingerprint(),
        "config": AUDIT_CONFIG,
    }
