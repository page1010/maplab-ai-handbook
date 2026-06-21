# rubrics/

放**共用、可重複使用**的評分標準（rubric），給主觀輸出（文案語氣、報告格式、
影片風格、客戶溝通措辭……）的 reviewer 角色引用。

## 為什麼要有這個資料夾

主觀判斷如果只靠 agent「自己感覺對不對」，標準會因人/因次而異，
而且同一套標準很容易散落在十張 task card 裡，改一次要改十次。
做法：**rubric 只在這裡寫一份**，task card 的 `(B) Definition of Done`
裡用一行連結過去，不要把整份 rubric 內聯貼進 task card。

## 怎麼建立一份新 rubric

1. 複製 `templates/rubric-template.md` 到 `rubrics/<主題>.md`。
2. 照六步法填：先跑 baseline → 記皺眉點 → 分維度 → 每維度寫具體
   do-not 案例 → 補多樣化案例避免 overfitting → 最後才讓 reviewer 用它打分。
3. 在引用這份 rubric 的 task card 的 `(B) Definition of Done` 寫：
   `Verification（主觀任務）：依 rubrics/<檔名>.md`。
4. 新 rubric 上線前兩週、或維度修改後一週內，照 rubric 裡的「評審打分說明」
   人工抽查，確認 reviewer 判斷跟人眼一致。

## 目前生效中的 rubric

| 檔案 | 狀態 | 連結的 task card / 文件 |
|------|------|--------------------------|
| `rubrics/telegram-digest-quality.md` | ✅ 生效中（Owner 2026-06-20 採納） | `handoff/tasks/T-A1-LEARNING-LOOP-001.md`（A0 patrol Telegram card）、`handoff/tasks/T-A6-001.md`（A6 一般聊天/案件摘要）、`docs/ios-kol/daily-telegram-workflow.md`（IOS-KOL 單集重點/夜盤總經摘要，尚無正式 task card） |

`rubrics/telegram-digest-quality.md` 取自 `pitfalls.md` 既有的 Telegram
digest 踩坑紀錄（內部流程語外洩、Q/A 殘渣），示範「具體 do-not 案例」
該寫到什麼程度，同時也是目前唯一正式生效的 rubric。新建 rubric 時可以
參考它的填法，再依「怎麼建立一份新 rubric」的步驟建自己的檔案。
