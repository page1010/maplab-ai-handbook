from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional


warnings.filterwarnings("ignore", category=FutureWarning, module=r"google\..*")

SHEET_ID = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
LOG_SHEET = "CONVERSATION_LOG"
DEFAULT_TOKEN_PATH = Path.home() / ".claude" / "mcp-keys" / "google-token.json"
TAIPEI = timezone(timedelta(hours=8))
_LAST_FETCH_SOURCE = "unknown"


class CaseStoreError(RuntimeError):
    pass


@dataclass(frozen=True)
class ConversationMessage:
    msg_id: str
    case_id_sheet: str
    timestamp_text: str
    timestamp_iso: str
    speaker: str
    message: str
    source: str
    line_user_id: str
    reply_to_msg_id: str
    row_number: int


@dataclass(frozen=True)
class CaseRecord:
    case_id: str
    source: str
    channel_user_id: str
    client_name: str
    first_seen_iso: str
    last_seen_iso: str
    first_row_number: int
    last_row_number: int
    message_count: int
    status: str
    summary: str
    extracted: dict


@dataclass(frozen=True)
class SyncResult:
    fetched_rows: int
    message_upserts: int
    case_upserts: int
    latest_row: int
    latest_timestamp: str
    source: str


class CaseStore:
    """Read-only index over LINE CONVERSATION_LOG.

    CONVERSATION_LOG stays the raw evidence source. This store only keeps
    pointers, extracted facts, and candidate case grouping for A6/Telegram.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @classmethod
    def from_env(cls, repo_path: Optional[Path] = None) -> "CaseStore":
        repo = repo_path or Path(os.getenv("REPO_PATH", "/Users/pagemacmini/maplab-ai-handbook"))
        raw_path = os.getenv("CASE_STORE_DB_PATH")
        db_path = Path(raw_path) if raw_path else repo / "data" / "case-store" / "a6_case_store.sqlite3"
        return cls(db_path)

    def sync_from_sheet(self, max_rows: int = 600) -> SyncResult:
        rows = fetch_conversation_log_rows(max_rows=max_rows)
        messages = [row for row in rows if row.source == "LINE" and row.message.strip()]
        message_upserts = self.upsert_messages(messages)
        cases = build_cases_from_messages(messages)
        case_upserts = self.upsert_cases(cases, messages)
        latest = max(messages, key=lambda m: m.row_number, default=None)
        return SyncResult(
            fetched_rows=len(rows),
            message_upserts=message_upserts,
            case_upserts=case_upserts,
            latest_row=latest.row_number if latest else 0,
            latest_timestamp=latest.timestamp_text if latest else "",
            source=_LAST_FETCH_SOURCE,
        )

    def upsert_messages(self, messages: Iterable[ConversationMessage]) -> int:
        count = 0
        now = datetime.now(TAIPEI).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            for msg in messages:
                conn.execute(
                    """
                    INSERT INTO raw_messages (
                        msg_id, case_id_sheet, timestamp_text, timestamp_iso,
                        speaker, message, source, line_user_id, reply_to_msg_id,
                        row_number, ingested_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(msg_id) DO UPDATE SET
                        case_id_sheet=excluded.case_id_sheet,
                        timestamp_text=excluded.timestamp_text,
                        timestamp_iso=excluded.timestamp_iso,
                        speaker=excluded.speaker,
                        message=excluded.message,
                        source=excluded.source,
                        line_user_id=excluded.line_user_id,
                        reply_to_msg_id=excluded.reply_to_msg_id,
                        row_number=excluded.row_number,
                        ingested_at=excluded.ingested_at
                    """,
                    (
                        msg.msg_id,
                        msg.case_id_sheet,
                        msg.timestamp_text,
                        msg.timestamp_iso,
                        msg.speaker,
                        msg.message,
                        msg.source,
                        msg.line_user_id,
                        msg.reply_to_msg_id,
                        msg.row_number,
                        now,
                    ),
                )
                count += 1
        return count

    def upsert_cases(self, cases: Iterable[CaseRecord], messages: Iterable[ConversationMessage]) -> int:
        message_by_case = group_messages_by_case(messages)
        count = 0
        now = datetime.now(TAIPEI).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            for case in cases:
                conn.execute(
                    """
                    INSERT INTO cases (
                        case_id, source, channel_user_id, client_name,
                        first_seen_iso, last_seen_iso, first_row_number,
                        last_row_number, message_count, status, summary, extracted_json,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(case_id) DO UPDATE SET
                        source=excluded.source,
                        channel_user_id=excluded.channel_user_id,
                        client_name=excluded.client_name,
                        first_seen_iso=excluded.first_seen_iso,
                        last_seen_iso=excluded.last_seen_iso,
                        first_row_number=excluded.first_row_number,
                        last_row_number=excluded.last_row_number,
                        message_count=excluded.message_count,
                        status=excluded.status,
                        summary=excluded.summary,
                        extracted_json=excluded.extracted_json,
                        updated_at=excluded.updated_at
                    """,
                    (
                        case.case_id,
                        case.source,
                        case.channel_user_id,
                        case.client_name,
                        case.first_seen_iso,
                        case.last_seen_iso,
                        case.first_row_number,
                        case.last_row_number,
                        case.message_count,
                        case.status,
                        case.summary,
                        json.dumps(case.extracted, ensure_ascii=False, sort_keys=True),
                        now,
                        now,
                    ),
                )
                conn.execute("DELETE FROM case_messages WHERE case_id = ?", (case.case_id,))
                for msg in message_by_case.get(case.case_id, []):
                    conn.execute(
                        "INSERT OR IGNORE INTO case_messages (case_id, msg_id) VALUES (?, ?)",
                        (case.case_id, msg.msg_id),
                    )
                count += 1
        return count

    def recent_cases(self, limit: int = 8, today_only: bool = False) -> list[CaseRecord]:
        where = ""
        params: list[object] = []
        if today_only:
            today = datetime.now(TAIPEI).date().isoformat()
            where = "WHERE substr(last_seen_iso, 1, 10) = ?"
            params.append(today)
        return self._case_query(where, params, limit=limit)

    def search_cases(self, query: str, limit: int = 8) -> list[CaseRecord]:
        query = query.strip()
        if not query:
            return self.recent_cases(limit=limit)
        needle = f"%{query}%"
        params: list[object] = [needle, needle, needle, needle, needle]
        where = """
        WHERE case_id LIKE ?
           OR client_name LIKE ?
           OR channel_user_id LIKE ?
           OR summary LIKE ?
           OR EXISTS (
                SELECT 1 FROM case_messages cm
                JOIN raw_messages rm ON rm.msg_id = cm.msg_id
                WHERE cm.case_id = cases.case_id
                  AND (rm.speaker LIKE ? OR rm.message LIKE ?)
           )
        """
        params.append(needle)
        return self._case_query(where, params, limit=limit)

    def get_case_messages(self, case_id: str, limit: int = 12) -> list[ConversationMessage]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT rm.*
                FROM case_messages cm
                JOIN raw_messages rm ON rm.msg_id = cm.msg_id
                WHERE cm.case_id = ?
                ORDER BY rm.row_number DESC
                LIMIT ?
                """,
                (case_id, limit),
            ).fetchall()
        return [_message_from_sql(row) for row in reversed(rows)]

    def build_quote_context(self, query: str) -> tuple[Optional[CaseRecord], str]:
        cases = self.search_cases(query, limit=1)
        if not cases:
            return None, f"找不到 Case Store 案件：{query}"
        case = cases[0]
        messages = self.get_case_messages(case.case_id, limit=14)
        lines = [
            "# Case Store Context",
            f"- case_id: {case.case_id}",
            f"- source: {case.source}",
            f"- client_name: {case.client_name}",
            f"- line_user_id: {case.channel_user_id}",
            f"- last_seen: {case.last_seen_iso}",
            f"- summary: {case.summary}",
            f"- extracted: {json.dumps(case.extracted, ensure_ascii=False)}",
            "",
            "## Recent LINE inbound messages",
        ]
        for msg in messages:
            lines.append(f"- row {msg.row_number} | {msg.timestamp_text} | {msg.speaker}: {msg.message}")
        lines.extend(
            [
                "",
                "請用以上案件脈絡產出 A5 報價草稿。注意 LINE webhook 只含客戶傳入訊息，",
                "若缺少我方回覆或最後確認資訊，請列在待確認，不要自行補完。",
            ]
        )
        return case, "\n".join(lines)

    def _case_query(self, where_sql: str, params: list[object], limit: int) -> list[CaseRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"""
                SELECT *
                FROM cases
                {where_sql}
                ORDER BY last_row_number DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()
        return [_case_from_sql(row) for row in rows]

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS raw_messages (
                    msg_id TEXT PRIMARY KEY,
                    case_id_sheet TEXT,
                    timestamp_text TEXT,
                    timestamp_iso TEXT,
                    speaker TEXT,
                    message TEXT,
                    source TEXT,
                    line_user_id TEXT,
                    reply_to_msg_id TEXT,
                    row_number INTEGER,
                    ingested_at TEXT
                );

                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    source TEXT,
                    channel_user_id TEXT,
                    client_name TEXT,
                    first_seen_iso TEXT,
                    last_seen_iso TEXT,
                    first_row_number INTEGER,
                    last_row_number INTEGER,
                    message_count INTEGER,
                    status TEXT,
                    summary TEXT,
                    extracted_json TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS case_messages (
                    case_id TEXT,
                    msg_id TEXT,
                    PRIMARY KEY (case_id, msg_id)
                );

                CREATE INDEX IF NOT EXISTS idx_raw_messages_line_user
                    ON raw_messages(line_user_id, row_number);
                CREATE INDEX IF NOT EXISTS idx_cases_last_row
                    ON cases(last_row_number);
                """
            )


def fetch_conversation_log_rows(max_rows: int = 600) -> list[ConversationMessage]:
    values = _fetch_sheet_values()
    if not values:
        return []
    header = values[0]
    data_rows = values[1:]
    start_index = max(0, len(data_rows) - max_rows)
    messages: list[ConversationMessage] = []
    for offset, row in enumerate(data_rows[start_index:], start=start_index + 2):
        padded = list(row) + [""] * max(0, 8 - len(row))
        record = dict(zip(header, padded))
        msg_id = (record.get("msg_id") or "").strip()
        if not msg_id:
            continue
        timestamp_text = (record.get("timestamp") or "").strip()
        messages.append(
            ConversationMessage(
                msg_id=msg_id,
                case_id_sheet=(record.get("case_id") or "").strip(),
                timestamp_text=timestamp_text,
                timestamp_iso=parse_sheet_timestamp(timestamp_text),
                speaker=(record.get("speaker") or "").strip(),
                message=(record.get("message") or "").strip(),
                source=(record.get("source") or "").strip(),
                line_user_id=(record.get("line_user_id") or "").strip(),
                reply_to_msg_id=(record.get("reply_to_msg_id") or "").strip(),
                row_number=offset,
            )
        )
    return messages


def _fetch_sheet_values() -> list[list[str]]:
    global _LAST_FETCH_SOURCE
    fallback_path = Path(
        os.getenv(
            "CASE_STORE_FALLBACK_JSON",
            "/Users/pagemacmini/maplab-ai-handbook/data/case-store/conversation_log_seed.json",
        )
    )
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except Exception as exc:  # pragma: no cover - local dependency issue
        raise CaseStoreError(f"Google Sheets libraries unavailable: {exc}") from exc

    token_path = Path(os.getenv("GOOGLE_OAUTH_TOKEN_PATH", str(DEFAULT_TOKEN_PATH))).expanduser()
    if not token_path.exists():
        if fallback_path.exists():
            _LAST_FETCH_SOURCE = f"fallback:{fallback_path}"
            return json.loads(fallback_path.read_text(encoding="utf-8"))
        raise CaseStoreError(f"Google OAuth token not found: {token_path}")

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_authorized_user_file(str(token_path), scopes=scopes)
    try:
        service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=SHEET_ID,
                range=f"{LOG_SHEET}!A:H",
                valueRenderOption="FORMATTED_VALUE",
            )
            .execute()
        )
        _LAST_FETCH_SOURCE = "live_google_sheets"
        return result.get("values", [])
    except Exception as exc:
        if fallback_path.exists():
            _LAST_FETCH_SOURCE = f"fallback:{fallback_path}"
            return json.loads(fallback_path.read_text(encoding="utf-8"))
        raise CaseStoreError(
            "Google Sheets read failed and no fallback seed is available. "
            f"Token path: {token_path}. Error: {exc}"
        ) from exc


