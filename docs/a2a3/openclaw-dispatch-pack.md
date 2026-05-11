# OpenClaw Dispatch Pack for A2/A3

這份文件是給 A6 / OpenClaw 的短任務包規格。

目標不是聊天，而是把任務變成可追蹤的工作包：

`Task -> Draft -> Review Bundle -> Owner Review -> Next Action`

## 工作包是什麼

工作包就是「一個任務對應一個資料夾」。

例如你今天要處理 `台南開幕茶會外燴`，就不是把所有東西丟給 OpenClaw 聊天，而是把這一包資料夾交給它：

- `brief.md`
- `draft.md`
- `seo.md`
- `rankmath_payload.json`
- `source_bridge.md`
- `preview.html`
- `assets/`

然後叫它只做這一包，產出 review bundle。

## 最小使用方式

你可以這樣交辦：

```text
job_id: JOB-A2A3-OPENING-001
task_type: ads_wordpress_pack
work_package: /Users/pagemacmini/Desktop/wordpress 素材庫/wordpress/opening-event-catering-tainan
goal: 請檢查這包內容，補齊圖文與 Rank Math，最後輸出 review bundle path
rules:
- read brief.md, draft.md, seo.md, source_bridge.md, preview.html
- no publish
- no main push
```

OpenClaw 讀到這段後，會知道它只需要處理單一工作包，不需要掃整個 Drive 或整個 repo。

## 必讀來源

1. `CURRENT_STATUS.md`
2. `projects/seo-ads-agent.md`
3. `skills/brand-voice-guide.md`
4. `skills/seo-session-checklist.md`
5. `skills/gdrive-to-wordpress-upload-guide.md`
6. `skills/a4-photo-asset-skills.md`
7. `skills/a6-sales-rapid-response-skills.md`
8. `wordpress 素材庫/source_manifest.json`

## 任務類型

### 1) `ads_wordpress_pack`

用途：

- WordPress 草稿
- Meta 廣告素材包
- SEO title / description / slug

輸出：

- `task_request.md`
- `draft.md` 或 `output.json`
- `execution_log.json`
- `output_manifest.json`
- `verification_log.json`
- `review_request.md`
- `rankmath_payload.json`
- `source_bridge.md`

### 2) `photo_material_pack`

用途：

- IG 截圖 + 文字整理
- 素材分類
- 對應 WordPress 頁面 / 廣告 campaign

輸出同上，另外要加：

- `asset_map.json`
- `source_index.md`

### 3) `tracking_pixel_pack`

用途：

- 像素 / GTM / 來源欄位整理
- 案件來源回填
- 廣告素材與頁面對照

輸出同上，另外要加：

- `tracking_matrix.json`
- `case_source_fields.md`

## 硬性安全邊界

- 不直接發布 WordPress
- 不推送 GitHub main
- 不刪原始照片
- 不掃整個 Drive
- 不讀 `.env`
- 不安裝新技能，除非 Owner 明確批准
- 若需 WordPress / Rank Math API，僅從 Notion vault 或本機 env 讀取，不得把憑證寫回 repo

## 任務回報格式

每個任務完成後，A6 至少要回：

1. `task_type`
2. `worker`
3. `review bundle path`
4. `next_action`

## 短 prompt 模板

### WordPress + Meta

```text
job_id: JOB-...
task_type: ads_wordpress_pack
goal: 產出一份可審查的 WordPress 草稿與 Meta 素材包
inputs:
- source notes
- target slug
- audience
- case references
outputs:
- draft.md
- output.json
- review bundle
safety:
- no publish
- no main push
```

### WordPress 工作包檢查

```text
job_id: JOB-...
task_type: ads_wordpress_pack
work_package: /Users/pagemacmini/Desktop/wordpress 素材庫/wordpress/<slug>
goal: 檢查這個 WordPress 工作包是否完整，並補齊 review bundle
inputs:
- brief.md
- draft.md
- seo.md
- rankmath_payload.json
- source_bridge.md
- preview.html
safety:
- no publish
- no main push
- no overwrite original assets
```

### 素材整理

```text
job_id: JOB-...
task_type: photo_material_pack
goal: 把 IG/Drive 素材整理成可回填的素材包
inputs:
- screenshots
- captions
- source folder path
outputs:
- asset_map.json
- source_index.md
- review bundle
safety:
- no delete
- no overwrite original
```

### Tracking / Pixel

```text
job_id: JOB-...
task_type: tracking_pixel_pack
goal: 整理像素、GTM、來源欄位與 campaign 對應表
inputs:
- pixel ids
- campaign names
- case source fields
outputs:
- tracking_matrix.json
- case_source_fields.md
- review bundle
safety:
- no publish
- no irreversible changes
```
