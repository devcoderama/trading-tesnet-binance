"""Telethon menu helpers (gradual implementation)."""

def main_menu_buttons():
    from telethon import Button
    import os
    btns = [
        [Button.inline("Trading", b"menu_trading"), Button.inline("AI", b"menu_ai")],
        [Button.inline("Status Bot", b"menu_status")],
    ]
    url = os.getenv("MINIAPP_URL")
    if url:
        btns.append([Button.url("Mini App", url)])
    return btns

def trading_menu_buttons():
    from telethon import Button
    return [
        [Button.inline("Timeframe", b"trading_timeframe"), Button.inline("Symbols", b"trading_symbols")],
        [Button.inline("Symbol Mode", b"trading_symbolmode"), Button.inline("Risk", b"trading_risk")],
        [Button.inline("Back", b"menu_back")],
    ]