"""PDF renderer — weasyprint (primario) → xhtml2pdf (fallback).

weasyprint produce PDF de calidad editorial pero requiere libs del sistema
(Cairo, Pango, GDK-Pixbuf). En Railway puede no estar disponible — en ese
caso caemos a xhtml2pdf que es pure-Python con CSS más limitado pero
suficiente para producción.

Uso:
    pdf_path = render_pdf(html_content, report_id="abc123")
    # → reports/elite/abc123/report.pdf
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


REPORTS_DIR = Path(__file__).parent.parent.parent.parent.parent / "reports" / "elite"


def render_pdf(html: str, report_id: str) -> Optional[str]:
    """Renderiza HTML a PDF.

    Intenta weasyprint primero. Si falla (libs sistema faltantes), cae a xhtml2pdf.
    Retorna el path del archivo generado, o None si ambos fallaron.
    """
    base_dir = REPORTS_DIR / report_id
    base_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = base_dir / "report.pdf"

    # 1. Primer intento: weasyprint
    try:
        from weasyprint import HTML, CSS  # type: ignore
        HTML(string=html).write_pdf(str(pdf_path))
        return str(pdf_path)
    except Exception as e_wp:
        # 2. Fallback: xhtml2pdf (ya instalado, ver build_pdf.py en el root)
        try:
            from xhtml2pdf import pisa  # type: ignore
            with open(pdf_path, "wb") as out:
                result = pisa.CreatePDF(html, dest=out, encoding="utf-8")
            if result.err:
                return None
            return str(pdf_path)
        except Exception as e_xh:
            # Ambos fallaron
            print(f"[PDFRenderer] Ambos motores fallaron: weasyprint={e_wp}, xhtml2pdf={e_xh}")
            return None
