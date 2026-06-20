# A6/A5 地端報價模型調教技能書

版本：v1.0 | 建立：2026-06-14 | 維護：A0 + A5/A6

---

## 何時使用

看到以下任一情境，先讀這本：

- A6 Telegram 收到競品菜單、報價截圖、圖片菜單 OCR。
- Owner 要「辨識所有品項 → 做 MAPLAB 雷同品項 → 成本總價 * 5 → 產試算表」。
- A5 本地模型輸出 Thinking、沒有 JSON、發明不存在的菜名。
- `createQuoteVariants` 有 payload 但 GAS 沒回 Google Sheet URL。

---

## 2026-06-14 實測結論

### 品質評估

| 能力 | 實測品質 | 判斷 |
|---|---:|---|
| Telegram bot 存活與接圖 | 可用 | A6 能存照片到 `data/a6-photos/`，但長駐環境曾找不到 `claude` CLI |
| 競品菜單意圖判斷 | 修後可用 | 原本「比照、雷同、成本*5、毛利、試算表」不會進報價路由，已補 route guard |
| 地端模型 gemma4 直接產報價 | 不可單獨信任 | 會輸出 Thinking，可能沒有合法 JSON，速度約 40-100 秒 |
| MAPLAB 品項匹配 | 黃燈 | prompt 收窄後會引用 Items，但仍要用 deterministic fallback 保底 |
| Sheet 報價 payload | 修後可用 | fallback 可產 `createQuoteVariants` JSON，A6 `_extract_form_data()` 可讀 |
| live Case Store 讀 Sheet | 阻塞 | Google token 回 `invalid_grant`；fallback seed 不是 live Sheet 成功 |
| GAS 建 Sheet | 黃燈 | `createQuoteVariants` 可打到 GAS；缺 `eventDate` 會被拒絕 |

### 本次競品菜單試算結果

OCR 菜單包含：手撕豬小漢堡、燻雞三明治、蛋沙拉可頌、鴨胸串、雞腿排蔬菜盤、義大利麵、迷你小塔、馬卡龍、泡芙、布丁、甜甜圈蛋糕、蜂蜜檸檬飲、伯爵茶。

deterministic fallback 產出：

- 可估 MAPLAB 雷同品項：12 項。
- 食材/餐點成本小計：NT$5,520。
- 成本乘以 5 報價：NT$27,600。
- 食材成本佔比：約 20%；餐點毛利：約 80%。
- 待人工補成本：甜甜圈蛋糕、烤蔬菜盤。

---

## 正確架構

A6 不應該自己算正式報價。A6 的責任是：

1. 辨識任務類型與圖片/OCR 內容。
2. 把報價任務交給 A5。
3. 確認 A5 輸出有合法 JSON。
4. 呼叫 GAS 產出 Google Sheet 副本。
5. 把 Sheet URL 回給 Owner/業務。

A5 的責任是：

1. 讀 `data/items_master.json` 的 MAPLAB 品項與成本。
2. 匹配雷同品項。
3. 成本未知就列 `needsManualCost`，不硬猜。
4. 產出 `createQuoteVariants` payload。

---

## 調教規則

### 1. prompt 只能降低風險，不能當保證

prompt 要明寫：

- 只能用 `data/items_master.json` 裡存在且有成本的品項。
- 不可發明「核心主餐點模擬組合」「基底組」「模擬菜單」。
- 不可輸出 Thinking、自我對話、模型訓練說明。
- 競品菜單/雷同品項/成本乘以 5 一律輸出 `action=createQuoteVariants`。

但即使 prompt 寫了，地端模型仍可能違規，所以必須有後處理。

### 2. output sanitize 是必要防線

Telegram-facing output 必做：

- 移除 ANSI/control codes。
- 移除 `<think>...</think>`。
- 如果開頭是 `Thinking...` 且找不到正式 Markdown/JSON，就丟棄 raw answer，不送給業務。

### 3. JSON 不合法時，直接 deterministic fallback

