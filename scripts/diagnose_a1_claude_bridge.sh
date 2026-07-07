#!/bin/bash
# 診斷 + 修復指引:A1 Telegram bot → 獨立 Claude Code session 橋接
# 用途:Owner 說「bot 不會自動連 Claude Code 了,只剩 Dispatch」時跑這支。
# 在 Mac mini 執行:bash scripts/diagnose_a1_claude_bridge.sh
# (也可由 A0 Cowork 開 Code task 代跑,輸出全部可安全轉述,不印 secrets)

REPO="$HOME/maplab-ai-handbook"
ENVF="$REPO/.env"
PASS=0; FAIL=0
ok(){ echo "✅ $1"; PASS=$((PASS+1)); }
bad(){ echo "❌ $1"; FAIL=$((FAIL+1)); }

echo "=== A1 Claude 橋接診斷 $(date '+%F %T') ==="

# 1. bot 進程
if launchctl list | grep -q com.maplab.telegrambot; then
  ok "A1 bot launchd job 存在(com.maplab.telegrambot)"
else
  bad "A1 bot 沒在跑 → 修復:bash $REPO/scripts/bot_restart_emergency.sh"
fi

# 2. token 存在性(只看長度,不印值)
if [ -f "$ENVF" ] && grep -q "^CLAUDE_CODE_OAUTH_TOKEN=" "$ENVF"; then
  TLEN=$(grep "^CLAUDE_CODE_OAUTH_TOKEN=" "$ENVF" | head -1 | cut -d= -f2- | tr -d '"' | wc -c | tr -d ' ')
  ok "CLAUDE_CODE_OAUTH_TOKEN 存在(長度 ${TLEN})"
else
  bad "CLAUDE_CODE_OAUTH_TOKEN 不在 .env → 修復:claude setup-token 產新 token 寫入 .env"
fi

# 3. claude CLI
if command -v claude >/dev/null 2>&1; then
  ok "claude CLI: $(command -v claude) / $(claude --version 2>/dev/null | head -1)"
else
  bad "claude CLI 不在 PATH → 修復:npm install -g @anthropic-ai/claude-code,並確認 launchd plist 的 PATH 含其路徑"
fi

# 4. 實測一次 claude -p(關鍵測試:token 是否還有效)
if command -v claude >/dev/null 2>&1; then
  set -a; [ -f "$ENVF" ] && source "$ENVF"; set +a
  OUT=$(echo | claude -p --dangerously-skip-permissions "只回覆 PONG 兩個字" 2>&1 | tail -3)
  if echo "$OUT" | grep -qi "PONG"; then
    ok "claude -p 實測成功 → 橋接本體是好的,問題在 bot 端(sticky 鎖或 bot 沒重啟)"
    echo "   → 修復:Telegram 對 A1 bot 發 /claude(解除 Hermes 黏著/手動鎖),再發一句話測試"
  else
    bad "claude -p 實測失敗,輸出尾段:"
    echo "----"; echo "$OUT" | sed 's/^/   /'; echo "----"
    if echo "$OUT" | grep -qiE "auth|token|login|expired|credential"; then
      echo "   → 判定:TOKEN 過期/失效。修復三步:"
      echo "     1) 在 Mac 跑:claude setup-token(跟著瀏覽器流程)"
      echo "     2) 把新 token 更新進 $ENVF 的 CLAUDE_CODE_OAUTH_TOKEN="
      echo "     3) bash $REPO/scripts/bot_restart_emergency.sh(重啟後 sticky 狀態自動清空)"
    elif echo "$OUT" | grep -qiE "quota|rate|limit|usage"; then
      echo "   → 判定:訂閱額度用盡/限流。等額度恢復,期間 bot 會自動走 Hermes/Ollama 備援(by design)。"
    fi
  fi
fi

# 5. log 尾段
[ -f "$REPO/bot/launchd_stderr.log" ] && { echo "--- bot stderr 最後 5 行 ---"; tail -5 "$REPO/bot/launchd_stderr.log"; }

echo "=== 結果:$PASS 項通過 / $FAIL 項需修 ==="
echo "全部修完的驗收:Telegram 私窗對 A1 bot 發「開一個 Code task 讀 CURRENT_STATUS 標頭回報我」,"
echo "收到正確回覆 = Telegram→Claude Code 獨立作業線恢復,與 Dispatch(Cowork)雙線並行。"
