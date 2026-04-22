---
name: electoral-data-integration
description: Descarga, cachea y consulta los cuatro datasets base de PEIRS (V-Dem v15, Freedom House FIW 2025, PEI 10.0, RSF Press Freedom Index 2025). Unifica todo con código numérico ONU (M49) como llave maestra y calcula un índice compuesto PEIRS con ponderaciones configurables por país. Úsalo siempre que un agente de Democrac.IA/PEIRS necesite leer, actualizar o combinar estos datasets, o cuando se pida calcular el score PEIRS de uno o varios países. No usar para datasets ajenos al núcleo (encuestas, padrones) — para eso, crear un skill específico.
---

# Electoral Data Integration — PEIRS Core Datasets

Este skill centraliza el acceso a las cuatro fuentes canónicas de PEIRS y expone una API común en Python para los agentes LangGraph.

## Principios

1. **Una sola llave**: código numérico ONU (M49) en columna `country_code`. Los nombres y códigos alfa son solo para visualización.
2. **Cache local primero**: todos los datasets viven en `D:\DemocracIA\data\` con subcarpetas por fuente. La descarga solo corre si el archivo no existe o si se pasa `force_refresh=True`.
3. **Trazabilidad obligatoria**: cada descarga genera un sidecar `.meta.json` con URL fuente, fecha, SHA-256 y versión. Esto alimenta al futuro skill `source-traceability`.
4. **Año-consciente**: todos los loaders aceptan `year=` y devuelven el año más reciente disponible por defecto.
5. **Nada silencioso**: si un país no existe en un dataset, devolver `None` y loguear warning — nunca rellenar con ceros ni promedios.

## Estructura de la cache

```
D:\DemocracIA\data\
├── vdem\
│   ├── V-Dem-CY-Full+Others-v15.csv
│   └── V-Dem-CY-Full+Others-v15.csv.meta.json
├── freedomhouse\
│   ├── fiw_2025.xlsx
│   └── fiw_2025.xlsx.meta.json
├── pei\
│   ├── PEI_country-level_10.0.csv
│   └── PEI_country-level_10.0.csv.meta.json
├── rsf\
│   ├── rsf_index_2025.csv
│   └── rsf_index_2025.csv.meta.json
└── iso\
    └── un_m49_country_codes.csv
```

Nunca toques manualmente estos archivos — usar los scripts del skill.

## Quick start

```python
from scripts.peirs_data import PeirsData

data = PeirsData(cache_dir=r"D:\DemocracIA\data")

# Descarga/carga todos los datasets para el último año disponible
data.ensure_all()

# Consultar un país por código ONU (Argentina = 32, Perú = 604, Bolivia = 68)
arg = data.country_snapshot(country_code=32)
print(arg["vdem"]["v2x_polyarchy"])
print(arg["pei"]["PEIIndexp"])
print(arg["fh"]["total_score"])
print(arg["rsf"]["score"])

# Índice compuesto PEIRS con ponderaciones por defecto
score = data.peirs_score(country_code=604)  # Perú

# Ponderaciones específicas para un país de alto riesgo
score = data.peirs_score(
    country_code=604,
    weights={"vdem": 0.40, "pei": 0.30, "fh": 0.20, "rsf": 0.10}
)
```

## Ponderaciones por defecto

El índice compuesto PEIRS se calcula como promedio ponderado de los cuatro subíndices, cada uno normalizado a escala 0–100 (mayor = mejor integridad).

| Fuente | Peso por defecto | Racional |
|--------|------------------|----------|
| V-Dem (`v2x_polyarchy`) | 0.35 | Más granular y académicamente sólido |
| PEI (`PEIIndexp`) | 0.30 | Específico para integridad electoral |
| Freedom House (`total_score`) | 0.20 | Amplia cobertura, bueno para benchmark |
| RSF (`score` invertido) | 0.15 | Captura libertad de prensa, proxy débil pero necesario |

Las ponderaciones se sobreescriben por país pasando `weights=` o usando los presets en `references/country_weight_presets.json`.

## Normalización

Cada dataset usa escala distinta. El skill normaliza a 0–100 (más alto = mejor):

- **V-Dem `v2x_polyarchy`**: originalmente 0–1 → multiplicar por 100.
- **PEI `PEIIndexp`**: originalmente 0–100 → se usa tal cual.
- **FH `total_score`**: originalmente 0–100 → se usa tal cual.
- **RSF `score`**: originalmente 0–100 donde **menor = mejor** → invertir: `100 - score`.

## Workflow típico desde un agente

```python
# Agent 1 (OSINT ingestion) — al arrancar observación
data = PeirsData(cache_dir=PEIRS_CACHE)
data.ensure_all()  # garantiza datos frescos

# Agent 3 (legal compliance) — consulta baseline
baseline = data.country_snapshot(country_code=COUNTRY_UN)
risk_level = "HIGH" if data.peirs_score(COUNTRY_UN) < 50 else "STANDARD"

# Agent 5 (dictamen) — comparación regional
regional = data.regional_scores(un_codes=[32, 604, 68, 858])  # ARG, PER, BOL, URY
```

## Scripts

- `scripts/peirs_data.py` — clase principal `PeirsData`.
- `scripts/download_datasets.py` — CLI para refrescar la cache manualmente.
- `scripts/verify_cache.py` — valida SHA-256 y reporta datasets faltantes.

## Referencias

- `references/dataset_schemas.md` — columnas exactas que usa PEIRS de cada dataset.
- `references/un_m49_mapping.md` — cómo mapear ISO alfa-3/alfa-2 ↔ M49.
- `references/country_weight_presets.json` — ponderaciones custom por país.

## Errores comunes

- **"KeyError: country_code 530"** — ese código M49 está reservado (Antillas Holandesas disueltas). Revisar `references/un_m49_mapping.md`.
- **PEI no tiene dato para el año solicitado** — PEI no publica anualmente; usar `year="latest"` o el año de la última elección del país.
- **V-Dem pesa >500MB** — es normal. El CSV completo tarda ~30s en cargar. Usar `data.load_vdem(columns=[...])` para cargar solo las columnas necesarias.

## Limitaciones conocidas

- RSF cambió metodología en 2022. Comparaciones pre/post-2022 requieren nota al pie.
- Freedom House FIW sale en marzo con datos del año anterior. El "año actual" siempre es año-1.
- V-Dem agrega ~1 año de rezago. Para elecciones en curso, complementar con fuentes OSINT del Agent 1.
