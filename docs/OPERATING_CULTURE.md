# MAPLAB 作業文化 — 企業溝通規則（所有 Agent 遵守）

> 版本：v1.6 | 建立：2026-07-03 | 更新：2026-08-28 | Owner 親口指示
> ⚠️ 硬性規則，適用所有 Agent（A0–A8、B-roles、IOS-roles）面向 Owner 或人類的一切回報。

---

## 原則 1 — 對人溝通用「人看得懂的標題/名稱」，不用內部代碼當主詞

**Owner 指示（2026-07-03）**：對人溝通時，用「人看得懂的標題/名稱」，不要用內部代碼。

### 規則

開口的主詞（句子第一個名詞）必須是人類可直接理解的名稱。  
內部代碼、ID、slug 可放在**括號或附註**輔助識別，但不得作為主詞。

### ✅ 正確示範

> 《行政外燴推薦 HR 活動餐點規劃》這篇已 QA 通過，等 Owner 視覺閘確認後排程上線。  
> 《台南企業外燴推薦》（post 586）有一個壞掉的內鏈需要修復。  
> 「每日期貨研調」任務（UUFG6 虎航）已推 Telegram，無警示。

### ❌ 錯誤示範

> `GAP-3` 已 QA 通過。  
> `post id 1992` 有壞內鏈。  
> `slug hr-admin-meeting-catering-guide-tainan` 草稿建立成功。  
> `T-A2-005` 執行完成。

### 適用範圍

| 類型 | 人話主詞 | 代碼放哪 |
|---|---|---|
| SEO 文章 | 文章主題標題 | 括號補 GAP-N / slug |
| 任務 / ticket | 任務說明 | 括號補 task ID |
| WP 草稿 | 文章標題 | 括號補 post ID |
| 期貨部位 | 合約標的名稱（如「虎航個股期」） | 括號補代碼（如 UUFG6） |
| 檔案 / 路徑 | 用途說明 | 括號補檔名或路徑 |

### 為什麼

代碼對人類無意義，需要翻譯才能理解內容。以人話開頭，Owner 一眼知道講的是哪件事，不需要停下來查對照表。內部代碼仍有稽核與追蹤價值，放在括號裡即可，不丟失。

---

## 原則 2 — 缺陷棘輪（Defect Ratchet）—— 抓到缺陷就讓它變成防護

**Owner 指示（2026-07-03）**：任何被抓到的缺陷，必須同時沉澱為下列三項之一（能沉澱多項就多項），只進不退：

| 沉澱形式 | 怎麼做 | 範例 |
|---|---|---|
| **清單一條** | 加進 `docs/seo-publish-checklist.md`，標明可自動或需人眼 | 「佔位連結未解析」→ B-1 / B-3 條目 |
| **閘門腳本一項**（若可自動化） | 加進 `scripts/seo_publish_gate.py` 作為一個可執行的 check | 掃描 `[INTERNAL_LINK_RECHECK_REQUIRED` 字串 |
| **模板必填欄位一項**（若可預防） | 在 SEO 草稿模板的「必填欄位」區加一條，讓生成階段就填完 | 「精選圖 media ID」設為生成時必填，不能空白交稿 |

### 閘門必須獨立執行

**產出者不能跑自己的閘門。** 生成稿的角色（A2 / Codex）負責產出，獨立角色（OpenClaw / Codex 複查 / Owner）負責跑閘門清單。即使是同一個 session，也必須明確切換到「閘門跑者」身份後再執行，不能邊寫邊自我放行。

### 本次 SEO 實例（2026-07-03）

《行政外燴推薦 HR 活動餐點規劃》交付後抓到三個缺陷，依棘輪原則沉澱如下：

