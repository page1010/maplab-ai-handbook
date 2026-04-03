# A6 bot_a6.py × createSlides 整合評估
版本：v1.0 | 建立：2026-04-03 | 評估者：A1

---

## a) bot_a6.py 目前運作方式

```
Telegram 訊息 → handle_message() → _run_claude_guarded()
  → asyncio.create_task(_run_claude_background())
    → claude_ask()
      → asyncio.create_subprocess_exec("claude", "-p", "--dangerously-skip-permissions", full_prompt)
        → 等待 stdout → 回傳文字 → bot.send_message()
```

**核心機制：**
- Long polling 持續監聽 Telegram 群組
- 每則訊息都組合成完整 prompt（系統提示 + 對話歷史 + 本次訊息）丟給 `claude -p`
- Claude 回傳純文字，bot 直接轉發給群組
- 一次只處理一則（`asyncio.Semaphore(1)`），有排隊保護

---

## b) 目前有沒有能力直接發 HTTP POST？

**沒有。**

bot_a6.py 的 import 清單：
```python
import asyncio, json, logging, os, subprocess, sys
from collections import deque
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ...
```

**沒有 `requests`、`urllib`、`httpx`、`aiohttp`。**

現在唯一能做 HTTP 的路徑是讓 `claude -p` 在回應中產生 curl 指令，但 bot 只取 stdout 文字，不執行它。

---

## c) 整合後的程式碼大概長什麼樣（如果加了 requests）

```python
import requests  # 新增

GAS_URL = "https://script.google.com/macros/s/AKfycbyMvc3-gl1sI_9prPjzp0zg0N353f9fL5jzR-9wm_xYPZ8A8IsTJSoTjbmDefYFI0o/exec"

def post_gas(payload: dict) -> dict:
    """POST 到 GAS Web App，自動跟隨 302 redirect。"""
    resp = requests.post(
        GAS_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        allow_redirects=True,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    text = (update.message.text or "").strip()
    if not text:
        return

    # ── 新增：偵測「報價」關鍵字，走自動雙 POST 流程 ──
    if text.startswith("報價") or text.startswith("新報價"):
        await _handle_auto_quote(update, context, text)
        return

    # 其他訊息繼續走 Claude
    await _run_claude_guarded(update, context, text)


async def _handle_auto_quote(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """
    觸發：「報價 王小明 婚禮 80人 預算6萬」
    流程：createQuote → createSlides → 回傳兩個 URL
    """
    await update.message.reply_text("⏳ 建立報價單 + Slide 中，約 20 秒…")

    # Step 1：解析基本欄位（簡單版，正式版可丟 Claude 解析）
    parts = text.split()
    # 格式：報價 客名 活動類型 人數 預算
    client_name = parts[1] if len(parts) > 1 else "未命名客戶"
    event_type  = parts[2] if len(parts) > 2 else "活動"
    pax         = parts[3].replace("人", "") if len(parts) > 3 else "30"
    budget      = parts[4].replace("預算", "") if len(parts) > 4 else ""

    try:
        # Step 2：createQuote
        quote_payload = {
            "action": "createQuote",
            "clientName": client_name,
            "eventType": event_type,
            "pax": pax,
        }
        if budget:
            quote_payload["budget"] = budget

        quote_result = post_gas(quote_payload)
        if not quote_result.get("success"):
            await update.message.reply_text(f"❌ 報價單建立失敗：{quote_result}")
            return

        sheet_url      = quote_result.get("sheetUrl", "")
        spreadsheet_id = sheet_url.split("/d/")[1].split("/")[0] if "/d/" in sheet_url else ""

        # Step 3：createSlides
        slide_result = post_gas({
            "action": "createSlides",
            "spreadsheetId": spreadsheet_id,
            "clientName": client_name,
        })
        if not slide_result.get("success"):
            await update.message.reply_text(
                f"✅ 報價單已建立\n📎 {sheet_url}\n\n❌ Slide 建立失敗：{slide_result}"
            )
            return

        slide_url = slide_result.get("slideUrl", "")

        await update.message.reply_text(
            f"✅ 報價完成！\n\n"
            f"客戶：{client_name}\n"
            f"活動：{event_type} / {pax}人\n\n"
            f"📊 報價單：{sheet_url}\n"
            f"📑 Slide 簡報：{slide_url}\n\n"
            f"⚠️ 請確認品項和金額後再發給客戶"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ 自動報價失敗：{e}")
```

---

## d) 需要加什麼

| 項目 | 說明 | 工作量 |
|------|------|--------|
| `import requests` | 加到 bot_a6.py 頂部 | 1行 |
| `pip install requests` | requirements.txt / launchd env | 5分鐘 |
| `post_gas()` helper | 見上方範例 | 15行 |
| `_handle_auto_quote()` | 解析 + 雙 POST + 回傳 | ~40行 |
| `handle_message()` 路由 | 偵測「報價」關鍵字分流 | 5行 |
| 訊息解析強化（可選） | 目前是 split()，可改丟 Claude 解析自然語言 | 視需求 |

**requirements.txt 確認（需有 requests）：**
```
python-telegram-bot[job-queue]>=21
python-dotenv
requests  # ← 需新增
```

---

## e) 完整流程圖

```
Telegram 業務訊息
  「報價 王小明 婚禮 80人 預算6萬」
          │
          ▼
  handle_message() 偵測關鍵字「報價」
          │
          ▼
  bot 回覆「⏳ 建立中…」
          │
          ▼
  post_gas({ action:"createQuote", clientName:"王小明", eventType:"婚禮", pax:"80" })
          │
          ▼ 回傳 { success:true, sheetUrl:"https://docs.google.com/spreadsheets/d/XXX" }
          │
  解析 spreadsheetId = "XXX"
          │
          ▼
  post_gas({ action:"createSlides", spreadsheetId:"XXX", clientName:"王小明" })
          │
          ▼ 回傳 { success:true, slideUrl:"https://docs.google.com/presentation/d/YYY" }
          │
          ▼
  bot 回傳：
    ✅ 報價完成！
    📊 報價單：https://docs.google.com/spreadsheets/d/XXX
    📑 Slide 簡報：https://docs.google.com/presentation/d/YYY
    ⚠️ 請確認品項和金額後再發給客戶
```

---

## 評估結論

| 項目 | 結論 |
|------|------|
| 現有 bot 有 HTTP 能力？ | ❌ 沒有，需加 requests |
| 整合難度 | ✅ 低，~60行新程式碼 |
| 是否需要改 GAS 端？ | ❌ 不需要，GAS 已支援 createSlides |
| 主要風險 | Slide 生成約 10-20 秒，Telegram 要等；需加 timeout 處理 |
| 建議訊息解析方式 | 簡單關鍵字 → split() 即可；複雜自然語言 → 先丟 Claude 解析再 POST |
| 建議執行 | Owner 確認後，A0 或 A1 直接 patch bot_a6.py |

---

*評估日期：2026-04-03 | 基於 bot_a6.py + skills/a6-rapid-quote-sop.md SECTION 8/9*
