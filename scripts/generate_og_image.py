"""
generate_og_image.py
─────────────────────────────────────────────────────────────────────────
Genera la imagen Open Graph (og-image.png) en 1200×630 para previews
sociales (Facebook, LinkedIn, X, Slack — ninguno acepta SVG en og:image).

Usa Pillow puro. Diseño consistente con el brand kit:
- Fondo crema (#fbf9f6)
- Símbolo de Democrac.IA (3 círculos concéntricos) en navy + núcleo terracota
- Wordmark "Democrac.IA" con .IA en terracota
- Tagline editorial
- Footer con URL

Uso:
    python scripts/generate_og_image.py
    python scripts/generate_og_image.py --out frontend/public/og-image.png
    python scripts/generate_og_image.py --variant voto
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────────────────────────────────
# BRAND TOKENS (espejo del brand kit)
# ─────────────────────────────────────────────────────────────────────────

BG          = (251, 249, 246)   # crema cálida
INK         = (28, 34, 48)      # navy institucional
INK_SOFT    = (58, 67, 86)      # navy más claro
TERRACOTTA  = (194, 90, 58)     # acento de marca
MUTED       = (93, 104, 120)

WIDTH, HEIGHT = 1200, 630


def find_font(*candidates: str, size: int) -> ImageFont.FreeTypeFont:
    """
    Intenta cargar la primera fuente disponible de la lista.
    Si ninguna se encuentra, cae al default de Pillow (bitmap, feo pero seguro).
    """
    # Path típicos en Windows + algunos comunes
    search_dirs = [
        Path("C:/Windows/Fonts"),
        Path("/usr/share/fonts"),
        Path("/Library/Fonts"),
        Path.home() / "AppData/Local/Microsoft/Windows/Fonts",
    ]
    for candidate in candidates:
        # Path absoluto
        p = Path(candidate)
        if p.is_file():
            return ImageFont.truetype(str(p), size=size)
        # Buscar en system fonts
        for sd in search_dirs:
            if not sd.exists():
                continue
            try:
                for f in sd.rglob(candidate):
                    return ImageFont.truetype(str(f), size=size)
            except (OSError, PermissionError):
                continue
    return ImageFont.load_default()


def draw_logo_symbol(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    """
    Tres círculos concéntricos centrados en (cx, cy).
    Mismas proporciones que el componente BrandLogo del front:
    - exterior r=32 stroke 2.5
    - interior r=18 stroke 2.5
    - núcleo  r=5  fill terracota
    """
    r_outer = int(64 * scale)   # 2x para visibilidad en og
    r_inner = int(36 * scale)
    r_core  = int(10 * scale)
    sw      = max(3, int(5 * scale))

    draw.ellipse(
        (cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer),
        outline=INK, width=sw,
    )
    draw.ellipse(
        (cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner),
        outline=INK, width=sw,
    )
    draw.ellipse(
        (cx - r_core, cy - r_core, cx + r_core, cy + r_core),
        fill=TERRACOTTA,
    )


def generate_default_og(out: Path) -> None:
    """OG card institucional · Democrac.IA"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Fuentes (fallbacks razonables si no están las del brand)
    f_eyebrow = find_font("Inter-Bold.ttf", "DMSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf", size=22)
    f_headline = find_font("Fraunces-Black.ttf", "Fraunces-Bold.ttf", "georgiab.ttf", size=88)
    f_subhead = find_font("Inter-Regular.ttf", "DMSans-Regular.ttf", "arial.ttf", size=28)
    f_footer = find_font("Inter-SemiBold.ttf", "arialbd.ttf", size=20)
    f_url = find_font("DMMono-Medium.ttf", "consolab.ttf", "cour.ttf", size=22)

    # Símbolo arriba a la izquierda
    draw_logo_symbol(draw, cx=130, cy=110, scale=1.2)

    # Wordmark "Democrac.IA" al lado del símbolo
    wordmark_y = 75
    draw.text((220, wordmark_y), "Democrac", font=find_font("Fraunces-Black.ttf", "georgiab.ttf", size=64), fill=INK)
    # Calcular ancho real del fragmento "Democrac" para colocar ".IA" al lado
    fnt_demo = find_font("Fraunces-Black.ttf", "georgiab.ttf", size=64)
    bbox = draw.textbbox((220, wordmark_y), "Democrac", font=fnt_demo)
    demo_w = bbox[2] - bbox[0]
    draw.text((220 + demo_w, wordmark_y), ".IA", font=fnt_demo, fill=TERRACOTTA)

    # Eyebrow
    draw.text((90, 240), "PREDICTIVE ELECTORAL INTEGRITY & RISK SYSTEM",
              font=f_eyebrow, fill=TERRACOTTA)

    # Headline grande
    draw.text((90, 280), "Inteligencia electoral", font=f_headline, fill=INK)
    draw.text((90, 380), "basada en evidencia.", font=f_headline, fill=INK)

    # Subhead
    draw.text((90, 500), "V-Dem · Freedom House · PEI · RSF · 38 países",
              font=f_subhead, fill=INK_SOFT)

    # Footer URL
    draw.text((90, 560), "democracia.ar", font=f_url, fill=TERRACOTTA)
    # Tag a la derecha — calcular ancho real para alinear bien al borde
    right_tag = "Apartidario · Open-source"
    bbox_tag = draw.textbbox((0, 0), right_tag, font=f_footer)
    tag_w = bbox_tag[2] - bbox_tag[0]
    tag_x = WIDTH - 90 - tag_w
    draw.text((tag_x, 560), right_tag, font=f_footer, fill=MUTED)
    draw.line([(tag_x, 595), (WIDTH - 90, 595)], fill=(229, 220, 208), width=2)

    img.save(out, "PNG", optimize=True)


