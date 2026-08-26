#!/usr/bin/env python3
"""Deterministically classify a MAPLAB tool candidate without network access."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List


ALLOWED = {
    "kind": {"tool", "skill", "service", "reference", "claim"},
    "identity": {"official_verified", "upstream_verified", "ambiguous", "social_only"},
    "license": {"verified_open", "verified_proprietary", "missing", "unclear", "not_applicable"},
    "maintenance": {"active", "unclear", "stale", "archived"},
    "fit": {"high", "medium", "low", "none"},
    "overlap": {"none", "partial", "substantial", "duplicate"},
    "smoke": {"passed", "not_run", "failed", "not_applicable"},
    "max_allowed": {"public", "approved_brand", "synthetic", "private"},
    "egress": {"none", "public_only", "external_service", "unknown"},
    "credentials": {"none", "api_key", "oauth", "github_read_token", "github_write_token", "llm_key"},
    "side_effects": {"none", "local_files", "dependency_install", "network_read", "external_write", "security_scan", "paid_generation", "publish"},
}


class ContractError(ValueError):
    pass


def _enum(label: str, value: Any) -> str:
    if value not in ALLOWED[label]:
        raise ContractError(f"{label} must be one of {sorted(ALLOWED[label])}; got {value!r}")
    return str(value)


def _enum_list(label: str, values: Any) -> List[str]:
    if not isinstance(values, list) or not values:
        raise ContractError(f"{label} must be a non-empty list")
    return [_enum(label, value) for value in values]


def _require(mapping: Dict[str, Any], key: str, where: str) -> Any:
    if key not in mapping:
        raise ContractError(f"missing {where}.{key}")
    return mapping[key]


def validate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(candidate, dict):
        raise ContractError("candidate must be a JSON object")
    candidate_id = _require(candidate, "candidate_id", "candidate")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ContractError("candidate.candidate_id must be a non-empty string")

    identity = _require(candidate, "identity", "candidate")
    license_info = _require(candidate, "license", "candidate")
    runtime = _require(candidate, "runtime", "candidate")
    data = _require(candidate, "data", "candidate")
    evidence = _require(candidate, "evidence", "candidate")
    for label, value in (("identity", identity), ("license", license_info), ("runtime", runtime), ("data", data), ("evidence", evidence)):
        if not isinstance(value, dict):
            raise ContractError(f"candidate.{label} must be an object")
    runtime_ready = _require(runtime, "ready", "candidate.runtime")
    if not isinstance(runtime_ready, bool):
        raise ContractError("candidate.runtime.ready must be a JSON boolean")

    normalized = {
        "candidate_id": candidate_id.strip(),
        "kind": _enum("kind", _require(candidate, "kind", "candidate")),
        "identity_status": _enum("identity", _require(identity, "status", "candidate.identity")),
        "identity_url": _require(identity, "url", "candidate.identity"),
        "license_status": _enum("license", _require(license_info, "status", "candidate.license")),
        "license_id": license_info.get("id"),
        "maintenance": _enum("maintenance", _require(candidate, "maintenance", "candidate")),
        "fit": _enum("fit", _require(candidate, "fit", "candidate")),
        "overlap": _enum("overlap", _require(candidate, "overlap", "candidate")),
        "runtime_ready": runtime_ready,
        "smoke": _enum("smoke", _require(runtime, "smoke", "candidate.runtime")),
        "max_allowed": _enum("max_allowed", _require(data, "max_allowed", "candidate.data")),
        "egress": _enum("egress", _require(data, "egress", "candidate.data")),
        "credentials": _enum_list("credentials", _require(candidate, "credentials", "candidate")),
        "side_effects": _enum_list("side_effects", _require(candidate, "side_effects", "candidate")),
        "social_url": evidence.get("social_url"),
        "official_urls": _require(evidence, "official_urls", "candidate.evidence"),
        "checked_at": _require(evidence, "checked_at", "candidate.evidence"),
        "note": candidate.get("note", ""),
    }
    if not isinstance(normalized["identity_url"], str):
        raise ContractError("candidate.identity.url must be a string")
    if not isinstance(normalized["official_urls"], list):
        raise ContractError("candidate.evidence.official_urls must be a list")
    if any(not isinstance(url, str) or not url.strip() for url in normalized["official_urls"]):
        raise ContractError("candidate.evidence.official_urls entries must be non-empty strings")
    if normalized["identity_status"] in {"official_verified", "upstream_verified"} and not normalized["official_urls"]:
        raise ContractError("verified identity requires at least one official URL")
    checked_at = normalized["checked_at"]
    if not isinstance(checked_at, str):
        raise ContractError("candidate.evidence.checked_at must be an ISO date")
    try:
        date.fromisoformat(checked_at)
    except ValueError as exc:
        raise ContractError("candidate.evidence.checked_at must be an ISO date") from exc
    if normalized["credentials"] != ["none"] and "none" in normalized["credentials"]:
        raise ContractError("credentials 'none' cannot be combined with another value")
    if normalized["side_effects"] != ["none"] and "none" in normalized["side_effects"]:
        raise ContractError("side_effects 'none' cannot be combined with another value")
    if normalized["egress"] == "public_only" and normalized["max_allowed"] != "public":
        raise ContractError("data.egress 'public_only' requires data.max_allowed 'public'")
    if normalized["egress"] == "external_service" and normalized["max_allowed"] == "private":
        raise ContractError("private data cannot be routed to an external service")
    return normalized


def _result(candidate_id: str, decision: str, reasons: Iterable[str], gates: Iterable[str]) -> Dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "decision": decision,
        "reasons": list(dict.fromkeys(reasons)),
        "required_gates": list(dict.fromkeys(gates)),
    }


def evaluate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    c = validate(candidate)
    cid = c["candidate_id"]

    if c["kind"] in {"reference", "claim"}:
        return _result(cid, "NOT_A_TOOL", ["reference_or_claim_only"], ["keep_as_cited_reference"])
    if c["identity_status"] in {"ambiguous", "social_only"}:
        return _result(cid, "REJECT", ["identity_not_resolved_to_primary_source"], ["exact_official_identity"])
    if c["maintenance"] == "archived":
        return _result(cid, "REJECT", ["upstream_archived"], ["maintained_alternative"])
    if c["overlap"] == "duplicate":
        return _result(cid, "REJECT", ["duplicates_existing_control_plane"], ["use_existing_route"])
    if c["fit"] == "none":
        return _result(cid, "REJECT", ["no_maplab_use_case"], ["none"])
    if c["fit"] == "low" and c["overlap"] in {"substantial", "duplicate"}:
        return _result(cid, "REJECT", ["low_value_and_high_overlap"], ["use_existing_route"])

    hold_reasons: List[str] = []
    hold_gates: List[str] = []
    if c["license_status"] in {"missing", "unclear"}:
        hold_reasons.append("license_or_terms_not_verified")
        hold_gates.append("license_or_service_terms")
    if c["maintenance"] in {"unclear", "stale"}:
        hold_reasons.append("maintenance_not_current")
        hold_gates.append("fresh_upstream_evidence")
    if c["egress"] == "unknown":
        hold_reasons.append("data_egress_unknown")
        hold_gates.append("data_flow_review")
    if c["smoke"] == "failed":
        hold_reasons.append("isolated_smoke_failed")
        hold_gates.append("new_fix_or_capability_change")
    if "github_write_token" in c["credentials"]:
        hold_reasons.append("requires_github_write_token")
        hold_gates.append("explicit_repository_write_authorization")
    if any(effect in c["side_effects"] for effect in {"external_write", "security_scan", "publish"}):
        hold_reasons.append("high_risk_execution_surface")
        hold_gates.append("explicit_target_and_execution_scope")
    if c["egress"] == "external_service" and c["max_allowed"] != "public":
        hold_reasons.append("third_party_processing_boundary")
        hold_gates.append("synthetic_or_public_fixture")
    if "paid_generation" in c["side_effects"]:
        hold_reasons.append("metered_spend_required")
        hold_gates.append("explicit_cost_approval")
    if hold_reasons:
        return _result(cid, "HOLD", hold_reasons, hold_gates)

    external = (
        c["egress"] == "external_service"
        or any(value in c["credentials"] for value in {"api_key", "oauth", "github_read_token", "llm_key"})
        or "paid_generation" in c["side_effects"]
    )
    if external:
        reasons = ["useful_but_requires_external_service_or_credential"]
        gates = ["synthetic_or_public_fixture", "explicit_credential_or_cost_gate", "isolated_receipt"]
        if c["overlap"] == "substantial":
            reasons.append("substantial_overlap_requires_unique_value_proof")
            gates.extend(["document_unique_capability", "isolated_comparison"])
        return _result(cid, "PILOT", reasons, gates)

    if not c["runtime_ready"]:
        return _result(cid, "HOLD", ["runtime_not_ready"], ["runtime_preflight"])
    if c["smoke"] not in {"passed", "not_applicable"}:
        return _result(cid, "HOLD", ["isolated_smoke_missing"], ["isolated_smoke"])
    if c["overlap"] == "substantial":
        return _result(
            cid,
            "PILOT",
            ["substantial_overlap_requires_unique_value_proof"],
            ["document_unique_capability", "isolated_comparison"],
        )
    if c["fit"] != "high":
        return _result(cid, "PILOT", ["fit_requires_bounded_validation"], ["isolated_use_case_smoke"])

    return _result(cid, "ADOPT", ["verified_narrow_and_locally_validated"], ["pin_and_receipt"])


def _load(path: str) -> Dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", help="candidate JSON path, or - for stdin")
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    args = parser.parse_args()
    try:
        result = evaluate(_load(args.candidate))
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
