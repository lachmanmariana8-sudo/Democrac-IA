"""
peirs_data.py — API unificada para los datasets base de PEIRS.

Uso típico:
    from scripts.peirs_data import PeirsData
    data = PeirsData(cache_dir=r"D:\\DemocracIA\\data")
    data.ensure_all()
    snapshot = data.country_snapshot(country_code=32)  # Argentina
    score = data.peirs_score(country_code=604)         # Perú
"""

from __future__ import annotations

import hashlib
import json
import logging
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger("peirs_data")

# URLs oficiales. Verificar periódicamente con verify_cache.py.
DATASET_SOURCES = {
    "vdem": {
        "url": "https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/data/vdem.rda",
        "filename": "vdem_v16.csv",
        "folder": "vdem",
        "version": "v16",
        "raw_filename": "vdem.rda",
        "needs_conversion": True,
    },
    "fh": {
        "url": "https://freedomhouse.org/sites/default/files/2025-02/All_data_FIW_2013-2024.xlsx",
        "filename": "All_data_FIW_2013-2024.xlsx",
        "folder": "freedomhouse",
        "version": "2025",
    },
    "pei": {
        "url": "https://www.electoralintegrityproject.com/pei-data",
        "filename": "PEI_country-level_10.0.csv",
        "folder": "pei",
        "version": "10.0",
    },
    "rsf": {
        "url": "https://rsf.org/sites/default/files/import_classement/2025.csv",
        "filename": "rsf_index_2025.csv",
        "folder": "rsf",
        "version": "2025",
    },
}

DEFAULT_WEIGHTS = {
    "vdem": 0.35,
    "pei": 0.30,
    "fh": 0.20,
    "rsf": 0.15,
}


@dataclass
class CacheEntry:
    path: Path
    meta_path: Path
    version: str
    source_url: str


