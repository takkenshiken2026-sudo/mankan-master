#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""試験ガイド記事を 50本以内へ削減（archived 化＋guide_retired.json リダイレクト）。

docs/guide-article-genres.md / guide-article-catalog.md の「本番50本以内」ルールに合わせ、
非アフィリエイト111本→40本へ統合。退役記事は近いカノニカル記事へ noindex リダイレクト。
アフィリエイト10本は維持。
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.editorial_quality import is_published_guide, norm  # noqa: E402
from tools.rewrite_guide_boilerplate import _csv_fieldnames  # noqa: E402

CSV_PATH = ROOT / "data" / "guide_articles.csv"
RETIRED_JSON = ROOT / "data" / "guide_retired.json"
REVISION = "2026-06-18: 50本以内ルールに合わせ統合（カノニカル記事へリダイレクト）"

# 残すカノニカル（非アフィリエイト40本）
KEEP_NONAFF = {
    # 試験概要(4)
    "exam-overview", "official-info-sources", "exam-purpose-and-career",
    "compare-similar-qualifications",
    # 受験・申込(5)
    "exam-eligibility", "exemption-system", "exam-schedule", "exam-fees",
    "exam-application-flow",
    # 出題・形式(4)
    "exam-format-overview", "exam-scope-overview", "subject-breakdown",
    "time-limit-strategy",
    # 合格・難易度(3)
    "exam-difficulty", "pass-rate", "pass-score",
    # 学習計画(2)
    "study-plan", "first-30-days-plan",
    # 独学対策(5)
    "self-study-roadmap", "textbook-selection", "problem-book-selection",
    "free-materials-online", "correspondence-course-guide",
    # 過去問活用(4)
    "past-question-strategy", "past-questions-by-field",
    "past-questions-review-cycle", "mock-exam-how-to",
    # 用語ハブ(4)
    "glossary-how-to", "important-terms-list", "confusing-terms", "calculation-drill",
    # 復習・苦手(2)
    "mistake-notebook", "review-cycle-spaced",
    # 直前・当日(3)
    "exam-day-flow", "exam-day-items", "final-week-prep",
    # 注意点・更新 + 合格後(4)
    "common-misconceptions", "exam-changes", "retake-strategy", "after-pass-procedure",
}

