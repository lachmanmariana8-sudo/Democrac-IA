"""Sprint 5b — 13 renderers SVG adicionales para el Elite Report.

Estilo y tamaños alineados con renderers.py (Sprint 5a) y palette.py.
Todos reciben `data: dict` y retornan SVG inline (str). Sin matplotlib.

Renderers incluidos (mapeados al capítulo donde aparecen):

  Cap. 1   — events_timeline
  Cap. 3   — flow_chart_voting
  Cap. 3,7 — network_institutions
  Cap. 5   — hourly_timeline, map_regions_affected
  Cap. 6   — progress_chart, integrity_incidents_grid
  Cap. 7   — actor_network, judicial_timeline
  Cap. 8   — compliance_matrix
  Cap. 9   — early_warning_meter
  Cap. 11  — matrix_recommendations
  Cap. 12  — system_architecture
"""
from __future__ import annotations

import html
import math
from typing import Any, Dict, List

from agents.elite_report.visualizer.palette import (
    COLORS, SERIES_PALETTE, FONT_SANS, FONT_MONO,
)


def _esc(s: Any) -> str:
    return html.escape(str(s) if s is not None else "")


def _render_empty_state(title: str, subtitle: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 120" '
        f'role="img" aria-label="Sin datos">'
        f'<rect width="640" height="120" fill="{COLORS["bg_soft"]}" '
        f'stroke="{COLORS["border"]}" stroke-width="1" stroke-dasharray="4,4" rx="8"/>'
        f'<text x="320" y="54" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="12" font-weight="700" fill="{COLORS["text_muted"]}">'
        f'⊘ {_esc(title)}</text>'
        f'<text x="320" y="78" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="10" fill="{COLORS["text_dim"]}">{_esc(subtitle[:110])}</text>'
        f'</svg>'
    )


def _severity_color(sev: str) -> str:
    return {
        "critical": COLORS["critical"],
        "high":     COLORS["high"],
        "medium":   COLORS["medium"],
        "low":      COLORS["low"],
        "info":     COLORS["info"],
    }.get(sev, COLORS["text_muted"])


