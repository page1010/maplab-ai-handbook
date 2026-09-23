#!/usr/bin/env bash
# uninstall_ollama.sh — 卸載本機 Ollama（Owner msg 4723「llama 先卸載」授權）
# 邊界（skills/a0-selfops）：只殺全路徑吻合的 Ollama 進程；不碰外接冷資料
# /Volumes/MacExternal/FABLE5_ARCHIVE/models/dot-ollama（保留，只拆 ~/.ollama symlink）。
# 每步如實記錄到 state/ollama_uninstall_20260904.log。
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$ROOT/state/ollama_uninstall_20260904.log"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" | tee -a "$LOG"; }

log "=== ollama 卸載開始（Owner msg 4723）==="

# 1. 停止進程（只殺 Ollama.app 全路徑進程）
if pgrep -f "/Applications/Ollama.app" >/dev/null; then
    pkill -f "/Applications/Ollama.app" && log "已送 TERM 給 Ollama.app 進程"
    sleep 3
    if pgrep -f "/Applications/Ollama.app" >/dev/null; then
        pkill -9 -f "/Applications/Ollama.app" && log "殘留進程已 KILL -9"
        sleep 1
    fi
else
    log "無 Ollama.app 進程在跑"
fi
pgrep -f "/Applications/Ollama.app" >/dev/null && log "❌ 進程仍存在" || log "✅ 進程已全部停止"

# 2. 移除 App 本體
if [[ -d /Applications/Ollama.app ]]; then
    rm -rf /Applications/Ollama.app && log "✅ /Applications/Ollama.app 已移除" || log "❌ App 移除失敗（權限？）"
else
    log "App 不存在，略過"
fi

# 3. 移除 CLI（/usr/local/bin/ollama，通常是指向 App 的 symlink）
if [[ -e /usr/local/bin/ollama || -L /usr/local/bin/ollama ]]; then
    rm -f /usr/local/bin/ollama && log "✅ /usr/local/bin/ollama 已移除" || log "❌ CLI 移除失敗（權限？）"
else
    log "CLI 不存在，略過"
fi

# 4. 拆 ~/.ollama symlink（指向外接冷資料庫；冷資料本體保留不動）
if [[ -L "$HOME/.ollama" ]]; then
    TARGET="$(readlink "$HOME/.ollama")"
    rm -f "$HOME/.ollama" && log "✅ ~/.ollama symlink 已拆（外接冷資料 $TARGET 保留未動）"
elif [[ -d "$HOME/.ollama" ]]; then
    log "⚠️ ~/.ollama 是實體目錄非 symlink，未刪（避免誤刪資料，留給人工確認）"
else
    log "~/.ollama 不存在，略過"
fi

# 5. 收尾驗證
command -v ollama >/dev/null 2>&1 && log "⚠️ PATH 上仍找得到 ollama：$(command -v ollama)" || log "✅ PATH 上已無 ollama"
[[ -d /Applications/Ollama.app ]] && log "⚠️ App 目錄仍在" || log "✅ App 目錄已無"
pgrep -f -i "ollama" >/dev/null && log "⚠️ 仍有 ollama 相關進程" || log "✅ 無任何 ollama 進程"

log "=== 卸載結束 ==="
