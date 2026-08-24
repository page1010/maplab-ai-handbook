# Owner Telegram 正常對話 SOP(A0 成功經驗標準化)

版本:v1.0 | 建立:2026-08-24 | Writer:A0/Fable5 | 觸發:任何 agent 要接一條「跟 Owner 像正常人一樣對話」的 Telegram 線(含 Codex cogov、antigravity、hermes 或任何新 bot),動工前先讀本 skill。

> 來源:2026-08-22~24 A0/Fable5 ↔ maplab_claude_bot 實戰驗證(Owner 2026-08-24 核定「做成 sop skill、所有 agent 都要能在指向性導覽讀到」)。反面教材:同日 Codex cogov bot 沉默不回覆審查 `investment-os/reports/codex_runs/CODEX_BOT_REVIEW_20260824_SILENT_DROPS.md`。

---

## 零、驗收標準(一句話)

**Owner 發出的每一則訊息,無論 agent 在不在線,都在可預期時間內得到一則有標示來源的回覆;agent 離線也不斷線、上線後不換腦。**

---

## 一、五個必備元件(缺一即會出現「說話沒人回」)

### 1. Inbox 落檔(append-only,收訊與回覆解耦)
- bot 收到 Owner 任何入站,**先寫一行 jsonl 再說**:`{ts, chat_id, text, message_id, source}`。
- 範本:`claude-daily-operations/state/a0_inbox.jsonl`(寫入點在 maplab bot.py 的入站分接)。
- 目的:agent 離線時訊息不丟;上線後 diff 即知欠了誰的回覆。
- 陷阱(Codex 實錄):只讀 `message.text` 會把圖片/檔案的 caption 整則吃掉——**text 與 caption 都要讀**,兩者皆空至少回「收到附件但讀不到內容,請補一句文字」。

### 2. 收據式回覆(回了才算回)
- agent 回覆一律走 reply 腳本,**同時發 Telegram + 落收據**:`{ts, reply_to_inbox_ts, message_id, output_hash, len}` → `a0_replies.jsonl`。
- 範本:`maplab-ai-handbook/scripts/a0_reply.sh "<text>" [reply_to_inbox_ts]`(位置參數,不是旗標;內文禁反引號)。
- 「未回覆」的定義由此可機器判定:inbox 有、replies 無對應 `reply_to_inbox_ts`。
- **每一則 Owner 訊息都要回,哪怕一句「收到」。**

### 3. 先 ACK 再開工
- 收到派工,第一動作是回「收到,開工了」(附任務代號更好),**然後**才開始跑。
- 跑完再回成品或進度。長任務中途要有進度訊息,不能一潛就是幾小時。
- Owner 原話:「假設開工了也要跟我說有收到去開工了吧」。

### 4. 永不沉默 fallback:同 session 續接(本 SOP 的核心發明)
- bot 送出 Owner 訊息後等收據(maplab 線 150s);逾時則 bot 自己執行
  `claude -p --resume <固定 session id> --output-format text`,把該 turn 的**最終文字輸出**加標籤後轉送 Owner。
- 關鍵:**resume 同一個 session,不是開新 context**——人格、記憶、未完成事項全部延續;handoff 檔頂部維護 RESUME PROMPT 作為單一真相源(範本 `claude-daily-operations/state/FABLE5_HANDOFF.md`)。
- 續接 turn 的鐵律:先 git pull、讀 RESUME PROMPT、diff inbox/replies、只回當則;**不得宣稱已派工、已稽核或已完成任何實際上還沒做的事**。
- resume 也失敗才落到 bot 罐頭代答,且必須標示(見元件 5)。

### 5. 來源標示(Owner 永遠知道在跟誰說話)
- 【<agent> 本人】= agent 主程式親答;【<agent> 本人・同 session 續接】= fallback 續接;【bot 代答】= 罐頭。
- 說人話三段式:發生什麼/對你的意義/要不要你做。不發收據式流水帳給 Owner。

---

## 二、群組接入(Codex 沉默事件的教訓,依嚴重度)

1. **privacy mode 是 root cause**:bot 隱私模式開啟時,群組內純文字 @提及**根本不會投遞**給 bot(只投斜線指令與對 bot 的 reply)。修法是 Telegram 操作不是程式:請 Owner 把 bot 設為**群組管理員**(推薦),或 BotFather /setprivacy Disable。程式碼改再多都救不了沒送達的訊息。
2. 群組解析不要只認斜線指令:含 @bot 提及的自然語言 → 視同派工;非提及的一般群聊維持靜默。
3. 空指令(如 /research 後面沒題目)不要死路:記 pending 狀態,同 chat 120 秒內下一則純文字自動接為題目。
4. DM 純文字不要回語法教學罐頭:Owner-only 的線,DM 說話就是派工,直接 ACK + 開工。
5. Owner 若開群組匿名發言,sender 會變 GroupAnonymousBot——owner 過濾要考慮 `sender_chat`。
6. 所有 ignore/handle 決策 log 要帶 timestamp,否則除錯只能靠心跳夾擠。

---

## 三、新 agent 接線 checklist

- [ ] BotFather 建 bot(或沿用),token 走 secrets-from-notion-vault 規則,**不入 repo、不貼給其他 agent**
- [ ] 入站分接 → `state/<agent>_inbox.jsonl`(text+caption 都讀)
- [ ] reply 腳本 + `state/<agent>_replies.jsonl` 收據
- [ ] 逾時 fallback → resume 固定 session(或該 runtime 的等價續接機制),標籤標示
- [ ] handoff 檔 + RESUME PROMPT,last-writer 勝 + timestamp
- [ ] 群組要用的話:bot 設群管理員 / privacy off + 提及即派工
- [ ] 驗收:Owner 連發 5 則(含 1 張帶 caption 的圖、1 則群組 @提及、1 則 agent 離線時發的),5/5 在時限內收到有標示的回覆

## 邊界

- 鑰匙/token/cookie 一律不入本 repo、不入 Design、不貼進 inbox;走 vault 或 Owner 直貼對應 runtime。
- 本 SOP 管「對話不斷線」,不改變各角色的能力邊界(金流、下單、發布仍走原 gate)。
