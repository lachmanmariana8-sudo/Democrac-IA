---
title: DEMOCRAC.IA / PEIRS — Copilot Instructions
description: Workspace conventions, architecture patterns, and AI-agent productivity guide
version: "1.0"
lastUpdated: "2026-04-04"
appliesTo: ["backend/**/*.py", "frontend/**/*.{jsx,js}", "tests/**/*.py"]
---

# DEMOCRAC.IA / PEIRS — Copilot Instructions

**Context:** Electoral integrity analysis system using LangGraph + FastAPI (backend), React (frontend).  
**Scope:** https://github.com/democracia-peirs (planned)  
**Status:** ✅ v0.4.0 production-ready backend, frontend in integration phase

---

## 🎯 Core Principles

1. **Think before coding** — Read relevant files (CODEBASE_ANALYSIS.md, architecture doc) before implementing changes.
2. **Token efficiency** — Be concise but thorough. Prefer editing to rewriting. Batch independent operations.
3. **Test-driven** — Run `pytest` before declaring done. 82/82 tests must pass.
4. **Link, don't embed** — Reference [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md), [docs/architecture_2026_v1.4.md](docs/architecture_2026_v1.4.md), [QUICKSTART.md](QUICKSTART.md) instead of repeating their content.
5. **Backend-first stability** — Backend API is the source of truth. Frontend is a dashboard layer.
6. **Data privacy** — No sensitive electoral data. Only public sources (V-Dem, Freedom House, PEI).

---

## 📋 Quick Reference

### Startup Commands

**Backend** (Python 3.14.3):
```powershell
cd d:\DemocracIA\backend
C:/Python314/python.exe -m uvicorn app:app --reload --port 8000
```

**Frontend** (Node.js 24.14.1):
```powershell
cd d:\DemocracIA\frontend
npm run dev  # http://localhost:5173
```

**Tests**:
```powershell
cd d:\DemocracIA
C:/Python314/python.exe -m pytest backend/tests/ -v
```

### Port Assignments
- **Backend API:** http://localhost:8000 (FastAPI + Uvicorn)
- **API Docs:** http://localhost:8000/docs (Swagger)
- **Frontend Dashboard:** http://localhost:5173 (React + Vite)

### Key Directories
| Path | Purpose |
|------|---------|
| `backend/app.py` | FastAPI main server, route definitions |
| `backend/agents/` | 5 LangGraph agents (architect, auditor, hunter, validator, alerts) |
| `backend/modules/` | Data loaders, validators, Peru 2026 electoral data |
| `backend/rag/` | Legal knowledge base (ChromaDB + keyword fallback) |
| `backend/db/` | SQLite schema, CRUD operations |
| `backend/tests/` | 82 pytest tests (100% passing) |
| `frontend/src/App.jsx` | Main React dashboard component |
| `data/` | Real datasets: V-Dem, Freedom House, PEI, RSF |
| `docs/` | Architecture decisions, deployment guides |

---

## 🏗️ Architecture Overview

### Backend: LangGraph DAG Pipeline
```
FastAPI Route (/api/analyze)
    ↓
FieldDataValidationAgent
    ├─→ Validate country code
    ├─→ Check entry quality
    └─→ Detect duplicates
    ↓
CountryArchitectAgent
    ├─→ Load V-Dem, Freedom House, PEI data
    ├─→ Query RAG legal base
    └─→ Frame analysis context
    ↓
AuditorAgent
    ├─→ Electoral integrity scoring
    ├─→ Governance evaluation
    └─→ Risk flagging
    ↓
HunterAgent
    ├─→ Pattern detection (fraud, interference)
    ├─→ Anomaly scoring
    └─→ Red-flag synthesis
    ↓
AlertDispatchAgent
    ├─→ Slack/webhook/email dispatch
    └─→ Data persistence
    ↓
Response: Markdown report + JSON trace
```

**Execution:** Synchronous DAG in LangGraph (state-threaded, immutable updates).  
**State:** `PEIRSState` TypedDict with 20+ fields (see `agents/pipeline.py`).  
**Type safety:** Pydantic models for all I/O, type hints throughout.

### Frontend: React Dashboard
- **Framework:** React 19.2 + Vite 7.3
- **Charting:** Recharts 3.8 (custom electoral distribution, timeline charts)
- **API Client:** Fetch-based (no axios)
- **Styling:** CSS inline + external (App.css)
- **Build:** `npm run build` → dist/ (production-optimized)

See [docs/architecture_2026_v1.4.md](docs/architecture_2026_v1.4.md) for detailed design decisions.

---

## 🔧 How to Add/Modify Code

### Adding a Data Source (Backend)

