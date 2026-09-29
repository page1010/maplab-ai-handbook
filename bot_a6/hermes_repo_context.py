#!/usr/bin/env python3
"""Repo context + task inbox for the A6 Hermes Telegram gateway.

2026-09-29 Owner 指令：「把 hermes a6 接好，讓他可以和我直接對話、直接交辦事項、直接讀取 github」。

背景（HERMES_CAPABILITY_BOUNDARY.md §3／誠實項 #4、HERMES_READ_MAP.md §0）：
隨問隨答那條通道之前送出去的 repo 資料是 0 bytes，所以模型只能編。
排程通道 `scripts/free_quota_daily.sh::load_ctx()` 已證明「餵了就答對」；本模組把同一套
做法接到 Telegram 對話：

1. 開機包：每一則對話固定附 `AGENT_CORE.md`（這間公司在做什麼）。
2. 讀檔：訊息裡出現的 repo 相對路徑（可加 `#headN` / `#tailN` / `#La-b` 切片）自動附上原文。
   「讀 GitHub」= 讀本機 clone（`com.maplab.git-pull` 同步），讀不需要任何 token。
3. 交辦：`/task …`、`交辦：…` 會落成 `handoff/inbox/TG-*.md` 任務卡並排進 QUEUE.md，
   下一個 Claude／Codex session 開工必讀；gateway 本身不執行、不 push。

安全邊界不變：只讀 repo 內的文字檔；secrets／.env／cookies／token／.git 一律不讀；
沒有網路寫入；任務卡只是本機檔案。
"""
from __future__ import annotations