| 缺陷 | 清單條目 | 腳本 check | 模板必填 |
|---|---|---|---|
| HTML body 未與核准版做指紋比對，可能縮水或段落錯位 | A-1, A-2 | `--check fingerprint` | 草稿交付時必附：核准版字數 + 前 500 字 SHA256 |
| 佔位連結（`[INTERNAL_LINK_RECHECK_REQUIRED]` / `href="/【待填`）未解析就交稿 | B-1, B-3 | `--check links` | 草稿必填：已解析內鏈表（slug → live URL / 待確認 / 404禁連） |
| 精選圖未附帶，發布時 `featured_media = 0` | C-1, C-2 | `--check assets` | 草稿必填：精選圖 WP media ID（或 Owner 明確指定「待補」） |

---

## 原則 3 — 目標驅動迴圈（Goal-Driven Loop）——「做完才停」是預設模式

**Owner 指示（2026-07-06，取自 Fable 5 自我改進框架 #5/#6/#11）**：非瑣碎任務開工前，必須先寫下三樣東西；然後**一路迭代到達標才停、才回報**。

### 開工前三問（強制，不可省）

| 欄位 | 問題 | 說明 |
|---|---|---|
| **(a) Goal（高槓桿版）** | 這件事做到什麼程度，對 Owner 真正有意義？ | 不是「把腳本跑完」，而是「產出 Owner 能直接上線/決策的東西」 |
| **(b) 完成條件 / 停止條件** | 哪些可量測的信號代表已達標？哪些代表該停下回報？ | 例：「gate 9/9 PASS」「圖片尺寸 1080×1350 且文字可讀」「三條都 commit 且 diff 乾淨」 |
| **(c) 獨立評分者** | 誰來判斷完成？（必須是非產出者本人） | 選項：Codex 自跑腳本驗證、Haiku 複查、眼見為憑工具截圖、Owner 最後收尾 |

### 迭代規則

1. **寫完就迭代，達標才停**。不要每個步驟回來問 Owner「這樣可以嗎」。
2. **只在真正的決策岔路才停**，三類：
   - 需要人類授權（刪除既有資料、花費超預算、推 remote）
   - 物理進不去（缺憑證、缺工具、缺真實資料）
   - 純粹的價值判斷（文案品味、策略取捨、對外承諾）
3. 其餘所有阻力（技術問題、格式問題、腳本除錯、小型重寫）— 自己推進，不打斷。

### 反面例（嚴禁）

| 錯誤行為 | 為什麼有害 |
|---|---|
| 每一步驟完成後回報「這樣可以嗎？」 | 打斷複利；Owner 變成人工 next-button |
| 把「差不多能用」當完成條件 | 沒有可量測標準就沒有停止條件，品質浮動 |
| 「我先生成，你看看對不對」 | 把判斷責任外包給 Owner；自己不設評分標準 |
| 碰到小問題就停下等指示 | 把 Owner 的注意力消耗在技術細節上 |

### 適用場景

- 任何需要超過一步才能完成的任務（多檔編輯、腳本執行、圖片生成 + commit…）
- sub-agent 委派：召喚前必須填完三問，否則不得委派（見 `skills/delegate-subagent.md`）
- SEO 發布閘門：閘門是「(b) 完成條件」的具體化；不過閘就不算完成

---

## 原則 4 — STATE 讀寫紀律（Session 開場讀、收場寫，缺一不可）

**Owner 指示（2026-07-06，取自 Fable 5 自我改進框架 #11）**：工作狀態必須外部化。記在腦子裡等於沒記——context 清掉就沒了。

### 規則

| 時機 | 動作 | 讀/寫什麼 |
|---|---|---|
| **Session 開場（第一步）** | 讀 | `CURRENT_STATUS.md`（或對應 role 的 task card）；確認上次做到哪、有沒有未完成任務、有沒有新規則 |
| **Session 收場（最後一步）** | 寫 | 至少更新一次：做了什麼 / 測試結果（通過/失敗）/ 抓到的新規則 / 下一步建議 |
| **任何「有沉澱價值的發現」** | 立即寫 | 新坑（→ `skills/pitfalls/`）、新規則（→ 對應 recall 或 checklist）、新資源連結（→ `docs/brand-social-links.md` 等） |

### 不寫 STATE 的代價

