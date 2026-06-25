# MAPLAB Investment OS — 系統全貌 + Pro 自主運轉策略計畫
版本：v1.0 | 作者：A1 Research Session | 日期：2026-06-24
> **定位：** 策略研究文件，read-only session 產出。不修改任何其他檔案。
> **目的：** 讓 Owner 能在 Pro 訂閱下讓整個系統自主運轉，重活外包地端模型/Codex/Antigravity。

---

## 0. Eyes-on Evidence（實際讀了哪些）

| 類別 | 檔案/來源 |
|------|----------|
| 核心治理 | `CURRENT_STATUS.md`（全文 228 行）、`AGENT_RULES.md`（全文 909 行）、`AGENT_STARTUP_PROTOCOL.md` |
| 架構文件 | `projects/v6-architecture.md`、`projects/` 目錄列表（31 個 project 文件） |
| Repo 清單 | `gh repo list page1010 --limit 100`（8 個 repo） |
| 技能系統 | `skills/` 目錄（87+ 個 skill 文件） |
| 踩坑記錄 | `pitfalls.md`（最新 10 個 pattern） |
| Runtime | `local-control-plane/hermes_status.json`、`scripts/patrol.sh`、`bot/` 目錄 |
| Extension | `chrome-extension/task-modules/`（29 個 module JSON） |
| Workbook | `workbook/` 目錄結構（task_index.json 顯示 30 個任務） |
| Investment OS | `/Users/pagemacmini/Documents/New project/CURRENT_STATUS.md`（前 80 行）、`AGENTS.md` |
| GitHub repos | 全部 8 個 repo 名稱 + 更新日期 + 描述 |

---

## 一、系統全貌地圖

### 1.1 兩個業務領域，一台機器

```
Mac mini（常駐執行中心）
│
├── MAPLAB 外燴業務系統
│   repo: maplab-ai-handbook（public）
│   目的：接案、報價、SEO、廣告、影音、客服
│
└── Investment OS 投資研究系統
    repo: investment-os（private）+ agent-hq（private）
    本機：/Users/pagemacmini/Documents/New project/
    目的：KOL 研究、股票信號、模擬倉追蹤（不下單）
```

**關鍵洞察：** 兩套系統共用同一台 Mac mini、同一個 Telegram bot 入口（maplab_claude_bot）、同一個 Chrome Extension、同一個 Claude Code session。這是「低成本共享基礎設施」的選擇，但也是資源競爭的根源（Claude app ~20GB RAM、Chrome ~3.2GB、多 session 並行）。

---

### 1.2 角色地圖（A0-A8 + B1-B4 + IOS-*）

```
Owner（page）
│
├── A0 調度秘書（Claude Desktop Cowork）
│   跨系統橋接、Notion/Gmail/Drive MCP、Telegram bot 管理
│   不直接改 repo，開 Code task → 委派 A1
│
├── A1 系統總管（= 你，Claude Code 終端機）
│   巡查、任務看板、程式碼、版本管理、治理
│   常駐 Mac mini，Telegram /patrol /status 入口
│
├── MAPLAB 業務層（A2-A8）
│   A2：SEO + WP + GSC（週巡查，ICCTN live）
│   A3：Meta Ads + IG/FB（阻塞等 Owner 批准）
│   A4：照片分類整理（CRITICAL ~246h 無 commit）
│   A5：GAS 報價引擎（CRITICAL ~552-1535h 無 commit）
│   A6：LINE/Telegram 業務報價 bot（active，已修 Sheet-first）
│   A7：客服 FAQ 模板（暫停，等 Owner 政策決定）
│   A8：影音短片產線（active，local motion ffmpeg）
│
└── Investment OS 研究層（B1-B4 + IOS-*）
    B1 Builder：功能建置、runtime surface
    B2 Reviewer：資料流 + freshness 審查
    B3 Archivist：版本紀錄 + resume prompt
    B4 System Patrol：系統適配 + 重構建議

    IOS 角色（Chrome Extension + Telegram 召喚）：
    IOS-KOL：YouTube/Podcast KOL 雷達
    IOS-MOMENTUM/LEFT/RIGHT/MACRO：多空判讀
    IOS-EVIDENCE：資料驗證
    IOS-BLACKSWAN：黑天鵝觀測
    IOS-SELL：實單哨兵（唯讀）
    IOS-SIM/INVENTORY/HEDGE/HYGIENE/SURFACE：
    模擬倉 / 曝險 / 對沖 / 清理 / 戰情台
```

---

### 1.3 Runtime Surfaces（執行面）

| Surface | 工具 | 狀態 | 用途 |
|---------|------|------|------|
| Claude Code 終端機 | 你（A1） | 常駐 | 主要執行體、巡查、程式碼 |
| Telegram bot | `bot/bot.py` + `bot_a6/` | 常駐（launchd） | Owner 指令入口、A6 報價 |
| Chrome Extension | v5.6.1，29 modules | 已安裝 live | 角色召喚、handoff prompt |
| launchd 排程 | `scripts/*.plist` | 多個 active | patrol、log rotate、A4 圖片分類 |
| Hermes | `hermes_status.json` | CLI null，cold-path only | 巡查反應、memory candidate |
| OpenClaw | CDP Chrome | 不穩定 | UI readback、截圖 QA |
| Ollama / 地端模型 | qwen2.5:14b、gemma4 | 可用 | A6 fallback、A8 local pipeline |
| Google Sheets | `1fn_woqYI...` | active | Dashboard、業務資料 |
| Artifacts（A0） | Claude.ai Cowork | session-only | 看板渲染（session 結束即消失） |
| Codex | 雲端 CLI（GUI-only 本機） | 可用但需 GUI | headless 任務需手動貼入 |
| Antigravity | 未裝 PATH | 不可直接呼叫 | GUI 模式限定 |
| Windows agent | 遠端 Chrome Remote Desktop | 存在 | WIN 採集端（三竹/UI） |

