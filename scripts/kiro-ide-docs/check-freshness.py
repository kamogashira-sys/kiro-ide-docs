#!/usr/bin/env python3
"""check-freshness.py - Kiro IDE 新バージョン検知（3情報源の和集合 vs 文書）

使用方法:
    ./scripts/kiro-ide-docs/check-freshness.py
    ./scripts/kiro-ide-docs/check-freshness.py --offline   # 手元スナップショットのみで検証
    make check-kiro-ide-freshness

目的:
    公式に新バージョンが出たのに文書が追随していない状態を検知する。

⚠️ フィード単独運用は成立しない（実測）:
    **1.0.165（2026-07-16）はフィードに存在しない**（直近25件のローリング
    ウィンドウから溢れた）。フィードだけを見ていると版を取り落とす。
    そのため次の**3情報源の和集合**を取る（M-F）。

    ① フィード              … 速報。`<category term="IDE"/>` のエントリ
    ② 系列ページの埋め込み JSON … 網羅。`"patches":[{version,date}]`
    ③ sitemap               … 新しいマイナー系列・新しい専用ページの検知

    どれも単独では欠陥がある:
      ① 取り落とし・同一ビルドの重複配信
      ② 新系列が新設されるとその URL を知らないと取得できない → ③ で補う
      ③ 日付が取れない。パッチは系列ページ内なので URL に現れない

exit コード:
    0 … 文書が追随している（または情報源を取得できず手動確認を促した）
    1 … 未掲載の版がある／情報源の構造が変わった疑いがある

設計メモ:
    - **外部依存のため `check-kiro-ide-all` と CI（PR）には含めない**手動ターゲット。
      ネットワーク障害で CI が赤くなるのを避ける（q-cli-docs と同運用）。
    - 「取得できなかった」と「追随できていない」を**区別**する。取得失敗は
      exit 0（fail-safe）とし、手動確認コマンドを表示する。
      ただし**取得できたのに抽出0件**なら構造変化の疑いとして exit 1（R8・注意5/6）。
    - 既知例外: **0.9.40 は URL がスラッグ**でバージョンが取れない（注意7）。
"""
import json
import re
import subprocess
import sys
import os

DOC_ROOT = "kiro-ide-docs"
CHANGELOG = f"{DOC_ROOT}/02_update/01_changelog.md"
CHANGELOG_0X = f"{DOC_ROOT}/02_update/02_changelog-0x.md"
SNAPSHOT_DIR = f"{DOC_ROOT}/06_embedded-docs"

FEED_URL = "https://kiro.dev/changelog/feed.atom"
SITEMAP_URL = "https://kiro.dev/sitemap.xml"
SERIES_URL = "https://kiro.dev/changelog/ide/{}/"

UA = "Mozilla/5.0 (compatible; kiro-ide-docs-freshness-check)"

# 目次テーブルの行（`| [1.0.242](#v1-0-242) | ... |`）
TOC_ROW_RE = re.compile(r"^\|\s*\[(\d+\.\d+(?:\.\d+)?)\]\(#")

# 既知例外: URL がスラッグでバージョンを取れないリリース（注意7）
KNOWN_SLUG_EXCEPTIONS = {
    "external-identity-provider-support-for-kiro-ide": "0.9.40",
}

# `patches` 索引を**持たない**ことが実測で確認済みの系列。
# ここに無い系列で索引が取れなくなったら、ページ構造が変わった疑いとして扱う（R8）。
# 0.1 と 0.4 はパッチが無い系列、0.2 は系列ランディングページ自体が存在しない
# （0.2 は 0-2-13 などの専用ページのみ）。
SERIES_WITHOUT_INDEX = {"0.1", "0.2", "0.4"}

warnings = []
notes = []


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def fetch(url, timeout=25):
    """URL を取得して本文を返す（失敗時は None）。

    末尾スラッシュなしは 301 なので -L で追う。UA を空にすると 403 になるため
    明示的に送る（F-15）。
    """
    try:
        out = subprocess.run(
            ["curl", "-sSL", "-A", UA, "--max-time", str(timeout),
             "--retry", "2", "--retry-delay", "2", url],
            capture_output=True, text=True, timeout=timeout + 20,
        )
        if out.returncode != 0 or not out.stdout.strip():
            return None
        return out.stdout
    except (subprocess.SubprocessError, OSError):
        return None


