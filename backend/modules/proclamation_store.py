"""Persistencia del resultado OFICIAL proclamado (override del balotaje).

El dict estático PERU_RUNOFF_2026 refleja el estado PROVISIONAL e indeterminado.
Cuando el EMB (JNE) proclama el resultado oficial, el observador lo carga por el
endpoint POST /api/runoff/{cc}/proclamation; este módulo lo persiste en disco como
override versionable y trazable, SIN editar el código fuente (peru_data.py).

El override se fusiona en `second_round_results` por enrich_runoff_observation:
proclamation.proclaimed=True + winner, uncertainty.indeterminate=False, status, y
opcionalmente un dispute_resolution_tracker. La REGENERACIÓN final del informe
sigue siendo una acción autorizada por el usuario (no se dispara aquí).

Función con I/O mínimo, sin estado de proceso. Path configurable por env
RUNOFF_OVERRIDES_DIR (default: <backend>/../data/overrides).
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

_DEFAULT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "overrides")


def overrides_dir() -> str:
    return os.getenv("RUNOFF_OVERRIDES_DIR", _DEFAULT_DIR)


def _path(country_code: str) -> str:
    cc = (country_code or "").upper()
    return os.path.join(overrides_dir(), f"{cc}_proclamation.json")


def load_proclamation(country_code: str) -> Optional[Dict[str, Any]]:
    """Devuelve el override de proclamación persistido para el país, o None."""
    p = _path(country_code)
    try:
        if not os.path.exists(p):
            return None
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_proclamation(country_code: str, payload: Dict[str, Any]) -> str:
    """Persiste el resultado oficial proclamado. Devuelve la ruta del archivo."""
    os.makedirs(overrides_dir(), exist_ok=True)
    p = _path(country_code)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return p


def clear_proclamation(country_code: str) -> bool:
    """Elimina el override (vuelve al estado provisional). True si existía."""
    p = _path(country_code)
    try:
        if os.path.exists(p):
            os.remove(p)
            return True
    except Exception:
        pass
    return False
