# A4 事實鏈找圖技能 — Fact-first Asset Matching

版本：v1.0 | 建立：2026-05-12 | 維護：A1/Codex

## 什麼時候用

看到以下需求就先用這本，不要直接憑圖片印象挑圖：

- 找 MAPLAB 真實案例照片
- 補 WordPress / SEO / 廣告素材
- 對齊 IG、報價單、Google Drive、ASSET_LOG
- Owner 要求「讓事實說話」
- 需要確認某張圖是哪一場活動
- 2025 / 2026 外燴素材要分到企業、開幕、會議、週歲、婚禮等場景

## 核心原則

圖片辨識只能當 QA，不是第一索引鍵。

正確順序：

```text
Drive 圖片拍攝日期
→ 報價單日期
→ TimeTree 外燴事件
→ ASSET_LOG year/category/keywords/seo_name
→ Drive source file
→ 視覺 QA
→ public / internal 分層
```

不要從 IG 網格截圖或 AI 生成圖開始。先確認「這張圖屬於哪一場真實活動」。

## 標準流程

1. 先讀事實源：
   - `docs/a4/source-of-truth.md`
   - `docs/a4/drive-map.md`
   - `docs/a4/asset-finding-path.md`
   - `pitfalls.md`

2. 跑 2025 事實鏈匹配：

   ```bash
   python3 tools/ai_workbook/cli.py asset-case-match --year 2025 --limit 120
   ```

   若要查特定日期：

   ```bash
   python3 tools/ai_workbook/cli.py asset-case-match --year 2025 --limit 25 --date 2025-02-19
   ```

3. 只把 `confidence >= 90` 的候選拿來做案例素材。

4. 視覺 QA：
   - 確認餐桌、場景、光線、構圖可用
   - 避免人臉、兒童、非 MAPLAB logo、模糊低解析
   - 不要把可辨識電話、地址、私人資訊放進公開稿

5. 分層輸出：
   - internal QA 可保留日期、報價單、row id、Drive link、本機路徑
   - public draft 不得出現內部日期、價格、聯絡資訊、地址、本機 `file://` 路徑

## 輸出格式

每組可用案例至少要留下：

```text
case_name_public_safe:
scenario:
seo_targets:
evidence:
  - photo_date:
  - quote_sheet:
  - timetree_event:
  - asset_log_rows:
  - drive_file_ids:
assets:
  - seo_name:
  - alt_text:
  - drive_url:
  - suggested_destination:
public_notes:
internal_notes:
next_action:
```

## 驗收標準

一組案例能進 A2/A3 素材庫，必須同時滿足：

- 有 Drive metadata 拍攝日期
- 同日期找到報價單 `.gsheet`
- 同日期有 TimeTree 外燴事件，或報價單本身足以說明活動
- ASSET_LOG 是 `category=外燴` 且有 `keywords/seo_name/alt_text`
- 圖片通過視覺 QA
- public copy 已去除價格、電話、地址、內部日期與本機路徑

## 已驗證成功案例

第一組 seed case：

- 日期：`2025-02-19`
- 場景：B2B 公司茶點 / 開春聚餐
- 報價單：`2025 2 19 900 15人.gsheet`
- public-safe case name：`亞綸科技開春聚餐茶點外燴`
- ASSET_LOG rows：`27133`, `27135`
- 對應 SEO：`台南企業外燴`、`台南會議茶點外燴`、`台南公司茶會`
- 證據包：`workbook/outputs/2026-05-12/T-A4-2025-asset-link-proof/confirmed_combo.md`

## 常見錯誤

- 只看圖片覺得像企業活動，就寫成企業案例。
- 只靠 AI 圖片辨識文字，沒對報價單。
- 把報價單上的價格、人數、電話、地址寫進公開稿。
- 把生成圖或裁切失敗圖放進 publish-ready 素材包。
- 把舊 A6 / OpenClaw raw bundle 當 active evidence。

## 相關工具與文件

- CLI：`tools/ai_workbook/asset_case_matcher.py`
- 入口：`python3 tools/ai_workbook/cli.py asset-case-match`
- 文件：`docs/a4/asset-finding-path.md`
- 事實源：`docs/a4/source-of-truth.md`
- Drive map：`docs/a4/drive-map.md`
- 踩坑：`pitfalls.md`
