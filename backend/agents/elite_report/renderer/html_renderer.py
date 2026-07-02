"""HTML + Markdown renderers del Elite Report.

CSS institucional embebido (OEA-style: tipografía Fraunces+DM Sans+DM Mono,
paleta teal petróleo, layout para pantalla y print/PDF).

Produce HTML autónomo (todo inline: CSS, SVG, fuentes webfont) para:
- Mostrar en iframe del tab frontend
- Base del PDF (pasado a weasyprint/xhtml2pdf)
- Publicación web directa
"""
from __future__ import annotations

import html as _html
import json as _json
import re
from datetime import datetime
from pathlib import Path as _Path
from typing import Any, Dict, List, Optional

from agents.elite_report.models import (
    EliteChapter,
    EliteReportRequest,
    CitationEntry,
    ForecastPayload,
    VizSpec,
)
from agents.elite_report.visualizer import render_svg
from agents.elite_report.i18n import t, category_label
from agents.elite_report.section_titles import translate_section_titles


# ── CSS institucional ──────────────────────────────────────────────────
ELITE_CSS = """
:root {
  --teal: #00796b;
  --teal-dark: #004d40;
  --teal-light: #e0f2f1;
  --text: #1a1a1a;
  --text-muted: #64748b;
  --text-dim: #94a3b8;
  --bg: #ffffff;
  --bg-soft: #fafafa;
  --border: #cbd5e1;
  --border-dim: #e5e7eb;
  --critical: #d32f2f;
  --high: #f97316;
  --medium: #fbc02d;
  --low: #388e3c;
  --info: #1976d2;
}

/* display=block: el navegador espera a la webfont (hasta ~3s) en vez de
   pintar primero un fallback. Evita el "flash" de fuente de sistema que en
   impresión/PDF dejaba la 'l' minúscula con grosor distinto al sustituir. */
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@400;600;800&family=DM+Sans:wght@400;500;700&family=DM+Mono:wght@400;500;700&display=block');

* { box-sizing: border-box; }

html, body {
  margin: 0; padding: 0;
  /* Fallback cross-platform (system-ui/Segoe UI/Roboto) para que, si la
     webfont no carga, la sustitución sea consistente y no afecte la 'l'. */
  font-family: 'DM Sans', system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text);
  background: var(--bg);
  overflow-x: hidden;  /* evita scroll horizontal accidental */
  /* Ligaduras desactivadas + smoothing uniforme: el bug de la 'l' en negrita
     al imprimir venía de ligaduras/anti-aliasing inconsistente entre la
     webfont y el fallback durante el swap. */
  font-feature-settings: "liga" 0, "clig" 0;
  font-variant-ligatures: none;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

article.elite-report {
  max-width: 880px;
  margin: 0 auto;
  padding: 48px 56px;
  overflow-wrap: break-word;
  word-wrap: break-word;
  counter-reset: figure-counter;  /* numeración continua de figuras */
}

article.elite-report * {
  max-width: 100%;  /* protección global contra overflow */
}

article.elite-report p,
article.elite-report li,
article.elite-report blockquote {
  overflow-wrap: break-word;
  word-wrap: break-word;
  hyphens: auto;
}

article.elite-report a {
  word-break: break-all;  /* URLs largas no rompen el layout */
}

/* ── Portada ───────────────────────────────────────────────────────── */
section.cover {
  min-height: 700px;
  padding: 80px 0 64px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 20px;                                  /* espacio uniforme entre elementos */
  border-bottom: 3px solid var(--teal);
  page-break-after: always;
}

section.cover .pretitle {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin: 0;
}

section.cover h1 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 40px;
  font-weight: 800;
  line-height: 1.15;
  color: var(--teal-dark);
  margin: 8px 0 0;                            /* sin margen abajo — flex gap lo maneja */
  letter-spacing: -0.8px;
}

section.cover .subtitle {
  font-family: 'Fraunces', serif;
  font-size: 22px;
  color: var(--text);
  font-style: italic;
  margin: 0 0 24px;
}

section.cover .cover-stats {
  font-family: 'Fraunces', serif;
  font-size: 18px;
  color: var(--text);
  line-height: 1.7;
  margin: 0;
}

section.cover .metadata {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: var(--text-muted);
  line-height: 2;
  border-top: 1px solid var(--border);
  padding-top: 24px;
  margin: 24px 0 0;
}

section.cover .metadata strong {
  color: var(--text);
  font-weight: 700;
}

section.cover .classification {
  align-self: flex-start;
  padding: 4px 12px;
  background: var(--teal);
  color: white;
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  border-radius: 3px;
}

section.cover .brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 16px 0 4px;
}

section.cover .brand .brand-glyph {
  display: block;
  flex-shrink: 0;
}

section.cover .brand .wordmark {
  font-family: 'Inter', 'DM Sans', sans-serif;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -1px;
  color: #1c2230;
}

section.cover .brand .wordmark-accent {
  color: #c25a3a;
}

section.cover .disclosure {
  font-family: 'DM Sans', sans-serif;
  font-size: 11px;
  color: var(--text);
  background: var(--bg-soft);
  border-left: 3px solid var(--teal);
  padding: 14px 18px;
  margin: 28px 0 0;
  line-height: 1.65;
  font-style: italic;
}

section.cover .disclosure strong {
  color: var(--teal-dark);
  font-style: normal;
  font-weight: 700;
}

/* ── TOC ───────────────────────────────────────────────────────────── */
nav.toc {
  margin: 40px 0 64px;
  padding: 32px 40px;
  background: var(--bg-soft);
  border-left: 4px solid var(--teal);
}

nav.toc h2 {
  font-family: 'Fraunces', serif;
  font-size: 22px;
  color: var(--teal-dark);
  margin: 0 0 20px;
  font-weight: 600;
}

nav.toc ol {
  list-style: none;
  padding: 0;
  margin: 0;
  columns: 1;
}

nav.toc li {
  padding: 6px 0;
  border-bottom: 1px dashed var(--border-dim);
  font-size: 13px;
  /* Flexbox para que .num y <a> nunca se solapen aunque el numerador sea
     largo (ej. "Declaración" o "Cap. 12"). El gap garantiza separacion. */
  display: flex;
  align-items: baseline;
  gap: 14px;
}

nav.toc li .num {
  flex-shrink: 0;          /* nunca se comprime */
  min-width: 92px;         /* cubre "Declaración" + "Cap. 12" sin overlap */
  font-family: 'DM Mono', monospace;
  color: var(--teal);
  font-weight: 700;
}

nav.toc li a {
  flex: 1;                 /* el titulo ocupa el espacio restante */
  color: var(--text);
  text-decoration: none;
}

nav.toc li a:hover { color: var(--teal); }

/* ── Apertura: prólogo + síntesis ejecutiva (destacada) ──────────── */
section.declaration {
  padding: 40px 48px;
  background: linear-gradient(135deg, #e0f2f1 0%, #fafafa 100%);
  border-left: 6px solid var(--teal);
  margin: 0 -48px 64px;
}

section.declaration h2 {
  font-family: 'Fraunces', serif;
  font-size: 24px;
  color: var(--teal-dark);
  margin: 0 0 20px;
}

/* ── Capítulos ──────────────────────────────────────────────────────── */
section.chapter {
  margin: 56px 0;
  page-break-before: always;
}

section.chapter:first-of-type { page-break-before: avoid; }

section.chapter h2 {
  font-family: 'Fraunces', serif;
  font-size: 28px;
  font-weight: 800;
  color: var(--teal-dark);
  border-bottom: 2px solid var(--teal);
  padding-bottom: 12px;
  margin: 0 0 28px;
  letter-spacing: -0.5px;
}

section.chapter h2 .ch-num {
  font-family: 'DM Mono', monospace;
  font-size: 18px;
  color: var(--teal);
  font-weight: 700;
  margin-right: 12px;
  letter-spacing: 2px;
}

section.chapter h3 {
  font-family: 'Fraunces', serif;
  font-size: 17px;
  font-weight: 600;
  color: var(--teal-dark);
  margin: 28px 0 10px;
}

section.chapter h4 {
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: var(--teal);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin: 18px 0 6px;
}

section.chapter code {
  font-family: 'DM Mono', monospace;
  font-size: 0.88em;
  background: var(--bg-soft);
  padding: 1px 5px;
  border-radius: 3px;
}

section.chapter p {
  margin: 12px 0;
  text-align: justify;
  hyphens: auto;
}

section.chapter strong { font-weight: 700; color: var(--text); }

section.chapter a {
  color: var(--teal);
  text-decoration: underline;
  text-underline-offset: 2px;
}

section.chapter a:hover { color: var(--teal-dark); }

section.chapter ul, section.chapter ol {
  margin: 12px 0;
  padding-left: 24px;
}

section.chapter li { margin: 4px 0; }

section.chapter table.md-table {
  width: 100%;
  border-collapse: collapse;
  margin: 18px 0;
  font-size: 12px;
}
section.chapter table.md-table th {
  background: var(--teal);
  color: #fff;
  text-align: left;
  padding: 8px 10px;
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 11px;
  letter-spacing: 0.3px;
}
section.chapter table.md-table td {
  padding: 7px 10px;
  border-bottom: 1px solid var(--border-dim);
  vertical-align: top;
}
section.chapter table.md-table tr:nth-child(even) td { background: var(--bg-soft); }

section.chapter blockquote {
  margin: 20px 0;
  padding: 14px 20px;
  background: var(--bg-soft);
  border-left: 4px solid var(--teal);
  font-style: italic;
  color: var(--text-muted);
  font-size: 13px;
}

/* ── Visualizaciones ──────────────────────────────────────────────── */
figure.viz {
  margin: 28px 0;
  padding: 16px;
  background: var(--bg);
  border: 1px solid var(--border-dim);
  border-radius: 6px;
  page-break-inside: avoid;
  overflow: hidden;  /* contiene SVG que puedan exceder el ancho */
  max-width: 100%;
  box-sizing: border-box;
  counter-increment: figure-counter;  /* numeración automática de figuras */
}

figure.viz figcaption.viz-title::before {
  content: "Figura " counter(figure-counter) ". ";
  font-weight: 700;
  color: var(--teal);
}

figure.viz figcaption.viz-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--teal-dark);
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

figure.viz .viz-svg {
  text-align: center;
  overflow: hidden;  /* evita que texto de SVG se desborde */
  max-width: 100%;
}
figure.viz .viz-svg svg {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

figure.viz figcaption.viz-caption {
  font-size: 11px;
  color: var(--text);
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--border-dim);
  text-align: left;
  line-height: 1.55;
  overflow-wrap: break-word;
}

/* ── Findings citados ─────────────────────────────────────────────── */
.findings-cited {
  margin-top: 20px;
  padding: 14px 18px;
  background: var(--bg-soft);
  border-left: 3px solid var(--teal);
  border-radius: 4px;
}

.findings-cited h4 {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--teal-dark);
  margin: 0 0 8px;
}

.findings-cited ul { margin: 0; padding-left: 18px; }

.findings-cited li {
  margin: 6px 0;
  font-size: 12px;
  color: var(--text);
  line-height: 1.55;
}

.findings-cited .sev {
  display: inline-block;
  padding: 1px 7px;
  border-radius: 3px;
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-right: 6px;
}

/* Badges con contraste WCAG AA: texto oscurecido + borde para no depender
   solo del color (accesibilidad). */
.sev-critical { background: #fef2f2; color: #991b1b; border: 1px solid #d32f2f; }
.sev-high     { background: #fff7ed; color: #9a3412; border: 1px solid #f97316; }
.sev-medium   { background: #fefce8; color: #854d0e; border: 1px solid #ca8a04; }
.sev-low      { background: #f0fdf4; color: #166534; border: 1px solid #16a34a; }
.sev-info     { background: #eff6ff; color: #1e40af; border: 1px solid #2563eb; }

/* ── Anexos ────────────────────────────────────────────────────────── */
aside.appendix {
  margin: 64px 0;
  padding-top: 40px;
  border-top: 2px solid var(--teal);
  page-break-before: always;
}

aside.appendix h2 {
  font-family: 'Fraunces', serif;
  font-size: 24px;
  color: var(--teal-dark);
}

/* ── Bibliografía ─────────────────────────────────────────────────── */
ol.bibliography {
  list-style: none;
  padding: 0;
  counter-reset: bib;
}

/* Antes habia conflicto: padding shorthand 8px ... 32px y luego
   padding-left: 2em (~22px) lo sobreescribia, dejando que el [N]
   absoluto se solapara con el texto. Ahora padding-left consistente
   y sin text-indent negativo. */
ol.bibliography li {
  counter-increment: bib;
  padding: 10px 0 10px 44px;       /* 44px de espacio para el [NN] absoluto */
  position: relative;
  font-size: 12px;
  line-height: 1.7;
  border-bottom: 1px solid var(--border-dim);
}

ol.bibliography li::before {
  content: "[" counter(bib, decimal) "]";
  position: absolute;
  left: 0;
  top: 10px;
  width: 36px;                     /* numero contenido en 36px, deja 8px de gap */
  color: var(--teal);
  font-family: 'DM Mono', monospace;
  font-weight: 700;
  font-size: 11px;
  text-align: left;
}

/* ── Tabla anexo C (hallazgos) ──────────────────────────────────── */
table.findings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
  margin-top: 16px;
}

table.findings-table th {
  background: var(--teal);
  color: white;
  padding: 8px 10px;
  text-align: left;
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 9px;
  text-transform: uppercase;
}

table.findings-table td {
  padding: 6px 10px;
  border-bottom: 1px solid var(--border-dim);
  vertical-align: top;
}

table.findings-table tr:nth-child(even) { background: var(--bg-soft); }

/* Cuadro de hallazgos por FASE electoral y severidad — tabla nítida (reemplaza
   el gráfico SVG previo, poco legible al imprimir). */
table.phase-sev-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  margin: 8px 0 4px;
}
table.phase-sev-table th {
  background: var(--teal);
  color: #fff;
  padding: 7px 10px;
  text-align: center;
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 9px;
  letter-spacing: .5px;
  text-transform: uppercase;
}
table.phase-sev-table td {
  padding: 6px 10px;
  text-align: center;
  border-bottom: 1px solid var(--border-dim);
  font-variant-numeric: tabular-nums;
}
table.phase-sev-table tr:nth-child(even) td { background: var(--bg-soft); }
table.phase-sev-table tr.tbl-total td {
  border-top: 2px solid var(--teal);
  background: var(--bg-soft);
}
.sev-dot {
  display: inline-block;
  width: 9px; height: 9px;
  border-radius: 50%;
  margin-right: 7px;
  vertical-align: middle;
}
.sev-dot.sev-critical { background: var(--critical); }
.sev-dot.sev-high     { background: var(--high); }
.sev-dot.sev-medium   { background: var(--medium); }
.sev-dot.sev-low      { background: var(--low); }
.sev-dot.sev-info     { background: var(--info); }

/* Chips de FASE — diferencian cada temática por fase electoral con color. */
.phase-chip {
  display: inline-block;
  padding: 1px 7px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 700;
  white-space: nowrap;
}
.phase-pre   { background: #e3f2fd; color: #0d47a1; border: 1px solid #1565c0; }  /* pre-electoral — azul */
.phase-day   { background: #e0f2f1; color: #004d40; border: 1px solid #00796b; }  /* jornada — teal */
.phase-count { background: #fff3e0; color: #bf360c; border: 1px solid #e65100; }  /* escrutinio — naranja */
.phase-post  { background: #f3e5f5; color: #4a148c; border: 1px solid #6a1b9a; }  /* post-electoral — violeta */
.phase-other { background: #eceff1; color: #455a64; }   /* otros — gris */

/* ── Dashboard ejecutivo (1 página) ────────────────────────────────── */
section.executive-dashboard {
  margin: 8px 0 48px;
  padding: 28px 0 32px;
  border-top: 3px solid var(--teal);
  border-bottom: 1px solid var(--border-dim);
}
section.executive-dashboard h2 {
  font-family: 'Fraunces', serif;
  font-size: 22px;
  color: var(--teal-dark);
  margin: 0 0 18px;
}
.kpi-grid { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 26px; }
.kpi {
  flex: 1; min-width: 120px;
  background: var(--bg-soft);
  border-left: 3px solid var(--teal);
  padding: 12px 16px; border-radius: 4px;
}
.kpi-num {
  font-family: 'Fraunces', serif; font-size: 26px; font-weight: 800;
  color: var(--teal-dark); line-height: 1.1;
}
.kpi-label {
  font-family: 'DM Sans', sans-serif; font-size: 9px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted);
  margin-top: 4px;
}
.exec-viz-grid { display: flex; flex-wrap: wrap; gap: 18px; align-items: flex-start; }
.exec-viz { flex: 1; min-width: 280px; }

/* ── Cuadro de indicadores de datasets (post-TOC) ──────────────────── */
section.datasets-overview { margin: 8px 0 40px; }
section.datasets-overview h2 {
  font-family: 'Fraunces', serif; font-size: 20px; color: var(--teal-dark); margin: 0 0 6px;
}

/* ── Panorama cuantitativo (Bloque Q) ──────────────────────────────── */
section.quant-panel { margin: 8px 0 44px; }
section.quant-panel h2 {
  font-family: 'Fraunces', serif; font-size: 20px; color: var(--teal-dark); margin: 0 0 6px;
}
.quant-kpis { display: flex; flex-wrap: wrap; gap: 12px; margin: 6px 0 22px; }
.quant-kpi {
  flex: 1 1 120px; min-width: 110px; padding: 12px 14px;
  background: var(--bg-soft); border: 1px solid var(--border);
  border-left: 3px solid var(--teal); border-radius: 6px;
}
.quant-kpi-val {
  font-family: 'DM Mono', monospace; font-size: 24px; font-weight: 600;
  color: var(--teal-dark); line-height: 1.1;
}
.quant-kpi-lbl {
  font-family: 'DM Sans', sans-serif; font-size: 10px; letter-spacing: 0.5px;
  text-transform: uppercase; color: var(--text-muted); margin-top: 4px;
}
table.theme-table td { vertical-align: top; font-size: 11px; }
table.theme-table ul.theme-examples { margin: 0; padding-left: 16px; }
table.theme-table ul.theme-examples li { margin-bottom: 4px; line-height: 1.4; }
table.theme-table .theme-src { color: var(--text-muted); font-size: 10px; }

/* ── Footer ────────────────────────────────────────────────────────── */
footer.elite-footer {
  margin-top: 80px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  color: var(--text-dim);
  text-align: center;
  line-height: 1.8;
  letter-spacing: 1px;
}

/* ── Print / PDF ──────────────────────────────────────────────────── */
@page {
  size: A4;
  margin: 2.2cm 2cm 2.5cm 2cm;
  @bottom-center {
    content: counter(page) " / " counter(pages);
    font-family: 'DM Mono', monospace;
    font-size: 8pt;
    color: #64748b;
  }
}

@media print {
  html, body {
    font-size: 10pt;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;   /* preserva fondos/badges en PDF */
  }
  article.elite-report { max-width: none; padding: 0; }
  section.chapter { page-break-before: always; }
  section.executive-dashboard { page-break-after: always; }
  section.cover { min-height: auto; page-break-after: always; }
  nav.toc { page-break-after: always; }
  aside.appendix { page-break-before: always; }
  figure.viz { page-break-inside: avoid; }
  /* Evitar huérfanas/viudas y títulos al pie de página */
  p, li, blockquote { orphans: 2; widows: 2; }
  h1, h2, h3, h4 { orphans: 3; widows: 3; page-break-after: avoid; }
  table { page-break-inside: avoid; }
  a { color: var(--teal); text-decoration: none; }
}
"""