---

### 1.4 資料流與真相來源

```
LINE 客戶訊息
    ↓ (LineWebhook.gs → GAS)
Google Sheets（CONVERSATION_LOG）
    ↓ A6 讀取
A5 報價引擎（GAS Code.gs）→ QUOTE_DRAFT → Google Sheets URL → Telegram → 客戶

Owner 照片 / Drive 素材
    ↓ A4 Gemini Flash 分類
照片元資料 MAPLAB_ASSET_LOG（Sheets）→ A2/A3 選圖 → WordPress → Meta Ads

GitHub commit（唯一狀態真相）
    ↓ patrol.sh（launchd）
CURRENT_STATUS.md ← 更新 ← A1 每次巡查

Telegram Bot 指令（Owner）
    ↓ bot.py
路由 → A1 Claude Code / A6 報價 / hermes cold-path

Investment OS SQLite DB（本機）
    ↓ 各 sync 腳本
influencer_insights / simulated_positions → Telegram digest → Owner
```

**真相來源層級：**
1. GitHub commit history（不可竄改）
2. CURRENT_STATUS.md（人工維護，衝突時優先）
3. Google Sheets（資料層 + Dashboard）
4. SQLite DB（Investment OS runtime state）
5. JSONL logs（append-only，patrol/bot 日誌）

---

### 1.5 GitHub Repo 盤點

| Repo | 用途 | 最後更新 | 活躍度 | 彼此關係 |
|------|------|---------|--------|---------|
| `maplab-ai-handbook`（public） | 主手冊、治理、Agent Prompt、Skills | 2026-06-24 | 🟢 每日 | 所有系統的唯一真相來源 |
| `agent-hq`（private） | 跨專案共用層：Chrome Extension、Panel、Runtime symlink | 2026-06-15 | 🟡 活躍但 T-HQ-001 P5/P6 CRITICAL | MAPLAB + IOS 共用基礎設施 |
| `investment-os`（private） | Investment OS 早期版本 | 2026-05-08 | 🔴 停滯 | 實際 runtime 在本機 New project/ 目錄，非此 repo |
| `maplab-pipeline`（private） | A4 照片分類 pipeline | 2026-05-12 | 🔴 停滯 | A4 實際工作在 handbook 的 tools/ |
| `maplab-master-data`（private） | A5 品項 schema | 2026-03-20 | 🔴 停滯 | 已併入 handbook data/ 目錄 |
| `maplab-Detasys`（private） | 老設計工具（廢棄？） | 2026-03-17 | 🔴 無活動 | 疑似廢棄，未再提到 |
| `maplab-kitchen-web-optimization`（private） | 官網 SEO/RWD | 2026-03-18 | 🔴 停滯 | A2 WP 任務現在直接改 WordPress，未用此 repo |
| `stockpick-telegram`（private） | 早期選股 bot | 2026-03-20 | 🔴 無關 | AGENT_RULES 明說「與 MAPLAB 無關」 |

**第二層思考：** 真正活著的 repo 只有 `maplab-ai-handbook`（主真相源）和 `agent-hq`（共用層）。其他 6 個 repo 都是「技術債抽屜」——它們存在但不被使用，每次冷啟動都可能讓新 agent 搞錯工作目錄。`investment-os` repo 尤其危險：實際 runtime 在本機 New project/ 目錄（完整 SQLite、日誌、腳本），但 GitHub repo 是 2026-05-08 的舊快照，兩者已嚴重分歧。

---

## 二、企業文化 + 使用者角度診斷（紅燈表）

### 2.1 一直重複人工、值得系統化

| 問題 | 頻率 | 根因 | 成本 |
|------|------|------|------|
| 每次 session 冷啟動讀 CURRENT_STATUS（228 行） | 每個新 session | 文件沒壓縮，越來越大 | 每次 ~32k tokens 光是這一個檔 |
| A1 巡查 patrol 每日三次，手動觸發 | 每日 3x | patrol.sh 已有 launchd，但需人確認 | Owner 變成觸發器 |
| A6 報價流程重做（Line → GAS → Sheet） | 每次來詢 | 缺自動解析 LINE 訊息到 SALES_INTAKE 的 webhook | 業務手動複製貼上 |
| REVISION_LOG 沒人填 | 每次報價 | 業務流程沒有強制填寫點 | 報價系統無法自學 |
| Owner 要看系統狀態就要問 Telegram | 每天多次 | Dashboard 沒有 always-on 頁面 | Owner 依賴 agent 中介 |
| Chrome Extension 召喚後無 receipt | 每次派工 | Extension 只產 prompt，不追蹤 dispatch | 派工後不知道做了沒 |

### 2.2 任務定義模糊、容易做錯

