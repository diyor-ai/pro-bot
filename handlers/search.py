from telegram import Update
from telegram.ext import ContextTypes
from keyboards import products_keyboard, back_keyboard
from sheets import get_products
from config import LOCALES_DIR, FUZZY_THRESHOLD
from rapidfuzz import fuzz
import json

def t(context, key):
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        return l.get(key, key)
    except Exception:
        return key

def fuzzy_search(query, products, threshold=FUZZY_THRESHOLD):
    query = query.lower()
    results = []

    for p in products:
        name = str(p.get("Nomi", "")).lower()
        desc = str(p.get("Tavsif", "")).lower()
        cat = str(p.get("Kategoriya", "")).lower()

        score = max(
            fuzz.partial_ratio(query, name),
            fuzz.token_sort_ratio(query, name),
            fuzz.partial_ratio(query, desc),
            fuzz.token_sort_ratio(query, desc),
            fuzz.partial_ratio(query, cat),
            fuzz.token_sort_ratio(query, cat),
        )

        if score >= threshold:
            results.append((score, p))

    results.sort(key=lambda x: -x[0])
    return [p for _, p in results]

async def handle_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    products = get_products()
    found = fuzzy_search(text, products)

    if found:
        keyboard = products_keyboard(context, found)
        found_text = t(context, "found")
        await update.message.reply_text(
            f"✅ *{len(found)} {found_text}:*",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(t(context, "not_found"))

    context.user_data['step'] = None