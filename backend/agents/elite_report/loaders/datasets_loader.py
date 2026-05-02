"""
DatasetsLoader — series históricas V-Dem, Freedom House, PEI, RSF.

Extrae datos multi-año (10+ años) para visualizaciones del Cap. 1
(Contexto histórico). Usa las funciones de carga existentes en
backend/modules/data_loaders.py.
"""
from __future__ import annotations

from typing import List, Optional

from agents.elite_report.models import HistoricalSeries, HistoricalDatapoint


DEFAULT_YEARS_WINDOW = 10


class DatasetsLoader:
    """Carga 4 series históricas del país para informe Elite."""

    def __init__(self, years_window: int = DEFAULT_YEARS_WINDOW):
        self.years_window = years_window

    def load(self, country_code: str, up_to_year: Optional[int] = None) -> List[HistoricalSeries]:
        """
        Retorna lista de HistoricalSeries: V-Dem Liberal Democracy, Freedom
        House total, PEI EMBs, RSF score.

        Cada serie cubre los últimos `years_window` años disponibles.
        """
        cc = country_code.upper()
        out: List[HistoricalSeries] = []

        # V-Dem
        vdem_series = self._load_vdem_series(cc, up_to_year)
        if vdem_series:
            out.append(vdem_series)

        # Freedom House
        fh_series = self._load_fh_series(cc, up_to_year)
        if fh_series:
            out.append(fh_series)

        # PEI
        pei_series = self._load_pei_series(cc)
        if pei_series:
            out.append(pei_series)

        # RSF
        rsf_series = self._load_rsf_series(cc)
        if rsf_series:
            out.append(rsf_series)

        return out

    # ── V-Dem ───────────────────────────────────────────────────────────
    def _load_vdem_series(self, cc: str, up_to_year: Optional[int] = None) -> Optional[HistoricalSeries]:
        """Carga la serie V-Dem Liberal Democracy Index.

        Estrategia 2-tier:
          1. CSV completo via load_vdem_data() — solo disponible en local
             (data/V-Dem-CY-Full+Others-v15.csv son 384MB, gitignored).
          2. Fallback: VDEM_STATIC dict pre-procesado en modules/vdem_static.py
             — 38 paises x 1985-2024 x 25 indicadores, tracked en git, ~682KB.
             Es lo que efectivamente corre en Railway.
        """
        from modules.data_loaders import VDEM_LAST_YEAR
        last_year = up_to_year or VDEM_LAST_YEAR
        first_year = last_year - self.years_window + 1

        # ── Tier 1: CSV ─────────────────────────────────────────────────
        try:
            from modules.data_loaders import load_vdem_data
            df = load_vdem_data()
            if df is not None:
                rows = df[
                    (df["country_text_id"] == cc) &
                    (df["year"] >= first_year) &
                    (df["year"] <= last_year)
                ].sort_values("year")

                if not rows.empty:
                    datapoints: List[HistoricalDatapoint] = []
                    import pandas as pd
                    for _, r in rows.iterrows():
                        val = r.get("v2x_libdem")
                        if pd.isna(val):
                            continue
                        try:
                            datapoints.append(HistoricalDatapoint(
                                year=int(r["year"]),
                                value=round(float(val), 4),
                                source="V-Dem Institute v15",
                            ))
                        except Exception:
                            continue

                    if datapoints:
                        trend = self._compute_trend([d.value for d in datapoints])
                        return HistoricalSeries(
                            indicator="vdem_libdem",
                            indicator_label="Liberal Democracy Index (V-Dem)",
                            source="V-Dem Institute, University of Gothenburg",
                            source_citation="V-Dem Institute. (2025). *Varieties of Democracy (V-Dem) Dataset v15*. University of Gothenburg.",
                            unit="0.0–1.0",
                            datapoints=datapoints,
                            trend_direction=trend[0],
                            trend_note=trend[1],
                        )
        except Exception:
            pass  # Cae a tier 2

        # ── Tier 2: VDEM_STATIC pre-procesado ───────────────────────────
        try:
            from modules.vdem_static import VDEM_STATIC
            country_data = VDEM_STATIC.get(cc, {})
            if not country_data:
                return None

            datapoints = []
            for y in range(first_year, last_year + 1):
                year_block = country_data.get(str(y))
                if not year_block:
                    continue
                val = year_block.get("v2x_libdem")
                if val is None:
                    continue
                try:
                    datapoints.append(HistoricalDatapoint(
                        year=y,
                        value=round(float(val), 4),
                        source="V-Dem Institute v15 (static)",
                    ))
                except Exception:
                    continue

            if not datapoints:
                return None

            trend = self._compute_trend([d.value for d in datapoints])
            return HistoricalSeries(
                indicator="vdem_libdem",
                indicator_label="Liberal Democracy Index (V-Dem)",
                source="V-Dem Institute, University of Gothenburg",
                source_citation="V-Dem Institute. (2025). *Varieties of Democracy (V-Dem) Dataset v15*. University of Gothenburg.",
                unit="0.0–1.0",
                datapoints=datapoints,
                trend_direction=trend[0],
                trend_note=trend[1],
            )
        except Exception:
            return None

    # ── Freedom House ───────────────────────────────────────────────────
    def _load_fh_series(self, cc: str, up_to_year: Optional[int] = None) -> Optional[HistoricalSeries]:
        try:
            from modules.data_loaders import load_freedom_house_data
            from modules.config import FH_COUNTRY_NAMES
            df = load_freedom_house_data()
            if df is None:
                return None

            # FH usa nombre en ingles en columna Country/Territory.
            # Mapeamos cc (ISO-3) -> nombre via FH_COUNTRY_NAMES; fallback a cc literal.
            country_name = FH_COUNTRY_NAMES.get(cc, cc)

            rows = None
            if "Country/Territory" in df.columns:
                rows = df[df["Country/Territory"] == country_name].sort_values("Edition")
            if rows is None or rows.empty:
                # Backstop: case-insensitive contains
                if "Country/Territory" in df.columns:
                    rows = df[df["Country/Territory"].astype(str).str.contains(
                        country_name, case=False, na=False)]
            if rows is None or rows.empty:
                return None

            datapoints: List[HistoricalDatapoint] = []
            import pandas as pd
            for _, r in rows.iterrows():
                year_val = r.get("Edition") or r.get("year") or r.get("Year")
                if year_val is None or pd.isna(year_val):
                    continue
                try:
                    year_int = int(year_val)
                except Exception:
                    continue

                total = r.get("Total")
                if total is None or pd.isna(total):
                    total = r.get("total_score") or r.get("Total Score")
                if total is None or pd.isna(total):
                    continue
                datapoints.append(HistoricalDatapoint(
                    year=year_int,
                    value=float(total),
                    source="Freedom House FIW",
                ))

            # Filtrar ventana
            datapoints.sort(key=lambda d: d.year)
            if up_to_year:
                first_year = up_to_year - self.years_window + 1
                datapoints = [d for d in datapoints if first_year <= d.year <= up_to_year]
            else:
                datapoints = datapoints[-self.years_window:]

            if not datapoints:
                return None

            trend = self._compute_trend([d.value for d in datapoints])
            return HistoricalSeries(
                indicator="fh_total",
                indicator_label="Freedom House Total Score (FIW)",
                source="Freedom House",
                source_citation="Freedom House. (2025). *Freedom in the World 2025*. Freedom House.",
                unit="0–100",
                datapoints=datapoints,
                trend_direction=trend[0],
                trend_note=trend[1],
            )
        except Exception:
            return None

    # ── PEI ─────────────────────────────────────────────────────────────
    def _load_pei_series(self, cc: str) -> Optional[HistoricalSeries]:
        """PEI da usualmente 1 punto por elección. Puede haber 2-3 elecciones en window."""
        try:
            from modules.data_loaders import load_pei_data, get_pei_country
            df = load_pei_data()
            if df is None:
                return None
            summary = get_pei_country(df, cc)
            if not summary:
                return None

            # PEI devuelve ultimo valor. Intentamos extraer todas las elecciones del país.
            rows = df[df.get("VenezuelaCountry", df.get("country", "")) == cc] if "VenezuelaCountry" in df.columns else df[df.get("country", "") == cc]
            if rows.empty and "Country" in df.columns:
                rows = df[df["Country"] == cc]
            if rows.empty:
                # Usar solo el summary como 1 datapoint
                datapoints = []
                if summary.get("year"):
                    datapoints.append(HistoricalDatapoint(
                        year=int(summary["year"]),
                        value=float(summary.get("overall_integrity", 0)),
                        source="PEI v10.0",
                        note=summary.get("election_id"),
                    ))
                if not datapoints:
                    return None
                return HistoricalSeries(
                    indicator="pei_overall",
                    indicator_label="Perceptions of Electoral Integrity (PEI Overall)",
                    source="Electoral Integrity Project",
                    source_citation="Electoral Integrity Project. (2024). *Perceptions of Electoral Integrity (PEI 10.0) Dataset*. Universities of Sydney and Harvard.",
                    unit="0–100",
                    datapoints=datapoints,
                    trend_direction="stable",
                    trend_note="Punto único disponible en el dataset.",
                )

            datapoints: List[HistoricalDatapoint] = []
            import pandas as pd
            for _, r in rows.iterrows():
                year_col = r.get("year") or r.get("Year")
                val = r.get("PEIIndexi") or r.get("overall_integrity")
                if year_col is None or val is None or pd.isna(year_col) or pd.isna(val):
                    continue
                datapoints.append(HistoricalDatapoint(
                    year=int(year_col),
                    value=float(val),
                    source="PEI v10.0",
                    note=str(r.get("PEIID") or r.get("election_id") or ""),
                ))

            datapoints.sort(key=lambda d: d.year)
            if not datapoints:
                return None

            trend = self._compute_trend([d.value for d in datapoints])
            return HistoricalSeries(
                indicator="pei_overall",
                indicator_label="Perceptions of Electoral Integrity (PEI Overall)",
                source="Electoral Integrity Project",
                source_citation="Electoral Integrity Project. (2024). *Perceptions of Electoral Integrity (PEI 10.0) Dataset*. Universities of Sydney and Harvard.",
                unit="0–100",
                datapoints=datapoints,
                trend_direction=trend[0],
                trend_note=trend[1],
            )
        except Exception:
            return None

    # ── RSF ─────────────────────────────────────────────────────────────
    def _load_rsf_series(self, cc: str) -> Optional[HistoricalSeries]:
        """RSF típicamente 1 snapshot por año (no series larga). El dataset 2025
        trae Score 2025 y Score N-1 — extraemos ambos para tener al menos 2 puntos."""
        try:
            from modules.data_loaders import load_rsf_data
            df = load_rsf_data()
            if df is None:
                return None

            country_col = None
            for col in ("ISO", "iso_code", "country_code", "Country code"):
                if col in df.columns:
                    country_col = col
                    break
            if not country_col:
                return None
            rows = df[df[country_col] == cc]
            if rows.empty:
                return None

            datapoints: List[HistoricalDatapoint] = []
            import pandas as pd
            for _, r in rows.iterrows():
                # RSF 2025 dataset: columna 'Score 2025' (snapshot) + 'Score N-1' (anterior).
                # Usamos ambos para tener serie minima de 2 puntos (2024 y 2025).
                score_curr = r.get("Score 2025") or r.get("Global Score 2025")
                score_prev = r.get("Score N-1")
                year_curr = 2025
                # Si hay columna 'Year (N)' tomar de ahi, sino hardcoded
                yn = r.get("Year (N)")
                if yn is not None and not pd.isna(yn):
                    try: year_curr = int(yn)
                    except Exception: pass
                if score_prev is not None and not pd.isna(score_prev):
                    datapoints.append(HistoricalDatapoint(
                        year=year_curr - 1, value=float(score_prev),
                        source="Reporters Without Borders",
                    ))
                if score_curr is not None and not pd.isna(score_curr):
                    datapoints.append(HistoricalDatapoint(
                        year=year_curr, value=float(score_curr),
                        source="Reporters Without Borders",
                    ))

            datapoints.sort(key=lambda d: d.year)
            datapoints = datapoints[-self.years_window:]
            if not datapoints:
                return None

            trend = self._compute_trend([d.value for d in datapoints])
            return HistoricalSeries(
                indicator="rsf_score",
                indicator_label="Press Freedom Index (RSF)",
                source="Reporters Without Borders (RSF)",
                source_citation="Reporters Without Borders. (2025). *Press Freedom Index 2025*. RSF.",
                unit="0–100",
                datapoints=datapoints,
                trend_direction=trend[0],
                trend_note=trend[1],
            )
        except Exception:
            return None

    # ── Análisis de tendencia ───────────────────────────────────────────
    @staticmethod
    def _compute_trend(values: List[float]) -> tuple[str, str]:
        """Determina dirección y nota interpretativa."""
        if len(values) < 2:
            return "stable", "Serie insuficiente para inferir tendencia."
        first, last = values[0], values[-1]
        delta = last - first
        rel = abs(delta) / (abs(first) if abs(first) > 0.01 else 1.0)

        # Volatilidad
        changes = [abs(values[i+1] - values[i]) for i in range(len(values)-1)]
        avg_change = sum(changes) / len(changes) if changes else 0
        volatility = avg_change / (abs(first) if abs(first) > 0.01 else 1.0)

        if volatility > 0.25:
            return "volatile", (
                f"Alta volatilidad en la serie (variación media interanual "
                f"{volatility*100:.0f}% del valor base)."
            )
        if rel < 0.05:
            return "stable", (
                f"Serie estable: variación neta {delta:+.3f} sobre {len(values)} "
                f"observaciones."
            )
        if delta > 0:
            return "up", (
                f"Mejora sostenida: +{delta:.3f} sobre {len(values)} años "
                f"({rel*100:.0f}% relativo)."
            )
        return "down", (
            f"Deterioro sostenido: {delta:.3f} sobre {len(values)} años "
            f"({rel*100:.0f}% relativo)."
        )
