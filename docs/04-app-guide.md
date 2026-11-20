# 04 — App guide

**Audience:** the operator (you).
**Last updated:** 2026-11-20.

The app is a local web application: a FastAPI backend and a Vue 3 frontend, serving one user on `localhost`. No account, no sync, no cloud.

---

## Start it

| Mode | Command | What happens |
|---|---|---|
| Dev | `run-dev.bat` | starts the backend and the Vite dev server; open `http://localhost:5173` |
| Prod (exe) | `run-build.bat`, then `run-prod.bat` | builds `dist/PersonalLogManager.exe` and launches it; browser opens on the configured port |
| Manual backend | `.venv\Scripts\python.exe -m backend.main` | serves the built frontend on `http://localhost:8855` |

Port comes from `config.json → app.port` (8855 here); if busy, the app tries 8001, 8002, 8003, 5000, 3000, 18080, 28080. The Vite dev proxy reads the same file, so dev and prod always agree.

Log file: `personallog.log` at the project root. Database: `data/personal_log.db`.

---

## Screens and what they are for

### Inbox

Everything captured from Telegram lands here: text, and photos with their caption. Nothing is parsed until you triage.

1. Click an item. The line is pre-filled, and the mark suggests the type:
   - `⇒ Name: …` → **TASK**, owner `Name`, status ASSIGNED
   - `→ …` → **TODO**, owner `me`, status PENDING
   - `? …` → **TODO**, status PENDING, follow-up `waiting: `
   - `•` / `-` / `*` → **LOG**
2. Adjust: owner, area, next check, note. Convert.
3. The item leaves the inbox and becomes a row in the log with `owner` and `next_check`.

Discard is for noise only — a discarded line is lost on purpose.

### Today

The 16:30 screen.

- **Quick add** — one line, mark first. `Enter` saves. Type, owner (for TODO/TASK), next check, area. This is how paper lines enter the app.
- **Due now** — every open item that is due, overdue or stale. `+3d` snoozes; `Done` closes.
- **Written today** — what you already registered, so you do not double-enter.

### Follow-up

The register on screen.

- Four counters: **open / overdue / stale / no owner**, clickable as filters. Plus *waiting*.
- Groups by owner, sorted by urgency (overdue → stale → due date → age).
- Per item: `+3d`, **Nudge** (copies `#123 — item — due date — status?`), **Done**.
- Per owner: **Copy N nudge(s)** — the whole list in one paste for a Teams message.
- **Copy handover** — markdown of every open item grouped by owner, with risks from the last 7 days and a "notes for my back-to-back" section. It is also saved in `analysis_reports` as type `handover`.

Definitions: **overdue** = `eta` in the past; **stale** = `next_check` in the past, or no next check and older than 7 days; **orphan** = no owner. An open item without an owner is always a defect.

### Log Timeline

The searchable history. Click any row to edit: activity, type, status, ETA, **owner**, **next check**, **area**, follow-up, delete. Filters: free text (activity, follow-up, owner) and type.

### New Entry

The same fields as the timeline, plus *Load from file* (`.txt`/`.md`) and a reference to another entry. Use it for a structured entry when the quick add is not enough (e.g. pasting meeting minutes as one LOG).

### Tasks Board

Kanban over TODO + TASK by status: Pending → Assigned → Ongoing → Completed. Useful for a weekly sweep; the Follow-up view is the daily instrument.

### Analysis

Generates markdown reports and stores them in `analysis_reports`:

| Type | Content |
|---|---|
| **weekly** | the report for the Commissioning Manager, in his format (see below) |
| comprehensive | everything, with statistics and pending items |
| overdue | tasks past their ETA |
| next_steps | suggestions from the last 10 entries |
| patterns | recurring themes across the last 100 entries |

**The weekly report prompt** (in `backend/services/llm_service.py`) produces exactly:

```
## WEEK n REPORT
### Key Activities
### Tasks Progress
### Critical path
### Week n+1 Outlook
### Resourcing & people
```

It is fed the week's entries **plus every open commitment and every stale item**, so the "Critical path" section is derived from the register, not from prose. Rules in the prompt: use tag numbers exactly, never invent owners or dates, write "no update" instead of padding.

Choose the week with the year/week selector or an explicit date range. The report is saved and can be downloaded as markdown.

### Chat and Compaction

- **Chat** — ask questions over the log. BM25 retrieval (text or date range), toggle RAG, select which entries to include. Conversations are saved as markdown in `data/conversations/`.
- **Compaction** — AI duplicate detection and merge. A database backup is taken before every merge; merging cannot be undone.

### Settings

- **Database** — import Excel, export Excel, backup (download `.db`), restore (upload `.db`).
- **Application** — server port (restart required).
- **Telegram Capture** — enable, bot token, allowed chat IDs, *Test bot*. See [`07-telegram-setup.md`](07-telegram-setup.md).
- **Chat** — RAG top-K.
- **LLM** — primary and fallback endpoints, keys, models, SSL verification, CA bundle, Test connection. The default config is set up for a Gemini-compatible endpoint with SSL verification off (corporate inspection).

---

## The daily ritual, mapped to screens

| Time | Screen | Action |
|---|---|---|
| 07:25 | paper | move `⇒`/`→`/`?`/`!` from the grid to the A4 |
| 12:45 | paper | cross off, add |
| 16:30 | **Inbox** | triage captures; 2–4 minutes |
| 16:30 | **Today** | quick-add the day's paper lines; close what closed; `+3d` what slipped |
| 16:30 | **Follow-up** | send the nudges for anything due today **now**; copy the owner batch into Teams |
| Fri 13:00 | **Analysis → weekly** | generate, adjust, save; then the 14:00 meeting needs nothing else |
| Before leave | **Follow-up → Copy handover** | paste into the handover note for the back-to-back |

The 20 minutes is a ceiling, not a target. If it takes longer, the day's capture was too coarse — fix the lines, not the speed.

---

## Data, backup, restore

| Thing | Where |
|---|---|
| Database | `data/personal_log.db` (WAL: `-wal`, `-shm`) |
| Automatic backups | `data/backups/` (before AI merges; manual pre-migration copies) |
| Telegram photos | `data/inbox/YYYY-MM/` |
| Chat transcripts | `data/conversations/*.md` |
| Config + secrets | `config.json` (gitignored) |

Backup before any upgrade: Settings → *Backup Database*, or copy `data/personal_log.db` with the app closed. A WAL database copied while the app is writing can be stale — close the app, or checkpoint first (see [`08-operations.md`](08-operations.md)).

Restore is destructive: it replaces the database. Export first if in doubt.

---

## Known constraints

- One user. No authentication; the backend binds `127.0.0.1`.
- The exe does not pick up Python changes: rebuild after editing `backend/` or `frontend/src/`.
- The database grows slowly (303 entries in four months); compaction is for duplicates, not for size.
- The app sends nothing anywhere except the configured LLM endpoint and, if enabled, Telegram.
