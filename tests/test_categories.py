import asyncio
from types import SimpleNamespace

import bot
from keyboards import category_keyboard
from tests.helpers import make_context

LONG = "Juda uzun kategoriya nomi " * 6  # far beyond Telegram's 64-byte callback_data limit


def test_category_buttons_never_carry_the_name():
    context = make_context()
    cats = [LONG, "Krossovka", "Ўзбекча категория"]
    keyboard = category_keyboard(context, cats)
    data = [row[0].callback_data for row in keyboard.inline_keyboard]
    assert data[:3] == ["cat_0", "cat_1", "cat_2"]
    assert all(len(d.encode()) <= 64 for d in data)
    assert keyboard.inline_keyboard[0][0].text == LONG


def test_resolve_category_uses_the_list_shown_to_the_user(monkeypatch):
    monkeypatch.setattr(bot, "get_categories", lambda: ["changed"])
    context = make_context({"categories": ["A", "B"]})
    assert asyncio.run(bot.resolve_category(context, 1)) == "B"
    assert asyncio.run(bot.resolve_category(context, 2)) is None


def test_resolve_category_reloads_when_list_is_missing(monkeypatch):
    monkeypatch.setattr(bot, "get_categories", lambda: ["A", "B"])
    context = make_context()
    assert asyncio.run(bot.resolve_category(context, 0)) == "A"
    assert context.user_data["categories"] == ["A", "B"]


class FakeQuery:
    def __init__(self, data):
        self.data = data
        self.edits = []
        self.from_user = SimpleNamespace(id=1)

    async def answer(self, *a, **k):
        pass

    async def edit_message_text(self, text, **kwargs):
        self.edits.append((text, kwargs))


def test_category_click_loads_products_of_that_category(monkeypatch):
    seen = []
    monkeypatch.setattr(bot, "get_products", lambda category=None: seen.append(category) or [
        {"ID": 1, "Nomi": "Air", "Narxi": 100, "Kategoriya": category}
    ])
    context = make_context({"categories": ["Aksessuar", LONG]})
    query = FakeQuery("cat_1")
    asyncio.run(bot.button_handler(SimpleNamespace(callback_query=query), context))
    assert seen == [LONG]
    assert query.edits


def test_stale_or_garbage_category_index_does_not_crash(monkeypatch):
    monkeypatch.setattr(bot, "get_products", lambda category=None: [])
    context = make_context({"categories": ["A"]})
    for data in ("cat_9", "cat_x"):
        query = FakeQuery(data)
        asyncio.run(bot.button_handler(SimpleNamespace(callback_query=query), context))
        assert query.edits
