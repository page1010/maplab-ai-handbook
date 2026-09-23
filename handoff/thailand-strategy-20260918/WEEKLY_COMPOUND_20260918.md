# 本週最大複利工作盤點(2026-09-18 ~ 09-25)

> 對應 Owner 5343(ts 2026-09-18T11:05:29):兩台電腦 OpenRouter 全開、接單工作流+GA4 行銷自動化、留泰國快速複製路徑。
> 主軸:每件工作同時滿足「本週有產出」+「路徑留檔可複製」兩個條件才上榜。

## A. 接單工作流(收單軸,最大複利)

現況鏈:訪客(新首頁 v5.1)→ LINE 詢價 → hermes 免費鏈輔助應答(不報價不承諾檔期)→ 人工報價(A4 Sheet)→ 訂金(Owner)→ 案後 48 小時入庫(照片/報價/案例文/關鍵字)。

本週動作(依序):
1. **詢價漏斗表**:建 Google Sheet 記每筆詢價(日期/來源頁/場景/人數/成交狀態),hermes 應答後人工補一列。零工程,當天可用。→ 複製路徑:表格模板直接複製,欄位不改。
2. **GA4+Clarity 佈碼**(需 Owner 授權開帳號):win-01 以 WP 外掛或 header 佈碼,Clarity 看捲動/CTA 熱圖,GA4 看來源與轉換事件(LINE 點擊=關鍵事件)。→ 複製路徑:留 INSTALL_PATH.md(帳號建立→佈碼位置→事件命名規則),泰國站照抄。
3. **案場 48 小時入庫 SOP 定版**:把 9/18 泰國計畫 R1 寫成 checklist 檔,下一場實跑。

## B. 兩台 OpenRouter 全開(算力軸)

- Mac 班表 free_quota_daily.sh 已上線(9/18 首跑 7/7):每日英文頁翻譯+gym 模擬題,queue 持續補件(本週目標:全站主力頁英文版草稿補齊+案例文底稿排程)。
- **win-01 今日實況:heartbeat stalled、0 張在跑**——它那把 key 整天閒置。本週動作:發新卡讓它 ①核對 6 篇英文草稿事實(對照中文原頁,守門者角色)②接手每日一篇案例文底稿(它有 44 夾 Drive 素材與五套 SOP)。→ 複製路徑:兩機分工模式(Mac=生成/派工,win=核對/上稿)原樣搬泰國。

## C. codex 投資線現況(只讀確認,不插手)

方向確認(讀 cogov_work_registry + 任務卡 INVESTMENT_OS_AUTONOMOUS_RESOURCE_ROUTER_20260910):
- 架構:Wave 0 資源路由器(額度感知,codex 稀缺算力/確定性工作免模型/hermes 財務唯讀隔離)→ #24 點時資料 → #25 統計防火牆 → #23 券商/成本引擎 → Demo → Live(Owner 閘)。方向健康,紀律嚴(quota 耗盡=執行者狀態非任務失敗;金融絕不走 web 版 hermes;不開實盤)。
- 已完成:US 動量驗證實驗(結論:alpha 未確立)、策略方向研究切片、#23 context bridge(PR28);Router Wave 0 本體尚未動工。
- **缺口(Owner 5343 點名)**:現行卡只寫 eToro Demo;**永豐/富途模擬單不在 DAG 內**;「所有 agent 進工作流」只定義了 hermes 財務唯讀,win-01/Fable5/antigravity 的進入點沒寫。
- 本週動作:開 codex 工作單(不改方向、不搶 Wave 順序)請他補規劃:①BrokerAdapter 介面同時涵蓋 永豐(Shioaji 模擬)/富途(OpenD SIMULATE)/eToro Demo 三家,統一模擬單合約 ②各 agent 進入工作流的角色契約表(誰能做什麼類工作、從哪個介面進)。紅線:全程模擬,金鑰 Owner 管,富途解鎖交易 GUI-only。

## D. 泰國快速複製包(路徑軸,本週只留檔不建站)

REPLICATION_PATH.md 累積中,本週要留下:詢價漏斗表模板連結、GA4/Clarity 安裝路徑、兩機分工說明、英文內容資產清單、48 小時入庫 checklist。原則:每完成 A/B 一項,同回合補一段路徑筆記,不事後補課。

## 本週驗收(9/25 對照)
1. 詢價漏斗表建好+至少記到真實詢價。
2. GA4/Clarity:Owner 授權後佈碼完成;未授權則 INSTALL_PATH.md 先寫好等開帳號。
3. Mac 班表天天跑(日報連續);win-01 復工且英文稿核對回執至少一批。
4. codex 收到補齊工作單且回了規劃(不催實作)。
5. REPLICATION_PATH.md 五段齊。
