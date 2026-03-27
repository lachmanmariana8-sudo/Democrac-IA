"""
DEMOCRAC.IA / PEIRS — RAG Legal Knowledge Base
Retrieval-Augmented Generation sobre corpus de derecho electoral internacional.

Diseño:
  - ChromaDB como vector store local (sin servidor, cero costo)
  - sentence-transformers/all-MiniLM-L6-v2 como modelo de embeddings (~90MB)
  - Corpus: ICCPR, CADH, CDI, jurisprudencia CIDH, manuales OSCE/ODIHR, CEDAW
  - Fallback gracioso: si chromadb no instalado, el sistema funciona sin RAG

Uso:
  from rag import query_legal_context, RAG_AVAILABLE, init_rag
"""

from .retriever import query_legal_context, query_fraud_context, query_hate_speech_context
from .indexer import init_rag, RAG_AVAILABLE

__all__ = [
    "query_legal_context",
    "query_fraud_context",
    "query_hate_speech_context",
    "init_rag",
    "RAG_AVAILABLE",
]