| 任務 | 模糊點 | 後果 |
|------|--------|------|
| T-A4-001 照片分類 | 「分類完成」的標準從未定義 | ~246h 無 commit，不知道還剩多少 |
| T-A5-004 createSlides.gs | Owner 期待的 Slide 格式 vs 系統能產的 | ~1512h 無 commit，最長未動任務 |
| IOS-KOL Daily Digest | 哪些 KOL 算「完整」，逐字稿缺失時的 fallback | 多次 pitfall（最近 4 條都跟這有關） |
| T-A8-001 影音分發 | 「什麼樣的影片可以上傳」缺具體 rubric | 每次都要 Owner/A1 核准才能上 |
| T-A2-005 SEO Factory | SEO 文章數量/品質門檻未定 | ~912h 無 commit，阻塞在「WordPress 憑證」 |
| B1-B4 RSI baseline | score=44 是好是壞，沒有明確目標 | RSI 分數每次評估沒有改善指標 |

### 2.3 沒被記錄的狀態

| 狀態 | 未記錄在哪 | 影響 |
|------|----------|------|
| Investment OS runtime 實際 SQLite 狀態 | New project/ 本機，未推 GitHub | Mac mini 故障 = 所有 IOS 數據消失 |
| Hermes CLI 是否可用 | `hermes_status.json` 顯示 cli_path null | 每次呼叫都要重新確認 |
| OpenClaw CDP 狀態 | 不穩定，無永久 registry | A8/A2 依賴它但不知道當下是否可用 |
| LINE 雙向對話 | 只有客戶→OA 訊息進 Sheet | OA→客戶回應丟失，學習資料不完整 |
| Owner Chrome 登入態 | 無追蹤 | 每次需要登入態都要重新 bootstrap |
| GCP 帳單狀態 | CURRENT_STATUS blockers 提到 ~57天未處理 | 不知道服務是否正常 |
| 多個 launchd job 的最後執行時間 | 無統一 registry | T-HQ-001 發現殭屍 cron 才刪 |

### 2.4 低槓桿 / 情緒性、只是在忙沒推動複利

| 行為 | 為什麼是低槓桿 | 建議替換 |
|------|--------------|---------|
| 每次巡查重寫 Blockers 表格（144 行 blockers）  | 大量 patrol log 記錄已知問題，不解決 | 只記「狀態變了什麼」，不重複堆積已知 |
| 反覆警示 A4 CRITICAL（已持續 10.3 天） | 警示不等於推動，沒人接 | 明確指定地端模型自動跑 A4 pipeline |
| 20+ 個 OpenClaw 訓練 round（A6 報價） | 學徒訓練可以，但每輪要人在場 | 固定 gate 自動通過/失敗，不要每輪人工 |
| CURRENT_STATUS 累積 patrol log 成 200 行 blockers | 老 blockers 不清理，新的加在上面 | 超過 30 天未解決 = 移 archive 或關閉 |
| 每次 deploy 後驗證 Extension version 號 | 單一版本號驗證，不等於功能可用 | 加 smoke test：實際點召喚看 prompt 對不對 |

### 2.5 漂亮輸出但缺真實證據（eyes-on）

| 輸出 | 問題 |
|------|------|
| B-role RSI score=44 | 分數本身是地端模型自評，沒有外部 benchmark |
| IOS-KOL "digest sent" | Telegram 回報已送，但 Owner 截圖問「真的有嗎」才發現內容空洞 |
| OpenClaw "QA PASS" | Round 1/2 自評 PASS，supervisor 校正為 NEEDS_CORRECTION |
| "A8 local fallback 可用" | 只是 JSON storyboard，沒有 MP4 + ffprobe 驗證 |
| "A6 已召喚 A3" | 只是文字路由建議，沒有 dispatch receipt |
| "已 push 到 main" | AGENT_RULES 有強制存檔，但 ~232 個文件曾積壓 3 天才一次性 commit |

**Owner 真正需要什麼（first principles）：**
Owner 是一個人同時管一間外燴公司（MAPLAB）和一套投資研究系統（Investment OS）。他需要的不是「AI 在忙」，而是：

> **MAPLAB：** 業務報價 → 確認接案 → 素材到位 → SEO 引流 → 客戶回頭（一條能閉環的商業鏈）
> **Investment OS：** 每日研究 → 信號確認 → 模擬倉追蹤 → alpha 量化 → 優化信號品質（不下單，研究閉環）

現在系統最大問題不是「AI 不夠強」，而是**閉環沒接通**：
- MAPLAB：LINE→報價→Sheet 有接（A6 修好了），但 REVISION_LOG 空白，系統無法自學優化
- Investment OS：研究→信號→模擬倉有架構，但 Telegram digest 品質不穩，Owner 看不到有意義的 daily signal

---

## 三、Pro 訂閱自主運轉路線

### 3.1 目前哪些環節依賴高額度

| 環節 | 目前方式 | 高額度依賴原因 |
|------|---------|--------------|
| 冷啟動讀 CURRENT_STATUS | Claude Code session 讀全文 | 228 行 ~32k tokens，乘以每天 3 次巡查 = ~100k tokens/天 光這一個動作 |
| A1 patrol 每日三次 | Max session 逐筆分析 | 每次 patrol 讀多個 task card + CURRENT_STATUS |
| IOS-KOL digest 產出 | Claude 生成摘要 + 判讀 | 每集 transcript 可能數萬字 |
| A8 影音腳本生成 | Claude 長文產出 | 圖片轉影音要讀多張照片 + 寫腳本 |
| 多 agent 並行 session | 多個 Claude Code/tab 同時開 | Claude app 20GB RAM = 多 session 並行 |
| Extension handoff prompt | 每次召喚觸發一個完整 session | 每個角色召喚 = 一個新 session 冷啟動 |

