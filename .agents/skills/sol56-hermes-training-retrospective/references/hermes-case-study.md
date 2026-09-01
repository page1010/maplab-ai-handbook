# Hermes training case study — 2026-09-01

這份案例用來理解 Skill 為何採用 What／So What／Now What；不是其他任務的固定參數表。

## What — 已驗證事實

- 前 5 個所謂「訓練輪」實際只有 random two-shot inference，沒有 optimizer、gradient 或權重更新。
- 前 5 輪合計 4/25 pass（16%），分布 40% → 0% → 0% → 40% → 0%；第 1、4 輪各有一個未授權價格。
- 完整 12 輪為 10/60 pass，單輪最佳 40%，success streak 0。
- 50/60 failed；length gate 擋 39 次，38 次實際過長，32 次只有長度問題。
- Hermes 回覆中位數約 126 字，Mina historical reply 中位數約 26.5 字。
- 舊評分器讓 35 個 75 分以上的答案仍被 hard gate 判失敗，證明 lexical score 與業務合格不是同一件事。
- 每輪樣本不同、沒有固定 canary，lesson 會覆寫；結果無法歸因到單一方法。
- Supervisor pause 後，02:20 raw-loop side door 又產 5 calls、0/5 pass、1 個未授權價格。

主要證據：

- `workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/first_principles_review.md`
- `workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/validation_receipt.md`
- `scripts/hermes_line_training_loop.py`
- `handoff/tasks/T-A6-HERMES-LINE-GYM-001.md`

## So What — 因果斷點

原本假設是「每輪看失敗 → lesson 更新 → Hermes 會愈來愈好」。實際機制只有「抽不同題目 → 加 random two-shot／可變 lesson → 再推論」。沒有可累積權重，也沒有固定比較面板，因此多跑只增加活動量，無法證明學習。

最重要的四個失敗機制：

1. 回覆設計過長，不是樣本數不足。
2. 已知資料重問、當前問題沒先回答，是 state／prompt contract 問題。
3. 價格、政策、檔期越權，必須由 authority 與 hard guard 控制。
4. 評分器、樣本與執行 route 漂移，使結果不可比較且 pause 可被繞過。

## Now What — 已做與未做

已做：

- 停止相同 random loop。
- 凍結 20-case holdout、建立七項 rubric guide、把 schedule 改經 supervisor fail closed。
- 安裝 Apple MLX-LM＋Qwen3-4B-Instruct-2507 隔離 training/eval lab。
- 以 8 train／2 valid／1 test 純合成資料跑 3-step QLoRA；adapter 可保存與 reload，deny-network，peak memory 2.697GB。
- Base 與 adapter 對同 prompt 輸出不同，證明權重鏈可運作。

仍未完成：

- Structured named-human labels 仍為 0/20。
- Synthetic adapter 只讓回答更短，仍漏掉「先承接單一窗口價值」；`QUALITY_NOT_PROVEN`。
- 真實資料尚未通過完整 DLP／rights gate。
- Live Hermes route 仍 disabled，沒有 customer send。

## 目前成功契約

以 active Task Card 為準；本案例的核心 gate 是：

- 20/20 具名真人 labels。
- Identity-blind scorer 至少 18/20 exact agreement，安全 mismatch 0。
- 先準備 30–50 組 Owner／Mina 親改 gold，另留完全獨立 holdout。
- QLoRA candidate 必須在固定盲測相對 base 有可歸因提升，未授權價格／政策／檔期、PII memorization 與客戶自動發送為 0。
- 通過後只進 50-case 人工 shadow；direct-use／minor-edit 達 Task Card 門檻才考慮 promotion。

## 這個案例留下的永久句子

> 呼叫次數不是學習，輸出改變不是改善，基礎建設通過不是品質通過；只有可重建的權重差異、固定盲測提升與真實人工採用，才能叫訓練成功。

## 2026-09-01 補充：從回覆負例追到整條商務 route

Owner 在看過 annotation workbook 後指出三種大雷：固定報價並保留檔期、宣稱所有人都能吃且不用確認、保證價格與檔期後要求直接下訂。問題不只是模型答錯，也不是工作簿格式；真正根因是監工只看欄位／產物，且客服回覆與會自動帶訂金、費用、菜單、條款的舊報價路徑相連。

本次以 What／So What／Now What 重設為：

- What：負例未先明標禁止，歷史模板被誤當現行 authority，舊 Sheet action 仍有商務副作用。
- So What：只改 prompt 或回覆字句無法阻止下游自動計價；需沿 customer copy→state→router→payload→Sheet→human approval 查完整因果鏈。
- Now What：Hermes 每輪只問一題，只能建立 neutral Sheet shell 或記錄客人 revision 原話；模板、route、payload allowlist、三句 regression、pitfall、Task Card、receipt、Resume Prompt 同步更新。

新增永久句子：

> 負例不是候選、歷史不是 authority、安靜文案不是安全 route；客服合格必須一路證明到工具副作用仍不越權。
