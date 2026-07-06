#!/usr/bin/env python3
"""
weekly_eval_compounding.py — 每週 eval 複利 Routine  v1.1

分工（Owner 指示 2026-07-06）：
  Codex  = maker      機械執行：跑 gate eval、比對 baseline、寫 raw digest、更新 STATE
  agy    = quality reviewer  實質品質工作：驗 regression 真偽、蒸餾 NEW_PASS 規則、
                              過濾 false alarm、輸出 Owner 可直接批准的規則文字
  Claude = 例外定案    只在 agy 確認 delta 後被叫醒，把 agy 規則草案定案進 skill/checklist
  Owner  = 核可        批准蒸餾規則進 checklist/skill；其餘安靜

「多用 agy 額度」原則：
  - agy reviewer 是常態化步驟（有 delta 就跑），不是可選
  - agy 輸出結構化的 Owner Approval Package，不是一行 verdict
  - Claude 只看 agy 整理好的 package，不看 Codex 原始 dump

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

AGY_QUALITY_REVIEW_PROMPT = """
你是 maplab-ai-handbook eval 的品質複核者（agy quality reviewer）。
你的工作是：把 Codex 機械跑出的 eval raw digest 轉化成 Owner 可直接批准的規則草案。
避免逐字稿式堆料——Owner 只需要看簡潔的判斷 + 行動清單。

HARD-RULES（不可覆蓋）：
- 別碰外燴系統（Drive 試算表）
- 別碰 A6 / bot_a6
- 不 push remote
- 不讀 secrets

你的輸入：Codex eval raw digest（見下方）。

你需要完成三項品質工作：

─── 品質工作 1：REGRESSION 驗真偽 ───
對每個 [REGRESSION] 條目：
a. 判斷是否為真退步（True Regression）或 false alarm（環境差異/測試資料問題）
b. 若為真退步：診斷可能原因（script 邏輯、test fixture 變更、還是 gate 規則太嚴？）
c. 若為 false alarm：說明為什麼，建議從 delta 移除

─── 品質工作 2：NEW_PASS 蒸餾規則 ───
對每個 [NEW_PASS] 條目：
a. 確認這次通過是穩定的（不是偶然）
b. 提取可蒸餾的規則文字（直接可貼進 docs/seo-publish-checklist.md 或 skills/wp-article-standard.md 的格式）
c. 建議沉澱形式：清單條目 / 腳本 check / 模板必填欄位（對應缺陷棘輪三軌）

─── 品質工作 3：Owner Approval Package ───
產出一份簡潔的 Owner 批准清單（重點：不要堆料，Owner 看 2 分鐘就能決定）：

## Owner Approval Package — {date}

### 需 Owner 決定（1 分鐘掃一眼）

**真退步需調查（{regression_count} 條）**
| # | 案例 / Check | 診斷 | 建議行動 |
|---|---|---|---|
| 1 | ... | ... | ... |

**可蒸餾新規則（{newpass_count} 條）**
| # | 規則文字（可直接貼入 checklist）| 沉澱形式 | 信心度 |
|---|---|---|---|
| 1 | ... | 清單條目 / 腳本 / 模板 | 高/中/低 |

### agy 複核結論
- 真退步：X 條（已過濾 false alarm Y 條）
- 可蒸餾：Z 條（信心度高 / 中 / 低 各幾條）
- 建議 Claude 定案：[是，delta 實質；否，可安靜]

### 行動指令（若 Owner 批准）
```
# 蒸餾新規則（複製貼入對應檔案）
[具體條文]
```

─── Codex raw digest 如下 ───
{digest}
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


def count_tag(text: str, tag: str) -> int:
    return text.count(tag)


