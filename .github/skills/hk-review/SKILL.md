---
name: hk-review
description: Quick review of a pull request against its task in PLAN.md. Use for changes to shared code (contracts/, config), or when asked. Most PRs don't need it: green checks + a look at the running app is enough.
argument-hint: "[PR number, or leave empty for your current branch]"
disable-model-invocation: true
---

# Quick review

Short, and only real problems. Skip style: the formatter handles it.

1. Get the changes: `gh pr diff <number>` if a number was given, otherwise `git diff origin/main...HEAD`
2. Find the task ID (like B-01) in the PR title or branch name. Read only that row of PLAN.md.
3. Check, in this order:
   - Does it do what "Done when" says?
   - Does it change files outside the row's **Files**? (`hk push` warns about this; here it's a FIX FIRST unless the PR says why.)
   - Does it change a shape in `contracts/` that others use?
   - Will anything crash the demo? Wrong field names, missing error handling at the API edge, secrets or personal data in code or logs.
4. Reply in at most 8 lines:

```
Verdict: MERGE   (or: FIX FIRST)
- <problem> · <file:line> · <one-line fix>
```

No praise, no summary of the code.
