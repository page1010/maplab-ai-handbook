# A0 派工報告 — 2026-07-12

> Owner 例會格式 | 執行者：A0/A1 | 完成時間：2026-07-12 午後

---

## 執行摘要

Owner 一週不在電腦前，A0 受命完成三個 Phase：
- **Phase A**：全貌閱讀 → 產出系統地圖
- **Phase B**：每角色使用者視角走查（5 角色實測）
- **Phase C**：Codex/Antigravity 角色適配實驗 + 派工 2-3 件積壓工作

全部執行完畢，commit 落地，無後續 blocker。

---

## Phase A — 系統全貌

**產出**：`docs/system-panorama-2026-07-12.md`（Owner 回來後的第一份讀物）

### 關鍵發現
| 角色 | 定位 | 實際狀態 | 主要斷點 |
|------|------|---------|---------|
| A1 | 系統總管 | ✅ 每日巡查正常 | T-A1-V7 Phase 5 待做；8 張 Task Card 未標記 |
| A2 | SEO 工廠 | 🔄 活躍但 WP 寫入憑證缺 | T-A2-007 ✅ 完成（婚禮 pillar 草稿已寫）；缺 WP Application Password |
| A3 | 社群廣告 | ⏸️ stale 104天 | B3 操作稿已備，等 Owner 登入啟動 |
| A4 | 照片管線 | 🔄 launchd 未啟用 | 兩個 `launchctl load` Owner 5分鐘可解 |
| A5 | 報價引擎 | 🔄 核心正常，Dashboard 未建 | GAS 需 Owner 執行 `setupSyncTrigger` + `setupDashboard` |
| A6 | Telegram Bot | ✅ PID 正常運行 | LINE Webhook URL 未填；Case Store 依賴 Google OAuth |
| A7 | 客服 FAQ | 🔄 模板完整，Phase 3 等授權 | Owner 授權 Mina 開始使用即可上線 |
| A8 | 影音產線 | 🔄 研究完，未實際製片 | 缺第一支測試影片 |
| B1-B4 | Investment OS | 🔄 RSI 閉環已建 | T-HQ-001 等 Owner 執行 3 個指令 |
| B5 | 影子蒸餾 | 🆕 剛建立 | 第一輪蒸餾尚未開始 |
| Codex | Sub-agent | ✅ 額度可用 | 本次派工正式啟動利用 |
| Antigravity | Sub-agent | ✅ 額度可用 | 本次派工正式啟動利用 |

---

## Phase B — 使用者視角走查

### A5 報價（模擬業務走一次）
- **GAS 報價核心**：正常（`createQuoteVariants` 被 A6 bot 呼叫，有日誌）
- **斷點**：Dashboard/狀態同步未啟動（Owner 需 GAS 執行 2 個設定函式）
- **修復**：無（需 Owner 動作）

### A6 Telegram（查最近對話 + 路由驗證）
- **Bot 狀態**：PID 29067 正常，報價路由 Sheet-first 確認
- **斷點**：`/linecases` 依賴 Google OAuth；LINE Webhook URL 未填
- **修復**：無（需 Owner 動作）

### A7 FAQ（Q1-Q10 逐題驗證）
- **Q1-Q10 模板**：全部可用，品質達標
- **唯一空缺**：Q5 外送費級距（A5 尚未建立）
- **結論**：Phase 3 授權後 Mina 可立即上線使用

### A2 SEO Factory（dry-run）
- **骨架狀態**：`automation/seo_factory/` 7 階段流程存在，dry-run 已驗證
- **斷點**：缺 WP Application Password，無法實際發布

### A4 照片管線（ASSET_LOG 抽樣）
- **ALT pipeline**：腳本存在，gemma4 vision 驗證可用
- **斷點**：launchd 未 load，管線沒有自動跑

---

## Phase C — Codex/Antigravity 角色適配實驗

### 實驗設計
丟相同任務給 Codex 和 agy，比較品質/速度/準確度：

