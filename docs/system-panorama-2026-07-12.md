# MAPLAB 系統全貌 — 2026-07-12
> 作者：A0/A1 A0 派工執行 | 生成時間：2026-07-12 午後
> 目的：Owner 回來後的第一份讀物，也是每日例會的基準
> 格式：每角色一節 — 定位、任務、實際運作狀態、斷點、推進方向

---

## 一、全局快照

| 維度 | 狀態 |
|------|------|
| 今日巡查 | 2026-07-12 09:00 ✅ 自動執行 |
| 任務總數 | 43 張 Task Card（11 done / 11 active / 7 stale-active / 4 blocked / 8 unmarked / 9 paused） |
| 緊急事項 | T-A7-001 Phase 3 等 Owner 授權（~172h 停等）；T-A5-005 等 Owner 執行 GAS 設定函式 |
| Codex/Antigravity | 有額度、未充分利用；本次派工啟動利用 |
| Hermes patrol | 正常每日執行，hermes CLI 本身 missing（patrol 走 scripts/patrol.sh 替代） |

---

## 二、A1 — 系統總管中心（Claude Code / Mac mini 常駐）

### 定位
A1 是全系統的中樞神經：任務看板、狀態同步、巡檢、debug、版本管理、對 A0+A2-A8 下指令。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-A1-V7 | 🔄 進行中 | Phase 1-4 完成，Phase 5（自動壓縮）待做 |
| T-A1-EXT-001 | 🔄 進行中 | dynamic role modules，1天前有活動 |
| T-A1-LEARNING-LOOP-001 | 🔄 進行中 | token capital registry 建立，1天前有活動 |
| T-A1-SYNC-GUARD-001 | 🔲 待開始 | 同步守護機制 |
| T-A1-002 | （未掃到狀態） | 舊任務 |

### 實際運作狀態
- 每日巡查正常（com.maplab.patrol 排程每日 08:00/16:00/22:00）
- Hermes patrol 產出 reaction cards（today: long-blocked-three-layer-review / stale-active-dispatch / task-card-status-normalization）
- checkpoint.sh 正常運作，預設直接 push main

### 斷點
1. T-A1-V7 Phase 5（自動壓縮）尚未啟動
2. 8 張 Task Card 狀態未標記（T-A1-RTK-001 / T-A2-006 / T-A2-SEO-CATERING-MATRIX-001 / T-A4-002 / T-A5-004 / T-A8-001 / T-B1-DASH-001 / T-HQ-001）

### 推進方向
- 立即：補標 8 張未標記 Task Card 狀態（可用 Codex 快速掃）
- 短期：T-A1-V7 Phase 5 自動壓縮啟動
- 中期：T-A1-SYNC-GUARD-001 啟動（狀態同步守護）

---

## 三、A2 — SEO 內容工廠

### 定位
負責 MAPLAB WordPress 網站 SEO：三大 Pillar（婚禮/企業/生日）、cannibalization 清理、Google Search Console 驗收。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-A2-007 | ✅ 完成 | SEO 三人小組評審（2026-07-07），婚禮 pillar 草稿+B3操作稿+cannibalization 定案 |
| T-A2-005 | 🔄 stale ~69天 | SEO Factory 骨架已建，WP 寫入憑證未到 |
| T-A2A3-001-B | 🔄 stale ~45天 | WP post 1696 建立為草稿，等 GSC 驗收 |
| T-A2-002 | ⏸️ 阻塞 | 等 Owner 決定 post 698 FAQ 改法 |
| T-A2A3-001 | ⏸️ 阻塞 ~48天 | RM/GSC 驗證需 Owner/A1 另開 |
| T-A2-006 / T-A2-SEO-CATERING-MATRIX-001 | ❓ 未標記 | 需補狀態 |

### 實際運作狀態（Phase B 走查結論）
- SEO Factory 地端骨架存在（`automation/seo_factory/`），7階段流程 dry-run 已驗證
- 缺 WP Application Password → 無法從 CLI 發布草稿，只能 dry-run
- T-A2-007 婚禮 pillar 草稿已寫完，**尚未發布到 WordPress**（手動操作點）
- cannibalization 定案表已寫入 `docs/seo-keyword-map.md`
- GSC 驗收窗口 T+14（2026-07-21，婚禮 pillar）

### 斷點
1. WP 寫入 Application Password 未到位（核心阻塞）
2. T-A2A3-001 slug 驗收路徑不清（planned slug ≠ live URL）
3. post 698 FAQ 決策等 Owner

