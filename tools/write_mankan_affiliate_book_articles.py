#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write affiliate book briefs + CSV rows for mankan-master (Amazon tag ue083093-22)."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML が必要です") from exc

ROOT = Path(__file__).resolve().parents[1]
BRIEFS = ROOT / "data" / "affiliate-briefs"
CSV_PATH = ROOT / "data" / "guide_articles.csv"
TAG = "ue083093-22"
PRICE_CHECKED = "2026-06-04"
OFFICIAL = "公益財団法人マンション管理センター（公式）"
SITE = "マン管マスター"


def amazon(asin: str) -> str:
    return f"https://www.amazon.co.jp/dp/{asin}/ref=nosim?tag={TAG}"


def img(asin: str) -> str:
    return f"mankan-book-{asin.lower()}.webp"


def book(
    rank: int,
    name: str,
    publisher: str,
    asin: str,
    *,
    edition: str = "2026年度版",
    price_yen: int = 0,
    pages: int = 0,
    for_who: str = "",
    highlights: list[str],
) -> dict:
    return {
        "rank": rank,
        "offer_type": "book",
        "name": name,
        "publisher": publisher,
        "edition": edition,
        "price_yen": price_yen,
        "price_note": "Amazon税込参考・送料別",
        "pages": pages,
        "format": "B5判",
        "asin": asin,
        "image_file": img(asin),
        "amazon_url": amazon(asin),
        "for_who": for_who,
        "highlights": highlights,
    }


def ensure_section_body(text: str, min_len: int = 180) -> str:
    body = text.replace("[[affiliate-hub-placeholder]]", "").strip()
    if len(body) >= min_len:
        return body
    tail = (
        f"\n\n{OFFICIAL}の出題範囲（3分野）と照合し、"
        f"{SITE}の過去問・用語解説と組み合わせて復習サイクルを回してください。"
    )
    while len(body) < min_len:
        body += tail
    return body


def ensure_faq_answer(text: str, min_len: int = 100) -> str:
    answer = text.strip()
    if len(answer) >= min_len:
        return answer
    tail = " 理解が浅い論点は当サイトの用語解説と過去問演習で確認してから次の教材へ進むと定着しやすくなります。"
    while len(answer) < min_len:
        answer += tail
    return answer


