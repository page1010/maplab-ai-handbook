"""Offline execution checks for the shell runner's embedded Python program."""

import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import urllib.error


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/free_quota_daily.sh"
PROGRAM = RUNNER.read_text(encoding="utf-8").split("<<'PYEOF'\n", 1)[1].split("\nPYEOF", 1)[0]
PROVIDER_ROOT = ROOT.parent / "investment-os/scripts/free_compute"


class ShellPreflightTests(unittest.TestCase):
    def run_shell(self, *args, extra_env=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = dict(os.environ, MAPLAB_HB=tmp, MAPLAB_ENV=str(root / "missing.env"))
            if extra_env:
                env.update(extra_env)
            result = subprocess.run(["/bin/bash", str(RUNNER), *args], env=env,
                                    text=True, capture_output=True, timeout=10)
            return result, sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))

    def test_invalid_bands_stop_before_reading_env_or_writing(self):
        for band, bands in (("10", "6"), ("-1", "6"), ("0", "6"), ("2", "0"), ("foo", "6")):
            result, paths = self.run_shell(band, bands)
            self.assertEqual(result.returncode, 2)
            self.assertIn("1 <= BAND <= BANDS", result.stderr)
            self.assertNotIn("env file", result.stdout)
            self.assertEqual(paths, [])

    def test_selftest_needs_no_key_provider_or_output_directory(self):
        result, paths = self.run_shell("0", "0", "selftest")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("selftest: 7/7", result.stdout)
        self.assertEqual(paths, [])

    def test_python_failure_does_not_mark_complete_or_invoke_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_file = root / "test.env"
            env_file.write_text("OPENROUTER_API_KEY=offline-fixture\n", encoding="utf-8")
            bindir = root / "bin"
            bindir.mkdir()
            git_marker = root / "git-called"
            fake_git = bindir / "git"
            fake_git.write_text("#!/bin/sh\ntouch '" + str(git_marker) + "'\n", encoding="utf-8")
            fake_git.chmod(0o700)
            env = dict(os.environ, MAPLAB_HB=tmp, MAPLAB_ENV=str(env_file), FQ_MAX_CALLS="0",
                       PATH=str(bindir) + os.pathsep + os.environ.get("PATH", ""))
            result = subprocess.run(["/bin/bash", str(RUNNER), "1", "6"], env=env,
                                    text=True, capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FQ_MAX_CALLS", result.stderr)
            self.assertFalse(list((root / "data/free-quota").glob(".queue_sig*")))
            self.assertFalse(git_marker.exists())


@unittest.skipUnless((PROVIDER_ROOT / "providers.py").is_file(), "canonical shared provider module is not installed")
class RunnerExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("freequota_test_providers", PROVIDER_ROOT / "providers.py")
        cls.providers = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.providers
        spec.loader.exec_module(cls.providers)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fq = self.root / "data/free-quota"
        (self.fq / "queue").mkdir(parents=True)
        (self.fq / "lists").mkdir()
        (self.fq / "lists/items.txt").write_text("scene one\nscene two\nscene three\n", encoding="utf-8")
        self.job = self.fq / "queue/40-image-prompt.job.md"
        self.job.write_text("OUTPUT: data/free-quota/images/prompt.md\nFANOUT: lists/items.txt\n"
                            "FANOUT_N: 3\nDAILY: yes\n\nCreate a SYNTHETIC scene: {{ITEM}}\n", encoding="utf-8")
        self.ledger = self.root / "private/request-ledger.json"
        self.counter = self.providers.DailyCounter(self.ledger, min_interval_seconds=0)
        self.observed_models = []

    def transport(self, request, timeout):
        # A real locked ledger reservation must exist before the transport sees a request.
        state = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(state["calls"][-1]["status"], "reserved")
        payload = json.loads(request.data)
        model = payload["model"]
        self.observed_models.append(model)
        is_review = payload["messages"][0]["content"].startswith("你是嚴格審稿人")
        text = "VERDICT: PASS\nSynthetic fixture checked." if is_review else "SYNTHETIC scene, no people."
        return io.BytesIO(json.dumps({"id": "fixture-response", "model": model,
                                     "choices": [{"message": {"content": text}}]}).encode())

    def execute(self, run_id, transport=None, env_overrides=None, expected_exit=None):
        env = {"OPENROUTER_API_KEY": "offline-fixture", "FQ_PROVIDER_ROOT": str(PROVIDER_ROOT),
               "FQ_JOB": self.job.name, "FQ_MAX_ITEMS": "1", "FQ_MAX_CALLS": "4"}
        env.update(env_overrides or {})
        argv = ["-", str(self.root), "20990101", "2099-W01", "1", "1", "", run_id]
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(sys, "argv", argv), \
                mock.patch.dict(sys.modules, {"providers": self.providers}), \
                mock.patch.object(self.providers, "build_training_counter", return_value=self.counter), \
                mock.patch("urllib.request.urlopen", side_effect=transport or self.transport) as network, \
                mock.patch("sys.stdout", new_callable=io.StringIO):
            if expected_exit is None:
                exec(compile(PROGRAM, str(RUNNER), "exec"), {"__name__": "__main__"})
            else:
                with self.assertRaises(SystemExit) as stopped:
                    exec(compile(PROGRAM, str(RUNNER), "exec"), {"__name__": "__main__"})
                self.assertEqual(stopped.exception.code, expected_exit)
        return json.loads((self.fq / ("report_" + run_id + ".json")).read_text(encoding="utf-8")), network

    def test_one_item_uses_shared_ledger_and_different_reviewer_without_queue_changes(self):
        before = self.job.read_bytes()
        receipt, network = self.execute("20990101-b1of1-test-a")
        self.assertEqual(network.call_count, 2)
        self.assertEqual(receipt["provider_requests_this_run"], 2)
        self.assertEqual(receipt["items_attempted"], 1)
        self.assertEqual(receipt["shared_utc_day_used_at_end"], 2)
        self.assertEqual(receipt["shared_utc_day_cap"], 950)
        self.assertEqual(receipt["owner_reserve"], 50)
        self.assertEqual(receipt["execution_status"], "COMPLETE")
        self.assertEqual(receipt["model_review_pass"], 1)
        self.assertEqual(receipt["jobs"][0]["note"],
                         "本班候選 3 件；本次實際成功 1 件；bounded item limit reached")
        self.assertIn("prior_unmetered_usage_unknown", receipt["daily_usage_coverage"])
        self.assertNotEqual(*self.observed_models)
        self.assertEqual(self.job.read_bytes(), before)
        self.assertFalse(list(self.fq.glob("weekly_review*")))
        self.assertEqual(self.ledger.stat().st_mode & 0o777, 0o600)

    def test_repeated_band_preserves_both_outputs_reviews_and_reports(self):
        self.execute("20990101-b1of1-test-a")
        first_files = {p: p.read_bytes() for p in self.fq.rglob("*") if p.is_file() and "test-a" in str(p)}
        second, _ = self.execute("20990101-b1of1-test-b")
        self.assertTrue(first_files)
        self.assertTrue(all(p.read_bytes() == content for p, content in first_files.items()))
        self.assertEqual(len(list((self.fq / "images").glob("*/*.md"))), 2)
        self.assertEqual(len(list((self.fq / "reviews").glob("*.review.md"))), 2)
        self.assertEqual(len(list(self.fq.glob("report_*.json"))), 2)
        self.assertEqual(second["shared_utc_day_used_at_end"], 4)

    def test_http_failure_and_fallback_each_consume_a_reserved_attempt(self):
        real_fixture = self.transport
        seen = [0]

        def flaky(request, timeout):
            seen[0] += 1
            if seen[0] == 1:
                state = json.loads(self.ledger.read_text(encoding="utf-8"))
                self.assertEqual(state["calls"][-1]["status"], "reserved")
                raise urllib.error.HTTPError(request.full_url, 429, "fixture rate limit", {}, None)
            return real_fixture(request, timeout)

        receipt, _ = self.execute("20990101-b1of1-fallback", transport=flaky)
        self.assertEqual(receipt["provider_requests_this_run"], 3)
        self.assertEqual([a["status"] for a in receipt["attempts"]], ["http_error", "ok", "ok"])
        self.assertEqual(self.counter.count, 3)

    def test_exhausted_daily_ledger_blocks_transport(self):
        self.counter = self.providers.DailyCounter(self.ledger, daily_cap=1, min_interval_seconds=0)
        self.counter.record("another-run", "fixture/model:free", "ok")
        receipt, network = self.execute("20990101-b1of1-exhausted", expected_exit=3)
        self.assertEqual(network.call_count, 0)
        self.assertEqual(receipt["provider_requests_this_run"], 0)
        self.assertTrue(receipt["budget_blocked"])
        self.assertEqual(receipt["execution_status"], "INCOMPLETE")
        self.assertEqual(self.counter.count, 1)

    def test_ambiguous_review_cannot_be_counted_as_pass(self):
        def ambiguous(request, timeout):
            response = self.transport(request, timeout)
            payload = json.loads(request.data)
            if payload["messages"][0]["content"].startswith("你是嚴格審稿人"):
                response.close()
                return io.BytesIO(json.dumps({"choices": [{"message": {"content": "NOT PASS"}}]}).encode())
            return response

        receipt, _ = self.execute("20990101-b1of1-badreview", transport=ambiguous, expected_exit=3)
        self.assertEqual(receipt["model_review_pass"], 0)
        self.assertEqual(receipt["execution_status"], "INCOMPLETE")

    def test_full_shell_completion_marks_signature_and_never_calls_git(self):
        # A subprocess fixture replaces transport and injects a temporary ledger.
        # Neither production secrets nor the real shared ledger are accessed.
        fixture_modules = self.root / "fixture_modules"
        fixture_modules.mkdir()
        provider_wrapper = ("from pathlib import Path\n"
                            "exec(compile(Path(%r).read_text(), %r, 'exec'))\n"
                            "def build_training_counter():\n"
                            "    return DailyCounter(Path(%r), min_interval_seconds=0)\n"
                            % (str(PROVIDER_ROOT / "providers.py"), str(PROVIDER_ROOT / "providers.py"),
                               str(self.ledger)))
        (fixture_modules / "providers.py").write_text(provider_wrapper, encoding="utf-8")
        (fixture_modules / "sitecustomize.py").write_text(
            "import io, json, urllib.request\n"
            "def offline(request, timeout):\n"
            "    prompt = json.loads(request.data)['messages'][0]['content']\n"
            "    text = 'VERDICT: PASS' if prompt.startswith('你是嚴格審稿人') else 'SYNTHETIC scene'\n"
            "    return io.BytesIO(json.dumps({'choices':[{'message':{'content':text}}]}).encode())\n"
            "urllib.request.urlopen = offline\n", encoding="utf-8")
        env_file = self.root / "test.env"
        env_file.write_text("OPENROUTER_API_KEY=offline-fixture\n", encoding="utf-8")
        git_marker = self.root / "git-called"
        fake_git = fixture_modules / "git"
        fake_git.write_text("#!/bin/sh\ntouch '" + str(git_marker) + "'\n", encoding="utf-8")
        fake_git.chmod(0o700)
        env = dict(os.environ, MAPLAB_HB=str(self.root), MAPLAB_ENV=str(env_file),
                   FQ_PROVIDER_ROOT=str(fixture_modules), PYTHONPATH=str(fixture_modules),
                   FQ_JOB=self.job.name, FQ_MAX_ITEMS="1", FQ_MAX_CALLS="4",
                   PATH=str(fixture_modules) + os.pathsep + os.environ.get("PATH", ""))
        result = subprocess.run(["/bin/bash", str(RUNNER), "1", "6"], env=env,
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(self.fq.glob(".queue_sig_v3_*"))), 1)
        self.assertEqual(len(list(self.fq.glob("report_*.json"))), 1)
        self.assertFalse(git_marker.exists())


if __name__ == "__main__":
    unittest.main()
