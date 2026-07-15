# A0 委派任務總回報 — 2026-07-10

**委派方：** A0 系統總管（GUI session 卡 AskUserQuestion >1天）  
**執行方：** A1 系統總管（Claude Code terminal）  
**完成時間：** 2026-07-10  
**Git commit 範圍：** 本次 session 所有 commit（詳見 git log）

---

## 執行結果摘要

### ① 規範注入：superpowers 強制條款補注入 A0 ✅

- **問題：** A0 recall prompt 缺少 `⚠️ 每次 recall 必讀 skills/superpowers-guide.md` 規範（其他 14 個 agent 已有）
- **修正：** `AGENT_RECALL_PROMPTS.md` A0 段落補入強制條款
- **狀態：** ✅ 完成。所有 agent（A0–A8、B1–B4、WIN、Codex、Antigravity）均已注入

---

### ② T-A4-001 七連警告解除 / patrol 誤報清理 ✅

- **問題：** T-A4-001 S11(2024) 已於 2026-07-08 完成（07-09 A0 驗收），但 CURRENT_STATUS.md 和 AGENT_RECALL_PROMPTS.md 仍顯示 CRITICAL 七連警告
- **修正：**
  - `CURRENT_STATUS.md` 2026-07-10 patrol 說明更新為「七連警告已解除，GBP 照片評分 🔓 解鎖」
  - `AGENT_RECALL_PROMPTS.md` A4 段落狀態更新為「✅ T-A4-001 S11(2024) 完成」
- **Patrol 對齊：** patrol.sh 讀 Task Card `- **狀態**` 欄位，T-A4-001 卡已標 ✅，未來巡檢不再警告
- **狀態：** ✅ 完成。T-A4-003/004 和 GCP帳單仍為 🔴 CRITICAL，已保留在 A4 recall。

---

### ③ Codex 通路驗證 ✅

- **測試：** `codex exec --ephemeral -s read-only` 直接 CLI vs「經 A6 route」
- **結果：** 兩條通路均使用相同本機 codex CLI，A6 route 不額外提升功能（只有 prompt 包裝差異）
- **修正：** `skills/codex-offload-guide.md` 移除無效 `-m gpt-5.1-codex` 旗標，新增 §八「兩條召喚通路實測對比」
- **狀態：** ✅ 完成。Codex 呼叫通路已釐清並更新技能書。

---

### ④ 技能複利收尾：Loop-02/15/17 基線確認 ✅

| Loop | 狀態 | 備注 |
|------|------|------|
| Loop-15 SOP 漂移 | ✅ 可跑 | 腳本正常；基線依現有 Task Cards 狀態 |
| Loop-02 頁面品質 | ⚠️ 部分可跑 | 腳本可執行但 GSC MCP 需 service account 憑證（非 OAuth），GSC 連線暫 block |
| Loop-17 KPI 異常 | ✅ 可跑（觀察期） | 2026 YTD 6 筆訂單已錄入；需累積 7 天後計算滾動基線 |

- **狀態：** ✅ 完成。Loop-17 基線已建立（`state/loop_17_kpi_daily.json`）。Loop-02 依賴 GSC service account，已記錄為技術債。

---

### ⑤ GBP 照片評分（A4 item 7） ✅

**執行詳情：** `workbook/reviews/JOB-A4-GBP-PHOTO-20260710/REVIEW.md`

| 目標夾 | 照片數 | 結果 |
|--------|--------|------|
| 0702中興工程 | 0 | Drive 未同步，跳過 |
| 20260627東門教會證婚 | 0 | Drive 未同步，跳過 |
| 0621歡樂時光-性別派對 | 20 | ✅ 11 張成功，最高 8/10 |
| 20260621說事實木地板開幕 | 17 | ✅ 15 張成功，最高 8/10 |
| 20260614富信飯店-社工公會會議 | 9 | ✅ 6 張成功，最高 8/10 |
| 20260613遊艇氣泡水 | 10 | ✅ 5 張成功 |

**Top 5 WP1992 企業茶會精選：**

