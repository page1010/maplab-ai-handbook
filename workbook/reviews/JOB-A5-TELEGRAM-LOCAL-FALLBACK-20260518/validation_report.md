# A5 Telegram Local Fallback Validation — 2026-05-18

## Startup Check

- Role: MAPLAB A5 報價與提案引擎部，由 A6 Telegram bot 入口承接。
- Environment: canonical repo `/Users/pagemacmini/maplab-ai-handbook`; stale download copy `/Users/pagemacmini/Downloads/maplab-ai-handbook-main` not used for writeback.
- Read first: `CURRENT_STATUS.md`, `AGENT_RULES.md`, `AGENT_STARTUP_PROTOCOL.md`, `pitfalls.md`, A5/A6 task cards, `skills/task-progress-guide.md`.
- Scope: Telegram 內對話可以呼叫 A5 報價草稿；雲端 A5/Claude path 失敗時，改走 local Ollama/OpenClaw fallback。
- Safety: local fallback does not write Google Sheets, does not create official quote URLs, and marks output as internal draft.

## Implementation Summary

- Added `bot_a6/a5_quote_engine.py` for A5 prompt construction, OpenClaw/Ollama execution, deterministic parsing, budget correction, and output sanitizing.
- Updated `bot_a6/bot_a6.py` quote mode to try cloud A5 first, then local fallback; added `/localquote` for forced local tests.
- Added `REVIEWS_DIR` to `tools/ai_workbook/paths.py`, restoring OpenClaw review bundle creation.
- Added `scripts/simulate_a5_quote_requests.py` as a non-Telegram local simulation helper, but Telegram Web tests below are the acceptance path.

## Telegram Test Matrix

| # | Telegram input | Result | Evidence |
|---|---|---|---|
| 1 | `/localquote 報價 陳小姐 週歲派對 30人 預算2萬 台南東區 室內 甜點多一點 不吃牛` | PASS with direct local fallback before `REVIEWS_DIR` fix; no Sheet write. | Telegram visible at 22:38; `job_id=A5-QUOTE-20260518-223609` |
| 2 | `/localquote 報價 台南科技公司 開幕茶會 80人 預算5萬 ...` | FOUND ISSUE: model returned `NT$500,000`; fixed by deterministic correction. | `workbook/reviews/A5-QUOTE-20260518-224914` |
| 3 | `/localquote 重測 報價 林先生 婚禮 after party 60人 預算4萬 嘉義市區 鹹食多一點 不要海鮮` | PASS: Telegram showed `NT$40,000` correction and OpenClaw bundle. | `workbook/reviews/A5-QUOTE-20260518-225632` |
| 4 | `/localquote 報價 王小姐 性別揭曉派對 24人 預算15000 台南安平 希望粉藍色甜點 不要酒` | PASS: Telegram showed `NT$15,000` correction and no alcohol suggestion. | `workbook/reviews/A5-QUOTE-20260518-225923` |
| 5 | `/localquote 報價 品牌發表會 120人 預算6萬 高雄展覽館 企業版 需要茶點 不確定樓層搬運` | PASS: Telegram showed `NT$60,000`; also exposed ANSI `[K` noise, then sanitized in engine. | `workbook/reviews/A5-QUOTE-20260518-230511` |
| 6 | `/localquote 重測 報價 台南科技公司 開幕茶會 80人 預算5萬 台南永康 需要飲品和質感鹹食` | PASS: patched runtime showed `NT$50,000`; sanitized draft written back. | `workbook/reviews/A5-QUOTE-20260518-231132` |
| 7 | `/localquote 報價 launchd修正後測試 8人 預算8000 台南` | PASS with direct API fallback: launchd returned `NT$8,000`; exposed missing `PATH` for `ollama` CLI. | `workbook/reviews/A5-QUOTE-20260518-232422` task_request only |
| 8 | `/localquote 報價 launchd PATH 測試 6人 預算6000 台南` | PASS: launchd used `engine=ollama model=llama3.1:latest`, returned `NT$6,000`, full review bundle created. | `workbook/reviews/A5-QUOTE-20260518-232655` |

