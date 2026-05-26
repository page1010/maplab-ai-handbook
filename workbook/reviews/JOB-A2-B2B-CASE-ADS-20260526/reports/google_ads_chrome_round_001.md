# Google Ads Chrome Readonly Round 001

日期：2026-05-26
執行者：A2 / Codex Computer Use on Chrome
模式：只讀；未新增、未儲存、未套用、未修改任何 Google Ads 設定。

## 已驗證事實

- Chrome 已登入 Google Ads account `844-336-3178`。
- 可進入 `https://ads.google.com/aw/keywords?ocid=252396667`。
- 頁面標題：`搜尋關鍵字 - 844-336-3178 - Google Ads`。
- 日期範圍：`2026年 3月 13日 - 4月 9日`。
- 篩選器：
  - 廣告活動狀態：已啟用
  - 廣告群組狀態：已啟用、已暫停
  - 關鍵字狀態：已啟用、已暫停
- 目前表格顯示：第 1 到 13 列，共約 13 列。
- 所有可見 keyword 皆屬於 `Campaign 4：高意圖搜尋_南台灣外燴` / `廣告群組 1`。
- 目前 keyword 層級的 `最終到達網址` 欄皆顯示 `—`，表示未在 keyword row 顯示指定 final URL。

## Keyword Matrix

| # | Keyword | Match type | Campaign | Ad group | Status | Final URL shown | B2B routing note |
|---:|---|---|---|---|---|---|---|
| 1 | `"台南研討會餐點"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 應導到 `corporate-tea-party-desserts` |
| 2 | `"台南診所開幕茶會"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 應導到 `tainan-corporate-opening-tea-catering`，可另補醫療院所案例 |
| 3 | `"台南品牌活動外燴"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 應導到 `brand-esg-catering-service` |
| 4 | `"台南週歲派對外燴"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 偏 To C，先不放 B2B 第一波 |
| 5 | `"台南開幕茶會"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 符合資格 | `—` | P1，應導到 `tainan-corporate-opening-tea-catering` |
| 6 | `"台南會議茶點"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 符合資格 | `—` | P1/P2，應導到 `corporate-tea-party-desserts` |
| 7 | `"台南企業外燴"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 應導到 `corporate-catering-tainan` |
| 8 | `"活動公司 外燴 配合"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 可導 `brand-esg-catering-service` 或 `press-conference-catering` |
| 9 | `"公關公司 茶會 配合"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 可導 `brand-esg-catering-service` / `press-conference-catering` |
| 10 | `"台南 醫院活動 茶會"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 應導到 `corporate-tea-party-desserts`，但需醫療/院所案例支撐 |
| 11 | `"台南婚禮外燴"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 符合資格 | `—` | 偏 To C，先不放 B2B 第一波 |
| 12 | `"台南茶會點心"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 符合資格 | `—` | 可導 `corporate-tea-party-desserts` 或 `tainan-corporate-opening-tea-catering` |
| 13 | `"台南辦公室外燴"` | 詞組比對 | Campaign 4：高意圖搜尋_南台灣外燴 | 廣告群組 1 | 不符合資格 / 搜尋量偏低 | `—` | 應導到 `tainan-corporate-opening-tea-catering` 或 `corporate-catering-tainan` |

## A2 Interpretation

- 目前 Google Ads 是「一個 ad group 混收多種意圖」：會議、開幕、品牌、公關、醫院、婚禮、週歲、辦公室都在同一組。
- 這會讓廣告文案與 landing page 很難精準；下一輪應先做 `proposal only`，不要直接改設定。
- 第一波 B2B 建議把 To C keyword 暫放，不拿來評估企業案例頁成效。
- Keyword row final URL 目前未顯示指定 URL，下一輪需檢查 ad group / ad level final URL，確認是否全都導到同一頁。

## Recommended Google Ads Structure Proposal

| Proposed ad group | Keep / move keywords | Recommended landing page |
|---|---|---|
| 會議茶點 / 研討會 | `"台南研討會餐點"`, `"台南會議茶點"`, `"台南茶會點心"` | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` |
| 開幕茶會 / 辦公室 | `"台南開幕茶會"`, `"台南診所開幕茶會"`, `"台南辦公室外燴"` | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` |
| 企業 / 品牌 / 公關 | `"台南企業外燴"`, `"台南品牌活動外燴"`, `"活動公司 外燴 配合"`, `"公關公司 茶會 配合"` | `https://www.maplabkitchen.com/brand-esg-catering-service/` or `https://www.maplabkitchen.com/corporate-catering-tainan/` |
| To C 暫放 | `"台南週歲派對外燴"`, `"台南婚禮外燴"` | Not first-wave B2B; route later to party/wedding content |

## Not Done

- 未點擊任何 keyword。
- 未建立新 ad group。
- 未修改 final URL。
- 未下載報表。
- 未變更 budget / conversion / bid / status。
