"""Tiers de acceso para Democrac.IA / PEIRS.

Define los 5 niveles de acceso y sus capabilities. La autenticacion via
Observer Key actual queda como single-tier "observer"; este modulo define
el modelo extendido que sucesivos sprints van a implementar.

Sprint plan (referenciado por proyecto memory):

  Sprint A — modelo de tiers + tier_id en Observer Key (lo presente)
  Sprint B — email signup + verificacion para Tier 2 (researcher_press)
  Sprint C — Stripe/Paddle billing para Tier 3 (institutional)
  Sprint D — features de Tier 4 (mission) — multi-pais, custom webhooks
  Sprint E — Tier 5 enterprise (deal-driven, instancia separada)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Tier(str, Enum):
    """Niveles de acceso de la plataforma. Ordenados por privilegio."""
    PUBLIC = "public"                  # gratis, sin signup
    RESEARCHER = "researcher_press"    # gratis con verificacion academica/prensa
    INSTITUTIONAL = "institutional"    # USD 200-500/mes — ONGs, universidades
    MISSION = "mission"                # USD 1.5k-5k/mes — misiones de observacion
    ENTERPRISE = "enterprise"          # custom — gobiernos, organismos supranacionales


@dataclass(frozen=True)
class TierCapabilities:
    """Capabilities de un tier. Los flags determinan que features puede
    consumir el usuario y los limites cuantitativos aplicables."""
    tier: Tier
    display_name: str
    monthly_price_usd: Optional[float]  # None = gratis o custom
    description: str

    # Acceso a features
    can_view_landing: bool = True
    can_view_dashboard: bool = False
    can_view_country_detail: bool = False
    can_search_findings: bool = False
    can_download_archived_reports: bool = True   # >90 dias
    can_download_recent_reports: bool = False    # <90 dias
    can_generate_elite_report: bool = False
    can_use_webhook: bool = False
    can_use_api: bool = False
    can_multi_country: bool = False
    can_custom_hunter_sources: bool = False
    can_white_label: bool = False
    has_sla: bool = False
    has_dedicated_support: bool = False

    # Limites cuantitativos
    max_elite_reports_per_day: int = 0
    max_api_requests_per_day: int = 0
    max_webhook_endpoints: int = 0
    sla_uptime_pct: Optional[float] = None  # ej. 99.0 (Tier 4), 99.9 (Tier 5)


# Definicion canonica de los 5 tiers
TIERS: Dict[Tier, TierCapabilities] = {
    Tier.PUBLIC: TierCapabilities(
        tier=Tier.PUBLIC,
        display_name="Público",
        monthly_price_usd=0.0,
        description=(
            "Acceso libre a la landing, estadísticas agregadas en vivo, "
            "mapa de cobertura y metodología pública. Informes Elite "
            "archivados (>90 días) disponibles en formato PDF/HTML."
        ),
        can_view_landing=True,
        can_view_dashboard=False,
        can_view_country_detail=False,
        can_download_archived_reports=True,
    ),

    Tier.RESEARCHER: TierCapabilities(
        tier=Tier.RESEARCHER,
        display_name="Investigador / Prensa",
        monthly_price_usd=0.0,  # gratis con verificacion
        description=(
            "Para investigadores académicos y periodistas. Acceso al "
            "dashboard técnico completo con detalle por país, feed de "
            "alertas en tiempo real, búsqueda y filtros sobre hallazgos "
            "del Hunter, descarga de Elite Reports recientes."
        ),
        can_view_landing=True,
        can_view_dashboard=True,
        can_view_country_detail=True,
        can_search_findings=True,
        can_download_archived_reports=True,
        can_download_recent_reports=True,
        max_api_requests_per_day=100,  # read-only acotado
    ),

    Tier.INSTITUTIONAL: TierCapabilities(
        tier=Tier.INSTITUTIONAL,
        display_name="Institucional",
        monthly_price_usd=300.0,  # rango 200-500, valor medio
        description=(
            "Para ONGs, universidades, institutos de investigación. "
            "Webhook integration (Slack/Discord/email), API read-only con "
            "cuota institucional, alertas customizables por severidad/categoría/país, "
            "comparative reports cross-country."
        ),
        can_view_landing=True,
        can_view_dashboard=True,
        can_view_country_detail=True,
        can_search_findings=True,
        can_download_archived_reports=True,
        can_download_recent_reports=True,
        can_use_webhook=True,
        can_use_api=True,
        max_api_requests_per_day=1000,
        max_webhook_endpoints=3,
    ),

    Tier.MISSION: TierCapabilities(
        tier=Tier.MISSION,
        display_name="Misión de Observación",
        monthly_price_usd=2500.0,  # rango 1.5k-5k, valor medio
        description=(
            "Para misiones de observación electoral profesionales (OEA/DECO, "
            "EU EOM, Carter Center, OSCE/ODIHR, IDEA Internacional). "
            "Generación de Elite Reports on-demand sin budget cap, custom "
            "Hunter sources por país de interés, multi-country coverage, "
            "Observer Protocol full access, white-label del informe con "
            "branding de la misión, priority API tier, SLA 99% uptime."
        ),
        can_view_landing=True,
        can_view_dashboard=True,
        can_view_country_detail=True,
        can_search_findings=True,
        can_download_archived_reports=True,
        can_download_recent_reports=True,
        can_generate_elite_report=True,
        can_use_webhook=True,
        can_use_api=True,
        can_multi_country=True,
        can_custom_hunter_sources=True,
        can_white_label=True,
        has_sla=True,
        max_elite_reports_per_day=20,
        max_api_requests_per_day=10000,
        max_webhook_endpoints=10,
        sla_uptime_pct=99.0,
    ),

    Tier.ENTERPRISE: TierCapabilities(
        tier=Tier.ENTERPRISE,
        display_name="Enterprise / Partner",
        monthly_price_usd=None,  # custom
        description=(
            "Para gobiernos, organismos supranacionales, tribunales "
            "electorales. Onboarding completo de país nuevo, dedicated "
            "infrastructure (instancia separada si requieren confidencialidad), "
            "SLA 99.9%, soporte directo con equipo técnico, integration con "
            "sistemas internos (Salesforce, Slack, MS Teams), co-branding y "
            "citas formales."
        ),
        can_view_landing=True,
        can_view_dashboard=True,
        can_view_country_detail=True,
        can_search_findings=True,
        can_download_archived_reports=True,
        can_download_recent_reports=True,
        can_generate_elite_report=True,
        can_use_webhook=True,
        can_use_api=True,
        can_multi_country=True,
        can_custom_hunter_sources=True,
        can_white_label=True,
        has_sla=True,
        has_dedicated_support=True,
        max_elite_reports_per_day=100,  # de hecho sin limit duro
        max_api_requests_per_day=100000,
        max_webhook_endpoints=100,
        sla_uptime_pct=99.9,
    ),
}


def get_capabilities(tier: Tier) -> TierCapabilities:
    """Devuelve capabilities del tier. Default: PUBLIC."""
    return TIERS.get(tier, TIERS[Tier.PUBLIC])


def list_public_tiers() -> List[Dict[str, Any]]:
    """Lista publica de tiers para mostrar en pricing page.
    Excluye campos internos sensibles."""
    return [
        {
            "tier": t.tier.value,
            "display_name": t.display_name,
            "monthly_price_usd": t.monthly_price_usd,
            "description": t.description,
            "features": {
                "dashboard": t.can_view_dashboard,
                "country_detail": t.can_view_country_detail,
                "search_findings": t.can_search_findings,
                "download_recent_reports": t.can_download_recent_reports,
                "generate_elite_report": t.can_generate_elite_report,
                "webhook": t.can_use_webhook,
                "api": t.can_use_api,
                "multi_country": t.can_multi_country,
                "custom_hunter_sources": t.can_custom_hunter_sources,
                "white_label": t.can_white_label,
                "sla": t.has_sla,
                "dedicated_support": t.has_dedicated_support,
            },
            "limits": {
                "elite_reports_per_day": t.max_elite_reports_per_day,
                "api_requests_per_day": t.max_api_requests_per_day,
                "webhook_endpoints": t.max_webhook_endpoints,
                "sla_uptime_pct": t.sla_uptime_pct,
            },
        }
        for t in TIERS.values()
    ]
