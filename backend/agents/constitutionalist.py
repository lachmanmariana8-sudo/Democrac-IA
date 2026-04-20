"""
DEMOCRAC.IA / PEIRS — Constitutionalist Agent

Sub-agente experto en derecho constitucional y electoral peruano. Responde
consultas sobre la Constitución de 1993, Ley Orgánica de Elecciones N° 26859,
Ley de Organizaciones Políticas N° 28094, jurisprudencia JNE, y marco
internacional aplicable (ICCPR, CADH, CDI).

Uso típico:
    from agents.constitutionalist import ConstitutionalistAgent
    agent = ConstitutionalistAgent(llm=llm)
    respuesta = await agent.ask(
        question="¿Puede la ONPE seguir organizando la segunda vuelta con Corvetto investigado?",
        context="Contexto opcional del caso"
    )

Arquitectura:
    1. Recibe la pregunta.
    2. Recupera pasajes relevantes del corpus RAG (filtrados por tags PERU*).
    3. Arma prompt con rol de jurista peruano + pasajes como contexto.
    4. Claude responde citando artículos específicos + marca nivel de confianza.
    5. Devuelve respuesta estructurada (answer, legal_basis, case_law, sources).
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from collections import Counter


# Tags que identifican contenido peruano en el corpus RAG
PERU_TAGS = {"peru", "constitucion", "JNE", "ONPE", "RENIEC", "LOE", "LOP",
             "derechos_politicos", "sistema_electoral", "partidos", "financiamiento",
             "paridad", "jurisprudencia", "democracia_interna", "sufragio",
             "cedula", "escrutinio", "impugnaciones", "silencio_electoral",
             "voto_electronico", "autonomia", "EMB", "institucional", "registro"}


_SYSTEM_PROMPT = """Eres un/a jurista peruano/a especializado/a en derecho constitucional y electoral.
Tu expertise cubre: la Constitución Política del Perú de 1993, la Ley Orgánica de Elecciones
N° 26859, la Ley de Organizaciones Políticas N° 28094, la jurisprudencia del Jurado Nacional
de Elecciones (JNE), y los instrumentos internacionales vinculantes para el Perú (ICCPR, CADH,
Carta Democrática Interamericana).

Tu misión es responder consultas de observadoras/es electorales de manera rigurosa,
fundamentada en norma positiva y jurisprudencia, y con lenguaje jurídico claro.

REGLAS DE RESPUESTA:

