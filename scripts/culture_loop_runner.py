#!/usr/bin/env python3
"""
MAPLAB Culture Compounding Loop Runner
地端模型驅動的學習迴圈：感測 → 獨立評分 → 蒸餾規則 → 複利寫回 → 閉環路由

設計原則：
- 製作者不評自己：獨立 qwen2.5 呼叫，只看證據
- 複利寫回：規則直接 append 到 pitfalls.md，不只寫 log
- 地端驅動：不需 Claude；escalate=true 才推給 Claude/Owner
- 接上現有 reaction_ledger.jsonl，不取代

用法：
  python3 scripts/culture_loop_runner.py --mode dry-run
  python3 scripts/culture_loop_runner.py --mode full
  python3 scripts/culture_loop_runner.py --mode sense
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "workbook" / "learning_loop" / "reaction_ledger.jsonl"
STATE_FILE = REPO / "workbook" / "learning_loop" / "culture_loop_state.md"
ESCALATION = REPO / "workbook" / "learning_loop" / "escalation_queue.jsonl"
PITFALLS = REPO / "pitfalls.md"
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
VERIFIER_MODEL = os.getenv("CULTURE_LOOP_MODEL", "qwen2.5:14b")
MAX_EVIDENCE_CHARS = 3000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ─── §1 感測：收集硬證據 ─────────────────────────────────────────────────────


def get_recent_commits(n: int = 10) -> list[str]:
    """讀 git log，只要 hash + message，不要 agent 自述。"""
    try:
        out = subprocess.check_output(
            ["git", "log", "--oneline", f"-{n}"],
            cwd=REPO, text=True, stderr=subprocess.DEVNULL
        )
        return out.strip().splitlines()
    except Exception:
        return ["[git log failed]"]


def read_open_reactions() -> list[dict]:
    """讀 reaction_ledger.jsonl，只取 status=open。"""
    if not LEDGER.exists():
        return []
    reactions = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            if r.get("status") == "open":
                reactions.append(r)
        except json.JSONDecodeError:
            pass
    return reactions


def read_evidence_file(path_str: str) -> str:
    """讀 evidence_path 指向的檔案，截斷到 MAX_EVIDENCE_CHARS。"""
    p = REPO / path_str
    if not p.exists():
        return f"[MISSING: {path_str}]"
    text = p.read_text(encoding="utf-8", errors="replace")
    if len(text) > MAX_EVIDENCE_CHARS:
        text = text[:MAX_EVIDENCE_CHARS] + "\n...[truncated]"
    return text


def build_evidence_bundle(reactions: list[dict], commits: list[str]) -> dict:
    """把感測到的所有硬證據打包成一個 dict，供地端模型消化。"""
    bundle: dict = {
        "generated_at": utc_now(),
        "recent_commits": commits,
        "open_reactions": [],
    }
    for r in reactions:
        entry = {
            "reaction_id": r.get("reaction_id"),
            "severity": r.get("severity"),
            "decision": r.get("decision"),
            "why": r.get("why"),
            "due_at": r.get("due_at"),
            "assigned_to": r.get("assigned_to"),
            "evidence_file_content": read_evidence_file(r.get("evidence_path", "")),
            # 禁止攜帶 agent 自述欄位
            "_note": "agent 自述欄位已排除；只看 evidence_file_content + commits",
        }
        bundle["open_reactions"].append(entry)
    return bundle


# ─── §2 獨立驗證者評分（地端模型） ────────────────────────────────────────────


VERIFIER_SYSTEM = (
    "你是 MAPLAB Culture Compounding Loop 獨立稽核員。"
    "你沒有參與任何本輪的 MAPLAB 工作任務。"
    "只看「證據清單」裡的硬證據（commit hash / receipt file / DB preview / readback）。"
    "禁止把 agent 自述（「我做了」「已完成」「應該 OK」）當作證據。"
    "只輸出合法 JSON 陣列，不輸出任何其他文字。"
)

VERIFIER_PROMPT_TEMPLATE = """
【評分基準】
- evidence_quality (0-5)：有 commit hash / receipt file / DB preview / readback = 高分；只有 agent 說「做了」= 0。
- pltr_readiness (true/false)：今晚客戶現場要用，資料流/介面/操作節點/文件是否全部可驗證？
- rule_compliance (0-5)：符合 company-values.md 核心原則（增量保存/回報/不做白工/記錄/測試 receipt/Claude 成本優化）？
- distilled_rule (string|empty)：能否抽出一條「遇到 X 情境，應該 Y，不做 Z」的通則？若不能，留空。
- escalate (true/false)：evidence_quality<=1 OR (pltr_readiness=false AND severity=high) OR rule_compliance<=1

