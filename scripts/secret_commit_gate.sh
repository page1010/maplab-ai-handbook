#!/bin/bash
# secret_commit_gate.sh — 阻止把憑證 commit 進版控的閘門(只印檔名行號與樣式名,絕不印值)
#
# 背景(2026-09-30):handbook 這個倉在 GitHub 是公開的(匿名 curl 回 200),而 scripts/ 底下
# 有 20 支音樂線腳本把 Telegram bot 權杖寫死在原始碼。那些檔當時全部 untracked、也沒被
# .gitignore 蓋到,所以一次 `git add -A` 就會把 Owner 的 bot 權杖推上公開網路。
#
# 本檔是三道防線的第三道:
#   第一道 原始碼裡根本沒有值 → scripts/maplab_secrets.py 統一從 .env 讀
#   第二道 .gitignore 蓋住會夾帶憑證的檔型(瀏覽器設定檔、整頁另存 HTML、.work/)
#   第三道 本閘門 → 任何把值寫回原始碼的 commit 一律擋下
# 規範全文=docs/OPERATING_CULTURE.md 原則 11。
#
# 用法:
#   bash scripts/secret_commit_gate.sh                    # 檢查已 staged 的檔(pre-commit 用)
#   bash scripts/secret_commit_gate.sh --all              # 掃全部已追蹤檔(稽核用)
#   bash scripts/secret_commit_gate.sh --untracked        # 掃未追蹤且未被忽略的檔(=下一次 add -A 會送出去的)
#   bash scripts/secret_commit_gate.sh --repo <路徑> ...  # 對別的倉做上面任一種掃描
#   bash scripts/secret_commit_gate.sh --install          # 裝成本倉 .git/hooks/pre-commit
#   bash scripts/secret_commit_gate.sh --install-into <倉路徑>   # 裝到別的倉(失敗關閉:閘門檔不在就擋住 commit)
# 退出碼:0=乾淨 1=命中(擋下) 2=用法或環境錯誤
set -u

# 倉庫位置由本腳本自身路徑推出,不看呼叫者的工作目錄(bot 的工作目錄不在倉內)
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SELF="$HERE/$(basename "${BASH_SOURCE[0]}")"
HOME_REPO="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null)"

MODE="staged"
REPO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --all)        MODE="all"; shift;;
    --untracked)  MODE="untracked"; shift;;
    --repo)       REPO="${2:-}"; shift 2 || exit 2;;
    --install)
      if [ -z "$HOME_REPO" ]; then echo "不在 git 倉裡:$HERE"; exit 2; fi
      H="$HOME_REPO/.git/hooks/pre-commit"
      printf '%s\n' '#!/bin/bash' 'exec bash "$(git rev-parse --show-toplevel)/scripts/secret_commit_gate.sh"' > "$H"
      chmod +x "$H"; echo "已裝 pre-commit -> $H"; exit 0;;
    --install-into)
      T="${2:-}"; shift 2 || exit 2
      TR="$(git -C "$T" rev-parse --show-toplevel 2>/dev/null)"
      if [ -z "$TR" ]; then echo "不是 git 倉:$T"; exit 2; fi
      H="$TR/.git/hooks/pre-commit"
      # 失敗關閉:閘門檔被移走/改名時,擋住 commit 而不是默默放行
      {
        printf '%s\n' '#!/bin/bash'
        printf '%s\n' '# 由 maplab-ai-handbook/scripts/secret_commit_gate.sh --install-into 產生(2026-09-30)'
        printf '%s\n' "GATE=\"$SELF\""
        printf '%s\n' 'if [ ! -f "$GATE" ]; then'
        printf '%s\n' '  echo "⛔ 憑證閘門不見了:$GATE"'
        printf '%s\n' '  echo "   這是失敗關閉設計——閘門不在就不准 commit。修好路徑或重裝後再試。"'
        printf '%s\n' '  exit 1'
        printf '%s\n' 'fi'
        printf '%s\n' 'exec bash "$GATE" --repo "$(git rev-parse --show-toplevel)"'
      } > "$H"
      chmod +x "$H"; echo "已裝 pre-commit -> $H"; exit 0;;
    *) echo "不認得的參數:$1"; exit 2;;
  esac
done

[ -z "$REPO" ] && REPO="$HOME_REPO"
if [ -z "$REPO" ]; then echo "不在 git 倉裡:$HERE"; exit 2; fi
REPO="$(git -C "$REPO" rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO" ]; then echo "不是 git 倉"; exit 2; fi

case "$MODE" in
  all)        FILES=$(git -C "$REPO" ls-files);;
  untracked)  FILES=$(git -C "$REPO" ls-files --others --exclude-standard);;
  *)          FILES=$(git -C "$REPO" diff --cached --name-only --diff-filter=ACM);;
esac
[ -z "$FILES" ] && { echo "沒有要檢查的檔($MODE)"; exit 0; }

# 一次 grep 掃完所有樣式(4000+ 檔逐檔逐樣式跑會慢到不能當 pre-commit 用)
#
# EAA 那條刻意要求 150 字以上:Meta 長效權杖實測長度 201,而瀏覽器的 Local State
# 之類 base64 blob 很容易湊出 40 字的 EAA 開頭 → 2026-09-30 在 agent-bus 實測到
# 21 個這種誤判。把門檻拉到 150 可以保留真權杖、濾掉 blob 巧合。
#
# 最後一條抓的是「把 Owner 的聊天室編號寫死」:只寫樣式不寫值,
# 因為本檔自己是進版控的公開檔,把值寫進來等於自己洩自己。
RE='[0-9]{8,12}:AA[A-Za-z0-9_-]{30,}|EAA[A-Za-z0-9]{150,}|AIza[A-Za-z0-9_-]{35}|sk-ant-[A-Za-z0-9_-]{20,}|sk-or-v1-[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{36,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(chat_id|CHAT_ID)[ \t]*[=:][ \t]*["'"'"']?[0-9]{9,12}'

echo "== 憑證閘門掃描($MODE / $REPO,只印位置.不印值) =="
# 排除本檔自身(只放樣式不放值),再排除 .secretgateignore 列出的白名單
LIST=$(printf '%s\n' "$FILES" | grep -v '^scripts/secret_commit_gate.sh$' || true)
IGN="$REPO/.secretgateignore"
if [ -s "$IGN" ]; then
  while IFS= read -r pat; do
    case "$pat" in ""|\#*) continue;; esac
    if printf '%s' "$pat" | grep -q '[*?]'; then
      # 有萬用字元 → 當 glob 比對(2026-09-30 新增:agent-bus 的瀏覽器設定檔要整片排除)
      NEXT=""
      while IFS= read -r f; do
        case "$f" in $pat) continue;; esac
        NEXT="$NEXT$f
"
      done <<< "$LIST"
      LIST="${NEXT%$'\n'}"
    else
      LIST=$(printf '%s\n' "$LIST" | grep -vxF "$pat" || true)
    fi
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
echo "正確做法=把值移到 bot/.env 或 ~/.maplab/*.env,程式改成 get_secret(\"鍵名\") 執行時讀;"
echo "         python 腳本可直接跑 scripts/secret_migrate_to_env.py --apply 自動改寫。"
echo "不要改成把樣式湊短來躲閘門。已經推出去的值必須輪替.不是刪檔了事。"
echo "若確定是假值測資或第三方公開檔,把路徑加進 $IGN(支援萬用字元)。"
exit 1
