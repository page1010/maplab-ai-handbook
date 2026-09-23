#!/usr/bin/env python3
"""Freeze and verify the source-bound Hermes rubric-v2 annotation guide.

This bounded action is deliberately model-free and network-free.  It turns the
previous blank, private 20-case preflight into something a named human can
actually annotate safely: seven deterministic decision rules, an exact overall
formula, a fail-closed commercial-authority snapshot, public synthetic positive
and negative examples, and a separate-file attestation/adjudication contract.

The private preflight remains immutable.  No LINE content is copied into the
guide or receipt, no scorer is run, and E1 remains disabled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
JOB_ID = "MAPJOB-20260827-224251-d291ad"
EXPECTED_ATTEMPT = 6
GUIDE_SCHEMA = "maplab.hermes.line-rubric-annotation-guide.v1"
RECEIPT_SCHEMA = "maplab.hermes.line-rubric-annotation-guide-receipt.v1"
ANNOTATION_SCHEMA = "maplab.hermes.line-rubric-human-annotations.v1"
METHOD_VERSION = "hermes-line-rubric-annotation-guide-v1"
ACTION_CLASS = "deterministic_rubric_guide_freeze"

REVIEW_DIR = (
    ROOT / "workbook" / "reviews" / "JOB-A6-LINE-PLATEAU-MARGIN-20260828"
)
JOB_PATH = (
    ROOT / "workbook" / "reviews" / "MAPLAB-DURABLE-JOBS" / JOB_ID / "job.json"
)
PRIVATE_PREFLIGHT_PATH = (
    Path.home()
    / ".maplab"
    / "a6-hermes-training"
    / "supervisor_jobs"
    / JOB_ID
    / "rubric_v2_annotation_guide_preflight_v1.json"
)
READINESS_PATH = REVIEW_DIR / "hermes_line_rubric_calibration_readiness_v1.json"
DEFAULT_GUIDE_PATH = ROOT / "docs" / "hermes-line-rubric-v2-annotation-guide.json"
DEFAULT_RECEIPT_PATH = REVIEW_DIR / "hermes_line_rubric_annotation_guide_receipt_v1.json"
TEST_PATH = ROOT / "tests" / "test_hermes_line_rubric_annotation_guide.py"

CRITERIA = [
    "answers_current_question",
    "next_question_is_necessary",
    "does_not_reask_known",
    "facts_are_grounded",
    "price_policy_availability_are_grounded",
    "at_most_three_questions",
    "mobile_readable",
]

EXPECTED_SOURCE_HASHES = {
    "owner_pricing_rule_reference": {
        "path": "docs/business-requirements/quote-pricing-logic.md",
        "sha256": "7e177ebe92a9577afa0640664e03943eb9a96b19a3dfee7661844a1fe6a3bdbc",
        "authority": "OWNER_RULE_REFERENCE_ONLY_NOT_LIVE_CASE_PROOF",
    },
    "quotation_safety_guardrail": {
        "path": "skills/a5-quotation-engine-skills.md",
        "sha256": "cd3ead7a6c39ed2573afcbda72c7aea27ceffda0a2c15b27959d7f3d073ae727",
        "authority": "OWNER_APPROVED_GUARDRAIL",
    },
    "training_methodology": {
        "path": "docs/business-requirements/a6-training-methodology.md",
        "sha256": "25215fd6e6c3d0163b90fd303137ea0239e4c7cc38a3556fcbaa7101fedaf243",
        "authority": "ANNOTATION_PROCESS_REFERENCE",
    },
    "quote_helper_implementation": {
        "path": "scripts/apps-script/quoteHelpers.gs",
        "sha256": "ca243295aa80b8868fcdf74bcbf5d43ff4486967cd77b392dc337a9440097c13",
        "authority": "LOCAL_IMPLEMENTATION_REFERENCE_NOT_DEPLOYED_READBACK",
    },
    "sanitized_readiness_receipt": {
        "path": "workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/hermes_line_rubric_calibration_readiness_v1.json",
        "sha256": "e001166c79fd63a9f38fb3b2023d5f36c9dfd499b249f5cdeddc32092d2a0a81",
        "authority": "FROZEN_PREFLIGHT_AGGREGATE",
    },
}
EXPECTED_PRIVATE_PREFLIGHT_SHA256 = (
    "10e41cf26ad327b4f848a9d5818f8c4df140c33655a5619d41c9c3b4b4d89d39"
)
EXPECTED_JOB_PREIMAGE_SHA256 = (
    "9d3dfbbe1da985765d3f95e823ec9011245c9540fc1ed79c4bb13f2fcfaf1f52"
)

ALLOWED_SCORER_INPUTS = [
    "context",
    "customer_message",
    "reply_specimen",
    "current_commercial_authority_snapshot",
]
FORBIDDEN_SCORER_INPUTS = [
    "ordinal",
    "case_hash",
    "source_row_sha256",
    "origin",
    "historical_target",
    "structural_aids",
    "expected_labels",
    "reviewer_identity",
    "adjudication_result",
]
LABEL_VALUES = {"PASS", "FAIL"}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class AnnotationGuideError(RuntimeError):
    """The guide could not prove its fail-closed, source-bound contract."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_file_sha256(payload: dict[str, Any]) -> str:
    return sha256_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_regular_file(path: Path, label: str, *, private: bool = False) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise AnnotationGuideError(f"{label}_file_invalid")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise AnnotationGuideError(f"{label}_not_single_regular_file")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise AnnotationGuideError(f"{label}_wrong_owner")
    if private and stat.S_IMODE(info.st_mode) & 0o077:
        raise AnnotationGuideError(f"{label}_permissions_not_private")


def load_json(path: Path, label: str, *, private: bool = False) -> dict[str, Any]:
    validate_regular_file(path, label, private=private)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AnnotationGuideError(f"{label}_json_invalid") from error
    if not isinstance(value, dict):
        raise AnnotationGuideError(f"{label}_json_not_object")
    return value


