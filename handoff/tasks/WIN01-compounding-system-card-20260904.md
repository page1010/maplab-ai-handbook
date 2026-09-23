# 任務卡（待主視窗推上 agent-bus）：win-01 建置「設計歸 Fable5、執行歸機器」複利系統

- 建卡：2026-09-04，依 Owner msg 4689「一樣的要把方法送到win os 的卡，也建置起這個複利系統」
- 狀態：**卡片內容完成、尚未上 bus**——agent-bus 目錄在本 bot 窗沙盒之外，推卡由主視窗執行
- 方法出處：skills/fable5-design-hermes-run-sop.md v1.0（Owner msg 4684 定調）

## 給 win-01 的任務內容

把 Mac mini 側剛成文的分工制度複製到 win-01 的 WP/SEO 線：

1. **角色**：Fable5＝設計 SOP＋驗收；win-01＝執行者（等同 Mac 側的 Hermes 角色）；Owner＝發布放行閘門。
2. **三條回饋線落地**：
   - prompt 回饋：win-01 每張卡完成時，回執必附「SOP 哪一步不清楚／哪一步失敗」段落（沒有就寫無），Fable5 據此修 SOP 遞版本。
   - 省額度：卡片回執記「本卡用了什麼模型/額度 vs 若由 Claude 高階跑的估耗」。
   - 進步紀錄：SOP changelog 進 git；win-01 執行紀錄照現行 receipt 規矩留檔。
3. **首批適用**：現行 SEO 10x10 管線卡（GAP 四篇視覺閘門→Owner 圈選→發布→回 live URL）照舊，但加上上面三條回饋要求；未來新卡一律帶「SOP 版本號」欄位。
4. **紅線不變**：未經 Owner 圈選不發布；不碰 secrets；發布只在 WP 草稿→Owner 核可後轉正式。

## 主視窗待辦

1. 把本卡轉成 agent-bus 格式推上 bus（win-01 約每 9 分鐘 pull 一次）。
2. 檢查 win-01 上次回執有無帶回饋段，沒有就在卡裡標明為必填。
