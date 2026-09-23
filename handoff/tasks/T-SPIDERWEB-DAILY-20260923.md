# T-SPIDERWEB-DAILY-20260923 — 每日財經 KOL 巡覽 → 查證 → 更新蛛網

Owner 原話(2026-09-23T21:26:29,msg 6045):
「我們不是有申請 agent 用 fb 然後是要追蹤財經的嗎? 可以加一個案子是每天幫我滑滑並查證後更新蛛網嗎 我們一開始有做功課去篩選過追蹤的 kol」

裁決:**准,立案**。屬標準決定,依 a0-decision-autonomy 由 A0 自行定案並留紀錄,不上呈。

---

## 0. 先講實況(2026-09-23 實查,不是印象)

Owner 記得的三件事**全部屬實,而且東西都還在**:

| Owner 記得的 | 實況 | 證據 |
|---|---|---|
| 有申請 agent 專用 FB | **有,而且用過兩次都成功** | 申請包 `investment-os/reviews/OPENCLAW-FB-ACCOUNT-APPLICATION-20260524/application_packet.md`;2026-05-25 冒煙測試 follow 成功 10 個粉專(`fb_follow_smoke_20260525.md`);**2026-09-12 還讀到 12 篇全文**(`reports/markyang_fb_radar/20260912/facebook_sources.json`,`collection_method: agent-login authorized account`) |
| 一開始有做功課篩 KOL | **有,20 條來源路由 + 4 個 YouTube + 3 個影子代理** | `investment-os/config/fb_radar_source_routes.yml`(version 1,generated_at 2026-05-25,20 source,台股 10 + 美股 10,含品質閘 `min_sources_for_model_preflight: 4` 等);`config/influencer_sources.yml`、`config/kol_shadow_agents.yml` |
| 要每天更新蛛網 | **蛛網只產過一份,17 天前** | `investment-os/state/spiderweb_20260906.md`,全 repo 索引只有這一份;格式由 Owner msg 4844 裁定為固定格式 |

**⭐ 真正的斷點不是缺功課,是鏈斷了而且還在假裝活著:**

1. **真正的 FB 抓取最後一次是 2026-06-11**(`fb_kol_intel/normalized/fb_loggedin_posts_2026-06-11_summary.json`),距今 **104 天**。
2. **但 `com.investmentos.fb-shadow-refresh` 每天 03:00 照跑照 exit 0**——payload 自 2026-06-02 起**逐字相同**(`draft_tasks: 354 / row_judgements: 776 / candidates: 354`,指向 `historical_corpus/.../2026-03-25_to_2026-04-25/`),**它在重播一份三到四月的舊 corpus**。`T-IOS-KOL-001` 白紙黑字寫「不得用舊 corpus 假裝今日報告」,**我們自己的排程正在違反自己的規矩**。
3. `kol_transcript_routing_*.md` 從 2026-08-26 到 2026-09-22 **天天有檔,每一份都寫「今日無 completed transcript」**——有檔不等於有料。
4. `kol_leaderboard_freshness_latest.json` 自評 **`unhealthy`**,推薦抽取停在 2026-08-13、**落後 40 天**。
5. `ai.openclaw.gateway` exit **-11(segfault)**、`com.openclaw.browser-autostart` exit **127**——整個 FB 計畫依賴的瀏覽器工人不健康。
6. `com.investmentos.kol-daily-research-refresh` 與 `kol-leaderboard-freshness` 最後 exit **1**。

**A0 自己也犯過一次**:2026-09-20 觸發 FB 登入牆時,A0 問 Owner「agent 專用 FB 到底有沒有」並把這條線**凍結等回覆**——答案一直躺在自家 repo 裡(9/12 才剛讀過 12 篇)。這是「研究第 0 步先查自家庫」再犯一次,已入本卡。

---

## 派工六欄(gate 可解析的一行式,細節見下方各節)

