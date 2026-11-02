# kiro-ide-docs 作業規約（エージェント向け）

## 適用範囲

本ファイルは、リポジトリ `kamogashira-sys/kiro-ide-docs`（猫でもわかるKiro IDE アップデート情報。Kiro IDE の非公式日本語解説サイト）での作業にだけ適用します。成果物は公開されます。適用範囲の正本は [.github/UPDATE_GUIDE.md](.github/UPDATE_GUIDE.md) §0 です。

## 品質優先

- 一次情報（`kiro.dev` の changelog と docs）で確認できたことだけを書く。確認できないことは「未確認」と書く
- 速さより正確さを優先し、検証工程を省略しない
- 推測表現（おそらく・たぶん・一般的に・通常・最低〜以上）を使わない
- Kiro IDE と Kiro CLI を混同しない。CLI 版へのリンクは `docs/cli/v3/` を指す
- 公式ドキュメント間の食い違いは、更新日の新しい方を正とし、食い違いの存在も本文に書く
- 取得日（いつ取得したか）を公開文書に書かない

## 版更新（Kiro IDE の新しい版への追随）

- 版更新は `site-update` スキル（`.kiro/skills/site-update/SKILL.md`）と、手順書 [.github/UPDATE_GUIDE.md](.github/UPDATE_GUIDE.md) に従う
- 完了条件は `make check-kiro-ide-cloud` の exit 0（手順書 §14。coverage の「一次情報 N / 文書 N」を PR 本文に転記する）
- 作業は feature branch で行い、PR を作る。PR 本文は手順書 §15.1 の4節で書く

## 禁止事項

手順書 §13 が正本です。主なもの:

- main への直接 push、タグの作成、Release の公開
- `.gitignore` とローカル管理領域（`kiro-ide-docs/work_plans/`・`kiro-ide-docs/05_meta/`・`kiro-ide-docs/06_embedded-docs/`・`work_records/`）の変更
- 版更新 PR での `.github/workflows/`・`.kiro/skills/`・`AGENTS.md`・`Makefile`・検査スクリプトの判定ロジックの変更（変えてよい値は手順書 §16）
- 正準値（機能数・ショートカット数・capability 数・コンテキストプロバイダ数）の根拠のない変更

## コミット前の順序

1. 対象ファイルを名前で指定して `git add`（`git add .` は使わない）
2. `make check-kiro-ide-ignore`（exit 0）
3. `make fetch-kiro-ide-primary && make check-kiro-ide-all HTML_DIR=/tmp/kiro-ide-primary`（exit 0。スナップショットを更新しない。手順書 §11.3）
4. コミット（形式は `<type>: <subject>`、本文の末尾に `出典:`。[.github/WORKFLOW.md](.github/WORKFLOW.md) の「7⃣ コミット」）
