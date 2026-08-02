# 00_information - 基本情報・公式情報源

**Kiro IDE がどういう製品なのか、公式情報がどこにどんな形で置かれているのかをまとめたセクションです。**

---

## 📂 このセクションのファイル

| ファイル | 内容 |
|---------|------|
| [01_official-site-structure.md](01_official-site-structure.md) | **公式サイトの構造マップ**。`kiro.dev` の全体像とドキュメントのセクション構成 |
| [02_information-sources.md](02_information-sources.md) | **情報源一覧**。`llms.txt`・`sitemap.xml`・Atom フィードなど機械可読な資産の性質と使い分け |

---

## 📢 Kiro IDE とは

**Kiro IDE** は、AI エージェントを中核に据えた統合開発環境です。公式は「**An agentic IDE that helps you do your best work**」と説明しています（[公式ドキュメントトップ](https://kiro.dev/docs/)）。

VS Code の基盤である **Code OSS のフォーク**として構築されているため、VS Code の拡張機能・キーバインド・設定を活かしたまま、エージェント前提の機能群を使えます。

### 5つの中核機能

公式ドキュメントトップが「Core capabilities」として挙げるものです。

| 機能 | 公式の説明（要約） | 本サイトの解説 |
|------|-----------------|--------------|
| **Specs** | 構造化された仕様で機能を計画・構築する | [01_features/01_specs.md](../01_features/01_specs.md) |
| **Hooks** | 賢いトリガーで繰り返し作業を自動化する | [01_features/05_hooks.md](../01_features/05_hooks.md) |
| **Agentic chat** | AI との自然な対話で機能を構築する | [01_features/02_chat.md](../01_features/02_chat.md) |
| **Steering** | 独自のルールとコンテキストで AI を導く | [01_features/06_steering.md](../01_features/06_steering.md) |
| **MCP Servers** | 外部のツールやデータソースを接続する | [01_features/08_mcp.md](../01_features/08_mcp.md) |

> 公式トップは6番目に「Privacy First」（プライバシー制御によるコードの保護）も挙げています。
> 本サイトでは [03_deployment/](../03_deployment/) のセキュリティ関連ページで扱います。

### 3つのサーフェス（IDE / CLI / Web）

Kiro は IDE 単体の製品ではありません。公式の `llms.txt` は次の説明で始まります。

> Kiro is a coding agent with an IDE, CLI, and web interface.

| サーフェス | 製品ページ | 公式ドキュメント | 本サイトの扱い |
|-----------|----------|---------------|--------------|
| **IDE** | <https://kiro.dev/ide/> | `/docs/`（117ページ） | **本サイトの対象** |
| **CLI** | <https://kiro.dev/cli/> | `/docs/cli/`（101ページ） | 姉妹サイト [q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs) が扱う |
| **Web** | <https://kiro.dev/web/> | `/docs/web/`（20ページ） | 姉妹サイト [kiro-web-docs](https://github.com/kamogashira-sys/kiro-web-docs) が扱う |

> **モバイル**: <https://kiro.dev/mobile/> も存在しますが、専用のドキュメントツリーはありません。

3つのサーフェスは設定ディレクトリ `~/.kiro/`（Specs / Hooks / Steering / MCP など）を共有します。
ファイル仕様は [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) にまとめています。

---

## 🔖 バージョンの数え方

| 項目 | 内容 |
|------|------|
| 形式 | `1.0.NNN`（メジャー.マイナー.**ビルド番号**） |
| 最新版 | **1.0.242**（2026-07-28） |
| GA | **1.0.0**（2026-06-25） |
| 最初の公開版 | **0.1**（2025-07-14・Preview release） |
| リリース頻度 | 実測でおおむね**週次**（1.0 系は 2026-06-25 〜 2026-07-28 の約1か月で12版） |

ビルド番号は系列内で連続しません（1.0.52 → 1.0.89 → 1.0.116 …）。
全バージョンの内容は [02_update/](../02_update/) にまとめています。

---

## 🐾 IDE と CLI を混同しないために

Kiro IDE と Kiro CLI は**同じ名前の機能でも仕様が異なる**ことがあります。特に注意が必要な3つ:

| 機能 | Kiro IDE 1.0 | Kiro CLI での対応 |
|------|-------------|-----------------|
| **Permissions** | capability ベース（`fs_read`・`shell` など） | **CLI 3.0（Early Access）**の [`docs/cli/v3/permissions`](https://kiro.dev/docs/cli/v3/permissions) が対応。CLI 2.x は旧モデル |
| **Custom agents** | Markdown 形式・タグベースのツール指定 | [`docs/cli/v3/agent-config`](https://kiro.dev/docs/cli/v3/agent-config)。CLI 2.x は JSON 形式 |
| **Hooks** | `.kiro/hooks/*.json`（イベント駆動の自動化） | [`docs/cli/v3/hooks`](https://kiro.dev/docs/cli/v3/hooks)。**CLI 2.x の hooks は完全な別物**（stdin 経由 JSON のライフサイクルフック） |

**スラッシュコマンド**は、同名でも仕組み自体が違います。IDE のスラッシュコマンドは**すべてユーザー定義**（manual トリガのフックと `inclusion: manual` のステアリングファイルが `/` メニューに並ぶ）で、製品が提供する固定のコマンド一覧はありません。CLI 版の固定コマンド一覧を IDE に当てはめないでください。

> 本サイトで Kiro CLI 版のページにリンクするときは、上記のとおり **`docs/cli/v3/` を指す**規約にしています。

---

## 関連セクション

- [01_features](../01_features/) - 機能詳細ガイド（10機能）
- [02_update](../02_update/) - アップデート情報（1.0 系・0.x 系）
- [03_deployment](../03_deployment/) - インストール・認証・エンタープライズ配布
- [04_reference](../04_reference/) - リファレンス（設定ファイル・ショートカットほか）
