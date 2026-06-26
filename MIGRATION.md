# Migration: Bootstrap the @btbai / ai-pipeline rename

This document is the **one-time manual checklist** for deploying the renamed
pipeline. Complete every step before using `@btbai` — the pipeline won't work
until you finish all of them.

**Background:** The pipeline's core changes (GPT-5.5 for implement/revise,
`@btbai` command, `btbai:plan` markers, `PIPELINE_WORKFLOWS_PAT` secret) are
coded in the `main` branch. But the active workflow files that drive every run
live under `.github/workflows/`, and the pipeline bot **cannot author files
there** (GitHub's hard limit for non-PAT tokens). So the first installation of
the new workflow files must be applied by you with your own credentials.

After this one-time bootstrap, future `@btbai` runs use `PIPELINE_WORKFLOWS_PAT`
and can update workflow files automatically — you'll never need this checklist
again for routine maintenance.

---

## Checklist

### 1 — Provision the three secrets in `ai-pipeline`

If you haven't already (or are setting up from scratch):

```bash
# 1a. Claude Code token (for plan/review/respond phases)
claude setup-token
gh secret set CLAUDE_CODE_OAUTH_TOKEN --app actions --repo btoddb/ai-pipeline

# 1b. OpenAI API key (for implement/revise phases — see INSTALL.md §Step 1)
gh secret set OPENAI_API_KEY --app actions --repo btoddb/ai-pipeline

# 1c. Fine-grained PAT (Contents R/W + Workflows R/W + Pull requests R/W)
#     See INSTALL.md §Step 3 to create it.
gh secret set PIPELINE_WORKFLOWS_PAT --app actions --repo btoddb/ai-pipeline
```

### 2 — Set Actions workflow permissions

```bash
gh api -X PUT repos/btoddb/ai-pipeline/actions/permissions/workflow \
  -f default_workflow_permissions=write
```

### 3 — Apply the new workflow files

Using your local `workflows`-scoped credentials (i.e. your regular git push,
which uses your PAT or SSH key, not the `GITHUB_TOKEN`):

```bash
# Check out the repo if you haven't already
git clone git@github.com:btoddb/ai-pipeline.git
cd ai-pipeline
git checkout main && git pull

# Copy the staged template files into the live .github/workflows/ directory
cp templates/ai-pipeline.yml        .github/workflows/ai-pipeline.yml
cp templates/ai-pipeline-caller.yml .github/workflows/ai-pipeline-caller.yml

# Remove the old workflow files
git rm .github/workflows/claude.yml
git rm .github/workflows/claude-caller.yml

# Commit and push (your credentials can write workflow files)
git add .github/workflows/
git commit -m "chore: activate @btbai / ai-pipeline workflows (MIGRATION.md step 3)"
git push origin main
```

### 4 — Rename the GitHub repository

1. Go to **github.com/btoddb/claude-pipeline** → Settings → General →
   Repository name → change to `ai-pipeline` → Rename.
   GitHub auto-creates a redirect from `claude-pipeline`, but update all
   explicit references (see step 5).
2. Update your local remote:
   ```bash
   git remote set-url origin git@github.com:btoddb/ai-pipeline.git
   ```

### 5 — Update `uses:` pins in consumer repos

Every repo that calls this pipeline has a line like:
```yaml
uses: btoddb/claude-pipeline/.github/workflows/claude.yml@v1
```
Change it to:
```yaml
uses: btoddb/ai-pipeline/.github/workflows/ai-pipeline.yml@v1
```

The caller workflow template (`templates/caller-ai-pipeline.yml.template`)
already has the correct path. See `INSTALL-IN-CLIENT-REPO.md` for the full
per-repo setup if a repo doesn't have the three secrets yet.

### 6 — Ship the `v1` tag

From a clean `main` in `ai-pipeline`:
```bash
scripts/ship.sh
```

This pushes `main` and moves the `v1` tag to it so all consumers pick up the
change on their next run.

### 7 — Verify

Open a test issue in `ai-pipeline` and comment `@btbai plan`. Confirm:
- The Actions tab shows a run starting.
- Claude Opus posts a plan comment.
- The gate control comment contains `<!-- btbai:plan -->` (not `claude:plan`).
- Comment `@btbai implement` → GPT-5.5 opens a PR.
- PR branch name starts with `btbai/`.

---

## After the bootstrap

From this point on, `implement` and `revise` runs check out code using
`PIPELINE_WORKFLOWS_PAT`, which has Workflows R/W. Any `@btbai` run that
touches `.github/workflows/**` will push successfully without a manual step.

The old `@claude` command will **not** trigger anything (hard switch — no
alias was kept). Existing open issues that reference `@claude` in their title
or body will not fire the pipeline; they need a new `@btbai` comment.