| 任務類型 | Codex wall_time | agy wall_time | 品質勝者 | 備註 |
|---------|----------------|--------------|---------|------|
| 批量文字生成（3筆 ALT text） | ~20s | ~5s | agy（速度碾壓） | 品質相當，agy 快 4x |
| 唯讀 repo 分析（讀 5 張 Task Card） | ~74s | ~10s（無 repo 存取）| Codex（有根據）| agy 無法讀 repo，只能用 prompt 資訊判斷 |

### 角色適配結論（已寫入 `skills/codex-offload-guide.md` 九、角色適配表）
- **純文字生成 → agy**（速度 4x，品質等量）
- **需讀 repo → Codex**（唯一能讀本機檔案的選擇）
- **結構化 JSON Schema → Codex**（`--output-schema` 原生支援）
- **eval 品質複核 → agy**（模型可切換，已在 weekly_eval_compounding.py 驗證）

### 實際派工成果（本次積壓工作）

| 任務 | 工具 | 落檔路徑 | 品質評估 |
|------|------|---------|---------|
| Task Card 狀態補標（5 張） | Codex | `workbook/reviews/JOB-CODEX-TASK-CARD-NORMALIZE-20260712/` | ✅ 有根據（讀了真實 repo） |
| A2 SEO 關鍵字矩陣草稿 | agy | `workbook/reviews/JOB-AGY-SEO-MATRIX-BRIEF-20260712/` | ✅ 品質達 A2 標準，主/長尾/競分析齊全 |
| 批量 ALT 文字測試 × 3 | agy | `workbook/reviews/JOB-AGY-TASK1-ALT-20260712/` | ✅ JSON 格式正確，可直接使用 |

---

## Owner 回來後優先行動（5件 × 5分鐘）

| 優先 | 動作 | 解鎖什麼 |
|------|------|---------|
| 1 | 授權 Mina 使用 `data/a7-reply-templates.md` | A7 Phase 3 立即上線 |
| 2 | GAS 編輯器執行 `setupSyncTrigger` + `setupDashboard` | A5 報價狀態自動同步 + Dashboard |
| 3 | `launchctl load` A4 photo-alt + photo-classify | 照片管線每小時自動跑 |
| 4 | 告知外送費級距 | A7 Q5 + A5 完整 |
| 5 | B3 廣告按操作稿啟動 | 廣告流量開始 |

---

## A0 派工效益

| 節省 Claude 額度 | 省掉什麼工作 |
|----------------|------------|
| ~2-3 個 Claude session | Task Card 狀態掃描（Codex 做）+ SEO 矩陣草稿（agy 做）|
| 約 $0.5-2 Claude 費用 | 用已付費的 Codex/agy 額度替代 |

**關鍵洞察**：Codex 和 agy 都已付費，每次用 Claude 做可卸載的任務等於浪費了已買的資源。本次派工建立了有根據的路由標準，後續所有角色都應先查 `skills/codex-offload-guide.md` 九、角色適配表再決定用誰。

---

## Phase B — Investment OS 全角色價值走查（擴充）

> 完整執行 log：`state/a0_delegate_20260712b.log`
> 量尺文件：`projects/investment-os-value-definition.md`
> 紅線：不下單、不給個股買賣建議；所有建議設計為「Owner 規則觸發 → 三選項通知」

### B1. 第一性思考：Investment OS 到底要帶來什麼

Investment OS 存在的唯一理由：**讓 Owner 每天回答 5 個問題的速度從 30 分鐘 → 3 分鐘**

五大核心交付：
1. 今日可動性判斷
2. 風控閘門狀態（集中度/槓桿/現金）
3. 世界觀錨定（終局假設 1-2 個）
4. 訊號新鮮度保證（過期不上介面）
5. Owner 決策紀錄（觀察/等待/排除都算決策）

**最大發現**：20 個輸出，沒有一個服務四層篩選第一層（世界觀/終局框架）。這是系統的根本盲點，不是功能缺失，而是方向缺失。

### B2. 全角色走查（17 個角色）