**計算真相：**
- 目前 A1 每日 3 次巡查，每次讀 CURRENT_STATUS（32k）+ 所有 task cards（25 張 × 平均 2k ≈ 50k）+ AGENT_RULES（30k）= **每次巡查約 112k tokens 僅讀取**，一天 3 次 ≈ 336k 讀取 tokens
- Pro 計畫的 rate limit 約 80k tokens/hour，這意味著一次完整巡查可能超出 Pro 的承受範圍
- 解法不是「切 Pro 然後就撐過去」，而是「重新設計讓 Pro 夠用」

### 3.2 降到 Pro 可負擔的工程路線（分三階段）

---

#### Phase 1：脂肪砍掉，讓現有 session 更小（1-2 週）

**P1-A：CURRENT_STATUS 壓縮術**
- 問題：228 行 ~32k tokens，其中 144 行是 patrol log（已知的問題重複記錄）
- 做法：把 CURRENT_STATUS 拆成兩份
  - `CURRENT_STATUS.md`（保留，僅最新 30 行 = 「今天發生了什麼」）
  - `archive/CURRENT_STATUS_LOG.md`（自動 append 舊 patrol log）
  - 每次冷啟動只讀 30 行，需要歷史才讀 archive
- 預期效果：冷啟動讀取成本從 32k → 3k tokens（90% 降幅）
- 驗收：新 session 冷啟動後能在 5k tokens 內完成 Startup Check
- 負責：A1
- 注意：CURRENT_STATUS 已有 archive 慣例，只需建立自動 rotate 機制

**P1-B：只讀需要的 task card（不全讀）**
- 問題：patrol 讀所有 task card，其中 ~60% 是 CRITICAL/停滯 card，本輪根本不會動
- 做法：patrol.sh 加過濾邏輯：只讀「本週有 commit 或有 Owner action 的 task card」
- 預期效果：每次 patrol 讀取量從 50k → 15k tokens
- 驗收：patrol 輸出包含「跳過了哪些 card 及原因」
- 負責：A1

**P1-C：launchd patrol 改地端模型**
- 問題：patrol.sh 現在 trigger Claude Code，等於每次定時觸發一個付費 session
- 做法：patrol-scheduled.sh 改為先跑地端 `qwen2.5:14b` 做 task card 差異摘要，僅當「發現新異常」才推 Telegram 通知，讓 Owner 決定是否呼叫 Claude Code 深挖
- 預期效果：70% 的 patrol 觸發可由地端完成（只有確認異常的 30% 才上 Claude）
- 驗收：地端 patrol 輸出格式 = `{status: 'ok'|'alert', summary: string, trigger_claude: bool}`
- 負責：A1（改腳本）+ qwen2.5:14b（執行）

---

#### Phase 2：最小閉環接通（3-6 週）

「Pro 下自主運轉」需要的最小閉環：
```
對齊 → 派工 → 驗證 → commit → 交接 → 回報
```

目前缺哪幾塊：

| 閉環步驟 | 現況 | 缺少的 |
|---------|------|--------|
| 對齊（Owner 目標） | 需要 Owner 每次 session 說一遍 | **缺：** 固定 goal spec，機器可讀 |
| 派工 | Telegram → bot → dispatch packet（已修） | **缺：** 自動路由判斷（不靠人工） |
| 驗證 | 各自定義，不統一 | **缺：** 統一 output contract（每個 agent 產什麼格式）|
| commit | 手動，多人累積才一起 commit | **缺：** 觸發條件：任務結束即自動 commit |
| 交接 | handoff/tasks/ task card（人工維護） | **缺：** task card 自動從 commit diff 更新狀態 |
| 回報 | Telegram bot /status | ✅ 已接通，但需要地端模型加速 |

**P2-A：統一 Output Contract**
每個 agent 的輸出格式標準化，讓地端模型和雲端模型都能處理：
```json
{
  "agent": "A6",
  "task_id": "T-A6-001",
  "output_type": "quote",
  "status": "complete|partial|failed",
  "evidence": "workbook/reviews/JOB-A6-QUOTE-20260624/",
  "next_action": "owner_review|auto_proceed|escalate",
  "tokens_used": 1200
}
```
好處：地端模型只需解析 JSON，不需要理解全文。Claude 只在 `next_action=escalate` 時介入。

**P2-B：MAPLAB 業務閉環最小版**
目前 Phase 2 業務閉環（v6-architecture.md）缺 2.2-2.5 的測試資料。
最小可驗證改進：
1. Owner / 業務在 SALES_INTAKE 填 3 筆真實訂單（5 分鐘行動）
2. A6 自動讀取 → 產 QUOTE_WORKBENCH 報價 → 推 Telegram
3. 業務確認/修改後自動寫 REVISION_LOG（GAS trigger）
4. A1 每週讀 REVISION_LOG 差異 → 推薦 A5 品項調整

這 4 步就能讓報價系統開始「越用越準」，不需要更多 AI 基礎設施。

