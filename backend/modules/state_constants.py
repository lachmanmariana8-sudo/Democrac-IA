"""
DEMOCRAC.IA / PEIRS — Constantes del framework de trazabilidad

Constantes compartidas entre app.py, agents/, modules/. Antes vivían inline
en app.py — extraídas el 2026-05-30 como Fase 1 del refactor de migración
(audit #2 del 2026-05-29). Mover acá hace posible que futuros módulos en
agents/nodes.py importen sin crear dependencias circulares con app.py.

Estos identificadores forman parte del esquema de 9 metadatos por dato que
el proyecto enforza (cf. PEIRS_Documento_Institucional_v2.0):
  - source_type → uno de SOURCE_*
  - confidence_level → uno de CONFIDENCE_*

Si se publica un dato con confidence_level == "mock", NO alimenta el risk
score ni los gráficos públicos.
"""
from __future__ import annotations

# ── Confidence levels ──────────────────────────────────────────────────────
# Marcan el grado de verificabilidad de un dato. Solo "confirmed" y "probable"
# alimentan el Elite Report; "unverified" y "mock" quedan en el anexo C
# (todos los hallazgos) sin propagar al score público.
CONFIDENCE_CONFIRMED = "confirmed"
CONFIDENCE_PROBABLE = "probable"
CONFIDENCE_UNVERIFIED = "unverified"
CONFIDENCE_MOCK = "mock"

# ── Source types ───────────────────────────────────────────────────────────
# Categoriza la procedencia del dato. Determina cómo formatear la cita
# bibliográfica APA 7 en el Anexo B del Elite Report.
SOURCE_API = "api"               # Dataset estructural (V-Dem, FH, PEI, RSF)
SOURCE_SCRAPING = "scraping"     # Web scraping / RSS Hunter
SOURCE_DOCUMENT = "document"     # PDF / resolución oficial
SOURCE_SOCIAL = "social_media"   # Hallazgo en redes (X, TikTok)
SOURCE_MANUAL = "manual_entry"   # Observador con sesión activa
SOURCE_MOCK = "mock_data"        # Fallback para países sin cobertura real


__all__ = [
    "CONFIDENCE_CONFIRMED",
    "CONFIDENCE_PROBABLE",
    "CONFIDENCE_UNVERIFIED",
    "CONFIDENCE_MOCK",
    "SOURCE_API",
    "SOURCE_SCRAPING",
    "SOURCE_DOCUMENT",
    "SOURCE_SOCIAL",
    "SOURCE_MANUAL",
    "SOURCE_MOCK",
]
