#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error

BRIDGE_URL = "http://127.0.0.1:9876/execute"

def send_command(payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BRIDGE_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.URLError as e:
        print(f"Error: Could not connect to Browser Bridge. Make sure http_bridge.py is running. {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from Bridge.")
        sys.exit(1)

def read_chat(lines=5):
    res = send_command({"action": "read_last_messages", "count": lines})
    if "error" in res:
        print(f"Error reading chat: {res['error']}")
    elif res.get("success") is False:
        print(f"Error reading chat: {res.get('result')}")
    else:
        print(res.get("result", {}).get("text", ""))

def paste_chat(text, auto_send=False):
    res = send_command({"action": "paste_text", "text": text, "auto_send": auto_send})
    if "error" in res:
        print(f"Error pasting chat: {res['error']}")
    elif res.get("success") is False:
        print(f"Error pasting chat: {res.get('result')}")
    else:
        print("Successfully pasted text into browser.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 browser_control.py read [lines]")
        print("       python3 browser_control.py paste \"your text\" [--send]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "read":
        lines = 5
        if len(sys.argv) > 2:
            try:
                lines = int(sys.argv[2])
            except ValueError:
                pass
        read_chat(lines)
        
    elif command == "paste":
        if len(sys.argv) < 3:
            print("Error: Please provide text to paste.")
            sys.exit(1)
        text = sys.argv[2]
        auto_send = "--send" in sys.argv
        paste_chat(text, auto_send)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
