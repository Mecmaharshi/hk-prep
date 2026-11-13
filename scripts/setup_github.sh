#!/usr/bin/env bash
# One-time GitHub setup. The lead runs it once, before the event, from the team repo:
#   bash scripts/setup_github.sh teammate1 teammate2 ...    (their GitHub usernames)
# It makes you the approver for shared files, sets the merge rules and invites teammates.
set -euo pipefail

fail() { printf 'setup: %s\n' "$*" >&2; exit 1; }
command -v gh >/dev/null 2>&1 || fail "Install the GitHub CLI first: https://cli.github.com"
gh auth status >/dev/null 2>&1 || fail "Log in first: gh auth login"
cd "$(git rev-parse --show-toplevel)"
[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || fail "Switch to main first: git switch main"

repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
me=$(gh api user -q .login)

# 1. You approve changes to shared files (see .github/CODEOWNERS).
if grep -q '@LEAD_USERNAME' .github/CODEOWNERS; then
  sed -i.bak "s/@LEAD_USERNAME/@$me/g" .github/CODEOWNERS
  rm -f .github/CODEOWNERS.bak
  git add .github/CODEOWNERS
  git commit -q -m "Set @$me as the approver for shared files"
  git push -q origin main
fi
echo "Approver for shared files: @$me"

# 2. Squash merge only, PR title as the commit title, merged branches deleted.
gh api -X PATCH "repos/$repo" \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=BLANK >/dev/null
echo "Merges: squash only, branches deleted after merge"

# 3. main changes only through pull requests: 1 approval, checks must pass.
#    As the admin, you can still merge your own pull requests.
gh api -X PUT "repos/$repo/branches/main/protection" --input - >/dev/null <<'JSON'
{
  "required_status_checks": {"strict": false, "contexts": ["checks"]},
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": true,
    "dismiss_stale_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
echo "main: pull requests only, 1 approval, checks must pass"

# 4. Teammates get write access. They accept the invite email.
for user in "$@"; do
  user=${user#@}
  if gh api -X PUT "repos/$repo/collaborators/$user" >/dev/null 2>&1; then
    echo "Invited $user"
  else
    echo "Couldn't invite $user: check the username" >&2
  fi
done

echo "Done: $repo is ready."
