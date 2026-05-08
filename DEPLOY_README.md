# DEMOCRAC.IA / PEIRS — Despliegue a Producción

**Sistema de Inteligencia Electoral OSINT** — operativo en
[democracia.ar](https://democracia.ar)

---

## Arquitectura de Producción

```text
democracia.ar                                  → Netlify (Frontend React 19 + Vite 7)
democracia-peirs-production.up.railway.app     → Railway (Backend FastAPI + SQLite + volumen)
api.democracia.ar (secundario, hibernado)      → Railway con auto-deploy DESACTIVADO
```

Ambos backends están conectados al mismo repo + branch `main`. Sólo el
**primario** (`democracia-peirs-production.up.railway.app`) tiene auto-deploy
activo. El secundario se preserva como backup vivo pero NO recibe pushes
automáticos. Esto evita el patrón de dual-deploy original.

---

## Estado Actual (4-may-2026)

| Capa | Estado | Versión / Notas |
|---|---|---|
| Backend | OPERATIVO | v0.5.2 — recovery exitoso tras incidente Railway |
| Frontend | OPERATIVO | Bundle `assets/index-BF4UNvwu.js` |
| Tests | 91/91 pasando | ~8s para suite completa |
| SQLite triple-tier | OPERATIVO | filesystem + TEXT columns + PDF on-demand |
| i18n trilingüe (es/en/pt) | OPERATIVO | 180+ claves + section_titles 50 entries |
| Hunter scheduler | OPERATIVO | 14 fuentes RSS (8 PER + 6 intl) cada 24h |
| Sesión PER 2026 | ACTIVA | Volumen preservado tras restore |

---

## Despliegue Inicial — checklist completo

### 1. Backend (Railway)

- [ ] Crear proyecto en [railway.app](https://railway.app)
- [ ] Conectar repo GitHub `lachmanmariana8-sudo/democracia-peirs`
- [ ] Branch: `main` con auto-deploy ON
- [ ] Crear **volumen persistente** montado en `/data` (1GB alcanza para meses)
- [ ] Agregar variables de entorno (mínimas):

  ```env
  ANTHROPIC_API_KEY=sk-ant-...
  OBSERVER_API_KEYS=clave-produccion-2026
  DEMOCRACIA_DB_PATH=/data/democracia.db
  AUTO_OBSERVE_COUNTRIES=PER
  HUNTER_INTERVAL_MINUTES=1440
  MAX_ELITE_PER_DAY=20
  VDEM_VERSION=v16
  VDEM_LAST_YEAR=2025
  VDEM_CSV_PATH=../data/vdem/vdem_v16.csv
  ALLOWED_ORIGINS=https://democracia.ar,https://www.democracia.ar
  ```

- [ ] Variables opcionales para alertas:

  ```env
  ALERT_WEBHOOK_URL=https://discord.com/api/webhooks/...
  ALERT_MIN_SEVERITY=high
  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
  ALERT_EMAIL_FROM=...
  ALERT_EMAIL_TO=...
  ALERT_SMTP_HOST=...
  ALERT_SMTP_PORT=587
  ALERT_SMTP_USER=...
  ALERT_SMTP_PASS=...
  ```

- [ ] Verificar build: `nixpacks.toml` debe estar usando `python311`
- [ ] Verificar healthcheck: `/api/health` con timeout 300s en `railway.toml`
- [ ] Esperar primer deploy (~6-10 min)

### 2. Frontend (Netlify)

- [ ] Crear sitio en [netlify.com](https://netlify.com) conectado al mismo repo
- [ ] Build settings: `npm run build` desde `frontend/`, publish `frontend/dist`
- [ ] Variables de entorno:

  ```env
  VITE_API_BASE=https://democracia-peirs-production.up.railway.app
  NODE_VERSION=20
  ```

- [ ] Configurar dominio custom: `democracia.ar` y `www.democracia.ar`

### 3. DNS (en el registrador del dominio `democracia.ar`)

```text
Tipo    Nombre    Valor
A       @         75.2.60.5             (Netlify)
CNAME   www       <netlify-cname>.netlify.app
```

> Nota: el registro `CNAME api → railway` queda como reliquia del dual-deploy
> original. Se puede dejar como fallback o eliminar — el dominio activo del
> backend es `democracia-peirs-production.up.railway.app` directamente, no
> via `api.democracia.ar`.

---

## Endpoints de Producción

| Endpoint | Método | Auth | Descripción |
|---|---|---|---|
| `https://democracia.ar` | GET | — | Dashboard principal |
| `/api/health` | GET | público | Estado del sistema, version, features |
| `/api/countries` | GET | público | Lista de 38 países |
| `/api/analyze` | POST | público | Pipeline LangGraph 4 agentes |
| `/api/elite-report` | POST | X-Observer-Key | Genera Elite Report |
| `/api/elite-report/{id}` | GET | X-Observer-Key | HTML del informe |
| `/api/elite-report/{id}/markdown` | GET | X-Observer-Key | Versión MD |
| `/api/elite-report/{id}/printable` | GET | X-Observer-Key | HTML A4 para `window.print()` |
| `/api/elite-report/{id}/structured` | GET | X-Observer-Key | Extracción de secciones |
| `/api/observation/{cc}/active` | GET | público | Sesión activa del país |
| `/api/sentinel/alerts` | GET | público | Alertas Hunter |

Documentación Swagger: `https://democracia-peirs-production.up.railway.app/docs`

### Ejemplo: Health check

```bash
curl https://democracia-peirs-production.up.railway.app/api/health | jq
```

### Ejemplo: Generar Elite Report en EN

```bash
curl -X POST https://democracia-peirs-production.up.railway.app/api/elite-report \
  -H "Content-Type: application/json" \
  -H "X-Observer-Key: $OBSERVER_KEY" \
  -d '{
    "country_code": "PER",
    "language": "en",
    "audience": "institutional",
    "report_type": "preliminary"
  }'
```

---

## Monitoreo y Logs

### Railway (Backend)

- **Deployments → último** — estado del deploy más reciente y logs de build/runtime
- **Metrics** — CPU, memoria, network I/O
- **Volume usage** — `/data` (SQLite + ChromaDB index + reports filesystem)
- **Variables** — env vars editables sin redeploy automático

### Netlify (Frontend)

- **Deploys** — historial de builds con clear cache option
- **Analytics** — visitas, países, performance
- **Domain status** — SSL Let's Encrypt auto-renewal

### Manual (CLI)

```bash
# Health check
curl https://democracia-peirs-production.up.railway.app/api/health | jq

# Verificar build version desplegado
curl -s https://democracia-peirs-production.up.railway.app/api/health \
  | jq '{version, features, llm_configured, active_observation_sessions}'
```

---

## Procedimientos Operativos

### Trigger redeploy desde main

Para subir código nuevo al primario sin disparar build en el secundario:

1. Verificar en Railway → secundario (`api.democracia.ar`) → Settings → Source
   que **"Auto deploys when pushed to GitHub"** esté en **DESACTIVADO**.
2. `git push origin main` → sólo el primario buildea.

### Subir el budget diario de Elite Reports

`MAX_ELITE_PER_DAY` (default 5). Para subirlo:

1. Railway → primario → **Variables** → editar/agregar `MAX_ELITE_PER_DAY=20`
2. Railway redeploya automáticamente al cambiar variables
3. Verificar en `/api/health` que el container está operativo

### Reset de Observer Key en browser

Si la usuaria pierde el `localStorage` (incognito, clear cache):

1. Copiar valor de `OBSERVER_API_KEYS` desde Railway → primario → Variables
2. Navegar a `https://democracia.ar/?key=ESA_KEY`
3. El frontend ingiere automáticamente, guarda en localStorage, limpia URL
4. Refresh con `Ctrl+F5`

### Restore de proyecto Railway eliminado por error

Documentado tras incidente del 4-may-2026:

1. Ir a [railway.app](https://railway.app) → tu avatar → **Account Settings**
2. Buscar **"Recently Deleted Projects"** o **"Trash"**
3. Si aparece el proyecto: click → **Restore**. Volumen viene íntegro
4. Si no aparece (ventana de 7 días agotada o plan sin restore): contactar
   soporte por chat dentro del dashboard:

   > *"Hi — I accidentally deleted my production project today (DATE), name
   > was X. It had a persistent volume with critical data. Please restore
   > the project and the volume ASAP. Thanks."*

5. Tras restore: el deploy puede tardar 5-10 min en levantar el container
   nuevo. El build viejo (snapshot pre-delete) se restaura — para subir al
   código actual, hacer un `git push` con commit nuevo

### Backup completo de producción

Antes de operaciones de riesgo (delete, migration, etc.):

```bash
python scripts/backup.py --targz
# Genera backups/peirs_backup_YYYY-MM-DD_HHMMSS.tar.gz
# Incluye: SQLite, reports filesystem, env vars NO secretas
```

---

## Troubleshooting

| Problema | Síntoma | Solución |
|---|---|---|
| DNS no propaga | `democracia.ar` no carga | Esperar 24-48h, verificar registros con `nslookup` |
| Backend timeout (cold start) | API timeout primer request tras 5+ min idle | Esperar 30-60s y reintentar |
| Backend muerto post-restore | URL responde 000 timeout indefinido | Verificar Railway dashboard, restore manual |
| CORS error | Frontend no conecta | Verificar `ALLOWED_ORIGINS` y `VITE_API_BASE` |
| Build falla | Deploy error en Railway | Revisar Build Logs, verificar Python 3.11 nested f-strings |
| Datasets faltan (V-Dem) | Reportes con datos mock | El static fallback en `vdem_static.py` cubre 38 países × 21 indicators × 1985-2025 |
| Volumen Railway perdido | Reportes desaparecidos | SQLite triple-tier debería preservar `md_content` y `html_content` en TEXT columns |
| Budget elite agotado | `429 Budget diario agotado` | Subir `MAX_ELITE_PER_DAY` o esperar reset 00:00 UTC |
| Observer Key inválida | `403 Acceso restringido` | Pegar `?key=...` en URL del browser |

### Comandos de Diagnóstico

```bash
# Verificar DNS
nslookup democracia.ar
nslookup democracia-peirs-production.up.railway.app

# Test API
curl -o /dev/null -w "%{http_code} %{time_total}s\n" \
  https://democracia-peirs-production.up.railway.app/api/health

# Verificar SSL
openssl s_client -connect democracia-peirs-production.up.railway.app:443 -servername democracia-peirs-production.up.railway.app < /dev/null

# Listar deploys con git
git log --oneline -10
```

---

## Configuración Avanzada

### Cambiar modelo LLM

```env
LLM_MODEL=claude-sonnet-4-6              # Default operativo
LLM_TEMPERATURE=0.3                      # 0.0-1.0
```

### Tests pre-deploy

```bash
cd backend
python -m pytest -q
# 91 tests pasando — bloquear push si falla
```

### Datasets

| Dataset | Path | Estado |
|---|---|---|
| V-Dem v16 (full) | `data/vdem/vdem_v16.csv` (~440MB) | Excluido de git, opcional en Railway |
| V-Dem static | `backend/modules/vdem_static.py` | En git (618KB), 38 países × 21 indicators × 1985-2025 |
| Freedom House FIW | `data/All_data_FIW_2013-2025 - Index.csv` | En git |
| PEI 10.0 | `data/PEI/PEI_10 Election External.csv` | En git |
| RSF 2025 | `data/RSF/2025 - 2025.csv` | En git |

> El sistema funciona sin el CSV completo de V-Dem porque `vdem_static.py`
> provee fallback para los 38 países monitoreados con todos los indicadores
> usados por el Elite Report.

---

## Documentación

- [STATUS_REPORT.md](STATUS_REPORT.md) — diagnóstico técnico completo v0.5.2
- [QUICKSTART.md](QUICKSTART.md) — guía de uso productivo + dev local
- [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md) — navegación del codebase
- [AUDIT_TECNICO_COMPLETO.md](AUDIT_TECNICO_COMPLETO.md) — auditoría detallada
- [DOCS Proyect/PEIRS_Documento_Institucional_v2.0.md](DOCS%20Proyect/PEIRS_Documento_Institucional_v2.0.md) — dossier para partners (CONFIDENCIAL)
- [DOCS Proyect/PEIRS_Arquitectura_Roadmap.md](DOCS%20Proyect/PEIRS_Arquitectura_Roadmap.md) — roadmap técnico cronológico
- [DOCS Proyect/INFORME_METODOLOGIA.md](DOCS%20Proyect/INFORME_METODOLOGIA.md) — playbook reproducible

---

**Estado:** En producción
**Versión:** v0.5.2
**Fecha:** 4 de mayo de 2026
**URL principal:** <https://democracia.ar>
