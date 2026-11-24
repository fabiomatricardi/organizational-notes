# The note-taking method (v1)

**Purpose:** stop holding the ship in your head. Capture in seconds, keep one page that is always true, and let Friday 14:00 be a by-product instead of a reconstruction.

**Start here:** if this document feels like too much, read [`print/00-how-it-works.pdf`](print/00-how-it-works.pdf) — page 1 is the whole method on one sheet, page 2 answers the three questions that always come up about it. Pin page 1 above the desk. This file is the reference behind it, not the daily tool.

**One idea:** four artefacts, four jobs. Never let one do another's work.

| Artefact | Its only job | Lives | Refreshed |
|---|---|---|---|
| iPhone → Telegram "inbox" | catch anything in 5 seconds | pocket | never organised on the phone |
| **Kick-off grid** (A4 portrait) | who said what, and who stayed silent | barge, one per working day | 07:20, from a pre-dated stack |
| **OPEN sheet** (A4 landscape, clipboard) | what is open, who owes it, by when | desk, always visible | rewritten Monday, updated in pencil daily |
| **Notebook** (A5) + the app | appointments, decisions, the day's record | desk / laptop | 3 min at 16:30, Friday 15 min |

The OPEN sheet is the whole point: it is the **only page you ever read**. The Kick-off grid is the day's capture, the Notebook is the day's history, and the OPEN sheet is the present. This is what fixes "my paper list is spread across several pages".

---

## Where each dated thing goes

This is the whole calendar question. Four kinds of dated thing, four places — never two.

| It is… | The test | It lives on |
|---|---|---|
| **A target** | the week's 3 outcomes | Top of the **OPEN sheet**, each with a date |
| **An appointment** | it happens at a time; nobody owes a thing | `TODAY'S 3` on that day's **Kick-off grid**, and the **Notebook** page |
| **A commitment** | someone owes a thing by a date | **OPEN sheet** — WHO + DUE |
| **A note** | neither | **Notebook**, one `•` line |

Consequence: you do not need a separate calendar. The week's fixed points live in `TODAY'S 3` on five pre-dated **Kick-off grids**, and the week's obligations live in the **OPEN sheet**'s DUE column, read every morning.

---

## The grammar

One line per thing. Symbol first. Used identically on paper, in Telegram and in the app.

| Mark | Meaning | Ends up in the app as |
|---|---|---|
| `•` | fact, decision, event — what happened, and so what | daily LOG entry |
| `→` | **my** action — verb + object + date | TODO (mine) |
| `⇒` | **their** action — name + verb + object + date | TASK (delegated) |
| `?` | waiting on / unanswered | TODO, status PENDING, `waiting: name` |
| `!` | risk or issue | daily LOG + Thursday/Friday agenda |
| `✓` | closed — cross it off the OPEN sheet the same day | COMPLETED |
| `@name` | anything about a person | inbox/people line + owner |

Non-negotiable convention: **TODO = mine, TASK = theirs.** `follow_up` always holds the owner's name. Never write your own name there.

---

## The day (14 min of admin, 20 min on Friday)

| Time | Where | What | Budget |
|---|---|---|---|
| 07:20 | barge / whiteboard | Kick-off. **Photograph the whiteboard.** On today's **Kick-off grid** — already printed and dated — one line per person, **only what is new**. `TODAY'S 3` is already filled for anything fixed. Blank is information. | **2 min** |
| 07:25 | desk | Move `⇒`, `→`, `?`, `!` onto the **OPEN sheet**. Then run a pencil down the DUE column and **circle every date inside the next five working days** — that is the lookahead. Check PEOPLE: who has no LAST TALK younger than five days? | **5 min** |
| during the day | anywhere | Anything someone owes → one new row on the **OPEN sheet**, there and then. Anything you learn or decide → one `•` line on the **Notebook**. Thirty seconds each, no tidying. | seconds |
| 12:45 | desk | Cross off what closed on the **OPEN sheet**. Nothing else. | **5 min** |
| 16:30 | laptop / desk | Register the day. Then three `•` lines on the **Notebook** (*done / moved / blocked*) and tomorrow's appointments. Send the nudges for anything due today **before you stop**. With the app running, this is the Inbox → Today pass instead. | **10–20 min** |

The Notebook's daily block is three lines, never an essay. Essays belong in the Friday report.

---

## The week (it already matches your rhythm)

- **Sunday or Monday 07:25** — print the week first: one **OPEN sheet** and **five pre-dated Kick-off grids** (see below). Then rewrite the **OPEN sheet**: the week's 3 targets with their dates, the fixed points, and only the live lines carried forward. 10 minutes.
- **Wednesday 16:30** — pull the `?` lines waiting on SHI into the Thursday agenda. 5 minutes.
- **Thursday** — SHI alignment. Capture decisions immediately, update the **OPEN sheet** before you leave the room.
- **Friday 13:00** — close the week: mark ✓/✗, write 3 lines (done / blocked / risk), generate the AI report from the week, adjust to Thierry's format, save as a LOG. **15 minutes.** Then 14:00 is a meeting, not a panic.
- **Last day before leave** — the **OPEN sheet** *is* the handover. Copy it to Syukri with the 5-line outlook. Nothing written from scratch.

