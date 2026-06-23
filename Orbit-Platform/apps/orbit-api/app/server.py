import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", "8080"))
APP_NAME = os.getenv("APP_NAME", "orbit-api")
MESSAGE = os.getenv("MESSAGE", "Welcome to Orbit Platform")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local-dev")
VERSION = os.getenv("VERSION", "0.1.0")

REQUEST_COUNT = 0


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))

    def _send_metrics(self):
        metrics = f"""# HELP orbit_api_requests_total Total HTTP requests handled by orbit-api
# TYPE orbit_api_requests_total counter
orbit_api_requests_total{{app="{APP_NAME}",environment="{ENVIRONMENT}",version="{VERSION}"}} {REQUEST_COUNT}

# HELP orbit_api_info Static application information
# TYPE orbit_api_info gauge
orbit_api_info{{app="{APP_NAME}",environment="{ENVIRONMENT}",version="{VERSION}"}} 1
"""

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.end_headers()
        self.wfile.write(metrics.encode("utf-8"))

    def _send_html(self, status_code, html):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        global REQUEST_COUNT
        REQUEST_COUNT += 1

        path = self.path.split("?")[0]

        if path == "/metrics":
            self._send_metrics()
            return

        if path == "/healthz":
            self._send_json(200, {"status": "healthy"})
            return

        if path == "/readyz":
            self._send_json(200, {"status": "ready"})
            return

        if path == "/api/status":
            self._send_json(200, {
                "app": APP_NAME,
                "message": MESSAGE,
                "environment": ENVIRONMENT,
                "version": VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            return

        if path != "/":
            self._send_json(404, {"error": "not found", "path": path})
            return

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{APP_NAME}</title>
</head>
<body>
  <h1>{APP_NAME}</h1>
  <p>{MESSAGE}</p>
  <p>Environment: {ENVIRONMENT}</p>
  <p>Version: {VERSION}</p>
  <p>Port: {PORT}</p>
  <ul>
    <li><a href="/api/status">API Status</a></li>
    <li><a href="/healthz">Health Check</a></li>
    <li><a href="/readyz">Readiness Check</a></li>
    <li><a href="/metrics">Metrics</a></li>
  </ul>
</body>
</html>
"""
        self._send_html(200, html)


server = HTTPServer(("0.0.0.0", PORT), Handler)
print(f"{APP_NAME} listening on port {PORT}")
server.serve_forever()