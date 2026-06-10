Thinking...
Here's a thinking process to generate the response:

1.  **Analyze the Request & Role:**
    *   **Role:** MAPLAB A5 Quoting and Proposal Engine.
    *   **Output Goal:** Generate a draft quote/proposal in Markdown format
format.
    *   **Critical Constraint (Mandatory):** The *absolute last part* must 
be a JSON block following the specific structure provided.

2.  **Analyze User Input (The Need):**
    *   Client Name: Gina浥慧
    *   Event Type: 企業開幕 (Corporate Grand Opening)
    *   Headcount (People): 30-40人
    *   Budget: 12,000 (Assumed NTD or local currency based on context/exam
context/example structure)
    *   Date/Time: 11/9, 早上十點到下午五點
    *   Location: 安平區慶平路440號 室內一樓
    *   Menu Focus: 茶點為主 (Tea snacks/light refreshments focus).

3.  **Determine Required Data for JSON Structure:**
    *   `action`: "createQuote"
    *   `clientName`: Gina浥慧
    *   `eventType`: 企業開幕
    *   `headcount`: Needs a single number. Since the user provided 30-40, 
I'll use the upper bound or an average that fits standard quoting practices
practices (I will choose 40, as it's safer for budgeting). *Self-correction
*Self-correction: The JSON structure asks for `headcount`: 人數數字.*
    *   `budget`: 12000
    *   `items`: I need to estimate plausible items and quantities based on
on a corporate opening/tea snack focus.

4.  **Drafting the Markdown Quote (Structure & Content):**
    *   *Tone:* Professional, formal, service-oriented.
    *   *Sections:* Title, Client Details, Event Summary, Menu/Items, Estim
Estimated Cost Breakdown.
    *   *Pricing Strategy (Estimation based on Budget):* A budget of 12,000
12,000 for 30-40 people suggests a per-person cost of approximately $300 - 
$400 (~$30 - $40 if we assume NTD/local currency is used flexibly).
    *   *Items Selection:* Drinks (coffee/tea), light snacks (pastries, min
mini desserts).

5.  **Populating the JSON Data (The Technical Output):**
    *   `clientName`: "Gina浥慧"
    *   `eventType`: "企業開幕"
    *   `headcount`: 40 (Using the max estimate)
    *   `budget`: 12000
    *   `items`: I need specific items.
        *   Item 1: 茶點套餐/點心組 (Tea Snack Set/Dessert Mix) - Quantity:
Quantity: 40 people servings.
        *   Item 2: 飲品供應 (Beverage Supply, e.g., Coffee/Tea station) - 
Quantity: 1 set (or sufficient for 40). *I will use a single unit count for
for simplicity in the JSON.*

6.  **Final Review and Formatting:**
    *   Ensure the Markdown draft is complete and professional.
    *   Ensure the final output segment is *only* the JSON block, as requir
required by the prompt structure (and remember to add internal explanatory 
text before it).

**(Self-Check Complete: The response meets all role requirements and format
formatting constraints.)**
...done thinking.

# 🍽️ MAPLAB A5 報價單草稿：企業開幕茶點套餐

***

### I. 基本資訊概覽

*   **客戶名稱：** Gina浥慧
*   **活動類型：** 企業開幕慶典 (Corporate Grand Opening)
*   **日期/時間：** 11月9日（週五）/ 上午十點至下午五點
*   **地點：** 安平區慶平路440號 室內一樓
*   **預計人數：** 30 - 40 位 (以 40 人計算)
*   **服務主題：** 茶點輕食套餐，維持優雅且不具飽足感的氣氛。

### II. 活動建議方案：「都會時光茶歇」

基於「茶點為主」的需求以及企業開幕的節慶氣氛，本案設計了兼顧視覺美觀、口味和
便利性的茶歇餐點組合。此方案適合用於聯誼會或舉行典禮後的閒聊時間。

**✅ 涵蓋範圍：**
*   輕食精選搭配 (Pastries & Desserts)
*   飲品自助供應 (Coffee/Tea Bar Setup)
*   擺設佈置與服務人力安排 (包含基礎餐台陳設)

### III. 品項報價細節（預估）

| 編號 | 品項名稱 | 內容描述 | 建議數量 | 單價 (NTD) | 備註 |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | **精選茶點套餐 A** | 精緻小食組合，包含法式甜點三組、可頌類糕點二
組。色彩豐富，適合拍照留念。 | 40 人份 | $X,XXX | 高階質感為主，保鮮期限考慮
進去安排。 |
| **2** | **專業茶飲自助區** | 提供咖啡機/紅茶供應，包含三種口味現磨咖啡豆與
綜合茶包。 | 1 組 | $Y,YYY | 服務至下午五點，確保持續新鮮。 |
| **3** | **餐檯布置及服務費** | 活動場地佈置、備品（盤叉餐巾）、以及專人協
助上菜/清理。 | 1 個 | $Z,ZZZ | 人力費用依實際需求與時間長度調整。 |

**💰 預計總經費控制：** 約新台幣 NT$ 12,000 - NT$ 15,000 (包含所有稅金、服務
費與最低餐點標準)
*(註：此報價為草稿建議，最終價格需確認具體品牌和品項後確定。)*

### IV. 預計流程規劃（供參考）

*   **10:00 - 10:30：** 客人抵達，暖場與接待 (茶點輕食供應)。
*   **10:30 - 12:30：** 開幕典禮及重要發表環節。
*   **12:30 - 14:00：** 午餐/休息時間（可調整為較完整的餐點，或延長茶歇）。

*   **14:00 - 16:30：** 交流聯誼時間 (持續提供茶飲與精緻茶點補給)。

***

```json
{
  "action": "createQuote",
  "clientName": "Gina浥慧",
  "eventType": "企業開幕",
  "headcount": 40,
  "budget": 12000,
  "items": [
    {"name": "精選茶點套餐A (小食組合)", "quantity": 40},
    {"name": "專業茶飲自助區", "quantity": 1}
  ]
}
```
