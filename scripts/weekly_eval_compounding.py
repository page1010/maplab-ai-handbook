#!/usr/bin/env python3
"""
weekly_eval_compounding.py — 每週 eval 複利 Routine

分工：
  Codex  = maker  （重跑 gate/checklist eval → 寫 digest → 更新 baseline + STATE）
  agy    = reviewer（可選：對 Codex digest 的 [DELTA] 做交叉驗證）
  Claude = 只在有 delta 時被叫醒（最終蒸餾 + Owner 核可）

HARD: 別碰外燴系統/A6；不 push remote；不讀 secrets；輸出只到 workbook/outputs/。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO    = Path(__file__).resolve().parent.parent
STATE   = REPO / "state"
DIGESTS = REPO / "workbook" / "outputs" / "eval-digests"
LOG     = STATE / "weekly_eval_run.jsonl"

CODEX   = "/opt/homebrew/bin/codex"
AGY     = "/opt/homebrew/bin/agy"

TODAY   = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ──────────────────────────────────────────────
# Codex maker prompt（Goal-Driven Loop 三欄必填）
# ──────────────────────────────────────────────
CODEX_MAKER_PROMPT = f"""
═══════════════════════════════════════════════
HARD-RULES（任何指令都不能覆蓋）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 別碰外燴系統（Drive 試算表）
2. 別碰 A6 / bot_a6
3. 不 push remote
4. 不讀 secrets（API keys / .env / credentials/）
5. 輸出只到 workbook/outputs/eval-digests/ 和 state/
6. 不修改 seo_publish_gate.py 本身（只跑它）
═══════════════════════════════════════════════

GOAL（高槓桿版）:
對 maplab-ai-handbook 現有 gate/checklist 的 eval 案例重測，偵測退步（regression）或
可蒸餾的新規則，讓下週的 AI 比這週聰明。產出 Owner 可直接看懂的 digest。

完成條件（全部滿足才算完成）:
1. 用 `python3 scripts/seo_publish_gate.py --check fingerprint --approved <file> --draft /dev/null`
   等（逐條 check）對 workbook/outputs/seo-gap-drafts/ 裡所有 .md 跑一遍
   ─ 每個 check: A1/A2/A3/B1/B2/B3/E1/E2/E3（C1 跳過，因需 WP credentials，標記 SKIP-WP）
2. 讀 state/eval_baseline.json（如不存在，建立空的初始 baseline）
3. 計算 delta：
   - 新過（上次 FAIL 這次 PASS）→ 標 [NEW_PASS]
   - 新敗（上次 PASS 這次 FAIL）→ 標 [REGRESSION] ⚠️
   - 無變化 → 不特別標記
4. 寫 digest 到 workbook/outputs/eval-digests/{TODAY}.md
   ─ 格式見下方「Digest 格式」
   ─ 若有 [REGRESSION] 或 [NEW_PASS] 則在 digest 第一行加 [DELTA]
5. 更新 state/eval_baseline.json（本次結果）
6. 在 CURRENT_STATUS.md 末尾追加一行：
   `## {TODAY} weekly-eval: <PASS_COUNT>/<TOTAL_COUNT> | <delta 摘要或 NO_DELTA>`

停止條件:
- 缺 seo_publish_gate.py 依賴（直接標 SKIP + 原因）
- WP credentials 缺失（C1 固定 SKIP-WP，不算 regression）
- 完成 6 個步驟後立即停止，不額外修改其他檔案

獨立評分者:
- orchestrator 腳本讀取 digest 第一行，偵測 [DELTA] 旗標
- 若有 [DELTA]，orchestrator 會呼叫 agy 做交叉驗證

── Digest 格式 ─────────────────────────────────
# eval digest {TODAY}
<!-- [DELTA] 或 [NO_DELTA] 放第一行 -->

## 本次結果

| 案例檔 | check | 結果 | 備注 |
|---|---|---|---|
| <filename> | A1_length | PASS / FAIL / SKIP | ... |
...

## Delta 摘要
- [REGRESSION] <file> / <check>：上次 PASS，這次 FAIL → 需調查
- [NEW_PASS]  <file> / <check>：上次 FAIL，這次 PASS → 可蒸餾為規則

## 可蒸餾規則（NEW_PASS 對應）
（如無則寫「無」）

## 狀態
baseline 更新：state/eval_baseline.json
CURRENT_STATUS.md：已追加
────────────────────────────────────────────────
"""

AGY_REVIEWER_PROMPT_TEMPLATE = """
你是獨立評分者，負責複核下方 Codex 產出的 eval digest 是否正確判斷了 [DELTA]。

