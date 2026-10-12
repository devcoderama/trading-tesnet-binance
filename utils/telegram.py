import urllib.request, urllib.parse, json
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