**P2-C：Investment OS 每日 digest 品質 gate**
目前 IOS-KOL digest 最大問題：逐字稿缺失時靜默 fallback 到舊資料。
修法：
1. 每日 digest pipeline 在 Telegram 發送前加 `gate_check()`
2. gate 規則：至少 1 個 KOL 有 transcript_status=ok，否則標「今日無新逐字稿，以下為 RSS 標題摘要」
3. 地端模型（qwen2.5:14b）做標題摘要，Claude 只做「多 KOL 共識判讀」（每週一次，不是每天）
4. 成本：每日 digest 從 Claude 生成 → 地端模型，節省 ~90%

---

#### Phase 3：重活外包，Owner 只看 dashboard（6-12 週）

**P3-A：把「重活」定義清楚**

| 任務類型 | 重活定義 | 外包給誰 |
|---------|---------|---------|
| 程式碼生成 | >500 行的功能開發 | Codex（GUI 貼入）|
| 大量圖片分類 | A4，~270h 積壓 | Gemini Flash API（已有 pipeline）|
| 長 transcript 摘要 | IOS-KOL，逐字稿全文 | Gemini 1.5 Pro（長 context 便宜）|
| A8 影音腳本 | 每支 15-30 秒影片腳本 | qwen2.5:14b 地端 |
| Telegram 初步路由 | 哪個 agent 該接 | 地端模型 + 規則 routing |
| WP 內容草稿 | A2 SEO 文章 | GPT（已是 A2 標準工具）|
| Meta Ads 受眾分析 | A3 廣告優化 | Gemini（Google 生態）|

**P3-B：可移植性 — 同一套 task card 讓任何 worker 接手**

目前 task card 格式已經夠好，但缺一個關鍵欄位：
```yaml
output_contract:
  type: "quote|seo_article|photo_alt|video_mp4"
  format: "json|markdown|file"
  validation: "sheet_readback|url_200|ffprobe_1080"
  worker_capable: ["claude", "codex", "qwen2.5", "gemini"]
```

加了這個欄位，A1 就能自動判斷「這個 task 可以丟地端模型嗎？」不需要人工決定。

**P3-C：Session 生命週期成本控制**

目前最浪費的地方：
1. 同名 session 重複開（已有規則但沒有強制）
2. Chrome tab 不關（已有規則但依靠自律）
3. 背景 session 沒有結束條件（新規則 2026-06-24 已補）

技術解法（不靠自律）：
- `com.maplab.session-watchdog.plist`：每小時掃 Claude app 的 RAM，超過 15GB 推 Telegram 通知
- `session_registry.jsonl`：每個 session 開始/結束自動 append（不依賴人工）
- Chrome Extension 加「清理」按鈕：點一下關掉所有 task-related tabs

---

### 3.3 Pro 自主運轉的最終架構願景

```
Owner 每天做的事（5 分鐘）：
  Telegram 看 morning brief（地端模型產）
  ↓ 有問題 → 回 Telegram 指令
  ↓ 沒問題 → 自動繼續

Claude Code（A1）做的事（每週 2-3 次，每次 30 分鐘）：
  看 patrol 發現的 alert
  核准 approval-ready plan（A2 SEO、A3 Ads）
  解 CRITICAL blockers（真正需要推理的）

地端模型（24/7 自動）：
  每日 patrol：掃 task card 狀態差異
  每日 IOS-KOL：RSS 摘要 + 標題 digest
  A4 照片：Gemini Flash API 批次分類
  A8 腳本：qwen2.5 草稿 → Claude 只做品質 gate

人類只介入：
  有新業務詢問（LINE）
  Owner 決策（新方向、高風險操作）
  系統 alert（真正異常，不是每次巡查）
```

---

## 四、20 個外部參照 — 每個的第二層思考

### 規則：為什麼這個對「你的系統」有意義，不可照搬什麼，最小可驗證改進是什麼

---

**1. CrewAI（multi-agent orchestration）**
- 為什麼吸引：你的 A0-A8 就是一個「crew」，已有角色分工
- 可學什麼：CrewAI 的 `Task` 物件有 `expected_output` 欄位——強制定義產出格式，不讓 agent 自己決定
- 不可照搬什麼：CrewAI 假設你在 Python 環境裡編排，你的系統是跨 Telegram/Extension/launchd 的 hybrid
- 最小落地改進：**把 `output_contract` 欄位加進 task card template**（已在 P3-B 建議中）

**2. LangGraph（stateful agent graphs，LangChain 出品）**
- 為什麼吸引：你的 patrol → alert → dispatch → execute → commit 就是一個 graph
- 可學什麼：LangGraph 的 `state` 概念：整個 workflow 共享一個 state dict，不靠 session 間傳話
- 不可照搬什麼：LangGraph 是 Python 庫，你的系統是多工具 + 多平台，不適合單一 Python 編排
- 最小落地改進：**`workbook/hermes/patrol/latest.json` 就是你的 state dict，讓所有 agent 讀同一個 JSON 而不是各自讀 CURRENT_STATUS**

**3. Letta / MemGPT（持久記憶 agent）**
- 為什麼吸引：你已有 `skills/session-handoff.md`、`AGENT_RECALL_PROMPTS.md`，在手動實作 MemGPT 的概念
- 可學什麼：Letta 的 in-context/archival/recall memory 三層分離。你的 CURRENT_STATUS（in-context）、GitHub history（archival）、task card（recall）已是同樣架構
- 不可照搬什麼：Letta 是 SaaS，有外部 API 依賴。你的系統要離線可跑
- 最小落地改進：**把 `CURRENT_STATUS.md` 拆成 `hot.md`（最近 7 天）+ `cold.md`（更早），agent 預設只讀 `hot.md`**——等同 Letta 的 in-context vs archival 分層

