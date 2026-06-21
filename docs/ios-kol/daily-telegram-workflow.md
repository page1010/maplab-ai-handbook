# IOS-KOL Daily Telegram Workflow

版本：2026-06-17
Owner：IOS-KOL Influencer Radar Manager
用途：定義 KOL/RSS/OpenClaw/ASR 到 Telegram 的責任歸屬、每日工作與品質 gate。

## 責任歸屬

Telegram 的 `網紅單集重點`、`網紅投資 seed triage`、`網紅操作筆記` 屬於 IOS-KOL 部門責任。

OpenClaw 是 worker，不是責任 owner。OpenClaw 可被 IOS-KOL 指派做瀏覽器、NotebookLM、ChatGPT/Gemini、截圖或格式檢查工作；但是否能發給 Owner，由 IOS-KOL 的 quality gate 決定。

Telegram 訊息開頭必須標明：

```text
IOS-KOL 網紅雷達經理｜團隊指派 OpenClaw/ASR 回報 | YYYY-MM-DD HH:MM
```

若 OpenClaw 尚未實際完成，訊息內必須用 worker 狀態說明，不得假裝已完成。

## 現行 runtime

已查到的 Investment OS runtime 路徑：

```text
/Users/pagemacmini/.local/share/investmentos-telegram-operator
```

主要 jobs：

| Job | 排程 | 用途 |
| --- | --- | --- |
| `influencer-youtube-rss-poll` | 每 600 秒 | 只抓 YouTube RSS metadata，偵測新片；不得直接當正式研究結論。 |
| `influencer-sync-refresh` | 02:30 / 08:30 / 14:30 / 21:20 | 抓逐字稿或 ASR、整理摘要、做 cross-check、發 Telegram。 |
| `influencer-hermes-report` | 另一路報告 | 可做較冷路徑的 KOL 報告，不取代 hot-path Telegram gate。 |

主要腳本：

```text
scripts/run_invest_os_background_job.py influencer-sync-refresh
scripts/sync_influencer_agents.py --db-path ... --notify-telegram --kol-shadow
```

## 資訊來源

現行 YouTube KOL sources：

| Source | 角色定位 |
| --- | --- |
| 游庭皓的財經皓角 | 總經、利率、資金流、大盤風險。 |
| 股癌 Gooaye | 市場情緒、科技供應鏈、散戶/社群語氣。 |
| 財報狗 StatementDog | 基本面、產業趨勢、財報與供需。 |
| 理財達人秀 | 標的、籌碼、技術與操作框架。 |
| 定錨產業筆記 | 產業鏈、capex、規格升級、供應鏈瓶頸。 |

現行 RSS：

| Source | 用途 |
| --- | --- |
| BlockTempo 動區動趨 | 加密、AI、預測市場、地緣政治與風險偏好線索。 |
| 理財達人秀／兆華與股惑仔 Podcast | 李兆華 SoundOn RSS；作為理財達人秀/李兆華補充來源。進單集雷達時只能標 `Podcast/RSS 摘要（待逐字稿）`，不可冒充逐字稿。 |

待補 sources：

| 類型 | 要求 |
| --- | --- |
| 英文 KOL / 英文新聞 | 必須先翻譯，再整理成同一格式；不可只貼英文標題。 |
| 總經資料 | 夜盤、美債殖利率、美元、油價、BTC、VIX、重要數據日曆。 |
| 台股對照 | 台指夜盤、ADR、SOX、NVIDIA/TSMC ADR、AI server 供應鏈。 |

## 發送流程

單集更新流程：

1. RSS 偵測新片或新文章。
2. 取得 YouTube transcript / subtitle / ASR。
3. 摘要模型整理：逐字稿重點、Q&A、操作筆記、缺資料、失敗條件。
4. Investment OS cross-check：持倉、候選池、強勢族群、主線 tag。
5. 格式檢查：手機可讀、來源 URL、非下單語氣、操作筆記不可是段落標題。
6. Telegram 發送。

正式 `網紅單集重點` gate：

