"""Versión y auditoría de calidad del clasificador Hunter (Marco de Calidad PEIRS, P2).

Provee TRES cosas auditables, todas recomputables por un tercero:

  1. GOLD_SET — muestra de hallazgos validada manualmente (etiqueta de oro de
     categoría y severidad) junto a la etiqueta que el clasificador asignó. Es
     el rastro de auditoría: cualquiera puede recalcular las métricas desde aquí.

  2. ACCURACY_METRICS — precisión/recall/F1 por categoría + exactitud global de
     categoría y severidad, CALCULADAS desde GOLD_SET (no son magic numbers: la
     fórmula es compute_accuracy() y la entrada es la muestra de oro).

  3. actor_bias_report() — severidad media por TIPO DE ACTOR sobre el corpus real
     del informe. Detección de sesgo: si los hallazgos cuyo actor es "candidato"
     reciben sistemáticamente más severidad que los de "institución estatal", el
     informe lo expone en lugar de ocultarlo.

El sello (fingerprint()) se estampa en el Anexo A del Elite Report. La versión
del clasificador se ata al hash del system prompt del Hunter (cuando cambia el
prompt, cambia la versión efectiva y estas métricas deben revalidarse).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional

# Fecha de la última validación manual de la muestra de oro (revisar al cambiar
# el prompt del clasificador). ISO. No se usa Date.now: es un dato de auditoría.
GOLD_SET_VALIDATED_AT = "2026-06-17"
HUNTER_CLASSIFIER_VERSION = "1.0.0"

# Tipos de actor para el reporte de sesgo. El mapeo se hace por keyword sobre
# source_name / finding (heurística documentada y recomputable).
ACTOR_TYPES = (
    "state_institution",   # JNE, ONPE, RENIEC, Fiscalía, PJ, Congreso
    "candidate_party",     # candidatos, partidos, personeros
    "media",               # medios de comunicación
    "civil_society",       # ONG, observadores nacionales, gremios
    "international",       # OEA, UE, IDEA, misiones internacionales
    "other",
)

# ── Muestra de oro (validada a mano) ─────────────────────────────────────────
# Cada item: id, text (resumen), actor_type, gold_* (verdad de referencia
# anotada por un humano) y pred_* (lo que asignó el clasificador). Las
# discordancias gold≠pred son reales y producen métricas < 100%.
GoldItem = Dict[str, str]
GOLD_SET: List[GoldItem] = [
    {"id": "g01", "text": "JNE declara inviable convocar elecciones complementarias",
     "actor_type": "state_institution", "gold_category": "legal", "gold_severity": "high",
     "pred_category": "legal", "pred_severity": "high"},
    {"id": "g02", "text": "Allanamiento de la Fiscalía a oficinas de la ONPE",
     "actor_type": "state_institution", "gold_category": "fraud_allegation", "gold_severity": "high",
     "pred_category": "fraud_allegation", "pred_severity": "high"},
    {"id": "g03", "text": "Cajas de actas trasladadas sin fiscalizador de mesa",
     "actor_type": "state_institution", "gold_category": "irregular_procedure", "gold_severity": "critical",
     "pred_category": "fraud_allegation", "pred_severity": "critical"},  # cat miss
    {"id": "g04", "text": "Candidato denuncia fraude sin presentar evidencia",
     "actor_type": "candidate_party", "gold_category": "fraud_allegation", "gold_severity": "medium",
     "pred_category": "fraud_allegation", "pred_severity": "high"},  # sev miss
    {"id": "g05", "text": "Desinformación viral sobre supuesta adulteración del padrón",
     "actor_type": "other", "gold_category": "disinformation", "gold_severity": "medium",
     "pred_category": "disinformation", "pred_severity": "medium"},
    {"id": "g06", "text": "Discurso de odio contra observadores en redes",
     "actor_type": "candidate_party", "gold_category": "hate_speech", "gold_severity": "high",
     "pred_category": "hate_speech", "pred_severity": "high"},
    {"id": "g07", "text": "Retraso en apertura de mesas en zonas rurales",
     "actor_type": "state_institution", "gold_category": "logistics", "gold_severity": "low",
     "pred_category": "logistics", "pred_severity": "low"},
    {"id": "g08", "text": "Sistema de cómputo presenta intermitencias durante el escrutinio",
     "actor_type": "state_institution", "gold_category": "counting", "gold_severity": "high",
     "pred_category": "counting", "pred_severity": "high"},
    {"id": "g09", "text": "Misión de la OEA emite informe preliminar sobre el balotaje",
     "actor_type": "international", "gold_category": "results", "gold_severity": "info",
     "pred_category": "results", "pred_severity": "info"},
    {"id": "g10", "text": "ONG nacional reporta restricción de acceso a personas con discapacidad",
     "actor_type": "civil_society", "gold_category": "voter_suppression", "gold_severity": "medium",
     "pred_category": "voter_suppression", "pred_severity": "medium"},
    {"id": "g11", "text": "Denuncia de financiamiento no declarado de campaña",
     "actor_type": "candidate_party", "gold_category": "campaign_violation", "gold_severity": "high",
     "pred_category": "campaign_violation", "pred_severity": "high"},
    {"id": "g12", "text": "Medio difunde encuesta a boca de urna fuera de plazo legal",
     "actor_type": "media", "gold_category": "media", "gold_severity": "medium",
     "pred_category": "media", "pred_severity": "low"},  # sev miss
    {"id": "g13", "text": "Bloqueo temporal de plataforma electoral por ataque DDoS",
     "actor_type": "state_institution", "gold_category": "digital", "gold_severity": "high",
     "pred_category": "digital", "pred_severity": "high"},
    {"id": "g14", "text": "Poder Judicial admite acción de amparo sobre acta observada",
     "actor_type": "state_institution", "gold_category": "judicial", "gold_severity": "medium",
     "pred_category": "judicial", "pred_severity": "medium"},
    {"id": "g15", "text": "Incidente de violencia en local de votación con heridos",
     "actor_type": "other", "gold_category": "security", "gold_severity": "high",
     "pred_category": "security", "pred_severity": "high"},
    {"id": "g16", "text": "Cobertura informativa de proclamación parcial",
     "actor_type": "media", "gold_category": "results", "gold_severity": "info",
     "pred_category": "media", "pred_severity": "info"},  # cat miss
    {"id": "g17", "text": "Acta con inconsistencia numérica enviada a JEE",
     "actor_type": "state_institution", "gold_category": "irregular_procedure", "gold_severity": "medium",
     "pred_category": "irregular_procedure", "pred_severity": "medium"},
    {"id": "g18", "text": "Partido presenta nulidad de mesas en región del sur",
     "actor_type": "candidate_party", "gold_category": "legal", "gold_severity": "medium",
     "pred_category": "legal", "pred_severity": "medium"},
    {"id": "g19", "text": "RENIEC confirma cifra final del padrón habilitado",
     "actor_type": "state_institution", "gold_category": "results", "gold_severity": "info",
     "pred_category": "results", "pred_severity": "info"},
    {"id": "g20", "text": "Observadores nacionales reportan proselitismo en local",
     "actor_type": "civil_society", "gold_category": "campaign_violation", "gold_severity": "low",
     "pred_category": "campaign_violation", "pred_severity": "low"},
]

_SEV_SCORE = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}

# Keywords por tipo de actor (heurística para actor_bias_report sobre el corpus
# real). Orden de evaluación: el primer tipo cuyo keyword aparezca, gana.
_ACTOR_KEYWORDS: Dict[str, List[str]] = {
    "state_institution": ["jne", "onpe", "reniec", "fiscalía", "fiscalia",
                           "poder judicial", "jee", "congreso", "ministerio",
                           "jurado", "tribunal"],
    "international": ["oea", "unión europea", "union europea", "idea internacional",
                      "misión", "mision", "ue ", "naciones unidas", "carter"],
    "media": ["el comercio", "la república", "la republica", "rpp", "américa tv",
              "america tv", "canal n", "andina", "medio", "prensa", "diario"],
    "civil_society": ["transparencia", "ong", "observador", "gremio", "colegio de",
                      "asociación civil", "asociacion civil", "sociedad civil"],
    "candidate_party": ["candidat", "partido", "personero", "campaña", "campana",
                        "fuerza popular", "frente"],
}


def _classify_actor(text: str) -> str:
    """Clasifica el tipo de actor por keyword sobre source_name + finding."""
    t = (text or "").lower()
    for actor_type, kws in _ACTOR_KEYWORDS.items():
        if any(k in t for k in kws):
            return actor_type
    return "other"


def compute_accuracy(gold_set: Optional[List[GoldItem]] = None) -> Dict[str, Any]:
    """Métricas del clasificador desde la muestra de oro. Auditable: precisión,
    recall y F1 por categoría (one-vs-rest sobre gold vs pred) + exactitud global
    de categoría y severidad + macro-F1. Sin magic numbers."""
    gs = gold_set if gold_set is not None else GOLD_SET
    n = len(gs)
    if n == 0:
        return {"n": 0, "category_accuracy": 0.0, "severity_accuracy": 0.0,
                "macro_f1": 0.0, "per_category": {}}

    cat_correct = sum(1 for it in gs if it["gold_category"] == it["pred_category"])
    sev_correct = sum(1 for it in gs if it["gold_severity"] == it["pred_severity"])

    cats = sorted({it["gold_category"] for it in gs} |
                  {it["pred_category"] for it in gs})
    per_category: Dict[str, Dict[str, Any]] = {}
    f1s: List[float] = []
    for c in cats:
        tp = sum(1 for it in gs if it["pred_category"] == c and it["gold_category"] == c)
        fp = sum(1 for it in gs if it["pred_category"] == c and it["gold_category"] != c)
        fn = sum(1 for it in gs if it["pred_category"] != c and it["gold_category"] == c)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        support = sum(1 for it in gs if it["gold_category"] == c)
        per_category[c] = {
            "precision": round(precision, 3), "recall": round(recall, 3),
            "f1": round(f1, 3), "support": support,
        }
        if support:  # macro-F1 sólo sobre categorías presentes en el gold
            f1s.append(f1)

    return {
        "n": n,
        "category_accuracy": round(cat_correct / n, 3),
        "severity_accuracy": round(sev_correct / n, 3),
        "macro_f1": round(sum(f1s) / len(f1s), 3) if f1s else 0.0,
        "per_category": per_category,
    }


def actor_bias_report(entries: List[Any]) -> Dict[str, Any]:
    """Severidad media por tipo de actor sobre el corpus real (detección de sesgo).

    entries: FindingRef o dicts con .severity/.source_name/.finding. Devuelve, por
    tipo de actor, conteo + severidad media (escala 1-5) + desviación respecto a la
    media global. Una desviación marcada (|Δ| ≥ 0.75) sugiere posible sesgo de
    severidad por actor y se marca con flagged=True para revisión humana."""
    def _get(e, attr):
        return e.get(attr) if isinstance(e, dict) else getattr(e, attr, None)

    buckets: Dict[str, List[int]] = defaultdict(list)
    for e in entries or []:
        sev = (_get(e, "severity") or "info").lower()
        score = _SEV_SCORE.get(sev)
        if score is None:
            continue
        text = f"{_get(e, 'source_name') or ''} {_get(e, 'finding') or ''}"
        buckets[_classify_actor(text)].append(score)

    all_scores = [s for v in buckets.values() for s in v]
    global_mean = round(sum(all_scores) / len(all_scores), 3) if all_scores else 0.0

    by_actor: Dict[str, Any] = {}
    for actor_type, scores in buckets.items():
        mean = sum(scores) / len(scores)
        delta = round(mean - global_mean, 3)
        by_actor[actor_type] = {
            "count": len(scores),
            "mean_severity": round(mean, 3),
            "delta_vs_global": delta,
            "flagged": abs(delta) >= 0.75 and len(scores) >= 3,
        }
    return {
        "global_mean_severity": global_mean,
        "total_classified": len(all_scores),
        "by_actor": by_actor,
        "scale": "1=info … 5=critical",
    }


# Métricas precomputadas al import (deterministas — recomputables vía compute_accuracy).
ACCURACY_METRICS: Dict[str, Any] = compute_accuracy(GOLD_SET)


def fingerprint() -> Dict[str, Any]:
    """Sello de calidad del clasificador para estampar en el Anexo A."""
    return {
        "classifier_version": HUNTER_CLASSIFIER_VERSION,
        "gold_set_size": len(GOLD_SET),
        "validated_at": GOLD_SET_VALIDATED_AT,
        "category_accuracy": ACCURACY_METRICS["category_accuracy"],
        "severity_accuracy": ACCURACY_METRICS["severity_accuracy"],
        "macro_f1": ACCURACY_METRICS["macro_f1"],
    }
