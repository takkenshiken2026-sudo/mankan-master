# -*- coding: utf-8 -*-
"""cmp/num/mis helpers for mankan S31+ batches."""
import json
from tools.write_mankan_hub_s30 import HEADER_COMPARE, HEADER_MISTAKES, HEADER_NUMBERS, DATA
from tools.write_mankan_hub_s30_data import COMPARISONS, MISTAKES, NUMBERS

def _faq(qa: list[tuple[str, str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for i, (q, a) in enumerate(qa, start=1):
        out[f"faq_{i}_question"] = q
        out[f"faq_{i}_answer"] = a
    return out

def _rows(*items: dict) -> str:
    return json.dumps(list(items), ensure_ascii=False)

def cmp(slug, title, cat, tags, summary, labels, axes, article_title, lead, points, mistakes, tip, related, qa):
    return {
        "slug": slug, "title": title, "category": cat, "tags": tags, "summary": summary,
        "col_labels": labels,
        "compare_rows": _rows(*[{"axis": a, "cols": c} for a, c in axes]),
        "article_title": article_title, "article_lead": lead, "exam_points": points,
        "common_mistakes": mistakes, "memory_tip": tip, "related_terms": related, **_faq(qa),
    }

def num(slug, title, cat, tags, summary, highlight, items, article_title, lead, points, mistakes, tip, related, qa):
    return {
        "slug": slug, "title": title, "category": cat, "tags": tags, "summary": summary,
        "highlight": highlight,
        "item_rows": _rows(*[{"item": i, "value": v, "note": n} for i, v, n in items]),
        "article_title": article_title, "article_lead": lead, "exam_points": points,
        "common_mistakes": mistakes, "memory_tip": tip, "related_terms": related, **_faq(qa),
    }

def mis(slug, title, cat, tags, summary, confusion, patterns, article_title, lead, points, mistakes, tip, related, qa):
    return {
        "slug": slug, "title": title, "category": cat, "tags": tags, "summary": summary,
        "confusion_point": confusion,
        "pattern_rows": _rows(*[{"topic": t, "wrong": w, "correct": c, "trap": p} for t, w, c, p in patterns]),
        "article_title": article_title, "article_lead": lead, "exam_points": points,
        "common_mistakes": mistakes, "memory_tip": tip, "related_terms": related, **_faq(qa),
    }
