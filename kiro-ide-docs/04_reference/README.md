# 04_reference - リファレンス

**設定ファイルの仕様やショートカットの一覧など、辞書的に引くための情報をまとめたセクションです。**

---

## 📂 このセクションのファイル

| ファイル | 内容 | 収録件数 |
|---------|------|---------|
| [01_kiro-directory.md](01_kiro-directory.md) | **`.kiro/` ディレクトリのファイル仕様**。Specs・Hooks・Steering・Custom Agents・MCP・権限の置き場所 | — |
| [02_keyboard-shortcuts.md](02_keyboard-shortcuts.md) | **キーボードショートカット** | **30件** |
| [03_permissions.md](03_permissions.md) | **権限モデル**。capability・ルールの書式・既定の挙動 | capability **14種** |
| [04_context-providers.md](04_context-providers.md) | **コンテキストプロバイダ**。チャットで `#` から呼び出せる参照元 | — |
| [05_models.md](05_models.md) | **モデル**。選べるモデルと選び方 | — |

---

## 🔍 目的別の入口

| 引きたいもの | 参照先 |
|------------|-------|
| フックやステアリングのファイルをどこに置くか | [01_kiro-directory.md](01_kiro-directory.md) |
| チャットを開くショートカット | [02_keyboard-shortcuts.md](02_keyboard-shortcuts.md) |
| エージェントに `.env` を読ませない設定 | [03_permissions.md](03_permissions.md) |
| チャットに特定のファイルだけ渡す方法 | [04_context-providers.md](04_context-providers.md) |
| どのモデルを使うか | [05_models.md](05_models.md) |

---

## 📏 このセクションの書き方

| 方針 | 内容 |
|------|------|
| **出典を明記する** | 各項目に公式ページの URL を付けます |
| **件数を数値で持つ** | ショートカット数（29）と capability 数（14）は本サイトの検証対象です。公式ページで件数が変わったら本サイトも更新します |
| **IDE 版として完結させる** | 設定ファイルの仕様は Kiro CLI とも共通ですが、引くときにリンクを往復しなくて済むよう **IDE 版で完結**して書きます。CLI 側の対応ページは各項目に併記します |

---

## 関連セクション

- [00_information](../00_information/) - 基本情報・公式情報源
- [01_features](../01_features/) - 機能詳細ガイド（使い方の解説）
- [02_update](../02_update/) - アップデート情報（仕様が変わった時期）
- [03_deployment](../03_deployment/) - インストール・組織導入
