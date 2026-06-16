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
    "affiliate-beginner-material-set",
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
            "https://www.amazon.co.jp/dp/4300120323/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/430012034X/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/4300120293/ref=nosim?tag=ue083093-22",
        ]
    ),
    "affiliate-beginner-material-set": ";".join(
        [
            "exam-overview:試験概要",
            "study-plan:学習計画の立て方",
            "textbook-selection:テキストの選び方",
            "affiliate-textbooks-recommend:おすすめテキスト3選",
            "affiliate-problem-books:おすすめ問題集3選",
            "https://www.amazon.co.jp/dp/4300120218/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/4300120072/ref=nosim?tag=ue083093-22",
            "https://www.amazon.co.jp/dp/4300120080/ref=nosim?tag=ue083093-22",
        ]
    ),
}

BODY_PATCHES: dict[str, dict[str, str]] = {
    "affiliate-textbooks-recommend": {
        "section_2_body": (
            "上の比較表は、価格だけでなく「誰向きか」とページ配分の違いを見るためのものです。購入判断は次の順がおすすめです。"
            "1. for_who（向いている人）を自分の状況と照合する"
            "2. ページ数と7分野の章ボリューム感を目次で確認する"
            "3. 週10時間で10月末までに第1周できるかをざっくり見積もる"
            "たとえば管理組合法だけ演習正答率が低い人は、はじめの一歩で全体像をつかんでからWマスターへ移行し、"
            "論点を一覧で整理したい人は出る順を候補にします。表をノートに転記したら、テキスト1章読了→演習10問で理解を確認し、"
            "誤答は用語解説と該当章で読み直してください。"
            "[テキストの選び方](../textbook-selection/)と併読すると、公式テキストとの使い分けも整理できます。"
        ),
        "section_3_body": (
            "「2026年度版 みんなが欲しかった! マンション管理士・管理業務主任者 合格へのはじめの一歩」"
            "（TAC出版・300ページ・Amazon税込参考1,980円）は、イラストと板書で7分野の輪郭をつかみたい初学者向けです。"
            "オリエンテーション編と入門講義編の2部構成のため、「試験の全体像→各分野の入口」まで短時間で進みやすいのが強みです。"
            "向いている人：マン管·管業のW受験をこれから始め、法律の勉強が初めての人。"
            "週10時間で6〜8月に第1周し、9月から通し50問に移行する計画と相性がよいです。"
            "注意点：解説は入門向けコンパクトなので、条文の細部まで厚く読みたい場合はWマスターへの移行を早めに検討してください。"
            "演習量は[おすすめ問題集3選](../affiliate-problem-books/)の過去問系と併用すると48％ラインの判断が安定します。"
        ),
        "section_7_body": (
            "購入前に次を確認してください。1. Amazon販売ページで税込価格·在庫·2026年度版（2026年版）表記"
            "2. 要項の受験区分（マン管単独かW受験か）と目次の章立て"
            "3. 6/14開始なら残り25週・週10時間で第1周が終わるか"
            "たとえば6/14（日）に1冊決定→7月末まで第1周→8月から[おすすめ問題集3選](../affiliate-problem-books/)で演習中心、という順が定番です。"
            "[初学者向け学習計画](../study-plan-beginner/)で月次計画を組み、速習·一問一答が必要になった段階で"
            "[おすすめ一問一答・速習](../affiliate-mock-exam-materials/)を検討してください。"
            "価格は変動するため、申込・購入の直前に必ず販売ページで再確認してください。"
        ),
    },
    "affiliate-problem-books": {
        "section_2_body": (
            "比較表は価格だけでなく「どの演習サイクルに乗せるか」で読むのがポイントです。"
            "| 組み合わせ | テキスト | 問題集 || --- | --- | --- || TAC系 | はじめの一歩·速習 | 項目別過去8年 || LEC系 | 出る順テキスト | 分野別過去問題集 || 早稲田系 | Wマスターテキスト | Wマスター過去問集 |"
            "[おすすめテキスト3選](../affiliate-textbooks-recommend/)で決めた1冊と縦串を揃えると、章読了→同分野20問の接続がスムーズです。"
            "マン管マスターの分野別演習は無料で現在地把握に使えるため、問題集は「通し50問の追加」か「過去8年の解説読み込み」かの役割で1冊選ぶとコスト対効果が高いです。"
            "11月以降は新規購入を抑え、解き直しに時間を回してください。"
        ),
        "section_6_body": (
            "独学の最小構成は「テキスト1冊＋問題集1冊」です。6〜8月はテキスト第1周、9〜10月は問題集中心、11月は通し演習と解き直し、という2段階が定番です。"
            "たとえば6/14（日）に[おすすめテキスト3選](../affiliate-textbooks-recommend/)でテキスト決定→8/31（日）第1周完了→9/7（日）からTAC過去8年の管理組合パート開始、の順です。"
            "テキストと問題集の出版社を揃えると、章と過去問項目の対応づけが楽になります。"
            "速習·一問一答が必要になった段階で[おすすめ一問一答・速習](../affiliate-mock-exam-materials/)を検討し、"
            "11月以降は新規教材追加を抑えて解き直しに集中してください。"
        ),
        "section_7_body": (
            "購入前に次を確認してください。1. Amazon販売ページで税込価格·在庫·2026年度版表記"
            "2. メインテキストと同系列か（TAC·LEC·早稲田）"
            "3. 9月開始なら11/29までに通し50問を最低4回入れられるか"
            "[初学者向け学習計画](../study-plan-beginner/)で週10時間×25週を先にカレンダー固定し、問題集は「9月1冊購入・11月追加なし」を原則にすると教材コストを抑えられます。"
            "価格は変動するため、購入の直前に必ず販売ページで再確認してください。"
        ),
    },
    "affiliate-mock-exam-materials": {
        "section_2_body": (
            "3冊はすべてTAC系ですが、役割が異なります。"
            "| 商品 | 主な用途 | 向く時期 || --- | --- | --- || 速習テキスト | 論点の短期整理 | 6〜7月·テキスト並行 || マン管セレクト1000 | マン管短問演習 | 8〜10月 || 管業セレクト1000 | W受験の管業短問 | 9月以降（Wのみ） |"
            "通勤30分×平日5日＝週150分なら、マン管セレクトで短問10問/日×5日が現実的な上限です。"
            "[おすすめテキスト3選](../affiliate-textbooks-recommend/)·[おすすめ問題集3選](../affiliate-problem-books/)で主教材を決めてから、"
            "足りない演習形式だけを1冊追加する判断がコスト対効果が高いです。"
        ),
        "section_3_body": (
            "「2026年度版 らくらくわかる! マンション管理士速習テキスト」（TAC出版·900ページ·Amazon税込参考3,190円）は、"
            "テキスト読了前後に7分野の論点を速習形式で整理したい人向けです。解説がコンパクトで、社会人の平日90分学習と相性がよいのが強みです。"
            "向いている人：はじめの一歩読了後、本格テキストへ進む前の橋渡しが欲しい人。"
            "たとえば7/5（土）〜8/2（土）の4週で「週末90分×速習2章→平日演習10問」を固定する運用が定番です。"
            "注意点：50問通しの時間練習は担えないため、9月以降は[おすすめ問題集3選](../affiliate-problem-books/)の通し演習を別途入れてください。"
            "速習だけで合格を狙うのではなく、第1周の理解確認用と割り切ることが重要です。"
        ),
        "section_6_body": (
            "W受験の教材順番の定番は次の4段階です。"
            "| 段 | 教材 || --- | --- || 1 | はじめの一歩またはWマスターテキスト || 2 | おすすめ問題集3選の過去問1冊 || 3 | マン管セレクト1000（+必要なら管業セレクト） || 4 | 11月の通し50問×2回 |"
            "たとえば6/14（日）テキスト決定→8/31（日）第1周→9/7（日）過去問開始→10/6（月）からマン管セレクト10問/日、"
            "W受験なら10/20（月）から管業セレクト追加、の流れです。速習テキストは段1と並行で7月だけ使い、8月以降は問題集·セレクトに役割を移すと迷いが減ります。"
        ),
        "section_7_body": (
            "一問一答·速習は「メインテキスト80％読了後」に1冊だけ追加する80％ルールが安全です。"
            "6/14開始·残り25週なら、7〜8月はテキスト·速習、9月以降セレクト、10〜11月通し50問、の大枠を"
            "[初学者向け学習計画](../study-plan-beginner/)で先に固定してください。"
            "テキスト·問題集が未決なら、[おすすめテキスト3選](../affiliate-textbooks-recommend/)と"
            "[おすすめ問題集3選](../affiliate-problem-books/)で先に1冊ずつ決めてから一問一答を選ぶと無駄がありません。"
            "購入前チェック：Amazonで税込価格·2026年度版表記·受験区分。"
            "11月以降の新規教材追加は抑え、解き直しに週10時間の50％以上を回す判断が定番です。"
            "価格は変動するため、購入直前に必ず販売ページで再確認してください。"
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