| 優先 | 檔名 | 夾名 | 分數 | Drive 連結 |
|------|------|------|------|-----------|
| ★★★ | IMG_1396.HEIC | 20260614富信飯店-社工公會會議 | 8/10 | https://drive.google.com/file/d/1ahWLEgEY8CkXkDNmA2USz4rzRv0CzYfv/view |
| ★★★ | IMG_1400.HEIC | 20260621說事實木地板開幕 | 8/10 | https://drive.google.com/file/d/1AbixvFOYJzFYEKH70YHKpiTT6Fq2_2U-/view |
| ★★ | IMG_1408.HEIC | 20260621說事實木地板開幕 | 8/10 | https://drive.google.com/file/d/1QIszV1OrQwLaaD2qCB8_-uvZpjHb-jnZ/view |
| ★★ | IMG_1411.HEIC | 20260621說事實木地板開幕 | 8/10 | https://drive.google.com/file/d/1vI0gEKUcZcVcuG_dsWCTsyvOcaBhtXHe/view |
| ★★ | IMG_1413.HEIC | 20260621說事實木地板開幕 | 8/10 | https://drive.google.com/file/d/1aNt8U47JaNj80TwmMJliW6c9kuxC30zA/view |

**技術備注：**
- gemma4:latest **有**視覺編碼器（`mmproj` 已掛載，曾多次拿到準確描述），真正問題是本機 `llama-server` 多模態呼叫間歇性退化成空輸出，與 prompt/圖片內容無關，疑似 GPU/Neural Engine 資源競爭（`mediaanalysisd` 佔用 100%+ CPU 時觀察到）；moondream+qwen2.5 兩步驟繞開此問題但非「gemma4 沒有視覺能力」的定論。詳見 `pitfalls.md` 2026-07-10 條目。
- sips `--resampleLongSide` → 修正為 `--resampleHeightWidthMax`
- Drive 分享連結已補齊（見上表）：用本機 Google Drive for Desktop 的 `com.google.drivefs.item-id#S` extended attribute 取得真實 file ID，不需 Drive API/MCP 存取權限（`xattr -p "com.google.drivefs.item-id#S" <本機路徑>`）

---

## 待辦（Owner 確認後執行）

1. ~~Drive 分享連結~~ ✅ 已補齊（見上表，改用本機 xattr 方法，不需等 MCP 修復）
2. **未同步夾補跑：** `0702中興工程` + `20260627東門教會證婚` 本機掛載目錄確認為 0 個檔案（非只是「未同步」——若 Drive 端確實有照片，需 Owner 檢查該資料夾的 Drive for Desktop 同步設定；若 Drive 端也是空的，代表尚未上傳）
3. **GSC service account：** Loop-02 需補 GSC service account JSON key（非 OAuth client），步驟：① GCP 建 Service Account 並開通 Search Console API ② search.google.com/search-console 把該 email 加為 maplab.com.tw 使用者 ③ 下載 key 存 `~/.claude/mcp-keys/` 並更新 `~/.claude/.mcp.json` 的 `GOOGLE_APPLICATION_CREDENTIALS`
4. **T-A4-003/004：** 720h+ 無 commit，需 Owner 確認優先順序

---

## 文件索引

| 文件 | 路徑 |
|------|------|
| 評分原始 JSON | `workbook/reviews/JOB-A4-GBP-PHOTO-20260710/gbp_scores_raw.json` |
| 評分報告 | `workbook/reviews/JOB-A4-GBP-PHOTO-20260710/REVIEW.md` |
| 評分腳本 | `scripts/gbp_photo_scorer.py` |
| Loop-17 基線 | `state/loop_17_kpi_daily.json` |
| Codex 指南 | `skills/codex-offload-guide.md` |
| A4 Task Card | `handoff/tasks/T-A4-001.md` |

---

# A0 委派任務總回報（第二批）— 2026-07-10 付費 subagent + 複利治理修補

**委派方：** A0（派工時間：2026-07-10）  
**執行方：** A1 系統總管（Claude Code terminal）  
**完成時間：** 2026-07-10  
**Git commit 範圍：** a28c0a1（治理修補）、5626656（JOB 落檔）

