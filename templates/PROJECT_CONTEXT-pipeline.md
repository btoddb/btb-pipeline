# Project context template for client repositories

The shared `@claude` command contract is injected at runtime by
`btoddb/claude-pipeline`. Do not paste that shared workflow behavior into client
repositories; copied contract text drifts as the pipeline evolves.

Use the client repository's `ai-rules/PROJECT_CONTEXT.md` only for local facts
the shared pipeline cannot know, such as:

- repository layout and important source directories
- repo-specific lint, test, build, deploy, or validation commands
- generated artifacts that are intentionally committed
- release details that differ from the standard `scripts/ship` contract
- project-specific security or review constraints

Keep those local rules short and specific. When the shared pipeline behavior
changes, update `btoddb/claude-pipeline` and release the moving `v1` tag instead
of editing every client repository.
