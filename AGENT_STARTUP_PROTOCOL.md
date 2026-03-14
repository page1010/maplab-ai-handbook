# AGENT_STARTUP_PROTOCOL.md — 接手前必讀 SOP

**所有 Agent 開始任務前，必須依序完成以下步驟。**

這份文件的目的是解決「每個 Agent 一開始沒有大局觀」的問題。

---

## 啟動前必讀清單（8 步驟）

**Step 1.** 閱讀 README.md
確認：系統使命是什麼、這個系統為什麼存在、成功的定義是什麼

**Step 2.** 閱讀 PROJECT_CONTEXT.md
確認：目前有哪些專案、每個專案的狀態、專案間的依賴關係

**Step 3.** 閱讀 AI_WORKFLOW_MAP.md
確認：Claude/GPT/Gemini 各自的分工、自己在任務流程的位置、交接規則

**Step 4.** 閱讀 AGENT_RULES.md
確認：自己的角色編號（A1-A7）、負責任務範圍、禁止事項

**Step 5.** 閱讀對應的 projects/ 專案文件
確認：該專案目前版本、最後一次更新了什麼、下一步是什麼

**Step 6.** 閱讀 skills/superpowers-guide.md
確認：可用的 13 項技能工具箱，選擇最適合當前任務的技能

**Step 7.** 閱讀最新的 handoff/ 文件
確認：上一個 Agent 做了什麼、遺留了什麼問題、阻塞點在哪

**Step 8.** 閱讀 CHANGELOG.md
確認：系統目前版本、最近的重大變更

---

## 確認後才能開始執行

完成以上 8 步驟後，你應該能回答以下問題：

- 我是誰？（角色編號 + 職責）
- 我要做什麼？（具體任務）
- 我不能做什麼？（禁止事項）
- 上一個 Agent 做到哪裡了？
- 我完成後要交接什麼？

如果無法回答其中任何一個問題，回報給 owner 後再開始。

---

## 完成任務後的收尾 SOP

**Step A.** 更新對應 projects/ 文件的狀態欄位（版本號 + 狀態）

**Step B.** 填寫 handoff/HANDOFF_TEMPLATE.md（完成了什麼、下一步是什麼、阻塞點）

**Step C.** 更新 CHANGELOG.md（新增一條版本記錄）

**Step D.** 若新增了 projects/*.md，必須同步更新 AGENT_RULES.md SECTION 1 角色表

**Step E.** 回報 owner：完成摘要 + 需要 owner 決策的事項

---

## 關鍵約束（每次接手前確認）

- .env 金鑰、token、密碼 **絕對不能** 上傳 GitHub
- Google Photos 原始照片 **只讀不刪**
- 不修改 main branch schema without changelog
- Notion 是人工快照，GitHub commit 是唯一狀態真相
- 不假設任務範圍，有疑問先確認

---

*版本：v1.0 | 建立：2026-03-14 | 維護者：A1 Handbook Agent*
