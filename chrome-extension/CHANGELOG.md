# Chrome Extension Changelog

## v5.7.0 — 2026-08-25
變更者：A1 Codex
- **指向性地圖入口**：角色召喚區新增離線 `🗺 指向性地圖` 按鈕，直接開啟 Extension 內建地圖，不依賴 GitHub raw 或外部網站。
- **單一資料源**：`docs/system-map/index.html` 與 `chrome-extension/system-map/index.html` 改由 `config/system-map/maplab-directional-map.json` 同步生成，避免兩份地圖人工漂移。
- **七個管理視角**：系統總圖、Repo／地址、角色與派工、A2–A8 工作流、產物血緣、能力／工具／硬體、治理／記憶／證據。
- **NotebookLM 安全包**：同一生成器建立帶 source hash 與去敏紀錄的 MAPLAB Project Brain source pack；不把整個 repo、secrets、客戶 raw data 或 runtime logs 直接上傳。

## v5.6.1 — 2026-06-05
變更者：A1 Codex
- **交接目標拆細**：runtime selector 從 4 個粗分類擴充為 Claude Code、Codex、GPT/ChatGPT、Claude Chrome tab、Antigravity、Gemini、OpenClaw、Hermes、Gemini Chrome tab。
- **Prompt 人話化**：handoff 會輸出 `runtime_target_label`，並依目標加入對應使用邊界，避免把 browser chat、repo runtime、operator worker 與 cold-path worker 混在一起。
- **舊值相容**：既有 `claude_tab` / `gemini` / `codex` / `openclaw` 儲存值仍可正常載入。

## v5.6.0 — 2026-05-29
變更者：A1 Codex
- **召喚任務欄位**：新增 `召喚任務` textarea，Owner 可直接輸入本次要交辦的目標，handoff prompt 會帶入 `本次召喚任務`。
- **自動選角**：新增 `自動選角` 按鈕，依任務文字建議並切到 A2 / B1 / B2 / B3 / B4。
- **本機 module 優先**：task modules 先讀 extension 內建的本機 `task-modules/*.json`，GitHub raw 只作 fallback；本機改版後只需 reload extension，不需要重新下載或重新設定。
- **Recall fallback**：task module 內建 role recall excerpt；GitHub raw 尚未同步時，live popup 仍可產生完整角色摘要。

## v5.5.6 — 2026-05-29
變更者：A1 Codex
- **Investment OS B1-B4 角色家族**：B1 改為 Builder，新增 B2 Reviewer、B3 Archivist、B4 System Patrol；原 B1 投資邏輯橋接改為 B1-B4 共用來源。
- **A2 Ads/SEO/WordPress Patrol**：A2 module 召喚後必須先確認品牌價值、品牌語氣、品牌顏色/視覺來源、live web 狀態與高風險批准項。
- **下拉選單改吃 module index**：popup 會用 `chrome-extension/task-modules/index.json` 動態產生 A/B 角色群組，避免新增角色後忘記手動加選項。

## v5.5.5 — 2026-05-21
變更者：A1 Codex
- **B1 投資邏輯橋接入口**：B1 下拉選單改為 `投資邏輯橋接顧問`，不再顯示成單純暫停角色。
- **Owner 投資人格底稿**：新增 `projects/b1-investment-os-owner-profile.md`，讓 B1 召喚時帶入 Investment OS 的世界觀、選股模式、公司研究、加減碼、盲點與風險提示語氣。
- **Owner canonical 校正版**：新增 `projects/b1-investment-os-owner-persona-canonical.md`，將 Owner 定義的「多層敘事 x 右側交易 x 左側預期差 x 嚴格風控 x 創業者式複利系統」作為 B1 最高優先召喚底稿。
- **模組來源同步**：更新 B1 recall、skill、Task Card 與 module builder，讓後續重建 Chrome Extension role module 時維持同一定位。

## v5.5.4 — 2026-05-21
變更者：A1 Codex
- **B1 下拉選單標籤修正**：`popup.html` 的 B1 顯示從舊的 `InnerFlowLab 內容創作` 改為 `跨專案治理顧問（暫停）`，避免側邊欄入口和 B1 module JSON 狀態不一致。

