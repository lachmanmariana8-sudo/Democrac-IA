"""
DEMOCRAC.IA / PEIRS — Expert Architect Agent
Meta-agente de mejora continua: audita, prioriza, implementa y verifica mejoras
al sistema de forma autónoma. Usa claude-agent-sdk con acceso completo al codebase.

Uso CLI:
    python -m backend.agents.architect                   # ciclo completo
    python -m backend.agents.architect --task audit      # solo auditoría
    python -m backend.agents.architect --task improve    # mejora específica
    python -m backend.agents.architect --task test       # correr tests
    python -m backend.agents.architect --task "describe tu tarea aquí"

Uso programático:
    from agents.architect import run_architect, ArchitectTask
    await run_architect(ArchitectTask.AUDIT)
"""
from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

# ── System prompt del Agente Experto Arquitecto ───────────────────────────────
ARCHITECT_SYSTEM_PROMPT = """
Eres el CTO, Arquitecto Principal y Especialista en Integridad Electoral de DEMOCRAC.IA (PEIRS — Predictive Electoral Integrity & Risk System). Combinas tres áreas de expertise:

## 1. EXPERTISE TÉCNICA (Full-Stack & IA)

Eres experto en: Python, FastAPI, LangGraph, LangChain, React, SQLite, ChromaDB,
arquitectura de agentes IA, scraping OSINT, y sistemas RAG.

Tu rol técnico:
- Diseñas y construyes la plataforma de punta a punta
- Tomas decisiones de arquitectura justificadas, nunca arbitrarias
- Implementas mejora continua: cada iteración debe ser mejor que la anterior
- Documentas todo cambio con su razón técnica
- Propones proactivamente mejoras sin esperar a que te las pidan
- NUNCA rompes funcionalidad existente — siempre verificas antes de modificar

## 2. EXPERTISE EN DEMOCRACIA Y OBSERVACIÓN ELECTORAL

Conoces en profundidad:
- ICCPR Art. 25 (derecho al voto), Art. 19 (expresión), Art. 21 (reunión)
- CADH Art. 23, CEDAW Art. 7-8, CRPD Art. 29, UNDRIP Art. 5/18
- Metodologías MOE-UE, OSCE/ODIHR, Centro Carter (EOS)
- Principios: No legitimación, evidencia empírica, trazabilidad, contextualización

## 3. CICLO DE MEJORA CONTINUA

Operas bajo este ciclo estricto:
1. EVALUAR — Diagnóstica el estado actual leyendo el código
2. PRIORIZAR — Identifica el cambio de mayor impacto (ROI técnico)
3. IMPLEMENTAR — Construye con calidad de producción
4. VERIFICAR — Corre tests, verifica imports, asegura que nada se rompe
5. DOCUMENTAR — Registra qué se hizo y por qué en el commit
6. PROPONER — Sugiere el siguiente paso lógico

## REGLAS ABSOLUTAS

1. Leer SIEMPRE antes de editar — nunca modificar código que no has leído
2. Fallbacks graciosos — toda nueva funcionalidad tiene fallback si falla
3. Sin romper backwards compatibility — imports existentes en app.py deben seguir funcionando
4. Tests primero — si agregas código nuevo, agrega su test
5. Commits atómicos — un cambio lógico por commit, mensaje descriptivo
6. Trazabilidad — cada dato tiene fuente, timestamp, nivel de confianza
7. No usar "libre y justa" — anclar análisis a obligaciones legales específicas

## ARQUITECTURA ACTUAL (resumen)

```
backend/
├── app.py              ← FastAPI + LangGraph pipeline (monolito en migración)
├── agents/             ← Módulos de agentes IA (en extracción)
│   ├── architect.py   ← (este archivo) Meta-agente de mejora continua
│   └── pipeline.py    ← build_workflow() LangGraph (pendiente)
├── chapters/           ← Generadores de capítulos (pendiente extracción)
├── modules/            ← Lógica de dominio refactorizada
│   ├── config.py      ← Env vars, constantes LLM, metadatos datasets
│   ├── data_loaders.py ← V-Dem, FH, RSF, PEI loaders
│   ├── instruments.py ← Instrumentos legales internacionales
│   ├── catalog.py     ← Catálogo de 41 países
│   ├── peru_data.py   ← Datos electorales Perú 2026
│   ├── field_validator.py  ← Agent 5: validación observadores
│   └── fraud_hate_analysis.py ← Análisis fraude y discurso odio
├── integrations/
│   ├── ooni.py        ← Detección censura web (OONI API)
│   └── alerts.py      ← Agent 7: Slack/webhook/SMTP
├── rag/               ← RAG legal (ChromaDB + 60+ docs ICCPR/CADH/CEDAW)
├── db/                ← Persistencia SQLite
├── tests/             ← Test suite pytest
└── startup_checks.py  ← Health checks al iniciar
```

## ESTADO DE MIGRACIÓN (al 2026-03-27)
✅ Completado: modules/ (config, data_loaders, instruments, catalog, peru_data, field_validator, fraud_hate_analysis)
✅ Completado: integrations/ (ooni, alerts)
✅ Completado: rag/ (corpus, indexer, retriever)
✅ Completado: db/ (schema, crud)
✅ Completado: startup_checks.py
✅ Completado: tests/ (test_db, test_field_validator, test_config_and_modules, test_data_loaders)
⏳ En progreso: agents/pipeline.py, agents/nodes.py, chapters/generators.py
❌ Pendiente: integrar db/ en app.py, integrar startup_checks en app.py

Cuando termines una tarea, reporta:
- Qué hiciste
- Por qué (justificación técnica)
- Qué tests agregaste o verificaste
- Próximo paso recomendado
"""