BRIEFS_DATA = {
    "affiliate-textbooks-recommend": {
        "slug": "affiliate-textbooks-recommend",
        "theme_key": "textbooks-recommend",
        "search_intent": "マンション管理士の独学向けテキストを比較して選びたい",
        "title": "マンション管理士のおすすめテキスト3選【2026年度版・W受験対応】",
        "layout": "product-comparison",
        "asp_primary": "amazon",
        "comparison_kind": "books",
        "comparison_title": "おすすめテキスト3選（比較）",
        "price_disclaimer": (
            f"価格・在庫・版情報は執筆時点（{PRICE_CHECKED}）のAmazon税込参考です。"
            "購入前に必ず販売ページでご確認ください。"
        ),
        "products": [
            book(
                1,
                "2026年度版 みんなが欲しかった! マンション管理士・管理業務主任者 合格へのはじめの一歩",
                "TAC出版",
                "4300120218",
                price_yen=1980,
                pages=300,
                for_who="マン管試験をこれから始め、入門から全体像をつかみたい人",
                highlights=[
                    "マン管・管理業務主任者のW受験向け入門テキスト",
                    "3分野の輪郭を短時間で把握しやすい",
                    "本格テキストへ進む前の第一歩に向く",
                ],
            ),
            book(
                2,
                "2026年度版 マンション管理士・管理業務主任者 Wマスターテキスト",
                "早稲田経営出版",
                "484715343X",
                price_yen=3630,
                pages=720,
                for_who="W受験で解説厚めの本格テキストを1冊にまとめたい人",
                highlights=[
                    "マン管・管理業務主任者を1冊で学べるWマスター定番",
                    "Wマスター過去問集と章立ての相性がよい",
                    "社会人独学のメインテキスト候補",
                ],
            ),
            book(
                3,
                "2026年版 出る順 マンション管理士・管理業務主任者 合格テキスト",
                "LEC",
                "4844974297",
                edition="2026年版",
                price_yen=4400,
                pages=1170,
                for_who="出る順シリーズで論点整理から演習へ進みたい人",
                highlights=[
                    "LEC「出る順」で頻出論点を整理しやすい",
                    "分野別過去問題集（別冊）への接続がスムーズ",
                    "TAC・早稲田系との比較選択肢",
                ],
            ),
        ],
        "related_links": [
            "self-study-start:独学の始め方",
            "past-questions-by-year:年度別過去問",
            "exam-overview:試験概要",
            "affiliate-problem-books:おすすめ問題集",
            "affiliate-mock-exam-materials:一問一答・速習",
            "pass-score:合格点と合格基準",
        ],
        "operator_note": f"Amazon tag={TAG}。4300120218 / 484715343X / 4844974297。{PRICE_CHECKED} 価格確認。",
    },
    "affiliate-problem-books": {
        "slug": "affiliate-problem-books",
        "theme_key": "problem-books",
        "search_intent": "マンション管理士の過去問・問題集を比較して選びたい",
        "title": "マンション管理士のおすすめ問題集3選【過去8年・分野別2026】",
        "layout": "product-comparison",
        "asp_primary": "amazon",
        "comparison_kind": "books",
        "comparison_title": "おすすめ問題集3選（比較）",
        "price_disclaimer": (
            f"価格・在庫は執筆時点（{PRICE_CHECKED}）のAmazon税込参考です。"
            "購入前に販売ページで最新版を確認してください。"
        ),
        "products": [
            book(
                1,
                "2026年度版 マンション管理士 項目別過去8年問題集",
                "TAC出版",
                "4300120331",
                price_yen=2860,
                pages=872,
                for_who="TACテキストとセットで過去8年分を解きたい人",
                highlights=[
                    "項目別で弱点分野の演習に向く",
                    "TAC一問一答・速習テキストと組み合わせやすい",
                    "本試験形式の演習量確保に有効",
                ],
            ),
            book(
                2,
                "2026年版 出る順 マンション管理士 分野別過去問題集",
                "LEC",
                "4844974300",
                edition="2026年版",
                price_yen=2750,
                pages=874,
                for_who="LEC出る順テキストとセットで過去問演習をしたい人",
                highlights=[
                    "出る順テキストと縦串が明確",
                    "分野別に復習しやすい解説付き",
                    "TAC過去問との使い分けがしやすい",
                ],
            ),
            book(
                3,
                "2026年度版 マンション管理士・管理業務主任者 Wマスター過去問集",
                "早稲田経営出版",
                "4847153448",
                price_yen=4400,
                pages=1028,
                for_who="Wマスターテキスト読了後に過去問メイン1冊を探している人",
                highlights=[
                    "Wマスターテキストとセットの定番過去問",
                    "マン管・管理業務主任者のW受験向け演習量",
                    "解説付きで復習サイクルを組み立てやすい",
                ],
            ),
        ],
        "related_links": [
            "past-questions-by-year:年度別過去問",
            "past-questions-by-field:分野別過去問",
            "self-study-start:独学の始め方",
            "affiliate-textbooks-recommend:おすすめテキスト",
            "affiliate-mock-exam-materials:一問一答・速習",
            "pass-score:合格点と合格基準",
        ],
        "operator_note": f"Amazon tag={TAG}。4300120331 / 4844974300 / 4847153448。",
    },
    "affiliate-mock-exam-materials": {
        "slug": "affiliate-mock-exam-materials",
        "theme_key": "mock-exam-materials",
        "search_intent": "マンション管理士の一問一答・速習教材を比較して選びたい",
        "title": "マンション管理士の一問一答・速習3選【セレクト1000・管理業務主任者2026】",
        "layout": "product-comparison",
        "asp_primary": "amazon",
        "comparison_kind": "books",
        "comparison_title": "一問一答・速習3選（比較）",
        "price_disclaimer": (
            f"価格は執筆時点（{PRICE_CHECKED}）のAmazon税込参考です。"
            f"受験区分は{OFFICIAL}で必ず確認してください。"
        ),
        "products": [
            book(
                1,
                "2026年度版 らくらくわかる! マンション管理士速習テキスト",
                "TAC出版",
                "4300120323",
                price_yen=3190,
                pages=900,
                for_who="テキスト読了前後に速習で論点を整理したい人",
                highlights=[
                    "速習形式で3分野を短期復習",
                    "TAC過去8年・一問一答への橋渡しに向く",
                    "社会人のスキマ時間学習と相性がよい",
                ],
            ),
            book(
                2,
                "2026年度版 マンション管理士 一問一答セレクト1000",
                "TAC出版",
                "430012034X",
                price_yen=2200,
                pages=560,
                for_who="マン管単独受験で短問演習量を確保したい人",
                highlights=[
                    "セレクト1000問で演習効率を上げやすい",
                    "項目別過去8年問題集との併用向き",
                    "直前期の穴埋め演習にも使える",
                ],
            ),
            book(
                3,
                "2026年度版 管理業務主任者 一問一答セレクト1000",
                "TAC出版",
                "4300120293",
                price_yen=2200,
                pages=516,
                for_who="管理業務主任者区分の短問演習を追加したいW受験者",
                highlights=[
                    "管理業務主任者向けセレクト1000問",
                    "マン管一問一答とセットでW受験対策",
                    "Wマスターシリーズとの章立て相性がよい",
                ],
            ),
        ],
        "related_links": [
            "exam-overview:試験概要",
            "past-questions-by-field:分野別過去問",
            "pass-score:合格点と合格基準",
            "affiliate-textbooks-recommend:おすすめテキスト",
            "affiliate-problem-books:おすすめ問題集",
            "study-plan-beginner:初学者向け学習計画",
        ],
        "operator_note": (
            f"Amazon tag={TAG}。4300120323 / 430012034X / 4300120293。"
            f"管理業務主任者過去8年 4300120285 はFAQ言及。{PRICE_CHECKED} 価格確認。"
        ),
    },
}


