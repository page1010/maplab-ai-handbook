from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Optional


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "hermes-line-sheets-assistant-v1.json"

COLLECTING = "COLLECTING"
AWAITING_SUMMARY_CONFIRMATION = "AWAITING_SUMMARY_CONFIRMATION"
CONFIRMED = "CONFIRMED"

_CASE_ID = re.compile(r"^[A-Z0-9][A-Z0-9._:-]{5,79}$")
_QUOTE_ID = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DATE = re.compile(r"^(20\d{2})-(\d{2})-(\d{2})$")
_TIME_RANGE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$")


@lru_cache(maxsize=1)
def load_contract() -> dict:
    with CONTRACT_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@dataclass(frozen=True)
class ConfirmationReceipt:
    summary_digest: str
    confirmation_message_digest: str
    confirmation_source_ref_hash: str
    confirmed_at: str


@dataclass(frozen=True)
class SheetsAssistantState:
    """Explicit intake facts plus the stage-bound confirmation receipt.

    Hermes may collect and hand facts to Sheets. It cannot calculate a quote,
    select a menu, hold availability, confirm a booking, or decide food safety.
    """

    fields: dict[str, object] = field(default_factory=dict)
    stage: str = COLLECTING
    pending_summary_digest: str = ""
    confirmation_receipt: Optional[ConfirmationReceipt] = None

    @property
    def missing_fields(self) -> list[str]:
        return [
            key
            for key in load_contract()["required_field_order"]
            if not _field_is_valid(key, self.fields.get(key))
        ]

    @property
    def intake_complete(self) -> bool:
        return not self.missing_fields

    @property
    def summary_confirmed(self) -> bool:
        return self.stage == CONFIRMED and self.confirmation_receipt is not None

    def next_question(self) -> Optional[str]:
        if not self.missing_fields:
            return None
        return load_contract()["field_questions"][self.missing_fields[0]]


def apply_survey_response(
    state: SheetsAssistantState,
    response: Mapping[str, object],
) -> SheetsAssistantState:
    """Apply explicit survey fields; invalid or unknown facts fail closed."""

    allowed = set(load_contract()["required_field_order"])
    fields = dict(state.fields)
    for key, raw_value in response.items():
        if key not in allowed:
            raise ValueError(f"unknown_survey_field:{key}")
        value = _normalise_field(key, raw_value)
        if not _field_is_valid(key, value):
            raise ValueError(f"invalid_survey_field:{key}")
        fields[key] = value
    return SheetsAssistantState(fields=fields)


def apply_sheets_customer_message(
    state: SheetsAssistantState,
    message: str,
) -> SheetsAssistantState:
    """Capture only the answer to the currently asked field.

    This stage-aware parser intentionally does not reuse the legacy quote
    parser. In particular, a bare ``沒有`` is dietary data only while the
    dietary question is pending, and an event type never implies a service.
    """

    text = message.strip()
    if not text:
        return state

    fields = dict(state.fields)
    if _contains_budget_statement(text):
        fields["customer_budget_verbatim"] = text

    missing = SheetsAssistantState(fields=fields).missing_fields
    if missing:
        key = missing[0]
        value = _extract_expected_field(key, text)
        if value is not None:
            value = _normalise_field(key, value)
            if _field_is_valid(key, value):
                fields[key] = value

    # Any new customer message invalidates an older receipt. A new
    # confirmation must be bound to the freshly rendered summary.
    return SheetsAssistantState(fields=fields)


def prepare_summary_confirmation(
    state: SheetsAssistantState,
) -> tuple[SheetsAssistantState, str]:
    if not state.intake_complete:
        raise ValueError("intake_not_complete")
    summary = render_summary_confirmation(state)
    digest = _sha256_text(summary)
    awaiting = SheetsAssistantState(
        fields=dict(state.fields),
        stage=AWAITING_SUMMARY_CONFIRMATION,
        pending_summary_digest=digest,
    )
    return awaiting, summary


