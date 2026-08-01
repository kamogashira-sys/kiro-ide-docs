# Kiro IDE のインストール

**対応環境の確認からインストール・初回起動・旧版へのダウングレードまでを扱います。**

- **一次情報**: [Installation](https://kiro.dev/docs/getting-started/installation/)・[ダウンロードページ](https://kiro.dev/downloads/)
- **本ページの基準バージョン**: **1.0.242**（2026-07-28）

---

## 1. 対応環境（システム要件）

| OS | 要件 |
|----|------|
| **macOS** | Intel / Apple Silicon の両方。**最新のセキュリティ更新が適用されていること** |
| **Windows** | Windows 10 / 11 の **64bit のみ**。**ARM は現時点で非対応** |
| **Linux** | **glibc 2.39 以上**。公式が例として挙げるディストリビューション: Ubuntu 24 以降・Debian 13 以降・Fedora 40 以降・Arch Linux・Linux Mint 22 以降 |

> **Linux で最初に確認すること**: glibc のバージョンは `ldd --version` で確認できます。
> 2.39 未満のディストリビューション（Ubuntu 22.04 など）では動きません。

---

## 2. 配布形態

[ダウンロードページ](https://kiro.dev/downloads/)から入手します。1.0.242 で提供されているのは次の7種類です。

| プラットフォーム | 形式 | ダウンロードページの表記 |
|---------------|------|--------------------|
| macOS（Apple Silicon） | `.dmg` | macOS (Apple Silicon) |
| macOS（Intel） | `.dmg` | macOS (Intel) |
| macOS（Apple Silicon） | `.pkg` | macOS (Apple Silicon, pkg) |
| macOS（Intel） | `.pkg` | macOS (Intel, pkg) |
| Windows | `.exe` | Windows (x64) |
| Linux | `.deb` | Linux (Debian/Ubuntu 24+) |
| Linux | `.tar.gz` | Linux (Universal) |

**`.dmg` と `.pkg` の使い分け**: `.pkg` はコマンドラインや MDM から無人インストールできる形式です。個人利用なら `.dmg`、組織配布なら `.pkg` が扱いやすくなります（配布については [04_enterprise.md](04_enterprise.md) を参照）。

**配信チャネル**: ダウンロード URL は `releases/**stable**/...` の形をしており、**stable チャネルのみ**が公開されています。beta や insiders 相当のチャネルについて公式の記述はありません（未確認）。

**旧版**: ダウンロードページには最新版のほかに **1.0.228・1.0.212・1.0.203・1.0・0.12・0.11** が並んでいます（2026-08-01 時点）。

> **Kiro CLI を入れる場合**: `curl -fsSL https://cli.kiro.dev/install | bash` です（IDE とは別の製品。CLI の解説は姉妹サイト [q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs) を参照）。

---

## 3. インストール手順

公式の手順は3ステップです。

1. [kiro.dev](https://kiro.dev/) からインストーラをダウンロードする
2. ダウンロードしたファイルを開き、OS ごとの案内に従う
3. Kiro IDE を開く

---

## 4. 初回起動でやること

初回起動時には次の順で聞かれます。

| 順 | 内容 | 補足 |
|----|------|------|
| 1 | **サインイン** | ソーシャルログインと AWS のログイン方法から選びます。詳細は [02_authentication.md](02_authentication.md) |
| 2 | **VS Code の設定と拡張機能のインポート** | VS Code 以外を使っていた場合はスキップできます。詳細は [03_migrating-from-vscode.md](03_migrating-from-vscode.md) |
| 3 | **テーマの選択** | 用意されたテーマから選びます |
| 4 | **シェル統合の許可** | これを許可すると**エージェントが利用者の代わりにコマンドを実行できる**ようになります |
| 5 | ウェルカムページ | プロジェクトを開いて開始します |

> **手順4は権限の話です**: シェル統合を許可するとエージェントがコマンドを実行できます。
> 既定ではコマンドごとに承認を求められますが、「信頼するコマンド」に登録したものは確認なしで走ります。
> 何がどこまで許されるかは [05_security.md](05_security.md) と [04_reference/03_permissions.md](../04_reference/03_permissions.md) を確認してください。

---

## 5. 更新

| 方式 | 現状 |
|------|------|
| **自動更新** | **段階的に展開中**。公式は「Auto-updates are being rolled out gradually to users.」と記載 |
| 手動更新 | [downloads ページ](https://kiro.dev/downloads/)から最新版を入れる |

1.0 系のリリースノートでは、公式が「最新の 1.0.x を入れるには kiro.dev/downloads から直接ダウンロードしてください」と案内しています。**自動更新が来るのを待つ運用は現時点では前提にできません。**

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
