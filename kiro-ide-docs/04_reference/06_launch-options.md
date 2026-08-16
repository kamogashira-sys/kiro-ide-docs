# 起動オプション（コマンドライン）

**ターミナルから `kiro` コマンドで Kiro IDE を起動するときに使えるオプションです。**

- **公式ページ: 該当なし（実測値・1.0.309 で確認）**
- **収録件数**: オプション **38個**（4グループ）＋ サブコマンド **3個**
- **取得方法**: `kiro --help` の出力（1.0.309・コミット `02a5e3e7b5e09a492744835470a3cf4939045fbd`・x64）

> ⚠️ **本ページは公式ドキュメントに対応ページがありません。**
> 公式が `kiro` コマンドについて記述しているのは
> [Setup & First Run](https://kiro.dev/docs/ide/setup/)（公式ページ更新日: 2026-08-04）の
> 「プロジェクトディレクトリで `kiro .` を実行する」という一文だけで、**オプションの説明は公開されていません**。
> `docs/reference/cli-commands` は**別製品の Kiro CLI（`kiro-cli`）**のコマンド一覧であり、本ページとは無関係です。
>
> そのため本ページは**実機の `kiro --help` 出力を一次資料として記載しています**。
> 公式が文書化していないため、**将来のバージョンで予告なく変わる可能性があります**。
>
> **0.12.333 と 1.0.309 で出力を比較しましたが、オプションの集合・グループ構成・サブコマンドは同一でした**
> （差分はバージョン行とコミットハッシュのみ）。

> **Kiro IDE は Code OSS のフォーク**のため、大半のオプションは VS Code と共通です。
> **Kiro 固有の価値がある**のは `--add-mcp`・`--telemetry`・`chat` サブコマンドです（§7）。

---

## 1. 基本の書式

```
kiro [options] [paths...]
```

| 使い方 | 例 |
|-------|-----|
| カレントディレクトリを開く | `kiro .` |
| ファイル・フォルダを指定して開く | `kiro src/index.ts` |
| **標準入力から読む** | `echo Hello World \| kiro -`（末尾に `-` を付ける） |

> **Windows では実行ファイル名が `kiro.exe`** です（`--help` の Usage 行も `kiro.exe` と表示されます）。

---

## 2. Options（12個）

| オプション | 引数 | 内容 |
|-----------|------|------|
| **`-d` `--diff`** | `<file> <file>` | **2つのファイルを比較する** |
| **`-m` `--merge`** | `<path1> <path2> <base> <result>` | **3方向マージを行う**。変更された2つの版・共通の元・結果の出力先を指定する |
| **`-a` `--add`** | `<folder>` | **最後にアクティブだったウィンドウにフォルダを追加する** |
| `--remove` | `<folder>` | 最後にアクティブだったウィンドウからフォルダを取り除く |
| **`-g` `--goto`** | `<file:line[:character]>` | **指定した行・桁の位置でファイルを開く** |
| **`-n` `--new-window`** | — | **強制的に新しいウィンドウで開く** |
| **`-r` `--reuse-window`** | — | **すでに開いているウィンドウでファイル・フォルダを開く** |
| **`-w` `--wait`** | — | **ファイルが閉じられるまで戻らない**（エディタを外部ツールから呼ぶときに使う） |
| `--locale` | `<locale>` | 使用するロケール（例: `en-US`・`zh-TW`） |
| **`--user-data-dir`** | `<dir>` | **ユーザーデータの保存先ディレクトリを指定する**。**別々のインスタンスを複数開く**のに使える |
| `--profile` | `<profileName>` | 指定したプロファイルでフォルダ・ワークスペースを開き、プロファイルをワークスペースに関連付ける。**プロファイルが無ければ空のものが新規作成される** |
| `-h` `--help` | — | 使い方を表示する |

> **`-w --wait` の使いどころ**: `git config core.editor "kiro --wait"` のように、
> **編集が終わるまで待たせたい外部ツールから呼ぶ**場合に必要です。

---

## 3. Extensions Management（9個）

**拡張機能をコマンドラインから管理します。** Kiro のレジストリは Open VSX です（[01_features/10_editor.md](../01_features/10_editor.md#6-拡張機能)）。

| オプション | 引数 | 内容 |
|-----------|------|------|
| `--extensions-dir` | `<dir>` | 拡張機能のルートパスを設定する |
| **`--list-extensions`** | — | **インストール済みの拡張機能を一覧する** |
| `--show-versions` | — | `--list-extensions` と併用して**バージョンも表示する** |
| `--category` | `<category>` | `--list-extensions` と併用してカテゴリで絞り込む |
| **`--install-extension`** | `<ext-id \| path>` | **拡張機能をインストール・更新する**。引数は拡張機能 ID（`${publisher}.${name}` 形式）または VSIX のパス。最新版へ更新するには `--force` を併用する。特定のバージョンは `@${version}` を付ける（例: `vscode.csharp@1.2.3`） |
| `--pre-release` | — | `--install-extension` と併用して**プレリリース版**を入れる |
| **`--uninstall-extension`** | `<ext-id>` | **拡張機能をアンインストールする** |
| `--update-extensions` | — | インストール済みの拡張機能を更新する |
| `--enable-proposed-api` | `<ext-id>` | 拡張機能の proposed API を有効にする。**複数の拡張機能 ID を渡せる** |

> **`--force` は独立したオプションではありません。** `--install-extension` の説明文の中で
> 「最新版に更新するには `--force` を使う」と案内されている引数です（`--help` の一覧に定義行はありません）。

---

## 4. Model Context Protocol（1個）

| オプション | 引数 | 内容 |
|-----------|------|------|
| **`--add-mcp`** | `<json>` | **MCP サーバの定義をユーザープロファイルに追加する。** JSON 形式で渡す（`{"name":"server-name","command":...}` の形） |

MCP の設定ファイルの書き方は [01_features/08_mcp.md](../01_features/08_mcp.md)・
[01_kiro-directory.md](01_kiro-directory.md) を参照してください。

---

## 5. Troubleshooting（16個）

| オプション | 引数 | 内容 |
|-----------|------|------|
| **`-v` `--version`** | — | **バージョンを表示する**（バージョン・コミットハッシュ・アーキテクチャの3行） |
| `--verbose` | — | 詳細な出力を表示する（**`--wait` を暗黙的に伴う**） |
| **`--log`** | `<level>` | **ログレベル**。既定は `info`。指定できるのは `critical`・`error`・`warn`・`info`・`debug`・`trace`・`off`。**拡張機能ごとに `${publisher}.${name}:${logLevel}` の形式**でも指定でき（例: `vscode.csharp:trace`）、複数渡せる |
| `-s` `--status` | — | プロセスの使用状況と診断情報を表示する |
| `--prof-startup` | — | 起動時に CPU プロファイラを実行する |
| **`--disable-extensions`** | — | **インストール済みのすべての拡張機能を無効にする。** 設定として保存されず、**新しいウィンドウを開くときにのみ有効** |
| `--disable-extension` | `<ext-id>` | 指定した拡張機能を無効にする（保存されず、新しいウィンドウを開くときのみ有効） |
| `--sync` | `<on \| off>` | 同期を有効・無効にする |
| `--inspect-extensions` | `<port>` | 拡張機能のデバッグとプロファイリングを許可する。接続 URI は開発者ツールで確認する |
| `--inspect-brk-extensions` | `<port>` | 同上。ただし**拡張機能ホストを起動直後に一時停止**した状態にする |
| `--disable-lcd-text` | — | LCD 用のフォントレンダリングを無効にする |
| `--disable-gpu` | — | **GPU ハードウェアアクセラレーションを無効にする** |
| `--disable-chromium-sandbox` | — | **Linux で sudo として、あるいは Windows の applocker 環境で昇格ユーザーとしてアプリを起動する必要がある場合にのみ使う** |
| `--locate-shell-integration-path` | `<shell>` | ターミナルのシェル統合スクリプトのパスを表示する。指定できるのは `bash`・`pwsh`・`zsh`・`fish` |
| **`--telemetry`** | — | **Kiro が収集しているテレメトリイベントをすべて表示する** |
| `--transient` | — | 一時的なデータ・拡張機能ディレクトリで実行する（**初回起動と同じ状態**になる） |

> **拡張機能の切り分けに使えます**: 不具合が Kiro 本体か拡張機能かを分けたいときは
> `--disable-extensions` で起動して再現するか確かめます（[03_deployment/01_installation.md](../03_deployment/01_installation.md)）。
>
> **`--telemetry` は何が送られているかを自分で確認する手段**です。
> 収集内容の方針は [03_deployment/05_security.md](../03_deployment/05_security.md) を参照してください。

---

## 6. Subcommands（3個）

| サブコマンド | 内容 |
|------------|------|
| **`chat`** | **プロンプトを渡して、カレントディレクトリでチャットセッションを実行する** |
| `serve-web` | ブラウザでエディタ UI を表示するサーバを実行する |
| `tunnel` | セキュアなトンネル経由で、`vscode.dev` や他のマシンから現在のマシンにアクセスできるようにする |

> ⚠️ **`kiro chat` と `kiro-cli` は別物です。** `kiro chat` は **IDE の実行ファイルのサブコマンド**で、
> `kiro-cli` は**独立した製品である Kiro CLI** です。
> CLI 版の詳細は[姉妹サイト](https://github.com/kamogashira-sys/q-cli-docs)・
> 公式 [CLI commands](https://kiro.dev/docs/reference/cli-commands/) を参照してください。
>
> **`kiro chat` の詳しい引数（プロンプトの渡し方・対応オプション）は `kiro --help` の一覧には出てきません**（**未確認**）。
> 公式ドキュメントにも記述がないため、本サイトでは `--help` に出ている説明文の範囲に留めています。

---

## 7. Kiro 固有として押さえるもの

**38個のうち大半は Code OSS 由来で VS Code と共通です。** Kiro を使う上で意味が違うのは次の3つです。

| 項目 | なぜ Kiro 固有か |
|------|----------------|
| **`--add-mcp`** | MCP サーバ定義の追加。**MCP は Kiro の5つの中核機能の1つ**（[01_features/08_mcp.md](../01_features/08_mcp.md)） |
| **`--telemetry`** | 説明文が「**Kiro** が収集するテレメトリイベント」を示す |
| **`chat` サブコマンド** | ターミナルからプロンプトを渡してエージェントのセッションを開始できる |

---

## 📌 本ページの扱いについて

| 方針 | 内容 |
|------|------|
| **検証対象の数値としては扱いません** | 公式が文書化していないため、公式ページとの突き合わせ（自動検証）ができません。オプション数は参考値です |
| **バージョンを明記します** | 実測したバージョン（**1.0.309**）を必ず併記します。将来の版で変わりうるためです |
| **推測を書きません** | `--help` の出力にない挙動は書きません。確認できない点は「未確認」と明示します |

**自分の環境で確認する方法**:

```
kiro --help
kiro --version
```

---

## 関連ドキュメント

- [02_keyboard-shortcuts.md](02_keyboard-shortcuts.md) - IDE 内のキー操作
- [01_kiro-directory.md](01_kiro-directory.md) - `.kiro/` の設定ファイル仕様
- [01_features/10_editor.md](../01_features/10_editor.md) - エディタ基盤（Code OSS フォークとしての性質・拡張機能レジストリ）
- [01_features/08_mcp.md](../01_features/08_mcp.md) - MCP の設定（`--add-mcp` の対象）
- [03_deployment/01_installation.md](../03_deployment/01_installation.md) - インストールと初回起動
