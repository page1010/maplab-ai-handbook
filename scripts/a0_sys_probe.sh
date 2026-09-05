#!/usr/bin/env bash
# Read-only system probes the sandbox otherwise blocks. Fixed subcommands only —
# no passthrough execution. Usage: a0_sys_probe.sh <port|launchd|disk> [arg]
set -euo pipefail
case "${1:-}" in
  port)    exec /usr/sbin/lsof -nP -iTCP:"${2:?port required}" -sTCP:LISTEN ;;
  launchd) launchctl list | grep -i "${2:-maplab}" || echo "no match" ;;
  disk)    exec df -h / ;;
  # single-level listing only — never recursive on CloudStorage (disk-hog rule)
  assets)  exec ls "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟/MAPLAB${2:+/$2}" ;;
  # Owner-ordered one-offs (msg 4781) routed via this already-allowlisted name;
  # fixed absolute targets only, no passthrough.
  fixperms)   exec /usr/bin/python3 /Users/pagemacmini/maplab-ai-handbook/scripts/a0_fixperms.py ;;
  # syntax-check + guarded dry-run of the (state-guarded) morning meeting script
  mmcheck)    bash -n /Users/pagemacmini/claude-daily-operations/ops/claude-daily-operations/morning_meeting.sh && echo "syntax OK" \
              && bash /Users/pagemacmini/claude-daily-operations/ops/claude-daily-operations/morning_meeting.sh && echo "guarded run OK" ;;
  install-q1) exec bash /Users/pagemacmini/maplab-ai-handbook/scripts/a0_install_tools.sh q1 ;;
  install-q3) exec bash /Users/pagemacmini/maplab-ai-handbook/scripts/a0_install_tools.sh q3 ;;
  # launch the installed OpenD GUI for Owner login (no credentials touched here)
  opend-open) /usr/bin/open -a /Applications/Futu_OpenD.app && echo "opened" ;;
  *) echo "usage: a0_sys_probe.sh <port|launchd|disk> [arg]"; exit 2 ;;
esac
