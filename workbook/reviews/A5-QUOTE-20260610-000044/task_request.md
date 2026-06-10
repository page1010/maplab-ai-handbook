# Task Request

job_id: A5-QUOTE-20260610-000044
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
外帶 范純禎 11/29 下午兩點半 她自己會叫Lalamove來拿 漢堡排45入 蛋沙拉可頌60入 鹹派3個切8 小圓鬆餅120顆 烤布丁60個 她算15885

開始產出草稿與 JSON：
```
