"""
ReportDesigner — Visualizer (Fase D).

Genera SVG reales para cada VizSpec. Sin dependencias pesadas (no usamos
matplotlib para evitar instalar paquetes en Railway). SVG artesanal con
templates simples → livianos, determinísticos, embebibles en HTML/PDF.

Tipos soportados:
- infographic_top: grid de KPI cards
- timeline: serie temporal apilada por severidad
- bar_horizontal: ranking de barras
- donut: distribución por severidad
- kpi_card: card individual

Cada función recibe VizSpec.data y retorna string SVG.
"""
from __future__ import annotations

import html
from typing import Dict, List, Any


COLORS = {
    "critical": "#d32f2f",
    "high": "#f97316",
    "medium": "#fbc02d",
    "moderate": "#fbc02d",
    "low": "#388e3c",
    "info": "#1976d2",
    "accent": "#00796b",
    "text": "#1a1a1a",
    "text_muted": "#64748b",
    "text_dim": "#94a3b8",
    "bg": "#ffffff",
    "border": "#cbd5e1",
}


def render_infographic_top(data: Dict[str, Any]) -> str:
    """Grid 4-columna de KPI cards. Ancho 640, alto 160."""
    kpis = data.get("kpis", [])[:4]
    if not kpis:
        return ""
    W, H = 640, 160
    card_w = (W - 30) / len(kpis) - 8
    card_h = H - 20

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="KPIs">']
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{COLORS["bg"]}" />')
    x = 10
    for kpi in kpis:
        color = kpi.get("color", COLORS["accent"])
        value = str(kpi.get("value", ""))
        label = html.escape(str(kpi.get("label", "")))
        svg.append(f'<rect x="{x}" y="10" width="{card_w}" height="{card_h}" rx="8" '
                   f'fill="{COLORS["bg"]}" stroke="{color}" stroke-width="2" />')
        svg.append(f'<text x="{x + card_w/2}" y="80" text-anchor="middle" '
                   f'font-family="DM Mono, Courier, monospace" font-size="36" '
                   f'font-weight="800" fill="{color}">{html.escape(value)}</text>')
        svg.append(f'<text x="{x + card_w/2}" y="115" text-anchor="middle" '
                   f'font-family="Helvetica, sans-serif" font-size="10" '
                   f'font-weight="700" fill="{COLORS["text_muted"]}" '
                   f'letter-spacing="1.5">{label.upper()[:28]}</text>')
        x += card_w + 8
    svg.append('</svg>')
    return "".join(svg)


def render_timeline(data: Dict[str, Any]) -> str:
    """Área apilada de hallazgos por día y severidad. Ancho 640, alto 220."""
    days = data.get("days", [])
    if not days:
        return '<div style="padding:20px;color:#94a3b8;">Sin datos temporales.</div>'

    W, H = 640, 220
    margin_left, margin_right, margin_top, margin_bottom = 50, 20, 20, 40
    plot_w = W - margin_left - margin_right
    plot_h = H - margin_top - margin_bottom

    # Totales por día para escala
    severities = ["critical", "high", "medium", "low", "info"]
    totals = []
    for d in days:
        counts = d.get("counts", {})
        totals.append(sum(counts.get(s, 0) + counts.get("moderate" if s == "medium" else s, 0) for s in severities))
    max_total = max(totals) if totals else 1
    if max_total == 0:
        max_total = 1

    n_days = len(days)
    x_step = plot_w / max(n_days - 1, 1) if n_days > 1 else plot_w

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Timeline">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}" />')

    # Grid horizontal
    for i in range(5):
        y = margin_top + plot_h * i / 4
        v = int(max_total * (1 - i / 4))
        svg.append(f'<line x1="{margin_left}" y1="{y}" x2="{W - margin_right}" y2="{y}" '
                   f'stroke="{COLORS["border"]}" stroke-width="0.5" stroke-dasharray="2,3" />')
        svg.append(f'<text x="{margin_left - 5}" y="{y + 3}" text-anchor="end" '
                   f'font-family="DM Mono, monospace" font-size="9" '
                   f'fill="{COLORS["text_dim"]}">{v}</text>')

    # Barras apiladas por día
    bar_w = min(plot_w / max(n_days, 1) * 0.75, 40)
    for i, d in enumerate(days):
        cx = margin_left + (i * x_step if n_days > 1 else plot_w / 2)
        counts = d.get("counts", {})
        # Normalizar moderate
        if "moderate" in counts:
            counts["medium"] = counts.get("medium", 0) + counts["moderate"]
        cumulative = 0
        for sev in severities:
            n = counts.get(sev, 0)
            if n == 0:
                continue
            bar_h = plot_h * n / max_total
            y = margin_top + plot_h - cumulative - bar_h
            svg.append(f'<rect x="{cx - bar_w/2}" y="{y}" width="{bar_w}" height="{bar_h}" '
                       f'fill="{COLORS[sev]}" stroke="{COLORS["bg"]}" stroke-width="0.5" '
                       f'opacity="0.9" />')
            cumulative += bar_h
        # Label día
        day = d.get("day", "")
        if day:
            day_label = day[5:]  # MM-DD
            svg.append(f'<text x="{cx}" y="{H - margin_bottom + 16}" text-anchor="middle" '
                       f'font-family="DM Mono, monospace" font-size="9" '
                       f'fill="{COLORS["text_muted"]}">{day_label}</text>')

    # Leyenda
    legend_x = margin_left
    legend_y = H - 10
    for sev in severities:
        svg.append(f'<rect x="{legend_x}" y="{legend_y - 8}" width="10" height="10" '
                   f'fill="{COLORS[sev]}" />')
        svg.append(f'<text x="{legend_x + 14}" y="{legend_y}" font-family="Helvetica, sans-serif" '
                   f'font-size="9" fill="{COLORS["text_muted"]}">{sev}</text>')
        legend_x += 90

    svg.append('</svg>')
    return "".join(svg)


