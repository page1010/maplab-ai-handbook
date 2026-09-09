#!/bin/bash
# yt_daily_hermes_meeting.sh v1 — MAP TABLE RADIO 每日晨會（Fable5 主持 × hermes 免費鏈）
# 授權：Owner msg 5048（2026-09-09）「用每天hermes額度至少產出1個可用…每天早上跟hermes開會並執行,全權給你負責」
# 產出：data/music-style-db/daily/brief_YYYYMMDD.md（當日曲目 brief：Suno prompt+標題+含引流心機的描述+封面道具）
# 心機規則：描述前兩行=一句真實派對場景故事+外燴站連結（音樂聽眾裡的辦活動族群→導到 maplabkitchen）
# 安全邊界：金鑰只 source 不回顯；只寫 handbook data/ 目錄；同日重跑冪等（已有 brief 即跳過）
set -u
ENV_FILE="$HOME/.maplab/free_compute.env"
[ -f "$ENV_FILE" ] || { echo "FATAL: env file missing"; exit 1; }
set -a; source "$ENV_FILE"; set +a
[ -n "${OPENROUTER_API_KEY:-}" ] || { echo "FATAL: OPENROUTER_API_KEY empty"; exit 1; }

HB="/Users/pagemacmini/maplab-ai-handbook"
DAILY="$HB/data/music-style-db/daily"
mkdir -p "$DAILY"
TODAY=$(date +%Y%m%d)
BRIEF="$DAILY/brief_$TODAY.md"
if [ -f "$BRIEF" ]; then
  if [ "$(wc -c < "$BRIEF" | tr -d ' ')" -gt 300 ]; then
    echo "[skip] 今日 brief 已存在: $BRIEF"; exit 0
  else
    echo "[warn] 發現半成品 brief，重做"; rm -f "$BRIEF"
  fi
fi

SEEDS="$HB/data/music-style-db/style-seeds-20260909.csv"
RECENT=$(grep -h '"title_zh"' "$DAILY"/brief_*.md 2>/dev/null | tail -14)

REQ="$DAILY/.req.json"
/usr/bin/python3 - "$REQ" "$SEEDS" "$RECENT" <<'PYEOF'
import json, sys
req_path, seeds_path, recent = sys.argv[1], sys.argv[2], sys.argv[3]
seeds = open(seeds_path, encoding="utf-8-sig").read()
prompt = f"""你是台南外燴品牌 maplabkitchen 的 YouTube 音樂頻道「MAP TABLE RADIO」的音樂總監 hermes，正在和頻道負責人 Fable5 開每日晨會。頻道定位：台南外燴品牌的餐桌 BGM 廠牌，全部純音樂（instrumental, no vocals）。

以下是頻道的 20 首風格種子資料庫（CSV）：
{seeds}

最近已排過的曲目標題（避免重複同場景）：
{recent if recent.strip() else "（尚無，今天是第一天）"}

請產出今日一首曲目的完整 brief，只回一個 JSON 物件（無 markdown、無說明文字），鍵如下：
- base_style_id: 從種子庫挑一個最適合今天的 style_id 當基底
- suno_prompt: 英文 Suno 生成 prompt，基於基底但做一個新變化，必含 instrumental 與 no vocals
- bpm: 數字
- title_zh: 繁體中文曲名，用台南真實派對場景命名（例：開幕茶會的第一杯香檳），不用引號
- scene_story: 一句繁體中文場景故事（30字內，像真的發生在某場台南派對）
- yt_description: YouTube 描述全文繁體中文。第一行=scene_story，第二行=「這樣的派對真實存在——台南外燴 maplabkitchen：https://sites.google.com/view/maplabkitchen」，之後兩三行寫曲風/BPM/適合情境，最後一行 hashtags（#台南 #外燴 #BGM 加曲風標籤）
- cover_prop: 封面微動畫這次要換上的一樣桌上道具（繁中）
- next_variation_note: 給明天晨會的一句備忘（哪個方向還沒排過）"""
payload = {"model": "MODEL_PLACEHOLDER", "max_tokens": 3000,
  "messages": [{"role": "user", "content": prompt}]}
json.dump(payload, open(req_path, "w"), ensure_ascii=False)
PYEOF

MODELS="nvidia/nemotron-3-super-120b-a12b:free
google/gemma-4-31b-it:free
minimax/minimax-m3:free
dots-studio/dots-3-note-preview:free"

