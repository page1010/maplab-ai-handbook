#!/usr/bin/env python3
"""Read-only OpenD smoke test (Owner msg 4804). Quote snapshot only —
no trade context, no unlock_trade (GUI-manual only per skill), SIMULATE 環境.
"""
from futu import OpenQuoteContext, RET_OK

ctx = OpenQuoteContext(host="127.0.0.1", port=11111)
try:
    ret, data = ctx.get_market_snapshot(["HK.00700"])
    if ret == RET_OK:
        row = data.iloc[0]
        print(f"SNAPSHOT OK: {row['code']} last_price={row['last_price']} "
              f"update_time={row['update_time']}")
    else:
        print(f"SNAPSHOT FAIL: {data}")
finally:
    ctx.close()
