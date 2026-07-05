# Project context

This repository owns the shared `/btbai` pipeline for BToddB repositories.
Client repositories should call the reusable workflow at
`btoddb/btb-pipeline/.github/workflows/btb.yml@v1` instead of copying the
pipeline implementation.

## Shared agent contract

The shared `/btbai` command contract is injected at runtime from the
`SHARED_AGENT_CONTRACT` environment value in `.github/workflows/btb.yml`.
Update that workflow value, the executable workflow behavior, and
`requirements/spec/btb-workflow.md` together when command semantics or phase
boundaries change.

Do not paste the full shared contract into `CLAUDE.md`, `AGENTS.md`, client
`ai-rules`, or templates. Those files should contain local repo guidance and
short pointers only.

## Ship mechanics

Common `/btbai ship` release mechanics live in `scripts/btb-ship-base`. Client
repositories should customize release behavior with executable
`scripts/ship.d/` hooks or a thin `scripts/ship` wrapper, not by copying the
full base release script.

## Agent rules

- Treat `templates/` as client bootstrap material, not another source of truth
  for shared pipeline behavior.
- When a fix needs to reach client repositories, release this repository and move
  the floating `v1` tag as part of the ship flow.

- Follow every file in `ai-rules/` before editing.
- Work on a fresh branch from `main`; never edit directly on `main`.
- Keep the living spec in `requirements/spec/` synchronized with workflow
  behavior changes.
- For new code, always create a unit test
  - For Typescript, use Vitest
  - For Java, use JUnit 6
  - For Python, use Pytest
- If you can't make a needed change, give clear instructions on how I must manually change it.  Assume I'm a 5 year old that knows how to write, but I know nothing else.
