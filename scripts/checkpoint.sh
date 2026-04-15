#!/bin/bash
# checkpoint.sh — 一鍵存檔
# 預設：commit 到 agent branch，等 Owner 執行 approve.sh 才進 main
# 加 --fast：直接 push 到 main（信任模式，適合 A1 本身操作）
#
# 用法：
#   bash scripts/checkpoint.sh "角色名" "做了什麼"           # 預設 branch 模式
#   bash scripts/checkpoint.sh "角色名" "做了什麼" --fast    # 直接進 main
#
# 例如：
#   bash scripts/checkpoint.sh "A5" "修正 QUOTE_DRAFT 公式"
#   bash scripts/checkpoint.sh "A1" "更新 CURRENT_STATUS" --fast

ROLE="${1:-}"
MESSAGE="${2:-}"
FAST_MODE=false
REPO_ROOT="/Users/pagemacmini/maplab-ai-handbook"
TASKS_DIR="$REPO_ROOT/handoff/tasks"

# === 自動更新 Task Card「最後活動」欄位 ===
_inject_status_block() {
  # 對缺接續狀態區塊的 Task Card 補上空白模板
  local card="$1"
  local today=$(date +%Y-%m-%d)

  # 已有接續狀態區塊 → 跳過
  grep -q '^\- \*\*狀態\*\*' "$card" && return 1

  # 在第一個 --- 或 ## 之後插入（跳過標題行）
  # 找到第一個非標題、非空行的位置，在檔案開頭的標題後插入
  local tmp="${card}.tmp"
  local inserted=false

  while IFS= read -r line; do
    echo "$line" >> "$tmp"
    # 在第一個 # 標題行之後插入
    if [[ "$inserted" == false ]] && echo "$line" | grep -q '^# '; then
      inserted=true
      cat >> "$tmp" << BLOCK

## 接續狀態
- **狀態**: 🔄 進行中
- **最後活動**: ${today}
- **接續點**: （checkpoint.sh 自動補建，請 agent 填寫）
- **阻塞**: 無
BLOCK
    fi
  done < "$card"

  if [[ "$inserted" == true ]]; then
    mv "$tmp" "$card"
    return 0
  else
    rm -f "$tmp"
    return 1
  fi
}

_update_task_cards() {
  local role="$1"
  local short_hash="$2"
  local today=$(date +%Y-%m-%d)
  local updated=0
  local injected=0

  # 找該角色的進行中 (🔄) 或任何 Task Card
  for card in "$TASKS_DIR"/T-${role}-*.md "$TASKS_DIR"/T-${role}[A-Z]*-*.md; do
    [ -f "$card" ] || continue

    # 偵測缺接續區塊 → 自動補上
    if ! grep -q '^\- \*\*最後活動\*\*' "$card"; then
      if _inject_status_block "$card"; then
        injected=$((injected + 1))
        echo "🔧 Task Card 自動補建接續區塊：$(basename "$card")"
      fi
    fi

    if grep -q '🔄 進行中' "$card"; then
      # 更新「最後活動」行
      if grep -q '^\- \*\*最後活動\*\*' "$card"; then
        sed -i '' "s/^- \*\*最後活動\*\*:.*/- **最後活動**: ${today} ${short_hash}/" "$card"
        updated=$((updated + 1))
        echo "📝 Task Card 更新：$(basename "$card") → 最後活動 ${today} ${short_hash}"
      fi
    fi
  done

  if [ "$injected" -gt 0 ]; then
    echo ""
    echo "⚠️  ${injected} 張 Task Card 缺接續區塊，已自動補建。請檢查內容是否正確。"
  fi

  if [ "$updated" -gt 0 ]; then
    echo ""
    echo "⚠️  Task Card「最後活動」已更新（本地）。下次 checkpoint 會一起提交。"
    echo "⚠️  請同時更新 Task Card 的「接續點」欄位（做到哪、下一步做什麼）。"
  elif [ "$injected" -eq 0 ]; then
    echo "ℹ️  未找到 ${role} 的 🔄 進行中 Task Card，跳過自動更新。"
  fi
}