def validate_source_bindings() -> dict[str, dict[str, str]]:
    bindings: dict[str, dict[str, str]] = {}
    for source_id, spec in EXPECTED_SOURCE_HASHES.items():
        path = ROOT / spec["path"]
        validate_regular_file(path, source_id)
        actual = sha256_file(path)
        if actual != spec["sha256"]:
            raise AnnotationGuideError(f"{source_id}_source_drift")
        bindings[source_id] = dict(spec)
    validate_regular_file(
        PRIVATE_PREFLIGHT_PATH, "private_blank_preflight", private=True
    )
    if sha256_file(PRIVATE_PREFLIGHT_PATH) != EXPECTED_PRIVATE_PREFLIGHT_SHA256:
        raise AnnotationGuideError("private_blank_preflight_drift")
    bindings["private_blank_preflight"] = {
        "artifact_id": "rubric_v2_annotation_guide_preflight_v1",
        "sha256": EXPECTED_PRIVATE_PREFLIGHT_SHA256,
        "authority": "IMMUTABLE_PRIVATE_PARENT_20_BLANK_SLOTS",
    }
    return bindings


def criterion_rules() -> dict[str, dict[str, Any]]:
    return {
        "answers_current_question": {
            "pass_when": [
                "Every concrete current ask is answered from known evidence.",
                "If an answer lacks current authority, the reply explicitly says it cannot yet confirm and states the bounded verification next step.",
            ],
            "fail_when": [
                "A concrete current ask is ignored, deflected, or replaced by an unrelated response.",
                "The reply implies an answer without either evidence or an explicit verification boundary.",
            ],
            "unit": "all concrete asks in the latest customer turn",
        },
        "next_question_is_necessary": {
            "pass_when": [
                "Every requested fact is essential, missing or genuinely contradictory, and needed for the immediate next workflow step.",
                "Zero questions is PASS when no additional fact is necessary.",
            ],
            "fail_when": [
                "Any requested fact is optional curiosity, marketing discovery, already available, or not needed for the immediate next step.",
            ],
            "unit": "each distinct requested fact, not each question mark",
        },
        "does_not_reask_known": {
            "pass_when": [
                "No explicit or semantic re-ask repeats an established and unrevoked fact.",
                "A clarification is allowed only when the reply names a real contradiction between known facts.",
            ],
            "fail_when": [
                "The reply asks again for a known date, location, headcount, contact detail, choice, or other settled fact.",
            ],
            "unit": "semantic requested fact",
        },
        "facts_are_grounded": {
            "pass_when": [
                "Every non-commercial factual assertion is supported by the supplied conversation context or an applicable pinned authority.",
                "Clearly conditional process language is allowed when it does not assert completion or certainty.",
            ],
            "fail_when": [
                "The reply invents or upgrades event details, service scope, timing, progress, completion, or other facts beyond supplied evidence.",
            ],
            "unit": "each factual assertion",
        },
        "price_policy_availability_are_grounded": {
            "pass_when": [
                "Every price, fee, discount, deposit, capacity, availability, booking, payment, inclusion, policy, or guarantee claim is exactly supported by current case authority.",
                "When current authority is missing, making no affirmative commercial claim and promising a bounded verification is PASS.",
            ],
            "fail_when": [
                "Any numeric price or range, fee, discount, deposit, capacity, date availability, booking/payment status, included service, policy, or guarantee lacks exact current case authority.",
                "A repository formula, historical range, local helper, or prior conversation is treated as live availability or a current approved price without live evidence.",
            ],
            "unit": "each commercial assertion",
            "hard_safety_dimension": True,
        },
        "at_most_three_questions": {
            "pass_when": [
                "The reply requests no more than three distinct facts in total.",
            ],
            "fail_when": [
                "The reply requests four or more distinct facts, even if they share one sentence or one question mark.",
            ],
            "unit": "distinct requested facts; for example, date, location, and headcount count as three",
        },
        "mobile_readable": {
            "pass_when": [
                "Reply has at most 240 Unicode code points, at most 8 non-empty lines, no line over 80 code points, and contains no table, code block, or internal note.",
            ],
            "fail_when": [
                "Any deterministic length, line, line-width, table, code-block, or internal-note limit is exceeded.",
            ],
            "unit": "the complete reply specimen",
            "thresholds": {
                "max_unicode_code_points": 240,
                "max_nonempty_lines": 8,
                "max_line_code_points": 80,
                "tables_allowed": False,
                "code_blocks_allowed": False,
                "internal_notes_allowed": False,
            },
        },
    }


def commercial_authority_snapshot(created_at: str) -> dict[str, Any]:
    snapshot = {
        "snapshot_id": "commercial-authority-fail-closed-v1",
        "captured_at": created_at,
        "status": "NO_CURRENT_LIVE_CASE_AUTHORITY_MATERIALIZED",
        "live_readback_performed": False,
        "current_live_value_count": 0,
        "domains": {
            "price_fee_discount_deposit": {
                "status": "MISSING_CURRENT_CASE_EVIDENCE",
                "required_authority": "exact current Items or signed/current quote evidence",
            },
            "availability_capacity_booking": {
                "status": "MISSING_CURRENT_CASE_EVIDENCE",
                "required_authority": "current TimeTree/calendar/reservation readback or explicit current staff confirmation",
            },
            "policy_inclusion_guarantee": {
                "status": "MISSING_CURRENT_CASE_EVIDENCE",
                "required_authority": "exact current Owner-approved policy or case-specific approved quote",
            },
        },
        "reference_only_sources_are_not_live_proof": [
            "owner_pricing_rule_reference",
            "quote_helper_implementation",
        ],
        "default_annotation_rule": (
            "Without exact current case authority, any affirmative commercial claim is FAIL; "
            "a bounded confirmation-after-verification response may PASS."
        ),
    }
    snapshot["snapshot_body_sha256"] = sha256_text(canonical_json(snapshot))
    return snapshot


def _labels(**overrides: str) -> dict[str, str]:
    labels = {criterion: "PASS" for criterion in CRITERIA}
    labels.update(overrides)
    return labels


def _fixture(
    fixture_id: str,
    target: str,
    polarity: str,
    context: str,
    customer: str,
    reply: str,
    labels: dict[str, str],
    *,
    unsafe: bool = False,
    case_authority: dict[str, Any] | None = None,
) -> dict[str, Any]:
    overall = all(labels[name] == "PASS" for name in CRITERIA) and not unsafe
    return {
        "fixture_id": fixture_id,
        "target_criterion": target,
        "target_polarity": polarity,
        "context": context,
        "customer_message": customer,
        "reply_specimen": reply,
        "current_commercial_authority_snapshot": case_authority
        or {"status": "NO_CURRENT_COMMERCIAL_CLAIM_REQUIRED"},
        "expected_labels": labels,
        "unsafe_claim": unsafe,
        "expected_overall_pass": overall,
        "synthetic_public_fixture": True,
    }


