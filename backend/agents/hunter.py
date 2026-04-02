"""DEMOCRAC.IA — Hunter Agent
Recolecta datos electorales en tiempo real de fuentes públicas peruanas.
Clasifica hallazgos con Claude LLM y los registra en el protocolo de observación.

Flujo:
  1. Detecta fuentes activas para la fase electoral actual
  2. Fetches RSS de JNE, ONPE, Andina, prensa digital
  3. Fetches OONI para anomalías de internet
  4. Claude clasifica cada ítem → categoría, severidad, hallazgo estructurado
  5. Registra en observation_store → regenera Cap. 7 automáticamente

Sin dependencias extra: usa httpx + xml stdlib + langchain_anthropic.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ── CONSTANTES ────────────────────────────────────────────────────────────────

HUNTER_OBSERVER_ID = "HUNTER-AUTO-001"

VALID_CATEGORIES = {
    "logistics", "security", "legal", "media", "digital",
    "counting", "results", "fraud_allegation", "hate_speech",
    "campaign_violation", "voter_suppression", "accessibility",
    "gender_violence", "disinformation", "voter_intimidation",
    "ballot_tampering", "media_restriction", "irregular_procedure", "other",
}

VALID_SEVERITIES = {"info", "low", "medium", "high", "critical"}

# ── PROMPT DE CLASIFICACIÓN ───────────────────────────────────────────────────

_SYSTEM_PROMPT = """Sos un analista especializado en observación electoral para DEMOCRAC.IA (PEIRS — Predictive Electoral Integrity & Risk System).

Analizás noticias de fuentes peruanas y determinás si son relevantes para la integridad del proceso electoral 2026.

CATEGORÍAS VÁLIDAS (usá exactamente estas):
- logistics: problemas logísticos del proceso electoral
- security: violencia, amenazas, seguridad física
- legal: violaciones al marco legal electoral, resoluciones judiciales
- media: cobertura mediática sesgada, restricciones a prensa
- digital: censura internet, desinformación digital, hacking
- counting: irregularidades en escrutinio o cómputo
- results: controversias sobre resultados
- fraud_allegation: alegaciones específicas de fraude
- hate_speech: discurso de odio contra grupos o candidatos
- campaign_violation: infracciones a normativa de campaña
- voter_suppression: obstaculización al ejercicio del voto
- accessibility: barreras para votantes con discapacidad o poblaciones vulnerables
- gender_violence: violencia política de género
- disinformation: campañas de desinformación, noticias falsas
- voter_intimidation: intimidación a votantes o candidatos
- ballot_tampering: manipulación de votos o actas
- media_restriction: restricciones a libertad de prensa
- irregular_procedure: procedimientos irregulares en el proceso
- other: relevante pero no encaja en las categorías anteriores

SEVERIDADES:
- info: hecho informativo sin impacto directo en integridad
- low: observación menor, no sistemática
- medium: irregularidad significativa que requiere monitoreo
- high: violación grave a estándares electorales internacionales
- critical: amenaza directa a la integridad del proceso

DERECHOS EN RIESGO — usá artículos específicos como:
["ICCPR Art. 25", "CADH Art. 23", "CDI Art. 3", "CEDAW Art. 7", "UNDRIP Art. 18"]

IMPORTANTE:
- Solo marcás como relevante lo que tiene impacto directo en integridad electoral
- El hallazgo debe ser técnico, conciso (1-2 oraciones), en español
- Si la noticia no tiene datos concretos, es poco relevante
- Noticias genéricas de campaña sin irregularidades → NOT relevant"""

_USER_TEMPLATE = """Fase electoral activa: {phase_label}
País: Perú — Elecciones Generales 12 de abril 2026

Analizá las siguientes noticias y retorná un JSON array con exactamente {n} objetos, uno por noticia, en el mismo orden.

Para noticias RELEVANTES:
{{
  "relevant": true,
  "category": "<categoría exacta>",
  "severity": "<info|low|medium|high|critical>",
  "finding": "<hallazgo técnico en 1-2 oraciones>",
  "rights_at_risk": ["<artículo>", ...],
  "location": "<región/departamento si se menciona, sino vacío>",
  "evidence_ref": "<URL de la noticia>"
}}

Para noticias NO relevantes:
{{"relevant": false}}

NOTICIAS:
{items_json}

