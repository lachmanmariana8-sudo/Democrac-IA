"""
RAGLoader — carga corpus constitucionalista filtrado por país.

Usa el LEGAL_CORPUS existente de backend/rag/corpus.py. Filtra por tags
relevantes al país (ej. 'peru' para Perú) para devolver documentos
normativos que alimentarán:
- Cap. 2 (Marco jurídico)
- Cap. 3 (Sistema electoral)
- Cap. 8 (Derechos vulnerados)
- CrossReference (matcheo hallazgo ↔ norma)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


# Mapeo de country_code a tags peruanos del corpus (extensible a otros países)
COUNTRY_TAGS = {
    "PER": {
        "peru", "constitucion", "LOE", "LOP", "JNE", "ONPE", "RENIEC",
        "derechos_politicos", "sistema_electoral", "partidos",
        "financiamiento", "paridad", "jurisprudencia", "democracia_interna",
        "sufragio", "cedula", "escrutinio", "impugnaciones",
        "silencio_electoral", "voto_electronico", "autonomia", "EMB",
        "institucional", "registro", "CADH", "CIDH", "CDI", "ICCPR",
        "estandares_internacionales",
    },
}


class RAGLoader:
    """Carga documentos del corpus RAG relevantes al país."""

    def load(self, country_code: str) -> List[Dict[str, Any]]:
        """
        Retorna lista de documentos {id, title, instrument, category, tags, text}
        filtrados por relevancia al país.

        Un documento se incluye si:
        - Su instrument contiene el código o 'PERU' / país.
        - O si tiene ≥ 2 tags en COUNTRY_TAGS[cc].
        - O si es de categoría universal (ICCPR, CADH, CDI aplicable a todo país).
        """
        cc = country_code.upper()
        target_tags = COUNTRY_TAGS.get(cc, set())

        try:
            from rag.corpus import LEGAL_CORPUS
        except ImportError:
            return []

        relevant: List[Dict[str, Any]] = []
        for doc in LEGAL_CORPUS:
            instrument = str(doc.get("instrument", "")).upper()
            category = doc.get("category", "")
            tags = set(doc.get("tags", []))

            # Criterio 1: instrument contiene el código país o 'PERU'
            if cc in instrument or (cc == "PER" and "PERU" in instrument):
                relevant.append(doc)
                continue

            # Criterio 2: ≥ 2 tags en el target
            if target_tags and len(tags & target_tags) >= 2:
                relevant.append(doc)
                continue

            # Criterio 3: instrumentos universales aplicables a todos los países
            if category in ("international_framework", "electoral_rights",
                            "international_standards"):
                relevant.append(doc)
                continue
            if instrument in ("ICCPR", "CADH", "CDI", "ACHR", "ACDC",
                              "AFRICAN_CHARTER", "OSCE_COPENHAGEN"):
                relevant.append(doc)
                continue

        return relevant
