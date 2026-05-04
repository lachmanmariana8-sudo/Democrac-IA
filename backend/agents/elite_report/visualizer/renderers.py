"""Implementación de los 8 renderers SVG clave del Elite Report (Sprint 5a).

Todos los renderers reciben `data: dict` y retornan `str` con SVG inline.
SVG artesanal para evitar dependencias pesadas en Railway (no matplotlib).

Incluidos en Sprint 5a:
1. timeseries_multi     — series históricas superpuestas (cap. 1)
2. phase_timeline       — 9 fases × densidad de hallazgos (cap. 4)
3. forecast_chart       — escenarios probabilísticos con bandas (cap. 9)
4. scenario_probability — barras horizontales con % de cada escenario (cap. 9)
5. heatmap_rights       — derechos × categorías (cap. 8)
6. semaphore_institutional — semáforo JNE/ONPE/RENIEC/proceso (cap. 10)
7. dimensions_radar     — radar 8 dimensiones PEIRS (cap. 10)
8. matrix_normativa     — tabla normativa (cap. 2)
"""
from __future__ import annotations

import html
import math
from typing import Any, Dict, List

from agents.elite_report.visualizer.palette import (
    COLORS, SERIES_PALETTE, FONT_SANS, FONT_MONO,
    DIM_INFOGRAPHIC, DIM_TIMELINE, DIM_MATRIX, DIM_RADAR,
)
from agents.elite_report.i18n import t as _t


def _lang(data: Dict[str, Any]) -> str:
    """Lee `_language` inyectado en el data dict por _attach_visualizations.
    Cae a 'es' si no esta presente (compat con renderers que se llaman fuera
    del pipeline normal, ej. tests). Mantiene paridad con renderers_5b._lang."""
    return (data.get("_language") if isinstance(data, dict) else None) or "es"


def _esc(s: str) -> str:
    return html.escape(s or "")


def _wrap_2lines(text: str, max_chars_per_line: int) -> tuple[str, str]:
    """Quiebra `text` en hasta 2 líneas para evitar truncations crudos.
    Retorna (line1, line2) ambos HTML-escapados. Si el texto cabe en una
    línea, line2 = "". Si excede 2*max_chars_per_line, trunca con '…'.

    Estrategia: busca espacio cercano a max_chars_per_line para partir
    sin romper palabras. Si no hay espacio, parte en max_chars literal.
    """
    text = (text or "").strip()
    if not text:
        return "", ""
    if len(text) <= max_chars_per_line:
        return _esc(text), ""
    # Limitar a 2 líneas
    cap = max_chars_per_line * 2
    if len(text) > cap:
        text = text[:cap - 1].rstrip() + "…"
    # Buscar último espacio dentro de la primera línea
    cut = text.rfind(" ", 0, max_chars_per_line + 1)
    if cut <= 0:
        # No hay espacio — partir literal en max_chars
        return _esc(text[:max_chars_per_line]), _esc(text[max_chars_per_line:])
    line1 = text[:cut]
    line2 = text[cut + 1:]
    return _esc(line1), _esc(line2)


def _render_empty_state(title: str, subtitle: str = "") -> str:
    """Placeholder visual consistente cuando no hay datos para graficar.

    Evita dejar un `<figure>` vacío después del viz-title (que confunde al lector).
    """
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 120" '
        f'role="img" aria-label="Sin datos disponibles">'
        f'<rect width="640" height="120" fill="{COLORS["bg_soft"]}" '
        f'stroke="{COLORS["border"]}" stroke-width="1" stroke-dasharray="4,4" rx="8"/>'
        f'<text x="320" y="54" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="12" font-weight="700" fill="{COLORS["text_muted"]}">'
        f'⊘ {_esc(title)}</text>'
        f'<text x="320" y="78" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="10" fill="{COLORS["text_dim"]}">{_esc(subtitle[:110])}</text>'
        f'</svg>'
    )


