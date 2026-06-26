#!/usr/bin/env bash
#
# Run OpenAI Codex CLI to revise code on an existing PR branch.
# Invoked by the `revise` job in templates/ai-pipeline.yml.
#
# Required env vars:
#   OPENAI_API_KEY    - OpenAI API key (set as a repo secret)
#   IMPLEMENT_MODEL   - OpenAI model id, e.g. "gpt-5.5"
#   PR_NUMBER         - GitHub PR number being revised
#   GITHUB_REPOSITORY - "owner/repo" string
#   COMMENT_BODY      - Full body of the trigger comment (contains the feedback)
#
set -euo pipefail

MODEL="${IMPLEMENT_MODEL:-gpt-5.5}"
PR_NUMBER="${PR_NUMBER:?PR_NUMBER is required}"
REPO="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
OUT="${GITHUB_OUTPUT:-/dev/null}"

# Strip the "@btbai revise" prefix to extract the actionable feedback.
RAW_COMMENT="${COMMENT_BODY:-}"
feedback="$(printf '%s' "$RAW_COMMENT" | sed -E 's/^[[:space:]]*@btbai[[:space:]]+revise[[:space:]]*//')"
[ -z "$feedback" ] && feedback="$RAW_COMMENT"

if [ -z "$feedback" ]; then
  echo "::error::No revision feedback found in the trigger comment."
  printf 'failure_text=No revision feedback in trigger comment\n' >> "$OUT"
  exit 1
fi
echo "==> Feedback extracted (${#feedback} chars)."

git config user.email "github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"

# --- Install Codex CLI -------------------------------------------------------
echo "==> Installing @openai/codex..."
npm install -g @openai/codex --quiet

# --- Run Codex in full-auto (non-interactive) mode ---------------------------
PROMPT="$(printf '%s\n\n%s\n\n%s' \
  "You are revising code on pull request #${PR_NUMBER} in the repository ${REPO}." \
  "Apply the following review feedback precisely — only change what is explicitly requested:" \
  "${feedback}")"

echo "==> Running Codex for revision (model=${MODEL})..."
set +e
codex --model "$MODEL" --approval-mode full-auto "$PROMPT"
codex_exit=$?
set -e

if [ $codex_exit -ne 0 ]; then
  echo "::error::Codex exited with non-zero status ${codex_exit}"
  printf 'failure_text=Codex exited with status %s\n' "$codex_exit" >> "$OUT"
  exit $codex_exit
fi

# --- Commit and push changes -------------------------------------------------
git add -A
if git diff --cached --quiet; then
  echo "==> No file changes detected after Codex revision."
else
  git commit -m "$(printf 'fix: revise PR #%s per @btbai feedback\n\nRevised by OpenAI %s via Codex CLI.' \
    "$PR_NUMBER" "$MODEL")"
  git push origin HEAD
  echo "==> Revision committed and pushed."
fi
