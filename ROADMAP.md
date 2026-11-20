# Roadmap

Ordered by value, not by ambition. Everything here is optional: the paper half works without any of it.

## Now (next 2 weeks)

- [ ] Run week 1 and week 2 of the method ([`docs/03-first-two-weeks.md`](docs/03-first-two-weeks.md)); do not skip to week 2.
- [ ] Give the 4 legacy open items an owner and a next check in **Follow-up**.
- [ ] Wire the Telegram bot ([`docs/07-telegram-setup.md`](docs/07-telegram-setup.md)) and capture for one full week.
- [ ] Print the A4 register on Monday, once. If it is not on the desk by Tuesday, the method is not running.

## Next (4–8 weeks)

- [ ] **Public viewer: Open register tab.** The viewer repo (`20261007.personalDB_online`) shows the timeline; add a tab that lists open items by owner, overdue first. This is what makes the encrypted copy useful from home.
- [ ] **Weekly report check.** Compare the generated report with the hand-written one for three Fridays; if a section is empty, the capture is empty.
- [ ] **Publish script hardening.** Point `publish.ps1` at `data/personal_log.db` and checkpoint the WAL before encrypting.
- [ ] **First handover by export.** Before the next 15-day rotation, generate the handover from Follow-up and hand it to the back-to-back.

## Later (before June 2027)

- [ ] **Kick-off at 100.** Replace the single round table with area stand-ups (AIR / FIR / ICSS / PTW) that send a written 5-line update by 07:00.
- [ ] **Area boards.** Aggregate 6 area registers on the A4 instead of 100 individuals.
- [ ] **Monthly skip-levels.** Draw names from the blank rows of the kick-off grid — the people who never surface.
- [ ] **Board photo OCR (optional).** Let the LLM extract `⇒` and `!` lines from the whiteboard photo into the inbox. Only after the grammar is stable.
- [ ] **Stale-report nudge.** Friday 12:00: warn if fewer than N entries exist this week (catches the 17-day gap).
- [ ] **Area dashboards** in the app (read-only) if the leads ever need to see them.

## Explicit non-goals

- Multi-user, authentication, sync. This is one person's instrument; the leads do not log in.
- A mobile app. Telegram is the mobile app.
- Replacing Outlook, Teams or the completion system. Notes reference them; they do not compete.

## Ideas parked

- `owner` suggestions from history (autocomplete in the forms).
- Recurring commitments (weekly reports, alignment meetings) auto-created each Monday.
- Export the register as `.xlsx` for the weekly pack.
