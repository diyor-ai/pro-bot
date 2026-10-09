import pytest

from utils import (
    esc, format_price, fuzzy_search, is_available, next_order_id,
    parse_price, sanitize, validate_phone,
)


@pytest.mark.parametrize("raw,expected", [
    ("+998901234567", "+998901234567"),
    ("998901234567", "+998901234567"),
    ("901234567", "+998901234567"),
    ("+998 90 123-45-67", "+998901234567"),
    ("  901234567 ", "+998901234567"),
])
def test_validate_phone_ok(raw, expected):
    assert validate_phone(raw) == expected


@pytest.mark.parametrize("raw", ["", "abc", "12345", "+99890123456", "+9989012345678", "801234567", "+1 202 555 0100"])
def test_validate_phone_rejects(raw):
    assert validate_phone(raw) is None


@pytest.mark.parametrize("raw,expected", [
    (150000, 150000),
    ("150000", 150000),
    ("150 000", 150000),
    ("150,000", 150000),
    ("1.250.000", 1250000),
    ("99.5", 99),
    ("99,5", 99),
    ("150000 so'm", 150000),
    ("", 0),
    (None, 0),
    ("abc", 0),
])
def test_parse_price(raw, expected):
    assert parse_price(raw) == expected


def test_format_price():
    assert format_price("1500000") == "1 500 000 so'm"
    assert format_price("bad") == "0 so'm"


def test_esc_escapes_html_and_keeps_markdown_chars():
    assert esc("<b>a_b*c</b> & d") == "&lt;b&gt;a_b*c&lt;/b&gt; &amp; d"
    assert esc(123) == "123"
    assert esc('say "hi"') == 'say "hi"'


def test_sanitize_only_strips():
    assert sanitize("  Ali_*<x>  ") == "Ali_*<x>"


@pytest.mark.parametrize("value,expected", [
    ("TRUE", True), ("true", True), ("YES", True), ("", True), (None, True),
    ("FALSE", False), ("no", False),
    (5, True), ("5", True), ("2.0", True), ("0", False), (0, False), ("-1", False),
    ("abc", False),
])
def test_is_available(value, expected):
    assert is_available(value) is expected


@pytest.mark.parametrize("column,expected", [
    ([], 1),
    (["1", "2", "3"], 4),
    ([1, 2, 7], 8),
    (["1", "", "x", "5"], 6),
    (["3", "1"], 4),
])
def test_next_order_id(column, expected):
    assert next_order_id(column) == expected


PRODUCTS = [
    {"ID": 1, "Nomi": "Nike Air Max", "Tavsif": "Running shoes", "Kategoriya": "Krossovka"},
    {"ID": 2, "Nomi": "Adidas Superstar", "Tavsif": "Classic sneakers", "Kategoriya": "Krossovka"},
    {"ID": 3, "Nomi": "Leather Wallet", "Tavsif": "Brown wallet", "Kategoriya": "Aksessuar"},
]


def test_fuzzy_search_finds_typo():
    found = fuzzy_search("nikee air", PRODUCTS)
    assert found and found[0]["ID"] == 1


def test_fuzzy_search_case_insensitive_and_by_category():
    assert {p["ID"] for p in fuzzy_search("AKSESSUAR", PRODUCTS)} == {3}


def test_fuzzy_search_no_match_and_threshold():
    assert fuzzy_search("zzzzqqq", PRODUCTS) == []
    assert fuzzy_search("nike", PRODUCTS, threshold=101) == []


def test_product_emoji_by_category():
    from config import DEFAULT_PRODUCT_EMOJI
    from utils import product_emoji

    assert product_emoji("Krossovka") == "\U0001f45f"
    assert product_emoji(" aksessuar ") == "\U0001f45c"
    assert product_emoji("Kamar") == DEFAULT_PRODUCT_EMOJI == "\U0001f6cd"
    assert product_emoji(None) == DEFAULT_PRODUCT_EMOJI
    assert product_emoji("Kamar", {"kamar": "x"}) == "x"


def test_parse_category_emoji():
    from config import parse_category_emoji

    assert parse_category_emoji("Krossovka=A, Kiyim = B,bad,=C,D=") == {"krossovka": "A", "kiyim": "B"}
    assert parse_category_emoji("") == {}
