---
name: site-update
description: このリポジトリ（猫でもわかる系の非公式解説サイト）の更新要否を確かめ、必要なら手順書に従って更新し PR を作る。site-update ラベルの Issue、「サイトを更新」「版更新」「freshness」の依頼で使う。
---

# site-update

<!-- site-update:common:begin -->
## 手順（全リポ共通）

リポ固有の値（ターゲット名・手順書のパス・変えてよい値）は、下の「リポ固有の値」を使う。

⓪ **道具の確認**: `python3 --version`・`make --version`・`curl --version`・`git --version` の出力で判定する（`command -v` は見つからなくても exit 0 を返すことがあるため使わない）。あわせて `curl -sS -o /dev/null -w '%{http_code}\n' -A "Mozilla/5.0" https://kiro.dev/` が 200 であることを確かめる。足りなければ⑥の方法で報告して終了する。

① **更新要否**: 3値の freshness ターゲットを実行し、出力の `freshness-result: rc=` 行で判定する（make の終了コードでは判定しない）。
- rc=0: 「更新不要」と⑥の方法で報告して終了する
- rc=3: 「未検証」（取得失敗・構造変化の疑い・文書ファイルが無い）と⑥の方法で報告して終了する。直そうとしない
- rc=1: `freshness-missing:` 行の版（またはスラッグ）を控えて②へ進む

② **更新**: リポの手順書に従う。手順書が定める人のゲート（承認待ちの工程）は、手順書の定めどおりに扱う。公式に確認できないことは書かず「未確認」とする。

③ **検証**: クラウド用の一括検証ターゲットが exit 0 になるまで直す。ただし一括検証の中の `freshness-result: rc=3` は直さず、⑥の方法で「未検証」と報告して終了する。

④ **PR**: feature branch から PR を作る。本文は手順書が定める節（見出しの名前をそのまま使う）と、起動した Issue を閉じる `Closes #<Issue 番号>` を含める。

⑤ **禁止**:
- main への push、タグの作成、Release の公開
- `.gitignore`・ローカル管理領域・`.github/workflows/`・`.kiro/skills/`・`AGENTS.md`・`Makefile` の変更
- 検査スクリプトの**判定ロジック**の変更。`scripts/` 配下で変えてよいのは、手順書が版更新で変えると定め、下の「リポ固有の値」に列挙した定数・台帳・TSV と、それらの値を記したコメント・docstring の行（値・出典・取得時点・値の数え方の注記に限る。判定の方法（正規表現・条件・処理の流れ）を説明する記述は含まない）だけとする
- 正準値の根拠のない変更
- 判定ロジックの修正や正準値の変更が必要だと判断したら、変更せずに PR 本文の「未確認・据え置き」に理由を書く

⑥ **終了報告**: PR を作らずに終わるときは、理由を起動した Issue にコメントする。Issue にコメントできない場合は、セッションの最終応答に理由を書く。
<!-- site-update:common:end -->

<!-- site-update:repo:begin -->
## リポ固有の値（kiro-ide-docs）

| 項目 | 値 |
|---|---|
| 手順書 | `.github/UPDATE_GUIDE.md` |
| 3値の freshness | `make check-kiro-ide-cloud-freshness` |
| クラウド用の一括検証 | `make check-kiro-ide-cloud`（手順書 §14） |
| changelog 以外のページへの反映 | 手順書 §6.6（対応表を PR 本文の「更新計画」に書く）と §6.4 の同期 |
| PR 本文の節 | 手順書 §15.1 の4節（更新計画・実施内容・検証結果・未確認・据え置き） |
| リリースノート | `.github/release-notes/v<版>.md`（手順書 §15.2） |

版更新で変えてよい `scripts/` の値（手順書 §16）:

| ファイル | 定数 |
|---|---|
| `scripts/kiro-ide-docs/check-freshness.py` | `SERIES_WITHOUT_INDEX` |
| `scripts/kiro-ide-docs/check-freshness.py` | `SERIES_RELEASE_LABEL` |
| `scripts/kiro-ide-docs/check-freshness.py` | `KNOWN_SLUG_EXCEPTIONS` |
<!-- site-update:repo:end -->