# ── Prompts por tipo de tarea ──────────────────────────────────────────────────

TASK_PROMPTS = {
    "audit": """
Realiza una auditoría completa del proyecto DEMOCRAC.IA en d:/DemocracIA/backend/.

Sigue el ciclo de mejora continua:

1. EVALUAR: Lee y analiza:
   - Todos los archivos en backend/modules/, backend/agents/, backend/chapters/, backend/db/, backend/tests/
   - Los últimos cambios en git (git log --oneline -20)
   - El estado de backend/modules/__init__.py (tracking de migración)
   - Corre los tests: cd backend && python -m pytest tests/ -v --tb=short 2>&1 | head -100

2. DIAGNOSTICA:
   - ¿Qué tests pasan y cuáles fallan?
   - ¿Hay imports rotos?
   - ¿Hay código duplicado entre app.py y los módulos nuevos?
   - ¿Falta algún módulo crítico?

3. PRIORIZA: Lista los 3-5 problemas más importantes ordenados por impacto

4. REPORTA con formato:
   ## Estado General: [VERDE/AMARILLO/ROJO]
   ## Tests: X/Y pasando
   ## Issues Críticos: (lista)
   ## Oportunidades de Mejora: (lista priorizada)
   ## Próximo Paso Recomendado: (1 acción concreta)
""",

    "improve": """
Identifica y ejecuta la mejora de mayor impacto al proyecto DEMOCRAC.IA.

Proceso:
1. Lee el estado actual de los módulos
2. Corre los tests para identificar lo que está roto: cd backend && python -m pytest tests/ -v --tb=short
3. Si hay tests fallando: arregla el problema más crítico primero
4. Si todos los tests pasan: identifica la siguiente mejora de mayor ROI técnico
5. Implementa la mejora con calidad de producción
6. Verifica que los tests siguen pasando
7. Haz commit con mensaje descriptivo

Restricciones:
- NO romper imports existentes en app.py
- Todo código nuevo necesita tests
- Mantener fallbacks graciosos
""",

    "test": """
Corre la suite de tests completa y reporta el estado.

Comandos a ejecutar en backend/:
1. python -m pytest tests/ -v --tb=short
2. Si hay failures: python -m pytest tests/test_db.py -v --tb=long (el más crítico primero)
3. Reporta: cuántos tests pasan, cuáles fallan, con qué error

Si hay tests fallando, diagnostica la causa raíz e implementa el fix.
""",

    "integrate_db": """
Integra el módulo db/ en app.py para persistir análisis y reportes.

Tareas:
1. Lee backend/app.py líneas 1-150 (imports y config)
2. Lee backend/db/__init__.py y backend/db/crud.py
3. Agrega importación condicional de db en app.py:
   ```python
   try:
       from db import init_db, create_run, complete_run, save_report, create_session, save_entry, save_alert
       DB_AVAILABLE = True
   except ImportError:
       DB_AVAILABLE = False
   ```
4. Llama init_db() durante el startup de FastAPI (evento @app.on_event("startup"))
5. En el endpoint POST /api/analyze: llama create_run() al inicio y complete_run() al final
6. En POST /api/observation/*/entry: llama save_entry() tras validar
7. Verifica que nada se rompe: python -m pytest tests/test_db.py -v
8. Haz commit
""",

    "integrate_startup": """
Integra startup_checks.py en app.py para que se ejecute al arrancar.

Tareas:
1. Lee backend/app.py buscando el bloque de inicialización (líneas ~1-150)
2. Lee backend/startup_checks.py
3. Agrega al inicio de app.py (después de imports):
   ```python
   try:
       from startup_checks import run_startup_checks
       _startup_report = run_startup_checks(raise_on_critical=False)
   except ImportError:
       print("[STARTUP] startup_checks.py no encontrado — continuando sin validación")
   ```
4. Verifica que el servidor sigue levantando: python -c "import app; print('OK')"
5. Haz commit
""",
}


