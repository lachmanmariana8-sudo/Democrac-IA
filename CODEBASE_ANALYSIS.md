# DEMOCRAC.IA (PEIRS) — Codebase Analysis for AI Agents

**Comprehensive Guide to Navigate, Build, and Extend the Codebase**
**Current Version:** v0.5.2 (May 2026)

> **Update note (May 4, 2026):** This document was refreshed from v0.4.0
> baseline to reflect v0.5.2. Major changes since v0.4.0:
>
> - Two pipelines now coexist: original LangGraph (4 agents) + Elite Report
>   (6-stage pipeline producing 12 chapters + 3 appendices).
> - V-Dem upgraded to v16 (1789-2025).
> - i18n trilingual (es/en/pt) with 180+ keys + 50 subchapter title mappings.
> - SQLite triple-tier persistence (filesystem + TEXT columns + PDF on-demand).
> - 91/91 tests passing (was 82).
> - Python 3.11 in Railway (Nixpacks); 3.14 in dev local.
> - PDF generation via browser-native `/printable` + `window.print()` (no
>   xhtml2pdf).
> - Architect Agent autonomous via Claude Opus 4.7 + claude-agent-sdk.

---

## 1. GIT & BUILD CONVENTIONS

### Repository Structure

```text
d:\DemocracIA/
├── backend/              # FastAPI + LangGraph agents (Python 3.11 prod / 3.14 dev)
│   └── agents/
│       ├── elite_report/ # Elite Report 6-stage pipeline (12 chapters + 3 appendices)
│       └── ...
├── frontend/             # React 19 + Vite 7 (Node.js ES6 modules)
├── data/                 # Datasets: V-Dem v16, Freedom House, RSF, PEI (~440MB CSV excluded)
├── DOCS Proyect/         # Institutional + technical documentation (es)
├── scripts/              # backup.py, generate_vdem_static.py
├── nixpacks.toml         # Railway Python 3.11 build config
└── [config files]        # Procfile, railway.toml, netlify.toml, requirements.txt
```

### Build & Deployment Files
- **Procfile**: Heroku-compatible — `web: cd backend && python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
- **railway.toml**: Railway.app deployment config (backend)
- **netlify.toml**: Netlify deployment config (frontend)
  - Build command: `npm run build` (from `frontend/`)
  - Publish directory: `frontend/dist`
- **package.json** (frontend): Scripts: `dev`, `build`, `lint`, `preview`
- **requirements.txt** (backend): production dependencies pinned (LangGraph, FastAPI, Anthropic SDK, ChromaDB, sentence-transformers, etc.)
- **requirements-dev.txt**: pytest + dev tooling, separated from prod (NOT installed on Railway)

### Git Conventions
- **.gitignore**: Excludes large datasets (>100MB), generated reports, SQLite DBs, build artifacts
  - Data files like V-Dem CSV, PEI .dta files are NOT versioned
  - Reports generated at `/data/reports/` are auto-generated
  - Database files (`*.db`) regenerated on startup
- **No Docker files present** — uses native Python + Node.js runtimes

### Local Development Setup

```bash
# Backend: Python 3.11 (paridad con Railway) o 3.14 (dev local Windows)
cd backend
pip install -r ../requirements.txt
pip install -r ../requirements-dev.txt   # for pytest + dev tooling
python -m uvicorn app:app --reload --port 8000

# Frontend: Node.js 18+ required
cd frontend
npm install
npm run dev         # Vite dev server on localhost:5173
npm run build       # Production build to dist/
npm run lint        # ESLint check

# Full stack (PowerShell scripts provided)
.\iniciar_backend.ps1     # Backend with PYTHONUTF8=1
.\iniciar_frontend.ps1    # Frontend dev server
```

---

## 2. ARCHITECTURE PATTERNS

### System Topology

```text
┌──────────────────────────────┐
│   React 19 + Vite            │  democracia.ar (Netlify)
│   Single-file App.jsx        │
└────────────┬─────────────────┘
             │ HTTP REST (Railway 8080 prod, localhost:8000 dev)
