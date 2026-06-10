# Task Request

job_id: A5-QUOTE-20260610-000345
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
報價 張雅淳 證婚儀式 70-80人 Candy bar 19800 3/22 下午一點到四點半 王老爹的開心農場 只要甜點不要鹹食

開始產出草稿與 JSON：
```
