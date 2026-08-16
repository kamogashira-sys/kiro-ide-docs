#!/bin/bash
# check-urls.sh - kiro-ide-docs 外部 URL の到達性チェック
#
# 使用方法:
#   ./scripts/kiro-ide-docs/check-urls.sh              # 抽出した全 URL をチェック
#   ./scripts/kiro-ide-docs/check-urls.sh --dry-run    # 抽出のみ（ネットワークを使わない）
#   ./scripts/kiro-ide-docs/check-urls.sh --sample 10  # 先頭 N 件のみ
#   ./scripts/kiro-ide-docs/check-urls.sh --important  # 重要 URL のみを確実に確認
#
# 目的:
#   公式サイトの改廃でリンクが切れたことを検知する。本サイトは GitHub 直読みのため
#   リダイレクトを自前で用意できず、リンク切れがそのまま読者に見える。
#
# ⚠️ 実測にもとづく取得の作法（F-15。ここを外すと誤って「リンク切れ」と判定する）:
#   1. **末尾スラッシュなしは 301**（404 ではない）。`-L` でリダイレクトを追う
#   2. **User-Agent を空文字にすると 403**（CloudFront が Request blocked. を返す）。
#      curl の既定 UA なら 200 だが、確実性のため `-A` を明示する
#   3. `/docs/enterprise/` の索引ページは **404**（配下22ページは実在する）。
#      「404 だからその領域が無い」ではないので重要 URL リストに入れない（M-B）
#   4. `/docs/editor/` も 404、`/docs/getting-started/` は `/docs/` へリダイレクト
#
# 除外するもの:
#   - ローカル管理領域（05_meta / 06_embedded-docs / work_plans / work_records）
#   - 説明用のプレースホルダ（example.com・updates.example.com・endpoint.to.connect.to 等）
#   - 本サイト自身の GitHub URL（Phase 4 の公開まで存在しないため）
#
# 注意:
#   本チェックは**外部サイトの状態に依存する**ため、レート制限や一時障害で失敗し得る。
#   `check-kiro-ide-all` には含めず、CI では push / nightly / 手動でのみ実行する。

set -euo pipefail

MODE="all"
SAMPLE_SIZE=0
case "${1:-}" in
    --dry-run)   MODE="dry-run" ;;
    --sample)    MODE="sample"; SAMPLE_SIZE="${2:-10}" ;;
    --important) MODE="important" ;;
    "")          ;;
    *)           echo "不明な引数: $1"; exit 2 ;;
esac

cd "$(dirname "$0")/../.."

# 実測にもとづく共通オプション（-L と -A は必須。理由は冒頭のコメント参照）
UA="Mozilla/5.0 (compatible; kiro-ide-docs-link-check)"
CURL_OPTS=(-s -o /dev/null -L -A "$UA" --max-time 20 --retry 2 --retry-delay 2)

echo "=== kiro-ide-docs 外部 URL 到達性チェック（mode=$MODE） ==="
echo ""

TEMP_URLS="$(mktemp -t kiro-ide-urls.XXXXXX)"
trap 'rm -f "$TEMP_URLS" "$TEMP_URLS".s' EXIT

