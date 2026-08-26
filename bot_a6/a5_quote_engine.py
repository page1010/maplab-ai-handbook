from __future__ import annotations

import json
import math
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from ai_workbook.openclaw_adapter import OpenClawAdapter
except Exception:  # pragma: no cover - fallback path is tested from runtime.
    OpenClawAdapter = None  # type: ignore[assignment]


DEFAULT_LOCAL_MODEL = os.getenv("A5_LOCAL_MODEL", os.getenv("OPENCLAW_MODEL", "qwen2.5:14b"))
DEFAULT_LOCAL_ENGINE = os.getenv("A5_LOCAL_ENGINE", "auto")
DEFAULT_THINKING = os.getenv("A5_LOCAL_THINKING", "off")
DEFAULT_PROMPT_PROFILE = os.getenv("A5_QUOTE_PROMPT_PROFILE", "telegram")


@dataclass(frozen=True)
class A5QuoteResult:
    answer: str
    engine_used: str
    model_used: str
    fallback_used: bool
    bundle_dir: Optional[str] = None
    error: str = ""


def build_a5_quote_prompt(
    user_message: str,
    user_name: str = "",
    history: Optional[Iterable[dict]] = None,
    runtime: str = "local",
    profile: Optional[str] = None,
) -> str:
    prompt_profile = profile or DEFAULT_PROMPT_PROFILE
    docs = _load_support_docs(prompt_profile)
    parsed_facts = _extract_normalized_facts(user_message)

    if runtime == "openclaw/ollama-fallback":
        items_catalog = _load_items_catalog_for_prompt()
        # Simplified prompt for local model to prevent context collapse
        return f"""你是 MAPLAB A5 報價與提案引擎。
請根據使用者的需求，產出一份 Markdown 報價單草稿，並把最後的 JSON 做到可以交給 GAS 建立 Google Sheet 報價副本。
【極端重要】回覆的最後【絕對必須】附上一組合法的 ```json 區塊，不可只回覆「好的」或單一字元。
【禁止】輸出 Thinking、推理過程、自我對話、模型訓練說明。
【品項規則】
- 優先只能使用下方「MAPLAB 已知品項」裡存在的 standard_name 與成本。
- 不可發明「核心主餐點模擬組合」「基底組」「模擬菜單」這種不存在的品項名稱。
- 如果競品菜單無法精準匹配 MAPLAB 品項，請選最接近的已知品項，並在 internalNote 說明假設。
- 成本為 0、空白、未知的品項不得自動納入報價；只能列入 needsManualCost。
- 若使用者要求「成本*5」「成本乘以 5」，請設定餐點收入 foodRevenue = foodCost * 5，食材成本佔比約 20%，餐點毛利約 80%。
- 若使用者是競品菜單/雷同品項/比照菜單/截圖辨識/毛利試算，請輸出 action=createQuoteVariants。

MAPLAB 已知品項（item_id｜類別｜standard_name｜成本/單位）：
{items_catalog}

範例如下：
```json
{{
  "action": "createQuoteVariants",
  "base": {{
    "clientName": "競品菜單試算",
    "eventName": "雷同品項成本乘以5報價",
    "headcount": 人數數字或空字串,
    "dietaryNotes": "待確認"
  }},
  "variants": [
    {{
      "label": "A",
      "title": "MAPLAB 雷同品項試算",
      "menu": [
        {{"name": "MAPLAB已知品項名稱", "qty": 數量, "unit": "個", "unitCost": 單位成本, "subtotal": 小計成本}}
      ],
      "foodCost": 餐點成本總和,
      "foodRevenue": 餐點成本總和乘以5,
      "totalCost": 總成本,
      "totalRevenue": 總成本乘以5,
      "internalNote": "列出競品原品項與 MAPLAB 替代假設；成本未知者列 needsManualCost"
    }}
  ],
  "needsManualCost": [
    {{"sourceItem": "競品原品項", "reason": "找不到足夠接近且有成本的 MAPLAB 品項"}}
  ]
}}
```

使用者的需求：
{user_message.strip()}

開始產出草稿與 JSON："""

    sections = [
        "# MAPLAB A5 Quote Runtime",
        "",
        f"- runtime: {runtime}",
        f"- requester: {user_name or 'Owner'}",
        f"- generated_at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Identity",
        "你是 MAPLAB A5 報價與提案引擎部。你負責菜單品項資料庫、成本/毛利邏輯、報價公式、活動模板、報價草稿生成。",
        "你正在協助 Owner 或業務整理內部報價草稿，不是直接對客戶發送正式報價。",
        "",
        "## Operating rules",
        "- 先產出可用草稿，不因為缺少日期、地點或預算而卡住；缺資料時列為待確認。",
        "- 不得自行改 Google Sheets、Items 主表、GAS、Drive、WordPress 或正式 truth source。",
        "- 不得揭露內部成本給客戶；但可以在內部草稿中標示估算成本與毛利風險。",
        "- 報價判斷必須分開寫：餐點毛利 / 食材成本佔比，以及整體毛利；餐點安全線以食材成本不超過餐點收入 20% 為優先。",
        "- 客戶指定的價格級距只是詢價條件，不等於 A5 已核准承接價；若指定價格低於毛利安全線，必須先說明限制，提供「升價保留內容」或「精簡菜單守毛利」兩條路，不得默默犧牲毛利。",
        "- 如果使用者只是說「第一版 / 毛利太低 / 調高一點」但近期上下文沒有明確案件或報價連結，不要沿用舊測試案，請先要求指定案件或報價單。",
        "- 不猜不存在的報價單 URL；如果沒有外部寫入，就明確說這是本地草稿。",
        "- 如果本地模型信心不足，最後輸出一段可交給其他模型或 A5 雲端引擎的 handoff prompt。",
        "",
        "## Response contract",
        "請用繁體中文 Markdown，控制在手機可讀長度。輸出固定包含：",
        "1. `A5 報價草稿`：案件摘要、缺漏資訊、建議方案。",
        "2. `建議菜單`：依類別列出品項與數量，優先用已知 MAPLAB 品項。",
        "3. `金額判斷`：建議報價、車馬/服務/搬運假設、餐點毛利/食材成本佔比、整體毛利。",
        "4. `業務下一步`：要問客戶或 Owner 的 3-5 件事。",
        "5. `GAS 觸發 JSON`：最後【必須】以 ```json 包裹一段供 Google Sheet 解析的 JSON 資料。範例如下：",
        "```json",
        "{",
        "  \"action\": \"createQuote\",",
        "  \"clientName\": \"客戶名稱\",",
        "  \"eventType\": \"活動類型\",",
        "  \"headcount\": 人數數字,",
        "  \"budget\": 預算數字,",
        "  \"items\": [",
        "    {\"name\": \"品項1\", \"quantity\": 數量},",
        "    {\"name\": \"品項2\", \"quantity\": 數量}",
        "  ]",
        "}",
        "```",
        "若資訊不足，請補齊預設值或留空，但務必輸出此 JSON 區塊。",
        "",
        "## Deterministic parsing hints",
        "以下是進模型前的硬解析提示。若與模型自行推測衝突，優先採用本段，尤其是中文金額單位。",
        parsed_facts,
        "",
        "## Support docs",
        f"(profile: {prompt_profile})",
    ]
    for path, content in docs.items():
        sections.extend([f"### {path}", content, ""])

    if history:
        sections.append("## Recent conversation")
        history_limit = 8 if prompt_profile == "full" else 3
        content_limit = 900 if prompt_profile == "full" else 300
        for msg in list(history)[-history_limit:]:
            role = "使用者" if msg.get("role") == "user" else "助理"
            content = str(msg.get("content", "")).strip()
            if content:
                sections.append(f"{role}: {content[:content_limit]}")
        sections.append("")

    sections.extend(
        [
            "## User request",
            "```text",
            user_message.strip(),
            "```",
            "",
            "【極端重要】你的回覆必須是完整的 Markdown 報價單草稿，並且在最後【絕對必須】附上一組合法的 ```json 區塊，不可只回覆「好的」。請立即開始產出草稿與 JSON：",
        ]
    )
    return "\n".join(sections)


