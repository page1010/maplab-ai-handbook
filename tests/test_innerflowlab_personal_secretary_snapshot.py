import tempfile
import unittest
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from tools.innerflowlab_personal_secretary_snapshot import (
    LaunchJob,
    build_snapshot,
    file_freshness,
    parse_launchctl,
)


class SecretarySnapshotTests(unittest.TestCase):
    def test_parse_launchctl_distinguishes_running_and_standby(self):
        jobs = parse_launchctl(
            "12838\t-15\tcom.investmentos.telegram-operator\n"
            "-\t0\tcom.investmentos.black-swan-scanner\n"
            "-\t2\tcom.investmentos.live-position-gpt-watchdog\n"
        )

        self.assertEqual(jobs["com.investmentos.telegram-operator"], LaunchJob(12838, -15))
        self.assertEqual(jobs["com.investmentos.telegram-operator"].status, "running")
        self.assertEqual(jobs["com.investmentos.black-swan-scanner"].status, "standby")
        self.assertEqual(jobs["com.investmentos.live-position-gpt-watchdog"].status, "warning")

    def test_file_freshness_reports_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            now = datetime(2026, 7, 23, tzinfo=timezone.utc)
            self.assertEqual(file_freshness(Path(tmp) / "missing.json", now), "missing")

    def test_build_snapshot_never_reads_or_emits_secret_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            maplab = root / "maplab"
            ios = root / "ios"
            (maplab / "chrome-extension" / "task-modules").mkdir(parents=True)
            (maplab / "recalls").mkdir()
            ios.mkdir()
            (maplab / ".env").write_text("TOP_SECRET=do-not-emit\n")
            (ios / ".env").write_text("BROKER_SECRET=do-not-emit\n")
            (maplab / "CURRENT_STATUS.md").write_text("clean\n")
            (ios / "CURRENT_STATUS.md").write_text("status\n")
            (ios / "SYSTEM_MAP.md").write_text("map\n")

            with mock.patch(
                "tools.innerflowlab_personal_secretary_snapshot.read_launchctl",
                return_value={},
            ):
                snapshot = build_snapshot(
                    maplab,
                    ios,
                    datetime(2026, 7, 23, tzinfo=timezone.utc),
                )
            rendered = str(snapshot)

            self.assertNotIn("TOP_SECRET", rendered)
            self.assertNotIn("BROKER_SECRET", rendered)
            self.assertEqual(set(snapshot), {"generated_at", "roles", "modules", "alerts"})
            self.assertEqual(len(snapshot["roles"]), 31)
            b5 = next(role for role in snapshot["roles"] if role["id"] == "B5")
            self.assertEqual(b5["status"], "warning")
            self.assertIn("不能判定可用", b5["result"])

    def test_build_snapshot_flags_merge_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            maplab = root / "maplab"
            ios = root / "ios"
            maplab.mkdir()
            ios.mkdir()
            (maplab / "CURRENT_STATUS.md").write_text("<<<<<<< Updated upstream\n")

            with mock.patch(
                "tools.innerflowlab_personal_secretary_snapshot.read_launchctl",
                return_value={},
            ):
                snapshot = build_snapshot(
                    maplab,
                    ios,
                    datetime(2026, 7, 23, tzinfo=timezone.utc),
                )

            self.assertTrue(
                any("merge conflict" in alert["title"] for alert in snapshot["alerts"])
            )

    def test_role_source_hash_drift_is_context_warning_not_runtime_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            maplab = root / "maplab"
            ios = root / "ios"
            modules = maplab / "chrome-extension" / "task-modules"
            recalls = maplab / "recalls"
            modules.mkdir(parents=True)
            recalls.mkdir()
            ios.mkdir()
            source = maplab / "CURRENT_STATUS.md"
            source.write_text("new status\n")
            (recalls / "A0_recall.md").write_text("recall\n")
            (modules / "A0.json").write_text(json.dumps({
                "read_first": [{
                    "path": "CURRENT_STATUS.md",
                    "source_sha256": hashlib.sha256(b"old status\n").hexdigest(),
                }]
            }))

            with mock.patch(
                "tools.innerflowlab_personal_secretary_snapshot.read_launchctl",
                return_value={},
            ):
                snapshot = build_snapshot(
                    maplab,
                    ios,
                    datetime(2026, 7, 23, tzinfo=timezone.utc),
                )

            a0 = next(role for role in snapshot["roles"] if role["id"] == "A0")
            self.assertEqual(a0["status"], "standby")
            self.assertIn("stale source hash", a0["evidence"])
            self.assertTrue(
                any(
                    "來源線索已過期" in alert["title"]
                    for alert in snapshot["alerts"]
                )
            )

    def test_ios_alpha_freshness_uses_runtime_root_not_stale_repo_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            maplab = root / "maplab"
            ios = root / "ios"
            runtime = root / "runtime"
            (maplab / "chrome-extension" / "task-modules").mkdir(parents=True)
            (maplab / "recalls").mkdir()
            (ios / "data").mkdir(parents=True)
            (runtime / "data").mkdir(parents=True)
            (ios / "data" / "convergence_phone.md").write_text("stale repo copy\n")
            (runtime / "data" / "convergence_phone.md").write_text("fresh runtime\n")

            with mock.patch(
                "tools.innerflowlab_personal_secretary_snapshot.read_launchctl",
                return_value={
                    "com.investmentos.convergence-engine": LaunchJob(None, 0),
                },
            ):
                snapshot = build_snapshot(
                    maplab,
                    ios,
                    datetime.now(timezone.utc),
                    ios_runtime_root=runtime,
                )

            alpha = next(
                module
                for module in snapshot["modules"]
                if module["id"] == "ios_alpha"
            )
            self.assertEqual(alpha["status"], "ready")
            self.assertEqual(alpha["freshness"], "0h")


if __name__ == "__main__":
    unittest.main()
