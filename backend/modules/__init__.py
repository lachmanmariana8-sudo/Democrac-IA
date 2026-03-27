"""
DEMOCRAC.IA / PEIRS — Módulos refactorizados
Split del monolito app.py (v0.4 → v1.0)

Estado de migración:
  ✅ rag/                      — RAG legal (ChromaDB + corpus legal)
  ✅ integrations/ooni.py      — OONI API (censura real-time)
  ✅ integrations/alerts.py    — Agent 7: AlertDispatchAgent
  ✅ modules/instruments.py    — REGION_*, COUNTRY_REGIONS, UNIVERSAL/REGIONAL_INSTRUMENTS, EMB_NAMES
  ✅ modules/catalog.py        — COUNTRY_CATALOG
  ✅ modules/mock_data.py      — MOCK_OSINT_DATA, MOCK_POLITICAL_DATA
  ✅ modules/peru_data.py      — Todos los dicts PERU_*
  ✅ modules/fraud_hate_analysis.py — FraudAllegationAnalysis, HateSpeechAnalysis
  ✅ modules/field_validator.py     — Agent 5: FieldDataValidationAgent

  ⏳ Pendiente:
     modules/config.py        — Configuración (env vars, LLM, constants)
     modules/data_loaders.py  — V-Dem, FH, RSF, PEI loaders + helpers
     chapters/                — Generadores de capítulos (Cap 0–10)
     agents/                  — Los 4 agentes LangGraph
     db/                      — SQLite helpers + migration

Patrón de importación en app.py:
  from modules.instruments import UNIVERSAL_INSTRUMENTS, REGIONAL_INSTRUMENTS, EMB_NAMES
  from modules.catalog import COUNTRY_CATALOG
  from modules.mock_data import MOCK_OSINT_DATA, MOCK_POLITICAL_DATA
  from modules.peru_data import PERU_COUNTRY_PROFILE, PERU_POLITICAL_FORCES, ...
  from modules.fraud_hate_analysis import analyze_fraud_and_hate
  from modules.field_validator import validate_entry, detect_patterns, render_pattern_markdown
"""
