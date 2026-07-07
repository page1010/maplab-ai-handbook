# Superpowers 內化對照表 — 取其精華，接我們的零件

> 生成：2026-07-07｜來源：https://github.com/obra/superpowers（v6.1.1，live 抓取，非記憶）
> 定位：回答「我們一直沒有複利迴圈，是不是因為沒真正內化 superpowers」。
> 結論先講：**認同一半**。我們抄了它的「目錄」（`skills/superpowers-guide.md` 自 3 月就有路由表），
> 沒抄它的「執法機制」。但複利斷點的第一因更底層（Evolution Channel 三表 07-07 才首建、
> Learning Loop 停在 P1）——帳本沒建，內化做再好也不複利。**兩者都要，順序：帳本先、機制跟上。**

---

## 1. 逐技能對照（它的 14 本 vs 我們的現況）

| Superpowers 技能 | 我們對應的零件 | 差距判定 |
|---|---|---|
| test-driven-development | 無正式 TDD 規則；test receipt 硬規（06-18）管「測了沒」不管「先寫測試」 | 🟡 部分：我們管結果證據，不管紅綠循環 |
| systematic-debugging（4 階段根因） | `skills/systematic-debugging-cloud-guide.md` + 文化 #20 root cause + IS 錯誤 186 fast path | 🟢 已有，且 fast path 比它多走一步 |
| **verification-before-completion** | 文化 #8 Evidence、test receipt、IS 錯誤 185 Eye Proof Gate | 🟡 精神同、**缺禁語清單與 5 步硬序**（見 §2-G2） |
| brainstorming（蘇格拉底式一次一問） | 文化 #2 Question-led（問句必須具體到可執行選項） | 🟢 已有，我們版本更完整 |
| writing-plans（每步 2-5 分鐘、路徑寫死） | `templates/go-prompt-template.md` 五要素 + task card 協議 | 🟡 有骨架、無「步驟粒度」硬規 |
| executing-plans（分批+人工確認點） | 文化 #12 執行迴圈 + Progress Log #N | 🟢 已有 |
| dispatching-parallel-agents | Chrome Extension 召喚 + agent_courier（IS） | 🟢 已有 |
| requesting/receiving-code-review | 三人小組評審制（Claude+Codex+Antigravity，已實跑 3 輪） | 🟢 **我們更強**：跨模型獨立 session，它只是同 session 清單 |
| using-git-worktrees | SECTION 19 無人長跑 worktree-only + cleanup-worktrees job | 🟢 已有 |
| finishing-a-development-branch | 文化 #8「branch 必有收斂路徑」 | 🟢 已有 |
| subagent-driven-development（兩階段審） | 文化 #26 Builder≠Reviewer、Shadow 獨立 session | 🟢 已有 |
| **writing-skills（技能 TDD）** | `generate-skill.sh` + `skills/auto/`（checkpoint 偵測 fix commit 提示生成） | 🔴 **最大差距**：我們的技能/pitfalls 寫完從不驗證有效（見 §2-G1） |
| **using-superpowers（1% 觸發規則）** | CLAUDE.md 技能索引 + superpowers-guide 路由表 | 🔴 **第二大差距**：我們是「建議查表」，它是「行動前強制檢查」（見 §2-G3） |
| （skill description 規範） | 路由表「說明」欄 | 🟡 我們的說明欄踩了它實測過的反模式（見 §2-G4） |

**總分**：14 項裡 8 項我們已有等價或更強（評審、問句、根因、交接尤其強）。
真正該借的是 **4 個執法機制**，不是技能內容。

---

## 2. 四個精華機制（它的原文 → 我們的最小落地）

### G1 技能 TDD：「NO SKILL WITHOUT A FAILING TEST FIRST」🔴 最高槓桿

**它的機制**：寫任何 skill 前，先跑「壓力情境」記錄無 skill 時的失敗行為（RED），
寫最小 skill 驗證行為改善（GREEN），收集新的合理化藉口再加反制（REFACTOR）。

**我們的洞**：190 條 IS pitfalls + 60 本 MAPLAB 技能書，**零條驗證過「冷啟動 agent 讀了真的會避坑」**。
最鐵的反例就是 07-07 當天發現的：pitfalls 早寫了「launchd 不得讀寫 ~/Documents」，
plist 照樣違規死了 8 天——規則沒經過壓力測試，就不知道它攔不住。

**最小落地**（接既有零件，與 IS 錯誤 186 fast path 匯流）：
- pitfall/skill 模板加一欄 `封坑驗證`：一條可執行指令或情境，證明「有這條規則後坑真的進不去」。
  寫不出驗證指令的 pitfall 標 `unverified`，巡查統計 unverified 比例。
