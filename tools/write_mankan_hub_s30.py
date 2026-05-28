#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""マン管マスター向け 知識ハブ30件（比較10・早見10・誤答10）CSV 書き込みヘルパー。"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.scaffold_knowledge_hub_article import (  # noqa: E402
    HUB_TYPES,
    append_row,
    existing_titles,
    load_fieldnames,
)
CATEGORY = "法令・制度"

OFFICIAL_ORG = "公益財団法人マンション管理センター"
OFFICIAL_URL = "https://www.mankan.org"

DISCLAIMER = (
    f"本ページは学習用の整理です。試験制度・数値・法令の正確な内容は"
    f"{OFFICIAL_ORG}（{OFFICIAL_URL}）の公式情報で必ず確認してください。"
)

SLUG_BY_TITLE: dict[str, str] = {
    "専有部分と共用部分の違い": "senyu-kyoyou",
    "法定共用部分と規約共用部分の違い": "hotei-kiyaku-kyoyou",
    "普通決議と特別多数決議の違い": "futsu-tokubetsu-ketsugi",
    "敷地と敷地利用権の違い": "shikichi-riyouken",
    "区分所有権と区分建物の違い": "kubun-shoyuken-tatemono",
    "集会と管理組合の違い": "shukai-kanri-kumiai",
    "招集通知と議事録の違い": "shuchou-gijiroku",
    "区分所有者と区分所有権の違い｜地位の整理": "kubun-shoyusha-ken",
    "一部共用部分と法定共用部分の違い": "ichibu-hotei-kyoyou",
    "規約と議決権の関係": "kiyaku-giketsuken",
    "マンション管理士試験の問題数と合格点": "mankan-goukaku-mondai",
    "管理業務士試験との同日受験（5問免除）": "kangyou-menjo-5mon",
    "マンション管理士試験の受験手数料": "mankan-juken-tesuryo",
    "マンション管理士試験時間120分": "mankan-jikan-120",
    "普通決議の過半数要件": "futsu-ketsugi-yohken",
    "特別多数決議 4分の3と建替え 5分の4": "tokubetsu-tatekae-wariai",
    "招集通知 1週間前と建替え 2か月前": "shuchou-tatekae-kigen",
    "集会の年1回開催義務": "shukai-nen1kai",
    "議事録の署名3人": "gijiroku-shomei-3",
    "集会招集請求 5分の1": "shukai-shuchou-5bun1",
    "専有部分と共用部分の混同": "senyu-kyoyou-kon",
    "法定共用部分と規約共用部分の混同": "hotei-kiyaku-kon",
    "普通決議と特別多数決議の混同": "futsu-tokubetsu-kon",
    "議決権1住戸1票の誤り": "giketsuken-1to1-go",
    "招集通知にない事項の決議": "shuchou-jikougai-ketsugi",
    "議事録署名の誤り": "gijiroku-shomei-go",
    "分離処分が可能という誤り": "bunri-shobun-go",
    "賃借人を区分所有者と誤認": "chintai-kubun-go",
    "管理組合加入が任意という誤り": "kanri-kanyu-ninni-go",
    "敷地と敷地利用権の混同": "shikichi-riyouken-kon",
}

ALLOWED_RELATED_TERMS: frozenset[str] = frozenset(
    {
        "専有部分",
        "共用部分",
        "法定共用部分",
        "規約共用部分",
        "一部共用部分",
        "区分所有者",
        "区分所有権",
        "区分建物",
        "敷地",
        "敷地利用権",
        "分離処分の禁止",
        "規約",
        "集会",
        "議決権",
        "普通決議",
        "特別多数決議",
        "集会の招集",
        "招集通知",
        "議事録",
        "管理組合",
    }
)


def _check_related_terms(raw: str) -> None:
    terms = [t.strip() for t in raw.split(";") if t.strip()]
    if len(terms) < 2:
        raise ValueError(f"related_terms は2件以上必要です: {raw!r}")
    for term in terms:
        if term not in ALLOWED_RELATED_TERMS:
            raise ValueError(f"related_terms に未許可の用語があります: {term!r}")


