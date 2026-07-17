#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全公開 HTML の <head> に AdSense スクリプトを注入する。

site-config.json の adsenseClientId が設定されているときだけ挿入する。
build_all.py から呼ばれる。単独実行も可。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.html_footer import adsense_head_snippet, inject_adsense_head
from tools.site_config import adsense_client_id

SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    "public_site",
    "__pycache__",
    ".cursor",
}


def iter_html_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*.html"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.name.startswith("."):
            continue
        out.append(path)
    return sorted(out)


def main() -> int:
    client = adsense_client_id()
    snippet = adsense_head_snippet()
    if client and not snippet:
        print(f"ERROR: adsenseClientId の形式が不正です: {client!r}", file=sys.stderr)
        return 1

    changed = 0
    total = 0
    for path in iter_html_files(ROOT):
        total += 1
        old = path.read_text(encoding="utf-8")
        new = inject_adsense_head(old)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed += 1

    if snippet:
        print(f"AdSense head: injected/updated in {changed}/{total} HTML files ({client})")
    else:
        print(f"AdSense head: removed/cleared in {changed}/{total} HTML files (adsenseClientId unset)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
