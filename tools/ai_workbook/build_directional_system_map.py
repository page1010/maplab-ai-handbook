#!/usr/bin/env python3
"""Build MAPLAB directional maps and a sanitized NotebookLM source pack.

The canonical input is config/system-map/maplab-directional-map.json. Generated
HTML/graph/NotebookLM files must never be edited directly.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "config/system-map/maplab-directional-map.json"
SCHEMA_PATH = ROOT / "config/system-map/maplab-directional-map.schema.json"
DOC_MAP_PATH = ROOT / "docs/system-map/index.html"
EXT_MAP_PATH = ROOT / "chrome-extension/system-map/index.html"
GRAPH_PATH = ROOT / "docs/system-map/maplab-directional-map.graph.json"
BUILD_REPORT_PATH = ROOT / "docs/system-map/build-report.json"
NOTEBOOK_DIR = ROOT / "workbook/notebooklm/maplab-project-brain"
NOTEBOOK_DOC_PATH = NOTEBOOK_DIR / "maplab-project-brain.md"
NOTEBOOK_MANIFEST_PATH = NOTEBOOK_DIR / "source-manifest.json"
NOTEBOOK_README_PATH = NOTEBOOK_DIR / "README.md"

EXPECTED_VIEWS = {
    "overview",
    "repositories",
    "roles",
    "workflows",
    "artifacts",
    "capabilities",
    "governance",
}
EXPECTED_WORKFLOWS = {f"workflow:A{i}" for i in range(2, 9)}
REMOTE_PATH_PREFIXES = ("google-sheet:", "google-drive:", "https://", "http://")
GENERATED_PATH_PREFIXES = ("docs/system-map/", "chrome-extension/system-map/", "workbook/notebooklm/")
SECRET_VALUE_PATTERNS = [
    re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+\-/=]{12,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\b(api[_ -]?key|token|secret|password|cookie|authorization)\s*[:=]\s*([^\s`]+)"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+PRIVATE KEY-----"),
]


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_base_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def generated_at(manifest: dict[str, Any]) -> str:
    return f"{manifest['scope']['last_verified']}T00:00:00+08:00"


def iter_entities(manifest: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for collection in ("repositories", "hardware", "runtimes", "roles", "data_sources", "governance"):
        for entity in manifest[collection]:
            yield collection, entity


def validate_manifest(manifest: dict[str, Any], check_paths: bool = True) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != "2026-08-25.maplab-directional-map.v1":
        errors.append("schema_version is not the supported v1 value")

    view_ids = [view.get("id") for view in manifest.get("views", [])]
    if set(view_ids) != EXPECTED_VIEWS or len(view_ids) != len(EXPECTED_VIEWS):
        errors.append(f"views must be exactly {sorted(EXPECTED_VIEWS)}")

    entity_ids: list[str] = []
    for collection, entity in iter_entities(manifest):
        entity_id = entity.get("id")
        entity_ids.append(entity_id)
        for key in ("id", "name", "status", "description"):
            if not entity.get(key):
                errors.append(f"{collection}:{entity_id or '?'} missing {key}")
        path_value = entity.get("path")
        if (
            check_paths
            and path_value
            and not path_value.startswith(REMOTE_PATH_PREFIXES)
            and not path_value.startswith(GENERATED_PATH_PREFIXES)
        ):
            candidate = Path(path_value)
            if not candidate.is_absolute():
                candidate = ROOT / candidate
            if not candidate.exists():
                errors.append(f"missing referenced path: {path_value}")

    if len(entity_ids) != len(set(entity_ids)):
        errors.append("entity ids are not unique")

    workflow_ids = {workflow.get("id") for workflow in manifest.get("workflows", [])}
    if workflow_ids != EXPECTED_WORKFLOWS:
        errors.append(f"workflows must be exactly {sorted(EXPECTED_WORKFLOWS)}")

    stage_ids: list[str] = []
    for workflow in manifest.get("workflows", []):
        for stage in workflow.get("stages", []):
            stage_ids.append(stage.get("id"))
            for key in ("id", "name", "inputs", "actions", "outputs", "acceptance", "handoff_to", "evidence"):
                if key not in stage or not stage[key]:
                    errors.append(f"{workflow.get('id')}:{stage.get('id', '?')} missing/empty {key}")
    if len(stage_ids) != len(set(stage_ids)):
        errors.append("workflow stage ids are not unique")

    if not SCHEMA_PATH.exists():
        errors.append(f"missing schema: {SCHEMA_PATH.relative_to(ROOT)}")
    return errors


def graph_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    edge_keys: set[tuple[str, str, str]] = set()

    def add_node(node_id: str, node_type: str, label: str, status: str = "verified", path: str = "") -> None:
        nodes.setdefault(node_id, {"id": node_id, "type": node_type, "label": label, "status": status, "path": path})

    def add_edge(source: str, target: str, relation: str) -> None:
        key = (source, target, relation)
        if key not in edge_keys:
            edges.append({"from": source, "to": target, "relation": relation})
            edge_keys.add(key)

    for collection, entity in iter_entities(manifest):
        add_node(entity["id"], collection.rstrip("s"), entity["name"], entity["status"], entity.get("path", ""))

    role_ids = {role["id"] for role in manifest["roles"]}
    for workflow in manifest["workflows"]:
        add_node(workflow["id"], "workflow", workflow["name"])
        owner_id = f"role:{workflow['owner_role']}"
        if owner_id in role_ids:
            add_edge(owner_id, workflow["id"], "owns")
        previous_stage: str | None = None
        for stage in workflow["stages"]:
            add_node(stage["id"], "workflow_stage", stage["name"])
            add_edge(workflow["id"], stage["id"], "contains")
            if previous_stage:
                add_edge(previous_stage, stage["id"], "next_stage")
            previous_stage = stage["id"]
            for value in stage["inputs"]:
                artifact_id = f"artifact:{slug(value)}"
                add_node(artifact_id, "artifact", value)
                add_edge(artifact_id, stage["id"], "input_to")
            for value in stage["outputs"]:
                artifact_id = f"artifact:{slug(value)}"
                add_node(artifact_id, "artifact", value)
                add_edge(stage["id"], artifact_id, "produces")
            for value in stage.get("tools", []):
                tool_id = f"tool:{slug(value)}"
                add_node(tool_id, "tool", value, "declared")
                add_edge(tool_id, stage["id"], "enables")
            if stage.get("approval_gate"):
                gate_id = f"gate:{stage['id']}"
                add_node(gate_id, "approval_gate", stage["approval_gate"], "declared")
                add_edge(stage["id"], gate_id, "requires")
            for value in stage["evidence"]:
                evidence_id = f"evidence:{slug(value)}"
                add_node(evidence_id, "evidence", value)
                add_edge(stage["id"], evidence_id, "proven_by")
            for target in stage["handoff_to"]:
                if target.startswith("A") and "-" not in target and "/" not in target:
                    add_edge(stage["id"], f"role:{target}", "handoff_to")

    manifest_hash = sha256_file(MANIFEST_PATH)
    return {
        "schema_version": manifest["schema_version"],
        "generated_at": generated_at(manifest),
        "source_manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "source_manifest_sha256": manifest_hash,
        "build_base_commit": git_base_commit(),
        "scope": manifest["scope"],
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": sorted(edges, key=lambda item: (item["from"], item["to"], item["relation"])),
    }


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if clean:
        return clean[:72]
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def render_html(manifest: dict[str, Any], graph: dict[str, Any]) -> str:
    payload = json.dumps({"manifest": manifest, "graph": graph}, ensure_ascii=False).replace("</", "<\\/")
    manifest_hash = graph["source_manifest_sha256"][:12]
    commit = graph["build_base_commit"]
    title = html.escape(manifest["scope"]["title"])
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
:root{{--bg:#11100f;--panel:#1c1a18;--panel2:#24211e;--line:#3c3833;--text:#eee8de;--muted:#a49a8c;--ok:#62c98b;--warn:#e6b64c;--bad:#ed6a6a;--accent:#77a8dc;--role:#d399d5;--data:#92a2dd}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:14px/1.55 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif}}
header{{padding:18px 20px 12px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:5}}h1{{font-size:20px;margin:0 0 4px}}h2{{font-size:17px;margin:0 0 12px}}h3{{font-size:14px;margin:0 0 5px}}.meta,.muted{{color:var(--muted)}}.meta{{font-size:12px;display:flex;gap:12px;flex-wrap:wrap}}
nav{{display:flex;gap:7px;overflow:auto;padding:10px 20px;border-bottom:1px solid var(--line);position:sticky;top:74px;background:var(--bg);z-index:4}}button,select{{font:inherit}}nav button,.role-filter button{{border:1px solid var(--line);background:var(--panel);color:var(--text);border-radius:16px;padding:6px 11px;cursor:pointer;white-space:nowrap}}nav button.on,.role-filter button.on{{background:var(--text);color:var(--bg);border-color:var(--text)}}main{{padding:18px 20px 40px;max-width:1440px;margin:auto}}.view{{display:none}}.view.on{{display:block}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-bottom:20px}}.card{{background:var(--panel);border-left:4px solid var(--line);padding:12px;min-height:86px}}.card.verified{{border-color:var(--ok)}}.card.declared{{border-color:var(--warn)}}.card.missing{{border-color:var(--bad)}}.card.excluded{{opacity:.58}}.chips{{display:flex;gap:5px;flex-wrap:wrap;margin-top:8px}}.chip{{background:var(--panel2);border-radius:12px;padding:2px 7px;font-size:11px;color:var(--muted)}}.path{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;color:var(--accent);overflow-wrap:anywhere;margin-top:6px}}.section{{margin-bottom:25px}}.flow{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:20px;margin-bottom:22px}}.stage{{background:var(--panel);padding:12px;position:relative;border-top:3px solid var(--accent)}}.stage:not(:last-child)::after{{content:"→";position:absolute;right:-15px;top:44%;color:var(--muted)}}.stage-id{{font-size:11px;color:var(--accent)}}.stage ul{{padding-left:17px;margin:7px 0}}.stage details{{border-top:1px solid var(--line);margin-top:8px;padding-top:7px}}.stage summary{{cursor:pointer;color:var(--muted)}}.gate{{color:var(--warn);font-size:12px;margin-top:7px}}.role-filter{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;vertical-align:top;padding:9px;border-bottom:1px solid var(--line)}}th{{color:var(--muted)}}.table-wrap{{overflow:auto}}.lineage{{display:grid;grid-template-columns:minmax(160px,.8fr) 28px minmax(220px,1fr) 28px minmax(180px,.8fr);gap:7px;align-items:center;margin:7px 0}}.arrow{{text-align:center;color:var(--muted)}}.status{{display:inline-flex;align-items:center;gap:5px;font-size:11px;color:var(--muted)}}.status::before{{content:"";width:8px;height:8px;border-radius:50%;background:var(--line)}}.status.verified::before{{background:var(--ok)}}.status.declared::before{{background:var(--warn)}}.status.missing::before{{background:var(--bad)}}.callout{{background:#142130;border-left:4px solid var(--accent);padding:12px;margin:12px 0 20px}}
@media(max-width:760px){{header{{position:static}}nav{{top:0}}main{{padding:14px}}.flow{{grid-template-columns:1fr;gap:8px}}.stage:not(:last-child)::after{{content:"↓";right:auto;left:50%;top:auto;bottom:-14px}}.lineage{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg)}}}}
</style>
</head>
<body>
<header><h1>{title}</h1><div class="meta"><span>manifest <b>{manifest_hash}</b></span><span>build base <b>{commit}</b></span><span>verified <b>{manifest['scope']['last_verified']}</b></span><span>投資系統：本輪排除</span></div></header>
<nav id="tabs"></nav>
<main>
  <section class="view" data-view="overview"><div id="overview"></div></section>
  <section class="view" data-view="repositories"><div id="repositories"></div></section>
  <section class="view" data-view="roles"><div id="roles"></div></section>
  <section class="view" data-view="workflows"><div id="workflows"></div></section>
  <section class="view" data-view="artifacts"><div id="artifacts"></div></section>
  <section class="view" data-view="capabilities"><div id="capabilities"></div></section>
  <section class="view" data-view="governance"><div id="governance"></div></section>
</main>
<script id="map-data" type="application/json">{payload}</script>
<script>
const DATA=JSON.parse(document.getElementById('map-data').textContent), M=DATA.manifest;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[c]));
const chips=a=>(a||[]).map(x=>`<span class="chip">${{esc(x)}}</span>`).join('');
const card=e=>`<article class="card ${{esc(e.status)}}"><h3>${{esc(e.name)}}</h3><span class="status ${{esc(e.status)}}">${{esc(e.status)}}</span><div>${{esc(e.description)}}</div>${{e.path?`<div class="path">${{esc(e.path)}}</div>`:''}}${{chips(e.used_by||e.outputs)}}</article>`;
const section=(title,items)=>`<div class="section"><h2>${{esc(title)}}</h2><div class="grid">${{items.map(card).join('')}}</div></div>`;
const tabs=document.getElementById('tabs');
M.views.forEach((v,i)=>{{const b=document.createElement('button');b.textContent=v.title;b.dataset.id=v.id;b.title=v.question;b.onclick=()=>show(v.id);tabs.appendChild(b);}});
function show(id){{document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on',v.dataset.view===id));document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.id===id));localStorage.setItem('maplab-map-view',id);}}
function renderOverview(){{document.getElementById('overview').innerHTML=`<div class="callout"><b>讀圖順序：</b>Owner 定方向與 gate → A0/A1 路由與治理 → A2–A8 持有專業工作流 → 模型/代理提供可替換能力 → Sheet/Drive/索引保存營運資料 → commit/receipt 證明完成。</div>${{section('地端與外部工作面',M.hardware)}}${{section('共治與執行能力',M.runtimes)}}${{section('責任角色',M.roles)}}${{section('優先資料入口',M.data_sources)}}`;}}
function renderRepos(){{document.getElementById('repositories').innerHTML=section('Repo、輸出根與排除邊界',M.repositories)+`<div class="callout"><b>Freshness：</b>圖以 manifest SHA 驗證內容；外部 live 狀態仍以 API/UI/runtime readback 為準。生成 HTML 不取代 CURRENT_STATUS 或 receipt。</div>`;}}
function renderRoles(){{document.getElementById('roles').innerHTML=`<div class="table-wrap"><table><thead><tr><th>角色</th><th>責任</th><th>主要輸入</th><th>主要輸出</th><th>正式來源</th></tr></thead><tbody>${{M.roles.map(r=>`<tr><td><b>${{esc(r.name)}}</b></td><td>${{esc(r.description)}}</td><td>${{chips(r.inputs)}}</td><td>${{chips(r.outputs)}}</td><td class="path">${{esc(r.path||'—')}}</td></tr>`).join('')}}</tbody></table></div>`;}}
function stageCard(s){{return `<article class="stage"><div class="stage-id">${{esc(s.id)}}</div><h3>${{esc(s.name)}}</h3><b>輸出</b><div class="chips">${{chips(s.outputs)}}</div>${{s.approval_gate?`<div class="gate">Gate：${{esc(s.approval_gate)}}</div>`:''}}<details><summary>輸入／執行／驗收／交接</summary><b>輸入</b><ul>${{s.inputs.map(x=>`<li>${{esc(x)}}</li>`).join('')}}</ul><b>執行</b><ul>${{s.actions.map(x=>`<li>${{esc(x)}}</li>`).join('')}}</ul><b>驗收</b><ul>${{s.acceptance.map(x=>`<li>${{esc(x)}}</li>`).join('')}}</ul><b>交接</b><div>${{chips(s.handoff_to)}}</div><b>證據</b><div>${{chips(s.evidence)}}</div></details></article>`;}}
function renderWorkflow(id){{const w=M.workflows.find(x=>x.id===id)||M.workflows[0];document.getElementById('workflow-body').innerHTML=`<h2>${{esc(w.name)}}</h2><p class="muted">${{esc(w.purpose)}}</p><div class="flow">${{w.stages.map(stageCard).join('')}}</div>`;document.querySelectorAll('.role-filter button').forEach(b=>b.classList.toggle('on',b.dataset.id===w.id));}}
function renderWorkflows(){{document.getElementById('workflows').innerHTML=`<div class="role-filter">${{M.workflows.map(w=>`<button data-id="${{esc(w.id)}}">${{esc(w.owner_role)}}</button>`).join('')}}</div><div id="workflow-body"></div>`;document.querySelectorAll('.role-filter button').forEach(b=>b.onclick=()=>renderWorkflow(b.dataset.id));renderWorkflow('workflow:A2');}}
function renderArtifacts(){{const chains=[['LINE／對話','A7 structured intake','A5 quote payload／A6 reply'],['Items＋QUOTE_DRAFT','A5 calculation','Sheet／Slides／A6 customer draft'],['Drive＋MAPLAB_ASSET_LOG','A4 approved asset pack','A2 article／A3 creative／A6 proposal／A8 video'],['A2 approved case brief','A2 article branch＋A8 media branch','WP／social publish＋performance readback'],['lyrics＋style＋licensed audio','A8 video master','platform versions＋distribution receipt'],['Task Card＋code change','tests＋live readback','Git commit＋review receipt']];document.getElementById('artifacts').innerHTML=`<h2>主要產物血緣</h2>${{chains.map(c=>`<div class="lineage"><div class="card verified"><b>${{esc(c[0])}}</b></div><div class="arrow">→</div><div class="card declared"><b>${{esc(c[1])}}</b></div><div class="arrow">→</div><div class="card verified"><b>${{esc(c[2])}}</b></div></div>`).join('')}}${{section('可追溯資料入口',M.data_sources)}}`;}}
function renderCapabilities(){{document.getElementById('capabilities').innerHTML=section('硬體／工作面',M.hardware)+section('模型／代理能力',M.runtimes)+`<div class="callout"><b>重要：</b>角色是責任；Claude、Codex、Antigravity、Hermes、GPT、OpenClaw 是能力。能力可以替換，但角色的輸入、輸出、gate 與 receipt 契約不能消失。</div>`;}}
function renderGovernance(){{document.getElementById('governance').innerHTML=section('治理、記憶與完成證據',M.governance)+`<div class="lineage"><div class="card verified"><b>Owner correction</b></div><div class="arrow">→</div><div class="card verified"><b>CURRENT_STATUS＋Task Card</b></div><div class="arrow">→</div><div class="card verified"><b>commit＋receipt＋Resume Prompt</b></div></div><div class="callout"><b>NotebookLM：</b>只作 sanitized 專案閱讀與帶引用問答；不自動同步 Git，也不取代 live fact、Task Card、commit 或 receipt。</div>`;}}
renderOverview();renderRepos();renderRoles();renderWorkflows();renderArtifacts();renderCapabilities();renderGovernance();show(localStorage.getItem('maplab-map-view')||'overview');
</script>
</body></html>
"""


