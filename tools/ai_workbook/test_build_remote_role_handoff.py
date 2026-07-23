#!/usr/bin/env python3
"""Regression tests for Remote Role Launcher routing and relation coverage."""

from __future__ import annotations

import unittest

from build_remote_role_handoff import (
    auto_route,
    existing_source_state,
    load_module_index,
    load_relation_rows,
)


class RemoteRoleHandoffSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _, entries = load_module_index()
        cls.available_roles = set(entries)

    def assert_route(self, task: str, expected_role: str) -> None:
        role, _ = auto_route(task, self.available_roles)
        self.assertEqual(expected_role, role)

    def test_a_quote_routes_to_a5_with_shared_sheet_relations(self) -> None:
        self.assert_route("A6 報價後沒有寫入 REVISION_LOG，找根因並驗證", "A5")
        rows = {row["source_id"]: row for row in load_relation_rows("A5")}
        shared_sheet = rows["DRIVE-MAPLAB-SHEET"]
        self.assertIn("A6", shared_sheet["used_by_roles"])
        self.assertIn("A7", shared_sheet["used_by_roles"])

    def test_b_seo_routes_to_a2_with_a4_case_assets(self) -> None:
        self.assert_route("從 Drive 找企業開幕案例素材，規劃 SEO 與社群使用", "A2")
        rows = {row["source_id"]: row for row in load_relation_rows("A2")}
        self.assertIn("A4", rows["DRIVE-CASE-ASSETS"]["used_by_roles"])

    def test_c_investment_freshness_routes_to_b2_with_decision_loop(self) -> None:
        self.assert_route("審查 IOS-LEFT 與 IOS-RIGHT 是否停更及下游影響", "B2")
        rows = {row["source_id"]: row for row in load_relation_rows("B2")}
        self.assertIn("Investment Decision Loop", rows["GOV-INVEST-STATE"]["related_loops"])

    def test_d_global_index_routes_to_a1_with_governance_sources(self) -> None:
        self.assert_route("建立冷啟動全局索引並接入 Extension 與 Remote Codex", "A1")
        source_ids = {row["source_id"] for row in load_relation_rows("A1")}
        self.assertTrue(
            {"GOV-DIRECTORY", "GOV-RELATION", "GOV-STARTUP", "ROLE-MODULE-INDEX"}
            <= source_ids
        )

    def test_launcher_validation_stays_with_a1(self) -> None:
        self.assert_route(
            "驗證 Remote Codex Role Launcher 的四個角色 smoke tests，"
            "檢查 Draft PR #20 實作與 branch freshness，產出 validation report；"
            "不修改 production runtime、不讀 secrets、不合併 main。",
            "A1",
        )

    def test_source_hash_drift_is_visible(self) -> None:
        self.assertEqual("ok", existing_source_state("SYSTEM_DIRECTORY_INDEX.md"))
        self.assertEqual(
            "stale_hash",
            existing_source_state("SYSTEM_DIRECTORY_INDEX.md", "0" * 64),
        )


if __name__ == "__main__":
    unittest.main()
