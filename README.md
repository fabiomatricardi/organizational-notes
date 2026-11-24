# Organizational notes

A note-taking and follow-up system for an instrumentation & control discipline superintendent on an FLNG project under construction: **one A4 register on the desk, one printed kick-off grid, a Telegram inbox, and a local desktop app that keeps the register honest.**

Status: **v1.1** — 2026-11-20. Single user, local SQLite, no cloud required.

---

## The problem this solves

At 20 people you can hold the open loops in your head. At 100 (June 2027) you cannot. The failure is not laziness, it is architecture:

1. **Capture is unscoped** — notes spread over pages, so retrieval fails, not writing.
2. **Registration is transcription** — notes exist but never reach the app, because the app needs a laptop and 20 quiet minutes.
3. **Follow-up has no register** — you chase from memory. The app's own history shows the symptom: 303 entries, 4 open items.

The system separates those three jobs into three artefacts, each with one job.

## The 60-second method

**Capture** in five seconds on the phone (Telegram bot → Inbox).
**Keep one page that is always true**: the A4 *OPEN sheet* — commitments on the left, people on the right — rewritten every Monday, only live items crossing over.
**Register** for 20 minutes at 16:30: new commitments (owner + next check), closures, one 5-line day LOG, and the nudges sent *before* the laptop closes.
**Close the week** on Friday in 15 minutes: the report is generated from the register, not reconstructed from memory.

Marks: `•` fact · `→` my action · `⇒` their action + name + date · `?` waiting · `!` risk · `✓` closed · `@name` person.

> Acceptance test: **Friday 13:00, zero report bullets reconstructed from memory.**

## Quick start

1. Read [`docs/00-overview.md`](docs/00-overview.md) and [`docs/01-method.md`](docs/01-method.md).
2. Build the week: `.venv\Scripts\python.exe tools\build_week_pack.py` — one **OPEN sheet** (A4 landscape) and **five pre-dated Kick-off grids** (A4 portrait), names already printed. The `.html` versions let you change the team list once.
3. Start the app: `run-dev.bat` (dev) or `run-build.bat` then `run-prod.bat` (`.exe`). It opens on `http://localhost:8855`.
4. Set the Telegram bot token in **Settings → Telegram Capture** — see [`docs/07-telegram-setup.md`](docs/07-telegram-setup.md).
5. Follow week 1 of [`docs/03-first-two-weeks.md`](docs/03-first-two-weeks.md). Do not skip to week 2.

## The app in one table

| Screen | Job |
|---|---|
| **Inbox** | Telegram text and whiteboard photos waiting to be triaged into entries |
| **Today** | today's entries, everything due/stale, one-line quick add |
| **Follow-up** | all open commitments by owner, with overdue / stale / no-owner flags, nudges, handover export |
| **Log Timeline** | the searchable history, editable including owner / next check / area |
| **New Entry** | structured entry with the same fields |
| **Tasks Board** | kanban: Pending → Assigned → Ongoing → Completed |
| **Analysis** | weekly report in the Commissioning Manager's format, plus overdue / next steps / patterns |
| **Chat** | ask questions over the log (BM25 retrieval, optional RAG) |
| **Compaction** | AI duplicate detection and merge, with automatic backup |
| **Settings** | port, LLM, Telegram, backup / restore / export |

## Repository map

```
backend/              FastAPI + SQLite (routers, services, schema, Telegram poller)
frontend/             Vue 3 + Vite (views, API client, styles)
data/                 runtime data: personal_log.db, backups/, conversations/, inbox/ (gitignored)
templates/            printable A4 sheets (html + pdf, plus the weekly pack)
reference/            personal_log.sample.db — a 302-entry sample, no live data
docs/                 the method, the app, the architecture, the operations manual
config.json           local config incl. API keys and bot token (gitignored)
config.example.json   the same shape, empty secrets
run-dev.bat           dev mode (Vite + uvicorn)
run-build.bat         build the standalone .exe (PyInstaller)
run-prod.bat          launch the built .exe
```

## Documentation

| Document | What it answers |
|---|---|
| [`docs/00-overview.md`](docs/00-overview.md) | Why three registers, how the pieces fit, glossary |
| [`docs/01-method.md`](docs/01-method.md) | The daily and weekly method, the seven rules |
| [`docs/02-legend-and-examples.md`](docs/02-legend-and-examples.md) | The marks, with the whiteboards rewritten line by line |
| [`docs/03-first-two-weeks.md`](docs/03-first-two-weeks.md) | Setup and a day-by-day rollout, plus recovery rules |
| [`docs/04-app-guide.md`](docs/04-app-guide.md) | Every screen, the 16:30 ritual, weekly report, handover |
| [`docs/05-architecture.md`](docs/05-architecture.md) | Stack, modules, startup, Telegram poller, frozen vs dev |
| [`docs/06-data-model.md`](docs/06-data-model.md) | Tables, columns, statuses, migrations, mark → row mapping |
| [`docs/07-telegram-setup.md`](docs/07-telegram-setup.md) | BotFather to first captured line, in 10 minutes |
| [`docs/08-operations.md`](docs/08-operations.md) | Run, build, backup, restore, publish, troubleshoot |
| [`docs/09-scaling-to-100.md`](docs/09-scaling-to-100.md) | What changes when the team is 100 |
| [`docs/decisions.md`](docs/decisions.md) | The six design decisions and what was rejected |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed, when |
| [`ROADMAP.md`](ROADMAP.md) | Now / next / later |

### Print-ready A4

| Document | File |
|---|---|
| **How it works** — pin sheet + the three questions | [`docs/print/00-how-it-works.pdf`](docs/print/00-how-it-works.pdf) |
| Legend and worked examples | [`docs/print/02-legend-and-examples.pdf`](docs/print/02-legend-and-examples.pdf) |
| First two weeks, step by step | [`docs/print/03-first-two-weeks.pdf`](docs/print/03-first-two-weeks.pdf) |

Black, white and grey only; A4; no dependencies. Rebuild after editing the Markdown with `python tools/build_print.py` (Edge is used headless for the PDF).

## Data, secrets, backup

- **`data/personal_log.db`** — the only source of truth. SQLite, WAL mode. Gitignored.
- **`config.json`** — holds LLM API keys and the Telegram bot token. Gitignored; `config.example.json` is committed.
- **Backup** — Settings → *Backup Database*, and automatic backups in `data/backups/` before any AI merge.
- **Public viewer** — separate repository (`20261007.personalDB_online`) publishes an **encrypted** copy of the DB to GitHub Pages. The repo is public; the data is behind a password. The plaintext DB is never published.

## Stack

Python 3.12+, FastAPI, aiosqlite, httpx · Vue 3, Vite, PrimeIcons · PyInstaller for the standalone build.

## License

MIT (see the upstream app); internal notes © Fabio Matricardi.
