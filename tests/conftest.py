import pytest


@pytest.fixture(autouse=True)
def no_real_google(monkeypatch):
    """Tests must never reach Google: any real authorize/credentials call fails loudly."""
    import sheets

    def boom(*a, **k):
        raise AssertionError("real Google call attempted in a test")

    monkeypatch.setattr(sheets, "get_credentials", boom)
    monkeypatch.setattr(sheets.gspread, "authorize", boom)
    sheets._reset_spreadsheet()
    sheets._cache.clear()
    yield
    sheets._reset_spreadsheet()
    sheets._cache.clear()