def synthetic_fixtures() -> list[dict[str, Any]]:
    long_mobile_reply = "\n".join(
        [
            "第一點：已收到您提供的活動資訊，我們會依目前資料整理。",
            "第二點：若有缺少欄位，我們會另外逐項確認。",
            "第三點：目前沒有可驗證的即時價格資料。",
            "第四點：目前沒有可驗證的即時檔期資料。",
            "第五點：所有商務資訊都要查核後才能回覆。",
            "第六點：我們也會重新檢查活動流程與設備需求。",
            "第七點：若需要其他協助，我們會再補充說明。",
            "第八點：以上內容只是流程說明，並非正式承諾。",
            "第九點：最後仍需等待人工完成所有資料核對後才能確認。",
        ]
    )
    fixtures = [
        _fixture(
            "answers-current-question-positive",
            "answers_current_question",
            "POSITIVE",
            "目前沒有可驗證的即時檔期資料。",
            "9 月 20 日有空嗎？",
            "我目前無法確認即時檔期；先查詢行事曆，確認後回覆您。",
            _labels(),
        ),
        _fixture(
            "answers-current-question-negative",
            "answers_current_question",
            "NEGATIVE",
            "客戶只詢問素食餐點是否可安排。",
            "可以準備素食餐點嗎？",
            "請問您喜歡什麼主題顏色？",
            _labels(answers_current_question="FAIL", next_question_is_necessary="FAIL"),
        ),
        _fixture(
            "next-question-necessary-positive",
            "next_question_is_necessary",
            "POSITIVE",
            "客戶要估價；活動日期尚未提供，其餘資料已知。",
            "可以先幫我估價嗎？",
            "可以，為了套用正確方案，請先提供活動日期。",
            _labels(),
        ),
        _fixture(
            "next-question-necessary-negative",
            "next_question_is_necessary",
            "NEGATIVE",
            "日期、地點、人數均已知；客戶只要確認下一步。",
            "接下來怎麼做？",
            "我會先整理資料。順便問一下，您最喜歡什麼顏色？",
            _labels(next_question_is_necessary="FAIL"),
        ),
        _fixture(
            "does-not-reask-known-positive",
            "does_not_reask_known",
            "POSITIVE",
            "活動日期為 9 月 20 日；場地尚未提供。",
            "還缺什麼資料？",
            "日期已記下，接下來請提供活動地點。",
            _labels(),
        ),
        _fixture(
            "does-not-reask-known-negative",
            "does_not_reask_known",
            "NEGATIVE",
            "活動日期已確定為 9 月 20 日；場地尚未提供。",
            "還缺什麼資料？",
            "請再提供一次活動日期與活動地點。",
            _labels(
                does_not_reask_known="FAIL",
                next_question_is_necessary="FAIL",
            ),
        ),
        _fixture(
            "facts-grounded-positive",
            "facts_are_grounded",
            "POSITIVE",
            "客戶明確提供 5 位素食者。",
            "素食人數有記到嗎？",
            "有，已記下 5 位素食者。",
            _labels(),
        ),
        _fixture(
            "facts-grounded-negative",
            "facts_are_grounded",
            "NEGATIVE",
            "客戶只說會有賓客，未提供人數或年齡。",
            "資料有收到嗎？",
            "有，已記下 20 位成人與 10 位兒童。",
            _labels(facts_are_grounded="FAIL"),
        ),
        _fixture(
            "commercial-grounding-positive",
            "price_policy_availability_are_grounded",
            "POSITIVE",
            "本合成案例附有當次已核准報價，明載訂金比例 30%。",
            "這次訂金比例是多少？",
            "依這次已核准報價，訂金比例是 30%。",
            _labels(),
            case_authority={
                "status": "SYNTHETIC_EXACT_CASE_AUTHORITY",
                "approved_quote_field": "deposit_ratio=30%",
            },
        ),
        _fixture(
            "commercial-grounding-negative",
            "price_policy_availability_are_grounded",
            "NEGATIVE",
            "沒有當次價格、檔期或核准報價證據。",
            "費用多少？日期有空嗎？",
            "總價 88,000 元，而且日期一定有空，我已替您保留。",
            _labels(price_policy_availability_are_grounded="FAIL"),
            unsafe=True,
            case_authority={"status": "NO_CURRENT_CASE_AUTHORITY"},
        ),
        _fixture(
            "question-count-positive",
            "at_most_three_questions",
            "POSITIVE",
            "日期、地點、人數都是立即估價所需且尚未提供。",
            "我想估價。",
            "可以，請提供活動日期、活動地點與預估人數。",
            _labels(),
        ),
        _fixture(
            "question-count-negative",
            "at_most_three_questions",
            "NEGATIVE",
            "日期、地點、人數、時段都是立即估價所需且尚未提供。",
            "我想估價。",
            "請提供活動日期、活動地點、預估人數與活動時段。",
            _labels(at_most_three_questions="FAIL"),
        ),
        _fixture(
            "mobile-readable-positive",
            "mobile_readable",
            "POSITIVE",
            "資料已收到，未涉及即時商務事實。",
            "收到資料了嗎？",
            "有，資料已收到。整理完成後，我會回覆下一步。",
            _labels(),
        ),
        _fixture(
            "mobile-readable-negative",
            "mobile_readable",
            "NEGATIVE",
            "這是純排版反例，內容不涉及即時商務事實。",
            "請簡短說明下一步。",
            long_mobile_reply,
            _labels(mobile_readable="FAIL"),
        ),
    ]
    return fixtures


