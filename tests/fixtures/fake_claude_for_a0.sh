#!/usr/bin/env bash

set -u

printf '%s\n' "$*" >> "${FAKE_CLAUDE_CALLS:?FAKE_CLAUDE_CALLS is required}"

case "${FAKE_CLAUDE_MODE:-resume_success}" in
  resume_success)
    printf '%s\n' 'fake resume ok'
    exit 0
    ;;
  quota_blocked)
    printf '%s\n' 'usage limit reached; resets 23:59' >&2
    exit 1
    ;;
  resume_fail_fresh_success)
    for arg in "$@"; do
      if [[ "$arg" == "--resume" ]]; then
        printf '%s\n' 'session not found' >&2
        exit 7
      fi
    done
    printf '%s\n' 'fake fresh ok'
    exit 0
    ;;
  *)
    printf 'unknown fake mode: %s\n' "$FAKE_CLAUDE_MODE" >&2
    exit 64
    ;;
esac
