#!/bin/bash
# task_gate.sh — 任務需求閘(Owner 5144:自己問+防作弊,不靠 Owner 抽查)
# check  <task_dir>            動工前跑:讀 TASK_BRIEF、列需求條目、落已讀收據(綁版本 hash)
# verify <task_dir> [coverage] 交付前跑:驗收據+逐條對照表,任一缺=FAIL 不得交付
# 防作弊設計:
#   1) 收據綁 TASK_BRIEF 當前 sha256——brief 改版舊收據即失效,讀舊版無效。
#   2) 交付必附 COVERAGE.md:含全 hash(只有跑過 check 才拿得到)+每條 R# 逐條寫怎麼滿足,
#      空跑 check 產不出對照;對照與成品入 git,事後可稽核對不上=造假留痕。
#   3) 決定論腳本判 PASS/FAIL,不靠模型自律、不靠 Owner 開口問。
set -euo pipefail

MODE="${1:-}"; DIR="${2:-}"
usage(){ echo "usage: task_gate.sh check|verify <task_dir> [coverage_file]"; exit 2; }
[ -n "${MODE}" ] || usage
[ -n "${DIR}" ] && [ -d "${DIR}" ] || usage
BRIEF="${DIR}/TASK_BRIEF.md"
GATE="${DIR}/.gate"
RECEIPT="${GATE}/read_receipt.txt"

[ -f "${BRIEF}" ] || { echo "GATE FAIL: ${BRIEF} 不存在——先從原話建需求檔再動工"; exit 1; }
HASH=$(shasum -a 256 "${BRIEF}" | awk '{print $1}')
REQS=$(grep -o '^R[0-9]*\.' "${BRIEF}" | tr -d '.' | sort -u)
[ -n "${REQS}" ] || { echo "GATE FAIL: TASK_BRIEF 無 R# 需求條目(需 R1. R2. ... 格式)"; exit 1; }

case "${MODE}" in
  check)
    mkdir -p "${GATE}"
    printf 'BRIEF_SHA256: %s\nCHECKED_AT: %s\n' "${HASH}" "$(date '+%Y-%m-%dT%H:%M:%S')" > "${RECEIPT}"
    echo "=== 需求條目(逐條讀,交付 COVERAGE.md 每條都要寫怎麼滿足)==="
    grep '^R[0-9]*\.' "${BRIEF}"
    echo ""
    echo "GATE CHECK OK  已讀收據落檔:${RECEIPT}"
    echo "BRIEF_SHA256: ${HASH}"
    echo "(COVERAGE.md 第一行必須原樣含上行全碼)"
    ;;
  verify)
    COV="${3:-${DIR}/COVERAGE.md}"
    fail(){ echo "GATE FAIL: $1"; exit 1; }
    [ -f "${RECEIPT}" ] || fail "無已讀收據——動工前沒跑 check"
    grep -q "BRIEF_SHA256: ${HASH}" "${RECEIPT}" || fail "收據綁的是舊版 TASK_BRIEF——需求已改,重跑 check 重讀"
    [ -f "${COV}" ] || fail "缺逐條對照表 ${COV}"
    grep -q "BRIEF_SHA256: ${HASH}" "${COV}" || fail "COVERAGE.md 未含當前版本全碼——對照表不是照這版需求寫的"
    MISS=""
    for r in ${REQS}; do
      line=$(grep "^${r}:" "${COV}" || true)
      body=$(echo "${line}" | sed "s/^${r}://" | tr -d '[:space:]')
      [ -n "${body}" ] || MISS="${MISS} ${r}"
    done
    [ -z "${MISS}" ] || fail "對照表缺條目或空白:${MISS}"
    echo "GATE PASS  ${DIR} 需求 $(echo "${REQS}" | wc -w | tr -d ' ') 條全對照,收據綁當前版本"
    ;;
  *) usage ;;
esac
