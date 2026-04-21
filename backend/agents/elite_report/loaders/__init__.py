"""Loaders del Elite Report — 3 subloaders + orquestador.

Cada subloader devuelve un slice de evidencia normalizada:
- hunter_loader: entries + alerts + themes del Hunter
- rag_loader: corpus constitucionalista filtrado por país
- datasets_loader: series históricas V-Dem, FH, PEI, RSF

El orquestador EliteLoader ensambla un EvidenceBundle listo para el pipeline.
"""
from agents.elite_report.loaders.hunter_loader import HunterLoader
from agents.elite_report.loaders.rag_loader import RAGLoader
from agents.elite_report.loaders.datasets_loader import DatasetsLoader
from agents.elite_report.loaders.elite_loader import EliteLoader

__all__ = ["HunterLoader", "RAGLoader", "DatasetsLoader", "EliteLoader"]
