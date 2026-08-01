# Makefile - kiro-ide-docs 検証ツール一括実行
#
# 使用方法:
#   make                        # ヘルプを表示
#   make check-kiro-ide-quick   # 高速チェック（ネットワーク不要。コミット前に実行）
#   make check-kiro-ide-all     # 全チェック（ネットワーク不要のもの全部）
#   make check-kiro-ide-ignore  # 公開範囲チェック（コミット前に必須・exit 0 必須）
#
# ⚠️ 「exit 0」は「検証して合格した」を必ずしも意味しません:
#   - 網羅性チェックは一次情報 HTML が無いとスキップして成功扱いになります
#     （クローン直後・CI では未検証。出力に警告を表示します）
#   - 外部依存のターゲット（-urls / -freshness）は all に含まれません
#   検証スクリプトを新規作成・改修したときは、意図的に文書を壊して検出されることを
#   確認してください（ネガティブテスト）。手順は 05_meta/10_version-update-guide.md §11.4。

.DEFAULT_GOAL := help

.PHONY: help \
        check-kiro-ide-all check-kiro-ide-quick check-kiro-ide-ignore \
        check-kiro-ide-links check-kiro-ide-changelog check-kiro-ide-structure \
        check-kiro-ide-coverage check-kiro-ide-counts check-kiro-ide-notation \
        check-kiro-ide-consistency check-kiro-ide-urls check-kiro-ide-urls-important \
        check-kiro-ide-freshness \
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
	@echo "  make check-kiro-ide-all        # 全チェック（ネットワーク不要のもの全部）"
	@echo "  make check-kiro-ide-quick      # 高速チェック（構造とリンクのみ。執筆中の確認用）"
	@echo "  make check-kiro-ide-ignore     # 公開範囲チェック（コミット前に必須）"
	@echo ""
	@echo "個別に実行（ネットワーク不要）:"
	@echo "  make check-kiro-ide-links      # 内部リンク実在＋アンカー＋kiro.dev URL 書式"
	@echo "  make check-kiro-ide-changelog  # changelog の構造・日付・記述粒度（D9）"
	@echo "  make check-kiro-ide-structure  # ディレクトリ構成・H1・公開境界・CLI リンク"
	@echo "  make check-kiro-ide-coverage   # 一次情報との突き合わせ（版・日付・説明の転記漏れ）"
	@echo "                                 #   HTML_DIR=<dir> で一次情報の場所を指定（既定 $(HTML_DIR)）"
	@echo "  make check-kiro-ide-counts     # 正準値（機能数・ショートカット数）の水平展開"
	@echo "  make check-kiro-ide-notation   # 表記規約（CLI 混入・製品名・日付・autolink）"
	@echo "  make check-kiro-ide-consistency # 用語・記述整合（最新版・出典日・誤解を招く断定）"
	@echo ""
	@echo "個別に実行（★外部サイトに依存。all には含めない）:"
	@echo "  make check-kiro-ide-urls           # 外部 URL の到達性（全件）"
	@echo "  make check-kiro-ide-urls-important # 重要 URL のみ（切り分け用）"
	@echo "  make check-kiro-ide-freshness      # 新バージョン検知（3情報源の和集合）"
	@echo ""
	@echo "保守用:"
	@echo "  make extract-kiro-ide-changelog FILES=\"<html...>\"  # 公式 changelog HTML から一次情報を抽出"

# ------------------------------------------------------------
# まとめて実行
# ------------------------------------------------------------
# 全チェック。**外部サイトに依存するものは含めない**（-urls / -freshness）。
# ネットワーク障害やレート制限で CI が赤くなるのを避けるため、それらは
# push / nightly / 手動でのみ実行する（q-cli-docs と同じ運用）。
# G3（公開判定）ではこのターゲットの exit 0 を条件とする。
check-kiro-ide-all: check-kiro-ide-links check-kiro-ide-changelog check-kiro-ide-structure \
                    check-kiro-ide-coverage check-kiro-ide-counts check-kiro-ide-notation \
                    check-kiro-ide-consistency
	@echo ""
	@echo "✅ kiro-ide-docs 全チェックが完了しました"
	@echo "   （外部 URL の到達性と新バージョン検知は別ターゲットです:"
	@echo "     make check-kiro-ide-urls / make check-kiro-ide-freshness）"

# 高速チェック。執筆中に繰り返し回す用（構造とリンクだけを見る）。
# コミット前は check-kiro-ide-all を使う。
check-kiro-ide-quick: check-kiro-ide-links check-kiro-ide-structure
	@echo ""
	@echo "✅ kiro-ide-docs 高速チェックが完了しました"
	@echo "   （これは全チェックではありません。コミット前に make check-kiro-ide-all を実行してください）"

# 公開範囲チェック。ローカル管理対象が GitHub に出ないことを機械確認する。
# 各コミット前に実行し exit 0 を必須とする（作業計画書 Phase 1-5 / 4-1 / 5-3）。
check-kiro-ide-ignore:
	@$(SCRIPTS)/check-ignore.sh

# ------------------------------------------------------------
# 個別ターゲット（ネットワーク不要）
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

# 正準値（D12 の2本柱: 機能数・ショートカット数）を表の実体から数え、
# 文書中の件数記述と突き合わせる。予備の capability 数・プロバイダ数も検証する。
check-kiro-ide-counts:
	@$(SCRIPTS)/check-counts.py

# 表記規約（CLI コマンドの混入・製品名の揺れ・v プレフィックス・非 ISO 日付・
# 取得日の混入・裸 URL 直後の全角文字による autolink 事故）
check-kiro-ide-notation:
	@$(SCRIPTS)/check-notation.py

# 用語・記述整合（最新版の水平展開漏れ・出典日の欠落・公式が否定している内容の断定・
# 公式ページ間の食い違い注記の片側欠落）
check-kiro-ide-consistency:
	@$(SCRIPTS)/check-consistency.py

# ------------------------------------------------------------
# 個別ターゲット（★外部サイトに依存。all / CI（PR）には含めない）
# ------------------------------------------------------------
# 外部 URL の到達性。レート制限や一時障害で失敗し得るため独立ターゲットにする。
# 末尾スラッシュなしは 301・UA を空にすると 403（F-15）。詳細はスクリプト冒頭を参照。
check-kiro-ide-urls:
	@$(SCRIPTS)/check-urls.sh

# 重要 URL のみ。全件チェックが外部要因で落ちたときの切り分けに使う。
check-kiro-ide-urls-important:
	@$(SCRIPTS)/check-urls.sh --important

# 新バージョン検知（3情報源の和集合: フィード／系列ページの埋め込み索引／sitemap）。
# ⚠️ フィード単独では版を取り落とす（1.0.165 の実例）ため和集合が必須（M-F）。
check-kiro-ide-freshness:
	@$(SCRIPTS)/check-freshness.py

# ------------------------------------------------------------
# 保守用（取得済み HTML を対象にするため check-*-all には含めない）
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