# ═══════════════════════════════════════════════════════════════════════
# 1. timeseries_multi — series históricas superpuestas (V-Dem, FH, PEI, RSF)
# ═══════════════════════════════════════════════════════════════════════
def render_timeseries_multi(data: Dict[str, Any]) -> str:
    """Data esperada:
        {
          "series": [
            {"label": "V-Dem LibDem", "unit": "0-1", "points": [{"year": 2015, "value": 0.55}, ...]},
            ...
          ],
          "events": [{"year": 2020, "label": "Crisis 3 presidentes"}, ...]  (opcional)
        }
    """
    series = data.get("series", [])
    events = data.get("events", [])
    if not series:
        return _render_empty_state(
            "Series históricas no disponibles en el entorno de ejecución actual",
            "Los datasets V-Dem, Freedom House, PEI y RSF no pudieron cargarse. "
            "La narrativa del capítulo cita los valores disponibles.",
        )

    W, H = 680, 300
    ml, mr, mt, mb = 60, 120, 12, 56
    pw, ph = W - ml - mr, H - mt - mb

    # Rango temporal global
    all_years = [p["year"] for s in series for p in s.get("points", [])]
    if not all_years:
        return ""
    year_min, year_max = min(all_years), max(all_years)
    x_range = max(year_max - year_min, 1)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Series históricas">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')
    # (El título del gráfico lo pone la figcaption HTML — no lo duplicamos en SVG)

    # Grid eje Y (cada serie normalizada a 0-1 para comparación)
    for i in range(5):
        y = mt + ph * i / 4
        svg.append(f'<line x1="{ml}" y1="{y}" x2="{ml+pw}" y2="{y}" '
                   f'stroke="{COLORS["border_dim"]}" stroke-width="0.5"/>')

    # Eje X — años
    n_labels = min(x_range + 1, 8)
    for i in range(n_labels):
        year = int(year_min + (x_range * i / max(n_labels - 1, 1)))
        x = ml + pw * i / max(n_labels - 1, 1)
        svg.append(f'<text x="{x}" y="{mt+ph+16}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="9" '
                   f'fill="{COLORS["text_muted"]}">{year}</text>')

    # Event markers
    for ev in events:
        ey = ev.get("year")
        if ey is None or not (year_min <= ey <= year_max):
            continue
        x = ml + pw * (ey - year_min) / x_range
        svg.append(f'<line x1="{x}" y1="{mt}" x2="{x}" y2="{mt+ph}" '
                   f'stroke="{COLORS["critical"]}" stroke-width="0.5" stroke-dasharray="3,3"/>')

    # Series
    for si, s in enumerate(series):
        pts = s.get("points", [])
        if not pts:
            continue
        color = SERIES_PALETTE[si % len(SERIES_PALETTE)]
        # Normalizar al rango de esa serie
        vals = [p["value"] for p in pts]
        vmin = min(vals)
        vmax = max(vals)
        vrange = max(vmax - vmin, 0.001)

        path_d = []
        for i, p in enumerate(pts):
            x = ml + pw * (p["year"] - year_min) / x_range
            y_norm = (p["value"] - vmin) / vrange
            y = mt + ph * (1 - y_norm)
            path_d.append(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}")

        svg.append(f'<path d="{" ".join(path_d)}" fill="none" '
                   f'stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')
        # Puntos
        for p in pts:
            x = ml + pw * (p["year"] - year_min) / x_range
            y_norm = (p["value"] - vmin) / vrange
            y = mt + ph * (1 - y_norm)
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{color}"/>')

        # Leyenda (sidebar derecho) — truncamos labels para que no excedan el margen
        ly = mt + si * 22
        label_truncated = _esc(s["label"])[:16]  # 16 chars cabe en los 120px de mr
        svg.append(f'<rect x="{W-mr+8}" y="{ly+2}" width="10" height="10" fill="{color}"/>')
        svg.append(f'<text x="{W-mr+22}" y="{ly+11}" font-family="{FONT_SANS}" '
                   f'font-size="9" fill="{COLORS["text"]}">{label_truncated}</text>')
        svg.append(f'<text x="{W-mr+22}" y="{ly+22}" font-family="{FONT_MONO}" '
                   f'font-size="8" fill="{COLORS["text_dim"]}">'
                   f'{vmin:.2f}→{vmax:.2f}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 2. phase_timeline — densidad de hallazgos por las 9 fases del ciclo
# ═══════════════════════════════════════════════════════════════════════
def render_phase_timeline(data: Dict[str, Any]) -> str:
    """Data:
        {
          "phases": [
            {"phase": "preparatory", "label": "📋 Preparatorio",
             "total": 20, "critical": 0, "high": 3, "medium": 8, "low": 4, "info": 5},
            ...
          ]
        }
    """
    phases = data.get("phases", [])
    if not phases:
        return _render_empty_state(
            "Sin fases con hallazgos registrados",
            "El período no contiene hallazgos asignables a las 9 fases del ciclo electoral.",
        )

    W, H = 680, 320
    ml, mr, mt, mb = 50, 20, 16, 110
    pw, ph = W - ml - mr, H - mt - mb

    # Saltar fases con total=0: si todas las fases vacias se grafican, las
    # 2 con datos quedan ahogadas. Mantenemos el orden cronologico original
    # pero solo mostramos las que tienen al menos 1 hallazgo.
    phases = [p for p in phases if p.get("total", 0) > 0] or phases

    # Total por fase para escala
    totals = [p.get("total", 0) for p in phases]
    max_total = max(totals) if totals else 1
    if max_total == 0:
        max_total = 1

    n_phases = len(phases)
    step = pw / n_phases

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Timeline por fase electoral">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    # Grid Y
    for i in range(5):
        y = mt + ph * i / 4
        v = int(max_total * (1 - i / 4))
        svg.append(f'<line x1="{ml}" y1="{y}" x2="{ml+pw}" y2="{y}" '
                   f'stroke="{COLORS["border_dim"]}" stroke-width="0.5" stroke-dasharray="2,3"/>')
        svg.append(f'<text x="{ml-6}" y="{y+3}" text-anchor="end" '
                   f'font-family="{FONT_MONO}" font-size="9" '
                   f'fill="{COLORS["text_dim"]}">{v}</text>')

    # Barras apiladas por fase
    sev_order = ["info", "low", "medium", "high", "critical"]
    bar_w = step * 0.68
    for pi, p in enumerate(phases):
        cx = ml + step * pi + step / 2
        cumul = 0
        for sev in sev_order:
            n = p.get(sev, 0)
            if n == 0:
                continue
            bh = ph * n / max_total
            y = mt + ph - cumul - bh
            svg.append(f'<rect x="{cx-bar_w/2:.1f}" y="{y:.1f}" '
                       f'width="{bar_w:.1f}" height="{bh:.1f}" '
                       f'fill="{COLORS[sev]}" opacity="0.85"/>')
            cumul += bh

        # Label fase rotado -35° con wrap a 2 líneas si el nombre es largo
        # (ej. "Escrutinio y cómputo", "Resolución de disputas").
        label = p.get("label", p.get("phase", ""))
        label_clean = label.replace("📋", "").replace("📣", "").replace("🗣️", "").replace("🤫", "") \
                           .replace("🗳️", "").replace("🔢", "").replace("📊", "") \
                           .replace("⚖️", "").replace("✅", "").strip()
        # Total arriba (centrado, no rotado, mas legible)
        svg.append(f'<text x="{cx}" y="{mt+ph+16}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="11" font-weight="700" '
                   f'fill="{COLORS["text"]}">{p.get("total", 0)}</text>')
        # Label rotado: 2 líneas via tspan si excede 16 chars
        line1, line2 = _wrap_2lines(label_clean, 16)
        if line2:
            svg.append(f'<text x="{cx}" y="{mt+ph+32}" text-anchor="end" '
                       f'font-family="{FONT_SANS}" font-size="9" '
                       f'transform="rotate(-35 {cx} {mt+ph+32})" '
                       f'fill="{COLORS["text_muted"]}">'
                       f'<tspan x="{cx}" dy="0">{line1}</tspan>'
                       f'<tspan x="{cx}" dy="11">{line2}</tspan>'
                       f'</text>')
        else:
            svg.append(f'<text x="{cx}" y="{mt+ph+32}" text-anchor="end" '
                       f'font-family="{FONT_SANS}" font-size="9" '
                       f'transform="rotate(-35 {cx} {mt+ph+32})" '
                       f'fill="{COLORS["text_muted"]}">{line1}</text>')

    # Leyenda — etiquetas en español, mas espacio entre items, en linea
    # superior (mt-2) para no chocar con los labels rotados del eje X.
    legend_y = 12
    lang_local = _lang(data)
    legend_labels = {
        "info":     _t(lang_local, "viz.severity.info"),
        "low":      _t(lang_local, "viz.severity.low"),
        "medium":   _t(lang_local, "viz.severity.medium"),
        "high":     _t(lang_local, "viz.severity.high"),
        "critical": _t(lang_local, "viz.severity.critical"),
    }
    lx = ml
    for sev in sev_order:
        svg.append(f'<rect x="{lx}" y="{legend_y-8}" width="10" height="10" fill="{COLORS[sev]}"/>')
        svg.append(f'<text x="{lx+14}" y="{legend_y}" font-family="{FONT_SANS}" '
                   f'font-size="9" font-weight="600" '
                   f'fill="{COLORS["text"]}">{legend_labels[sev]}</text>')
        lx += 70

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 3. forecast_chart — proyección con bandas de confianza
# ═══════════════════════════════════════════════════════════════════════
def render_forecast_chart(data: Dict[str, Any]) -> str:
    """Data:
        {
          "scenarios": [
            {"label": "Disputa prolongada", "probability": 0.55,
             "ci_low": 0.40, "ci_high": 0.70},
            ...
          ],
          "warning_level": "orange"   # green|amber|orange|red
        }
    """
    scenarios = data.get("scenarios", [])
    warning_level = data.get("warning_level", "amber")
    if not scenarios:
        return _render_empty_state(
            "Motor predictivo sin escenarios activos",
            "No se activaron escenarios probabilísticos para este informe.",
        )

    warn_color = {
        "green":  COLORS["warn_green"],
        "amber":  COLORS["warn_amber"],
        "orange": COLORS["warn_orange"],
        "red":    COLORS["warn_red"],
    }.get(warning_level, COLORS["warn_amber"])

    W = 680
    row_h = 46
    H = 50 + row_h * len(scenarios) + 30

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Forecast de escenarios">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    # Badge warning level (solo)
    svg.append(f'<rect x="{W-160}" y="8" width="150" height="22" rx="4" '
               f'fill="{warn_color}"/>')
    svg.append(f'<text x="{W-85}" y="23" text-anchor="middle" '
               f'font-family="{FONT_SANS}" font-size="10" font-weight="700" '
               f'fill="white">{_t(_lang(data), "viz.alert").upper()} {warning_level.upper()}</text>')

    # Escala 0-100%
    ml, mr, mt = 240, 60, 44
    pw = W - ml - mr
    # ticks 0, 25, 50, 75, 100
    for i in range(5):
        x = ml + pw * i / 4
        svg.append(f'<line x1="{x}" y1="{mt}" x2="{x}" y2="{H-30}" '
                   f'stroke="{COLORS["border_dim"]}" stroke-width="0.5" stroke-dasharray="2,3"/>')
        svg.append(f'<text x="{x}" y="{H-12}" text-anchor="middle" '
                   f'font-family="{FONT_MONO}" font-size="9" '
                   f'fill="{COLORS["text_muted"]}">{i*25}%</text>')

    # Rows
    for si, s in enumerate(scenarios):
        y = mt + si * row_h + row_h / 2
        prob = s.get("probability", 0)
        ci_low = s.get("ci_low", max(prob - 0.1, 0))
        ci_high = s.get("ci_high", min(prob + 0.1, 1))

        # Label — truncamos para caber en los 230px de ml=240 (margen izq 10)
        label = _esc(s.get("label", ""))[:34]
        svg.append(f'<text x="{ml-10}" y="{y+4}" text-anchor="end" '
                   f'font-family="{FONT_SANS}" font-size="10" '
                   f'fill="{COLORS["text"]}">{label}</text>')

        # Banda de confianza (rectángulo tenue)
        x_low = ml + pw * ci_low
        x_high = ml + pw * ci_high
        svg.append(f'<rect x="{x_low:.1f}" y="{y-10}" '
                   f'width="{(x_high-x_low):.1f}" height="20" '
                   f'fill="{COLORS["teal"]}" opacity="0.18"/>')

        # Punto probabilidad
        x_prob = ml + pw * prob
        svg.append(f'<circle cx="{x_prob:.1f}" cy="{y}" r="6" '
                   f'fill="{COLORS["teal"]}" stroke="white" stroke-width="2"/>')

        # Probabilidad texto
        svg.append(f'<text x="{W-mr+8}" y="{y+4}" '
                   f'font-family="{FONT_MONO}" font-size="11" font-weight="700" '
                   f'fill="{COLORS["teal_dark"]}">{int(prob*100)}%</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 4. scenario_probability — variante compacta en barras horizontales
# ═══════════════════════════════════════════════════════════════════════
def render_scenario_probability(data: Dict[str, Any]) -> str:
    """Data:
        {"scenarios": [{"label": "...", "probability": 0.55}, ...]}
    """
    scenarios = data.get("scenarios", [])
    if not scenarios:
        return _render_empty_state("Sin escenarios para graficar", "")

    W = 640
    row_h = 32
    H = 12 + row_h * len(scenarios) + 20
    ml, mr = 220, 50
    pw = W - ml - mr

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Probabilidad de escenarios">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    for si, s in enumerate(scenarios):
        y = 12 + si * row_h
        prob = s.get("probability", 0)
        # ml=220 con 8px margen → 212px disponibles; truncamos a 30 chars
        label = _esc(s.get("label", ""))[:30]
        svg.append(f'<text x="{ml-8}" y="{y+18}" text-anchor="end" '
                   f'font-family="{FONT_SANS}" font-size="10" '
                   f'fill="{COLORS["text"]}">{label}</text>')
        bar_w = pw * prob
        svg.append(f'<rect x="{ml}" y="{y+6}" width="{pw}" height="16" rx="3" '
                   f'fill="{COLORS["bg_soft"]}"/>')
        svg.append(f'<rect x="{ml}" y="{y+6}" width="{bar_w:.1f}" height="16" rx="3" '
                   f'fill="{COLORS["teal"]}" opacity="0.8"/>')
        svg.append(f'<text x="{W-mr+6}" y="{y+18}" '
                   f'font-family="{FONT_MONO}" font-size="10" font-weight="700" '
                   f'fill="{COLORS["teal_dark"]}">{int(prob*100)}%</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 5. heatmap_rights — derechos × categorías (cap 8)
# ═══════════════════════════════════════════════════════════════════════
def render_heatmap_rights(data: Dict[str, Any]) -> str:
    """Data:
        {
          "rights": ["ICCPR Art. 25", "CADH Art. 23", ...],   (filas)
          "categories": ["logistics", "disinformation", ...],  (cols)
          "matrix": [[12, 0, 3, ...], [...], ...]              (conteos)
        }
    """
    rights = data.get("rights", [])
    categories = data.get("categories", [])
    matrix = data.get("matrix", [])
    if not rights or not categories or not matrix:
        return _render_empty_state(
            "Heatmap derechos × categorías no disponible",
            "El período no presenta hallazgos con cruce derechos×categoría.",
        )

    # Cap dimensiones
    rights = rights[:8]
    categories = categories[:8]
    matrix = matrix[:8]

    W = 680
    cell_w = 54
    cell_h = 36
    ml, mt = 200, 96   # sin título interno: solo dejamos margen para labels rotados
    pw = cell_w * len(categories)
    ph = cell_h * len(rights)
    H = mt + ph + 30
    # Si el ancho calculado excede W, reducir cell_w (fit-to-width)
    if ml + pw > W - 20:
        cell_w = max(30, (W - 20 - ml) // max(len(categories), 1))
        pw = cell_w * len(categories)

    # Si toda la matriz es ceros (no hay cross_references que linkeen
    # findings con la categoria + articulo), preferimos un empty state
    # explicito a un grid de celdas blancas que confunde al lector.
    flat_max = max((max(row[:len(categories)] or [0]) for row in matrix if row),
                   default=0)
    if flat_max == 0:
        return _render_empty_state(
            "Sin cruces derecho × categoría detectados en el período",
            "El motor de cross-references no asoció hallazgos del Hunter con "
            "los artículos ICCPR/CADH/CDI listados. Esto puede indicar (a) que "
            "los hallazgos del período no invocan los derechos top-6, o (b) que "
            "el mapeo categoría→derecho del CrossReferenceBuilder requiere "
            "ajuste para esta cobertura específica.",
        )
    max_val = flat_max

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Heatmap derechos por categoría">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    # Labels categorías (arriba, rotadas). Acortamos a 14 chars y subimos mt.
    for ci, cat in enumerate(categories):
        cx = ml + ci * cell_w + cell_w / 2
        # rotamos sobre el punto base del texto (extremo derecho) para que
        # los labels nunca se desborden por arriba del viewBox
        label = _esc(cat[:14])
        svg.append(f'<text x="{cx}" y="{mt-6}" text-anchor="end" '
                   f'font-family="{FONT_SANS}" font-size="9" '
                   f'fill="{COLORS["text_muted"]}" '
                   f'transform="rotate(-40 {cx} {mt-6})">{label}</text>')

    # Filas: derechos + celdas — truncar a 22 chars para caber en ml=200
    for ri, right in enumerate(rights):
        ry = mt + ri * cell_h + cell_h / 2
        svg.append(f'<text x="{ml-8}" y="{ry+4}" text-anchor="end" '
                   f'font-family="{FONT_SANS}" font-size="10" '
                   f'fill="{COLORS["text"]}">{_esc(right[:22])}</text>')

        row = matrix[ri] if ri < len(matrix) else []
        for ci, cat in enumerate(categories):
            val = row[ci] if ci < len(row) else 0
            intensity = val / max_val if max_val > 0 else 0
            # Interpolar teal desde claro a oscuro
            opacity = 0.08 + 0.85 * intensity
            x = ml + ci * cell_w
            y = mt + ri * cell_h
            svg.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" '
                       f'fill="{COLORS["teal"]}" opacity="{opacity:.2f}" '
                       f'stroke="{COLORS["bg"]}" stroke-width="1"/>')
            if val > 0:
                text_color = "white" if intensity > 0.5 else COLORS["text"]
                svg.append(f'<text x="{x+cell_w/2}" y="{y+cell_h/2+4}" '
                           f'text-anchor="middle" font-family="{FONT_MONO}" '
                           f'font-size="10" font-weight="700" fill="{text_color}">{val}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 6. semaphore_institutional — semáforo JNE/ONPE/RENIEC + proceso global
# ═══════════════════════════════════════════════════════════════════════
def render_semaphore_institutional(data: Dict[str, Any]) -> str:
    """Data:
        {
          "organs": [
            {"label": "JNE",  "status": "amber",  "note": "Denuncia penal contra ONPE"},
            {"label": "ONPE", "status": "red",    "note": "Crisis operativa"},
            {"label": "RENIEC", "status": "green", "note": "Sin incidentes"},
            {"label": "Proceso global", "status": "amber", "note": "Legítimo con observaciones"}
          ]
        }
    """
    organs = data.get("organs", [])
    if not organs:
        return _render_empty_state("Sin evaluación institucional disponible", "")

    status_color = {
        "green":  COLORS["warn_green"],
        "amber":  COLORS["warn_amber"],
        "orange": COLORS["warn_orange"],
        "red":    COLORS["warn_red"],
    }

    W = 680
    col_w = W / len(organs)
    H = 230

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Semáforo institucional">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    for oi, o in enumerate(organs):
        cx = col_w * oi + col_w / 2
        status = o.get("status", "amber")
        color = status_color.get(status, COLORS["warn_amber"])
        label = _esc(o.get("label", ""))
        note = _esc(o.get("note", ""))

        # Semáforo vertical con 4 estados, el activo en color
        levels = ["red", "orange", "amber", "green"]
        for li, lvl in enumerate(levels):
            cy = 28 + li * 36
            is_active = (lvl == status)
            r = 16 if is_active else 11
            fill = status_color[lvl] if is_active else COLORS["border_dim"]
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
                       f'stroke="{COLORS["bg"]}" stroke-width="2"/>')
            if is_active:
                svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r+4}" '
                           f'fill="none" stroke="{fill}" stroke-width="1.5" opacity="0.4"/>')

        # Label órgano
        svg.append(f'<text x="{cx}" y="195" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="11" font-weight="700" '
                   f'fill="{COLORS["text"]}">{label}</text>')
        # Nota breve
        svg.append(f'<text x="{cx}" y="213" text-anchor="middle" '
                   f'font-family="{FONT_SANS}" font-size="8" '
                   f'fill="{COLORS["text_muted"]}">{note[:40]}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 7. dimensions_radar — radar 8 dimensiones PEIRS (cap 10)
# ═══════════════════════════════════════════════════════════════════════
def render_dimensions_radar(data: Dict[str, Any]) -> str:
    """Data:
        {
          "dimensions": [
            {"label": "Sufragio", "value": 72},
            {"label": "Marco legal", "value": 68},
            ... (8 en total)
          ],
          "scale_max": 100
        }
    """
    dims = data.get("dimensions", [])
    if len(dims) < 3:
        return _render_empty_state("Radar 8 dimensiones no disponible", "Se requieren ≥3 dimensiones evaluadas.")

    scale_max = data.get("scale_max", 100)
    # W más amplio para acomodar labels de 14 chars en los lados sin overflow
    W, H = 500, 420
    cx, cy = W / 2, H / 2
    r_max = 140
    n = len(dims)
    angles = [-math.pi/2 + 2 * math.pi * i / n for i in range(n)]

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Radar 8 dimensiones">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    # Círculos concéntricos (4 niveles)
    for lvl in range(1, 5):
        r = r_max * lvl / 4
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
                   f'stroke="{COLORS["border_dim"]}" stroke-width="0.5" stroke-dasharray="2,3"/>')

    # Ejes
    for a in angles:
        x = cx + r_max * math.cos(a)
        y = cy + r_max * math.sin(a)
        svg.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" '
                   f'stroke="{COLORS["border_dim"]}" stroke-width="0.5"/>')

    # Polígono de valores
    path_d = []
    for i, d in enumerate(dims):
        val = d.get("value", 0)
        r = r_max * (val / scale_max)
        x = cx + r * math.cos(angles[i])
        y = cy + r * math.sin(angles[i])
        path_d.append(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}")
    path_d.append("Z")
    svg.append(f'<path d="{" ".join(path_d)}" fill="{COLORS["teal"]}" '
               f'opacity="0.25" stroke="{COLORS["teal"]}" stroke-width="2"/>')

    # Puntos
    for i, d in enumerate(dims):
        val = d.get("value", 0)
        r = r_max * (val / scale_max)
        x = cx + r * math.cos(angles[i])
        y = cy + r * math.sin(angles[i])
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{COLORS["teal_dark"]}"/>')

    # Labels de dimensión
    for i, d in enumerate(dims):
        label = _esc(d.get("label", ""))[:14]
        val = d.get("value", 0)
        lr = r_max + 26
        lx = cx + lr * math.cos(angles[i])
        ly = cy + lr * math.sin(angles[i])
        anchor = "middle"
        if lx < cx - 10: anchor = "end"
        elif lx > cx + 10: anchor = "start"
        svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
                   f'font-family="{FONT_SANS}" font-size="9" '
                   f'fill="{COLORS["text"]}">{label}</text>')
        svg.append(f'<text x="{lx:.1f}" y="{ly+11:.1f}" text-anchor="{anchor}" '
                   f'font-family="{FONT_MONO}" font-size="9" font-weight="700" '
                   f'fill="{COLORS["teal_dark"]}">{int(val)}</text>')

    svg.append('</svg>')
    return "".join(svg)


