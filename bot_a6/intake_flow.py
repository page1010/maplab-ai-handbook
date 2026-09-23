from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


QUESTION_ORDER = (
    "business_category",
    "event_date",
    "event_time",
    "venue",
    "indoor_outdoor",
    "headcount",
    "service_format",
    "budget",
    "dietary_notes",
    "logistics",
)

FIELD_LABELS = {
    "business_category": "需求業務類別",
    "event_date": "活動日期",
    "event_time": "活動時間",
    "venue": "場地／完整地址",
    "indoor_outdoor": "室內或戶外",
    "headcount": "預計人數",
    "service_format": "服務形式",
    "budget": "預算",
    "dietary_notes": "飲食禁忌／過敏",
    "logistics": "樓層、電梯、停車與搬運條件",
}

QUESTIONS = {
    "business_category": "想先確認您需要哪一類服務：外燴、外帶／餐盒、Candy Bar／甜品桌，還是企業長期合作？",
    "event_date": "活動預計是哪一天？請提供西元年月日。",
    "event_time": "活動預計幾點開始、幾點結束？",
    "venue": "活動場地名稱與完整地址方便提供嗎？",
    "indoor_outdoor": "場地是在室內還是戶外？",
    "headcount": "預計大約幾位參加？",
    "service_format": "希望採現場外燴、送達擺盤，還是自取／外帶？",
    "budget": "這次整體預算大約是多少？",
    "dietary_notes": "賓客是否有過敏、素食、宗教或不吃的食材？若無也請回覆「無」。",
    "logistics": "最後確認搬運條件：樓層、有無電梯、臨停／停車位置，以及現場是否有人協助？",
}

# A quote can be calculated only after these facts are explicit.  Dietary and
# logistics remain required because they can change menu safety and service cost.
QUOTE_REQUIRED_FIELDS = QUESTION_ORDER


@dataclass
class IntakeState:
    fields: dict[str, object] = field(default_factory=dict)

    @property
    def missing_fields(self) -> list[str]:
        return [key for key in QUESTION_ORDER if key not in self.fields]

    @property
    def quote_ready(self) -> bool:
        return not self.missing_fields

    def next_question(self) -> Optional[str]:
        missing = self.missing_fields
        return QUESTIONS[missing[0]] if missing else None

    def quote_request_text(self, case_id: str) -> str:
        if not self.quote_ready:
            labels = "、".join(FIELD_LABELS[key] for key in self.missing_fields)
            raise ValueError(f"quote_not_ready: missing {labels}")
        f = self.fields
        return (
            f"報價 case_id={case_id} {f['business_category']} "
            f"{f['event_date']} {f['event_time']} {f['venue']} {f['indoor_outdoor']} "
            f"{f['headcount']}人 形式:{f['service_format']} 預算{f['budget']} "
            f"飲食:{f['dietary_notes']} 搬運:{f['logistics']}"
        )


def apply_customer_message(state: IntakeState, message: str) -> IntakeState:
    """Extract explicit facts only; never infer commercial commitments."""
    text = message.strip()
    compact = re.sub(r"\s+", "", text)
    fields = dict(state.fields)

    categories = (
        ("企業長期合作", ("長期合作", "企業合作", "固定供應")),
        ("Candy Bar／甜品桌", ("candybar", "甜品桌", "甜點桌", "場佈")),
        ("外帶／餐盒", ("外帶", "餐盒", "自取")),
        ("外燴", ("外燴", "公司活動", "生日", "婚禮", "開幕", "茶會")),
    )
    lowered = compact.lower()
    for label, aliases in categories:
        if any(alias in lowered for alias in aliases):
            fields["business_category"] = label
            break

    date = re.search(r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})", text)
    if not date:
        date = re.search(r"(20\d{2})年(\d{1,2})月(\d{1,2})日", text)
    if date:
        fields["event_date"] = f"{int(date.group(1)):04d}-{int(date.group(2)):02d}-{int(date.group(3)):02d}"

    time_range = re.search(r"(\d{1,2}[:：]\d{2})\s*(?:[-~到至])\s*(\d{1,2}[:：]\d{2})", text)
    if time_range:
        fields["event_time"] = f"{time_range.group(1).replace('：', ':')}-{time_range.group(2).replace('：', ':')}"

    people = _extract_attendee_count(text)
    if people is not None:
        fields["headcount"] = people

    budget = re.search(r"(?:預算|費用|金額)?\s*(\d+(?:\.\d+)?)\s*([萬万kK])", text)
    if budget:
        amount = float(budget.group(1)) * (10000 if budget.group(2) in "萬万" else 1000)
        fields["budget"] = int(amount)
    else:
        budget = re.search(r"(?:預算|費用|金額)\s*(?:約|大約)?\s*(\d{4,7})", text)
        if budget:
            fields["budget"] = int(budget.group(1))

    if "室內" in text:
        fields["indoor_outdoor"] = "室內"
    elif "戶外" in text:
        fields["indoor_outdoor"] = "戶外"

    for value in ("現場外燴", "送達擺盤", "自取", "外帶"):
        if value in text:
            fields["service_format"] = value
            break

    address = re.search(r"(?:場地|地址)[:：]?\s*([^。\n]+)", text)
    if address:
        fields["venue"] = address.group(1).strip()

    if re.search(r"(?:飲食|禁忌|過敏)[:：]", text) or text in {"無", "沒有"}:
        fields["dietary_notes"] = re.sub(r"^.*?(?:飲食|禁忌|過敏)[:：]\s*", "", text) or "無"

    if any(term in text for term in ("樓", "電梯", "停車", "臨停", "搬運")):
        fields["logistics"] = text

    return IntakeState(fields=fields)


def _extract_attendee_count(text: str) -> Optional[int]:
    candidates: list[int] = []
    for match in re.finditer(r"(\d{1,4})\s*(?:人|位)", text):
        window = text[max(0, match.start() - 8):match.end() + 10]
        if any(term in window for term in ("素食", "吃素", "過敏", "工作人員", "服務人員", "協助搬運")):
            continue
        candidates.append(int(match.group(1)))
    return candidates[-1] if candidates else None


def build_training_snapshot(state: IntakeState) -> dict:
    return {
        "fields": state.fields,
        "missing_fields": state.missing_fields,
        "missing_labels": [FIELD_LABELS[key] for key in state.missing_fields],
        "quote_ready": state.quote_ready,
        "next_question": state.next_question(),
    }
