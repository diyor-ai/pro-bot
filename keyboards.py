from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from i18n import tr
from utils import parse_price


def lang_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\U0001f1fa\U0001f1ff O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton("\U0001f1f7\U0001f1fa Русский", callback_data="lang_ru"),
        InlineKeyboardButton("\U0001f1ec\U0001f1e7 English", callback_data="lang_en"),
    ]])

def main_menu_keyboard(context):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(context, "all_products", "\U0001f4e6 Products"), callback_data="show_products")],
        [InlineKeyboardButton(tr(context, "search", "\U0001f50d Search"), callback_data="search")],
    ])

def back_keyboard(context):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(tr(context, "back", "\U0001f519 Back"), callback_data="back")
    ]])

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f4cb Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton("\U0001f4ca Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("\U0001f4e2 Broadcast", callback_data="admin_broadcast")],
    ])

def broadcast_confirm_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Yuborish", callback_data="broadcast_send"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="broadcast_cancel"),
    ]])

def category_keyboard(context, categories):
    # callback_data is limited to 64 bytes, so send the index and map it back in the handler
    buttons = [[InlineKeyboardButton(cat, callback_data=f"cat_{i}")] for i, cat in enumerate(categories)]
    buttons.append([InlineKeyboardButton(tr(context, "back", "\U0001f519 Back"), callback_data="back")])
    return InlineKeyboardMarkup(buttons)

def products_keyboard(context, products):
    buttons = [
        [InlineKeyboardButton(
            f"{p['Nomi']} \U0001f4b0 {parse_price(p['Narxi']):,}".replace(",", " "),
            callback_data=f"product_{p['ID']}"
        )] for p in products
    ]
    buttons.append([InlineKeyboardButton(tr(context, "back", "\U0001f519 Back"), callback_data="back")])
    return InlineKeyboardMarkup(buttons)

def product_action_keyboard(context, product_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(context, "yes", "✅ Yes"), callback_data=f"buy_{product_id}"),
         InlineKeyboardButton(tr(context, "no", "❌ No"), callback_data="back")]
    ])

def confirm_keyboard(context):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(context, "confirm_btn", "✅ Confirm"), callback_data="confirm_order")],
        [InlineKeyboardButton(tr(context, "cancel_btn", "❌ Cancel"), callback_data="cancel_order")]
    ])

def order_status_keyboard(order_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f525 Jarayonda", callback_data=f"status_{order_id}_processing")],
        [InlineKeyboardButton("\U0001f6a6 Yo'lda", callback_data=f"status_{order_id}_delivering")],
        [InlineKeyboardButton("\U0001f69a Yetkazildi", callback_data=f"status_{order_id}_delivered")]
    ])

def phone_keyboard(context):
    return ReplyKeyboardMarkup(
        [[KeyboardButton(tr(context, "share_phone", "Share phone"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
