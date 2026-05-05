# DEMOCRAC.IA / PEIRS — Status Report

**Generated:** 2026-05-04 (cierre de sesión) | **Version:** v0.5.2

---

## SISTEMA EN PRODUCCION

| Capa | Estado | URL / Endpoint |
| --- | --- | --- |
| Frontend (React + Vite) | OPERATIVO | <https://democracia.ar> |
| Backend (FastAPI) | OPERATIVO | <https://democracia-peirs-production.up.railway.app> |
| Healthcheck | OPERATIVO | `/api/health` (timeout 300s) |
| Volumen persistente | OPERATIVO | SQLite triple-tier (filesystem + TEXT + PDF on-demand) |
| Sesión observación PER 2026 | ACTIVA | Restaurada tras restore Railway 4-may |
| Hunter scheduler | OPERATIVO | Cada 4h sobre 8 fuentes RSS Perú |
| Discord webhook alerts | OPERATIVO | Severidad ≥ high |

---

## BACKEND

### Entorno Python

- **Producción (Railway):** Python 3.11 (Nixpacks `python311`)
- **Desarrollo local (Windows):** Python 3.14.3 en `C:/Python314/`
- **Parity confirmada:** sin nested f-strings PEP 701 (3.14 acepta, 3.11 no)

### Dependencias clave

- LangGraph 0.2.x (orchestration)
- LangChain Core 0.3.x + langchain-anthropic
- FastAPI 0.115.x + Uvicorn
- Pydantic 2.x
- Pandas 2.x (subido a 3.x en local)
- ChromaDB + sentence-transformers (all-MiniLM-L6-v2, 90MB)
- httpx (RSS + OONI)
- Anthropic SDK + claude-agent-sdk
- pytest (separado en `requirements-dev.txt`)

### Tests

- **Total:** 91/91 pasando (era 82 al 4-abr; +9 con `test_elite_pipeline.py`)
- **Coverage:** loaders, persistencia, e2e pipeline, Elite Report integration
- **Warnings:** 2 deprecation no-críticos (LangChain Core Pydantic V1, ChromaDB asyncio.iscoroutinefunction)

### Endpoints principales

```
GET  /api/health                                System status (público)
GET  /api/countries                             Lista de 38 países
POST /api/analyze                               Pipeline LangGraph 4 agentes
GET  /api/report/{run_id}                       Recupera reporte
GET  /api/report/{run_id}/markdown              Versión Markdown
GET  /api/report/{run_id}/traceability          JSON de trazabilidad APA 7

POST /api/elite-report                          Genera Elite Report (Observer Key)
GET  /api/elite-report/{run_id}                 HTML del Elite Report
GET  /api/elite-report/{run_id}/structured      Extracción dinámica de secciones
GET  /api/elite-report/{run_id}/printable       HTML A4 para window.print()
GET  /api/elite-report/{run_id}/markdown        Versión MD (i18n aplicado)

GET  /api/sentinel/alerts                       Alertas en tiempo real (Hunter)
GET  /api/peru/actors                           8 fuerzas políticas 2026
GET  /api/peru/scenarios                        Escenarios parlamentarios
GET  /api/observation/{country}/active          Sesión activa del país
POST /api/observation/{session_id}/entry        Registrar entry de campo
```

### Fuentes de datos integradas

| Fuente | Formato | Estado | Cobertura |
| --- | --- | --- | --- |
| V-Dem v16 | CSV + static | OPERATIVO | 1789-2025, 38 países × 21 indicadores en `vdem_static.py` |
| Freedom House FIW | CSV | OPERATIVO | 2013-2025 |
| PEI v10.0 | CSV | OPERATIVO | 2012-2023, 586 elecciones |
| RSF 2025 | CSV | OPERATIVO | 180 países |
| OONI | API | OPERATIVO | Censura web en tiempo real (date-only since/until) |
| Hunter RSS Perú | RSS | OPERATIVO | Andina, RPP, El Comercio, Gestión, IDL-Reporteros, Wayka, JNE, ONPE |
| Marco legal | RAG | OPERATIVO | 14 instrumentos vectorizados en ChromaDB |

---

## FRONTEND

### Estado

- **OPERATIVO en producción** en <https://democracia.ar>
- Bundle actual: `assets/index-BF4UNvwu.js`
- Auto-deploy desde GitHub `main` via Netlify

### Stack

- React 19 + Vite 7 + Recharts 2.x
- Estilos inline (sin Tailwind/CSS-in-JS framework)
- Tema oscuro institucional con Fraunces + DM Sans + DM Mono
- Single-file app (`src/App.jsx`, ~5000 líneas)

### Tabs operativas

- **Overview** — Dashboard global 38 países
- **Detalle país** — Análisis individual con gauge + radar + violaciones
- **Sentinel** — Alertas Hunter en tiempo real
- **Perú Situation Room** — 11 secciones específicas Perú 2026
- **Metodología** — Documentación de indicadores