check_one() {
    # $1=URL -> HTTP ステータスを標準出力へ
    local url="$1" status
    # HEAD を拒否するサーバがあるため GET で本文を破棄する（-o /dev/null）
    status=$(curl "${CURL_OPTS[@]}" -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    # --retry があると試行ごとに %{http_code} が出力され "000000" のように連結される。
    # 判定と表示に使うのは**最後の試行**なので末尾3桁を取る。
    echo "${status: -3}"
}

# 移転スタブ検出（2026-08 の公式サイト再構成で判明）:
# 旧 URL 体系のページは HTTP 200 を返すが実体を持たない「移転案内スタブ」になっている場合がある。
# スタブは HTTP リダイレクトを一切行わない（-L でも遷移しない。redirect_url が空のまま 200 を返す）。
# 本文に "moved to <a href="..."" が含まれるかどうかでのみ判定できる。
# $1=URL -> 移転先パスを標準出力へ（移転スタブでなければ空文字）
check_moved_stub() {
    local url="$1" body target
    body=$(curl -s -A "$UA" --max-time 15 --retry 2 --retry-delay 1 "$url" 2>/dev/null || echo "")
    target=$(printf '%s' "$body" | grep -oE 'moved to <a href="[^"]+"' | head -1 | sed -E 's/.*href="([^"]+)".*/\1/')
    echo "$target"
}

# ------------------------------------------------------------
# important モード: 構成の根拠になっている URL を確実に確認する
# ------------------------------------------------------------
# 全 URL チェックが外部要因で落ちたときでも、「サイト構成の前提が崩れていないか」
# だけは切り分けられるようにする。索引が 404 のページ（enterprise / editor）は
# 意図的に入れない（M-B・実測）。
if [ "$MODE" = "important" ]; then
    IMPORTANT_URLS=(
        # changelog（系列ページと専用ページ。末尾スラッシュ必須）
        "https://kiro.dev/changelog/ide/"
        "https://kiro.dev/changelog/ide/1-0/"
        "https://kiro.dev/changelog/ide/1-0-242/"
        "https://kiro.dev/changelog/ide/0-12/"
        "https://kiro.dev/changelog/ide/0-1/"
        # 情報源
        "https://kiro.dev/changelog/feed.atom"
        "https://kiro.dev/llms.txt"
        "https://kiro.dev/sitemap.xml"
        # IDE の主要 docs（本サイトの機能ページの一次情報）
        "https://kiro.dev/docs/"
        "https://kiro.dev/docs/specs/"
        "https://kiro.dev/docs/ide/chat/"
        "https://kiro.dev/docs/permissions/"
        "https://kiro.dev/docs/ide/chat/autopilot/"
        "https://kiro.dev/docs/hooks/"
        "https://kiro.dev/docs/steering/"
        "https://kiro.dev/docs/custom-agents/"
        "https://kiro.dev/docs/mcp/"
        "https://kiro.dev/docs/ide/experimental/focus-mode/"
        # 新規機能（Powers・Cloud Sessions・Agent Skills）の一次情報。
        # 本サイトの機能ページから公式へ送る導線なので、切れたら読者が行き止まりになる
        "https://kiro.dev/docs/powers/"
        "https://kiro.dev/docs/cloud-sessions/"
        "https://kiro.dev/docs/skills/"
        "https://kiro.dev/docs/ide/editor/interface/"
        "https://kiro.dev/docs/ide/editor/keyboard-shortcuts/"
        "https://kiro.dev/docs/models/"
        # 導入・組織
        "https://kiro.dev/downloads/"
        "https://kiro.dev/docs/getting-started/authentication/"
        "https://kiro.dev/docs/enterprise/managed-updates/"
        "https://kiro.dev/docs/privacy-and-security/firewalls/"
        "https://kiro.dev/docs/privacy-and-security/data-protection/"
        # CLI 版へのリンクは v3 を指す規約（F-7）。リンク先の実在を確認する
        "https://kiro.dev/docs/cli/v3/permissions/"
        "https://kiro.dev/docs/cli/v3/agent-config/"
        "https://kiro.dev/docs/cli/v3/hooks-migration/"
    )
    errors=0
    for url in "${IMPORTANT_URLS[@]}"; do
        status=$(check_one "$url")
        if [[ ! "$status" =~ ^[23] ]]; then
            echo "❌ $status  $url"
            errors=$((errors + 1))
            continue
        fi
        moved_to=$(check_moved_stub "$url")
        if [ -n "$moved_to" ]; then
            echo "❌ $status  $url  → 移転スタブ（実体なし）。移転先: $moved_to"
            errors=$((errors + 1))
        else
            echo "✅ $status  $url"
        fi
    done
    echo ""
    echo "=== チェック結果 ==="
    echo "重要 URL ${#IMPORTANT_URLS[@]} 件 / エラー $errors 件"
    if [ "$errors" -gt 0 ]; then
        echo ""
        echo "❌ 重要 URL チェックに失敗しました"
        echo "   → 一時障害の可能性があります。再実行しても失敗するなら公式サイトの改廃を確認してください"
        exit 1
    fi
    echo ""
    echo "✅ すべての重要 URL が有効です"
    exit 0
fi

# ------------------------------------------------------------
# URL 抽出
# ------------------------------------------------------------
echo "🔍 URL を抽出中..."
find kiro-ide-docs README.md -name "*.md" -type f \
    -not -path "*/06_embedded-docs/*" \
    -not -path "*/05_meta/*" \
    -not -path "*/work_plans/*" \
    -not -path "*/work_records/*" \
    -exec grep -hoP 'https?://[^\s\)\]>"'"'"'`]+' {} \; \
    | sed 's/[,;:.、。」）]*$//' \
    | grep -vE '(localhost|127\.0\.0\.1|0\.0\.0\.0)' \
    | grep -vE 'example\.(com|org|net)' \
    | grep -vE '(endpoint\.to\.connect\.to|start\.us-gov-home\.awsapps\.com)' \
    | grep -vE '(XXXX|\{|\}|\$|<|>)' \
    | grep -vE 'kamogashira-sys/kiro-ide-docs' \
    | grep -E '^https?://[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}' \
    | sort -u > "$TEMP_URLS"

total=$(wc -l < "$TEMP_URLS")
echo "   抽出した URL 数: $total"
echo ""
echo "   除外したもの: プレースホルダ（example.com 等）・GovCloud の例示 Start URL・"
echo "                 本サイト自身の GitHub URL（Phase 4 の公開まで存在しない）"
echo ""

if [ "$total" -eq 0 ]; then
    echo "❌ URL が1件も抽出できませんでした（抽出パターンが壊れている可能性）"
    exit 1
fi

if [ "$MODE" = "dry-run" ]; then
    echo "=== ドライラン（抽出のみ・ネットワークは使わない） ==="
    sed 's/^/  /' "$TEMP_URLS"
    echo ""
    echo "✅ URL 抽出が完了しました（到達性は未検証）"
    exit 0
fi

if [ "$MODE" = "sample" ]; then
    head -n "$SAMPLE_SIZE" "$TEMP_URLS" > "$TEMP_URLS".s && mv "$TEMP_URLS".s "$TEMP_URLS"
    total=$(wc -l < "$TEMP_URLS")
    echo "=== サンプルモード（先頭 $SAMPLE_SIZE 件） ==="
    echo "   ⚠️  これは全件検証ではありません"
    echo ""
fi

# ------------------------------------------------------------
# 到達性チェック
# ------------------------------------------------------------
errors=0
checked=0
stub_checked=0
echo "🔍 到達性をチェック中..."
while IFS= read -r url; do
    [ -z "$url" ] && continue
    checked=$((checked + 1))
    [ $((checked % 20)) -eq 0 ] && echo "   進捗: $checked/$total"
    status=$(check_one "$url")
    if [[ "$status" =~ ^[23] ]]; then
        # 移転スタブ検出は kiro.dev/docs/ 配下のみ対象
        # （パフォーマンスと誤検知防止のため。q-cli-docs で確認済みの構造）
        case "$url" in
            https://kiro.dev/docs/*)
                stub_checked=$((stub_checked + 1))
                moved_to=$(check_moved_stub "$url")
                if [ -n "$moved_to" ]; then
                    echo "❌ 移転スタブ（実体なし）: $url  → 移転先: $moved_to"
                    errors=$((errors + 1))
                fi
                ;;
        esac
        continue
    elif [ "$status" = "000" ]; then
        echo "❌ 到達できません（タイムアウトまたは名前解決失敗）: $url"
        errors=$((errors + 1))
    else
        echo "❌ HTTP $status: $url"
        errors=$((errors + 1))
    fi
done < "$TEMP_URLS"

echo ""
echo "   移転スタブ判定を実施した kiro.dev/docs/ URL: $stub_checked 件"
echo ""
echo "=== チェック結果 ==="
echo "対象 $total 件 / 実施 $checked 件 / エラー $errors 件"

if [ "$errors" -gt 0 ]; then
    echo ""
    echo "❌ URL チェックに失敗しました"
    echo "   → 403 が出た場合は UA が空になっていないか、301 が追えていないかを確認してください"
    echo "   → 公式サイトの改廃なら本文の修正が必要です（05_meta/10_version-update-guide.md §5.7）"
    exit 1
fi

echo ""
echo "✅ すべての URL が到達可能です"
exit 0
