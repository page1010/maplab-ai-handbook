# Investment OS 全功能檢討 + Goal-Signal-Decision-Review 複利循環方案

版本：v1.0 | 建立：2026-07-07 | 狀態：**方案定案，待 Owner 核准後排入 Investment OS B1-B4 任務卡執行**
維護：B1（決策整合）+ Codex/Antigravity（唯讀評審）
評審紀要：`workbook/reviews/JOB-B1-INVESTOS-TRIO-REVIEW-20260707/decision_summary.md`
紅線：本文件全程不下單、不建模擬單、不給個股買賣建議；檢討對象是系統功能與決策輔助結構。

---

## 0. 背景

Owner 原話：「把 invest os 優化也比照辦理，把每個功能拿出來檢討，從使用者需求出發到發送的格式與內容到底可以輔助做出什麼決策，再到延伸尋找新策略到 dashboard，以 goal 的複利循環跑起來。」

比照 SEO 三人小組流程：Claude/B1 決策整合，Codex + Antigravity 唯讀評審，紅線不變。

---

## 1. 現有功能盤點（20 個已驗證使用者可見輸出）

盤點方法：Explore agent 系統性抽樣讀取 `/Users/pagemacmini/Documents/New project/` 的 `reports/`、`scripts/`、`app/`、`config/` 等目錄，對每個功能讀取最新 1-2 份實際輸出檔驗證內容（非只看程式碼猜測）。完整逐項細節見 `workbook/reviews/JOB-B1-INVESTOS-TRIO-REVIEW-20260707/inventory_raw.md`。

### 按 Owner 五大判斷維度分組

| 維度 | 功能 | 使用者需求 | 目前格式與內容 | 實際能輔助的決策 | 缺口 |
|---|---|---|---|---|---|
| **左側** | 左側敘事候選（`reports/left_side_narratives/`） | 找世界觀/終局故事+預期差+小部位非對稱下注的候選 | L-Score候選表，含entry/stop/RR，明列缺資料（P/E、月營收未載入） | 左側觀察候選（非結論） | 更新頻率不穩定（週1-3次非每日），Antigravity：容易讓 Owner 暴露於用過期數據決策的風險 |
| **右側** | 股期開盤戰術（`reports/stock_future_order_plan/`） | 右側三碼（試單/回測/動能）確認、進出場時機 | TXF/MXF regime、觸發點、停損 | 期貨開盤戰術執行 | **IOS-MOMENTUM「每日動能PM簡報/Top3研究」registry宣稱存在，本次盤點找不到獨立近期輸出檔**——只有Telegram按鈕入口，兩位評審均點名此為「決策資訊幻覺」風險 |
| **風控** | 曝險帳本+死亡清單（`state/exposure_ledger.md`）、盤後風控、實單哨兵 | regime判斷/降槓桿/1R/總曝險/集中度 | 跨帳戶曝險、4條生存SOP、槓桿1.27x、最壞情境回撤、Quad-Sell四指標賣出警示 | 風控決策的完整輸入 | **兩位評審一致認定是全系統最強維度**，無重大缺口 |
| **籌碼** | 籌碼快報 | 外資/投信/自營商是否同向 | TX三大法人期貨買賣超+全市場融資融券餘額，每日18:30 | 籌碼確認 | Codex：需要補「金額vs股數、資料日期、法人是否同向、與價格動能是否衝突」的明確標註 |
| **新聞** | 富途即時新聞/報價、市場事件島 | 事實/推論/缺資料/下一步分層判讀 | 官方API唯讀news/quote（純on-demand無排程）、事件寫入DB無獨立報告 | 原始素材 | **兩位評審一致認定偏弱**——尚未穩定轉成 Owner 可讀的事實/推論/缺資料判斷卡，目前只是 raw input |
| **平台/治理** | Telegram操控員、Dashboard(8分頁)、財經早報v2、夜間進度簡報、影子教練、系統真相地圖/生成器、守夜人巡查、模擬研究訊號帳本、量化資源橋接 | 入口整合、系統健康、研究品質追蹤 | 財經早報有「昨日校準覆盤」機制；Dashboard首屏已改「今天可不可以動+誰負責+下一步」三問 | 系統可用性、研究品質追蹤 | **守夜人（nightwatch）最新報告 2026-06-02，停擺超過一個月**；Codex/Antigravity均指出Dashboard/Telegram本身「偏入口與治理，不等於決策輔助」，不要跟決策層混為一談 |