class ArchitectTask(str, Enum):
    AUDIT = "audit"
    IMPROVE = "improve"
    TEST = "test"
    INTEGRATE_DB = "integrate_db"
    INTEGRATE_STARTUP = "integrate_startup"
    CUSTOM = "custom"


# ── Función principal ──────────────────────────────────────────────────────────

async def run_architect(
    task: str = "audit",
    cwd: str = "d:/DemocracIA",
    max_turns: int = 40,
    verbose: bool = True,
) -> str:
    """
    Ejecuta el Expert Architect Agent con la tarea indicada.

    Args:
        task: Nombre de tarea predefinida o prompt personalizado
        cwd: Directorio de trabajo del proyecto
        max_turns: Máximo de turnos del agente
        verbose: Imprimir progreso en tiempo real

    Returns:
        Resultado final del agente como string
    """
    try:
        from claude_agent_sdk import (
            query, ClaudeAgentOptions,
            ResultMessage, SystemMessage, AssistantMessage, TextBlock,
        )
    except ImportError:
        raise ImportError(
            "claude-agent-sdk no instalado. Instala con: pip install claude-agent-sdk"
        )

    # Obtener el prompt de la tarea
    prompt = TASK_PROMPTS.get(task, task)  # Si no es predefinida, usar como prompt custom

    start_time = datetime.now(timezone.utc)
    sep = "=" * 60
    if verbose:
        print(f"\n{sep}")
        print(f"  [ARCHITECT] Expert Architect Agent -- Tarea: {task}")
        print(f"  [DIR]       {cwd}")
        print(f"  [INICIO]    {start_time.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"{sep}\n")

    result_text = ""
    session_id = None

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=cwd,
            allowed_tools=["Read", "Glob", "Grep", "Edit", "Write", "Bash"],
            permission_mode="acceptEdits",
            system_prompt=ARCHITECT_SYSTEM_PROMPT,
            max_turns=max_turns,
            model="claude-opus-4-7",
        )
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            session_id = message.data.get("session_id")
            if verbose:
                print(f"  [SESSION]   {session_id}\n")

        elif isinstance(message, AssistantMessage) and verbose:
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    print(block.text)

        elif isinstance(message, ResultMessage):
            result_text = message.result
            if verbose:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                print(f"\n{sep}")
                print(f"  [OK] Completado en {elapsed:.1f}s")
                print(f"{sep}\n")

    # Guardar log de la sesión
    _save_architect_log(task, result_text, session_id, start_time, cwd)

    return result_text


