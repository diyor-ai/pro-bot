"""Pure helper functions (no Telegram or Google calls)."""
import html
import re

from rapidfuzz import fuzz

from config import FUZZY_THRESHOLD


def parse_price(value):
    """Turn a sheet value like 150000, "150 000", "150,000" or "99.5" into an int (0 if unparseable)."""
    text = re.sub(r"[^\d.,]", "", str(value if value is not None else ""))
    if not text:
        return 0
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", text):  # thousands separators
        text = re.sub(r"[.,]", "", text)
    else:
        text = text.replace(",", ".")
    try:
        return int(float(text))
    except ValueError:
        return 0


def format_price(price):
    return f"{parse_price(price):,} so'm".replace(",", " ")


def esc(text):
    """Escape user/sheet text for Telegram parse_mode='HTML'."""
    return html.escape(str(text), quote=False)


def sanitize(text):
    return text.strip()


def validate_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    patterns = [r'^\+998\d{9}$', r'^998\d{9}$', r'^9\d{8}$']
    for pattern in patterns:
        if re.match(pattern, phone):
            if not phone.startswith("+"):
                phone = "+" + phone if phone.startswith("998") else "+998" + phone
            return phone
    return None


def fuzzy_search(query, products, threshold=FUZZY_THRESHOLD):
    query = query.lower()
    results = []
    for p in products:
        name = str(p.get("Nomi", "")).lower()
        desc = str(p.get("Tavsif", "")).lower()
        cat = str(p.get("Kategoriya", "")).lower()
        score = max(
            fuzz.partial_ratio(query, name),
            fuzz.token_sort_ratio(query, name),
            fuzz.partial_ratio(query, desc),
            fuzz.token_sort_ratio(query, desc),
            fuzz.partial_ratio(query, cat),
            fuzz.token_sort_ratio(query, cat),
        )
        if score >= threshold:
            results.append((score, p))
    results.sort(key=lambda x: -x[0])
    return [p for _, p in results]


def is_available(value):
    """Mavjud: TRUE/YES/HA, blank, or a number > 0 means available; FALSE/NO/0 means not."""
    v = str(value if value is not None else "").strip().upper()
    if v in ("", "TRUE", "YES", "HA"):
        return True
    if v in ("FALSE", "NO", "YO'Q"):
        return False
    try:
        return float(v.replace(",", ".")) > 0
    except ValueError:
        return False


def next_order_id(id_column_values):
    """Next order ID from the raw ID column (header and junk cells are ignored)."""
    ids = [int(str(v)) for v in id_column_values if str(v).strip().isdigit()]
    return max(ids, default=0) + 1
