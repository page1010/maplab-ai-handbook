# Meta 受眾 + 素材 + 佈局 Buildout 計畫

版本：v1.1 | 建立：2026-07-05 | 更新：2026-07-05 | 狀態：**Owner 已清障，進入執行準備**
隸屬：`docs/ad-funnel-battle-plan.md` 延伸執行層（§6）
維護：A2

> ⚠️ 硬規則：不改「外燴系統」Drive 試算表；不碰 A6；這是計畫草案，產完 Owner 審。

---

## 1. 缺口盤點

| 缺口類型 | 現況 | 缺什麼 |
|---|---|---|
| Meta 溫層 retarget | 完全空白（最痛缺口） | ThruPlay≥50% 受眾 → 現在就能建；網站訪客 → ✅ Pixel 已確認，可建 |
| Meta B 端冷受眾 | 全是 C 端（週歲/高收入媽媽） | 開幕/會議/公關/VIP/藝文各情境的職業受眾包未建 |
| Meta C 端受眾擴充 | 週歲/家庭已跑 | 入厝/長輩壽宴 + 對應 Lookalike 未建 |
| 溫層素材（案例 proof） | 幾乎沒有 | 用真實案例（富信/會展/入厝）做的「我做過這個」視覺 — **全漏斗最缺** |
| 熱層素材（CTA 款） | 無 | 菜單展示 + 份量說明 + 報價 CTA 款 4:5 — 搭配 Google 熱層收割 |
| Google 競品防守 | 無 | 「玖二品生活外燴廚房」品牌詞未設防守廣告 |

---

## 2. 受眾 Buildout（按優先序）

### 🔴 P0：溫層 retarget（本週內可建，資料現有）

**這層是現在最快可動的槓桿。** 不需等 Pixel，不需新素材，用現有影片觀看資料立即建。

| 受眾名稱 | 建立條件 | 資料來源 | 有效期 | 說明 |
|---|---|---|---|---|
| `warm-thruplay-50pct` | ThruPlay ≥ 50%（看完一半以上影片） | Meta 現有影片互動資料 | 30 天 | 最強意圖信號，現在就能建 |
| `warm-fb-page-engaged` | 粉專互動者（按讚/留言/分享/傳訊/點選 CTA）| FB 粉專互動 | 30 天 | 覆蓋曾跟品牌有過互動的人 |
| `warm-ig-engaged` | IG 帳號互動者（同上） | IG 互動 | 30 天 | 特別涵蓋看過 reels 互動的人 |
| `warm-website-visitors` | 網站訪客（任何頁面） | Meta Pixel | 30 天 | ✅ **可建**（Pixel 已確認安裝） |
| `warm-landing-visitors` | 特定 landing 訪客（依情境） | Meta Pixel + UTM | 14 天 | ✅ **可建**（Pixel 已確認；需搭 UTM 參數） |

**各溫層受眾的 Lookalike（建完 Custom Audience 後自動可建）：**
- `lal-thruplay-1pct`、`lal-fb-engaged-1pct`、`lal-website-1pct`（1% 最像，3% 覆蓋廣）

---

### 🟠 P1：B 端冷受眾（依情境分包，抄廣告巡邏表）

每個情境一個受眾包，搭配對應廣告素材才能做 message-match。

| 情境 | 受眾包名稱 | 職業興趣定向 | 搭配 cluster | 備注 |
|---|---|---|---|---|
| **開幕茶會** | `cold-b-opening` | 職業：總經理/執行長/營運長/採購主管；興趣：開幕/店面裝潢/創業 | `opening_tea` | 適合新品牌/新店開幕場景 |
| **機構/學術會議** | `cold-b-meeting-edu` | 職業：教育機構/大學行政/醫療機構/研究員；興趣：研討會/學術會議/繼續教育 | `meeting_refreshment` | 對上工研院/社工公會案型 |
| **企業會議茶點/HR** | `cold-b-meeting-corp` | 職業：人力資源/行政助理/秘書/辦公室主任；興趣：企業培訓/員工活動 | `meeting_refreshment` | 對上 HR 文章線（WP 1992） |
| **公關/品牌活動** | `cold-b-pr` | 職業：公關主任/行銷經理/品牌管理；興趣：品牌活動/媒體公關/企業 CSR | `corporate_forum` | 對上三立論壇/ESG 案型 |
| **VIP 接待/建案** | `cold-b-vip` | 職業：房地產開發/室內設計師；興趣：豪宅/奢侈品牌/財富管理/預售屋 | `brand_vip` | 對上擎川建案場型 |
| **藝文/文化場域** | `cold-b-arts` | 職業：展覽策劃/博物館/藝廊；興趣：當代藝術/文化活動/博物館/設計展 | `cultural_venue` | 優先序最低（待 SEO 文章上線後評估） |

