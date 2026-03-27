"""
DEMOCRAC.IA / PEIRS — Configuración centralizada
Centraliza todas las variables de entorno, constantes LLM y del framework de trazabilidad.
"""
import os
from fastapi.security import APIKeyHeader

# ── LLM ─────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL: str = "claude-sonnet-4-20250514"
LLM_TEMPERATURE: float = 0.2

# ── Observer Protocol — Autenticación ────────────────────────────────────────
# Formato env: OBSERVER_API_KEYS=key1,key2,key3
# Default dev key — CAMBIAR en producción via variable de entorno
_raw_keys = os.getenv("OBSERVER_API_KEYS", "democracia-obs-dev-2026")
OBSERVER_API_KEYS: set = set(k.strip() for k in _raw_keys.split(",") if k.strip())

obs_key_header = APIKeyHeader(name="X-Observer-Key", auto_error=False)

# ── Rutas a datasets ─────────────────────────────────────────────────────────
VDEM_CSV_PATH: str = os.getenv("VDEM_CSV_PATH", "../data/V-Dem-CY-Full+Others-v15.csv")
FH_CSV_PATH: str   = os.getenv("FH_CSV_PATH",   "../data/All_data_FIW_2013-2025 - Index.csv")
RSF_CSV_PATH: str  = os.getenv("RSF_CSV_PATH",  "../data/RSF/2025 - 2025.csv")
PEI_CSV_PATH: str  = os.getenv("PEI_CSV_PATH",  "../data/PEI/PEI_10 Election External.csv")

# ── Columnas V-Dem ───────────────────────────────────────────────────────────
VDEM_COLUMNS = [
    "country_text_id", "year",
    "v2x_libdem", "v2x_polyarchy", "v2x_partipdem", "v2x_delibdem", "v2x_egaldem",
    "v2xel_frefair", "v2x_freexp_altinf", "v2x_frassoc_thick", "v2x_suffr", "v2xcl_rol",
    "v2elembaut", "v2elembcap", "v2elirreg", "v2elintim", "v2elintmon",
    "v2mecenefi", "v2mecenefm", "v2meharjrn", "v2mebias",
    "v2smgovdom", "v2smgovfilcap", "v2smregcap",
    "v2psbars", "v2psoppaut", "v2jureview",
]
VDEM_LAST_YEAR = 2024
VDEM_VERSION   = "v15"
VDEM_CITATION  = (
    "Coppedge et al. 2025. 'V-Dem Country-Year Dataset v15' "
    "Varieties of Democracy (V-Dem) Project. https://doi.org/10.23696/vdemds25"
)
VDEM_SOURCE_URL = "https://v-dem.net/data/the-v-dem-dataset/"

# ── Freedom House ────────────────────────────────────────────────────────────
FH_LAST_EDITION = 2025
FH_VERSION      = "FIW_2025"
FH_CITATION     = (
    "Freedom House. 2025. 'Freedom in the World 2025: The Uphill Battle to Safeguard Rights.' "
    "Washington, DC: Freedom House. https://freedomhouse.org/report/freedom-world"
)
FH_SOURCE_URL = "https://freedomhouse.org/report/freedom-world"

FH_COUNTRY_NAMES = {
    "VEN": "Venezuela", "NIC": "Nicaragua", "GTM": "Guatemala", "URY": "Uruguay",
    "COL": "Colombia", "BRA": "Brazil", "MEX": "Mexico", "ARG": "Argentina",
    "CHL": "Chile", "BOL": "Bolivia", "ECU": "Ecuador", "PER": "Peru",
    "HND": "Honduras", "SLV": "El Salvador", "PAN": "Panama",
    "CRI": "Costa Rica", "DOM": "Dominican Republic", "PRY": "Paraguay", "CUB": "Cuba",
    "DEU": "Germany", "FRA": "France", "HUN": "Hungary", "POL": "Poland",
    "TUR": "Turkey", "RUS": "Russia", "BLR": "Belarus", "UKR": "Ukraine", "GEO": "Georgia",
    "ZAF": "South Africa", "NGA": "Nigeria", "KEN": "Kenya", "ZWE": "Zimbabwe", "GHA": "Ghana",
    "IND": "India", "PHL": "Philippines", "IDN": "Indonesia", "THA": "Thailand", "TUN": "Tunisia",
}

# ── RSF ──────────────────────────────────────────────────────────────────────
RSF_VERSION   = "RSF_2025"
RSF_CITATION  = (
    "Reporters Without Borders (RSF). 2025. 'World Press Freedom Index 2025.' "
    "https://rsf.org/en/index"
)
RSF_SOURCE_URL = "https://rsf.org/en/index"

# ── PEI ──────────────────────────────────────────────────────────────────────
PEI_VERSION  = "PEI-10.0"
PEI_CITATION = (
    "Garnett, H. A., James, T. S., & Caal-Lam, S. (2024). "
    "'Perceptions of Electoral Integrity (PEI-10.0).' "
    "Electoral Integrity Project. https://doi.org/10.7910/DVN/FQ5ECC"
)
PEI_SOURCE_URL = "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/FQ5ECC"

PEI_COLUMNS = [
    "ISO", "election", "year", "office",
    "OVERALLINTEGRITY", "EMBs", "LAWS", "PROCEDURES", "BOUNDARIES",
    "VOTERREGISTRATION", "MEDIACOVERAGE", "CAMPAIGNFINANCE",
    "VOTINGPROCESS", "VOTECOUNT", "VOTINGRESULTS", "ELECTIONAUTHORITIES",
]

# ── Framework de trazabilidad ─────────────────────────────────────────────────
CONFIDENCE_CONFIRMED  = "confirmed"
CONFIDENCE_PROBABLE   = "probable"
CONFIDENCE_UNVERIFIED = "unverified"
CONFIDENCE_MOCK       = "mock"

SOURCE_API      = "api"
SOURCE_SCRAPING = "scraping"
SOURCE_DOCUMENT = "document"
SOURCE_SOCIAL   = "social_media"
SOURCE_MANUAL   = "manual_entry"
SOURCE_MOCK     = "mock_data"