1. Cita artículos y fuentes específicos con número y nombre exacto (ej. "Art. 178 de la
   Constitución", "Art. 190 LOE", "Res. JNE 0891-2025-JNE").

2. Si la pregunta tiene múltiples vertientes (constitucional, legal, jurisprudencial,
   internacional), organízalas por separado.

3. Si hay ambigüedad o vacío normativo, declaralo explícitamente. No inventes doctrina.

4. Si el caso concreto requiere elementos fácticos que no tienes, indica qué información
   adicional sería necesaria para un dictamen completo.

5. Usa el formato estructurado siguiente (JSON) al final:
```json
{
  "answer": "texto de la respuesta principal (2-5 párrafos)",
  "legal_basis": ["Constitución Art. X", "LOE Art. Y", "Ley N° ..."],
  "case_law": ["Res. JNE XXXX", "Caso Corte IDH ..."],
  "international_framework": ["ICCPR Art. X", "CADH Art. Y", "CDI Art. Z"],
  "confidence": "high | medium | low",
  "caveats": ["limitaciones, supuestos, zonas grises..."]
}
```

6. NO emitas opinión política. Sí puedes indicar consecuencias jurídicas de cursos de acción
   alternativos.

7. Responde en español rioplatense-peruano formal. Usa "la ONPE", "el JNE" (artículo + sigla).

PASAJES DEL CORPUS LEGAL PERUANO RELEVANTES A LA CONSULTA:
__CONTEXT_PASSAGES__
"""


class ConstitutionalistAgent:
    """Agente experto en derecho constitucional y electoral peruano."""

    def __init__(self, llm=None, retriever=None):
        """
        Args:
            llm: instancia de Claude / LangChain (ChatAnthropic) con API key válida
            retriever: función custom(query, max) → List[Dict]. Si None, usa el
                       buscador léxico interno sobre LEGAL_CORPUS (ver _internal_search).
        """
        self.llm = llm
        self._retriever = retriever

    def _internal_search(self, query: str, max_results: int = 6) -> List[Dict[str, Any]]:
        """Búsqueda léxica TF sobre LEGAL_CORPUS filtrando PERU_TAGS.
        Reemplaza al retriever anterior (keyword_search no existía en rag.retriever)."""
        try:
            from rag.corpus import LEGAL_CORPUS
        except ImportError:
            return []

        # Tokenización simple con unicode
        def tok(t):
            return re.findall(r"[a-záéíóúüñ]{3,}", (t or "").lower())

        # Query expandida: agregamos sinónimos del dominio si aparecen keywords
        q_lower = query.lower()
        q_extra = []
        if re.search(r"\bjne\b", q_lower): q_extra.append("jurado nacional elecciones")
        if re.search(r"\bonpe\b", q_lower): q_extra.append("oficina nacional procesos electorales")
        if re.search(r"\breniec\b", q_lower): q_extra.append("registro nacional identificación")
        if "partido" in q_lower: q_extra.append("organizaciones políticas financiamiento")
        if "paridad" in q_lower or "mujer" in q_lower: q_extra.append("paridad alternancia ley 31030")
        if "voto electrónico" in q_lower or "venp" in q_lower: q_extra.append("voto electrónico VENP 0891-2025")
        if "escrutin" in q_lower or "acta" in q_lower: q_extra.append("escrutinio actas observadas impugnaciones")
        if "nulidad" in q_lower: q_extra.append("nulidad elección")
        if "segunda vuelta" in q_lower: q_extra.append("segunda vuelta 380")
        if "silencio" in q_lower: q_extra.append("silencio electoral 190")

        full_query = query + " " + " ".join(q_extra)
        q_tokens = Counter(tok(full_query))
        if not q_tokens:
            return []

        scored = []
        for doc in LEGAL_CORPUS:
            tags = set(doc.get("tags", []))
            instrument = str(doc.get("instrument", ""))
            # Boost si es peruano
            peru_boost = 2.0 if (tags & PERU_TAGS or "PERU" in instrument) else 1.0

            doc_text = f"{doc.get('title','')} {doc.get('text','')} {' '.join(tags)}"
            d_tokens = Counter(tok(doc_text))
            overlap = sum(min(q_tokens[t], d_tokens[t]) for t in q_tokens if t in d_tokens)
            score = (overlap / (sum(q_tokens.values()) + 1)) * peru_boost
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:max_results]]

    def _get_peru_passages(self, question: str, max_passages: int = 6) -> List[Dict[str, Any]]:
        """Recupera pasajes del corpus relevantes a la consulta peruana."""
        if self._retriever is not None:
            try:
                return self._retriever(question, max_passages)
            except Exception:
                pass
        return self._internal_search(question, max_passages)

    def _format_passages(self, passages: List[Dict[str, Any]]) -> str:
        if not passages:
            return "(No se encontraron pasajes específicos. Respondé desde tu conocimiento general del derecho peruano.)"

        blocks = []
        for i, p in enumerate(passages, 1):
            title = p.get("title", "Sin título")
            instrument = p.get("instrument", "—")
            text = p.get("text", "").strip()
            # Truncar textos muy largos para no superar contexto
            if len(text) > 3500:
                text = text[:3500] + "\n[... truncado]"
            blocks.append(f"### Pasaje {i}: {title}\nInstrumento: {instrument}\n\n{text}\n")
        return "\n---\n".join(blocks)

    async def ask(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Responde la consulta constitucional.

        Returns dict con:
            answer, legal_basis, case_law, international_framework, confidence,
            caveats, sources_cited (lista de pasajes usados), tokens_used
        """
        if not self.llm:
            return {
                "error": "LLM no configurado",
                "answer": None,
            }

        passages = self._get_peru_passages(question, max_passages=6)
        context_block = self._format_passages(passages)

        user_msg = f"CONSULTA:\n{question}\n"
        if context:
            user_msg += f"\nCONTEXTO ADICIONAL DEL CASO:\n{context}\n"
        user_msg += "\nRespondé en el formato indicado (texto jurídico + JSON final)."

        from langchain_core.messages import HumanMessage, SystemMessage
        # NO usar .format() — el template contiene {} literales del ejemplo JSON
        # que rompen format(). Usamos replace simple sobre un token único.
        system = _SYSTEM_PROMPT.replace("__CONTEXT_PASSAGES__", context_block)

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system),
                HumanMessage(content=user_msg),
            ])
            raw = response.content.strip() if hasattr(response, "content") else str(response)
        except Exception as e:
            return {
                "error": f"{type(e).__name__}: {e}",
                "answer": None,
            }

        # Extraer el bloque JSON de respuesta (lo ponemos al final del prompt)
        parsed = {}
        match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", raw)
        if match:
            try:
                parsed = json.loads(match.group(1))
            except json.JSONDecodeError:
                parsed = {}
        else:
            # Intento sin fences
            match = re.search(r"\{[\s\S]*\"answer\"[\s\S]*\}", raw)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    parsed = {}

        # Si no se pudo parsear, devolver el raw como answer
        if not parsed.get("answer"):
            # Quitar bloque json si quedó, devolver texto limpio
            text_answer = re.sub(r"```json[\s\S]*?```", "", raw).strip()
            parsed = {
                "answer": text_answer or raw,
                "legal_basis": [],
                "case_law": [],
                "international_framework": [],
                "confidence": "medium",
                "caveats": ["Respuesta no estructurada por el modelo; parseo manual aplicado."],
            }

        # Metadata del retrieval
        parsed["sources_cited"] = [
            {"id": p.get("id"), "title": p.get("title"), "instrument": p.get("instrument")}
            for p in passages
        ]
        parsed["generated_at"] = datetime.now(timezone.utc).isoformat()
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("usage", {})
            parsed["tokens_used"] = {
                "input": usage.get("input_tokens"),
                "output": usage.get("output_tokens"),
            }

        return parsed
