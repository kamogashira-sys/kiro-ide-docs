# エディタ基盤（画面構成・索引・Git・アクセス制御）

**Code OSS 由来の画面と、Kiro が加えたエディタ側の機能をまとめます。**

- **一次情報**: [Kiro Interface](https://kiro.dev/docs/ide/editor/interface/)（公式ページ更新日: 2026-08-04）・[Codebase indexing（単独ページは廃止。IDE概要ページの Editor 項目内で言及）](https://kiro.dev/docs/ide/)・[Source Control](https://kiro.dev/docs/ide/editor/source-control/)・[Kiroignore](https://kiro.dev/docs/kiroignore/)・[Multi-root Workspaces](https://kiro.dev/docs/ide/editor/multi-root-workspaces/)

> **前提**: Kiro IDE は **VS Code の基盤（Code OSS）のフォーク**です。エディタの基本操作は VS Code と同じで、
> **AI 機能が全体に統合されている**点が違います。VS Code からの移行は
> [03_deployment/03_migrating-from-vscode.md](../03_deployment/03_migrating-from-vscode.md) を参照してください。

---

## 1. 画面構成（5つの構成要素）

| # | 要素 | 役割 |
|---|------|------|
| 1 | **Editor** | コードを書く中央の作業領域 |
| 2 | **Chat Panel** | AI とやり取りする専用パネル |
| 3 | **Views** | サイドバー（ファイル管理・検索・ソース管理などの専用ビュー） |
| 4 | **Status Bar** | 現在のファイル・Git の状態・エラー/警告の件数 |
| 5 | **Command Palette** | よく使う操作と AI ツールへの素早いアクセス |

### 1.1 Editor

| 機能 |
|------|
| 複数言語の構文ハイライト |
| 行番号とエラー表示 |
| コードの折りたたみ |
| 複数タブでのファイル横断作業 |
| **分割ビュー**（並べて編集） |

### 1.2 Chat Panel

| できること |
|----------|
| コードについて質問する |
| コードの生成・変更を依頼する |
| デバッグとトラブルシューティングの助けを得る |
| コードレビューと最適化の提案を求める |
| **`#` コマンドでコンテキストを含める**（`#File`・`#Folder` など） |
| ボイラープレートやテンプレートを生成する |

> **チャットパネルを反対側に移す**: メニューバーの **View > Appearance > Move Primary Side Bar Right**

チャットの詳細は [02_chat.md](02_chat.md)、`#` の一覧は [04_reference/04_context-providers.md](../04_reference/04_context-providers.md) を参照してください。

### 1.3 Views（サイドバーの6ビュー）

| ビュー | 内容 |
|-------|------|
| **Explorer** | プロジェクトのファイル構造を辿る。**Git の状態表示**、**Specs と MCP サーバの専用セクション**がある。**1つ以上のファイル・フォルダを右クリックし `Select Files as Context` でチャットのコンテキスト参照に追加できる（1.0.288）** |
| **Search** | プロジェクト全体の検索と置換 |
| **Source Control** | Git 操作・変更の確認・**AI 生成のコミットメッセージ**でのコミット（§3） |
| **Run and Debug** | 変数・コールスタック・ブレークポイントの管理 |
| **Extensions** | 拡張機能のインストールと管理（**Open VSX レジストリ**） |
| **Kiro** | **AI 機能の専用ビュー**（下記） |

**Kiro ビューの中身（4種）**:

| 項目 | 参照 |
|------|------|
| **Specs** の概要と管理 | [01_specs.md](01_specs.md) |
| **Agent Hooks** の管理 | [05_hooks.md](05_hooks.md) |
| **Agent Steering** の設定 | [06_steering.md](06_steering.md) |
| **MCP サーバ** | [08_mcp.md](08_mcp.md) |

### 1.4 Status Bar

| 表示されるもの |
|-------------|
| 現在のファイルの情報 |
| Git のブランチと同期状態 |
| エラーと警告の件数 |
| **エージェントの状態表示** |

### 1.5 Command Palette

`Cmd+Shift+P` / `Ctrl+Shift+P` で開きます。

| できること |
|----------|
| よく使う操作の実行 |
| **MCP ツールへのアクセス** |
| 設定の変更 |
| **エージェントフックの実行** |

---

## 2. コードベースの索引（Codebase indexing）

**Kiro はコードベースとドキュメントを自動的に索引化**して、コード補完・ナビゲーション・文脈に応じた支援を提供します。

### 2.1 自動で索引化されるとき

| 契機 | 内容 |
|------|------|
| **プロジェクトのインポート** | Kiro でプロジェクトを初めて開いたとき、ワークスペースの全ファイルの索引化が始まる |
| **ファイルの変更** | 新しいファイルが作成・追加されると自動的に索引化される |
| **外部からの変更** | **Kiro の外で変更されたとき**（git 操作など）に再索引化される |

### 2.2 手動の索引化コマンド

コマンドパレット（`Cmd+Shift+P` / `Ctrl+Shift+P`）から実行します。

| コマンド | 使うとき |
|---------|--------|
| **`Kiro: Codebase Force Re-Index`** | 索引が壊れている・不完全だと疑われる／**プロジェクトに大きな構造変更をした**／**Kiro の提案が古く見える** |
| **`Kiro: Rebuild codebase index`** | 索引が**深刻に壊れている**／コードナビゲーションや提案の問題が**継続している**（force re-index より徹底的） |
| `Kiro: Docs Index` | プロジェクトのドキュメントファイルの索引化を開始する |
| `Kiro: Docs Force Re-Index` | すべてのドキュメントファイルを強制的に再索引化する |

> **`Force Re-Index` と `Rebuild` の違い**: Rebuild は**ゼロから作り直す**ため、より徹底的です。
> まず Force Re-Index を試し、それでも直らない場合に Rebuild を使います。

### 2.3 進捗の確認

| 順 | 操作 |
|----|------|
| 1 | Kiro の **Output** パネルを開く |
| 2 | ドロップダウンから **"Kiro Logs"** を選ぶ |
| 3 | リアルタイムの進捗と状態を見る |

**ログに出るもの**: 索引化の開始と完了／**見つかったファイル数と処理済み数**／大規模コードベースでの**進捗率**／完了までの時間。

### 2.4 索引化される内容

| 種別 | 内容 |
|------|------|
| **ソースコード** | ワークスペース内のすべてのプログラミング言語のファイル |
| **ドキュメント** | Markdown・MDX・その他のドキュメント形式 |
| **設定** | プロジェクトの設定ファイルとマニフェスト |
| **依存関係** | パッケージ定義と依存情報 |

**索引データが可能にする機能**: 賢いコード補完／ファイル横断のナビゲーション／文脈に応じた提案／ドキュメントの参照／リファクタリング支援。

### 2.5 エディタの検索結果と一致（1.0.288 で改善）

**`grep_search` と `file_search` が IDE 自身の検索機能を経由するようになりました。** これにより、エージェントの検索結果がエディタで実際に見える内容と一致します。

---

## 3. Source Control（Git 統合）

### 3.1 コミットメッセージの AI 生成

**ステージした変更を AI が分析して、意味のあるコミットメッセージを自動生成します。**

| 順 | 操作 |
|----|------|
| 1 | Source Control パネルで**変更をステージする** |
| 2 | コミットメッセージ入力欄の隣の **🪄 ボタン**を押す |
| 3 | 生成されたメッセージを確認する |
| 4 | 必要なら編集する |
| 5 | コミットする |

> **`Kiro: Generate Commit Message` にカスタムショートカットを割り当てられます**（公式の Tip）。
> 割り当て方は [04_reference/02_keyboard-shortcuts.md](../04_reference/02_keyboard-shortcuts.md#ショートカットをカスタマイズする) を参照してください。

### 3.2 メッセージの形式

**[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) 形式**に、詳細な本文セクションが付きます。

```
<type>(<scope>): <subject>

- First change or addition
- Second change or improvement
- Third change if applicable
- Why this change was needed (if relevant)
```

**type の種類（9種）**:

| type | 内容 |
|------|------|
| `feat` | 新機能 |
| `fix` | バグ修正 |
| `docs` | ドキュメントの変更 |
| `style` | 書式の変更 |
| `refactor` | コードの再構成 |
| `test` | テストの追加・更新 |
| `chore` | 保守作業 |
| `perf` | 性能改善 |
| `ci` | CI/CD の変更 |

### 3.3 Git の変更をチャットに渡す

**`#Git Diff`** と打つと、**ステージ済みとステージしていない変更の両方**を Kiro に見せられます。

```
Hey Kiro, can you fix the merge conflicts? #Git Diff
```

### 3.4 Git 操作が失敗するとき（公式の対処）

- Git の設定と資格情報を確認する
- リポジトリに対する適切な権限があるか確認する

---

## 4. `.kiroignore`（エージェントに読ませないファイル）

**`.kiroignore` は Kiro が特定のファイルを読むのを防ぎます。** 使い慣れた gitignore 構文で、非公開にしたいファイル（資格情報・秘密情報・エージェントのコンテキストに入れたくない内容）のパターンを定義します。

### 4.1 なぜ使うか（公式の4点）

| 目的 | 内容 |
|------|------|
| **セキュリティ** | 資格情報・API キー・機密データを含むファイルへのアクセスを防ぐ |
| **プライバシー** | 秘密情報を AI とのやり取りから除外する |
| **コンプライアンス** | **外部サービスに共有すべきでないファイルにアクセスさせない** |
| **集中** | 大きなファイルやビルド成果物を除外して、コンテキストを関連あるものに保つ |

### 4.2 設定手順

| 順 | 操作 |
|----|------|
| 1 | プロジェクトルート（または任意のサブディレクトリ）に `.kiroignore` を作る |
| 2 | 除外したいファイルのパターンを書く |
| 3 | 設定を開く（`Cmd+,` / `Ctrl+,`） |
| 4 | **Agent Ignore Files** を検索する（設定キー: **`kiroAgent.agentIgnoreFiles`**） |
| 5 | 配列に **`.kiroignore`** を追加する |

> **手順3〜5が必要です。** ファイルを作るだけでは有効になりません。
>
> 公式の Tip: **まず資格情報と秘密情報から始める**（最優先で守るべきファイル）。パターンは後から広げられます。

**設定値の書き方**:

| 値 | 意味 |
|----|------|
| `[".gitignore", ".kiroignore"]` | 複数の無視ファイルを同時に使う |
| `[]` | ワークスペースレベルの無視ファイルを無効化する |

### 4.3 パターンの書き方

**標準的な gitignore 構文**です。

| パターン | 効果 |
|---------|------|
| `file.txt` | 特定のファイルを無視 |
| `*.log` | 拡張子で無視 |
| `folder/` | ディレクトリを無視 |
| `**/temp` | **任意のサブディレクトリで無視** |
| `!keep.txt` | **無視しない（否定）** |

> ⚠️ **親ディレクトリを除外すると、その中のファイルを再包含できません**（公式明記）。
> 例: `secrets/` を無視した場合、`!secrets/public.txt` は**効きません**。
> ディレクトリ内の特定ファイルを含めたい場合は、**ディレクトリ全体を除外せず、より具体的なパターンを使います**。

### 4.4 記述例

**API キーと秘密情報を守る**:

```bash
# Environment files with credentials
.env
.env.local
.env.production

# Keep the template accessible
!.env.example

# Certificate and key files
*.pem
*.key
*.p12
credentials/
```

**ビルド成果物とデータファイルを除外する**:

```bash
# Build outputs
dist/
build/
.next/

# Data files
*.sql
*.dump
data/exports/
```

**チームのコンプライアンス対応**:

```bash
# Customer data directories
customer-data/
pii/

# Audit and compliance docs
compliance/internal/
audit-reports/
```

### 4.5 サブディレクトリとグローバル

| 種別 | 場所 | 設定 |
|------|------|------|
| **サブディレクトリ** | 任意のサブディレクトリの `.kiroignore` | **親のパターンを上書き・拡張できる**（そのディレクトリ内では優先される） |
| **グローバル** | **`~/.kiro/settings/kiroignore`** | **設定不要。存在すれば自動的に尊重される** |
| Git のグローバル無視ファイル | git の `core.excludesfile` | 自動。**ただし git リポジトリ内でのみ適用** |

### 4.6 `.gitignore` との使い分け

公式の指針:

> **エージェントのアクセスとバージョン管理で異なるルールが必要なとき**、または
> **git で追跡しているが Kiro には読ませたくない**ファイルを遮断したいときに `.kiroignore` を使います。

**公式のベストプラクティス**: コメントで**なぜ無視しているかを書き残す**（チームメンバーの助けになる）。

> **`.kiroignore` は保護されたパスです。** エージェントが書き換えようとすると必ず確認が求められます
> （[03_deployment/05_security.md](../03_deployment/05_security.md#3-保護されたパスprotected-paths)）。

### 4.7 作業中も ignore ファイルが即時反映される（1.0.288 で改善）

**`kiroAgent.agentIgnoreFiles` を編集すると、リロードなしで実行中のセッションに反映されます。** さらに以下の改善が入りました。

| 改善内容 |
|---------|
| ignore ルールが**読み取りだけでなく書き込みにも適用される**ようになった |
| **無効なエントリは黙って失敗せず表面化する**ようになった |

---

## 5. マルチルートワークスペース

**1つのワークスペースに複数のルートフォルダを持たせられます。**

作り方: **File > Add Folder to Workspace...** で別のフォルダを選ぶ／Finder や エクスプローラから Kiro の Explorer ビューにドラッグ&ドロップする。

**Kiro は各ルートフォルダ配下の `.kiro` から成果物を読み書きします。**

| 対象 | 挙動 |
|------|------|
| **Specs** | 各ルートから取得し統合表示。**各 spec の隣にルートフォルダ名が表示される** |
| **ステアリング** | 各ルートから取得し **Workspace** グループに統合表示。**新規作成時は保存先のルートを選ぶ** |
| **フック** | 各ルートから取得し **Agent Hooks** に統合表示 |
| **MCP サーバ** | 各ルートから取得し **MCP Servers** に統合表示。**Open MCP config** は既定でユーザーレベルを開き、**Workspace Config** を押すとどのルートかを選ぶ |
| **コードベースの索引・リポジトリマップ** | **すべてのルートのコードを含む**。プロンプトからの参照方法は単一ルートと同じ |

**ファイルパスはルートフォルダを横断して賢く解決されます。**

---

## 6. 拡張機能

| 項目 | 内容 |
|------|------|
| **レジストリ** | **Open VSX**（<https://open-vsx.org>）。**VS Code Marketplace ではない** |
| 対応 | 言語拡張・テーマ・デバッグ拡張・Git 拡張 |
| **制約** | **Open VSX にあるものだけ**が使える |
| 組織での変更 | **`ExtensionGalleryServiceUrl`** ポリシーで社内レジストリに向けられる（[03_deployment/04_enterprise.md](../03_deployment/04_enterprise.md#6-拡張機能レジストリの変更)） |

> ⚠️ **リモート拡張機能の注意**: リモート拡張機能を使うとローカルマシンとリモートマシンの間に接続が開きます。
> **信頼できる相手が所有する安全なリモートマシンにのみ接続してください**
> （[03_deployment/05_security.md](../03_deployment/05_security.md#71-リモート拡張機能の注意)）。

### 6.1 リモートホストの信頼プロンプト（1.0.288 で追加）

**リモートホストへの接続時、リモート拡張機能が実行される前に信頼するかどうかを確認するプロンプトが表示されます。**

| 選択肢 | 内容 |
|-------|------|
| **Trust and Connect** | このホストを信頼して接続する |
| **Don't Connect** | 接続しない |
| **Always trust this remote host** | 常に信頼する（**マシン単位で記憶される**） |

---

## 7. Code OSS のバージョン追従

公式の説明:

> Kiro は定期的なリベースによって VS Code の開発サイクルに同期しています。最新の機能や改善を取り込みますが、**安定した VS Code のリリースを戦略的に選んでいます**。

取り込みは changelog で明示されます（例: **1.0.242 で Code OSS v1.108.2**・**1.0.288 で Code OSS v1.109.5**）。推移は [02_update/01_changelog.md](../02_update/01_changelog.md) で追えます。

### 7.1 Code OSS v1.109.5 での新設定（1.0.288 で追加）

| 設定キー | 内容 |
|---------|------|
| `terminal.integrated.stickyScroll.ignoredCommands` | ターミナルのスティッキースクロールで、特定のコマンドを対象外にできる |
| `editorBracketMatch.foreground` | 一致する括弧の色を変更できる |
| `terminal.integrated.allowInUntrustedWorkspace` | 信頼していないワークスペースでもターミナルを使うことを選択できる |

---

## 8. ナビゲーションのコツ（公式）

- **キーボードショートカット**を使う（[04_reference/02_keyboard-shortcuts.md](../04_reference/02_keyboard-shortcuts.md)）
- **コマンドパレット**で機能に素早くアクセスする
- よく使うファイルを**ピン留め**する
- **分割ビュー**でコードを比較・参照する

---

## 関連ドキュメント

- [02_chat.md](02_chat.md) - チャットパネルの使い方
- [04_reference/02_keyboard-shortcuts.md](../04_reference/02_keyboard-shortcuts.md) - ショートカット30件
- [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) - `.kiro/` と `.kiroignore` の仕様
- [03_deployment/03_migrating-from-vscode.md](../03_deployment/03_migrating-from-vscode.md) - VS Code からの移行
- [03_deployment/04_enterprise.md](../03_deployment/04_enterprise.md) - 拡張機能レジストリの変更
- [03_deployment/05_security.md](../03_deployment/05_security.md) - 保護されたパス・リモート拡張機能
