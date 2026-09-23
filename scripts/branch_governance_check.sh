#!/usr/bin/env bash
# branch_governance_check.sh — 分支治理的體檢表,一次掃四個 repo。
#
# 為什麼有這支(Owner msg 6021 → 6049):
#   6021 問「所有分支不就沒有一個確定版本…沒有一個角色來檢查」,當時的結論是
#   「缺的是整合官這個角色」,然後就寫進 #72 卡在那裡。6049 再問一次「有人管了嗎」。
#   ⭐ 設一個沒人來當的角色 = 沒有管。所以這輪把整合官該做的那份「每週掃一次」
#   改成程式:角色可以缺席,腳本不會。這是制度 E 的 L1(筆記)→ L3(擋在路上)。
#
# 它只回答三個問題,每個都給數字:
#   1. 有幾條分支,其中幾條已經超過 30 天沒人動(= 該封成 tag 的候選)
#   2. 出貨線(main)跟真正在做事的那條差多少個 commit(分岔數,0/0 才叫收斂)
#   3. 有多少檔案根本沒進版控(= 凡走過必留下痕跡當下是破的)
#
# 用法: bash scripts/branch_governance_check.sh
# 退出碼: 0 = 四個 repo 全部收斂且無老分支 / 1 = 至少一項不合格(細節看輸出)

set -uo pipefail

CUTOFF=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d '30 days ago' +%Y-%m-%d)
RC=0

echo "== 分支治理體檢($(date +%Y-%m-%d),老分支門檻=$CUTOFF 之前沒動過) =="
echo

# $1=repo 路徑  $2=出貨線  $3=實際做事那條(空=只有一條線)
check_repo () {
  local dir="$1" ship="$2" work="${3:-}"
  local name; name=$(basename "$dir")
  echo "--- $name"
  if [ ! -d "$dir/.git" ]; then
    echo "  (查無 $dir,略過)"
    echo
    return
  fi

  local total stale
  total=$(git -C "$dir" for-each-ref --format='%(refname:short)' refs/remotes/origin | wc -l | tr -d ' ')
  stale=$(git -C "$dir" for-each-ref --format='%(committerdate:short)' refs/remotes/origin \
          | while read -r d; do [ "$d" \< "$CUTOFF" ] && echo x; done | wc -l | tr -d ' ')
  echo "  遠端分支:${total} 條;其中 ${stale} 條超過 30 天沒人動"
  if [ "${stale:-0}" -gt 0 ]; then
    echo "  ✗ 有老分支沒收:到期該封成 tag 保留痕跡,不是放著也不是刪掉"
    RC=1
  fi

  if [ -n "$work" ]; then
    local div
    div=$(git -C "$dir" rev-list --left-right --count "origin/${ship}...origin/${work}" 2>/dev/null)
    if [ -n "$div" ]; then
      echo "  分岔 ${ship} vs ${work}:${div}(左=main 獨有,右=工作線獨有;0 0 才叫收斂)"
      case "$div" in
        "0	0") : ;;
        *) echo "  ✗ 未收斂:今天要出貨,這兩條沒有一條是完整版本"; RC=1 ;;
      esac
    fi
  fi

  local dirty untracked
  dirty=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  untracked=$(git -C "$dir" ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
  echo "  工作區:${dirty} 檔有異動,其中 ${untracked} 檔從未進版控"
  if [ "${untracked:-0}" -gt 50 ]; then
    echo "  ✗ 大量檔案只存在於這台硬碟:沒有第二份,機器壞了就沒了"
    RC=1
  fi
  echo
}

check_repo "$HOME/maplab-ai-handbook"        main chore/agent-login-governance-20260816
check_repo "$HOME/investment-os"             main research/markyang-finance-20260911
check_repo "$HOME/claude-daily-operations"   main ops/relocate-register-20260803
check_repo "$HOME/agent-bus"                 main

# 分支名寫死在腳本裡 = 日常工作被綁在一條分支上,搬不回 main
echo "--- 把分支名寫死的腳本(這些不改,日常就搬不回 main)"
grep -rln "chore/agent-login-governance-20260816" "$HOME/maplab-ai-handbook/scripts" 2>/dev/null | sed 's/^/  /'
n=$(grep -rln "chore/agent-login-governance-20260816" "$HOME/maplab-ai-handbook/scripts" 2>/dev/null | wc -l | tr -d ' ')
if [ "${n:-0}" -gt 0 ]; then
  echo "  ✗ 還有 ${n} 支寫死分支名"
  RC=1
fi
echo

if [ "$RC" = "0" ]; then
  echo "== 結論:四個 repo 都收斂,沒有老分支,沒有未進版控的檔案 =="
else
  echo "== 結論:上面標 ✗ 的就是還沒有人管的部分 =="
fi
exit $RC