---

## Item 1：治理修補 ✅

### 1a. `skills/codex-offload-guide.md` 強制落檔條款

版本從 v1.0 升到 v1.1，在技能書頂端插入：

```
## ⛔ 強制落檔規則（違反即為治理錯誤，2026-07-10 Owner 核准）
所有 Codex / Antigravity 呼叫的輸出必須落檔，禁止用完即丟。
- 輸出目錄：workbook/reviews/JOB-<TOOL>-<SLUG>-<YYYYMMDD>/
- 每個 JOB 至少包含：output.md + README.md
- 沒有落檔 = 沒有複利
```

### 1b. `scripts/weekly_eval_compounding.py` 掃描範圍擴展

`CODEX_MAKER_PROMPT` 完成條件 #1 改為掃兩個目錄：

- `workbook/outputs/seo-gap-drafts/`（原有）
- `workbook/reviews/`（新增，僅掃 output.md 和 draft*.md）

### 1c. `TASK_QUEUE.md` 補記本輪分派

新增 4 個 JOB 條目，狀態全標 ✅ 落檔。

---

## Item 2：Codex 分發（直接 CLI，輸出全落檔）✅

### 2a. 婚禮 pillar 終稿潤飾

**輸出：** `workbook/reviews/JOB-CODEX-WEDDING-PILLAR-20260710/`  
**模型：** gpt-5.5（codex-cli 0.142.0）  
**品牌語音核查：** 6 項全通過（無禁用字詞、無把話說死、無說服式句型、場景先行）  
**產出物：**
- Draft A：開頭段落終稿（台南午後光線切入、外燴細節導向）
- Draft B：婚禮群組五篇子頁內鏈錨文字範本

### 2b. B3 廣告素材文案初稿（Week1 企業茶會冷層）

**輸出：** `workbook/reviews/JOB-CODEX-B3-ADCOPY-20260710/`  
**受眾：** cold-b-meeting-corp（Week1 100% corp）  
**日預算：** NT$100 | 試跑 3-4 週  
**落地頁：** corporate-tea-party-desserts/  
**三組文案：**

| 組 | 差異化切入點 | 測試順序 |
|---|---|---|
| A | HR/行政窗口視角 | 1st |
| B | 外賓接待現場秩序 | 2nd |
| C | 活動後主管回報角度 | 3rd |

**溫層條件（三人小組定案）：** 落地頁停留 > 15s 或觀看影片 > 15s，Day 1 即建立。

**狀態：** ⏳ 待 A3/Owner 核准後在 Meta Ads Manager 建立廣告

### 2c. 57 篇舊文內鏈 + 語氣批量分析（唯讀）

**輸出：** `workbook/reviews/JOB-CODEX-CONTENT-AUDIT-20260710/`  
**tokens 消耗：** ~145,800  
**主要發現：**

**內鏈機會 Top 3（雙向閉環優先）：**
1. `tainan-outdoor-wedding-catering` ↔ `tainan-wedding-catering-cost`（婚禮 pillar/費用雙向）
2. `corporate-tea-party-desserts` ↔ `corporate-tea-party-catering-tips`（企業茶點雙向）
3. `catering-one-year-old-party-tainan` ↔ `gender-reveal-party-tips`（週歲 pillar/性別派對雙向）

**語氣複查 Top 1（最高優先）：** post 698 `tainan-custom-catering-menu` 食安紅線（「無麩質」）：
- 正文 + JSON-LD FAQ schema 兩處均需手動改為「素食或特殊飲食需求」等中性表述
- 這個問題若不修正，未來 seo_publish_gate.py F-1 gate 可能產生漏報

**系統性觀察：**
- 雙向內鏈閉環是當前最高優先（不是再新增文章）
- 2026-03 矩陣頁是語氣最大風險（低圖、低內鏈、AI 腔但掛「案例」分類）

**狀態：** ⏳ 所有建議需 A2/Owner 核准後才可實際修改 WordPress 文章

