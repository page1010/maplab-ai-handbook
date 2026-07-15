# T-A1-RTK-001: RTK Token Proxy 掛載與選擇性上線

## 接續狀態
- **狀態**: 🟢 已上線
- **最後活動**: 2026-05-31
- **接續點**: Codex hook 已掛（`~/.codex/RTK.md`）、驗收通過（patrol diff 一致）、git 排除生效。任務完成，無後續。
- **阻塞**: 無

- **負責**: A1（落地）+ Owner（指定 agent / 批准 hook）
- **建立**: 2026-05-31（B1 評估 + 安裝完成）
- **狀態**: 🟢 已上線（Codex hook 已掛、裝前/裝後 patrol diff 驗收通過、git 排除生效）
- **依據**: `docs/governance/rtk-token-proxy-evaluation-v0.1.md`

## 已完成（B1）
- brew 裝 rtk 0.42.0；telemetry 確認關閉。
- `config.toml` `exclude_commands=["git"]` —— 保護治理腳本與上雲判斷。
- 實測：find -98%、整體 74.8% token 省量。

## 已完成（hook 上線）
- Owner 指定掛 **Codex**（額度較多較穩）。`rtk init -g --codex`：建 `~/.codex/RTK.md` + AGENTS.md 加一行 `@RTK.md` 參考（**非強制改寫 hook，是指令引導**，比 bash hook 更溫和）。AGENTS.md 已備份 `AGENTS.md.bak-pre-rtk-*`。
- **驗收通過**：裝前/裝後 patrol 輸出僅時間戳/OAuth 刷新時間不同，巡查邏輯一致；verify-commit-on-main 正常；git 確認走原生。

## 待觀察
- 跑 1 週後看 `rtk gain` 24h/30d，用數據決定是否擴張白名單；弱指令（<30% 省）不加。
- Codex session 是否確實採用 rtk（AGENTS.md 引導非強制，需實際觀察）。

## 禁止 / 邊界
- 不在未經 A6+Owner 確認下掛 A6 live codex bot。
- 不解除 git 排除,除非先過 §3 diff 驗收。
- 不開 telemetry。