def _save_architect_log(
    task: str,
    result: str,
    session_id: Optional[str],
    start_time: datetime,
    cwd: str,
) -> None:
    """Guarda un log de la ejecución del arquitecto."""
    log_dir = Path(cwd) / "data" / "architect_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"architect_{task}_{timestamp}.json"

    log_data = {
        "task": task,
        "session_id": session_id,
        "started_at": start_time.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "result_preview": result[:500] if result else "",
    }

    try:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # Log es best-effort, no crítico


# ── FastAPI endpoint (para disparar desde la API) ─────────────────────────────

def get_architect_router():
    """
    Retorna un APIRouter de FastAPI con endpoints del Architect Agent.
    Importar en app.py:
        from agents.architect import get_architect_router
        app.include_router(get_architect_router(), prefix="/api/architect")
    """
    try:
        from fastapi import APIRouter, BackgroundTasks, HTTPException
        from pydantic import BaseModel
    except ImportError:
        return None

    router = APIRouter(tags=["Architect Agent"])

    class ArchitectRequest(BaseModel):
        task: str = "audit"
        max_turns: int = 30

    _running_tasks: dict = {}

    @router.post("/run")
    async def run_architect_endpoint(
        req: ArchitectRequest,
        background_tasks: BackgroundTasks,
    ):
        """
        Dispara el Expert Architect Agent en background.
        Tasks predefinidas: audit, improve, test, integrate_db, integrate_startup
        """
        task_id = f"{req.task}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

        async def _run():
            try:
                _running_tasks[task_id] = {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}
                result = await run_architect(req.task, max_turns=req.max_turns, verbose=False)
                _running_tasks[task_id] = {
                    "status": "completed",
                    "result": result[:1000],
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as e:
                _running_tasks[task_id] = {"status": "failed", "error": str(e)}

        background_tasks.add_task(_run)
        return {"task_id": task_id, "status": "started", "task": req.task}

    @router.get("/status/{task_id}")
    async def get_task_status(task_id: str):
        if task_id not in _running_tasks:
            raise HTTPException(404, f"Task '{task_id}' no encontrada")
        return _running_tasks[task_id]

    @router.get("/logs")
    async def list_architect_logs():
        log_dir = Path("../data/architect_logs")
        if not log_dir.exists():
            return {"logs": []}
        logs = sorted(log_dir.glob("*.json"), reverse=True)[:20]
        result = []
        for log in logs:
            try:
                import json
                with open(log) as f:
                    result.append(json.load(f))
            except Exception:
                pass
        return {"logs": result}

    return router


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="DEMOCRAC.IA — Expert Architect Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tareas predefinidas:
  audit            Auditoría completa del sistema
  improve          Ejecuta la mejora de mayor impacto
  test             Corre tests y arregla failures
  integrate_db     Integra db/ en app.py
  integrate_startup  Integra startup_checks en app.py

Ejemplo de tarea personalizada:
  python -m backend.agents.architect --task "Agrega endpoint GET /api/stats que retorne get_db_stats()"
        """
    )
    parser.add_argument(
        "--task", default="audit",
        help="Tarea predefinida o prompt personalizado (default: audit)"
    )
    parser.add_argument(
        "--cwd", default="d:/DemocracIA",
        help="Directorio del proyecto (default: d:/DemocracIA)"
    )
    parser.add_argument(
        "--max-turns", type=int, default=40,
        help="Máximo de turnos del agente (default: 40)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suprimir output detallado del agente"
    )
    args = parser.parse_args()

    result = asyncio.run(run_architect(
        task=args.task,
        cwd=args.cwd,
        max_turns=args.max_turns,
        verbose=not args.quiet,
    ))

    if args.quiet:
        print(result)


if __name__ == "__main__":
    main()
