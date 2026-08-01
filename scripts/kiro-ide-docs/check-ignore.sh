#!/usr/bin/env bash
# 公開範囲の機械検証（作業計画書 Phase 1-5 / 4-1 / 5-3）
#
# ローカル管理対象が .gitignore で除外されていること、および
# 公開対象が誤って除外されていないことを機械確認する。
#
# 使い方: make check-kiro-ide-ignore  または  scripts/kiro-ide-docs/check-ignore.sh
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT" || exit 1

fail=0

# ローカル管理対象（GitHub 非公開）: ignore されていなければ NG
LOCAL_ONLY=(
  "kiro-ide-docs/work_plans/x_plan.md"
  "kiro-ide-docs/05_meta/10_version-update-guide.md"
  "kiro-ide-docs/05_meta/templates/worklog.md"
  "kiro-ide-docs/06_embedded-docs/x.md"
  "work_records/20260801/x_worklog.md"
  "x_update_plan.md"
  ".claude/settings.local.json"
)

# 公開対象: ignore されていたら NG
PUBLIC=(
  "README.md"
  "LICENSE"
  "CODE_OF_CONDUCT.md"
  ".github/ISSUE_TEMPLATE/bug_report.yml"
  ".github/WORKFLOW.md"
  ".github/COMMIT_CHECKLIST.md"
  ".github/pull_request_template.md"
  "kiro-ide-docs/README.md"
  "kiro-ide-docs/00_information/README.md"
  "kiro-ide-docs/01_features/README.md"
  "kiro-ide-docs/02_update/README.md"
  "kiro-ide-docs/03_deployment/README.md"
  "kiro-ide-docs/04_reference/README.md"
  "scripts/kiro-ide-docs/check-ignore.sh"
  "Makefile"
)

echo "=== ローカル管理対象が除外されていることを確認 ==="
for p in "${LOCAL_ONLY[@]}"; do
  if git check-ignore -q "$p"; then
    echo "  OK   ignored: $p"
  else
    echo "  FAIL not ignored: $p"
    fail=1
  fi
done

echo "=== 公開対象が除外されていないことを確認 ==="
for p in "${PUBLIC[@]}"; do
  if git check-ignore -q "$p"; then
    echo "  FAIL wrongly ignored: $p"
    fail=1
  else
    echo "  OK   publishable: $p"
  fi
done

echo "=== コミット済みツリーにローカル管理対象が含まれていないことを確認 ==="
tracked=$(git ls-files | grep -E "work_plans/|05_meta/|06_embedded-docs/|work_records/|_plan\.md$" || true)
if [ -n "$tracked" ]; then
  echo "  FAIL 以下がトラックされています:"
  echo "$tracked" | sed 's/^/    /'
  fail=1
else
  echo "  OK   local-only files are not tracked"
fi

if [ "$fail" -eq 0 ]; then
  echo "=== 結果: すべて OK ==="
else
  echo "=== 結果: 失敗あり（公開してはいけない状態） ==="
fi
exit "$fail"
