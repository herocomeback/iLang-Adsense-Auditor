#!/usr/bin/env bash
# 打包 skill 发行包。产物落在 dist/(不入库),内容与仓库当前源文件严格一致。
#
# 用法:
#   bash scripts/build.sh
#
# 产物:dist/ilang-adsense-auditor-skill-<日期>.zip
set -euo pipefail

cd "$(dirname "$0")/.."

# 打包前先验证:校验器自检必须通过,样例报告必须过闸门
python3 validator/audit_validator.py --selftest >/dev/null
python3 validator/audit_validator.py --check examples/sample-audit.json >/dev/null

mkdir -p dist
out="dist/ilang-adsense-auditor-skill-$(date +%F).zip"
rm -f "$out"

zip -r "$out" \
  skill \
  validator/audit_validator.py \
  examples/sample-audit.json \
  -x '*/.DS_Store' >/dev/null

echo "已打包:$out"
unzip -l "$out"
