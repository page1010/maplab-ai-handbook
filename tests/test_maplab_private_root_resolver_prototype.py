import copy
import errno
import importlib.util
import json
import os
import stat
import sys
import tempfile
import threading
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_private_root_resolver_prototype.py"
SPEC = importlib.util.spec_from_file_location("maplab_private_root_resolver_prototype", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class LabCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="maplab-resolver-test-")
        self.sandbox = Path(self.temp.name)
        self.lab = MODULE.SyntheticPrivateRootLab(self.sandbox, ROOT)

    def tearDown(self):
        self.lab.close()
        self.temp.cleanup()

    def seed(self, name="seed", files=None):
        files = files or {"payload.bin": b"synthetic bytes"}
        self.lab.create_input(name, files)
        return files

    def publish_first(self, surface="case_store", name="seed", files=None):
        files = self.seed(name, files)
        result = self.lab.publish(surface, "g1", name, files, None)
        return files, result

    def assert_code(self, code, action):
        with self.assertRaises(MODULE.PrototypeError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)


class TopologyAndPathTests(LabCase):
    def test_exact_distinct_nonoverlapping_surface_roots(self):
        contract = self.lab.root_contract()
        self.assertEqual(tuple(contract["surfaces"]), MODULE.SURFACES)
        self.assertEqual(contract["surface_count"], 8)
        roots = [(self.sandbox / "private" / surface).resolve() for surface in MODULE.SURFACES]
        self.assertEqual(len(set(roots)), 8)
        for left in roots:
            for right in roots:
                if left != right:
                    self.assertNotIn(left, right.parents)

    def test_sandbox_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="maplab-resolver-real-") as real:
            link = self.sandbox / "link"
            link.symlink_to(real)
            self.assert_code(
                "SANDBOX_UNSAFE",
                lambda: MODULE.SyntheticPrivateRootLab(link, ROOT),
            )

    def test_repository_root_cannot_contain_synthetic_targets(self):
        self.assert_code(
            "SANDBOX_INSIDE_REPOSITORY",
            lambda: MODULE.SyntheticPrivateRootLab(
                self.sandbox, self.sandbox / "private"
            ),
        )

    def test_logical_path_poisons_reject(self):
        self.publish_first()
        for poison in ("", ".", "..", "../x", "a/../x", "/x", "a//b", "a\\b", "x\x00y"):
            with self.subTest(poison=repr(poison)):
                self.assert_code("INVALID_LOGICAL_PATH", lambda poison=poison: self.lab.read("case_store", poison))
        self.assert_code("UNKNOWN_SURFACE", lambda: self.lab.read("unknown", "x"))

    def test_ancestor_and_leaf_symlinks_reject(self):
        self.seed("base")
        inputs = self.sandbox / "inputs"
        (inputs / "ancestor").mkdir(mode=0o700)
        (inputs / "ancestor" / "link").symlink_to(inputs / "base")
        self.assert_code(
            "ANCESTOR_SYMLINK_OR_NON_DIRECTORY",
            lambda: self.lab.publish("case_store", "g1", "ancestor", ["link/payload.bin"], None),
        )
        (inputs / "leaf").mkdir(mode=0o700)
        (inputs / "leaf" / "payload.bin").symlink_to(inputs / "base" / "payload.bin")
        self.assert_code(
            "SOURCE_NOT_REGULAR",
            lambda: self.lab.publish("case_store", "g2", "leaf", ["payload.bin"], None),
        )