def confirm_intake_summary(
    state: SheetsAssistantState,
    customer_message: str,
    *,
    source_message_ref: str,
    confirmed_at: Optional[str] = None,
) -> SheetsAssistantState:
    """Confirm only as a reply to the current, digest-bound summary."""

    if state.stage != AWAITING_SUMMARY_CONFIRMATION:
        raise ValueError("summary_confirmation_wrong_stage")
    if not state.intake_complete:
        raise ValueError("intake_not_complete")
    current_digest = _sha256_text(render_summary_confirmation(state))
    if not state.pending_summary_digest or not hmac.compare_digest(
        current_digest, state.pending_summary_digest
    ):
        raise ValueError("summary_digest_stale")

    compact = re.sub(r"[\s，。！!？?]", "", customer_message)
    accepted = {"正確", "資料正確", "以上正確", "確認", "確認無誤", "沒錯", "是的"}
    if compact not in accepted:
        raise ValueError("explicit_summary_confirmation_required")
    if not source_message_ref.strip():
        raise ValueError("confirmation_source_ref_required")

    timestamp = confirmed_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    parsed_timestamp = _parse_utc_timestamp(timestamp)
    receipt = ConfirmationReceipt(
        summary_digest=current_digest,
        confirmation_message_digest=_sha256_text(customer_message.strip()),
        confirmation_source_ref_hash=_sha256_text(source_message_ref.strip()),
        confirmed_at=parsed_timestamp.isoformat().replace("+00:00", "Z"),
    )
    return SheetsAssistantState(
        fields=dict(state.fields),
        stage=CONFIRMED,
        pending_summary_digest=current_digest,
        confirmation_receipt=receipt,
    )


def compose_intake_reply(
    state: SheetsAssistantState,
    customer_message: str,
) -> tuple[SheetsAssistantState, str]:
    """Apply one customer answer and return one restrained next response."""

    updated = apply_sheets_customer_message(state, customer_message)
    if updated.intake_complete:
        awaiting, reply = prepare_summary_confirmation(updated)
        assert_safe_customer_reply(reply, require_question=True)
        return awaiting, reply

    question = updated.next_question()
    prefix = _bounded_acknowledgement(customer_message)
    reply = f"{prefix}{question}" if prefix else str(question)
    assert_safe_customer_reply(reply, require_question=True)
    return updated, reply


def render_summary_confirmation(state: SheetsAssistantState) -> str:
    if not state.intake_complete:
        raise ValueError("intake_not_complete")
    f = state.fields
    return "\n".join(
        [
            "我先跟您確認：",
            f"需求類別：{f['business_category']}",
            f"日期：{f['event_date']}",
            f"時間：{f['event_time']}",
            f"人數：{f['headcount']} 位",
            f"場地：{f['venue']}（{f['indoor_outdoor']}）",
            f"服務形式：{f['service_format']}",
            f"飲食需求：{f['dietary_notes']}",
            f"搬運條件：{f['logistics']}",
            "以上資訊是否正確呢？",
        ]
    )


def render_sheet_handoff_acknowledgement() -> str:
    reply = "謝謝確認，我先把資料整理進內部需求單，內容會由 Mina 核對後再回覆您。"
    assert_safe_customer_reply(reply)
    return reply


def route_no_reply(*, reminder_already_sent: bool) -> str:
    return "WAITING_PAUSED" if reminder_already_sent else "FOLLOWUP_ONCE"


def route_customer_quote_response(response_type: str) -> str:
    routes = {
        "yes": "NEEDS_MINA_CONFIRMATION",
        "no": "WAITING_CLOSE_REASON",
        "adjustment": "WAITING_REVISION_DETAIL",
        "no_reply": "WAITING_QUOTE",
    }
    try:
        return routes[response_type]
    except KeyError as exc:
        raise ValueError("unsupported_quote_response_type") from exc


def render_flow_template(template_id: str, state: SheetsAssistantState) -> str:
    """Connect the audited template inventory to executable copy rendering."""

    templates = {item["id"]: item for item in load_contract()["templates"]}
    if template_id not in templates:
        raise ValueError("unknown_template_id")
    text = templates[template_id]["customer_facing"]
    if "{next_missing_question}" in text:
        question = state.next_question()
        if not question:
            raise ValueError("template_requires_missing_field")
        text = text.replace("{next_missing_question}", question)
    assert_safe_customer_reply(text, require_question=("？" in text or "?" in text))
    return text