def build_cases_from_messages(messages: Iterable[ConversationMessage]) -> list[CaseRecord]:
    by_user: dict[str, list[ConversationMessage]] = {}
    for msg in messages:
        if not msg.line_user_id:
            continue
        by_user.setdefault(msg.line_user_id, []).append(msg)

    cases: list[CaseRecord] = []
    for line_user_id, user_messages in by_user.items():
        ordered = sorted(user_messages, key=lambda m: (m.timestamp_iso, m.row_number))
        clusters: list[list[ConversationMessage]] = []
        for msg in ordered:
            if not clusters:
                clusters.append([msg])
                continue
            previous = clusters[-1][-1]
            if _gap_hours(previous.timestamp_iso, msg.timestamp_iso) > 168:
                clusters.append([msg])
            else:
                clusters[-1].append(msg)
        for cluster in clusters:
            cases.append(_case_from_cluster(line_user_id, cluster))
    return sorted(cases, key=lambda c: c.last_row_number, reverse=True)


def group_messages_by_case(messages: Iterable[ConversationMessage]) -> dict[str, list[ConversationMessage]]:
    grouped: dict[str, list[ConversationMessage]] = {}
    cases = build_cases_from_messages(messages)
    for case in cases:
        grouped[case.case_id] = []
    for msg in messages:
        if not msg.line_user_id:
            continue
        for case in cases:
            if (
                case.channel_user_id == msg.line_user_id
                and case.first_row_number <= msg.row_number <= case.last_row_number
            ):
                grouped[case.case_id].append(msg)
    return grouped


