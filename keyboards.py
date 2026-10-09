from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from config import ADMIN_IDS

def _to_int(value):
    digits = "".join(ch for ch in str(value).split(".")[0] if ch.isdigit())
    return int(digits) if digits else 0

def lang_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\U0001f1fa\U0001f1ff O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton("\U0001f1f7\U0001f1fa Русский", callback_data="lang_ru"),
        InlineKeyboardButton("\U0001f1ec\U0001f1e7 English", callback_data="lang_en"),
    ]])

def main_menu_keyboard(context):
    from config import LOCALES_DIR
    import json
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        all_p = l.get("all_products", "\U0001f4e6 Products")
        srch = l.get("search", "\U0001f50d Search")
    except Exception:
        all_p = "\U0001f4e6 Products"
        srch = "\U0001f50d Search"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(all_p, callback_data="show_products")],
        [InlineKeyboardButton(srch, callback_data="search")],
    ])

def back_keyboard(context):
    from config import LOCALES_DIR
    import json
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        back = l.get("back", "\U0001f519 Back")
    except Exception:
        back = "\U0001f519 Back"

    return InlineKeyboardMarkup([[
        InlineKeyboardButton(back, callback_data="back")
    ]])

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f4cb Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton("\U0001f4ca Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("\U0001f4e2 Broadcast", callback_data="admin_broadcast")],
    ])

def category_keyboard(context, categories):
    from config import LOCALES_DIR
    import json
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        back = l.get("back", "\U0001f519 Back")
    except Exception:
        back = "\U0001f519 Back"

    buttons = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}") for cat in categories]]
    buttons.append([InlineKeyboardButton(back, callback_data="back")])
    return InlineKeyboardMarkup(buttons)

def products_keyboard(context, products):
    from config import LOCALES_DIR
    import json
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        back = l.get("back", "\U0001f519 Back")
    except Exception:
        back = "\U0001f519 Back"

    buttons = [
        [InlineKeyboardButton(
            f"{p['Nomi']} \U0001f4b0 {_to_int(p['Narxi']):,}".replace(",", " "),
            callback_data=f"product_{p['ID']}"
        )] for p in products
    ]
    buttons.append([InlineKeyboardButton(back, callback_data="back")])
    return InlineKeyboardMarkup(buttons)

def product_action_keyboard(context, product_id):
    from config import LOCALES_DIR
    import json
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        yes = l.get("yes", "✅ Yes")
        no = l.get("no", "❌ No")
    except Exception:
        yes = "✅ Yes"
        no = "❌ No"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(yes, callback_data=f"buy_{product_id}"),
         InlineKeyboardButton(no, callback_data="back")]
    ])

def confirm_keyboard(context):
    from config import LOCALES_DIR
    import json
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        confirm = l.get("confirm_btn", "✅ Confirm")
        cancel = l.get("cancel_btn", "❌ Cancel")
    except Exception:
        confirm = "✅ Confirm"
        cancel = "❌ Cancel"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(confirm, callback_data="confirm_order")],
        [InlineKeyboardButton(cancel, callback_data="cancel_order")]
    ])

def order_status_keyboard(order_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f525 Jarayonda", callback_data=f"status_{order_id}_processing")],
        [InlineKeyboardButton("\U0001f6a6 Yo'lda", callback_data=f"status_{order_id}_delivering")],
        [InlineKeyboardButton("\U0001f69a Yetkazildi", callback_data=f"status_{order_id}_delivered")]
    ])

def phone_keyboard(context):
    from config import LOCALES_DIR
    import json
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        share = l.get("share_phone", "Share phone")
    except Exception:
        share = "Share phone"

    return ReplyKeyboardMarkup(
        [[KeyboardButton(share, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )