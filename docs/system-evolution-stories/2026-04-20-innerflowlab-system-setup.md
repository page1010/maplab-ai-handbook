# 2026-04-20 — InnerFlowLab 個人品牌站系統建置

> 記錄者：A1 系統總管
> 日期：2026-04-20
> 背景：Owner 決定啟用 innerflowlab.com 作為個人品牌站，需要完整 API 接口讓 AI Agent 接手社群發文

---

## Owner 原始構想

> 掛在 innerflow 那邊的子域名好了，那邊沒什麼好失去，賭一個爆擊，沒有就算了。伺服器最多支援兩個站，暫時不打算升級。

### 一開始的方向：旅遊子域名
- 最初想法：`travel.innerflowlab.com` 做旅遊 blog
- 用途：旅遊業配文、SEO 流量

### Owner 調整：改為個人日誌
> 不用 travel，把他當我個人日誌之類的可以嗎？

調整後方向：
- **不用子域名** → 直接用 innerflowlab.com 主站
- **不限主題** → 旅遊、生活反思、AI 實戰心得，什麼都能寫
- **不佔伺服器額度** → 原本就有的站，不需要新增

### 為什麼這樣更好
1. 主題彈性大 — 個人日誌不限主題，不會被「travel」框死
2. 內容越雜反而越像真人部落客 — 業配廠商喜歡有生活感的帳號
3. SEO 集中在一個域名 — 所有流量灌同一站，權重累積更快
4. 不佔伺服器額度 — 伺服器最多 2 站（maplabkitchen + innerflowlab）

---

## 系統建置 — 兩站完整接口

### 目標
讓 A1（Claude Code）能用 API 接手兩站的內容管理 + 社群發文：
- **maplabkitchen.com** → A2/A3 用（MAPLAB 商業 SEO + 社群）
- **innerflowlab.com** → B1 用（個人品牌 + Threads 引流）

### Step 1: WP Application Password（API 接口）

**為什麼需要**：WP REST API 需要認證才能建立/編輯頁面和文章。Application Password 是最安全的方式（不用給管理員密碼）。

**操作步驟**：
1. WP 後台 → 使用者 → 點管理員帳號
2. 滑到底部「應用程式密碼」區塊
3. 名稱填 `claude-code` → 新增
4. 複製密碼（只顯示一次）

**結果**：

| 站 | 帳號 | App Password | 狀態 |
|---|---|---|---|
| maplabkitchen.com | pagewu1010@gmail.com | `tWqC bFv5...` | 之前已建（名稱 maplab-detasys） |
| innerflowlab.com | pagewu1010@gmail.com | `8ra1 vHYG...` | 2026-04-20 建立 |

**踩坑**：maplabkitchen.com 的 Cloudways 環境 Basic Auth 失效，要改用 X-WP-Nonce 方式認證。

### Step 2: 隱私政策頁（Meta App 必要條件）

**為什麼需要**：Meta Developer Portal 建 App 時必須填隱私政策 URL，沒有就無法通過審核。

**操作**：A1 用 WP REST API 自動建立兩站的隱私政策頁。

| 站 | URL |
|---|---|
| maplabkitchen.com | `https://www.maplabkitchen.com/privacy-policy/` |
| innerflowlab.com | `https://innerflowlab.com/privacy-policy/` |

### Step 3: Meta Developer Portal — App 設定（進行中）

**架構**：

| Meta App | 對應站 | 用途 | IG 帳號 |
|-----|--------|------|---------|
| B1 文章引流（App ID: 134019781154959） | innerflowlab.com | 個人 Threads 自動發文 | Owner 個人 IG |
| MAPLAB Social（待建） | maplabkitchen.com | MAPLAB 社群/SEO | MAPLAB Kitchen IG |

每個 App 需要：
1. 應用程式圖示（1024x1024）
2. 隱私政策網址（Step 2 的 URL）
3. 用戶資料刪除指示網址
4. 類別：商業

### Step 4: Meta App 完成設定

**已完成**（2026-04-20）：