def _case_from_cluster(line_user_id: str, cluster: list[ConversationMessage]) -> CaseRecord:
    first = cluster[0]
    last = cluster[-1]
    date_key = (first.timestamp_iso or datetime.now(TAIPEI).isoformat())[:10].replace("-", "")
    case_id = first.case_id_sheet or f"LINE-{date_key}-{_line_hash(line_user_id)}-{first.row_number}"
    extracted = extract_case_facts(cluster)
    summary = summarize_cluster(cluster, extracted)
    return CaseRecord(
        case_id=case_id,
        source="LINE",
        channel_user_id=line_user_id,
        client_name=last.speaker or first.speaker or "不明",
        first_seen_iso=first.timestamp_iso,
        last_seen_iso=last.timestamp_iso,
        first_row_number=first.row_number,
        last_row_number=last.row_number,
        message_count=len(cluster),
        status="candidate",
        summary=summary,
        extracted=extracted,
    )


def extract_case_facts(messages: Iterable[ConversationMessage]) -> dict:
    text = "\n".join(msg.message for msg in messages)
    facts: dict[str, object] = {}
    date_match = re.search(r"(\d{1,2})[/-](\d{1,2})(?:\s*[\(（]?[一二三四五六日天][\)）]?)?", text)
    if date_match:
        facts["event_date_hint"] = date_match.group(0)
    full_date = re.search(r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})", text)
    if full_date:
        facts["event_date_hint"] = full_date.group(0)
    people = re.findall(r"(\d{1,4})\s*(?:人|位)", text)
    if people:
        facts["pax_hint"] = int(people[-1])
    budget = _find_budget(text)
    if budget:
        facts["budget_hint"] = budget
    time_match = re.search(r"(\d{1,2}[:：]\d{2}\s*[-~到至]\s*\d{1,2}[:：]\d{2})", text)
    if time_match:
        facts["event_time_hint"] = time_match.group(1)
    event_keywords = [
        "講座",
        "開幕",
        "茶會",
        "婚禮",
        "週歲",
        "生日",
        "家庭日",
        "晚宴",
        "派對",
        "記者會",
    ]
    found = [kw for kw in event_keywords if kw in text]
    if found:
        facts["event_type_hint"] = found[-1]
    if "台南" in text:
        facts["location_hint"] = "台南"
    elif "高雄" in text:
        facts["location_hint"] = "高雄"
    elif "嘉義" in text:
        facts["location_hint"] = "嘉義"
    missing = [
        label
        for key, label in [
            ("event_date_hint", "日期"),
            ("event_time_hint", "時段"),
            ("pax_hint", "人數"),
            ("budget_hint", "預算"),
            ("location_hint", "地點"),
            ("event_type_hint", "活動類型"),
        ]
        if key not in facts
    ]
    facts["missing_fields"] = missing
    return facts


