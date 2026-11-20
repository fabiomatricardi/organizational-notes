# 05 — Architecture

**Audience:** whoever changes the code next (including you in six months).
**Last updated:** 2026-11-20.

---

## Runtime picture

```
 iPhone ── Telegram cloud ──► getUpdates (long poll) ──┐
                                                       │
 Browser (localhost:8855) ── HTTP ──► FastAPI ─────────┼──► SQLite  data/personal_log.db
        ▲                              │              │
        └──── SPA from frontend/dist ──┘              │
                                                       └──► data/inbox/YYYY-MM/*.jpg
                                                       
 FastAPI ── HTTPS ──► LLM endpoint (reports, chat, compaction)
```

Three processes at most: the browser, the Python backend, and (dev only) Vite. Nothing is exposed to the network; the server binds `127.0.0.1`.

---

## Module map

```
backend/
  main.py                 app factory, lifespan, port selection, SPA catch-all
  database.py             connection, schema, guarded migrations, data dir resolution
  models.py               Pydantic request/response models
  routers/
    entries.py            CRUD + /follow-up + /today + /stats/dashboard
    inbox.py              Telegram inbox list / convert / attach / discard / photo
    analysis.py           report generation + report CRUD + week helpers
    import_export.py      Excel, DB backup/restore, handover export
    settings.py           config read/write
    tags.py               tags CRUD
    chat.py               conversations, RAG search, send
    compaction.py         duplicate detection and merge
  services/
    entries.py            all entry SQL + derived open-item flags
    telegram.py           long-poll loop, photo download, meta offset
    llm_service.py        prompts, primary/fallback calls
    bm25_search.py        pure-Python retrieval for chat
    chat_service.py       conversation persistence
    compaction.py         duplicate grouping and merge logic
    excel_parser.py       .xlsx import/export
    database.py           backup/restore/info
    config.py             defaults, deep merge, save
    tags.py               tag queries

frontend/src/
  App.vue                 view switch (no router); sidebar + one component
  components/             Dashboard, Today, Inbox, FollowUp, LogTimeline, NewEntry,
                          TasksBoard, Analysis, Chat, Settings, Compaction
  composables/useApi.js   axios wrapper, one function per endpoint
  styles/main.css         dark theme, shared classes
```

There is no ORM and no migration framework. SQL lives in the services; the schema is additive.

---

## Startup sequence

1. `main.py` resolves `APP_BASE_DIR` — project root in dev, the exe directory when frozen (`sys._MEIPASS` for bundled read-only assets).
2. Logging to `personallog.log`; `data/` created if missing.
3. FastAPI `lifespan`:
   - `init_db()` — `CREATE TABLE IF NOT EXISTS`, then `ALTER TABLE` for any missing column, then indexes (order matters: new-column indexes are created **after** the columns exist), then commit.
   - `start_poller()` — Telegram, only if enabled and a token is configured.
   - open the browser at the configured port.
4. Routers registered; the SPA catch-all `/{full_path}` serves `frontend/dist`.
5. On shutdown: `stop_poller()`.

Port selection: `config.app.port`, then a fixed fallback list, testing with `socket.bind`. If it changes, the browser still opens the right port because `app.state.port` is set before serving.

---

## Request flows

**Capture (Telegram).** `getUpdates(offset, timeout=25)` → for each message: filter `chat_id` against `allowed_chat_ids`; text → `inbox(kind=text)`; photo → `getFile` → download to `data/inbox/YYYY-MM/<message_id>.jpg` → `inbox(kind=photo, body=caption, file_path=...)`. The `update_id + 1` is written to `meta.telegram_offset` after the row commits, so a restart neither duplicates nor skips.

**Triage.** `POST /api/inbox/{id}/convert` → `entries.create_entry(...)` → delete the inbox row (or mark `processed=1` and store `entry_id`). The mark parsing is client-side in `Inbox.vue`; the server accepts explicit fields.

**Follow-up.** `GET /api/entries/follow-up` → `entries.get_open_items()` (one query, `type IN (TODO,TASK) AND status != COMPLETED`) → flags computed in Python (`age_days`, `overdue`, `stale`, `orphan`, `waiting`) → grouped and sorted. Nothing derived is stored, so nothing goes stale in the database.

**Weekly report.** `POST /api/analysis/generate {report_type: weekly, year, week_number}` → filter entries to the ISO week → fetch the full open register → build the prompt (entries + open + stale) → LLM → save to `analysis_reports` → return markdown.

**Handover.** `GET /api/data/export/handover` → open register grouped by owner + overdue list + waiting + risks containing `!` in the last N days → markdown, saved as `analysis_reports(report_type='handover')`.

---

## Frontend

- One `App.vue` with `currentView` and `v-if` blocks; no vue-router. Adding a screen is: a component, a sidebar item, a line in `App.vue`.
- All HTTP through `composables/useApi.js`. `baseURL: '/api'`, so the Vite proxy (`config.json` port) and the packaged build behave identically.
- The sidebar polls `/api/inbox/count` every 60 seconds for the badge.
- Styling is a small shared class set in `main.css` (`card`, `toolbar`, `row-item`, `badge`, `count-chip`, `split`); no component library beyond PrimeIcons.

---

## Frozen vs dev

| | Dev (`run-dev.bat`) | Frozen (`dist/PersonalLogManager.exe`) |
|---|---|---|
| Code | live files | bundled into `_MEIPASS` |
| Frontend | Vite on 5173, proxy to backend | `frontend/dist` served by FastAPI |
| Data | `./data` next to the project | `data` next to the exe |
| Config | project `config.json` | `config.json` copied next to the exe at build |
| Python changes | immediate | require `run-build.bat` |

`build.py` bundles `frontend/dist` and `config.json`, collects the `backend.*` packages and the hidden imports uvicorn needs, and copies the config next to the exe.

---

## Constraints and the reasoning

- **SQLite, single file.** One user, one machine, tens of thousands of rows at most. No server to maintain; trivial backup.
- **No auth.** Bound to loopback. The public viewer is a separate artefact with its own encryption.
- **Additive schema.** New columns only, applied on startup. Old rows stay valid; `owner` empty is a legitimate state (flagged, not fatal).
- **Derived flags are computed.** `overdue`/`stale`/`orphan` depend on *today*; storing them would require a nightly job and would rot.
- **No multi-user.** Leads do not log; the app models one person's commitments.

## Security notes

- `config.json` holds the LLM keys and the Telegram token — gitignored, never published.
- Telegram and the LLM are the only outbound calls; both receive project text. Assume the cloud sees what you send.
- The public viewer repository contains only an AES-256-GCM encrypted blob; the password is the boundary.
- The backend has no CSRF protection and no auth: do not expose the port beyond `127.0.0.1`.

## Known failure modes

| Symptom | Cause / fix |
|---|---|
| `no such column: owner` on first start | index created before migration — already fixed; keep the order in `init_db` |
| Inbox empty, log says `invalid bot token (401)` | wrong/revoked token; re-paste, restart |
| Port changes unexpectedly | configured port busy; check `personallog.log` |
| Blank page, 404 on assets | `frontend/dist` missing; run `npm run build` |
| Frozen exe lacks a change | rebuild; `_MEIPASS` is a snapshot |
| DB copied but data missing | WAL not checkpointed; copy with the app closed |
