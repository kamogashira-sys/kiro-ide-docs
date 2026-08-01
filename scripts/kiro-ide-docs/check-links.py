#!/usr/bin/env python3
"""check-links.py - kiro-ide-docs 内部リンク整合チェック

使用方法:
    ./scripts/kiro-ide-docs/check-links.py
    ./scripts/kiro-ide-docs/check-links.py --check-anchors   # アンカー(見出し)実在も検査(ASCIIのみ)
    ./scripts/kiro-ide-docs/check-links.py --check-anchors --paths <file...>
        # 指定ファイルのみ検査（既定の除外を適用しない。05_meta 等のローカル管理文書の
        # 相互リンク・目次アンカー検証用。--paths 時は非 ASCII アンカーも検査する）

機能:
    - kiro-ide-docs/**/*.md ＋ ルート README.md の相対 Markdown リンクを抽出
    - リンク先ファイルの実在を検証（アンカー #... は分離して判定）
    - kiro.dev の外部リンクの書式を検証:
        - changelog ページは末尾スラッシュ必須（`/changelog/ide/1-0` は空応答を返す）
        - Kiro CLI 版へのリンクは `docs/cli/v3/` を指す（非 v3 は 2.x 系の別仕様）
    - 上記以外の http(s)/mailto/tel/# 始まりは到達性を検証しない（check-urls.sh の担当）

除外（スコープ外・ローカル管理のため。ソースのスキャン／リンク先の検証の両方に適用）:
    - kiro-ide-docs/06_embedded-docs/**  … 公式サイトページのスナップショット（GitHub 非公開）
    - kiro-ide-docs/05_meta/**           … 保守手順書・テンプレート（GitHub 非公開）
    - kiro-ide-docs/work_plans/**        … 作業計画書（GitHub 非公開）
    - *_plan.md                          … gitignore 対象の計画書
"""
import glob
import os
import re
import sys

LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
# 素の URL（<https://...> 形式を含む）も書式検証の対象にする
BARE_URL_RE = re.compile(r'<?(https://kiro\.dev/[^\s>)"\']*)>?')
HEADING_RE = re.compile(r'^#{1,6}\s+(.*?)\s*$')
# 明示的な HTML アンカー（`<a id="v1-0-242"></a>`）。絵文字を含む見出しは
# slug の生成規則が処理系で揺れるため、リンク先には明示アンカーを使う。
HTML_ANCHOR_RE = re.compile(r'<a\s+(?:id|name)=["\']([^"\']+)["\']')

EXCLUDE_SUBSTR = (
    "kiro-ide-docs/06_embedded-docs/",   # 公式サイトページのスナップショット（GitHub 非公開）
    "kiro-ide-docs/05_meta",             # 保守手順書・テンプレート（GitHub 非公開）
    "kiro-ide-docs/work_plans",          # 作業計画書（GitHub 非公開）
    "work_records/",                     # 作業記録（GitHub 非公開）
    "_plan.md",                          # *_plan.md は gitignore 対象の計画書
)
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "#")

# GitHub が解決する相対リンク（`../../issues` = リポジトリの Issues タブ）。
# ファイルシステム上には存在しないため実在検証の対象外にする。
GITHUB_RELATIVE = ("../../issues", "../../pulls", "../../discussions", "../../wiki")

# kiro.dev の changelog は末尾スラッシュがないと空応答になる（実測）
CHANGELOG_RE = re.compile(r'^https://kiro\.dev/changelog/[^\s]*$')
# Kiro CLI 版のドキュメントへのリンク
CLI_DOCS_RE = re.compile(r'^https://kiro\.dev/docs/cli/([^\s#?]*)')
# IDE 1.0 の GA 機能に対応する CLI ページは v3。非 v3 は 2.x 系の別仕様なので誤リンクを弾く。
# hooks は特に別物（IDE: .kiro/hooks/*.json ／ CLI 非 v3: stdin JSON のライフサイクルフック）。
CLI_V3_REQUIRED = ("permissions", "agent-config", "custom-agents", "hooks")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_excluded(path):
    norm = path.replace(os.sep, "/")
    return any(sub in norm for sub in EXCLUDE_SUBSTR)


def slugify(heading):
    """GitHub 風 slug。記号除去・空白をハイフン・小文字化。
    GitHub は空白 1 文字ごとにハイフン 1 つ（連続空白を潰さない。例: 「a / b」→ a--b）。"""
    s = heading.strip().lower()
    s = s.replace("`", "")
    s = re.sub(r"[^\w\s\-ぁ-んァ-ヶ一-龠ー]", "", s)
    return re.sub(r"\s", "-", s)


def strip_code(txt):
    """フェンスコードブロックとインラインコードスパンを除去（コード内のリンク記法例は
    Markdown ではリンクとして描画されないため、リンク抽出の対象外にする）。"""
    out = []
    in_fence = False
    for line in txt.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(re.sub(r"`[^`\n]*`", "", line))
    return "".join(out)


def collect_headings(filepath):
    slugs = set()
    in_fence = False
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                # フェンス内の「# コメント」を見出しと誤認しない
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for m in HTML_ANCHOR_RE.finditer(line):
                    slugs.add(m.group(1).lower())
                m = HEADING_RE.match(line)
                if m:
                    slugs.add(slugify(m.group(1)))
    except OSError:
        pass
    return slugs


