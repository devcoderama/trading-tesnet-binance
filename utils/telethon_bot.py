import os
from config.settings import settings

try:
    from telethon import TelegramClient, events, Button
    HAS_TELETHON = True
except Exception:
    HAS_TELETHON = False

async def _run():
    api_id = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    if not api_id or not api_hash or not settings.TELEGRAM_BOT_TOKEN:
        return
    client = TelegramClient("hermes_bot", api_id, api_hash)
    await client.start(bot_token=settings.TELEGRAM_BOT_TOKEN)

    @client.on(events.NewMessage(pattern="/start"))
    async def handler(event):
        await event.respond("Bot trading aktif.", buttons=[
            [Button.inline("Status", b"status"), Button.inline("Pause", b"pause")],
            [Button.inline("Resume", b"resume"), Button.inline("Back", b"back")],
        ])

    @client.on(events.CallbackQuery)
    async def cb(event):
        data = event.data.decode()
        if data == "status":
            from utils.db import get_config
            await event.edit(f"Paused: {get_config('BOT_PAUSED','false')}\nRisk: {get_config('RISK_LEVEL','MEDIUM')}", buttons=[[Button.inline("Back", b"back")]])
        elif data == "pause":
            from utils.db import set_config
            set_config("BOT_PAUSED", "true")
            await event.answer("Paused")
        elif data == "resume":
            from utils.db import set_config
            set_config("BOT_PAUSED", "false")
            await event.answer("Resumed")
        elif data == "back":
            await event.edit("Main menu", buttons=[[Button.inline("Status", b"status")], [Button.inline("Pause", b"pause")], [Button.inline("Resume", b"resume")]])

    await client.run_until_disconnected()

def start_telethon():
    if not HAS_TELETHON:
        return False
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not (api_id and api_hash):
        return False
    import threading, asyncio
    def runner():
        asyncio.run(_run())
    threading.Thread(target=runner, daemon=True).start()
    return True