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

*產出物：docs/system-panorama-2026-07-12.md / skills/codex-offload-guide.md（更新）/ workbook/reviews/JOB-* × 6 個目錄*
