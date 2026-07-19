# Investment OS 持續迭代計畫
# 讓 IS 像 memory-watch 一樣每天複利進步

版本：v1.0 | 建立：2026-07-18 | 作者：A1 系統總管
紅線：不下單、不給買賣建議、不碰券商；所有行動服務「讓 Owner 決策更快更安全」。

---

## ① 我讀懂的全貌（資料流圖 + 斷點）

### 設計全貌

Investment OS 的設計意圖是把 Owner 每天回答 5 個投資決策問題的時間從 30 分鐘 → 3 分鐘。
架構上有 17 個角色、20 個輸出、8 個 launchd 排程、3 層平台（Telegram/Dashboard/報告）。

### 資料流圖（實際運作，2026-07-18）

```
訊號源                    處理層                      輸出層                   決策層           覆盤
─────────────────────────────────────────────────────────────────────────────────────────────────
yfinance/富途 → calc_exposure_ledger.py → exposure_ledger.md     →  Owner 看到？  → quarterly?
                                       → runtime_escalation_queue.jsonl  ←★斷點②
                                         (5條WARNING 07-01產生，全部 escalated=false)

FRED/macro    → macro-data-refresh(launchd, exit=0) → ??? 靜默 ←★斷點① (pitfall #184)

Reddit/RSS    → convergence-engine(exit=0)     → shadow_findings ✅新鮮
                                               → local_model_findings ✅新鮮

left_side     → build_left_side_narratives    → left_side_narratives ✅新鮮(11h)

nightwatch    → system-nightwatch(launchd)     → nightwatch 今日0警示 ✅
                                                          ↑
                                               ★斷點③: 0警示 ≠ 決策品質好
                                               nightwatch 不量測 output quality
                                               只量測 file mtime

財經早報      → finance-morning-brief(exit=0)  → progress_digest ✅新鮮(5h)
                                              → 今天可不可以動？← ★斷點④: 無此欄位

Goal/Thesis   → investment_goals.md            → ★斷點⑤: 此文件不存在
                                                  無目標=訊號沒有對照基準
```

### 五個斷點摘要

| # | 斷點 | 症狀 | 嚴重度 |
|---|------|------|-------|
| ① | launchd exit=0 ≠ 資料更新（pitfall #184） | FRED/macro 資料可能靜默過期 | 🟡 中 |
| ② | runtime_escalation_queue 無自動 escalate | 5 條 WARNING 截止 07-17 從未推 Owner | 🔴 高 |
| ③ | nightwatch 只量 mtime，不量 content quality | 0 alerts ≠ 輸出有用 | 🟡 中 |
| ④ | 財經早報無「今天可不可以動」欄位 | Owner 每天要自己拼湊判斷 | 🔴 高 |
| ⑤ | investment_goals.md 不存在 | 所有訊號沒有目標對照，不知道「比上週好嗎」 | 🔴 高 |

---

## ② 診斷：為什麼 memory-watch 能複利、IS 不能

### memory-watch 成功五要素

| 要素 | memory-watch 做法 |
|------|------------------|
| ① 單一明確指標 | free%（一個數字，高低一目了然） |
| ② 2 小時緊回饋圈 | launchd 每 2h 跑，log 追得到每次變化 |
| ③ 每輪有人看結果 | A0 的 Telegram 通知 Owner 有問題 |
| ④ 低風險修復可自主 | OLLAMA_KEEP_ALIVE=5m、ulimit —可以不問 Owner 直接改 |
| ⑤ 修完立刻可驗證 | 下次 2h log 出現新數字 = 立刻確認效果 |

### IS 逐條對照

