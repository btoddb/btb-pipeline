# Claude Pipeline

Holds the common scripts/actions for Claude to work in BToddB repos

# Repos

## Permissions

## Github User

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

### Claude

generate new token for the repo:
- claude setup-token

CLAUDE_CODE_OAUTH_TOKEN: only for authenticating Claude, so it can talk to Anthropic's servers.  ask Claude to generate one somehow then doc

gh secret set CLAUDE_CODE_OAUTH_TOKEN --app actions --repo btoddb/<repo>

### Github token

gh api -X PUT repos/btoddb/<repo>/actions/permissions/workflow \
  -f default_workflow_permissions=write

(UI: Settings → Actions → General → Workflow permissions → "Read and write permissions" → Save)

## Copy 

- templates/caller-claude.template.yml to <repo>/.github/workflows/claude-caller.yml
- CLAUDE-pipeline.md to <repo>/CLAUDE.md (or paste into existing)
- templates/ship.template to <repo>/scripts/ship (required for `@claude ship`; supports `--public-release`, appends a `beta` suffix for non-public release tags, and requires exactly one of `--bump-patch`, `--bump-minor`, or `--bump-major`)

## Install Claude

from terminal -> repo
- claude
  - /install-github-app
  - follow prompts
  - skip the part about installing CLAUDE_CODE_OAUTH_TOKEN - we did that above

# Dependabot

[`dependabot-review.yml`](.github/workflows/dependabot-review.yml) posts `@claude
review` on every Dependabot PR so it gets the same Opus line-by-line review a human
typing that comment would trigger (see the `@claude` command table in
[CLAUDE.md](CLAUDE.md#github-workflow)).

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

Copy templates/dependabot.template.yml to your repo's .github/dependabot.yml
Copy templates/dependabot-review.yml to your repo's .github/workflows/dependabot-review.yml



# Notes
- Don't forget to set a description and topics for you HACS custom component in the Repo's "About" section
