import os
from dotenv import load_dotenv

load_dotenv()

def as_bool(v:str, default=False)->bool:
    if v is None:
        return default
    return v.strip().lower() in ("1","true","yes","y","on")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN","").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID","").strip()

X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN","").strip()
X_USER_ID = os.getenv("X_USER_ID","").strip()

USE_STATIC_USERNAMES = as_bool(os.getenv("USE_STATIC_USERNAMES","false"))
STATIC_USERNAMES = [u.strip().lstrip("@") for u in os.getenv("STATIC_USERNAMES","").split(",") if u.strip()]

KEYWORDS = [k.strip() for k in os.getenv("KEYWORDS","").split(",") if k.strip()]
EXCLUDE_RETWEETS = as_bool(os.getenv("EXCLUDE_RETWEETS","true"))
EXCLUDE_REPLIES = as_bool(os.getenv("EXCLUDE_REPLIES","true"))

POLL_SECONDS = int(os.getenv("POLL_SECONDS","45"))
MAX_TWEETS_PER_USER = max(1, int(os.getenv("MAX_TWEETS_PER_USER","5")))

STATE_FILE = os.getenv("STATE_FILE","data/state.json")
LOG_LEVEL = os.getenv("LOG_LEVEL","INFO").upper()
