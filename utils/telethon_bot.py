import os

try:
    from telethon import TelegramClient, events, Button
    HAS_TELETHON = True
except Exception:
    HAS_TELETHON = False

_pending_ai_users = set()
_pending_ai_delete = set()

async def _run():
    api_id = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    from config.settings import settings
    if not api_id or not api_hash or not settings.TELEGRAM_BOT_TOKEN:
        return
    client = TelegramClient("hermes_bot", api_id, api_hash)
    await client.start(bot_token=settings.TELEGRAM_BOT_TOKEN)

    @client.on(events.NewMessage(pattern="/start"))
    async def handler(event):
        from config.settings import settings
        from exchange.binance_client import BinanceClient
        from utils.telethon_menu import main_menu_buttons, trading_menu_buttons
        from utils.db import get_config
        cli = BinanceClient().get_client()
        balance = float(cli.get_asset_balance(asset=settings.QUOTE_ASSET)["free"])
        uname = event.sender.username or "-"
        uid = event.sender_id
        text = (
            "<blockquote>"
            f"Bot Type: {settings.BOT_TYPE}\n"
            "Exchange: Binance\n"
            f"Symbols: {settings.SYMBOL or settings.SYMBOLS or '-'}\n"
            f"Profit Currency: {settings.QUOTE_ASSET}\n"
            f"Risk Level: {get_config('RISK_LEVEL', settings.RISK_LEVEL)}\n"
            f"Interval: {settings.INTERVAL}\n"
            f"Dry Run: {settings.DRY_RUN}\n"
            f"Testnet: {settings.TESTNET}\n"
            f"Indicators: {'AI multi-provider' if settings.USE_AI else 'SMA crossover'}\n"
            f"AI Mode: {'ON' if settings.USE_AI else 'OFF'}\n"
            f"AI Providers: {settings.AI_PROVIDERS if settings.USE_AI else '-'}\n"
            f"Telegram Username: @{uname}\n"
            f"Telegram UserID: {uid}\n"
            f"Balance: {balance} {settings.QUOTE_ASSET}"
            "</blockquote>"
        )
        await event.respond(text, parse_mode='html', buttons=main_menu_buttons())

    @client.on(events.CallbackQuery)
    async def cb(event):
        data = event.data.decode()
        if data == "trading_timeframe":
            await event.edit("Set Timeframe: (edit .env INTERVAL). Back ->", buttons=[[Button.inline("Back", b"menu_trading")]])
            return
        if data == "trading_symbols":
            await event.edit("Symbols manage: set in .env SYMBOL/SYMBOLS or use auto. Back ->", buttons=[[Button.inline("Back", b"menu_trading")]])
            return
        if data == "trading_risk":
            await event.edit("Set Risk: set RISK_LEVEL in settings/db. Back ->", buttons=[[Button.inline("Back", b"menu_trading")]])
            return
        if data == "menu_trading":
            await event.edit("Trading Menu", buttons=trading_menu_buttons())
            return
        if data == "menu_back":
            from utils.telethon_menu import main_menu_buttons
            await event.edit("Main Menu", buttons=main_menu_buttons())
            return
        if data == "menu_ai":
            await event.edit("AI Menu", buttons=[
                [Button.inline("Save Token", b"ai_save"), Button.inline("Edit", b"ai_edit")],
                [Button.inline("Add", b"ai_add"), Button.inline("Delete", b"ai_delete")],
                [Button.inline("Single/Multi", b"ai_mode"), Button.inline("Back", b"menu_back")],
            ])
            return
        if data == "ai_delete":
            _pending_ai_delete.add(event.sender_id)
            await event.edit("Kirim provider untuk dihapus: gemini (hanya nama provider)", buttons=[[Button.inline("Back", b"menu_ai")]])
            return
        if data == "ai_save":
            _pending_ai_users.add(event.sender_id)
            await event.edit("Kirim token dengan format: <provider> <token>\nContoh: gemini ABC123", buttons=[[Button.inline("Back", b"menu_ai")]])
            return
        if data == "menu_status":
            await event.edit("Status Bot", buttons=[[Button.inline("Start", b"resume"), Button.inline("Stop", b"pause"), Button.inline("Back", b"menu_back")]])
            return
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

    @client.on(events.NewMessage)
    async def _capture_token(event):
        if event.sender_id in _pending_ai_delete:
            provider = (event.message.text or "").strip().lower()
            from utils.ai import delete_ai_token
            delete_ai_token(provider)
            _pending_ai_delete.discard(event.sender_id)
            await event.reply(f"Token {provider} dihapus.")
            return
        if event.sender_id not in _pending_ai_users:
            return
        parts = (event.message.text or "").split(maxsplit=1)
        if len(parts) != 2:
            await event.reply("Format salah. Gunakan: <provider> <token>")
            return
        provider, token = parts[0].strip().lower(), parts[1].strip()
        from utils.ai import save_ai_token
        save_ai_token(provider, token)
        _pending_ai_users.discard(event.sender_id)
        await event.reply(f"Token {provider} tersimpan.")

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