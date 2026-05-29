#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""manabist.org の令和7年度解説記事を past_questions.csv に反映する。

  python3 tools/import_manabist_past_explanations.py --dry-run
  python3 tools/import_manabist_past_explanations.py
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data" / "past_questions.csv"

MANABIST_2025_URLS: dict[int, str] = {
    1: "https://manabist.org/mankan-kakomon-2025-1-kiyaku-kyoyo-bubun",
    2: "https://manabist.org/mankan-kakomon-2025-2-kanrisha-kainin",
    3: "https://manabist.org/mankan-kakomon-2025-03-ichibu-kyoyo",
    4: "https://manabist.org/mankan-kakomon-2025-04-shukai",
    5: "https://manabist.org/mankan-kakomon-2025-05-shukai-ketsugi",
    6: "https://manabist.org/mankan-kakomon-2025-06-shukai-02",
    7: "https://manabist.org/mankan-kakomon-2025-07-senyu",
    8: "https://manabist.org/mankan-kakomon-2025-08-management-association-corporation",
    9: "https://manabist.org/mankan-kakomon-2025-09-reconstruction-resolution",
    10: "https://manabist.org/mankan-kakomon-2025-10-danchi-nai-no-tatemono-no-ikkatsu-tatekaeketsugi",
    11: "https://manabist.org/mankan-kakomon-2025-11-resolution-to-demolish-the-building",
    12: "https://manabist.org/mankan-kakomon-2025-12-requirements-for-asserting-ownership-rights-against-third-parties",
    13: "https://manabist.org/mankan-kakomon-2025-13-mortgage",
    14: "https://manabist.org/mankan-kakomon-2025-14-civil-law-conclusion-of-a-contract",
    15: "https://manabist.org/mankan-kakomon-2025-15-civil-law-conclusion-of-a-contract2",
    16: "https://manabist.org/mankan-kakomon-2025-16-civil-law-ukeoi",
    17: "https://manabist.org/mankan-kakomon-2025-17-shakuchi-shakuya-ho",
    18: "https://manabist.org/mankan-kakomon-2025-18-kubun-tatemono-no-toki",
    19: "https://manabist.org/mankan-kakomon-2025-19-saisei-enkatsu-kaho",
    20: "https://manabist.org/mankan-kakomon-2025-20-city-planning-act",
    21: "https://manabist.org/mankan-kakomon-2025-21-building-standards-law",
    22: "https://manabist.org/mankan-kakomon-2025-22-suido",
    23: "https://manabist.org/mankan-kakomon-2025-23-shobo-ho",
    24: "https://manabist.org/mankan-kakomon-2025-24-bohan",
    25: "https://manabist.org/mankan-kakomon-2025-25-hyo-kan",
}

FW_DIGIT = str.maketrans("０１２３４５６７８９", "0123456789")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "mankan-master/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", errors="replace")


def entry_text(html: str) -> str:
    m = re.search(r'class="entry-content[^"]*"[^>]*>(.*)</div>\s*<footer', html, re.S)
    if not m:
        m = re.search(r'<article[^>]*>(.*)</article>', html, re.S)
    chunk = m.group(1) if m else html
    chunk = re.sub(r"<script[^>]*>.*?</script>", "", chunk, flags=re.S)
    chunk = re.sub(r"<style[^>]*>.*?</style>", "", chunk, flags=re.S)
    chunk = re.sub(r"<br\s*/?>", "\n", chunk, flags=re.I)
    chunk = re.sub(r"</p>", "\n", chunk, flags=re.I)
    chunk = re.sub(r"<[^>]+>", "", chunk)
    chunk = re.sub(r"\n{3,}", "\n\n", chunk)
    return chunk.strip()


def parse_correct_num(text: str) -> int | None:
    for pat in (
        r"正解[：:]\s*([０-９0-9]+)",
        r"正解は\s*([０-９0-9]+)\s*です",
    ):
        m = re.search(pat, text)
        if m:
            return int(m.group(1).translate(FW_DIGIT))
    return None


