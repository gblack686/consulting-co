"""
Telegram notifications for GBAutomation.
Sends messages to Greg's Telegram via bot.

Secret: gbautomation/telegram/bot
  { "bot_token": "...", "chat_id": "..." }
"""
import json
import urllib.request
import urllib.parse

SECRET_ID = "gbautomation/telegram/bot"


def _get_config() -> dict:
    from .secret_cache import get_secret
    return get_secret(SECRET_ID)


def send(message: str, parse_mode: str = "HTML") -> dict:
    """Send a message to Greg's Telegram. Returns API response dict."""
    cfg = _get_config()
    url = f"https://api.telegram.org/bot{cfg['bot_token']}/sendMessage"
    payload = json.dumps({
        "chat_id": cfg["chat_id"],
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())
