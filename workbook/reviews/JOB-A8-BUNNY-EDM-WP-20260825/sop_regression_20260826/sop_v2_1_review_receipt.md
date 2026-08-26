# A8 SOP v2.1 歷史人工精修回收與回歸收據

日期：2026-08-27  
範圍：SOP、acceptance gate、legacy platform exporter；沒有生成新歌、剪正式片、上傳、發布或發訊息。

## VERIFIED

- Owner 確認歷史 MAPLAB 影音曾使用 Canva／CapCut 與人工精修；這項事實已寫回 canonical SOP，不再用「repo 沒 project」否定歷史使用。
- 同步 Drive 的 2025 開幕素材留有可恢復 precedent：
  - `網站/網站用/開幕/White and Blue Vintage Cinematic POV Travel Getaway Instagram Reel.mp4`：SHA-256 `0b128c58771432cfb18e3397750beda4a7554b326dc67c8b8317949e7aae9378`；1080×1920、13.2 秒、H.264、無音軌，檔名符合 Canva template export 跡象。
  - `網站/網站用/開幕/0326.mp4`：SHA-256 `d1b117481feaa58d42b38ed277ea6c1416ee50e997efcf5b4743e60a489653f2`；1080×1920、14.21 秒、H.264＋AAC，為後續重新編碼版本。
- 第二支片符合「另進 NLE 加音訊／精修」跡象；沒有 CapCut project 或明確 encoder tag，所以只標 `INFERRED_NOT_VERIFIED`，不冒充 CapCut 已驗證。
- 邦尼兔 bundle 沒有 matching Canva design、CapCut editable project 或 Google Vids project；其可追溯 review receipt 是 Swift/AppKit＋FFmpeg。此結論只限邦尼兔歸因，不外推成「歷史上沒使用 Canva／CapCut」。

## SOP gap → v2.1 control

| 舊缺口 | v2.1 強制收據／阻擋 |
|---|---|
| 只寫工具名，沒有實際工具鏈 | `tool_chain[]` 逐步綁 tool、role、version 與 receipt |
| 每次重建 receipt 容易漏欄位 | 複製 `config/a8/video-acceptance-v2.template.json`；模板帶 `template_only`，未填完並移除標記永遠不能 PASS |
| CapCut／Canva／Google Vids 工程做完即消失 | `edit.project`、app version、timeline、export、`project_reopen` hash PASS |
| 人工 motion／字體／封面判斷沒留下 | `polish.recipe`＋cover hash；motion、typography、safe zone、palette、small-size 五項 PASS |
| 配樂商用狀態留空 | `rights.status`＋rights receipt；無新增音樂也要明寫 |
| `target_device_pass=true` 沒有眼見紀錄 | `target_devices[]` 綁 output hash、surface、1×／0.5× duration、verdict |
| 多平台只宣稱「同檔都可發」 | `delivery.targets[]`＋每平台 video／cover／metadata／safe-zone package |
| 雲端處理、草稿、公開、通知混成一次核准 | `THIRD_PARTY_PROCESSING`、`DRAFT_UPLOAD`、`PUBLICATION`、`MESSAGE_SEND` 分開 |
| legacy formatter 被誤寫成 final exporter | `export` fail-closed；`review-export` manifest 固定 `REVIEW_ONLY_NOT_FOR_UPLOAD` |

## 回歸結果

```text
python3 -m unittest -v \
  tests.test_a8_video_acceptance \
  tests.test_a8_platform_formats_guard \
  tests.test_a8_one_pass_timeline \
  tests.test_a8_enhanced_metadata

Ran 23 tests — OK
```

- 現行邦尼兔 v2 acceptance：`ok=false`、13 errors，原退件理由未漂移。
- 內部 one-pass regression acceptance：`ok=false`、5 errors，仍被音訊 ASR、品牌詞、真人聽辨、歌詞版本與 target-device gate 擋住。
- `a8_platform_formats.py export`：exit 2，正式匯出拒絕。
- `review-export`：測試確認每個 manifest entry 都標 `REVIEW_ONLY_NOT_FOR_UPLOAD`。

## DRIFT

- 以前 Canva／CapCut 人工精修做法有實作記憶與檔案跡象，但缺 design/project/timeline receipt，無法精確復原每個參數。
- 現行母帶仍未通過 actual-audio gate；本輪只修 SOP 地基，沒有假裝已產出合格新歌或影片。

## DISPATCH

- 無外部 dispatch。未登入 Canva／CapCut／Google Vids，未上傳 YouTube／TikTok 等平台，未發 Telegram。

## NEXT

從 Owner 現行 Google Doc 鎖定唯一歌詞並重生母帶；actual-audio ASR＋Owner 真人聽辨通過後，依 v2.1 建立可重開 editor project、人工精修配方與完整 platform package。只有 acceptance v2 `ok=true` 才進 `OWNER_VIDEO_GATE`。