### ⚠️ 最大缺口：世界觀/終局層完全空白

Owner 四層篩選框架的**第一層**（世界觀與終局資格——這個產業是否處於三年以上大趨勢、是否有十倍股結構、AI基礎設施/機器人/低軌衛星/功率半導體這類終局題材）在 20 個盤點到的輸出裡，**沒有一個是專門服務這一層的**。IOS-ALPHA（跨源共振）偏事件異常偵測，IOS-MACRO偏regime/現金水位判斷，都不是「終局題材發現」。

**兩位評審原話**：
- Codex：「這不是多做一份宏觀報告，而是 Owner 四層篩選的第一層缺席，後面的左側、右側、籌碼、新聞都會變成事件追逐。」
- Antigravity：「這是致命的系統級盲點...沒有第一層的宏觀敘事錨定，系統產出的左/右側訊號將失去靈魂。」

### 已知系統缺口（來自 `pitfalls.md` 真實錯誤紀錄，非猜測）

- **錯誤184（2026-06-26）**：launchd job exit=0 不代表資料真的更新——FRED API key 未設定，總經利率/匯率資料靜默停在舊日期，job本身卻顯示成功。
- **守夜人本身停擺**（本次盤點發現）：連「系統健康監控」這個監控層都沒人在看它自己健不健康，形成監控的監控真空。

---

## 2. Goal-Signal-Decision-Review 複利循環設計（三人小組整合版）

### 為什麼現有循環不夠

系統目前有兩種循環，但都不是 Owner 要的：

1. **B1-B4系統維護循環**（`invest-os-b-role-recursive-self-improvement.md`）：B4偵測→B2驗證→B1修復→B3保存→下一輪改善。這是「系統健不健康」的循環，不是「投資決策對不對」的循環。
2. **財經早報的「昨日校準覆盤」**：記錄判斷vs結果的誤差，但只在單一報告內，沒有累積成長期趨勢，也沒有「目標」可以對照。

**真正缺的環節**：沒有任何地方定義「這一季/這一年的投資目標是什麼」，也就沒辦法回頭問「這個訊號/決策，離目標更近還是更遠」。

### 四環節設計（採納三人小組共識修訂版）

```
① 目標設定（新增，三分類，機器可讀 schema 而非長文）
   投資目標拆三類，避免變成「第21個沒人看的輸出」（Codex 警語）：
   - 風控目標：最大回撤、現金/曝險區間、集中度上限
     → 直接連結 exposure_ledger.md 既有欄位，不重新發明（Antigravity：程式碼化才有強制力）
   - Thesis 目標：本季只驗證 1-2 個終局假設（例如「AI infra 今年是否進入主升段」），
     每個假設有明確的證實條件與證偽條件
   - 流程目標：哪些訊號品質要改善（例如資料新鮮度、來源分層、右側失敗條件完整率）
   → investment_goals.md（一頁式，人工填寫但欄位結構固定）

② 訊號（已存在，串接既有20個輸出，不新增第21個）
   左側/右側/籌碼/新聞/風控訊號持續產生，可選擇性標註 goal_tag
   **允許 no_goal_match / radar_only**（Codex 提醒：不能強迫每個訊號都掛目標，
   否則雜訊會污染敘事，變成事後合理化的工具）

③ 決策（部分存在，財經早報+Telegram已有部分）
   新增「決策紀錄契約」（Codex 提案）：觀察、等待、排除、降低信任，都算決策，
   不是只有下單才算。每筆記錄：對應目標／訊號來源／判斷類型／預期驗證時間／
   失效條件／資料可信度

④ 覆盤 + 修正目標（三層節奏，取代原案單一季度週期）
   - **週度**：資料新鮮度／訊號品質檢查（Codex：對抗 stale decision 需要高頻）
   - **月度**：風控配比／1R執行率檢查（Antigravity：配比變化比 thesis 快，季度太慢）
   - **季度**：thesis 證實／證偽 + 目標調整（世界觀層變化本來就慢，季度合理）
   → quarterly_goal_review.md 回頭修正①的目標設定，形成真正複利
```

