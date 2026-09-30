#!/bin/bash
# ad_image_scene_check.sh — 廣告「圖片是不是佈景特寫」的機器檢查
#
# 由來:Owner msg 2026-09-30T16:58:50「０６b4金架 鮮花 改掉 品牌用語
#       不要這種敘事 應該有教過 描述一個場景使用者感受與情境的美好」。
#       這一輪查下去,金架與鮮花根本不在文案裡——文案早就改過了、
#       而且 ad_copy_voice_check.sh 全綠。字詞是在「圖」裡:
#       06 三張卡分別是金色層架、白色蕾絲桌巾配金色層架、金盤金架,
#       正好就是企業文化原則 12 第 388 行列的兩個負面例子本身。
#
# 缺口:文案閘門一個字都看不到圖。文案改成對客人說話、圖還在拍桌子,
#       整則廣告的敘事就還是佈景敘事。閘門全綠不等於廣告沒問題。
#
# 定位:缺陷棘輪(原則 2)閘門腳本層。執行層零 LLM,純樣式比對。
#       「這張圖是什麼」無法由程式判讀,所以判讀結果由人看過之後寫進
#       清單,程式負責強制「每張圖都要有人看過、而且不准整則都是佈景特寫」。
#
# 用法:bash scripts/ad_image_scene_check.sh <清單檔>
# 清單格式(TSV,# 開頭略過):廣告代號 <TAB> image_hash <TAB> 標記 <TAB> 看過日期 <TAB> 來源檔名
# 標記僅三種:
#   scene       整個場合看得出來在哪裡、發生什麼事
#   has-person  畫面裡有人(最強,一則有一張就夠)
#   prop        佈景或食物特寫,看不出場合
# 回傳:全過 exit 0;任一條不合格 exit 1。
set -u

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "用法:bash scripts/ad_image_scene_check.sh <清單檔>"
  exit 2
fi

fail=0
rows=0

# ① 標記合法、欄位齊全、看過日期存在
while IFS=$'\t' read -r ad hash tag seen src; do
  case "${ad:-}" in ""|\#*) continue;; esac
  rows=$((rows + 1))
  if [ -z "${hash:-}" ] || [ -z "${tag:-}" ] || [ -z "${seen:-}" ] || [ -z "${src:-}" ]; then
    echo "FAIL $ad $hash:欄位不齊(hash/標記/看過日期/來源檔名 四欄都要有)"
    fail=$((fail + 1)); continue
  fi
  case "$tag" in
    scene|has-person|prop) ;;
    *) echo "FAIL ${ad} ${hash}:標記「${tag}」不合法,只能是 scene / has-person / prop"
       fail=$((fail + 1));;
  esac
  case "$seen" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;;
    *) echo "FAIL ${ad} ${hash}:看過日期「${seen}」不是 YYYY-MM-DD——沒有人真的開圖看過就不准上"
       fail=$((fail + 1));;
  esac
done < "$FILE"

# ② 同一個 hash 被兩則以上廣告共用 = 兩則廣告在放同一張照片
dups=$(grep -v '^#' "$FILE" | awk -F'\t' 'NF>=2 && $2!=""{print $2}' | sort | uniq -d)
if [ -n "$dups" ]; then
  for h in $dups; do
    who=$(grep -v '^#' "$FILE" | awk -F'\t' -v h="$h" '$2==h{printf "%s ", $1}')
    echo "FAIL 圖片 ${h} 同時掛在:${who}——不同檔期的廣告不該放同一張照片"
    fail=$((fail + 1))
  done
fi

# ③ 整則廣告的圖全部是 prop = 這則廣告在拍桌子,沒有在講一個場合
ads=$(grep -v '^#' "$FILE" | awk -F'\t' 'NF>=3 && $1!=""{print $1}' | sort -u)
for a in $ads; do
  total=$(grep -v '^#' "$FILE" | awk -F'\t' -v a="$a" '$1==a{c++} END{print c+0}')
  props=$(grep -v '^#' "$FILE" | awk -F'\t' -v a="$a" '$1==a && $3=="prop"{c++} END{print c+0}')
  if [ "$total" -gt 0 ] && [ "$total" -eq "$props" ]; then
    echo "FAIL $a:$total 張圖全部是佈景特寫,整則廣告沒有一張看得出場合"
    fail=$((fail + 1))
  fi
done

echo "---"
if [ "$fail" -eq 0 ]; then
  echo "PASS:$rows 張圖全部有人看過、沒有共用、每則都有看得出場合的畫面"
  exit 0
fi
echo "FAIL:$rows 張圖裡有 $fail 條不合格"
echo "改法不是換文案,是換圖。文案講客人、圖還在拍金架鮮花,整則還是佈景敘事。"
exit 1
