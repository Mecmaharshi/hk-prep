---
name: hk-task
description: Do one task from PLAN.md on the current branch, touching only its files. Run after hk start. Aim to finish in this one chat.
argument-hint: "B-01 (or leave empty to use the current branch)"
disable-model-invocation: true
---

# Do one task

Work fast and quietly. One task, one chat, one pull request.

## Find the task
- The ID is the text after `/hk-task` (like `B-01`). If none, read it from the branch: `git branch --show-current` gives `task/B-01-...`.
- Read that one row of `PLAN.md`: Task, For, Files, Needs, Done when. Also read the `Goal` and `Backup` lines at the top.

## Read only these
- `.github/copilot-instructions.md`
- The files listed in the row's **Files** column. Open another file only when a Files entry imports it and you need a name or a shape from it (`contracts/api.py` is the usual one).

Don't search the repo. Don't open other tasks' files. Don't open `data/`.

## Build
1. Create or change **only** the files in Files. If the task truly needs another file, stop and say which one and why, in one line.
2. Keep it simple: the version that makes "Done when" true, nothing extra. No refactors, no renames, no new libraries.
3. Follow the shapes in `contracts/api.py` exactly. Never change `contracts/`.
4. No secrets, keys, phone numbers or emails in code.

## Check
Make "Done when" true and prove it the cheapest way:
- Backend: `pytest` (only the tests for the files you changed, if you can pick them).
- Frontend: `npm run build` in `frontend/`.
- API behaviour: start it with `hk run` and call the endpoint, or read the test output.

Fix until it passes. If you can't after two tries, stop and say what's wrong in two lines.

## Reply
At most 4 lines: what you built · how you checked "Done when" · anything the lead must know · then: `Run: hk push`

Never ask a question that PLAN.md or the row already answers. Never start a second task in the same chat.
