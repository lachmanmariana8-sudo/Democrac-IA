"""
ReportDesigner — Structurer (Fase B).

Transforma el raw data del sistema (entries del Hunter, alertas, datasets) en
una estructura semántica ordenada lista para el Composer.

Pipeline interno:
  1. load_data(cc) — tira de observation_store + tabla alerts + reports_store
  2. dedupe(entries) — normaliza URLs, agrupa por (cat, url_norm, date)
  3. classify_themes(entries) — 1-3 temas canónicos por hallazgo
  4. prioritize(entries) — score = severity * recency * source_credibility
  5. build_section_findings(entries, audience) — asigna hallazgos a secciones

Fase B NO usa LLM. Solo lógica Python + regex + counters.
"""
from __future__ import annotations

import re
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from agents.report_designer.models import FindingRef


# ── Temas canónicos ───────────────────────────────────────────────────────
# Cada tema tiene un conjunto de keywords que, si aparecen en el finding o
# title del hallazgo, lo asignan a ese tema. Un hallazgo puede tener 1-3
# temas simultáneos. Estos temas alimentan las secciones "temas_criticos" /
# "3_temas_mas_criticos" / "findings" según la audiencia.

THEMES: Dict[str, Dict[str, Any]] = {
    "crisis_logistica_emb": {
        "label": "Crisis logística del organismo electoral",
        "keywords": ["onpe", "material electoral", "instalación de mesa", "instalar mesa",
                     "no llegó", "sin material", "corvetto", "distribución", "logística",
                     "no pudieron votar", "sin sufragar", "mesa de sufragio", "personero",
                     "miembro de mesa", "retraso", "demora"],
        "categories": ["logistics", "voter_suppression", "accessibility", "other"],
    },
    "tecnologia_electoral_ia": {
        "label": "Tecnología electoral e IA no auditada",
        "keywords": ["stae", "venp", "voto electrónico", "sistema informático", "ia electoral",
                     "inteligencia artificial", "sce", "spr", "auditoría", "código fuente",
                     "iriarte", "tecnológico"],
        "categories": ["digital", "counting"],
    },
    "desinformacion": {
        "label": "Desinformación y manipulación informativa",
        "keywords": ["falso", "falsa", "engañoso", "mentira", "desinforma", "verificación",
                     "fact-check", "fact check", "idl-reporteros", "fake", "deepfake",
                     "bot", "red social", "imagen manipulada"],
        "categories": ["disinformation"],
    },
    "integridad_escrutinio": {
        "label": "Integridad del escrutinio y conteo",
        "keywords": ["cédula", "cedula", "acta", "escrutinio", "conteo", "rompió",
                     "destruy", "adulter", "fiscalizadora", "manipulación de votos",
                     "irregularidad en mesa", "ballot"],
        "categories": ["ballot_tampering", "counting", "irregular_procedure", "fraud_allegation"],
    },
    "captura_institucional": {
        "label": "Captura institucional y conflictos de poder",
        "keywords": ["captura", "coalición", "impunidad", "pacto", "concertad",
                     "intereses particulares", "bancada", "reforma legal", "ley corta"],
        "categories": ["legal", "other"],
    },
    "financiamiento_campana": {
        "label": "Financiamiento de campaña y transparencia",
        "keywords": ["financiamiento", "aporte", "aportes", "reporte de gastos",
                     "campaña electoral", "donación", "obras", "belmont", "recompensa",
                     "s/20.000", "s/ 20", "soborno"],
        "categories": ["campaign_violation", "fraud_allegation"],
    },
    "genero_violencia_politica": {
        "label": "Violencia política de género",
        "keywords": ["candidata", "mujer", "género", "acoso político", "ley 31170",
                     "observa igualdad", "paridad", "alternancia", "ley 31030",
                     "violencia política"],
        "categories": ["hate_speech", "other"],
    },
    "medios_libertad_prensa": {
        "label": "Medios y libertad de prensa",
        "keywords": ["periodista", "prensa", "libertad de expresión", "medio", "censura",
                     "restricción a medio", "ataque a periodista", "rsf"],
        "categories": ["media", "campaign_violation"],
    },
    "violencia_politica": {
        "label": "Violencia política y seguridad electoral",
        "keywords": ["violencia", "ataque", "amenaza", "muerte", "muerto", "mitin",
                     "campaña electoral", "candidato herido", "accidente", "fallec",
                     "seguridad"],
        "categories": ["security", "other"],
    },
    "resolucion_disputas": {
        "label": "Resolución de disputas electorales",
        "keywords": ["impugnación", "nulidad", "apelación", "recurso", "jee",
                     "jurado electoral especial", "jne denuncia", "jnj", "medida cautelar",
                     "proclamación"],
        "categories": ["legal", "results"],
    },
    "responsabilidad_penal": {
        "label": "Responsabilidad penal e institucional",
        "keywords": ["denuncia penal", "fiscalía", "fiscal de la nación", "detención",
                     "flagrancia", "procesado", "prisión", "investigación penal",
                     "contraloría", "galaga", "colusión", "omisión de funciones"],
        "categories": ["legal", "fraud_allegation"],
    },
}


