# 待插入 → AGENT_RULES.md

> DRAFT。等 Owner 批准才套用。**插入位置：接在最後一個 SECTION 之後，新增 SECTION 26。**

---

## SECTION 26 — 固定存檔規範（Agent Output Convention，2026-07-24）

所有 agent 產出一律落單一固定根目錄 `/Volumes/MacExternal/MAPLAB_WORKSPACE/`：

- 交辦任務產出 → `outputs/<YYYY-MM-DD>_<任務短名>/`（先開子夾再產檔）
- 跨 session 狀態 → `state/`（取代 `~/.claude/state`）
- 可重用腳本 → `tools/`（取代 `~/.claude/tools`）
- 素材/資產索引 → `index/`

**禁止**散存到 home、`/tmp`、桌面、各 session 的 `outputs/`。

完整規範：`skills/agent-output-convention.md`。
開工硬檢查：`AGENT_STARTUP_PROTOCOL.md` Step 6 必填欄 `輸出根目錄` + 執行中規則 6。

### 關聯

- SECTION 24（可逆先行）— 建立/複製到 WORKSPACE 屬可逆動作，直接做。
- Step 6 Startup Check — `輸出根目錄` 缺欄＝開工檢查不過。
- 邊界：不碰 Google Drive 同步（另一任務）；與 MacExternal 既有 `maplab-data/` 等並存不覆蓋。
