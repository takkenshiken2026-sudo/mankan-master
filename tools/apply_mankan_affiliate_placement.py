#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フェーズE: マン管 通常ガイド → 比較記事（affiliate-*）導線を一括接続。"""

from __future__ import annotations

import csv
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# slug -> affiliate_slug（1記事1本。公開済み比較記事のみ）
PLACEMENTS: dict[str, str] = {
    # テキスト・教材選び
    "textbook-selection": "affiliate-textbooks-recommend",
    "material-update-cycle": "affiliate-textbooks-recommend",
    "self-study-environment": "affiliate-textbooks-recommend",
    "self-study-roadmap": "affiliate-textbooks-recommend",
    "self-study-schedule": "affiliate-textbooks-recommend",
    "self-study-without-school": "affiliate-textbooks-recommend",
    "study-plan": "affiliate-textbooks-recommend",
    "study-plan-beginner": "affiliate-textbooks-recommend",
    "study-plan-3months": "affiliate-textbooks-recommend",
    "study-plan-6months": "affiliate-textbooks-recommend",
    "study-plan-1year": "affiliate-textbooks-recommend",
    "study-plan-working": "affiliate-textbooks-recommend",
    "first-30-days-plan": "affiliate-textbooks-recommend",
    "textbook-vs-past-questions": "affiliate-textbooks-recommend",
    "first-time-exam-guide": "affiliate-textbooks-recommend",
    "exam-overview": "affiliate-textbooks-recommend",
    # 問題集・過去問
    "problem-book-selection": "affiliate-problem-books",
    "past-question-strategy": "affiliate-problem-books",
    "past-questions-by-year": "affiliate-problem-books",
    "past-questions-by-field": "affiliate-problem-books",
    "past-questions-first-attempt": "affiliate-problem-books",
    "past-questions-latest-year": "affiliate-problem-books",
    "past-questions-review-cycle": "affiliate-problem-books",
    "past-questions-score-analysis": "affiliate-problem-books",
    "past-questions-wrong-reasons": "affiliate-problem-books",
    "scope-vs-past-questions": "affiliate-problem-books",
    "drill-volume-guide": "affiliate-problem-books",
    "field-law-past-question-focus": "affiliate-problem-books",
    "field-limit-past-question-focus": "affiliate-problem-books",
    "field-rights-past-question-focus": "affiliate-problem-books",
    "bookmark-review-method": "affiliate-problem-books",
    "almost-correct-review": "affiliate-problem-books",
    "mistake-notebook": "affiliate-problem-books",
    "plateau-breakthrough": "affiliate-problem-books",
    "score-gap-analysis": "affiliate-problem-books",
    "retake-strategy": "affiliate-problem-books",
    "fail-retry-plan": "affiliate-problem-books",
    # 模試・直前・一問一答
    "mock-exam-how-to": "affiliate-mock-exam-materials",
    "simulation-exam-schedule": "affiliate-mock-exam-materials",
    "timed-practice": "affiliate-mock-exam-materials",
    "time-limit-strategy": "affiliate-mock-exam-materials",
    "final-week-prep": "affiliate-mock-exam-materials",
    "final-day-checklist": "affiliate-mock-exam-materials",
    "final-mock-last-run": "affiliate-mock-exam-materials",
    "final-scope-narrowing": "affiliate-mock-exam-materials",
    "final-sleep-and-health": "affiliate-mock-exam-materials",
    "mental-prep-exam-day": "affiliate-mock-exam-materials",
    "exam-day-time-allocation": "affiliate-mock-exam-materials",
    "ichimon-practice": "affiliate-mock-exam-materials",
    # 無料/有料・独学判断
    "free-materials-online": "affiliate-free-vs-paid-study",
    "self-study-start": "affiliate-free-vs-paid-study",
    "self-study-mistakes": "affiliate-free-vs-paid-study",
    "self-study-motivation": "affiliate-free-vs-paid-study",
    "balance-work-study": "affiliate-free-vs-paid-study",
    "time-management": "affiliate-free-vs-paid-study",
    "study-hours-myth": "affiliate-free-vs-paid-study",
    "correspondence-course-guide": "affiliate-free-vs-paid-study",
    "pass-only-past-questions-myth": "affiliate-free-vs-paid-study",
    "common-misconceptions": "affiliate-free-vs-paid-study",
}

AFFILIATE_LABELS: dict[str, str] = {
    "affiliate-textbooks-recommend": "おすすめテキスト3選",
    "affiliate-problem-books": "おすすめ問題集3選",
    "affiliate-mock-exam-materials": "おすすめ一問一答・速習",
    "affiliate-free-vs-paid-study": "無料と有料教材の使い分け",
}

