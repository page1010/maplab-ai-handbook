# skills/agent-output-convention.md — Agent 固定存檔規範

> **狀態：正式（Owner 核准 2026-07-24；本機 main commit）。**
> 建立日 2026-07-24。來源 review bundle：`handoff/review-bundles/2026-07-24-agent-output-convention/`。

## 目的

根治「各 agent 到處亂存檔」——產出散落在 `~/.claude/state/`、`~/.claude/tools/`、
40+ 個 Cowork session 各自的 `outputs/`、`/tmp` 等，造成重工與「找不到」。
本規範建立**單一固定輸出根目錄**，所有 agent 一致遵守。

## 固定根目錄（外接硬碟）

```
/Volumes/MacExternal/MAPLAB_WORKSPACE/
├── outputs/<YYYY-MM-DD>_<任務短名>/   ← 交辦任務產出只准放這裡
├── state/                            ← 跨 session 狀態檔（取代 ~/.claude/state）
├── tools/                            ← 可重用腳本（取代 ~/.claude/tools）
└── index/                           ← 素材/資產單一真相索引與關聯圖
```

## 三條硬規則

1. **交辦任務產出** → `outputs/<YYYY-MM-DD>_<任務短名>/`。先開子資料夾再產檔。
2. **跨 session 狀態** → `state/`。不再寫 `~/.claude/state/`。
3. **可重用腳本** → `tools/`；**素材/資產索引** → `index/`。

## 禁止

- 禁止散存到 `~`（home）、`/tmp`、桌面、各 session 的 `outputs/`。
- 檔名須帶語意，禁止 `temp`／`test1`／`未命名`。

## 開工硬檢查（治本，非只寫散文）

每個 agent 開工時，於 `AGENT_STARTUP_PROTOCOL.md` Step 6 Startup Check
必填一欄 `輸出根目錄`，值必須指向 `MAPLAB_WORKSPACE`；缺欄或指向他處即視為未通過開工檢查。
詳見 review bundle 內 `AGENT_STARTUP_PROTOCOL.insert.md`。

## 邊界

- 本規範只管 agent 輸出／交辦資料夾。
- **不碰 Google Drive 同步設定**（另一條並行任務處理中）。
- 與 MacExternal 既有資料夾並存不覆蓋：`MAPLAB_BACKUP/`、`maplab-data/`（LINE 個資）、
  `MAPLAB_素材_依TA_20260724/`。

## 相關

- 規範源＋搬移紀錄：`/Volumes/MacExternal/MAPLAB_WORKSPACE/README_存檔規範.md`、`MANIFEST_搬移紀錄.md`
- 教訓依據：`pitfalls.md`「規則存在於散文等於不存在」→ 故本規範配一條開工硬檢查。