## Runtime Verification

- `python3 -m py_compile bot_a6/a5_quote_engine.py bot_a6/bot_a6.py tools/ai_workbook/paths.py scripts/simulate_a5_quote_requests.py` passed.
- Prompt smoke check: A5 Telegram profile prompt length about 6.2k chars.
- Telegram Web was used as the send path; final `/ping` after launchd bootstrap returned `A6 pong` at 23:14.
- LaunchAgent loaded: `gui/501/com.maplab.a6bot`; `/ping` at 23:14 confirmed the long-running service.
- LaunchAgent default runtime initially used a slower local path; the repo plist now pins `PATH`, `A5_LOCAL_ENGINE=ollama`, `A5_LOCAL_MODEL=llama3.1:latest`, `A5_LOCAL_NUM_PREDICT=650`, and `OPENCLAW_AGENT_TIMEOUT_SECONDS=45`.
- After setting model/engine, launchd `/localquote 報價 launchd修正後測試 8人 預算8000 台南` returned through Telegram with `NT$8,000`; before PATH was added it used direct Ollama API fallback because `ollama` CLI was not visible to launchd.
- After adding PATH, launchd `/localquote 報價 launchd PATH 測試 6人 預算6000 台南` returned through Telegram with `engine=ollama model=llama3.1:latest` and a complete review bundle.

## Findings

- Local Ollama is usable as a quota-fallback draft maker, but it must be guarded by deterministic parsing for Chinese money units.
- The local fallback should stay clearly labeled as internal draft only until A5 writes the formal Google Sheet quote.
- OpenClaw bundle creation is useful for review evidence; direct Ollama without bundle is only acceptable as emergency fallback.
- Telegram command tests must be real slash-command sends, not only local script simulation.
- Current output quality is "usable draft", not final client quote: wording, item selection, and margin assumptions still need A5/Owner review.
- Long-running service config matters: foreground tests were fast with `llama3.1:latest`; launchd must pin the same non-secret local runtime settings and CLI `PATH` or Telegram may sit on heartbeat / lose OpenClaw bundles.

## Resume Prompt

```text
我是接手 A5/A6 Telegram 報價 fallback 的下一位 agent。
先讀 CURRENT_STATUS.md、pitfalls.md、AGENT_RULES.md、AGENT_STARTUP_PROTOCOL.md、skills/task-progress-guide.md。
本輪已在 canonical repo /Users/pagemacmini/maplab-ai-handbook 完成：
1. bot_a6/a5_quote_engine.py 新增 A5 local quote engine。
2. bot_a6/bot_a6.py 新增雲端 A5 -> local Ollama/OpenClaw fallback 與 /localquote。
3. tools/ai_workbook/paths.py 補 REVIEWS_DIR，OpenClawAdapter 可產生 workbook/reviews/A5-QUOTE-* bundle。
4. Telegram Web 已實送 5+ 組 localquote；最後 5萬重測正確顯示 NT$50,000。
5. launchd com.maplab.a6bot 已 bootstrap；/ping at 23:24 回 A6 pong，localquote PATH test at 23:27 回完整 bundle。
下一步：
- 若要正式出報價單，接 Google Sheets/GAS write path，不要讓 local fallback 直接寫 truth source。
- 若 launchd localquote 變慢，先確認 ~/Library/LaunchAgents/com.maplab.a6bot.plist 是否同步了 repo plist 的 A5_LOCAL_* 設定。
- 補強菜單品項選擇與飲食禁忌硬過濾，避免 local model 推錯品項。
- 檢查 launchd stdout/stderr 是否持續穩定；必要時把 A5_LOCAL_MODEL 等環境寫進受保護 runtime config。
- review bundle 原始 output.json 可能仍保留模型 raw ANSI，Telegram-facing draft.md 已 sanitize；若要 commit raw bundle，先 sanitize。
- 不要提交 bot_a6/.env、bot_a6/*.log、conv_history_a6.json 或含 Telegram token 的內容。
```
