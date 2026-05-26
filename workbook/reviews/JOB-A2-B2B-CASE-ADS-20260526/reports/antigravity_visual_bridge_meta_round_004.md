# Antigravity Visual Bridge Meta Report — Round 004

## 1. Visual Bridge Protocol

- **How A2 should continue giving UI state:** A2 must use Computer Use to take targeted, cropped screenshots specifically of the Owner's active MAPLAB Chrome window (`adsmanager.facebook.com`), excluding any other agent or private chat windows. A2 must extract the visible data into a structured Markdown report.
- **What screenshot/text facts are sufficient:** Cropped screenshots of the exact UI layer (e.g., the Ad Sets table or the detailed targeting dropdown) accompanied by a text transcript of the visible fields (names, toggles, delivery statuses, specific targeting tags).
- **What cannot be inferred without a new packet:** As Antigravity, I cannot see beyond the current campaign-level view. I cannot infer Ad Set settings (Detailed Targeting, Advantage+, Custom Audiences), Ad-level destination URLs, or Pixel event statuses until A2 provides a new visual bridge packet for those specific layers.

## 2. Verified Current Meta Campaign Facts

Based on `meta_ads_owner_chrome_visual_bridge_round_004.md` and the cropped screenshot:
- **Account Context:** Ad account `318634712 (318634712)`, Business/global scope `215690449213844`.
- **Date Range:** `過去 30 天：2026年4月26日 – 2026年5月25日`.
- **Campaign Rows:** 13 visible rows.
- **Active vs Closed State:**
  - **Active (進行中):** 3 campaigns (`2026 品牌知名度廣告 A組 周歲與廣泛...複本`, `2026 策略一｜頂層品牌認知...複本`, `2026 B組"互動"行銷活動-cta`).
  - **Closed (已關閉):** 10 campaigns.

## 3. B2B Usefulness Ranking

- **Likely Useful Campaigns (B2B Seeds):**
  - `開發潛在客戶2026` (Lead gen surface)
  - `Instagram 貼文：#外燴紀錄 | 中華賓士-愛心慈善捐贈活動｜ESG｜...` (Strong B2B/ESG proof)
  - `新的開發潛在顧客行銷活動` (Generic lead gen)
- **Likely To C / Noise Campaigns:**
  - All campaigns targeting "周歲", "家庭冷受眾", "高收入媽媽族群".
  - `Instagram post: #派對實拍場景 | Wedding Party...`
  - `Instagram 貼文：#外燴紀錄 今年夏天...邦尼托嬰...`
  - `竹南加盟廣告A`
- **Unknown Campaigns Needing Ad Set Inspection:**
  - `2026 B組"互動"行銷活動-cta` (Active; need to see if it targets B2B or B2C)
  - `新的品牌認知行銷活動` (Generic; need to see audiences)

## 4. Next Read-Only UI Instructions for A2

- **Exact Layer to Open Next:** The `廣告組合` (Ad Sets) layer or the Edit pane for the selected candidate campaigns.
- **Priority Campaign Order:**
  1. `開發潛在客戶2026`
  2. `Instagram 貼文：#外燴紀錄 | 中華賓士-愛心慈善捐贈活動｜ESG｜在...`
  3. `新的開發潛在顧客行銷活動`
- **Columns/Fields to Capture:**
  - `詳細的目標設定` (Detailed Targeting) - specifically look for B2B tags like 創業, 公關, 室內設計, 企業管理.
  - `優勢+ 廣告受眾` (Advantage+ Audience) suggestions.
  - Custom Audiences / Pixel connection status.
- **Forbidden Actions:** Do not click `檢查並發佈 (4)`, `捨棄草稿`, save, publish, duplicate, edit settings, accept policy dialogs, or change toggles.

## 5. Updated A3 Meta Instruction

- **Proposal-Only Interest Clusters:** The audience hypotheses for `Real Estate VIP`, `Brand PR ESG Event`, and `Opening Tea Party` remain in a proposal-only state.
- **Candidate Surfaces:** Focus on using the 3 priority campaigns identified above as the base for building or analyzing B2B audiences, rather than the active To C campaigns.
- **Remaining `Needs UI Check` Facts:** We still cannot verify if the desired B2B interest tags (e.g., 房地產, 創業, 公關, 美術館) are actually selectable in this account. Pixel and Custom Audience status also remain unverified.

## 6. Updated Dashboard / Loop Status

- **What Can Now Move Forward:**
  - A2 has a clear, safe visual bridge protocol to inspect the Meta Ad Sets layer without triggering API blocks.
  - The WordPress update plan (drafting case copies into existing posts) and Google Ads restructuring plan (grouping keywords by exact intent) are ready for Owner review and approval.
- **What Remains Blocked by Missing UI Data:**
  - Meta detailed targeting validation.
  - Final URL destination checks at the Meta Ad level.
  - Pixel and Custom Audience retargeting availability.
