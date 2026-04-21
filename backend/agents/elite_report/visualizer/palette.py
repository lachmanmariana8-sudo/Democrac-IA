"""Paleta institucional del Elite Report.

Colores, tipografías y dimensiones estándar para todas las visualizaciones.
Coherente con el CSS del renderer HTML.
"""

# ── Paleta base institucional ─────────────────────────────────────────
COLORS = {
    # Principales
    "teal":       "#00796b",   # verde petróleo institucional
    "teal_dark":  "#004d40",   # verde oscuro para títulos
    "teal_light": "#e0f2f1",   # fondo sutil
    # Texto
    "text":       "#1a1a1a",
    "text_muted": "#64748b",
    "text_dim":   "#94a3b8",
    # Neutros
    "bg":         "#ffffff",
    "bg_soft":    "#fafafa",
    "border":     "#cbd5e1",
    "border_dim": "#e5e7eb",
    # Severidad (consistente con tab Alertas)
    "critical":   "#d32f2f",
    "high":       "#f97316",
    "medium":     "#fbc02d",
    "low":        "#388e3c",
    "info":       "#1976d2",
    # Alertas early warning
    "warn_green":  "#16a34a",
    "warn_amber":  "#ca8a04",
    "warn_orange": "#ea580c",
    "warn_red":    "#dc2626",
    # Acentos
    "accent_blue":   "#3b82f6",
    "accent_purple": "#a855f7",
    "accent_pink":   "#ec4899",
}

# Secuencia de colores para series múltiples
SERIES_PALETTE = [
    "#00796b",  # teal
    "#3b82f6",  # blue
    "#a855f7",  # purple
    "#ec4899",  # pink
    "#f97316",  # orange
    "#16a34a",  # green
]

# ── Dimensiones estándar ───────────────────────────────────────────────
# Ver ELITE_REPORT.md sección 10.2

DIM_INFOGRAPHIC = (640, 200)
DIM_TIMELINE    = (640, 260)
DIM_MATRIX      = (640, 400)
DIM_MAP         = (560, 560)
DIM_NETWORK     = (640, 480)
DIM_RADAR       = (400, 400)
DIM_DONUT       = (320, 320)
DIM_BAR         = (640, None)   # altura variable según cantidad de filas

# ── Tipografías (SVG inline) ──────────────────────────────────────────
FONT_SANS = "'DM Sans', 'Helvetica Neue', Arial, sans-serif"
FONT_MONO = "'DM Mono', 'SF Mono', Menlo, monospace"
FONT_SERIF = "'Fraunces', 'Georgia', serif"

# ── Tamaños ────────────────────────────────────────────────────────────
SIZE_TITLE = 14
SIZE_LABEL = 10
SIZE_VALUE = 24
SIZE_SMALL = 8
