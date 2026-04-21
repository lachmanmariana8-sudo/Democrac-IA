"""Renderizadores del Elite Report: HTML institucional + PDF + Markdown.

- html_renderer.py: genera HTML completo + Markdown estructurado
- pdf_renderer.py: genera PDF (weasyprint primario, xhtml2pdf fallback)
"""
from agents.elite_report.renderer.html_renderer import render_html, render_markdown
from agents.elite_report.renderer.pdf_renderer import render_pdf

__all__ = ["render_html", "render_markdown", "render_pdf"]
