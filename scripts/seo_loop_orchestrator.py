#!/usr/bin/env python3
"""
seo_loop_orchestrator.py — SEO 自走 loop 主控（步驟 1–4）。
步驟 1: 挑 GAP
步驟 2: Codex 起草 + agy 審查
步驟 3: 確定性 QA（不燒 Claude）
步驟 4: HTML render + 寫 escalation → 停住（等 A0 視覺閘門）
HARD: 不碰 A6/bot_a6、不 push、不發布。
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO    = Path(__file__).parent.parent
SCRIPTS = Path(__file__).parent
PYTHON  = "/usr/bin/python3"
STATE   = REPO / "state" / "seo_loop_state.json"
LOG     = REPO / "state" / "seo_loop_run.jsonl"


def run(cmd: list[str], **kw) -> tuple[int, str, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r.returncode, r.stdout, r.stderr


def log_append(entry: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def update_state(gap_id: str, key: str) -> None:
    state: dict = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text())
        except Exception:
            pass
    lst = state.setdefault(key, [])
    if gap_id not in lst:
        lst.append(gap_id)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def main() -> None:
    ts_start = datetime.now(timezone.utc).isoformat()
    run_log: dict = {"started_at": ts_start, "steps": []}

    # ── Step 1: pick next GAP ─────────────────────────────────────────────────
    print("[SEO Loop] Step 1: 挑 GAP…", flush=True)
    rc, out, err = run([PYTHON, str(SCRIPTS / "seo_gap_picker.py")], cwd=str(REPO))
    if rc != 0:
        run_log["error"] = f"gap_picker failed: {err[:200]}"
        log_append(run_log)
        print(f"[SEO Loop] ERROR: gap_picker exit {rc}")
        sys.exit(rc)

    picker_result = json.loads(out)
    if picker_result.get("status") == "all_gaps_drafted":
        run_log["status"] = "all_gaps_drafted"
        log_append(run_log)
        print("[SEO Loop] 所有 GAP 已草稿。退出。")
        sys.exit(0)

    gap = picker_result["gap"]
    gap_id = gap["gap_id"]
    print(f"[SEO Loop] 選定: {gap_id} — {gap['title']}", flush=True)
    run_log["gap_id"] = gap_id
    run_log["gap"] = gap
    run_log["steps"].append({"step": "pick_gap", "status": "OK", "gap_id": gap_id})

    # ── Step 2: Codex draft + agy review ─────────────────────────────────────
    print(f"[SEO Loop] Step 2: Codex 起草 + agy 審查 ({gap_id})…", flush=True)
    rc, out, err = run(
        [PYTHON, str(SCRIPTS / "seo_draft_runner.py"), "--gap-json", json.dumps(gap)],
        cwd=str(REPO), timeout=900,
    )
    try:
        draft_result = json.loads(out.strip().split("\n")[-1])
    except Exception:
        draft_result = {"steps": [], "draft_path": "", "review_path": ""}

    draft_path  = draft_result.get("draft_path", "")
    review_path = draft_result.get("review_path", "")

    if not draft_path or not Path(draft_path).exists():
        run_log["steps"].append({"step": "draft_runner", "status": "FAILED", "detail": "draft_path missing"})
        log_append(run_log)
        print("[SEO Loop] ERROR: 草稿未建立，退出")
        sys.exit(1)

    run_log["steps"].append({"step": "draft_runner", "status": "OK", "draft_path": draft_path, "review_path": review_path})
    print(f"[SEO Loop] 草稿: {draft_path}", flush=True)

    # ── Step 3: 確定性 QA ─────────────────────────────────────────────────────
    print(f"[SEO Loop] Step 3: QA scan ({gap_id})…", flush=True)
    qa_cmd = [
        PYTHON, str(SCRIPTS / "seo_qa_checker.py"),
        draft_path,
        "--gap-type", gap.get("article_type", "case_study"),
        "--kw", gap.get("main_kw", ""),
    ]
    rc_qa, qa_out, qa_err = run(qa_cmd, cwd=str(REPO))
    qa_result = json.loads(qa_out) if qa_out.strip() else {"pass": False, "failures": ["QA output empty"]}

    if not qa_result.get("pass"):
        run_log["steps"].append({"step": "qa", "status": "FAILED", "qa": qa_result})
        update_state(gap_id, "qa_failed")
        # Mark in state so next run re-drafts
        state: dict = json.loads(STATE.read_text()) if STATE.exists() else {}
        if gap_id in state.get("drafted", []):
            state["drafted"].remove(gap_id)
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))

        log_append(run_log)
        print(f"[SEO Loop] QA FAILED — failures: {qa_result.get('failures', [])}")
        print(json.dumps(qa_result, ensure_ascii=False, indent=2))
        sys.exit(2)

    run_log["steps"].append({"step": "qa", "status": "PASS", "score": qa_result.get("score"), "warnings": qa_result.get("warnings", [])})
    print(f"[SEO Loop] QA PASS (score={qa_result.get('score')})", flush=True)

    # ── Step 4: HTML render + escalation (VISUAL GATE — 停住) ─────────────────
    print(f"[SEO Loop] Step 4: render preview + 寫 escalation ({gap_id})…", flush=True)
    preview_cmd = [
        PYTHON, str(SCRIPTS / "seo_preview_render.py"),
        draft_path, gap_id, review_path, json.dumps(qa_result),
    ]
    rc_pr, pr_out, pr_err = run(preview_cmd, cwd=str(REPO))
    try:
        preview_result = json.loads(pr_out)
    except Exception:
        preview_result = {}

    run_log["steps"].append({
        "step": "preview_render",
        "status": "OK" if rc_pr == 0 else "WARN",
        "preview_html": preview_result.get("preview_html"),
        "escalation_id": preview_result.get("escalation_id"),
    })

    update_state(gap_id, "drafted")

    # ── 完成（停在 step 4，等 visual 閘門）────────────────────────────────────
    run_log["status"] = "awaiting_visual_review"
    run_log["completed_at"] = datetime.now(timezone.utc).isoformat()
    run_log["preview_html"] = preview_result.get("preview_html", "")
    run_log["escalation_id"] = preview_result.get("escalation_id", "")
    log_append(run_log)

    print(f"""
[SEO Loop] ✅ STEP 4 完成，已停住（等 A0 視覺閘門）

  GAP ID      : {gap_id}
  草稿路徑    : {draft_path}
  審查報告    : {review_path}
  預覽 HTML   : {preview_result.get('preview_html', 'N/A')}
  Escalation  : {preview_result.get('escalation_path', 'N/A')}
  Escalation ID: {preview_result.get('escalation_id', 'N/A')}

→ 視覺驗證後更新 escalation status=approved 即可進入 Step 5（發布）。
""")


if __name__ == "__main__":
    main()