# ── Helpers ────────────────────────────────────────────────────────────
def _esc(s) -> str:
    """Escape HTML. Acepta cualquier tipo; convierte a str primero."""
    if s is None:
        return ""
    return _html.escape(str(s))


_TABLE_SEP_RE = re.compile(r'^\s*\|?[\s:\-|]+\|[\s:\-|]*$')


def _is_table_sep(s: str) -> bool:
    """¿La línea es el separador de cabecera de una tabla? (|---|:--:|)"""
    s = s.strip()
    return bool(s) and "|" in s and _TABLE_SEP_RE.match(s) is not None and "-" in s


def _split_row(s: str) -> List[str]:
    s = s.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _markdown_to_html(md: str) -> str:
    """Conversor markdown → HTML liviano, sin libs externas.
    Soporta: #### H4, ### / ## / # (h3/h4), **bold**, *em*, _em_, `code`,
    [text](url), listas -/*, blockquotes >, TABLAS pipe (| a | b |) y párrafos."""
    if not md:
        return ""
    lines = md.split("\n")
    out = []
    in_list = False
    in_blockquote = False

    def inline(s: str) -> str:
        s = _html.escape(s)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                   r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'<em>\1</em>', s)
        s = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<em>\1</em>', s)
        return s

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def close_bq():
        nonlocal in_blockquote
        if in_blockquote:
            out.append("</blockquote>")
            in_blockquote = False

    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].rstrip()
        # ── Tabla pipe: fila con | seguida de separador |---|---| ──────────
        if ("|" in s and i + 1 < n and _is_table_sep(lines[i + 1])):
            close_list(); close_bq()
            header = _split_row(s)
            rows = []
            j = i + 2
            while j < n and "|" in lines[j] and lines[j].strip():
                rows.append(_split_row(lines[j]))
                j += 1
            thead = "".join(f"<th>{inline(c)}</th>" for c in header)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                for r in rows
            )
            out.append(f'<table class="md-table"><thead><tr>{thead}</tr></thead>'
                       f"<tbody>{tbody}</tbody></table>")
            i = j
            continue
        if not s.strip():
            close_list(); close_bq()
            i += 1
            continue
        if s.startswith("#### "):
            close_list(); close_bq()
            out.append(f"<h4>{inline(s[5:])}</h4>")
        elif s.startswith("### "):
            close_list(); close_bq()
            out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "):
            close_list(); close_bq()
            out.append(f"<h3>{inline(s[3:])}</h3>")  # Forzamos h3 para mantener h2 reservado al cap
        elif s.startswith("# "):
            close_list(); close_bq()
            out.append(f"<h3>{inline(s[2:])}</h3>")
        elif s.startswith("> "):
            close_list()
            if not in_blockquote:
                out.append("<blockquote>"); in_blockquote = True
            out.append(f"<p>{inline(s[2:])}</p>")
        elif s.startswith("- ") or s.startswith("* "):
            close_bq()
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(s[2:])}</li>")
        else:
            close_list(); close_bq()
            out.append(f"<p>{inline(s)}</p>")
        i += 1

    close_list(); close_bq()
    return "\n".join(out)


