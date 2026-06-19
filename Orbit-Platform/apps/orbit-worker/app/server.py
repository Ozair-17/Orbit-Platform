import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", "8080"))
APP_NAME = os.getenv("APP_NAME", "orbit-worker")
MESSAGE = os.getenv("MESSAGE", "Welcome to Orbit Worker")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local-dev")
VERSION = os.getenv("VERSION", "0.1.0")


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))

    def _send_html(self, status_code, html):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        if self.path == "/healthz":
            self._send_json(200, {"status": "healthy"})
            return

        if self.path == "/readyz":
            self._send_json(200, {"status": "ready"})
            return

        if self.path == "/api/status":
            self._send_json(200, {
                "app": APP_NAME,
                "message": MESSAGE,
                "environment": ENVIRONMENT,
                "version": VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            return

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{APP_NAME}</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: linear-gradient(135deg, #0f172a, #1e293b);
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .card {{
      width: 90%;
      max-width: 780px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 24px;
      padding: 40px;
      box-shadow: 0 25px 80px rgba(0, 0, 0, 0.35);
    }}

    .badge {{
      display: inline-block;
      padding: 8px 14px;
      border-radius: 999px;
      background: #22c55e;
      color: #052e16;
      font-weight: 700;
      font-size: 13px;
      margin-bottom: 20px;
    }}

    h1 {{
      font-size: 48px;
      margin: 0 0 12px;
      letter-spacing: -1px;
    }}

    p {{
      font-size: 18px;
      color: #cbd5e1;
      line-height: 1.6;
    }}

    .grid {{
      margin-top: 28px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
    }}

    .tile {{
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 16px;
      padding: 18px;
    }}

    .label {{
      color: #94a3b8;
      font-size: 13px;
      margin-bottom: 6px;
    }}

    .value {{
      font-size: 17px;
      font-weight: 700;
    }}

    code {{
      background: rgba(15, 23, 42, 0.9);
      padding: 4px 8px;
      border-radius: 8px;
      color: #93c5fd;
    }}

    .links {{
      margin-top: 28px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}

    a {{
      color: #0f172a;
      background: #f8fafc;
      padding: 12px 16px;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <main class="card">
    <div class="badge">Kubernetes Deployment Running</div>
    <h1>{APP_NAME}</h1>
    <p>{MESSAGE}</p>
    <p>
      This app is running inside your local Kubernetes platform lab and is exposed through a Kubernetes Service.
    </p>

    <div class="grid">
      <div class="tile">
        <div class="label">Environment</div>
        <div class="value">{ENVIRONMENT}</div>
      </div>

      <div class="tile">
        <div class="label">Version</div>
        <div class="value">{VERSION}</div>
      </div>

      <div class="tile">
        <div class="label">Port</div>
        <div class="value">{PORT}</div>
      </div>

      <div class="tile">
        <div class="label">Health Checks</div>
        <div class="value">Ready / Healthy</div>
      </div>
    </div>

    <div class="links">
      <a href="/api/status">View API Status</a>
      <a href="/healthz">Health Check</a>
      <a href="/readyz">Readiness Check</a>
    </div>

    <p style="margin-top: 28px; font-size: 14px;">
      Try: <code>curl http://localhost:8080/api/status</code>
    </p>
  </main>
</body>
</html>
"""
        self._send_html(200, html)


server = HTTPServer(("0.0.0.0", PORT), Handler)
print(f"{APP_NAME} listening on port {PORT}")
server.serve_forever()