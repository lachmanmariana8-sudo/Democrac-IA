"""Backup completo del estado del PEIRS en producción.

Descarga a un directorio local con timestamp:
  - health snapshot
  - observation status de cada país activo
  - lista completa de Elite Reports
  - para cada Elite Report: HTML, MD, JSON estructurado, metadata
  - manifest.json con SHA256 de cada archivo

Uso:
    python scripts/backup.py [--api URL] [--out backups/] [--key OBSERVER_KEY]
                              [--country PER] [--targz]

La OBSERVER_KEY se lee de env var OBSERVER_API_KEY si no se pasa por flag.
Sin key, los endpoints publicos se descargan igual; los privados se omiten.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import tarfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


DEFAULT_API = "https://democracia-peirs-production.up.railway.app"


def fetch(url: str, observer_key: Optional[str] = None,
          timeout: int = 30) -> tuple[int, bytes, dict]:
    """Hace GET; devuelve (status, body, headers)."""
    headers = {"Accept": "*/*"}
    if observer_key:
        headers["X-Observer-Key"] = observer_key
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as r:
            body = r.read()
            return r.status, body, dict(r.headers)
    except HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        return e.code, body, {}
    except URLError as e:
        print(f"  [warn] {url}: {e}")
        return 0, b"", {}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write_file(path: Path, content: bytes, manifest: List[Dict[str, Any]],
               relpath: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    manifest.append({
        "path": relpath,
        "size_bytes": len(content),
        "sha256": sha256(content),
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default=DEFAULT_API)
    ap.add_argument("--out", default="backups")
    ap.add_argument("--key", default=os.getenv("OBSERVER_API_KEY", ""))
    ap.add_argument("--country", action="append", default=None,
                   help="Pais a backupear (ISO-3). Repetir flag para varios. Default: todos los activos.")
    ap.add_argument("--targz", action="store_true",
                   help="Empaquetar resultado en .tar.gz al final")
    args = ap.parse_args()

    api = args.api.rstrip("/")
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%S")
    out_root = Path(args.out) / f"peirs-backup-{ts}"
    out_root.mkdir(parents=True, exist_ok=True)
    print(f"Backup target: {out_root}")

    manifest: List[Dict[str, Any]] = []

    # 1) Health
    print("[1/4] Health snapshot")
    code, body, _ = fetch(f"{api}/api/health?deep=true")
    if code == 200:
        write_file(out_root / "health.json", body, manifest, "health.json")
        try:
            health = json.loads(body)
            print(f"      version={health.get('version')} llm={health.get('llm_configured')} sessions={health.get('active_observation_sessions')}")
        except Exception:
            pass
    else:
        print(f"      FAIL code={code}")

    # 2) Observation status — paises activos
    print("[2/4] Observation sessions")
    countries = args.country or ["PER"]   # default a Peru por ahora
    for cc in countries:
        code, body, _ = fetch(f"{api}/api/observation/{cc}/status")
        if code == 200:
            write_file(out_root / f"observation_{cc}.json", body, manifest,
                       f"observation_{cc}.json")
            try:
                obs = json.loads(body)
                print(f"      {cc}: total_entries={obs.get('total_entries')} phase={obs.get('phase')}")
            except Exception:
                pass
        else:
            print(f"      {cc}: code={code} (sin sesion activa o no autorizado)")

    # 3) Lista de Elite Reports
    print("[3/4] Elite Reports list")
    elite_ids: List[str] = []
    for cc in countries:
        code, body, _ = fetch(f"{api}/api/report/elite/list?country_code={cc}&limit=100")
        if code == 200:
            write_file(out_root / f"elite_list_{cc}.json", body, manifest,
                       f"elite_list_{cc}.json")
            try:
                lst = json.loads(body)
                items = lst.get("items", [])
                ids = [it["report_id"] for it in items]
                elite_ids.extend(ids)
                print(f"      {cc}: {len(ids)} informes")
            except Exception:
                pass

    # 4) Para cada Elite Report — HTML, MD, structured
    print(f"[4/4] Descargando {len(elite_ids)} informes Elite (3 formatos c/u)")
    elite_dir = out_root / "elite"
    success = 0
    fails: List[str] = []
    for rid in elite_ids:
        rid_dir = elite_dir / rid
        ok = True
        for fmt, ext in (("html", "html"), ("md", "md")):
            code, body, _ = fetch(f"{api}/api/report/elite/{rid}/download?format={fmt}")
            if code == 200 and body:
                write_file(rid_dir / f"report.{ext}", body, manifest,
                           f"elite/{rid}/report.{ext}")
            else:
                ok = False
                fails.append(f"{rid}/{fmt} (code={code})")
        # structured (JSON)
        code, body, _ = fetch(f"{api}/api/report/elite/{rid}/structured")
        if code == 200:
            write_file(rid_dir / "structured.json", body, manifest,
                       f"elite/{rid}/structured.json")
        elif code == 410:
            # Report previo a la migracion output_json — no fatal
            pass
        else:
            ok = False
            fails.append(f"{rid}/structured (code={code})")
        if ok:
            success += 1

    print(f"      {success}/{len(elite_ids)} informes con HTML+MD OK")
    if fails:
        print(f"      Fallos parciales: {len(fails)}")
        for f in fails[:5]:
            print(f"        - {f}")

    # 5) Manifest
    manifest_data = {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "api": api,
        "countries": countries,
        "files": manifest,
        "totals": {
            "files_count": len(manifest),
            "total_bytes": sum(f["size_bytes"] for f in manifest),
            "elite_reports": len(elite_ids),
            "elite_reports_full": success,
        },
    }
    manifest_bytes = json.dumps(manifest_data, indent=2, ensure_ascii=False).encode()
    (out_root / "manifest.json").write_bytes(manifest_bytes)

    total_mb = manifest_data["totals"]["total_bytes"] / (1024 * 1024)
    print(f"\nBackup OK — {len(manifest)} archivos, {total_mb:.1f} MB")
    print(f"  {out_root}")

    # 6) Opcional: tar.gz
    if args.targz:
        targz_path = Path(args.out) / f"peirs-backup-{ts}.tar.gz"
        print(f"\nComprimiendo a {targz_path}...")
        with tarfile.open(targz_path, "w:gz") as tar:
            tar.add(out_root, arcname=out_root.name)
        targz_mb = targz_path.stat().st_size / (1024 * 1024)
        print(f"  {targz_mb:.1f} MB comprimido")


if __name__ == "__main__":
    main()
