"""
generate_brand_kit.py
─────────────────────────────────────────────────────────────────────────
Genera el brand kit completo de Democrac.IA / Voto Informado.

Produce SVGs procedimentales del logo (mismas geometrías que el componente
React BrandLogo de frontend/src/App.jsx), paletas de color con
swatches, especificaciones tipográficas, un preview HTML navegable y un
único brand-tokens.json como fuente de verdad.

Uso:
    python scripts/generate_brand_kit.py [--out brand_kit]

Salida (folder brand_kit/):
    logo/
        democracia-primary.svg          navy+terracota sobre crema
        democracia-inverse.svg          crema+terracota sobre navy
        democracia-mono-dark.svg        monocromo negro
        democracia-mono-light.svg       monocromo blanco
        democracia-icon.svg             solo símbolo
        democracia-wordmark-h.svg       símbolo + wordmark (horizontal)
        democracia-wordmark-v.svg       símbolo + wordmark (vertical)
        favicon-{16,32,64,180,512}.svg  íconos para meta tags
        voto-informado-h.svg            sub-marca Voto Informado
    palette/
        palette.svg
        palette.json
    typography/
        typography.svg
        typography.json
    brand-tokens.json
    preview.html
    README.md

Cero dependencias externas más allá de stdlib.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────
# BRAND TOKENS — fuente de verdad. Espejo de frontend/src/App.jsx LIGHT/COLORS.
# ─────────────────────────────────────────────────────────────────────────

PALETTE = {
    # Identidad
    "ink":            {"hex": "#1c2230", "rgb": (28, 34, 48),   "role": "Navy institucional · headings, autoridad"},
    "terracotta":     {"hex": "#c25a3a", "rgb": (194, 90, 58),  "role": "Acento de marca · CTAs, énfasis"},
    "terracottaSoft": {"hex": "#e8b8a6", "rgb": (232, 184, 166),"role": "Terracota suavizada · bordes, hover"},
    "terracottaBg":   {"hex": "#fdf2ed", "rgb": (253, 242, 237),"role": "Fondo de bloques destacados"},
    # Backgrounds cálidos
    "bg":             {"hex": "#fbf9f6", "rgb": (251, 249, 246),"role": "Fondo primario crema cálido"},
    "bgAlt":          {"hex": "#f4efe8", "rgb": (244, 239, 232),"role": "Fondo secundario un tono más oscuro"},
    "surface":        {"hex": "#ffffff", "rgb": (255, 255, 255),"role": "Cards y superficies elevadas"},
    "surfaceAlt":     {"hex": "#f7f3ed", "rgb": (247, 243, 237),"role": "Segundo nivel de superficie"},
    # Bordes y texto
    "border":         {"hex": "#e5dcd0", "rgb": (229, 220, 208),"role": "Bordes sutiles beige"},
    "borderStrong":   {"hex": "#d0c4b0", "rgb": (208, 196, 176),"role": "Bordes con presencia"},
    "inkSoft":        {"hex": "#3a4356", "rgb": (58, 67, 86),   "role": "Texto secundario, copy denso"},
    "textMuted":      {"hex": "#5d6878", "rgb": (93, 104, 120), "role": "Texto auxiliar, metadatos"},
    "textDim":        {"hex": "#8b94a3", "rgb": (139, 148, 163),"role": "Hints, captions"},
    # Status (paleta reducida deliberadamente)
    "success":        {"hex": "#4a7c59", "rgb": (74, 124, 89),  "role": "Verde apagado · confirmaciones"},
    "warning":        {"hex": "#c8893a", "rgb": (200, 137, 58), "role": "Ámbar dorado · advertencias"},
}

TYPOGRAPHY = {
    "Inter": {
        "role": "Tipografía de interfaz · UI, navegación, botones, copy denso",
        "weights": [400, 500, 600, 700, 800, 900],
        "sample": "El derecho a saber antes de elegir.",
        "source": "Google Fonts · fonts.google.com/specimen/Inter",
        "licensing": "Open Font License",
    },
    "Fraunces": {
        "role": "Serif editorial · headings principales, identidad institucional",
        "weights": [300, 500, 700, 900],
        "sample": "voto.informado",
        "source": "Google Fonts · fonts.google.com/specimen/Fraunces",
        "licensing": "Open Font License",
    },
    "Source Serif Pro": {
        "role": "Serif para citas itálicas, frases editoriales",
        "weights": [400, 600],
        "italic": True,
        "sample": '"Saber antes de elegir."',
        "source": "Google Fonts · fonts.google.com/specimen/Source+Serif+Pro",
        "licensing": "Open Font License",
    },
    "DM Sans": {
        "role": "Sans alternativa para display y branding secundario",
        "weights": [400, 500, 600, 700, 800],
        "sample": "Democrac.IA",
        "source": "Google Fonts · fonts.google.com/specimen/DM+Sans",
        "licensing": "Open Font License",
    },
    "DM Mono": {
        "role": "Monoespaciada · números, datos, status indicators",
        "weights": [400, 500, 600],
        "sample": "AR-2027-pres · v0.6.0",
        "source": "Google Fonts · fonts.google.com/specimen/DM+Mono",
        "licensing": "Open Font License",
    },
}

# ─────────────────────────────────────────────────────────────────────────
# SVG BUILDERS
# ─────────────────────────────────────────────────────────────────────────

def rgb_to_cmyk(r: int, g: int, b: int) -> tuple[int, int, int, int]:
    if (r, g, b) == (0, 0, 0):
        return (0, 0, 0, 100)
    rn, gn, bn = r / 255, g / 255, b / 255
    k = 1 - max(rn, gn, bn)
    c = (1 - rn - k) / (1 - k) if (1 - k) else 0
    m = (1 - gn - k) / (1 - k) if (1 - k) else 0
    y = (1 - bn - k) / (1 - k) if (1 - k) else 0
    return (round(c * 100), round(m * 100), round(y * 100), round(k * 100))


def logo_symbol_svg(ink: str, accent: str, size: int = 80) -> str:
    """
    Símbolo de Democrac.IA: tres círculos concéntricos.
    - Anillo exterior r=32
    - Anillo interior r=18
    - Núcleo r=5 (sólido, color de acento)
    Viewbox 80x80 con padding 4 (replica BrandLogo del front).
    """
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 80 80">
  <g transform="translate(4,4)">
    <circle cx="36" cy="36" r="32" fill="none" stroke="{ink}" stroke-width="2.5"/>
    <circle cx="36" cy="36" r="18" fill="none" stroke="{ink}" stroke-width="2.5"/>
    <circle cx="36" cy="36" r="5" fill="{accent}"/>
  </g>
</svg>'''


def logo_with_wordmark_horizontal(ink: str, accent: str, bg: str | None = None) -> str:
    """Logo + 'Democrac.IA' a la derecha en una línea."""
    bg_rect = f'<rect width="280" height="80" fill="{bg}"/>' if bg else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="80" viewBox="0 0 280 80">
  {bg_rect}
  <g transform="translate(8,4)">
    <circle cx="36" cy="36" r="32" fill="none" stroke="{ink}" stroke-width="2.5"/>
    <circle cx="36" cy="36" r="18" fill="none" stroke="{ink}" stroke-width="2.5"/>
    <circle cx="36" cy="36" r="5" fill="{accent}"/>
  </g>
  <text x="92" y="50" font-family="Inter, 'DM Sans', system-ui, sans-serif"
        font-size="28" font-weight="800" letter-spacing="-1" fill="{ink}">Democrac<tspan fill="{accent}">.IA</tspan></text>
</svg>'''


def logo_with_wordmark_vertical(ink: str, accent: str, bg: str | None = None) -> str:
    """Logo arriba, 'Democrac.IA' centrado debajo."""
    bg_rect = f'<rect width="200" height="160" fill="{bg}"/>' if bg else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="160" viewBox="0 0 200 160">
  {bg_rect}
  <g transform="translate(60,10)">
    <circle cx="36" cy="36" r="32" fill="none" stroke="{ink}" stroke-width="2.5"/>
    <circle cx="36" cy="36" r="18" fill="none" stroke="{ink}" stroke-width="2.5"/>
    <circle cx="36" cy="36" r="5" fill="{accent}"/>
  </g>
  <text x="100" y="125" text-anchor="middle" font-family="Inter, 'DM Sans', system-ui, sans-serif"
        font-size="24" font-weight="800" letter-spacing="-0.8" fill="{ink}">Democrac<tspan fill="{accent}">.IA</tspan></text>
</svg>'''


def voto_informado_logo(ink: str, accent: str, bg: str | None = None) -> str:
    """Sub-marca voto.informado — wordmark editorial sin símbolo."""
    bg_rect = f'<rect width="320" height="80" fill="{bg}"/>' if bg else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="80" viewBox="0 0 320 80">
  {bg_rect}
  <text x="20" y="58" font-family="Fraunces, Georgia, serif"
        font-size="44" font-weight="900" letter-spacing="-2" fill="{ink}">voto<tspan fill="{accent}">.</tspan>informado</text>
</svg>'''


def favicon_svg(size: int, ink: str, accent: str) -> str:
    """Versión simplificada del símbolo para favicons pequeños."""
    # En tamaños chicos engrosamos el stroke para visibilidad
    stroke = max(2.5, 80 / size * 1.5)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 80 80">
  <g transform="translate(4,4)">
    <circle cx="36" cy="36" r="32" fill="none" stroke="{ink}" stroke-width="{stroke:.1f}"/>
    <circle cx="36" cy="36" r="18" fill="none" stroke="{ink}" stroke-width="{stroke:.1f}"/>
    <circle cx="36" cy="36" r="5" fill="{accent}"/>
  </g>
</svg>'''


def palette_swatches_svg() -> str:
    """Tarjeta visual con todos los colores de la paleta."""
    items = list(PALETTE.items())
    cols = 4
    cell_w, cell_h = 200, 110
    rows = (len(items) + cols - 1) // cols
    width = cols * cell_w + 20
    height = rows * cell_h + 60

    swatches = []
    for i, (name, info) in enumerate(items):
        r, c = divmod(i, cols)
        x = 10 + c * cell_w
        y = 50 + r * cell_h
        text_fill = "#1c2230" if info["hex"] in ("#fbf9f6", "#ffffff", "#f4efe8", "#f7f3ed", "#fdf2ed", "#e5dcd0", "#e8b8a6") else "#ffffff"
        swatches.append(f'''
  <g>
    <rect x="{x}" y="{y}" width="{cell_w - 10}" height="{cell_h - 10}" fill="{info['hex']}" stroke="#e5dcd0" stroke-width="1" rx="6"/>
    <text x="{x + 12}" y="{y + 28}" font-family="Inter, sans-serif" font-size="13" font-weight="700" fill="{text_fill}">{name}</text>
    <text x="{x + 12}" y="{y + 48}" font-family="DM Mono, monospace" font-size="11" fill="{text_fill}" opacity="0.75">{info['hex']}</text>
    <text x="{x + 12}" y="{y + 78}" font-family="Inter, sans-serif" font-size="10" fill="{text_fill}" opacity="0.7">{info['role'][:42]}</text>
  </g>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#fbf9f6"/>
  <text x="20" y="30" font-family="Fraunces, serif" font-size="22" font-weight="800" fill="#1c2230">Paleta Democrac.IA</text>
  {''.join(swatches)}
</svg>'''


def typography_spec_svg() -> str:
    width, height = 880, 100 + len(TYPOGRAPHY) * 130
    items = []
    for i, (font, info) in enumerate(TYPOGRAPHY.items()):
        y = 80 + i * 130
        font_family = f"{font}, serif" if font in ("Fraunces", "Source Serif Pro") else f"{font}, sans-serif"
        sample_style = "italic" if info.get("italic") else "normal"
        weights_label = " · ".join(f"{w}" for w in info["weights"])
        items.append(f'''
  <g>
    <text x="20" y="{y}" font-family="DM Mono, monospace" font-size="11" font-weight="700"
          letter-spacing="2" fill="#c25a3a">{font.upper()}</text>
    <text x="20" y="{y + 24}" font-family="Inter, sans-serif" font-size="13" fill="#5d6878">{info['role']}</text>
    <text x="20" y="{y + 70}" font-family="{font_family}" font-size="32" font-weight="700"
          font-style="{sample_style}" fill="#1c2230">{info['sample']}</text>
    <text x="20" y="{y + 95}" font-family="DM Mono, monospace" font-size="10" fill="#8b94a3">weights · {weights_label}</text>
    <line x1="20" y1="{y + 110}" x2="{width - 20}" y2="{y + 110}" stroke="#e5dcd0" stroke-width="1"/>
  </g>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#fbf9f6"/>
  <text x="20" y="40" font-family="Fraunces, serif" font-size="22" font-weight="800" fill="#1c2230">Tipografía Democrac.IA</text>
  {''.join(items)}
</svg>'''


# ─────────────────────────────────────────────────────────────────────────
# PREVIEW HTML
# ─────────────────────────────────────────────────────────────────────────

PREVIEW_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<title>Brand Kit · Democrac.IA</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500;600&family=Fraunces:wght@300;500;700;900&family=Inter:wght@400;500;600;700;800;900&family=Source+Serif+Pro:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg: #fbf9f6; --bg-alt: #f4efe8; --surface: #fff; --ink: #1c2230;
    --ink-soft: #3a4356; --terracotta: #c25a3a; --border: #e5dcd0; --muted: #5d6878;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: var(--bg); color: var(--ink); }}
  header {{ padding: 40px 7%; border-bottom: 1px solid var(--border); }}
  h1 {{ font-family: Fraunces, serif; font-size: 42px; letter-spacing: -1.5px; margin: 0 0 8px; }}
  h2 {{ font-family: Fraunces, serif; font-size: 28px; margin: 48px 0 16px; letter-spacing: -0.5px; }}
  .tag {{ display: inline-block; font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--terracotta); font-weight: 700; padding: 4px 0; }}
  section {{ padding: 0 7% 40px; max-width: 1280px; margin: 0 auto; }}
  .grid {{ display: grid; gap: 16px; }}
  .grid.cols-3 {{ grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
  .grid.cols-2 {{ grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 24px; display: flex; flex-direction: column; gap: 12px; }}
  .card .label {{ font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--muted); font-weight: 700; }}
  .card img, .card object {{ max-width: 100%; height: auto; }}
  .card.dark {{ background: var(--ink); color: #fff; }}
  .card.dark .label {{ color: #e8b8a6; }}
  .swatch {{ display: flex; align-items: center; gap: 14px; padding: 10px 14px;
    border: 1px solid var(--border); border-radius: 8px; background: var(--surface); }}
  .swatch .chip {{ width: 36px; height: 36px; border-radius: 6px; border: 1px solid var(--border); flex-shrink: 0; }}
  .swatch .meta {{ display: flex; flex-direction: column; gap: 2px; }}
  .swatch code {{ font-family: 'DM Mono', monospace; font-size: 12px; color: var(--muted); }}
  .swatch strong {{ font-size: 13px; color: var(--ink); }}
  pre {{ background: var(--bg-alt); padding: 14px; border-radius: 8px; overflow: auto;
    font-family: 'DM Mono', monospace; font-size: 12px; }}
  footer {{ padding: 40px 7%; border-top: 1px solid var(--border); background: var(--bg-alt);
    font-size: 13px; color: var(--muted); margin-top: 60px; }}
</style>
</head>
<body>
<header>
  <span class="tag">Brand Kit · v1.0</span>
  <h1>Democrac<span style="color:var(--terracotta)">.IA</span></h1>
  <p style="font-size:18px;color:var(--ink-soft);max-width:680px;line-height:1.6;margin:8px 0 0">
    Identidad visual completa: símbolo, wordmark, paleta y tipografía. Replica
    fielmente el componente <code>BrandLogo</code> del frontend en
    <code>App.jsx</code>. Todos los SVGs son editables y escalables sin pérdida.
  </p>
</header>

<section>
  <span class="tag">01 · Logo</span>
  <h2>Variantes del logo</h2>
  <div class="grid cols-2">
{logo_cards}
  </div>
</section>

<section>
  <span class="tag">02 · Paleta</span>
  <h2>Colores</h2>
  <div class="grid cols-3">
{palette_cards}
  </div>
</section>

<section>
  <span class="tag">03 · Tipografía</span>
  <h2>Familias</h2>
  <object data="typography/typography.svg" type="image/svg+xml" style="width:100%;max-width:880px"></object>
</section>

<section>
  <span class="tag">04 · Uso</span>
  <h2>Reglas mínimas</h2>
  <div class="grid cols-2">
    <div class="card">
      <div class="label">Clearspace</div>
      <p>Reservar un espacio libre alrededor del símbolo equivalente al radio
      del anillo exterior (≈ 50% del lado del bounding box). No colocar texto,
      imágenes ni elementos gráficos dentro de esa zona.</p>
    </div>
    <div class="card">
      <div class="label">Tamaño mínimo</div>
      <p>El símbolo solo: 24 px en pantalla, 8 mm en impresión.
      Logo + wordmark: 120 px en pantalla, 30 mm en impresión. Por debajo,
      usar solo el símbolo.</p>
    </div>
    <div class="card">
      <div class="label">No hacer</div>
      <p>· No cambiar las proporciones de los círculos.<br/>
         · No modificar la posición relativa wordmark/símbolo.<br/>
         · No usar gradientes ni sombras sobre el símbolo.<br/>
         · No rotar ni invertir el símbolo.</p>
    </div>
    <div class="card">
      <div class="label">Sí hacer</div>
      <p>· Usar el monocromo cuando el contexto lo requiera (impresión a una
      tinta, bordados).<br/>
         · Variar el color del símbolo solo entre navy y blanco / negro.<br/>
         · El núcleo siempre va en terracota o en el mismo color del trazo
         si la versión es monocroma.</p>
    </div>
  </div>
</section>

<footer>
  Brand Kit Democrac.IA · generado por <code>scripts/generate_brand_kit.py</code> ·
  Replica el componente BrandLogo del frontend para mantener identidad consistente
  entre la app y materiales externos.
</footer>
</body>
</html>
"""


