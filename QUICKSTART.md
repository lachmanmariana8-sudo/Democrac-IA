# DEMOCRAC.IA / PEIRS — Quick Start Guide

**v0.5.2** — Predictive Electoral Integrity & Risk System

---

## ESTADO ACTUAL (2026-05-04)

| Componente | Estado | URL |
| --- | --- | --- |
| Frontend | OPERATIVO | <https://democracia.ar> |
| Backend | OPERATIVO | <https://democracia-peirs-production.up.railway.app> |
| Tests | 91/91 pasando | -- |
| Hunter scheduler | Activo cada 4h | 8 fuentes RSS Perú |
| Sesión observación PER 2026 | Activa | Restaurada tras restore Railway |
| i18n | es / en / pt | Elite Report trilingüe completo |

Para diagnóstico detallado, ver [STATUS_REPORT.md](STATUS_REPORT.md).

---

## USO EN PRODUCCION

La plataforma está en producción y accesible públicamente. No necesitás
correr nada localmente para usarla.

### Acceder al dashboard

1. Abrir <https://democracia.ar> en cualquier navegador moderno.
2. Si vas a generar Elite Reports, primero ingresá la Observer Key:
   - URL `https://democracia.ar/?key=TU_OBSERVER_KEY` (la key se guarda
     en `localStorage` y la URL se limpia automáticamente).
   - La key es la misma que está en `OBSERVER_API_KEYS` (variable de
     entorno en Railway → primario → Variables).

### Generar un Elite Report

1. Ir a **Perú Situation Room → Tab Informe Elite**.
2. Seleccionar **idioma** (es / en / pt) y **audiencia** (institutional /
   executive / press / international).
3. Click **Generar Informe Elite** (~$0.40-0.80 por informe, ~30-60s).
4. Tras la generación, descargar como:
   - **HTML** (visualizable en browser).
   - **Markdown** (para archivado / conversión).
   - **PDF** vía botón "Imprimir / Print" → `Ctrl+P` del browser.

### Descargar informes generados previamente

Los reportes ya generados están en SQLite triple-tier (sobreviven a
reinicios). Buscalos en la misma tab Informe Elite por `run_id` o desde
el endpoint:

```bash
curl -H "X-Observer-Key: TU_KEY" \
  https://democracia-peirs-production.up.railway.app/api/elite-report/{run_id}
```

---

## DESARROLLO LOCAL

### Prerequisitos

- Python 3.14 (Windows) o 3.11 (Linux/macOS — paridad con Railway)
- Node.js 18+ con npm
- Git

### Setup inicial

```bash
git clone https://github.com/lachmanmariana8-sudo/democracia-peirs.git
cd democracia-peirs

# Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r ../requirements.txt

# Frontend
cd ../frontend
npm install
```

### Variables de entorno (`.env` en raíz)

```env
ANTHROPIC_API_KEY=sk-ant-...
OBSERVER_API_KEYS=tu-clave-dev
LLM_MODEL=claude-sonnet-4-5
LLM_TEMPERATURE=0.3

# Opcionales
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
HUNTER_INTERVAL_MINUTES=240
MAX_ELITE_PER_DAY=20

# Datos (si usás CSV completos en local)
VDEM_CSV_PATH=../data/vdem/vdem_v16.csv
VDEM_VERSION=v16
VDEM_LAST_YEAR=2025
```

### Levantar el stack local

**Opción A — Scripts PowerShell (Windows):**

```powershell
# Terminal 1 — Backend
.\iniciar_backend.ps1

# Terminal 2 — Frontend
.\iniciar_frontend.ps1
```

**Opción B — Manual:**

```bash
# Terminal 1 — Backend (puerto 8000)
cd backend
uvicorn app:app --reload --port 8000

# Terminal 2 — Frontend (puerto 5173)
cd frontend
npm run dev
```

### Verificación