def dispatch_flow_event(
    state: SheetsAssistantState,
    event: str,
    *,
    customer_message: str = "",
    reminder_already_sent: bool = False,
) -> dict[str, object]:
    """Executable transition router for the owner-approved flowchart."""

    if event in {"survey_received", "customer_reply"}:
        updated, reply = compose_intake_reply(state, customer_message)
        return {
            "state": updated,
            "reply": reply,
            "next": (
                AWAITING_SUMMARY_CONFIRMATION
                if updated.stage == AWAITING_SUMMARY_CONFIRMATION
                else "WAITING_CUSTOMER"
            ),
        }
    if event == "intake_no_reply":
        template_id = "F48" if not reminder_already_sent else None
        return {
            "state": state,
            "reply": render_flow_template(template_id, state) if template_id else "",
            "next": route_no_reply(reminder_already_sent=reminder_already_sent),
        }
    if event == "quote_yes":
        return {
            "state": state,
            "reply": render_flow_template("HUMAN_CONFIRM", state),
            "next": route_customer_quote_response("yes"),
        }
    if event == "quote_no":
        return {
            "state": state,
            "reply": render_flow_template("CLOSE_REASON", state),
            "next": route_customer_quote_response("no"),
        }
    if event == "quote_adjustment":
        return {
            "state": state,
            "reply": render_flow_template("Q8_REVISION", state),
            "next": route_customer_quote_response("adjustment"),
        }
    if event == "quote_no_reply":
        return {"state": state, "reply": "", "next": route_customer_quote_response("no_reply")}
    raise ValueError("unsupported_flow_event")


def build_quote_shell_payload(
    state: SheetsAssistantState,
    *,
    case_id: str,
    source: str,
    client_name: str = "",
    company: str = "",
    contact_ref_hash: str = "",
) -> dict:
    """Build a non-commercial Sheets handoff bound to customer confirmation."""

    if not state.intake_complete:
        raise ValueError(f"intake_not_complete:{','.join(state.missing_fields)}")
    if not state.summary_confirmed or not state.confirmation_receipt:
        raise ValueError("explicit_summary_confirmation_required")
    if not _CASE_ID.fullmatch(case_id.strip()):
        raise ValueError("invalid_case_id")
    if source != "line":
        raise ValueError("source_must_be_line")
    if contact_ref_hash and not _SHA256.fullmatch(contact_ref_hash):
        raise ValueError("contact_ref_hash_required")

    f = state.fields
    receipt = state.confirmation_receipt
    payload = {
        "action": "createQuoteShell",
        "schemaVersion": load_contract()["schema_version"],
        "caseId": case_id.strip(),
        "source": source,
        "clientName": str(client_name).strip(),
        "company": str(company).strip(),
        "contactRefHash": contact_ref_hash,
        "businessCategory": str(f["business_category"]),
        "eventDate": str(f["event_date"]),
        "eventTime": str(f["event_time"]),
        "venue": str(f["venue"]),
        "indoorOutdoor": str(f["indoor_outdoor"]),
        "headcount": int(f["headcount"]),
        "serviceFormat": str(f["service_format"]),
        "dietaryNotesVerbatim": str(f["dietary_notes"]),
        "logisticsNotesVerbatim": str(f["logistics"]),
        "summaryConfirmed": True,
        "summaryText": render_summary_confirmation(state),
        "summaryDigest": receipt.summary_digest,
        "summaryConfirmedAt": receipt.confirmed_at,
        "confirmationMessageDigest": receipt.confirmation_message_digest,
        "confirmationSourceRefHash": receipt.confirmation_source_ref_hash,
        "availabilityStatus": "UNVERIFIED",
        "dietaryReviewStatus": "PENDING_HUMAN",
        "commercialReviewStatus": "PENDING_MINA",
    }
    validate_quote_shell_payload(payload)
    return payload


