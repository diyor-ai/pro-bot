import asyncio

import bot
from tests.helpers import make_context, make_update


def test_start_resets_every_flow_and_shows_language_menu():
    update, message = make_update("/start")
    context = make_context({
        "lang": "ru",
        "step": "manzil",
        "order": {"mahsulot": "X"},
        "pending_order": {"mahsulot": "X"},
        "broadcast_text": "hello",
    })
    asyncio.run(bot.start(update, context))
    assert context.user_data == {}
    assert len(message.replies) == 1
    assert message.replies[0][1]["reply_markup"].inline_keyboard[0][0].callback_data == "lang_uz"


def test_text_without_active_step_keeps_language():
    update, message = make_update("hello")
    context = make_context({"lang": "ru"})
    asyncio.run(bot.message_handler(update, context))
    assert context.user_data == {"lang": "ru"}
    assert len(message.replies) == 1


def test_orders_are_saved_one_at_a_time(monkeypatch):
    state = {"running": 0, "peak": 0, "next_id": 0}

    def slow_save(order):
        import time
        state["running"] += 1
        state["peak"] = max(state["peak"], state["running"])
        current = state["next_id"]
        time.sleep(0.05)  # simulate the Sheets round-trip between "read max" and "append"
        state["next_id"] = current + 1
        state["running"] -= 1
        return state["next_id"]

    monkeypatch.setattr(bot, "save_order", slow_save)

    async def run():
        return await asyncio.gather(*(bot.save_order_locked({}) for _ in range(5)))

    ids = asyncio.run(run())
    assert state["peak"] == 1
    assert sorted(ids) == [1, 2, 3, 4, 5]
