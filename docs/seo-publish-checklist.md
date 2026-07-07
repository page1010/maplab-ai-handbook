# SEO 發布前閘門清單（只進不退）

版本：v1.0 | 建立：2026-07-03 | 維護：A2 / Codex
> **本清單是「會長大的防護層」**。每次抓到缺陷，必須回填為一條。任何 SEO 文章在 draft → publish 之前，必須完整跑完本清單。閘門須由**產出者以外的角色**執行（獨立驗證原則，詳見 `docs/OPERATING_CULTURE.md` 原則 2）。

自動化程度標記：🤖 = 腳本可自動跑 | 👁 = 需人眼或 Owner 確認

---

## 必過項目

### A. 內容忠實度

| # | 項目 | 自動化 | 說明 |
|---|---|---|---|
| A-1 | 發布版字數 ≥ 核准版字數 × 0.95 | 🤖 | 禁止手動搬運造成縮水；差異超過 5% 視為不符 |
| A-2 | 核准版關鍵段落指紋核對（前 500 字 + 最後 200 字 + 所有 H2/H3 標題） | 🤖 | `seo_publish_gate.py --check fingerprint` |
| A-3 | 發布版不含 CHECKER NOTE 或任何 `<!-- CHECKER NOTE ... -->` 區塊 | 🤖 | CHECKER NOTE 為內部用，不得進 WP content |

> **本次觸發缺陷（2026-07-03）**：《行政外燴推薦 HR 活動餐點規劃》HTML body 由 Codex 手動轉換，未與核准版做指紋比對；若內容縮水或段落錯位，Owner 無法立即發現。

---

### B. 連結完整性

| # | 項目 | 自動化 | 說明 |
|---|---|---|---|
| B-1 | 無任何 `[INTERNAL_LINK_RECHECK_REQUIRED` 佔位字串殘留 | 🤖 | `grep -n 'INTERNAL_LINK_RECHECK_REQUIRED'` |
| B-2 | 無直連到 404 slug（對照 `docs/seo-keyword-map.md` 的 planned_404 清單） | 🤖 | `seo_publish_gate.py --check links` |
| B-3 | CTA 區塊（LINE / 聯絡）href 不是佔位符，是真實 URL | 🤖 | 掃描 `href="/【待填` 或 `href="#"` |
| B-4 | 所有 `live_referenced` slug 已通過 WP REST 確認為 live，或已標為待確認並通知 Owner | 👁 | Owner 在發布前確認或同意暫時保留佔位 |

> **本次觸發缺陷（2026-07-03）**：`tainan-corporate-catering-cost`（`live_referenced`）和 `line-official` 在 HTML body 中以佔位形式存在，若直接 copy-paste 進 WP 發布，前台會出現壞連結。

---

### C. 資產完整性

| # | 項目 | 自動化 | 說明 |
|---|---|---|---|
| C-1 | WP 草稿有設定 Featured Image（精選圖） | 🤖 | WP REST `featured_media ≠ 0` |
| C-2 | 至少一個真實案例錨（WP media ID 可查，非 stock / 佔位圖） | 👁 | 至少 1 張已上傳且視覺核對的自有照片 |
| C-3 | 所有圖片 alt 符合 A 式格式（`台南{場景}外燴—{描述}`） | 🤖 | `grep -E 'alt="台南.{2,10}外燴—'` 數量 = img 數量 |

> **本次觸發缺陷（2026-07-03）**：HTML body 交付時未附帶精選圖或任何已上傳 media，如果 Owner 直接發布，精選圖欄位為空，GSC 可能降低卡片點擊率。

---

### D. SEO meta 欄位

| # | 項目 | 自動化 | 說明 |
|---|---|---|---|
| D-1 | slug 已設定，不含大寫/中文/底線 | 🤖 | `wp/v2/posts/{id}` → `slug` 欄位 |
| D-2 | Rank Math focus keyword 已填 | 🤖 | `meta._yoast_wpseo_focuskw` 或 `rank_math_focus_keyword` 非空 |
| D-3 | excerpt / meta description 已填（≤ 155 字元） | 🤖 | `excerpt.raw` 非空且長度合規 |
| D-4 | 首段前 110 字含主關鍵字 × ≥ 1 | 🤖 | 字串搜尋 |

---

### E. 品牌語氣（快速掃描）

| # | 項目 | 自動化 | 說明 |
|---|---|---|---|
| E-1 | 無禁用詞（超值/保證/精緻出現 > 2 次 / CP值/佛心/便宜又大碗） | 🤖 | `brand-voice-guide.md §三` 禁詞清單 |
| E-2 | 無說服式對比句型（`不是.*而是` `不僅.*更` 等） | 🤖 | regex 掃描 |
| E-3 | 無把話說死（一定/保證/最適合/絕對/唯一/最好） | 🤖 | regex 掃描 |
| E-4 | 無內部指令或策略備註殘留（「讓讀者理解…」「適合作為…案例」等） | 👁 | 最後人眼確認 |

---

### F. 食安 / 法規紅線（獨立於品牌語氣，勿與 E 類混用）

> 2026-07-07 新增：A2 回溯掃描 58 篇既有 WordPress 文章時發現 1 篇（post 698）含「無麩質」FAQ 答案，且這類食安/法規風險用詞從未被自動擋在新內容產出的關卡上（E-1 管的是行銷語氣，不是這個）。詳見 `handoff/tasks/T-A2-002-foodsafety-seo-cleanup.md`。

| # | 項目 | 自動化 | 說明 |
|---|---|---|---|
| F-1 | 無食安/法規紅線用詞（無麩質/Gluten-free/ESG 認證/SDG/醫療級/第三方認證） | 🤖 | `seo_publish_gate.py` `FOOD_SAFETY_BANNED_WORDS` 清單，來源 T-A2-002 |

---

## 執行流程

```
生成稿 (核准版)
     ↓
Codex / A2 轉換為 WP HTML body
     ↓
【獨立角色跑本清單】← seo_publish_gate.py (A-C 自動) + 人眼 (D-E)
     ↓
PASS → Owner 視覺確認 → 手動或 wp_publish_draft.py 建立 draft
FAIL → 列出缺陷清單 → 修復 → 重跑閘門
```

---

## 清單版本記錄（只進不退）

| 版本 | 日期 | 新增項 | 觸發缺陷 |
|---|---|---|---|
| v1.0 | 2026-07-03 | A-1 ~ A-3, B-1 ~ B-4, C-1 ~ C-3, D-1 ~ D-4, E-1 ~ E-4 | 內容忠實度未核對；佔位連結未解析；精選圖未附帶 |
| v1.1 | 2026-07-07 | F-1（食安/法規紅線用詞，獨立於 E-1 品牌語氣禁用詞） | T-A2-002 回溯掃描發現既有文章（post 698）含「無麩質」，且此風險從未被自動擋在新內容產出關卡上 |
