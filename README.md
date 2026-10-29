# 猫でもわかるKiro IDE アップデート情報

**[Kiro IDE](https://kiro.dev/) のアップデート情報を、初心者にも分かりやすく解説するプロジェクトです。** より正確な情報発信を心がけて更新していきます。

> **姉妹サイト**: Kiro CLI 版は **[猫でもわかるkiro-cli アップデート情報（q-cli-docs）](https://github.com/kamogashira-sys/q-cli-docs)**、Kiro Web 版は **[猫でもわかるKiro Web アップデート情報（kiro-web-docs）](https://github.com/kamogashira-sys/kiro-web-docs)** をご覧ください。Kiro IDE と Kiro CLI の比較は CLI 版サイトの [Kiro IDE 版との比較](https://github.com/kamogashira-sys/q-cli-docs/blob/main/kiro-docs/09_v3/02_kiro-ide-vs-cli.md) にまとめています。

## 🧭 目的別の入口

| 状況 | 行き先 |
|------|-------|
| 🚀 **はじめて Kiro IDE を使う** | [インストール](kiro-ide-docs/03_deployment/01_installation.md) → [認証](kiro-ide-docs/03_deployment/02_authentication.md) → [機能を知る](kiro-ide-docs/01_features/) |
| ⚠️ **0.x から 1.0 に上げたら動かなくなった** | [1.0 移行ガイド](kiro-ide-docs/02_update/03_migration-to-1.0.md)（フックの形式変更・セッション移行） |
| 📖 **最新版で何が変わったか知りたい** | [アップデート情報（1.x 系）](kiro-ide-docs/02_update/01_changelog.md) |
| 📚 **機能の使い方を知りたい** | [機能詳細ガイド（12機能）](kiro-ide-docs/01_features/) |
| 🔍 **設定ファイルやショートカットを引きたい** | [リファレンス](kiro-ide-docs/04_reference/) |
| 🖥️ **VS Code から乗り換えたい** | [VS Code からの移行](kiro-ide-docs/03_deployment/03_migrating-from-vscode.md) |
| 🏢 **組織に導入したい** | [エンタープライズ配布](kiro-ide-docs/03_deployment/04_enterprise.md)・[セキュリティ](kiro-ide-docs/03_deployment/05_security.md) |

## 📚 コンテンツ

| セクション | 内容 |
|-----------|------|
| [00_information](kiro-ide-docs/00_information/) | **基本情報・公式情報源**。公式サイトの構造マップ・`llms.txt` や changelog の性質と使い分け |
| [01_features](kiro-ide-docs/01_features/) | **機能詳細ガイド（12機能）**: Specs / Chat / Permissions / Autopilot・Supervised / Hooks / Steering / Custom Agents / MCP / Agent Focus Mode / エディタ基盤 / Powers / Cloud Sessions |
| [02_update](kiro-ide-docs/02_update/) | **アップデート情報**。[1.x 系](kiro-ide-docs/02_update/01_changelog.md)・[0.x 系](kiro-ide-docs/02_update/02_changelog-0x.md)の**全79バージョン**＋[1.0 移行ガイド](kiro-ide-docs/02_update/03_migration-to-1.0.md) |
| [03_deployment](kiro-ide-docs/03_deployment/) | **インストール・認証・VS Code 移行・エンタープライズ配布・セキュリティ** |
| [04_reference](kiro-ide-docs/04_reference/) | **リファレンス**: `.kiro/` ファイル仕様・キーボードショートカット（30件）・権限（capability 15種）・チャットの `#` コンテキストプロバイダ（14種）・モデル・起動オプション |

**カバー範囲**: 0.1（2025-07-14）〜 **1.4.26**（2026-10-22）の**全79バージョン**。公式が説明を公開しているものは省略せず掲載しています。

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

**1.1・1.2 で加わった主なもの**: [Agent Artifacts](kiro-ide-docs/01_features/02_chat.md#12-agent-artifacts11-で追加)・Windows / Linux の[ネイティブ ARM64 版](kiro-ide-docs/03_deployment/01_installation.md#2-配布形態)（1.1）、[Workflows](kiro-ide-docs/01_features/02_chat.md#13-workflows124-で追加)・[信頼していないワークスペースの保護強化](kiro-ide-docs/04_reference/03_permissions.md#72-信頼していないワークスペースworkspace-trust)・[エンタープライズのサインイン制御](kiro-ide-docs/03_deployment/04_enterprise.md#7-サインイン制御12-以降)（1.2.4）。

**1.3・1.4 で加わった主なもの**: [ローカルコマンドのサンドボックス](kiro-ide-docs/01_features/03_permissions.md#10-ローカルコマンドのサンドボックス13-で追加)・[Markdown Review](kiro-ide-docs/01_features/10_editor.md#9-markdown-review1311-で追加)（1.3）、[Memory](kiro-ide-docs/01_features/02_chat.md#16-memory140-で追加)（1.4）、チャットでワークフローを使う頻度を選ぶ [Use workflows](kiro-ide-docs/01_features/02_chat.md#138-use-workflows1426-で追加)（1.4.26）。

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

## 🤝 コントリビューション

誤りの指摘・改善提案は [Issues](../../issues) までお寄せください。

## 📄 ライセンス

[MIT License](LICENSE)
