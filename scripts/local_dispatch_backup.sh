#!/usr/bin/env bash
# local_dispatch_backup.sh — 每日 03:00 本地備份 + INDEX 重生
# 備份三個 repo：maplab-ai-handbook / agent-hq / New project
# 目標：~/maplab_backup/YYYYMMDD/（保留 7 天）
# INDEX：os.walk 走訪三個 repo → state/dispatch_backup_index.json

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NOTIFY="$REPO_ROOT/scripts/notify_owner.sh"
LOG_FILE="$REPO_ROOT/state/dispatch_backup.log"
DATE=$(date '+%Y%m%d')
BACKUP_BASE="$HOME/maplab_backup"
BACKUP_DIR="$BACKUP_BASE/$DATE"
INDEX_FILE="$REPO_ROOT/state/dispatch_backup_index.json"

ts()  { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] $*" >> "$LOG_FILE"; }

mkdir -p "$BACKUP_DIR"
log "=== dispatch backup $DATE start ==="

declare -a SOURCES=("$REPO_ROOT" "$HOME/agent-hq" "/Users/pagemacmini/Documents/New project")
declare -a NAMES=("maplab-ai-handbook" "agent-hq" "new-project")

ERRORS=0
for i in "${!SOURCES[@]}"; do
    SRC="${SOURCES[$i]}"
    NAME="${NAMES[$i]}"
    DST="$BACKUP_DIR/$NAME"
    if [[ -d "$SRC" ]]; then
        mkdir -p "$DST"
        rsync -a --delete \
              --exclude='.git' \
              --exclude='__pycache__' \
              --exclude='*.pyc' \
              --exclude='.DS_Store' \
              --exclude='node_modules' \
              --exclude='.venv' \
              --exclude='venv' \
              "$SRC/" "$DST/" 2>&1 | tail -2 | while read -r line; do log "  rsync[$NAME]: $line"; done || true
        log "✅ rsync $NAME done"
    else
        log "⚠️  skip $NAME — not found: $SRC"
        (( ERRORS++ )) || true
    fi
done

# INDEX 重生（os.walk 邏輯，沿用既有索引設計）
log "rebuilding INDEX..."
python3 - <<PYEOF
import os, json, datetime

REPO_ROOT = "$REPO_ROOT"
BACKUP_DIR = "$BACKUP_DIR"
INDEX_FILE = "$INDEX_FILE"

sources = {
    "maplab-ai-handbook": REPO_ROOT,
    "agent-hq":           os.path.expanduser("~/agent-hq"),
    "new-project":        "/Users/pagemacmini/Documents/New project",
}
SKIP = {'.git', '__pycache__', '.DS_Store', 'node_modules', '.venv', 'venv', 'maplab_backup'}

index = {
    "generated_at": datetime.datetime.now().isoformat(),
    "backup_dir":   BACKUP_DIR,
    "repos":        {},
}

for name, root in sources.items():
    if not os.path.isdir(root):
        print(f"  [{name}] skip (not found)")
        continue
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fn in filenames:
            fpath = os.path.join(dirpath, fn)
            try:
                stat = os.stat(fpath)
                rel  = os.path.relpath(fpath, root)
                files.append({
                    "path":  rel,
                    "size":  stat.st_size,
                    "mtime": int(stat.st_mtime),
                })
            except Exception:
                pass
    index["repos"][name] = {"root": root, "file_count": len(files), "files": files}
    print(f"  [{name}] {len(files)} files indexed")

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
print(f"INDEX written: {INDEX_FILE}")
PYEOF

log "✅ INDEX rebuilt → $INDEX_FILE"

# 保留 7 天備份
python3 -c "
import os, shutil, datetime
base   = '$BACKUP_BASE'
cutoff = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y%m%d')
if not os.path.isdir(base):
    exit()
for d in os.listdir(base):
    dpath = os.path.join(base, d)
    if os.path.isdir(dpath) and d.isdigit() and d < cutoff:
        shutil.rmtree(dpath)
        print(f'pruned: {d}')
" 2>/dev/null || true

log "=== dispatch backup done ==="

if [[ $ERRORS -gt 0 ]]; then
    bash "$NOTIFY" "⚠️ [dispatch-backup] $ERRORS 個備份來源找不到，請確認路徑" 2>/dev/null \
        || log "NOTIFY_FAILED"
fi
