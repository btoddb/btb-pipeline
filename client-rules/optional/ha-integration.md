<!--
  Opt-in topic rules for btoddb Home Assistant custom-integration repos.
  Clients consume this ONLY via an explicit pointer file in their local
  ai-rules/ (see templates/HA-INTEGRATION-template.md); it is not part of
  the universal client-rules/ set.
-->
# Home Assistant Integration Rules

Shared rules for btoddb repositories that are Home Assistant **custom
integrations** (HACS-installable, based on the `integration_blueprint` dev
scaffold). Repo-specific facts (integration name, exact script names, test
paths) stay in each repo's local `ai-rules/PROJECT_CONTEXT.md`.

## Repo layout (integration_blueprint scaffold)

- `config/` is a throwaway Home Assistant instance for local testing.
- `scripts/` holds dev helpers; `requirements.txt` pins the Home Assistant and
  lint toolchain.
- **constraint** Every directory under `custom_components/` except the repo's
  own integration is a **vendored third-party integration** kept only for
  local testing. Never modify any of them. If any command — including
  `scripts/lint` — leaves changes under one of these directories, revert them;
  never commit a diff outside the repo's own integration.

## Production safety

- **constraint** Do not change, create, or delete anything in the user's
  production Home Assistant instance.

## Implementation details

- **Python version:** target Python 3.14 or newer.
- **Ruff formatting:** format all Python code according to the ruff formatting
  rules.
- **Ruff linting:** make coding decisions with ruff linting rules in mind.

## Key dev commands

- **Run HA locally:** `scripts/develop` launches Home Assistant against
  `config/`. It runs in the foreground with `--debug` and does not return; to
  verify a change, background it and read `config/home-assistant.log`.
- **Lint:** `scripts/lint` runs ruff format plus ruff check/fix. It rewrites
  files, so expect working-tree changes after it runs.
- **Unit tests:** `python3 -m pytest` from the repo root (see the repo's local
  rules for any repo-specific test paths).
- **Validate manifest/HACS:** `python3 -m script.hassfest` and the repo's
  `.github/workflows/validate.yml` workflow.
- **Hassfest locally (Docker):** `scripts/validate` runs CI's Hassfest check
  (`ghcr.io/home-assistant/hassfest`) against the working tree — use it to
  catch manifest/dependency/translation errors before pushing. Requires
  Docker.

## Before committing

- **constraint** Run `scripts/validate` (Hassfest via Docker) before pushing.

## Versioning

- **constraint** The integration version lives in the integration's
  `manifest.json` (`"version": "vX.Y.Z"` — the leading `v` is intentional).
  It is bumped only by the repo's ship script; never hand-edit it.
- **constraint** If the repo ships a Lovelace card, the card has an
  independent version in `card/package.json` (plain `X.Y.Z`), bumped only by
  the repo's card-deploy script (which also syncs the console banner in
  `card/src/index.ts`); never hand-edit either.

## Lovelace cards

- **constraint** For any integration that ships a Lovelace card, register the
  built JS bundle as a Lovelace resource with a content-hash `?v=` URL, and
  serve the bundle directory through
  `hass.http.async_register_static_paths`. Do not rely only on
  `add_extra_js_url`; those module URLs are baked into cached frontend pages
  and can intermittently produce `Custom element doesn't exist` during HA
  startup/cache races.
- Implementation hook: import `LOVELACE_DATA` and `ResourceStorageCollection`,
  update or create a resource whose base URL matches the card bundle, and fall
  back to `add_extra_js_url` only when resources are YAML-managed/read-only.
- **constraint** Edit a card's TypeScript source under the integration's
  `card/src/`; never hand-edit the generated `www/*.js` bundle.
