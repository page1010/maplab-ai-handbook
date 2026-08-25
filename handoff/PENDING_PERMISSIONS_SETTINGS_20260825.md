# 待套用:relay 視窗權限白名單(解決腳本推送 + A6 啟動)

- 建立:2026-08-25|作者:A0/Fable5|背景:bot 續接的無頭視窗白名單外指令自動拒絕,連本設定檔也不允許視窗自己改(防自我加權)。
- 目標檔:/Users/pagemacmini/Documents/.claude/settings.local.json
- 誰能套用:①Codex/dispatch(有自己的執行權限)②任何互動 Claude 視窗(人按允許)。套用後,之後新開的 relay 視窗即可自己發收據、自己啟動 A6 hermes 閘道。

## 套用方式

把目標檔整份換成下面內容(前 13 條 MCP 是原有的,一條都不能少;後面是新增):

```json
{
  "permissions": {
    "allow": [
      "mcp__Desktop_Commander__read_file",
      "mcp__Desktop_Commander__list_directory",
      "mcp__Desktop_Commander__start_search",
      "mcp__Desktop_Commander__start_process",
      "mcp__Desktop_Commander__edit_block",
      "mcp__Claude_in_Chrome__read_page",
      "mcp__Claude_in_Chrome__navigate",
      "mcp__Claude_in_Chrome__find",
      "mcp__Claude_in_Chrome__get_page_text",
      "mcp__Claude_in_Chrome__browser_batch",
      "mcp__Desktop_Commander__write_file",
      "mcp__Claude_in_Chrome__tabs_context_mcp",
      "mcp__Claude_in_Chrome__javascript_tool",
      "Bash(bash /Users/pagemacmini/maplab-ai-handbook/scripts/a0_reply.sh:*)",
      "Bash(bash /Users/pagemacmini/maplab-ai-handbook/scripts/a0_reply_from_file.sh:*)",
      "Bash(bash /Users/pagemacmini/maplab-ai-handbook/scripts/notify_group.sh:*)",
      "Bash(/Users/pagemacmini/maplab-ai-handbook/scripts/a0_reply.sh:*)",
      "Bash(/Users/pagemacmini/maplab-ai-handbook/scripts/a0_reply_from_file.sh:*)",
      "Bash(/Users/pagemacmini/maplab-ai-handbook/scripts/notify_group.sh:*)",
      "Bash(kill 1068)",
      "Bash(pkill -f bot_a6/bot_a6.py)",
      "Bash(/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python3 -m py_compile:*)"
    ]
  }
}
```

改完驗證:jq . /Users/pagemacmini/Documents/.claude/settings.local.json 必須成功輸出(JSON 合法)。

## 順手一起做(A6 hermes 視窗啟動,見 PENDING_A6_HERMES_ACTIVATION_20260825.md)

1. kill 1068(舊 bot_a6.py 殭屍;launchd KeepAlive 30 秒內用新 run_daemon.sh 重生=直接跑 hermes 閘道)。PID 變了就 pkill -f "bot_a6/bot_a6.py"。
2. 驗證 bot_a6/hermes_gateway.log 出現 hermes gateway start 且 openrouter_key=yes;Owner 對 A6 bot 發 /start 應回【hermes】。
3. 完成後把兩張 PENDING 卡狀態改「已套用/已啟動+時間」。

## 邊界

- 只加上面列的白名單,不加其他 Bash 權限;不動 deny 規則;金鑰照舊不進對話不進 git。
