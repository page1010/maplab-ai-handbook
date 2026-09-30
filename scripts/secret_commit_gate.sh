#!/bin/bash
# secret_commit_gate.sh — 阻止把憑證 commit 進版控的閘門(只印檔名行號與樣式名,絕不印值)
#
# 背景(2026-09-30):本倉在 GitHub 是公開的(匿名 curl 回 200),而 scripts/ 底下有 20 支
# 音樂線腳本把 Telegram bot 權杖寫死在原始碼裡。這些檔目前全部 untracked、也沒被
# .gitignore 蓋到,所以一次 `git add -A` 就會把 Owner 的 bot 權杖推上公開倉。
# 這支閘門把「靠自律不要 add -A」換成「機器擋」。
#
# 用法:
#   bash scripts/secret_commit_gate.sh              # 檢查已 staged 的檔(pre-commit 用)
#   bash scripts/secret_commit_gate.sh --all        # 掃全部已追蹤檔(稽核用)
#   bash scripts/secret_commit_gate.sh --install    # 裝成本倉 .git/hooks/pre-commit
# 退出碼:0=乾淨 1=命中(擋下)
set -u
# 倉庫位置由本腳本自身路徑推出,不看呼叫者的工作目錄(bot 的工作目錄不在倉內)
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO" ]; then echo "不在 git 倉裡:$HERE"; exit 2; fi

if [ "${1:-}" = "--install" ]; then
  H="$REPO/.git/hooks/pre-commit"
  printf '%s\n' '#!/bin/bash' 'exec bash "$(git rev-parse --show-toplevel)/scripts/secret_commit_gate.sh"' > "$H"
  chmod +x "$H"
  echo "已裝 pre-commit -> $H"
  exit 0
fi

if [ "${1:-}" = "--all" ]; then
  FILES=$(git -C "$REPO" ls-files)
else
  FILES=$(git -C "$REPO" diff --cached --name-only --diff-filter=ACM)
fi
[ -z "$FILES" ] && { echo "沒有要檢查的檔"; exit 0; }

# 一次 grep 掃完所有樣式(4000+ 檔逐檔逐樣式跑會慢到不能當 pre-commit 用)
RE='[0-9]{8,12}:AA[A-Za-z0-9_-]{30,}|EAA[A-Za-z0-9]{40,}|AIza[A-Za-z0-9_-]{35}|sk-ant-[A-Za-z0-9_-]{20,}|sk-or-v1-[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{36,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'

echo "== 憑證閘門掃描(只印位置.不印值) =="
# 排除本檔自身(只放樣式不放值),再排除 .secretgateignore 列出的白名單(假值測資)
LIST=$(printf '%s\n' "$FILES" | grep -v '^scripts/secret_commit_gate.sh$' || true)
IGN="$REPO/.secretgateignore"
if [ -s "$IGN" ]; then
  while IFS= read -r pat; do
    case "$pat" in ""|\#*) continue;; esac
    LIST=$(printf '%s\n' "$LIST" | grep -vxF "$pat" || true)
  done < "$IGN"
fi
HIT=0
if [ -n "$LIST" ]; then
  # cut 只留 檔名:行號,值永遠不會被印出來
  # -H 強制印檔名:單檔時 grep 預設不印檔名,cut 會把「值」當成第 2 欄印出來(2026-09-30 負向測試抓到)
  MATCH=$(printf '%s\n' "$LIST" | tr '\n' '\0' | (cd "$REPO" && LC_ALL=C xargs -0 grep -HnEI "$RE" 2>/dev/null) | cut -d: -f1,2 || true)
  if [ -n "$MATCH" ]; then
    while IFS=: read -r f l; do
      [ -n "$f" ] && echo "  ⛔ $f  行 $l"
    done <<< "$MATCH"
    HIT=1
  fi
fi

if [ "$HIT" -eq 0 ]; then
  echo "PASS:沒有命中任何憑證樣式"
  exit 0
fi
echo ""
echo "FAIL:上列檔案含憑證樣式.已擋下。"
echo "正確做法=把值移到 bot/.env 或 ~/.maplab/*.env.程式改成執行時讀環境變數;"
echo "不要改成把樣式湊短來躲閘門。已經推出去的值必須輪替.不是刪檔了事。"
exit 1
