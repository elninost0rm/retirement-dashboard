#!/usr/bin/env python3
"""Local web server for the Retirement Flexibility Calculator dashboard.

Serves index.html on http://127.0.0.1:<port> and opens it in your default
browser (Chrome, if that is what you use). Standard library only - no
pip installs required.

Usage:
    python serve.py                # start and open the browser
    python serve.py --no-browser   # start without opening a window
    python serve.py --port 9000    # use a specific port
"""

import argparse
import http.server
import os
import socket
import threading
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PORT = 8420


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        # Always serve the freshest version while iterating locally.
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def find_free_port(start):
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise SystemExit(f"No free port found in range {start}-{start + 19}.")


def main():
    parser = argparse.ArgumentParser(description="Serve the retirement dashboard locally.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="preferred port (default: 8420)")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser window")
    args = parser.parse_args()

    port = find_free_port(args.port)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), DashboardHandler)
    url = f"http://127.0.0.1:{port}/"

    print("Retirement Flexibility Calculator")
    print(f"  Serving: {os.path.join(ROOT, 'index.html')}")
    print(f"  Open:    {url}")
    print("  Stop:    Ctrl+C")
    print()

    if not args.no_browser:
        threading.Timer(0.7, webbrowser.open, args=[url]).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
