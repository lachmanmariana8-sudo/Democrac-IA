"""
Enriquecimiento de la observación del balotaje peruano con evidencia del Hunter.

Función pura, sin I/O, sin estado. Toma el dict estático PERU_RUNOFF_2026 y la
lista de entries del observation_store, y devuelve una COPIA PROFUNDA en la que:

  1. Los 3 ejes OSINT (hate_speech, osint_narratives, electoral_violence) quedan
     poblados con los hallazgos del Hunter que correspondan por categoría.
  2. El audit_status de esos 3 ejes se recalcula objetivamente — NO por OK humano.

NO muta los inputs. NO importa de app.py (evita import circular).

Regla de escalación (operacionaliza el comentario de peru_data.py:444-448
"escala objetivamente por documento oficial o cruce de 2 fuentes primarias
independientes"). Toda constante está nombrada y documentada — sin magic numbers:

  CONFIRMED            si hay ≥1 entry verified=True (documento oficial / OONI
                       primaria verificada)  O  ≥3 fuentes primarias independientes.
  VERIFIED_SECONDARY   si hay ≥2 fuentes primarias independientes.
  PENDIENTE_VERIFICACION  en cualquier otro caso (incluye 0 hallazgos: estado
                       honesto "monitoreado, sin hallazgos corroborados").

"Fuente primaria" = entry con credibility en PRIMARY_CREDIBILITY.
"Independiente"   = valor distinto de hunter_source (p.ej. "ooni", "rss", feed).
"""

import copy

# ── Constantes auditables (la "fórmula"; sin magic numbers) ───────────────────

# ≥2 fuentes primarias independientes elevan el eje a VERIFIED_SECONDARY.
# Literal de peru_data.py:446 ("cruce de 2 fuentes primarias independientes").
MIN_INDEPENDENT_PRIMARY = 2

# ≥3 fuentes primarias independientes elevan a CONFIRMED: un escalón por encima
# del umbral secundario, decisión del owner (doc oficial ó ≥3 primarias).
CONFIRM_INDEPENDENT_PRIMARY = 3

# Tier de credibility que cuenta como "fuente primaria" a efectos de escalación.
PRIMARY_CREDIBILITY = frozenset({"high"})

# Valores posibles de audit_status, en orden de menor a mayor corroboración.
AUDIT_PENDING = "PENDIENTE_VERIFICACION"
AUDIT_SECONDARY = "VERIFIED_SECONDARY"
AUDIT_CONFIRMED = "CONFIRMED"

# Mapping categoría Hunter → eje OSINT destino. Un entry aterriza en a lo sumo un
# eje (primera coincidencia en este orden de prioridad). Categorías ausentes aquí
# (logistics, legal, media, counting, results, campaign_violation, accessibility,
# irregular_procedure, other) se ignoran: siguen en observation_store para otros
# consumidores pero no inflan los contadores de los ejes.
HUNTER_CATEGORY_TO_AXIS = {
    # Eje: discurso de odio + intimidación (⚠) — array "incidents"
    "hate_speech": "hate_speech_and_intimidation_incidents",
    "voter_intimidation": "hate_speech_and_intimidation_incidents",
    # Eje: OSINT · integridad informativa (🌐) — array "narratives"
    "disinformation": "osint_information_integrity_monitor",
    "fraud_allegation": "osint_information_integrity_monitor",
    "digital": "osint_information_integrity_monitor",
    "media_restriction": "osint_information_integrity_monitor",
    # Eje: violencia política y seguridad (🚨) — array "incidents"
    "security": "electoral_violence_incidents",
    "gender_violence": "electoral_violence_incidents",
    "voter_suppression": "electoral_violence_incidents",
    "ballot_tampering": "electoral_violence_incidents",
}

# Nombre del array que cada eje OSINT usa para sus items (ver schemas en
# peru_data.py:470 / :536 / :544).
_AXIS_ITEM_KEY = {
    "hate_speech_and_intimidation_incidents": "incidents",
    "osint_information_integrity_monitor": "narratives",
    "electoral_violence_incidents": "incidents",
}


