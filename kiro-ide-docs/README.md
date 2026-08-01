# 猫でもわかるKiro IDE アップデート情報

**[Kiro IDE](https://kiro.dev/) のアップデート情報・機能・リファレンスを、初心者にも分かりやすく解説する日本語ドキュメントです。**

> **姉妹サイト**: Kiro CLI 版は **[猫でもわかるkiro-cli アップデート情報（q-cli-docs）](https://github.com/kamogashira-sys/q-cli-docs)** をご覧ください。

---

## 🧭 目的別の入口

| 状況 | 行き先 |
|------|-------|
| 🚀 **はじめて Kiro IDE を使う** | [インストール・環境構築](03_deployment/) → [機能詳細ガイド](01_features/) |
| ⚠️ **0.x から 1.0 に上げたら動かなくなった** | [1.0 移行ガイド](02_update/03_migration-to-1.0.md)（フックの形式変更・セッション移行） |
| 📖 **最新版で何が変わったか知りたい** | [アップデート情報（1.0 系）](02_update/01_changelog.md) |
| 📚 **機能の使い方を知りたい** | [機能詳細ガイド](01_features/) |
| 🔍 **設定ファイルやショートカットを引きたい** | [リファレンス](04_reference/) |
| 🏢 **組織に導入したい** | [エンタープライズ配布・セキュリティ](03_deployment/) |

---

## 📂 セクション構成

| セクション | 内容 |
|-----------|------|
| [00_information](00_information/) | Kiro IDE の基本情報・公式サイトの構造・情報源一覧 |
| [01_features](01_features/) | **機能詳細ガイド（10機能）**: Specs / Chat / Permissions / Autopilot・Supervised / Hooks / Steering / Custom Agents / MCP / Agent Focus Mode / エディタ基盤 |
| [02_update](02_update/) | **アップデート情報**: [1.0 系](02_update/01_changelog.md)・[0.x 系](02_update/02_changelog-0x.md)・[1.0 移行ガイド](02_update/03_migration-to-1.0.md) |
| [03_deployment](03_deployment/) | インストール・認証・VS Code からの移行・エンタープライズ配布・セキュリティ |
| [04_reference](04_reference/) | **リファレンス**: `.kiro/` ファイル仕様・キーボードショートカット・権限・コンテキストプロバイダ・モデル |

---

## 📢 Kiro IDE とは

**Kiro IDE** は、**仕様駆動開発（Spec-driven development）** を中核とする AI エージェント搭載の統合開発環境です。VS Code の基盤である Code OSS のフォークとして構築されており、VS Code の拡張機能・キーバインド・設定を活かしながら、エージェントによる開発を前提とした機能群を備えます。

**5つの中核機能**（最初の公開版 0.1 から一貫）:

| 機能 | 概要 |
|------|------|
| **[Specs](01_features/01_specs.md)** | 複雑な機能について、要件・設計・タスクを構造化された成果物として形式化する |
| **[Hooks](01_features/05_hooks.md)** | ファイル保存やツール呼び出しなどのイベントで自動化を実行する |
| **[Steering](01_features/06_steering.md)** | エージェントの振る舞いをファイルで導く |
| **[Agentic chat](01_features/02_chat.md)** | チャットから機能を構築する（[Autopilot / Supervised](01_features/04_autopilot-supervised.md) の2モード） |
| **[MCP](01_features/08_mcp.md)** | Model Context Protocol で外部のツールやサービスと連携する |

**1.0（GA・2026-06-25）で加わった主なもの**: [capability ベースの Permissions](01_features/03_permissions.md)、[Markdown で定義する Custom Agents](01_features/07_custom-agents.md)、並列エージェントを指揮する [Agent Focus Mode](01_features/09_agent-focus-mode.md)。

Kiro IDE・Kiro CLI・Kiro Web は**統一されたエンジン**の上に構築され、設定ディレクトリ `~/.kiro/`（Specs / Hooks / Steering / MCP など）を共有します。ファイル仕様は [04_reference/01_kiro-directory.md](04_reference/01_kiro-directory.md) にまとめています。

> ⚠️ **同名の機能でも Kiro CLI とは仕様が異なります**（特に hooks は完全な別物）。
> 詳細は [00_information/README.md](00_information/README.md#-ide-と-cli-を混同しないために) を参照してください。

---

## 🔗 公式情報源

| 種別 | URL |
|------|-----|
| 公式サイト | <https://kiro.dev/> |
| 公式ドキュメント | <https://kiro.dev/docs/> |
| 公式 Changelog（IDE） | <https://kiro.dev/changelog/ide/> |
| ダウンロード | <https://kiro.dev/downloads/> |
| Atom フィード | <https://kiro.dev/changelog/feed.atom> |
| Issue 管理 | [GitHub - kirodotdev/Kiro](https://github.com/kirodotdev/Kiro) |

> 各情報源の性質と使い分けは [00_information/02_information-sources.md](00_information/02_information-sources.md) にまとめています。

---

## 🧭 編集方針

1. **品質最優先**: 時間より正確性を優先します
2. **推測禁止・検証徹底**: 一次情報（公式 changelog・公式ドキュメント）のみを根拠とし、各記述に出典を持ちます。公式に確認できない事項は「未確認」と明示し、断定して掲載しません
3. **完全性の追求**: 公式が公開している情報は省略せず掲載します
4. **自動検証**: リンク・数値の整合・changelog の構造を検証スクリプトと CI で機械チェックします
5. **IDE と CLI を混同しない**: 本ドキュメントは **Kiro IDE 版**の仕様を扱います。Kiro CLI と仕様が異なる箇所は明示し、CLI 側の詳細は姉妹サイトに委ねます

---

## ⚖️ 免責

本ドキュメントは非公式の解説であり、Kiro および Amazon Web Services, Inc. とは関係ありません。
最新かつ正確な情報は必ず[公式ドキュメント](https://kiro.dev/docs/)を確認してください。

---

**ライセンス**: [MIT License](../LICENSE)