def _sev_class(s: str) -> str:
    s = (s or "").lower()
    if s == "moderate": s = "medium"
    return f"sev-{s}" if s else "sev-info"


def _monitoring_days(mm, stats: Dict[str, Any]) -> int:
    """Duración del monitoreo = span CALENDARIO del período (period_start →
    period_end), no los días con hallazgos. El monitoreo es continuo; reportar
    'días con hallazgos' subestimaba (el ciclo de 1ª vuelta se monitorea desde
    antes de la elección). Fallback a days_covered si las fechas no parsean."""
    try:
        from datetime import date
        d0 = date.fromisoformat((mm.period_start or "")[:10])
        d1 = date.fromisoformat((mm.period_end or "")[:10])
        n = (d1 - d0).days + 1
        if n > 0:
            return n
    except Exception:
        pass
    return int(stats.get("days_covered", 0) or 0)


# ── RENDER HTML ────────────────────────────────────────────────────────
def render_html(
    chapters: List[EliteChapter],
    citations: List[CitationEntry],
    req: EliteReportRequest,
    stats: Dict[str, Any],
    forecast: Optional[ForecastPayload],
    country_name: str,
    report_id: str,
    generated_at: str,
    findings: Optional[List[Any]] = None,
    audit: Optional[Dict[str, Any]] = None,
    dashboard: Optional[Dict[str, Any]] = None,
    intl_series: Optional[List[Any]] = None,
) -> str:
    """Genera el HTML completo del Elite Report."""

    # Portada
    cover_html = _render_cover(req, stats, country_name, generated_at, report_id)

    # Dashboard ejecutivo (banda de KPIs, sin gráficos — esos van en Conclusiones)
    dashboard_html = _render_executive_dashboard(
        stats, req, gauge=(dashboard or {}).get("early_warning_meter"))

    # TOC
    toc_html = _render_toc(chapters, req)

    # Cuadro de indicadores de datasets (trayectoria): va DEBAJO del capítulo de
    # contexto histórico (su lugar natural — "cómo venía" el proceso).
    datasets_html = _render_datasets_overview(intl_series, req.language or "es")

    # Panorama cuantitativo (Bloque Q): cuadro por vuelta + nube temática +
    # desglose temático con ejemplos enlazados. Va inmediatamente DESPUÉS del
    # cuadro de datasets (bajo Contexto histórico).
    quant_html = _render_quant_panel(stats, req.language or "es", findings=findings)

    # Capítulos (datasets + panorama cuantitativo se insertan tras "contexto_historico")
    chapters_html_parts = []
    for ch in chapters:
        chapters_html_parts.append(_render_chapter(ch, req))
        if ch.chapter_id == "contexto_historico" and (datasets_html or quant_html):
            if datasets_html:
                chapters_html_parts.append(datasets_html)
                datasets_html = ""  # ya insertado
            if quant_html:
                chapters_html_parts.append(quant_html)
                quant_html = ""  # ya insertado
    # Fallback: si no hubo capítulo de contexto, ubicarlo tras el TOC.
    chapters_html = "\n".join(chapters_html_parts)

    # Anexo A — Metodología, limitaciones y versión del pipeline
    appendix_a = _render_appendix_a(req, stats, language=req.language or "es", audit=audit)

    # Anexo B — Bibliografía APA
    appendix_b = _render_appendix_b(citations, language=req.language or "es")

    # Anexo C — Listado completo de hallazgos con trazabilidad (si incluido)
    appendix_c = ""
    if req.include_appendix_c:
        appendix_c = _render_appendix_c(findings or [], language=req.language or "es")

    # Footer
    footer_html = _render_footer(report_id, generated_at, req.language or "es")

    # Ensamblaje
    return f"""<!DOCTYPE html>
<html lang="{req.language}">
<head>
<meta charset="utf-8">
<title>PEIRS Elite Report — {_esc(country_name)} — {req.mission_metadata.report_number}</title>
<style>{ELITE_CSS}</style>
</head>
<body>
<article class="elite-report">
{cover_html}
{dashboard_html}
{toc_html}
{datasets_html}
{quant_html}
{chapters_html}
{appendix_a}
{appendix_b}
{appendix_c}
{footer_html}
</article>
</body>
</html>"""


