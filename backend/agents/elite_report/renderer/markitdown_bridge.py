"""Puente hacia microsoft/markitdown para convertir el HTML del Elite Report
en Markdown de alta fidelidad.

markitdown es una librería oficial de Microsoft (https://github.com/microsoft/markitdown)
que convierte múltiples formatos (HTML, PDF, DOCX, PPTX, XLSX, imágenes, …)
a Markdown limpio y legible. La usamos para producir el archivo `.md` que
el usuario puede descargar, con mejor fidelidad que nuestro generador casero
(preserva tablas, listas anidadas, blockquotes, énfasis, links).

Si `markitdown` no está disponible en el entorno (no instalado), devolvemos
una cadena vacía y el pipeline degrada al generador interno `render_markdown`.
"""
from __future__ import annotations

import io
import tempfile
from pathlib import Path
from typing import Optional


def html_to_markdown(html: str) -> Optional[str]:
    """Convierte un HTML string a Markdown usando microsoft/markitdown.

    Retorna el Markdown generado, o una cadena vacía si markitdown no está
    instalado / falla (dejando que el caller haga fallback).
    """
    if not html:
        return ""

    try:
        from markitdown import MarkItDown  # type: ignore
    except Exception:
        return ""

    # markitdown trabaja con rutas de archivo o streams. Escribimos a un
    # temporal (extensión .html para que el detector de tipo lo identifique).
    try:
        md = MarkItDown()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(html)
            tmp_path = f.name

        try:
            result = md.convert(tmp_path)
            return getattr(result, "text_content", "") or getattr(result, "markdown", "") or ""
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass
    except Exception:
        return ""


def file_to_markdown(path: str | Path) -> Optional[str]:
    """Convierte un archivo (PDF/DOCX/PPTX/XLSX/HTML/imagen/...) a Markdown.

    Útil para alimentar el corpus RAG desde documentos subidos por el usuario
    (dictámenes de TC, actas JNE en PDF, etc.).
    Retorna None si markitdown no está disponible o falla.
    """
    try:
        from markitdown import MarkItDown  # type: ignore
    except Exception:
        return None

    try:
        md = MarkItDown()
        result = md.convert(str(path))
        return getattr(result, "text_content", None) or getattr(result, "markdown", None)
    except Exception:
        return None
