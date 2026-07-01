# AGY 審查報告 — MAPLAB SEO 草稿 GAP-3 行政/HR guide
**審查日期**: 2026-07-01
**審查範圍**: workbook/outputs/seo-gap-drafts/hr-admin-meeting-catering-guide-tainan.md
**HARD RULES 遵守**: 唯讀審查，不動草稿，不發布。

---

## (a) 方向確認

### 1. GAP-3 草稿之 SEO 定位與商業價值
*   **結論**：**定位精準且具備極高轉換商業價值**。
*   **分析**：
    *   依據 [seo-keyword-map.md](file:///Users/pagemacmini/maplab-ai-handbook/docs/seo-keyword-map.md)，本篇針對的是 **買家角色群（Buyer Persona）** 中「行政、HR、秘書」等企業活動直接籌辦者。
    *   主關鍵字鎖定 `行政外燴推薦` 與 `HR 活動餐點規劃`。這類搜尋意圖雖然搜尋量（Volume）可能低於泛詞，但 **商業意圖極高**（搜尋者即為有具體發包需求的 B2B 決策/執行窗口）。
    *   次關鍵字涵蓋 `會議茶點怎麼訂`、`份量`、`預算審核`、`approval-ready`。草稿內文從 HR/行政籌辦活動的真實痛點（如送審主管、拆分預算、場地協調等）切入，提供結構化的工具表單（如：Approval-ready brief 表格、預算拆解結構），能有效吸引尋找實用指南的窗口並建立信任感。

---

## (b) 語氣落地

### 1. 語氣層級對照 ([brand-voice-guide.md](file:///Users/pagemacmini/maplab-ai-handbook/skills/brand-voice-guide.md))
*   本草稿完全符合 **B級 資訊引導** 語氣（清楚、具體、可搜尋、可理解，保留品牌溫度）。
*   **對窗口特性的精準契合**：語氣俐落、商務感強、不拖泥帶水。以專業顧問視角協助 HR 排除主管審核阻礙，例如：「*對行政、HR、秘書窗口來說，一份好送審的餐點 brief，會讓主管更快看懂預算，也讓現場接待更穩。*」
*   **去推銷化與克制感**：全篇無過度吹噓或硬推銷，著重在解決窗口的實際執行難題。
*   **無說服式對比句型**：文中沒有出現「不是⋯而是⋯」、「不只⋯也⋯」、「與其⋯不如⋯」等說教式 AI 句型，表達自然平穩。

### 2. 禁用詞與少用詞掃描
*   **內文實查結果**：**100% 符規**。
    *   主體文章內 **零** 禁用詞（無「最頂、超值、保證滿意、CP值、佛心、便宜又大碗、快私訊」等）。
    *   主體文章內 **零** 少用字（無「精緻、質感、用心、客製化」等）。
*   **自動化指令偽陽性警報（False Positive Report）**：
    *   執行 `seo_qa_checker.py` 時，腳本回報了「出現禁用詞：『超值』x 1、『CP值』x 1」的錯誤（得分為 70 分）。
    *   **原因分析**：這是因為草稿結尾的 `<!-- CHECKER NOTE: -->` 註解塊中，包含了自我檢查說明 `[ ] 無禁用語（超值/保證/精緻×多/CP值）`。QA 腳本以常規方式掃描全文（含註解），因而誤判。
    *   **結論**：草稿文章本體並無違規，在實際發布（過濾掉註解）後，即可完全通過品牌語氣的確定性測試。

---

## (c) 6 盲點逐項檢查

草稿針對 SEO 規範中強制的「6 盲點」均進行了覆蓋：

| 盲點項目 | 草稿覆蓋位置 | 具體寫作內容與符合度 | 評定 |
| :--- | :--- | :--- | :---: |
| **1. 肖像隱私** | FAQ 5、正文第四段 | 提醒 Drive 照片若有貴賓清晰正面，需模糊化或確認授權後再公開；建議優先選用食物特寫、桌面全景或背影畫面。 | **PASS** |
| **2. 禁帶外食/清潔費** | FAQ 6、正文第四段 | 提醒行政/HR 在會議中心、飯店或展場舉辦活動時，需提前確認場地禁帶外食、清潔費及進場/貨梯時間規定，以防報價與動線衝突。 | **PASS** |
| **3. 飲食禁忌** | FAQ 4 | 針對全素、無麩質、過敏及個人忌口給予具體建議：分盤獨立標示、分區、或使用單獨餐盒，並提醒過敏原交叉接觸風險。 | **PASS** |
| **4. 超時撤場費** | FAQ 7、正文第三段 | 預算拆解表中明列「超時撤場費」為可能追加費用；FAQ 解釋其與現場人力、等待時間、場地管制有關，建議報價階段即先確認。 | **PASS** |
| **5. 色彩 visual-spec** | CHECKER NOTE 註解 | CHECKER NOTE 明確引用了 [maplab-visual-spec.md](file:///Users/pagemacmini/maplab-ai-handbook/skills/maplab-visual-spec.md) 中的標準 B2B 企業色彩配置：**深橄欖 `#3A3A2E`** 作主文字、**暖米 `#EDE5D8`** 作區塊底、**鼠尾草綠 `#8FA68E`** 作標籤提示色。 | **PASS** |
| **6. Crawl Budget / Redirect** | FAQ 8 | 正確指明為避免與企業茶會或費用頁 cannibalize，定位需為 buyer role guide。若日後需要整併，應採「單步驟 301 重定向」直接導向 canonical 頁，避免 Redirect Chain（多跳）消耗 Google 抓取配額，並同步更新內鏈。 | **PASS** |

---

## (d) Alt 文案

*   **Alt 格式檢查**：草稿中建議的兩張圖片 Alt 文案為：
    *   精選圖 alt：`台南企業茶會外燴—會議點心與飲品分區`
    *   內文圖 alt：`台南商務會議外燴—長桌茶點與器皿陳列`
*   **符合度**：
    *   均符合 **A式標準** (`台南{場景}外燴—{具體描述}`)。
    *   精準嵌入「台南」與「外燴」核心關鍵字，且無過度堆疊，描述與 H2 段落內容（預算拆解、動線分流）高度相關。

---

## (e) 內鏈安全

*   **無 404 禁連連結**：草稿完全避免了 [seo-keyword-map.md](file:///Users/pagemacmini/maplab-ai-handbook/docs/seo-keyword-map.md) §4 羅列的 7 個 404 舊 slug（如 `catering-corporate-tainan` 等）。
*   **占位格式安全**：所有內部連結皆使用 `[INTERNAL_LINK_RECHECK_REQUIRED: slug]` 包裹，確保上線驗證前不會直連未確認之 slug。
    *   `[INTERNAL_LINK_RECHECK_REQUIRED: corporate-catering-tainan]` (指向 ID 586 - 已驗證 live)
    *   `[INTERNAL_LINK_RECHECK_REQUIRED: tainan-corporate-catering-cost]` (已驗證 live_referenced)
    *   `[INTERNAL_LINK_RECHECK_REQUIRED: corporate-tea-party-desserts]` (指向 ID 924 - 已驗證 live)
    *   `[INTERNAL_LINK_RECHECK_REQUIRED: line-official]` (CTA 專用安全內鏈)

---

## (f) 補盲點（買家痛點進階建議）

雖然草稿已完整覆蓋基本 6 盲點，但若想讓本篇作為 **行政/HR 實用送審指南** 的威力最大化，建議在實際上線前補充以下細節（免改動現存草稿，直接在此記錄以利後續上線微調）：

1.  **核銷與財務 compliance（B2B 痛點）**：
    *   HR 和行政在向主管報帳時，最在乎發票格式。建議在詢價 FAQ 1 中，明確提示 MAPLAB 可以提供 **「三聯式統一發票」（含 5% 營業稅拆計）**，並可配合 corporate 開戶與月結/預支流程，主管審預算時對此點極為敏感。
2.  **起訂量（Minimum Order Value）門檻**：
    *   行政窗口常需要承辦 10 - 20 人的微型小會議。建議增設「起訂人數/起訂金額」的概略說明（例如：南科或台南市區是否設有運費或最低消費門檻），避免 HR 興沖沖送審後發現不符外燴起訂門檻。
3.  **場勘與菜單確認時程（Timeline）**：
    *   企業送審通常需要時間。建議給予 HR 一個送審時程參考（如：*活動前 14 天送審 brief、活動前 7 天確認最終人數與素食比例*），讓行政窗口在內部推動流程時有時間表可循。

---

## (g) 綜合結論

### **綜合判定：PASS（通過審查，建議直接排程上線）**

*   **判定理由**：
    1.  文章在 SEO 主次關鍵字、標題佈局、首段密度上均 100% 符規。
    2.  對外文案完全無禁用詞或少用詞，品牌語氣與 B2B 窗口痛點深度契合。
    3.  6 盲點（肖像、清潔費、素食過敏、超時費、色彩色碼、Redirect配額）均透過 FAQ 或 Checker Note 獲得完全覆蓋。
    4.  QA 腳本之 Exit Code 2（Failure）屬於 CHECKER NOTE 註解文字觸發的 false positive，不影響文章發布主體之合規性。

*   **後續執行建議**：
    1.  **確認 live 連結**：上線前，將 `[INTERNAL_LINK_RECHECK_REQUIRED]` 中的預留 slug 在 WordPress 後台逐一校對為真實 url。
    2.  **套用色彩系統**：通知視覺與前端排版人員，於發布此文時套用註解中所列之商務色票（深橄欖 `#3A3A2E`，暖米 `#EDE5D8`，鼠尾草綠 `#8FA68E`）。
