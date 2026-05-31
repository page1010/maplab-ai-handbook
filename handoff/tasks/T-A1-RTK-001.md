# T-A1-RTK-001: RTK Token Proxy 掛載與選擇性上線

- **負責**: A1（落地）+ Owner（指定 agent / 批准 hook）
- **建立**: 2026-05-31（B1 評估 + 安裝完成）
- **狀態**: 🟡 部分完成（binary 已裝、config 已設、實測省 74.8%；hook 待 Owner 指定 agent）
- **依據**: `docs/governance/rtk-token-proxy-evaluation-v0.1.md`

## 已完成（B1）
- brew 裝 rtk 0.42.0；telemetry 確認關閉。
- `config.toml` `exclude_commands=["git"]` —— 保護治理腳本與上雲判斷。
- 實測：find -98%、整體 74.8% token 省量。

## 待做
1. **Owner 決定掛哪個 agent**。⚠️ A6 live codex bot 屬客戶流程，掛載前需 A6 + Owner 確認不影響 Telegram 回覆。
2. A1 執行 `rtk init -g --agent <指定>`。
3. **驗收**：裝前/裝後各跑 `bash scripts/patrol.sh` 與 `bash scripts/verify-commit-on-main.sh`，輸出 diff 必須一致（證明 git 排除生效、治理腳本不受影響）。
4. 跑 1 週後看 `rtk gain` 24h/30d，用數據決定是否擴張白名單；弱指令（<30% 省）不加。

## 禁止 / 邊界
- 不在未經 A6+Owner 確認下掛 A6 live codex bot。
- 不解除 git 排除,除非先過 §3 diff 驗收。
- 不開 telemetry。
