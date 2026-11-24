# 08 — Operations manual

**Audience:** the operator, and whoever rebuilds this machine.
**Last updated:** 2026-11-20.

---

## Prerequisites

| Need | For | Check |
|---|---|---|
| `uv` | Python env in dev | `uv --version` |
| Node.js 20+ | frontend dev and build | `node --version`, `npm.cmd --version` |
| A browser | the UI | any |
| PyInstaller (via uv) | the standalone exe | `run-build.bat` installs it |

On this machine `npm` must be invoked as `npm.cmd` in PowerShell (execution policy blocks `npm.ps1`).

## First setup from a fresh clone

```powershell
cd C:\myAI\fabio-notes\better_noteTaking
uv sync
npm.cmd install --prefix frontend
npm.cmd run build --prefix frontend
Copy-Item config.example.json config.json
# then fill in the LLM keys and (optionally) the Telegram token
```

`data/` is gitignored, so a fresh clone has no database: the app creates `data/personal_log.db` on first start with the full schema. Copy a backup into `data/` to restore history.

## Run

| Mode | Command | Notes |
|---|---|---|
| Dev | `run-dev.bat` | Vite on 5173 + backend; hot reload |
| Prod exe | `run-build.bat` → `run-prod.bat` | `dist/PersonalLogManager.exe` |
| Backend only | `.venv\Scripts\python.exe -m backend.main` | serves `frontend/dist` |

Port: `config.json → app.port` (8855). Fallbacks: 8001, 8002, 8003, 5000, 3000, 18080, 28080. Changing it needs a restart; the Settings UI warns.

## Build the exe

```powershell
.\run-build.bat
```
What it does: deletes `build/` and `dist/`, runs `npm install` + `npm run build`, then PyInstaller `--onefile --noconsole`, bundling `frontend/dist` and `config.json`, and copies the config next to the exe.

Notes:
- Rebuild after **any** change to `backend/` or `frontend/src/`. The frozen app bundles a snapshot.
- First launch of a fresh exe may be slow (unpacking) and Windows Defender may scan it; `exclude-defender.bat` (admin) helps.
- The exe writes `data/` and `personallog.log` next to itself, not in the source tree. Keep that in mind when backing up.

## Build the printable A4 documents

The two reference documents have a print pipeline (no external dependencies):

```powershell
.venv\Scripts\python.exe tools\build_print.py            # both
.venv\Scripts\python.exe tools\build_print.py --only 02  # one
.venv\Scripts\python.exe tools\build_print.py --no-pdf   # HTML only
```

- Sources: `docs/00-how-it-works.md` (one page), `docs/02-legend-and-examples.md`, `docs/03-first-two-weeks.md`.
- Style: `tools/print.css` (black/white/grey, A4, fixed margins, page-break rules).
- Output: `docs/print/<name>.html` and `.pdf`.
- PDF is produced by Microsoft Edge in headless mode (`--print-to-pdf`). If Edge is busy or hangs, the script retries once with a fresh profile; close stray headless Edge processes if it still fails.
- Page breaks are tuned per document in the `DOCS` list (`breaks`, `notes`). If you change the Markdown, re-render and check the last page: a notes block that no longer fits will move to its own page.

## Build the weekly paper pack

One command produces the week's paper, pre-dated, with the names already printed:

```powershell
.venv\Scripts\python.exe tools\build_week_pack.py
.venv\Scripts\python.exe tools\build_week_pack.py --week 50 --monday 2026-12-07
```

- Output: `templates/03-OPEN-SHEET-A4-wk<NN>.pdf` (1 page, landscape) and `templates/04-KICKOFF-GRID-A4-wk<NN>.pdf` (5 pages, portrait, Monday–Friday).
- The team list lives in `PEOPLE` at the top of the script: `("Name", "Area")`, one canonical spelling per person. Vendors are owners, never rows.
- The date, day name and week number come from `--monday`; it must be a Monday.
- `--no-pdf` writes the HTML only.
- `TODAY'S 3` is left blank on purpose: write the day's fixed points on the printed page, then complete it at the kick-off. That box is the calendar.
- The blank templates (`03-OPEN-SHEET-A4.pdf`, `04-KICKOFF-GRID-A4.pdf`) are generated from the same HTML with an empty name list; regenerate them with Edge if you edit the templates by hand.

## Build the tutorial (cards and video)

The written tutorial is [`10-scenarios.md`](10-scenarios.md) — six situations from one week. It is built with the other print editions:

```powershell
.venv\Scripts\python.exe tools\build_print.py --only 10
```

The video is the same six scenes, narrated, with one clip per beat:

```powershell
cd video
npm.cmd install
npm.cmd run audio       # regenerate public/audio/*.mp3 (Edge TTS, en-US-BrianNeural)
npm.cmd run render      # -> video/out/tutorial.mp4
npm.cmd run studio      # live editor, to change timing
```

