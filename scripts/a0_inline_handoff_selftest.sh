#!/bin/bash
# a0_inline_handoff_selftest.sh — 驗 build_remote_role_handoff.py --inline(#111)
#
# 為什麼要有這支:交接包本來把 raw.githubusercontent 連結丟給沒有權杖的外部模型,
# 倉一轉 private 那些連結全部 404。內嵌模式把必讀來源全文直接放進交接包,
# 讓外部執行環境零連外就能冷啟動——這是「四個倉改 private」的前置條件。
# 規範=docs/OPERATING_CULTURE.md 原則 11 的同一條線(不要靠公開暴露換方便)。
set -u
B=/Users/pagemacmini/maplab-ai-handbook/tools/ai_workbook/build_remote_role_handoff.py
OUT=/Users/pagemacmini/maplab-ai-handbook/.work/inline-test
mkdir -p "$OUT"
FAIL=0

echo "=== 1) gemini(無本機檔案系統)應自動內嵌 ==="
/usr/bin/python3 "$B" --role A0 --runtime gemini --task "冷啟動確認現況" --output "$OUT/gemini.md" >/dev/null
wc -c < "$OUT/gemini.md" | tr -d ' ' | sed 's/^/  bytes=/'
if grep -q "6b. 必讀來源全文" "$OUT/gemini.md"; then echo "  OK:有內嵌段"; else echo "  FAIL:沒有內嵌"; FAIL=1; fi
grep "內嵌統計" "$OUT/gemini.md" | sed 's/^/  /'

echo
echo "=== 2) claude_code(有本機檔案系統)不該內嵌 ==="
/usr/bin/python3 "$B" --role A0 --runtime claude_code --task "冷啟動確認現況" --output "$OUT/cc.md" >/dev/null
wc -c < "$OUT/cc.md" | tr -d ' ' | sed 's/^/  bytes=/'
if grep -q "6b. 必讀來源全文" "$OUT/cc.md"; then echo "  FAIL:不該內嵌卻內嵌"; FAIL=1; else echo "  OK:未內嵌"; fi

echo
echo "=== 3) 內嵌版還有沒有連外依賴 ==="
# 要分清楚兩種 raw.githubusercontent:
#  (a) 產生器自己吐出來、叫外部模型去抓的連結 → 這才是「連外依賴」,倉轉 private 就 404。
#  (b) 被內嵌進來的文件「內文」裡提到這個字串 → 那是別人寫的散文,不是依賴。
# 只數 (a):以 6b 內嵌段的標題當分界,分界之前才算產生器自己吐的。
CUT=$(grep -n "^## 6b. 必讀來源全文" "$OUT/gemini.md" | head -1 | cut -d: -f1)
if [ -z "${CUT:-}" ]; then CUT=$(wc -l < "$OUT/gemini.md"); fi
N=$(head -n "$CUT" "$OUT/gemini.md" | grep -c "raw.githubusercontent" || true)
M=$(tail -n "+$CUT" "$OUT/gemini.md" | grep -c "raw.githubusercontent" || true)
echo "  產生器自己吐的連外連結=$N;內嵌文件內文提到=$M(內文不是依賴,但代表文件本身該更新)"
if [ "$N" -eq 0 ]; then echo "  OK:零連外依賴"; else echo "  FAIL:仍有連外連結"; FAIL=1; fi

echo
echo "=== 4) 截斷有沒有誠實標示 ==="
grep -c "\[截斷\]" "$OUT/gemini.md" | sed 's/^/  截斷標示數=/'

echo
echo "=== 5) 預算是否被遵守(always + 小預算 5000) ==="
/usr/bin/python3 "$B" --role A0 --runtime codex --task t --inline always --inline-budget 5000 --output "$OUT/small.md" >/dev/null
S=$(wc -c < "$OUT/small.md" | tr -d ' ')
G=$(wc -c < "$OUT/gemini.md" | tr -d ' ')
echo "  小預算=$S bytes / 預設預算=$G bytes"
if [ "$S" -lt "$G" ]; then echo "  OK:預算真的有作用"; else echo "  FAIL:預算沒作用"; FAIL=1; fi

echo
echo "=== 6) never 模式 ==="
/usr/bin/python3 "$B" --role A0 --runtime gemini --task t --inline never --output "$OUT/never.md" >/dev/null
if grep -q "6b. 必讀來源全文" "$OUT/never.md"; then echo "  FAIL:never 沒生效"; FAIL=1; else echo "  OK:never 生效"; fi

echo
if [ "$FAIL" -eq 0 ]; then echo "SELFTEST PASS"; else echo "SELFTEST FAIL"; fi
exit "$FAIL"
