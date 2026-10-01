#!/bin/bash
# ad_copy_gate_regression.sh — 文案閘門的全量回歸,升類之後必跑
#
# 由來:2026-10-01 加第 ⑮ 類時順手跑了全部測資,才發現**昨天**加第 ⑫⑭ 類
#       造成兩份正例測資(ad_copy_after / ad_copy_variants)從 PASS 變 FAIL,
#       掛了一整天沒人看見。原因很單純:升類那一輪只跑了新寫的稿跟新建的反例,
#       沒有回頭跑既有的正例。企業文化原則 12 的「回歸例」章節列了這些檔案,
#       但列在散文裡等於沒有東西在跑它(原則 11 同一個教訓)。
#
# 這支腳本就是那段散文的可執行版本:正例必須 PASS、反例必須 FAIL,
# 任何一份翻面就 exit 1。閘門改完沒跑這支,等於沒改完。
#
# 用法:bash scripts/ad_copy_gate_regression.sh
# 回傳:全部符合預期 exit 0;任何一份翻面 exit 1。
set -u
HB=/Users/pagemacmini/maplab-ai-handbook
G="$HB/scripts/ad_copy_voice_check.sh"
F="$HB/tests/fixtures"

# 必須 PASS 的正例(翻成 FAIL = 閘門誤殺自家合格稿,或新類沒回頭改文案)
POS="ad_copy_after_20260930.txt ad_copy_variants_20260930.txt"
# 必須 FAIL 的反例(翻成 PASS = 對應的類別被改鬆)
NEG="ad_copy_before_20260930.txt \
     ad_copy_promise_bad_20260930.txt \
     ad_copy_ctamix_bad_20260930.txt \
     ad_copy_lack_bad_20260930.txt \
     ad_copy_handoff_bad_20260930.txt \
     ad_copy_downplay_bad_20261001.txt \
     ad_copy_opening_dup_20261001.txt \
     ad_copy_offscope_bad_20261001.txt"
# 交付稿:每一份都必須 PASS(新稿加進來,舊稿不刪——舊稿會在新類上線時翻面,
#         翻面就是要被看見的那件事)
DELIV="$HB/handoff/ADS_COPY_TA_V6_20261001.txt \
       $HB/handoff/zhuazhou_video_overlay_v3_20260930.txt"

rc=0
echo "== 正例(必須 PASS)=="
for p in $POS; do
  if bash "$G" "$F/$p" ad >/dev/null 2>&1; then
    echo "  OK   PASS  $p"
  else
    echo "  翻面 FAIL  $p  <= 這份本來該過"
    bash "$G" "$F/$p" ad 2>&1 | grep -E '^(FAIL 第|\[開頭|\[一個模子)' | sed 's/^/        /'
    rc=1
  fi
done

echo "== 反例(必須 FAIL)=="
for p in $NEG; do
  if bash "$G" "$F/$p" ad >/dev/null 2>&1; then
    echo "  翻面 PASS  $p  <= 對應類別被改鬆了"
    rc=1
  else
    echo "  OK   FAIL  $p"
  fi
done

echo "== 交付稿(必須 PASS)=="
for p in $DELIV; do
  b=$(basename "$p")
  if [ ! -f "$p" ]; then echo "  缺檔       $b"; rc=1; continue; fi
  if bash "$G" "$p" ad >/dev/null 2>&1; then
    echo "  OK   PASS  $b"
  else
    echo "  翻面 FAIL  $b"
    bash "$G" "$p" ad 2>&1 | grep -E '^(FAIL 第|\[開頭|\[一個模子)' | sed 's/^/        /'
    rc=1
  fi
done

echo "---"
if [ "$rc" -eq 0 ]; then
  echo "回歸全綠:正例沒被誤殺、反例沒被改鬆、交付稿仍過閘。"
else
  echo "回歸有翻面。閘門改鬆就改回來;正例被新類擋到就改文案不改閘門(原則 12 第 5 條)。"
fi
exit "$rc"
