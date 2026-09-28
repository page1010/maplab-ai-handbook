#!/bin/bash
# doc_governance_check.sh — 新來的看著照做,前提是「照做的那份清單裡真的找得到」
#
# 來源 Owner 訊息 6108(2026-09-24 22:02):
#   「建立了這麼多文件目的就是新來的看著照做ok , 不要亂搞。建立標準與新的路徑都只有最前沿的模型」
#
# 這支腳本檢查一件事:repo 最上層的治理 .md,是不是每一份都登錄在 SYSTEM_DIRECTORY_INDEX.md 裡。
# 沒登錄 = 新來的照著索引讀就永遠看不到那份檔 = 那份檔等於不存在,規則形同虛設。
#
# 2026-09-24 第一次跑的實數:最上層 25 份 .md(扣掉索引自己 24 份),其中 14 份沒登錄,
# 包含 AGENT_CORE.md、SOP_SEE_BEFORE_YOU_SAY.md、NAMING_GLOSSARY.md 這三份被點名必讀的。
# 也就是說「文件建了但新人找不到」是當時的實況,不是假想風險。
#
# 用法:
#   bash scripts/doc_governance_check.sh          檢查,有漏登錄就 exit 1
#   bash scripts/doc_governance_check.sh selftest 自我測試(故意塞一個不存在的檔名,應該被抓出來)
set -u
# 可搬移性見 PORTABILITY.md:路徑從腳本自己的位置推,不寫死使用者名稱。
HB="${MAPLAB_HB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
INDEX="$HB/SYSTEM_DIRECTORY_INDEX.md"
MODE="${1:-}"

[ -f "$INDEX" ] || { echo "FATAL: 找不到索引 $INDEX"; exit 2; }

/usr/bin/python3 - "$HB" "$INDEX" "$MODE" <<'PYEOF'
import os, sys

HB, INDEX, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
index_text = open(INDEX, encoding="utf-8", errors="ignore").read()
index_name = os.path.basename(INDEX)

names = sorted(f for f in os.listdir(HB)
               if f.endswith(".md") and f != index_name
               and os.path.isfile(os.path.join(HB, f)))

if MODE == "selftest":
    # 故意加一份不存在的檔名,檢查器必須把它算成沒登錄;全過表示這支腳本本身是活的,
    # 不是「永遠印 PASS」的假檢查。判定程式自己也要有測試——P10 那次關鍵詞漏一個字
    # 就把對的答案判成錯的,教訓寫在 HERMES_CAPABILITY_BOUNDARY.md。
    fake = "ZZZ_THIS_FILE_SHOULD_NOT_BE_IN_THE_INDEX.md"
    missing = [n for n in names + [fake] if n not in index_text]
    ok = fake in missing
    print("[%s] 假檔案有沒有被抓出來:%s" % ("過" if ok else "沒過", fake))
    real_missing = [n for n in missing if n != fake]
    ok2 = not real_missing
    print("[%s] 真實漏登錄數 = %d %s"
          % ("過" if ok2 else "沒過", len(real_missing),
             ("→ " + ", ".join(real_missing)) if real_missing else ""))
    sys.exit(0 if (ok and ok2) else 1)

missing = [n for n in names if n not in index_text]
print("最上層 .md(扣掉索引自己):%d 份;已登錄 %d;漏登錄 %d"
      % (len(names), len(names) - len(missing), len(missing)))
for n in missing:
    print("  🔴 沒登錄:%s —— 新來的照索引讀不會看到這份" % n)
if missing:
    print("")
    print("處理方式(Owner msg 6108):新增治理檔必須同一輪登錄進 SYSTEM_DIRECTORY_INDEX.md,")
    print("否則視同沒建立。立標準是最前沿模型那一席的事,其他席位只能交提案。")
sys.exit(1 if missing else 0)
PYEOF