OUT=""
USED=""
while IFS= read -r MODEL; do
  [ -z "$MODEL" ] && continue
  R2="$DAILY/.req_m.json"
  /usr/bin/python3 -c "import json,sys; d=json.load(open(sys.argv[1])); d['model']=sys.argv[2]; json.dump(d,open(sys.argv[3],'w'),ensure_ascii=False)" "$REQ" "$MODEL" "$R2"
  RESP="$DAILY/.resp.json"
  HTTP=$(curl -sS -o "$RESP" -w "%{http_code}" --max-time 120 \
    -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
    -X POST https://openrouter.ai/api/v1/chat/completions --data-binary @"$R2")
  echo "[try] $MODEL http=$HTTP"
  if [ "$HTTP" = "200" ]; then
    OUT=$(/usr/bin/python3 - "$RESP" <<'PYEOF'
import json, sys, re
try:
    d = json.load(open(sys.argv[1]))
    c = (d.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    m = re.search(r'\{.*\}', c, re.S)
    print(m.group(0) if m else "")
except Exception:
    print("")
PYEOF
)
    if [ -n "$OUT" ] && echo "$OUT" | /usr/bin/python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('suno_prompt') and d.get('title_zh')" 2>/dev/null; then
      USED="$MODEL"; break
    fi
    OUT=""
  fi
done <<< "$MODELS"

rm -f "$DAILY"/.req.json "$DAILY"/.req_m.json "$DAILY"/.resp.json
[ -z "$OUT" ] && { echo "FATAL: 四模型皆失敗，今日晨會未產出（明日重試或人工補）"; exit 1; }

{
  echo "# MAP TABLE RADIO 每日晨會 brief — $TODAY"
  echo "會議：Fable5 × hermes（${USED}）｜狀態：待 A8 燒 Suno"
  echo ""
  echo '```json'
  echo "$OUT" | /usr/bin/python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=1))"
  echo '```'
} > "$BRIEF"
echo "$(date +%F) model=$USED brief=brief_$TODAY.md $(echo "$OUT" | /usr/bin/python3 -c "import json,sys; d=json.load(sys.stdin); print('\"title_zh\": '+d.get('title_zh',''))")" >> "$DAILY/meeting_log.md"

# 進度板自動記錄（Owner 5077 要求）：失敗只警告不擋晨會
BOARD_TMP="$DAILY/.board_row.json"
printf '%s' "$OUT" > "$BOARD_TMP"
/usr/bin/python3 - "$BOARD_TMP" "$TODAY" "$USED" <<'PYEOF' || echo "[warn] 進度板寫入失敗(不影響晨會產出,下輪補)"
import json, sys, urllib.request, urllib.parse
brief = json.load(open(sys.argv[1]))
today, used = sys.argv[2], sys.argv[3]
tok = json.load(open("/Users/pagemacmini/.claude/mcp-keys/google-token.json"))
data = urllib.parse.urlencode({
    "client_id": tok["client_id"], "client_secret": tok["client_secret"],
    "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}).encode()
r = urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data), timeout=60)
access = json.load(r)["access_token"]
sid = "1EUnKAB5ptjIpYnEewld8erfbWWrAbfX9o85toHJhmZw"
row = [[today[4:6] + "/" + today[6:8], "晨會產出：" + brief.get("title_zh", "?"),
        "brief 完成,待燒 Suno", "",
        "基底 " + str(brief.get("base_style_id", "?")) + " " + str(brief.get("bpm", "?"))
        + "BPM｜道具:" + str(brief.get("cover_prop", "?")) + "｜model=" + used]]
vb = json.dumps({"values": row}).encode()
rng = urllib.parse.quote("board!A1")
req = urllib.request.Request(
    "https://sheets.googleapis.com/v4/spreadsheets/" + sid + "/values/" + rng
    + ":append?valueInputOption=RAW&insertDataOption=INSERT_ROWS",
    data=vb, headers={"Authorization": "Bearer " + access, "Content-Type": "application/json"},
    method="POST")
d = json.load(urllib.request.urlopen(req, timeout=60))
print("[board] 進度板已記一列")
PYEOF
rm -f "$BOARD_TMP"

cd "$HB" && git pull --rebase --autostash >/dev/null 2>&1
git -C "$HB" add data/music-style-db/daily/ && git -C "$HB" commit -m "晨會brief $TODAY (MAP TABLE RADIO)" >/dev/null 2>&1 && git -C "$HB" push origin chore/agent-login-governance-20260816 >/dev/null 2>&1 && echo "[git] pushed" || echo "[git] 未推送(留本地,下輪補)"

echo ""
echo "== 今日 brief =="
cat "$BRIEF"
