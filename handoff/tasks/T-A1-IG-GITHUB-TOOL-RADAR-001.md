# T-A1-IG-GITHUB-TOOL-RADAR-001 — IG and GitHub Tool Evidence Radar

## 接續狀態

- **狀態**: 🔄 IN_PROGRESS
- **最後活動**: 2026-08-27 Codex A1
- **接續點**: 建立 implementation commit，補 validation receipt／SSOT／commit hash 後做 docs checkpoint。
- **阻塞**: 無。外部 OAuth、API key、credits、security scan 與安裝均不在本版授權範圍。
- **assigned_session**: 2026-08-27 / Codex acting as System Tool Research and Process Optimization Engineer
- **可逆性**: 可逆。新 repo skill、離線 evaluator、任務卡與收據皆可由 task-scoped commit revert；沒有外部寫入。

## Owner 需求

用已登入 Chrome 的 Instagram 做工具／GitHub 唯讀研究；自行判斷適用性，只採用能提升 MAPLAB 且不重複的工具或流程，並把可複用判斷回灌 skills／SOP。

## 本版 v0.1

- [x] Chrome Instagram 唯讀取樣；不按讚、不追蹤、不留言、不私訊、不儲存。
- [x] 現有 skill lifecycle audit：`skills=14 duplicates=0`。
- [x] 官方 GitHub／產品文件、license、維護、runtime、credential、egress、cost 與 overlap 核實。
- [x] 建立 `maplab-tool-evidence-radar` 與 deterministic evaluator。
- [x] 產生候選矩陣與採用／試點／保留／淘汰結論。
- [x] validators、14 個 focused tests、7 情境 independent forward regression 與 skill audit。
- [ ] task-scoped implementation commit、validation receipt、SSOT 與 docs checkpoint。

## Resume Prompt

我是 A1/Codex System Tool Research and Process Optimization Engineer。
環境是 `/Users/pagemacmini/maplab-ai-handbook`。
先讀 `CURRENT_STATUS.md`。
再讀 `pitfalls.md` 最後三條 2026-08-27 規則。
再讀本卡與 `workbook/reviews/JOB-A1-IG-GITHUB-TOOL-RADAR-20260827/validation_receipt.md`。
Instagram 只作 SOCIAL_LEAD，不是安裝授權。
不要按讚、追蹤、留言、私訊或儲存貼文。
技術工具只採官方 GitHub／官方文件作 PRIMARY_IDENTITY。
先跑 lifecycle audit，重複工具直接用既有路徑。
第三方 skill 必須 pin、inspect、quick_validate、smoke、audit。
不得建立 OAuth、API key、GitHub write token 或訂閱。
不得耗影片 credits、上傳客戶素材、執行 live security scan 或發佈。
Context7 若無新授權只可 public-code pilot proposal。
Strix 必須有明確 authorized target/scope 才可掃描。
Higgsfield 只可 synthetic/public fixture pilot，仍需 credential/cost gate。
Skill UI、Taste、ai-copywriter 要先以現有 lifecycle／Impeccable／品牌 SEO SOP 去重。
所有決策須留 candidate JSON 與 evaluator output。
若外部能力沒有 live receipt，不能寫成已連接或已採用。
