#!/bin/bash
# DeerFlow protected env 金鑰接線 — 照 scripts/hermes_gateway_setup.sh 同模式
#   - 金鑰不經過對話、不進 git:OPENROUTER_API_KEY 直接從 ~/.maplab/free_compute.env
#     複製進 DeerFlow checkout 的 .env(寫入前先驗證 .env 已被 gitignore)
#   - 本腳本只搬「變數名=值」整行,任何情況下不 echo 金鑰值
set -euo pipefail

CHECKOUT="/Volumes/MacExternal/MAPLAB_WORKSPACE/tools/deer-flow"
ENV_FILE="$CHECKOUT/.env"
FREE_ENV="/Users/pagemacmini/.maplab/free_compute.env"

if [ ! -d "$CHECKOUT" ]; then
  echo "[setup] 錯誤: DeerFlow checkout 不存在 $CHECKOUT"
  exit 1
fi

# .env 必須被 gitignore,否則金鑰會進 git — 直接拒絕
if ! git -C "$CHECKOUT" check-ignore -q .env; then
  echo "[setup] 錯誤: $CHECKOUT 的 .env 沒有被 gitignore,拒絕寫入金鑰"
  exit 1
fi

if grep -q "^OPENROUTER_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  echo "[setup] OPENROUTER_API_KEY 已存在於 DeerFlow .env,略過"
elif grep -q "^OPENROUTER_API_KEY=" "$FREE_ENV" 2>/dev/null; then
  touch "$ENV_FILE"
  grep "^OPENROUTER_API_KEY=" "$FREE_ENV" >> "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo "[setup] OPENROUTER_API_KEY 已從 free_compute.env 複製進 DeerFlow .env(chmod 600)"
else
  echo "[setup] 警告: $FREE_ENV 沒有 OPENROUTER_API_KEY,無法接線"
  exit 1
fi

echo "[setup] done"
