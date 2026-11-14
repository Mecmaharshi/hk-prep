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
Who uses it and what they need · what the judges score · data traps (future-info columns, personal data, repeats, rare cases) · the simplest approach that can win, and a backup that surely works · what the 3-minute demo shows · which LLM provider the contest gives (see `.env.example`: Claude, OpenAI, or none).

## Write PLAN.md in exactly this shape

```markdown
# Plan: <short name>

Goal: <one line>
How: <one line>
Backup: <one line: the simple version we can always ship>
Demo: <step → step → step>
Watch out: <one line: the biggest traps>

| ID | Task | For | Files | Needs | Done when |
|---|---|---|---|---|---|
| A-01 | <task> | lead | contracts/api.py, backend/tests/test_api.py | – | <something you can see or run> |
| F-02 | <task> | anyone | frontend/src/Results.tsx | B-01 | <something you can see or run> |

Later, only if time: <comma-separated ideas>
Times: H3 real shapes + backup rules work end to end · H14 all features in · H22 no new code
```

## Task rules
- Each task takes 1–3 hours. Split anything bigger. A task is done by **one person with an AI agent in one chat** (`/hk-task`), so it must be fully described by its row.
- **For** says who can pick it: `anyone` (clear job, own files, low risk), `dev` (needs judgement or touches shared code), `lead`, or a name when it must be one person. People pick tasks themselves: don't pre-assign unless you must. Aim for at least half the tasks `anyone`.
- **Files** lists the exact files the task creates or changes (comma-separated; a folder like `frontend/src/results/` is fine). Two tasks never share a file. New files are better than shared files.
- **Done when** is something anyone can see or run: a URL that shows X, a test that passes, a command that prints Y.
- The starter already runs end to end with a fake model (`hk run`). First tasks: put the real shapes in `contracts/api.py` (update `backend/tests/test_api.py` and `frontend/src/api.ts` with them), and turn the fake in `backend/app/model.py` into the Backup rules. Then everyone builds on those at once.
- ML plugs in by writing `ml/predict.py` (see `ml/README.md`); the API switches to it by itself. No loader task needed.
- LLM features call `backend.app.llm.ask(prompt)`; the provider is chosen in `.env`. No "set up the LLM" task needed, just one row to add the real key.
- Count hours per person from TEAM.md: keep each under 60% of their hours.
- IDs: A = lead, B = backend, F = frontend, M = data/ML, then a number: B-01, B-02.
- Move the times to match the event's check-ins, if TEAM.md lists them.

## Re-plan
If PLAN.md exists, change only what's needed. Keep every ID, never renumber, never touch finished tasks.

## Reply
At most 5 lines: the approach in one line, what you assumed, and up to 3 questions, only if an answer would change the plan.
