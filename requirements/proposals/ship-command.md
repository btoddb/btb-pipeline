# ship command

**Status:** shipped

## Goal

Merge an open PR to main and cut a GitHub release from a single `@claude ship`
comment, removing the manual merge + release steps from each PR landing.

## Behavior

1. **constraint** `@claude ship` is PR-only; on an issue it posts a `notify` message
   directing the user to an open pull request.
2. **constraint** By default, ship refuses to merge if any required check has a
   `FAILURE`, `TIMED_OUT`, or `CANCELLED` conclusion. Add `--force` to the comment
   (`@claude ship --force`) to skip the guard and merge anyway.
3. **constraint** Ship squash-merges the PR (`gh pr merge --squash --delete-branch
   --yes`) and deletes the head branch. The human's `@claude ship` comment is the
   approval signal — no separate `gh pr review --approve` step is needed.
4. **constraint** After merging, the job checks out the updated `main` and runs
   `scripts/ship` if the file exists. If the script is missing the job fails with
   guidance to create one from `templates/ship.template`.
5. **constraint** `scripts/ship` is the per-repo release hook. The pipeline ships
   `templates/ship.template` as a reference implementation that defaults to a
   pre-release: creates an annotated git tag, pushes it, then calls
   `gh release create --prerelease` with auto-generated notes and the title
   `<version>-beta`.
6. Passing `--public-release` in the comment forwards the flag to `scripts/ship`,
   which calls `gh release create --latest` (no `--prerelease`) with the plain
   version string as the title.
7. **constraint** `scripts/ship` in *this* repo (`btoddb/claude-pipeline`) keeps
   its existing behaviour — float the `v1` major tag — because that is the correct
   release mechanism for a reusable workflow. When running in GitHub Actions
   (`$GITHUB_ACTIONS == true`) the interactive confirmation prompt is skipped
   automatically (no `--yes` flag needed).
8. **constraint** On any failure — preflight check, merge error, release script
   error — the `report-failure` action tags the maintainer with the phase name
   **Ship**.

## Out of scope

- Interactive version selection. Version is resolved from a `VERSION` file or the
  latest `vX.Y.Z` tag + patch bump. Custom version overrides are a future addition.
- Rollback / unship. Reverting a bad release is a manual operation.
- Running `@claude ship` on an issue (this is an explicit notify / wrong-context
  event, not a silent skip).

## Acceptance criteria

- [ ] `@claude ship` on an open PR with all checks green squash-merges, deletes the
      branch, and produces a GitHub pre-release tagged `<version>` with title
      `<version>-beta`.
- [ ] `@claude ship --force` on a PR with a failed check merges anyway.
- [ ] `@claude ship` on an issue posts a `notify` comment; no job runs.
- [ ] Missing `scripts/ship` posts a clear error comment and fails the job.
- [ ] `@claude ship --public-release` creates a `--latest` (non-prerelease) release.
- [ ] `scripts/ship` in the pipeline repo skips the interactive prompt when run
      in GitHub Actions.
