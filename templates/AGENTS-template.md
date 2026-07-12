<!--
  Client AGENTS.md pointer. Copy this file ONCE to <repo>/AGENTS.md.
  Shared rules live in btoddb/btb-pipeline/client-rules/ and are delivered via
  the gitignored .btb-pipeline/ checkout at tag v1 — never paste them here.
-->
# General Agent Rules

This file provides guidance to AI agents (Claude Code, OpenAI Codex, Cline, and others) for working with code in this repository.

**constraint** Follow all the rules in every file directly under [.btb-pipeline/client-rules/](./.btb-pipeline/client-rules/). If that directory is missing or stale, bootstrap it first (see below). Files under `client-rules/optional/` are opt-in topic rules — follow one only when a file in this repo's local `ai-rules/` points to it.
**constraint** Follow all the rules in all files in directory, [ai-rules](./ai-rules/) — these are this repo's local rules.
**constraint** Add new repo-local rules to [PROJECT_CONTEXT.md](./ai-rules/PROJECT_CONTEXT.md). Propose changes to shared rules in btoddb/btb-pipeline instead of editing them here.

## Bootstrap the shared rules

If `.btb-pipeline/` is missing:

    git clone --quiet --config advice.detachedHead=false --depth 1 --branch v1 \
        https://github.com/btoddb/btb-pipeline.git .btb-pipeline

If it already exists, refresh it:

    git -C .btb-pipeline fetch --quiet --depth 1 --force origin refs/tags/v1:refs/tags/v1
    git -C .btb-pipeline checkout --quiet v1

Then ensure the checkout stays untracked:

    exclude_file="$(git rev-parse --git-path info/exclude)"
    mkdir -p "$(dirname "$exclude_file")" && touch "$exclude_file"
    grep -Fxq '/.btb-pipeline/' "$exclude_file" || printf '%s\n' '/.btb-pipeline/' >> "$exclude_file"
