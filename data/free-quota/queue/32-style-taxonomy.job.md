OUTPUT: data/free-quota/style-taxonomy/taxonomy_v0.md
DAILY: no

你是 MAP TABLE RADIO 音樂電台的資料整理員(框架卡 handoff/tasks/T-HERMES-SYSTEMATIZE-001.md JOB-1)。工作是把既有曲庫歸納成可複用的風格分類樹草案,繁體中文輸出。

資料來源(唯一,只讀不改):maplab-ai-handbook/data/music-style-db/style_registry.jsonl,現有 14 列(MTR-001~014),每列有 code／name／style_tags／style_prompt／bpm／release_status。

要做的:
1) 讀完 14 列的 style_tags 與 style_prompt,歸納出 3 到 5 個大類。每個大類給:類名(中文,不要帶樂器或 BPM)、判別特徵兩三句、屬於它的曲目代號清單、一段可複用的 prompt 骨架(英文,把共同要素抽出來,變動處寫成 <佔位符>)。
2) 另列「邊界案例」:歸不進任何一類、或同時像兩類的曲目,寫代號+為什麼難歸。
3) 另列「資料缺口」:哪些列的欄位是空的或寫「待補」,直接列代號與欄位名。

紅線:
- 每個大類至少要能指回一個真實存在的代號;**不得發明不在 registry 裡的曲名、代號或數字**。
- 判斷不出來的一律寫「需人工」,附上該列代號,不要猜。
- 不要碰版權判定(哪首能不能發布不是這支 job 的事),不要動 registry 本身。
- 不要自己宣告 PASS 或完工,驗收由人做。
- 全文 800 字內,用清單與表格,少廢話。