def _lead(*parts: str) -> str:
    body = "".join(parts)
    if len(body) < 30:
        raise ValueError("article_lead は30文字以上必要です")
    return body


def build_compare_row(
    title: str,
    *,
    subject_a: str,
    subject_b: str,
    summary: str,
    compare_rows: list[dict[str, Any]],
    article_title: str,
    article_lead: str,
    exam_points: str,
    common_mistakes: str,
    memory_tip: str,
    related_terms: str,
    tags: str = "区分所有法;整理",
    faqs: list[tuple[str, str]] | None = None,
) -> dict[str, str]:
    _check_related_terms(related_terms)
    labels = f"{subject_a};{subject_b}"
    if faqs is None:
        faqs = [
            (
                f"{subject_a}と{subject_b}の違いは何ですか？",
                f"{subject_a}は{subject_b}と目的が異なります。"
                f"{summary}表の定義行と試験の見方行をセットで確認すると、"
                f"四択の言い換え問題でも取り違えにくくなります。{DISCLAIMER}",
            ),
            (
                "どちらから覚えるのが効率的ですか？",
                f"用語解説で{subject_a}と{subject_b}の定義を押さえたうえで、"
                "この比較表で差分だけを復習する流れが効率的です。"
                "過去問で間違えた肢があれば表の引っかけ行に追記してください。",
            ),
            (
                "マンション管理士試験ではどう出題されますか？",
                "定義の言い換え、帰属・主体の取り違え、決議要件との組み合わせが"
                "典型です。数字や期限が絡む場合は早見表記事もあわせて確認してください。",
            ),
            (
                "関連用語はどこで深掘りできますか？",
                f"ページ下部の関連用語リンクから用語解説へ進み、"
                f"{subject_a}・{subject_b}それぞれの条文根拠まで読み返してください。"
                "比較表と用語解説を交互に読むと定着しやすくなります。",
            ),
        ]
    slug = SLUG_BY_TITLE.get(title)
    if not slug:
        raise KeyError(f"SLUG_BY_TITLE に slug がありません: {title!r}")
    row: dict[str, str] = {
        "slug": slug,
        "title": title,
        "category": CATEGORY,
        "tags": tags,
        "summary": summary,
        "col_labels": labels,
        "compare_rows": json.dumps(compare_rows, ensure_ascii=False),
        "article_title": article_title,
        "article_lead": _lead(article_lead, " ", DISCLAIMER),
        "exam_points": exam_points,
        "common_mistakes": common_mistakes,
        "memory_tip": memory_tip,
        "related_terms": related_terms,
    }
    for i, (q, a) in enumerate(faqs[:4], start=1):
        row[f"faq_{i}_question"] = q
        row[f"faq_{i}_answer"] = a
    return row


def build_numbers_row(
    title: str,
    *,
    summary: str,
    highlight: str,
    item_rows: list[dict[str, str]],
    article_title: str,
    article_lead: str,
    exam_points: str,
    common_mistakes: str,
    memory_tip: str,
    related_terms: str,
    tags: str = "数字;期限",
    faqs: list[tuple[str, str]] | None = None,
) -> dict[str, str]:
    _check_related_terms(related_terms)
    if faqs is None:
        faqs = [
            (
                f"{title}の代表的な数字は？",
                f"早見表の value 列を参照してください。{highlight}がこの記事の要点です。"
                f"年度や制度改正で変わる場合があるため、{OFFICIAL_ORG}の試験要項も確認してください。",
            ),
            (
                "早見表記事の使い方は？",
                "学習中の確認と直前の総復習向けです。数字だけ暗記せず、"
                "note 列の条件（誰が・いつ・例外）までセットで覚えてください。",
            ),
            (
                "試験ではどのような問われ方をしますか？",
                "数値そのものの暗記、近い数字との選択、条件の追加（例外・主体）が典型です。"
                "誤答パターン記事とあわせて読むと、引っかけ肢を見抜きやすくなります。",
            ),
            (
                "公式情報はどこで確認できますか？",
                f"{OFFICIAL_ORG}（{OFFICIAL_URL}）の試験要項・公式テキストで"
                "最新の数値と制度を必ず裏取りしてください。",
            ),
        ]
    slug = SLUG_BY_TITLE.get(title)
    if not slug:
        raise KeyError(f"SLUG_BY_TITLE に slug がありません: {title!r}")
    row = {
        "slug": slug,
        "title": title,
        "category": CATEGORY,
        "tags": tags,
        "summary": summary,
        "highlight": highlight,
        "item_rows": json.dumps(item_rows, ensure_ascii=False),
        "article_title": article_title,
        "article_lead": _lead(article_lead, " ", DISCLAIMER),
        "exam_points": exam_points,
        "common_mistakes": common_mistakes,
        "memory_tip": memory_tip,
        "related_terms": related_terms,
    }
    for i, (q, a) in enumerate(faqs[:4], start=1):
        row[f"faq_{i}_question"] = q
        row[f"faq_{i}_answer"] = a
    return row