---

## Item 3：Antigravity 分發（二讀覆核，唯讀）✅

**輸出：** `workbook/reviews/JOB-AGY-SECOND-READ-20260710/`  
**模型：** Antigravity（Gemini）  
**覆核對象：** JOB-A2-SEO-TRIO-REVIEW-20260707 + JOB-B1-INVESTOS-TRIO-REVIEW-20260707

**SEO 矩陣覆核 — 5 大盲點：**
1. B2B 轉化週期估算過短（3-4 週）
2. 廣告每日預算上限欄位留白（需補確認值）
3. 地區性關鍵字 slug 稀釋風險（台南婚禮外燴 + 性別派對共用 pillar）
4. 遊艇廣告落地頁不對稱跳轉（Relevance Score 下降）
5. 溫層受眾觸發條件未定義（冷→溫轉換規則空白）

**Investment OS 覆核 — 最高優先行動：**
- `investment_goals.md` 格式解析安全機制（Schema Validation）→ 應在 CI/CD 或 Nightwatch 執行前加 Linter
- 世界觀/終局層應前置於 Pilot 之前（否則 Pilot 數據需大幅重構）

**agy 結論：** IS Schema Validation 最需立即啟動

**狀態：** ⏳ 所有行動建議需 Owner/A1 核准後執行

---

## Item 4：weekly_eval_compounding 掃描範圍驗證 ✅

**驗證方式：** Python 模擬掃描（不跑完整 Codex eval，避免額外 token 費用）

**驗證結果：**
```
SEO gap drafts: 7 files
workbook/reviews output/draft*.md: 48 files total（含今日 4 個 JOB）

今日新落檔驗證：
  ✅ workbook/reviews/JOB-CODEX-WEDDING-PILLAR-20260710/output.md
  ✅ workbook/reviews/JOB-CODEX-B3-ADCOPY-20260710/output.md
  ✅ workbook/reviews/JOB-CODEX-CONTENT-AUDIT-20260710/output.md
  ✅ workbook/reviews/JOB-AGY-SECOND-READ-20260710/output.md

Total scan scope: 55 files（4/4 新 JOB 全在掃描範圍內）
```

**CODEX_MAKER_PROMPT 更新確認：** `workbook/reviews/` 已正確加入完成條件 #1，
過濾規則（只掃 output.md 和 draft*.md，跳過 README / validation_report / supervisor_lesson）已生效。

**工程補充說明（A5-QUOTE 邊緣案例）：** `workbook/reviews/` 含大量 A5-QUOTE 報價草稿（draft.md），
跑 seo_publish_gate.py 對這類檔案會產生大量 FAIL（非 SEO 文章，不適用 gate 規則）。
建議未來在 CODEX_MAKER_PROMPT 中加入「A5-QUOTE 子目錄跳過」條件，或讓 Codex 自判分類後選擇性跑 gate。
**本輪不阻塞**，記錄為 backlog。

---

## Item 5：commits + checkpoint ✅

| commit | 內容 |
|--------|------|
| a28c0a1 | 治理修補：codex-offload-guide 強制落檔條款 + weekly_eval_compounding 掃描擴展 + TASK_QUEUE 記錄 |
| 5626656 | A0 委派分發落檔：4 個 JOB 全部落檔至 workbook/reviews/ |
| (本次) | 總報告完成 + checkpoint --notify |

---

## Owner 需決策事項

| 序號 | 事項 | 優先度 | 背景 |
|------|------|--------|------|
| 1 | B3 廣告文案（A/B/C 三組）上線核准 | **高** | 待 A3 在 Meta Ads Manager 建立廣告組 |
| 2 | 婚禮 pillar WP 文章套用終稿 | **高** | Draft A/B 已產出，需 A2 實際更新 WP post 1215 |
| 3 | post 698 食安紅線（「無麩質」）手動修正 | **高** | 正文 + JSON-LD 兩處，seo_publish_gate F-1 風險 |
| 4 | SEO 矩陣：B3 廣告每日預算上限確認值 | **高** | 建議 NT$100/天，總上限 NT$3,000-4,000（4週） |
| 5 | Investment OS：`investment_goals.md` 加 JSON Schema Validator | **中** | 防解析崩潰，CI/CD 前置 Linter |
| 6 | 57 篇內鏈 Top 10 實際修改授權 | **中** | 建議由 A2 分批執行（先雙向婚禮群組） |
| 7 | `weekly_eval_compounding` 正式跑一輪（跑 Codex eval） | **低** | 驗證 Codex 是否能正確掃 workbook/reviews/ 並產 digest |


