# Team repo

Plain commands for git and the API (fast, no AI), plus four short AI commands for Copilot. One task = one chat = one pull request.

**New here? Read [docs/GUIDE.md](docs/GUIDE.md): the step-by-step guide to everything.** (Nicer to read at http://localhost:8000/guide once `hk run` is up.)

## Setup, once per laptop

1. Install git, Python 3.12, Node.js (LTS) and the GitHub CLI (`gh`). On Windows, use Git Bash.
2. `gh auth login`, then clone this repo and open its folder.
3. Run these:

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: source .venv/Scripts/activate
pip install -r backend/requirements.txt -r ml/requirements.txt
echo 'hk() { bash "$(git rev-parse --show-toplevel)/hk" "$@"; }' >> ~/.bashrc   # Mac: ~/.zshrc
```

4. Open a new terminal and run `hk doctor`. Fix anything marked ✗. Do this **before** the event.

Windows, PowerShell or cmd: type `.\hk doctor` (with the `.\`) instead of `hk doctor`. Everything else is the same.

`hk run` starts the API (http://localhost:8000/docs) and the team board (http://localhost:8000/board). `hk web` starts the website.

## Every task

```
hk status          → pick a free task (anyone = anyone can do it)
hk start F-02      → it's yours; the team sees it on the board
/hk-task F-02      → in a NEW Copilot chat: the agent builds it, in that task's files only
hk push            → tidy, sync, push (warns if you touched other tasks' files)
hk pr              → a teammate approves (green checks + it runs = merge)
```

- A red ✗ on your pull request means something broke: click it to see what.
- Changes to shared files (`contracts/`, `.github/`, `PLAN.md`) need the lead's approval.
- Save credits: one task per chat, the 0x/"included" model unless stuck, don't ask the agent to explore or explain.

## Where things go

- `contracts/api.py`: shapes everyone shares (lead only) · mirrored in `frontend/src/api.ts`
- `backend/app/`: the API · `backend/app/model.py`: where predictions come from · `backend/app/llm/`: `ask(prompt)` for any LLM
- `ml/`: data and model work · `ml/predict.py` plugs the model into the API (see `ml/README.md`)
- `frontend/`: the website (React + Tailwind); `hk web` runs it
- `backend/app/board/`: the team board (plan, team, API, LLM, data, checks)
- `.env` (copy `.env.example`): the LLM provider and key. Never pushed.

## Lead only

- Before the event: create the team repo from this template, run `bash scripts/setup_github.sh` followed by your teammates' GitHub usernames, fill in `TEAM.md` (names must match each person's `git config user.name`, plus the `Ends:` time), and hold a 1-hour rehearsal: everyone runs `hk doctor` and does one tiny practice task end to end.
- At the start: problem into `brief/`, data into `data/`, run `hk data`, then `/hk-plan` in Copilot Chat. Put the contest's LLM key in `.env`.
- The board's Overview tab is the check-in screen.

## Stuck?

- "Conflict" → `/hk-fix` in Copilot Chat
- Anything else → `hk help`, the board's Checks tab, or ask the lead