def build_mistakes_row(
    title: str,
    *,
    summary: str,
    confusion_point: str,
    pattern_rows: list[dict[str, str]],
    article_title: str,
    article_lead: str,
    exam_points: str,
    common_mistakes: str,
    memory_tip: str,
    related_terms: str,
    tags: str = "誤答;区分所有法",
    faqs: list[tuple[str, str]] | None = None,
) -> dict[str, str]:
    _check_related_terms(related_terms)
    if faqs is None:
        faqs = [
            (
                f"{title}の典型誤答は？",
                "表の wrong 列に、正しそうに見える誤りの言い回しをまとめています。"
                "自分が過去問で間違えた肢があれば追記して復習ノート代わりに使えます。",
            ),
            (
                "比較表記事との使い分けは？",
                "比較表は制度の差分整理、誤答パターンは選択肢レベルの引っかけ整理です。"
                "同じテーマでも両方読むと、理解と演習対策の両方に効きます。",
            ),
            (
                "試験対策でどう活用しますか？",
                "過去問演習の前後に読み、間違えた問題の理由と表の trap 列を照合してください。"
                "声に出して wrong→correct と置き換えると記憶に残りやすくなります。",
            ),
            (
                "関連用語はどこで確認できますか？",
                "ページ下部の関連用語から用語解説へ進み、定義と数字を確認してから解き直してください。",
            ),
        ]
    slug = SLUG_BY_TITLE.get(title)
    if not slug:
        raise KeyError(f"SLUG_BY_TITLE に slug がありません: {title!r}")
    row = {
        "slug": slug,
        "title": title,
        "category": CATEGORY,
        "tags": tags,
        "summary": summary,
        "confusion_point": confusion_point,
        "pattern_rows": json.dumps(pattern_rows, ensure_ascii=False),
        "article_title": article_title,
        "article_lead": _lead(article_lead, " ", DISCLAIMER),
        "exam_points": exam_points,
        "common_mistakes": common_mistakes,
        "memory_tip": memory_tip,
        "related_terms": related_terms,
    }
    for i, (q, a) in enumerate(faqs[:4], start=1):
        row[f"faq_{i}_question"] = q
        row[f"faq_{i}_answer"] = a
    return row


def append_hub_row(hub_type: str, row: dict[str, str]) -> None:
    append_row(hub_type, row)


def write_rows(hub_type: str, rows: list[dict[str, str]], *, reset: bool = False) -> int:
    path = HUB_TYPES[hub_type]["csv"]
    if reset and path.is_file():
        fieldnames = load_fieldnames(hub_type)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
    written = 0
    for row in rows:
        title = row.get("title", "").strip()
        if title in existing_titles(hub_type):
            continue
        append_hub_row(hub_type, row)
        written += 1
    return written


def write_batch(
    *,
    comparisons: list[dict[str, str]],
    numbers: list[dict[str, str]],
    mistakes: list[dict[str, str]],
    reset: bool = True,
) -> tuple[int, int, int]:
    c = write_rows("compare", comparisons, reset=reset)
    n = write_rows("numbers", numbers, reset=reset)
    m = write_rows("mistakes", mistakes, reset=reset)
    return c, n, m
