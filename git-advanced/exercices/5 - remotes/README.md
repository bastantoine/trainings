# Remotes

There a few prerequistes:
1. Create a remote repo in https://github.com or https://gitlab.com
2. Open two terminals and clone the repo twice in two different places
   - This will simulate two people working locally on the same remote repo

Steps

- In one of the terminals, try to make some changes: creating a branch, make commits, merging... and then push.

    In the other try to get the changes and make this repo at the same state as the other one.

- In one the terminals, change some commits that have already been pushed (using a rebase for example), and then try to push the changes. You will probably need the `--force` option

    In the other try to get the changes and see what happens.

https://git-scm.com/docs/git-push
