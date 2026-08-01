#!/usr/bin/env python3
"""check-consistency.py - kiro-ide-docs 用語・記述整合チェック

使用方法:
    ./scripts/kiro-ide-docs/check-consistency.py

目的:
    「片方の文書だけ直して、もう片方が古いまま」を落とす。
    件数の整合は check-counts.py が見るので、こちらは**文章として矛盾する記述**を見る。

検証内容:
    (a) 最新版の整合      … 各所の「最新版 = X」が changelog の目次先頭と一致するか
    (b) 版番号の実在      … 本文が参照する版が changelog にあるか（**警告のみ**。下記参照）
    (c) 出典日の明記      … リファレンス・機能ページに公式ページの更新日があるか
    (d) 誤解を招く断定    … 公式が明示的に否定している内容を肯定していないか
    (e) 「未確認」の作法  … 未確認の記述に、何が未確認かの説明があるか
    (f) 食い違い注記の維持 … 公式ページ間の食い違い（F-14）を書いた箇所が
                             対になる相手ページからも辿れるか

設計メモ:
    - (d) は本サイトが最も避けたい誤りを対象にする。特に
      **「Supervised モードはセキュリティ機構ではない」**（公式が警告として明記）を
      肯定形で書いてしまう事故は、読者に安全でない運用をさせるため最優先で弾く。
    - (b) は**エラーではなく警告**にする。changelog に載るのは「公式 changelog に
      エントリがある版」だけで、**docs ページはそれより細かい版に言及することがある**。
      実例: 認証ページの「GovCloud には Kiro IDE 0.9.2 以降が必要」は公式ページで
      確認できる正しい記述だが、0.9.2 は changelog に単独エントリを持たない
      （0.9 系のエントリは 0.9・0.9.40・0.9.47 のみ）。
      当初これをエラーにしたため、正しい記述を「転記ミス」と誤判定した。
      **転記ミスの疑いを知らせるが、公式で確認できるなら記述側が正しい。**
    - 日付の書式そのものは check-notation.py が見る。ここでは**内容の一致**を見る。
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-ide-docs"
LOCAL_ONLY = ("05_meta", "06_embedded-docs", "work_plans", "work_records")

CHANGELOG = f"{DOC_ROOT}/02_update/01_changelog.md"
CHANGELOG_0X = f"{DOC_ROOT}/02_update/02_changelog-0x.md"

# 目次テーブルの行（`| [1.0.242](#v1-0-242) | 2026-07-28 | ... |`）
TOC_ROW_RE = re.compile(r"^\|\s*\[(\d+\.\d+(?:\.\d+)?)\]\(#")

# 出典日の書式（公式ページの更新日）
SOURCE_DATE_RE = re.compile(
    r"(?:公式ページ更新日|公式ページ最終更新|Page updated|公式更新日)[^0-9\n]{0,4}(\d{4}-\d{2}-\d{2})"
)
# 公式ページに更新日の表示が本当に無い場合の逃げ道（明示的に書けば通す）。
# 「書けないから省略」と「書く欄が無い」を区別するために形式を決めておく。
SOURCE_DATE_ABSENT_RE = re.compile(r"公式ページ更新日:\s*未記載")

errors = []
warnings = []
notes = []


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
    return docs


def strip_fences(lines):
    out, in_fence = [], False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else ln)
    return out


def read_doc(path):
    with open(path, encoding="utf-8") as f:
        return strip_fences(f.read().splitlines())


# ------------------------------------------------------------
# changelog から正準情報を取る
# ------------------------------------------------------------
def changelog_versions():
    """(最新版, 全バージョン集合) を返す。最新版は 1.0 系目次の先頭。"""
    latest, versions = None, set()
    for path in (CHANGELOG, CHANGELOG_0X):
        if not os.path.isfile(path):
            errors.append(f"{path}: changelog がありません（正準情報を取得できない）")
            continue
        for ln in read_doc(path):
            m = TOC_ROW_RE.match(ln)
            if not m:
                continue
            versions.add(m.group(1))
            if path == CHANGELOG and latest is None:
                latest = m.group(1)
    return latest, versions


# ------------------------------------------------------------
# (d) 公式が否定している内容を肯定していないか
# ------------------------------------------------------------
# (検出パターン, なぜ誤りか, 打ち消しに必要な語)
MISLEADING = [
    (
        re.compile(r"Supervised[^。\n]{0,30}?(?:セキュリティ(?:機構|制御|機能)|安全(?:性|に)?)"
                   r"[^。\n]{0,10}?(?:です|である|として|になり|になる|を提供)"),
        "Supervised モードはセキュリティ機構ではない（公式が警告として明記）。"
        "アクセス範囲を絞るのは Permissions",
        ("ではありません", "ではない", "ではなく"),
    ),
    (
        re.compile(r"Trusted Commands[^。\n]{0,40}?(?:構造を(?:解析|理解)|複合コマンドを分割)"),
        "Trusted Commands は単純な前方一致で、コマンドの構造を解析しない",
        ("しません", "しない", "ではありません"),
    ),
    (
        re.compile(r"`?\.kiroignore`?[^。\n]{0,30}?(?:権限|アクセス制御|セキュリティ)"
                   r"[^。\n]{0,10}?(?:です|である|として)"),
        ".kiroignore はエージェントに見せないファイルの指定であって権限機構ではない",
        ("ではありません", "ではない", "ではなく", "別物"),
    ),
]

# (e) 「未確認」は何が未確認かを示す（単に「未確認」だけでは読者が判断できない）
UNCONFIRMED_CONTEXT = ("公式", "記述", "確認できません", "確認できない", "未記載",
                       "明示されて", "不明", "判断できません")


def main():
    os.chdir(repo_root())
    docs = public_docs()

    print("=== kiro-ide-docs 用語・記述整合チェック ===")
    print("")

    latest, versions = changelog_versions()
    if latest is None:
        print("❌ changelog から最新版を取得できませんでした")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    print(f"🔍 正準情報: 最新版 = {latest} / 収録バージョン = {len(versions)} 件")
    print("")

    # ---- (a) 最新版の整合 ----
    print("🔍 (a) 最新版の記述が一致するか検証中...")
    # 「最新版 = X」と**主張している**箇所だけを対象にする。
    # 「最新版のほかに 1.0.228・…」のような列挙は最新版の主張ではないため、
    # 助詞（の・より・以外・ほか）が挟まる形は除外する。
    # （当初この除外がなく、正しい旧版の列挙をエラーと誤判定した）
    LATEST_CLAIM_RE = re.compile(
        r"最新(?:バージョン|版)"
        r"(?![^0-9\n]{0,12}?(?:のほか|の他|以外|より前|より古い|を除))"
        r"[^0-9\n]{0,12}?(\d+\.\d+\.\d+)"
    )
    latest_claims = 0
    for doc in docs:
        for i, ln in enumerate(read_doc(doc)):
            for m in LATEST_CLAIM_RE.finditer(ln):
                latest_claims += 1
                if m.group(1) != latest:
                    errors.append(
                        f"{doc}:{i + 1}: (a) 最新版の記述が changelog と不一致"
                        f"（記述={m.group(1)} changelog={latest}）: {ln.strip()[:60]}"
                    )
    notes.append(f"最新版の記述 {latest_claims} 箇所を検証（正準 = {latest}）")

    # ---- (b) 版番号の実在 ----
    print("🔍 (b) 参照している版番号が changelog に存在するか検証中...")
    ver_refs = 0
    for doc in docs:
        for i, ln in enumerate(read_doc(doc)):
            # 「1.0.52 で」「1.0.116 から」のように版に言及する箇所
            for m in re.finditer(r"(?<![\w.])(1\.0\.\d+|0\.\d+\.\d+)\s*(?:で|から|以降|時点|より)", ln):
                ver_refs += 1
                if m.group(1) not in versions:
                    warnings.append(
                        f"{doc}:{i + 1}: (b) changelog に無い版を参照しています"
                        f"（{m.group(1)}）: {ln.strip()[:60]}"
                        " → 転記ミスでなく公式 docs ページ由来の版なら正しい記述です"
                        "（changelog は「エントリのある版」しか持たない）"
                    )
    notes.append(f"版番号への言及 {ver_refs} 箇所を検証")

    # ---- (c) 出典日の明記 ----
    print("🔍 (c) 出典日（公式ページの更新日）の明記を検証中...")
    # 一次情報の更新日は「公式がいつ時点の記述か」を読者に示すため、
    # リファレンスと機能ページには必須とする。
    need_source_date = sorted(
        glob.glob(f"{DOC_ROOT}/04_reference/[0-9][0-9]_*.md")
        + glob.glob(f"{DOC_ROOT}/01_features/[0-9][0-9]_*.md")
    )
    missing_date = []
    for path in need_source_date:
        body = "\n".join(read_doc(path))
        if not SOURCE_DATE_RE.search(body) and not SOURCE_DATE_ABSENT_RE.search(body):
            missing_date.append(path)
    # 出典日は**エラー**にする。公式ページ間の食い違いを「更新日が新しい方を正」で
    # 解決する方針（F-14）を取っているため、更新日が無いページは方針を適用できない。
    # 公式に更新日の表示が無い場合は「公式ページ更新日: 未記載」と明示的に書く。
    for p in missing_date:
        errors.append(
            f"(c) 出典日（公式ページ更新日: YYYY-MM-DD）がありません: {p}"
            "（公式に更新日の表示が無い場合は『公式ページ更新日: 未記載』と明記する）"
        )
    notes.append(f"出典日を必須とするページ {len(need_source_date)} 件を検証"
                 f"（うち未記載 {len(missing_date)} 件）")

    # ---- (d) 誤解を招く断定 ----
    print("🔍 (d) 公式が否定している内容を肯定していないか検証中...")
    for doc in docs:
        for i, ln in enumerate(read_doc(doc)):
            for pattern, why, negations in MISLEADING:
                m = pattern.search(ln)
                if not m:
                    continue
                # 同じ行で打ち消していれば正しい記述
                if any(neg in ln for neg in negations):
                    continue
                errors.append(
                    f"{doc}:{i + 1}: (d) 誤解を招く断定: '{m.group(0)[:40]}'"
                    f"（{why}）"
                )

    # ---- (e) 「未確認」の作法 ----
    print("🔍 (e) 「未確認」に説明が伴っているか検証中...")
    unconfirmed = 0
    for doc in docs:
        lines = read_doc(doc)
        for i, ln in enumerate(lines):
            if "未確認" not in ln:
                continue
            unconfirmed += 1
            # 前後1行を含めて、何が未確認かの手がかりがあるか見る
            ctx = " ".join(lines[max(0, i - 1):i + 2])
            if not any(k in ctx for k in UNCONFIRMED_CONTEXT):
                warnings.append(
                    f"{doc}:{i + 1}: (e) 「未確認」に何が未確認かの説明が見当たりません"
                    f": {ln.strip()[:60]}"
                )
    notes.append(f"「未確認」の記述 {unconfirmed} 箇所を検証")

    # ---- (f) 食い違い注記の対応 ----
    print("🔍 (f) 公式ページ間の食い違い（F-14）の注記を検証中...")
    # hooks/types の食い違いは 01_features/05_hooks.md と
    # 02_update/03_migration-to-1.0.md の両方に書いてある。
    # 片方だけ消えると、もう片方を読んだ読者が裏取りできなくなる。
    pair = [f"{DOC_ROOT}/01_features/05_hooks.md",
            f"{DOC_ROOT}/02_update/03_migration-to-1.0.md"]
    have = [p for p in pair if os.path.isfile(p)
            and re.search(r"docs/hooks/types|types ページ", "\n".join(read_doc(p)))]
    # 片方だけ残る状態は「もう片方の読者が裏取りできない」＝方針の劣化なのでエラー。
    # 両方から消えている場合は、公式の食い違いが解消したと判断して通す
    # （そのときは意図的に両方から消す運用になる）。
    if len(have) == 1:
        errors.append(
            f"(f) 公式ページ間の食い違い（`docs/hooks/types` が 0.x のトリガー名のまま）の注記が "
            f"{have[0]} にしかありません。対になる {[p for p in pair if p not in have][0]} "
            "からも辿れる状態を維持してください"
            "（公式が更新されて食い違いが解消したら、両方から消すのが正しい対応です）"
        )

    # ---- 結果 ----
    print("")
    print("=== チェック結果 ===")
    print(f"走査した公開 Markdown: {len(docs)} 件")
    for n in notes:
        print(f"   - {n}")
    print("")

    if warnings:
        print(f"⚠️  警告 {len(warnings)} 件（エラーではないが確認推奨）:")
        for w in warnings:
            print(f"   - {w}")
        print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 用語・記述整合チェックに失敗しました")
        sys.exit(1)

    print("✅ 用語・記述の整合に問題はありません")
    sys.exit(0)


if __name__ == "__main__":
    main()
