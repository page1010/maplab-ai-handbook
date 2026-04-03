#!/bin/bash
# update_extension.sh — 拉最新 Extension 程式碼
# 用法：bash scripts/update_extension.sh

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "📦 更新 MAPLAB Extension..."
cd "$REPO_DIR"
git pull origin main

echo ""
echo "✅ 程式碼已更新到最新版"
echo ""
echo "最後一步（5秒）："
echo "  → 開 Extension popup → 點「⟳ 重載 Extension」"
echo "  → Extension 自動從磁碟重載，完成。"