┌────────────▼─────────────────────────────────────────────┐
│   FastAPI Backend (Python 3.11 Railway / 3.14 dev)       │
│   ┌───────────────────────────────────────────────────┐  │
│   │  Pipeline A — LangGraph (4 agents, original)      │  │
│   │  OSINT → Political → Legal → Report               │  │
│   └───────────────────────────────────────────────────┘  │
│   ┌───────────────────────────────────────────────────┐  │
│   │  Pipeline B — Elite Report (6 stages, canonical)  │  │
│   │  EliteLoader → PhaseOrganizer → CrossRefBuilder   │  │
│   │  → PredictiveEngine → ChapterComposer →           │  │
│   │  Visualizer + Renderer → Persist (triple-tier)    │  │
│   └───────────────────────────────────────────────────┘  │
│                                                           │
│   ┌──────────┐ ┌──────────┐ ┌──────────────┐            │
│   │Hunter    │ │Auditor   │ │Architect     │            │
│   │RSS+OONI  │ │FieldVali │ │Agent (Opus 4│            │
│   │24/7      │ │+Patterns │ │.7 autónomo)  │            │
│   └──────────┘ └──────────┘ └──────────────┘            │
│                                                           │
│   i18n: 180+ keys (es/en/pt) + section_titles.py         │
│   Core: data_loaders, catalog, schema, vdem_static       │
└────────────┬───────────────────┬─────────────────────────┘
             │                   │
        ┌────▼────────────┐ ┌────▼──────────┐
        │ SQLite triple   │ │ RAG (ChromaDB)│  ← keyword fallback
        │ tier (FS+TEXT+  │ │ 14 legal docs │
        │ PDF on-demand)  │ │ + sentence-tr │
        └─────────────────┘ └───────────────┘
             │
        ┌────▼──────────────────┐
        │ Data layers:          │
        │ V-Dem v16 (1789-2025) │
        │ FH FIW, PEI 10, RSF   │
        │ OONI API (real-time)  │
        │ Hunter RSS Perú (4h)  │
        └───────────────────────┘
```

### Pipeline A — LangGraph (4 agents, original)

**State**: `PEIRSState` (TypedDict) passes immutably through 4 nodes
- **run_id**: UUID for tracking
- **country_code**: ISO 3166-1 alpha-3
- **context_data**: V-Dem v16 indices + FH + PEI + RSF normalized 0–1
- **political_data**: Coalition, polarization, media bias scores
- **legal_analysis**: Violations per international instrument
- **risk_score**: 0–100 aggregated risk
- **risk_level**: `critical|high|moderate|low`
- **report_chapters**: Dict of markdown sections
- **agent_logs**: Audit trail of all operations
- **trace_log**: Chronological operations log

**Agent Nodes:**

1. **Ingestion Agent** (OSINT loader)
   - Loads V-Dem v16 (~440MB CSV with 21 monitored indicators) or static fallback (`vdem_static.py`, 38 countries × 21 indicators × 1985-2025)
   - Loads Freedom House FIW 2013-2025, RSF 2025, PEI 10.0
   - Normalizes indices to 0–1 scale
   - Integrates real-time OONI API for internet censorship

2. **Political Analyst Agent**
   - Evaluates media independence (V-Dem `v2mebias` + RSF)
   - Calculates polarization, opposition barriers
   - References Claude Sonnet 4.6 for contextual analysis
   - Rule-based heuristics fallback if LLM unavailable

3. **Legal Compliance Agent**
   - RAG query: matches country/issue to international instruments
   - Checks violations: ICCPR, CADH, CDI, CEDAW, OSCE/ODIHR, UNDRIP, jurisprudence CIDH, Constitución Perú 1993, LOE, LOP, Resoluciones JNE (14 instruments total)
   - Uses ChromaDB semantic search OR keyword fallback
   - Returns `applicable_instruments` dict + violation_count

4. **Report Generator Agent**
   - Assembles markdown report (3000+ words)
   - Generates executive summary via Claude
   - Stores report in SQLite + JSON files in `/data/reports/{run_id}.json`

### Pipeline B — Elite Report (6 stages, canonical product)

Located in `backend/agents/elite_report/`. Produces the institutional-grade
12-chapter + 3-appendix report.

1. **EliteLoader** (`loaders/elite_loader.py`) — parallel evidence loading: Hunter entries, dispatched alerts, country-filtered constitutionalist RAG corpus, V-Dem v16 + FH + PEI + RSF historical series. Cache TTL 1h.

2. **PhaseOrganizer** (`organizers/phase_organizer.py`) — groups Hunter findings into 9 electoral cycle phases by date and electoral calendar.

3. **CrossReferenceBuilder** (`organizers/cross_reference.py`) — links high/critical findings to normative-framework articles via curated 14-category mapping.

4. **PredictiveEngine** (`predictive/engine.py`) — hybrid engine: deterministic rules + Claude Sonnet 4.6 producing 6 probabilistic scenarios with confidence bands + early-warning meter.

5. **ChapterComposer** (`composer/chapter_composer.py`) — 12 specialized prompts with Anthropic prompt caching, concurrency limit 4. Each chapter generated with shared context + chapter-specific data. LANGUAGE_RULE enforces output language (es/en/pt).

6. **Visualizer + Renderer** — 21 server-side SVG visualizations (`visualizer/renderers.py` + `renderers_5b.py`); HTML+CSS @page A4 + @media print (`renderer/html_renderer.py`); SQLite triple-tier persistence (filesystem + TEXT columns + PDF on-demand).

**Supporting Agents:**

- **Agent 5 — FieldDataValidator** (`modules/field_validator.py`): Validates observation entries, detects duplicates, calculates quality scores
- **Agent 7 — AlertDispatch** (`integrations/alerts.py`): Sends alerts to Slack/webhooks/SMTP based on risk level
- **Expert Architect Agent** (`agents/architect.py`): Meta-agent that audits system quality, proposes structural improvements (runs periodically, non-blocking)

### Module Organization

```text
backend/agents/                    # Agents + pipeline orchestration
  ├── pipeline.py                  # LangGraph pipeline original
  ├── architect.py                 # Architect Agent (Opus 4.7 autónomo via claude-agent-sdk)
  ├── elite_report/                # Elite Report 6-stage pipeline
  │   ├── elite_report.py          # Orchestrator (PEIRSEliteReport)
  │   ├── i18n.py                  # 180+ keys for chrome trilingüe (es/en/pt)
  │   ├── section_titles.py        # 50 entries — subchapter title translation
  │   ├── models.py                # Pydantic models (FindingRef, ForecastScenario, etc.)
  │   ├── loaders/                 # EliteLoader (parallel evidence)
  │   ├── organizers/              # PhaseOrganizer + CrossReferenceBuilder
  │   ├── predictive/              # PredictiveEngine + scenarios.py templates
  │   ├── composer/                # ChapterComposer + 13 prompts cap_NN.md
  │   ├── visualizer/              # 21 SVG renderers + dispatch
  │   └── renderer/                # html_renderer.py (cover, footer, TOC, anexos)
  └── report_designer/              # ReportDesigner sub-agent (4 audiencias)
