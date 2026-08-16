# VS Code から Kiro IDE への移行

**VS Code の設定・拡張機能・キーバインドを Kiro IDE に持ち込む方法を扱います。**

- **一次情報**: [Migrating from VSCode](https://kiro.dev/docs/upgrade-guides/migrating-from-vscode/)

> **前提**: Kiro IDE は **VS Code のオープンソース基盤（Code OSS）**の上に構築されています。
> そのため慣れた操作画面のまま、既存の設定を持ち込めます。

---

## 1. 何が持ち込めるか

プロファイルをインポートすると、次のものが入ります。

| 項目 | 内容 |
|------|------|
| **カラーテーマと UI 設定** | 見た目の設定 |
| **エディタとワークスペースの設定** | `settings.json` の内容 |
| **キーバインド** | カスタムキーボードショートカット |

拡張機能については §3 に条件があります。

---

## 2. プロファイルの移行手順

初回起動時に「VS Code の設定をインポートするか」を聞かれます（[01_installation.md](01_installation.md) の手順2）。ここでスキップした場合や、別のマシンから持ってきたい場合は、VS Code のプロファイル機能を使って手動で移行します。

### 2.1 VS Code からエクスポートする

| 順 | 操作 |
|----|------|
| 1 | VS Code で**コマンドパレット**を開く（`⌘`/`Ctrl` + `Shift` + `P`） |
| 2 | 「Preferences: Open Profiles (UI)」を選ぶ |
| 3 | サイドバーで移行したいプロファイルを選ぶ |
| 4 | 3点メニューから **Export** を選ぶ |
| 5 | ローカルに保存するか、GitHub Gist に公開する |

### 2.2 Kiro にインポートする

| 順 | 操作 |
|----|------|
| 1 | Kiro で**コマンドパレット**を開く（`⌘`/`Ctrl` + `Shift` + `P`） |
| 2 | 「Preferences: Open Profiles (UI)」を選ぶ |
| 3 | **New Profile** の隣のドロップダウンから **Import Profile** を選ぶ |
| 4 | GitHub Gist の URL を入れるか、ローカルのエクスポートファイルを選ぶ |
| 5 | **Import** を選んで保存する |
| 6 | サイドバーでプロファイルを選び、チェックマークを選んで有効化する |

> **VS Code と同じコマンド名**です（「Preferences: Open Profiles (UI)」）。Kiro が Code OSS ベースであることがそのまま効いています。

---

## 3. 拡張機能の互換性（最重要の注意点）

**Kiro は Open VSX レジストリを使います。** VS Code Marketplace ではありません。

| 種別 | 互換性 |
|------|-------|
| 言語拡張 | Open VSX にあるものは機能をそのまま維持 |
| テーマ拡張 | Open VSX にあるものは見た目もそのまま |
| デバッグ拡張 | 対応しているものはデバッグ作業を継続できる |
| Git 拡張 | コミットメッセージ生成・自動コードレビューが加わる |

公式の注記:

> **Open VSX レジストリにある拡張機能だけがインポートできます。** VS Code Marketplace 専用のものは Kiro では利用できない場合があります。

**移行前にやっておくとよいこと**: 現在使っている拡張機能が [open-vsx.org](https://open-vsx.org/) にあるかを先に確認します。無い場合は代替を探すか、その作業だけ VS Code に残す判断が必要です。

> **組織で配布する場合**: 独自の拡張機能レジストリ（審査済みの拡張機能だけを置いた社内レジストリなど）に向けることもできます。設定方法は [04_enterprise.md](04_enterprise.md) を参照してください。

---

## 4. 設定画面の構成

Kiro は VS Code の設定の仕組みに、AI 機能向けの項目を追加しています。

| 種別 | 開き方 | 内容 |
|------|-------|------|
| **Kiro の設定** | コマンドパレット → 「Preferences: Open Settings (UI)」→ **Kiro Agent** セクション | AI の挙動・エージェントの自動化・**信頼するコマンド**・Kiro 固有機能 |
| **VS Code の設定** | 同じ操作 | 従来の VS Code の設定がそのまま機能する |

**信頼するコマンド（Trusted Commands）は Kiro Agent セクションにあります。** エージェントが確認なしで実行できるコマンドを決める設定なので、移行後に一度確認しておくことをおすすめします（[05_security.md](05_security.md)）。

---

## 5. VS Code のバージョン追従について

公式の説明:

> Kiro は定期的なリベースによって VS Code の開発サイクルに同期しています。最新の機能や改善を取り込みますが、**安定した VS Code のリリースを戦略的に選んでいます**。

そのため VS Code の最新版と Kiro が取り込んでいる Code OSS のバージョンは一致しません。取り込みは changelog で明示されます（例: **1.0.242 で Code OSS v1.108.2**）。バージョンの推移は [02_update/01_changelog.md](../02_update/01_changelog.md) で追えます。

---

## 6. 移行のチェックリスト

| # | 確認事項 | 参照 |
|---|---------|------|
| 1 | 使っている拡張機能が Open VSX にあるか | §3 |
| 2 | プロファイルをエクスポートしたか | §2.1 |
| 3 | **信頼するコマンド**の設定を確認したか | §4・[05_security.md](05_security.md) |
| 4 | `.kiroignore` でエージェントに見せないファイルを決めたか | [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) |

---

## 関連ドキュメント

- [01_installation.md](01_installation.md) - インストール（初回起動時にもインポートできる）
- [04_enterprise.md](04_enterprise.md) - 独自の拡張機能レジストリの設定
- [05_security.md](05_security.md) - 信頼するコマンド・保護されるパス
- [01_features/10_editor.md](../01_features/10_editor.md) - エディタ基盤の機能
