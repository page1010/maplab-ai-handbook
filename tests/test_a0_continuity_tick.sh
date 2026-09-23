#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TICK_SCRIPT="${REPO_ROOT}/scripts/a0_continuity_tick.sh"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/a0-continuity-tests.XXXXXX")
PASS_COUNT=0

cleanup() {
  if [[ -n "${TEST_ROOT:-}" ]] && [[ "$TEST_ROOT" == "${TMPDIR:-/tmp}/a0-continuity-tests."* ]]; then
    rm -rf -- "$TEST_ROOT"
  fi
}
trap cleanup EXIT

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  printf 'PASS %d/5: %s\n' "$PASS_COUNT" "$1"
}

assert_eq() {
  local expected="$1"
  local actual="$2"
  local label="$3"
  [[ "$actual" == "$expected" ]] || fail "${label}: expected=${expected}, actual=${actual}"
}

new_case() {
  local name="$1"
  CASE_DIR="${TEST_ROOT}/${name}"
  STATE_DIR="${CASE_DIR}/state"
  CALLS_FILE="${CASE_DIR}/claude.calls"
  FAKE_CLAUDE="${CASE_DIR}/fake-claude"
  mkdir -p "$STATE_DIR"
  printf '%s\n' '{"session_id":"session-test-123","model":"claude-fable-5"}' > "${STATE_DIR}/a0_session.json"
  printf '%s\n' '# recall fixture' > "${CASE_DIR}/recall.md"

  cp "${REPO_ROOT}/tests/fixtures/fake_claude_for_a0.sh" "$FAKE_CLAUDE"
  chmod +x "$FAKE_CLAUDE"
}

write_alive_heartbeat() {
  printf '{"ts":"%s","pid":999}\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" > "${STATE_DIR}/a0_heartbeat.json"
}

write_stale_heartbeat() {
  printf '%s\n' '{"ts":"1970-01-01T00:00:00+0000","pid":999}' > "${STATE_DIR}/a0_heartbeat.json"
}

run_tick() {
  local fake_mode="$1"
  env \
    A0_STATE_DIR="$STATE_DIR" \
    A0_HEARTBEAT_FILE="${STATE_DIR}/a0_heartbeat.json" \
    A0_SESSION_FILE="${STATE_DIR}/a0_session.json" \
    A0_LOCK_FILE="${STATE_DIR}/a0_resume.lock" \
    A0_STATUS_FILE="${STATE_DIR}/a0_continuity_status.json" \
    A0_LOG_FILE="${STATE_DIR}/a0_continuity.log" \
    A0_PROMPT_FILE="${CASE_DIR}/recall.md" \
    A0_CLAUDE_BIN="$FAKE_CLAUDE" \
    A0_TIMEOUT_SECONDS=3 \
    FAKE_CLAUDE_MODE="$fake_mode" \
    FAKE_CLAUDE_CALLS="$CALLS_FILE" \
    bash "$TICK_SCRIPT"
}

status_mode() {
  jq -r '.mode' "${STATE_DIR}/a0_continuity_status.json"
}

call_count() {
  if [[ -f "$CALLS_FILE" ]]; then
    wc -l < "$CALLS_FILE" | tr -d ' '
  else
    printf '0\n'
  fi
}

# 1. Fresh heartbeat: no model call.
new_case alive
write_alive_heartbeat
run_tick resume_success
assert_eq skipped_alive "$(status_mode)" "alive status"
assert_eq 0 "$(call_count)" "alive model calls"
pass "alive -> skipped_alive"

# 2. Stale heartbeat: resume the pinned session.
new_case stale_resume
write_stale_heartbeat
run_tick resume_success
assert_eq resume "$(status_mode)" "resume status"
assert_eq 1 "$(call_count)" "resume model calls"
grep -q -- '--resume session-test-123' "$CALLS_FILE" || fail "resume args missing session id"
grep -q -- '--model claude-fable-5 -p --output-format text --max-turns 40' "$CALLS_FILE" || fail "resume args missing pinned model/options"
pass "stale -> resume"

# 3. A live lock prevents a second Claude process.
new_case locked
write_stale_heartbeat
printf '%s\n' "$$" > "${STATE_DIR}/a0_resume.lock"
run_tick resume_success
assert_eq locked "$(status_mode)" "locked status"
assert_eq 0 "$(call_count)" "locked model calls"
pass "live pid lock -> locked"

# 4. Quota stderr creates backoff and the next tick does not call Claude again.
new_case quota
write_stale_heartbeat
run_tick quota_blocked
assert_eq quota_blocked "$(status_mode)" "quota status"
assert_eq 1 "$(call_count)" "quota first model calls"
jq -e '.next_retry != null' "${STATE_DIR}/a0_continuity_status.json" >/dev/null || fail "quota next_retry missing"
run_tick resume_success
assert_eq quota_blocked "$(status_mode)" "quota backoff status"
assert_eq 1 "$(call_count)" "quota backoff model calls"
pass "quota_blocked -> next_retry backoff"

# 5. A non-quota resume failure gets one fresh attempt.
new_case resume_fallback
write_stale_heartbeat
run_tick resume_fail_fresh_success
assert_eq fresh "$(status_mode)" "fresh fallback status"
assert_eq 2 "$(call_count)" "fresh fallback model calls"
sed -n '1p' "$CALLS_FILE" | grep -q -- '--resume session-test-123' || fail "first attempt was not resume"
if sed -n '2p' "$CALLS_FILE" | grep -q -- '--resume'; then
  fail "fresh fallback unexpectedly used --resume"
fi
pass "resume failure -> fresh"

printf 'ALL PASS: %d/5 A0 continuity paths\n' "$PASS_COUNT"
