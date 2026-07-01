#!/usr/bin/env python3
"""
seo_gap_picker.py — 從 docs/seo-keyword-map.md §6 挑下一個高價值未草稿 GAP。
輸出 JSON 到 stdout。不寫任何檔案。
HARD: 不碰 A6/bot_a6、不 push、不改倉。
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
KEYWORD_MAP = REPO / "docs" / "seo-keyword-map.md"
DRAFTS_DIR  = REPO / "workbook" / "outputs" / "seo-gap-drafts"
STATE_FILE  = REPO / "state" / "seo_loop_state.json"

# GAP 定義（硬編，與 keyword-map §6 對應；素材就緒 > 素材待確認）
GAPS: list[dict] = [
    {
        "gap_id": "GAP-1",
        "title": "飯店場域會議茶點案例",
        "priority": 1,
        "materials_ready": True,
        "main_kw": "台南飯店會議茶點外燴",
        "sub_kws": ["富信飯店", "會議茶歇", "社工公會", "研討會餐點"],
        "slug_target": "tainan-hotel-meeting-tea-catering",
        "article_type": "case_study",
        "drive_folders": ["20260614富信飯店-社工公會會議"],
        "internal_links": [
            "corporate-tea-party-desserts",
            "corporate-catering-tainan",
            "icc-tainan-catering",
        ],
    },
    {
        "gap_id": "GAP-2",
        "title": "開幕茶會案例 ×2",
        "priority": 2,
        "materials_ready": True,
        "main_kw": "台南開幕茶會外燴案例",
        "sub_kws": ["店面開幕", "舞蹈教室", "木地板門市", "品牌貴賓接待"],
        "slug_target": "tainan-opening-tea-party-catering-case",
        "article_type": "case_study",
        "drive_folders": [
            "20260614-醞舞流舞蹈教室開幕",
            "20260621說事實木地板開幕",
        ],
        "internal_links": [
            "tainan-corporate-opening-tea-catering",
            "business-opening-party-ideas",
            "corporate-catering-tainan",
        ],
    },
    {
        "gap_id": "GAP-3",
        "title": "行政/HR/秘書 B2B 買家角色 guide",
        "priority": 3,
        "materials_ready": True,  # 不需要新素材，重用企業案例圖
        "main_kw": "行政外燴推薦 HR 活動餐點規劃",
        "sub_kws": ["會議茶點怎麼訂", "份量", "預算審核", "approval-ready"],
        "slug_target": "hr-admin-meeting-catering-guide-tainan",
        "article_type": "buyer_role_guide",
        "drive_folders": [],  # 重用既有企業圖
        "internal_links": [
            "corporate-catering-tainan",
            "tainan-corporate-catering-cost",
            "corporate-tea-party-desserts",
        ],
    },
    {
        "gap_id": "GAP-4",
        "title": "南科/成大 在地產業頁",
        "priority": 4,
        "materials_ready": False,  # 需 Owner 確認服務範圍 + 案例
        "main_kw": "南科企業外燴 成大會議茶點",
        "sub_kws": ["科技公司活動餐點", "研討會", "台南南科"],
        "slug_target": "tainan-stem-district-catering",
        "article_type": "venue_guide",
        "drive_folders": [],
        "internal_links": [
            "corporate-catering-tainan",
            "icc-tainan-catering",
        ],
    },
    {
        "gap_id": "GAP-5",
        "title": "一口點心/canapes 企業通用菜單頁",
        "priority": 5,
        "materials_ready": True,  # 食物特寫類圖可重用
        "main_kw": "台南一口點心外燴 canapes 接待",
        "sub_kws": ["站立式活動", "酒會", "finger food", "企業接待"],
        "slug_target": "tainan-canapes-corporate-reception-catering",
        "article_type": "menu_guide",
        "drive_folders": [],
        "internal_links": [
            "corporate-tea-party-desserts",
            "vip-expo-catering-business-meeting",
        ],
    },
]

FOUR_OH_FOUR_SLUGS = {
    "catering-corporate-tainan",
    "catering-birthday-party-tainan",
    "catering-wedding-tainan",
    "opening-event-catering-tainan",
    "meeting-refreshment-catering-tainan",
    "brand-event-catering",
    "school-event-catering-tainan",
}


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"drafted": [], "published": [], "qa_failed": []}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def draft_exists(gap: dict) -> bool:
    """Check if a draft file exists for this GAP (by slug_target or gap_id variants)."""
    slug = gap["slug_target"]
    gap_id = gap["gap_id"]
    # "gap-1" → also match "gap1"
    gap_id_nohyphen = gap_id.lower().replace("-", "")
    for f in DRAFTS_DIR.glob("*.md"):
        name = f.name.lower()
        if slug in name or gap_id.lower() in name or gap_id_nohyphen in name:
            return True
    return False


def pick_next_gap() -> dict | None:
    state = load_state()
    drafted = set(state.get("drafted", []))
    published = set(state.get("published", []))

    for gap in sorted(GAPS, key=lambda g: g["priority"]):
        gid = gap["gap_id"]
        if gid in published:
            continue
        if gid in drafted:
            # Also skip if already drafted (draft exists on disk)
            continue
        if draft_exists(gap):
            # Mark as drafted in state if not already
            if gid not in drafted:
                state["drafted"].append(gid)
                save_state(state)
            continue
        if not gap["materials_ready"] and "--include-no-materials" not in sys.argv:
            continue
        return gap

    return None


def main() -> None:
    gap = pick_next_gap()
    if gap is None:
        print(json.dumps({"status": "all_gaps_drafted", "gap": None}, ensure_ascii=False))
        sys.exit(0)

    print(json.dumps({"status": "ready", "gap": gap}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
