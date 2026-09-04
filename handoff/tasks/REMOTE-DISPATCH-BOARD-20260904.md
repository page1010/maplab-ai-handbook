# 遠端派工看板（2026-09-04 起）— Owner 不在電腦前也能開工

依據：Owner msg 4703「我不在電腦前也可以遠端讓你開工 你留好任務卡好 和如何喚醒派工的promot給我」。
配套制度：skills/fable5-design-hermes-run-sop.md（設計歸 Fable5、執行歸 Hermes）、memory a0-decision-autonomy-rule（標準答案自己定）。

## 怎麼遠端喚醒（Owner 只要做這一件事）

在 Telegram 對 bot 傳一句話即可——bot 會用同一個 session 續接把訊息帶進來，不用開電腦、不用終端機。

**萬用派工 prompt（複製改編號就能用）：**

派工 T編號。有補充決定寫在冒號後面。按任務卡執行，紅線照舊：不對外發布、不碰secrets、不動錢；做完留 handoff 報告與收據，做不了就回報卡在哪，不准假裝完成。

**極簡版（我看得懂）：** 「開工 T1 選B」／「派工 T3」／「T5 go」

**查進度 prompt：** 「進度」或「T3 進度」——我回各卡狀態，不重跑工作。

## 任務卡清單（現在就能派 vs 缺你一個決定）

### 你一句話就能點火的（缺的只是你的裁決）

| 卡號 | 任務 | 缺你哪句話 | 派工範例 |
|---|---|---|---|
| T1 | 健康爺爺角色重畫：精緻化現有 2D 向量引擎（Kurzgesagt／Headspace 調性），重畫進渲染程式並重渲染短片 | 同意路線＋選 A（鄰家阿伯）／B（活力教練）／C（安心嚮導） | 開工 T1 選B |
| T4 | 邦妮兔音訊重生（AUDIO_REGEN_REQUIRED） | 歌詞版本：公開安全版 or 點名版（一個詞） | T4 公開安全版 |
| T5 | lo-fi 頻道試作一支（燒 Suno 額度） | go／no-go | T5 go |
| T8 | 語音庫規劃啟動（固定聲音身分＋台詞庫＋樂齡語氣規則） | 開始與否（會綁 T1 的角色選擇） | 開工 T8 |

### 不用等你、我方可先動的（派了就跑）

| 卡號 | 任務 | 說明 |
|---|---|---|
| T3 | Hermes A8 音樂健身房訓練（目前 0%） | 照 owner-homework-and-hermes-burn-plan 訓練 Hermes 跑 Suno 流程，週四 22:00 重置前燒完額度窗口 |
| T9 | 對手拆解＋影片 QA 跑批工具安裝（video-autopilot-kit） | 裝好後首發給 Hermes 跑批 |

### 有前置條件的（先答前置，卡才能動）

| 卡號 | 任務 | 前置 |
|---|---|---|
| T2 | Draw Things／Stable Diffusion 可行性測試（備案路線） | 同意在這台機器裝免費 App Store app |
| T6 | eToro 每日抓富途對應即時線圖 job | 同意安裝 Futu OpenD（全程 Demo，Real 端點禁用） |
| T7 | 廠商詢價發送 | 你點名對象名單（對外發訊是紅線，定稿後仍會先給你過目） |

### 你自己的功課（我無法代做，見 handoff/A8-owner-manual-youtube-pinterest-20260904.md）

頻道建立、youtube.upload OAuth、Suno 登入、Gmail 頻道、Pinterest token、eToro Demo scope、IG 登入。做完任一項回一句「功課X完成」，我就接後續自動化。

## 派工後我這邊的固定流程

1. 讀對應任務卡與相關 handoff → 執行（重複性活按 SOP 轉 Hermes）
2. 產出與過程留在 handoff/ 並 git commit（branch chore/agent-login-governance-20260816）
3. Telegram 回報結果＋收據；卡住就講卡在哪，不假裝完成
4. 紅線不變：對外定稿、轉公開、secrets、金流、最終 QA 放行都回到你或我本人

## Changelog

- v1.0（2026-09-04）：初版，依 msg 4703 建看板。
