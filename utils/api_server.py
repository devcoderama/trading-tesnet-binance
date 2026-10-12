import json, os, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from config.settings import settings
from utils.db import get_config, set_config, load_trades, save_audit, load_audit

class Handler(BaseHTTPRequestHandler):
    def _auth_ok(self):
        import os
        expected = os.getenv("MINIAPP_TOKEN")
        if not expected:
            return True
        q = self.path.split("?",1)[1] if "?" in self.path else ""
        token = None
        for part in q.split("&"):
            if part.startswith("t="):
                token = part[2:]
        if token == expected:
            return True
        auth = self.headers.get("Authorization","")
        if auth == "Bearer " + expected:
            return True
        return False

    def _json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api") and not self._auth_ok():
            self._json(401, {"ok": False, "error": "unauthorized"})
            return
        p = self.path.split("?")[0]
        if p == "/api/ai/providers":
            provs = [x.strip() for x in (get_config("AI_PROVIDERS", settings.AI_PROVIDERS) or "").split(",") if x.strip()]
            self._json(200, {"providers": provs})
            return
        if p == "/api/audit":
            self._json(200, {"audit": load_audit(20)})
            return
        if p == "/api/history":
            rows = load_trades()[-20:]
            self._json(200, {"history": rows})
            return
        if p == "/api/status":
            status = {
                "bot_type": settings.BOT_TYPE,
                "interval": get_config("INTERVAL", settings.INTERVAL),
                "risk": get_config("RISK_LEVEL", "MEDIUM"),
                "symbols": get_config("SYMBOLS", settings.SYMBOLS),
                "symbol_mode": get_config("SYMBOL_MODE", "auto"),
                "ai_mode": get_config("AI_MODE", "multi"),
                "paused": get_config("BOT_PAUSED", "false"),
            }
            self._json(200, status)
            return
        # serve static
        path = self.path.split("?")[0]
        base = os.path.join(os.path.dirname(__file__), "..", "miniapp")
        if path in ("/", "/index.html"):
            fp = os.path.join(base, "index.html")
        else:
            fp = os.path.join(base, path.lstrip("/"))
        if os.path.isfile(fp):
            with open(fp, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self._auth_ok():
            self._json(401, {"ok": False, "error": "unauthorized"})
            return
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode() if n else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}
        if self.path == "/api/ai/validate":
            provider = str(data.get("provider", "")).strip().lower()
            token = str(data.get("token", "")).strip()
            if not provider or not token:
                self._json(400, {"ok": False, "error": "missing fields"})
                return
            import os
            os.environ[f"{provider.upper()}_API_KEY"] = token
            from utils.ai import _call
            try:
                _call(provider, "Reply with one word: HOLD")
                from utils.ai import save_ai_token
                save_ai_token(provider, token)
                save_audit("ai.validate", provider)
                self._json(200, {"ok": True})
            except Exception as e:
                self._json(400, {"ok": False, "error": str(e)})
            return
        if self.path == "/api/ai/providers":
            provs = [p.strip() for p in (get_config("AI_PROVIDERS", settings.AI_PROVIDERS) or "").split(",") if p.strip()]
            self._json(200, {"providers": provs})
            return
        if self.path == "/api/ai/providers/add":
            name = str(data.get("name","")).strip().lower()
            if not name:
                self._json(400, {"ok": False, "error": "missing name"}); return
            provs = [p.strip() for p in (get_config("AI_PROVIDERS", settings.AI_PROVIDERS) or "").split(",") if p.strip()]
            if name not in provs:
                provs.append(name)
            set_config("AI_PROVIDERS", ",".join(provs))
            self._json(200, {"ok": True, "providers": provs})
            return
        if self.path == "/api/ai/providers/remove":
            name = str(data.get("name","")).strip().lower()
            provs = [p.strip() for p in (get_config("AI_PROVIDERS", settings.AI_PROVIDERS) or "").split(",") if p.strip()]
            provs = [p for p in provs if p != name]
            set_config("AI_PROVIDERS", ",".join(provs))
            self._json(200, {"ok": True, "providers": provs})
            return
        if self.path == "/api/config":
            key = str(data.get("key", ""))
            val = str(data.get("value", ""))
            if key:
                set_config(key, val)
                save_audit("config.update", f"{key}={val}")
                self._json(200, {"ok": True})
            else:
                self._json(400, {"ok": False, "error": "missing key"})
            return
        self._json(404, {"ok": False})

    def log_message(self, *args):
        pass


def start_api_server(port=8080):
    class ReuseHTTP(ThreadingHTTPServer):
        allow_reuse_address = True
    httpd = ReuseHTTP(("0.0.0.0", port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd