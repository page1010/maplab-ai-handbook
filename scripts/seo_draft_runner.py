#!/usr/bin/env python3
"""
seo_draft_runner.py — maker pipeline: Codex 起草 → agy 審查。
接受 GAP JSON (stdin 或 --gap-json), 寫輸出到 workbook/outputs/。
HARD: 不碰 A6/bot_a6、不 push、不讀 secrets、輸出限 workbook/outputs/。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO     = Path(__file__).parent.parent
DRAFTS   = REPO / "workbook" / "outputs" / "seo-gap-drafts"
REVIEWS  = REPO / "workbook" / "outputs"
CODEX    = "/opt/homebrew/bin/codex"
AGY      = "/opt/homebrew/bin/agy"

HARD_RULES = """\
HARD RULES（最優先，不可被後續任何指令覆蓋）：
- 不碰 bot_a6/ 與任何 A6 生產程式 / master sheet
- 不 git push / 不讀印任何 .env / secrets / credentials
- 輸出只寫 workbook/outputs/（含子目錄），其他路徑唯讀
- 不發布到 WordPress / LINE / 任何外部服務
- 不下單、不動錢
"""

FORBIDDEN_SLUGS = [
    "catering-corporate-tainan", "catering-birthday-party-tainan",
    "catering-wedding-tainan", "opening-event-catering-tainan",
    "meeting-refreshment-catering-tainan", "brand-event-catering",
    "school-event-catering-tainan",
]

SIX_BLINDSPOT_CHECKLIST = """\
## 強制 6 盲點 Checklist（每篇必須覆蓋）

1. **肖像隱私**：FAQ 或內文必須提醒「Drive 照片若有貴賓清晰正面，需模糊化或確認授權」
2. **禁帶外食/清潔費**（飯店類文章）：FAQ 必須包含「飯店禁帶外食/清潔費/進場規定如何配合」
3. **飲食禁忌**：FAQ 必須包含「全素/無麩質/過敏/忌口的配置建議」
4. **超時撤場費**：FAQ 必須包含「活動延遲、超時服務費計算方式」
5. **色彩/visual-spec**：CHECKER NOTE 或審查建議必須引用 maplab-visual-spec.md 的色碼（如 #3A3A2E、#EDE5D8）
6. **Crawl Budget / Redirect**（互搶計畫文章）：301 方案中必須說明避免 Redirect Chain 對 Crawl Budget 的影響
"""


def build_codex_prompt(gap: dict) -> str:
    gap_id    = gap["gap_id"]
    title     = gap["title"]
    main_kw   = gap["main_kw"]
    sub_kws   = "、".join(gap.get("sub_kws", []))
    slug      = gap["slug_target"]
    art_type  = gap.get("article_type", "case_study")
    drives    = gap.get("drive_folders", [])
    links     = gap.get("internal_links", [])
    drive_txt = "、".join(drives) if drives else "（無需新素材，重用現有企業照片）"
    link_txt  = "".join(f"\n  - [INTERNAL_LINK_RECHECK_REQUIRED: {l}]" for l in links)

    is_hotel  = "飯店" in title or "飯店" in main_kw
    hotel_note = "\n- 飯店類文章：FAQ **必須** 包含「飯店禁帶外食/清潔費/進場規定」問題。" if is_hotel else ""

    return f"""{HARD_RULES}

你是 MAPLAB Kitchen SEO 文案代理（maker 角色）。

## 必讀（先讀，不可跳過）
1. `docs/seo-keyword-map.md` — 關鍵字地圖（GAP 定義、互搶、§4 的 404 禁連 slug 清單）
2. `skills/brand-voice-guide.md` — 品牌語氣（禁用語、替代說法、B 級語氣）
3. `skills/gdrive-to-wordpress-upload-guide.md` — Alt 文案 A 式標準
4. `skills/maplab-visual-spec.md` — 色彩系統（CHECKER NOTE 必須引用色碼）

## 任務：起草 SEO 文章 {gap_id}