backend/modules/                    # Data loaders, validation, analysis
  ├── config.py                    # Centralized env vars + constants (~50 vars). VDEM_VERSION, etc.
  ├── data_loaders.py              # V-Dem v16, FH, RSF, PEI CSV loaders
  ├── vdem_static.py               # Static V-Dem fallback (38 países × 21 indicators × 1985-2025, 618KB)
  ├── catalog.py                   # Country metadata (38 countries)
  ├── field_validator.py           # Entry quality + pattern detection
  ├── fraud_hate_analysis.py       # Pattern clustering
  └── peru_data.py                 # Peru 2026-specific data (forces, scenarios, regions)
backend/db/                         # SQLite triple-tier persistence
  ├── schema.py                    # 8 tables + elite_reports with md_content/html_content TEXT
  └── crud.py                      # Queries for entries, reports
backend/rag/                        # Legal knowledge base
  ├── corpus.py                    # 14 instruments + curated docs
  ├── indexer.py                   # ChromaDB init + embedding (in async background task)
  └── retriever.py                 # Semantic + keyword fallback queries
backend/integrations/               # External APIs
  ├── ooni.py                      # Censorship alerts (date-only since/until)
  ├── alerts.py                    # Slack/webhook/SMTP dispatch
  └── peru_sources.py              # Peru JNE, ONPE APIs
backend/tests/                      # 91 tests
  ├── test_elite_pipeline.py       # 9 Sprint 1 tests for Elite Report
  ├── test_e2e_pipeline.py         # End-to-end LangGraph pipeline
  ├── test_db.py                   # 30 CRUD tests
  ├── test_data_loaders.py         # V-Dem, FH, RSF, PEI loaders
  ├── test_field_validator.py      # 6 validation tests
  ├── test_config_and_modules.py   # 18 config tests
  └── conftest.py                  # Fixtures
scripts/                            # Operational scripts
  ├── backup.py                    # Backup completo prod (--targz para tar.gz)
  └── generate_vdem_static.py      # Regenerate vdem_static.py from full CSV
