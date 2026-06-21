# Rubric：Telegram Digest 文案品質

> **狀態：生效中（Owner 2026-06-20 採納）。** 對 IOS-KOL / A0 / A6 任何
> 產出 Telegram-facing 摘要文字的任務生效。內容取自 `pitfalls.md` 既有
> 踩坑紀錄整理而成。已連結的 task card / 文件：
> `handoff/tasks/T-A1-LEARNING-LOOP-001.md`（A0 patrol Telegram card）、
> `handoff/tasks/T-A6-001.md`（A6 一般聊天/案件摘要文字）、
> `handoff/tasks/T-IOS-KOL-001.md`（IOS-KOL 單集重點/夜盤總經摘要；運作細節見
> `docs/ios-kol/daily-telegram-workflow.md`）。
> 上線前兩週、或維度修改後一週內，仍需依下方「評審打分說明」人工抽查。

---

## 0. 適用範圍

評「Telegram digest 文案品質」——任何要產生 Telegram-facing 摘要文字的任務
（IOS-KOL 網紅雷達、A0 巡查推送、A6 報價回覆摘要）都可參考此檔。

---

## 1. 維度列表

1. 資訊密度（是否每句話都有資訊量，沒有空話）
2. 格式一致性（是否符合既定 digest 格式，不是自由發揮）
3. 措辭安全（是否洩漏內部流程語、是否有禁用詞）
4. 資料層級透明（是否標示出處是 RSS/逐字稿/ASR，不假裝有更高品質）

---

## 2. 每維度「具體」do-not 案例

**維度 3：措辭安全**（來源：`pitfalls.md` 2026-06-17「A8 local fallback...
internal ops wording」、2026-06-18「IOS-KOL radar must separate digest
visibility from transcript confidence」）
1. ❌ 絕不使用內部流程語：`取餐要順`、`動線穩`、`節奏更穩`、`分開`、`詳盡`
   ——這些是給自己人看的工作用語，不是給 Owner/客戶看的詞。
2. ❌ 絕不在正式單集重點裡留下 `Q1`/`A1` 這種問答殘渣格式——這是格式失敗，
   不是內容好壞問題。

**維度 4：資料層級透明**（來源：`pitfalls.md` 2026-06-18 IOS-KOL 條目）
1. ❌ 絕不把 metadata-only（只有 RSS 標題描述）包裝成已有完整內容結論；
   必須標 `RSS/標題描述摘要（待逐字稿）`。
2. ❌ 絕不在沒有逐字稿/ASR 時讓核心 KOL 整列消失；必須顯示
   `待 ASR/逐字稿` 與下一步，不能靜默跳過。

---

## 3. 多樣化案例區（避免 overfitting）

不要只給一種正面範本（例如「都寫成事件摘要」），否則所有 digest 會收斂成
單一樣板。依內容類型挑選：
1. **事件摘要式**：發生什麼事 → 可用訊號 → 限制 → 下一步（適合有逐字稿的核心 KOL）
2. **數據對照式**：本週 vs 上週關鍵指標變化（適合有結構化數據的來源）
3. **缺口提示式**：沒有逐字稿時，明確標示 `待 ASR/逐字稿` 與下一步
   （適合 metadata-only 或暫時拿不到內容的來源）

---

## 4. 評審打分說明

1. 每則 digest 對 4 個維度各打 0-2 分（0=違反 do-not 案例，2=完全符合）。
2. 任一維度為 0 分 → 該則 digest 不得送出，retry 或回報，不能降級放行。
3. 正式生效前兩週、或任何維度被修改後一週內，人工抽查至少 20% 的
   reviewer 判斷；連續 3 次跟人眼不一致就停用該維度的自動 gate，回去修
   rubric，不要放寬通過標準。
4. 抽查紀錄留在對應 `workbook/reviews/JOB-<TASK>-<DATE>/rubric_audit.md`。

---

## 5. 變更紀錄

| 日期 | 改了什麼 | 為什麼 |
|------|----------|--------|
| 2026-06-21 | 建立範例版本，整理自既有 pitfalls.md 踩坑紀錄 | B1 把 GO/rubric 方法落成 repo 標準模板時建立的示範填法 |
| 2026-06-20 | 由「範例/未生效」升級為「生效中」；檔名由 `example-telegram-digest-quality.md` 改為 `telegram-digest-quality.md`；連結 T-A1-LEARNING-LOOP-001 / T-A6-001 / IOS-KOL daily-telegram-workflow.md | Owner 拍板正式採納 |
| 2026-06-21 | IOS-KOL 連結改指向新建的 `handoff/tasks/T-IOS-KOL-001.md`，不再是暫放在 `daily-telegram-workflow.md` | IOS-KOL 正式 task card 已建立 |