def _extract_normalized_facts(user_message: str) -> str:
    lines: list[str] = [
        "- 中文金額單位：1萬 = 10,000；5萬 = 50,000；不要把 5萬 展成 500,000。"
    ]
    budget = _find_budget(user_message)
    if budget:
        lines.append(f"- 偵測預算：NT${budget[0]:,}（來源：{budget[1]}）")
    people = re.findall(r"(\d{1,4})\s*(?:人|位)", user_message)
    if people:
        lines.append(f"- 偵測人數：{people[-1]} 人")
    restrictions = _find_restrictions(user_message)
    if restrictions:
        lines.append(f"- 偵測飲食禁忌：{'; '.join(restrictions)}")
    return "\n".join(lines)


def _find_restrictions(user_message: str) -> list[str]:
    patterns = [
        (r"(?:不吃|不要|無|不能有)\s*牛", "不可含牛肉"),
        (r"(?:不吃|不要|無|不能有)\s*海鮮", "不可含海鮮"),
        (r"(?:不吃|不要|無|不能有)\s*酒", "不可含酒精"),
        (r"素食|吃素|蔬食", "需要素食或蔬食選項"),
        (r"堅果.*過敏|過敏.*堅果", "堅果過敏，需做硬性排除與交叉污染確認"),
    ]
    return [label for pattern, label in patterns if re.search(pattern, user_message)]


