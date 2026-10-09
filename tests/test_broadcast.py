import asyncio

from telegram.error import Forbidden, RetryAfter

import bot


class FakeBot:
    def __init__(self, behaviour):
        self.behaviour = behaviour
        self.calls = []

    async def send_message(self, chat_id, text):
        self.calls.append(chat_id)
        action = self.behaviour.get(chat_id)
        if callable(action):
            action(self)
        return None


def run(fake, ids):
    return asyncio.run(bot.send_broadcast(fake, ids, "hi", delay=0))


def test_counts_sent_and_failed_and_continues_after_error():
    def blocked(_):
        raise Forbidden("bot was blocked by the user")

    fake = FakeBot({2: blocked})
    assert run(fake, [1, 2, 3]) == (2, 1)
    assert fake.calls == [1, 2, 3]


def test_retry_after_is_retried_once(monkeypatch):
    async def no_sleep(_):
        pass

    monkeypatch.setattr(bot.asyncio, "sleep", no_sleep)
    state = {"n": 0}

    def flood(_):
        state["n"] += 1
        if state["n"] == 1:
            raise RetryAfter(1)

    fake = FakeBot({1: flood})
    assert run(fake, [1]) == (1, 0)
    assert fake.calls == [1, 1]
