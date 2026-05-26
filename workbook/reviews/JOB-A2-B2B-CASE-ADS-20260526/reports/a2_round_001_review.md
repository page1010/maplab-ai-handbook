# A2 Round 001 Review

日期：2026-05-26
管理方：A2 搜尋流量作戰部

## 已驗證事實

- Antigravity 已用 `Gemini 3.1 Pro (High)` 執行，並輸出 `reports/antigravity_round_001.md`。
- Antigravity 只完成 public live URL check：7 個 To B front-end URLs 皆為 HTTP 200。
- Antigravity 無登入 cookie，無法進 WordPress admin / Google Ads / Meta Ads UI。
- A2 已用 Chrome 登入狀態補做 Google Ads readonly check，輸出 `reports/google_ads_chrome_round_001.md`。
- Google Ads account `844-336-3178` 可進入；目前 13 筆 keyword 都在同一個 `Campaign 4：高意圖搜尋_南台灣外燴 / 廣告群組 1`。
- Google Ads keyword row 的 final URL 欄目前均顯示 `—`。
- A2 已用 Chrome 補做 Meta Ads readonly check，輸出 `reports/meta_ads_chrome_round_001.md`。
- Meta Ads Manager 目前導到 onboarding / 引導式啟用流程，不能由 A2 代點 `立即開始`。
- A3 worker 已交付 `reports/a3_meta_round_001.md`，但 detailed targeting 仍需 UI check。
- A4 worker 已交付 `reports/a4_assets_round_001.md`。
- 每小時巡檢 automation 已建立：`a2-b2b-case-ads-loop-check`。

## 合理推論

- 第一波 To B 應先做 `Real Estate VIP Reception`、`Opening Tea Party`、`Brand PR ESG Event` 三組。
- Google Ads 目前最大問題不是缺 keyword，而是多種搜尋意圖混在單一 ad group，landing page 無法精準。
- Meta 目前可先做素材與受眾假設，不應直接進投放設定。
- 酒類、外部 logo、人臉與建案模型畫面不應當第一波廣告主視覺；可先作網站 proof 或裁切後再投。

## 缺資料

- 7 個 WordPress live posts 的後台 editor id / Elementor 插入點仍未完整列出。
- Google Ads ad / ad group level final URL 尚未檢查；keyword row 顯示 `—` 不等於完全沒有 final URL。
- Meta 是否已有可用 business portfolio / ad account / pixel / custom audience 尚未確認。
- Owner 尚未決定外部品牌名是否可在網站內文保留，以及廣告素材是否可露出 logo。

## A2 判斷

- Antigravity 已善用，但它不具備登入態；後台事實由 A2 Chrome readonly 補位。
- 下一輪不應先改 Ads，而是產生 `proposal only` 的 Google Ads ad group / final URL restructuring plan。
- A2 已完成 `a2_case_copy_round_001.md`，可供 Owner 審稿。
- A4 下一步可依 manifest 處理 P1 素材本機輸出，不上傳、不覆蓋原圖。

## Round 002 指令

1. A2：產出 `google_ads_change_plan.md`，只做 proposal，列 keyword -> proposed ad group -> final URL。
2. A2：產出 `wordpress_update_plan.md`，只做 existing post update plan，不碰 Rank Math。
3. A4：依 `asset_conversion_manifest_round_001.csv` 先處理 P1 圖片本機 WebP/crop review output。
4. A3：Meta 維持 `Needs UI Check`，等 Owner 確認 onboarding / business portfolio 後再進 UI。

## 不做事項

- 不發布 WordPress。
- 不改 Google Ads / Meta Ads 設定、預算、keyword 或 final URL。
- 不點 Meta onboarding 的 `立即開始`。
- 不碰 Rank Math focus keyword / schema / paid UI。
- 不使用 404 planned slugs。