def redact_secret_values(text: str) -> tuple[str, int]:
    redactions = 0
    output = text
    for pattern in SECRET_VALUE_PATTERNS:
        if pattern.pattern.startswith("(?i)\\b(api"):
            output, count = pattern.subn(lambda match: f"{match.group(1)}=[REDACTED_CONFIG_VALUE]", output)
        elif "bearer" in pattern.pattern.lower():
            output, count = pattern.subn(lambda match: f"{match.group(1)}[REDACTED]", output)
        else:
            output, count = pattern.subn("[REDACTED_SECRET_VALUE]", output)
        redactions += count
    return output, redactions


def build_notebooklm_pack(manifest: dict[str, Any]) -> dict[str, Any]:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    source_rows: list[dict[str, Any]] = []
    chapters: list[str] = [
        "# MAPLAB Project Brain — NotebookLM Safe Source Pack",
        "",
        f"> Generated from `{MANIFEST_PATH.relative_to(ROOT)}`. Build base commit `{git_base_commit()}`; manifest SHA `{sha256_file(MANIFEST_PATH)}`.",
        "> This is a curated internal-governance corpus, not a literal repository dump and not a live-state authority.",
        "> Excluded: secrets, credentials, cookies, customer raw data, runtime logs, SQLite/DB dumps, investment data, media binaries and generated noise.",
        "",
        "## How to answer from this pack",
        "",
        "1. Cite the source path and its embedded SHA for every material claim.",
        "2. Treat CURRENT_STATUS/Task Cards/runtime/UI/receipts as separate truth layers.",
        "3. If a fact may have changed after the embedded source hash, answer `needs live refresh`.",
        "4. Never infer approval, publishing, platform state or completion from a plan alone.",
    ]
    total_redactions = 0
    for relative in manifest["notebooklm"]["source_files"]:
        source = ROOT / relative
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"NotebookLM source missing: {relative}")
        raw = source.read_text(encoding="utf-8")
        sanitized, count = redact_secret_values(raw)
        total_redactions += count
        row = {
            "path": relative,
            "sha256": sha256_bytes(raw.encode("utf-8")),
            "bytes": len(raw.encode("utf-8")),
            "classification": "internal_governance",
            "redactions": count,
        }
        source_rows.append(row)
        fence = "````" if "```" in sanitized else "```"
        chapters.extend(
            [
                "",
                f"## Source: `{relative}`",
                "",
                f"- SHA-256: `{row['sha256']}`",
                f"- Classification: `{row['classification']}`",
                f"- Redactions: `{count}`",
                "",
                f"{fence}markdown",
                sanitized,
                fence,
            ]
        )
    NOTEBOOK_DOC_PATH.write_text("\n".join(chapters).rstrip() + "\n", encoding="utf-8")
    source_manifest = {
        "schema_version": "2026-08-25.notebooklm-source-pack.v1",
        "generated_at": generated_at(manifest),
        "build_base_commit": git_base_commit(),
        "directional_map_manifest_sha256": sha256_file(MANIFEST_PATH),
        "upload_files": [str(NOTEBOOK_DOC_PATH.relative_to(ROOT)), str(NOTEBOOK_MANIFEST_PATH.relative_to(ROOT))],
        "allowed_sensitivity": manifest["notebooklm"]["allowed_sensitivity"],
        "excluded_patterns": manifest["notebooklm"]["excluded_patterns"],
        "sources": source_rows,
        "total_redactions": total_redactions,
        "not_live_truth": True,
    }
    NOTEBOOK_MANIFEST_PATH.write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    NOTEBOOK_README_PATH.write_text(
        "# MAPLAB NotebookLM Project Brain\n\n"
        "Upload only `maplab-project-brain.md` and `source-manifest.json` to the MAPLAB notebook. "
        "The pack is generated by `python3 tools/ai_workbook/build_directional_system_map.py`; "
        "never upload the repository wholesale. Regenerate after governance changes, replace the "
        "NotebookLM sources, and keep the source manifest so answers can cite file hashes.\n\n"
        "NotebookLM is a reading and education layer. For current platform/runtime state, refresh "
        "from API/UI/runtime readback and write the result back through Task Card, commit and receipt.\n",
        encoding="utf-8",
    )
    return source_manifest


