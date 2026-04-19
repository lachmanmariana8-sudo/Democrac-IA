"""
ReportDesigner — Sub-agente de composición de informes de observación electoral.

Ver d:/DemocracIA/REPORT_DESIGNER.md para blueprint arquitectónico completo.

Fase A: esqueleto funcional. Structurer, Visualizer y Composer son mocks que
devuelven datos deterministas basados en el informe v1.1 ya escrito. Permite
validar el loop end-to-end (API → frontend) antes de implementar la lógica real.
"""
from agents.report_designer.designer import ReportDesigner
from agents.report_designer.models import ReportRequest, ReportOutput

__all__ = ["ReportDesigner", "ReportRequest", "ReportOutput"]
