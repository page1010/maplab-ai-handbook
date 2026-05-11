# Chrome Extension Changelog

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
