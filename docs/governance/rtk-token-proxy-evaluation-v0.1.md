# RTK Token Proxy — 評估 v0.1（L1 指令輸出壓縮層）

**建立：2026-05-31 | 作者：B1 | 狀態：已安裝+測試，hook 尚未掛載（等 Owner 指定 agent）**
**配套：`multi-model-orchestration-v0.1.md`（RTK = L1 的「指令輸出壓縮」實作）**

---

## 0. 是什麼

`rtk-ai/rtk`：Rust 寫的 CLI proxy，把常見指令（grep/find/test/build/lint/docker/aws…）
輸出在送進 LLM 前壓縮 60–90%。支援 claude/gemini/codex/antigravity/hermes hook。

## 1. 來源與安全驗證（已做）

- 安裝：Homebrew 官方 formula `rtk` stable 0.42.0（bottled），homepage rtk-ai.app，
  與 GitHub 最新 release v0.42.0 一致。非 curl-to-bash，來源乾淨。Apache-2.0。
- Telemetry：預設 **關**（`consent: never asked / enabled: no`，config `telemetry.enabled=false`）。
  另可加 `export RTK_TELEMETRY_DISABLED=1` 雙保險。
- `tracking.enabled=true` 只是本機 `rtk gain` 分析（不外傳），保留。

## 2. 實測省量（本 repo，2026-05-31）

| 指令 | 原始 | RTK | 省 |
|------|------|-----|----|
| `find . -name "*.md"` | 60,669 字元 | 1,178 字元 | ~98% |
| `rtk gain` 總計（2 指令）| 23.1K token | 5.8K | **74.8%** |

結論：對「掃 repo / 列檔 / 測試 / build」這類冗長輸出極有效，正中 patrol/守夜人痛點。

## 3. 風險規避（已落實配置）

關鍵前提：**RTK hook 只攔截 agent 頂層 Bash tool 指令**；patrol.sh / checkpoint.sh /
verify-commit-on-main.sh 內部的 git 呼叫在腳本內執行，不被攔截 → 天生安全。

額外鎖死：`config.toml` `[hooks] exclude_commands = ["git"]` —— git 完全走原生，
保證治理腳本與「是否上雲」判斷永遠看到原始輸出。config 路徑：
`~/Library/Application Support/rtk/config.toml`。

## 4. 白名單（建議只壓這些）

grep / rg / find / ls / tree / rtk read(cat-head-tail) / 測試 runner / build / lint /
docker ps / log 檢視。git 全排除（見上）。投資/SEO 正式產出走 L3 原生,不壓。

## 5. 回滾

`rtk init -g --uninstall`（移 hook）；`brew uninstall rtk`（移 binary）。單一 binary，零殘留。

## 6. 尚未做（等 Owner 決策）

- **agent hook 掛載**：`rtk init -g --agent <x>`。**A6 live codex bot 屬 A6 客戶流程域,
  B1 不擅自掛**。需 Owner 指定要掛哪個 agent（建議先非生產或 Owner 自己的 Claude Code/Codex）。
- 掛載後驗收:裝前/裝後各跑 patrol.sh + verify-commit-on-main.sh,輸出 diff 必須一致。