【輸出格式】（只輸出 JSON，無其他文字）
[{
  "reaction_id": "...",
  "evidence_quality": N,
  "pltr_readiness": true/false,
  "rule_compliance": N,
  "pltr_fail_reasons": ["..."],
  "violated_principles": ["..."],
  "verified_facts": ["..."],
  "distilled_rule": "...或空字串",
  "escalate": true/false,
  "escalate_reason": "...或空字串"
}]

【證據清單】
{EVIDENCE_JSON}
"""


def call_verifier(evidence_bundle: dict, dry_run: bool = False) -> list[dict] | None:
    """呼叫 qwen2.5 做獨立評分。dry_run 模式用 mock 資料。"""
    if dry_run:
        # dry-run：用 mock 輸出，驗證 pipeline 本身
        return _mock_verifier_output(evidence_bundle)

    prompt = VERIFIER_PROMPT_TEMPLATE.replace(
        "{EVIDENCE_JSON}",
        json.dumps(evidence_bundle, ensure_ascii=False, indent=2)[:6000],
    )
    payload = json.dumps({
        "model": VERIFIER_MODEL,
        "prompt": prompt,
        "system": VERIFIER_SYSTEM,
        "stream": False,
        "options": {"num_ctx": 32768, "temperature": 0},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = (data.get("response") or "").strip()
            # 提取 JSON 陣列
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
            print(f"[verifier] JSON parse failed. Raw:\n{raw[:500]}", file=sys.stderr)
            return None
    except Exception as exc:
        print(f"[verifier] Ollama error: {exc}", file=sys.stderr)
        return None


def _mock_verifier_output(bundle: dict) -> list[dict]:
    """dry-run 時的 mock，展示 pipeline 走通。"""
    results = []
    for r in bundle.get("open_reactions", []):
        rid = r["reaction_id"]
        # 模擬：所有 stale reaction 都有 evidence 問題
        results.append({
            "reaction_id": rid,
            "evidence_quality": 1,
            "pltr_readiness": False,
            "rule_compliance": 3,
            "pltr_fail_reasons": [
                "evidence_path 指向的 latest.json 是 patrol 輸出，不是 receipt",
                "沒有 commit hash 指向實際修復",
                "沒有 owner-facing surface 截圖或 readback",
            ],
            "violated_principles": [
                "company-values §7: 測試與 receipt 是交付的一部分",
                "company-values §1: 定時回報並存檔（reaction 已逾期 9 天）",
            ],
            "verified_facts": [
                f"reaction_id={rid} 在 ledger 中已超期 9+ 天",
                "evidence_path 指向 hermes/patrol/latest.json，不是 task 完成證明",
                "reaction 的 next_action 未轉成實際 task card 或 commit",
            ],
            "distilled_rule": (
                "patrol 偵測到的問題若 9 天後仍 open，"
                "必須關閉為 false_alarm 或轉成有接續點的 task card；"
                "不得只在 reaction_ledger 裡寫「待處理」"
            ) if rid == "long-blocked-three-layer-review" else "",
            "escalate": rid in ("google-oauth-reauth-card", "long-blocked-three-layer-review"),
            "escalate_reason": (
                "Owner 5min action 尚未執行（OAuth reauth）" if rid == "google-oauth-reauth-card"
                else "blocked task cards 超過 14 天，需 Claude 或 Owner 介入拆解" if rid == "long-blocked-three-layer-review"
                else ""
            ),
        })
    return results


# ─── §3+④ 五階段記憶 + 複利寫回 ──────────────────────────────────────────────


def update_state_file(
    bundle: dict,
    scores: list[dict],
    mode: str,
) -> None:
    """寫 STATE 檔（五段結構）。"""
    now = utc_now()
    commits_str = "\n".join(f"  - {c}" for c in bundle.get("recent_commits", []))
    open_failures = []
    verified_facts_all = []
    general_rules = []
    lessons = []

    for s in scores:
        rid = s["reaction_id"]
        facts = s.get("verified_facts", [])
        rule = s.get("distilled_rule", "")
        verified_facts_all.extend([f"`{rid}`: {f}" for f in facts])
        if rule:
            general_rules.append(f"- {rule}  _(source: {rid})_")
        if s.get("escalate"):
            open_failures.append(
                f"- **{rid}** [ESCALATE] evidence_quality={s['evidence_quality']} "
                f"pltr={s['pltr_readiness']} reason={s.get('escalate_reason','')}"
            )
        else:
            open_failures.append(
                f"- {rid} evidence={s['evidence_quality']}/5 pltr={s['pltr_readiness']}"
            )
        if rule and s.get("evidence_quality", 0) >= 2:
            lessons.append(
                f"- [{now[:10]}] {rule[:80]}... (已寫回 pitfalls)"
                if s.get("evidence_quality", 0) >= 3
                else f"- [{now[:10]}] {rule[:80]}... (待驗收後寫回)"
            )

    content = f"""# Culture Compounding Loop — STATE

