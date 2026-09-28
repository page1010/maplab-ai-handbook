# HERMES 讀取地圖 — 企業文化與資料指路卡

來源:Owner 訊息 6088(2026-09-24T17:19:53)
原話:去把讀資料的功能開給hermes他不懂企業文化 你們一直阻擋他 那還做什麼事情 股票的程式單避開就好其他企業文化 去哪裡拿資料 指路都幫他指好 不然你沒有事情可以交辦 我額度每週都在不夠你們不把工讀生訓練起來幫忙

維護者:A0 / Fable5 線。修改本檔要同步改 `SYSTEM_DIRECTORY_INDEX.md` 的對應列。

---

## 0. 先講清楚:hermes 卡住的不是權限

2026-09-24 實查結果(全部在本機檔案系統上核對過):

- 全 repo 搜過 `allow_paths` / `allowed_paths` / `ALLOWLIST` / `allowed_read` / `read_allow` / `path_allow`,**沒有任何一條檔案讀取白名單把 hermes 擋在外面**。
- 唯一叫 allowlist 的東西是 `config/deerflow/hermes-public-research*.yaml` 裡的 `deerflow.guardrails.builtin:AllowlistProvider`,那是**對外網路研究的網域範圍**,跟讀本機檔案無關。
- `SYSTEM_DIRECTORY_INDEX.md` 共 625 行,提到 Hermes 的只有 3 行(第 6 行的適用名單、第 125 行指向性地圖、第 132 行 NotebookLM 路由)。

所以真正的狀況是:hermes 一直被列在「適用對象」裡,卻從來沒有人寫過一張 hermes 尺寸的路線卡。625 行的全角色索引不是指路,是地圖集。這張檔就是那張路線卡。

---

## 1. 冷啟動讀順序(企業文化)

照順序讀。行數列出來是為了讓 hermes 自己估 context 預算,不要一次全吞。

| 順序 | 檔案 | 行數 | 讀它是為了回答什麼 |
|---|---|---|---|
| 1 | `AGENT_CORE.md` | 14 | 這間公司在幹什麼、誰是唯一的 user |
| 2 | `AGENTS.md` | 17 | 有哪些席位、自己是哪一個 |
| 3 | `docs/company-values.md` | 261 | 企業文化本體。價值觀、對客人的態度、什麼不做 |
| 4 | `CULTURE_DECISION_LOGIC.md` | 170 | 遇到沒寫過的情況怎麼自己判斷,不要等人 |
| 5 | `NAMING_GLOSSARY.md` | 92 | 稱謂 SSOT。講錯名字會找錯人、報錯修 |
| 6 | `SOP_SEE_BEFORE_YOU_SAY.md` | 87 | 查到不等於看到。沒看到就標出來,不准腦補 |
| 7 | `AGENT_RULES.md` | 1316 | 全域行為準則。太長,先讀目錄再跳讀相關章節 |
| 8 | `AGENT_STARTUP_PROTOCOL.md` | 291 | 每次開工的固定動作 |
| 9 | `pitfalls.md` | 941 | 別人踩過的坑。開工前用關鍵字搜自己要做的那一塊 |
| 10 | `decisions.md` | 183 | 已經定案的抉擇,含被否決的方案與理由 |
| 11 | `A0_USER_PREFERENCES.md` | 49 | Owner 的偏好與說話方式 |
| 12 | `docs/fable5-direction-and-guidance.md` | 201 | 系統往哪走 |

以上十二檔合計 3622 行,全部在 `/Users/pagemacmini/maplab-ai-handbook/` 根目錄或 `docs/`,2026-09-24 逐檔核對存在(看到等級)。

最短路徑版:時間只夠讀三檔,就讀 1、3、6。

---

## 2. 資料在哪(去哪裡拿)

取像等級沿用 `SOP_SEE_BEFORE_YOU_SAY.md`:**看到** = 本機實際開過檔或看過畫面;**查到** = 從索引或紀錄查到路徑但這次沒實際開。引用查到等級的東西,每一句推論都要標。

| 要什麼 | 位置 | 等級 | 怎麼讀 |
|---|---|---|---|
| 企業文化 | `maplab-ai-handbook/docs/company-values.md` | 看到 | 直接讀 |
| 全域準則 | `maplab-ai-handbook/AGENT_RULES.md` | 看到 | 先讀目錄再跳讀 |
| 任務卡 | `maplab-ai-handbook/handoff/tasks/` | 看到 | 一張卡一檔 |
| 任務索引 | `maplab-ai-handbook/workbook/task_index.json` | 查到 | 先讀索引再挑卡,不要掃整個目錄 |
| 當前狀態 | `maplab-ai-handbook/CURRENT_STATUS.md`(461 行) | 看到 | 多個 agent 同時在寫,讀到的是當下快照 |
| 踩坑紀錄 | `maplab-ai-handbook/pitfalls.md` + `skills/experience-log.md`(349 行) | 看到 | 用關鍵字搜,不要通讀 |
| 決策紀錄 | `maplab-ai-handbook/decisions.md` | 看到 | 含被否決方案的理由 |
| 對 Owner 的說話方式 | `maplab-ai-handbook/skills/owner-telegram-conversation-sop.md`(72 行) | 看到 | 產草稿前必讀 |
| 全域資料位置索引 | `maplab-ai-handbook/SYSTEM_DIRECTORY_INDEX.md`(625 行) | 看到 | 本表查不到的東西去那裡查 |
| 指向性地圖 | `maplab-ai-handbook/config/system-map/maplab-directional-map.json` | 查到 | 適用名單本來就含 Hermes |
| 地端模型與 NotebookLM 路由 | `maplab-ai-handbook/config/notebooklm/maplab-project-brain-router.json` | 查到 | 適用名單本來就含 Hermes |
| 每日續接紀錄 | `claude-daily-operations/state/FABLE5_HANDOFF.md` | 看到 | 最新在最上面 |
| Owner 原話逐字稿 | `claude-daily-operations/state/a0_inbox.jsonl` | 看到 | 一行一則,含 ts。摘要不算,要引用就引原話 |
| 報價案卷 | `~/.maplab/quote_intake/` | 查到 | 2026-09-24 未實際列出目錄。客資內容不進 repo、不進 Telegram |
| gold 清洗輸出 | `~/.maplab/gold_replies/` | 查到 | 同上。repo 只放筆數、路徑、時間 |
| Credential 說明 | `maplab-ai-handbook/skills/credentials/` | 查到 | **只有路徑與 scope 的說明,沒有也不准有 secret 值** |

