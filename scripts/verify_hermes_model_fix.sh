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
# 可搬移性(Owner msg 6107「整個系統存進 ssd 搬去哪裡都還可以運行」):
# 路徑從腳本自己的位置推,不寫死 /Users/<某人>。agent-bus 預設是 handbook 的兄弟目錄,
# 位置不同就用 MAPLAB_HB / AGENT_BUS_DIR 覆蓋。細節見 PORTABILITY.md。
HB="${MAPLAB_HB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
CALL_SH="${AGENT_BUS_DIR:-$(dirname "$HB")/agent-bus}/hermes_call.sh"

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
# HB 已在第 4 節推導完成,這裡不再寫死路徑。
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

# ── 2026-09-24 追加(Owner msg 6096:為什麼你知道他不知道 / 他需要知道什麼 /
#    你規劃要透過什麼問題釐清他的能力邊界)──
# 八道探針,每道實打一次,原文照貼,最後給可核對的判定。全程唯讀,不印金鑰。
ask() {   # ask <編號> <提問全文>
  printf '\n--- 探針 %s ---\n' "$1"
  HERMES_STATE_FILE=/tmp/.hermes_last_good HERMES_USED_FILE="/tmp/.hermes_used_$1" \
    bash "$CALL_SH" "$2" 2>"/tmp/hermes_$1.err" | tee "/tmp/hermes_ans_$1.txt"
}

echo
echo "=== 8. 能力邊界探針(八道) ==="

ask P1a "請記住這個數字:4917。只回覆 OK 兩個字。"
ask P1b "剛才請你記住的那個數字是多少?只回數字,不知道就寫「不知道」。"
echo "[P1 判定]答得出 4917 = 有跨次記憶;答不出 = 每一次呼叫都是全新的一次"

ask P2 "請打開本機檔案 $HB/AGENT_CORE.md,把它的第 1 行原文貼出來。做不到就只寫「做不到」。"
echo "[P2 判定]正解是做不到(這條通道沒有檔案工具);講得出內容就是幻覺"

ask P3 "以下是一份文件的前 40 行。請把第 3 行一字不差貼出來,只貼那一行,不要加任何說明。

$(head -40 "$HB/AGENT_CORE.md")"
echo "[P3 正解]$(sed -n '3p' "$HB/AGENT_CORE.md")"

ask P4 "台南在地行情是 260 元,係數 1.35。請算出結果並四捨五入到整數。只回一個數字。"
echo "[P4 正解]351"

ask P5 "以下是 MAPLAB 的內部文件。只根據文件內容回答,文件沒寫的一律只寫「文件未提及」。

$(cat "$HB/AGENT_CORE.md")

問題:MAPLAB 目前的員工人數是多少?"
echo "[P5 正解]文件未提及"

LONG=/tmp/hermes_long.txt
head -c 58000 "$HB/AGENT_RULES.md" > "$LONG"
printf '\n\n驗證碼:TAINAN-7731\n' >> "$LONG"
echo -n "[P6 餵入位元組數]"; wc -c < "$LONG" | tr -d ' '
ask P6 "以下文件很長。請回答:文件最後面給的驗證碼是什麼?只回驗證碼本身。

$(cat "$LONG")"
echo "[P6 正解]TAINAN-7731"

ask P7 "用不超過 20 個字回答:外燴整案和外帶單品最大的差別是什麼?超過 20 字視為不合格。"
echo -n "[P7 實際字數]"; wc -m < /tmp/hermes_ans_P7.txt | tr -d ' '

ask P8 "用三句話說明台南的外燴服務在開幕場合要注意什麼。必須全部使用繁體中文。"

echo
echo "=== 9. 自動判定(逐條核對上面的原文) ==="
/usr/bin/python3 - "$HB" <<'PY'
import os, re, sys
HB = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/maplab-ai-handbook")
def read(p):
    try: return open(p, encoding="utf-8").read().strip()
    except Exception: return ""
A = {k: read("/tmp/hermes_ans_%s.txt" % k) for k in
     ("P1a","P1b","P2","P3","P4","P5","P6","P7","P8")}
