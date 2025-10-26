import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from .config import (
    KEYWORDS, EXCLUDE_RETWEETS, EXCLUDE_REPLIES, POLL_SECONDS, MAX_TWEETS_PER_USER,
    USE_STATIC_USERNAMES, STATIC_USERNAMES, X_USER_ID, STATE_FILE, LOG_LEVEL
)
from . import x_api
from .tg import send_message
from .util import load_state, save_state

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format="%(asctime)s %(levelname)s: %(message)s")

def compile_keyword_regex(keywords:List[str])->re.Pattern:
    parts = []
    for k in keywords:
        k = re.escape(k)
        parts.append(k)
    if not parts:
        # если ключевые слова не заданы — матчить всё
        return re.compile(r".+", re.IGNORECASE | re.DOTALL)
    return re.compile(r"(" + "|".join(parts) + r")", re.IGNORECASE | re.DOTALL)

async def resolve_user_ids()->List[Tuple[str,str]]:
    """Возвращает пары (user_id, username) источников для мониторинга."""
    users: List[Tuple[str,str]] = []
    if USE_STATIC_USERNAMES:
        for uname in STATIC_USERNAMES:
            info = x_api.get_user_by_username(uname)
            if info:
                users.append((info["id"], info["username"]))
            else:
                logging.warning("Не удалось получить пользователя по username: @%s", uname)
        return users

    if not X_USER_ID:
        raise RuntimeError("X_USER_ID не задан в .env (нужно для получения списка подписок)")
    following = x_api.get_following(X_USER_ID, limit=10_000)
    for u in following:
        users.append((u["id"], u["username"]))
    logging.info("Загружено подписок: %d", len(users))
    return users

def build_tweet_url(username:str, tweet_id:str)->str:
    return f"https://x.com/{username}/status/{tweet_id}"

def format_telegram_message(username:str, name:str, text:str, url:str, created_at_iso:str)->str:
    created = created_at_iso.replace("T"," ").replace("Z"," UTC")
    # Экранируем HTML спецсимволы
    import html
    return (
        f"<b>Новый твит по ключевым словам</b>\n"
        f"Автор: <b>@{html.escape(username)}</b> ({html.escape(name)})\n"
        f"Время: {html.escape(created)}\n\n"
        f"{html.escape(text)}\n\n"
        f"{html.escape(url)}"
    )

async def poll():
    kw_re = compile_keyword_regex(KEYWORDS)
    state: Dict[str,str] = load_state(STATE_FILE)  # {user_id: last_tweet_id}
    users = await resolve_user_ids()
    # предварительно получим карту id->username для форматирования ссылок
    id_to_username = {uid: uname for uid, uname in users}

    while True:
        try:
            for uid, uname in users:
                since_id = state.get(uid)
                tweets = x_api.get_user_tweets(uid, since_id=since_id,
                                               max_results=MAX_TWEETS_PER_USER,
                                               exclude_retweets=EXCLUDE_RETWEETS,
                                               exclude_replies=EXCLUDE_REPLIES)
                if not tweets:
                    continue
                # X возвращает от новых к старым. Пройдем от старых к новым, чтобы порядок в чате был хронологический
                tweets_sorted = sorted(tweets, key=lambda t: int(t["id"]))
                for t in tweets_sorted:
                    text = t.get("text","")
                    if not kw_re.search(text):
                        continue
                    url = build_tweet_url(uname, t["id"])
                    # Вытянем имя автора (display name) через ленивая подгрузка (если доступно)
                    # чтобы не бить доп. запросом, используем username как name по умолчанию
                    name = uname
                    created = t.get("created_at","")
                    msg = format_telegram_message(uname, name, text, url, created)
                    send_message(msg)
                    logging.info("Отправлено в Telegram: %s", url)
                # обновим since_id: последний просмотренный твит
                max_id = max(int(t["id"]) for t in tweets_sorted)
                state[uid] = str(max_id)
                save_state(STATE_FILE, state)
        except Exception as e:
            logging.exception("Ошибка в цикле опроса: %s", e)

        await asyncio.sleep(POLL_SECONDS)

def main():
    logging.info("Запуск Twitter->Telegram фильтра. Ключевые слова: %s", ", ".join(KEYWORDS) if KEYWORDS else "(все)")
    asyncio.run(poll())

if __name__ == "__main__":
    main()
