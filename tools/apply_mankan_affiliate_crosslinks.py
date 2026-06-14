#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フェーズF: マン管 公開比較記事4本の相互 related_links と本文 slug を整備。"""

from __future__ import annotations

import csv
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLISHED_AFFILIATE = (
    "affiliate-textbooks-recommend",
    "affiliate-problem-books",
    "affiliate-mock-exam-materials",
    "affiliate-free-vs-paid-study",
)

# 非アフィリ3 + アフィリ3 + 演習 + ASP（hub3本のみ）
RELATED_LINKS: dict[str, str] = {
    "affiliate-textbooks-recommend": ";".join(
        [
            "study-plan:学習計画の立て方",
            "textbook-selection:テキストの選び方",
            "self-study-start:独学の始め方",
            "affiliate-problem-books:おすすめ問題集3選",
            "affiliate-mock-exam-materials:おすすめ一問一答・速習",
            "affiliate-free-vs-paid-study:無料と有料教材の使い分け",
            "https://www.amazon.co.jp/dp/4300120218/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/484715343X/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/4844974297/ref=nosim?tag=ue083093-22",
        ]
    ),
    "affiliate-problem-books": ";".join(
        [
            "study-plan:学習計画の立て方",
            "textbook-selection:テキストの選び方",
            "past-questions-by-field:分野別過去問",
            "affiliate-textbooks-recommend:おすすめテキスト3選",
            "affiliate-mock-exam-materials:おすすめ一問一答・速習",
            "affiliate-free-vs-paid-study:無料と有料教材の使い分け",
            "https://www.amazon.co.jp/dp/4300120331/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/4844974300/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/4847153448/ref=nosim?tag=ue083093-22",
        ]
    ),
    "affiliate-mock-exam-materials": ";".join(
        [
            "study-plan:学習計画の立て方",
            "past-questions-by-field:分野別過去問",
            "final-week-prep:直前1週間の対策",
            "affiliate-textbooks-recommend:おすすめテキスト3選",
            "affiliate-problem-books:おすすめ問題集3選",
            "affiliate-free-vs-paid-study:無料と有料教材の使い分け",
            "https://www.amazon.co.jp/dp/4300120323/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/430012034X/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/4300120293/ref=nosim?tag=ue083093-22",
        ]
    ),
    "affiliate-free-vs-paid-study": ";".join(
        [
            "free-materials-online:無料教材の活用",
            "study-plan:学習計画の立て方",
            "self-study-start:独学の始め方",
            "affiliate-textbooks-recommend:おすすめテキスト3選",
            "affiliate-problem-books:おすすめ問題集3選",
            "affiliate-mock-exam-materials:おすすめ一問一答・速習",
            "past-question-strategy:過去問の使い方",
        ]
    ),
}

BODY_PATCHES: dict[str, dict[str, str]] = {
    "affiliate-textbooks-recommend": {
        "section_7_body": (
            "購入前に次を確認してください。1. Amazon販売ページで税込価格·在庫·2026年度版（2026年版）表記"
            "2. 要項の受験区分（マン管単独かW受験か）と目次の章立て"
            "3. 6/14開始なら残り25週・週10時間で第1周が終わるか"
            "たとえば6/14（日）に1冊決定→7月末まで第1周→8月からaffiliate-problem-booksで演習中心、という順が定番です。"
            "教材予算の全体像は、affiliate-free-vs-paid-study で無料範囲と最小2冊セットを先に整理すると迷いが減ります。"
            "study-plan-beginnerで月次計画を組み、速習·一問一答が必要になった段階でaffiliate-mock-exam-materialsを検討してください。"
            "価格は変動するため、申込・購入の直前に必ず販売ページで再確認してください。"
        ),
    },
    "affiliate-problem-books": {
        "section_7_body": (
            "購入前に次を確認してください。1. Amazon販売ページで税込価格·在庫·2026年度版表記"
            "2. メインテキストと同系列か（TAC·LEC·早稲田）"
            "3. 9月開始なら11/29までに通し50問を最低4回入れられるか"
            "購入順序の前後関係は、affiliate-free-vs-paid-study で段階投入の具体例を確認してください。"
            "study-plan-beginnerで週10時間×25週を先にカレンダー固定し、問題集は「9月1冊購入・11月追加なし」を原則にすると教材コストを抑えられます。"
            "価格は変動するため、購入の直前に必ず販売ページで再確認してください。"
        ),
    },
    "affiliate-mock-exam-materials": {
        "section_7_body": (
            "一問一答·速習は「メインテキスト80％読了後」に1冊だけ追加する80％ルールが安全です。"
            "6/14開始·残り25週なら、7〜8月はテキスト·速習、9月以降セレクト、10〜11月通し50問、の大枠をstudy-plan-beginnerで先に固定してください。"
            "テキスト·問題集が未決なら、affiliate-textbooks-recommend と affiliate-problem-books で先に1冊ずつ決めてから一問一答を選ぶと無駄がありません。"
            "購入前チェック：Amazonで税込価格·2026年度版表記·受験区分。"
            "11月以降の新規教材追加は抑え、解き直しに週10時間の50％以上を回す判断が定番です。"
            "価格は変動するため、購入直前に必ず販売ページで再確認してください。"
        ),
    },
    "affiliate-free-vs-paid-study": {
        "section_6_body": (
            "有料教材の優先順位は固定です。具体例として、9月第1週にテキスト1冊、"
            "10月第1週に同系統の問題集1冊、11月以降に一問一答（任意）——"
            "という順が24週逆算と整合します。"
            "| 順位 | 教材 || --- | --- || 1 | 2026年度版テキスト1冊 || 2 | 同系統問題集1冊 || 3 | 一問一答（任意） |"
            "2冊目を検討するのは、分野別正答率50％未満が2つ以上残る場合か、"
            "通し模試で15問以上時間切れが続く場合です。"
            "テキスト比較は affiliate-textbooks-recommend、問題集は affiliate-problem-books、"
            "一問一答は affiliate-mock-exam-materials へ。"
        ),
        "section_7_body": (
            "無料と有料の境界が決まったら、次の記事へ進んでください。"
            "・無料の手順詳細 → free-materials-online"
            "・月次計画 → study-plan（11/29から逆算）"
            "・テキスト1冊選び → textbook-selection と affiliate-textbooks-recommend"
            "・問題集1冊選び → affiliate-problem-books"
            "・一問一答（任意）→ affiliate-mock-exam-materials"
            "・独学の始め方 → self-study-start"
            "11月第1週以降は新規購入より解き直し90％を優先し、"
            "受験区分・試験日はマン管センター要項で必ず照合してください。"
            "本記事は収益リンクを含みません（asp=internal）。"
        ),
    },
}


def main() -> int:
    csv_path = ROOT / "data" / "guide_articles.csv"
    rows: list[dict[str, str]] = []
    updated = 0

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print("ERROR: empty CSV", file=sys.stderr)
            return 1
        for row in reader:
            slug = row["slug"]
            if slug in RELATED_LINKS:
                row["related_links"] = RELATED_LINKS[slug]
                updated += 1
            patches = BODY_PATCHES.get(slug)
            if patches:
                for col, value in patches.items():
                    row[col] = value
                updated += 1
            rows.append(row)

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

    print(f"OK: cross-links updated for {len(PUBLISHED_AFFILIATE)} affiliate articles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
