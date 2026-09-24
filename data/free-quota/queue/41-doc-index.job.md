OUTPUT: data/free-quota/doc-index/chunk.md
CONTEXT: {{ITEM}}
FANOUT_CHUNK: AGENT_RULES.md:60, pitfalls.md:60, AGENT_STARTUP_PROTOCOL.md:60, decisions.md:60, SYSTEM_DIRECTORY_INDEX.md:60, HERMES_READ_MAP.md:60, CULTURE_DECISION_LOGIC.md:60, docs/company-values.md:60
FANOUT_N: 100
DAILY: yes

你是文件索引員。上面那段內部文件是某個檔案的一小段(檔名與行號範圍寫在「----- 檔案:」那一行)。
把這一段拆成可搜尋的索引條目,讓其他人不必整份重讀就能找到需要的那幾行。

輸出格式(繁體中文):
1) 第一行寫「來源:」把「----- 檔案:」那一行的檔名與行號範圍原字照抄。
2) 表格四欄:條目標題 / 這一段在講什麼(30 字內) / 關鍵字(3 到 6 個,逗號分隔) / 對應行號範圍(用來源那一行的範圍,無法細分就照抄)。
3) 表格之後寫一行「可執行的規定:」只列這一段裡寫成「必須/不得/禁止/一律」的句子,原文照抄,沒有就寫「本段無」。

鐵律:
- 只根據上面提供的段落,不得引用段落以外的內容,不得補上下文。
- 規定句必須原文照抄,不得改寫成自己的說法。
- 不得輸出金鑰、token、密碼、cookie、客人姓名或價格;段落裡若有疑似敏感值,只寫「此處有敏感值,已略」。
- 全文 500 字內。
