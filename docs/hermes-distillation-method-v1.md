# Hermes 蒸餾與微調方法 v1

日期：2026-09-01
狀態：`TRAINING_LAB_READY / QUALITY_NOT_PROVEN / LIVE_ROUTE_DISABLED`

## 結論

前五輪不是「訓練得不夠久」，而是沒有更新任何模型權重。它們只是用 random two-shot 範例反覆推論：合計 4/25 通過（16%），各輪為 40% → 0% → 0% → 40% → 0%，第 1 與第 4 輪各有一個未授權價格。完整 12 輪也只有 10/60 通過、最佳 40%、連勝 0。

舊方法已停止。新方法把「產答案」「更新權重」「驗收」「上線」拆開：

1. 固定人工 rubric 與盲測集。
2. 用強模型產生多個去識別候選，但不把候選直接叫 gold。
3. Owner／Mina 選擇或最小改寫後，形成高品質 SFT 資料。
4. 在本機用 QLoRA 真正更新 adapter 權重。
5. Base／adapter 用相同盲測比較；安全硬違規為 0 才能進人工 shadow。
6. SFT 確認有效、且有足夠 chosen／rejected 後，才評估 DPO 或 KTO。

## 這次真正學到什麼

- API 呼叫、回答數與推論輪數都不是模型學會的證據；要看到可保存的權重差異與獨立盲測提升。
- 主要錯誤是回覆過長、重問已知資料、沒有先回答當前問題，以及商業資訊越權，不是缺更多原始聊天紀錄。
- 價格、政策、檔期、付款、工具權限與路由必須由 deterministic authority 控制，不能埋進模型記憶。
- 舊 lexical grader 會把字數與關鍵字混成業務正確；promotion 必須先以真人逐項校正。
- 小量高品質、可追責的修正資料，比再抽數百個未篩選答案更有價值。

## 外部方案比較

| 方案 | 可借用的價值 | 本機決策 |
|---|---|---|
| DeepSeek-R1 distillation | 強教師產資料、過濾後對小模型做 SFT；證明直接對小模型做大量 RL 不一定更好 | 借用資料蒸餾思想；不用 R1-Distill-Qwen-7B 當短客服主模型，也不搬重型 RL |
| Qwen3 distillation | Off-policy teacher response distillation；另有需要 teacher logits 的 on-policy KD | 先做 response distillation；OpenRouter chat API 沒有 logits，不能假稱真正 logits KD |
| Apple MLX-LM | Apple Silicon 原生 LoRA／QLoRA、prompt masking、本地 JSONL | 現在的主線 |
| ModelScope ms-swift | GKD、OPD、SFT、DPO、KTO 等中國開源完整訓練框架 | 留給日後隔離 CUDA 主機，不裝進這台 Mac |
| LLaMA-Factory／TRL | 成熟的 SFT 與偏好訓練工作流 | 作資料格式與未來 GPU benchmark，不作目前本機底座 |
| Unsloth | 快速變動，macOS／MLX 支援正在擴張 | 只作後續釘版本 canary，不與主線混裝 |

參考：

- DeepSeek-R1：<https://github.com/deepseek-ai/DeepSeek-R1>
- Qwen3：<https://github.com/QwenLM/Qwen3>
- MLX-LM：<https://github.com/ml-explore/mlx-lm>
- MLX-LM LoRA：<https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md>
- ModelScope ms-swift：<https://github.com/modelscope/ms-swift>
- LLaMA-Factory：<https://github.com/hiyouga/LlamaFactory>
- TRL：<https://github.com/huggingface/trl>

## 本機選型與已安裝拓撲

- 硬體：Apple M4、24GB unified memory。
- Framework：Python 3.12.13、MLX 0.32.2、MLX-LM 0.31.3。
- Student：`mlx-community/Qwen3-4B-Instruct-2507-4bit`，revision `50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b`。
- 公開基模：`/Volumes/MacExternal/MAPLAB_PUBLIC_MODELS/huggingface/`。
- 私有 runtime／dataset／adapter／receipt：`/Users/pagemacmini/.maplab/a6-hermes-training/mlx/`。
- 正式路由：停用；目前僅 training/eval。

外接碟未加密且 ownership disabled，只能放公開且 hash-pinned 的基模與 cache。真實 LINE、私有衍生資料、正式 adapter、log 與 fused model 一律留在 owner-only 私有根目錄。

## 最小新資料，不要再丟更多 raw logs

### 必要解鎖

- 完成既有 frozen 20 案的七項 PASS／FAIL、overall 與安全判定。
- 只有爭議案才找第二位真人仲裁。

### Pilot 修正集

先做 30–50 組 Owner／Mina 親自核准的繁中 gold；若可行，擴到 80 train／20 validation。每筆最少包含：

- 客戶上下文。
- 本案允許使用的事實。
- 理想回覆。
- 必問欄位。
- 禁止承諾。
- 何時轉人工。
- 舊答案與最小修正版，以及一個失敗原因代碼。

優先覆蓋四類：過長、重問已知資料、未回答當前問題、未授權價格／政策。易變價格與政策只作 runtime authority，不進模型記憶。

## 可證偽的升級流程

| 階段 | 唯一主要變因 | 通過條件 |
|---|---|---|
| P0 評分器校準 | 人工 rubric | 20 案至少 18 案 exact agreement；安全錯判 0 |
| P1 Prompt E1 | 只換 prompt contract | 相對 baseline 至少 +4/20，任一 stage 不得退步超過 1 |
| P2 QLoRA SFT | 固定 base + 一個 adapter | 獨立 holdout 至少 85%；各 stage 至少 80%；硬違規 0 |
| P3 偏好學習 | 人工 chosen／rejected 或好／壞標籤 | 盲測偏好勝率至少 60%，安全不退步 |
| P4 私有 shadow | 真實案例、人工確認、絕不自動發送 | 連續 50 案 direct-use／minor-edit 至少 80% |
| P5 底層模型降級 | 只換 student | 工具、路由、安全 100% 一致；對話品質落後不超過 5 個百分點 |

任何未授權價格／政策／檔期、個資洩漏、holdout 汙染或客戶自動發送，立即停止該實驗。

## 當前證據邊界

已完成 3-step 純合成 QLoRA smoke：adapter 可保存、重新載入，base 與 adapter 對同 prompt 的輸出不同，deny-network sandbox 下 peak memory 2.697GB。這只證明本機權重更新鏈可用；三筆更新不代表業務品質改善，正式資料訓練仍由人工 rubric 與 DLP gate 擋住。

## Resume Prompt

我是接手 Hermes 訓練的 Codex／A1。先讀 CURRENT_STATUS、pitfalls、T-A6-HERMES-LINE-GYM-001、hermes-line-reply-training-plan與本文件。MLX training/eval lab 已完成，正式 route 仍 disabled；不要重裝 CUDA framework，也不要把 950 個 OpenRouter requests 稱為訓練輪。下一步先完成 frozen 20 案具名真人 labels，再校正 identity-blind scorer；達 18/20 且安全 mismatch=0 後，才建立 30–50 組 Owner-corrected gold、跑 DLP、用固定 Qwen3-4B-Instruct-2507 base 做第一個可證偽 QLoRA。外接碟只能放公開模型；私有 dataset／adapter／logs 留在 owner-only root。任何硬違規立即停止，不接 live gateway。