import hashlib
import os
import re
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOT_FILES = ("AGENT_CORE.md",)
CTX_BUDGET = int(os.environ.get("HERMES_CTX_BUDGET", "60000"))  # bytes per message
TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".json", ".yaml", ".yml", ".csv", ".toml", ".plist"}
DENY_PARTS = {".git", "secrets", "trash", "backups", "cookies.txt", "__pycache__"}
DENY_NAME_RE = re.compile(r"(\.env|token|cookie|secret|credential|password|\.pem|\.key$)", re.IGNORECASE)
PATH_RE = re.compile(
    r"(?<![\w/@])((?:[\w.\-]+/)*[\w.\-]+\.(?:md|txt|py|sh|json|ya?ml|csv|toml|plist))"
    r"(#(?:head\d+|tail\d+|L\d+-\d+))?"
)
TASK_PREFIXES = ("/task", "交辦：", "交辦:", "任務：", "任務:")
# 附檔內容的 DLP 不看「字樣」（治理文件到處寫 token／金鑰這些詞），看「長得像真憑證的值」。
# 字樣層 DLP 仍只掃 Owner 原話（gateway.provider_egress_rejection）。
SECRET_VALUE_RE = re.compile(
    r"(sk-or-v1-[0-9a-f]{20,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"xox[abp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|"
    r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b|"  # Telegram bot token
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"(?i)(api[_-]?key|secret|token|password|passwd)\s*[=:]\s*['\"]?[A-Za-z0-9_\-./+]{16,})"
)


def find_secret_values(text: str) -> list[str]:
    """Return redacted hints of secret-looking values in text (empty = clean)."""
    hits = []
    for m in SECRET_VALUE_RE.finditer(text or ""):
        frag = m.group(0)
        hits.append(frag[:8] + "…")
    return hits
INBOX_DIR = REPO_ROOT / "handoff" / "inbox"
QUEUE_FILE = INBOX_DIR / "QUEUE.md"


def _safe_rel(rel: str) -> Path | None:
    """Resolve a repo-relative path; None if it escapes the repo or hits the deny list."""
    try:
        path = (REPO_ROOT / rel).resolve()
        path.relative_to(REPO_ROOT)
    except (OSError, ValueError):
        return None
    parts = set(path.relative_to(REPO_ROOT).parts)
    if parts & DENY_PARTS or DENY_NAME_RE.search(path.name):
        return None
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    if not path.is_file():
        return None
    return path


def read_slice(spec: str) -> tuple[str | None, str, str | None]:
    """'CURRENT_STATUS.md#tail150' -> (text, label, error)."""
    rel, _, slc = spec.partition("#")
    path = _safe_rel(rel)
    if path is None:
        return None, spec, "不存在、非文字檔或不在可讀範圍"
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return None, spec, type(exc).__name__
    m = re.match(r"(head|tail)(\d+)$", slc)
    mr = re.match(r"L(\d+)-(\d+)$", slc)
    if m:
        n = int(m.group(2))
        lines = text.splitlines()
        lines = lines[:n] if m.group(1) == "head" else lines[-n:]
        text = "\n".join(lines)
    elif mr:
        a, b = int(mr.group(1)), int(mr.group(2))
        text = "\n".join(text.splitlines()[a - 1 : b])
        if not text.strip():
            return None, spec, "行號範圍超出檔尾"
    return text, spec, None


def extract_path_specs(text: str) -> list[str]:
    seen: list[str] = []
    for m in PATH_RE.finditer(text or ""):
        spec = m.group(1) + (m.group(2) or "")
        if spec not in seen:
            seen.append(spec)
    return seen


def build_context(user_text: str, budget: int = CTX_BUDGET) -> tuple[str, list[str], list[str]]:
    """Return (context_text, attached_labels, missing_labels).

    Boot files come first so the company facts are never squeezed out by a big file.
    """
    got: list[str] = []
    missing: list[str] = []
    parts: list[str] = []
    used = 0
    specs = [f for f in BOOT_FILES] + [s for s in extract_path_specs(user_text) if s.split("#")[0] not in BOOT_FILES]
    for spec in specs:
        text, label, err = read_slice(spec)
        if text is None:
            missing.append(f"{label}({err})")
            continue
        if find_secret_values(text):
            missing.append(f"{label}(內容含疑似真憑證值，拒送 provider)")
            continue
        room = budget - used
        if room <= 0:
            missing.append(f"{label}(超出 context 預算未讀)")
            continue
        if len(text) > room:
            text = text[:room] + "\n…(本檔被 context 預算截斷，未讀完；可用 #headN/#tailN/#La-b 切片)"
        used += len(text)
        got.append(f"{label}[{len(text)}B]")
        parts.append(f"----- 檔案:{label} -----\n{text}")
    return "\n\n".join(parts), got, missing


def context_footer(got: list[str], missing: list[str]) -> str:
    line = "📎 已附原文：" + (", ".join(got) if got else "無")
    if missing:
        line += "｜讀不到：" + ", ".join(missing)
    return line


def compose_prompt(user_text: str) -> tuple[str, list[str], list[str]]:
    ctx, got, missing = build_context(user_text)
    prompt = (
        user_text
        + "\n\n【以下是內部文件原文，回答只能根據這些文件與對話；文件沒寫的一律回「文件未提及」，不得補數字、價格或猜測。】\n\n"
        + ctx
    )
    return prompt, got, missing


# ---------------------------------------------------------------- task inbox

def split_task(text: str) -> str | None:
    for prefix in TASK_PREFIXES:
        if text.startswith(prefix):
            body = text[len(prefix) :].strip()
            return body or None
    return None


def write_task_card(body: str, *, chat_type: str | None, sender_id: int | None) -> Path:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:6]
    task_id = f"TG-{stamp}-{digest}"
    path = INBOX_DIR / f"{task_id}.md"
    title = body.splitlines()[0][:80]
    card = (
        f"# {task_id} — {title}\n\n"
        f"- source: telegram/{chat_type or 'unknown'} (owner {sender_id})\n"
        f"- received: {time.strftime('%Y-%m-%d %H:%M:%S %z')}\n"
        f"- status: OPEN\n"
        f"- owner_text_sha256: {hashlib.sha256(body.encode('utf-8')).hexdigest()}\n\n"
        f"## Owner 原話\n\n{body}\n\n"
        f"## 接手規則\n\n"
        f"1. 接手者先在本卡把 status 改成 IN_PROGRESS 並寫自己的名字，做完改 DONE 並附成果路徑。\n"
        f"2. 做不到、需 Owner 拍板的，改 BLOCKED 並寫清楚缺什麼。\n"
        f"3. 不要另開一張卡重講同一件事；此卡即真相來源。\n"
    )
    path.write_text(card, encoding="utf-8")
    line = f"- [ ] {time.strftime('%Y-%m-%d %H:%M')} `{task_id}` — {title}\n"
    if not QUEUE_FILE.exists():
        QUEUE_FILE.write_text(
            "# handoff/inbox/QUEUE.md — Owner 從 Telegram 交辦的任務佇列\n\n"
            "> 由 A6 gateway 自動追加。每個 Claude／Codex session 開工必讀；接手時把 `[ ]` 改 `[x]` 並在卡片內更新 status。\n\n",
            encoding="utf-8",
        )
    with QUEUE_FILE.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return path


def task_card_reply(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    return (
        f"【hermes】已收交辦，落檔 `{rel}`，並排進 `handoff/inbox/QUEUE.md`。\n"
        "下一個 Claude／Codex session 開工會先讀 inbox；我這邊不執行、不 push。"
        "要立刻查資料可直接跟我講檔名，例如「看 CURRENT_STATUS.md#tail120 的 A6 狀態」。"
    )
