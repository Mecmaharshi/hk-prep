---
name: hk-plan
description: Turn the hackathon problem into a one-page PLAN.md with a task list for the team. Lead only. Run once at the start, and again only when the plan must change.
argument-hint: "[what changed, for a re-plan]"
disable-model-invocation: true
---

# Make or update PLAN.md

Work fast. Write short, plain English that anyone on the team can read.

## Read only these
- Everything in `brief/`: the problem and the judging rules.
- `TEAM.md`: people, roles, skills, hours, event times.
- `docs/data-summary.md`: made by `hk data`. Never open the raw data.
- `PLAN.md`, only if it already exists.

Don't search the repo or open any other file.

## Think, but don't write it down
Who uses it and what they need · what the judges score · data traps (future-info columns, personal data, repeats, rare cases) · the simplest approach that can win, and a backup that surely works · what the 3-minute demo shows.

## Write PLAN.md in exactly this shape

```markdown
# Plan: <short name>

Goal: <one line>
How: <one line>
Backup: <one line: the simple version we can always ship>
Demo: <step → step → step>
Watch out: <one line: the biggest traps>

| ID | Task | Who | Needs | Done when |
|---|---|---|---|---|
| A-01 | <task> | <name> | – | <something you can see or run> |

Later, only if time: <comma-separated ideas>
Times: H3 real shapes + backup rules work end to end · H14 all features in · H22 no new code
```

## Task rules
- Each task takes 1–3 hours. Split anything bigger.
- The starter already runs end to end with a fake model (`hk run`). First tasks: put the real shapes in `contracts/api.py`, and turn the fake in `backend/app/model.py` into the Backup rules. Then everyone builds on those at once.
- ML plugs in by writing `ml/predict.py` (see `ml/README.md`); the API switches to it by itself. No loader task needed.
- One owner per task, from TEAM.md, matched to their skills. Keep each person under 60% of their hours.
- "Done when" is something anyone can see or run.
- Two people never edit the same file.
- IDs: A = lead, B = backend, F = frontend, M = data/ML, then a number: B-01, B-02.
- Move the times to match the event's check-ins, if TEAM.md lists them.

## Re-plan
If PLAN.md exists, change only what's needed. Keep every ID, never renumber, never touch finished tasks.

## Reply
At most 5 lines: the approach in one line, what you assumed, and up to 3 questions, only if an answer would change the plan.
