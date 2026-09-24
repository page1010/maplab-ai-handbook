# MAPLAB Agent Core

## §0 這間公司在做什麼(2026-09-24 補,Owner msg 6091)

**MAPLAB 是台南的外燴品牌**,官網 `www.maplabkitchen.com`。核心生意是**到場外燴整案**,另有**外帶單品**;兩者**價格體系不同、不得混用**(見 `bot_a6/QUOTE_PLAYBOOK.md` 與 `QUOTE.md`)。常見場景包含開幕、壽宴、企業茶會、婚宴與證婚、日照中心活動、抓周。在地定價基準為**台南在地行情 × 1.35**(此係數與成本、毛利**一律不得出現在對外檔案**)。

同一個組織另有兩條內部線:**investment-os**(自營策略研究與模擬交易,不動真錢)與**音樂／內容線**(YouTube 頻道、SEO 文章、品牌視覺)。

**為什麼這一段要寫在最前面**:2026-09-24 實測,把 `AGENT_CORE.md` 加 `docs/company-values.md` 前 120 行(9,945 bytes)餵給 hermes 後問「MAPLAB 在做什麼」,hermes 的回答是**「文件未提及 MAPLAB 的具體產品、服務或商業模式」——而且他是對的**:那兩份檔案裡 `外燴`／`餐飲`／`台南`／`料理`／`辦桌`／`廚` 出現次數**全部是 0**。沒餵資料時他則整段編造成「產品研發、測試驗證顧問」。**不是 agent 不懂企業文化,是企業文化檔裡沒有寫這間企業。** 任何新增的文化條文都不得再假設讀者已經知道公司在賣什麼。

驗收方式(可重跑):`bash scripts/verify_hermes_model_fix.sh` 第 6 節(不餵資料)與第 7 節(餵資料)對照。

---

This file is the cold-start control contract. Detailed policy remains in `AGENT_RULES.md`; current work truth remains in `CURRENT_STATUS.md` and the active Task Card.

1. Read `CURRENT_STATUS.md`, `pitfalls.md`, and the active Task Card before action. Never rely on chat memory as state truth.
2. State role, environment, and exact task before acting.
3. For development: clarify the requested outcome, state the bounded version change, and ask only when a material choice cannot be discovered safely.
4. Every session leaves file-backed evidence, one Next Bounded Action, and a Resume Prompt. Stage only task-related files.
5. A repeated mistake becomes a `pitfalls.md` entry with trigger, root cause, remedy, prevention, and verification.
6. A third repeat, version churn without objective improvement, or an Owner challenge triggers the first-principles five questions before more execution.
7. Before asking the Owner to unblock work, try two safe methods, inspect available tools/agents, and report attempts plus the smallest five-minute Owner action.
8. Separate the business goal from the suggested method. Reuse existing assets and alternate authorized evidence when coverage is insufficient; read `docs/OPERATING_CULTURE.md` principle 8. Missing observations are not proof of absence, and candidate counts are not verified coverage.

External publishing, customer messaging, secrets, trading, irreversible changes, new spend, and private-data egress follow their explicit approval gates. A process exit, API 200, queued worker, or chat response is not completion without the promised artifact/live readback.
