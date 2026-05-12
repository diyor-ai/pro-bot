import json
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from config import TELEGRAM_TOKEN, SHOP_NAME, LOCALES_DIR
from sheets import get_products, get_categories, get_product_by_id, save_order, get_orders, get_stats, update_order_status
from keyboards import (
    lang_keyboard, main_menu_keyboard, back_keyboard, admin_keyboard,
    category_keyboard, products_keyboard, product_action_keyboard, confirm_keyboard,
    phone_keyboard, order_status_keyboard
)
from rapidfuzz import fuzz

load_dotenv()

# ============== LOCALES ==============
def load_locales():
    locales = {}
    try:
        for file in __import__("os").listdir(LOCALES_DIR):
            if file.endswith(".json"):
                lang = file.replace(".json", "")
                with open(f"{LOCALES_DIR}/{file}", encoding="utf-8") as f:
                    locales[lang] = json.load(f)
    except Exception as e:
        print(f"Locale error: {e}")
    return locales

LOCALES = load_locales()

def t(context, key):
    lang = context.user_data.get("lang", "uz")
    return LOCALES.get(lang, LOCALES.get("uz", {})).get(key, key)

# ============== HELPERS ==============
def format_price(price):
    return f"{int(price):,} so'm".replace(",", " ")

def sanitize(text):
    return text.replace("<", "&lt;").replace(">", "&gt;").strip()

def validate_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    patterns = [r'^\+998\d{9}$', r'^998\d{9}$', r'^9\d{8}$']
    for pattern in patterns:
        if re.match(pattern, phone):
            if not phone.startswith("+"):
                phone = "+" + phone if phone.startswith("998") else "+998" + phone
            return phone
    return None

def fuzzy_search(query, products, threshold=65):
    q = query.lower()
    results = []
    for p in products:
        name = str(p.get("Nomi", "")).lower()
        desc = str(p.get("Tavsif", "")).lower()
        cat = str(p.get("Kategoriya", "")).lower()
        score = max(
            fuzz.partial_ratio(q, name),
            fuzz.token_sort_ratio(q, name),
            fuzz.partial_ratio(q, desc),
            fuzz.token_sort_ratio(q, desc),
            fuzz.partial_ratio(q, cat),
            fuzz.token_sort_ratio(q, cat),
        )
        if score >= threshold:
            results.append((score, p))
    results.sort(key=lambda x: -x[0])
    return [p for _, p in results]

# ============== ADMIN ==============
from config import ADMIN_CHAT_ID, ADMIN_IDS

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def notify_admin(context, order):
    try:
        text = (
            f"\U0001f195 YANGI BUYURTMA!\n"
            f"\U0001f3ea {SHOP_NAME}\n"
            f"\U0001f30d {order.get('til', 'uz').upper()}\n"
            f"{'=' * 30}\n"
            f"\U0001f45f {order['mahsulot']}\n"
            f"\U0001f4b0 {format_price(order['narx'])}\n"
            f"\U0001f464 {order['ism']}\n"
            f"\U0001f4f1 {order['telefon']}\n"
            f"\U0001f4cd {order['manzil']}\n"
            f"\U0001f55c {order['sana']}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=text,
            reply_markup=order_status_keyboard("latest")
        )
    except Exception as e:
        print(f"Admin notify error: {e}")