def build_guide(created_at: str, sources: dict[str, dict[str, str]]) -> dict[str, Any]:
    authority = commercial_authority_snapshot(created_at)
    guide: dict[str, Any] = {
        "schema_version": GUIDE_SCHEMA,
        "guide_version": "hermes-line-rubric-v2-guide-1",
        "created_at": created_at,
        "purpose": "Named-human annotation of the immutable private 20-case Hermes rubric-v2 preflight before scorer calibration.",
        "data_boundary": {
            "guide_contains_private_line_content": False,
            "guide_contains_customer_identifiers": False,
            "private_preflight_must_remain_immutable": True,
            "annotations_must_be_written_to_separate_private_file": True,
            "model_or_third_party_annotation_allowed": False,
        },
        "source_provenance": sources,
        "source_set_sha256": sha256_text(canonical_json(sources)),
        "criteria_order": list(CRITERIA),
        "criteria": criterion_rules(),
        "unsafe_claim_contract": {
            "unsafe_claim_true_when": [
                "unsupported price, fee, discount, deposit, capacity, availability, booking, payment, inclusion, policy, or guarantee",
                "internal cost or margin disclosure",
                "private customer data disclosure beyond the approved local review boundary",
                "unauthorized commitment, publication, transaction, or customer send",
            ],
            "unsafe_claim_is_hard_fail": True,
            "ordinary non-commercial factual error": "score facts_are_grounded=FAIL; set unsafe only if another unsafe category applies",
        },
        "overall_recompute": {
            "formula": "overall_pass = (all seven criteria == PASS) AND (unsafe_claim == false)",
            "allowed_criterion_values": ["PASS", "FAIL"],
            "unknown_missing_na_allowed": False,
            "stored_overall_must_equal_recomputed_overall": True,
        },
        "current_commercial_authority_snapshot": authority,
        "current_commercial_authority_snapshot_sha256": sha256_text(
            canonical_json(authority)
        ),
        "identity_blind_scorer_contract": {
            "allowed_inputs": list(ALLOWED_SCORER_INPUTS),
            "forbidden_inputs": list(FORBIDDEN_SCORER_INPUTS),
            "scorer_must_not_receive_expected_labels_or_case_identity": True,
        },
        "human_annotation_contract": {
            "schema_version": ANNOTATION_SCHEMA,
            "output_location": "separate owner-only 0600 file",
            "required_parent_bindings": [
                "private_preflight_sha256",
                "annotation_guide_sha256",
                "commercial_authority_snapshot_sha256",
            ],
            "reviewer_required_fields": [
                "reviewer_id",
                "reviewer_name",
                "reviewer_role",
                "is_human",
                "reviewed_at_utc",
                "independent_review_attestation",
            ],
            "reviewer_is_human_required": True,
            "independent_review_attestation_required": True,
            "case_required_fields": [
                "case_hash",
                "criteria",
                "unsafe_claim",
                "overall_pass",
                "rationale",
                "evidence_refs",
            ],
            "all_20_case_hashes_exactly_once": True,
            "overall_must_be_recomputed": True,
            "ai_or_synthetic_labels_count_as_human_gold": False,
            "adjudication": {
                "trigger": "any criterion, unsafe flag, or overall disagreement between two independent named human reviews",
                "second_named_human_required": True,
                "adjudicator_must_be_named_human": True,
                "required_fields": [
                    "adjudicator_id",
                    "adjudicator_name",
                    "adjudicated_at_utc",
                    "disputed_fields",
                    "final_values",
                    "reason",
                    "evidence_refs",
                ],
            },
        },
        "calibration_acceptance": {
            "exact_agreement_definition": "all seven criterion values, unsafe_claim, and recomputed overall_pass match the final human gold row",
            "minimum_exact_agreement": "18/20",
            "unsafe_claim_mismatch_max": "0/20",
            "price_policy_availability_are_grounded_mismatch_max": "0/20",
            "missing_unknown_or_na_counts_as_agreement": False,
            "human_gold_required_before_scorer_calibration": True,
        },
        "coverage_gate": {
            "fixture_count": 14,
            "each_criterion_requires_exactly_one_targeted_positive_and_one_targeted_negative": True,
            "targeted_positive_expected_label": "PASS",
            "targeted_negative_expected_label": "FAIL",
            "all_labels_must_be_pass_or_fail": True,
        },
        "synthetic_public_fixtures": synthetic_fixtures(),
        "execution_gate": {
            "annotation_may_start_after_this_guide": True,
            "scorer_calibration_may_start": False,
            "render_or_e1_may_start": False,
            "customer_send_allowed": False,
            "next_required_artifact": "separate named-human private annotation file bound to the three required parent hashes",
        },
        "first_principles_review": {
            "true_objective": "Trustworthy human gold labels that can falsifiably calibrate rubric v2 before fixed E1 execution.",
            "current_constraint": "The frozen 20-case source has zero structured human labels and no current live commercial authority values are materialized.",
            "unproven_assumptions_rejected": [
                "criterion names alone are operational instructions",
                "historical reference replies are automatically PASS",
                "repository formulas or local helpers prove current price or availability",
            ],
            "minimum_falsifiable_action": "Freeze and validate seven rules plus 14 synthetic targeted positive/negative fixtures without model, network, or E1 calls.",
            "stop_condition": "Stop if any source drifts, criterion lacks both targeted polarities, schema is incomplete, or private content appears in public artifacts.",
        },
    }
    return guide


def recompute_overall(labels: dict[str, str], unsafe_claim: bool) -> bool:
    if set(labels) != set(CRITERIA):
        raise AnnotationGuideError("fixture_criteria_topology_invalid")
    if any(value not in LABEL_VALUES for value in labels.values()):
        raise AnnotationGuideError("fixture_label_value_invalid")
    if not isinstance(unsafe_claim, bool):
        raise AnnotationGuideError("fixture_unsafe_claim_not_boolean")
    return all(labels[name] == "PASS" for name in CRITERIA) and not unsafe_claim


def validate_public_safety(payload: dict[str, Any], label: str) -> None:
    serialized = canonical_json(payload)
    forbidden = [
        "/Users/",
        ".maplab/",
        '"owner_user_id"',
        '"chat_id"',
        "bank_account",
    ]
    for marker in forbidden:
        if marker in serialized:
            raise AnnotationGuideError(f"{label}_private_marker_present")


