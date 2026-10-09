import json
import logging
import os

from config import ADMIN_LANG as _ADMIN_LANG_RAW
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


def resolve_admin_lang(value, locales=None):
    """ADMIN_LANG if we have that locale, otherwise the default language (with a warning)."""
    locales = LOCALES if locales is None else locales
    if value in locales:
        return value
    logger.warning("ADMIN_LANG=%r is not one of %s, using %r", value, sorted(locales), DEFAULT_LANG)
    return DEFAULT_LANG


ADMIN_LANG = resolve_admin_lang(_ADMIN_LANG_RAW)


def translate(lang, key, /, **kwargs):
    """Text for `key` in `lang` (falls back to the default language, then to the key itself)."""
    value = LOCALES.get(lang, {}).get(key)
    if value is None:
        value = LOCALES.get(DEFAULT_LANG, {}).get(key)
    if value is None:
        return key
    return value.format(**kwargs) if kwargs else value


def tr(context, key, /, **kwargs):
    return translate(context.user_data.get("lang", DEFAULT_LANG), key, **kwargs)
