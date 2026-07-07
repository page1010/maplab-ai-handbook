# Investment OS 功能盤點原始資料（Explore agent，2026-07-07）

來源：Explore subagent 對 `/Users/pagemacmini/Documents/New project/` 的系統性盤點，抽樣讀取各 report 分類最新 1-2 份實際輸出檔驗證內容，非猜測。

20 個已驗證使用者可見輸出：Real Holdings Sentinel、Exposure Ledger + Death List、Finance Morning Brief v2、Left-Side Narratives、Telegram Operator Bot、System Status Card、System Truth Map、Dashboard (Streamlit)、Nightly Progress Digest、Shadow Coach Report、Chip Daily Digest、Stock Future Opening Playbook、Futu Real-Time News/Quotes、Simulated Research Signal Ledger、Market Event Watch Island、Nightwatch System Audit、Shadow Findings、Quant Resource Bridge、Post-Market Risk Control、System Truth Gen + Governance Alerts。

完整逐項細節（trigger/code location/output destination/實際內容摘要）保留在本次 session 對話紀錄中，未逐字複製於此檔以控制檔案大小；如需完整原始逐項報告，重跑相同 Explore prompt 即可重現（純唯讀查詢，冪等）。

## 17 角色 registry 對照（design-level，來源 `config/investment_os_role_registry.json`）

IOS-MOMENTUM（每日動能經理）、IOS-KOL（網紅雷達經理）、IOS-FB（FB社群情報經理）、IOS-ALPHA（阿爾法共振經理）、IOS-BLACKSWAN（黑天鵝監控官）、IOS-INVENTORY（庫存審查經理）、IOS-MACRO（總經大師）、IOS-CHIP（籌碼經理）、IOS-LEFT（左側預期差經理）、IOS-RIGHT（右側交易經理）、IOS-EVIDENCE（研究證據經理）、IOS-SIM（模擬倉經理）、IOS-FAMILY（家族基金經理）、IOS-HEDGE（盤後對沖經理）、IOS-SURFACE（介面契約守門員）、IOS-HYGIENE（系統衛生官）、IOS-SENTINEL（實單哨兵）。

每個角色定義 mission/owns/background_jobs/data_sources/telegram_outputs/dashboard_workspace/output_contract/bad_data_rule，是「設計時應該有什麼」；20 個實際盤點輸出是「現在真的有什麼」。兩者對照可看出：多數 registry 角色都能在實際輸出裡找到對應（IOS-LEFT↔左側敘事候選、IOS-CHIP↔籌碼快報、IOS-SENTINEL↔實單哨兵），但 IOS-MOMENTUM 的「每日動能PM簡報」在本次盤點沒有找到獨立驗證的近期輸出檔案，只有 Telegram bot 按鈕入口，實際產出頻率/內容未驗證。
