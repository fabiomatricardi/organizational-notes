# Changelog

All notable changes to this project. Dates are local (KST).

## [1.4.2] — 2026-11-25

### Added
- `docs/01-method.md`: **Erasing, and running out of lines** — what may be erased on the **OPEN sheet** (mistakes, duplicates, non-commitments, closures after Friday), what may not (open lines, target changes), and what to do when the page runs out mid-week.

## [1.4.1] — 2026-11-25

### Added
- **Narration.** Microsoft Edge TTS, voice `en-US-BrianNeural`, one clip per beat (35 clips, 0.8 MB) in `video/public/audio/`.
- `video/src/narration.json` — the spoken script, separate from the on-screen text.
- `video/tools/build_audio.py` — regenerates the clips and fails when a line would overlap the next beat.

### Changed
- The video is narrated, not silent: now about 3:27. Scene tails were extended to fit the closing line of each scene.
- `docs/10-scenarios.md`, `docs/08-operations.md` and `video/README.md` no longer describe the video as silent; the audio build is documented.
- `video/package.json` gains `npm.cmd run audio`.

## [1.4.0] — 2026-11-24

### Added
- **The tutorial.** `docs/10-scenarios.md` — six situations from one week, one card per working day, with the print edition `docs/print/10-scenarios.pdf` (4 pages). It is the method at the moment it is needed, not another reference.
- **The video.** `video/` — the same six scenes as a silent 16:9 composition in Remotion 4 (`npm.cmd run render` → `video/out/tutorial.mp4`, about three minutes). Content lives in `video/src/script.ts`; scene durations derive from the script.
- **Ideas have a home.** `docs/01-method.md` gains "Where ideas go": no date and no owner → the back pages of the **Notebook**, with three fates on Friday (dead, `→` on the OPEN sheet, `ROADMAP.md`).
- Rule 11: an idea never touches the **OPEN sheet**.

### Changed
- `docs/01-method.md` — ten rules → **eleven**.
- `README.md` — quick start points at the tutorial; repository map, documentation table and print table updated; four artefacts instead of three, eleven rules instead of seven.
- `docs/08-operations.md` — how to build the cards and the video, including the corporate-proxy workaround (`--browser-executable`).
- `tools/build_print.py` — `DOCS` gains document `10`; print version 1.4.

### Notes
- Remotion's own browser download fails behind the TLS proxy (`unable to get local issuer certificate`); the npm scripts render with the installed Chrome.
- `video/out/` is gitignored — the MP4 is a build artefact, not source.

## [1.3.0] — 2026-11-24

### Added
- `tools/build_week_pack.py` — one command builds the week's paper: one **OPEN sheet** and **five pre-dated Kick-off grids**, with the names already printed. Output `templates/03-OPEN-SHEET-A4-wk<NN>.pdf` and `templates/04-KICKOFF-GRID-A4-wk<NN>.pdf`.
- `docs/01-method.md`: **Where each dated thing goes** (target / appointment / commitment / note) and **The five daily pages** — the pre-dated stack, and `TODAY'S 3` as the calendar.
- The first pack, week 49: `templates/03-OPEN-SHEET-A4-wk49.pdf`, `templates/04-KICKOFF-GRID-A4-wk49.pdf`.

### Changed
- `docs/01-method.md` now describes **four artefacts**: the Kick-off grid, the OPEN sheet, the Notebook and the phone inbox. The Notebook has a job again — appointments, decisions, the day's record, three lines at 16:30.
- Seven rules → **ten**: target changes are struck through with date and reason; one canonical name per person, printed not handwritten; the OPEN sheet follows the week, not the Monday morning.
- `WHAT THEY NEED FROM ME` is now documented as the debt list — ask it as *"what am I blocking?"*.
- OPEN sheet template: the ANCHORS block is now **Fixed this week** — four free lines plus the standing THU SHI / FRI 14:00 anchors.
- `docs/00-how-it-works.md` pin sheet updated to four artefacts and the pre-dated week. Still two A4 pages.
- `docs/03-first-two-weeks.md` and `docs/08-operations.md` describe the weekly pack instead of printing sheets one at a time.
- `learning/README.md` indexes all seven artefacts; `20261123_OPEN_sheet.jpg` renamed to `20261123_open_sheet.jpg`.

