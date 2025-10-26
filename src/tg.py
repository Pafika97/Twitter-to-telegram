import html
import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def _escape_html(text:str)->str:
    return html.escape(text, quote=False)

def send_message(text:str, disable_web_page_preview:bool=True) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID не заданы в .env")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": disable_web_page_preview
    }
    r = requests.post(url, json=payload, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Telegram sendMessage error {r.status_code}: {r.text}")
