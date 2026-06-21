# Task Request

job_id: A5-QUOTE-20260614-214222
engine: ollama-direct
model: gemma4:latest
thinking: off
status: queued

## Prompt

```text
你是 MAPLAB A5 報價與提案引擎。
請根據使用者的需求，產出一份 Markdown 報價單草稿。
【極端重要】回覆的最後【絕對必須】附上一組合法的 ```json 區塊，不可只回覆「好的」或單一字元。

範例如下：
```json
{
  "action": "createQuote",
  "clientName": "客戶名稱",
  "eventType": "活動類型",
  "headcount": 人數數字,
  "budget": 預算數字,
  "items": [
    {"name": "品項1", "quantity": 數量}
  ]
}
```

使用者的需求：
報價 測試競品菜單 20人 預算50000 比照競爭對手菜單做MAPLAB雷同品項 成本乘以5報價 毛利80%以上

開始產出草稿與 JSON：
```
