import logging

import bot


def test_http_loggers_never_log_request_urls():
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.NOTSET)
    bot.setup_logging()
    for name in ("httpx", "httpcore"):
        assert logging.getLogger(name).getEffectiveLevel() >= logging.WARNING


def test_token_is_not_written_to_logs(caplog):
    bot.setup_logging()
    caplog.set_level(logging.INFO)
    logging.getLogger("httpx").info('HTTP Request: POST https://api.telegram.org/bot123:SECRET/getMe "HTTP/1.1 200 OK"')
    assert "SECRET" not in caplog.text
