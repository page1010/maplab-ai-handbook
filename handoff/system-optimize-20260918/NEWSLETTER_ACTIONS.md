# Claude Code 更新套用提案(Owner 5316-5318,2026-09-14 貼文;本檔 2026-09-18 交付)

Owner 原話(5316,2026-09-14T20:14:01):「用來優化一下系統---」+ Claude 官方 newsletter 全文(5317 續貼;5318「可以上我mail看詳情」→ bot 窗無信箱通道,以貼文為準)。

## A. 建議直接套用(等 Owner 點頭或主視窗執行;bot 窗依規不自改設定檔)

### A1. 每模型記住 effort 檔位(額度紀律)
~/.claude/settings.json 加:
```
"modelSettings": {
  "claude-fable-5": { "effortLevel": "high" },
  "claude-opus-4-8": { "effortLevel": "medium" }
}
```
效果:換模型不用手動調 /effort;bot 續接窗若用較低階模型收尾(Owner 慣用「換模型收尾/sonnet接上」),effort 自動對檔。對齊章程「週四 22:00 額度紀律」。
前提:Claude Code ≥ 2.1.260(本窗無法跑 claude --version 確認,主視窗先查)。

### A2. 子代理預設用較低階模型
```
"env": { "CLAUDE_CODE_SUBAGENT_MODEL": "opus" }
```
效果:主對話留 Fable,子代理(搜檔/盤點類)走 Opus——直接落實「Fable5 派工為主、不自燒高階額度」。跑 /tasks 可驗證子代理實際用哪個模型。

### A3. SessionStart/SessionEnd hooks + 具名 session(治斷線)
newsletter 案例:hooks 把每個 session 的 id/名稱/目錄寫進檔案,重開機後照檔案逐一 resume,不靠人腦記。
我們的病(9/9 已驗屍):本 session 逐字稿 133MB,claude -p --resume 重載 >900s 被 SIGKILL→Telegram 靜默、watchdog 補跑(5316 這則本身就是補跑活例)。
建議:SessionEnd hook 寫 session id+最後活動時間到 cdo state/session_ledger.jsonl;watchdog 讀 ledger 判斷「該 resume 哪條、還是該開新 session 接手」。與 codex 修卡 CODEX_A0_RESUME_TIMEOUT_FIX_20260909 合併處理,不另開第二套機制。
註:hooks 屬自動化行為,必須進 settings.json 由 harness 執行——需 Owner 核可後由主視窗改(8/31 既定規則:權限/設定檔 bot 不自改)。

## B. 先不動
- **Fable 5.1 升級**:官方明說更急躁、舊 prompt 要重調。生產 bot 穩定優先;主視窗先跑 /claude-api prompt-audit 評估,通過再談升級。
- /diff 面板、桌面 app 彈窗、Files pane:互動視窗的 QoL,headless bot 用不到。
- bypassPermissions 位置要求(須在 user settings):現行設定若有衝突,主視窗檢查時一併處理。

## C. 待用清單
- **桌面版背景 computer use(beta,macOS 15+,Settings→General 開)**:Claude 可背景點 GUI 不佔滑鼠鍵盤。潛在用途=Drive「改串流」偏好設定的 GUI 授權(external-drive 線卡點)、GA4/Clarity 若 win-01 卡登入牆時的本機備援。
- /claude-api cost-optimize、hillclimb:等有量化壓額度需求時再用。

## D. newsletter 下半段補充(5317,2026-09-14T20:14:04;2026-09-18 補入)
- **D1(升版時優先驗證)2.1.259 平行 session 修復**:多視窗不再互蓋 ~/.claude.json(workspace trust 重問、MCP/專案狀態消失的元凶)。我們 bot 常態開平行續接窗(split-brain 實錄多次),升版後此項直接受益;連同 2.1.267「/model 與 --resume 後快取命中改善」一起驗證。
- **D2 bypassPermissions 只認 user settings(2.1.257)**:專案 .claude/settings.json 裡的 defaultMode: bypassPermissions 會被忽略。主視窗檢查現行設定位置,有放專案層的要搬 ~/.claude/settings.json。
- **D3 額度檢討工具**:/skill-doctor 找沒在用的 skill(省 context)、/cost 看快取命中率與 miss 原因、PreModelSwitch/PostModelSwitch hooks 可記錄或攔模型切換(配合「換模型收尾」慣例可留審計線)。留給週四 22:00 額度紀律檢討時用。

## 執行順序建議
1. 主視窗回歸時:查版本→套 A1+A2(低風險純設定)→A3 併入 codex 修卡設計→檢查 D2 設定位置。
2. 升版後驗證 D1;額度檢討日用 D3。
3. Owner 只需一句「照 A 做」即可,無需逐項圈。
