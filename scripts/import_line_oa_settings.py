#!/usr/bin/env python3
"""Import a read-only LINE OA settings snapshot into the local A6 store.

The JSON payload is read from stdin so private saved-reply content never needs
to be written to a tracked source file. The destination SQLite DB is gitignored.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bot_a6.case_store import CaseStore  # noqa: E402


def import_payload(payload: dict) -> dict:
    store = CaseStore.from_env(REPO_ROOT)
    result = store.import_line_oa_settings(payload)
    os.chmod(store.db_path, 0o600)
    summary = store.latest_line_oa_settings_summary()
    output = asdict(result)
    output["db_path"] = str(store.db_path)
    output["policy"] = {
        "auto_send_count": summary["auto_send_count"] if summary else None,
        "human_review_count": summary["human_review_count"] if summary else None,
        "financial_count": summary["financial_count"] if summary else None,
    }
    return output


def serve_once(port: int) -> int:
    class Handler(BaseHTTPRequestHandler):
        imported = False

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def do_GET(self) -> None:  # noqa: N802
            body = (
                "<!doctype html><meta charset='utf-8'><title>A6 LINE settings import</title>"
                "<h1>A6 local import</h1>"
                "<form method='post' action='/import'>"
                "<label>JSON payload<textarea name='payload' rows='12' cols='80'></textarea></label>"
                "<button type='submit'>Import to local A6 DB</button></form>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/import":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 1_000_000:
                self.send_error(400, "invalid payload length")
                return
            form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
            try:
                payload = json.loads(form.get("payload", [""])[0])
                output = import_payload(payload)
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_error(400, html.escape(str(exc)))
                return
            Handler.imported = True
            body = (
                "<!doctype html><meta charset='utf-8'><title>A6 import complete</title>"
                f"<h1>Imported</h1><p>tags={output['tag_count']}; "
                f"saved_replies={output['saved_reply_count']}; "
                f"auto_send={output['policy']['auto_send_count']}</p>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            print(json.dumps(output, ensure_ascii=False, sort_keys=True), flush=True)

    server = HTTPServer(("127.0.0.1", port), Handler)
    while not Handler.imported:
        server.handle_request()
    server.server_close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve-once", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.serve_once:
        return serve_once(args.port)
    output = import_payload(json.load(sys.stdin))
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
