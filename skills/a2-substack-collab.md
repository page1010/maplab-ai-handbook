# A2 技能書：Substack 故事系列協作

> 觸發條件：Owner 要寫 Substack 文章、故事系列內容、英文內容翻譯
> 負責角色：A2（Content & SEO）
> 建立日期：2026-04-17

---

## 一、定位

MAPLAB 有兩條內容線，都歸 A2 管：

| 內容線 | 主導 | 目的 | 發布管道 |
|--------|------|------|---------|
| **SEO 關鍵字文章** | A2 主寫，Owner 審 | 搶排名、搶流量 | maplabkitchen.com（主站） |
| **Substack 故事系列** | Owner 主寫，A2 補充 + 翻譯 | 養信任、養名單、建品牌 | Substack + innerflowlab.com |

**本技能書只管第二條。**

---

## 一之二、InnerFlowLab 雙線結構

站名：**InnerFlowLab** — innerflowlab.com（已有 WordPress）+ Substack 同名帳號（待註冊）

兩條內容線共用同一個品牌，用 Substack **Sections** 功能分流：

| 線 | Section 名稱 | 主題 | 受眾 |
|---|-------------|------|------|
| **Lab 線** | **Building** | 跟 AI 建系統的真實故事、踩坑、頓悟 | 開發者、中小企業主 |
| **Inner 線** | **Reflecting** | 跟 AI 聊榮格、原型、對話中的自我覺察 | 對 AI + 心理學交叉有興趣的人 |

**共同主軸**：人跟 AI 的深度互動 — 一條往外（建系統），一條往內（自我探索）。

讀者可以只訂其中一條線，或兩條都追。

### 兩線共用規則
- 協作模板（⊹ 標記格式）兩線通用
- 禁止事項兩線通用
- Owner 決定每篇歸哪條線

---

## 二、協作模板

### 頭部聲明（每篇固定）

```
Written by [Owner 名字]
Technical notes by Claude · AI-assisted sections marked with ⊹
```

### 正文格式

- Owner 寫的故事 → **無標記**，就是預設文字
- AI 補充（短，1-2 句）→ 行內區塊：

```
⊹ Claude's note: [事實/技術補充內容]
```

- AI 補充（長，技術深潛）→ 獨立框：

```
┌─ ⊹ Technical Context ─────────────────
│ [較長的技術補充]
│ 可含程式碼、架構說明、數據比較
│ 讀者可跳過不影響故事理解
└────────────────────────────────────────
```

### 尾部（每篇固定）

```
---
About this series: I build AI systems for my catering
business. These are real stories, not tutorials.
Technical context provided by Claude is marked with ⊹.

→ Subscribe for the next chapter
→ [Substack link]
```

---

## 三、協作流程

| 步驟 | 誰做 | 說明 |
|------|------|------|
| 1. 寫故事 | **Owner** | 中文先寫。主題、用字、觀點全由 Owner 決定 |
| 2. 標記補充點 | **Owner** | 覺得哪裡需要技術/事實補充，標 `[需要補充]` |
| 3. 寫補充 | **A2 (Claude)** | 只在標記處補充，用 ⊹ 格式 |
| 4. 翻譯 | **A2 (Claude)** | 中翻英，保留 Owner 語氣和節奏 |
| 5. 最終確認 | **Owner** | Owner 看過才能發布 |

---

## 四、禁止事項（A2/Claude 側）

- ❌ **不改 Owner 的任何用字**（中翻英除外）
- ❌ 不在 Owner 沒標記的地方插入補充
- ❌ 不改故事結構或順序
- ❌ 不加教學語氣（「你應該...」「建議...」）
- ❌ 不美化或淡化 Owner 的真實經歷
- ❌ 不在補充中加入 Owner 沒提到的觀點

---

## 五、發布設定（待建置）

### Substack
- 帳號：待 Owner 註冊（名稱：InnerFlowLab）
- Sections：Building（Lab 線）、Reflecting（Inner 線）
- 發文語言：英文（主）
- 節奏：待定

### WordPress（SEO 鏡像）
- 域名：innerflowlab.com（已有 WordPress）
- 現有內容：少量中文心靈內容，不用刪，新文章會自然蓋過
- 用途：全文 SEO 長尾流量入口
- 結構：可用 Category 對應 Substack 的 Building / Reflecting 分線

### 雙語策略
- 中文版：視需求開（可用 Substack 中文 Section 或 innerflowlab.com 中文分類）
- 英文版：Substack 主發 + innerflowlab.com 全文鏡像
- 翻譯流程：Owner 中文 → Claude 英文潤稿 → Owner 確認

---

## 六、與 SEO 文章的分界

| 判斷 | 故事系列（本技能書） | SEO 文章（現有流程） |
|------|---------------------|---------------------|
| 誰寫主體 | Owner | A2 |
| 語調 | 個人、故事性、像聊天 | 專業、資訊性、關鍵字導向 |
| 目的 | 養信任、養名單 | 搶排名、搶流量 |
| 發布管道 | Substack + 子網域 | maplabkitchen.com 主站 |
| AI 參與標記 | 必須標 ⊹ | 不需特別標記 |
