# Hooks（イベント駆動の自動化）

**ファイル保存やツール呼び出しなどのイベントで、自動的に処理を走らせる仕組みです。**

- **一次情報**: [Hooks](https://kiro.dev/docs/hooks/)（公式ページ更新日: 2026-10-10）・[Hook types](https://kiro.dev/docs/hooks/types/)（公式ページ更新日: 2026-10-10）・[Hook actions](https://kiro.dev/docs/hooks/actions/)・[Hook management](https://kiro.dev/docs/hooks/management/)（公式ページ更新日: 2026-08-21）・[What's new in IDE 1.0: Hooks](https://kiro.dev/docs/ide/whats-new-v1/hooks/)（公式ページ更新日: 2026-08-21）
- **ファイル形式**: [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#5-フック--kirohooksjson)
- **1.0 で形式が変わりました**（`.hook` → **v1 JSON**）。移行は [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md)

> ⚠️ **公式ドキュメント間の記述に差が残っています**（本サイトの再確認結果。公式ページの更新日付き）:
>
> **以前は、[Hooks](https://kiro.dev/docs/hooks/) ページがトリガー一覧を10種で示して manual フックが manual ステアリングファイルに置き換わったと書き、[Hook types](https://kiro.dev/docs/hooks/types/)・[Hook management](https://kiro.dev/docs/hooks/management/)・[IDE 0.x reference](https://kiro.dev/docs/ide/0x-reference/) が「Manual Trigger」を IDE のトリガーとして載せていたため、公式ページ間で食い違っていました。**
>
> **現行の公式ページでは、そのうち3ページが整合しています。**
>
> | 公式ページ（更新日） | 現行の記述 |
> |-------------------|-----------|
> | [Hooks](https://kiro.dev/docs/hooks/)（2026-10-10） | トリガーの一覧は載せず、[Hook types](https://kiro.dev/docs/hooks/types/) を「the authoritative trigger list」（権威ある一覧）と案内している。以前の版にあった「Manual hooks from earlier IDE versions have been replaced by manual steering files.」の文は、現行ページに見当たらない |
> | [Hook types](https://kiro.dev/docs/hooks/types/)（2026-10-10） | 「Availability by surface」の表で、IDE の対応は Prompt Submit・Agent Stop・Session Start・Pre Tool Use・Post Tool Use・File Create・File Save・File Delete・Pre Task Execution・Post Task Execution の**10種**。Manual は CLI V3 が一覧に載せるだけ（`/hooks` に実行の操作なし）で、IDE は「Legacy manual Hooks (IDE only)」として別に扱う |
> | [Hook management](https://kiro.dev/docs/hooks/management/)（2026-08-21） | 「Run legacy manual hooks」節。IDE 0.x で作った manual フックは legacy ラベル付きで Agent Hooks パネルに残り、有効なら `▷`（Quick run）または Hook view の `Start Hook` で実行できる |
>
> **この3ページと [What's new in IDE 1.0: Hooks](https://kiro.dev/docs/ide/whats-new-v1/hooks/)（2026-08-21）は一致して、`userTriggered` に v1 のトリガー相当がなく、IDE では manual トリガーのフックを新規作成できない（新しいオンデマンドの作業には manual ステアリングファイルを使う）と説明しています。**
>
> **なお差が残っているページがあります。** [IDE 0.x reference](https://kiro.dev/docs/ide/0x-reference/)（2026-08-21）は、同ページ冒頭で 0.x の挙動を記述するページと説明したうえで、次を載せています。
>
> | 該当節 | 記述 |
> |--------|------|
> | 「Available triggers（**unchanged from 0.x**）」 | `userTriggered`（"Triggered manually by user"）を含む**11種**を `when.type` の値（`sessionStart`・`fileEdited` など）で掲載 |
> | 「Current format (1.0)」 | `when`／`then` を使う JSON 例を v1 形式として掲載。Hooks ページと What's new in IDE 1.0 の `trigger`／`matcher`／`action`（PascalCase）とは、スキーマの記述が異なる |
> | 「Legacy manual Hooks in 1.0」 | 既存の `userTriggered` フックは legacy ラベル付きで残り実行できる。1.0 では新規作成できない（上の3ページと一致） |
>
> **本ページのトリガー一覧（第2節）は、Hook types の IDE 対応（10種）と What's new in IDE 1.0 の表に従って、v1 JSON の `trigger` フィールドの値のみを記載しています。**
> **manual トリガーは v1 JSON にありません。** 新規のオンデマンド実行は manual ステアリングファイルに置き換わりました（[06_steering.md](06_steering.md)）。
> IDE 0.x で作った manual フックは、legacy として残り、有効なものは実行できます（第5節）。

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
| **`PreToolUse`** | **ツール実行の前** | **ツール名（ツール ID・カテゴリ・セレクタ・正規表現。§2.1）** | **✅ できる** |
| `PostToolUse` | ツール実行の後 | ツール名（§2.1 と同じ） | ❌ |
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

`PreToolUse` / `PostToolUse` では**ツール名**で絞り込みます。IDE のエディタでは **Tool name pattern** 欄に、正確なツール ID・組み込みカテゴリ・ソースセレクタ・正規表現のいずれかを指定します。複数のエントリを指定できます（公式 [Hook types](https://kiro.dev/docs/hooks/types/#pre-tool-use)・2026-10-10）。

**組み込みのカテゴリ**:

| 指定 | 内容 |
|------|------|
| `read` | 組み込みのファイル読み取りツールすべて |
| `write` | 組み込みのファイル書き込みツールすべて |
| `shell` | 組み込みのシェルコマンド関連ツールすべて |
| `web` | 組み込みの Web ツールすべて |
| `spec` | 組み込みの spec ツールすべて |

**ソースセレクタ**（ツールの出自で絞る）:

| セレクタ | 内容 |
|---------|------|
| `@mcp` | すべての MCP ツール |
| `@powers` | すべての **Powers** ツール（Powers = MCP サーバ・ステアリング・フックのバンドルを動的に読み込む仕組み。[0.7 の導入時の説明](../02_update/02_changelog-0x.md#powers)・公式 [`/docs/powers`](https://kiro.dev/docs/powers/)） |
| `@builtin` | すべての組み込みツール |
| `@<server>` | 1つの MCP サーバのすべてのツール（例: `@postgres`） |
| `@<server>/<tool>` | 1つの MCP サーバの1つのツール（例: `@postgres/query`） |

**照合のしかた**（公式）:

- IDE のエディタは、各エントリを**正規表現**としてツール ID に照合します。このため `read` のような単純な名前は、そのテキストを含む任意のツール ID に一致し得ます。
- **欄を空にすると、すべてのツールに一致**します。
- Hook JSON ファイルでは**ワイルドカード**も使えます。`*` は任意の文字数に、`?` は1文字に一致します。IDE のエディタはこれらを無効な正規表現として拒否するため、使うときは Hook JSON ファイルを直接編集します。

> **1.2.56 で追加されたセレクタ**: 1.2.56 の changelog は、`PreToolUse`・`PostToolUse` のフックで、ツール ID を1つずつ挙げる代わりに、カテゴリとセレクタ（`shell`・`read`・`write`・`@builtin`・`@mcp`・`@server`・`@server/tool`）でツールのグループを指定できるようになったと説明しています（[1.2.56](../02_update/01_changelog.md#v1-2-56)）。
>
> **公式の2つの記述は列挙が異なります。** 上の changelog は7種を挙げています。Hook types ページ（2026-10-10）は、これに加えて `web`・`spec` のカテゴリと `@powers` のセレクタを載せています。本ページは両方を載せ、Hook types ページの記述を詳細の出典としています。
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
| **legacy manual フックの実行** | IDE 0.x で作った manual フック（`userTriggered`）は **legacy ラベル付き**で Agent Hooks パネルに残ります。**有効なものは**、パネルでフック名の隣の **`▷`（Quick run）**、またはフックを選んで右上の **Start Hook** で実行できます（公式 [Hook management](https://kiro.dev/docs/hooks/management/) の「Run legacy manual hooks」）。**IDE では manual トリガーのフックを新規作成できません。** 新しいオンデマンドの作業には manual ステアリングファイルを使います（冒頭の注記） |

> JSON ファイルの `enabled` を `false` にしても同じことができます（[04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md#5-フック--kirohooksjson)）。

---

## 6. スコープ（ワークスペースとグローバル）

| スコープ | 場所 | 適用範囲 |
|---------|------|---------|
| **ワークスペース** | `.kiro/hooks/*.json` | そのプロジェクトのみ。**バージョン管理でチーム共有できる** |
| **グローバル** | `~/.kiro/hooks/*.json` | **すべてのワークスペース** |

> **グローバルフックは 1.0.182（2026-07-20）で追加されました。** フォーマットやリントのような
> **プロジェクト横断の自動化**に使えます。
>
> 公式 [Hooks](https://kiro.dev/docs/hooks/) ページ（2026-10-10）の「File naming and location」は、グローバルの場所を「Global location (CLI V3): `~/.kiro/hooks/`」と記載しています。IDE のグローバルフックについては、このページに記述がありません。本ページの IDE のグローバルフックの記述は、1.0.182 の changelog が根拠です。

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
| 5 | **v1 JSON に manual トリガーはありません。** IDE 0.x で作った manual フックは legacy として残り、有効なものは実行できますが、新規には作れません。新しいオンデマンドの作業は manual ステアリングファイルで行います（[06_steering.md](06_steering.md)） |
| 6 | **`~/.kiro/hooks/` への書き込みも常に確認が求められます**（公式 Permissions ページの 2026-10-20 更新版では、ワークスペースの `.kiro` と `~/.kiro` の両方の `hooks` ディレクトリが対象） |

### 8.1 1.1 での信頼性の改善

| 内容 |
|------|
| **プロセスがすぐに終了しても、フックの出力が保持される** |
| **正当なフックの出力が、プロンプトインジェクションと誤認されずに受け付けられる** |
| **`SessionStart` フックのコンテキストが、すべてのターンで一貫して使えるようになった** |
| **`UserPromptSubmit` フックが、ユーザーのメッセージ・フックの指示・環境コンテキストを重複してモデルに送る問題**が修正された |

### 8.2 1.2.56 での改善

| 内容 |
|------|
| **`PreToolUse`・`PostToolUse` のフックで、カテゴリとセレクタによるツールのグループ指定ができる**（§2.1） |
| **`UserPromptSubmit` フックとクライアント側で実行されるコマンドフックの出力が、セッションの再読み込み後にモデルのコンテキストから落ちる問題**が修正された |

---

## 関連ドキュメント

- [06_steering.md](06_steering.md) - manual トリガーの新規作成の代わりになるスラッシュコマンド
- [01_specs.md](01_specs.md) - `PreTaskExec` / `PostTaskExec` が対象にする spec タスク
- [03_permissions.md](03_permissions.md) - フック実行と権限の関係
- [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) - v1 JSON の全フィールド
- [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) - `.hook` からの移行手順
