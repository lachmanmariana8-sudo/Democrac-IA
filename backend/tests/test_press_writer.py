"""Tests del agente de prensa (PressWriter) — Bloque D.

Sin red ni LLM real: se prueban extracción de hechos, fidelidad (llm_guard),
formato de salida y el fallback determinista. Paridad 3.11/3.14 (sin f-strings
anidados con misma comilla)."""
import asyncio

import pytest

from agents.press_writer import PressWriter, PressArticleRequest, PressArticleOutput


def _source(proclaimed=False, indeterminate=True, winner=None):
    return {
        "country_code": "PER", "country_name": "Perú",
        "period": "2026-03-30 → 2026-06-10",
        "markdown": ("## Informe\nDemocrac.IA PEIRS monitoreó el ciclo electoral. "
                     "Se registraron 42 hallazgos, 5 críticos y 9 altos. El margen "
                     "fue de ~1303 votos."),
        "stats": {"total": 42, "critical": 5, "high": 9, "consolidated_total": 30,
                  "by_round": {"1ª vuelta": {"total": 18}, "2ª vuelta": {"total": 12}}},
        "result": {"second_round_results": {
            "proclamation": {"proclaimed": proclaimed, "winner": winner},
            "uncertainty": {"indeterminate": indeterminate},
            "status": "proclaimed" if proclaimed else "provisional",
            "margin_votes_approx": 1303}},
    }


def _run(coro):
    return asyncio.run(coro)


def test_extract_facts_reads_stats_and_result():
    facts = PressWriter._extract_facts(_source())
    assert facts["total_findings"] == 42
    assert facts["critical"] == 5 and facts["high"] == 9
    assert facts["round_1_total"] == 18 and facts["round_2_total"] == 12
    assert facts["indeterminate"] is True and facts["proclaimed"] is False


def test_deterministic_article_provisional_does_not_proclaim():
    pw = PressWriter(llm=None)
    out = _run(pw.compose(_source(indeterminate=True),
                          PressArticleRequest(report_id="r1", language="es", use_llm=False)))
    assert isinstance(out, PressArticleOutput)
    assert out.headline and out.standfirst and out.body_markdown
    assert out.html.startswith("<style")
    assert out.word_count > 0
    # No debe proclamar un ganador cuando el informe es indeterminado
    assert "proclamó" not in out.body_markdown.lower()
    # Cifras del artículo (42/5/9) están en el informe → sin flags de alucinación
    assert out.audit_flags == []


def test_deterministic_article_proclaimed_names_winner():
    pw = PressWriter(llm=None)
    src = _source(proclaimed=True, indeterminate=False, winner="Candidata Z")
    out = _run(pw.compose(src, PressArticleRequest(report_id="r2", language="es", use_llm=False)))
    assert "Candidata Z" in out.body_markdown or "Candidata Z" in out.standfirst


def test_llm_guard_flags_unsupported_figure():
    """Una cifra inventada que no está en el informe debe ir a audit_flags."""
    from agents.elite_report.llm_guard import guard_chapter
    md = _source()["markdown"]
    flags = guard_chapter("press_article",
                          "El proceso tuvo 987.654 incidentes documentados.", md)
    assert flags  # 987.654 no está en el informe


def test_multilingual_byline_and_terminology():
    pw = PressWriter(llm=None)
    for lang, term in (("en", "monitoring"), ("pt", "monitoramento"), ("es", "monitoreo")):
        out = _run(pw.compose(_source(),
                              PressArticleRequest(report_id="r", language=lang, use_llm=False)))
        assert out.byline == "Democrac.IA"
        blob = (out.headline + out.standfirst + out.body_markdown).lower()
        assert term in blob
