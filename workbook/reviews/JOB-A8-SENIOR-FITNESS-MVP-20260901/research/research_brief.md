# 中高齡華語跟著動｜研究 Brief

Date: 2026-09-01  
Status: `PUBLIC_RESEARCH_COMPLETE / PT_REQUIRED`  
Scope: public sources only; not medical advice

## VERIFIED｜官方基準

- WHO 對 65+ 的整體框架是有氧、肌力與包含平衡／肌力的多元活動；能力不足時仍應依自身能力活動。來源：[WHO 2020 Guidelines](https://www.who.int/publications/i/item/9789240015128)、[WHO older-adult summary](https://www.who.int/publications/b/67181)。
- CDC 2025 指引：65+ 每週需要有氧、肌力和平衡活動；中等強度主觀約 5–6/10，可說話、但不能唱歌，且強度因人而異。來源：[CDC older-adult activity](https://www.cdc.gov/physical-activity-basics/adding-older-adults/what-counts.html)。
- NIA 建議漸進增加、活動前暖身、結束後緩和；既有傷病或慢性病應與醫療／運動專業者討論。來源：[NIA getting and staying active](https://www.nia.nih.gov/health/exercise-and-physical-activity/tips-getting-and-staying-active-you-age)。
- NHS 坐姿與平衡指引要求使用穩固、無輪的椅子，雙腳能踩平；平衡練習應靠牆或穩固椅。來源：[NHS sitting exercises](https://www.nhs.uk/live-well/exercise/sitting-exercises/)、[NHS balance exercises](https://www.nhs.uk/live-well/exercise/balance-exercises/)。
- 台灣國健署公開的居家五招以坐站、扶椅與慢慢增加為核心，並要求疲憊時休息、不勉強。來源：[長者居家來運動](https://www.hpa.gov.tw/Pages/Detail.aspx?nodeid=4306&pid=14190)。

MVP 命名結論：用「低衝擊節奏間歇」，不把經典 20 秒高強度／10 秒休息的 Tabata 當中高齡預設。

## VERIFIED｜成熟案例的抽象結構

| 案例 | 可學的抽象結構 | 不照搬 |
|---|---|---|
| [台灣國健署銀髮資源](https://www.hpa.gov.tw/Pages/Detail.aspx?nodeid=4576&pid=15023) | 華語在地、生活化、坐／站成套 | 政府品牌、影片與腳本 |
| [More Life Health](https://www.youtube.com/watch?v=4E5E-sr0Hvw) | 專業者定位、呼吸與倒數、坐姿後進站姿 | 個別診斷暗示 |
| [HASFIT senior workout](https://www.youtube.com/watch?v=LHx3eP93Zrg) | 兩人同時示範站／坐版本、完整暖身與緩和 | 彎腰、旋轉、快跑段 |
| [yes2next chair strength](https://www.youtube.com/watch?v=dNW2Pdn1dA0) | 高齡真人、站／坐退階、動休節奏 | 人物關係與原編排 |
| [SeniorShape library](https://www.seniorshape.com/videos) | 按器材、時間、形式篩選，證明短模組→合輯 | 全站姿 20/10 當預設 |
| [SilverSneakers](https://www.youtube.com/watch?v=TyDidA1czCU) | 連結日常功能，不靠瘦身焦慮 | 「人人每日必做」處方語氣 |
| [Walk at Home](https://www.youtube.com/watch?v=X3q5e1pV4pc) | 原地走、側步、踢腿、抬膝；不會就回安全基地 | 加速與大幅度段 |
| [Yoga With Adriene chair yoga](https://www.youtube.com/watch?v=-Ts01MC2mIo) | 慢語速、呼吸、可暫停、椅子調整 | 抽象意象取代安全口令 |

共同模式：片頭先交代對象／時間／器材；動作先示範再計時；口令順序為姿勢→呼吸→幅度→倒數；固定安全基地是坐姿、扶椅或小幅度；每支短片要獨立包含做法、退階與停止條件。

## DeerFlow Receipt

- First attempt: `DFR-20260901-122235-be404e` — `FAILED`, cause=`langchain_ollama missing`, network calls=`0`, clean shutdown=`true`.
- Remediation: synced the pinned backend lockfile's `deerflow-harness[ollama]` extra into DeerFlow's own virtual environment; no provider switch.
- Verified retry: `DFR-20260901-122529-0f23b8` — `COMPLETED`, provider=`local`, model=`hermes-local-gemma4`, one bounded public DDGS retrieval, no file/browser/MCP/memory/subagent capability, clean shutdown=`true`.
- Artifact: `workbook/reviews/A6-HERMES-TASKS/DFR-20260901-122529-0f23b8/research.md`, sha256 `6343d3707636efb95925ef8f4d58b565dc4d93f30d51686453f263f5376264f3`.
- Boundary: DeerFlow retrieval returned mostly academic/secondary sources, so it supports the broad strength/balance direction but does not replace the official-source synthesis or professional movement review above.

## INFERENCE｜MVP Product Decisions

- 5 independent 17.5-second shorts provide a minimal, testable motion language.
- 107.5-second compilation validates continuity and channel packaging; it is not a full exercise prescription.
- Spoken coaching is the control. Instrumental hip-hop provides a stable beat. Sung commands are a later A/B test because clear safety wording matters more than novelty.
- The target ring is labeled「主要活動區（非診斷）」and never implies spot reduction or treatment.

## MISSING｜Public Release Gaps

- Qualified Taiwan PT or senior-fitness professional review.
- Segmentation for healthy 50–64, 65+, frail/high-fall-risk, chronic disease and post-operative audiences.
- 3–5 target-age usability tests on comprehension, tempo, type size and chair placement.
- Rights-cleared narration, music, font/illustration and any coach likeness.
- Phone/TV target-device readback and actual-audio full listen.
- YouTube AI disclosure, commercial-rights and original/authentic policy readback at upload time.
