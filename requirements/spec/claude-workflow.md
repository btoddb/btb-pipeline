# Claude workflow

## Shared agent contract

1. **constraint CW-20** The reusable workflow must inject the shared `@claude`
   command contract into every Claude-running phase at runtime. The injected
   contract must cover command routing, phase boundaries, code-write
   restrictions, PR/revision/review expectations, ship behavior, non-interactive
   GitHub CLI usage, the `[QUESTION]` planning gate signal (including the
   prohibition on hand-writing `<!-- claude:* -->` markers), and the review
   comment tag convention (`[REQUIRED]`/`[QUESTION]`/`[NIT]`/`[PRAISE]` plus a
   non-bare summary).
2. **constraint CW-21** Client repository templates must not require consumers
   to paste the full shared command contract into `CLAUDE.md`, `AGENTS.md`, or
   `ai-rules/PROJECT_CONTEXT.md`. Client agent files should contain only local
   repository guidance and short pointers because shared pipeline behavior is
   supplied by `btoddb/claude-pipeline@v1`.
3. **constraint CW-22** If command semantics or phase boundaries change, update
   `.github/workflows/claude.yml`, this living spec, and any client installation
   guidance together. Do not add another long-form copy of the contract as a
   template.

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
4. **constraint CW-4** Phases must call `gh issue create` non-interactively,
   with `--title` and `--body` provided, so GitHub CLI does not prompt or fail
   for missing required input in CI.

## Ship command

1. **constraint CW-5** `@claude ship` runs only on open pull requests. On an
   issue, it posts a notify message directing the user to comment on an open
   pull request instead.
2. **constraint CW-6** By default, ship requires all status checks to be green
   before merging. Failed, cancelled, timed-out, pending, and in-progress checks
   all block the merge, and the blocking comment must name each non-green check.
3. **constraint CW-7** `@claude ship --force` skips the all-green guard and
   attempts the merge anyway.
4. **constraint CW-8** Ship squash-merges the pull request with
   `gh pr merge --squash --delete-branch` and deletes the head branch. The human
   `@claude ship` comment is the approval signal; no separate approval command
   is required.
5. **constraint CW-9** After merging, ship checks out the updated `main` branch
   and runs `scripts/ship` in the repository root.
6. **constraint CW-10** Before running `scripts/ship`, ship configures the local
   checkout's Git author as `github-actions[bot]` so per-repository release
   hooks can create release commits and annotated tags in CI.
7. **constraint CW-11** If `scripts/ship` is missing, ship fails with guidance to
   create one from `templates/ship.template`.
8. **constraint CW-12** `scripts/ship` is the per-repository release hook. The
   pipeline's `templates/ship.template` is a reference implementation that
   creates a pre-release by default.
9. **recommendation CW-13** Client `scripts/ship` implementations should support
   `--public-release`, `--bump-patch`, `--bump-minor`, and `--bump-major`. The
   workflow forwards these flags to `scripts/ship`; `--public-release` creates a
   public latest release, non-public releases append a `beta` suffix to the
   version/tag, and exactly one bump flag is required to increment the release
   version by patch, minor, or major.
10. **constraint CW-14** `scripts/ship` in `btoddb/claude-pipeline` keeps the
   reusable-workflow release behavior by floating the lightweight `v1` major tag
   directly to the released commit while accepting the same release flags as
   `templates/ship.template`. When it runs in GitHub Actions, it skips the
   interactive confirmation prompt automatically.
11. **constraint CW-15** On any ship failure, including preflight, merge, and
    release-hook failures, the `report-failure` action tags the maintainer with
    the phase name `Ship`.

## Plan-to-implementation handoff

1. **constraint CW-16** When planning posts a control marker, the marker must
   identify the approved plan comment with `<!-- claude:plan-comment-id:... -->`
   while preserving the existing `<!-- claude:plan -->` and
   `<!-- claude:proceed -->` markers.
2. **constraint CW-17** The implement job must resolve the approved plan comment
   before running Claude. It should prefer the explicit plan-comment id and fall
   back to the latest non-marker, non-`github-actions` comment before the marker
   for older control comments.
3. **constraint CW-18** The implement job must pass the approved plan body to
   Claude as explicit implementation-phase prompt context. Sonnet must execute
   that plan, not rediscover it from issue comments created after the trigger.
   The action must still run in tag/track-progress mode so it creates the normal
   Claude branch and tracking comment.
4. **constraint CW-19** A successful implement job must leave an implementation
   pull request open. If Claude does not open one, the workflow must create it
   from the pushed Claude branch or fail with an explanatory issue comment when
   no branch or no diff exists.
