import copy
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_line_schedule_gate_contract.py"
SPEC = importlib.util.spec_from_file_location("hermes_line_schedule_gate_contract_tested", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def valid_payload():
    return {
        "Label": MODULE.LABEL,
        "ProgramArguments": list(MODULE.EXPECTED_ARGUMENTS),
        "WorkingDirectory": str(MODULE.ROOT),
        "EnvironmentVariables": dict(MODULE.EXPECTED_ENVIRONMENT),
        "Umask": 0o77,
        "StartCalendarInterval": {"Hour": 2, "Minute": 20},
        "StandardOutPath": str(MODULE.ROOT / "state" / "hermes_line_training_stdout.log"),
        "StandardErrorPath": str(MODULE.ROOT / "state" / "hermes_line_training_stderr.log"),
    }


class HermesLineScheduleGateContractTests(unittest.TestCase):
    def test_current_tracked_plists_are_identical_and_supervisor_only(self):
        report = MODULE.validate_contract(include_installed=False)
        self.assertEqual(report["validated_plist_route"], "supervisor-only")
        self.assertFalse(report["validated_plists_contain_raw_loop"])
        self.assertFalse(report["installed_plist_verified"])
        self.assertFalse(report["live_launchd_verified"])
        self.assertEqual(len(set(report["plist_sha256"].values())), 1)

    def test_direct_raw_loop_route_is_rejected(self):
        payload = valid_payload()
        payload["ProgramArguments"][1] = str(MODULE.RAW_LOOP)
        with self.assertRaisesRegex(MODULE.ScheduleGateError, "plist_arguments_invalid"):
            MODULE.validate_payload(payload)

    def test_missing_or_duplicate_job_binding_is_rejected(self):
        missing = valid_payload()
        missing["ProgramArguments"] = missing["ProgramArguments"][:2]
        duplicate = valid_payload()
        duplicate["ProgramArguments"].extend(["--job-path", str(MODULE.JOB_PATH)])
        for payload in (missing, duplicate):
            with self.subTest(arguments=payload["ProgramArguments"]):
                with self.assertRaises(MODULE.ScheduleGateError):
                    MODULE.validate_payload(payload)

    def test_cloud_provider_or_permissive_umask_is_rejected(self):
        cloud = valid_payload()
        cloud["EnvironmentVariables"]["HERMES_LINE_PROVIDER"] = "openrouter"
        permissive = valid_payload()
        permissive["Umask"] = 0o22
        for payload in (cloud, permissive):
            with self.subTest(payload=payload):
                with self.assertRaises(MODULE.ScheduleGateError):
                    MODULE.validate_payload(payload)

    def test_unbounded_or_changed_runtime_budget_is_rejected(self):
        for index, value in ((7, "2"), (9, "840")):
            payload = valid_payload()
            payload["ProgramArguments"][index] = value
            with self.subTest(index=index, value=value):
                with self.assertRaisesRegex(MODULE.ScheduleGateError, "plist_arguments_invalid"):
                    MODULE.validate_payload(payload)

    def test_qualification_overrides_are_not_present(self):
        arguments = valid_payload()["ProgramArguments"]
        for flag in (
            "--batch",
            "--stage",
            "--seed-base",
            "--target-streak",
            "--target-pass-rate",
            "--regression-threshold",
        ):
            self.assertNotIn(flag, arguments)

    def test_schedule_and_exact_topology_are_frozen(self):
        wrong_time = valid_payload()
        wrong_time["StartCalendarInterval"] = {"Hour": 3, "Minute": 20}
        extra_key = copy.deepcopy(valid_payload())
        extra_key["RunAtLoad"] = True
        for payload in (wrong_time, extra_key):
            with self.subTest(payload=payload):
                with self.assertRaises(MODULE.ScheduleGateError):
                    MODULE.validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
