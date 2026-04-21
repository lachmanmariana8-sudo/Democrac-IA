"""Dispatcher de visualizaciones del Elite Report.

render_svg(kind, data) → string SVG.

Delega a los renderers específicos de renderers.py. Los kinds no implementados
aún (Sprint 5b) devuelven un placeholder SVG con la info del kind.

Para los kinds ya existentes en el ReportDesigner Fase D, se reutilizan esos
renderers importándolos del módulo del ReportDesigner (no duplicamos código).
"""
from __future__ import annotations

from typing import Any, Dict

from agents.elite_report.visualizer import renderers as elite
from agents.elite_report.visualizer.palette import COLORS, FONT_SANS


# Renderers del ReportDesigner Fase D (reutilizados)
try:
    from agents.report_designer import visualizer as legacy
except ImportError:
    legacy = None


# Mapa kind → función
_ELITE_MAP = {
    "timeseries_multi":     elite.render_timeseries_multi,
    "phase_timeline":       elite.render_phase_timeline,
    "forecast_chart":       elite.render_forecast_chart,
    "scenario_probability": elite.render_scenario_probability,
    "heatmap_rights":       elite.render_heatmap_rights,
    "semaphore_institutional": elite.render_semaphore_institutional,
    "dimensions_radar":     elite.render_dimensions_radar,
    "matrix_normativa":     elite.render_matrix_normativa,
}

# Kinds del ReportDesigner que se delegan al módulo legacy
_LEGACY_KINDS = {
    "infographic_top", "timeline", "bar_horizontal", "donut",
}


def render_svg(kind: str, data: Dict[str, Any]) -> str:
    """Dispatcher principal. Retorna SVG inline o placeholder si el kind no
    está implementado aún."""
    # 1. Elite Sprint 5a
    renderer = _ELITE_MAP.get(kind)
    if renderer:
        try:
            svg = renderer(data)
            if svg:
                return svg
        except Exception as e:
            return _render_error(kind, f"{type(e).__name__}: {e}")

    # 2. Legacy del ReportDesigner (Fase D)
    if kind in _LEGACY_KINDS and legacy is not None:
        try:
            svg = legacy.render(kind, data)
            if svg:
                return svg
        except Exception as e:
            return _render_error(kind, f"legacy: {type(e).__name__}: {e}")

    # 3. Placeholder para Sprint 5b (kinds aún no implementados)
    return _render_placeholder(kind, data)


def _render_placeholder(kind: str, data: Dict[str, Any]) -> str:
    """Placeholder visualmente consistente para kinds no implementados aún."""
    title = data.get("title", kind)
    caption = data.get("caption", "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 120" '
        f'role="img" aria-label="Visualización pendiente">'
        f'<rect width="640" height="120" fill="{COLORS["bg_soft"]}" '
        f'stroke="{COLORS["border"]}" stroke-width="1" stroke-dasharray="4,4" rx="8"/>'
        f'<text x="320" y="52" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="13" font-weight="700" fill="{COLORS["text_muted"]}">'
        f'📊 {title}</text>'
        f'<text x="320" y="74" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="10" fill="{COLORS["text_dim"]}">'
        f'Visualización {kind} — implementación en Sprint 5b</text>'
        f'<text x="320" y="100" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="9" fill="{COLORS["text_dim"]}">{caption[:80]}</text>'
        f'</svg>'
    )


def _render_error(kind: str, error: str) -> str:
    """Mensaje visual de error (no rompe el informe)."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 80" '
        f'role="img" aria-label="Error en visualización">'
        f'<rect width="640" height="80" fill="#fef2f2" '
        f'stroke="{COLORS["critical"]}" stroke-width="1" rx="6"/>'
        f'<text x="320" y="34" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="11" font-weight="700" fill="{COLORS["critical"]}">'
        f'Error al renderizar {kind}</text>'
        f'<text x="320" y="56" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="9" fill="{COLORS["text_muted"]}">{error[:120]}</text>'
        f'</svg>'
    )
