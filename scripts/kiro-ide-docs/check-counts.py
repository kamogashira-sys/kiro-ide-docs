#!/usr/bin/env python3
"""check-counts.py - kiro-ide-docs 数値整合チェック（正準値の水平展開）

使用方法:
    ./scripts/kiro-ide-docs/check-counts.py

目的:
    「表を1行増やしたのに本文の件数を直し忘れた」を機械的に落とす。
    表（実体）から件数を数え、それを**正準値**として文書中の件数記述と突き合わせる。

検証する正準値（作業計画書 D12）:
    第1: 機能数            = 01_features/README.md の機能一覧テーブルのデータ行数
    第2: ショートカット数   = 04_reference/02_keyboard-shortcuts.md の
                              カテゴリ節（`## 名前（N件）`）のデータ行数の合計
    予備: capability 数     = 04_reference/03_permissions.md の capability 一覧の行数
    予備: プロバイダ数      = 04_reference/04_context-providers.md の一覧の行数

3方向から突き合わせる:
    (a) 節見出しの `（N件）` が、その節の表の実行数と一致するか
    (b) 内訳表・「収録件数」行・カテゴリ名の直後の数値が実体と一致するか
    (c) 文書全体の件数記述（正準値の所有ファイルへリンクする行／キーワード近傍）が
        正準値と一致するか

注意:
    - 作業計画書 Phase 3-1 では `check-counts.sh` としていたが、節ごとの表の
      行数集計を確実に行うため Python で実装した（links / structure / coverage と同じ方針）。
    - 「N件」「N種」は日本語の一般的な助数詞のため、全件を機械判定すると
      部分集合の記述（「AI features の3件」等）を誤検出する。そのため
      **正準値ごとに検出対象の文脈を限定**し、部分集合として妥当な数値は
      SUBSET_OK に明示列挙する（暗黙に見逃さないため、実行時に一覧を表示する）。
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-ide-docs"

# ローカル管理（GitHub 非公開）。件数記述の走査対象から除く。
LOCAL_ONLY = ("05_meta", "06_embedded-docs", "work_plans", "work_records")

SEP_RE = re.compile(r"^\s*\|[\s:\-|]+\|\s*$")
ROW_RE = re.compile(r"^\s*\|")
H2_RE = re.compile(r"^##\s+(.*?)\s*$")
# 数値。直前が数字か `.` の場合は拾わない
# （節番号 `### 4.5 機能を使う場合...` の "5 機能"、バージョン番号 `1.0` を件数と誤読しないため）
NUM = r"(?<![\d.])(\d+)"
COUNT_RE = NUM + r"\s*(?:件|種|機能|個)"
# Markdown リンクの宛先
LINK_RE = re.compile(r"\]\(([^)\s]+)")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_local_only(path):
    norm = path.replace(os.sep, "/")
    return any(f"/{lo}/" in norm or norm.startswith(f"{lo}/") for lo in LOCAL_ONLY)


def public_docs():
    """公開対象の Markdown（ルート README.md を含む）。"""
    docs = [d for d in sorted(glob.glob(f"{DOC_ROOT}/**/*.md", recursive=True))
            if not is_local_only(d)]
    if os.path.isfile("README.md"):
        docs.append("README.md")
    return docs


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def strip_fences(lines):
    """フェンスコードブロックの中身を空行に置き換える（行番号を保つ）。"""
    out, in_fence = [], False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else ln)
    return out


def count_data_rows(lines):
    """Markdown 表のデータ行数を数える。

    ヘッダ行（次の行が区切り行）と区切り行は数えない。
    節の中に表が複数あっても正しく数えられる。
    """
    n = 0
    for i, ln in enumerate(lines):
        if not ROW_RE.match(ln) or SEP_RE.match(ln):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if SEP_RE.match(nxt):
            continue  # ヘッダ行
        n += 1
    return n


def h2_sections(lines):
    """`## ` 見出しごとに (見出しテキスト, 本文行, 見出しの行番号) を返す。"""
    out, cur, body, start = [], None, [], 0
    for i, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if m:
            if cur is not None:
                out.append((cur, body, start))
            cur, body, start = m.group(1), [], i + 1
        elif cur is not None:
            body.append(ln)
    if cur is not None:
        out.append((cur, body, start))
    return out


def find_section(lines, needle):
    """見出しに needle を含む最初の `## ` 節を返す。"""
    for title, body, start in h2_sections(lines):
        if needle in title:
            return title, body, start
    return None, None, None


# ------------------------------------------------------------
# 正準値の定義
# ------------------------------------------------------------
FEATURE_DOC = f"{DOC_ROOT}/01_features/README.md"
SHORTCUT_DOC = f"{DOC_ROOT}/04_reference/02_keyboard-shortcuts.md"
PERMISSION_DOC = f"{DOC_ROOT}/04_reference/03_permissions.md"
PROVIDER_DOC = f"{DOC_ROOT}/04_reference/04_context-providers.md"

# 部分集合として妥当な数値（正準値と異なっていてもエラーにしない）。
# 暗黙に見逃さないよう、根拠を必ず添えて列挙する。
SUBSET_OK = {
    "機能数": {
        3: "1.0 で追加された3機能（Permissions・Custom Agents・Agent Focus Mode）は部分集合",
    },
    "ショートカット数": {
        9: "General カテゴリの件数", 11: "Navigation カテゴリの件数",
        6: "Editing カテゴリの件数", 3: "AI features カテゴリの件数",
    },
    "capability数": {},
    "プロバイダ数": {},
}

errors = []
warnings = []


def err(msg):
    # 同じ行が複数の規則（リンク経由とキーワード経由）に当たることがあるため重複を除く
    if msg not in errors:
        errors.append(msg)


# ------------------------------------------------------------
# 第1正準値: 機能数
# ------------------------------------------------------------
def canonical_feature_count():
    """01_features/README.md の機能一覧テーブルのデータ行数。

    「今後追加する機能」節の表は**含めない**（公式ページへの外部リンクのみで
    本サイトの収録機能ではない）。節境界で切り出すことで構造的に除外する。
    """
    lines = strip_fences(read_lines(FEATURE_DOC))
    title, body, _ = find_section(lines, "機能一覧")
    if body is None:
        err(f"{FEATURE_DOC}: 「機能一覧」の `## ` 節が見つかりません（正準値を抽出できない）")
        return None

    rows = count_data_rows(body)

    # 見出しの「（N機能）」と一致するか
    m = re.search(r"[（(]\s*(\d+)\s*機能", title)
    if not m:
        err(f"{FEATURE_DOC}: 機能一覧の見出しに「（N機能）」がありません: '{title}'")
    elif int(m.group(1)) != rows:
        err(f"{FEATURE_DOC}: 見出し '{title}' の件数が表の実行数と不一致"
            f"（見出し={m.group(1)} 実際={rows}）")

    # 「今後追加する機能」節に本サイト内ページへのリンクが混ざっていないか
    _, future, fstart = find_section(lines, "今後追加する機能")
    if future is not None:
        for i, ln in enumerate(future):
            if not ROW_RE.match(ln) or SEP_RE.match(ln):
                continue
            if re.search(r"\]\((?!https?://)[^)]*\d\d_[^)]+\.md", ln):
                err(f"{FEATURE_DOC}:{fstart + i + 1}: 「今後追加する機能」の表が"
                    "本サイト内のページを指しています（執筆したなら機能一覧へ移す）")

    # 実ファイル数との突き合わせ（表に載せ忘れ／消し忘れを検出する）
    feature_files = sorted(
        os.path.basename(p) for p in glob.glob(f"{DOC_ROOT}/01_features/[0-9][0-9]_*.md")
    )
    if len(feature_files) != rows:
        err(f"機能ページのファイル数が機能一覧の行数と不一致"
            f"（ファイル={len(feature_files)} 表={rows}）: {feature_files}")

    # 表の各行がリンクしているファイルが実在するか（並びの取り違えも見える）
    linked = re.findall(r"\]\((\d\d_[^)]+\.md)\)", "\n".join(body))
    missing = [f for f in linked if not os.path.isfile(f"{DOC_ROOT}/01_features/{f}")]
    if missing:
        err(f"{FEATURE_DOC}: 機能一覧が実在しないページを指しています: {missing}")
    unlisted = sorted(set(feature_files) - set(linked))
    if unlisted:
        err(f"{FEATURE_DOC}: 機能ページが機能一覧に載っていません: {unlisted}")

    return rows


# ------------------------------------------------------------
# 第2正準値: ショートカット数
# ------------------------------------------------------------
def canonical_shortcut_count():
    """カテゴリ節（`## 名前（N件）`）のデータ行数の合計。

    「ショートカットをカスタマイズする」のような手順表は `（N件）` を持たないため
    自動的に対象外になる（公式の「Custom shortcuts」は表を持たない）。
    """
    lines = strip_fences(read_lines(SHORTCUT_DOC))
    per_cat = {}
    for title, body, start in h2_sections(lines):
        m = re.match(r"^(.*?)\s*[（(]\s*(\d+)\s*件\s*[）)]\s*$", title)
        if not m:
            continue
        name, declared = m.group(1).strip(), int(m.group(2))
        actual = count_data_rows(body)
        per_cat[name] = actual
        if declared != actual:
            err(f"{SHORTCUT_DOC}:{start}: 見出し '{title}' の件数が表の実行数と不一致"
                f"（見出し={declared} 実際={actual}）")

    if not per_cat:
        err(f"{SHORTCUT_DOC}: カテゴリ節（`## 名前（N件）`）が見つかりません（正準値を抽出できない）")
        return None, {}

    total = sum(per_cat.values())

    # 文書内でカテゴリ名の直後に書かれた数値（内訳表・「収録件数」の括弧書き・本文）
    for i, ln in enumerate(lines):
        if H2_RE.match(ln):
            continue  # 見出しは上で検証済み
        for name, actual in per_cat.items():
            for m in re.finditer(re.escape(name) + r"[^0-9\n]{0,8}?(\d+)", ln):
                if int(m.group(1)) != actual:
                    err(f"{SHORTCUT_DOC}:{i + 1}: カテゴリ '{name}' の件数が実体と不一致"
                        f"（記述={m.group(1)} 実際={actual}）: {ln.strip()[:70]}")

    # 内訳表の「合計」行
    found_total_row = False
    for i, ln in enumerate(lines):
        for m in re.finditer(r"合計[^0-9\n]{0,8}?(\d+)", ln):
            found_total_row = True
            if int(m.group(1)) != total:
                err(f"{SHORTCUT_DOC}:{i + 1}: 内訳表の合計がカテゴリの総和と不一致"
                    f"（記述={m.group(1)} 総和={total}）")
    if not found_total_row:
        warnings.append(f"{SHORTCUT_DOC}: 内訳表に「合計」行が見つかりません")

    return total, per_cat


# ------------------------------------------------------------
# 予備の正準値
# ------------------------------------------------------------
def canonical_table_count(path, needle, label):
    """`## ` 見出しに needle を含む節の表の行数を正準値として返す。"""
    if not os.path.isfile(path):
        err(f"{path}: ファイルがありません（{label} の正準値を抽出できない）")
        return None
    lines = strip_fences(read_lines(path))
    title, body, start = find_section(lines, needle)
    if body is None:
        err(f"{path}: 「{needle}」の `## ` 節が見つかりません（{label} の正準値を抽出できない）")
        return None
    rows = count_data_rows(body)
    m = re.search(r"[（(]\s*(\d+)\s*(?:種|件)", title)
    if not m:
        err(f"{path}: 見出しに「（N種）」がありません: '{title}'")
    elif int(m.group(1)) != rows:
        err(f"{path}:{start}: 見出し '{title}' の件数が表の実行数と不一致"
            f"（見出し={m.group(1)} 実際={rows}）")
    return rows


# ------------------------------------------------------------
# 文書全体の件数記述との突き合わせ
# ------------------------------------------------------------
def links_to_owner(line, base_dir, owner_norm):
    """行中の Markdown リンクが正準値の所有ファイルを指しているか。"""
    for m in LINK_RE.finditer(line):
        target = m.group(1).split("#")[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = os.path.normpath(os.path.join(base_dir, target)).replace(os.sep, "/")
        if resolved == owner_norm:
            return True
    return False



def check_claims(label, canonical, owner_doc, keyword_res, docs):
    """件数記述を集めて正準値と突き合わせる。

    検出対象:
      (a) 正準値の所有ファイルへリンクしている行に含まれる件数
      (b) keyword_res（キーワード近傍パターン）に一致する行の件数
      (c) 所有ファイル内の「収録件数」行
    """
    owner_norm = owner_doc.replace(os.sep, "/")
    subset_ok = SUBSET_OK.get(label, {})
    checked = 0

    for doc in docs:
        try:
            lines = strip_fences(read_lines(doc))
        except OSError:
            continue
        base_dir = os.path.dirname(doc)
        for i, ln in enumerate(lines):
            nums = []

            # (a) 所有ファイルへのリンクを含む行
            # リンク先を実際に解決して比較する。basename 一致で判定すると
            # 「どの README.md へのリンクでも一致」してしまい誤検出になる。
            if links_to_owner(ln, base_dir, owner_norm):
                nums += [int(m.group(1)) for m in re.finditer(COUNT_RE, ln)]

            # (b) キーワード近傍
            for kre in keyword_res:
                nums += [int(m.group(1)) for m in kre.finditer(ln)]

            # (c) 所有ファイル内の「収録件数」行
            if doc == owner_doc and "収録件数" in ln:
                nums += [int(m.group(1)) for m in re.finditer(COUNT_RE, ln)]

            for n in nums:
                checked += 1
                if n == canonical:
                    continue
                if n in subset_ok:
                    continue
                err(f"{doc}:{i + 1}: {label}の記述が正準値と不一致"
                    f"（記述={n} 正準値={canonical}）: {ln.strip()[:70]}")

    return checked


def main():
    os.chdir(repo_root())
    docs = public_docs()

    print("=== kiro-ide-docs 数値整合チェック（正準値の水平展開） ===")
    print("")

    print("🔍 正準値を表から抽出中...")
    feature = canonical_feature_count()
    shortcut, per_cat = canonical_shortcut_count()
    capability = canonical_table_count(PERMISSION_DOC, "capability 一覧", "capability数")
    provider = canonical_table_count(PROVIDER_DOC, "一覧", "プロバイダ数")

    print(f"   第1: 機能数           = {feature}")
    if per_cat:
        breakdown = "・".join(f"{k} {v}" for k, v in per_cat.items())
        print(f"   第2: ショートカット数 = {shortcut}（{breakdown}）")
    else:
        print(f"   第2: ショートカット数 = {shortcut}")
    print(f"   予備: capability 数   = {capability}")
    print(f"   予備: プロバイダ数    = {provider}")
    print("")

    print("🔍 文書中の件数記述を検証中...")
    total_checked = 0

    if feature is not None:
        total_checked += check_claims(
            "機能数", feature, FEATURE_DOC,
            [re.compile(NUM + r"\s*機能")],
            docs,
        )
    if shortcut is not None:
        total_checked += check_claims(
            "ショートカット数", shortcut, SHORTCUT_DOC,
            [
                re.compile(r"ショートカット[^。\n]{0,12}?" + COUNT_RE),
                re.compile(COUNT_RE + r"[^。\n]{0,10}?ショートカット"),
            ],
            docs,
        )
    if capability is not None:
        total_checked += check_claims(
            "capability数", capability, PERMISSION_DOC,
            [re.compile(r"capability[^。\n]{0,10}?" + COUNT_RE)],
            docs,
        )
    if provider is not None:
        total_checked += check_claims(
            "プロバイダ数", provider, PROVIDER_DOC,
            [
                re.compile(r"プロバイダ[^。\n]{0,10}?" + COUNT_RE),
                re.compile(COUNT_RE + r"[^。\n]{0,10}?プロバイダ"),
            ],
            docs,
        )

    print("")
    print("=== チェック結果 ===")
    print(f"走査した公開 Markdown: {len(docs)} 件 / 検証した件数記述: {total_checked} 箇所")
    print("部分集合として許可した数値（暗黙に見逃さないため明示する）:")
    for label, allowed in SUBSET_OK.items():
        for n, why in sorted(allowed.items()):
            print(f"     許可 {label}={n} … {why}")
    print("")

    if warnings:
        print(f"⚠️  警告 {len(warnings)} 件:")
        for w in warnings:
            print(f"   - {w}")
        print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 数値整合チェックに失敗しました")
        sys.exit(1)

    print("✅ 正準値は表の実体と全箇所の記述で一致しています")
    sys.exit(0)


if __name__ == "__main__":
    main()