```

### Design Patterns

**Graceful Fallbacks** (error resilience)
- LLM unavailable? → Rule-based heuristics
- ChromaDB unavailable? → Keyword TF-IDF retrieval
- CSV data missing? → Mock data generators
- OONI API down? → Cached alerts from 1h window
- Result: System never silently fails; logs degradation mode

**Immutable State Machines** (via LangGraph TypedDict)
- Each agent node receives a copy of state, returns modified copy
- No shared mutable objects; deterministic replay from logs

**Centralized Config** (`modules/config.py`)
- 50+ env vars + constants defined once
- Env var fallbacks with sensible defaults
- Easy to override via `ANTHROPIC_API_KEY`, `VDEM_CSV_PATH`, etc.

**RAG Dual-Mode**
- Mode 1 (semantic): ChromaDB + SentenceTransformers (~90MB embeddings)
- Mode 2 (lexical): TF-IDF keyword matching on plain text (no deps)
- Unified `query_legal_context(query, category_filter)` interface

**Observer Protocol** (field observations)
- Entry model: category, severity, finding, location, observer_id, confidence
- Audit agent detects: flood attacks, single-observer concentration, unverified fraud allegations
- Validation agent: checks for duplicates, evidence quality, pattern clustering

---

## 3. TESTING STRATEGY

### Test Framework & Coverage

- **Framework**: `pytest` (separated in `requirements-dev.txt`, NOT installed on Railway)
- **Total Tests**: 91 unit + E2E + Elite Report integration tests
- **Coverage**: 100% passing (as of May 4, 2026)
- **Runtime**: ~8s for full suite
- **Test Command**: `python -m pytest backend/tests/ -v`
- **Sprint 1 additions**: `test_elite_pipeline.py` adds 9 integration tests for the Elite Report pipeline (VizKind dispatch, FindingRef shape, PredictiveEngine returns, attach_visualizations, render SVG, ChapterComposer no-LLM mode, `_format_vdem_emb`, disclosure presence)
- **Coverage Report**: `python -m pytest backend/tests/ --cov=backend --cov-report=html`

### Test File Organization
```
backend/tests/
├── conftest.py                    # Shared fixtures (tmp_db, sample_entry, sample_entries_batch)
├── test_config_and_modules.py     # Config loading, env var fallbacks
├── test_data_loaders.py           # V-Dem, FH, RSF, PEI CSV parsing
├── test_db.py                     # SQLite schema, CRUD operations
├── test_field_validator.py        # Entry validation, pattern detection
└── test_e2e_pipeline.py           # Full agent pipeline execution
```

### Fixtures (conftest.py)
- **tmp_db**: Temporary SQLite DB for test isolation
- **sample_entry**: Single observation entry (voter_intimidation example)
- **sample_entries_batch**: 6 entries for pattern tests
- Environment variables isolated per test (pytest automatic cleanup)

### Test Naming & Patterns
- `test_<function>_<scenario>()` — e.g., `test_validate_entry_detects_duplicates()`
- Setup: `@pytest.fixture` with `yield` for cleanup
- Use monkeypatch for env vars: `monkeypatch.setenv("ANTHROPIC_API_KEY", "mock-key")`
- Assertions: Standard `assert` statements

### Common Issues & Workarounds
- **Windows UTF-8 encoding**: Code at `app.py:~25` reconfigures stdout/stderr to avoid `cp1252` crashes with emojis
- **CSV path issues**: Tests use relative paths; conftest sets `PEIRS_DB_PATH` env var
- **Mock LLM responses**: Agents don't fail if `ANTHROPIC_API_KEY` missing; tests use mocked responses

---

## 4. KEY TECH STACK CHOICES

### Backend: FastAPI + LangGraph + Claude
**Why FastAPI?**
- Type-safe with Pydantic (automatic validation + docs)
- Built-in OpenAPI/Swagger UI at `/docs`
- Async-first → efficient under concurrent requests
- CORS middleware built-in
- Deployment: Single Python process via Uvicorn

**Why LangGraph?**
- Manages agent orchestration as DAG (directed acyclic graph)
- State threading: immutable state passing between nodes
- Built-in error handling + retry logic
- Integrates natively with LangChain's LLM abstractions
- Alternative considered: Apache Airflow (too heavyweight for 5 nodes)

**Why Claude (Anthropic)?**
- Model: Claude Sonnet for narratives + Claude Opus for meta-analysis
- Extended thinking capability (for Expert Architect Agent)
- Better instruction-following than alternatives
- Cost-efficient vs GPT-4 for legal document analysis
- Fallback: System never depends solely on LLM; rules-based heuristics as backup

**Why SQLite + WAL?**
- No external DB server required; single `democracia.db` file
- WAL (Write-Ahead Logging) mode: safe concurrent reads + writes
- Foreign keys enabled: referential integrity for observation entries
- Sufficient for 38-country analysis + field observation storage
- Limitation: Not suitable for >10k concurrent connections (fine for this use case)

### Frontend: React 19 + Vite 7 + Recharts
**Why React 19?**
- JSX syntax for component composition
- Hooks ecosystem (useState, useContext)
- Fast virtual DOM diffing
- Large community library ecosystem

**Why Vite 7?**
- 10–100x faster dev server than Webpack (instant HMR)
- Native ES6 module bundling
- Minimal config: `vite.config.js` just plugins + server settings
- Production build: Optimized tree-shaking, code splitting
- Works with external CSS imports (Recharts)

**Why NOT Next.js?**
- Next.js adds SSR complexity; this is pure client-side SPA
- Vite + React is simpler, lighter, faster for dashboard use case

**Why Recharts?**
- Composable React components for charts (LineChart, BarChart, PieChart)
- Built for Recharts for accessibility (aria labels)
- Lightweight (~50KB gzipped)
- Alternatives (D3, Chart.js) require more wrapper code

### Data Pipeline: Pandas + ChromaDB + sentence-transformers
**Why Pandas?**
- Standard for tabular data (V-Dem, FH CSVs)
- Fast indexing: `df[(df["country"] == code) & (df["year"] == year)]`
- Easy normalization: vectorized operations

**Why ChromaDB + sentence-transformers?**
- ChromaDB: Local vector DB, serverless, ~5MB overhead
- sentence-transformers: Pre-trained embeddings (~90MB model) for semantic search
- Fallback to keyword TF-IDF if ChromaDB missing (graceful degradation)
- Learning curve: Minimal; simple `collection.query()` interface

**Why not Pinecone or Weaviate?**
- Requires external service (adds latency + cost)
- DEMOCRAC.IA philosophy: minimize external dependencies
- Local-first evaluation: Corpus doesn't change frequently, no sync overhead

### Configuration Management: Environment Variables + Python Module
- **modules/config.py**: Centralized 50+ constants
  - LLM models: `LLM_MODEL`, `LLM_TEMPERATURE`
  - Data paths: `VDEM_CSV_PATH`, `FH_CSV_PATH`, etc. (with defaults)
  - API keys: `ANTHROPIC_API_KEY` (optional fallback)
  - Observer auth: `OBSERVER_API_KEYS` (comma-separated)
- Advantages: Single source of truth, easy to override via env vars, no config file parsing needed

---

## 5. COMMON DEVELOPMENT ISSUES

### Known Issues & Solutions

**Issue 1: Node.js Not in PATH (Frontend)**
- **Symptom**: `npm: El término 'npm' no se reconoce como nombre de un cmdlet`
- **Cause**: Windows system PATH doesn't include Node.js binary directory
- **Solution**: 
  - Install Node.js 18+ from https://nodejs.org/
  - Close VS Code, reopen (PATH updates)
  - Verify: `node --version` and `npm --version` in terminal
  - Restart Vite dev server

**Issue 2: Python UTF-8 Encoding Crashes (Windows)**
- **Symptom**: `UnicodeEncodeError` when agents output reports with emojis
- **Cause**: Windows default codepage is `cp1252`, not UTF-8
- **Solution**: Code at `app.py:20–25` already handles this:
  ```python
  if hasattr(sys.stdout, "reconfigure"):
      sys.stdout.reconfigure(encoding="utf-8", errors="replace")
  ```
  If issues persist, set env var: `set PYTHONIOENCODING=utf-8`

**Issue 3: CSV Data Files Missing (V-Dem, FH, etc.)**
- **Symptom**: `[V-Dem] AVISO: CSV no encontrado. Usando datos mock.`
- **Cause**: Data files >100MB not in `data/` directory (excluded from git)
- **Solution**:
  - For local dev: Download datasets manually (see `docs/architecture_2026_v1.4.md`)
  - For production (Railway): Upload via Railway volume (see `docs/deploy_guide.md`)
  - System auto-generates mock data; all tests pass but results are less accurate

**Issue 4: ANTHROPIC_API_KEY Missing**
- **Symptom**: Reports generated but Claude narratives skipped
- **Cause**: Env var not set
- **Solution**:
  - Set `ANTHROPIC_API_KEY="sk-ant-..."` in terminal or `.env` file
  - dotenv auto-loads from `.env` at `app.py:26–28`
  - Fallback: System uses rule-based summary instead of LLM text

**Issue 5: Port Conflicts (8000, 5173)**
- **Symptom**: `Address already in use` when starting backend/frontend
- **Cause**: Previous instance still running or another process on port
- **Solution**:
  - Backend: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr 8000` (Windows)
  - Frontend: Change in `vite.config.js`: `server: { port: 5174 }`
  - Or kill process: `kill -9 <PID>` or `taskkill /PID <PID>`