### 推進方向
- Owner 5 分鐘動作：① WP 後台建立 Application Password → 給 A2；② post 698 FAQ 決策
- A1 下指令：T-A2-005 接 WP 憑證做 `--publish` 驗證（WP 憑證到位後馬上啟動）
- T-A2-007 草稿發布待 Owner 確認（婚禮/gender-reveal 兩篇都在 `workbook/outputs/seo-gap-drafts/`）

---

## 四、A3 — 社群廣告

### 定位
Facebook/Instagram Meta Ads、Google B3 廣告試營運操作。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-A3-001 | ✅ 完成 | GTM v21 2026-04-15 |
| T-A3-002 | ⏸️ stale ~104天 | 等廣告週期 + Owner 登入 Meta Ads Manager |

### 實際運作狀態
- B3 Google Ads 試營運操作稿已完成（`docs/runbooks/2026-07-07-b3-trial-launch-stepbystep.md`）
- Meta Ads 需 Owner 親自登入後台操作（A3 無法代操）
- GTM 追蹤碼已佈（T-A3-001 ✅）

### 斷點
- T-A3-002 阻塞 104 天：Meta Ads 登入依賴 Owner
- B3 Google Ads $100/day 試營運操作稿已備，Owner 可按稿執行

### 推進方向
- **B3 廣告**：Owner 按 `docs/runbooks/2026-07-07-b3-trial-launch-stepbystep.md` 啟動（5分鐘）
- **Meta Ads**：若 Owner 一週後回來，重新評估廣告週期是否適合

---

## 五、A4 — 照片素材管線

### 定位
管理 MAPLAB 所有照片素材：分類、ALT 文字生成（SEO）、Drive 串流優化。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-A4-003 | 🔄 進行中 | ALT pipeline：36,676 張待處理，launchd 需 Owner load |
| T-A4-004 | 🔄 進行中 | 分類搬移：98,400 張，10,000 張批次背景執行中 |
| T-A4-001 | ✅ 完成 | 大批照片整理完成 |
| T-A4-002 | ❓ 未標記 | pagewu1010 187GB Takeout，待 T-A4-001 完成後啟動 |

### 實際運作狀態（Phase B 走查）
- gemma4 vision 驗證可用，ALT 品質測試 OK（「豐盛的慶生派對餐桌佈置…」）
- T-A4-003 pipeline script 已建，但 launchd 未 load → **不是每小時自動跑**
- T-A4-004 分類 script 建立，30 張實測正確，但同樣 launchd 未 load
- 兩個任務目前都需要 Owner 執行兩個 `launchctl load` 才能自動化

### 斷點
兩個任務共同阻塞：Owner 需執行：
```bash
launchctl load ~/Library/LaunchAgents/com.maplab.a4-photo-alt.plist
launchctl load ~/Library/LaunchAgents/com.maplab.a4-photo-classify.plist
```

### 推進方向
- Owner 5 分鐘動作：執行上述兩個 launchctl load
- 進度查詢：`/usr/bin/python3 scripts/a4_photo_alt_pipeline.py --status`
- 全部處理完後：Drive 桌面改「串流檔案」釋出 ~531GB

---

## 六、A5 — 報價引擎

### 定位
Google Sheets + GAS 報價系統：SALES_INTAKE 錄入 → 產出 QUOTE_DRAFT → 同步狀態 → Dashboard。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-A5-002 | 🔄 stale ~18天 | fixMasterTemplate_() 已加，Owner 需測試 |
| T-A5-005 | 🔄 stale ~18天 | clasp push 完成，Owner 需 GAS 執行兩個設定函式 |
| T-A5-007-codex-takeover | 🔲 待開始 | Codex 接手 A5 任務 |
| T-A5-006 | 🔲 待開始 | OrderLines 2025 重建 |

### 實際運作狀態（Phase B 走查）
- GAS 報價系統核心功能（`createQuoteVariants`）運作中——A6 Telegram bot 每次報價都會呼叫
- T-A5-005 `setupSyncTrigger` / `setupDashboard` 未執行 → **SALES_INTAKE 沒有自動同步狀態欄、沒有 Dashboard**
- T-A5-002 `fixMasterTemplate_()` 是否已在 GAS 執行尚不明確
- 報價走 GAS Web App deployment @12，A6 bot 驗證過正常

