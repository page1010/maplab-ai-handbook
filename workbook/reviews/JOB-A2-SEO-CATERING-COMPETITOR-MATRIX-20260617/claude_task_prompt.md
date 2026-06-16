# Claude Task Prompt - MAPLAB Catering SEO Article Matrix

你是 MAPLAB A2 SEO Writer / WordPress Content Strategist。

請先讀以下本地檔案，不要跳過：

1. `CURRENT_STATUS.md`
2. `pitfalls.md`
3. `handoff/tasks/T-A2-005-local-seo-factory.md`
4. `handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`
5. `handoff/tasks/T-A2A3-001-B.md`
6. `projects/seo-ads-agent.md`
7. `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/competitor_seo_matrix_benchmark.md`
8. `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/article_matrix_seed.md`

任務：

根據 A0 的國外外燴 SEO matrix benchmark，幫 MAPLAB 產出第一批「台南高質感外燴 / 企業外燴 / 會議茶點」SEO 文章與矩陣規劃。目標不是寫一篇孤立文章，而是建立可重複生產的 keyword matrix。

請做以下輸出，全部寫到：

`workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/claude_outputs/`

必交付：

1. `keyword_matrix_v1.md`
   - 用表格整理 location / venue / event type / buyer role / menu type / proof / FAQ 七條軸線。
   - 每列包含 target keyword、supporting keywords、search intent、recommended page type、priority、evidence status、asset need。

2. `article_briefs_v1.md`
   - 產 10 篇文章/landing page brief。
   - 每篇包含 SEO title、slug 建議、meta description、H1、H2 outline、FAQ、CTA、內部連結、需要 A4 補圖或 Owner 補證據的地方。

3. `draft_01_icc_tainan_expansion.md`
   - 主題：大臺南會展中心外燴指南。
   - 要能接到現有 live page `https://www.maplabkitchen.com/icc-tainan-catering/`。
   - 不要假裝已經能改 WordPress；只產草稿。

4. `draft_02_tainan_corporate_catering_admin_guide.md`
   - 主題：台南企業外燴推薦：行政窗口如何規劃會議茶點與午餐。

5. `draft_03_opening_tea_party.md`
   - 主題：台南開幕茶會外燴：品牌活動、貴賓接待與照片好看的餐桌配置。

6. `publication_risk_checklist.md`
   - 列出發布前必查：live URL、內部連結、圖片授權、案例是否可公開、場地名稱是否可用、價格/費用措辭、RankMath/Yoast 欄位、schema/FAQ。

寫作規則：

- 不要複製 Social Pantry / ZeroCater / Fooditude / Rocket Food 的文案，只學架構。
- 不要誇大 MAPLAB 沒證據的業績、合作品牌或場地。
- 不要用「最便宜」「保證第一名」「全台第一」這類低信任字眼。
- 文章語氣要像 MAPLAB：精準、溫暖、有畫面、重視現場秩序與品牌感。
- 所有資訊分成：
  - `verified_public`
  - `verified_internal`
  - `reasonable_inference`
  - `needs_owner_evidence`
- 看到 planned slug 時要特別小心，因為本 repo pitfall 已記錄：planned slug 不等於 live WordPress URL。
- 不要做 WordPress 發布、Google Ads 變更或任何需要憑證的動作。

影片/Reel 邏輯：

Owner 提到「如果 Claude 可以搞定影片，文章應該也行」。這次 Instagram Reel 內容尚未被 A0 可靠讀取，所以不要假裝知道影片內容。請只在流程設計裡寫：

`video/reel -> transcript or screenshot evidence -> event facts -> article brief -> draft -> publication risk check -> WordPress-ready draft`

如果需要影片內容，請在輸出中列為 `needs_owner_evidence`，不要腦補。

完成後，請在 `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/claude_outputs/README.md` 留 30 行以內的 Resume Prompt，讓下一個 agent 可以直接接續。
