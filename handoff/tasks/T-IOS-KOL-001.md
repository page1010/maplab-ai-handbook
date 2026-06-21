# T-IOS-KOL-001 — IOS-KOL 網紅雷達 Daily Telegram Digest

---

## 接續狀態

> **Agent 冷啟動時第一個看的區塊。每次 checkpoint 必須更新。**

- **狀態**：🔄 進行中
- **最後活動**：2026-06-20（`build_cross_checks()` 補 `source_ids` scoped cross-check；接上正式 rubric）
- **接續點**：四個每日時段（02:30/08:30/14:30/21:20）的 Telegram digest 已依 `docs/ios-kol/daily-telegram-workflow.md` 的 gate 規則運作；核心 YouTube KOL（游庭皓/股癌/財報狗/理財達人秀/定錨）+ 理財達人秀／兆華與股惑仔 Podcast RSS 已接上 visibility gate 與 scoped cross-check。下一步：補「待補 sources」（英文 KOL/英文新聞、總經資料、台股對照）。
- **阻塞**：無。

---

建立：2026-06-21 | **Owner 角色（executor）**：IOS-KOL 網紅雷達經理 | **Reviewer 角色**：B2 Investment OS Reviewer

---

## (A) Goal / Outcome

每天 4 個固定時段（02:30 夜盤總經 / 08:30 早盤前 / 14:30 盤中午後 / 21:20 晚間）依
`docs/ios-kol/daily-telegram-workflow.md` 的責任歸屬與 gate 規則，把 KOL/RSS/OpenClaw/ASR
原始素材整理成 Telegram digest（`網紅單集重點` / `網紅投資 seed triage` /
`IOS-KOL 夜盤總經共識雷達`）送出；**沒有過 gate 的內容（metadata-only 充當完整內容、
Q/A 殘渣、核心 KOL 整列消失、內部流程語外洩）不得送出。**

---

## (B) Definition of Done（GO Prompt 五要素）

> 完整填寫說明見 `templates/go-prompt-template.md`。

| 要素 | 內容 |
|------|------|
| Outcome | 同上 (A) |
| Verification | 兩層：① 客觀 gate（先過）：依 `docs/ios-kol/daily-telegram-workflow.md`「正式『網紅單集重點』gate」表逐項檢查 `transcript_status` / `metadata_only` / RSS 規則 / Q&A 完整度。② 主觀任務（文字品質，gate 通過後再評）：依 `rubrics/telegram-digest-quality.md` 評分（資訊密度/格式一致/措辭安全/資料層級透明）。 |
| Constraint | 見下方 (C)。 |
| Iteration Policy | 每次 `influencer-sync-refresh` 等排程 job 跑完後，把「這輪改了什麼/結果/下一步」append 到本文件 `docs/ios-kol/daily-telegram-workflow.md` 的「修正記錄」區塊（該區塊本身就是 append-only 變更日誌）；較大改動另開 `workbook/reviews/JOB-IOS-KOL-*/` bundle。 |
| Error Handling | 見下方 (C)。 |

**Verification 類型**：**混合**——先過 `docs/ios-kol/daily-telegram-workflow.md` 的客觀 gate 表（transcript/metadata/RSS/content/Q&A/操作筆記），通過後再依共用 rubric → `rubrics/telegram-digest-quality.md` 評文字品質（rubric 本體不內聯複製，只連結）。

---

## (C) Constraints + Error-handling / Escalation

**Constraints（不能碰什麼）**：
- 不下單、不建模擬單、不給買賣建議（Investment OS B-role 共用規則，見
  `projects/invest-os-b-role-system.md`）。
- 不讀 secrets / `.env` / API keys / cookies。
- 不可讓核心 KOL（游庭皓/股癌/財報狗/理財達人秀/定錨）整列消失；沒有逐字稿/ASR
  時必須顯示 `待 ASR/逐字稿` 與下一步，不能靜默跳過。