完整評分表見 `state/a0_delegate_20260712b.log` 第二節。

**最高優先（直接服務風控閘門）：**
- IOS-SENTINEL ⭐⭐⭐⭐⭐：技術三重賣出警示，半導體修正最直接適用
- IOS-INVENTORY ⭐⭐⭐⭐⭐：持倉風控卡，實倉第一道守門員

**需修復（停擺 49-54 天）：**
- IOS-LEFT（~49天停更）/ IOS-RIGHT（~54天停更）：廣度/右側訊號斷供

**需新建：**
- IOS-THESIS：四層篩選第一層（世界觀/終局框架），建議 `projects/investment-os-thesis-registry.md`，每季一份

### B3. 半導體修正案例覆盤（2026-07）

**事前可偵測的訊號 vs 實際發出狀況：**

| 訊號 | 理論可偵測 | 實際 | 原因 |
|------|---------|------|------|
| 集中度警示（82.7%） | ✅ | ⚠️ 部分 | exposure_ledger 有標 CRITICAL，但無三選項通知閉環 |
| 廣度惡化 | ✅ | ❌ | IOS-LEFT 停更 49 天 |
| 籌碼鬆動 | ✅ | ❓ | IOS-CHIP 狀態待查 |
| 新聞密度 | ✅ | ❌ | shadow_findings 自 2026-06-02 斷供 |

**根本問題**：功能存在，資料管道斷鏈。唯一確實發出的警告是 exposure_ledger CRITICAL 標記，但沒有「警示 → 通知 Owner 選行動」的閉環。

### B4. 規則引擎草稿（5 條，等 Owner 核准後才實裝）

| Rule | 觸發條件 | 通知格式 |
|------|---------|---------|
| R-01 | US tech 曝險 > X% + 技術面兩個指標轉負 | 降部位/對沖研究/觀察 三選項 |
| R-02 | Firstrade 槓桿 > 1.8x + 制度轉 C/D | 降槓桿/補現金/靜觀 三選項 |
| R-03 | 外資連 3 日賣超 + 廣度下降 | 觀察/降一碼/保持 三選項 |
| R-04 | 任一持倉達 1R 止損線 | 執行止損/縮手/持有 三選項 |
| R-05 | 帳戶 30 天回撤 > 15% | 緊急通知（無選項，立即查看） |

**Owner 需確認 4 個參數**：`threshold_A`（集中度門檻）/ `leverage_threshold`（槓桿門檻）/ `1R_pct`（止損%）/ `drawdown_30d_pct`（急性警示%）

### B5. 通知管道評估

| 方案 | 成本 | 優先 |
|------|------|------|
| Telegram 緊急前綴 🚨 分類 | 30min | 立即 |
| 規則觸發 Mail（pagewu1010@gmail.com） | ~2-4h B1 | 規則引擎核准後 |
| Dashboard Investment OS 首頁 tab | ~4h B1 | 第三步 |

Mail 原型已設計，不啟用，等 Owner 核准。前置需確認：gmail.send OAuth scope 或 App Password。

### B6. 系統修復優先排序（Owner 看完後的行動清單）

| 優先 | 任務 | 解鎖 |
|------|------|------|
| P1 | 確認 R-01 到 R-05 的 4 個參數 | 規則引擎才能實裝 |
| P1 | B4 確認 IOS-CHIP / IOS-MOMENTUM 是否每日有真實 Telegram 輸出 | 釐清「決策資訊幻覺」 |
| P2 | B1 修復 shadow_findings.jsonl 供料（convergence-engine JSON 解析） | IOS-ALPHA / 新聞密度恢復 |
| P2 | B1 修復 FRED API key（pitfall #184） | IOS-MACRO 可信 |
| P3 | 建立 IOS-THESIS（終局假設管理員） | 四層篩選第一層補齊 |
| P4 | 規則觸發 Mail 原型實裝 | Owner 出門也能收到警示 |

---

## 全派工產出物清單