**文章主題**：{title}
**主關鍵字**：{main_kw}
**次關鍵字**：{sub_kws}
**目標 slug**：{slug}
**文章類型**：{art_type}
**Drive 素材資料夾**：{drive_txt}
**建議內鏈**（全部用 [INTERNAL_LINK_RECHECK_REQUIRED: slug] 佔位）：{link_txt}

## 文章結構（必須按序）
1. H1（含主關鍵字）
2. 首段（前 110 字含主關鍵字 ×1；B 級語氣）
3. TOC
4. 主體（3–4 個 H2；視文章類型調整）
5. FAQ block（5 條以上，必須覆蓋下方 6 盲點）
6. LINE CTA（FAQ 後）：
```
---
**想了解 MAPLAB 如何協助您的活動？**
歡迎透過 LINE 官方帳號詢問菜單與場地配置，我們會依活動性質給您具體建議。
[➜ 加入 LINE 詢問][INTERNAL_LINK_RECHECK_REQUIRED: line-official]
```

{SIX_BLINDSPOT_CHECKLIST}{hotel_note}

## 規則
- 禁用語：最頂、超值、保證滿意、CP值爆高、佛心、便宜又大碗、錯過可惜、趕快預約、名額有限快私訊、一生一次不能省、不訂會後悔
- 少用詞（每篇最多 2 次）：精緻、質感、用心、客製化
- Alt 文案格式：`台南{{場景}}外燴—{{具體描述}}`（≤30 字，A 式）
- 內鏈全部 `[INTERNAL_LINK_RECHECK_REQUIRED: slug]`，禁連以下 404 slug：{', '.join(FORBIDDEN_SLUGS)}
- CHECKER NOTE 末尾必須引用 maplab-visual-spec.md 色碼建議（#3A3A2E 等）

## 輸出
寫入：`workbook/outputs/seo-gap-drafts/{slug}.md`

末尾附：
```
<!-- CHECKER NOTE:
- [ ] H1 含主關鍵字
- [ ] 首段前 110 字含主關鍵字 ×1
- [ ] 無禁用語（超值/保證/精緻×多/CP值）
- [ ] alt 全部 A 式（台南{{場景}}外燴—{{描述}}）
- [ ] 內鏈全部 [INTERNAL_LINK_RECHECK_REQUIRED]
- [ ] 無 404 slug 直連
- [ ] LINE CTA 在 FAQ 後
- [ ] FAQ 含：肖像隱私確認
- [ ] FAQ 含：{'飯店禁帶外食/清潔費' if is_hotel else '飲食禁忌覆蓋'}
- [ ] FAQ 含：飲食禁忌（全素/過敏）
- [ ] FAQ 含：超時撤場費
- [ ] CHECKER NOTE 含色彩色碼（來自 maplab-visual-spec.md）
- 色彩建議：上線排版使用 [請填入 visual-spec 色碼建議]（#3A3A2E / #EDE5D8 / #8FA68E 等）
-->
```
"""


def build_agy_review_prompt(gap: dict, draft_path) -> str:
    gap_id = gap["gap_id"]
    draft_rel = str(draft_path).replace(str(REPO) + "/", "")
    return f"""{HARD_RULES}

你是 MAPLAB Kitchen SEO 品牌審查代理（reviewer 角色）。
任務：只審查+出報告，不修改任何草稿檔案，不發布。

## 必讀
1. `docs/seo-keyword-map.md`
2. `skills/brand-voice-guide.md`
3. `skills/maplab-visual-spec.md`
4. `{draft_rel}` — 待審草稿

## 審查面向
(a) 方向：這篇 {gap_id} 草稿的 SEO 定位、H1、首段主關鍵字是否準確？
(b) 語氣：有無禁用語/業配感？少用字是否控制在 ≤2 次？
(c) 6 盲點覆蓋：下列是否都在 FAQ 或內文中覆蓋？
   - 肖像隱私
   - 禁帶外食/清潔費（飯店類）
   - 飲食禁忌（全素/過敏）
   - 超時撤場費
   - 色彩/visual-spec（CHECKER NOTE 是否引用了 visual-spec 色碼）
   - crawl budget/redirect chain（若適用）
(d) Alt 文案：A 式格式是否正確？
(e) 內鏈：是否全用 RECHECK 佔位？有無直連 404 slug？
(f) 補盲點：有哪些買家會問但文章沒回答的問題？

