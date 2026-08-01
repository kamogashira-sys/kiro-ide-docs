# Custom Agents（カスタムエージェント）

**目的に特化したエージェントを Markdown ファイル1枚で作り、チームで共有できます。1.0 で導入されました。**

- **一次情報**: [Custom agents](https://kiro.dev/docs/custom-agents/)（公式ページ更新日: 2026-07-01）・[Switching agents](https://kiro.dev/docs/custom-agents/agent-selector/)
- **ファイルの置き場所**: [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#6-カスタムエージェント--kiroagentsmd)
- **導入バージョン**: **1.0**（2026-06-25）

> **これは何か**: Markdown ファイルを書き、`read`・`write`・`shell` のような**タグ**で使えるツールの
> カテゴリを宣言し、MCP サーバと権限ルールをインラインに埋め込んで、**バージョン管理でチームに共有**します。
> **保存した瞬間にエージェントセレクタに現れます。**
>
> **Kiro CLI 版の対応ページ**: [`docs/cli/v3/agent-config`](https://kiro.dev/docs/cli/v3/agent-config)（CLI 3.0 Early Access）。
> **CLI 2.x は JSON 形式**の別仕様です。

---

## 1. Markdown 形式

**設定は YAML front matter に、システムプロンプトは本文に書きます。**

```markdown
---
description: Backend development agent
model: claude-sonnet-4
tools: [read, write, shell, web]
mcpServers:
  postgres:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-postgres"]
    env:
      DATABASE_URL: "${DATABASE_URL}"
permissions:
  rules:
    - capability: shell
      effect: allow
      match:
        - "npm *"
        - "node *"
---

You are a backend developer focused on Node.js and TypeScript.
Always use async/await. All database queries must be parameterized.
```

**1つのファイルにプロンプト・ツール・MCP サーバ・権限がすべて入る**のが特徴です。ファイルを渡せばエージェントを丸ごと共有できます。

---

## 2. ツールのタグ

`tools` フィールドは**カテゴリのタグ**を受け取り、そのカテゴリのツールをすべて含めます。

| タグ | 含まれるもの |
|------|-----------|
| **`read`** | ファイル読み取り・ディレクトリ一覧・検索 |
| **`write`** | ファイル書き込み・編集・削除 |
| **`shell`** | **コマンド実行とプロセス管理** |
| `web` | Web の取得 |
| `subagent` | サブエージェントへの委譲 |
| `context` | コンテキストとステアリングのツール |
| `@mcp` | **`mcp.json` のすべての MCP ツール** |
| `@builtin` | すべての組み込みツール |
| **`*`** | **すべて** |

> **カテゴリに新しいツールが追加されると、エージェントは自動的にそれを取り込みます。**
> ツール名を1つずつ列挙する方式より保守が楽になります。

---

## 3. ファイルの置き場所

| スコープ | 場所 | 特徴 |
|---------|------|------|
| **ワークスペース** | `.kiro/agents/` | **バージョン管理でチーム共有できる** |
| **ユーザー** | `~/.kiro/agents/` | すべてのプロジェクトで使える |

**ネストしたディレクトリに対応**します。エージェント名は agents ディレクトリからの相対パス（拡張子なし）です。

| ファイル | エージェント名 |
|---------|-------------|
| `~/.kiro/agents/team/planner.md` | **`team/planner`** |

> ⚠️ **ワークスペースのエージェントは、そのワークスペースが信頼されている場合のみ読み込まれます。**
> `.kiro/agents/` を持つワークスペースを初めて開くと、Kiro が信頼するかを確認します。
> **クローンしてきたリポジトリのエージェントが黙って動くことはありません。**

---

## 4. 権限をプロファイルに埋め込む

権限ルールを**エージェントプロファイルに直接**書けます。

```yaml
permissions:
  rules:
    - capability: builtin
      effect: allow
    - capability: shell
      effect: deny
      match:
        - "rm *"
        - "sudo *"
    - capability: filesystem
      effect: deny
      match:
        - ".env"
        - "secrets/**"
```

| 規則 | 内容 |
|------|------|
| **一致するルールがないとき** | **既定は `ask`** |
| **効果の解決** | **`deny` > `ask` > `allow`**（グローバルの権限と同じ） |

権限モデルの詳細は [03_permissions.md](03_permissions.md) と [04_reference/03_permissions.md](../04_reference/03_permissions.md) を参照してください。

> **エージェントごとに権限を絞れる**のが実用上の価値です。たとえば「レビュー専用エージェントは
> 読み取りだけ」「デプロイ用エージェントは特定のコマンドだけ」といった設計ができます。

---

## 5. MCP サーバをインラインで定義する

**エージェントプロファイルを完全に自己完結**させられます。

```yaml
mcpServers:
  local-server:
    command: npx
    args: ["-y", "@org/mcp-server"]
    env:
      API_KEY: "${API_KEY}"
    requestTimeout: 180000
  remote-server:
    url: https://api.example.com/mcp
    headers:
      Authorization: "Bearer ${TOKEN}"
```

| 項目 | 内容 |
|------|------|
| **環境変数** | **`${...}` 構文**で書き、**実行時に展開される** |
| **stdio サーバのタイムアウト** | `timeout`（接続のハンドシェイク・**既定 60 秒**）と `requestTimeout`（呼び出しごと・**既定 120 秒**） |
| **HTTP サーバ** | 認証が必要なエンドポイント用に **`headers`** に対応 |

MCP の詳細は [08_mcp.md](08_mcp.md) を参照してください。

---

## 6. エージェントの切り替え（Agent selector）

**会話履歴を失わずに、セッション内でエージェントを切り替えられます。**

セレクタは**チャット入力欄の行**（モデルピッカーの隣）にあり、**現在有効なエージェントの名前**を表示します。クリックするとドロップダウンが開きます。

### 6.1 出自でグループ分けされる

| グループ | 内容 |
|---------|------|
| **Built-in** | **Default・Spec・Quick Spec・Bug Fix・Plan** |
| **User** | `~/.kiro/agents/` のカスタムエージェント |
| **Workspace** | プロジェクトの `.kiro/agents/` のカスタムエージェント |

**組み込みエージェントは5種**です。Spec・Quick Spec・Bug Fix は [01_specs.md](01_specs.md) のワークフローに対応します。

選ぶと**次のメッセージから即座に**そのエージェントの設定に切り替わります。

### 6.2 切り替えたときに何が変わるか

| 対象 | 挙動 |
|------|------|
| **システムプロンプト** | 新しいエージェントのプロンプトに変わる |
| **使えるツール** | 新しいエージェントの `tools` 設定に切り替わる |
| **権限** | **ユーザーとワークスペースの権限は維持される** |
| **MCP サーバ** | **エージェントが定義したサーバが読み込まれ、共有サーバはそのまま残る** |
| **会話履歴** | **保持される。エージェントは以前のメッセージを見られる** |

> **履歴が引き継がれる**ので、「広く始めて、必要になったところで専門エージェントに絞り込む」
> という進め方ができます（公式が挙げる使い方）。

### 6.3 既定のエージェントを変える

選んだエージェントはそのセッションで有効になります。**常に特定のエージェントで新しいセッションを始めたい場合は、セレクタから既定に設定**できます。**この選択は再起動をまたいで保持され**、新しいチャットセッションは組み込みの既定ではなく好みのエージェントで開きます。

### 6.4 切り替えられないとき

> ⚠️ **エージェントが多段階のワークフローを実行中は、セレクタが無効になります。**
> **エージェントがアイドルで次のメッセージを待っているときだけ**切り替えられます。

---

## 7. サブエージェントとしての利用

**カスタムエージェントはサブエージェントとしても使えます。** Kiro はサブエージェントを起動するとき、**`description` フィールドをもとに適切な設定を自動選択**します。

| 呼び出し方 | 例 |
|----------|-----|
| 自動選択に任せる | （Kiro が `description` で判断する） |
| 自然言語で指定 | "Use the code-reviewer subagent to find performance issues in my code" |
| **スラッシュコマンド** | **`/code-reviewer find performance issues in my code`** |

サブエージェント固有の属性（`includeMcpJson`・`includePowers` など）と制約は [02_chat.md](02_chat.md#7-サブエージェント並列実行と委譲) にまとめています。

> **サブエージェント内では Specs にアクセスできず、Hooks も発火しません。**
> ステアリングと MCP はメインエージェントと同じように動きます。

---

## 8. 作る手順の例

「コードレビュー専用エージェント」を作る場合:

| 順 | 操作 |
|----|------|
| 1 | `~/.kiro/agents/code-reviewer.md` を作る（全プロジェクトで使う場合） |
| 2 | front matter に `description` を書く（**サブエージェントの自動選択に使われる**ので具体的に） |
| 3 | `tools` を絞る（レビューなら `[read, context]` など） |
| 4 | 必要なら `permissions` で書き込みを拒否する |
| 5 | 本文にシステムプロンプトを書く |
| 6 | 保存する（**即座にエージェントセレクタに現れます**） |

チームで共有したい場合は `~/.kiro/agents/` ではなく **`.kiro/agents/`** に置いてコミットします。

---

## 関連ドキュメント

- [02_chat.md](02_chat.md) - サブエージェント（`tools` の全指定・属性の一覧）
- [03_permissions.md](03_permissions.md) - 権限モデル
- [08_mcp.md](08_mcp.md) - MCP サーバの設定
- [01_specs.md](01_specs.md) - 組み込みの Spec / Quick Spec / Bug Fix エージェント
- [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) - `.kiro/agents/` の仕様
- [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) - 1.0 での導入
