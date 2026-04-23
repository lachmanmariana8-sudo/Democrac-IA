"""FrameRenderer — compositor de PNGs por beat (Fase B1).

Fase B1 cubre los 3 visuales más simples basados en Pillow puro:
  - solid_bg     : fondo sólido + overlays (intro/outro)
  - kpi_grid     : grilla de 4 KPIs destacados
  - quote_panel  : cita grande con atribución

Los visuales restantes (bar_chart, donut_chart, timeline, map_regions) se
implementan en Fase B2 con matplotlib. Mientras tanto caen al default
solid_bg con un aviso.

Fase C sincroniza audio (edge-tts), Fase D compone en MP4 (moviepy/ffmpeg).
"""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except ImportError:  # pragma: no cover
    _PIL_OK = False

from agents.video_producer.models import Beat, Overlay


# ── Paleta institucional DemocracIA (alineada con el dashboard) ──────────────

BRAND: Dict[str, str] = {
    "bg":         "#0B1F2A",   # teal oscuro (fondo principal)
    "bg_soft":    "#0F4F4B",   # teal medio (cards/chips)
    "text":       "#EAF2EF",   # blanco cálido
    "text_dim":   "#94B0AA",
    "accent":     "#D97706",   # naranja institucional (CTA, KPI críticos)
    "info":       "#38BDF8",
    "danger":     "#EF4444",
    "warning":    "#F59E0B",
    "success":    "#10B981",
    "purple":     "#A855F7",
}


# ── Carga de fuentes (con fallback graceful) ─────────────────────────────────

