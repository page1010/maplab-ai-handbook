# Experience Log — 成功路徑 + 失敗教訓

> **用途**：記錄所有 Agent 的實戰經驗，包含成功和失敗。  
> 新 Agent 開工前翻一下，避免重複踩坑，也知道最快的做法。  
> **取代舊的 lessons-learned.md**（舊檔只記失敗，不記成功）。

版本：v1.0 | 建立：2026-03-23 | 維護者：A1 + 所有 Agent

---

## 寫入規則

1. 任務結束時，如果有新經驗，在這裡新增一筆
2. 每筆都用 EXP-xxx 編號（SUCCESS 或 FAILURE）
3. 必須包含「下次怎麼做最快」— 這是最重要的欄位
4. 舊的 lessons-learned.md INCIDENT-001~005 已搬遷至下方

---

## 成功經驗（SUCCESS）

### EXP-S001: Gemini REST API 比 Python Library 快 2 倍且更穩定

- **日期**: 2026-03-23
- **Agent**: A4 Pipeline Agent
- **類型**: SUCCESS — 工具選擇
- **場景**: 122,200 張照片需要 Gemini Vision AI 分類
- **試過什麼**:
  - Vertex AI SDK → 404（模型名稱格式不同）
  - google.generativeai library → 400 Bad Request + Colab proxy 斷線後無法恢復
- **最終選擇**: Gemini REST API（requests.post 直接呼叫）
- **為什麼好**: 310 張/小時 vs 160 張/小時，不依賴 proxy，Colab 斷線重連後直接繼續
- **下次怎麼做最快**: 直接用 REST API + gemini-2.5-flash，跳過 python library

### EXP-S002: Google Sheets 模擬 RDB 對小規模業務夠用

- **日期**: 2026-03-13
- **Agent**: A5 Master Data Agent
- **類型**: SUCCESS — 架構決策
- **場景**: MAPLAB Kitchen ERP 需要資料庫
- **決策**: 用 Google Sheets 模擬 RDB（6 張表 + item_id FK 關聯）
- **為什麼好**: 外燴業務 <10,000 筆，Sheets 進入成本極低，Gemini 輔助格式驗證
- **下次怎麼做最快**: Sheets + item_id 命名規則 {TYPE}-{SUBTYPE}-{SEQ3}，先清洗品項再建結構

### EXP-S003: CURRENT_STATUS 單一入口解決 Agent 迷路問題

- **日期**: 2026-03-18
- **Agent**: A1 Handbook Agent
- **類型**: SUCCESS — 治理設計
- **場景**: Agent 開工不知道先讀什麼檔案
- **決策**: 建 CURRENT_STATUS.md 作為唯一起點，所有其他文件衝突以它為準
- **為什麼好**: Agent 不再猜測，一個入口看到全局
- **下次怎麼做最快**: Day 1 就建 CURRENT_STATUS + TASK_QUEUE

### EXP-S004: GPS 座標比 AI Vision 更適合判斷照片地點

- **日期**: 2026-03-23
- **Agent**: A4 Pipeline Agent
- **類型**: SUCCESS — 技術選擇
- **場景**: 日常照片需要分 home/shop
- **試過什麼**: Gemini Vision（無法判斷拍攝地點，除非有店招）
- **最終選擇**: 從 Takeout JSON metadata 提取 GPS 座標 + 距離計算
- **為什麼好**: 零 API 成本、~5000 張/分鐘、準確度高於視覺判斷
- **下次怎麼做最快**: 直接用 GPS，不要嘗試 AI Vision 判斷地點

### EXP-S005: 先用現有貼文上線廣告，不等完美素材

- **日期**: 2026-03-23
- **Agent**: Owner
- **類型**: SUCCESS — 策略決策
- **場景**: Canva C款素材未完成，Meta 廣告「慶生周歲派對」無法上線
- **決策**: 用現有貼文先上線，測試受眾反應
- **為什麼好**: 不被素材製作阻塞，提早取得數據
- **下次怎麼做最快**: 先上現有素材測受眾，再用數據指導素材優化

