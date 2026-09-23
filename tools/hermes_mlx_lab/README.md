# Hermes MLX training lab

這是 Hermes 的本機、隔離、可重複 QLoRA 實驗底座；不是正式 LINE provider，也不會自動傳送訊息。

## 固定選型

- Apple MLX-LM `0.31.3`
- Python `3.12` arm64
- `mlx-community/Qwen3-4B-Instruct-2507-4bit`
- Base model revision `50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b`
- 訓練資料格式：MLX chat JSONL，使用 `--mask-prompt`

公開基模放在外接碟；外接碟目前未加密，因此不得放 LINE 原文、私有資料集、正式 adapter、訓練 log 或 fused model。私有衍生物固定放在 `/Users/pagemacmini/.maplab/a6-hermes-training/mlx/`，目錄 `0700`、檔案 `0600`。

## 重建與煙霧測試

```zsh
./tools/hermes_mlx_lab/bootstrap.zsh
./tools/hermes_mlx_lab/run_synthetic_smoke.zsh
```

煙霧測試只用 repo 內的合成對話，並在 deny-network sandbox 中執行。它必須真的產生可重新載入的 adapter，才能證明有權重更新；輸出變化不代表業務品質合格。

## 正式訓練前的硬閘

1. 20/20 具名真人 rubric labels 完成。
2. Identity-blind scorer 與真人至少 18/20 exact agreement，安全錯判為 0。
3. DLP 清除姓名、電話、地址、Email、帳號及自由文字中的個資，且有資料使用權 manifest。
4. 先準備 30–50 組 Owner 親改 gold；完全獨立的 holdout 不得進訓練。
5. 未授權價格、政策、檔期或付款承諾必須為 0。
6. 固定盲測勝過 base 後，只能進人工 shadow；不得直接接客戶或 live gateway。

## 已知限制

MLX-LM `0.31.3` 的 server adapter 路徑有 upstream 風險，不能用 server 啟動成功當 adapter 生效證據。此 lab 只用 `mlx_lm.generate --adapter-path` 做 base／adapter 對照；正式接入需另做 adapter-effect regression 與 loopback-only shadow provider。
