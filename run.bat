@echo off
:: DEMOCRAC.IA — Script de arranque (Windows)
:: Ejecutar desde D:\DemocracIA: run.bat
::
:: Opciones:
::   run.bat          -> levanta backend + abre browser
::   run.bat backend  -> solo backend (http://localhost:8000)
::   run.bat frontend -> solo frontend (http://localhost:5173)
::   run.bat test     -> corre tests
::   run.bat architect -> corre Expert Architect Agent (audit)

chcp 65001 > nul
set PYTHONIOENCODING=utf-8

set MODE=%1
if "%MODE%"=="" set MODE=backend

if "%MODE%"=="backend" goto backend
if "%MODE%"=="frontend" goto frontend
if "%MODE%"=="test" goto test
if "%MODE%"=="architect" goto architect
goto backend

:backend
echo.
echo  DEMOCRAC.IA -- Backend
echo  http://localhost:8000
echo  http://localhost:8000/docs (Swagger)
echo.
cd /d "%~dp0backend"
venv\Scripts\uvicorn app:app --reload --port 8000
goto end

:frontend
echo.
echo  DEMOCRAC.IA -- Frontend
echo  http://localhost:5173
echo.
cd /d "%~dp0frontend"
npm run dev
goto end

:test
echo.
echo  DEMOCRAC.IA -- Tests
echo.
cd /d "%~dp0backend"
venv\Scripts\python -m pytest tests/ -v --tb=short
goto end

:architect
echo.
echo  DEMOCRAC.IA -- Expert Architect Agent (audit)
echo.
cd /d "%~dp0backend"
venv\Scripts\python -m agents.architect --task audit
goto end

:end
