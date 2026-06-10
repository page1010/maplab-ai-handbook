#!/usr/bin/env python3
import json
import time
import uuid
import threading
import queue
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# In-memory storage and state synchronization for commands
import time
import threading

# Thread safety lock
bridge_lock = threading.Lock()

# command_id -> {"action": "...", "text": "...", "status": "pending|completed", "result": ..., "ts": ...}
commands = {}

# List of pending command IDs to be retrieved by Extension short-poll
pending_commands = []

# Event dictionary to wait for specific command results: command_id -> threading.Event()
command_events = {}

class BridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/poll':
            response_data = {}
            with bridge_lock:
                if pending_commands:
                    cmd_id = pending_commands.pop(0)
                    cmd = commands.get(cmd_id)
                    if cmd:
                        print(f"Delivering command {cmd_id} to extension via short-poll")
                        response_data = {
                            "command_id": cmd_id,
                            "action": cmd.get("action"),
                            "text": cmd.get("text"),
                            "count": cmd.get("count", 5),
                            "auto_send": cmd.get("auto_send", False)
                        }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/execute':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req = json.loads(post_data.decode('utf-8'))
            
            cmd_id = str(uuid.uuid4())
            event = threading.Event()
            
            with bridge_lock:
                # Slide-window cleanup of expired commands (older than 60s) to prevent memory leaks
                now = time.time()
                expired = [k for k, v in list(commands.items()) if now - v.get("ts", 0) > 60.0]
                for k in expired:
                    commands.pop(k, None)
                    command_events.pop(k, None)
                    if k in pending_commands:
                        pending_commands.remove(k)
                
                # Register new command execution
                commands[cmd_id] = {
                    "action": req.get("action"),
                    "text": req.get("text", ""),
                    "count": req.get("count", 5),
                    "auto_send": req.get("auto_send", False),
                    "status": "pending",
                    "ts": now
                }
                command_events[cmd_id] = event
                pending_commands.append(cmd_id)
            
            # Block the current request thread for up to 12 seconds waiting for the extension to complete the action
            completed = event.wait(timeout=12.0)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response_payload = {"error": "timeout or no active tabs"}
            with bridge_lock:
                if cmd_id in commands:
                    if completed and commands[cmd_id]["status"] == "completed":
                        response_payload = commands[cmd_id].get("result", {})
                    # Delete command from memory immediately after resolution/timeout
                    commands.pop(cmd_id, None)
                    command_events.pop(cmd_id, None)
            
            self.wfile.write(json.dumps(response_payload).encode('utf-8'))
                
        elif self.path == '/result':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            res = json.loads(post_data.decode('utf-8'))
            
            cmd_id = res.get("command_id")
            print(f"Received result for command {cmd_id}")
            
            with bridge_lock:
                if cmd_id in commands:
                    commands[cmd_id]["status"] = "completed"
                    commands[cmd_id]["result"] = res
                    if cmd_id in command_events:
                        command_events[cmd_id].set()
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass

def run(server_class=ThreadingHTTPServer, handler_class=BridgeHandler, port=9876):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting Extension Browser Bridge on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
