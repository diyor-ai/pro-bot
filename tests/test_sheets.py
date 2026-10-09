import sheets


class FakeSheet:
    def __init__(self, rows):
        self.rows = rows
        self.reads = 0

    def get_all_records(self):
        self.reads += 1
        return self.rows


class FakeSpreadsheet:
    def __init__(self, rows):
        self.sheet1 = FakeSheet(rows)


ROWS = [
    {"ID": 1, "Nomi": "A", "Narxi": 10, "Kategoriya": "Krossovka", "Mavjud": "TRUE"},
    {"ID": 2, "Nomi": "B", "Narxi": 20, "Kategoriya": "Aksessuar", "Mavjud": ""},
    {"ID": 3, "Nomi": "C", "Narxi": 30, "Kategoriya": "Aksessuar", "Mavjud": "FALSE"},
]


def install_fake(monkeypatch, rows=ROWS):
    spreadsheet = FakeSpreadsheet(rows)
    calls = {"authorize": 0}

    class Client:
        def open(self, name):
            return spreadsheet

    def authorize(creds):
        calls["authorize"] += 1
        return Client()

    monkeypatch.setattr(sheets, "get_credentials", lambda: object())
    monkeypatch.setattr(sheets.gspread, "authorize", authorize)
    return spreadsheet, calls


def test_client_is_created_once_and_reused(monkeypatch):
    spreadsheet, calls = install_fake(monkeypatch)
    monkeypatch.setattr(sheets, "CACHE_TTL", 0)  # force a re-read every call
    sheets.get_products()
    sheets.get_products()
    assert spreadsheet.sheet1.reads == 2
    assert calls["authorize"] == 1


def test_categories_are_filtered_from_one_sheet_read(monkeypatch):
    spreadsheet, _ = install_fake(monkeypatch)
    assert [p["ID"] for p in sheets.get_products()] == [1, 2]
    assert [p["ID"] for p in sheets.get_products("aksessuar")] == [2]
    assert sheets.get_categories() == ["Aksessuar", "Krossovka"]
    assert spreadsheet.sheet1.reads == 1


def test_stale_products_are_served_when_google_fails(monkeypatch):
    spreadsheet, _ = install_fake(monkeypatch)
    monkeypatch.setattr(sheets, "CACHE_TTL", 0)
    assert len(sheets.get_products()) == 2

    def fail():
        raise RuntimeError("quota")

    monkeypatch.setattr(spreadsheet.sheet1, "get_all_records", fail)
    assert len(sheets.get_products()) == 2