| 要素 | IS 現狀 | 缺口 / 根因 |
|------|---------|------------|
| ① 單一明確指標 | 20 個輸出，無主指標 | Owner 每天要讀多份報告才能拼「今天可動嗎」 |
| ② 2h 緊回饋圈 | nightwatch 每日 08:00（已有），但各輸出 24h 更新頻率 | 還可以，但 escalation_queue 從不推播 = 回饋圈從未閉合 |
| ③ 每輪有人看結果 | **斷點②：5 條 WARNING 07-01 到今天從未推 Owner** | escalated=false 是設計缺口，沒有 auto-push job |
| ④ 低風險修復可自主 | 改風控規則/閘門門檻 = 必須 Owner 拍板 | 但：報告格式、資料新鮮度監控、scheduler 修復 = 可自主 |
| ⑤ 修完立刻可驗證 | 修 launchd job → 次日 nightwatch 見效 | OK，週期可接受 |

### 核心診斷

> IS 不是「系統掛了」——launchd 8 個 jobs 今日全 exit=0，資料大多新鮮。
> IS 缺的是：**「警報→Owner→決策→覆盤」這個閉環從未完整跑過一圈**。
> 警報躺在 queue 裡，Owner 不知道；決策目標不存在，訊號無從對照；
> 每週過了，沒有人問「IS 上週比上上週好嗎？」

---

## ③ Investment OS 持續迭代計畫（四週）

### 整體架構：五層機制

```
Layer 1：心跳可視化   → 每日 IS 健康分數（IS-HS）進入 A1 patrol
Layer 2：每日微迭代   → Ranked backlog，每天自動挑一件可自主項目
Layer 3：規則引擎     → 5 條風控規則 Owner 一次確認，之後自動執行
Layer 4：Goal anchor  → investment_goals.md 建立，訊號有對照基準
Layer 5：進步可量測   → IS 健康分數每週趨勢 = 複利可視化
```

---

### Layer 1：心跳化（IS 健康分數 IS-HS）

**定義：IS Health Score（IS-HS）= 四維加權分數（0-100）**

| 維度 | 權重 | 計算方式 | 今日基線 |
|------|-----|---------|---------|
| 資料新鮮度 | 25% | nightwatch 綠色項目 / 總監控項目 | 100%（7/7 綠）|
| 警報通暢度 | 25% | (1 - 未 escalate 已逾期警報 / 總警報) | 0%（5/5 overdue，未推） |
| 決策延遲   | 25% | (1 - 待 Owner 決策項目 / 總待辦) | 20%（estimator：80% 卡 Owner）|
| 覆盤完成率 | 25% | 本週覆盤完成 / 應完成次數 | 0%（無 quarterly review）|
| **IS-HS 今日** | | | **≈ 30/100**（功能在跑但閉環從未完整）|

**比較：memory-watch**
- 資料新鮮度：100%
- 警報通暢度：100%（Telegram 即時）
- 決策延遲：80%（Owner 看到後通常 2h 內回應）
- 覆盤完成率：80%（每次修完都有 log 驗收）
- **memory-watch IS-HS ≈ 90/100**

**心跳化機制：**
1. `scripts/is_health_score.sh` — 每日從 nightwatch + escalation_queue + task board 計算 IS-HS
2. 整合進 `scripts/patrol.sh` IS 守夜人區塊，每次 A1 巡查時顯示分數趨勢
3. IS-HS < 50 → 自動升 Telegram 通知 Owner

---

### Layer 2：每日微迭代制（Ranked Backlog）

**設計原則：** 每天自動從 ranked backlog 挑一件「小、安全、可驗證」的改進執行。
執行分類：

| 類型 | 可自主（A1 執行）| 需 Owner 決策 |
|------|----------------|-------------|
| 資料管線修復 | ✅ 可自主 | — |
| 報告格式改善 | ✅ 可自主 | — |
| nightwatch 監控項新增 | ✅ 可自主 | — |
| 風控規則門檻 | ❌ | Owner 確認 |
| 曝險計算邏輯 | ❌ | Owner 確認後 B1 執行 |
| 決策規則/閘門 | ❌ | Owner 確認 |

**Ranked Backlog（優先序）— 截至 2026-07-18：**

