"""Base CountryAdapter — interfaz que cada pais debe implementar.

Cada metodo retorna estructura lista para consumo por los renderers.
Las strings localizadas se reciben con `language` cuando es relevante
(actor labels, recommendations, etc.). Datos invariantes al idioma
(ids, status, dates) se devuelven sin parametro language.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Protocol, Tuple


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