---

### 🟡 P2：C 端擴充（補週歲/家庭以外的場景）

> **Owner 定案 cluster 預設（2026-07-05）**：婚禮線開；性別派對併入慶生線；遊艇先不做。

| 情境 | 受眾包名稱 | 定向方式 | 說明 |
|---|---|---|---|
| 入厝宴客 | `cold-c-housewarming` | 生命里程碑：新屋主；興趣：室內裝潢/喬遷 | 搭配說事實木地板/醞舞流開幕案例照 |
| 長輩壽宴 | `cold-c-senior-party` | 年齡 40-60（子女輩）；興趣：長輩照護/家庭聚餐/生日宴 | 文案對子女說話，不對長輩說 |
| **婚禮外燴** ✅ 開 | `cold-c-wedding` | 生命里程碑：訂婚/結婚；年齡 25-40；興趣：婚禮籌備/婚紗攝影/婚宴 | 已有 `maplab-outdoor-wedding-catering-venue.webp` 可用；戶外婚禮場景差異化強 |
| **慶生（含性別派對）** | `cold-c-birthday` | 現跑冷層延伸；性別派對受眾隨 birthday 定向一起涵蓋 | 性別派對不獨立受眾包，語氣友善即可，受眾定向沒有差異化必要 |
| **遊艇外燴** ❌ 先不做 | — | — | 受眾規模太小、無對應 landing；此版本排除，待日後評估 |
| Lookalike 擴充 | `lal-c-birthday-1pct` | 現有週歲/家庭成交客為種子 | 最快有 Lookalike 的 C 端來源 |

---

## 3. 素材 Buildout（按漏斗階段）

> **核心洞察**：素材要匹配受眾的「心理狀態」，不是匹配案例類型。
> 冷受眾不認識你 → 不要推報價；溫受眾已看過你 → 推案例 proof 和理由；熱受眾在搜尋 → 直接 CTA。

### 素材需求對照表

| 漏斗階段 | 素材款式 | 版位格式 | 現況 | 行動 |
|---|---|---|---|---|
| 🔵 冷層（Meta 認知） | 故事/場景款（情境植入，不賣） | 9:16 Reels / Stories | ✅ **現有夠**（週歲/家庭影片 NT$0.12 ThruPlay 效率佳） | 繼續跑；B 端補同格式素材 |
| 🟡 溫層（retarget proof） | 真實案例照片輪播 + 軟提案文字（「上次你看的這個，我做過幾場」）| 4:5 輪播 / 單圖 | ❌ **最缺**——目前溫層素材幾乎為零 | 用 6 月真實案例圖製作（見下） |
| 🔴 熱層（收割 CTA） | 菜單展示 + 份量說明 + 「加 LINE 估價」直接 CTA | 4:5 單圖 / Stories + 滑動 | ❌ **缺**——目前無這類素材 | 靜態圖製作（優先 B3 HR 茶會線） |

### 各 Cluster 溫層素材來源（真實案例優先）