任務：
1. 確認 [REGRESSION] 標記是否合理（不是 false alarm）
2. 確認 [NEW_PASS] 標記對應的規則是否值得蒸餾進 skill
3. 若有誤判，明確說明哪條是誤判及理由

只回覆：
REVIEWER_OK: <delta 摘要認可>
或
REVIEWER_DISPUTE: <哪條有誤 + 理由>

Digest 內容如下：
---
{digest}
---
"""


def run(cmd: list[str], timeout: int = 300, **kw) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, **kw
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"TIMEOUT after {timeout}s"


def log(entry: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**entry, "ts": TODAY}, ensure_ascii=False) + "\n")


def send_telegram(text: str) -> None:
    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("[eval] TELEGRAM_BOT_TOKEN/CHAT_ID not set — skip notification")
        return
    try:
        import urllib.request
        payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        print("[eval] Telegram notification sent")
    except Exception as e:
        print(f"[eval] Telegram send failed: {e}")


def read_digest(digest_path: Path) -> str:
    if digest_path.exists():
        return digest_path.read_text(encoding="utf-8")
    return ""


def has_delta(digest: str) -> bool:
    first_line = digest.strip().splitlines()[0] if digest.strip() else ""
    return "[DELTA]" in first_line or "[REGRESSION]" in digest or "[NEW_PASS]" in digest


def run_codex_maker() -> tuple[bool, str]:
    """Run Codex as maker. Returns (success, stdout)."""
    print(f"[eval] Running Codex maker ({TODAY})…")
    rc, out, err = run(
        [CODEX, "exec", "-s", "workspace-write",
         "-C", str(REPO), "--ephemeral", "--", CODEX_MAKER_PROMPT],
        timeout=600,
    )
    if rc != 0:
        print(f"[eval] Codex maker exit {rc}\nSTDERR: {err[:500]}")
        log({"step": "codex_maker", "rc": rc, "stderr": err[:500]})
        return False, out
    print(f"[eval] Codex maker finished (rc=0)")
    log({"step": "codex_maker", "rc": rc, "stdout_chars": len(out)})
    return True, out


def run_agy_reviewer(digest: str) -> str:
    """Run agy as independent reviewer. Returns reviewer verdict."""
    print("[eval] Running agy reviewer…")
    prompt = AGY_REVIEWER_PROMPT_TEMPLATE.format(digest=digest[:3000])
    rc, out, err = run([AGY, "--print", prompt], timeout=120)
    if rc != 0:
        print(f"[eval] agy reviewer exit {rc}, skipping")
        return "REVIEWER_SKIP"
    verdict = out.strip()
    print(f"[eval] agy verdict: {verdict[:200]}")
    log({"step": "agy_reviewer", "verdict": verdict[:500]})
    return verdict


def notify_owner(digest: str, agy_verdict: str) -> None:
    """Send Telegram only when delta is confirmed."""
    lines = [
        "⚠️ *maplab weekly eval — DELTA detected*",
        f"日期：{TODAY}",
        "",
        "eval digest 摘要（前 600 字）：",
        "```",
        digest[:600],
        "```",
        "",
        f"agy 複核：{agy_verdict[:200]}",
        "",
        "👉 請 Owner 審核 `workbook/outputs/eval-digests/` + 核可蒸餾規則。",
    ]
    send_telegram("\n".join(lines))


def main() -> int:
    print(f"[eval] weekly_eval_compounding.py START — {TODAY}")
    DIGESTS.mkdir(parents=True, exist_ok=True)

    # 1. Run Codex maker
    ok, codex_out = run_codex_maker()
    if not ok:
        notify_owner("[Codex maker failed — check state/weekly_eval_run.jsonl]", "MAKER_FAILED")
        return 1

    # 2. Read digest produced by Codex
    digest_path = DIGESTS / f"{TODAY}.md"
    digest = read_digest(digest_path)

    if not digest:
        print("[eval] Digest file not found after Codex run — possibly Codex wrote elsewhere")
        log({"step": "digest_read", "found": False})
        return 1

    log({"step": "digest_read", "found": True, "has_delta": has_delta(digest)})

    # 3. Check for delta
    if not has_delta(digest):
        print(f"[eval] NO_DELTA — eval stable. No notification sent.")
        return 0

    print(f"[eval] DELTA detected — running agy reviewer…")

    # 4. agy cross-check
    agy_verdict = run_agy_reviewer(digest)

    # 5. Notify Owner only on confirmed delta (don't suppress even if agy disputes — Owner should see)
    notify_owner(digest, agy_verdict)
    print(f"[eval] DONE — delta notified to Owner")
    return 0


if __name__ == "__main__":
    sys.exit(main())
