"""PressWriter — agente de prensa de Democrac.IA.

Produce un análisis periodístico (~600 palabras) fiel al informe final de PEIRS,
firmado por Democrac.IA. Sigue el patrón de ChapterComposer: prompts en
prompts/{es,en,pt}, LLM global inyectado, validación anti-alucinación con
llm_guard contra el markdown del informe (cifras sin respaldo → audit_flags).

compose(source, req) NO genera el informe; recibe el contenido del informe ya
producido (markdown + stats + resultado) y escribe la pieza de divulgación.
"""
from __future__ import annotations

import asyncio
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.press_writer.models import PressArticleRequest, PressArticleOutput
from agents.press_writer.formatter import render_article_html

_LANG_NAME = {"es": "español", "en": "English", "pt": "português"}


class PressWriter:
    def __init__(self, llm=None):
        self.llm = llm
        self.retries = 2
        self._prompts_dir = Path(__file__).parent / "prompts"
        self._prompt_cache: Dict[str, str] = {}

    # ── Prompts ──────────────────────────────────────────────────────────
    def _load_prompt_file(self, filename: str, language: str = "es") -> str:
        lang = (language or "es").lower()
        key = f"{lang}::{filename}"
        if key in self._prompt_cache:
            return self._prompt_cache[key]
        p = self._prompts_dir / lang / filename
        if not p.exists() and lang != "es":
            p = self._prompts_dir / "es" / filename
        content = p.read_text(encoding="utf-8") if p.exists() else ""
        self._prompt_cache[key] = content
        return content

    # ── Extracción de hechos del informe ──────────────────────────────────
    @staticmethod
    def _extract_facts(source: Dict[str, Any]) -> Dict[str, Any]:
        """Hechos clave verificables desde el informe (stats + resultado)."""
        stats = source.get("stats") or {}
        facts: Dict[str, Any] = {
            "total_findings": stats.get("total", 0),
            "critical": stats.get("critical", 0),
            "high": stats.get("high", 0),
            "consolidated_total": stats.get("consolidated_total"),
        }
        by_round = stats.get("by_round") or {}
        if by_round:
            facts["round_1_total"] = (by_round.get("1ª vuelta") or {}).get("total")
            facts["round_2_total"] = (by_round.get("2ª vuelta") or {}).get("total")
        # Resultado (provisional/indeterminado o proclamado)
        result = source.get("result") or {}
        srr = result.get("second_round_results") if isinstance(result, dict) else None
        if isinstance(srr, dict):
            proc = srr.get("proclamation") or {}
            unc = srr.get("uncertainty") or {}
            facts["proclaimed"] = bool(proc.get("proclaimed"))
            facts["winner"] = proc.get("winner")
            facts["indeterminate"] = bool(unc.get("indeterminate"))
            facts["status"] = srr.get("status")
            facts["actas_processed_pct"] = srr.get("actas_processed_pct")
            facts["margin_votes_approx"] = srr.get("margin_votes_approx")
        return {k: v for k, v in facts.items() if v is not None}

    @staticmethod
    def _facts_to_bullets(facts: Dict[str, Any], language: str = "es") -> str:
        L = (language or "es").lower()
        def lbl(es, en, pt):
            return {"es": es, "en": en, "pt": pt}.get(L, es)
        lines = []
        if facts.get("total_findings") is not None:
            lines.append(f"- {lbl('Hallazgos totales','Total findings','Achados totais')}: "
                         f"{facts['total_findings']} ({lbl('críticos','critical','críticos')}: "
                         f"{facts.get('critical', 0)}; {lbl('altos','high','altos')}: {facts.get('high', 0)})")
        if facts.get("round_1_total") is not None or facts.get("round_2_total") is not None:
            lines.append(f"- {lbl('Hallazgos por vuelta','Findings by round','Achados por turno')}: "
                         f"1ª={facts.get('round_1_total','—')}, 2ª={facts.get('round_2_total','—')}")
        if facts.get("proclaimed"):
            res_lbl = lbl("Resultado: PROCLAMADO", "Result: PROCLAIMED", "Resultado: PROCLAMADO")
            win_lbl = lbl("ganador", "winner", "vencedor")
            lines.append(f"- {res_lbl}; {win_lbl}: {facts.get('winner', '—')}")
        elif facts.get("indeterminate"):
            res_lbl = lbl("Resultado: PROVISIONAL/INDETERMINADO (sin proclamación)",
                          "Result: PROVISIONAL/UNDETERMINED (not proclaimed)",
                          "Resultado: PROVISÓRIO/INDETERMINADO (sem proclamação)")
            lines.append(f"- {res_lbl}")
            if facts.get("margin_votes_approx"):
                margin_lbl = lbl("Margen aproximado", "Approx. margin", "Margem aproximada")
                votes_lbl = lbl("votos", "votes", "votos")
                lines.append(f"- {margin_lbl}: ~{facts['margin_votes_approx']} {votes_lbl}")
        return "\n".join(lines) if lines else lbl("(sin hechos cuantitativos)",
                                                  "(no quantitative facts)", "(sem fatos quantitativos)")

    # ── Parseo de la salida del LLM ───────────────────────────────────────
    @staticmethod
    def _parse_output(text: str) -> Dict[str, str]:
        headline, standfirst, body = "", "", ""
        m_t = re.search(r"TITULAR:\s*(.+)", text)
        m_b = re.search(r"BAJADA:\s*(.+)", text)
        m_c = re.search(r"CUERPO:\s*\n?(.+)", text, re.DOTALL)
        if m_t:
            headline = m_t.group(1).strip()
        if m_b:
            standfirst = m_b.group(1).strip()
        if m_c:
            body = m_c.group(1).strip()
        else:
            # Fallback: si no respetó el formato, todo el texto es cuerpo.
            body = text.strip()
        return {"headline": headline, "standfirst": standfirst, "body": body}

    # ── Composición ───────────────────────────────────────────────────────
    async def compose(self, source: Dict[str, Any],
                      req: PressArticleRequest) -> PressArticleOutput:
        lang = (req.language or "es").lower()
        facts = self._extract_facts(source)
        key_facts = self._facts_to_bullets(facts, lang)
        report_md = source.get("markdown") or ""
        excerpt = report_md[:6000]

        out = PressArticleOutput(
            article_id=uuid.uuid4().hex[:12],
            report_id=req.report_id,
            country_code=source.get("country_code", ""),
            language=lang,
            byline=req.byline,
            generated_at=datetime.now(timezone.utc).isoformat(),
            source_facts=facts,
        )

        if self.llm is None or not req.use_llm:
            # Fallback determinista: artículo armado desde los hechos (sin LLM).
            parsed = self._deterministic_article(facts, source, lang)
            out.warnings.append("Artículo generado sin LLM (modo determinista).")
        else:
            base = self._load_prompt_file("base_context.md", lang)
            tmpl = self._load_prompt_file("press_article.md", lang)
            angle_line = ""
            if req.angle:
                angle_line = {"es": f"Enfoque editorial sugerido: {req.angle}.",
                              "en": f"Suggested editorial angle: {req.angle}.",
                              "pt": f"Enfoque editorial sugerido: {req.angle}."}.get(lang, req.angle)
            system = (base
                      .replace("{language_name}", _LANG_NAME.get(lang, "español"))
                      .replace("{country_name}", source.get("country_name", source.get("country_code", "")))
                      .replace("{period}", source.get("period", "—"))
                      .replace("{key_facts}", key_facts)
                      .replace("{report_excerpt}", excerpt))
            user = (tmpl
                    .replace("{max_words}", str(req.max_words))
                    .replace("{angle_line}", angle_line))
            parsed = await self._invoke_llm(system, user, out)

        out.headline = parsed.get("headline", "")
        out.standfirst = parsed.get("standfirst", "")
        out.body_markdown = parsed.get("body", "")
        out.word_count = len(out.body_markdown.split())
        out.html = render_article_html(
            out.headline, out.standfirst, out.body_markdown,
            byline=out.byline, language=lang, generated_at=out.generated_at)

        # Control anti-alucinación: cifras del artículo sin respaldo en el informe.
        try:
            from agents.elite_report.llm_guard import guard_chapter
            context = (report_md + "\n" + key_facts)
            out.audit_flags = guard_chapter("press_article",
                                            out.headline + "\n" + out.standfirst + "\n" + out.body_markdown,
                                            context)
        except Exception as e:
            out.warnings.append(f"llm_guard falló: {type(e).__name__}: {e}")

        return out

    async def _invoke_llm(self, system: str, user: str,
                          out: PressArticleOutput) -> Dict[str, str]:
        from langchain_core.messages import HumanMessage, SystemMessage
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                resp = await self.llm.ainvoke([
                    SystemMessage(content=system),
                    HumanMessage(content=user),
                ])
                text = resp.content.strip() if hasattr(resp, "content") else str(resp)
                if hasattr(resp, "response_metadata"):
                    usage = resp.response_metadata.get("usage", {})
                    out.tokens_used = {"input": usage.get("input_tokens", 0),
                                       "output": usage.get("output_tokens", 0)}
                return self._parse_output(text)
            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e)[:200]}"
                if attempt < self.retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
        out.warnings.append(f"LLM falló tras reintentos: {last_error}")
        return self._deterministic_article(out.source_facts, {}, out.language)

    # ── Fallback determinista (sin LLM) ───────────────────────────────────
    @staticmethod
    def _deterministic_article(facts: Dict[str, Any], source: Dict[str, Any],
                               language: str = "es") -> Dict[str, str]:
        L = (language or "es").lower()
        country = source.get("country_name", source.get("country_code", "el país"))
        total = facts.get("total_findings", 0)
        crit, high = facts.get("critical", 0), facts.get("high", 0)
        if L == "en":
            if facts.get("proclaimed"):
                state = f"the EMB proclaimed {facts.get('winner','the winner')}"
            elif facts.get("indeterminate"):
                state = "the result remained provisional and undetermined, pending official proclamation"
            else:
                state = "the cycle was monitored across both rounds"
            headline = f"PEIRS monitoring of {country}: {total} findings across the electoral cycle"
            standfirst = (f"Democrac.IA's automated monitoring registered {crit} critical and "
                          f"{high} high-severity findings; {state}.")
            body = (f"Democrac.IA PEIRS monitored the {country} electoral cycle across the first "
                    f"and second rounds. The platform registered {total} findings, of which {crit} "
                    f"were critical and {high} high-severity.\n\n"
                    f"As recorded in the final report, {state}. All figures derive from the "
                    f"consolidated monitoring corpus, with full traceability to primary sources.")
        elif L == "pt":
            if facts.get("proclaimed"):
                state = f"o EMB proclamou {facts.get('winner','o vencedor')}"
            elif facts.get("indeterminate"):
                state = "o resultado permaneceu provisório e indeterminado, à espera da proclamação oficial"
            else:
                state = "o ciclo foi monitorado nos dois turnos"
            headline = f"Monitoramento PEIRS do {country}: {total} achados no ciclo eleitoral"
            standfirst = (f"O monitoramento automatizado da Democrac.IA registrou {crit} achados "
                          f"críticos e {high} de severidade alta; {state}.")
            body = (f"A Democrac.IA PEIRS monitorou o ciclo eleitoral do {country} no primeiro e no "
                    f"segundo turno. A plataforma registrou {total} achados, dos quais {crit} "
                    f"críticos e {high} de severidade alta.\n\n"
                    f"Conforme o relatório final, {state}. Todos os números derivam do corpus "
                    f"consolidado de monitoramento, com rastreabilidade às fontes primárias.")
        else:
            if facts.get("proclaimed"):
                state = f"el organismo electoral proclamó a {facts.get('winner','el ganador')}"
            elif facts.get("indeterminate"):
                state = ("el resultado se mantuvo provisional e indeterminado, a la espera de la "
                         "proclamación oficial")
            else:
                state = "el ciclo fue monitoreado en ambas vueltas"
            headline = f"Monitoreo PEIRS de {country}: {total} hallazgos en el ciclo electoral"
            standfirst = (f"El monitoreo automatizado de Democrac.IA registró {crit} hallazgos "
                          f"críticos y {high} de severidad alta; {state}.")
            body = (f"Democrac.IA PEIRS monitoreó el ciclo electoral de {country} en la primera y la "
                    f"segunda vuelta. La plataforma registró {total} hallazgos, de los cuales {crit} "
                    f"fueron críticos y {high} de severidad alta.\n\n"
                    f"Según consta en el informe final, {state}. Todas las cifras provienen del corpus "
                    f"consolidado de monitoreo, con trazabilidad completa a las fuentes primarias.")
        return {"headline": headline, "standfirst": standfirst, "body": body}