---

## Item 4 補充：weekly_eval_compounding 實際跑完結果（背景任務完成）

**實際執行結果（非模擬）：**
- exit code: 0 ✅
- digest 落地：`workbook/outputs/eval-digests/2026-07-10.md` ✅
- baseline 更新：`state/eval_baseline.json` ✅
- CURRENT_STATUS.md 已追加 weekly-eval 行 ✅

**掃描結果：**
- SEO gap drafts: 7 files
- workbook/reviews output/draft*.md: 48 files（含今日 4 個 JOB）
- PASS: 476 / 495（不含 SKIP）
- SKIP-WP: 55（C1 需 WP credentials，依規格跳過）
- DELTA: **[NO_DELTA]** — 無 regression、無 NEW_PASS（首次跑 baseline 建立完成）

**今日 4 個 JOB output.md 掃描確認：**

| JOB | 結果 | 備注 |
|-----|------|------|
| JOB-CODEX-WEDDING-PILLAR-20260710 | ✅ 全 PASS（E1/E2/E3/B1/B2/B3 全過） | 品牌語音完全符合 |
| JOB-CODEX-B3-ADCOPY-20260710 | ✅ 全 PASS | 廣告文案符合 gate 規則 |
| JOB-CODEX-CONTENT-AUDIT-20260710 | ⚠️ E1/E2/E3 FAIL（false positive） | 因 audit 文件本身**引用**禁用詞作為警告範例，gate 誤判為踩線。非真實違規，已識別為 false positive。 |
| JOB-AGY-SECOND-READ-20260710 | ✅ 全 PASS | 覆核報告符合 gate 規則 |

**false positive 處理建議（backlog，本輪不阻塞）：**
審計型 output.md（如 CONTENT-AUDIT）引用禁用詞是設計行為，非違規。建議未來在 CODEX_MAKER_PROMPT 的完成條件中加入「JOB-*-CONTENT-AUDIT 類型跳過 E1/E2/E3，或加 `<!-- gate-skip: E1 E2 E3 reason=audit-quotes -->` 標頭」豁免機制。


---

## A0 委派第二批（2026-07-10 下午）— A1 執行回報

**執行時間：** 2026-07-10 14:30–15:10  
**委派原因：** A0 自主派工（複利迴圈 — 回報後自己修理）

---

### 任務一：nightwatch Investment OS 守夜人修復

**問題（根因更正）：**
- nightwatch 從未真正停擺。「06-02 停擺」是 TCC 阻擋 `cross-project-mirror` → repo 副本凍結在 06-02 → 07-07 三人小組審查時誤讀為停擺。
- 真正的問題：nightwatch CHECKS 使用 `reports/shadow/*` glob，會找到最新的 `local_model_findings.jsonl`（每日更新），從而掩蓋 `shadow_findings.jsonl`（06-02 後停供）失鮮的盲區。
- `shadow_findings.jsonl` 停供根因：convergence-engine 的 Hermes reviewer 自 06-02 開始持續失敗（`ValueError: no JSON object in reviewer response`），寫入中斷。

**修復：**
1. `investment-os/scripts/system_nightwatch.py`（repo + runtime 同步）：
   - 移除 glob `reports/shadow/*`
   - 新增 `影子教練巡查 shadow_findings.jsonl`（file, 48h 上限）
   - 新增 `本地模型影子 local_model_findings.jsonl`（file, 72h 上限）
