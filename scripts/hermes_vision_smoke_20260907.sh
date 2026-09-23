#!/bin/bash
# hermes 免費鏈讀圖冒煙測 v3：PARSE_FAIL/空內容視為探路失敗換下一模型；保留原始回應供診斷
# 邊界: 只送成人場景照片; 兒童照片一律走本地模型不外送; 金鑰只 source 不回顯不落地
set -u
ENV_FILE="$HOME/.maplab/free_compute.env"
[ -f "$ENV_FILE" ] || { echo "FATAL: env file missing"; exit 1; }
set -a; source "$ENV_FILE"; set +a
[ -n "${OPENROUTER_API_KEY:-}" ] || { echo "FATAL: OPENROUTER_API_KEY empty"; exit 1; }

OUTDIR="/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/adok-dualcheck/hermes-vision-smoke-20260907"
TMPDIR_S="$OUTDIR/tmp"
mkdir -p "$OUTDIR" "$TMPDIR_S"
RESULTS="$OUTDIR/results.tsv"

echo "== 免費多模態模型即時清單 =="
curl -s --max-time 60 https://openrouter.ai/api/v1/models -o "$TMPDIR_S/models.json"
/usr/bin/python3 - "$TMPDIR_S/models.json" "$TMPDIR_S/vision_free.txt" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
out = []
for m in d.get("data", []):
    mid = m.get("id", "")
    if not mid.endswith(":free"):
        continue
    mods = (m.get("architecture", {}) or {}).get("input_modalities", []) or []
    if "image" in mods:
        out.append(mid)
with open(sys.argv[2], "w") as f:
    f.write("\n".join(out))
print("\n".join(out) if out else "(none)")
PYEOF

BASE="/Users/pagemacmini/Library/CloudStorage/GoogleDrive-pagewu1010@gmail.com/我的雲端硬碟/2026maplab外燴紀錄"
PHOTOS=(
"$BASE/0612大台南會展中心-工研院在宅醫療科技推動計畫跨部會工作小組會議/IMG_20260612_145700.jpg"
"$BASE/0612大台南會展中心-工研院在宅醫療科技推動計畫跨部會工作小組會議/IMG_20260612_145735.jpg"
"$BASE/0612大台南會展中心-工研院在宅醫療科技推動計畫跨部會工作小組會議/IMG_20260612_145909.jpg"
"$BASE/0621說事實木地板開幕/IMG_1400.HEIC"
"$BASE/0621說事實木地板開幕/IMG_1408.HEIC"
"$BASE/0621說事實木地板開幕/IMG_1411.HEIC"
"$BASE/0702中興工程/IMG_1492.HEIC"
"$BASE/0702中興工程/IMG_1495.HEIC"
"$BASE/0702中興工程/IMG_1497.HEIC"
"$BASE/0702中興工程/IMG_1499.HEIC"
)

PROMPT='You are a photo compliance checker for event catering marketing photos. Look at the image and answer ONLY a single-line JSON object with keys: face (one of NONE, ADULT, CHILD - CHILD if ANY person under ~16 is visible), face_prominent (YES if any face is close-up/clearly identifiable, NO if faces are distant/backs/blurred or no faces), logo (YES if any company logo/brand sign readable, NO otherwise), scene_guess (max 4 English words). No markdown, no explanation.'

call_one () {  # $1=model $2=photo $3=tag ; echoes "HTTPcode<TAB>content"
  local MODEL="$1" P="$2" TAG="$3"
  local SMALL="$TMPDIR_S/img_$TAG.jpg"
  sips -s format jpeg -Z 768 "$P" --out "$SMALL" >/dev/null || { echo "SIPS_FAIL	-"; return; }
  local B64; B64=$(base64 -i "$SMALL" | tr -d '\n')
  local REQ="$TMPDIR_S/req_$TAG.json"
  /usr/bin/python3 - "$REQ" "$MODEL" "$PROMPT" "$B64" <<'PYEOF'
import json, sys
req_path, model, prompt, b64 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
payload = {"model": model, "max_tokens": 2000,
  "messages": [{"role": "user", "content": [
    {"type": "text", "text": prompt},
    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
json.dump(payload, open(req_path, "w"))
PYEOF
  local RESP="$TMPDIR_S/resp_${TAG}_$(echo "$MODEL" | tr '/:' '__').json"
  local HTTP
  HTTP=$(curl -sS -o "$RESP" -w "%{http_code}" --max-time 90 \
    -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    -H "Content-Type: application/json" \
    -X POST https://openrouter.ai/api/v1/chat/completions \
    --data-binary @"$REQ")
  local CONTENT
  CONTENT=$(/usr/bin/python3 - "$RESP" <<'PYEOF'
import json, sys
import re
try:
    d = json.load(open(sys.argv[1]))
    if "choices" in d and d["choices"]:
        msg = d["choices"][0].get("message", {}) or {}
        c = (msg.get("content") or "") + " " + (msg.get("reasoning") or "")
        m = re.search(r'\{[^{}]*"face"[^{}]*\}', c)
        if m:
            print("JSON:" + m.group(0).replace("\n", " ").replace("\t", " "))
        else:
            c = c.replace("\n", " ").replace("\t", " ").strip()
            print(("NOJSON:" + c[:250]) if c else "EMPTY_CONTENT")
    else:
        print("ERR:" + str(d.get("error", {}).get("message", ""))[:200])
except Exception:
    try:
        raw = open(sys.argv[1], "rb").read(300).decode("utf-8", "replace")
        print("RAWHEAD:" + raw.replace("\n", " ").replace("\t", " "))
    except Exception:
        print("PARSE_FAIL_NO_FILE")
PYEOF
)
  rm -f "$REQ"
  echo "HTTP${HTTP}	${CONTENT}"
}

probe_ok () {  # $1=probe output line; PASS 需 HTTP200 且內容看得出在回 JSON/關鍵字
  case "$1" in
    HTTP200*face*|HTTP200*FACE*|HTTP200*"{"*) return 0 ;;
    *) return 1 ;;
  esac
}

: > "$RESULTS"
WINNER=""
while IFS= read -r MODEL; do
  [ -z "$MODEL" ] && continue
  echo ""
  echo "== 試模型: ${MODEL} (先打 1 張探路) =="
  PROBE=$(call_one "$MODEL" "${PHOTOS[0]}" "00")
  echo "probe: $PROBE"
  if probe_ok "$PROBE"; then WINNER="$MODEL"; else continue; fi
  echo "== $MODEL 探路通過，跑滿 10 張 =="
  i=0
  for P in "${PHOTOS[@]}"; do
    i=$((i+1)); TAG=$(printf "%02d" "$i")
    [ -f "$P" ] || { printf "%s\t%s\tFILE_MISSING\t-\n" "$TAG" "$(basename "$P")" >> "$RESULTS"; continue; }
    R=$(call_one "$MODEL" "$P" "$TAG")
    printf "%s\t%s\t%s\t%s\n" "$TAG" "$(basename "$P")" "$MODEL" "$R" >> "$RESULTS"
    sleep 2
  done
  break
done < "$TMPDIR_S/vision_free.txt"

echo ""
echo "== results (model=$WINNER) =="
cat "$RESULTS" 2>/dev/null || echo "(no full run — all models failed probe)"
find "$TMPDIR_S" -name "img_*.jpg" -delete
echo "(原始回應保留在 $TMPDIR_S 供診斷)"
