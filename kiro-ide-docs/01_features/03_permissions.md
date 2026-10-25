# Permissions（権限）

**エージェントに何を許すかを、1つのルールで全ツールに効かせる仕組みです。1.0 の中核機能です。**

- **一次情報**: [Permissions](https://kiro.dev/docs/permissions/)（公式ページ更新日: 2026-10-20。§6 の Kiro スコープと信頼していないワークスペースの記述は、この更新版で確認）・[Local command sandbox](https://kiro.dev/docs/sandbox/)（公式ページ更新日: 2026-10-15。§10 の出典）
- **辞書的な一覧**: [04_reference/03_permissions.md](../04_reference/03_permissions.md)（capability 15種・書式・既定の挙動）
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

> **1.0.337での改善**: Kiroが保存済みルールが機能すると検証できないコマンドでは、**Always allow** と **Always deny** を表示せず、理由をプロンプトに示します。解析できるコマンドの永続化方法は変わりません。

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

> **例外: `sandbox_network`**（ローカルコマンドのサンドボックスのホスト規則）。この capability は deny が常に勝つ方式ではなく、**先に一致した規則が決める**方式です（公式 Permissions ページ）。詳細は [§10](#10-ローカルコマンドのサンドボックス13-で追加) を参照してください。

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

**ハードコードされた不変条件**があり、利用者も管理者も上書きできません（公式 Permissions ページ・2026-10-20 更新版）。

| 効果 | 主な対象 |
|------|---------|
| **常に拒否** | `~/.kiro/settings/`・`.kiro/settings/`・`~/.kiro/workspace-roots/` への書き込み（**エージェントが自身の権限ファイルを書き換えるのを防ぐ**）。インストール済み Power の MCP 構成や Kiro 自身の状態ストアも含む |
| **常に確認** | `.git/**`・`.vscode/**`・`**/*.code-workspace`・`.kiroignore`、および `.kiro` と `~/.kiro` の `agents`・`hooks`・`workflows`・`powers` ディレクトリへの書き込み |
| **信頼していない間だけ確認** | `.kiro/steering`・`.kiro/skills`・`.kiro/extensions` などへの書き込み |

**「エージェントに権限を緩めさせる」ことは構造上できません。** 全パスの一覧は [04_reference/03_permissions.md](../04_reference/03_permissions.md#71-kiro-スコープの不変条件上書き不可) を参照してください。

### 6.1 信頼していないワークスペース（1.2.4 で強化）

クローンしたリポジトリには、エージェントの振る舞いを変える入力（カスタムエージェント・Steering・MCP 構成・Skills・Workflow ファイル）が含まれ得ます。**Kiro はワークスペースを信頼するまで、これらを読み込みません。** さらに信頼していない間は、**以前に許可したコマンドでも、シェルコマンドの実行前に毎回確認します**（MCP ツールの呼び出し・Power の利用も同様）。

全項目は [04_reference/03_permissions.md](../04_reference/03_permissions.md#72-信頼していないワークスペースworkspace-trust) を参照してください。

公式の現行ページ（2026-10-20）は、信頼していない間の動作として次も挙げています。`~/.kiro/memories/` のメモリのデータベースと、エージェントのセッションストア（既定は `~/.kiro/sessions/`）への書き込みは、確認なしで拒否されます。また、エージェントはメモリ・ナレッジベース・リモートのラーニングを追加・変更・削除できません（読み取りはできます）。メモリの機能は [02_chat.md §16](02_chat.md#16-memory140-で追加) を参照してください。

---

## 7. パターンの書き方が capability で違う（つまずきどころ）

| 系統 | 使える記法 |
|------|----------|
| **ファイルシステム系**（`fs_read`・`fs_write`） | `*`（1つのパス要素内）・**`**`（パス区切りをまたぐ）**・`{a,b}`・`[abc]` |
| **シェル・Web・MCP 系** | **`*` のみ**（`**`・`?`・文字クラスは**非対応**） |

**シェルのパターンで `**` は使えません。** ファイルシステム系のほうが表現力が高いことを覚えておいてください。

また、ファイルシステム系では**ワイルドカードのないパターンが暗黙的に子も一致**します（`~/temp` は `~/temp/child` に一致）。

**1.0.337での評価改善**: `src/`・`src/**`のようなディレクトリパターンは、ディレクトリ自身とその子孫を対象にします。絶対パスと`~/`で始まるパターンも正しく一致し、ファイルを変更するコードアクションは`fs_write`の権限で評価されます。

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
| **ローカルコマンドのサンドボックス** | 権限が許可したシェルコマンドの**到達範囲を OS の仕組みで限定**する別の層（[§10](#10-ローカルコマンドのサンドボックス13-で追加)） |
| **`.kiroignore`** | **権限とは別の仕組み**。エージェントに見せないファイルを指定する（[04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#10-無視ファイル--kiroignore)） |
| **Autopilot / Supervised** | **権限とは別物**。レビューのタイミングを変えるだけで、**権限は両モードで同一**（[04_autopilot-supervised.md](04_autopilot-supervised.md)） |

---

## 10. ローカルコマンドのサンドボックス（1.3 で追加）

**エージェントが実行するシェルコマンドの周りに、OS レベルの境界を加える機能です。** 各コマンドとその子プロセスが到達できる範囲を限定しますが、エージェント本体をサンドボックスに入れるものではありません。**Kiro IDE 1.3 以降で利用でき、既定はオフです**（公式 [Local command sandbox](https://kiro.dev/docs/sandbox/)・[1.3.0](../02_update/01_changelog.md#v1-3-0)）。

**権限との関係**: シェルコマンドを開始する前に、[権限](#1-何が変わったのか)が実行してよいかを決めます。サンドボックスは、そのうえで実行中のコマンドと子プロセスが到達できる範囲を限定します。

| 範囲 | 対象（公式） |
|------|------------|
| **サンドボックスの内側** | エージェントが実行するターミナルコマンドと、それらが起動するすべての子プロセス。`mcpSandboxing` を有効にしたときは stdio MCP サーバのプロセス |
| **サンドボックスの外側** | エージェント本体とモデルとの会話。組み込みのファイルツール（読み書きできる範囲は引き続き権限ルールが制御する）。リモートの HTTP／SSE MCP サーバ（そのネットワーク通信はサンドボックスの規則に従わない） |

サンドボックスが適用されるのは**自分のマシンで動くセッションだけ**です。クラウドセッションは、管理されたクラウドのサンドボックスを別に使います（[12_cloud-sessions.md](12_cloud-sessions.md)）。

> ⚠️ **サンドボックスは、コマンドにできることを減らすものであって、隔離を保証するものではありません**（公式）。提案されたコマンドのレビューを続け、決して実行させたくない操作には deny ルールを残してください。

### 10.1 プラットフォームごとの要件

| プラットフォーム | 要件（公式） |
|--------------|------------|
| macOS | なし。`sandbox-exec` 経由で組み込みの Seatbelt サンドボックスを使う |
| Linux | `PATH` 上の Bubblewrap（`bwrap`）。Kiro はインストールしない。`COMMON_DEPENDENCIES` と、許可ホストを伴う `DEFAULT_BLOCKED` には `socat` も必要。どちらもディストリビューションのパッケージマネージャーでインストールする |
| Windows | `COMMON_DEPENDENCIES` または `DEFAULT_ALLOWED` でコマンドを実行する前に、**管理者によるセットアップが1回**必要。Kiro IDE が案内する。`DEFAULT_BLOCKED` はセットアップの前から動く |

プラットフォームのバックエンドがないとき、Kiro はサンドボックスを利用不可として報告します。現在のモードが保護を必須としていなければ、コマンドは OS による隔離なしで実行されます。

### 10.2 使い方

1. ステータスバーの **Command sandbox** を選びます。Kiro が有効な設定ファイルを開きます（プロジェクトのファイルがあればそれ、なければグローバルのファイル）。どちらも存在しないときは、`{"enabled": false}` を含むグローバルのファイルを作成します。
2. グローバルのファイルを直接開くには、コマンドパレットから **Open User Sandbox Config (JSON)** を実行します。
3. `enabled` を `true` にして、ネットワークのモードを選びます。

```json
{
  "enabled": true,
  "networkAccess": "COMMON_DEPENDENCIES"
}
```

保存すると、有効な変更は実行中のセッションに適用されます。ステータスバーは **Applying**、続いて **Active** を表示します。

| 状態 | 意味（公式） |
|------|------------|
| **Off** | サンドボックスを有効にする設定がない |
| **Active** | コマンドが現在のサンドボックスとネットワークモードを使う |
| **Applying** | 設定の変更を適用中 |
| **Error** | 変更に失敗した。以前の設定は有効なまま |
| **Unavailable** | プラットフォームのバックエンドがない。コマンドは OS による隔離なしで実行される |

要求した MCP のラップが利用できない場合は、ツールチップにも表示されます。

### 10.3 設定ファイル

| 範囲 | パス（IDE） | 用途（公式） |
|------|-----------|------------|
| グローバル | `~/.kiro/settings/sandbox.json` | プロジェクトをまたぐ既定のポリシー |
| プロジェクト | `<workspace-root>/.kiro/settings/sandbox.json` | 1つのリポジトリでサンドボックスを有効にする、または絞り込む |

マルチルートの IDE ワークスペースでは、**最初のワークスペースフォルダ**だけがプロジェクトのファイルを供給します。

| キー | 必須 | 値 | 既定 |
|------|------|-----|------|
| `enabled` | はい | `true`・`false` | なし |
| `networkAccess` | いいえ | `DEFAULT_BLOCKED`・`COMMON_DEPENDENCIES`・`DEFAULT_ALLOWED` | `DEFAULT_BLOCKED` |
| `mcpSandboxing` | いいえ | `true`・`false` | `false` |

`networkAccess` の値は**大文字小文字を区別**します。未知のキーは無視されます。

**グローバルとプロジェクトの組み合わせ**:

- グローバルのポリシーが有効なとき、プロジェクトのファイルはそれを**絞り込むことだけ**ができます。プロジェクトは `enabled` を `false` にすること、より開いたネットワークモードを選ぶこと、グローバルで有効な MCP のラップを無効にすることができません。
- グローバルのファイルがない、または `enabled: false` のとき、`enabled: true` のプロジェクトのファイルは、そのプロジェクトでサンドボックスを有効にします。

クローンしたリポジトリのプロジェクトファイルで、ネットワークアクセスを開いたり、有効なグローバルのサンドボックスポリシーを無効にしたりすることはできません。

### 10.4 ネットワークのモード

`networkAccess` は、サンドボックス内のコマンドの外向きネットワークアクセスの出発点を決めます。`sandbox_network` の権限ルールがそれを調整します。

| モード | 外向きネットワーク（公式） |
|--------|------------------------|
| `DEFAULT_BLOCKED`（既定） | ブロック。`sandbox_network` ルールが許可したホストを除く |
| `COMMON_DEPENDENCIES` | よく使われるパッケージ・ソース・ビルド・コンテナのサービスに到達できる。他のホストは、ルールが許可しない限りブロック |
| `DEFAULT_ALLOWED` | 開放。サンドボックス内のコマンドはどのホストにも到達できる。このモードでは `sandbox_network` の deny ルールに頼らない |

最も厳しいネットワーク制御には `DEFAULT_BLOCKED` を使い、インストールやビルドで共通の開発サービスが必要なときは `COMMON_DEPENDENCIES` を使い、`DEFAULT_ALLOWED` はネットワークのフィルタリングが不要なときだけ使う、と公式は案内しています。

**特定のホストを許可する**: `sandbox_network` は[権限の capability](../04_reference/03_permissions.md) です。ホストの規則は**順に適用され、最初に一致した規則が決めます**（他の capability では deny が常に勝つのと異なります）。特定のホストの規則は、それにも一致する広いワイルドカードの**前**に置きます。パターンは大文字小文字を区別せず、完全一致のホスト名と `*.suffix` 形式のワイルドカードに対応します。

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

ワークスペースの規則（`~/.kiro/workspace-roots/<hash>/permissions.yaml`）も、1つのプロジェクトについて同じように働きます。

`sandbox_network` は **`all` メタ capability に含まれません**。`capability: all`・`effect: allow` を書いても、サンドボックスのネットワークアクセスは開きません。`fs_read` と `fs_write` のルールも、サンドボックス内のコマンドが見られる・書けるパスを決めます。

### 10.5 stdio MCP サーバのラップ

`mcpSandboxing` を `true` にすると、stdio MCP サーバのプロセスを、シェルコマンドと同じサンドボックス内で起動します。

```json
{
  "enabled": true,
  "networkAccess": "DEFAULT_BLOCKED",
  "mcpSandboxing": true
}
```

リモートの HTTP／SSE MCP サーバは影響を受けません。`mcpSandboxing` を変更するとローカルの MCP サーバが再起動し、約1分かかることがあります。あるサーバでラップに失敗した場合も、コマンドのサンドボックスは有効なままで、Kiro はそのサーバが対象外であることを報告します。プロジェクトは、グローバルで有効な MCP のラップを無効にできません。MCP 全般は [08_mcp.md](08_mcp.md) を参照してください。

### 10.6 うまくいかないとき（IDE に関係するもの）

| 症状 | 確認すること（公式） |
|------|------------------|
| コマンドがホストに到達できない | `sandbox_network` の allow ルールを追加する。よく使われる開発サービスなら `COMMON_DEPENDENCIES` も使える |
| サンドボックスが利用不可 | Linux では `bwrap` が `PATH` にあるか確認する。プロキシのフィルタリングが必要なときは `socat` をインストールする。Windows では管理者セットアップを完了する。原因を直すまでコマンドは OS による隔離なしで実行される。直したあとは IDE のウィンドウを再読み込みする |
| Windows が `COMMON_DEPENDENCIES` または `DEFAULT_ALLOWED` を拒否する | IDE の案内から1回限りのセットアップを完了する。セットアップの前でも `DEFAULT_BLOCKED` は使える |
| MCP サーバが対象外と報告される | 1つ以上の stdio サーバでラップに失敗した。シェルコマンドのサンドボックスは有効なまま。サーバのコマンドと MCP のログまたは状態を確認する。`mcpSandboxing` の値を変えて保存するとローカルの MCP サーバが再起動する |
| ステータスバーが **Error** を表示する | ファイルが不正または読めない、あるいは Kiro が変更を適用できなかった。以前の設定は有効なまま。JSON を直して保存し直す。Kiro が **Reload Window** を提示したら使う |

> 公式は Windows の管理者セットアップの画面の詳細までは記述していません。本サイトでは画面の見え方を扱いません。

---

## 関連ドキュメント

- [04_reference/03_permissions.md](../04_reference/03_permissions.md) - capability 15種・全フィールドの一覧
- [04_autopilot-supervised.md](04_autopilot-supervised.md) - Autopilot / Supervised との違い
- [03_deployment/05_security.md](../03_deployment/05_security.md) - 信頼するコマンド・保護されたパス
- [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) - 0.x からの移行
