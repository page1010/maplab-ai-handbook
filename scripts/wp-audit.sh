#!/bin/bash
# WP 內容稽核腳本
# 用法：./scripts/wp-audit.sh <post_id>  或  ./scripts/wp-audit.sh --all
# 禁用詞來源：skills/seo-session-checklist.md

WP_URL="https://www.maplabkitchen.com/wp-json/wp/v2"
# 認證從環境變數讀（安全考量，不 hardcode）
AUTH="${WP_USER}:${WP_APP_PASSWORD}"

if [ -z "$WP_USER" ] || [ -z "$WP_APP_PASSWORD" ]; then
  AUTH=""
fi

check_post() {
  local POST_ID=$1
  local RESPONSE

  if [ -n "$AUTH" ]; then
    RESPONSE=$(curl -s -u "$AUTH" "$WP_URL/posts/$POST_ID?context=edit")
  else
    RESPONSE=$(curl -s "$WP_URL/posts/$POST_ID")
  fi

  local CONTENT=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('content', {}).get('rendered', d.get('content', {}).get('raw', '')))" 2>/dev/null)
  local TITLE=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('title', {}).get('rendered', ''))" 2>/dev/null)

  local FAIL=0

  # 檢查 1：HTML 違規標籤
  if echo "$CONTENT" | grep -qE '<script|<style'; then
    echo "❌ FAIL [$POST_ID] $TITLE — 含 <script> 或 <style> 標籤"
    FAIL=1
  fi

  # 檢查 2：JSON-LD 重複
  if echo "$CONTENT" | grep -q 'application/ld+json'; then
    echo "❌ FAIL [$POST_ID] $TITLE — content 含 JSON-LD schema（應由 Rank Math 處理）"
    FAIL=1
  fi

  # 檢查 3：禁用詞（從 seo-session-checklist.md 動態讀）
  local FORBIDDEN="無麩質|Gluten-free|gluten.free|ESG 認證|SDG|醫療級|第三方認證"
  if echo "$CONTENT" | grep -qE "$FORBIDDEN"; then
    echo "❌ FAIL [$POST_ID] $TITLE — 含禁用詞"
    echo "$CONTENT" | grep -oE "$FORBIDDEN" | head -3
    FAIL=1
  fi

  # 檢查 4：過度承諾
  local OVERCLAIM="保證.*完全|100%.*保證|絕對.*無"
  if echo "$CONTENT" | grep -qE "$OVERCLAIM"; then
    echo "⚠️ WARN [$POST_ID] $TITLE — 含過度承諾字眼"
    FAIL=1
  fi

  if [ $FAIL -eq 0 ]; then
    echo "✅ PASS [$POST_ID] $TITLE"
  fi

  return $FAIL
}

if [ "$1" == "--all" ]; then
  echo "🔍 稽核全站文章..."
  curl -s "$WP_URL/posts?per_page=100&_fields=id" | python3 -c "import sys,json; [print(p['id']) for p in json.load(sys.stdin)]" | while read ID; do
    check_post "$ID"
  done
elif [ -n "$1" ]; then
  check_post "$1"
else
  echo "用法：$0 <post_id>  或  $0 --all"
  exit 1
fi
