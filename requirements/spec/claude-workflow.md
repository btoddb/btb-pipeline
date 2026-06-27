# Claude workflow

## Follow-up issues

1. **constraint CW-1** Every Claude-running phase (`respond`, `plan`,
   `implement`, `revise`, and `review`) may file follow-up GitHub issues with
   `gh issue create` when it discovers work that belongs outside the current
   task.
2. **constraint CW-2** Follow-up issue filing must use the workflow's
   `issues: write` GitHub token.
3. **constraint CW-3** Follow-up issue filing must not relax each phase's
   code-write boundary: `plan`, `review`, and `respond` remain unable to edit
   files or push branches through their Claude tool allow-lists.
