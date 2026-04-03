# Skill: summon-role — 召喚角色 SOP

## 觸發條件

Owner 說以下任何形式：
- 「開 A4」「開 A1」「開 A0」（開 + 角色名）
- 「召喚 A3」「召喚 A6」（召喚 + 角色名）
- 「跑 A7」「跑 A2」（跑 + 角色名）
- 任何「開/召喚/跑 + AX（A0～A8）」組合

---

## 召喚路徑一：Code session 召喚（A0 Cowork 開 Code task）

1. 讀 `AGENT_RECALL_PROMPTS.md`
2. 找到目標角色的 `## AX` 段落，取出其下的 ` ``` ` code block 內容
3. 把 code block 內容**原封不動（verbatim）**作為 prompt 傳入 `start_code_task`
   - ⛔ 禁止自己改寫、摘要、或重組 prompt 內容
   - ⛔ 禁止用記憶、對話歷史、或 Task Card 拼湊 prompt
4. session 開啟後前 30 秒讀 transcript，確認角色有輸出正確的 **Startup Check**
5. 如果角色走歪（身份錯誤、略過啟動流程、遺漏任何步驟），立即 `send_message` 糾正

---

## 召喚路徑二：Extension + Chrome tab 召喚

1. 打開 Chrome Extension popup（MAPLAB Agent Commander）
2. 在角色下拉選單選擇對應角色（A0～A8）
3. Extension 自動從 GitHub raw 拉取 `AGENT_RECALL_PROMPTS.md`
   - 使用 `parseRecallPrompts()` 解析 `## AX` 段落下的 code block
   - 將解析結果填入 prompt 文字框
4. 點「複製 Startup Prompt」→ 貼入目標 Claude tab

> Extension 抓取邏輯（popup.js）：
> ```
> regex: /## (A\d)[^\n]*\n[\s\S]*?```\n([\s\S]*?)```/g
> 來源：GitHub raw — AGENT_RECALL_PROMPTS.md（main branch）
> 私有 repo：改用 GitHub Contents API + PAT token（設定於 Extension 儲存）
> ```

---

## 注意事項

| 規則 | 說明 |
|------|------|
| 唯一 prompt 來源 | `AGENT_RECALL_PROMPTS.md` 的 `## AX` code block — 不接受其他來源 |
| 斷點資訊過時沒關係 | 角色開工後會自己讀 `CURRENT_STATUS.md` 確認真實狀態 |
| 不要自己拼 prompt | 即使你「知道」這個角色做什麼，也不能自己寫 prompt |
| 角色的存檔責任 | 每個角色 session 結束前必須更新 `AGENT_RECALL_PROMPTS.md` 自己的段落 |
| 私有 repo 補救 | Extension 抓不到 → 在 popup 設定欄填入 GitHub PAT；或 A0 直接讀本地檔案 |

---

## 給 AI 的說明

收到「開/召喚/跑 + AX」後：
1. 確認目標角色（A0～A8）
2. 判斷當前是 Cowork（路徑一）還是 Extension/Chrome（路徑二）
3. 依對應路徑執行，不要混用
4. 召喚完成後，回報「AX 已開啟，Startup Check 確認正常」或「AX 走歪，已糾正」
