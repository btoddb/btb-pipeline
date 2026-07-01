# Project context

This repository owns the shared `@claude` pipeline for BToddB repositories.
Client repositories should call the reusable workflow at
`btoddb/claude-pipeline/.github/workflows/claude.yml@v1` instead of copying the
pipeline implementation.

## Shared agent contract

The shared `@claude` command contract is injected at runtime from the
`SHARED_AGENT_CONTRACT` environment value in `.github/workflows/claude.yml`.
Update that workflow value, the executable workflow behavior, and
`requirements/spec/claude-workflow.md` together when command semantics or phase
boundaries change.

Do not paste the full shared contract into `CLAUDE.md`, `AGENTS.md`, client
`ai-rules`, or templates. Those files should contain local repo guidance and
short pointers only.

## Codex rules

- Follow every file in `ai-rules/` before editing.
- Work on a fresh branch from `main`; never edit directly on `main`.
- Keep the living spec in `requirements/spec/` synchronized with workflow
  behavior changes.
- Treat `templates/` as client bootstrap material, not another source of truth
  for shared pipeline behavior.
- When a fix needs to reach client repositories, release this repository and move
  the floating `v1` tag as part of the ship flow.