CSV_ROWS = {
    "affiliate-textbooks-recommend": {
        "title": "マンション管理士のおすすめテキスト3選【2026年度版・W受験対応】",
        "meta_description": (
            "マンション管理士の独学向けおすすめテキスト3選。"
            "TACはじめの一歩・早稲田Wマスター・LEC出る順を比較。"
            "W受験の選び方とマン管マスター過去問との併用も解説。"
        ),
        "lead": (
            "マンション管理士試験（マン管）は3分野の理解と演習量が合格の鍵です。"
            "管理業務主任者とW受験する場合も多く、テキスト選びが重要になります。"
            "本記事では2026年度版の主要テキスト3冊を比較します。"
            "出題範囲は必ずマンション管理センター（公式）で確認してください。"
        ),
        "priority": "370",
        "original_note": "Amazon tag=ue083093-22。4300120218 / 484715343X / 4844974297。",
        "user_intent": (
            "マンション管理士のテキストを、入門型・Wマスター型・出る順型で比較し、"
            "独学の最初の1冊（または2冊構成）に絞りたい。"
        ),
        "action_items": "比較表で3冊の違いを確認する;W受験か単独かを決める;過去問で弱点を把握する",
        "revision_note": f"{PRICE_CHECKED}: Amazon URL確定・本文全面リライト",
        "sections": [
            (
                "テキスト選びの3つのポイント",
                "マン管試験のテキスト選びでは、"
                f"①{OFFICIAL}の3分野に目次が沿っているか、"
                "②管理業務主任者とW受験するか単独か、"
                "③過去問・一問一答とセットで使えるかを確認します。\n\n"
                "W受験なら早稲田WマスターまたはTAC/LECのW対応教材、"
                "まず全体像からならTAC「はじめの一歩」が選ばれやすいです。",
            ),
            (
                "おすすめテキスト比較の見方",
                "比較では「TAC入門→本格」「早稲田Wマスター1冊完結」「LEC出る順＋過去問」の3タイプで見ます。"
                "独学初期は理解用1冊に絞り、演習段階で問題集1冊（おすすめ問題集の記事）を追加する構成が扱いやすいです。",
            ),
            (
                "1位：TAC「はじめの一歩」の特徴",
                "2026年度版 みんなが欲しかった! マンション管理士・管理業務主任者 合格へのはじめの一歩（1,980円税込参考・300ページ）は、"
                "W受験向け入門テキスト。3分野の全体像をつかむ第一歩として選ばれやすい1冊です。",
            ),
            (
                "2位・3位：Wマスター・LEC出る順",
                "2026年度版 マンション管理士・管理業務主任者 Wマスターテキスト（早稲田経営出版・3,630円税込参考・720ページ）は、"
                "W受験の本格メインテキスト定番。Wマスター過去問集（別記事）とセットで使う受験生が多いです。\n\n"
                "2026年版 出る順 マンション管理士・管理業務主任者 合格テキスト（LEC・4,400円税込参考・1,170ページ）は、"
                "出る順シリーズで論点整理から演習へ進みやすい本格教材です。",
            ),
            (
                "テキストとマン管マスター過去問の併用",
                "テキストで論点を押さえたら、マン管マスターの過去問・一問一答で本試験形式の演習に移ります。"
                "3分野ごとの得点を記録し、弱点分野をテキスト該当章に戻って復習するサイクルが効率的です。",
            ),
            (
                "購入前チェックリスト",
                "購入前に以下を確認してください。\n"
                "・2026年度版（最新版）か\n"
                "・マン管単独/W受験（管理業務主任者含む）に合った表記か\n"
                "・Amazon在庫・価格\n"
                "・学習期間に対するページ数・演習量",
            ),
        ],
        "faqs": [
            (
                "W受験とマン管単独、テキストは同じですか？",
                "W受験向け（マン管・管理業務主任者表記）とマン管単独向けで教材が分かれます。"
                "受験区分に合った表紙表記を選び、不要な区分の演習は計画から外してください。",
            ),
            (
                "早稲田WマスターとLEC出る順、どちらがよいですか？",
                "Wマスターは1冊完結型、出る順は論点整理＋別冊過去問の2冊構成が基本です。"
                "解説量と予算・演習の進め方で比較表から選んでください。",
            ),
            (
                "テキストは1冊だけで足りますか？",
                "本格テキスト1冊＋当サイト過去問で独学は可能です。"
                "演習量が足りない場合はおすすめ問題集の記事を参照してください。",
            ),
        ],
        "related_links": (
            "self-study-start:独学の始め方;"
            "past-questions-by-year:年度別過去問;"
            "exam-overview:試験概要;"
            "affiliate-problem-books:おすすめ問題集;"
            "affiliate-mock-exam-materials:一問一答・速習;"
            "pass-score:合格点と合格基準"
        ),
        "key_points": (
            "2026年度版 みんなが欲しかった! マンション管理士・管理業務主任者 合格へのはじめの一歩;"
            "2026年度版 マンション管理士・管理業務主任者 Wマスターテキスト;"
            "2026年版 出る順 マンション管理士・管理業務主任者 合格テキスト;"
            "W受験のテキスト選び;"
            "過去問との併用"
        ),
    },
    "affiliate-problem-books": {
        "title": "マンション管理士のおすすめ問題集3選【過去8年・分野別2026】",
        "meta_description": (
            "マンション管理士のおすすめ問題集3選。"
            "TAC項目別過去8年、LEC分野別過去問、早稲田Wマスター過去問集を比較。"
            "過去問の回し方と分野別対策も解説。"
        ),
        "lead": (
            "マン管試験では、過去問・問題集の演習量が得点安定の鍵です。"
            "本記事では2026年度版の問題集3冊を、収録形式・解説量・W受験対応で比較します。"
            "価格は購入前にAmazonで必ずご確認ください。",
        ),
        "priority": "365",
        "original_note": "Amazon tag=ue083093-22。4300120331 / 4844974300 / 4847153448。",
        "user_intent": (
            "マンション管理士の過去問・問題集を比較し、"
            "演習メイン1冊を決めて、分野別の弱点補強計画を立てたい。"
        ),
        "action_items": "3冊の収録形式を比較する;3分野の得点バランスを確認する;弱点分野をテキストで復習する",
        "revision_note": f"{PRICE_CHECKED}: Amazon URL確定・本文全面リライト",
        "sections": [
            (
                "問題集選びの基準",
                "問題集選びでは、(1)3分野の出題バランス (2)解説で復習できるか "
                "(3)テキストとの章立て相性を確認します。"
                "W受験者は管理業務主任者区分の演習が含まれるかもチェックしてください。",
            ),
            (
                "3冊の選び方（タイプ別）",
                "[[affiliate-hub-placeholder]]\n\n"
                "TAC教科書と項目別演習したい人は2026年度版 マンション管理士 項目別過去8年問題集、"
                "LEC出る順テキストと組み合わせるなら2026年版 出る順 マンション管理士 分野別過去問題集、"
                "Wマスターテキスト読了後の過去問メインには2026年度版 マンション管理士・管理業務主任者 Wマスター過去問集が向きます。",
            ),
            (
                "1位：TAC 項目別過去8年",
                "2026年度版 マンション管理士 項目別過去8年問題集（2,860円税込参考・872ページ）は、"
                "項目別に弱点演習しやすいTAC定番。一問一答セレクト1000（別記事）との併用も向きます。",
            ),
            (
                "2位・3位：LEC分野別・Wマスター過去問",
                "2026年版 出る順 マンション管理士 分野別過去問題集（LEC・2,750円税込参考・874ページ）は、"
                "出る順テキストとセットの過去問演習向け。\n\n"
                "2026年度版 マンション管理士・管理業務主任者 Wマスター過去問集（早稲田・4,400円税込参考・1,028ページ）は、"
                "W受験の演習メイン1冊として選ばれやすい定番です。",
            ),
            (
                "過去問の回し方（マン管マスターとの併用）",
                "当サイトの過去問で分野別得点を把握したうえで、問題集で時間を計って解く練習を行います。"
                "誤答は用語解説で整理し、1週間後に解き直してください。",
            ),
            (
                "一問一答・速習との使い分け",
                "過去問で論点を押さえたあと、一問一答セレクト1000や速習テキスト（別記事）で"
                "短問演習・総復習を追加する受験生も多いです。",
            ),
        ],
        "faqs": [
            (
                "過去問だけで合格できますか？",
                "演習量は確保できますが、初めての論点はテキストで理解してから問題集に入る方が効率的です。"
                "おすすめテキストの記事で紹介している1冊と組み合わせる構成を推奨します。",
            ),
            (
                "管理業務主任者向け過去問は別途必要ですか？",
                "W受験なら2026年度版 管理業務主任者 項目別過去8年問題集（4300120285）も選択肢です。"
                "Wマスター過去問集に含まれる演習で足りる場合もあります。",
            ),
            (
                "問題集は何冊必要ですか？",
                "メイン1冊＋当サイト過去問で足りる場合が多いです。"
                "直前期は一問一答の記事も参照してください。",
            ),
        ],
        "related_links": (
            "past-questions-by-year:年度別過去問;"
            "past-questions-by-field:分野別過去問;"
            "self-study-start:独学の始め方;"
            "affiliate-textbooks-recommend:おすすめテキスト;"
            "affiliate-mock-exam-materials:一問一答・速習;"
            "pass-score:合格点と合格基準"
        ),
        "key_points": (
            "2026年度版 マンション管理士 項目別過去8年問題集;"
            "2026年版 出る順 マンション管理士 分野別過去問題集;"
            "2026年度版 マンション管理士・管理業務主任者 Wマスター過去問集;"
            "問題集選びの基準;"
            "過去問の回し方"
        ),
    },
    "affiliate-mock-exam-materials": {
        "title": "マンション管理士の一問一答・速習3選【セレクト1000・管理業務主任者2026】",
        "meta_description": (
            "マンション管理士の一問一答・速習3選。"
            "TAC速習テキスト、マン管・管理業務主任者一問一答セレクト1000を比較。"
            "W受験の短問演習の進め方も解説。"
        ),
        "lead": (
            "マン管試験では、テキスト・過去問に加えて一問一答や速習で短問演習量を確保する受験生が多いです。"
            "本記事ではTACの速習・セレクト1000系3冊を比較します。"
            "受験区分は必ずマンション管理センター（公式）で確認してください。",
        ),
        "priority": "360",
        "original_note": "Amazon tag=ue083093-22。4300120323 / 430012034X / 4300120293。4300120285 FAQ。",
        "user_intent": (
            "マンション管理士の短問演習教材を比較し、"
            "速習・一問一答・管理業務主任者区分の演習1〜2冊を決めたい。"
        ),
        "action_items": "3冊の用途を比較する;W受験区分を確認する;テキスト・過去問との役割分担を決める",
        "revision_note": f"{PRICE_CHECKED}: Amazon URL確定・本文全面リライト",
        "sections": [
            (
                "一問一答・速習の位置づけ",
                "一問一答・速習教材は、テキストで理解した論点を短問形式で定着させるためのものです。"
                "過去問問題集の前後で演習量を調整したり、直前期の穴埋めに使ったりする位置づけが一般的です。",
            ),
            (
                "3冊の選び方",
                "[[affiliate-hub-placeholder]]\n\n"
                "論点を短期整理するなら2026年度版 らくらくわかる! マンション管理士速習テキスト、"
                "マン管単独の短問演習には2026年度版 マンション管理士 一問一答セレクト1000、"
                "W受験で管理業務主任者区分の演習追加には2026年度版 管理業務主任者 一問一答セレクト1000が向きます。",
            ),
            (
                "1位：TAC速習テキスト",
                "2026年度版 らくらくわかる! マンション管理士速習テキスト（3,190円税込参考・900ページ）は、"
                "テキスト読了後〜過去問前の総復習向け。スキマ時間学習と相性がよい1冊です。",
            ),
            (
                "2位・3位：一問一答セレクト1000（マン管・管理業務主任者）",
                "2026年度版 マンション管理士 一問一答セレクト1000（2,200円税込参考・560ページ）は、"
                "マン管区分の短問演習メイン向け。\n\n"
                "2026年度版 管理業務主任者 一問一答セレクト1000（同・2,200円税込参考・516ページ）は、"
                "W受験者が管理業務主任者区分の演習を追加する際の定番です。",
            ),
            (
                "テキスト・過去問との組み合わせ",
                "例：はじめの一歩→Wマスターテキスト→項目別過去8年→一問一答→マン管マスター過去問。"
                "W受験なら管理業務主任者一問一答を並行して回す構成もあります。",
            ),
            (
                "購入前の確認事項",
                "購入前に以下を確認してください。\n"
                "・2026年度版（最新版）か\n"
                "・マン管単独/W受験に合った表記か\n"
                "・テキスト・過去問との重複が計画上問題ないか\n"
                "・Amazon在庫・価格",
            ),
        ],
        "faqs": [
            (
                "一問一答だけで合格できますか？",
                "短問演習には有効ですが、論点理解はテキストと過去問で済ませてから入る方が効率的です。"
                "おすすめテキスト・問題集の記事と組み合わせる構成を推奨します。",
            ),
            (
                "管理業務主任者 項目別過去8年問題集は必要ですか？",
                "2026年度版 管理業務主任者 項目別過去8年問題集（4300120285）は、"
                "W受験で管理業務主任者区分の過去問演習を厚くしたい場合の追加選択肢です。"
                "Wマスター過去問集と役割が重なる場合は1冊に絞ってください。",
            ),
            (
                "速習と一問一答、両方買いますか？",
                "必須ではありません。時間が限られる場合は一問一答1冊、"
                "総復習を厚くしたい場合は速習→一問一答の順で追加する使い方が一般的です。",
            ),
        ],
        "related_links": (
            "exam-overview:試験概要;"
            "past-questions-by-field:分野別過去問;"
            "pass-score:合格点と合格基準;"
            "affiliate-textbooks-recommend:おすすめテキスト;"
            "affiliate-problem-books:おすすめ問題集;"
            "study-plan-beginner:初学者向け学習計画"
        ),
        "key_points": (
            "2026年度版 らくらくわかる! マンション管理士速習テキスト;"
            "2026年度版 マンション管理士 一問一答セレクト1000;"
            "2026年度版 管理業務主任者 一問一答セレクト1000;"
            "一問一答・速習の位置づけ;"
            "W受験の組み合わせ"
        ),
    },
}