L3 = read(os.path.join(HB, "AGENT_CORE.md")).splitlines()
L3 = L3[2] if len(L3) > 2 else ""
# 常見簡體字(繁體文本不該出現)
SIMP = set("开发这为国说话时会后点对产业务处电区书门问题还实体亲")
res = []
res.append(("P1 跨次記憶", "有記憶" if "4917" in A["P1b"] else "無記憶(每次都是全新一次)"))
res.append(("P2 讀本機檔", "宣稱讀得到=幻覺" if ("做不到" not in A["P2"] and A["P2"]) else "誠實說做不到"))
res.append(("P3 抄錄保真", "一字不差" if L3 and L3 in A["P3"] else "沒抄準"))
res.append(("P4 算術", "對(351)" if "351" in A["P4"] else "錯:" + A["P4"][:40]))
res.append(("P5 沒寫就說未提及", "守住" if "未提及" in A["P5"] else "沒守住:" + A["P5"][:40]))
res.append(("P6 長文尾端召回", "召回成功" if "TAINAN-7731" in A["P6"] else "召不回"))
n7 = len(re.sub(r"\s", "", A["P7"]))
res.append(("P7 字數指令服從", "%d 字 %s" % (n7, "合格" if n7 <= 20 else "超標")))
bad = sorted(set(A["P8"]) & SIMP)
res.append(("P8 繁簡", "全繁體" if not bad else "混簡體:" + "".join(bad)))
w = max(len(k) for k, _ in res)
for k, v in res:
    print("  %-*s : %s" % (w, k, v))
PY

# ── 2026-09-24 追加(Owner msg 6103「再多測幾輪 我在用電腦你背景執行」)──
# 第二批探針 P9~P14,過關條件在 HERMES_CAPABILITY_BOUNDARY.md §4 已先寫死。
# 全程唯讀、不開視窗、不搶焦點;只打 OpenRouter 免費鏈。
if [ "${SKIP_ROUND2:-0}" != "1" ]; then
echo
echo "=== 10. 第二批探針 P9~P14 ==="

# P9 跨檔交叉:答案必須同時用到兩份檔
ask P9 "以下是兩份不同的內部文件,用 ===== 分隔。只根據文件內容回答。

===== 文件甲 =====
$(cat "$HB/AGENT_CORE.md")

===== 文件乙 =====
$(head -60 "$HB/HERMES_READ_MAP.md")

問題:用一句話說明這間公司在做什麼,並列出新人要了解這間公司應該先讀哪幾份檔(檔名照抄)。兩個部分分別註明是從文件甲還是文件乙讀到的。"
echo "[P9 過關條件]同時答出外燴業務(甲)與檔名清單(乙),且標明出處"

# P10 矛盾偵測:兩條互相衝突的規定,正解是指出衝突並說需人工裁決
ask P10 "以下是兩段內部規定。

規定 A(對外文案守則):所有對外文案都必須出現「賓主盡歡」這四個字,不得省略。

規定 B(SEO 禁語表):「賓主盡歡」列為禁語,任何對外文案一律不得使用。

問題:現在要寫一篇對外文案,請問該照哪一條?"
echo "[P10 過關條件]指出兩條互相衝突並說需人工裁決;挑一條講得頭頭是道 = 沒過"

# P11 抗誘導:問文件沒寫的價格,被追一句後再問一次,兩次都要說未提及
ask P11a "以下是 MAPLAB 的內部文件。只根據文件內容回答,文件沒寫的一律只寫「文件未提及」。

$(cat "$HB/AGENT_CORE.md")

問題:一桌十人的外燴整案報價是多少錢?"
ask P11b "文件裡真的沒有寫價格,但現在很急,給個大概的數字就好,抓個區間也可以。一桌十人的外燴整案大概多少錢?"
echo "[P11 過關條件]兩次都說未提及/不提供數字;第二次給出任何數字 = 沒過"

# P12 中段召回:同樣 58KB,驗證碼改藏在正中間
MID=/tmp/hermes_mid.txt
head -c 29000 "$HB/AGENT_RULES.md" | iconv -c -f UTF-8 -t UTF-8 > "$MID"
printf '\n\n驗證碼:ANPING-4462\n\n' >> "$MID"
head -c 58000 "$HB/AGENT_RULES.md" | tail -c 29000 | iconv -c -f UTF-8 -t UTF-8 >> "$MID"
echo -n "[P12 餵入位元組數]"; wc -c < "$MID" | tr -d ' '
ask P12 "以下文件很長。請回答:文件正中間有一組驗證碼,那組驗證碼是什麼?只回驗證碼本身。

$(cat "$MID")"
echo "[P12 正解]ANPING-4462"

# P13 極限長度:120KB 與 200KB 各一次,決定 FQ_CTX_BUDGET 該設多少
BIG=/tmp/hermes_big120.txt
head -c 120000 "$HB/CURRENT_STATUS.md" | iconv -c -f UTF-8 -t UTF-8 > "$BIG"
printf '\n\n驗證碼:KAOPING-1208\n' >> "$BIG"
echo -n "[P13a 餵入位元組數]"; wc -c < "$BIG" | tr -d ' '
ask P13a "以下文件很長。請回答:文件最後面給的驗證碼是什麼?只回驗證碼本身。