1. **Create loader** in `backend/modules/data_loaders.py`:
   ```python
   def load_newsource_data(filepath: str) -> Optional[pd.DataFrame]:
       """Load and validate new source."""
       try:
           df = pd.read_csv(filepath)
           return df if len(df) > 0 else None
       except Exception as e:
           print(f"[NEWSOURCE] Error: {e}")
           return None
   
   def get_newsource_country(df: Optional[pd.DataFrame], country_code: str) -> Optional[Dict]:
       """Extract country row, return structured dict."""
       if not df:
           return None
       # Filter, validate, return
   ```

2. **Write test** in `backend/tests/test_data_loaders.py`:
   ```python
   def test_load_newsource_returns_df_when_file_exists():
       df = load_newsource_data("path/to/file.csv")
       assert df is not None
   ```

3. **Integrate into agent node** (e.g., `agents/nodes.py`):
   ```python
   newsource_real = get_newsource_country(df, code)
   state.findings.append(create_trace(
       value=newsource_real or {},
       source_id=...,
       source_type=SOURCE_API if newsource_real else SOURCE_MOCK,
       ...
   ))
   ```

4. **Test end-to-end**: `pytest backend/tests/test_e2e_pipeline.py -v`

### Adding a Frontend Component

1. **Create component** in `frontend/src/components/` (or inline in App.jsx):
   ```jsx
   export function MyChart({ data }) {
       return (
           <div>
               {/* Use Recharts or custom render */}
           </div>
       );
   }
   ```

2. **Import and integrate** in `App.jsx`.

3. **Test with dev server**: `npm run dev` → http://localhost:5173

4. **Build for production**: `npm run build` (check bundle size warnings)

### Modifying an Agent

1. **Read agent file** (e.g., `backend/agents/hunter.py`) to understand current state transformations.
2. **Update node function** in `backend/agents/nodes.py` (where `invoke()` is called).
3. **Update state type** in `agents/pipeline.py` if adding new fields to `PEIRSState`.
4. **Test via**: 
   ```powershell
   C:/Python314/python.exe -m pytest backend/tests/test_e2e_pipeline.py::TestHunterAgentE2E -v
   ```

---

## 🧪 Testing Strategy

**Framework:** pytest (v9.0.2)  
**Coverage:** 82 tests across 5 modules (100% passing)  
**Execution:** ~5 seconds locally

### Test File Naming
- `test_config_and_modules.py` — Configuration, module imports, startup checks
- `test_data_loaders.py` — V-Dem, FH, PEI, RSF data loading
- `test_db.py` — SQLite CRUD, deduplication, alerts
- `test_e2e_pipeline.py` — Full LangGraph DAG, RAG retrieval, audit scoring
- `test_field_validator.py` — Entry validation, deduplication, pattern detection

### Running Tests
```powershell
# All tests
pytest backend/tests/ -v

# Specific module
pytest backend/tests/test_data_loaders.py -v

# Specific test
pytest backend/tests/test_field_validator.py::TestValidateEntry::test_valid_entry_passes -v

# With coverage
pytest backend/tests/ --cov=backend --cov-report=html
```

⚠️ **Rule:** Run `pytest` before declaring any backend work done. Tests must pass.

---

## 🔌 Integration Points

### Backend ↔ Frontend
- **API Base:** `http://localhost:8000`
- **CORS:** Enabled (FastAPI middleware in app.py)
- **Main endpoint:** `POST /api/analyze` → returns `{ report, trace, timestamp }`
- **Real-time:** No WebSockets. Poll `/api/report/{id}` if async needed.

### Backend ↔ Data
- **V-Dem:** `data/V-Dem-CY-Full+Others-v15.csv` (3.5MB, ~2000 rows)
- **Freedom House:** `data/All_data_FIW_2013-2025.csv` (scores 1973–2025)
- **PEI v10:** `data/PEI/PEI_10 Election External.csv` (expert ratings)
- **RSF:** `data/RSF/2025 - 2025.csv` (press freedom index)
- **Peru:** `backend/modules/peru_data.py` (2026 election data, 17 regions, political forces)

### Backend ↔ External APIs
- **OONI:** HTTP GET to detect internet censorship (read-only, cached)
- **Anthropic (Claude):** Optional, requires `ANTHROPIC_API_KEY` env var

See [CODEBASE_ANALYSIS.md § Integration Points](CODEBASE_ANALYSIS.md) for detailed headers, timeouts, error handling.

---

## 🚀 Deployment

### Development
```
Backend: uvicorn app:app --reload --port 8000
Frontend: npm run dev --port 5173
Database: db.sqlite3 (local, persistent)
```

