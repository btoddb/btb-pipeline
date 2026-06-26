#!/usr/bin/env bash
#
# Run OpenAI Codex CLI to implement the latest @btbai plan for a GitHub issue.
# Invoked by the `implement` job in templates/ai-pipeline.yml.
#
# Required env vars:
#   OPENAI_API_KEY    - OpenAI API key (set as a repo secret)
#   IMPLEMENT_MODEL   - OpenAI model id, e.g. "gpt-5.5"
#   ISSUE_NUMBER      - GitHub issue number to implement
#   GITHUB_REPOSITORY - "owner/repo" string
#   GH_TOKEN          - GitHub token for the gh CLI (PAT with PR write)
#
set -euo pipefail

ISSUE="${ISSUE_NUMBER:?ISSUE_NUMBER is required}"
REPO="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
MODEL="${IMPLEMENT_MODEL:-gpt-5.5}"
OUT="${GITHUB_OUTPUT:-/dev/null}"

# --- Fetch the latest btbai:plan comment -------------------------------------
echo "==> Fetching latest btbai:plan comment from issue #${ISSUE}..."
plan="$(gh issue view "$ISSUE" --repo "$REPO" --json comments \
  --jq '[.comments[] | select(.body | contains("btbai:plan"))] | last | .body // ""')"

if [ -z "$plan" ]; then
  echo "::error::No btbai:plan comment found on issue #${ISSUE}. Run @btbai plan first."
  printf 'failure_text=No plan comment found on issue #%s\n' "$ISSUE" >> "$OUT"
  exit 1
fi
echo "==> Plan found (${#plan} chars)."

# --- Create a timestamped branch ---------------------------------------------
TIMESTAMP="$(date -u +%Y%m%d-%H%M)"
BRANCH="btbai/issue-${ISSUE}-${TIMESTAMP}"
git config user.email "github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"
git checkout -b "$BRANCH"
echo "==> Created branch: ${BRANCH}"

# --- Install Codex CLI -------------------------------------------------------
echo "==> Installing @openai/codex..."
npm install -g @openai/codex --quiet

# --- Run Codex in full-auto (non-interactive) mode ---------------------------
PROMPT="$(printf '%s\n\n%s\n\n%s' \
  "You are implementing a plan for GitHub issue #${ISSUE} in the repository ${REPO}." \
  "Here is the approved plan to implement:" \
  "${plan}")"

echo "==> Running Codex (model=${MODEL})..."
set +e
codex --model "$MODEL" --approval-mode full-auto "$PROMPT"
codex_exit=$?
set -e

if [ $codex_exit -ne 0 ]; then
  echo "::error::Codex exited with non-zero status ${codex_exit}"
  printf 'failure_text=Codex exited with status %s\n' "$codex_exit" >> "$OUT"
  exit $codex_exit
fi

# --- Commit any changes Codex made -------------------------------------------
git add -A
if git diff --cached --quiet; then
  echo "::warning::No file changes detected after Codex run."
else
  git commit -m "$(printf 'feat: implement issue #%s via @btbai\n\nImplemented by OpenAI %s via Codex CLI.\n\nCloses #%s' \
    "$ISSUE" "$MODEL" "$ISSUE")"
  echo "==> Changes committed."
fi

# --- Push branch -------------------------------------------------------------
git push origin "$BRANCH"
echo "==> Branch pushed: ${BRANCH}"
printf 'branch=%s\n' "$BRANCH" >> "$OUT"

# --- Create PR (non-interactive, all flags explicit) -------------------------
PR_BODY="## Summary

Implementation of issue #${ISSUE} via the @btbai pipeline.

Implemented by: \`${MODEL}\` (OpenAI Codex)

Closes #${ISSUE}

---
Generated with [AI Pipeline](https://github.com/${REPO})"

pr_out="$(gh pr create \
  --base main \
  --head "$BRANCH" \
  --title "feat: implement issue #${ISSUE}" \
  --body "$PR_BODY" 2>&1)" && {
  echo "==> Pull request created: ${pr_out}"
  exit 0
}

# gh pr create returns non-zero when a PR already exists — that is not a failure.
if printf '%s' "$pr_out" | grep -qiE 'already exists|pull request.*already'; then
  echo "==> Pull request already exists: ${pr_out}"
  exit 0
fi

echo "::error::gh pr create failed: ${pr_out}"
printf 'failure_text=PR creation failed\n' >> "$OUT"
exit 1
