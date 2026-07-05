# BTB workflow

## Shared agent contract

1. **constraint BW-20** The reusable workflow must inject the shared `/btbai`
   command contract into every LLM-running phase at runtime. The injected
   contract must cover command routing, phase boundaries, code-write
   restrictions, PR/revision/review expectations, ship behavior, non-interactive
   GitHub CLI usage, the `[QUESTION]` planning gate signal (including the
   prohibition on hand-writing `<!-- btb:* -->` markers), and the review
   comment tag convention (`[REQUIRED]`/`[QUESTION]`/`[NIT]`/`[PRAISE]` plus a
   non-bare summary).
2. **constraint BW-21** Client repository templates must not require consumers
   to paste the full shared command contract into `CLAUDE.md`, `AGENTS.md`, or
   `ai-rules/PROJECT_CONTEXT.md`. Client agent files should contain only local
   repository guidance and short pointers because shared pipeline behavior is
   supplied by `btoddb/btb-pipeline@v1`.
3. **constraint BW-22** If command semantics or phase boundaries change, update
   `.github/workflows/btb.yml`, this living spec, and any client installation
   guidance together. Do not add another long-form copy of the contract as a
   template.
4. **constraint BW-23** Every `anthropics/claude-code-action@v1` step in the
   reusable workflow must set `trigger_phrase: "/btbai"`. The action has its own
   built-in trigger gate that defaults to `@claude` and silently skips running
   Claude (no error, no output) whenever no explicit `prompt` input is
   supplied and the triggering text does not contain the configured phrase.
   Without this override, any phase invoked without an explicit `prompt`
   (`plan`, `respond`, `revise`, `review`) would never actually run even
   though `dispatch` already routed the event on `/btbai`, producing a
   downstream "no output" failure instead of a clear error.

## Runtime setup

1. **constraint BW-24** The reusable workflow's `setup` input supports
   `python`, `node`, `java`, and `none`. Java setup must run in every
   validation/code-running phase that already supports Python and Node setup
   (`implement`, `revise`, and `review`), default to Java 25, use the Temurin
   distribution, and avoid mandatory dependency-cache preconditions so setup
   does not fail before Claude runs in repositories without committed Gradle
   metadata.
2. **constraint BW-25** Java repositories must be able to validate through the
   default Claude tool allow-lists: review may run Gradle test/check commands,
   and implementation/revision may run Gradle commands needed to build, test,
   and update project files.
3. **constraint BW-26** Review, revision, and implementation checkouts must use
   full git history so Gradle builds that derive versions from tags or commit
   history behave consistently across phases.

## Follow-up issues

1. **constraint BW-1** Every LLM-running phase (`respond`, `plan`,
   `implement`, `revise`, and `review`) may file follow-up GitHub issues with
   `gh issue create` when it discovers work that belongs outside the current
   task.
2. **constraint BW-2** Follow-up issue filing must use the workflow's
   `issues: write` GitHub token.
3. **constraint BW-3** Follow-up issue filing must not relax each phase's
   code-write boundary: `plan`, `review`, and `respond` remain unable to edit
   files or push branches through their Claude tool allow-lists.
4. **constraint BW-4** Phases must call `gh issue create` non-interactively,
   with `--title` and `--body` provided, so GitHub CLI does not prompt or fail
   for missing required input in CI.

## Ship command

1. **constraint BW-5** `/btbai ship` runs only on open pull requests. On an
   issue, it posts a notify message directing the user to comment on an open
   pull request instead.
2. **constraint BW-6** By default, ship requires all status checks to be green
   before merging. Failed, cancelled, timed-out, pending, and in-progress checks
   all block the merge, and the blocking comment must name each non-green check.
3. **constraint BW-7** `/btbai ship --force` skips the all-green guard and
   attempts the merge anyway.
4. **constraint BW-8** Ship squash-merges the pull request with
   `gh pr merge --squash --delete-branch` and deletes the head branch. The human
   `/btbai ship` comment is the approval signal; no separate approval command
   is required.
5. **constraint BW-9** After merging, ship checks out the updated `main` branch,
   checks out `btoddb/btb-pipeline@v1` into `.btb-pipeline`, and runs the
   repository release command.
6. **constraint BW-10** Before running the release command, ship configures the
   local checkout's Git author as `github-actions[bot]` so release hooks can
   create release commits and annotated tags in CI.
7. **constraint BW-11** If `scripts/ship` exists, ship runs it from the
   repository root with `BTB_PIPELINE_ROOT` pointing at the checked-out pipeline.
   If `scripts/ship` is missing, ship runs `.btb-pipeline/scripts/btb-ship-base`
   directly against the repository root.
8. **constraint BW-12** `scripts/btb-ship-base` owns common release mechanics:
   version/tag resolution, clean-main validation, duplicate-tag checks, optional
   `VERSION` updates, release commit creation when files changed, pushing
   `main`, creating the immutable version tag, and creating the GitHub release.
9. **constraint BW-13** The base release command supports repo-local executable
   hooks under `scripts/ship.d/` named `before-version`, `after-version`,
   `before-release-commit`, `after-release-commit`, `before-github-release`, and
   `after-github-release`. Hooks receive `BTB_REPO_ROOT`, `BTB_VERSION_TAG`,
   `BTB_PUBLIC_RELEASE`, `BTB_DRY_RUN`, `BTB_BUMP`, and
   `BTB_RELEASE_COMMIT_CREATED`.
10. **constraint BW-14** Client release commands and the base release command
   must support `--public-release`, `--bump-patch`, `--bump-minor`,
   `--bump-major`, and `--dry-run`; `--set-version vX.Y.Z` remains supported for
   explicit releases. The workflow forwards all non-`--force` ship arguments to
   the release command. Non-public releases create a pre-release titled
   `<tag>-beta`, and exactly one version option is required.
11. **constraint BW-27** `scripts/ship` in `btoddb/btb-pipeline` uses the shared
   base release command, requires releases to stay under the `v1` major line,
   and then floats the lightweight `v1` major tag directly to the released
   commit. When it runs in GitHub Actions, it skips the interactive confirmation
   prompt automatically.
12. **constraint BW-15** On any ship failure, including preflight, merge, and
    release-hook failures, the `report-failure` action tags the maintainer with
    the phase name `Ship`.

## Plan-to-implementation handoff

1. **constraint BW-16** When planning posts a control marker, the marker must
   identify the approved plan comment with `<!-- btb:plan-comment-id:... -->`
   while preserving the existing `<!-- btb:plan -->` and
   `<!-- btb:proceed -->` markers.
2. **constraint BW-17** The implement job must resolve the approved plan comment
   before running Claude. It should prefer the explicit plan-comment id and fall
   back to the latest non-marker, non-`github-actions` comment before the marker
   for older control comments.
3. **constraint BW-18** The implement job must pass the approved plan body to
   Claude as explicit implementation-phase prompt context. Sonnet must execute
   that plan, not rediscover it from issue comments created after the trigger.
   The action must still run in tag/track-progress mode so it creates the normal
   implementation branch and tracking comment.
4. **constraint BW-19** A successful implement job must leave an implementation
   pull request open. If Claude does not open one, the workflow must create it
   from the pushed implementation branch or fail with an explanatory issue comment when
   no branch or no diff exists.
