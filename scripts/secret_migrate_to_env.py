#!/usr/bin/env python3
"""secret_migrate_to_env — 把寫死在 python 原始碼裡的憑證改成執行時讀 .env。

背景(2026-09-30):handbook 這個倉在 GitHub 是公開的,而 scripts/ 底下有 20 支音樂線
腳本把 Telegram 機器人權杖寫死在原始碼。全量稽核確認那 20 支從未進版控、沒有外洩,
但它們也沒被忽略清單蓋到——一次 `git add -A` 就會把權杖推上公開網路。
把「靠自律不要 add -A」換成「原始碼裡根本沒有值可洩」。

處理兩種形式:
  A) 頂層字面指派   BOT_TOKEN = "<值>"      → get_secret("TELEGRAM_BOT_TOKEN")
  B) 字串內嵌       ".../bot<值>/sendAudio" → f-string 引用 BOT_TOKEN,並補上頂層定義

用法:
  python3 scripts/secret_migrate_to_env.py --dry-run          # 只報告,不動檔(預設)
  python3 scripts/secret_migrate_to_env.py --apply            # 真的改,改前先備份
  python3 scripts/secret_migrate_to_env.py --verify           # 改完檢查:殘留數 + 語法

絕不印出任何憑證值:命中一律以 <REDACTED> 呈現,只報檔名、行號與筆數。
"""

import argparse
import datetime
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent

# 值的樣式 → 要改讀哪個環境變數名
RULES = [
    # Telegram 機器人權杖
    (re.compile(r"[0-9]{8,12}:AA[A-Za-z0-9_-]{30,}"), "TELEGRAM_BOT_TOKEN", "BOT_TOKEN"),
    # Owner 的聊天室編號(不是憑證,但是個人識別碼,一併收進 .env)
    (re.compile(r"\b1077768811\b"), "OWNER_CHAT_ID", "CHAT_ID"),
]

IMPORT_LINE = "from maplab_secrets import get_secret  # 憑證只從 .env 讀,不寫死(原則 11)"