## v5.5.3 — 2026-05-19
變更者：A1 Codex
- **B1 角色模組重定位**：B1 從 `InnerFlowLab Content` 改為 `Cross-Project Governance Advisor`，側邊欄 handoff 改指向跨專案治理、報告契約、prompt 整理與 pause/resume 輸出。
- **B1 專案暫停防呆**：移除 B1 module 對 `skills/credentials/substack-api.md` 的必讀依賴，避免暫停中的內容發文專案被誤啟動或要求讀發布憑證。
- **關聯圖同步**：重建 `chrome-extension/task-modules/*.json`、`index.json`、`docs/extension/dynamic-role-task-modules.md` 與 `workbook/task_modules/*`，讓 Extension / Gemini / Codex / OpenClaw 看到同一份 B1 狀態。

## v5.5.2 — 2026-05-12
變更者：A1 Codex
- **MV3 按鈕綁定修正**：移除 HTML inline `onclick`，改由 `popup.js` 在 `DOMContentLoaded` 用 `addEventListener` 綁定，避免 Chrome Extension CSP 擋住「檢查 MD 同步 / 重新抓取 / 重載 Extension」等動作。

## v5.5.1 — 2026-05-12
變更者：A1 Codex
- **角色模組 raw-first**：`chrome-extension/task-modules/*.json` 優先走 GitHub raw + cache-busting；GitHub Contents API 只作 fallback，避免 token/API 快取讓側邊欄拿到舊 module。

## v5.5 — 2026-05-12
變更者：A1 Codex
- **Markdown 同步檢查**：role module 生成時記錄每個必讀來源的 SHA-256，側邊欄可用「檢查 MD 同步」比對 GitHub raw 最新內容。
- **動態連結語意修正**：handoff prompt 明確標示 role JSON 是 routing envelope，不是來源內容本體；Gemini/Codex/OpenClaw 必須讀最新 Markdown/JSON raw link。
- **Stale 防呆**：若 `.md` 已改但 module JSON 尚未重建，側邊欄會顯示 stale，提醒先跑 `python3 tools/ai_workbook/build_extension_task_modules.py` 再交辦高風險任務。

## v5.4 — 2026-05-11
變更者：A1 Codex
- **側邊欄改成任務模組入口**：popup 會讀 `chrome-extension/task-modules/index.json` 與各角色 JSON，顯示 runtime target、必讀來源、影響範圍、輸出契約與風險。
- **新增 runtime selector**：Gemini / Codex / OpenClaw / Claude tab legacy，產生不同交接語境的 handoff prompt。
- **新增一鍵複製 Handoff**：`📦 複製任務模組 Handoff` 會輸出平台中立任務包，讓 Gemini/Codex/OpenClaw 都能接角色。
- **Claude tab 降級為 legacy**：保留舊注入能力，但不再是主流程。

## v5.4-data — 2026-05-11
變更者：A1 Codex
- **GitHub Dynamic Role Task Modules v0.1**：新增 `chrome-extension/task-modules/` 與 `chrome-extension/config/task-modules.json`，把 A0-A8+B1 全角色改成平台中立的任務模組資料層。
- **跨 runtime 交接**：每個角色模組都標示 Gemini / Codex / OpenClaw 可讀來源、技能組、輸出契約、禁止事項、writeback 路徑與影響對象。
- **指向性關聯圖**：新增 `workbook/task_modules/role_module_relation_graph.json`、`role_module_relationships.csv`、`role_module_relationships.xlsx`，讓任務能追到「讀什麼 → 影響誰 → 產出去哪裡」。
- **安全邊界**：本次只新增 JSON/Markdown/Excel 資料層，不執行遠端 JS；Claude tab 注入仍是 legacy，不再是唯一設計中心。
- **已知缺口**：正式 repo 目前缺 `TASK_QUEUE.md`，模組已保留 missing 記錄並以 `workbook/task_index.json` 作為可讀替代來源。

