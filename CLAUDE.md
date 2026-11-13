# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Hackathon team template: a FastAPI backend, an ML slot, and an (optional, not yet created) `frontend/`, glued together by a `hk` bash script that wraps the team's git workflow. The repo is built for a 24h event with mixed-skill teammates, so keep answers and code short and plain.

## Commands

Python 3.12, run from the repo root. On Windows `hk` needs Git Bash (`bash hk <cmd>`).

```bash
python -m venv .venv && source .venv/Scripts/activate   # Mac/Linux: .venv/bin/activate
pip install -r backend/requirements.txt -r ml/requirements.txt

bash hk run                       # uvicorn backend.app.main:app --reload → http://localhost:8000/docs
pytest                            # all tests (config in pyproject.toml: testpaths=backend/tests, pythonpath=.)
pytest backend/tests/test_api.py::test_predict_gives_one_answer_per_item   # single test
ruff check --select E9,F63,F7,F82 .   # the only lint CI enforces (crash bugs, not style)
ruff format <files>                   # formatting; hk push does this automatically
bash hk data [file]               # summarise data/ → docs/data-summary.md (masks phones/emails)
bash hk sync                      # merge latest origin/main into the current branch
```

`Makefile` is empty; use `hk` instead.

CI (`.github/workflows/checks.yml`) runs the ruff crash check, `pytest`, and `npm run build` in `frontend/` if `frontend/package.json` exists. It only installs `backend/requirements.txt`, so tests must not import ML packages (pandas/sklearn) at module level.

## Architecture

- **`contracts/api.py`** — the single source of truth for Pydantic shapes (`Item`, `Prediction`, `PredictRequest/Response`, `Health`). Backend, ML and frontend all build on these. The current shapes are placeholders the lead replaces with the real problem's shapes. Lead-owned (CODEOWNERS): don't change it unless asked; if you do, update `backend/tests/test_api.py` too.
- **`backend/app/main.py`** — FastAPI app: `GET /health`, `POST /predict`. CORS is wide open on purpose (demo).
- **`backend/app/model.py`** — the one place predictions come from. At import it checks for `ml/predict.py`: if present and importable, uses `ml.predict.predict` (`MODE="real"`); otherwise falls back to `fake_predict` (`MODE="fake"`) and puts the reason in `NOTE`. An ML import error must never take the API down. `fake_predict` is deterministic (MD5 of the text), so tests can rely on stable output. The fake is meant to be replaced early with simple rule-based "Backup" logic so the demo always works.
- **`ml/predict.py`** (not yet written) — contract: `predict(items: list[Item]) -> list[Prediction]`, one per item, same order; load model files once at module level from `ml/artifacts/`. `/health` reports `"model": "real"` once it loads. Files >5 MB can't be pushed. Packages it needs go in `ml/requirements.txt` (never `backend/requirements.txt`).
- **`data/`** — gitignored except its README; raw data stays local. Read `docs/data-summary.md` instead of raw data.
- **`brief/`** — problem statement and judging rules (added at event start). **`PLAN.md`** (created at the start) holds the task table; **`TEAM.md`** holds people/roles/hours.

## Team workflow (`hk`)

`hk start B-01` → code → `hk push` → `hk pr` → teammate approves → squash merge.

- Task IDs are `<A|B|F|M>-NN` (A lead, B backend, F frontend, M data/ML) and map to rows in `PLAN.md`'s table; branches are `task/<ID>-<slug>`. `hk status` derives state from merged commit titles (`<ID>: ...`) and remote `task/` branches.
- `hk push` auto-formats changed files (ruff, prettier if installed), commits, merges `origin/main`, and refuses to push `.env*`, keys, or files >5 MB.
- Never commit to `main` directly; never force-push.
- Changes to `contracts/`, `.github/`, `scripts/`, `hk`, `pyproject.toml`, `PLAN.md` need the lead's approval.

## Team rules (from `.github/copilot-instructions.md`)

- Backend is Python + FastAPI + Pydantic. Don't add new libraries without asking.
- Stay inside the files of the current task; two people never edit the same file.
- Never put secrets, API keys, or personal data (phone numbers, emails) in code, logs or prompts.

## Copilot skills

`.github/skills/` defines three team workflows written for Copilot Chat; follow them if asked to do the same thing:
- **hk-plan** — turn `brief/` + `TEAM.md` + `docs/data-summary.md` into a one-page `PLAN.md` in a fixed format (read only those files, never raw data; on re-plan keep all IDs).
- **hk-fix** — resolve merge conflicts, keeping both sides where possible; ask when logic genuinely diverges.
- **hk-review** — review a PR against its `PLAN.md` "Done when" row; ≤8 lines, verdict MERGE / FIX FIRST, no style comments.
