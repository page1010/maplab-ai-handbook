# launchd/_archive — 退役記錄

此目錄存放已退役的 launchd plist。  
`gen_system_truth` 掃描邏輯明確排除此目錄，不會將這裡的 plist 視為「待安裝」或產生 Tier-B load remediation。

---

## com.maplab.b-role-maintenance.plist.retired-20260629

**退役日期**: 2026-06-29  
**原 ghost job label**: `com.investmentos.b-role-maintenance`（前綴錯誤，應為 `com.maplab.*`）  
**腳本路徑**: `/Users/pagemacmini/maplab-ai-handbook/scripts/b_role_local_maintenance.sh`  
**腳本狀態**: **不存在**（遺失，從未建立）  
**執行紀錄**: `runs=0`，從未執行過，launchctl `last exit code: never exited`

**退役原因**:
1. 腳本遺失 — 沒有腳本就不能 load
2. 前綴錯誤 — 原 label `com.investmentos.*` 掛 maplab 路徑的腳本
3. 功能從未啟用過 — 純候用 plist，無歷史執行

**功能概念**: B-role 地端模型維護交接（本機 Ollama 模型版本管控、切換、清理）

**⚠️ Owner 決策待定**:  
> 功能概念可能有價值。若要啟用：
> 1. 補寫 `maplab/scripts/b_role_local_maintenance.sh`
> 2. 從此 `_archive/` 恢復 plist 至 `launchd/`（去掉 `.retired-*` 後綴）
> 3. `launchctl load ~/Library/LaunchAgents/com.maplab.b-role-maintenance.plist`
>
> 若永久廢棄：此條目保留作治理歷史，無需額外操作。

**交叉參照**: IS repo `CHANGELOG.md` 2026-06-28 退役段落
