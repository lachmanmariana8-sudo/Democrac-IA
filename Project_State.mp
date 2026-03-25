# DEMOCRAC.IA (PEIRS) — Project State
*Última actualización: 2026-03-22*

## Estado General: v0.4.0 — Dashboard dinámico con 33 países, caché, búsqueda y agrupación regional

---

## DATOS REALES CONFIRMADOS (4 países)

| País | FH | V-Dem libdem | EMB | PEI EMBs | Risk Score |
|------|----|-------------|-----|----------|------------|
| VEN | 13/100 NF | 0.049 (2024) | CAPTURED 0.2535 | 20.0 (2018) | 78.9 CRITICAL |
| NIC | 14/100 NF | 0.019 (2024) | CAPTURED 0.2924 | 29.0 (2021) | 76.1 CRITICAL |
| GTM | 48/100 PF | 0.469 (2024) | PARTIAL 0.6005 | 61.0 (2023) | 34.7 MODERATE |
| URY | 96/100 F  | 0.769 (2024) | FULL 0.8448 | 88.0 (2019) | 14.3 LOW |

---

## INFORME VIP — ESTADO ACTUAL

### ✅ Capítulos operativos con datos reales
- Cap. 1: Resumen Ejecutivo — FH + V-Dem + EMB + PEI con fuente y año
- Cap. 2: Contexto Político — marco legal + libertades civiles (mock)
- Cap. 3: EMB — nombre + independencia + autonomía + irregularidades (V-Dem real)
- Cap. 4: Inclusividad — V-Dem suffrage + association + FH CL rating (LLM narrative)
- Cap. 5: Campaña y Medios — sesgo + financiamiento + red de poder (mock)
- Cap. 6: Ecosistema Digital — bots + censura + desinformación (mock)
- Cap. 8: Justicia Electoral — 10 violaciones ICCPR/CADH/CDI con severidad
- Cap. 9: Recomendaciones — outlook + impacto inversores

### 🔴 Pendientes
- Cap. 7: Día de Votación — se genera en tiempo real via /api/analyze/voting-day

---

## ARQUITECTURA

### Backend (FastAPI + LangGraph)
- `D:\DemocracIA\backend\app.py` — v0.3.2
- 4 agentes: OSINT → Political → Legal → ReportGenerator
- Endpoints: /api/dashboard, /api/report/{id}/markdown, /api/report/{id}/traceability
- Persistencia: reports guardados en /data/reports/ (JSON) + índice por país

### Frontend (Vite + React)
- `D:\DemocracIA\frontend\src\App.jsx`
- ReportViewer con 3 tabs: Dashboard / Dictamen / Informe
- Dashboard tab: Gauge + Source badges + **Resumen Ejecutivo (Cap. 1)** + Dimensiones + Violaciones
- Dictamen tab: Narrativa técnica del agente
- Informe tab: renderMarkdownWithTooltips — informe completo con tooltips interactivos

### Datasets
| Dataset | Archivo | Filas | Cobertura |
|---------|---------|-------|-----------|
| V-Dem v15 | V-Dem-CY-Full+Others-v15.csv | 27,913 | 1789–2024 |
| Freedom House FIW | All_data_FIW_2013-2025 - Index.csv | 2,723 | 2013–2025 |
| PEI 10.0 | PEI/PEI_10 Election External.csv | 586 | 2012–2023 |
| RSF 2025 | RSF/2025 - 2025.csv | 180 | 2025 |

---

## ISSUES

| ID | Descripción | Prioridad | Estado |
|----|-------------|-----------|--------|
| #003 | Marco legal, padrón electoral: mock | Media | Abierto |
| #004 | Contador confianza Agente Legal no cuenta PEI | Baja | Abierto |
| #005 | Warning "Duplicate key border" en App.jsx | Baja | Abierto |
| #006 | PEI Venezuela: OVERALLINTEGRITY = N/D (2018) | Info | Abierto |
| #007 | reports_store en memoria — no persiste entre reinicios | Media | **RESUELTO** (save_report a disco) |
| #008 | Dashboard muestra marcadores de capítulos | Alta | **RESUELTO** (renderMarkdownWithTooltips + exec summary en Dashboard tab) |

---

## PRÓXIMAS TAREAS — ARQUITECTURA v1.0 (PEIRS + SENTINEL)

### Fase v0.4.0 — Fundación de datos (próxima sesión)
- [ ] Escalar a 38 países (batch processing en /api/dashboard)
- [ ] SQLite como capa de persistencia primaria (reemplaza JSON files)
- [ ] Endpoint /api/countries con lista completa

### Fase v0.5.0 — SENTINEL: Monitoreo en tiempo real
- [ ] Módulo `sentinel/calendar.py` — calendario electoral global (próximas 90 días)
- [ ] Módulo `sentinel/osint_feeds.py` — scraping de noticias/ONG por elección activa
- [ ] Endpoint /api/sentinel/alerts — lista de alertas por país en tiempo real
- [ ] Frontend: tab "🔴 Sentinel" en la barra de navegación principal

### Fase v0.6.0 — MOE: Misiones de Observación Electoral
- [ ] Endpoint /api/moe/brief/{run_id} — genera brief de misión en markdown
- [ ] Brief incluye: contexto riesgo, marco legal aplicable, áreas de observación prioritarias
- [ ] Frontend: botón "Generar Brief MOE" en DetailView

### Fase v0.7.0 — Agente de Mejora Continua
- [ ] Script `agents/improvement_agent.py` — diagnóstica el sistema semanalmente
- [ ] Genera IMPROVEMENT_REPORT_YYYYMMDD.md en /docs/improvements/
- [ ] Propone mejoras priorizadas con justificación técnica

### Fase v1.0 — Plataforma integrada
- [ ] PEIRS (histórico) + SENTINEL (tiempo real) corriendo en paralelo
- [ ] Dashboard unificado: KPIs + mapa + alertas + tendencias
- [ ] Informes VIP + MOE brief + estadísticas comparativas

---

## INICIO DE SESIÓN
```powershell
cd D:\DemocracIA
.\actualizar.ps1
.\iniciar_backend.ps1   # ventana 1
.\iniciar_frontend.ps1  # ventana 2
# Verificar: [V-Dem] ✅ [FH] ✅ [PEI] ✅
# Llamar /api/dashboard PRIMERO para poblar reports_store
```
