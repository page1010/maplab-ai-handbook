# Hermes 可見操作／獨立 Telegram／1000 額度計畫 — 2026-10-02

- Executor: Codex；delegated: hermes_desktop_integration_audit、hermes_1000_runtime_audit。
- Task: `handoff/tasks/T-HERMES-VISIBLE-COMPUTER-001.md`。
- Overall: **AMBER / COMPUTER_USE_LIVE_PASS / SYNTHETIC_BATCH_PASS / TELEGRAM_OWNER_GATE**。
- Window: 2026-10-02 下午，Asia/Taipei。這是實測回執，不是1000次用滿或業務成效證明。

## What — VERIFIED

1. **可見原生對話**：Hermes desktop v0.21.0 (+20361), source `86b50fb`，default profile；session `20261002_151604_3c4eb0` 已置頂，名稱 `MAPLAB｜Hermes 電腦操作驗證 2026-10-02`。真實 computer_use 呼叫、錯誤、修復後點擊、vision 回讀與批次檔案讀取都在該視窗。它是 Hermes 的對話，不是 Codex 全部聊天內容的自動鏡像。
2. **權限與修復**：cua-driver 0.23.2 的 accessibility/screen-recording 已為 true，沒有關閉安全審批或複製瀏覽器登入資料。capture 能用，但舊 indexed-click adapter 沒傳 schema 支援的快照 token。最小修補沿用現有 token，保留 stale guard；不改 capture 隔離策略。
3. **重載與 live**：完整 Quit/Open desktop，舊 app/serve PID `44340/44368` 消失；新 app/serve `38713/38737`（15:39:01/02）。不是只按 Messaging Restart gateway。
4. **操作閉環**：先前 Chrome 公開頁測試因 token 錯誤停止；Chrome AX 是否跨視窗隔離未證明，因此改單一計算機。Hermes 對 Calculator `pid=38887/window_id=13362` 執行 list→capture SOM→click index5（數字7）→capture。工具回 `ok:true / Performed AXPress`；Codex 獨立 CUA AX 回讀顯示 `0 → 7`。SOM 漏靜態 display，後續只做一次 `capture(mode=vision)`，工具輸出 `Window Title=計算機, 230x408, auxiliary.vision` 且 `main display area shows the number 7`。Hermes 自身也回報讀到7。
5. **既有批次受控實跑**：run `20261002-b1of6-072757-36898`，4 provider attempts／2成功回應／1合成圖片指令草稿／1換模型審稿。生成 nemotron-super；gemma、minimax HTTP失敗；dots-note審稿成功。今日舊程式未記帳用量 UNKNOWN。原生桌面對話／vision 請求不包含在這4次或該共用ledger。
6. **排程已註冊**：既有 `com.maplab.freequota` 六班 LaunchAgent 已安裝，kickstart `runs=1 / last exit code=0`；stdout 為 `[hold] automatic ramp starts on UTC 2026-10-03; historical usage unknown`。正式自動小批次尚未到期、尚無排程產稿證據。首個非hold班次預計 **2026-10-03 10:05 TST**；之後當地02/06/10/14/18/22:05。每班 max3 items/max12 requests，只跑合成 queue40；全日受控runner cap950 + Owner reserve50，不為吃滿額度而產無用稿。

### 檔案與測試

- 真實批次 JSON/MD：`data/free-quota/report_20261002-b1of6-072757-36898.{json,md}`。
- 草稿：`data/free-quota/image-prompts/prompt_20261002-b1of6-072757-36898/001.md`。
- 審稿：`data/free-quota/reviews/40-image-prompt_20261002-b1of6-072757-36898_001.review.md`。
- `synthetic-smoke-verification.json`：9項獨立結構／ledger／排程 parity assertions 通過，附原檔 SHA。不是採用驗收。
- `calculator-vision-readback.png`：Hermes自身capture的230×408計算機圖；SHA256 `b0af68afe8435bbd5d4ab1b4c53b1f94d1f2501f1e7ffa98323b03ce089177e2`。
- `driver-token-compat.patch`：實際修改 installed Hermes 的 backend＋tests，可重現的zero-context patch；SHA256 `7479d25b7b21b8811eb9e7b42a5ba31c89340cca3dfdf75486bafe11d30c4cfb`，`git apply --reverse --check --unidiff-zero`通過。上游更新可能覆蓋，更新後需重驗，不盲目套patch。
- Hermes focused regression：修前2 failed/4 passed→修後6 passed；三檔 `test_computer_use.py`、`test_computer_use_cua_0_9.py`、`test_computer_use_delivery_ladder.py` 合计135 passed/0 failed（delegated官方run_tests.sh離線執行）。既有contributors dirty保留。
- MAPLAB `python3 -m unittest discover -s tests -p 'test_free_quota_daily.py' -v`：9 passed/0 failed（含候選／成功措辭精確斷言，root最後一次0.532s）。
- `bash -n` runner/wrapper：PASS。repo及installed plist `plutil -lint`：兩個OK。相同完成班次重跑直接skip，無新增provider請求；runner不再自行git add/commit/push。
- `graphify update .`：最終措辭修正後AST-only完成，5135 nodes/9363 edges/424 communities；自動生成及其他人的dirty不納入本任務commit。

