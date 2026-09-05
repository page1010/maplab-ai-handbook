import importlib.util
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_builder():
    path = ROOT / "tools/ai_workbook/build_extension_task_modules.py"
    spec = importlib.util.spec_from_file_location("build_extension_task_modules", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_remote_builder():
    path = ROOT / "tools/ai_workbook/build_remote_role_handoff.py"
    spec = importlib.util.spec_from_file_location("build_remote_role_handoff", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ExtensionFitnessRoleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.remote = load_remote_builder()
        cls.role = next(role for role in cls.builder.ROLES if role.role_id == "A8-FITNESS")
        cls.module = cls.role.to_module()

    def test_role_sources_and_contract_exist(self):
        expected = {
            "recalls/A8-FITNESS_recall.md",
            "skills/a8-senior-fitness-video-sop.md",
            "handoff/tasks/T-A8-FITNESS-MVP-001.md",
            "projects/a8-senior-fitness-follow-along.md",
        }
        module_sources = {item["path"] for item in self.module["read_first"]}
        self.assertTrue(expected.issubset(module_sources))
        for relative in expected:
            self.assertTrue((ROOT / relative).is_file(), relative)
        expected_outputs = {
            "research/research_brief.md",
            "prompts/movement_plan.json",
            "qa/movement_safety_review.json",
            "render/01-chair-march.mp4",
            "render/05-seated-chest-open.mp4",
            "render/a8-fitness-mvp-compilation-107.5s.mp4",
            "receipts/acceptance/01-chair-march.json",
            "receipts/acceptance/compilation.json",
            "qa/target_device_readback.json",
        }
        self.assertTrue(expected_outputs.issubset(set(self.module["output_contract"])))
        self.assertEqual(
            self.module["writeback"]["task_card"],
            "handoff/tasks/T-A8-FITNESS-MVP-001.md",
        )
        self.assertEqual(
            self.module["writeback"]["default_review_bundle"],
            "workbook/reviews/JOB-A8-SENIOR-FITNESS-MVP-20260901/",
        )

    def test_recall_and_module_share_verifiable_relative_output_paths(self):
        recall = (ROOT / "recalls/A8-FITNESS_recall.md").read_text(encoding="utf-8")
        for relative in self.module["output_contract"]:
            self.builder.validate_safe_relative_path(relative, "test")
            self.assertIn(f"`{relative}`", recall)
        resolved = self.remote.resolve_output_contract(self.module)
        self.assertEqual(len(resolved), len(self.module["output_contract"]))
        self.assertTrue(
            all(path.startswith("workbook/reviews/JOB-A8-SENIOR-FITNESS-MVP-20260901/") for path in resolved)
        )
        with self.assertRaises(ValueError):
            self.builder.validate_safe_relative_path("../escape.json", "test")
        with self.assertRaises(ValueError):
            self.remote.resolve_output_contract(
                {"writeback": {"default_review_bundle": "/tmp"}, "output_contract": ["receipt.json"]}
            )

    def test_safety_rules_reach_generated_module(self):
        serialized = json.dumps(self.module, ensure_ascii=False)
        for token in ("stable chair", "pain", "medical", "qualified human", "five independent short hashes"):
            self.assertIn(token, serialized)

    def test_popup_and_remote_auto_route_include_fitness(self):
        popup = (ROOT / "chrome-extension/popup.js").read_text(encoding="utf-8")
        remote = (ROOT / "tools/ai_workbook/build_remote_role_handoff.py").read_text(encoding="utf-8")
        self.assertIn("role: 'A8-FITNESS'", popup)
        self.assertIn("module.startup_contract", popup)
        self.assertIn("module.verification_required", popup)
        self.assertLess(popup.index("role: 'A8-FITNESS'"), popup.index("role: 'IOS-KOL'"))
        self.assertIn('"A8-FITNESS"', remote)
        self.assertLess(remote.index('"A8-FITNESS"'), remote.index('"A8"'))

        selected, scores = self.remote.auto_route(
            "研究中高齡低衝擊扶椅健身，建立華語跟著動短影音",
            {"A1", "A8", "A8-FITNESS", "B4"},
        )
        self.assertEqual(selected, "A8-FITNESS")
        self.assertGreater(dict(scores)["A8-FITNESS"], dict(scores)["A8"])

        node_probe = r"""
const fs = require('fs');
const source = fs.readFileSync('chrome-extension/popup.js', 'utf8');
const start = source.indexOf('function routeScore');
const end = source.indexOf('async function hydrateRole');
if (start < 0 || end <= start) throw new Error('popup route functions not found');
eval(source.slice(start, end));
process.stdout.write(JSON.stringify(suggestRoleForTask('中高齡低衝擊扶椅健身跟著動 MVP')));
"""
        popup_result = subprocess.run(
            ["node", "-e", node_probe],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(popup_result.stdout)["role"], "A8-FITNESS")

        contract_probe = r"""
const fs = require('fs');
const source = fs.readFileSync('chrome-extension/popup.js', 'utf8');
const start = source.indexOf('function isSafeModuleRelativePath');
const end = source.indexOf('function buildModuleHandoff');
if (start < 0 || end <= start) throw new Error('popup contract helpers not found');
eval(source.slice(start, end));
const module = JSON.parse(fs.readFileSync('chrome-extension/task-modules/A8-FITNESS.json', 'utf8'));
process.stdout.write(JSON.stringify({paths: resolveModuleOutputPaths(module), gate: evaluateModuleReleaseGate(module)}));
"""
        contract_result = subprocess.run(
            ["node", "-e", contract_probe],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        popup_contract = json.loads(contract_result.stdout)
        self.assertEqual(popup_contract["gate"]["state"], "HOLD")
        self.assertIn(
            "workbook/reviews/JOB-A8-SENIOR-FITNESS-MVP-20260901/qa/movement_safety_review.json",
            popup_contract["paths"],
        )

    def test_a8_fitness_inherits_a8_relation_rows(self):
        rows = self.remote.load_relation_rows("A8-FITNESS")
        self.assertTrue(rows)
        self.assertTrue(any("A8" in row.get("used_by_roles", "").split(";") for row in rows))

    def test_pt_gate_fails_closed(self):
        gate = self.module["release_gate"]
        required = gate["required_checks"]
        all_pass = {check: "PASS" for check in required}

        missing_pt = dict(all_pass)
        missing_pt["qualified_movement_professional_review"] = "MISSING"
        self.assertEqual(self.remote.evaluate_release_gate(self.module, missing_pt)["state"], "HOLD")

        lower_case_pt = dict(all_pass)
        lower_case_pt["qualified_movement_professional_review"] = "pass"
        self.assertEqual(self.remote.evaluate_release_gate(self.module, lower_case_pt)["state"], "HOLD")

        self.assertEqual(
            self.remote.evaluate_release_gate(self.module, all_pass)["state"],
            "OWNER_PUBLICATION_REVIEW",
        )

    def test_generated_index_and_a8_source_hashes_are_fresh(self):
        index = json.loads((ROOT / "chrome-extension/task-modules/index.json").read_text(encoding="utf-8"))
        generated = json.loads((ROOT / "chrome-extension/task-modules/A8-FITNESS.json").read_text(encoding="utf-8"))
        entry = next(item for item in index["modules"] if item["role_id"] == "A8-FITNESS")
        self.assertEqual(entry["module_id"], generated["module_id"])
        self.assertEqual(entry["path"], "chrome-extension/task-modules/A8-FITNESS.json")
        self.assertEqual(index["generated_at"], generated["generated_at"])

        sources = {item["path"]: item for item in generated["read_first"]}
        for relative in ("recalls/A8-FITNESS_recall.md", "skills/a8-senior-fitness-video-sop.md"):
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(sources[relative]["source_sha256"], actual)

    def test_remote_cli_auto_route_handoff_is_fail_closed(self):
        command = [
            sys.executable,
            str(ROOT / "tools/ai_workbook/build_remote_role_handoff.py"),
            "--task",
            "中高齡低衝擊扶椅健身跟著動 MVP",
            "--role",
            "AUTO",
            "--runtime",
            "codex",
        ]
        result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertIn("selected_role: A8-FITNESS", result.stdout)
        self.assertIn("task_card_path: handoff/tasks/T-A8-FITNESS-MVP-001.md", result.stdout)
        self.assertIn("release_gate_state: HOLD", result.stdout)
        self.assertIn(
            "workbook/reviews/JOB-A8-SENIOR-FITNESS-MVP-20260901/qa/movement_safety_review.json",
            result.stdout,
        )
        self.assertNotIn("relation_index_gap=true", result.stdout)

    def test_build_report_does_not_declare_stale_xlsx(self):
        report = json.loads((ROOT / "workbook/task_modules/role_module_build_report.json").read_text(encoding="utf-8"))
        self.assertNotIn("workbook/task_modules/role_module_relationships.xlsx", report["outputs"])
        excluded = {item["path"] for item in report["excluded_outputs"]}
        self.assertIn("workbook/task_modules/role_module_relationships.xlsx", excluded)

        graph = json.loads((ROOT / "workbook/task_modules/role_module_relation_graph.json").read_text(encoding="utf-8"))
        self.assertFalse(any(node["id"] == "output:relationship-xlsx" for node in graph["nodes"]))


if __name__ == "__main__":
    unittest.main()
