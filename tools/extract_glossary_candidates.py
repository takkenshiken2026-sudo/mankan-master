#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""既存問題（past_questions.csv + practice_questions.csv）から
用語候補を抽出して頻度ランキングを出力する。

抽出ロジック:
- 漢字 2〜15 文字の連続を候補とする
- カタカナ 3 文字以上の連続も候補
- 漢字+カタカナ 混在も候補
- 一般的なつなぎ語・助動詞由来の語を除外
"""
from __future__ import annotations
import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KANJI = r"[一-龥々]"
KATA = r"[ァ-ヴー]"
TOKEN_RE = re.compile(
    rf"(?:{KANJI}{{2,15}}|{KATA}{{3,15}}|{KANJI}+{KATA}+{KANJI}*|{KATA}+{KANJI}+)"
)

STOPWORDS = {
    "場合", "次", "以下", "以上", "未満", "超", "等", "及び", "並びに", "若しくは",
    "又は", "且つ", "但し", "ただし", "なお", "すなわち", "もって", "もつて",
    "当該", "この", "その", "あの", "前項", "前条", "次項", "次条", "前号", "次号",
    "本条", "本項", "本号", "上記", "下記", "別表", "別紙", "別添",
    "について", "における", "において", "により", "によって", "ため",
    "とき", "こと", "もの", "ところ", "やむ", "得ない", "得る", "できる",
    "係る", "対する", "する", "した", "して", "され", "された", "される",
    "あり", "ある", "ない", "なし",
    "事項", "規定", "適用", "解釈", "判断", "考え", "選択", "理由",
    "問題", "解答", "解説", "正解", "誤り", "正しい",
    "数値", "年", "月", "日", "件", "回", "倍", "割", "分", "秒", "時",
    "個", "名", "者", "対象", "範囲", "内容", "目的", "効果",
    "選択肢", "答え", "問", "ア", "イ", "ウ", "エ",
    "次の", "上の", "下の", "右の", "左の",
    "従って", "したがって", "また", "さらに", "なお",
    "本問", "本件", "全て", "全部", "一部", "原則", "例外", "特例",
    "適切", "不適切", "妥当", "誤", "正", "最も", "もっとも",
    "なければならない", "ならない", "なれない",
}


def extract_terms(text: str) -> list[str]:
    if not text:
        return []
    out: list[str] = []
    for m in TOKEN_RE.findall(text):
        if not m or len(m) < 2:
            continue
        if m in STOPWORDS:
            continue
        out.append(m)
    return out


def main() -> int:
    files = [
        ROOT / "data" / "past_questions.csv",
        ROOT / "data" / "practice_questions.csv",
    ]
    counter: Counter[str] = Counter()
    rows_processed = 0
    for path in files:
        if not path.exists():
            print(f"skip {path}", file=sys.stderr)
            continue
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows_processed += 1
                blob = " ".join(
                    str(row.get(k) or "")
                    for k in (
                        "question",
                        "choice1",
                        "choice2",
                        "choice3",
                        "choice4",
                        "explanation",
                        "category",
                    )
                )
                for term in extract_terms(blob):
                    counter[term] += 1

    out_path = ROOT / "tools" / "glossary_candidates.tsv"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("freq\tterm\n")
        for term, freq in counter.most_common():
            if freq < 2:
                continue
            f.write(f"{freq}\t{term}\n")
    print(f"processed_rows: {rows_processed}")
    print(f"unique_terms (freq>=2): {sum(1 for _, n in counter.items() if n >= 2)}")
    print(f"top 60:")
    for term, freq in counter.most_common(60):
        print(f"  {freq:4d}  {term}")
    print(f"\nwrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
