#!/usr/bin/env python3
"""Read-only export of the A8 theme-song Google Doc as plain text.

Reuses the repository's existing Google OAuth profile the same way
a8_download_drive_case.py does; never prints credentials. Output goes to
stdout only, so callers decide where the text lands. Scope: this one
Owner-authorized doc (T-A8-002 lyrics SSOT readback), nothing else.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN_PATH = Path.home() / ".claude/mcp-keys/google-token.json"
DOC_ID = "1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI"


def get_access_token() -> str:
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


def main() -> int:
    token = get_access_token()
    url = (
        f"https://www.googleapis.com/drive/v3/files/{DOC_ID}/export"
        + "?" + urllib.parse.urlencode({"mimeType": "text/plain"})
    )
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        sys.stdout.write(response.read().decode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