- **結果**: 每日產出一份 investment-os/state/spiderweb_YYYYMMDD.md,沿用 msg 4844 固定格式(事實層 F# 附來源與抓取時間、共振層引 F 編號、未掃節點清單、待驗區),外加當日 sources_manifest.json。
- **指標**: 事實層每條都有來源與時間戳;當日來源成功數 ≥ 4 且可用列數 ≥ 6,不足須在檔頭標「來源受限」;當日產出與前一日 payload 不得逐字相同。
- **期限**: Phase 0 自 2026-09-24 起每日一份,先跑七天看穩定度;Phase 1(需既有瀏覽器 session 的 20 條路由)待 OpenClaw 瀏覽器工人修好後起算,不設死線。
- **權限**: 可讀公開網頁與 RSS、可寫 investment-os/state 與 reports;禁止讀寫任何憑證類資訊、禁止第三方爬蟲 skill、禁止掛機大量爬、禁止進私密社團與私訊留言、禁止任何下單或買賣建議。
- **回報點**: 每日回報蛛網檔路徑與事實層條目數與來源成功筆數(只給計數與路徑);全數達標記 done,達標但來源受限記 partial,卡住記 blocked 並附卡在哪一步與錯誤訊息原文,不得用舊檔頂替。
- **動作可逆性**: 全部可逆,只做讀取與產檔,不刪既有資料、不改線上設定、不動錢、不下單;要停只需停排程,既有檔案保留當痕跡。

---

## 1. 結果(交付物,可驗收)

每日產出一份 `investment-os/state/spiderweb_YYYYMMDD.md`,**沿用 Owner msg 4844 裁定的固定格式**:

- **事實層 F#**:每行=節點／日期／事實／數字／**來源 URL 與抓取時間**,**零判讀**。
- **共振層**:每行**必須引 F 編號**,並標 共振＋／背離－／自走○。
- **未掃節點清單**:這輪沒掃到的部位一律列出來,不得沉默略過。
- **待驗區**:抓到但查證不過的 claim 放這裡,**不得升進事實層**。

附帶交付:當日 `sources_manifest.json`(每筆:source_id、取得管道、抓取時間、是否需登入、成功或 `auth_missing`)。

## 2. 指標(做到什麼算數)

- 事實層每一條都有 source URL + 抓取時間戳,**沒有來源的不得入檔**。
- 當日來源成功數 ≥ 4 且可用列數 ≥ 6(沿用 `fb_radar_source_routes.yml` 既有品質閘);不足就在檔頭標「**來源受限**」,不得照常出報告。
- **禁止重播**:當日產出與前一日產出的 payload 不得逐字相同;相同即判失敗(這條就是為了防第 0 節那個 bug)。
- 粉專主張不是事實:每一條有用的 claim 產生一個查證任務,查不過的留在待驗區。

## 3. 期限

- **Phase 0(零登入來源)**:2026-09-24 起,每日一份,先跑七天看穩定度。
- **Phase 1(需 agent FB session 的 20 條路由)**:待 OpenClaw 瀏覽器工人修好(現為 exit -11 / 127)或 Owner 指定可借的 Chrome profile 之後起算,不設死線,**不得為了趕期限去猜帳密**。
- 每七天一次回顧:哪些來源真的產出過事實層條目,沒產出的下架。

## 4. 權限

- 允許:讀公開網頁與 RSS;需登入時**只用 agent 專用 FB 帳號**的既有瀏覽器 session;寫入 `investment-os/state/` 與 `reports/`。
- **禁止**:讀或輸入任何帳密、2FA、recovery code、cookie、token、email、電話;把上述任一寫進 repo 或 Telegram;用任何要 cookie/帳密的第三方爬蟲 skill;掛機大量爬;進私密社團、私訊、留言互動;**任何下單、買賣建議或金額決策**。
- FB 登入相關分頁一律 `do_not_close_refresh_type_or_inspect`。

## 5. 回報點

- 每日:蛛網檔路徑 + 事實層條目數 + 來源成功／`auth_missing` 各幾筆,回報進 Telegram(**只給計數與路徑,不貼內容**)。
- 失敗時:終態寫 `partial` 或 `blocked`,附卡在哪一步與錯誤訊息原文;**不得用舊檔頂替**。
- 健康檢查:`bash maplab-ai-handbook/scripts/kol_chain_health.sh`,任何一段標 ✗ 就要在當日回報裡講明。

## 6. 動作可逆性

**全部可逆**。本案只做讀取與產檔,不刪除任何既有資料、不改任何線上設定、不動錢、不下單。唯一會動到的是新增 `state/spiderweb_*.md` 與報告檔;要停只要停排程,既有檔案保留當痕跡。

---

## 7. 執行者現況(照實記,不宣稱已派工)

**目前沒有一個活著的執行席位可以接 Phase 1**:
- invest 席位心跳停在 2026-08-21(#67),
- openclaw 瀏覽器工人 segfault,
- win-01 自己的 claude 登入過期(hermes 代打中,但帳號關一樣過不去)。

所以先這樣走:**Phase 0 由 A0 主線每日第一輪續接時自己跑**(晨會腳本已有同樣前例),**不假手尚未證明活著的席位**。Phase 1 等瀏覽器工人修好再談,修好之前不寫「已派工」。

## 8. 下一個動作(單一,可驗收)

跑 `bash maplab-ai-handbook/scripts/kol_chain_health.sh` 取得基線數字,然後產出第一份 Phase 0 蛛網 `state/spiderweb_20260924.md`,事實層條目數與來源清單一起回報。