若模型沒有合法 ```json 區塊：

1. 從 OCR 文字找競品品項與數量。
2. 用固定 mapping 對 `items_master.json` 的 `item_id`。
3. 只採用 `default_cost > 0` 的 MAPLAB 品項。
4. `foodCost = sum(qty * unitCost)`。
5. `foodRevenue = foodCost * 5`。
6. `totalRevenue = totalCost * 5`。
7. 產 `createQuoteVariants` JSON。

### 4. GAS payload 必填欄位

`createQuoteVariants` 最少要有：

```json
{
  "action": "createQuoteVariants",
  "base": {
    "clientName": "競品菜單試算",
    "eventDate": "2026-06-14",
    "eventName": "MAPLAB 雷同品項成本乘以5試算"
  },
  "variants": [
    {
      "label": "A",
      "title": "MAPLAB 雷同品項成本乘以5試算",
      "menu": [],
      "foodCost": 5520,
      "foodRevenue": 27600,
      "totalCost": 5520,
      "totalRevenue": 27600
    }
  ]
}
```

沒有 `eventDate` / `date` 時，GAS 會回：

```text
活動日期為空（表單 date / eventDate 欄位都沒值）
```

若使用者沒有提供活動日期，草稿可用試算日當 `eventDate`，但必須在 `dietaryNotes` 註明「eventDate 暫填試算日，不是正式活動日」。

---

## 最短驗證指令

### `.env` 與 secrets 操作邊界

Agent 可以在任務需要時 source 或讀取 `bot_a6/.env` 來啟動/驗證 A6，但要遵守：

- 可以回報：key 是否存在、非秘密 runtime 值，例如 `A5_LOCAL_MODEL=gemma4:latest`。
- 不要回報：Telegram token、OAuth token、API key、GAS Web App URL 的完整值。
- 需要檢查 secret 是否有效時，用實際 API smoke test 驗證，不把 secret 值印出來。
- 需要修改、輪替或貼出 secret 時，才向 Owner 明確確認。

安全規則的目的不是阻止 agent 上班，而是避免把 secret 洩到聊天、log、commit 或 review bundle。

### 編譯

```bash
rtk bot/venv/bin/python -c 'import os, tempfile, py_compile; files=["bot_a6/bot_a6.py","bot_a6/a5_quote_engine.py"]; [py_compile.compile(f, cfile=os.path.join(tempfile.gettempdir(), os.path.basename(f)+".pyc"), doraise=True) for f in files]; print("py_compile ok")'
```

### 路由

```bash
rtk bot/venv/bin/python -c 'import json, sys; sys.path.insert(0,"bot_a6"); import bot_a6; samples={"status":"你現在是跑什麼模型","competitor":"比照這張菜單做我們雷同品項，成本*5報價，毛利要過20%，產試算表"}; print(json.dumps({k: {"status": bot_a6._looks_like_runtime_status_request(v), "quote": bot_a6._looks_like_quote_request(v)} for k,v in samples.items()}, ensure_ascii=False, indent=2))'
```

### deterministic fallback

```bash
rtk bot/venv/bin/python -c 'import json, sys; sys.path.insert(0,"bot_a6"); import a5_quote_engine as e; msg="競品菜單 OCR：BBQ手撕豬小漢堡20個、卡士達迷你泡芙12個，成本*5產試算表"; payload=e._build_competitor_quote_payload(msg); print(json.dumps({"action":payload["action"],"foodCost":payload["variants"][0]["foodCost"],"foodRevenue":payload["variants"][0]["foodRevenue"]},ensure_ascii=False,indent=2))'
```

### live Case Store，不可被 fallback 騙過

```bash
rtk env CASE_STORE_FALLBACK_JSON=/tmp/a6-case-store-missing.json bot/venv/bin/python bot_a6/case_store.py today --rows 20 --limit 1
```

如果看到 `invalid_grant`，代表 live Google Sheets 讀取仍未恢復。

---

## 調度判斷

可以派給 A6/A5：

- 競品菜單 OCR 後產內部試算草稿。
- 用 MAPLAB 已知品項成本做 `成本 * 5` 報價。
- 產 `createQuoteVariants` payload，再由 GAS 建 Google Sheet 副本。

不要讓 A6/A5 自動做：

- 把成本未知品項硬塞進正式報價。
- 只靠模型猜菜名、猜單位成本。
- 在 Google OAuth 尚未修好時宣稱 live Case Store 可讀。
- 沒有 Sheet URL 就說報價完成。

---

## 本次程式落點

- `bot_a6/bot_a6.py`：修 Claude CLI path、競品菜單 quote intent、圖片 caption 報價路由。
- `bot_a6/a5_quote_engine.py`：加 Items catalog prompt、Thinking sanitize、deterministic `createQuoteVariants` fallback、eventDate 補值。
- `workbook/reviews/A5-QUOTE-20260614-A6-ROUTE-TEST/`：本次地端模型調教 review bundle。
