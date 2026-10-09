import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
SHOP_NAME = os.getenv("SHOP_NAME", "Pro Shop")
ADMIN_LANG = os.getenv("ADMIN_LANG", "uz").strip().lower() or "uz"  # validated against locales in i18n
SHEET_NAME = os.getenv("SHEET_NAME", "Mahsulotlar")

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "credentials.json"
ORDERS_SHEET = "Buyurtmalar"
USERS_SHEET = "Users"
LOCALES_DIR = "locales"
CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "65"))
DEFAULT_PRODUCT_EMOJI = "\U0001f6cd"  # 🛍


def parse_category_emoji(raw):
    """Parse "Krossovka=👟,Aksessuar=👜" into {"krossovka": "👟", "aksessuar": "👜"}."""
    result = {}
    for part in (raw or "").split(","):
        name, sep, emoji = part.partition("=")
        if sep and name.strip() and emoji.strip():
            result[name.strip().lower()] = emoji.strip()
    return result


# Emoji shown next to a product, by category (case-insensitive). Add more here or
# override/extend with the CATEGORY_EMOJI env var; other categories get the default.
CATEGORY_EMOJI = {
    "krossovka": "\U0001f45f",  # 👟
    "aksessuar": "\U0001f45c",  # 👜
    **parse_category_emoji(os.getenv("CATEGORY_EMOJI", "")),
}
PERSISTENCE_FILE = os.getenv("PERSISTENCE_FILE", "data/bot_data.pickle")
BROADCAST_DELAY = 0.05  # seconds between messages (Telegram limit is ~30/s)