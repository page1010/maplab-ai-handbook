# SEO 結構修正提案(5301 根因 ②③④)— 全貌與任務目標
> 作者:mac-a0 (Fable5) | 2026-09-14 | Owner 5307 指令:立即修改前先寫全貌,送 codex+antigravity 回饋再動手
> 狀態:**提案中,未動手**。首頁切換是 Owner 直令,另卡進行(win01-homepage-golive-20260914),不在本提案等待範圍。

## 0. 任務目標(一句話)

把「對企業佈局必要、但卡在第一頁之外」的關鍵字,用最短路徑推進前三——不砍文、只集中票源與對準意圖。

成功指標(30 天,基準=2026-09-14 SC 12 個月資料):
- 台南外燴:7.5 → 前 5(主指標,10/14 鬧鐘覆盤)
- 台南企業茶會相關詞:20/18.2 → 合併後單一主文進第一頁(<10)
- 壽宴詞 CTR:0.36% → >1.5%(不動排名,只改標題)
- http 版首頁曝光佔比:25.1%/月 → 趨零(Google 合併)

## 1. 你看到什麼(現況事實,全部有出處)

- **F1 自己人分票**:場地意圖三篇分散 5.3~8.6 名;茶會意圖兩篇 20.0/18.2 名;buffet 兩篇、餐廳比較兩篇同意圖互搶。(SC 12m, data/sc-probe/;win-01 merge-group-a 已核對現站原文:2023 常青版 2,865 字 Elementor 為最強主體)
- **F2 http 幽靈首頁**:http://maplabkitchen.com/ 12 個月 23,788 曝光、排 17.8,搶走首頁 25.1% 曝光。win-01 9/14 實測:**301 沒壞**(四變體+五 UA 全 301、canonical 正確、站內 0 個 http 連結)→ 真因=Google 未完成正規化合併+**缺 HSTS 標頭**(VERIFIED)+轉址要跳兩次+疑站外訊號(GBP/名錄)仍指 http。
- **F3 企業茶會無專屬資產**:最高客單 B2B 意圖,全站沒有一篇以「台南企業茶會外燴」為主詞的文,只有點心角度一篇排 20。
- **F4 有排名沒人點**:壽宴 838 曝光排 9.2 CTR 0.36%;入厝趴前三 CTR 0.89%。內容能見度有了,標題不像答案。
- **F5 量測盲區**:現在只有 SC(進站前)。進站後哪個區塊流失、哪個 CTA 有效,無任何量測(Owner 5307 點名要)。

## 2. 要如何改(五個工作包,依 ROI 排序)

- **W1 HSTS+轉址壓一跳**(F2,技術,零內容風險):Cloudflare 開 HSTS max-age=300 觀察一週再拉長(win-01 建議,不可逆風險已知,先短效期);Bulk Redirect 讓 http://裸域 一跳直達 https://www;GSC URL Inspection 查 Google 認定的標準網址(mac-a0 有 webmasters 權限,試 API;不行=Owner 後台一分鐘);GBP 網站欄位確認 https www(Owner 或授權窗)。
- **W2 企業茶會主文**(F3):corporate-tea-party-desserts + catering-tips 兩篇併成「台南企業茶會外燴」主文,連 ICC 案例,舊 URL 301。稿=mac-a0 自有 Hermes;核對組裝=win-01(分工照 5296)。
- **W3 三組併文**(F1):場地三篇→2023 常青版;buffet 兩篇併一;餐廳比較併入 private-room。301 對照表 win-01 已交(301-map.csv),缺的是我的合併全文稿。
- **W4 標題/meta 改寫**(F4):壽宴+入厝趴+14 篇零點擊,只動標題與描述,內容不動。稿=mac-a0。
- **W5 行為量測**(F5):新首頁裝 Microsoft Clarity(免費,熱圖+滾動深度+錄影=Owner 要的「看到第幾屏走人/哪區黏著/哪張圖被點」)+GA4 事件(LINE 按鈕點擊=CTA 轉化)。加追蹤碼=動站,由 win-01 執行;Clarity/GA4 帳號建立需 Owner Google 帳號授權一次。

執行順序:W1(今天可做的部分)→W5(新首頁上線同週裝,基準期完整)→W2→W3→W4(W2-W4 依賴我的 Hermes 產稿,見 §4)。

## 3. 今天做什麼(2026-09-14 剩餘時段)

1. 本提案送 codex+antigravity,收回饋(阻塞 W1-W5 動手)。
2. 首頁切換卡已發 win-01(Owner 直令,不等回饋)。
3. 回饋抵達前,先產 W2/W3 合併稿+W4 標題稿的底稿(Hermes 免費鏈,只產草稿不動站,不屬「修改」)。
4. 回饋後:修訂提案→W1 派卡/自做 GSC 檢查→回報 Owner。

## 4. 萬一沒額度:接手線索

- 正典=maplab-ai-handbook handoff/landing-draft-v2-20260911/TASK_BRIEF.md(R27-R30)+本檔。
- 數據=handbook data/sc-probe/*.csv(12m);win-01 交付=agent-bus drafts/win-01/seo-inventory-20260914/(status-report/http-redirect-report/merge-group-a,b,c/zero-click-14/301-map.csv)。
- 欠稿=mac-a0 欠 win-01:三組合併全文+14 篇標題 meta,放 agent-bus shared/,win-01 等組裝(merge-group-a.md §0 點名)。
- 產稿通道=hermes_call 免費鏈(handbook 內建,四上游);Sheets/Drive 寫入=bot venv python+google-token.json+info.pop expiry 繞期限 bug。
- 追蹤中的卡=win01-homepage-golive-20260914(切換)、win01-seo-inventory-execute-20260914(partial)、seo-cases-drive-batch-20260910(已復活,4 篇案例文等 Owner 一次核對)。
- 紅線=draft-first 未圈選不發布;歌詞不進 WP;成本毛利不出對外檔;憑證不落檔不印出;cdo 不 commit。

## 5. 要 codex/antigravity 回饋的問題

1. W1 的 HSTS 短效期起步+Bulk Redirect 有沒有漏想的風險(子網域/信件/既有 Cloudflare 規則衝突)?
2. W2-W4 併文與改標題,有沒有會傷到既有前三詞(小型外燴價格 3.4/10人推薦 3.3)的路徑?
3. W5 Clarity+GA4 的裝法,對頁速/consent(隱私頁要不要更新)有沒有要先做的事?
4. 順序或 ROI 排錯的地方直說。
