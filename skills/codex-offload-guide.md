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
- 需要 MCP 工具（Google Sheets/Drive/Ads 等）現場讀寫的任務——Codex/Antigravity 的 sandbox 呼叫方式不帶 MCP 連線
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
