import urllib.request, urllib.parse, json, threading, time
from config.settings import settings

def send_telegram(text):
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    target = settings.TELEGRAM_CHANNEL_ID or settings.TELEGRAM_USER_ID
    if not target:
        return
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": target, "text": text}).encode()
    try:
        urllib.request.urlopen(urllib.request.Request(url, data=data))
    except Exception as e:
        print("Telegram notify error:", e)

def _api(method, params=None):
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"ok": False}
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=35) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def poll_updates():
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    offset = 0
    while True:
        res = _api("getUpdates", {"timeout": 30, "offset": offset})
        if not res.get("ok"):
            time.sleep(5)
            continue
        for upd in res.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message") or upd.get("edited_message")
            if not msg:
                continue
            chat_id = msg["chat"]["id"]
            text = (msg.get("text") or "").strip()
            reply = None
            if text.startswith("/start"):
                reply = ("Bot trading aktif.\nCommands:\n/status\n/pause\n/resume")
            elif text.startswith("/status"):
                from utils.db import get_config
                reply = (f"Bot Type: {settings.BOT_TYPE}\n"
                         f"Paused: {get_config('BOT_PAUSED','false')}\n"
                         f"Risk: {get_config('RISK_LEVEL','MEDIUM')}")
            elif text.startswith("/pause"):
                from utils.db import set_config
                set_config("BOT_PAUSED", "true")
                reply = "Trading paused."
            elif text.startswith("/resume"):
                from utils.db import set_config
                set_config("BOT_PAUSED", "false")
                reply = "Trading resumed."
            else:
                reply = "Unknown command. /start for help."
            if reply:
                data = urllib.parse.urlencode({"chat_id": chat_id, "text": reply}).encode()
                try:
                    urllib.request.urlopen(urllib.request.Request(
                        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                        data=data))
                except Exception:
                    pass
        time.sleep(1)

def start_telegram_polling():
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    t = threading.Thread(target=poll_updates, daemon=True)
    t.start()