def find_targets(scripts_dir):
    hits = []
    for path in sorted(scripts_dir.glob("*.py")):
        if path.name in ("maplab_secrets.py", "secret_migrate_to_env.py"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        n = sum(len(pat.findall(text)) for pat, _, _ in RULES)
        if n:
            hits.append((path, n))
    return hits


def ensure_import(lines):
    """把 import 行插在最後一個頂層 import 之後;沒有 import 就插在 shebang/docstring 之後。"""
    if any(line.strip() == IMPORT_LINE.split("  #")[0].strip() for line in lines):
        return lines, False
    last_import = -1
    for i, line in enumerate(lines[:80]):
        if re.match(r"^(import |from )\S", line):
            last_import = i
    if last_import >= 0:
        lines.insert(last_import + 1, IMPORT_LINE)
        return lines, True
    # 沒有頂層 import:跳過 shebang 與編碼宣告
    i = 0
    while i < len(lines) and (lines[i].startswith("#!") or lines[i].startswith("# -*-")):
        i += 1
    lines.insert(i, IMPORT_LINE)
    return lines, True


def migrate_one(path, backup_dir, apply_changes):
    text = path.read_text(encoding="utf-8")
    original = text
    report = {"form_a": 0, "form_b": 0, "form_c": 0, "var_defs_added": []}

    for pat, env_name, var_name in RULES:
        # ── 形式 A:頂層字面指派 ─────────────────────────────
        # 例 BOT_TOKEN = "<值>" / ALLOWED_CHAT_ID = '<值>'
        def repl_a(m):
            report["form_a"] += 1
            return '%s%s = get_secret("%s")' % (m.group("indent"), m.group("name"), env_name)

        text, n_a = re.subn(
            r'(?m)^(?P<indent>[ \t]*)(?P<name>[A-Za-z_][A-Za-z0-9_]*)[ \t]*=[ \t]*["\']'
            + pat.pattern
            + r'["\']',
            repl_a,
            text,
        )

        # ── 形式 B:值內嵌在字串裡 ──────────────────────────
        # 例 "https://api.telegram.org/bot<值>/sendAudio"
        #    → f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
        def repl_b(m):
            report["form_b"] += 1
            body = m.group("body")
            body = pat.sub("{%s}" % var_name, body)
            return '%s"%s"' % ("f" if not m.group("pfx") else m.group("pfx"), body)

        text, n_b = re.subn(
            r'(?P<pfx>f?)"(?P<body>[^"\n]*' + pat.pattern + r'[^"\n]*)"',
            repl_b,
            text,
        )

        if n_b:
            # 形式 B 用到了 var_name,確保頂層有定義
            if not re.search(r"(?m)^%s[ \t]*=" % re.escape(var_name), text):
                lines = text.split("\n")
                lines, _ = ensure_import(lines)
                # 插在 import 之後
                for i, line in enumerate(lines):
                    if line == IMPORT_LINE:
                        lines.insert(i + 1, '%s = get_secret("%s")' % (var_name, env_name))
                        break
                text = "\n".join(lines)
                report["var_defs_added"].append(var_name)

    # ── 形式 C:值出現在註解／docstring 的說明文字裡 ──────────
    # 改不到程式行為,但一樣是把識別碼留在原始碼。統一換成指向 .env 的字樣。
    text, n_c = re.subn(r"\b1077768811\b", "見 .env 的 OWNER_CHAT_ID", text)
    report["form_c"] = n_c

    if text == original:
        return None

    # 用到 get_secret 就一定要有 import
    if "get_secret(" in text:
        lines = text.split("\n")
        if not any("from maplab_secrets import get_secret" in line for line in lines):
            lines, _ = ensure_import(lines)
            text = "\n".join(lines)

    if apply_changes:
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_dir / path.name)
        path.write_text(text, encoding="utf-8")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真的改檔(預設只報告)")
    ap.add_argument("--verify", action="store_true", help="只檢查殘留與語法")
    args = ap.parse_args()

    scripts_dir = HERE
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = pathlib.Path.home() / ".maplab" / "backup" / ("secret-migration-" + stamp)

    if args.verify:
        left = find_targets(scripts_dir)
        print("== 殘留寫死憑證的檔 ==")
        if not left:
            print("  (無)")
        for path, n in left:
            print("  ⛔ %s  %d 處" % (path.name, n))
        print()
        print("== 語法檢查(只檢查本次會動到的那批) ==")
        bad = 0
        for path in sorted(scripts_dir.glob("*.py")):
            if "get_secret(" not in path.read_text(encoding="utf-8", errors="replace"):
                continue
            try:
                # 用內建 compile 而不是 py_compile:只要語法正確就好,不落 .pyc 檔
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
                print("  PASS %s" % path.name)
            except SyntaxError as exc:
                bad += 1
                print("  FAIL %s -> 第 %s 行 SyntaxError" % (path.name, exc.lineno))
        print()
        print("結果:殘留 %d 檔,語法失敗 %d 檔" % (len(left), bad))
        return 1 if (left or bad) else 0

    targets = find_targets(scripts_dir)
    print("== 命中 %d 檔(值一律不印) ==" % len(targets))
    for path, n in targets:
        print("  %s  %d 處" % (path.name, n))
    if not args.apply:
        print()
        print("這是 dry-run。要真的改請加 --apply(會先備份到 ~/.maplab/backup/)。")
        return 0

    print()
    print("== 開始改寫.備份目錄 %s ==" % backup_dir)
    changed = 0
    for path, _ in targets:
        rep = migrate_one(path, backup_dir, apply_changes=True)
        if rep is None:
            print("  -- %s 無可自動改寫的形式" % path.name)
            continue
        changed += 1
        extra = ("+定義 " + ",".join(rep["var_defs_added"])) if rep["var_defs_added"] else ""
        print(
            "  ok %s  形式A %d / 形式B %d / 形式C %d  %s"
            % (path.name, rep["form_a"], rep["form_b"], rep["form_c"], extra)
        )
    print()
    print("改寫完成 %d 檔。備份在 %s" % (changed, backup_dir))
    print("接著跑 --verify 確認殘留為 0 且語法全過。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
