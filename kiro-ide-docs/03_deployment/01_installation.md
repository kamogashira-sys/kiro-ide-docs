# Kiro IDE のインストール

**対応環境の確認からインストール・初回起動・旧版へのダウングレードまでを扱います。**

- **一次情報**: [Installation](https://kiro.dev/docs/getting-started/installation/)（公式ページ更新日: 2026-10-05。第1・5・6節）・[ダウンロードページ](https://kiro.dev/downloads/)（第2・6節）・[Setup & First Run](https://kiro.dev/docs/ide/setup/)（公式ページ更新日: 2026-08-04。第4節の初回起動とプロジェクトの開き方）・[IDE Troubleshooting](https://kiro.dev/docs/ide/troubleshooting/)（公式ページ更新日: 2026-10-20。第8節）・公式 changelog（第5・8節）
- **本ページの基準バージョン**: 第1節の対応環境は Installation ページ（公式ページ更新日: 2026-10-05）で再確認し、表の内容に変更はありません。第2節の配布形態（10種類）は **1.2.4**（2026-09-30）時点の記載のままで、最新版（1.4.10）の時点では確認できていません（第2節）

---

## 1. 対応環境（システム要件）

| OS | 要件 |
|----|------|
| **macOS** | Intel / Apple Silicon の両方 |
| **Windows** | Windows 10 / 11 の **x64 または ARM64** |
| **Linux** | Ubuntu 24 以降・Debian 13 以降・Fedora 40 以降・Arch・Mint 22 以降の **x86_64 または ARM64** |

> **1.1 でネイティブ ARM64 版が加わりました。** Windows と Linux で、x64 エミュレーションに頼らずネイティブの ARM64 版を使えます（[1.1.14](../02_update/01_changelog.md#v1-1-14)）。
> 1.0 系の時点では Windows は 64bit（x64）のみで、ARM は非対応でした。

> **公式ページの記述が変わった点**: 以前の Installation ページは Linux の要件を「glibc 2.39 以上」、macOS の要件を「最新のセキュリティ更新が適用されていること」と書いており、本サイトもそれを掲載していました。
> 現行のページ（2026-10-05 更新）の IDE の要件には、**glibc の版と macOS のセキュリティ更新についての記述がありません**（同ページにある「glibc 2.34 以上」は **Kiro CLI** の要件です）。
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

> **配布形態の再確認について**: ダウンロードページの HTML から取得できる配布ファイルの表記は、macOS 4種・Windows（x64）・Linux（x64）2種の計7種だけで、Windows（ARM64）と Linux（ARM64）の表記を含みません。上の10種類が最新版（1.4.10）でも提供されているかは、公式の記述を確認できていないため**未確認**です。

**`.dmg` と `.pkg` の使い分け**: `.pkg` はコマンドラインや MDM から無人インストールできる形式です。個人利用なら `.dmg`、組織配布なら `.pkg` が扱いやすくなります（配布については [04_enterprise.md](04_enterprise.md) を参照）。

**配信チャネル**: ダウンロード URL は `releases/**stable**/...` の形をしており、**stable チャネルのみ**が公開されています。beta や insiders 相当のチャネルについて公式の記述はありません（未確認）。

**旧版**: ダウンロードページの埋め込みデータ（`releases`）には、最新版の IDE 1.4.10 のほかに、**1.4.5・1.4.0・1.3.11・1.3.0・1.2.56・1.2.37・1.2.4・1.1.70・1.1.14・1.0.437・1.0.411・1.0.395 …** が載っています。1.x 系は 1.0.0 までの 29 版で、公式 changelog の 1.x 系の版（[アップデート情報](../02_update/01_changelog.md)）と一致します。画面上の並びは、公式の記述を確認できていないため未確認です。

> **1.1.14 について**: 公式 changelog の系列ページ `/changelog/ide/1-1/` のページに表示される版表記は **1.1.14** です。ダウンロードページの「IDE 1.1.14」は、この系列ページのリリースにあたります（[1.1.14](../02_update/01_changelog.md#v1-1-14)）。

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
| 1 | **サインイン** | ソーシャルログインと AWS のログイン方法から選びます（公式 [Setup & First Run](https://kiro.dev/docs/ide/setup/) は、Google・GitHub・AWS Builder ID・組織の ID プロバイダを挙げています）。詳細は [02_authentication.md](02_authentication.md) |
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

| 方式 | 現状（公式 Installation ページ・2026-10-05 更新） |
|------|------|
| **自動更新** | Kiro IDE は**バックグラウンドで更新を自動的にダウンロード**し、準備ができると再起動して適用するよう通知する |
| **手動で確認** | **Kiro** メニューの **Check for Updates...**。Windows・Linux ではコマンドパレット（`Ctrl + Shift + P`）で **`Kiro: Check for Updates`** を実行する |
| 手動で入れ直す | [downloads ページ](https://kiro.dev/downloads/)から最新版を入れる |

> **公式ページの記述が変わった点**: 以前の公式ページは自動更新を「Auto-updates are being rolled out gradually to users.」（段階的に展開中）と書いており、
> 1.0 系のリリースノートでも「最新の 1.0.x を入れるには kiro.dev/downloads から直接ダウンロードしてください」と案内していました。
> 現行の Installation ページは上の表のとおり、自動更新を前提とした説明に変わっています。

> **Windows のアプリ内更新（1.2.37 の修正）**: IDE 1.2.37 から開始した更新では、インストールの開始後に Windows のアプリ内更新をキャンセルできてしまう問題が修正され、キャンセルに関連するインストール失敗が減りました（[1.2.37](../02_update/01_changelog.md#v1-2-37)）。この修正の対象は、1.2.37 から開始した更新です。

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

> ⚠️ **2027-01-15 にも同様の告知があります。** ダウンロードページは「**2027-01-15** 以降、**0.11.133 から 0.12.291 までの Kiro IDE**（と 1.28.2 から 2.5.0 までの Kiro CLI）は Kiro のサービスに接続できなくなる。この日より前に最新版に更新してほしい」とも告知しています。1.x 系の版（1.0.0 以降）は、この2つの告知が挙げる範囲に含まれません。

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

## 8. Linux で Kiro が起動しないとき（Ubuntu 24.04 以降）

> 出典: [IDE Troubleshooting](https://kiro.dev/docs/ide/troubleshooting/)（公式ページ更新日: 2026-10-20）・[1.4.0](../02_update/01_changelog.md#v1-4-0)・[1.4.5](../02_update/01_changelog.md#v1-4-5)

Ubuntu 24.04 以降で、Kiro がまったく開かない、または起動した直後に終了することがあります。ターミナルから `kiro` を実行すると、`chrome-sandbox` が root の所有でモード 4755 でなければならないという趣旨の、`The SUID sandbox helper binary was found, but is not configured correctly.` のエラーが表示されます。

**原因（公式の説明）**: Ubuntu 24.04 は、AppArmor のプロファイルが許可しない限り、アプリがユーザー名前空間を作ることを禁じます。Kiro のサンドボックスにはユーザー名前空間が必要なため、プロファイルがないと `chrome-sandbox` ヘルパーに切り替わり、これは root が所有しているときにだけ動きます。

### 8.1 推奨: `.deb` パッケージを入れる

**Kiro 1.4.0 から、`.deb` パッケージは Kiro 用の AppArmor プロファイルを入れる**ため、追加の手順なしで起動します（1.4.0 の修正は「Ubuntu 24.04 以降の Ubuntu で、.deb パッケージからインストールした後に Kiro が起動しない問題」です）。[ダウンロードページ](https://kiro.dev/downloads/)から `.deb` を入手して入れます。

```bash
sudo apt install ./<file>.deb
```

- 1.4.0 より前に `.deb` を入れていた場合は、Kiro を更新するか、新しい `.deb` を同じ方法で入れます。
- `.tar.gz` で動かしていた場合は、`.deb` を入れた後にアプリケーションメニューまたは `kiro` から起動し、展開したフォルダを削除します。

### 8.2 `.tar.gz` を使い続ける場合

root だけが変更できるフォルダへ Kiro を移し、そのパス用の AppArmor プロファイルを追加します。公式の手順は次のとおりです（`~/path/to/kiro` は展開したフォルダに置き換えます）。

```bash
sudo mv ~/path/to/kiro /opt/kiro
sudo chown -R root:root /opt/kiro
sudo chmod 4755 /opt/kiro/chrome-sandbox
sudo tee /etc/apparmor.d/kiro >/dev/null <<'EOF'
abi <abi/4.0>,
include <tunables/global>
profile kiro /opt/kiro/kiro flags=(unconfined) {
  userns,
  include if exists <local/kiro>
}
EOF
sudo apparmor_parser -r /etc/apparmor.d/kiro
```

その後は `/opt/kiro/bin/kiro` で起動します。プロファイルが適用されるのは `/opt/kiro/kiro` だけで、そのフォルダは root が所有するため、ほかのプログラムは使えません。公式は、**ホームディレクトリのフォルダにプロファイルを向けない**よう注意しています（そのパスに書き込めるものが同じ権限を得てしまうため）。

> ⚠️ 公式は、`sysctl kernel.apparmor_restrict_unprivileged_userns=0` で制限を無効にすることを**避けるよう**案内しています。Kiro だけでなく、マシン上のすべてのプログラムに対して保護を無効にするためです。

### 8.3 ほかの Linux ディストリビューション

強化されたカーネルや、`kernel.unprivileged_userns_clone=0` の Debian など、ユーザー名前空間を制限するシステムでも、同じ `chrome-sandbox` のエラーが出ることがあります。公式の案内は次のとおりです。

- システムが `.deb` に対応しているなら、`.deb` を入れる（その `chrome-sandbox` は root 所有でモード 4755 になっている）
- そうでなければ、root だけが変更できるフォルダへ Kiro を移し、`chrome-sandbox` を root 所有・モード 4755 にする（8.2 の `sudo mv`・`sudo chown -R root:root`・`sudo chmod 4755` の3行と同じ。起動は `/opt/kiro/bin/kiro`）
- 8.2 の AppArmor プロファイルは**使わない**（これらのシステムはこの制限に AppArmor を使わず、`/etc/apparmor.d` がないものもある）

### 8.4 起動時の警告（1.4.5）

IDE 1.4.5 では、展開した tarball から Kiro を起動すると失敗しそうな場合（システムがユーザー名前空間を制限しているとき）に、Kiro が問題を説明し、トラブルシューティングの手順へのリンクを示す警告を出力します（[1.4.5](../02_update/01_changelog.md#v1-4-5)）。警告が出たときは、上の手順に従います。

---

## 関連ドキュメント

- [02_authentication.md](02_authentication.md) - サインイン方法
- [03_migrating-from-vscode.md](03_migrating-from-vscode.md) - VS Code からの移行
- [04_enterprise.md](04_enterprise.md) - 組織へのインストール・バージョン固定
- [02_update/](../02_update/) - 各バージョンの変更内容