# ═══════════════════════════════════════════════════════════════════════
# 1. events_timeline — eventos críticos con marcadores (Cap. 1)
# ═══════════════════════════════════════════════════════════════════════
def render_events_timeline(data: Dict[str, Any]) -> str:
    """Data:
        {
          "events": [
            {"date": "2026-04-12", "label": "Jornada electoral",
             "severity": "info"},
            {"date": "2026-04-14", "label": "JNE: elecciones complementarias inviables",
             "severity": "high"},
            ...
          ],
          "date_range": {"start": "2026-04-01", "end": "2026-04-30"}  (opcional)
        }
    """
    events = data.get("events", [])
    if not events:
        return _render_empty_state("Timeline de eventos vacío")

    events = events[:14]
    W, H = 680, 240
    ml, mr, mt, mb = 40, 40, 30, 60
    pw = W - ml - mr

    # Eje temporal: ordinal por índice (no fechas reales) para simplicidad
    n = len(events)
    if n == 1:
        positions = [ml + pw / 2]
    else:
        positions = [ml + pw * i / (n - 1) for i in range(n)]

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Timeline de eventos críticos">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    # Línea base
    base_y = mt + 60
    svg.append(f'<line x1="{ml}" y1="{base_y}" x2="{ml+pw}" y2="{base_y}" '
               f'stroke="{COLORS["border"]}" stroke-width="1.5"/>')

    for i, (ev, x) in enumerate(zip(events, positions)):
        sev = ev.get("severity", "info")
        color = _severity_color(sev)
        date = _esc(ev.get("date", ""))
        label = _esc(ev.get("label", ""))[:42]
        # Marcador
        svg.append(f'<circle cx="{x:.1f}" cy="{base_y}" r="6" '
                   f'fill="{color}" stroke="{COLORS["bg"]}" stroke-width="2"/>')
        # Fecha (arriba)
        svg.append(f'<text x="{x:.1f}" y="{base_y-14}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="8" '
                   f'fill="{COLORS["text_muted"]}">{date}</text>')
        # Label (debajo, alternando vertical para evitar choque)
        ly = base_y + 22 + (24 if i % 2 == 1 else 0)
        svg.append(f'<line x1="{x:.1f}" y1="{base_y+8}" x2="{x:.1f}" y2="{ly-12}" '
                   f'stroke="{color}" stroke-width="0.8" opacity="0.5"/>')
        svg.append(f'<text x="{x:.1f}" y="{ly}" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="9" font-weight="600" '
                   f'fill="{COLORS["text"]}">{label}</text>')

    # Leyenda
    legend_y = H - 16
    legend_items = [("critical", "Crítico"), ("high", "Alto"),
                    ("medium", "Medio"), ("info", "Info")]
    lx = ml
    for sev, lbl in legend_items:
        svg.append(f'<circle cx="{lx+5}" cy="{legend_y-3}" r="4" '
                   f'fill="{_severity_color(sev)}"/>')
        svg.append(f'<text x="{lx+14}" y="{legend_y}" font-family="{FONT_SANS}" '
                   f'font-size="9" fill="{COLORS["text_muted"]}">{lbl}</text>')
        lx += 70

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 2. flow_chart_voting — cadena padrón → proclamación (Cap. 3)
# ═══════════════════════════════════════════════════════════════════════
def render_flow_chart_voting(data: Dict[str, Any]) -> str:
    """Data:
        {
          "stages": [
            {"name": "Padrón", "actor": "RENIEC", "status": "ok"},
            {"name": "Mesa", "actor": "ONPE", "status": "ok"},
            {"name": "Acta", "actor": "Mesa+ODPE", "status": "warn"},
            {"name": "STAE/SCE", "actor": "ONPE", "status": "warn"},
            {"name": "Cómputo", "actor": "JEE", "status": "ok"},
            {"name": "Proclamación", "actor": "JNE", "status": "pending"},
          ]
        }
    Status: ok | warn | fail | pending
    """
    stages = data.get("stages", [])
    if not stages:
        return _render_empty_state("Cadena de voto sin etapas")

    stages = stages[:7]
    n = len(stages)
    W, H = 680, 220
    box_w = min(98, (W - 60) // n - 14)
    gap = ((W - 30) - n * box_w) / max(n - 1, 1)
    box_h = 64
    y_box = 70

    status_color = {
        "ok":      COLORS["low"],
        "warn":    COLORS["medium"],
        "fail":    COLORS["critical"],
        "pending": COLORS["text_muted"],
    }

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Cadena del voto">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    # Header
    svg.append(f'<text x="20" y="28" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">CADENA DEL VOTO</text>')

    # Boxes + arrows
    for i, st in enumerate(stages):
        x = 20 + i * (box_w + gap)
        status = st.get("status", "pending")
        color = status_color.get(status, COLORS["text_muted"])
        # Box
        svg.append(f'<rect x="{x:.1f}" y="{y_box}" width="{box_w}" height="{box_h}" '
                   f'rx="6" fill="{COLORS["bg"]}" '
                   f'stroke="{color}" stroke-width="2"/>')
        # Status dot
        svg.append(f'<circle cx="{x+box_w-12:.1f}" cy="{y_box+12}" r="4" '
                   f'fill="{color}"/>')
        # Stage name
        name = _esc(st.get("name", ""))[:14]
        svg.append(f'<text x="{x+box_w/2:.1f}" y="{y_box+30}" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="11" font-weight="700" '
                   f'fill="{COLORS["text"]}">{name}</text>')
        # Actor
        actor = _esc(st.get("actor", ""))[:18]
        svg.append(f'<text x="{x+box_w/2:.1f}" y="{y_box+48}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="8" '
                   f'fill="{COLORS["text_muted"]}">{actor}</text>')

        # Arrow al siguiente
        if i < n - 1:
            ax1 = x + box_w
            ax2 = ax1 + gap
            ay = y_box + box_h / 2
            svg.append(f'<line x1="{ax1:.1f}" y1="{ay}" x2="{ax2-6:.1f}" y2="{ay}" '
                       f'stroke="{COLORS["text_muted"]}" stroke-width="1.5"/>')
            svg.append(f'<polygon points="{ax2-6:.1f},{ay-4} {ax2:.1f},{ay} '
                       f'{ax2-6:.1f},{ay+4}" fill="{COLORS["text_muted"]}"/>')

    # Leyenda
    ly = H - 14
    items = [("ok", "OK"), ("warn", "Atención"), ("fail", "Falla"),
             ("pending", "Pendiente")]
    lx = 20
    for st, lbl in items:
        svg.append(f'<circle cx="{lx+5}" cy="{ly-3}" r="4" '
                   f'fill="{status_color[st]}"/>')
        svg.append(f'<text x="{lx+14}" y="{ly}" font-family="{FONT_SANS}" '
                   f'font-size="9" fill="{COLORS["text_muted"]}">{lbl}</text>')
        lx += 80

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 3. network_institutions — diagrama JNE/ONPE/RENIEC + relaciones (Cap. 3, 7)
# ═══════════════════════════════════════════════════════════════════════
def render_network_institutions(data: Dict[str, Any]) -> str:
    """Data:
        {
          "nodes": [
            {"id": "JNE", "label": "JNE", "role": "árbitro", "status": "ok"},
            {"id": "ONPE", "label": "ONPE", "role": "organización", "status": "warn"},
            {"id": "RENIEC", "label": "RENIEC", "role": "padrón", "status": "ok"},
          ],
          "edges": [
            {"from": "RENIEC", "to": "ONPE", "label": "padrón"},
            {"from": "ONPE", "to": "JNE", "label": "actas"},
            ...
          ]
        }
    """
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not nodes:
        return _render_empty_state("Red institucional vacía")

    W, H = 680, 380
    cx, cy = W / 2, H / 2 + 10
    R = 130

    nodes = nodes[:6]
    n = len(nodes)
    # Layout circular
    positions = {}
    for i, node in enumerate(nodes):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        positions[node["id"]] = (cx + R * math.cos(ang), cy + R * math.sin(ang))

    status_color = {
        "ok":      COLORS["low"],
        "warn":    COLORS["medium"],
        "fail":    COLORS["critical"],
        "pending": COLORS["text_muted"],
    }

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Red institucional">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    # Header
    svg.append(f'<text x="20" y="28" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">RED INSTITUCIONAL ELECTORAL</text>')

    # Edges
    for ed in edges[:12]:
        a = positions.get(ed.get("from"))
        b = positions.get(ed.get("to"))
        if not (a and b):
            continue
        svg.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                   f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{COLORS["teal"]}" stroke-width="1" '
                   f'opacity="0.45"/>')
        # Label en el medio
        lbl = _esc(ed.get("label", ""))[:14]
        if lbl:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            svg.append(f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" '
                       f'font-family="{FONT_MONO}" font-size="8" '
                       f'fill="{COLORS["text_muted"]}">{lbl}</text>')

    # Nodes
    for node in nodes:
        x, y = positions[node["id"]]
        color = status_color.get(node.get("status", "ok"), COLORS["teal"])
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="38" '
                   f'fill="{COLORS["bg"]}" stroke="{color}" stroke-width="2.5"/>')
        svg.append(f'<text x="{x:.1f}" y="{y-2:.1f}" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="13" font-weight="700" '
                   f'fill="{COLORS["text"]}">{_esc(node.get("label", ""))[:8]}</text>')
        role = _esc(node.get("role", ""))[:14]
        svg.append(f'<text x="{x:.1f}" y="{y+13:.1f}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="8" '
                   f'fill="{COLORS["text_muted"]}">{role}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 4. hourly_timeline — eventos hora por hora del día electoral (Cap. 5)
# ═══════════════════════════════════════════════════════════════════════
def render_hourly_timeline(data: Dict[str, Any]) -> str:
    """Data:
        {
          "events": [
            {"hour": "08:00", "count": 12, "severity": "low"},
            {"hour": "09:00", "count": 24, "severity": "medium"},
            ...
          ],
          "start_hour": 8,  (default)
          "end_hour": 18    (default)
        }
    """
    events = data.get("events", [])
    if not events:
        return _render_empty_state("Sin eventos horarios registrados")

    start = data.get("start_hour", 8)
    end = data.get("end_hour", 18)
    hours = list(range(start, end + 1))

    # Mapa hora → evento
    by_hour: Dict[int, Dict[str, Any]] = {}
    for ev in events:
        h_str = str(ev.get("hour", "")).split(":")[0]
        try:
            h = int(h_str)
            by_hour[h] = ev
        except (ValueError, TypeError):
            continue

    W, H = 680, 220
    ml, mr, mt, mb = 40, 30, 30, 50
    pw, ph = W - ml - mr, H - mt - mb
    n_hours = len(hours)
    bar_w = pw / n_hours - 6

    max_count = max((e.get("count", 0) for e in events), default=1) or 1

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Timeline horario jornada electoral">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="22" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">JORNADA — EVENTOS POR HORA</text>')

    # Grid horizontal
    for i in range(5):
        y = mt + ph * i / 4
        svg.append(f'<line x1="{ml}" y1="{y}" x2="{ml+pw}" y2="{y}" '
                   f'stroke="{COLORS["border_dim"]}" stroke-width="0.5"/>')
        if i < 4:
            v = max_count - max_count * i / 4
            svg.append(f'<text x="{ml-6}" y="{y+3}" text-anchor="end" '
                       f'font-family="{FONT_MONO}" font-size="8" '
                       f'fill="{COLORS["text_muted"]}">{int(v)}</text>')

    # Bars
    for i, h in enumerate(hours):
        ev = by_hour.get(h)
        x = ml + i * (pw / n_hours) + 3
        # Hour label
        svg.append(f'<text x="{x+bar_w/2:.1f}" y="{mt+ph+18}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="9" '
                   f'fill="{COLORS["text_muted"]}">{h:02d}:00</text>')
        if not ev:
            continue
        count = ev.get("count", 0)
        sev = ev.get("severity", "info")
        bar_h = ph * count / max_count if max_count else 0
        color = _severity_color(sev)
        svg.append(f'<rect x="{x:.1f}" y="{mt+ph-bar_h:.1f}" '
                   f'width="{bar_w:.1f}" height="{bar_h:.1f}" '
                   f'fill="{color}" rx="2"/>')
        if count > 0:
            svg.append(f'<text x="{x+bar_w/2:.1f}" y="{mt+ph-bar_h-4:.1f}" '
                       f'text-anchor="middle" font-family="{FONT_MONO}" '
                       f'font-size="8" font-weight="700" '
                       f'fill="{COLORS["text"]}">{count}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 5. map_regions_affected — grilla regional con intensidad (Cap. 5)
# ═══════════════════════════════════════════════════════════════════════
def render_map_regions_affected(data: Dict[str, Any]) -> str:
    """Data:
        {
          "regions": [
            {"name": "Lima", "intensity": "high", "incidents": 47},
            {"name": "Callao", "intensity": "medium", "incidents": 18},
            ...
          ]
        }
    Renderizado como grilla rectangular (no mapa geográfico) ordenada por intensidad.
    """
    regions = data.get("regions", [])
    if not regions:
        return _render_empty_state("Sin datos regionales")

    regions = regions[:25]
    intensity_color = {
        "critical": COLORS["critical"],
        "high":     COLORS["high"],
        "medium":   COLORS["medium"],
        "low":      COLORS["low"],
        "none":     COLORS["bg_soft"],
    }

    W = 640
    cols = 5
    rows = math.ceil(len(regions) / cols)
    cell_w = (W - 40) / cols
    cell_h = 70
    H = 50 + rows * cell_h + 30

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Regiones afectadas">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="28" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">REGIONES AFECTADAS — INTENSIDAD POR INCIDENTES</text>')

    for idx, reg in enumerate(regions):
        r = idx // cols
        c = idx % cols
        x = 20 + c * cell_w
        y = 50 + r * cell_h
        intens = reg.get("intensity", "low")
        color = intensity_color.get(intens, COLORS["bg_soft"])
        # Cell
        svg.append(f'<rect x="{x:.1f}" y="{y}" width="{cell_w-6:.1f}" height="{cell_h-6}" '
                   f'rx="4" fill="{color}" opacity="0.18" '
                   f'stroke="{color}" stroke-width="1.5"/>')
        name = _esc(reg.get("name", ""))[:14]
        svg.append(f'<text x="{x+(cell_w-6)/2:.1f}" y="{y+22}" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="11" font-weight="700" '
                   f'fill="{COLORS["text"]}">{name}</text>')
        incs = reg.get("incidents", 0)
        svg.append(f'<text x="{x+(cell_w-6)/2:.1f}" y="{y+42}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="14" font-weight="700" '
                   f'fill="{color}">{incs}</text>')
        svg.append(f'<text x="{x+(cell_w-6)/2:.1f}" y="{y+56}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="7" '
                   f'fill="{COLORS["text_muted"]}">incidentes</text>')

    # Leyenda
    ly = H - 14
    legend = [("critical", "Crítica"), ("high", "Alta"),
              ("medium", "Media"), ("low", "Baja")]
    lx = 20
    for k, lbl in legend:
        svg.append(f'<rect x="{lx}" y="{ly-9}" width="12" height="10" '
                   f'fill="{intensity_color[k]}" opacity="0.4" '
                   f'stroke="{intensity_color[k]}" stroke-width="1"/>')
        svg.append(f'<text x="{lx+18}" y="{ly}" font-family="{FONT_SANS}" '
                   f'font-size="9" fill="{COLORS["text_muted"]}">{lbl}</text>')
        lx += 80

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 6. progress_chart — % actas procesadas vs tiempo (Cap. 6)
# ═══════════════════════════════════════════════════════════════════════
def render_progress_chart(data: Dict[str, Any]) -> str:
    """Data:
        {
          "points": [
            {"t": "21:00", "pct": 8.2},
            {"t": "00:00", "pct": 32.5},
            ...
          ],
          "target_pct": 100,
          "current_pct": 95.1  (último valor reportado)
        }
    """
    points = data.get("points", [])
    if not points:
        return _render_empty_state("Sin datos de progreso de actas")

    points = points[:48]
    W, H = 680, 240
    ml, mr, mt, mb = 50, 40, 30, 50
    pw, ph = W - ml - mr, H - mt - mb

    n = len(points)
    coords: List[tuple] = []
    for i, p in enumerate(points):
        x = ml + (pw * i / (n - 1)) if n > 1 else ml + pw / 2
        y = mt + ph * (1 - min(p.get("pct", 0), 100) / 100)
        coords.append((x, y))

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Progreso de actas procesadas">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="22" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">PROGRESO DE ACTAS PROCESADAS</text>')

    # Grid Y
    for i in range(5):
        y = mt + ph * i / 4
        pct = 100 - 25 * i
        svg.append(f'<line x1="{ml}" y1="{y}" x2="{ml+pw}" y2="{y}" '
                   f'stroke="{COLORS["border_dim"]}" stroke-width="0.5"/>')
        svg.append(f'<text x="{ml-6}" y="{y+3}" text-anchor="end" '
                   f'font-family="{FONT_MONO}" font-size="9" '
                   f'fill="{COLORS["text_muted"]}">{pct}%</text>')

    # Eje X — labels alternos
    step = max(1, n // 6)
    for i in range(0, n, step):
        x, _ = coords[i]
        label = _esc(points[i].get("t", ""))
        svg.append(f'<text x="{x:.1f}" y="{mt+ph+16}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="8" '
                   f'fill="{COLORS["text_muted"]}">{label}</text>')

    # Línea + área bajo curva
    if len(coords) > 1:
        path_line = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
        # Área
        path_area = (path_line +
                     f" L {coords[-1][0]:.1f},{mt+ph} "
                     f"L {coords[0][0]:.1f},{mt+ph} Z")
        svg.append(f'<path d="{path_area}" fill="{COLORS["teal"]}" opacity="0.15"/>')
        svg.append(f'<path d="{path_line}" fill="none" '
                   f'stroke="{COLORS["teal"]}" stroke-width="2"/>')

    # Punto final con valor
    if coords:
        x, y = coords[-1]
        current = data.get("current_pct", points[-1].get("pct", 0))
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" '
                   f'fill="{COLORS["teal"]}" stroke="{COLORS["bg"]}" stroke-width="2"/>')
        svg.append(f'<text x="{x:.1f}" y="{y-12:.1f}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="11" font-weight="700" '
                   f'fill="{COLORS["teal_dark"]}">{current}%</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 7. integrity_incidents_grid — grilla 2D de incidentes (Cap. 6)
# ═══════════════════════════════════════════════════════════════════════
def render_integrity_incidents_grid(data: Dict[str, Any]) -> str:
    """Data:
        {
          "rows": ["Lima", "Callao", "Arequipa", ...],   (regiones)
          "cols": ["Logística", "Conteo", "STAE", "Disturbios", "Reclamos"],
          "values": [[3, 1, 0, 0, 2], [0, 0, 1, 0, 0], ...]  (counts por celda)
        }
    """
    rows = data.get("rows", [])
    cols = data.get("cols", [])
    values = data.get("values", [])
    if not rows or not cols or not values:
        return _render_empty_state("Grilla de incidentes vacía")

    rows = rows[:14]
    cols = cols[:8]
    values = [v[:len(cols)] for v in values[:len(rows)]]

    flat = [v for row in values for v in row]
    vmax = max(flat) if flat else 1

    W = 680
    label_w = 110
    cell_w = (W - label_w - 30) / max(len(cols), 1)
    cell_h = 28
    H = 90 + len(rows) * cell_h + 20

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Grilla de incidentes">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="26" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">INCIDENTES DE INTEGRIDAD — REGIÓN × CATEGORÍA</text>')

    # Headers (cols)
    header_y = 70
    for ci, col in enumerate(cols):
        x = label_w + 15 + ci * cell_w
        svg.append(f'<text x="{x+cell_w/2:.1f}" y="{header_y}" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="9" font-weight="700" '
                   f'fill="{COLORS["text_muted"]}" '
                   f'transform="rotate(-25 {x+cell_w/2:.1f} {header_y})">{_esc(col)[:14]}</text>')

    # Rows
    for ri, row in enumerate(rows):
        y = 90 + ri * cell_h
        # Label
        svg.append(f'<text x="{label_w+8}" y="{y+cell_h/2+4:.1f}" text-anchor="end" '
                   f'font-family="{FONT_SANS}" font-size="10" '
                   f'fill="{COLORS["text"]}">{_esc(row)[:18]}</text>')
        for ci in range(len(cols)):
            x = label_w + 15 + ci * cell_w
            v = values[ri][ci] if ci < len(values[ri]) else 0
            intensity = (v / vmax) if vmax else 0
            # Background
            svg.append(f'<rect x="{x:.1f}" y="{y}" '
                       f'width="{cell_w-3:.1f}" height="{cell_h-3}" '
                       f'rx="3" fill="{COLORS["critical"]}" '
                       f'opacity="{0.05 + 0.7 * intensity:.2f}"/>')
            if v > 0:
                svg.append(f'<text x="{x+cell_w/2:.1f}" y="{y+cell_h/2+4:.1f}" '
                           f'text-anchor="middle" font-family="{FONT_MONO}" '
                           f'font-size="10" font-weight="700" '
                           f'fill="{COLORS["text"]}">{v}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 8. actor_network — red de actores con aristas labeled (Cap. 7)
# ═══════════════════════════════════════════════════════════════════════
def render_actor_network(data: Dict[str, Any]) -> str:
    """Data:
        {
          "actors": [
            {"id": "JNE", "label": "JNE", "type": "institución"},
            {"id": "FIS", "label": "Fiscalía", "type": "institución"},
            {"id": "FP", "label": "Fuerza Popular", "type": "partido"},
            ...
          ],
          "edges": [
            {"from": "FIS", "to": "ONPE", "action": "investiga", "severity": "high"},
            ...
          ]
        }
    """
    actors = data.get("actors", [])
    edges = data.get("edges", [])
    if not actors:
        return _render_empty_state("Red de actores vacía")

    actors = actors[:9]
    W, H = 680, 440
    cx, cy = W / 2, H / 2 + 10
    R = 160
    n = len(actors)
    positions = {}
    for i, a in enumerate(actors):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        positions[a["id"]] = (cx + R * math.cos(ang), cy + R * math.sin(ang))

    type_color = {
        "institución":  COLORS["teal"],
        "institucion":  COLORS["teal"],
        "partido":      COLORS["accent_purple"],
        "candidato":    COLORS["accent_pink"],
        "fiscal":       COLORS["critical"],
        "judicial":     COLORS["high"],
        "media":        COLORS["accent_blue"],
    }

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Red de actores">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="28" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">RED DE ACTORES — ACCIONES E INTERVENCIONES</text>')

    # Edges
    for ed in edges[:18]:
        a = positions.get(ed.get("from"))
        b = positions.get(ed.get("to"))
        if not (a and b):
            continue
        sev = ed.get("severity", "info")
        color = _severity_color(sev)
        svg.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                   f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{color}" stroke-width="1.2" opacity="0.55"/>')
        # Mid arrow
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        svg.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="3" fill="{color}"/>')
        action = _esc(ed.get("action", ""))[:14]
        if action:
            svg.append(f'<text x="{mx:.1f}" y="{my-7:.1f}" text-anchor="middle" '
                       f'font-family="{FONT_MONO}" font-size="8" '
                       f'fill="{COLORS["text_muted"]}">{action}</text>')

    # Nodes
    for a in actors:
        x, y = positions[a["id"]]
        atype = a.get("type", "institución")
        color = type_color.get(atype, COLORS["teal"])
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="34" '
                   f'fill="{COLORS["bg"]}" stroke="{color}" stroke-width="2.5"/>')
        svg.append(f'<text x="{x:.1f}" y="{y-2:.1f}" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="11" font-weight="700" '
                   f'fill="{COLORS["text"]}">{_esc(a.get("label", ""))[:10]}</text>')
        svg.append(f'<text x="{x:.1f}" y="{y+12:.1f}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="7" '
                   f'fill="{COLORS["text_muted"]}">{_esc(atype)[:14]}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 9. judicial_timeline — cronología judicial (Cap. 7)
# ═══════════════════════════════════════════════════════════════════════
def render_judicial_timeline(data: Dict[str, Any]) -> str:
    """Data:
        {
          "actions": [
            {"date": "2026-04-15", "actor": "Fiscalía",
             "action": "Allanamiento ONPE", "severity": "high"},
            ...
          ]
        }
    """
    actions = data.get("actions", [])
    if not actions:
        return _render_empty_state("Sin acciones judiciales registradas")

    actions = actions[:10]
    W = 680
    row_h = 56
    H = 60 + row_h * len(actions) + 20

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Cronología judicial">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="30" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">CRONOLOGÍA JUDICIAL</text>')

    # Línea vertical
    line_x = 130
    svg.append(f'<line x1="{line_x}" y1="50" x2="{line_x}" y2="{H-30}" '
               f'stroke="{COLORS["border"]}" stroke-width="2"/>')

    for i, act in enumerate(actions):
        y = 60 + i * row_h
        sev = act.get("severity", "info")
        color = _severity_color(sev)
        # Marker
        svg.append(f'<circle cx="{line_x}" cy="{y+row_h/2:.1f}" r="7" '
                   f'fill="{color}" stroke="{COLORS["bg"]}" stroke-width="2"/>')
        # Date a la izquierda
        date = _esc(act.get("date", ""))
        svg.append(f'<text x="{line_x-16}" y="{y+row_h/2-4:.1f}" text-anchor="end" '
                   f'font-family="{FONT_MONO}" font-size="9" font-weight="700" '
                   f'fill="{COLORS["text"]}">{date}</text>')
        # Actor abajo de la fecha
        actor = _esc(act.get("actor", ""))[:18]
        svg.append(f'<text x="{line_x-16}" y="{y+row_h/2+10:.1f}" text-anchor="end" '
                   f'font-family="{FONT_SANS}" font-size="9" '
                   f'fill="{COLORS["text_muted"]}">{actor}</text>')
        # Action a la derecha
        action = _esc(act.get("action", ""))[:62]
        svg.append(f'<text x="{line_x+16}" y="{y+row_h/2+4:.1f}" '
                   f'font-family="{FONT_SANS}" font-size="11" font-weight="600" '
                   f'fill="{COLORS["text"]}">{action}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 10. compliance_matrix — cumplimiento ICCPR/CADH por artículo (Cap. 8)
# ═══════════════════════════════════════════════════════════════════════
def render_compliance_matrix(data: Dict[str, Any]) -> str:
    """Data:
        {
          "rows": [
            {"article": "ICCPR Art. 25", "topic": "Derecho a votar",
             "status": "partial", "evidence_count": 7},
            ...
          ]
        }
    Status: ok | partial | breach | unknown
    """
    rows = data.get("rows", [])
    if not rows:
        return _render_empty_state("Matriz de cumplimiento vacía")

    rows = rows[:14]
    status_color = {
        "ok":      COLORS["low"],
        "partial": COLORS["medium"],
        "breach":  COLORS["critical"],
        "unknown": COLORS["text_muted"],
    }
    status_label = {
        "ok": "CUMPLE", "partial": "PARCIAL",
        "breach": "INCUMPLE", "unknown": "S/D",
    }

    W = 680
    row_h = 30
    H = 60 + row_h * len(rows) + 20

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Matriz de cumplimiento">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="26" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">MATRIZ DE CUMPLIMIENTO ICCPR / CADH</text>')

    # Header
    y_hdr = 50
    headers = [("ARTÍCULO", 16), ("TEMA", 200), ("EVIDENCIA", 470), ("ESTADO", 560)]
    for label, x in headers:
        svg.append(f'<text x="{x}" y="{y_hdr}" font-family="{FONT_SANS}" '
                   f'font-size="9" font-weight="700" letter-spacing="1.2" '
                   f'fill="{COLORS["text_muted"]}">{label}</text>')
    svg.append(f'<line x1="12" y1="{y_hdr+6}" x2="{W-12}" y2="{y_hdr+6}" '
               f'stroke="{COLORS["teal"]}" stroke-width="1.5"/>')

    for ri, r in enumerate(rows):
        y = 70 + ri * row_h + 18
        if ri % 2 == 1:
            svg.append(f'<rect x="12" y="{y-18}" width="{W-24}" height="{row_h}" '
                       f'fill="{COLORS["bg_soft"]}"/>')
        article = _esc(r.get("article", ""))[:24]
        topic = _esc(r.get("topic", ""))[:38]
        ev_count = r.get("evidence_count", 0)
        status = r.get("status", "unknown")
        color = status_color.get(status, COLORS["text_muted"])

        svg.append(f'<text x="16" y="{y}" font-family="{FONT_SANS}" font-size="10" '
                   f'font-weight="600" fill="{COLORS["text"]}">{article}</text>')
        svg.append(f'<text x="200" y="{y}" font-family="{FONT_SANS}" font-size="10" '
                   f'fill="{COLORS["text_muted"]}">{topic}</text>')
        svg.append(f'<text x="470" y="{y}" font-family="{FONT_MONO}" '
                   f'font-size="10" fill="{COLORS["text_muted"]}">{ev_count} ev.</text>')
        # Badge
        svg.append(f'<rect x="555" y="{y-13}" width="105" height="18" rx="3" '
                   f'fill="{color}" opacity="0.18" stroke="{color}" stroke-width="1"/>')
        svg.append(f'<text x="607" y="{y}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="9" font-weight="700" '
                   f'fill="{color}">{status_label.get(status, "S/D")}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 11. early_warning_meter — velocímetro de alerta (Cap. 9)
# ═══════════════════════════════════════════════════════════════════════
def render_early_warning_meter(data: Dict[str, Any]) -> str:
    """Data:
        {
          "level": "amber",     # green | amber | orange | red
          "score": 0.62,        # 0..1 (posición de la aguja)
          "label": "Riesgo elevado",
          "drivers": ["Disputa en cómputo", "Renuncia ONPE"]  (opcional)
        }
    """
    level = data.get("level", "green")
    score = max(0.0, min(1.0, float(data.get("score", 0))))
    label = data.get("label", level.upper())
    drivers = data.get("drivers", [])

    W, H = 480, 320
    cx, cy = W / 2, 200
    R_outer = 130
    R_inner = 100

    bands = [
        (0.00, 0.25, COLORS["warn_green"], "VERDE"),
        (0.25, 0.50, COLORS["warn_amber"], "ÁMBAR"),
        (0.50, 0.75, COLORS["warn_orange"], "NARANJA"),
        (0.75, 1.00, COLORS["warn_red"],   "ROJO"),
    ]

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Medidor de alerta temprana">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="{cx}" y="40" text-anchor="middle" '
               f'font-family="{FONT_SANS}" font-size="11" font-weight="700" '
               f'letter-spacing="1.5" fill="{COLORS["teal_dark"]}">'
               f'ALERTA TEMPRANA — NIVEL DE RIESGO</text>')

    # Bandas (semicírculo)
    def arc_path(a0: float, a1: float, ro: float, ri: float) -> str:
        # ángulos en radianes; 0 = derecha, π = izquierda
        x0o = cx + ro * math.cos(math.pi - math.pi * a0)
        y0o = cy - ro * math.sin(math.pi - math.pi * a0)
        x1o = cx + ro * math.cos(math.pi - math.pi * a1)
        y1o = cy - ro * math.sin(math.pi - math.pi * a1)
        x0i = cx + ri * math.cos(math.pi - math.pi * a1)
        y0i = cy - ri * math.sin(math.pi - math.pi * a1)
        x1i = cx + ri * math.cos(math.pi - math.pi * a0)
        y1i = cy - ri * math.sin(math.pi - math.pi * a0)
        return (f"M {x0o:.1f},{y0o:.1f} "
                f"A {ro},{ro} 0 0 1 {x1o:.1f},{y1o:.1f} "
                f"L {x0i:.1f},{y0i:.1f} "
                f"A {ri},{ri} 0 0 0 {x1i:.1f},{y1i:.1f} Z")

    for a0, a1, color, _lbl in bands:
        svg.append(f'<path d="{arc_path(a0, a1, R_outer, R_inner)}" '
                   f'fill="{color}" opacity="0.85"/>')

    # Aguja
    needle_angle = math.pi - math.pi * score
    nx = cx + (R_outer - 10) * math.cos(needle_angle)
    ny = cy - (R_outer - 10) * math.sin(needle_angle)
    svg.append(f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" '
               f'stroke="{COLORS["text"]}" stroke-width="3" stroke-linecap="round"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{COLORS["text"]}"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{COLORS["bg"]}"/>')

    # Score y label
    svg.append(f'<text x="{cx}" y="{cy+40}" text-anchor="middle" '
               f'font-family="{FONT_MONO}" font-size="22" font-weight="700" '
               f'fill="{COLORS["text"]}">{score:.2f}</text>')
    svg.append(f'<text x="{cx}" y="{cy+62}" text-anchor="middle" '
               f'font-family="{FONT_SANS}" font-size="11" font-weight="700" '
               f'fill="{COLORS["text"]}">{_esc(label)[:36]}</text>')

    # Drivers (1-3 líneas)
    for i, drv in enumerate(drivers[:3]):
        svg.append(f'<text x="{cx}" y="{cy+82+i*14}" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="9" '
                   f'fill="{COLORS["text_muted"]}">• {_esc(drv)[:46]}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 12. matrix_recommendations — 3×N con priority flags (Cap. 11)
# ═══════════════════════════════════════════════════════════════════════
def render_matrix_recommendations(data: Dict[str, Any]) -> str:
    """Data:
        {
          "rows": [
            {"recommendation": "Auditar STAE/SCE",
             "addressee": "ONPE", "priority": "high",
             "horizon": "corto",  # corto | medio | largo
             "feasibility": "alta"},  # alta | media | baja
            ...
          ]
        }
    """
    rows = data.get("rows", [])
    if not rows:
        return _render_empty_state("Sin recomendaciones")

    rows = rows[:14]
    pri_color = {
        "critical": COLORS["critical"],
        "high":     COLORS["high"],
        "medium":   COLORS["medium"],
        "low":      COLORS["low"],
    }
    horizon_color = {
        "corto": COLORS["critical"],
        "medio": COLORS["medium"],
        "largo": COLORS["info"],
    }

    W = 680
    row_h = 36
    H = 70 + row_h * len(rows) + 20

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Matriz de recomendaciones">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="26" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">RECOMENDACIONES — DESTINATARIO × PRIORIDAD × HORIZONTE</text>')

    # Header
    y_hdr = 56
    for x, label in [(16, "RECOMENDACIÓN"), (340, "DESTINATARIO"),
                     (470, "PRIORIDAD"), (570, "HORIZONTE")]:
        svg.append(f'<text x="{x}" y="{y_hdr}" font-family="{FONT_SANS}" '
                   f'font-size="9" font-weight="700" letter-spacing="1.2" '
                   f'fill="{COLORS["text_muted"]}">{label}</text>')
    svg.append(f'<line x1="12" y1="{y_hdr+6}" x2="{W-12}" y2="{y_hdr+6}" '
               f'stroke="{COLORS["teal"]}" stroke-width="1.5"/>')

    for ri, r in enumerate(rows):
        y = 76 + ri * row_h + 22
        if ri % 2 == 1:
            svg.append(f'<rect x="12" y="{y-22}" width="{W-24}" height="{row_h}" '
                       f'fill="{COLORS["bg_soft"]}"/>')
        rec = _esc(r.get("recommendation", ""))[:46]
        addr = _esc(r.get("addressee", ""))[:14]
        pri = r.get("priority", "medium")
        hor = r.get("horizon", "medio")
        pcolor = pri_color.get(pri, COLORS["text_muted"])
        hcolor = horizon_color.get(hor, COLORS["text_muted"])

        svg.append(f'<text x="16" y="{y}" font-family="{FONT_SANS}" font-size="10" '
                   f'font-weight="600" fill="{COLORS["text"]}">{rec}</text>')
        svg.append(f'<text x="340" y="{y}" font-family="{FONT_MONO}" font-size="9" '
                   f'fill="{COLORS["text"]}">{addr}</text>')
        svg.append(f'<rect x="465" y="{y-13}" width="80" height="18" rx="3" '
                   f'fill="{pcolor}" opacity="0.18" stroke="{pcolor}" stroke-width="1"/>')
        svg.append(f'<text x="505" y="{y}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="9" font-weight="700" '
                   f'fill="{pcolor}">{_esc(pri).upper()[:8]}</text>')
        svg.append(f'<rect x="565" y="{y-13}" width="90" height="18" rx="3" '
                   f'fill="{hcolor}" opacity="0.18" stroke="{hcolor}" stroke-width="1"/>')
        svg.append(f'<text x="610" y="{y}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="9" font-weight="700" '
                   f'fill="{hcolor}">{_esc(hor).upper()[:9]}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 13. system_architecture — STAE + SCE + SPR + flujos (Cap. 12)
# ═══════════════════════════════════════════════════════════════════════
def render_system_architecture(data: Dict[str, Any]) -> str:
    """Data:
        {
          "components": [
            {"id": "STAE", "label": "STAE",
             "subtitle": "Mesa — laptops/impresoras",
             "layer": "edge", "audited": false},
            {"id": "SCE", "label": "SCE",
             "subtitle": "Cómputo + IA dual",
             "layer": "core", "audited": false},
            {"id": "SPR", "label": "SPR",
             "subtitle": "resultadoelectoral.onpe.gob.pe",
             "layer": "publish", "audited": true},
          ],
          "flows": [
            {"from": "STAE", "to": "SCE", "label": "actas + foto"},
            {"from": "SCE", "to": "SPR", "label": "agregados"},
          ]
        }
    Layout horizontal (edge → core → publish).
    """
    comps = data.get("components", [])
    flows = data.get("flows", [])
    if not comps:
        return _render_empty_state("Diagrama de arquitectura vacío")

    comps = comps[:5]
    W, H = 680, 320
    box_w, box_h = 150, 120
    n = len(comps)
    total_box_w = n * box_w + (n - 1) * 50
    start_x = (W - total_box_w) / 2
    y_box = 90

    layer_color = {
        "edge":    COLORS["accent_blue"],
        "core":    COLORS["teal"],
        "publish": COLORS["accent_purple"],
    }

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Arquitectura del sistema electoral">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    svg.append(f'<text x="20" y="30" font-family="{FONT_SANS}" font-size="11" '
               f'font-weight="700" letter-spacing="1.5" '
               f'fill="{COLORS["teal_dark"]}">ARQUITECTURA DEL SISTEMA ELECTORAL</text>')

    positions = {}
    for i, c in enumerate(comps):
        x = start_x + i * (box_w + 50)
        positions[c["id"]] = (x + box_w / 2, y_box + box_h / 2)
        layer = c.get("layer", "core")
        color = layer_color.get(layer, COLORS["teal"])
        audited = c.get("audited", False)

        # Box
        svg.append(f'<rect x="{x:.1f}" y="{y_box}" width="{box_w}" height="{box_h}" '
                   f'rx="8" fill="{COLORS["bg"]}" '
                   f'stroke="{color}" stroke-width="2"/>')
        # Layer chip
        svg.append(f'<rect x="{x+10:.1f}" y="{y_box+10}" width="48" height="14" rx="2" '
                   f'fill="{color}" opacity="0.18"/>')
        svg.append(f'<text x="{x+34:.1f}" y="{y_box+20}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="8" font-weight="700" '
                   f'fill="{color}">{_esc(layer).upper()[:8]}</text>')
        # Audit badge
        adt_color = COLORS["low"] if audited else COLORS["critical"]
        adt_lbl = "✓ AUDIT" if audited else "✗ NO AUDIT"
        svg.append(f'<rect x="{x+box_w-72:.1f}" y="{y_box+10}" '
                   f'width="62" height="14" rx="2" '
                   f'fill="{adt_color}" opacity="0.18"/>')
        svg.append(f'<text x="{x+box_w-41:.1f}" y="{y_box+20}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="8" font-weight="700" '
                   f'fill="{adt_color}">{adt_lbl}</text>')
        # Label
        svg.append(f'<text x="{x+box_w/2:.1f}" y="{y_box+58}" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="18" font-weight="700" '
                   f'fill="{COLORS["text"]}">{_esc(c.get("label", ""))[:8]}</text>')
        # Subtitle (multi-line manual: corta a 24 chars por línea, hasta 2 líneas)
        sub = c.get("subtitle", "")
        line1 = _esc(sub[:24])
        line2 = _esc(sub[24:48]) if len(sub) > 24 else ""
        svg.append(f'<text x="{x+box_w/2:.1f}" y="{y_box+82}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="8" '
                   f'fill="{COLORS["text_muted"]}">{line1}</text>')
        if line2:
            svg.append(f'<text x="{x+box_w/2:.1f}" y="{y_box+96}" text-anchor="middle" '
                       f'font-family="{FONT_MONO}" font-size="8" '
                       f'fill="{COLORS["text_muted"]}">{line2}</text>')

    # Flows
    for fl in flows[:8]:
        a = positions.get(fl.get("from"))
        b = positions.get(fl.get("to"))
        if not (a and b):
            continue
        x1 = a[0] + box_w / 2 - 4
        x2 = b[0] - box_w / 2 + 4
        y = a[1]
        svg.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2-6:.1f}" y2="{y:.1f}" '
                   f'stroke="{COLORS["teal"]}" stroke-width="1.5"/>')
        svg.append(f'<polygon points="{x2-6:.1f},{y-5} {x2:.1f},{y:.1f} '
                   f'{x2-6:.1f},{y+5}" fill="{COLORS["teal"]}"/>')
        lbl = _esc(fl.get("label", ""))[:18]
        if lbl:
            svg.append(f'<text x="{(x1+x2)/2:.1f}" y="{y-8:.1f}" text-anchor="middle" '
                       f'font-family="{FONT_MONO}" font-size="8" '
                       f'fill="{COLORS["text_muted"]}">{lbl}</text>')

    # Caption gap auditoría
    audited_comps = [c for c in comps if c.get("audited")]
    note = (f"{len(audited_comps)}/{len(comps)} componentes con auditoría pública. "
            f"Gap estructural: SCE/STAE sin auditoría independiente.")
    svg.append(f'<text x="{W/2:.1f}" y="{H-30}" text-anchor="middle" '
               f'font-family="{FONT_SANS}" font-size="10" font-style="italic" '
               f'fill="{COLORS["text_muted"]}">{_esc(note)}</text>')

    svg.append('</svg>')
    return "".join(svg)