`~/.maplab/*` 那三列標查到是誠實的:這次要列目錄被工作目錄限制擋下,失敗原文是 `outside the allowed working directories`。hermes 若讀得到就自己升級成看到並回寫本表。

---

## 3. 避開清單

Owner 6088 只畫了一條紅線:**股票的程式單避開就好**。落地成具體範圍:

- 不讀、不改、不執行 `investment-os/` 底下的下單與交易執行路徑。
- 不下單、不改倉位、不動錢、不碰真倉。
- 交易紀錄的**唯讀查詢**(例如 ledger 裡的損益欄位)不在禁止範圍,但產出只能是報表,不能是指令。

以下四類不在 6088 的授權範圍內,維持全面禁止,跟 hermes 的等級無關:

1. **金鑰 / token / cookie / 帳密 / 授權碼** — 不讀、不印、不入版控、不外傳。`secrets/` 目錄與 `.env` 檔一律不開,需要環境變數只列**名稱**。
2. **他人客戶資料** — 未來 B2B 客戶的資料需要該客戶自己的同意與隔離,MAPLAB 客資絕不混入他客。
3. **兒童照片與私有客照** — 等 Owner 明確授權才談外送。
4. **瀏覽器網址與截圖** — History 與分頁網址夾帶權杖,任何印出網址的動作都要砍掉 `?` 與 `#` 之後;截圖只存 `~/.maplab/screenshots/`,不入 repo、不傳 Telegram。

另外,hermes 的 fail-closed 四類照舊標「需人工」:不報價、不選菜、不承諾檔期、不判定飲食安全。其中「不報價」指的是**不准憑猜測生出數字**,程式從有 source 的價目表算出來的內部試算不在此列。

---

## 4. 卡住怎麼辦

不准靜默推論。照三段回報:

1. **失敗原文照貼**,一個字都不要改寫。
2. **說出卡在哪一層** — 模型層 / 角色層 / 席位層 / 程式層 / 別家 app,先分層再報修。
3. **給出唯一一個解鎖動作** — 要誰做什麼、一句話能不能解。

讀不到某個檔不等於那個檔不存在,也不等於可以推論內容。讀不到就講讀不到。

要付錢的事情才上呈 Owner。帳密、授權碼、cookie 這三樣不是權限問題,是做不到,一句話帶過不要說教。其餘自家模組的事自己修、自己重啟、自己驗。

---

## 5. 今天就能接的工作(唯讀,不碰交易)

Owner 6088 的後半句是重點:額度每週都不夠,是因為沒把讀東西這種吃 token 的活外包出去。以下五件都是純讀加產出文字,沒有不可逆動作,可以立刻派:

1. **讀完 `pitfalls.md` 941 行,產出分類索引** — 按「哪一層的坑」分組,每組列行號。之後任何 agent 開工前查坑只要讀索引,不用通讀 941 行。
2. **讀完 `AGENT_RULES.md` 1316 行,產出可搜尋的規則目錄** — 每條規則一行:規則、出處 msg id、適用對象。現在沒有目錄,所以每次都得全讀。
3. **核對 `workbook/task_index.json` 與 `handoff/tasks/` 實際檔案** — 列出索引有卡沒有、或卡有索引沒有的差集。這是 #79 的延伸,純比對。
4. **讀 `decisions.md` 183 行,列出「已定案但程式裡還沒寫死」的條目** — 對照 `AGENT_RULES.md`,找出只存在於紀錄、沒落到程式的決策。
5. **把本表 `~/.maplab/*` 三列從查到升級成看到** — 實際列目錄、回報檔數與最新時間,不印任何客資內容。

每件的交付都是一份 md 加一句「哪些沒讀到、為什麼」。做完回寫本檔第 5 節,把完成的劃掉、補上新的。

---

## 6. 升級門檻(不改)

`AGENT_RULES.md` §五 的 hermes 三階段養成照舊生效:

- S1 受理 — 已具備。
- S2 自算 — 程式已具備,**端到端未驗過**(`~/.maplab/quote_intake/` 至今沒有收到過一筆真實案件)。
- S3 管實作 — 未開始。**S2 未驗過不得進 S3。**

本檔開放的是**讀取與產出文字**,不是升級。S3 開放後也只能派可逆工作(改檔、產草稿、跑測試),不可逆動作永遠回到 Owner。