**Issue 6: ChromaDB Index Stale**
- **Symptom**: RAG queries return outdated legal documents
- **Cause**: Corpus updated but ChromaDB not re-indexed
- **Solution**: Delete `data/rag_index/` directory; system reinitializes on next startup
  - Or set env: `RAG_FORCE_REINDEX=1`

**Issue 7: SQLite Database Locked**
- **Symptom**: `sqlite3.OperationalError: database is locked`
- **Cause**: Multiple processes writing to DB simultaneously
- **Solution**: 
  - DB uses WAL mode with 10-sec timeout (built-in)
  - If persists: Delete `democracia.db-wal` and `democracia.db-shm` files
  - Restart backend

**Issue 8: Memory Pressure (V-Dem DataFrame)**
- **Symptom**: Backend slow/crashes with `MemoryError`
- **Cause**: `VDEM_DF` (383K rows × 24 cols) loaded into memory at startup
- **Solution**:
  - Consider lazy-loading if >50GB RAM unavailable
  - Current design: ~50MB memory footprint (acceptable)
  - For >1000 concurrent users: Move to indexed database (PostgreSQL)

---

## 6. CODE STYLE

### Python Style Guide
- **Framework**: Follows PEP 8 with some pragmatism
- **Line length**: 88 characters (implicit, not strict)
- **Type hints**: Used throughout (`from __future__ import annotations`)
  - All function signatures include return types
  - TypedDict for state objects (e.g., `PEIRSState`)
  - Optional types for nullable returns
  
