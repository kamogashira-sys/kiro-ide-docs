#!/usr/bin/env python3
"""check-notation.py - kiro-ide-docs 表記チェック（IDE 文脈で誤りになる表記の検出）

使用方法:
    ./scripts/kiro-ide-docs/check-notation.py

目的:
    Kiro CLI 版（姉妹サイト q-cli-docs）と同名機能が多いため、**CLI の表記が IDE 版に
    混入する**事故が起きやすい。それを機械的に落とす。
    加えて GitHub 上での表示事故（autolink 境界）と、本サイトの表記規約を検証する。

検証内容:
    (a) CLI コマンドの混入          … IDE は GUI 製品。`kiro-cli chat` 等は CLI 版の話
    (b) Amazon Q 時代の名称の無検証な使用 … 陳腐化の混入源（言及は文脈付きのみ許可）
    (c) 製品名の表記揺れ            … 「Kiro IDE」「Kiro CLI」に統一
    (d) バージョン番号の `v` プレフィックス … 本サイトは `1.0.242` 形式（`v1.0.242` は禁止）
    (e) 日付の非 ISO 表記           … `YYYY-MM-DD` に統一（`2026年7月28日` は禁止）
    (f) 取得日の本文混入            … 取得日は本文に書かない（出典日は書く）
    (g) 裸 URL 直後の全角文字        … GitHub の autolink が全角文字まで URL に含めて 404 になる

設計メモ:
    - (b)(d)(e) は**正当な用例が実在する**（公式原文の引用・Code OSS のバージョン）。
      機械判定できないものを一律禁止すると、回避のために事実を曲げることになる。
      そこで**許可する文脈をパターンで明示**し、実行時に許可した用例を全件表示する
      （暗黙に見逃さないため）。
    - **URL 書式（kiro.dev の末尾スラッシュ・CLI 版リンクの v3 規約）はここでは検証しない。**
      `check-links.py` が所有する規則であり、二重に持つと規約変更時に片方だけ古くなる。
      実際、実装時に本スクリプト側で「全 kiro.dev URL に末尾スラッシュ必須」と
      誤って一般化し、正しい URL を 20 件 false positive にした。
      正しい規則は「**changelog ページのみ**末尾スラッシュ必須」（`docs/` 配下や
      `feed.atom` は対象外）。
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-ide-docs"
LOCAL_ONLY = ("05_meta", "06_embedded-docs", "work_plans", "work_records")

CHANGELOG = f"{DOC_ROOT}/02_update/01_changelog.md"


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_local_only(path):
    norm = path.replace(os.sep, "/")
    return any(f"/{lo}/" in norm or norm.startswith(f"{lo}/") for lo in LOCAL_ONLY)


def public_docs():
    docs = [d for d in sorted(glob.glob(f"{DOC_ROOT}/**/*.md", recursive=True))
            if not is_local_only(d)]
    if os.path.isfile("README.md"):
        docs.append("README.md")
    # `.github/` の Markdown（WORKFLOW.md・COMMIT_CHECKLIST.md・PR テンプレート）も
    # **GitHub に公開される**ため表記規約の対象にする。
    # 対象外にしていたため、公開後に `.github/COMMIT_CHECKLIST.md` の
    # 「スラッシュなしは空応答になる」（実際は **301**）という誤りを見逃していた。
    # なお `check-consistency.py` の対象には**しない** — これらは
    # 「未確認と書く作法」を*説明する*文書で、規則 (e)（未確認に説明が伴うか）が
    # 誤検知する（実測2件）。
    docs += sorted(glob.glob(".github/**/*.md", recursive=True))
    return docs


def strip_fences(lines):
    """フェンスコードブロックの中身を空行にする（行番号を保つ）。

    コードブロックには設定例や公式の出力をそのまま載せるため、
    表記規約の対象外にする。
    """
    out, in_fence = [], False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else ln)
    return out


# ------------------------------------------------------------
# 規則定義
# ------------------------------------------------------------
# 各規則: (ラベル, 検出パターン, 正しい表記の説明, 許可パターン列)
# 許可パターンに一致する行は違反としない（理由を必ず添える）。
RULES = [
    (
        "(a) CLI コマンドの混入",
        re.compile(r"\bkiro-cli\s+(chat|login|logout|settings|agent|mcp|update|doctor)\b"),
        "Kiro IDE は GUI 製品。CLI の操作は姉妹サイト q-cli-docs の領域",
        [
            # 姉妹サイトの名称「猫でもわかるkiro-cli アップデート情報」は固有名詞
            (re.compile(r"猫でもわかるkiro-cli"), "姉妹サイトの正式名称"),
        ],
    ),
    (
        "(b) Amazon Q 時代の名称",
        re.compile(r"Amazon Q(?!\s+Developer)"),
        "現行の製品名は Kiro。旧名に触れるときは Amazon Q Developer と正式名で書く",
        [],
    ),
    (
        "(c) 製品名の表記揺れ",
        re.compile(r"\b(?:kiro\s+IDE|KIRO\s+IDE|Kiro-IDE|kiro\s+ide|Kiro-CLI|kiro\s+CLI)\b"),
        "「Kiro IDE」「Kiro CLI」に統一（半角スペース区切り）",
        [],
    ),
    (
        "(d) バージョンの v プレフィックス",
        re.compile(r"(?<![\w.])v\d+\.\d+\.\d+"),
        "Kiro のバージョンは `1.0.242` 形式（`v` を付けない）",
        # 許可判定は**一致箇所の周辺**で行う（行単位にすると、その行に
        # 「Code OSS」が出てくるだけで Kiro 版の `v1.0.242` も通ってしまう）。
        [
            # Code OSS のバージョンは上流の表記に従う（公式 changelog も v 付き）
            (re.compile(r"Code OSS\s*(?:は\s*)?$"), "直前が Code OSS（上流表記）"),
            (re.compile(r"Code OSS\s*v\d+\.\d+\.\d+\s*(?:から|へ)\s*$"),
             "Code OSS のバージョン移行の記述"),
            # 外部サイトの URL に含まれる版（Conventional Commits の /v1.0.0/ 等）
            (re.compile(r"https?://[^\s)]*$"), "外部 URL に含まれる版番号"),
        ],
    ),
    (
        "(e) 日付の非 ISO 表記",
        re.compile(r"\d{4}\s*年\s*\d{1,2}\s*月"),
        "日付は ISO 形式 `YYYY-MM-DD` に統一",
        [
            # 公式の注記をそのまま引用する場合は原文の表記を保つ（改変しないため）
            (re.compile(r"公式注記|公式の注記|原文"), "公式原文の引用"),
        ],
    ),
    (
        "(f) 取得日の本文混入",
        re.compile(r"\d{4}-\d{2}-\d{2}\s*取得"),
        "取得日は本文に書かない（書くのは公式ページの更新日＝出典日）",
        [],
    ),
    (
        "(g) 裸 URL 直後の全角文字",
        # 裸 URL の直後に非 ASCII があると GitHub の autolink が空白まで URL 扱いにする。
        # URL 文字クラスから ) > ] ` を除くので、明示リンク・<URL>・コードには当たらない。
        re.compile(r"https?://[\x21-\x28\x2A-\x3D\x3F-\x5C\x5E\x5F\x61-\x7E]*[^\x00-\x7F]"),
        "[表示文字](URL) の明示リンク・<URL>・`URL` のいずれかにする",
        [],
    ),
]
errors = []
allowed_hits = []


def main():
    os.chdir(repo_root())
    docs = public_docs()

    print("=== kiro-ide-docs 表記チェック ===")
    print("")

    print("🔍 表記規約の違反を検証中...")
    for doc in docs:
        try:
            with open(doc, encoding="utf-8") as f:
                lines = strip_fences(f.read().splitlines())
        except OSError:
            continue

        for i, ln in enumerate(lines):
            # インラインコードは (g) 以外の対象外にする（設定キー名や公式の値をそのまま書くため）
            no_code = re.sub(r"`[^`\n]*`", "", ln)

            for label, pattern, correct, allows in RULES:
                target = ln if label.startswith("(g)") else no_code
                # 1行に複数の違反があり得るので全件見る（先頭だけ見ると残りを見逃す）
                for m in pattern.finditer(target):
                    # 許可判定は**一致箇所の直前まで**の文字列に対して行う。
                    # 行全体で判定すると、同じ行のどこかに許可語があるだけで通ってしまう。
                    before = target[:m.start()]
                    allow_why = next((why for arex, why in allows if arex.search(before)), None)
                    if allow_why:
                        allowed_hits.append(
                            f"{doc}:{i + 1}: {label} '{m.group(0)}' … {allow_why}")
                        continue
                    errors.append(
                        f"{doc}:{i + 1}: {label} '{m.group(0)}' を検出"
                        f"（{correct}）: {ln.strip()[:70]}"
                    )

    print("")
    print("   （kiro.dev の URL 書式と CLI 版リンクの v3 規約は check-links.py が検証する）")
    print("=== チェック結果 ===")
    print(f"走査した公開 Markdown: {len(docs)} 件")
    if allowed_hits:
        print(f"許可した用例 {len(allowed_hits)} 件（暗黙に見逃さないため明示する）:")
        for a in allowed_hits:
            print(f"     {a}")
    print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 表記チェックに失敗しました")
        sys.exit(1)

    print("✅ 表記規約に違反はありません")
    sys.exit(0)


if __name__ == "__main__":
    main()
