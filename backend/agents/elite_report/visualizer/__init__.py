"""Visualizer elite — SVG artesanal sin matplotlib (compat Railway).

Dispatcher principal en `renderer.py`. Cada tipo de visualización tiene
su propio módulo. Paleta institucional común en `palette.py`.

21 kinds soportados (blueprint sección 10):
- Base (reutilizados del ReportDesigner): infographic_top, timeline,
  bar_horizontal, donut, kpi_card, matrix, map_mesas
- Elite (nuevos): timeseries_multi, events_timeline, matrix_normativa,
  phase_timeline, hourly_timeline, map_regions_affected, actor_network,
  judicial_timeline, heatmap_rights, compliance_matrix, forecast_chart,
  scenario_probability, early_warning_meter, semaphore_institutional,
  dimensions_radar, matrix_recommendations, system_architecture,
  network_institutions, flow_chart_voting, progress_chart,
  integrity_incidents_grid
"""
from agents.elite_report.visualizer.renderer import render_svg

__all__ = ["render_svg"]
