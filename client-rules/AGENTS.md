<!--

  This directory is the single source of truth for shared AI-agent rules
  across btoddb repositories. It is delivered to client repos via the
  gitignored `.btb-pipeline/` checkout at the floating `v1` tag. Never paste
  its content into client repos; edit it here and release btb-pipeline
  instead.

-->
# General Agent Rules

This file provides guidance to AI agents for working with code in this repository.

**constraint** Follow all the rules in all files in the consuming repository's own root-level `ai-rules/` directory.
**constraint** Add new general project rules to the consuming repository's `ai-rules/PROJECT_CONTEXT.md`.
**suggestion** If a new feature has a lot of new rules, create a new rule file in the consuming repository's `ai-rules/` directory, purely for organization.  Otherwise add it to PROJECT_CONTEXT.md

**constraint** If you can't make a required change (for instance, github restriction), give clear instructions on how I must manually change it.  Assume I'm a 5 year old that knows how to read and write, but I know nothing else.

## New Code

**constraint** With all new code written, a unit test case must also be added.  Old code in the same file that doesn't have coverage should be left untested, but produce a note in the plan or result.  Untested code in unrelated files should be left untested and without a note.

## Specs

- Keep the living spec in `requirements/spec/` synchronized with workflow
  behavior changes.

## Coding

- For new code, always create a unit test
  - For Typescript, use Vitest
  - For Java, use JUnit 6
  - For Python, use Pytest
- Prefer readability and maintainability over optimization unless the optimization show real value and isn't simply academic

## Terminal

- **constraint** Never run commands that open a pager. Use `git --no-pager` for `log`, `diff`, `show`, and `blame`, and prefix `gh` commands with `GH_PAGER=cat` (or pipe to `cat`).