# slug 別の本文1文（未指定は affiliate 既定文）
BODY_SENTENCES: dict[str, str] = {
    "textbook-selection": (
        "テキスト1冊は、affiliate-textbooks-recommend で出版社別の解説量を比較してから固定すると途中で変えずに済みます。"
    ),
    "problem-book-selection": (
        "問題集1冊は、affiliate-problem-books で過去8年・分野別の違いを比較してからテキスト系列に合わせて選ぶと失敗が少ないです。"
    ),
    "free-materials-online": (
        "無料だけでどこまで進むかは、affiliate-free-vs-paid-study で48％ラインと段階投入の具体例を先に確認すると安心です。"
    ),
    "self-study-start": (
        "教材投資のタイミングは、affiliate-free-vs-paid-study で無料範囲と最小2冊セットを確認してから進めると無駄がありません。"
    ),
    "correspondence-course-guide": (
        "通信講座を検討する前に、affiliate-free-vs-paid-study で独学の最小セットと費用判断を先に整理すると選び直しが減ります。"
    ),
    "past-questions-by-year": (
        "演習用の問題集は、affiliate-problem-books で7分野50問120分に合う1冊を先に決めると年別周回が立てやすいです。"
    ),
    "ichimon-practice": (
        "一問一答の1冊選びは、affiliate-mock-exam-materials で誤答語の短問反復に向く3冊を比較してから固定すると効率的です。"
    ),
}

DEFAULT_BODY: dict[str, str] = {
    "affiliate-textbooks-recommend": (
        "テキスト1冊は、affiliate-textbooks-recommend で出版社別の解説量を比較してから固定すると途中で変えずに済みます。"
    ),
    "affiliate-problem-books": (
        "演習用の問題集は、affiliate-problem-books で収録形式を比較してから9月に1冊に絞ると周回計画が立てやすいです。"
    ),
    "affiliate-mock-exam-materials": (
        "直前の短問演習は、affiliate-mock-exam-materials で一問一答と速習を比較してから1冊を選ぶと効率的です。"
    ),
    "affiliate-free-vs-paid-study": (
        "教材の費用判断は、affiliate-free-vs-paid-study で無料範囲と最小2冊セットを24週逆算で確認できます。"
    ),
}

BODY_SECTION_KEYS = tuple(f"section_{n}_body" for n in range(1, 8))


def split_semicolon(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def join_semicolon(items: list[str]) -> str:
    return ";".join(items)


def related_has_slug(related: str, slug: str) -> bool:
    for item in split_semicolon(related):
        target = item.split(":", 1)[0].strip()
        if target == slug:
            return True
    return False


def add_related_link(related: str, affiliate_slug: str) -> str:
    if related_has_slug(related, affiliate_slug):
        return related
    label = AFFILIATE_LABELS[affiliate_slug]
    token = f"{affiliate_slug}:{label}"
    items = split_semicolon(related)
    return join_semicolon([token] + items)


def pick_body_section(row: dict[str, str]) -> str:
    for key in reversed(BODY_SECTION_KEYS):
        if (row.get(key) or "").strip():
            return key
    return "section_5_body"


def add_body_sentence(row: dict[str, str], affiliate_slug: str, guide_slug: str) -> None:
    sentence = BODY_SENTENCES.get(guide_slug) or DEFAULT_BODY[affiliate_slug]
    if affiliate_slug in "".join(row.get(k, "") for k in BODY_SECTION_KEYS):
        return
    col = pick_body_section(row)
    body = row.get(col) or ""
    if body.rstrip().endswith(("。", "．")):
        row[col] = body.rstrip() + sentence
    else:
        row[col] = body.rstrip() + "。" + sentence if body.strip() else sentence


def main() -> int:
    csv_path = ROOT / "data" / "guide_articles.csv"
    rows: list[dict[str, str]] = []
    updated = 0
    missing: list[str] = []

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print("ERROR: empty CSV", file=sys.stderr)
            return 1
        slug_set = set()
        for row in reader:
            slug_set.add(row["slug"])
            rows.append(row)

    for guide_slug, affiliate_slug in PLACEMENTS.items():
        if guide_slug not in slug_set:
            missing.append(guide_slug)
            continue
        if affiliate_slug not in slug_set:
            missing.append(f"{guide_slug}->{affiliate_slug}")
            continue

    if missing:
        print("ERROR: missing slugs:", ", ".join(missing), file=sys.stderr)
        return 1

    for row in rows:
        guide_slug = row["slug"]
        if guide_slug not in PLACEMENTS:
            continue
        if row.get("content_status") != "published":
            continue
        affiliate_slug = PLACEMENTS[guide_slug]
        before_related = row.get("related_links", "")
        before_body = "".join(row.get(k, "") for k in BODY_SECTION_KEYS)
        row["related_links"] = add_related_link(before_related, affiliate_slug)
        add_body_sentence(row, affiliate_slug, guide_slug)
        after_related = row.get("related_links", "")
        after_body = "".join(row.get(k, "") for k in BODY_SECTION_KEYS)
        if after_related != before_related or after_body != before_body:
            updated += 1

    orig_lines = sum(1 for _ in csv_path.open(encoding="utf-8-sig"))
    fd, tmp = tempfile.mkstemp(suffix=".csv", dir=csv_path.parent)
    try:
        with open(fd, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        new_lines = sum(1 for _ in open(tmp, encoding="utf-8"))
        if new_lines != orig_lines:
            print(f"ERROR: line count {orig_lines} -> {new_lines}", file=sys.stderr)
            return 1
        shutil.move(tmp, csv_path)
    finally:
        if Path(tmp).exists():
            Path(tmp).unlink()

    print(f"OK: affiliate placement on {updated} guides ({len(PLACEMENTS)} planned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
