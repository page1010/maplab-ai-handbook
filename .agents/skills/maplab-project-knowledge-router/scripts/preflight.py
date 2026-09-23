#!/usr/bin/env python3
"""Read-only preflight for the existing MAPLAB project knowledge routes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).expanduser().resolve()
    router_path = root / "config/notebooklm/maplab-project-brain-router.json"
    required = {
        "current_status": root / "CURRENT_STATUS.md",
        "pitfalls": root / "pitfalls.md",
        "graph_ignore": root / ".graphifyignore",
        "graph_json": root / "graphify-out/graph.json",
        "graph_html": root / "graphify-out/graph.html",
        "graph_report": root / "graphify-out/GRAPH_REPORT.md",
        "notebook_router": router_path,
        "notebook_manifest": root / "workbook/notebooklm/maplab-project-brain/source-manifest.json",
    }
    checks = {name: path.exists() for name, path in required.items()}
    source_checks: list[dict[str, object]] = []
    refresh_command = "python3 tools/ai_workbook/build_directional_system_map.py"

    if router_path.exists():
        router = json.loads(router_path.read_text(encoding="utf-8"))
        refresh_command = router.get("refresh_command", refresh_command)
        for entry in router.get("source_packs", []):
            relative = entry.get("path", "")
            path = root / relative
            actual = sha256(path) if path.is_file() else None
            expected = entry.get("sha256")
            source_checks.append(
                {
                    "path": relative,
                    "exists": path.is_file(),
                    "hash_matches_router": actual == expected if actual else False,
                }
            )

    graphify_bin = shutil.which("graphify")
    graph_report = required["graph_report"]
    built_commit = None
    if graph_report.is_file():
        match = re.search(
            r"Built from commit:\s*`([0-9a-fA-F]+)`",
            graph_report.read_text(encoding="utf-8"),
        )
        built_commit = match.group(1).lower() if match else None
    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    repo_head = head_result.stdout.strip().lower() if head_result.returncode == 0 else None
    graph_fresh = bool(built_commit and repo_head and repo_head.startswith(built_commit))
    files_ready = all(checks.values())
    packs_ready = bool(source_checks) and all(
        item["exists"] and item["hash_matches_router"] for item in source_checks
    )
    graph_ready = checks["graph_json"] and checks["graph_html"] and bool(graphify_bin) and graph_fresh
    notebook_ready = checks["notebook_router"] and checks["notebook_manifest"] and packs_ready
    ready = files_ready and graph_ready and notebook_ready
    if ready:
        status = "ready"
    elif not files_ready or not graphify_bin:
        status = "missing_dependency"
    else:
        status = "needs_refresh"

    result = {
        "status": status,
        "repo_root": str(root),
        "graphify_binary": graphify_bin,
        "graph_built_commit": built_commit,
        "repo_head": repo_head,
        "graph_fresh": graph_fresh,
        "required_files": checks,
        "source_packs": source_checks,
        "routes": {
            "graphify": {
                "status": "ready" if graph_ready else "needs_refresh",
                "refresh_command": "graphify update .",
            },
            "notebooklm": {
                "status": "ready" if notebook_ready else "needs_refresh",
                "refresh_command": refresh_command,
            },
        },
        "boundaries": {
            "graphify": "code topology only",
            "notebooklm": "sanitized navigation only",
            "live_readback": "required for current external or runtime claims",
        },
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(status)
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