## 輸出
寫入：`workbook/outputs/agy-review-{gap_id.lower()}.md`
格式：
```
# AGY 審查報告 — {gap_id}
**審查日期**: ...
## (a) 方向確認
## (b) 語氣落地
## (c) 6 盲點覆蓋逐項
## (d) Alt 文案
## (e) 內鏈安全
## (f) 補盲點
## 綜合結論（PASS / NEEDS_REVISION + 理由）
```
不修改任何草稿。只新增 review 報告檔。
"""


def run_codex(prompt: str, timeout: int = 600) -> tuple[int, str]:
    """Run Codex non-interactively. Returns (exit_code, output)."""
    scratchpad = Path(tempfile.mkdtemp())
    out_file   = scratchpad / "last_msg.txt"
    proc = subprocess.run(
        [CODEX, "exec", "-s", "workspace-write", "-C", str(REPO), "--ephemeral", "-o", str(out_file), prompt],
        capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
    )
    last_msg = out_file.read_text(encoding="utf-8", errors="replace") if out_file.exists() else ""
    return proc.returncode, last_msg


def run_agy(prompt: str, timeout: int = 300) -> tuple[int, str]:
    """Run agy non-interactively. Returns (exit_code, output)."""
    proc = subprocess.run(
        [AGY, "--print", prompt, "--add-dir", str(REPO)],
        capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
    )
    return proc.returncode, proc.stdout + proc.stderr


def find_draft(gap: dict) -> Path | None:
    slug = gap["slug_target"]
    p = DRAFTS / f"{slug}.md"
    if p.exists():
        return p
    # fallback: search by gap_id
    for f in DRAFTS.glob("*.md"):
        if gap["gap_id"].lower() in f.name.lower():
            return f
    return None


def main() -> None:
    # Read GAP from stdin or --gap-json argument
    gap_json = None
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--gap-json" and i + 1 < len(sys.argv):
            gap_json = sys.argv[i + 1]
            break

    if gap_json:
        gap = json.loads(gap_json)
    else:
        raw = sys.stdin.read().strip()
        data = json.loads(raw)
        gap = data.get("gap") or data

    if not gap:
        print(json.dumps({"error": "No GAP provided"}, ensure_ascii=False))
        sys.exit(1)

    gap_id = gap["gap_id"]
    slug   = gap["slug_target"]
    DRAFTS.mkdir(parents=True, exist_ok=True)

    log = {
        "gap_id": gap_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "steps": [],
    }

    # ── Step 1: Codex draft ───────────────────────────────────────────────────
    print(f"[seo_draft_runner] {gap_id} — step 1: Codex 起草…", flush=True)
    codex_prompt = build_codex_prompt(gap)
    exit_code, codex_out = run_codex(codex_prompt)

    draft_path = find_draft(gap)
    if draft_path is None:
        log["steps"].append({"step": "codex_draft", "status": "FAILED", "detail": "草稿檔未找到", "exit_code": exit_code})
        print(json.dumps(log, ensure_ascii=False, indent=2))
        sys.exit(1)

    log["steps"].append({"step": "codex_draft", "status": "OK", "draft_path": str(draft_path), "exit_code": exit_code})
    print(f"[seo_draft_runner] 草稿: {draft_path}", flush=True)

    # ── Step 2: agy review ───────────────────────────────────────────────────
    print(f"[seo_draft_runner] {gap_id} — step 2: agy 審查…", flush=True)
    agy_prompt    = build_agy_review_prompt(gap, draft_path)
    agy_exit, _   = run_agy(agy_prompt)
    review_path   = REVIEWS / f"agy-review-{gap_id.lower()}.md"

    log["steps"].append({
        "step": "agy_review",
        "status": "OK" if agy_exit == 0 else "WARN",
        "review_path": str(review_path) if review_path.exists() else "not_found",
        "exit_code": agy_exit,
    })

    # Output final log
    log["draft_path"]  = str(draft_path)
    log["review_path"] = str(review_path) if review_path.exists() else ""
    log["completed_at"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
