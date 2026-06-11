# Social Accounts Credential 技能書

版本：v1.0 | 建立：2026-06-11 | 維護者：A1

---

## 用途

FB / IG / Threads / 其他社群平台需要登入態時，先讀本技能書。這份文件只記取用流程，不存帳號、密碼、token、cookie、OTP、backup code。

---

## Credential 位置

社群帳號 credential 由 Owner 管理，可能存於：

1. Owner Chrome 既有登入態。
2. A0 / Notion MCP 可讀的 Owner credential vault / index。
3. 已授權的本機 MCP 或 credential skill。

若 task card / handoff 沒有標出 Notion page、database、帳號 label 或 Owner Chrome route，視為 `auth_missing`，不得自行猜測。

---

## 取用順序

### A. 優先用既有登入態

- 使用 Owner Chrome / visual bridge / 已登入分頁做只讀收集。
- 不在 agent 對話中要求 Owner 貼密碼。
- 不導出 cookie、session、localStorage 或瀏覽器 profile。

### B. 透過 A0 / Notion MCP 做受控 handoff

如果 Owner 明確指定「帳密在 Notion」，由 A0 或 Owner-approved A1/Codex 走受控流程：

```text
A0: 請依 task card 指定的社群帳號 label，確認 credential vault 是否有可用登入方式。
只回報 account label、可用/不可用、需要 Owner 5 分鐘操作；不要把密碼/token/cookie 貼進 repo 或群聊。
```

可接受的回報例：

```text
credential_route: notion_vault
account_label: MAPLAB FB/IG owner account
status: available_to_owner_chrome_login
owner_action_5min: open Owner Chrome and confirm logged-in FB session
```

不可接受的回報：

```text
password: ...
token: ...
cookie: ...
OTP: ...
```

### C. 沒有 credential 時輸出 auth_missing

若 A/B 都不可行，輸出到 review bundle：

```text
auth_missing:
  service: FB / IG / Threads
  tried:
    - checked Owner Chrome route
    - checked task card credential reference
    - checked A0/Notion credential route availability
  reason: no usable login session or approved credential handoff
  owner_action_5min: open Owner Chrome FB session or ask A0 to validate the Notion credential label
```

不得改跑舊 corpus、公開 fallback 或未登入結果來假裝完成今天的社群報告。

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| 讀 account label / route availability | 不含密碼本體 |
| 使用既有登入態做只讀收集 | 例如 Owner Chrome 已登入 FB |
| 產出 `auth_missing` / `source_route_health.md` | 讓 Owner 知道缺哪個登入步驟 |

---

## 禁止操作

- 不讀取、列印、commit、記憶、轉貼密碼、token、cookie、OTP、backup code。
- 不把 credential 文件貼進 Gemini / OpenClaw / Chrome side panel prompt。
- 不用 agent 自己的私人瀏覽器帳號替代 Owner 帳號。
- 不切換帳號、登出、改密碼、改 2FA、接受政策、開關社群/廣告設定。
- 不發布貼文、不送訊息、不改廣告、不觸發費用。

---

## IOS-FB 特別規則

IOS-FB 在跑 FB Radar / social source route health / candidate review 前，必須先確認：

1. collection route 是 Owner Chrome logged-in、A0/Notion credential handoff，或明確公開資料路由。
2. report 使用的是本次收集或明確標為 historical / shadow sample 的資料。
3. 若缺登入，輸出 `source_route_health.md` 的 `auth_missing`，不要用歷史樣本生成「今日報告」。
