#!/usr/bin/env python3
"""Build the read-only MAPLAB deployed-source/header inventory receipt.

This is a fail-closed inventory tool, not a deployer.  It reads only local
source/config metadata plus caller-supplied, hash-only Google header
observations.  It never contacts Apps Script, Sheets, LINE, a model, or a
customer-facing system.

The receipt deliberately distinguishes three kinds of truth:

* a local checkout or binding exists;
* the local source digest matches the pinned integration plan; and
* a deployed revision was independently read back.

The first two must never be promoted into the third.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import plistlib
import re
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "maplab.margin.deployed-source-inventory-receipt.v1"
METHOD_VERSION = "margin-deployed-source-inventory-v1"
DATA_CLASS = "private-local-metadata-and-public-schema-hashes"
EXPECTED_CREATED_AT = "2026-08-27T21:06:04.406000+00:00"
PLAN_PATH = Path("docs/margin-leak-case-id-integration-plan.md")
PINNED_PLAN_SHA256 = "e93da7d1c480112118d1e803fc1809faa1129db7101a52b9454cda33bbeb2695"

METHOD_CONTRACT = {
    "hypothesis": (
        "read-only local source, binding, mode, writer-history, and fresh header "
        "metadata can close the current truth boundaries without a live write; "
        "anything not independently readable remains unresolved"
    ),
    "changed_variable": (
        "replace static integration assumptions with local source/deployment "
        "inventory plus connector-derived full-header hashes"
    ),
    "fixed_holdout": (
        "quote GAS, separate LINE GAS, Orders writer, OrderCharges writer, "
        "Case Store root, OpenClaw root, and four full header hashes"
    ),
    "expected_delta": (
        "classify every holdout as verified local truth, unsafe local truth, "
        "or explicit unresolved deployed truth"
    ),
    "stop_loss": (
        "no deployment, Apps Script or Sheet write, source pull, secret movement, "
        "customer row read, private egress, or inference from a local binding"
    ),
    "model": "none",
    "sampling": "fixed-seven-surface-inventory-plus-four-full-header-hashes",
    "evaluator": "deterministic-source-mode-hash-and-history-gates",
    "acceptance": (
        "all local pins and header hashes checked; inaccessible deployed source "
        "and writer authority use UNRESOLVED codes; live adoption remains false"
    ),
}

PLATEAU_REVIEW = {
    "prior_method_fingerprints": (
        "cfe227ba61206a7a1825aa9a960054fe8f9ca6858ac8152819a4ab6c36e09ae0",
        "a1573a74b88222ae10c2b8edcbeaa9c7bdf2f139596df6be6c33db7b2bea2123",
        "201cf84e8090c12ba743f47f9073dc733a87dd7a57874729b6ce302e4c627133",
    ),
    "same_method_repeated": False,
    "verified_improvement_claimed": False,
    "new_repair_point": "read_only_deployed_source_and_header_inventory",
}

PINNED_SOURCE_SHA256 = {
    "scripts/apps-script/.clasp.json": "54d250fd991c659f11b301ae04f73f8e3f0eae2be2d6931392e2f9e99a104bb5",
    "scripts/apps-script/.claspignore": "165d9c88aeaca43de6dccff90eaa0320ccde8de469ce31eb41bd1763c9f715f2",
    "scripts/apps-script/appsscript.json": "40e8bae75f2ccb326ab43e0be04dec610b966f8032f48b8840f0d5895483d14e",
    "scripts/apps-script/Code.gs": "f7dcb4d4b673e3a74a97d00b15621a427451795e6295cd95bcf29fe379c2fbc3",
    "scripts/apps-script/ApiEndpoint.gs": "bffd474cb10aa1d39115ac01ffc8445177d628b795c285486ac93cfcdfc87754",
    "scripts/apps-script/README.md": "0fbccbebeab481a10b75df82bcf9ee6c12cdb0e8426a5fa631dd7d9d115c2cf9",
    "bot_a6/bot_a6.py": "0ad1bba2aa94267427276663695cfabbc8f75e75f06878a8fa46cdeed0cc6774",
    "bot_a6/case_store.py": "5e1e934d3adb1f7d918d72eeef0ef6cc5632d7c52a0d9c52a7138a4772f35007",
    "bot_a6/openclaw_dispatch.py": "dcbb8e1490c1f48c68ff0b4d285c108e5dc3d14c4589c6efc1303a8bcdb9dbc2",
    "bot_a6/run_daemon.sh": "35fc9a95692e54a170b0ed00aa9de0e024699dd1cca2ffc82adc38d77a9c03ba",
    "launchd/com.maplab.a6bot.plist": "8d656716087dda4f1605982f1e463e28cab7770b7a3123c33c07b786876aff1a",
    "tools/ai_workbook/openclaw_adapter.py": "e02ccbd0db33fa277640924171f81c5bb336afe715acf1f48cc46f5de0808aa4",
    "tools/ai_workbook/paths.py": "ed2663e28fe3530f5c5151d30173dd942254b001d0b4443c4b3d4952314b9a2a",
    "workbook/reviews/A6-QUOTE-SHEET-FIRST-20260618/validation_report.md": "b13fa3ab3f92eeea938ab1a4400cbd00454b3fb729cc2a6f5117674b9551e100",
    "skills/credentials/line-bot.md": "7bcf0d15d441e53cc7f8f30d69723693a1e2626a6772ad2608537d11b498649b",
    "AGENT_RULES.md": "0e6152ddc7702ba02467da5dc63168c35ff0b6dfa911c6c91dbc0ae28bd86afb",
}

QUOTE_GAS_SOURCE_FILES = (
    "ApiEndpoint.gs",
    "Code.gs",
    "QuoteForm.html",
    "appsscript.json",
    "contractTerms.gs",
    "generateProposal_v2.gs",
    "quoteHelpers.gs",
    "setup-template.gs",
)
PINNED_QUOTE_GAS_TREE_SHA256 = "4d3014633bf0bc76e716e9570f34c396b0f3f69ad50e49528da8bc4d5cfa4a46"
PINNED_QUOTE_BINDING_FINGERPRINT = "7714b97b541ee0ee73aa4fbfeecf500ff064fe9b3ec718e50496d89b8908440d"

HISTORICAL_EVIDENCE = {
    "quote_script_id_sha256": "9a1e92b9334587ca63b7b241c0c5c672e089e3326a618740a2bc1cad94b2d675",
    "quote_deployment_id_sha256": "f40bc41a8337e9072f44a4a930ee4f60b8f1e2193c177fd71029924f0ce65d07",
    "quote_latest_versioned_receipt_sha256": "b13fa3ab3f92eeea938ab1a4400cbd00454b3fb729cc2a6f5117674b9551e100",
    "line_script_id_sha256": "574c565ce94de0465e54695a7dad5d940760b5e7effb9d327ff02765c06e2f0b",
    "line_deployment_id_sha256": "75a2b1726bfb7e5d27f92d3556d584476e1fe9eadf788b2dd77083c94e8baadd",
    "line_last_observed_date": "2026-05-19",
    "current_deployed_source_complete": False,
}

PINNED_HEADER_SHA256 = {
    "SALES_INTAKE": (15, "b1ac8e43777ffe23e17dc4e0303b07b9d0cc1cbe7de46de03786865c7b3245fd"),
    "Orders": (29, "672d0fa668a436d57a5f8593339839e22c347aabfa2600d00ac59e0bfa2b363e"),
    "OrderCharges": (4, "2b34bd9c0b10b6ff00111ac9724d2e72b2567366491b487bf58dc53114fae949"),
    "MAPLAB_ASSET_LOG": (14, "8ce84e88737b3d906ea1b789a2964a05d499cd3909d46b0906ecc3f7705ff9c9"),
}

EXPECTED_TOKEN_MODE = 0o644
EXPECTED_CASE_DIR_MODE = 0o755
EXPECTED_CASE_FILE_MODE = 0o644
EXPECTED_CASE_FALLBACK_MODE = 0o644
EXPECTED_REVIEW_ROOT_MODE = 0o755
EXPECTED_CONNECTOR_METADATA_READS = 2
EXPECTED_CONNECTOR_HEADER_READS = 7
WRITER_SEARCH_MANIFEST_VERSION = "writer-search-v2"
EXPECTED_WRITER_SOURCE_FILE_COUNT = 67
EXPECTED_TOKEN_SCOPE_COUNT = 3
PINNED_REPO_PATH_FINGERPRINT = "d1420068bbedfdc3b8fb120401a9dca286849e45a5af61f88bc785e25e0d838a"
EXPECTED_OPENCLAW_ARTIFACT_FILE_COUNT = 405
EXPECTED_OPENCLAW_ARTIFACT_MODE_HISTOGRAM = {"0644": 405}

OPENCLAW_BUNDLE_FILENAMES = {
    "task_request.md",
    "output.json",
    "draft.md",
    "execution_log.json",
    "verification_log.json",
    "review_request.md",
    "output_manifest.json",
    "terminal.log",
}


class InventoryError(RuntimeError):
    """Fail-closed error with a stable code."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(f"{code}: {detail}" if detail else code)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_regular_file(path: Path, *, root: Path | None = None) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    if root is not None:
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            return False
    return True