def _source_identity(entry):
    """Identidad de fuente para el conteo de independencia. hunter_source no es
    una URL (es 'ooni', 'rss', nombre de feed), así que su valor ES la identidad.
    Cae a source_org si hunter_source viene vacío."""
    return (entry.get("hunter_source") or entry.get("source_org") or "").strip()


def _verification_level(entry):
    return "OONI_PRIMARY" if entry.get("verified") is True else "HUNTER_UNVERIFIED"


def _merge_item(entry):
    """Convierte un entry del observation_store en un item de eje, conservando
    trazabilidad completa al observation_store vía hunter_entry_id."""
    return {
        "date": entry.get("timestamp"),
        # Alias para que cualquier consumidor de los schemas documentados encuentre
        # el resumen tanto como content_summary (hate_speech) como narrative_summary
        # (osint). incident_type para el eje de violencia.
        "content_summary": entry.get("finding", ""),
        "narrative_summary": entry.get("finding", ""),
        "incident_type": entry.get("category"),
        "classification": entry.get("category"),
        "location_district": entry.get("location") or None,
        "severity": entry.get("severity"),
        "credibility": entry.get("credibility"),
        "verified": entry.get("verified", False),
        "verification_level": _verification_level(entry),
        "source_url": entry.get("evidence_ref") or None,
        "sources": [s for s in [_source_identity(entry)] if s],
        # Trazabilidad de vuelta al observation_store.
        "hunter_entry_id": entry.get("entry_id"),
    }


def compute_axis_audit_status(items):
    """Calcula audit_status objetivamente desde los items fusionados de un eje.

    No depende de OK humano: solo de verified=True (doc oficial/OONI) y del número
    de fuentes primarias independientes (credibility high, hunter_source distinto).
    """
    if not items:
        return AUDIT_PENDING

    has_official = any(it.get("verified") is True for it in items)

    independent_primary_sources = set()
    for it in items:
        if it.get("credibility") in PRIMARY_CREDIBILITY:
            for src in it.get("sources", []):
                if src:
                    independent_primary_sources.add(src)
    independent_primary = len(independent_primary_sources)

    if has_official or independent_primary >= CONFIRM_INDEPENDENT_PRIMARY:
        return AUDIT_CONFIRMED
    if independent_primary >= MIN_INDEPENDENT_PRIMARY:
        return AUDIT_SECONDARY
    return AUDIT_PENDING


def enrich_runoff_observation(runoff, entries, *, now=None):
    """Devuelve una copia profunda de `runoff` con los 3 ejes OSINT poblados
    desde `entries` (observation_store) y su audit_status recalculado.

    No muta `runoff` ni `entries`. Los 6 ejes institucionales + 2 de conducta de
    campaña pasan tal cual (escalan solo con docs oficiales cargados a mano).

    `now` se acepta por compatibilidad de firma; la lógica no depende del reloj.
    """
    enriched = copy.deepcopy(runoff)
    observation = enriched.get("runoff_phase_observation")
    if not isinstance(observation, dict):
        return enriched

    # Acumular items por eje según el mapping de categorías.
    items_by_axis = {axis: [] for axis in _AXIS_ITEM_KEY}
    for entry in entries or []:
        axis = HUNTER_CATEGORY_TO_AXIS.get(entry.get("category"))
        if axis is None:
            continue
        items_by_axis[axis].append(_merge_item(entry))

    # Poblar solo los 3 ejes OSINT; recalcular su audit_status.
    for axis, item_key in _AXIS_ITEM_KEY.items():
        block = observation.get(axis)
        if not isinstance(block, dict):
            continue
        merged = items_by_axis[axis]
        existing = block.get(item_key) or []
        block[item_key] = list(existing) + merged
        block["audit_status"] = compute_axis_audit_status(block[item_key])

    return enriched
