#!/usr/bin/env python3
"""Generate the docs/csv-files.json manifest from the CSV files present on disk.

This helper keeps the front-end CSV selector in sync with the files shipped
in the `docs/` folder. Run it whenever you add or remove a CSV file.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Iterable


def discover_csv_files(base_dir: Path) -> list[dict[str, Any]]:
    csv_files: list[dict[str, Any]] = []
    csv_dir = base_dir / 'csv'
    if not csv_dir.exists():
        return []
    for path in sorted(csv_dir.glob('*.csv')):
        if path.is_file():
            # Lecture pour compter les cartes (nombre de lignes non vides - 1 pour l'en-tête)
            content = path.read_text(encoding='utf-8')
            lines = [line for line in content.splitlines() if line.strip()]
            card_count = max(0, len(lines) - 1)

            # Récupération de la date de modification (format ISO YYYY-MM-DD HH:MM:SS)
            mtime = path.stat().st_mtime
            updated_date = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

            csv_files.append({
                "path": f"csv/{path.name}",
                "count": card_count,
                "updated": updated_date
            })
    return csv_files


def write_manifest(json_path: Path, files: Iterable[dict[str, Any]]) -> None:
    payload = list(files)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--docs-dir',
        type=Path,
        default=Path(__file__).resolve().parents[1] / 'docs',
        help='Directory that contains the CSV files and manifest (default: %(default)s)',
    )
    parser.add_argument(
        '--manifest-name',
        default='csv-files.json',
        help='Name of the manifest file to generate inside the docs directory (default: %(default)s)',
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    docs_dir: Path = args.docs_dir

    if not docs_dir.exists():
        raise SystemExit(f"Docs directory not found: {docs_dir}")

    csv_files = discover_csv_files(docs_dir)

    if not csv_files:
        raise SystemExit('No CSV files were found — nothing to write in the manifest.')

    manifest_path = docs_dir / args.manifest_name
    write_manifest(manifest_path, csv_files)
    print(f"Manifest updated with {len(csv_files)} file(s): {manifest_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