## So What — 價值與限制

- 不再把 Gateway ready 當 Telegram已接；不再把OS權限當電腦操作閉環已通。Owner可以在真正的Hermes桌面置頂對話看工具操作和回執。
- 停止了非法 `10/6` 舊batch（精確PID97595/97607），保存已產草稿；修復班次驗證、共用UTC ledger保留、唯一run_id、完整成功才skip、無自動Git副作用。沒有刪除歷史產出。
- 批次仍沿用既有shell/provider runner；Hermes桌面是讀取檔案回執，**不是已證明所有批次都由原生Hermes自主agent執行**。
- 1000是容量計畫，非已完成量；目前沒有實際生圖、模型權重訓練、Owner採用、SEO提升或業務複利成效證據。
- 抓到一次摘要誤讀：歷史 jobs.note「扇出9件成功1件」被Hermes說成成功9件。實際只有1件；已在同一對話更正，後續runner文字分列候選／實際成功，不回改歷史原回執。模型審稿PASS也仍需獨立驗收。
- private A8、客資、LINE、登入態、secrets不得送OpenRouter/DeerFlow。自動ramp只queue40合成場景；其他含CONTEXT queue未准自動放行。

## Now What — 一個接續動作

**Owner在本機Hermes安全設定填入獨立BotFather bot的token並確認Owner-only允許身份後，做一次nonce Telegram往返＋同default profile桌面session readback。** 不在聊天或receipt貼token，不重用A6 token開第二個poller。

| task | status | owner/evidence | acceptance proof |
|---|---|---|---|
| Desktop computer-use | verified | Codex＋Hermes live session | click＋獨立AX＋auxiliary vision均讀到7 |
| Runner repair / ramp | installed, first scheduled output pending | existing com.maplab.freequota | live手動1件已驗；首班排程需另查receipt |
| Separate Telegram | owner_gate | 四profile native token均缺；已問Owner | 新bot Owner-only，nonce往返，desktop同session |

兩種方案已告知Owner：建議保留A6另接Hermes；另一個選項是由Owner明確改授權原A6入口遷移。尚無選擇／新token，不自行偷換服務。現有A6 custom文字bot和native gateway保持原樣。

## Alignment Audit

- CURRENT_STATUS頂層Active Task仍為既有LINE→Sheets；本案新增具名Parallel Active Task，不搶走別人工作。
- 本Task Card、Parallel Next Bounded Action、Resume Prompt：對齊Telegram Owner gate；runner排程另列為dynamic/pending首次產出。
- generic governance audit按頂層LINE task檢runner會報routing unresolved（exit2）；未宣稱全系統指標已對齊。
- Nativegateway service可活著而platforms為空；四profile均無nativeTelegramtoken，桌面Messaging顯示Disabled/Needs setup。本輪不能稱Telegram已完成。

## Resume Prompt

先讀AGENT_CORE/CURRENT_STATUS/pitfalls與T-HERMES-VISIBLE-COMPUTER-001，再讀本receipt。延續置頂Hermes session 20261002_151604_3c4eb0。電腦點擊及vision讀回已驗，不重跑湊次數；Chrome多視窗隔離仍未證，不開真實瀏覽器profile複製登入態。下一步只接Owner提供的新nativeTelegrambot：token只入安全欄位，Owner-only白名單，不與A6共用poller；一次nonce往返＋桌面同profile讀回才升PASS。另按日期查首個排程batch artifact，不能以launchctl存在冒充成功。今日舊用量未知，原生desktop不在4次batchledger內。遇摘要數量錯誤，分列候選、attempted、success、adoption；兩輪無改進做失敗分桶，不提高round。所有未涉本案dirty保持原樣。