| Meta App | App ID | Threads App ID | App Secret | 對應站 |
|---------|--------|---------------|------------|--------|
| MAPLAB-AI | `2394935917598400` | `1875971873108650` | `dda4c9...` | maplabkitchen.com |
| B1 文章引流 | `1340197811549591` | `1675941176953389` | `027d0c...` | innerflowlab.com |
| 第三個 App | — | — | — | 不理它 |

**踩坑**：
- 「用戶資料刪除」欄位要填完整 `https://` 開頭的 URL，不然報錯 `name_placeholder should represent a valid URL`
- 其實填隱私政策頁 URL 就好

### Step 5: Threads API Token（進行中）

流程：
1. App 內加 Threads 測試用戶（個人 IG 帳號）
2. IG App 接受測試邀請
3. 用授權 URL 取得 authorization code
4. A1 拿 code 換 long-lived token（60 天有效）
5. A1 設定 MCP 環境變數 + 50 天自動刷新排程

### Step 6: 跨平台擴展（2026-04-20 新增）

Owner 決定一次做完所有平台的 API 設定：

| 平台 | 需要什麼 | 用途 |
|------|---------|------|
| Threads | Access Token（授權 URL → code → long-lived token） | 自動發文引流 |
| X (Twitter) | Developer Account → API Key + Secret + Access Token + Secret | 短文引流（280字） |
| Reddit | script app → client_id + client_secret + 帳密 | 深度文投到目標 subreddit |
| Substack | 帳號 + Stripe Connect | 長文主站 + 付費訂閱 |

### 收費模型決策

> Owner: 那個賺錢的文章需要開什麼 api token 申請什麼你一次列出來，我今天有空一次做

- **Substack 付費**: 月費 $5 / 年費 $50，透過 Stripe Connect
- **內容比例**: 80% 免費（引流）+ 20% 付費深度文
- **雙線內容**: Building（技術實戰，週更）+ Reflecting（思考，雙週更）

---

## 決策紀錄

| 決策 | 選擇 | 理由 |
|------|------|------|
| 子域名 vs 主站 | 主站 innerflowlab.com | 不佔伺服器額度、SEO 集中、主題彈性大 |
| 旅遊 blog vs 個人日誌 | 個人日誌 | 不被主題框死，業配接受度更高 |
| 新建 WP 帳號 vs 用管理員 | 用管理員 + Application Password | 簡單、Owner 只有一人，不需要權限分離 |
| 認證憑證存放 | Notion API Keys 保管室 | 集中管理、Owner 可隨時查看 |
| 跨平台一次設定 vs 分批 | 一次做完 | Owner 有空檔，Max 快到期，趁有時間全部弄好 |
| Substack 收費模式 | 80/20 免費/付費 | 免費文引流、付費文養深度讀者 |
| 帳號名稱統一 | `innerflowlab` 全平台 | 品牌一致性，好記好搜 |

---

## 學到的事

1. **伺服器限制要先問** — 「最多 2 站」這個限制差點讓我們走錯方向（建子域名 = 佔額度）
2. **Owner 的直覺通常更好** — 「不用 travel，當個人日誌」比我們分析出來的方案更好
3. **系統建置初期需要 Notion 溝通** — GitHub 是半自動接手後的事，建置期有太多需要 Owner 手動操作的步驟，用 Notion checklist 更直覺
4. **WP Application Password 是最快的 API 接口** — 不用改伺服器設定、不用裝外掛，內建功能就夠用
5. **隱私政策頁是 Meta App 的前置條件** — 很多人卡在這一步，其實用 WP 內建範本 5 分鐘就搞定
6. **Meta App 用戶資料刪除欄位** — 就填隱私政策 URL，記得完整 `https://` 開頭
7. **一次做完比分批好** — Owner 的時間窗口有限（Max 到期），所有平台 API 一次列清單、一次做完效率最高

---

## 相關文件
- B1 技能書：`skills/b1-innerflowlab-skills.md`
- Notion Threads SOP：https://www.notion.so/347ab0806d5c8165a484cf8d7aba769f
- Notion 完整設定清單：https://www.notion.so/348ab0806d5c81fd832bed51a7c07fb5
- 任務卡：`handoff/tasks/T-B1-001.md`
- 憑證保管：Notion API Keys 保管室