```bash
curl http://localhost:8000/api/health
# {"status":"operational","system":"DEMOCRAC.IA (PEIRS)","version":"0.4.0"...}
```

Abrir <http://localhost:5173> en el browser → debería verse el dashboard.

---

## QUE PUEDE HACER LA PLATAFORMA

### Países cubiertos (38)

| Región | Países |
| --- | --- |
| Américas (19) | VEN, NIC, GTM, URY, COL, BRA, MEX, ARG, CHL, BOL, ECU, PER, HND, SLV, PAN, CRI, DOM, PRY, CUB |
| Europa (8) | DEU, FRA, HUN, POL, SRB, GEO, ARM, AZE |
| África (5) | CMR, COD, ETH, NGA, ZWE |
| Asia / Medio Oriente (6) | BGD, PHL, MMR, PAK, THA, TUR |

**Caso de uso activo:** Perú 2026 (elecciones 12-abr-2026).

### Tipos de análisis

```bash
# Healthcheck
curl https://democracia-peirs-production.up.railway.app/api/health

# Lista de países
curl https://democracia-peirs-production.up.railway.app/api/countries

# Análisis pipeline 4 agentes (público)
curl -X POST https://democracia-peirs-production.up.railway.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"country_code": "PER"}'

# Elite Report (con Observer Key)
curl -X POST https://democracia-peirs-production.up.railway.app/api/elite-report \
  -H "Content-Type: application/json" \
  -H "X-Observer-Key: TU_KEY" \
  -d '{"country_code": "PER", "language": "en", "audience": "institutional", "report_type": "preliminary"}'
```

### Datasets integrados

| Dataset | Cobertura | Uso |
| --- | --- | --- |
| V-Dem v16 | 1789-2025 | EMB, irregularidades, libertad civil, media, ecosistema digital |
| Freedom House FIW | 2013-2025 | Score democracia, libertades civiles/políticas |
| PEI 10.0 | 2012-2023 | Integridad EMBs, financiamiento, medios, registro |
| RSF 2025 | 180 países | Libertad de prensa por país |
| OONI | Tiempo real | Censura web (date-only since/until) |
| Hunter RSS Perú | Cada 4h | 8 fuentes verificadas mapeadas a 9 fases electorales |

---

## TESTING

### Suite completa

```bash
cd backend
pytest -q  # 91 tests, ~8s
```

### Sólo Elite Report integration

```bash
cd backend
pytest tests/test_elite_pipeline.py -v
```

### Coverage

```bash
cd backend
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

---

## ESTRUCTURA DEL REPO

```text
d:\DemocracIA\
├── backend/                    FastAPI + LangGraph
│   ├── app.py                  Server principal (5400+ líneas)
│   ├── agents/
│   │   ├── elite_report/       Pipeline Elite Report (12 caps + 3 anexos)
│   │   ├── pipeline.py         LangGraph 4 agentes
│   │   ├── architect.py        Architect Agent (Opus 4.7 autónomo)
│   │   └── ...
│   ├── modules/                Loaders V-Dem v16, FH, PEI, RSF, validators
│   ├── rag/                    ChromaDB + sentence-transformers
│   ├── integrations/           OONI, alerts, peru_sources
│   ├── db/                     SQLite triple-tier
│   ├── tests/                  91 tests
│   └── requirements.txt
│
├── frontend/                   React 19 + Vite 7
│   ├── src/App.jsx             Single-file app (~5000 líneas)
│   ├── package.json
│   └── vite.config.js
│
├── data/                       Datasets (V-Dem CSV completo excluido de git)
│   ├── vdem/vdem_v16.csv       Excluido de git (~440MB)
│   ├── All_data_FIW_2013-2025 - Index.csv
│   ├── PEI/PEI_10 Election External.csv
│   └── RSF/2025 - 2025.csv
│
├── DOCS Proyect/               Documentación institucional
│   ├── PEIRS_Documento_Institucional_v2.0.md   Para partners (CONFIDENCIAL)
│   ├── PEIRS_Arquitectura_Roadmap.md           Script técnico de sesiones
│   ├── INFORME_METODOLOGIA.md                  Playbook reproducible
│   └── PROMPT_MAESTRO.md                       Instrumento de evaluación
│
├── scripts/
│   ├── backup.py                Backup completo prod (--targz para tar.gz)
│   └── generate_vdem_static.py  Regenera vdem_static.py desde CSV
│
├── STATUS_REPORT.md             Diagnóstico actualizado
├── QUICKSTART.md                Esta guía
├── DEPLOY_README.md             Procedimiento de despliegue
├── AUDIT_TECNICO_COMPLETO.md    Auditoría técnica
├── CLAUDE.md                    Token-efficient rules
├── nixpacks.toml                Config Railway build
├── railway.toml                 Config Railway deploy
├── Procfile                     Backup start command
├── netlify.toml                 Config frontend
└── iniciar_*.ps1                Scripts de bring-up local
```

---

## TROUBLESHOOTING

### El dashboard no carga (`https://democracia.ar`)

