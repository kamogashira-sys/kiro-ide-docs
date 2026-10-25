# 認証（サインイン方法）

**Kiro IDE にサインインする5つの方法と、その選び方を扱います。**

- **一次情報**: [Authentication](https://kiro.dev/docs/getting-started/authentication/)（公式ページ更新日: 2026-10-17）・[IDE Troubleshooting](https://kiro.dev/docs/ide/troubleshooting/)（公式ページ更新日: 2026-10-20。第5節）・公式 changelog [1.3.11](https://kiro.dev/changelog/ide/1-3-11/)・[1.4.0](https://kiro.dev/changelog/ide/1-4/)（第2.6節）

> **前提**: Kiro は AWS のアプリケーションですが、**AWS アカウントを用意しなくても単体で使えます**。
> ダウンロードして外部アカウントの設定なしにすぐ使い始められる、というのが公式の説明です。

---

## 1. 5つの認証方式

| 方式 | 公式の説明 | 主な用途 |
|------|----------|---------|
| **GitHub** | GitHub アカウントとの統合 | 個人 |
| **Google** | Google の資格情報でサインイン | 個人 |
| **AWS Builder ID** | 個人開発者向けの手早いセットアップ | 個人 |
| **AWS IAM Identity Center** | エンタープライズ向けの認証 | 組織 |
| **外部 ID プロバイダ** | 組織の IdP（Microsoft Entra ID・Okta など）経由で接続 | 組織 |

> **組織の管理端末では、表示される方法が絞られていることがあります**（1.2 以降）。管理者はサインイン制御で
> 許可する方法を制限し、組織のサインイン情報を事前入力し、サインイン画面に **Need help signing in?** のリンクを出せます。
> 許可されていない方法を選ぶと、Kiro は許可されている選択肢を示します（公式 [Sign-in controls](https://kiro.dev/docs/enterprise/governance/sign-in/)・
> 公式ページ更新日: 2026-10-09）。管理者向けの設定は [04_enterprise.md](04_enterprise.md#7-サインイン制御12-以降) を参照してください。

> **公式の対応表（IDE）**: 現行の Authentication ページ（公式ページ更新日: 2026-10-17）の対応表では、IDE は上の5つの方式すべてに対応しています。API キーによる認証は CLI だけの対応で、IDE には載っていません。

---

## 2. 方式ごとの手順

> **公式ページの記述が変わった点**: 現行の Authentication ページ（公式ページ更新日: 2026-10-17）は、IDE のサインインを「ウェルカム画面でサインインを選ぶと、Kiro が既定のブラウザへリダイレクトし、認証後にブラウザに IDE へ戻る案内が表示されて、IDE がサインイン済みになる」と説明しています。GitHub・Google・AWS Builder ID は「プロバイダーを選び、ブラウザで認証し、Kiro アプリを認可する」流れで、GitHub では認可するアプリが `kirodotdev` と表示されます。
> **現行のページには、下の 2.1〜2.5 に書いたボタン名（`Sign in with GitHub`・`Login with AWS Builder ID` など）や各ステップの画面の記述はありません**。これらのボタン名が現行の IDE の画面と一致するかは**未確認**（現行のページに記述がなく、確認できません）です。なお、[04_enterprise.md](04_enterprise.md#73-ルールの形式) が引く Sign-in controls のページ（2026-10-09）は、AWS IAM Identity Center をサインイン画面で **Your organization** と表示すると説明しています。

### 2.1 GitHub

1. Kiro で **Sign in with GitHub** を選ぶ（既定のブラウザにリダイレクトされます）
2. ユーザー名またはメールアドレスとパスワードを入れて **Sign in**
3. **Authorize kirodotdev** を選んで Kiro アプリを認可する

### 2.2 Google

1. Kiro で **Sign in with Google** を選ぶ
2. 使いたい Google アカウントを選ぶ
3. **Continue** を選んで Kiro アプリを認可する

### 2.3 AWS Builder ID

1. Kiro で **Login with AWS Builder ID** を選ぶ
2. メールアドレスを入れて **Next**
3. パスワードを入れて **Sign in**
4. **Allow access** を選んで Kiro アプリを認可する

### 2.4 AWS IAM Identity Center

1. Kiro で **Sign in with AWS IAM Identity Center** を選ぶ
2. **Start URL** に管理者やヘルプデスクから渡された開始 URL を入れる
3. **Region** に ID ディレクトリをホストしている AWS リージョンを入れて **Continue**

### 2.5 外部 ID プロバイダ

1. Kiro で **Your organization** を選ぶ
2. 職場のメールアドレスを入れて組織を特定し **Continue**（現行の Authentication ページは、職場のメールアドレスか、管理者から渡された Kiro の開始 URL のどちらかを入れると説明しています）
3. 組織の ID プロバイダでサインインを完了する

現行の Authentication ページは、**Your organization** を管理者が管理するアカウントの入口として、AWS IAM Identity Center（開始 URL と、ID ディレクトリをホストする AWS リージョンが必要）と外部 ID プロバイダー（Okta・Microsoft Entra ID など）のどちらにも使えると説明しています。外部 ID プロバイダーの入口は、AWS GovCloud (US) リージョンの入口でもあります。

### 2.6 サインイン待機画面の Cancel（1.4.0）

サインインが完了しないとき、「We will take you to your default web browser to sign in」の画面が Cancel を無視する問題が、IDE 1.4.0 で修正されました。Cancel でサインインの開始画面に戻り、キャンセルした試行が再試行を妨げることもありません（[1.4.0](../02_update/01_changelog.md#v1-4-0)）。

### 2.7 IAM Identity Center のサインインと Kiro プロファイルの選択（1.3.11）

IDE 1.3.11 で、次の2点が変わりました（[1.3.11](../02_update/01_changelog.md#v1-3-11)）。

- ブラウザを開けないとき、IAM Identity Center のサインインが無言で待機していた問題を修正しました。Kiro は失敗を表示し、再試行できます
- Kiro プロファイルを複数持つエンタープライズアカウントで、保存されたプロファイルがないときに最初のプロファイルが割り当てられていた問題を修正しました。Kiro は **Choose a Kiro profile to continue** を表示し、選べます。プロファイルが1つだけのときは、従来どおり自動で選択されます

### 2.8 サインアウト

IDE のコマンドパレットで **Kiro: Sign Out** を実行します（現行の Authentication ページの記述）。

---

## 3. 選び方

| 状況 | 推奨 |
|------|------|
| 個人で試したい | **GitHub / Google / AWS Builder ID** のいずれか（最も手数が少ない） |
| 組織が IAM Identity Center を運用している | **AWS IAM Identity Center** |
| 組織が Microsoft Entra ID や Okta を使っている | **外部 ID プロバイダ**（管理者側の接続設定が必要。[04_enterprise.md](04_enterprise.md)） |
| **AWS GovCloud (US) を使う** | **IAM Identity Center または外部 IdP のみ**（§4） |

---

## 4. 注意点

### 4.1 個人サブスクライバーのデータ利用（重要）

公式の注記:

> ソーシャルログイン（GitHub・Google など）または AWS Builder ID で有料の Kiro サブスクリプションを利用しているユーザーは *individual subscribers* とみなされます。Kiro Free Tier と individual subscribers の一部のコンテンツは、**サービス改善に利用される場合があります**。

**オプトアウトが可能**です。詳細は公式の [Service improvement](https://kiro.dev/docs/privacy-and-security/data-protection/#service-improvement) を参照してください。データの扱いは [05_security.md](05_security.md) にもまとめています。

組織で使う場合にこの扱いを避けたいときは、IAM Identity Center や外部 IdP による認証を選ぶことになります。

### 4.2 AWS GovCloud (US) の制約

| 項目 | 内容 |
|------|------|
| 使える認証方式 | **IAM Identity Center と外部 ID プロバイダのみ** |
| 使えない認証方式 | **GitHub・Google・AWS Builder ID**（個人向けのログイン方法） |
| GovCloud を使っているかの見分け方 | 認証時の Start URL に `us-gov-home` が含まれる（例: `https://start.us-gov-home.awsapps.com/directory/d-XXXXXXXXXX`） |
| インストーラ | **商用リージョンと同一**。IAM Identity Center 認証が自動的に適切な GovCloud リージョンへ振り分ける |
| **必要バージョン** | **Kiro IDE 0.9.2 以降**（Kiro CLI は 1.25.0 以降） |

### 4.3 サインインはブラウザを使う

サインインは既定のブラウザを開いて `app.kiro.dev` にアクセスします。この通信は **IDE のプロキシ設定を通らず OS のネットワークスタックを使います**。ファイアウォールがある環境では、IDE のプロキシ設定とは別にネットワーク側で許可が必要です。許可すべき URL は [05_security.md](05_security.md) にまとめています。

---

## 5. うまくいかないとき

ブラウザのリダイレクトが失敗する・サインインエラーが出るといった場合は、公式の [トラブルシューティング（認証の問題）](https://kiro.dev/docs/ide/troubleshooting/#authentication-issues) にプラットフォーム別の対処があります（公式ページ更新日: 2026-10-20）。

| 症状（公式） | 公式の案内 |
|------|------|
| Identity Center で `There was an error signing you in` と表示される | サブスクリプションが有効であることを確認する。IAM Identity Center の認証には有効なサブスクリプションが必要。Kiro のプロファイルは、現在 US East (N. Virginia) と Europe (Frankfurt) のリージョンで対応している |
| Identity Center のセッションが期限切れになる | 既定のタイムアウトは8時間で、定期的に再認証が必要。管理者はより長いセッション時間を設定できる |
| 組織の一部の利用者だけが接続できない。サインイン後に「No profiles available」と表示される | TLS インスペクションを行う社内のファイアウォールが、Kiro のエンドポイントへの接続を妨げることが、よくある原因として挙げられている。影響を受ける利用者が `curl -v https://runtime.us-east-1.kiro.dev` と `curl -v https://management.us-east-1.kiro.dev` で接続を確認する |
| Windows でブラウザにリダイレクトされない | 管理者として開いたコマンドプロンプトで `--enable-logging` を付けて起動し、ログを確認する |
| macOS でブラウザにリダイレクトされない | **Help → Toggle Developer Tools** の Console タブでエラーを確認する。`ioreg` コマンドが PATH にないことが、よくある原因として挙げられている |

---

## 関連ドキュメント

- [01_installation.md](01_installation.md) - インストール（サインインは初回起動の最初のステップ）
- [04_enterprise.md](04_enterprise.md) - 組織での ID プロバイダ接続・サブスクリプション管理
- [05_security.md](05_security.md) - 許可すべき URL・データの扱い
