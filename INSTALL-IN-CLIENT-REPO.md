# BTB Pipeline

Holds the common scripts/actions for BTB automation in BToddB repos.

# Repos

Create the repo.  Naming convention is "ha-<topic>"
- Ex: ha-music -> repo path becomes btoddb/ha-music

If you want this repo to be HACS compatible:
- in the Repo's "About" section
  - set a description
  - set topics for you HACS custom component 

## Permissions

### Repo required permissions

Repo -> settings -> Actions -> General
- check box "Allow GitHub Actions to create and approve pull requests"

### Github User required permissions

This is true for many things, but doc'ing here because it needs to be somewhere (maybe homelab doc 🤷)

btoddb -> settings -> developer settings -> personal access tokens -> fine-grained tokens
- pick all repos you want
- permissions -> repositories
  - Actions: R/W
  - administration: R/W
  - contents: R/W
  - Dependabot secrets: R/W
  - issues: R/W
  - pull requests: R/W
  - secrets: R/W
  - workflows: R/W

gh api -X PUT repos/btoddb/<repo>/actions/permissions/workflow \
  -f default_workflow_permissions=write

(UI: Settings → Actions → General → Workflow permissions → "Read and write permissions" → Save)

### Claude required permissions

generate new token for the repo:
- claude setup-token

CLAUDE_CODE_OAUTH_TOKEN: only for authenticating Claude, so it can talk to Anthropic's servers.  ask Claude to generate one somehow then doc

gh secret set CLAUDE_CODE_OAUTH_TOKEN --app actions --repo btoddb/<repo>

## Install 

- templates/btb-client.template.yml to <repo>/.github/workflows/btb-client.yml,
  filling in the `with:` block (`maintainer`, `setup`, language version,
  `install-command`, and any `*-allowed-tools` the repo needs) for that repo
- templates/PROJECT_CONTEXT-pipeline.md to <repo>/ai-rules/PROJECT_CONTEXT.md
  only as a local-rules starter. Do not paste the shared `/btbai` command
  contract into client repos; the reusable workflow injects that at runtime.
- templates/ship.template to <repo>/scripts/ship (required for `/btbai ship`; supports `--public-release`, appends a `beta` suffix for non-public release tags, and requires exactly one of `--bump-patch`, `--bump-minor`, or `--bump-major`)

## Install Claude

from terminal -> repo
- claude
  - /install-github-app
  - follow prompts
    - don't install workflow, we've done that
  - skip the part about installing CLAUDE_CODE_OAUTH_TOKEN - we did that above

# Dependabot

[`dependabot-review.yml`](.github/workflows/dependabot-review.yml) posts `/btbai
review` on every Dependabot PR so it gets the same BTB review path a human
typing that comment would trigger (see the `/btbai` command semantics in
[ai-rules/GITHUB_WORKFLOW.md](ai-rules/GITHUB_WORKFLOW.md) and
[requirements/spec/btb-workflow.md](requirements/spec/btb-workflow.md)).

## Permissions

The DEPENDABOT_REVIEW_PAT needs
- btoddb -> settings -> secrets
  - Choose all repos that you want
  - Repositories
    - Pull requests: Read and write
    - Issues: Read and write

Add the DEPENDABOT_REVIEW_PAT as a Dependabot secret (not actions secret) on the repos you want:
- gh secret set DEPENDABOT_REVIEW_PAT --app dependabot --repo btoddb/<repo>

## Install

1. Copy templates/dependabot.yml.template to your repo's .github/dependabot.yml
1. Copy templates/dependabot-review.yml.template to your repo's .github/workflows/dependabot-review.yml

# Notes
