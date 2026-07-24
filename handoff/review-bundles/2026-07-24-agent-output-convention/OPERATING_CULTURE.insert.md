# 待插入 → docs/OPERATING_CULTURE.md

> DRAFT。等 Owner 批准才套用。**插入位置：接在「原則 4 — STATE 讀寫紀律」之後，新增原則 5。**

---

## 原則 5 — 固定存檔（不亂放，存固定位置、開子資料夾）

### 規則

所有 agent 的產出只存單一固定根目錄 `/Volumes/MacExternal/MAPLAB_WORKSPACE/`，
每個交辦任務開一個 `outputs/<YYYY-MM-DD>_<任務短名>/` 子資料夾。
跨 session 狀態存 `state/`、可重用腳本存 `tools/`、素材索引存 `index/`。

### ❌ 錯誤示範

產出散在 `~/.claude/state/`、`/tmp`、桌面、以及每個 Cowork session 各自的 `outputs/`
——同一份東西存好幾個地方，事後找不到、重工。

### ✅ 正確示範

開工先在 Startup Check 填 `輸出根目錄: /Volumes/MacExternal/MAPLAB_WORKSPACE`，
任務產出全部落 `outputs/2026-07-24_素材索引-TA場景/` 這類子夾。

### 為什麼

散落存檔是「找不到」與重工的主因。固定位置＋任務子夾讓產出可被索引、可交接。
配套硬檢查見 `AGENT_STARTUP_PROTOCOL.md` Step 6，規範全文見 `skills/agent-output-convention.md`。