def _find_budget(user_message: str) -> Optional[tuple[int, str]]:
    budget_patterns = [
        r"(?:預算|budget|費用|金額)\s*(?:約|大約|around)?\s*(\d+(?:\.\d+)?)\s*([萬万kK]?)",
        r"(\d+(?:\.\d+)?)\s*([萬万kK])\s*(?:預算|budget|費用|金額)?",
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, user_message, flags=re.IGNORECASE)
        if not match:
            continue
        raw_number = match.group(1)
        unit = match.group(2) or ""
        amount = float(raw_number)
        if unit in {"萬", "万"}:
            amount *= 10000
        elif unit in {"k", "K"}:
            amount *= 1000
        return int(amount), match.group(0).strip()
    return None


def _load_items_records() -> list[dict]:
    path = ROOT / "data/items_master.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"items catalog unavailable: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError("items catalog is not a list")
    return [record for record in data if isinstance(record, dict)]


def _load_items_catalog_for_prompt(limit: int = 140) -> str:
    try:
        records = _load_items_records()
    except Exception as exc:
        return f"(items catalog unavailable: {exc})"

    rows: list[str] = []
    skipped_zero: list[str] = []
    for record in records:
        name = str(record.get("standard_name", "")).strip()
        if not name:
            continue
        raw_cost = str(record.get("default_cost", "")).strip()
        try:
            cost = float(raw_cost)
        except ValueError:
            cost = 0
        if cost <= 0:
            skipped_zero.append(name)
            continue
        cost_text = str(int(cost)) if cost.is_integer() else str(cost)
        rows.append(
            "｜".join(
                [
                    str(record.get("item_id", "")).strip(),
                    str(record.get("category", "")).strip() or "未分類",
                    name,
                    f"{cost_text}/{str(record.get('unit', '')).strip() or '份'}",
                ]
            )
        )
        if len(rows) >= limit:
            break

    if skipped_zero:
        rows.append(
            "成本未知不可自動報價｜"
            + "、".join(skipped_zero[:12])
            + ("..." if len(skipped_zero) > 12 else "")
        )
    return "\n".join(rows) if rows else "(no priced items found)"


