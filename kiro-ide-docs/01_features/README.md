# 01_features - 機能詳細ガイド

**Kiro IDE の機能を、公式ドキュメントをもとに解説します。**

---

## 📋 機能一覧（12機能）

| # | 機能 | 概要 | 導入 |
|---|------|------|------|
| 1 | [Specs](01_specs.md) | **仕様駆動開発**。要件・設計・タスクの3成果物で機能を作る。Quick Spec・Bugfix Spec・要件分析 | 0.1 |
| 2 | [Chat](02_chat.md) | **エージェントとの対話**。Vibe / Spec セッション・サブエージェント・チェックポイント・会話の書き出し | 0.1 |
| 3 | [Permissions](03_permissions.md) | **capability ベースの権限**。1つのルールを全ツールに効かせる | **1.0** |
| 4 | [Autopilot・Supervised](04_autopilot-supervised.md) | **2つの実行モード**。レビューのタイミングを変える（**権限は同一**） | 0.x |
| 5 | [Hooks](05_hooks.md) | **イベント駆動の自動化**。v1 JSON 形式・トリガー10種 | 0.x（**1.0 で形式変更**） |
| 6 | [Steering](06_steering.md) | **持続的な指示**。読み込みタイミング4種・スラッシュコマンドの実体 | 0.1 |
| 7 | [Custom Agents](07_custom-agents.md) | **専用エージェント**。Markdown 1枚にプロンプト・ツール・MCP・権限 | **1.0** |
| 8 | [MCP](08_mcp.md) | **外部ツールの接続**。プロンプト・リソーステンプレート・elicitation | 0.1 |
| 9 | [Agent Focus Mode](09_agent-focus-mode.md) | **チャット中心のレイアウト**（実験的）。並列セッション・Dockable chat | **1.0** |
| 10 | [エディタ基盤](10_editor.md) | 画面構成・コードベース索引・Git 統合・`.kiroignore`・マルチルート | 0.1 |
| 11 | [Powers](11_powers.md) | **動的に読み込まれる専門知識パッケージ**。Agent Plugins 仕様・MCP と Skills のバンドル | **1.0.288** |
| 12 | [Cloud Sessions](12_cloud-sessions.md) | **クラウドサンドボックスで動くセッション**（プレビュー）。IDE/CLI/Web/Mobile 間で継続 | **1.0.293** |

**「導入」列**: 機能が最初に登場したバージョンです。1.0 で追加された3機能（Permissions・Custom Agents・Agent Focus Mode）は [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) も参照してください。

---

## 🧭 目的別の入口