| Gate | 規則 |
| --- | --- |
| transcript | `transcript_status=ok` 才能進正式單集重點。 |
| metadata | `metadata_only` 只留待補，不發正式重點。 |
| RSS | 一般 RSS 文章不進單集重點，進 seed triage 或夜間綜合；核心 KOL podcast RSS 可進單集雷達，但必須標 `Podcast/RSS 摘要（待逐字稿）`。 |
| content | `content_extraction` 不可為「偵測到新片」或「尚未取得可用內容萃取」。 |
| Q&A | 必須有 Q1/A1 到至少 Q4/A4，且不是純標題重寫。 |
| 操作筆記 | 只記節目裡真的提到的操作/策略/處置，不得把 `操作/策略筆記` 標題本身當內容。 |

## 每日工作

02:30 夜盤/半夜綜合：

- 整合美股收盤或盤中、台指夜盤、SOX/NVIDIA/TSMC ADR、美債、美元、油價、BTC/VIX。
- 整合過去 24 小時多 KOL 最新內容。
- 輸出 `IOS-KOL 夜盤總經共識雷達`。
- 必答：多 KOL 是否有一致看法？一致在哪個主線？反對或缺口在哪？

08:30 早盤前：

- 抓最新 YouTube RSS 與核心 KOL podcast RSS。
- 若已有 transcript/ASR，整理單集重點。
- 若只有 metadata，僅列待補，不發正式研究結論。
- 若是 podcast RSS，只列節目摘要線索與待逐字稿，不寫成完整節目結論。

14:30 盤中/午後：

- 更新中午前後新片與 RSS。
- 檢查是否與台股盤中族群強弱、成交量、法人方向共振。

21:20 晚間：

- 整理晚間新片。
- 先做單集重點與 seed triage。
- 若多 KOL 同時指向同一主線，標成共識候選，留給 02:30 夜盤總經綜合。

## 夜間綜合格式

```text
IOS-KOL 夜盤總經共識雷達 | YYYY-MM-DD HH:MM

1. 夜盤與總經狀態
- 美股 / SOX / 台指夜盤 / 美債 / 美元 / 油價 / BTC / VIX

2. 多 KOL 一致看法
- 一致主線：
- 支持 KOL：
- 反對或保留：
- 一致程度：高 / 中 / 低

3. 第二層產業推演
- 供需：
- 規格：
- capex：
- ASP / 毛利：

4. 第三層 radar
- 公司 call / 供應鏈 / BOM / 操作筆記：
- 證據標籤：
- 待驗問題：

5. 今日最該查
- 官方資料：
- 產業報價：
- 籌碼/成交量：
- 反證條件：
```

## 修正記錄

2026-06-17 已在 runtime 修正：

- `網紅單集重點` 開頭加入 IOS-KOL 與流程說明。
- 正式單集重點只允許 `transcript_status=ok` 的 YouTube 內容。
- RSS / metadata-only 不再混進正式單集重點。
- 操作筆記濾除段落標題與 Q/A 殘渣。

2026-06-20 已在 runtime 補《兆華與股惑仔》SoundOn RSS：

- Castbox app link `http://castbox.fm/app/castbox/feed/1a64de3cc9215d1a2fc86338e14e4d2772edc5a4/track/18dbb6bb4844a5e0675576351dbc7773c16848f4` 驗證為《兆華與股惑仔》，非股癌；穩定 source 使用 SoundOn RSS `https://feeds.soundon.fm/podcasts/91be014b-9f55-4bf3-a910-b232eda82d11.xml`。
- Runtime source name 為 `理財達人秀／兆華與股惑仔 Podcast`，對應核心 KOL `理財達人秀` visibility gate。
- `build_cross_checks()` 改支援 `source_ids`，新 podcast row 即使發布日較舊也會被 cross-check，不再被全域 latest 20 擠掉。

2026-06-20 接上正式 rubric（Owner 採納）：

- `網紅單集重點` / `IOS-KOL 夜盤總經共識雷達` 文字品質的 Verification（主觀任務）依 `rubrics/telegram-digest-quality.md` 評分；該 rubric 的維度 3（措辭安全）對應本文件 `修正記錄` 已落地的內部流程語禁用，維度 4（資料層級透明）對應上方 `網紅單集重點` gate 表的 transcript/metadata/RSS/Q&A 規則。
- IOS-KOL 目前在 `handoff/tasks/` 下沒有正式 task card，故先把 verification 連結補在本文件；若日後建立 `T-IOS-KOL-*.md`，應把這行搬過去並沿用 `templates/task-card-template.md` 的格式。
