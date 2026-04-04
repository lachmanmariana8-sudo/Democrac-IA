# DEMOCRAC.IA Full Stack Startup Script
# Arranca backend + frontend en el orden correcto

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "DEMOCRAC.IA / PEIRS — Full Stack" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Check Node.js ────────────────────────────────────────────────────────
Write-Host "[1/3] Checking Node.js..." -ForegroundColor Yellow
$node_check = node --version 2>&1
$npm_check = npm --version 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js not found in PATH" -ForegroundColor Red
    Write-Host "   Please install Node.js 18+ from: https://nodejs.org/" -ForegroundColor Red
    Write-Host "   Then restart your terminal." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Node.js: $node_check" -ForegroundColor Green
Write-Host "✅ npm: $npm_check" -ForegroundColor Green
Write-Host ""

# ── 2. Start Backend ────────────────────────────────────────────────────────
Write-Host "[2/3] Starting Backend (FastAPI)..." -ForegroundColor Yellow
Write-Host "      Port: http://localhost:8000" -ForegroundColor Gray

Push-Location backend
Start-Process powershell -ArgumentList "C:/Python314/python.exe -m uvicorn app:app --reload --port 8000" -NoNewWindow
Pop-Location

Start-Sleep -Seconds 3
Write-Host "✅ Backend started (check http://localhost:8000/api/health)" -ForegroundColor Green
Write-Host ""

# ── 3. Start Frontend ────────────────────────────────────────────────────────
Write-Host "[3/3] Starting Frontend (React/Vite)..." -ForegroundColor Yellow
Write-Host "      Port: http://localhost:5173" -ForegroundColor Gray

Push-Location frontend
npm run dev
Pop-Location