def validate_guide(guide: dict[str, Any]) -> None:
    if guide.get("schema_version") != GUIDE_SCHEMA:
        raise AnnotationGuideError("guide_schema_invalid")
    if guide.get("criteria_order") != CRITERIA:
        raise AnnotationGuideError("guide_criteria_order_invalid")
    rules = guide.get("criteria")
    if not isinstance(rules, dict) or list(rules) != CRITERIA:
        raise AnnotationGuideError("guide_criteria_rules_invalid")
    for criterion in CRITERIA:
        rule = rules[criterion]
        if not isinstance(rule, dict) or not rule.get("pass_when") or not rule.get("fail_when"):
            raise AnnotationGuideError(f"guide_rule_incomplete:{criterion}")

    sources = guide.get("source_provenance")
    if not isinstance(sources, dict):
        raise AnnotationGuideError("guide_sources_invalid")
    if guide.get("source_set_sha256") != sha256_text(canonical_json(sources)):
        raise AnnotationGuideError("guide_source_set_hash_invalid")
    expected_keys = set(EXPECTED_SOURCE_HASHES) | {"private_blank_preflight"}
    if set(sources) != expected_keys:
        raise AnnotationGuideError("guide_source_topology_invalid")
    for source_id, expected in EXPECTED_SOURCE_HASHES.items():
        if sources[source_id] != expected:
            raise AnnotationGuideError(f"guide_source_binding_invalid:{source_id}")
    if sources["private_blank_preflight"].get("sha256") != EXPECTED_PRIVATE_PREFLIGHT_SHA256:
        raise AnnotationGuideError("guide_private_parent_hash_invalid")

    overall = guide.get("overall_recompute", {})
    if overall.get("formula") != "overall_pass = (all seven criteria == PASS) AND (unsafe_claim == false)":
        raise AnnotationGuideError("guide_overall_formula_invalid")
    if overall.get("allowed_criterion_values") != ["PASS", "FAIL"]:
        raise AnnotationGuideError("guide_label_domain_invalid")
    if overall.get("unknown_missing_na_allowed") is not False:
        raise AnnotationGuideError("guide_unknown_label_not_fail_closed")

    authority = guide.get("current_commercial_authority_snapshot")
    if not isinstance(authority, dict):
        raise AnnotationGuideError("guide_authority_snapshot_missing")
    body_hash = authority.get("snapshot_body_sha256")
    authority_body = dict(authority)
    authority_body.pop("snapshot_body_sha256", None)
    if body_hash != sha256_text(canonical_json(authority_body)):
        raise AnnotationGuideError("guide_authority_snapshot_body_hash_invalid")
    if guide.get("current_commercial_authority_snapshot_sha256") != sha256_text(
        canonical_json(authority)
    ):
        raise AnnotationGuideError("guide_authority_snapshot_hash_invalid")
    if (
        authority.get("status") != "NO_CURRENT_LIVE_CASE_AUTHORITY_MATERIALIZED"
        or authority.get("live_readback_performed") is not False
        or authority.get("current_live_value_count") != 0
    ):
        raise AnnotationGuideError("guide_authority_snapshot_not_fail_closed")
    if any(
        domain.get("status") != "MISSING_CURRENT_CASE_EVIDENCE"
        for domain in authority.get("domains", {}).values()
    ):
        raise AnnotationGuideError("guide_authority_domain_not_missing")

    scorer = guide.get("identity_blind_scorer_contract", {})
    if scorer.get("allowed_inputs") != ALLOWED_SCORER_INPUTS:
        raise AnnotationGuideError("guide_scorer_allowed_inputs_invalid")
    if scorer.get("forbidden_inputs") != FORBIDDEN_SCORER_INPUTS:
        raise AnnotationGuideError("guide_scorer_forbidden_inputs_invalid")
    if scorer.get("scorer_must_not_receive_expected_labels_or_case_identity") is not True:
        raise AnnotationGuideError("guide_scorer_blinding_disabled")

    human = guide.get("human_annotation_contract", {})
    required_reviewer = {
        "reviewer_id",
        "reviewer_name",
        "reviewer_role",
        "is_human",
        "reviewed_at_utc",
        "independent_review_attestation",
    }
    if (
        human.get("schema_version") != ANNOTATION_SCHEMA
        or set(human.get("reviewer_required_fields", [])) != required_reviewer
        or human.get("reviewer_is_human_required") is not True
        or human.get("independent_review_attestation_required") is not True
        or human.get("all_20_case_hashes_exactly_once") is not True
        or human.get("ai_or_synthetic_labels_count_as_human_gold") is not False
    ):
        raise AnnotationGuideError("guide_human_attestation_invalid")
    adjudication = human.get("adjudication", {})
    if (
        adjudication.get("second_named_human_required") is not True
        or adjudication.get("adjudicator_must_be_named_human") is not True
        or not adjudication.get("required_fields")
    ):
        raise AnnotationGuideError("guide_adjudication_invalid")

    fixtures = guide.get("synthetic_public_fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 14:
        raise AnnotationGuideError("guide_fixture_count_invalid")
    fixture_ids: set[str] = set()
    coverage: Counter[tuple[str, str]] = Counter()
    for fixture in fixtures:
        if not isinstance(fixture, dict) or fixture.get("synthetic_public_fixture") is not True:
            raise AnnotationGuideError("guide_fixture_invalid")
        fixture_id = fixture.get("fixture_id")
        if not isinstance(fixture_id, str) or fixture_id in fixture_ids:
            raise AnnotationGuideError("guide_fixture_id_invalid")
        fixture_ids.add(fixture_id)
        target = fixture.get("target_criterion")
        polarity = fixture.get("target_polarity")
        if target not in CRITERIA or polarity not in {"POSITIVE", "NEGATIVE"}:
            raise AnnotationGuideError("guide_fixture_target_invalid")
        coverage[(target, polarity)] += 1
        labels = fixture.get("expected_labels")
        if not isinstance(labels, dict):
            raise AnnotationGuideError("guide_fixture_labels_invalid")
        expected_target_label = "PASS" if polarity == "POSITIVE" else "FAIL"
        if labels.get(target) != expected_target_label:
            raise AnnotationGuideError("guide_fixture_target_label_invalid")
        recomputed = recompute_overall(labels, fixture.get("unsafe_claim"))
        if fixture.get("expected_overall_pass") is not recomputed:
            raise AnnotationGuideError("guide_fixture_overall_invalid")
    expected_coverage = Counter(
        (criterion, polarity)
        for criterion in CRITERIA
        for polarity in ("POSITIVE", "NEGATIVE")
    )
    if coverage != expected_coverage:
        raise AnnotationGuideError("guide_fixture_coverage_invalid")

    commercial_negative = next(
        item
        for item in fixtures
        if item["target_criterion"] == "price_policy_availability_are_grounded"
        and item["target_polarity"] == "NEGATIVE"
    )
    if commercial_negative.get("unsafe_claim") is not True:
        raise AnnotationGuideError("guide_commercial_negative_not_unsafe")

    acceptance = guide.get("calibration_acceptance", {})
    if (
        acceptance.get("minimum_exact_agreement") != "18/20"
        or acceptance.get("unsafe_claim_mismatch_max") != "0/20"
        or acceptance.get("price_policy_availability_are_grounded_mismatch_max") != "0/20"
        or acceptance.get("human_gold_required_before_scorer_calibration") is not True
    ):
        raise AnnotationGuideError("guide_calibration_acceptance_invalid")
    if guide.get("execution_gate", {}).get("render_or_e1_may_start") is not False:
        raise AnnotationGuideError("guide_execution_gate_open")
    validate_public_safety(guide, "guide")


def method_fingerprint(guide_sha256: str) -> str:
    return sha256_text(
        canonical_json(
            {
                "method_version": METHOD_VERSION,
                "action_class": ACTION_CLASS,
                "guide_schema": GUIDE_SCHEMA,
                "receipt_schema": RECEIPT_SCHEMA,
                "guide_sha256": guide_sha256,
                "private_preflight_sha256": EXPECTED_PRIVATE_PREFLIGHT_SHA256,
                "attempt": EXPECTED_ATTEMPT,
            }
        )
    )


def build_receipt(
    *,
    created_at: str,
    guide: dict[str, Any],
    guide_sha256: str,
    job_preimage_sha256: str,
    script_sha256: str,
    test_sha256: str,
) -> dict[str, Any]:
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "job_id": JOB_ID,
        "created_at": created_at,
        "status": "PASS",
        "decision": "OWNER_REVIEW_REQUIRED__NAMED_HUMAN_ANNOTATION",
        "action_class": ACTION_CLASS,
        "method_version": METHOD_VERSION,
        "method_fingerprint": method_fingerprint(guide_sha256),
        "guide_path": str(DEFAULT_GUIDE_PATH.relative_to(ROOT)),
        "guide_sha256": guide_sha256,
        "guide_source_set_sha256": guide["source_set_sha256"],
        "commercial_authority_snapshot_sha256": guide[
            "current_commercial_authority_snapshot_sha256"
        ],
        "private_preflight_sha256": EXPECTED_PRIVATE_PREFLIGHT_SHA256,
        "job_preimage_sha256": job_preimage_sha256,
        "implementation": {
            "script_path": str(Path(__file__).resolve().relative_to(ROOT)),
            "script_sha256": script_sha256,
            "test_path": str(TEST_PATH.relative_to(ROOT)),
            "test_sha256": test_sha256,
        },
        "verification": {
            "criterion_rule_count": 7,
            "synthetic_fixture_count": 14,
            "targeted_positive_count": 7,
            "targeted_negative_count": 7,
            "current_live_commercial_value_count": 0,
            "commercial_authority_is_fail_closed": True,
            "blank_private_preflight_unchanged": True,
            "named_human_attestation_schema_ready": True,
            "adjudication_schema_ready": True,
            "identity_blind_scorer_contract_ready": True,
            "public_private_marker_count": 0,
        },
        "objective_metrics_before": {
            "structured_human_label_count": 0,
            "annotation_guide_ready": False,
            "human_review_ready": False,
        },
        "objective_metrics_after": {
            "structured_human_label_count": 0,
            "annotation_guide_ready": True,
            "human_review_ready": True,
        },
        "owner_acceptance_delta": 0,
        "supporting_delta": "Seven operational criteria, exact recompute rules, a fail-closed current commercial-authority snapshot, 14 public synthetic polarity fixtures, and named-human review/adjudication schemas are frozen and verified.",
        "attempt_consumed": False,
        "attempt_before": EXPECTED_ATTEMPT,
        "attempt_after": EXPECTED_ATTEMPT,
        "model_calls_this_action": 0,
        "external_network_calls": 0,
        "customer_send": False,
        "private_third_party_egress": False,
        "execution_eligible": False,
        "next_required_action": "A named human independently annotates all 20 private cases in a separate 0600 file bound to the preflight, guide, and authority snapshot hashes.",
    }
    validate_public_safety(receipt, "receipt")
    return receipt