def summarize_cluster(messages: Iterable[ConversationMessage], facts: dict) -> str:
    items = []
    for key, label in [
        ("event_date_hint", "日期"),
        ("event_time_hint", "時段"),
        ("event_type_hint", "類型"),
        ("pax_hint", "人數"),
        ("budget_hint", "預算"),
        ("location_hint", "地點"),
    ]:
        value = facts.get(key)
        if value:
            if key == "budget_hint" and isinstance(value, int):
                value = f"NT${value:,}"
            items.append(f"{label}:{value}")
    latest = list(messages)[-1].message.replace("\n", " ")[:80]
    if items:
        return " / ".join(items) + f" / 最新:{latest}"
    return f"最新:{latest}"


def render_case_list(cases: list[CaseRecord], title: str = "LINE 案件候選") -> str:
    if not cases:
        return f"{title}\n目前找不到符合條件的案件。"
    lines = [f"{title}（{len(cases)} 筆）"]
    for index, case in enumerate(cases, start=1):
        missing = "、".join(case.extracted.get("missing_fields", [])) or "無"
        lines.append(
            "\n".join(
                [
                    f"{index}. {case.client_name}｜{case.case_id}",
                    f"   最新 row {case.last_row_number}｜訊息 {case.message_count} 則｜缺：{missing}",
                    f"   {case.summary}",
                ]
            )
        )
    return "\n\n".join(lines)


