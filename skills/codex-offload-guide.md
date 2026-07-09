# Codex / Antigravity 卸載指南

版本：v1.0 | 建立：2026-07-06 | 觸發：任何角色在動筆前，先判斷這份工作是不是能卸載給已付費的 sub-agent（Codex / Antigravity），不要每次都用 Claude 額度。

> 背景：Owner 2026-07-06 原話「gpt最近額度很多誒 他是你的sub agent你都不好好用起來 訓練他」「我指的是codex antigravity我都有付費 允許的話 幫我把telegram上的服務分過去給他們做」。
> Codex、Antigravity（`agy`）不是獨立角色，是可調度的執行層——跟 A6 Telegram 服務的底層模型可插拔設計是同一個原則：**角色與分工不變，只是換掉底層跑的大語言模型**。完整 pluggable backend 設計見 `projects/a6-llm-backend-adapter.md`。

---

## 一、判斷準則：適合 vs 不適合

### 適合卸載（Codex 或 Antigravity 皆可）
- 批量文字生成：SEO 草稿、FAQ 草稿、alt text、產品/案例描述
- 唯讀分析：讀一批資料/log/報表找模式，不需要寫入任何系統
- 翻譯改寫：中英互譯、語氣調整、格式轉換
- 一般對話 / 客服草稿回覆（不牽涉報價運算或 Sheet 寫入時）

### 不適合卸載（留給 Claude Code / A6 本體）
- 任何會寫入 repo（commit/push）、Google Sheets、GAS、WordPress、Google/Meta Ads 後台的操作
- 需要跨系統工具鏈的任務（例如同時要讀 Sheet + 呼叫 GAS + 寫 Drive）
- 牽涉報價成本/毛利計算（A5 核心公式，屬於「寫入」等級的信任，不外包）
- 需要 MCP 工具（Google Sheets/Drive/Ads 等）現場讀寫的任務——**目前**我們沒有把這些 MCP 註冊給 Codex（見第六節，這是設定問題不是架構限制，但註冊前要先過權限審查）
- 任何客戶個資/憑證會經過 prompt 的場景

判斷口訣：**只出一段文字 = 可以卸載；會動到系統狀態 = 留給 Claude/本體角色。**

---

## 二、Codex 呼叫範例

沿用 `bot_a6/bot_a6.py` `_codex_generate_sync()` 已驗證的呼叫方式：

```bash
codex exec --ephemeral -C /Users/pagemacmini/maplab-ai-handbook -s read-only -m gpt-5.1-codex - <<'EOF'
（AGENT_RECALL_PROMPTS.md「## Codex」段落的召回 prompt + 具體任務）
EOF
```

要點：
- `--ephemeral`：不留對話記錄，每次呼叫獨立。
- `-s read-only`：唯讀 sandbox，不能寫檔案——這是目前唯一驗證過對 Codex 有效的權限鎖。
- `-C <repo path>`：限定工作目錄，避免 Codex 誤讀到其他 repo。
- `-o <output file>`：A6 的實作額外把輸出導到暫存檔再讀回，避免 stdout 被其他訊息污染（見 `_codex_generate_sync`）。

## 三、Antigravity（agy）呼叫範例

沿用 `scripts/weekly_eval_compounding.py` `run_agy_quality_review()` 已驗證的呼叫方式：

```bash
agy --print "（AGENT_RECALL_PROMPTS.md「## Antigravity (agy)」段落的召回 prompt + 具體任務）"
```

⚠️ **權限風險（2026-07-06 盤點發現，接生產路徑前必須解決）**：agy 在 `--print --sandbox` 模式下觀察到會**主動執行 shell 指令探測環境**，沒有等同 Codex `-s read-only` 的強制唯讀保證。目前只建議用在「純文字進、純文字出」且不牽涉任何敏感操作的場景（例如 eval 品質複核）。若要接進 A6 Telegram 這種面向客戶的路徑，先做：
1. 讀 `agy help`/`agy plugin` 是否有明確的權限/sandbox 範圍設定
2. 或用 `--add-dir` 限定一個空的 scratch 目錄，避免碰到 repo 真實檔案
3. 拿到官方文件確認 `--sandbox` 到底限制了什麼之前，不要假設它等於「唯讀」

## 四、可切換的底層模型（agy）

`agy models` 目前列出：Gemini 3.5 Flash（Medium/High/Low）、Gemini 3.1 Pro（Low/High）、Claude Sonnet 4.6（Thinking）、Claude Opus 4.6（Thinking）、GPT-OSS 120B（Medium）。用 `--model <name>` 指定。

---

## 五、與 Ollama 的關係