def card_html_for_logo(label: str, filename: str, dark: bool = False) -> str:
    cls = "card dark" if dark else "card"
    return f'''    <div class="{cls}">
      <div class="label">{label}</div>
      <object data="logo/{filename}" type="image/svg+xml" style="width:100%;max-width:320px"></object>
      <code style="font-size:11px;opacity:0.7">logo/{filename}</code>
    </div>'''


def card_html_for_swatch(name: str, info: dict) -> str:
    return f'''    <div class="swatch">
      <div class="chip" style="background:{info['hex']}"></div>
      <div class="meta">
        <strong>{name}</strong>
        <code>{info['hex']} · rgb({info['rgb'][0]}, {info['rgb'][1]}, {info['rgb'][2]})</code>
      </div>
    </div>'''


# ─────────────────────────────────────────────────────────────────────────
# README
# ─────────────────────────────────────────────────────────────────────────

README_TEMPLATE = """# Brand Kit · Democrac.IA

Identidad visual completa para Democrac.IA y su sub-marca Voto Informado.

Este folder es generado automáticamente por `scripts/generate_brand_kit.py`.
**No editar a mano**: cualquier cambio se sobreescribe en la próxima
regeneración. La fuente de verdad es el script.

## Estructura

```
brand_kit/
├── logo/                       Variantes del logo en SVG
├── palette/                    Paleta completa
├── typography/                 Especificación tipográfica
├── brand-tokens.json           Single source of truth (JSON)
├── preview.html                Vista previa navegable
└── README.md                   Este archivo
```

## Logo · concepto

Tres círculos concéntricos:

- **Anillo exterior** (r=32) · marco institucional, sistema democrático
- **Anillo interior** (r=18) · proceso, deliberación, contexto
- **Núcleo** (r=5, terracota) · el voto, el ciudadano, el punto decisivo

Lectura: el ciudadano (núcleo) opera dentro de capas institucionales que lo
contienen pero no lo sustituyen. La terracota del núcleo marca que ahí está
el punto vital del sistema.

## Wordmark

`Democrac` en navy + `.IA` en terracota. Tipografía Inter 800,
letter-spacing -1. Nunca alterar el peso o el spacing.

## Paleta

Cremas cálidas + navy + terracota. Mínima por diseño:

{palette_table}

## Tipografía

Cinco familias, todas open source:

- **Inter** — interfaz, copy denso, navegación
- **Fraunces** — headings principales, identidad editorial
- **Source Serif Pro** (italic) — citas, frases destacadas
- **DM Sans** — alternativa display secundaria
- **DM Mono** — números, datos, status

## Regenerar el kit

```bash
python scripts/generate_brand_kit.py --out brand_kit
```

Si querés exportar PNGs además de SVGs, agregale `--png` (requiere
`cairosvg` instalado). Sin esa flag, solo SVGs (suficiente para web).

## Uso en otros materiales

- **Slides** · usar `democracia-wordmark-h.svg` en footer, símbolo solo en
  esquinas
- **Documentos** · `democracia-primary.svg` en portada, monocromo en cuerpo
- **Web externa** · favicons en `logo/favicon-*.svg`
- **Voto Informado** · `voto-informado-h.svg` como wordmark independiente

Cualquier ajuste que se haga en `frontend/src/App.jsx` (paleta, BrandLogo)
debe replicarse en este script para mantener consistencia.
"""


