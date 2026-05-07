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
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.elite_report.models import (
    EliteChapter,
    EliteReportRequest,
    CitationEntry,
    ForecastPayload,
    VizSpec,
)
from agents.elite_report.visualizer import render_svg
from agents.elite_report.i18n import t
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

@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@400;600;800&family=DM+Sans:wght@400;500;700&family=DM+Mono:wght@400;500;700&display=swap');

* { box-sizing: border-box; }

html, body {
  margin: 0; padding: 0;
  font-family: 'DM Sans', -apple-system, sans-serif;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text);
  background: var(--bg);
  overflow-x: hidden;  /* evita scroll horizontal accidental */
}

article.elite-report {
  max-width: 880px;
  margin: 0 auto;
  padding: 48px 56px;
  overflow-wrap: break-word;
  word-wrap: break-word;
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

/* ── Declaración preliminar (destacada) ──────────────────────────── */
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
  font-size: 10px;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 8px;
  text-align: center;
  line-height: 1.5;
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

.sev-critical { background: #fef2f2; color: var(--critical); }
.sev-high     { background: #fff7ed; color: var(--high); }
.sev-medium   { background: #fefce8; color: #b45309; }
.sev-low      { background: #f0fdf4; color: var(--low); }
.sev-info     { background: #eff6ff; color: var(--info); }

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
}

@media print {
  html, body { font-size: 10pt; }
  article.elite-report { max-width: none; padding: 0; }
  section.chapter { page-break-before: always; }
  section.cover { min-height: auto; page-break-after: always; }
  nav.toc { page-break-after: always; }
  aside.appendix { page-break-before: always; }
  figure.viz { page-break-inside: avoid; }
  a { color: var(--teal); text-decoration: none; }
}
"""


# ── Helpers ────────────────────────────────────────────────────────────
def _esc(s) -> str:
    """Escape HTML. Acepta cualquier tipo; convierte a str primero."""
    if s is None:
        return ""
    return _html.escape(str(s))


def _markdown_to_html(md: str) -> str:
    """Conversor markdown → HTML liviano, sin libs externas.
    Soporta: ## H2 y ### H3, **bold**, *em*, _em_, [text](url), listas -/*,
    blockquotes >, párrafos separados por líneas en blanco."""
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

    for line in lines:
        s = line.rstrip()
        if not s.strip():
            close_list(); close_bq()
            continue
        if s.startswith("### "):
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

    close_list(); close_bq()
    return "\n".join(out)


def _sev_class(s: str) -> str:
    s = (s or "").lower()
    if s == "moderate": s = "medium"
    return f"sev-{s}" if s else "sev-info"


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
) -> str:
    """Genera el HTML completo del Elite Report."""

    # Portada
    cover_html = _render_cover(req, stats, country_name, generated_at, report_id)

    # TOC
    toc_html = _render_toc(chapters, req)

    # Capítulos
    chapters_html_parts = []
    for ch in chapters:
        chapters_html_parts.append(_render_chapter(ch, req))
    chapters_html = "\n".join(chapters_html_parts)

    # Anexo A — Metodología (breve fijo)
    appendix_a = _render_appendix_a(req, stats, language=req.language or "es")

    # Anexo B — Bibliografía APA
    appendix_b = _render_appendix_b(citations, language=req.language or "es")

    # Anexo C — Listado de hallazgos (si incluido)
    appendix_c = ""
    if req.include_appendix_c:
        # Los findings vienen de chapters o del output; en orquestador pasamos bundle
        appendix_c = _render_appendix_c_placeholder(language=req.language or "es")

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
{toc_html}
{chapters_html}
{appendix_a}
{appendix_b}
{appendix_c}
{footer_html}
</article>
</body>
</html>"""


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
<strong>{stats.get("days_covered", 0)}</strong> {t(lang, "cover.days_monitoring")}
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


def _render_appendix_a(req: EliteReportRequest, stats: Dict[str, Any],
                       language: str = "es") -> str:
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
<li>{t(language, "appendix.a.li_predictive")}</li>
<li>{t(language, "appendix.a.li_composer")}</li>
<li>{t(language, "appendix.a.li_visualizer")}</li>
</ol>
<h3>{t(language, "appendix.a.h_sources")}</h3>
<p>{t(language, "appendix.a.p_sources")}</p>
<h3>{t(language, "appendix.a.h_limits")}</h3>
<ul>
<li>{t(language, "appendix.a.li_lim_bias")}</li>
<li>{t(language, "appendix.a.li_lim_horizon")}</li>
<li>{t(language, "appendix.a.li_lim_no_replace")}</li>
</ul>
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


def _render_appendix_c_placeholder(language: str = "es") -> str:
    return f"""<aside class="appendix" id="appendix-c">
<h2>{t(language, "appendix.c.title")}</h2>
<p style="color:var(--text-muted); font-size:11px;">{t(language, "appendix.c.placeholder")}</p>
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
        f"**{stats.get('days_covered', 0)}** {t(lang, 'cover.days_monitoring')}.",
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
