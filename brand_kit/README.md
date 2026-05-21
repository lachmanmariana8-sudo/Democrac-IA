# Brand Kit · Democrac.IA

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

| Token | Hex | RGB | Rol |
|---|---|---|---|
| `ink` | `#1c2230` | `28, 34, 48` | Navy institucional · headings, autoridad |
| `terracotta` | `#c25a3a` | `194, 90, 58` | Acento de marca · CTAs, énfasis |
| `terracottaSoft` | `#e8b8a6` | `232, 184, 166` | Terracota suavizada · bordes, hover |
| `terracottaBg` | `#fdf2ed` | `253, 242, 237` | Fondo de bloques destacados |
| `bg` | `#fbf9f6` | `251, 249, 246` | Fondo primario crema cálido |
| `bgAlt` | `#f4efe8` | `244, 239, 232` | Fondo secundario un tono más oscuro |
| `surface` | `#ffffff` | `255, 255, 255` | Cards y superficies elevadas |
| `surfaceAlt` | `#f7f3ed` | `247, 243, 237` | Segundo nivel de superficie |
| `border` | `#e5dcd0` | `229, 220, 208` | Bordes sutiles beige |
| `borderStrong` | `#d0c4b0` | `208, 196, 176` | Bordes con presencia |
| `inkSoft` | `#3a4356` | `58, 67, 86` | Texto secundario, copy denso |
| `textMuted` | `#5d6878` | `93, 104, 120` | Texto auxiliar, metadatos |
| `textDim` | `#8b94a3` | `139, 148, 163` | Hints, captions |
| `success` | `#4a7c59` | `74, 124, 89` | Verde apagado · confirmaciones |
| `warning` | `#c8893a` | `200, 137, 58` | Ámbar dorado · advertencias |

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
