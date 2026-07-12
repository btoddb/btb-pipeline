# Client rules distribution

## Source of truth

1. **constraint CR-1** `client-rules/` in `btoddb/btb-pipeline` is the single
   source of truth for shared AI-agent rules (Git, GitHub, coding
   conventions, etc.) across btoddb repositories. Rules must be edited there,
   never pasted into client repos, templates, or this repo's own
   `CLAUDE.md`/`AGENTS.md`.
2. **constraint CR-2** This repository (`btb-pipeline`) must itself follow
   `client-rules/` via a pointer in its root `AGENTS.md`, so the source of
   truth is exercised the same way client repos consume it.

## Delivery

1. **constraint CR-3** Client repositories consume `client-rules/` through a
   gitignored `.btb-pipeline/` clone checked out at the floating `v1` tag —
   the same bootstrap mechanism `templates/ship.template` already uses.
2. **constraint CR-4** The bootstrap must add `/.btb-pipeline/` to the
   client's git exclude file, resolved via
   `git rev-parse --git-path info/exclude` (worktree-safe, since `.git` is a
   file rather than a directory in a worktree checkout), so the cached
   checkout never shows up as an untracked repository file.
3. **suggestion CR-5** Clients refresh `.btb-pipeline/` by re-fetching and
   re-checking-out the `v1` tag rather than re-cloning, when a local checkout
   already exists.

## Client pointer files

1. **constraint CR-6** Client `AGENTS.md`, `CLAUDE.md`, and
   `.clinerules/one-rule.md` must contain pointers only — a short constraint
   directing the agent to follow every file under
   `.btb-pipeline/client-rules/` (bootstrapping it first if missing) — and
   must never contain the shared rule text itself.
2. **constraint CR-7** This mechanism must be agent-agnostic: the same
   `client-rules/` content must be reachable by Claude Code, OpenAI Codex,
   Cline, and other agents through their respective pointer files.

## Update path

1. **constraint CR-8** To change shared rules for clients, edit
   `client-rules/` in `btoddb/btb-pipeline` and release this repository,
   moving the floating `v1` tag as part of the ship flow. Editing a client
   repository's pointer files or `ai-rules/` does not change shared rule
   behavior.
2. **constraint CR-9** Breaking changes to shared rules require a new major
   tag (for example `v2`) rather than a breaking change under the floating
   `v1` tag. Client repositories opt into the new major version by updating
   the tag reference in their bootstrap commands.
