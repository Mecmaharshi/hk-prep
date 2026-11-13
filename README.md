# Team repo

Plain commands for git and the API (fast, no AI), plus three short AI commands for Copilot.

## Setup, once per laptop

1. Install git, Python 3.12 and the GitHub CLI (`gh`). On Windows, use Git Bash.
2. `gh auth login`, then clone this repo and open its folder.
3. Run these:

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: source .venv/Scripts/activate
pip install -r backend/requirements.txt -r ml/requirements.txt
echo 'hk() { bash "$(git rev-parse --show-toplevel)/hk" "$@"; }' >> ~/.bashrc   # Mac: ~/.zshrc
```

Open a new terminal, then `hk run` starts the API at http://localhost:8000/docs.

## Every task

`hk start B-01` → write code → `hk push` → `hk pr` → a teammate approves → merge

- A red ✗ on your pull request means something broke: click it to see what.
- Changes to shared files (`contracts/`, `.github/`, `PLAN.md`) need the lead's approval.

## Where things go

- `contracts/api.py`: shapes everyone shares (lead only)
- `backend/app/`: the API · `backend/app/model.py`: where predictions come from
- `ml/`: data and model work · `ml/predict.py` plugs the model into the API (see `ml/README.md`)
- `frontend/`: create the app here; the checks build it automatically

## Lead only

- Before the event: create the team repo from this template, run `bash scripts/setup_github.sh` followed by your teammates' GitHub usernames, and fill in `TEAM.md`.
- At the start: problem into `brief/`, data into `data/`, run `hk data`, then `/hk-plan` in Copilot Chat.

## Stuck?

- "Conflict" → `/hk-fix` in Copilot Chat
- Anything else → `hk help`, or ask the lead
