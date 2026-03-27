"""
DEMOCRAC.IA / PEIRS — Data Loaders
Carga y consulta de los datasets externos: V-Dem v15, Freedom House FIW 2025,
RSF Press Freedom Index 2025, PEI v10.0.

Todos los loaders siguen el mismo patrón:
  - load_*_data()  → DataFrame o None (fallback gracioso si CSV no existe)
  - get_*_country() → Dict o None
"""
from __future__ import annotations

import os
from io import StringIO
from typing import Dict, Optional

import pandas as pd

from modules.config import (
    VDEM_CSV_PATH, VDEM_COLUMNS, VDEM_LAST_YEAR, VDEM_VERSION, VDEM_CITATION,
    FH_CSV_PATH, FH_LAST_EDITION, FH_VERSION, FH_CITATION, FH_COUNTRY_NAMES,
    RSF_CSV_PATH, RSF_VERSION, RSF_CITATION,
    PEI_CSV_PATH, PEI_VERSION, PEI_CITATION,
)


# ═══════════════════════════════════════════════════════════════════════════════
# V-Dem v15
# ═══════════════════════════════════════════════════════════════════════════════

def load_vdem_data() -> Optional[pd.DataFrame]:
    if not os.path.exists(VDEM_CSV_PATH):
        print(f"[V-Dem] AVISO: CSV no encontrado en '{VDEM_CSV_PATH}'. Usando datos mock.")
        return None
    try:
        df = pd.read_csv(VDEM_CSV_PATH, usecols=VDEM_COLUMNS, low_memory=False)
        print(f"[V-Dem] ✅ Dataset cargado: {len(df):,} filas, {len(df.columns)} columnas.")
        print(f"[V-Dem] Años disponibles: {int(df['year'].min())}–{int(df['year'].max())}")
        return df
    except Exception as e:
        print(f"[V-Dem] ERROR al cargar CSV: {e}. Usando datos mock.")
        return None