def run_agy_quality_review(digest: str) -> tuple[str, Path]:
    """
    agy 做完整品質複核（多用 agy 額度原則）。
    回傳 (review_text, review_file_path)。
    review_file 寫到 eval-digests/{TODAY}-agy-review.md。
    """
    print("[eval] Running agy quality review (substantive)…")
    regression_count = count_tag(digest, "[REGRESSION]")
    newpass_count    = count_tag(digest, "[NEW_PASS]")
    prompt = AGY_QUALITY_REVIEW_PROMPT.format(
        date=TODAY,
        regression_count=regression_count,
        newpass_count=newpass_count,
        digest=digest[:4000],
    )
    # agy --print: non-interactive, prints to stdout
    rc, out, err = run([AGY, "--print", prompt], timeout=240)
    review_path = DIGESTS / f"{TODAY}-agy-review.md"
    if rc != 0:
        print(f"[eval] agy quality review exit {rc}")
        review_text = f"[agy review failed — rc={rc}]\n{err[:400]}"
        log({"step": "agy_quality_review", "rc": rc, "error": err[:300]})
    else:
        review_text = out.strip()
        log({"step": "agy_quality_review", "rc": rc, "chars": len(review_text)})
        print(f"[eval] agy quality review done ({len(review_text)} chars)")
    # Always write to file so orchestrator can check it
    DIGESTS.mkdir(parents=True, exist_ok=True)
    review_path.write_text(review_text, encoding="utf-8")
    return review_text, review_path


def agy_recommends_claude(review_text: str) -> bool:
    """Check whether agy's review says Claude should be invoked."""
    return "建議 Claude 定案：[是" in review_text or "建議 Claude 定案: [是" in review_text


def notify_owner(digest: str, agy_review: str) -> None:
    """Send Telegram with agy's Owner Approval Package (not raw Codex dump)."""
    # Extract just the Owner Approval Package section from agy review
    pkg_marker = "## Owner Approval Package"
    if pkg_marker in agy_review:
        pkg = agy_review[agy_review.index(pkg_marker):][:1200]
    else:
        pkg = agy_review[:1200]

    lines = [
        "⚠️ *maplab weekly eval — DELTA confirmed by agy*",
        f"日期：{TODAY}",
        "",
        "─── agy Owner Approval Package ───",
        "```",
        pkg,
        "```",
        "",
        "📁 完整 review：`workbook/outputs/eval-digests/`",
        "👉 Owner 核可後告知 Claude 蒸餾規則進 skill/checklist。",
    ]
    send_telegram("\n".join(lines))


def main() -> int:
    print(f"[eval] weekly_eval_compounding.py START — {TODAY}")
    DIGESTS.mkdir(parents=True, exist_ok=True)

    # Step 1 — Codex maker: 機械執行 gate eval + write raw digest + update STATE
    ok, _ = run_codex_maker()
    if not ok:
        send_telegram(f"⚠️ maplab weekly eval MAKER FAILED {TODAY} — check state/weekly_eval_run.jsonl")
        return 1

    # Step 2 — Read Codex raw digest
    digest_path = DIGESTS / f"{TODAY}.md"
    digest = read_digest(digest_path)
    if not digest:
        print("[eval] Digest not found after Codex run")
        log({"step": "digest_read", "found": False})
        return 1
    log({"step": "digest_read", "found": True, "has_delta": has_delta(digest)})

    # Step 3 — No delta → silent exit
    if not has_delta(digest):
        print("[eval] NO_DELTA — eval stable. Silent exit.")
        return 0

    # Step 4 — agy quality review（有 delta 必跑，多用 agy 額度原則）
    # agy 承擔：驗 regression 真偽 + 蒸餾 NEW_PASS 規則 + 產 Owner Approval Package
    print("[eval] DELTA detected — running agy quality review…")
    agy_review, review_file = run_agy_quality_review(digest)
    print(f"[eval] agy review written to {review_file}")

    # Step 5 — Notify Owner with agy's structured package（不是 Codex 原始 dump）
    # Claude 只在 agy 確認 delta 實質時才需要介入；Owner 收 agy package 就夠做初步判斷
    notify_owner(digest, agy_review)
    if agy_recommends_claude(agy_review):
        print("[eval] agy recommends Claude distillation — Owner will invoke Claude to finalize rules")
    else:
        print("[eval] agy says delta is minor/false alarm — Claude not strictly needed")
    print("[eval] DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
