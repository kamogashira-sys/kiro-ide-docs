# 猫でもわかるKiro IDE アップデート情報

**[Kiro IDE](https://kiro.dev/) のアップデート情報を、初心者にも分かりやすく解説するプロジェクトです。** より正確な情報発信を心がけて更新していきます。

> **姉妹サイト**: Kiro CLI 版は **[猫でもわかるkiro-cli アップデート情報（q-cli-docs）](https://github.com/kamogashira-sys/q-cli-docs)**、Kiro Web 版は **[猫でもわかるKiro Web アップデート情報（kiro-web-docs）](https://github.com/kamogashira-sys/kiro-web-docs)** をご覧ください。Kiro IDE と Kiro CLI の比較は CLI 版サイトの [Kiro IDE 版との比較](https://github.com/kamogashira-sys/q-cli-docs/blob/main/kiro-docs/09_v3/02_kiro-ide-vs-cli.md) にまとめています。

## 🧭 目的別の入口

| 状況 | 行き先 |
|------|-------|
| 🚀 **はじめて Kiro IDE を使う** | [インストール](kiro-ide-docs/03_deployment/01_installation.md) → [認証](kiro-ide-docs/03_deployment/02_authentication.md) → [機能を知る](kiro-ide-docs/01_features/) |
| ⚠️ **0.x から 1.0 に上げたら動かなくなった** | [1.0 移行ガイド](kiro-ide-docs/02_update/03_migration-to-1.0.md)（フックの形式変更・セッション移行） |
| 📖 **最新版で何が変わったか知りたい** | [アップデート情報（1.0 系）](kiro-ide-docs/02_update/01_changelog.md) |
| 📚 **機能の使い方を知りたい** | [機能詳細ガイド（10機能）](kiro-ide-docs/01_features/) |
| 🔍 **設定ファイルやショートカットを引きたい** | [リファレンス](kiro-ide-docs/04_reference/) |
| 🖥️ **VS Code から乗り換えたい** | [VS Code からの移行](kiro-ide-docs/03_deployment/03_migrating-from-vscode.md) |
| 🏢 **組織に導入したい** | [エンタープライズ配布](kiro-ide-docs/03_deployment/04_enterprise.md)・[セキュリティ](kiro-ide-docs/03_deployment/05_security.md) |

## 📚 コンテンツ

| セクション | 内容 |
|-----------|------|
| [00_information](kiro-ide-docs/00_information/) | **基本情報・公式情報源**。公式サイトの構造マップ・`llms.txt` や changelog の性質と使い分け |
| [01_features](kiro-ide-docs/01_features/) | **機能詳細ガイド（10機能）**: Specs / Chat / Permissions / Autopilot・Supervised / Hooks / Steering / Custom Agents / MCP / Agent Focus Mode / エディタ基盤 |
| [02_update](kiro-ide-docs/02_update/) | **アップデート情報**。[1.0 系](kiro-ide-docs/02_update/01_changelog.md)・[0.x 系](kiro-ide-docs/02_update/02_changelog-0x.md)の**全61バージョン**＋[1.0 移行ガイド](kiro-ide-docs/02_update/03_migration-to-1.0.md) |
| [03_deployment](kiro-ide-docs/03_deployment/) | **インストール・認証・VS Code 移行・エンタープライズ配布・セキュリティ** |
| [04_reference](kiro-ide-docs/04_reference/) | **リファレンス**: `.kiro/` ファイル仕様・キーボードショートカット（29件）・権限（capability 14種）・コンテキストプロバイダ（14種）・モデル |

**カバー範囲**: 0.1（2025-07-14）〜 **1.0.242**（2026-07-28）の**全61バージョン**。公式が説明を公開しているものは省略せず掲載しています。

## 📢 Kiro IDE とは

**Kiro IDE** は、AI エージェントを中核に据えた統合開発環境です。公式は「**An agentic IDE that helps you do your best work**」と説明しています。**VS Code の基盤である Code OSS のフォーク**として構築されているため、VS Code の拡張機能・キーバインド・設定を活かしたまま使えます。

**5つの中核機能**（公式ドキュメントトップの Core capabilities）:

| 機能 | 概要 |
|------|------|
| **[Specs](kiro-ide-docs/01_features/01_specs.md)** | 要件・設計・タスクの3成果物で機能を形式化する |
| **[Hooks](kiro-ide-docs/01_features/05_hooks.md)** | ファイル保存やツール呼び出しなどのイベントで自動化を実行する |
| **[Agentic chat](kiro-ide-docs/01_features/02_chat.md)** | 自然言語の対話で機能を構築する |
| **[Steering](kiro-ide-docs/01_features/06_steering.md)** | エージェントの振る舞いをファイルで導く |
| **[MCP](kiro-ide-docs/01_features/08_mcp.md)** | 外部のツールやサービスと連携する |

**1.0（GA・2026-06-25）で加わった主なもの**: [capability ベースの Permissions](kiro-ide-docs/01_features/03_permissions.md)・[Markdown で定義する Custom Agents](kiro-ide-docs/01_features/07_custom-agents.md)・[Agent Focus Mode](kiro-ide-docs/01_features/09_agent-focus-mode.md)（実験的）。

**公式情報源**:

| 種別 | URL |
|------|-----|
| 公式サイト | <https://kiro.dev/> |
| 公式ドキュメント | <https://kiro.dev/docs/> |
| 公式 Changelog（IDE） | <https://kiro.dev/changelog/ide/> |
| ダウンロード | <https://kiro.dev/downloads/> |
| Issue 管理 | [GitHub - kirodotdev/Kiro](https://github.com/kirodotdev/Kiro) |

> 各情報源の性質と使い分けは [00_information/02_information-sources.md](kiro-ide-docs/00_information/02_information-sources.md) にまとめています。

Kiro IDE・Kiro CLI・Kiro Web は統一されたエンジンの上に構築されており、設定ディレクトリ `~/.kiro/`（Specs / Hooks / Steering / MCP など）を共有します。ファイル仕様は [04_reference/01_kiro-directory.md](kiro-ide-docs/04_reference/01_kiro-directory.md) にまとめています。CLI 側の情報は[姉妹サイト](https://github.com/kamogashira-sys/q-cli-docs)をご覧ください。

> ⚠️ **Kiro IDE と Kiro CLI は同名の機能でも仕様が異なります。** 特に **hooks は完全な別物**です。
> 本サイトから CLI 版にリンクする場合は `docs/cli/v3/` を指す規約にしています
> （詳細は [00_information/README.md](kiro-ide-docs/00_information/README.md#-ide-と-cli-を混同しないために)）。

## 📂 ディレクトリ構成

```
kiro-ide-docs/
├── README.md         # サイト入口
├── 00_information/   # 基本情報・公式サイト構造・情報源一覧
├── 01_features/      # 機能詳細ガイド（10機能）
├── 02_update/        # アップデート情報（changelog 2本）・1.0 移行ガイド
├── 03_deployment/    # インストール・認証・VS Code 移行・エンタープライズ・セキュリティ
└── 04_reference/     # リファレンス（.kiro/ ファイル仕様・ショートカット・権限・コンテキスト・モデル）
```

## 🧭 編集方針

Kiro CLI 版サイトで実績のある方針を継承します:

1. **品質最優先**: 時間より正確性を優先する
2. **推測禁止・検証徹底**: 一次情報（公式 changelog・公式ドキュメント・Atom フィード）のみを使用し、各記述に根拠を持つ。公式に確認できない事項は「未確認」と明示し、断定して掲載しない
3. **完全性の追求**: 漏れのない網羅的な更新。**公式が説明を公開しているものは省略せず掲載する**
4. **自動検証**: リンク・数値整合・changelog 構造・**一次情報との突き合わせ**を検証スクリプト＋ CI で機械チェック
5. **公式ドキュメント間の食い違いも記載する**: 公式ページ同士で内容が異なる場合、更新日を比べて新しい方を正としたうえで、**食い違いの存在自体も明記する**（読者が公式を読んだときに混乱しないようにするため）

### 検証について

本サイトは記述の正しさを目視だけに任せず、機械チェックを併走させています。

| 検証 | 内容 |
|------|------|
| リンク・アンカーの実在 | 内部リンク全件＋`kiro.dev` の URL 書式（changelog は末尾スラッシュ必須） |
| changelog の構造 | バージョン書式・降順・ISO 日付・記述粒度 |
| ディレクトリ構成 | 公開セクション・H1 見出し・公開境界 |
| **一次情報との突き合わせ** | **公式の全バージョンが掲載されているか・日付が一致するか・説明が転記されているか** |

**文書内部の整合だけでは「公式にあるのに書き忘れた」を検出できない**ため、最後の突き合わせを別に用意しています。

## 🗂️ 作業記録の運用ルール（メンテナー向け・ローカル管理）

作業の経緯・調査結果・レビュー報告書は `work_records/` に保存し、セッションをまたいだ作業再開を可能にします。

- **保存場所**: `work_records/YYYYMMDD/`（作業日ごとのフォルダ）
- **ファイル名**: `YYYYMMDDHHMM_<内容を表すスラッグ>.md`（例: `202608010948_worklog.md`、`202608010930_..._review_report.md`）
- **必須記録（セッション終了時）**: 作業記録（worklog）に①今回やったこと ②成果物一覧 ③次のアクション ④再開時の注意事項 ⑤ディレクトリ現況 を記載する
- **作業再開時**: まず最新日付フォルダの worklog を読み、そこから計画書（`kiro-ide-docs/work_plans/` 配下のマスタープラン）へ辿る
- **公開範囲**: `work_records/` はローカル管理（`.gitignore` 対象）とし、GitHub には公開しない。作業計画書（`kiro-ide-docs/work_plans/`）・保守手順書（`kiro-ide-docs/05_meta/`）も同様
- **日付規約**: 記録内の日付は ISO 形式（YYYY-MM-DD）。相対表現（「今日」「先週」）は使わない

## 🤝 コントリビューション

誤りの指摘・改善提案は [Issues](../../issues) までお寄せください。

## 📄 ライセンス

[MIT License](LICENSE)
