"""
DEMOCRAC.IA / PEIRS — FieldDataValidationAgent (Agent 5)
Validación, deduplicación y detección de patrones en hallazgos de campo.

Corre automáticamente al ingresar cada entry via POST /api/observation/{cc}/entry.
No bloquea el ingreso — emite warnings que se devuelven al observador en la respuesta.

Funciones principales:
  validate_entry(entry, existing)     → ValidationResult para un hallazgo nuevo
  detect_patterns(entries)            → PatternReport sobre toda la sesión
  render_pattern_markdown(patterns)   → Sección markdown para Cap. 7
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


# ── Constantes ────────────────────────────────────────────────────────────────

DUPLICATE_WINDOW_MINUTES = 5      # Ventana temporal para considerar duplicado potencial
PATTERN_MIN_SAME_DISTRICT = 3     # Mínimo hallazgos graves por distrito = patrón sistemático
PATTERN_MIN_SAME_TYPE = 3         # Mínimo por categoría = patrón de tipo
ESCALATION_WINDOW_HOURS = 2       # Ventana para detectar escalada de severidad
SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

REQUIRED_FIELDS_BY_CATEGORY = {
    "fraud_allegation": ["location", "fraud_type", "credibility"],
    "hate_speech":      ["target_group", "platform"],
    "security":         ["location"],
    "counting":         ["location", "observer_id"],
    "results":          ["location", "observer_id", "evidence_ref"],
}

CREDIBILITY_WEIGHTS = {
    "confirmed": 1.0,
    "high":      0.8,
    "medium":    0.5,
    "low":       0.2,
    "unverified": 0.1,
}


# ── Estructuras de resultado ──────────────────────────────────────────────────

@dataclass
class ValidationResult:
    """Resultado de validar un hallazgo individual."""
    valid: bool = True
    errors: List[str] = field(default_factory=list)       # Bloquean el ingreso (reservado para futuro)
    warnings: List[str] = field(default_factory=list)     # No bloquean; se devuelven al observador
    duplicate_of: Optional[str] = None                    # entry_id del posible duplicado
    suggested_rights: List[str] = field(default_factory=list)
    quality_score: float = 1.0                            # 0.0–1.0: calidad del hallazgo


@dataclass
class GeographicPattern:
    """Patrón detectado en una zona geográfica."""
    district: str
    entry_count: int
    severity_max: str
    categories: List[str]
    entry_ids: List[str]
    alert_level: str    # "watch"|"concern"|"critical"
    iccpr_ref: str


@dataclass
class PatternReport:
    """Informe completo de patrones detectados en una sesión."""
    geographic_patterns: List[GeographicPattern] = field(default_factory=list)
    category_clusters: Dict[str, int] = field(default_factory=dict)   # category → count
    escalation_detected: bool = False
    escalation_description: str = ""
    multi_observer_corroboration: List[Dict] = field(default_factory=list)
    fraud_pattern_score: float = 0.0     # 0–1: probabilidad de fraude sistemático
    has_significant_patterns: bool = False
    summary: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_ts(ts_str: str) -> Optional[datetime]:
    """Parsea timestamp ISO8601 con fallback."""
    if not ts_str:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(ts_str[:26], fmt[:len(fmt)])
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def _extract_district(location: str) -> str:
    """Extrae el distrito/municipio de una cadena de ubicación."""
    if not location:
        return ""
    # Asume formato "Mesa X, Distrito Y, Provincia Z" o "Distrito Y"
    parts = [p.strip() for p in location.split(",")]
    return parts[0] if parts else location.strip()


def _severity_int(sev: str) -> int:
    return SEVERITY_ORDER.get(sev, 0)


# ── Validación de entrada individual ─────────────────────────────────────────

def validate_entry(entry: Dict, existing_entries: List[Dict]) -> ValidationResult:
    """
    Valida un hallazgo nuevo contra los ya registrados.
    No bloquea el ingreso — devuelve warnings para que el observador decida.
    """
    result = ValidationResult()
    category = entry.get("category", "other")
    severity  = entry.get("severity", "info")
    finding   = entry.get("finding", "")
    location  = entry.get("location", "")
    ts_str    = entry.get("timestamp", "")

    # ── 1. Campos recomendados por categoría ──────────────────────────────────
    required = REQUIRED_FIELDS_BY_CATEGORY.get(category, [])
    missing  = [f for f in required if not entry.get(f)]
    if missing:
        result.warnings.append(
            f"Campos recomendados faltantes para '{category}': {', '.join(missing)}. "
            "Esto reduce la capacidad de análisis legal."
        )
        result.quality_score -= 0.1 * len(missing)

    # ── 2. Validación de credibilidad para fraude ─────────────────────────────
    if category == "fraud_allegation":
        cred = entry.get("credibility", "unverified")
        if cred == "unverified" and severity in ("high", "critical"):
            result.warnings.append(
                "Alegación de alta severidad sin nivel de credibilidad asignado. "
                "Asigna 'credibility' para que el análisis ICCPR sea correcto."
            )
            result.quality_score -= 0.15

    # ── 3. Detección de duplicados ────────────────────────────────────────────
    dup_id = _detect_duplicate(entry, existing_entries)
    if dup_id:
        result.duplicate_of = dup_id
        result.warnings.append(
            f"Posible duplicado del hallazgo {dup_id} "
            f"(misma categoría/ubicación en ventana de {DUPLICATE_WINDOW_MINUTES} min). "
            "El hallazgo fue registrado; verifica si es un incidente separado."
        )
        result.quality_score -= 0.2

    # ── 4. Finding muy corto (poco informativo) ───────────────────────────────
    if len(finding.strip()) < 20:
        result.warnings.append(
            "Descripción del hallazgo muy corta (< 20 caracteres). "
            "Una descripción detallada mejora la trazabilidad legal."
        )
        result.quality_score -= 0.1

    # ── 5. Hallazgo crítico sin evidencia referenciada ────────────────────────
    if severity == "critical" and not entry.get("evidence_ref"):
        result.warnings.append(
            "Hallazgo CRÍTICO sin referencia de evidencia (foto/doc/URL). "
            "Para alegaciones ante JNE/Fiscalía se requiere documentación."
        )
        result.quality_score -= 0.1

    # ── 6. Hallazgo crítico sin verificación ──────────────────────────────────
    if severity == "critical" and not entry.get("verified"):
        result.warnings.append(
            "Hallazgo CRÍTICO no verificado. Considera marcar 'verified=true' "
            "si fue corroborado por un segundo observador."
        )

    result.quality_score = max(0.0, round(result.quality_score, 2))
    return result


def _detect_duplicate(entry: Dict, existing: List[Dict]) -> Optional[str]:
    """
    Retorna el entry_id del posible duplicado si lo hay, None si no.
    Criterio: misma categoría + mismo observador/ubicación + dentro de DUPLICATE_WINDOW_MINUTES.
    """
    ts_new = _parse_ts(entry.get("timestamp", ""))
    cat_new = entry.get("category", "")
    loc_new = (_extract_district(entry.get("location", ""))).lower()
    obs_new = (entry.get("observer_id", "")).lower()

    for e in existing:
        # Misma categoría
        if e.get("category") != cat_new:
            continue
        # Mismo observador O misma ubicación exacta
        same_obs = (e.get("observer_id", "")).lower() == obs_new and obs_new
        same_loc = (_extract_district(e.get("location", ""))).lower() == loc_new and loc_new
        if not (same_obs or same_loc):
            continue
        # Dentro de la ventana temporal
        ts_exist = _parse_ts(e.get("timestamp", ""))
        if ts_new and ts_exist:
            delta = abs((ts_new - ts_exist).total_seconds())
            if delta <= DUPLICATE_WINDOW_MINUTES * 60:
                return e.get("entry_id", "?")
    return None


# ── Detección de patrones en la sesión completa ───────────────────────────────

def detect_patterns(entries: List[Dict]) -> PatternReport:
    """
    Analiza todos los hallazgos de una sesión en busca de patrones sistemáticos.
    """
    report = PatternReport()
    if not entries:
        return report

    # ── Patrones geográficos ──────────────────────────────────────────────────
    district_map: Dict[str, List[Dict]] = {}
    for e in entries:
        if _severity_int(e.get("severity", "info")) >= _severity_int("medium"):
            d = _extract_district(e.get("location", ""))
            if d:
                district_map.setdefault(d, []).append(e)

    for district, dist_entries in district_map.items():
        if len(dist_entries) >= PATTERN_MIN_SAME_DISTRICT:
            max_sev   = max(dist_entries, key=lambda x: _severity_int(x.get("severity", "info")))["severity"]
            cats      = list({e.get("category", "other") for e in dist_entries})
            entry_ids = [e.get("entry_id", "?") for e in dist_entries]

            if max_sev == "critical" or len(dist_entries) >= 5:
                alert = "critical"
                iccpr = "ICCPR Art. 25(b) + CDI Art. 3 — patrón sistemático de supresión"
            elif max_sev == "high" or len(dist_entries) >= 4:
                alert = "concern"
                iccpr = "ICCPR Art. 25(b) — irregularidades reiteradas en circunscripción"
            else:
                alert = "watch"
                iccpr = "ICCPR Art. 25 — requiere monitoreo reforzado"

            report.geographic_patterns.append(GeographicPattern(
                district=district,
                entry_count=len(dist_entries),
                severity_max=max_sev,
                categories=cats,
                entry_ids=entry_ids,
                alert_level=alert,
                iccpr_ref=iccpr,
            ))

    report.geographic_patterns.sort(key=lambda x: (
        {"critical": 0, "concern": 1, "watch": 2}.get(x.alert_level, 3),
        -x.entry_count
    ))

    # ── Clusters por categoría ────────────────────────────────────────────────
    cat_counts: Dict[str, int] = {}
    for e in entries:
        cat = e.get("category", "other")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    report.category_clusters = {k: v for k, v in cat_counts.items() if v >= PATTERN_MIN_SAME_TYPE}

    # ── Detección de escalada de severidad ────────────────────────────────────
    sorted_entries = sorted(
        [e for e in entries if _parse_ts(e.get("timestamp", ""))],
        key=lambda x: _parse_ts(x["timestamp"])
    )
    if len(sorted_entries) >= 4:
        window = timedelta(hours=ESCALATION_WINDOW_HOURS)
        for i in range(len(sorted_entries) - 3):
            chunk = sorted_entries[i:i+4]
            ts_first = _parse_ts(chunk[0]["timestamp"])
            ts_last  = _parse_ts(chunk[-1]["timestamp"])
            if ts_first and ts_last and (ts_last - ts_first) <= window:
                sevs = [_severity_int(e.get("severity", "info")) for e in chunk]
                if sevs[-1] >= 3 and sevs[-1] > sevs[0] + 1:   # escaló 2+ niveles
                    report.escalation_detected = True
                    report.escalation_description = (
                        f"Escalada de {chunk[0].get('severity','?')} → {chunk[-1].get('severity','?')} "
                        f"en {int((ts_last - ts_first).total_seconds() / 60)} minutos "
                        f"(zona: {_extract_district(chunk[-1].get('location','?'))})."
                    )
                    break

    # ── Corroboración multi-observador ────────────────────────────────────────
    # Mismo incidente reportado por ≥2 observadores distintos
    loc_cat_map: Dict[str, List[Dict]] = {}
    for e in entries:
        key = f"{_extract_district(e.get('location',''))}|{e.get('category','')}"
        loc_cat_map.setdefault(key, []).append(e)

    for key, group in loc_cat_map.items():
        observers = {e.get("observer_id", "") for e in group}
        if len(observers) >= 2 and len(group) >= 2:
            loc, cat = key.split("|", 1)
            report.multi_observer_corroboration.append({
                "location": loc,
                "category": cat,
                "count":    len(group),
                "observers": list(observers),
            })

    # ── Score de fraude sistemático ───────────────────────────────────────────
    fraud_entries = [e for e in entries if e.get("category") == "fraud_allegation"]
    if fraud_entries:
        high_cred = [e for e in fraud_entries
                     if e.get("credibility") in ("confirmed", "high")]
        corroborated = len(report.multi_observer_corroboration)
        geo_critical = sum(1 for p in report.geographic_patterns if p.alert_level == "critical")

        score = (
            min(len(fraud_entries) / 10, 0.3)
            + min(len(high_cred) / 5, 0.3)
            + min(corroborated / 3, 0.2)
            + min(geo_critical / 2, 0.2)
        )
        report.fraud_pattern_score = round(min(score, 1.0), 2)

    # ── Resumen ───────────────────────────────────────────────────────────────
    report.has_significant_patterns = bool(
        report.geographic_patterns
        or report.category_clusters
        or report.escalation_detected
        or report.multi_observer_corroboration
    )

    parts = []
    if report.geographic_patterns:
        critical_geos = [p for p in report.geographic_patterns if p.alert_level == "critical"]
        if critical_geos:
            parts.append(f"{len(critical_geos)} zona(s) con patrón CRÍTICO")
        else:
            parts.append(f"{len(report.geographic_patterns)} zona(s) con patrón detectado")
    if report.escalation_detected:
        parts.append("escalada de severidad confirmada")
    if report.multi_observer_corroboration:
        parts.append(f"{len(report.multi_observer_corroboration)} incidente(s) corroborado(s) por múltiples observadores")
    if report.fraud_pattern_score >= 0.6:
        parts.append(f"score de fraude sistemático: {report.fraud_pattern_score:.0%}")

    report.summary = "; ".join(parts) if parts else "Sin patrones significativos detectados."
    return report


# ── Renderizado markdown para Cap. 7 ─────────────────────────────────────────

def render_pattern_markdown(report: PatternReport) -> str:
    """Genera la sección de patrones para el Capítulo 7 del informe."""
    if not report.has_significant_patterns:
        return ""

    lines = ["\n### 7.4 Patrones Sistemáticos Detectados — Agent 5\n"]

    # Alerta de fraude sistemático
    if report.fraud_pattern_score >= 0.5:
        bar = "🔴" if report.fraud_pattern_score >= 0.75 else "🟠" if report.fraud_pattern_score >= 0.5 else "🟡"
        lines.append(
            f"> {bar} **SCORE DE FRAUDE SISTEMÁTICO: {report.fraud_pattern_score:.0%}**  \n"
            f"> Basado en credibilidad, corroboración multi-observador y concentración geográfica.\n"
        )

    # Escalada de severidad
    if report.escalation_detected:
        lines.append(
            f"> ⚡ **ESCALADA DETECTADA:** {report.escalation_description}  \n"
            "> Posible respuesta a intervención externa — reforzar cobertura en la zona.\n"
        )

    # Patrones geográficos
    if report.geographic_patterns:
        lines.append("\n**Concentración geográfica de hallazgos:**\n")
        rows = ["| Zona | Hallazgos | Severidad | Categorías | Alerta | Marco Legal |",
                "|---|---|---|---|---|---|"]
        badge = {"critical": "🚨 CRÍTICO", "concern": "⚠️ PREOCUPANTE", "watch": "👁 MONITOREAR"}
        for p in report.geographic_patterns:
            rows.append(
                f"| {p.district} | {p.entry_count} | {p.severity_max.upper()} "
                f"| {', '.join(p.categories[:3])} "
                f"| {badge.get(p.alert_level, p.alert_level)} "
                f"| {p.iccpr_ref} |"
            )
        lines.append("\n".join(rows))

    # Clusters por categoría
    if report.category_clusters:
        cluster_text = " | ".join(
            f"**{cat}**: {cnt}" for cat, cnt in
            sorted(report.category_clusters.items(), key=lambda x: -x[1])
        )
        lines.append(f"\n**Concentración por tipo de hallazgo:** {cluster_text}\n")

    # Corroboración multi-observador
    if report.multi_observer_corroboration:
        lines.append("\n**Hallazgos corroborados por múltiples observadores:**\n")
        for c in report.multi_observer_corroboration[:5]:
            obs_list = ", ".join(c["observers"])
            lines.append(
                f"- **{c['location']}** / {c['category']}: "
                f"{c['count']} reportes por {obs_list}"
            )
        lines.append("")

    return "\n".join(lines)