def _load_font(size: int, bold: bool = False) -> "ImageFont.FreeTypeFont":
    """Busca una TTF razonable en el sistema; si no encuentra, usa default."""
    candidates_regular = [
        "DejaVuSans.ttf",                                          # Linux/Railway nixpacks
        "DejaVuSans-Bold.ttf",                                     # solo como fallback
        "Arial.ttf",
        "arial.ttf",                                               # Windows
        "/System/Library/Fonts/Helvetica.ttc",                     # macOS
    ]
    candidates_bold = [
        "DejaVuSans-Bold.ttf",
        "Arial Bold.ttf",
        "arialbd.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    search = candidates_bold if bold else candidates_regular
    for name in search:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    # Pillow ships con una default bitmap font chiquita — último recurso.
    return ImageFont.load_default()  # type: ignore[return-value]


def _measure(draw: "ImageDraw.ImageDraw", text: str, font) -> Tuple[int, int]:
    """Devuelve (w, h) del bounding box del texto."""
    # textbbox existe desde Pillow 8. Fallback a textsize para compat.
    try:
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
        return (r - l, b - t)
    except Exception:
        try:
            return draw.textsize(text, font=font)  # type: ignore[attr-defined]
        except Exception:
            return (len(text) * 8, 14)


def _fit_font(
    draw: "ImageDraw.ImageDraw",
    text: str,
    max_w: int,
    max_h: int,
    initial_size: int,
    bold: bool = False,
    min_size: int = 12,
) -> "ImageFont.FreeTypeFont":
    """Busca el tamaño de fuente más grande que entra en (max_w × max_h)."""
    size = max(int(initial_size), min_size)
    while size > min_size:
        font = _load_font(size, bold=bold)
        w, h = _measure(draw, text, font)
        if w <= max_w and h <= max_h:
            return font
        size = int(size * 0.9)
    return _load_font(min_size, bold=bold)


# ── Renderer principal ────────────────────────────────────────────────────────

class FrameRenderer:
    """Compone un frame PNG (PIL Image) a partir de un Beat.

    El renderizado es determinístico: mismo beat → mismo PNG. Esto permite
    hacer diffs visuales en tests y cachear frames.
    """

    def __init__(self, width: int = 1080, height: int = 1920):
        if not _PIL_OK:
            raise RuntimeError(
                "Pillow no está instalado — agregar 'pillow>=10.0' a requirements.txt"
            )
        self.width = int(width)
        self.height = int(height)

    # ── Punto de entrada ────────────────────────────────────────────────
    def render(self, beat: Beat) -> "Image.Image":
        dispatch = {
            "solid_bg":    self._render_solid_bg,
            "kpi_grid":    self._render_kpi_grid,
            "quote_panel": self._render_quote_panel,
        }
        fn = dispatch.get(beat.visual, self._render_fallback)
        img = fn(beat)
        self._apply_overlays(img, beat)
        self._apply_brand_footer(img)
        return img

    def render_png(self, beat: Beat) -> bytes:
        buf = BytesIO()
        self.render(beat).save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    # ── Visuales (Fase B1) ──────────────────────────────────────────────

    def _render_solid_bg(self, beat: Beat) -> "Image.Image":
        bg = beat.bg_color_hex or BRAND["bg"]
        return Image.new("RGB", (self.width, self.height), bg)

    def _render_kpi_grid(self, beat: Beat) -> "Image.Image":
        img = Image.new("RGB", (self.width, self.height), beat.bg_color_hex or BRAND["bg"])
        draw = ImageDraw.Draw(img)

        kpis: List[Dict] = list(beat.visual_data.get("kpis") or [])[:4]
        if not kpis:
            return img

        # Grilla 2×2 centrada
        cols, rows = 2, 2
        margin_x = int(self.width * 0.08)
        margin_y = int(self.height * 0.18)
        grid_w = self.width - 2 * margin_x
        grid_h = self.height - 2 * margin_y
        cell_w = grid_w // cols
        cell_h = grid_h // rows
        gap = int(min(cell_w, cell_h) * 0.06)

        # Padding interno de la card (donde se pintan value/label).
        inner_pad_x = int(cell_w * 0.12)
        inner_pad_y = int(cell_h * 0.12)

        for idx, kpi in enumerate(kpis):
            col = idx % cols
            row = idx // cols
            x0 = margin_x + col * cell_w + gap
            y0 = margin_y + row * cell_h + gap
            x1 = x0 + cell_w - 2 * gap
            y1 = y0 + cell_h - 2 * gap

            # Card con borde acento
            draw.rounded_rectangle((x0, y0, x1, y1), radius=20, fill=BRAND["bg_soft"])
            accent = BRAND["accent"] if idx == 0 else BRAND["info"]
            draw.rounded_rectangle((x0, y0, x0 + 8, y1), radius=4, fill=accent)

            value = str(kpi.get("value", "—"))
            label = str(kpi.get("label", ""))

            # Caja útil para el valor (deja lugar arriba/abajo para el label).
            inner_w = (x1 - x0) - 2 * inner_pad_x
            value_box_h = int((y1 - y0) * 0.55)   # ~55% para el número
            label_box_h = int((y1 - y0) * 0.20)   # ~20% para el label

            font_value = _fit_font(
                draw, value,
                max_w=inner_w, max_h=value_box_h,
                initial_size=int(cell_h * 0.50), bold=True,
            )
            font_label = _fit_font(
                draw, label.upper(),
                max_w=inner_w, max_h=label_box_h,
                initial_size=int(cell_h * 0.11),
            )

            vw, vh = _measure(draw, value, font_value)
            lw, lh = _measure(draw, label.upper(), font_label)

            cx = (x0 + x1) // 2
            # Valor centrado vertical/horizontal en la zona superior de la card.
            draw.text(
                (cx - vw / 2, y0 + inner_pad_y + (value_box_h - vh) / 2),
                value, font=font_value, fill=accent,
            )
            # Label debajo, justo encima del padding inferior.
            draw.text(
                (cx - lw / 2, y1 - inner_pad_y - lh),
                label.upper(), font=font_label, fill=BRAND["text_dim"],
            )

        return img

    def _render_quote_panel(self, beat: Beat) -> "Image.Image":
        img = Image.new("RGB", (self.width, self.height), beat.bg_color_hex or BRAND["bg"])
        draw = ImageDraw.Draw(img)

        # Tomamos el primer overlay de kind=quote; si no hay, usamos el primer texto.
        quote_text = ""
        attr = ""
        for ov in beat.overlays:
            if ov.kind == "quote" and ov.text:
                quote_text = ov.text
                attr = ov.secondary_text or ""
                break
        if not quote_text and beat.overlays:
            quote_text = beat.overlays[0].text

        if not quote_text:
            return img

        # Comillas gigantes decorativas arriba-izquierda
        font_quotes = _load_font(int(self.height * 0.18), bold=True)
        draw.text((int(self.width * 0.08), int(self.height * 0.08)), "“",
                  font=font_quotes, fill=BRAND["accent"])

        # Cuerpo de la cita — wrap manual por ancho del canvas
        font_body = _load_font(int(self.height * 0.035), bold=True)
        max_w = int(self.width * 0.82)
        lines = _wrap_text(draw, quote_text, font_body, max_w)

        line_h = _measure(draw, "Ag", font_body)[1]
        total_h = line_h * len(lines) * 1.3
        y0 = int((self.height - total_h) / 2)
        x0 = int(self.width * 0.09)
        for i, line in enumerate(lines):
            draw.text((x0, y0 + int(i * line_h * 1.3)), line,
                      font=font_body, fill=BRAND["text"])

        # Atribución abajo
        if attr:
            font_attr = _load_font(int(self.height * 0.025))
            draw.text((x0, int(self.height * 0.78)), f"— {attr}",
                      font=font_attr, fill=BRAND["text_dim"])

        return img

    # ── Fallback para visuales no implementados (Fase B2) ───────────────

    def _render_fallback(self, beat: Beat) -> "Image.Image":
        img = Image.new("RGB", (self.width, self.height), beat.bg_color_hex or BRAND["bg"])
        draw = ImageDraw.Draw(img)
        font = _load_font(int(self.height * 0.03))
        msg = f"visual={beat.visual!r} — pendiente Fase B2"
        w, h = _measure(draw, msg, font)
        draw.text(((self.width - w) / 2, (self.height - h) / 2), msg,
                  font=font, fill=BRAND["text_dim"])
        return img

    # ── Overlays + branding ─────────────────────────────────────────────

    def _apply_overlays(self, img: "Image.Image", beat: Beat) -> None:
        if not beat.overlays:
            return
        draw = ImageDraw.Draw(img)
        for ov in beat.overlays:
            # quote ya se dibuja dentro de quote_panel — no duplicar.
            if ov.kind == "quote" and beat.visual == "quote_panel":
                continue
            self._draw_overlay(draw, ov)

    def _draw_overlay(self, draw: "ImageDraw.ImageDraw", ov: Overlay) -> None:
        if ov.kind == "title":
            font = _load_font(int(self.height * 0.055), bold=True)
            w, h = _measure(draw, ov.text, font)
            draw.text(((self.width - w) / 2, (self.height - h) / 2), ov.text,
                      font=font, fill=BRAND["text"])
            return

        if ov.kind == "lower_third":
            # Franja semi-opaca en el tercio inferior
            strip_y0 = int(self.height * 0.72)
            strip_y1 = int(self.height * 0.90)
            draw.rectangle((0, strip_y0, self.width, strip_y1), fill=BRAND["bg_soft"])
            draw.rectangle((0, strip_y0, 16, strip_y1), fill=BRAND["accent"])

            font_primary = _load_font(int(self.height * 0.028), bold=True)
            font_secondary = _load_font(int(self.height * 0.020))
            pad = int(self.width * 0.04)
            draw.text((pad, strip_y0 + int(self.height * 0.03)), ov.text,
                      font=font_primary, fill=BRAND["text"])
            if ov.secondary_text:
                draw.text((pad, strip_y0 + int(self.height * 0.085)),
                          ov.secondary_text.upper(),
                          font=font_secondary, fill=BRAND["text_dim"])
            return

        if ov.kind == "source":
            font = _load_font(int(self.height * 0.020))
            pad = int(self.width * 0.05)
            draw.text((pad, int(self.height * 0.92)), ov.text,
                      font=font, fill=BRAND["text_dim"])
            return

        if ov.kind == "cta":
            font = _load_font(int(self.height * 0.050), bold=True)
            w, h = _measure(draw, ov.text, font)
            y = int(self.height * 0.55)
            draw.text(((self.width - w) / 2, y), ov.text,
                      font=font, fill=BRAND["accent"])
            # Subtítulo
            sub = "democracIA — observación electoral"
            font_sub = _load_font(int(self.height * 0.018))
            sw, sh = _measure(draw, sub, font_sub)
            draw.text(((self.width - sw) / 2, y + h + int(self.height * 0.02)), sub,
                      font=font_sub, fill=BRAND["text_dim"])
            return

        # Fallback: dibujar como texto simple abajo
        font = _load_font(int(self.height * 0.022))
        pad = int(self.width * 0.04)
        draw.text((pad, int(self.height * 0.94)), ov.text,
                  font=font, fill=BRAND["text_dim"])

    def _apply_brand_footer(self, img: "Image.Image") -> None:
        """Microlink + logo texto en el footer — consistente en todos los frames."""
        draw = ImageDraw.Draw(img)
        font = _load_font(int(self.height * 0.014))
        brand = "DEMOCRAC.IA · democracia.ar"
        w, h = _measure(draw, brand, font)
        draw.text((self.width - w - int(self.width * 0.04),
                   self.height - h - int(self.height * 0.015)),
                  brand, font=font, fill=BRAND["text_dim"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _wrap_text(draw, text: str, font, max_w: int) -> List[str]:
    """Word-wrap simple por ancho en píxeles."""
    words = text.split()
    if not words:
        return []
    lines: List[str] = []
    cur = words[0]
    for w in words[1:]:
        candidate = cur + " " + w
        width, _ = _measure(draw, candidate, font)
        if width <= max_w:
            cur = candidate
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


# ── API de módulo ─────────────────────────────────────────────────────────────

def render_beat_png(beat: Beat, width: int, height: int) -> bytes:
    """Shortcut: render directo a PNG bytes."""
    return FrameRenderer(width=width, height=height).render_png(beat)


def render_beat_to_file(beat: Beat, out_path: Path, width: int, height: int) -> Path:
    """Render + save. Devuelve la ruta del archivo escrito."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(render_beat_png(beat, width, height))
    return out_path
