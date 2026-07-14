你是 MAPLAB A3，運行在 Codex。
Telegram 派工 ID: TG-DISPATCH-20260714-215943-ads-performance-review
任務類型: 投放成效判讀任務
主責/協作: A3, A2, A1

## Cold Start
1. 先讀 CURRENT_STATUS.md。
2. 再讀 pitfalls.md，尤其是 Telegram command window / artifact substitution / Hermes fallback 相關教訓。
3. 再讀本派工列出的 task cards / docs。
4. 第一句先說：我是 [role]，環境 Codex，任務 [task]。

## Owner 原始指令
```text
任務進行的如何 除了派工可以回報詳情嗎？
```

## 最近 Telegram context
```text
source=data/telegram-logs/2026-07-14.md
# Telegram 對話紀錄 — 2026-07-14

> 自動產生，供 agent 恢復記憶用

## 2026-07-14 09:19:20 `[dispatch-local]`
**Owner：** 1.用api key是不是就不能吃免費額度 為什麼不讓hermes去貼去調用 2.昨天說的R01-R10進行到哪裡 3.幫我用三個agent 討論模式，去閱讀我的網站，以及過往貼給你的廣告資訊，為我在關鍵字與廣告受眾佈局做更新，meta,TA輪廓長相、幾歲、興趣，地點、對應素材。至少三組，並研究Meta廣告，在設定目的與符合我們的關鍵字矩陣策略要怎麼設定最好，寫一份讓我照著做的指引。近期素材見----https://drive.google.com/drive/folders/1pKfGSOZXBpG7qXcJrW5T7aoHX4nqB1Tt

**Bot：** ✅ 已建立派工包：TG-DISPATCH-20260714-091918-ads-performance-review
這不是只回覆：已落檔，並寫入 Codex clipboard bridge。
- 主責：A3（協作：A3, A2, A1）
- worker：Codex primary; OpenClaw read-only browser proof if logged-in Ads UI is needed
- status：queued_for_codex
- openclaw_worker：will_start
- packet：workbook/telegram-dispatch/TG-DISPATCH-20260714-091918-ads-performance-review/packet.json
- prompt：workbook/telegram-dispatch/TG-DISPATCH-20260714-091918-ads-performance-review/prompt.md
下一步：worker 必須用這個 dispatch_id 回報；沒有 receipt 就不能再說已召喚。

---

```

## 必讀來源
- handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md
- projects/maplab-ads-monitor.md
- projects/seo-ads-agent.md

## 本輪目標
讀近 7/14/30 天 Google Ads + Meta Ads 成效，拆出花費、曝光、點擊、CTR、CPC、轉換、CPA、ROAS，輸出保留/暫停/調整預算與素材下一步。

## 需要取得/驗證的資料
- Google Ads: spend, impressions, clicks, CTR, CPC, conversions, CPA, ROAS by 7/14/30 days
- Meta Ads: spend, impressions, clicks, CTR, CPC, conversions/leads, CPA/ROAS by 7/14/30 days
- Landing-page conversion context from A2 when ad data suggests page or SEO mismatch

## 邊界
- read-only first; do not change budget, campaign status, targeting, creative, Pixel, GTM, or landing pages
- if login/API data is missing, report the missing source and the exact 5-minute Owner action
- recommendations must separate verified metrics, inference, and approval-needed changes

## 輸出契約
請回報：
1. Startup Check：角色、環境、任務、資料來源。
2. 已做的事：真的讀了哪些檔案/資料或執行了哪些 read-only checks。
3. 結論：分成 verified facts、reasonable inference、missing data、next action。
4. 若需要 Owner：只列 5 分鐘內可完成的具體動作。
5. 若要寫回：列出要改的檔案與理由，未核准不得碰 live external settings。
