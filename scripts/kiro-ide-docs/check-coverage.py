#!/usr/bin/env python3
"""check-coverage.py - changelog の網羅性を一次情報と突き合わせて検証する

使用方法:
    # 一次情報の HTML を取得済みのディレクトリを指定する
    ./scripts/kiro-ide-docs/check-coverage.py --html-dir /tmp/kiro_pr

    # 抽出済み JSON（extract-changelog.py の出力）を使う
    ./scripts/kiro-ide-docs/check-coverage.py --json /tmp/kiro_pr/extract.json

検証内容:
    1. **版の網羅性**: 一次情報に存在する全バージョンが、changelog の目次表に載っていること
       （およびその逆。目次に架空の版がないこと）
    2. **日付の一致**: 各版のリリース日が一次情報と一致すること（ISO 正規化後）
    3. **説明の転記**: 一次情報に説明を持つ版が、文書側にも本文記述を持つこと

なぜ必要か:
    D9（記述粒度）の前提は「**全45パッチに公式の説明が実在する**」である。説明の欠落は
    公式の情報不足ではなく本サイトの転記漏れを意味するため、機械で突き合わせる。
    `check-changelog.sh` は文書内部の整合しか見ないので、一次情報との照合は本スクリプトが担う。

判定の注意（誤検知を避けるための実測知見）:
    - 文書側の「記述あり」は箇条書きだけでは測れない。**表形式**（0.1 の5つの柱・パッチ一覧表）も
      正当な転記形式である。行頭 `- ` のみを数えると 0.1 が「未転記」に見える。
    - 一次情報側の項目数はそのまま比較できない。動画トランスクリプト（`<details>` 内）と
      画像の alt テキストが `li`/`p` として混入するため、**項目数の一致は要求せず**、
      「説明を持つ版に本文記述があるか」を見る。
    - セクション配下の箇条書きは `groups`（`<p><strong>ラベル</strong></p>` で束ねられた組）に
      入ることがある。`items` だけを数えると 0.8.135 が「0項目」に見える（実際は33項目）。

ネットワークは使わない。HTML の取得手順は `05_meta/10_version-update-guide.md` を参照。
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import sys

DOC_FILES = [
    "kiro-ide-docs/02_update/01_changelog.md",
    "kiro-ide-docs/02_update/02_changelog-0x.md",
]

# 目次の表の行: `| [1.0.242](#v1-0-242) | 2026-07-28 | ▫️パッチ | 概要 |`
# パッチ一覧表の行: `| **0.6.29** | 2025-11-27 | 概要 |`
TOC_RE = re.compile(
    r'^\|\s*(?:\[|\*\*)(\d+\.\d+(?:\.\d+)?)(?:\]\(#[a-z0-9-]+\)|\*\*)\s*\|'
    r'\s*(\d{4}-\d{2}-\d{2})\s*\|'
)


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_extractor():
    """extract-changelog.py をモジュールとして読み込む（ハイフン入りのため import 不可）。"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract-changelog.py")
    spec = importlib.util.spec_from_file_location("extract_changelog", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def n_items(section):
    """節の項目数。`groups` に束ねられた箇条書きも数える（0.8.135 の33項目はここに入る）。"""
    return len(section.get("items") or []) + sum(
        len(g.get("items") or []) for g in (section.get("groups") or [])
    )


def primary(pages):
    """一次情報を {版: {"date": ISO, "described": bool}} に畳む。"""
    out = {}
    for p in pages:
        v = p.get("version")
        if v and p.get("date_iso"):
            described = bool(p.get("intro")) or any(n_items(s) for s in p.get("sections") or [])
            out[v] = {"date": p["date_iso"], "described": described}
        for pt in p.get("patches") or []:
            if not pt.get("date_iso"):
                continue
            described = bool(pt.get("lines")) or any(
                n_items(s) for s in pt.get("sections") or []
            )
            # 専用ページと系列ページの両方に現れる版は、説明ありを優先して残す
            cur = out.get(pt["version"])
            if cur is None or (described and not cur["described"]):
                out[pt["version"]] = {"date": pt["date_iso"], "described": described}
    return out


def doc_versions():
    """文書側の {版: 日付} を目次表・パッチ一覧表から取る。"""
    out = {}
    for f in DOC_FILES:
        try:
            lines = open(f, encoding="utf-8").read().splitlines()
        except OSError:
            continue
        for ln in lines:
            m = TOC_RE.match(ln)
            if m:
                out.setdefault(m.group(1), set()).add(m.group(2))
    return out


def doc_bodies():
    """文書側で本文記述を持つ版の集合。

    記述の形は3通りある。いずれも正当な転記なので、どれか1つでも該当すれば「記述あり」とする。
      (a) 見出し節（`### ▫️ 1.0.165` / `## 🔹 1.0.52`）の配下に箇条書き・表・段落がある
      (b) パッチ節の本文（`**0.11.130**（2026-04-02）— 概要`）
      (c) パッチ一覧表の行（`| **0.6.29** | 2025-11-27 | 概要 |`）
    """
    have = set()
    for f in DOC_FILES:
        try:
            txt = open(f, encoding="utf-8").read()
        except OSError:
            continue

        # (c) 表形式：内容セルが空でないこと
        for m in re.finditer(r'^\|\s*\*\*(\d+\.\d+\.\d+)\*\*\s*\|[^|]*\|([^|]*)\|', txt, re.M):
            if m.group(2).strip():
                have.add(m.group(1))

        # (b) パッチ節の本文
        for m in re.finditer(r'^\*\*(\d+\.\d+\.\d+)\*\*（\d{4}-\d{2}-\d{2}）\s*—\s*\S', txt, re.M):
            have.add(m.group(1))

        # (a) 見出し節：次の見出しまでに本文行があること
        heads = list(re.finditer(r'^(#{2,4}) .*?(\d+\.\d+(?:\.\d+)?)', txt, re.M))
        for i, m in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(txt)
            region = txt[m.end():end]
            body = [
                ln for ln in region.splitlines()
                # メタ情報・明示アンカー・区切り線は「記述」に数えない
                if ln.strip()
                and not ln.startswith(("**リリース日**:", "**公式ページ**:", "<a id=", "---"))
            ]
            if body:
                have.add(m.group(2))
    return have


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--html-dir", help="取得済み changelog HTML のディレクトリ")
    src.add_argument("--json", help="extract-changelog.py の出力 JSON")
    args = ap.parse_args()

    os.chdir(repo_root())

    print("=== changelog 網羅性チェック（一次情報との突き合わせ） ===")
    print("")

    if args.json:
        pages = json.load(open(args.json, encoding="utf-8"))
        origin = args.json
    else:
        html_dir = args.html_dir
        if not html_dir:
            print("⚠️  一次情報が指定されていないためスキップしました")
            print("   使い方: check-coverage.py --html-dir <dir> | --json <file>")
            print("   （一次情報の取得手順は 05_meta/10_version-update-guide.md を参照）")
            return 0
        files = sorted(glob.glob(os.path.join(html_dir, "*.html")))
        if not files:
            print(f"❌ {html_dir} に HTML がありません")
            return 2
        ex = load_extractor()
        pages = []
        for path in files:
            d = ex.extract(path)
            if not d["title"]:
                print(f"❌ {path}: 本文を抽出できませんでした（ページ構造の変化を疑ってください）")
                return 2
            pages.append(d)
        origin = f"{html_dir}（{len(files)} ページ）"

    truth = primary(pages)
    doc = doc_versions()
    bodies = doc_bodies()

    print(f"一次情報: {origin}")
    print(f"  一次情報の版数: {len(truth)}")
    print(f"  文書の版数:     {len(doc)}")
    print("")

    errors = []
    vkey = lambda v: [int(x) for x in v.split(".")]

    # ---- 1. 版の網羅性 ----
    missing = sorted(set(truth) - set(doc), key=vkey)
    extra = sorted(set(doc) - set(truth), key=vkey)
    for v in missing:
        errors.append(f"一次情報にあるが文書に無い版: {v}（{truth[v]['date']}）")
    for v in extra:
        errors.append(f"文書にあるが一次情報に無い版: {v}（誤記または一次情報の取得漏れ）")

    # ---- 2. 日付の一致 ----
    for v in sorted(set(truth) & set(doc), key=vkey):
        if truth[v]["date"] not in doc[v]:
            errors.append(
                f"{v} の日付が一次情報と不一致: 一次={truth[v]['date']} 文書={sorted(doc[v])}"
            )

    # ---- 3. 説明の転記 ----
    described = [v for v, d in truth.items() if d["described"]]
    for v in sorted(set(described) - bodies, key=vkey):
        errors.append(
            f"{v} は公式に説明があるのに文書に本文記述がありません（転記漏れ）"
        )

    print(f"公式に説明がある版: {len(described)} / {len(truth)}")
    print(f"文書に本文記述がある版: {len(bodies)}")
    print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 網羅性チェックに失敗しました")
        return 1

    print("✅ 全ての版・日付・説明が一次情報と一致しています")
    return 0


if __name__ == "__main__":
    sys.exit(main())
