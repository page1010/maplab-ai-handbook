#!/usr/bin/env python3
"""Build MAPLAB dynamic role task modules for Chrome/Gemini/Codex/OpenClaw.

This generator deliberately writes data/config artifacts, not executable remote
Chrome logic. Chrome MV3 blocks remote JS execution, so GitHub is treated as the
source of task manifests, role context, relationship maps, and output contracts.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).replace(microsecond=0).isoformat()

MODULE_DIR = ROOT / "chrome-extension" / "task-modules"
CONFIG_DIR = ROOT / "chrome-extension" / "config"
DOCS_DIR = ROOT / "docs" / "extension"
WORKBOOK_DIR = ROOT / "workbook" / "task_modules"
TASK_CARD_PATH = ROOT / "handoff" / "tasks" / "T-A1-EXT-001-dynamic-role-modules.md"


COMMON_READ_FIRST = [
    "CURRENT_STATUS.md",
    "AGENT_RULES.md",
    "AGENT_STARTUP_PROTOCOL.md",
    "pitfalls.md",
    "TASK_QUEUE.md",
    "workbook/task_index.json",
    "AGENT_RECALL_PROMPTS.md",
    "skills/superpowers-guide.md",
    "skills/task-progress-guide.md",
]

COMMON_GOVERNANCE = [
    "docs/openclaw/output-contract.md",
    "docs/openclaw/relation-graph.md",
    "docs/openclaw/security-boundaries.md",
    "workbook/reviews/README.md",
]

CODE_SURFACES = [
    {
        "id": "chrome-extension",
        "paths": [
            "chrome-extension/manifest.json",
            "chrome-extension/popup.html",
            "chrome-extension/popup.js",
            "chrome-extension/CHANGELOG.md",
            "chrome-extension/task-modules/index.json",
            "chrome-extension/config/task-modules.json",
        ],
        "impact": "Owner side panel entrypoint; role selection; GitHub dynamic data loading; Gemini/Codex/OpenClaw handoff prompt generation.",
    },
    {
        "id": "ai-workbook",
        "paths": [
            "tools/ai_workbook/cli.py",
            "tools/ai_workbook/build_context_pack.py",
            "tools/ai_workbook/create_microtask.py",
            "tools/ai_workbook/relation_graph.py",
            "tools/ai_workbook/openclaw_adapter.py",
            "workbook/relation_graph.json",
        ],
        "impact": "Turns role modules into review bundles, context packs, microtasks, and relation graph records.",
    },
    {
        "id": "a6-openclaw-runtime",
        "paths": [
            "bot_a6/bot_a6.py",
            "bot_a6/openclaw_dispatch.py",
            "docs/openclaw/dispatch-role.md",
            "docs/openclaw/closed-loop-playbook.md",
            "docs/openclaw/memory-governance.md",
        ],
        "impact": "Telegram/A6 route should dispatch short work packages to OpenClaw, not fall back to old Claude-only flows.",
    },
    {
        "id": "a2a3-workbench",
        "paths": [
            "automation/seo_factory/build_a2a3_workbench.py",
            "automation/seo_factory/seo_factory.py",
            "docs/a2a3/handoff-board.html",
            "docs/a2a3/launchpad.html",
            "docs/a2a3/openclaw-dispatch-pack.md",
            "docs/a2a3/rankmath-keyword-recovery-2026-05-11.md",
        ],
        "impact": "SEO/ads work packages, Rank Math recovery tasks, launchpad links, and public/internal content boundaries.",
    },
]


@dataclass
class RoleModule:
    role_id: str
    role_name: str
    department: str
    role_simulation: str
    task_types: list[str]
    project_docs: list[str]
    skills: list[str]
    runtime_targets: list[str] = field(default_factory=lambda: ["gemini", "codex", "openclaw"])
    restricted_sources: list[str] = field(default_factory=list)
    output_contract: list[str] = field(default_factory=list)
    startup_contract_extra: list[str] = field(default_factory=list)
    affects: list[str] = field(default_factory=list)
    recall_path: str | None = None
    risk_level: str = "medium"

    @property
    def module_id(self) -> str:
        safe = self.role_name.upper().replace(" ", "_").replace("/", "_").replace("-", "_")
        return f"MAPLAB_{self.role_id}_{safe}_DYNAMIC_ROLE_MODULE"

    def to_module(self) -> dict[str, Any]:
        recall_path = self.recall_path or f"recalls/{self.role_id}_recall.md"
        read_first = COMMON_READ_FIRST + [recall_path]
        read_first += self.project_docs + self.skills + COMMON_GOVERNANCE
        read_first = dedupe(read_first)
        return {
            "schema_version": "2026-05-11.dynamic-role-module.v1",
            "generated_at": NOW,
            "module_id": self.module_id,
            "role_id": self.role_id,
            "role_name": self.role_name,
            "department": self.department,
            "role_simulation": self.role_simulation,
            "packaged_role_recall_excerpt": read_text_excerpt(ROOT / recall_path),
            "runtime_targets": self.runtime_targets,
            "task_types": self.task_types,
            "read_first": as_source_entries(read_first),
            "restricted_sources": as_source_entries(self.restricted_sources, load_mode="a1_only"),
            "skill_group": self.skills,
            "source_policy": {
                "truth_source": "GitHub repo /Users/pagemacmini/maplab-ai-handbook",
                "live_fact_rule": "For external systems, verify live API/UI facts before using repo notes as current truth.",
                "remote_code_rule": "GitHub dynamic links may load JSON/Markdown task data only; do not execute remote JS in Chrome.",
                "public_output_rule": "Public drafts must not include prices, internal dates, local file:// paths, or secrets.",
                "markdown_refresh_rule": "Role modules are routing envelopes. Runtimes must read linked Markdown/JSON sources live from GitHub raw; source hashes detect when a module envelope needs regeneration.",
            },
            "source_freshness": {
                "generated_from": "local canonical repo",
                "hash_algorithm": "sha256",
                "refresh_command": "python3 tools/ai_workbook/build_extension_task_modules.py",
                "rule": "If any source_sha256 differs from the current GitHub raw content, regenerate task modules before relying on routing metadata.",
            },
            "startup_contract": [
                f"Confirm: I am {self.role_id} {self.role_name}.",
                "Read CURRENT_STATUS.md first, then role recall, then only the sources listed in this module.",
                "State the current task, expected output path, affected roles, and unresolved blockers before acting.",
            ]
            + self.startup_contract_extra,
            "output_contract": self.output_contract
            or [
                "task_summary.md",
                "output.md or output.json",
                "relation_update.json",
                "review_request.md",
            ],
            "writeback": {
                "default_review_bundle": "workbook/reviews/JOB-xxx/",
                "task_module_graph": "workbook/task_modules/role_module_relation_graph.json",
                "task_card": str(TASK_CARD_PATH.relative_to(ROOT)),
                "status_rule": "Update CURRENT_STATUS.md only for major status changes; otherwise write a review bundle or task output first.",
            },
            "affects": self.affects,
            "forbidden_actions": [
                "Do not publish WordPress content without Owner approval.",
                "Do not push main or overwrite truth sources unless the task explicitly allows it.",
                "Do not read secrets/.env/API keys unless the module marks the source as a1_only and the Owner has approved the operation.",
                "Do not treat old repo notes as live facts when APIs/UI can be checked.",
            ],
            "verification_required": [
                "List source files actually read.",
                "List outputs created and exact paths.",
                "List affected agents/tasks/files.",
                "Produce review bundle or explain why no bundle was needed.",
            ],
            "risk_level": self.risk_level,
        }


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def as_source_entries(paths: list[str], load_mode: str = "read") -> list[dict[str, str]]:
    entries = []
    for path in paths:
        p = ROOT / path
        item_load_mode = load_mode
        purpose = classify_source(path)
        source_sha256 = file_sha256(p) if p.exists() else ""
        size_bytes = str(p.stat().st_size) if p.exists() else ""
        if path == "TASK_QUEUE.md" and not p.exists():
            item_load_mode = "fallback_to_workbook_task_index"
            purpose = "legacy task queue listed in CURRENT_STATUS; missing in canonical repo, use workbook/task_index.json"
        entries.append(
            {
                "path": path,
                "load_mode": item_load_mode,
                "exists": str(p.exists()).lower(),
                "purpose": purpose,
                "source_sha256": source_sha256,
                "size_bytes": size_bytes,
            }
        )
    return entries


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text_excerpt(path: Path, limit: int = 8000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n\n[truncated: {len(text) - limit} chars omitted]"


def classify_source(path: str) -> str:
    if path.startswith("recalls/"):
        return "role recall prompt"
    if path.startswith("skills/"):
        return "skill / operating guide"
    if path.startswith("projects/"):
        return "project context"
    if path.startswith("docs/"):
        return "governance or workflow document"
    if path.startswith("automation/") or path.startswith("tools/") or path.startswith("bot"):
        return "code surface"
    if path.startswith("data/"):
        return "data source"
    if path.startswith("workbook/"):
        return "workbook artifact"
    if path.startswith("handoff/"):
        return "handoff or task card"
    return "core governance"


ROLES = [
    RoleModule(
        "A0",
        "Dispatch Secretary",
        "總調度秘書",
        "跨系統任務調度與 Owner 入口管理者，不直接取代各專業角色。",
        ["dispatch", "owner_briefing", "cross_system_handoff", "status_review"],
        ["docs/a0-dispatch-operations-manual.md", "projects/a0-a1-briefing-protocol.md", "handoff/a0-briefing.md"],
        ["skills/a0-proactive-dispatch-guide.md", "skills/remote-desktop-agent-bridge.md", "skills/mcp-usage-guide.md"],
        ["gemini", "codex", "openclaw", "cowork"],
        affects=["A1", "A2-A8", "B1-B4", "Telegram", "Chrome side panel", "Google Drive/Sheets connectors"],
    ),
    RoleModule(
        "A1",
        "System Orchestrator",
        "系統總管中心",
        "版本治理、模組化、任務閉環、關聯圖與系統修復的工程執行者。",
        ["governance", "repo_edit", "task_module_build", "relation_graph", "runtime_debug"],
        [
            "projects/v6-architecture.md",
            "docs/openclaw/README.md",
            "docs/openclaw/closed-loop-playbook.md",
            "docs/openclaw/memory-governance.md",
            "projects/extension-browser-bridge.md",
        ],
        [
            "skills/extension-agent-summon-guide.md",
            "skills/extension-update",
            "skills/save-checkpoint/SKILL.md",
            "skills/first-principles-check/SKILL.md",
            "skills/pitfalls/SKILL.md",
            "skills/github-api-workflow-guide.md",
        ],
        ["codex", "openclaw", "gemini"],
        affects=["chrome-extension", "tools/ai_workbook", "bot_a6", "CURRENT_STATUS", "handoff/tasks"],
        risk_level="high",
    ),
    RoleModule(
        "A2",
        "Ads SEO WordPress Patrol",
        "搜尋流量作戰部（廣告/SEO/WordPress 巡查）",
        "WordPress/SEO/Ads/品牌記憶巡查者。召喚後先確認品牌價值、品牌語氣、品牌顏色與 live web 狀態，再做 read-only 巡查與安全 repo/proposal 修改。",
        [
            "seo_audit",
            "ads_seo_wordpress_patrol",
            "brand_memory_check",
            "wordpress_live_status",
            "rankmath_recovery",
            "wordpress_draft",
            "internal_linking",
            "schema_planning",
        ],
        [
            "projects/a2-ads-seo-wordpress-patrol.md",
            "projects/seo-ads-agent.md",
            "handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md",
            "docs/a2a3/README.md",
            "docs/a2a3/live-wp-rankmath-fact-check-2026-05-11.md",
            "docs/a2a3/rankmath-keyword-recovery-2026-05-11.md",
            "docs/a2a3/live-wordpress-audit.md",
            "automation/seo_factory/README.md",
            "automation/seo_factory/config/strategy_matrix_rules.json",
            "automation/seo_factory/config/link_policy.json",
        ],
        [
            "skills/seo-session-checklist.md",
            "skills/seo-ranking-evaluation-guide.md",
            "skills/page-checker.md",
            "skills/wp-content-audit/SKILL.md",
            "skills/brand-voice-guide.md",
            "skills/maplab-visual-spec.md",
            "skills/gdrive-to-wordpress-upload-guide.md",
        ],
        restricted_sources=["skills/credentials/wordpress-api.md", "skills/credentials/google-search-console-api.md"],
        output_contract=[
            "ads_seo_wordpress_patrol.md",
            "brand_memory_check.md",
            "wordpress_status_matrix.md",
            "ads_landing_alignment.md",
            "safe_fix_log.md",
            "review_request.md",
        ],
        startup_contract_extra=[
            "Before patrol, answer MAPLAB brand value, brand voice, brand color/visual source, live website state source, and shared MAPLAB/Investment OS culture rules.",
            "Only perform read-only external checks or safe repo/proposal edits unless Owner/A1 approves publishing or ads changes.",
        ],
        affects=[
            "WordPress pages/posts",
            "Rank Math metadata",
            "Google Ads / Meta Ads read-only review",
            "A3 ad landing pages",
            "A4 asset needs",
            "Google indexing workflow",
            "Investment OS-style evidence discipline",
        ],
        risk_level="high",
    ),
    RoleModule(
        "A3",
        "Ads Growth Studio",
        "社群與廣告成長部",
        "Meta/Google Ads 漏斗與素材投放規劃者，必須與 A2 landing pages 對齊。",
        ["ad_campaign_plan", "creative_matrix", "tracking_pixel", "landing_page_alignment", "roi_review"],
        [
            "projects/maplab-ads-monitor.md",
            "projects/seo-ads-agent.md",
            "docs/a2a3/tracking-pack.md",
            "docs/a2a3/b2b-5x5-matrix.md",
            "docs/a2a3/b2b-crosswalk.md",
        ],
        [
            "skills/a3-social-ads-skills.md",
            "skills/brand-voice-guide.md",
            "skills/sheets-tracking-guide.md",
            "skills/verification-checklist-guide.md",
        ],
        restricted_sources=["skills/credentials/meta-ads-api.md", "skills/credentials/google-ads-api.md"],
        output_contract=["campaign_matrix.md", "creative_copy_pack.md", "tracking_requirements.json", "review_request.md"],
        affects=["A2 landing pages", "Meta Ads", "Google Ads", "GTM/Pixel", "A4 creative asset selection"],
        risk_level="high",
    ),
    RoleModule(
        "A4",
        "Photo Archive",
        "影像資產整理部",
        "素材來源與照片分類管理者，負責讓 A2/A3/A6/A8 找得到可信圖片。",
        ["photo_index", "asset_classification", "drive_folder_map", "alt_text_draft", "material_shortlist"],
        ["projects/maplab-pipeline.md", "projects/a2-asset-guide.md", "docs/a4/source-of-truth.md", "docs/a4/drive-map.md", "docs/a4/workflow.md"],
        [
            "skills/a4-photo-asset-skills.md",
            "skills/photo-pipeline-toolkit-guide.md",
            "skills/maplab-visual-spec.md",
            "skills/canva-photo-filter/SKILL.md",
            "skills/image-convert/SKILL.md",
        ],
        restricted_sources=["skills/credentials/google-drive-api.md", "skills/credentials/gemini-api.md"],
        output_contract=["asset_inventory.csv", "source_bridge.md", "photo_shortlist.json", "review_request.md"],
        affects=["A2 WordPress images", "A3 creative packs", "A6 proposal materials", "A8 video pipeline", "Google Drive MAPLAB_ASSETS"],
        risk_level="medium",
    ),
    RoleModule(
        "A5",
        "Quotation Engine",
        "報價與提案引擎部",
        "報價資料、品項、成本毛利與菜單結構的資料管理者。",
        ["quote_data_review", "item_master_update", "pricing_logic", "sheet_schema_check", "proposal_inputs"],
        [
            "projects/maplab-master-data.md",
            "projects/quote-system-v2.md",
            "data/items_master.json",
            "data/quote-terms-reference.md",
            "archive/data/item-master-cross-reference.md",
            "archive/data/item-frequency-top50.md",
            "archive/data/quote_items_deduped.json",
            "handoff/table-relationship-map.md",
        ],
        [
            "skills/a5-quotation-engine-skills.md",
            "skills/items-management/SKILL.md",
            "skills/sheets-data-cleaning-guide.md",
            "skills/sheet-version-restore/SKILL.md",
        ],
        restricted_sources=["skills/credentials/google-sheets-api.md"],
        output_contract=["quote_data_diff.md", "sheet_change_plan.json", "validation_report.md", "review_request.md"],
        affects=["A6 quote workflow", "A7 customer answers", "Google Sheets master data", "Slides quotation system"],
        risk_level="high",
    ),
    RoleModule(
        "A6",
        "Sales Rapid Response",
        "業務快反應部隊",
        "Telegram/OpenClaw 快速任務分派與報價/素材工作包整理者，不做最終發布。",
        ["telegram_dispatch", "openclaw_short_task", "quote_intake", "proposal_draft", "review_bundle"],
        [
            "projects/line-conversation-training.md",
            "projects/dual-bot-architecture.md",
            "projects/quote-system-v2.md",
            "docs/openclaw/dispatch-role.md",
            "docs/openclaw/ads-assistant.md",
            "docs/openclaw/security-boundaries.md",
            "docs/business-requirements/a6-training-methodology.md",
            "docs/business-requirements/a6-usage-scenarios.md",
            "bot_a6/openclaw_dispatch.py",
        ],
        [
            "skills/a6-system-operations.md",
            "skills/a6-sales-rapid-response-skills.md",
            "skills/a6-rapid-quote-sop.md",
            "skills/a6-safety-boundaries.md",
            "skills/a6-telegram-window.md",
            "skills/a6-qa-examples.md",
        ],
        restricted_sources=["skills/credentials/telegram-bot.md", "skills/credentials/line-bot.md"],
        output_contract=["routing.json", "draft.md", "execution_log.json", "verification_log.json", "review_request.md"],
        affects=["Telegram bot", "OpenClaw workspace", "A5 quote data", "A4 materials", "A7 reply handoff"],
        risk_level="high",
    ),
    RoleModule(
        "A7",
        "Service Desk",
        "客服與對話轉單部",
        "客戶詢問分類、標準回覆、補問流程與 A5/A6 轉單接口。",
        ["customer_reply", "faq_flow", "lead_qualification", "handoff_to_quote", "reply_training"],
        ["projects/ai-reply-system.md", "docs/business-requirements/a6-training-methodology.md"],
        ["skills/a7-customer-service-skills.md", "skills/brand-voice-guide.md", "skills/a6-safety-boundaries.md"],
        restricted_sources=["skills/credentials/line-bot.md"],
        output_contract=["reply_template.md", "qualification_flow.json", "handoff_note.md", "review_request.md"],
        affects=["A6 intake", "A5 quote requirements", "LINE/Telegram responses", "A2/A3 FAQ insights"],
        risk_level="medium",
    ),
    RoleModule(
        "A8",
        "Content Repurposing Pipeline",
        "影音內容產線",
        "把 A4/A2/A3 素材與內容轉成多平台影音、短影音與分發稿。",
        ["video_script", "shorts_plan", "podcast_outline", "content_repurpose", "publishing_queue"],
        ["projects/maplab-pipeline.md", "docs/a4/source-of-truth.md"],
        ["skills/a8-video-pipeline-skills.md", "skills/media-limit-workaround.md", "skills/next-three-report.md", "skills/brand-voice-guide.md"],
        restricted_sources=["skills/credentials/youtube-api.md"] if (ROOT / "skills/credentials/youtube-api.md").exists() else [],
        output_contract=["video_script.md", "shot_list.md", "platform_copy.md", "review_request.md"],
        affects=["A4 assets", "A3 social calendar", "A2 SEO video titles", "YouTube/Shorts publishing queue"],
        risk_level="medium",
    ),
    RoleModule(
        "B1",
        "Investment OS Builder",
        "Investment OS Builder（功能建造）",
        "負責把已確認的 Investment OS / MAPLAB 跨專案需求寫成功能、接上 repo/runtime surface，並留下可驗證的變更紀錄；原 B1 投資邏輯橋接改為 B1-B4 共用底座。",
        [
            "feature_build",
            "repo_runtime_wiring",
            "dashboard_telegram_surface",
            "safe_file_only_fix",
            "task_card_execution",
            "investment_logic_implementation",
        ],
        [
            "projects/invest-os-b-role-system.md",
            "projects/b1-invest-os-builder.md",
            "handoff/tasks/T-B1-B4-investment-os-role-split.md",
            "projects/b1-cross-project-governance-advisor.md",
            "projects/b1-investment-logic-bridge.md",
            "projects/b1-investment-os-owner-persona-canonical.md",
            "projects/b1-investment-os-owner-profile.md",
            "handoff/tasks/T-B1-001.md",
        ],
        ["skills/invest-os-b-role-system.md", "skills/task-progress-guide.md"],
        output_contract=[
            "implementation_plan.md",
            "changed_files.md",
            "validation_report.md",
            "builder_handoff.md",
            "review_request.md",
        ],
        affects=[
            "Chrome side panel",
            "Investment OS repo/runtime surfaces",
            "Telegram/Dashboard report surfaces",
            "Investment OS investment logic prompt bridge",
            "Investment OS owner profile summon context",
            "B2 Reviewer",
            "B3 Archivist",
            "B4 System Patrol",
        ],
        risk_level="high",
    ),
    RoleModule(
        "B2",
        "Investment OS Reviewer",
        "Investment OS Reviewer（資料流與錯誤審查）",
        "負責檢查 Investment OS / MAPLAB 跨專案資料流、錯誤、freshness、報告契約與 owner-facing surface；預設 read-only review。",
        [
            "dataflow_review",
            "error_review",
            "source_freshness_review",
            "report_contract_review",
            "owner_visible_surface_check",
            "risk_boundary_review",
        ],
        [
            "projects/invest-os-b-role-system.md",
            "projects/b2-invest-os-reviewer.md",
            "handoff/tasks/T-B1-B4-investment-os-role-split.md",
            "projects/b1-investment-logic-bridge.md",
            "projects/b1-investment-os-owner-persona-canonical.md",
            "projects/b1-investment-os-owner-profile.md",
        ],
        ["skills/invest-os-b-role-system.md", "skills/task-progress-guide.md"],
        output_contract=[
            "dataflow_review.md",
            "error_report.md",
            "source_freshness_matrix.md",
            "owner_visible_surface_check.md",
            "review_request.md",
        ],
        affects=[
            "Investment OS dataflow",
            "Telegram/Dashboard report surfaces",
            "OpenClaw report contracts",
            "B1 Builder review request",
            "B3 Archivist handoff",
            "Chrome side panel",
        ],
        risk_level="medium",
    ),
    RoleModule(
        "B3",
        "Investment OS Archivist",
        "Investment OS Archivist（版本與交接紀錄）",
        "負責把版本紀錄、交接紀錄、resume prompt、review bundle、task card 與 pitfalls 整理成下一個 agent 可接手的 durable artifact。",
        [
            "version_note",
            "handoff_checkpoint",
            "resume_prompt",
            "status_writeback_plan",
            "pitfalls_append",
            "review_bundle_index",
        ],
        [
            "projects/invest-os-b-role-system.md",
            "projects/b3-invest-os-archivist.md",
            "handoff/tasks/T-B1-B4-investment-os-role-split.md",
            "workbook/reviews/README.md",
            "projects/b1-investment-logic-bridge.md",
        ],
        ["skills/invest-os-b-role-system.md", "skills/task-progress-guide.md"],
        output_contract=[
            "version_note.md",
            "handoff_checkpoint.md",
            "resume_prompt.md",
            "status_writeback_plan.md",
            "review_request.md",
        ],
        affects=[
            "CURRENT_STATUS.md",
            "handoff/tasks",
            "workbook/reviews",
            "pitfalls.md",
            "B1/B2/B4 handoff quality",
            "Chrome side panel",
        ],
        risk_level="medium",
    ),
    RoleModule(
        "B4",
        "Investment OS System Patrol",
        "Investment OS System Patrol（系統適配巡查）",
        "負責定期問「這套東西還適合嗎？」並檢查 Investment OS / MAPLAB 跨專案流程是否過度建置、錯誤路由、缺乏 owner-facing proof、或應該暫停/縮小/重構。",
        [
            "system_fit_patrol",
            "pause_resume_review",
            "workflow_suitability_check",
            "overbuild_detection",
            "role_routing_review",
            "owner_surface_review",
        ],
        [
            "projects/invest-os-b-role-system.md",
            "projects/b4-invest-os-system-patrol.md",
            "handoff/tasks/T-B1-B4-investment-os-role-split.md",
            "projects/b1-cross-project-governance-advisor.md",
            "projects/b1-investment-logic-bridge.md",
            "projects/b1-investment-os-owner-persona-canonical.md",
            "projects/b1-investment-os-owner-profile.md",
        ],
        ["skills/invest-os-b-role-system.md", "skills/task-progress-guide.md"],
        output_contract=[
            "system_patrol_report.md",
            "fit_check.md",
            "stop_continue_refactor_recommendations.md",
            "next_owner_decision.md",
            "review_request.md",
        ],
        affects=[
            "Investment OS workflow suitability",
            "MAPLAB governance docs",
            "Chrome side panel",
            "B1 Builder scope",
            "B2 Reviewer focus",
            "B3 Archivist writeback",
        ],
        risk_level="medium",
    ),
]


IOS_PROJECT_DOCS = ["projects/invest-os-strategy-role-system.md"]
IOS_SKILLS = ["skills/invest-os-b-role-system.md", "skills/task-progress-guide.md"]
IOS_RECALL_PATH = "recalls/IOS_strategy_role_recall.md"


def ios_role(
    role_id: str,
    role_name: str,
    department: str,
    simulation: str,
    task_types: list[str],
    output_contract: list[str],
    affects: list[str],
    risk_level: str = "medium",
) -> RoleModule:
    return RoleModule(
        role_id,
        role_name,
        department,
        simulation,
        task_types,
        IOS_PROJECT_DOCS,
        IOS_SKILLS,
        ["codex", "openclaw", "gemini", "hermes"],
        output_contract=output_contract,
        startup_contract_extra=[
            "Use Investment OS local repo as the canonical runtime truth: /Users/pagemacmini/Documents/New project.",
            "Read Investment OS AGENT_CORE.md, CURRENT_STATUS.md, pitfalls.md, config/investment_os_role_registry.json, and docs/INVESTMENT_OS_ROLE_WORKSPACES.md before acting.",
            f"Find role_id {role_id} in config/investment_os_role_registry.json and use its required_reads, bad_data_rule, background_jobs, Telegram outputs, Dashboard workspace, and B1-B4 escalation path.",
            f"Name this session {role_id} {department} when dispatching a dedicated cleanup or audit thread.",
            "If output quality is bad, inspect the whole strategy loop before asking a shared Telegram/Dashboard owner to patch formatting.",
        ],
        affects=affects,
        recall_path=IOS_RECALL_PATH,
        risk_level=risk_level,
    )


ROLES.extend(
    [
        ios_role(
            "IOS-MOMENTUM",
            "Daily Momentum Manager",
            "每日動能經理",
            "每日漲停、動能、成交量、強勢股與 16:00 籌碼合併的策略 owner。",
            ["momentum_scan", "limit_up_review", "top3_shortlist", "chip_merge", "pm_brief_quality"],
            ["momentum_shortlist.md", "openclaw_research_dispatch.md", "chip_merge_validation.md", "telegram_readback.md", "dashboard_freshness_check.md"],
            ["Daily Momentum Telegram PM Brief", "Momentum Dashboard section", "OpenClaw research dispatch", "B2 freshness review", "B1 runtime repair"],
            "high",
        ),
        ios_role(
            "IOS-KOL",
            "Influencer Radar Manager",
            "網紅雷達經理",
            "YouTube、Podcast、FB/KOL 與操作筆記抽取的策略 owner。",
            ["kol_digest", "youtube_rss", "notebooklm_packet", "operation_notes", "source_quality_review"],
            ["kol_digest.md", "operation_notes_validation.md", "source_freshness_matrix.md", "telegram_readback.md", "feedback_ledger_update.md"],
            ["KOL Telegram digest", "KOL shadow Dashboard evidence", "NotebookLM/OpenClaw worker packets", "B2 report quality review"],
            "medium",
        ),
        ios_role(
            "IOS-FB",
            "FB Social Intelligence Manager",
            "FB / 社群情報經理",
            "FB 與公開社群來源收集、正規化、路由健康與 candidate 品質的策略 owner。",
            ["fb_radar", "source_route_health", "social_candidate_review", "price_proof_manifest"],
            ["source_route_health.md", "normalized_quality_report.md", "candidate_review_queue.md", "price_proof_manifest.md"],
            ["FB Radar evidence", "social source route health", "B2 low-signal review", "B1 route repair"],
            "medium",
        ),
        ios_role(
            "IOS-ALPHA",
            "Cross-Source Alpha Manager",
            "阿爾法共振經理",
            "Reddit、RSS/X、Polymarket、市場異常與 convergence scoring 的策略 owner。",
            ["alpha_convergence", "polymarket_watch", "cross_source_event", "research_task_creation"],
            ["convergence_quality_report.md", "phone_card_readback.md", "shadow_review_sidecar.md", "research_task_queue.md"],
            ["Alpha Dashboard", "convergence phone card", "Polymarket hybrid strategy", "local model shadow findings"],
            "high",
        ),
        ios_role(
            "IOS-BLACKSWAN",
            "Black Swan Monitor",
            "黑天鵝監控官",
            "地緣、VIX、油價、美元、利率、Polymarket tail-risk 與 hedge watch 的風險 owner。",
            ["black_swan_watch", "tail_risk_monitor", "hedge_signal_review", "risk_regime_alert"],
            ["black_swan_watch.md", "hedge_signal_quality.md", "alert_readback.md", "missing_data_questions.md"],
            ["Black swan alert", "hedge playbook", "Macro/Risk Dashboard", "B2 risk-boundary review"],
            "high",
        ),
        ios_role(
            "IOS-INVENTORY",
            "Real Position Review Manager",
            "庫存審查經理",
            "實單持股、股期與真實部位風險控制的 portfolio owner。",
            ["live_position_review", "broker_snapshot_freshness", "position_research", "risk_card"],
            ["live_position_review.md", "chip_research_merge.md", "news_source_matrix.md", "risk_action_boundary.md", "telegram_readback.md"],
            ["Real position Telegram risk card", "Inventory Dashboard", "broker-free research handoff", "B2 risk review"],
            "high",
        ),
        ios_role(
            "IOS-MACRO",
            "Macro Master",
            "總經大師",
            "FRED、BLS、利率、美元、油價、景氣 regime 與台股風險框架的策略 owner。",
            ["macro_regime", "fred_bls_review", "risk_weather", "macro_dashboard"],
            ["macro_regime_card.md", "source_release_check.md", "dashboard_readback.md", "strategy_impact_note.md"],
            ["Macro Dashboard", "risk weather card", "B2 freshness review", "B4 regime workflow fit"],
            "medium",
        ),
        ios_role(
            "IOS-CHIP",
            "Chip Flow Manager",
            "籌碼經理",
            "三大法人、融資融券、集保、chip anomaly 與盤後合併的資料 owner。",
            ["chip_refresh", "twse_t86", "margin_balance", "chip_anomaly", "after_1600_merge"],
            ["chip_freshness_matrix.md", "chip_anomaly_report.md", "merge_receipt.md", "downstream_role_handoff.md"],
            ["Chip merge", "Momentum/Inventory/Macro downstream cards", "B2 dataflow review"],
            "medium",
        ),
        ios_role(
            "IOS-LEFT",
            "Left-Side Research Manager",
            "左側預期差經理",
            "左側研究、公開資訊缺口、敘事早期變化與買前功課問題包的策略 owner。",
            ["left_side_research", "expectation_gap", "public_fact_questions", "research_evidence_packet"],
            ["left_side_candidates.md", "public_fact_gap_matrix.md", "openclaw_question_pack.md", "research_task_handoff.md"],
            ["Left-side Dashboard", "OpenClaw research packet", "B2 evidence review"],
            "medium",
        ),
        ios_role(
            "IOS-RIGHT",
            "Right-Side Execution Manager",
            "右側交易經理",
            "右側強勢股、開盤劇本、股期候選與只讀決策卡的策略 owner。",
            ["right_side_shortlist", "opening_playbook", "stock_future_watch", "execution_boundary"],
            ["right_side_shortlist.md", "opening_playbook.md", "stock_future_watch.md", "risk_boundary_readback.md"],
            ["Trader Dashboard", "opening playbook Telegram", "B2 action-boundary review"],
            "high",
        ),
        ios_role(
            "IOS-EVIDENCE",
            "Research Evidence Manager",
            "研究證據經理",
            "研究證據矩陣、來源分類、推論標記、缺資料與 OpenClaw/Hermes evidence contract 的 platform owner。",
            ["evidence_matrix", "source_quality", "fact_inference_split", "openclaw_validation"],
            ["evidence_matrix.md", "source_quality_report.md", "fact_inference_split.md", "worker_output_validation.md"],
            ["Research Evidence Dashboard", "OpenClaw/Hermes evidence packets", "B2 review contracts"],
            "medium",
        ),
        ios_role(
            "IOS-SIM",
            "Simulation Ledger Manager",
            "模擬倉經理",
            "本地模擬倉 ledger、ROI、模擬紀錄與 broker simulation wording boundary 的 portfolio owner。",
            ["local_simulation_ledger", "roi_review", "simulation_boundary", "sim_dashboard"],
            ["simulation_ledger_review.md", "roi_quality_report.md", "boundary_wording_check.md", "dashboard_readback.md"],
            ["Simulation Dashboard", "local ledger reports", "B2 broker-boundary review"],
            "medium",
        ),
        ios_role(
            "IOS-FAMILY",
            "Family Fund Manager",
            "家族基金經理",
            "家族基金、大盤、帳戶層級總覽、資金池與 dashboard account-level proof 的 portfolio owner。",
            ["family_fund_dashboard", "account_level_summary", "capital_bucket_review", "fund_readback"],
            ["family_fund_summary.md", "account_level_readback.md", "capital_bucket_review.md", "dashboard_freshness_check.md"],
            ["Family fund Dashboard", "account-level charts", "B2 source separation review"],
            "medium",
        ),
        ios_role(
            "IOS-HEDGE",
            "After-Hours Hedge Manager",
            "盤後對沖經理",
            "盤後、夜盤、海外期貨、風險對沖觀察與 watch-only hedge playbook 的策略 owner。",
            ["after_hours_watch", "hedge_playbook", "global_futures_monitor", "watch_only_boundary"],
            ["after_hours_hedge_watch.md", "global_risk_snapshot.md", "watch_only_boundary.md", "owner_decision_options.md"],
            ["After-hours hedge brief", "Black swan and Macro downstream", "B2 risk boundary review"],
            "high",
        ),
        ios_role(
            "IOS-SURFACE",
            "Surface Contract Steward",
            "介面契約守門員",
            "Telegram、Dashboard、閱讀體驗、色彩安全與 shared renderer defects 的 platform owner。",
            ["telegram_contract", "dashboard_readability", "surface_renderer_review", "runtime_readback"],
            ["surface_contract_review.md", "readability_check.md", "runtime_readback.md"],
            ["Chrome side panel", "Telegram PM Brief format", "Dashboard readability", "B1 shared renderer fixes"],
            "high",
        ),
        ios_role(
            "IOS-HYGIENE",
            "System Hygiene Steward",
            "系統衛生官",
            "dirty worktree、stale bundles、duplicated logs、checkpoint drift 與 keep/drop 決策包的 platform owner。",
            ["dirty_worktree_inventory", "keep_drop_decision", "cleanup_handoff", "scheduled_hygiene"],
            ["dirty_worktree_inventory.md", "keep_drop_decision_package.md", "cleanup_handoff_to_B1_B3.md", "patrol_receipt.md"],
            ["dirty worktree inventory", "B4 cleanup patrol", "B3 archive handoff", "B1 cleanup script repair"],
            "high",
        ),
    ]
)


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "MAPLAB Dynamic Role Task Module",
    "type": "object",
    "required": [
        "schema_version",
        "module_id",
        "role_id",
        "runtime_targets",
        "read_first",
        "startup_contract",
        "output_contract",
        "writeback",
        "affects",
    ],
    "properties": {
        "schema_version": {"type": "string"},
        "generated_at": {"type": "string"},
        "module_id": {"type": "string"},
        "role_id": {"type": "string"},
        "role_name": {"type": "string"},
        "department": {"type": "string"},
        "role_simulation": {"type": "string"},
        "runtime_targets": {"type": "array", "items": {"type": "string"}},
        "task_types": {"type": "array", "items": {"type": "string"}},
        "read_first": {"type": "array"},
        "restricted_sources": {"type": "array"},
        "skill_group": {"type": "array", "items": {"type": "string"}},
        "source_policy": {"type": "object"},
        "source_freshness": {"type": "object"},
        "startup_contract": {"type": "array", "items": {"type": "string"}},
        "output_contract": {"type": "array", "items": {"type": "string"}},
        "writeback": {"type": "object"},
        "affects": {"type": "array", "items": {"type": "string"}},
        "forbidden_actions": {"type": "array", "items": {"type": "string"}},
        "verification_required": {"type": "array", "items": {"type": "string"}},
        "risk_level": {"type": "string"},
    },
}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_graph(modules: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    def node(node_id: str, node_type: str, title: str, path: str = "", status: str = "active") -> None:
        nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "title": title,
            "status": status,
            "path": path,
            "updated_at": NOW,
        }

    def edge(src: str, dst: str, relation: str, confidence: float = 1.0) -> None:
        edges.append({"from": src, "to": dst, "relation": relation, "confidence": confidence})

    node("task:T-A1-EXT-001", "task", "GitHub dynamic role modules for Chrome/Gemini/Codex/OpenClaw", str(TASK_CARD_PATH.relative_to(ROOT)))
    node("output:role-module-index", "output", "Role module index", "chrome-extension/task-modules/index.json")
    node("output:relationship-table", "output", "Role module relationship table", "workbook/task_modules/role_module_relationships.csv")
    node("output:relationship-xlsx", "output", "Role module relationship workbook", "workbook/task_modules/role_module_relationships.xlsx")
    edge("task:T-A1-EXT-001", "output:role-module-index", "produces")
    edge("task:T-A1-EXT-001", "output:relationship-table", "produces")
    edge("task:T-A1-EXT-001", "output:relationship-xlsx", "produces")

    for surface in CODE_SURFACES:
        surface_id = f"code:{surface['id']}"
        node(surface_id, "code_surface", surface["id"], ", ".join(surface["paths"]))
        edge("task:T-A1-EXT-001", surface_id, "affects_code_surface")

    for module in modules:
        mid = f"module:{module['role_id']}"
        aid = f"agent:{module['role_id']}"
        node(mid, "task_module", module["module_id"], f"chrome-extension/task-modules/{module['role_id']}.json")
        node(aid, "agent", f"{module['role_id']} {module['role_name']}")
        edge("task:T-A1-EXT-001", mid, "defines_module")
        edge(mid, aid, "activates_role")
        for runtime in module["runtime_targets"]:
            rid = f"runtime:{runtime}"
            node(rid, "runtime", runtime)
            edge(mid, rid, "portable_to")
        for item in module["read_first"]:
            sid = f"source:{item['path']}"
            node(sid, "source_doc", item["path"], item["path"], "active" if item["exists"] == "true" else "missing")
            edge(mid, sid, "must_read")
        for item in module.get("restricted_sources", []):
            sid = f"source:{item['path']}"
            node(sid, "source_doc", item["path"], item["path"], "restricted" if item["exists"] == "true" else "missing")
            edge(mid, sid, "restricted_reference")
        for affect in module["affects"]:
            target_id = f"impact:{module['role_id']}:{affect}"
            node(target_id, "impact", affect)
            edge(mid, target_id, "affects")

    return {"generated_at": NOW, "nodes": list(nodes.values()), "edges": edges}


def build_relationship_rows(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for module in modules:
        for source in module["read_first"]:
            rows.append(
                {
                    "role_id": module["role_id"],
                    "module_id": module["module_id"],
                    "source_path": source["path"],
                    "source_type": source["purpose"],
                    "relation": "must_read",
                    "load_mode": source["load_mode"],
                    "exists": source["exists"],
                    "source_sha256": source.get("source_sha256", ""),
                    "size_bytes": source.get("size_bytes", ""),
                    "runtime_targets": ", ".join(module["runtime_targets"]),
                    "affects": "; ".join(module["affects"]),
                    "risk_level": module["risk_level"],
                    "notes": "Loaded into handoff pack unless missing; use live API/UI for external system facts.",
                }
            )
        for source in module.get("restricted_sources", []):
            rows.append(
                {
                    "role_id": module["role_id"],
                    "module_id": module["module_id"],
                    "source_path": source["path"],
                    "source_type": source["purpose"],
                    "relation": "restricted_reference",
                    "load_mode": source["load_mode"],
                    "exists": source["exists"],
                    "source_sha256": source.get("source_sha256", ""),
                    "size_bytes": source.get("size_bytes", ""),
                    "runtime_targets": ", ".join(module["runtime_targets"]),
                    "affects": "; ".join(module["affects"]),
                    "risk_level": module["risk_level"],
                    "notes": "Do not paste credential/secrets docs into Gemini/OpenClaw prompts; A1-only lookup when approved.",
                }
            )
    for surface in CODE_SURFACES:
        for path in surface["paths"]:
            rows.append(
                {
                    "role_id": "ALL",
                    "module_id": "CODE_SURFACE",
                    "source_path": path,
                    "source_type": "code surface",
                    "relation": f"implemented_by:{surface['id']}",
                    "load_mode": "read/modify_by_A1",
                    "exists": str((ROOT / path).exists()).lower(),
                    "source_sha256": file_sha256(ROOT / path) if (ROOT / path).exists() else "",
                    "size_bytes": str((ROOT / path).stat().st_size) if (ROOT / path).exists() else "",
                    "runtime_targets": "codex",
                    "affects": surface["impact"],
                    "risk_level": "high" if surface["id"] in {"chrome-extension", "a6-openclaw-runtime"} else "medium",
                    "notes": "Changing this surface can affect multiple runtimes; update relation graph and changelog.",
                }
            )
    return rows


def build_doc(modules: list[dict[str, Any]]) -> str:
    lines = [
        "# GitHub Dynamic Role Task Modules",
        "",
        f"Generated: {NOW}",
        "",
        "## Purpose",
        "",
        "This module set turns the Chrome side panel from a Claude-tab injector into a platform-neutral role handoff surface.",
        "GitHub stores JSON/Markdown task data. Chrome/Gemini/Codex/OpenClaw consume the same module contracts.",
        "",
        "## Non-negotiable design rule",
        "",
        "- GitHub dynamic links load data/config only.",
        "- Do not execute remote JavaScript in Chrome. Chrome MV3 CSP already broke that path in extension v4.0/v4.2.",
        "- Claude tab injection remains optional legacy behavior, not the main runtime.",
        "",
        "## Outputs",
        "",
        "- `chrome-extension/task-modules/index.json` — public module index for the side panel.",
        "- `chrome-extension/task-modules/{role}.json` — one portable role module per agent.",
        "- `chrome-extension/config/task-modules.json` — extension config pointer.",
        "- `workbook/task_modules/role_module_relation_graph.json` — directed impact graph.",
        "- `workbook/task_modules/role_module_relationships.csv` and `.xlsx` — Excel-readable relationship table.",
        "",
        "## Markdown Refresh Model",
        "",
        "- Role JSON files are routing envelopes, not frozen copies of the source documents.",
        "- The Chrome side panel hands Gemini/Codex/OpenClaw GitHub raw links so the runtime reads the latest Markdown/JSON content.",
        "- Each source entry includes `source_sha256`; the side panel can compare it with current GitHub raw content and warn when a Markdown file changed after module generation.",
        "- If hashes differ, run `python3 tools/ai_workbook/build_extension_task_modules.py`, commit, push, then reload the side panel.",
        "",
        "## Role Modules",
        "",
    ]
    for module in modules:
        lines.extend(
            [
                f"### {module['role_id']} — {module['role_name']}",
                "",
                f"- Department: {module['department']}",
                f"- Simulation: {module['role_simulation']}",
                f"- Runtime targets: {', '.join(module['runtime_targets'])}",
                f"- Task types: {', '.join(module['task_types'])}",
                f"- Affects: {'; '.join(module['affects'])}",
                f"- Module file: `chrome-extension/task-modules/{module['role_id']}.json`",
                "",
            ]
        )
    lines.extend(
        [
            "## Relationship Rule",
            "",
            "Every role handoff must answer these before work starts:",
            "",
            "1. Which role am I simulating?",
            "2. Which exact repo files must I read?",
            "3. Which outputs must I produce?",
            "4. Which other roles/files/systems are affected?",
            "5. Where will the review bundle or task output be written?",
            "",
            "## OpenClaw/Gemini/Codex Prompt Contract",
            "",
            "A runtime that receives a module should summarize the module, read only the listed files, then produce the declared output contract. If it cannot read files directly, it must ask for the content pack rather than hallucinating context.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_task_card(modules: list[dict[str, Any]]) -> str:
    return f"""# T-A1-EXT-001 — GitHub Dynamic Role Task Modules