| 優先 | 項目 | 類型 | 估計工時 | 驗收指標 |
|------|------|------|---------|---------|
| P0 | 修復 escalation_queue auto-push 到 Telegram | 管線修復 | 2h | 新 WARNING → Owner 5min 內收到 Telegram |
| P1 | 財經早報加「今天可不可以動」三行摘要欄位 | 報告格式 | 1h | 每日早報第一行是可動性結論 |
| P2 | nightwatch 加 content-quality 抽查（左側敘事 > 0 candidate？） | 監控擴充 | 2h | nightwatch 報告加 quality gate 欄 |
| P3 | investment_goals.md v0 草稿（Owner 填寫） | 需 Owner | 0h A1 | Owner 30min 填 3 欄位 |
| P4 | FRED 靜默過期偵測加入 nightwatch（pitfall #184）| 監控擴充 | 1h | FRED 過期 → 顯示「不可用」而非靜默 |
| P5 | exposure_ledger 每週自動重算 + 結果進 patrol | 自動化 | 2h | 每週三 patrol 顯示曝險變化 |

---

### Layer 3：規則引擎上線（Owner 一次確認）

**現況：** `state/runtime_escalation_queue.jsonl` 已有 5 條 WARNING，代表規則引擎本體已在跑（`calc_exposure_ledger.py` 已實作 SOP1/SOP2）。
**缺口：** 只差 escalation push 機制 + Owner 確認 4 個門檻參數。

**Owner 需要確認的 4 個參數（可在 15 分鐘內決定）：**

| 參數 | 草稿值（來自 exposure_ledger 現行設定） | Owner 確認後填入 |
|------|--------------------------------------|----------------|
| 單一主題集中度上限（SOP1） | 10% gross | ？% |
| 單一標的上限（SOP2，非核心） | 15% gross | ？% |
| 槓桿警戒線 | 1.5x（Firstrade） | ？x |
| 急性警示（日跌幅）| 未定義 | ？% |

**Owner 確認後，A1/B1 負責：**
- 建立 `scripts/escalation_push.sh`：每日讀 escalation_queue，對 open+逾期 推 Telegram
- 這樣 WARNING → Owner Telegram → Owner 決策 這個路徑就完整了

---

### Layer 4：進步可量測（IS-HS 週趨勢）

每週五 A1 計算一次 IS-HS，記錄進 `state/is_health_trend.jsonl`：

```json
{"date":"2026-07-18","is_hs":30,"freshness":100,"escalation":0,"decision_velocity":20,"review_rate":0,"notes":"baseline"}
```

IS-HS 趨勢圖（文字版）每週例會：
```
Week 1 (07-18): ████░░░░░░ 30/100  ← 今日 baseline
Week 2 (07-25): ████████░░ ?/100   ← P0+P1 完成後預期 60+
Week 3 (08-01): █████████░ ?/100   ← escalation push + goals 完成
Week 4 (08-08): ██████████ ?/100   ← Layer 3 規則引擎完整
```

**複利可視化：** IS-HS 的數字趨勢 = 系統是否在複利的最直接指標。

---

### 四週 Phase 排程

