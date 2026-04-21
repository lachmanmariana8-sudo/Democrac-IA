"""Motor predictivo del Elite Report.

Genera 3-5 escenarios probabilísticos sobre dinámica institucional del
proceso electoral en curso. NO es pronóstico político (quién gana) —
es estimación de dinámica post-proceso (disputas, nulidad, segunda vuelta,
crisis institucional, activación de mecanismos internacionales).
"""
from agents.elite_report.predictive.engine import PredictiveEngine
from agents.elite_report.predictive.scenarios import SCENARIO_TEMPLATES

__all__ = ["PredictiveEngine", "SCENARIO_TEMPLATES"]
