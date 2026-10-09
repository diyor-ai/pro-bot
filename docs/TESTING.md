# Manual test checklist (real Telegram + test Google Sheet)

## Preparation
1. Create a **separate** test spreadsheet and a **separate** test bot (BotFather). Do not test on production data.
2. Share the sheet with the service account `client_email` (Editor).
3. First worksheet columns: `ID, Nomi, Narxi, Kategoriya, Tavsif, Rasm_URL, Mavjud`. Add rows:
   - A: with a valid image URL, category `Krossovka`, `Mavjud` = `5`
   - B: no image, category `Aksessuar`, `Mavjud` = `TRUE`, price written as `150 000`
   - C: `Mavjud` = `FALSE` (must stay hidden)
   - D: `Mavjud` = `0` (must stay hidden)
   - E: name containing `_` and `*` (for example `Air_Max *Pro*`)
4. `.env`: set `TELEGRAM_TOKEN`, `SHEET_NAME`, `ADMIN_CHAT_ID` and `ADMIN_IDS` to your own account (and a second account that is NOT an admin).
5. `pytest` passes, then `python bot.py` starts and logs without errors.

## Customer flow
- [ ] `/start` shows the language buttons; pick each of uz / ru / en, menu text changes language
- [ ] "Products" lists categories (one button per row); products C and D are not shown anywhere
- [ ] Open product A (photo): photo with caption appears
- [ ] On the photo message press "No/Orqaga": returns to the menu without an error (photo edit fix)
- [ ] Open product A again, press "Yes": the bot asks for your name (no error)
- [ ] Product B shows price `150 000 so'm`; product E shows its name literally with `_` and `*`, no formatting error
- [ ] Search: exact name, a typo (`nikee`), a category word, and nonsense (shows "not found")
- [ ] Order: name with `_ * < >` characters → phone: invalid values (`123`, `+1202…`) are rejected; `901234567` becomes `+998901234567`; the "share phone" button also works
- [ ] Share a contact when NOT ordering: the bot ignores it, no crash
- [ ] Address → confirmation message shows all data correctly (special characters intact)
- [ ] Cancel works and returns to the menu
- [ ] Confirm: user sees "order accepted"; sheet `Buyurtmalar` has a new row (ID, date, product, price as a number, **Kategoriya filled**, Status `Yangi`); `Users` has a row (count 1)
- [ ] Order again as the same user: `Users` count becomes 2 and a new order gets ID +1 (no duplicate)

## Failure handling
- [ ] Temporarily unshare the sheet (or break `SHEET_NAME`), try to confirm an order: user gets an error alert and the order is NOT reported as accepted; the log shows the exception. Restore access afterwards.

## Admin
- [ ] Non-admin account: `/admin` → "Access denied"
- [ ] Admin chat received the new-order message with `#ID`; press "Jarayonda", "Yo'lda", "Yetkazildi": sheet Status changes each time and the bot answers "Holat yangilandi!"
- [ ] `/admin` → Orders: lists only `Yangi` orders, buttons work there too
- [ ] `/admin` → Statistics: totals match the sheet (add a row with price `150 000` text; stats must not collapse to zeros)
- [ ] Non-admin cannot trigger status changes (forward the admin message or use a group chat if `ADMIN_CHAT_ID` is a group)

## Broadcast (use only test accounts)
- [ ] `/admin` → Broadcast → type a message → preview with Send / Cancel
- [ ] Cancel: nothing is sent
- [ ] Send: every customer in `Users` receives it; admin gets "Yuborildi: N / Xato: M"
- [ ] Add a fake `User_ID` (e.g. `1`) to `Users`: it is counted as failed, the others still receive the message
- [ ] Block the bot from a test account: it counts as failed, no crash

## Restart / misc
- [ ] Restart the bot mid-order: next message restarts with `/start` language selection (known limitation)
- [ ] Edit a price in the sheet: the new price shows within `CACHE_TTL` seconds
- [ ] Check logs: errors appear with tracebacks (logging works), no silent failures
