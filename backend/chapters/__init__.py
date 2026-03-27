"""
chapters/ — Módulo de generadores de capítulos del informe VIP para DEMOCRAC.IA (PEIRS)

Estado de migración:
  - chapters/generators.py → todas las funciones _generate_* extraídas de app.py

Funciones exportadas:
  _generate_country_profile_section   — Cap. 0: Perfil del País
  _generate_executive_summary         — Cap. 1: Resumen Ejecutivo & Dashboard
  _generate_political_context         — Cap. 2: Contexto Político y Marco Legal
  _generate_emb_chapter               — Cap. 3: Administración Electoral (EMB)
  _generate_inclusivity_chapter       — Cap. 4: Inclusividad y Derechos Humanos
  _generate_campaign_chapter          — Cap. 5: Campaña, Redes de Poder y Financiamiento
  _generate_digital_chapter           — Cap. 6: Ecosistema de Información y Monitoreo Digital
  _generate_voting_day_chapter        — Cap. 7: Desarrollo del Día de Votación
  _generate_observation_chapter       — Cap. 7 (alternativo): Observación Electoral
  _generate_justice_chapter           — Cap. 8: Justicia Electoral y Resolución de Disputas
  _generate_recommendations           — Cap. 9: Matriz de Recomendaciones VIP
  _generate_ai_regulation_chapter     — Cap. 10: IA Electoral (solo Perú 2026)

Nota: las funciones originales permanecen definidas en app.py durante la
fase de migración.  Solo se agregan aliases/imports condicionales para
habilitar la transición gradual.
"""

from __future__ import annotations

try:
    from chapters.generators import (
        _generate_country_profile_section,
        _generate_executive_summary,
        _generate_political_context,
        _generate_emb_chapter,
        _generate_inclusivity_chapter,
        _generate_campaign_chapter,
        _generate_digital_chapter,
        _generate_voting_day_chapter,
        _generate_observation_chapter,
        _generate_justice_chapter,
        _generate_recommendations,
        _generate_ai_regulation_chapter,
    )
    CHAPTERS_AVAILABLE = True
except Exception:
    CHAPTERS_AVAILABLE = False

__all__ = [
    "_generate_country_profile_section",
    "_generate_executive_summary",
    "_generate_political_context",
    "_generate_emb_chapter",
    "_generate_inclusivity_chapter",
    "_generate_campaign_chapter",
    "_generate_digital_chapter",
    "_generate_voting_day_chapter",
    "_generate_observation_chapter",
    "_generate_justice_chapter",
    "_generate_recommendations",
    "_generate_ai_regulation_chapter",
    "CHAPTERS_AVAILABLE",
]