def render_case_detail(case: CaseRecord, messages: list[ConversationMessage]) -> str:
    missing = "、".join(case.extracted.get("missing_fields", [])) or "無"
    lines = [
        f"Case Store：{case.case_id}",
        f"客戶/LINE 名稱：{case.client_name}",
        f"來源：{case.source}｜line_user_id: {case.channel_user_id}",
        f"時間：{case.first_seen_iso} → {case.last_seen_iso}",
        f"摘要：{case.summary}",
        f"缺資料：{missing}",
        "",
        "近期訊息：",
    ]
    for msg in messages:
        one_line = msg.message.replace("\n", " ")
        lines.append(f"- row {msg.row_number}｜{msg.timestamp_text}｜{msg.speaker}: {one_line}")
    return "\n".join(lines)


def parse_sheet_timestamp(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    match = re.match(
        r"(?P<y>\d{4})/(?P<m>\d{1,2})/(?P<d>\d{1,2})\s+(?P<ampm>上午|下午)\s+(?P<h>\d{1,2}):(?P<mi>\d{2})(?::(?P<s>\d{2}))?",
        value,
    )
    if match:
        hour = int(match.group("h"))
        if match.group("ampm") == "下午" and hour < 12:
            hour += 12
        if match.group("ampm") == "上午" and hour == 12:
            hour = 0
        dt = datetime(
            int(match.group("y")),
            int(match.group("m")),
            int(match.group("d")),
            hour,
            int(match.group("mi")),
            int(match.group("s") or 0),
            tzinfo=TAIPEI,
        )
        return dt.isoformat()
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=TAIPEI).isoformat()
        except ValueError:
            pass
    return value


