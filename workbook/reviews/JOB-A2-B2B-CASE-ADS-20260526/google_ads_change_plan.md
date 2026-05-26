# Google Ads Change Plan

日期：2026-05-26
狀態：proposal only
來源：`reports/google_ads_chrome_round_001.md`

## Guardrails

- 不直接修改 Google Ads。
- 不新增、不暫停、不刪 keyword。
- 不改 final URL / budget / bid / conversion。
- 本檔只作 Owner/A3 審核前的結構提案。

## Diagnosis

目前 13 個 phrase match keywords 全部在同一組：

`Campaign 4：高意圖搜尋_南台灣外燴 / 廣告群組 1`

問題不是「沒有投 To B」，而是不同搜尋意圖混在一起：

- 會議茶點 / 研討會
- 開幕茶會 / 辦公室
- 企業 / 品牌 / 公關
- 婚禮 / 週歲等 To C

keyword row 的 `最終到達網址` 欄都顯示 `—`。這不等於完全沒有 final URL，但表示下一輪必須檢查 ad / ad group level final URL，不能假設每個搜尋意圖已導到正確文章。

## Proposed Ad Group Map

| Current keyword | Current status | Proposed action | Proposed ad group | Recommended final URL | Reason |
|---|---|---|---|---|---|
| `"台南研討會餐點"` | 搜尋量偏低 | Move later | 會議茶點 / 研討會 | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | 搜尋意圖明確，需用成大/校園/研討會案例補 landing proof |
| `"台南會議茶點"` | 符合資格 | Move P1 | 會議茶點 / 研討會 | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | To B 意圖清楚，適合搭配會議茶點案例段 |
| `"台南茶會點心"` | 符合資格 | Move P1 | 會議茶點 / 開幕茶會 cross-test | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | 字面較泛，可先導會議茶點，也可另測開幕茶會 |
| `"台南診所開幕茶會"` | 搜尋量偏低 | Move later | 開幕茶會 / 辦公室 | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | 開幕意圖明確，但需院所/醫療案例支撐 |
| `"台南開幕茶會"` | 符合資格 | Move P1 | 開幕茶會 / 辦公室 | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | 第一波最乾淨的開幕搜尋意圖 |
| `"台南辦公室外燴"` | 搜尋量偏低 | Move later | 開幕茶會 / 辦公室 | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | 辦公室開幕與企業據點案例可補強 |
| `"台南企業外燴"` | 搜尋量偏低 | Keep / move | 企業 / 品牌 / 公關 | `https://www.maplabkitchen.com/corporate-catering-tainan/` | 企業主入口，適合做 umbrella keyword |
| `"台南品牌活動外燴"` | 搜尋量偏低 | Move later | 企業 / 品牌 / 公關 | `https://www.maplabkitchen.com/brand-esg-catering-service/` | 品牌活動意圖明確，需 ESG/論壇案例補 landing proof |
| `"活動公司 外燴 配合"` | 搜尋量偏低 | Move later | 企業 / 品牌 / 公關 | `https://www.maplabkitchen.com/brand-esg-catering-service/` | B2B partner 型搜尋，文案需寫「可配合活動公司」 |
| `"公關公司 茶會 配合"` | 搜尋量偏低 | Move later | 企業 / 品牌 / 公關 | `https://www.maplabkitchen.com/press-conference-catering/` | PR / media event 意圖，建議導記者會或品牌活動頁 |
| `"台南 醫院活動 茶會"` | 搜尋量偏低 | Move later | 會議茶點 / 院所活動 | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | 需補院所/機構活動案例；可先不做第一波 |
| `"台南週歲派對外燴"` | 搜尋量偏低 | Park | To C 暫放 | 待第二波 party landing | 非本輪 To B 主線 |
| `"台南婚禮外燴"` | 符合資格 | Park | To C 暫放 | 待第二波 wedding / private event landing | 雖符合資格，但非本輪 To B 主線 |

## First Proposal Batch

先只提案三組，不動帳戶：

1. `開幕茶會 / 辦公室`
   - `"台南開幕茶會"`
   - `"台南診所開幕茶會"`
   - `"台南辦公室外燴"`
   - URL: `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/`

2. `會議茶點 / 研討會`
   - `"台南會議茶點"`
   - `"台南研討會餐點"`
   - `"台南茶會點心"`
   - URL: `https://www.maplabkitchen.com/corporate-tea-party-desserts/`

3. `企業 / 品牌 / 公關`
   - `"台南企業外燴"`
   - `"台南品牌活動外燴"`
   - `"活動公司 外燴 配合"`
   - `"公關公司 茶會 配合"`
   - URL split:
     - umbrella: `https://www.maplabkitchen.com/corporate-catering-tainan/`
     - brand/ESG: `https://www.maplabkitchen.com/brand-esg-catering-service/`
     - PR: `https://www.maplabkitchen.com/press-conference-catering/`

## Ad Copy Direction

| Proposed ad group | Headline direction | Proof needed before launch |
|---|---|---|
| 開幕茶會 / 辦公室 | 台南開幕茶會、辦公室開幕餐點、企業開幕接待 | AMD / 東京威力 / 興達 / 家居設計案例段與圖 |
| 會議茶點 / 研討會 | 台南會議茶點、研討會 Coffee Break、校園講座點心 | 成大 / 長榮 / 機構案例段與圖 |
| 企業 / 品牌 / 公關 | 企業活動外燴、品牌活動茶會、公關活動餐點 | 國泰 / 賓士 / 美麗代言人 / 文化場館 proof |

## Owner Approval Needed Before Any Ads Change

- 是否允許把 To C keyword 暫放或移出本輪評估。
- 是否允許拆 ad group。
- 是否允許設定 ad/ad group final URL 到上述 live URLs。
- 是否保留低搜尋量 keywords 作長尾測試。
