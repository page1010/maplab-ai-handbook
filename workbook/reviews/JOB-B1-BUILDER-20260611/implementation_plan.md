# Implementation Plan - Browser Bridge Refactoring

JOB_ID: JOB-B1-BUILDER-20260611
ROLE: B1 Investment OS Builder
DATE: 2026-06-11

## User Need

Audit and refactor the Chrome Extension Browser Bridge (`bot/http_bridge.py`, `chrome-extension/background.js`, `chrome-extension/content.js`) to fix memory leaks, execution thread blocking, desync timeout races, port collisions on port `9876`, and duplicate event listener registration in content scripts.

## Scope

- Move legacy clipboard port in `bot/bot.py` from `9876` to `9875` to resolve process conflicts.
- Refactor `bot/http_bridge.py` from a blocking long-poll queue to a lock-protected status dictionary with instant non-blocking responses.
- Implement slide-window cache cleanup in the Python server to remove expired commands older than 60 seconds (solving memory leaks).
- Update `chrome-extension/background.js` to short-poll every 1000ms when idle and 100ms when active, resolving worker shutdown issues.
- Fix `chrome-extension/content.js` to guard message listener registration and avoid duplicate actions.
- Perform compilation syntax and endpoint smoke tests using curl.

## Out Of Scope

- No third-party Python library additions (remain zero-dependency standard library).
- No production WordPress updates.
- No broker/order credentials manipulation.