### Dashboard 呈現（排在最後一步，見下方分階段順序）

在既有8個工作流分頁之外，加一個「目標」分頁，首屏顯示：本季目標 vs 目前實際曝險/現金水位的落差、正在驗證的終局假設清單與各自的訊號累積進度。**不在本輪設計介面細節**，留給屆時的 B1 Builder 任務卡。

---

## 3. 分階段執行清單（兩位評審給出完全相同的第一步，無分歧）

> 兩位評審一致原話：Codex「如果先建 goal file 或 goal_tag，會把 stale data 包裝成很漂亮的複利循環，反而更危險」；Antigravity「nightwatch 停擺一個月，系統處於不知道自己健不健康的盲目狀態」。**第一步不是建目標文件，是先讓資料可信。**

| Phase | 內容 | 產出 | 前置條件 |
|---|---|---|---|
| **Phase 0** | 恢復 nightwatch / freshness gate，範圍窄：只回答「哪些資料真的新、哪些 job 只是 exit=0、哪些輸出不可用」 | `reports/nightwatch/latest.md` 恢復每日更新；順便排查錯誤184同類的「job成功但資料未更新」靜默失敗 | 無（可立即開始） |
| **Phase 1** | 一頁式 `investment_goals.md`：本季曝險目標、最大回撤、1-2個thesis、證實/證偽條件（三分類：風控/thesis/流程） | `investment_goals.md` v0 | Phase 0 完成（資料可信後才有意義設目標） |
| **Phase 2** | 只接 2 個 pilot：財經早報 + 曝險帳本加 goal/freshness 對照，**不要一次改20個輸出** | 財經早報/曝險帳本新增「本季目標對照」區塊 | Phase 1 完成 |
| **Phase 3** | 補世界觀/終局層：做成「thesis registry + evidence ladder」，**不是每日長文** | 新的 thesis registry 文件（一次性/低頻更新，不進日報節奏） | 可與 Phase 2 並行 |
| **Phase 4** | 決策紀錄契約落地：觀察/等待/排除都要留紀錄 | 決策記錄 schema + 至少 1 個現有輸出（建議財經早報）先試用 | Phase 2 完成 |
| **Phase 5** | Dashboard 目標分頁 | 新增「目標」nav_mode | Phase 1-4 都跑過至少一輪覆盤週期後才做，避免把未驗證的流程視覺化 |

**明確排除本輪範圍**：右側動能（IOS-MOMENTUM）獨立報告是否真的需要重建、新聞層是否需要新開發一個「事實/推論/缺資料」轉換器——這兩項是本次盤點發現的真缺口，但屬於「補現有維度」而非「複利循環」本身，建議另開 Investment OS 任務卡處理，不塞進本方案。

---

## 4. 與現有文件的關係

- Owner 判斷框架來源：`projects/b1-investment-os-owner-persona-canonical.md`、`projects/b1-investment-logic-bridge.md`
- B1 跨專案治理發現（本次驗證仍然成立）：`projects/b1-cross-project-governance-advisor.md`（「Investment OS 缺的是治理外殼，不是功能」——本次盤點補充：治理外殼裡最關鍵的一塊 nightwatch 本身也停擺了）
- B1-B4 系統維護循環（不同於本方案的投資目標循環）：`projects/invest-os-b-role-recursive-self-improvement.md`
- 角色 registry（17 角色設計）：`/Users/pagemacmini/Documents/New project/config/investment_os_role_registry.json`
- 評審紀要：`workbook/reviews/JOB-B1-INVESTOS-TRIO-REVIEW-20260707/`
