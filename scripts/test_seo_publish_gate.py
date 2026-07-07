#!/usr/bin/env python3
"""Test for seo_publish_gate.py F-1（食安/法規紅線用詞）gate.

背景：T-A2-002 回溯掃描 58 篇既有 WordPress 文章時發現 1 篇（post 698）
含「無麩質」FAQ 答案，且這類食安/法規風險用詞從未被自動擋在新內容產出
的關卡上（E-1 管的是行銷語氣，不是這個）。這支測試驗證新增的 F-1 gate
真的會擋下食安/法規紅線用詞，且不會跟 E-1 的品牌語氣禁用詞混在一起。

用法：
  python3 scripts/test_seo_publish_gate.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from seo_publish_gate import (
    FOOD_SAFETY_BANNED_WORDS,
    BANNED_WORDS,
    check_f1_food_safety_words,
    check_e1_banned_words,
)

FAILED = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  {status}  {label}")
    if not condition:
        FAILED.append(label)


def test_food_safety_words_are_a_separate_list_from_brand_words() -> None:
    print("\n[1] 食安清單與品牌語氣清單互不重疊")
    overlap = set(FOOD_SAFETY_BANNED_WORDS) & set(BANNED_WORDS)
    check("FOOD_SAFETY_BANNED_WORDS 與 BANNED_WORDS 無重複詞", len(overlap) == 0)


def test_gluten_free_chinese_is_caught() -> None:
    print("\n[2] 中文「無麩質」會被 F-1 擋下")
    draft = "<p>本活動可依需求提供素食、無麩質或低糖選項的菜單。</p>"
    result = check_f1_food_safety_words(draft)
    check("F-1 判定 FAIL（found 非空）", not result.passed)
    check("check_id 為 F-1（跟 E-1 分開，不共用同一個錯誤）", result.check_id == "F-1")
    check("details 有抓到含「無麩質」的那一行", any("無麩質" in d for d in result.details))


def test_gluten_free_english_case_insensitive_is_caught() -> None:
    print("\n[3] 英文「Gluten-Free」「GLUTENFREE」（大小寫/連字號變體）會被擋下")
    for variant in ["Gluten-Free", "gluten free", "GLUTENFREE"]:
        draft = f"<p>We offer a fully {variant} menu option upon request.</p>"
        result = check_f1_food_safety_words(draft)
        check(f"「{variant}」被擋下", not result.passed)


def test_other_food_safety_terms_are_caught() -> None:
    print("\n[4] 其餘食安/法規詞（ESG 認證/SDG/醫療級/第三方認證）會被擋下")
    for word in ["ESG 認證", "SDG", "醫療級", "第三方認證"]:
        draft = f"<p>本活動符合 {word} 標準。</p>"
        result = check_f1_food_safety_words(draft)
        check(f"「{word}」被擋下", not result.passed)


def test_clean_draft_passes_f1() -> None:
    print("\n[5] 沒有食安字眼的乾淨草稿應該 PASS")
    draft = "<p>本次外燴提供多樣菜色，歡迎依活動需求詢問客製化菜單。</p>"
    result = check_f1_food_safety_words(draft)
    check("F-1 判定 PASS", result.passed)


def test_f1_does_not_flag_brand_voice_words_and_vice_versa() -> None:
    print("\n[6] F-1 不會誤判品牌語氣詞；E-1 不會誤判食安詞（兩份清單真的分開）")
    brand_only_draft = "<p>本次活動超值優惠，CP值爆表，名額有限快私訊！</p>"
    f1_on_brand = check_f1_food_safety_words(brand_only_draft)
    check("F-1 對純行銷語氣違規的草稿判定 PASS（不誤判）", f1_on_brand.passed)

    food_safety_only_draft = "<p>提供無麩質餐點選項，歡迎洽詢。</p>"
    e1_on_food_safety = check_e1_banned_words(food_safety_only_draft)
    check("E-1 對純食安用詞違規的草稿判定 PASS（不誤判，證明是兩份清單）", e1_on_food_safety.passed)


def main() -> None:
    print("seo_publish_gate.py F-1 食安/法規紅線用詞 gate 測試")
    test_food_safety_words_are_a_separate_list_from_brand_words()
    test_gluten_free_chinese_is_caught()
    test_gluten_free_english_case_insensitive_is_caught()
    test_other_food_safety_terms_are_caught()
    test_clean_draft_passes_f1()
    test_f1_does_not_flag_brand_voice_words_and_vice_versa()

    print()
    if FAILED:
        print(f"❌ {len(FAILED)} 項失敗：")
        for f in FAILED:
            print(f"   - {f}")
        sys.exit(1)
    print("✅ 全部通過")


if __name__ == "__main__":
    main()
