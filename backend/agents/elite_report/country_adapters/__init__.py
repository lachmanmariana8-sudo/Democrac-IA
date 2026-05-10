"""CountryAdapter — interfaz pluggable para datos electorales por país.

Sprint 2 (10-may-2026): Antes de este modulo, todos los datos especificos
de Peru (instituciones JNE/ONPE/RENIEC, marco legal, recomendaciones,
arquitectura tecnologica STAE/SCE/SPR, calendario electoral, etc.)
estaban hardcoded en `elite_report.py:_attach_visualizations` y
`organizers/phase_organizer.py`. Esto hacia imposible escalar a Brasil
o USA sin reescribir la logica.

Ahora cada pais implementa la interfaz `CountryAdapter` con sus datos
canonicos. `_attach_visualizations` llama `get_adapter(cc).method(...)`
en vez de inline data dicts. Para sumar Brasil 2026:

    from .brazil import BrazilAdapter
    _ADAPTERS["BRA"] = BrazilAdapter

Y todo el pipeline funciona con TSE/TREs en lugar de JNE/ONPE/RENIEC.
"""
from __future__ import annotations

from typing import Dict, Type

from .base import CountryAdapter
from .peru import PeruAdapter

_ADAPTERS: Dict[str, Type[CountryAdapter]] = {
    "PER": PeruAdapter,
}


def get_adapter(country_code: str) -> CountryAdapter:
    """Devuelve adapter del pais. Default: PeruAdapter (legacy).

    Mientras se onboardea Brasil/USA, paises sin adapter caen al de
    Peru — eso preserva el comportamiento previo del Elite Report. Una
    vez que existan BrazilAdapter/USAAdapter, esta logica se reemplaza
    por raise ValueError para forzar adapter explicito.
    """
    cls = _ADAPTERS.get((country_code or "").upper())
    if cls is None:
        # Fallback temporal: PER mientras no haya BRA/USA adapters.
        return PeruAdapter()
    return cls()


__all__ = ["CountryAdapter", "PeruAdapter", "get_adapter"]
