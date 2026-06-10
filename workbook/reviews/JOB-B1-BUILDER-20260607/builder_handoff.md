# Builder Handoff — JOB-B1-BUILDER-20260607

## 一句話
做了一個**單檔、離線可開**的遊戲化部門作戰板:21 個部門各有擬人成員、策略流程圖、與「沒額度也能跑」的閉環降級階梯,每個經理都能被任一 AI agent 對話框召喚。

## 怎麼用
- **開啟:** 直接雙擊 `workbook/dashboards/maplab-ops-game-dashboard.html`(或已在 Claude Code preview 面板)。
- **瀏覽:** 上方分頁切策略/部位/平台/維運/調度;右側搜尋經理或成員。
- **看細節:** 點任一部門卡 → 右側抽屜:管轄策略 / 流程圖 / 降級階梯 / 成員(含 quota bar)/ Surface / 召喚提示。
- **召喚:** 抽屜底「複製召喚提示」→ 貼進任何 AI agent 對話框,即把該經理叫醒並帶上鐵則。

## 資料來源 (要改內容時動這裡)
- 角色資料:HTML 內 `const D = [...]`(21 部門)。對應真相 = `config/investment_os_role_registry.json`。
- 成員池:HTML 內 `const W = {...}`(9 種共用成員 + quota 分級 `QMAP`)。
- 改完不需 build step,存檔即生效(純前端)。

## 與既有系統的關係
- 召喚邏輯對齊 `chrome-extension/task-modules/<ROLE>.json` 的 `packaged_role_recall_excerpt`;若 registry 角色變動,理想做法是讓 `tools/ai_workbook/build_extension_task_modules.py` 同步生成此面板資料(尚未接,見下方未做項)。

## 未做 / 後續卡 (留給 B1 或 Owner 決定)
1. **資料自動同步**:目前 `D[]` 為手抄 registry。可寫小 generator 從 registry → 注入 HTML,避免雙真相漂移。
2. **即時狀態燈**:接 launchd / `agent-command-center status` 讓「運作中/有斷點」變即時。
3. **直接召喚按鈕**:目前是複製貼上;若要一鍵丟進 Chrome 擴充對話框,需接 extension messaging。

## 轉交對象
- 內容/資料正確性與 freshness → **B2 Reviewer**(已開 review_request.md)。
- 版本紀錄 / pitfalls 回寫 → **B3 Archivist**。
- 是否值得接即時狀態 / 自動同步(避免過建)→ **B4 System Patrol**。