### 斷點
1. Owner 需在 GAS 編輯器執行：
   - `setupSyncTrigger`（建立每 30 分鐘定時掃描）
   - `setupDashboard`（建立 Dashboard 分頁）
2. A5 外送費級距未建立（影響 A7 Q5 自動計算）

### 推進方向
- **Owner 5 分鐘動作**：開啟 GAS 編輯器 → 執行 `setupSyncTrigger` + `setupDashboard`
- 外送費級距：Owner 告知規則後 A1/A5 立即建入 Items 表
- T-A5-007 Codex 接手：可把 A5 GAS debug/維護卸載給 Codex（唯讀診斷）

---

## 七、A6 — LINE 業務報價助手 / Telegram Bot

### 定位
LINE OA 客戶詢問 → Telegram bot 接收 → A5 報價引擎 → 回覆業務。運行於 Mac mini launchd（`com.maplab.a6bot`）。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-A6-001 | 🔄 stale ~124h | Case Store v0 接入，最後活動 2026-07-08 |
| T-A6-002 | 💤 暫停 | ~95天 |

### 實際運作狀態（Phase B 走查）
- **Bot 正常運行**：PID 29067，launchd `com.maplab.a6bot` 運作中
- **Codex-first 聊天路由**：一般聊天 → Codex exec → fallback Ollama（透明降級）
- **Sheet-first 報價路由**：明確報價文字 → `build_sheet_quote_payload()` → GAS `createQuoteVariants` → Google Sheet URL
- **`/takeover` 接手包**：已建立，包含 repo/runtime/冷啟動檔案/最近 local memory
- **已知限制**：LINE OA 雙向對話仍無法完整捕捉（Webhook 只有 inbound）
- **断点**：`/linecases today` / `/case` / `/casequote` 三個 Case Store 指令功能依賴 live Google Sheet，本機 OAuth 若 `invalid_grant` 會降級到 seed 檔

### 斷點
1. LINE Developers Console Webhook URL 未填入（Inbound 可讀但 Webhook 未正式設置）
2. `/linecases today` 等 Case Store 指令依賴 Google OAuth（本機 token 曾回 `invalid_grant`）
3. 與 A7 的交接尚未實作（急件 → 轉 A6 的路徑存在於模板但未自動觸發）

### 推進方向
- Owner 5 分鐘動作：LINE Developers Console → Channel 1654658337 → 填入 Webhook URL
- Google OAuth token 刷新（`skills/credentials/google-token.md`）
- A7 Phase 3 上線後，自然形成 A7→A6 急件轉接閉環

---

## 八、A7 — 客服 FAQ

### 定位
Mina（業務）的 LINE 回覆助手：Q1-Q10 模板庫 + 補問流程 + 客戶分類標籤。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-A7-001 | 🔄 Phase 3 等 Owner 授權 | 模板庫完整，Phase 3 = Mina 開始用真實 LINE 對話 |
| T-A7-002 | ⏸️ 阻塞 | LINE bot 後台 + TimeTree 權限等 Owner |
| T-A7-003 | （未確認） | 需補查 |

### 實際運作狀態（Phase B 走查）
模擬 Q1-Q10 客人提問驗證：

| Q | 模擬場景 | 模板可用？ | 備註 |
|---|----------|-----------|------|
| Q1 | 缺人數「企業活動不知道幾人」 | ✅ 可用 | 補問模板完整 |
| Q2 | 「大概多少錢？」 | ✅ 可用 | 提供門檻不報具體價格 |
| Q3 | 外帶禮盒詢問 | ✅ 可用 | 低消三千、提前兩週 |
| Q4 | 婚禮 Candy Bar 加購 | ✅ 可用 | 導向 A5 加購欄 |
| Q5 | 高雄外燴費用 | ✅ 部分可用 | 高雄兩萬五起有答，外送費級距 [PENDING] |
| Q6 | 檔期確認 | ✅ 可用 | 依賴 TimeTree（A6 技能2）|
| Q7 | 試吃要求 | ✅ 可用 | 2026-07-06 Owner 政策：不提供試吃，改照片/案例 |
| Q8 | 報價後要求降價 | ✅ 可用 | 菜色調整而非直接降價 |
| Q9 | 7人婚禮不達門檻 | ✅ 可用 | 婉拒+導向外帶 |
| Q10 | 回頭客再詢 | ✅ 可用 | 2026-07-11 Owner 確認政策落地 |

