# Hooks（イベント駆動の自動化）

**ファイル保存やツール呼び出しなどのイベントで、自動的に処理を走らせる仕組みです。**

- **一次情報**: [Hooks](https://kiro.dev/docs/hooks/)（公式ページ更新日: 2026-08-06）・[Hook actions](https://kiro.dev/docs/hooks/actions/)・[Hook management](https://kiro.dev/docs/hooks/management/)
- **ファイル形式**: [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#5-フック--kirohooksjson)
- **1.0 で形式が変わりました**（`.hook` → **v1 JSON**）。移行は [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md)

> ⚠️ **公式ドキュメント間の食い違いに注意**（本サイトの調査結果）:
>
> **本サイトは、更新日が最も新しく階層も上位の [Hooks](https://kiro.dev/docs/hooks/)（更新日 2026-08-06）を正としています。**
> 同ページはトリガー一覧を**10種**で示し（Manual Trigger を含めず）、その直後に
> 「**Manual hooks from earlier IDE versions have been replaced by manual steering files.**」と明記しています。
> [What's new in IDE 1.0: Hooks](https://kiro.dev/docs/ide/whats-new-v1/hooks/) の移行対応表も
> `userTriggered` → 「Replaced by manual steering files」と一致しています。
>
> 一方、次の2ページ（いずれも更新日 2026-08-04）には異なる記述が残っています。
>
> | 公式ページ | 記述 |
> |-----------|------|
> | [Hook types](https://kiro.dev/docs/hooks/types/) | 「Manual Trigger」を IDE・CLI 対応の**トリガーとして掲載**（11種類目）。[Hook management](https://kiro.dev/docs/hooks/management/) にも「Run manual trigger hooks」節があり、Agent Hooks パネルの `▷`（Quick run）・hook view の `Start Hook` で実行すると説明されている |
> | [IDE 0.x reference](https://kiro.dev/docs/ide/0x-reference/) | 「Available triggers（**unchanged from 0.x**）」という見出しで `userTriggered`（"Triggered manually by user"）を含む**11種**を掲載。さらに「Current format (1.0)」節は `when`/`then` + camelCase でv1形式を説明しており、`docs/hooks/` の `trigger`/`matcher`/`action`（PascalCase）と**スキーマの記述自体が食い違っています** |
>
> **本ページのトリガー一覧（第2節）は、`docs/hooks/` に従って v1 JSON の `trigger` フィールドの値のみを記載しています。**
> **manual トリガは 1.0 で廃止**され、manual ステアリングファイルに置き換わりました（[06_steering.md](06_steering.md)）。
> なお「Manual Trigger」という**UI 操作**（既存フックの手動実行ボタン）について公式が上記のように記述している事実は
> そのまま伝えますが、どのトリガーを持つフックに対して有効なのかは公式に明示がなく、**実機未確認**です。

---

## 1. 何ができるか

公式が挙げるイベント:

- **ファイルの保存・作成・削除**
- **ユーザーのプロンプト送信**と**エージェントのターン完了**
- **ツール呼び出しの前後**
- **spec タスク実行の前後**

これらにフックを設定することで、次のことができます。

| 目的 |
|------|
| **一貫したコード品質を保つ** |
| **セキュリティ上の脆弱性を防ぐ** |
| **手作業の負担を減らす** |
| **チームのプロセスを標準化する** |

### 1.1 仕組みは2段階

| 段階 | 内容 |
|------|------|
| **1. イベント検出** | IDE 内の特定のイベントを監視する |
| **2. 自動アクション** | イベントが起きたら、**エージェントプロンプト**または**シェルコマンド**を実行する |

---

## 2. トリガーの一覧（10種）

**v1 JSON の `trigger` フィールドに書く値**です。

| トリガー | 発火するとき | `matcher` の対象 | **ブロックできるか** |
|---------|------------|---------------|-----------------|
| `SessionStart` | セッション開始時 | — | ❌ |
| `Stop` | **エージェントがターンを完了したとき** | — | ❌ |
| **`PreToolUse`** | **ツール実行の前** | **ツール名（正規表現）** | **✅ できる** |
| `PostToolUse` | ツール実行の後 | ツール名（正規表現） | ❌ |
| **`PreTaskExec`** | spec タスクの開始前 | — | **✅ できる** |
| `PostTaskExec` | spec タスクの終了後 | — | ❌ |
| **`UserPromptSubmit`** | **ユーザーがプロンプトを送信したとき** | — | **✅ できる** |
| `PostFileCreate` | **エージェントが**ファイルを作成した後 | ファイルパス（正規表現） | ❌ |
| **`PostFileSave`** | **エージェントが**ファイルを保存した後 | ファイルパス（正規表現） | ❌ |
| `PostFileDelete` | **エージェントが**ファイルを削除した後 | ファイルパス（正規表現） | ❌ |

**ブロックできるのは3種のみ**（`PreToolUse`・`PreTaskExec`・`UserPromptSubmit`）です。事前に止められるトリガーだけがブロック可能という素直な設計になっています。

> **ファイル系トリガーは「エージェントによる」変更で発火します。** 1.0.116（2026-07-09）で
> 「エージェントが書き込み・作成・削除したときにも発火する」ようになりました。
> それ以前は手動保存が主な契機でした。**format-on-save や review-on-create のフックが
> エージェント起点の変更にも自動的に効きます。**

### 2.1 `matcher` の書き方（ツール名の指定）

`PreToolUse` / `PostToolUse` では**ツール名**で絞り込みます。組み込みのカテゴリが使えます。

| 指定 | 内容 |
|------|------|
| `read` | 組み込みのファイル読み取りツールすべて |
| `write` | 組み込みのファイル書き込みツールすべて |
| `shell` | 組み込みのシェルコマンド関連ツールすべて |
| `web` | 組み込みの Web ツールすべて |
| `spec` | 組み込みの spec ツールすべて |
| `*` | **すべてのツール**（組み込みと MCP） |

**プレフィックスでツールの出自を絞る**こともできます。

| プレフィックス | 内容 |
|-------------|------|
| `@mcp` | すべての MCP ツール |
| `@powers` | すべての **Powers** ツール（Powers = MCP サーバ・ステアリング・フックのバンドルを動的に読み込む仕組み。[0.7 の導入時の説明](../02_update/02_changelog-0x.md#powers)・公式 [`/docs/powers`](https://kiro.dev/docs/powers/)） |
| `@builtin` | すべての組み込みツール |

> **`@` で始まるプレフィックスは正規表現で照合されます。** `@mcp.*sql.*` のようなパターンで
> 名前から特定の MCP ツールを狙えます。
>
> **使えるツール名は Kiro に聞けます**（公式の案内）。

---

## 3. アクションの2種類

トリガーを決めたら、何をするかを選びます。

### 3.1 Agent Prompt（エージェントプロンプト／「Ask Kiro」）

フックが発火するたびに**エージェントに送るプロンプト**を定義します。エージェントは、チャットパネルで渡されたプロンプトと同じように応答・行動します。

> **`UserPromptSubmit` トリガーの場合、このアクションは「Add to prompt」と呼ばれます。**
> フックに書いたプロンプトが**ユーザーのプロンプトに追記され**、結合されたプロンプトがエージェントに送られます。

### 3.2 Shell Command（シェルコマンド）

フックが発火するたびに**シェルコマンドを実行**します。

| 終了コード | 挙動 |
|----------|------|
| **`0`**（成功） | **`stdout` の出力がエージェントのコンテキストに追加される** |
| **`2`** | **実行をブロックする**（`PreToolUse`・`UserPromptSubmit`・`PreTaskExec` のみ）。**`stderr` がエージェントに返される** |
| **その他** | **利用者に警告が表示される。ツールの実行は続行される** |

タイムアウトを指定できます。**既定は 60 秒**、**`0` で無効化**できます。

> **終了コード `2` が特別**です。「失敗したら止まる」ではなく「**`2` を返したときだけ止まる**」という設計です。
> それ以外の非ゼロは警告どまりで処理は進みます。

### 3.3 どちらを使うか（公式の指針）

| 使うとき | アクション |
|---------|----------|
| トリガーイベントに応じて、**自然言語でコンテキストに基づいた作業**をエージェントに指示したい | **Agent Prompt** |
| **特定のコマンドを走らせたい**、あるいは**エージェントの現在のコンテキストに依存しない決定的な処理**をしたい | **Shell Command** |

**コストと速度の違い（重要）**:

| | クレジット消費 | 速度 |
|-|------------|------|
| **Agent Prompt** | **消費する**（新しいエージェントループを起動するため） | 遅い |
| **Shell Command** | **消費しない** | **速い**（ローカルで実行され LLM を使わない） |

**決定的な処理は Shell Command にする**のが基本です。

### 3.4 `Stop` トリガーの確認プロンプト（`confirm`）

**`Stop` トリガーの Shell Command は、実行前に確認を求められます。** `confirm` ブロックに質問文と選択肢を書きます。

```json
{
  "version": "v1",
  "hooks": [
    {
      "name": "submit-session-results",
      "trigger": "Stop",
      "action": { "type": "command", "command": "./submit.sh" },
      "confirm": {
        "question": "このセッションの結果を送信しますか？",
        "options": [
          { "id": "submit", "label": "はい、送信する", "run": true },
          { "id": "dismiss", "label": "今回はしない", "run": false }
        ]
      }
    }
  ]
}
```

各選択肢は `id`・ボタンに表示する `label`・選んだときにコマンドを実行するかを決める `run` フラグを持ちます。

#### 3.4.1 動的な確認オプション（`confirmCommand`、1.0.288 で追加）

**実行時に何を尋ねるかを動的に決めたい場合**、`confirm` ブロックに任意で `confirmCommand` を追加します。プロンプトが表示される前にこのコマンドが実行され、その `stdout` が JSON としてプロンプトを制御します。

| `stdout` の JSON | 効果 |
|-----------------|------|
| `{ "skip": true }` | プロンプトを抑制し、このターンはフックをスキップする |
| `{ "question": "...", "options": [...] }` | 静的な `question`・`options` を置き換える |

```json
{
  "confirm": {
    "question": "このセッションの結果を送信しますか？",
    "confirmCommand": "./confirm-options.sh",
    "options": [
      { "id": "submit", "label": "はい、送信する", "run": true },
      { "id": "dismiss", "label": "今回はしない", "run": false }
    ]
  }
}
```

`confirmCommand` が**非ゼロで終了・タイムアウト・不正な JSON を出力**した場合、静的な `question`・`options` がフォールバックとして使われます。「今回のセッションでは二度と聞かない」というオプションでマーカーファイルを書き、次のターンから `{ "skip": true }` を返す、といった条件付きの確認に使えます。

---

## 4. フックの作り方（3通り）

### 4.1 JSON ファイルを直接書く

`.kiro/hooks/*.json`:

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

フィールドの一覧は [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#5-フック--kirohooksjson) を参照してください。

### 4.2 チャットで作らせる（Ask Kiro to create a hook）

| 順 | 操作 |
|----|------|
| 1 | Kiro パネルの **Agent Hooks** セクションで **`+`** ボタンを押す |
| 2 | 表示される**2つの選択肢**（§4.3）から **Ask Kiro to create a hook** を選ぶ |
| 3 | **チャット入力欄にプロンプトが事前入力される**（Kiro にフックの機能概要を尋ねる内容） |
| 4 | 作りたいことを自然言語で説明し、**会話しながら設定を詰める**（例: 「ファイルを保存するたびにテストを走らせて」） |
| 5 | 生成されたフックは **`.kiro/hooks/` の JSON ファイルとして保存される** |

### 4.3 `+` ボタンの2つの選択肢

| 選択肢 | 内容 |
|-------|------|
| **Manually create a steering file** | **`/<ファイル名>` スラッシュコマンドとして呼び出す Markdown のステアリングファイル**を自分で書く |
| **Ask Kiro to create a hook** | チャットにプロンプトが事前入力され、会話でフック設定を作る（§4.2） |

> **「Manually create a steering file」がフック作成の選択肢に並んでいる理由**: **manual フックの後継が
> manual ステアリングファイル**だからです（冒頭の食い違い注記・[06_steering.md](06_steering.md)）。

### 4.4 0.x のフォーム UI は 1.0 で削除された

**0.x には「Manually create a hook」のフォーム UI がありました**（Title・Description・Event・Tool name・
File pattern・Action・Instructions/Command の各欄を埋める形式）。**1.0 でこのフォームは会話フローに置き換えられ、
`+` を押すとチャットにプロンプトが事前入力される形になりました。**

コマンドパレットの `Kiro: Open Kiro Hook UI` も 0.x のフォーム UI を開くためのものでした。

> 出典: [IDE 0.x reference](https://kiro.dev/docs/ide/0x-reference/) の
> 「Hook creation UI (**removed in 1.0**)」節。0.x から上げた方は操作が変わった点に注意してください。

---

## 5. フックの管理

Kiro パネルの **Agent Hooks** セクションから操作します。

| 操作 | 方法 |
|------|------|
| **有効・無効の切り替え**（削除せず） | Agent Hooks パネルでフックの隣の**目のアイコン**をクリック／フックを選んで右上の **Hook Enabled** スイッチ |
| **編集** | パネルでフックを選び、トリガー・ファイルパターン・指示・説明などを変更する。**更新は即座に反映される** |
| **削除** | フックを選び、下部の **Delete Hook** → **delete**。**この操作は取り消せません** |
| **手動実行**（manual trigger hooks） | Agent Hooks パネルでフック名の隣の **`▷`（Quick run）**／フックを選んで右上の **Start Hook**。**⚠️ 公式 [Hook management](https://kiro.dev/docs/hooks/management/) に「Run manual trigger hooks」として記載されている操作ですが、v1 JSON に manual トリガが存在しないため、どのフックに対して有効かは公式に明示がありません（実機未確認。冒頭の食い違い注記を参照）** |

> JSON ファイルの `enabled` を `false` にしても同じことができます（[04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#5-フック--kirohooksjson)）。

---

## 6. スコープ（ワークスペースとグローバル）

| スコープ | 場所 | 適用範囲 |
|---------|------|---------|
| **ワークスペース** | `.kiro/hooks/*.json` | そのプロジェクトのみ。**バージョン管理でチーム共有できる** |
| **グローバル** | `~/.kiro/hooks/*.json` | **すべてのワークスペース** |

> **グローバルフックは 1.0.182（2026-07-20）で追加されました。** フォーマットやリントのような
> **プロジェクト横断の自動化**に使えます。

マルチルートワークスペースでは、各ルートフォルダの `.kiro` からフックが集められ、**Agent Hooks** に統合表示されます（[04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#11-マルチルートワークスペースでの扱い)）。

---

## 7. 用途の例（公式のユースケースから）

| トリガー | 用途 |
|---------|------|
| `UserPromptSubmit` | プロンプトに関連する**追加のコンテキストをエージェントに渡す**／内容に応じて**特定のプロンプトをブロックする**／全プロンプトを中央に記録する |
| `Stop` | **コードをコンパイルして失敗をエージェントに報告する**／エージェントが生成したコードを整形・レビューする／変更をレビューして追加の指示を出す |
| `PreToolUse` | **特定のツール呼び出しをブロックする**／ツール呼び出し前にエージェントへ追加の指示を出す |
| `PostToolUse` | **監査のためにツール呼び出しを記録する**／write 系の呼び出し後にファイルを整形・レビューする |
| `PostFileCreate` | 新しいコンポーネントの**ボイラープレートを生成する**／新規ファイルに**ライセンスヘッダを付ける**／実装ファイル作成時にテストファイルを用意する |
| `PostFileSave` | **リントと整形を走らせる**／関連ファイルを更新する／ドキュメントを生成する／変更されたファイルのテストを走らせる |
| `PostFileDelete` | 関連ファイルを片付ける／他ファイルの import 参照を更新する |
| `PreTaskExec` | タスク実行前に**セットアップスクリプトや環境準備**を走らせる／**前提条件が満たされているか検証する**／タスク開始を記録する |
| `PostTaskExec` | **タスク完了後にテストを走らせて正しさを検証する**／変更ファイルにリント・整形をかける／完了分のドキュメントを生成する／外部システムに完了を通知する |

---

## 8. 制約と注意点

| # | 注意点 |
|---|-------|
| 1 | **サブエージェント内ではフックは発火しません**（[02_chat.md](02_chat.md#subagent-capabilities)） |
| 2 | **`.kiro/hooks/**` への書き込みは、エージェントに対して常に確認が求められます**（Kiro スコープの不変条件・上書き不可。[04_reference/03_permissions.md](../04_reference/03_permissions.md#71-kiro-スコープの不変条件上書き不可)） |
| 3 | **Agent Prompt アクションはクレジットを消費します。** 高頻度のトリガー（`PostFileSave` など）に付けると消費が増えます |
| 4 | **`timeout` は agent アクションでは無視されます**（command アクションのみ有効） |
| 5 | **manual トリガは 1.0 で廃止**されました。以前 manual フックを使っていた場合は manual ステアリングファイルに移行されます（[06_steering.md](06_steering.md)） |

---

## 関連ドキュメント

- [06_steering.md](06_steering.md) - manual トリガの後継（スラッシュコマンド）
- [01_specs.md](01_specs.md) - `PreTaskExec` / `PostTaskExec` が対象にする spec タスク
- [03_permissions.md](03_permissions.md) - フック実行と権限の関係
- [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) - v1 JSON の全フィールド
- [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) - `.hook` からの移行手順
