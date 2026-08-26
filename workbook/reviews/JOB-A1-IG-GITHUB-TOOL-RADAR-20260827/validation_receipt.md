# JOB-A1 IG／GitHub 工具證據雷達 — Validation Receipt

- 日期：2026-08-27（Asia/Taipei）
- 狀態：`PASS`
- 角色：A1 / System Tool Research and Process Optimization Engineer
- Implementation commit：`4a930e8` (`feat(skills): add evidence-gated tool radar`)
- 外部狀態：`READ_ONLY_RESEARCH_ONLY`

## Owner 需求與本版邊界

用 Owner 已登入的 Chrome 在 Instagram 做工具／GitHub 唯讀研究，自行淘汰不適合或重複的工具，把可複用的採用判斷回灌成 MAPLAB skill／SOP。

本版沒有按讚、追蹤、留言、私訊、儲存或發布；沒有建立 OAuth、API key、GitHub token、訂閱或帳號；沒有安裝第三方候選、執行安全掃描、上傳素材或消耗生成 credits。

## Instagram discovery evidence

Instagram 只作 `SOCIAL_LEAD`：

- [jayte.genai — Playwright／Supabase／Strix／Skill UI／Context7](https://www.instagram.com/jayte.genai/reel/DcJK_hHprkV/)
- [jayte.genai — UI inspiration claim](https://www.instagram.com/jayte.genai/reel/DbLMNb_TnSe/)
- [jasonxtsai — ai-copywriter](https://www.instagram.com/jasonxtsai/p/DbxxjhQCegU/)
- [jasonxtsai — Impeccable／Taste／Higgsfield](https://www.instagram.com/jasonxtsai/p/Dcda5y2CegR/)

需要留言才揭露的 UI 網站清單未留言索取，也沒有猜工具名稱；該項只保留為 `NOT_A_TOOL` reference。

## Candidate matrix

| Candidate | Primary identity / pinned evidence | License / terms | MAPLAB overlap and risk | Decision |
|---|---|---|---|---|
| Context7 | [upstash/context7 `9a384f0`](https://github.com/upstash/context7/commit/9a384f099011d6299df530fd8d7a22510b2004d5), release `4.0.3` | MIT | 可補公開套件版本文件，但查詢會送遠端且與官方 Web 查證部分重疊 | `PILOT`：只限公開 library／合成問題，仍回官方文件二次核實；本版未安裝、未接 API key |
| Strix | [usestrix/strix `bfaaa90`](https://github.com/usestrix/strix/commit/bfaaa904f29ad976a751cc894c0cf534d89bc6ff), release `v1.5.3` | Apache-2.0 | 主動滲透面、Docker／LLM key、預設 telemetry；目標衍生內容可能送外部 LLM | `HOLD`：只有明確所有權、target/scope、隔離 staging、telemetry off 才能另案 pilot |
| Skill UI | [gishamer/skill-ui `3a91861`](https://github.com/gishamer/skill-ui/commit/3a91861f421f2ea0589aa3219e432e28071b21f0) | Repo 無 LICENSE；`package.json` 只宣稱 MIT | 重複既有 lifecycle；會找 GitHub token、recursive replace、建立 branch／PR，Electron 加密不可用時以 base64 fallback | `REJECT` |
| Taste | [tyfarrago-hub/taste `acbb3e9`](https://github.com/tyfarrago-hub/taste/commit/acbb3e9c9051e096cb9e5e5cc1af88d56bc05459) | 聚合包 provenance／attribution 不完整 | 重複已鎖版 Impeccable；含未渲染 placeholders、自動安裝與跨 harness 寫入；README 與實際 tree 不符 | `REJECT` whole pack |
| ai-copywriter | [mikiarlo3/ai-copywriter `08b53b1`](https://github.com/mikiarlo3/ai-copywriter/commit/08b53b1ad39887cd94cbaab61cac3b6aae2d8518) | [MIT](https://github.com/mikiarlo3/ai-copywriter/blob/08b53b1ad39887cd94cbaab61cac3b6aae2d8518/LICENSE) | 無 credential surface，但與品牌／SEO／Impeccable 高度重疊；clickbait／viral defaults 與品牌語氣衝突，package validator 不驗文案品質 | `HOLD`：不安裝；最多另案抽象 anti-AI audit 概念做離線 A/B eval |
| Higgsfield | [官方 MCP](https://higgsfield.ai/mcp), [Privacy Policy](https://higgsfield.ai/privacy-policy) | Proprietary terms | OAuth＋subscription＋metered credits；無原生 session cap；非 Enterprise 輸入／輸出可能用於訓練，與本地 motion／正式剪輯 SOP 部分重疊 | `HOLD / DO NOT INSTALL`：若另案，只可 Owner 核准的一次純合成 5 秒 web pilot |
| UI inspiration list | IG Reel only | N/A | 只有設計參考 claim，精確連結未公開 | `NOT_A_TOOL` |

Context7 的遠端資料邊界依 [官方 Data Privacy](https://context7.com/docs/security/data-privacy)；Strix 的 telemetry 與 runtime 依 [官方 configuration](https://github.com/usestrix/strix/blob/main/docs/advanced/configuration.mdx) 與 [quickstart](https://github.com/usestrix/strix/blob/main/docs/quickstart.mdx)；Higgsfield 的費用與 agent 邊界依 [credits](https://higgsfield.ai/creator-hub/help-center/credits/how-credits-work) 與 [agent integration](https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-ai-agent)。

## Adopted local improvement

新增 `.agents/skills/maplab-tool-evidence-radar/`：

- `SKILL.md`：規定 social discovery、primary identity、license／provenance、overlap、credential、egress、cost、side-effect 與 receipt gates。
- `references/candidate-contract.md`：定義 `ADOPT / PILOT / HOLD / REJECT / NOT_A_TOOL` 與資料交叉欄位。
- `scripts/evaluate_candidate.py`：離線 deterministic evaluator；不連網、不安裝、不改外部狀態。
- `scripts/test_evaluate_candidate.py`：覆蓋 identity、license、duplicate、OAuth、scan、cost、資料邊界與型別混淆。
- 七份 candidate JSON 與 `evaluation_results.json`：讓本輪結論可重跑，不只存在聊天裡。

Evaluator 只判斷輸入 contract，不能自行證明研究者是否誠實填寫 `official_verified`、`smoke=passed` 或完整 side effects；因此官方來源與 receipt 仍是強制證據，不可用 evaluator exit 0 代替。

## Validation

- Focused evaluator tests：`14/14 PASS`。
- Skill validator：`Skill is valid!`。
- Lifecycle audit：`skills=15 duplicates=0`。
- Candidate replay：`7/7` 與 committed `evaluation_results.json` 完全一致。
- Independent forward regression：7 個代表情境全部符合預期；social-only=`REJECT`、OAuth＋付費媒體=`HOLD`、低風險本地工具=`ADOPT`、security scanner=`HOLD`、substantial-overlap UI=`PILOT`、truthy string=`ContractError`、private＋public-only egress=`ContractError`。
- Independent hash：evaluator `0b82089fbfec47c0177ac62fa5e69e69fcb1fdcdd81a494449eaba9f1fdb6427`；tests `dcfbbd1036731a8d693f4836d06adba7f9feab95102fc7274d920a29585ca3fc`；contract `6e99cdf1fdedde2f12d66eeb017386389647f28c92e43d4667152391d394a5e8`。
- `git diff --check`：`PASS`。

第一次 independent forward test 曾抓到三個高風險缺口：`bool("false")`、private／public-only 矛盾，以及 substantial overlap 可誤升 `ADOPT`。本版已加入 strict JSON boolean、資料交叉欄位拒絕與 substantial-overlap 上限 `PILOT`；第二次獨立回歸確認無高風險誤升。

## Final receipt summary

```text
ADOPTED_NOW: MAPLAB tool evidence radar + deterministic evaluator + seven reproducible candidate records
PILOT_LATER: Context7, public libraries and synthetic questions only; requires an explicit credential/cost gate and isolated receipt
HELD: Strix; ai-copywriter whole skill; Higgsfield
REJECTED: Skill UI; Taste whole pack
NOT_A_TOOL: comment-gated UI inspiration list
SOCIAL_ACTIONS: none
EXTERNAL_WRITES: none
ROLLBACK: git revert 4a930e8
NEXT_BOUNDED_ACTION: use this radar on the next concrete social lead; do not connect any held or pilot service without its named gate
```
