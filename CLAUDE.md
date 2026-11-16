# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Hackathon team template: a FastAPI backend, an LLM helper, an ML slot, a React frontend and a team board, glued together by an `hk` bash script that wraps the team's git workflow. Built for a 24h event with 6–8 mixed-skill teammates who each drive an AI agent (mainly Copilot) on their own laptop with their own, limited credits. Design goal: **one task = one agent chat = one PR**, with the least possible exploration. Keep answers and code short and plain.

Team rules (shared with Copilot, follow them too): @.github/copilot-instructions.md

## Commands

Python 3.12, run from the repo root. `hk` is a bash script; on Windows run it as `bash hk <cmd>` in Git Bash, or `.\hk <cmd>` in PowerShell/cmd (`hk.cmd` finds Git Bash and runs it).

```bash
python -m venv .venv && source .venv/Scripts/activate   # Mac/Linux: .venv/bin/activate
pip install -r backend/requirements.txt -r ml/requirements.txt

bash hk doctor                    # is this laptop ready (git identity, GitHub, python, packages, node, .env)?
bash hk run                       # uvicorn → http://localhost:8000/docs and /board
bash hk web                       # frontend dev server (npm install on first run)
bash hk board                     # open the team board (API must be running)
pytest                            # all tests (config in pyproject.toml: testpaths=backend/tests, pythonpath=.)
pytest backend/tests/test_api.py::test_predict_gives_one_answer_per_item   # single test
ruff check --select E9,F63,F7,F82 .   # the only lint CI enforces (crash bugs, not style)
ruff format <files>                   # formatting; hk push does this automatically
cd frontend && npm run build          # what CI runs for the frontend
bash hk data [file]               # summarise data/ → docs/data-summary.md (masks phones/emails)
bash hk sync                      # merge latest origin/main into the current branch
```

`Makefile` is empty; use `hk` instead.

CI (`.github/workflows/checks.yml`) runs the ruff crash check, `pytest`, and `npm run build` in `frontend/`. It only installs `backend/requirements.txt`, so tests must not import ML packages (pandas/sklearn) at module level, and must never need a network or an LLM key.

## Architecture

- **`contracts/api.py`** — the single source of truth for Pydantic shapes (`Item`, `Prediction`, `PredictRequest/Response`, `Health`). Mirrored by hand in `frontend/src/api.ts`. The current shapes are placeholders the lead replaces with the real problem's shapes. Lead-owned (CODEOWNERS): don't change it unless asked; if you do, update `backend/tests/test_api.py` and `frontend/src/api.ts` too.
- **`backend/app/main.py`** — FastAPI app: `GET /health`, `POST /predict`, plus the board router. CORS is wide open on purpose (demo).
- **`backend/app/model.py`** — the one place predictions come from. At import it checks for `ml/predict.py`: if present and importable, uses `ml.predict.predict` (`MODE="real"`); otherwise falls back to `fake_predict` (`MODE="fake"`) and puts the reason in `NOTE`. An ML import error must never take the API down. `fake_predict` is deterministic (MD5 of the text). The fake is meant to be replaced early with simple rule-based "Backup" logic so the demo always works.
- **`backend/app/llm/`** — the one place the team calls an LLM: `ask(prompt, system=None) -> str`, `status()`. `__init__.py` reads `.env` (`LLM_PROVIDER=fake|claude|openai`, `LLM_MODEL`, keys) and picks `claude.py` (official `anthropic` SDK, default `claude-opus-5-5`, server-side fallback on), `openai_.py` (official `openai` SDK, `OPENAI_BASE_URL` for compatible services) or `fake.py`. No key, or an SDK that fails to import, means fake answers with the reason in `NOTE`: same philosophy as `model.py`. Provider modules import their SDK at module level and are imported lazily, so keep them separate; never put Anthropic calls in the OpenAI file or vice versa.
- **`backend/app/board/`** — the team board at `/board`: one static `index.html` (vanilla JS/CSS, no build) + `router.py` (`/board/api/<section>` JSON) + `data.py` (facts from git, PLAN.md, TEAM.md, the model, the LLM, `gh`). Read-only; every section is wrapped so one failure greys one card. It reads `PLAN.md` from `origin/main` (not the local checkout) and derives task state the same way `hk status` does: **done** if a commit title on `origin/main` starts with `<ID>:`, **in progress** if a remote `task/<ID>-*` branch exists (who = its tip author), else **free**. Keep `hk status` and `data.plan()` in sync if you change either.
- **`frontend/`** — Vite + React 19 + TypeScript + Tailwind v4. `src/api.ts` is the only file that talks to the API (`VITE_API_URL`, default `http://localhost:8000`); `src/App.tsx` is a working placeholder page. `package.json` overrides `rollup` with `@rollup/wasm-node` so `npm run build` works on laptops whose security policy blocks native binaries; leave the override in place.
- **`ml/predict.py`** (not yet written) — contract: `predict(items: list[Item]) -> list[Prediction]`, one per item, same order; load model files once at module level from `ml/artifacts/`. `/health` reports `"model": "real"` once it loads. Files >5 MB can't be pushed. Packages it needs go in `ml/requirements.txt` (never `backend/requirements.txt`).
- **`data/`** — gitignored except its README; raw data stays local. Read `docs/data-summary.md` instead of raw data.
- **`brief/`** — problem statement and judging rules (added at event start). **`PLAN.md`** (created at the start) holds the task table; **`TEAM.md`** holds people/roles/hours and the `Ends:` time the board counts down to. Names in TEAM.md must match each person's `git config user.name`.