def version_key(v):
    return tuple(int(x) for x in v.split("."))


def canon(v):
    """バージョン表記を比較用に正規化する。

    公式は**同じリリースを2通りに書く**: 系列ランディングページの URL は
    `/changelog/ide/1-0/`（= `1.0`）だが、そのリリース自体は **`1.0.0`（GA）**
    として扱われる。文書側は公式のリリース名に従い `1.0.0` と書いている。
    正規化しないと「公式にあるのに文書に無い版: 1.0」という誤検知になる。

    末尾の `.0` を落として比較する（`1.0.0` → `1.0`）。
    実在する版で末尾が `.0` になるのは 1.0.0 だけなので、他の版には影響しない
    （`0.9.40` は `.40` であって `.0` ではない）。
    """
    while v.count(".") >= 2 and v.endswith(".0"):
        v = v[:-2]
    return v


# ------------------------------------------------------------
# 文書側
# ------------------------------------------------------------
def doc_versions():
    """文書の目次テーブルに載っている全バージョン。"""
    vers = set()
    for path in (CHANGELOG, CHANGELOG_0X):
        if not os.path.isfile(path):
            print(f"❌ {path} がありません")
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            for ln in f:
                m = TOC_ROW_RE.match(ln)
                if m:
                    vers.add(m.group(1))
    return vers


# ------------------------------------------------------------
# ① フィード
# ------------------------------------------------------------
def feed_versions(text):
    """Atom フィードの IDE エントリからバージョン集合を作る。

    IDE 判定は `<category term="IDE"/>`（リンクパターンより堅牢・注意1）。
    同一ビルドが `/1-0-242` と `/1-0#patch-1-0-242` の2エントリで配信される
    ことがあるため、バージョン文字列に正規化して集合化する（注意2）。
    """
    versions, entries = set(), 0
    for entry in re.findall(r"<entry>(.*?)</entry>", text, re.S):
        if 'term="IDE"' not in entry:
            continue
        entries += 1
        m = re.search(r'<link[^>]*href="([^"]+)"', entry)
        if not m:
            continue
        link = m.group(1)
        mv = (re.search(r"#patch-([0-9-]+)$", link)
              or re.search(r"/changelog/ide/([0-9-]+)/?$", link))
        if mv:
            versions.add(mv.group(1).replace("-", "."))
            continue
        # スラッグ URL（既知例外）
        ms = re.search(r"/changelog/ide/([a-z0-9-]+)/?$", link)
        if ms and ms.group(1) in KNOWN_SLUG_EXCEPTIONS:
            versions.add(KNOWN_SLUG_EXCEPTIONS[ms.group(1)])
    return versions, entries


# ------------------------------------------------------------
# ② 系列ページの埋め込み JSON
# ------------------------------------------------------------
def patch_index(html):
    """系列ページ埋め込みの `"patches"` 索引から (version, date) を取る。

    ⚠️ これは「Latest Patches」の**ナビゲーション索引**であり version/date しか
    持たない（F-11）。網羅性の判定にはこれを使い、記述内容の判定には
    本文ノード `<div id="patch-*">` を見る。索引に説明が無いことを
    「説明が存在しない」と読み替えてはならない。
    """
    s = html.replace('\\"', '"')
    m = re.search(r'"patches":(\[.*?\])', s)
    if not m:
        return None  # キーが無い = ページ構造変化の疑い（R8・注意6）
    try:
        return [(p["version"], p.get("date", "")) for p in json.loads(m.group(1))]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


