import asyncio

import bot


def test_user_state_survives_a_restart(tmp_path):
    path = tmp_path / "data" / "state.pickle"  # directory does not exist yet
    state = {"lang": "ru", "step": "manzil", "order": {"mahsulot": "Air", "narx": 100}}

    async def first_run():
        p = bot.build_persistence(str(path))
        await p.update_user_data(42, state)
        await p.flush()

    async def second_run():
        return await bot.build_persistence(str(path)).get_user_data()

    asyncio.run(first_run())
    assert asyncio.run(second_run()) == {42: state}


def test_only_user_data_is_stored(tmp_path):
    p = bot.build_persistence(str(tmp_path / "s.pickle"))
    assert p.store_data.user_data is True
    assert not (p.store_data.bot_data or p.store_data.chat_data or p.store_data.callback_data)
