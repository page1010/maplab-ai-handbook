#!/bin/bash
cd "$(dirname "$0")"

PID_FILE="http_bridge.pid"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p $OLD_PID > /dev/null; then
        echo "Killing old bridge server (PID: $OLD_PID)"
        kill -9 $OLD_PID
    fi
fi

echo "Starting HTTP Browser Bridge on port 9876..."
nohup python3 http_bridge.py > bridge.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"
echo "Bridge server started with PID $NEW_PID"
