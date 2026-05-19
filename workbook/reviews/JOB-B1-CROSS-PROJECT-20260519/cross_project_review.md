# Cross-Project Governance Review — B1

日期：2026-05-19
狀態：completed for prompt setup / no runtime change

## 結論

MAPLAB 的強項是治理外殼：Chrome Extension role module、Task Card、必讀來源、輸出契約、pitfalls、resume prompt。Investment OS 的強項是 runtime：Telegram、dashboard、SQLite、Hermes、OpenClaw browser/CDP、report artifacts。

目前 Investment OS 看起來「比較差」的原因，不是功能少，而是缺少一個像 MAPLAB Agent Commander 這樣的可複製接手面：角色、來源、風險、輸出、暫停/恢復規則沒有被包成一張 handoff envelope。

## 已觀察事實

- MAPLAB Agent Commander 可在 Chrome side panel 切換角色、顯示 module、copy handoff prompt、檢查 Markdown sync。
- B1 在 MAPLAB Extension 裡可載入，但仍是 InnerFlowLab 內容創作角色。
- Investment OS dashboard 可讀 runtime DB 與多個 tab，包含研究、Rumour、Hermes、決策、籌碼、模擬等。
- Investment OS 有 `AGENT_CORE.md`、`CURRENT_STATUS.md`、`pitfalls.md`、OpenClaw operator manual、report/evidence 目錄。
- Investment OS 缺的是跨模型可直接使用的角色 prompt / task module，而不是單一功能或更多模型。

## 建議

1. B1 暫停內容發文專案，保留為跨專案治理顧問 prompt。
2. B1 不常駐，不做財經教學日常任務；只有在 Owner 問「為什麼這套不好用 / 怎麼移植 MAPLAB 治理」時啟用。
3. Investment OS 先不用急著做 Chrome Extension。最短路徑是先做 `Invest OS role handoff card`：角色、必讀檔案、禁止事項、輸出契約、手機可見驗收。
4. B1 每次輸出要分清楚：觀察事實、推論、建議、要 A1 做的具體改動。
5. 任何涉及投資的內容只能做 report UX / prompt / governance 建議，不做買賣建議。

## 對 Investment OS 的具體提案

- 建 `PM Brief Contract`，讓 Telegram 第一屏和 dashboard 首屏回答同一組問題：
  - 今天資料新鮮嗎？
  - 哪些結論可用，哪些不可用？
  - 下一個動作是研究、觀察、刷新資料，還是不要動？
  - 這些判斷來自哪個 evidence？
- 建 `role handoff card`，先用 Markdown，不急著寫 Extension：
  - role: Investment OS PM Brief Reviewer
  - read first: `CURRENT_STATUS.md`、`pitfalls.md`、operator manual、runtime DB freshness note
  - forbidden: no orders, no secrets, no raw local model as fact
  - outputs: `pm_brief_review.md`、`telegram_copy.md`、`validation_report.md`
- 每次 Telegram/report 修改後，要求手機可見 smoke test，而不是只看 script pass。

## 不建議

- 不建議讓 B1 變成常駐財經老師，使用頻率不足，會增加維護成本。
- 不建議把 Investment OS 直接搬 MAPLAB Extension 架構；先把 handoff card 和 report contract 做順。
- 不建議讓本地模型自由接管投資語意；本地模型可做備料，但事實和決策邊界要由 deterministic runtime / DB / review contract 管住。
