# 額度值班輪替制 v1.0（quota-duty-rotation）

依據：Owner 2026-09-04 msg 4738「把他（Antigravity）加進來在沒人有額度值班時可以輪替，現在階段性完成後你要接回去」。
配套：agent-hq README 模型分工表、docs/governance/antigravity-execution-lease-ontology-v0.1.md（agy 唯讀保證未驗證）、handoff/dispatch/window-bus-20260904.md。

## 輪替順位（誰有額度誰上，管理權永遠回到 Fable5）

| 順位 | 值班者 | 什麼時候上 | 值班內容 | 權限邊界 |
|---|---|---|---|---|
| 1 | Fable5（Claude） | 有 Claude 額度時 | 主導：派工、驗收、回 Owner | 全權（紅線照舊） |
| 2 | Codex | Claude 額度盡、Codex 有額度 | 接手執行中任務卡、續跑管線 | 依既有 Codex offload 規則 |
| 3 | Antigravity（agy） | 1、2 都沒額度 | 唯讀值班：巡邏狀態、監看 bus/監控 log、起草回報與方案 | **唯讀**。產出只寫 bus 的 outbox/antigravity/ 當提案；不改生產檔、不發布、不碰 secrets（agy 沙盒唯讀保證未驗證前不升格，見 ExecutionLease 治理檔） |

## 交接規則

1. **下班交接**：值班者把「做到哪、卡在哪、下一步」寫進 `agent-bus outbox/<自己>/duty-handover-<日期>.md`（Fable5/Codex 亦同，寫 handbook handoff/ 也可）。
2. **接回**（Owner 拍板的鐵則）：Claude 額度一回復，Fable5 必須主動接回主導——第一步讀最新 duty-handover 與 window-bus，驗收值班期間產出，該轉正的轉正、該丟的丟。輪替者不自動延任。
3. **Antigravity 召喚方式**：`scripts/agy_duty_patrol.sh`（版控腳本，包 agy --print 值班 prompt，產出落 bus）。GUI 視窗跑的東西不算值班產出——不落地等於沒做。
4. **誰觸發輪替**：正常由 Fable5 交棒；Fable5 無預警斷線時，watchdog 或 Owner 一句「agy 值班」即可觸發腳本。

## 目前狀態（2026-09-04 19:10）

- 本階段完成，**Fable5 已接回主導**（本 session 運作中，額度已回復）。
- Antigravity 轉 standby：bus 通道 inbox/antigravity/、outbox/antigravity/ 已開，等無額度時輪值。
- agy 腳本已入庫但**尚未實跑驗證**（無頭模式跑 agy 需權限核准；首次驗證排在下次有人在電腦前或主視窗接手時）。

## Changelog

- v1.0（2026-09-04）：初版，依 msg 4738 建制。