def validate_quote_shell_payload(payload: Mapping[str, object]) -> None:
    contract = load_contract()["sheets_handoff"]
    _validate_exact_keys(payload, contract, "unsafe_quote_shell_payload")
    if payload.get("action") != "createQuoteShell":
        raise ValueError("unsafe_quote_shell_action")
    if payload.get("schemaVersion") != load_contract()["schema_version"]:
        raise ValueError("unsafe_quote_shell_schema")
    if payload.get("source") != "line":
        raise ValueError("source_must_be_line")
    if not _CASE_ID.fullmatch(str(payload.get("caseId", ""))):
        raise ValueError("invalid_case_id")
    if payload.get("contactRefHash") and not _SHA256.fullmatch(str(payload["contactRefHash"])):
        raise ValueError("invalid_contact_ref_hash")
    field_map = {
        "business_category": payload.get("businessCategory"),
        "event_date": payload.get("eventDate"),
        "event_time": payload.get("eventTime"),
        "venue": payload.get("venue"),
        "indoor_outdoor": payload.get("indoorOutdoor"),
        "headcount": payload.get("headcount"),
        "service_format": payload.get("serviceFormat"),
        "dietary_notes": payload.get("dietaryNotesVerbatim"),
        "logistics": payload.get("logisticsNotesVerbatim"),
    }
    invalid = [key for key, value in field_map.items() if not _field_is_valid(key, value)]
    if invalid:
        raise ValueError(f"invalid_intake_fields:{','.join(invalid)}")
    if payload.get("summaryConfirmed") is not True:
        raise ValueError("summary_confirmation_receipt_required")
    if _sha256_text(str(payload.get("summaryText", ""))) != payload.get("summaryDigest"):
        raise ValueError("summary_digest_mismatch")
    for key in ("summaryDigest", "confirmationMessageDigest", "confirmationSourceRefHash"):
        if not _SHA256.fullmatch(str(payload.get(key, ""))):
            raise ValueError(f"invalid_confirmation_receipt:{key}")
    _parse_utc_timestamp(str(payload.get("summaryConfirmedAt", "")))
    if payload.get("availabilityStatus") != "UNVERIFIED":
        raise ValueError("availability_must_be_unverified")
    if payload.get("dietaryReviewStatus") != "PENDING_HUMAN":
        raise ValueError("dietary_review_must_be_human")
    if payload.get("commercialReviewStatus") != "PENDING_MINA":
        raise ValueError("commercial_review_must_be_mina")


def build_revision_request_payload(
    *,
    case_id: str,
    quote_id: str,
    customer_change_verbatim: str,
    source: str = "line",
    contact_ref_hash: str = "",
) -> dict:
    """Request a revision; the server owns lineage and revision numbering."""

    change = customer_change_verbatim.strip()
    payload = {
        "action": "appendQuoteRevisionRequest",
        "schemaVersion": "hermes-sheets-revision-v1",
        "caseId": case_id.strip(),
        "quoteId": quote_id.strip(),
        "source": source,
        "contactRefHash": contact_ref_hash,
        "customerChangeVerbatim": change,
        "changeDigest": _sha256_text(change),
        "changeStatus": "PENDING_MINA",
    }
    validate_revision_request_payload(payload)
    return payload


def validate_revision_request_payload(payload: Mapping[str, object]) -> None:
    contract = load_contract()["revision_handoff"]
    _validate_exact_keys(payload, contract, "unsafe_revision_payload")
    if payload.get("action") != "appendQuoteRevisionRequest":
        raise ValueError("unsafe_revision_action")
    if payload.get("schemaVersion") != "hermes-sheets-revision-v1":
        raise ValueError("unsafe_revision_schema")
    if not _CASE_ID.fullmatch(str(payload.get("caseId", ""))):
        raise ValueError("invalid_case_id")
    if not _QUOTE_ID.fullmatch(str(payload.get("quoteId", ""))):
        raise ValueError("invalid_quote_id")
    if payload.get("source") != "line":
        raise ValueError("source_must_be_line")
    if payload.get("contactRefHash") and not _SHA256.fullmatch(str(payload["contactRefHash"])):
        raise ValueError("invalid_contact_ref_hash")
    change = str(payload.get("customerChangeVerbatim", "")).strip()
    if not change or len(change) > 2000:
        raise ValueError("invalid_customer_change")
    if payload.get("changeDigest") != _sha256_text(change):
        raise ValueError("change_digest_mismatch")
    if payload.get("changeStatus") != "PENDING_MINA":
        raise ValueError("revision_must_be_pending_mina")


def build_signed_request_envelope(
    payload: Mapping[str, object],
    *,
    secret: str,
    issued_at: int,
    nonce: str,
    actor: str = "hermes-sheets-assistant",
) -> dict:
    """Create the exact envelope accepted by the isolated Apps Script."""

    if not secret:
        raise ValueError("hmac_secret_required")
    if not isinstance(issued_at, int) or isinstance(issued_at, bool) or issued_at < 1:
        raise ValueError("issued_at_must_be_epoch_seconds")
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", nonce):
        raise ValueError("invalid_nonce")
    action = str(payload.get("action", ""))
    if action not in {"createQuoteShell", "appendQuoteRevisionRequest"}:
        raise ValueError("action_not_allowed")
    signed_payload = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    auth_version = "hmac-sha256-v1"
    message = "\n".join(
        [auth_version, actor, str(issued_at), nonce, action, signed_payload]
    )
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return {
        "action": action,
        "authVersion": auth_version,
        "actor": actor,
        "issuedAt": issued_at,
        "nonce": nonce,
        "signedPayload": signed_payload,
        "signature": signature,
    }