# ------------------------------------------------------------
# ③ sitemap
# ------------------------------------------------------------
def sitemap_entries(text):
    """sitemap から /changelog/ide/ 配下の URL 末尾スラッグを集める。

    ⚠️ **ページネーション URL（`/changelog/ide/page/2/`）を除く**。
    末尾要素だけを見ると `2`・`3` をバージョンと誤読する（実測で発生した）。
    """
    slugs = set()
    for loc in re.findall(r"<loc>([^<]*changelog/ide[^<]*)</loc>", text):
        path = loc.rstrip("/")
        if re.search(r"/changelog/ide/page/\d+$", path):
            continue  # 一覧のページ送り
        slug = path.rsplit("/", 1)[-1]
        if slug and slug != "ide":
            slugs.add(slug)
    return slugs


def slug_to_version(slug):
    """`1-0-242` → `1.0.242`。スラッグ型は既知例外表を引く。"""
    if re.fullmatch(r"[0-9]+(-[0-9]+)*", slug):
        return slug.replace("-", ".")
    return KNOWN_SLUG_EXCEPTIONS.get(slug)


def main():
    os.chdir(repo_root())
    offline = "--offline" in sys.argv[1:]

    print("=== Kiro IDE 新バージョン検知（3情報源の和集合 vs 文書） ===")
    print("")

    docs = doc_versions()
    doc_latest = max(docs, key=version_key)
    print(f"🔍 文書側: {len(docs)} 版（最新 = {doc_latest}）")
    print("")

    official = set()          # 公式で確認できた版の和集合
    sources_ok = []           # 実際に取得できた情報源
    structure_error = []      # 取得できたのに抽出できなかった情報源

    # ---- ① フィード ----
    if offline:
        notes.append("① フィード: --offline のためスキップ")
    else:
        print(f"🔍 ① フィードを取得中... ({FEED_URL})")
        text = fetch(FEED_URL)
        if text is None:
            warnings.append(
                f"① フィードを取得できませんでした（ネットワークの問題）。手動確認: "
                f"curl -sS {FEED_URL} | grep -c '<entry>'"
            )
        else:
            vers, entries = feed_versions(text)
            if not vers:
                # 取得できたのに0件 = 構造変化の疑い（注意5）
                structure_error.append(
                    "① フィードから IDE エントリのバージョンを1件も抽出できませんでした。"
                    "フィードの構造が変わった疑いがあります"
                    "（`<category term=\"IDE\"/>` とリンク形式を確認してください）"
                )
            else:
                official |= vers
                sources_ok.append("①フィード")
                print(f"   IDE エントリ {entries} 件 → ユニーク {len(vers)} 版")
                print("   ⚠️ フィードは直近25件のローリングウィンドウで、"
                      "取り落としが実在します（1.0.165）")

    # ---- ② 系列ページの埋め込み JSON ----
    # 文書が持つマイナー系列を対象にする（新系列は ③ sitemap で検知する）
    series = sorted({".".join(v.split(".")[:2]) for v in docs}, key=version_key)
    print("")
    print(f"🔍 ② 系列ページの埋め込み索引を確認中...（{len(series)} 系列）")
    for s in series:
        slug = s.replace(".", "-")
        local = os.path.join(SNAPSHOT_DIR, f"{slug}.html")
        html = None
        src = ""
        if os.path.isfile(local):
            with open(local, encoding="utf-8", errors="replace") as f:
                html = f.read()
            src = "スナップショット"
        elif not offline:
            html = fetch(SERIES_URL.format(slug))
            src = "取得"
        if html is None:
            warnings.append(f"② 系列 {s} のページを取得できませんでした（{slug}.html）")
            continue
        idx = patch_index(html)
        if idx is None:
            if s in SERIES_WITHOUT_INDEX:
                # 索引を持たないことが既知の系列（実測・仕様）
                notes.append(f"② 系列 {s}: `patches` 索引なし（既知・{src}）")
            else:
                # 索引を持っていた系列で取れなくなった = ページ構造変化の疑い。
                # ここを「注記」で流すと、索引が丸ごと消えても exit 0 になり
                # 網羅性の担保を失ったことに気づけない（実装時のテストで実際に起きた）。
                structure_error.append(
                    f"② 系列 {s} から `patches` 索引を抽出できませんでした（{src}）。"
                    "ページ構造が変わった疑いがあります"
                    "（RSC ペイロード内のキー名の変更など・R8）"
                )
            continue
        official |= {v for v, _ in idx}
        official.add(s)  # 系列自体のリリース
        if "②埋め込み索引" not in sources_ok:
            sources_ok.append("②埋め込み索引")
        print(f"   {s}: パッチ索引 {len(idx)} 件（{src}）")

    # ---- ③ sitemap ----
    if offline:
        notes.append("③ sitemap: --offline のためスキップ")
    else:
        print("")
        print(f"🔍 ③ sitemap を取得中... ({SITEMAP_URL})")
        text = fetch(SITEMAP_URL)
        if text is None:
            warnings.append("③ sitemap を取得できませんでした（ネットワークの問題）")
        else:
            slugs = sitemap_entries(text)
            if not slugs:
                structure_error.append(
                    "③ sitemap から /changelog/ide/ 配下の URL を1件も抽出できませんでした。"
                    "sitemap の構造が変わった疑いがあります"
                )
            else:
                mapped = {v for v in (slug_to_version(s) for s in slugs) if v}
                unknown = sorted(s for s in slugs if slug_to_version(s) is None)
                official |= mapped
                sources_ok.append("③sitemap")
                print(f"   changelog/ide 配下 {len(slugs)} URL → 版に対応 {len(mapped)} 件")
                if unknown:
                    # スラッグ URL の新規追加は既知例外表の更新が必要
                    warnings.append(
                        f"③ sitemap にバージョンを判定できない URL があります: {unknown}"
                        "（スラッグ型のリリースなら KNOWN_SLUG_EXCEPTIONS に追加してください）"
                    )

    # ---- 判定 ----
    print("")
    print("=== チェック結果 ===")

    if structure_error:
        print(f"❌ 情報源の構造変化の疑い {len(structure_error)} 件:")
        for s in structure_error:
            print(f"   - {s}")
        print("")
        print("❌ 検知の前提が崩れています（サイト改修の可能性・R8）")
        sys.exit(1)

    if not sources_ok:
        print("⚠️  情報源を1つも取得できませんでした（未検証です）")
        for w in warnings:
            print(f"   - {w}")
        print("")
        print("   → これは「追随している」ではありません。手動で確認してください:")
        print(f"      curl -sS {FEED_URL} | grep -oP 'changelog/ide/[0-9-]+' | head")
        print("✅ 外部依存の失敗のため exit 0 とします（fail-safe）")
        sys.exit(0)

    print(f"確認できた情報源: {' / '.join(sources_ok)}")
    print(f"公式で確認できた版（和集合）: {len(official)} 件")
    print(f"文書に載っている版: {len(docs)} 件")

    for n in notes:
        print(f"   - {n}")

    # 比較は正規化した表記で行う（`1.0` と `1.0.0` を同一視する。canon() 参照）
    docs_c = {canon(v) for v in docs}
    official_c = {canon(v) for v in official}
    missing = sorted(official_c - docs_c, key=version_key)
    extra = sorted(docs_c - official_c, key=version_key)

    if warnings:
        print("")
        print(f"⚠️  警告 {len(warnings)} 件:")
        for w in warnings:
            print(f"   - {w}")

    if extra:
        # 公式で確認できないのに文書にある = フィードの取り落ちか転記ミス。
        # 取得できた情報源が一部だけなら正常なこともあるため警告にとどめる。
        print("")
        print(f"⚠️  文書にあるが今回の情報源では確認できなかった版 {len(extra)} 件:")
        print(f"     {', '.join(extra)}")
        print("     → フィードのローリングウィンドウから溢れた版なら正常です")

    if missing:
        print("")
        print(f"❌ 公式にあるのに文書に無い版 {len(missing)} 件:")
        for v in missing:
            print(f"   - {v}")
        print("")
        print("   → 手順書（05_meta/10_version-update-guide.md）の更新フローを開始してください")
        print("❌ 文書が公式に追随していません")
        sys.exit(1)

    print("")
    print("✅ 文書は公式で確認できた全バージョンを収録しています")
    sys.exit(0)


if __name__ == "__main__":
    main()
