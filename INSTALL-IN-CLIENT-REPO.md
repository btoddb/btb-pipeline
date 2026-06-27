# Claude Pipeline

Holds the common scripts/actions for Claude to work in BToddB repos

# Repos

## Permissions

## Github User

This is true for many things, but doc'ing here because it needs to be somewhere (maybe homelab doc 🤷)

btoddb -> settings -> personal access tokens -> fine-grained tokens
- all repos
- permissions -> repositories
  - administration: R/W
  - contents: R/W
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

- templates/caller-claude.yml.template to <repo>/.github/workflows/claude-caller.yml
- CLAUDE-pipeline.md to <repo>/CLAUDE.md (or paste into existing)
- templates/ship.sh.template to <repo>/scripts/ship (required for `@claude ship`)

## Install Claude

from terminal -> repo
- claude
  - /install-github-app
  - follow prompts
  - skip the part about installing CLAUDE_CODE_OAUTH_TOKEN - we did that above


# Dependabot

## Permissions
the BToddB Projects PAT needs: 
- btoddb -> settings -> secrets
  - give repository dependabot secrets R/W

The DEPENDABOT_TOKEN needs
- btoddb -> settings -> secrets
  - give repository dependabot secrets RO

gh secret set DEPENDABOT_REVIEW_PAT --app dependabot --repo btoddb/room-climate-controller



# Notes
- Don't forget to set a description and topics for you HACS custom component in the Repo's "About" section
