# 🇵🇪 DEMOCRAC.IA / PEIRS — Quick Start Guide

**Democracia PEIRS v0.4.0** — Predictive Electoral Integrity & Risk System

---

## ⚡ Quick Status (April 4, 2026)

| Component | Status | Notes |
|-----------|--------|-------|
| **Backend** | ✅ OPERATIONAL | Python 3.14.3, FastAPI, 82/82 tests passing |
| **API Server** | ✅ LIVE | Running on `http://localhost:8000` |
| **Data Sources** | ✅ INTEGRATED | V-Dem, Freedom House, PEI v10, OONI, Peru 2026 |
| **Database** | ✅ READY | SQLite with full schema |
| **Frontend** | ⚠️ BLOCKED | Node.js missing from PATH |
| **Dashboard** | ❌ CANNOT START | Waiting for Node.js installation |

See [STATUS_REPORT.md](STATUS_REPORT.md) for full diagnostics.

---

## 🚀 How to Run

### Step 1: Install Node.js (if not already installed)

```bash
# Download and install from:
https://nodejs.org/  (version 18 or later)

# Verify installation:
node --version
npm --version
```

### Step 2: Start the Full Stack

**Option A: PowerShell (Recommended)**
```powershell
# From the d:\DemocracIA directory:
.\arrange_all.ps1
```

**Option B: Command Prompt (Windows)**
```cmd
# From the d:\DemocracIA directory:
arrange_all.bat
```

**Option C: Manual (Two terminals)**

Terminal 1 — Backend:
```powershell
cd d:\DemocracIA\backend
C:/Python314/python.exe -m uvicorn app:app --reload --port 8000
```

Terminal 2 — Frontend:
```powershell
cd d:\DemocracIA\frontend
npm run dev
```

### Step 3: Open Dashboard

Once both servers are running:
- **Backend:** http://localhost:8000
- **Dashboard:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs (Swagger)

---

## 📊 What's Ready to Analyze

### Supported Countries (38 available)
- **Peru 2026** ← Primary focus
- Argentina, Bolivia, Brazil, Chile, Colombia, Costa Rica
- Mexico, Panama, Paraguay, Uruguay, Venezuela
- And 26 more (see `/api/countries`)

### Available Analysis

```bash
# Health check
curl http://localhost:8000/api/health

# List available countries
curl http://localhost:8000/api/countries

# Run full electoral integrity analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"country_code": "PER", "election_date": "2026-04-12"}'
```

---

## 📈 Data Sources Integrated

| Source | Dataset | Last Updated | Coverage |
|--------|---------|--------------|----------|
| **V-Dem** | V-Dem v15 Full | 2025 | 179 countries, 1789–2024 |
| **Freedom House** | FIW Ratings 2013–2025 | 2025 | Countries + territories |
| **PEI** | Perceptions of Electoral Integrity v10 | 2023 | 150+ elections |
| **RSF** | Press Freedom Index 2025 | 2025 | 180 countries |
| **OONI** | Internet Censorship Detection | Daily | Real-time (API) |
| **Peru Specifics** | Electoral data 2026 | 2026 | Peru 2026 elections |

---

## 🔧 Testing Backend (Without Frontend)

```powershell
# Run all 82 tests
cd d:\DemocracIA
C:/Python314/python.exe -m pytest backend/tests/ -v

# Run specific test module
C:/Python314/python.exe -m pytest backend/tests/test_data_loaders.py -v

# Generate test coverage
C:/Python314/python.exe -m pytest backend/tests/ --cov=backend --cov-report=html
```

---

## 📁 Project Structure

```
d:\DemocracIA\
├── backend/               ← FastAPI + LangGraph agents ✅
│   ├── app.py             ← Main server
│   ├── agents/            ← 4 AI agents for analysis
│   ├── modules/           ← Data loaders, validators
│   ├── db/                ← SQLite schema & CRUD
│   ├── rag/               ← Legal knowledge base
│   ├── tests/             ← 82 unit + E2E tests
│   └── requirements.txt   ← Python dependencies
│
├── frontend/              ← React + Vite ⚠️
│   ├── src/
│   ├── App.jsx            ← Main dashboard
│   ├── package.json       ← npm dependencies
│   └── vite.config.js
│
├── data/                  ← Real datasets
│   ├── V-Dem-CY-Full+Others-v15.csv
│   ├── All_data_FIW_2013-2025.csv
│   ├── PEI/               ← Electoral integrity project
│   └── RSF/               ← Press freedom index
│
├── STATUS_REPORT.md       ← Full diagnostics
├── arrange_all.ps1        ← PowerShell startup script
├── arrange_all.bat        ← Command prompt startup script
└── this file
```