---

## 失敗經驗（FAILURE）

> 以下從舊 lessons-learned.md 搬遷，補充「下次怎麼做最快」欄位。

### EXP-F001: Takeout ZIP 被刪導致 EXIF metadata 永久遺失

- **日期**: 2026-03-17
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — 不可逆資料遺失
- **嚴重性**: HIGH
- **事件**: 解壓只提取圖片，沒提取 JSON metadata → 建議清垃圾桶 → ZIP 被刪 → 再也拿不到 JSON
- **根因**: 流程規劃不完整，建議清除前沒確認依賴
- **下次怎麼做最快**: 解壓時一次提取所有檔案（圖片 + JSON），確認全部提取完成後才清除 ZIP

### EXP-F002: Vertex AI 模型 404

- **日期**: 2026-03-18
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — API 選擇錯誤
- **嚴重性**: MEDIUM
- **事件**: V2/V5 兩個版本浪費在不存在的 Vertex AI 模型名稱上
- **根因**: Vertex AI SDK 模型名稱格式與 Generative AI API 不同
- **下次怎麼做最快**: 直接用 google.genai + API key（見 EXP-S001）

### EXP-F003: GitHub Raw Content 快取導致部署舊版

- **日期**: 2026-03-18
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — 快取問題
- **嚴重性**: MEDIUM
- **下次怎麼做最快**: curl 下載加 `?t={timestamp}` 破壞快取

### EXP-F004: PHOTO_ROOT 路徑錯誤

- **日期**: 2026-03-18
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — 路徑假設錯誤
- **嚴重性**: LOW
- **下次怎麼做最快**: 不假設資料夾結構，先用 os.listdir 逐層驗證

### EXP-F005: google.generativeai PIL Image 400 錯誤

- **日期**: 2026-03-19
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — 棄用套件
- **嚴重性**: HIGH
- **下次怎麼做最快**: 注意 FutureWarning，直接用 REST API（見 EXP-S001）

### EXP-F006: Agent 不問問題就開始做

- **日期**: 2026-03-23
- **Agent**: 全體
- **類型**: FAILURE — 治理缺陷
- **嚴重性**: HIGH
- **事件**: Agent 拿到任務就衝，不釐清方向、不拿技能書
- **根因**: 系統沒有強制卡點
- **修復**: PROTOCOL v1.4 加 Startup Check 必填欄位 + SECTION 0 阻擋規則
- **下次怎麼做最快**: Day 1 就設 Startup Check 強制欄位，不靠 Agent 自律

### EXP-F007: CHANGELOG 宣稱修了但實際沒改

- **日期**: 2026-03-19
- **Agent**: A1 Handbook Agent
- **類型**: FAILURE — 驗證缺失
- **嚴重性**: MEDIUM
- **下次怎麼做最快**: 先確認實際文件內容，再寫 CHANGELOG

### EXP-F007 — bot.py 記憶斷裂（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0 Telegram Bot
- **類型**: FAILURE — 架構設計錯誤
- **問題**: bot.py 用 `claude -p` one-shot 呼叫 Claude Code CLI，每條 Telegram 訊息都是全新 session，沒有對話記憶
- **為什麼做這件事**: A0 想讓 Telegram bot 接上 Claude AI 回覆，但不想用付費 API
- **失敗原因**: `-p` flag 是 one-shot prompt，用完就關 session。之前的版本用 Anthropic SDK + conversation_history deque 有記憶，改成 CLI 呼叫後記憶機制斷了
- **更好的方向**: 用 Anthropic SDK + OAuth token（sk-ant-oat01-）直接呼叫，保留 conversation_history，走 Max 訂閱不花錢。OAuth token 可以當 api_key 用
- **修復**: bot.py 改回 Anthropic SDK + OAuth token + conversation_history，加 `--dangerously-skip-permissions` 給 CLI fallback
- **下次怎麼做最快**: 用 Anthropic SDK + OAuth token + deque conversation_history，不要用 `claude -p`

