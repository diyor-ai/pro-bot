import json
import logging
import os

from config import LOCALES_DIR

logger = logging.getLogger(__name__)
DEFAULT_LANG = "uz"


def load_locales():
    locales = {}
    try:
        for file in os.listdir(LOCALES_DIR):
            if file.endswith(".json"):
                with open(os.path.join(LOCALES_DIR, file), encoding="utf-8") as f:
                    locales[file[:-5]] = json.load(f)
    except Exception:
        logger.exception("Failed to load locales from %s", LOCALES_DIR)
    return locales


LOCALES = load_locales()


def tr(context, key, default=None):
    lang = context.user_data.get("lang", DEFAULT_LANG)
    value = LOCALES.get(lang, LOCALES.get(DEFAULT_LANG, {})).get(key)
    if value is None:
        return default if default is not None else key
    return value
