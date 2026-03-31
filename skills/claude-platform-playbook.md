# Claude 平台功能對照手冊 — MAPLAB 實戰版
版本：v1.0 | 建立：2026-03-31 | 來源：動區動趨 Claude 全攻略 + MAPLAB 實務經驗

---

## 用途

對照 Claude 平台功能與 MAPLAB 系統的使用方式。
每個功能標註：我們用了沒、怎麼用、還能怎麼進化。

---

## 一、Cowork 上下文體系

### 1.1 上下文資料夾（Context Folder）

| 功能 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| about-me.md | 定義角色、工作重心、服務對象 | ✅ 有 User Preferences（但在 auto-memory，非 context folder） |
| brand-voice.md | 品牌語氣、用語規範、寫作樣本 | ✅ skills/brand-voice-guide.md + skills/maplab-visual-spec.md |
| working-preferences.md | 執行規範、輸出格式、禁止行為 | ⚠️ 散在 AGENT_RULES.md，未獨立成 context file |

**進化建議：** 把 User Preferences 從 auto-memory 搬到 mounted workspace 的 context folder，Cowork 每次啟動都能讀到。

### 1.2 全域指令（Global Instructions）

| 設定 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| Settings > Cowork > Edit Global Instructions | 每次會話最先載入的底層行為規範 | ⚠️ 沒設定，靠 User Preferences 代替 |

**進化建議：** 在 Global Instructions 寫入：「啟動時先讀 auto-memory/MEMORY.md，再讀 GitHub repo 的 CURRENT_STATUS.md」。這樣每次新 session 都自動恢復上下文。

### 1.3 AskUserQuestion

| 功能 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| 讓 Claude 主動設計結構化問題 | 不用寫完美 prompt，讓 AI 問你 | ✅ 系統有提示用 AskUserQuestion |

---

## 二、Connectors（聯結器）

| Connector | MAPLAB 狀態 | 用法 |
|-----------|------------|------|
| Google Drive | ✅ 已接 | 讀報價單、圖片資料夾 |
| Gmail | ✅ 已接 | 讀郵件、客戶通訊 |
| Notion | ✅ 已接 | API Keys 保管室（非狀態來源） |
| Google Calendar | ❌ 未接 | 可接：活動日期管理 |
| Slack | ❌ 未接 | 不需要（用 Telegram） |

**進化建議：** 接 Google Calendar，配合報價系統自動查檔期衝突。

---

## 三、Scheduled Tasks（定時任務）

| 任務 | MAPLAB 狀態 | 問題 |
|------|------------|------|
| a0-github-sync（每小時） | 🔴 失敗 9 次 | 排程 session 沒有 mount repo |
| a4-colab-monitor（每 15 分鐘） | ⏸️ 已停用 | 同上問題 |

**根本問題：** Scheduled task 開在新 VM session，沒有 repo 也沒有 auto-memory。

**進化建議：** 排程任務的 prompt 要包含完整的環境設定指令：
```
啟動時：
1. mount /Users/pagemacmini/maplab-ai-handbook
2. 讀 auto-memory/MEMORY.md
3. 然後執行巡查
```
或者改用 Code task 觸發（Code task 有 cwd）。

---

## 四、Dispatch（遠端派任）

| 功能 | MAPLAB 狀態 | 問題 |
|------|------------|------|
| 手機連 Cowork | ✅ 可用 | 開新 session，不繼承原 Cowork context |
| Keep awake | ⚠️ 需手動開 | Mac mini 進入睡眠會中斷 |

**進化建議：** Dispatch 新 session 的第一句自動讀 auto-memory/MEMORY.md + CURRENT_STATUS.md。寫進 Global Instructions。

---

## 五、Claude Code 擴展體系

### 5.1 CLAUDE.md 分層

| 層級 | 位置 | MAPLAB 狀態 |
|------|------|------------|
| 專案級 | ./CLAUDE.md | ✅ 已改為指向器 |
| 全域級 | ~/.claude/CLAUDE.md | ❌ 沒用 |
| 本地覆蓋 | CLAUDE.local.md | ❌ 沒用 |

**進化建議：** 在 `~/.claude/CLAUDE.md` 寫入個人偏好（繁體中文、30 分鐘 checkpoint、Owner 資訊），這樣即使在其他 repo 開 Claude Code 也會帶上。

### 5.2 Rules Directory

