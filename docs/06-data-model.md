# 06 — Data model

**Audience:** whoever writes SQL against this database (app, viewer, scripts).
**Last updated:** 2026-11-20.

SQLite, one file at `data/personal_log.db`, WAL mode, foreign keys on.

---

## Tables

```
log_entries ──< entry_tags >── tags
     │
     └── reference_id ──► log_entries.id      (thread / follow-up chain)

inbox            capture queue, independent of log_entries
meta             key/value: telegram_offset
analysis_reports generated reports (weekly, comprehensive, handover, ...)
conversations    chat sessions (also mirrored as markdown on disk)
```

### `log_entries` — the only table that matters

| Column | Type | Meaning |
|---|---|---|
| `id` | INTEGER PK | |
| `timestamp` | DATETIME | when the thing happened or was captured (local time) |
| `activity` | TEXT | the line itself; the first line is the title |
| `type` | TEXT | `LOG`, `TODO`, `TASK` |
| `status` | TEXT | `LOG`, `PENDING`, `ASSIGNED`, `ONGOING`, `COMPLETED` |
| `follow_up` | TEXT | human note: context, `waiting: SHI`, etc. |
| `owner` | TEXT | **who owes the action** (added 1.0.0) |
| `next_check` | DATE | when to chase it (`YYYY-MM-DD`, added 1.0.0) |
| `area` | TEXT | `AIR`, `FIR`, `QIR`, `ICSS`, `PTW`, `LQ`, ... (added 1.0.0) |
| `eta` | DATETIME | the promised completion |
| `reference_id` | INTEGER | link to a parent entry (threads) |
| `created_at`, `updated_at` | DATETIME | audit |

Indexes: `type`, `status`, `timestamp`, `reference_id`, `owner`, `next_check`.

### Semantics

**Type is ownership, not workflow.**

| `type` | Means | Typical status |
|---|---|---|
| `LOG` | something that happened or was decided | `LOG` |
| `TODO` | **my** action | `PENDING` / `ONGOING` / `COMPLETED` |
| `TASK` | **their** action (delegated) | `ASSIGNED` / `ONGOING` / `COMPLETED` |

Convention since 1.0.0: `follow_up` is the human note, `owner` is the machine field, and `owner` never contains your own name (except the literal `me` for TODO, which the UI can set).

**Legacy rows** (before 1.0.0) may have `status='LOG'` on a TODO. They are treated as open because the rule is "not COMPLETED", not "is PENDING".

### Derived flags (computed, never stored)

Computed in `services/entries.py::_decorate_open_item` against *today*:

| Flag | Rule |
|---|---|
| `age_days` | today − timestamp |
| `due` | `next_check` if set, else `eta[:10]` |
| `overdue` | `next_check < today`, or `eta[:10] < today` |
| `stale` | `next_check < today`, or no `next_check` and `age_days > 7` |
| `orphan` | `owner` empty |
| `waiting` | `follow_up` starts with `waiting` |

If you need these in SQL (e.g. the static viewer), reproduce the rules exactly, otherwise the app and the viewer will disagree.

### `inbox`

| Column | Meaning |
|---|---|
| `id`, `received_at` | |
| `source` | `telegram` or `manual` |
| `kind` | `text` or `photo` |
| `body` | the message, or the photo caption |
| `file_path` | `inbox/YYYY-MM/<message_id>.jpg`, relative to `data/` |
| `chat_id`, `message_id` | Telegram provenance |
| `processed` | 0 = waiting for triage, 1 = handled |
| `entry_id` | the resulting entry, when converted |

### `meta`

Key/value. Currently only `telegram_offset` (the last processed `update_id`). Also useful for future one-off migration markers.

### `analysis_reports`

`report_type` ∈ `weekly`, `comprehensive`, `overdue`, `next_steps`, `patterns`, `handover`. `content` is markdown; `period_start` / `period_end` are dates.

### `tags`, `entry_tags`

Created in the first release and still unused (0 rows). Kept for a future area/person tagging use; the current `area` column is simpler and indexed.

### `conversations`

Chat sessions mirrored as markdown in `data/conversations/`.

---

## Migrations

Applied at every startup, idempotent, in `database.py`:

```python
MIGRATIONS = [
    ("log_entries", "owner", "TEXT"),
    ("log_entries", "next_check", "DATE"),
    ("log_entries", "area", "TEXT"),
]
```

`ALTER TABLE ... ADD COLUMN` does not exist with `IF NOT EXISTS` in SQLite, so the code reads `PRAGMA table_info` first. New-column indexes are created **after** the columns (an index in `SCHEMA_SQL` would fail on an old database).

Adding a column later:
1. Add it to `SCHEMA_SQL` (new installs) **and** to `MIGRATIONS` (existing installs).
2. Add it to `services/entries.py::FIELDS`, `models.py`, and the forms.
3. Create any index after the migration loop.

There is no down-migration. Take a backup before schema work; the app does not do it automatically.

---

## Mark → row

| Mark | `type` | `status` | `owner` | `next_check` |
|---|---|---|---|---|
| `•` fact / decision | LOG | LOG | — | — |
| `!` risk | LOG | LOG | — | — (goes to Thu/Fri agenda) |
| `→` my action | TODO | PENDING | `me` | the date |
| `⇒` their action | TASK | ASSIGNED | the name | the date |
| `?` waiting | TODO | PENDING | the person/org | the chase date; `follow_up` starts `waiting:` |
| `✓` closed | — | COMPLETED | — | — |

One LOG per day is the target: five lines assembled from the `•`/`!` items, not a retelling.

---

## Queries behind the screens

| Screen | Query |
|---|---|
| Follow-up | `type IN ('TODO','TASK') AND status != 'COMPLETED'`, decorated and grouped in Python |
| Today — due | same, filtered after decoration (`due = today` or `overdue` or `stale`) |
| Today — entries | `timestamp LIKE '<today>%'` |
| Dashboard | counts by type/status + the open register counters |
| Handover | the open register + `LOG` rows in the last N days containing `!` |

The single source for "open" is `get_open_items()`. If a new view needs open items, use it rather than writing another query — otherwise the definitions will drift.

---

## Size and retention

- 303 entries over four months ≈ 470 KB, including the new tables.
- No retention policy: history is the product. Compaction only merges duplicates.
- Backups: `data/backups/`. Manual copies are cheap; keep them outside the repository (the DB is gitignored).
- `reference/personal_log.sample.db` is a frozen 302-entry copy for documentation and demos. Never write to it.

## Access from other tools

- Read-only scripts: open the file directly, but use `mode=ro` URI and expect WAL. Or copy with the app closed.
- The public viewer never reads this file: it reads an encrypted blob produced by `encrypt.py` in the viewer repository.
