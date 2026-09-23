#!/usr/bin/env bash
# check_rubric_ssot_selftest.sh — 驗「禁語表單一真相」這條 L3 真的生效
#
# 背景(Owner msg 5961:「卡片自己互打是你們存檔的治理問題,你應該設法解決而非推脫卸責」):
#   2026-09-23 之前,同一件事有三份檔在講三種話——
#     seo-voice-rules-20260905.md R3 要求必放「賓主盡歡」;
#     SEO_COPY_RUBRIC.md 禁語表根本沒有這個詞;
#     check_rubric.py 第 8 行硬編的 BAN 卻在擋它(還偷加了「動線」「琳瑯滿目」)。
#   而審稿清單對 Owner 寫的是「rubric 明文禁用」——一個不存在的條文被當成事實上呈。
#   改法:禁語表只留在 SEO_COPY_RUBRIC.md 的 BANNED_PHRASES 標記之間,
#         check_rubric.py 執行時去讀,程式內不留硬編。改規範=改執法。
#
# 這支驗四件事:
#   A 禁語命中要 FAIL(「賓主盡歡」現在在表上,必須擋)
#   B 乾淨文字要 PASS(沒有誤殺)
#   C 標記被刪 -> 必須 FATAL 退出,不得以空表安靜放行(fail-closed 的核心)
#   D 規範檔不存在 -> 必須 FATAL 退出
set -uo pipefail

BUS="/Users/pagemacmini/agent-bus"
TOOL="$BUS/drafts/win-01/tools/check_rubric.py"
RUBRIC="$BUS/shared/seo/SEO_COPY_RUBRIC.md"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
ok()  { echo "  ✓ $1"; pass=$((pass+1)); }
ng()  { echo "  ✗ $1"; fail=$((fail+1)); }

echo "=== A 禁語命中要被擋 ==="
printf '餐檯靠牆擺,客人從左側取餐。\n這句故意寫賓主盡歡,必須被擋。\n' > "$TMP/a.txt"
/usr/bin/python3 "$TOOL" "$TMP/a.txt" "$TMP/a.rep" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 1 ] && grep -q "賓主盡歡" "$TMP/a.rep" 2>/dev/null; then
  ok "exit=1 且報告指名「賓主盡歡」"
else
  ng "exit=$rc,報告內容:$(cat "$TMP/a.rep" 2>/dev/null | tr '\n' ' ')"
fi

echo "=== B 乾淨文字不得誤殺 ==="
printf '餐檯靠牆擺,客人從左側取餐,現場由兩位同仁補菜。\n' > "$TMP/b.txt"
/usr/bin/python3 "$TOOL" "$TMP/b.txt" "$TMP/b.rep" >/dev/null 2>&1
rc=$?
[ "$rc" -eq 0 ] && ok "exit=0 未誤殺" || ng "exit=$rc(誤殺,報告:$(cat "$TMP/b.rep" 2>/dev/null | tr '\n' ' '))"

echo "=== C 標記被刪 -> 必須 FATAL,不得空表放行 ==="
cp "$RUBRIC" "$TMP/rubric.bak"
/usr/bin/sed -i '' 's/BANNED_PHRASES_START/BANNED_PHRASES_XXXXX/' "$RUBRIC"
out="$(/usr/bin/python3 "$TOOL" "$TMP/a.txt" "$TMP/c.rep" 2>&1)"
rc=$?
cp "$TMP/rubric.bak" "$RUBRIC"   # 立刻還原,不留破壞
if [ "$rc" -ne 0 ] && printf '%s' "$out" | grep -q "FATAL"; then
  ok "exit=$rc 且輸出含 FATAL(fail-closed 成立)"
else
  ng "exit=$rc 輸出=$out — 標記不見了竟然還放行,這就是最危險的狀況"
fi
if diff -q "$TMP/rubric.bak" "$RUBRIC" >/dev/null; then
  ok "規範檔已還原,無殘留破壞"
else
  ng "規範檔未還原,請手動比對 $TMP/rubric.bak"
fi

echo "=== D 規範檔不存在 -> 必須 FATAL ==="
mv "$RUBRIC" "$TMP/rubric.moved"
out="$(/usr/bin/python3 "$TOOL" "$TMP/a.txt" "$TMP/d.rep" 2>&1)"
rc=$?
mv "$TMP/rubric.moved" "$RUBRIC"
if [ "$rc" -ne 0 ] && printf '%s' "$out" | grep -q "FATAL"; then
  ok "exit=$rc 且輸出含 FATAL"
else
  ng "exit=$rc 輸出=$out"
fi
[ -f "$RUBRIC" ] && ok "規範檔已歸位" || ng "規範檔沒歸位!在 $TMP/rubric.moved"

echo
echo "通過 $pass / 失敗 $fail"
[ "$fail" -eq 0 ] || exit 1
echo "✓ 禁語表單一真相 L3 生效:改 SEO_COPY_RUBRIC.md 就等於改執法,兩邊不可能再互打。"
