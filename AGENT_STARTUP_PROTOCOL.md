# AGENT_STARTUP_PROTOCOL.md — 接手前必讀 SOP

**所有 Agent 開始任務前，必須依序完成以下步驟。**

這份文件的目的是解決「每個 Agent 一開始沒有大局觀」的問題。

---

## 啟動前必讀清單（9 步驟）

**Step 1.** 閱讀 README.md
確認：系統使命是什麼、這個系統為什麼存在、成功的定義是什麼

**Step 2.** 閱讀 CURRENT_EXECUTION_BOARD.md
確認：系統當前階段、各 Agent 即時狀態、Active Session 有沒有人佔住你要改的檔案

> ⚠️ 若 Active Session 中有其他 Agent 正在修改你需要的檔案 → 等待或換任務，不要同時編輯。

**Step 3.** 閱讀 AI_WORKFLOW_MAP.md
確認：Claude/GPT/Gemini 各自的分工、自己在任務流程的位置、交接規則（含 Rule 6 簽到簽退、Rule 7 檔案衝突檢查）

**Step 4.** 閱讀 AGENT_RULES.md
確認：自己的角色編號（A1-A7）、負責任務範圍、禁止事項

**Step 5.** 閱讀對應的 projects/ 專案文件
確認：該專案目前版本、最後一次更新了什麼、下一步是什麼

**Step 6.** 閱讀 skills/superpowers-guide.md
確認：可用的技能工具箱，查「任務類型 → 建議預讀技能書」路由表，選擇最適合當前任務的技能

**Step 7.** 閱讀最新的 handoff/ 文件
確認：上一個 Agent 做了什麼、遺留了什麼問題、阻塞點在哪

**Step 8.** 閱讀 CHANGELOG.md
確認：系統目前版本、最近的重大變更

**Step 9.** 在 CURRENT_EXECUTION_BOARD.md 的 Active Session 簽到
登記：你的 Agent 編號 / 開始時間 / 正在修改的檔案 / 預計完成項目

---

## 確認後才能開始執行

完成以上 9 步驟後，你應該能回答以下問題：

- 我是誰？（角色編號 + 職責）
- 我要做什麼？（具體任務）
- 我不能做什麼？（禁止事項）
- 上一個 Agent 做到哪裡了？
- 我完成後要交接什麼？
- 有沒有其他 Agent 正在改我要碰的檔案？

如果無法回答其中任何一個問題，回報給 owner 後再開始。

---

## 執行中卡住怎麼辦？

**不要浪費 context 亂試。** 依以下順序處理：

1. 嘗試 1-2 次自行修復
2. 修不好 → 查 skills/troubleshooting-hub.md（症狀 → 解法 → 技能書）
3. 找到解法 → 照技能書做 → 繼續執行
4. 找不到解法 → 用 hub 內的回報格式記錄問題 → 回報 A1 或 owner
5. A1 補充到 hub → 下次所有 Agent 都能查到

> 重點：troubleshooting-hub.md 是你的急救手冊，不是額外負擔。

---

## 完成任務後的收尾 SOP

**Step A.** 清除 CURRENT_EXECUTION_BOARD.md 的 Active Session 簽到（刪除你的簽到行）
**Step B.** 在 CURRENT_EXECUTION_BOARD.md 的 Session Log 新增一條記錄（誰 / 何時 / 做了什麼 / 改了哪些檔案 / 未完成什麼）
**Step C.** 更新對應 projects/ 文件的狀態欄位（版本號 + 狀態）
**Step D.** 填寫 handoff/HANDOFF_TEMPLATE.md（完成了什麼、下一步是什麼、阻塞點）
**Step E.** 更新 CHANGELOG.md（新增一條版本記錄）
**Step F.** 若新增了 projects/*.md，必須同步更新 AGENT_RULES.md SECTION 1 角色表
**Step G.** 回報 owner：完成摘要 + 需要 owner 決策的事項

---

## 關鍵約束（每次接手前確認）

- .env 金鑰、token、密碼 **絕對不能** 上傳 GitHub
- Google Photos 原始照片 **只讀不刪**
- 不修改 main branch schema without changelog
- Notion 是人工快照，GitHub commit 是唯一狀態真相
- 不假設任務範圍，有疑問先確認

---

*版本：v1.1 | 建立：2026-03-14 | 更新：2026-03-18 | 維護者：A1 Handbook Agent*
