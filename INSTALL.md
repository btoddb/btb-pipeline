# Installing the AI Pipeline

This document covers everything from scratch: setting up the `ai-pipeline` repo
itself, provisioning all three required secrets, doing the one-time manual
bootstrap, and then adding new client repos.

---

## Part A — What runs automatically (brief)

Once the pipeline is deployed, the following happens automatically:

| Trigger | What happens |
| --- | --- |
| Comment `@btbai` on a new issue | Claude Opus writes a plan → GPT-5.5 implements it → PR opened |
| Comment `@btbai plan` on an issue | Claude Opus writes a plan only (no PR) |
| Comment `@btbai implement` on an issue | GPT-5.5 implements the latest plan → PR opened |
| Comment `@btbai review` on a PR | Claude Opus reviews the PR and posts comments |
| Comment `@btbai revise <feedback>` on a PR | GPT-5.5 applies feedback to the PR branch |
| Comment `@btbai` on a PR | Claude responds conversationally |

After each phase, the pipeline posts a comment recording which model ran.
If a phase fails (usage limit, API error, timeout), it posts a tagged comment
instead of going silently red.

---

## Part B — Manual setup steps (assume nothing)

Complete these steps in order. All commands assume you have `gh` (GitHub CLI)
and `git` installed and authenticated as `btoddb`.

### Step 1 — Create an OpenAI API key

1. Go to [platform.openai.com](https://platform.openai.com) and sign in (or create an account).
2. Select your **Organization** and create or select a **Project**.
3. Add billing: Settings → Billing → Add payment method.
   A key with no payment method returns a `429 insufficient_quota` error, which
   the pipeline will detect and report.
4. Confirm model access: Settings → Limits → verify `gpt-5.5` is listed under
   accessible models. If not, contact OpenAI to enable it for your account.
5. Create the API key:
   - Project → API keys → **Create new secret key**
   - **Scope:** restrict to this project
   - **Permissions:** All (the key must be allowed to invoke the Chat Completions
     and Responses endpoints that Codex uses; a read-only key will fail)
   - Copy the key — it is shown only once.
6. Store the key as a GitHub Actions secret:
   ```bash
   gh secret set OPENAI_API_KEY --app actions --repo btoddb/<repo>
   ```
   UI path: Settings → Secrets and variables → Actions → New repository secret →
   Name: `OPENAI_API_KEY`, Value: (paste key).
   **Never commit the key to git.**

### Step 2 — Create a Claude Code OAuth token

1. In a terminal, from any directory, run:
   ```bash
   claude setup-token
   ```
   Follow the prompts. Copy the generated token.
2. Store it as a GitHub Actions secret:
   ```bash
   gh secret set CLAUDE_CODE_OAUTH_TOKEN --app actions --repo btoddb/<repo>
   ```
   UI path: Settings → Secrets and variables → Actions → New repository secret →
   Name: `CLAUDE_CODE_OAUTH_TOKEN`, Value: (paste token).

### Step 3 — Create the `PIPELINE_WORKFLOWS_PAT`

This fine-grained PAT lets `implement` and `revise` push commits that may
include changes to `.github/workflows/**`. The default `GITHUB_TOKEN` cannot
author workflow files (a GitHub hard limit), so a PAT is required.

1. Go to **github.com → your avatar → Settings → Developer settings →
   Personal access tokens → Fine-grained tokens → Generate new token**.
2. Set the following:
   - **Token name:** `pipeline-workflows-pat` (or similar)
   - **Expiration:** 1 year (or set a calendar reminder to rotate it)
   - **Resource owner:** btoddb
   - **Repository access:** Only select repositories → pick `ai-pipeline` (and any
     client repos you want to self-update; you can add more later)
   - **Repository permissions:**
     - Contents: **Read and write**
     - Pull requests: **Read and write**
     - Workflows: **Read and write**
3. Click **Generate token** and copy it.
4. Store it as a GitHub Actions secret:
   ```bash
   gh secret set PIPELINE_WORKFLOWS_PAT --app actions --repo btoddb/<repo>
   ```
   UI path: Settings → Secrets and variables → Actions → New repository secret →
   Name: `PIPELINE_WORKFLOWS_PAT`, Value: (paste token).

> **GitHub App alternative (no expiry to babysit):** Instead of a PAT, you can
> use `actions/create-github-app-token` in the workflow to mint a short-lived
> installation token. This avoids PAT expiry but requires creating a GitHub App
> and storing its private key as a secret. The PAT approach above is simpler for
> a single-owner setup.

### Step 4 — Set workflow permissions for Actions

This allows the default `GITHUB_TOKEN` to write comments and create issues/PRs.

```bash
gh api -X PUT repos/btoddb/<repo>/actions/permissions/workflow \
  -f default_workflow_permissions=write
```

UI path: Settings → Actions → General → Workflow permissions →
"Read and write permissions" → Save.

### Step 5 — Install the Claude GitHub App

This makes Claude Code available in the repo for the plan/review/respond phases.

1. From a terminal, in the repo directory:
   ```bash
   claude
   /install-github-app
   ```
2. Follow the prompts to install the GitHub App on your repo.
3. Skip any prompt to install `CLAUDE_CODE_OAUTH_TOKEN` — you did that in Step 2.

### Step 6 — Install the workflow files (one-time bootstrap)

This is the unavoidable manual step: wiring the PAT into the workflow files
*is itself* a workflow-file edit, so the first installation must be done by you
with your `workflows`-scoped credentials. After this, the pipeline can update
its own workflow files automatically.

See `MIGRATION.md` for the exact file-copy checklist.

### Step 7 — Add client repos

See `INSTALL-IN-CLIENT-REPO.md` for the step-by-step guide to adding a new
repo that calls this pipeline.

### Step 8 — Verify

1. Open a test issue in the repo, comment `@btbai` in the body.
2. Watch the Actions tab — you should see a workflow run start within seconds.
3. Claude Opus should post a plan comment, then GPT-5.5 should open a PR.
4. Comment `@btbai review` on the PR — Opus should post a review.

---

## Secrets reference

| Secret | Where used | How to generate |
| --- | --- | --- |
| `CLAUDE_CODE_OAUTH_TOKEN` | Plan, Review, Respond (Claude phases) | `claude setup-token` |
| `OPENAI_API_KEY` | Implement, Revise (GPT phases) | OpenAI Platform → Project → API keys |
| `PIPELINE_WORKFLOWS_PAT` | Implement, Revise (git push + gh pr create) | GitHub → Settings → Fine-grained tokens |

---

## Rotating the `PIPELINE_WORKFLOWS_PAT`

Fine-grained PATs expire. When yours expires:

1. Generate a new token at **github.com → Settings → Developer settings →
   Personal access tokens → Fine-grained tokens** with the same permissions.
2. Update the secret:
   ```bash
   gh secret set PIPELINE_WORKFLOWS_PAT --app actions --repo btoddb/ai-pipeline
   # Repeat for each client repo that also uses this PAT
   ```