def check_kiro_url(url):
    """kiro.dev の URL の書式を検証し、問題があれば理由を返す（なければ None）。"""
    # フィードは静的ファイルなので末尾スラッシュの規則は適用されない
    is_page = not os.path.splitext(url)[1]
    if is_page and CHANGELOG_RE.match(url) and not url.endswith("/"):
        return "changelog の URL は末尾スラッシュが必須（スラッシュなしは空応答を返す）"
    m = CLI_DOCS_RE.match(url)
    if m:
        rest = m.group(1).rstrip("/")
        if not rest.startswith("v3/"):
            page = rest.split("/")[-1]
            if page in CLI_V3_REQUIRED:
                return (f"Kiro CLI 版の '{page}' は `docs/cli/v3/{page}` を指すこと"
                        "（非 v3 は 2.x 系の別仕様）")
    return None


def main():
    args = sys.argv[1:]
    check_anchors = "--check-anchors" in args
    paths_mode = "--paths" in args
    target_paths = []
    if paths_mode:
        # --paths 以降をすべて検査対象ファイルとして受け取る（フラグは --paths より前に置く）
        target_paths = args[args.index("--paths") + 1:]
        if not target_paths:
            print("❌ --paths にファイルを 1 つ以上指定してください")
            sys.exit(2)
    os.chdir(repo_root())

    if paths_mode:
        missing = [p for p in target_paths if not os.path.isfile(p)]
        if missing:
            for p in missing:
                print(f"❌ --paths 指定ファイルが存在しません: {p}")
            sys.exit(2)
        files = sorted(target_paths)
    else:
        files = sorted(glob.glob("kiro-ide-docs/**/*.md", recursive=True)) + ["README.md"]

    checked = 0
    url_checked = 0
    broken = []
    anchor_broken = []
    bad_urls = []
    anchor_skipped = 0
    heading_cache = {}

    for f in files:
        if not paths_mode and (is_excluded(f) or f.endswith(".bak")):
            continue
        base = os.path.dirname(f)
        try:
            txt = open(f, encoding="utf-8").read()
        except OSError:
            continue
        # コードブロック内のリンク記法例・コマンド例の URL を誤検出しない
        txt = strip_code(txt)

        # kiro.dev の URL 書式検証（Markdown リンクと素の URL の両方）
        seen_urls = set()
        for m in BARE_URL_RE.finditer(txt):
            url = m.group(1).rstrip(".,)")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            url_checked += 1
            reason = check_kiro_url(url)
            if reason:
                bad_urls.append((f, url, reason))

        for m in LINK_RE.finditer(txt):
            target = m.group(2).strip()
            # 同一ファイル内アンカー（#... のみのリンク）は既定ではスキップ。
            # --paths では目次アンカー検証が目的のため検査する。
            if target.startswith("#"):
                if paths_mode and check_anchors:
                    anchor = target[1:]
                    checked += 1
                    if f not in heading_cache:
                        heading_cache[f] = collect_headings(f)
                    if anchor.lower() not in heading_cache[f]:
                        anchor_broken.append((f, target, anchor))
                continue
            if target.startswith(SKIP_PREFIX):
                continue
            if target.rstrip("/") in GITHUB_RELATIVE:
                continue
            path, _, anchor = target.partition("#")
            if not path:
                continue
            resolved = os.path.normpath(os.path.join(base, path))
            # 除外パス（GitHub 非公開のローカル管理領域）へのリンクは検証対象外。
            # --paths ではローカル管理文書そのものを検査するため除外を適用しない。
            if not paths_mode and is_excluded(resolved):
                continue
            checked += 1
            if not os.path.exists(resolved):
                broken.append((f, target, resolved))
                continue
            # アンカー検査（任意）
            if check_anchors and anchor and resolved.endswith(".md"):
                # 非 ASCII を含むアンカーはスラッグ規則が複雑なため既定ではスキップ（誤検知防止）。
                # --paths は目次アンカー検証が目的（対象が少なく目視確認可能）のため日本語も検査する。
                if not anchor.isascii() and not paths_mode:
                    anchor_skipped += 1
                    continue
                if resolved not in heading_cache:
                    heading_cache[resolved] = collect_headings(resolved)
                if anchor.lower() not in heading_cache[resolved]:
                    anchor_broken.append((f, target, anchor))

    print("=== kiro-ide-docs 内部リンク整合チェック ===")
    print("")
    print(f"チェックした相対リンク数: {checked}")
    print(f"リンク切れ: {len(broken)} 件")
    for f, t, r in broken:
        print(f"  ❌ {f}: '{t}' -> {r}")

    print("")
    print(f"kiro.dev URL の書式チェック: {url_checked} 件中 {len(bad_urls)} 件が不正")
    for f, u, reason in bad_urls:
        print(f"  ❌ {f}: {u}")
        print(f"      → {reason}")

    if check_anchors:
        print("")
        print(f"アンカー検査: 切れ {len(anchor_broken)} 件 / スキップ(非ASCII) {anchor_skipped} 件")
        for f, t, a in anchor_broken:
            print(f"  ⚠️  {f}: '{t}'（見出し '#{a}' が見つからない）")

    print("")
    total_errors = len(broken) + len(bad_urls) + (len(anchor_broken) if check_anchors else 0)
    if total_errors > 0:
        print("❌ リンクチェックに失敗しました")
        sys.exit(1)
    print("✅ すべての内部リンクと kiro.dev URL の書式が有効です")
    sys.exit(0)


if __name__ == "__main__":
    main()
