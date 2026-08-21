你是 MAPLAB A3，運行在 Codex。
Telegram 派工 ID: TG-DISPATCH-20260821-084616-ads-performance-review
任務類型: 投放成效判讀任務
主責/協作: A3, A2, A1

## Cold Start
1. 先讀 CURRENT_STATUS.md。
2. 再讀 pitfalls.md，尤其是 Telegram command window / artifact substitution / Hermes fallback 相關教訓。
3. 再讀本派工列出的 task cards / docs。
4. 第一句先說：我是 [role]，環境 Codex，任務 [task]。

## Owner 原始指令
```text
seo部分你當核稿和確認方向的，沒問題就發，目前看行政外燴推薦Hr的部分把無麩質特殊飲食敘述拿掉，---格式通病，服務亮點不用自己說，動線好拿取說法不要再出現很AI,客戶與場景背景直接寫在標題，但問題是我不希望出現在標題是要去做，去研究客戶IG官網,圖片場景說故事，讚美一下，不是只在標題 +line可以上line圖示嗎？-----
```

## 最近 Telegram context
```text
source=data/telegram-logs/2026-08-21.md
# Telegram 對話紀錄 — 2026-08-21

> 自動產生，供 agent 恢復記憶用

## 2026-08-21 00:34:43
**Owner：** 呼叫fable5 你可以自行閱讀上面貼過來的嗎？

**Bot：** 🟢 [Claude]
可以，上面貼過來的對話我已經讀到了（Telegram 轉發內容整段都在我的 context 裡），不需要另外開檔案讀取。

不過要澄清一點：我目前這個 session 是 **A1（Sonnet 5）**，不是 Fable 5。如果你是想指定讓 Fable 5 處理這類任務，我這邊的身份跟模型底層對不上——要嘛你直接跟 Fable 5 的 session/視窗對話，要嘛請 A0 那邊的 dispatch 路由過去（看 commit `ae486eb` 提到的 "A0"-prefix 直接通道）。

需要我針對上面那段對話內容做什麼後續動作嗎？（例如整理成任務卡、回報 R0x 狀態、或針對 Meta 廣告指引繼續往下做）

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
