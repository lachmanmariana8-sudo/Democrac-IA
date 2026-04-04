# DEMOCRAC.IA — Verificación Post-Despliegue
# Verificar que www.democracia.ar y api.democracia.ar funcionan

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEMOCRAC.IA — VERIFICACIÓN POST-DESPLIEGUE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── Verificar DNS ─────────────────────────────────────────────────────────────
Write-Host "[1] Verificando DNS..." -ForegroundColor Yellow

try {
    $www_ip = Resolve-DnsName www.democracia.ar -Type A 2>$null | Select-Object -ExpandProperty IPAddress
    Write-Host "✅ www.democracia.ar → $www_ip" -ForegroundColor Green
} catch {
    Write-Host "❌ www.democracia.ar no resuelve" -ForegroundColor Red
}

try {
    $api_cname = Resolve-DnsName api.democracia.ar -Type CNAME 2>$null | Select-Object -ExpandProperty NameHost
    Write-Host "✅ api.democracia.ar → $api_cname" -ForegroundColor Green
} catch {
    Write-Host "❌ api.democracia.ar no resuelve" -ForegroundColor Red
}

Write-Host ""

# ── Verificar servicios ───────────────────────────────────────────────────────
Write-Host "[2] Verificando servicios..." -ForegroundColor Yellow

# Verificar frontend
try {
    $frontend_response = Invoke-WebRequest -Uri "https://www.democracia.ar" -UseBasicParsing -TimeoutSec 10
    if ($frontend_response.StatusCode -eq 200) {
        Write-Host "✅ Frontend: https://www.democracia.ar (HTTP $($frontend_response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Frontend: HTTP $($frontend_response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Frontend no responde" -ForegroundColor Red
}

# Verificar backend
try {
    $backend_response = Invoke-WebRequest -Uri "https://api.democracia.ar/api/health" -UseBasicParsing -TimeoutSec 10
    if ($backend_response.StatusCode -eq 200) {
        $health = $backend_response.Content | ConvertFrom-Json
        Write-Host "✅ Backend: https://api.democracia.ar/api/health" -ForegroundColor Green
        Write-Host "   Status: $($health.status)" -ForegroundColor Gray
        Write-Host "   Version: $($health.version)" -ForegroundColor Gray
        Write-Host "   Countries: $($health.countries_available)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Backend: HTTP $($backend_response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Backend no responde" -ForegroundColor Red
}

Write-Host ""

# ── Verificar API funcionalidad ───────────────────────────────────────────────
Write-Host "[3] Verificando API funcionalidad..." -ForegroundColor Yellow

# Verificar lista de países
try {
    $countries_response = Invoke-WebRequest -Uri "https://api.democracia.ar/api/countries" -UseBasicParsing -TimeoutSec 10
    if ($countries_response.StatusCode -eq 200) {
        $countries = $countries_response.Content | ConvertFrom-Json
        Write-Host "✅ /api/countries: $($countries.Count) países disponibles" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ /api/countries no funciona" -ForegroundColor Red
}

# Verificar análisis (con timeout más largo)
Write-Host ""
Write-Host "Probando análisis de Perú 2026..." -ForegroundColor Gray
try {
    $analysis_body = @{
        country_code = "PER"
        election_date = "2026-04-12"
    } | ConvertTo-Json

    $analysis_response = Invoke-WebRequest -Uri "https://api.democracia.ar/api/analyze" -Method POST -Body $analysis_body -ContentType "application/json" -UseBasicParsing -TimeoutSec 30

    if ($analysis_response.StatusCode -eq 200) {
        $result = $analysis_response.Content | ConvertFrom-Json
        Write-Host "✅ /api/analyze funciona" -ForegroundColor Green
        Write-Host "   Report ID: $($result.id)" -ForegroundColor Gray
        Write-Host "   Status: $($result.status)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  /api/analyze: HTTP $($analysis_response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ /api/analyze no funciona" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# ── Verificar integración frontend-backend ────────────────────────────────────
Write-Host "[4] Verificando integración..." -ForegroundColor Yellow

# Verificar que el frontend puede hacer requests al backend
Write-Host "Para verificar integración completa:" -ForegroundColor Cyan
Write-Host "1. Abrir https://www.democracia.ar en navegador" -ForegroundColor White
Write-Host "2. Seleccionar 'Peru' en el dropdown" -ForegroundColor White
Write-Host "3. Hacer clic en 'Analizar'" -ForegroundColor White
Write-Host "4. Verificar que aparece el reporte" -ForegroundColor White
Write-Host ""

# ── Resumen final ────────────────────────────────────────────────────────────
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  📊 RESUMEN DE VERIFICACIÓN" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "URLs de producción:" -ForegroundColor Cyan
Write-Host "• Dashboard: https://www.democracia.ar" -ForegroundColor White
Write-Host "• API: https://api.democracia.ar" -ForegroundColor White
Write-Host "• API Docs: https://api.democracia.ar/docs" -ForegroundColor White
Write-Host "• Health Check: https://api.democracia.ar/api/health" -ForegroundColor White
Write-Host ""

Write-Host "Si todo está verde ✅, ¡el despliegue fue exitoso!" -ForegroundColor Green
Write-Host ""

Write-Host "Para monitoreo continuo:" -ForegroundColor Cyan
Write-Host "• Railway dashboard para backend logs" -ForegroundColor White
Write-Host "• Netlify dashboard para frontend analytics" -ForegroundColor White
Write-Host "• Ejecutar este script periódicamente" -ForegroundColor White
Write-Host ""

Write-Host "¡www.democracia.ar está vivo! 🎉" -ForegroundColor Green