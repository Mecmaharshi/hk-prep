# Team rules

- Keep answers short and in plain English. Explain only when asked.
- Map: shared shapes `contracts/api.py` · API `backend/app/` · predictions `backend/app/model.py` · LLM calls `backend/app/llm/` (use `ask(prompt)`) · ML `ml/predict.py` · website `frontend/src/` · plan `PLAN.md` · team board http://localhost:8000/board.
- Backend: Python, FastAPI, Pydantic. Frontend: React, TypeScript, Tailwind. Don't add new libraries without asking.
- Change `contracts/` only with the lead.
- Never put secrets, API keys or personal data (phone numbers, emails) in code, logs or AI prompts. Keys live in `.env` only.
- Stay inside the **Files** of your task's row in `PLAN.md`. Need another file? Say so and stop.
- Team commands: `hk help`. Start the API: `hk run`. Start the website: `hk web`.

## Save AI credits
- One task per chat: `hk start B-01`, then `/hk-task B-01`. Start a new chat for the next task.
- In Copilot's model picker use the model marked **0x** or **included** for normal tasks. Switch to a premium model only when the cheap one is stuck.
- Don't ask the agent to explore the repo or explain it: the row in PLAN.md and `hk status` already say what you need.
- Don't ask the agent to review what the checks already check. Green checks + the app runs = good enough to merge.