| 產出物 | 路徑 | 用途 |
|--------|------|------|
| 系統全貌地圖 | `docs/system-panorama-2026-07-12.md` | Owner 回來後第一份讀物（含 Investment OS 第十六節） |
| Investment OS 量尺 | `projects/investment-os-value-definition.md` | 後續所有角色決策的量尺 |
| Phase B 執行 log | `state/a0_delegate_20260712b.log` | 完整走查/覆盤/通知設計 |
| Codex/agy 適配表 | `skills/codex-offload-guide.md`（更新） | 路由標準 |
| Codex/agy 派工作品 | `workbook/reviews/JOB-* × 6 個目錄` | Task Card 補標 + SEO 矩陣 + ALT text |

---

*A0/A1 派工全部完成 | 執行時間：2026-07-12 | 下一步：Owner 回來後確認 B6 優先清單*

---

## A0/Fable5 交棒任務 — 系統修正方向與複利計畫巡查

> 執行者：A1 | 執行時間：2026-07-12 23:30 | Owner 原話：「在結束 fable5 之前先給我們整個系統寫下往哪個方向的修正與指引…讓我們系統反覆可以去檢視全貌並優化然後向複利迴圈前進，把這個 prompt 變成自動化並留存一個在我的 chrome extension 外掛，叫做複利計畫巡查」

### 本次交付物

| 產出物 | 路徑 | 說明 |
|--------|------|------|
| 系統方向指引 | `docs/fable5-direction-and-guidance.md` | 北極星 + 三個結構性風險 + 方向優先序 + 決策文化 |
| 複利計畫巡查 prompt | `skills/compounding-patrol-prompt.md` | 單一真相源，可直接餵 claude -p，含五步驟完整流程 |
| Chrome Extension 模組 | `chrome-extension/task-modules/COMPOUNDING-PATROL.json` | 按既有模組格式，可從 Extension 直接複製 prompt |
| AGENT_RULES Section 22 | `AGENT_RULES.md` 末尾 | 複利計畫巡查正式成為每週例行治理規則 |

### 核心設計決策

**北極星（一句話）**：每輪工作後，系統要比之前「更容易持續進步」——衡量標準是複利迴圈是否轉了一圈，不是忙碌量。

**三個永久防守的結構性風險**：
1. **狀態腐化**（文件與現實漂移）→ A1 每日巡查必做 CURRENT_STATUS ↔ Task Card 交叉比對
2. **三類消音**（做完沒人知道/拍板沒人推進/宣稱未驗證）→ 每週複利計畫巡查強制掃描
3. **單點依賴**（A0 額度/OAuth token/單一派工通路）→ 雙線備援清單維持可用

**方向優先序**：
1. 現金流業務閉環（A5+A6+A7 真正被真實客人使用）— **最高優先**
2. B3 廣告試跑「可複製結構」再放大
3. Investment OS 規則引擎上線（不給建議只觸發規則）
4. B5 每月蒸餾，向地端模型遷移能力

**複利計畫巡查五步驟**（完整 prompt：`skills/compounding-patrol-prompt.md`）：
1. 全貌掃描（3 分鐘重建全局狀態）
2. 五問檢視（業務閉環/三類消音/複利四環/資源浪費/Owner 待決）
3. 修正行動（直接修 + TASK_QUEUE 提案 + owner-action-queue）
4. 沉澱教訓（pitfalls + panorama 增量更新）
5. 例會格式回報 + `checkpoint.sh --notify`

### Owner 使用方式

**每週啟動**：從 Chrome Extension 選「複利計畫巡查」模組 → 複製 prompt → 貼到 Claude Code terminal

**自動化**：`skills/compounding-patrol-prompt.md` 中已附 cron/launchd 接線指令（每週一 09:00）

**歷史參照**：所有巡查報告落檔 `state/compounding-patrol-YYYY-MM-DD.md`，可追溯每週複利迴圈健康狀態

---

*Fable5 交棒任務完成 | A1 執行 | 2026-07-12 23:30*
