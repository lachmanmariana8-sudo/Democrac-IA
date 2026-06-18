"""Formateo del artículo de prensa a HTML autónomo (web-ready).

Markdown ligero (párrafos, **negrita**, *itálica*, ## subtítulos) → HTML, dentro
de un <article> con titular, bajada, cuerpo y firma. Sin dependencias externas.
"""
from __future__ import annotations

import html as _html
import re

_BYLINE_LABEL = {"es": "Por", "en": "By", "pt": "Por"}


def _esc(s: str) -> str:
    return _html.escape(s or "", quote=False)


def _inline(text: str) -> str:
    """Negrita/itálica inline sobre texto ya escapado."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def body_markdown_to_html(md: str) -> str:
    """Convierte el cuerpo (párrafos + subtítulos ##) a HTML."""
    parts = []
    for block in re.split(r"\n\s*\n", (md or "").strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith("### "):
            parts.append(f"<h3>{_inline(_esc(block[4:].strip()))}</h3>")
        elif block.startswith("## "):
            parts.append(f"<h2>{_inline(_esc(block[3:].strip()))}</h2>")
        else:
            para = _inline(_esc(block)).replace("\n", "<br>")
            parts.append(f"<p>{para}</p>")
    return "\n".join(parts)


def render_article_html(headline: str, standfirst: str, body_md: str,
                        byline: str = "Democrac.IA", language: str = "es",
                        generated_at: str = "") -> str:
    """Artículo HTML autónomo, estilo nota de prensa online."""
    lang = (language or "es").lower()
    by_label = _BYLINE_LABEL.get(lang, "Por")
    date_str = (generated_at or "")[:10]
    body_html = body_markdown_to_html(body_md)
    css = (
        "article.press{max-width:720px;margin:0 auto;font-family:Georgia,"
        "'Times New Roman',serif;color:#1a1a1a;line-height:1.7;padding:24px}"
        "article.press h1{font-size:30px;line-height:1.2;margin:0 0 12px;"
        "font-family:'Helvetica Neue',Arial,sans-serif}"
        "article.press .standfirst{font-size:18px;color:#444;font-style:italic;"
        "margin:0 0 18px}"
        "article.press .byline{font-size:13px;color:#666;border-top:1px solid #ddd;"
        "border-bottom:1px solid #ddd;padding:8px 0;margin:0 0 22px;"
        "font-family:'Helvetica Neue',Arial,sans-serif;letter-spacing:.3px}"
        "article.press p{margin:0 0 16px;font-size:17px}"
        "article.press h2{font-size:21px;margin:26px 0 10px;"
        "font-family:'Helvetica Neue',Arial,sans-serif}"
        "article.press .sig{margin-top:28px;font-size:13px;color:#888;"
        "font-style:italic}"
    )
    byline_line = f"{by_label} <strong>{_esc(byline)}</strong>"
    if date_str:
        byline_line += f" · {_esc(date_str)}"
    sig = ("Análisis producido por Democrac.IA PEIRS — plataforma apartidaria de "
           "monitoreo electoral.") if lang == "es" else (
           "Analysis produced by Democrac.IA PEIRS — a non-partisan electoral "
           "monitoring platform." if lang == "en" else
           "Análise produzida pela Democrac.IA PEIRS — plataforma apartidária de "
           "monitoramento eleitoral.")
    return (
        f"<style>{css}</style>"
        f'<article class="press">'
        f"<h1>{_inline(_esc(headline))}</h1>"
        f'<p class="standfirst">{_inline(_esc(standfirst))}</p>'
        f'<div class="byline">{byline_line}</div>'
        f"{body_html}"
        f'<p class="sig">{_esc(sig)}</p>'
        f"</article>"
    )