# ============== HANDLERS ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(t(context, "choose_lang"), reply_markup=lang_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Language
    if query.data.startswith("lang_"):
        lang = query.data.replace("lang_", "")
        context.user_data["lang"] = lang
        await query.edit_message_text(
            f"\U0001f3ea *{SHOP_NAME}*\n\n{t(context, 'welcome')}",
            reply_markup=main_menu_keyboard(context),
            parse_mode='Markdown'
        )
        return

    # Back
    if query.data == "back":
        await query.edit_message_text(
            f"\U0001f3ea *{SHOP_NAME}*",
            reply_markup=main_menu_keyboard(context),
            parse_mode='Markdown'
        )
        return

    # Show products (categories)
    if query.data == "show_products":
        categories = get_categories()
        if not categories or len(categories) == 0:
            products = get_products()
            if not products:
                await query.edit_message_text("❌ Mahsulotlar topilmadi", reply_markup=back_keyboard(context))
                return
            await query.edit_message_text(
                f"*{t(context, 'choose_product')}*",
                reply_markup=products_keyboard(context, products),
                parse_mode='Markdown'
            )
            return
        await query.edit_message_text(
            f"*{t(context, 'choose_category')}*",
            reply_markup=category_keyboard(context, categories),
            parse_mode='Markdown'
        )
        return

    # Category filter
    if query.data.startswith("cat_"):
        category = query.data[4:]
        products = get_products(category)
        if not products:
            await query.edit_message_text(t(context, "not_found"), reply_markup=back_keyboard(context))
            return
        await query.edit_message_text(
            f"*{t(context, 'choose_product')}*",
            reply_markup=products_keyboard(context, products),
            parse_mode='Markdown'
        )
        return

    # Product detail
    if query.data.startswith("product_"):
        pid = int(query.data.split("_")[1])
        p = get_product_by_id(pid)
        if not p:
            await query.edit_message_text("❌ Mahsulot topilmadi", reply_markup=back_keyboard(context))
            return

        cap = f"\U0001f45f *{p['Nomi']}*\n\n\U0001f4b0 {format_price(p['Narxi'])}\n\U0001f4dd {p.get('Tavsif', '-')}\n\n{t(context, 'buy_confirm')}"

        try:
            rasm = p.get("Rasm_URL", "")
            if rasm and str(rasm).strip():
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=rasm,
                    caption=cap,
                    reply_markup=product_action_keyboard(context, p['ID']),
                    parse_mode='Markdown'
                )
                await query.delete_message()
                return
        except Exception:
            pass

        await query.edit_message_text(cap, reply_markup=product_action_keyboard(context, p['ID']), parse_mode='Markdown')
        return

    # Buy product
    if query.data.startswith("buy_"):
        pid = int(query.data.split("_")[1])
        p = get_product_by_id(pid)
        if not p:
            return
        context.user_data['order'] = {"mahsulot": p['Nomi'], "narx": p['Narxi'], "user_id": query.from_user.id}
        context.user_data['step'] = 'ism'
        await query.edit_message_text(t(context, "ask_name"))
        return

    # Confirm order
    if query.data == "confirm_order":
        order = context.user_data.get('pending_order')
        if not order:
            return
        save_order(order)
        await notify_admin(context, order)
        await query.edit_message_text(
            f"{t(context, 'order_done')}!\n\n\U0001f64f Tez orada bog'lanamiz!",
            reply_markup=main_menu_keyboard(context)
        )
        context.user_data['step'] = None
        context.user_data['order'] = {}
        context.user_data['pending_order'] = None
        return

    # Cancel order
    if query.data == "cancel_order":
        await query.edit_message_text(t(context, "order_cancelled"), reply_markup=main_menu_keyboard(context))
        context.user_data['step'] = None
        context.user_data['order'] = {}
        context.user_data['pending_order'] = None
        return

    # Search
    if query.data == "search":
        context.user_data['step'] = 'searching'
        await query.edit_message_text(t(context, "search_prompt"))
        return

    # Admin
    if query.data == "admin_orders":
        if not is_admin(query.from_user.id):
            await query.answer("❌ Access denied")
            return
        orders = get_orders(status="Yangi", limit=10)
        if not orders:
            await query.edit_message_text(t(context, "no_orders"), reply_markup=back_keyboard(context))
            return
        for o in orders:
            txt = f"\U0001f45f {o.get('Mahsulot', '-')}\n\U0001f4b0 {format_price(o.get('Narx', 0))}\n\U0001f464 {o.get('Ism', '-')}\n\U0001f4f1 {o.get('Telefon', '-')}\n\U0001f4cd {o.get('Manzil', '-')}"
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=txt,
                reply_markup=order_status_keyboard(o.get('ID', 0))
            )
        await query.delete_message()
        return

    if query.data == "admin_stats":
        if not is_admin(query.from_user.id):
            await query.answer("❌ Access denied")
            return
        stats = get_stats()
        txt = f"\U0001f4ca Statistika:\n\nJami: {stats.get('total', 0)}\nBugun: {stats.get('today', 0)}\nYangi: {stats.get('new', 0)}\nDaromad: {stats.get('revenue', 0):,} so'm".replace(",", " ")
        await query.edit_message_text(txt, reply_markup=back_keyboard(context))
        return

    if query.data == "admin_broadcast":
        if not is_admin(query.from_user.id):
            await query.answer("❌ Access denied")
            return
        context.user_data['step'] = 'broadcast'
        await query.edit_message_text("Xabar matnini yozing:", reply_markup=back_keyboard(context))
        return

    # Status update
    if query.data.startswith("status_"):
        parts = query.data.split("_")
        if len(parts) >= 3:
            order_id, st = parts[1], parts[2]
            status_map = {"processing": "Jarayonda", "delivering": "Yo'lda", "delivered": "Yetkazildi"}
            update_order_status(order_id, status_map.get(st, st))
            await query.answer(t(context, "order_status_updated"))
        return

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')
    text = update.message.text

    # Contact
    if update.message.contact:
        phone = update.message.contact.phone_number
        validated = validate_phone(phone)
        if validated:
            context.user_data['order']['telefon'] = validated
            context.user_data['step'] = 'manzil'
            await update.message.reply_text(t(context, "ask_address"), reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text(t(context, "invalid_phone"))
        return

    if not step:
        await start(update, context)
        return

    # Search
    if step == 'searching':
        products = get_products()
        found = fuzzy_search(sanitize(text), products)
        if found:
            await update.message.reply_text(
                f"✅ *{len(found)} {t(context, 'found')}:*",
                reply_markup=products_keyboard(context, found),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(t(context, "not_found"))
        context.user_data['step'] = None
        return

    # Broadcast
    if step == 'broadcast':
        if not is_admin(update.effective_user.id):
            return
        await update.message.reply_text(f"Broadcast yuborildi!\n\n{text}")
        context.user_data['step'] = None
        return

    # Order flow
    if step == 'ism':
        context.user_data['order']['ism'] = sanitize(text)
        context.user_data['step'] = 'telefon'
        await update.message.reply_text(
            t(context, "ask_phone"),
            reply_markup=phone_keyboard(context)
        )

    elif step == 'telefon':
        validated = validate_phone(text)
        if validated:
            context.user_data['order']['telefon'] = validated
            context.user_data['step'] = 'manzil'
            await update.message.reply_text(t(context, "ask_address"), reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text(t(context, "invalid_phone"))

    elif step == 'manzil':
        order = context.user_data['order']
        order['manzil'] = sanitize(text)
        order['sana'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        order['til'] = context.user_data.get("lang", "uz")

        context.user_data['pending_order'] = order

        await update.message.reply_text(
            f"\U0001f4cb *{t(context, 'confirm_order')}*\n\n"
            f"\U0001f45f {order['mahsulot']}\n"
            f"\U0001f4b0 {format_price(order['narx'])}\n"
            f"\U0001f464 {order['ism']}\n"
            f"\U0001f4f1 {order['telefon']}\n"
            f"\U0001f4cd {order['manzil']}",
            reply_markup=confirm_keyboard(context),
            parse_mode='Markdown'
        )

# ============== ADMIN COMMAND ==============
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Access denied")
        return
    await update.message.reply_text("\U0001f4cb Admin panel:", reply_markup=admin_keyboard())

# ============== MAIN ==============
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.CONTACT, message_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print(f"🤖 {SHOP_NAME} boti ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()