#!/usr/bin/env python3
"""check-structure.py - kiro-ide-docs のディレクトリ・文書構造チェック

使用方法:
    ./scripts/kiro-ide-docs/check-structure.py

検証内容:
    1. 公開5セクション（D6 確定構成）が存在すること
    2. 各セクションに README.md があること（未着手セクションは .gitkeep のみを許容）
    3. 各 Markdown が H1 見出しから始まること
    4. `04_reference/` は確定した5ファイル軸に沿っていること
    5. ローカル管理セクション（05_meta / 06_embedded-docs / work_plans）が
       公開文書から参照されていないこと（公開リポジトリからは辿れないため）
    6. CLI 版へのリンクが `docs/cli/v3/` を指していること（非 v3 は 2.x の別仕様）

規則は Phase 2a では最小集合とし、量産（Phase 2b）に合わせて拡張する。
未執筆のセクションは「まだ執筆されていない」として警告にとどめ、エラーにしない。
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-ide-docs"

# D6 で確定した公開セクション
PUBLIC_SECTIONS = [
    "00_information",
    "01_features",
    "02_update",
    "03_deployment",
    "04_reference",
]

# ローカル管理（GitHub 非公開）。公開文書からリンクしてはいけない。
LOCAL_ONLY = ["05_meta", "06_embedded-docs", "work_plans"]

# 04_reference/ の確定した軸（D12・G1 確定）。CLI 版の写しではない。
# 06 は公式に対応ページが存在しない実測値ベースのページ（`kiro --help` の出力）。
REFERENCE_FILES = [
    "01_kiro-directory.md",
    "02_keyboard-shortcuts.md",
    "03_permissions.md",
    "04_context-providers.md",
    "05_models.md",
    "06_launch-options.md",
]

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
CLI_DOCS_RE = re.compile(r'https://kiro\.dev/docs/cli/([^\s#?)]*)')
# IDE 1.0 の GA 機能に対応する CLI ページは v3 のみ
CLI_V3_REQUIRED = ("permissions", "agent-config", "custom-agents", "hooks")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def strip_code(txt):
    """フェンスコードブロックとインラインコードを除去する。"""
    out, in_fence = [], False
    for line in txt.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(re.sub(r"`[^`\n]*`", "", line))
    return "".join(out)


def main():
    os.chdir(repo_root())
    errors, warnings = [], []

    print("=== kiro-ide-docs 構造チェック ===")
    print("")

    # ---- 1. 公開セクションの存在 ----
    print("🔍 公開セクションの存在を検証中...")
    for sec in PUBLIC_SECTIONS:
        path = os.path.join(DOC_ROOT, sec)
        if not os.path.isdir(path):
            errors.append(f"公開セクションがありません: {path}")

    # ---- 2. セクションの README ----
    print("🔍 各セクションの README を検証中...")
    written_sections = []
    for sec in PUBLIC_SECTIONS:
        path = os.path.join(DOC_ROOT, sec)
        if not os.path.isdir(path):
            continue
        mds = [f for f in os.listdir(path) if f.endswith(".md")]
        if not mds:
            # 未着手セクション（.gitkeep のみ）は Phase 2b で執筆する
            warnings.append(f"{sec}/ はまだ執筆されていません（Phase 2b で執筆）")
            continue
        written_sections.append(sec)
        if "README.md" not in mds:
            errors.append(f"{sec}/ に README.md がありません（本文が {len(mds)} 件あるのに索引がない）")

    # ---- 3. H1 見出しから始まっているか ----
    print("🔍 各 Markdown の H1 見出しを検証中...")
    docs = sorted(glob.glob(f"{DOC_ROOT}/**/*.md", recursive=True))
    docs = [d for d in docs if not any(f"/{lo}/" in d.replace(os.sep, "/") or
                                       d.replace(os.sep, "/").endswith(f"/{lo}")
                                       for lo in LOCAL_ONLY)]
    for d in docs:
        try:
            with open(d, encoding="utf-8") as f:
                first = next((ln for ln in f if ln.strip()), "")
        except OSError:
            continue
        if not first.startswith("# "):
            errors.append(f"{d}: H1 見出し（`# `）から始まっていません: {first.strip()[:40]!r}")

    # ---- 4. 04_reference/ の軸 ----
    print("🔍 04_reference/ のファイル軸を検証中...")
    ref_dir = os.path.join(DOC_ROOT, "04_reference")
    if os.path.isdir(ref_dir):
        present = {f for f in os.listdir(ref_dir) if f.endswith(".md")}
        if present:
            unexpected = present - set(REFERENCE_FILES) - {"README.md"}
            if unexpected:
                errors.append(
                    f"04_reference/ に想定外のファイルがあります: {sorted(unexpected)}"
                    f"（確定した軸は {REFERENCE_FILES}）"
                )
            missing = set(REFERENCE_FILES) - present
            if missing:
                warnings.append(f"04_reference/ の未執筆ファイル: {sorted(missing)}")

    # ---- 5・6. 公開文書からのリンク先 ----
    print("🔍 公開文書からのリンク先を検証中...")
    for d in docs:
        try:
            txt = strip_code(open(d, encoding="utf-8").read())
        except OSError:
            continue
        for m in LINK_RE.finditer(txt):
            target = m.group(1).strip()
            # ローカル管理領域へのリンク（公開リポジトリからは辿れない）
            norm = target.replace(os.sep, "/")
            for lo in LOCAL_ONLY:
                if f"{lo}/" in norm and not norm.startswith(("http://", "https://")):
                    errors.append(
                        f"{d}: ローカル管理領域へのリンクがあります: '{target}'"
                        f"（{lo}/ は GitHub 非公開のため公開リポジトリから辿れない）"
                    )
        for m in CLI_DOCS_RE.finditer(txt):
            rest = m.group(1).rstrip("/")
            if not rest.startswith("v3/") and rest.split("/")[-1] in CLI_V3_REQUIRED:
                errors.append(
                    f"{d}: Kiro CLI 版へのリンクが v3 を指していません: 'docs/cli/{rest}'"
                    "（非 v3 は 2.x 系の別仕様）"
                )

    # ---- 結果 ----
    print("")
    print("=== チェック結果 ===")
    print(f"検証した公開 Markdown: {len(docs)} 件")
    print(f"執筆済みセクション: {len(written_sections)} / {len(PUBLIC_SECTIONS)}"
          f"（{', '.join(written_sections) or 'なし'}）")
    print("")

    if warnings:
        print(f"⚠️  警告 {len(warnings)} 件（未執筆。エラーではない）:")
        for w in warnings:
            print(f"   - {w}")
        print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 構造チェックに失敗しました")
        sys.exit(1)

    print("✅ 構造は健全です")
    sys.exit(0)


if __name__ == "__main__":
    main()
