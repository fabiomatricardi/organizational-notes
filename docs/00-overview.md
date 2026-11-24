# 00 — Overview: why four artefacts

**Audience:** Fabio, and anyone who has to run this system in his absence.
**Last updated:** 2026-11-20.

---

## The situation

Discipline superintendent for instrumentation & control on an FLNG under construction in South Korea. 20 people today, ~100 by June 2027. The day is 50 emails, two vendor calls, one 20-minute kick-off, several portal actions, constant verbal feedback to leads, and site walks. Everything arrives faster than it can be written down in prose.

The old system was a single daily log, written in the evening. It produced good history and almost no follow-up: at the last count, 303 entries and **4 open items**. The log was a diary, not an instrument.

## The diagnosis

Three different jobs were sharing one medium:

| Job | What it needs | Why the old system failed it |
|---|---|---|
| **Capture** | 5 seconds, one hand, anywhere | Required a laptop and a quiet 20 minutes, so it happened after the fact |
| **Registration** | Once, structured | Became transcription, so it lost to email every time |
| **Follow-up** | One view of what is open and who owes it | Lived in memory, the calendar, and pages of paper |

Separate the jobs and each one becomes cheap.

## The four artefacts

| Artefact | Its only job | Lives | Refreshed |
|---|---|---|---|
| iPhone → Telegram inbox | catch anything in 5 seconds | pocket | never organised on the phone |
| **OPEN sheet** | what is open, and who owes what | desk, always visible | rewritten Monday; updated in pencil daily |
| **Kick-off grid** | who said what, and who stayed silent | barge, one per working day | 07:20, from a pre-dated stack |
| **Notebook** + the app | appointments, decisions, the day's record | desk / laptop | 3 min at 16:30; Friday 15 min |

The OPEN sheet is the heart of it: **the only page you ever read**. Daily pages are history; the sheet is the present. This is what kills "my notes are spread across several pages".

The kick-off grid is not a fourth register — it is the daily intake for the people dimension. The board already carries area status; the grid carries what the board cannot: commitments and silence.

## One weekly cycle, already in his calendar

```
MON 07:25  new OPEN sheet: 3 targets, per-lead goals, Thu + Fri anchors
    daily  photo board → Kick-off grid → 5 min onto the OPEN sheet → Telegram during the day
           → 5 min at lunch → 10–20 min at 16:30 (register, Notebook, nudges)
WED 16:30  SHI waiting list into Thursday's agenda
THU        SHI alignment; capture decisions before leaving the room
FRI 13:00  close the week, generate the report, 14:00 meeting
```

No new meetings. No new report format. The only new artefact is a sheet of paper.

## Why the app

The paper is the interface. The app is the memory, and it exists to answer four questions the paper cannot:

1. What is open, by owner, and what did I fail to chase?
2. What happened on this date, about this tag, with this person?
3. What is the Friday report? (generated from the register)
4. What do I hand to my back-to-back before 15 days of leave?

Everything else in the app (kanban, tags, compaction, chat) is optional.

## Principles

1. **Capture is not storage.** Never organise at the moment of capture.
2. **One page must always be true.** If retrieving an open item takes more than a glance, the system is broken.
3. **A commitment without a date is not a commitment.** He sets the dates; that is the job.
4. **Blank is information.** A name with no line means nothing new — a finding, not a gap.
5. **No backfill.** Missed days are written as `gap`, never reconstructed. Reconstruction is what kills the habit.
6. **The report is a by-product.** If Friday requires memory, the capture was too coarse.

## What this system is not

- Not a second task tracker beside the completion system and Outlook. It records **commitments**, not the project plan.
- Not shared. The leads do not log; they speak, and he writes.
- Not a replacement for conversations. The people column exists to cause them, not to replace them.

## Reading order

1. [`10-scenarios.md`](10-scenarios.md) — six situations, one per working day; read one before the day.
2. [`01-method.md`](01-method.md) — the daily and weekly routine.
3. [`02-legend-and-examples.md`](02-legend-and-examples.md) — the marks, with real boards rewritten.
4. [`03-first-two-weeks.md`](03-first-two-weeks.md) — setup and rollout.
5. [`04-app-guide.md`](04-app-guide.md) — the screens.
6. [`09-scaling-to-100.md`](09-scaling-to-100.md) — what changes at 100 people.

## Glossary

| Term | Meaning |
|---|---|
| **Commitment** | An action with a named owner and a date. Mine (`→`) or theirs (`⇒`). |
| **Register / OPEN sheet** | The A4 sheet with all live commitments and the people table. |
| **Open item** | TODO/TASK not completed; includes items with no owner (flagged). |
| **Stale** | Past its next-check date, or older than 7 days with no next check. |
| **Orphan** | Open item with no owner. Always a defect. |
| **Waiting (`?`)** | Blocked on someone or something; listed before the Thursday SHI meeting. |
| **Kick-off grid** | The pre-dated A4 page, one per working day, one line per person. |
| **Anchor** | A fixed weekly commitment (Thursday SHI, Friday 14:00 report). |
