"""
PredictiveEngine — motor híbrido reglas + Claude para forecast de escenarios.

Pipeline:
1. Regla determinista sobre EvidenceBundle → identifica escenarios candidatos
   con probabilidad base + indicadores instanciados.
2. Prompt Claude con toda la evidencia + candidatos → ajusta probabilidades,
   genera narrativa específica por escenario, declara early_warning_level.
3. Normaliza y garantiza que las probabilidades no sean mutuamente exclusivas
   (varios escenarios pueden coexistir).

Fallback graceful: si Claude falla, retorna los escenarios con probabilidades
base y narrativa de template.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agents.elite_report.models import (
    EvidenceBundle,
    ForecastPayload,
    ForecastScenario,
)
from agents.elite_report.predictive.scenarios import SCENARIO_TEMPLATES


class PredictiveEngine:
    """Genera ForecastPayload desde un EvidenceBundle."""

    def __init__(self, llm=None, country_code: str = "PER"):
        self.llm = llm
        self.country_code = country_code.upper()

    async def forecast(
        self,
        bundle: EvidenceBundle,
        horizon_days: int = 14,
    ) -> ForecastPayload:
        """Genera forecast con escenarios probabilísticos."""
        # 1. Evaluar reglas deterministas sobre la evidencia
        candidates = self._evaluate_rules(bundle)

        # 2. Ajustar con Claude (si disponible)
        # llm_meta guarda dominant_pattern + early_warning_level que vienen
        # del JSON del LLM. Antes se intentaba monkey-patch sobre la lista
        # (updated.append_pattern = ...) lo cual es ilegal en Python (list
        # no acepta atributos arbitrarios) -> AttributeError siempre.
        # Fix 2-may-2026: pasarlo explicito via dict.
        llm_meta: dict = {}
        if self.llm is not None and candidates:
            try:
                candidates, llm_meta = await self._refine_with_llm(candidates, bundle)
            except Exception as e:
                # Fallback: mantener candidatos con base_probability
                bundle.warnings.append(
                    f"PredictiveEngine: fallback sin LLM ({type(e).__name__}: {e})"
                )

        # 3. Ensamblar payload
        dominant_pattern = self._describe_dominant_pattern(bundle, candidates, llm_meta)
        early_warning = self._compute_early_warning(candidates, bundle, llm_meta)

        return ForecastPayload(
            horizon_days=horizon_days,
            generated_at=datetime.now(timezone.utc).isoformat(),
            scenarios=candidates,
            dominant_pattern=dominant_pattern,
            early_warning_level=early_warning[0],
            early_warning_note=early_warning[1],
        )

    # ── 1. REGLAS DETERMINISTAS ─────────────────────────────────────────
    def _evaluate_rules(self, bundle: EvidenceBundle) -> List[ForecastScenario]:
        """Aplica triggers de cada template sobre la evidencia. Retorna la lista
        de escenarios que cumplen al menos una regla, con probabilidad base."""
        # Señales agregadas del bundle
        signals = self._aggregate_signals(bundle)

        active_scenarios: List[ForecastScenario] = []
        for tpl in SCENARIO_TEMPLATES:
            triggers = tpl.get("triggers", {})
            if not self._triggers_match(triggers, signals):
                continue

            # Instanciar indicators con datos reales
            indicators = self._instantiate_indicators(
                tpl["indicators_template"], signals
            )

            active_scenarios.append(ForecastScenario(
                scenario_id=tpl["scenario_id"],
                label=tpl["label"],
                probability=float(tpl["base_probability"]),
                confidence_interval=None,
                indicators=indicators,
                implications=tpl["implications_template"],
                watch_signals=list(tpl["watch_signals_template"]),
                legal_basis=tpl.get("legal_basis"),
            ))

        # Si ningún escenario se activó (muy raro), incluimos proclamación normal
        if not active_scenarios:
            tpl = next(
                (t for t in SCENARIO_TEMPLATES if t["scenario_id"] == "s_proclamacion_sin_disputa"),
                None,
            )
            if tpl:
                active_scenarios.append(ForecastScenario(
                    scenario_id=tpl["scenario_id"],
                    label=tpl["label"],
                    probability=0.5,
                    indicators=tpl["indicators_template"],
                    implications=tpl["implications_template"],
                    watch_signals=tpl["watch_signals_template"],
                    legal_basis=tpl.get("legal_basis"),
                ))

        return active_scenarios

    @staticmethod
    def _aggregate_signals(bundle: EvidenceBundle) -> Dict[str, Any]:
        """Computa señales agregadas sobre la evidencia para alimentar triggers."""
        by_cat: Counter = Counter()
        by_sev: Counter = Counter()
        penal_complaints = 0
        stae_incidents = 0
        regions_critical_logistics: set = set()

        for f in bundle.hunter_entries:
            cat = (f.category or "").lower()
            sev = (f.severity or "").lower()
            by_cat[cat] += 1
            by_sev[sev] += 1

            text = (f.finding or "").lower() + " " + (f.source_title or "").lower()
            if any(kw in text for kw in ["denuncia penal", "fiscal", "detención",
                                         "procesado", "flagrancia", "corvetto"]):
                if "onpe" in text or "jne" in text or "autoridad electoral" in text:
                    penal_complaints += 1
            if "stae" in text or "sistema tecnológico" in text:
                stae_incidents += 1
            if cat == "logistics" and sev in ("critical", "high"):
                # Heurística simple para región/lugar
                loc_match = re.search(r"(lima|callao|trujillo|arequipa|cusco|puno|piura)",
                                      text)
                if loc_match:
                    regions_critical_logistics.add(loc_match.group(1))

        return {
            "country": bundle.country_code,
            "by_category": dict(by_cat),
            "by_severity": dict(by_sev),
            "total_findings": len(bundle.hunter_entries),
            "critical_count": by_sev.get("critical", 0),
            "high_count": by_sev.get("high", 0),
            "fraud_allegation_count": by_cat.get("fraud_allegation", 0),
            "ballot_tampering_count": by_cat.get("ballot_tampering", 0),
            "digital_count": by_cat.get("digital", 0),
            "security_violence_count": by_cat.get("security", 0) + by_cat.get("violence", 0),
            "penal_complaints_against_emb": penal_complaints,
            "stae_incidents": stae_incidents,
            "critical_logistics_regions": len(regions_critical_logistics),
        }

    @staticmethod
    def _triggers_match(triggers: Dict[str, Any], signals: Dict[str, Any]) -> bool:
        """Evalúa si las triggers de un template se cumplen sobre las señales."""
        if not triggers:
            return True

        # country-specific
        country_req = triggers.get("country")
        if country_req and country_req != signals.get("country"):
            return False

        # Reglas simples por nombre: {metric}_ge
        or_any = False
        has_or = False
        and_all = True

        for key, threshold in triggers.items():
            if key == "country":
                continue
            is_or = key.startswith("or_")
            metric_key = key[3:] if is_or else key
            if metric_key.endswith("_ge"):
                metric_name = metric_key[:-3]
                current = signals.get(metric_name, 0)
                matches = current >= threshold
            elif isinstance(threshold, bool):
                # Flags booleanos: stae_incidents, low_disruption, etc.
                current = signals.get(metric_key, 0)
                if metric_key == "low_disruption":
                    # Complemento: se activa cuando hay pocos findings high/critical
                    matches = (signals.get("critical_count", 0)
                               + signals.get("high_count", 0)) < 10
                else:
                    matches = bool(current) == threshold
            else:
                matches = signals.get(metric_key) == threshold

            if is_or:
                has_or = True
                if matches:
                    or_any = True
            else:
                if not matches:
                    and_all = False

        if has_or:
            return or_any or and_all
        return and_all

    @staticmethod
    def _instantiate_indicators(templates: List[str], signals: Dict[str, Any]) -> List[str]:
        """Reemplaza placeholders numéricos en los indicators con datos reales
        cuando es posible."""
        out: List[str] = []
        for t in templates:
            replaced = t
            # Sustituciones heurísticas simples
            if "fraud_allegation" in t.lower():
                replaced = replaced.replace(
                    "Alta densidad de fraud_allegation",
                    f"{signals.get('fraud_allegation_count', 0)} hallazgos fraud_allegation registrados"
                )
            out.append(replaced)
        return out

    # ── 2. REFINAMIENTO CON LLM ─────────────────────────────────────────
    async def _refine_with_llm(
        self,
        candidates: List[ForecastScenario],
        bundle: EvidenceBundle,
    ) -> tuple[List[ForecastScenario], dict]:
        """Pide a Claude que ajuste probabilidades y genere implications
        específicas. Retorna (escenarios actualizados, llm_meta_dict) donde
        llm_meta tiene dominant_pattern + early_warning_level + note."""
        from langchain_core.messages import HumanMessage, SystemMessage

        # Evidencia compacta
        signals = self._aggregate_signals(bundle)
        top_findings = bundle.hunter_entries[:15]
        findings_text = "\n".join([
            f"- [{f.severity}] [{f.category}] {(f.finding or '')[:180]}"
            for f in top_findings
        ])

        scenarios_text = json.dumps([
            {
                "id": s.scenario_id, "label": s.label,
                "base_prob": s.probability,
                "indicators": s.indicators,
            }
            for s in candidates
        ], ensure_ascii=False, indent=2)

        system_prompt = f"""Sos un/a analista institucional especializada en dinámica
