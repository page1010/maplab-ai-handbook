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
  *) echo "usage: a0_sys_probe.sh <port|launchd|disk> [arg]"; exit 2 ;;
esac
