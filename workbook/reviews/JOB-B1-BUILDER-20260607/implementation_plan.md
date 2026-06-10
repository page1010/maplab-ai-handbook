# JOB-B1-BUILDER-20260607 · Guild Ops Board (遊戲化部門作戰板)

**Role:** B1 Investment OS Builder · **Date:** 2026-06-07 · **Type:** feature_build + dashboard surface

## Owner 需求 (原話拆解)
1. 遊戲畫面版 dashboard:每個邏輯/角色都有自己的工作,工作 = 某個策略,並畫出流程。
2. 範例 = KOL:RSS .py → 通知地端模型(Hermes/OpenClaw)→ NotebookLM 或 Antigravity 解法(語音轉文字+摘要)→ 地端發 Telegram + 更新 Dashboard。
3. 每個角色設 dashboard,並**擬人化**簡單畫出該部門成員(如 KOL 部門有地端模型 / OpenClaw / Codex / Antigravity,因額度多互為備援)。
4. 設計與存檔要考量:這個管理者可能在**任何 AI agent 對話框**被召喚出來。
5. 因額度上限 → 成員**互為備援**。
6. **所有任務必須閉環**:即使沒訂閱、沒額度也要穩定運作。

## 設計決策
- **單一 HTML、零外部依賴**:直接滿足「沒訂閱/沒額度/沒網路也能開」。無 CDN、無 fetch、資料內嵌。
- **資料即真相**:21 個部門資料抽自 `config/investment_os_role_registry.json`(16 IOS 角色)+ B1–B4 維運迴圈 + A0 調度;成員池 = registry `workers` + topology memory 的 runtime(codex/antigravity/gemini/claude/py)。
- **擬人化**:每部門 1 句 persona + avatar;成員卡帶 quota bar(local 無限 / high 高額度 / meter 計量 / session 需登入)。
- **流程圖**:每部門一條 vertical flow,每步標 actor chips + 守則(bad-data 規則來自 registry `bad_data_rule`)。
- **閉環降級階梯 (FAILSAFE LADDER)**:每部門 La 理想線 → Lb 額度備援 → Lc 本地降級 → **FLOOR(本地 .py + 誠實降級)**。FLOOR 共用,鐵則「絕不用標題/舊資料假裝完成」直接編碼,呼應 pitfalls 與 KOL 斷點教訓。
- **召喚**:每部門 detail 抽屜內含可複製的 recall 文字,可貼進任何 AI agent 對話框;與 `chrome-extension/task-modules/<ROLE>.json` 召喚機制同邏輯。

## 範圍邊界
- 只新增檔案,不改任何既有 runtime / registry / 腳本。
- 不下單、不讀 secrets、不碰生產 DB。
- 不宣稱已驗證 owner-facing Telegram/Dashboard runtime(此為**離線展示面**,非生產渲染器)。