### Production
- **Backend:** Railway/Vercel/Heroku (Procfile provided)
- **Frontend:** Netlify (netlify.toml configured)
- **Database:** SQLite with WAL mode (serverless-ready)
- **See:** [docs/deploy_guide.md](docs/deploy_guide.md)

---

## 📊 Common Development Scenarios

| Scenario | How-To | Files |
|----------|--------|-------|
| **Add electoral indicator** | Extend `PEIRSState`, add agent node, test | agents/*, backend/tests/test_e2e* |
| **Fix data loader bug** | Read loader, add test case, fix, retest | modules/data_loaders.py, tests/test_data_loaders.py |
| **Add dashboard chart** | Create component, integrate in App.jsx, npm run dev | frontend/src/App.jsx |
| **Debug LangGraph execution** | Check agent logs via `agent_log()` calls, trace output | agents/nodes.py, app.py |
| **Test with Peru data** | Pass `{"country_code": "PER"}` to `/api/analyze` | backend/modules/peru_data.py |
| **Fix Unicode/emoji issues** | Already handled (sys.stdout.reconfigure in app.py) | app.py:14–18 |
| **Update legal instruments** | Extend `modules/instruments.py`, reindex RAG | modules/instruments.py, rag/corpus.py |
| **Add validation rule** | Update `modules/field_validator.py`, add test | modules/field_validator.py, tests/test_field_validator.py |

---

## ⚠️ Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **Port 8000 in use** | "Address already in use" | `taskkill /PID <pid> /F` (find via `netstat -ano \| findstr :8000`) |
| **Node.js not in PATH** | "npm: command not found" | Download from https://nodejs.org/, install with "Add to PATH" |
| **CSV files missing** | No data in analysis | Copy CSV files to `data/` folder (or auto-mocks used) |
| **ChromaDB unavailable** | RAG queries fail | Keyword fallback always works; semantic requires `chromadb` + `sentence-transformers` (installed) |
| **Pydantic v1 deprecations** | Warnings in tests | Non-critical; use `from pydantic.v1` in legacy code |
| **LLM features disabled** | Analysis runs but no Claude scores | Set `ANTHROPIC_API_KEY` env var (optional) |

See [CODEBASE_ANALYSIS.md § Common Dev Issues](CODEBASE_ANALYSIS.md) for detailed troubleshooting.

---

## 📚 Documentation

**Read first:**
1. [QUICKSTART.md](QUICKSTART.md) — Get running in 5 minutes
2. [docs/architecture_2026_v1.4.md](docs/architecture_2026_v1.4.md) — Full system design
3. [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md) — Agent-focused productivity guide

**Reference:**
- [docs/whitepaper_2026_v2.md](docs/whitepaper_2026_v2.md) — PEIRS methodology
- [docs/deploy_guide.md](docs/deploy_guide.md) — Production deployment
- Backend inline docstrings (always current)
- [STATUS_REPORT.md](STATUS_REPORT.md) — Real-time system status (auto-generated)

---

## 🔐 Environment Variables

### Required
- None (system runs with mocks by default)

### Optional
```bash
ANTHROPIC_API_KEY=sk-ant-...          # Claude API for LLM features
LLM_MODEL=claude-3-5-sonnet-20241022  # Model selection
LLM_TEMPERATURE=0.3                   # Reasoning vs. creativity
OBSERVER_API_KEYS=key1,key2           # Observer network authentication
```

### Alert Channels (if configured)
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=...
SMTP_PASSWORD=...
```

See [backend/modules/config.py](backend/modules/config.py) for defaults and validation.

---

## ✅ AI Agent Checklist

Before implementing a task, an AI agent should:

- [ ] Read [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md) for architectural context
- [ ] Identify affected test files and existing tests
- [ ] Check if backend/frontend/both are impacted
- [ ] Review related agent nodes or data loaders
- [ ] Write/update tests **before** declaring done
- [ ] Run full test suite: `pytest backend/tests/ -v`
- [ ] If frontend: verify `npm run build` succeeds (check bundle size)
- [ ] Test end-to-end with Peru data if possible
- [ ] Update relevant docs if behavior changes
- [ ] Leave a `# TODO` or `# FIXME` comment if partial/incomplete

---

## 🤝 Collaboration

**Style guide:** [CODEBASE_ANALYSIS.md § Code Style](CODEBASE_ANALYSIS.md)  
**PR process:** (GitHub workflow TBD)  
**Issues/bugs:** Use GitHub Issues with labels: `bug`, `feature`, `docs`, `backend`, `frontend`  

---

**Last updated:** 2026-04-04  
**Maintained by:** DEMOCRAC.IA Dev Team  
**Questions?** See [STATUS_REPORT.md](STATUS_REPORT.md) or run diagnostics:  
```powershell
C:/Python314/python.exe backend/agents/architect.py --audit
```
