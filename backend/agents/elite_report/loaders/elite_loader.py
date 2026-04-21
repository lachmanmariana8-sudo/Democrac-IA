"""
EliteLoader — orquestador que ensambla EvidenceBundle desde los 3 subloaders.

Ejecuta Hunter + RAG + Datasets en paralelo (cuando corresponde), normaliza a
los modelos Elite y cachea el resultado con TTL configurable.

Cache: in-memory simple keyed por (country, period_start, period_end, window).
TTL 1 hora por defecto — dentro del ciclo electoral los datos cambian rápido
pero no segundo a segundo.
"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from agents.elite_report.models import EvidenceBundle
from agents.elite_report.loaders.hunter_loader import HunterLoader
from agents.elite_report.loaders.rag_loader import RAGLoader
from agents.elite_report.loaders.datasets_loader import DatasetsLoader


DEFAULT_TTL_SECONDS = 3600  # 1 hora


class EliteLoader:
    """Ensambla EvidenceBundle con todos los vértices del triángulo."""

    def __init__(
        self,
        observation_store: Optional[Dict] = None,
        alerts_loader: Optional[Callable] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        datasets_window: int = 10,
    ):
        """
        Args:
            observation_store: dict {cc: session} del backend FastAPI.
            alerts_loader: callable(cc, limit) para tabla alerts.
            ttl_seconds: vida del cache.
            datasets_window: años de ventana histórica para datasets.
        """
        self._hunter = HunterLoader(
            observation_store=observation_store,
            alerts_loader=alerts_loader,
        )
        self._rag = RAGLoader()
        self._datasets = DatasetsLoader(years_window=datasets_window)
        self._ttl = ttl_seconds
        self._cache: Dict[str, Any] = {}  # key → (bundle, expires_at)

    async def load_all(
        self,
        country_code: str,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        force_refresh: bool = False,
    ) -> EvidenceBundle:
        """Carga todos los vértices del triángulo de evidencia.
        Cachea el resultado por TTL."""
        cc = country_code.upper()
        cache_key = f"{cc}::{period_start or ''}::{period_end or ''}"

        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached and cached["expires_at"] > time.time():
                return cached["bundle"]

        start_time = time.time()
        warnings: list[str] = []

        # Ejecutar subloaders.
        # hunter y rag son síncronos; datasets puede ser I/O. Los corremos en hilos
        # para no bloquear el event loop (aunque en Fase A son fast).
        def _run_hunter():
            try:
                return self._hunter.load(cc, period_start, period_end)
            except Exception as e:
                warnings.append(f"hunter_loader error: {type(e).__name__}: {e}")
                return [], 0, {}

        def _run_rag():
            try:
                return self._rag.load(cc)
            except Exception as e:
                warnings.append(f"rag_loader error: {type(e).__name__}: {e}")
                return []

        def _run_datasets():
            try:
                return self._datasets.load(cc)
            except Exception as e:
                warnings.append(f"datasets_loader error: {type(e).__name__}: {e}")
                return []

        hunter_future = asyncio.to_thread(_run_hunter)
        rag_future = asyncio.to_thread(_run_rag)
        datasets_future = asyncio.to_thread(_run_datasets)

        hunter_result, rag_docs, datasets_series = await asyncio.gather(
            hunter_future, rag_future, datasets_future
        )
        findings, alerts_count, hunter_stats = hunter_result

        bundle = EvidenceBundle(
            country_code=cc,
            period_start=period_start or "",
            period_end=period_end or "",
            loaded_at=datetime.now(timezone.utc).isoformat(),
            hunter_entries=findings,
            hunter_stats=hunter_stats,
            alerts_dispatched=alerts_count,
            rag_documents=rag_docs,
            historical_series=datasets_series,
            warnings=warnings,
        )

        # Cachear
        self._cache[cache_key] = {
            "bundle": bundle,
            "expires_at": time.time() + self._ttl,
        }
        # Stats operativas
        bundle.warnings.append(
            f"Load time: {time.time() - start_time:.2f}s. "
            f"Hunter findings: {len(findings)} | RAG docs: {len(rag_docs)} | "
            f"Datasets series: {len(datasets_series)} | Alerts: {alerts_count}."
        )
        return bundle

    def invalidate_cache(self, country_code: Optional[str] = None) -> int:
        """Limpia cache. Si country_code se provee, solo esa entrada."""
        if country_code is None:
            n = len(self._cache)
            self._cache.clear()
            return n
        cc = country_code.upper()
        removed = 0
        keys_to_remove = [k for k in self._cache if k.startswith(f"{cc}::")]
        for k in keys_to_remove:
            del self._cache[k]
            removed += 1
        return removed
