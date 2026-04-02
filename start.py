"""
DEMOCRAC.IA — Script de arranque unificado
Levanta backend (puerto 8001) y frontend (puerto 5173) en paralelo.

Uso:
    python start.py              # arranque completo
    python start.py --backend    # solo backend
    python start.py --frontend   # solo frontend
    python start.py --stop       # matar todos los procesos
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

BASE_DIR     = Path(__file__).parent
BACKEND_DIR  = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
VENV_PYTHON  = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
VENV_UVICORN = BACKEND_DIR / "venv" / "Scripts" / "uvicorn.exe"
BACKEND_PORT = 8001
FRONTEND_PORT = 5173

processes = []


def _kill_port(port: int):
    """Mata cualquier proceso escuchando en el puerto dado."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True
        )
        pids = set()
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTEN" in line:
                parts = line.split()
                if parts and parts[-1].isdigit() and parts[-1] != "0":
                    pids.add(parts[-1])
        for pid in pids:
            subprocess.run(["taskkill", "/F", "/PID", pid],
                           capture_output=True, text=True)
        if pids:
            print(f"  [stop] Puerto {port}: {len(pids)} proceso(s) terminado(s)")
    except Exception as e:
        print(f"  [warn] No se pudo limpiar puerto {port}: {e}")


def start_backend():
    print(f"[backend] Iniciando en http://localhost:{BACKEND_PORT} ...")
    _kill_port(BACKEND_PORT)
    time.sleep(1)

    if not VENV_UVICORN.exists():
        print(f"  [error] uvicorn no encontrado en {VENV_UVICORN}")
        print("  Ejecuta: cd backend && python -m venv venv && venv/Scripts/pip install -r requirements.txt")
        return None

    env = dict(os.environ)
    env_file = BACKEND_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip())

    proc = subprocess.Popen(
        [str(VENV_UVICORN), "app:app", "--port", str(BACKEND_PORT)],
        cwd=str(BACKEND_DIR),
        env=env,
    )
    return proc


def start_frontend():
    print(f"[frontend] Iniciando en http://localhost:{FRONTEND_PORT} ...")
    _kill_port(FRONTEND_PORT)
    time.sleep(1)

    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    proc = subprocess.Popen(
        [npm, "run", "dev", "--", "--port", str(FRONTEND_PORT)],
        cwd=str(FRONTEND_DIR),
    )
    return proc


def stop_all():
    print("[stop] Deteniendo todos los procesos DEMOCRAC.IA ...")
    _kill_port(BACKEND_PORT)
    _kill_port(FRONTEND_PORT)
    print("[stop] Listo.")


def wait_for_backend(timeout=30):
    """Espera hasta que el backend responda."""
    try:
        import urllib.request
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                urllib.request.urlopen(
                    f"http://localhost:{BACKEND_PORT}/api/health", timeout=2
                )
                return True
            except Exception:
                time.sleep(1)
    except Exception:
        pass
    return False


def main():
    args = sys.argv[1:]
    only_backend  = "--backend"  in args
    only_frontend = "--frontend" in args
    do_stop       = "--stop"     in args

    if do_stop:
        stop_all()
        return

    procs = []

    if not only_frontend:
        p = start_backend()
        if p:
            procs.append(("backend", p))
            print(f"[backend] PID {p.pid} — esperando arranque...")
            if wait_for_backend(30):
                print(f"[backend] Listo: http://localhost:{BACKEND_PORT}")
            else:
                print(f"[backend] Tardando en responder — revisa los logs")

    if not only_backend:
        p = start_frontend()
        if p:
            procs.append(("frontend", p))
            print(f"[frontend] PID {p.pid}")
            time.sleep(3)
            print(f"[frontend] Listo: http://localhost:{FRONTEND_PORT}")

    if not procs:
        print("[error] No se pudo iniciar ningún servicio.")
        return

    print("\n" + "=" * 50)
    print("  DEMOCRAC.IA corriendo")
    print(f"  Backend:  http://localhost:{BACKEND_PORT}")
    print(f"  Frontend: http://localhost:{FRONTEND_PORT}")
    print("  Ctrl+C para detener todo")
    print("=" * 50 + "\n")

    def shutdown(sig=None, frame=None):
        print("\n[stop] Deteniendo servicios ...")
        for name, p in procs:
            try:
                p.terminate()
                print(f"  [stop] {name} (PID {p.pid}) terminado")
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Esperar a que algún proceso termine inesperadamente
    while True:
        for name, p in procs:
            if p.poll() is not None:
                print(f"\n[warn] {name} terminó inesperadamente (código {p.returncode})")
                shutdown()
        time.sleep(2)


if __name__ == "__main__":
    main()
