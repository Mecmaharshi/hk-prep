---
name: hk-fix
description: Fix a git merge conflict after hk sync or hk push stops with "Conflict".
disable-model-invocation: true
---

# Fix a merge conflict

Be quick. Touch only the files with conflicts.

1. List them: `git diff --name-only --diff-filter=U`
2. In each file, look at every block between `<<<<<<<`, `=======` and `>>>>>>>`. Usually both sides should stay: combine them.
3. If both sides changed the same logic in different ways and you can't tell which is right, stop. Show the user both versions in 2–3 lines each, and ask.
4. Remove every conflict marker. If the file has tests that run fast, run them.
5. Save: `git add <files>`, then `git commit --no-edit`
6. Tell the user in 2 lines what you kept. Then they run: `hk push`

Never delete a teammate's work without asking. Never force-push.