Si ves error en consola tipo "Error: Acceso restringido", la Observer Key
del browser se perdió. Solución:

```text
https://democracia.ar/?key=TU_OBSERVER_KEY
```

El frontend ingiere la key, la guarda en localStorage, limpia la URL.
Refresh con `Ctrl+F5`.

### Backend remoto da timeout

Probable cold start de Railway tras inactividad. Esperar ~30-60s y
reintentar. Si persiste >5 min, verificar Railway dashboard
(`Deployments → último deploy verde`).

### Budget diario agotado

```text
{"error":"Budget diario agotado para PER.","limit":5}
```

Subir `MAX_ELITE_PER_DAY` en Railway → primario → Variables. El cambio
re-despliega automático.

### Backend local: `Cannot find module 'anthropic'`

```bash
cd backend
pip install -r ../requirements.txt
```

### Backend local: puerto 8000 ocupado

```powershell
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

---

## CONFIGURACION AVANZADA

### Alertas

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
ALERT_EMAIL_FROM=alerts@democracia.ar
ALERT_EMAIL_TO=tu@email.com
ALERT_SMTP_HOST=smtp.sendgrid.net
ALERT_SMTP_PORT=587
ALERT_SMTP_USER=apikey
ALERT_SMTP_PASS=...
ALERT_MIN_SEVERITY=high
```

### Hunter scheduler

```env
HUNTER_INTERVAL_MINUTES=240         # Default 4h
AUTO_OBSERVE_COUNTRIES=PER          # Arranca observación auto al boot
```

### CORS

```env
ALLOWED_ORIGINS=https://democracia.ar,https://www.democracia.ar
# O wildcard (acepta cualquier origen + credenciales):
ALLOWED_ORIGINS=*
```

---

## DOCUMENTOS

- [STATUS_REPORT.md](STATUS_REPORT.md) — Diagnóstico técnico completo
- [DEPLOY_README.md](DEPLOY_README.md) — Procedimiento de despliegue
- [AUDIT_TECNICO_COMPLETO.md](AUDIT_TECNICO_COMPLETO.md) — Auditoría detallada
- [DOCS Proyect/PEIRS_Documento_Institucional_v2.0.md](DOCS%20Proyect/PEIRS_Documento_Institucional_v2.0.md) — Dossier para partners
- [DOCS Proyect/PEIRS_Arquitectura_Roadmap.md](DOCS%20Proyect/PEIRS_Arquitectura_Roadmap.md) — Roadmap técnico cronológico
- [DOCS Proyect/INFORME_METODOLOGIA.md](DOCS%20Proyect/INFORME_METODOLOGIA.md) — Playbook del Elite Report

---

**Versión:** v0.5.2 (cierre 4-may-2026)
**Sistema:** Producción en `democracia.ar` + `democracia-peirs-production.up.railway.app`
