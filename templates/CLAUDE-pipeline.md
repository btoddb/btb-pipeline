<!--
  Shared @btbai pipeline contract for CLAUDE.md.

  Paste this block into the consuming repo's own CLAUDE.md (there is no
  GitHub mechanism to "include" a remote markdown file at runtime, so each
  repo carries its own copy). Replace every <MAINTAINER> with the GitHub
  username configured as the `maintainer` input in that repo's caller
  workflow, and adjust the `--allowedTools` examples in the Implementation
  and Review sections to match the repo's actual lint/test commands.
-->

## GitHub Workflow

`.github/workflows/ai-pipeline.yml` is driven by **`@btbai` commands**. A `dispatch`
job parses the text that mentions `@btbai` and routes the run; the model is then
fixed per phase:

| Where you write it | Command | What runs |
| --- | --- | --- |
| New issue body/title, or any issue comment | `@btbai` | Full pipeline: **plan (Claude Opus)** → **implement (GPT-5.5)** if the plan has no open questions |
| New issue body/title, or any issue comment | `@btbai plan` | **Planning only (Claude Opus)** — posts the plan as a comment, never implements |
| Any issue comment | `@btbai implement` | **Implementation only (GPT-5.5)** — skips planning, implements the latest `<!-- btbai:plan -->` comment and opens a PR |
| PR comment / PR review | `@btbai review` | **Line-by-line review (Claude Opus)** — posts tagged comments; cannot change code (`contents` is read-only) |
| PR comment / PR review | `@btbai revise` | **Iterate on the PR (GPT-5.5)** — re-implements from the feedback in your comment, committing to the PR branch |
| PR comment / PR review | `@btbai` | Conversational reply — **Claude Opus** for a submitted review, **Claude Sonnet** for follow-up comments |

**Model routing summary:**

| Phase | Model |
| --- | --- |
| Plan | Claude Opus (`claude-opus-4-8`) |
| Implement | GPT-5.5 via OpenAI Codex CLI |
| Revise | GPT-5.5 via OpenAI Codex CLI |
| Review | Claude Opus (`claude-opus-4-8`) |
| Respond | Claude Opus (PR review) / Claude Sonnet (follow-up) |

The subcommand is the word immediately after `@btbai`; bare `@btbai` defaults to
the full pipeline (on an issue) or a conversational reply (on a PR). `@btbai
implement` bypasses the no-questions gate — it's an explicit instruction to build
the most recent plan as-is. `@btbai revise` is the PR counterpart to `implement`:
use it (not bare `@btbai`) when you want code changes on an open PR, because the
plain conversational reply does **not** carry the code-changing toolset.
`@btbai plan` / `@btbai implement` are issue-only and `@btbai review` /
`@btbai revise` are PR-only. A subcommand used in the wrong context (e.g. `@btbai
implement` on a PR, `@btbai review` on an issue) or one that isn't recognized does
**not** silently fall back: the `notify` job posts a comment explaining that nothing
ran and lists the valid commands. A plain comment with no `@btbai` mention never
starts the pipeline at all.

So planning is no longer tied to issue-open: commenting `@btbai` (or `@btbai
plan`) on an already-open issue triggers it too.

The plan→implement handoff is a job dependency inside one run, not a re-trigger:
GitHub will not start a new workflow run from a comment the action posts with
`GITHUB_TOKEN`, so the pipeline is chained via `needs:` instead.

After each phase, the workflow posts a short comment recording the **actual**
model id used for that run — on the issue for planning, on the PR for
implementation. This is automatic; you don't need to report your own model.

If a phase fails outright — usage/token limit reached, an API error, a
timeout — the pipeline's failure helper posts a `@<MAINTAINER>`-tagged comment
naming the phase and, heuristically, the likely cause, instead of the run just
going red with no comment. Every phase job wires this in automatically.

### Required secrets

| Secret | Purpose |
| --- | --- |
| `CLAUDE_CODE_OAUTH_TOKEN` | Authenticates Claude Code → Anthropic API (plan, review, respond) |
| `OPENAI_API_KEY` | Authenticates Codex CLI → OpenAI API (implement, revise) |
| `PIPELINE_WORKFLOWS_PAT` | Fine-grained PAT (Contents R/W + Workflows R/W + Pull requests R/W) — lets implement/revise push code including workflow files |

