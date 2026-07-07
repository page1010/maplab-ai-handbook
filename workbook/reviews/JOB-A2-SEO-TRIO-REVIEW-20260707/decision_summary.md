# SEO 三人小組評審紀要 — 2026-07-07

**席位**：Claude/A2（決策整合）+ Codex（唯讀評審，`codex exec -s read-only`）+ Antigravity/agy（唯讀評審，`agy --print`，無 repo 存取）
**評審對象**：`docs/ad-funnel-battle-plan.md` / `docs/ansoff-mot-audience-matrix.md` / `docs/A2-ad-ops-improvement-plan.md` / `docs/real-cases-to-seo-matrix.md`
**評審包**：`review_packet.md`（同資料夾）｜**原始回覆**：`codex_review_raw.md` / `antigravity_review_raw.md`

---

## 三方意見摘要

### Q1 矩陣草案的盲點/風險

| | 意見 |
|---|---|
| **Codex** | 文件版本不一致是最大風險（婚禮/派對已非缺口，遊艇才是真缺口）；B3「詢價轉換率」定義太粗需拆解；受眾規模可能太窄；ThruPlay 不該當靜態圖冷層的 KPI；SEO cannibalization 需先定 pillar 頁；競品防守廣告注意品牌/法律風險 |
| **Antigravity** | 版本/狀態同步落差；NT$100/天太低易導致溫層受眾規模不足系統門檻、漏斗第二階段失效；高考慮期產品 + 跨平台歸因在 API 未接通前難以判讀 |
| **共識** | 兩者都指出「文件過期未回填」與「低預算下溫/熱層訊號不可靠」是兩大核心風險 |

### Q2 B3 試跑方案（NT$100/天）合理性

| | 意見 |
|---|---|
| **Codex** | 均分兩包太薄，建議 70/30（corp/edu）或先合併成一包；溫層不該等 Week 2，Day 1 就該建；2 週夠看方向不夠判定可複製；KPI 建議冷層看CTR/LPV/CPC、熱層看筆數+CPL |
| **Antigravity** | 建議 Week 1 **100% 集中 corp 線**（比 Codex 更激進）；試跑期建議拉長到 3-4 週；KPI 應分階段，不要在小樣本下就用「詢價率>3%」當唯一門檻 |
| **共識/分歧** | 兩者都同意「不要均分預算」「延長評估期」「KPI 要分階段」；分歧在集中比例（Codex 70/30 留一點edu、Antigravity 建議 100% corp）——**採納 Antigravity 更保守的版本**：Week 1 集中 corp，edu 暫緩不是留 30%，理由是 edu 和 B5 會展線本來就重疊，此階段目標是先看 corp 訊號乾不乾淨，行有餘力再說 |

### Q3 三個 landing 的專業意見

| Landing | Codex | Antigravity | 是否同意 Owner 07-05 決定 |
|---|---|---|---|
| 婚禮 | 同意開，但強調「不是新缺口」，應整合到單一主 landing，不要再開新 slug；注意隱私/臉部裁切、多頁互搶 | 同意開；既有頁需確認至少一頁排版/色票/語氣達到「整合型 landing」水準，否則承接不了廣告點擊 | ✅ 兩者皆同意，且都補充了「整合而非新建」「素材要真的到位」的執行提醒 |
| 性別派對 | 同意併入慶生線；但 SEO 頁可保留，廣告受眾不拆，素材仍要 message-match | 同意併入；建議慶生 landing 內設計一個小節/案例圖承接性別派對受眾 | ✅ 兩者皆同意，做法建議一致 |
| 遊艇 | 同意不做；建議先放特殊場域內文插圖觀察 GSC/私訊反應再評估升級 | 同意不做；更進一步建議直接轉作 B4 VIP/公關 cluster 的廣告輪播素材 | ✅ 兩者皆同意，Antigravity 的素材再利用建議更具體，已採納 |

**沒有出現任何一方反對 Owner 07-05 決定的情況**——三人小組的價值主要在補執行細節與風險提醒，不是推翻方向。

---

## Claude（A2）整合決策

1. **矩陣文件版本不一致** → 已在 `real-cases-to-seo-matrix.md`、`ansoff-mot-audience-matrix.md`、`ad-funnel-battle-plan.md` 回填 07-05 決策 + 本次覆核結論，消除「待確認」的過期表述。
2. **B3 預算配置** → 採納「Week 1 集中 100% 於 `cold-b-meeting-corp`，`cold-b-meeting-edu` 暫緩」（Antigravity 版本，較 Codex 的 70/30 更保守，理由是 edu 與 B5 會展線受眾重疊，優先看乾淨訊號）；溫層 Day 1 建立（Codex 意見，Pixel/ThruPlay 資料已可用不必等）；試跑期由 2 週延長為 3-4 週；KPI 改分階段（冷層 CTR/LPV/CPC，溫層 CTR>2%+頻率，熱層看「筆數+CPL」不是單一百分比）。已寫入 `ad-funnel-battle-plan.md` §5。
3. **三個 landing** → 維持 Owner 07-05 決定（婚禮開/性別派對併慶生/遊艇不做），補上三人小組的執行提醒（婚禮整合單一主頁不新開slug、性別派對慶生頁補案例小節、遊艇照片轉作VIP廣告素材）。已寫入 `real-cases-to-seo-matrix.md`。
4. **SEO cannibalization 提醒**（Codex）→ 補進 `A2-ad-ops-improvement-plan.md` Phase 2 廣告發布閘門的「矩陣對齊」檢查項。
5. **Landing page 規格**（Owner 指示：不限Elementor）→ 已寫入 `ad-funnel-battle-plan.md` §5：只需符合 `skills/brand-voice-guide.md` + `skills/maplab-visual-spec.md`（婚禮/週歲場景用裸粉`#D9C4B8`+暖米`#EDE5D8`），工具不設限。
6. **治理制度** → SEO 三人小組正式寫入 `ad-funnel-battle-plan.md` §7，含席位分工、召喚方式、Antigravity 唯讀邊界（不給 repo 存取）。

## 未採納 / 保留給 Owner 的項目

- Codex 提醒的「競品防守廣告品牌/法律風險」— 屬既有計畫 §3④ 範圍，本次未修訂文案本身，留待實際撰寫防守廣告文案時再處理。
- 兩位都提到 Phase 1（Ads API 唯讀盤點）尚未開始會限制歸因判讀的準確度——這是既有已知阻塞（Meta/Google API 未接通），非本次評審新發現，不重複列為待辦。
