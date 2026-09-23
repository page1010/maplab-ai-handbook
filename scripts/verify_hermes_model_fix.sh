#!/usr/bin/env bash
# verify_hermes_model_fix.sh — 第二方查核 win-01 hermes 壓縮模型修正
#
# 背景:2026-09-23 P0 工單 win01-hermes-compression-ctx-fix-20260923 的回執由 hermes 自己產出,
# 回執裡自己標了「⚠ 以下 VERIFIED 均未經第二方查核,發布前逐條重驗」。
# 依 CULTURE_DECISION_LOGIC.md 制度 A:別人說修好不算修好,要自己驗一次才能對 Owner 講。
#
# 這支只驗「可以在 Mac 這邊驗的那一半」= 模型事實:
#   1. thinkingmachines/inkling:free 這個 model id 在 OpenRouter 上真的存在嗎?
#   2. 它的 context_length 真的是 1,048,576(或至少 >= 64,000)嗎?
#   3. 它真的是免費的嗎(prompt/completion 定價為 0)?
# 順便對照被換掉的 z-ai/glm-5.2:free 是否真的只有 32,768,確認原始診斷沒冤枉它。
#
# 驗不到的那一半(win-01 的 config.yaml 實際內容、備份檔是否存在、hermes -z 是否真的 rc=0)
# 在 Windows 機上,依 selfops 邊界不碰別人的機器 → 只能靠該機回執,本檔不宣稱驗過。
#
# 安全:/models 是公開端點,不帶任何金鑰。本檔不讀 ~/.maplab/free_compute.env,不印任何憑證。
set -uo pipefail

NEW_ID="thinkingmachines/inkling:free"
OLD_ID="z-ai/glm-5.2:free"
MIN_CTX=64000
TMP="$(mktemp -t or_models.XXXXXX)"
trap 'rm -f "$TMP"' EXIT

echo "=== 1. 抓 OpenRouter 公開模型清單(不帶金鑰) ==="
HTTP="$(curl -s --max-time 30 https://openrouter.ai/api/v1/models -o "$TMP" -w '%{http_code}')"
BYTES="$(wc -c <"$TMP" | tr -d ' ')"
echo "http=$HTTP bytes=$BYTES"
if [ "$HTTP" != "200" ] || [ "$BYTES" -lt 1000 ]; then
  echo "FATAL: 取不到模型清單,無法查核。不要據此對 Owner 宣稱任何結論。"
  exit 1
fi

echo
echo "=== 2. 逐項查核 ==="
python3 - "$TMP" "$NEW_ID" "$OLD_ID" "$MIN_CTX" <<'PY'
import json, sys
path, new_id, old_id, min_ctx = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
data = json.load(open(path))["data"]
idx = {m.get("id"): m for m in data}

def report(mid, label):
    m = idx.get(mid)
    if not m:
        print(f"{label} {mid}: 查無此 model id  <-- 回執這一條不成立")
        return None
    ctx = m.get("context_length")
    pr = m.get("pricing", {}) or {}
    def z(k):
        v = pr.get(k)
        try: return float(v) == 0.0
        except (TypeError, ValueError): return False
    free = z("prompt") and z("completion")
    print(f"{label} {mid}")
    print(f"    context_length = {ctx}")
    print(f"    免費(prompt/completion 定價為 0) = {free}")
    return ctx, free

print("[新模型]")
new = report(new_id, " ->")
print()
print("[被換掉的舊模型,對照組:確認原始診斷沒冤枉它]")
old = report(old_id, " ->")

print()
print("=== 3. 結論(只涵蓋模型事實,不涵蓋 win-01 機上狀態) ===")
if not new:
    print("FAIL: 回執指定的新模型在 OpenRouter 上不存在。工單不算修好,必須退回。")
    sys.exit(2)
ctx, free = new
if ctx is None or ctx < min_ctx:
    print(f"FAIL: 新模型 context_length={ctx},未達 hermes 要求的 {min_ctx}。換了等於沒換。")
    sys.exit(2)
if not free:
    print("WARN: 新模型不是零定價,與「免費鏈」前提不符,要先跟 Owner 確認會不會產生費用。")
    sys.exit(3)
print(f"PASS: 新模型存在、context_length={ctx} >= {min_ctx}、且為零定價。")
if old:
    octx, _ = old
    if octx is not None and octx < min_ctx:
        print(f"PASS: 舊模型 context_length={octx} 確實低於 {min_ctx},原始診斷成立,沒有冤枉它。")
    else:
        print(f"WARN: 舊模型 context_length={octx} 看起來並不低於門檻,原始診斷可能另有原因,要回頭再查。")
print()
print("⚠ 仍未驗(在 Windows 機上,本檔不碰別人的機器):")
print("   config.yaml 是否真的改到、config.yaml.bak-20260923 是否真的存在、hermes -z 是否真的 rc=0。")
print("   這三條目前只有 win-01 自己的回執,對 Owner 講的時候要說清楚是誰驗的。")
PY
rc=$?
echo
echo "exit=$rc"
exit $rc
