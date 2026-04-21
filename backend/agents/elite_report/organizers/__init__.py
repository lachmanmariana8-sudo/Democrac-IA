"""
Organizers del Elite Report — agrupan y cruzan evidencia.

- PhaseOrganizer: agrupa findings por las 9 fases del ciclo electoral
- CrossReference: linkea findings con artículos de la normativa (RAG)
"""
from agents.elite_report.organizers.phase_organizer import PhaseOrganizer
from agents.elite_report.organizers.cross_reference import CrossReferenceBuilder

__all__ = ["PhaseOrganizer", "CrossReferenceBuilder"]
