#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""マン管サイトの一覧用要約（short_def / summary）を記事内容ベースで更新する。"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GLOSSARY_SHORT_DEF: dict[str, str] = {
    "専有部分": "各住戸の床・壁・天井で囲まれた室内が中心。玄関ドア本体や窓サッシは共用に属し、境界部位の帰属が試験頻出。",
    "共用部分": "専有部分以外で全員が共有する建物部分・付属物。法定・規約・一部共用の3分類と、保存・管理・変更の区分が論点。",
    "法定共用部分": "規約がなくても全員共用となる部分。廊下・階段・エレベーター・外壁が典型で、登記は不要。",
    "規約共用部分": "専有部分にできる場所を規約で共用に位置づけた部分。集会室・管理人室が典型で、登記が第三者対抗要件。",
    "一部共用部分": "特定の区分所有者グループだけが使う共用部分。複合用途型の店舗専用入口や住宅専用廊下が典型例。",
    "区分所有者": "専有部分の区分所有権を有する者。売買・相続で自動取得・喪失し、管理組合の構成員になる（賃借人は含まない）。",
    "区分所有権": "専有部分を目的とする所有権で、共用持分と敷地利用権を一体とする。分離処分は原則禁止。",
    "区分建物": "登記法上の住戸単位表示。区分所有権と同じ住戸を指すが、表題部の2層構造や一体移転が登記論点。",
    "敷地": "建物直下の法定敷地に加え、規約で駐車場などを取り込んだ規約敷地を含む、マンションが建つ土地の範囲。",
    "敷地利用権": "専有部分を保有するための土地側権利（所有権・地上権・賃借権等）。住戸と切り離して譲渡できない。",
    "分離処分の禁止": "専有部分と敷地利用権を切り離して売却・設定できない原則。規約の別段定めで例外的に認められる。",
    "規約": "区分所有関係の基本ルール文書。設定・変更・廃止には各4分の3の特別多数決議が必要。",
    "集会": "区分所有者が規約・予算・役員等を決議する会議（総会）。年1回以上の開催が義務付けられる。",
    "議決権": "集会で賛否を示す投票力。原則は床面積比配分で、規約により1住戸1票等に変更可能。",
    "普通決議": "区分所有者数と議決権数の各過半数で成立。通常管理・軽微変更・役員選任など日常議題が対象。",
    "特別多数決議": "規約変更・重大変更は各4分の3、建替え決議は各5分の4が必要な加重要件の決議。",
    "集会の招集": "管理者の年1回義務と、5分の1以上による臨時招集請求。通知期限は議題（建替えは2か月前）で変わる。",
    "招集通知": "会日の1週間前まで発出（建替えは2か月前）。規約変更等は議案の要領添付が必要。",
    "議事録": "集会の決定内容を記録する公式書面。議長と区分所有者2人の計3人署名、管理者等が保管。",
    "管理組合": "区分所有関係成立で全区分所有者が当然構成される管理団体。加入・脱退の自由はない。",
}

COMPARE_SUMMARY: dict[str, str] = {
    "senyu-kyoyou": "住戸内側と全員共有部分の帰属・修繕主体・費用負担を表で対照。玄関ドア・窓サッシ・バルコニーなど境界部位の仕分けが焦点。",
    "hotei-kiyaku-kyoyou": "規約なくても共用となる法定部分と、規約＋登記が必要な規約共用部分の差。集会室とエレベーターの典型例の取り違えに注意。",
    "futsu-tokubetsu-ketsugi": "通常管理は各過半数、規約変更・重大変更は4分の3、建替えだけ5分の4。対象議題ごとの数字対応が過去問の定番。",
    "shikichi-riyouken": "敷地は土地の物理的範囲（法定＋規約）、敷地利用権は区分所有者が持つ土地を使う権利。分離処分の禁止とセットで理解する。",
    "kubun-shoyuken-tatemono": "区分所有権は権利関係、区分建物は登記上の住戸単位。同じ住戸でも表題部構造や一体移転の論点が異なる。",
    "shukai-kanri-kumiai": "管理組合は常設の管理団体、集会はその意思決定の場。組合員資格は自動取得で、決議は集会でのみ行う。",
    "shuchou-gijiroku": "招集通知は決める前の告知（1週間前／建替え2か月前）、議事録は決めた後の記録（署名3人）。時期と記載要件が対比の軸。",
    "kubun-shoyusha-ken": "区分所有者は「人」、区分所有権はその人が持つ「権利」。賃借人等の占有者とは議決権・組合員資格が異なる。",
    "ichibu-hotei-kyoyou": "法定共用は全員が当然に利用、一部共用は特定所有者グループ専用。複合用途型の店舗入口・住宅廊下が典型例。",
    "kiyaku-giketsuken": "規約は管理ルール本体で変更に4分の3必要。議決権は集会での投票力で、配分は原則床面積比だが規約で調整可。",
}

