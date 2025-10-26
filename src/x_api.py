import time
import requests
from typing import Dict, List, Optional, Tuple
from .config import X_BEARER_TOKEN

BASE = "https://api.x.com/2"

def _headers()->Dict[str,str]:
    if not X_BEARER_TOKEN:
        raise RuntimeError("X_BEARER_TOKEN не задан в .env")
    return {"Authorization": f"Bearer {X_BEARER_TOKEN}"}

def get_user_by_username(username:str)->Optional[dict]:
    r = requests.get(f"{BASE}/users/by/username/{username}", headers=_headers(), timeout=30)
    if r.status_code != 200:
        return None
    return r.json().get("data")

def get_following(user_id:str, limit:int=1000)->List[dict]:
    """Возвращает список аккаунтов, на которых пользователь подписан."""
    out = []
    params = {"max_results": 1000}
    next_token = None
    while True:
        if next_token:
            params["pagination_token"] = next_token
        r = requests.get(f"{BASE}/users/{user_id}/following", headers=_headers(), params=params, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"X following error {r.status_code}: {r.text}")
        j = r.json()
        out.extend(j.get("data", []))
        next_token = j.get("meta", {}).get("next_token")
        if not next_token or len(out) >= limit:
            break
        time.sleep(1.0)
    return out[:limit]

def get_user_tweets(user_id:str, since_id:Optional[str], max_results:int=5,
                    exclude_retweets:bool=True, exclude_replies:bool=True)->List[dict]:
    params = {
        "max_results": max(5, min(100, max_results)),
        "tweet.fields": "created_at,entities,lang,author_id,public_metrics",
        "exclude": ",".join([p for p in ["retweets" if exclude_retweets else None,
                                         "replies" if exclude_replies else None] if p])
    }
    if since_id:
        params["since_id"] = since_id
    r = requests.get(f"{BASE}/users/{user_id}/tweets", headers=_headers(), params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"X user tweets error {r.status_code}: {r.text}")
    return r.json().get("data", [])