def customer_reply_violations(reply: str, *, require_question: bool = False) -> list[str]:
    """Deterministic backstop; production replies use approved templates."""

    text = reply.strip()
    violations: list[str] = []
    question_count = text.count("？") + text.count("?")
    if question_count > 1:
        violations.append("more_than_one_question")
    if require_question and question_count != 1:
        violations.append("expected_exactly_one_question")
    question_clause = re.split(r"[。！!\n]", text)[-1]
    if question_count and _requested_field_count(question_clause) > 1:
        violations.append("multiple_requested_fields")

    chinese_amount = r"[零〇一二兩三四五六七八九十百千萬億]+\s*(?:元|塊)"
    patterns = {
        "money_or_terms_commitment": (
            r"(?:NT\$|新台幣|\$)\s*\d",
            r"\d[\d,]*(?:\.\d+)?\s*元",
            chinese_amount,
            r"(?:免費|免(?:費|訂金)|不用訂金|不收訂金)",
            r"(?:總價|價格|報價|費用|低消|訂金|折扣)[^。！？\n]{0,24}(?:固定|就是|為|是)",
        ),
        "availability_commitment": (
            r"(?:檔期|這天|那天|日期)[^。！？\n]{0,20}(?:有空|可以接|能接|沒問題|保留|留起來|留給|已滿|一定)",
            r"(?:我們|這邊)[^。！？\n]{0,8}(?:可以接|能接)",
            r"(?:替您|幫您|已經|我已)[^。！？\n]{0,16}(?:保留|留起來|留給)",
        ),
        "dietary_safety_claim": (
            r"(?:所有人|大家)[^。！？\n]{0,16}(?:可以吃|都能吃|安全)",
            r"沒有任何飲食限制",
            r"(?:不含|沒有)[^。！？\n]{0,16}(?:堅果|過敏原|麩質|乳製品)[^。！？\n]{0,16}(?:放心|安全|可以吃|可食用)",
            r"(?:過敏|飲食|食材)[^。！？\n]{0,20}(?:沒問題|一定安全|都可以|放心)",
            r"(?:放心食用|可以放心吃)",
        ),
        "no_more_confirmation": (
            r"(?:不用|不必|無須)再(?:提供資料|確認|詢問)",
            r"資料都齊了[^。！？\n]{0,8}(?:不用|不必|無須)",
        ),
        "booking_commitment": (
            r"直接下訂",
            r"(?:訂單|預約)[^。！？\n]{0,10}(?:已成立|成立了|完成|已確認)",
            r"(?:已|替您|幫您)[^。！？\n]{0,12}(?:下訂|訂位|保留)",
            r"已為您登記完成",
        ),
        "overconfident_tone": (
            r"(?:^|[，。！\s])沒問題(?:[，。！\s]|$)",
            r"(?:一定|保證|絕對)(?:有空|可以|安全|沒問題|能)",
        ),
    }
    for code, expressions in patterns.items():
        if any(re.search(expression, text, re.IGNORECASE) for expression in expressions):
            violations.append(code)
    return violations


def assert_safe_customer_reply(reply: str, *, require_question: bool = False) -> None:
    violations = customer_reply_violations(reply, require_question=require_question)
    if violations:
        raise ValueError(f"unsafe_customer_reply:{','.join(violations)}")


def _validate_exact_keys(payload: Mapping[str, object], contract: Mapping[str, object], label: str) -> None:
    allowed = set(contract["allowed_payload_keys"])
    forbidden = set(contract["forbidden_payload_keys"])
    keys = set(payload)
    extra = sorted(keys - allowed)
    blocked = sorted(keys & forbidden)
    missing = sorted(allowed - keys)
    if extra or blocked or missing:
        raise ValueError(f"{label}:extra={extra} blocked={blocked} missing={missing}")


def _field_is_valid(key: str, value: object) -> bool:
    if isinstance(value, str) and not value.strip():
        return False
    if key == "business_category":
        return value in {"外燴", "外帶／餐盒", "Candy Bar／甜品桌", "企業長期合作"}
    if key == "event_date":
        return _valid_calendar_date(str(value))
    if key == "event_time":
        return bool(_TIME_RANGE.fullmatch(str(value)))
    if key == "indoor_outdoor":
        return value in {"室內", "戶外"}
    if key == "headcount":
        return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 5000
    if key == "service_format":
        return value in {"現場外燴", "送達擺盤", "自取／外帶"}
    if key in {"venue", "dietary_notes", "logistics"}:
        return isinstance(value, str) and 1 <= len(value.strip()) <= 1000
    return False


