"""Tiny fakes for driving handlers without Telegram."""
from types import SimpleNamespace


class FakeMessage:
    def __init__(self, text=None, contact=None):
        self.text = text
        self.contact = contact
        self.replies = []

    async def reply_text(self, text, **kwargs):
        self.replies.append((text, kwargs))


def make_update(text=None, user_id=1):
    message = FakeMessage(text)
    return SimpleNamespace(
        message=message,
        effective_user=SimpleNamespace(id=user_id),
    ), message


def make_context(user_data=None):
    return SimpleNamespace(user_data=user_data if user_data is not None else {}, bot=None)
