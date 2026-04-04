@echo off
REM DEMOCRAC.IA Full Stack Startup Script (Batch version for Windows)
REM Arranca backend + frontend en el orden correcto

setlocal enabledelayedexpansion

echo.
echo =====================================
echo DEMOCRAC.IA / PEIRS — Full Stack
echo =====================================
echo.

REM ── 1. Check Node.js ────────────────────────────────────────────────────────
echo [1/3] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Node.js not found in PATH
    echo Please install Node.js 18+ from: https://nodejs.org/
    echo Then restart your terminal.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
for /f "tokens=*" %%i in ('npm --version') do set NPM_VER=%%i

echo [OK] Node.js: %NODE_VER%
echo [OK] npm: %NPM_VER%
echo.

REM ── 2. Start Backend ────────────────────────────────────────────────────────
echo [2/3] Starting Backend (FastAPI)...
echo       Port: http://localhost:8000
echo.

cd backend
start "DEMOCRAC.IA Backend" cmd /k C:\Python314\python.exe -m uvicorn app:app --reload --port 8000
cd ..

timeout /t 3 /nobreak
echo [OK] Backend started
echo.

REM ── 3. Start Frontend ────────────────────────────────────────────────────────
echo [3/3] Starting Frontend (React/Vite)...
echo       Port: http://localhost:5173
echo.

cd frontend
call npm run dev
cd ..
