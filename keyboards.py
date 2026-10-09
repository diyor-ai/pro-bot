from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from i18n import translate, tr
from utils import parse_price


def lang_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\U0001f1fa\U0001f1ff O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton("\U0001f1f7\U0001f1fa Русский", callback_data="lang_ru"),
        InlineKeyboardButton("\U0001f1ec\U0001f1e7 English", callback_data="lang_en"),
    ]])

def main_menu_keyboard(context):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(context, "all_products"), callback_data="show_products")],
        [InlineKeyboardButton(tr(context, "search"), callback_data="search")],
    ])

def back_keyboard(context, lang=None):
    """Back button in the user's language, or in `lang` (used for admin screens)."""
    label = translate(lang, "back") if lang else tr(context, "back")
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="back")]])

def admin_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate(lang, "admin_orders"), callback_data="admin_orders")],
        [InlineKeyboardButton(translate(lang, "admin_stats"), callback_data="admin_stats")],
        [InlineKeyboardButton(translate(lang, "admin_broadcast"), callback_data="admin_broadcast")],
    ])

def broadcast_confirm_keyboard(lang):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(translate(lang, "admin_broadcast_send_btn"), callback_data="broadcast_send"),
        InlineKeyboardButton(translate(lang, "cancel_btn"), callback_data="broadcast_cancel"),
    ]])

def category_keyboard(context, categories):
    # callback_data is limited to 64 bytes, so send the index and map it back in the handler
    buttons = [[InlineKeyboardButton(cat, callback_data=f"cat_{i}")] for i, cat in enumerate(categories)]
    buttons.append([InlineKeyboardButton(tr(context, "back"), callback_data="back")])
    return InlineKeyboardMarkup(buttons)

def products_keyboard(context, products):
    buttons = [
        [InlineKeyboardButton(
            f"{p['Nomi']} \U0001f4b0 {parse_price(p['Narxi']):,}".replace(",", " "),
            callback_data=f"product_{p['ID']}"
        )] for p in products
    ]
    buttons.append([InlineKeyboardButton(tr(context, "back"), callback_data="back")])
    return InlineKeyboardMarkup(buttons)

def product_action_keyboard(context, product_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(context, "yes"), callback_data=f"buy_{product_id}"),
         InlineKeyboardButton(tr(context, "no"), callback_data="back")]
    ])

def confirm_keyboard(context):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(context, "confirm_btn"), callback_data="confirm_order")],
        [InlineKeyboardButton(tr(context, "cancel_btn"), callback_data="cancel_order")]
    ])

def order_status_keyboard(order_id, lang):
    # Only the labels are translated; the callback names map to the sheet values in bot.py.
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate(lang, "status_processing"), callback_data=f"status_{order_id}_processing")],
        [InlineKeyboardButton(translate(lang, "status_delivering"), callback_data=f"status_{order_id}_delivering")],
        [InlineKeyboardButton(translate(lang, "status_delivered"), callback_data=f"status_{order_id}_delivered")]
    ])

def phone_keyboard(context):
    return ReplyKeyboardMarkup(
        [[KeyboardButton(tr(context, "share_phone"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
