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
    appendix_a = _render_appendix_a(req, stats)

    # Anexo B — Bibliografía APA
    appendix_b = _render_appendix_b(citations)

    # Anexo C — Listado de hallazgos (si incluido)
    appendix_c = ""
    if req.include_appendix_c:
        # Los findings vienen de chapters o del output; en orquestador pasamos bundle
        appendix_c = _render_appendix_c_placeholder()

    # Footer
    footer_html = _render_footer(report_id, generated_at)

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
    type_labels = {
        "pre_electoral": "Informe Pre-Electoral",
        "jornada": "Informe de Jornada",
        "preliminary": "Informe Preliminar",
        "final": "Informe Final",
        "ad_hoc": "Informe Ad-hoc",
    }
    type_label = type_labels.get(req.report_type, req.report_type.title())

    return f"""<section class="cover">
<div class="classification">{_esc(mm.classification).upper()}</div>
<p class="pretitle">Misión de Observación Electoral · PEIRS</p>
<h1>{_esc(country_name)} — {_esc(type_label)}</h1>
<p class="subtitle">Elecciones {mm.jornada_date[:4]} · Jornada del {_esc(mm.jornada_date)}</p>
<p class="cover-stats">
<strong>{_esc(stats.get("total", 0))}</strong> hallazgos monitoreados ·
<strong style="color:var(--critical);">{stats.get("critical", 0)} críticos</strong> ·
<strong style="color:var(--high);">{stats.get("high", 0)} altos</strong> ·
<strong>{stats.get("days_covered", 0)} días</strong> de monitoreo continuo
</p>
<div class="metadata">
<strong>Misión:</strong> {_esc(mm.mission_name)}<br>
<strong>Observadora responsable:</strong> {_esc(mm.lead_observer)}<br>
<strong>Organización emisora:</strong> {_esc(mm.organization)}<br>
<strong>N° de informe:</strong> {_esc(mm.report_number)}<br>
<strong>Período cubierto:</strong> {_esc(mm.period_start)} a {_esc(mm.period_end)}<br>
<strong>Audiencia:</strong> {_esc(req.audience)}<br>
<strong>Idioma:</strong> {_esc(req.language)}<br>
<strong>Generado:</strong> {generated_at[:16].replace('T', ' ')} UTC<br>
<strong>Report ID:</strong> {_esc(report_id)}
</div>
</section>"""


def _render_toc(chapters: List[EliteChapter], req: EliteReportRequest) -> str:
    items = []
    for ch in chapters:
        num = ch.number
        num_str = f"Cap. {num}" if num > 0 else ("Declaración" if num == -2 else "—")
        # Espacio explicito entre <span> y <a> para que la conversion HTML→MD
        # (markitdown) no los fusione: "Declaracion[Declaracion preliminar]".
        items.append(
            f'<li><span class="num">{num_str}</span> '
            f'<a href="#chapter-{ch.chapter_id}">{_esc(ch.title)}</a></li>'
        )
    # Anexos
    items.append('<li><span class="num">A</span> <a href="#appendix-a">Metodología técnica</a></li>')
    items.append('<li><span class="num">B</span> <a href="#appendix-b">Bibliografía APA</a></li>')
    if req.include_appendix_c:
        items.append('<li><span class="num">C</span> <a href="#appendix-c">Hallazgos completos</a></li>')

    return f"""<nav class="toc">
<h2>Tabla de contenidos</h2>
<ol>
{chr(10).join(items)}
</ol>
</nav>"""


def _render_chapter(ch: EliteChapter, req: EliteReportRequest) -> str:
    # Sección especial para declaración preliminar
    is_declaration = ch.number == -2
    section_class = "declaration" if is_declaration else "chapter"
    ch_num_label = ""
    if ch.number > 0:
        ch_num_label = f'<span class="ch-num">Cap. {ch.number:02d}</span>'

    narrative_html = _markdown_to_html(ch.narrative) if ch.narrative else '<p style="color:var(--text-dim);"><em>Contenido pendiente.</em></p>'

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
        findings_html = (
            f'<div class="findings-cited">'
            f'<h4>Hallazgos citados</h4>'
            f'<ul>{chr(10).join(items)}</ul>'
            f'</div>'
        )

    # Separador explicito entre el span de numeracion y el titulo. En HTML el
    # margin-right del span lo disimula, pero la conversion a MD via markitdown
    # los fusiona ("Cap. 01Contexto historico"). Un espacio ASCII entre tags
    # se preserva en MD y no afecta el render HTML.
    sep = " " if ch_num_label else ""
    return f"""<section class="{section_class}" id="chapter-{ch.chapter_id}">
<h2>{ch_num_label}{sep}{_esc(ch.title)}</h2>
{narrative_html}
{viz_html}
{findings_html}
</section>"""