2. 實測：手動跑一輪，結果 `1 alert — shadow_findings.jsonl 921h 前(上限 48h)` ✅ 正確偵測
3. `maplab-ai-handbook/scripts/patrol.sh`：新增「投資 OS 守夜人」自健檢區塊（防 nightwatch 自身死掉無人知）
4. `projects/investment-os-functional-audit-2026-07-07.md` Phase 0 欄位更新為 ✅ 完成

**待解（不在本批範圍）：** shadow_findings.jsonl 供料停止需修 Hermes reviewer，另建任務。

**證據：** 今日 nightwatch 報告 `nightwatch_2026-07-10.md` 第二版：`1 alert`；patrol.sh 測試輸出：`🔴 nightwatch 今日有警示：影子教練巡查 shadow_findings.jsonl：921h 前`。

---

### 任務二：影子系統專責角色

**搜索結論：**
- MAPLAB `AGENT_RULES.md` 角色表中無任何角色專責「能力蒸餾」或 recall prompt 品質維護
- `B2` 是 Investment OS Reviewer（IS 專屬），不涵蓋 MAPLAB 域
- 現有能力蒸餾機制：`skills/auto/`（幾乎空）、`pitfalls.md`（190+ 條但 0 封坑驗證）、`weekly_eval_compounding.py`（gate-eval 迴歸，非蒸餾）

**新角色章程：**
- 新建 `projects/b5-shadow-capability-distillation.md`（**待 Owner 核准**）
- 角色名：**B5 — 影子系統總管（Shadow System & Capability Distillation Manager）**
- 三項職責：① 全體 recall prompt 版本與品質管理 ② 複利輸出能力盤點（蒸餾評分 1-5）③ 每月打包「地端模型教材包」（recall prompts + top JOB 輸出 + eval 案例 + pitfalls 蒸餾版）
- 設計原則：雲端高智能 Claude 累積知識 → B5 固態化 → Ollama 地端模型低成本繼承
- 狀態：草稿，**等 Owner 一句話：「B5 角色通過，A1 建立配套文件」即可執行**

**附帶修復：Telegram bot A1 召回注入**
- `bot/bot.py` 新增 `_build_system_prompt()` 函式，啟動時讀 `AGENT_RECALL_PROMPTS.md` 的 A1 code block（截至阻塞審查規則，共 23 行）+ CURRENT_STATUS.md 最新 3 條事實
- 實測：bot 重啟（14:54:39 `Starting MAPLAB A1 遠端終端`），啟動 log 無 recall 載入錯誤，`Bot running` 確認 ✅

---

---

### ⑦ convergence-engine Hermes reviewer 修復 + shadow_findings.jsonl 供料恢復 ✅

**問題：** shadow_findings.jsonl 自 2026-06-02 停供（921h/38天）。nightwatch 今日修好後正確報 1 alert。

**根因（A0 診斷已接近正確，實際差一層）：**
- A0 說「根因 = Hermes reviewer ValueError」— 部分正確：reviewer 的 ValueError 確實在 Jun 1 首次出現，但 ValueError 已被 except Exception 捕捉，不是 crash 原因
- 實際根因：`shadow_findings.jsonl` 是由 Codex 排程 automation（`system-patrol-hourly`、`heartbeat-watchdog`）寫入，這些 automations 於 Jun 2 停止供料、Jun 11 正式封存，且無任何機制接管
- convergence-engine 的 shadow review hook 寫入的是 `local_model_findings.jsonl`（1.8MB 仍在更新），但 nightwatch 把兩個檔案分開檢查後才發現 shadow_findings.jsonl 的缺口

