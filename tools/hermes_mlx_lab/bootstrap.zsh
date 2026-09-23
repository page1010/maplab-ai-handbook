#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
private_root="${HERMES_MLX_PRIVATE_ROOT:-/Users/pagemacmini/.maplab/a6-hermes-training/mlx}"
public_root="${HERMES_MLX_PUBLIC_ROOT:-/Volumes/MacExternal/MAPLAB_PUBLIC_MODELS}"
runtime_python="${HERMES_MLX_PYTHON:-/Users/pagemacmini/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12}"
uv_bin="${HERMES_MLX_UV:-/opt/homebrew/bin/uv}"
model_repo="mlx-community/Qwen3-4B-Instruct-2507-4bit"
model_revision="50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b"
model_dir="$public_root/huggingface/$model_repo"
uv_cache="$public_root/uv-cache"
hf_cache="$public_root/huggingface-cache"

if [[ ! -d /Volumes/MacExternal ]]; then
  print -u2 "External volume is not mounted: /Volumes/MacExternal"
  exit 2
fi
if [[ ! -x "$uv_bin" || ! -x "$runtime_python" ]]; then
  print -u2 "Required uv or Python 3.12 runtime is unavailable."
  exit 2
fi

umask 077
mkdir -p "$private_root"/{runtime,datasets,adapters,receipts,tmp}
chmod 700 "$private_root" "$private_root"/{runtime,datasets,adapters,receipts,tmp}
mkdir -p "$public_root"/{uv-cache,huggingface-cache} "${model_dir:h}"

UV_CACHE_DIR="$uv_cache" "$uv_bin" venv --python "$runtime_python" "$private_root/runtime/.venv"
UV_CACHE_DIR="$uv_cache" UV_LINK_MODE=copy "$uv_bin" pip install \
  --python "$private_root/runtime/.venv/bin/python" \
  --only-binary=:all: \
  --requirements "$script_dir/requirements.lock"

HF_HOME="$hf_cache" "$private_root/runtime/.venv/bin/hf" download \
  "$model_repo" \
  --revision "$model_revision" \
  --local-dir "$model_dir"

"$private_root/runtime/.venv/bin/python" -c \
  'import importlib.metadata as m; print("mlx=" + m.version("mlx")); print("mlx-lm=" + m.version("mlx-lm"))'
print "runtime=$private_root/runtime/.venv"
print "public_model=$model_dir"
print "production_route=disabled"