def write_outputs(manifest: dict[str, Any]) -> dict[str, Any]:
    graph = graph_from_manifest(manifest)
    rendered = render_html(manifest, graph)
    DOC_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXT_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_MAP_PATH.write_text(rendered, encoding="utf-8")
    EXT_MAP_PATH.write_text(rendered, encoding="utf-8")
    GRAPH_PATH.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    notebook = build_notebooklm_pack(manifest)
    report = {
        "schema_version": manifest["schema_version"],
        "generated_at": generated_at(manifest),
        "build_base_commit": git_base_commit(),
        "source_manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "source_manifest_sha256": sha256_file(MANIFEST_PATH),
        "views": len(manifest["views"]),
        "roles": len(manifest["roles"]),
        "workflows": len(manifest["workflows"]),
        "workflow_stages": sum(len(item["stages"]) for item in manifest["workflows"]),
        "graph_nodes": len(graph["nodes"]),
        "graph_edges": len(graph["edges"]),
        "notebook_sources": len(notebook["sources"]),
        "outputs": [
            str(DOC_MAP_PATH.relative_to(ROOT)),
            str(EXT_MAP_PATH.relative_to(ROOT)),
            str(GRAPH_PATH.relative_to(ROOT)),
            str(NOTEBOOK_DOC_PATH.relative_to(ROOT)),
            str(NOTEBOOK_MANIFEST_PATH.relative_to(ROOT)),
            str(NOTEBOOK_README_PATH.relative_to(ROOT)),
        ],
    }
    BUILD_REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def check_generated_outputs(manifest: dict[str, Any]) -> list[str]:
    expected = [
        DOC_MAP_PATH,
        EXT_MAP_PATH,
        GRAPH_PATH,
        BUILD_REPORT_PATH,
        NOTEBOOK_DOC_PATH,
        NOTEBOOK_MANIFEST_PATH,
        NOTEBOOK_README_PATH,
    ]
    errors = [f"missing generated output: {path.relative_to(ROOT)}" for path in expected if not path.exists()]
    if errors:
        return errors

    manifest_hash = sha256_file(MANIFEST_PATH)
    if DOC_MAP_PATH.read_bytes() != EXT_MAP_PATH.read_bytes():
        errors.append("docs map and Extension offline map differ")

    try:
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        if graph.get("source_manifest_sha256") != manifest_hash:
            errors.append("graph source manifest hash is stale")
    except json.JSONDecodeError as exc:
        errors.append(f"graph JSON is invalid: {exc}")

    try:
        report = json.loads(BUILD_REPORT_PATH.read_text(encoding="utf-8"))
        if report.get("source_manifest_sha256") != manifest_hash:
            errors.append("build report source manifest hash is stale")
    except json.JSONDecodeError as exc:
        errors.append(f"build report JSON is invalid: {exc}")

    try:
        notebook = json.loads(NOTEBOOK_MANIFEST_PATH.read_text(encoding="utf-8"))
        if notebook.get("directional_map_manifest_sha256") != manifest_hash:
            errors.append("NotebookLM pack manifest hash is stale")
        expected_sources = manifest["notebooklm"]["source_files"]
        actual_sources = [row.get("path") for row in notebook.get("sources", [])]
        if actual_sources != expected_sources:
            errors.append("NotebookLM source list differs from canonical manifest")
        notebook_text = NOTEBOOK_DOC_PATH.read_text(encoding="utf-8")
        for row in notebook.get("sources", []):
            relative = row.get("path", "")
            source = ROOT / relative
            if not source.exists():
                errors.append(f"NotebookLM source missing after build: {relative}")
                continue
            current_hash = sha256_file(source)
            if row.get("sha256") != current_hash:
                errors.append(f"NotebookLM source hash is stale: {relative}")
            if relative not in notebook_text or current_hash not in notebook_text:
                errors.append(f"NotebookLM combined source lacks path/hash: {relative}")
    except json.JSONDecodeError as exc:
        errors.append(f"NotebookLM source manifest JSON is invalid: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate manifest and generated outputs without writing")
    args = parser.parse_args()
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    if args.check:
        generated_errors = check_generated_outputs(manifest)
        print(
            json.dumps(
                {
                    "ok": not generated_errors,
                    "manifest": "valid",
                    "source_manifest_sha256": sha256_file(MANIFEST_PATH),
                    "generated_outputs": "fresh" if not generated_errors else "stale",
                    "errors": generated_errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1 if generated_errors else 0
    report = write_outputs(manifest)
    print(json.dumps({"ok": True, **report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