> 這是地端模型每日更新的狀態檔。不要手動修改；由 `scripts/culture_loop_runner.py` 維護。
> 真相源：`workbook/learning_loop/reaction_ledger.jsonl`

---

## Verified facts
_有 evidence 指向的確認事實（非 agent 自述）_

{chr(10).join(f'- {f}' for f in verified_facts_all) or '- (本輪無新驗證事實)'}

---

## General rules（蒸餾通則）
_可被 cold-start 讀到的通則；同步 append 到 pitfalls.md_

{chr(10).join(general_rules) or '- (本輪無新蒸餾規則)'}

---

## Open failures
_未通過 pltr_readiness 或 evidence_quality 的 reactions_

{chr(10).join(open_failures) or '- (無 open failure)'}

---

## Lessons learned
_已 Distill 並寫回的規則_

{chr(10).join(lessons) or '- (本輪無新寫回)'}

---

## Last session
- **執行時間**: {now}
- **模式**: {mode}
- **使用模型**: {VERIFIER_MODEL}（{"dry-run mock" if mode == "dry-run" else "real Ollama call"}）
- **處理 reactions**: {len(scores)} 筆
- **escalate**: {sum(1 for s in scores if s.get('escalate'))} 筆
- **最近 10 commits**:
{commits_str}
"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(content, encoding="utf-8")
    print(f"[state] 寫入 {STATE_FILE.relative_to(REPO)}")


def append_to_pitfalls(scores: list[dict], dry_run: bool = False) -> list[str]:
    """
    把 evidence_quality >= 3 且有 distilled_rule 的條目 append 到 pitfalls.md。
    先 grep 確認唯一性，不重複 append。
    """
    appended = []
    for s in scores:
        rule = s.get("distilled_rule", "").strip()
        if not rule or s.get("evidence_quality", 0) < 3:
            continue
        rid = s["reaction_id"]
        # 唯一性檢查
        if PITFALLS.exists():
            existing = PITFALLS.read_text(encoding="utf-8")
            if rid in existing:
                print(f"[pitfalls] skipped (already exists): {rid}")
                continue
        entry = f"""
## {utc_now()[:10]} — [Culture Loop] {rid}

- 觸發條件：reaction_ledger open reaction `{rid}` 經獨立稽核員評分，evidence_quality={s['evidence_quality']}/5，pltr_readiness={s['pltr_readiness']}。
- 根因：{'; '.join(s.get('pltr_fail_reasons', ['未詳']) or ['未詳'])}
- 解法：{rule}
- 預防：任何 reaction 在 culture_loop_runner 評分 evidence_quality <= 2 時，自動進 escalation_queue，不得自行關閉。
- 違反原則：{'; '.join(s.get('violated_principles', []) or [])}
"""
        if dry_run:
            print(f"[pitfalls] DRY-RUN — 預計 append:\n{entry}")
        else:
            with open(PITFALLS, "a", encoding="utf-8") as f:
                f.write(entry)
            print(f"[pitfalls] appended: {rid}")
        appended.append(rid)
    return appended


