# 認証（サインイン方法）

**Kiro IDE にサインインする5つの方法と、その選び方を扱います。**

- **一次情報**: [Authentication methods](https://kiro.dev/docs/getting-started/authentication/)

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

---

## 2. 方式ごとの手順

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
2. 職場のメールアドレスを入れて組織を特定し **Continue**
3. 組織の ID プロバイダでサインインを完了する

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

ブラウザのリダイレクトが失敗する・サインインエラーが出るといった場合は、公式の [トラブルシューティング（認証の問題）](https://kiro.dev/docs/ide/troubleshooting/#authentication-issues) にプラットフォーム別の対処があります。

---

## 関連ドキュメント

- [01_installation.md](01_installation.md) - インストール（サインインは初回起動の最初のステップ）
- [04_enterprise.md](04_enterprise.md) - 組織での ID プロバイダ接続・サブスクリプション管理
- [05_security.md](05_security.md) - 許可すべき URL・データの扱い
