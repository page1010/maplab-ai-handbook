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
    briefing, _meta = load_briefing()
    if briefing:
        used += len(briefing)
        got.append(f"洞悉簡報[{len(briefing)}B]")
        parts.append("----- 洞悉簡報（/boot 時讀完核心文件後寫給自己的） -----\n" + briefing)
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


# ---------------------------------------------------------------- self-fetch (model picks files)

INDEX_DIRS = ("docs", "handoff/tasks", "skills", "recalls", "projects", "config", "bot_a6", "scripts")
INDEX_BUDGET = int(os.environ.get("HERMES_INDEX_BUDGET", "24000"))
READ_LINE_RE = re.compile(r"^\s*(?:【hermes】)?\s*READ\s*[:：]\s*`?([\w.\-/]+(?:#(?:head\d+|tail\d+|L\d+-\d+))?)`?\s*$", re.MULTILINE)
MAX_READS_PER_ROUND = 6
MAX_READ_ROUNDS = 2


def _list_repo_files() -> list[tuple[str, int]]:
    """(relpath, bytes) for the files Hermes may pick from. git ls-files first, os.walk fallback."""
    import subprocess

    rels: list[str] = []
    try:
        out = subprocess.run(
            ["git", "ls-files", "--", "*.md", "*.json", "*.py", "*.sh"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10, check=False,
        ).stdout
        rels = [line.strip() for line in out.splitlines() if line.strip()]
    except (OSError, subprocess.SubprocessError):
        pass
    if not rels:
        for base in ("",) + INDEX_DIRS:
            d = REPO_ROOT / base
            if d.is_dir():
                rels += [str(x.relative_to(REPO_ROOT)) for x in d.iterdir() if x.is_file()]
    keep: list[tuple[str, int]] = []
    for rel in rels:
        top = rel.split("/")[0]
        depth = rel.count("/")
        if not (depth == 0 or any(rel.startswith(d + "/") for d in INDEX_DIRS)):
            continue
        if depth > 2:
            continue
        path = _safe_rel(rel)
        if path is None:
            continue
        try:
            keep.append((rel, path.stat().st_size))
        except OSError:
            continue
    keep.sort()
    return keep


def build_index(budget: int = INDEX_BUDGET) -> str:
    """Route card (HERMES_READ_MAP §1-2) + a bounded file list with sizes, so the model can pick."""
    parts = []
    text, _l, err = read_slice("HERMES_READ_MAP.md#L1-75")
    if text:
        parts.append("----- 路線卡:HERMES_READ_MAP.md(節錄) -----\n" + text)
    lines = [f"{rel} ({size // 1000}KB)" if size >= 1000 else f"{rel} ({size}B)" for rel, size in _list_repo_files()]
    listing = "----- 可讀檔案清單(相對路徑,大檔請用 #headN/#tailN 切片) -----\n" + "\n".join(lines)
    used = sum(len(x) for x in parts)
    if used + len(listing) > budget:
        listing = listing[: max(0, budget - used)] + "\n…(清單被截斷；找不到的檔可先讀 SYSTEM_DIRECTORY_INDEX.md)"
    parts.append(listing)
    return "\n\n".join(parts)


def parse_read_requests(reply: str) -> list[str]:
    specs = []
    for m in READ_LINE_RE.finditer(reply or ""):
        if m.group(1) not in specs:
            specs.append(m.group(1))
    return specs[:MAX_READS_PER_ROUND]


def looks_like_read_only(reply: str) -> bool:
    """True when the model answered with READ lines only (no substantive answer)."""
    stripped = re.sub(r"【hermes】", "", reply or "").strip()
    rest = READ_LINE_RE.sub("", stripped).strip()
    return bool(parse_read_requests(reply)) and len(rest) < 80


PLAN_INSTRUCTION = (
    "\n\n【調閱規則】你手上有上面的路線卡與檔案清單，但還沒有檔案內容。"
    "如果回答需要看檔案，這一輪**只**回覆要讀的檔，每行一個，格式 `READ: 路徑#切片`（最多 6 行，大檔一定切片，例如 `READ: CURRENT_STATUS.md#head60`），不要作答。"
    "如果不需要看檔就能答，直接作答。Owner 不記檔名，由你來挑。"
)


# ---------------------------------------------------------------- boot ritual (召喚：先讀完，再對話)

# Owner 2026-09-29：「你不是應該給一個固定模組召喚他出來嗎？詠唱咒語讓他先讀完，然後我對話他可以找到洞悉。」
# 模型沒有記憶（P1），所以「讀完」必須變成一份檔案：/boot 把 HERMES_READ_MAP §1 的冷啟動清單一次餵進去，
# 讓模型寫一份洞悉簡報存在本機 runtime；之後每一則對話都固定帶這份簡報＋開機包，再加自助調閱。
# 簡報綁 git HEAD；HEAD 變了或 Owner 再唸一次 /boot 就重建。
BOOT_READING = (
    "AGENT_CORE.md",
    "AGENTS.md",
    "docs/company-values.md",
    "CULTURE_DECISION_LOGIC.md",
    "NAMING_GLOSSARY.md",
    "SOP_SEE_BEFORE_YOU_SAY.md",
    "A0_USER_PREFERENCES.md",
    "skills/owner-telegram-conversation-sop.md",
    "docs/fable5-direction-and-guidance.md",
    "decisions.md",
    "AGENT_STARTUP_PROTOCOL.md#head120",
    "AGENT_RULES.md#head350",
    "pitfalls.md#tail250",
    "CURRENT_STATUS.md#head80",
    "TASK_QUEUE.md#head40",
)
BOOT_BUDGET = int(os.environ.get("HERMES_BOOT_BUDGET", "180000"))  # P13 已驗 200KB 召得回
BOOT_PREFIXES = ("/boot", "/召喚", "召喚", "開機", "詠唱")
BRIEFING_PATH = Path.home() / ".local" / "share" / "maplab-a6-hermes" / "briefing.md"
BRIEFING_MAX_CHARS = 6000
BRIEFING_INSTRUCTION = (
    "你是 Hermes，剛被 Owner 召喚上工。上面是 MAPLAB 的核心文件原文。請寫一份「洞悉簡報」給未來沒有記憶的自己，"
    "之後每一則對話都會先讀這份簡報。要求：全繁體、不超過 2500 字、只寫文件裡有的事、每一段標出處檔名。固定七節：\n"
    "1. 這間公司在做什麼、Owner 是誰、怎麼跟 Owner 說話\n2. 席位與我的角色（A6）\n3. 企業文化與判斷邏輯：遇到沒寫過的事怎麼決定\n"
    "4. 紅線（不報價、不選菜、不承諾檔期、不判飲食安全、不碰金鑰與交易；哪些是「需人工」）\n"
    "5. 現在的狀態：進行中任務、Owner 阻塞點、最近三個決策\n6. 常見的坑（從 pitfalls 挑最會再犯的 8 條）\n"
    "7. 我不知道的事（文件沒寫、需要現查的）\n"
    "只輸出簡報本文，第一個字元就是「1.」；不要開場白、不要用英文思考、不要解釋你怎麼寫。"
)


BRIEFING_START_RE = re.compile(r"(?m)^\s*(?:#{1,3}\s*|\*\*)?(?:1[.、．]|一、)")


def extract_briefing(text: str) -> str:
    """模型常先用英文自言自語再寫簡報；從第一個「1.」章節標題起算才是簡報本文。"""
    m = BRIEFING_START_RE.search(text or "")
    if m and m.start() > 0:
        return (text or "")[m.start():].strip()
    return (text or "").strip()


def briefing_quality_issue(text: str) -> str | None:
    """None if the briefing is usable; else the reason. 2026-09-29 實測 nemotron 把英文推理草稿當成簡報吐出來還無限重複。"""
    body = (text or "").strip()
    if len(body) < 400:
        return "太短"
    # 2026-09-29 第一版閘用「中文字 < 英文字母」判定，把一份正常簡報退件了：檔名、網址、Owner、Telegram
    # 這些英文字母本來就多。改看中文佔比（不含空白）。
    compact = re.sub(r"\s+", "", body)
    cjk = sum(1 for ch in compact if "\u4e00" <= ch <= "\u9fff")
    if cjk < 0.35 * len(compact):
        return "中文佔比過低（疑似推理草稿）"
    if re.search(r"\b(we need to|we'll|let's|the user|must not)\b", body[:600], re.IGNORECASE):
        return "開頭是推理草稿不是簡報"
    lines = [ln.strip() for ln in body.splitlines() if len(ln.strip()) > 12]
    if lines:
        from collections import Counter
        top = Counter(lines).most_common(1)[0][1]
        if top >= 4:
            return "同一行重複 %d 次（退化輸出）" % top
    if "1." not in body[:400] and "一、" not in body[:400] and "## 1" not in body[:400]:
        return "沒有第 1 節標題"
    return None


def is_boot_command(text: str) -> bool:
    t = (text or "").strip()
    return any(t == p or t.startswith(p + " ") for p in BOOT_PREFIXES)


def repo_head() -> str:
    import subprocess

    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                              capture_output=True, text=True, timeout=5, check=False).stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def build_boot_prompt() -> tuple[str, list[str], list[str]]:
    got, missing, parts, used = [], [], [], 0
    for spec in BOOT_READING:
        text, label, err = read_slice(spec)
        if text is None:
            missing.append(f"{label}({err})"); continue
        if find_secret_values(text):
            missing.append(f"{label}(疑似憑證值)"); continue
        room = BOOT_BUDGET - used
        if room <= 0:
            missing.append(f"{label}(超出預算)"); continue
        if len(text) > room:
            text = text[:room] + "\n…(截斷)"
        used += len(text); got.append(f"{label}[{len(text)}B]")
        parts.append(f"----- 檔案:{label} -----\n{text}")
    return "\n\n".join(parts) + "\n\n" + BRIEFING_INSTRUCTION, got, missing