def write_escalations(scores: list[dict], dry_run: bool = False) -> list[str]:
    """把 escalate=true 的條目寫到 escalation_queue.jsonl。"""
    written = []
    for s in scores:
        if not s.get("escalate"):
            continue
        entry = {
            "reaction_id": s["reaction_id"],
            "escalated_at": utc_now(),
            "escalate_reason": s.get("escalate_reason", ""),
            "evidence_quality": s.get("evidence_quality"),
            "pltr_readiness": s.get("pltr_readiness"),
            "verified_facts": s.get("verified_facts", []),
            "violated_principles": s.get("violated_principles", []),
            "suggested_next": (
                f"請 Claude/Owner 處理：{s.get('escalate_reason','')}"
                f"；distilled_rule={s.get('distilled_rule','')}"
            ),
            "status": "pending",
        }
        line = json.dumps(entry, ensure_ascii=False)
        if dry_run:
            print(f"[escalation] DRY-RUN — 預計寫入:\n{line}")
        else:
            ESCALATION.parent.mkdir(parents=True, exist_ok=True)
            with open(ESCALATION, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            print(f"[escalation] queued: {entry['reaction_id']}")
        written.append(entry["reaction_id"])
    return written


# ─── 主流程 ───────────────────────────────────────────────────────────────────


def run(mode: str) -> None:
    dry_run = mode == "dry-run"
    print(f"[runner] mode={mode} model={VERIFIER_MODEL} time={utc_now()}")

    # §1 感測
    commits = get_recent_commits()
    reactions = read_open_reactions()
    print(f"[sense] {len(commits)} commits, {len(reactions)} open reactions")

    if not reactions:
        print("[runner] 沒有 open reaction，跳過評分。")
        return

    bundle = build_evidence_bundle(reactions, commits)

    # §2 獨立驗證者評分
    print(f"[verifier] calling {VERIFIER_MODEL} ({'mock' if dry_run else 'real'})...")
    scores = call_verifier(bundle, dry_run=dry_run)
    if not scores:
        print("[runner] ERROR: verifier returned None. 終止。", file=sys.stderr)
        sys.exit(1)
    print(f"[verifier] scored {len(scores)} reactions")

    # §3 + STATE 更新
    update_state_file(bundle, scores, mode)

    # §4 複利寫回（pitfalls）
    appended = append_to_pitfalls(scores, dry_run=dry_run)
    print(f"[pitfalls] {len(appended)} rules written")

    # §5 閉環路由（escalation）
    escalated = write_escalations(scores, dry_run=dry_run)
    print(f"[escalation] {len(escalated)} reactions queued")

    # 摘要
    print("\n=== CULTURE LOOP SUMMARY ===")
    for s in scores:
        status = "ESCALATE" if s.get("escalate") else "OK"
        print(
            f"  {s['reaction_id']}: "
            f"evidence={s['evidence_quality']}/5 "
            f"pltr={'Y' if s['pltr_readiness'] else 'N'} "
            f"rule={s['rule_compliance']}/5 "
            f"[{status}]"
        )
    print(f"\nSTATE: {STATE_FILE.relative_to(REPO)}")
    print(f"ESCALATION: {ESCALATION.relative_to(REPO)}")
    print(f"PITFALLS appended: {appended}")


def main() -> int:
    parser = argparse.ArgumentParser(description="MAPLAB Culture Compounding Loop Runner")
    parser.add_argument(
        "--mode",
        choices=["dry-run", "full", "sense"],
        default="dry-run",
        help="dry-run=mock 驗證; full=真實 Ollama 呼叫; sense=只感測不評分",
    )
    args = parser.parse_args()

    if args.mode == "sense":
        commits = get_recent_commits()
        reactions = read_open_reactions()
        bundle = build_evidence_bundle(reactions, commits)
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
        return 0

    run(args.mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
