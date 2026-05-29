#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""過去問 CSV の正答と解説の整合性を監査する。

検出:
  - explanation / summary が別番号を正解と記載
  - explanation_choices に正答肢が含まれる
  - 生成 HTML の legacy 解説が別番号を正解と記載

Usage:
  python3 tools/audit_past_answer_explanation.py
  python3 tools/audit_past_answer_explanation.py --strict
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_past_question_pages import page_dict, parse_correct  # noqa: E402
from tools.q_explanation import (  # noqa: E402
    build_explanation_html,
    norm,
    parse_explanation_choices,
    question_ask_mode,
    split_legacy_explanation,
)

DATA_CSV = ROOT / "data" / "past_questions.csv"

_LEGACY_ANS_RE = re.compile(
    r"(?:正解|正答)(?:は|が)?\s*[（(]?(\d+)[）)]?",
)


@dataclass
class Finding:
    year: int
    qno: int
    code: str
    message: str


def _load_rows(csv_path: Path) -> list[tuple[int, dict]]:
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [(i, row) for i, row in enumerate(reader, start=2)]


def _legacy_mismatches(text: str, correct: int, field: str) -> list[Finding]:
    out: list[Finding] = []
    if not text:
        return out
    for m in _LEGACY_ANS_RE.finditer(text):
        n = int(m.group(1))
        if n != correct:
            out.append(
                Finding(
                    0,
                    0,
                    "legacy_answer_mismatch",
                    f"{field} が正答（{correct}）と異なる番号（{n}）を正解と記載: 「{m.group(0)}」",
                )
            )
    return out


def audit_row(line_no: int, row: dict) -> list[Finding]:
    inv = norm(row.get("is_invalidated", "")).upper() == "TRUE"
    correct = parse_correct(row.get("correct"))
    if inv or correct is None:
        return []

    try:
        page = page_dict(row, line_no)
    except ValueError as exc:
        year = int(row.get("exam_year") or 0)
        qno = int(row.get("question_no") or 0)
        return [Finding(year, qno, "page_dict", str(exc))]

    year = page["year"]
    qno = page["qno"]
    findings: list[Finding] = []

    def add(code: str, msg: str) -> None:
        findings.append(Finding(year, qno, code, msg))

    exp = norm(row.get("explanation"))
    for f in _legacy_mismatches(exp, correct, "explanation"):
        add(f.code, f.message)

    summary = norm(row.get("explanation_summary"))
    for f in _legacy_mismatches(summary, correct, "explanation_summary"):
        add(f.code, f.message)

    leg_summary, leg_body = split_legacy_explanation(exp)
    if not summary and leg_summary:
        summary = leg_summary
    correct_body = norm(row.get("explanation_correct")) or leg_body
    for f in _legacy_mismatches(correct_body, correct, "explanation_correct"):
        add(f.code, f.message)

    parsed = parse_explanation_choices(norm(row.get("explanation_choices")))
    if correct in parsed:
        add(
            "correct_in_explanation_choices",
            f"explanation_choices に正答肢（{correct}）が含まれています",
        )

    # 生成 HTML: 要約・正解理由に別番号のみ
    html = build_explanation_html(page, row)
    lead_m = re.search(r'class="q-exp-lead"[^>]*>([^<]+)', html)
    if lead_m:
        for f in _legacy_mismatches(lead_m.group(1), correct, "生成HTML要約"):
            add(f.code, f.message)

    correct_sec = re.search(
        r'id="q-exp-correct-h".*?</section>',
        html,
        re.DOTALL,
    )
    if correct_sec:
        sec_text = re.sub(r"<[^>]+>", " ", correct_sec.group(0))
        for f in _legacy_mismatches(sec_text, correct, "生成HTML正解の理由"):
            add(f.code, f.message)

    stem = page.get("stem_plain") or ""
    asks_wrong_option = bool(
        re.search(
            r"適切でない|不適切|誤って|誤り|正しくない|正確でない|妥当でない|内容が正確でない",
            stem,
        )
    )
    mode = question_ask_mode(stem)
    if mode == "most_correct" and not asks_wrong_option and correct_body:
        pat = re.compile(
            rf"選択肢{correct}[（(](?:誤|不正|不適切|正しくない|内容が正確でない)",
        )
        if pat.search(correct_body):
            add(
                "correct_marked_wrong",
                f"explanation_correct で正答（{correct}）を誤りと記載",
            )

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="過去問 正答×解説 整合性監査")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--csv", type=Path, default=DATA_CSV)
    args = ap.parse_args()

    rows = _load_rows(args.csv.resolve())
    all_findings: list[Finding] = []
    for line_no, row in rows:
        all_findings.extend(audit_row(line_no, row))

    if not all_findings:
        print(f"OK: {len(rows)} 問 — 正答と解説の不一致は検出されませんでした")
        return 0

    print(f"監査結果: {len(rows)} 問, error={len(all_findings)}\n")
    for f in sorted(all_findings, key=lambda x: (x.year, x.qno, x.code)):
        print(f"  [ERROR] {f.year}-{f.qno:02d} {f.code}: {f.message}")

    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