def _theme_examples(findings: Optional[List[Any]], category: str, k: int = 2) -> List[Any]:
    """Hasta k hallazgos representativos de una categoría (mayor priority_score)."""
    if not findings:
        return []
    sub = [f for f in findings if (_finding_attr(f, "category", "") or "") == category]
    sub.sort(key=lambda f: (_finding_attr(f, "priority_score", 0) or 0), reverse=True)
    return sub[:k]


def _finding_source_link(f: Any) -> str:
    """Primer enlace de fuente de un hallazgo consolidado (o nombre si no hay URL)."""
    srcs = _finding_attr(f, "sources", []) or []
    for s in srcs:
        su = (s.get("url") if isinstance(s, dict) else "") or ""
        sn = (s.get("name") if isinstance(s, dict) else "") or "fuente"
        if su:
            return f'<a href="{_esc(str(su))}" target="_blank" rel="noopener">{_esc(str(sn))}</a>'
    url = _finding_attr(f, "source_url", "") or ""
    name = _finding_attr(f, "source_name", "") or "fuente"
    if url:
        return f'<a href="{_esc(str(url))}" target="_blank" rel="noopener">{_esc(str(name))}</a>'
    return _esc(str(name))


def _render_theme_breakdown(by_cat: List[Dict[str, Any]], total: int,
                            findings: Optional[List[Any]], language: str) -> str:
    """Tabla 'Hallazgos por temática': categoría → conteo deduplicado ('+N') →
    severidad máx → 1-2 ejemplos representativos enlazados a su fuente. Los
    conteos son el universo CONSOLIDADO (sin repetir); Σ = total."""
    if not by_cat:
        return ""
    rows = []
    for c in by_cat:
        cat = c.get("category", "other")
        n = c.get("count", 0)
        sev = c.get("severity_max", "info")
        label = category_label(cat, language)
        exs = _theme_examples(findings, cat, k=2)
        ex_html = ""
        if exs:
            items = []
            for f in exs:
                txt = str(_finding_attr(f, "finding", "") or "").strip()
                if len(txt) > 150:
                    txt = txt[:147] + "…"
                items.append(f'<li>{_esc(txt)} <span class="theme-src">— {_finding_source_link(f)}</span></li>')
            ex_html = f'<ul class="theme-examples">{"".join(items)}</ul>'
        rows.append(
            f'<tr><td><strong>{_esc(label)}</strong></td>'
            f'<td style="text-align:right;font-family:\'DM Mono\',monospace">+{n}</td>'
            f'<td><span class="sev {_sev_class(sev)}">{_esc(sev)}</span></td>'
            f'<td>{ex_html or "—"}</td></tr>'
        )
    head = (f'<th>{t(language, "theme.col.topic")}</th>'
            f'<th style="text-align:right">{t(language, "theme.col.count")}</th>'
            f'<th>{t(language, "theme.col.sevmax")}</th>'
            f'<th>{t(language, "theme.col.examples")}</th>')
    return (
        f'<figure class="viz theme-breakdown">'
        f'<figcaption class="viz-title">{t(language, "theme.title")}</figcaption>'
        f'<table class="md-table theme-table"><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
        f'<figcaption class="viz-caption">'
        f'{t(language, "theme.caption").format(total=total)}</figcaption>'
        f'</figure>'
    )


_ORGAN_DETECT = [
    ("JNE", ["jne", "jurado nacional", "jurado electoral"]),
    ("ONPE", ["onpe", "oficina nacional de procesos"]),
    ("RENIEC", ["reniec", "registro nacional"]),
    ("Fiscalía", ["fiscal", "ministerio público"]),
    ("Poder Judicial", ["poder judicial", "corte suprema", "juez", "tribunal constitucional"]),
    ("Congreso", ["congreso", "parlamento"]),
]


def _detect_organ(text: str) -> str:
    low = (text or "").lower()
    for label, kws in _ORGAN_DETECT:
        if any(k in low for k in kws):
            return label
    return "—"


def _render_critical_events(findings: Optional[List[Any]], language: str) -> str:
    """Tabla de eventos críticos del ciclo (reemplaza la línea de tiempo que
    amontonaba puntos): fecha · evento · severidad · órgano · fuente enlazada.
    Selección: críticos y altos, ordenados por severidad y luego fecha; top 14."""
    if not findings:
        return ""
    rank = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
    crit = [f for f in findings
            if (_finding_attr(f, "severity", "") or "").lower() in ("critical", "high")]
    crit.sort(key=lambda f: (-rank.get((_finding_attr(f, "severity", "") or "").lower(), 0),
                             str(_finding_attr(f, "recorded_at", "") or "")))
    crit = crit[:14]
    if not crit:
        return ""
    rows = []
    for f in crit:
        date = str(_finding_attr(f, "recorded_at", "") or "")[:10] or "—"
        sev = (_finding_attr(f, "severity", "info") or "info").lower()
        txt = str(_finding_attr(f, "finding", "") or "").strip()
        if len(txt) > 160:
            txt = txt[:157] + "…"
        organ = _detect_organ(_finding_attr(f, "finding", "") + " " +
                              (_finding_attr(f, "source_name", "") or ""))
        rows.append(
            f'<tr><td style="white-space:nowrap">{_esc(date)}</td>'
            f'<td><span class="sev {_sev_class(sev)}">{_esc(sev)}</span></td>'
            f'<td>{_esc(organ)}</td>'
            f'<td>{_esc(txt)}</td>'
            f'<td>{_finding_source_link(f)}</td></tr>'
        )
    head = (f'<th>{t(language, "crit.col.date")}</th>'
            f'<th>{t(language, "crit.col.sev")}</th>'
            f'<th>{t(language, "crit.col.organ")}</th>'
            f'<th>{t(language, "crit.col.event")}</th>'
            f'<th>{t(language, "crit.col.source")}</th>')
    return (
        f'<figure class="viz crit-events">'
        f'<figcaption class="viz-title">{t(language, "crit.title")}</figcaption>'
        f'<table class="md-table crit-table"><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
        f'<figcaption class="viz-caption">{t(language, "crit.caption")}</figcaption>'
        f'</figure>'
    )


def _render_phase_severity_table(by_phase: Dict[str, Any], total: int,
                                 language: str) -> str:
    """Cuadro HTML determinista de hallazgos por FASE electoral y severidad
    (1ª vuelta · entre vueltas · 2ª vuelta · Total). Reemplaza el gráfico SVG
    previo por una tabla nítida e imprimible; cada columna y la fila TOTAL suman
    exactamente el universo consolidado (coherencia auditable)."""
    phases = ["1ª vuelta", "entre vueltas", "2ª vuelta"]
    phase_lbls = {
        "1ª vuelta": t(language, "quant.kpi.round1"),
        "entre vueltas": t(language, "quant.kpi.interround"),
        "2ª vuelta": t(language, "quant.kpi.round2"),
    }
    sev_keys = ["critical", "high", "medium", "low", "info"]
    cols = [by_phase.get(p) or {} for p in phases]
    header = (
        f'<th style="text-align:left">{_esc(t(language, "quant.tbl.severity"))}</th>'
        + "".join(f'<th>{_esc(phase_lbls[p])}</th>' for p in phases)
        + f'<th>{_esc(t(language, "quant.tbl.total"))}</th>'
    )
    body_rows = []
    for s in sev_keys:
        cells = [int(c.get(s, 0) or 0) for c in cols]
        row_total = sum(cells)
        body_rows.append(
            f'<tr><td style="text-align:left"><span class="sev-dot sev-{s}"></span>'
            f'{_esc(t(language, "sev." + s))}</td>'
            + "".join(f"<td>{v}</td>" for v in cells)
            + f"<td><strong>{row_total}</strong></td></tr>"
        )
    tot_cells = [int((c.get("total", 0)) or 0) for c in cols]
    total_row = (
        f'<tr class="tbl-total"><td style="text-align:left"><strong>'
        f'{_esc(t(language, "quant.tbl.total"))}</strong></td>'
        + "".join(f"<td><strong>{v}</strong></td>" for v in tot_cells)
        + f"<td><strong>{total}</strong></td></tr>"
    )
    return (
        f'<figure class="viz"><figcaption class="viz-title">'
        f'{_esc(t(language, "viz.findings_by_round.title"))}</figcaption>'
        f'<table class="phase-sev-table"><thead><tr>{header}</tr></thead>'
        f'<tbody>{"".join(body_rows)}{total_row}</tbody></table>'
        f'<figcaption class="viz-caption">'
        f'{_esc(t(language, "viz.findings_by_round.caption"))}</figcaption></figure>'
    )


def _render_quant_panel(stats: Dict[str, Any], language: str = "es",
                        findings: Optional[List[Any]] = None) -> str:
    """Panorama cuantitativo (Bloque Q): cuadro de hallazgos por vuelta/severidad
    + nube de hallazgos por temática + desglose temático con ejemplos + banda de
    KPIs de volumen. Determinista, construido sobre el corpus CONSOLIDADO
    (stats.by_round / stats.by_category). Va tras el cuadro de datasets."""
    by_round = stats.get("by_round") or {}
    by_cat = stats.get("by_category") or []
    # by_phase (3 fases) con fallback al binario by_round para compatibilidad.
    by_phase = stats.get("by_phase") or {
        "1ª vuelta": by_round.get("1ª vuelta") or {},
        "entre vueltas": {},
        "2ª vuelta": by_round.get("2ª vuelta") or {},
    }
    r1 = by_round.get("1ª vuelta") or {}
    r2 = by_round.get("2ª vuelta") or {}
    ph_i = by_phase.get("1ª vuelta") or {}
    ph_e = by_phase.get("entre vueltas") or {}
    ph_2 = by_phase.get("2ª vuelta") or {}
    if not (r1.get("total") or r2.get("total")) and not by_cat:
        return ""
    total = stats.get("consolidated_total",
                      int(r1.get("total", 0)) + int(r2.get("total", 0)))

    # 1) Cuadro por FASE electoral (tabla HTML nítida, imprimible)
    fbr_html = _render_phase_severity_table(by_phase, total, language)

    # 2) Nube temática — TODO el ciclo (todas las temáticas, sin recorte top-N)
    cc_data = {
        "categories": [
            {"label": category_label(c.get("category", "other"), language),
             "count": c.get("count", 0),
             "severity_max": c.get("severity_max", "info")}
            for c in by_cat
        ],
        "total": total,
        "_language": language,
    }

    cc_svg = render_svg("category_cloud", cc_data)

    # KPIs de volumen — consolidado + 3 fases + temáticas
    kpis = [
        (str(total), t(language, "quant.kpi.consolidated")),
        (str(int(ph_i.get("total", 0))), t(language, "quant.kpi.round1")),
        (str(int(ph_e.get("total", 0))), t(language, "quant.kpi.interround")),
        (str(int(ph_2.get("total", 0))), t(language, "quant.kpi.round2")),
        (str(len(by_cat)), t(language, "quant.kpi.topics")),
    ]
    kpi_cards = "".join(
        f'<div class="quant-kpi"><div class="quant-kpi-val">{_esc(v)}</div>'
        f'<div class="quant-kpi-lbl">{_esc(lbl)}</div></div>'
        for v, lbl in kpis
    )

    def _fig(title_key: str, caption_key: str, svg: str) -> str:
        return (
            f'<figure class="viz">'
            f'<figcaption class="viz-title">{_esc(t(language, title_key))}</figcaption>'
            f'<div class="viz-svg">{svg}</div>'
            f'<figcaption class="viz-caption">{_esc(t(language, caption_key))}</figcaption>'
            f'</figure>'
        )

    theme_html = _render_theme_breakdown(by_cat, total, findings, language)
    crit_html = _render_critical_events(findings, language)

    return (
        f'<section class="quant-panel" id="panorama-cuantitativo">'
        f'<h2>{t(language, "quant.section.title")}</h2>'
        f'<p style="color:var(--text-muted);font-size:11px;margin-bottom:14px">'
        f'{t(language, "quant.section.intro")}</p>'
        f'<div class="quant-kpis">{kpi_cards}</div>'
        f'{fbr_html}'
        f'{_fig("viz.category_cloud.title", "viz.category_cloud.caption", cc_svg)}'
        f'{theme_html}'
        f'{crit_html}'
        f'</section>'
    )


_TREND_GLYPH = {
    "up": "↑", "down": "↓", "stable": "→", "volatile": "↕",
}


def _render_datasets_overview(series_list: Optional[List[Any]], language: str = "es") -> str:
    """Cuadro de indicadores de datasets (V-Dem/FH/PEI/RSF) con TRAYECTORIA:
    valor inicial → valor actual + tendencia. Va después del TOC para mostrar
    'cómo venía' el proceso electoral. Determinista."""
    if not series_list:
        return ""
    rows = []
    multi_window = set()
    for s in series_list:
        dps = sorted((getattr(s, "datapoints", None) or []), key=lambda d: getattr(d, "year", 0))
        if not dps:
            continue
        first, last = dps[0], dps[-1]
        fy, ly = getattr(first, "year", None), getattr(last, "year", None)
        multi_window.add((fy, ly))
        # Variación: Δ (con signo) y % sobre el valor inicial. Para todos estos
        # índices, mayor = mejor → Δ<0 = deterioro (rojo), Δ>0 = mejora (verde).
        var_cell = "—"
        try:
            fv, lv = float(getattr(first, "value")), float(getattr(last, "value"))
            delta = lv - fv
            pct = (delta / fv * 100) if fv else 0.0
            color = ("#c0392b" if delta < -0.001 else
                     "#1e8449" if delta > 0.001 else "var(--text-muted)")
            sign = "+" if delta > 0 else ""
            var_cell = (f"<span style='color:{color};font-family:\"DM Mono\",monospace'>"
                        f"{sign}{delta:.2f} ({sign}{pct:.0f}%)</span>")
        except (TypeError, ValueError):
            pass
        glyph = _TREND_GLYPH.get(getattr(s, "trend_direction", "stable"), "→")
        rows.append(
            f"<tr><td>{_esc(getattr(s, 'indicator_label', ''))}</td>"
            f"<td><span style='color:var(--text-muted)'>{_esc(getattr(first, 'value', '—'))} "
            f"<small>({_esc(fy or '—')})</small></span></td>"
            f"<td><strong>{_esc(getattr(last, 'value', '—'))}</strong> "
            f"<small>({_esc(ly or '—')})</small></td>"
            f"<td>{var_cell}</td>"
            f"<td>{glyph}</td>"
            f"<td style='font-size:10px'>{_esc(getattr(s, 'unit', ''))}</td>"
            f"<td style='color:var(--text-muted);font-size:10px'>{_esc(getattr(s, 'source', ''))}</td></tr>")
    if not rows:
        return ""
    head = (f"<th>{t(language, 'intl.col.indicator')}</th>"
            f"<th>{t(language, 'intl.col.initial')}</th>"
            f"<th>{t(language, 'intl.col.current')}</th>"
            f"<th>{t(language, 'intl.col.variation')}</th>"
            f"<th>{t(language, 'intl.col.trend')}</th>"
            f"<th>{t(language, 'intl.col.unit')}</th>"
            f"<th>{t(language, 'intl.col.source')}</th>")
    # Nota: las ventanas temporales difieren por dataset (cada serie usa su rango
    # disponible). Lo explicitamos para que la comparación sea honesta.
    footnote = ""
    if len(multi_window) > 1:
        footnote = (f'<p style="color:var(--text-muted);font-size:10px;margin-top:8px">'
                    f'{t(language, "intl.windows_note")}</p>')
    return (f'<section class="datasets-overview" id="datasets-overview">'
            f'<h2>{t(language, "intl.title")}</h2>'
            f'<p style="color:var(--text-muted);font-size:11px;margin-bottom:14px">'
            f'{t(language, "intl.intro")}</p>'
            f'<table class="md-table"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>{footnote}</section>')


def _render_executive_dashboard(stats: Dict[str, Any], req: EliteReportRequest,
                                gauge: Optional[Dict[str, Any]] = None) -> str:
    """Resumen ejecutivo compacto: banda de KPIs (sin gráficos — esos viven en
    Conclusiones, para no duplicarlos)."""
    lang = req.language or "es"
    if not stats:
        return ""
    gauge = gauge or {}
    level = gauge.get("level", "—")
    score = gauge.get("score")
    risk_val = f'{_esc(level)}' + (f' · {_esc(score)}' if score is not None else "")
    # Universo CONSOLIDADO (un hecho = un hallazgo): cifra titular del informe,
    # coherente con el panel cuantitativo y el Anexo C. La severidad consolidada
    # se reconcilia sumando by_round (no el crudo, para no inflar la portada).
    raw_total = int(stats.get("total", 0))
    consolidated = int(stats.get("consolidated_total", raw_total))
    by_round = stats.get("by_round") or {}
    rounds = [v for v in by_round.values() if isinstance(v, dict)]
    cons_crit = sum(int(r.get("critical", 0)) for r in rounds) if rounds else int(stats.get("critical", 0))
    cons_high = sum(int(r.get("high", 0)) for r in rounds) if rounds else int(stats.get("high", 0))
    kpis = [
        (str(consolidated), t(lang, "exec.kpi.consolidated")),
        (str(raw_total), t(lang, "exec.kpi.captures")),
        (str(cons_crit), t(lang, "exec.kpi.critical")),
        (str(cons_high), t(lang, "exec.kpi.high")),
        (str(_monitoring_days(req.mission_metadata, stats)), t(lang, "exec.kpi.days")),
        (risk_val, t(lang, "exec.kpi.risk")),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-num">{v}</div>'
        f'<div class="kpi-label">{_esc(lbl)}</div></div>' for v, lbl in kpis)
    # Nota de trazabilidad al inicio (los totales de la base, antes enterrados en
    # el Anexo C): deja claro de entrada que cada cifra está respaldada y sellada.
    trace_note = (f'<p class="exec-trace" style="font-size:10px;color:var(--text-muted);'
                  f'margin-top:10px">{t(lang, "exec.traceability").format(consolidated=consolidated, raw=raw_total)}</p>')
    return f"""<section class="executive-dashboard" id="executive-dashboard">
<h2>{t(lang, "exec.title")}</h2>
<div class="kpi-grid">{kpi_html}</div>
{trace_note}
</section>"""


def _render_cover(req, stats, country_name, generated_at, report_id) -> str:
    mm = req.mission_metadata
    lang = req.language or "es"
    type_label = t(lang, f"report_type.{req.report_type}", req.report_type.title())
    # Conector "a" entre fechas: "Apr 1 to Apr 30" / "1 abr a 30 abr"
    period_sep = {"es": "a", "en": "to", "pt": "a"}.get(lang, "a")

    # Brand logo target glyph — embedded SVG inline para reproducibilidad print
    brand_logo_svg = (
        '<svg class="brand-glyph" xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 80 80" width="64" height="64" aria-label="Democrac.IA">'
        '<g transform="translate(4,4)">'
        '<circle cx="36" cy="36" r="32" fill="none" stroke="#1c2230" stroke-width="2.5"/>'
        '<circle cx="36" cy="36" r="18" fill="none" stroke="#1c2230" stroke-width="2.5"/>'
        '<circle cx="36" cy="36" r="5" fill="#c25a3a"/>'
        '</g></svg>'
    )

    return f"""<section class="cover">
<div class="classification">{_esc(mm.classification).upper()}</div>
<div class="brand">
{brand_logo_svg}
<span class="wordmark">Democrac<span class="wordmark-accent">.IA</span></span>
</div>
<p class="pretitle">{t(lang, "cover.pretitle")}</p>
<h1>{_esc(country_name)} — {_esc(type_label)}</h1>
<p class="subtitle">{t(lang, "cover.elections_year")} {mm.jornada_date[:4]} · {t(lang, "cover.election_day")} {_esc(mm.jornada_date)}</p>
<p class="cover-stats">
<strong>{_esc(stats.get("total", 0))}</strong> {t(lang, "cover.findings_monitored")} ·
<strong style="color:var(--critical);">{stats.get("critical", 0)} {t(lang, "cover.critical")}</strong> ·
<strong style="color:var(--high);">{stats.get("high", 0)} {t(lang, "cover.high")}</strong> ·
<strong>{_monitoring_days(mm, stats)}</strong> {t(lang, "cover.days_monitoring")}
</p>
<div class="metadata">
<strong>{t(lang, "cover.mission")}</strong> {_esc(mm.mission_name)}<br>
{(f'<strong>{t(lang, "cover.lead_observer")}</strong> {_esc(mm.lead_observer)}<br>' if mm.lead_observer else '')}
<strong>{t(lang, "cover.organization")}</strong> {_esc(mm.organization)}<br>
<strong>{t(lang, "cover.report_number")}</strong> {_esc(mm.report_number)}<br>
<strong>{t(lang, "cover.period")}</strong> {_esc(mm.period_start)} {period_sep} {_esc(mm.period_end)}<br>
<strong>{t(lang, "cover.audience")}</strong> {_esc(req.audience)}<br>
<strong>{t(lang, "cover.language")}</strong> {_esc(req.language)}<br>
<strong>{t(lang, "cover.generated")}</strong> {generated_at[:16].replace('T', ' ')} UTC<br>
<strong>Report ID:</strong> {_esc(report_id)}
</div>
<div class="disclosure">
<strong>{t(lang, "disclosure.headline")}</strong> {t(lang, "disclosure.body")}
</div>
</section>"""


def _render_toc(chapters: List[EliteChapter], req: EliteReportRequest) -> str:
    lang = req.language or "es"
    cap_prefix = t(lang, "toc.cap_prefix")
    decl_label = t(lang, "toc.declaration_label")
    items = []
    for ch in chapters:
        num = ch.number
        num_str = f"{cap_prefix}{num}" if num > 0 else (decl_label if num == -2 else "—")
        # Translate chapter title via i18n key chapter.{chapter_id}
        title_translated = t(lang, f"chapter.{ch.chapter_id}", ch.title)
        items.append(
            f'<li><span class="num">{num_str}</span> '
            f'<a href="#chapter-{ch.chapter_id}">{_esc(title_translated)}</a></li>'
        )
    # Anexos
    items.append(
        f'<li><span class="num">A</span> '
        f'<a href="#appendix-a">{t(lang, "appendix.a.title_short")}</a></li>'
    )
    items.append(
        f'<li><span class="num">B</span> '
        f'<a href="#appendix-b">{t(lang, "appendix.b.title_short")}</a></li>'
    )
    if req.include_appendix_c:
        items.append(
            f'<li><span class="num">C</span> '
            f'<a href="#appendix-c">{t(lang, "appendix.c.title_short")}</a></li>'
        )

    return f"""<nav class="toc">
<h2>{t(lang, "toc.title")}</h2>
<ol>
{chr(10).join(items)}
</ol>
</nav>"""


def _render_chapter(ch: EliteChapter, req: EliteReportRequest) -> str:
    lang = req.language or "es"
    # Sección especial para declaración preliminar
    is_declaration = ch.number == -2
    section_class = "declaration" if is_declaration else "chapter"
    ch_num_label = ""
    if ch.number > 0:
        cap_prefix = t(lang, "toc.cap_prefix").rstrip()  # "Cap." / "Ch."
        ch_num_label = f'<span class="ch-num">{cap_prefix} {ch.number:02d}</span>'

    # Translate chapter title via i18n key chapter.{chapter_id}
    chapter_title = t(lang, f"chapter.{ch.chapter_id}", ch.title)

    # Subchapter titles (## N.M ...) vienen en español por los prompts —
    # post-procesamos antes de convertir a HTML hasta traducir prompts (Sprint 4).
    narrative_md = translate_section_titles(ch.narrative, lang) if ch.narrative else ""
    narrative_html = _markdown_to_html(narrative_md) if narrative_md else '<p style="color:var(--text-dim);"><em>Contenido pendiente.</em></p>'

    # Visualizaciones
    viz_html_parts = []
    for viz in ch.visualizations:
        svg = render_svg(viz.kind, viz.data)
        viz_html_parts.append(
            f'<figure class="viz">'
            f'<figcaption class="viz-title">{_esc(viz.title)}</figcaption>'
            f'<div class="viz-svg">{svg}</div>'
            f'<figcaption class="viz-caption">{_esc(viz.caption)}</figcaption>'
            f'</figure>'
        )
    viz_html = "\n".join(viz_html_parts)

    # Findings citados (si hay)
    findings_html = ""
    if ch.findings:
        items = []
        for f in ch.findings[:8]:
            src = _esc(f.source_name or "fuente")
            finding_text = _esc((f.finding or "")[:220])
            if f.source_url:
                link = f' — <a href="{_esc(f.source_url)}" target="_blank" rel="noopener">{src}</a>'
            else:
                link = f' — {src}'
            items.append(
                f'<li><span class="sev {_sev_class(f.severity)}">{_esc(f.severity)}</span>'
                f'{finding_text}{link}</li>'
            )
        heading = t(lang, "findings_cited.heading")
        findings_html = (
            f'<div class="findings-cited">'
            f'<h4>{heading}</h4>'
            f'<ul>{chr(10).join(items)}</ul>'
            f'</div>'
        )

    # Separador explicito entre el span de numeracion y el titulo (i18n-safe).
    sep = " " if ch_num_label else ""
    return f"""<section class="{section_class}" id="chapter-{ch.chapter_id}">
<h2>{ch_num_label}{sep}{_esc(chapter_title)}</h2>
{narrative_html}
{viz_html}
{findings_html}
</section>"""


