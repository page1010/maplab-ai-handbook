#!/bin/bash
# ad_copy_voice_check.sh — 廣告文案「有沒有對客人說話」的機器檢查
#
# 由來:Owner msg 2026-09-30T15:33:34「你文案在敘述場景在敘述你的工作內容,
#       就沒有對我客人好好說話」。前一輪只跑了禁語表掃描就宣稱文案沒問題,
#       禁語表管的是「有沒有講不該講的話」,管不到「有沒有對人說話」——
#       缺了這道檢查,十則裡有十則的主詞都不是客人。
#
# 定位:這是缺陷棘輪(企業文化原則 2)的閘門腳本層,不是清單層。
#       執行層零 LLM,純樣式比對,結果可重現。
#
# 用法:bash scripts/ad_copy_voice_check.sh <文案檔>
#       檔案格式:一行一則文案,空行與 # 開頭的行略過。
# 回傳:全過 exit 0;有任何一則命中 exit 1。
set -u

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "用法:bash scripts/ad_copy_voice_check.sh <文案檔>"
  exit 2
fi

# ① 自家工作流程術語:在講內部怎麼做事,不是在講客人得到什麼
PROCESS='一手規劃|一次交辦|一次到位|一次規劃|一站式|全方位|專業團隊|量身打造|客製化|流程|方案規劃|統籌'

# ② 內部製作文件術語:分鏡表、拍攝腳本誤植進廣告欄位
INTERNAL='前[0-9]+秒|尾板|分鏡|近拍|全景|開場→|→整桌|B-?roll|版位|素材'

# ③ 指向人的詞:一則文案裡完全沒有這類詞,代表整則沒有主體
PERSON='媽媽|爸爸|家人|長輩|兒孫|孩子|寶寶|新人|賓客|來客|主人|同事|行政|窗口|主辦|接待|講者|客人|大家|來的人'

# ④ 純佈景名詞:兩個以上同時出現且整則沒有指向人的詞 = 在描述桌子長什麼樣
PROP='桌巾|層架|金架|鮮花|色系|佈置|擺設|器皿|餐具|花藝'

# ⑤ 做不到的服務承諾(Owner msg 2026-09-30T15:47):
#    「30 分鐘 LINE 回覆」這種話說出去就是承諾。回覆這條線由模型與額度撐著,
#    當機、額度滿、人不在都會讓承諾跳票,而跳票的成本落在客人身上不是落在我們身上。
#    凡是把「多久內一定會怎樣」寫死的,一律擋。
SLA='[0-9]+ *分鐘內|[0-9]+ *小時內|半小時內|當天回覆|當日回覆|馬上回覆|立刻回覆|立即回覆|即時回覆|秒回|隨時回覆|24 *小時|全年無休|不打烊|使命必達|準時送達|保證|一定會|絕對|包您|包你|免費試吃'

# ⑥ 按鈕與文案打架(Owner msg 2026-09-30T16:02):
#    「了解更多」是引流到網頁的按鈕,十則廣告的 CTA 全部是它。
#    文案結尾卻在叫人留言或私訊,等於文字要對話、按鈕導連結,兩邊把人往不同地方推。
#    按鈕是 LEARN_MORE 時,結尾要請人去看頁面,不是請人留言。
CTAMIX='留言|私訊|傳訊|加 *LINE|加我們 *LINE|小盒子|inbox|DM'

fail=0
n=0
while IFS= read -r line; do
  case "$line" in ""|\#*) continue;; esac
  n=$((n + 1))
  msgs=""

  hit=$(printf '%s' "$line" | grep -oE "$PROCESS" | sort -u | tr '\n' ' ')
  if [ -n "$hit" ]; then
    msgs="$msgs
    [工作內容敘述] 命中:$hit"
  fi

  hit=$(printf '%s' "$line" | grep -oE "$INTERNAL" | sort -u | tr '\n' ' ')
  if [ -n "$hit" ]; then
    msgs="$msgs
    [內部文件術語] 命中:$hit"
  fi

  hit=$(printf '%s' "$line" | grep -oE "$SLA" | sort -u | tr '\n' ' ')
  if [ -n "$hit" ]; then
    msgs="$msgs
    [做不到的承諾] 命中:$hit ——回覆速度與到貨時間會因為當機或額度用完跳票,不寫死"
  fi

  hit=$(printf '%s' "$line" | grep -oE "$CTAMIX" | sort -u | tr '\n' ' ')
  if [ -n "$hit" ]; then
    msgs="$msgs
    [按鈕與文案打架] 命中:$hit ——按鈕是「了解更多」會把人帶到網頁,文案不要把人叫回留言區"
  fi

  person=$(printf '%s' "$line" | grep -coE "$PERSON" || true)
  props=$(printf '%s' "$line" | grep -oE "$PROP" | sort -u | wc -l | tr -d ' ')
  if [ "$person" -eq 0 ]; then
    if [ "$props" -ge 2 ]; then
      msgs="$msgs
    [場景敘述] 佈景名詞 $props 個而全篇沒有任何指向人的詞"
    else
      msgs="$msgs
    [沒有主體] 全篇沒有任何指向人的詞"
    fi
  fi

  if [ -n "$msgs" ]; then
    fail=$((fail + 1))
    echo "FAIL 第 $n 則:$line$msgs"
  fi
done < "$FILE"

echo "---"
if [ "$fail" -eq 0 ]; then
  echo "PASS:$n 則全部有對客人說話"
  exit 0
fi
echo "FAIL:$n 則裡有 $fail 則不合格"
echo "改法不是加形容詞,是把主詞換成客人,講那個人當天實際會遇到什麼事。"
echo "命中[做不到的承諾]的,改法是把承諾換成邀請,而邀請要跟按鈕同一個方向。"
echo "命中[按鈕與文案打架]的,改法是把結尾換成請人去看頁面,不是請人留言或私訊。"
exit 1
