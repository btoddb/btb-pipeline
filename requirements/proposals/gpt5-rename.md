# Proposal: Move code-writing to GPT-5.5, rename to @btbai / ai-pipeline

**Status:** Shipped (branch `btbai/issue-2-*`)
**Issue:** #2
**Author:** btoddb

---

## Summary

Move the code-writing phases (`implement` and `revise`) from Claude Sonnet to
OpenAI GPT-5.5, keep planning and reviewing on Claude Opus, rename the pipeline
from `@claude` / `claude-pipeline` to `@btbai` / `ai-pipeline`.

---

## Decisions (locked)

| ID | Decision | Value |
|---|---|---|
| P2-1 | GPT mechanism | OpenAI Codex CLI (`@openai/codex`) via `scripts/gpt-implement.sh` and `scripts/gpt-revise.sh` |
| P2-2 | GPT model id | `gpt-5.5` (pinned as `implement-model` input default) |
| P2-3 | New command word | `@btbai` (hard replaces `@claude` — no alias kept) |
| P2-4 | Repo rename | `btoddb/claude-pipeline` → `btoddb/ai-pipeline` |
| P2-5 | Transition style | Hard switch (no `@claude` alias) |
| P2-6 | Respond/follow-up | Stays Claude (Opus for PR reviews, Sonnet for follow-ups) |
| P2-7 | Token name | `CLAUDE_CODE_OAUTH_TOKEN` unchanged (still Claude-specific) |

---

## Behavior changes (rules)

### P2-8 — Model routing

| Phase | Before | After |
|---|---|---|
| Plan | `claude-sonnet-4-6` | `claude-opus-4-8` (unchanged) |
| Implement | `claude-sonnet-4-6` | `gpt-5.5` via Codex CLI |
| Revise | `claude-sonnet-4-6` | `gpt-5.5` via Codex CLI |
| Review | `claude-opus-4-8` | `claude-opus-4-8` (unchanged) |
| Respond | `claude-opus-4-8` / `claude-sonnet-4-6` | unchanged |

### P2-9 — Trigger phrase

`@claude` → `@btbai` (hard switch). A comment with `@claude` no longer starts
the pipeline.

### P2-10 — Markers

`<!-- claude:plan -->` / `<!-- claude:proceed -->` → `<!-- btbai:plan -->` /
`<!-- btbai:proceed -->`. The implement job looks for `btbai:plan` in comments.

### P2-11 — Branch prefix

`claude/issue-<n>-<ts>` → `btbai/issue-<n>-<ts>`

### P2-12 — Secrets

Added: `OPENAI_API_KEY`, `PIPELINE_WORKFLOWS_PAT`
Unchanged: `CLAUDE_CODE_OAUTH_TOKEN`

### P2-13 — Self-permissioning

The `implement` and `revise` jobs check out using `PIPELINE_WORKFLOWS_PAT`
(a fine-grained PAT with Workflows R/W), enabling them to push commits that
include changes to `.github/workflows/**` without manual intervention.

### P2-14 — log-model action

Added `model` input: when provided, reports that model id directly instead of
reading from the claude-code-action execution file. GPT phases pass
`model: ${{ inputs.implement-model }}`.

Added `model-prefix` input: controls the prefix filter when reading from an
execution file. Defaults to `claude` (preserves existing Claude-phase behavior).

### P2-15 — report-failure action

Added `failure-text` input: when provided, uses this text for failure
classification instead of reading from the execution file. GPT scripts emit
`failure_text` via `$GITHUB_OUTPUT`.

Added OpenAI-specific error patterns to the usage-limit heuristic:
`insufficient_quota`, `rate_limit_exceeded`.

---

## Files changed

| File | Change |
|---|---|
| `scripts/gpt-implement.sh` | New — Codex CLI engine for implement |
| `scripts/gpt-revise.sh` | New — Codex CLI engine for revise |
| `actions/log-model/action.yml` | Updated — `model` + `model-prefix` inputs |
| `actions/report-failure/action.yml` | Updated — `failure-text` input + OpenAI heuristics |
| `templates/ai-pipeline.yml` | New — staged reusable workflow (copy to `.github/workflows/`) |
| `templates/ai-pipeline-caller.yml` | New — staged caller for this repo |
| `templates/caller-ai-pipeline.yml.template` | New — consumer template |
| `templates/CLAUDE-pipeline.md` | Updated — `@btbai`, model table, markers |
| `CLAUDE.md` | Updated — same as above |
| `INSTALL.md` | New — canonical install doc |
| `INSTALL-IN-CLIENT-REPO.md` | Rewritten — detailed client repo setup |
| `INSTALL-WORKFLOW.md` | Updated — pointer to INSTALL.md |
| `RELEASING.md` | Updated — `ai-pipeline` action paths |
| `scripts/ship.sh` | Updated — header comment references `ai-pipeline` |
| `MIGRATION.md` | New — one-time bootstrap checklist |
