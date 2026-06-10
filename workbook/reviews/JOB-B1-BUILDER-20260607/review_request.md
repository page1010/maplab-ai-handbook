# Review Request → B2 Reviewer

**From:** B1 Investment OS Builder · **Job:** JOB-B1-BUILDER-20260607
**Artifact:** `workbook/dashboards/maplab-ops-game-dashboard.html`

## 請 B2 審查的重點
1. **資料 freshness / 正確性**:`D[]` 內 16 個 IOS 角色的 mission / jobs / dashboard / telegram 是否仍與 `config/investment_os_role_registry.json` 一致(我抄的時間點 = 2026-06-07)。registry `generated_at` 為 2026-06-03,若期間有改動請點出。
2. **誠實降級鐵則**:每部門 FLOOR 與守則是否確實反映 pitfalls(尤其 KOL「拿不到 NotebookLM 就 FAIL,不准用標題假裝」)。
3. **越權檢查**:確認此產出**只新增檔案**、無觸碰 runtime / secrets / 生產 DB、無下單語言、無把 proposed_orders/simulation=True 講成本地模擬單(IOS-INVENTORY / IOS-SIM 卡片用詞)。
4. **狀態燈標註**:KOL 標 `warn`、CHIP 標 `idle` 等為靜態手標,是否會誤導為即時健康?需不需要在 UI 上更明確標「示意,非即時」。

## 我已自驗 (見 validation_report.md)
- JS syntax OK;21 部門結構完整;單檔零依賴;部門 id 對齊 registry。

## 已知限制
- 非生產渲染器,狀態燈為靜態示意;資料為手抄(未自動同步 registry)。

→ 若僅資料微調 = 退回 **B1** 修 `D[]`;若要接即時狀態/自動同步的取捨 = **B4** 判是否值得。
