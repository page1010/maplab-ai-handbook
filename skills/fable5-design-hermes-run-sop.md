# 設計歸 Fable5、執行歸 Hermes——分工制度 SOP v1.0（2026-09-04）

- 依據：Owner msg 4684「你可以做設定與制度sop規劃，讓hermes跑與執行，這樣你得到 1.prompt的回饋 2.省下的額度 3.對我們系統的進步留下記錄」
- 相關：memory fable5-a0-quota-and-dispatch-discipline（派工為主、不自燒高階額度）、hermes-quote-gym-pipeline（報價健身房先例，4 輪全 PASS）

## 原則

貴的腦（Fable5/Codex 額度）只做一次性的設計：SOP、決定性腳本、驗收標準。
便宜的腦（Hermes 免費鏈，1000 次/天）跑重複性的執行。
每一次執行都要回饋到設計，形成閉環——這是複利，不是外包。

## 三條回饋線（Owner 點名的三個收益，各自要有落點）

1. **prompt 回饋**：Hermes 每輪執行結果必附「哪一步看不懂／哪一步失敗／SOP 哪裡寫得不清楚」。Fable5 據此修 SOP，版本號遞增，改動寫進該 SOP 檔尾的 changelog。報價健身房 SOP v1→v3 就是這個模式的先例。
2. **省下的額度**：每項移交 Hermes 的任務，在 data/subscription_credit_ledger.md 逐筆記「若由 Claude 跑的估計消耗 vs Hermes 實耗（免費鏈）」，月底金流監察引用。
3. **系統進步紀錄**：SOP 版本 changelog＋健身房 round 評測結果＝系統資產，全部進 git。人離開、窗斷線，制度還在。

## 移交門檻（什麼任務可以給 Hermes）

全部符合才移交：
- 有成文 SOP 可循（不靠臨場判斷）
- 重活由決定性腳本包辦（Hermes 負責調度與初判，不負責發明）
- 失敗可以無代價重跑
- 不碰 secrets、不對外發布、不動金流

## 不可移交（紅線，Fable5 或 Owner 保留）

- 對外發訊定稿與送出（客人、廠商、社群）
- 「轉公開」與任何發布動作
- secrets／金鑰／帳號操作
- 最終 QA 放行（Fable5 抽查簽核；Hermes 只做初判）

## 首批適用清單（2026-09-04 起）

| 任務 | SOP／工具 | 狀態 |
|---|---|---|
| A8 音樂健身房（Suno 流程） | owner-homework-and-hermes-burn-plan-20260904.md | 已規劃，0% 訓練，等燒額度窗口 |
| 對手拆解跑批（3 支參考片） | video-autopilot-kit teardown（決定性腳本） | 工具未裝，裝好後首發 |
| 影片交付 QA 跑批 | video-autopilot-kit media_delivery_qa | 同上 |
| 每日保底報告 | daily-report-guardian skill | 已上線 |

## Changelog

- v1.0（2026-09-04）：初版，依 Owner msg 4684 定調成文。
