# Agents


## Shared agent contract

The shared `/btbai` command contract is injected at runtime from the
`SHARED_AGENT_CONTRACT` environment value in `.github/workflows/btb.yml`.
Update that workflow value, the executable workflow behavior, and
`requirements/spec/btb-workflow.md` together when command semantics or phase
boundaries change.

Do not paste the full shared contract into `CLAUDE.md`, `AGENTS.md`, client
`ai-rules`, or templates. Those files should contain local repo guidance and
short pointers only.

## Agent rules

- Treat `templates/` as client bootstrap material, not another source of truth
  for shared pipeline behavior.
- When a fix needs to reach client repositories, release this repository and move
  the floating `v1` tag as part of the ship flow.

## Python

**constraint** Use requirements.txt to bootstrap dependencies
**constraint** Run pytest before committing any changes

## Shared client rules

**constraint** Follow all the rules in every file directly under [client-rules](./client-rules/) — this repository consumes the same shared rules it distributes to client repos. Files under `client-rules/optional/` are opt-in topic rules for client repos and do not apply here unless a local `ai-rules/` file points to one.

`client-rules/` is the single source of truth for shared agent rules. Edit rules there; never paste them into this file, templates, or client repos. Changes reach clients when the floating `v1` tag moves (ship flow).