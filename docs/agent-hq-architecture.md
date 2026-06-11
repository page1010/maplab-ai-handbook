# AGENT-HQ 架構 — 集團共用層設計（v1.0）

建立：2026-06-11 ｜ 設計：B1（Owner 指示「你來解決這個問題」）
狀態：✅ Owner 已核准方向（「全部都要做」前例 + 本次直接指派），等執行遷移

---

## 1. 問題定義

兩個專案（MAPLAB 外燴公司 / Investment OS 投資公司）共用 Mac mini、Chrome Extension、版本治理，但共用資產全部住在 `maplab-ai-handbook` 裡，造成：

- Investment OS session 看不到共用檔案
- 側邊欄讀不到 session root 之外的檔案（File could not be read）
- 沒人說得清哪份是正本，worktree 髒、所有人做所有事

**根因：共用層沒有自己的家。**

## 2. 目標結構（控股公司模式）

```
/Users/pagemacmini/
├── agent-hq/                 ← 新 repo（page1010/agent-hq, private）：集團平台
│   ├── chrome-extension/     ← 唯一正本（從 maplab 遷出；Desktop symlink 改指這裡）
│   ├── governance/
│   │   ├── AGENT_RULES.md    ← 全域行為準則（跨公司部分）
│   │   ├── STARTUP.md        ← 召喚 prompt / startup check
│   │   └── ROLES.md          ← A 系列 + B 系列 + WIN 角色對照
│   ├── panel/
│   │   └── owner_requirements_panel.md  ← 跨公司 session log（唯一一份）
│   ├── runtime/
│   │   ├── launchd/          ← 所有 plist 的登記處（Mac mini 排程唯一真相）
│   │   └── PORTS.md          ← 18501/18502/8501 等 port 登記
│   ├── skills/shared/        ← task-progress-guide、credentials 路由等跨專案 skill
│   ├── memory/
│   │   └── hermes/           ← Hermes 操作程序記憶的歸檔鏡像
│   └── data-policy.md        ← 資料保留 / 壓縮 / 刪除規則
│
├── maplab-ai-handbook/       ← 外燴公司：A0-A8 業務（SEO/報價/LINE/照片/影音）
└── investment-os/            ← 投資公司：B1-B4 + WIN（面板/telebotfin/研究）
    （目前本機在 /Users/pagemacmini/Documents/New project，遷移時搬到家目錄平級）
```

## 3. 路徑契約（防「找不到檔案」的三條規則）

1. **共用資產只活在 agent-hq**。公司 repo 引用（路徑/symlink），禁止複製副本。
2. **三個根目錄是固定絕對路徑**，寫進每個 agent 的 handoff prompt 頭三行：
   ```
   hq:      /Users/pagemacmini/agent-hq
   maplab:  /Users/pagemacmini/maplab-ai-handbook
   ios:     /Users/pagemacmini/investment-os
   ```
3. **Claude Code 設定 additionalDirectories** 含上述三路徑（`~/.claude/settings.json`），
   側邊欄與工具永遠可讀，無論 session 從哪個 repo 啟動。

## 4. 模型分工

| 層 | 模型 | 職責 | 理由 |
|---|------|------|------|
| 管理層 | Claude Code | 治理、review、commit 把關、派工、架構決策 | Owner 指定 |
| 主力產能 | Codex / Antigravity | 大量寫碼、批次實作、長任務 | 額度多 |
| 固定流程 | ollama（gemma/qwen） | A6 報價單、telebotfin 推播等模板化流程 | 零成本、可離線 |
| 操作手 | OpenClaw / Hermes | computer use、貼指令到雲端模型窗口、遠端操作 | 系統級控制 |

派工原則：Claude 收到任務 → 判斷層級 → 模板化交地端、大量碼交 Codex/Antigravity、需要桌面操作交 OpenClaw/Hermes，Claude 只做驗收與 commit。

## 5. 資料閉環（修「只爬不用、硬碟焦慮」）

### 5.1 事實基線（2026-06-11 量測）

| 項目 | 大小 | 判定 |
|------|------|------|
| 磁碟總用量 | 802GB / 926GB | ⚠️ 89% |
| Google Drive CloudStorage | **531GB** | 🔴 最大元兇，改串流可釋放數百 GB |
| Investment OS repo | 1.7GB（archive 243MB） | 🟡 可控，需保留政策 |
| maplab repo | 474MB（bot 161MB） | 🟢 健康 |
| Hermes | 3.3GB（本體 2.7GB） | 🟢 正常 |
| Hermes memories/ | **0 bytes** | 🔴 地端記憶零利用 |

### 5.2 資料保留規則（data-policy.md 草案）

- raw 爬檔：30 天後 gzip 壓縮，90 天後刪除（git 已有歷史的 durable 摘要除外）
- archive/：每季由 B3 整理，保留摘要、刪 raw
- Google Drive：Owner 在 Drive 設定改「串流檔案」（人工一次性動作）
- logs/：超過 10MB 自動 rotate（launchd weekly job）

### 5.3 Hermes 記憶啟用

Hermes 記憶定位 = **操作程序記憶**（哪個網站怎麼登入、哪個 UI 怎麼點、雲端模型窗口怎麼貼），
不是知識庫。要求 Hermes 任務結束時把學到的操作寫進 `~/.hermes/memories/`，
agent-hq/memory/hermes/ 每週鏡像備份一份。

### 5.4 A7 LINE 訓練管線

```
LINE Sheet (CONVERSATION_LOG)
  → case_store.py SQLite（已存在 ✅）
  → 每晚 export 清洗成 JSONL（客戶問句 → 正確回覆/報價 配對）
  → 累積 ≥500 對後 fine-tune 地端 qwen（LoRA）
  → 用真實舊對話 replay 模擬測試，比對模型回覆 vs 業務實際回覆
```

## 6. 遷移步驟（task card: T-HQ-001）

| Phase | 動作 | 風險 | 負責 |
|-------|------|------|------|
| 1 | 建 `page1010/agent-hq` private repo + 本機 clone | 低 | B1（建 repo 屬 SECTION 5 新 repo，本文件即 Owner 核准依據） |
| 2 | 遷 chrome-extension（git mv + Desktop symlink 改指 + Chrome 重新載入驗證） | 中（需三層驗證，見 pitfalls 2026-05-29） | B1 |
| 3 | 遷 governance/panel/shared skills；maplab 與 ios 留指向檔 | 低 | B1 |
| 4 | launchd plists 登記到 runtime/；改 `~/.claude/settings.json` additionalDirectories | 低 | B1 + Owner（settings 需手動） |
| 5 | data-policy 落地：log rotate job + archive 壓縮 job | 低 | B1 |
| 6 | Hermes 記憶啟用 + A7 JSONL export 腳本 | 中 | B1 寫，地端模型跑 |

每 Phase 一個 commit，壞了用 git 還原上一版（Owner 的版本治理原則）。

## 7. 不做的事

- 不把兩家公司 repo 合併（業務隔離、權限隔離、未來可能拆帳）
- 不把 secrets 收進 agent-hq（維持各 runtime 本機 .env）
- 不動 Investment OS broker/runtime 高風險 surface
