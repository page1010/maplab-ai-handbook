# KOL 網紅同步線成效檢討＋hermes 接手方案（2026-09-03，Owner msg 4588）

## 一、成效檢討（證據：influencer_sync_launchd.out.log 9/3 兩輪實跑 02:30、08:30）

### 有效的部分（值得留）
- **抓新聞源頭有效**：RSS-first 偵測當天就抓到 股癌 EP693、財報狗 560、理財達人秀 9/2 part2、定錨 EP14；RSS 線（兆華與股惑仔等 8 集）判重正常。
- **地端 ASR 有效**：YouTube 字幕全滅（Transcript API 全部拒），但 mlx-whisper（whisper-small-mlx）音訊轉錄 fallback 實跑成功，逐字稿來源標 ok。
- **閉環出貨有效**：DB 寫入 changed=2/3、Telegram digest 正常送達、job panel 有產出。

### 壞掉的部分（Owner 8/30 抱怨的根因就在這）
摘要 LLM 鏈四層全滅，每輪每集都在空轉重試：
1. **Gemini**：429，「monthly spending cap exceeded」——付費專案月額度燒完了。
2. **OpenAI**：403，專案根本沒有 gpt-4o-mini 權限（設定錯，不是額度）。
3. **ChatGPT 網頁貼取**（股癌專用線）：no valid response（login/timeout）——瀏覽器 session 掉了。
4. **Ollama 地端**：HTTP 500「unexpected EOF」——qwen2.5:14b 在這台機器上跑掛，而且每集要空等 2~4 分鐘才失敗。今天已依 Owner 指令連 caller 一起關（見下）。
→ 結果：摘要退化成 whisper-small 逐字稿直接餵模板，所以出現「誰說：講者待確認」、簡體字漏出（「坚持长期发展策略」）、以及**幻覺級錯誤**（「2026 台灣 GDP 成長率 11%、39 年最高」＝小模型聽錯／編造）。這正對上 8/30 的抱怨：只做標題猜測、股癌摘要沒在重點上。

### 結論一句話
**管線骨架（RSS 偵測＋whisper 逐字稿＋DB＋digest）是好的；死掉的只有「摘要腦」。** 換腦即可，不必砍線。

## 二、同步線狀態（依 msg 4588「不能全停」已恢復）
- 14:5x 依 msg 4578 指令 bootout 了 com.investmentos.influencer-sync-refresh（它是 ollama 的 caller）。
- **15:2x 已重新 enable + bootstrap**，排程回到 02:30/08:30/14:30/21:20，下一輪 21:20。
- 已核對程式碼：sync 只以 HTTP 呼叫 127.0.0.1:11434，**不會自己生出 ollama**；ollama/llama-server 現在不在 → 連線秒拒、秒過，比之前空等 2~4 分鐘還快。ollama 保持關閉。
- 也就是：今晚起同步線照跑（RSS＋whisper＋digest 全在），只是摘要腦缺位，等 hermes 接上。

## 三、hermes 接手方案（待主視窗執行，本檔僅方案，未派工）
1. `sync_influencer_agents.py` 摘要層（get_ollama_summary 那一段 fallback 鏈）改接 **hermes 免費鏈**（OpenRouter :free 四上游、max_tokens ≤ 12000、429 不硬重試）——取代 Gemini/OpenAI/Ollama 三個死腦。
2. 移除 Ollama 分支（或留 env 開關預設關），省掉逾時空轉。
3. Gemini 月額度已爆、OpenAI 403 是權限設定錯——都不用修，直接繞過；ChatGPT 瀏覽器貼取線（股癌專用）要不要救，另問 Owner。
4. 改完先手動跑一輪 influencer-sync-refresh 冒煙，確認 digest 摘要品質（有講者、無簡體、無幻覺數字）再收工。
5. 品質驗收基準＝Owner 8/30 的抱怨清單：勝率表、不只標題猜測、股癌摘要抓重點、產業蛛網消息不漏。

## 四、風險備忘
- Ollama.app 是登入項，重開機可能復活（需 GUI 移除，已在待辦）。
- whisper-small 聽錯專有名詞是幻覺源頭之一；hermes 摘要 prompt 要加「數字與人名需標不確定」護欄。
