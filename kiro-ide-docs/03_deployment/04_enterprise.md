# エンタープライズ配布とガバナンス

**組織で Kiro IDE を配るときに決めることをまとめます。バージョンの制御・ガバナンス・拡張機能レジストリが中心です。**

- **一次情報**: [Onboarding quickstart](https://kiro.dev/docs/enterprise/getting-started/)・[Managed updates](https://kiro.dev/docs/enterprise/managed-updates/)・[Governance](https://kiro.dev/docs/enterprise/governance/)・[Settings](https://kiro.dev/docs/enterprise/settings/)・[Supported regions](https://kiro.dev/docs/enterprise/supported-regions/)・[Custom extension registry](https://kiro.dev/docs/editor/extension-registry/)

> **本ページの範囲**: エンタープライズ関連の公式ドキュメントは **IDE と CLI の共有領域**です（`/docs/enterprise/` と `/docs/cli/enterprise/` の内容は同一）。本ページは **Kiro IDE の管理者に必要な範囲**を扱います。AWS コンソール側の操作手順の細部は公式ページに委ねます。

---

## 1. 導入の流れ（公式のオンボーディング手順）

| 順 | やること | 補足 |
|----|---------|------|
| 1 | **AWS アカウントを作る** | すでにあれば不要 |
| 2 | **AWS アカウントにサインインする** | root ユーザーまたは権限のあるロール。最小権限で管理者に Kiro を使わせる方法も公式に用意されています |
| 3 | **ID プロバイダに接続する** | AWS IAM Identity Center のディレクトリにユーザーを追加するか、外部 IdP（Okta・Microsoft Entra ID など）を接続する |
| 4 | **Kiro プロファイルを作りユーザーをサブスクライブする** | プロファイルが**ユーザー ID とサブスクリプション・設定を結びつける要**になります |
| 5 | **ダウンロード手順を配る** | サブスクライブされたユーザーは [downloads ページ](https://kiro.dev/downloads/)から入手し、IdP の資格情報でサインインする |

利用者側のサインイン手順は [02_authentication.md](02_authentication.md) を参照してください。

---

## 2. 対応リージョン

管理者が意識するリージョンは2種類あります。

| 種別 | 意味 |
|------|------|
| **IAM Identity Center のリージョン** | ユーザー ID を管理している IAM Identity Center インスタンスが有効なリージョン |
| **Kiro プロファイルのリージョン** | プロファイルを作成したリージョン。**データが保存され、推論が行われる場所**。IAM Identity Center のリージョンと異なっていてもよい |

### 2.1 Kiro コンソールと Kiro プロファイルが使えるリージョン（4）

- US East (N. Virginia)
- Europe (Frankfurt)
- AWS GovCloud (US-East)
- AWS GovCloud (US-West)

### 2.2 IAM Identity Center 側で使えるリージョン（19）

US East (Ohio) / US East (N. Virginia) / US West (N. California) / US West (Oregon) / Asia Pacific (Mumbai) / Asia Pacific (Osaka) / Asia Pacific (Seoul) / Asia Pacific (Singapore) / Asia Pacific (Sydney) / **Asia Pacific (Tokyo)** / Canada (Central) / Europe (Frankfurt) / Europe (Ireland) / Europe (London) / Europe (Paris) / Europe (Stockholm) / South America (São Paulo) / AWS GovCloud (US-East) / AWS GovCloud (US-West)

> **東京リージョンの位置づけ**: Asia Pacific (Tokyo) は **IAM Identity Center 側では使えます**が、
> **Kiro プロファイル（＝データ保存と推論の場所）としては使えません**。
> 日本の組織で導入する場合、プロファイルは N. Virginia または Frankfurt に置くことになります。

---

## 3. バージョンの制御（管理更新）

**`UpdateUrl` 管理ポリシー**で Kiro IDE を自社ホストの更新サーバに向けられます。これにより段階的な展開とバージョン固定ができます。

### 3.1 ポリシーの設定方法

| OS | 方法 |
|----|------|
| **macOS** | 管理設定（managed preferences）: `sudo defaults write dev.kiro.desktop UpdateUrl -string "https://updates.example.com"`。または `dev.kiro.desktop` ドメインを対象にした MDM プロファイル |
| **Windows** | レジストリ `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Kiro` に `UpdateUrl`（`REG_SZ`）を設定。またはグループポリシー／MDM |
| **Linux** | `/etc/kiro/policy.json` に `{"UpdateUrl": "https://updates.example.com"}` を置く |

### 3.2 `UpdateUrl` の要件

| 要件 | 内容 |
|------|------|
| スキーム | **`https://` のみ**。非 HTTPS や不正な値はログに記録され、Kiro は組み込みの既定値にフォールバックする |
| 末尾スラッシュ | **自動的に削除される** |
| 反映タイミング | **起動時に解決**。変更後は Kiro の再起動が必要 |
| `UpdateMode` との関係 | **`UpdateMode=none` が常に優先**され、`UpdateUrl` の値にかかわらず更新を完全に無効化する |

**設定の確認方法**: Kiro の **Help > About** で更新 URL が有効かを確認できます。URL またはアプリのコミットハッシュが無い場合、Kiro は更新を無効として `MissingConfiguration` ステータスを表示します。

### 3.3 マニフェストのパス

Kiro は「ベース URL・チャネル・OS・アーキテクチャ」から組み立てたパスに JSON マニフェストを要求します。

| プラットフォーム | パス |
|---------------|------|
| macOS | `{base}/{quality}/metadata-darwin-{arch}-{quality}.json` |
| Linux | `{base}/{quality}/metadata-linux-{arch}-{quality}.json` |
| Windows | `{base}/{quality}/metadata-{win-variant}-{quality}.json` |

| プレースホルダ | 値 |
|-------------|----|
| `{quality}` | リリースチャネル。**自社ホストの更新サーバでは常に `stable`** |
| `{arch}` | `x64` または `arm64` |
| `{win-variant}` | `win32-{arch}` にインストール種別のサフィックスを付けたもの: `-system`（既定）・`-user`・`-archive`（ポータブル） |

**例**:

- macOS: `https://updates.example.com/stable/metadata-darwin-arm64-stable.json`
- Windows（ユーザーインストール）: `https://updates.example.com/stable/metadata-win32-x64-user-stable.json`
- Linux: `https://updates.example.com/stable/metadata-linux-x64-stable.json`

自動のバックグラウンド確認では `?bg=true` が付きます。サーバ側は無視してかまいません。

### 3.4 マニフェストの形式

Kiro は `releases` の**最初の要素だけ**を読みます。

```json
{
  "currentRelease": "1.2.0",
  "releases": [
    {
      "version": "1.2.0",
      "updateTo": {
        "version": "1.2.0",
        "pub_date": "2026-07-10",
        "notes": "Kiro-darwin-arm64-1.2.0",
        "name": "Kiro-darwin-arm64-1.2.0",
        "url": "https://updates.example.com/releases/stable/darwin-arm64/signed/1.2.0/kiro-ide-1.2.0-stable-darwin-arm64.zip"
      }
    }
  ]
}
```

| フィールド | 意味 |
|-----------|------|
| `currentRelease` | 最新リリースのバージョン文字列 |
| `releases[0].version` | **インストール済みバージョンと比較される。これが大きいときだけ更新が提示される** |
| `releases[0].updateTo.url` | 署名済みバイナリのダウンロード URL。**HTTPS 必須**。マニフェストと同じホストである必要はない |
| `updateTo.pub_date` | 公開日（`YYYY-MM-DD` 形式） |
| `updateTo.name` / `notes` | 更新プロンプトで利用者に表示されるメタ情報 |

**プラットフォーム別のバイナリ形式**:

| プラットフォーム | 形式と挙動 |
|---------------|----------|
| macOS | **署名済み `.zip`**。ダウンロード・インストール・再起動まで自動 |
| Windows | `.exe` インストーラ。Kiro がダウンロードして直接起動する |
| Linux | アーカイブの URL。**Kiro は既定のブラウザで開くだけ**で、インストールは手動 |

> **macOS の注意**: アプリが適切にコード署名されていないと更新は拒否されます。

### 3.5 段階的な展開

| 順 | 内容 |
|----|------|
| 1 | **リリースをミラーする**。新バージョンが公開されたら `prod.download.desktop.kiro.dev` からインストーラを取得し、自社にホストしたコピーを指すマニフェストを作る |
| 2 | **パイロットグループ**の端末の `UpdateUrl` を、新バージョンを提示するマニフェストに向ける |
| 3 | **検証**する（公式は 3〜7 日を一般的な期間として挙げています） |
| 4 | **全体展開**。本番エンドポイントのマニフェストを新バージョンに更新すると、残りの利用者は次回チェック時に更新を受け取る |

### 3.6 バージョン固定と更新の無効化

| やりたいこと | 方法 |
|------------|------|
| **特定バージョンに固定する** | `releases[0].version` を**現在配布しているバージョンと同じ値**にする。Kiro はマニフェストのバージョンがインストール済みより大きいときだけ更新を提示するため、同じ値を出し続ければ固定になる |
| **更新を完全に止める** | 管理ポリシーで **`UpdateMode=none`** を設定する（`UpdateUrl` と同じ配布方法）。すべての更新チェックがスキップされる |

> **バージョン固定は自動更新チェックだけを制御します。** 利用者が手で別のバージョンを入れることは防げません。
> 完全にロックするには、`prod.download.desktop.kiro.dev` への外向き通信を**ファイアウォールで遮断**して自社エンドポイントのみ許可する必要があります（[05_security.md](05_security.md)）。

---

## 4. ガバナンス（利用できる機能の制限）

Kiro コンソールの **Settings > Shared settings** で管理します。組織レベルで設定し、アカウント単位で上書きすることもできます。

| 対象 | 既定 | 制限方法 |
|------|-----|---------|
| **モデル** | 利用者は Kiro が対応するどのモデルも使える | モデルアクセス管理を有効にし、承認したモデルの一覧を選ぶ。**全クライアントに適用される既定モデル**も設定できる |
| **MCP サーバ** | 利用者はどの MCP サーバも使える | MCP を完全に無効化するか、MCP レジストリで**審査済みサーバの許可リスト**を指定する |
| **API キー** | **利用者は API キーを生成できない** | 生成を許可できる（Kiro CLI 用） |
| **Web ツール** | 利用者は `web_search` と `web_fetch` を使える | アカウントまたは組織の全利用者に対して無効化できる。無効化すると**ツールが利用者から見えなくなり `/tools` に通知が出る** |

---

## 5. Kiro プロファイルの管理設定

Kiro プロファイルで管理者が制御できる設定です。

| 設定 | 内容 |
|------|------|
| **暗号化キー** | 既定では保管データを AWS 管理キーで暗号化。一部の機能では**自前のキー（カスタマー管理キー）**を指定できる |
| **コードリファレンス付きの提案を含める** | 有効にすると、公開コードに似た提案をしたときに**その出典情報を併せて表示**する |
| **Kiro 利用状況ダッシュボード** | Kiro コンソールのメインページにダッシュボードを表示する |
| **Kiro ユーザーアクティビティレポート** | 個々のサブスクライバーの利用テレメトリを収集しレポートとして表示する |
| **プロンプトログ** | **Kiro IDE 上のインライン提案とチャット会話をすべて記録する** |
| **メンバーアカウントのサブスクリプション** | AWS Organizations の管理アカウント管理者の場合、管理アカウントとメンバーアカウントのサブスクリプションを1つの一覧で表示する |
| **Model Context Protocol (MCP)** | サブスクライバーが MCP サーバを使えるようにする |
| **Web Tools** | サブスクライバーが `web_search`・`web_fetch` を使えるようにする |
| **Overages** | プラン上限を超えても作業を続けられるようにする |

> **プロンプトログは利用者の入力内容そのものを記録します。** 組織のポリシーや従業員への周知が必要になる設定です。

---

## 6. 拡張機能レジストリの変更

既定では Kiro は <https://open-vsx.org> を拡張機能マーケットプレイスとして使います。**OS ごとのポリシーで別のレジストリに向けられます**（審査済みの拡張機能だけを置いた社内レジストリなど）。

設定するプロパティは3 OS 共通で **`ExtensionGalleryServiceUrl`** です。

| OS | 設定方法 |
|----|---------|
| **Windows** | `.admx`/`.adml` によるレジストリベースポリシーで `ExtensionGalleryServiceUrl` を定義する。ローカルグループポリシーエディタ（`gpedit.msc`）の **Computer Configuration > Administrative Templates > Kiro > Extensions** で値を設定 |
| **macOS** | `ExtensionGalleryServiceUrl` プロパティを持つ構成プロファイル（`.mobileconfig`）を作り、MDM で配布する。`PayloadType` は `dev.kiro.desktop` |
| **Linux** | `/etc/kiro/policy.json` に `{"ExtensionGalleryServiceUrl": "https://registry.example.com/extensions"}` を置く |

いずれも**設定後に Kiro を再起動**して反映を確認し、そのうえで MDM やグループポリシーで全端末に展開する流れです。サンプルファイル（`.admx`・`.adml`・`.mobileconfig`）は公式ページに全文が掲載されています。

> **Windows のサンプルに含まれる情報**: 公式サンプルには `Kiro >= 0.11.133` という対応バージョン表記が入っています。
> レジストリキーは `Software\Policies\Microsoft\Kiro` です（`Microsoft` を含むパスであることに注意）。

> **`policy.json` は共用されます**: Linux では拡張機能レジストリの設定も管理更新の `UpdateUrl` も
> 同じ `/etc/kiro/policy.json` に書きます。両方使う場合は1つのファイルにまとめてください。

---

## 7. 管理者向けチェックリスト

| # | 決めること | 参照 |
|---|----------|------|
| 1 | Kiro プロファイルを置くリージョン（**東京は選べない**） | §2 |
| 2 | ID プロバイダの接続方式 | §1・[02_authentication.md](02_authentication.md) |
| 3 | 更新の方針（自動 / 固定 / 段階展開 / 無効化） | §3 |
| 4 | 使わせるモデル・MCP サーバ・Web ツール | §4 |
| 5 | プロンプトログ・暗号化キー・利用状況の追跡 | §5 |
| 6 | 拡張機能レジストリを社内に限定するか | §6 |
| 7 | ファイアウォールで許可する URL | [05_security.md](05_security.md) |

---

## 関連ドキュメント

- [01_installation.md](01_installation.md) - 配布形態（`.pkg` は無人インストール向け）
- [02_authentication.md](02_authentication.md) - IAM Identity Center・外部 IdP
- [05_security.md](05_security.md) - 許可 URL・データ保護・エージェントの権限
- [04_reference/03_permissions.md](../04_reference/03_permissions.md) - 権限モデルの詳細