| 功能 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| .claude/rules/*.md | 模組化指令，會話開始時自動載入 | ❌ 沒用 |
| 路徑作用域 | YAML header 指定 glob 匹配 | ❌ 沒用 |

**進化建議：** 把 AGENT_RULES.md 的 SECTION 拆到 .claude/rules/：
```
.claude/rules/
├── git-rules.md          # SECTION 2 Git 規則
├── checkpoint-rules.md   # SECTION 3 存檔規則
├── api-fallback.md       # SECTION 9 三層備援
└── credential-rules.md   # SECTION 8 權限治理
```
好處：token 更省（只載入相關的），維護更清晰。

### 5.3 Commands（斜槓命令）

| 功能 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| .claude/commands/*.md | 自定義 /project:xxx 命令 | ❌ 沒用 |
| $ARGUMENTS 傳參 | /project:fix-issue 234 | ❌ 沒用 |
| ! 反引號嵌入 shell 輸出 | 執行前先跑 git diff | ❌ 沒用 |

**進化建議（高價值）：**

```markdown
# .claude/commands/review.md
先執行以下命令取得變更：
!git diff --cached --stat
!git log --oneline -5

根據以上變更，執行 AGENT_RULES SECTION 7 全域檢查器：
1. 檢查是否有未更新的 CHANGELOG
2. 檢查是否有未同步的 CURRENT_STATUS
3. 檢查是否有遺漏的 credential
4. 回報結果
```

```markdown
# .claude/commands/checkpoint.md
執行 30 分鐘 checkpoint：
!git status
!git diff --stat

1. 把所有改動 commit（格式：checkpoint(Ax): [做了什麼] — [下一步]）
2. push 到 origin
3. 回報 commit hash
```

### 5.4 Skills（自動觸發技能）

| 功能 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| .claude/skills/*/SKILL.md | 自動偵測場景觸發 | ⚠️ 有 skills/ 但不在 .claude/skills/ |
| YAML header 設定觸發條件 | 基於描述匹配 | ❌ 沒用 |
| effort 參數 | 控制推理強度 | ❌ 沒用 |

**進化建議：** 把高頻 skill 搬到 .claude/skills/ 並加 YAML header：

```markdown
---
name: pre-commit-check
description: 在 commit 前自動檢查 CHANGELOG、CURRENT_STATUS、credential 是否需要更新
trigger: 當使用者要求 commit 或準備 push 時自動觸發
---

執行 AGENT_RULES SECTION 7 全域檢查器...
```

### 5.5 Hooks（生命週期鉤子）

| 功能 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| pre-commit hook | commit 前自動檢查 | ❌ 沒用 |
| post-tool-call hook | 工具呼叫後觸發 | ❌ 沒用 |
| 防止敏感資訊提交 | 攔截 credential 檔案 | ❌ 沒用（之前 Gemini key 洩漏就是這個問題）|

**進化建議（最高優先）：**

在 `.claude/settings.json` 加入：
```json
{
  "hooks": {
    "pre-commit": {
      "command": "grep -r 'AIza\\|ghp_\\|ntn_\\|sk-' --include='*.md' --include='*.json' --include='*.py' . | grep -v node_modules | grep -v .git",
      "description": "攔截 API key 洩漏",
      "fail_on_match": true
    }
  }
}
```

這能防止 Gemini API key 洩漏事件再次發生。

### 5.6 Agents（子代理）

