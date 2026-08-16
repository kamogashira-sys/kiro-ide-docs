# コンテキストプロバイダ

**チャットで `#` から呼び出せる参照元の一覧です。**

- **一次情報**: [Chat（Context management）](https://kiro.dev/docs/ide/chat/#context-providers)（公式ページ更新日: 2026-06-25）
- **収録件数**: **14種**

> **これは何か**: Kiro はエディタで開いているファイルとその依存関係・構造を自動的に解析しますが、
> **`#` を使って明示的にコンテキストを追加できます**。チャット入力欄で `#` を打つと候補が出ます。

---

## 一覧（14種）

| プロバイダ | 内容 | 使用例 |
|-----------|------|-------|
| **`#codebase`** | プロジェクト全体から関連ファイルを自動的に探させる | `#codebase explain the authentication flow` |
| **`#file`** | コードベースの特定のファイルを参照する | `#auth.ts explain this implementation` |
| `#folder` | 特定のフォルダとその中身を参照する | `#components/ what components do we have?` |
| `#git diff` | 現在の Git の変更を参照する | `#git diff explain what changed in this PR` |
| **`#terminal`** | アクティブなターミナルの最近の出力とコマンド履歴を含める | `#terminal help me fix this build error` |
| `#problems` | 現在のファイルのすべての問題を含める | `#problems help me resolve these issues` |
| `#url` | Web のドキュメントを含める | `#url:https://docs.example.com/api explain this API` |
| `#code` | 特定のコードスニペットをコンテキストに含める | `#code:const sum = (a, b) => a + b; explain this function` |
| `#repository` | リポジトリ構造のマップを含める | `#repository how is this project organized?` |
| `#current` | エディタで現在アクティブなファイルを参照する | `#current explain this component` |
| `#steering` | 特定のステアリングファイルを含める | `#steering:coding-standards.md review my code` |
| `#docs` | ドキュメントファイルとその内容を参照する | `#docs:api-reference.md explain this API endpoint` |
| **`#spec`** | 特定の spec のすべてのファイル（requirements・design・tasks）を参照する | `#spec:user-authentication update the design file to include password reset flow` |
| `#mcp` | 接続済みサーバの MCP ツール・プロンプト・リソーステンプレートにアクセスする | `#mcp:aws-docs how do I configure S3 buckets?` |

---

## 書き方の注意

### 引数の付け方が2通りある

| 形 | 該当するプロバイダ | 例 |
|----|-----------------|-----|
| **`#` の直後に値を書く** | `#file`・`#folder` | `#auth.ts`・`#components/`（`#file:auth.ts` ではありません） |
| **`#名前:値` と書く** | `#url`・`#code`・`#steering`・`#docs`・`#spec`・`#mcp` | `#steering:coding-standards.md` |
| **引数なし** | `#codebase`・`#git diff`・`#terminal`・`#problems`・`#repository`・`#current` | `#terminal` |

公式の例に従うと、**ファイルとフォルダはプロバイダ名を書かずに直接名前を書きます**（`#auth.ts`）。

### 複数を組み合わせられる

```
#codebase #auth.ts explain how authentication works with our database
```

---

## 使い分けの指針

| やりたいこと | 使うもの |
|------------|--------|
| どのファイルを見ればいいか分からない | **`#codebase`**（Kiro が探す） |
| 見せたいファイルが決まっている | **`#file`**（`#auth.ts` のように書く） |
| プロジェクトの全体像を伝えたい | `#repository`（構造のマップ） |
| ビルドやテストのエラーを解決したい | **`#terminal`** |
| 開いているファイルについて聞きたい | `#current` |
| チームの規約に沿わせたい | `#steering` |
| spec の内容を踏まえて作業させたい | **`#spec`** |

### `#terminal` は特に有効

公式が推奨する使い方です。`#terminal` を含めると、Kiro は**最近のコマンド履歴・出力・エラーメッセージ**にアクセスして対処を提示できます。

公式が挙げる場面:

| 場面 | 例 |
|------|-----|
| ビルド失敗 | `#terminal My build is failing, what's the issue?` |
| テストのデバッグ | `#terminal These tests aren't passing, help me understand why` |
| Git の問題 | `#terminal I'm stuck on this merge conflict` |
| 依存関係の問題 | `#terminal npm install is throwing errors` |

---

## 📌 件数について

コンテキストプロバイダ数 **14種**は、公式ページの表の行数と一致します。公式で増減した場合は本ページと [README.md](README.md) を更新します。

---

## 関連ドキュメント

- [01_features/02_chat.md](../01_features/02_chat.md) - チャットの使い方
- [01_features/06_steering.md](../01_features/06_steering.md) - `#steering` で参照するファイル
- [01_features/01_specs.md](../01_features/01_specs.md) - `#spec` で参照する成果物
- [01_features/08_mcp.md](../01_features/08_mcp.md) - `#mcp` で使えるツール
- [01_kiro-directory.md](01_kiro-directory.md) - ステアリングや spec の置き場所
