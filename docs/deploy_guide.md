# DEMOCRAC.IA — Guía de Deploy a Producción
## www.democracia.ar — Railway (backend) + Netlify (frontend)

---

## ARQUITECTURA DE PRODUCCIÓN

```
www.democracia.ar          → Netlify (frontend React estático)
api.democracia.ar          → Railway (backend FastAPI + SQLite)
```

---

## PASO 1: BACKEND EN RAILWAY

### 1.1 Crear proyecto en Railway
1. Ir a https://railway.app → New Project → Deploy from GitHub
2. Conectar el repo de DemocracIA
3. Railway detecta `railway.toml` automáticamente

### 1.2 Configurar Variables de Entorno en Railway
En el panel de Railway → Variables, agregar:

```
ANTHROPIC_API_KEY=sk-ant-...
OBSERVER_API_KEYS=clave-observadores-produccion-2026
```

### 1.3 Volumen persistente para el CSV de V-Dem (384MB)
El CSV de V-Dem no puede ir a GitHub (demasiado grande).
Opciones:

**Opción A — Volume en Railway (recomendado):**
1. Railway → tu servicio → Volumes → Add Volume → Mount path: `/data`
2. Subir el CSV via Railway CLI:
   ```bash
   npm install -g @railway/cli
   railway login
   railway volume upload data/V-Dem-CY-Full+Others-v15.csv /data/
   railway volume upload "data/All_data_FIW_2013-2025 - Index.csv" /data/
   railway volume upload data/RSF/2025\ -\ 2025.csv /data/RSF/
   railway volume upload data/PEI/PEI_10\ Election\ External.csv /data/PEI/
   ```
3. Agregar variable de entorno:
   ```
   VDEM_CSV_PATH=/data/V-Dem-CY-Full+Others-v15.csv
   FH_CSV_PATH=/data/All_data_FIW_2013-2025 - Index.csv
   RSF_CSV_PATH=/data/RSF/2025 - 2025.csv
   PEI_CSV_PATH=/data/PEI/PEI_10 Election External.csv
   ```

**Opción B — Sin CSV (solo datos mock):**
No subir los CSV. El sistema corre con datos mock hasta que se suban los datasets.
El informe seguirá generándose, con datos menos precisos.

### 1.4 Dominio personalizado en Railway
1. Railway → tu servicio → Settings → Domains → Add Custom Domain
2. Ingresar: `api.democracia.ar`
3. Railway te da un CNAME: `xxx.railway.app`

---

## PASO 2: FRONTEND EN NETLIFY

### 2.1 Conectar repo a Netlify
1. Ir a https://netlify.com → Add new site → Import from Git
2. Conectar repo → Branch: `main`
3. Netlify detecta `frontend/netlify.toml` automáticamente:
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`

### 2.2 Variable de entorno en Netlify
En Netlify → Site settings → Environment variables:
```
VITE_API_BASE=https://api.democracia.ar
```

### 2.3 Dominio personalizado en Netlify
1. Netlify → Domain management → Add custom domain
2. Ingresar: `www.democracia.ar`
3. Netlify te da un CNAME: `xxx.netlify.app`

---

## PASO 3: CONFIGURAR DNS EN democracia.ar

Entrar al panel de tu registrador de dominio (donde compraste democracia.ar).
Agregar estos registros DNS:

```
Tipo    Nombre    Valor                           TTL
CNAME   www       xxx.netlify.app.                3600
CNAME   api       xxx.up.railway.app.             3600
A       @         75.2.60.5                       3600   ← IP de Netlify para apex
```

> **Nota:** El registro `A` para `@` (democracia.ar sin www) apunta a Netlify
> para que `democracia.ar` redirija a `www.democracia.ar`.
> Netlify maneja SSL automáticamente (Let's Encrypt).

### Verificar propagación DNS
```bash
nslookup www.democracia.ar
nslookup api.democracia.ar
```
La propagación DNS tarda entre 15 minutos y 48 horas.

---

## PASO 4: CORS en producción

El backend debe aceptar requests de `www.democracia.ar`.
En `backend/app.py`, la línea:
```python
allow_origins=["*"]
```
ya acepta cualquier origen. Para producción segura, cambiar a:
```python
allow_origins=[
    "https://www.democracia.ar",
    "https://democracia.ar",
    "http://localhost:5173",   # dev local
]
```
Agregar como variable de entorno:
```
ALLOWED_ORIGINS=https://www.democracia.ar,https://democracia.ar
```

---

## VERIFICACIÓN FINAL

```bash
# Backend
curl https://api.democracia.ar/api/health

# Frontend
curl https://www.democracia.ar
```

---

## COSTOS ESTIMADOS

| Servicio  | Plan          | Costo          |
|-----------|---------------|----------------|
| Railway   | Hobby ($5 crédito/mes gratis) | $0–$10/mes |
| Netlify   | Free tier     | $0/mes         |
| Anthropic | API por uso   | ~$0.01/reporte |
| Dominio   | Ya tenés democracia.ar | $0 adicional |

**Total estimado: $5–15 USD/mes** dependiendo del tráfico.
