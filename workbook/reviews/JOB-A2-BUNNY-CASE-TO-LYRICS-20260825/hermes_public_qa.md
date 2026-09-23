# Hermes public-only QA receipt

## Dispatch

- Payload：只有 `wp_draft.md` 的預計公開文字。
- 未送：Drive 路徑／ID、客戶姓名與聯絡資料、地址、報價、原始素材、repo 私有治理內容。
- Task：獨立判斷搜尋意圖、關鍵字自然度、內部工程語言、過度推論與最多三個修正；不得發布。

## Result

`QA_NOT_ACCEPTED`

- 第一個免費候選在時限內無可讀回覆。
- Ox Alpha 回空結果。
- Nemotron 回傳的是分析過程而非要求的五行 final，且在有效結論前被截斷；不能冒充 QA 完成。
- 兩個 Gemma 候選回 HTTP error。

## Governance decision

Hermes 可以接公開、可丟棄的粗查工作，但本輪免費鏈品質／可用性不足，沒有任何文章修改以 Hermes 回覆為依據。A2 live REST checker 與主流程人工查證仍是本案 judgment gate。下一次要把 Hermes 用在判斷工作前，先做一個固定 JSON output 的 capability probe；不通就把它降級為摘要／格式化，不讓它卡住交付。
