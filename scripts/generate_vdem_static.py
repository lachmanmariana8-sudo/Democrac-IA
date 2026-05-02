"""Genera data/vdem_static_all.json + backend/modules/vdem_static.py
desde el CSV completo de V-Dem (cualquier version v15+).

Uso:
    python scripts/generate_vdem_static.py [--csv PATH] [--out-json PATH] [--out-py PATH]

Defaults apuntan a v16. Re-ejecutar cada vez que V-Dem publique nueva version
(suele ser anual en marzo).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent

# 38 ISO-3 codes que monitorea PEIRS (mismo orden que COUNTRY_CATALOG).
COUNTRIES = [
    "VEN", "NIC", "GTM", "URY", "COL", "BRA", "MEX", "ARG",
    "CHL", "BOL", "ECU", "PER", "HND", "SLV", "PAN", "CRI",
    "DOM", "PRY", "CUB", "DEU", "FRA", "HUN", "POL", "TUR",
    "RUS", "BLR", "UKR", "GEO", "ZAF", "NGA", "KEN", "ZWE",
    "GHA", "IND", "PHL", "IDN", "THA", "TUN",
]

# 21 indicadores que usamos en analisis Elite + PEIRS clasico.
INDICATORS = [
    "v2x_libdem", "v2x_polyarchy", "v2x_partipdem", "v2x_delibdem", "v2x_egaldem",
    "v2xel_frefair", "v2x_freexp_altinf", "v2x_frassoc_thick", "v2x_suffr", "v2xcl_rol",
    "v2elembaut", "v2elembcap", "v2elirreg", "v2elintim", "v2elintmon",
    "v2mecenefm", "v2meharjrn", "v2mebias",
    "v2psbars", "v2psoppaut", "v2jureview",
]

YEAR_FROM = 1985
YEAR_TO = None  # auto: max year disponible


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(REPO_ROOT / "data" / "vdem" / "vdem_v16.csv"))
    ap.add_argument("--out-json", default=str(REPO_ROOT / "data" / "vdem_static_all.json"))
    ap.add_argument("--out-py", default=str(REPO_ROOT / "backend" / "modules" / "vdem_static.py"))
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise SystemExit(f"CSV no encontrado: {csv_path}")

    print(f"[1/4] Leyendo {csv_path}...")
    cols_needed = ["country_text_id", "year"] + INDICATORS
    df = pd.read_csv(csv_path, usecols=cols_needed, low_memory=False)
    print(f"      {len(df):,} filas, {len(df.columns)} columnas")

    year_to = YEAR_TO or int(df["year"].max())
    print(f"      rango años: {YEAR_FROM}-{year_to}")

    print(f"[2/4] Filtrando {len(COUNTRIES)} paises x {year_to - YEAR_FROM + 1} años...")
    sub = df[
        (df["country_text_id"].isin(COUNTRIES)) &
        (df["year"] >= YEAR_FROM) &
        (df["year"] <= year_to)
    ].copy()
    print(f"      {len(sub):,} filas resultantes")

    print("[3/4] Construyendo dict {country: {year: {indicator: value}}}...")
    out: dict = {}
    for cc in COUNTRIES:
        cc_data: dict = {}
        rows = sub[sub["country_text_id"] == cc]
        for _, r in rows.iterrows():
            year_block: dict = {}
            for ind in INDICATORS:
                v = r.get(ind)
                if pd.notna(v):
                    year_block[ind] = round(float(v), 3)
            if year_block:
                cc_data[str(int(r["year"]))] = year_block
        out[cc] = cc_data

    # JSON canonical
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    json_size = Path(args.out_json).stat().st_size / 1024
    print(f"      JSON: {args.out_json} ({json_size:.0f} KB)")

    print(f"[4/4] Escribiendo modulo Python...")
    py_header = f'''"""
DEMOCRAC.IA / PEIRS — V-Dem v{{version}} static fallback — ALL supported countries.
Auto-generated from {csv_path.name} ({YEAR_FROM}-{year_to}, {len(COUNTRIES)} countries, {len(INDICATORS)} indicators).
Used when the full CSV is not available (Railway production).

Structure: VDEM_STATIC[country_code][year] = {{indicator: value, ...}}
Example:   VDEM_STATIC["PER"][2024]["v2x_libdem"]  -> 0.4821

Regenerar via: python scripts/generate_vdem_static.py
"""

VDEM_STATIC: dict = '''
    py_header = py_header.replace("{{version}}", "16")

    py_path = Path(args.out_py)
    py_path.parent.mkdir(parents=True, exist_ok=True)
    # Compactamos JSON a python literal con orjson-style separators.
    py_body = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(py_header)
        f.write(py_body)
        f.write("\n")
    py_size = py_path.stat().st_size / 1024
    print(f"      PY:   {py_path} ({py_size:.0f} KB)")

    print("\nOK")


if __name__ == "__main__":
    main()