def _first_json_object(answer: str) -> Optional[dict]:
    match = re.search(r"```json\s*(\{.*?\})\s*```", answer, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _ensure_required_json(answer: str, user_message: str) -> str:
    if _first_json_object(answer):
        return answer

    payload = build_sheet_quote_payload(user_message)
    if not payload:
        return answer

    variant = payload["variants"][0]
    menu_rows = [
        f"- {item['name']}：{item.get('qtyText') or str(item['qty']) + item.get('unit', '')}，"
        f"成本 NT${item['subtotal']:,.0f}"
        for item in variant["menu"]
    ]
    manual_rows = [
        f"- {item['sourceItem']}：{item['reason']}"
        for item in payload.get("needsManualCost", [])
    ]
    draft = [
        "## A5 報價草稿",
        "地端模型未輸出可直接建 Sheet 的合法 JSON，已改用 MAPLAB 品項表與成本規則產出結構化試算。",
        "",
        "### 建議雷同品項",
        *menu_rows,
        "",
        "### 金額判斷",
        f"- 食材/餐點成本小計：NT${variant['foodCost']:,.0f}",
        f"- 成本乘以 5 報價：NT${variant['foodRevenue']:,.0f}",
        "- 對應食材成本佔比：約 20%；餐點毛利：約 80%。",
        "",
        "### 待人工確認",
        *(manual_rows or ["- 無"]),
        "",
        "```json",
        json.dumps(payload, ensure_ascii=False, indent=2),
        "```",
    ]
    return "\n".join(draft)


def build_sheet_quote_payload(user_message: str, user_name: str = "") -> Optional[dict]:
    """Build a deterministic GAS payload when the request is concrete enough.

    This is the A6 hot-path guard: Telegram quote completion must not depend on
    a local model producing perfect JSON.
    """
    competitor_payload = _build_competitor_quote_payload(user_message)
    if competitor_payload:
        return competitor_payload
    return _build_basic_high_margin_quote_payload(user_message, user_name=user_name)


def _build_basic_high_margin_quote_payload(user_message: str, user_name: str = "") -> Optional[dict]:
    compact = re.sub(r"\s+", "", user_message)
    trigger_terms = (
        "報價",
        "菜單",
        "外燴",
        "正餐",
        "主食",
        "高毛利",
        "毛利",
        "英文菜單",
        "一麵一飯",
        "肉丸",
        "鬆餅雞球",
        "生日",
        "派對",
    )
    if not any(term in compact for term in trigger_terms):
        return None

    headcount = _extract_headcount(user_message)
    if not headcount:
        return None

    try:
        records = _load_items_records()
    except Exception:
        return None
    by_name = {str(record.get("standard_name", "")).strip(): record for record in records}

    menu_specs = _basic_high_margin_menu_specs(headcount, compact)
    menu: list[dict] = []
    for name, qty, qty_text, note in menu_specs:
        row = _quote_menu_row(by_name, name, qty, qty_text, note)
        if not row:
            return None
        menu.append(row)

    food_cost = round(sum(float(item["subtotal"]) for item in menu), 2)
    total_revenue = _round_up(food_cost * 5, 100)
    event_date, event_date_note = _extract_event_date_for_payload(user_message)
    event_time = _extract_event_time(user_message)
    client_name = _extract_client_name(user_message, user_name)
    event_type = "生日派對" if any(term in compact for term in ("生日", "birthday", "Birthday")) else "外燴正餐"
    event_name = f"{headcount}人{event_type}高毛利正餐"
    tracking = _extract_quote_tracking_fields(user_message)

    notes = [
        "A6 deterministic Sheet-first payload；品項皆取自 Items standard_name。",
        "含甜點與飲品共 10 道。",
        event_date_note,
    ]
    if "英文" in compact or "english" in compact.lower():
        notes.append("可能需英文版；急件確認後需 50% 訂金。")
    if any(term in compact for term in ("桌面", "餐檯", "桌上")):
        notes.append("服務範圍以桌面餐檯佈置為準。")

    variant_title = "基本版高毛利正餐 10 道"
    return {
        "action": "createQuoteVariants",
        "base": {
            "caseId": tracking["case_id"],
            "clientName": client_name,
            "customer": client_name,
            "eventDate": event_date,
            "date": event_date,
            "time": event_time,
            "eventType": event_type,
            "eventName": event_name,
            "headcount": headcount,
            "pax": headcount,
            "budget": tracking["budget"],
            "venue": tracking["venue"],
            "indoorOutdoor": tracking["indoor_outdoor"],
            "serviceFormat": tracking["service_format"],
            "totalItems": len(menu),
            "depositAmount": int(total_revenue * 0.5),
            "dietaryNotes": "｜".join(notes),
        },
        "variants": [
            {
                "label": "A",
                "title": variant_title,
                "totalItems": len(menu),
                "positioning": "15 人左右正餐桌面餐檯，高毛利基本版。",
                "menu": menu,
                "foodCost": food_cost,
                "foodRevenue": total_revenue,
                "totalCost": food_cost,
                "totalRevenue": total_revenue,
                "foodNote": "totalRevenue 依 foodCost * 5 後百元進位；食材成本佔比約 20%。",
                "decorNote": "桌面餐檯佈置。",
                "internalNote": "；".join(notes),
            }
        ],
        "needsManualCost": [],
    }


def _extract_quote_tracking_fields(user_message: str) -> dict[str, object]:
    def value_after(label: str) -> str:
        match = re.search(rf"{label}[:=]([^\s]+)", user_message)
        return match.group(1).strip() if match else ""

    case_match = re.search(r"case_id=([A-Za-z0-9._:-]+)", user_message)
    budget = _find_budget(user_message)
    venue_match = re.search(
        r"\d{1,2}[:：]\d{2}\s*[-~到至]\s*\d{1,2}[:：]\d{2}\s+(.+?)\s+(?:室內|戶外)\s+\d{1,4}人",
        user_message,
    )
    indoor_match = re.search(r"\b(室內|戶外)\b", user_message)
    return {
        "case_id": case_match.group(1) if case_match else "",
        "budget": budget[0] if budget else "",
        "venue": venue_match.group(1).strip() if venue_match else "",
        "indoor_outdoor": indoor_match.group(1) if indoor_match else "",
        "service_format": value_after("形式"),
    }


def _basic_high_margin_menu_specs(headcount: int, compact: str) -> list[tuple[str, float, str, str]]:
    # Current A5 basic high-margin dinner set: one noodle, one rice, one meatball,
    # one waffle chicken ball, four desserts, two drinks.
    return [
        ("義式經典拿波里肉醬義大利麵", 1, "1鍋", "一麵"),
        ("鍋炒台南七股虱目魚香腸炒飯", 1, "1份", "一飯"),
        ("義大利嫩煎香料豚肉球", headcount, f"{headcount}個", "肉丸"),
        ("澳式雞球迷你鬆餅", headcount, f"{headcount}份", "鬆餅雞球"),
        ("手工焦糖烤布丁", headcount, f"{headcount}份", "甜點"),
        ("卡士達香緹手工小泡芙", headcount, f"{headcount}個", "甜點"),
        ("葡式酥皮蛋塔", headcount, f"{headcount}個", "甜點"),
        ("布朗尼切小正方/25", headcount, f"{headcount}片", "甜點"),
        ("冷泡冰釀烏龍茶_無糖", 1, "1桶", "飲品"),
        ("阿薩姆紅茶", 1, "1桶", "飲品"),
    ]


def _quote_menu_row(
    by_name: dict[str, dict],
    name: str,
    qty: float,
    qty_text: str,
    note: str,
) -> Optional[dict]:
    record = by_name.get(name)
    if not record:
        return None
    unit_cost = _numeric_cost(record.get("default_cost"))
    if unit_cost <= 0:
        return None
    subtotal = round(float(qty) * unit_cost, 2)
    return {
        "sourceItem": note,
        "itemId": str(record.get("item_id", "")).strip(),
        "name": name,
        "qty": qty,
        "unit": str(record.get("unit", "")).strip() or "份",
        "qtyText": qty_text,
        "unitCost": unit_cost,
        "subtotal": subtotal,
        "matchNote": "A6 deterministic basic set",
    }


def _extract_headcount(user_message: str) -> Optional[int]:
    patterns = [
        r"(\d{1,4})\s*(?:人|位)",
        r"(?:estimated\s+number\s+of|number\s+of|headcount|pax)\s*[:：]?\s*(\d{1,4})",
    ]
    for pattern in patterns:
        matches = []
        for match in re.finditer(pattern, user_message, flags=re.IGNORECASE):
            window = user_message[max(0, match.start() - 8):match.end() + 10]
            if any(term in window for term in ("素食", "吃素", "過敏", "工作人員", "服務人員", "協助搬運")):
                continue
            matches.append(match.group(1))
        if matches:
            try:
                return int(matches[-1])
            except (TypeError, ValueError):
                continue
    return None


def _extract_event_time(user_message: str) -> str:
    match = re.search(r"(\d{1,2})[:：](\d{2})", user_message)
    if match:
        return f"{int(match.group(1)):02d}:{match.group(2)}"
    match = re.search(r"\b(\d{1,2})\s*(am|pm)\b", user_message, flags=re.IGNORECASE)
    if match:
        hour = int(match.group(1))
        suffix = match.group(2).lower()
        if suffix == "pm" and hour < 12:
            hour += 12
        if suffix == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:00"
    return ""


def _extract_client_name(user_message: str, user_name: str = "") -> str:
    match = re.search(r"(?:報價|估價|新報價)\s+([^\s，,。]+)", user_message)
    if match:
        candidate = match.group(1).strip()
        if not re.match(r"^\d", candidate) and candidate not in {"一下", "這個", "客人", "她", "他"}:
            return candidate[:30]
    if user_name and user_name not in {"業務", "Owner"}:
        return f"{user_name}_Telegram報價"
    return "Telegram報價試算"


def _round_up(value: float, step: int) -> int:
    if value <= 0:
        return 0
    return int(math.ceil(value / step) * step)


def _build_competitor_quote_payload(user_message: str) -> Optional[dict]:
    compact = re.sub(r"\s+", "", user_message)
    trigger_terms = ("競品", "競爭對手", "雷同", "比照", "成本*5", "成本乘以5", "成本總價*5", "試算表")
    if not any(term in compact for term in trigger_terms):
        return None

    try:
        records = _load_items_records()
    except Exception:
        return None
    by_id = {str(record.get("item_id", "")).strip(): record for record in records}

    mappings = [
        (("BBQ手撕豬小漢堡", "手撕豬小漢堡", "手撕豬"), "APP014", "以手撕豬普切塔替代迷你漢堡型態。"),
        (("洋蔥燻雞三明治", "燻雞三明治", "燻雞"), "APP011", "以青醬雞肉乳酪三明治替代燻雞三明治。"),
        (("蛋沙拉小可頌", "蛋沙拉", "小可頌"), "APP030", "以日式蛋沙拉小漢堡替代蛋沙拉可頌。"),
        (("櫻桃鴨胸串", "鴨胸串", "鴨胸"), "APP003", "以燻鵝胸葡萄小串替代鴨胸串。"),
        (("烤雞腿排與烤蔬菜盤", "烤雞腿排", "雞腿排"), "MAIN007", "以招牌義式炸雞腿估算雞腿主盤成本，烤蔬菜需人工確認。"),
        (("義大利麵", "白酒蛤蜊", "白酒蛤蠣"), "MAIN005", "以蒜香白酒蛤蠣義大利麵作為義大利麵基準盤。"),
        (("水果迷你小塔", "迷你小塔", "水果小塔"), "DST021", "以覆盆子小塔估算水果迷你小塔。"),
        (("季節水果馬卡龍", "馬卡龍"), "DST039", "以馬卡龍派對品項換算單顆成本。"),
        (("卡士達迷你泡芙", "迷你泡芙", "泡芙"), "DST017", "以卡士達香緹手工小泡芙估算。"),
        (("水果焦糖布丁", "焦糖布丁", "布丁"), "DST011", "以法式焦糖烤布丁估算，水果裝飾需確認。"),
        (("蜂蜜檸檬飲", "檸檬飲"), "BEV006", "以檸檬紅茶桶裝成本暫估蜂蜜檸檬飲。"),
        (("英式伯爵茶", "伯爵茶"), "BEV007", "以阿薩姆紅茶桶裝成本暫估伯爵茶。"),
    ]
    manual_patterns = [
        ("甜甜圈蛋糕", "items_master 內甜甜圈架成本為 0，不能自動報價。"),
        ("烤蔬菜盤", "目前以雞腿主盤估算，蔬菜盤成本需人工補價。"),
    ]

    menu: list[dict] = []
    notes: list[str] = []
    used_source_terms: set[str] = set()
    for aliases, item_id, note in mappings:
        source_term = next((alias for alias in aliases if alias in compact), "")
        if not source_term or source_term in used_source_terms:
            continue
        record = by_id.get(item_id)
        if not record:
            continue
        cost = _numeric_cost(record.get("default_cost"))
        if cost <= 0:
            continue
        qty, unit, qty_text = _extract_menu_quantity(compact, aliases)
        unit_cost = _effective_unit_cost(cost, str(record.get("unit", "")), unit)
        subtotal = round(qty * unit_cost, 2)
        menu.append(
            {
                "sourceItem": source_term,
                "itemId": item_id,
                "name": str(record.get("standard_name", "")).strip(),
                "qty": qty,
                "unit": unit,
                "qtyText": qty_text,
                "unitCost": unit_cost,
                "subtotal": subtotal,
                "matchNote": note,
            }
        )
        notes.append(f"{source_term}->{record.get('standard_name')}：{note}")
        used_source_terms.add(source_term)

    if not menu:
        return None

    event_date, event_date_note = _extract_event_date_for_payload(user_message)
    needs_manual_cost = [
        {"sourceItem": source, "reason": reason}
        for source, reason in manual_patterns
        if source in compact
    ]
    food_cost = round(sum(float(item["subtotal"]) for item in menu), 2)
    food_revenue = round(food_cost * 5, 2)
    title = "MAPLAB 雷同品項成本乘以5試算"
    return {
        "action": "createQuoteVariants",
        "base": {
            "clientName": "競品菜單試算",
            "eventDate": event_date,
            "date": event_date,
            "eventName": title,
            "dietaryNotes": f"競品菜單 OCR 轉換；{event_date_note}；正式報價前需人工確認成本未知品項。",
        },
        "variants": [
            {
                "label": "A",
                "title": title,
                "positioning": "比照競品菜單，以 MAPLAB 近似品項估算。",
                "menu": menu[:12],
                "foodCost": food_cost,
                "foodRevenue": food_revenue,
                "totalCost": food_cost,
                "totalRevenue": food_revenue,
                "foodNote": "foodRevenue = foodCost * 5；食材成本佔比約 20%。",
                "internalNote": "；".join(notes + [item["reason"] for item in needs_manual_cost]),
            }
        ],
        "needsManualCost": needs_manual_cost,
    }


def _extract_event_date_for_payload(user_message: str) -> tuple[str, str]:
    patterns = [
        (r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})", 0, "使用訊息中的西元活動日期"),
        (r"(20\d{2})年(\d{1,2})月(\d{1,2})日", 0, "使用訊息中的中文西元活動日期"),
        (r"(?<!\d)(1\d{2})[/-](\d{1,2})[/-](\d{1,2})(?!\d)", 1911, "使用訊息中的民國活動日期"),
    ]
    for pattern, year_offset, note in patterns:
        match = re.search(pattern, user_message)
        if not match:
            continue
        year = int(match.group(1)) + year_offset
        month = int(match.group(2))
        day = int(match.group(3))
        try:
            event_date = datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            continue
        return event_date, note

    match = re.search(r"(?<!\d)(\d{1,2})[/-](\d{1,2})(?!\d)", user_message)
    if match:
        year = datetime.now().year
        month = int(match.group(1))
        day = int(match.group(2))
        try:
            event_date = datetime(year, month, day).strftime("%Y-%m-%d")
            return event_date, "使用訊息中的月日並以今年補齊年份"
        except ValueError:
            pass

    return datetime.now().strftime("%Y-%m-%d"), "未提供活動日期，eventDate 暫填試算日而非正式活動日"


