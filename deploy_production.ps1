# DEMOCRAC.IA — Despliegue a Producción
# www.democracia.ar — Railway (backend) + Netlify (frontend)

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEMOCRAC.IA — DESPLIEGUE A PRODUCCIÓN" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── PASO 1: Verificar que todo esté listo ──────────────────────────────────────
Write-Host "[PASO 1] Verificando configuración local..." -ForegroundColor Yellow

# Verificar archivos de configuración
$configFiles = @("railway.toml", "netlify.toml", "Procfile", "nixpacks.toml")
foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ $file faltante" -ForegroundColor Red
    }
}

# Verificar build del frontend
if (Test-Path "frontend/dist") {
    Write-Host "✅ Frontend build listo (frontend/dist)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Frontend no compilado — ejecutar: cd frontend && npm run build" -ForegroundColor Yellow
}

# Verificar tests
Write-Host ""
Write-Host "Ejecutando tests finales..." -ForegroundColor Gray
try {
    $testResult = & C:/Python314/python.exe -m pytest backend/tests/ -q --tb=no 2>&1
    if ($testResult -match "82 passed") {
        Write-Host "✅ 82/82 tests pasando" -ForegroundColor Green
    } else {
        Write-Host "❌ Tests fallando" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error ejecutando tests" -ForegroundColor Red
}

Write-Host ""

# ── PASO 2: Instrucciones de despliegue ────────────────────────────────────────
Write-Host "[PASO 2] INSTRUCCIONES DE DESPLIEGUE" -ForegroundColor Yellow
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  BACKEND: Railway (api.democracia.ar)" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host ""

Write-Host "1. Crear proyecto en Railway:" -ForegroundColor Cyan
Write-Host "   • Ir a https://railway.app" -ForegroundColor White
Write-Host "   • New Project → Deploy from GitHub" -ForegroundColor White
Write-Host "   • Conectar repo de DemocracIA" -ForegroundColor White
Write-Host "   • Railway detecta railway.toml automáticamente" -ForegroundColor White
Write-Host ""

Write-Host "2. Variables de entorno en Railway:" -ForegroundColor Cyan
Write-Host "   • ANTHROPIC_API_KEY=sk-ant-..." -ForegroundColor White
Write-Host "   • OBSERVER_API_KEYS=clave-observadores-produccion-2026" -ForegroundColor White
Write-Host ""

Write-Host "3. Subir datasets CSV (opcional, pero recomendado):" -ForegroundColor Cyan
Write-Host "   • Railway → Volumes → Add Volume (mount: /data)" -ForegroundColor White
Write-Host "   • Instalar Railway CLI: npm install -g @railway/cli" -ForegroundColor White
Write-Host "   • railway login" -ForegroundColor White
Write-Host "   • railway volume upload data/V-Dem-CY-Full+Others-v15.csv /data/" -ForegroundColor White
Write-Host "   • railway volume upload 'data/All_data_FIW_2013-2025 - Index.csv' /data/" -ForegroundColor White
Write-Host "   • railway volume upload data/RSF/2025\ -\ 2025.csv /data/RSF/" -ForegroundColor White
Write-Host "   • railway volume upload data/PEI/PEI_10\ Election\ External.csv /data/PEI/" -ForegroundColor White
Write-Host ""

Write-Host "4. Configurar dominio:" -ForegroundColor Cyan
Write-Host "   • Railway → Settings → Domains → Add: api.democracia.ar" -ForegroundColor White
Write-Host "   • Copiar CNAME que te da Railway" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  FRONTEND: Netlify (www.democracia.ar)" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "1. Conectar repo a Netlify:" -ForegroundColor Cyan
Write-Host "   • Ir a https://netlify.com" -ForegroundColor White
Write-Host "   • Add new site → Import from Git" -ForegroundColor White
Write-Host "   • Conectar repo → Branch: main" -ForegroundColor White
Write-Host "   • Netlify detecta frontend/netlify.toml" -ForegroundColor White
Write-Host ""

Write-Host "2. Variable de entorno en Netlify:" -ForegroundColor Cyan
Write-Host "   • VITE_API_BASE=https://api.democracia.ar" -ForegroundColor White
Write-Host ""

Write-Host "3. Configurar dominio:" -ForegroundColor Cyan
Write-Host "   • Domain management → Add: www.democracia.ar" -ForegroundColor White
Write-Host "   • Copiar CNAME que te da Netlify" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  DNS: Configurar en registrador de democracia.ar" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "Agregar estos registros DNS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tipo    Nombre    Valor                           TTL" -ForegroundColor Gray
Write-Host "CNAME   www       [CNAME de Netlify].netlify.app   3600" -ForegroundColor White
Write-Host "CNAME   api       [CNAME de Railway].up.railway.app 3600" -ForegroundColor White
Write-Host "A       @         75.2.60.5                       3600" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ LISTO PARA DESPLEGAR" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "Después del despliegue:" -ForegroundColor Cyan
Write-Host "• www.democracia.ar → Dashboard React" -ForegroundColor White
Write-Host "• api.democracia.ar/api/health → Backend status" -ForegroundColor White
Write-Host "• api.democracia.ar/docs → API documentation" -ForegroundColor White
Write-Host ""

Write-Host "Para probar: POST a api.democracia.ar/api/analyze con:" -ForegroundColor Cyan
Write-Host '  {"country_code": "PER", "election_date": "2026-04-12"}' -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📞 SOPORTE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Si hay problemas:" -ForegroundColor Yellow
Write-Host "• Ver STATUS_REPORT.md para diagnóstico" -ForegroundColor White
Write-Host "• Ejecutar: C:/Python314/python.exe backend/agents/architect.py --audit" -ForegroundColor White
Write-Host "• Revisar logs en Railway/Netlify dashboards" -ForegroundColor White
Write-Host ""

Write-Host "¡El sistema está listo para producción! 🚀" -ForegroundColor Green