def _file_sha256(path: Path, *, root: Path | None = None) -> str | None:
    if not _safe_regular_file(path, root=root):
        return None
    return _sha256_bytes(path.read_bytes())


def _mode(path: Path) -> int | None:
    if path.is_symlink() or not path.exists():
        return None
    return stat.S_IMODE(path.stat().st_mode)


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _is_sha256_or_none(value: object) -> bool:
    return value is None or _is_sha256(value)


def normalize_header_cells(values: Iterable[object]) -> tuple[str, ...]:
    """Drop connector null placeholders, not the literal string ``null``."""

    normalized: list[str] = []
    for value in values:
        if value is None:
            continue
        if not isinstance(value, str):
            raise InventoryError("HEADER_NON_STRING")
        clean = value.strip()
        if clean:
            normalized.append(clean)
    return tuple(normalized)


def header_sha256(values: Iterable[object]) -> str:
    headers = normalize_header_cells(values)
    payload = json.dumps(headers, ensure_ascii=False, separators=(",", ":"))
    return _sha256_bytes(payload.encode("utf-8"))


def method_fingerprint() -> str:
    return _sha256_bytes(
        _canonical_json(
            {
                "method_version": METHOD_VERSION,
                "created_at": EXPECTED_CREATED_AT,
                "method_contract": METHOD_CONTRACT,
                "source_pins": PINNED_SOURCE_SHA256,
                "quote_tree_pin": PINNED_QUOTE_GAS_TREE_SHA256,
                "quote_binding_fingerprint": PINNED_QUOTE_BINDING_FINGERPRINT,
                "historical_evidence": HISTORICAL_EVIDENCE,
                "header_pins": PINNED_HEADER_SHA256,
                "expected_modes": {
                    "token": EXPECTED_TOKEN_MODE,
                    "case_dir": EXPECTED_CASE_DIR_MODE,
                    "case_file": EXPECTED_CASE_FILE_MODE,
                    "case_fallback": EXPECTED_CASE_FALLBACK_MODE,
                    "review_root": EXPECTED_REVIEW_ROOT_MODE,
                },
                "repo_path_fingerprint": PINNED_REPO_PATH_FINGERPRINT,
                "openclaw_artifact_file_count": EXPECTED_OPENCLAW_ARTIFACT_FILE_COUNT,
                "openclaw_artifact_mode_histogram": EXPECTED_OPENCLAW_ARTIFACT_MODE_HISTOGRAM,
            }
        )
    )


def inspect_source_pins(
    repo_root: Path, overrides: dict[str, bytes] | None = None
) -> list[dict[str, Any]]:
    root = repo_root.resolve()
    rows: list[dict[str, Any]] = []
    for relative, pinned in PINNED_SOURCE_SHA256.items():
        if overrides and relative in overrides:
            actual = _sha256_bytes(overrides[relative])
        else:
            actual = _file_sha256(root / relative, root=root)
        rows.append(
            {
                "path": relative,
                "sha256": actual,
                "pinned_sha256": pinned,
                "matches_pinned": actual == pinned,
                "status": "MATCH" if actual == pinned else "DRIFT",
            }
        )
    return rows


def inspect_plan(repo_root: Path) -> dict[str, Any]:
    actual = _file_sha256(repo_root.resolve() / PLAN_PATH, root=repo_root.resolve())
    return {
        "path": str(PLAN_PATH),
        "sha256": actual,
        "pinned_sha256": PINNED_PLAN_SHA256,
        "matches_pinned": actual == PINNED_PLAN_SHA256,
        "status": "MATCH" if actual == PINNED_PLAN_SHA256 else "DRIFT",
    }


def _tree_sha256(root: Path, names: Iterable[str]) -> str | None:
    parts: list[str] = []
    for name in names:
        digest = _file_sha256(root / name, root=root)
        if digest is None:
            return None
        parts.append(f"{name}\0{digest}\n")
    return _sha256_bytes("".join(parts).encode("utf-8"))


