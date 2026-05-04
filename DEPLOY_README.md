# 🇵🇪 DEMOCRAC.IA / PEIRS — Despliegue a Producción

**www.democracia.ar** — Sistema de Inteligencia Electoral OSINT

---

## 🚀 Despliegue Rápido

### Arquitectura de Producción
```
www.democracia.ar     → Netlify (Frontend React)
democracia-peirs-production.up.railway.app     → Railway (Backend FastAPI + SQLite)
```

### Estado Actual
- ✅ **Backend:** v0.4.0 listo para Railway
- ✅ **Frontend:** React 19 listo para Netlify
- ✅ **Configuración:** railway.toml, netlify.toml, Procfile
- ✅ **Tests:** 82/82 pasando
- ✅ **Build:** Frontend compilado (939KB JS, 0.91KB CSS)

---

## 📋 Checklist de Despliegue

### Backend (Railway)
- [ ] Crear proyecto en https://railway.app
- [ ] Conectar repo GitHub
- [ ] Agregar variables de entorno:
  ```
  ANTHROPIC_API_KEY=sk-ant-...
  OBSERVER_API_KEYS=clave-produccion-2026
  ```
- [ ] Configurar dominio: `democracia-peirs-production.up.railway.app`
- [ ] (Opcional) Subir datasets CSV via Railway CLI

### Frontend (Netlify)
- [ ] Crear sitio en https://netlify.com
- [ ] Conectar repo GitHub
- [ ] Agregar variable: `VITE_API_BASE=https://democracia-peirs-production.up.railway.app`
- [ ] Configurar dominio: `www.democracia.ar`

### DNS (En registrador de democracia.ar)
```
Tipo    Nombre    Valor
CNAME   www       [netlify-cname].netlify.app
CNAME   api       [railway-cname].up.railway.app
A       @         75.2.60.5
```

---

## 🛠️ Scripts de Ayuda

### Despliegue Paso a Paso
```powershell
.\deploy_production.ps1
```

### Verificación Post-Despliegue
```powershell
.\verify_production.ps1
```

### Inicio Local (Desarrollo)
```powershell
.\arrange_all.ps1
```

---

## 📊 Endpoints de Producción

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `https://www.democracia.ar` | GET | Dashboard principal |
| `https://democracia-peirs-production.up.railway.app/api/health` | GET | Estado del sistema |
| `https://democracia-peirs-production.up.railway.app/api/countries` | GET | Lista de países (38) |
| `https://democracia-peirs-production.up.railway.app/api/analyze` | POST | Análisis electoral completo |
| `https://democracia-peirs-production.up.railway.app/docs` | GET | Documentación Swagger |

### Ejemplo de Request
```bash
curl -X POST https://democracia-peirs-production.up.railway.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"country_code": "PER", "election_date": "2026-04-12"}'
```

---

## 📈 Monitoreo

### Railway (Backend)
- Logs en tiempo real
- Métricas de CPU/memoria
- Health checks automáticos
- Volume usage (si se suben CSVs)

### Netlify (Frontend)
- Analytics de visitas
- Build logs
- Form submissions
- Domain SSL status

### Manual
```powershell
# Health check
curl https://democracia-peirs-production.up.railway.app/api/health

# Test completo
.\verify_production.ps1
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno Opcionales

**Railway:**
```env
# LLM features
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022

# Observer authentication
OBSERVER_API_KEYS=key1,key2,key3

# Custom data paths (si se suben CSVs)
VDEM_CSV_PATH=/data/V-Dem-CY-Full+Others-v15.csv
FH_CSV_PATH=/data/All_data_FIW_2013-2025 - Index.csv
PEI_CSV_PATH=/data/PEI/PEI_10 Election External.csv
RSF_CSV_PATH=/data/RSF/2025 - 2025.csv
```

**Netlify:**
```env
VITE_API_BASE=https://democracia-peirs-production.up.railway.app
NODE_VERSION=20
```

### Datasets Opcionales
Los CSVs grandes (V-Dem: 384MB) no están en GitHub. Opciones:

1. **Railway Volume** (recomendado): Subir via CLI
2. **Sin datasets**: Sistema usa datos mock
3. **External storage**: Configurar URLs externas

---

## 🚨 Troubleshooting

### Problemas Comunes

| Problema | Síntoma | Solución |
|----------|---------|----------|
| DNS no propaga | Sitio no carga | Esperar 24-48h, verificar registros |
| Backend timeout | API no responde | Revisar Railway logs, aumentar timeout |
| CORS error | Frontend no conecta | Verificar VITE_API_BASE en Netlify |
| Build falla | Deploy error | Revisar logs, verificar Node version |
| Datasets faltan | Solo datos mock | Subir CSVs o usar datos simulados |

### Comandos de Diagnóstico
```powershell
# Verificar DNS
nslookup www.democracia.ar
nslookup democracia-peirs-production.up.railway.app

# Test API
curl https://democracia-peirs-production.up.railway.app/api/health

# Verificar SSL
openssl s_client -connect democracia-peirs-production.up.railway.app:443
```

---

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) — Inicio rápido desarrollo
- [STATUS_REPORT.md](STATUS_REPORT.md) — Estado actual del sistema
- [CODEBASE_ANALYSIS.md](docs/CODEBASE_ANALYSIS.md) — Arquitectura detallada
- [docs/deploy_guide.md](docs/deploy_guide.md) — Guía completa de despliegue
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — Instrucciones para AI

---

## 🎯 Próximos Pasos

1. **Desplegar** usando `.\deploy_production.ps1`
2. **Verificar** con `.\verify_production.ps1`
3. **Monitorear** logs en Railway/Netlify
4. **Configurar** alertas y monitoreo
5. **Documentar** procedimientos de mantenimiento

---

**Estado:** Listo para producción 🚀  
**Fecha:** Abril 4, 2026  
**Versión:** v0.4.0

Para soporte: Ver STATUS_REPORT.md o ejecutar diagnóstico local.