## [1.2.0] — 2026-11-23

### Added
- `docs/00-how-it-works.md` — the whole method on one page, plus a second page answering the three questions that always come up. Print-ready as [`docs/print/00-how-it-works.pdf`](docs/print/00-how-it-works.pdf).
- The one-pager is a separate layout in the print pipeline (`onepager` flag in `tools/build_print.py`): larger type, numbered steps, no colophon, and a compact legend strip. Page 1 is the poster; page 2 is set smaller as reference.

### Changed
- `docs/01-method.md` and `docs/03-first-two-weeks.md` now point to the one-pager as the entry point; the long documents are reference, not the daily tool.

### Note
- The app is unchanged. This release is the document set only; `VERSION` in the print pipeline tracks the documents.

## [1.1.0] — 2026-11-20

### Added
- Consolidated repository: the app, the method, the print templates and the reference database now live in one place.
- `docs/` set: overview, method, legend, rollout, app guide, architecture, data model, Telegram setup, operations, scaling, decision log.
- `templates/` with the A4 OPEN sheet and the A4 kick-off grid (HTML + PDF), both with a **Names** box that saves the team list in the browser.
- `reference/personal_log.sample.db` — 302-entry sample, no live data.
- `config.example.json` — the config shape with empty secrets.
- `docs/03-first-two-weeks.md`: a day-by-day rollout with recovery rules.
- Print pipeline (`tools/build_print.py` + `tools/print.css`) and print-ready A4 PDFs for the legend and the rollout: `docs/print/`.

### Changed
- Kick-off grid moved from A5 to **A4 portrait** (only A4 is available on site).
- `06-TELEGRAM-SETUP.md` now documents the 24-hour queue limit, photo captions and the `allowed_chat_ids` lock.
- Legend examples rewritten from the **20.11 whiteboard**, with corrected names (Aras, Seong, Chang, Anto) and `0-T?` documented as the cabinet-keys request.
- `.gitignore` now excludes all of `data/` except a placeholder, plus `.ruff_cache`.

## [1.0.0] — 2026-11-19

### Added
- **Inbox** — Telegram text/photo capture, stored in a new `inbox` table, triaged into entries from the UI.
- **Telegram long-polling** service (`backend/services/telegram.py`), configured in Settings, no public URL needed.
- **Today** view: today's entries, due/stale items, one-line quick add.
- **Follow-up** view: open commitments grouped by owner, with overdue / stale / orphan / waiting flags, copyable nudges, snooze and close, and a **handover export**.
- `owner`, `next_check` and `area` columns on `log_entries`, with guarded startup migrations.
- `meta` table for the Telegram offset (no duplicate imports after restart).
- Weekly report prompt rewritten to the Commissioning Manager's format: Key Activities / Tasks Progress / Critical path / Week outlook / Resourcing & people, fed with all open and stale commitments.
- Frontend: sidebar entries, inbox badge, dashboard counters, owner/next-check/area in the entry forms.

### Changed
- `follow_up` is now the human note; `owner` is the machine field. TODO = mine, TASK = theirs.
- Dashboard counts open / overdue / stale / unowned separately from kanban status.

### Fixed
- `update_entry` can now clear `owner`, `next_check`, `area`, `eta` and `follow_up`.
- SQLite migration order: indexes on new columns are created after the `ALTER TABLE` statements.

## [0.9.0] — 2026-07 → 2026-11 (baseline)

- Single-user log app: LOG/TODO/TASK, kanban, tags, AI analysis, RAG chat, compaction, Excel import/export, database backup/restore.
- 303 entries logged between 27 July and 19 November 2026 — the baseline this system was designed against.