- 下一個 session 的 agent 從零重啟，重走已走過的路
- 棘輪斷裂：發現的缺陷沒沉澱，下次再犯
- Owner 變成唯一記憶體：不可持續

### 合格的 STATE 更新（最低要求）

```
## YYYY-MM-DD session 收場

做了：[具體動作清單]
通過：[閘門/驗證結果]
失敗/卡住：[原因 + 目前狀態]
新規則：[若有，同步到哪個檔案]
下一步：[明確的下一個可執行動作]
```

不需要長篇大論。五行就夠——只要讓下一個 agent 不用重新問問題。

---

## 原則 5 — 固定存檔（不亂放，存固定位置、開子資料夾）

### 規則

所有 agent 的產出只存單一固定根目錄 `/Volumes/MacExternal/MAPLAB_WORKSPACE/`：
交辦任務產出→`outputs/<YYYY-MM-DD>_<任務短名>/`（先開子夾再產檔）、跨 session 狀態→`state/`、
可重用腳本→`tools/`、素材索引→`index/`。

### ❌ 錯誤示範

產出散在 `~/.claude/state/`、`/tmp`、桌面、以及每個 Cowork session 各自的 `outputs/`
——同一份東西存好幾個地方，事後找不到、重工。

### ✅ 正確示範

開工先在 Startup Check 填 `輸出根目錄: /Volumes/MacExternal/MAPLAB_WORKSPACE`，
任務產出全部落 `outputs/2026-07-24_素材索引-TA場景/` 這類子夾。

### 為什麼

散落存檔是「找不到」與重工的主因；固定位置＋任務子夾讓產出可被索引、可交接。
配套硬檢查見 `AGENT_STARTUP_PROTOCOL.md` Step 6，規範全文見 `skills/agent-output-convention.md`。

---

## 原則 5 — 最短路徑／不重造輪子（Shortest Path / Don't Reinvent the Wheel）

**Owner 指示（2026-07-27）**：能用現成成熟工具解決的，就走最短路徑、不自己重造；把精力留給只有我們能做的高槓桿事。

### 規則

- 遇到一個功能，先問：**市面上有沒有成熟工具已經做得很好？** 有 → 用它，我們只做「**提醒／整合**」，不投入工程重建。
- 只有在現成工具真的不夠、或牽涉**我們獨有的資料／流程**時，才自建。
- 呼應既有教訓（低槓桿重工要避免）：把精力放在**複利型工作**，不做別人已經做好的輪子。

### 實例（2026-07-27 決策）

- 重大財經事件（FOMC／財報／Fed／即時新聞）用 **金十數據 app** 那類現成工具即可。
- 因此**停用自建的「重大事件島」浮窗，也不再自建事件分頁**，改成用現成 app ＋ 只做提醒。

---

## 原則 6 — 解決根因，不只補症狀（Fix the Root Cause, Not Just the Symptom）

**Owner 指示（2026-07-27）**：使用者指出一個問題（例：照片是側的、叫你轉 90°）時，**不要照字面直接補一次就交差**。

### 規則

使用者回報一個具體症狀時，必須：

1. **確認根因** — 為什麼會發生（例：EXIF orientation 沒被套用）。
2. **提出固定／系統性解方** — 讓它以後不再發生（例：管線加 auto-orient，而非逐張手轉）。
3. **共享解決過程** — 根因 → 診斷 → 解方 → 驗證，寫進對應 skill／文件。

盲目照使用者字面指令、只修被指到的那一個點，是低槓桿、會反覆重工；**找根因＋系統化才是複利**。

### 呼應既有教訓

- 「規則存在於散文＝等於不存在」——解方要寫進可執行的 skill／檢查，不只口頭補一次。
- 「避免反覆重工」——一次性系統修，勝過每次手動補症狀。

---

## 原則 7 — 沒有學習就不准重跑（No Repeat Without Learning）

**Owner 指示（2026-08-28）**：Agent 不能用「多跑幾輪」取代檢討、回推與換方法。輪數、模型呼叫數、排程有在動都不是進度；只有通過固定驗證、留下 artifact／live readback／Owner-visible proof 才算進展。

