#!/usr/bin/env python3
"""Build an Extension-style cold-start handoff for Remote Codex or another runtime.

This tool is a file-backed equivalent of MAPLAB Agent Commander. It does not
execute agents or read secrets. It combines:

- chrome-extension/task-modules/index.json
- chrome-extension/task-modules/{ROLE}.json
- recalls/{ROLE}_recall.md (when present)
- CURRENT_STATUS.md
- SYSTEM_DIRECTORY_INDEX.md
- workbook/system_index/system_relation_index.csv

The output is a platform-neutral Markdown prompt that can be passed to Codex,
Claude Code, Gemini, OpenClaw, Hermes, or Antigravity.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
MODULE_INDEX = ROOT / "chrome-extension/task-modules/index.json"
MODULE_DIR = ROOT / "chrome-extension/task-modules"
RELATION_INDEX = ROOT / "workbook/system_index/system_relation_index.csv"
SYSTEM_DIRECTORY = ROOT / "SYSTEM_DIRECTORY_INDEX.md"
CURRENT_STATUS = ROOT / "CURRENT_STATUS.md"
RECALL_DIR = ROOT / "recalls"
INVESTMENT_OS_ROOT = Path("/Users/pagemacmini/investment-os")

RUNTIME_LABELS = {
    "codex": "Codex / Remote Codex",
    "claude_code": "Claude Code",
    "gpt": "GPT / ChatGPT",
    "antigravity": "Antigravity",
    "gemini": "Gemini",
    "openclaw": "OpenClaw",
    "hermes": "Hermes",
}


@dataclass(frozen=True)
class Route:
    role: str
    label: str
    keywords: tuple[str, ...]


ROUTES: tuple[Route, ...] = (
    Route("A0", "A0 總調度秘書", ("dispatch", "調度", "跨系統", "owner", "全局", "協調", "派工")),
    Route("A1", "A1 系統總管", ("system", "governance", "repo", "extension", "module", "index", "系統", "治理", "全貌", "索引", "關聯", "冷啟動", "debug", "版本")),
    Route("A2", "A2 搜尋流量作戰部", ("seo", "wordpress", "gsc", "rank math", "關鍵字", "官網", "文章", "搜尋")),
    Route("A3", "A3 社群與廣告成長部", ("ads", "meta", "facebook", "instagram", "廣告", "社群", "roas", "gtm", "pixel")),
    Route("A4", "A4 影像資產整理部", ("photo", "image", "asset", "圖片", "照片", "素材", "alt", "相簿")),
    Route("A5", "A5 報價與提案引擎", ("quotation", "quote", "報價", "菜單", "成本", "毛利", "items", "proposal")),
    Route("A6", "A6 業務快反應部隊", ("sales", "telegram", "急件", "業務", "回覆", "casequote", "linecases")),
    Route("A7", "A7 客服與對話轉單部", ("customer", "service", "faq", "客服", "對話", "line", "補問", "轉單")),
    Route("A8", "A8 影音內容產線", ("video", "reel", "shorts", "影片", "短影音", "剪輯", "higgsfield")),
    Route("B1", "B1 Investment OS Builder", ("build", "implement", "feature", "bug", "修復", "功能", "實作", "runtime")),
    Route("B2", "B2 Investment OS Reviewer", ("review", "freshness", "dataflow", "驗證", "審查", "資料流", "錯誤", "證據")),
    Route("B3", "B3 Investment OS Archivist", ("archive", "handoff", "resume", "version", "交接", "存檔", "版本", "紀錄")),
    Route("B4", "B4 Investment OS System Patrol", ("patrol", "fit", "refactor", "方向", "巡查", "暫停", "過度建置", "重構")),
    Route("B5", "B5 Shadow Distillation", ("distill", "recall", "teaching", "蒸餾", "召回", "教材", "能力盤點")),
    Route("IOS-MOMENTUM", "IOS-MOMENTUM 每日動能經理", ("momentum", "動能", "強勢", "成交量", "漲停", "股期")),
    Route("IOS-KOL", "IOS-KOL 網紅雷達經理", ("kol", "influencer", "youtube", "podcast", "網紅", "逐字稿")),
    Route("IOS-FB", "IOS-FB 社群情報經理", ("fb radar", "facebook", "fb", "粉專", "社群情報")),
    Route("IOS-ALPHA", "IOS-ALPHA 阿爾法共振經理", ("alpha", "convergence", "共振", "阿爾法", "polymarket", "reddit")),
    Route("IOS-BLACKSWAN", "IOS-BLACKSWAN 黑天鵝監控官", ("black swan", "黑天鵝", "tail risk", "崩盤", "戰爭", "vix")),
    Route("IOS-INVENTORY", "IOS-INVENTORY 庫存審查經理", ("inventory", "position", "holding", "庫存", "持股", "部位", "保證金")),
    Route("IOS-MACRO", "IOS-MACRO 總經大師", ("macro", "fred", "cpi", "利率", "總經", "景氣", "殖利率")),
    Route("IOS-CHIP", "IOS-CHIP 籌碼經理", ("chip", "籌碼", "法人", "融資", "融券", "集保")),
    Route("IOS-LEFT", "IOS-LEFT 左側預期差經理", ("left side", "左側", "預期差", "非共識", "買前功課")),
    Route("IOS-RIGHT", "IOS-RIGHT 右側交易經理", ("right side", "右側", "突破", "交易劇本", "執行")),
    Route("IOS-EVIDENCE", "IOS-EVIDENCE 研究證據經理", ("evidence", "source", "證據", "來源", "推論", "已驗證事實")),
    Route("IOS-SIM", "IOS-SIM 模擬倉經理", ("simulation", "模擬倉", "模擬單", "ledger", "shioaji simulation")),
    Route("IOS-FAMILY", "IOS-FAMILY 家族基金經理", ("family fund", "家族基金", "資金池", "account level")),
    Route("IOS-HEDGE", "IOS-HEDGE 盤後對沖經理", ("hedge", "對沖", "夜盤", "盤後", "海外期貨")),
    Route("IOS-SURFACE", "IOS-SURFACE 介面契約守門員", ("surface", "format", "介面", "格式", "telegram ux", "dashboard ux")),
    Route("IOS-HYGIENE", "IOS-HYGIENE 系統衛生官", ("hygiene", "cleanup", "dirty", "worktree", "系統衛生", "清掃", "髒檔")),
    Route("IOS-SELL", "IOS-SELL 實單哨兵", ("sell", "position sentinel", "賣出", "止損", "實單哨兵")),
)


def fail(message: str, code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON {path}: {exc}")


def read_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default


def normalize_task(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def auto_route(task: str, available_roles: set[str]) -> tuple[str, list[tuple[str, int]]]:
    normalized = normalize_task(task)
    scores: list[tuple[str, int]] = []
    for route in ROUTES:
        if route.role not in available_roles and not (MODULE_DIR / f"{route.role}.json").exists():
            continue
        score = sum(1 for keyword in route.keywords if keyword in normalized)
        scores.append((route.role, score))
    scores.sort(key=lambda item: (-item[1], item[0]))
    if not scores or scores[0][1] <= 0:
        fallback = "B4" if "B4" in available_roles else "A1"
        return fallback, scores[:5]
    return scores[0][0], scores[:5]


def load_module_index() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    index = load_json(MODULE_INDEX)
    modules = {str(item.get("role_id")): item for item in index.get("modules", [])}
    return index, modules


def load_role_module(role: str, entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    path_value = entries.get(role, {}).get("path") or f"chrome-extension/task-modules/{role}.json"
    return load_json(ROOT / path_value)


def role_matches(value: str, role: str) -> bool:
    tokens = {item.strip() for item in value.split(";") if item.strip()}
    if role in tokens:
        return True
    if role.startswith("IOS-") and "ALL-IOS" in tokens:
        return True
    return False


def load_relation_rows(role: str) -> list[dict[str, str]]:
    try:
        with RELATION_INDEX.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except FileNotFoundError:
        fail(f"missing relation index: {RELATION_INDEX}")
    return [row for row in rows if role_matches(row.get("used_by_roles", ""), role)]


def parse_status(md: str) -> dict[str, Any]:
    result: dict[str, Any] = {"version": "?", "phase": "?", "critical": [], "active": [], "blockers": []}
    section = ""
    for line in md.splitlines():
        stripped = line.strip()
        if stripped.startswith("- **Version**:"):
            result["version"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- **Phase**:"):
            result["phase"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("## "):
            section = stripped.lower()
        elif stripped.startswith("|") and "task" not in stripped.lower() and "---" not in stripped:
            cols = [col.strip() for col in stripped.split("|") if col.strip()]
            if len(cols) >= 4 and ("進行中" in section or "current" in section):
                item = " | ".join(cols[:4])
                if "critical" in item.lower() or "🔴" in item:
                    result["critical"].append(item)
                elif "🔄" in item:
                    result["active"].append(item)
        elif "blocker" in section and stripped.startswith("-"):
            result["blockers"].append(stripped.lstrip("- "))
    return result


def existing_source_state(path_text: str) -> str:
    if not path_text or path_text.startswith("http"):
        return "external"
    path = ROOT / path_text
    return "ok" if path.exists() else "missing_or_external"


def format_relation_rows(rows: Iterable[dict[str, str]]) -> str:
    lines: list[str] = []
    for row in rows:
        lines.extend(
            [
                f"### {row.get('source_id')} — {row.get('title')}",
                f"- source_type: {row.get('source_type')}",
                f"- path_or_id: {row.get('path_or_id')}",
                f"- canonical_status: {row.get('canonical_status')}",
                f"- used_by_departments: {row.get('used_by_departments')}",
                f"- used_by_roles: {row.get('used_by_roles')}",
                f"- upstream: {row.get('upstream') or '—'}",
                f"- downstream: {row.get('downstream') or '—'}",
                f"- related_tasks: {row.get('related_tasks') or '—'}",
                f"- related_loops: {row.get('related_loops') or '—'}",
                f"- sensitivity: {row.get('sensitivity') or 'unknown'}",
                f"- last_verified: {row.get('last_verified') or 'unknown'}",
                f"- notes: {row.get('notes') or '—'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def runtime_instruction(runtime: str) -> list[str]:
    mapping = {
        "codex": [
            "你正在 Remote Codex／Codex 執行。可讀 repo、修改本 branch、跑測試並留下 review bundle。",
            "先確認 branch、git status、兩個 repo 與工具能力；不得讀 secrets 或直接修改 main。",
        ],
        "claude_code": [
            "你正在 Claude Code terminal 執行。請以本機 repo 與 live readback 為準。",
            "修改需留下驗證 receipt；跨系統行動先確認 credential route 與 approval boundary。",
        ],
        "gpt": [
            "你正在 GPT／ChatGPT 做高判斷研究與第二意見。輸出是 evidence／draft，不是 runtime 完成聲明。",
            "無法讀本機、Drive 或 UI 時明確標記 unknown。",
        ],
        "antigravity": [
            "你正在 Antigravity 做 80/20 簡化、Google／瀏覽器可見狀態與第二意見。",
            "沒有登入態時不得把舊資料假裝成 live；不得要求或暴露 secrets。",
        ],
        "gemini": [
            "你正在 Gemini 做 Google 生態、表格、文件與長上下文分析。",
            "若無本機 repo access，使用 linked sources 並清楚列缺資料。",
        ],
        "openclaw": [
            "你正在 OpenClaw 做 bounded browser/operator evidence。",
            "不決定策略、不發布、不改正式真相源；高風險動作需 Owner／A1 批准。",
        ],
        "hermes": [
            "你正在 Hermes 做 cold-path 摘要、question pack、巡查 reaction 與下一步整理。",
            "輸出必須讓 A1／Codex／B-role 可驗證後整合。",
        ],
    }
    return mapping.get(runtime, mapping["codex"])


def build_handoff(task: str, role: str, runtime: str, module: dict[str, Any], relations: list[dict[str, str]], status: dict[str, Any], route_scores: list[tuple[str, int]]) -> str:
    recall_path = RECALL_DIR / f"{role}_recall.md"
    recall = read_text(recall_path).strip() or str(module.get("packaged_role_recall_excerpt") or "").strip()
    read_first = module.get("read_first", [])
    skills = module.get("skill_group", [])
    affects = module.get("affects", [])
    output_contract = module.get("output_contract", [])
    forbidden = module.get("forbidden_actions", [])
    verification = module.get("verification_required", [])

    lines: list[str] = [
        f"# MAPLAB {role} Extension-style Runtime Handoff",
        "",
        f"runtime_target: {runtime}",
        f"runtime_target_label: {RUNTIME_LABELS.get(runtime, runtime)}",
        f"role_id: {role}",
        f"role_name: {module.get('role_name', '?')}",
        f"department: {module.get('department', '?')}",
        f"module_id: {module.get('module_id', '?')}",
        f"module_generated_at: {module.get('generated_at', '?')}",
        f"canonical_maplab_repo: {ROOT}",
        f"canonical_investment_os_repo: {INVESTMENT_OS_ROOT}",
        "",
        "## 0. 本次召喚任務",
        task,
        "",
        "## 1. Runtime 使用邊界",
    ]
    lines.extend(f"- {item}" for item in runtime_instruction(runtime))
    lines.extend(
        [
            "",
            "## 2. 自動選角結果",
            f"- selected_role: {role}",
            "- top_route_scores: " + ", ".join(f"{r}:{score}" for r, score in route_scores),
            "- 若角色不合理，先用索引與 task module 證據改派，不要靜默換角色。",
            "",
            "## 3. 全貌冷啟動順序（不得跳步）",
            f"1. `{SYSTEM_DIRECTORY.relative_to(ROOT)}` — 全局導航與部門／角色反向索引",
            f"2. `{RELATION_INDEX.relative_to(ROOT)}` — 篩選 `{role}` 的來源、upstream、downstream、credential、loop",
            "3. `CURRENT_STATUS.md` — MAPLAB 最新治理狀態",
            "4. `/Users/pagemacmini/investment-os/CURRENT_STATE.md` — 若任務涉及 Investment OS",
            f"5. `chrome-extension/task-modules/{role}.json` — 角色任務 envelope",
            f"6. `recalls/{role}_recall.md` — 角色身份與靜態規則（如存在）",
            "7. Task Card／review bundle／pitfall — 找接續點與過去 incident",
            "8. Drive metadata／runtime readback — 只有任務需要時才讀 live operational facts",
            "",
            "## 4. 即時狀態摘要",
            f"- MAPLAB version: {status.get('version')}",
            f"- MAPLAB phase: {status.get('phase')}",
            f"- critical: {status.get('critical')[:5] or ['none parsed']}",
            f"- active: {status.get('active')[:8] or ['none parsed']}",
            f"- blockers: {status.get('blockers')[:5] or ['none parsed']}",
            "- 以上是文件摘要；涉及『現在是否在線』仍需 live readback。",
            "",
            "## 5. 本角色關聯來源",
            format_relation_rows(relations) or "- relation_index_gap=true",
            "",
            "## 6. Role Module 必讀來源",
        ]
    )
    for item in read_first:
        path = str(item.get("path", ""))
        lines.append(
            f"- [{existing_source_state(path)}] `{path}` — {item.get('purpose') or item.get('load_mode') or 'source'}"
        )
    lines.extend(["", "## 7. 必拿技能"])
    base_skills = [
        "skills/system-directory-index/SKILL.md",
        "skills/task-progress-guide.md",
        "skills/session-lifecycle/SKILL.md",
        "skills/superpowers-guide.md",
    ]
    seen: set[str] = set()
    for skill in [*base_skills, *map(str, skills)]:
        if skill and skill not in seen:
            seen.add(skill)
            lines.append(f"- `{skill}`")

    lines.extend(["", "## 8. 角色召回摘要", recall or "[recall missing — use module fields and mark gap]"])
    lines.extend(["", "## 9. 影響範圍"])
    lines.extend(f"- {item}" for item in affects) if affects else lines.append("- 依 relation index 的 downstream 判斷")
    lines.extend(["", "## 10. 預期產出"])
    lines.extend(f"- {item}" for item in output_contract) if output_contract else lines.append("- review bundle + validation receipt + handoff")
    lines.extend(["", "## 11. 禁止事項"])
    common_forbidden = [
        "不得讀或輸出 .env、password、token、cookie、OTP、API key value。",
        "不得把 generated index 當作 live truth。",
        "不得要求 Owner 提供自己可從索引、GitHub 或 Drive metadata 找到的檔案位置。",
    ]
    for item in [*common_forbidden, *map(str, forbidden)]:
        lines.append(f"- {item}")
    lines.extend(["", "## 12. 驗證要求"])
    for item in verification:
        lines.append(f"- {item}")
    if not verification:
        lines.extend(
            [
                "- 跑最小可證明測試。",
                "- owner-facing surface 需 readback／smoke，而非只看 log。",
                "- 驗證結果寫入 review bundle／Task Card／handoff。",
            ]
        )

    lines.extend(
        [
            "",
            "## 13. 啟動輸出（先回覆後直接執行）",
            "請先輸出以下 Startup Check；任務清楚且無高風險 blocker 時，輸出後直接繼續，不要等待 Owner 重複確認：",
            "",
            "```text",
            "Startup Check",
            f"- Role: {role}",
            f"- Department: {module.get('department', '?')}",
            "- Task:",
            "- Files read:",
            "- Directory index rows:",
            "- Canonical sources:",
            "- Upstream dependencies:",
            "- Downstream consumers:",
            "- Drive operational sources:",
            "- Credential routes:",
            "- Related incidents / pitfalls:",
            "- Skills loaded:",
            "- Test plan:",
            "- Receipt path:",
            "- Risks / ambiguities:",
            "- High-risk approvals required:",
            "- Proposed scope:",
            "```",
            "",
            "## 14. 執行與複利格式",
            "每個重要發現使用 What／So What／Now What。",
            "完成後輸出 Index Loop Back：下一個 Agent 是否找得到、角色關聯是否更新、是否新增 prevention、Owner 負擔是否下降。",
            "",
            "現在開始：先讀全局索引與本角色匹配列，輸出 Startup Check，然後直接執行任務。",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="The task to route and package.")
    parser.add_argument("--role", default="AUTO", help="Explicit role id or AUTO.")
    parser.add_argument("--runtime", default="codex", choices=sorted(RUNTIME_LABELS))
    parser.add_argument("--output", type=Path, help="Write Markdown handoff to this path; stdout otherwise.")
    parser.add_argument("--explain-route", action="store_true", help="Print route candidates to stderr.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not SYSTEM_DIRECTORY.exists():
        fail(f"missing system directory index: {SYSTEM_DIRECTORY}")
    index, entries = load_module_index()
    available_roles = set(entries)
    role = args.role.strip().upper()
    route_scores: list[tuple[str, int]] = []
    if role == "AUTO":
        role, route_scores = auto_route(args.task, available_roles)
    else:
        route_scores = [(role, -1)]
    module = load_role_module(role, entries)
    relations = load_relation_rows(role)
    status = parse_status(read_text(CURRENT_STATUS))
    handoff = build_handoff(args.task, role, args.runtime, module, relations, status, route_scores)
    if args.explain_route:
        print("route candidates:", route_scores, file=sys.stderr)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(handoff, encoding="utf-8")
        print(args.output)
    else:
        sys.stdout.write(handoff)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
