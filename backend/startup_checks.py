"""
DEMOCRAC.IA / PEIRS — Startup Checks
Valida el entorno antes de arrancar la app: API keys, datasets, RAG, DB.
Llamar desde app.py al inicio: run_startup_checks()
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class CheckResult:
    name: str
    ok: bool
    message: str
    critical: bool = False  # Si falla un check crítico, se lanza excepción


@dataclass
class StartupReport:
    checks: List[CheckResult] = field(default_factory=list)

    def add(self, result: CheckResult) -> None:
        self.checks.append(result)

    @property
    def all_ok(self) -> bool:
        return all(c.ok for c in self.checks)

    @property
    def critical_failures(self) -> List[CheckResult]:
        return [c for c in self.checks if not c.ok and c.critical]

    def print_summary(self) -> None:
        print("\n" + "═" * 60)
        print("  DEMOCRAC.IA — Startup Checks")
        print("═" * 60)
        for c in self.checks:
            icon = "✅" if c.ok else ("🔴" if c.critical else "⚠️ ")
            print(f"  {icon}  {c.name:<30} {c.message}")
        print("═" * 60)
        failures = [c for c in self.checks if not c.ok]
        if not failures:
            print("  Sistema listo. Todos los checks pasaron.")
        else:
            crit = [c for c in failures if c.critical]
            warn = [c for c in failures if not c.critical]
            if crit:
                print(f"  🔴 {len(crit)} checks críticos fallaron — sistema puede no funcionar")
            if warn:
                print(f"  ⚠️  {len(warn)} checks opcionales fallaron — funcionalidad reducida")
        print("═" * 60 + "\n")


# ── Checks individuales ───────────────────────────────────────────────────────

def check_anthropic_key() -> CheckResult:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return CheckResult(
            "ANTHROPIC_API_KEY", False,
            "No configurada — análisis LLM deshabilitado",
            critical=False  # fallbacks determinísticos disponibles
        )
    if not key.startswith("sk-ant-"):
        return CheckResult(
            "ANTHROPIC_API_KEY", False,
            "Formato inválido (debe empezar con 'sk-ant-')",
            critical=False
        )
    return CheckResult("ANTHROPIC_API_KEY", True, f"Configurada ({key[:12]}...)")


def check_observer_keys() -> CheckResult:
    raw = os.getenv("OBSERVER_API_KEYS", "")
    dev_key = "democracia-obs-dev-2026"
    if not raw or raw == dev_key:
        return CheckResult(
            "OBSERVER_API_KEYS", True,
            "Usando clave dev — cambiar en producción",
            critical=False
        )
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    return CheckResult("OBSERVER_API_KEYS", True, f"{len(keys)} claves configuradas")


def check_dataset(name: str, env_var: str, default_path: str) -> CheckResult:
    path = Path(os.getenv(env_var, default_path))
    if path.exists():
        size_mb = path.stat().st_size / (1024 * 1024)
        return CheckResult(name, True, f"Encontrado ({size_mb:.1f} MB)")
    return CheckResult(
        name, False,
        f"No encontrado en '{path}' — usando datos mock",
        critical=False
    )


def check_vdem() -> CheckResult:
    return check_dataset(
        "V-Dem v15", "VDEM_CSV_PATH",
        "../data/V-Dem-CY-Full+Others-v15.csv"
    )


def check_freedom_house() -> CheckResult:
    return check_dataset(
        "Freedom House FIW", "FH_CSV_PATH",
        "../data/All_data_FIW_2013-2025 - Index.csv"
    )


def check_rsf() -> CheckResult:
    return check_dataset(
        "RSF 2025", "RSF_CSV_PATH",
        "../data/RSF/2025 - 2025.csv"
    )


def check_pei() -> CheckResult:
    return check_dataset(
        "PEI v10.0", "PEI_CSV_PATH",
        "../data/PEI/PEI_10 Election External.csv"
    )


def check_rag() -> CheckResult:
    try:
        import chromadb  # noqa: F401
    except ImportError:
        return CheckResult(
            "RAG (ChromaDB)", False,
            "chromadb no instalado — pip install chromadb",
            critical=False
        )
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        return CheckResult(
            "RAG (sentence-transformers)", False,
            "sentence-transformers no instalado — pip install sentence-transformers",
            critical=False
        )
    # Intenta inicializar RAG
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from rag import init_rag, RAG_AVAILABLE  # type: ignore
        if RAG_AVAILABLE:
            init_rag()
            return CheckResult("RAG Legal", True, "ChromaDB + corpus legal inicializado")
        return CheckResult("RAG Legal", False, "RAG_AVAILABLE=False tras import", critical=False)
    except Exception as e:
        return CheckResult("RAG Legal", False, f"Error al inicializar: {e}", critical=False)


def check_db() -> CheckResult:
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from db import init_db, get_db_stats  # type: ignore
        init_db()
        stats = get_db_stats()
        return CheckResult(
            "SQLite DB", True,
            f"OK — {stats.get('analysis_runs', 0)} runs, "
            f"{stats.get('reports', 0)} reportes"
        )
    except Exception as e:
        return CheckResult("SQLite DB", False, f"Error: {e}", critical=False)


def check_ooni() -> CheckResult:
    try:
        import httpx  # noqa: F401
        return CheckResult("OONI (httpx)", True, "httpx disponible — censura en tiempo real OK")
    except ImportError:
        return CheckResult(
            "OONI (httpx)", False,
            "httpx no instalado — pip install httpx",
            critical=False
        )


def check_alerts() -> CheckResult:
    slack = bool(os.getenv("ALERT_SLACK_WEBHOOK_URL"))
    webhook = bool(os.getenv("ALERT_WEBHOOK_URL"))
    email = bool(os.getenv("ALERT_EMAIL_TO"))
    active = sum([slack, webhook, email])
    if active == 0:
        return CheckResult(
            "Alert Channels", False,
            "Ningún canal configurado — alertas deshabilitadas",
            critical=False
        )
    channels = ", ".join(
        [c for c, b in [("Slack", slack), ("Webhook", webhook), ("Email", email)] if b]
    )
    return CheckResult("Alert Channels", True, f"{active} canal(es): {channels}")


def check_frontend() -> CheckResult:
    dist = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    if dist.exists():
        return CheckResult("Frontend (dist)", True, "Build encontrado")
    return CheckResult(
        "Frontend (dist)", False,
        "No compilado — ejecuta 'npm run build' en frontend/",
        critical=False
    )


# ── Función principal ─────────────────────────────────────────────────────────

def run_startup_checks(raise_on_critical: bool = True) -> StartupReport:
    """
    Ejecuta todos los checks de startup y retorna un StartupReport.
    Si raise_on_critical=True y hay fallos críticos, lanza RuntimeError.
    """
    report = StartupReport()

    # Checks críticos primero
    report.add(check_anthropic_key())

    # Autenticación
    report.add(check_observer_keys())

    # Datasets (todos opcionales — fallback a mock)
    report.add(check_vdem())
    report.add(check_freedom_house())
    report.add(check_rsf())
    report.add(check_pei())

    # Componentes opcionales
    report.add(check_rag())
    report.add(check_db())
    report.add(check_ooni())
    report.add(check_alerts())
    report.add(check_frontend())

    report.print_summary()

    if raise_on_critical and report.critical_failures:
        names = [c.name for c in report.critical_failures]
        raise RuntimeError(
            f"Checks críticos fallaron: {', '.join(names)}. "
            "Revisa la configuración antes de continuar."
        )

    return report


if __name__ == "__main__":
    run_startup_checks(raise_on_critical=False)
