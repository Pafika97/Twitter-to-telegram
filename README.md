# Twitter(X) → Telegram: фильтр по словам от аккаунтов, на которых вы подписаны

Эта программа оповещает в Telegram, когда **любой аккаунт, на которого вы подписаны в X (Twitter)**,
публикует твит, содержащий заданные ключевые слова (например: *биткоин, bitcoin, btc*).

## Как это работает
- Скрипт раз в N секунд получает список ваших подписок (или использует статический список юзернеймов — на ваш выбор).
- Для каждой подписки забирает последние твиты и фильтрует по ключевым словам.
- Совпадения отправляются в выбранный Telegram‑чат (ботом).

> ⚠️ Нужен доступ к **X API v2** (учетные данные приложения) и токен вашего Telegram‑бота.
> В X могут действовать тарифные ограничения/права. Если эндпоинт «following» недоступен в вашем плане,
> используйте статический список юзернеймов (см. `.env`).

---

## Быстрый запуск (Windows/Mac/Linux)

1) Установите Python 3.10+
2) Склонируйте/распакуйте папку `twitter_to_telegram`
3) В консоли:
```bash
cd twitter_to_telegram
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```
4) Заполните `.env` (см. ниже).
5) Запуск:
```bash
python src/twitter_to_telegram.py
```

---

## Настройка `.env`

Откройте файл `.env` и задайте значения:

```
# --- Telegram ---
TELEGRAM_BOT_TOKEN=123456789:AA...            # токен вашего Telegram-бота
TELEGRAM_CHAT_ID=-1001234567890               # id чата/канала/группы (можно и личный id)

# --- X (Twitter) ---
X_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAA...        # Bearer Token приложения X API v2
X_USER_ID=1234567890123456789                 # id вашего аккаунта X (не username)

# --- Режимы источника аккаунтов ---
USE_STATIC_USERNAMES=false                    # true/false: использовать ли статический список вместо ваших подписок
STATIC_USERNAMES=elonmusk,binance,...         # список юзернеймов через запятую (если USE_STATIC_USERNAMES=true)

# --- Фильтр ---
KEYWORDS=биткоин,bitcoin,btc                  # ключевые слова через запятую (регистр не важен)
EXCLUDE_RETWEETS=true                         # исключать ретвиты
EXCLUDE_REPLIES=true                          # исключать реплаи

# --- Параметры опроса ---
POLL_SECONDS=45                               # как часто опрашивать (в секундах)
MAX_TWEETS_PER_USER=5                         # сколько последних твитов проверять по каждому аккаунту за цикл

# --- Прочее ---
STATE_FILE=data/state.json                    # файл состояния (последние обработанные id твитов по каждому аккаунту)
LOG_LEVEL=INFO                                # DEBUG/INFO/WARN/ERROR
```

### Как получить TELEGRAM_CHAT_ID
- Добавьте бота в ваш чат/канал как админа (если канал/группа).
- Напишите в чат сообщение.
- Узнайте ID: пересланное боту @RawDataBot покажет chat_id, либо используйте свой инструмент.

### Как получить X_USER_ID
- Узнайте свой username, затем выполните:
```bash
python -m pip install requests
python - << 'PY'
import os, requests
bearer="ВАШ_BEARER_TOKEN"
username="ВАШ_USERNAME_БЕЗ_@"
r=requests.get(f"https://api.x.com/2/users/by/username/{username}",
               headers={"Authorization": f"Bearer {bearer}"})
print(r.status_code, r.text)
PY
```
- В ответе будет поле `id` — это ваш `X_USER_ID`.

> Если эндпоинты X недоступны на вашем плане, переключитесь на `USE_STATIC_USERNAMES=true` и перечислите нужные аккаунты в `STATIC_USERNAMES`.

---

## Автозапуск

### Windows (Task Scheduler)
- Импортируйте планировщик из примера `run.bat` или создайте задачу, запускающую `run.bat` при входе пользователя.

### Linux (systemd)
1) Отредактируйте путь в `deploy/twitter2tg.service`
2) Установите сервис:
```bash
sudo cp deploy/twitter2tg.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now twitter2tg
```

---

## Ограничения и советы
- Следите за лимитами X API (частота запросов).
- При большом количестве подписок увеличьте `POLL_SECONDS` или включите статический список.
- Ключевые слова ищутся в тексте твита (включая кириллицу). Можно задавать словоформы через запятую.

Удачи!
