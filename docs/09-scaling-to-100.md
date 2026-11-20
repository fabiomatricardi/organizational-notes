# 09 — Scaling to 100

**Audience:** Fabio, before June 2027.
**Last updated:** 2026-11-20.

The method is designed to survive the growth, but not by doing more of it. At 100 people the constraint changes from *capture* to *aggregation*.

---

## The arithmetic that breaks first

The 07:00 round table is 20 minutes for 20 people — about one minute each, already tight. At 100 people it is either 100 minutes or 20 seconds each. Neither is a meeting.

The second thing that breaks is the people table: 100 rows on an A4 is a phone book, not a working document.

Everything else holds: the register is a list of commitments, and the number of commitments you personally own does not grow with headcount — it grows with delegation.

## The change: from people to areas

Keep the same artefact, change its granularity.

| Now | At 100 |
|---|---|
| One kick-off grid, 20 names | Six area boards: AIR, FIR, QIR, ICSS, PTW, LQ |
| One round table, 20 min | Area stand-ups, 10 min each, leads only |
| You write every line | Leads send a **5-line written update by 07:00** |
| People table: 20 individuals | People table: 6 area owners + your direct reports |
| Register: ~12 commitments | Register: ~12 commitments, aggregated from areas |

The 5-line update is a **speaking standard, not a logging habit** — that is why it can be imposed on people who will never open the app:

```
DONE      what finished since yesterday
NEXT      what starts today, with the tag and the date
BLOCKED   what is stuck, on whom, since when
DECIDE    what he needs from you
OWE       what he owes you, by when
```

You copy the last two lines into the register. Nothing else needs transcribing.

## The delegation rule

At 100, you cannot know everyone. You can know six people and audit the rest.

- **Weekly walk-and-talk** with the four leads (Aras, Buly, Yernar, Yang Zheng), Syukri, and the area owners — 15 minutes each, attached to a site walk, not a calendar slot.
- **Monthly skip-level** with 5 people drawn from the **blank rows** of the grids — the people who never surface. One hour, no agenda except "what is stopping you".
- **Two-week rule:** nobody goes two weeks without a real conversation. The people column makes it visible; the walk makes it happen.

## Metrics that matter (and only these)

| Metric | Source | Target |
|---|---|---|
| Open commitments | Follow-up counter | stable; growth means delegation is failing |
| Overdue | Follow-up | < 10% of open |
| Stale (> 7 days no chase) | Follow-up | 0 at Friday 13:00 |
| Orphans (no owner) | Follow-up | 0 — always a defect |
| Friday bullets reconstructed from memory | your own count | 0 |
| Blank rows per week | kick-off grid | < 20% at 20 people; irrelevant at 100 |

Do not add KPIs to the weekly report unless Thierry asks. The register is a working tool, not a dashboard.

## What to build later (and what not to)

Worth doing before June 2027:

- **Area dashboard** (read-only) if the leads ever need to see their own open items — but only if they ask.
- **Recurring commitments** (weekly report, Thursday alignment) auto-created on Monday, so the register starts with the anchor lines.
- **Owner autocomplete** from history, to keep names consistent ("Seong" vs "Seong Lee").

Not worth doing:

- Multi-user accounts, roles, permissions. The leads will not log in; do not build for them.
- A mobile app. Telegram is the mobile app.
- More report formats. One format, on time, every Friday.

## Onboarding a new person (the 10-minute version)

At 100 people the hidden cost is not the contract, it is the context. For each new engineer:

1. One line in the people table: name, area, start date.
2. A 10-minute talk with the same four questions: what they did before, what they think this job is, what they are afraid of, what they want to learn.
3. The `@name` note in the app: what they need, what you promised, when to check.
4. Add them to the kick-off grid; blank rows are the signal that they are not yet in the flow.

That is the same mechanism as the quality conversations, applied on day one instead of month three — which was exactly what slipped in October.

## The invariants

Whatever changes, these do not:

1. One page is always true.
2. Capture is never organised at the moment of capture.
3. No backfill.
4. A commitment without an owner and a date is not a commitment.
5. The Friday report is a by-product, not a reconstruction.