- `generate-skill.sh` 產草稿時強制帶 `RED 情境`（沒有 skill 時 agent 會怎麼錯）欄位。
- 高風險規則（碰 runtime/secrets/發布類）→ 用既有三人小組跑一次壓力測試：
  唯讀 Codex session 給它任務但不給 skill，看它掉不掉坑。

### G2 完成宣告禁語 + 五步硬序 🟡

**它的機制**（原文）：`IDENTIFY → RUN → READ → VERIFY → ONLY THEN claim`；
禁語清單：should / probably / seems to / Done! / Perfect! / I'm confident /「就這一次」。
「Skip any step = lying, not verifying」。

**我們的洞**：文化 #8 + test receipt 精神相同但散在 5 份文件，**沒有禁語清單**——
禁語清單的價值是給 reviewer/巡查一個可 grep 的客觀訊號，不用讀懂內容就能抓「無證據宣告」。

**最小落地**：
- `docs/company-values.md` 測試 receipt 段補「完成宣告五步 + 禁語表」（中文版：應該就好了/大概/看起來/完成了！但無 receipt）。
- 巡查腳本對 CURRENT_STATUS 新條目 grep 禁語 pattern＋無 evidence path 者標 `unverified-claim`。

### G3 1% 觸發規則：技能檢查在行動之前，不是之後 🔴

**它的機制**（原文）：「If you think there is even a 1% chance a skill might apply,
you ABSOLUTELY MUST invoke the skill」——在回答問題、探索 codebase、進 plan mode **之前**。
紅旗合理化：「這任務很簡單」「先看一下 context 再說」。

**我們的洞**：CLAUDE.md 索引表寫「按觸發條件搜尋」，是被動查表；agent 略過無後果。

**最小落地**：
- `AGENT_STARTUP_PROTOCOL.md` Startup Check 加必填欄 `Skills loaded: [路徑清單 or "查過索引，無適用"]`——
  缺此欄 = Startup Check 不合格（巡查可機器檢查此欄存在與否）。
- 召喚文化前言（`templates/go-prompt-template.md`）加一句 1% 規則。

### G4 Description 只寫觸發條件，不寫流程摘要 🟡

**它的機制**（實測結論）：description 若摘要了流程，agent 會照摘要做、不讀全文，漏掉細節。
❌ "Use for TDD—write test first, watch it fail..." ✅ "Use when implementing features, before writing code"。

**我們的洞**：`superpowers-guide.md` 路由表的「說明」欄多處是流程摘要（例：「API 流程」「7步 API 工作流」）。
Chrome Extension 30 個 task module 的 description 同理需檢視。

**最小落地**：路由表說明欄改寫為「觸發症狀」語式（漸進，改到哪算哪，不停工重寫）；
新技能書 frontmatter 規範寫進 `generate-skill.sh` 模板。

### 附：Rationalization Table（合理化藉口對照表）— 隱藏的第五個精華

它給每條紀律規則配「實測收集的藉口清單 + 反制句」。我們的 pitfalls 記「觸發條件/根因」
但不記「agent 當時給自己的藉口」。建議 pitfall 模板加選填欄 `當時的合理化`——
這欄累積起來就是我們自己的紅旗清單（例：「巡查列每次新增比較保險」→ 66 筆重複列）。

---

## 3. 不借的部分（明確寫下 do_not_copy，文化 #24）

- **不裝它的 plugin**：我們已有 60 技能書 + 召喚體系 + checkpoint 紀律，裝第二套技能框架
  違反「接線不重造」（SELF_HEALING spec §0），且它的 hook 機制與 checkpoint.sh/巡查會形成雙軌。
- **不抄 TDD 全套紅綠循環為硬規**：我們的主力產出是 SEO 內容/報價/照片管線/治理腳本，
  純程式碼比例低；test receipt（測了+留證據）比紅綠循環更貼合現況。
- **不抄它的 2-5 分鐘步驟粒度**：我們任務多為跨系統操作（WP/GAS/Sheets/Telegram），
  粒度由 task card 的 Progress Log 節奏管理即可。

## 4. 落地順序（併入科技樹 R1/R2，不另開軌道）

| 順序 | 項目 | 動作 | 工作量 |
|---|---|---|---|
| 1 | G3 觸發紀律 | AGENT_STARTUP_PROTOCOL 加 `Skills loaded` 必填欄 + go-prompt 前言 1% 規則 | ~30 min |
| 2 | G2 禁語表 | company-values 補五步+禁語；巡查 grep 規則 | ~1 h |
| 3 | G1 技能 TDD | pitfall/skill 模板加 `封坑驗證` 欄；generate-skill.sh 加 RED 情境 | ~2 h |
| 4 | G4 description | 路由表說明欄漸進改寫 | 漸進 |
| 5 | 五 rationalization 欄 | pitfall 模板選填欄 | 順手 |

執行前提：G1 的完整版（壓力測試跑真 session）等 Evolution Channel 接正式 DB 後再上，
先做欄位版——**帳本先、機制跟上**。
