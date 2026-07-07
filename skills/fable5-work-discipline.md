# Skill: Fable 5 工作紀律(蒸餾版)

> 來源:2026-07-06 Fable 5 遠端會話實戰蒸餾(全系統診斷 + A5 診斷 + investment-os 閉環)。
> 用途:給 Codex / Ollama 地端模型 / Opus 級模型在本 repo 工作時遵循。
> 定位:移植的是「行為紀律」不是「原生能力」——照著做,便宜模型也能穩定產出可信結果。
> 對齊:docs/company-values.md §8「先用 Claude 開發,重複維護任務交地端模型」。

---

## 1. 驗證優先(Verification-first)

- 「改完了」不等於「修好了」。宣稱修好前,必須**跑通一次完整閉環**並貼出證據。
- 證據 = 實際輸出,不是推論。例:investment-os 修 pipeline 後,跑 `run_open_batch.py --dry-run`
  並查 SQLite 三張表(proposed_orders/order_events/system_logs)都有列,才算修好。
- 沒有辦法在當前環境驗證時,明說「未驗證」+ 給接手者確切的驗證指令,不得含糊。

## 2. 根因優先,不看症狀就改(Root-cause-first)

- 看到異常,先讀 **log 與 git history**,再判斷,最後才改 code。
- 例:報價單毛利 75.7% 與成本矛盾——不是公式被改爆(git 證明公式三個月沒人動),
  是副本吃了模型 payload 的 preset 值無防呆。若直接「修公式」就是白做+製造新風險。
- 判斷句式:先寫「已知事實(含出處)→ 推論 → 假設」,三者分開,不可混寫。

## 3. 最小變更(Minimal change)

- 正式路徑行為**不變**,新能力用旁路加(例:加 `--dry-run` 而不是改掉真實下單路徑)。
- 一次 commit 只做一件事,commit message 寫「為什麼」不只寫「做了什麼」。
- 新建任何腳本前先 `ls scripts/` 確認不存在;能改一行就不要重寫一檔。

## 4. 結論先行的回報格式(Answer-first reporting)

- 第一句就是答案/結果,支持細節放後面。Owner 用手機讀,不要讓他滾三屏才看到結論。
- 積壓/異常回報用四分類:已完成 / 卡住(卡誰) / Agent 可自解 / 需 Owner 決策(附具體動作)。
- 不確定的數字不寫成確定;寫「約」「推估」並給出處。

## 5. 發案包紀律(Dispatch packet)

- 交接任務時,產出**不需要對話歷史就能開工**的 packet:背景結論、開工順序(讀哪些檔)、
  第一批工作、驗收標準、硬規則。範例:`handoff/dispatch/2026-07-06-*.md`。
- 接手者的第一步永遠是讀 CURRENT_STATUS.md,不是聽轉述。
- 派工要有 receipt:派了給誰、對方要回報什麼、何時檢查。

## 6. 阻塞三層審查(對齊 AGENT_RULES.md Section 16)

- 上報 Owner 前強制自問:①能不能自己解?②阻塞理由站得住嗎(質疑「沒權限/等確認」)?
  ③解除後下一步派工是什麼?
- 「等 Owner」超過 48h 的任務,每次巡查要重新驗證阻塞是否仍成立,不可照抄上次。

## 7. 存檔即工作(Checkpoint discipline)

- 每個有意義變更立即 `bash scripts/checkpoint.sh "角色" "摘要"`;
  CURRENT_STATUS.md 是 commit 的一部分,沒更新 = commit 不完整。
- Session 結束前:更新斷點(AGENT_RECALL_PROMPTS)、push、輸出交接摘要。
  經驗不寫回 repo = 經驗不存在。
