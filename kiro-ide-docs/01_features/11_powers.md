# Powers（動的に読み込まれる専門知識パッケージ）

**MCP サーバ・Skills・ステアリングをバンドルし、会話の文脈に応じて動的に読み込む仕組みです。1.0.288 で導入されました。**

- **一次情報**: [Powers](https://kiro.dev/docs/powers/)（公式ページ更新日: 2026-10-21）・[Install powers](https://kiro.dev/docs/powers/installation/)（公式ページ更新日: 2026-10-23）・[Create powers](https://kiro.dev/docs/powers/create/)（公式ページ更新日: 2026-10-08）
- **導入バージョン**: **1.0.288**（2026-08-07 ※§4.1.1 参照）
- **Kiro CLI 版の対応ページ**: CLI 3.0（Early Access）で対応（利用・作成とも `v3` 扱い）。[`docs/cli/v3/`](https://kiro.dev/docs/cli/v3/) 配下に個別の Powers ページはなく、共通ページ [`docs/powers/`](https://kiro.dev/docs/powers/) が正

> **これは何か**: **エージェントに、その場で必要な専門知識を渡す仕組みです。** MCP サーバをすべて事前に読み込むのではなく、
> 会話中のキーワードに応じて Power を動的に読み込みます。「payment」「checkout」と言えば Stripe の Power が起動し、
> 話題がデータベースに移れば Supabase の Power に切り替わります。

---

## 1. なぜ必要か（公式の説明）

### 1.1 コンテキスト不足の問題

**フレームワークの文脈がないと、エージェントは推測で動きます。** Stripe の API を呼べても、冪等キーを使うべきだと知っているとは限りません。Neon にクエリを投げられても、サーバーレスのコネクションプーリングを理解しているとは限りません。組み込みの専門知識がないと、ドキュメントを手動で読みながら出力を調整する作業になります。

### 1.2 コンテキスト過多の問題

**MCP サーバを5つ接続すると、コードを1行も書く前に100種類以上のツール定義が読み込まれます。** 5サーバーで5万トークン超（コンテキストウィンドウの40%）を消費することもあります。ツールが増えれば結果が良くなるはずですが、構造化されていない文脈はエージェントを圧倒し、応答を遅く・品質を低くします。

**Powers はこの両方を解決します**: 会話のキーワードに応じて必要な Power だけを動的に読み込みます。

---

## 2. 動作の仕組み

**タスクを開始すると、Kiro は次の手順で Power を評価します:**

| 順 | 内容 |
|----|------|
| 1 | タスクの説明を読む |
| 2 | インストール済みの Power をタスクと照合する |
| 3 | 関連する Power だけをコンテキストに読み込む |

Stripe の Power をワンクリックでインストールした場合、「payment」「checkout」と言及すると Power が起動し、Stripe の MCP ツールと Skills がコンテキストに読み込まれます。決済の話が終わってデータベース作業に移ると、Supabase の Power が起動し Stripe は非アクティブになります。

---

## 3. Power の構造（Agent Plugins 仕様）

**Power は [Agent Plugins](https://agent-plugins.org/) 仕様に従います。** これは AI エージェントを拡張する再利用可能なコンポーネントをパッケージ化する、オープンでベンダー中立な形式です。Amazon・Cursor・Microsoft・OpenAI・Vercel がメンテナに参加しています。

**Power は必須のマニフェストと任意のコンポーネントを持つディレクトリです:**

| コンポーネント | 内容 |
|--------------|------|
| **`plugin.json`**（必須） | Power を識別し、起動のためのキーワードを宣言するマニフェスト |
| `skills/`（任意） | タスク固有の指示・スクリプト・参考資料を提供する **Agent Skills** |
| `mcp.json`（任意） | ツール連携のための MCP サーバ設定 |

```
my-power/
├── plugin.json          # 必須マニフェスト
├── skills/              # Agent Skills
│   └── setup/
│       ├── SKILL.md
│       └── references/
└── mcp.json             # MCP サーバ設定
```

> 本サイトのこれまでの記述には、`dev.kiro/`（ステアリングファイルなど Kiro 固有の拡張を置く任意のディレクトリ）がありました。現行の公式 Powers ページ（2026-10-21）と Create powers ページ（2026-10-08）の構成の説明にはこのディレクトリの記述がなく、現在もそのとおりかは未確認です。

> **旧形式（`POWER.md`）で作られた Power は引き続き動作します。** 新規に作る場合は Agent Plugins 形式が推奨されており、既存の Power は Power Builder で変換できます。

---

## 4. Powers・Skills・Steering の違い（公式の説明）

**3つは役割が異なります。**

| 概念 | 役割 | 使うとき |
|------|------|---------|
| **Powers** | MCP ツール・Skills・知識を1つのインストール可能なパッケージにまとめたプラグイン。文脈に応じて動的に起動する | ツールとガイダンスの両方が必要な連携。Powers は Skills をコンポーネントとして含められる |
| **Skills** | 特定のタスクをエージェントに導く、単体で可搬な指示パッケージ。単独でも Power にバンドルされても存在できる | 共有・import したい再利用可能なワークフロー |
| **Steering** | Kiro 固有の、エージェントの振る舞いを形づくるコンテキスト。`always`・`auto`・`fileMatch`・`manual` の各モードに対応 | プロジェクトの標準・規約 |

---

## 5. Powers の特徴（公式の説明）

| 特徴 | 内容 |
|------|------|
| **可搬なプラグイン形式** | Agent Plugins 仕様に従うため、**互換性のあるエージェントクライアント間でそのまま動く** |
| **動的な MCP ツール読み込み** | 従来の MCP サーバは全ツールを事前に読み込むが、Powers はオンデマンドで読み込み、ベースラインのコンテキスト使用量を抑えながら多数の技術にアクセスできる |
| **オープンなエコシステム** | Datadog・Dynatrace・Figma・Neon・Netlify・Postman・Supabase・Stripe・Strands SDK・AWS Aurora など、ローンチパートナーの厳選 Power を閲覧できる。GitHub URL からコミュニティ製 Power もインストールできる |
| **ワンクリックインストール** | Kiro 内または kiro.dev で Power を閲覧し、Install を押すだけ。JSON 設定ファイルの記述やコマンドライン操作は不要 |

---

## 6. インストールと作成

| 操作 | 方法 |
|------|------|
| **インストール** | マーケットプレイスまたは GitHub リポジトリから（詳細: [Install powers](https://kiro.dev/docs/powers/installation/)） |
| **作成** | Agent Plugins 仕様に沿って独自の Power を構築し、コミュニティに共有できる（詳細: [Create powers](https://kiro.dev/docs/powers/create/)） |

**対応状況（公式の Capability 表）**:

| Capability | IDE | CLI | Web | Mobile |
|-----------|-----|-----|-----|--------|
| Install and use powers | ✓ | v3 | ✓ | — |
| Create powers | ✓ | v3 | — | — |

### 6.0 IDE からインストールする手順と、Available Powers の検索（1.2.56）

公式 [Install powers](https://kiro.dev/docs/powers/installation/#from-the-ide)（2026-10-23）の IDE での手順です。

| 順 | 操作 |
|----|------|
| 1 | Powers パネルを開く（Ghosty のアイコンに稲妻が付いたアイコンを選ぶ） |
| 2 | **Available Powers** で検索アイコンを選び、表示名で絞り込むために入力する。一致するものがないときは、空の結果のメッセージを表示する |
| 3 | Power を選んで詳細を表示する |
| 4 | **+ Install** を選ぶ |

インストール後は **Try** で Power のオンボーディングを試せます。その Power に関係する質問をすると、Kiro のエージェントが自動で有効にして使います。Available Powers の名前での絞り込みは、1.2.56 で追加されました（[1.2.56](../02_update/01_changelog.md#v1-2-56)）。

### 6.1 クラウドと同期された Powers を IDE で試す（1.0.437）

クラウドと同期された Powers は**アカウントに紐づく設定（account-backed configuration）**であり、エージェントをクラウドのサンドボックスで動かす [Cloud Sessions](12_cloud-sessions.md) とは**別の仕組み**です。ローカルの Power を Kiro Web アカウントに上げるには、Kiro Web の **Agent Config > Cloud Config**（Configuration Sync）を使います（手順は公式の [Configuration Sync](https://kiro.dev/docs/web/cloud-configuration/) を参照）。

> **Kiro Web の画面名の変化**: 本サイトのこれまでの記述は、アップロードの画面を **Settings > Sync**、Powers の管理画面を **Settings > Powers** と書いていました。現行の公式 Powers ページ（2026-10-21）・Cloud sessions ページ（2026-10-23）・Configuration Sync ページ（2026-10-21）は、それぞれ **Agent Config > Cloud Config**・**Agent Config > Powers & MCP** と書いています。本サイトは現行の公式の表記に従います。

**Kiro IDE 1.0.437 以降**では、Kiro Web の **Agent Config > Powers & MCP** で管理している Powers が、IDE のインストール済み Powers の一覧に表示されます。

| 挙動 | 内容 |
|------|------|
| **クラウドインジケータ** | クラウドと同期された各 Power にインジケータが付く |
| **Try power** | 選ぶとその Power をそのまま使える |
| **詳細の確認** | 詳細を開くと、束ねられた Skills と MCP 構成を確認できる |
| **管理** | これらの Powers は Kiro Web（**Agent Config > Powers & MCP**）で管理する |

**束ねられた MCP 構成はその Power に付随します。** Power が有効になったときに使えるようになるもので、**単独で同期される MCP サーバではありません**。リポジトリの `.kiro/settings/mcp.json` に置いたプロジェクトの MCP サーバは、これまでどおりプロジェクト設定としてリポジトリとともに移動します（スコープの全体像は [12_cloud-sessions.md](12_cloud-sessions.md) §6.2 を参照）。

### 6.2 Power の MCP サーバに接続できないとき（1.4.10）

Power の MCP サーバが接続に失敗しても、**ターンはそのサーバなしで実行されます**。チャットは、エラーカードではなく**警告**を表示します。**サインインが必要なサーバは、従来どおりサインインを求めます**（[1.4.10](../02_update/01_changelog.md#v1-4-10)）。この項目の公式の機能ページは changelog からリンクされていません（未確認）。MCP 全般は [08_mcp.md](08_mcp.md) を参照してください。

### 6.3 インストール済み Power の表示と manifest の情報（1.4.26）

**1.4.26 以降**、Powers パネルの **Installed** 一覧と Power の詳細ビューは、インストール済みの Power の manifest にある情報を表示します（公式 [Install powers](https://kiro.dev/docs/powers/installation/)・[1.4.26](../02_update/01_changelog.md#v1-4-26)）。

| 項目 | 内容（公式） |
|------|------------|
| 読み込む manifest | `plugin.json` があればそれを読む。なければ `POWER.md` の front matter を読む |
| カタログの値との関係 | manifest が宣言した **description・author・repository・keywords** の値が、カタログの値を置き換える。manifest が省略した項目は、カタログの値のまま |
| リポジトリのリンク | HTTP または HTTPS の場合だけ表示する |
| Kiro CLI でインストールした Power | IDE の Powers パネルの **Installed** 一覧にも表示される（1.4.26 以降）。1.4.26 の修正により、パネルが壊れる、または一覧から消えることがなくなった |

### 6.4 カスタム Power のインストールと更新

公式 [Install powers](https://kiro.dev/docs/powers/installation/)（2026-10-23）の IDE での手順です。Kiro は Agent Plugins 形式（`plugin.json`）と旧形式（`POWER.md`）の両方に対応し、インストールの操作はどちらの形式でも同じです。公式は、Power がサードパーティのツールであり、別の規約が適用される場合があるため、信頼できる提供元からだけインストールし、ドキュメントとライセンスを確認するよう警告しています。

| 方法 | 操作（公式） |
|------|------------|
| **kiro.dev から** | [kiro.dev/powers](https://kiro.dev/powers) で Power を選び、**Add to Kiro** を選ぶ。Kiro IDE が開き、ワンクリックでインストールを完了できる |
| **公開 GitHub の URL から** | Powers パネルの **Add Custom Power** → **Import power from GitHub** → リポジトリの URL を入力 → **Install**。各 Power は、パッケージのルートに有効な `plugin.json` または `POWER.md` が必要。1つのリポジトリに、それぞれ別のディレクトリで複数の Power を置ける |
| **ローカルのパスから** | 非公開リポジトリで作成・管理する Power は、リポジトリをローカルにクローンしてインストールする。**Add Custom Power** → **Import power from a folder** → `plugin.json` または `POWER.md` を含む Power のディレクトリを選ぶ → **Install** |
| **更新** | Powers パネルで Power を選び、**Check for updates** を選ぶ。更新があれば **Install updates** を選ぶ。Power はリモートのリポジトリから更新され、最新版が適用される |

| Power に MCP が含まれる場合 | 内容（公式） |
|--------------------------|------------|
| 共通 | Kiro がサーバー名に名前空間を付けて衝突を避け、MCP サーバーを管理する |
| **Agent Plugins 形式（`plugin.json`）** | MCP サーバーは Kiro が内部で管理し、ユーザー単位の `~/.kiro/settings/mcp.json` には追加されない。Power とともに有効・無効になる |
| **旧形式（`POWER.md`）** | MCP サーバーは `~/.kiro/settings/mcp.json` の Powers の節に登録される |

**セキュリティ**（公式）: Power は Skills・スクリプト・MCP サーバーを Kiro に加えられます。Power のツール呼び出しは、ほかのツールと同じ Kiro の権限設定に従います。ローカルの MCP サーバーは、サンドボックスで隔離しない限り、あなたのユーザーの権限でマシン上で動き、コードの実行とあなたが読めるファイルの読み取りができます。インストールの前に、Power のソースと要求するアクセスを確認してください。削除するには、IDE の Powers パネルで Power の **Uninstall** を選びます。

---

## 関連リンク

- [公式ドキュメント](https://kiro.dev/docs/powers/)
- [12_cloud-sessions.md](12_cloud-sessions.md) - 同時期に導入された新機能
- [07_custom-agents.md](07_custom-agents.md) - カスタムエージェント（Powers と組み合わせて使う）
- [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) - `.kiro/` ファイル仕様（Agent Skills の配置先）

---

**最終更新**: 2026-09-13
**対象バージョン**: Kiro IDE 1.0.288+（§6.1 のクラウド同期 Powers は 1.0.437 以降、§6.3 は 1.4.26 以降）
