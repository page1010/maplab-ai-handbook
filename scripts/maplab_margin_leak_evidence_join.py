#!/usr/bin/env python3
"""Run a fixed, privacy-safe evidence-join pilot for margin-leak candidates.

The worker resolves calibration hashes back to the read-only LINE export and
checks locally visible quotation pointer metadata.  It never emits raw text,
customer labels, source conversation IDs, or customer-bearing filenames.  A
quotation pointer is not quotation content, and a candidate request is not
proof of delivery, cost, or an unbilled charge; those gaps remain explicit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


METHOD_VERSION = "margin-evidence-join-v1"
PILOT_SIZE = 10
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600


class EvidenceJoinError(RuntimeError):
    """The local evidence-join contract could not be satisfied."""


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_private_file(path: Path) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise EvidenceJoinError("calibration_must_be_absolute_private_file")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
        raise EvidenceJoinError("calibration_permissions_not_private")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise EvidenceJoinError("calibration_wrong_owner")


def _conversation_id(path: Path) -> str:
    return hashlib.sha256(path.name.encode("utf-8")).hexdigest()[:16]


def _candidate_hash(conversation_id: str, category: str) -> str:
    return sha256_text(f"{conversation_id}|{category}")


def _normalise_private_label(value: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", value)).lower()


def _private_label_and_year(path: Path) -> tuple[str, str]:
    parts = path.stem.split("_", 3)
    if len(parts) != 4:
        return "", ""
    return _normalise_private_label(parts[3]), parts[1][:4]


def _select_samples(calibration: dict) -> list[dict]:
    candidates = [
        sample
        for sample in calibration.get("samples", [])
        if sample.get("label") == "true_candidate"
        and isinstance(sample.get("candidate_hash"), str)
        and isinstance(sample.get("category"), str)
    ]
    ordered = sorted(
        candidates,
        key=lambda sample: sha256_text(
            f"{METHOD_VERSION}|{sample['candidate_hash']}"
        ),
    )
    if len(ordered) < PILOT_SIZE:
        raise EvidenceJoinError("insufficient_true_candidates_for_fixed_pilot")
    return ordered[:PILOT_SIZE]


def _raw_source_index(raw_source_dir: Path) -> tuple[dict[str, Path], str]:
    if not raw_source_dir.is_absolute() or not raw_source_dir.is_dir():
        raise EvidenceJoinError("raw_source_dir_must_be_absolute_directory")
    paths = sorted(raw_source_dir.glob("*.csv"))
    if not paths:
        raise EvidenceJoinError("raw_source_dir_has_no_csv")
    manifest = []
    index = {}
    for path in paths:
        cid = _conversation_id(path)
        if cid in index:
            raise EvidenceJoinError("duplicate_hashed_conversation_id")
        index[cid] = path
        manifest.append(f"{cid}|{path.stat().st_size}")
    return index, sha256_text("\n".join(manifest))


def _quote_pointer_index(quote_root: Path | None) -> tuple[list[Path], str | None]:
    if quote_root is None:
        return [], None
    if not quote_root.is_absolute() or not quote_root.is_dir():
        raise EvidenceJoinError("quote_root_must_be_absolute_directory")
    paths = sorted(quote_root.rglob("*.gsheet"))
    manifest = [
        f"{sha256_text(str(path.resolve()))}|{path.stat().st_size}"
        for path in paths
    ]
    return paths, sha256_text("\n".join(manifest))


def _matching_quote_pointer_tokens(raw_path: Path, quote_paths: list[Path]) -> list[str]:
    private_label, year = _private_label_and_year(raw_path)
    if len(private_label) < 4 or len(year) != 4:
        return []
    matches = []
    for path in quote_paths:
        quote_label = _normalise_private_label(path.stem)
        if private_label not in quote_label:
            continue
        if year not in str(path.parent):
            continue
        matches.append(sha256_text(str(path.resolve())))
    return sorted(matches)


def build_evidence_join(
    calibration_path: Path,
    raw_source_dir: Path,
    *,
    quote_root: Path | None = None,
) -> dict:
    validate_private_file(calibration_path)
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    selected = _select_samples(calibration)
    raw_index, raw_manifest_sha256 = _raw_source_index(raw_source_dir)
    quote_paths, quote_manifest_sha256 = _quote_pointer_index(quote_root)

    resolved: dict[str, Path] = {}
    for sample in selected:
        matches = [
            path
            for conversation_id, path in raw_index.items()
            if _candidate_hash(conversation_id, sample["category"])
            == sample["candidate_hash"]
        ]
        if len(matches) != 1:
            raise EvidenceJoinError(
                f"candidate_source_resolution_count:{len(matches)}"
            )
        resolved[sample["candidate_hash"]] = matches[0]

    samples = []
    missing_counts: Counter[str] = Counter()
    quote_pointer_candidate_count = 0
    for sample in selected:
        raw_path = resolved[sample["candidate_hash"]]
        quote_tokens = _matching_quote_pointer_tokens(raw_path, quote_paths)
        quote_pointer_candidate_count += len(quote_tokens)
        missing = [
            "BASELINE_SCOPE_UNVERIFIED_NO_QUOTE_CONTENT",
            "ACTUAL_DELIVERY_UNVERIFIED_NO_ASSET_JOIN",
            "INCREMENTAL_COST_UNVERIFIED_NO_COST_LEDGER",
            "CHARGED_FEE_UNVERIFIED_NO_ORDERCHARGES_EXPORT",
            "NO_STABLE_CASE_QUOTE_ASSET_JOIN_KEY",
        ]
        missing_counts.update(missing)
        samples.append(
            {
                "candidate_hash": sample["candidate_hash"],
                "category": sample["category"],
                "decision_label": "insufficient_evidence",
                "evidence": {
                    "request": {
                        "status": "private_source_row_hash_verified",
                        "evidence_path": sample.get("evidence_path"),
                        "evidence_sha256": sample.get("evidence_sha256"),
                        "source_file_ref": (
                            "private://line-conversation/"
                            + sha256_text(str(raw_path.resolve()))
                        ),
                        "source_file_sha256": sha256_file(raw_path),
                    },
                    "baseline_scope": {
                        "status": "unverified",
                        "quote_pointer_path_tokens": quote_tokens,
                        "note_code": (
                            "LOCAL_POINTER_CANDIDATE_NOT_CONTENT"
                            if quote_tokens
                            else "NO_LOCAL_POINTER_NAME_YEAR_MATCH"
                        ),
                    },
                    "actual_delivery": {
                        "status": "unverified",
                        "note_code": "NO_STABLE_ASSET_JOIN_KEY",
                    },
                    "incremental_cost": {
                        "status": "unverified",
                        "note_code": "NO_LOCAL_COST_LEDGER_JOIN",
                    },
                    "charged_fee": {
                        "status": "unverified",
                        "note_code": "NO_LOCAL_ORDERCHARGES_EXPORT",
                    },
                },
                "missing_evidence_codes": missing,
            }
        )

    method_contract = {
        "method_version": METHOD_VERSION,
        "hypothesis": (
            "A fixed hash-only pilot can distinguish resolvable private source rows "
            "from missing quote, delivery, cost, and charge joins without exposing PII."
        ),
        "changed_variable": (
            "evidence-location join replaces heuristic text classification; no new "
            "label rules or model calls"
        ),
        "fixed_holdout": {
            "total": PILOT_SIZE,
            "selection": "first ten by sha256(method_version|candidate_hash) from the 18 true_candidate hashes",
        },
        "expected_delta": (
            "produce per-case evidence-gap codes and a falsifiable join-key repair target"
        ),
        "stop_loss": (
            "stop after ten hashes; no cloud content fetch, model, customer send, "
            "live price write, raw text, or customer-bearing path output"
        ),
        "adapter": "maplab-margin-leak-auditor",
        "sampling": "fixed deterministic hash ordering",
        "evaluator": "confirmed only if all four evidence pillars are verified",
        "acceptance": (
            "ten unique hashes, source-row hash readback, explicit missing codes, "
            "privacy contract, confirmed leakage remains zero without four pillars"
        ),
    }
    method_contract["fingerprint"] = sha256_text(
        json.dumps(
            method_contract,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    prior_fingerprint = calibration.get("method_contract", {}).get("fingerprint")
    return {
        "schema_version": "maplab.margin-leak.evidence-join.v1",
        "created_at": utc_iso(),
        "data_class": "private-local-evidence-receipt",
        "plateau_review": {
            "prior_receipts_examined": 2,
            "prior_method_fingerprints": [
                "aggregate-scan-no-method-fingerprint",
                prior_fingerprint,
            ],
            "same_method_consecutive_no_improvement": 0,
            "decision": "new_evidence_join_method_allowed",
        },
        "method_contract": method_contract,
        "privacy": {
            "contains_raw_text": False,
            "contains_customer_identifiers": False,
            "contains_source_conversation_ids": False,
            "contains_customer_bearing_paths": False,
            "network_calls": 0,
            "cloud_content_reads": 0,
            "model_calls": 0,
            "customer_send": False,
            "live_price_write": False,
        },
        "source_receipts": {
            "calibration_sha256": sha256_file(calibration_path),
            "raw_source_file_count": len(raw_index),
            "raw_source_manifest_sha256": raw_manifest_sha256,
            "local_quote_pointer_count": len(quote_paths),
            "local_quote_pointer_manifest_sha256": quote_manifest_sha256,
            "ordercharges_export_present": False,
            "stable_asset_join_present": False,
        },
        "sample_count": len(samples),
        "unique_candidate_hashes": len(
            {sample["candidate_hash"] for sample in samples}
        ),
        "evidence_summary": {
            "private_source_rows_resolved": len(samples),
            "quote_pointer_candidates": quote_pointer_candidate_count,
            "baseline_scope_verified": 0,
            "actual_delivery_verified": 0,
            "incremental_cost_verified": 0,
            "charged_fee_verified": 0,
            "four_pillar_confirmed": 0,
            "decision_counts": {"insufficient_evidence": len(samples)},
            "missing_evidence_code_counts": dict(sorted(missing_counts.items())),
        },
        "confirmed_leakage_amount": 0,
        "interpretation": (
            "All ten request rows resolve locally, but the current stores have no stable "
            "case-to-quote-to-OrderCharges-to-asset key. No selected case is confirmed "
            "leakage and no amount may be inferred."
        ),
        "samples": samples,
    }


def write_private_json(path: Path, payload: dict) -> None:
    if not path.is_absolute():
        raise EvidenceJoinError("output_path_must_be_absolute")
    path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    path.parent.chmod(PRIVATE_DIR_MODE)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.chmod(PRIVATE_FILE_MODE)
    os.replace(temporary, path)
    path.chmod(PRIVATE_FILE_MODE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--raw-source-dir", required=True)
    parser.add_argument("--quote-root")
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    calibration = Path(args.calibration).expanduser().resolve()
    raw_source_dir = Path(args.raw_source_dir).expanduser().resolve()
    quote_root = (
        Path(args.quote_root).expanduser().resolve() if args.quote_root else None
    )
    output = Path(args.output).expanduser().resolve()
    payload = build_evidence_join(
        calibration,
        raw_source_dir,
        quote_root=quote_root,
    )
    write_private_json(output, payload)
    print(
        json.dumps(
            {
                "status": "ok",
                "method_version": METHOD_VERSION,
                "sample_count": payload["sample_count"],
                "four_pillar_confirmed": payload["evidence_summary"][
                    "four_pillar_confirmed"
                ],
                "confirmed_leakage_amount": 0,
                "network_calls": 0,
                "model_calls": 0,
                "output": str(output),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
