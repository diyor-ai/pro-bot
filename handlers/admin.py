from telegram import Update
from telegram.ext import ContextTypes
from keyboards import admin_keyboard, back_keyboard
from sheets import get_orders, get_stats, update_order_status
from config import ADMIN_IDS, LOCALES_DIR
import json

def t(context, key):
    lang = context.user_data.get("lang", "uz")
    try:
        with open(f"{LOCALES_DIR}/{lang}.json", encoding="utf-8") as f:
            l = json.load(f)
        return l.get(key, key)
    except Exception:
        return key

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Access denied")
        return
    await update.message.reply_text("\U0001f4cb Admin panel:", reply_markup=admin_keyboard())

async def show_orders(query, context):
    orders = get_orders(status="Yangi", limit=20)

    if not orders:
        await query.edit_message_text(t(context, "no_orders"), reply_markup=back_keyboard(context))
        return

    for o in orders[:10]:
        text = (
            f"\U0001f45f {o.get('Mahsulot', '-')}\n"
            f"\U0001f4b0 {int(o.get('Narx', 0)):,} so'm\n".replace(",", " ") +
            f"\U0001f464 {o.get('Ism', '-')}\n"
            f"\U0001f4f1 {o.get('Telefon', '-')}\n"
            f"\U0001f4cd {o.get('Manzil', '-')}"
        )
        from keyboards import order_status_keyboard
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=text,
            reply_markup=order_status_keyboard(o.get('ID', 0))
        )

    await query.delete_message()

async def show_stats(query, context):
    stats = get_stats()
    text = (
        f"\U0001f4ca Statistika:\n\n"
        f"Jami buyurtmalar: {stats.get('total', 0)}\n"
        f"Bugungi: {stats.get('today', 0)}\n"
        f"Yangi: {stats.get('new', 0)}\n"
        f"Daromad: {stats.get('revenue', 0):,} so'm".replace(",", " ")
    )
    await query.edit_message_text(text, reply_markup=back_keyboard(context))

async def handle_status_update(query, context):
    parts = query.data.split("_")
    if len(parts) >= 3:
        order_id = parts[1]
        new_status = parts[2]

        status_map = {
            "processing": "Jarayonda",
            "delivering": "Yo'lda",
            "delivered": "Yetkazildi"
        }
        new_status = status_map.get(new_status, new_status)

        if update_order_status(order_id, new_status):
            await query.answer(t(context, "order_status_updated"))
        else:
            await query.answer("Xatolik!")

async def start_broadcast(query, context):
    context.user_data['step'] = 'broadcast'
    await query.edit_message_text("Xabar matnini yozing:", reply_markup=back_keyboard(context))

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Access denied")
        return

    text = update.message.text
    from sheets import get_credentials, USERS_SHEET
    try:
        import gspread
        creds = get_credentials()
        client = gspread.authorize(creds)
        ws = client.open("Mahsulotlar").worksheet(USERS_SHEET)
        users = ws.get_all_records()
        count = len(users)
        await update.message.reply_text(
            f"Broadcast {count} foydalanuvchiga yuborildi!\n\n{text}"
        )
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")

    context.user_data['step'] = None