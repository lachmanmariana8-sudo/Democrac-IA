"""Modelos del agente de prensa (PressWriter).

Genera un análisis periodístico (~600 palabras) firmado por Democrac.IA, fiel al
informe final de PEIRS. No es el informe: es una pieza de divulgación con
excelencia narrativa y ortográfica, que expresa exactamente lo monitoreado.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PressArticleRequest(BaseModel):
    """Parámetros para generar el artículo a partir de un informe ya producido."""
    report_id: str
    language: str = "es"                 # es | en | pt
    angle: Optional[str] = None          # enfoque editorial opcional (ej. "crisis del EMB")
    max_words: int = 600
    byline: str = "Democrac.IA"
    use_llm: bool = True


class PressArticleOutput(BaseModel):
    """Artículo periodístico producido."""
    article_id: str
    report_id: str
    country_code: str = ""
    language: str = "es"
    headline: str = ""                   # titular
    standfirst: str = ""                 # bajada
    body_markdown: str = ""              # cuerpo (~600 palabras)
    html: str = ""                       # render listo para web
    byline: str = "Democrac.IA"
    word_count: int = 0
    generated_at: str = ""
    tokens_used: Dict[str, int] = Field(default_factory=dict)
    # Trazabilidad / control de calidad
    audit_flags: List[str] = Field(default_factory=list)   # cifras sin respaldo en el informe
    warnings: List[str] = Field(default_factory=list)
    source_facts: Dict[str, Any] = Field(default_factory=dict)  # hechos extraídos del informe
