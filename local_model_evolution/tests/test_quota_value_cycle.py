from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "bin" / "quota_value_cycle.py"
)
SPEC = importlib.util.spec_from_file_location("quota_value_cycle", MODULE_PATH)
assert SPEC and SPEC.loader
qvc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qvc)


def write_event(
    path: Path,
    timestamp: datetime,
    used: float,
    reset_at: int,
    limit_id: str = "codex",
) -> None:
    event = {
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {"total_token_usage": {"total_tokens": 1}},
            "rate_limits": {
                "limit_id": limit_id,
                "primary": {
                    "used_percent": used,
                    "window_minutes": 10080,
                    "resets_at": reset_at,
                },
            },
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


class QuotaValueCycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sessions = self.root / "sessions"
        self.state = self.root / "state"
        self.evidence = self.root / "evidence.md"
        self.evidence.write_text("verified\n", encoding="utf-8")
        self.config = self.root / "config.json"
        self.config.write_text(
            json.dumps(
                {
                    "safe_reserve_percent": 15,
                    "activation_window_hours": 36,
                    "cooldown_hours": 168,
                    "candidates": [
                        {
                            "id": "low",
                            "revision": "v1",
                            "project": "maplab",
                            "title": "low",
                            "owner_value": 3,
                            "step_change": 3,
                            "readiness": 5,
                            "risk": 1,
                            "evidence": [str(self.evidence)],
                            "acceptance": ["receipt"],
                            "external_mutation": False,
                            "owner_decision_required": False,
                        },
                        {
                            "id": "high",
                            "revision": "v1",
                            "project": "maplab",
                            "title": "high",
                            "owner_value": 5,
                            "step_change": 5,
                            "readiness": 5,
                            "risk": 1,
                            "evidence": [str(self.evidence)],
                            "acceptance": ["receipt"],
                            "external_mutation": False,
                            "owner_decision_required": False,
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_snapshot(
        self, now: datetime, used: float, reset_delta: timedelta
    ) -> None:
        write_event(
            self.sessions / "2026" / "run.jsonl",
            now,
            used,
            int((now + reset_delta).timestamp()),
        )

    def test_latest_codex_snapshot_wins_and_other_lane_is_ignored(self) -> None:
        now = datetime.now(timezone.utc)
        path = self.sessions / "2026" / "run.jsonl"
        write_event(path, now - timedelta(minutes=2), 5, int((now + timedelta(days=1)).timestamp()))
        write_event(
            path,
            now - timedelta(minutes=1),
            99,
            int((now + timedelta(days=1)).timestamp()),
            limit_id="codex_bengalfox",
        )
        write_event(path, now, 6, int((now + timedelta(days=1)).timestamp()))
        result = qvc.take_snapshot(self.sessions, self.state, "codex")
        self.assertEqual(result["used_percent"], 6)
        self.assertEqual(result["remaining_percent"], 94)

    def test_cli_accepts_tainan_game_project(self) -> None:
        parser = qvc.build_parser()
        args = parser.parse_args(["plan", "--project", "tainan-game"])
        self.assertEqual(args.project, "tainan-game")

    def test_plan_selects_highest_user_value_job(self) -> None:
        now = datetime.now(timezone.utc)
        self.add_snapshot(now, 20, timedelta(hours=20))
        plan = qvc.make_plan(
            self.config, self.sessions, self.state, "maplab", "codex", now=now
        )
        self.assertEqual(plan["gate"], "ready")
        self.assertEqual(plan["selected_job"]["id"], "high")
        self.assertTrue(Path(plan["job_card_path"]).exists())

    def test_safe_reserve_stops_work(self) -> None:
        now = datetime.now(timezone.utc)
        self.add_snapshot(now, 86, timedelta(hours=20))
        plan = qvc.make_plan(
            self.config, self.sessions, self.state, "maplab", "codex", now=now
        )
        self.assertEqual(plan["gate"], "blocked")
        self.assertEqual(plan["reason"], "safe_reserve_held")

    def test_outside_window_stops_work(self) -> None:
        now = datetime.now(timezone.utc)
        self.add_snapshot(now, 10, timedelta(hours=40))
        plan = qvc.make_plan(
            self.config, self.sessions, self.state, "maplab", "codex", now=now
        )
        self.assertEqual(plan["reason"], "outside_activation_window")

    def test_completed_revision_is_not_selected_again(self) -> None:
        now = datetime.now(timezone.utc)
        self.add_snapshot(now, 10, timedelta(hours=20))
        qvc.append_jsonl(
            self.state / "job_ledger.jsonl",
            {
                "recorded_at": qvc.iso_time(now - timedelta(hours=1)),
                "job_id": "high",
                "revision": "v1",
                "status": "done",
            },
        )
        plan = qvc.make_plan(
            self.config, self.sessions, self.state, "maplab", "codex", now=now
        )
        self.assertEqual(plan["selected_job"]["id"], "low")

    def test_done_record_requires_output(self) -> None:
        now = datetime.now(timezone.utc)
        self.add_snapshot(now, 10, timedelta(hours=20))
        plan = qvc.make_plan(
            self.config, self.sessions, self.state, "maplab", "codex", now=now
        )
        args = type(
            "Args",
            (),
            {
                "state_dir": str(self.state),
                "plan": plan["plan_path"],
                "status": "done",
                "summary": "done",
                "output": [],
                "test": ["pass"],
                "commit_sha": "abc123",
            },
        )
        with self.assertRaises(ValueError):
            qvc.record_job(args)

    def test_record_and_report_close_the_cycle(self) -> None:
        now = datetime.now(timezone.utc)
        self.add_snapshot(now, 10, timedelta(hours=20))
        plan = qvc.make_plan(
            self.config, self.sessions, self.state, "maplab", "codex", now=now
        )
        output = self.root / "validation.md"
        output.write_text("pass\n", encoding="utf-8")
        args = type(
            "Args",
            (),
            {
                "state_dir": str(self.state),
                "plan": plan["plan_path"],
                "status": "done",
                "summary": "owner-visible slice completed",
                "output": [str(output)],
                "test": ["7 passed"],
                "commit_sha": "abc123",
            },
        )
        receipt = qvc.record_job(args)
        report, report_path = qvc.build_report(self.state, "current")
        self.assertTrue(Path(receipt["receipt_path"]).exists())
        ledger = qvc.read_jsonl(self.state / "job_ledger.jsonl")
        self.assertEqual(ledger[-1]["receipt_path"], receipt["receipt_path"])
        self.assertEqual(report["counts"]["done"], 1)
        self.assertIn(str(output.resolve()), report_path.read_text(encoding="utf-8"))
        self.assertIn(receipt["receipt_path"], report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