NUMBERS_SUMMARY: dict[str, str] = {
    "mankan-goukaku-mondai": "本試験は50問120分・1問1点。令和7年度例では37点以上が合格ラインだが、相対評価のため年度で変動する。",
    "kangyou-menjo-5mon": "管業との同日受験で重複5問が免除され、マン管は45問で受験。合格判定も45問ベースになる。",
    "mankan-juken-tesuryo": "2025年度要項例で受験手数料9,400円。管業同日は各試験の手数料が別途必要。",
    "mankan-jikan-120": "試験時間120分固定。50問なら約2.4分/問、管業同日45問なら約2.7分/問のペース感。",
    "futsu-ketsugi-yohken": "普通決議は区分所有者数と議決権数の二重過半数。規約で議決権のみ過半数に緩和可能。",
    "tokubetsu-tatekae-wariai": "規約変更・重大変更は各4分の3、建替え決議だけ各5分の4。人数と議決権の双方が要件。",
    "shuchou-tatekae-kigen": "一般招集通知は会日1週間前、建替え決議は2か月前＋議案要領添付。規約で1週間前は変更可。",
    "shukai-nen1kai": "管理者は年1回以上集会を招集する義務あり。通常総会で予算・決算・役員等を決議。",
    "gijiroku-shomei-3": "議事録は議長と集会で選任した区分所有者2人、計3人の署名。管理者等が保管する。",
    "shukai-shuchou-5bun1": "区分所有者と議決権の各5分の1以上が請求すれば臨時集会の招集を求められる（過半数ではない）。",
}

MISTAKES_SUMMARY: dict[str, str] = {
    "senyu-kyoyou-kon": "「見える部分＝専有」が典型誤り。窓サッシ・玄関ドアは共用、バルコニーは専用使用の共用部分。",
    "hotei-kiyaku-kon": "集会室を法定共用と誤認する肢、規約共用の登記不要説。エレベーターは法定共用が正解。",
    "futsu-tokubetsu-kon": "規約変更を過半数とする誤り、建替えを4分の3とする誤り。軽微変更は普通決議で足りる。",
    "giketsuken-1to1-go": "1住戸1票を原則とする誤り。床面積比が原則で、二重要件（人数も4分の3）を見落とす肢。",
    "shuchou-jikougai-ketsugi": "通知にない事項を全員賛成で決議できる誤り。規約変更は要領添付、建替えは2か月前通知。",
    "gijiroku-shomei-go": "議長のみ署名で足りる、管理者が署名者、出席全員署名必要、など署名3人ルールの誤肢。",
    "bunri-shobun-go": "住戸だけ売れる・規約で分離不可、の両方向の誤り。原則禁止で規約例外あり。",
    "chintai-kubun-go": "賃借人＝区分所有者の混同。議決権・管理組合員は区分所有者（所有権者）に限る。",
    "kanri-kanyu-ninni-go": "管理組合への加入任意・脱退自由・非加入なら管理費不要、など当然構成の誤解。",
    "shikichi-riyouken-kon": "敷地＝所有権、真下だけが敷地、敷地利用権単独譲渡可、など概念混同の引っかけ。",
}


def _update_csv(path: Path, key_col: str, updates: dict[str, str], target_col: str) -> int:
    text = path.read_text(encoding="utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        return 0
    n = 0
    for row in rows:
        key = (row.get(key_col) or "").strip()
        if key in updates:
            row[target_col] = updates[key]
            n += 1
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=rows[0].keys(), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(out.getvalue(), encoding="utf-8")
    return n


def main() -> int:
    n_g = _update_csv(
        ROOT / "data" / "glossary_terms.csv",
        "term",
        GLOSSARY_SHORT_DEF,
        "short_def",
    )
    n_c = _update_csv(
        ROOT / "data" / "comparisons.csv",
        "slug",
        COMPARE_SUMMARY,
        "summary",
    )
    n_n = _update_csv(
        ROOT / "data" / "numbers.csv",
        "slug",
        NUMBERS_SUMMARY,
        "summary",
    )
    n_m = _update_csv(
        ROOT / "data" / "mistakes.csv",
        "slug",
        MISTAKES_SUMMARY,
        "summary",
    )
    print(
        f"Updated index summaries: glossary={n_g}, compare={n_c}, "
        f"numbers={n_n}, mistakes={n_m}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