def _numeric_cost(value: object) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


def _extract_menu_quantity(text: str, aliases: tuple[str, ...]) -> tuple[float, str, str]:
    for alias in aliases:
        index = text.find(alias)
        if index < 0:
            continue
        window = text[index:index + 36]
        match = re.search(r"(\d+(?:\.\d+)?)\s*(個|份|盤|組|桶|杯|公升|L|l)?", window)
        if match:
            qty = float(match.group(1))
            unit = match.group(2) or "份"
            if unit in {"公升", "L", "l"}:
                return 1.0, "桶", f"{qty:g}公升"
            return qty, unit, f"{qty:g}{unit}"
        if "四公升" in window:
            return 1.0, "桶", "4公升"
    return 1.0, "份", "1份"


def _effective_unit_cost(cost: float, catalog_unit: str, requested_unit: str) -> float:
    unit = catalog_unit.strip()
    match = re.match(r"^(\d+(?:\.\d+)?)(個|份|杯|片)$", unit)
    if match and requested_unit in {"個", "份", "杯", "片"}:
        pack_qty = float(match.group(1))
        if pack_qty > 0:
            return round(cost / pack_qty, 2)
    return cost


def _apply_deterministic_corrections(answer: str, user_message: str) -> str:
    answer = _sanitize_model_output(answer)
    budget = _find_budget(user_message)
    if not budget:
        return _ensure_required_json(answer, user_message)
    amount, source = budget
    normalized = f"NT${amount:,}"
    corrected_lines: list[str] = []
    changed = False
    for line in answer.splitlines():
        if "預算" in line and "NT$" in line:
            new_line = re.sub(r"NT\$[\d,]+", normalized, line, count=1)
            changed = changed or new_line != line
            corrected_lines.append(new_line)
        else:
            corrected_lines.append(line)
    note = f"> 金額校正：使用者預算解析為 {normalized}（來源：{source}；萬=10,000）。"
    corrected = "\n".join(corrected_lines).strip()
    if changed or note not in corrected:
        corrected = note + "\n\n" + corrected
    return _ensure_required_json(corrected, user_message)