def _render_version_block(audit: Optional[Dict[str, Any]], language: str = "es") -> str:
    """Bloque de versión/trazabilidad del pipeline — pilar de auditabilidad.
    Permite verificar con qué parámetros exactos se produjo el informe."""
    if not audit:
        return ""
    clf = audit.get("classifier") or {}
    cfg = audit.get("config") or {}
    llm = (cfg.get("llm") or {})
    esc = audit.get("config", {}).get("escalation", {}) or {}
    cons = audit.get("config", {}).get("consolidation", {}) or {}
    rows = [
        (t(language, "appendix.a.ver.pipeline"), _esc(audit.get("pipeline_version", "—"))),
        (t(language, "appendix.a.ver.config"),
         f'{_esc(audit.get("config_version", "—"))} · <code>{_esc(audit.get("config_hash", "—"))}</code>'),
        (t(language, "appendix.a.ver.classifier"),
         f'{_esc(clf.get("model", "—"))} · prompt <code>{_esc(clf.get("prompt_sha256_16") or "—")}</code>'),
        (t(language, "appendix.a.ver.llm"),
         f'{_esc(llm.get("model", "—"))} · T={_esc(llm.get("temperature", "—"))}'),
        (t(language, "appendix.a.ver.thresholds"),
         f'Jaccard {_esc(cons.get("jaccard_threshold", "—"))} · '
         f'escalación ≥{_esc(esc.get("min_independent_primary", "—"))}/'
         f'≥{_esc(esc.get("confirm_independent_primary", "—"))} fuentes primarias'),
    ]
    # P2 — Calidad del clasificador (gold set) + sesgo por actor
    cq = audit.get("classifier_quality") or {}
    if cq:
        rows.append((
            t(language, "appendix.a.ver.classifier_quality"),
            f'{t(language, "appendix.a.ver.gold_set")}: {_esc(cq.get("gold_set_size", "—"))} · '
            f'cat. {_esc(cq.get("category_accuracy", "—"))} · '
            f'sev. {_esc(cq.get("severity_accuracy", "—"))} · '
            f'macro-F1 {_esc(cq.get("macro_f1", "—"))} '
            f'({_esc(cq.get("validated_at", "—"))})'))

    trs = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows)
    version_table = (f'<h3>{t(language, "appendix.a.h_version")}</h3>'
                     f'<p>{t(language, "appendix.a.p_version")}</p>'
                     f'<table class="md-table"><tbody>{trs}</tbody></table>')
    return version_table + _render_bias_block(audit.get("actor_bias"), language)


def _render_bias_block(bias: Optional[Dict[str, Any]], language: str = "es") -> str:
    """Reporte de sesgo: severidad media por tipo de actor (Marco de Calidad, P2).
    Expone si algún tipo de actor recibe sistemáticamente mayor/menor severidad."""
    if not bias or not bias.get("by_actor"):
        return ""
    _ACTOR_LABEL = {
        "state_institution": {"es": "Institución estatal", "en": "State institution", "pt": "Instituição estatal"},
        "candidate_party":   {"es": "Candidato/partido",   "en": "Candidate/party",   "pt": "Candidato/partido"},
        "media":             {"es": "Medios",              "en": "Media",             "pt": "Mídia"},
        "civil_society":     {"es": "Sociedad civil",      "en": "Civil society",     "pt": "Sociedade civil"},
        "international":      {"es": "Internacional",       "en": "International",      "pt": "Internacional"},
        "other":             {"es": "Otros",               "en": "Other",             "pt": "Outros"},
    }
    lang = (language or "es").lower()
    by_actor = bias["by_actor"]
    rows = []
    for actor, m in sorted(by_actor.items(), key=lambda kv: -kv[1].get("mean_severity", 0)):
        lbl = _ACTOR_LABEL.get(actor, {}).get(lang, actor)
        flag = " ⚠" if m.get("flagged") else ""
        delta = m.get("delta_vs_global", 0)
        delta_s = f"+{delta}" if isinstance(delta, (int, float)) and delta > 0 else str(delta)
        rows.append(
            f"<tr><td>{_esc(lbl)}{flag}</td><td>{_esc(m.get('count', 0))}</td>"
            f"<td>{_esc(m.get('mean_severity', '—'))}</td><td>{_esc(delta_s)}</td></tr>")
    head = (f"<th>{t(language, 'appendix.a.bias.actor')}</th>"
            f"<th>{t(language, 'appendix.a.bias.count')}</th>"
            f"<th>{t(language, 'appendix.a.bias.mean')}</th>"
            f"<th>{t(language, 'appendix.a.bias.delta')}</th>")
    return (f'<h3>{t(language, "appendix.a.h_bias")}</h3>'
            f'<p>{t(language, "appendix.a.p_bias").format(g=bias.get("global_mean_severity", "—"))}</p>'
            f'<table class="md-table"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def _render_appendix_a(req: EliteReportRequest, stats: Dict[str, Any],
                       language: str = "es", audit: Optional[Dict[str, Any]] = None) -> str:
    n_findings = stats.get("total", 0)
    li_phase = t(language, "appendix.a.li_phaseorganizer").format(n=n_findings)
    return f"""<aside class="appendix" id="appendix-a">
<h2>{t(language, "appendix.a.title")}</h2>
<h3>{t(language, "appendix.a.h_pipeline")}</h3>
<p>{t(language, "appendix.a.intro")}</p>
<ol>
<li>{t(language, "appendix.a.li_eliteloader")}</li>
<li>{li_phase}</li>
<li>{t(language, "appendix.a.li_crossref")}</li>
<li>{t(language, "appendix.a.li_composer")}</li>
<li>{t(language, "appendix.a.li_visualizer")}</li>
</ol>
<h3>{t(language, "appendix.a.h_sources")}</h3>
<p>{t(language, "appendix.a.p_sources")}</p>
<h3>{t(language, "appendix.a.h_sampling")}</h3>
<p>{t(language, "appendix.a.p_sampling")}</p>
<h3>{t(language, "appendix.a.h_limits")}</h3>
<ul>
<li>{t(language, "appendix.a.li_lim_bias")}</li>
<li>{t(language, "appendix.a.li_lim_classifier")}</li>
<li>{t(language, "appendix.a.li_lim_llm")}</li>
<li>{t(language, "appendix.a.li_lim_horizon")}</li>
<li>{t(language, "appendix.a.li_lim_no_replace")}</li>
</ul>
{_render_version_block(audit, language)}
</aside>"""


def _render_appendix_b(citations: List[CitationEntry], language: str = "es") -> str:
    if not citations:
        return ""
    items = []
    for c in citations:
        url_link = ""
        if c.url:
            url_link = f' <a href="{_esc(c.url)}" target="_blank" rel="noopener" style="font-family: \'DM Mono\', monospace; font-size:9px;">[URL]</a>'
        items.append(f'<li>{_esc(c.apa_formatted)}{url_link}</li>')

    return f"""<aside class="appendix" id="appendix-b">
<h2>{t(language, "appendix.b.title")}</h2>
<p style="color:var(--text-muted); font-size:11px; margin-bottom:20px;">{len(citations)} {t(language, "appendix.b.intro")}</p>
<ol class="bibliography">
{chr(10).join(items)}
</ol>
</aside>"""


_APPENDIX_C_MAX_ROWS = 2500  # tope de seguridad para HTML/PDF; se nota si trunca


def _finding_attr(f: Any, attr: str, default: str = "") -> Any:
    """Lee un atributo tanto de FindingRef (pydantic) como de dict."""
    if isinstance(f, dict):
        return f.get(attr, default)
    return getattr(f, attr, default)


# Fase electoral → (clase de color, clave i18n). Diferencia cada temática por
# fase con color en el Anexo C. Se matchea por substring del campo `phase`.
_PHASE_RULES = [
    ("campaign", "pre", "phase.pre_electoral"),
    ("pre", "pre", "phase.pre_electoral"),
    ("election_day", "day", "phase.election_day"),
    ("jornada", "day", "phase.election_day"),
    ("count", "count", "phase.count"),
    ("escrutinio", "count", "phase.count"),
    ("computo", "count", "phase.count"),
    ("post", "post", "phase.post_electoral"),
]


