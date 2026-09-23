# 邦尼兔影片自動發佈能力盤點

日期：2026-08-25

狀態：`REVIEW_ASSET_READY / PUBLICATION_NOT_AUTHORIZED`

## 目前可交付影片

- 15 秒審核片：`workbook/a8/pilot-bunny/short15-review/bunny-v45-all-01-short15-review.mp4`
- 規格反讀：H.264 + AAC、1080×1920、30fps、15.000 秒。
- 內容 QA：既有 intro／middle／outro 抽幀未見人物、日期或內部工作語。
- 本輪目視接觸表：`bunny_short15_contact_sheet.jpg`；開場、7.5 秒、結尾的品牌字與 CTA 均未裁切，畫面未見人物或日期。
- 權利邊界：音源是既有免費期生成版本，商業使用權尚未驗證，因此目前只算內部審核片，不算可公開母帶。

## 「真的能由 Agent 自動送出」與「只有格式」

| 目的地 | 目前真實能力 | 證據／限制 | 本輪是否送出 |
|---|---|---|---|
| YouTube Studio | 已跑過 Chrome 操作建立私人 Short 草稿 | `skills/a8-produce-to-publish-sop.md` 記錄 2026-08-02 `maplabkitchen` 私人 Short 成功；現有 OAuth 無 `youtube.upload`，不是 API 無人值守發佈 | 否；本案仍缺音源權利與 Owner 上傳核准 |
| Google Drive | 可自動存放 review／publish 檔案 | 這是交付儲存，不是社群發佈 | 否 |
| Telegram | SOP 規劃以 `sendVideo` 送審 | 本 repo 尚未找到本案可重跑的影片 sender 與真實 readback receipt，不能列為已接通 | 否 |
| TikTok | 已有 9:16 檔案與 metadata 規格 | 未找到通過 app／scope／audit 的自動上傳器；目前是人工 Web／Studio 路徑 | 否 |
| Instagram Reels | 已有 9:16 檔案規格 | 未找到已驗證自動上傳器 | 否 |
| Facebook Reels | 已有 9:16 檔案規格 | 未找到已驗證自動上傳器 | 否 |
| Pinterest | 可產 2:3 cover／Pin 文案包 | 未找到已驗證自動建立 Pin 的寫入線路 | 否 |

## 結論

目前唯一有歷史真實成功證據的自動外部寫入，是 **Chrome → YouTube Studio 私人 Short 草稿**。其餘平台是「輸出格式可用」，不是「自動發佈已接通」。公開上線仍需依序完成：歌詞明確核准 → 有效訂閱權益下的新母帶 → Owner 選曲與音訊 QA → A8 長短片／封面 → 平台 approval card → Owner 核准發佈。

## 下一個可執行批准點

1. 若只想看上片流程：Owner 明確核准「可上傳 YouTube 私人草稿」，A8 才以審核用途建立私人草稿；不公開。
2. 若要正式對外：Owner 先在 `lyrics_review_v2.md` 回覆 `歌詞安全版通過` 或 `具名邦尼兔通過`，再以有效訂閱生成可追溯新母帶。
