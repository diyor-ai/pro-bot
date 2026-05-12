import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
SHOP_NAME = os.getenv("SHOP_NAME", "Pro Shop")
SHEET_NAME = os.getenv("SHEET_NAME", "Mahsulotlar")

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "credentials.json"
ORDERS_SHEET = "Buyurtmalar"
USERS_SHEET = "Users"
LOCALES_DIR = "locales"
CACHE_TTL = 60
FUZZY_THRESHOLD = 65