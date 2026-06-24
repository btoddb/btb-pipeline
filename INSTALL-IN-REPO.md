# Claude Pipeline

Holds the common scripts/actions for Claude to work in BToddB repos

# Repos

## Permissions

### Claude

CLAUDE_CODE_OAUTH_TOKEN: only for authenticating Claude, so it can talk to Anthropic's servers.  ask Claude to generate one somehow then doc

gh secret set CLAUDE_CODE_OAUTH_TOKEN --app actions --repo btoddb/btoddb-ha-reminders

### Github token

gh api -X PUT repos/btoddb/btoddb-ha-reminders/actions/permissions/workflow \
  -f default_workflow_permissions=write

(UI: Settings → Actions → General → Workflow permissions → "Read and write permissions" → Save)

## Copy 

- templates/caller-claude.yml.template to <repo>/.github/workflows/claude.yml
- CLAUDE-pipeline.md to <repo>/CLAUDE.md (or paste into existing)

## Install Claude

- don't remember how, but doc it here when done
- think you use Claude CLI in the repo's local dir

# Dependabot

## Permissions

DEPENDABOT_REVIEW_PAT = 

## Notes
- Don't forget to set a description and topics for you HACS custom component in the Repo's "About" section
