# T-A8-FITNESS-MVP-001 — 華語中高齡跟著動 MVP

Owner: A8-FITNESS（A8 子角色）  
Status: 🟡 PRIVATE_MVP_RENDERED_UNVERIFIED / PT_REQUIRED  
Created: 2026-09-01  
Risk: high（健康內容、第三方生成、帳號建立、平台發布）

## Owner Request

建立可持續滾動的華語中高齡跟著動專案：以 DeerFlow 研究 Tabata、瑜珈、低衝擊與成熟跟練案例；在同一個 Chrome Extension 入口建立專用角色 Prompt 與 SOP；用簡單圖示、主要活動區圓環、華語教練口令與適合音樂，先做每動作短影音，再剪成合輯；今天完成 MVP 並建立新的 YouTube 頻道。

## v0.1 Scope Lock

- 工作名：`跟著動｜華語樂齡節拍`（頻道最終名稱在建立前仍可由 Owner 改）。
- 定位：一般身體活動教育；不是醫療、復健、個別處方、減重或防跌保證。
- 形式：5 支 17.5 秒 9:16 動作短片 + 1 支 107.5 秒 9:16 合輯。
- 動作：扶椅小踏步、扶椅側點步、扶椅慢抬踵、坐姿輪流伸膝、坐姿開胸夾背。
- 視覺：全身簡圖、穩固無輪椅、主要活動區圓環、單一大字口令、右側與底部平台 UI 安全區。
- 音訊：96 BPM 純伴奏 + 清楚華語口令。Suno 先做 instrumental；唱口令只留 A/B 草稿，Owner 核詞後才生成。
- 公開邊界：今天只做本機 owner-viewable MVP 與新頻道；不公開、不上傳影片。若另行批准草稿上傳，只可 private/unlisted。

## Authorization Readback

- public research: approved
- local generation: approved
- Suno third-party generation: approved within existing plan/credits; new charge or plan change is not approved
- create a new YouTube channel: approved, but browser policy requires action-time confirmation immediately before final Create
- draft upload: not approved
- public publication: not approved
- private/customer data egress: not approved and not needed

## Safety Gate

- `PT_REQUIRED`: 台灣物理治療師或合格高齡體適能專業者尚未逐動作簽核。
- 使用穩固、無輪、抵牆的椅子；清空地面；依自己的速度與幅度；隨時可改坐姿或暫停。
- 胸痛／胸悶、暈眩、噁心、異常或嚴重喘、心悸、快暈倒、疼痛或不適，立即停止；症狀持續時尋求當地緊急醫療協助。
- 簡圖與 AI 輔助畫面只供私人 MVP；公開教學 final 必須使用真人專業示範，或取得逐幀專業簽核。

## Acceptance

- [ ] 5 支 H.264/AAC、1080x1920、30 fps、17.5 秒短片，hash 與 ffprobe receipt 齊全
- [ ] 1 支 107.5 秒合輯，無額外有損重編碼或有完整 one-pass lineage
- [ ] 每支含安全首屏、慢示範、三次跟做、退階、停止條件
- [ ] 實際音訊全片聽辨、字幕／口令 timing、contact sheet、1x/0.5x playback 與手機 readback
- [ ] Suno 生成收據、下載音檔 hash、方案／商用權 readback
- [ ] A8-FITNESS Extension module 可見，role prompt／SOP／Task Card 路由正確
- [ ] 新 YouTube 頻道 URL 與登入後頻道名稱 readback
- [ ] 所有公開前缺口保持 `MISSING`；沒有把本機 MVP 說成可發布成品

## Durable Receipts

- Main job: `workbook/reviews/MAPLAB-DURABLE-JOBS/MAPJOB-20260901-122122-386366/job.json`
- DeerFlow retry: `workbook/reviews/A6-HERMES-TASKS/DFR-20260901-122529-0f23b8/receipt.json`
- Review bundle: `workbook/reviews/JOB-A8-SENIOR-FITNESS-MVP-20260901/`

## Current Evidence Boundary

- 本機已有 5 支 movement short 與 1 支 107.5 秒 compilation 候選；`RENDERED_UNVERIFIED` 只代表可做私人技術檢查，不代表 `QA_PASS`。
- Suno 已在一次已授權 Create 中生成兩個私人候選；variant A 已用可見 Chrome／native Save 流程下載為 `audio/suno-variant-a-32s.wav`，長 `32.280 s`，SHA-256 `7245ce245774c6b52fb40a56cb2cea218dfc82e6e8f6e58e34b678348144cc9f`。人類完整聽辨、實際 final mix 綁定、voice rights 與獨立商用權驗證仍為 `MISSING`。
- `qa/movement_safety_review.json` 仍是全 `MISSING` 的 fail-closed template；沒有具名合格專業者對 exact video hashes 逐動作簽核。
- `receipts/acceptance/` 的 5 支短片與 1 支合輯只能是 `maplab.a8.video-acceptance/v2` 診斷 receipt；任何 canonical 缺件都必須讓 gate result 保持 `ok=false`。
- YouTube 建頻道表單已填名稱 `跟著動｜華語樂齡節拍` 與可用 handle `@跟著動樂齡節拍`，final `建立頻道` 按鈕 enabled 但未點；狀態是 `FORM_READY_CONFIRMATION_REQUIRED`。Final Create 尚需 action-time confirmation；upload 與任何 private/unlisted/public publication 均 `NOT_AUTHORIZED`。

## Next Bounded Action

先把修正後 exact MP4 hashes 凍結，從 encoded outputs 重建 hash-bound contact sheet，對六支影片逐支完成 1×／0.5× 全片與手機／電視安全區 readback；再由具名台灣物理治療師或合格高齡體適能專業者填寫 `movement_safety_review.json` 並綁定 exact hashes。上述證據未齊前，六份 acceptance gate 必須維持 `RENDERED_UNVERIFIED / ok=false`。YouTube 建頻道表單可填到 final Create 前，但 final Create 必須先向 Owner 取得 action-time confirmation；不得上傳或發布影片。

## Resume Prompt

```text
我是 MAPLAB A8-FITNESS 華語樂齡節拍導演，環境是 /Users/pagemacmini/maplab-ai-handbook。先讀 AGENT_CORE.md、CURRENT_STATUS.md、pitfalls.md、handoff/tasks/T-A8-FITNESS-MVP-001.md、recalls/A8-FITNESS_recall.md、skills/a8-senior-fitness-video-sop.md、skills/a8-produce-to-publish-sop.md，以及 durable job MAPJOB-20260901-122122-386366。只做 Task Card 的 next bounded action。

現在狀態是 PRIVATE_MVP_RENDERED_UNVERIFIED / PT_REQUIRED，不是醫療建議或可發布 final。Suno variant A 已下載為 32.280 秒 WAV、SHA-256 7245ce245774c6b52fb40a56cb2cea218dfc82e6e8f6e58e34b678348144cc9f，但 human listen、final mix binding、voice rights 與獨立商用權驗證仍 MISSING。公開前必須 exact-hash PT_PASS、actual-audio QA、encoded-output contact sheet、每支 1x/0.5x、target-device QA、六份 acceptance ok=true 與 Owner publication gate 全部通過。唱口令在 Owner 核詞前不得送生成；YouTube 頻道 final Create 必須 action-time confirmation；影片上傳與 private/unlisted/public publication均沒有授權。每次只更新可驗證 receipt、hash、readback 與下一個 bounded action。
```