| Cluster | 建議素材場次 | output_filename（草案，查 asset_conversion_manifest 確認）| 合規前置 |
|---|---|---|---|
| `meeting_refreshment` | 富信飯店社工公會（0614）★、大台南會展工研院（0612）★ | maplab-meeting-refreshment-[富信/會展]-hero.webp（待 A4 產出）| needs_face_crop 必查 |
| `opening_tea` | 說事實木地板（0621）、醞舞流舞蹈教室（0614） | maplab-opening-tea-[木地板/舞蹈]-hero.webp（待 A4 產出）| needs_logo_crop 必查 |
| `brand_vip` | 建案百慶擎川（0613） | maplab-corporate-forum-cathay-wealth-management-hero.webp（已驗 ad_ok） + 擎川案例（待 A4）| needs_face_crop 嚴查 |
| `corporate_forum` | 三立論壇（0625） | maplab-forum-[三立]-hero.webp（待 A4 產出）| needs_logo_crop（三立）嚴查 |
| C 端週歲/入厝 | 現有週歲影片 + 入厝案例（如有）| 現有冷層影片可截幀 | — |

> 真實案例圖的 HEIC→webp 轉換 + 人臉隱私處理，依 `skills/seo-image-from-album.md` 流程，由 A4 執行。A2 不自行裁圖。

### 素材版位對應（Meta 廣告管理員設定）

| 版位 | 格式 | 用途 |
|---|---|---|
| FB/IG Feed | 4:5（1080×1350）| 溫層輪播、熱層 CTA 單圖 |
| IG Reels / FB Stories | 9:16（1080×1920）| 冷層故事款 |
| IG Stories（靜態）| 9:16 | 溫層 proof 單圖 |
| Meta Audience Network | 同 Feed 格式 | 冷層擴散 |

---

## 4. 漏斗佈局（每 Cluster 一條迷你漏斗）

### 總架構

```
【Meta 冷層】職業興趣受眾 / Lookalike
    ↓ 看影片 / 互動 / 進站
【Meta 溫層 retarget】ThruPlay≥50% / 網站訪客 / 互動者
    ↓ 看案例 proof → 點擊 landing
【Landing】已對應的 slug（HR茶會/開幕/建案VIP…）
    ↓ LINE 詢價（唯一成交點）
【Google 熱層】高意圖搜尋字詞（現跑 Campaign4/5）
    ↓ 直接 → Landing → LINE
【Google 競品防守】「玖二品生活外燴廚房」品牌詞
    ↓ 出現自家廣告（場景文案，不攻擊競品）
```

### 各 Cluster 迷你漏斗

| Cluster | 冷層受眾包 | 溫層條件 | 熱層字詞（Google）| Landing slug | UTM campaign |
|---|---|---|---|---|---|
| B3 HR/會議茶點 ★ | `cold-b-meeting-corp` + `cold-b-meeting-edu` | ThruPlay≥50% + 看過 `/corporate-tea-party-desserts/` | `台南茶會點心推薦`、`台南會議茶點外燴`、`台南點心外燴` | `hr-admin-meeting-catering-guide-tainan` / `corporate-tea-party-desserts` | `b3-hr-tea` |
| B5 會展/政府會議 ★ | `cold-b-meeting-edu` | ThruPlay≥50% + 看過會展相關頁 | `大臺南會展中心外燴`、`台南研討會茶點`、`政府會議外燴` | `corporate-tea-party-desserts`（主）| `b5-forum-expo` |
| B1 開幕茶會 | `cold-b-opening` | 看過 `/tainan-corporate-opening-tea-catering/` | `台南開幕茶會外燴`、`台南店面開幕外燴` | `tainan-corporate-opening-tea-catering` | `b1-opening` |
| B4 VIP/建案 | `cold-b-vip` | 看過 VIP/建案頁 | `台南建案外燴`、`台南 VIP 接待外燴` | `vip-expo-catering-business-meeting` | `b4-vip` |
| C1 週歲/慶生 | 現跑冷層（繼續）| 現有影片互動者 | `台南周歲外燴`、`台南慶生外燴推薦` | 週歲 landing（確認 slug）| `c1-birthday` |
| C2 入厝 | `cold-c-housewarming` | 看過入厝相關頁 | `台南入厝外燴` | 入厝 landing（待確認）| `c2-housewarming` |
| C3 婚禮 ✅ 開 | `cold-c-wedding` | ThruPlay + 看過婚禮頁 | `台南戶外婚禮外燴`、`台南婚禮茶點` | `tainan-outdoor-wedding-catering`（2026-07-07 修正：原寫的 outdoor-wedding-catering-venue 為 404，非真實 slug） | `c3-wedding` |
| C1 性別派對 | ↪ 併入 `cold-c-birthday` | 同慶生線定向，不獨立 | — | 同慶生 landing | `c1-birthday` |
| 遊艇外燴 | ❌ 不做 | — | — | — | — |

