# コミット前チェックリスト

このチェックリストは、ドキュメントの品質を保証するために、コミット前に必ず確認してください。

---

## 🚫 必須確認事項

### 1. 出典の確認

- [ ] 全ての技術的記述に一次情報の出典がある
- [ ] バージョン番号は公式 changelog（<https://kiro.dev/changelog/ide/>）で確認済み
- [ ] 設定ファイル形式・設定値は公式ドキュメント（<https://kiro.dev/docs/>）に基づく
- [ ] 公式に確認できない事項は「未確認」と明示している（推測で断定していない）

### 2. 表現の確認

- [ ] 推測表現（「おそらく」「と思われる」等）を使用していない
- [ ] 「以降」「以前」等の曖昧な表現を避けている
- [ ] 断定的な記述には必ず根拠がある
- [ ] **Kiro IDE と Kiro CLI を混同していない**（`kiro-cli` コマンドが IDE の文脈に混入していないか）

### 3. リンクの確認

- [ ] 全ての内部リンクが有効である（相対パス）
- [ ] 全ての外部リンクが有効である
- [ ] **kiro.dev の changelog リンクは末尾スラッシュ付き**（`/changelog/ide/1-0/`。スラッシュなしは **301 リダイレクト**になる）
- [ ] **Kiro CLI 版へのリンクは `docs/cli/v3/` を指している**（非 v3 ページは 2.x 系の別仕様。特に hooks は完全な別物）

### 4. 公開範囲の確認

- [ ] ローカル管理対象（`work_plans/`・`05_meta/`・`06_embedded-docs/`・`work_records/`）がコミットに含まれていない

---

## 📋 バージョン番号チェック

### Kiro IDE のバージョン

Kiro IDE は `1.0.NNN`（3桁ビルド番号）でほぼ週次リリースされます。バージョン番号を記載する場合、以下で確認します。

1. **公式 changelog ページで確認**（**日付の正**）

   ```bash
   # 末尾スラッシュ必須（無しは 301）。UA は curl の既定でも 200 が返るが、
   # **空文字を明示指定すると 403** になるため `-A ""` を書かないこと
   curl -sSL -A "Mozilla/5.0" -o /tmp/kiro-ide-1-0.html "https://kiro.dev/changelog/ide/1-0/"
   ```

2. **パッチ全量は埋め込み JSON から抽出**（画面上は「+N more」で折りたたまれる）

   ```bash
   python3 - <<'PY'
   import re, json
   s = open('/tmp/kiro-ide-1-0.html', encoding='utf-8').read().replace('\\"', '"')
   m = re.search(r'"patches":(\[.*?\])', s)
   for p in json.loads(m.group(1)):
       print(p['version'], p['date'])
   PY
   ```

3. **Atom フィードは速報検知のみに使う**

   ```bash
   curl -sS https://kiro.dev/changelog/feed.atom
   ```

   > ⚠️ **フィード単独では網羅できません**。同一ビルドを2エントリで重複配信し、ローリングウィンドウから溢れた版を取り落とします（1.0.165 の実例）。必ず埋め込み JSON と和集合を取ってください。

4. **日付の扱い**
   - 正は**公式ページの表示日**（`Jul 28, 2026` 形式）。本サイトでは **ISO `YYYY-MM-DD`** に変換して記載
   - **タイムゾーン変換は行わない**（フィードの時刻は使わない）
   - **取得日は本文に書かない**

---

## 🔍 検証方法

### 自動検証

```bash
cd <リポジトリのルート>
make check-kiro-ide-quick    # 執筆中の常用（links / structure のみ）
make check-kiro-ide-ignore   # 公開範囲の機械確認（コミット前に必須・exit 0 必須）
make check-kiro-ide-all      # コミット前・公開前
```

外部フィードに依存する新バージョン検知は手動ターゲットです（CI・`all` には含めません）。

```bash
make check-kiro-ide-freshness
```

> **`check-kiro-ide-quick` は全チェックではありません**（links / structure のみ）。
> 執筆中の素早い確認用です。**コミット前には `check-kiro-ide-all` を実行してください**
> （利用可能なターゲットは `make` で確認できます）。

