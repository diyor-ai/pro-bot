from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from keyboards import category_keyboard, products_keyboard, product_action_keyboard, back_keyboard
from sheets import get_products, get_categories, get_product_by_id
from config import LOCALES_DIR
import json

def t(context, key):
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        return l.get(key, key)
    except Exception:
        return key

async def show_categories(query, context):
    categories = get_categories()
    if not categories or len(categories) == 0:
        products = get_products()
        if not products:
            await query.edit_message_text("❌ Mahsulotlar topilmadi", reply_markup=back_keyboard(context))
            return
        products_kb = products_keyboard(context, products)
        choose = t(context, "choose_product")
        await query.edit_message_text(f"*{choose}:*", reply_markup=products_kb, parse_mode='Markdown')
        return

    await query.edit_message_text(
        f"*{t(context, 'choose_category')}*",
        reply_markup=category_keyboard(context, categories),
        parse_mode='Markdown'
    )

async def show_products_by_category(query, context, category):
    products = get_products(category)
    if not products:
        await query.edit_message_text(t(context, "not_found"), reply_markup=back_keyboard(context))
        return

    await query.edit_message_text(
        f"*{t(context, 'choose_product')}*",
        reply_markup=products_keyboard(context, products),
        parse_mode='Markdown'
    )

async def show_product_detail(query, context, product_id):
    p = get_product_by_id(product_id)
    if not p:
        await query.edit_message_text("❌ Mahsulot topilmadi", reply_markup=back_keyboard(context))
        return

    caption = (
        f"\U0001f45f *{p['Nomi']}*\n\n"
        f"\U0001f4b0 {int(p['Narxi']):,} so'm\n"
        f"\U0001f4dd {p.get('Tavsif', '-')}\n\n"
        f"{t(context, 'buy_confirm')}"
    ).replace(",", " ")

    try:
        rasm = p.get("Rasm_URL", "")
        if rasm and rasm.strip():
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=rasm,
                caption=caption,
                reply_markup=product_action_keyboard(context, p['ID']),
                parse_mode='Markdown'
            )
            await query.delete_message()
        else:
            await query.edit_message_text(caption, reply_markup=product_action_keyboard(context, p['ID']), parse_mode='Markdown')
    except Exception:
        await query.edit_message_text(caption, reply_markup=product_action_keyboard(context, p['ID']), parse_mode='Markdown')