**結論**：Q1-Q10 模板庫完整可用，唯一技術空缺是 Q5 外送費級距。Phase 3 授權後 Mina 可立即開始用。

### 斷點
1. **Phase 3 上線等 Owner 授權** Mina 開始使用（最高優先，Owner 回來第一天可以做）
2. A5 外送費級距建立後 Q5 完整

### 推進方向
- **Owner 5 分鐘動作**：授權 Mina 開始用 `data/a7-reply-templates.md` 接真實 LINE 對話
- A5 外送費級距建立（Owner 告知規則即可，A5/A1 建入）

---

## 九、A8 — 影音內容產線

### 定位
將 MAPLAB 案例資料夾轉化成短影片，分發到 TikTok / YouTube / IG / Pinterest。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-A8-001 | 🔄 ACTIVE | 研究 IG Reel 底層邏輯，上次活動 2026-06-20 (~22天) |

### 實際運作狀態
- 研究已完成（IG Reel 邏輯 + MAPLAB 自身 41.7萬 views Reel 分析）
- 理解了工具主導型 Reel 格式（案例資料夾 → 公開安全標籤 → 分鏡 → AI 組裝 → 多平台分發）
- **尚未實際製作一支影片**：框架研究完畢但沒有一個 artifact

### 斷點
- 上次活動 ~22天前（f9d1c42 2026-06-20），停在「研究完畢，等工具選定」
- 實際影片製作工具鏈未決定（Higgsfield? Adobe Express? CapCut?）

### 推進方向
- 用 Codex 幫 A8 跑工具評估（純文字分析，符合 offload 準則）
- 先產出一支測試影片（15-30秒，婚禮或生日案例），驗證完整流程
- 完整流程後寫進技能書，再批次生產

---

## 十、B1-B4 — Investment OS 建造/審查/歸檔/系統巡查

### 定位
B1 Builder（寫功能）/ B2 Reviewer（資料流審查）/ B3 Archivist（版本紀錄）/ B4 System Patrol（系統適合性巡查）。例行維護由 Ollama 跑，Claude 只做清積欠 + escalation。

### 現有任務
| Task Card | 狀態 | 說明 |
|-----------|------|------|
| T-B1-B4 | 🔄 ACTIVE | RSI 成長閉環已建（2026-06-18），下一步接 scorer 進排程 |
| T-HQ-001 | 等 Owner | P1-P5/P6 腳本完成，Owner 需 launchctl load + hermes memory setup |
| T-B1-DASH-001 | ❓ 未標記 | 需補狀態 |

### 實際運作狀態
- RSI-like Recursive Self-Improvement v0 baseline 已建（2026-06-18）
- agent-hq 架構設計完成（`docs/agent-hq-architecture.md`）
- T-HQ-001 全部腳本已部署，等 Owner 執行三個一次性指令

### 斷點
Owner 需執行（T-HQ-001）：
```bash
launchctl load ~/Library/LaunchAgents/com.agent-hq.hermes.plist
launchctl load ~/Library/LaunchAgents/com.agent-hq.patrol.plist
hermes memory setup
```

### 推進方向
- B1-B4 scorer 接進排程/Telegram 摘要（下一個 B1 session 任務）
- Owner 執行 T-HQ-001 launchctl 指令

---

## 十一、B5 — 影子能力蒸餾

### 定位
新角色（2026-07-11 建立）。將 Owner 的隱性判斷力、決策模式蒸餾成可複用的 prompt 框架，供其他 agent 學習。

### 實際運作狀態
- 章程、AGENT_RULES、RECALL_PROMPTS 均已建立（commit 8ef8360）
- Q3 品質審查完成，首次蒸餾評分產出，教材包骨架已建
- 打包腳本已建

### 斷點
- 剛建立，第一輪實質蒸餾尚未開始

### 推進方向
- 收集 Owner 近 30 天的判斷案例（可從 decisions.md + git commit messages 抽取）
- 跑第一輪完整蒸餾並產出可用 prompt 框架

---

## 十二、Codex — 付費 Sub-agent（GPT/ChatGPT Plan）

### 定位
Claude 的付費輔助執行層，適合批量文字生成、唯讀分析、翻譯改寫。底層模型目前為 gpt-5.5（不帶 `-m`）。