class CopyLedgerTests(LabCase):
    def test_actual_bytes_are_reopened_and_ledgered(self):
        files, result = self.publish_first(files={"nested/a.bin": b"abc", "nested/b.bin": b"defgh"})
        self.assertEqual(result["actual_bytes"], 8)
        ledger_path = self.sandbox / "private" / "case_store" / "generations" / "g1" / "_ledger.json"
        ledger = json.loads(ledger_path.read_text())
        self.assertEqual(ledger["source"], "bytes_observed_during_copy")
        self.assertEqual(ledger["physical_paths_persisted"], 0)
        self.assertNotIn(str(self.sandbox), ledger_path.read_text())
        for row in ledger["entries"]:
            self.assertEqual(row["stream_sha256"], row["destination_sha256"])
            self.assertTrue(row["destination_matches_stream"])
            self.assertEqual(row["target_mode"], "0600")
            target = self.sandbox / "private" / "case_store" / "generations" / "g1" / row["logical_path"]
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            self.assertEqual(self.lab.read("case_store", row["logical_path"]), files[row["logical_path"]])

    def test_mutated_destination_fails_ledger_readback(self):
        self.publish_first()
        target = self.sandbox / "private" / "case_store" / "generations" / "g1" / "payload.bin"
        target.write_bytes(b"attacker")
        self.assert_code("GENERATION_ARTIFACT_MISMATCH", lambda: self.lab.read("case_store", "payload.bin"))

    def test_target_hardlink_is_rejected_on_read(self):
        self.publish_first()
        target = self.sandbox / "private" / "case_store" / "generations" / "g1" / "payload.bin"
        os.link(target, target.with_name("alias.bin"))
        self.assert_code("GENERATION_ARTIFACT_MISMATCH", lambda: self.lab.read("case_store", "payload.bin"))

    def test_hardlink_and_fifo_reject_without_blocking(self):
        self.seed("hard")
        original = self.sandbox / "inputs" / "hard" / "payload.bin"
        os.link(original, original.with_name("alias.bin"))
        self.assert_code(
            "SOURCE_HARDLINK",
            lambda: self.lab.publish("case_store", "g1", "hard", ["payload.bin"], None),
        )
        fifo_root = self.sandbox / "inputs" / "fifo"
        fifo_root.mkdir(mode=0o700)
        os.mkfifo(fifo_root / "pipe", 0o600)
        self.assert_code(
            "SOURCE_NOT_REGULAR",
            lambda: self.lab.publish("case_store", "g2", "fifo", ["pipe"], None),
        )

    def test_duplicate_artifact_job_and_generation_fail_closed(self):
        self.seed()
        self.assert_code(
            "DUPLICATE_ARTIFACT",
            lambda: self.lab.publish("case_store", "g1", "seed", ["payload.bin", "payload.bin"], None),
        )
        self.lab.claim_job("adapter_review", "JOB-ONE")
        self.assert_code("DUPLICATE_JOB", lambda: self.lab.claim_job("adapter_review", "JOB-ONE"))
        self.lab.publish("case_store", "g1", "seed", ["payload.bin"], None)
        self.assert_code(
            "GENERATION_EXISTS",
            lambda: self.lab.publish("case_store", "g1", "seed", ["payload.bin"], "g1", expected_epoch=1),
        )

    def test_generation_create_race_never_replaces_existing_directory(self):
        self.publish_first()
        self.seed("next", {"next.bin": b"next"})
        original = MODULE.os.mkdir
        injected = [False]
        def attacker_wins(name, mode=0o777, *, dir_fd=None):
            if name == "g2" and not injected[0]:
                injected[0] = True
                original(name, mode, dir_fd=dir_fd)
            return original(name, mode, dir_fd=dir_fd)
        MODULE.os.mkdir = attacker_wins
        try:
            self.assert_code(
                "GENERATION_EXISTS",
                lambda: self.lab.publish(
                    "case_store", "g2", "next", ["next.bin"], "g1",
                    expected_epoch=1,
                ),
            )
        finally:
            MODULE.os.mkdir = original
        attacker_dir = self.sandbox / "private" / "case_store" / "generations" / "g2"
        self.assertTrue(attacker_dir.is_dir())
        self.assertEqual(list(attacker_dir.iterdir()), [])
        self.assertEqual(self.lab.active_state("case_store")["generation"], "g1")

    def test_53_non_adapter_artifacts_are_actual_byte_covered(self):
        files = {f"classified/item-{index:02d}.json": f"value-{index}".encode() for index in range(53)}
        self.seed("classified", files)
        result = self.lab.publish("shared_review_non_adapter", "g1", "classified", files, None)
        self.assertEqual(result["entry_count"], 53)
        self.assertEqual(result["actual_bytes"], sum(map(len, files.values())))