狀態：🔄 in_progress
Owner request：把網路上 GitHub Chrome Extension 動態連結改成任務模組，讓 Gemini / Codex / OpenClaw 都能接角色、知道讀什麼、影響誰、產出去哪裡。

## Scope

- 建立平台中立的 role task module，不再把 Claude tab 注入當唯一入口。
- 全角色覆蓋：{", ".join(m["role_id"] for m in modules)}。
- 輸出指向性關聯圖、Excel/CSV 對照表、程式檔關聯面。

## Generated Outputs

- `docs/extension/dynamic-role-task-modules.md`
- `chrome-extension/config/task-modules.json`
- `chrome-extension/task-modules/index.json`
- `chrome-extension/task-modules/{{role}}.json` for every generated role module
- `workbook/task_modules/role_module_relation_graph.json`
- `workbook/task_modules/role_module_relationships.csv`
- `workbook/task_modules/role_module_relationships.xlsx`

## Guardrails

- GitHub dynamic link = data/config only, not remote JS.
- Credential docs are restricted references, not prompt payload.
- Public/外部 runtime must not receive secrets or internal-only facts.
- Live external systems must be verified via API/UI before treating repo notes as current facts.

## Next Implementation Step

Update Chrome extension UI to add:

1. role module selector
2. runtime target selector: Gemini / Codex / OpenClaw / legacy Claude
3. impact preview panel
4. one-click copy of platform-neutral handoff pack
5. Markdown freshness check so changed `.md` files are detected before dispatch

