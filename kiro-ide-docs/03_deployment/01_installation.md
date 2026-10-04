# Kiro IDE のインストール

**対応環境の確認からインストール・初回起動・旧版へのダウングレードまでを扱います。**

- **一次情報**: [Installation](https://kiro.dev/docs/getting-started/installation/)（公式ページ更新日: 2026-10-01。第1・5・6節）・[ダウンロードページ](https://kiro.dev/downloads/)（第2・6節）・[Setup & First Run](https://kiro.dev/docs/ide/setup/)（公式ページ更新日: 2026-08-04。第4節の初回起動とプロジェクトの開き方）
- **本ページの基準バージョン**: **1.2.4**（2026-09-30。第1・2節の対応環境と配布形態）

---

## 1. 対応環境（システム要件）

| OS | 要件 |
|----|------|
| **macOS** | Intel / Apple Silicon の両方 |
| **Windows** | Windows 10 / 11 の **x64 または ARM64** |
| **Linux** | Ubuntu 24 以降・Debian 13 以降・Fedora 40 以降・Arch・Mint 22 以降の **x86_64 または ARM64** |

> **1.1 でネイティブ ARM64 版が加わりました。** Windows と Linux で、x64 エミュレーションに頼らずネイティブの ARM64 版を使えます（[1.1](../02_update/01_changelog.md#v1-1)）。
> 1.0 系の時点では Windows は 64bit（x64）のみで、ARM は非対応でした。

> **公式ページの記述が変わった点**: 以前の Installation ページは Linux の要件を「glibc 2.39 以上」、macOS の要件を「最新のセキュリティ更新が適用されていること」と書いており、本サイトもそれを掲載していました。
> 現行のページ（2026-10-01 更新）の IDE の要件には、**glibc の版と macOS のセキュリティ更新についての記述がありません**（同ページにある「glibc 2.34 以上」は **Kiro CLI** の要件です）。
> IDE の Linux 版が求める glibc の版は、現行の公式ページでは確認できません（**未確認**）。

---

## 2. 配布形態

[ダウンロードページ](https://kiro.dev/downloads/)から入手します。1.2.4 で提供されているのは次の**10種類**です（1.0.242 の時点では7種類。1.1 で Windows と Linux の ARM64 版が加わりました）。

| プラットフォーム | 形式 | ダウンロードページの表記 |
|---------------|------|--------------------|
| macOS（Apple Silicon） | `.dmg` | macOS (Apple Silicon) |
| macOS（Intel） | `.dmg` | macOS (Intel) |
| macOS（Apple Silicon） | `.pkg` | macOS (Apple Silicon, pkg) |
| macOS（Intel） | `.pkg` | macOS (Intel, pkg) |
| Windows（x64） | `.exe` | Windows (x64) |
| **Windows（ARM64）** | `.exe` | Windows (ARM64) |
| Linux（x64） | `.deb` | Linux (x64, Debian/Ubuntu 24+) |
| Linux（x64） | `.tar.gz` | Linux (x64, Universal) |
| **Linux（ARM64）** | `.deb` | Linux (ARM64, Debian/Ubuntu 24+) |
| **Linux（ARM64）** | `.tar.gz` | Linux (ARM64, Universal) |

**`.dmg` と `.pkg` の使い分け**: `.pkg` はコマンドラインや MDM から無人インストールできる形式です。個人利用なら `.dmg`、組織配布なら `.pkg` が扱いやすくなります（配布については [04_enterprise.md](04_enterprise.md) を参照）。

**配信チャネル**: ダウンロード URL は `releases/**stable**/...` の形をしており、**stable チャネルのみ**が公開されています。beta や insiders 相当のチャネルについて公式の記述はありません（未確認）。

**旧版**: ダウンロードページには最新版（IDE 1.2.4）のほかに **IDE 1.1.70・1.1.14・1.0.437・1.0.411・1.0.395・1.0.337・1.0・0.12・0.11** が並んでいます。

> **1.1.14 について**: ダウンロードページには「IDE 1.1.14」がありますが、公式 changelog に 1.1.14 のエントリはありません（1.1 系の changelog は系列ページ「1.1」と専用ページ「1.1.70」のみ）。
> 1.1.14 が系列ページ「1.1」のリリースのビルド番号かどうかは公式に記載がなく、**未確認**です。

> **Kiro CLI を入れる場合**: `curl -fsSL https://cli.kiro.dev/install | bash` です（IDE とは別の製品。CLI の解説は姉妹サイト [q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs) を参照）。

---

## 3. インストール手順

公式の手順は3ステップです。

1. [kiro.dev](https://kiro.dev/) からインストーラをダウンロードする
2. ダウンロードしたファイルを開き、OS ごとの案内に従う
3. Kiro IDE を開く

---

## 4. 初回起動でやること

### 4.1 オンボーディングの5ステップ

初回起動時には次の順で聞かれます。

| 順 | 内容 | 補足 |
|----|------|------|
| 1 | **サインイン** | ソーシャルログインと AWS のログイン方法から選びます。詳細は [02_authentication.md](02_authentication.md) |
| 2 | **VS Code の設定と拡張機能のインポート** | VS Code 以外を使っていた場合はスキップできます。詳細は [03_migrating-from-vscode.md](03_migrating-from-vscode.md) |
| 3 | **テーマの選択** | 用意されたテーマから選びます |
| 4 | **シェル統合の許可** | これを許可すると**エージェントが利用者の代わりにコマンドを実行できる**ようになります |
| 5 | ウェルカムページ | プロジェクトを開いて開始します（[4.2](#42-プロジェクトを開く3つの方法)） |

> **手順4は権限の話です**: シェル統合を許可するとエージェントがコマンドを実行できます。
> 既定ではコマンドごとに承認を求められますが、「信頼するコマンド」に登録したものは確認なしで走ります。
> 何がどこまで許されるかは [05_security.md](05_security.md) と [04_reference/03_permissions.md](../04_reference/03_permissions.md) を確認してください。

### 4.2 プロジェクトを開く（3つの方法）

**ウェルカムページから、次の3つのいずれかでプロジェクトを開きます。** 公式はこの3つを挙げています。

| 方法 | 操作 |
|------|------|
| **メニューから開く** | **File > Open Folder** でプロジェクトのディレクトリを選ぶ |
| **ドラッグ&ドロップ** | プロジェクトのフォルダを Kiro にドラッグ&ドロップする |
| **ターミナルから開く** | プロジェクトのディレクトリで **`kiro .`** を実行する |

> **`kiro` コマンドには他にもオプションがあります。** ファイルを指定して開く・行位置を指定して開く・
> 新しいウィンドウで開くなどは [04_reference/06_launch-options.md](../04_reference/06_launch-options.md) にまとめています
> （公式が文書化していないため実測値です）。

開いた後の画面構成（チャットパネル・サイドバーの各ビュー）は
[01_features/10_editor.md](../01_features/10_editor.md) を参照してください。

---

## 5. 更新

| 方式 | 現状（公式 Installation ページ・2026-10-01 更新） |
|------|------|
| **自動更新** | Kiro IDE は**バックグラウンドで更新を自動的にダウンロード**し、準備ができると再起動して適用するよう通知する |
| **手動で確認** | **Kiro** メニューの **Check for Updates...**。Windows・Linux ではコマンドパレット（`Ctrl + Shift + P`）で **`Kiro: Check for Updates`** を実行する |
| 手動で入れ直す | [downloads ページ](https://kiro.dev/downloads/)から最新版を入れる |

> **公式ページの記述が変わった点**: 以前の公式ページは自動更新を「Auto-updates are being rolled out gradually to users.」（段階的に展開中）と書いており、
> 1.0 系のリリースノートでも「最新の 1.0.x を入れるには kiro.dev/downloads から直接ダウンロードしてください」と案内していました。
> 現行の Installation ページは上の表のとおり、自動更新を前提とした説明に変わっています。

更新の設定項目・チャネル・確認周期についての公式記述は見つかっていません（**未確認**）。組織側で更新を制御する方法は [04_enterprise.md](04_enterprise.md) の管理更新を参照してください。

各バージョンで何が変わったかは [02_update/01_changelog.md](../02_update/01_changelog.md) にまとめています。

---

## 6. 旧版に戻す（ダウングレード）

更新で不具合が出た場合、公式手順で旧版に戻せます。

| 順 | 操作 |
|----|------|
| 1 | [downloads ページ](https://kiro.dev/downloads/)を開く |
| 2 | 上部のダウンロードカードの下にあるバージョン一覧までスクロールする |
| 3 | 入れたいバージョン（例: 「IDE 0.12.x」）を展開する |
| 4 | 自分のプラットフォーム向けインストーラをダウンロードする |
| 5 | **現在のバージョンをアンインストールする**（下表） |
| 6 | ダウンロードしたインストーラを実行する |

**手順5のアンインストール方法**:

| OS | 操作 |
|----|------|
| macOS | アプリケーションから Kiro をゴミ箱へドラッグ |
| Windows | **設定 > アプリ > インストールされているアプリ** からアンインストール |
| Linux | パッケージマネージャに応じて `sudo apt remove kiro` または `sudo dnf remove kiro` |

**設定・拡張機能・サインイン状態は再インストールをまたいで保持されます。**

> ⚠️ **古い版はサービスに接続できなくなります。** ダウンロードページは「**2026-11-09** 以降、**0.11.133 より前の Kiro IDE**（と 1.28.2 より前の Kiro CLI）は Kiro のサービスに接続できなくなる。この日より前に最新版に更新してほしい」と告知しています。
> ダウングレードで 0.11.133 より前の版に戻すと、この日以降は使えなくなります。

> **0.x に戻す場合の注意**: 1.0 でフックの形式とセッションの保存形式が変わっています。
> 1.0 で移行したセッションが 0.x で読めるかについて公式の記述はありません（**未確認**）。
> 変更内容は [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) を参照してください。

---

## 7. 言語ごとの環境構築

公式は言語別のガイドを用意しています（本サイトでは扱いません）。

- [TypeScript and JavaScript](https://kiro.dev/docs/guides/languages-and-frameworks/typescript-javascript-guide/)
- [Java](https://kiro.dev/docs/guides/languages-and-frameworks/java-guide/)
- [Python](https://kiro.dev/docs/guides/languages-and-frameworks/python-guide/)

---

## 関連ドキュメント

- [02_authentication.md](02_authentication.md) - サインイン方法
- [03_migrating-from-vscode.md](03_migrating-from-vscode.md) - VS Code からの移行
- [04_enterprise.md](04_enterprise.md) - 組織へのインストール・バージョン固定
- [02_update/](../02_update/) - 各バージョンの変更内容
