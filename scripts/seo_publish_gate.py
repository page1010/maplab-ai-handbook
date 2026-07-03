#!/usr/bin/env python3
"""
seo_publish_gate.py — SEO 發布前自動閘門

規格版本：v0.1-spec（2026-07-03）
狀態：規格草稿 — 介面與邏輯已定義，尚未完整實作（TODO 標記處）

用途
----
在 SEO 草稿進入 WordPress 之前，自動執行 docs/seo-publish-checklist.md
中「🤖 可自動」的檢查項目，輸出 PASS/FAIL 與缺陷清單。

本腳本不依賴 Claude、不呼叫 broker/WP API（可選），可在本機 venv 跑。

用法
----
    # 只跑本地文件檢查（不需 WP 憑證）
    python seo_publish_gate.py \\
        --approved path/to/approved.md \\
        --draft    path/to/draft.html

    # 也對照 WP draft（需 WP Basic Auth 環境變數）
    python seo_publish_gate.py \\
        --approved path/to/approved.md \\
        --wp-post-id 1234

    # 只跑特定類別
    python seo_publish_gate.py --approved x.md --draft y.html --check links

環境變數（選用，只在 --wp-post-id 模式需要）
--------------------------------------------
    WP_API_BASE   https://www.maplabkitchen.com/wp-json
    WP_AUTH       Basic base64(email:app_password)
    SEO_404_LIST  逗號分隔的 404 slug，可覆蓋下方 DEFAULT_404_SLUGS

設計原則
--------
1. 本地優先：全部 check 都可以只靠本地文件跑，不強制需要 WP 憑證。
2. 確定性：同一輸入永遠同一輸出，無隨機或 AI 判斷。
3. 只進不退：新缺陷回填為新 Check，在 CHECKS 字典新增一項即可。
4. 不寫回：本腳本只讀取，不修改任何文件或 WP 內容。

輸出格式
--------
    PASS  [A-1] 內容長度符合（draft=3210 chars, approved=3220 chars, ratio=0.997）
    FAIL  [B-1] 找到 1 個 INTERNAL_LINK_RECHECK_REQUIRED 佔位
          → 位置: line 31: "企業外燴費用估算：[INTERNAL_LINK_RECHECK_REQUIRED: tainan-corporate-catering-cost]"
    FAIL  [B-3] CTA href 仍是佔位符
          → 位置: line 109: href="/【待填：line-official】"

    ─────────────────────────────────
    結果：2 項 FAIL，需修復後重跑閘門
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# ── 常數 ───────────────────────────────────────────────────────────────────────

# 404 禁連 slug 清單（來源：docs/seo-keyword-map.md planned_404 區）
# 維護：每次 seo-keyword-map.md 新增 planned_404 → 同步更新這裡
DEFAULT_404_SLUGS: list[str] = [
    "catering-corporate-tainan",
    "catering-birthday-party-tainan",
    "catering-wedding-tainan",
    "opening-event-catering-tainan",
    "meeting-refreshment-catering-tainan",
    "brand-event-catering",
    "school-event-catering-tainan",
    # ── 新缺陷棘輪：在此追加，保持時間序 ──
]

# 禁用詞清單（來源：skills/brand-voice-guide.md §三）
BANNED_WORDS: list[str] = [
    "超值", "保證滿意", "CP值", "佛心", "便宜又大碗",
    "錯過可惜", "名額有限", "一生一次", "不訂會後悔",
]
BANNED_WORD_MAX_OCCURRENCES = {"精緻": 2}  # 出現超過 N 次才算違規

# 說服式對比句型 regex（來源：brand-voice-guide.md 第 4 點）
PERSUASION_PATTERNS: list[str] = [
    r"不是.{0,12}而是",
    r"不僅.{0,12}更",
    r"不需要.{0,12}而是",
    r"雖然不.{0,8}但",
    r"與其.{0,12}不如",
]

# 把話說死的詞
ABSOLUTE_WORDS: list[str] = ["一定", "保證", "最適合", "絕對", "唯一", "最好"]

# 佔位字串 patterns
PLACEHOLDER_PATTERNS: list[str] = [
    r"\[INTERNAL_LINK_RECHECK_REQUIRED[^\]]*\]",
    r'href="/【待填[^"]*】"',   # /【待填：slug】
    r'href="【[^"]*】"',        # 【填入 LINE Official URL】等全形括號佔位
    r'href="\[待填[^"]*\]"',   # [待填...] ASCII括號
    r'href="#"',
]

# 最小 content-length 比例（draft / approved ≥ 此值才算 PASS）
MIN_LENGTH_RATIO = 0.95

# ── 資料型別 ────────────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    check_id: str          # e.g. "A-1"
    passed: bool
    description: str       # 簡短說明
    details: list[str] = field(default_factory=list)  # 失敗時的位置/內容


@dataclass
class GateReport:
    results: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    def print(self) -> None:
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            print(f"  {status}  [{r.check_id}] {r.description}")
            for d in r.details:
                print(f"        → {d}")
        print()
        fails = [r for r in self.results if not r.passed]
        if self.passed:
            print("  ✅ 全部通過，可進入 Owner 視覺確認流程")
        else:
            print(f"  ❌ {len(fails)} 項 FAIL，修復後重跑閘門")
            for r in fails:
                print(f"     [{r.check_id}] {r.description}")


# ── 輔助函式 ────────────────────────────────────────────────────────────────────

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def char_count(text: str) -> int:
    return len(text.replace("\n", "").replace(" ", ""))


def sha256_prefix(text: str, n: int = 500) -> str:
    segment = text.strip()[:n]
    return hashlib.sha256(segment.encode()).hexdigest()[:16]


def find_lines(text: str, pattern: str) -> list[str]:
    """回傳 text 中符合 regex pattern 的行（含行號）。"""
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(pattern, line):
            results.append(f"line {i}: {line.strip()[:120]}")
    return results


def strip_html_comments(text: str) -> str:
    """移除 HTML 注解區塊（<!-- ... -->），避免 E 類檢查掃到注解範例詞。"""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def extract_headings(text: str) -> list[str]:
    """從 markdown 或 HTML 中抓出所有 H2/H3 標題文字。"""
    md_heads = re.findall(r"^#{2,3}\s+(.+)", text, re.MULTILINE)
    html_heads = re.findall(r"<h[23][^>]*>([^<]+)</h[23]>", text, re.IGNORECASE)
    return md_heads + html_heads


# ── 各 Check 函式 ──────────────────────────────────────────────────────────────

def check_a1_length(approved: str, draft: str) -> CheckResult:
    """A-1: draft 字數 ≥ approved × 0.95"""
    a_len = char_count(approved)
    d_len = char_count(draft)
    ratio = d_len / a_len if a_len else 1.0
    passed = ratio >= MIN_LENGTH_RATIO
    desc = f"內容長度比例 {ratio:.3f}（draft={d_len}, approved={a_len}, 最低={MIN_LENGTH_RATIO}）"
    details = [] if passed else [f"draft 比 approved 短 {(1-ratio)*100:.1f}%，超過 5% 上限"]
    return CheckResult("A-1", passed, desc, details)


def check_a2_fingerprint(approved: str, draft: str) -> CheckResult:
    """A-2: 關鍵段落指紋比對（前 500 字 SHA256 + 所有 H2/H3 標題集合）"""
    # 前 500 字指紋
    a_fp = sha256_prefix(approved)
    d_fp = sha256_prefix(draft)
    head_match = set(extract_headings(approved)) == set(extract_headings(draft))
    passed = (a_fp == d_fp) and head_match
    details = []
    if a_fp != d_fp:
        details.append(f"前 500 字指紋不符：approved={a_fp} draft={d_fp}")
    if not head_match:
        only_in_approved = set(extract_headings(approved)) - set(extract_headings(draft))
        only_in_draft = set(extract_headings(draft)) - set(extract_headings(approved))
        if only_in_approved:
            details.append(f"approved 獨有標題：{only_in_approved}")
        if only_in_draft:
            details.append(f"draft 多出標題：{only_in_draft}")
    desc = "關鍵段落指紋比對" + ("通過" if passed else "不符")
    return CheckResult("A-2", passed, desc, details)


def check_a3_checker_note(draft: str) -> CheckResult:
    """A-3: draft 不含 CHECKER NOTE"""
    found = re.search(r"<!--\s*CHECKER NOTE", draft, re.IGNORECASE)
    passed = not bool(found)
    details = ["找到 CHECKER NOTE 區塊，不得進 WP content"] if not passed else []
    return CheckResult("A-3", passed, "CHECKER NOTE 已移除", details)


def check_b1_placeholders(draft: str) -> CheckResult:
    """B-1: 無 INTERNAL_LINK_RECHECK_REQUIRED 佔位（先移除 HTML 注解，避免 CHECKER NOTE 中的提示詞觸發假陽性）"""
    clean = strip_html_comments(draft)
    lines: list[str] = []
    for pat in PLACEHOLDER_PATTERNS[:1]:  # B-1 專跑 INTERNAL_LINK 佔位
        lines.extend(find_lines(clean, pat))
    passed = len(lines) == 0
    desc = f"無 INTERNAL_LINK 佔位字串" + ("" if passed else f"（找到 {len(lines)} 處）")
    return CheckResult("B-1", passed, desc, lines)


def check_b2_404_slugs(draft: str, forbidden_404: list[str]) -> CheckResult:
    """B-2: 無連到 404 slug"""
    found: list[str] = []
    for slug in forbidden_404:
        matches = find_lines(draft, re.escape(slug))
        found.extend(matches)
    passed = len(found) == 0
    desc = "無 404 slug 直連" + ("" if passed else f"（找到 {len(found)} 處）")
    return CheckResult("B-2", passed, desc, found)


def check_b3_cta_href(draft: str) -> CheckResult:
    """B-3: CTA href 不是佔位符"""
    lines: list[str] = []
    for pat in PLACEHOLDER_PATTERNS[1:]:  # B-3 跑 href 佔位
        lines.extend(find_lines(draft, pat))
    passed = len(lines) == 0
    desc = "CTA href 已填真實 URL" + ("" if passed else f"（找到 {len(lines)} 個佔位 href）")
    return CheckResult("B-3", passed, desc, lines)


def check_e1_banned_words(draft: str) -> CheckResult:
    """E-1: 無禁用詞（先移除 HTML 注解，避免掃到範例詞）"""
    clean = strip_html_comments(draft)
    found: list[str] = []
    for word in BANNED_WORDS:
        if word in clean:
            lines = find_lines(clean, re.escape(word))
            found.extend(lines)
    for word, max_count in BANNED_WORD_MAX_OCCURRENCES.items():
        count = clean.count(word)
        if count > max_count:
            found.append(f'「{word}」出現 {count} 次（上限 {max_count}）')
    passed = len(found) == 0
    desc = "無禁用詞" + ("" if passed else f"（找到 {len(found)} 處）")
    return CheckResult("E-1", passed, desc, found)


def check_e2_persuasion_patterns(draft: str) -> CheckResult:
    """E-2: 無說服式對比句型（先移除 HTML 注解）"""
    clean = strip_html_comments(draft)
    found: list[str] = []
    for pat in PERSUASION_PATTERNS:
        found.extend(find_lines(clean, pat))
    passed = len(found) == 0
    desc = "無說服式對比句型" + ("" if passed else f"（找到 {len(found)} 處）")
    return CheckResult("E-2", passed, desc, found)


def check_e3_absolute_words(draft: str) -> CheckResult:
    """E-3: 無把話說死的詞（先移除 HTML 注解；「不一定」中的「一定」用 negative lookbehind 排除）"""
    clean = strip_html_comments(draft)
    found: list[str] = []
    for word in ABSOLUTE_WORDS:
        # 「一定」特別處理：只抓前面不是「不」的情況
        if word == "一定":
            pat = r"(?<!不)一定"
        else:
            pat = re.escape(word)
        found.extend(find_lines(clean, pat))
    passed = len(found) == 0
    desc = "無絕對化用詞" + ("" if passed else f"（找到 {len(found)} 處）")
    return CheckResult("E-3", passed, desc, found)


# ── WP REST checks（需憑證，選用）─────────────────────────────────────────────

def check_c1_featured_image_wp(post_id: int, wp_base: str, auth: str) -> CheckResult:
    """C-1: WP draft 有設定 featured_media（需 WP REST 憑證）"""
    # TODO: 實作 WP REST 呼叫
    # url = f"{wp_base}/wp/v2/posts/{post_id}?_fields=featured_media"
    # req = urllib.request.Request(url, headers={"Authorization": auth})
    # resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    # featured = resp.get("featured_media", 0)
    # return CheckResult("C-1", featured != 0, ...)
    return CheckResult("C-1", False, "TODO: 需 WP REST 憑證才能檢查 featured_media", ["--wp-post-id 模式尚未實作"])


# ── 主程式 ─────────────────────────────────────────────────────────────────────

def build_404_list() -> list[str]:
    env_list = os.environ.get("SEO_404_LIST", "")
    if env_list:
        return [s.strip() for s in env_list.split(",") if s.strip()]
    return DEFAULT_404_SLUGS


def run_gate(
    approved_path: Path | None,
    draft_path: Path | None,
    wp_post_id: int | None,
    checks_filter: str | None,
) -> GateReport:
    report = GateReport()
    forbidden_404 = build_404_list()

    approved = read_text(approved_path) if approved_path else ""
    draft = read_text(draft_path) if draft_path else ""

    all_checks: list[tuple[str, Callable[[], CheckResult]]] = [
        ("fingerprint", lambda: check_a1_length(approved, draft)),
        ("fingerprint", lambda: check_a2_fingerprint(approved, draft)),
        ("fingerprint", lambda: check_a3_checker_note(draft)),
        ("links",       lambda: check_b1_placeholders(draft)),
        ("links",       lambda: check_b2_404_slugs(draft, forbidden_404)),
        ("links",       lambda: check_b3_cta_href(draft)),
        ("brand",       lambda: check_e1_banned_words(draft)),
        ("brand",       lambda: check_e2_persuasion_patterns(draft)),
        ("brand",       lambda: check_e3_absolute_words(draft)),
    ]

    if wp_post_id:
        wp_base = os.environ.get("WP_API_BASE", "")
        wp_auth = os.environ.get("WP_AUTH", "")
        all_checks.append(
            ("assets", lambda: check_c1_featured_image_wp(wp_post_id, wp_base, wp_auth))
        )

    for category, fn in all_checks:
        if checks_filter and category != checks_filter:
            continue
        if not approved and category == "fingerprint":
            report.results.append(CheckResult("A-?", False, "未提供 --approved 路徑，跳過指紋檢查"))
            continue
        if not draft and not wp_post_id:
            report.results.append(CheckResult("?", False, "未提供 --draft 或 --wp-post-id，無法檢查"))
            break
        report.results.append(fn())

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="SEO 發布前閘門（本地自動檢查）")
    parser.add_argument("--approved", type=Path, help="核准版文件路徑（.md 或 .html）")
    parser.add_argument("--draft",    type=Path, help="待發布 draft 路徑（.html）")
    parser.add_argument("--wp-post-id", type=int, help="WP post ID（啟用 WP REST 檢查）")
    parser.add_argument("--check", choices=["fingerprint", "links", "assets", "brand"],
                        help="只跑特定類別")
    args = parser.parse_args()

    if not args.approved and not args.draft and not args.wp_post_id:
        parser.print_help()
        sys.exit(1)

    print()
    print("SEO 發布閘門 — 自動檢查")
    print("─" * 50)

    report = run_gate(args.approved, args.draft, args.wp_post_id, args.check)
    report.print()

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