# ═══════════════════════════════════════════════════════════════════════
# 8. matrix_normativa — tabla estructurada artículo × tema (cap 2)
# ═══════════════════════════════════════════════════════════════════════
def render_matrix_normativa(data: Dict[str, Any]) -> str:
    """Data:
        {
          "rows": [
            {"instrument": "Constitución Art. 176",
             "topic": "Finalidad sistema electoral", "hierarchy": "constitucional"},
            ...
          ]
        }
    """
    rows = data.get("rows", [])
    if not rows:
        return _render_empty_state("Matriz normativa vacía", "")

    rows = rows[:12]
    W = 680
    row_h = 30
    H = 32 + row_h * len(rows)

    # Columnas
    col_x = {"instrument": 16, "article": 16, "topic": 280, "hierarchy": 540}
    # Colores por jerarquía
    h_color = {
        "constitucional": COLORS["critical"],
        "legal": COLORS["high"],
        "infralegal": COLORS["medium"],
        "jurisprudencial": COLORS["info"],
        "internacional": COLORS["accent_purple"],
    }

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Matriz normativa">']
    svg.append(f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>')

    # Header
    y_hdr = 18
    svg.append(f'<line x1="12" y1="{y_hdr+6}" x2="{W-12}" y2="{y_hdr+6}" '
               f'stroke="{COLORS["teal"]}" stroke-width="1.5"/>')
    for col, label in [("instrument", "INSTRUMENTO"), ("topic", "TEMA"),
                       ("hierarchy", "JERARQUÍA")]:
        svg.append(f'<text x="{col_x[col]}" y="{y_hdr}" font-family="{FONT_SANS}" '
                   f'font-size="9" font-weight="700" letter-spacing="1.5" '
                   f'fill="{COLORS["text_muted"]}">{label}</text>')

    # Rows
    for ri, r in enumerate(rows):
        y = 32 + ri * row_h + 18
        if ri % 2 == 1:
            svg.append(f'<rect x="12" y="{y-18}" width="{W-24}" height="{row_h}" '
                       f'fill="{COLORS["bg_soft"]}"/>')

        inst = _esc(r.get("instrument", ""))[:26]
        topic = _esc(r.get("topic", ""))[:38]
        hier = r.get("hierarchy", "legal")
        color = h_color.get(hier, COLORS["text_muted"])

        svg.append(f'<text x="{col_x["instrument"]}" y="{y}" '
                   f'font-family="{FONT_SANS}" font-size="10" font-weight="600" '
                   f'fill="{COLORS["text"]}">{inst}</text>')
        svg.append(f'<text x="{col_x["topic"]}" y="{y}" '
                   f'font-family="{FONT_SANS}" font-size="10" '
                   f'fill="{COLORS["text_muted"]}">{topic}</text>')
        # Badge jerarquía
        svg.append(f'<rect x="{col_x["hierarchy"]}" y="{y-13}" '
                   f'width="120" height="18" rx="3" '
                   f'fill="{color}" opacity="0.15" stroke="{color}" stroke-width="1"/>')
        svg.append(f'<text x="{col_x["hierarchy"]+60}" y="{y}" '
                   f'text-anchor="middle" font-family="{FONT_MONO}" '
                   f'font-size="9" font-weight="700" '
                   f'fill="{color}">{_esc(hier).upper()}</text>')

    svg.append('</svg>')
    return "".join(svg)
