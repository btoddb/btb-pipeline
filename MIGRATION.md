# Migration runbook: sharing the `@claude` pipeline across repos

This folder holds copy-ready artifacts for splitting the `@claude` plan →
implement → review pipeline out of `room-climate-controller` into a
dedicated, reusable repo, per
[issue #38](https://github.com/btoddb/room-climate-controller/issues/38).

This is a **plan/runbook only** — nothing here is wired up automatically.
The Claude GitHub App cannot create a new repository or write files under
`.github/workflows/` in any repo, so every step below is a manual action for
a human to carry out using the files in this folder as the source material.

## Why a runbook and not a finished migration

The bot produced everything it's permitted to touch: the two composite
actions, the shared CLAUDE.md block, and non-active `.template` copies of
the caller and reusable workflows (kept as `.template` files outside
`.github/workflows/` specifically so the App's checkout/push doesn't trip the
workflow-write restriction). Turning those into live workflow files is a step
only a human (or a PAT/deploy key with `workflows: write`) can do.

## Steps

1. **Create the dedicated repo** — `<owner>/claude-pipeline`, public (a
   private repo restricts which other repos may call it, via org settings
   that need to be set up separately).

2. **Copy the reusable workflow.**
   - Copy `reusable-claude.yml.template` from this folder to
     `claude-pipeline/.github/workflows/claude.yml`.
   - Replace every `<OWNER>/<PIPELINE_REPO>` placeholder with the real
     `owner/claude-pipeline`.
   - Review it against this repo's current `.github/workflows/claude.yml` to
     make sure it stayed in sync (this template was hand-converted to
     `workflow_call` and may drift if the source workflow changes later).

3. **Copy the composite actions.**
   - Copy `actions/log-model/` and `actions/report-failure/` from this
     folder to `claude-pipeline/actions/log-model/` and
     `claude-pipeline/actions/report-failure/`.
   - These already take `maintainer`/`number`/`phase`/`execution-file`/
     `github-token` as inputs — no further edits needed.

4. **Tag the release** — `git tag v1 && git push --tags` in the new repo
   (and adopt a moving `v1` convention so callers track patches without
   re-pinning).

5. **Migrate `room-climate-controller` itself:**
   - Replace `.github/workflows/claude.yml` with `caller-claude.yml.template`
     from this folder (fill in `<OWNER>/<PIPELINE_REPO>`, `maintainer:
     btoddb`, and the existing `--allowedTools` values from the current
     workflow).
   - Delete `.github/scripts/log-model.sh` and `.github/scripts/report-failure.sh`
     (superseded by the composite actions) and the `Stage CI helper scripts`
     steps that copied them.
   - Keep the four pipeline sections in this repo's own `CLAUDE.md` — they
     stay put, just now sourced from `CLAUDE-pipeline.md` in this folder so
     future edits land in both places deliberately.
   - This step touches `.github/workflows/claude.yml`, so it must be done by
     a human (or a PAT-backed commit) — the bot can prepare the diff but
     can't push it.

6. **Roll out to each other repo you own:**
   - Add `caller-claude.yml.template` (filled in for that repo) as
     `.github/workflows/claude.yml`.
   - Paste `CLAUDE-pipeline.md`'s contents into that repo's `CLAUDE.md`,
     substituting `<MAINTAINER>`.
   - Set the `CLAUDE_CODE_OAUTH_TOKEN` secret and install the Claude GitHub
     App on the repo.

## Files in this folder

| File | Purpose |
| --- | --- |
| `reusable-claude.yml.template` | `workflow_call` pipeline — becomes `claude-pipeline/.github/workflows/claude.yml` |
| `caller-claude.yml.template` | ~20-line per-repo caller — becomes each consumer's `.github/workflows/claude.yml` |
| `actions/log-model/action.yml` | Composite action — becomes `claude-pipeline/actions/log-model/` |
| `actions/report-failure/action.yml` | Composite action — becomes `claude-pipeline/actions/report-failure/` |
| `CLAUDE-pipeline.md` | The four shared CLAUDE.md sections, parameterized with `<MAINTAINER>` |
| `MIGRATION.md` | This file |
