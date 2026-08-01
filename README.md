# 猫でもわかるKiro IDE アップデート情報

**[Kiro IDE](https://kiro.dev/) のアップデート情報を、初心者にも分かりやすく解説するプロジェクトです。** より正確な情報発信を心がけて更新していきます。

> **姉妹サイト**: Kiro CLI 版は **[猫でもわかるkiro-cli アップデート情報（q-cli-docs）](https://github.com/kamogashira-sys/q-cli-docs)** をご覧ください。Kiro IDE と Kiro CLI の比較は CLI 版サイトの [Kiro IDE 版との比較](https://github.com/kamogashira-sys/q-cli-docs/blob/main/kiro-docs/09_v3/02_kiro-ide-vs-cli.md) にまとめています。

## 🚧 サイト構築中

本サイトは現在、初期構築中です（2026-08-01 着手）。公開時には以下のコンテンツを提供予定です:

1. **📖 アップデート情報** - Kiro IDE 全バージョン（0.1〜1.0.242）の変更内容を分かりやすく解説
2. **💻 インストール・環境構築** - OS 別インストール手順・認証・VS Code からの移行・エンタープライズ配布・セキュリティ
3. **📚 機能詳細ガイド** - Specs / Chat / Permissions / Autopilot / Hooks / Steering / Custom Agents / MCP / Agent Focus Mode / エディタ基盤の10機能
4. **🔍 リファレンス** - `.kiro/` ファイル仕様・キーボードショートカット・権限・コンテキストプロバイダ・モデル

> 構成は公式ドキュメントの調査結果に基づき 2026-08-01 に確定しました。

## 📢 Kiro IDE とは

**Kiro IDE** は、仕様駆動開発（Spec-driven development）を中核とする AI エージェント搭載の統合開発環境です。

- **公式サイト**: <https://kiro.dev/>
- **公式ドキュメント**: <https://kiro.dev/docs/>
- **公式 Changelog（IDE）**: <https://kiro.dev/changelog/ide/>
- **ダウンロード**: <https://kiro.dev/downloads>
- **Issue 管理**: [GitHub - kirodotdev/Kiro](https://github.com/kirodotdev/Kiro)

Kiro IDE・Kiro CLI・Kiro Web は**統一エンジン（single engine for all Kiro surfaces）**の上に構築されており、設定ディレクトリ `~/.kiro/`（Specs / Hooks / Steering / MCP 等）を共有します。CLI 側の情報は[姉妹サイト](https://github.com/kamogashira-sys/q-cli-docs)をご覧ください。

## 📂 ディレクトリ構成

```
kiro-ide-docs/
├── 00_information/   # 基本情報・公式サイト構造・情報源一覧
├── 01_features/      # 機能詳細ガイド（10機能）
├── 02_update/        # アップデート情報（changelog）・1.0 移行ガイド
├── 03_deployment/    # インストール・認証・VS Code 移行・エンタープライズ・セキュリティ
└── 04_reference/     # リファレンス（.kiro/ ファイル仕様・ショートカット・権限・コンテキスト・モデル）
```

## 🧭 編集方針

Kiro CLI 版サイトで実績のある方針を継承します:

1. **品質最優先**: 時間より正確性を優先する
2. **推測禁止・検証徹底**: 一次情報（公式 changelog・公式ドキュメント・Atom フィード）のみを使用し、各記述に根拠を持つ。公式に確認できない事項は「未確認」と明示し、断定して掲載しない
3. **完全性の追求**: 漏れのない網羅的な更新
4. **自動検証**: リンク・数値整合・changelog 構造などを検証スクリプト＋ CI で機械チェック

## 🗂️ 作業記録の運用ルール（メンテナー向け・ローカル管理）

作業の経緯・調査結果・レビュー報告書は `work_records/` に保存し、セッションをまたいだ作業再開を可能にします。

- **保存場所**: `work_records/YYYYMMDD/`（作業日ごとのフォルダ）
- **ファイル名**: `YYYYMMDDHHMM_<内容を表すスラッグ>.md`（例: `202608010948_worklog.md`、`202608010930_..._review_report.md`）
- **必須記録（セッション終了時）**: 作業記録（worklog）に①今回やったこと ②成果物一覧 ③次のアクション ④再開時の注意事項 ⑤ディレクトリ現況 を記載する
- **作業再開時**: まず最新日付フォルダの worklog を読み、そこから計画書（`kiro-ide-docs/work_plans/` 配下のマスタープラン）へ辿る
- **公開範囲**: `work_records/` はローカル管理（`.gitignore` 対象）とし、GitHub には公開しない。作業計画書（`kiro-ide-docs/work_plans/`）・保守手順書（`kiro-ide-docs/05_meta/`）も同様
- **日付規約**: 記録内の日付は ISO 形式（YYYY-MM-DD）。相対表現（「今日」「先週」）は使わない

## 🤝 コントリビューション

誤りの指摘・改善提案は [Issues](../../issues) までお寄せください。

## 📄 ライセンス

[MIT License](LICENSE)
