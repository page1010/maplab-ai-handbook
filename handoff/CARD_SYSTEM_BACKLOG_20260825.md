# 卡:系統待辦總表(Owner 3965/3971 指示,2026-08-25 00:30 檢查結果)

- 檢查者:Fable5(bot 代答窗,無網路/無進程權限;能查能改檔,不能 kill/curl/launchctl)
- 原則:好的留下,不好的留紀錄,不改錯方向

## A. 為什麼稽核會漏(兩個不同的洞,答 Owner 3965)

1. **執行斷鏈**:晶技 22:10 推播在 08-22 稽核(telbotfin_audit.md #5/#6)有抓到、判了「停+改寫」,但判決沒人執行 → 08-24 已補 top3-gate(見 CARD_TOP3_GATE_VERIFY_20260824)。
2. **樣本窗洞**:當時稽核方法=「讀回哪幾則審哪幾則」,16:20/16:50 下午檔不在讀回樣本裡,根本沒進稽核範圍。**修法:稽核單位改為「job 總表逐一對照」**(launchd 清單 × 每日應到訊息),不是按讀到的訊息審。→ 工作 A-1:建 telegram 產品應到/實到對照表(daily roll-call),缺席自動列警示。

## B. 動能三產品(前幾名/強股故事/股期劇本)現況——不是被停,是三天打魚

- 兩個 job 都活著:com.investmentos.strong-stock-story-early(16:20,前幾名+強股故事)、com.investmentos.stock-future-opening-playbook(16:50,股期劇本)。同屬 IOS-MOMENTUM 動能經理。
- 08-24 兩個都跑成功;強股故事 telegram_sent:true 已驗證;股期劇本訊息已組好但送達未驗證(log 無明確 sent 旗標)→ 工作 B-1:驗證股期劇本實際送達哪個 chat。
- **失敗模式 1**:ai_hermes_strong_stock_story_gpt(ChatGPT 瀏覽器步驟)08-18/19/21 valid:false,失敗時整則不送 → Owner 端體感=產品消失。→ 工作 B-2:GPT 步驟失敗時 fallback 送 rule-based 底稿(build_limit_up_chip_story 每次都成功,素材在),寧可送淺版也不斷供。
- **失敗模式 2**:08-22(五)兩個 job 整天沒跑 → 工作 B-3:查 08-22 斷跑原因(機器睡眠?launchd 漏 kick?),必要時加 RunAtLoad/補跑機制。

## C. gemma4 清理(Owner 明令停)

- 現況:7 個 /Users/pagemacmini/.hermes/hermes-agent venv 的 tui_gateway.slash_worker --model gemma4:latest(PID 47301/47313/47356/49342/49359=08-24 00:27-00:38 殭屍;73785/73824=08-25 00:18 新起)+ Ollama.app serve(PID 37787)。
- 工作 C-1(有權限窗口立即執行):pkill -f "slash_worker.*gemma4";確認 ollama 卸載 gemma4(ollama ps / ollama stop gemma4)。
- 工作 C-2(治本):查 hermes-agent tui_gateway 為何自動起 gemma4 worker(設定檔在 ~/.hermes/hermes-agent),改預設模型為 hermes 雲端方案,本地 gemma4 退役,釋放記憶體。

## D. hermes 備援接手設計(Owner:我額度滿就下班,hermes 無上限方案接)

- 目標:Fable5/Codex 額度滿時,每日產品(晨會/晚報/動能三件套的判讀層)由 hermes 方案接手,不再回退本地 gemma4。
- 前置:hermes 定位對齊稿先給 Owner 裁決(Owner 3938 已點出雙方認知不同步)——對齊稿=佇列最前。
- 設計要點:同一套 prompt/驗收標準,產出格式不變只換引擎;交接觸發=額度監測(quota_meter);產出仍走同一 telegram 通道+四問格式。

## E. 能力 skill 包(Owner msg 3992,2026-08-25 01:04)

- 四項能力已落 skills/(capability-*.md):NotebookLM 專案大腦(**可用**,方法 06-05 已驗證)、Firecrawl 抓站(**待接鑰匙**,啟用步驟已寫)、Owner 聲音生成(**待建**,先本地開源評測再談花錢)、指向性地圖導覽視覺化(**待認領**,三 repo 都沒找到既有實作,等 Owner 指出舊物在哪或當新建)。
- 工作 E-1:Firecrawl 註冊+MCP 接入(Owner 貼 key 照兩畫面模式)。E-2:語音克隆本地方案評測(可派 hermes/免費算力)。E-3:地圖導覽第一場景=maplabkitchen 店面導覽頁。

## 優先序(建議)

1. C-1 殺 gemma4(一條命令)2. B-2 fallback 防斷供 3. A-1 roll-call 對照表 4. B-1/B-3 排查 5. D hermes 對齊稿+接手設計 6. C-2 hermes 預設模型改雲端