| 功能 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| .claude/agents/*.md | 定義受限能力的子代理 | ❌ 沒用 |
| tools 限制 | 限制代理只能讀/不能寫 | ❌ 沒用 |
| model 選擇 | 低成本任務用 Haiku | ❌ 沒用 |

**進化建議：**

```markdown
# .claude/agents/security-auditor.md
---
name: security-auditor
description: 檢查 repo 中是否有 credential 洩漏風險
tools: [Read, Grep, Glob]
model: haiku
---

掃描所有檔案，找出可能的 API key、token、password。
回報位置和風險等級。
```

### 5.7 MCP 專案級配置

| 功能 | 說明 | MAPLAB 狀態 |
|------|------|------------|
| .mcp.json（專案級） | 團隊共享 MCP 設定 | ❌ 沒用 |
| 環境變數引用 | ${GITHUB_TOKEN} | ❌ 沒用 |

**進化建議：** 建 `.mcp.json` 讓所有 Code task 都能存取 Google Sheets / Drive（解決 Code task 不繼承 MCP 的問題）。

---

## 六、Computer Use（電腦操控）

| 功能 | MAPLAB 狀態 |
|------|------------|
| 點擊、輸入、開應用 | ✅ 用過（操作 Colab、終端機） |
| Chrome 擴展整合 | ✅ 有 Chrome MCP |
| prompt 注入風險 | ⚠️ 需注意不可信網站 |

---

## 七、優先進化清單（80/20 排序）

| 優先 | 項目 | 影響 | 難度 |
|------|------|------|------|
| 1 | **Hooks: pre-commit 防 key 洩漏** | 防再次出事 | 低（改設定檔） |
| 2 | **Commands: /review + /checkpoint** | 自動化 commit 品質 | 低（寫 md） |
| 3 | **Global Instructions 設定** | Dispatch/新 session 自動恢復 | 低（改設定） |
| 4 | **Rules Directory 拆分** | 降低 token、清晰維護 | 中 |
| 5 | **Skills YAML header** | 自動觸發不用手動 | 中 |
| 6 | **.mcp.json 專案級** | 解決 Code task MCP 繼承 | 中 |
| 7 | **~/.claude/CLAUDE.md 全域** | 跨專案偏好 | 低 |
| 8 | **Agents: security-auditor** | 安全掃描 | 低 |

---

## 八、不適用 MAPLAB 的功能（暫不投入）

| 功能 | 原因 |
|------|------|
| Agent Teams | 單人公司，不需要多 agent 並行協作 |
| Plugins Marketplace | 目前用 skills/ 就夠 |
| Voice Mode | 文字操作為主 |
| Channels (Telegram/Discord) | A1 Telegram 已棄用，改用 Cowork |

---

---

## 九、可直接部署的配置（從教學整理）

> 來源：Ahmed Nagdy - Learn Claude Code Interactively (claude.nagdy.me) + 動區動趨

### 9.1 Pre-commit Hook：防 credential 洩漏

在 `.claude/settings.json`（或 `~/.claude/settings.json`）：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "if": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "grep -rn 'AIza\\|ghp_\\|ntn_\\|sk-\\|password\\s*=' --include='*.md' --include='*.json' --include='*.py' --include='*.js' . | grep -v node_modules | grep -v .git | grep -v CHANGELOG | head -5 && echo 'BLOCKED: credential detected' >&2 && exit 2 || exit 0",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```
效果：每次 git commit 前自動掃描，發現 API key 就阻止提交。

### 9.2 Post-write Hook：自動格式化

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "#!/bin/bash\nINPUT=$(cat)\nFILE=$(echo \"$INPUT\" | python3 -c \"import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))\")\ncase \"$FILE\" in\n  *.py) black \"$FILE\" 2>/dev/null ;;\n  *.js|*.ts) prettier --write \"$FILE\" 2>/dev/null ;;\nesac\nexit 0",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### 9.3 Slash Command：/project:review

建 `.claude/commands/review.md`：
```markdown
先執行以下命令取得變更：
!`git diff --cached --stat`
!`git log --oneline -5`
!`git status`

根據以上變更，執行檢查：
1. 是否有未更新的 CHANGELOG
2. 是否有遺漏的 CURRENT_STATUS.md 變更
3. 是否有 credential 不小心進入追蹤
4. commit message 是否符合格式規範
5. 回報結果，如有問題列出修正建議
```

### 9.4 Slash Command：/project:checkpoint

建 `.claude/commands/checkpoint.md`：
```markdown
執行 30 分鐘 checkpoint：
!`git status`
!`git diff --stat`

1. 把所有相關改動 stage + commit
2. commit message 格式：checkpoint(Ax): [做了什麼] — [下一步]
3. push 到 origin
4. 回報 commit hash 和變更摘要
```

### 9.5 Skill：pre-commit-check

建 `.claude/skills/pre-commit-check/SKILL.md`：
```markdown
---
name: pre-commit-check
description: 在 commit 前自動檢查 CHANGELOG、CURRENT_STATUS、credential 是否需要更新。當使用者要求 commit、push 或提到 checkpoint 時觸發。
effort: medium
---

## 檢查項目

1. 掃描 staged files 是否含 API key pattern（AIza / ghp_ / ntn_ / sk-）
2. 如果改了 chrome-extension/ → 檢查 CHANGELOG.md 是否有對應版本
3. 如果改了系統狀態相關檔案 → 檢查 CURRENT_STATUS.md 是否同步
4. 如果改了 AGENT_RECALL_PROMPTS.md → 確認 CLAUDE.md 指向器不需要同步（因為已改為指向器）

## 輸出格式

✅ 全部通過 → 可以 commit
⚠️ 有遺漏 → 列出需要補的項目，問使用者要不要自動修正
```

### 9.6 Skill：security-auditor（子代理）

建 `.claude/skills/security-auditor/SKILL.md`：
```markdown
---
name: security-auditor
description: 掃描 repo 中的 credential 洩漏風險。當使用者提到安全、audit、key、洩漏時觸發。
context: fork
agent: Explore
effort: low
disable-model-invocation: true
---

掃描所有檔案（排除 .git / node_modules），找出：
1. API key pattern（AIzaSy / ghp_ / ntn_ / sk- / Bearer）
2. 寫死的密碼（password = / secret = ）
3. .env 檔案是否在 .gitignore 裡

回報：位置、風險等級、修正建議
```

### 9.7 常用快捷鍵參考

| 快捷鍵 | 功能 | 場景 |
|--------|------|------|
| Shift+Tab | 切換權限模式（default → acceptEdits → plan） | 複雜任務先規劃再執行 |
| Option+T | 切換 extended thinking | 需要深度推理時開 |
| Ctrl+O | verbose mode（看工具呼叫過程） | debug |
| /compact | 壓縮上下文 | 對話太長時 |
| /context | 視覺化上下文使用量 | 檢查是否快滿了 |
| /diff | 互動式 diff 檢視 | commit 前檢查改了什麼 |
| /effort high | 提升推理深度 | 複雜分析任務 |
| /btw | 問側邊問題不進入歷史 | 查語法不污染上下文 |

---

*本技能書基於動區動趨 2026-03-25 Claude 全攻略 + Ahmed Nagdy Learn Claude Code 教學整理。*
*對照 MAPLAB Kitchen AI 系統實際使用情況。每個進化建議可獨立執行，按優先順序一次做一個。*