def _sanitize_model_output(answer: str) -> str:
    answer = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", answer)
    answer = re.sub(r"(?is)<think>.*?</think>", "", answer)
    answer = answer.replace("\r", "").strip()
    lines = answer.splitlines()
    if lines and lines[0].strip().lower().startswith("thinking"):
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("```json"):
                answer = "\n".join(lines[index:]).strip()
                break
        else:
            answer = ""
    return answer


def run_a5_local_quote(
    user_message: str,
    user_name: str = "",
    history: Optional[Iterable[dict]] = None,
    job_id: Optional[str] = None,
    engine: Optional[str] = None,
    model: Optional[str] = None,
) -> A5QuoteResult:
    job = job_id or _new_job_id("A5-QUOTE")
    prompt = build_a5_quote_prompt(
        user_message=user_message,
        user_name=user_name,
        history=history,
        runtime="openclaw/ollama-fallback",
    )
    requested_engine = engine or DEFAULT_LOCAL_ENGINE
    requested_model = model or DEFAULT_LOCAL_MODEL

    if OpenClawAdapter is not None:
        try:
            adapter = OpenClawAdapter(default_model=requested_model)
            result = adapter.run_local_task(
                job_id=job,
                prompt=prompt,
                model=requested_model,
                engine=requested_engine,
                thinking=DEFAULT_THINKING,
            )
            draft_path = Path(str(result["draft_md"]))
            raw_answer = draft_path.read_text(encoding="utf-8").strip()
            answer = _apply_deterministic_corrections(
                raw_answer,
                user_message,
            )
            if answer != raw_answer:
                draft_path.write_text(answer + "\n", encoding="utf-8")
            return A5QuoteResult(
                answer=_append_local_footer(answer, result),
                engine_used=str(result.get("engine_used", requested_engine)),
                model_used=str(result.get("model_used", requested_model)),
                fallback_used=bool(result.get("fallback_used", False)),
                bundle_dir=str(result.get("bundle_dir", "")) or None,
            )
        except Exception as exc:
            direct = _run_direct_ollama(prompt, requested_model)
            direct = _apply_deterministic_corrections(direct, user_message)
            return A5QuoteResult(
                answer=_append_direct_footer(direct, job, str(exc)),
                engine_used="ollama-direct",
                model_used=requested_model,
                fallback_used=True,
                bundle_dir=None,
                error=str(exc),
            )

    direct = _run_direct_ollama(prompt, requested_model)
    direct = _apply_deterministic_corrections(direct, user_message)
    return A5QuoteResult(
        answer=_append_direct_footer(direct, job, "OpenClawAdapter unavailable"),
        engine_used="ollama-direct",
        model_used=requested_model,
        fallback_used=True,
        bundle_dir=None,
        error="OpenClawAdapter unavailable",
    )