class CrashExdevAndDurabilityTests(LabCase):
    def test_interrupted_copy_preserves_active_and_cleans_stage(self):
        self.publish_first()
        self.seed("large", {"large.bin": b"z" * 131072})
        before = self.lab.active_state("case_store")
        self.assert_code(
            "SIMULATED_COPY_INTERRUPT",
            lambda: self.lab.publish(
                "case_store", "g2", "large", ["large.bin"], "g1",
                expected_epoch=1, interrupt_after=1000,
            ),
        )
        self.assertEqual(self.lab.active_state("case_store"), before)
        generations = self.sandbox / "private" / "case_store" / "generations"
        self.assertFalse(list(generations.glob(".staging-*")))
        self.assertFalse((generations / "g2").exists())

    def test_injected_exdev_copies_seals_and_publishes(self):
        self.publish_first()
        self.seed("next", {"next.bin": b"cross-device"})
        result = self.lab.publish(
            "case_store", "g2", "next", ["next.bin"], "g1",
            expected_epoch=1, force_exdev=True,
        )
        self.assertEqual(result["actual_bytes"], len(b"cross-device"))
        self.assertEqual(self.lab.read("case_store", "next.bin"), b"cross-device")
        self.assertTrue((self.sandbox / "private" / "case_store" / "generations" / "g2" / "_SEALED.json").is_file())
        self.assertEqual(sum(row["kind"] == "exdev_copy_publish" for row in self.lab.events), 1)

    def test_real_fsync_order_precedes_pointer_publish(self):
        self.publish_first()
        kinds = [(row["kind"], row.get("artifact")) for row in self.lab.events]
        copied = kinds.index(("fsync_file", "copied_artifact"))
        ledger = kinds.index(("fsync_file", "actual_byte_ledger"))
        seal = kinds.index(("fsync_file", "sealed_marker"))
        generation_parent = kinds.index(("fsync_directory", "generations_root"))
        active = kinds.index(("fsync_file", "active_pointer"))
        pointer_parent = kinds.index(("fsync_directory", "surface_root"))
        self.assertLess(copied, ledger)
        self.assertLess(ledger, seal)
        self.assertLess(seal, generation_parent)
        self.assertLess(generation_parent, active)
        self.assertLess(active, pointer_parent)

    def test_fsync_failure_preserves_old_active_generation(self):
        self.publish_first()
        self.seed("next", {"next.bin": b"next"})
        original = MODULE._fsync_dir
        calls = [0]
        def fail_once(fd):
            calls[0] += 1
            if calls[0] == 6:
                raise OSError(errno.EIO, "injected fsync failure")
            return original(fd)
        MODULE._fsync_dir = fail_once
        try:
            with self.assertRaises(OSError):
                self.lab.publish(
                    "case_store", "g2", "next", ["next.bin"], "g1",
                    expected_epoch=1,
                )
        finally:
            MODULE._fsync_dir = original
        self.assertEqual(self.lab.active_state("case_store")["generation"], "g1")
        self.assertFalse((self.sandbox / "private" / "case_store" / "generations" / "g2").exists())

    def test_post_pointer_fsync_failure_preserves_new_sealed_generation(self):
        self.publish_first()
        self.seed("next", {"next.bin": b"next"})
        original = MODULE._fsync_dir
        raised = [False]
        active_path = self.sandbox / "private" / "case_store" / "active.json"
        def fail_after_replace(fd):
            if not raised[0] and active_path.exists():
                try:
                    active = json.loads(active_path.read_text())
                except (OSError, json.JSONDecodeError):
                    active = {}
                if active.get("generation") == "g2":
                    raised[0] = True
                    raise OSError(errno.EIO, "injected post-pointer fsync failure")
            return original(fd)
        MODULE._fsync_dir = fail_after_replace
        try:
            with self.assertRaises(OSError):
                self.lab.publish(
                    "case_store", "g2", "next", ["next.bin"], "g1",
                    expected_epoch=1,
                )
        finally:
            MODULE._fsync_dir = original
        self.assertTrue(raised[0])
        self.assertEqual(self.lab.active_state("case_store")["generation"], "g2")
        self.assertEqual(self.lab.read("case_store", "next.bin"), b"next")

    def test_unsealed_generation_cannot_be_read_or_rollback_target(self):
        self.publish_first()
        seal = self.sandbox / "private" / "case_store" / "generations" / "g1" / "_SEALED.json"
        seal.unlink()
        self.assert_code("GENERATION_UNSEALED", lambda: self.lab.read("case_store", "payload.bin"))
        self.seed("next", {"next.bin": b"next"})
        # Restore a clean lab for rollback-target validation.
        seal.write_text('{}\n')
        self.assert_code(
            "GENERATION_UNSEALED",
            lambda: self.lab.rollback("case_store", "g1", "g1", expected_epoch=1),
        )