post-electoral. Tu tarea es estimar la probabilidad de escenarios de dinámica
institucional (NO pronóstico político de quién gana) en el país {bundle.country_code}
sobre un horizonte corto (2 semanas).

NO sos adivino/a: trabajás sobre evidencia concreta. Usás criterio experto
para ajustar probabilidades base usando los patrones de hallazgos y las señales
agregadas.

PRINCIPIOS:
- Las probabilidades NO son mutuamente excluyentes. Varios escenarios pueden
  coexistir con probabilidades altas.
- Cada ajuste debe estar justificado en evidencia concreta del bundle.
- Si la evidencia es débil, devuelve el valor base o un ajuste menor.
- Devuelve números entre 0.05 y 0.95 (evita 0 y 1 absolutos).

Devolverás JSON puro con esta estructura exacta:
{{
  "scenarios": [
    {{"id": "...", "probability_adjusted": 0.XX, "implications_refined": "...",
      "confidence_low": 0.XX, "confidence_high": 0.XX}}
  ],
  "dominant_pattern": "Frase de 1-2 oraciones describiendo el patrón dominante",
  "early_warning_level": "green|amber|orange|red",
  "early_warning_note": "Explicación breve del nivel"
}}"""

        user_prompt = f"""SEÑALES AGREGADAS DEL SISTEMA:
{json.dumps(signals, ensure_ascii=False, indent=2)}

