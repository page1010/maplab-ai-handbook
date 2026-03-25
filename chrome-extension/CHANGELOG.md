# Chrome Extension Changelog

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
