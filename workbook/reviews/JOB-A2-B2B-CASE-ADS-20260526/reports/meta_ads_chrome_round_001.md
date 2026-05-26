# Meta Ads Chrome Readonly Round 001

日期：2026-05-26
執行者：A2 / Codex Computer Use on Chrome
模式：只讀；未點擊啟用流程、未建立廣告、未建立商家資產管理組合、未修改任何 Meta 設定。

## 已驗證事實

- Chrome 可開啟 `https://business.facebook.com/adsmanager`。
- 實際轉到：`adsmanager.facebook.com/adsmanager/onboarding?act=2441634989673207&nav_source=no_referrer#`
- 頁面標題：`廣告管理員 - 引導式啟用流程`。
- 可見文案：
  - `透過廣告管理員觸及理想受眾`
  - `開始設定以刊登廣告`
  - `開始建立你的第一則廣告`
  - 按鈕：`立即開始`
  - 區塊：`是否須要先建立商家資產管理組合？`
  - 按鈕 / link：`建立商家資產管理組合`

## A2 Interpretation

- 目前這個 Chrome 登入狀態可進 Meta Ads Manager onboarding surface，但沒有直接進入既有 campaign / ad set table。
- 因為畫面停在引導式啟用流程，不應由 A2 或 Antigravity 點 `立即開始`，那可能觸發帳戶設定或第一則廣告建立流程。
- A3 的 detailed targeting 規劃仍必須維持 `Needs UI Check`，不能硬說哪些 interest 一定可選。

## Missing Data

- 是否已有可用的 Meta ad account / business portfolio。
- 是否已有 pixel 或 website custom audience。
- Detailed targeting / Advantage+ audience suggestion 的實際可選項。
- 是否可建立或使用 campaign / ad set / ads table。

## Next Command

如果 Owner 要走 Meta 第一波，下一輪應先由 A3 / Owner 只讀確認：

1. 是否已有 business portfolio。
2. 是否已有 ad account，不需要重新 onboarding。
3. 是否已有 pixel / website custom audience。
4. 若必須完成 onboarding，Owner 需親自決定，不由 A2 代點。

在此之前，Meta 規劃維持為受眾假設與素材路線，不做投放設定。
