#!/usr/bin/env python3
"""Synthetic-only MAPLAB private-root resolver and copy-ledger prototype.

The prototype deliberately refuses paths outside a caller-supplied sandbox.
It copies generated regular files into distinct generation roots, derives its
ledger from the bytes actually copied, publishes through a generation CAS, and
never falls back to the repository.  It is not wired to any live consumer.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCHEMA_VERSION = "maplab.margin.private-root-resolver-prototype-receipt.v1"
METHOD_VERSION = "margin-private-root-resolver-prototype-v1"
EXPECTED_CREATED_AT = "2026-08-27T23:18:00+00:00"
PRIVATE_RECEIPT_ROOT = Path.home() / ".maplab" / "margin-leak-audit"
NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
DIRECTORY = getattr(os, "O_DIRECTORY", 0)
NONBLOCK = getattr(os, "O_NONBLOCK", 0)
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")

SURFACES = (
    "case_store",
    "bot_config",
    "provider_config",
    "hermes_training",
    "adapter_review",
    "shared_review_non_adapter",
    "dispatch",
    "backup_policy",
)
REVIEW_SURFACES = {"adapter_review", "shared_review_non_adapter", "dispatch"}

METHOD_CONTRACT = {
    "hypothesis": (
        "a sandbox-confined resolver with actual-byte ledgers and generation CAS "
        "can execute the static G1 safety contract without touching live roots"
    ),
    "changed_variable": (
        "replace generated policy predicates with real TemporaryDirectory file, "
        "copy, fsync, EXDEV, CAS, concurrency and recovery execution"
    ),
    "fixed_holdout": (
        "eight logical surfaces; distinct roots; traversal, ancestor symlink, "
        "hardlink, FIFO, duplicate job/artifact, O_EXCL, interrupted copy, EXDEV, "
        "file/parent fsync, concurrent writer, generation CAS, rollback and no fallback"
    ),
    "expected_delta": (
        "synthetic resolver_copy_ledger_runtime_validated becomes true while live "
        "adoption, live migration and repository fallback remain false"
    ),
    "stop_loss": (
        "sandbox paths only; synthetic bytes only; no live path, credential/customer "
        "payload, API, network, process, launchd, deployment, publication or price write"
    ),
    "model": "none",
    "sampling": "fixed-synthetic-runtime-fixtures",
    "evaluator": "deterministic-execution-and-receipt-validation",
    "acceptance": (
        "all runtime fixtures pass, every surface publishes once, ledgers match copied "
        "bytes, injected interruption preserves the old active generation, fsync paths "
        "execute, generation/epoch CAS invariants hold, and fallback attempts equal zero"
    ),
}

PLATEAU_REVIEW = {
    "prior_method_fingerprints": [
        "201cf84e8090c12ba743f47f9073dc733a87dd7a57874729b6ce302e4c627133",
        "d282b0fee8655a3cbc075bc332c0eb9ab2e5f18bac05abefdb7d63f97c5f53c0",
        "fa7086a124459dfa1ca3c872be7e4247d0e490e85dcc2e0ec3838626586bdde2",
    ],
    "same_method_repeated": False,
    "live_improvement_claimed": False,
    "synthetic_improvement_verified": True,
    "verified_improvement_scope": "synthetic-g1-only",
    "new_repair_point": "synthetic_private_root_resolver_and_actual_byte_ledger_runtime",
}

EXPECTED_FIXTURES = (
    ("distinct_non_overlapping_roots", "8"),
    ("all_surface_actual_byte_publish", "8/8"),
    ("non_adapter_fixed_53_covered", "53/53"),
    ("traversal_rejected", "INVALID_LOGICAL_PATH"),
    ("absolute_rejected", "INVALID_LOGICAL_PATH"),
    ("ancestor_symlink_rejected", "ANCESTOR_SYMLINK_OR_NON_DIRECTORY"),
    ("hardlink_rejected", "SOURCE_HARDLINK"),
    ("fifo_rejected", "SOURCE_NOT_REGULAR"),
    ("duplicate_artifact_rejected", "DUPLICATE_ARTIFACT"),
    ("duplicate_job_rejected", "DUPLICATE_JOB"),
    ("exclusive_generation_create", "GENERATION_EXISTS"),
    ("interrupted_copy_rejected", "SIMULATED_COPY_INTERRUPT"),
    ("interrupted_copy_active_unchanged", "clean"),
    ("exdev_actual_byte_fallback", "copied_and_published"),
    ("stale_generation_cas_rejected", "GENERATION_CAS_MISMATCH"),
    ("concurrent_writer_single_winner", "1"),
    ("prewrite_rollback_switches_generation", "g1"),
    ("postwrite_forward_repair_keeps_authority", "g3"),
    ("missing_artifact_no_repo_fallback", "ARTIFACT_NOT_FOUND_NO_FALLBACK"),
    ("backup_logical_surface_allowlist_no_repo_token", "0"),
    ("file_and_parent_fsync_executed", "yes"),
)

EXPECTED_METRICS = {
    "surface_publish_count": 8,
    "surface_count": 8,
    "non_adapter_artifact_count": 53,
    "fixture_passed": 21,
    "fixture_total": 21,
    "fsync_file_events": 117,
    "fsync_directory_events": 106,
    "exdev_publish_events": 1,
    "repo_fallback_attempts": 0,
    "network_calls": 0,
    "model_calls": 0,
    "live_path_operations": 0,
    "credential_customer_payload_reads": 0,
    "apps_script_google_calls": 0,
    "process_launchd_operations": 0,
    "customer_sends": 0,
    "price_writes": 0,
    "physical_paths_persisted": 0,
}


class PrototypeError(RuntimeError):
    """Fail-closed error with a stable machine-readable code."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class LedgerEntry:
    logical_path: str
    stream_sha256: str
    destination_sha256: str
    size: int
    target_mode: str = "0600"
    destination_matches_stream: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "logical_path": self.logical_path,
            "stream_sha256": self.stream_sha256,
            "destination_sha256": self.destination_sha256,
            "size": self.size,
            "target_mode": self.target_mode,
            "destination_matches_stream": self.destination_matches_stream,
        }


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _valid_identifier(value: str, code: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise PrototypeError(code)
    if value in {".", ".."}:
        raise PrototypeError(code)
    return value


def _logical_parts(value: str) -> tuple[str, ...]:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise PrototypeError("INVALID_LOGICAL_PATH")
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise PrototypeError("INVALID_LOGICAL_PATH")
    if str(path) != value:
        raise PrototypeError("INVALID_LOGICAL_PATH")
    return path.parts


def _dir_flags() -> int:
    return os.O_RDONLY | DIRECTORY | NOFOLLOW


def _open_child_dir(parent_fd: int, name: str) -> int:
    try:
        fd = os.open(name, _dir_flags(), dir_fd=parent_fd)
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise PrototypeError("ANCESTOR_SYMLINK_OR_NON_DIRECTORY") from exc
        raise
    current = os.fstat(fd)
    if (
        not stat.S_ISDIR(current.st_mode)
        or current.st_uid != os.geteuid()
        or stat.S_IMODE(current.st_mode) != 0o700
    ):
        os.close(fd)
        raise PrototypeError("UNSAFE_DIRECTORY")
    return fd


def _mkdir_child(parent_fd: int, name: str) -> int:
    try:
        os.mkdir(name, 0o700, dir_fd=parent_fd)
    except FileExistsError:
        pass
    return _open_child_dir(parent_fd, name)


def _open_relative_dir(root_fd: int, parts: Iterable[str], create: bool = False) -> int:
    fd = os.dup(root_fd)
    try:
        for part in parts:
            next_fd = _mkdir_child(fd, part) if create else _open_child_dir(fd, part)
            os.close(fd)
            fd = next_fd
        return fd
    except Exception:
        os.close(fd)
        raise


def _fsync_dir(fd: int) -> None:
    os.fsync(fd)


def _safe_unlink(name: str, parent_fd: int) -> None:
    try:
        os.unlink(name, dir_fd=parent_fd)
    except FileNotFoundError:
        pass


class SyntheticPrivateRootLab:
    """A resolver lab whose complete authority is inside one synthetic root."""

    def __init__(self, sandbox_root: Path, repo_root: Path):
        if not sandbox_root.is_absolute() or not repo_root.is_absolute():
            raise PrototypeError("ROOT_NOT_ABSOLUTE")
        sandbox_lstat = os.lstat(sandbox_root)
        if not stat.S_ISDIR(sandbox_lstat.st_mode) or stat.S_ISLNK(sandbox_lstat.st_mode):
            raise PrototypeError("SANDBOX_UNSAFE")
        self.sandbox_root = sandbox_root.resolve(strict=True)
        self.repo_root = repo_root.resolve(strict=False)
        if (
            self.sandbox_root == self.repo_root
            or self.repo_root in self.sandbox_root.parents
            or self.sandbox_root in self.repo_root.parents
        ):
            raise PrototypeError("SANDBOX_INSIDE_REPOSITORY")
        self.root_fd = os.open(self.sandbox_root, _dir_flags())
        opened = os.fstat(self.root_fd)
        if (
            opened.st_uid != os.geteuid()
            or not stat.S_ISDIR(opened.st_mode)
            or stat.S_IMODE(opened.st_mode) != 0o700
        ):
            os.close(self.root_fd)
            raise PrototypeError("SANDBOX_OWNER_MISMATCH")
        self.events: list[dict[str, Any]] = []
        self.fallback_attempts = 0
        self._closed = False
        self._init_layout()

    def close(self) -> None:
        if not self._closed:
            os.close(self.root_fd)
            self._closed = True

    def __enter__(self) -> "SyntheticPrivateRootLab":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _event(self, kind: str, surface: str, **extra: Any) -> None:
        row = {"kind": kind, "surface": surface}
        row.update(extra)
        self.events.append(row)

    def _init_layout(self) -> None:
        private_fd = _mkdir_child(self.root_fd, "private")
        inputs_fd = _mkdir_child(self.root_fd, "inputs")
        os.close(inputs_fd)
        roots: list[Path] = []
        try:
            for surface in SURFACES:
                surface_fd = _mkdir_child(private_fd, surface)
                generations_fd = _mkdir_child(surface_fd, "generations")
                claims_fd = _mkdir_child(surface_fd, "claims")
                _fsync_dir(generations_fd)
                _fsync_dir(claims_fd)
                os.close(generations_fd)
                os.close(claims_fd)
                os.close(surface_fd)
                roots.append(self.sandbox_root / "private" / surface)
            _fsync_dir(private_fd)
        finally:
            os.close(private_fd)
        canonical = [path.resolve(strict=True) for path in roots]
        if len(set(canonical)) != len(SURFACES):
            raise PrototypeError("ROOT_COLLISION")
        for left in canonical:
            for right in canonical:
                if left != right and (left in right.parents or right in left.parents):
                    raise PrototypeError("ROOT_OVERLAP")
            if (
                left == self.repo_root
                or self.repo_root in left.parents
                or left in self.repo_root.parents
            ):
                raise PrototypeError("REPOSITORY_ROOT_OVERLAP")
            if self.repo_root.exists() and os.path.samefile(left, self.repo_root):
                raise PrototypeError("REPOSITORY_ROOT_OVERLAP")

    def _surface_fd(self, surface: str) -> int:
        if surface not in SURFACES:
            raise PrototypeError("UNKNOWN_SURFACE")
        return _open_relative_dir(self.root_fd, ("private", surface))

    def _input_fd(self, source_name: str) -> int:
        _valid_identifier(source_name, "INVALID_SOURCE_NAME")
        return _open_relative_dir(self.root_fd, ("inputs", source_name))

    def create_input(self, source_name: str, files: dict[str, bytes]) -> None:
        _valid_identifier(source_name, "INVALID_SOURCE_NAME")
        if len(files) != len(set(files)):
            raise PrototypeError("DUPLICATE_ARTIFACT")
        inputs_fd = _open_relative_dir(self.root_fd, ("inputs",))
        try:
            try:
                os.mkdir(source_name, 0o700, dir_fd=inputs_fd)
            except FileExistsError as exc:
                raise PrototypeError("DUPLICATE_SOURCE") from exc
            source_fd = _open_child_dir(inputs_fd, source_name)
            try:
                for logical, payload in files.items():
                    parts = _logical_parts(logical)
                    parent_fd = _open_relative_dir(source_fd, parts[:-1], create=True)
                    try:
                        fd = os.open(
                            parts[-1],
                            os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
                            0o600,
                            dir_fd=parent_fd,
                        )
                        with os.fdopen(fd, "wb") as handle:
                            handle.write(payload)
                            handle.flush()
                            os.fsync(handle.fileno())
                        _fsync_dir(parent_fd)
                    finally:
                        os.close(parent_fd)
                _fsync_dir(source_fd)
            finally:
                os.close(source_fd)
            _fsync_dir(inputs_fd)
        finally:
            os.close(inputs_fd)

    def claim_job(self, surface: str, job_id: str) -> None:
        if surface not in REVIEW_SURFACES:
            raise PrototypeError("JOB_CLAIM_NOT_ALLOWED")
        _valid_identifier(job_id, "INVALID_JOB_ID")
        surface_fd = self._surface_fd(surface)
        claims_fd = _open_relative_dir(surface_fd, ("claims",))
        try:
            try:
                fd = os.open(
                    job_id,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
                    0o600,
                    dir_fd=claims_fd,
                )
            except FileExistsError as exc:
                raise PrototypeError("DUPLICATE_JOB") from exc
            with os.fdopen(fd, "wb") as handle:
                handle.write(b"claimed\n")
                handle.flush()
                os.fsync(handle.fileno())
            _fsync_dir(claims_fd)
            self._event("exclusive_job_claim", surface, job_id_hash=_sha256(job_id.encode()))
        finally:
            os.close(claims_fd)
            os.close(surface_fd)

    def _read_active_locked(self, surface_fd: int) -> dict[str, Any] | None:
        try:
            fd = os.open(
                "active.json", os.O_RDONLY | NOFOLLOW | NONBLOCK, dir_fd=surface_fd
            )
        except FileNotFoundError:
            return None
        try:
            info = os.fstat(fd)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_nlink != 1
                or info.st_uid != os.geteuid()
                or stat.S_IMODE(info.st_mode) != 0o600
            ):
                raise PrototypeError("ACTIVE_POINTER_UNSAFE")
            with os.fdopen(fd, "rb") as handle:
                fd = -1
                payload = json.load(handle)
        finally:
            if fd >= 0:
                os.close(fd)
        if set(payload) != {"epoch", "generation", "write_started"}:
            raise PrototypeError("ACTIVE_POINTER_INVALID")
        _valid_identifier(payload["generation"], "ACTIVE_POINTER_INVALID")
        if type(payload["epoch"]) is not int or payload["epoch"] < 1:
            raise PrototypeError("ACTIVE_POINTER_INVALID")
        if type(payload["write_started"]) is not bool:
            raise PrototypeError("ACTIVE_POINTER_INVALID")
        return payload

    def active_state(self, surface: str) -> dict[str, Any] | None:
        surface_fd = self._surface_fd(surface)
        try:
            return self._read_active_locked(surface_fd)
        finally:
            os.close(surface_fd)

    def _acquire_lock(self, surface_fd: int) -> int:
        try:
            return os.open(
                ".publish.lock",
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
                0o600,
                dir_fd=surface_fd,
            )
        except FileExistsError as exc:
            raise PrototypeError("PUBLISH_LOCK_BUSY") from exc

    def _write_active_locked(
        self, surface: str, surface_fd: int, generation: str, epoch: int, write_started: bool
    ) -> None:
        temp_name = f".active.{secrets.token_hex(8)}.tmp"
        fd: int | None = None
        try:
            fd = os.open(
                temp_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
                0o600,
                dir_fd=surface_fd,
            )
            payload = _canonical_json(
                {"epoch": epoch, "generation": generation, "write_started": write_started}
            ) + b"\n"
            with os.fdopen(fd, "wb") as handle:
                fd = None
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            self._event("fsync_file", surface, artifact="active_pointer")
            os.replace(temp_name, "active.json", src_dir_fd=surface_fd, dst_dir_fd=surface_fd)
            temp_name = ""
            _fsync_dir(surface_fd)
            self._event("fsync_directory", surface, artifact="surface_root")
        finally:
            if fd is not None:
                os.close(fd)
            if temp_name:
                _safe_unlink(temp_name, surface_fd)

    def _open_source_file(self, source_fd: int, parts: tuple[str, ...]) -> int:
        parent_fd = _open_relative_dir(source_fd, parts[:-1])
        try:
            before = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
            if not stat.S_ISREG(before.st_mode):
                raise PrototypeError("SOURCE_NOT_REGULAR")
            if before.st_nlink != 1:
                raise PrototypeError("SOURCE_HARDLINK")
            if before.st_uid != os.geteuid() or stat.S_IMODE(before.st_mode) != 0o600:
                raise PrototypeError("SOURCE_MODE_OR_OWNER")
            fd = os.open(
                parts[-1], os.O_RDONLY | NOFOLLOW | NONBLOCK, dir_fd=parent_fd
            )
            opened = os.fstat(fd)
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_nlink != 1
                or opened.st_uid != os.geteuid()
                or stat.S_IMODE(opened.st_mode) != 0o600
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
            ):
                os.close(fd)
                raise PrototypeError("SOURCE_CHANGED")
            return fd
        except OSError as exc:
            if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
                raise PrototypeError("SOURCE_SYMLINK") from exc
            raise
        finally:
            os.close(parent_fd)

    def _copy_one(
        self,
        surface: str,
        source_fd: int,
        stage_fd: int,
        logical: str,
        interrupt_after: int | None,
        copied_total: list[int],
    ) -> LedgerEntry:
        parts = _logical_parts(logical)
        src_fd = self._open_source_file(source_fd, parts)
        source_before = os.fstat(src_fd)
        parent_fd = _open_relative_dir(stage_fd, parts[:-1], create=True)
        dest_fd: int | None = None
        digest = hashlib.sha256()
        size = 0
        try:
            try:
                dest_fd = os.open(
                    parts[-1],
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
                    0o600,
                    dir_fd=parent_fd,
                )
            except FileExistsError as exc:
                raise PrototypeError("DESTINATION_EXISTS") from exc
            with os.fdopen(src_fd, "rb") as source, os.fdopen(dest_fd, "wb") as target:
                src_fd = -1
                dest_fd = None
                while True:
                    chunk = source.read(65536)
                    if not chunk:
                        break
                    target.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
                    copied_total[0] += len(chunk)
                    if interrupt_after is not None and copied_total[0] >= interrupt_after:
                        raise PrototypeError("SIMULATED_COPY_INTERRUPT")
                source_after = os.fstat(source.fileno())
                stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns", "st_nlink")
                if any(getattr(source_before, field) != getattr(source_after, field) for field in stable_fields):
                    raise PrototypeError("SOURCE_CHANGED_DURING_COPY")
                target.flush()
                os.fsync(target.fileno())
            self._event("fsync_file", surface, artifact="copied_artifact")
            verify_fd = os.open(
                parts[-1], os.O_RDONLY | NOFOLLOW | NONBLOCK, dir_fd=parent_fd
            )
            try:
                verified = os.fstat(verify_fd)
                if (
                    not stat.S_ISREG(verified.st_mode)
                    or verified.st_nlink != 1
                    or stat.S_IMODE(verified.st_mode) != 0o600
                ):
                    raise PrototypeError("DESTINATION_UNSAFE")
                destination_digest = hashlib.sha256()
                destination_size = 0
                with os.fdopen(verify_fd, "rb") as handle:
                    verify_fd = -1
                    while True:
                        chunk = handle.read(65536)
                        if not chunk:
                            break
                        destination_digest.update(chunk)
                        destination_size += len(chunk)
            finally:
                if verify_fd >= 0:
                    os.close(verify_fd)
            if destination_digest.hexdigest() != digest.hexdigest() or destination_size != size:
                raise PrototypeError("DESTINATION_READBACK_MISMATCH")
            _fsync_dir(parent_fd)
            self._event("fsync_directory", surface, artifact="artifact_parent")
            return LedgerEntry(
                logical,
                digest.hexdigest(),
                destination_digest.hexdigest(),
                size,
            )
        finally:
            if src_fd >= 0:
                os.close(src_fd)
            if dest_fd is not None:
                os.close(dest_fd)
            os.close(parent_fd)

    def _write_ledger(
        self, surface: str, stage_fd: int, generation: str, entries: list[LedgerEntry]
    ) -> dict[str, Any]:
        body = {
            "generation": generation,
            "surface": surface,
            "entries": [entry.as_dict() for entry in sorted(entries, key=lambda row: row.logical_path)],
            "source": "bytes_observed_during_copy",
            "physical_paths_persisted": 0,
        }
        body["entries_sha256"] = _sha256(_canonical_json(body["entries"]))
        fd = os.open(
            "_ledger.json",
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
            0o600,
            dir_fd=stage_fd,
        )
        with os.fdopen(fd, "wb") as handle:
            handle.write(_canonical_json(body) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._event("fsync_file", surface, artifact="actual_byte_ledger")
        seal = {
            "entries_sha256": body["entries_sha256"],
            "generation": generation,
            "surface": surface,
        }
        seal_fd = os.open(
            "_SEALED.json",
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
            0o600,
            dir_fd=stage_fd,
        )
        with os.fdopen(seal_fd, "wb") as handle:
            handle.write(_canonical_json(seal) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._event("fsync_file", surface, artifact="sealed_marker")
        _fsync_dir(stage_fd)
        self._event("fsync_directory", surface, artifact="generation_root")
        return body

    def _assert_sealed_generation(
        self, generation_fd: int, surface: str, generation: str
    ) -> dict[str, Any]:
        def read_regular(name: str) -> dict[str, Any]:
            fd = os.open(
                name, os.O_RDONLY | NOFOLLOW | NONBLOCK, dir_fd=generation_fd
            )
            try:
                info = os.fstat(fd)
                if (
                    not stat.S_ISREG(info.st_mode)
                    or info.st_nlink != 1
                    or stat.S_IMODE(info.st_mode) != 0o600
                ):
                    raise PrototypeError("GENERATION_UNSEALED")
                with os.fdopen(fd, "rb") as handle:
                    fd = -1
                    return json.load(handle)
            finally:
                if fd >= 0:
                    os.close(fd)

        try:
            ledger = read_regular("_ledger.json")
            seal = read_regular("_SEALED.json")
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise PrototypeError("GENERATION_UNSEALED") from exc
        if set(ledger) != {
            "generation", "surface", "entries", "source",
            "physical_paths_persisted", "entries_sha256",
        }:
            raise PrototypeError("GENERATION_UNSEALED")
        expected_seal = {
            "entries_sha256": ledger["entries_sha256"],
            "generation": generation,
            "surface": surface,
        }
        if (
            ledger["generation"] != generation
            or ledger["surface"] != surface
            or ledger["source"] != "bytes_observed_during_copy"
            or ledger["physical_paths_persisted"] != 0
            or ledger["entries_sha256"] != _sha256(_canonical_json(ledger["entries"]))
            or seal != expected_seal
        ):
            raise PrototypeError("GENERATION_UNSEALED")
        if not isinstance(ledger["entries"], list) or not ledger["entries"]:
            raise PrototypeError("GENERATION_UNSEALED")
        expected_entry_keys = {
            "logical_path", "stream_sha256", "destination_sha256", "size",
            "target_mode", "destination_matches_stream",
        }
        logical_paths: list[str] = []
        for entry in ledger["entries"]:
            if not isinstance(entry, dict) or set(entry) != expected_entry_keys:
                raise PrototypeError("GENERATION_UNSEALED")
            _logical_parts(entry["logical_path"])
            logical_paths.append(entry["logical_path"])
            if (
                not isinstance(entry["stream_sha256"], str)
                or len(entry["stream_sha256"]) != 64
                or entry["destination_sha256"] != entry["stream_sha256"]
                or type(entry["size"]) is not int
                or entry["size"] < 0
                or entry["target_mode"] != "0600"
                or entry["destination_matches_stream"] is not True
            ):
                raise PrototypeError("GENERATION_UNSEALED")
        if len(logical_paths) != len(set(logical_paths)):
            raise PrototypeError("GENERATION_UNSEALED")
        for entry in ledger["entries"]:
            parts = _logical_parts(entry["logical_path"])
            try:
                fd = self._open_source_file(generation_fd, parts)
            except (FileNotFoundError, PrototypeError) as exc:
                raise PrototypeError("GENERATION_ARTIFACT_MISMATCH") from exc
            digest = hashlib.sha256()
            size = 0
            with os.fdopen(fd, "rb") as handle:
                while True:
                    chunk = handle.read(65536)
                    if not chunk:
                        break
                    digest.update(chunk)
                    size += len(chunk)
            if (
                size != entry["size"]
                or digest.hexdigest() != entry["destination_sha256"]
            ):
                raise PrototypeError("GENERATION_ARTIFACT_MISMATCH")
        return ledger

    def _copy_stage_to_generation(
        self,
        surface: str,
        generations_fd: int,
        stage_name: str,
        generation: str,
        ledger: dict[str, Any],
    ) -> None:
        source_stage_fd = _open_child_dir(generations_fd, stage_name)
        generation_fd = _open_child_dir(generations_fd, generation)
        try:
            copied: list[LedgerEntry] = []
            for expected in ledger["entries"]:
                parts = _logical_parts(expected["logical_path"])
                src_fd = self._open_source_file(source_stage_fd, parts)
                parent_fd = _open_relative_dir(generation_fd, parts[:-1], create=True)
                try:
                    out_fd = os.open(
                        parts[-1],
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
                        0o600,
                        dir_fd=parent_fd,
                    )
                    digest = hashlib.sha256()
                    size = 0
                    with os.fdopen(src_fd, "rb") as source, os.fdopen(out_fd, "wb") as target:
                        while True:
                            chunk = source.read(65536)
                            if not chunk:
                                break
                            target.write(chunk)
                            digest.update(chunk)
                            size += len(chunk)
                        target.flush()
                        os.fsync(target.fileno())
                    _fsync_dir(parent_fd)
                    verify_fd = os.open(
                        parts[-1],
                        os.O_RDONLY | NOFOLLOW | NONBLOCK,
                        dir_fd=parent_fd,
                    )
                    destination_digest = hashlib.sha256()
                    destination_size = 0
                    with os.fdopen(verify_fd, "rb") as target:
                        while True:
                            chunk = target.read(65536)
                            if not chunk:
                                break
                            destination_digest.update(chunk)
                            destination_size += len(chunk)
                    if destination_digest.hexdigest() != digest.hexdigest() or destination_size != size:
                        raise PrototypeError("EXDEV_COPY_MISMATCH")
                    copied.append(LedgerEntry(
                        expected["logical_path"],
                        digest.hexdigest(),
                        destination_digest.hexdigest(),
                        size,
                    ))
                finally:
                    os.close(parent_fd)
            observed = [row.as_dict() for row in sorted(copied, key=lambda row: row.logical_path)]
            if observed != ledger["entries"]:
                raise PrototypeError("EXDEV_COPY_MISMATCH")
            self._write_ledger(surface, generation_fd, ledger["generation"], copied)
            _fsync_dir(generation_fd)
        finally:
            os.close(source_stage_fd)
            os.close(generation_fd)

    def publish(
        self,
        surface: str,
        generation: str,
        source_name: str,
        logical_paths: Iterable[str],
        expected_current: str | None,
        *,
        expected_epoch: int | None = None,
        interrupt_after: int | None = None,
        force_exdev: bool = False,
    ) -> dict[str, Any]:
        if surface not in SURFACES:
            raise PrototypeError("UNKNOWN_SURFACE")
        _valid_identifier(generation, "INVALID_GENERATION")
        _valid_identifier(source_name, "INVALID_SOURCE_NAME")
        paths = list(logical_paths)
        for path in paths:
            _logical_parts(path)
        if len(paths) != len(set(paths)):
            raise PrototypeError("DUPLICATE_ARTIFACT")
        if not paths:
            raise PrototypeError("EMPTY_GENERATION")
        if expected_current is not None:
            _valid_identifier(expected_current, "INVALID_EXPECTED_GENERATION")
            if type(expected_epoch) is not int or expected_epoch < 1:
                raise PrototypeError("EXPECTED_EPOCH_REQUIRED")
        elif expected_epoch is not None:
            raise PrototypeError("UNEXPECTED_EPOCH")

        surface_fd = self._surface_fd(surface)
        generations_fd = _open_relative_dir(surface_fd, ("generations",))
        source_fd = self._input_fd(source_name)
        stage_name = f".staging-{generation}-{secrets.token_hex(8)}"
        published_name = ""
        lock_fd: int | None = None
        try:
            try:
                os.stat(generation, dir_fd=generations_fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise PrototypeError("GENERATION_EXISTS")
            os.mkdir(stage_name, 0o700, dir_fd=generations_fd)
            stage_fd = _open_child_dir(generations_fd, stage_name)
            try:
                copied_total = [0]
                entries = [
                    self._copy_one(
                        surface,
                        source_fd,
                        stage_fd,
                        logical,
                        interrupt_after,
                        copied_total,
                    )
                    for logical in paths
                ]
                ledger = self._write_ledger(surface, stage_fd, generation, entries)
            finally:
                os.close(stage_fd)

            lock_fd = self._acquire_lock(surface_fd)
            current = self._read_active_locked(surface_fd)
            current_generation = None if current is None else current["generation"]
            current_epoch = None if current is None else current["epoch"]
            if current_generation != expected_current or current_epoch != expected_epoch:
                raise PrototypeError("GENERATION_CAS_MISMATCH")
            try:
                os.mkdir(generation, 0o700, dir_fd=generations_fd)
            except FileExistsError as exc:
                raise PrototypeError("GENERATION_EXISTS") from exc
            published_name = generation
            if force_exdev:
                try:
                    raise OSError(errno.EXDEV, "injected cross-device generation import")
                except OSError as exc:
                    if exc.errno != errno.EXDEV:
                        raise
                    self._copy_stage_to_generation(
                        surface, generations_fd, stage_name, generation, ledger
                    )
                self._event("exdev_copy_publish", surface, generation=generation)
            else:
                self._copy_stage_to_generation(
                    surface, generations_fd, stage_name, generation, ledger
                )
                self._event(
                    "exclusive_generation_publish", surface, generation=generation
                )
            _fsync_dir(generations_fd)
            self._event("fsync_directory", surface, artifact="generations_root")
            published_fd = _open_child_dir(generations_fd, generation)
            try:
                self._assert_sealed_generation(published_fd, surface, generation)
            finally:
                os.close(published_fd)
            next_epoch = 1 if current is None else current["epoch"] + 1
            try:
                self._write_active_locked(
                    surface, surface_fd, generation, next_epoch, False
                )
            except Exception:
                try:
                    observed = self._read_active_locked(surface_fd)
                except Exception:
                    observed = None
                if observed == {
                    "epoch": next_epoch,
                    "generation": generation,
                    "write_started": False,
                }:
                    # The pointer replace happened; preserving its sealed target
                    # is safer than deleting a generation now named active.
                    published_name = ""
                raise
            return {
                "surface": surface,
                "generation": generation,
                "entry_count": len(ledger["entries"]),
                "entries_sha256": ledger["entries_sha256"],
                "actual_bytes": sum(row["size"] for row in ledger["entries"]),
                "physical_paths_persisted": 0,
            }
        except Exception:
            if published_name:
                shutil.rmtree(
                    self.sandbox_root / "private" / surface / "generations" / published_name,
                    ignore_errors=True,
                )
                _fsync_dir(generations_fd)
            raise
        finally:
            if lock_fd is not None:
                os.close(lock_fd)
                _safe_unlink(".publish.lock", surface_fd)
                _fsync_dir(surface_fd)
            for name in (stage_name,):
                if name:
                    shutil.rmtree(
                        self.sandbox_root / "private" / surface / "generations" / name,
                        ignore_errors=True,
                    )
            os.close(source_fd)
            os.close(generations_fd)
            os.close(surface_fd)

    def read(self, surface: str, logical_path: str) -> bytes:
        parts = _logical_parts(logical_path)
        surface_fd = self._surface_fd(surface)
        try:
            active = self._read_active_locked(surface_fd)
            if active is None:
                raise PrototypeError("NO_ACTIVE_GENERATION")
            generations_fd = _open_relative_dir(surface_fd, ("generations",))
            generation_fd = _open_relative_dir(generations_fd, (active["generation"],))
            try:
                ledger = self._assert_sealed_generation(
                    generation_fd, surface, active["generation"]
                )
                matching = [
                    row for row in ledger["entries"]
                    if row["logical_path"] == logical_path
                ]
                if len(matching) != 1:
                    raise PrototypeError("ARTIFACT_NOT_FOUND_NO_FALLBACK")
                fd = self._open_source_file(generation_fd, parts)
                with os.fdopen(fd, "rb") as handle:
                    payload = handle.read()
                expected = matching[0]
                if (
                    len(payload) != expected["size"]
                    or _sha256(payload) != expected["destination_sha256"]
                ):
                    raise PrototypeError("ARTIFACT_LEDGER_MISMATCH")
                return payload
            except FileNotFoundError as exc:
                # Deliberately no repository lookup here.
                raise PrototypeError("ARTIFACT_NOT_FOUND_NO_FALLBACK") from exc
            finally:
                os.close(generation_fd)
                os.close(generations_fd)
        finally:
            os.close(surface_fd)

    def begin_authoritative_write(
        self, surface: str, generation: str, expected_epoch: int
    ) -> dict[str, Any]:
        _valid_identifier(generation, "INVALID_GENERATION")
        if type(expected_epoch) is not int or expected_epoch < 1:
            raise PrototypeError("EXPECTED_EPOCH_REQUIRED")
        surface_fd = self._surface_fd(surface)
        lock_fd: int | None = None
        try:
            lock_fd = self._acquire_lock(surface_fd)
            current = self._read_active_locked(surface_fd)
            if (
                current is None
                or current["generation"] != generation
                or current["epoch"] != expected_epoch
            ):
                raise PrototypeError("GENERATION_CAS_MISMATCH")
            self._write_active_locked(
                surface, surface_fd, generation, current["epoch"] + 1, True
            )
            return self._read_active_locked(surface_fd) or {}
        finally:
            if lock_fd is not None:
                os.close(lock_fd)
                _safe_unlink(".publish.lock", surface_fd)
                _fsync_dir(surface_fd)
            os.close(surface_fd)

    def rollback(
        self,
        surface: str,
        expected_current: str,
        prior_generation: str,
        expected_epoch: int,
    ) -> dict[str, Any]:
        _valid_identifier(expected_current, "INVALID_GENERATION")
        _valid_identifier(prior_generation, "INVALID_GENERATION")
        surface_fd = self._surface_fd(surface)
        generations_fd = _open_relative_dir(surface_fd, ("generations",))
        lock_fd: int | None = None
        try:
            lock_fd = self._acquire_lock(surface_fd)
            prior_fd = _open_relative_dir(generations_fd, (prior_generation,))
            self._assert_sealed_generation(prior_fd, surface, prior_generation)
            os.close(prior_fd)
            current = self._read_active_locked(surface_fd)
            if (
                current is None
                or current["generation"] != expected_current
                or current["epoch"] != expected_epoch
            ):
                raise PrototypeError("GENERATION_CAS_MISMATCH")
            if current["write_started"]:
                self._event("forward_repair_required", surface, generation=expected_current)
                return {
                    "action": "FORWARD_REPAIR",
                    "active_generation": expected_current,
                    "repo_fallback": False,
                }
            self._write_active_locked(
                surface, surface_fd, prior_generation, current["epoch"] + 1, False
            )
            self._event("prewrite_generation_rollback", surface, generation=prior_generation)
            return {
                "action": "ROLLED_BACK_PREWRITE",
                "active_generation": prior_generation,
                "repo_fallback": False,
            }
        finally:
            if lock_fd is not None:
                os.close(lock_fd)
                _safe_unlink(".publish.lock", surface_fd)
                _fsync_dir(surface_fd)
            os.close(generations_fd)
            os.close(surface_fd)

    def validate_backup_index(self, logical_sources: list[str]) -> dict[str, Any]:
        seen: set[str] = set()
        for logical in logical_sources:
            parts = _logical_parts(logical)
            if parts[0] not in SURFACES or logical in seen:
                raise PrototypeError("BACKUP_SOURCE_INVALID")
            if "repo" in {part.lower() for part in parts}:
                raise PrototypeError("REPO_BACKUP_FORBIDDEN")
            seen.add(logical)
        return {
            "logical_source_count": len(logical_sources),
            "classified_repo_paths": 0,
            "physical_paths_persisted": 0,
            "repo_fallback": False,
        }

    def root_contract(self) -> dict[str, Any]:
        return {
            "surface_count": len(SURFACES),
            "surfaces": list(SURFACES),
            "distinct_root_count": len(SURFACES),
            "overlap_count": 0,
            "physical_paths_persisted": 0,
            "repo_fallback_attempts": self.fallback_attempts,
        }


def _expect_error(name: str, code: str, action: Callable[[], Any]) -> dict[str, str]:
    try:
        action()
    except PrototypeError as exc:
        if exc.code != code:
            raise AssertionError(f"{name}: expected {code}, got {exc.code}") from exc
        return {"name": name, "result": "PASS", "observed": code}
    raise AssertionError(f"{name}: expected {code}")


def run_synthetic_fixtures(repo_root: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    fixtures: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="maplab-resolver-") as temp:
        sandbox = Path(temp)
        with SyntheticPrivateRootLab(sandbox, repo_root) as lab:
            root_contract = lab.root_contract()
            assert root_contract["distinct_root_count"] == len(SURFACES)
            fixtures.append({"name": "distinct_non_overlapping_roots", "result": "PASS", "observed": "8"})

            for index, surface in enumerate(SURFACES):
                source = f"seed{index}"
                if surface == "shared_review_non_adapter":
                    files = {
                        f"classified/item-{number:02d}.json":
                            f"synthetic:{surface}:{number}".encode()
                        for number in range(53)
                    }
                else:
                    files = {"payload.bin": f"synthetic:{surface}".encode()}
                lab.create_input(source, files)
                result = lab.publish(surface, "g1", source, files, None)
                assert result["actual_bytes"] == sum(len(payload) for payload in files.values())
                for logical, payload in files.items():
                    assert lab.read(surface, logical) == payload
            fixtures.append({"name": "all_surface_actual_byte_publish", "result": "PASS", "observed": "8/8"})
            fixtures.append({"name": "non_adapter_fixed_53_covered", "result": "PASS", "observed": "53/53"})

            fixtures.append(_expect_error("traversal_rejected", "INVALID_LOGICAL_PATH", lambda: lab.read("case_store", "../escape")))
            fixtures.append(_expect_error("absolute_rejected", "INVALID_LOGICAL_PATH", lambda: lab.read("case_store", "/escape")))

            # Ancestor symlink under the synthetic input root.
            inputs = sandbox / "inputs"
            os.mkdir(inputs / "symlinksrc", 0o700)
            os.symlink(inputs / "seed0", inputs / "symlinksrc" / "linked")
            fixtures.append(_expect_error(
                "ancestor_symlink_rejected",
                "ANCESTOR_SYMLINK_OR_NON_DIRECTORY",
                lambda: lab.publish("case_store", "g-symlink", "symlinksrc", ["linked/payload.bin"], "g1", expected_epoch=1),
            ))

            lab.create_input("hardlinksrc", {"original.bin": b"x"})
            os.link(inputs / "hardlinksrc" / "original.bin", inputs / "hardlinksrc" / "alias.bin")
            fixtures.append(_expect_error(
                "hardlink_rejected",
                "SOURCE_HARDLINK",
                lambda: lab.publish("case_store", "g-hardlink", "hardlinksrc", ["original.bin"], "g1", expected_epoch=1),
            ))

            os.mkdir(inputs / "fifosrc", 0o700)
            os.mkfifo(inputs / "fifosrc" / "pipe", 0o600)
            fixtures.append(_expect_error(
                "fifo_rejected",
                "SOURCE_NOT_REGULAR",
                lambda: lab.publish("case_store", "g-fifo", "fifosrc", ["pipe"], "g1", expected_epoch=1),
            ))

            fixtures.append(_expect_error(
                "duplicate_artifact_rejected",
                "DUPLICATE_ARTIFACT",
                lambda: lab.publish("case_store", "g-dup", "seed0", ["payload.bin", "payload.bin"], "g1", expected_epoch=1),
            ))
            lab.claim_job("adapter_review", "JOB-ONE")
            fixtures.append(_expect_error(
                "duplicate_job_rejected",
                "DUPLICATE_JOB",
                lambda: lab.claim_job("adapter_review", "JOB-ONE"),
            ))
            fixtures.append(_expect_error(
                "exclusive_generation_create",
                "GENERATION_EXISTS",
                lambda: lab.publish("case_store", "g1", "seed0", ["payload.bin"], "g1", expected_epoch=1),
            ))

            lab.create_input("interruptsrc", {"large.bin": b"z" * 131072})
            before = lab.active_state("case_store")
            fixtures.append(_expect_error(
                "interrupted_copy_rejected",
                "SIMULATED_COPY_INTERRUPT",
                lambda: lab.publish("case_store", "g-interrupt", "interruptsrc", ["large.bin"], "g1", expected_epoch=1, interrupt_after=1000),
            ))
            assert lab.active_state("case_store") == before
            assert not list((sandbox / "private" / "case_store" / "generations").glob(".staging-*"))
            fixtures.append({"name": "interrupted_copy_active_unchanged", "result": "PASS", "observed": "clean"})

            lab.create_input("exdevsrc", {"next.bin": b"exdev-bytes"})
            exdev = lab.publish(
                "case_store", "g2", "exdevsrc", ["next.bin"], "g1",
                expected_epoch=1, force_exdev=True,
            )
            assert exdev["actual_bytes"] == len(b"exdev-bytes")
            fixtures.append({"name": "exdev_actual_byte_fallback", "result": "PASS", "observed": "copied_and_published"})

            fixtures.append(_expect_error(
                "stale_generation_cas_rejected",
                "GENERATION_CAS_MISMATCH",
                lambda: lab.publish("case_store", "g-stale", "seed0", ["payload.bin"], "g1", expected_epoch=1),
            ))

            # Two concurrent first writers on a fresh logical surface lab: exactly one wins.
            with tempfile.TemporaryDirectory(prefix="maplab-resolver-race-") as race_temp:
                with SyntheticPrivateRootLab(Path(race_temp), repo_root) as race_lab:
                    race_lab.create_input("a", {"x": b"a"})
                    race_lab.create_input("b", {"x": b"b"})
                    outcomes: list[str] = []
                    outcome_lock = threading.Lock()
                    barrier = threading.Barrier(2)
                    def writer(generation: str, source: str) -> None:
                        barrier.wait()
                        try:
                            race_lab.publish("dispatch", generation, source, ["x"], None)
                            value = "WIN"
                        except PrototypeError as exc:
                            value = exc.code
                        with outcome_lock:
                            outcomes.append(value)
                    threads = [threading.Thread(target=writer, args=("ga", "a")), threading.Thread(target=writer, args=("gb", "b"))]
                    for thread in threads:
                        thread.start()
                    for thread in threads:
                        thread.join()
                    assert outcomes.count("WIN") == 1
                    assert len(outcomes) == 2
                    fixtures.append({"name": "concurrent_writer_single_winner", "result": "PASS", "observed": "1"})

            rollback = lab.rollback("case_store", "g2", "g1", expected_epoch=2)
            assert rollback["action"] == "ROLLED_BACK_PREWRITE"
            fixtures.append({"name": "prewrite_rollback_switches_generation", "result": "PASS", "observed": "g1"})
            lab.publish("case_store", "g3", "exdevsrc", ["next.bin"], "g1", expected_epoch=3)
            lab.begin_authoritative_write("case_store", "g3", expected_epoch=4)
            # Reopen the resolver to prove the barrier is durable, not in-memory.
            prior_events = list(lab.events)
            lab.close()
            reopened = SyntheticPrivateRootLab(sandbox, repo_root)
            lab = reopened
            lab.events[:0] = prior_events
            forward = lab.rollback("case_store", "g3", "g1", expected_epoch=5)
            assert forward["action"] == "FORWARD_REPAIR"
            assert lab.active_state("case_store")["generation"] == "g3"
            fixtures.append({"name": "postwrite_forward_repair_keeps_authority", "result": "PASS", "observed": "g3"})

            fixtures.append(_expect_error(
                "missing_artifact_no_repo_fallback",
                "ARTIFACT_NOT_FOUND_NO_FALLBACK",
                lambda: lab.read("case_store", "missing.bin"),
            ))
            backup = lab.validate_backup_index([f"{surface}/g1" for surface in SURFACES])
            assert backup["classified_repo_paths"] == 0 and not backup["repo_fallback"]
            fixtures.append({
                "name": "backup_logical_surface_allowlist_no_repo_token",
                "result": "PASS",
                "observed": "0",
            })
            assert any(row["kind"] == "fsync_file" for row in lab.events)
            assert any(row["kind"] == "fsync_directory" for row in lab.events)
            fixtures.append({"name": "file_and_parent_fsync_executed", "result": "PASS", "observed": "yes"})

            metrics = {
                "surface_publish_count": len(SURFACES),
                "surface_count": len(SURFACES),
                "non_adapter_artifact_count": 53,
                "fixture_passed": len(fixtures),
                "fixture_total": len(fixtures),
                "fsync_file_events": sum(row["kind"] == "fsync_file" for row in lab.events),
                "fsync_directory_events": sum(row["kind"] == "fsync_directory" for row in lab.events),
                "exdev_publish_events": sum(row["kind"] == "exdev_copy_publish" for row in lab.events),
                "repo_fallback_attempts": lab.fallback_attempts,
                "network_calls": 0,
                "model_calls": 0,
                "live_path_operations": 0,
                "credential_customer_payload_reads": 0,
                "apps_script_google_calls": 0,
                "process_launchd_operations": 0,
                "customer_sends": 0,
                "price_writes": 0,
                "physical_paths_persisted": 0,
            }
            lab.close()
            return fixtures, metrics


def method_fingerprint() -> str:
    return _sha256(_canonical_json({"method_version": METHOD_VERSION, **METHOD_CONTRACT}))


def _implementation_provenance(repo_root: Path) -> list[dict[str, str]]:
    relative_paths = (
        "scripts/maplab_private_root_resolver_prototype.py",
        "tests/test_maplab_private_root_resolver_prototype.py",
        "docs/margin-private-root-resolver-prototype.md",
    )
    rows: list[dict[str, str]] = []
    for relative in relative_paths:
        path = repo_root / relative
        info = os.lstat(path)
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise PrototypeError("IMPLEMENTATION_PROVENANCE_UNSAFE")
        rows.append({"path": relative, "sha256": _sha256(path.read_bytes())})
    return rows


def build_receipt(repo_root: Path, created_at: str) -> dict[str, Any]:
    if repo_root.resolve(strict=True) != repo_root:
        repo_root = repo_root.resolve(strict=True)
    if created_at != EXPECTED_CREATED_AT:
        raise PrototypeError("TIMESTAMP_MISMATCH")
    parsed = datetime.fromisoformat(created_at)
    if parsed.tzinfo is None:
        raise PrototypeError("TIMESTAMP_NOT_AWARE")
    fixtures, metrics = run_synthetic_fixtures(repo_root)
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "created_at": parsed.astimezone(timezone.utc).isoformat(),
        "method_version": METHOD_VERSION,
        "method_fingerprint": method_fingerprint(),
        "method_contract": METHOD_CONTRACT,
        "plateau_review": PLATEAU_REVIEW,
        "implementation_provenance": _implementation_provenance(repo_root),
        "scope": {
            "data_class": "synthetic-local-only",
            "surfaces": list(SURFACES),
            "temporary_directory_only": True,
            "live_roots_inspected": False,
            "live_paths_persisted": 0,
        },
        "fixtures": fixtures,
        "metrics": metrics,
        "decision": {
            "status": "SYNTHETIC_RESOLVER_COPY_LEDGER_VALIDATED",
            "adoption_status": "HOLD",
            "runtime_validation_scope": "temporarydirectory-synthetic-only",
            "resolver_copy_ledger_runtime_validated": True,
            "synthetic_resolver_copy_ledger_runtime_validated": True,
            "live_resolver_copy_ledger_runtime_validated": False,
            "synthetic_only": True,
            "eligible_for_live_change": False,
            "live_migration_performed": False,
            "repo_fallback_enabled": False,
            "injected_exdev_fallback_validated": True,
            "power_loss_durability_validated": False,
            "live_writer_quiescence_validated": False,
            "consumer_integration_validated": False,
            "sqlite_migration_validated": False,
            "current_private_roots_owner_only": False,
            "current_quote_line_deployed_truth_complete": False,
            "orders_writer_resolved": False,
            "header_capable_ingress_verified": False,
            "confirmed_leakage_amount": 0,
            "next_repair_point": "synthetic_backup_exclusion_fixture",
        },
    }
    body = {key: value for key, value in receipt.items() if key != "schema_version"}
    receipt["deterministic_body_sha256"] = _sha256(_canonical_json(body))
    validate_receipt(receipt)
    return receipt


def validate_receipt(receipt: dict[str, Any]) -> None:
    expected_keys = {
        "schema_version", "created_at", "method_version", "method_fingerprint",
        "method_contract", "plateau_review", "scope", "fixtures", "metrics",
        "decision", "implementation_provenance", "deterministic_body_sha256",
    }
    if set(receipt) != expected_keys or receipt.get("schema_version") != SCHEMA_VERSION:
        raise PrototypeError("RECEIPT_SCHEMA")
    if receipt.get("created_at") != EXPECTED_CREATED_AT:
        raise PrototypeError("RECEIPT_TIMESTAMP")
    try:
        parsed = datetime.fromisoformat(receipt["created_at"])
    except (TypeError, ValueError) as exc:
        raise PrototypeError("RECEIPT_TIMESTAMP") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise PrototypeError("RECEIPT_TIMESTAMP")
    if receipt["method_version"] != METHOD_VERSION:
        raise PrototypeError("RECEIPT_METHOD")
    if receipt["method_contract"] != METHOD_CONTRACT or receipt["plateau_review"] != PLATEAU_REVIEW:
        raise PrototypeError("RECEIPT_CONTRACT")
    if receipt["method_fingerprint"] != method_fingerprint():
        raise PrototypeError("RECEIPT_FINGERPRINT")
    provenance = receipt["implementation_provenance"]
    expected_paths = [
        "scripts/maplab_private_root_resolver_prototype.py",
        "tests/test_maplab_private_root_resolver_prototype.py",
        "docs/margin-private-root-resolver-prototype.md",
    ]
    if (
        not isinstance(provenance, list)
        or [row.get("path") for row in provenance] != expected_paths
        or any(
            not isinstance(row, dict)
            or set(row) != {"path", "sha256"}
            or not isinstance(row["sha256"], str)
            or len(row["sha256"]) != 64
            or any(character not in "0123456789abcdef" for character in row["sha256"])
            for row in provenance
        )
    ):
        raise PrototypeError("RECEIPT_IMPLEMENTATION_PROVENANCE")
    current_repo_root = Path(__file__).resolve(strict=True).parents[1]
    if provenance != _implementation_provenance(current_repo_root):
        raise PrototypeError("RECEIPT_IMPLEMENTATION_PROVENANCE")
    scope = receipt["scope"]
    if scope != {
        "data_class": "synthetic-local-only", "surfaces": list(SURFACES),
        "temporary_directory_only": True, "live_roots_inspected": False,
        "live_paths_persisted": 0,
    }:
        raise PrototypeError("RECEIPT_SCOPE")
    fixtures = receipt["fixtures"]
    expected_fixtures = [
        {"name": name, "result": "PASS", "observed": observed}
        for name, observed in EXPECTED_FIXTURES
    ]
    if fixtures != expected_fixtures:
        raise PrototypeError("RECEIPT_FIXTURES")
    metrics = receipt["metrics"]
    if (
        not isinstance(metrics, dict)
        or set(metrics) != set(EXPECTED_METRICS)
        or any(type(value) is not int for value in metrics.values())
        or metrics != EXPECTED_METRICS
    ):
        raise PrototypeError("RECEIPT_METRICS")
    expected_decision = {
        "status": "SYNTHETIC_RESOLVER_COPY_LEDGER_VALIDATED",
        "adoption_status": "HOLD",
        "runtime_validation_scope": "temporarydirectory-synthetic-only",
        "resolver_copy_ledger_runtime_validated": True,
        "synthetic_resolver_copy_ledger_runtime_validated": True,
        "live_resolver_copy_ledger_runtime_validated": False,
        "synthetic_only": True,
        "eligible_for_live_change": False,
        "live_migration_performed": False,
        "repo_fallback_enabled": False,
        "injected_exdev_fallback_validated": True,
        "power_loss_durability_validated": False,
        "live_writer_quiescence_validated": False,
        "consumer_integration_validated": False,
        "sqlite_migration_validated": False,
        "current_private_roots_owner_only": False,
        "current_quote_line_deployed_truth_complete": False,
        "orders_writer_resolved": False,
        "header_capable_ingress_verified": False,
        "confirmed_leakage_amount": 0,
        "next_repair_point": "synthetic_backup_exclusion_fixture",
    }
    if receipt["decision"] != expected_decision:
        raise PrototypeError("RECEIPT_DECISION")
    body = {
        key: value for key, value in receipt.items()
        if key not in {"schema_version", "deterministic_body_sha256"}
    }
    if receipt["deterministic_body_sha256"] != _sha256(_canonical_json(body)):
        raise PrototypeError("RECEIPT_BODY_HASH")
    serialized = _canonical_json(receipt).lower()
    forbidden = (
        b"/users/", b"/tmp/", b"/private/var/", b"/var/folders/",
        b"/home/", b"/volumes/", b"file://", b"customer_name", b"phone",
        b"address", b"token_value", b"api_key_value",
    )
    if any(value in serialized for value in forbidden):
        raise PrototypeError("RECEIPT_PATH_OR_SECRET_LEAK")


def write_private_receipt(path: Path, receipt: dict[str, Any]) -> None:
    validate_receipt(receipt)
    if not path.is_absolute() or path.parent != PRIVATE_RECEIPT_ROOT:
        raise PrototypeError("RECEIPT_PATH_OUTSIDE_PRIVATE_ROOT")
    parent = path.parent
    current = parent
    while True:
        if current.is_symlink():
            raise PrototypeError("RECEIPT_ANCESTOR_SYMLINK")
        if current.parent == current:
            break
        current = current.parent
    parent_lstat = os.lstat(parent)
    if not stat.S_ISDIR(parent_lstat.st_mode) or stat.S_IMODE(parent_lstat.st_mode) != 0o700:
        raise PrototypeError("RECEIPT_PARENT_UNSAFE")
    parent_fd = os.open(parent, _dir_flags())
    temp_name = f".{path.name}.{secrets.token_hex(8)}.tmp"
    fd: int | None = None
    try:
        try:
            existing = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None and not stat.S_ISREG(existing.st_mode):
            raise PrototypeError("RECEIPT_TARGET_UNSAFE")
        fd = os.open(
            temp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW,
            0o600, dir_fd=parent_fd,
        )
        with os.fdopen(fd, "wb") as handle:
            fd = None
            handle.write(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True).encode() + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        temp_name = ""
        final_fd = os.open(path.name, os.O_RDONLY | NOFOLLOW, dir_fd=parent_fd)
        try:
            info = os.fstat(final_fd)
            if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
                raise PrototypeError("RECEIPT_POST_WRITE_MODE")
            with os.fdopen(final_fd, "r", encoding="utf-8") as handle:
                final_fd = -1
                validate_receipt(json.load(handle))
        finally:
            if final_fd >= 0:
                os.close(final_fd)
        _fsync_dir(parent_fd)
    finally:
        if fd is not None:
            os.close(fd)
        if temp_name:
            _safe_unlink(temp_name, parent_fd)
        os.close(parent_fd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the synthetic MAPLAB private-root resolver prototype")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--created-at", default=EXPECTED_CREATED_AT)
    args = parser.parse_args()
    receipt = build_receipt(args.repo_root.resolve(strict=True), args.created_at)
    write_private_receipt(args.receipt, receipt)
    print(json.dumps({
        "status": receipt["decision"]["status"],
        "adoption_status": receipt["decision"]["adoption_status"],
        "fixture_passed": receipt["metrics"]["fixture_passed"],
        "fixture_total": receipt["metrics"]["fixture_total"],
        "surface_publish_count": receipt["metrics"]["surface_publish_count"],
        "repo_fallback_attempts": receipt["metrics"]["repo_fallback_attempts"],
        "eligible_for_live_change": receipt["decision"]["eligible_for_live_change"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
