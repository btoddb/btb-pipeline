
4. **Tag the release** — `git tag -f v1 && git push --force origin v1` in the new repo
   (and adopt a moving `v1` convention so callers track patches without
   re-pinning).

For `/btbai ship`, client repositories can either copy
`templates/ship.template` as a thin `scripts/ship` wrapper or rely on the
workflow fallback to `.btb-pipeline/scripts/btb-ship-base`. Put custom release
work in executable `scripts/ship.d/<hook>` files instead of copying the full
release script.
