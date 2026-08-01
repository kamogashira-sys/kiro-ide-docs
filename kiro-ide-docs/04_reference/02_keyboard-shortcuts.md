# キーボードショートカット

**Kiro IDE のキーボードショートカット一覧です。**

- **一次情報**: [Keyboard Shortcuts](https://kiro.dev/docs/editor/keyboard-shortcuts/)（公式ページ更新日: 2025-11-16）
- **収録件数**: **29件**（General 9・Navigation 11・Editing 6・AI features 3）

> **Kiro IDE は Code OSS のフォーク**のため、ショートカットの多くは VS Code と同じです。
> 下表のうち **AI features** の3件が Kiro 固有の価値になります。
> VS Code から移行する場合は、キーバインドをそのまま持ち込めます（[03_deployment/03_migrating-from-vscode.md](../03_deployment/03_migrating-from-vscode.md)）。

---

## General（9件）

| Mac | Windows / Linux | 内容 |
|-----|----------------|------|
| `Cmd+Shift+P` | `Ctrl+Shift+P` | コマンドパレットを開く |
| `Cmd+K Cmd+S` | `Ctrl+K Ctrl+S` | キーボードショートカットを開く |
| <code>Ctrl+`</code> | <code>Ctrl+`</code> | ターミナルの表示切り替え |
| `Cmd+N` | `Ctrl+N` | 新規ファイル |
| `Cmd+W` | `Ctrl+W` | タブを閉じる |
| `Cmd+S` | `Ctrl+S` | 保存 |
| `Cmd+Shift+S` | `Ctrl+Shift+S` | 名前を付けて保存 |
| `Cmd+Z` | `Ctrl+Z` | 元に戻す |
| `Cmd+Shift+Z` | `Ctrl+Shift+Z` | やり直す |

> **ターミナルの切り替えは Mac でも `Ctrl`** です（`Cmd` ではありません）。

---

## Navigation（11件）

| Mac | Windows / Linux | 内容 |
|-----|----------------|------|
| `Cmd+P` | `Ctrl+P` | ファイルをクイックオープン |
| `Cmd+O` | `Ctrl+O` | ファイルを開く |
| `Cmd+K Cmd+O` | `Ctrl+K Ctrl+O` | フォルダを開く |
| `Cmd+Shift+O` | `Ctrl+Shift+O` | シンボルへ移動 |
| `Ctrl+G` | `Ctrl+G` | 行へ移動 |
| `Cmd+F` | `Ctrl+F` | 検索 |
| `Cmd+Shift+F` | `Ctrl+Shift+F` | ファイル全体を検索 |
| `Cmd+B` | `Ctrl+B` | サイドバーの表示切り替え |
| `Cmd+\` | `Ctrl+\` | エディタを分割 |
| `Cmd+1/2/3` | `Ctrl+1/2/3` | エディタグループにフォーカス |
| `Ctrl+Shift+G` | `Ctrl+Shift+G` | ソース管理を開く |

> **行への移動とソース管理は Mac でも `Ctrl`** です。

---

## Editing（6件）

| Mac | Windows / Linux | 内容 |
|-----|----------------|------|
| `Cmd+X` | `Ctrl+X` | 切り取り |
| `Cmd+C` | `Ctrl+C` | コピー |
| `Cmd+V` | `Ctrl+V` | 貼り付け |
| `Cmd+/` | `Ctrl+/` | コメントの切り替え |
| `Option+Up/Down` | `Alt+Up/Down` | 行を上下に移動 |
| `Cmd+Shift+K` | `Ctrl+Shift+K` | 行を削除 |

---

## AI features（3件）

**Kiro 固有のショートカットです。**

| Mac | Windows / Linux | 内容 |
|-----|----------------|------|
| **`Cmd+L`** | **`Ctrl+L`** | **チャットセッションを開く** |
| **`Cmd+I`** | **`Ctrl+I`** | **インラインチャット** |
| `F5` | `F5` | デバッグを開始 |

> **`Cmd+L` と `Cmd+I` の違い**: `Cmd+L` はチャットパネルでの会話、`Cmd+I` はエディタ内でその場に書くインラインチャットです。
> チャットの使い方は [01_features/02_chat.md](../01_features/02_chat.md) を参照してください。

> **`F5`（デバッグ開始）は AI features に分類されていますが**、Code OSS 由来の標準的なデバッグ機能です。
> 公式ページの分類をそのまま反映しています。

---

## ショートカットをカスタマイズする

| 順 | 操作 |
|----|------|
| 1 | コマンドパレットを開く（`Cmd+Shift+P` / `Ctrl+Shift+P`） |
| 2 | **Keyboard Shortcuts** を検索する |
| 3 | **Preferences: Open Keyboard Shortcuts** を選ぶ |
| 4 | 変更したいコマンドを選ぶ |
| 5 | 鉛筆アイコンを選び、使いたいショートカットを入力する |

他のエディタで慣れた操作に合わせられます。

---

## 📌 件数について

本サイトはショートカット数 **29件**を検証対象の数値として持っています。公式ページで件数が変わった場合は本ページと [README.md](README.md) の両方を更新します。

**内訳**:

| カテゴリ | 件数 |
|---------|-----|
| General | 9 |
| Navigation | 11 |
| Editing | 6 |
| AI features | 3 |
| **合計** | **29** |

「Custom shortcuts」はカスタマイズ手順の説明で、表を持たないため件数に含めません。

---

## 関連ドキュメント

- [01_kiro-directory.md](01_kiro-directory.md) - 設定ファイルの置き場所
- [01_features/02_chat.md](../01_features/02_chat.md) - チャットの使い方
- [01_features/10_editor.md](../01_features/10_editor.md) - エディタ基盤の機能
- [03_deployment/03_migrating-from-vscode.md](../03_deployment/03_migrating-from-vscode.md) - VS Code からキーバインドを持ち込む