def render_bar_horizontal(data: Dict[str, Any]) -> str:
    """Barras horizontales para rankings. Ancho 640, alto dinámico."""
    bars = data.get("bars", [])
    if not bars:
        return ""
    max_val = max((b.get("value", 0) for b in bars), default=1) or 1
    row_h = 30
    margin_left, margin_right = 120, 40
    W = 640
    H = 20 + row_h * len(bars) + 10

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Ranking">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}" />')
    plot_w = W - margin_left - margin_right
    for i, b in enumerate(bars):
        label = html.escape(str(b.get("label", ""))[:20])
        val = b.get("value", 0)
        y = 20 + i * row_h
        bar_w = plot_w * val / max_val
        svg.append(f'<text x="{margin_left - 6}" y="{y + 18}" text-anchor="end" '
                   f'font-family="DM Mono, monospace" font-size="11" '
                   f'fill="{COLORS["text"]}">{label}</text>')
        svg.append(f'<rect x="{margin_left}" y="{y + 6}" width="{bar_w}" height="18" rx="3" '
                   f'fill="{COLORS["accent"]}" opacity="0.8" />')
        svg.append(f'<text x="{margin_left + bar_w + 6}" y="{y + 19}" '
                   f'font-family="DM Mono, monospace" font-size="11" font-weight="700" '
                   f'fill="{COLORS["text"]}">{val}</text>')
    svg.append('</svg>')
    return "".join(svg)


def render_donut(data: Dict[str, Any]) -> str:
    """Distribución por severidad en donut. Ancho 300, alto 300."""
    segments = data.get("segments", [])
    if not segments:
        return ""
    import math
    W = H = 300
    cx, cy = W/2, H/2
    r_outer, r_inner = 110, 65
    total = sum(s.get("value", 0) for s in segments) or 1

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Donut">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}" />')
    start_angle = -math.pi / 2
    for seg in segments:
        val = seg.get("value", 0)
        if val <= 0:
            continue
        end_angle = start_angle + 2 * math.pi * val / total
        large_arc = 1 if (end_angle - start_angle) > math.pi else 0
        x1 = cx + r_outer * math.cos(start_angle); y1 = cy + r_outer * math.sin(start_angle)
        x2 = cx + r_outer * math.cos(end_angle); y2 = cy + r_outer * math.sin(end_angle)
        x3 = cx + r_inner * math.cos(end_angle); y3 = cy + r_inner * math.sin(end_angle)
        x4 = cx + r_inner * math.cos(start_angle); y4 = cy + r_inner * math.sin(start_angle)
        color = seg.get("color", COLORS["accent"])
        d = (f"M {x1:.1f} {y1:.1f} A {r_outer} {r_outer} 0 {large_arc} 1 {x2:.1f} {y2:.1f} "
             f"L {x3:.1f} {y3:.1f} A {r_inner} {r_inner} 0 {large_arc} 0 {x4:.1f} {y4:.1f} Z")
        svg.append(f'<path d="{d}" fill="{color}" opacity="0.85" />')
        start_angle = end_angle
    # Total en el centro
    svg.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" '
               f'font-family="DM Mono, monospace" font-size="30" font-weight="800" '
               f'fill="{COLORS["text"]}">{total}</text>')
    svg.append(f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" '
               f'font-family="Helvetica, sans-serif" font-size="10" letter-spacing="2" '
               f'fill="{COLORS["text_muted"]}">TOTAL</text>')
    svg.append('</svg>')
    return "".join(svg)


def render(viz_kind: str, data: Dict[str, Any]) -> str:
    """Dispatcher. Devuelve string SVG o string vacío si el tipo no está soportado."""
    renderers = {
        "infographic_top": render_infographic_top,
        "timeline": render_timeline,
        "bar_horizontal": render_bar_horizontal,
        "donut": render_donut,
    }
    fn = renderers.get(viz_kind)
    return fn(data) if fn else ""
