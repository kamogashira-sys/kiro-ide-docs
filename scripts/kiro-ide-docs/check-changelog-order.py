#!/usr/bin/env python3
"""1.0系changelogの一覧表・本文の版順を検証する。

本文に明示アンカーを持つ1.0系では、一覧表と本文のリリース単位が
同じ版集合かつ新しい版から古い版への同じ順序でなければならない。
0.x系は表形式パッチを含み、全版が本文アンカーを持たないため対象外。
"""

from __future__ import annotations

from pathlib import Path
import argparse
import re
import sys

DEFAULT_CHANGELOG = Path("kiro-ide-docs/02_update/01_changelog.md")
TOC_RE = re.compile(
    r"^\| \[([0-9]+(?:\.[0-9]+){1,2})\]\(#([a-z0-9-]+)\) \|",
    re.MULTILINE,
)
ANCHOR_RE = re.compile(r'<a id="(v1-0-[0-9]+)"></a>')
HEADING_RE = re.compile(r"^## .*?([0-9]+\.[0-9]+\.[0-9]+)")


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def main(changelog: Path) -> int:
    print("=== kiro-ide-docs 1.0系 changelog 本文順チェック ===")

    if not changelog.is_file():
        print(f"❌ changelog が存在しません: {changelog}")
        return 1

    text = changelog.read_text(encoding="utf-8")
    toc = TOC_RE.findall(text)
    errors: list[str] = []

    if not toc:
        errors.append("一覧表からバージョンを1件も抽出できませんでした")
        toc_versions: list[str] = []
        toc_anchors: list[str] = []
    else:
        toc_versions = [version for version, _ in toc]
        toc_anchors = [anchor for _, anchor in toc]

        if len(toc_anchors) != len(set(toc_anchors)):
            errors.append("一覧表に重複したアンカーがあります")
        if toc_versions != sorted(toc_versions, key=version_key, reverse=True):
            errors.append("一覧表のバージョンが数値降順ではありません")

        for version, anchor in toc:
            expected = f"v{version.replace('.', '-')}"
            if anchor != expected:
                errors.append(
                    f"一覧表の {version} はアンカー #{expected} を指す必要があります（実際: #{anchor}）"
                )

    body_anchors = ANCHOR_RE.findall(text)
    if body_anchors != toc_anchors:
        errors.append("本文アンカーの版集合または出現順が一覧表と一致しません")

        if len(body_anchors) != len(toc_anchors):
            errors.append(
                f"版数が一致しません（一覧表: {len(toc_anchors)}、本文アンカー: {len(body_anchors)}）"
            )
        for index, (toc_anchor, body_anchor) in enumerate(
            zip(toc_anchors, body_anchors), start=1
        ):
            if toc_anchor != body_anchor:
                errors.append(
                    f"位置 {index} の不一致（一覧表: #{toc_anchor}、本文: #{body_anchor}）"
                )
                break

    lines = text.splitlines()
    for index, line in enumerate(lines):
        anchor_match = ANCHOR_RE.fullmatch(line)
        if not anchor_match:
            continue

        anchor = anchor_match.group(1)
        version = anchor[1:].replace("-", ".")
        heading_line = next(
            (candidate for candidate in lines[index + 1 :] if candidate.strip()),
            None,
        )
        if heading_line is None:
            errors.append(f"#{anchor} の後に見出しがありません")
            continue

        heading_match = HEADING_RE.match(heading_line)
        if heading_match is None or heading_match.group(1) != version:
            errors.append(
                f"#{anchor} の直後は {version} のH2見出しである必要があります"
            )

    print(f"一覧表のバージョン数: {len(toc_versions)}")
    print(f"本文アンカーのバージョン数: {len(body_anchors)}")

    if errors:
        print(f"❌ エラー: {len(errors)} 件")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✅ 一覧表と本文は同じ版集合で、完全な数値降順です")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="1.0系changelogの一覧表と本文の版順を検証する"
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=DEFAULT_CHANGELOG,
        help=f"対象changelog（既定: {DEFAULT_CHANGELOG}）",
    )
    sys.exit(main(parser.parse_args().path))