---

## i18n PROFUNDO (es / en / pt)

- **180+ claves** en `agents/elite_report/i18n.py`: cover, footer, TOC, captions, viz titles/subtitles, headers SVG, status labels, gauge bands, compliance columns, scenarios labels, audit notes, alert badges, severity legends, Appendix A body completo
- **50 entradas** de subchapter titles en `agents/elite_report/section_titles.py` cubriendo 1.1 a 12.6
- **LANGUAGE_RULE** reforzado en composer: LLM responde en idioma pedido aún con contexto en español

---

## SEGURIDAD

| Componente | Estado | Notas |
| --- | --- | --- |
| Autenticación API | OPERATIVA | X-Observer-Key sobre endpoints sensibles (`elite-report`, `observation`) |
| Rate limiting | OPERATIVO | Por IP en endpoints caros |
| Budget diario | OPERATIVO | `MAX_ELITE_PER_DAY` env var (default 5; producción 20) |
| CORS | OPERATIVO | Default a dominios explícitos + soporte wildcard via regex |
| Base de datos | LOCAL en volumen Railway | SQLite con WAL mode |
| LLM | CONFIGURADO | `ANTHROPIC_API_KEY` en Variables Railway |

---

## INFRAESTRUCTURA

| Servicio | Función | Estado |
| --- | --- | --- |
| Railway (primario) | Backend FastAPI + volumen persistente | OPERATIVO. Restore exitoso 4-may, dual-deploy resuelto |
| Railway (secundario) | `api.democracia.ar` | Auto-deploy DESACTIVADO (preservado por seguridad) |
| Netlify | Frontend `democracia.ar` | OPERATIVO |
| Discord webhook | Alertas severidad ≥ high | OPERATIVO |
| GitHub | Repo principal | `main` con auto-deploy |

---

## VALIDATION CHECKLIST

### Backend

- [x] Python deps instalados (Railway Nixpacks)
- [x] Configuración validada
- [x] 91/91 tests pasando
- [x] Healthcheck operativo
- [x] Loaders V-Dem v16 + FH + PEI + RSF funcionando
- [x] SQLite triple-tier inicializado
- [x] RAG ChromaDB indexado (init_rag en background)
- [x] OONI integration ready
- [x] Hunter scheduler operativo
- [x] Discord alerts operativos

### Frontend

- [x] Build production (Vite)
- [x] Servido en `democracia.ar`
- [x] Backend connection ok (CORS validado)
- [x] Observer Key flow operativo (URL `?key=`+ localStorage)
- [x] i18n trilingüe en informe Elite

### Integración

- [x] Backend ↔ SQLite triple-tier
- [x] Backend ↔ ChromaDB RAG
- [x] Backend ↔ OONI
- [x] Backend ↔ datasets reales
- [x] Backend ↔ Hunter RSS
- [x] Backend ↔ Discord webhook
- [x] Frontend ↔ Backend producción

---

## COMANDOS DE SOPORTE

### Healthcheck remoto

```bash
curl -s https://democracia-peirs-production.up.railway.app/api/health | jq
```

### Healthcheck local (dev)

```powershell
cd d:\DemocracIA
.\iniciar_backend.ps1
# Espera: [V-Dem] OK [FH] OK [PEI] OK + Application startup complete
```

### Tests (correr suite)

```powershell
cd d:\DemocracIA\backend
C:/Python314/python.exe -m pytest -q
```

### Backup de producción

```bash
python scripts/backup.py --targz
# Genera backups/peirs_backup_YYYY-MM-DD_HHMMSS.tar.gz
```

### Frontend dev local

```powershell
cd d:\DemocracIA\frontend
npm install
npm run dev
# Sirve en http://localhost:5173
```

---

## DOCUMENTOS ASOCIADOS

- [PEIRS_Documento_Institucional_v2.0.md](DOCS%20Proyect/PEIRS_Documento_Institucional_v2.0.md) — Dossier institucional ejecutivo (CONFIDENCIAL)
- [PEIRS_Arquitectura_Roadmap.md](DOCS%20Proyect/PEIRS_Arquitectura_Roadmap.md) — Roadmap técnico con script de sesiones
- [INFORME_METODOLOGIA.md](DOCS%20Proyect/INFORME_METODOLOGIA.md) — Playbook reproducible del Elite Report
- [QUICKSTART.md](QUICKSTART.md) — Guía de uso de la plataforma
- [DEPLOY_README.md](DEPLOY_README.md) — Procedimiento de despliegue
- [AUDIT_TECNICO_COMPLETO.md](AUDIT_TECNICO_COMPLETO.md) — Auditoría técnica detallada

---

**Generated:** 2026-05-04 (cierre v0.5.2)
**System:** Producción en `democracia.ar` + `democracia-peirs-production.up.railway.app`
**Next Review:** Tras Sprints 2-3 (CountryAdapter + modelo institucional generalizado)
