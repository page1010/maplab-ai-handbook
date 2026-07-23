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

# === 外接碟備份段（長期累加，絕不 --delete）===
EXT_MOUNT="/Volumes/MacExternal"
EXT_DST="$EXT_MOUNT/MAPLAB_BACKUP/dispatch-sessions"
SESSION_SRC="$HOME/Library/Application Support/Claude/local-agent-mode-sessions"

if [[ -d "$EXT_MOUNT" ]] && touch "$EXT_MOUNT/MAPLAB_BACKUP/.write_test" 2>/dev/null && rm "$EXT_MOUNT/MAPLAB_BACKUP/.write_test" 2>/dev/null; then
    log "外接碟已掛載，累加備份 → $EXT_DST"
    mkdir -p "$EXT_DST"
    rsync -a \
          --exclude='.DS_Store' \
          --exclude='*.tmp' \
          "$SESSION_SRC/" "$EXT_DST/" 2>&1 | tail -3 | while read -r line; do log "  ext-rsync: $line"; done || true

    # 重生 INDEX.md + 寫 backup.log
    python3 - <<EXTPYEOF
import os, json, datetime

EXT_DST   = "$EXT_DST"
EXT_LOG   = os.path.join(EXT_DST, "backup.log")
EXT_INDEX = os.path.join(EXT_DST, "INDEX.md")

def human_size(n):
    for unit in ['B','KB','MB','GB']:
        if n < 1024: return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"

rows = []
total_size = 0
for dirpath, dirnames, filenames in os.walk(EXT_DST):
    dirnames[:] = sorted(dirnames)
    for fn in filenames:
        if dirpath == EXT_DST and fn in ('INDEX.md', 'backup.log'):
            continue
        if not fn.endswith('.jsonl'):
            continue
        fpath = os.path.join(dirpath, fn)
        try:
            stat = os.stat(fpath)
            size_kb = stat.st_size // 1024
            total_size += stat.st_size
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
            rel = os.path.relpath(fpath, EXT_DST)
            topic = ""
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        obj = json.loads(line)
                        content = obj.get('message', {}).get('content', '') or obj.get('content', '')
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get('type') == 'text':
                                    topic = c.get('text', '')[:80]
                                    break
                        elif isinstance(content, str):
                            topic = content[:80]
                        if topic:
                            break
            except Exception:
                pass
            topic = topic.replace('|', '｜').replace('\n', ' ').strip()
            msg_count = 0
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                    for ln in fh:
                        if ln.strip():
                            msg_count += 1
            except Exception:
                pass
            rows.append((mtime, size_kb, msg_count, topic, rel))
        except Exception:
            pass

rows.sort(key=lambda r: r[0], reverse=True)
total_jsonl = len(rows)
now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
total_human = human_size(total_size)

with open(EXT_INDEX, 'w', encoding='utf-8') as fh:
    fh.write("# Dispatch Sessions 備份索引\n\n")
    fh.write(f"更新: {now_str} | 檔數: {total_jsonl} | 總大小: {total_human}\n\n")
    fh.write("| 日期 | KB | 訊息數 | 主題 | 路徑 |\n")
    fh.write("|---|---|---|---|---|\n")
    for mtime, size_kb, msg_count, topic, rel in rows[:200]:
        fh.write(f"| {mtime} | {size_kb} | {msg_count} | {topic} | {rel} |\n")

with open(EXT_LOG, 'a', encoding='utf-8') as fh:
    fh.write(f"{now_str}  backup_ok  jsonl={total_jsonl}  total={total_human}  INDEX.md regenerated\n")

print(f"外接碟 INDEX.md 更新：{total_jsonl} 個 jsonl，{total_human}")
EXTPYEOF

    log "✅ 外接碟備份完成 → $EXT_DST"
else
    log "外接碟未掛載或不可寫，跳過外接碟備份（正常，外接碟可能已拔走）"
fi

if [[ $ERRORS -gt 0 ]]; then
    bash "$NOTIFY" "⚠️ [dispatch-backup] $ERRORS 個備份來源找不到，請確認路徑" 2>/dev/null \
        || log "NOTIFY_FAILED"
fi
