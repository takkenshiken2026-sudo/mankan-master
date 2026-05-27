#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guide_articles.csv のプレースホルダ・重複文・誤リンクを修正する（一回限りの修復用）."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "guide_articles.csv"

DUP_PHRASE = "対象資格の最新情報に照合してください。"
NUM_OLD = "数値・期限は対象試験の公式要項で必ず確認してください。"
NUM_NEW = "数値・期限はマンション管理センターの受験案内・試験要項で必ず確認してください。"

FAQ3: dict[str, tuple[str, str]] = {
    "exam-overview": (
        "学習を始める順番は？",
        "まずマンション管理センターの公式サイトで受験案内・試験要項を確認し、申込期限と出題範囲をメモします。"
        "そのうえで本サイトの過去問を1年度分解き、間違えた語句は用語解説で定義と試験論点まで戻って確認してください。"
        "制度の数値は年度で変わるため、申込直前にも公式ページを見直すと安心です。",
    ),
    "study-plan": (
        "1日の学習量の目安は？",
        "生活リズムに合わせ、過去問・用語・復習の3つを短時間でも回せる量にします。"
        "完璧な暗記より、間違いの理由（知識不足・混同・読み落としなど）をメモし、翌日と数日後に同じ問題を解き直す習慣を優先してください。",
    ),
    "past-question-strategy": (
        "何問から始めるとよいですか？",
        "最初は1年度分を通しで解き、出題形式と選択肢の聞かれ方に慣れます。"
        "不正解と自信のない問題だけ解説を読み、関連用語ページで似た語の違いまで確認してください。"
        "記録は「分野・用語・理由」の3点があれば十分で、解きっぱなしにしないことが重要です。",
    ),
    "glossary-how-to": (
        "用語は何件から読めばよいですか？",
        "過去問や実践演習で実際に出た語句から読み始め、関連用語リンクで似た語をまとめて確認します。"
        "重要度の高い語は個別ページで試験論点・よくある誤解・例題まで読み返し、演習に戻って定着を確かめてください。",
    ),
    "self-study-roadmap": (
        "独学で教材は何冊必要ですか？",
        "公式要項と本サイトの過去問・実践演習・用語解説で足りる場合も多いです。"
        "教材を増やす前に過去問で弱点を可視化し、足りない分野だけテキストや講座を選ぶと、情報過多で迷いにくくなります。",
    ),
}


def clean_cell(value: str) -> str:
    if not value:
        return value
    s = value
    s = s.replace("◯◯試験", "マンション管理士試験")
    s = s.replace("Sampleマスター", "マン管マスター")
    s = s.replace("https://example.com/", "https://www.mankan.org/")
    s = s.replace(
        "試験実施団体（公式）|https://www.mankan.org/",
        "公益財団法人マンション管理センター（公式）|https://www.mankan.org/",
    )
    s = s.replace(NUM_OLD, NUM_NEW)
    while NUM_NEW + " " + NUM_NEW in s:
        s = s.replace(NUM_NEW + " " + NUM_NEW, NUM_NEW)
    # 同一フレーズの連続・繰り返しを除去
    while DUP_PHRASE + " " + DUP_PHRASE in s:
        s = s.replace(DUP_PHRASE + " " + DUP_PHRASE, DUP_PHRASE)
    s = re.sub(r"。?\s*" + re.escape(DUP_PHRASE) + r"(?:\s*" + re.escape(DUP_PHRASE) + r")+", "", s)
    s = s.replace("対象試験の公式要項", "マンション管理士試験の試験要項")
    s = s.replace("対象資格の最新情報", "マンション管理士試験の最新情報")
    dup_lead = (
        "公式情報を先に確認し、このサイトの演習と用語解説で弱点を補強する流れを推奨します。 "
        "公式情報を先に確認し、このサイトの演習と用語解説で弱点を補強する流れを推奨します。"
    )
    s = s.replace(
        dup_lead,
        "公式情報を先に確認し、このサイトの演習と用語解説で弱点を補強する流れを推奨します。",
    )
    return s.strip()


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8-sig")))
    if not rows:
        print("no rows", file=__import__("sys").stderr)
        return 1

    fieldnames = list(rows[0].keys())
    if "faq_3_question" not in fieldnames:
        idx = fieldnames.index("faq_3_answer")
        fieldnames.insert(idx, "faq_3_question")

    for row in rows:
        for key in list(row.keys()):
            if row.get(key):
                row[key] = clean_cell(row[key])
        slug = (row.get("slug") or "").strip()
        if slug in FAQ3:
            q, a = FAQ3[slug]
            row["faq_3_question"] = q
            row["faq_3_answer"] = a

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    text = CSV_PATH.read_text(encoding="utf-8")
    print("◯◯:", text.count("◯◯"))
    print("example.com:", text.count("example.com"))
    print("Sampleマスター:", text.count("Sampleマスター"))
    print("6連続照合:", "照合してください。 マンション" in text and text.count(DUP_PHRASE) > 3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
