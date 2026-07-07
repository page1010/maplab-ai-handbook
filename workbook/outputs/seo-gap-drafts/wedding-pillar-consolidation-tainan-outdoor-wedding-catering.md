# 婚禮 Pillar 整合方案 — tainan-outdoor-wedding-catering（草稿，未發布）

版本：v1.0 | 建立：2026-07-07 | 狀態：**草稿，等 Owner/A1 核准後才可寫入 WordPress**
維護：A2（結構決策）+ Codex（草稿產出，`codex exec -s read-only`）
證據狀態：`verified_public`（6 篇文章 slug/title 皆於 2026-07-07 WP REST 現查存在）

---

## 為什麼選這篇當 pillar，不開新 slug

台南婚禮外燴目前有 6 篇既有文章，互相有內容重疊風險（SEO 三人小組 Codex 覆核提醒：「婚禮頁已很多，需先定 pillar，不然會分散權重」）。不新建頁面，而是從既有 6 篇裡選 1 篇當 pillar：

**Pillar（主頁）**：`tainan-outdoor-wedding-catering`（post 1215，台南戶外婚禮外燴｜草坪、古蹟、海邊場地外燴規劃）

**選這篇的理由**：
1. 內容本來就最完整（場地類型/注意事項/菜單推薦/FAQ 齊全）
2. 完全對上 Meta 廣告受眾 `cold-c-wedding` 鎖定的熱層關鍵字「台南戶外婚禮外燴」（`docs/ad-buildout-plan.md` P2 段）
3. ⚠️ **修正一個廣告文件的錯誤**：`docs/ad-funnel-battle-plan.md` / `docs/ad-buildout-plan.md` 原本寫的廣告導流 landing slug 是 `outdoor-wedding-catering-venue`，2026-07-07 REST 查證這個 slug **回 404，不存在**。真正 live 的是 `tainan-outdoor-wedding-catering`。已在下方「待辦」註記，廣告投放前需同步修正兩份廣告文件裡的 slug。

**5 篇子頁（保留獨立，不刪除、不合併內容，只是明確定位成 pillar 的延伸）**：

| Slug | 定位 | 保留原因 |
|---|---|---|
| `wedding-catering-vs-banquet-tainan` | 決策比較型（外燴 vs 傳統桌菜） | 不同搜尋意圖（比較型），不與場地型 pillar 重疊 |
| `tainan-small-wedding-catering` | 規模區隔型（50人以下） | 明確人數區隔，不同意圖 |
| `tainan-wedding-welcome-canapes` | 菜單子項型（迎賓茶點） | 菜單細節頁，服務 pillar 的下游需求 |
| `tainan-wedding-catering-cost` | 費用型 | 費用搜尋意圖獨立且高頻，維持獨立頁面（不合併進 pillar） |
| `tainan-wedding-celebration-party-catering` | 形式區隔型（證婚派對） | 現代證婚派對 vs 傳統婚宴的形式選擇，獨立意圖 |

---

## 草稿 A — Pillar 頁開場段落（取代原本開場段第一段）

> 定位：讓讀者一開始就知道這篇涵蓋各種戶外場地的婚禮外燴規劃，同時清楚知道更明確的情境（室內/比較/小型/迎賓茶點/費用/證婚派對）在文末有更精準的頁面可以去。

```
在台南溫暖的陽光下，草坪、古蹟庭院、海邊與私人院落，都能成為婚禮外燴的一部分。這篇會先從戶外婚禮的場地條件、天氣備案、電源、餐點保鮮、取餐動線與菜單配置談起，幫你把一場台南婚禮外燴需要先想清楚的事整理成完整指南。若你正在比較室內宴會、傳統桌菜、小型 50 人以下婚禮、迎賓茶點、費用預算，或想把證婚儀式做成更親近的派對形式，文末也整理了不同情境的延伸頁面，方便你依照婚禮的樣子往下看。
```

**寫入位置**：取代現有 `<p>` 第一段（原文「在台南溫暖的陽光下，以自然為背景完成人生中最重要的誓約...」那一整段）。