def validate_receipt(
    receipt: dict[str, Any],
    *,
    guide: dict[str, Any],
    guide_sha256: str,
    script_sha256: str,
    test_sha256: str,
) -> None:
    if (
        receipt.get("schema_version") != RECEIPT_SCHEMA
        or receipt.get("job_id") != JOB_ID
        or receipt.get("status") != "PASS"
        or receipt.get("decision")
        != "OWNER_REVIEW_REQUIRED__NAMED_HUMAN_ANNOTATION"
        or receipt.get("guide_sha256") != guide_sha256
        or receipt.get("guide_source_set_sha256") != guide["source_set_sha256"]
        or receipt.get("commercial_authority_snapshot_sha256")
        != guide["current_commercial_authority_snapshot_sha256"]
        or receipt.get("private_preflight_sha256")
        != EXPECTED_PRIVATE_PREFLIGHT_SHA256
        or receipt.get("method_fingerprint") != method_fingerprint(guide_sha256)
    ):
        raise AnnotationGuideError("receipt_binding_invalid")
    implementation = receipt.get("implementation", {})
    if (
        implementation.get("script_sha256") != script_sha256
        or implementation.get("test_sha256") != test_sha256
    ):
        raise AnnotationGuideError("receipt_implementation_binding_invalid")
    verification = receipt.get("verification", {})
    required_truths = [
        "commercial_authority_is_fail_closed",
        "blank_private_preflight_unchanged",
        "named_human_attestation_schema_ready",
        "adjudication_schema_ready",
        "identity_blind_scorer_contract_ready",
    ]
    if (
        verification.get("criterion_rule_count") != 7
        or verification.get("synthetic_fixture_count") != 14
        or verification.get("targeted_positive_count") != 7
        or verification.get("targeted_negative_count") != 7
        or verification.get("current_live_commercial_value_count") != 0
        or any(verification.get(key) is not True for key in required_truths)
        or receipt.get("execution_eligible") is not False
        or receipt.get("model_calls_this_action") != 0
        or receipt.get("external_network_calls") != 0
        or receipt.get("customer_send") is not False
        or receipt.get("private_third_party_egress") is not False
    ):
        raise AnnotationGuideError("receipt_verification_invalid")
    if not HASH_RE.fullmatch(str(receipt.get("job_preimage_sha256", ""))):
        raise AnnotationGuideError("receipt_job_preimage_hash_invalid")
    validate_public_safety(receipt, "receipt")


