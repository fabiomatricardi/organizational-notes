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
