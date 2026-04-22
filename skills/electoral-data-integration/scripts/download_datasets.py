"""
download_datasets.py — CLI para refrescar la cache de datasets PEIRS.

Uso desde PowerShell:
    python download_datasets.py --cache "D:\\DemocracIA\\data"
    python download_datasets.py --cache "D:\\DemocracIA\\data" --force
    python download_datasets.py --cache "D:\\DemocracIA\\data" --only vdem fh
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from peirs_data import DATASET_SOURCES, PeirsData  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Refrescar cache de datasets PEIRS")
    parser.add_argument("--cache", required=True, help=r"Directorio cache (ej: D:\DemocracIA\data)")
    parser.add_argument("--force", action="store_true", help="Forzar redescarga aunque exista cache")
    parser.add_argument(
        "--only",
        nargs="*",
        choices=list(DATASET_SOURCES),
        help="Limitar a datasets específicos",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    data = PeirsData(cache_dir=args.cache)
    targets = args.only or list(DATASET_SOURCES)

    for key in targets:
        try:
            path = data.ensure(key, force_refresh=args.force)
            print(f"OK   {key:6s} -> {path}")
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {key:6s} -> {exc}", file=sys.stderr)

    print("\nEstado de cache:")
    print(data.cache_status().to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
