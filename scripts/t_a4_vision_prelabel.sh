#!/bin/bash
# t_a4_vision_prelabel.sh — T-A4 器皿辨識 OpenRouter 免費視覺預標註(Owner 5381 核可)
# 邊界:僅送「已目視確認無人像」的縮圖;key 不印出;計入 free-quota usage_log(每日 120 同帳)。
# 用法:編輯 IMAGES 清單後執行;來源=私有庫 training-外燴照片擺設/review-smoke/(1200px jpeg)。
set -u
ENV_FILE="$HOME/.maplab/free_compute.env"
set -a; . "$ENV_FILE"; set +a
[ -n "${OPENROUTER_API_KEY:-}" ] || { echo "FATAL: key empty"; exit 1; }
export OPENROUTER_API_KEY

/usr/bin/python3 - <<'PYEOF'
import base64, json, os, urllib.request
from pathlib import Path

KEY = os.environ["OPENROUTER_API_KEY"]
SRC = Path("/Users/pagemacmini/Documents/MAPLAB_外燴預擺/training-外燴照片擺設/review-smoke")
OUT = Path("/Users/pagemacmini/Documents/MAPLAB_外燴預擺/資料/openrouter-vision-smoke-20260918.md")
IMAGES = ["新居入厝.jpg", "純白主題風生日派對.jpg"]
MODEL = "google/gemma-4-31b-it:free"

PROMPT = """你是外燴器材盤點員。列出這張照片中所有「器皿與器材」(不是食物),逐件輸出:
- 名稱(中文,例:金色圓環三層點心架、方形保溫餐爐 chafing dish、蛋糕高腳瓷盤)
- 材質/顏色
- 數量(看得到幾件寫幾件)
- 大小線索(只能寫「相對於桌面/其他物件」的觀察,禁止猜絕對尺寸)
只列器皿器材,桌巾/裝飾花/立牌也算。用條列,不要開場白。"""

results = []
log_lines = []
for name in IMAGES:
    b64 = base64.b64encode((SRC / name).read_bytes()).decode()
    payload = json.dumps({
        "model": MODEL, "max_tokens": 3000,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        ]}],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=payload,
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=240))
        c = (d.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        err = d.get("error", {}).get("message", "")
        status = "OK" if c.strip() else f"EMPTY({err[:80]})"
        results.append((name, status, c.strip()))
    except Exception as e:
        results.append((name, f"ERR:{type(e).__name__}", str(e)[:200]))
    log_lines.append(f"20260918,vision-smoke-T-A4,{results[-1][1].split('(')[0]},{name} ({MODEL.split('/')[-1]})")

body = ["# OpenRouter 視覺煙霧測試 — 器皿預標註(2026-09-18, Owner 5381)",
        "", f"- 模型:{MODEL};僅送 2 張 Fable5 已目視確認無人像的縮圖(1200px)。", ""]
for name, status, text in results:
    body += [f"## {name} — {status}", "", text, ""]
OUT.write_text("\n".join(body))

log = Path("/Users/pagemacmini/maplab-ai-handbook/data/free-quota/usage_log.csv")
with log.open("a") as f:
    for ln in log_lines:
        f.write(ln + "\n")

for name, status, text in results:
    print(f"=== {name} [{status}] ===")
    print(text[:1500])
    print()
PYEOF
