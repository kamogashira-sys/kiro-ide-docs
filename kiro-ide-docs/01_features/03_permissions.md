# Permissions（権限）

**エージェントに何を許すかを、1つのルールで全ツールに効かせる仕組みです。1.0 の中核機能です。**

- **一次情報**: [Permissions](https://kiro.dev/docs/chat/permissions/)
- **辞書的な一覧**: [04_reference/03_permissions.md](../04_reference/03_permissions.md)（capability 14種・書式・既定の挙動）
- **導入バージョン**: **1.0**（2026-06-25）

> **本ページは使い方の解説です。** フィールドの一覧や capability の全種類は
> [04_reference/03_permissions.md](../04_reference/03_permissions.md) を引いてください。
>
> **Kiro CLI 版の対応ページ**: [`docs/cli/v3/permissions`](https://kiro.dev/docs/cli/v3/permissions)（CLI 3.0 Early Access）。
> **CLI 2.x は旧モデル**です。

---

## 1. 何が変わったのか

**エージェントが行うすべての操作に対する、単一の統一された権限モデル**です。公式の説明:

> ルールを1つ書けば `npm *` コマンドをすべてのセッションで許可できます。
> あるいは `.env` の読み取りを拒否すれば、**すべてのツールが同時にそれを守ります**。

0.x では機能ごとに承認の仕組みが分かれていましたが、1.0 でこれが1つにまとまりました。移行の詳細は [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) を参照してください。

---

## 2. 使い始め方: 設定ファイルを書かなくてよい

**最初にやることは何もありません。** 既定の状態でも動きます。

| 既定で許可されるもの | 内容 |
|-------------------|------|
| `fs_read` on `./**` | **ワークスペース内のあらゆるファイルを読める** |
| `shell`（読み取り専用の一般的なコマンド） | `git status`・`git log`・`git diff` など |
| ユーティリティツール | 診断・knowledge など |

**それ以外はすべて承認を求めます。**

そして**承認するたびにポリシーが育ちます**。公式の言い方では「視覚的な同意フローが、作業しながらポリシーを組み立てる」— プロンプトで許可か拒否を選び、パターンを選び、スコープを選ぶだけです。

---

## 3. 承認プロンプトの使い方

ツール呼び出しが `ask` と評価されると、チャットパネル上部にプロンプトが出ます。

| ボタン | 動作 |
|-------|------|
| **Allow** | この1回だけ許可 |
| **Always allow** | **保存ダイアログを開く**（allow ルールを保存） |
| **Deny** | この1回だけ拒否 |
| **Always deny** | 保存ダイアログを開く（deny ルールを保存） |

### 3.1 「Always」を選んだあとに決める2つのこと

**(a) Pattern（パターン）**

IDE が実際の操作から**一般化したパターンを自動提案**します。

| 実際の操作 | 提案されるパターン |
|----------|----------------|
| `git add contents/docs/` | `git add *` |
| `.env.local` | `.env*` または `**/.env*` |

**より制限的にも（特定のサブコマンドだけ）、より緩くも（広い操作をまとめて）編集できます。**

**(b) Apply to（保存先）**

| 選択肢 | 保存先 | 適用範囲 |
|-------|-------|---------|
| **All workspaces** | `~/.kiro/settings/permissions.yaml` | どこでも |
| **This workspace** | `~/.kiro/workspace-roots/<hash>/permissions.yaml` | **このプロジェクトのみ** |
| **This session** | メモリ上 | **セッション終了まで** |

確定するとルールは**即座に有効**になり、以後同じ操作では確認されません。

> **迷ったら This session を選ぶ**のが安全です。作業が終われば消えるので、後で見直せます。
> 定着したものだけを This workspace や All workspaces に昇格させる進め方ができます。

---

## 4. 設定ファイルで書く

ある程度パターンが固まったら、ファイルに書いたほうが見通しがよくなります。

`~/.kiro/settings/permissions.yaml`:

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

この例は「git・npm・npx は許可」「MCP は許可」「読み取りは許可」「書き込みは `src/` と `tests/` のみ許可」という意味です。

### 4.1 秘密情報を守る書き方

```yaml
rules:
  # どの深さにあっても秘密情報の読み取りを拒否
  - capability: fs_read
    effect: deny
    match:
      - "**/.env"
      - "**/.env.*"
      - "secrets/**"
      - "**/*.pem"
```

**`deny` は `allow` より強い**ので、「読み取りは全部許可」と書いていてもこの拒否が勝ちます。

### 4.2 例外を作る書き方

```yaml
rules:
  # npm publish 以外の npm コマンドを許可
  - capability: shell
    effect: allow
    match:
      - "npm *"
    exclude:
      - "npm publish*"
```

---

## 5. 覚えておくべき3つの性質

### 5.1 制限が強いほうが勝つ

**`deny` > `ask` > `allow`**

**より緩いルールが、より厳しいルールを上書きすることはできません。** 「あとに書いたほうが勝つ」ではありません。

### 5.2 複合コマンドは分割して評価される

シェルコマンドは**パターン照合の前に解析**され、`;`・`&&`・`||`・`|` で分割されて**サブコマンドごとに評価**されます。

これにより `npm test *` のルールが `npm test ; curl attacker.com` にうっかり一致することを防ぎます。

> **「信頼するコマンド」（Trusted Commands）とは別の仕組みです。** 設定の **Kiro Agent: Trusted Commands** は
> **単純な前方一致で構造を解析しません**。そちらは分割しないため、`npm *` を信頼すると連結コマンドも通ります。
> 詳細は [03_deployment/05_security.md](../03_deployment/05_security.md) を参照してください。

### 5.3 クローンしたリポジトリは権限を注入できない

**ワークスペースの権限はリポジトリの外に、利用者ごとに保存されます**（`~/.kiro/workspace-roots/<hash>/permissions.yaml`）。

リポジトリの中に `permissions.yaml` を置いても、それが読まれることはありません。**他人のリポジトリをクローンしても、勝手に権限が緩むことはない**という設計です。

---

## 6. 緩められない境界（Kiro スコープ）

**ハードコードされた不変条件**があり、利用者も管理者も上書きできません。

| 効果 | 対象 | 理由 |
|------|------|------|
| **常に拒否** | `~/.kiro/settings/`・`.kiro/settings/`・`~/.kiro/workspace-roots/` への書き込み | **エージェントが自身の権限ファイルを書き換えるのを防ぐ** |
| **常に確認** | `.git/**`・`.kiro/agents/**`・`.kiro/hooks/**`・`.kiroignore` への書き込み | 設定やエージェント定義の意図しない変更を防ぐ |

**「エージェントに権限を緩めさせる」ことは構造上できません。**

---

## 7. パターンの書き方が capability で違う（つまずきどころ）

| 系統 | 使える記法 |
|------|----------|
| **ファイルシステム系**（`fs_read`・`fs_write`） | `*`（1つのパス要素内）・**`**`（パス区切りをまたぐ）**・`{a,b}`・`[abc]` |
| **シェル・Web・MCP 系** | **`*` のみ**（`**`・`?`・文字クラスは**非対応**） |

**シェルのパターンで `**` は使えません。** ファイルシステム系のほうが表現力が高いことを覚えておいてください。

また、ファイルシステム系では**ワイルドカードのないパターンが暗黙的に子も一致**します（`~/temp` は `~/temp/child` に一致）。

---

## 8. 組織で使う場合

**Administration スコープ**（エンタープライズ／MDM 管理）があり、`deny` と `ask` を配布できます（`allow` は使えません）。

エンタープライズプラン限定です。設定の配布方法は [03_deployment/04_enterprise.md](../03_deployment/04_enterprise.md) を参照してください。

---

## 9. 他の機能との関係

| 機能 | 関係 |
|------|------|
| **Hooks** | フックの実行も権限モデルの対象（[05_hooks.md](05_hooks.md)） |
| **Custom agents** | エージェントごとにインラインで権限を持てる（[07_custom-agents.md](07_custom-agents.md)） |
| **MCP** | `mcp` capability で `server/tool` の単位で制御できる（[08_mcp.md](08_mcp.md)） |
| **`.kiroignore`** | **権限とは別の仕組み**。エージェントに見せないファイルを指定する（[04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#10-無視ファイル--kiroignore)） |
| **Autopilot / Supervised** | **権限とは別物**。レビューのタイミングを変えるだけで、**権限は両モードで同一**（[04_autopilot-supervised.md](04_autopilot-supervised.md)） |

---

## 関連ドキュメント

- [04_reference/03_permissions.md](../04_reference/03_permissions.md) - capability 14種・全フィールドの一覧
- [04_autopilot-supervised.md](04_autopilot-supervised.md) - Autopilot / Supervised との違い
- [03_deployment/05_security.md](../03_deployment/05_security.md) - 信頼するコマンド・保護されたパス
- [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) - 0.x からの移行
