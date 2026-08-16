# 03_deployment - インストール・環境構築・組織導入

**Kiro IDE を入れて使い始めるまでと、組織に配布するときに決めることをまとめたセクションです。**

---

## 📂 このセクションのファイル

| ファイル | 内容 | 主な読者 |
|---------|------|---------|
| [01_installation.md](01_installation.md) | **インストール**。対応 OS・配布形態・初回起動・旧版へのダウングレード | はじめて使う人 |
| [02_authentication.md](02_authentication.md) | **認証**。5つのサインイン方法と選び方 | はじめて使う人 |
| [03_migrating-from-vscode.md](03_migrating-from-vscode.md) | **VS Code からの移行**。プロファイル移行・拡張機能の互換性 | VS Code 利用者 |
| [04_enterprise.md](04_enterprise.md) | **エンタープライズ配布**。バージョン固定・段階ロールアウト・ガバナンス | 組織の管理者 |
| [05_security.md](05_security.md) | **セキュリティ**。エージェントの権限・許可すべき URL・データ保護 | 全員（特に管理者） |

---

## 🚀 はじめて使う（3ステップ）

| 順 | やること | 参照 |
|----|---------|------|
| 1 | **インストール** | [01_installation.md](01_installation.md) |
| 2 | **サインイン** | [02_authentication.md](02_authentication.md) |
| 3 | （VS Code 利用者のみ）**設定と拡張機能を持ち込む** | [03_migrating-from-vscode.md](03_migrating-from-vscode.md) |

その後の使い方は [01_features/](../01_features/) を参照してください。

---

## 🏢 組織に導入する（検討項目）

| 検討項目 | 決めること | 参照 |
|---------|----------|------|
| **認証方式** | IAM Identity Center を使うか、外部 IdP（Microsoft Entra ID・Okta）を接続するか | [02_authentication.md](02_authentication.md) |
| **バージョン管理** | 自動更新を許すか・特定バージョンに固定するか・段階的に配るか | [04_enterprise.md](04_enterprise.md) |
| **ネットワーク** | ファイアウォールで許可する URL の一覧 | [05_security.md](05_security.md) |
| **ガバナンス** | 使えるモデル・MCP サーバ・Web ツールの制限 | [04_enterprise.md](04_enterprise.md) |
| **データの扱い** | プロンプトログ・暗号化キー・利用状況の追跡 | [04_enterprise.md](04_enterprise.md)・[05_security.md](05_security.md) |

---

## ⚠️ 押さえておきたい前提

| # | 前提 |
|---|------|
| 1 | **Windows の ARM は非対応**（64bit の x64 のみ）。Linux は **glibc 2.39 以上**が必要です |
| 2 | **拡張機能は Open VSX レジストリ**から入れます。VS Code Marketplace 専用の拡張機能は入れられません |
| 3 | **自動更新は段階的に展開中**です。1.0 系では公式が「[downloads ページ](https://kiro.dev/downloads/)から直接ダウンロード」を案内しています |
| 4 | **Supervised モードはセキュリティ機構ではありません**（公式が明記）。エージェントのアクセス範囲を絞るには権限設定を使います |

---

## 関連セクション

- [00_information](../00_information/) - Kiro IDE の基本情報・公式情報源
- [01_features](../01_features/) - 機能詳細ガイド（12機能）
- [02_update](../02_update/) - アップデート情報（更新内容の確認）
- [04_reference](../04_reference/) - リファレンス（設定ファイル・権限ほか）
