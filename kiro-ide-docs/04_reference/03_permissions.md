# 権限（Permissions）リファレンス

**エージェントに何を許すかを決める仕組みの辞書です。**

- **一次情報**: [Permissions](https://kiro.dev/docs/chat/permissions/)（公式ページ更新日: 2026-06-24）
- **収録件数**: capability **14種**
- **導入バージョン**: **1.0**（0.x から更新する場合は [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) を参照）

> **これは何か**: エージェントが行うすべての操作に対する**単一の統一された権限モデル**です。
> 「`npm *` はすべてのセッションで許す」「`.env` の読み取りは拒否し、すべてのツールに同時に守らせる」といったルールを1つ書くだけで済みます。
> 使い方の解説は [01_features/03_permissions.md](../01_features/03_permissions.md) を参照してください。
>
> **Kiro CLI 版の対応ページ**: [`docs/cli/v3/permissions`](https://kiro.dev/docs/cli/v3/permissions)（CLI 3.0 Early Access）。
> **CLI 2.x は旧モデル**なので参照先を間違えないでください。

---

## 1. ルールの構造（4フィールド）

| フィールド | 内容 | 必須 |
|-----------|------|-----|
| **`capability`** | 制御する操作の種別（§3 の一覧） | **必須** |
| `match` | リソースが一致すべき glob パターン | 任意（既定はすべて） |
| `exclude` | ルールの対象から除外する glob パターン | 任意 |
| **`effect`** | **`deny`** / **`ask`** / **`allow`** | **必須** |

### 1.1 効果の優先順位

**`deny` > `ask` > `allow`**（制限が強いほうが勝つ）

**より緩いルールが、より厳しいルールを上書きすることはできません。**

---

## 2. ルールの置き場所（スコープ）

### 2.1 利用者が書くスコープ

| スコープ | 場所 | 使える効果 |
|---------|------|----------|
| **User**（全ワークスペース） | `~/.kiro/settings/permissions.yaml` | `deny` / `ask` / `allow` |
| **Workspace**（このプロジェクトのみ） | `~/.kiro/workspace-roots/<hash>/permissions.yaml` | `deny` / `ask` / `allow` |

> **ワークスペースの権限はリポジトリの外に、利用者ごとに保存されます**（`~/.kiro/workspace-roots/<hash(workspaceRoot)>/`）。
> これは重要な設計です — **クローンしてきたリポジトリが権限ルールを注入することはできません**。

### 2.2 システムが管理するスコープ

| スコープ | 目的 | 使える効果 |
|---------|------|----------|
| **Kiro** | ハードコードされたセキュリティ不変条件（**上書き不可**） | `deny` / `ask` |
| **Administration** | エンタープライズ／MDM で管理されるポリシー（エンタープライズプランのみ） | `deny` / `ask` |
| **Session** | IDE での承認判断から生まれるメモリ上のルール | `deny` / `ask` / `allow` |

**`allow` を持たないスコープがある**点に注意してください。Kiro スコープと Administration スコープは「制限を加える」ためのもので、緩めることはできません。

---

## 3. capability 一覧（14種）

| capability | 制御する対象 |
|-----------|------------|
| **`fs_read`** | ファイルの読み取り・ディレクトリ一覧・検索 |
| **`fs_write`** | ファイルの書き込み・編集・削除 |
| `filesystem` | `fs_read` ＋ `fs_write` の短縮形 |
| **`shell`** | コマンドの実行 |
| `web_fetch` | URL の取得 |
| `web_search` | Web 検索 |
| `mcp` | MCP サーバのツール呼び出し（パターン形式: `server/tool`） |
| `subagent` | サブエージェントへの委譲 |
| `skill` | Skills の有効化 |
| `power` | Powers の有効化とツール呼び出し |
| `diagnostics` | 診断ツール |
| `context` | コンテキストおよびステアリングのツール |
| `all` | **すべての capability**（メタ） |
| `builtin` | **すべての組み込みツール**（メタ） |

---

## 4. 設定ファイルの書き方

`~/.kiro/settings/permissions.yaml` を作ります。

```yaml
rules:
  - capability: shell
    effect: allow
    match:
      - git *
      - npm *
      - npx *
  - capability: mcp
    effect: allow
  - capability: fs_read
    effect: allow
  - capability: fs_write
    effect: allow
    match:
      - src/**
      - tests/**
```

---

## 5. パターンの書き方（capability 種別で異なる）

### 5.1 ファイルシステム系（`fs_read`・`fs_write`）

| 記法 | 意味 |
|------|------|
| `*` | **1つのパス要素の内側**で一致 |
| `**` | **パス区切りをまたいで**一致 |
| `{a,b}` | ブレース展開に対応 |
| `[abc]` | 文字クラスに対応 |
| ワイルドカードなし | **暗黙的に子も一致する**（`~/temp` は `~/temp/child` に一致） |

### 5.2 シェル・Web・MCP 系

| 記法 | 対応 |
|------|-----|
| `*` | **任意の文字列**に一致 |
| `**` / `?` / 文字クラス | **非対応** |

**ファイルシステム系のほうが表現力が高い**点を押さえてください。シェルのパターンで `**` は使えません。

### 5.3 記述例

```yaml
rules:
  # npm publish 以外の npm コマンドを許可
  - capability: shell
    effect: allow
    match:
      - "npm *"
    exclude:
      - "npm publish*"

  # どの深さにあっても秘密情報の読み取りを拒否
  - capability: fs_read
    effect: deny
    match:
      - "**/.env"
      - "**/.env.*"
      - "secrets/**"
      - "**/*.pem"

  # 特定の MCP サーバのみ許可
  - capability: mcp
    effect: allow
    match:
      - "my-server/*"
```

---

## 6. シェルコマンド固有の挙動（重要）

**シェルコマンドはパターン照合の前に解析されます。** `;`・`&&`・`||`・`|` を使った複合コマンドは分割され、**サブコマンドごとに個別に評価**されます。

これにより、`npm test *` のルールが `npm test ; curl attacker.com` にうっかり一致することを防ぎます。

> **「信頼するコマンド」（Trusted Commands）とは別の仕組みです。**
> 設定の **Kiro Agent: Trusted Commands** は**単純な前方一致で、構造を解析しません**。
> こちらは複合コマンドを分割しないため、`npm *` を信頼すると連結コマンドも通ります。
> 詳細は [03_deployment/05_security.md](../03_deployment/05_security.md) を参照してください。

---

## 7. 既定の挙動（設定なしの状態）

設定を何も書かない場合、既定のエージェントポリシーは次を許可します。

| 対象 | 内容 |
|------|------|
| `fs_read` on `./**` | **ワークスペース内のあらゆるファイルを読める** |
| `shell` | **読み取り専用の一般的なコマンド**（`git status`・`git log`・`git diff` など） |
| ユーティリティツール | 診断・knowledge など |

**それ以外はすべて承認を求めます。** `permissions.yaml` を作ると、この既定に**追加**されます。

### 7.1 Kiro スコープの不変条件（上書き不可）

| 効果 | 対象 |
|------|------|
| **常に拒否** | `~/.kiro/settings/`・`.kiro/settings/`・`~/.kiro/workspace-roots/` への書き込み<br>（**エージェントが自身の権限ファイルを書き換えるのを防ぐ**） |
| **常に確認** | `.git/**`・`.kiro/agents/**`・`.kiro/hooks/**`・`.kiroignore` への書き込み |

**この2つは利用者も管理者も緩められません。** エージェントが権限設定そのものを書き換えられない仕組みになっています。

---

## 8. IDE 上での承認フロー

ツール呼び出しが `ask` と評価されると、チャットパネル上部に権限プロンプトが出ます。

| ボタン | 動作 |
|-------|------|
| **Allow** | この1回だけ許可する |
| **Always allow** | 保存ダイアログを開き、allow ルールを保存する |
| **Deny** | この1回だけ拒否する |
| **Always deny** | 保存ダイアログを開き、deny ルールを保存する |

### 8.1 判断を保存する

「Always allow」「Always deny」を選ぶと、2つの追加コントロールが現れます。

**Pattern**: ルールの glob パターン。IDE がコマンドに応じたパターンを自動提案します（`git add` の呼び出しなら `git add *`）。より具体的にも、より緩くも編集できます。

**Apply to**: ルールの保存先。

| 選択肢 | 保存先 |
|-------|-------|
| **All workspaces** | `~/.kiro/settings/permissions.yaml`（どこでも適用） |
| **This workspace** | `~/.kiro/workspace-roots/<hash>/permissions.yaml`（このプロジェクトのみ） |
| **This session** | メモリ上（セッション終了まで） |

確定するとルールは**即座に有効**になり、選んだスコープ内で一致する操作は以後確認されません。

### 8.2 自動提案されるパターンの例

| 実際の操作 | 提案されるパターン |
|----------|----------------|
| `git add contents/docs/` | `git add *` |
| `.env.local` | `.env*` または `**/.env*` |

提案をそのまま使うか、**より制限的**（特定のサブコマンドだけ）にも**より緩く**（広い操作をまとめて）にも編集できます。

---

## 9. 他の機能との関係

| 機能 | 関係 |
|------|------|
| **Hooks** | フックの実行も権限モデルの対象。`.kiro/hooks/**` への書き込みは「常に確認」 |
| **Custom agents** | エージェントごとにインラインで権限を持てる。`.kiro/agents/**` への書き込みは「常に確認」 |
| **`.kiroignore`** | エージェントに見せないファイルの指定。書き込みは「常に確認」 |
| **Trusted commands** | **別の仕組み**（§6 の注記） |
| **Supervised モード** | **権限とは別物**。レビューのタイミングを変えるだけで、権限は Autopilot と同一（[03_deployment/05_security.md](../03_deployment/05_security.md)） |

---

## 関連ドキュメント

- [01_kiro-directory.md](01_kiro-directory.md) - `permissions.yaml` の置き場所
- [01_features/03_permissions.md](../01_features/03_permissions.md) - 権限の使い方（解説）
- [01_features/04_autopilot-supervised.md](../01_features/04_autopilot-supervised.md) - 2つのモード
- [03_deployment/05_security.md](../03_deployment/05_security.md) - 信頼するコマンド・保護されるパス
- [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) - 0.x からの移行