**Example:**
```python
def get_vdem_country(
    df: Optional[pd.DataFrame],
    country_code: str,
    year: int = VDEM_LAST_YEAR,
) -> Optional[Dict]:
    ...
```

**Imports Organization:**
```python
# 1. Future imports
from __future__ import annotations

# 2. Standard library (datetime, json, sys, etc.)
import os
import sys
from typing import Dict, List, Optional

# 3. Third-party (pandas, langchain, etc.)
import pandas as pd
from langchain_anthropic import ChatAnthropic

# 4. Local imports
from modules.config import VDEM_CSV_PATH
from agents.pipeline import PEIRSState
```

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `AuditAgent`, `ElectionRiskState`)
- Functions: `snake_case` (e.g., `get_vdem_country()`, `run_ingestion()`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `VDEM_CSV_PATH`, `LLM_TEMPERATURE`)
- Private functions: `_leading_underscore()` (e.g., `_rag_legal()`, `_tokenize()`)
- Protected/internal: Prefixed with underscore (e.g., `_SYSTEM_PROMPT`)

**Docstrings:**
- Module level: Triple-quoted summary at top
- Functions: Triple-quoted docstring immediately after `def`
- Format: Brief description, optional args/returns section
```python
def validate_entry(entry, existing):
    """
    Valida un hallazgo de observación.
    
    Args:
        entry: Dict con fields de hallazgo
        existing: List de hallazgos previos
    
    Returns:
        SimpleNamespace con validated, warnings, errors, duplicate_of, quality_score
    """
```

**Error Handling:**
- Use specific exceptions (`ValueError`, `ImportError`, `KeyError`)
- Graceful fallbacks via try-except (See "Graceful Fallbacks" in Architecture)
- Log errors and continue; don't crash silently
- Example: `try: from rag import query_legal_context; except ImportError: def query_legal_context(*a, **kw): return []`

**Comments:**
- Spanish preferred for domain-specific comments
- `# ──────────────────────` separators for major sections
- `# ── Subsection Name ───` for logical grouping
- Inline comments rare; code should be self-documenting

### JavaScript/ESLint Configuration
- **ESLint config**: `frontend/eslint.config.js` (ES2020 + React)
- **Rules enforced**:
  - `no-unused-vars`: Error if variable defined but not used (varsIgnorePattern: `^[A-Z_]` for constants)
  - React Hooks plugin: Ensures Hook dependency arrays correct
  - React Refresh plugin: Fast refresh compatibility
- **Run linting**: `npm run lint` (no autofix configured)
- **No Prettier**: Manual formatting expected (pragmatic for small team)