**4. AutoGen（Microsoft，multi-agent conversation）**
- 為什麼吸引：AutoGen 的 `ConversableAgent` 可以「agent 跟 agent 說話」，你的 A0↔A1 溝通協議是類似概念
- 可學什麼：AutoGen 有「終止條件」機制——對話 loop 必須定義何時停，不能無限跑
- 不可照搬什麼：AutoGen 的 cost control 機制不成熟，容易 runaway。你有 SECTION 19 無人長跑規則，比 AutoGen 的機制更嚴格
- 最小落地改進：**每個 Telegram dispatch receipt 加 `ttl_hours` 欄位，超過時間自動標 expired，不再被 patrol 計入「進行中」**

**5. Open Interpreter（自然語言控制本機）**
- 為什麼吸引：你的 A1 = Claude Code = 已經是 Open Interpreter 的 Claude 實作
- 可學什麼：OI 的 `safe_mode` 概念：危險操作前暫停等確認，你的 SECTION 19 已實作
- 不可照搬什麼：OI 假設單一 session 連續執行，你是多 session 跨天任務
- 最小落地改進：**在 `scripts/checkpoint.sh` 加入 pre-commit hook：若 diff 包含 `.env`、`secrets`、`production db` 路徑，自動暫停 + Telegram 警告**

**6. LiteLLM（統一 LLM API gateway）**
- 為什麼吸引：你已有三層備援（MCP/curl/截圖），LiteLLM 可以讓切換更乾淨
- 可學什麼：LiteLLM 的 `fallback` 機制：primary 失敗自動 fallback，不需要 if/else 寫死
- 不可照搬什麼：LiteLLM 增加一個中間層，引入新故障點，且你已有 credentials/ skill 系統
- 最小落地改進：**`bot_a6/a5_quote_engine.py` 的 model fallback 邏輯改為 config-driven，不要 hardcode model 名稱**

**7. Ollama + llama.cpp（地端模型服務）**
- 為什麼吸引：你已在跑 qwen2.5:14b + gemma4，這是最直接可用的基礎
- 可學什麼：Ollama 的 model keep-alive 設定：避免每次呼叫都重載模型（影響 RAM）
- 不可照搬什麼：地端模型無法替代 Claude 的長 context 推理和複雜任務
- 最小落地改進：**建立 `tools/local_model_router.py`：輸入 task type，輸出 `{model, endpoint, max_tokens}`，讓所有地端呼叫走同一個 router**

**8. Prefect（Python workflow orchestration）**
- 為什麼吸引：你的 launchd plist 就是 Prefect 的 cron trigger，但 Prefect 有 retry、依賴鏈、failure notification
- 可學什麼：Prefect 的 `flow.run_on_failure()` hook：任何排程任務失敗自動推通知
- 不可照搬什麼：Prefect 需要 server（雲端或本機），增加基礎設施複雜度
- 最小落地改進：**給每個 launchd plist 加一個 `StandardErrorPath`，patrol.sh 開頭讀 stderr log，若不為空就 Telegram 警報**

**9. n8n（low-code workflow automation）**
- 為什麼吸引：你的 LINE→GAS→Sheet 報價流程，正是 n8n 擅長的 webhook trigger + 多步驟自動化
- 可學什麼：n8n 的 visual workflow 可以讓 Owner 自己看到流程圖，不需要 agent 解釋
- 不可照搬什麼：n8n 增加外部依賴，且你已有 GAS（Apps Script）做到同樣的事
- 最小落地改進：**把 LINE→報價→Sheet 的流程畫成一頁 `docs/maplab-flow-diagram.md`（Mermaid），讓任何人接手都能理解**

**10. Haystack（RAG + agent，deepset）**
- 為什麼吸引：你的 skills/ 目錄 87+ 個文件 = 一個待建立的知識庫
- 可學什麼：Haystack 的 DocumentStore 可以讓 agent 「查技能書」而不是「讀技能書」——差別在於向量搜索 vs. 全讀
- 不可照搬什麼：RAG 系統需要 embedding + vector store，增加維護成本；你的技能書都是 Markdown，grep 已夠用
- 最小落地改進：**建立 `skills/INDEX.md`：每個技能書一行 `[觸發詞] → skills/xxx.md → 目的`，讓 agent 不需要讀全部技能書**（你的 CLAUDE.md 技能索引表已是這個概念，只需統一化）

**11. smolagents（HuggingFace，最小化 agent）**
- 為什麼吸引：smolagents 的核心是「agent 只有 3 個工具：code/search/answer」——極致簡化
- 可學什麼：最小 agent 的設計：每個 agent 有且只有它需要的工具，不帶多餘依賴
- 不可照搬什麼：smolagents 是研究展示用，production-grade 支援薄弱
- 最小落地改進：**審視每個 Chrome Extension task module JSON：工具清單只列「這個 agent 真正用得到的」，不要複製貼上全部**

**12. TaskWeaver（Microsoft，planning agent）**
- 為什麼吸引：TaskWeaver 把複雜任務分解成 planner → executor 兩層，避免 agent 自己決定執行策略
- 可學什麼：兩層架構：A1（planner）輸出執行計畫，地端模型（executor）照計畫跑，不讓 executor 有規劃權
- 不可照搬什麼：TaskWeaver 假設 Python Jupyter 環境，你的系統是 shell + Claude Code + GAS
- 最小落地改進：**A1 每次 patrol 後輸出 `handoff/patrol_plan.json`（計畫），由地端模型讀這個 JSON 執行，不讓地端模型自行決定要做什麼**

