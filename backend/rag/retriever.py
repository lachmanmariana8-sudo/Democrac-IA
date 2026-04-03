"""
DEMOCRAC.IA / PEIRS — RAG Retriever
Funciones de consulta al corpus legal para enriquecer análisis del agente legal.

Dos modos:
  1. ChromaDB (semántico): si chromadb + sentence-transformers están instalados
  2. Keyword fallback (léxico): siempre disponible, sin dependencias externas
     Búsqueda TF-IDF simplificada sobre LEGAL_CORPUS — suficiente para producción.
"""

from __future__ import annotations
import re
from collections import Counter
from typing import List, Dict, Optional
from .indexer import RAG_AVAILABLE, get_collection


# ── Keyword Retriever (fallback sin ChromaDB) ─────────────────────────────────

def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-záéíóúüñ]{3,}", text.lower())


def _keyword_query(query_text: str, n_results: int = 3, category_filter: Optional[List[str]] = None) -> List[Dict]:
    """
    Búsqueda léxica sobre LEGAL_CORPUS.
    Retorna los N documentos con mayor overlap de términos con la query.
    Siempre disponible — sin ChromaDB, sin embeddings.
    """
    from .corpus import LEGAL_CORPUS

    q_tokens = Counter(_tokenize(query_text))
    if not q_tokens:
        return []

    scores = []
    for doc in LEGAL_CORPUS:
        if category_filter and doc.get("category") not in category_filter:
            continue
        doc_text = f"{doc.get('title', '')} {doc.get('text', '')} {' '.join(doc.get('tags', []))}"
        d_tokens  = Counter(_tokenize(doc_text))
        # Overlap normalizado por longitud de query
        overlap = sum(min(q_tokens[t], d_tokens[t]) for t in q_tokens if t in d_tokens)
        score   = overlap / (sum(q_tokens.values()) + 1)
        if score > 0:
            scores.append((score, doc))

    scores.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, doc in scores[:n_results]:
        excerpt = doc.get("text", "")[:600]
        results.append({
            "title":      doc.get("title", ""),
            "instrument": doc.get("instrument", ""),
            "category":   doc.get("category", ""),
            "relevance":  round(min(score * 4, 1.0), 3),  # escalar a 0-1
            "excerpt":    excerpt + "…" if len(doc.get("text", "")) > 600 else excerpt,
        })
    return results


def _query(query_text: str, n_results: int = 3, where_filter: Optional[dict] = None) -> List[Dict]:
    """
    Consulta el corpus legal y retorna los fragmentos más relevantes.
    Modo 1 (ChromaDB semántico): si RAG_AVAILABLE=True
    Modo 2 (keyword fallback): siempre disponible como fallback
    """
    # Extraer filtro de categorías del where_filter de ChromaDB si lo hay
    category_filter = None
    if where_filter:
        cat_filter = where_filter.get("category", {})
        if isinstance(cat_filter, dict) and "$in" in cat_filter:
            category_filter = cat_filter["$in"]

    # Modo 1: ChromaDB semántico
    if RAG_AVAILABLE:
        collection = get_collection()
        if collection is not None:
            try:
                kwargs = {"query_texts": [query_text], "n_results": min(n_results, collection.count())}
                if where_filter:
                    kwargs["where"] = where_filter
                results   = collection.query(**kwargs)
                docs      = results.get("documents", [[]])[0]
                metas     = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]
                output = []
                for doc, meta, dist in zip(docs, metas, distances):
                    relevance = round(1 - dist, 3)
                    if relevance < 0.25:
                        continue
                    output.append({
                        "title":      meta.get("title", ""),
                        "instrument": meta.get("instrument", ""),
                        "category":   meta.get("category", ""),
                        "relevance":  relevance,
                        "excerpt":    doc[:600] + "…" if len(doc) > 600 else doc,
                    })
                if output:
                    return output
            except Exception as exc:
                print(f"[RAG] Error ChromaDB, usando keyword fallback: {exc}")

    # Modo 2: keyword fallback (siempre disponible)
    return _keyword_query(query_text, n_results=n_results, category_filter=category_filter)


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
