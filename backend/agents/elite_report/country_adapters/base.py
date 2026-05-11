"""Base CountryAdapter — interfaz que cada pais debe implementar.

Cada metodo retorna estructura lista para consumo por los renderers.
Las strings localizadas se reciben con `language` cuando es relevante
(actor labels, recommendations, etc.). Datos invariantes al idioma
(ids, status, dates) se devuelven sin parametro language.

Sprint 3 (11-may-2026): se agrega `institutional_model()` para describir
la arquitectura institucional electoral abstracta. Esto permite a
adapters de paises con sistemas distintos al unitario peruano
(federal centralizado tipo Brasil con TSE+TREs, federal descentralizado
tipo USA sin EMB nacional) declarar su topologia institucional de manera
estructurada, que puede consumirse desde el narrative del Cap 3 y desde
visualizaciones derivadas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Literal, Optional, Protocol, Tuple


# ── Modelo institucional generalizado (Sprint 3) ──────────────────────────

@dataclass(frozen=True)
class EMBBody:
    """Cuerpo institucional con rol en el proceso electoral.

    `role` distingue el rol funcional:
      - arbiter:    autoridad maxima de calificacion (PER: JNE; BRA: TSE)
      - operations: ejecuta el proceso operativo (PER: ONPE; BRA: TSE+TREs)
      - registry:   administra el padron electoral (PER: RENIEC)
      - judicial:   resuelve disputas en sede judicial (PER: PJ)
      - oversight:  fiscalizacion externa (Fiscalia, MP, contraloria)

    `scope` distingue national vs subnational (estados, provincias).
    """
    name: str
    role: Literal["arbiter", "operations", "registry", "judicial", "oversight"]
    scope: Literal["national", "subnational"]
    description: Optional[str] = None


@dataclass(frozen=True)
class LegalLayer:
    """Capa del marco legal electoral aplicable.

    `layer` ordenado por jerarquia normativa:
      - constitutional: Constitucion del pais (jerarquia maxima)
      - federal:        Leyes nacionales (Codigo Electoral, etc.)
      - subnational:    Leyes estatales/provinciales (vacio para sistemas unitarios)
      - international:  Tratados internacionales aplicables
    """
    layer: Literal["constitutional", "federal", "subnational", "international"]
    instruments: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class InstitutionalModel:
    """Modelo institucional electoral abstracto.

    Soporta los 3 tipos de arquitectura observados en el mundo:

      - unitary: un solo nivel de autoridad electoral nacional.
        Ejemplos: PER (JNE+ONPE+RENIEC), Argentina (CNE).

      - federal_centralized: autoridad nacional + bodies subnacionales
        subordinados o coordinados. Ejemplo: BRA (TSE federal + 27 TREs).

      - federal_decentralized: sin autoridad nacional electoral. Cada
        subdivision con autoridad propia. Ejemplo: USA (50 estados + DC,
        Election Assistance Commission federal es advisory, no ejecutiva).

    `transmission_chain_type`:
      - centralized:     un solo sistema de tabulacion nacional
      - per_subnational: cada subdivision tabula y reporta al centro
      - hybrid:          mezcla (e.g. urna electronica federal + canvassing
                         estatal en USA)

    `notes` es texto libre para detalles del pais que no encajan en el
    schema (e.g. presencia de IA en el conteo, particularidades historicas).
    """
    system_type: Literal["unitary", "federal_centralized", "federal_decentralized"]
    national_emb: Optional[EMBBody]
    subnational_embs: List[EMBBody] = field(default_factory=list)
    legal_layers: List[LegalLayer] = field(default_factory=list)
    transmission_chain_type: Literal["centralized", "per_subnational", "hybrid"] = "centralized"
    notes: Optional[str] = None


class CountryAdapter(Protocol):
    """Interfaz canonica de datos pais-especificos para el Elite Report."""

    country_code: str
    country_name: str

    # ── Marco legal y normativo ─────────────────────────────────────────

    def legal_framework_rows(self) -> List[Dict[str, str]]:
        """Filas de la matriz normativa (Cap 2). Cada row:
            {"instrument": str, "topic": str, "hierarchy": str}
        hierarchy ∈ {"constitucional", "legal", "jurisprudencial",
                     "internacional"}."""
        ...

    # ── Estructura institucional electoral ─────────────────────────────

    def actor_network(self, language: str) -> Dict[str, Any]:
        """Red de actores institucionales + extra-electorales (Cap 7).
        Retorna {"actors": [...], "edges": [...]} con labels traducidos."""
        ...

    def network_institutions(self, language: str) -> Dict[str, Any]:
        """Red institucional electoral nuclear (Cap 3). Sólo organismos
        oficiales (EMB+afines). Retorna {"nodes": [...], "edges": [...]}."""
        ...

    def flow_voting_stages(self, language: str) -> Dict[str, Any]:
        """Cadena del voto desde padrón a proclamación (Cap 3).
        Retorna {"stages": [...]}."""
        ...

    def architecture(self, language: str) -> Dict[str, Any]:
        """Arquitectura tecnológica del sistema electoral (Cap 12).
        Retorna {"components": [...], "flows": [...]}."""
        ...

    # ── Producto del informe ───────────────────────────────────────────

    def recommendations(self, language: str) -> Dict[str, Any]:
        """Tabla de recomendaciones (Cap 11). Retorna {"rows": [...]}."""
        ...

    def early_warning_label(self, level: str, language: str) -> str:
        """Label del nivel de alerta temprana (Cap 9).
        level ∈ {green|amber|orange|red}. Retorna label localizado."""
        ...

    # ── Inteligencia institucional ─────────────────────────────────────

    def organ_keywords(self) -> Dict[str, List[str]]:
        """Para semaforo institucional (Cap 10). Mapea label de organo
        a keywords (case-insensitive substring) que el matcher busca en
        finding o source_name de cada hunter entry."""
        ...

    # ── Calendario electoral ───────────────────────────────────────────

    def electoral_calendar(self) -> Dict[str, Tuple[date, date]]:
        """Mapeo phase_id -> (start_date, end_date) para PhaseOrganizer.
        Vacio = sin calendario activo, los findings caen en preparatory."""
        ...

    # ── Datos parlamentarios opcionales ────────────────────────────────

    def parliament_scenarios(self) -> Optional[Dict[str, Any]]:
        """Escenarios parlamentarios proyectados (Cap 9). None si el
        pais no tiene proyecciones disponibles."""
        ...

    # ── Datos regionales opcionales ────────────────────────────────────

    def regions_data(self) -> Optional[List[Dict[str, Any]]]:
        """Lista de regiones del pais para regions_affected viz (Cap 5).
        None si no se quiere mostrar el mapa regional."""
        ...

    # ── Modelo institucional (Sprint 3) ────────────────────────────────

    def institutional_model(self) -> InstitutionalModel:
        """Modelo institucional electoral abstracto. Permite al narrative
        del Cap 3 + visualizaciones derivadas conocer la topologia
        del sistema sin asumir el caso unitario peruano por default."""
        ...