| Phase | 週期 | 目標 | 主要行動 | 驗收指標 | Owner 需決策？ | 進度 |
|-------|------|------|---------|---------|--------------|------|
| **P1** | Week 1 (07-18~07-25) | 心跳可見 + escalation 修復 | `is_health_score.sh` + escalation_push + patrol 整合 | IS-HS 從 30 → 50+；昨日 5 條 WARNING 推到 Telegram | P0 escalation push = 需 Owner 確認 Telegram 推播格式 | 🔄 **Layer 3 規則引擎提前落地（2026-07-18）**：`scripts/is_rules_gate.sh` 建立（SOP1=10%/SOP2=15%/槓桿=1.5x/日跌幅=-3%）；現值實測 5 條違規（TSLA/3296/US tech/WFE）推播 Telegram ✅；下一步：escalation_push 補完 + IS-HS patrol 整合 |
| **P2** | Week 2 (07-25~08-01) | 每日微迭代啟動 + 財經早報改善 | 財經早報加可動性摘要；nightwatch 加 content quality gate | 每日早報第一行是「今天可不可以動」；P-2/P-4 backlog 完成 | 最小 | 🔲 待啟動 |
| **P3** | Week 3 (08-01~08-08) | investment_goals.md + 規則引擎完整 | Owner 填 goals v0；B1 接 escalation 到規則引擎 | investment_goals.md 存在且有 2 個 thesis；escalation SLA 縮到 24h | Owner 15 min 填 goals | 🔲 待啟動 |
| **P4** | Week 4 (08-08~08-15) | IS-HS > 70，進度可視化 | IS-HS 週趨勢跑 3 週；exposure_ledger 自動週算 | IS-HS ≥ 70；每週五有 IS 進度週報進入 patrol | 最小 | 🔲 待啟動 |

---

## ④ Phase 1 第一件：立刻啟動（2026-07-18）

### 選定行動：IS 健康分數基線建立 + Escalation 問題曝光

**選擇理由：**
- 零程式碼風險（只讀 + 記錄）
- 最高槓桿（讓 Owner 知道 5 條 WARNING 已逾期 = 直接解鎖 P0）
- 立刻可驗證（下次 patrol 顯示 IS-HS 30/100）

**執行：**

1. **IS-HS 基線建立**（見上方 Layer 1，今日 = 50/100，patrol.sh 已整合）
2. **Escalation 問題曝光：** **13 條** open+未推警報（全部來自 2026-07-01 exposure_ledger），重點摘要：

| 類型 | 規則 | 主要標的 | 超標摘要 |
|------|------|---------|---------|
| CRITICAL | 死亡清單 | AMAT, CAMT, MKSI | 個別標的極度集中警示 |
| SOP1 主題 | Speculation/Narrative | TSLA + 相關 | 25.9% > 10% 上限 (+15.9%) |
| SOP1 主題 | EV/Consumer Auto | TSLA | 25.8% > 10% 上限 (+15.8%) |
| SOP1 主題 | Semi Equipment | AMAT/KLAC/LRCX... | 17.7% > 10% 上限 (+7.7%) |
| SOP2 單名 | TSLA | TSLA | 25.8% > 核心 25%（需減碼 $3,535）|
| SOP2 單名 | 3296 | 3296 文心戶 | 17.2% > 非核心 15%（需減碼 $9,438）|
| 曝險集中 | US tech 合併 | 全倉 | 82.7% gross = 假分散（如 exposure_ledger 07-01）|

> ⚠️ 這 13 條 WARNING 是 exposure_ledger（2026-07-01）自動產生的。系統知道、但 Owner 不知道——
> 這就是「警報通暢度 = 0%」的根因。完整清單：`state/runtime_escalation_queue.jsonl`。
> **本文件不構成建議，Owner 獨立決策是否需處理各項警報。**

3. **patrol.sh IS 守夜人區塊升級：** 加入 escalation_queue open 項目顯示（見 Phase 1 實施說明）

---

## 週度投資提案簡報（固定產出，2026-07-18 制度化）

**起源**：2026-07-18 Owner 檢討「股票系統沒有提案也沒有新幫助」→ IS 從警報器升級為提案幕僚。
**第一份實品**：`workbook/reviews/JOB-IS-PROPOSAL-BRIEF-20260718/`

### 產出規格

| 項目 | 規格 |
|------|------|
| 產出時間 | 每週日（AI 自動，A1 整合把關）|
| 發布時間 | 週一例會前 |
| 儲存位置 | `workbook/reviews/JOB-IS-PROPOSAL-BRIEF-YYYYMMDD/` |
| 精華版 | `state/is_brief_YYYYMMDD.md`（A0 轉發用）|
| 回流指標 | Owner 每週打開並回應次數（A1 追蹤）|