### Planning (Claude Opus)
- For every new issue, Opus must read the codebase and generate a structural implementation plan before making any code changes.
- Ensure the plan is clear and outlines the required steps.
- **constraint** Opus must post the completed plan **as a comment on the issue** — this is the only thing that carries the plan to the implementation job.
- **You do NOT write any `<!-- btbai:* -->` markers.** The workflow's gate step stamps `<!-- btbai:plan -->` / `<!-- btbai:proceed -->` itself, deterministically, after your plan is posted.
- **The proceed-vs-park decision is driven entirely by `[QUESTION]` items in your plan body** — this is the one machine signal you control:
  - **No open questions** → write none, and the gate auto-stamps the proceed marker; GPT-5.5 implements and opens the PR with no human step.
  - **Any open question** → write it as a `[QUESTION]` item (literal `[QUESTION]` tag) and `@<MAINTAINER>` so they are notified. The gate sees the tag and parks implementation until a newer plan resolves it. Use `[QUESTION]` *only* for genuine blockers — a stray `[QUESTION]` anywhere in the body will park the run.
  - For an **`@btbai plan`** (plan-only) request, just write the plan; the gate stamps the plan marker but never proceeds, regardless of questions.
- **constraint** A plan **revision** is posted as a **new** comment — never silently rewrite history.
- **constraint** When re-planning (any `@btbai plan` after an earlier plan comment exists), read the full issue thread first: find the prior plan's `[QUESTION]` items and check later comments for answers. Resolve answered questions in the revision instead of re-asking.

### Implementation (GPT-5.5 via OpenAI Codex)
- GPT-5.5 executes the approved plan strictly via `scripts/gpt-implement.sh`. The plan is the **most recent substantive plan comment Opus wrote in the thread**.
- **constraint** The gate already validated a plan exists before invocation — do not re-verify markers.
- **constraint** **NEVER** work on main. `gpt-implement.sh` creates a new `btbai/issue-<n>-<ts>` branch automatically.
- The script opens a PR via `gh pr create --base main --head <branch> --title ... --body ...` — opening the PR is the deliverable.
- A re-run on a branch that already has a PR will hit `gh pr create`'s duplicate-PR error — that is handled gracefully in the script; it is not a failure.

### Revision (GPT-5.5 via OpenAI Codex)
- `@btbai revise <feedback>` runs on an **open PR** and is the only PR command that changes code. It checks out the PR's head branch, applies the requested changes, and commits **to that same branch** — it does not open a new PR.
- It runs the same language **setup + install** steps as implement, so tests, `scripts/deploy.sh`, and `npm` are available.
- **constraint** Read the PR thread and the triggering comment first; make the change the feedback asks for, then push it to the PR branch. Don't open a second PR for the same work.

#### What Not to Commit
- Build artifacts, generated bundles, and compiled outputs (unless the project explicitly tracks them).
- Dependency and cache directories: `node_modules/`, `__pycache__/`, `.venv/`, and equivalents.
- OS-generated files (`.DS_Store`, `Thumbs.db`) and editor swap/lock files.

#### Security
- **constraint** Never commit secrets, API keys, credentials, `.env` files, or private config — not even in test or scratch branches.
- **constraint** Flag any security vulnerability (XSS, SQL injection, command injection, etc.) and fix it before reporting the task complete.

### Review (Claude Opus)
- **constraint** On any new PR, Opus should perform a line-by-line review.
- Add specific, actionable comments in the PR.
- **constraint** Always **post your review as a PR comment** — never finish silently. Even when you find nothing to flag, post a short, warm summary that names what you reviewed and explains specifically why it's solid.
- Stop, wait, and request explicit human approval before attempting any fixes or merges.
- **constraint** If you are asked to review a PR, **NEVER** make changes to the code base. You are free to add comments with snippets of suggested code.

If you leave a comment on the PR, and it is more than just a comment, tag each comment with one of the following:
- [REQUIRED]: A critical issue that must be fixed before approval
- [QUESTION]: Asking for clarification on why an implementation was chosen
- [NIT]: Minor styling, naming choices, or optional micro-optimizations that won't hold up approval
- [PRAISE]: Highlighting particularly clean, clever, or well-written sections of code