class PeirsData:
    """API unificada para los datasets base de PEIRS."""

    def __init__(self, cache_dir: str | Path, iso_mapping_path: str | Path | None = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._frames: dict[str, pd.DataFrame] = {}
        self._iso_map: pd.DataFrame | None = None

        if iso_mapping_path is None:
            iso_mapping_path = self.cache_dir / "iso" / "un_m49_country_codes.csv"
        self.iso_mapping_path = Path(iso_mapping_path)

        # Presets de ponderación — cargados desde references/ si existen
        self._weight_presets: dict[int, dict[str, float]] = {}
        self._load_weight_presets()

    # ---------- Download & cache ----------

    def _entry(self, key: str) -> CacheEntry:
        spec = DATASET_SOURCES[key]
        folder = self.cache_dir / spec["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / spec["filename"]
        return CacheEntry(
            path=path,
            meta_path=path.with_suffix(path.suffix + ".meta.json"),
            version=spec["version"],
            source_url=spec["url"],
        )

    def _write_meta(self, entry: CacheEntry, key: str) -> None:
        sha = hashlib.sha256(entry.path.read_bytes()).hexdigest()
        meta = {
            "dataset": key,
            "version": entry.version,
            "source_url": entry.source_url,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "sha256": sha,
            "filename": entry.path.name,
            "size_bytes": entry.path.stat().st_size,
        }
        entry.meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    def ensure(self, key: str, force_refresh: bool = False) -> Path:
        """Garantiza que el dataset esté en cache. Devuelve el path local del CSV/XLSX listo para leer."""
        entry = self._entry(key)
        if entry.path.exists() and not force_refresh:
            return entry.path

        spec = DATASET_SOURCES[key]
        needs_conversion = spec.get("needs_conversion", False)

        if needs_conversion:
            raw_path = entry.path.parent / spec["raw_filename"]
            if not raw_path.exists() or force_refresh:
                logger.info("Descargando dataset crudo %s desde %s", key, entry.source_url)
                resp = requests.get(entry.source_url, stream=True, timeout=600)
                resp.raise_for_status()
                with open(raw_path, "wb") as fh:
                    for chunk in resp.iter_content(chunk_size=1 << 16):
                        fh.write(chunk)
                logger.info("Descarga cruda completa: %s (%.1f MB)",
                           raw_path.name, raw_path.stat().st_size / 1e6)

            logger.info("Convirtiendo %s a CSV (esto puede tardar)", raw_path.name)
            self._convert_rda_to_csv(key, raw_path, entry.path)
        else:
            logger.info("Descargando dataset %s desde %s", key, entry.source_url)
            resp = requests.get(entry.source_url, stream=True, timeout=300)
            resp.raise_for_status()
            with open(entry.path, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=1 << 16):
                    fh.write(chunk)

        self._write_meta(entry, key)
        return entry.path

    def _convert_rda_to_csv(self, key: str, rda_path: Path, csv_path: Path) -> None:
        """Convierte un archivo .rda (R) a CSV usando pyreadr."""
        try:
            import pyreadr
        except ImportError as exc:
            raise ImportError(
                "pyreadr no esta instalado. Correr: pip install pyreadr"
            ) from exc

        result = pyreadr.read_r(str(rda_path))
        if not result:
            raise RuntimeError(f"El archivo {rda_path} no contiene objetos legibles")
        df_name, df = next(iter(result.items()))
        logger.info("Objeto R '%s' leido: %d filas, %d columnas",
                   df_name, len(df), len(df.columns))
        df.to_csv(csv_path, index=False)
        logger.info("CSV convertido: %s (%.1f MB)",
                   csv_path.name, csv_path.stat().st_size / 1e6)

    def ensure_all(self, force_refresh: bool = False) -> dict[str, Path]:
        return {k: self.ensure(k, force_refresh) for k in DATASET_SOURCES}

    # ---------- ISO / M49 mapping ----------

    def iso_map(self) -> pd.DataFrame:
        """Tabla de códigos: columnas `country_code` (M49), `iso3`, `iso2`, `name_es`, `name_en`."""
        if self._iso_map is not None:
            return self._iso_map
        if not self.iso_mapping_path.exists():
            raise FileNotFoundError(
                f"Falta el mapeo ISO↔M49 en {self.iso_mapping_path}. "
                "Ver references/un_m49_mapping.md para cómo generarlo."
            )
        self._iso_map = pd.read_csv(self.iso_mapping_path, dtype={"country_code": int})
        return self._iso_map

    def _attach_m49(self, df: pd.DataFrame, iso_column: str, iso_type: str = "iso3") -> pd.DataFrame:
        iso = self.iso_map()[[iso_type, "country_code"]].drop_duplicates()
        out = df.merge(iso, how="left", left_on=iso_column, right_on=iso_type)
        missing = out["country_code"].isna().sum()
        if missing:
            logger.warning("%d filas sin match M49 al joinear por %s", missing, iso_column)
        return out

    # ---------- Loaders ----------

    def load_vdem(self, columns: list[str] | None = None, year: int | None = None) -> pd.DataFrame:
        path = self.ensure("vdem")
        use = None
        if columns:
            use = list({"country_text_id", "country_id", "year", *columns})
        df = pd.read_csv(path, usecols=use, low_memory=False)
        df = self._attach_m49(df, iso_column="country_text_id", iso_type="iso3")
        if year is not None:
            df = df[df["year"] == year]
        return df

    def load_fh(self, year: int | None = None) -> pd.DataFrame:
        path = self.ensure("fh")
        df = pd.read_excel(path, sheet_name=0, header=1)
        rename = {
            "Country/Territory": "country_name",
            "Edition": "year",
            "Total": "total_score",
            "Status": "status",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
        df = self._attach_m49(df, iso_column="country_name", iso_type="name_en")
        if year is not None:
            df = df[df["year"] == year]
        return df

    def load_pei(self, year: int | None = None) -> pd.DataFrame:
        path = self.ensure("pei")
        df = pd.read_csv(path, low_memory=False)
        if "ISO" in df.columns:
            iso_col, iso_type = "ISO", "iso3"
        elif "country" in df.columns:
            iso_col, iso_type = "country", "name_en"
        else:
            raise KeyError("PEI: no se encontró columna ISO ni country")
        df = self._attach_m49(df, iso_column=iso_col, iso_type=iso_type)
        if year is not None and "year" in df.columns:
            df = df[df["year"] == year]
        return df

    def load_rsf(self, year: int | None = None) -> pd.DataFrame:
        path = self.ensure("rsf")
        df = pd.read_csv(path, sep=";", encoding="utf-8")
        rename = {
            "ISO": "iso3",
            "Score 2025": "score",
            "Score": "score",
            "Country_EN": "country_name",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
        df = self._attach_m49(df, iso_column="iso3", iso_type="iso3")
        return df

    # ---------- Normalización ----------

    @staticmethod
    def _normalize(value: float | None, source: str) -> float | None:
        if value is None or pd.isna(value):
            return None
        if source == "vdem":
            return float(value) * 100.0
        if source == "pei":
            return float(value)
        if source == "fh":
            return float(value)
        if source == "rsf":
            return 100.0 - float(value)
        raise ValueError(f"Fuente desconocida: {source}")

    # ---------- Consultas por país ----------

    def country_snapshot(self, country_code: int, year: int | None = None) -> dict[str, Any]:
        """Devuelve los valores crudos y normalizados para un país."""
        snap: dict[str, Any] = {"country_code": country_code, "year": year}

        def _pick(df: pd.DataFrame, col: str) -> float | None:
            sub = df[df["country_code"] == country_code]
            if year is not None and "year" in sub.columns:
                sub = sub[sub["year"] == year]
            if sub.empty:
                return None
            if "year" in sub.columns:
                sub = sub.sort_values("year", ascending=False)
            val = sub.iloc[0].get(col)
            return None if pd.isna(val) else float(val)

        vdem_df = self.load_vdem(columns=["v2x_polyarchy"])
        pei_df = self.load_pei()
        fh_df = self.load_fh()
        rsf_df = self.load_rsf()

        snap["vdem"] = {"v2x_polyarchy": _pick(vdem_df, "v2x_polyarchy")}
        snap["pei"] = {"PEIIndexp": _pick(pei_df, "PEIIndexp")}
        snap["fh"] = {"total_score": _pick(fh_df, "total_score")}
        snap["rsf"] = {"score": _pick(rsf_df, "score")}

        snap["normalized"] = {
            "vdem": self._normalize(snap["vdem"]["v2x_polyarchy"], "vdem"),
            "pei": self._normalize(snap["pei"]["PEIIndexp"], "pei"),
            "fh": self._normalize(snap["fh"]["total_score"], "fh"),
            "rsf": self._normalize(snap["rsf"]["score"], "rsf"),
        }
        return snap

    # ---------- Índice compuesto PEIRS ----------

    def _effective_weights(self, country_code: int, weights: dict[str, float] | None) -> dict[str, float]:
        if weights is not None:
            return weights
        if country_code in self._weight_presets:
            return self._weight_presets[country_code]
        return DEFAULT_WEIGHTS

    def peirs_score(
        self,
        country_code: int,
        year: int | None = None,
        weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """Calcula el índice compuesto PEIRS (0–100, mayor = mejor)."""
        snap = self.country_snapshot(country_code, year=year)
        w = self._effective_weights(country_code, weights)

        # Filtrar fuentes sin dato y re-escalar pesos
        available = {k: v for k, v in snap["normalized"].items() if v is not None}
        if not available:
            return {"country_code": country_code, "score": None, "missing": list(snap["normalized"])}

        total_w = sum(w[k] for k in available)
        score = sum(available[k] * (w[k] / total_w) for k in available)

        return {
            "country_code": country_code,
            "year": year,
            "score": round(score, 2),
            "components": snap["normalized"],
            "weights_used": {k: round(w[k] / total_w, 4) for k in available},
            "missing": [k for k in snap["normalized"] if snap["normalized"][k] is None],
        }

    def regional_scores(self, un_codes: list[int], year: int | None = None) -> pd.DataFrame:
        rows = [self.peirs_score(c, year=year) for c in un_codes]
        return pd.DataFrame(rows).sort_values("score", ascending=False, na_position="last")

    # ---------- Presets ----------

    def _load_weight_presets(self) -> None:
        # El skill mira references/ relativo al archivo, pero desde la instalación
        # del usuario el path correcto es skills/electoral-data-integration/references/
        candidates = [
            Path(__file__).resolve().parent.parent / "references" / "country_weight_presets.json",
            self.cache_dir.parent / "skills" / "electoral-data-integration" / "references" / "country_weight_presets.json",
        ]
        for p in candidates:
            if p.exists():
                try:
                    raw = json.loads(p.read_text(encoding="utf-8"))
                    self._weight_presets = {int(k): v for k, v in raw.items() if not k.startswith("_")}
                    return
                except Exception as exc:
                    warnings.warn(f"No se pudo cargar presets de {p}: {exc}")

    # ---------- Utilidades ----------

    def cache_status(self) -> pd.DataFrame:
        rows = []
        for key in DATASET_SOURCES:
            entry = self._entry(key)
            exists = entry.path.exists()
            meta = {}
            if entry.meta_path.exists():
                try:
                    meta = json.loads(entry.meta_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            rows.append({
                "dataset": key,
                "cached": exists,
                "size_mb": round(entry.path.stat().st_size / 1e6, 2) if exists else None,
                "downloaded_at": meta.get("downloaded_at"),
                "sha256": meta.get("sha256"),
            })
        return pd.DataFrame(rows)
