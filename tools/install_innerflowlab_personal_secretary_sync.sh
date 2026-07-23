#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
repo_root="${script_dir:h}"
label="com.maplab.innerflowlab-personal-secretary-sync"
plist_source="${repo_root}/launchd/${label}.plist"
plist_target="${HOME}/Library/LaunchAgents/${label}.plist"
wp_user="${IFL_WP_USER:-pagewu1010@gmail.com}"
keychain_service="${IFL_WP_KEYCHAIN_SERVICE:-com.maplab.innerflowlab-personal-secretary}"

if [[ "${repo_root}" != "/Users/pagemacmini/maplab-ai-handbook" ]]; then
  print -u2 "Install blocked: merge this branch into the canonical repo first."
  print -u2 "Expected /Users/pagemacmini/maplab-ai-handbook, got ${repo_root}."
  exit 78
fi

if ! /usr/bin/security find-generic-password \
  -s "${keychain_service}" \
  -a "${wp_user}" >/dev/null 2>&1; then
  print -u2 "Install blocked: add the WordPress application password to Keychain first."
  exit 78
fi

/usr/bin/plutil -lint "${plist_source}"
mkdir -p "${HOME}/Library/LaunchAgents"
mkdir -p "/Users/pagemacmini/.local/share/investmentos-telegram-operator/logs/launchd"
/bin/cp "${plist_source}" "${plist_target}"

/bin/launchctl bootout "gui/$(id -u)/${label}" >/dev/null 2>&1 || true
/bin/launchctl bootstrap "gui/$(id -u)" "${plist_target}"
/bin/launchctl kickstart -k "gui/$(id -u)/${label}"
/bin/launchctl print "gui/$(id -u)/${label}"

