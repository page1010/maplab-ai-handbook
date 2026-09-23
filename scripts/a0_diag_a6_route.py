#!/usr/bin/env python3
"""診斷用:重放某筆 A6-HERMES-TASKS 的 request,印出 gateway 路由判定。

只讀 task.json、只做純函式判定,不連 Telegram、不呼叫任何 provider。
用法:python3 scripts/a0_diag_a6_route.py <TASK_ID>
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "bot_a6"))

import hermes_telegram_gateway as gw  # noqa: E402
from hermes_task_executor import classify  # noqa: E402

task_id = sys.argv[1] if len(sys.argv) > 1 else ""
task_file = REPO / "workbook" / "reviews" / "A6-HERMES-TASKS" / task_id / "task.json"
text = json.loads(task_file.read_text(encoding="utf-8"))["request"]

print("chars:", len(text))
print("SEO_CUSTOMER_SEND_RE:", bool(gw.SEO_CUSTOMER_SEND_RE.search(text)))
print("classify:", classify(text))
print("PROVIDER_PRIVATE_RE:", bool(gw.PROVIDER_PRIVATE_RE.search(text)))
hit = gw.PROVIDER_PRIVATE_RE.search(text)
if hit:
    print("PROVIDER_PRIVATE_RE hit:", hit.group(0))
route = gw.route_gateway_text(text)
print("disposition:", route.disposition, "| reason:", route.reason)
