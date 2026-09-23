#!/usr/bin/env bash
# A0 Continuity Watchdog tick.
# Owner approval: 2026-08-23 15:05. This runner never changes Claude permissions.

set -uo pipefail

export PATH="/Users/pagemacmini/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

CDO_ROOT="${A0_CDO_ROOT:-/Users/pagemacmini/claude-daily-operations}"
STATE_DIR="${A0_STATE_DIR:-${CDO_ROOT}/state}"
HEARTBEAT_FILE="${A0_HEARTBEAT_FILE:-${STATE_DIR}/a0_heartbeat.json}"
SESSION_FILE="${A0_SESSION_FILE:-${STATE_DIR}/a0_session.json}"
LOCK_FILE="${A0_LOCK_FILE:-${STATE_DIR}/a0_resume.lock}"
STATUS_FILE="${A0_STATUS_FILE:-${STATE_DIR}/a0_continuity_status.json}"
LOG_FILE="${A0_LOG_FILE:-${STATE_DIR}/a0_continuity.log}"
PROMPT_FILE="${A0_PROMPT_FILE:-/Users/pagemacmini/maplab-ai-handbook/scripts/a0_recall_prompt.md}"
CLAUDE_BIN="${A0_CLAUDE_BIN:-/Users/pagemacmini/.local/bin/claude}"
MODEL="claude-fable-5"

HEARTBEAT_MAX_AGE_SECONDS="${A0_HEARTBEAT_MAX_AGE_SECONDS:-600}"
TIMEOUT_SECONDS="${A0_TIMEOUT_SECONDS:-1500}"
LOG_MAX_BYTES="${A0_LOG_MAX_BYTES:-2097152}"
DRY_RUN="${DRY_RUN:-0}"
JQ_BIN="${A0_JQ_BIN:-$(command -v jq 2>/dev/null || true)}"

LOCK_OWNED=0
LOCK_HOLDER_PID=""
CHILD_PID=""
TIMER_PID=""
TMP_STDOUT=""
TMP_STDERR=""
TIMEOUT_MARKER=""

wall_epoch() {
  date +%s
}

now_epoch() {
  if [[ "${A0_NOW_EPOCH:-}" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "$A0_NOW_EPOCH"
  else
    wall_epoch
  fi
}

format_epoch() {
  local epoch="$1"
  if date -r "$epoch" "+%Y-%m-%dT%H:%M:%S%z" 2>/dev/null; then
    return 0
  fi
  date -d "@${epoch}" "+%Y-%m-%dT%H:%M:%S%z" 2>/dev/null
}

iso_now() {
  format_epoch "$(now_epoch)"
}

parse_epoch() {
  local raw="$1"
  if [[ "$raw" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "$raw"
    return 0
  fi
  if date -j -f "%Y-%m-%dT%H:%M:%S%z" "$raw" "+%s" 2>/dev/null; then
    return 0
  fi
  date -d "$raw" "+%s" 2>/dev/null
}

is_positive_integer() {
  [[ "$1" =~ ^[1-9][0-9]*$ ]]
}

rotate_log_if_needed() {
  local size=0
  [[ -f "$LOG_FILE" ]] || return 0
  size=$(wc -c < "$LOG_FILE" 2>/dev/null | tr -d '[:space:]' || printf '0')
  if [[ "$size" =~ ^[0-9]+$ ]] && (( size > LOG_MAX_BYTES )); then
    mv -f "$LOG_FILE" "${LOG_FILE}.1"
  fi
}

log_line() {
  rotate_log_if_needed
  printf '%s %s\n' "$(iso_now)" "$*" >> "$LOG_FILE"
}

write_status() {
  local mode="$1"
  local started="$2"
  local ended="$3"
  local exit_code="$4"
  local next_retry="${5:-}"
  local tmp="${STATUS_FILE}.$$.$RANDOM.tmp"

  if ! "$JQ_BIN" -n \
    --arg mode "$mode" \
    --arg started "$started" \
    --arg ended "$ended" \
    --argjson exit_code "$exit_code" \
    --arg next_retry "$next_retry" \
    '{mode:$mode, started:$started, ended:$ended, exit_code:$exit_code,
      next_retry:(if $next_retry == "" then null else $next_retry end)}' > "$tmp"; then
    rm -f "$tmp"
    return 1
  fi
  mv -f "$tmp" "$STATUS_FILE"
}

lock_pid() {
  local pid=""
  [[ -f "$LOCK_FILE" ]] || return 1
  IFS= read -r pid < "$LOCK_FILE" || true
  if [[ "$pid" =~ ^[1-9][0-9]*$ ]]; then
    printf '%s\n' "$pid"
    return 0
  fi
  return 1
}

acquire_lock() {
  local existing_pid=""
  local attempt

  for attempt in 1 2; do
    if [[ -e "$LOCK_FILE" ]]; then
      existing_pid=$(lock_pid || true)
      if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
        LOCK_HOLDER_PID="$existing_pid"
        return 1
      fi
      if ! rm -f "$LOCK_FILE" 2>/dev/null; then
        LOCK_HOLDER_PID="unknown"
        return 1
      fi
      log_line "removed stale lock pid=${existing_pid:-invalid}"
    fi

    if ( set -o noclobber; printf '%s\n' "$$" > "$LOCK_FILE" ) 2>/dev/null; then
      LOCK_OWNED=1
      return 0
    fi
  done

  LOCK_HOLDER_PID=$(lock_pid || printf 'unknown')
  return 1
}

release_lock() {
  local existing_pid=""
  (( LOCK_OWNED == 1 )) || return 0
  existing_pid=$(lock_pid || true)
  if [[ "$existing_pid" == "$$" ]]; then
    rm -f "$LOCK_FILE"
  fi
  LOCK_OWNED=0
}

cleanup() {
  if [[ -n "$TIMER_PID" ]] && kill -0 "$TIMER_PID" 2>/dev/null; then
    kill "$TIMER_PID" 2>/dev/null || true
    wait "$TIMER_PID" 2>/dev/null || true
  fi
  if [[ -n "$CHILD_PID" ]] && kill -0 "$CHILD_PID" 2>/dev/null; then
    kill "$CHILD_PID" 2>/dev/null || true
    wait "$CHILD_PID" 2>/dev/null || true
  fi
  [[ -z "$TMP_STDOUT" ]] || rm -f "$TMP_STDOUT"
  [[ -z "$TMP_STDERR" ]] || rm -f "$TMP_STDERR"
  [[ -z "$TIMEOUT_MARKER" ]] || rm -f "$TIMEOUT_MARKER"
  release_lock
}

trap cleanup EXIT
trap 'exit 130' HUP INT TERM

append_stream_to_log() {
  local label="$1"
  local source_file="$2"
  local line=""
  [[ -s "$source_file" ]] || return 0
  while IFS= read -r line || [[ -n "$line" ]]; do
    log_line "${label} | ${line}"
  done < "$source_file"
}

is_quota_error() {
  local source_file="$1"
  [[ -s "$source_file" ]] || return 1
  LC_ALL=C grep -Eiq 'session limit|usage limit|rate limit' "$source_file"
}

compute_next_retry() {
  local source_file="$1"
  local current_epoch="$2"
  local reset_phrase=""
  local hm=""
  local hour=""
  local minute=""
  local normalized_hm=""
  local today=""
  local target_epoch=""

  reset_phrase=$(LC_ALL=C grep -Eio 'resets([[:space:]]+at)?[[:space:]]+[0-2]?[0-9]:[0-5][0-9]' "$source_file" | head -n 1 || true)
  hm=$(printf '%s' "$reset_phrase" | grep -Eo '[0-2]?[0-9]:[0-5][0-9]' | tail -n 1 || true)

  if [[ -n "$hm" ]]; then
    hour="${hm%%:*}"
    minute="${hm##*:}"
    if (( 10#$hour <= 23 )); then
      printf -v normalized_hm '%02d:%02d' "$((10#$hour))" "$((10#$minute))"
      today=$(date "+%Y-%m-%d")
      target_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "${today} ${normalized_hm}:00" "+%s" 2>/dev/null || true)
      if [[ -z "$target_epoch" ]]; then
        target_epoch=$(date -d "${today} ${normalized_hm}:00" "+%s" 2>/dev/null || true)
      fi
    fi
  fi

  if ! [[ "$target_epoch" =~ ^[0-9]+$ ]]; then
    target_epoch=$(( current_epoch + 1800 ))
  elif (( target_epoch <= current_epoch )); then
    target_epoch=$(( target_epoch + 86400 ))
  fi

  format_epoch "$target_epoch"
}

run_claude() {
  local mode="$1"
  local -a command=("$CLAUDE_BIN")
  local rc=0
  local timed_out=0

  if [[ "$mode" == "resume" ]]; then
    command+=(--resume "$SESSION_ID")
  fi
  command+=(--model "$MODEL" -p --output-format text --max-turns 40)

  if [[ "$DRY_RUN" == "1" ]]; then
    log_line "dry_run mode=${mode} command=${command[*]} stdin=${PROMPT_FILE}"
    return 0
  fi

  : > "$TMP_STDOUT"
  : > "$TMP_STDERR"
  rm -f "$TIMEOUT_MARKER"
  log_line "invoke mode=${mode} model=${MODEL} timeout_s=${TIMEOUT_SECONDS}"

  "${command[@]}" < "$PROMPT_FILE" > "$TMP_STDOUT" 2> "$TMP_STDERR" &
  CHILD_PID=$!

  (
    sleep "$TIMEOUT_SECONDS"
    if kill -0 "$CHILD_PID" 2>/dev/null; then
      printf 'timeout\n' > "$TIMEOUT_MARKER"
      kill "$CHILD_PID" 2>/dev/null || true
      sleep 5
      kill -9 "$CHILD_PID" 2>/dev/null || true
    fi
  ) &
  TIMER_PID=$!

  wait "$CHILD_PID"
  rc=$?
  CHILD_PID=""

  if kill -0 "$TIMER_PID" 2>/dev/null; then
    kill "$TIMER_PID" 2>/dev/null || true
  fi
  wait "$TIMER_PID" 2>/dev/null || true
  TIMER_PID=""

  if [[ -f "$TIMEOUT_MARKER" ]]; then
    timed_out=1
    rc=124
  fi

  append_stream_to_log "${mode} stdout" "$TMP_STDOUT"
  append_stream_to_log "${mode} stderr" "$TMP_STDERR"
  if (( timed_out == 1 )); then
    log_line "${mode} timeout: child killed and reaped after ${TIMEOUT_SECONDS}s"
  else
    log_line "${mode} completed exit_code=${rc}"
  fi
  return "$rc"
}

main() {
  local tick_started=""
  local current_epoch=""
  local previous_mode=""
  local previous_next_retry=""
  local previous_retry_epoch=""
  local heartbeat_ts=""
  local heartbeat_epoch=""
  local heartbeat_age=""
  local session_id=""
  local resume_rc=0
  local fresh_rc=0
  local next_retry=""

  if [[ -z "$JQ_BIN" ]] || [[ ! -x "$JQ_BIN" ]]; then
    printf 'A0 continuity: jq is required but was not found\n' >&2
    return 127
  fi
  for value in "$HEARTBEAT_MAX_AGE_SECONDS" "$TIMEOUT_SECONDS" "$LOG_MAX_BYTES"; do
    if ! is_positive_integer "$value"; then
      printf 'A0 continuity: invalid positive integer: %s\n' "$value" >&2
      return 2
    fi
  done

  mkdir -p "$STATE_DIR" "$(dirname "$LOCK_FILE")" "$(dirname "$STATUS_FILE")" "$(dirname "$LOG_FILE")" || return 1
  if ! : >> "$LOG_FILE"; then
    printf 'A0 continuity: log is not writable: %s\n' "$LOG_FILE" >&2
    return 1
  fi

  tick_started=$(iso_now)
  current_epoch=$(now_epoch)

  if [[ -f "$STATUS_FILE" ]]; then
    previous_mode=$("$JQ_BIN" -r '.mode // empty' "$STATUS_FILE" 2>/dev/null || true)
    previous_next_retry=$("$JQ_BIN" -r '.next_retry // empty' "$STATUS_FILE" 2>/dev/null || true)
    previous_retry_epoch=$(parse_epoch "$previous_next_retry" 2>/dev/null || true)
    if [[ "$previous_mode" == "quota_blocked" ]] && [[ "$previous_retry_epoch" =~ ^[0-9]+$ ]] && (( current_epoch < previous_retry_epoch )); then
      log_line "quota backoff active next_retry=${previous_next_retry}; tick skipped"
      write_status "quota_blocked" "$tick_started" "$(iso_now)" 0 "$previous_next_retry"
      return 0
    fi
  fi

  if [[ -f "$HEARTBEAT_FILE" ]]; then
    heartbeat_ts=$("$JQ_BIN" -r '.ts // empty' "$HEARTBEAT_FILE" 2>/dev/null || true)
    heartbeat_epoch=$(parse_epoch "$heartbeat_ts" 2>/dev/null || true)
  fi

  if [[ "$heartbeat_epoch" =~ ^[0-9]+$ ]]; then
    heartbeat_age=$(( current_epoch - heartbeat_epoch ))
    (( heartbeat_age < 0 )) && heartbeat_age=0
  else
    heartbeat_age="$HEARTBEAT_MAX_AGE_SECONDS"
    log_line "heartbeat missing or invalid; treating as stale file=${HEARTBEAT_FILE}"
  fi

  if (( heartbeat_age < HEARTBEAT_MAX_AGE_SECONDS )); then
    log_line "skipped_alive heartbeat_age_s=${heartbeat_age}"
    write_status "skipped_alive" "$tick_started" "$(iso_now)" 0 ""
    return 0
  fi

  if ! acquire_lock; then
    log_line "locked holder_pid=${LOCK_HOLDER_PID:-unknown} heartbeat_age_s=${heartbeat_age}"
    write_status "locked" "$tick_started" "$(iso_now)" 0 ""
    return 0
  fi

  if [[ ! -r "$PROMPT_FILE" ]]; then
    log_line "failed recall prompt missing or unreadable file=${PROMPT_FILE}"
    write_status "failed" "$tick_started" "$(iso_now)" 66 ""
    return 66
  fi
  if [[ ! -x "$CLAUDE_BIN" ]]; then
    log_line "failed claude binary missing or not executable file=${CLAUDE_BIN}"
    write_status "failed" "$tick_started" "$(iso_now)" 127 ""
    return 127
  fi

  TMP_STDOUT=$(mktemp "${TMPDIR:-/tmp}/a0-continuity.stdout.XXXXXX") || return 1
  TMP_STDERR=$(mktemp "${TMPDIR:-/tmp}/a0-continuity.stderr.XXXXXX") || return 1
  TIMEOUT_MARKER=$(mktemp "${TMPDIR:-/tmp}/a0-continuity.timeout.XXXXXX") || return 1
  rm -f "$TIMEOUT_MARKER"

  if [[ -f "$SESSION_FILE" ]]; then
    session_id=$("$JQ_BIN" -r '.session_id // empty' "$SESSION_FILE" 2>/dev/null || true)
  fi
  SESSION_ID="$session_id"

  if [[ -n "$SESSION_ID" ]]; then
    run_claude "resume"
    resume_rc=$?
    if (( resume_rc == 0 )); then
      write_status "resume" "$tick_started" "$(iso_now)" 0 ""
      return 0
    fi
    if is_quota_error "$TMP_STDERR"; then
      next_retry=$(compute_next_retry "$TMP_STDERR" "$current_epoch")
      log_line "quota_blocked after resume exit_code=${resume_rc} next_retry=${next_retry}"
      write_status "quota_blocked" "$tick_started" "$(iso_now)" "$resume_rc" "$next_retry"
      return 0
    fi
    log_line "resume failed exit_code=${resume_rc}; falling back to fresh"
  else
    log_line "resume unavailable: session_id missing; falling back to fresh"
  fi

  run_claude "fresh"
  fresh_rc=$?
  if (( fresh_rc == 0 )); then
    write_status "fresh" "$tick_started" "$(iso_now)" 0 ""
    return 0
  fi
  if is_quota_error "$TMP_STDERR"; then
    next_retry=$(compute_next_retry "$TMP_STDERR" "$current_epoch")
    log_line "quota_blocked after fresh exit_code=${fresh_rc} next_retry=${next_retry}"
    write_status "quota_blocked" "$tick_started" "$(iso_now)" "$fresh_rc" "$next_retry"
    return 0
  fi

  log_line "failed after fresh exit_code=${fresh_rc}"
  write_status "failed" "$tick_started" "$(iso_now)" "$fresh_rc" ""
  return "$fresh_rc"
}

main "$@"
