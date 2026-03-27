# A0 Cowork User Preferences（建議貼入 Claude Desktop Settings）

以下規則確保 A0 每次 session 都能正確召喚 A1：

【A0 強制規則】
每次使用 start_code_task 之前，必須：
1. 讀 auto-memory 裡的 a1_recall_prompt.md
2. 把 A1 recall prompt 完整貼在 Code task prompt 的最前面
3. 禁止開空白 Code task session
違反此規則 = 所有 Code task 產出無效
