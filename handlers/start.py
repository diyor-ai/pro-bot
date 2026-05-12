from telegram import Update
from telegram.ext import ContextTypes
from keyboards import lang_keyboard, main_menu_keyboard
from config import SHOP_NAME, LOCALES_DIR
import json

def t(context, key):
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        return l.get(key, key)
    except Exception:
        return key

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(t(context, "choose_lang"), reply_markup=lang_keyboard())

async def handle_lang(query, context):
    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang
    await query.edit_message_text(
        f"\U0001f3ea *{SHOP_NAME}*\n\n{t(context, 'welcome')}",
        reply_markup=main_menu_keyboard(context),
        parse_mode='Markdown'
    )