# 技能：IG 廠商詢價發送（官方帳號、Chrome 分頁、截圖辨識）

建立：2026-09-07（Owner msg 4957/4963 裁定）。執行者：a0/Fable5 或任何接到派工的 agent。

## 目的
用 MAPLAB 官方 IG 帳號，向 vendor-db 名單中的廠商逐家發送詢價私訊。
只發送、不對話：發完那一句就停，廠商任何回覆一律留給 Owner。

## 前置條件（缺一即停，回報 Owner，不硬闖）
1. Owner 已在 Chrome 登入官方 IG（登入動作永遠是 Owner 做，agent 不碰帳密）。
2. Claude-in-Chrome 擴充已連到執行 agent 的 session（工具 mcp__claude-in-chrome__* 可用）；
   若只有 computer-use，瀏覽器是 read tier 不能點擊——必須走擴充，不硬用截圖點座標。
3. 詢價文字已由 Owner 核可（目前版本：data/vendor-db/inquiry-scripts-20260907-clinic-case.md）。
4. 發送名單已由 Owner 圈選（目前版本：handoff/drafts/a0-sendlist-4955.txt，11家）。

## 流程
1. 開分頁：bash scripts/a0_open_tabs.sh "https://www.instagram.com/direct/inbox/"
   （或直接開各廠商 profile URL）。
2. 截圖確認：右上有無登入頭像＝確認是官方帳號已登入；看到登入頁＝停、回報。
3. 逐家執行：
   a. 開廠商 IG profile URL（名單裡的連結）。
   b. 截圖辨識「發送訊息/Message」按鈕；無此鈕（不開放私訊）→ 記錄跳過。
   c. 點開私訊視窗，貼上對應類別的詢價稿全文（攝影/花藝/主持各用各的版本）。
   d. 發送前截圖一次留檔比對（文字完整、對象正確），按送出。
   e. 記錄到 data/vendor-db/sent-log.md：日期｜廠商｜類別｜已發/跳過原因。
4. 全部發完：更新 sent-log、Telegram 回報 Owner 一則（已發X家/跳過Y家＋原因），結束。

## 鐵則
- 一家一句：只發詢價稿，不追加任何訊息；廠商回覆不讀不回，歸 Owner。
- 不透露預算與報價（是我們挑廠商）。
- 不碰帳號設定、不改個人檔案、不追蹤/按讚/留言，只用私訊。
- 不輸入任何帳密/驗證碼；登入態掉了就停、回報 Owner 用 GUI 重登。
- 對外身分＝官方帳號；發送內容以 Owner 核可版本為準，臨場不改稿。

## 名單與稿件現行版本
- 名單：攝1-10＋擴7約瑟夫（見 a0-sendlist-4955.txt）；花1-5/主1-5 待 Owner 圈選後同流程。
- 稿件：inquiry-scripts-20260907-clinic-case.md（攝影/花藝/主持/音響四版）。