TOP FINDINGS (priorizados por severity × recency × credibilidad):
{findings_text}

ESCENARIOS CANDIDATOS (con probabilidad base de reglas deterministas):
{scenarios_text}

Ajustá las probabilidades según la evidencia. Para cada escenario incluido
devolvé probability_adjusted + confidence_low + confidence_high +
implications_refined (máximo 3 oraciones). Añadí dominant_pattern y
early_warning_level global."""

        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        raw = response.content.strip() if hasattr(response, "content") else str(response)

        # Extraer JSON
        m = re.search(r"\{[\s\S]*\}", raw)
        if not m:
            return candidates, {}
        try:
            parsed = json.loads(m.group(0))
        except json.JSONDecodeError:
            return candidates, {}

        # Aplicar ajustes a los candidatos
        updates = {s["id"]: s for s in parsed.get("scenarios", [])}
        updated: List[ForecastScenario] = []
        for c in candidates:
            u = updates.get(c.scenario_id)
            if u:
                prob_adj = float(u.get("probability_adjusted", c.probability))
                prob_adj = max(0.05, min(0.95, prob_adj))
                ci_low = u.get("confidence_low")
                ci_high = u.get("confidence_high")
                c.probability = round(prob_adj, 2)
                if ci_low is not None and ci_high is not None:
                    c.confidence_interval = (
                        max(0.0, min(1.0, float(ci_low))),
                        max(0.0, min(1.0, float(ci_high))),
                    )
                refined_impl = u.get("implications_refined")
                if refined_impl:
                    c.implications = refined_impl
            updated.append(c)

        # Retornamos (scenarios, llm_meta) — antes intentabamos monkey-patch
        # sobre la lista (updated.append_pattern = ...) que tiraba AttributeError
        # porque las listas Python no aceptan atributos arbitrarios.
        llm_meta = {
            "dominant_pattern": parsed.get("dominant_pattern"),
            "early_warning_level": parsed.get("early_warning_level"),
            "early_warning_note": parsed.get("early_warning_note"),
        }
        return updated, llm_meta

    # ── 3. HELPERS GLOBALES ─────────────────────────────────────────────
    @staticmethod
    def _describe_dominant_pattern(
        bundle: EvidenceBundle,
        scenarios: List[ForecastScenario],
        llm_meta: Optional[dict] = None,
    ) -> str:
        """Deriva una descripción del patrón dominante. Si el LLM lo proveyó
        en llm_meta['dominant_pattern'], usar ese; fallback heuristico."""
        if llm_meta and llm_meta.get("dominant_pattern"):
            return llm_meta["dominant_pattern"]

        top = max(scenarios, key=lambda s: s.probability, default=None)
        if not top:
            return "Sin patrones dominantes identificables sobre la evidencia actual."
        return f"{top.label} se proyecta como el escenario más probable ({top.probability*100:.0f}%)."

    @staticmethod
    def _compute_early_warning(
        scenarios: List[ForecastScenario],
        bundle: EvidenceBundle,
        llm_meta: Optional[dict] = None,
    ) -> tuple[str, str]:
        """Calcula nivel de alerta temprana. Si el LLM lo proveyó en
        llm_meta['early_warning_level'], usar ese; fallback heuristico."""
        llm_level = (llm_meta or {}).get("early_warning_level")
        llm_note = (llm_meta or {}).get("early_warning_note")
        if llm_level in ("green", "amber", "orange", "red"):
            return (
                llm_level,
                llm_note or f"Nivel {llm_level} según análisis del modelo.",
            )

        # Heurística de fallback
        crisis_prob = next(
            (s.probability for s in scenarios if s.scenario_id == "s_crisis_institucional"),
            0.0,
        )
        dispute_prob = next(
            (s.probability for s in scenarios if s.scenario_id == "s_dispute_prolongada"),
            0.0,
        )
        combined = max(crisis_prob, dispute_prob * 0.7)

        if combined >= 0.65:
            return "red", f"Alerta roja: combinación de disputa prolongada y crisis institucional proyectada ({combined*100:.0f}%)."
        if combined >= 0.45:
            return "orange", f"Alerta naranja: probabilidad elevada de disputa/crisis institucional ({combined*100:.0f}%)."
        if combined >= 0.25:
            return "amber", f"Alerta ámbar: indicadores mixtos con riesgo moderado ({combined*100:.0f}%)."
        return "green", "Indicadores dentro de rangos habituales de procesos electorales observados."
