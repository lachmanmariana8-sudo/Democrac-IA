"""
DEMOCRAC.IA / PEIRS — RAG Retriever
Funciones de consulta al corpus legal para enriquecer análisis del agente legal.
"""

from __future__ import annotations
from typing import List, Dict, Optional
from .indexer import RAG_AVAILABLE, get_collection


def _query(query_text: str, n_results: int = 3, where_filter: Optional[dict] = None) -> List[Dict]:
    """
    Consulta el corpus legal y retorna los fragmentos más relevantes.
    Retorna lista vacía si RAG no disponible (fallback gracioso).
    """
    if not RAG_AVAILABLE:
        return []

    collection = get_collection()
    if collection is None:
        return []

    try:
        kwargs = {"query_texts": [query_text], "n_results": min(n_results, collection.count())}
        if where_filter:
            kwargs["where"] = where_filter

        results = collection.query(**kwargs)

        docs      = results.get("documents", [[]])[0]
        metas     = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        output = []
        for doc, meta, dist in zip(docs, metas, distances):
            # Convertir distancia coseno a score de relevancia (1 - dist = similaridad)
            relevance = round(1 - dist, 3)
            if relevance < 0.25:   # Umbral mínimo de relevancia
                continue
            output.append({
                "title":      meta.get("title", ""),
                "instrument": meta.get("instrument", ""),
                "category":   meta.get("category", ""),
                "relevance":  relevance,
                "excerpt":    doc[:600] + "…" if len(doc) > 600 else doc,
            })
        return output

    except Exception as exc:
        print(f"[RAG] Error en consulta: {exc}")
        return []


def query_legal_context(
    risk_description: str,
    country: str = "",
    n_results: int = 4,
) -> List[Dict]:
    """
    Recupera provisiones legales relevantes para un contexto de riesgo electoral.

    Args:
        risk_description: descripción del riesgo o violación (ej. "intimidación de votantes")
        country: nombre del país para añadir contexto
        n_results: número de resultados a retornar

    Returns:
        Lista de {title, instrument, category, relevance, excerpt}
    """
    query = f"electoral rights violations {risk_description}"
    if country:
        query += f" {country}"
    return _query(query, n_results=n_results)


def query_fraud_context(
    fraud_type: str = "",
    phase: str = "",
    n_results: int = 3,
) -> List[Dict]:
    """
    Recupera estándares de análisis de fraude electoral.

    Args:
        fraud_type: tipo de alegación (ej. "actas alteradas", "compra de votos")
        phase: fase electoral en que ocurrió
        n_results: resultados a retornar
    """
    query = f"electoral fraud allegations {fraud_type} {phase} credibility evidence investigation"
    return _query(
        query,
        n_results=n_results,
        where_filter={"category": {"$in": ["fraud_allegations", "electoral_rights", "electoral_standards"]}},
    )


def query_hate_speech_context(
    target_group: str = "",
    platform: str = "",
    n_results: int = 3,
) -> List[Dict]:
    """
    Recupera estándares sobre discurso de odio en contextos electorales.

    Args:
        target_group: grupo objetivo del discurso (ej. "candidatas mujeres", "indígenas")
        platform: plataforma donde ocurrió (ej. "TikTok", "WhatsApp")
        n_results: resultados a retornar
    """
    query = f"hate speech electoral {target_group} {platform} discrimination incitement political violence"
    return _query(
        query,
        n_results=n_results,
        where_filter={"category": {"$in": ["hate_speech", "gender_rights", "freedom_of_expression"]}},
    )


def format_rag_context_for_llm(results: List[Dict], header: str = "JURISPRUDENCIA Y ESTÁNDARES RECUPERADOS") -> str:
    """
    Formatea los resultados RAG para incluir en un prompt LLM.
    Produce citas precisas con nombre del instrumento y relevancia.
    """
    if not results:
        return ""

    lines = [f"\n--- {header} (fuentes recuperadas via RAG) ---"]
    for i, r in enumerate(results, 1):
        lines.append(
            f"\n[{i}] {r['instrument']} — {r['title']} (relevancia: {r['relevance']:.2f})\n"
            f"{r['excerpt']}"
        )
    lines.append("--- FIN DE FUENTES RAG ---\n")
    return "\n".join(lines)
