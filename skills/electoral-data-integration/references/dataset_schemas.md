# Dataset Schemas — columnas usadas por PEIRS

Este documento lista SOLO las columnas que PEIRS consume de cada fuente. Los datasets originales tienen cientos de columnas más — ignorarlas.

## V-Dem v15

Archivo: `V-Dem-CY-Full+Others-v15.csv`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `country_text_id` | str (ISO3) | Llave para joinear con M49 |
| `country_name` | str | Nombre en inglés |
| `year` | int | Año de observación |
| `v2x_polyarchy` | float 0–1 | Electoral democracy index (Dahl) |
| `v2x_libdem` | float 0–1 | Liberal democracy index (opcional) |
| `v2xel_frefair` | float 0–1 | Free and fair elections (opcional) |
| `v2elfrfair` | float | Elecciones libres y justas, evaluación expertos |
| `v2elintim` | float | Intimidación violenta en elecciones |

Nota: V-Dem invierte la escala de algunas variables. Verificar codebook si se usa algo fuera del subset de arriba.

## Freedom House — FIW 2025

Archivo: `fiw_2025.xlsx`, hoja 1, header en fila 2.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `Country/Territory` → `country_name` | str | Nombre en inglés |
| `Edition` → `year` | int | Año de la edición |
| `Total` → `total_score` | int 0–100 | Score agregado (PR+CL) |
| `Status` → `status` | str | "F", "PF", "NF" |
| `PR` | int 0–40 | Political Rights |
| `CL` | int 0–60 | Civil Liberties |

## PEI 10.0 — Perceptions of Electoral Integrity

Archivo: `PEI_country-level_10.0.csv`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `ISO` | str (ISO3) | Llave para M49 |
| `country` | str | Nombre en inglés |
| `year` | int | Año elección |
| `PEIIndexp` | float 0–100 | PEI Index (percepción) |
| `electionid` | str | ID único de elección |

Importante: PEI no publica un dato por año-calendario; publica por elección. Si consultás Argentina 2023, te devuelve el score de las PASO/generales 2023.

## RSF Press Freedom Index 2025

Archivo: `rsf_index_2025.csv` (separador `;`)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `ISO` → `iso3` | str | Código ISO3 |
| `Country_EN` → `country_name` | str | Nombre |
| `Score 2025` → `score` | float 0–100 | **Menor = mejor** (invertir antes de agregar) |
| `Rank 2025` | int | Ranking global |

## Mapeo ISO ↔ M49

Archivo: `iso/un_m49_country_codes.csv`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `country_code` | int | Código M49 (llave maestra PEIRS) |
| `iso3` | str | ISO 3166-1 alpha-3 |
| `iso2` | str | ISO 3166-1 alpha-2 |
| `name_en` | str | Nombre oficial en inglés |
| `name_es` | str | Nombre oficial en español |
| `region` | str | Región ONU |
| `subregion` | str | Subregión ONU |