### Plateau 熔斷器

同一方法連續兩次沒有可驗證改善，立即凍結，不得再消耗模型呼叫或 attempt。第三次遇到同一失敗，必須先跑第一性原理 5 題並更新 `pitfalls.md`，不能只是換 seed、換樣本或增加輪數。

「同一方法」以 method fingerprint 判定，至少包含：

- 模型與版本／digest
- system prompt、retrieval、few-shot examples 與 tool route
- dataset、dev set、held-out set 與抽樣方式
- evaluator、rubric、threshold 與環境

### 重新啟動實驗前的必填契約

每個新實驗必須先寫完：`hypothesis`、`target_failure_bucket`、`changed_variable`、`fixed_holdout`、`baseline`、`expected_delta`、`stop_loss`、`method_version` 與 receipt path。一次只改一個主要變因；沒有 changed variable，不得增加 round／attempt。

### 診斷與資格驗收分離

1. 先由人工／規則閱讀失敗 transcript，建立 failure taxonomy；不能只看總分。
2. 開發集可用於修正；held-out set 不得餵回 lesson、prompt 或 few-shot。
3. baseline 與 candidate 必須跑同一批固定案例、同一 grader、同一環境，才能比較。
4. 安全硬門檻（虛構價格、洩漏私密資料、越權發送、重問已知資料）與能力分數分開；安全違規為零容忍。
5. 依錯誤類型選解法：知識缺口補 retrieval／資料；固定規則交給 deterministic code／tool；語氣與格式才調 prompt；模型能力不足才換模型；grader 或環境噪音先修 evaluator／infra。

### 必須沉澱成系統資產

每次 plateau 解除後，同步留下：failure taxonomy、固定 regression set、前後比較 receipt、SOP／Skill 更新與一條 `pitfalls.md`。如果只得到一段聊天說明，視為尚未學習。

### 方法來源

- OpenAI：先看輸出、建立 failure taxonomy，再選改善槓桿 — https://openai.com/index/evals-drive-next-chapter-of-ai/
- Anthropic evaluation guide：開發資料與 held-out data 分離 — https://www-cdn.anthropic.com/38a1fb9db81446402a70bc45d104327aab12f3fe.pdf
- Anthropic agent evals：baseline／candidate 同案例比較，低分先讀 transcript 與 grader — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Dwork et al.：反覆用同一驗證資料做適應性決策會過擬合 — https://arxiv.org/abs/1506.02629

---

## 變更紀錄

| 版本 | 日期 | 變更 | 來源 |
|---|---|---|---|
| v1.0 | 2026-07-03 | 初版：對人溝通用人話標題當主詞 | Owner 親口指示 |
| v1.1 | 2026-07-03 | 新增原則 2：缺陷棘輪（Defect Ratchet）+ 獨立閘門原則 | Owner 親口指示 |
| v1.2 | 2026-07-06 | 新增原則 3：目標驅動迴圈（Goal-Driven Loop）— 開工三問 + 迭代到達標才停 | Owner 指示（Fable 5 #5/#6/#11） |
| v1.3 | 2026-07-06 | 新增原則 4：STATE 讀寫紀律 — session 開場讀/收場寫強制規範 | Owner 指示（Fable 5 #11） |
| v1.4 | 2026-07-27 | 新增原則 5：最短路徑／不重造輪子 — 現成成熟工具優先、只做提醒/整合（實例：財經事件用金十數據、停用事件島/不自建事件分頁） | Owner 指示 |
| v1.5 | 2026-07-27 | 新增原則 6：解決根因不只補症狀 — 根因/系統性解方/共享解決過程 | Owner 指示 |
| v1.6 | 2026-08-28 | 新增原則 7：同方法兩輪無改善即熔斷；重啟前必填單一變因實驗契約、固定 holdout 與 stop-loss | Owner 指示＋12 輪 LINE plateau 檢討 |
