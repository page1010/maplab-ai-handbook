#!/usr/bin/env python3
"""工作單五欄檢查器——缺欄就擋,不准派工。

依據 AGENT_RULES.md SECTION 27 第三節(Owner msg 5862,2026-09-22):
所有工作單/task card/給實作性 agent 的指令必含
結果·指標·期限·權限·回報點,缺欄＝不准派工。

規則寫在文件裡沒有用,會忘;所以有這支。用法:

    python3 scripts/check_work_order.py handoff/tasks/T-XXX-001.md

exit 0 = 五欄齊全,可派工
exit 2 = 缺欄或只填了佔位符,不准派工(fail-closed,與報價引擎「需人工」同精神)
exit 1 = 檔案讀不到

刻意不做的事:不判斷內容寫得好不好(那是人的事),只判斷欄位在不在、
有沒有真的填、以及第五欄有沒有把 done 與 blocked 兩個終態都定義出來。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 五欄硬性欄位(SECTION 27 第三節原序,不要重排)+ 可逆性(S3 派工門檻要用)
REQUIRED = ("結果", "指標", "期限", "權限", "回報點")
ALSO_REQUIRED = ("動作可逆性",)

# 模板留的佔位符:填了這個等於沒填
PLACEHOLDER_MARKS = ("〈", "〉", "<填", "TODO", "TBD", "待填")

# 第五欄必須把兩個終態都定義出來,否則就是 win-01 七張卡的重演
TERMINAL_WORDS = ("done", "blocked")

# ── 派工無效類(2026-09-23,Owner msg 5954,CULTURE_DECISION_LOGIC.md 制度 E)──
#
# Owner 問:「你如果已經找出問題就發工作讓他自己修理?是這個意思嗎」——大多數情況是,
# 今天早上 win-01 的 hermes 就是自己撿卡、自己改、自己驗、自己回報的(12:57:49 rc=0)。
#
# 但有一類問題,卡發過去也沒有人能做,發了只是白等一輪:**需要在瀏覽器上用 Owner 的帳號
# 按「同意授權」的那一類**。agent 不碰帳密／授權碼／cookie,這是紅線,不因為方便就鬆動。
# 換長效憑證(claude setup-token)也走同一條瀏覽器流程,拿到的東西就是授權憑證本身,同樣不行。
#
# 這條以前只寫在 handoff 筆記裡(制度 E 的 L1,等於沒寫),所以下一個人看到機器掛了,
# 直覺還是發一張卡過去。現在把它挪到「他繞不過去的地方」= 這支 gate 與它的錯誤訊息本身(L3)。
#
# 只掃「結果」欄(這張卡要達成什麼),不掃全文——「權限」欄常常寫「不碰金鑰」,掃全文會誤殺。
UNDISPATCHABLE_MARKS = (
    "登入", "login", "重新授權", "同意授權", "授權碼", "帳密", "密碼",
    "oauth", "setup-token", "驗證碼", "cookie",
)


def field_value(text: str, name: str) -> str | None:
    """抓 `- **欄名**: 值` 這一行的值。抓不到回 None(=缺欄)。"""
    pattern = rf"^[ \t]*[-*+]?[ \t]*\*\*{re.escape(name)}\*\*[ \t]*[:：][ \t]*(.*)$"
    hit = re.search(pattern, text, flags=re.MULTILINE)
    if hit is None:
        return None
    return hit.group(1).strip()


def looks_unfilled(value: str) -> bool:
    if not value:
        return True
    return any(mark in value for mark in PLACEHOLDER_MARKS)


def check(path: Path) -> list[str]:
    """回傳問題清單;空清單=通過。"""
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []

    for name in REQUIRED + ALSO_REQUIRED:
        value = field_value(text, name)
        if value is None:
            problems.append(f"缺欄:{name}(整份文件找不到 - **{name}**: 這一行)")
        elif looks_unfilled(value):
            problems.append(f"未填:{name}(只有佔位符或空值)")

    goal = field_value(text, "結果")
    if goal is not None and not looks_unfilled(goal):
        lowered = goal.lower()
        hits = [m for m in UNDISPATCHABLE_MARKS if m in lowered]
        if hits:
            problems.append(
                "派工無效類:「結果」欄要求的是 " + "、".join(hits)
                + " 這一類事情。這需要在瀏覽器上用 Owner 的帳號按同意授權,"
                "agent 不碰帳密／授權碼／cookie(紅線),卡發過去沒有人能做,只會白等一輪。"
                "正確做法=不要派工,直接上呈 Owner 並附上『他只需要按哪一下』;"
                "能用工單修的部分(設定、程式、檔案)另開一張卡,不要跟這一類混在同一張。"
            )

    report = field_value(text, "回報點")
    if report is not None and not looks_unfilled(report):
        lowered = report.lower()
        missing = [w for w in TERMINAL_WORDS if w not in lowered]
        if missing:
            problems.append(
                "回報點沒定義終態:缺 " + "、".join(missing)
                + "(派工單上就要寫死 done 與 blocked 的條件,不留給 executor 自由心證)"
            )

    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("用法: python3 scripts/check_work_order.py <工作單路徑>")
        return 1
    path = Path(argv[1])
    if not path.is_file():
        print(f"讀不到檔案:{path}")
        return 1

    problems = check(path)
    if problems:
        print(f"不准派工:{path.name} 五欄檢查未通過")
        for p in problems:
            print(f"  ✗ {p}")
        print("模板:handoff/tasks/_WORK_ORDER_TEMPLATE.md")
        return 2

    print(f"可派工:{path.name} 結果·指標·期限·權限·回報點 全欄齊備,終態已定義")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