- **Content lives in `video/src/script.ts`** (what is on screen) and **`video/src/narration.json`** (what is said). Edit those, not `video/src/Video.tsx`.
- Scene durations derive from the number of steps, so adding a step adds time instead of desynchronising the picture.
- `video/tools/build_audio.py` measures every clip against its beat and fails if a line would overlap the next one. Shorten the line, or widen `TIMING` in `script.ts`.
- The 35 MP3s (0.8 MB) are committed, so a render works offline; re-run `npm.cmd run audio` only after changing the words.
- No API key and no account: Edge TTS is the same Read Aloud service the Edge browser uses. The script calls `uvx --from edge-tts`, and falls back to `python -m edge_tts` when uv is absent.
- **Rendering uses the installed Chrome, not Remotion's download.** The corporate TLS proxy breaks the browser download (`unable to get local issuer certificate`); the npm scripts already pass `--browser-executable`.
- `video/out/` is gitignored. Publish the MP4 as a release asset or copy it to a stick; do not commit it.
- Fonts are Arial with a `Segoe UI Symbol` fallback, needed for `⇒`, `✓`, `✗`. After any font change, render one still before the full video.

## Configuration

`config.json` — copied from `config.example.json`, never committed.

| Key | Meaning |
|---|---|
| `app.port` | HTTP port |
| `llm.primary` / `llm.fallback` | OpenAI-compatible endpoints (`base_url`, `api_key`, `model`, `timeout`, `max_tokens`, `enabled`) |
| `llm.verify_ssl`, `llm.ca_bundle` | corporate TLS inspection: `false`, or point at the corporate CA |
| `llm.analysis.weekly_report_day` | informational |
| `chat.top_k` | BM25 results sent as context |
| `telegram.enabled` | start the poller |
| `telegram.bot_token` | BotFather token |
| `telegram.allowed_chat_ids` | list of chat ids; empty = accept any (single user) |
| `telegram.poll_timeout` | long-poll seconds (25 is fine) |

The Settings UI writes the same file; editing it by hand is fine, but restart after changes to `app.port` or `telegram`.

## Backup

Three levels, use the first daily:

1. **Settings → Backup Database** — downloads a `.db`. Put it outside the repo.
2. **Copy `data/personal_log.db`** with the app closed. If the app must stay open, checkpoint first:
   ```powershell
   .venv\Scripts\python.exe -c "import sqlite3;c=sqlite3.connect(r'data/personal_log.db');print(c.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone());c.close()"
   ```
3. **`data/backups/`** — automatic before AI merges and manual pre-migration copies (e.g. `pre-notekeeping-*.db`).

Restore: Settings → *Restore Database* (destructive) or copy the file over with the app closed.

## Export

- **Excel** — Settings → *Export Excel* (all entries; new columns are not included in the sheet).
- **Markdown** — weekly reports and the handover are markdown; download from Analysis / copy from Follow-up.
- **Weekly report** — Analysis → weekly, choose week, generate, download.

## Publish the encrypted copy (GitHub Pages)

Separate repository: `C:\myAI\20261007.personalDB_online` → <https://fabiomatricardi.github.io/fmat-log-viewer/>.

```powershell
cd C:\myAI\20261007.personalDB_online
.\scripts\publish.ps1 -DbPath C:\myAI\fabio-notes\better_noteTaking\data\personal_log.db
```

- The script asks for the encryption password (never stored), encrypts to `data/log.enc`, commits and pushes. Pages republishes in a few minutes.
- The repository is public; **only the encrypted blob** is committed. The plaintext DB stays local.
- Close the app or checkpoint the WAL first (see above), otherwise the published copy can be stale.
- Do not rotate the encryption password without recording it: the published blob is unrecoverable without it.

## Upgrade procedure

1. Backup the database.
2. Close the app.
3. Pull the repository.
4. `uv sync` (if `pyproject.toml`/`uv.lock` changed) and `npm.cmd install --prefix frontend` + `npm.cmd run build` (if the frontend changed).
5. Start; the startup migration adds any new columns.
6. Open Follow-up and confirm the counters match expectation.

## Troubleshooting

| Symptom | Check | Fix |
|---|---|---|
| Browser opens a blank page | `personallog.log`; is `frontend/dist` present? | `npm.cmd run build --prefix frontend` |
| Port not the configured one | log line "port unavailable" | free the port or change `app.port` |
| `SSL: CERTIFICATE_VERIFY_FAILED` on reports | corporate inspection | `llm.verify_ssl=false` or set `ca_bundle` |
| Reports fail with 401/429 | key/quota | test in Settings, swap primary/fallback |
| Inbox empty | Settings → Telegram → *Test bot* | token, `enabled`, restart |
| `database is locked` | two app instances | close both; one process only |
| Missing recent data in a copy | WAL | checkpoint or copy with the app closed |
| Frozen app ignores a change | bundle snapshot | rebuild |
| Badge stays after triage | 60 s poll interval | wait, or refresh |

Log: `personallog.log` at the project root (or next to the exe). It is the first place to look for Telegram and LLM errors.

## Health check (30 seconds, monthly)

```powershell
# entry count and open items, without opening the UI
.venv\Scripts\python.exe -c "import sqlite3;c=sqlite3.connect(r'data/personal_log.db');print('entries',c.execute('select count(*) from log_entries').fetchone()[0]);print('open',c.execute(\"select count(*) from log_entries where type in ('TODO','TASK') and status!='COMPLETED'\").fetchone()[0]);print('no owner',c.execute(\"select count(*) from log_entries where type in ('TODO','TASK') and status!='COMPLETED' and (owner is null or owner='')\").fetchone()[0])"
```

Expected: entries rising, open items in the tens, **no unowned items**. The last number is the one that matters.

## Secrets checklist

- `config.json` is gitignored — verify with `git check-ignore -v config.json` after any `.gitignore` change.
- The Telegram token and LLM keys never appear in screenshots or commits.
- The published `.enc` file is safe to be public only because of the password; treat the password as the secret.
