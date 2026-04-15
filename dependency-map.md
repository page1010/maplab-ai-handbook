# dependency-map.md — 連動地圖

> **用途**：Agent 改任何東西前，查這張表確認「改 X 會影響 Y」。
> 更新方式：新增連動關係時追加。定期由 A1 巡查驗證。

最後更新：2026-04-15

---

## 關鍵連動叢集

### 1. Items 表 = 核心樞紐（改動最危險）

```
A5（擁有者）→ Items 表 → A6（讀品名/成本做報價）
                        → QUOTE_DRAFT 公式（VLOOKUP Items!C:E）
                        → Slide 生成（讀 K 欄 image_url）
                        → A7（讀定價規則回答客戶）
A4 → Items.K 欄（供圖 image_url）
```

⚠️ **改 Items 欄位結構（增刪欄、改欄位順序）= 整條報價管線斷裂**

| 你改了什麼 | 會壞什麼 |
|-----------|---------|
| Items 欄位順序 | A6 createQuote formData、QUOTE_DRAFT VLOOKUP、Slide 品項對照 |
| Items 品名編碼（APP/DST/MAIN/BEV） | A6 品項比對、A7 品名查詢 |
| Items.E（default_cost） | 所有 QUOTE_DRAFT 的毛利率公式 |
| Items.K（image_url） | Slide 自動插圖 |

### 2. GAS 雙專案（推錯就全毀）

```
報價系統 GAS（scriptId: 1JIiPW_OUwNzB...）
  ├─ createQuote / fromMaster
  ├─ generateProposalV2（Slide）
  └─ ApiEndpoint.gs（A6 bot HTTP 呼叫入口）

LINE 對話 GAS（scriptId: 1Fkl34P7p395k...）
  └─ LineWebhook.gs / doPost
```

⚠️ **clasp push 前必確認 .clasp.json scriptId — 曾連續 3 天推錯專案**

| 你改了什麼 | 會壞什麼 |
|-----------|---------|
| .clasp.json scriptId | 推到錯的 GAS 專案，正確專案沒被更新 |
| ApiEndpoint.gs 參數格式 | A6 bot 呼叫失敗 |
| createQuote 欄位寫入邏輯 | QUOTE_DRAFT 公式/下拉驗證被破壞 |
| generateProposalV2 頁面邏輯 | Slide 排版/圖片/文字全錯 |

### 3. Bot → main branch（worktree 看不到）

```
launchd bot（A1 Telegram + A6 報價）→ 讀 main branch
A0 開的 Code task → 可能在 worktree 裡
```

⚠️ **worktree 裡的 commit 不會自動到 main — bot 看不到改動**

### 4. A0 → A1 委派鏈

```
A0（Cowork）→ 開 Code task → A1（Claude Code terminal）
             必須帶：完整 recall prompt + 具體接續點
             漏帶 = A1 完全失憶
```

### 5. OAuth Token 單點故障

```
~/.claude/mcp-keys/google-token.json
  scope: spreadsheets + drive（沒有 presentations）
  ├─ A1 讀/寫 Sheets
  ├─ A5/A6 GAS 操作
  └─ A4 Drive 照片存取
```

⚠️ **token 過期 = 全部 agent 同時失去 API 存取**

---

## Agent 間資料流

```
┌─────────────────────────────────────────────────┐
│                  業務漏斗                        │
│                                                  │
│  A2(SEO) ──關鍵字──→ A3(廣告/社群)               │
│    ↑ 圖片              ↑ 素材                    │
│  A4(影像) ─────────────┘                         │
│    │ image_url                                   │
│    ↓                                             │
│  Items 表 ←── A5(報價引擎/擁有者)                 │
│    │                                             │
│    ├──→ A6(報價助手) → GAS createQuote → Slide    │
│    └──→ A7(客服) → 定價門檻回答                   │
│                                                  │
│  A2/A3 導流 ──→ A5/A6 轉單                       │
│  A7 問題熱點 ──→ A2/A3 內容方向                   │
│  A7 急件 ──→ A6 快速報價                          │
│  A8(影音) ←── A4 素材 + A2 SEO 標題 + A3 發布節奏 │
└─────────────────────────────────────────────────┘
```

## 共用資源一覽

| 資源 | 擁有者 | 讀取者 | 改動風險 |
|------|--------|--------|---------|
| MAPLAB_外燴系統_v0.1（Sheets） | A5 | A6, A7, GAS | 🔴 極高 |
| Items 表（108 品項） | A5 | A6, A7, Slide, A4(寫 K 欄) | 🔴 極高 |
| QUOTE_DRAFT 母版 | A5 | A6(fromMaster), GAS | 🔴 極高 |
| Task Board（Sheets） | A1 | A0(Dashboard) | 🟡 中 |
| CURRENT_STATUS.md | A1 | 全部 agent + Extension | 🟡 中（格式=API契約） |
| recalls/*.md | A1 | Extension + 各 agent 冷啟動 | 🟡 中 |
| google-token.json | A1 | A1, A4, A5, A6 | 🔴 極高（單點故障） |
| GAS 報價系統 | A5/A1 | A6 bot | 🔴 極高 |
| GAS LINE 對話 | A1 | LINE Webhook | 🟡 中 |
| ASSET_LOG（Sheets） | A4 | A4 | 🟢 低（獨立） |
| WordPress | A2 | A3(導流) | 🟡 中（改 slug 斷 SEO） |

## 常見改動影響速查

| 你要做的事 | 查這些 | 通知誰 |
|-----------|--------|--------|
| 改 Items 欄位 | QUOTE_DRAFT 公式、A6 createQuote、Slide 模板 | A5, A6, Owner |
| 改 GAS 函數 | .clasp.json scriptId、ApiEndpoint 參數、A6 bot 呼叫邏輯 | A1, A6 |
| 改 CURRENT_STATUS 格式 | Extension parseStatus()、popup.js detectOverdueTasks() | A1(Extension) |
| 改 recalls/*.md | Extension 注入的 prompt 內容 | A1(Extension) |
| 改 checkpoint.sh | recalls 自動更新、CURRENT_STATUS 生成、決策提示 | 全部 agent |
| 改品項照片/K欄 | Slide 生成、Items 表 | A4, A5 |
| 改 WordPress slug | SEO 排名、反向連結 | A2, Owner |
| 改 GTM/Pixel | Google Ads 轉換追蹤、Meta Ads 歸因 | A3, Owner |
| 改合約模板 | A6 四種合約生成邏輯 | A6, Owner |
