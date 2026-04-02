"""
DEMOCRAC.IA — Hunter Production Run
Inicia sesión de observación para PER y ejecuta el Hunter.
Uso: python run_hunter.py [--dry-run]
"""
import asyncio
import json
import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── Cargar .env manualmente ───────────────────────────────────────────────────
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import httpx

BASE_URL        = "http://localhost:8000"
RUN_ID          = "ad925532-b264-4af6-9509-9125dd788ce5"   # último reporte PER
OBSERVER_KEY    = os.environ.get("OBSERVER_API_KEY", "democracia-obs-dev-2026")
DRY_RUN         = "--dry-run" in sys.argv

OBS_HEADERS = {
    "Content-Type": "application/json",
    "X-Observer-Key": OBSERVER_KEY,
}

async def main():
    async with httpx.AsyncClient(timeout=180) as client:

        # ── 1. Verificar backend ──────────────────────────────────────────────
        print("▶ Verificando backend...")
        try:
            r = await client.get(f"{BASE_URL}/api/health")
            r.raise_for_status()
            print(f"  ✓ Backend OK — {r.json().get('status', 'ok')}\n")
        except Exception as e:
            print(f"  ✗ Backend no disponible: {e}")
            print("    Levantá el backend: cd backend && uvicorn app:app --reload --port 8000")
            return

        # ── 2. Iniciar sesión de observación ──────────────────────────────────
        print("▶ Iniciando sesión de observación para PER...")
        payload_obs = {
            "run_id":       RUN_ID,
            "mission_name": "Observación Electoral Perú 2026 — DEMOCRAC.IA",
            "lead_org":     "DEMOCRAC.IA / PEIRS",
        }
        r = await client.post(
            f"{BASE_URL}/api/observation/PER/start",
            json=payload_obs,
            headers=OBS_HEADERS,
        )
        if r.status_code in (200, 201):
            obs = r.json()
            session_id = obs.get("session_id", "?")
            phase      = obs.get("phase", "?")
            print(f"  ✓ Sesión iniciada: {session_id}")
            print(f"  ✓ Fase activa: {phase}\n")
        elif r.status_code == 409:
            print("  ✓ Sesión ya activa (409) — continuando con la existente\n")
        else:
            print(f"  ✗ Error al iniciar sesión: {r.status_code} — {r.text}")
            return

        # ── 3. Ejecutar Hunter ────────────────────────────────────────────────
        mode = "DRY-RUN" if DRY_RUN else "PRODUCCIÓN"
        print(f"▶ Ejecutando Hunter ({mode})...")
        print("  (puede tardar 30-60 seg — fetches RSS + clasificación LLM)\n")

        payload_hunter = {
            "run_id":               RUN_ID,
            "dry_run":              DRY_RUN,
            "max_items_per_source": 20,
        }
        r = await client.post(
            f"{BASE_URL}/api/hunter/PER/run",
            json=payload_hunter,
        )

        if r.status_code != 200:
            print(f"  ✗ Error Hunter: {r.status_code} — {r.text}")
            return

        result = r.json()

        # ── 4. Mostrar resumen ────────────────────────────────────────────────
        print("═" * 60)
        print("  RESULTADO DEL HUNTER")
        print("═" * 60)
        print(f"  Fase:              {result.get('phase', '?')}")
        print(f"  Fuentes fetched:   {', '.join(result.get('sources_fetched', [])) or 'ninguna'}")
        print(f"  Ítems fetched:     {result.get('items_fetched', 0)}")
        print(f"  Ítems clasificados:{result.get('items_classified', 0)}")
        print(f"  Hallazgos relevantes: {result.get('relevant_entries', 0)}")
        print(f"  OONI entradas:     {result.get('ooni_entries', 0)}")

        errors = result.get("errors", [])
        if errors:
            print(f"\n  Errores ({len(errors)}):")
            for e in errors:
                print(f"    • {e}")

        entries = result.get("entries_preview", [])
        if entries:
            print(f"\n  Primeros hallazgos ({len(entries)}):")
            for i, e in enumerate(entries, 1):
                sev = e.get("severity", "?").upper()
                cat = e.get("category", "?")
                src = e.get("source", "?")
                finding = e.get("finding", "")[:120]
                print(f"\n  [{i}] [{sev}] {cat} (fuente: {src})")
                print(f"      {finding}")
                if e.get("evidence_ref"):
                    print(f"      URL: {e['evidence_ref']}")
        else:
            print("\n  (Sin hallazgos relevantes en este ciclo)")

        if not DRY_RUN and result.get("relevant_entries", 0) > 0:
            print(f"\n  ✓ Hallazgos registrados en Cap. 7 del informe")
            print(f"  ✓ Informe actualizado: {RUN_ID}")

        print("\n" + "═" * 60)

asyncio.run(main())
