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

# ── 2026-09-24 追加(Owner msg 6091:「hermes 明明有超長上下文,為什麼你們不斷封印他」)──
# 目的:把「封印」從形容詞變成可引用的行號與數字。全程唯讀,不印金鑰。
CALL_SH="/Users/pagemacmini/agent-bus/hermes_call.sh"

echo
echo "=== 4. 封印在哪幾行(直接引 hermes_call.sh 原始碼) ==="
if [ ! -f "$CALL_SH" ]; then
  echo "查無 $CALL_SH —— 本節不成立,不要據此下結論。"
else
  echo "--- 4a. 人格/職能:寫死的 system prompt ---"
  grep -n 'SYS=' "$CALL_SH" | head -3
  echo
  echo "--- 4b. 輸出長度與思考深度:寫死的上限 ---"
  grep -n 'max_tokens' "$CALL_SH" | head -3
  echo
  echo "--- 4c. 模型清單過濾條件(看有沒有把長上下文模型濾掉) ---"
  grep -n 'not in i' "$CALL_SH" | head -3
  echo
  echo "--- 4d. 這支腳本總共讀了幾個本機檔當 context(0 = 從來沒餵過資料) ---"
  echo -n "讀檔動作(cat/<file/read -r 檔案)出現次數:"
  grep -cE '^[^#]*(cat |< *"?\$\{?[A-Z_]*FILE)' "$CALL_SH"
  echo "(STATE_FILE / USED_FILE 是模型名快取與蓋章檔,不是知識庫)"
fi

echo
echo "=== 5. 被濾掉的長上下文模型 vs 實際在跑的模型,context 差幾倍 ==="
python3 - "$TMP" <<'PY'
import json,sys
data=json.load(open(sys.argv[1]))["data"]
idx={m.get("id"):m for m in data}
def ctx(mid):
    m=idx.get(mid)
    return (m or {}).get("context_length")
ROT=["nvidia/nemotron-3-super-120b-a12b:free","poolside/laguna-s-2.1:free",
     "nvidia/nemotron-3.5-lightning:free","google/gemma-4-31b-it:free"]
BIG=["thinkingmachines/inkling:free","thinkingmachines/inkling-small:free"]
print("[實際在服務的輪替清單]")
served=[]
for m in ROT:
    c=ctx(m); served.append(c or 0)
    print(f"  {m:48s} context={c}")
print("[被第 36 行 'inkling' not in i 濾掉的]")
big=[]
for m in BIG:
    c=ctx(m); big.append(c or 0)
    print(f"  {m:48s} context={c}")
if max(served) and max(big):
    print(f"\n差距:被濾掉的最大 {max(big):,} vs 在跑的最大 {max(served):,} "
          f"= {max(big)/max(served):.1f} 倍")
PY

echo
echo "=== 6. 實跑一次 hermes,原文照貼(不改寫、不潤飾) ==="
ENVF="$HOME/.maplab/free_compute.env"
if [ -f "$ENVF" ]; then
  set -a; . "$ENVF" 2>/dev/null; set +a   # source only — 金鑰絕不 echo
  echo "(key 已載入,未印出)"
else
  echo "查無 $ENVF —— 無金鑰,以下若有輸出就是 fallback 不是 hermes。"
fi
HERMES_Q="${HERMES_Q:-用三句話說明 MAPLAB 這間公司在做什麼,以及對客人最重要的原則是什麼。}"
echo "問題:$HERMES_Q"
echo "--- hermes 回覆原文開始 ---"
HERMES_STATE_FILE=/tmp/.hermes_last_good HERMES_USED_FILE=/tmp/.hermes_last_used \
  bash "$CALL_SH" "$HERMES_Q" 2>/tmp/hermes_call.err
echo "--- hermes 回覆原文結束 ---"
echo "[實際服務的模型]"
cat /tmp/.hermes_last_used 2>/dev/null || echo "(沒有蓋章檔)"
echo "[stderr 最後 8 行]"
tail -8 /tmp/hermes_call.err 2>/dev/null

echo
echo "=== 7. 對照組:同一個問題,唯一差別是把企業文化檔餵進去 ==="
HB="/Users/pagemacmini/maplab-ai-handbook"
CTX_FILE="/tmp/hermes_ctx.txt"
: > "$CTX_FILE"
cat "$HB/AGENT_CORE.md" >> "$CTX_FILE" 2>/dev/null
head -120 "$HB/docs/company-values.md" >> "$CTX_FILE" 2>/dev/null
echo -n "餵進去的位元組數:"; wc -c < "$CTX_FILE" | tr -d ' '
CTX="$(cat "$CTX_FILE")"
echo "--- hermes(有餵資料)回覆原文開始 ---"
HERMES_STATE_FILE=/tmp/.hermes_last_good HERMES_USED_FILE=/tmp/.hermes_last_used2 \
  bash "$CALL_SH" "以下是 MAPLAB 的內部文件。只根據文件內容回答,文件沒寫的一律說「文件未提及」。

$CTX

問題:$HERMES_Q" 2>/tmp/hermes_call2.err
echo "--- hermes(有餵資料)回覆原文結束 ---"
echo "[實際服務的模型]"
cat /tmp/.hermes_last_used2 2>/dev/null || echo "(沒有蓋章檔)"

exit $rc