## Resume Prompt

我是 A1/Codex。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A1-EXT-001-dynamic-role-modules.md`。
接著讀 `docs/extension/dynamic-role-task-modules.md` 與 `workbook/task_modules/role_module_relationships.csv`。
下一步是修改 `chrome-extension/popup.html` / `popup.js`，讓側邊欄可讀 `chrome-extension/task-modules/index.json`，顯示角色模組、影響關係、runtime target、Markdown freshness，並產生 Gemini/Codex/OpenClaw 共用的 handoff prompt。
"""


def main() -> None:
    modules = [role.to_module() for role in ROLES]

    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    WORKBOOK_DIR.mkdir(parents=True, exist_ok=True)

    write_json(MODULE_DIR / "task-module.schema.json", SCHEMA)
    for module in modules:
        write_json(MODULE_DIR / f"{module['role_id']}.json", module)

    index = {
        "schema_version": "2026-05-11.dynamic-role-module-index.v1",
        "generated_at": NOW,
        "repository": "page1010/maplab-ai-handbook",
        "canonical_local_repo": "/Users/pagemacmini/maplab-ai-handbook",
        "dynamic_link_policy": "Load JSON/Markdown task data from GitHub; do not execute remote JS.",
        "modules": [
            {
                "role_id": module["role_id"],
                "module_id": module["module_id"],
                "role_name": module["role_name"],
                "department": module["department"],
                "path": f"chrome-extension/task-modules/{module['role_id']}.json",
                "runtime_targets": module["runtime_targets"],
                "risk_level": module["risk_level"],
            }
            for module in modules
        ],
    }
    write_json(MODULE_DIR / "index.json", index)
    write_json(
        CONFIG_DIR / "task-modules.json",
        {
            "generated_at": NOW,
            "module_index_path": "chrome-extension/task-modules/index.json",
            "module_schema_path": "chrome-extension/task-modules/task-module.schema.json",
            "relation_graph_path": "workbook/task_modules/role_module_relation_graph.json",
            "relationship_table_path": "workbook/task_modules/role_module_relationships.csv",
            "default_runtime_targets": ["gemini", "codex", "openclaw"],
            "legacy_runtime_targets": ["claude_tab"],
            "load_order": ["index", "role_module", "source_files", "relation_graph", "output_contract"],
            "security_note": "The extension should load data files only. Do not add remote script execution.",
        },
    )

    graph = build_graph(modules)
    write_json(WORKBOOK_DIR / "role_module_relation_graph.json", graph)

    rows = build_relationship_rows(modules)
    write_csv(
        WORKBOOK_DIR / "role_module_relationships.csv",
        rows,
        [
            "role_id",
            "module_id",
            "source_path",
            "source_type",
            "relation",
            "load_mode",
            "exists",
            "source_sha256",
            "size_bytes",
            "runtime_targets",
            "affects",
            "risk_level",
            "notes",
        ],
    )

    (DOCS_DIR / "dynamic-role-task-modules.md").write_text(build_doc(modules), encoding="utf-8")
    TASK_CARD_PATH.write_text(build_task_card(modules), encoding="utf-8")

    missing = sorted({row["source_path"] for row in rows if row["exists"] == "false"})
    write_json(
        WORKBOOK_DIR / "role_module_build_report.json",
        {
            "generated_at": NOW,
            "module_count": len(modules),
            "relationship_rows": len(rows),
            "graph_nodes": len(graph["nodes"]),
            "graph_edges": len(graph["edges"]),
            "missing_sources": missing,
            "outputs": [
                "docs/extension/dynamic-role-task-modules.md",
                "chrome-extension/config/task-modules.json",
                "chrome-extension/task-modules/index.json",
                "workbook/task_modules/role_module_relation_graph.json",
                "workbook/task_modules/role_module_relationships.csv",
                "workbook/task_modules/role_module_relationships.xlsx",
                str(TASK_CARD_PATH.relative_to(ROOT)),
            ],
        },
    )
    print(json.dumps({"modules": len(modules), "rows": len(rows), "missing_sources": missing}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
