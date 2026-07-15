# MAPLAB AI 系統 — 額度中斷接管程序
# Quota Outage Failover Runbook

> 版本：v1.0 | 建立：2026-07-12 | 維護者：A1
> 適用情境：A0 Cowork 額度耗盡 / Claude Code 無法使用 / Mac mini Claude 失聯

---

## 一、問題識別

### 觸發條件（任一即觸發本 Runbook）

| 條件 | 判斷方式 |
|------|---------|
| A0 Cowork 出現「額度不足」提示 | Claude Desktop 顯示 rate limit / billing error |
| Claude Code terminal 無法啟動 | `claude` 指令無回應或 `401 Unauthorized` |
| Telegram bot 無回應超過 30 分鐘 | 送 `/ping` 沒有收到任何回覆 |
| A1 巡查停止 | CURRENT_STATUS.md 超過 8h 無 patrol commit |

### 不觸發本 Runbook 的情況

- Telegram 網路短暫延遲（5 分鐘內恢復）→ 等待
- Mac mini 睡眠（SSH 進去 `caffeinate` 喚醒）→ 不算中斷
- 單次指令 timeout → 重試一次

---

## 二、分級接管程序

### Level 1：A0 Cowork 額度中斷（Claude Code 仍可用）

**誰負責**：Owner 一行指令觸發 A1 Claude Code 備援

**觸發指令**（在 Claude Code terminal 執行）：
```bash
# 確認 A1 bot 仍在線
launchctl list | grep maplab

# 立即接管 A0 調度職責
cat distill/backup-recalls/A1-codex-backup-recall.md
```

**A1 接管清單**：
- [ ] 確認 Telegram bot 仍回應
- [ ] 讀 CURRENT_STATUS.md 更新狀態
- [ ] 列出 A0 負責的積壓工作（從 `state/owner-action-queue.md`）
- [ ] 繼續執行 patrol 排程（`scripts/patrol.sh`）

---

### Level 2：Claude Code 額度中斷（Codex/agy 仍可用）

**誰負責**：Owner 用一行指令召喚 Codex 備援巡查

**觸發指令**：
```bash
# 召喚 A1 Codex 備援巡查（唯讀，約 60-90 秒完成）
codex exec --read-only -m o4-mini --print \
  --cwd /Users/pagemacmini/maplab-ai-handbook \
  "$(cat distill/backup-recalls/A1-codex-backup-recall.md)

任務：立即執行一輪 A1 Codex 備援巡查。
1. cat CURRENT_STATUS.md | head -60
2. git log --oneline -5
3. grep -l 'CRITICAL\|🔴' handoff/tasks/*.md 2>/dev/null | head -5

輸出格式（繁體中文）：
## [A1 Codex 備援巡查 — $(date '+%Y-%m-%d %H:%M')]
### 系統健康：[最新 commit hash] [時間]
### CRITICAL 任務：[列名]
### Owner 優先行動：[3件 × 5分鐘]
### 備援期間無法處理：[清單]"
```

**輸出保存**：
```bash
# 把輸出存入 state/ 目錄（launchd 偵測用）
codex exec --read-only ... > state/codex-patrol-$(date '+%Y%m%d-%H%M').md
```

**launchd 自動偵測（可選）**：
```bash
# /Library/LaunchAgents/com.maplab.codex-failover-check.plist
# 每 4 小時確認 Claude Code 是否恢復，未恢復則跑 Codex 備援巡查
# 觸發條件：claude --version 失敗超過 2 次連續檢查
```

---

### Level 3：Codex + Claude 都中斷（僅 agy 可用）

**誰負責**：Owner 用 agy 進行快速問答

**觸發指令**：
```bash
# agy 備援問答（純文字，無 repo 存取）
agy --print "$(cat distill/backup-recalls/A1-antigravity-backup-recall.md)

Owner 問：[在此描述問題]
請用四段式（問題/成因/解法/選項）回答，繁體中文"
```

**agy 能做的事**：
- 解釋任何系統概念
- 草擬 Owner 優先行動清單
- 回答基於 2026-07-12 凍結快照的系統問答

