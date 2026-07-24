# 待插入 → AGENT_STARTUP_PROTOCOL.md

> DRAFT。等 Owner 批准才套用。**插入位置：`### Step 6. 輸出 Startup Check（強制）` 區塊內，
> 加入下列必填欄；並在 `## 執行中規則（強制）` 加一條硬規則。**

---

## (1) Step 6 Startup Check 新增必填欄

在 Startup Check 既有必填欄（如 `Skills loaded`）旁，新增一欄：

```
- 輸出根目錄: /Volumes/MacExternal/MAPLAB_WORKSPACE   ← 必填。本 session 所有產出的落點根。
  - 本次任務子夾: outputs/<YYYY-MM-DD>_<任務短名>/    ← 交辦任務必填
```

**硬檢查判準（缺一即開工檢查不過，等同未讀 CURRENT_STATUS）：**

1. `輸出根目錄` 欄存在且值為 `/Volumes/MacExternal/MAPLAB_WORKSPACE`。
2. 若 MacExternal 未掛載 → **停下回報 Owner**，不得 fallback 到 `~/.claude/state` 或 session outputs。
3. 交辦任務必須先建 `outputs/<YYYY-MM-DD>_<任務短名>/` 才開始產檔。

## (2) 執行中規則新增一條（硬規則）

```
### 規則 6：輸出路徑鎖定（2026-07-24）
- 所有產出只落 MAPLAB_WORKSPACE：任務產出→outputs/<日期_任務>/、跨 session 狀態→state/、
  可重用腳本→tools/、素材索引→index/。
- 禁止寫入 ~/.claude/state、~/.claude/tools、/tmp、桌面、各 session 的 outputs/。
- 依據：skills/agent-output-convention.md。理由：規則存在於散文等於不存在，故做成開工必填欄＋執行中硬規則。
```

## 為什麼是「硬檢查」不是「散文」

`pitfalls.md` 反覆記錄：規則只寫在散文裡，agent 照樣違規（如 launchd 違規讀寫 Documents 死 8 天）。
故把存檔規範做成 **Step 6 必填欄位 + 執行中規則**，讓「沒指定 MAPLAB_WORKSPACE 就不算完成開工」，
才會被 startup check / patrol 抓到，而不是靠自律。
