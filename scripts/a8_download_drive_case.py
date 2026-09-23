#!/usr/bin/env python3
"""Download one Google Drive case folder to a private local asset vault.

The downloader reuses the repository's existing Google OAuth profile, never
prints credentials, preserves Drive filenames, and writes a SHA-256 manifest.
It is intentionally folder-scoped and does not recurse.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN_PATH = Path.home() / ".claude/mcp-keys/google-token.json"


def get_access_token() -> str:
    """Refresh a short-lived token without mutating the shared auth profile."""
    profile = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    payload = urllib.parse.urlencode(
        {
            "client_id": profile["client_id"],
            "client_secret": profile["client_secret"],
            "refresh_token": profile["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode()
    request = urllib.request.Request(profile["token_uri"], data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())["access_token"]


def drive_files(folder_id: str, access_token: str) -> list[dict]:
    params = {
        "q": f"'{folder_id}' in parents and trashed=false",
        "fields": "files(id,name,mimeType,size,modifiedTime)",
        "pageSize": "1000",
    }
    request = urllib.request.Request(
        "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(params),
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read()).get("files", [])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(file_id: str, target: Path, access_token: str) -> None:
    request = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    temporary = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(request, timeout=180) as response, temporary.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    os.chmod(temporary, 0o600)
    temporary.replace(target)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    access_token = get_access_token()
    files = sorted(drive_files(args.folder_id, access_token), key=lambda item: item["name"])
    print(f"folder_files={len(files)}")
    if args.dry_run:
        for item in files:
            print(f"{item['name']}\t{item.get('mimeType', '')}\t{item.get('size', '')}")
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(args.output_dir, 0o700)
    manifest: list[dict] = []
    for item in files:
        safe_name = Path(item["name"]).name
        if safe_name != item["name"]:
            raise ValueError(f"unsafe Drive filename: {item['name']!r}")
        target = args.output_dir / safe_name
        expected_size = int(item.get("size") or 0)
        if not target.exists() or (expected_size and target.stat().st_size != expected_size):
            download(item["id"], target, access_token)
        os.chmod(target, 0o600)
        manifest.append(
            {
                "drive_file_id": item["id"],
                "name": safe_name,
                "mime_type": item.get("mimeType"),
                "modified_time": item.get("modifiedTime"),
                "size": target.stat().st_size,
                "sha256": sha256(target),
            }
        )
        print(f"ready={safe_name} bytes={target.stat().st_size}")

    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {"source_folder_id": args.folder_id, "files": manifest},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    os.chmod(manifest_path, 0o600)
    print(f"manifest={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
