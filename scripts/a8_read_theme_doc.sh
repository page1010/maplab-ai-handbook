#!/bin/bash
# Read-only wrapper: export A8 theme-song Google Doc as plain text to stdout.
set -euo pipefail
exec /usr/bin/python3 "$(dirname "$0")/a8_read_theme_doc.py"