---

## 🎯 What's Running Right Now

### ✅ Backend Server (Port 8000)

```
[FastAPI + Uvicorn]
├─ /api/health              → System status
├─ /api/countries           → Available countries
├─ /api/analyze             → Run analysis pipeline
├─ /api/report/{id}         → Get completed report
├─ /docs                    → Swagger UI
└─ /openapi.json           → OpenAPI spec
```

**4-Agent Pipeline** (LangGraph):
1. **Architect Agent** — Frame analysis, validate inputs
2. **Auditor Agent** — Electoral integrity checks
3. **Hunter Agent** — Pattern detection, risk scoring
4. **Alert Agent** — Dispatch findings

**Data Connections:**
- V-Dem, Freedom House, PEI datasets
- OONI real-time API (censorship alerts)
- Peru-specific electoral data
- RAG legal knowledge base (14 instruments)
- SQLite database (analysis logs)

### ⚠️ Frontend Server (Port 5173)

Currently **NOT RUNNING** — needs Node.js. Once installed:

```
[React 19 + Vite]
├─ Dashboard (country selection)
├─ Analysis charts (Recharts)
├─ Real-time data streaming
├─ Report export (Markdown/JSON)
└─ Live backend connection
```

---

## ❓ Troubleshooting

### "npm: command not found"
**Solution:** Node.js is not in your system PATH
1. Uninstall Node.js
2. Download fresh from https://nodejs.org/
3. Install with "Add to PATH" option checked
4. Restart terminal/PowerShell
5. Verify: `npm --version`

### "Backend on port 8000 already in use"
```powershell
# Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "Cannot find module 'anthropic'" 
```powershell
# Reinstall Python dependencies
cd d:\DemocracIA
C:/Python314/python.exe -m pip install -r backend/requirements.txt
```

### Dashboard shows "Cannot connect to backend"
```powershell
# Verify backend is running:
curl http://localhost:8000/api/health

# If not, start it:
cd d:\DemocracIA\backend
C:/Python314/python.exe -m uvicorn app:app --reload --port 8000
```

---

## 📞 Commands Reference

| Task | Command |
|------|---------|
| **Run backend tests** | `C:/Python314/python.exe -m pytest backend/tests/ -v` |
| **Start backend only** | `cd backend && C:/Python314/python.exe -m uvicorn app:app --reload --port 8000` |
| **Start frontend only** | `cd frontend && npm run dev` |
| **Build frontend** | `cd frontend && npm run build` |
| **Lint frontend** | `cd frontend && npm run lint` |
| **Full diagnostics** | `C:/Python314/python.exe backend/agents/architect.py --audit` |
| **Check dependencies** | `C:/Python314/python.exe -m pip list \| grep -E "fastapi\|langgraph\|pydantic"` |

---

## 🔐 Configuration

### Required Environment Variables (Optional)
```env
# .env file in d:\DemocracIA\

ANTHROPIC_API_KEY=sk-ant-...          # Claude API (for LLM features)
LLM_MODEL=claude-3-5-sonnet-20241022  # Default model
LLM_TEMPERATURE=0.3                   # Reasoning mode

OBSERVER_API_KEYS=democracia-obs-dev-2026  # Observer network auth
```

### Optional: Alert Channels
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
```

---

## 📚 Documentation

- [Full Status Report](STATUS_REPORT.md) — Comprehensive diagnostics
- API Docs — http://localhost:8000/docs (when running)
- [Whitepaper](docs/whitepaper_2026_v2.md) — PEIRS methodology
- [Architecture](docs/architecture_2026_v1.4.md) — System design

---

## ✨ Next Steps

1. **[IMMEDIATE]** Install Node.js from https://nodejs.org/
2. **[THEN]** Run `.\arrange_all.ps1` to start both servers
3. **[VERIFY]** Open http://localhost:5173 in browser
4. **[TEST]** Analyze Peru 2026 via dashboard
5. **[EXPLORE]** Check API docs at http://localhost:8000/docs

---

**Status:** April 4, 2026 | **System Ready:** Backend ✅ | **Waiting for:** Node.js installation 🕐

For questions or issues, see [STATUS_REPORT.md](STATUS_REPORT.md) or run the diagnostic:
```powershell
C:/Python314/python.exe backend/agents/architect.py --audit
```
