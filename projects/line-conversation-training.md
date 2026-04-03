# LINE 對話訓練備份計畫

## 現況
- LINE Webhook 目前只記錄單邊對話（客戶發來的訊息）到 CONVERSATION_LOG
- 不含我方回覆、不含對話上下文
- 資料不足以做 AI 訓練

## 未來計畫（低優先）
- 建立定時抓取備份機制，把完整雙向對話存下來
- 用來訓練客服回覆模型

## 為什麼現在不做
- 需要 LINE Messaging API 的 reply log（目前 Webhook 只推送 incoming）
- 完整雙向紀錄可能需要額外 API 或手動匯出
- Owner 決定以後再做

## 記錄日期
2026-04-03
