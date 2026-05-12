from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from keyboards import confirm_keyboard, phone_keyboard, back_keyboard
from sheets import save_order
from config import LOCALES_DIR, ADMIN_CHAT_ID, ADMIN_IDS
from datetime import datetime
import re
import json

def t(context, key):
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        return l.get(key, key)
    except Exception:
        return key

def validate_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    patterns = [r'^\+998\d{9}$', r'^998\d{9}$', r'^9\d{8}$']
    for pattern in patterns:
        if re.match(pattern, phone):
            if not phone.startswith("+"):
                phone = "+" + phone if phone.startswith("998") else "+998" + phone
            return phone
    return None

async def start_order(query, context, product):
    context.user_data['order'] = {
        "mahsulot": product["Nomi"],
        "narx": product["Narxi"],
        "kategoriya": product.get("Kategoriya", ""),
        "user_id": query.from_user.id
    }
    context.user_data['step'] = 'ism'
    await query.edit_message_text(t(context, "ask_name"))

async def handle_order_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')
    text = update.message.text

    if step == 'ism':
        context.user_data['order']['ism'] = text.strip()
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
            await update.message.reply_text(
                t(context, "ask_address"),
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(t(context, "invalid_phone"))

    elif step == 'manzil':
        order = context.user_data['order']
        order['manzil'] = text.strip()
        order['sana'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        order['til'] = context.user_data.get("lang", "uz")

        context.user_data['pending_order'] = order

        price = int(order['narx'])
        await update.message.reply_text(
            f"\U0001f4cb *{t(context, 'confirm_order')}*\n\n"
            f"\U0001f45f {order['mahsulot']}\n"
            f"\U0001f4b0 {price:,} so'm\n"
            f"\U0001f464 {order['ism']}\n"
            f"\U0001f4f1 {order['telefon']}\n"
            f"\U0001f4cd {order['manzil']}".replace(",", " "),
            reply_markup=confirm_keyboard(context),
            parse_mode='Markdown'
        )

async def confirm_order(query, context):
    order = context.user_data.get('pending_order')
    if not order:
        await query.edit_message_text(t(context, "no_orders"), reply_markup=back_keyboard(context))
        return

    save_order(order)
    await notify_admin(context, order)

    await query.edit_message_text(
        f"{t(context, 'order_done')}!\n\n"
        f"\U0001f64f {t(context, 'order_done')}",
        reply_markup=back_keyboard(context)
    )

    context.user_data['step'] = None
    context.user_data['order'] = {}
    context.user_data['pending_order'] = None

async def cancel_order(query, context):
    await query.edit_message_text(t(context, "order_cancelled"), reply_markup=back_keyboard(context))
    context.user_data['step'] = None
    context.user_data['order'] = {}
    context.user_data['pending_order'] = None

async def notify_admin(context, order):
    try:
        from keyboards import order_status_keyboard
        text = (
            f"\U0001f195 YANGI BUYURTMA!\n"
            f"\U0001f3ea {order.get('shop_name', 'Shop')}\n"
            f"\U0001f30d {order.get('til', 'uz').upper()}\n"
            f"{'=' * 30}\n"
            f"\U0001f45f {order['mahsulot']}\n"
            f"\U0001f4b0 {int(order['narx']):,} so'm\n"
            f"\U0001f464 {order['ism']}\n"
            f"\U0001f4f1 {order['telefon']}\n"
            f"\U0001f4cd {order['manzil']}\n"
            f"\U0001f55c {order['sana']}"
        ).replace(",", " ")
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=text,
            reply_markup=order_status_keyboard("latest")
        )
    except Exception:
        pass