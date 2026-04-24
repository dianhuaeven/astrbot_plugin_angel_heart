#!/usr/bin/env python3
"""Replace every `memory_scope` value in JSON files with `dianhua`."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TARGET_VALUE = "dianhua"


def replace_memory_scope(node: Any) -> int:
    """Recursively replace all memory_scope fields and return the change count."""
    changes = 0

    if isinstance(node, dict):
        if "memory_scope" in node and node["memory_scope"] != TARGET_VALUE:
            node["memory_scope"] = TARGET_VALUE
            changes += 1

        for value in node.values():
            changes += replace_memory_scope(value)

    elif isinstance(node, list):
        for item in node:
            changes += replace_memory_scope(item)

    return changes


def iter_json_files(paths: list[str], recursive: bool) -> list[Path]:
    files: list[Path] = []

    for raw_path in paths:
        path = Path(raw_path).expanduser()

        if path.is_file():
            files.append(path)
            continue

        if path.is_dir():
            pattern = "**/*.json" if recursive else "*.json"
            files.extend(sorted(path.glob(pattern)))

    unique_files = sorted({file.resolve() for file in files})
    return unique_files


def process_file(path: Path, dry_run: bool) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    changes = replace_memory_scope(data)

    if changes and not dry_run:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return changes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace every memory_scope field in JSON files with 'dianhua'."
    )
    parser.add_argument("paths", nargs="+", help="JSON file(s) or directories to process.")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively scan directories for JSON files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show how many fields would change without writing files.",
    )
    args = parser.parse_args()

    files = iter_json_files(args.paths, args.recursive)
    if not files:
        print("No JSON files found.")
        return 1

    total_changes = 0
    changed_files = 0

    for file_path in files:
        changes = process_file(file_path, args.dry_run)
        total_changes += changes
        if changes:
            changed_files += 1
        action = "would update" if args.dry_run else "updated"
        print(f"{file_path}: {action} {changes} field(s)")

    print(
        f"Done. {changed_files} file(s) {'would be changed' if args.dry_run else 'changed'}, "
        f"{total_changes} field(s) processed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
