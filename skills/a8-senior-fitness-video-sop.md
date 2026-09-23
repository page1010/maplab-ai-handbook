# A8-FITNESS 華語中高齡跟著動 SOP

Version: v0.1 — 2026-09-01  
Applies to: `A8-FITNESS` only  
Canonical final-video SOP: `skills/a8-produce-to-publish-sop.md`

## 1. Intake and Classification

1. 鎖定對象、站／坐能力、器材、片長、平台、語言、音樂與是否需要真人。
2. 分開標記：一般教育、運動建議、醫療／復健主張。後兩者沒有專業者就不得公開。
3. 把研究、local generation、third-party generation、draft upload、publication、新費用拆成獨立 authorization。

## 2. Research Gate

1. 優先 WHO、台灣國健署、CDC、NIA、NHS 等一手來源。
2. 成熟頻道只學抽象結構；不重製影片、腳本、縮圖、音訊、品牌或人物關係。
3. 輸出 `VERIFIED / INFERENCE / MISSING`，並記錄查核日期與 URL。
4. DeerFlow 只處理公開／合成問題；private source、登入態、Chrome cookie 與客戶資料不送入。

## 3. Movement Card

每個動作必有：名稱、目的、起始姿勢、3 個以內要領、主要活動區、常見錯誤、站／坐退階、停止條件、專業簽核狀態。沒有 `PT_PASS` 只能產私人 MVP。

## 4. Script and Rhythm

- 首屏：一般運動教育／非醫療、穩固無輪椅抵牆、清空地面、防滑鞋、依自己速度、隨時暫停。
- 17.5 秒 short：0–2.5 安全首屏；2.5–5 超慢示範；5–12.5 三次慢做；12.5–15 退階；15–17.5 回中立＋停止警語。
- spoken control 先完成。hip-hop 只能承載短 cue 與安全錨點；完整姿勢、退階、停止條件另用 spoken voice。
- 每輪不得同時改 movement、lyrics、voice、tempo、mix；一次只改一個可歸因變因。

## 5. Visual Production

1. 先定 9:16 safe zones，站姿頭腳椅全入鏡；不 blind crop、不 blur fill。
2. 簡圖用明確關節、慢速循環；主要活動區圓環標「非診斷」。
3. AI 人體影像只作私人 review；若出現關節、重心、支撐錯誤，直接退件。
4. final 走 evidence-complete editor 或 `ffmpeg_one_pass`；保留 raw/hash、timing map、command/filtergraph、單次有損編碼 lineage。

## 6. Audio Production

1. Instrumental prompt 明寫 no vocals/spoken words、固定 BPM、留口令中頻空間、無突然 drop／tempo change。
2. 點一次 Create 後記錄平台自動產生的所有 variants；不為「多拿版本」連點。
3. 下載後鎖 hash、方案與 rights readback；實際音檔不是 prompt。
4. 唱口令需 prompt-free ASR＋Owner 真人全片逐字聽辨。任何安全句錯字／吞字，重生，不靠字幕修。
5. mix 先 duck 音樂，確保手機喇叭仍能聽清楚每個 cue。

## 7. QA State Machine

`MOVEMENT_DRAFT → PT_REQUIRED → PT_PASS → AUDIO_SELECTED → TIMING_LOCKED → EDIT_READY → RENDERED_UNVERIFIED → QA_PASS → OWNER_VIDEO_GATE → APPROVED_FOR_UPLOAD`

`QA_PASS` 至少需要：ffprobe/hash、intro/middle/outro contact sheet、逐動作完整播放、1x/0.5x、字幕／口令 timing、actual-audio listen、rights、手機真機、安全區與停止警語。缺任一項保持 `MISSING`。

## 8. Platform Gate

- 建頻道不等於可以上片；上片不等於可以公開。
- 新 YouTube 頻道 final Create 是帳號／身份建立動作，執行前要 action-time confirmation。
- 沒有 `DRAFT_UPLOAD` 不上傳；有草稿授權只用 private/unlisted；沒有 `PUBLICATION` 絕不公開。
- YouTube AI disclosure、商用權與 original/authentic policy 在每次上架時重新 readback。

## 9. Rolling Job

每次 heartbeat：讀 Task Card 和 durable job → 若 `OWNER_REVIEW/COMPLETED` 則 no-op → 執行一個 safe unfinished phase → 驗證 owner-viewable artifact → 更新 state/history/next bounded action/resume prompt。新費用、公開、私密資料第三方與不可逆動作進 Owner gate。
