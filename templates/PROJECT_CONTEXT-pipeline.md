# Project context template for client repositories

## Remove this after reading

The shared `/btbai` command contract is injected at runtime by
`btoddb/btb-pipeline`. Do not paste that shared workflow behavior into client
repositories; copied contract text drifts as the pipeline evolves.

Use the client repository's `ai-rules/PROJECT_CONTEXT.md` only for local facts
the shared pipeline cannot know, such as:

- repository layout and important source directories
- repo-specific lint, test, build, deploy, or validation commands
- generated artifacts that are intentionally committed
- release details that differ from the standard `scripts/ship` contract
- project-specific security or review constraints

Keep those local rules short and specific. When the shared pipeline behavior
changes, update `btoddb/btb-pipeline` and release the moving `v1` tag instead
of editing every client repository.

## Agent rules

- Follow every file in `ai-rules/` before editing.
- Work on a fresh branch from `main`; never edit directly on `main`.
- Keep the living spec in `requirements/spec/` synchronized with workflow
  behavior changes.
- For new code, always create a unit test
  - For Typescript, use Vitest
  - For Java, use JUnit 6
  - For Python, use Pytest