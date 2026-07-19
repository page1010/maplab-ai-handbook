from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_cases = load_module("build_eval_cases", "bin/build_eval_cases.py")
run_eval = load_module("run_eval", "bin/run_eval.py")
quota = load_module("quota_sentinel", "bin/quota_sentinel.py")


class PipelineTests(unittest.TestCase):
    def test_fixed_case_counts_and_ids(self) -> None:
        cases = build_cases.investment_cases() + build_cases.seo_cases()
        self.assertEqual(40, len(cases))
        self.assertEqual(40, len({case["case_id"] for case in cases}))
        self.assertTrue(all(case["sensitivity"] == "deidentified" for case in cases))

    def test_candidate_filter_excludes_wrong_entity_and_unapproved_fact(self) -> None:
        case = build_cases.investment_cases()[0]
        selected = run_eval.candidate_facts(case)
        self.assertEqual(["F1"], [item["fact_id"] for item in selected])

    def test_candidate_renderer_passes_all_fixed_checks_without_network(self) -> None:
        cases = build_cases.investment_cases() + build_cases.seo_cases()
        for case in cases:
            selected = run_eval.candidate_facts(case)
            raw = run_eval.deterministic_candidate(case, selected)
            parsed = json.loads(raw)
            checks = run_eval.score(case, raw, parsed, selected)
            self.assertTrue(all(checks.values()), (case["case_id"], checks))

    def test_forbidden_fact_is_rejected(self) -> None:
        case = build_cases.investment_cases()[0]
        raw = json.dumps({
            "subject_id": "ACME",
            "as_of": "2026-07-18",
            "status": "ready",
            "facts_used": ["F2"],
            "summary": "947",
            "missing_data": [],
            "recommended_next_step": "read only",
            "action_decision": "read_only_analysis",
            "confidence": "unknown",
        })
        checks = run_eval.score(case, raw, json.loads(raw), case["input"]["facts"])
        self.assertFalse(checks["fact_provenance"])
        self.assertFalse(checks["forbidden_fact_exclusion"])

    def test_quota_sentinel_never_enables_teacher_jobs_with_unknown_usage(self) -> None:
        status = quota.build_status(ROOT / "config/providers.yml", ROOT / "config/reset_calendar.yml")
        self.assertFalse(status["usage_apis_called"])
        self.assertEqual(0, status["teacher_jobs_created"])
        self.assertEqual("blocked", status["global_teacher_job_decision"])
        self.assertTrue(all(not item["teacher_jobs_allowed"] for item in status["providers"]))


if __name__ == "__main__":
    unittest.main()
