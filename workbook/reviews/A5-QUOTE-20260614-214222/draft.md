> 金額校正：使用者預算解析為 NT$50,000（來源：預算50000；萬=10,000）。

Thinking...
Here's a thinking process to generate the response:

1.  **Understand the Persona and Goal:** I need to act as the "MAPLAB A5 Qu
Quotation and Proposal Engine." My primary goal is to take user requirement
requirements and output two things:
    *   A professional, structured Markdown quote draft.
    *   A JSON payload that precisely follows a defined format (`{"action":
(`{"action": "createQuote", ...}`).

2.  **Analyze the User Requirements:**
    *   **Service/Product:** Quotation for testing against competitor menus
menus (Tasting/Sampling).
    *   **Headcount:** 20 people.
    *   **Budget Constraint:** NT$50,000.
    *   **Requirement Details:** "Compare to competitor's menu," use MAPLAB
MAPLAB comparable items, pricing model is `Cost * 5`, target gross profit m
margin (GP) must be `>= 80%`.

3.  **Structure the Markdown Quotation Draft (The Proposal):** A profession
professional quote needs:
    *   A clear title/header.
    *   Understanding of the scope (Objective).
    *   Detailed itemization based on the requirements.
    *   Pricing breakdown (Cost, Markup, Unit Price, Total).
    *   Terms and Notes (Why MAPLAB is better).

    *Self-Correction during drafting:* Since the user only provided *criter
*criteria* ("like competitor menu," "cost * 5") but no actual competitor it
items or raw costs, I must structure the quote using placeholders and logic
logical assumptions to demonstrate capability.

4.  **Determine Variables for the JSON Payload:** The specified format is:
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

    *   `action`: `createQuote` (Required)
    *   `clientName`: Unknown/Not provided. Must use a placeholder or descr
descriptive text. (e.g., "競爭對手菜單比較活動")
    *   `eventType`: Menu Comparison / Sampling Test (餐點品項測試／競品分析
)
    *   `headcount`: 20 (From user input)
    *   `budget`: 50000 (From user input)
    *   `items`: Need to list general categories that fit the "test menu" r
requirement. Since I don't have specific items, I will use descriptive plac
placeholder groupings that represent a full meal/menu experience for 20 peo
people.

5.  **Final Review and Assembly:** Combine the formatted Markdown output wi
with the required JSON block, ensuring the JSON structure is perfect. (The 
instruction states the JSON must be appended at the very end.)

**(Self-Check against Constraints):**
*   MAPLAB A5 persona? Yes.
*   Markdown quote draft produced? Yes.
*   JSON payload included at the end? Yes.
*   Does the JSON match the required schema? Yes. (Action, clientName, even
eventType, headcount=20, budget=50000, items list).
...done thinking.

# MAPLAB A5 報價與提案引擎
## 🏆 競品菜單對標及味覺測試活動方案草稿

**致：[客戶名稱]**
**日期：** 2024年X月X日
**主旨：** 為達成「比照競爭對手菜單」的產品測試需求，提供具高毛利、高再現度
的MAPLAB品項組合方案。

---

### 🎯 一、 活動目標與提案說明

本次活動的核心目的是利用MAPLAB豐富且高品質的食材與餐點，模擬並超越指定競爭對
手的味覺體驗水平。我們將依據您的預算及人次限制，提供一份具備高度可變動性的測
試菜單。

**主要優勢：**
1. **精準對標性：** 不僅是簡單的食材替代，而是根據競品口感、風味結構進行逆向
工程模擬。
2. **高毛利確保（>80%）：** 依您提供的成本x5報價機制，保證每次提案都能達到極
高的毛利率，提升商業價值。
3. **彈性可控：** 菜單組件化設計，方便根據市場反饋調整測試焦點。

### ✨ 二、 預算與本次方案總覽

| 項目 | 說明 | 數值 / 數量 |
| :--- | :--- | :--- |
| **活動主題** | 競爭對手菜單味覺對標與改良提案 | N/A |
| **目標人次 (Headcount)** | 20 位參與測試人員 | 20 人 |
| **預算上限 (Budget Cap)** | NT$50,000 元 | 約 $48,000 - $50,000 |
| **報價結構** | 品項成本 $\times 5$ （確保毛利 $> 80\%$） | N/A |

### 🍽️ 三、 測試菜單建議與報價細目（草稿）

*由於您未提供具體的競爭對手菜單，以下以「三道式模擬菜單」為基礎進行預估品項
分組。實際報價需客戶提供參考競品照片或เมนู內容。*

| 區塊 | 品項名稱 (類別) | 功能目標 / 備註 | 單品數量/人次 | 模擬平均成本 (
(CP) | **單價提案** (CP $\times$ 5) | 總計估算費用 |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **前菜組** | MAPLAB主打涼拌/沙拉基底包 | 模擬開胃度和視覺衝擊力（低成本，
高感官） | 20份 | $C_1$ | $5 \times C_1$ | $\text{金額A}$ |
| **主菜組** | MAPLAB招牌精選餐點 A (如：海鮮烤盤) | 模擬主要蛋白質及口感核
心，決定整體評價。 | 20份 | $C_2$ | $5 \times C_2$ | $\text{金額B}$ |
| **配菜組** | MAPLAB熱食佐餐配件 B (如：氣炸主食/小點心) | 增加飽足感與可變
動性，擴大品項組合。 | 20份 | $C_3$ | $5 \times C_3$ | $\text{金額C}$ |
| **飲品組** | MAPLAB限定測試飲料包 | 提升整體儀式感和體驗完整度。 | 20套 |
| $C_{L}$ | $5 \times C_{L}$ | $\text{金額D}$ |
| **總計預估費用** | - | - | - | - | - | $\text{A} + \text{B} + \text{C} + 
\text{D}$ ($\approx$ 預算範圍) |

***備註：本報價為草稿，實際價格將根據您提供的競品菜單細節與原材料批發成本確
定。***

### ✅ 四、 下一步行動建議

1. **提供參考菜單：** 請提供具體的競爭對手菜單圖片或文字描述。
2. **確認測試層級：** 確認本次活動是要進行「成本對標」還是「風味超越」，以便
我們優化品項推薦比例。
3. **議定最終組合：** 確定最終的餐點組合，啟動精確成本計算與正式報價流程。

---

```json
{
  "action": "createQuote",
  "clientName": "競品菜單對標客戶 (待確認)",
  "eventType": "味覺測試/產品線模擬活動",
  "headcount": 20,
  "budget": 50000,
  "items": [
    {"name": "涼拌開胃前菜包 (基底組)", "quantity": 1},
    {"name": "核心主餐點模擬組合 A", "quantity": 1},
    {"name": "佐餐熱食配件與補充品 B", "quantity": 1},
    {"name": "限定活動飲品測試包", "quantity": 1}
  ]
}
```
