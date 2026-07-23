import unittest

from tools.ai_workbook.build_extension_task_modules import ROLES


class DynamicRoleModuleTests(unittest.TestCase):
    def test_b5_is_part_of_the_generated_role_catalog(self):
        role_ids = [role.role_id for role in ROLES]

        self.assertEqual(len(role_ids), len(set(role_ids)))
        self.assertIn("B5", role_ids)
        self.assertEqual(len(role_ids), 32)

        b5 = next(role for role in ROLES if role.role_id == "B5")
        module = b5.to_module()
        self.assertEqual(module["role_id"], "B5")
        self.assertIn("recalls/B5_recall.md", [row["path"] for row in module["read_first"]])
        self.assertIn("packages/local-model-teaching", module["affects"])


if __name__ == "__main__":
    unittest.main()