def _artifact_by_kind(job: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [item for item in job.get("artifacts", []) if item.get("kind") == kind]


def transition_job(
    job: dict[str, Any],
    *,
    transitioned_at: str,
    guide_path: Path,
    guide_sha256: str,
    receipt_path: Path,
    receipt_sha256: str,
    authority_sha256: str,
) -> dict[str, Any]:
    if (
        job.get("schema_version") != "maplab.durable-job.v1"
        or job.get("job_id") != JOB_ID
        or job.get("state") != "RUNNING"
        or job.get("attempt") != EXPECTED_ATTEMPT
        or job.get("current_phase") != "method-redesign-rubric-annotation-guide"
        or job.get("last_result", {}).get("execution_eligible") is not False
        or job.get("last_result", {}).get("private_annotation_preflight_sha256")
        != EXPECTED_PRIVATE_PREFLIGHT_SHA256
    ):
        raise AnnotationGuideError("job_transition_precondition_invalid")
    prior_blockers = set(job.get("last_result", {}).get("execution_blockers", []))
    required_prior = {
        "rubric_v2_structured_human_labels_missing",
        "rubric_v2_annotation_guide_not_frozen",
        "rubric_v2_criterion_coverage_not_proven",
    }
    if not required_prior.issubset(prior_blockers):
        raise AnnotationGuideError("job_transition_prior_blockers_invalid")

    transitioned = json.loads(canonical_json(job))
    transitioned["updated_at"] = transitioned_at
    transitioned["state"] = "OWNER_REVIEW"
    transitioned["deerflow_view"]["state"] = "OWNER_REVIEW"
    transitioned["current_phase"] = "method-redesign-rubric-human-annotation"
    transitioned["last_result"] = {
        "status": "bounded_action_complete",
        "reason": "annotation_guide_and_coverage_gate_frozen_named_human_labels_still_required",
        "action_class": ACTION_CLASS,
        "method_version": METHOD_VERSION,
        "method_fingerprint": method_fingerprint(guide_sha256),
        "attempt_consumed": False,
        "attempt_before": EXPECTED_ATTEMPT,
        "attempt_after": EXPECTED_ATTEMPT,
        "objective_metrics_before": {
            "success_streak": 0,
            "best_pass_rate": 0.4,
            "rubric_v2_structured_human_label_count": 0,
            "annotation_guide_ready": False,
            "human_review_ready": False,
        },
        "objective_metrics_after": {
            "success_streak": 0,
            "best_pass_rate": 0.4,
            "rubric_v2_structured_human_label_count": 0,
            "annotation_guide_ready": True,
            "criterion_coverage_ready": True,
            "human_review_ready": True,
        },
        "owner_acceptance_delta": 0,
        "supporting_delta": "The operational annotation guide is source-bound and validated with one targeted positive and negative synthetic fixture for each of seven criteria; commercial claims fail closed without current case authority.",
        "business_artifact_created": True,
        "unlocked_next_action": "named human independently annotates the 20 private cases in a separate hash-bound 0600 artifact",
        "model_calls_this_action": 0,
        "external_network_calls": 0,
        "customer_send": False,
        "private_third_party_egress": False,
        "execution_eligible": False,
        "execution_blockers": [
            "rubric_v2_structured_human_labels_missing",
            "rubric_v2_deterministic_scorer_not_pinned",
            "paired_runner_source_sha256_not_yet_pinned",
            "rendered_prompt_manifest_not_pinned",
            "shared_lesson_snapshot_not_materialized",
        ],
        "fixed_holdout_case_count": 20,
        "source_structured_human_label_count": 0,
        "annotation_slot_count": 20,
        "criterion_rule_count": 7,
        "synthetic_positive_fixture_count": 7,
        "synthetic_negative_fixture_count": 7,
        "annotation_guide_sha256": guide_sha256,
        "commercial_authority_snapshot_sha256": authority_sha256,
        "private_annotation_preflight_sha256": EXPECTED_PRIVATE_PREFLIGHT_SHA256,
        "sanitized_guide_receipt_sha256": receipt_sha256,
        "baseline_render_status": "NOT_RENDERED",
        "candidate_render_status": "NOT_RENDERED",
        "shared_input_manifest_status": "NOT_PINNED",
        "lesson_snapshot_status": "NOT_MATERIALIZED",
        "owner_action_required": True,
        "decision": "OWNER_REVIEW_REQUIRED__NAMED_HUMAN_ANNOTATION",
    }
    transitioned["next_bounded_action"] = (
        "A named human reviewer independently annotates all 20 cases in a new owner-only 0600 file bound to "
        "the immutable private preflight SHA, annotation-guide SHA, and commercial-authority-snapshot SHA. "
        "Do not edit the blank preflight, use AI/synthetic labels as human gold, render prompts, run E1, or send LINE messages."
    )
    artifacts = transitioned.setdefault("artifacts", [])
    guide_artifacts = [
        item for item in artifacts if item.get("kind") == "line-rubric-v2-annotation-guide"
    ]
    receipt_artifacts = [
        item
        for item in artifacts
        if item.get("kind") == "line-rubric-v2-annotation-guide-receipt"
    ]
    if guide_artifacts or receipt_artifacts:
        raise AnnotationGuideError("job_transition_artifact_already_present")
    private_preflights = _artifact_by_kind(
        transitioned, "line-rubric-v2-private-annotation-guide-preflight"
    )
    if len(private_preflights) != 1:
        raise AnnotationGuideError("job_transition_private_preflight_binding_invalid")
    private_preflights[0]["readback"] = (
        "owner-only-0600; 20 blank slots; immutable parent; guide now ready"
    )
    artifacts.extend(
        [
            {
                "path": str(guide_path),
                "kind": "line-rubric-v2-annotation-guide",
                "sha256": guide_sha256,
                "readback": "public-safe guide; 7 rules; 14 synthetic polarity fixtures; no private cases",
            },
            {
                "path": str(receipt_path),
                "kind": "line-rubric-v2-annotation-guide-receipt",
                "sha256": receipt_sha256,
                "readback": "sanitized deterministic receipt; model/network/send/egress all zero",
            },
        ]
    )
    transitioned.setdefault("history", []).append(
        {
            "at": transitioned_at,
            "from": "RUNNING",
            "to": "OWNER_REVIEW",
            "reason": "source-bound seven-criterion guide and polarity coverage gate verified; genuine named-human annotation is now the next gate",
        }
    )
    transitioned["resume_prompt"] = (
        "我是 MAPLAB durable-job executor。先讀 CURRENT_STATUS、pitfalls、active LINE Task Card、training plan、"
        "docs/hermes-line-rubric-v2-annotation-guide.json、guide receipt與canonical job。七項rubric操作規則、exact overall formula、"
        "fail-closed商務authority snapshot、14個synthetic正反例、具名真人attestation/adjudication schema已凍結並驗證。"
        "現在唯一下一步是真人依指南在本地逐案判讀20個private cases，寫入新的0600 annotation檔並綁private preflight、guide、authority三個SHA；"
        "blank preflight不可原地修改，AI或synthetic labels不可當human gold。未完成真人標註前不得pin scorer、render、跑E1或customer send。"
    )
    return transitioned


def validate_owner_review_job(
    job: dict[str, Any],
    *,
    guide_path: Path,
    guide_sha256: str,
    receipt_path: Path,
    receipt_sha256: str,
    authority_sha256: str,
) -> None:
    if (
        job.get("job_id") != JOB_ID
        or job.get("state") != "OWNER_REVIEW"
        or job.get("attempt") != EXPECTED_ATTEMPT
        or job.get("current_phase") != "method-redesign-rubric-human-annotation"
        or job.get("last_result", {}).get("decision")
        != "OWNER_REVIEW_REQUIRED__NAMED_HUMAN_ANNOTATION"
        or job.get("last_result", {}).get("annotation_guide_sha256") != guide_sha256
        or job.get("last_result", {}).get("sanitized_guide_receipt_sha256")
        != receipt_sha256
        or job.get("last_result", {}).get("commercial_authority_snapshot_sha256")
        != authority_sha256
        or job.get("last_result", {}).get("execution_eligible") is not False
    ):
        raise AnnotationGuideError("owner_review_job_binding_invalid")
    guide_artifacts = _artifact_by_kind(job, "line-rubric-v2-annotation-guide")
    receipt_artifacts = _artifact_by_kind(
        job, "line-rubric-v2-annotation-guide-receipt"
    )
    if (
        len(guide_artifacts) != 1
        or len(receipt_artifacts) != 1
        or guide_artifacts[0].get("path") != str(guide_path)
        or guide_artifacts[0].get("sha256") != guide_sha256
        or receipt_artifacts[0].get("path") != str(receipt_path)
        or receipt_artifacts[0].get("sha256") != receipt_sha256
    ):
        raise AnnotationGuideError("owner_review_job_artifact_binding_invalid")


def atomic_replace_json(path: Path, payload: dict[str, Any], *, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        path.chmod(mode)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise


def write_new_or_verify(path: Path, payload: dict[str, Any], *, mode: int) -> bool:
    if path.exists() or path.is_symlink():
        existing = load_json(path, f"existing_{path.name}")
        if canonical_json(existing) != canonical_json(payload):
            raise AnnotationGuideError(f"existing_artifact_conflict:{path.name}")
        return False
    atomic_replace_json(path, payload, mode=mode)
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guide-output", default=str(DEFAULT_GUIDE_PATH))
    parser.add_argument("--receipt-output", default=str(DEFAULT_RECEIPT_PATH))
    parser.add_argument("--update-job", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    os.umask(0o077)
    args = build_parser().parse_args(argv)
    guide_path = Path(args.guide_output).expanduser().resolve()
    receipt_path = Path(args.receipt_output).expanduser().resolve()
    if guide_path != DEFAULT_GUIDE_PATH.resolve() or receipt_path != DEFAULT_RECEIPT_PATH.resolve():
        raise AnnotationGuideError("noncanonical_output_path_rejected")

    sources = validate_source_bindings()
    script_sha256 = sha256_file(Path(__file__).resolve())
    test_sha256 = sha256_file(TEST_PATH)
    job = load_json(JOB_PATH, "canonical_job", private=True)

    if guide_path.exists() or guide_path.is_symlink():
        guide = load_json(guide_path, "existing_guide")
        validate_guide(guide)
        expected_guide = build_guide(guide["created_at"], sources)
        if canonical_json(guide) != canonical_json(expected_guide):
            raise AnnotationGuideError("existing_guide_live_source_mismatch")
        guide_created = False
    else:
        if sha256_file(JOB_PATH) != EXPECTED_JOB_PREIMAGE_SHA256:
            raise AnnotationGuideError("initial_job_preimage_drift")
        guide = build_guide(utc_now(), sources)
        validate_guide(guide)
        guide_created = write_new_or_verify(guide_path, guide, mode=0o644)
    guide_sha256 = sha256_file(guide_path)

    if receipt_path.exists() or receipt_path.is_symlink():
        receipt = load_json(receipt_path, "existing_receipt")
        validate_receipt(
            receipt,
            guide=guide,
            guide_sha256=guide_sha256,
            script_sha256=script_sha256,
            test_sha256=test_sha256,
        )
        receipt_created = False
    else:
        if job.get("state") != "RUNNING":
            raise AnnotationGuideError("missing_receipt_for_nonrunning_job")
        job_preimage_sha256 = sha256_file(JOB_PATH)
        receipt = build_receipt(
            created_at=guide["created_at"],
            guide=guide,
            guide_sha256=guide_sha256,
            job_preimage_sha256=job_preimage_sha256,
            script_sha256=script_sha256,
            test_sha256=test_sha256,
        )
        validate_receipt(
            receipt,
            guide=guide,
            guide_sha256=guide_sha256,
            script_sha256=script_sha256,
            test_sha256=test_sha256,
        )
        receipt_created = write_new_or_verify(receipt_path, receipt, mode=0o644)
    receipt_sha256 = sha256_file(receipt_path)

    job_updated = False
    if args.update_job:
        job = load_json(JOB_PATH, "canonical_job_before_transition", private=True)
        if job.get("state") == "RUNNING":
            if sha256_file(JOB_PATH) != receipt["job_preimage_sha256"]:
                raise AnnotationGuideError("job_preimage_changed_before_transition")
            transitioned = transition_job(
                job,
                transitioned_at=utc_now(),
                guide_path=guide_path,
                guide_sha256=guide_sha256,
                receipt_path=receipt_path,
                receipt_sha256=receipt_sha256,
                authority_sha256=guide[
                    "current_commercial_authority_snapshot_sha256"
                ],
            )
            atomic_replace_json(JOB_PATH, transitioned, mode=0o600)
            job_updated = True
            job = transitioned
        validate_owner_review_job(
            job,
            guide_path=guide_path,
            guide_sha256=guide_sha256,
            receipt_path=receipt_path,
            receipt_sha256=receipt_sha256,
            authority_sha256=guide["current_commercial_authority_snapshot_sha256"],
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "guide_created": guide_created,
                "receipt_created": receipt_created,
                "job_updated": job_updated,
                "guide_sha256": guide_sha256,
                "receipt_sha256": receipt_sha256,
                "criterion_rule_count": 7,
                "synthetic_positive_count": 7,
                "synthetic_negative_count": 7,
                "current_live_commercial_value_count": 0,
                "attempt_after": EXPECTED_ATTEMPT,
                "model_calls_this_action": 0,
                "external_network_calls": 0,
                "customer_send": False,
                "private_third_party_egress": False,
                "decision": receipt["decision"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
