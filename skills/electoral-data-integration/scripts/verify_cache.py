"""
verify_cache.py — Valida SHA-256 y reporta datasets faltantes o corruptos.

Uso:
    python verify_cache.py --cache "D:\\DemocracIA\\data"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", required=True)
    args = parser.parse_args()

    cache = Path(args.cache)
    issues = 0
    ok = 0

    for meta_path in cache.rglob("*.meta.json"):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"CORRUPT META {meta_path}: {exc}", file=sys.stderr)
            issues += 1
            continue

        data_path = meta_path.with_suffix("")  # quita .json
        # .meta.json → quita dos sufijos
        if data_path.suffix == ".meta":
            data_path = data_path.with_suffix("")

        if not data_path.exists():
            # intentar otro esquema: archivo.csv.meta.json → archivo.csv
            data_path = Path(str(meta_path).replace(".meta.json", ""))

        if not data_path.exists():
            print(f"MISSING DATA  {data_path}", file=sys.stderr)
            issues += 1
            continue

        expected = meta.get("sha256")
        actual = sha256_of(data_path)
        if expected and expected != actual:
            print(f"HASH MISMATCH {data_path}\n  expected: {expected}\n  actual:   {actual}", file=sys.stderr)
            issues += 1
        else:
            print(f"OK {meta.get('dataset', '?'):6s} {data_path.name}")
            ok += 1

    print(f"\nResumen: {ok} OK, {issues} con problemas")
    return 0 if issues == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