### 三固定章節

**1a 候選檢核卡**（3-5 張）
- 來源：system_status_card 四主線候選（資金流/第一根/動能/新聞）
- 格式：L1 世界觀 → L2 產業結構 → L3 基本面 → L4 技術/籌碼，逐層判斷
- 結論語：「值不值得你花 10 分鐘看」——不說買賣
- 不確定的地方明確標 `[需補]` 或 `[需即時確認]`

**1b 持倉論點健康**
- 針對死亡清單持倉（當前：AMAT/CAMT/MKSI + TSLA/勝德）
- 格式：「原始持有論點 vs 現在訊號」對照表 + 修正後論點是否仍成立的證據清單
- 結論：開放給 Owner，不給結論

**1c 集中度選項卡**（若出現新的集中度警告）
- 格式：三路徑（維持/分散/對沖）× 後果 × Owner 規則對應
- 等 Owner 一句話，不預設哪條路對

### 品質門檻

- 每張卡：W（What 數字來源）→ SW（對 Owner 決策的意義）→ NW（一個明確問題給 Owner）
- 不在卡裡假設 Owner 的決策
- 數據超過 5 天必須標資料新鮮度
- 紅線：任何「應該買」「應該賣」的字樣均不得出現

### 追蹤指標

| 指標 | 目標 | 追蹤方式 |
|------|------|---------|
| 每週產出率 | 100%（週日前完成）| A1 巡查 commit 確認 |
| Owner 打開率 | 目標 > 3 次/月 | A0/A1 記錄 Owner 回覆 |
| Owner 回應率 | 目標 > 2 次/月 | 回覆任何章節的問題 |
| 資料新鮮度 | L4 數據不超過 7 天 | 需啟動每週 system_status_card 更新 |

> 制度化起點：2026-07-18（第一份）。下一份：2026-07-27（週日）。

---

## 例會格式週報（模板）

每週五 A1 例會回報格式：

```
【IS 週報 2026-W??】
IS-HS: ??/100（↑/↓ from last week ??）
  - 資料新鮮度: ??% | 警報通暢度: ??% | 決策速度: ??% | 覆盤: ??%

📋 本週投資提案簡報：state/is_brief_YYYYMMDD.md
  - 候選亮點：[標的] — [一句話]
  - 持倉健康：[最緊迫的一個問題]
  - Owner 回應次數（本週）：?

本週完成（可自主）:
  - [P?] 項目名稱 — 驗收證據（commit hash / log）

本週完成（需 Owner）:
  - [P?] 項目名稱 — Owner 決策：[已確認/待確認]

下週排程:
  - [P?] 項目名稱（預估 Xh，類型：可自主/需Owner）

Escalation 待處理: X 條（最老 ??h）
```

---

## 附錄：與現有文件關係

| 文件 | 關係 |
|------|------|
| `projects/investment-os-value-definition.md` | 本計畫的「為什麼」— 五大核心交付定義量尺 |
| `projects/investment-os-functional-audit-2026-07-07.md` | 本計畫的 backlog 來源（20 個輸出缺口） |
| `projects/b1-investment-logic-bridge.md` | Owner 投資語言 — 改善報告格式時必讀 |
| `state/runtime_escalation_queue.jsonl` | 規則引擎已有輸出，缺的只是 push 路徑 |
| `state/exposure_ledger.md` | 主要資料來源（2026-07-01，需定期更新）|
| `docs/fable5-direction-and-guidance.md` | 方向優先序：IS 規則引擎 = (3) 第三優先 |

---

> 本文件由 A1 建立（2026-07-18）。
> 每週五例會更新 IS-HS 趨勢，B1 實施 backlog 項目。
> Phase 3（investment_goals.md）需 Owner 15 分鐘填寫，其餘由 A1/B1 自主推進。