def get_vdem_country(
    df: Optional[pd.DataFrame],
    country_code: str,
    year: int = VDEM_LAST_YEAR,
) -> Optional[Dict]:
    if df is None:
        return None

    row = df[(df["country_text_id"] == country_code) & (df["year"] == year)]
    if row.empty:
        row = df[(df["country_text_id"] == country_code) & (df["year"] == year - 1)]
    if row.empty:
        print(f"[V-Dem] AVISO: No se encontraron datos para {country_code} ({year}).")
        return None

    r = row.iloc[0]
    actual_year = int(r["year"])

    def norm_vdem(val, min_val=-4.0, max_val=4.0):
        if pd.isna(val):
            return None
        return round((float(val) - min_val) / (max_val - min_val), 4)

    def norm_inverted(val, min_val=-4.0, max_val=4.0):
        n = norm_vdem(val, min_val, max_val)
        return round(1.0 - n, 4) if n is not None else None

    def safe_norm_inv(col, **kwargs):
        return norm_inverted(r[col], **kwargs) if col in r.index and pd.notna(r.get(col)) else None

    def safe_norm(col, **kwargs):
        return norm_vdem(r[col], **kwargs) if col in r.index and pd.notna(r.get(col)) else None

    emb_aut_raw = float(r["v2elembaut"]) if pd.notna(r["v2elembaut"]) else 0.0
    if emb_aut_raw >= 1.5:
        emb_independence_level = "full"
    elif emb_aut_raw >= 0.0:
        emb_independence_level = "partial"
    elif emb_aut_raw >= -1.5:
        emb_independence_level = "compromised"
    else:
        emb_independence_level = "captured"

    intmon_raw = r["v2elintmon"]
    international_observation = bool(intmon_raw == 1.0) if pd.notna(intmon_raw) else None

    return {
        "country_code": country_code,
        "year": actual_year,
        "liberal_democracy": round(float(r["v2x_libdem"]), 4),
        "electoral_democracy": round(float(r["v2x_polyarchy"]), 4),
        "participatory_democracy": round(float(r["v2x_partipdem"]), 4),
        "deliberative_democracy": round(float(r["v2x_delibdem"]), 4),
        "egalitarian_democracy": round(float(r["v2x_egaldem"]), 4),
        "free_fair_elections": round(float(r["v2xel_frefair"]), 4),
        "freedom_of_expression": round(float(r["v2x_freexp_altinf"]), 4),
        "freedom_of_association": round(float(r["v2x_frassoc_thick"]), 4),
        "universal_suffrage": round(float(r["v2x_suffr"]), 4),
        "rule_of_law": round(float(r["v2xcl_rol"]), 4),
        "emb_autonomy_raw": round(emb_aut_raw, 4),
        "emb_autonomy": norm_vdem(r["v2elembaut"]),
        "emb_capacity": norm_vdem(r["v2elembcap"]),
        "emb_independence_level": emb_independence_level,
        "electoral_irregularities": norm_inverted(r["v2elirreg"]),
        "electoral_intimidation": norm_inverted(r["v2elintim"]),
        "international_observation": international_observation,
        "internet_censorship": safe_norm_inv("v2mecenefi"),
        "media_censorship": safe_norm_inv("v2mecenefm"),
        "journalist_harassment": safe_norm_inv("v2meharjrn"),
        "media_bias_vdem": safe_norm_inv("v2mebias"),
        "gov_social_media_dominance": safe_norm_inv("v2smgovdom"),
        "gov_internet_filter_capacity": safe_norm_inv("v2smgovfilcap"),
        "social_media_regulation": safe_norm_inv("v2smregcap"),
        "opposition_party_barriers": safe_norm("v2psbars", min_val=0, max_val=4),
        "opposition_autonomy": safe_norm("v2psoppaut"),
        "judicial_review": safe_norm("v2jureview", min_val=0, max_val=4),
        "citation": VDEM_CITATION,
        "dataset_version": VDEM_VERSION,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Freedom House FIW 2025
# ═══════════════════════════════════════════════════════════════════════════════

def load_freedom_house_data() -> Optional[pd.DataFrame]:
    if not os.path.exists(FH_CSV_PATH):
        print(f"[FH] AVISO: CSV no encontrado en '{FH_CSV_PATH}'. Usando datos mock.")
        return None
    try:
        df = pd.read_csv(FH_CSV_PATH, sep=";", skiprows=1)
        df.columns = df.columns.str.strip()
        df["Edition"] = pd.to_numeric(df["Edition"], errors="coerce")
        df["Total"]   = pd.to_numeric(df["Total"],   errors="coerce")
        df["PR rating"] = pd.to_numeric(df["PR rating"], errors="coerce")
        df["CL rating"] = pd.to_numeric(df["CL rating"], errors="coerce")
        print(f"[FH] ✅ Dataset cargado: {len(df):,} filas.")
        print(f"[FH] Ediciones disponibles: {int(df['Edition'].min())}–{int(df['Edition'].max())}")
        return df
    except Exception as e:
        print(f"[FH] ERROR al cargar CSV: {e}. Usando datos mock.")
        return None


def get_freedom_house_country(
    df: Optional[pd.DataFrame],
    country_code: str,
    edition: int = FH_LAST_EDITION,
) -> Optional[Dict]:
    if df is None:
        return None

    fh_name = FH_COUNTRY_NAMES.get(country_code)
    if not fh_name:
        print(f"[FH] AVISO: No hay mapeo de nombre para {country_code}.")
        return None

    row = df[(df["Country/Territory"] == fh_name) & (df["Edition"] == edition)]
    if row.empty:
        row = df[(df["Country/Territory"] == fh_name) & (df["Edition"] == edition - 1)]
    if row.empty:
        print(f"[FH] AVISO: No se encontraron datos para {fh_name} ({edition}).")
        return None

    r = row.iloc[0]
    actual_edition = int(r["Edition"])

    status_map = {"F": "Free", "PF": "Partly Free", "NF": "Not Free"}
    status_raw  = str(r["Status"]).strip() if pd.notna(r["Status"]) else "NF"

    return {
        "country_code": country_code,
        "country_name_fh": fh_name,
        "edition": actual_edition,
        "total_score": int(r["Total"]) if pd.notna(r["Total"]) else 0,
        "score": int(r["Total"]) if pd.notna(r["Total"]) else 0,
        "status": status_map.get(status_raw, status_raw),
        "status_short": status_raw,
        "political_rights_rating": int(r["PR rating"]) if pd.notna(r["PR rating"]) else 7,
        "civil_liberties_rating":  int(r["CL rating"]) if pd.notna(r["CL rating"]) else 7,
        "citation": FH_CITATION,
        "dataset_version": FH_VERSION,
    }


def derive_civil_liberties_from_fh(fh_data: dict) -> dict:
    cl = fh_data.get("civil_liberties_rating", 7)
    pr = fh_data.get("political_rights_rating", 7)
    if cl >= 6:
        press, assembly, judicial = "severely_restricted", "banned", "captured"
    elif cl == 5:
        press, assembly, judicial = "severely_restricted", "restricted", "compromised"
    elif cl == 4:
        press, assembly, judicial = "restricted", "restricted", "compromised"
    elif cl == 3:
        press, assembly, judicial = "partially_restricted", "partially_restricted", "under_pressure"
    elif cl == 2:
        press, assembly, judicial = "mostly_free", "mostly_free", "mostly_independent"
    else:
        press, assembly, judicial = "guaranteed", "guaranteed", "strong"
    return {
        "freedom_of_press":    press,
        "freedom_of_assembly": assembly,
        "judicial_independence": judicial,
        "political_prisoners": pr >= 6,
        "cl_rating": cl,
        "pr_rating": pr,
        "data_source": "Freedom House FIW",
        "data_year": fh_data.get("edition"),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# RSF Press Freedom Index 2025
# ═══════════════════════════════════════════════════════════════════════════════

def load_rsf_data() -> Optional[pd.DataFrame]:
    if not os.path.exists(RSF_CSV_PATH):
        print(f"[RSF] AVISO: CSV no encontrado en '{RSF_CSV_PATH}'.")
        return None
    try:
        with open(RSF_CSV_PATH, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        processed = []
        for line in lines:
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1].replace('""', '"')
            processed.append(line)
        df = pd.read_csv(StringIO("\n".join(processed)))
        df.columns = df.columns.str.strip()
        numeric_cols = ["Score 2025", "Rank", "Political Context", "Economic Context",
                        "Legal Context", "Social Context", "Safety", "Score N-1"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
                df[col] = pd.to_numeric(df[col], errors="coerce")
        print(f"[RSF] ✅ Dataset cargado: {len(df):,} países.")
        return df
    except Exception as e:
        print(f"[RSF] ERROR al cargar CSV: {e}")
        return None


def get_rsf_country(df: Optional[pd.DataFrame], country_code: str) -> Optional[Dict]:
    if df is None:
        return None
    row = df[df["ISO"] == country_code]
    if row.empty:
        return None
    r = row.iloc[0]

    def safe(col):
        return round(float(r[col]), 2) if col in r.index and pd.notna(r[col]) else None

    return {
        "country_code": country_code,
        "score": safe("Score 2025"),
        "rank": int(r["Rank"]) if pd.notna(r.get("Rank")) else None,
        "political_context": safe("Political Context"),
        "economic_context":  safe("Economic Context"),
        "legal_context":     safe("Legal Context"),
        "social_context":    safe("Social Context"),
        "safety":            safe("Safety"),
        "country_en": str(r["Country_EN"]) if "Country_EN" in r.index and pd.notna(r.get("Country_EN")) else None,
        "zone": str(r["Zone"]) if "Zone" in r.index and pd.notna(r.get("Zone")) else None,
        "citation": RSF_CITATION,
        "dataset_version": RSF_VERSION,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PEI — Perceptions of Electoral Integrity v10.0
# ═══════════════════════════════════════════════════════════════════════════════

def load_pei_data() -> Optional[pd.DataFrame]:
    if not os.path.exists(PEI_CSV_PATH):
        print(f"[PEI] AVISO: CSV no encontrado en '{PEI_CSV_PATH}'. Usando datos mock.")
        return None
    try:
        df = pd.read_csv(PEI_CSV_PATH, low_memory=False)
        df.columns = df.columns.str.strip()
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        for col in ["OVERALLINTEGRITY", "EMBs", "LAWS", "PROCEDURES", "BOUNDARIES",
                    "VOTERREGISTRATION", "MEDIACOVERAGE", "CAMPAIGNFINANCE",
                    "VOTINGPROCESS", "VOTECOUNT", "VOTINGRESULTS", "ELECTIONAUTHORITIES"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        print(f"[PEI] ✅ Dataset cargado: {len(df):,} elecciones.")
        print(f"[PEI] Años disponibles: {int(df['year'].min())}–{int(df['year'].max())}")
        return df
    except Exception as e:
        print(f"[PEI] ERROR al cargar CSV: {e}. Usando datos mock.")
        return None


def get_pei_country(df: Optional[pd.DataFrame], country_code: str) -> Optional[Dict]:
    if df is None:
        return None

    rows = df[df["ISO"] == country_code].sort_values("year", ascending=False)
    if rows.empty:
        print(f"[PEI] AVISO: No hay datos para {country_code}.")
        return None

    presidential = rows[rows["office"].str.contains("Presidential", na=False)]
    r = presidential.iloc[0] if not presidential.empty else rows.iloc[0]

    def safe_float(val):
        return round(float(val), 1) if pd.notna(val) else None

    def safe_col(col):
        return safe_float(r[col]) if col in r.index and pd.notna(r[col]) else None

    def safe_col_fb(col_primary, col_fallback=None):
        val = safe_col(col_primary)
        if val is None and col_fallback:
            val = safe_col(col_fallback)
        return val

    return {
        "country_code": country_code,
        "election_id": str(r["election"]),
        "year": int(r["year"]),
        "office": str(r["office"]) if pd.notna(r["office"]) else "N/A",
        "overall_integrity": safe_col_fb("OVERALLINTEGRITY", "PEI_add_original"),
        "emb_score": safe_col_fb("EMBs", "EMBs_m"),
        "legal_framework": safe_col_fb("LAWS", "laws"),
        "procedures": safe_col_fb("PROCEDURES", "procedures"),
        "voter_registration": safe_col_fb("VOTERREGISTRATION", "votereg"),
        "media_coverage": safe_col_fb("MEDIACOVERAGE", "media"),
        "campaign_finance": safe_col_fb("CAMPAIGNFINANCE", "finance"),
        "voting_process": safe_col_fb("VOTINGPROCESS", "voting"),
        "vote_count": safe_col_fb("VOTECOUNT", "count"),
        "voting_results": safe_col_fb("VOTINGRESULTS", "results"),
        "election_authorities": safe_col_fb("ELECTIONAUTHORITIES", "EMBs"),
        "laws_unfair": safe_col("lawsunfair"),
        "laws_favored_incumbent": safe_col("favoredincumbent"),
        "laws_equal": safe_col("equal"),
        "laws_enfranchised": safe_col("enfranchised"),
        "reg_listed": safe_col("reglisted"),
        "reg_inaccurate": safe_col("reginaccurate"),
        "reg_ineligible": safe_col("ineligible"),
        "party_registration": safe_col("PARTYREGISTRATION"),
        "opp_prevent": safe_col("oppprevent"),
        "equal_opp": safe_col("equalopp"),
        "women_opp": safe_col("womenopp"),
        "media_balanced": safe_col("balanced"),
        "media_fair_access": safe_col("fairaccess"),
        "media_disinformation": safe_col("disinformation"),
        "finance_resources": safe_col("resources"),
        "finance_bribed": safe_col("bribed"),
        "citation": PEI_CITATION,
        "dataset_version": PEI_VERSION,
    }
