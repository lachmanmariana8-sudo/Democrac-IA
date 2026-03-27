"""
DEMOCRAC.IA / PEIRS — RAG Indexer
Inicializa ChromaDB con el corpus legal electoral.
Fallback gracioso si chromadb o sentence-transformers no están instalados.
"""

from __future__ import annotations
import os
import hashlib
from typing import Optional

# Importación condicional — el sistema funciona sin RAG
try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    _CHROMA_OK = True
except ImportError:
    _CHROMA_OK = False

RAG_AVAILABLE: bool = False
_chroma_client: Optional[object] = None
_collection: Optional[object] = None

# ChromaDB persiste en data/rag_index/ (gitignored, se regenera en startup)
_RAG_PERSIST_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "rag_index"
)


def init_rag() -> bool:
    """
    Inicializa ChromaDB con el corpus legal.
    Retorna True si el RAG quedó disponible, False si no (sin error).
    """
    global RAG_AVAILABLE, _chroma_client, _collection

    if not _CHROMA_OK:
        print("[RAG] ChromaDB no instalado — ejecutar: pip install chromadb sentence-transformers")
        print("[RAG] El sistema funciona sin RAG. Los análisis legales usarán solo el LLM base.")
        return False

    try:
        from .corpus import LEGAL_CORPUS

        os.makedirs(_RAG_PERSIST_DIR, exist_ok=True)

        # Modelo de embeddings ligero: all-MiniLM-L6-v2 (~90MB, descarga automática primer uso)
        embed_fn = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2",
            device="cpu",
        )

        _chroma_client = chromadb.PersistentClient(path=_RAG_PERSIST_DIR)
        _collection = _chroma_client.get_or_create_collection(
            name="legal_corpus_v1",
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

        # Calcular hash del corpus para detectar si necesita re-indexado
        corpus_hash = hashlib.md5(
            str([(d["id"], len(d["text"])) for d in LEGAL_CORPUS]).encode()
        ).hexdigest()[:8]

        stored_meta = _collection.metadata or {}
        if stored_meta.get("corpus_hash") == corpus_hash and _collection.count() == len(LEGAL_CORPUS):
            print(f"[RAG] Índice existente cargado: {_collection.count()} documentos legales.")
            RAG_AVAILABLE = True
            return True

        # Re-indexar corpus
        print(f"[RAG] Indexando {len(LEGAL_CORPUS)} documentos legales en ChromaDB...")
        _collection = _chroma_client.get_or_create_collection(
            name="legal_corpus_v1",
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine", "corpus_hash": corpus_hash},
        )

        # Upsert por lotes
        batch_ids, batch_docs, batch_metas = [], [], []
        for doc in LEGAL_CORPUS:
            batch_ids.append(doc["id"])
            batch_docs.append(f"{doc['title']}\n\n{doc['text']}")
            batch_metas.append({
                "instrument": doc.get("instrument", ""),
                "category":   doc.get("category", ""),
                "tags":       ",".join(doc.get("tags", [])),
                "title":      doc.get("title", ""),
            })

        _collection.upsert(ids=batch_ids, documents=batch_docs, metadatas=batch_metas)
        print(f"[RAG] Indexados {len(LEGAL_CORPUS)} documentos. Corpus hash: {corpus_hash}")
        RAG_AVAILABLE = True
        return True

    except Exception as exc:
        print(f"[RAG] Error al inicializar: {exc}")
        print("[RAG] El sistema continúa sin RAG.")
        RAG_AVAILABLE = False
        return False


def get_collection():
    """Retorna la colección ChromaDB o None si RAG no disponible."""
    return _collection
