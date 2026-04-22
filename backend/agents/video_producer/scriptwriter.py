"""Guionista-Claude: convierte findings en un guión periodístico estructurado."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.video_producer.models import VideoScript


# Duración estimada: 160 palabras por minuto en lectura natural
WPM_BY_LANGUAGE = {"es": 160, "en": 170, "pt": 160, "qu": 140}


LANGUAGE_INSTR = {
    "es": "Respondé en español rioplatense-peruano formal. Tono periodístico.",
    "en": "Respond in formal journalistic English.",
    "pt": "Responda em português formal jornalístico.",
    "qu": "Respondé en quechua sureño (Chanka/Cusco-Collao) formal, con términos técnicos en castellano cuando no haya equivalente.",
}

STYLE_INSTR = {
    "sober": "Tono sobrio y riguroso. Verbos precisos, sin adjetivación emocional. Estilo NHK/BBC.",
    "urgent": "Tono de urgencia informativa medida (no alarmista). Frases cortas, ritmo alto. Estilo AP/Reuters de última hora.",
    "explainer": "Tono didáctico explicativo. Define términos técnicos (JNE, ONPE, LOE, RENIEC). Estilo Vox/The Economist explainer.",
}


SYSTEM_PROMPT = """Sos periodista especializado en integridad electoral y observación democrática,
equivalente a un corresponsal de BBC Mundo, Reuters Americas o AP especializado en Perú.
Tu tarea: convertir hallazgos de monitoreo en un guión de video informativo de {target_duration_s}
segundos, listo para ser leído por un presentador.

Reglas de composición:
- Estructura en 4 bloques: HOOK (10s), CONTEXT (15s), FINDINGS (30-45s), CLOSING (10s).
- Citá SIEMPRE las fuentes específicas (IDL-Reporteros, El Comercio, Gestión, Andina, RPP, JNE, ONPE, etc.)
  cuando las tengas en los datos proporcionados.
- Precisión jurídica: si mencionás artículos de la Constitución peruana (176, 184, 176°, 31, 185, 186),
  Ley Orgánica de Elecciones (26859) o Ley de Partidos (28094), hacelo con número exacto.
- Cero especulación. Si el hallazgo es una denuncia, decí "se habría" o "denuncia presentada".
  Si es un hecho verificado, afirmalo.
- No uses clickbait ni adjetivos emocionales ("escandaloso", "vergonzoso", "terrible").
- Números específicos: "3 de los 5 órganos" en vez de "varios órganos".
- Evitá jerga técnica sin definir. Si usás "STAE", explicá "sistema automatizado de actas".

{language_instruction}
{style_instruction}

FORMATO DE SALIDA (JSON estricto, sin comentarios markdown):
```json
{{
  "hook": "...",
  "context": "...",
  "findings_narrative": "...",
  "closing": "...",
  "sources_cited": ["IDL-Reporteros", "JNE", ...]
}}
```

El HOOK debe empezar con un dato fuerte y específico. EJEMPLO DE HOOK BUENO:
"Perú ingresa a la recta final electoral con 21 hallazgos críticos registrados en 12 días de monitoreo."

EJEMPLO DE HOOK MALO:
"Las elecciones en Perú están generando mucha preocupación y es importante que todos estemos atentos."
"""


USER_PROMPT_TEMPLATE = """País: {country_name}
Período observado: últimos {period_days} días
Total hallazgos registrados: {total_findings}
Severidad mínima filtrada: {severity_min}

DISTRIBUCIÓN POR SEVERIDAD:
{severity_dist}

HALLAZGOS PRIORITARIOS (los que debés usar para el guión):
{findings_block}

CONTEXTO ADICIONAL (para el bloque CONTEXT):
{context_block}