# ── Pesos para priorización ──────────────────────────────────────────────
SEVERITY_WEIGHT = {"critical": 10, "high": 7, "medium": 3, "moderate": 3, "low": 1, "info": 0.5}
SOURCE_CREDIBILITY = {
    "ooni": 1.5, "idl": 1.4, "jne": 1.3, "onpe": 1.3,
    "elcomercio": 1.0, "gestion": 1.0, "rpp": 1.0,
    "andina": 0.9, "wayka": 0.8, "": 0.5, None: 0.5,
}


class Structurer:
    """Carga entries + alerts + datasets → esqueleto ordenado para el Composer."""

    def __init__(self, country_code: str):
        self.country_code = country_code.upper()
        self._entries: List[Dict] = []
        self._alerts: List[Dict] = []
        self._report_base: Dict = {}

    # ── 1. LOADER ───────────────────────────────────────────────────────
    def load_from_stores(
        self,
        observation_store: Optional[Dict] = None,
        alerts_loader=None,
        reports_store: Optional[Dict] = None,
    ) -> None:
        """Carga datos desde las estructuras en memoria del backend FastAPI.
        Todos los argumentos son opcionales — si faltan, Structurer trabaja con
        lo que haya y genera stats parciales."""
        if observation_store and self.country_code in observation_store:
            session = observation_store[self.country_code]
            self._entries = list(session.get("entries", []))

        if alerts_loader:
            try:
                self._alerts = list(alerts_loader(self.country_code, limit=500))
            except Exception:
                self._alerts = []

        if reports_store:
            # Tomar el último report del país si existe
            latest = None
            for run_id, r in reports_store.items():
                if (r.get("country_code") or r.get("country")) == self.country_code:
                    if latest is None or r.get("timestamp", "") > latest.get("timestamp", ""):
                        latest = r
            if latest:
                self._report_base = latest

    # ── 2. DEDUPE ───────────────────────────────────────────────────────
    @staticmethod
    def _normalize_url(url: Optional[str]) -> str:
        if not url:
            return ""
        try:
            p = urlparse(url.strip().lower())
            # quitar query strings y trailing slash
            path = (p.path or "").rstrip("/")
            return f"{p.netloc}{path}"
        except Exception:
            return (url or "").strip().lower()

    def dedupe_entries(self) -> List[Dict]:
        """Colapsa duplicados por (category, URL normalizada, fecha YYYY-MM-DD).
        Conserva el entry más reciente del grupo."""
        groups: Dict[Tuple[str, str, str], Dict] = {}
        for e in self._entries:
            cat = (e.get("category") or "other").lower()
            url_norm = self._normalize_url(e.get("evidence_ref"))
            date_key = (e.get("recorded_at") or "")[:10]
            # Si no hay URL, dedupear por (cat, finding[:80], date)
            key_extra = url_norm or (e.get("finding", "")[:80] or "").lower()
            key = (cat, key_extra, date_key)

            existing = groups.get(key)
            if existing is None or (e.get("recorded_at", "") > existing.get("recorded_at", "")):
                groups[key] = e

        return list(groups.values())

    # ── 3. CLASSIFY THEMES ──────────────────────────────────────────────
    @staticmethod
    def _themes_for(entry: Dict) -> List[str]:
        """Asigna 1-3 temas canónicos al entry según keywords + category."""
        text = " ".join([
            (entry.get("finding") or "").lower(),
            (entry.get("hunter_title") or entry.get("title") or "").lower(),
        ])
        category = (entry.get("category") or "other").lower()

        scores: Dict[str, int] = {}
        for theme_id, theme in THEMES.items():
            s = 0
            # Match por categoría
            if category in theme["categories"]:
                s += 3
            # Match por keywords
            for kw in theme["keywords"]:
                if kw in text:
                    s += 1
            if s > 0:
                scores[theme_id] = s

        if not scores:
            return []

        # Top 3 temas por score, mínimo score 2
        ordered = sorted(scores.items(), key=lambda x: -x[1])
        return [t for t, s in ordered[:3] if s >= 2]

    def classify_entries(self, entries: List[Dict]) -> List[Dict]:
        """Agrega _themes a cada entry (lista de theme_ids)."""
        out = []
        for e in entries:
            e_copy = dict(e)
            e_copy["_themes"] = self._themes_for(e)
            out.append(e_copy)
        return out

    # ── 4. PRIORITIZE ───────────────────────────────────────────────────
    @staticmethod
    def _entry_score(entry: Dict, now: datetime) -> float:
        sev = (entry.get("severity") or "low").lower()
        sw = SEVERITY_WEIGHT.get(sev, 1.0)

        # Recency decay exponencial con tiempo característico = 3 días
        try:
            dt = datetime.fromisoformat((entry.get("recorded_at") or "").replace("Z", "+00:00"))
            days = max(0, (now - dt).total_seconds() / 86400.0)
        except Exception:
            days = 30
        rw = 1.0 + 2.0 * math.exp(-days / 3.0)

        src = (entry.get("hunter_source") or entry.get("source") or "").lower()
        cw = SOURCE_CREDIBILITY.get(src, SOURCE_CREDIBILITY.get(None, 0.5))

        return sw * rw * cw

    def prioritize(self, entries: List[Dict]) -> List[Dict]:
        """Ordena entries por score descendente."""
        now = datetime.now(timezone.utc)
        scored = [(self._entry_score(e, now), e) for e in entries]
        scored.sort(key=lambda x: -x[0])
        out = []
        for score, e in scored:
            e_copy = dict(e)
            e_copy["_priority_score"] = round(score, 2)
            out.append(e_copy)
        return out

    # ── 5. SECTION ASSIGNMENT ───────────────────────────────────────────
    def build_theme_buckets(self, entries: List[Dict]) -> Dict[str, List[Dict]]:
        """Agrupa entries por tema canónico. Un entry puede aparecer en múltiples buckets."""
        buckets: Dict[str, List[Dict]] = defaultdict(list)
        for e in entries:
            for theme in e.get("_themes", []):
                buckets[theme].append(e)
        return dict(buckets)

    def to_finding_ref(self, entry: Dict) -> FindingRef:
        return FindingRef(
            entry_id=entry.get("entry_id"),
            finding=(entry.get("finding") or "")[:500],
            category=entry.get("category") or "other",
            severity=entry.get("severity") or "info",
            source_name=entry.get("hunter_source") or entry.get("source"),
            source_title=entry.get("hunter_title") or entry.get("title"),
            source_url=entry.get("evidence_ref"),
            recorded_at=entry.get("recorded_at"),
        )

    # ── PIPELINE COMPLETO ───────────────────────────────────────────────
    def run(self) -> Dict[str, Any]:
        """Ejecuta los 5 pasos en secuencia y devuelve el resultado estructurado."""
        deduped = self.dedupe_entries()
        classified = self.classify_entries(deduped)
        prioritized = self.prioritize(classified)
        theme_buckets = self.build_theme_buckets(prioritized)

        # Rankeo de temas por # de entries high+critical
        theme_ranking = []
        for theme_id, bucket in theme_buckets.items():
            high_crit = sum(1 for e in bucket if (e.get("severity") or "").lower() in ("high", "critical"))
            theme_ranking.append({
                "theme_id": theme_id,
                "label": THEMES[theme_id]["label"],
                "total": len(bucket),
                "high_critical": high_crit,
                "top_findings": [self.to_finding_ref(e) for e in bucket[:3]],
            })
        theme_ranking.sort(key=lambda x: (-x["high_critical"], -x["total"]))

        # Timeline agregado por día × severidad
        timeline_buckets: Dict[str, Counter] = defaultdict(Counter)
        for e in prioritized:
            day = (e.get("recorded_at") or "")[:10]
            if not day:
                continue
            sev = (e.get("severity") or "info").lower()
            timeline_buckets[day][sev] += 1
        timeline = [
            {"day": day, "counts": dict(counts)}
            for day, counts in sorted(timeline_buckets.items())
        ]

        # Source distribution
        source_dist = Counter(
            (e.get("hunter_source") or e.get("source") or "unknown").lower()
            for e in prioritized
        )

        # Severidad distribution
        sev_dist = Counter((e.get("severity") or "info").lower() for e in prioritized)
        # Normalizar moderate → medium
        if "moderate" in sev_dist:
            sev_dist["medium"] = sev_dist.get("medium", 0) + sev_dist.pop("moderate")

        # Stats finales
        days = len(timeline)
        stats = {
            "total_findings": len(prioritized),
            "critical": sev_dist.get("critical", 0),
            "high": sev_dist.get("high", 0),
            "medium": sev_dist.get("medium", 0),
            "low": sev_dist.get("low", 0),
            "info": sev_dist.get("info", 0),
            "days_covered": days,
            "sources_count": sum(1 for s in source_dist if s != "unknown"),
            "alerts_dispatched": len(self._alerts),
        }

        # Top hallazgos priorizados (para ranking general)
        top_overall = [self.to_finding_ref(e) for e in prioritized[:15]]

        return {
            "entries_deduped": prioritized,
            "theme_ranking": theme_ranking,
            "timeline": timeline,
            "source_distribution": dict(source_dist),
            "severity_distribution": dict(sev_dist),
            "top_findings_overall": top_overall,
            "stats": stats,
        }