def _normalise_field(key: str, value: object) -> object:
    if key == "headcount":
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value
        if isinstance(value, str) and re.fullmatch(r"\d+", value.strip()):
            return int(value.strip())
        return value
    text = str(value).strip()
    if key == "event_time":
        return text.replace("：", ":").replace("~", "-").replace("至", "-").replace("到", "-")
    if key == "service_format" and text in {"自取", "外帶"}:
        return "自取／外帶"
    return text


def _extract_expected_field(key: str, text: str) -> Optional[object]:
    compact = re.sub(r"\s+", "", text)
    lowered = compact.lower()
    if key == "business_category":
        categories = (
            ("企業長期合作", ("長期合作", "企業合作", "固定供應")),
            ("Candy Bar／甜品桌", ("candybar", "甜品桌", "甜點桌")),
            ("外帶／餐盒", ("外帶", "餐盒", "自取")),
            ("外燴", ("外燴",)),
        )
        for label, aliases in categories:
            if any(alias in lowered for alias in aliases):
                return label
    elif key == "event_date":
        match = re.search(r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})", text) or re.search(
            r"(20\d{2})年(\d{1,2})月(\d{1,2})日", text
        )
        if match:
            return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    elif key == "event_time":
        match = re.search(r"(\d{1,2}[:：]\d{2})\s*(?:[-~到至])\s*(\d{1,2}[:：]\d{2})", text)
        if match:
            return f"{match.group(1).replace('：', ':')}-{match.group(2).replace('：', ':')}"
    elif key == "venue":
        match = re.search(r"(?:場地|地址)[:：]?\s*([^。\n]+)", text)
        return match.group(1).strip() if match else text
    elif key == "indoor_outdoor":
        if "室內" in text:
            return "室內"
        if "戶外" in text:
            return "戶外"
    elif key == "headcount":
        match = re.search(r"(\d{1,5})\s*(?:人|位)", text)
        if match:
            return int(match.group(1))
    elif key == "service_format":
        for value in ("現場外燴", "送達擺盤", "自取", "外帶"):
            if value in text:
                return value
    elif key == "dietary_notes":
        if text in {"無", "沒有", "目前沒有"}:
            return "無"
        match = re.search(r"(?:飲食|禁忌|過敏)[:：]\s*(.+)", text)
        return match.group(1).strip() if match else text
    elif key == "logistics":
        return text
    return None


def _valid_calendar_date(value: str) -> bool:
    match = _DATE.fullmatch(value)
    if not match:
        return False
    try:
        date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return False
    return True


def _parse_utc_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid_confirmation_timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("confirmation_timestamp_must_be_utc")
    return parsed.astimezone(timezone.utc)


def _requested_field_count(text: str) -> int:
    groups = (
        r"(?:哪一類|需要的是[^？?]{0,60}還是)",
        r"(?:哪一天|幾月幾日)",
        r"(?:幾點)",
        r"(?:場地[^？?]{0,30}(?:哪裡|名稱|地址)|地址(?:嗎|呢))",
        r"(?:室內還是戶外)",
        r"(?:幾位|幾人|人數(?:多少|嗎|呢))",
        r"(?:希望是[^？?]{0,60}還是|服務形式(?:要|選|希望)[^？?]{0,20}(?:哪|嗎|呢))",
        r"(?:有需要留意的[^？?]{0,50}(?:過敏|素食|宗教|食材)|過敏[^？?]{0,20}(?:嗎|呢))",
        r"(?:搬運[^，。？?]{0,30}(?:嗎|呢)|有沒有需要留意的[^？?]{0,60}(?:樓層|電梯|停車))",
    )
    return sum(bool(re.search(pattern, text)) for pattern in groups)


def _contains_budget_statement(message: str) -> bool:
    return bool(re.search(r"(?:預算|費用|金額)", message))


def _bounded_acknowledgement(message: str) -> str:
    text = message.strip()
    if re.search(r"(?:多少錢|價格|報價|費用|低消)", text):
        return "我先把活動資料整理完整，內容會由 Mina 在資料齊全後確認。"
    if re.search(r"(?:檔期|有空|可以接|能不能接)", text):
        return "日期我先記下，檔期會由 Mina 再確認。"
    if re.search(r"(?:過敏|素食|飲食|忌口|不吃)", text):
        return "飲食需求會依實際限制由團隊確認，我先照您的說明記錄。"
    return "收到，我先幫您整理。"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