class CasConcurrencyRollbackTests(LabCase):
    def test_generation_and_epoch_cas_are_required(self):
        self.publish_first()
        self.seed("next", {"x": b"x"})
        self.assert_code(
            "EXPECTED_EPOCH_REQUIRED",
            lambda: self.lab.publish("case_store", "g2", "next", ["x"], "g1"),
        )
        self.assert_code(
            "GENERATION_CAS_MISMATCH",
            lambda: self.lab.publish("case_store", "g2", "next", ["x"], "g1", expected_epoch=2),
        )
        self.assertEqual(self.lab.active_state("case_store")["generation"], "g1")

    def test_concurrent_first_writers_have_one_winner(self):
        self.seed("a", {"x": b"a"})
        self.seed("b", {"x": b"b"})
        barrier = threading.Barrier(2)
        outcomes = []
        guard = threading.Lock()
        def writer(generation, source):
            barrier.wait()
            try:
                self.lab.publish("dispatch", generation, source, ["x"], None)
                result = "WIN"
            except MODULE.PrototypeError as exc:
                result = exc.code
            with guard:
                outcomes.append(result)
        threads = [threading.Thread(target=writer, args=("ga", "a")), threading.Thread(target=writer, args=("gb", "b"))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
        self.assertEqual(outcomes.count("WIN"), 1)
        self.assertEqual(len(outcomes), 2)

    def test_prewrite_rollback_and_durable_postwrite_barrier(self):
        self.publish_first()
        self.seed("next", {"x": b"x"})
        self.lab.publish("case_store", "g2", "next", ["x"], "g1", expected_epoch=1)
        rolled = self.lab.rollback("case_store", "g2", "g1", expected_epoch=2)
        self.assertEqual(rolled["action"], "ROLLED_BACK_PREWRITE")
        self.lab.publish("case_store", "g3", "next", ["x"], "g1", expected_epoch=3)
        barrier = self.lab.begin_authoritative_write("case_store", "g3", expected_epoch=4)
        self.assertTrue(barrier["write_started"])
        self.lab.close()
        self.lab = MODULE.SyntheticPrivateRootLab(self.sandbox, ROOT)
        forward = self.lab.rollback("case_store", "g3", "g1", expected_epoch=5)
        self.assertEqual(forward["action"], "FORWARD_REPAIR")
        self.assertEqual(self.lab.active_state("case_store")["generation"], "g3")
        self.assertFalse(forward["repo_fallback"])

    def test_rollback_rehashes_every_prior_artifact_before_activation(self):
        self.publish_first()
        self.seed("next", {"x": b"x"})
        self.lab.publish("case_store", "g2", "next", ["x"], "g1", expected_epoch=1)
        prior = self.sandbox / "private" / "case_store" / "generations" / "g1" / "payload.bin"
        prior.write_bytes(b"tampered")
        self.assert_code(
            "GENERATION_ARTIFACT_MISMATCH",
            lambda: self.lab.rollback(
                "case_store", "g2", "g1", expected_epoch=2
            ),
        )
        self.assertEqual(self.lab.active_state("case_store")["generation"], "g2")


class NoFallbackAndReceiptTests(LabCase):
    def test_missing_artifact_and_backup_policy_never_use_repo(self):
        self.publish_first()
        self.assert_code(
            "ARTIFACT_NOT_FOUND_NO_FALLBACK",
            lambda: self.lab.read("case_store", "missing.bin"),
        )
        valid = self.lab.validate_backup_index([f"{surface}/g1" for surface in MODULE.SURFACES])
        self.assertEqual(valid["classified_repo_paths"], 0)
        self.assertFalse(valid["repo_fallback"])
        self.assert_code("REPO_BACKUP_FORBIDDEN", lambda: self.lab.validate_backup_index(["case_store/repo/private.db"]))
        self.assert_code("BACKUP_SOURCE_INVALID", lambda: self.lab.validate_backup_index(["unknown/g1"]))
        self.assertEqual(self.lab.fallback_attempts, 0)

    def test_full_runtime_receipt_is_synthetic_hold(self):
        receipt = MODULE.build_receipt(ROOT, "2026-08-27T23:18:00+00:00")
        MODULE.validate_receipt(receipt)
        self.assertEqual(receipt["metrics"]["surface_publish_count"], 8)
        self.assertEqual(receipt["metrics"]["non_adapter_artifact_count"], 53)
        self.assertGreaterEqual(receipt["metrics"]["fixture_passed"], 20)
        self.assertEqual(receipt["metrics"]["fixture_passed"], receipt["metrics"]["fixture_total"])
        self.assertTrue(receipt["decision"]["resolver_copy_ledger_runtime_validated"])
        self.assertFalse(receipt["decision"]["eligible_for_live_change"])
        self.assertFalse(receipt["decision"]["live_migration_performed"])
        self.assertEqual(receipt["decision"]["adoption_status"], "HOLD")

    def test_receipt_type_decision_and_path_poisons_reject(self):
        receipt = MODULE.build_receipt(ROOT, "2026-08-27T23:18:00+00:00")
        poisons = []
        mutated = copy.deepcopy(receipt)
        mutated["metrics"]["repo_fallback_attempts"] = False
        poisons.append((mutated, "RECEIPT_METRICS"))
        mutated = copy.deepcopy(receipt)
        mutated["decision"]["eligible_for_live_change"] = True
        poisons.append((mutated, "RECEIPT_DECISION"))
        mutated = copy.deepcopy(receipt)
        mutated["fixtures"][0]["observed"] = "/var/folders/private"
        body = {key: value for key, value in mutated.items() if key not in {"schema_version", "deterministic_body_sha256"}}
        mutated["deterministic_body_sha256"] = MODULE._sha256(MODULE._canonical_json(body))
        poisons.append((mutated, "RECEIPT_FIXTURES"))
        mutated = copy.deepcopy(receipt)
        mutated["created_at"] = "2099-01-01T00:00:00+00:00"
        body = {key: value for key, value in mutated.items() if key not in {"schema_version", "deterministic_body_sha256"}}
        mutated["deterministic_body_sha256"] = MODULE._sha256(MODULE._canonical_json(body))
        poisons.append((mutated, "RECEIPT_TIMESTAMP"))
        mutated = copy.deepcopy(receipt)
        mutated["fixtures"][3] = {"name": "dummy_pass", "result": "PASS", "observed": "whatever"}
        body = {key: value for key, value in mutated.items() if key not in {"schema_version", "deterministic_body_sha256"}}
        mutated["deterministic_body_sha256"] = MODULE._sha256(MODULE._canonical_json(body))
        poisons.append((mutated, "RECEIPT_FIXTURES"))
        mutated = copy.deepcopy(receipt)
        mutated["metrics"]["unvalidated_private_payload_reads"] = 999
        body = {key: value for key, value in mutated.items() if key not in {"schema_version", "deterministic_body_sha256"}}
        mutated["deterministic_body_sha256"] = MODULE._sha256(MODULE._canonical_json(body))
        poisons.append((mutated, "RECEIPT_METRICS"))
        mutated = copy.deepcopy(receipt)
        mutated["implementation_provenance"][0]["sha256"] = "0" * 64
        body = {key: value for key, value in mutated.items() if key not in {"schema_version", "deterministic_body_sha256"}}
        mutated["deterministic_body_sha256"] = MODULE._sha256(MODULE._canonical_json(body))
        poisons.append((mutated, "RECEIPT_IMPLEMENTATION_PROVENANCE"))
        for poisoned, code in poisons:
            with self.subTest(code=code):
                self.assert_code(code, lambda poisoned=poisoned: MODULE.validate_receipt(poisoned))


if __name__ == "__main__":
    unittest.main()