## Team workflow (`hk`)

`hk status` → `hk start B-01` → `/hk-task B-01` in a new Copilot chat → `hk push` → `hk pr` → teammate approves → squash merge.

- `PLAN.md` table columns are `| ID | Task | For | Files | Needs | Done when |`. `For` is `anyone` / `dev` / `lead` / a name; people pick free tasks themselves. `Files` lists the exact files or folders the task owns (comma-separated, globs allowed). `hk`, the board and the Copilot skills all parse these columns by position.
- Task IDs are `<A|B|F|M>-NN` (A lead, B backend, F frontend, M data/ML); branches are `task/<ID>-<slug>`. `hk start` claims a task immediately (empty commit `<ID>: start` + push) and refuses a task someone else is on unless `--join` is given.
- `hk push` auto-formats changed files (ruff, prettier if installed), commits, merges `origin/main`, **warns** (never blocks) when the diff touches files outside the task's `Files`, and refuses to push `.env*`, keys, or files >5 MB.
- Never commit to `main` directly; never force-push.
- Changes to `contracts/`, `.github/`, `scripts/`, `hk`, `pyproject.toml`, `PLAN.md` need the lead's approval.

Before changing `hk`, `backend/app/board/data.py` or the PLAN.md format, read `docs/SYNC-NOTES.md`: the sync system's inventory, invariants, offline test harness and backlog.

## Copilot skills

`.github/skills/` defines the team's Copilot Chat workflows; follow them if asked to do the same thing:
- **hk-task** — do one PLAN.md task on the current branch: read only that row, the team rules and the row's `Files`; build; prove "Done when"; reply in ≤4 lines ending with `Run: hk push`.
- **hk-plan** — turn `brief/` + `TEAM.md` + `docs/data-summary.md` into a one-page `PLAN.md` in the fixed format above (read only those files, never raw data; on re-plan keep all IDs; at least half the tasks `anyone`).
- **hk-fix** — resolve merge conflicts, keeping both sides where possible; ask when logic genuinely diverges.
- **hk-review** — review a PR against its `PLAN.md` row; ≤8 lines, verdict MERGE / FIX FIRST, no style comments. Optional: green checks + the app runs is the normal bar.
