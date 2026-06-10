> 金額校正：使用者預算解析為 NT$60,000（來源：預算6萬；萬=10,000）。

Thinking...
Here's a thinking process to construct the response:

1.  **Analyze the Request:**
    *   **Role:** MAPLAB A5 Quote & Proposal Engine.
    *   **Goal:** Generate a Markdown draft quotation/proposal based on use
user input.
    *   **Crucial Constraint (Mandatory):** The *absolute last part* must b
be a JSON object representing the combination of all extracted data, format
formatted within a ```json block.

2.  **Analyze User Input:**
    *   Client Name: 王小明
    *   Event Type: 婚禮 (Wedding)
    *   Headcount: 80人 (80 people)
    *   Budget: 6萬 (60,000 units/currency implied, usually TWD or similar 
in this context).

3.  **Determine the Output Structure (Markdown Draft):**
    *   The draft needs a professional, quote-like structure.
    *   It must incorporate all user data points logically.
    *   I need to create plausible dummy line items since the user didn't s
specify product details, but only general parameters (Headcount/Event). I w
will use common wedding event planning services.

4.  **Drafting Content (Internal Simulation):**
    *   *Header:* Use MAPLAB A5 branding.
    *   *Client Info:* 王小明.
    *   *Event Info:* 婚禮, 80人.
    *   *Items:* Must be relevant to a wedding and fit the budget constrain
constraints (or at least suggest items that can fit).
        *   Venue/Decor: Main expense.
        *   Photography/Video: Essential for weddings.
        *   Catering/Dessert: Necessary for 80 people.

5.  **Constructing the Final JSON:**
    *   `action`: "createQuote" (as instructed).
    *   `clientName`: "王小明".
    *   `eventType`: "婚禮".
    *   `headcount`: 80.
    *   `budget`: 60000 (Converting "6萬").
    *   `items`: List of items/quantities used in the markdown draft.

6.  **Review and Final Output Generation:** (Assemble the Markdown first, e
ensuring professionalism, then appending the mandatory JSON block.) (Self-C
(Self-Correction: Ensure the tone is helpful and professional.)
...done thinking.

# 🌟 MAPLAB A5 活動報價提案系統 V2.1 🌟
## 「王小明」婚禮活動專案初步提案

**提案日期：** 2024年[當前月份]
**客戶名稱：** 王小明
**活動類型：** 婚禮（Wedding Reception）
**預計出席人數 (Headcount)：** 80 人位
**預算參考範圍 (Budget)：** NT$60,000

---

### ✨ 活動概覽與核心建議

恭喜王先生/女士的婚事！基於您的「婚禮」需求及 80 位賓客的規模，我們為您設計
了基礎且兼具質感的高級迎賓方案。本次提案重點著重在營造浪漫氛圍、優質餐飲體驗
，並符合預算範圍，提供一個高品質的活動規劃藍圖。

### 📋 建議採購品項明細 (Proposal Items)

| 品項編號 | 品項名稱 | 詳細說明 | 單位 | 數量 | 單價估計 |
| :---: | :--- | :--- | :---: | :---: | :---: |
| P01 | **典雅餐飲方案** | 80人份輕宴/茶歇搭配甜點，包含基礎餐具與擺設。 | 
人位 | 80 | (待定) |
| P02 | **場地佈置主軸設計** | 主舞台背景、迎賓區花艺拱門、氣球裝置（依現場
空間調整）。 | 套式 | 1 | (待定) |
| P03 | **新人攝影紀錄服務** | 新郎新娘專業婚禮拍照包（建議半日或全日拍攝）
。 | 次數 | 1 | (待定) |
| P04 | **基礎環節活動控場支援** | 活動流程指導、音響設備及基本佈景周邊設備
。 | 套式 | 1 | (待定) |

### 💰 初步預估成本分攤（依據 $60,000 預算為導向調整）

*   **餐飲與服務：** 約佔總預算的 35%
*   **佈景設計與裝飾：** 約佔總預算的 40%
*   **設備及內容物料 (攝影/控場)：** 約佔總預算的 25%

> **💡 風險提示：** 此報價單為初步草稿，實際費用將會根據您最終選擇的場地類型
（飯店、宴會館或戶外）、餐飲級別以及細節裝飾工藝而有顯著變動。建議進一步諮詢
我們的活動規劃師進行客製化估價。

---
**[下一步行動]：** 請您提供希望活動舉辦的大致日期與偏好風格（例如：歐式古典
、日式簡約或熱帶浪漫），我們將能更快為您制定精準的報價單！

***

```json
{
  "action": "createQuote",
  "clientName": "王小明",
  "eventType": "婚禮",
  "headcount": 80,
  "budget": 60000,
  "items": [
    {"name": "典雅餐飲方案 (基礎)", "quantity": 80},
    {"name": "場地佈置主軸設計", "quantity": 1},
    {"name": "新人攝影紀錄服務", "quantity": 1},
    {"name": "活動控場及設備支援", "quantity": 1}
  ]
}
```
