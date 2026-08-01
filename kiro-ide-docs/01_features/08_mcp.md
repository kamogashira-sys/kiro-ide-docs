# MCP（Model Context Protocol）

**外部のサーバに接続して、ツール・プロンプト・リソースを Kiro に追加する仕組みです。**

- **一次情報**: [MCP](https://kiro.dev/docs/mcp/)・[Configuration](https://kiro.dev/docs/mcp/configuration/)・[Tools](https://kiro.dev/docs/mcp/usage/)・[Best practices（security）](https://kiro.dev/docs/mcp/security/)
- **設定ファイル**: [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#8-mcp-サーバ定義--kirosettingsmcpjson)

> **これは何か**: MCP は Kiro が外部サーバと通信して、専門的なツール・プロンプト・リソースにアクセスするためのプロトコルです。
> 公式の例: **AWS Documentation MCP サーバ**は、AWS のドキュメントを Kiro 内で検索・読み取り・推薦するツールを提供します。

**MCP でできること（公式）**:

- 専門的な知識ベースとドキュメントにアクセスする
- 外部のサービスや API と統合する
- ドメイン固有のツールで Kiro の能力を拡張する
- **サーバが提供するプロンプトテンプレートとリソーステンプレート**を、チャットの `#` メンション経由で使う
- **サーバの elicitation 要求に応答する**（ツール実行中に追加の入力が必要になったとき）
- 自分のワークフロー向けのカスタムツールを作る

---

## 1. 使い始める

### 1.1 前提

| # | 条件 |
|---|------|
| 1 | 最新版の Kiro がインストールされている |
| 2 | 使いたい MCP サーバごとの前提条件（各サーバのドキュメントに記載） |

### 1.2 MCP を有効化する

設定ファイルを作ったあと、次の操作が必要です。

| 順 | 操作 |
|----|------|
| 1 | 設定を開く（`Cmd+,` / `Ctrl+,`） |
| 2 | **"MCP"** を検索する |
| 3 | **MCP サポートの設定を有効にする** |

---

## 2. 設定ファイル

### 2.1 置き場所

| 階層 | 場所 | 適用範囲 |
|------|------|---------|
| **ワークスペース** | `.kiro/settings/mcp.json` | 現在のワークスペースのみ |
| **ユーザー** | `~/.kiro/settings/mcp.json` | すべてのワークスペース |

> **両方が存在する場合、設定はマージされ、ワークスペース側が優先されます。**

**作り方**:

| 方法 | 操作 |
|------|------|
| **コマンドパレット** | `Cmd+Shift+P` / `Ctrl+Shift+P` → **Kiro: Open workspace MCP config (JSON)** または **Kiro: Open user MCP config (JSON)** |
| **Kiro パネル** | **Open MCP Config** アイコンを選ぶ |

### 2.2 形式

```json
{
  "mcpServers": {
    "local-server-name": {
      "command": "command-to-run-server",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR1": "hard-coded-variable",
        "ENV_VAR2": "${EXPANDED_VARIABLE}"
      },
      "disabled": false,
      "autoApprove": ["tool_name1", "tool_name2"],
      "disabledTools": ["tool_name3"]
    },
    "remote-server-name": {
      "url": "https://endpoint.to.connect.to",
      "headers": {
        "HEADER1": "value1",
        "HEADER2": "value2"
      },
      "oauth": {
        "clientId": "your-app-client-id"
      },
      "oauthScopes": ["scope1", "scope2"],
      "disabled": false,
      "autoApprove": ["tool_name1", "tool_name2"],
      "disabledTools": ["tool_name3"]
    }
  }
}
```

### 2.3 ローカルサーバのプロパティ

| プロパティ | 型 | 必須 | 内容 |
|-----------|----|-----|------|
| **`command`** | String | **必須** | MCP サーバを起動するコマンド |
| **`args`** | Array | **必須** | コマンドに渡す引数 |
| `env` | Object | 任意 | サーバプロセスの環境変数 |
| `disabled` | Boolean | 任意 | サーバを無効にするか（既定 `false`） |
| **`autoApprove`** | Array | 任意 | **確認なしで自動承認するツール名**（`"*"` で全ツール） |
| **`disabledTools`** | Array | 任意 | **エージェント呼び出し時に除外するツール名** |

### 2.4 リモートサーバのプロパティ

| プロパティ | 型 | 必須 | 内容 |
|-----------|----|-----|------|
| **`url`** | String | **必須** | リモート MCP サーバの **HTTPS** エンドポイント（localhost の場合は HTTP も可） |
| `headers` | Object | 任意 | 接続時に渡すヘッダ |
| `env` | Object | 任意 | サーバプロセスの環境変数 |
| `oauth` | Object | 任意 | 事前登録クライアントが必要なサーバ向けの OAuth 設定 |
| `oauth.clientId` | String | 任意 | **動的クライアント登録（DCR）に対応しないサービス**向けの、事前登録された OAuth クライアント ID |
| `oauth.redirectUri` | String | 任意 | ローカルの OAuth コールバックリスナのホストとポート（例: `"127.0.0.1:8080"`）。**Kiro が完全なリダイレクト URI を組み立てる**。省略時はランダムなポートが使われる |
| `oauthScopes` | Array | 任意 | 認可時に要求する OAuth スコープ |
| `disabled` | Boolean | 任意 | サーバを無効にするか（既定 `false`） |
| `autoApprove` | Array | 任意 | 自動承認するツール名 |
| `disabledTools` | Array | 任意 | 除外するツール名 |

### 2.5 環境変数

多くの MCP サーバは認証や設定のために環境変数を必要とします。**`${...}` 構文で実行時に展開されます。**

```json
{
  "mcpServers": {
    "server-name": {
      "env": {
        "API_KEY": "${YOUR_API_KEY}",
        "DEBUG": "true",
        "TIMEOUT": "30000"
      }
    }
  }
}
```

**設定例**（Brave Search）:

```json
{
  "mcpServers": {
    "web-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-bravesearch"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

> ⚠️ **API キーを設定ファイルに直接書かないでください**（公式のセキュリティ指針）。
> 環境変数として渡します。**`mcp.json` はバージョン管理に入る可能性がある**ためです。

---

## 3. サーバとツールの管理

### 3.1 MCP servers タブ

Kiro パネルの **MCP servers** タブで確認できます。

| 表示されるもの |
|-------------|
| 設定済みのすべての MCP サーバ |
| **接続状態のインジケータ** |
| サーバのツールへの素早いアクセス |

アクティビティバーの Kiro アイコン → **MCP servers** タブで開きます。**ツール名をクリックすると、チャットにプレースホルダのプロンプトが挿入されます。**

### 3.2 ツール単位の有効・無効

**サーバ全体に影響を与えずに、特定のツールだけを無効化できます。**

**パネルから**:

| 順 | 操作 |
|----|------|
| 1 | Kiro パネルで MCP servers へ移動する |
| 2 | サーバを展開してツール一覧を見る |
| 3 | ツールをクリックして **Enable** / **Disable** を選ぶ |

無効化されたツールには **"Disabled"** ラベルが付き、Kiro から使えなくなります。

**JSON から**（恒久的に無効化）:

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
      "disabledTools": ["delete_repository", "force_push", "merge_pull_request"]
    }
  }
}
```

**`disabledTools` が有用な理由（公式）**:

| 目的 | 内容 |
|------|------|
| **危険な操作を封じる** | 削除や force push など |
| **ツールの散らかりを減らす** | 使わないツールを隠す |
| **性能を上げる** | Kiro が検討するツールを絞る |
| **チームのポリシーを強制する** | ワークスペース設定を共有するとき |

### 3.3 サーバ単位の操作

MCP パネルでサーバを**右クリック**すると使えます。

| 操作 | 内容 |
|------|------|
| **Reconnect** | サーバへの接続を再起動する |
| **Disable** | サーバ全体を一時的に無効化する |
| **Disable All Tools** | このサーバのすべてのツールを一括で無効化する |
| **Enable All Tools** | 無効化していたツールをすべて再有効化する |
| **Show MCP Logs** | トラブルシューティング用の詳細ログを見る |

---

## 4. ツールの承認

**Kiro が MCP ツールを使おうとすると、まず承認を求めます。**

| 順 | 内容 |
|----|------|
| 1 | ツールとその目的を説明するプロンプトが出る |
| 2 | ツールの詳細とパラメータを確認する |
| 3 | **Approve**（実行を許可）または **Deny**（防ぐ）を選ぶ |

### 4.1 自動承認（`autoApprove`）

信頼するツールの繰り返しの確認を避けられます。

```json
{
  "mcpServers": {
    "aws-docs": {
      "autoApprove": [
        "mcp_aws_docs_search_documentation",
        "mcp_aws_docs_read_documentation"
      ]
    }
  }
}
```

保存（`Cmd+S`）すると自動的に反映されます。

**自動承認してよいツールの条件（公式）**:

| # | 条件 |
|---|------|
| 1 | **機密システムへの書き込み権限を持たない** |
| 2 | **信頼できる出所**で、コードが検証されている |
| 3 | ワークフローで**頻繁に使う** |
| 4 | **アクセスできる範囲が限定的**である |

**承認時に確認すること（公式）**: 各ツール要求を注意深くレビューする／**渡されるパラメータを確認する**／承認前にそのツールが何をするか理解する／**現在の作業と合わない不審な要求は拒否する**。

> **権限モデルからも制御できます。** `mcp` capability は `server/tool` の形式でパターン指定でき、
> `deny` で特定のサーバやツールを拒否できます（[04_reference/03_permissions.md](../04_reference/03_permissions.md)）。
> `autoApprove` は MCP 側の仕組み、権限は Kiro 全体の仕組みです。

---

## 5. `#` から使える3つのもの

MCP サーバはツール以外も提供できます。いずれも**チャットの `#` メンション一覧に MCP アイコン付きで現れます**（[04_reference/04_context-providers.md](../04_reference/04_context-providers.md)）。

### 5.1 MCP プロンプト（プロンプトテンプレート）

サーバが提供する**再利用可能なプロンプトテンプレート**です。引数を埋めてカスタマイズできます。

| 順 | 操作 |
|----|------|
| 1 | チャット入力欄で **`#`** を打つ |
| 2 | 接続済みサーバの MCP プロンプトが一覧に現れる |
| 3 | プロンプトを選んでメッセージに挿入する |

**引数がない場合**は解決された内容が直接挿入されます。**引数が必要な場合**はインラインのフォームが現れ、パラメータを埋めてから追加されます（公式の例: `code_review` プロンプトに必須の `code` 引数と任意の `language` 引数）。

> **プロンプトは常に利用者が起点です。** Kiro が利用者の選択なしにサーバへプロンプトを送ることはありません。
> **利用可能なプロンプトの一覧は、サーバが追加・削除すると自動更新されます。**

### 5.2 MCP リソーステンプレート

**パラメータ化された URI テンプレート**で、特定の内容に解決されます。

| 順 | 操作 |
|----|------|
| 1 | チャット入力欄で **`#`** を打つ |
| 2 | リソーステンプレートが一覧に現れる |
| 3 | テンプレートを選んで引数のフォームを見る |
| 4 | パラメータを入力して送信すると、**Kiro が URI を解決**して内容をコンテキストに含める |

### 5.3 MCP elicitation（実行中の追加入力）

**ツール実行中にサーバが追加の情報を必要とする場合**、失敗したり推測したりせずに**利用者に直接尋ねます**。

**フォーム形式**:

| フィールド型 | 表示 |
|-----------|------|
| Text | テキスト入力（email や date などの形式ヒントが付くことがある） |
| Number | 数値入力 |
| Yes/No | チェックボックス |
| Choice | 選択ドロップダウン |

必須フィールドには印が付き、サーバが既定値を提供した場合は事前入力されます。**送信・拒否・却下**が選べます。拒否・却下した場合、**サーバがどう進めるかを決めます**（代替を提示するか、その段階を飛ばすか）。

**URL 形式**: サーバが外部 URL の訪問を要求する場合（OAuth 認可フローの完了など）、Kiro は実行タイムラインに URL と **Open** ボタンを表示します。外部の操作を終えるとツールの実行が続きます。

> ⚠️ **セキュリティ上の注意**（公式）: Kiro は**どのサーバがどんなデータを要求しているか**を常に表示します。
> **いつでも拒否できます。**
> **サーバは elicitation でパスワードのような機密情報を要求すべきではありません**
> — そのような要求を見たら、そのサーバを信頼できるか考えてください。

---

## 6. ワークスペース分離（推奨される構成）

**プロジェクト固有の MCP サーバはワークスペースレベルで設定します。**

```
project-a/
├── .kiro/
│   └── settings/
│       └── mcp.json  # プロジェクト A 固有のサーバ
project-b/
├── .kiro/
│   └── settings/
│       └── mcp.json  # プロジェクト B 固有のサーバ
```

これにより次のことが保証されます（公式）:

| 効果 |
|------|
| **関連するプロジェクトで作業しているときだけ MCP サーバが動く** |
| **トークンと設定がプロジェクト間で分離される** |
| **セキュリティリスクが特定のワークスペースに封じ込められる** |

---

## 7. 組織で制限する

管理者は MCP を**完全に無効化**するか、**MCP レジストリで審査済みサーバの許可リスト**を指定できます。組織レベルで設定し、アカウント単位で上書きできます。

詳細は [03_deployment/04_enterprise.md](../03_deployment/04_enterprise.md#4-ガバナンス利用できる機能の制限) を参照してください。

---

## 8. 覚えておくべき点

| # | 注意点 |
|---|-------|
| 1 | **`mcp.json` は保護されたパス**です。エージェントが書き換えようとすると必ず確認が求められます（ベース名の完全一致） |
| 2 | **MCP はサブエージェント内でもメインエージェントと同じように動きます**（[02_chat.md](02_chat.md#73-サブエージェントで使えるもの使えないもの)） |
| 3 | **カスタムエージェントのプロファイルに MCP サーバをインラインで書けます**（[07_custom-agents.md](07_custom-agents.md#5-mcp-サーバをインラインで定義する)） |
| 4 | **1.0.116（2026-07-09）で MCP の遅延認証が入りました**（認証が必要なサーバは使うまで認証を求めない） |
| 5 | ファイアウォール環境では `github.com` と `raw.githubusercontent.com` の許可が必要な場合があります（[03_deployment/05_security.md](../03_deployment/05_security.md#45-機能を使う場合だけ必要な-url)） |

---

## 関連ドキュメント

- [07_custom-agents.md](07_custom-agents.md) - エージェントプロファイルへの MCP のインライン定義
- [02_chat.md](02_chat.md) - サブエージェントでの MCP
- [03_permissions.md](03_permissions.md) - `mcp` capability による制御
- [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) - `mcp.json` の置き場所
- [04_reference/04_context-providers.md](../04_reference/04_context-providers.md) - `#mcp` での参照
- [03_deployment/04_enterprise.md](../03_deployment/04_enterprise.md) - MCP ガバナンス
