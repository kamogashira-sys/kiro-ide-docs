# `.kiro/` ディレクトリのファイル仕様

**Kiro の設定ファイルがどこに置かれ、どんな形式なのかをまとめた辞書です。**

- **一次情報**: [Specs](https://kiro.dev/docs/specs/)（公式ページ更新日: 2026-07-22）・[Hooks](https://kiro.dev/docs/hooks/)・[Steering](https://kiro.dev/docs/steering/)・[Custom agents](https://kiro.dev/docs/custom-agents/)・[MCP Configuration](https://kiro.dev/docs/mcp/configuration/)・[Permissions](https://kiro.dev/docs/permissions/)・[Kiroignore](https://kiro.dev/docs/kiroignore/)・[Agent Skills](https://kiro.dev/docs/skills/)・[Multi-root Workspaces](https://kiro.dev/docs/ide/editor/multi-root-workspaces/)

> **このページの方針**: 引くときにリンクを往復しなくて済むよう、**IDE 版で完結**して書いています。
> 各項目には Kiro CLI 版の対応ページも併記します。

---

## 1. 全体像

設定は **2つの階層**に分かれます。

| 階層 | 場所 | 適用範囲 |
|------|------|---------|
| **ワークスペース** | プロジェクトルートの `.kiro/` | そのプロジェクトのみ。**バージョン管理でチーム共有できる** |
| **ユーザー（グローバル）** | ホームディレクトリの `~/.kiro/` | すべてのワークスペース |

```
プロジェクトルート/
├── .kiro/
│   ├── specs/<機能名>/       # 仕様（requirements.md / design.md / tasks.md）
│   ├── steering/*.md          # ステアリング（エージェントへの指示）
│   ├── hooks/*.json           # フック（v1 JSON 形式）
│   ├── agents/*.md            # カスタムエージェント
│   ├── skills/<名前>/SKILL.md # Agent Skills
│   └── settings/
│       └── mcp.json           # MCP サーバ定義（ワークスペース）
└── .kiroignore                # エージェントに読ませないファイル

~/.kiro/
├── steering/*.md              # ステアリング（全ワークスペース）
├── hooks/*.json               # フック（全ワークスペース・1.0.182 で追加）
├── agents/*.md                # カスタムエージェント（全ワークスペース）
├── skills/<名前>/SKILL.md     # Agent Skills（全ワークスペース）
├── settings/
│   ├── mcp.json               # MCP サーバ定義（ユーザー）
│   ├── permissions.yaml       # 権限ルール（全ワークスペース）
│   └── kiroignore             # グローバルな無視パターン（拡張子なし）
└── workspace-roots/<hash>/
    └── permissions.yaml       # 権限ルール（そのワークスペースのみ）
```

**注意すべき2点**:

1. **ワークスペースの権限だけはリポジトリの外**（`~/.kiro/workspace-roots/<hash>/`）に置かれます。クローンしたリポジトリが権限を注入できないようにするためです。
2. **`.kiroignore` は `.kiro/` の中ではなくプロジェクトルート**に置きます。グローバル版は `~/.kiro/settings/kiroignore`（**先頭のドットも拡張子もない**）です。

---

## 2. 一覧表

| 用途 | ワークスペース | ユーザー（グローバル） | 形式 | CLI 版の対応ページ |
|------|--------------|------------------|------|-----------------|
| **仕様（Specs）** | `.kiro/specs/<機能名>/` | — | Markdown | — |
| **ステアリング** | `.kiro/steering/*.md` | `~/.kiro/steering/*.md` | Markdown＋YAML front matter | — |
| **フック** | `.kiro/hooks/*.json` | `~/.kiro/hooks/*.json` | JSON（v1） | [`docs/hooks`](https://kiro.dev/docs/hooks/) |
| **カスタムエージェント** | `.kiro/agents/*.md` | `~/.kiro/agents/*.md` | Markdown | [`docs/cli/v3/agent-config`](https://kiro.dev/docs/cli/v3/agent-config) |
| **Agent Skills** | `.kiro/skills/<名前>/SKILL.md` | `~/.kiro/skills/<名前>/SKILL.md` | Markdown | — |
| **MCP サーバ定義** | `.kiro/settings/mcp.json` | `~/.kiro/settings/mcp.json` | JSON | — |
| **権限** | `~/.kiro/workspace-roots/<hash>/permissions.yaml` | `~/.kiro/settings/permissions.yaml` | YAML | [`docs/cli/v3/permissions`](https://kiro.dev/docs/cli/v3/permissions) |
| **無視ファイル** | `.kiroignore`（プロジェクトルート） | `~/.kiro/settings/kiroignore` | gitignore 構文 | — |

> **CLI 版の対応ページは `docs/cli/v3/` を指しています。** IDE 1.0 の GA 機能に対応するのは CLI 3.0（Early Access）です。
> **CLI 2.x の非 v3 ページは別仕様**で、特に hooks はまったくの別物（stdin 経由 JSON のライフサイクルフック）です。

---

<a id="specs-dir"></a>

## 3. 仕様（Specs）— `.kiro/specs/<機能名>/`

1つの機能につき1つのディレクトリを作り、その中に成果物を置きます。

| ファイル | 内容 |
|---------|------|
| **`requirements.md`**（または **`bugfix.md`**） | ユーザーストーリー・受け入れ基準、またはバグの分析を構造化した記法で記述 |
| **`design.md`** | 技術アーキテクチャ・シーケンス図・実装上の考慮事項 |
| **`tasks.md`** | 個別に追跡可能なタスクに分けた詳細な実装計画 |

**バグ修正の spec では `requirements.md` の代わりに `bugfix.md`** になります。

`tasks.md` には専用の実行インターフェースがあり、タスクの状態（進行中・完了）がリアルタイムに更新されます。Kiro は `tasks.md` のタスクから**依存グラフ**を作り、独立したタスクを**ウェーブ**にまとめます。

使い方の解説は [01_features/01_specs.md](../01_features/01_specs.md) を参照してください。

---

## 4. ステアリング — `.kiro/steering/*.md`

エージェントに守らせたい規約や文脈を Markdown で書きます。

### 4.1 スコープ

| スコープ | 場所 | 用途 |
|---------|------|------|
| **ワークスペース** | `.kiro/steering/` | そのワークスペース固有のパターン・ライブラリ・標準 |
| **グローバル** | `~/.kiro/steering/` | すべてのワークスペースに適用される規約 |
| **チーム** | `~/.kiro/steering/`（MDM やグループポリシーで配布） | チーム全体に適用する中央管理のステアリング |

**チームステアリングはグローバルステアリングの仕組みを使います。** MDM やグループポリシーで利用者の PC に配布するか、中央リポジトリから利用者がダウンロードして `~/.kiro/steering` フォルダに置きます。

### 4.2 基盤ステアリングファイル（3種）

Kiro パネルの **Steering** から **Generate Steering Docs** を選ぶと生成されます。

| ファイル | 内容 |
|---------|------|
| **`product.md`** | 製品の目的・対象ユーザー・主要機能・ビジネス目標 |
| **`tech.md`** | 採用しているフレームワーク・ライブラリ・開発ツール・技術的制約 |
| **`structure.md`** | ファイル構成・命名規約・インポートのパターン・アーキテクチャ上の決定 |

**この3ファイルは既定ですべてのやり取りに含まれ**、Kiro のプロジェクト理解の土台になります。

### 4.3 読み込みタイミング（inclusion modes・4種）

ファイル先頭の YAML front matter で指定します。**front matter はファイルの先頭に置き、前に空行や内容を入れてはいけません。**

**(a) 常に含める（既定）**

```yaml
---
inclusion: always
---
```

すべてのやり取りに自動的に読み込まれます。技術スタック・コーディング規約・基本的な設計原則など、全体に効かせたい標準に向きます。

**(b) 条件付きで含める**

```yaml
---
inclusion: fileMatch
fileMatchPattern: "components/**/*.tsx"
---
```

指定したパターンに一致するファイルを扱っているときだけ含まれます。配列で複数指定もできます。

```yaml
---
inclusion: fileMatch
fileMatchPattern: ["**/*.ts", "**/*.tsx", "**/tsconfig.*.json"]
---
```

**(c) 手動で含める**

```yaml
---
inclusion: manual
---
```

チャットで `#ステアリングファイル名` と参照したときだけ含まれます。

> **manual のステアリングファイルはスラッシュコマンドとしても現れます。** チャットで `/` を打つと選べます。
> **これが Kiro IDE のスラッシュコマンドの正体です**（[00_information/README.md](../00_information/README.md#-ide-と-cli-を混同しないために)）。
> 1.0 で manual トリガのフックが廃止され、この仕組みに置き換わりました。

**(d) 説明に応じて自動で含める**

```yaml
---
inclusion: auto
name: api-design
description: REST API design patterns and conventions. Use when creating or modifying API endpoints.
---
```

リクエストが `description` に一致したときに自動的に含まれます。**`name` と `description` の2つが必須**です。

| フィールド | 必須 | 内容 |
|-----------|-----|------|
| `name` | **必須** | ステアリングファイルの識別子（表示と照合に使われる） |
| `description` | **必須** | いつこのファイルを含めるか。Kiro がリクエストと照合する |

**`auto` のファイルもスラッシュコマンドとして現れます**（`/` に続けてファイル名）。

4種の使い分けは [01_features/06_steering.md](../01_features/06_steering.md#5-読み込みタイミングinclusion-modes4種) を参照してください。

### 4.3.1 ファイル参照（`#[[file:...]]`）

ステアリングファイル内から**ワークスペースの実ファイルを参照**できます。内容をコピーする代わりに参照することで、元ファイルの変更が反映されます。

```markdown
#[[file:api/openapi.yaml]]
```

### 4.4 `AGENTS.md` にも対応

Kiro は [AGENTS.md](https://agents.md/) 標準によるステアリング指示に対応しています。

| 項目 | 内容 |
|------|------|
| 置き場所 | **`~/.kiro/steering/`**（グローバルの場所）または**ワークスペースのルートフォルダ** |
| 形式 | Markdown（Kiro のステアリングファイルと同様） |
| **inclusion modes** | **非対応。常に含まれる** |

自動的に拾われるため設定は不要です。

---

## 5. フック — `.kiro/hooks/*.json`

**v1 JSON 形式**です（1.0 で `.hook` 形式から変わりました）。

```json
{
  "version": "v1",
  "hooks": [
    {
      "name": "lint-on-save",
      "trigger": "PostFileSave",
      "matcher": "\\.ts$",
      "action": { "type": "command", "command": "npm run lint" },
      "timeout": 30,
      "enabled": true
    }
  ]
}
```

| フィールド | 型 | 必須 | 既定 | 内容 |
|-----------|----|-----|------|------|
| **`name`** | string | **必須** | — | テレメトリに表示される識別子 |
| `description` | string | 任意 | — | ドキュメント目的のみ |
| **`trigger`** | string | **必須** | — | フックが発火する契機 |
| `matcher` | 正規表現の文字列 | 任意 | 常に一致 | ツール名またはファイルパスで絞り込む |
| **`action`** | object | **必須** | — | `{ "type": "command", "command": "..." }` または `{ "type": "agent", "prompt": "..." }` |
| `timeout` | 整数（秒） | 任意 | **60** | **0 でタイムアウト無効**。agent アクションでは無視される |
| `enabled` | boolean | 任意 | **true** | `false` にすると削除せずスキップできる |

**アクションは2種類**です。

| type | 内容 |
|------|------|
| `command` | シェルコマンドを実行する |
| `agent` | エージェントにプロンプトを渡す |

> **グローバルフックは 1.0.182（2026-07-20）で追加されました。** `~/.kiro/hooks/` に置いたフックファイルが
> すべてのワークスペースに適用され、フォーマットやリントのような横断的な自動化に使えます。

使い方の解説は [01_features/05_hooks.md](../01_features/05_hooks.md) を参照してください。

---

## 6. カスタムエージェント — `.kiro/agents/*.md`

**Markdown 形式**です（1.0 で導入）。

| スコープ | 場所 | 特徴 |
|---------|------|------|
| **ワークスペース** | `.kiro/agents/` | **バージョン管理で共有できる** |
| **ユーザー** | `~/.kiro/agents/` | すべてのプロジェクトで使える |

**ネストしたディレクトリに対応**します。エージェント名は agents ディレクトリからの相対パス（拡張子なし）です。

| ファイル | エージェント名 |
|---------|-------------|
| `~/.kiro/agents/team/planner.md` | `team/planner` |

> **ワークスペースのエージェントは、そのワークスペースが信頼されている場合のみ読み込まれます。**
> `.kiro/agents/` を持つワークスペースを初めて開くと、Kiro が信頼するかを確認します。

使い方の解説は [01_features/07_custom-agents.md](../01_features/07_custom-agents.md) を参照してください。

---

## 7. Agent Skills — `.kiro/skills/<名前>/SKILL.md`

**フォルダ単位**で、中に `SKILL.md` を必須で置きます。

| スコープ | 場所 | 用途 |
|---------|------|------|
| **ワークスペース** | `.kiro/skills/` | デプロイ手順やチーム規約などプロジェクト固有のワークフロー |
| **グローバル** | `~/.kiro/skills/` | コードレビューの進め方など、プロジェクトを問わない個人のワークフロー |

```
skills/<スキル名>/
├── SKILL.md        # 必須
└── references/     # 詳細なドキュメント（任意）
```

公式の推奨: **`SKILL.md` は要点に絞り、詳細は `references/` に置く**（有効化時に `SKILL.md` は全文が読み込まれるため）。

GitHub の公開リポジトリからインポートもできます（**URL はリポジトリのルートではなくサブディレクトリを指す必要があります**）。インポートされたスキルは skills ディレクトリにコピーされます。

---

## 8. MCP サーバ定義 — `.kiro/settings/mcp.json`

| 階層 | 場所 | 適用範囲 |
|------|------|---------|
| **ワークスペース** | `.kiro/settings/mcp.json` | 現在のワークスペースのみ |
| **ユーザー** | `~/.kiro/settings/mcp.json` | すべてのワークスペース |

> **両方が存在する場合、設定はマージされ、ワークスペース側が優先されます。**

コマンドパレットから開けます（**Kiro: Open workspace MCP config (JSON)** でワークスペース側）。

> **`mcp.json` は保護されたパスです。** エージェントが書き換えようとすると必ず確認を求められます
> （ベース名の完全一致。[03_deployment/05_security.md](../03_deployment/05_security.md) §3）。

使い方の解説は [01_features/08_mcp.md](../01_features/08_mcp.md) を参照してください。

---

## 9. 権限 — `permissions.yaml`

| スコープ | 場所 |
|---------|------|
| **ユーザー（全ワークスペース）** | `~/.kiro/settings/permissions.yaml` |
| **ワークスペース** | `~/.kiro/workspace-roots/<hash(workspaceRoot)>/permissions.yaml` |

**ワークスペースの権限がリポジトリ外にある**のは、クローンしたリポジトリによる権限の注入を防ぐためです。

> **`~/.kiro/settings/` と `.kiro/settings/` と `~/.kiro/workspace-roots/` への書き込みは、エージェントに対して常に拒否**されます（Kiro スコープの不変条件・上書き不可）。

書式の詳細は [03_permissions.md](03_permissions.md) を参照してください。

---

## 10. 無視ファイル — `.kiroignore`

エージェントに**読ませない**ファイルを gitignore 構文で指定します。

| 種別 | 場所 | 設定 |
|------|------|------|
| **ワークスペース** | プロジェクトルート（**サブディレクトリにも置ける**） | 設定で有効化が必要（下記） |
| **グローバル** | **`~/.kiro/settings/kiroignore`** | **設定不要。存在すれば自動的に尊重される** |
| Git のグローバル無視ファイル | git 設定の `core.excludesfile` | 自動。**ただし git リポジトリ内でのみ適用** |

### 10.1 ワークスペースの `.kiroignore` を有効にする

| 順 | 操作 |
|----|------|
| 1 | プロジェクトルート（または任意のサブディレクトリ）に `.kiroignore` を作る |
| 2 | パターンを書く |
| 3 | 設定を開く（`Cmd+,` / `Ctrl+,`） |
| 4 | **Agent Ignore Files** を検索する（設定キー: **`kiroAgent.agentIgnoreFiles`**） |
| 5 | 配列に `.kiroignore` を追加する |

**`kiroAgent.agentIgnoreFiles` はファイル名の配列**です。

| 設定値 | 意味 |
|-------|------|
| `[".gitignore", ".kiroignore"]` | 複数の無視ファイルを同時に使う |
| `[]` | ワークスペースレベルの無視ファイルを無効化する |

### 10.2 記述例

```bash
# Secrets and credentials
.env
.env.*
!.env.example
*.pem
*.key

# Private directories
secrets/
private/
```

**サブディレクトリの `.kiroignore` は親のパターンを上書き・拡張できます**（そのサブディレクトリ内のファイルについてはサブディレクトリ側が優先）。

> **`.gitignore` と使い分ける理由**（公式）: エージェントのアクセスとバージョン管理で異なるルールが必要なとき、
> または **git で追跡しているが Kiro には読ませたくない**ファイルを遮断したいときに `.kiroignore` を使います。

> **`.kiroignore` は保護されたパスです。** エージェントが書き換えようとすると必ず確認を求められます。

---

## 11. マルチルートワークスペースでの扱い

1つのワークスペースに複数のルートフォルダを持たせられます（**File > Add Folder to Workspace...**）。

**その場合、Kiro は各ルートフォルダ配下の `.kiro` から成果物を読み書きします。**

| 対象 | 挙動 |
|------|------|
| **Specs** | 各ルートの `.kiro` から取得し、**Specs** セクションに統合表示。**各 spec の隣に含まれるルートフォルダ名が表示される** |
| **ステアリング** | 各ルートから取得し、**Agent Steering** の **Workspace** グループに統合表示。新規作成時は**保存先のルートフォルダを選ぶ** |
| **フック** | 各ルートから取得し、**Agent Hooks** に統合表示 |
| **MCP サーバ** | 各ルートから取得し、**MCP Servers** に統合表示。**Open MCP config** は既定でユーザーレベルを開き、**Workspace Config** を押すと**どのルートの設定を見るか選ぶ** |
| コードベースの索引・リポジトリマップ | **すべてのルートフォルダのコードを含む**。プロンプトからの参照方法は単一ルートと同じ |

---

## 関連ドキュメント

- [03_permissions.md](03_permissions.md) - `permissions.yaml` の書式
- [04_context-providers.md](04_context-providers.md) - `#steering`・`#spec` での参照
- [01_features/](../01_features/) - 各機能の使い方
- [03_deployment/05_security.md](../03_deployment/05_security.md) - 保護されたパス・エージェントに見せないファイル
