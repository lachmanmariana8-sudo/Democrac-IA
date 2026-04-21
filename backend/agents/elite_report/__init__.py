"""
PEIRS Elite Report — Sub-agente de composición de informes de observación
electoral de nivel institucional internacional.

Ver d:/DemocracIA/ELITE_REPORT.md para blueprint completo (v1.1 aprobado).

Estado de implementación:
- Sprint 1 ✅ Blueprint
- Sprint 2 🟡 En curso — Loaders + models
- Sprint 3-6 ⏳ Pendientes
"""
from agents.elite_report.models import (
    EliteReportRequest,
    EliteReportOutput,
    MissionMetadata,
    EliteChapter,
    PhaseEvidence,
    CrossReference,
    HistoricalSeries,
    HistoricalDatapoint,
    ForecastScenario,
    ForecastPayload,
    CitationEntry,
    EvidenceBundle,
    FindingRef,
    VizSpec,
)
from agents.elite_report.elite_report import PEIRSEliteReport

__all__ = [
    "EliteReportRequest",
    "EliteReportOutput",
    "MissionMetadata",
    "EliteChapter",
    "PhaseEvidence",
    "CrossReference",
    "HistoricalSeries",
    "HistoricalDatapoint",
    "ForecastScenario",
    "ForecastPayload",
    "CitationEntry",
    "EvidenceBundle",
    "FindingRef",
    "VizSpec",
    "PEIRSEliteReport",
]