def save_briefing(text: str, *, provider: str | None, got: list[str], missing: list[str]) -> Path:
    BRIEFING_PATH.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    header = (
        f"<!-- hermes briefing | head={repo_head()} | built={time.strftime('%Y-%m-%d %H:%M:%S')} | provider={provider} -->\n"
        f"<!-- read={', '.join(got)} | missing={', '.join(missing) or 'none'} -->\n\n"
    )
    body = text.strip()[:BRIEFING_MAX_CHARS]
    fd = os.open(BRIEFING_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(header + body + "\n")
    return BRIEFING_PATH


def load_briefing() -> tuple[str | None, dict]:
    """(briefing_text, meta). meta['stale'] is True when HEAD moved since it was built."""
    try:
        raw = BRIEFING_PATH.read_text(encoding="utf-8")
    except OSError:
        return None, {"exists": False}
    m = re.search(r"head=(\S+) \| built=([^|]+) \| provider=([^ ]*)", raw)
    meta = {"exists": True, "head": m.group(1) if m else "?", "built": m.group(2).strip() if m else "?",
            "provider": m.group(3) if m else "?"}
    meta["stale"] = meta["head"] != repo_head()
    return raw, meta


def briefing_status_line() -> str:
    _b, meta = load_briefing()
    if not meta.get("exists"):
        return "🧠 洞悉簡報：尚未召喚（傳 /boot 讓我先讀完核心文件）"
    return f"🧠 洞悉簡報：{meta['built']} @ {meta['head']}" + ("（repo 已更新，可 /boot 重讀）" if meta.get("stale") else "")


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
