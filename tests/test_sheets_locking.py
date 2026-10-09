import threading
import time

import sheets


class Tracker:
    """Records how many threads are inside a fake gspread call at once."""

    def __init__(self):
        self.lock = threading.Lock()
        self.running = 0
        self.peak = 0

    def enter(self):
        with self.lock:
            self.running += 1
            self.peak = max(self.peak, self.running)
        time.sleep(0.01)
        with self.lock:
            self.running -= 1


class FakeWorksheet:
    def __init__(self, tracker):
        self.t = tracker

    def get_all_records(self):
        self.t.enter()
        return [{"ID": 1, "Nomi": "A", "Narxi": 5, "Kategoriya": "K", "Mavjud": "", "Status": "Yangi",
                 "Narx": 5, "Sana": "2026-01-01 10:00"}]

    def get_all_values(self):
        self.t.enter()
        return [["ID"], ["1"]]

    def col_values(self, _):
        self.t.enter()
        return ["ID", "1"]

    def append_row(self, _):
        self.t.enter()

    def update_cell(self, *_):
        self.t.enter()


class FakeSpreadsheet:
    def __init__(self, tracker):
        self.t = tracker
        self.sheet1 = FakeWorksheet(tracker)

    def worksheet(self, _):
        return FakeWorksheet(self.t)


def test_sheets_calls_from_many_threads_run_one_at_a_time(monkeypatch):
    tracker = Tracker()
    monkeypatch.setattr(sheets, "get_credentials", lambda: object())
    monkeypatch.setattr(sheets.gspread, "authorize", lambda creds: type("C", (), {
        "open": lambda self, name: FakeSpreadsheet(tracker)})())
    monkeypatch.setattr(sheets, "CACHE_TTL", 0)  # every get_products call goes to "Google"
    order = {"sana": "2026-01-01 10:00", "mahsulot": "A", "narx": 5, "ism": "x", "telefon": "+998901234567",
             "manzil": "y", "user_id": 1}
    calls = [
        sheets.get_products, sheets.get_orders, sheets.get_stats, sheets.get_user_ids,
        lambda: sheets.update_order_status("1", "Yo'lda"), lambda: sheets.save_order(dict(order)),
    ] * 3
    threads = [threading.Thread(target=call) for call in calls]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert tracker.peak == 1


def test_cache_hits_do_not_wait_for_a_busy_sheets_lock(monkeypatch):
    sheets._cache["products_all"] = {"data": [{"ID": 1}], "last_updated": time.time()}
    monkeypatch.setattr(sheets, "CACHE_TTL", 60)
    result = []
    with sheets._sheets_lock:  # simulate a slow save in progress
        thread = threading.Thread(target=lambda: result.append(sheets.get_products()))
        thread.start()
        thread.join(timeout=2)
    assert result == [[{"ID": 1}]]
