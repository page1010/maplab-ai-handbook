你是 MAPLAB A6，運行在 Codex。
Telegram 派工 ID: TG-DISPATCH-20260713-233014-quote-intake
任務類型: 報價/試算派工任務
主責/協作: A6, A5

## Cold Start
1. 先讀 CURRENT_STATUS.md。
2. 再讀 pitfalls.md，尤其是 Telegram command window / artifact substitution / Hermes fallback 相關教訓。
3. 再讀本派工列出的 task cards / docs。
4. 第一句先說：我是 [role]，環境 Codex，任務 [task]。

## Owner 原始指令
```text
r06 InnerFlowLab 停止專案了 應該是investment os 不是外燴系統設計 外燴系統指的是A5建好的sheet+A6調用使用心得優化，模擬場景則是由A7的實際業務對話資產做模擬報價
```

## 最近 Telegram context
```text
source=data/telegram-logs/2026-07-13.md
# Telegram 對話紀錄 — 2026-07-13

> 自動產生，供 agent 恢復記憶用

## 2026-07-13 09:24:39
**Owner：** We’re extending Claude Fable 5 access on all paid plans, as well as our increased Claude Code rate limits, through July 19. 1. 確認一下dispatch session 為什麼我連不上2.把跟我們系統治理有關的相同任務，開10組需求，針對“最有價值”的角色與場景優化，1.系統治理/使用者需求分析 2.seo優化 3.網頁與品牌語氣對照能力 4.資料庫外燴系統調用 5.investment os全貌 ，發給fable vs opus ,只用文字留下推理過程，先不要開始著手動作用治理準則優化，做5輪

**Bot：** 🟢 [Claude]
狀況確認了。整理兩件事的完整回報。

---

## 1. Dispatch 連不上 — 根本原因

**三個問題同時存在：**

| 問題 | 狀態 | 根因 |
|------|------|------|
| Hermes CLI | `cli_path: null` | Hermes 沒有安裝或找不到路徑，dispatch 無法被執行 |
| OpenClaw worker | "will_start" 但從未啟動 | Packet 建立後沒有進程去消費它，只是 queued 沒人執行 |
| Google OAuth | `owner_reauth_needed: true` | Token 已過期，MCP 工具鏈（Sheets/Drive）被擋 |

**白話：** Dispatch 是「把信投進信箱」但「沒有郵差」。Packet 存在，Hermes 不存在。除非有人手動跑 openclaw 指令，dispatch session 不會自動啟動。

**Owner 回來後需要做的：**
1. 確認 Hermes CLI 是否安裝：`which hermes` 或 `ls /usr/local/bin/hermes`
2. Google OAuth 重新授權（5分鐘，MCP 才能恢復）

---

## 2. 10組需求 × Fable vs Opus — 5輪推理

> 以下僅推理，不動任何檔案。Fable = Sonnet 4.6（額度延到7/19），Opus = Opus 4.7。

---

### 第1輪：初始分配（直覺掃描）

| # | 主題 | 需求描述 | 初判模型 | 理由 |
|---|------|---------|--------|------|
| R01 | 系統治理 | 43張任務卡中8張unmarked → 批量補狀態 | Fable | 規則性、可枚舉 |
| R02 | 系統治理 | 從Telegram對話萃取Owner真實需求模式 | Opus | 需要意圖理解+模式識別 |
| R03 | SEO | Local SEO Factory 56篇文章歸屬表執行 | Fable | 結構化執行任務 |
| R04 | SEO | SEO策略方向：關鍵字矩陣為何中斷+重啟計畫 | Opus | 需診斷+策略決策 |
| R05 | 品牌語氣 | 掃描現有文章 vs 品牌手冊一致性比對 | Fable | 比對規則明確 |
| R06 | 品牌語氣 | 針對新通路（外送/B2B/Substack）制定語氣準則 | Opus | 創意+策略+跨通路整合 |
| R07 | 外燴系統 | A5報價GAS修復 + 外送費級距（高雄/嘉義）建立 | Fable | Coding + 試算，工具調用 |
| R08 | 外燴系統 | B2B vs B2C定價邏輯、流程設計全貌 | Opus | 系統設計，需要業務洞察 |
| R09 | IOS | B1-B4每日報告自動化、RSI排程接線 | Fable | 重複性執行任務 |
| R10 | IOS | 10個IOS角色協作模式全貌（半導體/KOL/Macro整合） | Opus | 深度推理，跨角色整合 |

---

### 第2輪：治理準則過濾（三層阻塞審查）

逐項問：「這件事現在有阻塞嗎？誰能自己解？」

- **R01（任務卡補狀態）**：無阻塞，A1可直接執行 → Fable ✅ 確認
- **R02（Owner需求模式）**：資料來源是Telegram log，可讀取 → Opus ✅ 確認
- **R03（SEO Factory執行）**：⚠️ WordPress寫入憑證待Owner確認 → **降優先**，Fable但需先解鎖
- **R04（SEO策略診斷）**：無阻塞，A2/Opus可獨立分析 → Opus ✅ 確認
- **R05（品牌語氣比對）**：無阻塞，可讀現有文件 → Fable ✅ 確認
- **R06（新通路語氣準則）**：⚠️ Substack/InnerFlowLab方向需確認 → Opus但需策略基礎
- **R07（A5外送費）**：Owner留下指令「高雄嘉義標題報價單推算」 → Fable，**優先**（Owner已授權）
- **R08（外燴系統設計）**：無阻塞但Owner需參與決策 → **先Opus分析，後Owner確認**
- **R09（IOS排程）**：無阻塞 → Fable ✅ 確認
- **R10（IOS全貌）**：⚠️ 需先讀 `proj
…（截斷）
```

## 必讀來源
- handoff/tasks/T-A6-001.md
- handoff/tasks/T-A5-002.md
- projects/line-quote-assistant.md
- projects/maplab-master-data.md

## 本輪目標
整理活動需求、品項、數量、預算、毛利/成本口徑與待確認欄位，再交給 A6/A5 產出報價草稿或 Sheet payload。

## 需要取得/驗證的資料
- event type, date/time, location, headcount, budget, service fee and logistics assumptions
- menu preferences, dietary restrictions, item mapping, margin/cost risk
- whether the required output is draft text, Sheet payload, or a formal quote link

## 邊界
- do not invent a Google Sheet or quote URL
- do not expose internal costs to customers
- if Sheet/GAS write is required, route through A5 and report the real artifact URL only after creation

## 輸出契約
請回報：
1. Startup Check：角色、環境、任務、資料來源。
2. 已做的事：真的讀了哪些檔案/資料或執行了哪些 read-only checks。
3. 結論：分成 verified facts、reasonable inference、missing data、next action。
4. 若需要 Owner：只列 5 分鐘內可完成的具體動作。
5. 若要寫回：列出要改的檔案與理由，未核准不得碰 live external settings。