def _run_direct_ollama(prompt: str, model: str) -> str:
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "num_ctx": int(os.getenv("A5_LOCAL_NUM_CTX", "8192")),
                "num_predict": int(os.getenv("A5_LOCAL_NUM_PREDICT", "1500")),
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
        return data.get("message", {}).get("content", "")


def _load_support_docs(profile: str = "telegram") -> dict[str, str]:
    if profile == "full":
        files = {
            "recalls/A5_recall.md": 120,
            "handoff/tasks/T-A5-002.md": 180,
            "handoff/tasks/T-A5-004.md": 120,
            "handoff/tasks/T-A5-005.md": 90,
            "skills/a6-rapid-quote-sop.md": 230,
            "data/quote-terms-reference.md": 120,
            "archive/data/item-frequency-top50.md": 120,
            "archive/data/item-master-cross-reference.md": 160,
        }
    else:
        files = {
            "recalls/A5_recall.md": 25,
            "handoff/tasks/T-A5-002.md": 25,
            "handoff/tasks/T-A5-004.md": 8,
            "handoff/tasks/T-A5-005.md": 8,
            "skills/a6-rapid-quote-sop.md": 35,
            "data/quote-terms-reference.md": 25,
            "archive/data/item-frequency-top50.md": 35,
            "archive/data/item-master-cross-reference.md": 35,
        }
    return {path: _read_doc(ROOT / path, max_lines) for path, max_lines in files.items()}


def _read_doc(path: Path, max_lines: int) -> str:
    try:
        lines = path.read_text(encoding="utf-8").strip().splitlines()
    except Exception:
        return f"(missing: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path})"
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["", f"... ({len(lines) - max_lines} more lines omitted)"]
    return "\n".join(lines)


def _new_job_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def _append_local_footer(answer: str, result: dict) -> str:
    bundle_dir = result.get("bundle_dir", "")
    footer = [
        "",
        "---",
        f"本地備援：engine={result.get('engine_used')} model={result.get('model_used')} fallback={result.get('fallback_used')}",
    ]
    if bundle_dir:
        footer.append(f"review bundle: `{bundle_dir}`")
    return answer.rstrip() + "\n" + "\n".join(footer)


def _append_direct_footer(answer: str, job_id: str, reason: str) -> str:
    return (
        answer.rstrip()
        + "\n\n---\n"
        + f"本地備援：engine=ollama-direct job_id={job_id}\n"
        + f"fallback reason: {reason}"
    )
