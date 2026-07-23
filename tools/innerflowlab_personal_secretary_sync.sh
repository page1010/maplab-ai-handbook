#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
repo_root="${script_dir:h}"

wp_base_url="${IFL_WP_BASE_URL:-https://innerflowlab.com}"
wp_user="${IFL_WP_USER:-pagewu1010@gmail.com}"
keychain_service="${IFL_WP_KEYCHAIN_SERVICE:-com.maplab.innerflowlab-personal-secretary}"
security_bin="${IFL_SECURITY_BIN:-/usr/bin/security}"
python_bin="${IFL_PYTHON_BIN:-/opt/homebrew/bin/python3}"
ios_repo="${IFL_IOS_REPO:-/Users/pagemacmini/Documents/New project}"
ios_runtime_root="${IFL_IOS_RUNTIME_ROOT:-/Users/pagemacmini/.local/share/investmentos-telegram-operator}"
receipt_dir="${ios_runtime_root}/reviews/innerflowlab-personal-secretary"

if [[ ! -x "${security_bin}" ]]; then
  print -u2 "InnerFlowLab sync blocked: security command is unavailable."
  exit 69
fi

if [[ ! -x "${python_bin}" ]]; then
  print -u2 "InnerFlowLab sync blocked: Python runtime is unavailable."
  exit 69
fi

if ! wp_app_password="$("${security_bin}" find-generic-password \
  -w \
  -s "${keychain_service}" \
  -a "${wp_user}" 2>/dev/null)"; then
  print -u2 "InnerFlowLab sync blocked: WordPress application password is not in Keychain."
  exit 78
fi
trap 'unset wp_app_password' EXIT

mkdir -p "${receipt_dir}"

IFL_WP_BASE_URL="${wp_base_url}" \
IFL_WP_USER="${wp_user}" \
IFL_WP_APP_PASSWORD="${wp_app_password}" \
"${python_bin}" "${repo_root}/tools/innerflowlab_personal_secretary_snapshot.py" \
  --maplab-repo "${repo_root}" \
  --ios-repo "${ios_repo}" \
  --ios-runtime-root "${ios_runtime_root}" \
  --output "${receipt_dir}/snapshot.json" \
  --push

