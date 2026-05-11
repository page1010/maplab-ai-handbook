# MAPLAB A2/B2B Case Inventory

版本：v1.0
建立：2026-05-11
狀態：A2 first batch running

> 這份清單不是要再生 8 個泛用主頁，而是先把既有架構裡真正能成交的 B2B 場景補齊。
> 原則：先對齊 repo 與 live site 的既有頁面，再用 IG / Drive / 報價單 / 照片日期補案例。

## 方向鎖定

1. 不再先寫價位。
2. 不再先擴新頁，除非真的缺頁而且有證據。
3. 先補 B2B 缺口，家庭 / 婚禮 / 宗教場景先降到第二批。
4. 每個案例必須能回到至少兩個來源：IG、Drive 報價單、照片日期、素材截圖。
5. 每頁先看草稿與 SEO，再用 Computer Use 最後檢查版面。

## 目前最該先做的四個 B2B 叢集

| 優先級 | 叢集 | 現有頁面 / 承接頁 | 真實來源樣本 | 本批任務 |
|---|---|---|---|---|
| 1 | 企業會議 / 茶點 / 辦公室 | `catering-corporate-tainan`, `meeting-refreshment-catering-tainan` | `2026/4/11成大會議250/60人`, `2026/3/12成大迎春/智遊科技`, `2026/4/23科林研發300/80人`, IG「會議茶點｜醫學中心國際研討會」 | 補案例段、整理真實名稱、修正內連，不新開主頁 |
| 2 | 開幕 / 品牌活動 / VIP 接待 | `opening-event-catering-tainan`, `brand-event-catering` | IG「AMD 新辦公室開幕茶會」,「清清顏開幕」,「Grand Open｜開幕茶會」,「Kia Select 原廠精選中古車展」,「賓士賞車」 | 補案例區與場景段，區分開幕與品牌活動，不互搶 |
| 3 | 學校 / 研討會 / 畢典 | `school-event-catering-tainan` | `2026/3/12成大迎春/智遊科技`, IG「長榮大學 EMBA」, IG「南臺講座茶會」, Drive「成大會議」 | 補校園案例與 FAQ，強化校方流程與大量分發說明 |
| 4 | 文化場館 / 展覽 / 建案 | 先放在 `brand-event-catering` 作支援案例 | IG「臺南美術館外燴」, IG「文學館展覽開幕」, IG「奇美博物館外燴」, IG「川御建設」 | 不先新開主頁，先當品牌活動支援案例與圖文素材庫 |

## 暫緩項目

- `catering-birthday-party-tainan`：先保留，不當本批主軸
- `catering-wedding-tainan`：婚禮頁保留，等 B2B 收斂後再補
- `religious-event-catering-tainan`：長尾支援頁，暫不優先

## 這批頁面要補的內容

每個頁面都要補這些東西：

- 真實案例區
- 事件名稱與地點
- 場景用途
- 來賓 / 人數區間
- 頁面內部連結
- Rank Math 欄位
- 圖片插槽
- 可交接給 OpenClaw 的工作包說明

## 不要寫的內容

- 價位
- 空泛的品牌讚美
- 沒有來源的「案例感」
- 會跟主頁 / 其他頁互搶關鍵字的重複段落
- 未確認的時程表內容

## 第一輪任務拆解

### Task 1 — inventory crosswalk

- 目標：建立 `IG / Drive / 相片日期 / 報價單 / page slug` 的對照表
- 輸出：`docs/a2a3/b2b-crosswalk.md`
- 驗收：每個 B2B 叢集至少 2–4 個可對應案例

### Task 2 — enterprise & meeting pages

- 目標：先修正 `catering-corporate-tainan` 與 `meeting-refreshment-catering-tainan`
- 輸出：更新後的 `draft.md`, `seo.md`, `source_bridge.md`
- 驗收：不寫價格、案例名稱具體、內連不互搶

### Task 3 — opening & brand pages

- 目標：先修正 `opening-event-catering-tainan` 與 `brand-event-catering`
- 輸出：更新後的草稿與 Rank Math payload
- 驗收：把 `AMD / 清清顏 / Kia / 賓士 / 國泰` 等案例分清楚

### Task 4 — school page

- 目標：修正 `school-event-catering-tainan`
- 輸出：更新後的草稿與案例區
- 驗收：校園、講座、畢典、EMBA 的流程說明清楚

### Task 5 — final inspection

- 目標：用 Browser / Computer Use 開啟 preview.html 一頁一頁檢查
- 驗收：圖片裁切正常、類別正確、SEO 與內連不互搶

## 可交給 OpenClaw 的一句話

> 先讀 `docs/a2a3/b2b-case-inventory.md`，再只處理第一輪 B2B 四個叢集，所有輸出都停在 draft / review，不可發布。