INSTRUCCIÓN FINAL: Producí el JSON del guión. Los 4 bloques deben poder leerse de corrido
como una sola noticia coherente (ritmo, transiciones naturales). Total ~{target_words} palabras."""


class Scriptwriter:
    """Guionista que usa Claude para producir guiones de video."""

    def __init__(self, llm=None):
        self.llm = llm

    async def compose(
        self,
        findings: List[Dict[str, Any]],
        stats: Dict[str, Any],
        country_name: str,
        period_days: int,
        severity_min: str,
        language: str,
        style: str,
        target_duration_s: int,
    ) -> VideoScript:
        """Genera un VideoScript a partir de los findings provistos."""
        wpm = WPM_BY_LANGUAGE.get(language, 160)
        target_words = int(wpm * target_duration_s / 60)

        system = SYSTEM_PROMPT.format(
            target_duration_s=target_duration_s,
            language_instruction=LANGUAGE_INSTR.get(language, LANGUAGE_INSTR["es"]),
            style_instruction=STYLE_INSTR.get(style, STYLE_INSTR["sober"]),
        )

        user = USER_PROMPT_TEMPLATE.format(
            country_name=country_name,
            period_days=period_days,
            total_findings=stats.get("total", len(findings)),
            severity_min=severity_min,
            severity_dist=self._format_severity(stats),
            findings_block=self._format_findings(findings[:8]),
            context_block=self._format_context(stats),
            target_words=target_words,
        )

        if self.llm is None:
            return self._fallback_script(
                findings, country_name, language, style, target_words,
            )

        from langchain_core.messages import HumanMessage, SystemMessage
        response = await self.llm.ainvoke([
            SystemMessage(content=system),
            HumanMessage(content=user),
        ])
        text = response.content.strip() if hasattr(response, "content") else str(response)
        parsed = self._parse_json(text)

        hook = parsed.get("hook", "").strip()
        context = parsed.get("context", "").strip()
        findings_narr = parsed.get("findings_narrative", "").strip()
        closing = parsed.get("closing", "").strip()
        sources = parsed.get("sources_cited", []) or []

        full_text = "\n\n".join([p for p in [hook, context, findings_narr, closing] if p])
        wc = len(full_text.split())
        duration = wc / max(wpm / 60, 1e-6)

        return VideoScript(
            hook=hook, context=context, findings_narrative=findings_narr, closing=closing,
            word_count=wc, estimated_duration_s=round(duration, 1), full_text=full_text,
            sources_cited=[str(s) for s in sources][:10],
            language=language, tone=style,
        )

    # ── Helpers de formato ──────────────────────────────────────────────
    @staticmethod
    def _format_severity(stats: Dict[str, Any]) -> str:
        lines = []
        for k in ("critical", "high", "medium", "low", "info"):
            v = stats.get(k, 0)
            if v:
                lines.append(f"  - {v} {k}")
        return "\n".join(lines) or "  (sin datos)"

    @staticmethod
    def _format_findings(findings: List[Dict[str, Any]]) -> str:
        if not findings:
            return "  (sin hallazgos en el período)"
        lines = []
        for i, f in enumerate(findings):
            sev = f.get("severity", "info")
            cat = f.get("category", "other")
            src = f.get("source_name") or f.get("hunter_source") or "sin-fuente"
            url = f.get("source_url") or f.get("url") or ""
            title = (f.get("title") or f.get("headline") or f.get("finding") or "").strip()[:240]
            date = (f.get("recorded_at") or f.get("published_at") or "")[:10]
            line = f"  [{i+1}] ({sev.upper()}/{cat}) {date} — {src}: {title}"
            if url:
                line += f" [URL: {url}]"
            lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def _format_context(stats: Dict[str, Any]) -> str:
        bits = []
        days = stats.get("days_covered")
        if days:
            bits.append(f"- Días de monitoreo continuo: {days}")
        alerts = stats.get("alerts_dispatched")
        if alerts:
            bits.append(f"- Alertas despachadas a canales: {alerts}")
        phase = stats.get("phase")
        if phase:
            bits.append(f"- Fase electoral actual: {phase}")
        return "\n".join(bits) or "- (sin contexto adicional estructurado)"

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        """Extrae JSON del response aunque venga envuelto en ```json ... ```"""
        import json
        import re
        # Limpiar code fences
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if m:
            text = m.group(1)
        # Fallback: buscar primer bloque {...}
        if not text.strip().startswith("{"):
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                text = m.group(0)
        try:
            return json.loads(text)
        except Exception:
            return {}

    @staticmethod
    def _fallback_script(
        findings: List[Dict[str, Any]],
        country_name: str,
        language: str,
        style: str,
        target_words: int,
    ) -> VideoScript:
        """Guión mínimo cuando el LLM no está disponible (dev/offline)."""
        top = findings[0] if findings else {}
        title = (top.get("title") or top.get("finding") or "hallazgos múltiples").strip()[:160]
        source = top.get("source_name") or top.get("hunter_source") or "fuentes verificadas"

        hook = f"{country_name}. {len(findings)} hallazgos relevantes en el período observado."
        context = (
            f"El sistema PEIRS continúa monitoreando la integridad del proceso electoral "
            f"con fuentes primarias verificadas."
        )
        findings_narr = (
            f"Entre los más destacados: {title}. Reportado por {source}. "
            f"El equipo de observación mantiene el registro actualizado."
        )
        closing = "DemocracIA — observación electoral independiente."
        full = "\n\n".join([hook, context, findings_narr, closing])
        return VideoScript(
            hook=hook, context=context, findings_narrative=findings_narr, closing=closing,
            word_count=len(full.split()), estimated_duration_s=28.0,
            full_text=full, sources_cited=[source], language=language, tone=style,
        )