def verdict_label(raw: str) -> str:
    t = raw.strip()
    if re.search(r"誤り|不正|不適切|正しくない|適切でない|内容が正確でない", t):
        return "誤り"
    if re.search(r"正しい|妥当|適切|正当|内容が正確", t):
        return "正しい"
    return "解説"


def clean_note(note: str) -> str:
    note = re.sub(r"\s+", " ", note).strip()
    note = re.split(r"\s+(?:関連|関連記事|解法のポイント|シェアする)\s", note, maxsplit=1)[0]
    note = re.sub(r"\s+$", "", note)
    return note.strip()


def parse_choice_blocks(text: str) -> list[tuple[int, str, str]]:
    """(番号, 正誤ラベル, 本文)"""
    m = re.search(r"正解[：:]|正解は", text)
    body = text[m.start() :] if m else text
    m2 = re.search(r"各肢を検討していこう。", body)
    if m2:
        body = body[m2.end() :]
    body = re.split(r"\n(?:関連|関連記事|解法のポイント|コメントを書き込む|シェアする)", body, maxsplit=1)[0]

    parts = re.split(r"(?=\n[１２３４1-4]\s)", "\n" + body)
    out: list[tuple[int, str, str]] = []
    seen: set[int] = set()
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m3 = re.match(
            r"^([１２３４1-4])\s*(正しい|誤り|適切|不適切|妥当|不当|内容が正確|内容が正確でない)[。.]?\s*(.*)$",
            part,
            re.S,
        )
        if not m3:
            continue
        num = int(m3.group(1).translate(FW_DIGIT))
        if num in seen:
            continue
        label = verdict_label(m3.group(2))
        note = clean_note(m3.group(3).strip())
        if len(note) < 20:
            continue
        seen.add(num)
        out.append((num, label, note))
        if len(seen) == 4:
            break
    return sorted(out, key=lambda x: x[0])


def build_explanation(correct: int, blocks: list[tuple[int, str, str]]) -> str:
    lines = [f"正解は{correct}。"]
    for num, label, note in blocks:
        lines.append(f"\n選択肢{num}（{label}）　{note}")
    return "\n".join(lines).strip()


def article_to_explanation(html: str) -> tuple[int, str] | None:
    text = entry_text(html)
    correct = parse_correct_num(text)
    if correct is None:
        return None
    blocks = parse_choice_blocks(text)
    if not blocks:
        return None
    return correct, build_explanation(correct, blocks)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--year", type=int, default=2025)
    args = ap.parse_args()

    with DATA_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    updated = 0
    for qno, url in sorted(MANABIST_2025_URLS.items()):
        try:
            html = fetch(url)
        except Exception as exc:
            print(f"WARN Q{qno:02d}: fetch failed: {exc}", file=sys.stderr)
            continue
        parsed = article_to_explanation(html)
        if not parsed:
            print(f"WARN Q{qno:02d}: parse failed", file=sys.stderr)
            continue
        exp_correct_num, explanation = parsed
        row = next(
            (
                r
                for r in rows
                if int(r["exam_year"]) == args.year and int(r["question_no"]) == qno
            ),
            None,
        )
        if not row:
            print(f"WARN Q{qno:02d}: CSV row missing", file=sys.stderr)
            continue
        csv_correct = int(row["correct"])
        if exp_correct_num != csv_correct:
            print(
                f"WARN Q{qno:02d}: manabist correct={exp_correct_num} != CSV={csv_correct}",
                file=sys.stderr,
            )
        old = (row.get("explanation") or "").strip()
        if old == explanation.strip():
            continue
        print(f"UPDATE Q{qno:02d} ({len(explanation)} chars)")
        if not args.dry_run:
            row["explanation"] = explanation
            row["explanation_summary"] = ""
            row["explanation_correct"] = ""
            row["explanation_choices"] = ""
            row["explanation_point"] = ""
        updated += 1
        time.sleep(0.4)

    if args.dry_run:
        print(f"dry-run: would update {updated} row(s)")
        return 0

    if updated:
        with DATA_CSV.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    print(f"Updated {updated} row(s) in {DATA_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