- 不可把 metadata-only（只有 RSS 標題描述）包裝成已有完整內容結論。
- 全域硬性禁止見 `AGENT_RULES.md` SECTION 8.5。
- `influencer-sync-refresh` / `influencer-youtube-rss-poll` 是 cron 排程的無人執行
  job，適用 `AGENT_RULES.md` SECTION 19（無人長跑安全規則）與
  `docs/governance/unattended-run-safety.md`：高風險面（發送決策性結論、改 Investment OS
  持倉判斷）預設唯讀只能提議，不能未經 gate 直接執行；長跑/排程異常需有
  token/時間/iteration 上限與 append-only 日誌。

**Error Handling / Escalation（何時停下回報，回報給誰）**：
- 任一來源缺登入態、逐字稿、ASR 工具失效（例如 `yt-dlp` wrapper 壞掉）→ 輸出
  `auth_missing` 或對應缺口狀態，不得用舊 corpus 假裝今日報告，回報 IOS-KOL。
- 核心 KOL 連續多輪消失於 digest、或 rubric 評分任一維度持續 0 分 → 停止送出，
  回報 B2 Reviewer 一起檢查 visibility gate / cross-check 邏輯。
- 阻塞審查走 `AGENT_RULES.md` SECTION 16 三層審查 SOP：先看自己能不能解
  → 角色內審核理由合理性 → 解除後要推動下一步，不是回報完就結束。

---

## 目標

定義 KOL/RSS/OpenClaw/ASR 到 Telegram 的責任歸屬、每日工作與品質 gate，
讓 IOS-KOL 部門每日 4 個時段的 Telegram digest 可信、可稽核、不假裝完成。
完整運作細節見 `docs/ios-kol/daily-telegram-workflow.md`（本卡是它的
task card 入口，不重複展開全部規則）。

## 已完成

| Commit/日期 | 內容 |
|--------|------|
| 2026-06-17 | `網紅單集重點` 開頭加入 IOS-KOL 與流程說明；正式單集重點只允許 `transcript_status=ok`；RSS/metadata-only 不再混進正式單集重點；操作筆記濾除段落標題與 Q/A 殘渣 |
| 2026-06-18 | Test receipt 落檔（`workbook/reviews/JOB-IOS-KOL-RADAR-TEST-20260618/TEST_RECEIPT.md`）；單集重點/夜盤總經 digest 通過 live DB preview + pytest 驗證 |
| 2026-06-20 | 補《兆華與股惑仔》SoundOn RSS，`build_cross_checks()` 支援 `source_ids` scoped cross-check，新 podcast row 不再被全域 latest 20 擠掉 |
| 2026-06-20 | 接上正式 rubric `rubrics/telegram-digest-quality.md`（Owner 採納） |
| 2026-06-21 | 建立本正式 task card，取代 `docs/ios-kol/daily-telegram-workflow.md` 裡的暫放 verification 連結 |

## 現在卡在哪裡

「待補 sources」尚未接（見 `docs/ios-kol/daily-telegram-workflow.md` 待補 sources 表）：
1. 英文 KOL / 英文新聞 — 必須先翻譯，再整理成同一格式。
2. 總經資料 — 夜盤、美債殖利率、美元、油價、BTC、VIX、重要數據日曆。
3. 台股對照 — 台指夜盤、ADR、SOX、NVIDIA/TSMC ADR、AI server 供應鏈。

## Blockers

無立即阻塞；上述「待補 sources」是待辦，不是阻塞。

## 接續 Prompt

```
[直接複製此段貼到下一個 session 即可接手]

你是 MAPLAB IOS-KOL 網紅雷達經理。
repo: https://github.com/page1010/maplab-ai-handbook
先讀 CURRENT_STATUS.md，再讀 handoff/tasks/T-IOS-KOL-001.md，
再讀 docs/ios-kol/daily-telegram-workflow.md（完整運作規則）。

上次做到：四個每日時段 digest 已運作，核心 YouTube KOL + 理財達人秀／兆華與股惑仔
Podcast RSS 已接上 visibility gate 與 scoped cross-check；rubrics/telegram-digest-quality.md
已接上作為主觀文字品質 verification。
下一步：補「待補 sources」（英文 KOL/英文新聞、總經資料、台股對照）之一，
先確認資料來源是否需要 Owner credential bootstrap（見 AGENT_STARTUP_PROTOCOL.md Step 5.5）。
Blocker：無。

讀完文件後輸出 Startup Check。必拿：skills/task-progress-guide.md
```
