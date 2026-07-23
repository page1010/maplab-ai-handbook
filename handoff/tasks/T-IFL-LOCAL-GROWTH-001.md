# T-IFL-LOCAL-GROWTH-001 — InnerFlowLab Local Growth 第三產品線

## 接續狀態

- **狀態**: ✅ COMPLETE（v0.1.1 live draft validated；公開發布受 gate 保護）
- **最後活動**: 2026-07-23
- **動作可逆性**: 可逆
- **接續點**: Canonical source 位於 `/Users/pagemacmini/Documents/innerflowlab-local-growth`；本卡只保留跨專案指標。外掛 v0.1.1 已在 InnerFlowLab 啟用，公開 offer 維持 draft，管理台為 private。
- **阻塞**: 僅公開發布 gate：現有「聯絡我們」頁沒有表單或公開聯絡方式；補上並驗證後，仍需 Owner 明確批准發布。

---

建立：2026-07-23 | **負責**: B1 | **Reviewer 角色**：B2

---

## (A) Goal / Outcome

建立 `InnerFlowLab Local Growth` 為第三條可收費產品線：用合成資料完成
「商家輸入 → 一頁式網站 brief → SEO/轉換檢查 → 主管驗收 → 客戶成果 receipt」
閉環，同時在程式層拒絕 MAPLAB 實際外燴資料與 Investment OS 資料。

## (B) Definition of Done（GO Prompt 五要素）

| 要素 | 內容 |
|------|------|
| Outcome | 同上；新產品可單獨建置、測試、封裝，不依賴另外兩套 runtime。 |
| Verification | Python 單元測試、schema parse、隔離掃描、合成案例端到端、WordPress package 靜態檢查、live 頁 readback（若本輪發布）。 |
| Constraint | 禁止讀取或複製真實客戶、報價、LINE、Drive、外燴 WordPress、投資帳戶、持倉、ticker、broker、SQLite、credentials、raw logs。 |
| Iteration Policy | 每輪證據 append 到獨立 repo 的 `receipts/YYYY-MM-DD/`；MAPLAB 僅留本指標卡。 |
| Error Handling | 任一 contamination、未批准發布或 live 權限問題立即 fail closed；不得用「看起來沒事」取代測試。 |

## (C) Constraints + Error-handling / Escalation

**Constraints（不能碰什麼）**：

- 新產品程式不得 import 或讀取 `tools/innerflowlab_personal_secretary_snapshot.py`。
- 新產品不得以 MAPLAB repo、Investment OS repo 或它們的 runtime 作資料來源。
- 教材只可使用 synthetic / redacted / customer-approved inputs。
- 公開頁不得顯示內部 QA、檔案路徑、憑證、客戶名單或未核准價格。
- Google Business Profile、Ads、Analytics 的登入與修改維持另外的 approval gate。

**Error Handling / Escalation（何時停下回報，回報給誰）**：

- 隔離掃描發現禁用 key、runtime marker 或本機絕對路徑：停止產出並回傳具體欄位。
- 客戶未勾選 `publish_approved`：只能輸出 draft，不得標記可發布。
- WordPress live readback 與 repo 不一致：以 live HTML/REST 為準並保留 rollback。

## 目標

1. 建立第三產品線的唯一真相源與資料契約。
2. 把 MaplabKitchen 已驗證的訓練方法抽成可泛用 curriculum，不搬業務資料。
3. 以一個澳洲在地商家的合成案例跑完整閉環。
4. 建立獨立 WordPress 外掛與公開銷售頁，不修改私人秘書的 snapshot schema。
5. 產生 validation receipt、狀態回寫與 Resume Prompt。

## 已完成

| Commit | 日期 | 內容 |
|--------|------|------|
| `4258fe2` | 2026-07-23 | 建立獨立 repo、契約、schema、合成 curriculum、validator、WordPress 外掛與本機驗證。 |
| `8f47bff` | 2026-07-23 | 公開 offer 維持 draft，準備 live 管理員 preview。 |
| `b6b5182` | 2026-07-23 | v0.1.1 live draft 驗證：16/16、污染 0、WordPress/CTA/匿名/視覺 readback。 |
| `f6de297` | 2026-07-23 | live 視覺證據正規化為真正 PNG。 |

## 現在卡在哪裡

第三產品線切割與 live draft 驗證完成。尚未公開，因商業 contact route 與 Owner
publication approval 是刻意保留的 release gate。

## Blockers

1. 現有 `聯絡我們` 頁 HTTP 200，但只有標題，沒有可用表單、電話、Email 或其他公開聯絡方式。
2. 補上 contact route 後，仍需 Owner 明確批准，才可把 `/local-growth/` 從 draft 改為 publish。

## 接續 Prompt

```text
你是 InnerFlowLab Local Growth 的 B1 Builder / B2 Review 接手者。
canonical repo: /Users/pagemacmini/Documents/innerflowlab-local-growth
先讀該 repo 的 AGENT_CORE.md、CURRENT_STATUS.md、PRODUCT_CONTRACT.md 與 pitfalls.md。
MAPLAB repo 的 handoff/tasks/T-IFL-LOCAL-GROWTH-001.md 只是一張跨專案指標卡。

上次做到：v0.1.1 已在 WordPress 啟用；16/16 tests、污染 0、desktop/mobile/admin
visual QA、CTA permalink 與匿名 404/404/401 全部通過。公開 offer 仍是 draft，
管理台是 private，真實 tenant / published customer site 都是 0。
下一步：只處理公開 contact route。由 Owner 指定表單或聯絡目的地後，新增並測試；
接著重跑 CTA、匿名、管理員與 responsive readback。沒有 Owner 明確批准不得發布。
Blocker：現有聯絡頁無可用聯絡方式；不得自行暴露私人 Email 或電話。
踩過的坑：方法可以抽取，真實外燴與投資資料、runtime、憑證不可成為新產品依賴。

讀完文件後輸出 Startup Check。必拿：skills/task-progress-guide.md
```
