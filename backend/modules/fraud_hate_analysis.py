"""
DEMOCRAC.IA / PEIRS — Análisis de Fraude Electoral y Discurso de Odio
Módulo de análisis específico para las 3 fases del protocolo de observación.

Integra con:
  - ObservationEntry (categorías fraud_allegation, hate_speech)
  - RAG legal corpus (rag/)
  - Capítulo 7 del informe (_generate_observation_chapter)
"""

from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime, timezone

# ── Taxonomías ────────────────────────────────────────────────────────────────

FRAUD_TYPES = {
    "padron":          "Manipulación del padrón electoral",
    "vote_buying":     "Compra o coacción del voto",
    "intimidation":    "Intimidación de electores o candidatos",
    "polling_day":     "Irregularidades en jornada (voto múltiple, urnas, actas)",
    "counting":        "Fraude en escrutinio o transmisión de resultados",
    "results":         "Manipulación de resultados o sistema informático",
    "candidate":       "Inhabilitación irregular de candidatos",
    "financing":       "Financiamiento ilícito de campaña",
    "other":           "Otro tipo de irregularidad",
}

HATE_SPEECH_TARGETS = {
    "women_candidates":  "Candidatas mujeres",
    "indigenous":        "Pueblos indígenas / comunidades originarias",
    "lgbtq":             "Personas LGBTQ+",
    "migrants":          "Migrantes / extranjeros",
    "ethnic_minority":   "Minorías étnicas",
    "religious":         "Comunidades religiosas",
    "political_opponent":"Oponentes políticos (sin característica protegida)",
    "journalists":       "Periodistas / observadores",
    "other":             "Otro grupo",
}

CREDIBILITY_SCALE = {
    "confirmed":    ("CONFIRMADO", "🔴", "Documentado con evidencia primaria verificada"),
    "high":         ("ALTA",       "🟠", "Múltiples fuentes independientes, patrón consistente"),
    "medium":       ("MEDIA",      "🟡", "Fuente creíble, sin corroboración independiente aún"),
    "low":          ("BAJA",       "🟢", "Afirmación unilateral, sin evidencia documental"),
    "unverified":   ("SIN VERIFICAR", "⚪", "Recibido, pendiente de análisis"),
}

HATE_SEVERITY_ICCPR = {
    "critical": "Art. 20(2) ICCPR — incitación a la violencia; Art. 7 CEDAW — violencia política de género",
    "high":     "Art. 20(2) ICCPR — apología del odio; Art. 25 ICCPR — supresión de participación",
    "medium":   "Art. 19 ICCPR (límites) + Art. 25 ICCPR — efecto disuasorio sobre participación",
    "low":      "Art. 19 ICCPR — observar; podría escalar si hay patrón coordinado",
}

FRAUD_ICCPR = {
    "padron":       ["ICCPR Art. 25(b)", "GC25 párr. 11 — procedimientos de registro justos"],
    "vote_buying":  ["ICCPR Art. 25(b)", "GC25 párr. 19 — voto libre de influencias indebidas"],
    "intimidation": ["ICCPR Art. 25(b)", "GC25 párr. 20 — prohibición de intimidación y coacción"],
    "polling_day":  ["ICCPR Art. 25(b)", "CADH Art. 23(1)(b)", "CDI Art. 3"],
    "counting":     ["ICCPR Art. 25(b)", "GC25 párr. 25 — escrutinio transparente", "CADH Art. 23(1)(b)"],
    "results":      ["ICCPR Art. 25(b)", "CDI Art. 6 — transparencia electoral", "CADH Art. 23(1)(c)"],
    "candidate":    ["ICCPR Art. 25(b)", "CADH Art. 23(2)", "Castañeda Gutman vs. México (CIDH 2008)"],
    "financing":    ["UNCAC Art. 7", "ICCPR Art. 25(b) — competencia electoral equitativa"],
    "other":        ["ICCPR Art. 25", "CADH Art. 23"],
}


# ── Clases de análisis ────────────────────────────────────────────────────────

