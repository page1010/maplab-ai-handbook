# TASK_QUEUE.md — 開放任務軌道（防吃案）

> 用途：每個開放迴圈都在這裡，有狀態+下一步+成果路徑。每階段結尾更新。
> 排序規則：SECTION 23 價值密度排序 — Tier1（距現金流 ≤ 3 步）→ Tier2（有槓桿待解鎖）→ FROZEN（凍結，等 Owner 解鎖）
> 最後更新：2026-07-18（A0派工 W→SW→NW + 價值密度重排）

---

## 🔴 Tier 1 — 立即執行（3 步內直連現金流 / 解鎖 Owner 決策）

| 任務 | 負責 | 狀態 | 下一步 | Owner 阻塞點 |
|------|------|------|--------|------------|
| **A6 LINE webhook 上線** — T-A6-001 | A6 | 🔴 CRITICAL（~275h） | Owner 填入 Webhook URL → A6 bot 立即開始收 LINE 訊息 | ✋ 需 Owner 操作 LINE Developers Console（Channel 1654658337）填 Webhook URL，5 分鐘內可解 |
| **B3 廣告試跑點火** — B3-ADCOPY | B3 | ⏸️ 等 Owner 操作 | 操作稿已備 `docs/runbooks/2026-07-07-b3-trial-launch-stepbystep.md`，Owner 在 Meta Ads Manager（帳號 318634712）建立受眾包即可啟動 | ✋ 需 Owner 登入 Meta Ads Manager，無 API，需人工建立冷層受眾包 |
| **IS 規則引擎核准包** — IS-Layer3 | B1 | ⏸️ 等 Owner 確認 4 參數 | 規則引擎本體已跑（5 條 WARNING 在 escalation_queue），只差 Owner 確認門檻參數 → B1 建 escalation_push.sh | ✋ 需 Owner 確認：SOP1 主題集中度上限（草稿 10%）、SOP2 單標的上限（草稿 15%）、槓桿警戒線（草稿 1.5x）、日跌幅急性警示（草稿未定義） |
| **A7/Hermes LINE→Sheets 邊界重設** — T-A7-001 / T-A6-HERMES-LINE-GYM-001 | A7/A6 | 🟡 LOCAL CONTRACT PASS / LIVE NOT DEPLOYED | 先檢視 `docs/hermes-line-sheets-assistant-flow-v1.md` 與 `*` 樣板；獲授權後只在隔離測試部署 neutral Sheet actions | ✋ live GAS／LINE 測試需 Owner 明示授權；舊 `data/a7-reply-templates.md` 已降為 LEGACY，禁止直接上線 |
| **A2 廣告現況巡查 + 關鍵字/行銷規劃** — T-A2-006 | A2 | 🟢 不再等 MCP token | 走 `skills/ad-platform-browser-check.md`（瀏覽器唯讀巡查 Meta/Google Ads 現況：活動/受眾/素材），彙整結果餵進關鍵字與行銷整體規劃 | 無（唯讀巡查不需 Owner 操作，需在有 Chrome MCP 的環境如 Mac mini/Cowork 執行） |

**So What（Tier 1 空轉成本估算）**：
- A6 ~275h × 每日 3-5 則 LINE 詢問 = 估計 50+ 則真實業務對話未被 bot 學習
- A7 ~323h × 模板已備 = 323h Mina 仍手動回覆，AI 輔助效益 0

**Now What**：Owner 一次回覆清單 → `state/owner_one_reply_20260718.md`，30 秒可回。

---

## 🟡 Tier 2 — 次輪執行（有槓桿待上游解鎖）

| 任務 | 負責 | 狀態 | 解鎖條件 |
|------|------|------|---------|
| A7 QA 迭代（隔離測試後） | A7 | 🔲 待 live 測試授權 | neutral Sheet shell 回讀無商務欄位後，再由 Mina 回傳首週草稿微調 |
| A5 外送費級距建立（Q5 自動計算） | A5 | 🔲 待 Owner 定規格 | Owner 給外送費 base rate / 級距表 |
| A2 SEO 草稿發布（婚禮 pillar + gender-reveal） | A2 | ⏸️ 等 Owner 核准 | Owner review `workbook/outputs/seo-gap-drafts/` 草稿後授權 WP 發布 |
| A2/A3 Round 008 圖片插入 + 發布 | A2/A3 | ⏸️ 阻塞（Chrome extension file chooser Not allowed） | Owner 開啟 Codex Chrome extension file URL access |
| T-HQ-001 三個 launchctl load | HQ | ⏳ 代碼完成，等 Owner 執行 | Owner 跑三個 `launchctl load` 指令（見 T-HQ-001.md） |

---

## 🧊 FROZEN — 凍結（算力空轉，等解鎖條件）

> 凍結中不投新 token。解鎖條件達成後移回 Tier2。

| 任務 | 凍結原因 | 解鎖條件 |
|------|---------|---------|
| T-A2-002 foodsafety post 698 改法 | 等 Owner 決定改法，現有自動防護已上 | Owner 決定「無麩質 FAQ」答案改法 |
| T-A2-003 weekly WP audit 排程 | 等 Owner 建排程 | Owner 執行 `launchctl load` |
| T-A6-002 LINE 訓練資料收集 | 方向未定，依賴 T-A6-001 先上線 | A6 LINE webhook 上線後重評 |
| T-GBP-001 GBP 新圖 | 等 Owner 準備新圖 | Owner 提供新照片 |
| T-A5-002/T-A5-007 Codex 接手 | awaiting Owner 驗證 ~472h | Owner review Codex 輸出 |
| A8 影音上傳（IG/YouTube） | 等 Owner/A1 approval | Owner 核准 review draft |
| Investment OS B3 Archivist 例行維護 | B2-B4 由 Ollama 接手，Claude 待 escalation | Ollama 地端跑不動才 escalate |
| Antigravity ExecutionLease/Ontology 提案（`docs/governance/antigravity-execution-lease-ontology-v0.1.md`） | ①需 Codex 確認原始設計是否已存檔 ②agy sandbox 唯讀保證未驗證（`skills/codex-offload-guide.md` 2026-07-06 缺口至今未關）③是否擴大 Antigravity 角色屬於一次性升格決定，需 Owner 明確核准 | Codex 存檔原始設計 + agy sandbox 驗證通過 + Owner 對角色升格拍板 |

---

## ✅ 本階段已交付（近期）

- A1 外接碟備份修補（`42f8cae` 2026-07-18 03:09）
- A1 監控去依賴化（`cab2c28` 2026-07-17：3 腳本+3 launchd plist）
- fix(ollama) KEEP_ALIVE=5m 三層落地（`6820df0` 2026-07-18）
- A0 Fable5 交棒任務（`3a7bb9c` 2026-07-12：方向指引+複利巡查+SECTION 22）
- A0 IS Phase B 走查（`61bbd8a`/`0e7dc76`/`dd23864` 2026-07-12）
- 2026-07-10 A0 委派 4 JOB 全落檔（婚禮pillar/B3廣告/內鏈審查/IS二讀）
- T-A4-001 S11(2024) 完成（07-09 22:56）

---

## 👤 Owner 自己接

- 富途牛牛即時訊息 API（起點 script 已給）
- B3 Meta 廣告受眾包建立（操作稿已備，需 Owner 人工操作）

## ⏸ Owner 暫緩

- Notion 鑰匙搬遷（重授權 or 搬本機）
- A2 個人品牌 B2B/B2C 策略（雜談）