def inspect_quote_gas(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    project = root / "scripts" / "apps-script"
    binding_path = project / ".clasp.json"
    binding_present = _safe_regular_file(binding_path, root=root)
    binding_fingerprint: str | None = None
    if binding_present:
        try:
            binding = json.loads(binding_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InventoryError("QUOTE_BINDING_INVALID") from exc
        script_id = binding.get("scriptId")
        if not isinstance(script_id, str) or not script_id.strip():
            raise InventoryError("QUOTE_BINDING_ID_MISSING")
        binding_fingerprint = _sha256_bytes(
            f"{METHOD_VERSION}\0quote-gas\0{script_id}".encode("utf-8")
        )
    ignore_path = project / ".claspignore"
    ignore_text = (
        ignore_path.read_text(encoding="utf-8")
        if _safe_regular_file(ignore_path, root=root)
        else ""
    )
    source_tree = _tree_sha256(project, QUOTE_GAS_SOURCE_FILES)
    source_tree_match = source_tree == PINNED_QUOTE_GAS_TREE_SHA256
    return {
        "binding_present": binding_present,
        "binding_fingerprint": binding_fingerprint,
        "binding_file_sha256": _file_sha256(binding_path, root=root),
        "selected_source_file_count": len(QUOTE_GAS_SOURCE_FILES),
        "local_source_tree_sha256": source_tree,
        "pinned_source_tree_sha256": PINNED_QUOTE_GAS_TREE_SHA256,
        "local_source_tree_matches_pinned": source_tree_match,
        "line_webhook_excluded": "LineWebhook.gs" in {
            line.strip() for line in ignore_text.splitlines() if line.strip()
        },
        "deployed_revision_sha256": None,
        "status": (
            "LOCAL_BINDING_PRESENT_DEPLOYED_REVISION_UNRESOLVED"
            if binding_present and source_tree_match and "LineWebhook.gs" in {
                line.strip() for line in ignore_text.splitlines() if line.strip()
            }
            else "LOCAL_SOURCE_DRIFT_HOLD"
        ),
    }


def inspect_line_gas(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    declared = root / "scripts" / "apps-script-line"
    exists_or_symlink = declared.exists() or declared.is_symlink()
    trusted_checkout = declared.is_dir() and not declared.is_symlink()
    return {
        "declared_checkout": "scripts/apps-script-line",
        "exists_or_symlink": exists_or_symlink,
        "trusted_checkout": trusted_checkout,
        "binding_fingerprint": None,
        "local_source_tree_sha256": None,
        "deployed_revision_sha256": None,
        "direct_gas_header_capable": False,
        "status": (
            "DECLARED_CHECKOUT_MISSING"
            if not exists_or_symlink
            else "SOURCE_LAYOUT_CHANGED_REVIEW_REQUIRED"
        ),
    }


def _source_files(repo_root: Path) -> tuple[Path, ...]:
    roots = (
        repo_root / "scripts" / "apps-script",
        repo_root / "bot_a6",
        repo_root / "tools" / "ai_workbook",
    )
    allowed = {".gs", ".js", ".mjs", ".ts", ".py", ".sql"}
    files: list[Path] = []
    for base in roots:
        if not base.is_dir() or base.is_symlink():
            continue
        files.extend(
            path
            for path in base.rglob("*")
            if path.suffix in allowed and _safe_regular_file(path, root=repo_root)
        )
    return tuple(sorted(files))


def _git_history_writer_match_count(repo_root: Path) -> int | None:
    command = [
        "git",
        "log",
        "--all",
        "--format=%H",
        "-G",
        (
            r"(getSheetByName[[:space:]]*\([[:space:]]*['\"](Orders|OrderCharges)['\"]"
            r"|['\"](Orders|OrderCharges)![A-Za-z0-9_:]+"
            r"|worksheet[[:space:]]*\([[:space:]]*['\"](Orders|OrderCharges)['\"]"
            r"|INSERT[[:space:]]+INTO[[:space:]]+(Orders|OrderCharges))"
        ),
        "--",
        "*.gs",
        "*.js",
        "*.mjs",
        "*.ts",
        "*.py",
        "*.sql",
    ]
    process = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if process.returncode != 0:
        return None
    return len({line.strip() for line in process.stdout.splitlines() if line.strip()})


def inspect_orders_writer(repo_root: Path) -> dict[str, Any]:
    identity_patterns = (
        re.compile(r"getSheetByName\s*\(\s*['\"](?:Orders|OrderCharges)['\"]"),
        re.compile(r"['\"](?:Orders|OrderCharges)![A-Za-z0-9_:]+"),
        re.compile(r"(?:worksheet|sheet_by_title)\s*\(\s*['\"](?:Orders|OrderCharges)['\"]"),
        re.compile(r"INSERT\s+INTO\s+(?:Orders|OrderCharges)\b", re.IGNORECASE),
    )
    write_patterns = (
        re.compile(r"\bappendRow\s*\("),
        re.compile(r"\bsetValues\s*\("),
        re.compile(r"\bbatchUpdate\s*\("),
        re.compile(r"\bvalues\s*\(\s*\)\s*\.\s*(?:append|update)\s*\("),
        re.compile(r"\b(?:append_rows|update_cells|update_cell)\s*\("),
        re.compile(r"\b(?:INSERT|UPDATE)\b", re.IGNORECASE),
    )
    files = _source_files(repo_root.resolve())
    matching = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in identity_patterns) and any(
            pattern.search(text) for pattern in write_patterns
        ):
            matching += 1
    history_matches = _git_history_writer_match_count(repo_root.resolve())
    return {
        "search_manifest_version": WRITER_SEARCH_MANIFEST_VERSION,
        "current_source_file_count": len(files),
        "current_writer_match_count": matching,
        "git_history_selector_match_count": history_matches,
        "quote_gas_is_authoritative_writer": False,
        "status": (
            "AUTHORITATIVE_WRITER_UNRESOLVED"
            if matching == 0 and history_matches == 0
            else "REVIEW_REQUIRED"
        ),
    }


def _env_key_names(path: Path) -> set[str]:
    if not _safe_regular_file(path):
        return set()
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].removeprefix("export ").strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            names.add(key)
    return names


def _env_value(path: Path, target_key: str) -> str | None:
    """Return one local env value for internal comparison; callers must hash it."""

    if not _safe_regular_file(path):
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        raw_key, raw_value = stripped.split("=", 1)
        key = raw_key.removeprefix("export ").strip()
        if key != target_key:
            continue
        value = raw_value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value
    return None


def _plist_env_key_names(path: Path) -> set[str]:
    if not _safe_regular_file(path):
        return set()
    try:
        payload = plistlib.loads(path.read_bytes())
    except (OSError, plistlib.InvalidFileException) as exc:
        raise InventoryError("PLIST_INVALID") from exc
    env = payload.get("EnvironmentVariables", {})
    return set(env) if isinstance(env, dict) else set()


def _plist_has_owner_only_umask(path: Path) -> bool:
    if not _safe_regular_file(path):
        return False
    try:
        payload = plistlib.loads(path.read_bytes())
    except (OSError, plistlib.InvalidFileException) as exc:
        raise InventoryError("PLIST_INVALID") from exc
    value = payload.get("Umask")
    if isinstance(value, int) and not isinstance(value, bool):
        return value == 0o77
    if isinstance(value, str):
        try:
            return int(value, 8) == 0o77
        except ValueError:
            return False
    return False


def _openclaw_artifact_mode_inventory(review_root: Path) -> dict[str, Any]:
    histogram: dict[str, int] = {}
    regular_count = 0
    owner_only_count = 0
    symlink_count = 0
    if review_root.is_dir() and not review_root.is_symlink():
        for path in review_root.rglob("*"):
            if path.name not in OPENCLAW_BUNDLE_FILENAMES:
                continue
            if path.is_symlink():
                symlink_count += 1
                continue
            if not path.is_file():
                continue
            file_mode = _mode(path)
            if file_mode is None:
                continue
            regular_count += 1
            mode_key = f"{file_mode:04o}"
            histogram[mode_key] = histogram.get(mode_key, 0) + 1
            if file_mode == 0o600:
                owner_only_count += 1
    return {
        "artifact_file_count": regular_count,
        "artifact_file_mode_histogram": dict(sorted(histogram.items())),
        "artifact_owner_only_file_count": owner_only_count,
        "artifact_unsafe_file_count": regular_count - owner_only_count,
        "artifact_symlink_count": symlink_count,
    }


def inspect_private_roots(
    repo_root: Path, installed_plist_path: Path | None = None
) -> dict[str, Any]:
    root = repo_root.resolve()
    installed = installed_plist_path or (
        Path.home() / "Library" / "LaunchAgents" / "com.maplab.a6bot.plist"
    )
    env_keys = _env_key_names(root / "bot_a6" / ".env")
    repo_path_value = _env_value(root / "bot_a6" / ".env", "REPO_PATH")
    repo_path_fingerprint = (
        _sha256_bytes(
            f"{METHOD_VERSION}\0case-store-repo-path\0{repo_path_value}".encode(
                "utf-8"
            )
        )
        if repo_path_value is not None
        else None
    )
    repo_path_matches_root = bool(
        repo_path_value is not None
        and Path(os.path.expandvars(repo_path_value)).expanduser().resolve() == root
    )
    plist_keys = _plist_env_key_names(installed)
    case_dir = root / "data" / "case-store"
    case_db = case_dir / "a6_case_store.sqlite3"
    case_fallback = case_dir / "conversation_log_seed.json"
    review_root = root / "workbook" / "reviews"
    case_dir_mode = _mode(case_dir)
    case_file_mode = _mode(case_db)
    case_fallback_mode = _mode(case_fallback)
    review_mode = _mode(review_root)
    case_fallback_present = _safe_regular_file(case_fallback, root=root)
    case_fallback_owner_only = (
        not case_fallback_present or case_fallback_mode == 0o600
    )
    case_owner_only = (
        case_dir_mode == 0o700
        and case_file_mode == 0o600
        and case_fallback_owner_only
    )
    artifact_modes = _openclaw_artifact_mode_inventory(review_root)
    review_owner_only = (
        review_mode == 0o700
        and artifact_modes["artifact_unsafe_file_count"] == 0
        and artifact_modes["artifact_symlink_count"] == 0
    )
    repo_plist_sha = _file_sha256(root / "launchd" / "com.maplab.a6bot.plist", root=root)
    installed_plist_sha = _file_sha256(installed)
    return {
        "case_store": {
            "path_class": "REPO_CONTAINED",
            "env_override_present": bool(
                {"REPO_PATH", "CASE_STORE_DB_PATH", "CASE_STORE_FALLBACK_JSON"}
                & (env_keys | plist_keys)
            ),
            "repo_path_override_present": repo_path_value is not None,
            "repo_path_fingerprint": repo_path_fingerprint,
            "repo_path_matches_repo_root": repo_path_matches_root,
            "directory_mode": case_dir_mode,
            "database_mode": case_file_mode,
            "fallback_present": case_fallback_present,
            "fallback_mode": case_fallback_mode,
            "fallback_owner_only": case_fallback_owner_only,
            "owner_only": case_owner_only,
            "status": "OWNER_ONLY" if case_owner_only else "REPO_LOCAL_UNSAFE",
        },
        "openclaw": {
            "path_class": "REPO_CONTAINED",
            "env_override_present": bool(
                {"OPENCLAW_ARTIFACT_ROOT", "OPENCLAW_REVIEW_ROOT"}
                & (env_keys | plist_keys)
            ),
            "review_root_mode": review_mode,
            **artifact_modes,
            "owner_only": review_owner_only,
            "status": "OWNER_ONLY" if review_owner_only else "REPO_LOCAL_UNSAFE",
        },
        "launcher": {
            "installed_present": _safe_regular_file(installed),
            "installed_matches_repo": bool(
                repo_plist_sha and installed_plist_sha == repo_plist_sha
            ),
            "runtime_umask_declared_owner_only": _plist_has_owner_only_umask(
                installed
            ),
            "existing_paths_owner_only": case_owner_only and review_owner_only,
        },
    }


def inspect_credential_preflight(token_path: Path | None = None) -> dict[str, Any]:
    path = token_path or (Path.home() / ".claude" / "mcp-keys" / "google-token.json")
    present = _safe_regular_file(path)
    token_mode = _mode(path)
    scope_count = 0
    apps_script_scope_present = False
    if present:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InventoryError("GOOGLE_TOKEN_INVALID") from exc
        scopes = payload.get("scopes", payload.get("scope", ()))
        if isinstance(scopes, str):
            scopes = scopes.split()
        if not isinstance(scopes, list):
            scopes = []
        safe_scopes = [value for value in scopes if isinstance(value, str)]
        scope_count = len(safe_scopes)
        apps_script_scope_present = (
            "https://www.googleapis.com/auth/script.projects.readonly"
            in safe_scopes
        )
    owner_only = token_mode == 0o600
    safe_to_use = present and owner_only and apps_script_scope_present
    if not present:
        status = "TOKEN_MISSING"
    elif not owner_only and not apps_script_scope_present:
        status = "UNSAFE_MODE_AND_APPS_SCRIPT_SCOPE_MISSING"
    elif not owner_only:
        status = "UNSAFE_MODE"
    elif not apps_script_scope_present:
        status = "APPS_SCRIPT_SCOPE_MISSING"
    else:
        status = "SAFE_READBACK_CAPABILITY_PRESENT"
    return {
        "token_present": present,
        "token_mode": token_mode,
        "owner_only": owner_only,
        "scope_count": scope_count,
        "apps_script_scope_present": apps_script_scope_present,
        "safe_for_apps_script_readback": safe_to_use,
        "status": status,
    }


def normalize_header_observations(
    observations: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    supplied: dict[str, dict[str, Any]] = {}
    for observation in observations:
        table = observation.get("table")
        if table in supplied:
            raise InventoryError("DUPLICATE_HEADER_OBSERVATION")
        if table not in PINNED_HEADER_SHA256:
            raise InventoryError("UNKNOWN_HEADER_TABLE")
        field_count = observation.get("field_count")
        digest = observation.get("sha256")
        if type(field_count) is not int or field_count < 1:
            raise InventoryError("HEADER_FIELD_COUNT_INVALID")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise InventoryError("HEADER_SHA256_INVALID")
        expected_count, pinned = PINNED_HEADER_SHA256[table]
        supplied[table] = {
            "table": table,
            "field_count": field_count,
            "sha256": digest,
            "pinned_field_count": expected_count,
            "pinned_sha256": pinned,
            "matches_pinned": field_count == expected_count and digest == pinned,
        }
    if set(supplied) != set(PINNED_HEADER_SHA256):
        raise InventoryError("HEADER_OBSERVATION_SET_INCOMPLETE")
    return [supplied[table] for table in PINNED_HEADER_SHA256]


def build_receipt(
    repo_root: Path,
    created_at: str,
    header_observations: Iterable[dict[str, Any]],
    *,
    connector_metadata_reads: int,
    connector_header_reads: int,
    token_path: Path | None = None,
    installed_plist_path: Path | None = None,
) -> dict[str, Any]:
    try:
        timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InventoryError("TIMESTAMP_INVALID") from exc
    if timestamp.tzinfo is None:
        raise InventoryError("TIMESTAMP_NOT_OFFSET_AWARE")
    if created_at != EXPECTED_CREATED_AT:
        raise InventoryError("TIMESTAMP_CONTRACT_MISMATCH")
    if type(connector_metadata_reads) is not int or connector_metadata_reads < 0:
        raise InventoryError("METADATA_READ_COUNT_INVALID")
    if type(connector_header_reads) is not int or connector_header_reads < 0:
        raise InventoryError("HEADER_READ_COUNT_INVALID")
    if (
        connector_metadata_reads != EXPECTED_CONNECTOR_METADATA_READS
        or connector_header_reads != EXPECTED_CONNECTOR_HEADER_READS
    ):
        raise InventoryError("CONNECTOR_READ_COUNT_CONTRACT_MISMATCH")

    root = repo_root.resolve()
    source_pins = inspect_source_pins(root)
    plan = inspect_plan(root)
    quote = inspect_quote_gas(root)
    line = inspect_line_gas(root)
    writer = inspect_orders_writer(root)
    roots = inspect_private_roots(root, installed_plist_path)
    credential = inspect_credential_preflight(token_path)
    live_headers = normalize_header_observations(header_observations)

    local_pins_match = all(row["matches_pinned"] for row in source_pins)
    headers_match = all(row["matches_pinned"] for row in live_headers)
    private_roots_owner_only = (
        roots["case_store"]["owner_only"] and roots["openclaw"]["owner_only"]
    )
    inventory_complete = (
        local_pins_match
        and plan["matches_pinned"]
        and headers_match
        and quote["status"]
        == "LOCAL_BINDING_PRESENT_DEPLOYED_REVISION_UNRESOLVED"
        and line["status"] == "DECLARED_CHECKOUT_MISSING"
        and writer["status"] == "AUTHORITATIVE_WRITER_UNRESOLVED"
    )
    body = {
        "data_class": DATA_CLASS,
        "method_contract": METHOD_CONTRACT,
        "method_version": METHOD_VERSION,
        "method_fingerprint": method_fingerprint(),
        "plateau_review": PLATEAU_REVIEW,
        "plan_artifact": plan,
        "source_pins": source_pins,
        "historical_evidence": HISTORICAL_EVIDENCE,
        "quote_gas": quote,
        "line_gas": line,
        "orders_writer": writer,
        "private_roots": roots,
        "credential_preflight": credential,
        "live_headers": live_headers,
        "decision": {
            "status": "READ_ONLY_INVENTORY_COMPLETE" if inventory_complete else "HOLD",
            "adoption_status": "HOLD",
            "eligible_for_live_change": False,
            "deployed_source_truth_complete": False,
            "headers_match_pinned": headers_match,
            "private_roots_owner_only": private_roots_owner_only,
            "orders_writer_resolved": False,
            "line_header_capable_ingress_proven": False,
            "confirmed_leakage_amount": 0,
            "next_repair_point": "private_root_and_deployed_readback_hardening_plan",
        },
        "safety": {
            "contains_raw_text": False,
            "contains_customer_identifiers": False,
            "contains_customer_rows": False,
            "contains_raw_google_ids": False,
            "contains_secret_values": False,
            "connector_metadata_reads": connector_metadata_reads,
            "connector_header_reads": connector_header_reads,
            "google_read_operations": connector_metadata_reads + connector_header_reads,
            "google_writes": 0,
            "apps_script_api_calls": 0,
            "deployment_writes": 0,
            "credential_metadata_reads": 1 if credential["token_present"] else 0,
            "credential_network_use": False,
            "credential_writes": 0,
            "model_calls": 0,
            "customer_send": False,
            "price_system_write": False,
            "historical_mutations": 0,
            "new_third_party_private_data_egress": False,
        },
    }
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "created_at": created_at,
        **body,
        "deterministic_body_sha256": _sha256_bytes(
            _canonical_json({"created_at": created_at, **body})
        ),
    }
    validate_receipt(receipt)
    return receipt


def _validate_exact_keys(value: Any, expected: set[str], code: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise InventoryError(code)


def validate_receipt(receipt: dict[str, Any]) -> None:
    _validate_exact_keys(
        receipt,
        {
            "schema_version",
            "created_at",
            "data_class",
            "method_contract",
            "method_version",
            "method_fingerprint",
            "plateau_review",
            "plan_artifact",
            "source_pins",
            "historical_evidence",
            "quote_gas",
            "line_gas",
            "orders_writer",
            "private_roots",
            "credential_preflight",
            "live_headers",
            "decision",
            "safety",
            "deterministic_body_sha256",
        },
        "RECEIPT_TOP_LEVEL_ALLOWLIST",
    )
    if receipt["schema_version"] != SCHEMA_VERSION:
        raise InventoryError("RECEIPT_SCHEMA_VERSION")
    if receipt["data_class"] != DATA_CLASS:
        raise InventoryError("RECEIPT_DATA_CLASS")
    if receipt["method_version"] != METHOD_VERSION:
        raise InventoryError("RECEIPT_METHOD_VERSION")
    if _canonical_json(receipt["method_contract"]) != _canonical_json(METHOD_CONTRACT):
        raise InventoryError("RECEIPT_METHOD_CONTRACT")
    if receipt["method_fingerprint"] != method_fingerprint():
        raise InventoryError("RECEIPT_METHOD_FINGERPRINT")
    if _canonical_json(receipt["plateau_review"]) != _canonical_json(PLATEAU_REVIEW):
        raise InventoryError("RECEIPT_PLATEAU_REVIEW")
    try:
        created = datetime.fromisoformat(
            str(receipt["created_at"]).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise InventoryError("RECEIPT_TIMESTAMP_INVALID") from exc
    if created.tzinfo is None:
        raise InventoryError("RECEIPT_TIMESTAMP_NOT_OFFSET_AWARE")
    if receipt["created_at"] != EXPECTED_CREATED_AT:
        raise InventoryError("RECEIPT_TIMESTAMP_CONTRACT")

    exact_nested = {
        "historical_evidence": {
            "quote_script_id_sha256",
            "quote_deployment_id_sha256",
            "quote_latest_versioned_receipt_sha256",
            "line_script_id_sha256",
            "line_deployment_id_sha256",
            "line_last_observed_date",
            "current_deployed_source_complete",
        },
        "plan_artifact": {"path", "sha256", "pinned_sha256", "matches_pinned", "status"},
        "quote_gas": {
            "binding_present",
            "binding_fingerprint",
            "binding_file_sha256",
            "selected_source_file_count",
            "local_source_tree_sha256",
            "pinned_source_tree_sha256",
            "local_source_tree_matches_pinned",
            "line_webhook_excluded",
            "deployed_revision_sha256",
            "status",
        },
        "line_gas": {
            "declared_checkout",
            "exists_or_symlink",
            "trusted_checkout",
            "binding_fingerprint",
            "local_source_tree_sha256",
            "deployed_revision_sha256",
            "direct_gas_header_capable",
            "status",
        },
        "orders_writer": {
            "search_manifest_version",
            "current_source_file_count",
            "current_writer_match_count",
            "git_history_selector_match_count",
            "quote_gas_is_authoritative_writer",
            "status",
        },
        "credential_preflight": {
            "token_present",
            "token_mode",
            "owner_only",
            "scope_count",
            "apps_script_scope_present",
            "safe_for_apps_script_readback",
            "status",
        },
        "decision": {
            "status",
            "adoption_status",
            "eligible_for_live_change",
            "deployed_source_truth_complete",
            "headers_match_pinned",
            "private_roots_owner_only",
            "orders_writer_resolved",
            "line_header_capable_ingress_proven",
            "confirmed_leakage_amount",
            "next_repair_point",
        },
        "safety": {
            "contains_raw_text",
            "contains_customer_identifiers",
            "contains_customer_rows",
            "contains_raw_google_ids",
            "contains_secret_values",
            "connector_metadata_reads",
            "connector_header_reads",
            "google_read_operations",
            "google_writes",
            "apps_script_api_calls",
            "deployment_writes",
            "credential_metadata_reads",
            "credential_network_use",
            "credential_writes",
            "model_calls",
            "customer_send",
            "price_system_write",
            "historical_mutations",
            "new_third_party_private_data_egress",
        },
    }
    for key, expected in exact_nested.items():
        _validate_exact_keys(receipt[key], expected, f"RECEIPT_{key.upper()}_ALLOWLIST")
    if _canonical_json(receipt["historical_evidence"]) != _canonical_json(
        HISTORICAL_EVIDENCE
    ):
        raise InventoryError("RECEIPT_HISTORICAL_EVIDENCE")
    _validate_exact_keys(
        receipt["private_roots"], {"case_store", "openclaw", "launcher"}, "RECEIPT_ROOTS_ALLOWLIST"
    )
    _validate_exact_keys(
        receipt["private_roots"]["case_store"],
        {
            "path_class",
            "env_override_present",
            "repo_path_override_present",
            "repo_path_fingerprint",
            "repo_path_matches_repo_root",
            "directory_mode",
            "database_mode",
            "fallback_present",
            "fallback_mode",
            "fallback_owner_only",
            "owner_only",
            "status",
        },
        "RECEIPT_CASE_STORE_ALLOWLIST",
    )
    _validate_exact_keys(
        receipt["private_roots"]["openclaw"],
        {
            "path_class",
            "env_override_present",
            "review_root_mode",
            "artifact_file_count",
            "artifact_file_mode_histogram",
            "artifact_owner_only_file_count",
            "artifact_unsafe_file_count",
            "artifact_symlink_count",
            "owner_only",
            "status",
        },
        "RECEIPT_OPENCLAW_ALLOWLIST",
    )
    _validate_exact_keys(
        receipt["private_roots"]["launcher"],
        {"installed_present", "installed_matches_repo", "runtime_umask_declared_owner_only", "existing_paths_owner_only"},
        "RECEIPT_LAUNCHER_ALLOWLIST",
    )

    source_keys = {"path", "sha256", "pinned_sha256", "matches_pinned", "status"}
    if not isinstance(receipt["source_pins"], list):
        raise InventoryError("RECEIPT_SOURCE_LIST")
    if len(receipt["source_pins"]) != len(PINNED_SOURCE_SHA256):
        raise InventoryError("RECEIPT_SOURCE_COUNT")
    source_paths = [row.get("path") for row in receipt["source_pins"] if isinstance(row, dict)]
    if len(source_paths) != len(receipt["source_pins"]) or set(source_paths) != set(
        PINNED_SOURCE_SHA256
    ) or len(source_paths) != len(set(source_paths)):
        raise InventoryError("RECEIPT_SOURCE_MANIFEST")
    for row in receipt["source_pins"]:
        _validate_exact_keys(row, source_keys, "RECEIPT_SOURCE_ALLOWLIST")
        if row["path"] not in PINNED_SOURCE_SHA256:
            raise InventoryError("RECEIPT_SOURCE_PATH")
        pinned = PINNED_SOURCE_SHA256[row["path"]]
        if row["pinned_sha256"] != pinned:
            raise InventoryError("RECEIPT_SOURCE_PIN")
        if not _is_sha256_or_none(row["sha256"]):
            raise InventoryError("RECEIPT_SOURCE_SHA256")
        matches = row["sha256"] == pinned
        if row["matches_pinned"] is not matches or row["status"] != ("MATCH" if matches else "DRIFT"):
            raise InventoryError("RECEIPT_SOURCE_RELATION")

    header_keys = {
        "table",
        "field_count",
        "sha256",
        "pinned_field_count",
        "pinned_sha256",
        "matches_pinned",
    }
    if not isinstance(receipt["live_headers"], list):
        raise InventoryError("RECEIPT_HEADER_LIST")
    if len(receipt["live_headers"]) != len(PINNED_HEADER_SHA256):
        raise InventoryError("RECEIPT_HEADER_COUNT")
    header_tables = [row.get("table") for row in receipt["live_headers"] if isinstance(row, dict)]
    if len(header_tables) != len(receipt["live_headers"]) or set(header_tables) != set(
        PINNED_HEADER_SHA256
    ) or len(header_tables) != len(set(header_tables)):
        raise InventoryError("RECEIPT_HEADER_MANIFEST")
    for row in receipt["live_headers"]:
        _validate_exact_keys(row, header_keys, "RECEIPT_HEADER_ALLOWLIST")
        if row["table"] not in PINNED_HEADER_SHA256:
            raise InventoryError("RECEIPT_HEADER_TABLE")
        count, pinned = PINNED_HEADER_SHA256[row["table"]]
        if row["pinned_field_count"] != count or row["pinned_sha256"] != pinned:
            raise InventoryError("RECEIPT_HEADER_PIN")
        if (
            type(row["field_count"]) is not int
            or row["field_count"] < 1
            or not _is_sha256(row["sha256"])
        ):
            raise InventoryError("RECEIPT_HEADER_VALUE")
        matches = row["field_count"] == count and row["sha256"] == pinned
        if row["matches_pinned"] is not matches:
            raise InventoryError("RECEIPT_HEADER_RELATION")

    serialized = json.dumps(receipt, ensure_ascii=False, sort_keys=True)
    forbidden_keys = (
        "access_token",
        "refresh_token",
        "client_secret",
        "scriptId",
        "spreadsheetId",
        "customer_name",
        "line_user_id",
    )
    if any(key in serialized for key in forbidden_keys) or re.search(r"https?://", serialized):
        raise InventoryError("RECEIPT_FORBIDDEN_VALUE")

    plan = receipt["plan_artifact"]
    if plan["path"] != str(PLAN_PATH) or plan["pinned_sha256"] != PINNED_PLAN_SHA256:
        raise InventoryError("RECEIPT_PLAN_PIN")
    if not _is_sha256_or_none(plan["sha256"]):
        raise InventoryError("RECEIPT_PLAN_SHA256")
    if plan["matches_pinned"] is not (plan["sha256"] == PINNED_PLAN_SHA256):
        raise InventoryError("RECEIPT_PLAN_RELATION")
    if plan["status"] != ("MATCH" if plan["matches_pinned"] else "DRIFT"):
        raise InventoryError("RECEIPT_PLAN_STATUS")

    quote = receipt["quote_gas"]
    quote_digests = (
        quote["binding_fingerprint"],
        quote["binding_file_sha256"],
        quote["local_source_tree_sha256"],
        quote["pinned_source_tree_sha256"],
    )
    if any(not _is_sha256_or_none(value) for value in quote_digests):
        raise InventoryError("RECEIPT_QUOTE_SHA256")
    if type(quote["selected_source_file_count"]) is not int or quote[
        "selected_source_file_count"
    ] != len(QUOTE_GAS_SOURCE_FILES):
        raise InventoryError("RECEIPT_QUOTE_SOURCE_COUNT")
    quote_tree_matches = (
        quote["local_source_tree_sha256"] == quote["pinned_source_tree_sha256"]
    )
    if quote["local_source_tree_matches_pinned"] is not quote_tree_matches:
        raise InventoryError("RECEIPT_QUOTE_TREE_RELATION")
    expected_quote_status = (
        "LOCAL_BINDING_PRESENT_DEPLOYED_REVISION_UNRESOLVED"
        if quote["binding_present"] is True
        and quote_tree_matches
        and quote["line_webhook_excluded"] is True
        else "LOCAL_SOURCE_DRIFT_HOLD"
    )
    if (
        type(quote["binding_present"]) is not bool
        or type(quote["line_webhook_excluded"]) is not bool
        or quote["binding_fingerprint"] != PINNED_QUOTE_BINDING_FINGERPRINT
        or quote["binding_file_sha256"]
        != PINNED_SOURCE_SHA256["scripts/apps-script/.clasp.json"]
        or quote["pinned_source_tree_sha256"] != PINNED_QUOTE_GAS_TREE_SHA256
        or quote["deployed_revision_sha256"] is not None
        or quote["status"] != expected_quote_status
    ):
        raise InventoryError("RECEIPT_QUOTE_BOUNDARY")
    line = receipt["line_gas"]
    if (
        type(line["exists_or_symlink"]) is not bool
        or type(line["trusted_checkout"]) is not bool
        or type(line["direct_gas_header_capable"]) is not bool
    ):
        raise InventoryError("RECEIPT_LINE_TYPE")
    expected_line_status = (
        "DECLARED_CHECKOUT_MISSING"
        if line["exists_or_symlink"] is False
        and line["trusted_checkout"] is False
        else "SOURCE_LAYOUT_CHANGED_REVIEW_REQUIRED"
    )
    if (
        line["declared_checkout"] != "scripts/apps-script-line"
        or line["trusted_checkout"] is True
        and line["exists_or_symlink"] is not True
        or line["direct_gas_header_capable"] is not False
        or line["binding_fingerprint"] is not None
        or line["local_source_tree_sha256"] is not None
        or line["deployed_revision_sha256"] is not None
        or line["status"] != expected_line_status
    ):
        raise InventoryError("RECEIPT_LINE_BOUNDARY")
    writer = receipt["orders_writer"]
    integer_writer_fields = (
        writer["current_source_file_count"],
        writer["current_writer_match_count"],
        writer["git_history_selector_match_count"],
    )
    if any(type(value) is not int or value < 0 for value in integer_writer_fields):
        raise InventoryError("RECEIPT_WRITER_COUNT")
    expected_writer_status = (
        "AUTHORITATIVE_WRITER_UNRESOLVED"
        if writer["current_writer_match_count"] == 0
        and writer["git_history_selector_match_count"] == 0
        else "REVIEW_REQUIRED"
    )
    if (
        writer["search_manifest_version"] != WRITER_SEARCH_MANIFEST_VERSION
        or writer["current_source_file_count"] != EXPECTED_WRITER_SOURCE_FILE_COUNT
        or writer["current_writer_match_count"] != 0
        or writer["git_history_selector_match_count"] != 0
        or writer["quote_gas_is_authoritative_writer"] is not False
        or writer["status"] != expected_writer_status
    ):
        raise InventoryError("RECEIPT_WRITER_BOUNDARY")

    credential = receipt["credential_preflight"]
    roots = receipt["private_roots"]
    case_store = roots["case_store"]
    openclaw = roots["openclaw"]
    launcher = roots["launcher"]
    expected_case_owner_only = (
        case_store["directory_mode"] == 0o700
        and case_store["database_mode"] == 0o600
        and (
            case_store["fallback_present"] is False
            or case_store["fallback_mode"] == 0o600
        )
    )
    expected_fallback_owner_only = (
        case_store["fallback_present"] is False
        or case_store["fallback_mode"] == 0o600
    )
    expected_openclaw_owner_only = (
        openclaw["review_root_mode"] == 0o700
        and openclaw["artifact_unsafe_file_count"] == 0
        and openclaw["artifact_symlink_count"] == 0
    )
    if (
        case_store["path_class"] != "REPO_CONTAINED"
        or case_store["env_override_present"] is not True
        or case_store["repo_path_override_present"] is not True
        or case_store["repo_path_fingerprint"]
        != PINNED_REPO_PATH_FINGERPRINT
        or case_store["repo_path_matches_repo_root"] is not True
        or type(case_store["directory_mode"]) is not int
        or type(case_store["database_mode"]) is not int
        or case_store["directory_mode"] != EXPECTED_CASE_DIR_MODE
        or case_store["database_mode"] != EXPECTED_CASE_FILE_MODE
        or case_store["fallback_present"] is not True
        or type(case_store["fallback_mode"]) is not int
        or case_store["fallback_mode"] != EXPECTED_CASE_FALLBACK_MODE
        or case_store["fallback_owner_only"] is not expected_fallback_owner_only
        or case_store["owner_only"] is not expected_case_owner_only
        or case_store["status"]
        != ("OWNER_ONLY" if expected_case_owner_only else "REPO_LOCAL_UNSAFE")
    ):
        raise InventoryError("RECEIPT_CASE_STORE_BOUNDARY")
    if (
        openclaw["path_class"] != "REPO_CONTAINED"
        or openclaw["env_override_present"] is not False
        or type(openclaw["review_root_mode"]) is not int
        or openclaw["review_root_mode"] != EXPECTED_REVIEW_ROOT_MODE
        or type(openclaw["artifact_file_count"]) is not int
        or openclaw["artifact_file_count"]
        != EXPECTED_OPENCLAW_ARTIFACT_FILE_COUNT
        or openclaw["artifact_file_mode_histogram"]
        != EXPECTED_OPENCLAW_ARTIFACT_MODE_HISTOGRAM
        or type(openclaw["artifact_owner_only_file_count"]) is not int
        or openclaw["artifact_owner_only_file_count"] != 0
        or type(openclaw["artifact_unsafe_file_count"]) is not int
        or openclaw["artifact_unsafe_file_count"]
        != EXPECTED_OPENCLAW_ARTIFACT_FILE_COUNT
        or type(openclaw["artifact_symlink_count"]) is not int
        or openclaw["artifact_symlink_count"] != 0
        or openclaw["artifact_file_count"]
        != (
            openclaw["artifact_owner_only_file_count"]
            + openclaw["artifact_unsafe_file_count"]
        )
        or openclaw["owner_only"] is not expected_openclaw_owner_only
        or openclaw["status"]
        != ("OWNER_ONLY" if expected_openclaw_owner_only else "REPO_LOCAL_UNSAFE")
    ):
        raise InventoryError("RECEIPT_OPENCLAW_BOUNDARY")
    if (
        launcher["installed_present"] is not True
        or launcher["installed_matches_repo"] is not True
        or launcher["runtime_umask_declared_owner_only"] is not True
        or launcher["existing_paths_owner_only"]
        is not (expected_case_owner_only and expected_openclaw_owner_only)
    ):
        raise InventoryError("RECEIPT_LAUNCHER_BOUNDARY")

    expected_credential_owner_only = credential["token_mode"] == 0o600
    expected_credential_safe = (
        credential["token_present"] is True
        and expected_credential_owner_only
        and credential["apps_script_scope_present"] is True
    )
    if not credential["token_present"]:
        expected_credential_status = "TOKEN_MISSING"
    elif not expected_credential_owner_only and not credential[
        "apps_script_scope_present"
    ]:
        expected_credential_status = "UNSAFE_MODE_AND_APPS_SCRIPT_SCOPE_MISSING"
    elif not expected_credential_owner_only:
        expected_credential_status = "UNSAFE_MODE"
    elif not credential["apps_script_scope_present"]:
        expected_credential_status = "APPS_SCRIPT_SCOPE_MISSING"
    else:
        expected_credential_status = "SAFE_READBACK_CAPABILITY_PRESENT"
    if (
        credential["token_present"] is not True
        or type(credential["token_mode"]) is not int
        or credential["token_mode"] != EXPECTED_TOKEN_MODE
        or credential["owner_only"] is not expected_credential_owner_only
        or type(credential["scope_count"]) is not int
        or credential["scope_count"] != EXPECTED_TOKEN_SCOPE_COUNT
        or credential["apps_script_scope_present"] is not False
        or credential["safe_for_apps_script_readback"] is not expected_credential_safe
        or credential["status"] != expected_credential_status
    ):
        raise InventoryError("RECEIPT_CREDENTIAL_RELATION")
    safety = receipt["safety"]
    zero_fields = (
        "google_writes",
        "apps_script_api_calls",
        "deployment_writes",
        "credential_writes",
        "model_calls",
        "historical_mutations",
    )
    false_fields = (
        "contains_raw_text",
        "contains_customer_identifiers",
        "contains_customer_rows",
        "contains_raw_google_ids",
        "contains_secret_values",
        "credential_network_use",
        "customer_send",
        "price_system_write",
        "new_third_party_private_data_egress",
    )
    if any(type(safety[key]) is not int for key in zero_fields):
        raise InventoryError("RECEIPT_SAFETY_ZERO_TYPE")
    if any(safety[key] != 0 for key in zero_fields) or any(
        safety[key] is not False for key in false_fields
    ):
        raise InventoryError("RECEIPT_SAFETY_BOUNDARY")
    integer_safety_fields = (
        "connector_metadata_reads",
        "connector_header_reads",
        "google_read_operations",
        "credential_metadata_reads",
    )
    if any(
        type(safety[key]) is not int or safety[key] < 0
        for key in integer_safety_fields
    ):
        raise InventoryError("RECEIPT_SAFETY_COUNT_TYPE")
    if (
        safety["connector_metadata_reads"] != EXPECTED_CONNECTOR_METADATA_READS
        or safety["connector_header_reads"] != EXPECTED_CONNECTOR_HEADER_READS
        or safety["credential_metadata_reads"] != 1
    ):
        raise InventoryError("RECEIPT_SAFETY_COUNT_CONTRACT")
    if safety["google_read_operations"] != (
        safety["connector_metadata_reads"] + safety["connector_header_reads"]
    ):
        raise InventoryError("RECEIPT_READ_COUNT_RELATION")

    decision = receipt["decision"]
    headers_match = all(row["matches_pinned"] for row in receipt["live_headers"])
    private_owner_only = (
        receipt["private_roots"]["case_store"]["owner_only"]
        and receipt["private_roots"]["openclaw"]["owner_only"]
    )
    inventory_complete = (
        all(row["matches_pinned"] for row in receipt["source_pins"])
        and plan["matches_pinned"]
        and headers_match
        and quote["status"]
        == "LOCAL_BINDING_PRESENT_DEPLOYED_REVISION_UNRESOLVED"
        and line["status"] == "DECLARED_CHECKOUT_MISSING"
        and writer["status"] == "AUTHORITATIVE_WRITER_UNRESOLVED"
    )
    expected_status = "READ_ONLY_INVENTORY_COMPLETE" if inventory_complete else "HOLD"
    if (
        decision["status"] != expected_status
        or decision["adoption_status"] != "HOLD"
        or decision["eligible_for_live_change"] is not False
        or decision["deployed_source_truth_complete"] is not False
        or decision["headers_match_pinned"] is not headers_match
        or decision["private_roots_owner_only"] is not private_owner_only
        or decision["orders_writer_resolved"] is not False
        or decision["line_header_capable_ingress_proven"] is not False
        or type(decision["confirmed_leakage_amount"]) is not int
        or decision["confirmed_leakage_amount"] != 0
        or decision["next_repair_point"]
        != "private_root_and_deployed_readback_hardening_plan"
    ):
        raise InventoryError("RECEIPT_DECISION_BOUNDARY")

    body = {
        key: value
        for key, value in receipt.items()
        if key not in {"schema_version", "deterministic_body_sha256"}
    }
    if receipt["deterministic_body_sha256"] != _sha256_bytes(_canonical_json(body)):
        raise InventoryError("RECEIPT_BODY_SHA256")


def _reject_symlink_components(path: Path) -> None:
    current = path
    while current != current.parent:
        if current.exists() and current.is_symlink():
            raise InventoryError("OUTPUT_PATH_SYMLINK_FORBIDDEN")
        current = current.parent


def write_private_receipt(path: Path, receipt: dict[str, Any]) -> None:
    validate_receipt(receipt)
    target = path.expanduser()
    if not target.is_absolute():
        raise InventoryError("OUTPUT_PATH_MUST_BE_ABSOLUTE")
    _reject_symlink_components(target)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _reject_symlink_components(target.parent)
    os.chmod(target.parent, 0o700)
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise InventoryError("OUTPUT_TARGET_MUST_BE_REGULAR_FILE")
    payload = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
        os.chmod(target, 0o600)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    if _mode(target) != 0o600 or _mode(target.parent) != 0o700:
        raise InventoryError("OUTPUT_PERMISSIONS_NOT_PRIVATE")
    validate_receipt(json.loads(target.read_text(encoding="utf-8")))


def _parse_header_arg(value: str) -> dict[str, Any]:
    try:
        table, count, digest = value.split(":", 2)
        return {"table": table, "field_count": int(count), "sha256": digest}
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("expected TABLE:FIELD_COUNT:SHA256") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the no-write MAPLAB deployed-source/header inventory"
    )
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--created-at")
    parser.add_argument("--header", action="append", type=_parse_header_arg, required=True)
    parser.add_argument("--connector-metadata-reads", type=int, required=True)
    parser.add_argument("--connector-header-reads", type=int, required=True)
    args = parser.parse_args()
    receipt = build_receipt(
        args.repo_root,
        args.created_at or EXPECTED_CREATED_AT,
        args.header,
        connector_metadata_reads=args.connector_metadata_reads,
        connector_header_reads=args.connector_header_reads,
    )
    write_private_receipt(args.receipt, receipt)
    summary = {
        "method_version": METHOD_VERSION,
        "method_fingerprint": receipt["method_fingerprint"],
        "decision": receipt["decision"]["status"],
        "headers_match_pinned": receipt["decision"]["headers_match_pinned"],
        "deployed_source_truth_complete": False,
        "google_writes": 0,
        "customer_send": False,
    }
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0 if receipt["decision"]["status"] == "READ_ONLY_INVENTORY_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
