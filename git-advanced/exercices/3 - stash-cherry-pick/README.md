# Stashes and cherry-pick

## Stash


You have the following repo configuration:

```
.... B -- E -- F .. branch-1*
    /
.. A -- C -- G .... source
         \
......... D -- H .. branch-2
```

You are currently working in the `branch-1` branch with uncommited changes. Your boss calls you and requires that you urgentyl fix an issue in the `branch-2` branch.

You need to keep aside your changes, move to the `branch-2` branch, make the required changes, and then move back to `branch-1` and resume your work.

https://git-scm.com/docs/git-stash

## Cherry-pick

You have the following repo configuration:

```
.... B -- C ..... branch-1
    /
.. A -- D -- F .. source*
         \
......... E ..... branch-2
```

You realized that the commits B and C should instead belong to the branch `branch-2`, so you should copy them there using the `cherry-pick` command.

Try doing that with the commit range selection syntax.

https://git-scm.com/docs/git-cherry-pick

https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection
