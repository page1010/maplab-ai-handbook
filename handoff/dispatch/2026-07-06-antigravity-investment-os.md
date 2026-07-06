# Dispatch Packet — Antigravity 接手 Investment OS 落地(2026-07-06)

> 用法:把下方 code block 整段貼給 Antigravity(或任何接手的工程 agent),工作 repo 是 `page1010/investment-os`。

```
你接手 Investment OS(台股模擬交易系統)的落地驗證,Owner 已於 2026-07-06 核准發案。

背景(2026-07-06 遠端 Claude 已完成):
- 開盤批次管線(generate_open_orders → execute_open_orders → telegram push)已修好:
  shioaji 改為 lazy import、全管線支援 --dry-run、run_open_batch 改絕對路徑。
- 已在無憑證環境驗證閉環:proposed_orders → executed(dry-id)→ order_events + system_logs。
- PR:page1010/investment-os#16(draft,base=codex/investment-os-phase0-scaffold)。

你的工作(依序):
1. Review 並 merge PR #16。
2. 在 Mac mini 的 repo(/Users/pagemacmini/Documents/New project):
   git pull → python3 scripts/init_db.py → python3 scripts/run_open_batch.py --dry-run
   確認和雲端相同的閉環結果。
3. .venv 裝 shioaji,.env 填 SHIOAJI_*(模擬帳號)與 TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID,
   跑 python3 scripts/check_api_usage.py 確認登入與流量額度。
4. 不加 --dry-run 跑一次 run_open_batch.py(simulation 模式),驗收:
   Telegram 收到 run-id 摘要、SQLite 三張表都有真實 simulation 紀錄。
5. 確認 openclaw_tasks/cron.yml 的 preopen_open_batch(平日 08:30 Asia/Taipei)
   在 scheduler 上活著,能自動跑第 4 步。
6. 完成後更新 CURRENT_STATE.md / HANDOFF.md,回報 Owner。

硬規則:
- 只允許 simulation(Shioaji simulation=True),禁止真單;不改風控邊界。
- secrets 只進 .env,不進 git。
- 遵守 docs/API_LIMIT_RULES.md 的呼叫頻率限制。
```
