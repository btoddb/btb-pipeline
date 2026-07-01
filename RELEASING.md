# Releasing — how to ship a change

This repo is a **reusable workflow** consumed by other repos, which pin it as:

```yaml
uses: btoddb/btb-pipeline/.github/workflows/btb.yml@v1
```

That `@v1` is the contract. A fix that lands on `main` does **not** reach a single
consumer until the `v1` tag is moved onto it. This is the #1 way "it works on
`main`" silently fails to fix a downstream issue.

## The `v1` tag is a *moving* major tag

We follow the GitHub Actions convention: **`v1` is a lightweight tag that always
points directly at the newest released commit on `main`.** Consumers pin `@v1`
and pick up every patch on their next workflow run — no edit on their side. We
also cut an immutable `vMAJOR.MINOR.PATCH` tag per release so anyone who wants
to pin an exact version can.

```
… ─ A ─ B ─ C   (main)
            │
            └── v1   ← floats forward to each new release
                v1.4.0  ← immutable, never moves
```

## Shipping checklist

1. **Make the change on a branch**, not `main` (see [CLAUDE.md](CLAUDE.md)).
2. **Keep the spec in sync.** If behavior changed, update the matching rule under
   `requirements/spec/` in the *same* change and cite the rule IDs (`CC-*`, `PR-*`,
   `UX-*`). IDs are stable — add, never renumber. See
   [requirements/README.md](requirements/README.md).
3. **Merge to `main`** with linear history (fast-forward / rebase, not a merge
   commit).
4. **Ship it:** from a clean `main`, run

   ```bash
   scripts/ship --bump-patch            # pre-release; push main, tag, float v1
   scripts/ship --bump-minor            # pre-release; increment X.Y.Z to X.(Y+1).0
   scripts/ship --bump-major            # pre-release; increment X.Y.Z to (X+1).0.0
   scripts/ship --public-release --bump-patch
                                         # full release; label: latest, title: <tag>
   scripts/ship --dry-run --bump-patch  # print every command, change nothing
   ```

   The script pushes `main`, creates an immutable `vMAJOR.MINOR.PATCH` tag and
   GitHub release, then force-updates the lightweight `v1` tag to the same commit
   and pushes the tag. (Force-moving a *tag* is expected here; we never
   force-push the `main` *branch*.)
5. **Verify** the tag moved: `git ls-remote --tags origin v1` should show the new
   SHA, and the consumer's next `@btb` run uses the updated pipeline.

## Why a moving tag instead of re-pinning consumers

The plan→implement handoff and every consumer run reference `@v1`. Asking each
downstream repo to bump a pinned SHA on every fix doesn't scale and guarantees
they drift. A moving `v1` means **one `scripts/ship` here releases to all of
them at once.** If a release is bad, moving `v1` back to the previous commit is a
one-line rollback (`scripts/ship` from that commit, or `git tag -f v1 <old> &&
git push -f origin v1`).