**13. Agno / Phi Data（輕量 agent framework）**
- 為什麼吸引：Agno 的設計原則：agent 應該輕、快、可組合，不要每個都是重量級 session
- 可學什麼：agent 可以是 `function + system_prompt + tool` 的組合，不需要完整 session
- 不可照搬什麼：Agno 是 Python-native，你的主要執行體是 Claude Code + bash
- 最小落地改進：**把 A4 照片分類從「召喚完整 Claude session」改為「地端 Gemini Flash API call + bash 寫結果」**——不需要一個 agent，只需要一個 cron job + API call

**14. Dify（LLM app builder，有 workflow 模式）**
- 為什麼吸引：Dify 的 workflow 模式可以把 LLM call、API call、判斷分支組成 DAG
- 可學什麼：Dify 的 workflow JSON export 格式：可以版本控制 workflow 定義
- 不可照搬什麼：Dify 需要 self-hosted server，對一台 Mac mini 是額外負擔
- 最小落地改進：**把 A6 報價 hot path 的流程畫成 `docs/a6-flow.mermaid`，工程化記錄每個判斷點**

**15. OpenHands / OpenDevin（code agent）**
- 為什麼吸引：OpenHands 可以自主寫程式碼、跑測試、修 bug，類似你希望 Codex 做的事
- 可學什麼：OpenHands 的 sandbox 機制：所有 code 在隔離環境跑，不影響本機
- 不可照搬什麼：OpenHands 資源消耗大，且你已有 Claude Code（更成熟）
- 最小落地改進：**對 CRITICAL 任務（T-A4-001、T-A5-004）試跑 Claude Code + git worktree 模式：任務在 worktree 跑，完成後 A1 審查再 merge**

**16. Hermes 模型（Nous Research）**
- 為什麼吸引：你的系統已有 Hermes runtime，而 Nous Research 的 Hermes 系列模型擅長 function calling
- 可學什麼：Hermes-3 支援 JSON function call schema，可以讓地端模型產 structured output
- 不可照搬什麼：需要確認你本機的 Hermes runtime 是同一個「Hermes」，還是你自己的 patrol 工具（名稱撞了但不同東西）
- 最小落地改進：**把 Ollama 的 `qwen2.5:14b` 換成 `nous-hermes-3-8b` 試跑 A6 structured output，看 function call 準確率是否更高**

**17. CAMEL（角色扮演 agent，KAUST）**
- 為什麼吸引：CAMEL 的 role-playing 概念：兩個 agent 互相對話完成任務，一個出題、一個解答
- 可學什麼：CAMEL 的 inception prompt 讓 agent 「記住自己的角色」，這正是你的 recall prompt 在做的
- 不可照搬什麼：CAMEL 的多輪對話需要兩個完整 session，成本高
- 最小落地改進：**A6 報價驗收改為「地端 qwen2.5 產 payload → A1 判斷 pass/fail」，而不是「agent 自評 PASS」**——已在 pitfalls 記錄，這是修法

**18. AutoGPT（經典但已過時）**
- 為什麼吸引：AutoGPT 展示了 agent 自主規劃 + 執行的可能，你的 V7 計畫方向類似
- 可學什麼：AutoGPT 最大的教訓：沒有 stop condition 的 autonomous agent 會無限迴圈花錢
- 不可照搬什麼：幾乎全部。AutoGPT 是示範，不是 production system
- 最小落地改進：**SECTION 19 無人長跑規則是你已有的 AutoGPT 教訓提煉，確保每個新 cron/background task 都有明確 stop condition 才啟動**

**19. Sweep AI（GitHub issue → code PR）**
- 為什麼吸引：Sweep 可以把「修一個 bug」的 GitHub issue 自動轉成 PR
- 可學什麼：issue → PR 的 spec 格式：必須有「預期行為」「實際行為」「測試方法」
- 不可照搬什麼：Sweep 針對有 CI/CD 的 GitHub repo，你的系統沒有 CI/CD
- 最小落地改進：**把 Sweep 的 issue 格式塞進你的 task card template：每張 card 必須有「預期行為」「驗收標準」「測試方法」**——你已有類似欄位，只需統一

**20. Flowise（visual LangChain，low-code）**
- 為什麼吸引：Flowise 可以用 drag-and-drop 建 LLM pipeline，讓非工程師也能改流程
- 可學什麼：visual pipeline 的好處：Owner 可以自己看到資料怎麼流，不依賴 agent 解釋
- 不可照搬什麼：Flowise 需要 Node.js server，且你的主要 bottleneck 不是「建 pipeline 太難」
- 最小落地改進：**用 `workbook/dashboards/` 已有的 HTML dashboard 加一頁「資料流圖」（靜態 SVG），讓 Owner 一眼看到 LINE→Sheet→Telegram 的流向**

---

## 五、建議下一步 3 件事

### #1 壓縮 CURRENT_STATUS，讓 Pro 的冷啟動可以負擔
**為什麼第一：** 現在每個 session 的啟動成本是 32k+ tokens，Pro 下這比率會讓 rate limit 很快見底。沒解決這個，其他優化都是在漏水的桶子裡加水。