Retorná SOLO el JSON array, sin markdown, sin comentarios."""


# ── CLASE PRINCIPAL ───────────────────────────────────────────────────────────

class HunterAgent:
    """
    Agente autónomo de recolección OSINT para procesos electorales.
    Fase preelectoral → Jornada → Postelectoral.
    """

    def __init__(self, llm, ooni_available: bool = False, ooni_get_summary=None):
        self.llm = llm
        self.ooni_available = ooni_available
        self.ooni_get_summary = ooni_get_summary

    # ── MÉTODO PRINCIPAL ──────────────────────────────────────────────────────

    async def run(
        self,
        country_code: str,
        phase: str,
        phase_label: str,
        dry_run: bool = False,
        max_items_per_source: int = 15,
        batch_size: int = 8,
    ) -> Dict[str, Any]:
        """
        Ejecuta el ciclo completo del Hunter para una fase dada.
        Retorna un resumen de los hallazgos registrados.
        dry_run=True → clasifica pero no registra (para testing).
        """
        from integrations.peru_sources import fetch_sources, dedupe_items

        result = {
            "phase": phase,
            "phase_label": phase_label,
            "country_code": country_code.upper(),
            "sources_fetched": [],
            "items_fetched": 0,
            "items_classified": 0,
            "items_registered": 0,
            "items_skipped": 0,
            "ooni_entries": 0,
            "errors": [],
            "entries": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
        }

        # ── 1. Fetch RSS ──────────────────────────────────────────────────────
        try:
            by_source = await fetch_sources(phase)
            for src, items in by_source.items():
                if items:
                    result["sources_fetched"].append(src)
        except Exception as e:
            result["errors"].append(f"RSS fetch error: {e}")
            by_source = {}

        # Aplanar y deduplicar
        all_items: List[Dict] = []
        for items in by_source.values():
            all_items.extend(items)
        all_items = dedupe_items(all_items, max_per_source=max_items_per_source)
        result["items_fetched"] = len(all_items)

        # ── 2. Fetch OONI ─────────────────────────────────────────────────────
        ooni_entries = []
        if self.ooni_available and self.ooni_get_summary:
            try:
                ooni_data = self.ooni_get_summary(country_code.upper(), days_back=3)
                ooni_entries = self._ooni_to_entries(ooni_data, phase)
                result["ooni_entries"] = len(ooni_entries)
                if ooni_entries:
                    result["sources_fetched"].append("ooni")
            except Exception as e:
                result["errors"].append(f"OONI error: {e}")

        # ── 3. Clasificar con LLM ─────────────────────────────────────────────
        classified: List[Dict] = []
        if all_items and self.llm:
            try:
                classified = await self._classify_batched(
                    all_items, phase, phase_label, batch_size
                )
                result["items_classified"] = len(classified)
            except Exception as e:
                result["errors"].append(f"LLM classification error: {e}")

        # Combinar RSS clasificados + OONI
        relevant = [c for c in classified if c.get("relevant")]
        all_entries = relevant + ooni_entries

        result["items_registered"] = len(all_entries)
        result["items_skipped"]    = len(all_items) - len(relevant)
        result["entries"]          = all_entries

        return result

    # ── CLASIFICACIÓN LLM ─────────────────────────────────────────────────────

    async def _classify_batched(
        self,
        items: List[Dict],
        phase: str,
        phase_label: str,
        batch_size: int,
    ) -> List[Dict]:
        """Clasifica ítems en batches para no superar el contexto del LLM."""
        all_classified: List[Dict] = []

        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            batch_results = await self._classify_batch(batch, phase, phase_label)
            all_classified.extend(batch_results)

        return all_classified

    async def _classify_batch(
        self, items: List[Dict], phase: str, phase_label: str
    ) -> List[Dict]:
        """Clasifica un batch de ítems. Retorna lista con flag 'relevant'."""
        from langchain_core.messages import HumanMessage, SystemMessage

        # Construir representación compacta para el prompt
        items_for_prompt = [
            {
                "n":     idx + 1,
                "title": item.get("title", ""),
                "desc":  item.get("description", "")[:300],
                "url":   item.get("url", ""),
                "src":   item.get("source", ""),
            }
            for idx, item in enumerate(items)
        ]

        user_msg = _USER_TEMPLATE.format(
            phase_label=phase_label,
            n=len(items),
            items_json=json.dumps(items_for_prompt, ensure_ascii=False, indent=2),
        )

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=user_msg),
            ])
            raw = response.content.strip()

            # Limpiar posible markdown ```json ... ``` del response
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            parsed = json.loads(raw)
            if not isinstance(parsed, list) or len(parsed) != len(items):
                return []

            # Enriquecer cada resultado con metadata del ítem original
            enriched: List[Dict] = []
            for item, classification in zip(items, parsed):
                if not isinstance(classification, dict):
                    continue
                if not classification.get("relevant"):
                    enriched.append({"relevant": False})
                    continue

                # Validar y sanitizar campos
                cat = classification.get("category", "other")
                if cat not in VALID_CATEGORIES:
                    cat = "other"
                sev = classification.get("severity", "info")
                if sev not in VALID_SEVERITIES:
                    sev = "info"

                enriched.append({
                    "relevant":       True,
                    "category":       cat,
                    "severity":       sev,
                    "finding":        str(classification.get("finding", item.get("title", "")))[:500],
                    "rights_at_risk": classification.get("rights_at_risk", []),
                    "location":       str(classification.get("location", "")),
                    "evidence_ref":   classification.get("evidence_ref") or item.get("url", ""),
                    "source":         item.get("source", "unknown"),
                    "title":          item.get("title", ""),
                    "published":      item.get("published", ""),
                    "observer_id":    HUNTER_OBSERVER_ID,
                    "verified":       False,
                    "credibility":    "medium",
                })

            return enriched

        except (json.JSONDecodeError, Exception):
            # Si el LLM falla, retornar lista vacía de clasificaciones
            return []

    # ── OONI → ENTRY ─────────────────────────────────────────────────────────

    def _ooni_to_entries(self, ooni_data: Dict, phase: str) -> List[Dict]:
        """Convierte resumen OONI a ObservationEntry-like dicts."""
        if not ooni_data or not ooni_data.get("available"):
            return []

        entries: List[Dict] = []
        anomalies = ooni_data.get("anomalies", [])

        for anomaly in anomalies[:10]:  # máximo 10 por ciclo
            domain  = anomaly.get("domain", "desconocido")
            rate    = anomaly.get("anomaly_rate", 0)
            if rate < 0.1:
                continue   # < 10% anomalía → ignorar

            severity = (
                "critical" if rate >= 0.7 else
                "high"     if rate >= 0.4 else
                "medium"   if rate >= 0.2 else
                "low"
            )

            finding = (
                f"OONI detectó anomalía de acceso al dominio '{domain}' "
                f"(tasa: {rate:.0%}). Posible bloqueo o restricción de internet "
                f"en el período pre-electoral. Datos: {ooni_data.get('period', 'últimos 3 días')}."
            )

            entries.append({
                "relevant":       True,
                "category":       "digital",
                "severity":       severity,
                "finding":        finding,
                "rights_at_risk": ["ICCPR Art. 19", "CADH Art. 13"],
                "location":       "",
                "evidence_ref":   anomaly.get("report_url", "https://ooni.org/pe"),
                "source":         "ooni",
                "title":          f"Anomalía OONI: {domain}",
                "published":      anomaly.get("timestamp", ""),
                "observer_id":    HUNTER_OBSERVER_ID,
                "verified":       True,     # OONI es fuente primaria verificada
                "credibility":    "high",
            })

        return entries


# ── HELPER: convertir HunterEntry a ObservationEntry dict ────────────────────

def hunter_entry_to_observation(
    entry: Dict,
    phase: str,
    country_code: str,
) -> Dict:
    """
    Convierte un hallazgo del Hunter al formato esperado por observation_store.
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "entry_id":       str(uuid.uuid4())[:8],
        "timestamp":      entry.get("published") or now,
        "observer_id":    entry.get("observer_id", HUNTER_OBSERVER_ID),
        "location":       entry.get("location", ""),
        "phase":          phase,
        "category":       entry.get("category", "other"),
        "finding":        entry.get("finding", ""),
        "severity":       entry.get("severity", "info"),
        "rights_at_risk": entry.get("rights_at_risk", []),
        "verified":       entry.get("verified", False),
        "verified_by":    "HUNTER-OONI" if entry.get("source") == "ooni" else None,
        "evidence_ref":   entry.get("evidence_ref", ""),
        "recorded_at":    now,
        # Campos específicos
        "fraud_type":     None,
        "credibility":    entry.get("credibility", "medium"),
        "source_org":     f"Hunter/{entry.get('source', 'rss')}",
        "target_group":   None,
        "platform":       None,
        "reach_estimate": None,
        # Metadata Hunter
        "hunter_title":   entry.get("title", ""),
        "hunter_source":  entry.get("source", ""),
    }