**修復（2026-07-10 16:22 完成）：**
1. `run_convergence_engine.py`：新增 `_append_shadow_finding()`，每輪跑完後寫一筆 patrol-style 條目到 `shadow_findings.jsonl`，接管 Codex automation 的供料職責
2. `shadow_review_hook.py`：`_parse_first_json_object()` 加入 markdown code fence 去除（`_strip_code_fence`），減少模型回覆帶 ` ```json ` 包裝時的 reviewer_error
3. `docs/pitfalls.md`：新增 2026-07-10 監控盲區教訓

**驗證：**
- `shadow_findings.jsonl` 新增條目 `ts: 2026-07-10T16:22:32+08:00`，`patrol: convergence-engine`
- nightwatch 再跑：**1 alert → 0 alerts（全部 🟢）**
- investment-os repo commit: `a88119c9`

**代碼狀態：**
- 修改已同步到 runtime (`/Users/pagemacmini/.local/share/investmentos-telegram-operator/`)
- 下一輪 launchd 自動觸發的 convergence-engine 也會維持供料

---

### 本批 Owner 待決

| 項目 | 待決事項 | 優先 |
|------|---------|------|
| B5 角色 | 核准 `projects/b5-shadow-capability-distillation.md` 或提意見 | ⭐ 中 |
| shadow_findings.jsonl 供料斷供 | ✅ 已修（2026-07-10 A1 完成） | — |

---

## A0 委派回報（B5 建立批）— 2026-07-11

**觸發：** Owner 原話「b5通過」
**執行方：** A1 系統總管（代理 B5 首輪執行）
**完成時間：** 2026-07-11

---

### 執行確認（逐項）

**1. 章程狀態 ✅**
- `projects/b5-shadow-capability-distillation.md` 狀態改「✅ Owner 核准 2026-07-10」

**2. AGENT_RULES.md 角色表 ✅**
- Section 1 B4 行之後加入 B5（三項職責）

**3. AGENT_RECALL_PROMPTS.md ## B5 段落 ✅**
- 位置：B1-B4 之後、WIN 之前
- 含 superpowers + fable-mindset 條款、斷點、完整 recall 指向

**4. recalls/B5_recall.md ✅**
- 完整召回 prompt，含三項職責、斷點、輸出物

---

### B5 首輪執行結果

**① 召回品質審查 2026-Q3 ✅**
產出：`reports/recall-quality/recall_quality_2026-Q3.md`

🔴 **緊急發現**：
- 全 17 個 recall 文件 **0 個**有 fable-mindset 注入（AGENT_RECALL_PROMPTS.md 有注入，但獨立 recalls/*.md 全部缺失）
- **A5 recall 過時 ~85 天**（最後 commit 2026-04-17），T-A5-002/004/005 CRITICAL 狀態未反映
- **A7 recall 過時 ~85 天**（最後 commit 2026-04-17），T-A7-001 🔴 Phase 3 未啟動未反映

⚠️ 中等發現：A4 recall 未更新 T-A4-001 ✅ 完成；A6_recall_compact.md 重複待刪

**② 首次蒸餾評分 ✅**
產出：`reports/capability-inventory/inventory_2026-07.md`

Top 8 可直接打包（評分 5，無需改寫）：
- `docs/fable-mindset.md`（工作思維 10 條）
- `skills/task-progress-guide.md`（進度格式）
- `skills/brand-voice-guide.md`（品牌語氣）
- `skills/first-principles-check/SKILL.md`（決策框架）
- `skills/a6-safety-boundaries.md`（安全邊界）
- `skills/session-handoff.md`（Session 交接格式）
- pitfalls.md 6 條通用行為規則
- `workbook/reviews/JOB-A1-ALT-TEXT-STANDARD-20260630`（圖片標準）

**③ 教材包骨架建立 ✅**
- 目錄：`packages/local-model-teaching/2026-07/`（recall_prompts/ top_jobs/ eval_cases/）
- 打包腳本：`scripts/b5-pack-teaching-package.sh`（可執行，每月第一個週一跑）

---

### Owner 需決策的事項

| 優先 | 事項 | 建議 |
|------|------|------|
| P0 | A5/A7 recall 過時 85 天 | 授權 A1 更新（10 分鐘） |
| P0 | 全體 recall 缺 fable-mindset 注入 | 授權 A1 批次補注入（30 分鐘） |
| P1 | B5 首次完整教材包打包 | 確認評分 → `bash scripts/b5-pack-teaching-package.sh 2026-07` |
| P2 | B5 定期執行節奏確認 | 建議每月第一個週一蒸餾；每季召回審查 |