def _render_appendix_a(req: EliteReportRequest, stats: Dict[str, Any]) -> str:
    return f"""<aside class="appendix" id="appendix-a">
<h2>Anexo A — Metodología técnica</h2>
<h3>Pipeline PEIRS</h3>
<p>Este informe fue generado con el sistema DemocracIA / PEIRS (Predictive Electoral Integrity &amp; Risk System), aplicando el pipeline de 6 etapas:</p>
<ol>
<li><strong>EliteLoader</strong> — carga paralela de evidencia: entries del Hunter, alertas dispatchadas, corpus constitucionalista RAG filtrado por país, y series históricas V-Dem, Freedom House, PEI, RSF. Cache TTL 1 hora.</li>
<li><strong>PhaseOrganizer</strong> — agrupa {stats.get('total', 0)} hallazgos en las 9 fases del ciclo electoral según fecha y calendario electoral.</li>
<li><strong>CrossReferenceBuilder</strong> — linkea hallazgos high/critical con artículos del marco normativo (Constitución, LOE, LOP, jurisprudencia, ICCPR, CADH, CDI) mediante mapeo curado de 14 categorías.</li>
<li><strong>PredictiveEngine</strong> — motor híbrido de reglas deterministas + Claude Sonnet 4.6 para estimar escenarios probabilísticos de dinámica institucional post-proceso.</li>
<li><strong>ChapterComposer</strong> — 12 prompts especializados con prompt caching de Anthropic, concurrency limit 4. Cada capítulo se genera con contexto compartido y datos específicos.</li>
<li><strong>Visualizer + Renderer</strong> — SVG server-side con paleta institucional, HTML responsive, PDF A4 con tipografía Fraunces+DM Sans+DM Mono.</li>
</ol>
<h3>Fuentes Hunter</h3>
<p>Monitoreo RSS cada 4 horas sobre medios peruanos: Andina, El Comercio, Gestión, IDL-Reporteros, RPP Noticias. Clasificación automática con Claude Sonnet 4.6. Dedupe semántico por (categoría, URL normalizada, fecha). Priorización ponderada: severidad × recencia (decay exp. 3 días) × credibilidad de fuente.</p>
<h3>Limitaciones reconocidas</h3>
<ul>
<li>Sesgo de fuentes: los medios monitoreados son mayoritariamente limeños; la cobertura regional es indirecta.</li>
<li>Horizonte predictivo: las estimaciones del PredictiveEngine cubren 2-4 semanas. Más allá pierden precisión.</li>
<li>No reemplaza observación presencial: este informe complementa, no sustituye, las misiones oficiales de observación.</li>
</ul>
</aside>"""


def _render_appendix_b(citations: List[CitationEntry]) -> str:
    if not citations:
        return ""
    items = []
    for c in citations:
        url_link = ""
        if c.url:
            url_link = f' <a href="{_esc(c.url)}" target="_blank" rel="noopener" style="font-family: \'DM Mono\', monospace; font-size:9px;">[URL]</a>'
        items.append(f'<li>{_esc(c.apa_formatted)}{url_link}</li>')

    return f"""<aside class="appendix" id="appendix-b">
<h2>Anexo B — Bibliografía (APA 7)</h2>
<p style="color:var(--text-muted); font-size:11px; margin-bottom:20px;">{len(citations)} referencias ordenadas alfabéticamente.</p>
<ol class="bibliography">
{chr(10).join(items)}
</ol>
</aside>"""


def _render_appendix_c_placeholder() -> str:
    return """<aside class="appendix" id="appendix-c">
<h2>Anexo C — Hallazgos completos</h2>
<p style="color:var(--text-muted); font-size:11px;">Listado completo de hallazgos del Hunter disponible en formato Markdown descargable. Incluye entry_id, fecha, severidad, categoría, finding, medio, URL y priority_score.</p>
</aside>"""


def _render_footer(report_id: str, generated_at: str) -> str:
    return f"""<footer class="elite-footer">
DemocracIA · PEIRS Elite Report · {report_id} · {generated_at[:16].replace('T', ' ')} UTC<br>
Generado con pipeline de 6 etapas · SVG server-side · Citas APA 7 · Compatible con estándares OEA / EU EOM / Carter Center / IDEA
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
    lines = [
        f"# PEIRS Elite Report — {country_name}",
        "",
        f"*{req.audience} · {req.language} · {req.report_type} · {mm.report_number}*",
        "",
        "---",
        "",
        f"**Misión:** {mm.mission_name}  ",
        f"**Observadora:** {mm.lead_observer}  ",
        f"**Período:** {mm.period_start} a {mm.period_end}  ",
        f"**Jornada:** {mm.jornada_date}  ",
        f"**Clasificación:** {mm.classification}  ",
        "",
        f"**Cifras:** {stats.get('total', 0)} hallazgos · "
        f"{stats.get('critical', 0)} críticos · {stats.get('high', 0)} altos · "
        f"{stats.get('days_covered', 0)} días de monitoreo.",
        "",
        "---",
        "",
    ]
    for ch in chapters:
        ch_num = f"Cap. {ch.number:02d}" if ch.number > 0 else ("Declaración" if ch.number == -2 else "")
        header = f"## {ch_num}. {ch.title}" if ch_num else f"## {ch.title}"
        lines.append(header)
        lines.append("")
        lines.append(ch.narrative or "*Contenido pendiente.*")
        lines.append("")
        for viz in ch.visualizations:
            lines.append(f"> **[Visualización — {viz.kind}]** {viz.title}")
            if viz.caption:
                lines.append(f"> *{viz.caption}*")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Anexo B — Bibliografía")
    lines.append("")
    for c in citations:
        lines.append(f"- {c.apa_formatted}")
    return "\n".join(lines)