# 退役 slug → 統合先カノニカル slug
RETIRE = {
    "first-time-exam-guide": "exam-overview",
    "education-requirement": "exam-eligibility",
    "work-experience-requirement": "exam-eligibility",
    "concurrent-exam-rules": "exam-application-flow",
    "application-deadline-checklist": "exam-application-flow",
    "reschedule-and-absence": "exam-application-flow",
    "exam-venue-and-region": "exam-schedule",
    "cbt-computer-exam": "exam-format-overview",
    "new-topics-trend": "exam-scope-overview",
    "scope-revision-history": "exam-scope-overview",
    "scope-vs-past-questions": "exam-scope-overview",
    "syllabus-how-to-read": "exam-scope-overview",
    "weight-by-topic": "subject-breakdown",
    "difficulty-for-beginners": "exam-difficulty",
    "pass-rate-how-to-read": "pass-rate",
    "study-plan-1year": "study-plan",
    "study-plan-3months": "study-plan",
    "study-plan-6months": "study-plan",
    "study-plan-beginner": "study-plan",
    "study-plan-working": "study-plan",
    "balance-work-study": "study-plan",
    "time-management": "study-plan",
    "self-study-mistakes": "self-study-roadmap",
    "self-study-motivation": "self-study-roadmap",
    "self-study-schedule": "self-study-roadmap",
    "self-study-start": "self-study-roadmap",
    "self-study-without-school": "self-study-roadmap",
    "self-study-environment": "self-study-roadmap",
    "textbook-vs-past-questions": "textbook-selection",
    "material-update-cycle": "free-materials-online",
    "bookmark-review-method": "past-questions-review-cycle",
    "drill-volume-guide": "past-question-strategy",
    "ichimon-practice": "past-question-strategy",
    "past-questions-by-year": "past-question-strategy",
    "past-questions-first-attempt": "past-question-strategy",
    "past-questions-latest-year": "past-question-strategy",
    "past-questions-score-analysis": "past-questions-review-cycle",
    "past-questions-wrong-reasons": "past-questions-review-cycle",
    "simulation-exam-schedule": "mock-exam-how-to",
    "timed-practice": "mock-exam-how-to",
    "formula-memorization": "calculation-drill",
    "numbers-and-deadlines": "calculation-drill",
    "numeric-trap-choices": "calculation-drill",
    "rate-and-percentage": "calculation-drill",
    "glossary-study-method": "glossary-how-to",
    "related-terms-navigation": "important-terms-list",
    "terms-importance-levels": "important-terms-list",
    "terms-with-past-questions": "important-terms-list",
    "almost-correct-review": "review-cycle-spaced",
    "note-taking-method": "mistake-notebook",
    "plateau-breakthrough": "review-cycle-spaced",
    "exam-day-time-allocation": "exam-day-flow",
    "exam-day-troubleshooting": "exam-day-flow",
    "final-day-checklist": "final-week-prep",
    "final-mock-last-run": "final-week-prep",
    "final-scope-narrowing": "final-week-prep",
    "final-sleep-and-health": "final-week-prep",
    "mental-prep-exam-day": "exam-day-flow",
    "difficulty-myths": "common-misconceptions",
    "eligibility-myths": "common-misconceptions",
    "study-hours-myth": "common-misconceptions",
    "pass-only-past-questions-myth": "common-misconceptions",
    "legal-revision-impact": "exam-changes",
    "syllabus-update-tracker": "exam-changes",
    "official-info-update-habits": "official-info-sources",
    "fail-retry-plan": "retake-strategy",
    "retake-schedule-adjustment": "retake-strategy",
    "score-gap-analysis": "retake-strategy",
    "career-after-qualification": "after-pass-procedure",
    "registration-after-pass": "after-pass-procedure",
    "pass-announcement-guide": "after-pass-procedure",
}


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8-sig")))
    fieldnames = _csv_fieldnames(list(rows[0].keys()), rows)

    published = [r for r in rows if is_published_guide(r)]
    pub_nonaff = {norm(r["slug"]) for r in published if not norm(r["slug"]).startswith("affiliate-")}
    pub_aff = {norm(r["slug"]) for r in published if norm(r["slug"]).startswith("affiliate-")}

    # --- 整合性チェック（取りこぼし・誤マップを防ぐ） ---
    keep_and_retire = KEEP_NONAFF | set(RETIRE)
    missing = pub_nonaff - keep_and_retire
    extra = keep_and_retire - pub_nonaff
    overlap = KEEP_NONAFF & set(RETIRE)
    bad_targets = {t for t in RETIRE.values() if t not in KEEP_NONAFF}
    assert not missing, f"未分類の公開記事: {sorted(missing)}"
    assert not extra, f"存在しない slug を指定: {sorted(extra)}"
    assert not overlap, f"KEEPとRETIREの重複: {sorted(overlap)}"
    assert not bad_targets, f"リダイレクト先がKEEPにない: {sorted(bad_targets)}"

    # --- CSV 更新（archived 化） ---
    archived = 0
    for r in rows:
        slug = norm(r.get("slug"))
        if slug in RETIRE:
            r["content_status"] = "archived"
            r["revision_note"] = REVISION
            archived += 1

    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # --- リダイレクトマップ ---
    RETIRED_JSON.write_text(
        json.dumps({"redirects": dict(sorted(RETIRE.items()))}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"published before: {len(published)} (non-aff {len(pub_nonaff)} / aff {len(pub_aff)})")
    print(f"archived: {archived}")
    print(f"published after: {len(published) - archived} "
          f"(keep non-aff {len(KEEP_NONAFF)} + aff {len(pub_aff)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
