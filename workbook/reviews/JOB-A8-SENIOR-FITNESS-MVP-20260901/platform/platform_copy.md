# Platform Copy｜未授權上傳草稿

Status: `FORM_READY_CONFIRMATION_REQUIRED / COPY_DRAFT_ONLY / UPLOAD_NOT_AUTHORIZED / PUBLICATION_NOT_AUTHORIZED`

這份文件只凍結文案候選；不是 YouTube 上傳或發布指令。只有通過逐動作專業簽核、實際音訊 QA、完整播放與 target-device QA、六份 `maplab.a8.video-acceptance/v2` receipt，並取得 Owner 另外授權後，才可把 hash-bound 影片交給平台。

## Channel

- Proposed channel name: `跟著動｜華語樂齡節拍`
- Channel creation form: `FORM_READY_CONFIRMATION_REQUIRED`。登入後表單已填名稱 `跟著動｜華語樂齡節拍` 與可用 handle `@跟著動樂齡節拍`，綠勾且 final `建立頻道` 按鈕 enabled；尚未點擊。
- Visual receipt: `../qa/youtube-channel-form-ready.jpg`, SHA-256 `e1a9037bb2d69b8e69165a2fd004faf931998976542abaab2be769ea6d2e1735`。
- Final Create: 仍須 Owner action-time confirmation；不得把表單就緒說成頻道已建立。
- Video upload: `NOT_AUTHORIZED`
- Public/unlisted/private publication: `NOT_AUTHORIZED`

## Compilation draft

Title:

`107 秒跟著動｜5 個扶椅＋坐姿低衝擊動作｜華語樂齡節拍 MVP`

Description:

```text
這是 107 秒動作教學合輯：一段只看一個扶椅或坐姿動作，先看口令，再用自己的速度小幅跟做。它不是完整運動課，也不是醫療、復健或個別運動處方。

開始前請使用穩固、無輪且抵牆的椅子，清空腳邊地面。跟不上時可以縮小幅度、改坐姿或暫停。若出現胸痛／胸悶、暈眩或快暈倒、噁心、異常或嚴重喘、心悸、疼痛或任何不適，請立即停止；症狀持續時尋求當地緊急醫療協助。

本版本仍是私人技術 MVP：尚待合格專業者逐動作簽核、真人完整聽辨、手機／電視／YouTube 實機畫面驗證與 Owner 發布核准。
```

Suggested chapters only after a final accepted hash is available:

- `00:00` 安全提醒
- `00:10` 扶椅小踏步
- `00:28` 扶椅側點步
- `00:45` 扶椅慢抬踵
- `01:03` 坐姿輪流伸膝
- `01:20` 坐姿開胸夾背
- `01:38` 停止條件與收尾

The timestamps above are draft cues against the 107.5-second technical MVP and must be rechecked against the final accepted file before use.

## Short draft pattern

Title:

`{動作名}｜17 秒扶椅／坐姿跟著動｜華語低衝擊 MVP`

Description:

```text
先看再跟，用自己的速度與幅度。椅子須穩固、無輪並抵牆；跟不上可縮小幅度、改坐姿或暫停。胸痛／胸悶、暈眩或快暈倒、噁心、異常或嚴重喘、心悸、疼痛或任何不適時立即停止；症狀持續時尋求當地緊急醫療協助。

一般身體活動教育，不替代醫療、復健或個別運動處方。私人技術 MVP，尚未取得公開發布核准。
```

## Metadata candidates

- Keywords: `中高齡運動`, `樂齡運動`, `扶椅運動`, `坐姿運動`, `低衝擊運動`, `華語跟練`
- Hashtags: `#樂齡運動 #扶椅運動 #坐姿運動`
- Audience setting: `MISSING` — must be chosen in YouTube Studio with Owner/platform review; do not infer.
- AI/synthetic disclosure: `MISSING` — complete against the final asset and current YouTube form before upload.
- Thumbnail/cover: `MISSING`.

## Fail-closed platform rule

Channel creation is a separate authorization from upload. A created channel, a title draft, or a local MP4 never authorizes upload, unlisted/private publication, public publication, scheduling, monetization, or external sharing.
