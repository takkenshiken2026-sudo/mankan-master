#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""試験ガイド手書きリライト：具体性＋文中例示の追加ルール（v1.1）。"""

from __future__ import annotations

import re

from tools.editorial_quality import norm

# 文中の例示・場面描写（いずれか1つ以上を節本文に入れる）
EXAMPLE_MARKERS_RE = re.compile(
    r"例えば|たとえば|たとえ|例として|イメージ(?:として|すると)|好比|想像すると|"
    r"具体(?:例|的)には|一例として|場面として|ケース(?:として|例)|"
    r"たとえば[、,]?[0-9０-９月火水木金土日曜]|"
    r"「[^」]{6,48}」(?:の|と|なら|では)"
)

# 節本文の最低例示数（5節中）
MIN_SECTIONS_WITH_EXAMPLE = 3

# 1節あたりの具体アンカー（数字・日付・固有名詞など）—表の行は除く簡易判定
CONCRETE_ANCHOR_RE = re.compile(
    r"\d+[％%]|"
    r"\d+[問時間分]|"
    r"\d+:\d+|"
    r"[0-9０-９]+月[0-9０-９]+日|"
    r"令和[0-9０-９]+年度|"
    r"第[0-9０-９]+章|"
    r"P\.[0-9０-９]+|"
    r"区分所有法|管理組合|修繕積立|総会|マン管"
)

PIPE_TABLE_ROW_RE = re.compile(r"^\|", re.M)


def _body_without_table(body: str) -> str:
    lines = [ln for ln in body.split("\n") if ln.strip() and not PIPE_TABLE_ROW_RE.match(ln.strip())]
    return "\n".join(lines)


def section_has_example(body: str) -> bool:
    prose = _body_without_table(norm(body))
    return bool(prose and EXAMPLE_MARKERS_RE.search(prose))


def section_concrete_anchor_count(body: str) -> int:
    prose = _body_without_table(norm(body))
    if not prose:
        return 0
    return len(CONCRETE_ANCHOR_RE.findall(prose))


def validate_concrete_rewrite(slug: str, patch: dict[str, str]) -> list[str]:
    """REWRITES 1件分の具体性＋例示チェック。ERROR 文言の list を返す。"""
    errors: list[str] = []
    prefix = f"{slug}:"

    lead = norm(patch.get("lead"))
    if lead and not EXAMPLE_MARKERS_RE.search(lead) and not re.search(r"\d+週|\d+か月", lead):
        errors.append(
            f"{prefix} lead needs a micro-scenario (例えば/たとえば or 残り○週 など)"
        )

    example_sections = 0
    for n in range(1, 6):
        bcol = f"section_{n}_body"
        body = norm(patch.get(bcol))
        if not body:
            continue
        if section_has_example(body):
            example_sections += 1
        elif section_concrete_anchor_count(body) < 2:
            errors.append(
                f"{prefix} {bcol} needs 例えば/たとえば scene OR 2+ concrete anchors outside the table"
            )

    if example_sections < MIN_SECTIONS_WITH_EXAMPLE:
        errors.append(
            f"{prefix} need {MIN_SECTIONS_WITH_EXAMPLE}+ sections with 例えば/たとえば "
            f"(got {example_sections})"
        )

    return errors
