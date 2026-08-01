# Kiro 公式サイトの構造マップ

**公式サイト `kiro.dev` に何がどこにあるのかを、実測した URL 一覧に基づいて整理します。**

- **一次情報**: [`kiro.dev/sitemap.xml`](https://kiro.dev/sitemap.xml)（**463 URL**）・[`kiro.dev/llms.txt`](https://kiro.dev/llms.txt)（公式のドキュメント索引）
- **数え方**: 本ページの件数はすべて `sitemap.xml` を機械集計した実測値です

---

## 🗺️ サイト全体の内訳

| 領域 | URL 数 | 主な内容 |
|------|-------|---------|
| **`/docs/`** | **238** | 公式ドキュメント（下の §2 で内訳） |
| **`/changelog/`** | **104** | リリースノート（下の §3 で内訳） |
| `/blog/` | 88 | 技術記事・事例。**一次情報としては最下位**（仕様の根拠には使わない） |
| `/startups/`・`/students/`・`/birthday/` ほかキャンペーン系 | 各1〜4 | 応募条件・規約 |
| `/community/`・`/ambassadors/`・`/events/`・`/showcase/`・`/discord/` | 各1〜2 | コミュニティ |
| 製品トップ・単独ページ | 各1 | 下の §1 |
| **合計** | **463** | |

---

## 1. 製品トップと単独ページ

| URL | 内容 | 本サイトでの用途 |
|-----|------|---------------|
| <https://kiro.dev/> | サイトトップ | — |
| <https://kiro.dev/ide/> | **Kiro IDE 製品ページ** | 製品概要 |
| <https://kiro.dev/cli/> | Kiro CLI 製品ページ | 姉妹サイトの対象 |
| <https://kiro.dev/web/> | Kiro Web 製品ページ | 対象外 |
| <https://kiro.dev/mobile/> | モバイル | 専用ドキュメントなし |
| <https://kiro.dev/downloads/> | **ダウンロード** | インストール手順・配布形態・旧版一覧の一次情報 |
| <https://kiro.dev/pricing/> | 料金プラン | 課金の言及が必要な範囲のみ |
| <https://kiro.dev/enterprise/> | エンタープライズ製品ページ | 組織導入の概要 |
| <https://kiro.dev/faq/> | よくある質問 | 補助 |
| <https://kiro.dev/license/> | ライセンス | 補助 |
| <https://kiro.dev/about/> | 製品について | 補助 |

> **紛らわしい点**: エンタープライズ関連の URL は2系統あります。
> **`/enterprise/`（製品ページ）は 200 で存在**しますが、
> **`/docs/enterprise/`（ドキュメントの索引ページ）は 404** です。
> ただし `/docs/enterprise/governance/` のような**配下のページは 22 本すべて実在**します。
> 索引だけが無い状態なので、「404 だから領域自体が無い」と判断しないでください。

---

## 2. ドキュメント（`/docs/` = 238 URL）

### 2.1 サーフェス別の内訳

| URL ツリー | URL 数 | 対象 |
|-----------|-------|------|
| `/docs/`（`cli`・`web` 配下を除く） | **117** | **Kiro IDE**（本サイトの対象） |
| `/docs/cli/` | 101 | Kiro CLI |
| `/docs/web/` | 20 | Kiro Web |

IDE ツリーの 117 ページは、さらに次の2つに分かれます。

| 区分 | ページ数 | 説明 |
|------|--------|------|
| **IDE 固有** | **74** | IDE ツリーにしか存在しない |
| **IDE/CLI 共有** | **43** | 同じ内容が `/docs/cli/...` からも読める（§2.3） |

### 2.2 IDE 固有ドキュメントのセクション構成

公式索引 `llms.txt` の `## IDE` セクションの並びに沿った一覧です。かっこ内は配下ページ数。

| # | セクション | パス | 配下 | 本サイトの対応 |
|---|-----------|------|-----|--------------|
| 1 | Get started | `/docs/` | — | [00_information](README.md) |
| 2 | **Chat** | `/docs/chat` | 14 | [01_features/02_chat.md](../01_features/02_chat.md) ほか |
| 3 | **Custom agents** | `/docs/custom-agents` | 1 | [01_features/07_custom-agents.md](../01_features/07_custom-agents.md) |
| 4 | （Editor 群） | `/docs/editor/*` | 7 | [01_features/10_editor.md](../01_features/10_editor.md)・[04_reference/02_keyboard-shortcuts.md](../04_reference/02_keyboard-shortcuts.md) |
| 5 | Experimental features | `/docs/experimental` | 1 | [01_features/09_agent-focus-mode.md](../01_features/09_agent-focus-mode.md) |
| 6 | （Getting started 群） | `/docs/getting-started/*` | 3 | [03_deployment/](../03_deployment/) |
| 7 | Guides | `/docs/guides` | 15 | 参考（本サイトでは扱わない） |
| 8 | **Hooks** | `/docs/hooks` | 6 | [01_features/05_hooks.md](../01_features/05_hooks.md) |
| 9 | **MCP** | `/docs/mcp` | 4 | [01_features/08_mcp.md](../01_features/08_mcp.md) |
| 10 | Powers | `/docs/powers` | 2 | 未収録（公開後に追補） |
| 11 | Agent Skills | `/docs/skills` | 0 | 未収録（公開後に追補） |
| 12 | **Specs** | `/docs/specs` | 8 | [01_features/01_specs.md](../01_features/01_specs.md) |
| 13 | **Steering** | `/docs/steering` | 0 | [01_features/06_steering.md](../01_features/06_steering.md) |
| 14 | **What's new in IDE 1.0** | `/docs/whats-new-1-0` | 0 | [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) |
| — | Troubleshooting | `/docs/troubleshooting` | 0 | 参考 |

**配下の数え方**: 「配下」列は索引ページ自身を除いた子ページ数です。ただし Editor 群と Getting started 群には索引ページがないため、その2行はページ数そのものを示しています（`/docs/editor/` は **404**、`/docs/getting-started/` は `/docs/` へリダイレクト）。

**`llms.txt` の構造上の注意**: `Custom agents` の配下に `editor/*` の7ページが、`Experimental features` の配下に `getting-started/*` の3ページがインデントされて並んでいます。パスの階層とインデントの階層が一致していないため、**インデントだけでページの所属を判断しないでください**。上の表ではパスに従って区分しています。

`Chat` 配下の14ページ（`/docs/chat/*`）:
`autopilot`・`chat-export`・`chat-in-editor`・`checkpoints`・`dev-servers`・`diagnostics`・`notifications`・**`permissions`**・`slash-commands`・`subagents`・`summarization`・`terminal`・`vibe`・`webtools`

`Editor` 群の7ページ（`/docs/editor/*`）:
`codebase-indexing`・`extension-registry`・**`interface`**・**`keyboard-shortcuts`**・**`kiroignore`**・`multi-root-workspaces`・`source-control`

### 2.3 IDE/CLI 共有ドキュメント（43ページ）

`llms.txt` は共有ページを明示的に区分しており、次の注記があります。

> Pages in the "Shared" section are accessible from both the IDE (`/docs/billing`) and CLI (`/docs/cli/billing`) URL trees; the content is identical.

つまり**どちらのツリーから読んでも内容は同一**です。IDE ツリー側の43ページの内訳:

| 共有領域 | ページ数 | 主なパス | 本サイトでの扱い |
|---------|--------|---------|--------------|
| **Enterprise** | 22 | `/docs/enterprise/*`（governance・identity-provider・**managed-updates**・monitor-and-track ほか） | [03_deployment/](../03_deployment/) で IDE 読者に必要な範囲を要約 |
| **Billing** | 11 | `/docs/billing`＋配下 | 言及が必要な範囲のみ |
| **Privacy and security** | 8 | `/docs/privacy-and-security`＋配下（data-protection・firewalls・vpc-endpoints ほか） | [03_deployment/](../03_deployment/) のセキュリティページ |
| Models | 1 | `/docs/models` | [04_reference/05_models.md](../04_reference/05_models.md) |
| Migrating from Amazon Q Developer | 1 | `/docs/migrating-from-q-developer` | 言及のみ |

> **共有ページでも IDE 主体の内容がある**: `/docs/enterprise/managed-updates` は「**Kiro IDE** を自己ホストの更新サーバへ向ける `UpdateUrl` 管理ポリシー」の説明で、実体は IDE の話です。「共有 = IDE には関係ない」ではありません。

---

## 3. Changelog（`/changelog/` = 104 URL）

### 3.1 サーフェス別の内訳

| ツリー | URL 数 | 内容 |
|-------|-------|------|
| `/changelog/cli/` | 30 | Kiro CLI |
| **`/changelog/ide/`** | **26** | **Kiro IDE**（本サイトの対象） |
| `/changelog/models/` | 19 | モデルの追加・変更 |
| `/changelog/general/` | 10 | 全体のお知らせ |
| `/changelog/web/` | 8 | Kiro Web |
| `/changelog/page/2/`〜`/9/` | 8 | 全サーフェス混載の索引ページ |
| `/changelog/` | 1 | 索引トップ |
| `feed.atom`・`feed.rss` | 2 | フィード（[02_information-sources.md](02_information-sources.md)） |

### 3.2 IDE changelog の26 URL

| 区分 | 件数 | URL |
|------|-----|-----|
| 索引 | 3 | `/changelog/ide/`・`/changelog/ide/page/2/`・`/page/3/` |
| **系列ランディング** | **12** | `0-1`・`0-3`・`0-4`・`0-5`・`0-6`・`0-7`・`0-8`・`0-9`・`0-10`・`0-11`・`0-12`・`1-0` |
| **リリース専用ページ** | **11** | `0-2-13`・`0-2-38`・`0-2-59`・`0-2-68`・`1-0-52`・`1-0-89`・`1-0-116`・`1-0-138`・`1-0-182`・`1-0-242`・`external-identity-provider-support-for-kiro-ide` |

**2つのページ形式**:

| 形式 | 例 | 構成 |
|------|-----|------|
| **系列ランディング** | `/changelog/ide/1-0/` | 機能ごとの節（`#permissions` などのアンカー付き）＋ Improvements ＋ Fixes ＋ **その系列のパッチ一覧** |
| **リリース専用ページ** | `/changelog/ide/1-0-242/` | タイトル＋日付＋ Improvements・Fixes のみ（パッチ一覧なし） |

**注意点3つ**:

1. **0.2 系には系列ランディングがない**。`/changelog/ide/0-2/` は存在せず、専用ページ4本（`0-2-13`・`0-2-38`・`0-2-59`・`0-2-68`）だけがあります。
2. **同じビルドが2箇所に載る**。1.0.242 は専用ページ `/changelog/ide/1-0-242/` と系列ページのアンカー `/changelog/ide/1-0#patch-1-0-242` の両方に存在します。
3. **URL からバージョンが読めないページが1本ある**。0.9.40 は `/changelog/ide/external-identity-provider-support-for-kiro-ide/` というスラッグ形式です。バージョン番号を URL から機械抽出する処理では既知の例外として扱う必要があります。

各バージョンの内容は [02_update/01_changelog.md](../02_update/01_changelog.md)（1.0 系）と [02_update/02_changelog-0x.md](../02_update/02_changelog-0x.md)（0.x 系）にまとめています。

---

## 4. URL を叩くときの注意（実測）

公式ページを手元で取得する場合、次の2点でつまずきます。

| # | 現象 | 対処 |
|---|------|------|
| 1 | **末尾スラッシュなしは 301 リダイレクト**。`/changelog/ide/1-0` は本文を返さず `Location: /changelog/ide/1-0/` を返す | URL に末尾スラッシュを付けるか、リダイレクトを追う（`curl -L`） |
| 2 | **User-Agent が空だと 403**（CloudFront が `Request blocked.` を返す） | User-Agent を送る（`curl` の既定 UA でも 200。**空文字を明示指定した場合だけ**弾かれる） |

`.md` 版の有無:

| 対象 | `.md` 版 | 例 |
|------|---------|-----|
| **ドキュメント** | ✅ 全ページに存在 | `/docs/chat` → [`/docs/chat.md`](https://kiro.dev/docs/chat.md) |
| **Changelog** | ❌ **存在しない**（404） | `/changelog/ide/1-0-242.md` → 404 |

そのため changelog は HTML から読む必要があります。詳細は [02_information-sources.md](02_information-sources.md) を参照してください。

---

## 関連ドキュメント

- [情報源一覧](02_information-sources.md) - `llms.txt`・`sitemap.xml`・フィードの使い分け
- [02_update/](../02_update/) - 全バージョンのアップデート情報
- [03_deployment/](../03_deployment/) - インストール・エンタープライズ配布
