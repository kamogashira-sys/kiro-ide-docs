# Powers（動的に読み込まれる専門知識パッケージ）

**MCP サーバ・Skills・ステアリングをバンドルし、会話の文脈に応じて動的に読み込む仕組みです。1.0.288 で導入されました。**

- **一次情報**: [Powers](https://kiro.dev/docs/powers/)（公式ページ更新日: 2026-08-06）・[Install powers](https://kiro.dev/docs/powers/installation/)・[Create powers](https://kiro.dev/docs/powers/create/)
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
| `dev.kiro/`（任意） | ステアリングファイルなど Kiro 固有の拡張 |

```
my-power/
├── plugin.json          # 必須マニフェスト
├── skills/              # Agent Skills
│   └── setup/
│       ├── SKILL.md
│       └── references/
├── mcp.json             # MCP サーバ設定
└── dev.kiro/            # Kiro 固有の拡張
    └── steering/
```

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

---

## 関連リンク

- [公式ドキュメント](https://kiro.dev/docs/powers/)
- [12_cloud-sessions.md](12_cloud-sessions.md) - 同時期に導入された新機能
- [07_custom-agents.md](07_custom-agents.md) - カスタムエージェント（Powers と組み合わせて使う）
- [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) - `.kiro/` ファイル仕様（Agent Skills の配置先）

---

**最終更新**: 2026-08-16
**対象バージョン**: Kiro IDE 1.0.288+
