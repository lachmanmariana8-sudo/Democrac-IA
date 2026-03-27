"""
chapters/generators.py — Generadores de capítulos del informe VIP para DEMOCRAC.IA (PEIRS)

Extrae de app.py todas las funciones _generate_* y _llm_generate.
Durante la migración estas funciones son wrappers que delegan en las
implementaciones de app.py para evitar duplicación y mantener
la funcionalidad intacta.

MIGRADO desde app.py — funciones _generate_* (líneas ~2244–4065)
  _generate_country_profile_section  → línea 2244
  _generate_executive_summary        → línea 2366
  _generate_political_context        → línea 2473
  _generate_emb_chapter              → línea 2711
  _generate_inclusivity_chapter      → línea 2824
  _generate_campaign_chapter         → línea 2955
  _generate_digital_chapter          → línea 3105
  _generate_voting_day_chapter       → línea 3440
  _generate_observation_chapter      → línea 3650
  _generate_justice_chapter          → línea 3838
  _generate_ai_regulation_chapter    → línea 3894
  _generate_recommendations          → línea 4037
  _llm_generate                      → línea 1908
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from agents.pipeline import PEIRSState


# ─────────────────────────────────────────────────────────────────────────────
# Importación lazy desde app.py (evita circularidad en el arranque)
# ─────────────────────────────────────────────────────────────────────────────

def _get_app_generators():
    """Importa las funciones generadoras originales desde app.py."""
    try:
        from app import (  # type: ignore
            _generate_country_profile_section as _cp,
            _generate_executive_summary as _es,
            _generate_political_context as _pc,
            _generate_emb_chapter as _emb,
            _generate_inclusivity_chapter as _inc,
            _generate_campaign_chapter as _camp,
            _generate_digital_chapter as _dig,
            _generate_voting_day_chapter as _vd,
            _generate_observation_chapter as _obs,
            _generate_justice_chapter as _just,
            _generate_ai_regulation_chapter as _ai,
            _generate_recommendations as _rec,
        )
        return _cp, _es, _pc, _emb, _inc, _camp, _dig, _vd, _obs, _just, _ai, _rec
    except ImportError as e:
        raise ImportError(
            f"[chapters/generators] No se pudo importar generadores desde app.py: {e}"
        )


def _get_llm_generate():
    """Importa el helper LLM desde app.py."""
    try:
        from app import _llm_generate  # type: ignore
        return _llm_generate
    except ImportError as e:
        raise ImportError(
            f"[chapters/generators] No se pudo importar _llm_generate desde app.py: {e}"
        )


# ── LLM Helper ─────────────────────────────────────────────────────────────────

def _llm_generate(prompt_system: str, prompt_user: str, fallback_fn, *args, **kwargs) -> str:
    """
    Helper para generación de texto con LLM (Claude via LangChain).
    Si el LLM no está disponible o falla, usa el fallback.

    Delega en `_llm_generate` de app.py durante la migración.
    """
    fn = _get_llm_generate()
    return fn(prompt_system, prompt_user, fallback_fn, *args, **kwargs)


# ── Cap. 0: Perfil del País ─────────────────────────────────────────────────────

def _generate_country_profile_section(state: "PEIRSState", country_code: str = "") -> str:
    """
    Genera Sección 0 — Perfil del País, Datos Socioeconómicos y Padrón Electoral.

    Para PER usa datos detallados de PERU_COUNTRY_PROFILE.
    Para otros países genera una sección genérica con datos disponibles.

    Delega en `_generate_country_profile_section` de app.py durante la migración.
    """
    _cp, _, _, _, _, _, _, _, _, _, _, _ = _get_app_generators()
    return _cp(state, country_code)


# ── Cap. 1: Resumen Ejecutivo ───────────────────────────────────────────────────

def _generate_executive_summary(state: "PEIRSState") -> str:
    """
    Genera Cap. 1 — Resumen Ejecutivo & Dashboard de Riesgo.

    Incluye tabla de indicadores clave (FH, V-Dem, EMB, PEI)
    y dictamen técnico del Electoral Dictamen Agent.

    Delega en `_generate_executive_summary` de app.py durante la migración.
    """
    _, _es, _, _, _, _, _, _, _, _, _, _ = _get_app_generators()
    return _es(state)


# ── Cap. 2: Contexto Político ───────────────────────────────────────────────────

def _generate_political_context(context: dict, country_code: str = "") -> str:
    """
    Genera Cap. 2 — Contexto Político y Marco Legal.

    Analiza marco legal electoral, libertades civiles y,
    para PER, incluye fuerzas políticas, crisis democrática 2019-2026
    y crimen organizado.

    Delega en `_generate_political_context` de app.py durante la migración.
    """
    _, _, _pc, _, _, _, _, _, _, _, _, _ = _get_app_generators()
    return _pc(context, country_code)


# ── Cap. 3: EMB ────────────────────────────────────────────────────────────────

def _generate_emb_chapter(context: dict, country_code: str = "") -> str:
    """
    Genera Cap. 3 — Administración Electoral (EMB).

    Evalúa independencia del EMB, padrón electoral y observación internacional.
    Para PER incluye voto exterior, logística y cadena de custodia.

    Delega en `_generate_emb_chapter` de app.py durante la migración.
    """
    _, _, _, _emb, _, _, _, _, _, _, _, _ = _get_app_generators()
    return _emb(context, country_code)


# ── Cap. 4: Inclusividad ────────────────────────────────────────────────────────

def _generate_inclusivity_chapter(context: dict, country_code: str = "") -> str:
    """
    Genera Cap. 4 — Inclusividad y Derechos Humanos.

    Evalúa sufragio universal, libertad de asociación y condiciones para
    grupos vulnerables. Para PER incluye paridad de género, VPG y
    participación indígena.

    Delega en `_generate_inclusivity_chapter` de app.py durante la migración.
    """
    _, _, _, _, _inc, _, _, _, _, _, _, _ = _get_app_generators()
    return _inc(context, country_code)


# ── Cap. 5: Campaña y Financiamiento ────────────────────────────────────────────

def _generate_campaign_chapter(political: dict, context: dict = None) -> str:
    """
    Genera Cap. 5 — Campaña, Redes de Poder y Financiamiento.

    Analiza sesgo mediático (PEI + RSF), transparencia del financiamiento
    de campaña (PEI) y red de poder político-empresarial.

    Delega en `_generate_campaign_chapter` de app.py durante la migración.
    """
    _, _, _, _, _, _camp, _, _, _, _, _, _ = _get_app_generators()
    return _camp(political, context)


# ── Cap. 6: Ecosistema Digital ───────────────────────────────────────────────────

def _generate_digital_chapter(political: dict, context: dict = None, country_code: str = "") -> str:
    """
    Genera Cap. 6 — Ecosistema de Información y Monitoreo Digital.

    Combina datos V-Dem (censura, acoso, dominancia RRSS), RSF (libertad de prensa),
    OONI (censura en tiempo real) y FH. Para PER incluye amenazas digitales específicas.

    Delega en `_generate_digital_chapter` de app.py durante la migración.
    """
    _, _, _, _, _, _, _dig, _, _, _, _, _ = _get_app_generators()
    return _dig(political, context, country_code)


# ── Cap. 7: Día de Votación ──────────────────────────────────────────────────────

def _generate_voting_day_chapter(voting_day_data: dict, state: "PEIRSState") -> str:
    """
    Genera Cap. 7 — Desarrollo del Día de Votación.

    Prioridad 1: protocolo de observación activo → delega en _generate_observation_chapter.
    Prioridad 2: datos cargados via /api/analyze/voting-day.
    Default: placeholder de espera.

    Delega en `_generate_voting_day_chapter` de app.py durante la migración.
    """
    _, _, _, _, _, _, _, _vd, _, _, _, _ = _get_app_generators()
    return _vd(voting_day_data, state)


# ── Cap. 7 (alternativo): Observación Electoral ──────────────────────────────────

def _generate_observation_chapter(session: dict, state: "PEIRSState") -> str:
    """
    Genera Cap. 7 cuando hay un protocolo de observación activo.
    Cubre las 3 fases: pre-jornada, jornada electoral, post-electoral.

    Incluye análisis de patrones (Agent 5), fraude/discurso de odio (Agent 7)
    y derechos potencialmente vulnerados.

    Delega en `_generate_observation_chapter` de app.py durante la migración.
    """
    _, _, _, _, _, _, _, _, _obs, _, _, _ = _get_app_generators()
    return _obs(session, state)


# ── Cap. 8: Justicia Electoral ────────────────────────────────────────────────────

def _generate_justice_chapter(legal: dict) -> str:
    """
    Genera Cap. 8 — Justicia Electoral y Resolución de Disputas.

    Presenta la tabla de violaciones al derecho internacional detectadas
    (ICCPR, CADH, CDI) con nivel de confianza de cada hallazgo.

    Delega en `_generate_justice_chapter` de app.py durante la migración.
    """
    _, _, _, _, _, _, _, _, _, _just, _, _ = _get_app_generators()
    return _just(legal)


# ── Cap. 10: IA Electoral (solo Perú) ────────────────────────────────────────────

def _generate_ai_regulation_chapter(state: "PEIRSState") -> str:
    """
    Genera Cap. 10 — IA Electoral: usos, riesgos regulatorios y normas de comunicación.

    Específico para Perú 2026. Cubre usos de IA por actor electoral,
    marco normativo, estándares internacionales y recomendaciones urgentes.

    Delega en `_generate_ai_regulation_chapter` de app.py durante la migración.
    """
    _, _, _, _, _, _, _, _, _, _, _ai, _ = _get_app_generators()
    return _ai(state)


# ── Cap. 9: Recomendaciones ───────────────────────────────────────────────────────

def _generate_recommendations(state: "PEIRSState") -> str:
    """
    Genera Cap. 9 — Matriz de Recomendaciones VIP.

    Proyección, impacto para inversores y analistas, e índice predictivo
    final basados en el nivel de riesgo calculado por el pipeline.

    Delega en `_generate_recommendations` de app.py durante la migración.
    """
    _, _, _, _, _, _, _, _, _, _, _, _rec = _get_app_generators()
    return _rec(state)


__all__ = [
    "_llm_generate",
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
    "_generate_ai_regulation_chapter",
    "_generate_recommendations",
]
