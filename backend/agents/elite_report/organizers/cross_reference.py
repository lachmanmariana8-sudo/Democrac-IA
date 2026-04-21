"""
CrossReferenceBuilder — linkea findings del Hunter con artículos de la
normativa del corpus RAG.

Método híbrido:
1. Reglas deterministas: keywords por categoría de finding → artículos legales
   conocidos (mapeo tabular curado).
2. Búsqueda léxica en RAG: matchea tokens del finding con docs peruanos
   relevantes.

Resultado: lista de CrossReference con `relevance` (direct/related/contextual)
y `reasoning` en lenguaje natural.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Set

from agents.elite_report.models import CrossReference, FindingRef


# ── Mapeo curado categoría → (instrumento, artículo, reasoning template) ──
# Un finding de category X tiene cross-refs directas a estos instrumentos.
CATEGORY_TO_LAW: Dict[str, List[Dict[str, str]]] = {
    "logistics": [
        {"instrument": "Constitución Perú 1993", "article": "Art. 176",
         "reason": "La finalidad del sistema electoral de asegurar escrutinios fiel reflejo de la voluntad del elector es vulnerada ante fallas logísticas masivas."},
        {"instrument": "Constitución Perú 1993", "article": "Art. 183",
         "reason": "Atribuye a ONPE la organización operativa del proceso; incumplimientos en distribución de material comprometen esta función."},
        {"instrument": "LOE N° 26859", "article": "Art. 272",
         "reason": "Regula la instalación de mesas de sufragio a las 8:00 del día electoral con quórum mínimo; la no-instalación configura irregularidad."},
        {"instrument": "ICCPR", "article": "Art. 25(b)",
         "reason": "Derecho a votar en condiciones equitativas; fallas logísticas que impiden el sufragio vulneran esta garantía."},
        {"instrument": "CADH", "article": "Art. 23(1)(b)",
         "reason": "Derecho a votar y ser elegido; la no-instalación de mesas constituye restricción indebida."},
    ],
    "voter_suppression": [
        {"instrument": "ICCPR", "article": "Art. 25(b)",
         "reason": "La supresión del voto, aunque sea por fallas administrativas, vulnera el derecho al sufragio en condiciones equitativas."},
        {"instrument": "CADH", "article": "Art. 23",
         "reason": "Obliga al Estado a no imponer restricciones indebidas al derecho a votar."},
        {"instrument": "Constitución Perú 1993", "article": "Art. 31",
         "reason": "Establece el carácter obligatorio del voto y la nulidad de cualquier acto que lo limite."},
    ],
    "disinformation": [
        {"instrument": "ICCPR", "article": "Art. 19(2)",
         "reason": "Derecho a recibir información veraz; la desinformación sistemática durante campaña vulnera esta garantía."},
        {"instrument": "CADH", "article": "Art. 13",
         "reason": "Libertad de pensamiento y expresión con responsabilidades ulteriores por abuso (ej. fake news masivas)."},
        {"instrument": "CDI", "article": "Art. 4",
         "reason": "La transparencia y libertad de expresión son componentes fundamentales de la democracia representativa."},
    ],
    "media": [
        {"instrument": "ICCPR", "article": "Art. 19(2)",
         "reason": "Libertad de expresión y acceso a información."},
        {"instrument": "CADH", "article": "Art. 13",
         "reason": "Libertad de pensamiento y expresión — incluye libertad de prensa."},
    ],
    "campaign_violation": [
        {"instrument": "LOP N° 28094", "article": "Art. 34",
         "reason": "Obligación de transparencia financiera — sanción por omisión de reportes."},
        {"instrument": "LOP N° 28094", "article": "Art. 30",
         "reason": "Prohibiciones de financiamiento — aportes de origen ilícito."},
        {"instrument": "ICCPR", "article": "Art. 25",
         "reason": "Condiciones equitativas de campaña para todos los candidatos."},
    ],
    "fraud_allegation": [
        {"instrument": "Constitución Perú 1993", "article": "Art. 184",
         "reason": "Regula la nulidad de procesos electorales cuando votos nulos + blancos superan 2/3."},
        {"instrument": "LOE N° 26859", "article": "Art. 343",
         "reason": "Actas observadas y causales de impugnación."},
        {"instrument": "CADH", "article": "Art. 23",
         "reason": "Derecho a elecciones auténticas."},
    ],
    "ballot_tampering": [
        {"instrument": "LOE N° 26859", "article": "Art. 287",
         "reason": "Principios del escrutinio: público, en un solo acto ininterrumpido, con observación."},
        {"instrument": "LOE N° 26859", "article": "Art. 288",
         "reason": "Actas de escrutinio — requisitos de firma e integridad documental."},
        {"instrument": "ICCPR", "article": "Art. 25",
         "reason": "Elecciones auténticas con voto secreto que garantice la libre expresión de la voluntad."},
    ],
    "counting": [
        {"instrument": "Constitución Perú 1993", "article": "Art. 176",
         "reason": "Escrutinios como reflejo exacto y oportuno de la voluntad del elector."},
        {"instrument": "LOE N° 26859", "article": "Art. 287",
         "reason": "Principios del escrutinio público."},
    ],
    "digital": [
        {"instrument": "ICCPR", "article": "Art. 19(2)",
         "reason": "Acceso a internet y libertad informativa digital."},
        {"instrument": "Res. JNE 0891-2025-JNE", "article": "",
         "reason": "Rechazo del voto electrónico no presencial por ausencia de auditoría — estándar aplicable también a otros sistemas tecnológicos electorales."},
    ],
    "hate_speech": [
        {"instrument": "ICCPR", "article": "Art. 20",
         "reason": "Prohibición de apología del odio nacional, racial o religioso que constituya incitación."},
        {"instrument": "CADH", "article": "Art. 13(5)",
         "reason": "Apología del odio prohibida por ley."},
        {"instrument": "Ley 31170 Perú (2021)", "article": "",
         "reason": "Tipificación del acoso político contra mujeres en el Código Penal peruano."},
    ],
    "security": [
        {"instrument": "ICCPR", "article": "Art. 9",
         "reason": "Derecho a la seguridad personal."},
        {"instrument": "CADH", "article": "Art. 7",
         "reason": "Derecho a la libertad personal."},
    ],
    "irregular_procedure": [
        {"instrument": "LOE N° 26859", "article": "Art. 343",
         "reason": "Actas observadas por errores manifiestos o irregularidades en el escrutinio."},
        {"instrument": "LOE N° 26859", "article": "Art. 363",
         "reason": "Plazo de 3 días para impugnaciones ante el Jurado Electoral Especial."},
    ],
    "legal": [
        {"instrument": "Constitución Perú 1993", "article": "Art. 181",
         "reason": "Resoluciones del JNE en materia electoral dictadas en instancia final, definitiva y no revisable."},
        {"instrument": "Constitución Perú 1993", "article": "Art. 178",
         "reason": "Atribuciones del JNE: administra justicia electoral."},
    ],
    "accessibility": [
        {"instrument": "CADH", "article": "Art. 24",
         "reason": "Igualdad ante la ley — incluye accesibilidad para personas con discapacidad."},
        {"instrument": "Convención ONU sobre Derechos PcD", "article": "Art. 29",
         "reason": "Participación en la vida política y pública de personas con discapacidad."},
    ],
    "results": [
        {"instrument": "Constitución Perú 1993", "article": "Art. 178",
         "reason": "JNE proclama candidatos elegidos y el resultado del referéndum u otras consultas."},
        {"instrument": "LOE N° 26859", "article": "Art. 380",
         "reason": "Segunda vuelta electoral cuando ningún candidato presidencial obtiene mayoría absoluta."},
    ],
}


class CrossReferenceBuilder:
    """Construye cross-references finding ↔ normativa."""

    def __init__(self, rag_documents: List[Dict[str, Any]]):
        self.rag_documents = rag_documents
        self._index = self._build_rag_index()

    def _build_rag_index(self) -> Dict[str, List[Dict]]:
        """Pre-indexa docs del RAG por keyword para búsqueda rápida."""
        index: Dict[str, List[Dict]] = {}
        for doc in self.rag_documents:
            tags = doc.get("tags", []) or []
            text = doc.get("text", "")
            # Indexar por cada tag
            for t in tags:
                index.setdefault(t.lower(), []).append(doc)
            # Indexar por instrumento
            instr = str(doc.get("instrument", "")).lower()
            if instr:
                index.setdefault(instr, []).append(doc)
        return index

    def build_for_findings(
        self,
        findings: List[FindingRef],
        max_per_finding: int = 3,
    ) -> List[CrossReference]:
        """Para cada finding, construye hasta `max_per_finding` cross-references.

        Sólo procesa findings de severidad high o critical (no inunda con low/info).
        """
        refs: List[CrossReference] = []
        seen_keys: Set[tuple] = set()

        for f in findings:
            if (f.severity or "").lower() not in ("critical", "high"):
                continue

            added = 0
            # Regla 1: mapeo curado por categoría
            cat_mappings = CATEGORY_TO_LAW.get(f.category, [])
            for m in cat_mappings:
                if added >= max_per_finding:
                    break
                instrument = m["instrument"]
                article = m.get("article", "")
                key = (f.entry_id, instrument, article)
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                refs.append(CrossReference(
                    finding_entry_id=f.entry_id or "",
                    finding_snippet=(f.finding or "")[:200],
                    normative_instrument=instrument,
                    normative_article=article or None,
                    relevance="direct",
                    reasoning=m["reason"],
                ))
                added += 1

        return refs

    def top_articles_cited(self, cross_refs: List[CrossReference], top_n: int = 10) -> List[Dict]:
        """Ranking de artículos más citados por cross-references. Útil para
        Cap. 8 (Derechos vulnerados) y para la matriz normativa."""
        from collections import Counter
        counter: Counter = Counter()
        for r in cross_refs:
            key = f"{r.normative_instrument} {r.normative_article or ''}".strip()
            counter[key] += 1
        out = []
        for label, n in counter.most_common(top_n):
            out.append({"label": label, "count": n})
        return out
