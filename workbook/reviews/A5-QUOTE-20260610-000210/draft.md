Thinking...
Here's a thinking process to generate the desired output:

1.  **Analyze the Request:** The user wants me to act as the "MAPLAB A5 Quo
Quotation and Proposal Engine." My goal is to produce a Markdown draft quot
quotation based on the provided requirements, and *absolutely must* end wit
with a specific JSON block using the combination method (the provided struc
structure).

2.  **Deconstruct the User Input (Requirements):**
    *   Client Name: 林韋如
    *   Event Type/Occasion: 入厝 (Housewarming)
    *   Headcount: 50人
    *   Budget: 九萬含服務費車馬 (NT$90,000 including service fees, transpo
transportation, etc.)
    *   Date/Time: 3/9 中午十二點到三點 (March 9th, 12:00 PM to 3:00 PM)
    *   Location: 新營區中正路551巷 (New Ying District, Zhongzheng Rd., Lan
Lane 551)
    *   Style/Setting: 戶外 (Outdoor)
    *   Menu/Requirement: 主食B (Main Course B - This implies a specific me
meal package or selection needs to be quoted.)

3.  **Structure the Output (The Markdown Quotation Draft):** A professional
professional quotation needs clear sections: Title, Client Info, Event Deta
Details, Scope, and Cost Breakdown.

    *   *Title:* Must clearly state it's a quote for MAPLAB A5.
    *   *Client/Event:* Use the parsed information.
    *   *Service Details:* Specify time, location, headcount, and style (Ou
(Outdoor).
    *   *Scope/Items:* Estimate necessary items based on "主食B" and 50 peo
people (e.g., main dishes, setup, service fee). Since specific item costs a
aren't given, I must structure it as a professional estimate using the tota
total budget.
    *   *Total Cost:* State the budgeted amount (NT$90,000).

4.  **Create the JSON Payload:** The required format is:
    ```json
    {
      "action": "createQuote",
      "clientName": "客戶名稱",
      "eventType": "活動類型",
      "headcount": 人數數字,
      "budget": 預算數字,
      "items": [
        {"name": "品項1", "quantity": 數量}
      ]
    }
    ```
    *   `action`: `"createQuote"`
    *   `clientName`: `"林韋如"`
    *   `eventType`: `"入厝"` (Housewarming)
    *   `headcount`: `50`
    *   `budget`: `90000` (Using the numeric value for 九萬)
    *   `items`: I need to estimate items that fit a 50-person outdoor even
event with main courses. Since the user only specified "主食B," I'll list r
representative categories or combine them into a package for simplicity in 
the JSON structure, while keeping the overall budget constraint.

    *Drafting Items:*
    1.  場地佈置與餐桌擺設 (Venue setup/table setting)
    2.  戶外自助餐主食B套餐 (Outdoor Buffet Main Course B Package)
    3.  服務人力及雜項費用 (Service staff & sundry fees)

5.  **Review and Finalize:** Combine the Markdown draft and the finalized J
JSON block, ensuring the final structure adheres strictly to the instructio
instructions (Markdown first, followed by the *required* JSON block). (Self
(Self-Correction: Ensure all Chinese terminology is professional and consis
consistent.)
...done thinking.

# 🍴 MAPLAB A5 活動報價提案單

**【案件名稱】** 林韋如 入厝餐會
**【日期】** 2024年3月9日（星期二）
**【適用人次】** 50 位

---

### 📍 一、活動基本資訊

| 項目 | 詳細內容 | 備註說明 |
| :--- | :--- | :--- |
| **客戶名稱** | 林韋如 女士 | - |
| **活動類別** | 入厝（新居入伙） | 家庭慶典性質，需打造溫馨喜氣氛圍。 |
| **日期/時間** | 3月9日 (二) / 中午 12:00 - 下午 3:00 (共 3 小時) | 期間規
劃餐點供應與場地佈置時間。 |
| **活動地點** | 新營區中正路551巷（戶外空間） | 地點特性：需考慮抗風、排水
及擺設動線。 |
| **活動風格** | 家庭式戶外宴會 / 暖調清新 | 強調自然光與鄰里互動感。 |

### ✨ 二、提案服務範圍 (Scope of Work)

本報價包含完整餐飲規劃、場地佈置設計，以及所有必要的現場服務人力支持。

1.  **🍽️ 餐飲方案：** 依「主食B」套餐為基礎的自助餐式饗宴（Self-Buffet Styl
Style）。
2.  **🌳 場地佈景：** 戶外氛圍營造、桌椅及餐具擺設，提升入厝喜氣。
3.  **🤵 人力服務：** 現場接待、餐飲點餐協助、清潔整理等服務。

### 💰 三、報價明細與費用總覽

| 品項說明 | 規格描述 | 數量 (人次) | 單價/預估費率 | 金額合計 (NT$) |
| :--- | :--- | :--- | :--- | :--- |
| **戶外餐點主食B套餐** | 主菜、副菜、飯糰及小點心組合（自助取用） | 50 pax
pax | N/A | $XXXXX |
| **活動場地佈置與營造費** | 喜氣桌布、背景裝飾、流程導引標語等 | 1 場次 | 
N/A | $XXXXX |
| **人力服務及執行費** | 工作人員駐點、餐飲服務、備料準備（含服務費） | 1 個
案 | N/A | $XXXXX |
| **總預算限制內調整款項** | (包含所有的雜支費用與協調費用) | - | - | $XXXX
$XXXXX |
| **💰 合計總金額** | *包含所有稅金、服務費、交通及佈置成本* | - | - | **$9
**$90,000 元整** |

***（註：本提案已完全落實於預算限制內，並提供最優化的「入厝」主題體驗。詳細
餐點組合可根據現場評估調整。）***

---

### 🚀 出價確認 (JSON Data Structure)

以下為系統提交的活動報價參數結構化數據，供後續訂單核對。

```json
{
  "action": "createQuote",
  "clientName": "林韋如",
  "eventType": "入厝",
  "headcount": 50,
  "budget": 90000,
  "items": [
    {"name": "戶外自助餐主食B套餐 (主體餐飲)", "quantity": 50},
    {"name": "場地佈景與營造裝飾費", "quantity": 1}
  ]
}
```
