#!/usr/bin/env python3
"""Owner-ordered permission fix (Telegram msg 4771 + 4781 「第二點馬上改」).

Adds narrowly-scoped Bash allow rules and the two missing working directories
to ~/.claude/settings.json so bot resume sessions stop hitting approval walls.
Idempotent; writes a timestamped backup next to the file before changing it.
Scope deliberately excludes anything touching secrets, sudo, or production.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

SETTINGS = Path.home() / ".claude" / "settings.json"

ALLOW_ADD = [
    "Bash(bash /Users/pagemacmini/maplab-ai-handbook/scripts/:*)",
    "Bash(python3 /Users/pagemacmini/maplab-ai-handbook/scripts/:*)",
    "Bash(/usr/bin/python3 /Users/pagemacmini/maplab-ai-handbook/scripts/:*)",
    "Bash(bash /Users/pagemacmini/claude-daily-operations/ops/claude-daily-operations/:*)",
    "Bash(ls:*)",
    "Bash(tail:*)",
    "Bash(head:*)",
    "Bash(wc:*)",
    "Bash(grep:*)",
    "Bash(lsof:*)",
    "Bash(launchctl list:*)",
    "Bash(brew install:*)",
    "Bash(brew list:*)",
    "Bash(brew info:*)",
    "Bash(pip3 install --user:*)",
    "Bash(pip3 show:*)",
]
DIRS_ADD = [
    "/Users/pagemacmini/claude-daily-operations",
    "/Users/pagemacmini/agent-bus",
]


def main() -> int:
    data = json.loads(SETTINGS.read_text())
    perms = data.setdefault("permissions", {})
    allow = perms.setdefault("allow", [])
    dirs = perms.setdefault("additionalDirectories", [])

    added = [r for r in ALLOW_ADD if r not in allow]
    added_dirs = [d for d in DIRS_ADD if d not in dirs]
    if not added and not added_dirs:
        print("no-op: all rules already present")
        return 0

    backup = SETTINGS.with_name(
        f"settings.json.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    shutil.copy2(SETTINGS, backup)
    allow.extend(added)
    dirs.extend(added_dirs)
    SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"backup: {backup}")
    for r in added:
        print(f"+allow {r}")
    for d in added_dirs:
        print(f"+dir   {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
