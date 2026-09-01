#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
repo_root="${script_dir:h:h}"
private_root="${HERMES_MLX_PRIVATE_ROOT:-/Users/pagemacmini/.maplab/a6-hermes-training/mlx}"
public_root="${HERMES_MLX_PUBLIC_ROOT:-/Volumes/MacExternal/MAPLAB_PUBLIC_MODELS}"
python_env="$private_root/runtime/.venv"
model_dir="$public_root/huggingface/mlx-community/Qwen3-4B-Instruct-2507-4bit"
data_dir="$repo_root/tests/fixtures/hermes_mlx_smoke"
run_id="synthetic-smoke-qwen3-4b-instruct-2507-$(date -u +%Y%m%dT%H%M%SZ)"
adapter_dir="$private_root/adapters/$run_id"
sandbox_profile='(version 1)(allow default)(deny network*)'

if [[ ! -x "$python_env/bin/mlx_lm.lora" || ! -f "$model_dir/model.safetensors" ]]; then
  print -u2 "Hermes MLX lab is not bootstrapped."
  exit 2
fi

umask 077
mkdir -p "$adapter_dir"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export WANDB_DISABLED=true

sandbox-exec -p "$sandbox_profile" "$python_env/bin/mlx_lm.lora" \
  --model "$model_dir" \
  --train \
  --data "$data_dir" \
  --adapter-path "$adapter_dir" \
  --fine-tune-type lora \
  --mask-prompt \
  --batch-size 1 \
  --grad-accumulation-steps 1 \
  --num-layers 2 \
  --iters 3 \
  --max-seq-length 256 \
  --learning-rate 1e-5 \
  --steps-per-report 1 \
  --steps-per-eval 1 \
  --val-batches 1 \
  --save-every 1 \
  --test \
  --test-batches 1 \
  --seed 17

find "$adapter_dir" -maxdepth 1 -type f -exec chmod 600 {} +

sandbox-exec -p "$sandbox_profile" "$python_env/bin/mlx_lm.generate" \
  --model "$model_dir" \
  --adapter-path "$adapter_dir" \
  --system-prompt "你是台灣活動餐飲業務助理。只使用客戶已提供的資訊；缺少價格依據時不得報價。回覆要短，最多問三題。" \
  --prompt "公司要辦茶會，日期是9月20日，約40人，希望由同一窗口協助，但還沒提供地點、預算與餐飲限制。請回覆第一則訊息。" \
  --max-tokens 96 \
  --temp 0 \
  --verbose true

print "adapter=$adapter_dir"
print "network=denied"
print "data=synthetic_only"
print "quality_claim=false"
