# GitHub rules

## Tool selection

- **constraint** For GitHub write actions in this repository, prefer the local
  `gh` CLI over the a GitHub connector or skill, because `gh` cli has been authenticated with needed permissions.
- **constraint** If upi use a github connector or skill and it returns a permission error on a
  write action, immediately try the equivalent `gh` command before reporting
  the action as blocked.  And then ask yourself, why didn't I run `gh` and inform the user why.
- **constraint** Do not rely on `gh auth status` alone to decide that a GitHub
  write cannot work. If the exact `gh` write command is safe and scoped, try
  that command directly.
- **suggestion** If you think using a GitHub skill or connector is more efficient for reads than `gh`, then try it first on reads.