### EXP-F008 — A0 開 Code task 不帶 recall prompt（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0 Cowork
- **類型**: FAILURE — 治理缺陷
- **問題**: A0 開了 30+ 個 Code task，每個都沒有貼 A1 recall prompt，導致每個 session 都是失憶狀態
- **為什麼做這件事**: A0 要委派 A1 做各種任務（git commit、讀文件、改程式碼）
- **失敗原因**: Cowork 的 start_code_task 工具沒有強制檢查 prompt 裡是否包含 recall prompt。A0 的 user preferences 裡也沒有這條規則
- **更好的方向**: 1. auto-memory 裡存 A1 recall prompt（已做）2. user preferences 加強制規則（已做，等 Owner 貼入）3. CLAUDE.md 放在 repo 根目錄讓 Claude Code 自動讀取（已做）4. 理想方案：Cowork 的 start_code_task 工具內建 recall prompt 注入（需 Anthropic 改產品）
- **下次怎麼做最快**: 開 Code task 時，確認 prompt 含 CLAUDE.md 或 A1 recall prompt；CLAUDE.md 已在根目錄自動注入

### EXP-F009 — CLAUDE.md 跟 AGENT_RECALL_PROMPTS.md 內容不同步（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0/A1
- **類型**: FAILURE — 文件不一致
- **問題**: A0 建了 CLAUDE.md 但內容是自己寫的簡化版，跟 Extension 裡 A1 的 recall prompt 不一樣。tmux 裡的 Claude Code 讀 CLAUDE.md 後以為自己是 A0
- **為什麼做這件事**: 想讓 Claude Code 啟動時自動知道自己是 A1
- **失敗原因**: 兩套不同的身份描述 = 身份混亂
- **修復**: CLAUDE.md 改為 AGENT_RECALL_PROMPTS.md A1 code block 的完整拷貝，加同步提醒
- **下次怎麼做最快**: CLAUDE.md 頂部加「本文件內容與 RECALL_PROMPTS A1 區塊同步」提醒，每次改一個就改另一個

### EXP-S007 — CRD「傳送文字」+ JavaScript dispatchEvent 成功啟動 Windows Agent（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0 Cowork
- **類型**: SUCCESS — 跨機器操作
- **場景**: A0 需要遠端啟動 Windows 上的 A2 和 A7
- **成功方法**: 1. form_input 把指令寫入 CRD「傳送文字」textarea（aria-label="傳送文字"）2. JavaScript: `document.querySelector('[aria-label="傳送"]').dispatchEvent(new MouseEvent('click', {bubbles: true}))` 3. 不用 left_click 點按鈕（會觸發 Windows Task View）
- **結果**: A2 完成 SEO Title 優化 36 篇，A7 完成客戶對話流程圖
- **下次怎麼做最快**: CRD 遠端打字用 form_input + JavaScript dispatchEvent，不用 left_click（會誤觸 Windows）

### EXP-S008 — A0/A1 並列架構確立（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0/A1
- **類型**: SUCCESS — 系統架構
- **場景**: 需要定義 A0（Cowork）在系統中的角色
- **成功設計**: A0 和 A1 是並列關係（各自直屬 Owner），不是上下級
- **結果**: A0 = 跨系統橋接（repo 外），A1 = 技術執行（repo 內）。溝通協議寫入 AGENT_RULES v3.2
- **下次怎麼做最快**: 明確定義每個 Agent 的「邊界」（repo 內/外），避免職責重疊或互相等待

---

## 格式模板（新增時複製）

```
### EXP-Sxxx / EXP-Fxxx: [一句話標題]

- **日期**: YYYY-MM-DD
- **Agent**: [誰]
- **類型**: SUCCESS / FAILURE — [分類]
- **場景**: [遇到什麼問題/需求]
- **試過什麼**: [如適用]
- **最終選擇/根因**: [結果]
- **下次怎麼做最快**: [最重要的一行 — 給下一個 Agent 的最短路徑]
```