def _find_budget(text: str) -> Optional[int]:
    patterns = [
        r"(?:預算|budget|費用|金額)\s*(?:約|大約)?\s*\$?\s*(\d+(?:\.\d+)?)\s*([萬万kK]?)",
        r"\$?\s*(\d+(?:\.\d+)?)\s*([萬万kK])",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        amount = float(match.group(1))
        unit = match.group(2) or ""
        if unit in {"萬", "万"}:
            amount *= 10000
        elif unit in {"k", "K"}:
            amount *= 1000
        return int(amount)
    return None


def _gap_hours(left_iso: str, right_iso: str) -> float:
    try:
        left = datetime.fromisoformat(left_iso)
        right = datetime.fromisoformat(right_iso)
    except ValueError:
        return 0
    return abs((right - left).total_seconds()) / 3600


def _line_hash(line_user_id: str) -> str:
    return hashlib.sha1(line_user_id.encode("utf-8")).hexdigest()[:8]


def _case_from_sql(row: sqlite3.Row) -> CaseRecord:
    extracted = json.loads(row["extracted_json"] or "{}")
    return CaseRecord(
        case_id=row["case_id"],
        source=row["source"],
        channel_user_id=row["channel_user_id"],
        client_name=row["client_name"],
        first_seen_iso=row["first_seen_iso"],
        last_seen_iso=row["last_seen_iso"],
        first_row_number=int(row["first_row_number"] or 0),
        last_row_number=int(row["last_row_number"] or 0),
        message_count=int(row["message_count"] or 0),
        status=row["status"],
        summary=row["summary"],
        extracted=extracted,
    )


def _message_from_sql(row: sqlite3.Row) -> ConversationMessage:
    return ConversationMessage(
        msg_id=row["msg_id"],
        case_id_sheet=row["case_id_sheet"],
        timestamp_text=row["timestamp_text"],
        timestamp_iso=row["timestamp_iso"],
        speaker=row["speaker"],
        message=row["message"],
        source=row["source"],
        line_user_id=row["line_user_id"],
        reply_to_msg_id=row["reply_to_msg_id"],
        row_number=int(row["row_number"] or 0),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="MAPLAB A6 Case Store CLI")
    parser.add_argument("command", choices=["sync", "recent", "today", "search", "detail"])
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--rows", type=int, default=600)
    args = parser.parse_args()

    store = CaseStore.from_env()
    if args.command == "sync":
        result = store.sync_from_sheet(max_rows=args.rows)
        print(
            f"sync ok: fetched={result.fetched_rows} messages={result.message_upserts} "
            f"cases={result.case_upserts} latest_row={result.latest_row} "
            f"latest={result.latest_timestamp} source={result.source}"
        )
    elif args.command == "today":
        result = store.sync_from_sheet(max_rows=args.rows)
        print(f"source={result.source} latest_row={result.latest_row}")
        print(render_case_list(store.recent_cases(limit=args.limit, today_only=True), "今日 LINE 案件候選"))
    elif args.command == "recent":
        print(render_case_list(store.recent_cases(limit=args.limit), "近期 LINE 案件候選"))
    elif args.command == "search":
        print(render_case_list(store.search_cases(args.query, limit=args.limit), f"搜尋：{args.query}"))
    elif args.command == "detail":
        cases = store.search_cases(args.query, limit=1)
        if not cases:
            print(f"找不到案件：{args.query}")
            return
        print(render_case_detail(cases[0], store.get_case_messages(cases[0].case_id)))


if __name__ == "__main__":
    main()