# === 自動同步 CURRENT_STATUS.md 任務表（Phase 2-2: T-A1-V7） ===
_sync_current_status() {
  local status_file="$REPO_ROOT/CURRENT_STATUS.md"
  [ -f "$status_file" ] || return 0

  local today=$(date +%Y-%m-%d)
  local now_time=$(date +%H:%M)
  local now_ts=$(date +%s)

  # ── 掃描所有 Task Card，建任務表行 ──
  local table_rows=""
  local blocker_rows=""

  for card in "$TASKS_DIR"/T-*.md; do
    [ -f "$card" ] || continue
    local filename=$(basename "$card" .md)

    # 提取欄位
    local status=$(grep -m1 '^\- \*\*狀態\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "")
    local last_activity=$(grep -m1 '^\- \*\*最後活動\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "")
    local blocker=$(grep -m1 '^\- \*\*阻塞\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "無")
    local next_step=$(grep -m1 '^\- \*\*接續點\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "")

    # 提取標題（去掉 # 和 Task Card: 前綴）
    local title=$(head -1 "$card" | sed -e 's/^# //' -e 's/^Task Card: //' -e "s/^${filename}[: —–-]*//" | sed 's/^ *//')
    [ -z "$title" ] && title="$filename"

    # 提取 agent（從檔名 T-A5-002 → A5, T-A2A3-001 → A2/A3）
    local agent=$(echo "$filename" | sed -E 's/^T-//' | grep -oE 'A[0-9]+' | head -1 || echo "??")
    # 特殊處理 A2A3
    if echo "$filename" | grep -q 'A2A3'; then
      agent="A2/A3"
    fi
    # GBP 特殊處理
    if echo "$filename" | grep -q 'GBP'; then
      agent="Owner"
    fi

    # 跳過已完成的
    if echo "$status" | grep -q '✅'; then
      continue
    fi

    # 計算時間差（用於顯示）
    local activity_date=$(echo "$last_activity" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
    local age_info=""
    if [ -n "$activity_date" ]; then
      local then_ts=$(date -j -f "%Y-%m-%d" "$activity_date" +%s 2>/dev/null || echo 0)
      if [ "$then_ts" != "0" ]; then
        local hours_ago=$(( (now_ts - then_ts) / 3600 ))
        if [ "$hours_ago" -gt 48 ]; then
          age_info="~${hours_ago}h無commit"
        fi
      fi
    fi

    # 組裝狀態描述
    local display_status="$status"
    # 如果進行中且超過 48h → 標記 CRITICAL
    if echo "$status" | grep -q '🔄' && [ -n "$age_info" ]; then
      display_status="🔴 CRITICAL（${age_info}）"
    elif echo "$status" | grep -q '🔲' && [ -n "$age_info" ]; then
      display_status="$status"
    fi
    # 如果有接續點，附在狀態後
    if [ -n "$next_step" ] && [ "$next_step" != "（checkpoint.sh 自動補建，請 agent 填寫）" ] && ! echo "$display_status" | grep -q 'CRITICAL'; then
      # 截短到 60 字
      local short_next=$(echo "$next_step" | cut -c1-60)
      display_status="${display_status}（${short_next}）"
    fi

    # Task Card 路徑
    local card_path="handoff/tasks/${filename}.md"

    table_rows="${table_rows}| ${filename} | ${title} | ${agent} | ${display_status} | ${card_path} |
"

    # 收集 Blocker
    if [ "$blocker" != "無" ] && [ -n "$blocker" ]; then
      blocker_rows="${blocker_rows}| ${agent} | ${filename}: ${blocker} | 見 Task Card |
"
    fi
  done

  # ── 重組 CURRENT_STATUS.md ──
  # 策略：保留靜態區塊，只替換「當前進行中任務」表和「Blockers」和時間戳
  local tmp="${status_file}.tmp"

  # 更新時間戳
  sed "s/^最後更新：.*/最後更新：${today} ${now_time}（checkpoint.sh 自動同步）｜完整歷史存於 \`archive\/CURRENT_STATUS_2026-04-11_full.md\`/" "$status_file" > "$tmp"

  # 替換任務表：從 ## 當前進行中任務 到下一個 ---
  local new_table="## 當前進行中任務

| Task ID | 任務 | 負責 Agent | 狀態 | Task Card |
|---------|------|-----------|------|-----------|
${table_rows}
---"

  # 用 perl 替換多行區塊（從 ## 當前進行中任務 到 ---）
  perl -0777 -i -pe "s/## 當前進行中任務.*?(?=\n---\n\n## )/$(echo "$new_table" | sed 's/[&/\]/\\&/g; s/$/\\n/' | tr -d '\n')\n/s" "$tmp" 2>/dev/null

  # 替換 Blockers 區塊
  if [ -n "$blocker_rows" ]; then
    local new_blockers="## Blockers（只列未解決的）

| 對象 | 問題 | 行動 |
|------|------|------|
${blocker_rows}"
  else
    local new_blockers="## Blockers（只列未解決的）

（無阻塞項目）"
  fi

  # 用 perl 替換 Blockers 區塊（從 ## Blocker 到 ---）
  perl -0777 -i -pe "s/## Blockers.*?(?=\n---\n\n## Source)/$(echo "$new_blockers" | sed 's/[&/\]/\\&/g; s/$/\\n/' | tr -d '\n')\n/s" "$tmp" 2>/dev/null

  # 清除舊的 A1巡查 追加行（> ⚠️ A1巡查 開頭的行）— 這些由 patrol 負責
  # 保留最近一條作為歷史參考
  # 不做：保持向後兼容

  mv "$tmp" "$status_file"
  echo "📊 CURRENT_STATUS.md 自動同步完成（$(echo "$table_rows" | grep -c '^|') 張任務卡）"
}

# === 自動同步 recall 現況區（Phase 2-1: T-A1-V7） ===
_sync_recalls() {
  local role="$1"
  local recalls_dir="$REPO_ROOT/recalls"
  local recall_file="$recalls_dir/${role}_recall.md"

  [ -f "$recall_file" ] || return 0

  # 收集該角色所有進行中的 Task Card 現況
  local sync_content=""
  local card_count=0

  for card in "$TASKS_DIR"/T-${role}-*.md "$TASKS_DIR"/T-${role}[A-Z]*-*.md; do
    [ -f "$card" ] || continue
    grep -q '🔄 進行中' "$card" || continue

    local task_id=$(basename "$card" .md)
    # 提取標題：去掉 # 前綴、Task Card: 前綴、Task ID 前綴
    local title=$(head -1 "$card" | sed -e 's/^# //' -e 's/^Task Card: //' -e "s/^${task_id}[: —–-]*//" | sed 's/^ *//')
    local status="" next="" blocker="" last_activity=""

    # 提取接續狀態區塊的各欄位
    if grep -q '^\- \*\*狀態\*\*' "$card"; then
      status=$(grep '^\- \*\*狀態\*\*' "$card" | sed 's/^- \*\*狀態\*\*: //')
    fi
    if grep -q '^\- \*\*接續點\*\*' "$card"; then
      next=$(grep '^\- \*\*接續點\*\*' "$card" | sed 's/^- \*\*接續點\*\*: //')
    fi
    if grep -q '^\- \*\*阻塞\*\*' "$card"; then
      blocker=$(grep '^\- \*\*阻塞\*\*' "$card" | sed 's/^- \*\*阻塞\*\*: //')
    fi
    if grep -q '^\- \*\*最後活動\*\*' "$card"; then
      last_activity=$(grep '^\- \*\*最後活動\*\*' "$card" | sed 's/^- \*\*最後活動\*\*: //')
    fi

    local display_title="${title:-（無描述）}"
    sync_content="${sync_content}**${task_id}** ${display_title}
- 狀態: ${status:-未標記}
- 接續點: ${next:-未填寫}
- 阻塞: ${blocker:-無}
- 最後活動: ${last_activity:-未記錄}

"
    card_count=$((card_count + 1))
  done

  # 沒有進行中的 Task Card → 寫「無進行中任務」
  if [ "$card_count" -eq 0 ]; then
    sync_content="（無進行中任務）
"
  fi

  local today=$(date +%Y-%m-%d)
  local new_block="<!-- AUTO-SYNC START — checkpoint.sh 自動更新，勿手動修改 -->
## 當前任務現況（自動同步 ${today}）

${sync_content}<!-- AUTO-SYNC END -->"

  # 如果 recall 已有 AUTO-SYNC 區塊 → 替換
  if grep -q '<!-- AUTO-SYNC START' "$recall_file"; then
    # 寫新區塊到暫存檔
    local block_file=$(mktemp)
    echo "$new_block" > "$block_file"
    # 用 bash 逐行處理：遇到 START 標記時輸出新區塊，跳過到 END
    local tmp="${recall_file}.tmp"
    local skip=false
    > "$tmp"
    while IFS= read -r line; do
      if echo "$line" | grep -q '<!-- AUTO-SYNC START'; then
        cat "$block_file" >> "$tmp"
        skip=true
        continue
      fi
      if echo "$line" | grep -q '<!-- AUTO-SYNC END'; then
        skip=false
        continue
      fi
      if [[ "$skip" == false ]]; then
        echo "$line" >> "$tmp"
      fi
    done < "$recall_file"
    rm -f "$block_file"
    mv "$tmp" "$recall_file"
    echo "🔄 Recall 自動同步：${role}_recall.md（${card_count} 張 Task Card）"
  else
    # 沒有 AUTO-SYNC 區塊 → 在第一個 --- 分隔線後插入
    local inserted=false
    local tmp="${recall_file}.tmp"
    > "$tmp"
    while IFS= read -r line; do
      echo "$line" >> "$tmp"
      if [[ "$inserted" == false ]] && [[ "$line" == "---" ]]; then
        inserted=true
        echo "" >> "$tmp"
        echo "$new_block" >> "$tmp"
      fi
    done < "$recall_file"

    if [[ "$inserted" == true ]]; then
      mv "$tmp" "$recall_file"
      echo "🔄 Recall 自動同步（首次）：${role}_recall.md（${card_count} 張 Task Card）"
    else
      # 沒有 --- 分隔線，附加到檔案末尾
      echo "" >> "$recall_file"
      echo "$new_block" >> "$recall_file"
      rm -f "$tmp"
      echo "🔄 Recall 自動同步（附加）：${role}_recall.md（${card_count} 張 Task Card）"
    fi
  fi
}

# Parse --fast flag（位置不限）
for arg in "$@"; do
  [ "$arg" = "--fast" ] && FAST_MODE=true
done

if [ -z "$ROLE" ] || [ -z "$MESSAGE" ]; then
  echo "❌ 用法：bash scripts/checkpoint.sh \"角色名\" \"做了什麼\" [--fast]"
  echo "   角色名：A0 / A1 / A2 / A4 / A5 / A6 / A7 / A8"
  exit 1
fi

COMMIT_MSG="checkpoint($ROLE): $MESSAGE"
WORKTREE_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
TODAY=$(date +%Y%m%d)
AGENT_BRANCH="agent/$ROLE-$TODAY"

echo "======================================"
echo "🔄 CHECKPOINT 存檔流程啟動"
echo "   角色：$ROLE"
echo "   訊息：$MESSAGE"
if [ "$FAST_MODE" = true ]; then
  echo "   模式：⚡ --fast（直接進 main）"
else
  echo "   模式：🔒 branch 模式（需 Owner approve 才進 main）"
fi
echo "======================================"
echo ""

# 確認有沒有變更
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
  echo "ℹ️  沒有需要存檔的變更，跳過。"
  exit 0
fi

echo "📋 變更清單："
git status --short
echo ""

# ============================================================
# FAST MODE：直接 commit → cherry-pick 到 main → push（原有行為）
# ============================================================
if [ "$FAST_MODE" = true ]; then

  echo "📁 [1/4] 暫存所有變更..."
  git add -A && echo "       ✅ 完成" || { echo "❌ git add 失敗"; exit 1; }

  echo "💾 [2/4] Commit..."
  git commit -m "$COMMIT_MSG" || { echo "❌ git commit 失敗"; exit 1; }
  HASH=$(git rev-parse HEAD)
  SHORT="${HASH:0:7}"
  echo "       ✅ $SHORT — $COMMIT_MSG"
  echo ""

  if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🍒 [3/4] Cherry-pick 到 main..."
    cd "$REPO_ROOT"
    [ "$(git branch --show-current)" != "main" ] && git checkout main
    if git cherry-pick "$HASH"; then
      echo "       ✅ Cherry-pick 完成"
    else
      echo "⚠️  發現衝突，嘗試自動解（theirs 策略）..."
      git checkout --theirs . 2>/dev/null || true
      git add -A
      if git cherry-pick --continue --no-edit; then
        echo "       ✅ 衝突已自動解決"
      else
        echo "❌ Cherry-pick 失敗，請手動處理"
        git cherry-pick --abort 2>/dev/null || true
        exit 1
      fi
    fi
  else
    echo "⏭️  [3/4] 已在 main branch，跳過 cherry-pick"
    cd "$REPO_ROOT"
  fi

  echo "🚀 [4/4] Push main 到 remote..."
  if git push origin main; then
    echo "       ✅ Push 完成"
  else
    echo "⚠️  Push 失敗，嘗試 pull --rebase..."
    if git pull --rebase origin main && git push origin main; then
      echo "       ✅ Push 完成（rebase 後）"
    else
      echo "❌ Push 失敗，請手動處理"
      exit 1
    fi
  fi

  cd "$WORKTREE_DIR"

  echo ""
  echo "🔍 驗證 main 是否包含此次 commit..."
  bash "$WORKTREE_DIR/scripts/verify-commit-on-main.sh" "$HASH"

  # === 自動更新 Task Card 最後活動 ===
  _update_task_cards "$ROLE" "$SHORT"

  # === 自動同步 recall 現況區 ===
  _sync_recalls "$ROLE"

  # === 自動同步 CURRENT_STATUS.md ===
  _sync_current_status

  echo ""
  echo "======================================"
  echo "✅ 存檔完成（fast mode）"
  echo "   Commit: $SHORT"
  echo "   main 已同步到 remote。"
  echo "======================================"

# ============================================================
# 預設模式：commit 到 agent branch，push branch，等 Owner approve
# ============================================================
else

  # 如果在 main，切換到 agent branch（uncommitted changes 會跟過去）
  if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "🌿 [1/3] 切換到 agent branch: $AGENT_BRANCH"
    if git checkout -b "$AGENT_BRANCH" 2>/dev/null || git checkout "$AGENT_BRANCH" 2>/dev/null; then
      echo "       ✅ 完成"
    else
      echo "❌ 無法切換到 $AGENT_BRANCH"
      exit 1
    fi
  else
    # 已在 agent branch 或其他 branch，直接用
    AGENT_BRANCH="$CURRENT_BRANCH"
    echo "🌿 [1/3] 使用現有 branch: $AGENT_BRANCH"
  fi

  echo "💾 [2/3] 暫存 + Commit..."
  git add -A && git commit -m "$COMMIT_MSG" || { echo "❌ commit 失敗"; exit 1; }
  HASH=$(git rev-parse HEAD)
  SHORT="${HASH:0:7}"
  echo "       ✅ $SHORT — $COMMIT_MSG"
  echo ""

  echo "🚀 [3/3] Push $AGENT_BRANCH 到 remote..."
  if git push origin "$AGENT_BRANCH" 2>/dev/null || git push --set-upstream origin "$AGENT_BRANCH"; then
    echo "       ✅ Push 完成"
  else
    echo "❌ Push 失敗"
    exit 1
  fi

  # === 自動更新 Task Card 最後活動 ===
  _update_task_cards "$ROLE" "$SHORT"

  # === 自動同步 recall 現況區 ===
  _sync_recalls "$ROLE"

  # === 自動同步 CURRENT_STATUS.md ===
  _sync_current_status

  echo ""
  echo "======================================"
  echo "✅ 存檔完成（branch 模式）"
  echo "   Commit: $SHORT"
  echo "   Branch: $AGENT_BRANCH"
  echo ""
  echo "⚠️  尚未進入 main。Owner 確認後執行："
  echo "   bash scripts/approve.sh $AGENT_BRANCH"
  echo "======================================"
fi