| やりたいこと | 参照先 |
|------------|-------|
| **まず何ができるか知りたい** | [01_specs.md](01_specs.md) → [02_chat.md](02_chat.md) |
| **エージェントに勝手に触られたくない** | [03_permissions.md](03_permissions.md) → [04_autopilot-supervised.md](04_autopilot-supervised.md) |
| **秘密情報を読ませたくない** | [10_editor.md](10_editor.md#4-kiroignoreエージェントに読ませないファイル)（`.kiroignore`） |
| **チームの規約を守らせたい** | [06_steering.md](06_steering.md) |
| **保存時にリントを走らせたい** | [05_hooks.md](05_hooks.md) |
| **用途別のエージェントを作りたい** | [07_custom-agents.md](07_custom-agents.md) |
| **外部のツールと連携したい** | [08_mcp.md](08_mcp.md) |
| **複数の作業を並列に任せたい** | [09_agent-focus-mode.md](09_agent-focus-mode.md) → [02_chat.md](02_chat.md#7-サブエージェント並列実行と委譲) |

---

## 🔗 機能どうしの関係

覚えておくと混乱しにくい点です。

| 論点 | 押さえること |
|------|------------|
| **Permissions と Autopilot/Supervised** | **別物**。Supervised はレビューのタイミングを変えるだけで、**権限は Autopilot と同一**。アクセス範囲を絞るのは Permissions |
| **Permissions と Trusted Commands** | **別物**。Permissions は複合コマンドを分割して評価するが、Trusted Commands は**単純な前方一致で構造を解析しない** |
| **Permissions と `.kiroignore`** | **別物**。`.kiroignore` はエージェントに見せないファイルの指定 |
| **Hooks と Steering** | 1.0 で **manual トリガのフックが廃止**され、manual ステアリングファイルに置き換わった。**IDE のスラッシュコマンドはステアリング由来** |
| **Custom Agents とサブエージェント** | 同じ Markdown 定義を使う。サブエージェントは `description` で自動選択される |
| **サブエージェントの制約** | **Specs にアクセスできず、Hooks も発火しない**。ステアリングと MCP は動く |

---

## 📏 このセクションの方針

| 方針 | 内容 |
|------|------|
| **IDE 版の仕様として書く** | 本サイトは **Kiro IDE 版**を扱います。Kiro CLI と仕様が異なる箇所は明示し、CLI 側の詳細は姉妹サイト [q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs) に委ねます |
| **CLI 版へのリンクは v3 を指す** | IDE 1.0 の GA 機能（Permissions・Custom Agents・Hooks）に対応するのは **CLI 3.0（Early Access）**です。CLI 2.x の非 v3 ページは別仕様で、**特に hooks は完全な別物**です |
| **公式に記述のない内容は書かない** | 確認できない事項は「**未確認**」と明示します |
| **公式ドキュメント間の食い違いは明示する** | 更新日を比べて新しい方を正とし、食い違いの存在自体も記載します（例: [05_hooks.md](05_hooks.md) のトリガー名） |

---

## 📌 今後追加する機能

v1 公開時点では10機能を収録していました（現在は Powers・Cloud Sessions を追加し**12機能**）。公式ドキュメントには他にも次の領域があり、公開後に追補します。**それぞれ Issue を立てています**（[Issues](../../../../issues)）。

| 領域 | 公式ページ | Issue |
|------|----------|-------|
| **Agent Skills**（可搬な指示パッケージ） | [`/docs/skills`](https://kiro.dev/docs/skills/) | [#2](../../../../issues/2) |
| Dev servers（長時間実行プロセスの管理） | [`/docs/ide/chat/dev-servers`](https://kiro.dev/docs/ide/chat/dev-servers/) | [#3](../../../../issues/3) |
| Diagnostics tool | `/docs/ide/chat/*`（**未確認**: 公式索引 `llms.txt` の Chat 配下ページを確認しましたが、該当する専用ページの記述が見当たりません） | [#3](../../../../issues/3) |
| Agent Notifications | [`/docs/ide/chat/notifications`](https://kiro.dev/docs/ide/chat/notifications/) | [#3](../../../../issues/3) |
| Terminal integration | [`/docs/ide/chat/terminal`](https://kiro.dev/docs/ide/chat/terminal/) | [#3](../../../../issues/3) |
| Spec の Best practices | [`/docs/specs/best-practices`](https://kiro.dev/docs/specs/best-practices/) | [#4](../../../../issues/4) |

> **Spec の Correctness（プロパティベーステスト）は収録済み**です（[01_specs.md](01_specs.md) §9）。

---

## 🔎 未収録機能に関する記述の在りか

**専用ページはありませんが、次の情報は本サイト内にあります。**

| 項目 | 本サイト内の記述 |
|------|--------------|
| **Powers とは何か** | [0.7 の導入時の説明](../02_update/02_changelog-0x.md#powers)（**0.7 時点の内容**。現在の仕様は公式を参照） |
| Powers の権限（`power` capability） | [04_reference/03_permissions.md](../04_reference/03_permissions.md#3-capability-一覧14種) |
| Powers のツール指定（`@powers`・`includePowers`） | [05_hooks.md](05_hooks.md#21-matcher-の書き方ツール名の指定)・[02_chat.md](02_chat.md#7-サブエージェント並列実行と委譲) |
| **Agent Skills の置き場所**（`.kiro/skills/<名前>/SKILL.md`） | [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#7-agent-skills--kiroskills名前skillmd) |

---

## 関連セクション

- [00_information](../00_information/) - Kiro IDE の基本情報・公式情報源
- [02_update](../02_update/) - 各機能がいつ入ったか
- [03_deployment](../03_deployment/) - インストール・認証・組織導入
- [04_reference](../04_reference/) - 設定ファイル・ショートカット・権限の辞書