---

## 草稿 B — 文末「延伸閱讀」cluster 連結區塊（取代現有兩則模糊連結）

> 定位：明確的 pillar → 子頁導流，取代現有「台南外燴完整攻略」「台南婚禮外燴完整方案」這兩則連結對象不明確的延伸閱讀。

```markdown
## 依你的婚禮形式，看更貼近的規劃

**[婚宴外燴 vs 傳統桌菜：哪個更適合你的夢幻婚禮？](https://www.maplabkitchen.com/wedding-catering-vs-banquet-tainan/)** — 如果你正在比較飯店桌菜、流水席與外燴 buffet，這篇會從場地自由度、菜單形式、佈置與流程感受幫你整理差異。

**[台南小型婚禮外燴推薦｜50人以下草坪婚禮、居家婚宴](https://www.maplabkitchen.com/tainan-small-wedding-catering/)** — 適合 50 人以下、草坪證婚、居家婚宴或只邀請親近家人的婚禮，重點放在人數、桌面配置與取餐節奏。

**[台南婚禮迎賓茶點外燴｜讓賓客第一口就驚艷的茶點規劃](https://www.maplabkitchen.com/tainan-wedding-welcome-canapes/)** — 如果想讓賓客抵達時有一口輕巧的迎賓茶點，這篇會整理 canapes、甜點桌與飲品站的配置方式。

**[台南婚宴外燴費用完整指南｜各規模婚禮預算怎麼抓](https://www.maplabkitchen.com/tainan-wedding-catering-cost/)** — 想先抓預算、了解 50 人、100 人、150 人不同規模大概怎麼配置，可以從餐點、人力、器皿、場地條件與服務範圍一起看。

**[台南證婚派對外燴｜打造親密歡樂的現代婚禮慶典](https://www.maplabkitchen.com/tainan-wedding-celebration-party-catering/)** — 偏好比傳統婚宴更輕鬆的形式，或想在證婚後用輕食 buffet、甜點與飲品延續交流，這篇會比較貼近現代證婚派對的規劃方向。
```

**寫入位置**：取代現有文末「延伸閱讀：台南外燴完整攻略｜婚宴、企業、派對一次搞懂」「延伸閱讀：台南婚禮外燴完整方案」這兩則連結（LINE CTA 之後）。

---

## 品牌語氣/視覺檢查（skills/brand-voice-guide.md + skills/maplab-visual-spec.md）

- ✅ 無禁用字詞（最頂/超值/保證滿意/CP值/佛心/便宜又大碗/錯過可惜/趕快預約/名額有限/一生一次不能省/不訂會後悔）
- ✅ 無說服式對比句型（不是…而是…）
- ✅ 無把話說死（一定/保證/最適合/絕對/唯一/最好）
- ✅ 場景式敘述，非空泛形容詞堆砌
- ✅ 婚禮客戶專屬語氣：浪漫但克制、有場景感、不過度煽情
- 色票建議：本頁若重新設計視覺區塊，依 `skills/maplab-visual-spec.md`「婚禮外燴：裸粉 `#D9C4B8` + 暖米 `#EDE5D8`」場景專屬色；**不限定用 Elementor 製作**，符合語氣+色票即可（2026-07-07 Owner 指示）

---

## 待辦（需 Owner/A1 核准才能執行）

- [ ] 草稿 A/B 實際寫入 WordPress post 1215（目前只是 repo 內草稿）
- [ ] **修正 `docs/ad-funnel-battle-plan.md` 與 `docs/ad-buildout-plan.md` 裡錯誤的廣告 landing slug**：`outdoor-wedding-catering-venue`（404）→ `tainan-outdoor-wedding-catering`（真實 live slug）
- [ ] 確認 5 篇子頁內文尾端是否已內鏈回 pillar（`tainan-outdoor-wedding-catering`），若無則各自補一條
- [ ] `docs/seo-keyword-map.md` 婚禮群組正式標記 pillar/child 關係（見 T-A2-CANNIBALIZATION 任務）