def generate_voto_og(out: Path) -> None:
    """OG card alternativa · Voto Informado (sub-marca)"""
    img = Image.new("RGB", (WIDTH, HEIGHT), INK)  # fondo navy
    draw = ImageDraw.Draw(img)

    f_eyebrow = find_font("Inter-Bold.ttf", "arialbd.ttf", size=22)
    f_headline = find_font("Fraunces-Black.ttf", "georgiab.ttf", size=128)
    f_quote = find_font("SourceSerifPro-It.ttf", "georgiai.ttf", size=36)
    f_url = find_font("DMMono-Medium.ttf", "consolab.ttf", "cour.ttf", size=22)

    # Eyebrow superior
    draw.text((90, 90), "UN PROYECTO DE DEMOCRAC.IA",
              font=f_eyebrow, fill=(232, 184, 166))  # terracotaSoft

    # Wordmark editorial gigante "voto.informado"
    voto_y = 200
    fnt_voto = f_headline
    draw.text((90, voto_y), "voto", font=fnt_voto, fill=BG)
    bbox = draw.textbbox((90, voto_y), "voto", font=fnt_voto)
    voto_w = bbox[2] - bbox[0]
    draw.text((90 + voto_w, voto_y), ".", font=fnt_voto, fill=TERRACOTTA)
    bbox = draw.textbbox((90 + voto_w, voto_y), ".", font=fnt_voto)
    dot_w = bbox[2] - bbox[0]
    draw.text((90 + voto_w + dot_w, voto_y), "informado", font=fnt_voto, fill=BG)

    # Tagline serif itálica
    draw.text((90, 400), "Saber antes de elegir.", font=f_quote,
              fill=(232, 184, 166))

    # Línea separadora
    draw.line([(90, 480), (300, 480)], fill=TERRACOTTA, width=3)

    # Footer URL
    draw.text((90, 560), "democracia.ar/?voto=true", font=f_url, fill=(229, 220, 208))

    img.save(out, "PNG", optimize=True)


# ─────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Genera og-image.png para previews sociales")
    parser.add_argument("--out", default="frontend/public/og-image.png",
                        help="Destino del PNG (default: frontend/public/og-image.png)")
    parser.add_argument("--variant", default="default", choices=("default", "voto"),
                        help="Variante: default = institucional, voto = sub-marca")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.variant == "voto":
        generate_voto_og(out_path)
    else:
        generate_default_og(out_path)

    print(f"[OK] OG image generada: {out_path.resolve()} (1200x630)")
    print(f"     Variante: {args.variant}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