def _phase_chip(phase: Any, language: str = "es") -> str:
    p = str(phase or "").lower()
    cls, key = "other", "phase.other"
    for needle, c, k in _PHASE_RULES:
        if needle in p:
            cls, key = c, k
            break
    _lbl = _esc(t(language, key, "—"))
    return f'<span class="phase-chip phase-{cls}" aria-label="Fase: {_lbl}">{_lbl}</span>'


def _evidence_base_note(language: str = "es") -> str:
    """Nota que cita la base de prueba completa archivada (evidence_base/) con sus
    sha256, para dejar claro que el Anexo C es una MUESTRA y que la base íntegra y
    verificable respalda cada cifra. Best-effort: si no hay manifest, no estorba."""
    try:
        manifest = _Path(__file__).resolve().parents[4] / "evidence_base" / "manifest.json"
        if not manifest.exists():
            return ""
        m = _json.loads(manifest.read_text(encoding="utf-8"))
        files = m.get("files", {})
        shas = " · ".join(f"{name}: <code>{(info.get('sha256') or '')[:12]}…</code>"
                          for name, info in files.items())
        return (f'<p class="evidence-note" style="font-size:10px;color:var(--text-muted);'
                f'border-top:1px solid var(--border);padding-top:8px;margin-top:10px">'
                f'{t(language, "appendix.c.evidence_base").format(dedup=m.get("dedup_total", "—"), raw=m.get("raw_total", "—"))}'
                f' {shas}</p>')
    except Exception:
        return ""


def _render_appendix_c(findings: List[Any], language: str = "es") -> str:
    """Anexo C — listado completo de hallazgos del Hunter con TRAZABILIDAD.

    Una fila por hallazgo: fecha · severidad · categoría · hallazgo · fuente
    (enlazada a su URL primaria). Es el respaldo auditable del informe: cada
    afirmación del corpus es rastreable hasta su fuente."""
    total = len(findings or [])
    if total == 0:
        # Estado retrospectivo honesto, sin lenguaje de "pendiente".
        return f"""<aside class="appendix" id="appendix-c">
<h2>{t(language, "appendix.c.title")}</h2>
<p style="color:var(--text-muted); font-size:11px;">{t(language, "appendix.c.empty")}</p>
</aside>"""

    rows = findings[:_APPENDIX_C_MAX_ROWS]
    cols = (
        t(language, "appendix.c.col.n"), t(language, "appendix.c.col.date"),
        t(language, "appendix.c.col.phase"), t(language, "appendix.c.col.severity"),
        t(language, "appendix.c.col.category"), t(language, "appendix.c.col.finding"),
        t(language, "appendix.c.col.source"),
    )
    head = "".join(f"<th>{_esc(c)}</th>" for c in cols)

    body_rows = []
    for i, f in enumerate(rows, 1):
        date = str(_finding_attr(f, "recorded_at", "") or "")[:10] or "—"
        sev = str(_finding_attr(f, "severity", "info") or "info").lower()
        cat = _finding_attr(f, "category", "") or "—"
        phase_chip = _phase_chip(_finding_attr(f, "phase", ""), language)
        text = str(_finding_attr(f, "finding", "") or "").strip()
        if len(text) > 240:
            text = text[:237] + "…"
        # Fuentes consolidadas: un evento = todas sus fuentes en la misma celda.
        srcs = _finding_attr(f, "sources", []) or []
        url = _finding_attr(f, "source_url", "") or ""
        label = (_finding_attr(f, "source_title", "")
                 or _finding_attr(f, "source_name", "") or "—")
        links = []
        for s in srcs:
            su = (s.get("url") if isinstance(s, dict) else "") or ""
            sn = (s.get("name") if isinstance(s, dict) else "") or "fuente"
            if su:
                links.append(f'<a href="{_esc(str(su))}" target="_blank" '
                             f'rel="noopener">{_esc(str(sn))}</a>')
        if links:
            source = " · ".join(links)
        elif url:
            source = (f'<a href="{_esc(str(url))}" target="_blank" '
                      f'rel="noopener">{_esc(str(label))}</a>')
        else:
            source = _esc(str(label))
        body_rows.append(
            f"<tr><td>{i}</td><td>{_esc(date)}</td><td>{phase_chip}</td>"
            f'<td><span class="sev {_sev_class(sev)}" aria-label="Severidad: {_esc(sev)}">{_esc(sev)}</span></td>'
            f"<td>{_esc(str(cat))}</td><td>{_esc(text)}</td><td>{source}</td></tr>"
        )

    truncated = ""
    if total > _APPENDIX_C_MAX_ROWS:
        truncated = (f'<p style="color:var(--text-muted); font-size:10px;">'
                     f'{t(language, "appendix.c.truncated").format(shown=_APPENDIX_C_MAX_ROWS, total=total)}</p>')

    return f"""<aside class="appendix" id="appendix-c">
<h2>{t(language, "appendix.c.title")}</h2>
<p style="font-size:11px;">{t(language, "appendix.c.intro").format(n=total)}</p>
<table class="findings-table">
<thead><tr>{head}</tr></thead>
<tbody>
{chr(10).join(body_rows)}
</tbody>
</table>
{truncated}
{_evidence_base_note(language)}
</aside>"""


def _render_footer(report_id: str, generated_at: str, language: str = "es") -> str:
    return f"""<footer class="elite-footer">
<strong>{t(language, "disclosure.headline")}</strong>
{t(language, "footer.disclosure_short")}<br>
PEIRS Elite Report · {report_id} · {generated_at[:16].replace('T', ' ')} UTC ·
{t(language, "footer.pipeline_meta")}
</footer>"""


# ── RENDER MARKDOWN ────────────────────────────────────────────────────
def render_markdown(
    chapters: List[EliteChapter],
    citations: List[CitationEntry],
    req: EliteReportRequest,
    stats: Dict[str, Any],
    country_name: str,
) -> str:
    """Versión Markdown del informe (para archivado/conversión)."""
    mm = req.mission_metadata
    lang = req.language or "es"
    period_sep = {"es": "a", "en": "to", "pt": "a"}.get(lang, "a")
    cap_prefix = t(lang, "toc.cap_prefix").rstrip()
    decl_label = t(lang, "toc.declaration_label")
    viz_label = {"es": "Visualización", "en": "Visualization", "pt": "Visualização"}.get(lang, "Visualización")
    pending_label = {"es": "*Contenido pendiente.*", "en": "*Content pending.*",
                     "pt": "*Conteúdo pendente.*"}.get(lang, "*Contenido pendiente.*")

    lines = [
        f"# {t(lang, 'md.header_title')} — {country_name}",
        "",
        f"*{req.audience} · {req.language} · {req.report_type} · {mm.report_number}*",
        "",
        "---",
        "",
        f"**{t(lang, 'cover.mission')}** {mm.mission_name}  ",
        *([f"**{t(lang, 'cover.lead_observer')}** {mm.lead_observer}  "] if mm.lead_observer else []),
        f"**{t(lang, 'cover.period')}** {mm.period_start} {period_sep} {mm.period_end}  ",
        f"**{t(lang, 'cover.election_day')}** {mm.jornada_date}  ",
        f"**{t(lang, 'md.classification_label')}** {mm.classification}  ",
        "",
        f"**{stats.get('total', 0)}** {t(lang, 'cover.findings_monitored')} · "
        f"**{stats.get('critical', 0)}** {t(lang, 'cover.critical')} · "
        f"**{stats.get('high', 0)}** {t(lang, 'cover.high')} · "
        f"**{_monitoring_days(mm, stats)}** {t(lang, 'cover.days_monitoring')}.",
        "",
        "---",
        "",
    ]
    for ch in chapters:
        ch_title = t(lang, f"chapter.{ch.chapter_id}", ch.title)
        if ch.number > 0:
            header = f"## {cap_prefix} {ch.number:02d}. {ch_title}"
        elif ch.number == -2:
            header = f"## {decl_label} — {ch_title}"
        else:
            header = f"## {ch_title}"
        lines.append(header)
        lines.append("")
        narrative_md = translate_section_titles(ch.narrative, lang) if ch.narrative else ""
        lines.append(narrative_md or pending_label)
        lines.append("")
        for viz in ch.visualizations:
            lines.append(f"> **[{viz_label} — {viz.kind}]** {viz.title}")
            if viz.caption:
                lines.append(f"> *{viz.caption}*")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"## {t(lang, 'appendix.b.title')}")
    lines.append("")
    for c in citations:
        lines.append(f"- {c.apa_formatted}")
    return "\n".join(lines)