**Naming Conventions (JavaScript):**
- Components: `PascalCase` (e.g., `ElectionRiskChart.jsx`)
- Variables/functions: `camelCase` (e.g., `riskScore`, `handleAnalysis()`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
- Private methods: `_leadingUnderscore()`

**Import/Export:**
- ES6 modules: `import ... from ...` (not CommonJS `require`)
- Default exports for components, named exports for utilities
```javascript
// Good
export default function ElectionDashboard() { ... }
export const formatRiskScore = (score) => { ... }
```

**React Patterns:**
- Functional components + Hooks (not class components)
- Props destructuring in function signatures
- useEffect for data fetching, cleanup in return function
- Custom hooks for shared logic

---

## 7. DOCUMENTATION

### Architecture Documents
- **[docs/architecture_2026_v1.4.md](docs/architecture_2026_v1.4.md)** ← MOST IMPORTANT
  - System vision & principles (trazabilidad total, fallback gracioso, mejora continua)
  - Agent pipeline details (5 nodes + 2 supporting agents)
  - Tech stack rationale (FastAPI, LangGraph, Claude)
  - Database schema (8 tables)
  - Testing strategy
  - Deployment topology

- **[docs/deploy_guide.md](docs/deploy_guide.md)**
  - Production deployment to Railway (backend) + Netlify (frontend)
  - Environment variable setup
  - Volume mounting for large datasets (V-Dem)
  - DNS configuration for custom domain
  - Estimated costs

- **[QUICKSTART.md](QUICKSTART.md)** ← Entry point
  - Quick status table (backend ✅, frontend ⚠️)
  - 3 ways to run (PowerShell script, manual terminals, batch file)
  - Testing without frontend
  - Available countries + data sources

- **[STATUS_REPORT.md](STATUS_REPORT.md)** ← Current diagnostics
  - Python version + package list
  - Test results (82/82 passing)
  - API endpoints + live status
  - Data sources integration table
  - Frontend blockers

- **[backend/README.md](backend/README.md)**
  - API endpoints reference
  - Example curl requests
  - Agent architecture diagram
  - Staging vs production differences

### Inline Documentation
- **Agent modules** (`agents/architect.py`, `agents/auditor.py`, etc.)
  - Module docstring explains function
  - Class docstrings for major classes
  - Method docstrings for public methods
  - Comments for complex logic (especially pattern detection)

- **modules/config.py**
  - Each config section has `# ── Section Name ───` header
  - Comments explain why each const (e.g., "V-Dem v16 disponible desde marzo 2026")

- **Data schema** (`db/schema.py`)
  - Full DDL with comments on each column
  - Foreign key relationships documented
  - Default values explained

### Decision Records (Implicit)
Not formally documented as ADRs, but architectural decisions evident in:
- Choice of LangGraph in `agents/pipeline.py` (DAG orchestration)
- Graceful fallbacks in `rag/retriever.py` (keyword fallback if ChromaDB unavailable)
- SQLite WAL mode in `db/schema.py` (concurrent access)
- Immutable state pattern (PEIRSState TypedDict)

### What's Missing
- **API specification**: No OpenAPI/Swagger export (FastAPI auto-generates at `/docs`)
- **ER diagram**: Tables documented in schema.py but no visual diagram
- **Runbook**: No on-call operations guide for production issues
- **Contributing guide**: No CONTRIBUTING.md for external contributors

---

## 8. CRITICAL PATHS FOR AI AGENTS

### Reading Order for Understanding the System
1. Start: `QUICKSTART.md` — Get running, understand status
2. Architecture: `docs/architecture_2026_v1.4.md` — Cognitive model of 5 agents + LangGraph
3. Code entry point: `backend/app.py` lines 1–150 (imports, setup), then 4000–4100 (FastAPI routes)
4. Agent pipeline: `agents/pipeline.py` → `agents/nodes.py` → individual agent implementations
5. Data loaders: `modules/data_loaders.py` (CSV handling, normalization)
6. Tests: `backend/tests/test_e2e_pipeline.py` (end-to-end flow)

### Common Operating Scenarios

**Scenario 1: Add a new data source (e.g., IRI polling data)**
1. Add CSV path to `modules/config.py` as `IRI_CSV_PATH`
2. Create `load_iri_data()` → `get_iri_country()` functions in `modules/data_loaders.py`
3. Call in Ingestion Agent (`app.py:~1170`) to populate `context_data`
4. Update test: `backend/tests/test_data_loaders.py`

**Scenario 2: Add a new validation rule**
1. Edit `modules/field_validator.py` → add logic to `detect_patterns()`
2. Update `AuditAgent.audit_session()` in `agents/auditor.py` if it affects audit
3. Add test case to `backend/tests/test_field_validator.py`

**Scenario 3: Modify agent behavior (e.g., risk scoring)**
1. Find agent in `app.py` (search `def <agent_name>_agent`)
2. Modify score calculation logic
3. Update any downstream agents that consume the score (trace through `state` dict)
4. Test: `python -m pytest backend/tests/test_e2e_pipeline.py::test_full_workflow -v`

**Scenario 4: Deploy to production**
1. Ensure all tests pass: `python -m pytest -q`
2. Update `VDEM_VERSION`, `FH_LAST_EDITION`, etc. in `modules/config.py`
3. Follow `docs/deploy_guide.md`: Push to GitHub → Railway detects `railway.toml`
4. Upload datasets via Railway CLI (see deploy guide)
5. Verify: `curl https://democracia-peirs-production.up.railway.app/api/health`

**Scenario 5: Debug a failing test**
1. Run: `python -m pytest backend/tests/test_name.py::test_function -v -s` (capture output)
2. Check conftest fixtures (`tmp_db`, `sample_entry`) — are they correct?
3. Look for monkeypatch issues (env var isolation)
4. Check import paths (tests add `sys.path` in conftest)

### Key Files by Task
| Task | File | Lines |
|------|------|-------|
| Understand data flow | `agents/pipeline.py` | 50–120 |
| Add API endpoint | `backend/app.py` | 4000–4150 |
| Add validation | `modules/field_validator.py` | 1–200 |
| Fix data loading | `modules/data_loaders.py` | 1–150 |
| Configure deployment | `railway.toml`, `netlify.toml` | Entire file |
| Debug tests | `backend/tests/conftest.py` | Entire file |
| Understand RAG | `rag/retriever.py` | 1–150 |
| Add observer alert | `integrations/alerts.py` | 1–100 |

---

## 9. PERFORMANCE & SCALING CONSIDERATIONS

### Bottlenecks (Current)
1. **V-Dem DataFrame loading** (~2 sec startup, ~50MB memory)
   - Loads all 383K rows on startup
   - Queries via pandas indexing (fast after load)
   - Scaling: For >100 countries, consider lazy-loading or database

2. **RAG semantic search** (~500ms per query with ChromaDB)
   - Depends on sentence-transformers embedding (~90MB on first use)
   - Fallback to keyword search is faster (~50ms)
   - Corpus size: 60 documents (small enough for in-memory)

3. **Claude API calls** (~2–5 sec per request)
   - Political Analyst: 1 call
   - Dictamen Agent: 1 call
   - Report Generator: 1 call
   - Total: ~10–15 seconds of LLM latency per analysis

4. **Frontend Recharts rendering** (10+ charts → 100ms re-render)
   - One-time cost; not per-interaction
   - Could optimize with `React.memo()` if slow

### Scaling Roadmap (>10k concurrent users)
- Move to PostgreSQL (replaces SQLite)
- Add Redis for observation session caching
- Batch LLM requests (use Claude Batch API)
- Cache RAG queries per country/topic
- Frontend: Consider Next.js ISR for static report pages

### Memory Footprint
- Backend: ~150MB (Python runtime + V-Dem DF + ChromaDB model)
- Frontend: ~50MB (Node modules, not shipped to browser)
- Browser (Runtime JS): ~5MB

---

## 10. QUICK REFERENCE: ENVIRONMENT VARIABLES

| Variable | Default | Purpose |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | (empty) | Claude API; system degrades gracefully if missing |
| `OBSERVER_API_KEYS` | `democracia-obs-dev-2026` | Comma-separated API keys for observer endpoints |
| `VDEM_CSV_PATH` | `../data/V-Dem-CY-Full+Others-v15.csv` | Path to V-Dem v15 dataset |
| `FH_CSV_PATH` | `../data/All_data_FIW_2013-2025 - Index.csv` | Freedom House ratings |
| `RSF_CSV_PATH` | `../data/RSF/2025 - 2025.csv` | Press Freedom Index |
| `PEI_CSV_PATH` | `../data/PEI/PEI_10 Election External.csv` | Electoral Integrity Project |
| `VDEM_LAST_YEAR` | `2024` | Last year in V-Dem for normalization |
| `VDEM_VERSION` | `v15` | Version tag for citations |
| `PEIRS_DB_PATH` | `../data/democracia.db` | SQLite database file |
| `RAG_FORCE_REINDEX` | (not set) | Set to `1` to force RAG corpus re-indexing |
| `ALLOWED_ORIGINS` | `*` | CORS origins; set in production |

---

## 11. TESTING QUICK START

```bash
# Run all tests
python -m pytest backend/tests/ -v

# Run specific test file
python -m pytest backend/tests/test_e2e_pipeline.py -v

# Run with coverage
python -m pytest backend/tests/ --cov=backend --cov-report=html

# Run single test
python -m pytest backend/tests/test_field_validator.py::test_detect_patterns -v

# Show print statements / debugging output
python -m pytest backend/tests/ -v -s

# Stop at first failure
python -m pytest backend/tests/ -x

# Run last 5 failures
python -m pytest backend/tests/ --lf
```

---

## 12. DEPLOYMENT QUICK START

```bash
# Local dev
./arrange_all.ps1  # PowerShell (Windows recommended)
# OR
cd backend && python -m uvicorn app:app --reload --port 8000  # Terminal 1
cd frontend && npm run dev                                  # Terminal 2

# Production (Railway / Netlify)
# 1. Push to GitHub
# 2. Railway auto-deploys backend (detects railway.toml)
# 3. Netlify auto-deploys frontend (detects netlify.toml)
# 4. Upload datasets to Railway volume (see deploy_guide.md)

# Health check
curl http://localhost:8000/api/health
```

---

## Summary

**DEMOCRAC.IA is a LangGraph-orchestrated electoral integrity analysis system** combining:
- **5-agent pipeline** (Ingestion → Political → Legal → Dictamen → Reporting)
- **Multiple data sources** (V-Dem, Freedom House, PEI, RSF, OONI)
- **Graceful degradation** (always returns a result, never fails silently)
- **Full traceability** (every finding has a source, timestamp, confidence)
- **Type-safe Python + React frontend** with modern tooling (FastAPI, Vite, Recharts)

For AI agents extending this codebase:
1. Understand the LangGraph DAG flow first
2. Follow the immutable state pattern
3. Add graceful fallbacks for new services
4. Write tests before code (pytest fixtures ready)
5. Document configuration in `modules/config.py`
6. Check existing agents for patterns before implementing new ones