**agy 不能做的事**（重要）：
- 確認當前系統狀態（需等 Claude 恢復後 `cat CURRENT_STATUS.md`）
- 更新任何文件或發送任何訊息
- 確認 bot 是否在線、launchd 是否運行

---

### Level 4：全部中斷（Codex + agy + Claude 均不可用）

**誰負責**：Owner 手動查閱 repo 文件

**緊急自救指引**：
```bash
# 1. 查最新系統狀態
cat /Users/pagemacmini/maplab-ai-handbook/CURRENT_STATUS.md | head -80

# 2. 查最緊急任務
grep -l "CRITICAL\|🔴" /Users/pagemacmini/maplab-ai-handbook/handoff/tasks/*.md

# 3. 查最新 git log
git -C /Users/pagemacmini/maplab-ai-handbook log --oneline -10

# 4. 確認 bot 是否在線
launchctl list | grep maplab
# 預期輸出：PID com.maplab.telegrambot / com.maplab.a6bot
```

**聯絡方式**：
- Telegram bot 如果在線：送 `/status` 查詢系統狀態
- 如果 bot 不在線：`sudo launchctl unload && load ~/Library/LaunchAgents/com.maplab.telegrambot.plist`

---

## 三、備援輸出存放位置

所有備援執行個體的輸出一律存入：

```
state/
├── codex-patrol-YYYYMMDD-HHMM.md   ← Codex 備援巡查報告
├── agy-qa-YYYYMMDD-HHMM.md         ← agy 問答紀錄
└── failover-log-YYYYMMDD.md         ← 本次中斷紀錄（開始/結束/積壓工作）
```

---

## 四、Claude 恢復後的消化積壓程序

Claude 恢復後，**A1 第一件事**：

```bash
# 1. 讀備援期間的輸出
ls state/codex-patrol-*.md state/agy-qa-*.md 2>/dev/null | sort -r | head -10

# 2. 整合積壓工作清單
cat state/codex-patrol-*.md | grep "\[ \]" | sort -u

# 3. 補更新 CURRENT_STATUS.md 備援期間狀態
# （在 ## 最新事實核對 最頂端加入備援期間摘要）

# 4. 補推播積壓的 Telegram 通知
bash scripts/notify_owner.sh "Claude 恢復，備援期間積壓 X 項任務，正在消化..."

# 5. 執行一輪完整 patrol 更新系統狀態
bash scripts/patrol.sh

# 6. checkpoint.sh 存檔
bash scripts/checkpoint.sh "A1" "Claude 恢復後消化備援期間積壓工作" --notify
```

---

## 五、備援 Recall 快速查閱表

| 角色 | Codex 版 | agy 版 |
|------|---------|--------|
| A0 調度秘書 | `distill/backup-recalls/A0-codex-backup-recall.md` | `distill/backup-recalls/A0-antigravity-backup-recall.md` |
| A1 系統總管 | `distill/backup-recalls/A1-codex-backup-recall.md` | `distill/backup-recalls/A1-antigravity-backup-recall.md` |
| B1 IS Builder | `distill/backup-recalls/B1-codex-backup-recall.md` | `distill/backup-recalls/B1-antigravity-backup-recall.md` |

---

## 六、Owner 一行觸發指令（最常用）

```bash
# A1 Codex 備援巡查（Level 2）
codex exec --read-only -m o4-mini --print --cwd /Users/pagemacmini/maplab-ai-handbook "$(cat distill/backup-recalls/A1-codex-backup-recall.md) 任務：立即備援巡查，輸出 3 件最緊急問題 + Owner 優先行動清單"

# A0 agy 快速問答（Level 3）
agy --print "$(cat /Users/pagemacmini/maplab-ai-handbook/distill/backup-recalls/A0-antigravity-backup-recall.md) Owner 問：[問題]"

# 查系統健康（Level 4，純本機）
cat /Users/pagemacmini/maplab-ai-handbook/CURRENT_STATUS.md | head -60 && git -C /Users/pagemacmini/maplab-ai-handbook log --oneline -5
```

---

*版本：v1.0 | 建立：2026-07-12 A0 派工備援召喚機制任務*
*下次更新時機：Claude 恢復後，消化積壓期間若發現新的中斷模式，A1 負責更新本文件*
