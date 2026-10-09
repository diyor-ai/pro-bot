import asyncio
from types import SimpleNamespace

import pytest

import bot
import i18n
from tests.helpers import make_context

ORDER = {
    "id": 7, "mahsulot": "Air Max", "narx": 1500000, "ism": "Ali", "telefon": "+998901234567",
    "manzil": "Toshkent", "sana": "2026-10-09 12:00", "til": "ru", "kategoriya": "Krossovka",
}


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, **kwargs):
        self.sent.append(kwargs)


def notify(lang, monkeypatch):
    monkeypatch.setattr(bot, "ADMIN_LANG", lang)
    monkeypatch.setattr(bot, "ADMIN_CHAT_ID", "1")
    fake = FakeBot()
    asyncio.run(bot.notify_admin(SimpleNamespace(bot=fake), dict(ORDER)))
    return fake.sent[0]


def labels(message):
    return [row[0].text for row in message["reply_markup"].inline_keyboard]


def test_notification_and_buttons_follow_admin_lang(monkeypatch):
    uz = notify("uz", monkeypatch)
    assert "YANGI BUYURTMA" in uz["text"] and "1 500 000 so'm" in uz["text"]
    assert labels(uz) == ["🔥 Jarayonda", "🚦 Yo'lda", "🚚 Yetkazildi"]

    en = notify("en", monkeypatch)
    assert "NEW ORDER" in en["text"] and "1 500 000 UZS" in en["text"]
    assert labels(en) == ["🔥 Processing", "🚦 On the way", "🚚 Delivered"]

    ru = notify("ru", monkeypatch)
    assert "НОВЫЙ ЗАКАЗ" in ru["text"] and "1 500 000 сум" in ru["text"]
    assert "👟 Air Max" in ru["text"]  # Krossovka emoji, not a hard-coded one
    assert "🌍 RU" in ru["text"]  # the customer's language code


def test_admin_panel_follows_admin_lang(monkeypatch):
    monkeypatch.setattr(bot, "ADMIN_LANG", "en")
    monkeypatch.setattr(bot, "ADMIN_IDS", [1])
    message = SimpleNamespace(replies=[])

    async def reply_text(text, **kwargs):
        message.replies.append((text, kwargs))

    message.reply_text = reply_text
    update = SimpleNamespace(message=message, effective_user=SimpleNamespace(id=1))
    asyncio.run(bot.admin_cmd(update, make_context({"lang": "uz"})))
    text, kwargs = message.replies[0]
    assert text == "📋 Admin panel:"
    assert [r[0].text for r in kwargs["reply_markup"].inline_keyboard] == ["📋 Orders", "📊 Statistics", "📢 Broadcast"]


@pytest.mark.parametrize("admin_lang", ["uz", "ru", "en"])
def test_sheet_status_values_do_not_depend_on_language(monkeypatch, admin_lang):
    monkeypatch.setattr(bot, "ADMIN_LANG", admin_lang)
    monkeypatch.setattr(bot, "ADMIN_IDS", [1])
    saved = []
    monkeypatch.setattr(bot, "update_order_status", lambda oid, status: saved.append((oid, status)) or True)

    class Query:
        from_user = SimpleNamespace(id=1)

        def __init__(self, data):
            self.data = data

        async def answer(self, *a, **k):
            pass

    for data in ("status_7_processing", "status_7_delivering", "status_7_delivered"):
        asyncio.run(bot.button_handler(SimpleNamespace(callback_query=Query(data)), make_context()))
    assert saved == [("7", "Jarayonda"), ("7", "Yo'lda"), ("7", "Yetkazildi")]


def test_resolve_admin_lang():
    locales = {"uz": {}, "en": {}}
    assert i18n.resolve_admin_lang("en", locales) == "en"
    assert i18n.resolve_admin_lang("de", locales) == "uz"
    assert i18n.resolve_admin_lang("", locales) == "uz"
