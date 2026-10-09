# Pro Bot

A Telegram shop bot (Uzbek / Russian / English) that uses a Google Spreadsheet as its database.

## Features

- Language selection per user (`uz`, `ru`, `en`)
- Product catalog by category, with product photos
- Fuzzy product search (rapidfuzz)
- Order flow: name → phone (Uzbek `+998` format, or share contact) → address → confirmation
- Orders are saved to Google Sheets; every new order is sent to the admin chat with status buttons
- Admin panel (`/admin`): new orders, statistics, status updates, broadcast to all customers

## Requirements

- Python 3.11 or newer (the Docker image uses 3.11)
- A bot token from [@BotFather](https://t.me/BotFather)
- A Google Cloud service account with the Sheets and Drive APIs enabled
- A Google Spreadsheet shared (editor access) with the service account's `client_email`

## Setup

```bash
git clone git@github.com:diyor-ai/pro-bot.git
cd pro-bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env
```

Put the service account key in `credentials.json` in the project root, or set it as a single-line JSON string in the `GOOGLE_CREDENTIALS` environment variable (takes priority). Both `.env` and `credentials.json` are git-ignored and docker-ignored; never commit them.

## Configuration (environment variables)

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_TOKEN` | yes | – | Bot token |
| `ADMIN_CHAT_ID` | yes | – | Chat that receives new-order notifications |
| `ADMIN_IDS` | yes | – | Comma-separated Telegram user IDs allowed to use `/admin` and the status buttons |
| `SHOP_NAME` | no | `Pro Shop` | Name shown in the bot |
| `SHEET_NAME` | no | `Mahsulotlar` | Name of the Google **Spreadsheet** (the file) |
| `CACHE_TTL` | no | `60` | Product cache lifetime in seconds |
| `FUZZY_THRESHOLD` | no | `65` | Minimum search score (0–100) |
| `GOOGLE_CREDENTIALS` | no | – | Service account JSON; otherwise `credentials.json` is used |

## Spreadsheet layout

The **first worksheet** of the spreadsheet is the product list. The `Buyurtmalar` and `Users` worksheets are created automatically on the first order.

**Products (first worksheet)**

| ID | Nomi | Narxi | Kategoriya | Tavsif | Rasm_URL | Mavjud |
|---|---|---|---|---|---|---|

- `Narxi`: number; spaces or `,` as thousands separators are accepted.
- `Mavjud`: `TRUE`/`YES`/`HA` or a number greater than 0 means available; `FALSE`/`NO`/`0` hides the product; an empty cell counts as available.
- `Rasm_URL`: optional public image URL.

**Buyurtmalar (orders)**: `ID, Sana, Mahsulot, Narx, Kategoriya, Ism, Telefon, Manzil, Til, Status, User_ID`. Status is `Yangi`, `Jarayonda`, `Yo'lda` or `Yetkazildi`.

**Users**: `User_ID, Ism, Telefon, Til, Birinchi_sana, Oxirgi_sana, Buyurtmalar_soni`. Broadcast sends to every `User_ID` in this sheet, so only customers who have ordered at least once receive it.

## Running

```bash
python bot.py
```

Docker:

```bash
docker build -t pro-bot .
docker run -d --env-file .env -v "$PWD/credentials.json:/app/credentials.json:ro" pro-bot
```

(`credentials.json` is not baked into the image; mount it or use `GOOGLE_CREDENTIALS`.) `Procfile` defines a `worker` process for Heroku-style platforms.

## Commands

- `/start`: choose a language and open the menu
- `/admin`: admin panel (users listed in `ADMIN_IDS` only)

Broadcast asks for the message text, shows a preview, and sends only after you confirm. It reports how many messages were sent and how many failed (for example, users who blocked the bot).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests cover the pure helpers (phone validation, price parsing, HTML escaping, `Mavjud` parsing, order IDs, fuzzy search) and the broadcast loop. They use no real Telegram or Google calls. For a manual end-to-end check see [docs/TESTING.md](docs/TESTING.md).

## Project structure

```
bot.py            handlers, admin panel, broadcast, entry point
config.py         environment and constants
sheets.py         Google Sheets access (products cache, orders, users, stats)
keyboards.py      inline / reply keyboards
i18n.py           locale loading and translation lookup
utils.py          pure helpers (phone, price, escaping, search, Mavjud, order ID)
locales/          uz.json, ru.json, en.json
tests/            pytest suite
```

## Known limitations

- **State is in memory.** Language choice and an order in progress are lost when the bot restarts; users just run `/start` again.
- **Google Sheets is the database.** It is subject to the API quota (about 60 reads/minute per user by default), each save takes several API calls, and calls are synchronous, so heavy traffic will slow the bot. Products are cached for `CACHE_TTL` seconds, so sheet edits can take that long to show.
- **Order IDs are max+1.** Two orders saved at the very same moment could get the same ID.
- **Polling, single instance.** The bot uses long polling; running two instances with the same token causes `Conflict` errors.
- **Broadcast reaches only customers in `Users`** (people who completed an order), and sends sequentially, so large lists take time.
- Admin texts and status labels are Uzbek only; the price currency is fixed to "so'm".

## License

MIT, see [LICENSE](LICENSE).