---

## The five daily pages

Every week starts with **five Kick-off grids already printed and already dated** — Monday to Friday, week number, day name, the people already in the left column, the right column empty.

Nothing is written on them but the date. That is the point:

- **Nothing is transcribed twice.** No morning is spent writing dates and names; the stack is ready before Monday.
- **`TODAY'S 3` is written in advance** for anything already fixed — a TBT, a gate, a review, a power-up — and completed at the kick-off. That box is your calendar for the day, so you do not need a second one.
- **The names are printed, not handwritten.** One canonical spelling per person, identical on all five pages and on the **OPEN sheet**. Vendors never get a row; they appear as owners.
- **A lost day is still a dated page.** It keeps its `TODAY'S 3` and its blanks, so the week never becomes anonymous.

Build the stack with `tools/build_week_pack.py` — it writes the five grids and the matching **OPEN sheet** in one run, with the dates filled.

---

## The people mechanism (the thing that actually slipped)

Do not add 1:1s to a calendar that has no room. **Pair every site walk with one person.**

- Every walkdown or site visit: take one lead with you. The walk *is* the 1:1.
- After it, one `@name` line: what they need, what you promised, what to ask next.
- The **OPEN sheet**'s PEOPLE column then does the nagging: **nobody goes two weeks without a real conversation**, and you can see it at a glance.
- **`WHAT THEY NEED FROM ME` is your debt list, not a contact note.** It holds what this person is waiting on *you* for: a decision, an approval, a PTW signature, a spare, a clarification. Ask it as **"what am I blocking?"** — people answer "nothing" to "what do you need", but they will name the thing that is stuck on you. Write `—` when the answer really is nothing, so a blank cell means *not asked*, not *nothing owed*.
- Current cadence you already have: Syukri and Yernar/Yang Zheng daily; Aras and Buly weekly. Keep those, and let the sheet prove it happened.
- At 100 people: your 4 leads + deputy keep a weekly walk-and-talk; everyone else gets the kick-off plus a monthly skip-level drawn from the **blank rows** — the people who never surface.

---

## Ten rules

1. Never organise on the phone. Dump, don't sort.
2. One line, one thing. Two owners in one line means it dies.
3. A commitment without a date is not a commitment. You set the dates.
4. **Blank is information.** A name with no line means nothing new — that is a finding, not a gap.
5. Only live items cross to the new **OPEN sheet** on Monday. Dead lines do not migrate.
6. Nudge before the laptop closes. A follow-up that waits for tomorrow is a follow-up that dies.
7. **No backfill.** If you miss two days, do not reconstruct them. Write one line `gap 17–18.11` and start today. Reconstruction is what kills the habit.
8. **A target change is struck through, never reworded silently.** Draw the line through the old target, write the new one beside it, with the date and the reason: `3 AIR LWN ready & signed · 23.11 pm, power-up off (conditions)`. Friday then explains itself.
9. **One canonical name per person, printed not handwritten.** The same spelling on every **Kick-off grid** and on the **OPEN sheet**. Two initials for every surname that repeats (HJ Lee, JH Lee, Chor Lee, Seong Lee). Vendors are owners, never rows.
10. **The OPEN sheet follows the week, not the Monday morning.** If Tuesday's subject changes, Tuesday's rows change. A register that only knows what was true on Monday is a snapshot, not a register.

---

## Scaling to June 2027

- The 20-minute whole-team round table will not survive 100 people. Plan the replacement now: **area stand-ups** (AIR / FIR / ICSS / PTW) that send you a written 5-line update by 07:00 — a Teams message is fine. No new tool, no logging habit for leads.
- Your **OPEN sheet** then aggregates **6 area boards, not 100 individuals**. Same sheet, coarser grain.
- Your job shifts from collecting facts to **auditing exceptions**: what is overdue, what is silent, what escalated twice.
- Rotation 90/15 means the **OPEN sheet** must be legible to someone else. The two-column layout already is — that is why it is split that way.

---

## Acceptance test

**Friday 13:00, week 4: zero report bullets reconstructed from memory.** If you still have to remember, the capture is not granular enough — fix the grammar, not your discipline.

## What the app gives you

The app is the memory, not the method: an **Inbox** for Telegram captures, a **Today** screen for the 16:30 ritual, a **Follow-up** screen that lists every open commitment by owner with overdue/stale flags, and the weekly report and handover generated from the register. See [`04-app-guide.md`](04-app-guide.md). The paper half works on day one and is the part that matters; if the app is unavailable, keep the paper running and register when you can.
