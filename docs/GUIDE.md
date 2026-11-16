# Team guide

Everything in this repo exists for one reason: ship fast in 24 hours, with everyone in sync and without wasting AI credits.

**The one idea:** `one task = one Copilot chat = one pull request`. You pick a task, your AI agent builds it in that task's files, you push, a teammate approves, done. Repeat.

Windows users: wherever this guide says `hk ...`, type `.\hk ...` in PowerShell (or use Git Bash and type `hk ...`).

---

## 1. Before the event: everyone (20 minutes)

1. Install: [Git](https://git-scm.com), [Python 3.12](https://python.org), [Node.js LTS](https://nodejs.org), [GitHub CLI](https://cli.github.com), [VS Code](https://code.visualstudio.com) with the GitHub Copilot extension.
2. Tell git who you are. **Use the same name the lead puts in TEAM.md**, so the board knows your work is yours:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   gh auth login
   ```
3. Accept the GitHub invite email, then clone the team repo and open the folder in VS Code.
4. In the terminal:
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate        # Mac/Linux: source .venv/bin/activate
   pip install -r backend/requirements.txt -r ml/requirements.txt
   ```
5. Run `hk doctor`. It checks your laptop and tells you exactly what to fix. Repeat until it says **Ready**.
6. Run `hk run`, open http://localhost:8000/board. If you see the board, you're set.

## 2. Before the event: lead (30 minutes)

1. Create the team repo from this template on GitHub.
2. Run `bash scripts/setup_github.sh teammate1 teammate2 ...` (GitHub usernames). It invites everyone, protects `main`, sets squash-merge, and makes you the approver for shared files.
3. Fill in `TEAM.md`: names (exactly as in each person's `git config user.name`), roles, what they're good at, hours they can work, and the `Ends:` time.
4. Hold a **1-hour rehearsal**: everyone runs `hk doctor`, then does one tiny practice task end to end (section 4). This is where laptop problems and "how does this work" questions get solved, for free.

## 3. At the start of the event: lead (first hour)

| Step | Do this | Result |
|---|---|---|
| 1 | Put the problem statement into `brief/problem.md` (and the judging rules) | The planner can read it |
| 2 | Put the data into `data/` and run `hk data` | `docs/data-summary.md`: a safe summary (phones/emails masked). Raw data never leaves your laptop |
| 3 | Copy `.env.example` to `.env`, set `LLM_PROVIDER` and the key the contest gave you | `ask(prompt)` gives real answers; check the board's LLM tab |
| 4 | In Copilot Chat: `/hk-plan` | A one-page `PLAN.md`: goal, backup plan, demo steps, and the task table |
| 5 | Read the plan, fix what's wrong, commit it to `main` | `hk status` and the board show every task as free |
| 6 | Do A-01 yourself: the real shapes in `contracts/api.py` | Everyone else can start building against them |

Re-plan later with `/hk-plan what changed`. Task IDs never change.

## 4. Every task: everyone

```
hk status                 1. see which tasks are free. "anyone" = anyone can do it
hk start F-02             2. claim it. It's yours now; the team sees it instantly
/hk-task F-02             3. in a NEW Copilot chat. The agent reads the task row, builds it in
                             that task's files only, checks "Done when", and says: Run: hk push
hk push                   4. tidies, syncs with the team, pushes. Warns if you touched other tasks' files
hk pr                     5. opens the pull request. Ask a teammate to approve
                          6. teammate approves → click "Squash and merge" on GitHub → done
```

What each task row gives you (and the agent):

| Column | Meaning |
|---|---|
| **ID** | `B-01` = backend, `F-` frontend, `M-` data/ML, `A-` lead |
| **Task** | What to build, one line |
| **For** | `anyone` / `dev` / `lead` / a name. Pick tasks meant for you |
| **Files** | The files this task owns. Nobody else touches them |
| **Needs** | A task that must be done first (check `hk status`) |
| **Done when** | How you and the reviewer know it's finished |

Tips: `hk start B-01` again later brings you back to that branch. If the agent says it needs a file outside its list, stop and ask the lead. Not finished yet but want to save? `hk push` any time; the PR waits.

## 5. Reviewing a teammate's pull request: anyone

1. Open the PR link. Green check = the automatic checks passed. Red X = click it, see what broke, tell them.
2. Read the PR body: it shows the task's **Done when**. Is it met? If you can, pull the branch and look (`gh pr checkout 12`, then `hk run` / `hk web`).
3. Did it change files outside its **Files**? The PR should say why. If not, ask.
4. Approve → "Squash and merge". No style comments, no AI review needed. Shared files (`contracts/`, `.github/`, `PLAN.md`) need the lead's approval.

## 6. The team board: http://localhost:8000/board

Runs with `hk run`; `hk board` opens it. Reads the plan from GitHub, so it's the team's truth, not your copy. Refreshes itself. This guide is there too: http://localhost:8000/guide (searchable, with a PowerShell switch).

| Tab | Shows | Use it to |
|---|---|---|
| **Overview** | Done / in progress / free, hours left, model, LLM, PRs waiting | Check-ins. Put it on the projector |
| **Plan** | Every task with live state, who's on it, files, done-when. Filters: Free · For anyone · Mine | Pick your next task (click a row: it copies `hk start ...`) |
| **Team** | Who's on what right now, what each person has finished | See who's free to help |
| **API** | Health, model real/fake, every endpoint with the fields it takes and returns | Frontend people: read shapes here, not Python |
| **LLM** | Provider, model, key set or not, a **Test** button, the `.env` lines to copy | Check the LLM works before building on it |
| **Data** | The data summary, files in `data/` | Data people, without opening raw files |
| **Checks** | `hk doctor` for this laptop, CI on `main`, open PRs with their checks and review state | Day one, and "is anything stuck?" |

## 7. Commands

| Command | What it does |
|---|---|
| `hk doctor` | Is this laptop ready? ✓ fine · ! works but could be better · ✗ must fix |
| `hk status` | Who is doing what; which tasks are free |
| `hk start B-01` | Claim a task on a fresh branch (`--join` to share one with a teammate) |
| `hk push` | Tidy, sync with the team, push |
| `hk pr` | Open the pull request (or give you the link) |
| `hk sync` | Get the team's latest work into your branch |
| `hk run` | Start the API: http://localhost:8000/docs and the board |
| `hk web` | Start the website (installs its packages the first time) |
| `hk board` | Open the board in the browser |
| `hk data [file]` | Summarise a dataset into `docs/data-summary.md` |
| `hk help` | This list |

Copilot Chat commands (type them in the chat box):

| Command | Who | What |
|---|---|---|
| `/hk-task B-01` | everyone | Do the task you started. One task per chat |
| `/hk-plan` | lead | Problem → `PLAN.md` |
| `/hk-fix` | anyone | Fix a merge conflict after `hk push` says "Conflict" |
| `/hk-review 12` | optional | Quick review of PR 12, for shared code |

## 8. The project, folder by folder

| Folder / file | What lives there | Who touches it |
|---|---|---|
| `contracts/api.py` | The shapes everyone shares (`Item`, `Prediction`, ...) | Lead only |
| `backend/app/main.py` | The API: `/health`, `/predict` | Backend tasks |
| `backend/app/model.py` | Where predictions come from. Uses `ml/predict.py` if it exists, otherwise simple backup rules | Backend / ML |
| `backend/app/llm/` | `ask(prompt)`: the one way to call an LLM | Anyone, via `ask` |
| `backend/app/board/` | The team board | Nobody needs to |
| `backend/tests/` | Tests. The checks run them on every PR | Backend tasks |
| `ml/` | Data and model work. `ml/predict.py` plugs the model into the API | ML tasks |
| `frontend/src/` | The website. `api.ts` is the only file that talks to the API | Frontend tasks |
| `data/` | Raw data. Never pushed | Lead puts it there |
| `docs/data-summary.md` | The safe data summary from `hk data` | Read-only |
| `brief/` | Problem statement and judging rules | Lead |
| `PLAN.md` | The task table | Lead (via `/hk-plan`) |
| `TEAM.md` | People, roles, hours, `Ends:` time | Lead |
| `.env` | LLM provider and key. Never pushed | Each laptop |

## 9. Using the LLM in code

```python
from backend.app.llm import ask

summary = ask("Summarise this complaint in one line: " + text)
labels = ask(prompt, system="Answer with one word: Water, Roads or Power.")
```

Switch provider in `.env`, then restart `hk run`:

```
LLM_PROVIDER=claude        # or: openai · fake
LLM_MODEL=                 # optional, e.g. claude-opus-5-5 or gpt-4.1
ANTHROPIC_API_KEY=...      # for claude
OPENAI_API_KEY=...         # for openai
OPENAI_BASE_URL=           # optional: Groq, OpenRouter, Ollama, Gemini-compatible
```

No key → `fake` answers, always the same for the same prompt. Tests use the fake. The board's LLM tab shows which one is live.

## 10. Plugging in the ML model

Write `ml/predict.py` with one function (see `ml/README.md`):

```python
from contracts.api import Item, Prediction

# load model files here, once, from ml/artifacts/

def predict(items: list[Item]) -> list[Prediction]:
    ...  # one Prediction per item, same order
```

The API switches to it by itself. `/health` says `"model": "real"`. Files over 5 MB can't be pushed: share by drive. Extra packages go in `ml/requirements.txt`.

## 11. The website

`hk web` → http://localhost:5173. React + TypeScript + Tailwind. `src/api.ts` mirrors `contracts/api.py`: when the lead changes the shapes, update the types there (the board's API tab shows them). `src/App.tsx` is a working start page: replace it.

## 12. Saving AI credits

- **One task per chat.** `hk start`, then `/hk-task` in a **new** chat. Next task, new chat.
- In Copilot's model picker, use the model marked **0x** or **included**. Premium models only when the cheap one is stuck.
- Don't ask the agent to explore or explain the repo. The task row and `hk status` already say what you need; the board shows the rest.
- Don't ask the agent to review what the checks already check. Green + it runs = merge.
- Good task rows save the most: exact **Files**, a checkable **Done when**. Lead: spend two minutes per row.

## 13. When something goes wrong

| You see | Do |
|---|---|
| `hk` not recognised (PowerShell) | Type `.\hk` instead, or use Git Bash |
| `hk doctor` shows ✗ | Follow the → line under it, run `hk doctor` again |
| "X is already on B-01" | Pick another task. Or, if you agreed to share: `hk start B-01 --join` |
| "Conflict" after `hk push` | `/hk-fix` in Copilot Chat, then `hk push` |
| "Heads-up: these files aren't in ... Files" | Fine if on purpose: say why in the PR. Otherwise undo that change |
| "Not pushed. These files should not go to GitHub" | A secret or a huge file: add it to `.gitignore`, `hk push` again |
| Red X on the PR | Click it, read the failing step, fix, `hk push` |
| Board says "Couldn't load" | The API isn't running: `hk run` |
| Model shows **fake** | `ml/predict.py` isn't in yet, or didn't load: the note says why. The demo still works |
| LLM shows **fake** | No key in `.env`, or the SDK can't load on this laptop (the Checks tab says). The demo still works |
| Lost | `hk help`, or ask the lead |

## 14. Rules

- Never commit to `main` directly. Never force-push. `hk` won't let you by accident.
- Stay inside your task's **Files**. Two people never edit the same file.
- No keys, passwords, phone numbers or emails in code, logs or prompts. Keys live in `.env` only.
- Shared files (`contracts/`, `.github/`, `scripts/`, `hk`, `PLAN.md`) change only with the lead.
- Don't add libraries without asking.
