#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""glossary_headlist_draft.csv を tag 別に整形表示する。"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "glossary_headlist_draft.csv"

ORDERED_TAGS = [
    ("法令・制度", [
        "区分所有法",
        "標準管理規約_単棟",
        "標準管理規約_団地",
        "標準管理規約_複合用途",
        "民法",
        "適正化法",
        "関連法令",
    ]),
    ("契約・実務", [
        "管理組合運営",
        "標準管理委託契約書",
        "会計",
        "税務",
        "長期修繕計画",
        "大規模修繕",
        "紛争処理",
        "適正化基本方針",
        "実務一般",
    ]),
    ("設備・その他", [
        "建築基準法",
        "都市計画法",
        "建物構造",
        "給排水",
        "電気設備",
        "ガス設備",
        "防災・消防",
        "換気・空調",
        "昇降機",
        "防犯・警備",
        "個人情報",
        "その他法令",
    ]),
]

def main() -> int:
    by_tag: dict[str, list[dict[str, str]]] = defaultdict(list)
    with CSV_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_tag[row["tag"]].append(row)

    total = 0
    for category, tags in ORDERED_TAGS:
        cat_count = sum(len(by_tag.get(t, [])) for t in tags)
        print(f"\n========== {category}  ({cat_count}語) ==========")
        for tag in tags:
            rows = by_tag.get(tag, [])
            if not rows:
                continue
            print(f"\n--- [{tag}]  {len(rows)}語 ---")
            for r in rows:
                freq = int(r.get("freq") or 0)
                star = " *" if freq >= 10 else ""
                print(f"  {r['tier']}  {r['term']:24s} freq={freq}{star}")
            total += len(rows)

    print(f"\n========== 合計 {total}語 ==========")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
