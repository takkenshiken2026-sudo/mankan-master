#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用語 batch（TERMS）を glossary_terms.csv に追記。"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.scaffold_glossary_term import load_fieldnames  # noqa: E402


def load_terms_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("glossary_batch", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "TERMS"):
        raise ValueError(f"{path} must define TERMS dict")
    return mod


def apply_terms(
    csv_path: Path,
    terms: dict[str, dict[str, str]],
    *,
    dry_run: bool = False,
) -> int:
    rows: list[dict[str, str]] = []
    fieldnames: list[str] = load_fieldnames()
    if csv_path.is_file():
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or fieldnames)
            rows = list(reader)
    existing = {(r.get("term") or "").strip() for r in rows}
    added = 0
    for term, patch in terms.items():
        if term in existing:
            raise ValueError(f"term already exists: {term}")
        row = {col: "" for col in fieldnames}
        row.update(patch)
        row["term"] = term
        rows.append(row)
        added += 1
    if added and not dry_run:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    return added


def main() -> int:
    ap = argparse.ArgumentParser(description="用語 batch を glossary_terms.csv に追記")
    ap.add_argument("--batch", type=Path, required=True)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    mod = load_terms_module(args.batch.resolve())
    terms = getattr(mod, "TERMS")
    csv_path = args.root.resolve() / "data" / "glossary_terms.csv"
    n = apply_terms(csv_path, terms, dry_run=args.dry_run)
    print(f"apply_glossary_batch: added {n} terms from {args.batch.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