## v5.3 — 2026-04-03
變更者：A1 Claude Code
- **召喚文瘦身（Problem 1 修復）**：`recalls/A1_recall.md` 移除所有動態內容（斷點、任務清單、系統快照）
- 靜態 recall = 身份+規則+必讀指令+踩過的坑，Extension 架構說明
- 動態狀態 = 由 Extension 即時附加的 `buildSystemSnapshot()`（來自 CURRENT_STATUS.md），agent 自己讀文件
- 效果：注入文字大幅縮短，agent 取得的是即時狀態而非過期快照
- 新增踩坑條目：「recalls 塞斷點+任務清單 → 過期快照誤導 agent」
- **popup.js v5.3 程式碼更新（Problem 2 修復）**：
  - `loadAll()` 加入 `cachedRecallPrompts = {}` — 每次↻重新抓取都清除快取，確保拿到 GitHub 最新 recall
  - roleStatus 過濾掉 ✅ 已完成任務，只顯示 🔄 進行中 / 🔲 可認領

## v5.2 — 2026-04-03
變更者：A1 Claude Code
commit：a21d9a2
- **Bot 剪貼板橋接**：加入「📋 從 Bot 抓取」按鈕，從 127.0.0.1:9876 fetch /tmp/maplab_clip.json，自動填入 promptText 欄位
- **架構**：Telegram `/clip [文字]` → bot.py 寫入 /tmp/maplab_clip.json → Bot 內建 HTTP server（127.0.0.1:9876）→ Extension popup fetch → 注入 Claude tab
- **解決問題**：完全繞過 AppleScript / 輔助使用權限，macOS 系統更新不會壞掉
- ⚠️ 使用前提：bot.py 需已重啟（才能跑 HTTP server）

## v5.1 — 2026-04-03
變更者：A1 Claude Code
- **自我重載按鈕**：popup 右下加「⟳ 重載 Extension」，呼叫 `chrome.runtime.reload()`，更新後不需去 chrome://extensions/ 手動 reload
- **配套技能書**：`skills/extension-update` — 兩步更新流程（git pull + 點按鈕）
- **配套腳本**：`scripts/update_extension.sh` — 自動 pull + 提示下一步

## v5.0 — 2026-04-03
變更者：A1 Claude Code
- **注入按鈕（Task A）**：新增「⚡ 注入到 Claude tab」按鈕，透過 `chrome.scripting.executeScript` 直接填入 claude.ai 輸入框（ProseMirror contenteditable），不需手動貼上
- **即時系統快照（Task B）**：選角色後，recall prompt 底部自動附加即時快照（版本+進行中任務+可認領+blockers），來自當次抓取的 CURRENT_STATUS.md
- manifest 版本更新至 5.0.0

## v4.9 — 2026-04-03
變更者：A1 Claude Code
- **Recall 拆分**：各 agent 改用獨立 `recalls/Ax_recall.md`，不再從單一大檔 AGENT_RECALL_PROMPTS.md 解析
- **按需載入**：選角色時才抓該角色的 recall 檔（lazy load），初始載入只抓 CURRENT_STATUS.md + commits，速度更快
- **任務清單格式**：各 recall 檔底部加 `[ ]` / `[x]` 任務清單，做完直接畫 x
- commit：(本次)

## v4.8 — 2026-03-29
變更者：A1 Claude Code
- **Private repo 支援**：改用 GitHub Contents API（token 存在 chrome.storage），解決 raw.githubusercontent.com 對 private repo 不支援 Authorization header 的問題
- commit：b2f031c

## v4.7 — 2026-03-28
變更者：A1 Claude Code
- **A0 角色支援**：popup.html 加入 A0 角色選項，可直接召喚 A0（Cowork 總調度秘書）的 recall prompt
- commit：b330149

## v4.6 — 2026-03-25
變更者：A1 Claude Code
- **移除 commit history 面板**：使用者不需要看系統管理的 commit 紀錄，釋放空間給 prompt
- **UI 全面優化**：
  - 寬度 380px → 400px
  - 字體放大（body 13px，prompt 12px，標籤 10-11px）
  - 文字顏色提高對比度：主文字 #e8ecf4、次要 #9baab8、標籤 #7a8a9d（原本 #4a5568 太暗）
  - prompt 區域放大（min-height 220px，max-height 300px）
  - 連結顏色改為 #6a9ae8 更易辨識