def make_palette_markdown_table() -> str:
    lines = ["| Token | Hex | RGB | Rol |", "|---|---|---|---|"]
    for name, info in PALETTE.items():
        r, g, b = info["rgb"]
        lines.append(f"| `{name}` | `{info['hex']}` | `{r}, {g}, {b}` | {info['role']} |")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────
# GENERATE
# ─────────────────────────────────────────────────────────────────────────

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_brand_kit(out_dir: Path) -> None:
    ink = PALETTE["ink"]["hex"]
    terracotta = PALETTE["terracotta"]["hex"]
    bg = PALETTE["bg"]["hex"]

    logo_dir = out_dir / "logo"
    palette_dir = out_dir / "palette"
    typo_dir = out_dir / "typography"

    # ── Logo variants ───────────────────────────────────────────────────
    logo_files = [
        ("democracia-primary.svg",      logo_with_wordmark_horizontal(ink, terracotta, bg)),
        ("democracia-inverse.svg",      logo_with_wordmark_horizontal(bg, terracotta, ink)),
        ("democracia-mono-dark.svg",    logo_with_wordmark_horizontal("#000000", "#000000", None)),
        ("democracia-mono-light.svg",   logo_with_wordmark_horizontal("#ffffff", "#ffffff", None)),
        ("democracia-icon.svg",         logo_symbol_svg(ink, terracotta)),
        ("democracia-wordmark-h.svg",   logo_with_wordmark_horizontal(ink, terracotta, None)),
        ("democracia-wordmark-v.svg",   logo_with_wordmark_vertical(ink, terracotta, None)),
        ("voto-informado-h.svg",        voto_informado_logo(ink, terracotta, None)),
    ]
    for filename, content in logo_files:
        write(logo_dir / filename, content)

    # Favicons en varios tamaños
    for sz in (16, 32, 64, 180, 512):
        write(logo_dir / f"favicon-{sz}.svg", favicon_svg(sz, ink, terracotta))

    # ── Palette ────────────────────────────────────────────────────────
    write(palette_dir / "palette.svg", palette_swatches_svg())
    palette_json = {
        name: {
            **info,
            "cmyk": rgb_to_cmyk(*info["rgb"]),
        } for name, info in PALETTE.items()
    }
    write(palette_dir / "palette.json", json.dumps(palette_json, indent=2, ensure_ascii=False))

    # ── Typography ─────────────────────────────────────────────────────
    write(typo_dir / "typography.svg", typography_spec_svg())
    write(typo_dir / "typography.json", json.dumps(TYPOGRAPHY, indent=2, ensure_ascii=False))

    # ── Brand tokens (single source) ───────────────────────────────────
    tokens = {
        "version": "1.0",
        "brand": "Democrac.IA",
        "sub_brands": ["Voto Informado"],
        "palette": palette_json,
        "typography": TYPOGRAPHY,
        "logo": {
            "construction": {
                "viewbox": "80x80",
                "padding": 4,
                "outer_radius": 32,
                "inner_radius": 18,
                "core_radius": 5,
                "stroke_width": 2.5,
            },
            "files": [f for f, _ in logo_files] + [f"favicon-{s}.svg" for s in (16, 32, 64, 180, 512)],
        },
    }
    write(out_dir / "brand-tokens.json", json.dumps(tokens, indent=2, ensure_ascii=False))

    # ── Preview HTML ───────────────────────────────────────────────────
    logo_cards = "\n".join([
        card_html_for_logo("Primary · navy + terracota", "democracia-primary.svg"),
        card_html_for_logo("Inverse · cream sobre navy", "democracia-inverse.svg", dark=True),
        card_html_for_logo("Mono dark", "democracia-mono-dark.svg"),
        card_html_for_logo("Mono light", "democracia-mono-light.svg", dark=True),
        card_html_for_logo("Icon only", "democracia-icon.svg"),
        card_html_for_logo("Wordmark horizontal", "democracia-wordmark-h.svg"),
        card_html_for_logo("Wordmark vertical", "democracia-wordmark-v.svg"),
        card_html_for_logo("Voto Informado · sub-marca", "voto-informado-h.svg"),
    ])
    palette_cards = "\n".join(card_html_for_swatch(n, info) for n, info in PALETTE.items())
    preview = PREVIEW_TEMPLATE.format(
        logo_cards=logo_cards,
        palette_cards=palette_cards,
    )
    write(out_dir / "preview.html", preview)

    # ── README ────────────────────────────────────────────────────────
    readme = README_TEMPLATE.format(palette_table=make_palette_markdown_table())
    write(out_dir / "README.md", readme)


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera el brand kit de Democrac.IA")
    parser.add_argument("--out", default="brand_kit", help="Folder de salida (default: brand_kit/)")
    args = parser.parse_args()

    out_dir = Path(args.out)
    generate_brand_kit(out_dir)

    # ASCII-only print para compatibilidad con consolas cp1252 (Windows)
    print(f"[OK] Brand kit generado en {out_dir.resolve()}")
    print(f"     Abri {out_dir / 'preview.html'} para ver todos los assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
