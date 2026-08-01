#!/bin/bash
# check-changelog.sh - kiro-ide-docs changelog 構造チェック
#
# 使用方法:
#   ./scripts/kiro-ide-docs/check-changelog.sh
#
# 検証内容:
#   1. バージョン見出しの書式（`N.N` / `N.N.NNN`）と、目次からのアンカーの整合
#   2. リリース日の書式（ISO `YYYY-MM-DD`）と、日付が未来でないこと
#   3. 目次の表に載っている全バージョンに、本文の節が存在すること
#   4. 本文の節に載っている全バージョンが、目次の表にあること
#   5. 目次のバージョンが降順（新しい順）に並んでいること
#   6. **D9 の記述粒度**（Rev.4）:
#        - 専用ページを持つリリース（🔹）は Improvements / Fixes の節または箇条書きを持つ
#        - パッチ（▫️）は概要が空でない（**全45パッチに公式の説明が実在する**ため、
#          説明の欠落は転記漏れを意味する）
#   7. 公式 URL の書式（changelog は末尾スラッシュ必須）
#
# 前提（Kiro IDE 固有）:
#   - バージョンは `1.0.242`（3桁ビルド番号）と `0.12`（系列）の2形式
#   - 0.9.40 は URL がバージョン番号ではなくスラッグ
#     （`external-identity-provider-support-for-kiro-ide`）という既知の例外
#   - 見出しは絵文字を含むため、リンク先には明示的な HTML アンカー（`<a id="v1-0-242">`）を使う

set -euo pipefail

cd "$(dirname "$0")/../.."

FILES=(
    "kiro-ide-docs/02_update/01_changelog.md"
    "kiro-ide-docs/02_update/02_changelog-0x.md"
)

# URL がバージョン番号から導けない既知の例外
KNOWN_SLUG_URLS=("external-identity-provider-support-for-kiro-ide")

# 月名テーブルは日付が ISO に正規化済みかの検証にのみ使う。
# 公式表記（`Jul 28, 2026`）が本文に残っていたら正規化漏れ。
MONTH_NAMES='January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec'

echo "=== kiro-ide-docs changelog 構造チェック ==="
echo ""

errors=0
total_versions=0