Ollama（`gemma4:latest` 等本地模型）維持「末位冷備援」角色：Codex/Antigravity 都失敗或不可用時才落到 Ollama。原因：
1. Ollama 常駐佔用 RAM 偏高（llama-server 進程實測 ~9-14GB RSS，是 2026-07-06 記憶體警報的主要來源之一）。
2. Codex/Antigravity 是 Owner 已付費、額度充足的雲端資源，本來就該優先用滿，不需要每個任務都佔本機資源跑 Ollama。

完整降載鏈設計（codex → antigravity → ollama）與風險評估見 `projects/a6-llm-backend-adapter.md`；本次僅完成設計文件 + adapter 骨架，尚未接進線上 A6 Telegram 服務。

---

## 六、Codex CLI 版本盤點（2026-07-09，`codex --version`/`--help`/`mcp list`/`features list`/`doctor` 實測）

當時版本：`codex-cli 0.142.0`（`codex doctor` 顯示有 0.143.0 可更新，非急件）。

### 值得利用的新能力

- **`--output-schema <FILE>`**（`codex exec` 選項）：可指定 JSON Schema 限制 Codex 最終回覆格式，跟我們自己 Workflow 工具的 `agent(..., {schema})` 是同一個模式——**未來 offload 任務要結構化資料時，優先用這個，不要再靠 prompt 裡寫「請輸出 JSON」土法煉鋼**。
- **`codex exec resume --last`** / **`codex exec review`**：exec 模式現在支援續接上次 session（省重講一次上下文）與非互動 code review。目前 offload guide 只教一次性 `--ephemeral` 呼叫，**多輪任務可以改用 `resume --last`** 省 token。
- **`-i/--image <FILE>...`**（exec 也支援）：可在非互動呼叫時附圖片——A4/A6 有圖片相關任務要 offload 給 Codex 時可以直接用，不必先轉文字描述。
- **`--oss --local-provider ollama`**（`codex exec`/`codex` 都支援）：Codex CLI **原生內建**「改跑本地 Ollama/LM Studio 模型」的能力（例：`codex exec --oss --local-provider ollama -m qwen2.5:14b ...`）。這跟 `projects/a6-llm-backend-adapter.md` 想自己刻的「可插拔底層模型」目標高度重疊——**未來若要做 codex→ollama 降級鏈，優先評估直接用 Codex 原生 `--oss` 參數，而不是維護我們自己的 adapter 骨架**，除非有原生參數做不到的需求。
- **`--json`**：exec 事件輸出改 JSONL，方便程式解析（例如未來想在 bot_a6 裡結構化讀 Codex 進度，而不是只 tail 一段字串）。

### 更正一項舊假設：Codex 其實「能」接 MCP

第一節「不適合卸載」原本寫「Codex/Antigravity 的 sandbox 呼叫方式不帶 MCP 連線」——**這句不精確**。實測 `codex mcp list` 顯示 Codex CLI 本身有 `codex mcp add/list/get/remove/login/logout` 整組指令，目前已註冊 3 個 MCP server：`node_repl`（瀏覽器操作用）、`github`（`api.githubcopilot.com/mcp`，bearer token 已生效）、`notion`（未登入）。**沒有註冊 Google Sheets/Drive/Ads 之類我們會用到的 MCP**，所以現況下 Codex 仍碰不到我們的報價/Sheet 系統——但這是「沒註冊」的設定問題，不是「架構上做不到」。若未來想讓 Codex 直接讀寫 Google Sheets，路徑是 `codex mcp add`，不是重新設計；但**在把任何寫入型 MCP（Sheets/Drive/Ads）註冊給 Codex 之前，必須先過一輪跟 Section 8 權限治理一樣的審查**，不能因為技術上可行就直接開。

`features list` 額外確認 Codex 目前 stable 啟用中的能力：`browser_use`/`browser_use_external`（會瀏覽網頁）、`computer_use`（電腦操作）、`multi_agent`（多代理）、`plugins`/`plugin_sharing`（外掛生態）、`memories`（experimental，跨 session 記憶）——這些目前都還沒被我們的 offload 流程用到，先記錄，不代表要馬上採用。

## 七、Codex 必須遵守 Superpowers 技能路由（2026-07-09 Owner 指定）

召喚 Codex 執行任何任務前，Codex 端必須先查 `skills/superpowers-guide.md` 的路由表，找到對應技能書並遵守——跟我們自己所有角色開工前查技能索引的義務相同，不因為 Codex 是外部 sub-agent 就豁免。已寫入 `AGENT_RECALL_PROMPTS.md`「## Codex」召回 prompt 的強制條款。
