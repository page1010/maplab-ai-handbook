# 2026-03-27 — Telegram Bot 記憶斷裂與 A0/A1 並列架構

> 記錄者：A1 系統總管（從 experience-log EXP-F007b/F008/F009/S008/S009 整理）
> 日期：2026-03-27 ~ 2026-03-28
> 背景：bot.py 改用 CLI 呼叫後記憶全斷，連帶暴露 A0/A1 角色定位問題

---

## Owner 原始需求

要 Telegram bot 有 AI 對話能力 + 記憶 + MCP 工具 + bash 指令。

## 過程

### 第一個坑：bot.py 用 `claude -p` 失憶

bot.py 用 `claude -p` one-shot 呼叫 Claude Code CLI，每條 Telegram 訊息都是全新 session。之前用 Anthropic SDK + conversation_history deque 有記憶，改成 CLI 呼叫後記憶機制全斷。

**試過的錯誤方向**：
1. Anthropic SDK 替代 CLI → 有記憶但沒有 MCP 和 bash
2. ccbot tmux bridge → 過度複雜
3. `--dangerously-skip-permissions` → 解決授權但不解決記憶

**正確解法**：加 `-c` flag（continue 最近 session）。一個 flag 解決所有問題。

**根因**：沒先查 `claude --help` 就亂改。

### 第二個坑：A0 開 Code task 不帶 recall prompt

A0 開了 30+ 個 Code task，每個都沒帶 A1 recall prompt → 每個 session 都是失憶狀態。

**修復**：
1. auto-memory 存 A1 recall prompt
2. CLAUDE.md 放 repo 根目錄自動注入
3. user preferences 加強制規則

### 第三個坑：CLAUDE.md 跟 RECALL_PROMPTS 不同步

A0 自己寫了簡化版 CLAUDE.md，跟 Extension 裡的 recall prompt 不一樣 → Claude Code 啟動後以為自己是 A0。

**修復**：CLAUDE.md 改為 RECALL_PROMPTS A1 區塊的完整拷貝，加同步提醒。

### 好的結果：A0/A1 並列架構確立

| | A0 (Cowork) | A1 (Claude Code) |
|---|---|---|
| 能力 | 有手（Chrome、桌面控制） | 有腳（git、API、code） |
| 記憶 | session 歸零，靠 auto-memory | 持續壓縮，距離全貌更近 |

**設計**：不是互換，是 A1 當 A0 的大腦。各自直屬 Owner，不是上下級。

---

## 決策紀錄

| 決策 | 選擇 | 理由 |
|------|------|------|
| CLI 記憶方式 | `-c` flag continue session | 最簡單、保留 MCP + bash + 記憶 |
| A0/A1 關係 | 並列（各自直屬 Owner） | 手和眼的問題不會因為換角色解決 |
| 身份注入 | CLAUDE.md 自動讀取 | 不靠 A0 手動帶 prompt |

## 學到的事

1. **先查文件再動手** — `claude --help` 一個 flag 解決的事，我們繞了 3 個方向
2. **單一真相源很重要** — CLAUDE.md 和 RECALL_PROMPTS 不同步 = 身份混亂
3. **Agent 架構要按能力分，不按層級分** — 有手的做桌面操作，有腳的做技術執行

## 相關文件
- experience-log: EXP-F007b, EXP-F008, EXP-F009, EXP-S008, EXP-S009
- stories: [A0/A1 角色定位](2026-04-17-a0-a1-role-design.md)
