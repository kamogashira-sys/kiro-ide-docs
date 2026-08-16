# Kiro 公式サイトの構造マップ

**公式サイト `kiro.dev` に何がどこにあるのかを、実測した URL 一覧に基づいて整理します。**

- **一次情報**: [`kiro.dev/sitemap.xml`](https://kiro.dev/sitemap.xml)（**475 URL**）・[`kiro.dev/llms.txt`](https://kiro.dev/llms.txt)（公式のドキュメント索引）
- **数え方**: `/docs/` 配下（§2）は `llms.txt` を機械集計した実測値です（**`sitemap.xml` とは軸が異なるため使い分けます**。下記コラム参照）。それ以外の領域（§1・§3）は `sitemap.xml` の実測値です

> ⚠️ **比較軸に関する注意（2026-08 の公式サイト再構成で判明）**: `sitemap.xml` の `/docs/`（`cli`・`web` 配下を除く）は **188**、
> `llms.txt` の `## IDE` セクション（ドキュメントページの正式索引）は **89** です。両者は**別の集計対象**であり、
> 単純比較できません（`sitemap.xml` には `llms.txt` に載らない一覧ページ・リダイレクト専用ページ等が含まれます）。
> **本ページの §2 の内訳は `llms.txt` ベースの値**（パスの重複を除いた実体ページ数）を採用しています。

---

## 🗺️ サイト全体の内訳（`sitemap.xml` 実測）

| 領域 | URL 数 | 主な内容 |
|------|-------|---------|
| **`/docs/`** | **238** | 公式ドキュメント（下の §2 で `llms.txt` ベースの内訳） |
| **`/changelog/`** | **109** | リリースノート（下の §3 で内訳） |
| `/blog/` | 92 | 技術記事・事例。**一次情報としては最下位**（仕様の根拠には使わない） |
| `/startups/`・`/students/`・`/birthday/` ほかキャンペーン系 | 各1〜4 | 応募条件・規約 |
| `/community/`・`/ambassadors/`・`/events/`・`/showcase/`・`/discord/` | 各1〜2 | コミュニティ |
| 製品トップ・単独ページ | 各1 | 下の §1 |
| **合計** | **475** | |

---

## 1. 製品トップと単独ページ

| URL | 内容 | 本サイトでの用途 |
|-----|------|---------------|
| <https://kiro.dev/> | サイトトップ | — |
| <https://kiro.dev/ide/> | **Kiro IDE 製品ページ** | 製品概要 |
| <https://kiro.dev/cli/> | Kiro CLI 製品ページ | 姉妹サイトの対象 |
| <https://kiro.dev/web/> | Kiro Web 製品ページ | 対象外 |
| <https://kiro.dev/mobile/> | モバイル（Preview） | 専用ドキュメントは `/docs/mobile/` のみ |
| <https://kiro.dev/crew/> | **Kiro Crew 製品ページ**（新設） | 対象外（Kiro Crew は本サイト・姉妹サイトいずれの対象でもない新製品） |
| <https://kiro.dev/downloads/> | **ダウンロード** | インストール手順・配布形態・旧版一覧の一次情報 |
| <https://kiro.dev/pricing/> | 料金プラン | 課金の言及が必要な範囲のみ |
| <https://kiro.dev/enterprise/> | エンタープライズ製品ページ | 組織導入の概要 |
| <https://kiro.dev/faq/> | よくある質問 | 補助 |
| <https://kiro.dev/license/> | ライセンス | 補助 |
| <https://kiro.dev/about/> | 製品について | 補助 |

> **紛らわしい点（2026-08 の再構成で変化）**: エンタープライズ関連の URL は2系統あります。
> **`/enterprise/`（製品ページ）は 200 で存在**します。
> **`/docs/enterprise/`（ドキュメントの索引ページ）は、2026-08 以前は 404 でしたが、現在は `/docs/enterprise/concepts/` への移転案内スタブ**です（HTTP 200 を返しますが実体はありません）。
> 配下のページ（`/docs/enterprise/governance/` など）は **20 本すべて実在**します。
> 索引だけが実体を持たない状態なので、「200 だから中身がある」「404 だから領域自体が無い」のどちらの判断も禁物です。

---

## 2. ドキュメント（`/docs/` = `llms.txt` ベースで **194** ページ）

### 2.1 サーフェス別の内訳（`llms.txt` 実測・パスの重複を除いた実体ページ数）

| URL ツリー | ページ数 | 対象 |
|-----------|-------|------|
| `/docs/`（`cli`・`web` 配下を除く） | **146** | **Kiro IDE + 共有領域**（本サイトの対象） |
| `/docs/cli/` | **34** | Kiro CLI |
| `/docs/web/` | **14** | Kiro Web |

`llms.txt` はこの 146 ページを、さらに次の3区分に整理しています（**IDE 固有・共有・Optional** の3層）。

| 区分（`llms.txt` の見出し） | ページ数 | 説明 |
|------|--------|------|
| **`## IDE`**（IDE 固有＋汎用機能の索引） | **89** | IDE ツリー独自のページ＋ Specs・Hooks・MCP など汎用機能の主要ページ |
| **`## Shared`**（IDE/CLI 共有） | **34** | 同じ内容が `/docs/cli/...` からも読める（§2.3） |
| **`## Optional`**（学習ガイド・請求関連の枝葉） | **21** | Learn by playing 各話・Billing の枝葉ページなど |
| **合計** | **144** | ※`## IDE` の 89 には CLI 固有の参照ページ（`reference/*` 5本など）も含むため、`sitemap.xml` 集計（146）との差2はこの重複起因 |

### 2.2 `## IDE` セクションの構成（89 ページ）

公式索引 `llms.txt` の `## IDE` セクションの並びに沿った一覧です。かっこ内は配下ページ数（自身を除く）。

| # | セクション | パス | 配下 | 本サイトの対応 |
|---|-----------|------|-----|--------------|
| 1 | Get started（Authentication・Your first project・Installation） | `/docs/getting-started/*` | 3 | [03_deployment/](../03_deployment/) |
| 2 | Guides | `/docs/guides` | 5 | 参考（本サイトでは扱わない） |
| 3 | **Hooks** | `/docs/hooks` | 6 | [01_features/05_hooks.md](../01_features/05_hooks.md) |
| 4 | How Kiro works | `/docs/how-kiro-works` | 0 | 参考 |
| 5 | **IDE**（IDE 固有機能の親ページ） | `/docs/ide` | 15 | [01_features/](../01_features/)・[04_reference/](../04_reference/) 各ページ |
| 6 | **Kiroignore** | `/docs/kiroignore` | 0 | [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) |
| 7 | **MCP** | `/docs/mcp` | 7 | [01_features/08_mcp.md](../01_features/08_mcp.md) |
| 8 | Mobile | `/docs/mobile` | 0 | 対象外 |
| 9 | **Permissions**（ルート直下に昇格） | `/docs/permissions` | 0 | [01_features/03_permissions.md](../01_features/03_permissions.md) |
| 10 | **Powers**（新設） | `/docs/powers` | 2 | `01_features/11_powers.md`（Phase 4 で新規作成予定） |
| 11 | Commands and Reference（CLI 側の参照ページ） | `/docs/reference/*` | 5 | 姉妹サイト（`q-cli-docs`）の対象 |
| 12 | Agent Skills | `/docs/skills` | 0 | 参考（Powers・Steering との比較で言及） |
| 13 | **Specs** | `/docs/specs` | 8 | [01_features/01_specs.md](../01_features/01_specs.md) |
| 14 | **Steering** | `/docs/steering` | 0 | [01_features/06_steering.md](../01_features/06_steering.md) |
| 15 | **Custom agents** | `/docs/custom-agents` | 6 | [01_features/07_custom-agents.md](../01_features/07_custom-agents.md) |
| 16 | Built-in tools | `/docs/tools` | 2 | [04_reference/](../04_reference/) |
| 17 | Upgrade guides（Q Developer・VSCode 移行） | `/docs/upgrade-guides/*` | 3 | [03_deployment/03_migrating-from-vscode.md](../03_deployment/03_migrating-from-vscode.md) |
| — | Checkpoints and rewind（ルート直下に昇格） | `/docs/checkpoints` | 0 | [01_features/02_chat.md](../01_features/02_chat.md) §8 |
| — | Cloud sessions（新設） | `/docs/cloud-sessions` | 0 | `01_features/12_cloud-sessions.md`（Phase 4 で新規作成予定） |
| — | Compaction（ルート直下に昇格・改称） | `/docs/compaction` | 0 | [01_features/02_chat.md](../01_features/02_chat.md) §6 |
| — | Configuration scopes（新設） | `/docs/configuration` | 0 | 参考 |

**`/docs/ide` 配下 15 ページの内訳**:

| サブセクション | パス | 配下 |
|--------------|------|-----|
| （索引ページ自身） | `/docs/ide` | — |
| IDE 0.x reference | `/docs/ide/0x-reference` | 0 |
| **Chat** | `/docs/ide/chat` | 7（`autopilot`・`chat-export`・`chat-in-editor`・`dev-servers`・`notifications`・`slash-commands`・`terminal`） |
| （Editor 群。`Chat` の子として索引ではインデントされるが、パス上は `/docs/ide/editor/*`） | `/docs/ide/editor/*` | 5（`extension-registry`・`interface`・**`keyboard-shortcuts`**・`multi-root-workspaces`・`source-control`） |
| Experimental features | `/docs/ide/experimental` | 1（`focus-mode`） |
| Setup & First Run | `/docs/ide/setup` | 0 |
| Troubleshooting | `/docs/ide/troubleshooting` | 0 |
| **What's new in IDE 1.0** | `/docs/ide/whats-new-v1` | 4（`agent-config`・`compaction`・`hooks`・`permissions`） |

> **`llms.txt` の構造上の注意（変わらず該当）**: `Chat` の配下に Editor 群のページがインデントされて並んでいます。パスの階層とインデントの階層が一致していないため、**インデントだけでページの所属を判断しないでください**。上の表ではパスに従って区分しています。

### 2.3 IDE/CLI 共有ドキュメント（`## Shared` = 34ページ）

`llms.txt` は共有ページを明示的に区分しており、次の注記があります。

> Pages in the "Shared" section are accessible from both the IDE (`/docs/billing`) and CLI (`/docs/cli/billing`) URL trees; the content is identical.

つまり**どちらのツリーから読んでも内容は同一**です。34ページの内訳（実測）:

| 共有領域 | ページ数 | 主なパス | 本サイトでの扱い |
|---------|--------|---------|--------------|
| **Enterprise**（billing 含む） | **20** | `/docs/enterprise/*`（concepts・governance・identity-provider・**managed-updates**・monitor-and-track・billing ほか） | [03_deployment/](../03_deployment/) で IDE 読者に必要な範囲を要約 |
| **Privacy and security** | **8** | `/docs/privacy-and-security`＋配下（data-protection・firewalls・vpc-endpoints ほか） | [03_deployment/](../03_deployment/) のセキュリティページ |
| **Billing**（個人向け・`/docs/billing` 直下） | **3** | `/docs/billing`＋配下（contact-support・subscription-portal） | 言及が必要な範囲のみ |
| **Models** | **3** | `/docs/models`＋配下（available-models・effort） | [04_reference/05_models.md](../04_reference/05_models.md) |

> **共有ページでも IDE 主体の内容がある**: `/docs/enterprise/managed-updates` は「**Kiro IDE** を自己ホストの更新サーバへ向ける `UpdateUrl` 管理ポリシー」の説明で、実体は IDE の話です。「共有 = IDE には関係ない」ではありません。
>
> **Q Developer からの移行ページは Shared から IDE セクションへ移動**しています（`/docs/upgrade-guides/migrating-from-q*`）。旧版では Shared 扱いでしたが、現在は `## IDE` セクションの Upgrade guides に含まれます。

### 2.4 新設・改称された主要ページ（2026-08 の再構成以降）

| 新設・改称ページ | 関係する版 | 本サイトでの扱い |
|-----------|----------|---------------|
| `/docs/powers`・`/docs/powers/create`・`/docs/powers/installation` | 1.0.288（Agent Plugin 形式の Powers） | `01_features/11_powers.md`（Phase 4 で新規作成予定） |
| `/docs/cloud-sessions` | 1.0.293（Cloud Sessions プレビュー） | `01_features/12_cloud-sessions.md`（Phase 4 で新規作成予定） |
| `/docs/skills` | — | フォルダ + `SKILL.md` 構造（単一 `.md` ファイルではない） |
| `/docs/ide/whats-new-v1/*`（旧 `/docs/whats-new-1-0`。スラッグ改称＋配下4ページ新設） | — | [02_update/03_migration-to-1.0.md](../02_update/03_migration-to-1.0.md) の出典を精緻化 |
| `/docs/checkpoints`（旧 `/docs/chat/checkpoints`。ルート直下へ昇格） | — | [01_features/02_chat.md](../01_features/02_chat.md) §8 |
| `/docs/compaction`（旧 `/docs/chat/summarization`。ルート直下へ昇格＋改称） | — | [01_features/02_chat.md](../01_features/02_chat.md) §6 |
| `/docs/permissions`（旧 `/docs/chat/permissions`。ルート直下へ昇格） | — | [01_features/03_permissions.md](../01_features/03_permissions.md) |
| `/docs/kiroignore`（旧 `/docs/editor/kiroignore`。ルート直下へ昇格） | — | [04_reference/01_kiro-directory.md](../04_reference/01_kiro-directory.md) |
| `/docs/custom-agents/subagents`（旧 `/docs/chat/subagents`。ルート直下へ昇格） | — | [01_features/02_chat.md](../01_features/02_chat.md) §7 |
| `/docs/configuration`（新設） | — | 各ページの設定範囲の参考 |
| `/docs/ide`（旧 `/docs/editor/codebase-indexing` 単独ページが消滅し集約） | — | [01_features/10_editor.md](../01_features/10_editor.md) |
| `/docs/ide/setup`（旧 `/docs/chat/vibe` 単独ページが消滅し集約。**Vibe/Spec の二択ピッカーも廃止**） | — | ✅ [01_features/02_chat.md](../01_features/02_chat.md) 第3節を現行仕様（Free-flow chat・4ワークフロー・セッション中の切替）に改訂済み |

---

## 3. Changelog（`/changelog/` = 109 URL・`sitemap.xml` 実測）

### 3.1 サーフェス別の内訳

| ツリー | URL 数 | 内容 |
|-------|-------|------|
| `/changelog/cli/` | 32 | Kiro CLI |
| **`/changelog/ide/`** | **29** | **Kiro IDE**（本サイトの対象） |
| `/changelog/models/` | 19 | モデルの追加・変更 |
| `/changelog/general/` | 10 | 全体のお知らせ |
| `/changelog/web/` | 8 | Kiro Web |
| `/changelog/page/2/`〜 | 若干数 | 全サーフェス混載の索引ページ |
| `/changelog/` | 1 | 索引トップ |
| `feed.atom`・`feed.rss` | 2 | フィード（[02_information-sources.md](02_information-sources.md)） |

> ⚠️ **IDE changelog の内訳（3.2）は本改訂時点で個別カウントを実施していません。** 1.0.288/293/309 反映後に `make check-kiro-ide-freshness` で再集計してください。

### 3.2 IDE changelog の形式

**2つのページ形式**:

| 形式 | 例 | 構成 |
|------|-----|------|
| **系列ランディング** | `/changelog/ide/1-0/` | 機能ごとの節（`#permissions` などのアンカー付き）＋ Improvements ＋ Fixes ＋ **その系列のパッチ一覧** |
| **リリース専用ページ** | `/changelog/ide/1-0-242/` | タイトル＋日付＋ Improvements・Fixes のみ（パッチ一覧なし） |

**注意点（継続して該当）**:

1. **0.2 系には系列ランディングがない**。`/changelog/ide/0-2/` は存在せず、専用ページ4本（`0-2-13`・`0-2-38`・`0-2-59`・`0-2-68`）だけがあります。
2. **同じビルドが2箇所に載る**。系列ページのパッチ一覧（例: `/changelog/ide/1-0#patch-1-0-242`）と専用ページ（`/changelog/ide/1-0-242/`）の両方に存在するバージョンがあります。
3. **URL からバージョンが読めないページが1本ある**。0.9.40 は `/changelog/ide/external-identity-provider-support-for-kiro-ide/` というスラッグ形式です。バージョン番号を URL から機械抽出する処理では既知の例外として扱う必要があります。

各バージョンの内容は [02_update/01_changelog.md](../02_update/01_changelog.md)（1.0 系）と [02_update/02_changelog-0x.md](../02_update/02_changelog-0x.md)（0.x 系）にまとめています。

---

## 4. URL を叩くときの注意（実測）

公式ページを手元で取得する場合、次の点でつまずきます。

| # | 現象 | 対処 |
|---|------|------|
| 1 | **末尾スラッシュなしは 301 リダイレクト**。`/changelog/ide/1-0` は本文を返さず `Location: /changelog/ide/1-0/` を返す | URL に末尾スラッシュを付けるか、リダイレクトを追う（`curl -L`） |
| 2 | **User-Agent が空だと 403**（CloudFront が `Request blocked.` を返す） | User-Agent を送る（`curl` の既定 UA でも 200。**空文字を明示指定した場合だけ**弾かれる） |
| 3 | **🔴 旧 URL 体系のページは 200 を返す移転スタブになっている場合がある（2026-08 の再構成で判明）** | **HTTP ステータスだけでは判定不可**。本文に `moved to <a href="...">` が含まれるかを確認する。**スタブは `-L` を付けてもリダイレクトしない**（`redirect_url` が空のまま 200 を返す） |

`.md` 版の有無:

| 対象 | `.md` 版 | 例 |
|------|---------|-----|
| **ドキュメント** | ✅ 全ページに存在 | `/docs/ide/chat` → [`/docs/ide/chat.md`](https://kiro.dev/docs/ide/chat.md)（**旧 `/docs/chat.md` は 404**。パス変更に伴い `.md` companion の URL も変わる） |
| **Changelog** | ❌ **存在しない**（404） | `/changelog/ide/1-0-242.md` → 404 |

そのため changelog は HTML から読む必要があります。詳細は [02_information-sources.md](02_information-sources.md) を参照してください。

---

## 関連ドキュメント

- [情報源一覧](02_information-sources.md) - `llms.txt`・`sitemap.xml`・フィードの使い分け
- [02_update/](../02_update/) - 全バージョンのアップデート情報
- [03_deployment/](../03_deployment/) - インストール・エンタープライズ配布
