# A2/A3/A4 Approval-Ready Automation Protocol

建立：2026-06-09
Owner：Page
適用角色：A2 SEO / WordPress、A3 Ads / Social、A4 Assets
狀態：v0.1 protocol

## Purpose

A2/A3/A4 不應停在「這要 Owner 批准所以不能做」。正確行為是自動跑到
approval-ready plan：把為什麼要做、要改什麼、預期效果、影響範圍、風險、
驗收方式與 rollback 全部整理好，交給 Owner 批准、提問、退回或縮小範圍。

外部正式系統變更可以被規劃、自動預演與產生執行清單；但不能靜默執行。

## Operating Principle

分成三層：

1. **Discovery / Evidence：自動允許**
   - Read-only 檢查 WordPress、live URL、GSC/GA、Google Ads、Meta Ads、素材庫、Sheets。
   - 產出 evidence matrix、截圖/讀回紀錄、缺口清單。

2. **Approval-Ready Plan：自動必做**
   - 針對每個可改善點，自動產生計畫包。
   - 計畫包要讓 Owner 可以直接批准或問問題，不需要 Owner 幫 agent 補分析。

3. **Execution：精確批准後才做**
   - WordPress 發布或修改已發布頁面、Google Ads / Meta Ads 設定、GTM/Pixel、Rank Math、預算、開關、受眾、付款，都必須有 Owner/A1 批准的精確範圍。
   - 執行後必須留下 before/after、evidence、rollback note、task-card update 與 commit。

## Role Loop

### A4 First: Asset Readiness

A4 先整理素材：

- 檢查照片是否可公開使用。
- 產 WebP / 尺寸 / slot / alt / caption / no-face/no-logo/no-alcohol gate。
- 回傳 `a4_asset_manifest.md`。

### A2 Second: SEO / WordPress Plan

A2 使用 A4 manifest 和 live URL evidence：

- 決定對應 live page / draft / post。
- 保護 slug，不把 planned slug 當 live URL。
- 產 SEO copy、內連結、title/meta、圖片 slot、CTA。
- 回傳 `a2_seo_wordpress_plan.md`。

### A3 Third: Ads / Tracking Plan

A3 使用 A2 landing plan：

- 檢查 Google Ads keyword / final URL / conversion action。
- 檢查 Meta campaign / ad set / objective / audience / destination。
- 檢查 GTM / Pixel / UTM 是否能驗收。
- 回傳 `a3_ads_strategy_plan.md`。

### A2 Integration

A2 最後整合：

- 哪些可以直接做 repo/proposal。
- 哪些需要 Owner 批准。
- 哪些資料不足。
- 哪些不要做。
- 回傳 `owner_approval_card.md`。

## Approval Card Required Fields

每張 approval-ready card 必須包含：

```md
TASK_ID:
ROLE:
STATUS: approval_ready

WHY:
為什麼現在值得做。

EVIDENCE:
目前證據、數字、URL、截圖或讀回路徑。

PLAN:
準備改什麼，逐項列出。

EXPECTED_EFFECT:
預期改善什麼，例如 SEO 可讀性、詢問率、轉換追蹤、廣告導流一致性、素材品質。

IMPACT_SCOPE:
會影響哪些 WordPress page/post、campaign、ad set、素材、GTM、Pixel、預算、追蹤或報價 CTA。

RISKS:
可能副作用。

ROLLBACK:
出問題如何退回。

VALIDATION:
做完如何驗收。

OWNER_DECISION:
請 Owner 批准 / 提問 / 退回的具體選項。
```

## Owner Decision Syntax

Owner 可直接回：

- `批准 A2-SEO-001`
- `只批准草稿，不發布`
- `批准 A3-ADS-002，但預算不動`
- `退回，先補 A4 素材證據`
- `暫停，不要改這個 campaign`
- `縮小，只做 B 公關公司窗口 detail read-only`

## Output Contract

每輪固定寫到：

```text
workbook/reviews/JOB-A2A3A4-APPROVAL-READY-YYYYMMDD/
```

至少包含：

- `brand_memory_check.md`
- `a4_asset_manifest.md`
- `a2_seo_wordpress_plan.md`
- `a3_ads_strategy_plan.md`
- `owner_approval_card.md`
- `integration_review.md`

若某角色沒有可用輸入，該角色輸出仍要存在，並標明 `NO_ACTION`、原因與下一個可補證據。

## Forbidden Without Approval

- 發布 WordPress。
- 修改已發布 WordPress page/post。
- 修改 Google Ads / Meta Ads 預算、投放、受眾、開關、付款。
- 修改 GTM / Pixel / conversion action。
- 修改 Rank Math 付費/退訂相關設定。
- 讀 secrets、API keys、cookies、password。
- 用錯誤 Chrome/agent 帳號當 Owner evidence。

## Done Definition

此 protocol 的「自動跑起來」不等於外部系統已修改。Done 分兩種：

- `proposal_done`：已產出 approval-ready plan，Owner 可批准或提問。
- `execution_done`：Owner 已批准精確範圍，agent 已執行、驗收、回寫 task card 並 commit。

沒有 `owner_approval_card.md` 的巡查，不算完成。沒有 before/after evidence 的正式變更，不算完成。

## Resume Prompt

我是 A2/A3/A4 approval-ready automation runner。先讀 `CURRENT_STATUS.md`、`AGENT_RULES.md`、`projects/a2a3a4-approval-ready-automation.md`、`handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`，再讀 A2/A3/A4 各自 recall。
任務：自動跑 read-only discovery，產 A4 asset manifest、A2 SEO/WordPress plan、A3 Ads strategy plan，最後整合 `owner_approval_card.md`。
邊界：可以自動規劃到可批准狀態；未經 Owner/A1 精確批准，不發布、不改 Ads、不改 GTM/Pixel/Rank Math、不動預算或開關。
