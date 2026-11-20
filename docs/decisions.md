# Decision log

Short architecture and method decisions, with the reasoning that will be forgotten otherwise. Newest last. Format: context → decision → consequences → alternatives rejected.

---

## 0001 — Paper first, app second

**Status:** accepted, 2026-11-19.

**Context.** The app requires a laptop and a quiet 20 minutes; the job happens on site, in the barge, in corridors, with no wifi. Notes were written in the evening from memory, so the log became a retrospective and the follow-up depended on recall. 303 entries produced 4 open items.

**Decision.** Capture on paper and phone; the app is registered into, never captured into. The A4 OPEN sheet is the operational document; the app is the archive.

**Consequences.** The method works with no software at all. The app is optional on any given day, which removes the "I'll enter it later" failure. Cost: two places hold state for a few hours, and the 16:30 step is mandatory.

**Rejected.** App-first with a mobile client (a second app to maintain, still needs typing); a paperless tablet (gloves, sunlight, battery).

---

## 0002 — Three registers, not one inbox

**Status:** accepted, 2026-11-19.

**Context.** One daily log was doing three jobs: capture, history, follow-up. Each job has a different time constant (seconds / months / days), and the slowest one was starving the others.

**Decision.** Separate artefacts with one job each: phone inbox (seconds), A4 OPEN sheet (days), A5 + app (months). The kick-off grid is the daily intake for the people dimension.

**Consequences.** Each artefact is trivial to maintain. Cost: three habits, and the discipline to put each thing in its place. The weekly rewrite is what keeps the sheet small.

**Rejected.** One big notebook (that is the current failure); one app with three tabs (the app is still a laptop artefact).

---

## 0003 — `owner` and `next_check` as columns

**Status:** accepted, 2026-11-19.

**Context.** `follow_up` was a free-text field; in practice it held a name 39 times out of 75, and the name was often the author's own. The kanban could not answer "what does Aras owe me and when".

**Decision.** Add `owner` and `next_check` as first-class columns, plus `area`. Keep `follow_up` as the human note. Convention: TODO = mine, TASK = theirs.

**Consequences.** The Follow-up view, nudge copy, handover and weekly critical path all become possible. Cost: two fields to fill — which is the point, because a commitment without them is not one.

**Rejected.** Tags for owners (no date, no query); a separate `commitments` table (duplicates the entry model for no gain at this scale).

---

## 0004 — Telegram long polling

**Status:** accepted, 2026-11-19.

**Context.** The desktop app must receive captures from a phone with no wifi on site and no public address. The user already uses Telegram (web client).

**Decision.** A bot with `getUpdates` long polling, offset persisted in `meta`. Text becomes an inbox row; photos are downloaded to `data/inbox/YYYY-MM/`. `allowed_chat_ids` filters senders.

**Consequences.** No webhook, no port forwarding, works behind the ship firewall and on a laptop that sleeps. Cost: messages queue for up to 24 hours if the laptop is offline; project text transits Telegram's cloud.

**Rejected.** A webhook (needs a public URL); a PWA on localhost (unreachable on site); email-to-self (no structured capture, noisy).

---

## 0005 — Single-user, local SQLite, no auth

**Status:** accepted, 2026-11-19.

**Context.** The system models one person's commitments. Leads will not log in. The dataset is tens of thousands of rows at most.

**Decision.** One FastAPI process bound to `127.0.0.1`, one SQLite file, no accounts, no roles, no sync. The public view is a separate artefact with its own encryption.

**Consequences.** Zero operational surface: no server, no backups beyond a file copy, no password to lose. Cost: not reachable from another device except through the published copy.

**Rejected.** Postgres/Supabase (a server to babysit); a hosted SaaS (project data off-site).

---

## 0006 — The weekly report is generated from the register

**Status:** accepted, 2026-11-19.

**Context.** The Friday 14:00 report was written from memory in prose, and the fixed format was applied afterwards. The critical-path section was the weakest, because it depends on what is *still open*, not on what happened.

**Decision.** The prompt takes three inputs: the week's entries, **all open commitments**, and the stale subset. Output is the Commissioning Manager's exact sections. Weeks with no capture produce visibly thin reports.

**Consequences.** The report becomes an acceptance test for the capture: an empty section means an empty week, and that is useful information. Cost: the report is only as good as the register, so Friday at 13:00 is the real deadline for the week's discipline.

**Rejected.** Asking the model to "summarise the week" (produces narrative, loses the critical path); a separate hand-built report template (duplicated maintenance).

---

## 0007 — Additive schema, no migration framework

**Status:** accepted, 2026-11-19.

**Context.** One user, one file, a handful of releases. Alembic or similar would be more machinery than the problem.

**Decision.** `CREATE TABLE IF NOT EXISTS` + `PRAGMA table_info` checks + `ALTER TABLE ADD COLUMN`, run idempotently at startup. No down-migrations; back up before schema work.

**Consequences.** Upgrades are one restart. Cost: the order matters (new-column indexes after the ALTER), and there is no rollback path.

**Rejected.** Alembic (ceremony), a version table with scripts (more moving parts than columns added per year).

---

## 0008 — No backfill

**Status:** accepted, 2026-11-19 (method rule).

**Context.** The only multi-day gap in four months of data was a 17-day holiday — and the habit broke afterwards, with repeated 3–6 day gaps. The failure mode is not the gap; it is trying to reconstruct it.

**Decision.** A missed day is written as `gap <dates>` and abandoned. Never reconstruct.

**Consequences.** The log stays honest and cheap; the register never fills with archaeology. Cost: some history is missing, permanently, and that is accepted.

**Rejected.** "Catch up on Monday" (turns into an afternoon), retro-dating entries (destroys the report's timing).
