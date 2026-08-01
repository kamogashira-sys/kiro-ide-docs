# Makefile - kiro-ide-docs 検証ツール一括実行
#
# 使用方法:
#   make                        # ヘルプを表示
#   make check-kiro-ide-quick   # 高速チェック（ネットワーク不要。コミット前に実行）
#   make check-kiro-ide-ignore  # 公開範囲チェック（コミット前に必須・exit 0 必須）
#
# 注意（Phase 2a 時点）:
#   本 Makefile は暫定版です。`check-kiro-ide-all` と URL 到達性・数値整合・用語整合の
#   ターゲットは Phase 3（検証体制の完成）で追加します。現時点で定義済みのターゲットのみが
#   実行可能です。

.DEFAULT_GOAL := help

.PHONY: help \
        check-kiro-ide-quick check-kiro-ide-ignore \
        check-kiro-ide-links check-kiro-ide-changelog check-kiro-ide-structure \
        check-kiro-ide-coverage \
        extract-kiro-ide-changelog

SCRIPTS := ./scripts/kiro-ide-docs

# 一次情報（取得済み changelog HTML）の置き場。網羅性チェックで使う。
# 既定はリポジトリ内のスナップショット置き場（ローカル管理・.gitignore 対象）。
# 未指定・不在ならチェックはスキップする（ネットワークに依存させない）。
# スナップショットを持たない環境（CI・クローン直後）ではスキップされ、
# 「exit 0 = 網羅性を検証した」ではないことに注意する。
HTML_DIR ?= kiro-ide-docs/06_embedded-docs

# ------------------------------------------------------------
# ヘルプ
# ------------------------------------------------------------
help:
	@echo "=== kiro-ide-docs 検証ツール ==="
	@echo ""
	@echo "まとめて実行:"
	@echo "  make check-kiro-ide-quick      # 高速チェック（links / changelog / structure / coverage）"
	@echo "  make check-kiro-ide-ignore     # 公開範囲チェック（コミット前に必須）"
	@echo ""
	@echo "個別に実行:"
	@echo "  make check-kiro-ide-links      # 内部リンク実在＋アンカー＋kiro.dev URL 書式"
	@echo "  make check-kiro-ide-changelog  # changelog の構造・日付・記述粒度（D9）"
	@echo "  make check-kiro-ide-structure  # ディレクトリ構成・H1・公開境界・CLI リンク"
	@echo "  make check-kiro-ide-coverage   # 一次情報との突き合わせ（版・日付・説明の転記漏れ）"
	@echo "                                 #   HTML_DIR=<dir> で一次情報の場所を指定（既定 $(HTML_DIR)）"
	@echo ""
	@echo "保守用:"
	@echo "  make extract-kiro-ide-changelog FILES=\"<html...>\"  # 公式 changelog HTML から一次情報を抽出"
	@echo ""
	@echo "Phase 3 で追加予定: check-kiro-ide-all / -urls / -counts / -consistency / -freshness"

# ------------------------------------------------------------
# まとめて実行
# ------------------------------------------------------------
# 高速チェック（ネットワーク不要）。セクション完了ごと・コミット前に実行する。
# 網羅性チェックは一次情報 HTML があるときだけ実行される（無ければスキップして成功扱い）。
check-kiro-ide-quick: check-kiro-ide-links check-kiro-ide-changelog check-kiro-ide-structure \
                      check-kiro-ide-coverage
	@echo ""
	@echo "✅ kiro-ide-docs 高速チェックが完了しました"

# 公開範囲チェック。ローカル管理対象が GitHub に出ないことを機械確認する。
# 各コミット前に実行し exit 0 を必須とする（作業計画書 Phase 1-5 / 4-1 / 5-3）。
check-kiro-ide-ignore:
	@$(SCRIPTS)/check-ignore.sh

# ------------------------------------------------------------
# 個別ターゲット
# ------------------------------------------------------------
# 内部リンクの実在・アンカーの実在・kiro.dev URL の書式
# （changelog は末尾スラッシュ必須／CLI 版リンクは docs/cli/v3/ を指すこと）
check-kiro-ide-links:
	@$(SCRIPTS)/check-links.py --check-anchors

# changelog の構造（版番号書式・降順・アンカー整合・ISO 日付・D9 の記述粒度）
check-kiro-ide-changelog:
	@$(SCRIPTS)/check-changelog.sh

# ディレクトリ構成（公開5セクション・README の有無・H1 見出し・04_reference の軸・
# ローカル管理領域へのリンク禁止）
check-kiro-ide-structure:
	@$(SCRIPTS)/check-structure.py

# changelog を一次情報と突き合わせる（版の網羅性・日付の一致・公式の説明の転記漏れ）。
# 一次情報 HTML が無い環境（CI 等）ではスキップして成功扱いにする。
check-kiro-ide-coverage:
	@if [ -d "$(HTML_DIR)" ] && ls "$(HTML_DIR)"/*.html >/dev/null 2>&1; then \
	    $(SCRIPTS)/check-coverage.py --html-dir "$(HTML_DIR)"; \
	else \
	    echo "⚠️  網羅性チェックをスキップ: $(HTML_DIR) に一次情報 HTML がありません"; \
	    echo "   → これは「検証して合格した」ではありません（未検証です）"; \
	    echo "   取得手順は 05_meta/10_version-update-guide.md を参照"; \
	fi

# ------------------------------------------------------------
# 保守用（取得済み HTML を対象にするため check-*-quick には含めない）
# ------------------------------------------------------------
# 公式 changelog ページの HTML から本文構造（版番号・日付・Improvements/Fixes）を抽出する。
# 対象は FILES で渡す。例: make extract-kiro-ide-changelog FILES="/tmp/1-0.html" ARGS=--text
# HTML の取得手順は 05_meta/10_version-update-guide.md を参照（末尾スラッシュと UA が必須）。
FILES ?=
ARGS ?=
extract-kiro-ide-changelog:
	@if [ -z "$(FILES)" ]; then \
	    echo "使い方: make extract-kiro-ide-changelog FILES=\"<html...>\" [ARGS=--text]"; \
	    exit 2; \
	fi
	@$(SCRIPTS)/extract-changelog.py $(ARGS) $(FILES)