class FraudAllegationAnalysis:
    """Analiza un conjunto de alegaciones de fraude y genera reporte estructurado."""

    def __init__(self, entries: List[Dict]):
        self.entries = [e for e in entries if e.get("category") == "fraud_allegation"]

    @property
    def total(self) -> int:
        return len(self.entries)

    def by_fraud_type(self) -> Dict[str, List[Dict]]:
        """Agrupa alegaciones por tipo de fraude."""
        result: Dict[str, List[Dict]] = {}
        for e in self.entries:
            ft = e.get("fraud_type", "other")
            result.setdefault(ft, []).append(e)
        return result

    def by_phase(self) -> Dict[str, List[Dict]]:
        """Agrupa por fase electoral."""
        result: Dict[str, List[Dict]] = {}
        for e in self.entries:
            ph = e.get("phase", "unknown")
            result.setdefault(ph, []).append(e)
        return result

    def credibility_distribution(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self.entries:
            c = e.get("credibility", "unverified")
            counts[c] = counts.get(c, 0) + 1
        return counts

    def high_credibility_entries(self) -> List[Dict]:
        return [e for e in self.entries if e.get("credibility") in ("confirmed", "high")]

    def pattern_detected(self) -> bool:
        """True si hay ≥3 alegaciones del mismo tipo o ≥2 en el mismo distrito."""
        by_type = self.by_fraud_type()
        if any(len(v) >= 3 for v in by_type.values()):
            return True
        locations = [e.get("location", "") for e in self.entries if e.get("location")]
        loc_counts: Dict[str, int] = {}
        for loc in locations:
            district = loc.split(",")[0].strip() if "," in loc else loc
            loc_counts[district] = loc_counts.get(district, 0) + 1
        return any(v >= 2 for v in loc_counts.values())

    def iccpr_violations(self) -> List[str]:
        """Retorna conjunto de artículos ICCPR/CADH potencialmente vulnerados."""
        violations: set = set()
        for e in self.entries:
            if e.get("credibility") in ("confirmed", "high", "medium"):
                ft = e.get("fraud_type", "other")
                for art in FRAUD_ICCPR.get(ft, FRAUD_ICCPR["other"]):
                    violations.add(art)
        return sorted(violations)

    def render_markdown(self) -> str:
        """Genera sección markdown para el capítulo 7."""
        if not self.entries:
            return ""

        cred_dist = self.credibility_distribution()
        high_cred = self.high_credibility_entries()
        pattern   = self.pattern_detected()
        violations = self.iccpr_violations()

        # Tabla resumen
        rows = ["| # | Fase | Tipo | Ubicación | Alegación | Credibilidad | Fuente |",
                "|---|---|---|---|---|---|---|"]
        for i, e in enumerate(self.entries, 1):
            ft_label  = FRAUD_TYPES.get(e.get("fraud_type", "other"), "Otro")
            cred_key  = e.get("credibility", "unverified")
            cred_info = CREDIBILITY_SCALE.get(cred_key, CREDIBILITY_SCALE["unverified"])
            phase_map = {"pre_election": "Pre-48h", "election_day": "Jornada", "post_election": "Post-72h"}
            rows.append(
                f"| {i} | {phase_map.get(e.get('phase',''), '—')} | {ft_label} "
                f"| {(e.get('location') or '—')[:25]} "
                f"| {(e.get('finding') or '')[:60]}… "
                f"| {cred_info[1]} {cred_info[0]} "
                f"| {(e.get('source_org') or e.get('observer_id') or '—')} |"
            )
        table = "\n".join(rows)

        pattern_alert = (
            "\n> ⚠️ **PATRÓN DETECTADO**: Se registran alegaciones similares en múltiples ubicaciones "
            "o del mismo tipo. Esto puede indicar fraude sistemático. Se recomienda investigación inmediata.\n"
            if pattern else ""
        )

        violations_text = ""
        if violations:
            violations_text = (
                "\n**Derechos potencialmente vulnerados (alegaciones de credibilidad media-alta):**\n"
                + "\n".join(f"- {v}" for v in violations)
                + "\n"
            )

        high_cred_text = ""
        if high_cred:
            high_cred_text = f"\n> 🔴 **{len(high_cred)} alegaciones de alta credibilidad** requieren investigación formal ante JNE/Fiscalía Electoral.\n"

        cred_summary = " | ".join(
            f"{CREDIBILITY_SCALE.get(k, ('?','',''))[1]} {CREDIBILITY_SCALE.get(k, (k,'',''))[0]}: {v}"
            for k, v in sorted(cred_dist.items())
        )

        return (
            f"\n#### 7.x.1 Alegaciones de Fraude Electoral ({self.total} total)\n\n"
            f"> Distribución de credibilidad: {cred_summary}\n"
            f"{high_cred_text}"
            f"{pattern_alert}\n"
            f"{table}\n"
            f"{violations_text}"
        )


class HateSpeechAnalysis:
    """Analiza incidentes de discurso de odio y genera reporte estructurado."""

    def __init__(self, entries: List[Dict]):
        self.entries = [e for e in entries if e.get("category") == "hate_speech"]

    @property
    def total(self) -> int:
        return len(self.entries)

    def by_target(self) -> Dict[str, List[Dict]]:
        result: Dict[str, List[Dict]] = {}
        for e in self.entries:
            tg = e.get("target_group", "other")
            result.setdefault(tg, []).append(e)
        return result

    def critical_or_high(self) -> List[Dict]:
        return [e for e in self.entries if e.get("severity") in ("critical", "high")]

    def suppression_risk(self) -> bool:
        """True si hay evidencia de efecto disuasorio sobre participación."""
        for e in self.entries:
            finding = (e.get("finding") or "").lower()
            if any(kw in finding for kw in ["no votará", "amenaza", "renuncia", "retira", "abandona"]):
                return True
        return len(self.critical_or_high()) >= 2

    def iccpr_framework(self) -> str:
        """Retorna el marco legal aplicable según la severidad más alta detectada."""
        severities = [e.get("severity", "low") for e in self.entries]
        order = ["critical", "high", "medium", "low", "info"]
        top = next((s for s in order if s in severities), "low")
        return HATE_SEVERITY_ICCPR.get(top, HATE_SEVERITY_ICCPR["low"])

    def render_markdown(self) -> str:
        if not self.entries:
            return ""

        by_target  = self.by_target()
        critical_h = self.critical_or_high()
        suppression = self.suppression_risk()
        iccpr       = self.iccpr_framework()

        # Tabla de incidentes
        rows = ["| # | Fase | Grupo objetivo | Plataforma | Alcance | Hallazgo | Severidad |",
                "|---|---|---|---|---|---|---|"]
        phase_map = {"pre_election": "Pre-48h", "election_day": "Jornada", "post_election": "Post-72h"}
        sev_badge = {"critical": "🚨 CRÍTICO", "high": "🔴 ALTO", "medium": "🟡 MEDIO",
                     "low": "🟢 BAJO", "info": "ℹ️ INFO"}
        for i, e in enumerate(self.entries, 1):
            tg_label = HATE_SPEECH_TARGETS.get(e.get("target_group", "other"), "Otro")
            rows.append(
                f"| {i} | {phase_map.get(e.get('phase',''), '—')} "
                f"| {tg_label} "
                f"| {(e.get('platform') or '—')} "
                f"| {(e.get('reach_estimate') or '—')} "
                f"| {(e.get('finding') or '')[:60]}… "
                f"| {sev_badge.get(e.get('severity','info'), '—')} |"
            )
        table = "\n".join(rows)

        targets_summary = ", ".join(
            f"{HATE_SPEECH_TARGETS.get(tg, tg)} ({len(ents)})"
            for tg, ents in sorted(by_target.items(), key=lambda x: -len(x[1]))
        )

        suppression_alert = (
            "\n> ⚠️ **RIESGO DE SUPRESIÓN**: Los incidentes de discurso de odio presentan "
            "características que podrían tener efecto disuasorio sobre la participación electoral "
            "del grupo afectado. Ver CEDAW Rec. Gen. 35 y ICCPR Art. 25.\n"
            if suppression else ""
        )

        vdgp_alert = ""
        if any(e.get("target_group") in ("women_candidates", "lgbtq") for e in critical_h):
            vdgp_alert = (
                "\n> 🔴 **VDGP DETECTADA**: Violencia Digital de Género Político contra candidatas "
                "o personas LGBTQ+. Ley 31170 (Perú) y Art. 7 CEDAW — obligación de investigar y sancionar.\n"
            )

        return (
            f"\n#### 7.x.2 Discurso de Odio e Incidentes de Violencia Digital ({self.total} total)\n\n"
            f"> Grupos afectados: {targets_summary}\n"
            f"{suppression_alert}"
            f"{vdgp_alert}\n"
            f"{table}\n\n"
            f"**Marco legal aplicable:** {iccpr}\n"
        )


# ── Función principal de análisis combinado ───────────────────────────────────

def analyze_fraud_and_hate(entries: List[Dict]) -> Dict:
    """
    Analiza el conjunto completo de hallazgos de observación en busca de
    fraude y discurso de odio. Retorna análisis estructurado + markdown.

    Usado por _generate_observation_chapter() en app.py.
    """
    fraud = FraudAllegationAnalysis(entries)
    hate  = HateSpeechAnalysis(entries)

    # Intentar enriquecer con RAG si disponible
    rag_fraud_refs = []
    rag_hate_refs  = []
    try:
        from rag import query_fraud_context, query_hate_speech_context, RAG_AVAILABLE
        if RAG_AVAILABLE:
            if fraud.total > 0:
                top_ft = max(fraud.by_fraud_type(), key=lambda k: len(fraud.by_fraud_type()[k]), default="other")
                rag_fraud_refs = query_fraud_context(fraud_type=FRAUD_TYPES.get(top_ft, top_ft))
            if hate.total > 0:
                top_tg = max(hate.by_target(), key=lambda k: len(hate.by_target()[k]), default="other")
                rag_hate_refs = query_hate_speech_context(target_group=HATE_SPEECH_TARGETS.get(top_tg, top_tg))
    except Exception:
        pass

    return {
        "fraud": {
            "total": fraud.total,
            "pattern_detected": fraud.pattern_detected(),
            "high_credibility": len(fraud.high_credibility_entries()),
            "iccpr_violations": fraud.iccpr_violations(),
            "rag_references": rag_fraud_refs,
            "markdown": fraud.render_markdown(),
        },
        "hate_speech": {
            "total": hate.total,
            "suppression_risk": hate.suppression_risk(),
            "critical_or_high": len(hate.critical_or_high()),
            "iccpr_framework": hate.iccpr_framework(),
            "rag_references": rag_hate_refs,
            "markdown": hate.render_markdown(),
        },
        "has_significant_findings": (
            fraud.total > 0 or hate.total > 0 or
            fraud.pattern_detected() or hate.suppression_risk()
        ),
    }