### 手動検証

1. **出典の確認** — 技術的記述に出典リンクがあるか／リンクが有効か
2. **バージョン番号の確認** — 公式 changelog と一致するか／リリース日が正確か
3. **推測表現の確認** — 「おそらく」「と思われる」等がないか
4. **IDE / CLI の区別** — CLI 版の仕様を IDE の記述として書いていないか

---

## ✅ コミット前の最終確認

- [ ] 全てのチェック項目を確認した
- [ ] **`make check-kiro-ide-all` を実行した（exit 0）** — `quick` では代用できません
- [ ] `make check-kiro-ide-ignore` を実行した（exit 0）
- [ ] 公開範囲の確認を実施した（`git status` ＋ `git check-ignore`）
- [ ] コミットメッセージが明確である

---

## ☁️ クラウドセッション（Kiro Web）で作業する場合

クラウドセッションはリポジトリを clone して動くため、**`.gitignore` 対象のファイルは存在しません**。次の3点が変わります。

### 1. 検証は `make check-kiro-ide-cloud` を使う

```bash
make check-kiro-ide-cloud    # 公開範囲＋全チェック＋一次情報取得＋網羅性＋新版検知＋重要URL
```

**`make check-kiro-ide-all` だけでは網羅性が未検証です。** 一次情報スナップショット（`kiro-ide-docs/06_embedded-docs/`）が clone されないため `check-kiro-ide-coverage` は「スキップして exit 0」になります。**スキップは合格ではありません。**

`check-kiro-ide-cloud` は sitemap から取得対象を導出して一次情報を取り直し、網羅性を実測します。**出力の「一次情報 N / 文書 N」を PR 本文に転記してください**（人が「本当に検証したか」を判断できるようにするため）。

> Kiro Web で使う場合、**Sandbox > Internet Access の allow-list に `.kiro.dev` が必要**です（`Common dependencies` の許可ドメインに kiro.dev は含まれません）。

### 2. `main` へ直接コミットしない

フィーチャーブランチ＋PR で出し、**人のマージを承認行為**とします。

### 3. タグ作成・リリース公開をしない

`.github/release-notes/v<版>.md` を PR に含めるだけにします。マージ後に **`Release kiro-ide-docs` ワークフロー**がタグとリリースを作ります。

- 1行目が H1 でリリースタイトルになります（例: `# v1.0.437 — …`）
- **ファイル名の版と `02_update/01_changelog.md` の最新版が一致していること**（不一致はワークフローが検出して失敗します）

### 4. 触ってはいけないもの

- ローカル管理領域（`kiro-ide-docs/work_plans/`・`kiro-ide-docs/05_meta/`・`kiro-ide-docs/06_embedded-docs/`・`work_records/`）の追加・変更
- 正準値（機能数・ショートカット数・capability 数・コンテキストプロバイダ数）の根拠なき変更 → **変更せず PR 本文に理由を書いて人に委ねる**
- 旧版番号の一括置換（`01_features/10_editor.md`・`01_features/08_mcp.md` の履歴参照は残す）

---

## 📝 コミットメッセージガイドライン

### フォーマット

```
<type>: <subject>

<body>

<footer>
```

### Type

- `docs`: ドキュメント変更
- `chore(scripts)`: 検証スクリプト変更
- `chore(ci)`: CI 設定変更
- `fix`: 誤記・リンク切れ等の修正
- `chore`: その他のツール・設定変更

### 例

```
docs: Kiro IDE 1.0.242対応（changelog・Agent Focus Mode）

- 1.0.242 の Improvements・Fixes を追加
- Code OSS v1.108.2 への移行を記載
- リリース日: 2026-07-28

出典: https://kiro.dev/changelog/ide/1-0-242/
```

---

## 🔗 関連ドキュメント

- [ドキュメント作成ワークフロー](WORKFLOW.md)
- [サイト本体 README](../kiro-ide-docs/README.md)

---

**最終更新**: 2026-08-01
