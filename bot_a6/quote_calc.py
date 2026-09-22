#!/usr/bin/env python3
"""報價試算器(hermes 的算術層,零 LLM)。

存在理由(Owner msg 5774,2026-09-22):「快救起來,我才能報價,理論上沒人有額度上班時
他要能幫我」。a6 走免費鏈,Fable5/Opus 沒額度時他是唯一還在班上的。但 hermes 的紅線
第一條是「絕不編價」——所以數字不能由模型生,必須由這支程式從有 source 的價目表算出來。

分工:模型只負責問清需求與排版,毛利率/件數/每人件數/改單差額全部由這裡算。
價目與成本的 source 在 quote_price_book.json,沒有 source 的品項一律回「需人工」。
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PRICE_BOOK_PATH = Path(__file__).resolve().parent / "quote_price_book.json"

# 這三題是小肚肚案與 2026-09-21 東南亞案共同踩出來的:少問一題,整張報價就得重做。
REQUIRED_FACTS = (
    ("pax", "人數(幾位客人)"),
    ("budget", "預算或每人預算"),
    ("event_date", "活動日期(鹹派要 7 天前、菜單建議 10-15 天前預訂)"),
)


class QuoteError(ValueError):
    """需人工介入:資料不足或品項不在價目表。"""


def load_price_book(path: Path | None = None) -> dict:
    return json.loads((path or PRICE_BOOK_PATH).read_text(encoding="utf-8"))


def _index(book: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for line in book["menu_lines"]:
        index[line["key"]] = line
        for alias in line.get("aliases", ()):
            index[alias] = line
    return index


def lookup(name: str, book: dict | None = None) -> dict:
    book = book or load_price_book()
    index = _index(book)
    if name in index:
        return index[name]
    # 只做保守的包含式比對,不做模糊猜測——猜錯等於編價。
    hits = [line for key, line in index.items() if name and (name in key or key in name)]
    unique = {line["key"]: line for line in hits}
    if len(unique) == 1:
        return next(iter(unique.values()))
    raise QuoteError(f"品項「{name}」不在價目表(或對到多個),需人工確認後才可報價")


def _unit_cost(line: dict) -> float:
    """一個單位(組/張/份/個)的食材成本。

    有 cost_per_unit 就以它為準。Owner msg 5800 定的「三明治成本＝外帶售價的 50%」是
    按單位下的規則,先除成每件再乘回去會有除不盡的誤差(400÷12=33.333…),
    所以規則型成本一律存單位成本,每件成本只當顯示值。
    """
    if line.get("cost_per_unit") is not None:
        return float(line["cost_per_unit"])
    return float(line["cost_per_piece"]) * line["pieces_per_unit"]


def _cost_per_piece(line: dict) -> float:
    return _unit_cost(line) / line["pieces_per_unit"]


def margin_table(book: dict | None = None) -> list[dict]:
    """逐品項毛利率,由高到低。這張表就是「80% 做不做得到」的答案來源。"""
    book = book or load_price_book()
    rows = []
    for line in book["menu_lines"]:
        price_per_piece = line["price"] / line["pieces_per_unit"]
        cost_per_piece = _cost_per_piece(line)
        rows.append(
            {
                "key": line["key"],
                "unit": line["unit"],
                "pieces_per_unit": line["pieces_per_unit"],
                "price_per_unit": line["price"],
                "price_per_piece": round(price_per_piece, 2),
                "cost_per_piece": round(cost_per_piece, 2),
                "margin_rate": round(1 - cost_per_piece / price_per_piece, 4),
                "estimated": bool(line.get("price_estimated") or line.get("cost_estimated")),
            }
        )
    return sorted(rows, key=lambda row: row["margin_rate"], reverse=True)


def menu_sum_ceiling(book: dict | None = None) -> dict:
    """照菜單價逐項加總時的毛利率天花板=最高毛利那一項的毛利率。

    Owner msg 5771 問「毛利必須高於 80%」,答案是數學事實而不是方案:逐項加總達不到,
    砍件數也不會改變比率(收入與成本等比降)。這支函式讓 hermes 講得出同一個事實。
    """
    rows = margin_table(book)
    best = rows[0]
    return {
        "ceiling_rate": best["margin_rate"],
        "ceiling_item": best["key"],
        "note": "逐項加總的毛利率天花板;砍件數不會改變毛利率,要更高只能改用整案價法",
    }


def plan_by_items(items: list[tuple[str, int]], *, package_price: float | None = None, pax: int | None = None, book: dict | None = None) -> dict:
    """給定「品項 × 單位數」算成本、件數、毛利。

    package_price=None 時走「菜單價加總」;給了數字就走「整案價」(外燴含服務/佈置/運送/人力)。
    """
    book = book or load_price_book()
    lines = []
    total_cost = 0.0
    total_menu_price = 0.0
    total_pieces = 0
    estimated_keys = []
    for name, units in items:
        if units <= 0:
            raise QuoteError(f"品項「{name}」的數量必須大於 0")
        line = lookup(name, book)
        pieces = line["pieces_per_unit"] * units
        cost = _unit_cost(line) * units
        menu_price = line["price"] * units
        total_cost += cost
        total_menu_price += menu_price
        total_pieces += pieces
        if line.get("price_estimated") or line.get("cost_estimated"):
            estimated_keys.append(line["key"])
        lines.append(
            {
                "key": line["key"],
                "units": units,
                "unit": line["unit"],
                "pieces": pieces,
                "menu_price": round(menu_price, 2),
                "cost": round(cost, 2),
            }
        )

    revenue = float(package_price) if package_price is not None else total_menu_price
    if revenue <= 0:
        raise QuoteError("售價必須大於 0")
    result = {
        "mode": "整案價" if package_price is not None else "菜單價加總",
        "lines": lines,
        "revenue": round(revenue, 2),
        "menu_price_sum": round(total_menu_price, 2),
        "food_cost": round(total_cost, 2),
        "gross_profit": round(revenue - total_cost, 2),
        "margin_rate": round(1 - total_cost / revenue, 4),
        "pieces": total_pieces,
        "estimated_items": sorted(set(estimated_keys)),
        "warnings": [],
    }
    if pax:
        result["pax"] = pax
        result["pieces_per_pax"] = round(total_pieces / pax, 2)
        if result["pieces_per_pax"] < 3:
            result["warnings"].append(
                f"每人 {result['pieces_per_pax']} 件屬輕食小點,不取代正餐,必須先與客人定位清楚"
            )
    if package_price is not None and total_menu_price > 0:
        multiple = revenue / total_menu_price
        result["price_multiple_vs_menu"] = round(multiple, 2)
        if multiple >= 1.5:
            result["warnings"].append(
                f"整案價是菜單價加總的 {multiple:.2f} 倍,報價單不得列菜單單價(客人手上有外帶菜單會直接比對)"
            )
    if result["estimated_items"]:
        result["warnings"].append(
            "含推估成本品項(" + "、".join(result["estimated_items"]) + "),報價前要廚房試做抓實數與最低訂購量"
        )
    return result


def cost_budget_for_margin(package_price: float, target_margin: float) -> float:
    """目標毛利率 → 食材成本上限。整案價法唯一的槓桿就是這條線。"""
    if not 0 < target_margin < 1:
        raise QuoteError("目標毛利率要介於 0 與 1 之間")
    return package_price * (1 - target_margin)


def scale_mix_to_margin(
    mix: list[tuple[str, int]],
    package_price: float,
    pax: int,
    target_margin: float,
    *,
    book: dict | None = None,
) -> dict:
    """菜色由人定,程式只負責放大縮小到剛好達標。

    **刻意不自動選菜**:hermes 的 fail-closed 紅線含「不選菜」,而且自動配出來的組合
    會出現「16 張 pizza 配 2 份蝦棗」這種沒人敢端出去的菜單(2026-09-22 第一版實測)。
    所以輸入是人給的比例,程式找出最大的整數倍率 k,使 k×mix 的食材成本仍在上限內。
    """
    book = book or load_price_book()
    if not mix:
        raise QuoteError("沒有給菜色比例,需人工先定菜")
    cost_budget = cost_budget_for_margin(package_price, target_margin)
    unit_cost = 0.0
    for name, units in mix:
        line = lookup(name, book)
        unit_cost += _unit_cost(line) * units
    if unit_cost <= 0:
        raise QuoteError("這組菜色的食材成本算出來是 0,資料有問題,需人工檢查")
    k = int(cost_budget // unit_cost)
    if k < 1:
        raise QuoteError(
            f"食材成本上限 {cost_budget:.0f} 元,但這組菜色一輪就要 {unit_cost:.0f} 元,"
            f"毛利率 {target_margin:.0%} 在這組菜色下做不到——要嘛降毛利,要嘛換菜色(換菜色是人的決定)"
        )
    scaled = [(name, units * k) for name, units in mix]
    result = plan_by_items(scaled, package_price=package_price, pax=pax, book=book)
    result["target_margin"] = target_margin
    result["cost_budget"] = round(cost_budget, 2)
    result["scale_factor"] = k
    result["headroom"] = round(cost_budget - result["food_cost"], 2)
    return result


def reference_plans(book: dict | None = None) -> list[dict]:
    """已經算過、Owner 看過的配置。hermes 要能說「上次同規模是這樣配的」而不是重新發明。

    retired 的配置不列出來。Owner msg 5800 問「why 開了 60% 的」——A-60 是他下
    「毛利 80% 以上」之前的版本,留在清單裡就等於還在提案,這是提案清單沒清乾淨的錯。
    """
    book = book or load_price_book()
    return [plan for plan in book.get("reference_plans", []) if not plan.get("retired")]


def run_reference_plan(name: str, book: dict | None = None) -> dict:
    """照名字重算。作廢配置查得到但會擋下來,避免「不知道它為什麼還在」再發生一次。"""
    book = book or load_price_book()
    for plan in book.get("reference_plans", []):
        if plan["name"] == name and plan.get("retired"):
            raise QuoteError(
                f"配置「{name}」已作廢({plan.get('retired_reason', '無原因記載')}),不得提案"
            )
    for plan in reference_plans(book):
        if plan["name"] == name:
            result = plan_by_items(
                [(item["key"], item["units"]) for item in plan["mix"]],
                package_price=plan.get("package_price"),
                pax=plan.get("pax"),
                book=book,
            )
            result["reference_plan"] = plan["name"]
            result["reference_source"] = plan.get("source")
            return result
    raise QuoteError(f"沒有名為「{name}」的既有配置,需人工確認")


def change_order(before: dict, after: dict) -> dict:
    """改單:算前後差額。毛利率掉了要講「掉幾個百分點」,不要只講新數字。"""
    delta_rate = after["margin_rate"] - before["margin_rate"]
    return {
        "revenue_delta": round(after["revenue"] - before["revenue"], 2),
        "food_cost_delta": round(after["food_cost"] - before["food_cost"], 2),
        "gross_profit_delta": round(after["gross_profit"] - before["gross_profit"], 2),
        "margin_rate_before": before["margin_rate"],
        "margin_rate_after": after["margin_rate"],
        "margin_points_delta": round(delta_rate * 100, 2),
        "pieces_delta": after["pieces"] - before["pieces"],
    }


def external_item_price(local_base: float, book: dict | None = None) -> dict:
    """外部品項(道具、租借、外包服務)對外價=台南在地行情 × 1.35。

    小肚肚案 Owner msg 5197:緞帶對外價 260 → 1,350,因為基礎價要抓在地行情不抓網購低價。
    """
    book = book or load_price_book()
    markup = book["rules"]["external_markup"]
    return {
        "local_base": local_base,
        "markup": markup,
        "external_price": round(local_base * markup),
        "rule": book["rules"]["external_markup_source"],
    }


_PAX_RE = re.compile(r"(\d{1,4})\s*(?:人|位|pax)")
_BUDGET_RE = re.compile(r"(?:預算|budget)\D{0,6}(\d{3,7})|(\d{4,7})\s*(?:塊|元)")
_PER_PAX_RE = re.compile(r"每人\D{0,4}(\d{2,5})\s*(?:塊|元)")
_MARGIN_RE = re.compile(r"毛利\D{0,6}(\d{2})\s*(?:%|％|成)?")
_DATE_RE = re.compile(r"(\d{1,2}\s*[/月]\s*\d{1,2})|(\d{1,2}\s*月\s*(?:初|中|下|上)旬)")


def parse_brief(text: str) -> dict:
    """從 Owner 一句話裡抓出人數、預算、目標毛利、日期。抓不到就列進 missing,不猜。"""
    text = text or ""
    pax = _PAX_RE.search(text)
    per_pax = _PER_PAX_RE.search(text)
    budget_match = _BUDGET_RE.search(text)
    margin = _MARGIN_RE.search(text)
    date = _DATE_RE.search(text)

    facts: dict[str, object] = {}
    if pax:
        facts["pax"] = int(pax.group(1))
    if budget_match:
        facts["budget"] = int(budget_match.group(1) or budget_match.group(2))
    elif per_pax and pax:
        facts["budget"] = int(per_pax.group(1)) * int(pax.group(1))
        facts["budget_from_per_pax"] = True
    if margin:
        value = int(margin.group(1))
        facts["target_margin"] = value / 100 if value > 10 else value / 10
    if date:
        facts["event_date"] = date.group(0)

    missing = [label for key, label in REQUIRED_FACTS if key not in facts]
    return {"facts": facts, "missing": missing}


def render(result: dict) -> str:
    """給 Telegram 的純文字表。標題固定標內部試算,避免被直接轉給客人。"""
    lines = [
        "【內部試算・不得直接發給客人】",
        f"報價法:{result['mode']}",
        f"售價 {result['revenue']:.0f} 元／食材成本 {result['food_cost']:.0f} 元／毛利 {result['gross_profit']:.0f} 元",
        f"毛利率 {result['margin_rate'] * 100:.1f}%",
        f"總件數 {result['pieces']} 件" + (f"、每人 {result['pieces_per_pax']} 件" if result.get("pieces_per_pax") else ""),
        "",
        "配置:",
    ]
    for line in result["lines"]:
        lines.append(
            f"- {line['key']} {line['units']} {line['unit']}({line['pieces']} 件),食材成本 {line['cost']:.0f}"
        )
    if result.get("price_multiple_vs_menu"):
        lines.append("")
        lines.append(f"菜單價加總 {result['menu_price_sum']:.0f} 元,整案價為其 {result['price_multiple_vs_menu']} 倍")
    if result["warnings"]:
        lines.append("")
        lines.append("風險:")
        lines.extend(f"- {item}" for item in result["warnings"])
    return "\n".join(lines)


def _parse_items(values: list[str]) -> list[tuple[str, int]]:
    items = []
    for value in values:
        if "=" not in value:
            raise QuoteError(f"品項參數要寫成 名稱=單位數,收到「{value}」")
        name, _, count = value.partition("=")
        items.append((name.strip(), int(count)))
    return items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MAP LAB 報價試算(零 LLM)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("margin-table", help="逐品項毛利率與逐項加總天花板")

    scale = sub.add_parser("scale", help="菜色比例由人給,程式放大到剛好達標毛利率")
    scale.add_argument("--item", nargs="+", required=True, help="名稱=相對單位數")
    scale.add_argument("--package-price", type=float, required=True)
    scale.add_argument("--pax", type=int, required=True)
    scale.add_argument("--margin", type=float, required=True, help="目標毛利率,例 0.8")

    ref = sub.add_parser("ref", help="重算既有配置(不給名稱=列出全部)")
    ref.add_argument("name", nargs="?", default=None)

    items = sub.add_parser("items", help="指定品項與數量算毛利")
    items.add_argument("--item", nargs="+", required=True, help="名稱=單位數")
    items.add_argument("--package-price", type=float, default=None)
    items.add_argument("--pax", type=int, default=None)

    brief = sub.add_parser("brief", help="從一句話抓人數/預算/毛利/日期")
    brief.add_argument("text")

    external = sub.add_parser("external", help="外部品項在地價 ×1.35")
    external.add_argument("--local-base", type=float, required=True)

    args = parser.parse_args(argv)
    try:
        if args.cmd == "margin-table":
            print(json.dumps({"rows": margin_table(), "ceiling": menu_sum_ceiling()}, ensure_ascii=False, indent=2))
        elif args.cmd == "scale":
            result = scale_mix_to_margin(
                _parse_items(args.item), args.package_price, args.pax, args.margin
            )
            print(render(result))
        elif args.cmd == "ref":
            if args.name is None:
                for plan in reference_plans():
                    print(f"{plan['name']}\t{plan['label']}\t來源 {plan['source']}")
            else:
                print(render(run_reference_plan(args.name)))
        elif args.cmd == "items":
            result = plan_by_items(_parse_items(args.item), package_price=args.package_price, pax=args.pax)
            print(render(result))
        elif args.cmd == "brief":
            print(json.dumps(parse_brief(args.text), ensure_ascii=False, indent=2))
        elif args.cmd == "external":
            print(json.dumps(external_item_price(args.local_base), ensure_ascii=False, indent=2))
    except QuoteError as exc:
        print(f"需人工:{exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
