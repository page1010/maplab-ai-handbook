import json
import tempfile
import unittest
from pathlib import Path

from tools.ai_workbook import build_directional_system_map as system_map


class DirectionalSystemMapTest(unittest.TestCase):
    def setUp(self):
        self.manifest = system_map.load_manifest()

    def test_manifest_has_exact_views_and_a2_to_a8_workflows(self):
        self.assertEqual([], system_map.validate_manifest(self.manifest))
        self.assertEqual(system_map.EXPECTED_VIEWS, {item["id"] for item in self.manifest["views"]})
        self.assertEqual(system_map.EXPECTED_WORKFLOWS, {item["id"] for item in self.manifest["workflows"]})

    def test_graph_has_workflow_artifact_tool_gate_and_evidence_nodes(self):
        graph = system_map.graph_from_manifest(self.manifest)
        node_types = {node["type"] for node in graph["nodes"]}
        self.assertTrue({"workflow", "workflow_stage", "artifact", "tool", "approval_gate", "evidence"}.issubset(node_types))
        self.assertGreater(len(graph["nodes"]), 150)
        self.assertGreater(len(graph["edges"]), 200)

    def test_html_has_all_views_and_no_investment_detail_nodes(self):
        graph = system_map.graph_from_manifest(self.manifest)
        rendered = system_map.render_html(self.manifest, graph)
        for view in system_map.EXPECTED_VIEWS:
            self.assertIn(f'data-view="{view}"', rendered)
        self.assertNotIn("持股 ledger", rendered)
        self.assertNotIn("TWSE 官方報價", rendered)

    def test_secret_value_redaction_preserves_policy_words(self):
        sample = "token: abcdefghijklmnopqrstuvwxyz\npolicy says token values are excluded\nghp_abcdefghijklmnopqrstuvwxyz123456"
        sanitized, count = system_map.redact_secret_values(sample)
        self.assertGreaterEqual(count, 2)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", sanitized)
        self.assertIn("policy says token values are excluded", sanitized)
        self.assertFalse(any(pattern.search(sanitized) for pattern in system_map.SECRET_VALUE_PATTERNS))

    def test_manifest_json_and_schema_json_parse(self):
        for path in (system_map.MANIFEST_PATH, system_map.SCHEMA_PATH):
            with self.subTest(path=path):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_generated_outputs_match_current_manifest_and_sources(self):
        self.assertEqual([], system_map.check_generated_outputs(self.manifest))

    def test_notebooklm_router_has_two_supported_packs_and_local_fallback(self):
        notebook = self.manifest["notebooklm"]
        self.assertTrue(notebook["notebook_url"].startswith("https://notebook.google.com/notebook/"))
        self.assertGreaterEqual(len(notebook["sop_source_files"]), 15)
        self.assertEqual(len(notebook["sop_source_files"]), len(set(notebook["sop_source_files"])))
        routed_sops = {path for workflow in self.manifest["workflows"] for path in workflow["sop_paths"]}
        self.assertTrue(routed_sops.issubset(set(notebook["sop_source_files"])))

        source_manifest = json.loads(system_map.NOTEBOOK_MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(2, len(source_manifest["upload_files"]))
        self.assertTrue(all(path.endswith(".md") for path in source_manifest["upload_files"]))
        self.assertNotIn(str(system_map.NOTEBOOK_MANIFEST_PATH.relative_to(system_map.ROOT)), source_manifest["upload_files"])

        router = json.loads(system_map.NOTEBOOK_ROUTER_PATH.read_text(encoding="utf-8"))
        self.assertTrue(router["online_route"]["requires_browser_operator"])
        self.assertIn("maplab-sop-router.md", " ".join(router["local_model_route"]["read_first"]))
        self.assertEqual(["FOUND", "NEEDS_LIVE_REFRESH", "NOT_IN_PACK"], router["local_model_route"]["fallback_status"])

        sop_pack = system_map.NOTEBOOK_SOP_PATH.read_text(encoding="utf-8")
        self.assertIn("Authoritative A2-A8 workflow route cards", sop_pack)
        self.assertIn("skills/a8-video-pipeline-skills.md", sop_pack)
        self.assertIn("skills/a8-produce-to-publish-sop.md", sop_pack)
        self.assertIn("skills/maplab-hiphop-songwriter/SKILL.md", sop_pack)
        self.assertIn("Owner lyrics approval before paid/external generation", sop_pack)
        self.assertIn("licensed audio track", sop_pack)


if __name__ == "__main__":
    unittest.main()
