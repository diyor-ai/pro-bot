import logging
import time
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from utils import is_available, next_order_id, parse_price
from config import (
    SCOPES, CREDENTIALS_FILE, SHEET_NAME,
    ORDERS_SHEET, USERS_SHEET, CACHE_TTL
)

logger = logging.getLogger(__name__)
_cache = {}

def get_credentials():
    try:
        creds_json = os.getenv("GOOGLE_CREDENTIALS")
        if creds_json:
            return Credentials.from_service_account_info(
                json.loads(creds_json), scopes=SCOPES
            )
    except Exception:
        logger.exception("GOOGLE_CREDENTIALS env is invalid, falling back to %s", CREDENTIALS_FILE)
    return Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )

def get_products(category=None):
    now = time.time()
    cache_key = "products_all" if category is None else f"products_{category}"

    if cache_key in _cache:
        if (now - _cache[cache_key]["last_updated"]) < CACHE_TTL:
            return _cache[cache_key]["data"]

    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        all_products = sheet.get_all_records()

        available = [p for p in all_products if is_available(p.get("Mavjud"))]

        if category:
            available = [p for p in available
                        if str(p.get("Kategoriya", "")).lower() == category.lower()]

        _cache[cache_key] = {"data": available, "last_updated": now}
        return available
    except Exception:
        logger.exception("Sheets error in get_products")
        return []

def get_categories():
    products = get_products()
    categories = sorted(set(
        str(p.get("Kategoriya", "Boshqa")).strip()
        for p in products
        if p.get("Kategoriya")
    ))
    return categories if categories else ["Boshqa"]

def get_product_by_id(product_id):
    for p in get_products():
        if str(p.get("ID")) == str(product_id):
            return p
    return None

def save_order(order: dict):
    """Buyurtmani saqlaydi va uning ID sini qaytaradi (xatoda None)."""
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open(SHEET_NAME)

        try:
            ws = spreadsheet.worksheet(ORDERS_SHEET)
        except gspread.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(ORDERS_SHEET, rows=1000, cols=12)
            ws.append_row([
                "ID", "Sana", "Mahsulot", "Narx", "Kategoriya",
                "Ism", "Telefon", "Manzil", "Til", "Status", "User_ID"
            ])

        next_id = next_order_id(ws.col_values(1)[1:])

        ws.append_row([
            next_id,
            order["sana"],
            order["mahsulot"],
            order["narx"],
            order.get("kategoriya", ""),
            order["ism"],
            order["telefon"],
            order["manzil"],
            order.get("til", "uz"),
            "Yangi",
            order.get("user_id", "")
        ])

        update_user(spreadsheet, order)
        return next_id
    except Exception:
        logger.exception("save_order failed")
        return None

def update_user(spreadsheet, order):
    try:
        try:
            ws = spreadsheet.worksheet(USERS_SHEET)
        except gspread.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(USERS_SHEET, rows=1000, cols=7)
            ws.append_row([
                "User_ID", "Ism", "Telefon", "Til",
                "Birinchi_sana", "Oxirgi_sana", "Buyurtmalar_soni"
            ])

        records = ws.get_all_records()
        user_id = order.get("user_id", "")
        now = order["sana"]

        for i, r in enumerate(records):
            if str(r.get("User_ID")) == str(user_id):
                ws.update_cell(i + 2, 6, now)
                count = int(r.get("Buyurtmalar_soni", 0)) + 1
                ws.update_cell(i + 2, 7, count)
                return

        ws.append_row([
            user_id,
            order["ism"],
            order["telefon"],
            order.get("til", "uz"),
            now,
            now,
            1
        ])
    except Exception:
        logger.exception("update_user failed for order of user %s", order.get("user_id"))

def get_orders(status=None, limit=20):
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open(SHEET_NAME)
        ws = spreadsheet.worksheet(ORDERS_SHEET)

        records = ws.get_all_records()
        if status:
            records = [r for r in records
                      if str(r.get("Status", "")).lower() == status.lower()]

        return records[:limit]
    except Exception:
        logger.exception("get_orders failed")
        return []

def update_order_status(order_id, new_status) -> bool:
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open(SHEET_NAME)
        ws = spreadsheet.worksheet(ORDERS_SHEET)

        records = ws.get_all_values()
        for i, row in enumerate(records[1:], start=2):
            if str(row[0]) == str(order_id):
                ws.update_cell(i, 10, new_status)
                return True
        logger.warning("update_order_status: order %s not found", order_id)
        return False
    except Exception:
        logger.exception("update_order_status failed for order %s", order_id)
        return False

def get_stats() -> dict:
    try:
        import datetime
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open(SHEET_NAME)
        ws = spreadsheet.worksheet(ORDERS_SHEET)

        records = ws.get_all_records()
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        return {
            "total": len(records),
            "today": len([r for r in records if str(r.get("Sana", "")).startswith(today)]),
            "new": len([r for r in records if r.get("Status", "") == "Yangi"]),
            "revenue": sum(parse_price(r.get("Narx", 0)) for r in records)
        }
    except Exception:
        logger.exception("get_stats failed")
        return {}

def get_user_ids():
    """Unique Telegram User_IDs from the Users sheet (for broadcast)."""
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        ws = client.open(SHEET_NAME).worksheet(USERS_SHEET)
        ids = []
        for v in ws.col_values(1)[1:]:
            v = str(v).strip()
            if v.lstrip("-").isdigit() and int(v) not in ids:
                ids.append(int(v))
        return ids
    except Exception:
        logger.exception("get_user_ids failed")
        return None