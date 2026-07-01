#!/usr/bin/env python3
"""
seo_qa_checker.py — 確定性 QA 掃描 SEO 草稿。
不燒 Claude/Codex/agy；純 regex + 規則。

用法:
  python seo_qa_checker.py <draft_path> [--gap-type case_study|venue_guide|buyer_role_guide|menu_guide]
  → stdout JSON {pass: bool, score: int, failures: [...], warnings: [...]}
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent

# ── 禁用詞 (brand-voice-guide.md) ────────────────────────────────────────────
FORBIDDEN_WORDS = [
    "最頂", "超值", "保證滿意", "CP值爆高", "CP值", "佛心",
    "便宜又大碗", "錯過可惜", "趕快預約", "名額有限", "快私訊",
    "一生一次不能省", "不訂會後悔",
]
# 少用字（每篇最多 2 次）
CAUTIOUS_WORDS = ["精緻", "質感", "用心", "客製化"]

# ── 404 禁連 slug ─────────────────────────────────────────────────────────────
FOUR_OH_FOUR_SLUGS = [
    "catering-corporate-tainan",
    "catering-birthday-party-tainan",
    "catering-wedding-tainan",
    "opening-event-catering-tainan",
    "meeting-refreshment-catering-tainan",
    "brand-event-catering",
    "school-event-catering-tainan",
]

# ── 6 盲點 checklist ─────────────────────────────────────────────────────────
BLIND_SPOT_PATTERNS = {
    "肖像隱私": [r"肖像", r"隱私", r"照片.*處理", r"臉部.*模糊", r"模糊化", r"人像"],
    "禁帶外食/清潔費": [r"禁帶外食", r"清潔費", r"進場.*規定", r"飯店.*限制", r"保證金"],
    "飲食禁忌": [r"飲食禁忌", r"素食", r"全素", r"無麩質", r"過敏", r"忌口"],
    "超時撤場費": [r"超時", r"撤場費", r"延遲.*費", r"超時.*服務費"],
    "色彩/visual-spec": [
        r"#[0-9A-Fa-f]{6}", r"visual.?spec", r"色彩規範", r"色彩系統",
        r"深橄欖", r"暖米", r"鼠尾草綠", r"奶油白",
    ],
    "crawl_budget/redirect": [
        r"crawl.?budget", r"抓取配額", r"redirect.?chain", r"重定向.*鏈",
        r"301.*chain", r"一跳到", r"不能.*A.*B.*C", r"避免.*多跳",
    ],
}

# 案例文章必須檢查的盲點
CASE_STUDY_REQUIRED = {"肖像隱私", "飲食禁忌", "超時撤場費"}
# 飯店場地文章必須加的
HOTEL_REQUIRED = {"禁帶外食/清潔費"}
# 互搶計畫必須檢查的
CANNIBALIZATION_REQUIRED = {"crawl_budget/redirect"}


def load_draft(path: str) -> tuple[str, str]:
    """Return (full_text, content_text) where content_text strips HTML comments."""
    p = Path(path)
    if not p.exists():
        print(json.dumps({"pass": False, "error": f"File not found: {path}"}))
        sys.exit(1)
    raw = p.read_text(encoding="utf-8")
    content = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
    return raw, content


def check_forbidden_words(text: str) -> list[str]:
    failures = []
    for w in FORBIDDEN_WORDS:
        if w in text:
            count = text.count(w)
            failures.append(f"禁用詞出現: 「{w}」× {count}")
    return failures


def check_cautious_words(text: str) -> list[str]:
    warnings = []
    for w in CAUTIOUS_WORDS:
        count = text.count(w)
        if count > 2:
            warnings.append(f"少用字過多: 「{w}」× {count}（限 ≤2）")
    return warnings


def check_h1_keyword(text: str, main_kw: str | None) -> list[str]:
    failures = []
    h1_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if not h1_match:
        failures.append("未找到 H1（# 開頭標題）")
    elif main_kw and main_kw not in h1_match.group(1):
        # partial match ok (main_kw may be combined)
        # Check first keyword word
        kw_parts = main_kw.split() if main_kw else []
        first_kw = kw_parts[0] if kw_parts else ""
        if first_kw and first_kw not in h1_match.group(1):
            failures.append(f"H1 未含主關鍵字第一詞「{first_kw}」")
    return failures


def check_first_para_keyword(text: str, main_kw: str | None) -> list[str]:
    """首段前 110 字要含主關鍵字。"""
    failures = []
    if not main_kw:
        return failures
    # Skip H1 line, get first paragraph
    lines = text.split("\n")
    body_lines = [l for l in lines if l.strip() and not l.startswith("#") and not l.startswith("<!--")]
    first_para = " ".join(body_lines[:3])[:110]
    kw_parts = main_kw.split()
    first_kw = kw_parts[0] if kw_parts else ""
    if first_kw and first_kw not in first_para:
        failures.append(f"首段前 110 字未含主關鍵字「{first_kw}」")
    return failures


def check_alt_format(text: str) -> list[str]:
    """Alt 文案必須是 A 式：台南.*外燴—.*"""
    failures = []
    alt_blocks = re.findall(r"<!--\s*圖片\s*alt[^:]*:\s*([^-]+)", text)
    # Also check markdown image alts
    md_alts = re.findall(r'!\[([^\]]+)\]', text)

    all_alts = alt_blocks + md_alts
    for alt in all_alts:
        alt = alt.strip()
        if not alt or alt == "":
            continue
        if not re.search(r"台南.*外燴.{0,3}[—\-]", alt):
            failures.append(f"Alt 不符 A 式格式: 「{alt[:60]}」")
    return failures


def check_no_404_slugs(text: str) -> list[str]:
    """不能直連 404 slug（排除 INTERNAL_LINK_RECHECK_REQUIRED 包裹的）。"""
    failures = []
    # Remove RECHECK_REQUIRED blocks
    cleaned = re.sub(r"\[INTERNAL_LINK_RECHECK_REQUIRED:[^\]]*\]", "", text)
    for slug in FOUR_OH_FOUR_SLUGS:
        if slug in cleaned:
            failures.append(f"直連 404 slug: {slug}")
    return failures


def check_internal_links_format(text: str) -> list[str]:
    """內鏈應全用 [INTERNAL_LINK_RECHECK_REQUIRED: slug]，不能是裸 markdown 連結到 slug。"""
    warnings = []
    # Find bare markdown links that look like WP slugs (not RECHECK wrapped)
    bare_links = re.findall(r"\]\((?!/|http|#)([a-z0-9\-]+)\)", text)
    for slug in bare_links:
        if slug not in FOUR_OH_FOUR_SLUGS:  # already caught above
            warnings.append(f"疑似裸連 slug（未用 RECHECK 佔位）: {slug}")
    return warnings


def check_blind_spots(text: str, gap_type: str, article_title: str) -> list[str]:
    """6 盲點 checklist。"""
    failures = []

    # Determine required blind spots based on type
    required = set(BLIND_SPOT_PATTERNS.keys())  # 全部預設要檢查
    # For non-hotel articles, disable hotel check
    if gap_type not in ("case_study",) and "飯店" not in article_title:
        required.discard("禁帶外食/清潔費")
    # For non-cannibalization articles
    if gap_type != "cannibalization":
        required.discard("crawl_budget/redirect")

    for spot, patterns in BLIND_SPOT_PATTERNS.items():
        if spot not in required:
            continue
        found = any(re.search(p, text, re.IGNORECASE) for p in patterns)
        if not found:
            failures.append(f"缺少盲點覆蓋: 「{spot}」")
    return failures


def check_line_cta(text: str) -> list[str]:
    """LINE CTA 必須在 FAQ 之後。"""
    failures = []
    faq_pos = text.find("## FAQ")
    if faq_pos == -1:
        faq_pos = text.find("## 常見問題")
    cta_pos = text.find("LINE")
    if faq_pos == -1:
        failures.append("未找到 FAQ block")
    if cta_pos == -1:
        failures.append("未找到 LINE CTA")
    elif faq_pos != -1 and cta_pos < faq_pos:
        failures.append("LINE CTA 在 FAQ 之前（應在 FAQ 後）")
    return failures


def check_checker_note(text: str) -> list[str]:
    """CHECKER NOTE block 是否存在。"""
    if "<!-- CHECKER NOTE:" not in text:
        return ["缺少 <!-- CHECKER NOTE: --> block"]
    return []


def run_qa(draft_path: str, gap_type: str = "case_study", main_kw: str | None = None) -> dict:
    full_text, content_text = load_draft(draft_path)
    title_match = re.search(r"^#\s+(.+)$", full_text, re.MULTILINE)
    article_title = title_match.group(1) if title_match else ""

    failures: list[str] = []
    warnings: list[str] = []

    # Scan content_text (no HTML comments) for brand-voice violations
    failures += check_forbidden_words(content_text)
    warnings += check_cautious_words(content_text)
    # All other checks use full_text (CHECKER NOTE included)
    failures += check_h1_keyword(full_text, main_kw)
    failures += check_first_para_keyword(full_text, main_kw)
    failures += check_alt_format(full_text)
    failures += check_no_404_slugs(full_text)
    warnings += check_internal_links_format(full_text)
    failures += check_blind_spots(full_text, gap_type, article_title)
    failures += check_line_cta(full_text)
    failures += check_checker_note(full_text)

    score = max(0, 100 - len(failures) * 15 - len(warnings) * 5)
    return {
        "pass": len(failures) == 0,
        "score": score,
        "failures": failures,
        "warnings": warnings,
        "draft_path": draft_path,
        "article_title": article_title,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: seo_qa_checker.py <draft_path> [--gap-type TYPE] [--kw KEYWORD]"}))
        sys.exit(1)

    draft_path = sys.argv[1]
    gap_type = "case_study"
    main_kw = None

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--gap-type" and i + 1 < len(sys.argv):
            gap_type = sys.argv[i + 1]
        if arg == "--kw" and i + 1 < len(sys.argv):
            main_kw = sys.argv[i + 1]

    result = run_qa(draft_path, gap_type, main_kw)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