- 精簡 popup.js：移除 renderCommits、detectCheckpoints、commit 面板相關 DOM 操作
- overdue 偵測保留（用於狀態列警示），但不再顯示 commit 面板

## v4.5 — 2026-03-25
變更者：A1 Claude Code
- 移除角色 prompt 底部的 commit history 注入
- 原因：commit history 是 A1 系統管理的紀錄，跟各角色任務無關，注入後造成 prompt 污染
- 角色 prompt 現在只包含 AGENT_RECALL_PROMPTS.md 的純淨內容
- commit history 仍然在 Extension 面板可見，不影響使用

## v4.4 — 2026-03-25
變更者：A1 Claude Code
- Token 和 URL 自動儲存（失焦即存，不需要按按鈕）
- 打開 Extension 時顯示「✓ Token 已記住」狀態提示
- 填一次 token 永久記住，不需要重複輸入
- 「重新抓取」按鈕改為只重新載入資料（不再綁定儲存）

## v4.3 — 2026-03-25
變更者：A1 Claude Code
- **新增角色選擇下拉選單**（A2-A8），選角色後顯示該角色專屬召喚 prompt
- 從 GitHub 即時讀取 AGENT_RECALL_PROMPTS.md 並解析各角色 prompt
- 角色 prompt 自動注入即時 commit history
- 總覽模式保留（不選角色時顯示系統摘要）
- 記住上次選的角色（chrome.storage.local）
- popup.html 新增角色選擇器 UI + 角色狀態顯示
- 底部新增 AGENT_RECALL_PROMPTS.md 連結
- prompt textarea 高度增加（150-200px）

## v4.2 — 2026-03-25
變更者：A1 Claude Code
commit: 143e8e1
- **架構回歸本地執行**：放棄 remote-logic.js，所有邏輯回到 popup.js
- 原因：Chrome Manifest V3 的 CSP 禁止動態執行遠端 JS（script.textContent 被擋）
- 刪除 remote-logic.js
- popup.html 版本顯示更新為 v4.2
- **教訓：外部平台有安全限制時，選穩定本地方案，不要用聰明但脆弱的遠端架構**

## v4.1 — 2026-03-25
變更者：A1 Claude Code
commit: 859a1b5
- 加入 Side Panel 支援（sidePanel permission + setPanelBehavior）
- 解決 popup 點外面就關閉的問題，改為側邊欄模式
- popup.html 版本顯示從 v3.0 修正為 v4.1
- manifest.json version 4.1.0
- 確認 chrome.storage.local 讀寫邏輯正確（saveAndReload + DOMContentLoaded）

## v4.0 — 2026-03-25
變更者：A1 Claude Code
commit: 5aca2f8
- **嘗試遠端邏輯架構（失敗）**：popup.js 改為極簡 loader，從 GitHub 載入 remote-logic.js
- 新增 remote-logic.js（包含所有 v3.0 邏輯）
- manifest.json version 4.0.0
- 目標：讓使用者永遠不需要重新下載 Extension
- **結果：因 Chrome MV3 CSP 限制，遠端 JS 無法執行，v4.2 回滾此設計**

## v3.0 — 2026-03-25
變更者：A1 Claude Code
commit: ee232de
- 新增 commit history 面板（最近 8 筆，GitHub API）
- checkpoint commit 綠色高亮 + CP badge
- 進行中任務超過 48h 無 commit 自動警示
- Startup Prompt 自動合成（從 CURRENT_STATUS + commit history）
- 重構 popup.js：fetch/parse/render 分離
- 新增 GitHub Token 認證欄位（private repo 支援）
- popup.html 全新 UI（深色主題、commit panel、prompt textarea）
- manifest.json 新增 clipboardWrite permission + GitHub API host

## v2.0 — 2026-03-12
變更者：Owner
- 初始版本，顯示 CURRENT_STATUS 版本號
- GitHub repo 快速連結
- 基本設定存取（githubRawBase + projectStatePath）
- State Preview 面板
- Agent Roster 顯示
