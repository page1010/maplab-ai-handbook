#!/bin/bash
# 廣告文案閘門的回歸測試:兩份正例必須 PASS,四份反例必須 FAIL。
#
# 由來:閘門(scripts/ad_copy_voice_check.sh)每加一類檢查就要配一份反例測資,
#       否則那一類有沒有真的在跑,沒有人知道。這是缺陷棘輪(企業文化原則 2)。
#
# 2026-09-30 教訓:上一版 runner 用 tail -1 取結果,閘門的 FAIL 尾巴後來多加了
#       兩行提示,tail -1 就抓到提示行而不是計數行,連「測資檔根本不存在(exit=2)」
#       都被蓋掉,看起來像通過。現在改抓 ^PASS:|^FAIL: 並印 exit code。
#
# 用法:bash tests/run_ad_copy_regression.sh
# 回傳:全部符合預期 exit 0,任何一份不符 exit 1。
set -u
cd "$(dirname "$0")/.."

POS="tests/fixtures/ad_copy_after_20260930.txt tests/fixtures/ad_copy_variants_20260930.txt tests/fixtures/ad_carousel_cards_20260930.txt tests/fixtures/ad_video_overlay_20260930.txt"
NEG="tests/fixtures/ad_copy_before_20260930.txt tests/fixtures/ad_copy_promise_bad_20260930.txt tests/fixtures/ad_copy_ctamix_bad_20260930.txt tests/fixtures/ad_copy_brand_bad_20260930.txt"

bad=0
check() {
  f="$1"; want="$2"
  if [ ! -f "$f" ]; then
    echo "MISSING $f ——測資檔不存在,這一類等於沒有在測"
    bad=$((bad + 1))
    return
  fi
  out=$(bash scripts/ad_copy_voice_check.sh "$f" 2>&1)
  rc=$?
  line=$(printf '%s' "$out" | grep -E '^(PASS|FAIL):')
  if [ "$want" = "pass" ] && [ "$rc" -eq 0 ]; then
    echo "OK   $(basename "$f") 正例 exit=0 $line"
  elif [ "$want" = "fail" ] && [ "$rc" -eq 1 ]; then
    echo "OK   $(basename "$f") 反例 exit=1 $line"
  else
    echo "BAD  $(basename "$f") 預期 $want 實際 exit=$rc $line"
    bad=$((bad + 1))
  fi
}

for f in $POS; do check "$f" pass; done
for f in $NEG; do check "$f" fail; done

echo "---"
if [ "$bad" -eq 0 ]; then
  echo "PASS:八份測資全部符合預期"
  exit 0
fi
echo "FAIL:$bad 份不符預期"
exit 1
