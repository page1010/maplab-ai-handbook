# OpenClaw QA Prompt — A2 ICC Tainan Landing Page

你是 MAPLAB A2 Ads SEO WordPress Patrol 的部門小弟，由 OpenClaw 執行只讀 QA。

任務：檢查已發布 landing page 是否符合 A2 WordPress 案例 Landing Page 強制模板 Gate。

Live URL:

```text
https://www.maplabkitchen.com/icc-tainan-catering/
```

Review bundle:

```text
/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/
```

必讀本地文件：

1. `/Users/pagemacmini/maplab-ai-handbook/CURRENT_STATUS.md`
2. `/Users/pagemacmini/maplab-ai-handbook/handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`
3. `/Users/pagemacmini/maplab-ai-handbook/recalls/A2_recall.md`
4. `/Users/pagemacmini/maplab-ai-handbook/skills/brand-voice-guide.md`
5. `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_publish_execution.md`
6. `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_image_attach_result.json`
7. `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/wp_selected_media_manifest_icctn_001.csv`

只讀檢查項目：

1. URL 是否 200、post 是否可作 Google Ads landing page。
2. 文章是否屬於案例分類，且不是一般 FAQ/指南分類。
3. 首屏與開頭是否自然包含 `大臺南會展中心外燴` / `大臺南會展中心茶點` / `ICC Tainan` 意圖。
4. 是否有快速導覽按鈕：案例照片、適合場景、配置重點、進場檢查、常見問題、LINE 詢問。
5. 是否有至少 5 張圖片，且 media ID / alt / caption 對得上 manifest。
6. 是否有 featured image。
7. 是否有 FAQ block，而不是正文手寫 `<script>` 或 JSON-LD。
8. 是否有至少 3 個相關 live URL 內連。
9. 是否有 LINE CTA。
10. 品牌語氣是否符合 MAPLAB：說場景、具體、克制、不硬賣。
11. 是否有禁用/高風險內容：保證、唯一、最好、便宜、CP值、過度承諾、內部案名、Drive/本機路徑、價格、私人會議資料、未授權人臉、外部 logo。
12. 是否有 Google Ads 導流風險：頁面與「大臺南會展中心外燴 / 茶點 / 活動餐點」搜尋意圖是否一致。

安全邊界：

- 不登入 WordPress。
- 不讀 Notion、credential、cookie、token、`.env`。
- 不改 WordPress、Google Ads、Meta Ads、GTM、Pixel、預算或開關。
- 不 commit、不 push。
- 不發布、不刪除、不上傳媒體。

輸出請寫成：

```text
OPENCLAW_A2_ICCTN_QA_RESULT
verdict: PASS / PASS_WITH_NOTES / FAIL
checked_at: <local time>

facts:
- ...

findings:
- [severity] item — evidence

missing_or_risk:
- ...

ads_landing_readiness:
- ready / not_ready / ready_with_notes

next_actions:
- ...
```

請只回檢查結果，不要重寫文案。
