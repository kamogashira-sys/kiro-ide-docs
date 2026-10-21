# 権限（Permissions）リファレンス

**エージェントに何を許すかを決める仕組みの辞書です。**

- **一次情報**: [Permissions](https://kiro.dev/docs/permissions/)（公式ページ更新日: 2026-10-20）・[Local command sandbox](https://kiro.dev/docs/sandbox/)（公式ページ更新日: 2026-10-15。`sandbox_network` の項目）
- **収録件数**: capability **15種**
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

> **例外は `sandbox_network` のホスト規則です。** `sandbox_network` は deny-overrides を使わず、**規則を順に適用して、最初に一致した規則が決めます**（§3・§5.4）。

---

## 2. ルールの置き場所（スコープ）

### 2.1 利用者が書くスコープ

| スコープ | 場所 | 使える効果 |
|---------|------|----------|
| **User**（全ワークスペース） | `~/.kiro/settings/permissions.yaml` | `deny` / `ask` / `allow` |
| **Workspace**（このプロジェクトのみ） | `~/.kiro/workspace-roots/<hash>/permissions.yaml` | `deny` / `ask` / `allow` |
| **Agent**（そのエージェントのみ） | **エージェントプロファイルの `permissions` フィールドに埋め込む** | `deny` / `ask` / `allow` |

> **ワークスペースの権限はリポジトリの外に、利用者ごとに保存されます**（`~/.kiro/workspace-roots/<hash(workspaceRoot)>/`）。
> これは重要な設計です — **クローンしてきたリポジトリが権限ルールを注入することはできません**。

> **Agent スコープ**は、エージェント定義そのものに権限を持たせる方法です。
> 書き方は [01_features/07_custom-agents.md](../01_features/07_custom-agents.md) の `permissions` フィールドを参照してください。

### 2.2 システムが管理するスコープ

| スコープ | 目的 | 使える効果 |
|---------|------|----------|
| **Kiro** | ハードコードされたセキュリティ不変条件（**上書き不可**） | `deny` / `ask` |
| **Administration** | エンタープライズで管理されるポリシー（**`managed-settings.json`**、エンタープライズプランのみ） | `deny` / `ask` |
| **Session** | IDE での承認判断から生まれるメモリ上のルール | `deny` / `ask` / `allow` |

**`allow` を持たないスコープがある**点に注意してください。Kiro スコープと Administration スコープは「制限を加える」ためのもので、緩めることはできません。

### 2.3 スコープ間に優先順位はない

**評価は deny-overrides アルゴリズムで行われ、スコープ同士の優劣はありません。**
どのスコープから来たルールであっても、**最も制限の強い効果が勝ちます**（`deny` > `ask` > `allow`）。

> ⚠️ **どのスコープの `deny` も、他のスコープの `allow` で上書きできません。**
> `deny` ルールは慎重に書いてください。

> **例外**: `sandbox_network` のホスト規則だけは、スコープをまたいで deny-overrides で決まらず、最初に一致した規則で決まります。順序で決まるため、`allow` が先にあれば、後ろの `deny` は効きません（§5.4）。

---

## 3. capability 一覧（15種）

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
| `skill` | **Skills** の有効化（可搬な指示パッケージ。置き場所は [01_kiro-directory.md](01_kiro-directory.md#7-agent-skills--kiroskills名前skillmd)・公式 [`/docs/skills`](https://kiro.dev/docs/skills/)） |
| `power` | **Powers** の有効化とツール呼び出し（MCP サーバ・ステアリング・フックのバンドルを動的に読み込む仕組み。[0.7 の導入時の説明](../02_update/02_changelog-0x.md#powers)・公式 [`/docs/powers`](https://kiro.dev/docs/powers/)） |
| `diagnostics` | 診断ツール |
| `context` | コンテキストおよびステアリングのツール |
| `sandbox_network` | **ローカルコマンドのサンドボックスが有効なときだけ適用される**。サンドボックス内のシェルコマンドが到達できるホストを、`allow` と `deny` のルールで指定する（公式 [Permissions](https://kiro.dev/docs/permissions/)・[Local command sandbox](https://kiro.dev/docs/sandbox/)）。**ホスト規則は順に適用され、最初に一致した規則が決める**（他の capability の `deny` 優先とは逆）。**`all` に含まれない**。使い方は §5.4・[01_features/03_permissions.md](../01_features/03_permissions.md#10-ローカルコマンドのサンドボックス13-で追加) |
| `all` | **`sandbox_network` を除くすべての capability**（メタ） |
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

**1.0.337での評価改善**: `src/`・`src/**`のようなディレクトリパターンは、ディレクトリ自身と子孫を対象にします。絶対パスと`~/`で始まるパターンは正しく一致し、ファイルを変更するコードアクションは`fs_write`で評価されます。

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

### 5.4 サンドボックスのホスト規則（`sandbox_network`）

`sandbox_network` の `match` にはホスト名を書きます（公式 [Local command sandbox](https://kiro.dev/docs/sandbox/)。公式ページ更新日: 2026-10-15）。

| 項目 | 内容 |
|------|------|
| 書けるもの | 完全一致のホスト名、`*.suffix` 形式のワイルドカード |
| 大文字・小文字 | 区別しない |
| 評価の順序 | **規則を書いた順に適用し、最初に一致した規則が決める**。特定のホストの規則は、それにも一致する広いワイルドカードの**前**に置く |
| `all` との関係 | `sandbox_network` は `all` に含まれない。`capability: all`・`effect: allow` を書いても、サンドボックスのネットワークアクセスは開かない |

```yaml
# ~/.kiro/settings/permissions.yaml
rules:
  - capability: sandbox_network
    match: ['packages.internal.example.com']
    effect: allow

  # この規則は、下のワイルドカードより前に置く
  - capability: sandbox_network
    match: ['uploads.example-corp.net']
    effect: deny

  - capability: sandbox_network
    match: ['*.example-corp.net']
    effect: allow
```

ワークスペースの規則（`~/.kiro/workspace-roots/<hash>/permissions.yaml`）も、1つのプロジェクトについて同じように働きます。`fs_read` と `fs_write` のルールは、サンドボックス内のコマンドが見られる・書けるパスも決めます。`networkAccess` の 3 つのモード（`DEFAULT_BLOCKED`・`COMMON_DEPENDENCIES`・`DEFAULT_ALLOWED`）は [01_features/03_permissions.md](../01_features/03_permissions.md#10-ローカルコマンドのサンドボックス13-で追加) にまとめています。

---

## 6. シェルコマンド固有の挙動（重要）

**シェルコマンドはパターン照合の前に解析されます。** `;`・`&&`・`||`・`|` を使った複合コマンドは分割され、**サブコマンドごとに個別に評価**されます。

これにより、`npm test *` のルールが `npm test ; curl attacker.com` にうっかり一致することを防ぎます。

パーサーは、まとめて書いた短いオプションの中のフラグも評価します。たとえば `grep -iP` のようなコマンドは、フラグの1つが承認を必要とするなら、確認が出ます。**別のプログラムを起動できるオプションは、読み取り専用として扱われません**。`tar --use-compress-program` と `tar --to-command` は、基本の `tar` コマンドを信頼していても承認が必要です（公式 [Permissions](https://kiro.dev/docs/permissions/)・公式ページ更新日: 2026-10-20）。

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
| `shell` | **よく使う読み取り専用の git コマンド**（`git status`・`git log`・`git diff`・`git branch` など） |
| `shell` | **システム情報のコマンド**（`pwd`・`whoami`・`uname` など） |
| ユーティリティツール | 診断・knowledge など |

**それ以外はすべて承認を求めます。** `permissions.yaml` を作ると、この既定に**追加**されます。

### 7.1 Kiro スコープの不変条件（上書き不可）

| 効果 | 対象 |
|------|------|
| **常に拒否** | `~/.kiro/settings/`・`.kiro/settings/`・`~/.kiro/workspace-roots/` への書き込み（**エージェントが自身の権限ファイルを書き換えるのを防ぐ**）<br>インストール済みの Power の MCP 構成（`~/.kiro/powers/installed/<name>/mcp.json`）への書き込み<br>Kiro 自身の状態ストア（`~/.kiro/sandbox-state/`・`~/.kiro/web-session/`・`~/.kiro/cloud-cache/`・`~/.kiro/sandbox-curl/`）への書き込み |
| **常に確認** | `.git/**`・`.vscode/**`・`**/*.code-workspace`・`.kiroignore`、および**ワークスペースの `.kiro` と `~/.kiro` の両方**の `agents`・`hooks`・`workflows`・`powers` ディレクトリへの書き込み。**信頼済み・信頼していないどちらのワークスペースでも確認**し、どのスコープの `allow` ルールでも確認は消えない |
| **信頼していない間だけ確認** | `.kiro/steering`・`.kiro/skills`・`.kiro/extensions`、および Kiro が宣言していない `.kiro` ディレクトリへの書き込み（§7.2） |

**「常に拒否」と「常に確認」は利用者も管理者も緩められません。** エージェントが権限設定そのものを書き換えられない仕組みになっています。

> **1.2.4 での変更**: 1.2.4 の changelog は、エージェント・フック・Power のファイルと `.kiro/workflows/` の Workflow レシピについて、
> より広いファイル権限で書き込みが許可されていても確認を求めると説明しています（[1.2.4](../02_update/01_changelog.md#v1-2-4)）。

### 7.2 信頼していないワークスペース（Workspace trust）

**開いたリポジトリの中には、エージェントの振る舞いを変える入力があります**（`.kiro/agents/` のカスタムエージェント・`.kiro/steering/` の Steering・ワークスペースの MCP サーバ構成・Skills・Workflow のファイル）。クローンしたリポジトリがこれらを使ってエージェントの振る舞いを変えられるため、**Kiro はワークスペースを信頼するまで「信頼していない」ものとして扱います**。信頼の判断はワークスペースの外に保存されるので、**リポジトリが自分の信頼状態を変えることはできません**。

**信頼するまでの間、Kiro は次のように動きます**（公式の全項目）:

| # | 挙動 |
|---|------|
| 1 | ワークスペースのカスタムエージェント・Steering ファイル・MCP サーバ構成・Skills を**読み込まない** |
| 2 | ワークスペースの Workflow ファイルを**読み込まない**（ホームやクラウドのレシピディレクトリからリンクで辿れるものも含む）。自分のホーム・クラウド・同梱・生成された Workflows は使える |
| 3 | **すべてのシェルコマンドの開始前に確認する**（バックグラウンドプロセスを含む）。保存済みのルールや広いルールが許可していても同じで、確認には完全なコマンドが表示される。一致する `deny` ルールがあれば拒否される |
| 4 | **すべての MCP ツール呼び出しの前、および Power の有効化・内容の読み取り・ツール呼び出しの前に確認する**。保存済みのルールや `autoApprove` が許可していても同じで、MCP の認証や URL の確認の後に再試行するときも再度確認する。一致する `deny` ルールがあれば拒否される |
| 5 | ワークスペースと `~/.kiro` の両方で、`.kiro/steering`・`.kiro/skills`・`.kiro/extensions`、および Kiro が宣言していない `.kiro` ディレクトリへの書き込みの前に確認する（`agents`・`hooks`・`workflows`・`powers` への書き込みは、どのワークスペースでも確認する） |
| 6 | `~/.kiro/memories/` のメモリデータベースと、エージェントのセッションストア（既定は `~/.kiro/sessions/`）への書き込みを、**確認なしで拒否する**（信頼していないセッションが他のセッションの状態を書き換えられないようにする） |
| 7 | エージェントがメモリ・ナレッジベース・リモートの学習内容を追加・変更・削除できない（読み取りはできる） |

利用者・管理・エージェント・セッションのルールはこの間も適用されます。`~/.kiro/workspace-roots/` のワークスペースごとのストアもリポジトリの外にあるため、信頼の有無にかかわらず読み込まれます。

> **信頼していない間だけの確認を外すルール**: 自分の `~/.kiro/settings/permissions.yaml` に、`match` の制限も `exclude` もない
> `fs_write` の `allow` ルールを置くと、`.kiro` ディレクトリへの「信頼していない間だけの確認」が外れます。
> ただし**常に確認するパスは外れず**、一致する `ask`・`deny` も上書きせず、上の表 #1・#2 の入力も読み込まれません。

> **ワークスペースを信頼する IDE の操作手順**は、公式 Permissions ページに記載がありません（**未確認**）。

---

## 8. IDE 上での承認フロー

ツール呼び出しが `ask` と評価されると、チャットパネル上部に権限プロンプトが出ます。

| ボタン | 動作 |
|-------|------|
| **Allow** | この1回だけ許可する |
| **Always allow** | 保存ダイアログを開き、allow ルールを保存する |
| **Deny** | この1回だけ拒否する |
| **Always deny** | 保存ダイアログを開き、deny ルールを保存する |

> **1.0.337での改善**: 保存済みルールが機能するとKiroが検証できないコマンドでは、**Always allow** と **Always deny** を表示せず、理由をプロンプトに示します。

連結したコマンド（例: `cd /path && cargo build`）は、チェーン内のサブコマンドが**それぞれ別に**承認を求められます（公式 [Permissions](https://kiro.dev/docs/permissions/)・公式ページ更新日: 2026-10-20）。

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
| **Supervised モード** | **権限とは別物**。レビューのタイミングを変えるだけで、権限は Autopilot と同一（[03_deployment/05_security.md](../03_deployment/05_security.md)）。公式は、権限の層は Agent Autonomy（設定キー `kiroAgent.agentAutonomy`）のモードが進めるかどうかを決めた**後に**適用される、と説明している |
| **ローカルコマンドのサンドボックス**（1.3 以降） | 権限が、シェルコマンドを実行してよいかを開始前に決める。サンドボックスは、実行中のコマンドと子プロセスが到達できる範囲を限定する。**ネットワークの到達先は `sandbox_network` ルールで調整する**（§3・§5.4）。`fs_read` と `fs_write` のルールも、サンドボックス内のコマンドが見られる・書けるパスを決める。サンドボックスは隔離を保証するものではない。詳細は [01_features/03_permissions.md](../01_features/03_permissions.md#10-ローカルコマンドのサンドボックス13-で追加) |

---

## 関連ドキュメント

- [01_kiro-directory.md](01_kiro-directory.md) - `permissions.yaml` の置き場所
- [01_features/03_permissions.md](../01_features/03_permissions.md) - 権限の使い方（解説）
- [01_features/04_autopilot-supervised.md](../01_features/04_autopilot-supervised.md) - 2つのモード
- [03_deployment/05_security.md](../03_deployment/05_security.md) - 信頼するコマンド・保護されるパス
- [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) - 0.x からの移行