### 橋接層：UTM + LINE 詢價

所有漏斗共用同一個成交點（LINE），UTM 是唯一追蹤工具：

```
廣告點擊（帶 utm_campaign / utm_content）
    → Landing（GA4 事件：page_view + scroll_depth）
    → LINE 加好友（LINE Tag 抓 UTM 來源）
    → 詢價單（備注 UTM campaign 讓 A0 知道哪條漏斗有效）
    → TimeTree 成交備注（Phase 4 戰情中心接入）
```

---

## 5. 執行優先序

**第一步（本週可動）：補溫層 retarget**
1. 用現有 ThruPlay 資料建 `warm-thruplay-50pct`、`warm-fb-page-engaged`、`warm-ig-engaged` 三個受眾包
2. 用現有圖（如 `maplab-corporate-forum-cathay-wealth-management-hero.webp`）製作一張溫層輪播素材
3. 廣告訊息：說場景不硬賣（「上次的論壇茶點，有幾個常見問題可以提前確認」）

**第二步（B3 HR/會議線完整漏斗）**
1. A4 處理富信飯店 + 工研院案例圖（HEIC→webp、去臉、alt 命名）
2. 用真實案例圖做溫層輪播素材
3. 建 `cold-b-meeting-corp` + `cold-b-meeting-edu` 冷層受眾包
4. Google Campaign5 加碼 B5 字詞（`大臺南會展中心外燴` 系列）

**第三步（C 端確認現跑成效 → 複製結構）**
- C1 週歲/家庭冷層 ThruPlay NT$0.12 效率佳 → 補溫層承接
- C2 入厝受眾包建立

---

## 6. 執行前置（標「待 Owner / 連接器」）

| # | 前置條件 | 狀態 | 說明 |
|---|---|---|---|
| (a) | **Meta Pixel 確認已裝於 maplabkitchen.com** | ✅ **已確認安裝（2026-07-05 Owner 清障）** | `warm-website-visitors` 和 `warm-landing-visitors` 均已解鎖，可直接建立 |
| (b) | **Meta Ads 連接器或 Owner 手動建受眾/廣告** | ⚠️ **待 Owner 決定** | 實際建受眾包、新增廣告活動需要 Meta Business Manager 操作權限。選項：(1) Owner 授權 Adspirer/Meta Ads MCP 連接器（目前顯示需授權）；(2) A2 給精確設定，Owner 自行在後台建立 |
| (c) | **ThruPlay retarget 現在就能建** | ✅ **無前置** | `warm-thruplay-50pct` 不需 Pixel，用 Meta 現有影片觀看紀錄建立，今天就能操作 |
| (d) | **A4 真實案例圖片處理（去臉 + webp）** | ⚠️ **待 A4** | 富信飯店 + 工研院案例圖需 A4 跑 HEIC→webp + needs_face_crop 處理，才能進廣告素材 |
| (e) | **Google Ads 競品防守廣告** | ⚠️ **待 Owner 核准文案** | 「玖二品生活外燴廚房」防守廣告文案草案需 Owner 審核後才能上線 |

---

## 變更紀錄

| 版本 | 日期 | 變更 | 來源 |
|---|---|---|---|
| v1.0-draft | 2026-07-05 | 初版：受眾/素材/佈局三層 buildout 草案 | Owner 定案方向，A2 填入 |
| v1.1 | 2026-07-05 | Pixel ✅ 已確認→解鎖網站 retarget；cluster 預設：婚禮線開、性別派對併慶生、遊艇不做 | Owner 清障 |
