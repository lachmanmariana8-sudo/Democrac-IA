"""Composer del Elite Report — genera narrativas por capítulo con Claude.

- chapter_composer.py: orquesta la composición de los 12 capítulos con
  concurrency limitada y prompt caching.
- prompts/: 1 archivo de base compartido + 12 prompts específicos por capítulo.
- citation_builder.py: extrae citas in-line y arma bibliografía APA 7.
"""
from agents.elite_report.composer.chapter_composer import ChapterComposer
from agents.elite_report.composer.citation_builder import CitationBuilder

__all__ = ["ChapterComposer", "CitationBuilder"]
