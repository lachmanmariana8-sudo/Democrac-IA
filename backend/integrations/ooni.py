"""
DEMOCRAC.IA / PEIRS — OONI API Integration
Detecta bloqueos de URLs e interferencia de red en tiempo real.

API pública OONI Explorer v1 — sin autenticación requerida.
Documentación: https://api.ooni.io/apidocs/

Funciones principales:
  get_ooni_summary(country_code)          → resumen estructurado para el informe
  fetch_web_anomalies(country_code, ...)  → lista de dominios con anomalías
  fetch_network_interference(...)        → interferencia de red por ASN
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

# Importación condicional — el sistema funciona sin httpx
try:
    import httpx
    _HTTPX_OK = True
except ImportError:
    _HTTPX_OK = False

OONI_AVAILABLE: bool = False

# ── Configuración ─────────────────────────────────────────────────────────────

OONI_BASE_URL   = "https://api.ooni.io/api/v1"
OONI_TIMEOUT    = 10.0   # segundos
OONI_MAX_RETRY  = 2

# Cache simple en memoria: evita golpear la API en cada regeneración de informe
_cache: Dict[str, dict] = {}
_CACHE_TTL_MINUTES = 30


def _cache_key(country_code: str, endpoint: str) -> str:
    return f"{country_code}:{endpoint}"


def _is_cache_valid(entry: dict) -> bool:
    if "timestamp" not in entry:
        return False
    age = (datetime.now(timezone.utc) - entry["timestamp"]).total_seconds()
    return age < _CACHE_TTL_MINUTES * 60


# ── Cliente HTTP ──────────────────────────────────────────────────────────────

def _get(url: str, params: dict) -> Optional[dict]:
    """GET síncrono con retry. Retorna None en caso de error."""
    if not _HTTPX_OK:
        return None
    for attempt in range(OONI_MAX_RETRY):
        try:
            with httpx.Client(timeout=OONI_TIMEOUT) as client:
                r = client.get(url, params=params)
                r.raise_for_status()
                return r.json()
        except Exception as exc:
            if attempt == OONI_MAX_RETRY - 1:
                print(f"[OONI] Error en {url}: {exc}")
    return None


# ── Funciones de consulta ─────────────────────────────────────────────────────

def fetch_web_anomalies(
    country_code: str,
    days_back: int = 7,
    limit: int = 50,
) -> List[Dict]:
    """
    Retorna mediciones web_connectivity con anomalías (posibles bloqueos).

    Cada resultado incluye:
      domain, measurement_url, anomaly, confirmed, failure_reason, measurement_start_time
    """
    ck = _cache_key(country_code, f"web_anomalies_{days_back}")
    if ck in _cache and _is_cache_valid(_cache[ck]):
        return _cache[ck]["data"]

    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00")
    until = datetime.now(timezone.utc).strftime("%Y-%m-%dT23:59:59")

    data = _get(
        f"{OONI_BASE_URL}/measurements",
        params={
            "probe_cc":   country_code.upper(),
            "test_name":  "web_connectivity",
            "anomaly":    "true",
            "since":      since,
            "until":      until,
            "limit":      limit,
            "order_by":   "test_start_time",
        },
    )

    if data is None:
        return []

    results = []
    for m in data.get("results", []):
        domain = m.get("input", "")
        # Extraer dominio limpio de la URL
        if domain.startswith("http"):
            try:
                from urllib.parse import urlparse
                domain = urlparse(domain).netloc or domain
            except Exception:
                pass
        results.append({
            "domain":      domain,
            "url":         m.get("input", ""),
            "anomaly":     m.get("anomaly", False),
            "confirmed":   m.get("confirmed", False),
            "failure":     m.get("failure", None),
            "timestamp":   m.get("measurement_start_time", ""),
            "probe_asn":   m.get("probe_asn", ""),
            "report_url":  m.get("report_url", ""),
        })

    _cache[ck] = {"data": results, "timestamp": datetime.now(timezone.utc)}
    return results


def fetch_aggregated_blocking(
    country_code: str,
    days_back: int = 7,
) -> List[Dict]:
    """
    Usa el endpoint /aggregation para obtener estadísticas por dominio.
    Más eficiente para resúmenes — retorna dominios con mayor tasa de anomalía.
    """
    ck = _cache_key(country_code, f"aggregated_{days_back}")
    if ck in _cache and _is_cache_valid(_cache[ck]):
        return _cache[ck]["data"]

    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00")
    until = datetime.now(timezone.utc).strftime("%Y-%m-%dT23:59:59")

    data = _get(
        f"{OONI_BASE_URL}/aggregation",
        params={
            "probe_cc":   country_code.upper(),
            "test_name":  "web_connectivity",
            "since":      since,
            "until":      until,
            "axis_x":     "domain",
            "limit":      100,
        },
    )

    if data is None:
        return []

    results = []
    for row in data.get("result", []):
        anomaly_count   = row.get("anomaly_count", 0)
        ok_count        = row.get("ok_count", 0)
        total           = anomaly_count + ok_count
        anomaly_rate    = round(anomaly_count / total, 3) if total > 0 else 0

        if anomaly_rate >= 0.3:   # Solo dominios con ≥30% de tasa de anomalía
            results.append({
                "domain":         row.get("domain", ""),
                "anomaly_count":  anomaly_count,
                "ok_count":       ok_count,
                "total":          total,
                "anomaly_rate":   anomaly_rate,
                "confirmed_count": row.get("confirmed_count", 0),
            })

    results.sort(key=lambda x: -x["anomaly_rate"])
    _cache[ck] = {"data": results, "timestamp": datetime.now(timezone.utc)}
    return results


def fetch_network_interference(
    country_code: str,
    days_back: int = 3,
) -> List[Dict]:
    """
    Detecta interferencia de red por ASN (proveedor de internet).
    Útil para detectar apagones de ISP el día de la elección.
    """
    ck = _cache_key(country_code, f"network_{days_back}")
    if ck in _cache and _is_cache_valid(_cache[ck]):
        return _cache[ck]["data"]

    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00")
    until = datetime.now(timezone.utc).strftime("%Y-%m-%dT23:59:59")

    data = _get(
        f"{OONI_BASE_URL}/aggregation",
        params={
            "probe_cc":   country_code.upper(),
            "test_name":  "web_connectivity",
            "since":      since,
            "until":      until,
            "axis_x":     "probe_asn",
            "limit":      50,
        },
    )

    if data is None:
        return []

    results = []
    for row in data.get("result", []):
        anomaly_count = row.get("anomaly_count", 0)
        ok_count      = row.get("ok_count", 0)
        total         = anomaly_count + ok_count
        anomaly_rate  = round(anomaly_count / total, 3) if total > 0 else 0

        if anomaly_rate >= 0.4 and total >= 5:   # ASN con patrón significativo
            results.append({
                "asn":           row.get("probe_asn", ""),
                "anomaly_count": anomaly_count,
                "total":         total,
                "anomaly_rate":  anomaly_rate,
            })

    results.sort(key=lambda x: -x["anomaly_rate"])
    _cache[ck] = {"data": results, "timestamp": datetime.now(timezone.utc)}
    return results


# ── Función principal ─────────────────────────────────────────────────────────

def get_ooni_summary(country_code: str, days_back: int = 7) -> Dict:
    """
    Resumen estructurado OONI para incluir en el informe y en el protocolo
    de observación. Siempre retorna un dict válido (nunca lanza excepción).

    Returns:
      {
        "available": bool,
        "country_code": str,
        "period_days": int,
        "blocked_domains": [...],
        "high_anomaly_asns": [...],
        "censorship_detected": bool,
        "network_interference_detected": bool,
        "summary_text": str,         # para tabla del informe
        "alert_level": str,          # "none"|"low"|"medium"|"high"|"critical"
        "timestamp": str,
        "source": str,
      }
    """
    if not _HTTPX_OK:
        return _unavailable_summary(country_code, "httpx no instalado")

    try:
        aggregated  = fetch_aggregated_blocking(country_code, days_back=days_back)
        network     = fetch_network_interference(country_code, days_back=min(days_back, 3))

        blocked     = [r for r in aggregated if r["confirmed_count"] > 0 or r["anomaly_rate"] >= 0.6]
        anomalous   = [r for r in aggregated if r["anomaly_rate"] >= 0.3]

        censorship_detected   = len(blocked) > 0
        interference_detected = any(r["anomaly_rate"] >= 0.5 for r in network)

        # Nivel de alerta
        if len(blocked) >= 5 or any(r["anomaly_rate"] >= 0.8 for r in network):
            alert_level = "critical"
        elif len(blocked) >= 2 or interference_detected:
            alert_level = "high"
        elif len(anomalous) >= 3:
            alert_level = "medium"
        elif len(anomalous) >= 1:
            alert_level = "low"
        else:
            alert_level = "none"

        # Texto resumen para la tabla del informe
        if censorship_detected:
            top_domains = ", ".join(r["domain"] for r in blocked[:3])
            summary_text = f"Detectada — {len(blocked)} dominio(s) confirmado(s): {top_domains}"
        elif anomalous:
            summary_text = f"Anomalías ({len(anomalous)} dominio(s)) — sin bloqueo confirmado"
        else:
            summary_text = f"No detectada — {days_back} días monitoreados"

        return {
            "available":                   True,
            "country_code":                country_code.upper(),
            "period_days":                 days_back,
            "blocked_domains":             blocked[:10],
            "anomalous_domains":           anomalous[:20],
            "high_anomaly_asns":           network[:5],
            "censorship_detected":         censorship_detected,
            "network_interference_detected": interference_detected,
            "summary_text":                summary_text,
            "alert_level":                 alert_level,
            "timestamp":                   datetime.now(timezone.utc).isoformat(),
            "source":                      f"OONI Explorer API — últimos {days_back} días",
        }

    except Exception as exc:
        return _unavailable_summary(country_code, str(exc))


def _unavailable_summary(country_code: str, reason: str) -> Dict:
    return {
        "available":                   False,
        "country_code":                country_code.upper(),
        "period_days":                 0,
        "blocked_domains":             [],
        "anomalous_domains":           [],
        "high_anomaly_asns":           [],
        "censorship_detected":         False,
        "network_interference_detected": False,
        "summary_text":                f"Sin datos OONI ({reason})",
        "alert_level":                 "none",
        "timestamp":                   datetime.now(timezone.utc).isoformat(),
        "source":                      "OONI API no disponible",
    }


def clear_cache(country_code: Optional[str] = None) -> None:
    """Limpia el cache. Si country_code es None, limpia todo."""
    global _cache
    if country_code:
        _cache = {k: v for k, v in _cache.items() if not k.startswith(country_code + ":")}
    else:
        _cache = {}