**做什麼：**
1. 把 CURRENT_STATUS.md 的 patrol log（目前 144 行）移到 `archive/patrol-log-2026.md`
2. CURRENT_STATUS 只保留：系統版本、最新 3 條事實、當前任務表（無 blockers 詳情）、指向 archive 的連結
3. 在 `scripts/checkpoint.sh` 加一段：若 CURRENT_STATUS 超過 80 行，自動把最舊的 patrol log 移進 archive
4. 驗收：`wc -l CURRENT_STATUS.md` < 80

**負責：** A1（你）
**預計時間：** 30 分鐘
**驗收方式：** 新 session 從 CURRENT_STATUS 冷啟動，整個 Startup Check < 8k tokens

---

### #2 接通 MAPLAB 業務閉環：Owner 填 3 筆 SALES_INTAKE
**為什麼第二：** 整個 v6.0 的 Phase 2（業務閉環）被「等測試資料」卡了幾個月。技術端 A6/GAS 已修好，缺的只是人工輸入 3 筆真實訂單讓迴圈轉起來。這是 Owner 5 分鐘可以完成、但系統閉環需要的關鍵動作。

**做什麼：**
1. Owner 打開 MAPLAB_外燴系統_v0.1 Google Sheet → SALES_INTAKE 分頁
2. 填 3 筆過去 6 個月的真實接案（客戶可用代號，不需要真名）
3. A6 自動讀取 → 產 QUOTE_WORKBENCH 報價
4. A1 確認後推 Telegram 回報「閉環已通」

**負責：** Owner（填資料）→ A6 自動跑 → A1 驗收
**預計時間：** Owner 5 分鐘，A6 自動 10 分鐘
**驗收方式：** QUOTE_WORKBENCH 有 3 筆報價，REVISION_LOG 有 1 筆（業務確認/修改後自動寫入）

---

### #3 建立地端 patrol 路線，讓 Claude Code 不用每天巡查三次
**為什麼第三：** 目前每日 3 次 patrol 是 Pro 計畫的主要 token 消耗者，且大部分時候「沒發現新問題」。讓地端模型做差異掃描，Claude 只在真正有新 alert 時介入，是實現「Pro 下自主運轉」的核心工程。

**做什麼：**
1. 在 `scripts/patrol-scheduled.sh` 加地端 patrol 模式：
   - 讀 `handoff/tasks/` 目錄的 last-modified 時間
   - 跟 24 小時前比較，只輸出「有改變的 task」
   - 如果 0 個改變：Telegram 推「patrol OK，無新異常」，不啟動 Claude
   - 如果有改變：Telegram 推摘要 + 「要深入看嗎？」，Owner 回覆才啟動 Claude
2. 地端 patrol 用 `qwen2.5:14b` 做差異摘要（JSON input → plain text summary）
3. 驗收：連續 3 天地端 patrol 成功運行，至少 1 天 Claude Code 沒被觸發

**負責：** A1（寫腳本）+ qwen2.5:14b（執行）
**預計時間：** A1 1 小時寫腳本，之後自動運行
**驗收方式：** `launchd list | grep patrol` 有 active，連續 3 天 Telegram 有 patrol OK 推送

---

## 六、附錄：完整任務健康度快照（2026-06-24）

### CRITICAL（超過 48h 無 commit）

| Task ID | 任務 | 無 commit 時間 | 根因 | 建議 |
|---------|------|--------------|------|------|
| T-A5-004 | createSlides.gs | ~1512h（63天） | 無明確 owner，需 GAS 知識 | 外包 Codex |
| T-A5-005 | 報價狀態追蹤 | ~1535h（64天） | 前置 T-A5-002 blocked | 先解 002 |
| T-A1-V6-P2 | V6 Phase 2 | ~1272h（53天） | 等真實測試資料 | Owner 填 SALES_INTAKE（#2）|
| T-A1-V7 | 系統進化 V7 | ~1272h（53天） | 巨大任務，無分解 | 本文就是 V7 的分解 |
| T-A2-005 | SEO Factory | ~912h（38天） | 等 WP 憑證 + 測試站 | 移低優先（A2 已有 ICCTN active）|
| T-A2A3-001-B | SEO + 內連結 | ~360h（15天） | 等 Chrome ext file access | Owner 開 file URL access 權限 |
| T-A4-001 | 照片分類 | ~246h（10天） | 無 active worker | 地端 Gemini Flash API 自動跑 |
| T-HQ-001 P5/P6 | AGENT-HQ | ~243h（10天） | B1 需要繼續 | 召喚 B1 補 P5（data-policy）|

### Active（近 48h 有活動）

| Task ID | 任務 | 最後活動 | 下一步 |
|---------|------|---------|--------|
| T-A8-001 | 影音分發 | 2026-06-22 | 審核 local motion storyboard |
| T-A6-001 | LINE 報價助手 | 2026-06-18 | LINE 訓練資料來源 |
| T-IOS-KOL-001 | KOL 雷達 | 2026-06-21 | 英文 KOL + 總經資料補齊 |
| T-A2-006 | Ads/SEO/WP Patrol | 2026-06-16 | 週巡查持續 |
| T-A1-EXT-001 | Extension 動態模組 | 本 session | Task Card 同步中 |

---

*本文件為 read-only 研究產出。不修改任何其他 repo 檔案。*
*下一步由 Owner 選擇優先順序後，由 A1 建立對應 task card 執行。*
