"""Director cinematográfico: guión → plan de escenas con overlays y ritmo."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.video_producer.models import VideoScript, VideoPlan, SceneSpec, OverlaySpec


SYSTEM_PROMPT = """Sos director cinematográfico y editor de piezas informativas breves
(equivalente a un productor de TV de noticias internacionales: NHK World, DW, BBC World).

Tu tarea: tomar un guión de noticia ya escrito y descomponerlo en ESCENAS ejecutables
por un sistema de avatar hablante (tipo HeyGen). Cada escena debe tener:
  - Un fragmento del guión (lo que el avatar dirá en voz alta)
  - Duración estimada en segundos (150-170 palabras por minuto)
  - Overlays gráficos opcionales (lower third de fuente, stat card, cita textual, URL)
  - Un "background hint" (studio | solid | newsroom | brief)

REGLAS:
- El bloque HOOK debe ser UNA escena de 8-12s con un lower_third con el país y el dato clave.
- El bloque CONTEXT debe ser 1 escena con una stat_card que destaque el número principal.
- El bloque FINDINGS_NARRATIVE debe dividirse en 2-3 escenas, cada una con un lower_third
  que muestre la fuente citada en esa escena.
- El bloque CLOSING debe ser UNA escena con overlay source_url apuntando a democracia.ar.
- TOTAL: 5-8 escenas. Duración total objetivo: 60-90s.
- NO superar 90s totales.

FORMATO DE SALIDA (JSON estricto):
```json
{
  "scenes": [
    {
      "scene_id": "hook",
      "narration": "...",
      "duration_s": 10.0,
      "avatar_style": "authoritative",
      "background": "studio",
      "overlays": [
        {"kind": "lower_third", "content": "Perú · Observación PEIRS", "start_s": 2, "duration_s": 6, "position": "bottom"}
      ]
    },
    ...
  ],
  "intro_hint": "Logo DemocracIA (1s)",
  "outro_hint": "Tarjeta fin con CTA democracia.ar"
}
```"""


USER_PROMPT_TEMPLATE = """GUIÓN A DESCOMPONER:

[HOOK]
{hook}

[CONTEXT]
{context}

[FINDINGS_NARRATIVE]
{findings}

[CLOSING]
{closing}

DATOS ÚTILES:
- Fuentes citadas: {sources}
- Duración objetivo: {target_duration}s
- Idioma: {language}
- Tono: {tone}

Descomponé en escenas. Devolvé solo el JSON."""


class Director:
    """Traductor guión → plan de escenas usando Claude."""

    def __init__(self, llm=None):
        self.llm = llm

    async def plan(
        self,
        script: VideoScript,
        target_duration_s: int = 75,
    ) -> VideoPlan:
        """Produce un VideoPlan a partir del VideoScript."""
        if self.llm is None:
            return self._fallback_plan(script, target_duration_s)

        user = USER_PROMPT_TEMPLATE.format(
            hook=script.hook,
            context=script.context,
            findings=script.findings_narrative,
            closing=script.closing,
            sources=", ".join(script.sources_cited) or "—",
            target_duration=target_duration_s,
            language=script.language,
            tone=script.tone,
        )

        from langchain_core.messages import HumanMessage, SystemMessage
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user),
            ])
            text = response.content.strip() if hasattr(response, "content") else str(response)
            parsed = self._parse_json(text)
            return self._build_plan(parsed, script, target_duration_s)
        except Exception:
            return self._fallback_plan(script, target_duration_s)

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        import json
        import re
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if m:
            text = m.group(1)
        if not text.strip().startswith("{"):
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                text = m.group(0)
        try:
            return json.loads(text)
        except Exception:
            return {}

    def _build_plan(
        self, parsed: Dict[str, Any], script: VideoScript, target_duration_s: int,
    ) -> VideoPlan:
        scenes_raw = parsed.get("scenes") or []
        scenes: List[SceneSpec] = []
        for i, s in enumerate(scenes_raw):
            overlays = []
            for o in s.get("overlays", []) or []:
                overlays.append(OverlaySpec(
                    kind=o.get("kind", "caption"),
                    content=str(o.get("content", ""))[:200],
                    start_s=float(o.get("start_s", 0)),
                    duration_s=float(o.get("duration_s", 4)),
                    position=o.get("position", "bottom"),
                ))
            scenes.append(SceneSpec(
                scene_id=s.get("scene_id") or f"scene_{i+1}",
                narration=str(s.get("narration", "")).strip(),
                duration_s=float(s.get("duration_s", 10)),
                avatar_style=s.get("avatar_style", "talking"),
                background=s.get("background", "studio"),
                background_value=s.get("background_value", "#0f4f4b"),
                overlays=overlays,
                b_roll_hint=s.get("b_roll_hint"),
            ))

        if not scenes:
            return self._fallback_plan(script, target_duration_s)

        total = sum(s.duration_s for s in scenes)
        return VideoPlan(
            scenes=scenes,
            total_duration_s=round(total, 1),
            intro_hint=parsed.get("intro_hint"),
            outro_hint=parsed.get("outro_hint"),
        )

    @staticmethod
    def _fallback_plan(script: VideoScript, target_duration_s: int) -> VideoPlan:
        """Plan rule-based cuando Claude no está disponible."""
        wpm = 160
        def dur(text: str) -> float:
            wc = len(text.split())
            return max(wc / (wpm / 60), 3.0)

        scenes = [
            SceneSpec(
                scene_id="hook",
                narration=script.hook,
                duration_s=dur(script.hook),
                avatar_style="authoritative",
                background="studio",
                overlays=[OverlaySpec(
                    kind="lower_third",
                    content=f"Observación PEIRS · DemocracIA",
                    start_s=1.5, duration_s=6, position="bottom",
                )],
            ),
            SceneSpec(
                scene_id="context",
                narration=script.context,
                duration_s=dur(script.context),
                avatar_style="talking",
                background="studio",
                overlays=[OverlaySpec(
                    kind="stat_card", content="Fuente: PEIRS", start_s=2, duration_s=5,
                    position="right",
                )],
            ),
            SceneSpec(
                scene_id="findings",
                narration=script.findings_narrative,
                duration_s=dur(script.findings_narrative),
                avatar_style="talking",
                background="studio",
                overlays=[OverlaySpec(
                    kind="lower_third",
                    content=", ".join(script.sources_cited[:3]) or "Fuentes verificadas",
                    start_s=3, duration_s=10, position="bottom",
                )],
            ),
            SceneSpec(
                scene_id="closing",
                narration=script.closing,
                duration_s=dur(script.closing),
                avatar_style="authoritative",
                background="studio",
                overlays=[OverlaySpec(
                    kind="source_url", content="democracia.ar",
                    start_s=1, duration_s=5, position="bottom",
                )],
            ),
        ]
        total = sum(s.duration_s for s in scenes)
        return VideoPlan(
            scenes=scenes, total_duration_s=round(total, 1),
            intro_hint="Logo DemocracIA (1s)",
            outro_hint="Tarjeta fin · democracia.ar",
        )
