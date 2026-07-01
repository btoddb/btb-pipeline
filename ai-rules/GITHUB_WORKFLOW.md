# GitHub workflow rules

The reusable workflow in `.github/workflows/btb.yml` is the executable source
of truth for `/btbai` command routing, phase boundaries, tool allow-lists, and
runtime-injected shared agent instructions.

`requirements/spec/btb-workflow.md` is the living behavioral spec. Any
workflow behavior change must update both the workflow and the matching spec
constraint.

Do not maintain a second full copy of the shared command contract in
`CLAUDE.md`, `AGENTS.md`, `ai-rules/PROJECT_CONTEXT.md`, or client repository
templates. Those files should contain only local repository guidance or a short
pointer to the workflow/spec source of truth.

When changing client installation guidance, prefer a tiny caller workflow plus
repo-local configuration over copied shared markdown. Client repositories should
receive shared `/btbai` behavior by calling `btoddb/btb-pipeline@v1`.
