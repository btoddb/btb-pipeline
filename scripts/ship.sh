#!/usr/bin/env bash
#
# Ship a change: publish `main` and float the `v1` major tag onto it so every
# consumer pinned at `@v1` picks the change up on its next run.
#
# Consumers reference this pipeline as:
#   uses: btoddb/claude-pipeline/.github/workflows/claude.yml@v1
# `v1` is a MOVING tag (GitHub Actions convention): it always points at the newest
# released commit on main. Releasing therefore means: fast-forward `main` on the
# remote, then move `v1` to it. See RELEASING.md for the full process.
#
# Usage:
#   scripts/ship.sh                 # push main + float v1 onto current HEAD
#   scripts/ship.sh --tag v1.4.0    # also cut an immutable version tag
#   scripts/ship.sh --dry-run       # print every command, change nothing
#   scripts/ship.sh --yes           # skip the confirmation prompt (automation)
#
set -euo pipefail

MAJOR_TAG="v1"
REMOTE="origin"
MAIN_BRANCH="main"
DRY_RUN=false
ASSUME_YES=false
VERSION_TAG=""

while [ $# -gt 0 ]; do
  case "$1" in
    --tag)     VERSION_TAG="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --yes|-y)  ASSUME_YES=true; shift ;;
    -h|--help) sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "ship.sh: unknown argument '$1' (try --help)" >&2; exit 2 ;;
  esac
done

run() {
  if $DRY_RUN; then
    echo "DRY-RUN: $*"
  else
    echo "+ $*"
    "$@"
  fi
}

die() { echo "ship.sh: $*" >&2; exit 1; }

# --- Preconditions -----------------------------------------------------------
branch="$(git rev-parse --abbrev-ref HEAD)"
[ "$branch" = "$MAIN_BRANCH" ] || die "must be on '$MAIN_BRANCH' (currently on '$branch')."
[ -z "$(git status --porcelain)" ] || die "working tree is not clean — commit or stash first."

if [ -n "$VERSION_TAG" ]; then
  case "$VERSION_TAG" in
    v1.*) : ;;
    *) die "--tag '$VERSION_TAG' must be a v1.x.y tag so it stays under the $MAJOR_TAG line." ;;
  esac
  if git rev-parse -q --verify "refs/tags/$VERSION_TAG" >/dev/null; then
    die "tag '$VERSION_TAG' already exists — pick the next version."
  fi
fi

# Refuse to release a main that is behind the remote (someone pushed past us).
git fetch --quiet "$REMOTE" "$MAIN_BRANCH" || die "could not fetch $REMOTE/$MAIN_BRANCH."
if ! git merge-base --is-ancestor "$REMOTE/$MAIN_BRANCH" HEAD; then
  die "local $MAIN_BRANCH is behind $REMOTE/$MAIN_BRANCH — pull/rebase before shipping."
fi

sha="$(git rev-parse --short HEAD)"
echo "About to release $MAIN_BRANCH@$sha:"
echo "  • push $REMOTE/$MAIN_BRANCH"
[ -n "$VERSION_TAG" ] && echo "  • create immutable tag $VERSION_TAG"
echo "  • float $MAJOR_TAG -> $sha (force-update tag) and push it"

if ! $DRY_RUN && ! $ASSUME_YES; then
  printf 'Proceed? [y/N] '
  read -r reply
  case "$reply" in [yY]|[yY][eE][sS]) ;; *) die "aborted." ;; esac
fi

# --- Release -----------------------------------------------------------------
run git push "$REMOTE" "$MAIN_BRANCH"

if [ -n "$VERSION_TAG" ]; then
  run git tag -a "$VERSION_TAG" -m "Release $VERSION_TAG"
  run git push "$REMOTE" "$VERSION_TAG"
fi

run git tag -f -a "$MAJOR_TAG" -m "Float $MAJOR_TAG -> $sha"
run git push -f "$REMOTE" "$MAJOR_TAG"

echo "Done. $MAJOR_TAG now points at $sha; consumers pinned @$MAJOR_TAG get it on their next run."