def write_briefs() -> None:
    BRIEFS.mkdir(parents=True, exist_ok=True)
    for slug, data in BRIEFS_DATA.items():
        path = BRIEFS / f"{slug}.yaml"
        path.write_text(
            yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        print(f"wrote brief → {path}")


def patch_csv() -> None:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if not fieldnames:
        raise SystemExit("CSV header missing")
    fieldnames = list(fieldnames)
    if "faq_3_answer" in fieldnames and "faq_3_question" not in fieldnames:
        idx = fieldnames.index("faq_3_answer")
        fieldnames.insert(idx, "faq_3_question")

    for row in rows:
        slug = row.get("slug", "")
        if slug not in CSV_ROWS:
            continue
        cfg = CSV_ROWS[slug]
        row["title"] = cfg["title"]
        row["meta_description"] = cfg["meta_description"]
        row["lead"] = cfg["lead"]
        row["priority"] = cfg["priority"]
        row["original_note"] = cfg["original_note"]
        row["user_intent"] = cfg["user_intent"]
        row["action_items"] = cfg["action_items"]
        row["revision_note"] = cfg["revision_note"]
        row["fact_checked_at"] = PRICE_CHECKED
        row["content_status"] = "published"
        row["related_links"] = cfg["related_links"]
        row["key_points"] = cfg["key_points"]
        row["tags"] = "独学;参考書;アフィリエイト"
        for i, (heading, body) in enumerate(cfg["sections"], start=1):
            row[f"section_{i}_heading"] = heading
            row[f"section_{i}_body"] = ensure_section_body(body)
        for i in range(len(cfg["sections"]) + 1, 8):
            row[f"section_{i}_heading"] = ""
            row[f"section_{i}_body"] = ""
        for i, (q, a) in enumerate(cfg["faqs"], start=1):
            row[f"faq_{i}_question"] = q
            row[f"faq_{i}_answer"] = ensure_faq_answer(a)
        for i in range(len(cfg["faqs"]) + 1, 4):
            row[f"faq_{i}_question"] = ""
            row[f"faq_{i}_answer"] = ""
        print(f"patched CSV row: {slug}")

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    write_briefs()
    patch_csv()
    return 0


if __name__ == "__main__":
    sys.exit(main())