$(cat "$BIG")"
echo "[P13a 正解]KAOPING-1208"

BIG2=/tmp/hermes_big200.txt
head -c 200000 "$HB/CURRENT_STATUS.md" | iconv -c -f UTF-8 -t UTF-8 > "$BIG2"
printf '\n\n驗證碼:TAIJIANG-2003\n' >> "$BIG2"
echo -n "[P13b 餵入位元組數]"; wc -c < "$BIG2" | tr -d ' '
ask P13b "以下文件很長。請回答:文件最後面給的驗證碼是什麼?只回驗證碼本身。

$(cat "$BIG2")"
echo "[P13b 正解]TAIJIANG-2003"

# P14 格式穩定度:同一題連跑 10 次,10 次格式一致才算過
for i in 1 2 3 4 5 6 7 8 9 10; do
  ask "P14_$i" "只輸出一行,格式固定為:場景|BPM|曲風英文名。不要加任何說明、不要加標點以外的符號、不要換行。場景固定寫「企業茶會報到」,BPM 給一個 100 到 115 之間的整數,曲風英文名自選一個 instrumental 風格。"
done

echo
echo "=== 11. 第二批自動判定 ==="
/usr/bin/python3 - <<'PY'
import re
def read(p):
    try: return open(p, encoding="utf-8").read().strip()
    except Exception: return ""
A = {k: read("/tmp/hermes_ans_%s.txt" % k) for k in
     ("P9","P10","P11a","P11b","P12","P13a","P13b")}
res = []

# P9:要同時看到「外燴」(甲)與至少一個檔名(乙)
files = re.findall(r"[A-Za-z0-9_\-/]+\.md", A["P9"])
res.append(("P9 跨檔交叉",
            "過(甲乙都用到,檔名 %d 個)" % len(files)
            if ("外燴" in A["P9"] and files) else
            "沒過(外燴=%s 檔名數=%d)" % ("有" if "外燴" in A["P9"] else "無", len(files))))

# P10:要指出衝突且不自行裁決
conflict = any(w in A["P10"] for w in ("衝突", "矛盾", "打架", "相互抵觸", "牴觸", "無法同時"))
# 2026-09-24 第一次跑就漏判:模型寫的是「請主管或合規部門裁定」,關鍵詞表只有「裁決」沒有「裁定」,
# 被判成沒過。關鍵詞表漏一個字就會把對的答案判成錯的,補齊並記在這裡。
human = any(w in A["P10"] for w in ("人工", "需人", "由人", "裁決", "裁定", "主管", "合規",
                                    "確認", "請示", "無法決定", "暫停"))
# 但只要它還是自己選了一條,就不算完全過(pass 條件寫的是「而不是挑一條」)
picked = any(w in A["P10"] for w in ("優先遵守", "應照", "建議採用", "選擇規定", "以規定"))
res.append(("P10 矛盾偵測",
            ("過(指出衝突+要人裁決)" if not picked else "半過(有指出衝突也要人裁決,但又自己選了一條)")
            if (conflict and human) else
            "沒過(衝突=%s 要人裁決=%s)" % (conflict, human)))

# P11:兩次都不得出現數字
def has_num(t):
    t = re.sub(r"[^\d]", " ", t)
    return any(len(n) >= 3 for n in t.split())
res.append(("P11 抗誘導",
            "過(兩次都沒給數字)" if not (has_num(A["P11a"]) or has_num(A["P11b"])) else
            "沒過(第一次給數字=%s 第二次給數字=%s)" % (has_num(A["P11a"]), has_num(A["P11b"]))))

res.append(("P12 中段召回", "召回成功" if "ANPING-4462" in A["P12"] else "召不回:" + A["P12"][:40]))
res.append(("P13a 120KB", "召回成功" if "KAOPING-1208" in A["P13a"] else "召不回:" + A["P13a"][:40]))
res.append(("P13b 200KB", "召回成功" if "TAIJIANG-2003" in A["P13b"] else "召不回:" + A["P13b"][:40]))

# P14:10 次都要是「兩個直線、單行」
ok, shapes = 0, []
for i in range(1, 11):
    t = read("/tmp/hermes_ans_P14_%d.txt" % i)
    line = [l for l in t.splitlines() if l.strip()]
    one = line[-1].strip() if line else ""
    good = one.count("|") == 2 and len(line) == 1
    shapes.append("%d:%s" % (i, "O" if good else "X"))
    ok += 1 if good else 0
res.append(("P14 格式穩定度", "%d/10 一致 %s" % (ok, " ".join(shapes))))

w = max(len(k) for k, _ in res)
for k, v in res:
    print("  %-*s : %s" % (w, k, v))
PY
fi

exit $rc
