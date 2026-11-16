# Sync system: notes for the agent

Read this before touching anything that keeps the team in sync. It says what the sync system is, where each piece lives, which rules must not break, how to test without GitHub, and what to build next. Written 2026-11-14 after the first build; update it when the system changes.

## 1. What "sync" means here

Six to eight people, each on their own laptop with their own AI agent, must never step on each other and must always know what is done, in progress and free, without asking. The sync system is everything that makes that true. It is deliberately **git-only**: no database, no server, no extra service. The remote (`origin`) is the single source of truth and three facts are derived from it:

| Fact | Derived from | Where |
|---|---|---|
| Task **done** | a commit title on `origin/main` starts with `<ID>:` (squash-merge uses the PR title, which `hk pr` builds as `<ID>: <task>`) | `hk status`, `data.plan()` |
| Task **in progress**, by whom | a remote branch `task/<ID>-*` exists; **who** = author of its tip commit | same |
| Task **free** | neither | same |

Everything else (PLAN.md rows, the Files column, the board) is read from `origin/main`, not from the local checkout, so a stale laptop never shows a stale plan.

## 2. Inventory: the pieces and what each guarantees

### `hk` (bash, repo root): the only way teammates touch git

| Function | Lines | Guarantee |
|---|---|---|
| `task_id`, `me` | [hk:22](../hk#L22), [hk:25](../hk#L25) | ID comes from the branch name `task/<ID>-slug`; identity from `git config user.name` |
| `fetch` | [hk:42](../hk#L42) | every state-reading command fetches first (`--prune` so merged/deleted branches vanish) |
| `plan_row` | [hk:48](../hk#L48) | parses one PLAN.md row **by column position**: `ID \| Task \| For \| Files \| Needs \| Done when`, backticks stripped |
| `in_files`, `warn_outside_files` | [hk:57](../hk#L57), [hk:73](../hk#L73) | diff `origin/main...HEAD` vs the Files column (file, folder, or glob); **warns, never blocks** |
| `merge_main` | [hk:90](../hk#L90) | brings `origin/main` into the branch before every push; on conflict prints the files and points to `/hk-fix` |
| `format_changed`, `guard_staged` | [hk:106](../hk#L106), [hk:126](../hk#L126) | auto-format; refuse `.env*`, keys, files > 5 MB |
| `push_work` | [hk:154](../hk#L154) | commit (title `<ID>: update`) → fetch → merge main → warn outside files → push `-u` |
| `cmd_start` | [hk:211](../hk#L211) | **claims** a task: new branch from `origin/main`, empty commit `<ID>: start`, immediate push. Refuses a task whose remote branch tip author ≠ me, unless `--join`. Prints the row and the next command (`/hk-task <ID>`) |
| `cmd_sync` | [hk:272](../hk#L272) | `main`: ff-only; branch: `merge_main` |
| `cmd_push`, `cmd_pr` | [hk:283](../hk#L283), [hk:294](../hk#L294) | `pr` builds the title `<ID>: <task>` (this is what makes "done" detectable) and a body with Files/Done when |
| `cmd_status` | [hk:326](../hk#L326) | the three-state derivation above, plus For and Who |
| `cmd_doctor` | [hk:389](../hk#L389) | preconditions for sync: git identity set, remote reachable, gh (optional) |

`hk.cmd` is a Windows launcher only; it has no logic.

### The board's copy of the same logic (Python)

- [backend/app/board/data.py:75](../backend/app/board/data.py#L75) `parse_plan()` and [:105](../backend/app/board/data.py#L105) `plan()`: **must stay identical in behaviour to `plan_row` + `cmd_status`**. Same regexes (`^ID:` or `task/ID(-|$| )` for done; `task/ID(-|$)` for in progress), same column positions. A test for `parse_plan` lives in [backend/tests/test_board.py](../backend/tests/test_board.py).
- [data.py:58](../backend/app/board/data.py#L58) `fetch()` is rate-limited to once per 30 s (many browsers refreshing must not hammer GitHub).
- [data.py:389](../backend/app/board/data.py#L389) `github()`: open PRs + CI on main via `gh`, cached 60 s, degrades to a note when `gh` is missing.

### GitHub-side rules

- [scripts/setup_github.sh](../scripts/setup_github.sh): squash-only merges with **PR title as commit title** ([:28](../scripts/setup_github.sh#L28)); branches deleted on merge ([:29](../scripts/setup_github.sh#L29)), which is what frees a task's "in progress" state; `main` protected: PRs only, 1 approval, the `checks` job must pass ([:37](../scripts/setup_github.sh#L37)).
- [.github/CODEOWNERS](../.github/CODEOWNERS): shared files need the lead.
- [.github/workflows/checks.yml](../.github/workflows/checks.yml): what "green" means.

### The agent-side contract

- [PLAN.md format](../.github/skills/hk-plan/SKILL.md): the Files column is the conflict-prevention mechanism; two tasks never share a file.
- [hk-task](../.github/skills/hk-task/SKILL.md): the agent stays inside Files; [hk-fix](../.github/skills/hk-fix/SKILL.md): conflict resolution.

## 3. Invariants: do not break these

1. **Three states, derived only from `origin`.** Never introduce a file or server that must be updated by hand to track work. PLAN.md is never edited to record progress.
2. **Branch naming `task/<ID>-<slug>` and commit/PR title prefix `<ID>:`** are load-bearing. Changing either breaks done/in-progress detection in two places (`hk`, `data.py`).
3. **Column positions of PLAN.md** are parsed in three places (`hk`, `data.py`, the skills' examples). Change all or none.
4. **`hk push` warns, never blocks**, on files outside the task. Blocking was rejected by the lead: speed first.
5. **A failure of anything optional (gh, network, bash) degrades to a note.** Nothing in sync may take the API down or make `hk` exit on a non-essential step.
6. **No commits to `main` from `hk`, no force-push, no history rewriting.** `hk start` requires a clean tree (tracked files) to avoid carrying one task's edits into another.
7. **Zero AI tokens** in `hk`. Anything needing judgement is a Copilot skill, not a command.
8. Keep `hk` POSIX-ish bash that works in Git Bash on Windows (no GNU-only flags, `set -euo pipefail` is on: every `a && b || c` chain must end with a command that returns 0; see the doctor bug fixed on 2026-11-14).

## 4. How to test without GitHub (the rehearsal harness)

Everything was verified with a throwaway repo and a bare "origin". Reproduce it like this (bash, from anywhere):

```bash
S=/tmp/hktest; rm -rf $S; mkdir -p $S; SRC=/path/to/hk-prep
git init -q --bare $S/origin.git
mkdir $S/lead && cd $S/lead && git init -q -b main && git config user.name Lead && git config user.email lead@x.test
cp -r $SRC/hk $SRC/backend $SRC/contracts $SRC/.gitignore $SRC/TEAM.md $SRC/pyproject.toml .
printf '# Plan: T\n\nGoal: g\n\n| ID | Task | For | Files | Needs | Done when |\n|---|---|---|---|---|---|\n| B-01 | Shapes | lead | contracts/api.py | – | docs |\n| F-02 | Table | anyone | frontend/src/*.tsx | B-01 | shows |\n' > PLAN.md
git add -A && git commit -qm start && git remote add origin $S/origin.git && git push -q -u origin main
bash hk start B-01 && bash hk status
git clone -q $S/origin.git $S/anu && cd $S/anu && git config user.name Anu && git config user.email anu@x.test
bash hk start B-01            # expect: refused, Lead is on it
bash hk start F-02 && mkdir -p frontend/src && echo x > frontend/src/a.tsx && echo y > stray.py && bash hk push   # expect: heads-up about stray.py
```

Simulate a squash merge: on the lead clone, `git merge --squash origin/task/F-02-table && git commit -qm "F-02: Table" && git push && git push origin --delete task/F-02-table`, then `bash hk status` shows F-02 done by Lead. **Turn this into `scripts/rehearse.sh`** (see backlog) so it runs in one command and in CI.

Backend side: `pytest backend/tests/test_board.py` covers `parse_plan`; the live `plan()` path has no fixture yet.

## 5. Known gaps and the backlog, in priority order

1. **No automated test for `hk`.** The harness above is manual. → `scripts/rehearse.sh`, run by CI on Linux (bash is there).
2. **No way to release a task.** If someone claims B-03 and leaves, it stays "in progress" forever. → `hk drop [ID]`: delete the remote branch (and local), only if the branch has no commits beyond `<ID>: start` or `--force`. The board should offer the command.
3. **Stale claims are invisible.** → `hk status` and the board show last-push age and flag "in progress" > N hours with no push (the board already has `at`).
4. **Overlap is caught at push, not at start.** → at `hk start`, fetch other in-progress branches, diff them against `origin/main`, and warn if any touched file is in this task's Files (cheap: `git diff --name-only origin/main...origin/task/X`).
5. **The approver's step is manual on GitHub.** → `hk merge <PR|ID>` for the approver: `gh pr review --approve` + `gh pr merge --squash --delete-branch`, guarded by green checks; falls back to a link without gh.
6. **`hk status` doesn't show PRs.** → a column "PR: open / approved / failing" when gh is available (reuse `data.github()` logic in bash, or call the running board's `/board/api/overview`).
7. **"Done" detection trusts the PR title.** A teammate who edits the title loses the `<ID>:` prefix → task shows free again. → `hk pr` could also push a tag or note; or the board warns when a merged `task/` branch has no matching `<ID>:` commit (branch deleted on merge makes this hard; consider `git log --merges` fallback or `gh pr list --state merged`).
8. **Identity mismatch.** "Who" is `git config user.name`; TEAM.md names must match. → `hk doctor` checks the name is in TEAM.md; the board's Team tab already lists unmatched names.
9. **Behind-main warning.** → `hk status`/board: "your branch is N commits behind main; run hk sync" (`git rev-list --count HEAD..origin/main`).
10. **Line endings.** Windows clones warn about CRLF; `.gitattributes` exists, check it covers `* text=auto eol=lf` for `hk` (a CRLF `hk` breaks bash).

## 6. Prompt set for the next session

Paste these one at a time into a new Claude Code chat in this repo. Each is self-contained; do them in order (1 first: it is the safety net for the rest).

**P0, orientation (always first):**
> Read docs/SYNC-NOTES.md, CLAUDE.md, hk, backend/app/board/data.py (functions parse_plan, plan) and backend/tests/test_board.py. Don't read anything else yet. Tell me in 5 lines what the sync system guarantees and which two places must stay in sync. Then stop.

**P1, the test harness:**
> Turn section 4 of docs/SYNC-NOTES.md into scripts/rehearse.sh: a bash script that builds a throwaway bare origin plus two clones in a temp dir, runs hk start/status/push/pr-title/squash-merge scenarios, and asserts the expected outputs (claim visible, second claim refused, --join works, outside-Files warning names only the stray file, done detected after squash merge, dropped branch frees the task). Exit non-zero on any failed assertion, print one line per check. Add a CI step in .github/workflows/checks.yml that runs it on ubuntu. Keep invariants 1–8 from the notes. Run it and show me the output.

**P2, release a task:**
> Add `hk drop [ID]` per backlog item 2 in docs/SYNC-NOTES.md: deletes the task's remote and local branch so the task shows free again. Refuse if the branch has commits beyond "<ID>: start" unless --force. Must switch back to main first. Update hk help, docs/GUIDE.md section 7 and 13, and add a scenario to scripts/rehearse.sh. Warn, don't block, is the house style; dropping is the one destructive command, so confirm with a y/N prompt unless --force.

**P3, stale claims and behind-main:**
> Backlog items 3 and 9: hk status gains a column "Last push" (age) and marks in-progress tasks with no push for over 3 hours with "stale?"; the board's Plan and Overview tabs show the same. Add "N behind main, run hk sync" to hk status when on a task branch. Keep hk status and data.plan() producing the same facts; extend the parse/derive tests.

**P4, overlap at start:**
> Backlog item 4: at hk start, after fetch, compare this task's Files against files changed on every other in-progress task branch (origin/task/*) relative to origin/main. If any overlap, print "Heads-up: <ID> (<who>) has already changed <file>" and continue. Add a rehearse.sh scenario. Must add under 1 second for 10 branches.

**P5, the approver's command:**
> Backlog item 5: hk merge <PR number or task ID> for the reviewer: show title, Done when, changed files vs Files, checks state; if checks are green, gh pr review --approve then gh pr merge --squash --delete-branch; otherwise explain what's red. Without gh, print the PR link. Keep the PR title untouched (it's how "done" is detected). Update GUIDE.md section 5.

**P6, title safety:**
> Backlog item 7: make done-detection robust to a renamed PR title. Propose the smallest change (two options, one paragraph each, with the failure mode each still has) before writing code. Wait for my choice.

**Closing prompt for every session:**
> Update docs/SYNC-NOTES.md: inventory line numbers, invariants if any changed, move finished backlog items to a "Done" list with the date, and add anything you learned that the next agent must know. Run pytest and scripts/rehearse.sh and paste the last 5 lines of each.

## 7. Working rules for the agent on this topic

- Propose before building when a change touches an invariant; otherwise build, test with the harness, show output.
- Keep `hk` and `data.py` in lockstep: if you change a regex, a column, or a branch/commit convention in one, change the other in the same PR and add a test.
- Never test against the real team repo. Always the throwaway origin.
- Short, plain output. The team reads `hk` messages under stress; every message says what happened and what to do next.