### 實際狀態
- CLI 版本：`codex-cli 0.142.0`（有 0.143.0 可更新）
- 已驗證呼叫方式：`codex exec --ephemeral -s read-only -C <repo>`
- 已有 MCP：`node_repl`（瀏覽器）/ `github`（bearer token 有效）/ `notion`（未登入）
- 無 Google Sheets/Drive/Ads MCP（需先過安全審查才能加）
- 新能力：`--output-schema`（結構化輸出）/ `resume --last`（多輪續接）/ `-i`（附圖）

### 斷點
- T-A5-007-codex-takeover 待開始（Codex 接手 A5 診斷/維護）
- task-card-status-normalization（8張未標記卡）適合直接丟 Codex 快掃

### 推進方向（見 Phase C 結論）
- 預設派給 Codex：SEO 草稿/FAQ 草稿/Task Card 狀態補標/翻譯改寫/唯讀診斷
- 需結構化輸出時加 `--output-schema`

---

## 十三、Antigravity (agy) — 付費 Sub-agent（多模型）

### 定位
另一個付費輔助執行層，支援 Gemini / Claude / GPT-OSS 多底層模型切換。

### 實際狀態
- 已驗證呼叫：`agy --print "<prompt>"`
- 可用模型：Gemini 3.5 Flash（Medium/High/Low）/ Gemini 3.1 Pro / Claude Sonnet/Opus 4.6 / GPT-OSS 120B
- **權限風險**：`--print --sandbox` 下曾主動執行 shell 指令，沒有 Codex `-s read-only` 等級的保護
- 已用於：weekly_eval_compounding.py 品質複核（`run_agy_quality_review()`）

### 推進方向（見 Phase C 結論）
- 適合：定性品質審查（不需要 sandbox 嚴格管控的場景）/ eval 評分 / 長文審閱
- 需謹慎：接任何面向客戶的路徑前必須解決 sandbox 問題

---

## 十四、Owner 行動速查表（回來後優先執行）

### 5 分鐘內可完成的動作
| # | 動作 | 影響 |
|---|------|------|
| 1 | 授權 Mina 使用 `data/a7-reply-templates.md` 開始 Phase 3 | A7 立即上線，業務有工具 |
| 2 | GAS 編輯器執行 `setupSyncTrigger` + `setupDashboard` | A5 報價狀態自動同步 + Dashboard |
| 3 | 執行 `launchctl load` A4-photo-alt + A4-photo-classify | A4 開始每小時自動整理 36,676 張照片 |
| 4 | 告知外送費級距規則 | A7 Q5 / A5 完整，業務報價更精確 |
| 5 | 啟動 B3 Google Ads $100/day | 按操作稿（`docs/runbooks/2026-07-07-b3-trial-launch-stepbystep.md`）執行 |

### 需要更多時間的決策
| # | 決策 | 背景 |
|---|------|------|
| 6 | Post 698 FAQ「無麩質或低糖選項」答案 | A2 食安 SEO 阻塞 |
| 7 | T-A2A3-001 slug 驗收：planned slug 是否已 live | A2 SEO 驗收 |
| 8 | LINE Developers Console Webhook URL 填入 | A6 完整 LINE 同步 |
| 9 | Meta Ads 廣告週期是否適合重啟 T-A3-002 | A3 廣告策略 |
| 10 | T-HQ-001 launchctl load + hermes memory setup | agent-hq 集團層啟用 |

---

## 十五、系統健康摘要

### 正常運作（不需 Owner 介入）
- A1 每日巡查 / Hermes patrol
- A6 Telegram bot（PID 正常，報價路由正常）
- B1-B4 Investment OS 地端維護模式

### 等一次性 Owner 動作就能解鎖
- A7 Phase 3 上線（授權 Mina）
- A5 Dashboard + 狀態同步（GAS 設定函式）
- A4 自動化管線（launchctl load）

### 架構層面的隱患
1. **Codex/Antigravity 額度未充分利用**：每次都用 Claude 額度跑可卸載的任務（本次 A0 派工開始修正）
2. **Task Card 狀態混亂**：8 張未標記，patrol 無法可靠判斷 → 建議 A1 下週清一次
3. **Hermes CLI missing**：patrol 走替代路徑（scripts/patrol.sh），功能正常但整合度較低
4. **A5 外送費未建**：這是 A6 報價和 A7 Q5 兩個系統的共同空缺，Owner 告知後 30 分鐘可填

---

*本文件 Phase B 使用者視角走查結論已嵌入各角色節*
*Phase C Codex/Antigravity 派工結論見 `skills/codex-offload-guide.md`（角色適配表）和 `state/a0_delegate_20260712_report.md`*
