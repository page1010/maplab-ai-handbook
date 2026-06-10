# Changed Files - Browser Bridge Refactoring

JOB_ID: JOB-B1-BUILDER-20260611
ROLE: B1 Investment OS Builder
DATE: 2026-06-11

The following files have been modified in the repository:

### 1. [bot/bot.py](file:///Users/pagemacmini/maplab-ai-handbook/bot/bot.py)
*   **Diff**:
    ```diff
    -CLIP_SERVER_PORT = 9876
    +CLIP_SERVER_PORT = 9875
    ```
*   **Reason**: Changed clipboard server port to 9875 to resolve bind collision on port 9876.

### 2. [bot/http_bridge.py](file:///Users/pagemacmini/maplab-ai-handbook/bot/http_bridge.py)
*   **Reason**: Refactored blocking long-poll queue to non-blocking short-polling with cache expiration cleanup, solving execute desync races and memory leaks.

### 3. [chrome-extension/background.js](file:///Users/pagemacmini/maplab-ai-handbook/chrome-extension/background.js)
*   **Reason**: Changed extension long-polling loops to non-blocking short-polls with interval tuning (1s idle, 100ms processing) to prevent service worker timeouts.

### 4. [chrome-extension/content.js](file:///Users/pagemacmini/maplab-ai-handbook/chrome-extension/content.js)
*   **Reason**: Wrapped message listener registration in `window.hasMaplabBridgeListener` guard to prevent duplication errors on dynamic script injection.
