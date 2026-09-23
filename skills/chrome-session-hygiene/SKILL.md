---
name: chrome-session-hygiene
description: Protocol for any agent using the Owner's Chrome (Claude/Codex/Hermes/OpenClaw) — register every tab you open (agent+task), reuse an existing group instead of re-opening, close your group when a stage finishes, and never touch unregistered (Owner) tabs. Use whenever you are about to open, reuse, or close Chrome tabs.
---

# Skill: chrome-session-hygiene — Chrome 分頁衛生協定(所有 agent 共用)

> 單一真相源:`claude-daily-operations/GOVERNANCE.md`「Chrome/session 衛生」條。
> 適用:任何用 Owner Chrome 的 agent(Claude / Codex / Hermes / OpenClaw)。
> Owner 參數(2026-08-28):TTL 90 分、reaper 每 30 分、安靜關+每日一行彙整、**只收登記簿裡 agent 自己開的**、Owner 個人分頁永不動。

## 觸發條件
- 你(agent)**要開任何 Chrome 分頁之前**(強制)。
- 一個任務/階段**完成時**(強制)。
- Session 結束前(強制,收尾)。

## 規則

### 1. 開分頁前先查登記簿(複用不重開)
```
bash claude-daily-operations/ops/chrome_tabs_helper.sh list | grep "<agent>:<task>"
```
- 若同 `<agent>:<task>` 已有 `status:open` 的分頁 → **複用那組,不要再開一套**。
- 沒有才開新的。

### 2. 開分頁時標記歸屬(登記)
- 每開一個分頁,**立刻登記**(否則 reaper 不會幫你收,且會被當「未登記=Owner 個人」而永不動):
```
bash claude-daily-operations/ops/chrome_tabs_helper.sh open <agent> <task> <url> [group] [ttl_min=90]
```
- 有 tab group 能力者(claude-in-chrome `tabs_*`):把該任務分頁歸進**同一 group**,group 名 = `<agent>:<task>`。
- 無 group 能力者(Control_Chrome 等):仍要登記;歸屬靠登記簿。

### 3. 階段完成 → 關整組 + 標記
- 任務/階段一結束,**立刻關掉自己那組分頁**(claude-in-chrome=`tabs_close` 整組;其他=逐一關該 task 的分頁),並標記:
```
bash claude-daily-operations/ops/chrome_tabs_helper.sh close <agent> <task>   # 已自行關掉
# 或（你關不掉、想交給 reaper 收）:
bash claude-daily-operations/ops/chrome_tabs_helper.sh done  <agent> <task>   # 標 done，reaper 下輪收
```

### 4. 不留孤兒
- 誰開誰關。Session 結束前把自己開的分頁 `close` 掉;確實關不掉的標 `done`,reaper(每 30 分)會收。
- **絕不碰未登記的分頁**(那是 Owner 個人的)。

## 安全邊界(硬性)
- **只操作自己登記的分頁**;未登記分頁一律不碰。
- 白名單(login/Drive/dashboard/Facebook/ChatGPT…)即使登記也**不關**(reaper 兜底保護)。
- reaper 是安全網,不是藉口:agent 仍須主動關組;reaper 只收「done 或超過 TTL 90 分」的孤兒,安靜關 + 每日一行彙整。

## 相關
- 登記簿:`claude-daily-operations/state/chrome_tabs_registry.jsonl`
- helper:`claude-daily-operations/ops/chrome_tabs_helper.sh`
- reaper:`claude-daily-operations/ops/chrome_tab_reaper.sh`(launchd 每 30 分,dry-run 期間只記不關)
- session 紀律:`skills/session-lifecycle/SKILL.md`
