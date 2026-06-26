# Setting Up a New Client Repo to Use the AI Pipeline

This document explains how to wire an existing repo so that `@btbai` commands
work in its issues and PRs, using the shared pipeline at `btoddb/ai-pipeline`.

**Prerequisite:** The `btoddb/ai-pipeline` repo must already be deployed and
tagged `v1`. If you haven't done that yet, complete `INSTALL.md` and
`MIGRATION.md` first.

---

## What you'll set up

- Three GitHub Actions secrets in the client repo
- A caller workflow file (one YAML file in `.github/workflows/`)
- A CLAUDE.md snippet (the AI's instructions for this repo)
- Correct workflow permissions

---

## Step 1 — Add the three secrets

All three secrets are **per-repo** — they must be added to each client repo
individually. If you already have them in another repo, you still need to add
them here.

### 1a. `CLAUDE_CODE_OAUTH_TOKEN`

This authenticates the Claude Code agent to Anthropic's API for the plan,
review, and respond phases.

Generate a token if you don't already have one:
```bash
claude setup-token
```
Follow the prompts and copy the token.

Add it to the client repo:
```bash
gh secret set CLAUDE_CODE_OAUTH_TOKEN --app actions --repo btoddb/<client-repo>
```

UI path: Settings → Secrets and variables → Actions → New repository secret →
Name: `CLAUDE_CODE_OAUTH_TOKEN`, Value: (paste token).

### 1b. `OPENAI_API_KEY`

This authenticates the OpenAI Codex CLI to OpenAI's API for the implement and
revise phases.

You must have an OpenAI Platform account with billing enabled and model access
to `gpt-5.5`. See INSTALL.md §Step 1 for full OpenAI account and key setup.

Once you have a key, add it:
```bash
gh secret set OPENAI_API_KEY --app actions --repo btoddb/<client-repo>
```

UI path: Settings → Secrets and variables → Actions → New repository secret →
Name: `OPENAI_API_KEY`, Value: (paste key).

### 1c. `PIPELINE_WORKFLOWS_PAT`

This is a fine-grained Personal Access Token (PAT) with **Workflows: R/W**,
**Contents: R/W**, and **Pull requests: R/W** permissions. It lets the
implement and revise phases push commits — including commits that may contain
changes to `.github/workflows/**`. The default `GITHUB_TOKEN` cannot author
workflow files (a hard GitHub limit).

If you already created this PAT for `btoddb/ai-pipeline`, edit it to include
this client repo in its repository access, then store it here too:
```bash
gh secret set PIPELINE_WORKFLOWS_PAT --app actions --repo btoddb/<client-repo>
```

To add the client repo to an existing PAT:
1. Go to **github.com → your avatar → Settings → Developer settings →
   Personal access tokens → Fine-grained tokens**.
2. Click the existing `pipeline-workflows-pat` → **Edit** → Repository access →
   add the client repo → Save.

UI path for the secret: Settings → Secrets and variables → Actions →
New repository secret → Name: `PIPELINE_WORKFLOWS_PAT`, Value: (paste PAT).

**Never commit any of these secrets to git.**

---

## Step 2 — Set workflow permissions

Allow the default `GITHUB_TOKEN` to write comments, open issues, and create PRs.

```bash
gh api -X PUT repos/btoddb/<client-repo>/actions/permissions/workflow \
  -f default_workflow_permissions=write
```

UI path: Settings → Actions → General → Workflow permissions →
"Read and write permissions" → Save.

---

## Step 3 — Install the Claude GitHub App

The plan, review, and respond phases use the `claude-code-action`, which
requires the GitHub App to be installed on the repo.

1. From a terminal, in the client repo directory:
   ```bash
   claude
   /install-github-app
   ```
2. Follow the prompts. Select the client repo when asked which repos to install on.
3. Skip any prompt about `CLAUDE_CODE_OAUTH_TOKEN` — you set that in Step 1a.

---

## Step 4 — Add the caller workflow file

Copy the template:
```bash
cp templates/caller-ai-pipeline.yml.template \
   /path/to/<client-repo>/.github/workflows/ai-pipeline.yml
```

(Or copy the file content manually if you're working across repos.)

Open the copied file and fill in the `with:` block for this repo:

```yaml
with:
  maintainer: btoddb          # your GitHub username — gets @-mentioned on failures
  setup: python               # "python", "node", or "none"
  python-version: "3.14"      # only used when setup: python
  install-command: pip install -r requirements.txt  # your install command
```

The `uses:` line already points at `btoddb/ai-pipeline/.github/workflows/ai-pipeline.yml@v1`
and the secrets block already has all three secrets wired in. Don't change those.

Commit and push the workflow file:
```bash
git add .github/workflows/ai-pipeline.yml
git commit -m "chore: add @btbai pipeline caller"
git push
```

> **Note:** Because you are using your own credentials (not the pipeline bot),
> you can push workflow files normally. The PAT is only needed by the pipeline
> bot itself.

---

## Step 5 — Add the CLAUDE.md snippet

The AI agents read `CLAUDE.md` to understand how to behave in this repo. Paste
the contents of `templates/CLAUDE-pipeline.md` into the repo's `CLAUDE.md`:

```bash
cat templates/CLAUDE-pipeline.md >> /path/to/<client-repo>/CLAUDE.md
```

Then edit the pasted block to:
- Replace `<MAINTAINER>` with your GitHub username (e.g. `@btoddb`).
- Adjust the lint/test command examples to match this repo.

Commit:
```bash
git add CLAUDE.md
git commit -m "chore: add @btbai pipeline instructions to CLAUDE.md"
git push
```

---

## Step 6 — Verify

1. Open a test issue in the client repo and write `@btbai` somewhere in the body.
2. Watch the Actions tab — a workflow run should start within a few seconds.
3. Claude Opus should post a plan comment on the issue.
4. If the plan has no `[QUESTION]` items, GPT-5.5 should open a PR automatically.
5. Comment `@btbai review` on the PR to trigger a Claude Opus code review.

If the workflow doesn't trigger, check:
- All three secrets are set correctly (Settings → Secrets and variables → Actions).
- The workflow file exists at `.github/workflows/ai-pipeline.yml` and has no YAML syntax errors.
- The GitHub App is installed (Settings → GitHub Apps → check for Claude).
- Workflow permissions are set to "Read and write" (Settings → Actions → General).

---

## Updating the pipeline in this client repo

The client workflow pins `@v1`. When `btoddb/ai-pipeline` ships an update and
moves the `v1` tag, **no action is required in the client repo** — the next
`@btbai` run automatically uses the updated pipeline. This is why `v1` is a
moving tag.

If you need to pin an exact version (e.g. for a rollback), change:
```yaml
uses: btoddb/ai-pipeline/.github/workflows/ai-pipeline.yml@v1
```
to:
```yaml
uses: btoddb/ai-pipeline/.github/workflows/ai-pipeline.yml@v1.4.0
```
replacing `v1.4.0` with the specific immutable tag you want.

---

## Removing the pipeline from a client repo

1. Delete `.github/workflows/ai-pipeline.yml`.
2. Remove the three secrets (Settings → Secrets and variables → Actions → delete each).
3. Optionally remove the pipeline section from `CLAUDE.md`.
4. Optionally uninstall the GitHub App (Settings → GitHub Apps → Configure → Uninstall).