for CHANGELOG in "${FILES[@]}"; do
    if [ ! -f "$CHANGELOG" ]; then
        echo "❌ ファイルが存在しません: $CHANGELOG"
        errors=$((errors + 1))
        continue
    fi

    echo "── $CHANGELOG"
    errors_before=$errors

    # ---- 目次の表からバージョンとアンカーを取得 ----
    # 形式: | [1.0.242](#v1-0-242) | 2026-07-28 | 🔹専用ページ | 概要 |
    toc=$(grep -oE '^\| \[[0-9]+\.[0-9]+(\.[0-9]+)?\]\(#[a-z0-9-]+\) \|[^|]*\|[^|]*\|[^|]*\|' \
        "$CHANGELOG" || true)
    toc_versions=$(echo "$toc" | grep -oE '\[[0-9]+\.[0-9]+(\.[0-9]+)?\]' \
        | tr -d '[]' || true)
    n_toc=$(echo "$toc_versions" | grep -c . || true)
    total_versions=$((total_versions + n_toc))

    if [ "$n_toc" -eq 0 ]; then
        echo "  ❌ 目次の表からバージョンを1件も抽出できませんでした（書式の変更を疑ってください）"
        errors=$((errors + 1))
        continue
    fi
    echo "  目次のバージョン数: $n_toc"

    # ---- 1. 目次のバージョンが降順か ----
    sorted=$(echo "$toc_versions" | sort -rV)
    if [ "$toc_versions" != "$sorted" ]; then
        echo "  ❌ 目次のバージョンが降順ではありません"
        echo "     実際: $(echo "$toc_versions" | tr '\n' ' ')"
        echo "     期待: $(echo "$sorted" | tr '\n' ' ')"
        errors=$((errors + 1))
    fi

    # ---- 2. 目次のアンカーが本文に存在するか ----
    body_anchors=$(grep -oE '<a id="[a-z0-9-]+"></a>' "$CHANGELOG" \
        | sed -E 's/<a id="([a-z0-9-]+)"><\/a>/\1/' | sort -u || true)
    missing_anchor=0
    while read -r line; do
        [ -z "$line" ] && continue
        anchor=$(echo "$line" | grep -oE '\(#[a-z0-9-]+\)' | tr -d '(#)')
        if ! echo "$body_anchors" | grep -qx "$anchor"; then
            ver=$(echo "$line" | grep -oE '\[[0-9.]+\]' | tr -d '[]')
            echo "  ❌ 目次の $ver のアンカー '#$anchor' に対応する本文がありません"
            missing_anchor=$((missing_anchor + 1))
        fi
    done <<< "$toc"
    [ "$missing_anchor" -gt 0 ] && errors=$((errors + 1))

    # ---- 3. 日付が ISO 形式か・未来でないか ----
    today=$(date -u +%Y-%m-%d)
    bad_dates=0
    while read -r d; do
        [ -z "$d" ] && continue
        if [[ ! "$d" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
            echo "  ❌ ISO 形式でない日付: '$d'"
            bad_dates=$((bad_dates + 1))
        elif [[ "$d" > "$today" ]]; then
            echo "  ❌ 未来の日付: '$d'（本日 $today）"
            bad_dates=$((bad_dates + 1))
        fi
    done <<< "$(grep -oE '^\*\*リリース日\*\*: .*$' "$CHANGELOG" \
        | sed -E 's/^\*\*リリース日\*\*: //' || true)"
    [ "$bad_dates" -gt 0 ] && errors=$((errors + 1))

    # ---- 4. 公式表記の日付（Jul 28, 2026）が正規化されずに残っていないか ----
    # コードブロック内（取得コマンドの例など）は除外する
    raw_dates=$(awk -v months="$MONTH_NAMES" '
        /^```/ { in_fence = !in_fence; next }
        in_fence { next }
        {
            if ($0 ~ "(" months ") [0-9]{1,2}, [0-9]{4}") print FNR ": " $0
        }
    ' "$CHANGELOG" || true)
    if [ -n "$raw_dates" ]; then
        echo "  ❌ 公式表記の日付が ISO に正規化されていません:"
        echo "$raw_dates" | sed 's/^/       /'
        errors=$((errors + 1))
    fi

    # ---- 5. 公式 changelog URL の末尾スラッシュ ----
    # `/changelog/ide/1-0` は 301 リダイレクトになるため、ページ URL は末尾スラッシュが必須（F-15）。
    # 拡張子を持つもの（feed.atom）は静的ファイルなので対象外。
    #
    # grep -o で URL を切り出すと、正常な `.../1-0-242/` からも末尾スラッシュを含まない
    # 部分文字列（`.../1-0-242`）が取れてしまい全件が誤検出になる。URL の終端は Markdown の
    # 区切り文字（`>` `)` 空白 引用符 行末）で決まるので、awk で終端まで含めて切り出す。
    bad_urls=$(awk '
        {
            s = $0
            while (match(s, /https:\/\/kiro\.dev\/changelog\/[^ \t>)"'"'"']*/)) {
                url = substr(s, RSTART, RLENGTH)
                s = substr(s, RSTART + RLENGTH)
                # 拡張子付き（feed.atom 等）は静的ファイルなので対象外
                if (url ~ /\.[A-Za-z0-9]+$/) continue
                if (url !~ /\/$/) print url
            }
        }
    ' "$CHANGELOG" | sort -u || true)
    if [ -n "$bad_urls" ]; then
        echo "  ❌ changelog の URL に末尾スラッシュがありません（301 リダイレクトになる）:"
        echo "$bad_urls" | sed 's/^/       /'
        errors=$((errors + 1))
    fi

    # ---- 6. D9 の記述粒度 ----
    # 専用ページを持つリリース（🔹 / 🎉）は改善・修正の見出しか箇条書きを持つこと。
    # パッチ（▫️）は概要が空でないこと（全45パッチに公式の説明が実在する）。
    granularity=$(awk '
        function flush() {
            if (ver == "") return
            if (kind == "dedicated" && !has_body) {
                printf "  ❌ %s（専用ページ）に改善・修正の記述がありません\n", ver
                bad++
            }
            if (kind == "patch" && !has_body) {
                printf "  ❌ %s（パッチ）に概要がありません（公式の説明の転記漏れ）\n", ver
                bad++
            }
        }
        /^#{2,3} / {
            flush()
            ver = ""; kind = ""; has_body = 0
            # 見出しから種別と版番号を判定
            if (match($0, /[0-9]+\.[0-9]+(\.[0-9]+)?/)) {
                ver = substr($0, RSTART, RLENGTH)
                if ($0 ~ /🔹/ || $0 ~ /🎉/ || $0 ~ /🔷/) kind = "dedicated"
                else if ($0 ~ /▫️/ && $0 !~ /系の/) kind = "patch"
            }
            next
        }
        # 表形式のパッチ一覧（| **0.6.29** | 2025-11-27 | 内容 |）も検証する
        /^\| \*\*[0-9]+\.[0-9]+\.[0-9]+\*\* \|/ {
            n = split($0, f, "|")
            # f[2]=版, f[3]=日付, f[4]=内容
            v = f[2]; gsub(/[ *]/, "", v)
            body = f[4]; gsub(/^[ \t]+|[ \t]+$/, "", body)
            if (body == "") {
                printf "  ❌ %s（パッチ表）の内容が空です\n", v
                bad++
            }
            next
        }
        # メタ情報行（リリース日・公式ページ）と明示アンカーは「記述」に数えない。
        # これらを本文扱いすると、説明の転記漏れを検出できなくなる。
        /^\*\*(リリース日|公式ページ)\*\*:/ { next }
        /^<a id=/ { next }
        /^[-*] / || /^#### / || /^[^|># \t]/ { if (ver != "") has_body = 1 }
        END { flush(); exit 0 }
    ' "$CHANGELOG")
    if [ -n "$granularity" ]; then
        echo "$granularity"
        errors=$((errors + 1))
    fi

    if [ "$errors" -eq "$errors_before" ]; then
        echo "  ✅ 構造 OK"
    fi
    echo ""
done

echo "=== チェック結果 ==="
echo "検証したバージョン数: $total_versions"
echo "既知の URL 例外: ${KNOWN_SLUG_URLS[*]}"
echo "エラー: $errors 件"

if [ "$errors" -gt 0 ]; then
    echo ""
    echo "❌ changelog 構造チェックに失敗しました"
    exit 1
fi

echo ""
echo "✅ changelog 構造は健全です"
exit 0
